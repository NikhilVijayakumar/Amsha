---
type: Reference
title: "Contract: jobs/load/AtomicDbBuilderService"
description: The service contract a client implements or injects to assemble crews from database-backed atomic definitions.
tags: [amsha, contract, interface, crew-forge]
generated: { by: "opencode/big-pickle", at: 2026-09-29T00:00:00Z }
stale_after: 2027-03-29T00:00:00Z
sources:
  - id: constitution
    resource: ../../AGENTS.md
    title: Amsha coding constitution (sections 2-4)
    author: team:amsha
  - id: crew-forge-src
    resource: ../../src/nikhil/amsha/crew_forge
    title: Crew Forge source tree
    author: team:amsha
---

# Contract: `jobs/load/AtomicDbBuilderService`

Documented from the constitution and the module layout, **not** extracted
from an existing interface file — `crew_forge/service/` and `crew_forge/repo/`
contain no `AtomicDbBuilderService` class today. Treat this as the contract a
client is expected to satisfy, not as a description of shipped code.

## Shape

A service that assembles a runnable crew from atomic, separately-stored
agent and task definitions.

```python
class AtomicDbBuilderService:
    def __init__(self, agent_repo: IAgentRepository, task_repo: ITaskRepository):
        self.agent_repo = agent_repo
        self.task_repo = task_repo
```

## Rules

**Dependencies are injected, never constructed.** The service holds
references it was given. It does not instantiate `MongoAgentRepository()` or
any other adapter. Wiring happens in `dependency/containers.py` using
`dependency-injector`.

**Repository interfaces are `ABC`.** `IAgentRepository` and `ITaskRepository`
use `ABC` with `@abstractmethod`, giving nominal typing and runtime
enforcement. This is the distinction in [`AGENTS.md`](../../AGENTS.md) §2:
`ABC` for internal repository contracts, `Protocol` for client-facing
boundaries.

**Errors are component-specific.** Raise from
`crew_forge/exceptions/`, never a bare `Exception` or `ValueError` for domain
logic. The exception hierarchy roots at `AmshaException`.

**Building and running are separate concerns.** This service *builds*. A
separate orchestrator *runs*, per SRP in
[`AGENTS.md`](../../AGENTS.md) §4.

## The gap

`crew_forge/repo/` and `crew_forge/dependency/` are present but empty. The
repository adapters and container wiring this contract implies are not in the
source tree, so a client integrating Amsha today supplies them. Adding a new
backend (Postgres, DynamoDB) means a new class implementing the interface, not
an `if type == 'SQL'` branch — OCP in
[`AGENTS.md`](../../AGENTS.md) §4.

## Related

- [Crew Forge](../features/crew-forge.md)
- [AGENTS.md](../../AGENTS.md)
