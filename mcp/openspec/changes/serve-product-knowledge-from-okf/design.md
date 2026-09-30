# Design: Serve Amsha Product Knowledge from a Packaged OKF Bundle

## Context

The MCP server serves two knowledge planes:

| Plane | Source | Ships in wheel? |
|---|---|---|
| Methodology | `mcp/knowledge/methodology/` | Yes — 34 documents |
| Product | *did not exist* | *nothing* |

Methodology was solved by commit `15906f9`. Product was not, and the gap is
user-visible: with no target repository registered, `list_amsha_modules()`
returns `{}` and `get_quickstart()` returns a string pointing at a README the
process does not have.

## Goals / Non-Goals

**Goals**
- Answer "what is Amsha, what are its modules, how do I install it" with no repository.
- No hand-maintained copy of documentation that already exists.
- Drift between the Amsha repo and the MCP's copy is detectable in one command.
- `mcp/` remains buildable and copyable standalone.

**Non-Goals**
- Deleting the fallback inventory.
- Repository-specific capabilities (`source_files_for`).
- Restructuring the Amsha root `knowledge/` bundle.

## Decisions

### Decision 1: Project from existing artifacts, do not author

Amsha already states its module purposes in `knowledge/features/*.md`, its
behaviour in `openspec/specs/*/spec.md`, and its install/quickstart in the
README. Hand-authoring MCP-side copies would create a second source of truth that
drifts silently.

So `scripts/project_product_knowledge.py` is a **projector**: pure function from
repo artifacts to `mcp/knowledge/product/`. Every value in the output is either
copied verbatim or mechanically derived.

```
knowledge/features/<kebab>.md ──┐
openspec/specs/<kebab>/spec.md ─┼─> mcp/knowledge/product/<kebab>.md
README ## Installation/Quick Start ┘        (committed, --check for drift)
pyproject.toml requires-python ──┘
```

**Why commit the output rather than generate at build time?** The build must not
depend on the repository, or the wheel cannot be built from `mcp/` alone. The
projection is a *provenance* step that happens in the repo; the build is a pure
consumer. `--check` in any validation run keeps the two honest.

**Why not point the loader at the Amsha repo?** Because that is exactly the
repo-dependence being removed. It also means the wheel could never answer.

### Decision 2: Module inventory comes from packaged concepts, repo only narrows

Current `runtime_modules()` intersects `RUNTIME_MODULES` with directories found
in the target repo. That conflates two different questions:

- *What modules does Amsha have?* — a **product** fact, invariant across repos.
- *Which modules does this checkout have?* — a **repo** fact, legitimately
  varying (a pinned older Amsha).

Conflating them made the product answer depend on the repo. Now the packaged
concepts supply the inventory, purposes, and an optional description, and a
registered repo filters the list to the intersection it actually contains.

**Consequence:** with a repo registered, `list_amsha_modules()` may return
fewer than 8 modules. That is correct, not a regression.

`RUNTIME_MODULES` is kept as the declared inventory so a missing concept is
detectable, and `_MODULE_PURPOSE` as the last-resort purpose if the product
plane is missing entirely.

### Decision 3: Sections are structured, not prose

`install.py` hardcoded `python: ">=3.12,<3.14"`. That constraint appears **nowhere**
in the README — it exists only in `pyproject.toml` as `requires-python`.

Rather than keep an asserted constant or parse prose at runtime, the projector
emits the facts into the concept's frontmatter (`install_command`,
`optional_extra`, `requires_python`) and the loader reads them. The Markdown body
stays the human-readable procedure; the frontmatter is the machine contract.

The body of a section concept is the source section **verbatim**, with no
editorial preamble. This matters: the loader serves everything after the H1, so
any prose the projector added would be returned to the caller as though it were
part of the procedure. An earlier draft prepended "Generated from the README…"
and it leaked straight into `get_quickstart()` output. Provenance lives in
frontmatter instead.

### Decision 4: Product metadata survives frontmatter stripping

The build strips frontmatter from packaged documents, so a packaged concept has
no `module:`/`section:` fields and `_frontmatter_of` cannot recover them from a
wheel. Yet `_packaged_module_purposes` and `_packaged_section` both need them.

Resolution, split by origin:
- **Authored** (source checkout): parse frontmatter, then strip it before serving.
  `_frontmatter_of` must read the file *raw* — routing it through `_read` would
  hand it already-stripped text and always yield `{}`.
- **Packaged** (wheel): derive the module from the filename
  (`crew-forge.md` → `crew_forge`) and the section from a fixed
  filename→section map, taking the purpose from the first prose line after the
  H1.

No manifest file is needed, and no frontmatter reaches the caller.

## Risks / Trade-offs

- **Duplication on disk.** `mcp/knowledge/product/` is a committed copy of repo
  content. Accepted: it is the price of a self-contained wheel, and `--check`
  bounds the staleness window.
- **Loose product plane in the MCP bundle.** Product concepts are shipped
  *stripped of frontmatter* while the authored tree keeps it, so the two differ
  byte-wise by design. `--check` compares against the projection, not the tree.
- **Filename-derived packaged metadata.** If a concept is ever renamed without
  updating `SECTION_SLUG`, the packaged path silently loses metadata. Mitigated
  by `--check` and by the fact that `_packaged_module_purposes` returns `{}`
  loudly enough to fall back to `_MODULE_PURPOSE`.

## Migration

1. Run the projector; commit `mcp/knowledge/product/` (11 files).
2. Add `("product", "product")` to `MAPPING` in `_build_hooks.py`.
3. Rewire `docs_loader`, `tools/modules.py`, `tools/install.py`, `tools/search.py`.
4. Add the `packaged-product` capability spec; update `documentation-discovery`
   for the narrowed-repo semantics.
5. Validate, build, verify standalone, bump version.

## Open Questions

None blocking. Deferred: whether the root Amsha bundle should ever be
regenerated *into* the MCP tree by the same process (it is projected in the
opposite direction today).
