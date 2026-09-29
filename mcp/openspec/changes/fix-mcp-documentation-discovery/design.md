# Design

## Context

`docs_loader.py` already encodes the two knowledge planes. `_DOCS` is
`PACKAGE_ROOT / "docs"` (line 25), read unguarded at line 77, so packaged
docs always resolve. Every repo-sourced accessor returns `{}` behind
`if not _REPO_ROOT` (lines 98, 106, 146, 160, 192, 203), so repository
docs degrade to empty. The module docstring states the intent directly:
*"These never depend on an outer-repo layout; a standalone wheel carries
them."*

The defect is that `tools/architecture.py` bypasses that abstraction. It
imports `docs_loader as dl`, calls `dl.repo_root()`, then joins a path
against it — reaching for a repository location to find a packaged
artifact. The abstraction was available and unused.

`RUNTIME_MODULES` (lines 123-131) is a hand-maintained list checked against
the source directory at line 150. It is the only place a module can be
declared, and `configuration` was never added.

Separately, `docs_loader` documents a lazy-resolution contract twice — in the
`_repo_resolved` comment (lines 30-33) and in the `resolve_default_repo`
docstring ("lazily (`repo_root()`, for any caller that imports tools directly
without going through server.py)"). All six repository-plane accessors bypass
it and read `_REPO_ROOT` directly. `repo_root()` had no callers in the module.

## Goals / Non-Goals

**Goals:**

- `_stage_content()` returns real content, or an explicit signal that none exists.
- The fix routes through an existing accessor rather than correcting a literal path.
- `configuration` becomes discoverable and explainable.
- The documented lazy-resolution contract holds for direct library callers.
- The standalone-wheel property is preserved and demonstrably unchanged.

**Non-Goals:**

- Removing the hand-maintained `RUNTIME_MODULES` constant, or deriving purposes
  automatically. Purpose strings are editorial; deriving them is a larger design
  question and `common` needs an explicit rationale that a heuristic would lose.
- Adding frontmatter to, or restructuring, the 43 bundled docs.
- Changing any public tool signature or the MCP protocol surface.
- Touching `mcp/docs/`, which the loader does not read.

## Decisions

**Resolve through `dl.read_prerequisite()`, not through a corrected literal.**

`_stage_content()` becomes a dict lookup against the accessor's result,
keyed by the existing `_STAGE_DOC` filename. Rationale: the accessor is the
single place that knows where packaged docs live, and it is already correct.
Correcting the literal to `mcp/src/amsha_mcp/docs/prerequisite/` would fix
this instance while leaving the abstraction bypassed, so the same drift
recurs the next time packaging moves.

Alternative considered: derive the path from `PACKAGE_ROOT`. Rejected — it
reimplements what the accessor already does, and adds a second thing to keep
in sync.

**Distinguish "absent" from "empty".**

The current `except OSError: return ""` conflates two states. The
replacement distinguishes a stage with no packaged document from a stage
whose document is genuinely empty, so a caller is never handed a blank
string that reads as success.

Alternative considered: leave the empty-string return and let callers cope.
Rejected — it is the mechanism that hid this defect; preserving it preserves
the blindness.

**Add `configuration`; keep `common` excluded.**

`configuration` is a user-facing capability with a full layer structure and
no stated reason for exclusion, so it is added with a purpose line. `common`
holds the logger and rotation helpers and is documented in the inventory
comment as not user-facing, so it stays excluded — but the comment is
retained explicitly so the exclusion keeps its stated rationale, which
OpenSpec's "Internal module is excluded" scenario requires.

**Do not treat this as a documentation-only change.**

Both fixes are code. The archived proposal that moved the docs
(`ccc8f4c`) touched documentation and silently broke a code path. That is
the coupling this change exists to break.

**Call `repo_root()` in all six accessors rather than caching its result.**

Reading `_REPO_ROOT` directly is faster by a `None` check, and was
presumably done for that reason. It also means the accessors are correct
only when some other module happened to resolve the global first — an
invariant enforced by nothing but the current import order in `server.py`.
The cost of the correct version is one function call.

Alternative considered: make `_REPO_ROOT` resolve at import time via a
`__getattr__`-style module proxy. Rejected as over-engineered; it hides
resolution behind attribute access and makes the data flow harder to
follow, for a saving of one `if` per call.

**Scope the lazy-init fix into this change rather than splitting it out.**

It is a different symptom from the other two, so a separate change would be
defensible. But it lives in the same file, is six mechanical edits, and the
inventory requirement cannot be verified outside a server process without
it — a change whose own acceptance criteria are unverifiable in the common
case is worse than a slightly wider one. Fixing it here also restores the
guarantee that Phase 7's `knowledge/` work depends on: the new plane-2
accessors must be reachable from a test.

## Risks / Trade-offs

- **[Risk] Changing `docs_loader.RUNTIME_MODULES` shifts every list/inventory
  tool's output.** → Mitigation: additive only. No existing entry is removed
  or reworded, so no prior answer changes; the module list only grows.

- **[Risk] Making lazy init effective turns on five previously-dead
  code paths** for any caller that does not import `server.py`. → Mitigation:
  each accessor already returns a documented empty value when the repository
  is absent, and that branch is now genuinely reachable. Task 3.1 runs the
  suite and task 3.2 exercises the tools directly.

- **[Risk] A caller may have learned to treat an empty `doc` field as normal.**
  → Mitigation: that is the bug. The spec pins the new behaviour, and the
  fix is a strict improvement in information delivered.

- **[Trade-off] `RUNTIME_MODULES` stays hand-maintained.** Accepted for this
  change. The consistency check this enables — comparing the inventory
  against the Amsha `knowledge/` bundle — is the mechanism that will catch a
  future omission, which is cheaper than automating editorial purpose strings.
