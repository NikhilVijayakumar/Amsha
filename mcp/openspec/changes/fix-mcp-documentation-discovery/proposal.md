# Proposal

## Why

Two defects make the MCP server silently return incomplete or empty answers.

**Prerequisite documentation is never returned.** `tools/architecture.py:53` resolves prerequisite docs as `repo_root()/mcp/docs/prerequisite/<stage>`. That directory does not exist — `mcp/docs/` contains only `PACKAGING.md` and `mcp-validations/`. The bundled docs live at `mcp/src/amsha_mcp/docs/prerequisite/`, which is the packaged location that `docs_loader.read_prerequisite()` already resolves. The `except OSError: return ""` on line 56 absorbs the failure, so the `"doc"` field at line 112 is always an empty string. The commit `ccc8f4c` ("fix broken proposal-08 link in PACKAGING.md after docs move") records the move; this path was not updated with it. An agent in an architecture session therefore receives stage guidance as an empty string and has no indication anything failed.

**One source module is unreachable.** `docs_loader.RUNTIME_MODULES` lists 7 of the 9 modules under `src/nikhil/amsha/`. `common` is excluded deliberately, documented in the comment at `docs_loader.py:122`. `configuration` is absent with no stated reason. Because `runtime_modules()` filters the directory listing to that constant, `list_amsha_modules()` omits it and `explain_module("configuration")` can never return it. `configuration` has a full `domain/`, `application/`, `infrastructure/` and `exceptions/` layout and is a real capability.

Both are the same class of fault: the server's own model of the repository has drifted from the repository, and neither drift is surfaced to the caller.

**A third defect, found while verifying the first two, disables every repository-sourced tool outside a server process.** `docs_loader` declares a lazy-initialization contract: `repo_root()` self-initializes on first access so "any caller works correctly whether or not amsha_mcp.server ... has been imported in this process" (`docs_loader.py:30-33`, restated in the `resolve_default_repo` docstring). All six repository-plane accessors nevertheless read the module global `_REPO_ROOT` directly — `read_top_level_markdown`, `read_features_docs`, `runtime_modules`, `source_files_for`, `extract_quickstart`, `extract_installation`. None calls `repo_root()`. Before resolution runs, the global is `None`, so all six return empty.

In a live MCP session `server.py` imports first and resolves eagerly, so the tools happen to work. Every other caller — a test, a script, any direct library use — silently gets nothing. This was found by verifying the second defect: `runtime_modules()` still returned `{}` with `AMSHA_MCP_TARGET_REPO` set, which is what exposed the global being read uninitialized. The documented guarantee was dead code, and the fix to the inventory could not be verified outside a server process without also fixing this.

## What Changes

- `tools/architecture.py` resolves prerequisite documentation through the `docs_loader` accessor (`read_prerequisite()`) instead of reconstructing a path from the repository layout.
- `docs_loader.RUNTIME_MODULES` gains `configuration` and a purpose line for it.
- All six repository-plane accessors resolve through `repo_root()` rather than reading `_REPO_ROOT`, making the documented lazy-initialization contract true.
- No change to the bundled docs themselves; they stay byte-identical and remain the authoritative runtime artifact.
- No change to the standalone-wheel property. The fix makes the code use the packaging mechanism that already guarantees it.

## Capabilities

### New Capabilities

- `documentation-discovery`: How the MCP locates and serves its bundled methodology documentation, and how it enumerates the Amsha runtime modules it will answer questions about. Covers the product/repo knowledge-plane split, packaged-path resolution, module inventory completeness, lazy resolution of the target repository, and the requirement that a lookup failure is never silently reported as an empty success.

### Modified Capabilities

None. `mcp/openspec/specs/` is empty; this is the first change in this root.

## Impact

**Code**

- `mcp/src/amsha_mcp/tools/architecture.py` — `_stage_content()` path resolution
- `mcp/src/amsha_mcp/docs_loader.py` — `RUNTIME_MODULES`, `_MODULE_PURPOSE`, and the six repository-plane accessors

**Behaviour**

- `submit_stage_artifact()` returns real stage documentation instead of `""`
- `list_amsha_modules()` and `explain_module()` cover `configuration`
- All repository-plane tools return real content when used as a library, not only under `server.py`

**Not affected**

- `mcp/src/amsha_mcp/docs/` — 43 files, byte-identical, still `package-data`
- The wheel's standalone operation; `mcp/docs/` is not read by the loader
- Public tool signatures — all three fixes are internal to existing functions
- Live MCP sessions, which already resolved eagerly; behaviour there is unchanged
