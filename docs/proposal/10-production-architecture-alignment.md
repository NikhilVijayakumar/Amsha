# Proposal 10 — Align with CrewAI's Flow-First Production Architecture

| | |
|---|---|
| **Priority** | Phase 6, alongside/after [03](03-flows-adoption.md) |
| **Risk** | Medium — architectural, but framed as alignment not rewrite |
| **Effort** | Medium |
| **Depends on** | [02](02-crewai-version-migration.md), [03](03-flows-adoption.md), [05](05-checkpointing-consolidation.md) |

## What CrewAI recommends now

Flow as the app entry point, Pydantic-typed minimal state, Crews as focused units of work fed by explicit state→input mapping. Control primitives: Task Guardrails, structured (Pydantic/JSON) outputs, and **LLM Hooks** (message inspection/sanitization — new in 1.x, no 0.x equivalent). `kickoff_async()` for long-running ops; `@persist()` decorator for state recovery/resume with fork support via `restore_from_state_id`. CrewAI Enterprise is offered as a managed infra/auth/monitoring layer on top (not relevant to Amsha, which is a library, not a hosted product).

## How this maps onto Amsha's existing architecture

Amsha's `BaseCrewOrchestrator` + `RuntimeEngine` + `StateManager` is, structurally, already reaching for the same shape CrewAI's production guidance describes — an orchestration layer, a typed state/status object, sync/async execution modes. The gap is that Amsha built it generically (works with any `CrewManager` Protocol implementation) rather than on top of CrewAI's own now-native primitives, because those primitives didn't exist in 0.x.

Specific alignment points:

| CrewAI production primitive | Amsha equivalent today | Alignment action |
|---|---|---|
| Flow as entry point | `BaseCrewOrchestrator.run_crew()` single-crew entry | See [03](03-flows-adoption.md) — add Flow path for multi-step job configs |
| `@persist()` / fork via `restore_from_state_id` | `StateManager`/`ExecutionState` (status only, no resume) | See [05](05-checkpointing-consolidation.md) |
| Task Guardrails | None | See [08](08-agent-task-capability-expansion.md) — add `guardrail` field |
| Structured outputs (`output_pydantic`/`output_json`) | `add_task(..., output_json: Any = None)` exists but untyped, just assigned raw | See [08](08-agent-task-capability-expansion.md) — accept an actual Pydantic model type, not `Any` |
| LLM Hooks (message inspection/sanitization) | None — no interception point exists between Amsha and the LLM call | New surface, see below |
| `kickoff_async()` | `RuntimeEngine.submit(mode=ExecutionMode.BACKGROUND)` via thread pool | Functionally equivalent already; consider native `akickoff()` once available (see [03](03-flows-adoption.md)) for true async instead of thread-pool-wrapped sync |

## LLM Hooks — net-new proposal

CrewAI 1.x's LLM Hooks let you inspect/sanitize messages before they reach the LLM. Amsha's `llm_factory` module currently constructs and hands off an `LLM` instance (`CrewAIProviderAdapter`) with no interception point. Given Amsha already centralizes LLM construction (`llm_factory/service/`, `llm_factory/dependency/llm_container.py`), this is a natural place to add opt-in hook registration — e.g. for injecting Amsha-standard system context, logging outbound prompts through `MetricsLogger.log_llm_config` (already exists, currently only logs config, not actual message content), or redacting sensitive fields before they leave the process. Not required by anything else in this proposal set, but worth scoping once the rest of the migration is stable.

## What NOT to do

- Don't reframe this as "rewrite Amsha's orchestrator to look like CrewAI's reference architecture" — Amsha's value is the config-as-code/YAML/Mongo layer *around* CrewAI, not a copy of CrewAI's own app-scaffolding opinions. This proposal is about closing specific capability gaps (guardrails, structured output, hooks, persist/fork), not architectural mimicry for its own sake.
