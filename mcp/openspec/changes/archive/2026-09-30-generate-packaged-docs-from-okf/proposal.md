# Proposal: Generate Packaged Methodology Docs from an MCP-Local OKF Bundle

## Why

`mcp/` had no OpenSpec specs and no OKF bundle of its own. Everything it knew
about itself lived in the Amsha repository root, where `openspec/specs/`
described the library and `knowledge/` described Amsha's modules — not the
server. Its own behaviour was specified nowhere and linted by nothing.

The product plane made this worse. The 43 methodology documents under
`mcp/src/amsha_mcp/docs/` were authored **inside the installed package tree**,
which is why the layout was frozen: `_STAGE_DOC` hardcodes 10 prerequisite
filenames, and `get_preview()` preserves every non-empty line, so frontmatter
would leak into agent-visible text.

The target state separates the concerns:

- **Author** in a repo-side OKF bundle, `mcp/knowledge/`, with real frontmatter.
- **Materialize** at build time into the wheel, frontmatter removed.
- **Specify** the server's own behaviour in `mcp/openspec/specs/`.

## What Changes

1. **New OKF bundle at `mcp/knowledge/`** — 46 files: 43 concepts plus three
   indexes. The 34 runtime documents live in `methodology/`
   (`prerequisite/` 10, `implementation/` 24); the 9 superseded proposals live
   in `records/proposal-archive/`. Bodies preserved verbatim; frontmatter added.

2. **New `mcp/src/amsha_mcp/_build_hooks.py`** — a `setuptools.command.build_py`
   subclass, wired through `[tool.setuptools.cmdclass]` in `mcp/pyproject.toml`.
   On every build it materializes the 34 documents into
   `build_lib/amsha_mcp/docs/` and declares them via `get_outputs()`. Because
   the hook is attached to `build_py`, *every* packaging path gets the product
   plane: `pip install`, wheel, sdist, and the PyInstaller freeze. No manual
   step, nothing to forget.

3. **`mcp/src/amsha_mcp/docs_loader.py` gained a source-checkout fallback.**
   `_AUTHORED_DOCS` points at `mcp/knowledge/methodology/`, and `_read()` strips
   frontmatter for any path under it. A developer running from a source tree
   serves the full methodology with no build at all.

4. **`mcp/scripts/sync_packaged_docs.py`** — a manual helper that stages the
   same content into `mcp/build/package-docs/`. It imports the mapping and
   renderer from `_build_hooks`, so there is one source of truth for the
   mapping rather than two that can drift. `--check` verifies.

5. **The product plane left `src/` entirely.** `mcp/src/amsha_mcp/docs/` is no
   longer tracked and no longer authored in; `mcp/.gitignore` covers
   `build/package-docs/`.

6. **New current-state specs** in `mcp/openspec/specs/`: `packaged-documentation`,
   `documentation-build`, and `documentation-discovery`.

## Impact

- **Published wheel contents changed: 43 documents → 34.** The 9 archived
  proposals are no longer packaged. This is a deliberate reduction (see design
  D2) and is stated here because `openspec/config.yaml` requires it.
- **Standalone operation preserved.** Product knowledge still needs no
  repository, and the build hook runs at build time, never at runtime.
- **`get_preview()` contract preserved.** Both the build hook and the read-time
  fallback strip frontmatter, so no frontmatter can reach agent-visible text.
- **`read_proposal()` removed** along with its plane. This resolves the defect
  recorded in `mcp/openspec/config.yaml`, which claimed `read_proposal()` served
  the archived proposals when in fact its non-recursive glob over
  `docs/proposal/*.md` returned zero. The plane is gone rather than repaired.
  The 9 proposals remain available on the repo plane via
  `mcp/knowledge/records/`.
- **No contributor step.** Because generation is a build hook and the loader
  falls back to the bundle, a fresh clone works with no extra command. This was
  the main weakness of the discarded alternative, which required a manual
  `gitignore`d script run and would have broken editable installs.

## Out of Scope

- Converting document *content*. Only frontmatter was added.
- The Amsha repository-root `knowledge/` bundle and root `openspec/`.
- Reinstating the archived proposals into the runtime payload.
