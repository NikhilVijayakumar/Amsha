# Design: Generate Packaged Methodology Docs from an MCP-Local OKF Bundle

## Context

Two `docs/` directories exist under `mcp/` with opposite meanings, which is the
confusion this change resolves:

| Path | Meaning | Shipped? |
|---|---|---|
| `mcp/docs/` | Human docs: `PACKAGING.md`, `mcp-validations/` | No |
| `mcp/src/amsha_mcp/docs/` | Product plane: 43 LLM reference files | Yes, in the wheel |

The product plane is authored inside the installed package tree. That is the
root cause of three hard constraints, all of which this design must respect
rather than work around:

1. `_STAGE_DOC` (architecture.py) hardcodes 10 exact prerequisite filenames.
2. `read_prerequisite()` / `read_implementation()` / `read_proposal()` glob
   direct children of fixed directories.
3. `get_preview()` (docs_loader.py) keeps every non-empty line that is not a
   table row or a fence. YAML frontmatter is non-empty lines, so frontmatter
   leaks into agent-visible prose.

## Goals / Non-Goals

**Goals**
- One authoring home for the 43 documents, outside `src/`.
- Real OKF v0.2 metadata on all 43.
- Byte-identical wheel output.
- A CI-enforceable guarantee that packaged docs match the bundle.
- The server's own behaviour specified in `mcp/openspec/specs/`.

**Non-Goals**
- Rewriting document content.
- Fixing the unreachable `proposal/archive/` plane (tracked separately).
- Restructuring the repo-root `knowledge/` bundle.

## Decisions

### D1 — Frontmatter is stripped at packaging, not authored twice

The source (`mcp/knowledge/`) carries full OKF frontmatter. The packaged output
(`src/amsha_mcp/docs/`) is body-only.

**Alternative rejected:** author the 43 files with no frontmatter and keep OKF
metadata in a sidecar manifest. Rejected because the sidecar is a second source
of truth that can drift from the files it describes, and it is the pattern the
repo-root bundle exists to eliminate.

**Consequence:** constraint (3) above is satisfied structurally. `get_preview()`
never sees frontmatter because there is none in the packaged file. This is
strictly safer than the status quo, where adding frontmatter to a packaged file
would silently corrupt agent output.

### D2 — Directory mapping is explicit, not inferred

The generator holds a hardcoded mapping. It does not derive destinations from
the knowledge layout.

| Source (repo-side) | Destination (packaged) | Count |
|---|---|---|
| `methodology/prerequisite/*.md` | `docs/prerequisite/*.md` | 10 |
| `methodology/implementation/*.md` | `docs/implementation/*.md` | 24 |
| `records/proposal-archive/*.md` | `docs/proposal/archive/*.md` | 9 |

**Alternative rejected:** infer the destination from the OKF kind directory
(`methodology/` → `docs/methodology/`). Rejected because it couples the wheel
layout to OKF's taxonomy. The two will legitimately diverge — `records/` is not
an OKF-v0.2-conventional kind, and the packaged path is `proposal/archive/`.

### D3 — `records/` is a new kind directory

The 9 archived proposals are historical records, not methodology and not
current concepts. They get `type: Record` and `status: deprecated`.

This is a deliberate deviation from the four conventional kinds
(features/methodology/contracts/decisions), justified because the alternative —
filing superseded proposals as active methodology — is semantically wrong and
would misrepresent them to an agent that reads `knowledge/`.

### D4 — Methodology files omit `stale_after` and `verified[]`

Both are optional in OKF v0.2. Methodology is a stable, human-reviewed corpus
with no expiry model, and there is no automated verifier that can attest to a
prose document's correctness today. Fabricating either field would produce
metadata that looks authoritative and is not.

`verified[]` entries belong only on concepts a deterministic tool can check.
The repo-root `knowledge/` bundle already does this correctly for Amsha's
modules, and this change does not extend that pattern to prose.

### D5 — Generated output is gitignored, and the check is the safety net

`mcp/src/amsha_mcp/docs/` is removed from git and ignored.

**Trade-off accepted:** a contributor who runs `pip install -e .` without
generating gets an importable package whose `read_prerequisite()` returns
`{}` — a silent degradation, not a crash. Mitigations:
- the build pipeline generates before building, so no shipped artifact is stale;
- `--check` runs in CI and fails the build on drift or absence;
- `docs_loader` is unchanged, so the failure surface stays small.

The alternative (committing generated output) preserves editable-install
safety but keeps the build artifacts tracked in `src/`, which is the thing this
change exists to remove.

## Risks / Trade-offs

- **Silent empty product plane in a fresh editable checkout.** Accepted per D5.
  The check makes it a CI failure rather than a shipped defect.
- **Two-step local workflow.** Documented in `mcp/docs/PACKAGING.md` and
  `AGENTS.md`.
- **Generator drift from the wheel.** Neutralized by `--check`, which compares
  the materialized tree against the committed one before any build.

## Migration Plan

1. Create `mcp/knowledge/` with all 43 concepts, bodies byte-identical.
2. Add indexes and run `scripts/okf_lint.py mcp/knowledge`.
3. Write the generator; confirm it reproduces the current `docs/` tree exactly.
4. Only after (3) passes: `git rm` the packaged tree and ignore it.
5. Wire into `mcp/packaging/`; rebuild the wheel; diff against the old wheel.
6. Add `mcp/openspec/specs/`; rewrite `mcp/openspec/config.yaml`.
7. Update `AGENTS.md` §14 and proposal 15 to describe the new model.

## Open Questions

- None blocking. The `proposal/archive/` reachability defect is deliberately
  deferred to `fix-proposal-plane-reachability`.
