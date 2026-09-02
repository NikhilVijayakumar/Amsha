# Proposal 03 — Adopt CrewAI Flows

| | |
|---|---|
| **Priority** | Phase 3 (after capability expansion, memory, checkpointing) |
| **Risk** | Medium — architectural addition, not a rewrite |
| **Effort** | Medium-Large |
| **Depends on** | [02](02-crewai-version-migration.md), pairs with [10](10-production-architecture-alignment.md) |
| **Status** | ✅ Done (2026-09-02) |

## What CrewAI Flows are

`Flow[StateModel]` classes with `@start()`/`@listen()`/`@router()` decorated methods, driving execution as an event graph rather than a fixed pipeline. State is a Pydantic model (recommended) or dict. Crews run *inside* flow methods (`PoemCrew().crew().kickoff(inputs=...)`) and write results back into flow state. CrewAI's current docs explicitly reposition Flows as the **default top-level orchestrator**, with Crews as subordinate units of work — inverted from the older "Crew is the top-level thing" mental model Amsha was built around.

## Current state in Amsha

Amsha has no Flow usage at all. Instead it has a bespoke, parallel mechanism:

- `BaseCrewOrchestrator.run_crew()` — builds one crew, submits it to `RuntimeEngine`, tracks status via `StateManager`.
- `RuntimeEngine` — thread-pool-backed sync/async execution, returns an `ExecutionHandle`.
- `FileCrewOrchestrator`/`DbCrewOrchestrator` — presumably drive multi-step pipelines (job_config.yaml mentions "pipeline, including which crews to run, their steps") by calling `run_crew` repeatedly.

This means Amsha has already built, by hand, roughly what a Flow gives natively: multi-step orchestration, state tracking, sync/async modes. The difference is Amsha's version has no branching (`@router`), no structured state validation, no built-in persistence/fork, and isn't visualizable (`crewai flow plot`).

## Where this actually helps Amsha

Amsha's own docs (`docs/feature/crew_forge/functional.md`, FR-CREW-01/02) describe **one Crew per "use case" directory** — i.e., Amsha's current model is fundamentally single-crew-per-run, with `job_config.yaml` presumably sequencing multiple such runs at the application layer. This is exactly the "Low complexity, High precision → Flow + direct calls" or "High complexity → Flow orchestrating multiple Crews" quadrant from CrewAI's own crew-vs-flow decision guide. Multi-crew pipelines (the "steps" in `job_config.yaml`) are a natural Flow.

## Non-negotiable constraint (2026-09-02)

`BaseCrewOrchestrator`/`FileCrewOrchestrator` — the path that lets a user run a single crew directly, no Flow involved — **stays**. It is not being deprecated, wrapped, or made a legacy fallback. Flow adoption is a second, additional entry point for multi-step pipelines, not a replacement for the simple case. If any implementation step here would require an existing single-crew caller to go through `Flow` to keep working, that step is wrong.

Second constraint: Flow-driven runs must get the **same** production capabilities as direct crew runs, not a lesser or separately-built version of them:

- **Checkpointing** ([05](05-checkpointing-consolidation.md)) — a `Flow` takes its own `checkpoint=` param; wire it through the same `CrewData`-style config shape and the same `StateManager.attach_checkpoint`/`resume_crew` mechanism `BaseCrewOrchestrator` already uses, not a parallel Flow-only implementation.
- **Memory** ([04](04-memory-adoption.md)) — crews kicked off from inside a Flow method should still respect the `memory:` config the same way a directly-run crew does; nothing about routing a crew through a Flow should silently disable memory.
- **Event listeners** ([09](09-event-observability-upgrade.md)) — the event bus is global (`CrewAIEventsBus`), so this is mostly free, but confirm Flow-method-execution events get fed into the same `AmshaEventListener` rather than requiring a second listener setup for Flow-based runs.

Concretely: whatever `FlowCrewOrchestrator` (or equivalent) is built in this proposal should be a thin adapter that reuses `CrewBuilderService`, `StateManager`, and the event listener as-is — not a fork of the state/checkpoint/memory logic that now has to be maintained twice.

## Proposal

Don't replace `BaseCrewOrchestrator`/`RuntimeEngine` outright (see [10](10-production-architecture-alignment.md) for how they coexist). Instead:

1. Introduce an **optional** Flow-based orchestration path alongside the existing file orchestrator — e.g. `amsha.crew_forge.orchestrator.flow.FlowCrewOrchestrator` — for job configs that declare multiple sequential/branching steps. The existing single-crew orchestrator (`FileCrewOrchestrator`) stays as-is for the common case; nothing forces existing Amsha consumers onto Flows.
2. Define a minimal Amsha `Flow` state model mapped from `job_config.yaml`'s pipeline structure — one Pydantic model per pipeline, fields for step outputs, so `job_config.yaml`'s declared steps become `@listen()` chains instead of application-level loop logic (wherever that loop currently lives — trace `job_config.yaml` consumers to confirm).
3. Use `@router()` for any job configs that need conditional branching (e.g., "if validation fails, retry with different agent") — this isn't expressible in Amsha's current sequential model at all.
4. Wire `RuntimeEngine`'s existing `ExecutionMode.INTERACTIVE`/`BACKGROUND` distinction to `Flow.kickoff()` vs `Flow.kickoff_async()`/`akickoff()` rather than reimplementing thread-pool dispatch for flow-driven runs.
5. Checkpoint/memory/event-listener parity per the constraint above — this is not optional polish, it's part of what "done" means for this proposal.

## What NOT to do

- Don't force every existing single-crew use case through a Flow wrapper — that's needless ceremony for the common case Amsha already handles well.
- Don't attempt this before [08](08-agent-task-capability-expansion.md) — Flow state models will want to carry richer task/agent config than Amsha's current 4-field domain models support.
- Don't build a separate checkpoint/memory/event-wiring path for Flow-based crews — reuse what [04](04-memory-adoption.md)/[05](05-checkpointing-consolidation.md)/[09](09-event-observability-upgrade.md) already built.

## Note (2026-09-02)

The Mongo/DB backend referenced below (`DbCrewOrchestrator`) no longer exists — Amsha is file-config-only (see [00](00-overview-and-roadmap.md) §0). "File/db orchestrators" in the text below should be read as "the file orchestrator."

## Open question for the user

Confirm where `job_config.yaml`'s "steps" are currently consumed/looped over (not fully traced in this research pass) — that's the exact insertion point for a Flow-based rewrite of multi-step pipelines.

**Answered during implementation:** the `pipeline` key in `job_config.yaml` (an ordered list of crew names) was **not consumed anywhere** — the app reads only `crews[<name>]` and its `input`; multi-crew sequencing was left entirely to the consuming application. The `pipeline` key is exactly what the Flow path now executes.

## Execution log

- **Item 1 (additive Flow path):** new `src/nikhil/amsha/crew_forge/orchestrator/flow/flow_crew_pipeline.py` — `FlowCrewOrchestrator` + `PipelineState`. `FileCrewOrchestrator`/`BaseCrewOrchestrator` are untouched; single-crew callers keep using `orchestrator.run_crew()`.
- **Item 2 (state model from `pipeline`):** `PipelineState` Pydantic model (`inputs` fed to every crew step, `outputs` accumulating each crew's raw result by name). A `Flow` subclass is built dynamically from the `pipeline`: `@start()` on the first crew, `@listen(previous)` on each subsequent — so ordering is guaranteed by the listener graph, not an app-level loop. Step methods delegate to the injected orchestrator's `run_crew(..., INTERACTIVE)`, which preserves execution-state tracking, performance monitoring, and the proposal-05 checkpoint recording/resume wiring (nothing orphaned by the split).
- **Item 3 (`@router` branching):** NOT built — sequential pipelines only. Branching needs a config syntax change plus a decision model; noted as the follow-up (add when a branching `job_config` appears).
- **Item 4 (mode wiring):** `FlowCrewOrchestrator.kickoff(inputs, mode)` — INTERACTIVE runs `flow.kickoff()` (native CrewAI async internally), BACKGROUND submits the whole flow to the backing `RuntimeEngine` and returns an `ExecutionHandle`, preserving the surrounding runtime contract.
- **App entry:** `AmshaCrewFileApplication.run_pipeline(inputs=None, mode=..., filename_suffix=...)` — builds inputs from the union of each pipeline crew's declared `input`, constructs the flow, kicks off. Additive.
- **Trade-off documented:** `crewai flow plot` visualizes a *file-based* `flows.py` class; dynamically built flow classes aren't plottable. The Flow value delivered here is the event-graph execution + typed state validation, not the plot command.
- Exports: `FlowCrewOrchestrator`/`PipelineState` from `crew_forge/__init__.py`.
- Tests: `tests/unit/crew_forge/orchestrator/flow/test_flow_crew_pipeline.py` (6 tests: order, shared inputs, typed state, last output, empty→error, BACKGROUND handle). Example verify 10/10 → 11/11 with a build-level flow check (no LLM).
