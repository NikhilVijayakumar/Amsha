---
type: Playbook
title: "Methodology: proposals and OpenSpec"
description: How change intent is recorded — the historical numbered proposals, and the OpenSpec roots that supersede them for new work.
tags: [amsha, methodology, proposals, openspec]
generated: { by: "opencode/big-pickle", at: 2026-09-29T00:00:00Z }
stale_after: 2026-12-29T00:00:00Z
sources:
  - id: proposal-archive
    resource: ../../docs/proposal/archive
    title: Archived numbered proposals (00-14)
    author: team:amsha
  - id: openspec-root
    resource: ../../openspec
    title: OpenSpec change root
    author: team:amsha
  - id: openspec-mcp
    resource: ../../mcp/openspec
    title: OpenSpec change root (amsha-mcp)
    author: team:amsha
---

# Methodology: proposals and OpenSpec

**This concept describes the process. It does not contain the proposals.** The
numbered history is at `docs/proposal/archive/` (00–14); new work is recorded
as an OpenSpec change.

## Two eras of change record

**Numbered proposals (00–14, archived).** The historical record. Each
answers: what is the problem, what changes, what is the impact. They are
read, not executed. `04-crewai-version-migration.md` in particular records
the migration that makes [AGENTS.md](../../AGENTS.md) §13 stale.

**OpenSpec changes (two roots).** The current process for anything that
changes behaviour.

| Root | Scope | Resolution |
|---|---|---|
| `openspec/` | The Amsha library | Nearest `openspec/` up from the working directory |
| `mcp/openspec/` | The `amsha-mcp` server | Resolved from within `mcp/` |

Two roots rather than one because `amsha-mcp` is a **standalone
distribution**. It is published as its own wheel with its own version, and
its changes are reviewed separately from library changes. Nesting
`mcp/openspec/` inside the root `openspec/` directory would collide with the
root's `changes/` and `specs/` structure.

Each change carries a proposal, and where behaviour changes, a spec delta
expressed as `### Requirement:` with `#### Scenario:` blocks. `openspec
validate --strict` checks the delta, so a change with an unvalidated
requirement does not pass. A change that alters no behaviour sets
`skip_specs: true` rather than inventing a requirement to satisfy the tool.

## How this bundle relates to OpenSpec

The two have deliberately different jobs and neither restates the other:

| | Bundle (`knowledge/`) | OpenSpec (`openspec/`) |
|---|---|---|
| Answers | What a module **is** — role, boundaries, decisions | What behaviour **must be** true |
| Form | Prose, `type:` frontmatter | Requirements and scenarios, machine-validated |
| Lifetime | Durable | `changes/` are transient; `specs/` is current state |
| Read by | Humans and agents building context | Tools enforcing correctness |

A module concept links to its spec; a spec links back. Neither copies the
other's content, because a copy is a third thing to keep in sync.

## The lifecycle

```
knowledge/          what we know        (durable)
      │ context
      ▼
openspec/changes/   what we intend      (transient)
      │ implements
      ▼
Code                what exists
      │ verified by
      ▼
Tests + MCP verifiers  what we can demonstrate
      │ updates
      └──────────────► knowledge/
```

The loop closes: verification results update the knowledge bundle rather than
being recorded in a separate `evidence/` tree.

## Evidence

There is no top-level `evidence/` directory, deliberately. Evidence for a
knowledge claim is the test suite and the deterministic MCP verifiers, and
`verified` in a concept's frontmatter records who confirmed what and when.
Under OKF v0.2 a concept with no `verified` entry reads as *unverified*, and
one verified by a `human:` actor reads as *human-reviewed* — so the gap
between "written by an agent" and "confirmed by a person" is legible from
frontmatter alone.

## Related

- [Prerequisite](./prerequisite.md) — design precedes implementation
- [Implementation](./implementation.md) — the authoring rules
- [Decisions](../decisions/) — durable decisions with their rationale
