# Tasks

## 1. Fix prerequisite documentation resolution

- [x] 1.1 Replace the repository-derived path in `_stage_content()` (`tools/architecture.py:52-57`) with a lookup through `dl.read_prerequisite()` keyed by `_STAGE_DOC[stage]`, and verify by calling it for all ten stages `00`-`09` and confirming each returns non-empty content
- [x] 1.2 Make the absent-document case distinguishable from an empty document, and verify a stage with no packaged file reports the absence rather than returning `""`
- [x] 1.3 Confirm the resolved path lies under the package directory and not under the repository, and verify the test fails if `_DOCS` is temporarily pointed at an empty directory

## 2. Complete the runtime module inventory

- [x] 2.1 Add `configuration` to `RUNTIME_MODULES` and a `_MODULE_PURPOSE` entry for it, and verify `runtime_modules()` includes it
- [x] 2.2 Retain and clarify the inline comment documenting why `common` is excluded, and verify `runtime_modules()` still omits `common`
- [x] 2.3 Verify an inventory entry naming an absent directory is omitted rather than returned, by checking the filter at `docs_loader.py:150`

## 3. Make lazy target-repo resolution real

- [x] 3.1 Replace direct `_REPO_ROOT` reads with `repo_root()` in all six repository-plane accessors, and confirm the only remaining `_REPO_ROOT` references are in the resolution machinery (`configure_repo_root`, `repo_root`, `resolve_default_repo`)
- [x] 3.2 In a process that never imports `amsha_mcp.server`, verify with `AMSHA_MCP_TARGET_REPO` set that `runtime_modules()`, `read_top_level_markdown()`, `read_features_docs()`, `source_files_for()`, `extract_quickstart()` and `extract_installation()` all return real content
- [x] 3.3 Verify the same accessors still return their documented empty values when no repository is registered, and that calling them twice does not change the resolved root

## 4. Verify all fixes end to end

- [x] 4.1 Run the existing `mcp` test suite and confirm no regression against the pre-change baseline
- [x] 4.2 Exercise `explain_module("configuration")` and confirm it returns a purpose and source files
- [x] 4.3 Build the wheel and confirm `mcp/src/amsha_mcp/docs/` is present in it, so standalone operation still carries its documentation
- [x] 4.4 Confirm with no repository registered that prerequisite documentation still resolves, so the packaged plane is independent of `AMSHA_MCP_TARGET_REPO`
- [x] 4.5 Confirm the 43 bundled docs are byte-identical to their pre-change state
