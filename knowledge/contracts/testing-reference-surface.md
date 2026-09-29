---
type: Reference
title: "Reference: testing reference surface"
description: The repo-side testing references, templates, and execution guidance under docs/reference/testing and docs/test-execution.
tags: [amsha, reference, testing, reports]
generated: { by: "opencode/gpt-5.4", at: 2026-09-29T00:00:00Z }
stale_after: 2027-03-29T00:00:00Z
sources:
  - id: reference-testing
    resource: ../../docs/reference/testing
    title: Testing reference documents
    author: team:amsha
  - id: test-execution
    resource: ../../docs/test-execution/README.md
    title: Test execution readme
    author: team:amsha
  - id: constitution-testing
    resource: ../../AGENTS.md
    title: Testing standards in the coding constitution
    author: team:amsha
---

# Reference: testing reference surface

This concept records the testing-oriented documentation outside the source tree:

- `docs/reference/testing/`
- `docs/test-execution/README.md`

## What it covers

These files provide templates, report examples, and guidance for how testing
results are recorded and communicated. They support the test philosophy in
[AGENTS.md](../../AGENTS.md) but are not themselves behavioural specs of a
runtime module.

## Why it is a reference surface

The testing documents are process aids:

- report templates standardize outputs
- example reports show expected structure
- execution notes explain how test runs are documented

They are durable enough to belong in the OKF bundle, yet too operational to be
feature concepts.

## Relationship to specs

OpenSpec remains responsible for the current behavioural contract of the code.
This testing surface explains how evidence is captured around that behaviour.
The documentation-surface spec therefore covers these files as reference
material, rather than generating a dedicated runtime capability spec from each
template.

## Related

- [Methodology: proposal](../methodology/proposal.md)
- [Documentation coverage by knowledge and specs](../decisions/documentation-coverage.md)
