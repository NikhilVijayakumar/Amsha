# Proposal 10 — Align with CrewAI's Flow-First Production Architecture

| | |
|---|---|
| **Priority** | Phase 6, alongside/after [03](03-flows-adoption.md) |
| **Risk** | Medium — architectural, but framed as alignment not rewrite |
| **Effort** | Medium |
| **Depends on** | [02](02-crewai-version-migration.md), [03](03-flows-adoption.md), [05](05-checkpointing-consolidation.md) |
| **Status** | ✅ Done (2026-09-02) |

## What CrewAI recommends now

Flow as the app entry point, Pydantic-typed minimal state, Crews as focused units of work fed by explicit state→input mapping. Control primitives: Task Guardrails, structured (Pydantic/JSON) outputs, and **LLM Hooks** (message inspection/sanitization — new in 1.x, no 0.x equivalent). `kickoff_async()` for long-running ops; `@persist()` decorator for state recovery/resume with fork support via `restore_from_state_id`. CrewAI Enterprise is offered as a managed infra/auth/monitoring layer on top (not relevant to Amsha, which is a library, not a hosted product).

## Non-negotiable constraint (2026-09-02)

`BaseCrewOrchestrator` — the direct single-crew run path — **is not being removed or demoted**. "Flow-first" in CrewAI's own docs describes CrewAI's opinion for *new* apps; it does not mean Amsha's existing direct-run entry point has to disappear for this alignment work to count as done. The target end state is: a user can run one crew directly (today's path, unchanged) **or** run a Flow that orchestrates several crews ([03](03-flows-adoption.md)), and get memory, checkpointing, and event observability either way, from the same underlying machinery. This proposal is about closing capability gaps (guardrails, structured output, hooks, persist/fork) in both paths, not about picking Flow as the one true entry point and deprecating the other.

## How this maps onto Amsha's existing architecture

Amsha's `BaseCrewOrchestrator` + `RuntimeEngine` + `StateManager` is, structurally, already reaching for the same shape CrewAI's production guidance describes — an orchestration layer, a typed state/status object, sync/async execution modes. The gap is that Amsha built it generically (works with any `CrewManager` Protocol implementation) rather than on top of CrewAI's own now-native primitives, because those primitives didn't exist in 0.x.

Concretely, after [03](03-flows-adoption.md) and [05](05-checkpointing-consolidation.md), both entry points should share the same backing services:

| Capability | Direct crew run (`BaseCrewOrchestrator`) | Flow-driven run (`FlowCrewOrchestrator`, [03](03-flows-adoption.md)) |
|---|---|---|
| Memory | `Crew(memory=...)` via `CrewData.memory` ([04](04-memory-adoption.md), done) | Same `CrewData.memory` path — a crew kicked off inside a Flow method is still built by `CrewBuilderService`, so this is already shared, not duplicated |
| Checkpointing | `StateManager.attach_checkpoint`/`resume_crew` ([05](05-checkpointing-consolidation.md), done) | `Flow(checkpoint=...)` should record into the same `StateManager`, not a separate Flow-only state store |
| Event listeners | Global `CrewAIEventsBus` ([09](09-event-observability-upgrade.md)) | Same bus — Flow-method-execution events are just another event category on the same listener |

If an implementation detail in this proposal or [03](03-flows-adoption.md) would give Flow-driven runs a capability the direct-run path doesn't have (or vice versa) without a documented reason, that's a signal the two paths have drifted apart instead of sharing infrastructure — flag it rather than shipping it.

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

## Execution log

Alignment against the table's rows, closed across proposals 03/05/08 and this pass:

| CrewAI production primitive | Closed by |
|---|---|
| Flow as entry point | [03](03-flows-adoption.md) — `FlowCrewOrchestrator`/`run_pipeline()` for multi-crew job configs |
| `@persist()` / fork via `restore_from_state_id` | [05](05-checkpointing-consolidation.md) — native `checkpoint=` + `resume_crew()`; `@persist` itself remains unused (flow-level persistence is a follow-up) |
| Task Guardrails | [08](08-agent-task-capability-expansion.md) — `guardrail` field |
| Structured outputs (`output_pydantic`/`output_json`) | [08](08-agent-task-capability-expansion.md) |
| LLM Hooks | **Deferred** — the only net-new surface left. `llm_factory/` centralization point for hook registration is noted in the proposal body; nothing in the current migration requires it, so it stays out until e.g. a message-redaction or outbound-prompt-logging ask appears. |
| `kickoff_async()` | Flow's `kickoff()` already runs CrewAI's async path internally; Amsha BACKGROUND mode submits the whole flow to `RuntimeEngine` and returns an `ExecutionHandle` (see [03](03-flows-adoption.md) item 4) |

Flow state→input mapping: `PipelineState.inputs` is fed to every crew step's `run_crew(inputs=...)` — the explicit state→input bridge the proposal describes.
