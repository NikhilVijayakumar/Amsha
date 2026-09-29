---
type: Decision
title: "Two knowledge planes, one invariant"
description: Why the MCP server keeps packaged and repository documentation on separate planes, and what depends on that boundary holding.
tags: [amsha, decision, mcp, docs-loader, distribution]
generated: { by: "opencode/big-pickle", at: 2026-09-29T00:00:00Z }
stale_after: 2027-03-29T00:00:00Z
sources:
  - id: docs-loader
    resource: ../../mcp/src/amsha_mcp/docs_loader.py
    title: MCP documentation loader
    author: team:amsha
  - id: mcp-pyproject
    resource: ../../mcp/pyproject.toml
    title: amsha-mcp package configuration
    author: team:amsha
---

# Decision: two knowledge planes, one invariant

**Status:** in effect. Enforced in
[`docs_loader.py`](../../mcp/src/amsha_mcp/docs_loader.py).

## Context

The `amsha-mcp` server must answer methodology questions **without the Amsha
source repository present**, because it is published as a standalone wheel. It
also benefits from repository content when a repository *is* available.

These two requirements pull in opposite directions. Serving repository
documentation is convenient; depending on it would break the installed-wheel
case.

## Decision

| Plane | Location | Availability |
|---|---|---|
| **Product** | `_DOCS` = `PACKAGE_ROOT / "docs"` | Always. `package-data` in the wheel. |
| **Repo** | `_REPO_ROOT` | Optional. Empty when unregistered. |

**The invariant: product knowledge never depends on repo knowledge.**

The mechanism is a guard on every repository-plane accessor —
`if not root: return {}` (or `[]`, or `""`). `_DOCS` is read unguarded.

The second mechanism is resolution. `_REPO_ROOT` starts as `None`, and
`repo_root()` self-initialises on first access, so a caller that imports a
tool directly — a test, a script — gets the same answer as one that went
through `server.py`.

## Why the accessor matters

That second mechanism was documented twice and implemented zero times. All six
repository-plane accessors read the `_REPO_ROOT` global directly:

```python
if not _REPO_ROOT:      # wrong: bypasses lazy resolution
    return {}
```

Live MCP sessions worked only because `server.py` imports first and resolves
eagerly. Every other caller got `{}` — indistinguishable from "no repository"
and never reported as an error. The fix routes all six through `repo_root()`.

The deeper lesson: a guard that checks a *global* silently inherits whatever
state the process happened to be in. A guard that calls a *function* inherits
the function's contract. Recorded because the same pattern will recur wherever
a module-global is used as a cache.

## Boundary rules

- Do not add frontmatter to the packaged docs. `get_preview` does not strip
  it, so it would leak verbatim into what an agent reads.
- Do not read `mcp/docs/`. It holds only `PACKAGING.md` and
  `mcp-validations/`; the loader never consults it.
- Do not resolve a packaged path by joining onto a repository root. That is
  the defect the `fix-mcp-documentation-discovery` change corrects.
- Do not add `knowledge/` to the *packaged* plane. The bundle is repository
  knowledge by definition; it belongs on the repo plane, and the standalone
  wheel must be unaffected by its absence.

## Related

- [Two OpenSpec roots](./two-openspec-roots.md)
- [Methodology: prerequisite](../methodology/prerequisite.md)
- [Methodology: implementation](../methodology/implementation.md)
