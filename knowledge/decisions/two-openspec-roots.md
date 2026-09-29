---
type: Decision
title: "Two OpenSpec roots, not one"
description: Why the Amsha library and the amsha-mcp server keep separate OpenSpec roots and review changes separately.
tags: [amsha, decision, openspec, mcp, distribution]
generated: { by: "opencode/big-pickle", at: 2026-09-29T00:00:00Z }
stale_after: 2027-03-29T00:00:00Z
sources:
  - id: mcp-pyproject
    resource: ../../mcp/pyproject.toml
    title: amsha-mcp package configuration
    author: team:amsha
  - id: proposal-15
    resource: ../../docs/proposal/openspec-okf/proposal.md
    title: Proposal 15 — OpenSpec + OKF adoption
    author: team:amsha
---

# Decision: two OpenSpec roots, not one

**Status:** in effect. Recorded in
[Proposal 15](../../docs/proposal/openspec-okf/proposal.md).

## Context

`amsha-mcp` is not a subpackage of Amsha. It is a **standalone
distribution**: its own `pyproject.toml`, its own version (`0.1.0` against
the library's `2.11.4`), and its own wheel that installs without Amsha
present.

## Decision

| Root | Scope |
|---|---|
| `openspec/` | The Amsha library |
| `mcp/openspec/` | The `amsha-mcp` server |

Each is initialised independently and resolves to the nearest root from the
working directory.

## Rationale

**Version and review are separate.** A change to the MCP server does not
change the library's behaviour, and bumping the library to record it would be
wrong. One shared root would force a single version and a single review
queue over two products with different release cadences.

**`mcp/openspec/` nested inside `openspec/` would collide.** The root's own
structure is `openspec/changes/` and `openspec/specs/`. Placing
`mcp/openspec/changes/` inside the library's `changes/` directory would
interleave two independent change sets in one listing.

**The published wheel must stay self-contained.** The MCP package carries its
own methodology documentation as `package-data`. Its change record belongs
with it, not in a directory outside the distribution.

## Consequences

Two `openspec list` invocations instead of one, and no cross-root dependency
tracking. Accepted: the alternative couples the release cycles of a library
and a server that are versioned independently.

## Evidence

`mcp/openspec/changes/fix-mcp-documentation-discovery/` is the first change in
the MCP root, and it fixes three defects in `docs_loader.py` and
`architecture.py` — including a latent one that left every repository-sourced
tool returning empty outside a server process. Those fixes ship under the
MCP root because they are MCP code, regardless of how they were found.

## Related

- [Methodology: proposal](../methodology/proposal.md)
- [AmshaEventListener knowledge-plane decision](./knowledge-planes.md)
