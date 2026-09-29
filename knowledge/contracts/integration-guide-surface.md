---
type: Reference
title: "Reference: integration guide surface"
description: The client-facing integration guide for installing and wiring Amsha into a project, kept as repo-side reference material rather than a runtime module concept.
tags: [amsha, reference, integration, onboarding]
generated: { by: "opencode/gpt-5.4", at: 2026-09-29T00:00:00Z }
stale_after: 2027-03-29T00:00:00Z
sources:
  - id: integration-guide
    resource: ../../docs/integration-guide/USER_GUIDE.md
    title: Integration guide user documentation
    author: team:amsha
  - id: root-user-guide
    resource: ../../USER_GUIDE.md
    title: Root user guide
    author: team:amsha
---

# Reference: integration guide surface

This concept records the **project-integration reference surface** under
`docs/integration-guide/`. It is not a runtime module and therefore does not
belong in `knowledge/features/`.

## What it covers

The integration guide explains how a client project adopts Amsha in practice:
installation expectations, configuration files, project wiring, and the basic
usage path from dependency installation to a working application.

That material is reference documentation for users and integrators. It is
stable enough to need OKF coverage, but it does not describe behaviour that a
runtime module implements directly.

## Why it is recorded here

Without a knowledge concept, the guide is easy to miss because it sits outside
both the source tree and the feature-doc directories. Recording it here keeps
it visible in the OKF bundle and makes its role explicit:

- **reference material**, not a runtime feature
- **repo-side guidance**, not packaged MCP methodology
- **implementation support**, not an OpenSpec capability of its own

## Relationship to specs

The guide is covered by the documentation-surface spec rather than a dedicated
behaviour spec. That is deliberate: the guide explains usage and onboarding,
while the underlying behaviours are already specified by the module specs such
as [crew-forge](../features/crew-forge.md) and
[configuration](../features/configuration.md).

## Related

- [Crew Forge](../features/crew-forge.md)
- [Configuration](../features/configuration.md)
