# Tasks: Serve Amsha Product Knowledge from a Packaged OKF Bundle

## 1. Projector

- [x] 1.1 Add `scripts/project_product_knowledge.py` reading `knowledge/features/`,
      `openspec/specs/*/spec.md`, README sections, and `pyproject.toml`
- [x] 1.2 Map 8 Python module names to kebab-case source names; exclude internal
      `common` and retired `crew-gen`
- [x] 1.3 Emit 8 module concepts + `installation.md` + `quickstart.md` + `index.md`
- [x] 1.4 Emit structured install facts (`install_command`, `optional_extra`,
      `requires_python`) from the README section and `requires-python`
- [x] 1.5 Emit section bodies verbatim — no editorial preamble
- [x] 1.6 Add `--check` mode that fails on drift
- [x] 1.7 Verify all generated relative links resolve

## 2. Packaging

- [x] 2.1 Add `("product", "product")` to `MAPPING` in `_build_hooks.py`
- [x] 2.2 Update the build hook docstring to cover both shipped planes
- [x] 2.3 Confirm the build still requires no Amsha repository

## 3. Loader

- [x] 3.1 Add `read_product()` and generalise `_docs_under` to resolve the
      authored path under `knowledge/` (product is not under `methodology/`)
- [x] 3.2 Strip frontmatter for any authored knowledge file, not just methodology
- [x] 3.3 Make `_frontmatter_of` read raw — routed through `_read` it always saw
      already-stripped text and returned `{}`
- [x] 3.4 Add `packaged_install_facts()` reading structured frontmatter
- [x] 3.5 Make `_packaged_section` serve everything after the H1 to EOF, removing
      the sub-heading lookahead that truncated the procedure
- [x] 3.6 Add `product_concept()`; remove the reference to the undefined `_PRODUCT_DOCS`
- [x] 3.7 Rework `runtime_modules()`: packaged concepts supply inventory, purpose,
      and description; a registered repo narrows the list
- [x] 3.8 Fall back to `_packaged_section` for install/quickstart when no repo README

## 4. Tools

- [x] 4.1 `tools/modules.py`: fall back to the packaged concept when a repo has no
      per-module page; drop the absent `docs` key instead of returning `""`
- [x] 4.2 `tools/install.py`: read install facts from packaged knowledge; keep the
      hardcoded dict only as a last-resort fallback for a stripped install
- [x] 4.3 `tools/search.py`: include product knowledge, namespaced `product/…` so its
      `index.md` cannot mask the knowledge bundle's

## 5. Build configuration portability (W1)

- [x] 5.1 Add env > platform > top-level precedence to `build_standalone.py`
- [x] 5.2 Strip machine-specific paths from `build_config.json`
- [x] 5.3 Normalize public env names: `AMSHA_MCP_BUILD_VENV_DIR`,
      `AMSHA_MCP_BUILD_NAME`, `AMSHA_MCP_BUILD_VERSION` (not the doubled or
      JSON-key-derived spellings)
- [x] 5.4 Add macOS platform selection
- [x] 5.5 Fail with the env var name when a required setting is missing
- [x] 5.6 Document the variables in `mcp/docs/PACKAGING.md` and `AGENTS.md`

## 6. Verification

- [x] 6.1 Projection `--check` passes
- [x] 6.2 `scripts/okf_lint.py mcp/knowledge` conformant
- [x] 6.3 `openspec validate --all --strict` passes in `mcp/`
- [x] 6.4 Standalone: all four product tools answer with `AMSHA_MCP_TARGET_REPO`
      unset, and none reference a README the process lacks
- [x] 6.5 Registered repo: module list narrows, source files populate, purposes
      still come from packaged concepts
- [x] 6.6 Wheel contains both planes, frontmatter-free
- [x] 6.7 `source_files_for` remains repository-scoped

## 7. Governance

- [x] 7.1 Proposal, design, tasks, and delta specs written
- [x] 7.2 `packaged-product` capability spec added
- [x] 7.3 `documentation-discovery` and `documentation-build` deltas written
- [x] 7.4 Root `openspec validate --specs --strict` still passes (11 specs)
- [x] 7.5 Archive this change after W3 verification

## 8. W3 build

- [x] 8.1 Bump version 0.1.0 -> 0.2.0 in `pyproject.toml`, `build_config.json`,
      and the `.iss` literal
- [x] 8.2 Build via env config only (`AMSHA_MCP_BUILD_OUTPUT_DIR`,
      `AMSHA_MCP_BUILD_VENV_DIR`), no machine paths in the JSON
- [x] 8.3 Frozen binary built; driven over JSON-RPC stdio with
      `AMSHA_MCP_TARGET_REPO` unset from `cwd=/`
- [x] 8.4 All four product tools answered from the frozen binary
- [x] 8.5 Wheel: 44 docs (24 implementation + 10 prerequisite + 10 product),
      0 starting with `---`, 0 absolute repo paths, `manifest.json` present
- [x] 8.6 Clean-venv wheel install from `cwd=/tmp` serves all four tools
