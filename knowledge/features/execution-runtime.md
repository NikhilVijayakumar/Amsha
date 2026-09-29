---
type: Module
title: Execution Runtime
description: Submits work to a bounded thread pool and returns a cancellable, awaitable handle.
tags: [amsha, capability, concurrency, protocol]
generated: { by: "opencode/big-pickle", at: 2026-09-29T00:00:00Z }
stale_after: 2027-03-29T00:00:00Z
sources:
  - id: execution-runtime-src
    resource: ../../src/nikhil/amsha/execution_runtime
    title: Execution Runtime source tree
    author: team:amsha
---

# Execution Runtime

The concurrency boundary. It runs callables on a `concurrent.futures` thread
pool and hands back a handle the caller can poll, await, or cancel.

## Handle protocol

`ExecutionHandle` is a `Protocol` in `domain/execution_handle.py` with four
members:

| Member | Signature | Meaning |
|---|---|---|
| `execution_id` | `() -> str` | Stable identifier for this run |
| `status` | `() -> ExecutionStatus` | Current lifecycle status |
| `result` | `(timeout: Optional[float]) -> Any` | Blocks for the result |
| `cancel` | `() -> bool` | Requests cancellation |

`ExecutionHandle` deliberately mirrors [Execution
State](./execution-state.md)'s `ExecutionStatus` but declares it as a
`Protocol`, so a client can substitute a distributed handle backed by a queue
without inheriting from Amsha.

## Modes

`ExecutionMode` (`domain/execution_mode.py`) selects how a submission is
scheduled. `RuntimeEngine.submit(task, *args, mode=ExecutionMode.BACKGROUND,
**kwargs)` defaults to background execution.

## Thread pool

`RuntimeEngine(max_workers=4)` defaults to four workers. The default is
deliberately low: Amsha's concurrency is I/O-bound around LLM calls, and a
large pool mostly increases memory pressure and rate-limit exposure rather
than throughput. Raise it deliberately.

`LocalExecutionHandle` wraps a `concurrent.futures.Future` (or a plain value,
for already-complete work) and translates it into the handle protocol.
`RuntimeEngine.shutdown()` releases the pool and must be called.

## Relationship to async

Per [`AGENTS.md`](../../AGENTS.md) §6, async is for I/O-bound work only. This
module is the thread-pool counterpart: crews are mostly sequential and
tool-driven, so blocking threads fit better than an event loop. The handle
protocol is shaped so a future asyncio implementation can satisfy it without
changing callers.

## Related

- [Execution State](./execution-state.md) — status values and persistence
