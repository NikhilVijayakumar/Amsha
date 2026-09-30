# Proposal: Serve Amsha Product Knowledge from a Packaged OKF Bundle

## Why

Four product tools only worked when a target repository was registered. With
`AMSHA_MCP_TARGET_REPO` unset — the normal state of an installed wheel — the
server was hollow:

```
list_amsha_modules       -> {'modules': {}}                    empty
explain_module(config)   -> error: "Unknown module"            broken
get_install_instructions -> {'install': 'pip install amsha'}   hardcoded, 1 of 4 fields
get_quickstart           -> "See README.md → Quick Start"     points at a README it lacks
```

The cause: `runtime_modules()` intersected its hardcoded inventory with
directories found in the target repo's `src/nikhil/amsha/`, and
`extract_installation()` / `extract_quickstart()` parsed the target repo's
README. Both are *repo-plane* reads, but the questions they answer are
**product-plane** questions — what modules does Amsha have, and how do you
install it. Amsha's answer does not change with whichever repo the server
happens to be pointed at.

## What Changes

1. **Product knowledge is projected, not authored.**
   `scripts/project_product_knowledge.py` reads the artifacts that already
   exist — `knowledge/features/*.md`, `openspec/specs/*/spec.md`, the README's
   Installation and Quick Start sections, and `requires-python` from
   `pyproject.toml` — and emits `mcp/knowledge/product/`: 8 module concepts plus
   2 procedure references. Every field is copied or mechanically derived. The
   output is committed so `mcp/` stays buildable and copyable on its own;
   `--check` re-projects in memory and fails on drift.

2. **The build hook ships it.** `("product", "product")` joins `MAPPING` in
   `_build_hooks.py`, so the product plane lands in the wheel alongside the
   methodology.

3. **`runtime_modules()` no longer requires a repository.** The inventory and
   purposes come from the packaged concepts. A registered repo now *narrows* the
   list to the modules that checkout actually has, which is the correct meaning
   of that check: a target repo may legitimately be an older or newer Amsha.

4. **Product tools degrade gracefully instead of breaking.**
   `explain_module` falls back to its packaged concept; `get_install_instructions`
   reads structured facts from the packaged concept's frontmatter; both install
   and quickstart fall back to the packaged section when no repo README is
   available. `source_files_for` stays repository-only by design — a file list
   describes a checkout.

5. **Product knowledge is searchable.** `search_amsha_docs` includes the
   product group, namespaced `product/…` so its `index.md` cannot mask the
   knowledge bundle's.

## Impact

- **Standalone operation is materially improved**, which is the change's whole
  point. All four tools answer with no repository registered.
- **Wheel contents grow:** 34 → 44 packaged documents (10 product; the product
  `index.md` is an index and is not shipped).
- **Module purposes improve.** They now come from the Amsha knowledge concepts
  rather than the coarser `_MODULE_PURPOSE` table. `_MODULE_PURPOSE` is retained
  only as a last-resort fallback for a stripped install.
- **The Python constraint is now sourced, not asserted.** `>=3.12,<3.14` was
  hardcoded in `install.py` and appears nowhere in the README. It is now read
  from `requires-python` in `pyproject.toml`.
- **Drift is detectable, not silent.** Changing an Amsha module concept without
  re-running the projection is a `--check` failure.
- **No runtime cost.** The product plane is 11 small files, read on demand.

## Out of Scope

- Deleting `_MODULE_PURPOSE` or `RUNTIME_MODULES`. They remain the fallback and
  the declared inventory.
- `source_files_for`, which is inherently repository-specific.
- The Amsha root `knowledge/` bundle, which is unchanged; this projects *from* it.
