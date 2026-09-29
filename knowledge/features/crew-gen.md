---
type: Module
title: Crew Gen (retired)
description: The retired crew-generation capability — no source remains in src/, kept to preserve intent and history.
status: deprecated
tags: [amsha, retired, crewai, generation]
generated: { by: "opencode/big-pickle", at: 2026-09-29T00:00:00Z }
stale_after: 2027-03-29T00:00:00Z
sources:
  - id: crew-gen-docs
    resource: ../../docs/feature/crew_gen
    title: Crew Gen feature documentation
    author: team:amsha
---

# Crew Gen (retired)

`crew_gen` generated crew definitions automatically. It is no longer part of
Amsha.

## Evidence of removal

- No `crew_gen` directory exists under `src/nikhil/amsha/`.
- A stale copy survives at `build/lib/amsha/crew_gen/`. `build/` is a build
  artefact directory and is not a source of truth; nothing imports from it.
- Documentation remains at `docs/feature/crew_gen/`.
- The MCP server does not list it among its runtime modules.

## Why it is recorded rather than deleted

Automatic crew generation overlapped with the design-first methodology that
now precedes crew authoring. Amsha's current direction is that a crew is
designed through the prerequisite stages (see
[Methodology: prerequisite](../methodology/prerequisite.md)) and only then
written as YAML. Generation without that design step is what this capability
used to do, and the gap is worth keeping visible so it is not reintroduced
accidentally.

`status: deprecated` is the OKF lifecycle value for "kept for links and
history; no longer current" — distinct from deleting the concept, which
would break the documentation link from
[`docs/feature/crew_gen/`](../../docs/feature/crew_gen/).

## Successor

[Methodology: implementation](../methodology/implementation.md) covers how a
designed crew becomes implemented YAML.

## Related

- [Methodology: proposal](../methodology/proposal.md) — the proposal history
  that recorded this retirement
