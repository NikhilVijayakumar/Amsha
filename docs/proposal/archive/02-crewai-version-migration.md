# Proposal 02 — CrewAI Version Migration (0.201.1 → 1.x)

| | |
|---|---|
| **Status** | ✅ Done (2026-09-02) — migrated to crewai==1.15.18 / crewai-tools==1.15.18 |
| **Priority** | Second (after [01](01-nibandha-removal.md)) |
| **Risk** | Medium-High — breaking API + packaging changes |
| **Effort** | Medium (1–3 days depending on how much of 08 lands alongside) |
| **Blocks** | Every other proposal in this set (03–11) assumes 1.x APIs |

## Execution log

- **Correction to the version findings below**: the "umbrella `crewai` lags at 1.14.6" finding was stale/wrong — verified live against PyPI (`pip index versions crewai`), both `crewai` and `crewai-tools` are in sync at `1.15.18` as the latest release. No monorepo-lag issue in practice.
- Environment: found the project's `pyproject.toml` had `[tool.setuptools]` config but no `[build-system]` table, so `uv sync` was installing dependencies but never building/installing the Amsha package itself into `.venv`. Added `[build-system]` (setuptools). Also added `requires-python = ">=3.12,<3.14"` — `uv`'s universal resolver failed on a Python-3.14-only branch where `crewai`'s `mcp` dependency requires `pydantic>=2.12`, conflicting with Amsha's `pydantic==2.11.9` pin; irrelevant to the actual 3.12 install, fixed by scoping supported versions per uv's own hint.
- Two dependencies were silently satisfied before only because `crewai==0.201.1` happened to pull them in transitively: `litellm` (used directly by `amsha/llm_factory/service/llm_builder.py`) and `pytest`/`pytest-cov` (dev tooling, was never declared). Both added as explicit dependencies (`litellm` as a runtime dep, `pytest`/`pytest-cov`/`hypothesis` as a `[dependency-groups] dev` group) — this is a real gap the version bump surfaced, not a new one it created.
- **One genuine breaking change found, not predicted by docs research**: crewai 1.15.18's `BaseKnowledgeSource` added an abstract `aadd()` method (async variant of `add()`). Amsha's `AmshaCrewDoclingSource` didn't implement it, making the class non-instantiable. Fixed with `async def aadd(self) -> None: self.add()` — docling's conversion is CPU-bound, no real async path exists, so this just satisfies the interface.
- Full test suite after migration: **217 passed, 27 failed, 2 skipped** — all 27 failures are the same pre-existing baseline already identified during the Nibandha removal (mock arity, tuple-unpack drift in `shared_llm_initialization_service`, `output_file_path`/None checks in `json_cleaner_utils`, azure-prefix parsing in `llm_utils`, GPU/pynvml print-vs-logger drift). No new regressions from the version bump itself.
- Also deleted several pre-existing orphaned tests discovered during triage — referencing modules/classes that never existed in the current source tree at all (`amsha.analysis.architectural_alignment_tool`, `FileCrewApplication`/`DbCrewApplication` under wrong module paths, a stale duplicate of `test_crew_performance_monitor.py` at the tests root). Unrelated to this migration; they were dead weight regardless.
- Executed together with an out-of-band decision in the same session: full removal of the MongoDB/DB-backend code path (not part of the original proposal set — Amsha is file-config-only now). See note in [00](00-overview-and-roadmap.md) and [05](05-checkpointing-consolidation.md), which referenced the now-deleted Mongo adapters as a future durability option.

## Version findings (verified via docs + PyPI/changelog research, not assumed)

- CrewAI crossed 0.x → **1.0.0 on 2025-10-20** (after `1.0.0a1`→`a4`→`b1`→`b3` pre-releases).
- Current docs are pinned to **`v1.15.18`**, which is a real shipping version, not a docs-site-only label.
- The package has **split into a monorepo**: `crewai-core` and `crewai-cli` are at `1.15.18`, `crewai-tools` is at `1.15.16`, but the umbrella `crewai` package (the one Amsha actually depends on) lags behind at **`1.14.6`**.
- Release cadence is fast — roughly one release every 1–2 weeks since 1.0.0.
- **No official single "0.x → 1.x migration guide" exists.** The breaking changes below are reconstructed from changelogs/release notes and current docs. Before executing this migration, pull `github.com/crewAIInc/crewAI/releases` for tags `1.0.0a1` through `1.0.0` for a commit-level diff — treat this proposal as the map, not the final word.

## Breaking / structural changes that affect Amsha specifically

1. **Monorepo package split.** `crewai-tools` merged into the main workspace; `crewai-core`/`crewai-cli` now exist as separate packages. Amsha's `pyproject.toml` pins `crewai` and `crewai-tools` directly — **verify at migration time** whether `crewai` (umbrella, 1.14.6) or `crewai-core` (1.15.18) is the correct dependency for Amsha's actual import surface (`from crewai import Crew, Agent, Process, Task, LLM`). Don't assume; check what the umbrella package re-exports at the target version.
2. **Memory system fully rewritten.** Not currently used by Amsha (`memory=` is never set on `Crew`/`Agent`), so this is a **zero-migration-cost, pure-adoption** item — see [04](04-memory-adoption.md). No old memory code to break.
3. **`Flow`/`LLM` classes are now Pydantic `BaseModel` internally.** Amsha's `CrewAIProviderAdapter` (`llm_factory/adapters/crewai_adapter.py`) just holds a reference to a `crewai.LLM` instance and exposes `.get_raw_llm()` — it doesn't subclass or introspect `LLM` internals, so this should be a non-issue. Confirm by running Amsha's LLM factory tests against the new version.
4. **`CrewAgentExecutor` deprecated** (v1.14.5) in favor of `AgentExecutor`. Amsha never references `CrewAgentExecutor` directly (`grep` confirms) — no action needed unless a future Amsha feature reaches into executor internals.
5. **`CodeInterpreterTool` removed** (v1.14.0). Amsha doesn't reference it — no action needed.
6. **`allow_code_execution`/`code_execution_mode` on `Agent` deprecated.** Amsha's `CrewBuilderService.add_agent` doesn't set these — no action needed today, but don't add them when implementing [08](08-agent-task-capability-expansion.md); point users at external code-exec services instead if that need ever comes up.
7. **CrewAI's own streaming behavior.** `base_crew_orchestrator.py` already has version-aware handling for this (`# Handle streaming response (CrewAI 1.8.0+)`), so Amsha's orchestrator has *already* been partially adapted to 1.x streaming semantics even while pinned to 0.201.1 in `pyproject.toml` — **verify what version is actually installed in the working `.venv`** vs. what's pinned; there may already be drift (see verification step below).

## Verification step before writing any migration code

Run this first — the comment in `base_crew_orchestrator.py` referencing "CrewAI 1.8.0+" suggests the installed environment may already be ahead of the `pyproject.toml` pin:

```bash
pip show crewai crewai-tools | grep -E "Name|Version"
```

If the installed version is already >0.201.1, treat this proposal as "align the pin with reality and finish the job," not "upgrade from scratch."

## Migration plan

1. **Pin target versions explicitly** once step above confirms compatible sub-package versions:
   ```
   crewai == <verified umbrella version, e.g. 1.14.6 or later>
   crewai-tools == <verified compatible version>
   ```
   Avoid floating (`>=`) pins for a fast-moving dependency — Amsha's own versioning discipline (exact `==` pins throughout `pyproject.toml`) should extend here.
2. **Upgrade in a branch, run the existing test suite untouched first** (`src/nikhil/amsha/integration_tests/crew_forge/test_json_retry_workflow.py` and any others) to get a clean baseline of what breaks purely from the version bump, before adding any new 1.x-only features.
3. **Fix breakage** — expected candidates based on the research above: import paths if `crewai-core` split changes what `crewai` re-exports; any `Process`/`CrewOutput` shape changes (`base_crew_orchestrator.py` already handles `CrewOutput` explicitly — re-verify field names).
4. **Re-run `crew_performance_monitor.py`'s token-usage parsing** against a real 1.x `CrewOutput` — the code already has a defensive `usage is None` branch commented "CrewAI 1.8.0: token_usage might be None," so this is a known fragile point.
5. **Do not adopt new 1.x features in this same change** (Flows, Memory, Skills, etc.) — keep this migration to "same behavior, new version" and let proposals 03–11 add capability afterward. Mixing a version bump with new feature adoption makes it impossible to tell which change caused a regression.
6. **Update `pyproject.toml` version** (currently `2.11.2`) per whatever semver policy this project uses for dependency bumps — this is a breaking-adjacent change even if Amsha's own public API doesn't change.

## Rollback plan

Since the git dependency on Nibandha is removed in [01](01-nibandha-removal.md) *before* this step, a failed migration attempt only needs to revert the `crewai`/`crewai-tools` pins and any code changes in this branch — no compounding variables.
