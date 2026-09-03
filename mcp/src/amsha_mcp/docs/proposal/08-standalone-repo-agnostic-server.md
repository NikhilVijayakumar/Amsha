# Proposal 08 — Standalone, Repo-Agnostic MCP Server (Zero Amsha Dependency)

| | |
|---|---|
| **Status** | Proposed |
| **Priority** | High — fixes a real dependency-management defect, not a hypothetical one |
| **Risk** | Medium — touches server startup (the Phase-4 deadlock guard), schema-reuse imports, and doc resolution |
| **Effort** | Medium-large |
| **Depends on** | 01 (`docs_loader`), 03 (verification engine), 04 (`dry_run_parse`/`smoke_test`) |

## The problem, confirmed by reading the actual files

`mcp/pyproject.toml`'s `dependencies` is `["mcp>=1.0.0,<2"]` — it does **not** declare `amsha` at all. Today `amsha-mcp` only works because it happens to be installed into the same venv (`E:\Python\Amsha\.venv`) as Amsha's own editable install. That's accidental coupling through venv-sharing, not a declared dependency — real poor dependency management, not a necessary design constraint. Two more confirmed hard-codes compound it:

- `docs_loader.py`: `PACKAGE_ROOT = Path(__file__).resolve().parent`, `REPO_ROOT = MCP_ROOT.parent` — assumes `mcp/` physically lives inside the Amsha checkout it's meant to describe.
- `server.py`: eagerly imports `amsha.crew_forge.domain.models.agent_data`/`task_data` in the main thread before `mcp.run()` — the Phase-4 deadlock-guard fix (lazy import from inside a FastMCP worker thread deadlocked the stdio server). This assumes Amsha is statically importable at process start.

Net effect: `amsha-mcp` cannot run in a venv that doesn't happen to also have Amsha installed, and cannot be built/shipped as a standalone artifact today.

## Goal

`amsha-mcp` becomes a standalone package with **zero pip/build dependency on `amsha` or the Amsha repo**. It becomes aware of a *specific* repo only through explicit, runtime registration — usable against Amsha's own repo, any other repo that happens to depend on Amsha, or (for the doc/file-inspection tools) any repo at all.

## Design — three concerns, three different fixes

### 1. Docs-serving (Phase 1: `list_amsha_modules`, `get_quickstart`, `search_amsha_docs`, feature docs)

Pure file reads off `docs/`, `README.md`, feature docs — zero code dependency already. Replace the hardcoded `REPO_ROOT = MCP_ROOT.parent` walk-up with a **registered target repo**:

- `register_repo(path: str)` — a new tool that sets the target repo path.
- `AMSHA_MCP_TARGET_REPO` env var — sets the default at process start, so a Claude Code MCP registration's `env` block can point a given project's server instance at the right repo once, no per-session call needed.
- Precedence: an explicit `register_repo()` call overrides the env-var default.

**State model — process-global, not per-session.** `docs_loader` reads the target through one mutable global (`configure_repo_root`, `_REPO_ROOT`). Making it per-session would require thread-safe session-scoped state threaded through six modules that currently read the global directly. For v1 the target is **process-global**: last `register_repo()` (or env-var at startup) wins and applies to every session in this server process. That matches how a single-project MCP registration boots one server for the whole conversation, and it is the honest reflection of the existing code shape. Per-session switching is a non-goal for this proposal; if a future multi-repo need arises it is a separate change to the state model.

**Default when neither env var nor `register_repo()` is set:** no target repo. Doc/file-inspection tools return empty/absent (a standalone install with nothing registered serves only methodology docs); schema-verification tools report "no repo registered." This is a deliberate behavior change from today's `MCP_ROOT.parent` fallback — the fallback only ever worked inside a checkout, which a standalone wheel never is.

### 2. Methodology docs (`mcp/docs/prerequisite/`, `mcp/docs/implementation/`, `mcp/docs/proposal/`)

This is `amsha-mcp`'s **own** opinion/reference material — the prerequisite→implementation governance methodology — not the target repo's content. It should never have been read relative to an assumed outer-repo layout in the first place. Ship it as bundled package data (`package_data`/`include_package_data` in `mcp/pyproject.toml`) so a standalone wheel carries it. `get_prerequisite_stage`/`get_implementation_guide` keep working identically regardless of which repo (if any) is registered.

### 3. Schema-reuse validation (Phase 3+: `verify_crew_yaml`, `dry_run_parse`, `smoke_test`)

The one real tension. These tools import the actual `AgentRequest`/`TaskRequest`/`CrewData` Pydantic models to validate against — the "never invent a parallel schema, always reuse the real one" rule this entire build has held to since Phase 3. Zero build-time dependency means these can no longer statically `import amsha...`.

Fix: import **dynamically, from the registered repo, on the safe main-thread-at-startup path** — parameterize today's eager guard to `sys.path.insert(0, f"{target_repo}/src")` then `importlib.import_module("amsha.crew_forge.domain.models.agent_data")` **before `mcp.run()`**, using the env-var repo. Call-time re-import for a mid-session `register_repo()` is **deferred** (see the open question below — thin path-recorder only until a stdio test clears it). Loading the model modules is a separate step from resolving the repo path: doc/file-inspection tools need only the path (process-global, as section 1 defines); schema tools additionally need Amsha importable at that path. If the registered repo has no importable `amsha.crew_forge` (wrong path, or a repo that doesn't use Amsha at all), the tool reports that plainly — `{"error": "No amsha.crew_forge found at registered repo '<path>' — cannot verify against real schemas."}` — and does **not** fall back to a hand-maintained parallel schema. Staying honest to the existing rule matters more than always producing an answer.

## Deadlock risk — why the import guard does not move

This is the part that needs empirical validation, not just design on paper, because the original bug (lazy import inside a FastMCP worker thread deadlocking the stdio server) was found by testing, not analysis — its root cause was never fully reverse-engineered, only worked around.

Two cases, different risk:

- **Repo known at startup** (`AMSHA_MCP_TARGET_REPO` env var set — the expected common case, matching how Claude Code registrations already work via `env` blocks): do exactly what today's guard does, just parameterized — eager import in the main thread, from the env-var path, before `mcp.run()`. Same shape as the already-proven-safe fix. Low risk.
- **Repo registered mid-session** (`register_repo()` called as a tool, which itself executes inside a FastMCP worker thread): the same deadlock risk that motivated the original fix may reappear, since the first `amsha.crew_forge` import would again happen lazily inside a worker thread. **Not assumed solved — must be verified with a real stdio test** (register a repo mid-session, then immediately call `verify_crew_yaml`, confirm the server doesn't hang) before this path is trusted.

  **Pragmatic v1 stance (do not half-design a fix for a bug we only worked around, not understood):** mid-session `register_repo()` is a **thin path recorder only** — it sets the process-global target path and validates it exists on disk; it does **not** import Amsha. If the recorded repo differs from the startup-time env-var repo, the schema-verification tools report that the new repo will take effect **on the next (re)start** (and, where they can, note it). This keeps the only import that risks deadlock on the already-proven-safe main-thread-at-startup path. True mid-session re-targeting of schema imports is **out of scope until a real stdio test demonstrates it does not hang**; the test in the bar below is a gate, not a commitment to build the feature. If the gate passes later, revisit — do not design the thread-join mechanism on paper now.

## Non-negotiables

- **Zero `amsha` entry in `mcp/pyproject.toml` dependencies.** If a future need requires the real package, that's a new decision, not a quiet regression back to shared-venv coupling.
- **Never invent a parallel schema.** A registered repo with no importable Amsha means verification tools report inability to verify — never a hand-rolled substitute schema.
- **Methodology docs ship with the package**, not read from any registered repo.
- **The env-var startup path is the default, trusted path.** Mid-session `register_repo()` is a path recorder only — it never triggers an import until the (unresolved) deadlock risk is cleared by a real stdio test.

## What NOT to do

- Don't build a generic plugin system for arbitrary non-Amsha frameworks. Scope is: works fully for Amsha-shaped repos (real schema reuse), degrades gracefully and honestly for anything else (docs/file-inspection tools still work, schema-verification tools report their limitation).
- Don't bundle arbitrary *target*-repo docs into the package — only `amsha-mcp`'s own methodology docs get bundled. A registered repo's `docs/`/`README.md` are always read live, which is correct — that content is the whole point of registering a repo.

## Testing bar

- Real stdio test: register a fixture repo with a real `amsha.crew_forge` importable at its `src/`, call `verify_crew_yaml` against it, confirm real schema validation happens.
- Real stdio test: register a fixture repo **without** Amsha importable, call `verify_crew_yaml`, confirm a clear "cannot verify" error, not a crash, not a fake pass.
- Real stdio test: register two different repos in sequence within one server process, confirm doc/file-inspection tools reflect whichever is currently registered (these read only the path, safe live) **and** confirm schema tools still use the startup env-var repo until restart (the split behavior the deadlock stance implies).
- The deadlock-risk test described above — register-then-immediately-verify in one session, confirm no hang, before `register_repo()`'s dynamic-import path is trusted for anything beyond experimental use. **Gate only; if it hangs, ship the thin-recorder default (schema tools need a restart to re-target) and do not build the thread-join fix on paper.**
- `mcp/pyproject.toml` has no `amsha` dependency — assert this in a packaging/lint check, not just by eye.

## Why this scope and not more

Ponytail check: should this also solve "any CrewAI project, not just Amsha ones"? No — that's a different, bigger tool. This proposal only removes an *accidental* dependency that was never supposed to exist; it doesn't turn `amsha-mcp` into a general CrewAI governance server for projects that don't use Amsha's schemas at all.
