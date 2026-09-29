---
type: Module
title: Execution State
description: Models the lifecycle of a single run and persists it through an injected state repository.
tags: [amsha, capability, state, protocol]
generated: { by: "opencode/big-pickle", at: 2026-09-29T00:00:00Z }
stale_after: 2027-03-29T00:00:00Z
sources:
  - id: execution-state-src
    resource: ../../src/nikhil/amsha/execution_state
    title: Execution State source tree
    author: team:amsha
---

# Execution State

Tracks what one execution is doing. It holds no orchestration logic — it is a
state model plus a manager that persists it.

## Statuses

`ExecutionStatus` (in `domain/enums.py`) is a `str` enum with six members:

| Member | Value |
|---|---|
| `PENDING` | `pending` |
| `RUNNING` | `running` |
| `COMPLETED` | `completed` |
| `FAILED` | `failed` |
| `CANCELLED` | `cancelled` |
| `PAUSED` | `paused` |

Subclassing `str` means the value serialises directly to JSON or YAML without
a custom encoder, which matters because `ExecutionState` is persisted.

## Models

`StateSnapshot` is an immutable point-in-time record. `ExecutionState` is the
mutable aggregate, with `update_status(status, metadata)`, `set_output(key,
value)`, and `add_metadata(key, value)`.

## Persistence via Protocol

`StateManager` takes an `Optional[IStateRepository]` in its constructor.
`IStateRepository` is a **`Protocol`**, not an `ABC` — it declares `save` and
`get` structurally. This follows the rule in [`AGENTS.md`](../../AGENTS.md)
§2 that `Protocol` is for client-supplied implementations, and it is why a
client can plug in MongoDB, Postgres, or anything else without inheriting
from Amsha.

`InMemoryStateRepository` is the shipped default. It is a fallback for tests
and single-process runs, not the production path.

Defaulting the argument to `None` means `StateManager()` works out of the
box. The trade-off is that a forgotten injection silently gets the in-memory
repository, so state is lost on restart without any error — worth knowing when
debugging a production run.

## Related

- [Execution Runtime](./execution-runtime.md) — drives the state this module records
- [Crew Monitor](./crew-monitor.md) — observes it
