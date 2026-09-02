# Proposal 05 — Reconcile Amsha's StateManager with CrewAI Checkpointing

| | |
|---|---|
| **Priority** | Phase 5 (design together with [04](04-memory-adoption.md)) |
| **Risk** | Medium — overlapping responsibility with existing code, needs a clear decision, not just addition |
| **Effort** | Medium |
| **Depends on** | [02](02-crewai-version-migration.md) |
| **Status** | ✅ Done (2026-09-02) |

## What CrewAI's checkpointing does

`Crew`, `Flow`, and `Agent` all accept a `checkpoint` param (`True`/`False`/`CheckpointConfig`/`None` = inherit). A checkpoint captures: full config, agent memory + knowledge, task progress, intermediate outputs, internal state, kickoff inputs, event history, and a lineage ID. Resume skips completed tasks and reloads memory/knowledge. Forking (`restore_from_state_id`) starts a new lineage from a snapshot without mutating the original — can run concurrently with the original run. Config: `CheckpointConfig(location=, on_events=["task_completed"], provider=JsonProvider|SqliteProvider, max_checkpoints=, restore_from=)`.

## Current state in Amsha — this is the important part

Amsha **already has a parallel, hand-built system** for exactly this problem:

- `ExecutionState` (`execution_state/domain/execution_state.py`) — tracks `execution_id`, `inputs`, `status`, `set_output()`.
- `StateManager` — `create_execution()`, `get_execution()`, `update_status()`, backed by `IStateRepository` (currently only `InMemoryStateRepository` — **state is lost on process restart today**).
- `ExecutionHandle`/`RuntimeEngine` — wraps a `concurrent.futures.Future`, exposes `.status()`, `.result()`, `.cancel()`.

This is **not** the same thing as CrewAI's checkpointing yet — Amsha's version tracks *whether a run succeeded/failed and what its final output was*, not *task-by-task progress with resume capability*. There is no resume path in Amsha today: if a crew fails partway through a multi-task run, `StateManager` records `FAILED` but there's no way to pick up from the last completed task. CrewAI's native checkpointing does exactly that, natively, today.

## The actual decision to make

This isn't "add checkpointing," it's "stop maintaining a duplicate, less-capable version of something CrewAI now does natively." Three options, ranked:

1. **(Recommended) Delegate to CrewAI checkpointing for what it already covers, keep `StateManager` for what it doesn't.** CrewAI's checkpoint captures task-level resume state; Amsha's `StateManager`/`ExecutionState` covers Amsha-specific concerns CrewAI has no concept of — `execution_id` correlation with Amsha's own logging/monitoring (`CrewPerformanceMonitor`). Concretely: set `Crew(checkpoint=CheckpointConfig(...))` in `CrewBuilderService.build()`, and have `BaseCrewOrchestrator.run_crew()` record the CrewAI-issued lineage/checkpoint ID into Amsha's own `ExecutionState` (a new field) rather than reimplementing task-progress tracking. Use CrewAI's own `JsonProvider`/`SqliteProvider` for durability — see note below on why a Mongo-backed option is off the table now.
2. **Replace `StateManager` entirely with CrewAI checkpointing.** Simpler, but loses Amsha's independence from CrewAI's own execution model (relevant if Amsha ever orchestrates non-CrewAI work through the same `RuntimeEngine`).
3. **Keep both, fully separate.** This is the status quo plus checkpointing bolted on with no integration — not recommended, since it means two sources of truth for "did this run finish" with no reconciliation, and a future maintainer has to know which one to trust.

**Update (2026-09-02):** the MongoDB backend and `crew_forge/repo/adapters/mongo/` referenced below as a durability option no longer exist — Amsha dropped the DB/Mongo backend entirely in favor of file-only configuration (executed alongside [02](02-crewai-version-migration.md) in the same session, out-of-band from the original proposal set). `InMemoryStateRepository` remains the only `IStateRepository` implementation, so cross-process durability for `StateManager` is still an open gap — if it's ever needed, it'll have to be a new adapter (e.g. SQLite, flat-file), not Mongo.

## Proposal (Option 1, concretely)

1. Add `checkpoint: Optional[CheckpointConfig] = None` to `CrewData`.
2. In `CrewBuilderService.build()`, pass it through to `Crew(checkpoint=...)`.
3. In `BaseCrewOrchestrator.run_crew()`, after `crew_to_run.kickoff()`, extract whatever lineage/checkpoint identifier CrewAI exposes on the crew/result object and call a new `StateManager.attach_checkpoint(execution_id, checkpoint_ref)` — additive, doesn't change the existing status-tracking flow.
4. Implement a `MongoStateRepository` (mirroring the existing `crew_forge/repo/adapters/mongo/*` pattern) as an `IStateRepository` if durable, cross-process execution history is actually needed — currently `InMemoryStateRepository` is the only implementation, so state doesn't survive a restart regardless of what checkpointing config is added. This is a pre-existing gap this proposal surfaces but doesn't fully solve on its own; flag as a follow-up decision for the user.
5. Expose a resume entry point on `BaseCrewOrchestrator` (e.g. `resume_crew(execution_id)`) that looks up the stored checkpoint reference and calls CrewAI's restore path, rather than Amsha inventing its own resume semantics.

## What this looks like from the YAML side

Both `checkpoint` (this proposal) and `memory` ([04](04-memory-adoption.md)) thread through the same `CrewData` model, so a use case opting into both would look like:

```yaml
# job_config.yaml (crew-level config block)
crew:
  memory: true
  checkpoint:
    enabled: true
    on_events: ["task_completed"]
    provider: sqlite          # or "json"
    location: "./execution/checkpoints"
    max_checkpoints: 10
```

`CrewData` maps `checkpoint.enabled: false` (or the key omitted) to `checkpoint=None` passed to `Crew()`, preserving today's behavior for existing configs. `checkpoint.provider`/`location`/`on_events`/`max_checkpoints` map directly onto `CheckpointConfig`'s matching constructor fields. This is the concrete shape a user needs to know before adopting the feature — everything above is additive to the existing `job_config.yaml` schema, no existing keys change meaning.

## What NOT to do

- Don't build a second checkpoint/resume mechanism from scratch now that CrewAI has one natively — that's the exact duplication this proposal exists to stop.

## Execution log

- `CrewData.checkpoint: Optional[bool | dict] = None` added (domain layer stays free of crewai imports); `CrewBuilderService` coerces it for `Crew(checkpoint=...)`: `None`/`False`/`enabled: false` → `None`, `True` → `True` (CrewAI defaults), dict → `CheckpointConfig` with `provider` resolved to `JsonProvider`/`SqliteProvider`; an unknown provider raises a clear `ValueError`.
- `AmshaJobConfig.CrewDefinition` gained `checkpoint`, so the crew-level YAML key survives validation + `model_dump()` (this was the actual wiring trap — the manager's `crew_def` is the validated model's dump, which silently dropped unknown keys).
- Proposal item 3 done: `BaseCrewOrchestrator.run_crew()` now passes an optional `from_checkpoint` through to `kickoff(...)` and, after a successful run on a checkpoint-enabled crew, records the checkpoint `location` via new `StateManager.attach_checkpoint(execution_id, ref)`.
- Proposal item 5 done: `BaseCrewOrchestrator.resume_crew(crew_name, inputs, execution_id, restore_from)` looks up the stored checkpoint ref and forwards `CheckpointConfig(location=ref, restore_from=...)` into `run_crew`, delegating resume to CrewAI's native restore. A run with no recorded checkpoint raises `CrewExecutionException`.
- Proposal item 4 (**durable `IStateRepository`**, e.g. Mongo/SQLite/flat-file) remains an open follow-up — `InMemoryStateRepository` is still the only implementation, so `ExecutionState` (including the recorded checkpoint ref) does not survive a process restart. Not blocking: resume within a process works today.
- Example: `job_config.yaml` `copy_crew` opts into `json` checkpointing; `verify_capability_example.py` asserts the built crew's `CheckpointConfig.location` matches the YAML.
- Unit tests: builder coercion (bool/dict/provider/enabled-false/unknown-provider) in `test_crew_builder_service.py`; `attach_checkpoint` in `test_state_manager.py`; recording + `resume_crew` (+ error paths) in `test_base_crew_orchestrator.py`; config schema in `tests/unit/configuration/domain/test_amsha_job_config.py`.
- Docs updated: `functional.md` (FR-CREW-04), `About.md` §5, `00-overview-and-roadmap.md §4`.
