# Proposal 09 — Replace Manual Monitoring with CrewAI's Event Bus

| | |
|---|---|
| **Priority** | Phase 6 |
| **Risk** | Low-Medium — additive, but should coexist with existing metrics during transition |
| **Effort** | Medium |
| **Depends on** | [02](02-crewai-version-migration.md), more valuable after [03](03-flows-adoption.md)/[04](04-memory-adoption.md) land |

## What CrewAI's event system offers

A singleton event bus (`CrewAIEventsBus` + `BaseEvent` + `BaseEventListener`) with **~100+ events**: crew lifecycle, agent execution, tasks, tool usage, LLM calls (including streaming chunks), memory operations, flow/method execution, human feedback, knowledge retrieval, MCP connection events, A2A delegation events, agent reasoning, guardrail validation, planning/replanning. Pattern: subclass `BaseEventListener`, implement `setup_listeners()`, register handlers with `@crewai_event_bus.on(EventClass)`; a `scoped_handlers()` context manager exists for temporary listeners.

## Current state in Amsha

`CrewPerformanceMonitor` takes a manual, coarse-grained, before/after approach:

- `start_monitoring()`/`stop_monitoring()` snapshot `psutil` CPU/memory and `pynvml` GPU stats at two points in time — no visibility into *what happened during* execution, just delta.
- `log_usage(result)` parses `result.token_usage` **after the crew finishes** — a single aggregate number for the whole crew run, not per-agent, per-task, or per-LLM-call.
- Zero visibility into tool calls, individual task transitions, guardrail retries, or (once adopted) memory operations. If a task retries 5 times against a guardrail, Amsha never sees it — only the final success/failure and aggregate tokens.

`base_crew_orchestrator.py`'s streaming handler (`if hasattr(result, '__iter__')...`) is itself a workaround for not having access to real per-chunk events — it manually reconstructs a `CrewOutput` from consumed stream chunks because there's no better hook available in the current approach.

## Proposal

1. Build an `AmshaEventListener(BaseEventListener)` in `crew_monitor/` that subscribes to the events Amsha's current metrics already approximate, but properly: `TaskCompletedEvent`/`TaskFailedEvent` for per-task timing (replacing the single whole-crew duration `CrewPerformanceMonitor` currently produces), `LLMCallCompletedEvent` (or equivalent) for per-call token usage instead of end-of-crew aggregate parsing, `ToolUsageEvent` for tool-call visibility Amsha currently has none of.
2. **Keep `CrewPerformanceMonitor`'s `psutil`/`pynvml` system-resource sampling** — the event bus doesn't emit CPU/GPU metrics, that's process-level, not CrewAI-level, so this part of Amsha's existing code has no native replacement and should stay.
3. Feed event data into the same `MetricsLogger`/`get_logger()` pipeline Amsha already uses, so this is additive observability, not a new logging destination.
4. Once [03](03-flows-adoption.md) lands, subscribe to flow-method-execution events too — this is where the event bus earns its keep the most, since Amsha's `RuntimeEngine` currently has zero visibility into what a multi-step flow is doing mid-run beyond the coarse `ExecutionStatus` enum.
5. Remember the module-load-time gotcha CrewAI's docs call out: `BaseEventListener` subclasses must be instantiated at import time or the listener gets garbage-collected before it can fire — this is an easy footgun to hand to Amsha's consumers if this becomes a public API; instantiate it internally in `crew_monitor/__init__.py` rather than requiring each caller to remember to do so.

## What NOT to do

- Don't rip out `CrewPerformanceMonitor` — its OS-level resource sampling has no event-bus equivalent, it should be composed with the new listener, not replaced by it.
- Don't try to migrate this before the version bump — the event class names/shapes are 1.x-specific and may not exist (or may differ) on 0.201.1.
