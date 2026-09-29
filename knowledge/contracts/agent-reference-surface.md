---
type: Reference
title: "Reference: agent reference surface"
description: The repo-side agent reference corpus under docs/reference/agent, including skills, rules, and usage notes for human and agent operators.
tags: [amsha, reference, agent, skills, rules]
generated: { by: "opencode/gpt-5.4", at: 2026-09-29T00:00:00Z }
stale_after: 2027-03-29T00:00:00Z
sources:
  - id: agent-reference
    resource: ../../docs/reference/agent
    title: Agent reference documentation
    author: team:amsha
  - id: agents-constitution
    resource: ../../AGENTS.md
    title: Repository coding constitution
    author: team:amsha
---

# Reference: agent reference surface

This concept records the **operator reference surface** under
`docs/reference/agent/`.

## What lives there

The directory contains three kinds of reference material:

- the top-level operator guide in `README.md`
- reusable rule documents under `rules/`
- named skill references under `skills/`

These files explain how a human or coding agent should work in this repository.
They are not runtime library modules and they are not current-state behaviour
specs of the public Python package.

## Why it is reference material

The agent reference corpus is advisory and operational:

- it explains conventions
- it documents reusable skill profiles
- it mirrors or expands repository working rules

That makes it durable knowledge, but not a `knowledge/features/` concept and
not a one-file-per-skill OpenSpec requirement set.

## Why one concept instead of dozens

The individual skill files are numerous and intentionally human-facing. Their
behavioural force comes from the repository rules they summarize, not from each
skill being a separate product capability. This concept therefore records the
surface as one reference plane, while the documentation-surface spec requires
that the plane remain represented in OKF.

## Relationship to module and methodology docs

When a skill or rule describes actual library behaviour, the authoritative
behaviour lives elsewhere:

- module behaviour → the corresponding file in `openspec/specs/`
- durable rationale → the matching concept in `knowledge/`
- operator workflow guidance → this reference surface

## Related

- [Methodology: implementation](../methodology/implementation.md)
- [Documentation coverage by knowledge and specs](../decisions/documentation-coverage.md)
