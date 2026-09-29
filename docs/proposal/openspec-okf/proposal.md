# Proposal 15 — OpenSpec + OKF Adoption

| | |
|---|---|
| **Status** | In progress — Phase 6 pre-staged |
| **Date** | 2026-09-29 |
| **Author** | Nikhil (compiled with Claude) |
| **Priority** | High — unblocks agent context control; three live defects fixed en route |
| **Risk** | Low for docs (revertible `git mv` + additive files); Medium for the MCP fixes, which are code |
| **Effort** | Medium — spread across 9 phases, each independently shippable |
| **Depends on** | Nothing. Independent of [14](../archive/14-llm-lifecycle-management.md) |
| **Scope** | `AGENTS.md`, `docs/`, new `knowledge/` (OKF), new `openspec/` ×2, `mcp/src/amsha_mcp/docs_loader.py`, `mcp/src/amsha_mcp/tools/architecture.py`. `.agent/`, `.claude/`, `.vscode/`, `.idea/` explicitly **out of scope** |

---

## The problem

Three concrete defects, plus a structural one.

**1. The highest-authority agent instruction file contradicts itself.** `AGENTS.md` is 713 lines:

- Sections 10–13 and the Quick Reference Checklist appear **twice** — both copies are 194 lines. They are **not identical**: the first carries `2.0.9` and a checklist *truncated* mid-way, ending in an orphaned code fragment (a mangled copy of §8's `__init__.py` export example); the second carries `1.5.3` and a *complete* 10-item checklist. A bad merge appended one onto the other.
- Section 8 was missing; numbering jumped 7 → 9.
- Four stale Amsha version references: `2.0.9` (×3, including two in §14) and `1.5.3` (×1). `pyproject.toml` says **2.11.4**.

**Found during Phase 1, beyond the original scope.** §13 (formerly §14, Dependency Management Standards) is stale in a way that contradicts already-archived work:

| `AGENTS.md` claims | `pyproject.toml` actual |
|---|---|
| `crewai == 0.201.1` | `crewai == 1.15.18` |
| `crewai == 0.201.1` (requirements example) | — pre-[02](../archive/02-crewai-version-migration.md) era |
| `PyYAML == 6.0.2` (requirements example) | `PyYAML ==6.0.3` |
| §7: "Amsha requires Python 3.10+" | `requires-python = ">=3.12,<3.14"` |

The constitution currently prescribes a dependency set from before the CrewAI 1.x migration that archived proposal 02 records as *Done*. **Not fixed in Phase 1** — dependency content is out of that phase's scope. Needs its own decision.

**2. The MCP silently fails to serve prerequisite documentation.** `tools/architecture.py:53` resolves the path as `repo_root()/mcp/docs/prerequisite/<stage>`. That directory does not exist — `mcp/docs/` holds only `PACKAGING.md` and `mcp-validations/`. The docs moved to `mcp/src/amsha_mcp/docs/prerequisite/`. The `except OSError: return ""` on line 56 swallows the failure, so the `"doc"` field returned at `architecture.py:112` is **always an empty string**. Commit `ccc8f4c` ("fix broken proposal-08 link in PACKAGING.md *after docs move*") confirms the move happened and this path was missed.

**3. One of nine source modules is invisible to the MCP.** `docs_loader.py:123-131` lists 7 of the 9 modules in `src/nikhil/amsha/`. `common` is excluded by the comment on line 122 ("not user-facing"). `configuration` is missing with no justification, and `runtime_modules()` filters to that list — so `list_amsha_modules()` and `explain_module("configuration")` can never return it.

**4. No deterministic contract for how knowledge and change are described.** 14 proposals were hand-rolled without machine validation. A 9th module (`configuration`) has no feature doc at all; only 4 of 9 modules do.

---

## The two knowledge planes

This is the central architectural idea, and **it is not new — the code already implements it.**

`docs_loader.py` already splits every read into two planes:

| Plane | Source | Guard | Behaviour with no repo |
|---|---|---|---|
| **Product** | `_DOCS = PACKAGE_ROOT / "docs"` (`:25`, used `:77`) | none | always serves |
| **Repository** | `_REPO_ROOT` (`:98, :106, :146, :160, :192, :203`) | `if not _REPO_ROOT: return {}` | returns `{}` |

Six guarded entry points, one unguarded. The standalone-wheel property is already enforced structurally, per `docs_loader.py:5-7`: *"These never depend on an outer-repo layout; a standalone wheel carries them."*

This proposal **documents that boundary** rather than inventing one.

> **Invariant:** MCP runtime knowledge is self-contained within the distributable. Repository knowledge may describe the MCP; the MCP must never require it.

Therefore `mcp/src/amsha_mcp/docs/` (43 files) stays **byte-identical and permanently** inside the package. It is versioned with the `amsha_mcp` wheel (currently 0.1.0), loaded via `mcp/pyproject.toml:23` (`package-data: amsha_mcp = ["docs/**/*.md"]`), and its filenames are hardcoded in `_STAGE_DOC` (`architecture.py:32-38`) and `_STAGE_DOC_FILE`. Moving or renaming them breaks the standalone wheel — the property commit `2b137c7` ("standalone repo-agnostic server") was built to create.

---

## The layer model

```
OKF knowledge/          what we know about the system        (durable, years)
        │
        │ context
        ▼
OpenSpec changes/       what we intend to change             (transient)
        │
        │ implements
        ▼
Code                    what actually exists
        │
        │ verified by
        ▼
Tests + MCP verifiers   what we can demonstrate
        │
        │ updates
        └──────────────► OKF knowledge/
```

`knowledge/` and `openspec/specs/` deliberately have **different jobs**:

- `knowledge/features/crew-forge.md` — what Crew Forge *is*: role, dependencies, boundaries, design decisions. Prose.
- `openspec/specs/crew-forge/spec.md` — what behaviour *must be true*: `### Requirement:` + `#### Scenario:`, machine-validated by `openspec validate`.

Each spec links its OKF concept. Neither restates the other.

---

## Two OpenSpec roots

OpenSpec resolves the **nearest qualifying root** by walking up (`dist/core/root-selection.js:174`). A nested `mcp/openspec/` wins inside `mcp/`; the root one wins elsewhere. Two roots is safe and matches the distributable boundary: Amsha and amsha-mcp have separate source, separate documentation, and separate release cadence.

---

## Phases

| # | Phase | Change | Gate |
|---|---|---|---|
| **0** | Baseline inventory | Read-only. Counts: 9 modules, 26 skills, 43 packaged docs, 14 proposals, AGENTS.md defect list | Nothing modified |
| **1** | Fix `AGENTS.md` | Remove the truncated duplicate; renumber 9–14 → 8–13; reconcile 4 version refs | ✅ **Done** — 713 → 519 lines, §1–13 sequential, one version string (2.11.4), checklist complete |
| **2** | MCP fixes | Separate OpenSpec change, see below | `_stage_content()` returns text; `explain_module("configuration")` works |
| **3** | `openspec init` ×2 | Root + `mcp/`, `--tools opencode` | `openspec list` works in both |
| **4** | Specs, 9 capabilities | `openspec/specs/<capability>/spec.md` | ✅ **Done** — 9 specs, 44 requirements, `openspec validate --specs --strict` clean; each links its `knowledge/features/` concept |
| **5** | OKF bundle | `knowledge/` — 9 module concepts + 1 deprecated, 3 methodology playbooks, contracts, decisions | `type:` present on every non-reserved `.md` (§11) |
| **6** | `docs/` reorg | Proposals → archive | **Already pre-staged** |
| **7** | Loader: `knowledge/` as Plane 2 | Repo-side search only, keeps the `if not _REPO_ROOT` guard | Standalone wheel unaffected |
| **8** | OKF linter | `scripts/okf_lint.py`: frontmatter parses, `type:` non-empty, `status` ∈ {draft, stable, deprecated}, ISO-8601 timestamps, actor convention, `index.md` carries no frontmatter | Standalone script — see note |

### Phase 2 as a separate change

The two MCP bugs are code defects, not documentation architecture. They ship as their own OpenSpec change, `fix-mcp-documentation-discovery`, in their own review:

- **Bug A** — `architecture.py:53` must use the loader abstraction that already knows the packaged location: `dl.read_prerequisite()[_STAGE_DOC[stage]]`, not a path reconstructed from the repository layout. Requirement: *The MCP MUST retrieve prerequisite documentation from the same package-resolved source used by the standalone runtime.*
- **Bug B** — add `configuration` to `RUNTIME_MODULES`. Requirement: *The MCP MUST expose every supported Amsha runtime module.* This also enables a future consistency check comparing the OKF feature inventory against the MCP runtime inventory.

### Phase 6 — current state

Already staged in the working tree, uncommitted:

```
D  docs/proposal/00-overview-and-roadmap.md
MM docs/proposal/archive/00-overview-and-roadmap.md
R  docs/proposal/12-tools-and-mcp-adoption.md -> docs/proposal/archive/12-tools-and-mcp-adoption.md
R  docs/proposal/13-observability-tracing.md -> docs/proposal/archive/13-observability-tracing.md
RM docs/proposal/14-llm-lifecycle-management.md -> docs/proposal/archive/14-llm-lifecycle-management.md
```

All 14 proposals now sit in `docs/proposal/archive/`, with relative links fixed (`archive/08-…` → `08-…`) to account for the extra directory level. This mirrors the existing `docs/archived/` convention rather than introducing `docs/legacy/proposal/`.

---

## Knowledge bundle layout

```
knowledge/
├── index.md                      # reserved filename, no frontmatter (§8)
├── features/         common · configuration · crew-forge · crew-monitor
│                      execution-runtime · execution-state · llm-factory
│                      output-process · utils
│                      + crew-gen (status: deprecated)
├── contracts/
├── decisions/
└── methodology/      prerequisite.md · implementation.md · proposal.md
```

- **Vocabulary (corrected against the published OKF v0.2 spec during Phase 5).** The original note here said `type: Feature` + `status: active | retired`. That is wrong on both halves. OKF v0.2 fixes `status` to exactly `draft | stable | deprecated` (§5.4), and leaves `type` entirely unregistered (§4.1) — `Module`, `Playbook`, `Reference` and `Decision` are all conformant and all self-explanatory. So: the nine live modules are `type: Module` with **no** `status` (absent ⇒ `stable`, §5.4); `crew_gen` is `type: Module` + `status: deprecated`; "internal" is expressed with `tags: [internal]`, never with an invented status value. Lifecycle belongs in `status` because that is the field that means it — but only with the values the spec defines.
- **`crew-gen` is retired, not deleted.** It has no source in `src/` (only a stale `build/lib/amsha/crew_gen/`) but has historical docs. Retiring preserves intent explicitly.
- **The 5 undocumented modules** (`common`, `configuration`, `execution_runtime`, `execution_state`, `output_process`, `utils` minus the 4 with feature docs) are documented from source. A documentation gap that OKF exposes is the point of the exercise, not a reason to skip it.
- **The 3 methodology concepts describe, never copy.** Each explains what the stage means, when an agent uses it, its input/output contract, which packaged files are authoritative, how it is verified, and how it relates to the other stages. Then it links. Copying the 43 files into `knowledge/` would rebuild the exact duplication this proposal removes — and the wheel copy would go stale on the next `amsha_mcp` release.

---

## What NOT to do

- **Do not add OKF frontmatter to `mcp/src/amsha_mcp/docs/`.** They are runtime data served verbatim to the LLM by `get_prerequisite_stage` / `get_implementation_guide`, and `get_preview` (`docs_loader.py:173-187`) does not strip frontmatter — it would leak into what the agent reads. (Note: `verify_prerequisite_files` is *not* at risk — `_YAML_FENCE` at `verification.py:1362` matches only fenced ` ```yaml ` blocks, never frontmatter.)
- **Do not let OpenSpec artifacts become first-class OKF concepts.** The lifecycles genuinely differ: a proposal runs `proposed → archived` in weeks; a domain concept stays valid for years. They link; they do not merge.
- **Do not add an `evidence/` directory.** pytest, `docs/reference/testing/`, `.Amsha/Report` and coverage already hold evidence. A fourth store is a fourth thing to rot. Point at reproductions instead.
- **Do not move `docs/feature/`.** `read_features_docs()` (`docs_loader.py:104-114`) globs `_REPO_ROOT/docs/feature/*/*.md`. Moving it silently empties the MCP's feature docs. Only `docs/proposal/` is safe to relocate — nothing reads it.
- **Do not touch `.agent/`.** All 26 `.agent/skills/*/SKILL.md` carry frontmatter (`name`, `description`, `priority`) — they are the loadable definitions for a vibe-coding tool. `docs/reference/agent/skills/` is the human manual for the same 26 skills. The content matches (same stages, same venv enforcement, same `pyproject.toml` root discovery); the formats differ. These are two representations, not a fork. `docs/reference/agent/skills/` is inconsistently formatted — 14 files with frontmatter, 11 without — which signals hand-copying, not divergence. Delete nothing here.
- **Do not bridge OKF and OpenSpec with custom frontmatter.** The obvious bridge (`id:` on both, `context:` holding a path list) is not OKF v0.2. Those fields do not exist. Bridging via custom keys means forking the spec. Link in markdown bodies instead.
- **Do not make the MCP depend on repository knowledge.** Phase 7 adds `knowledge/` to the *repo-side* search surface only, behind the existing `if not _REPO_ROOT` guard. `_DOCS` never changes.
- **Do not backfill the 14 archived proposals into OpenSpec changes.** They are history. `openspec/specs/` records current behaviour; it grows forward from the next real change.

---

## Open decisions

1. **`common` — serve it or mark it internal?** After the Bug B fix the MCP serves 8 of 9 modules; `common` remains unserved by deliberate comment. That breaks an exact OKF-vs-MCP inventory match. Options: (a) add `common` to `RUNTIME_MODULES`; (b) file `common` under `knowledge/contracts/` as an internal module and let OKF show 8-of-8; (c) record the mismatch as intentional. *Recommendation: (b) — `common` is cross-cutting logging, not a feature.*
2. **Feature count.** Document 9 modules (mirrors `src/` exactly) or 8 (excludes `common` per (b))? *Recommendation: 9, with `common` typed as internal — a source tree is the least surprising thing to mirror.*
3. **Linter placement.** `scripts/okf_lint.py` (repo convention) or inside `mcp/`? *Recommendation: `scripts/`, since OKF is repository knowledge.*
4. **`AGENTS.md` §13 dependency staleness** — found during Phase 1, not fixed. The section prescribes `crewai == 0.201.1` and Python 3.10+ while the project runs `crewai == 1.15.18` on Python `>=3.12`. Options: (a) fix in this pass; (b) separate OpenSpec change `realign-agent-instruction-dependencies`; (c) replace the hand-maintained block with a pointer to `pyproject.toml` so it can never drift again. *Recommendation: (c) — the authoritative list already lives in `pyproject.toml`, and a second copy in prose is the same duplication class this proposal exists to remove.*
5. **OKF linter wiring.** `AGENTS.md` §13 claims `pre-commit` is a dev dependency, but `requirements.txt` does not list it, there is no `.pre-commit-config.yaml`, and `.git/hooks/` holds only samples. The linter therefore ships as a standalone `python3 scripts/okf_lint.py` rather than a hook. Options: (a) leave standalone, run it in CI; (b) add a real `.pre-commit-config.yaml` and the dependency, which also means fixing the §13 drift; (c) add a plain `.git/hooks/pre-commit` shim with no new dependency. *Recommendation: (a) now, (b) as part of the §13 realignment in decision 4 — a hook that is not installed because the config was never written is worse than no hook, and this leaves the drift visible instead of papering over it.*
6. **The linter found a bug in itself.** `sources[].author: team:...` appears in the OKF v0.2 specification's own normative examples (§5.1 and appendix A) but is not one of the three forms §7 defines. The first version of the check rejected it, making the linter stricter than the document it implements. It now accepts `team:` for `sources[].author` only, with a comment saying why, and still rejects it for `generated.by` / `verified[].by`. A second bug: PyYAML resolves a bare out-of-range scalar such as `2026-13-45` as an implicit timestamp and then raises `ValueError`, which is not a `YAMLError` — so a malformed `stale_after` crashed the linter instead of being reported. Both load sites now catch it.
7. **What Phase 4 is allowed to assert about unimplemented code.** `output_process/evaluation/` (3 files) and `output_process/validation/` (2 files) are zero-byte stubs, and `crew_forge/repo/` + `crew_forge/dependency/` are empty. Writing the obvious requirements for them would produce a spec that validates and describes software that does not exist. Two options: (a) omit them and let the specs be silent; (b) state the boundary as a requirement. *Decision: (b).* `specs/output-process/spec.md` carries an explicit requirement that evaluation and validation are **not** provided, with a scenario requiring the caller be told so rather than handed an empty-but-successful result. Silence would let a client assume a capability exists; a `TBD` would validate. When either is implemented, the requirement is MODIFIED — the spec makes the gap visible instead of hiding it. Same reasoning, applied silently, is why no `crew-forge` requirement promises a shipped repository adapter: the ABCs are specified, the adapters are a client responsibility.
8. **Phase 4 surfaced a real defect in `utils`.** `YamlUtils.yaml_safe_load` handles a missing or unparseable file with `print(...)` followed by bare `exit()` (`utils/yaml_utils.py:16,19`). Inside a library, that raises `SystemExit` and kills the host process instead of surfacing a recoverable error — and it contradicts `AGENTS.md` §5, which forbids bare generic errors for domain conditions. `JsonUtils`, in the same package, already does the right thing (reports and returns `None`). `specs/utils/spec.md` specifies the correct contract — report a configuration error naming the path, do not terminate the host — so the divergence is now a failing spec rather than invisible behaviour. **Not fixed in this pass:** a behaviour change needs its own change, per this proposal's own rule that specs are current-state and changes are separate. Candidate: `fix-utils-yaml-load-failure-handling`.


---

## Phase 0 baseline

Recorded read-only before any change, as the migration checkpoint:

| Metric | Count |
|---|---|
| Source modules under `src/nikhil/amsha/` | 9 |
| Modules served by MCP `RUNTIME_MODULES` | 7 |
| Modules with `docs/feature/` documentation | 4 |
| `.agent/skills/*/SKILL.md` definitions | 26 |
| Packaged MCP docs | 43 |
| Archived proposals | 15 (`00`–`14`) |
| Test files | 32 |
| `AGENTS.md` | 713 lines, 2 diverged copies, 1 gap, 4 stale version refs |

The four counts that disagree — 9 / 7 / 4 — are the gap this proposal closes.

---

## Non-negotiables carried over from earlier proposals

- **Verify against a real LLM, not just mocks.** Same bar as Round 1 (see [00](../archive/00-overview-and-roadmap.md)). For this proposal specifically: a smoke test that the standalone wheel still serves prerequisite docs after Phase 6/7, and that `explain_module("configuration")` works after Phase 2.
- **The standalone wheel must keep working.** Any change under `mcp/src/amsha_mcp/` is a change to a published artifact. Build the wheel and query it with no repo registered.
- **Additive, revertible phases.** Every phase is a `git mv` or an additive file except Phase 1 (content edit) and Phase 2 (code). Phases 3–8 are independently revertable.
