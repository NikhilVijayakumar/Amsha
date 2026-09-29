# Proposal: Generate Packaged Methodology Docs from an MCP-Local OKF Bundle

## Why

`mcp/` has no OpenSpec specs and no OKF bundle of its own. Everything it knows
about itself lives in two places that both belong to the Amsha repository root:

- `openspec/specs/` — describes the Amsha library, not `amsha-mcp`.
- `knowledge/` — describes Amsha's modules, not the server.

So the server's own behaviour is unspecified. Its 24 tools, the two knowledge
planes, the verification methodology, and the packaging contract have no
durable record, and no lint checks them.

Meanwhile the product plane — the 43 methodology files under
`mcp/src/amsha_mcp/docs/` — is authored inside the installed package tree. That
means the files an LLM reads at runtime are the same files tracked in `src/`,
which is why the layout is frozen: `_STAGE_DOC` hardcodes 10 filenames and
`get_preview()` does not strip frontmatter.

The target state separates the concerns properly:

- **Authoring** happens in a repo-side OKF bundle, `mcp/knowledge/`, with real
  OKF v0.2 frontmatter (lifecycle fields, verification evidence).
- **Shipping** is a build step that materializes that bundle into
  `src/amsha_mcp/docs/` with frontmatter stripped, preserving every filename
  and every body byte.
- **Contract** is written down in `mcp/openspec/specs/`, so the server's own
  behaviour is specified rather than inferred.

## What Changes

1. **New OKF bundle at `mcp/knowledge/`.** All 43 product-plane documents
   become OKF concepts. Bodies are preserved verbatim; only frontmatter is
   added. Layout:
   - `methodology/prerequisite/` — 10 files (stages 00-09)
   - `methodology/implementation/` — 24 files (topics 00-23)
   - `records/proposal-archive/` — 9 files (archived proposals 00-08)
2. **New generator `mcp/scripts/sync_packaged_docs.py`.** Maps the bundle to
   the package layout, strips frontmatter, writes `src/amsha_mcp/docs/`.
   `--check` fails on drift without writing, for CI.
3. **`mcp/src/amsha_mcp/docs/` becomes generated, not authored.** Removed from
   git, added to `.gitignore`, and produced by the generator.
4. **Wired into the existing build pipeline** (`mcp/packaging/`) so no build
   path can ship a stale or missing product plane.
5. **New current-state specs in `mcp/openspec/specs/`** for the product plane
   and the documentation build.
6. **`mcp/openspec/config.yaml` rewritten** — its current rule
   ("do not add YAML frontmatter to them") describes the old model and is
   inverted by this change. It becomes: frontmatter lives in the source, the
   packaged output is body-only.

## Impact

- **Wheel contents: unchanged.** 43 files, identical filenames, identical
  bytes. Verified by rebuilding the wheel and diffing against the current
  packaged tree.
- **Standalone operation: preserved.** Product knowledge still requires no
  repository. The generator runs at build time, never at runtime.
- **`get_preview()` contract: preserved.** Packaged output is body-only, so
  frontmatter cannot leak into agent-visible text.
- **New failure mode introduced: a missing build step.** A contributor doing
  `pip install -e .` without running the generator gets no `docs/`. Mitigated
  by `--check` in CI, by running the generator from the build pipeline, and by
  `MANIFEST`/packaging checks; documented as an explicit contributor step.
- **Adopted decision:** the 43 product-plane files become genuine OKF
  concepts. OKF lifecycle fields describe the document, not the product, so
  `stale_after` and `verified[]` are left off the methodology files rather
  than invented to fill the schema.

## Out of Scope

- **`read_proposal()` returns zero files.** `_docs_under("proposal")` globs
  `docs/proposal/*.md`, but all 9 archived proposals live in
  `docs/proposal/archive/`. They are packaged and unreachable. This change
  preserves the layout so the wheel stays identical, and records the defect
  rather than silently fixing it. A separate change
  (`fix-proposal-plane-reachability`) should decide whether to flatten the
  directory or make the glob recursive — either alters wheel layout and search
  results, so it must not ride along with a refactor.
- Repository-root `knowledge/` and root `openspec/`. Untouched.
- Converting the 43 documents' *content*. Only frontmatter is added.
