# Proposal 03 — Adopt CrewAI Flows

| | |
|---|---|
| **Priority** | Phase 3 (after capability expansion, memory, checkpointing) |
| **Risk** | Medium — architectural addition, not a rewrite |
| **Effort** | Medium-Large |
| **Depends on** | [02](02-crewai-version-migration.md), pairs with [10](10-production-architecture-alignment.md) |

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

## Proposal

Don't replace `BaseCrewOrchestrator`/`RuntimeEngine` outright (see [10](10-production-architecture-alignment.md) for how they coexist). Instead:

1. Introduce an **optional** Flow-based orchestration path alongside the existing file/db orchestrators — e.g. `amsha.crew_forge.orchestrator.flow.FlowCrewOrchestrator` — for job configs that declare multiple sequential/branching steps. Existing single-crew orchestrators (`FileCrewOrchestrator`, `DbCrewOrchestrator`) stay as-is for the common case; nothing forces existing Amsha consumers onto Flows.
2. Define a minimal Amsha `Flow` state model mapped from `job_config.yaml`'s pipeline structure — one Pydantic model per pipeline, fields for step outputs, so `job_config.yaml`'s declared steps become `@listen()` chains instead of application-level loop logic (wherever that loop currently lives — trace `job_config.yaml` consumers to confirm).
3. Use `@router()` for any job configs that need conditional branching (e.g., "if validation fails, retry with different agent") — this isn't expressible in Amsha's current sequential model at all.
4. Wire `RuntimeEngine`'s existing `ExecutionMode.INTERACTIVE`/`BACKGROUND` distinction to `Flow.kickoff()` vs `Flow.kickoff_async()`/`akickoff()` rather than reimplementing thread-pool dispatch for flow-driven runs.

## What NOT to do

- Don't force every existing single-crew use case through a Flow wrapper — that's needless ceremony for the common case Amsha already handles well.
- Don't attempt this before [08](08-agent-task-capability-expansion.md) — Flow state models will want to carry richer task/agent config than Amsha's current 4-field domain models support.

## Open question for the user

Confirm where `job_config.yaml`'s "steps" are currently consumed/looped over (not fully traced in this research pass) — that's the exact insertion point for a Flow-based rewrite of multi-step pipelines.
