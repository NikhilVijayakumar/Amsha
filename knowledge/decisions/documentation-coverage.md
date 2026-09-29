---
type: Decision
title: "Documentation coverage by knowledge and specs"
description: How the repository's non-research documentation under docs/ maps into OKF concepts and OpenSpec current-state specs, and which subtree is intentionally excluded.
tags: [amsha, decision, documentation, openspec, okf]
generated: { by: "opencode/gpt-5.4", at: 2026-09-29T00:00:00Z }
stale_after: 2027-03-29T00:00:00Z
sources:
  - id: docs-root
    resource: ../../docs
    title: Repository documentation tree
    author: team:amsha
  - id: knowledge-root
    resource: ../../knowledge
    title: OKF knowledge bundle
    author: team:amsha
  - id: openspec-root
    resource: ../../openspec/specs
    title: OpenSpec current-state specs
    author: team:amsha
---

# Decision: documentation coverage by knowledge and specs

## Decision

The former product-documentation trees under `docs/feature/`, `docs/proposal/`,
and `docs/archived/` have been migrated into `knowledge/` and
`openspec/specs/` and no longer need to remain in `docs/`.

The remaining documentation under `docs/` is classified as follows:

| Docs subtree | Coverage mode | Current representation |
|---|---|---|
| `docs/integration-guide/` | reference surface | `knowledge/contracts/integration-guide-surface.md` + documentation-surface spec |
| `docs/reference/` | reference surface | `knowledge/contracts/agent-reference-surface.md`, `knowledge/contracts/testing-reference-surface.md` + documentation-surface spec |
| `docs/test-execution/` | reference surface | `knowledge/contracts/testing-reference-surface.md` + documentation-surface spec |
| `docs/research/` | excluded | intentionally outside OKF/OpenSpec migration |

Migrated legacy trees:

| Former docs subtree | Migration target |
|---|---|
| `docs/feature/` | `knowledge/features/` + `openspec/specs/` |
| `docs/proposal/` | `knowledge/methodology/proposal.md` + OpenSpec roots |
| `docs/archived/` | durable knowledge and explicit retirement/history decisions where relevant |

## Why this classification exists

The repository originally mixed several kinds of documentation in one `docs/`
tree:

- current feature descriptions
- onboarding and integration guidance
- operator rules and skill references
- templates and test-report material
- proposal history
- archived historical notes
- research material for paper work

The migration keeps runtime capability knowledge and behaviour in
`knowledge/` and `openspec/specs/`, while leaving only the still-useful
reference and research surfaces in `docs/`.

## The explicit exclusion

`docs/research/` is excluded on purpose. It is paper-support material rather
than product or repository-governance documentation. Leaving it outside the OKF
bundle prevents research drafts and paper notes from being mistaken for current
product knowledge.

## Consequences

- Live runtime capability documentation belongs in `knowledge/features/` and
  `openspec/specs/`, not in a separate `docs/feature/` tree.
- Retired capability documentation belongs in deprecated concepts and current-
  state retirement specs rather than in a legacy feature-doc tree.
- Reference and testing documents must remain visible through OKF, but they do
  not require one behaviour spec per file.
- Proposal and archived material no longer require separate `docs/` trees once
  their durable content has been migrated or intentionally retired.

## Related

- [Methodology: proposal](../methodology/proposal.md)
- [Reference: agent reference surface](../contracts/agent-reference-surface.md)
- [Reference: testing reference surface](../contracts/testing-reference-surface.md)
- [Reference: integration guide surface](../contracts/integration-guide-surface.md)
