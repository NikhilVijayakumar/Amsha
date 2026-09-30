# Design: Generate Packaged Methodology Docs from an MCP-Local OKF Bundle

## Context

Two `docs/` directories under `mcp/` had opposite meanings, which was the
confusion this change resolved:

| Path | Meaning | Shipped? |
|---|---|---|
| `mcp/docs/` | Human docs: `PACKAGING.md`, `mcp-validations/` | No |
| `mcp/src/amsha_mcp/docs/` | Product plane: LLM reference files | Yes, in the wheel |

The product plane was authored inside the installed package tree, producing
three constraints that any design had to respect:

1. `_STAGE_DOC` hardcodes 10 exact prerequisite filenames.
2. The loaders glob fixed directories.
3. `get_preview()` keeps every non-empty line that is not a table row or fence,
   so frontmatter would leak into agent-visible prose.

## Goals / Non-Goals

**Goals**
- One authoring home for the documents, outside `src/`.
- Real OKF v0.2 metadata.
- Frontmatter must never reach an agent.
- No manual step, and no break for editable installs.
- The server's own behaviour specified and linted.

**Non-Goals**
- Rewriting document content.
- Reinstating superseded proposals into the runtime payload.
- Touching the repo-root bundle.

## Decisions

### D1 — Frontmatter is stripped in two places, both structural

The source (`mcp/knowledge/`) carries full OKF frontmatter. The product form
never does. Two code paths enforce this independently:

- **Build time** — `_build_hooks.render_authored_doc()` strips it before writing
  into `build_lib/amsha_mcp/docs/`.
- **Read time** — `docs_loader._read()` strips it for any path under
  `_AUTHORED_DOCS`, which is how a source checkout is served.

Neither is a convention; both raise on malformed frontmatter rather than
falling through, so a missing or unterminated block is a build error, not
silently-corrupt agent output.

### D2 — The 9 archived proposals leave the runtime payload

`MAPPING` covers only `methodology/prerequisite` and
`methodology/implementation` — 34 documents. `records/proposal-archive/` is not
mapped, and `read_proposal()` was removed.

**Rationale.** These are superseded design records: each documents a phase that
later shipped in a different form, and several contain scope decisions since
revised. Serving them as current methodology to an LLM invites it to cite
rejected decisions. They remain on the **repo** plane at
`mcp/knowledge/records/`, where a human or a repo-scoped search can still reach
them.

**Consequence, stated plainly: the published wheel drops from 43 documents to
34.** This also disposes of a real defect. `read_proposal()` globbed
`docs/proposal/*.md` — direct children only — while all 9 files sat in
`docs/proposal/archive/`, so it returned **zero** documents, and
`openspec/config.yaml` had asserted otherwise. Rather than fix the glob, the
plane is removed, so the config claim and the code now agree.

### D3 — Generation is a `build_py` hook, not a called script

`_build_hooks.build_py` overrides `setuptools.command.build_py`, wired in
`pyproject.toml` under `[tool.setuptools.cmdclass]`, and declares its outputs in
`get_outputs()`.

**Alternatives rejected:**

- *Standalone script invoked by `build_standalone.py`* — only covers the
  PyInstaller path. A plain `pip install` or `pip wheel` would silently produce
  a wheel with no methodology.
- *Generated files committed under `src/`, with a `gitignore` alternative* —
  keeps build artifacts in the source tree, and a contributor with a stale tree
  has no way to tell.

**Consequence:** every packaging path is covered by construction, and a fresh
clone needs no preparation step.

### D4 — The loader falls back to the bundle in a source checkout

`_AUTHORED_DOCS = PACKAGE_ROOT.parent.parent / "knowledge" / "methodology"`,
and `_read()` strips frontmatter for paths under it.

Without this, a source-tree run would serve nothing, because `docs/` only exists
inside a built artifact. This is what makes D3 safe: the build hook covers
packaged use, the fallback covers development use, and neither is a manual step.

### D5 — One source of truth for the mapping

`scripts/sync_packaged_docs.py` imports `authored_doc_mappings`,
`render_authored_doc`, and `materialize_package_docs` from `_build_hooks`. The
helper exists to stage a reviewable tree and to support `--check`; it does not
re-implement the mapping.

**Why this matters:** an earlier draft of this change had the mapping expressed
twice — in a standalone script and nowhere else. Two copies of a path map drift
silently, and the drift would only surface as a wheel missing a stage.

## Risks / Trade-offs

- **A source-tree run and a built artifact could theoretically disagree.** Both
  derive from the same bundle and both strip frontmatter, so they cannot
  disagree in content — only in the timing of regeneration, and neither caches.
- **`build/package-docs/` is a generated staging tree.** It is git-ignored and
  disposable; `--check` treats its absence as "bundle is build-ready" rather
  than an error, because a fresh clone legitimately has none.
- **34 documents is fewer than before.** Accepted under D2; the material is not
  lost, only moved to the repo plane.

## Migration Outcome

All steps completed. Verified after the fact:

- `python3 scripts/okf_lint.py mcp/knowledge` → 43 concepts, conformant.
- `cd mcp && openspec validate --all --strict` → 5 passed, 0 failed.
- Wheel → 34 packaged docs, **0** with frontmatter, 0 `knowledge/`, 0
  `openspec/`, `amsha_mcp/_build_hooks.py` present.
- Source checkout → 10 prerequisite + 24 implementation served via the fallback,
  with no frontmatter token present in `get_preview()` output.

## Open Questions

None. The `proposal/archive/` reachability defect is closed by D2.
