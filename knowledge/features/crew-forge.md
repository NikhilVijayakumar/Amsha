---
type: Module
title: Crew Forge
description: Turns crew definitions into runnable CrewAI crews and flows, and executes them.
tags: [amsha, capability, crewai, orchestration]
generated: { by: "opencode/big-pickle", at: 2026-09-29T00:00:00Z }
stale_after: 2027-03-29T00:00:00Z
sources:
  - id: crew-forge-src
    resource: ../../src/nikhil/amsha/crew_forge
    title: Crew Forge source tree
    author: team:amsha
---

# Crew Forge

The largest Amsha module (42 non-empty Python files) and the entry point for
most client applications. It reads crew definitions, constructs CrewAI `Crew`
and `Flow` objects from them, and runs them.

## Layer structure

| Layer | Non-empty files | Role |
|---|---|---|
| `domain` | 4 | Pydantic models and enums for crew definitions |
| `orchestrator` | 5 | Builds and drives crews and flows |
| `service` | 7 | Builder and orchestrator services |
| `protocols` | 4 | `Protocol` contracts for client-supplied behaviour |
| `exceptions` | 7 | Component-specific exception hierarchy |
| `knowledge` | 2 | Knowledge-source loading |
| `seeding` | 1 | Parser for seeding definitions |
| `repo` | 0 | **Empty** — repository adapters are not present in this tree |
| `dependency` | 0 | **Empty** |

The empty `repo/` and `dependency/` directories are worth knowing about: the
constitution in [`AGENTS.md`](../../AGENTS.md) describes MongoDB adapters and
a `dependency-injector` container for this module, and
[`jobs/load/AtomicDbBuilderService.md`](../contracts/jobs-load-atomic-db-builder-service.md)
documents the contract those adapters are expected to satisfy, but no concrete
implementation currently ships in `src/`. Clients supply their own via
dependency injection.

## Primary orchestration surface

`AmshaCrewFileApplication` (exported from the package `__init__`) is the base
class for file-backed orchestration. It loads job, app, and LLM configuration
from the filesystem at runtime, initialises the LLM through the LLM factory,
manages input preparation, and exposes `clean_json()` for output
post-processing.

## Contracts

- [`jobs/load/AtomicDbBuilderService`](../contracts/jobs-load-atomic-db-builder-service.md)

## Related

- [LLM Factory](./llm-factory.md) — supplies the model instances this module
  orchestrates
- [Configuration](./configuration.md) — the `AmshaJobConfig` schema consumed here
- [Output Process](./output-process.md) — consumes crew output
