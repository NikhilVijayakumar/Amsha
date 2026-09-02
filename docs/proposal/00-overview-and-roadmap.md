# Amsha × CrewAI 1.x — Overview, Gap Analysis & Roadmap

| | |
|---|---|
| **Status** | Phases 1–2, 4, 5, 6, 7, 8 done (2026-09-02); see below |
| **Date** | 2026-09-02 |
| **Author** | Nikhil (compiled with Claude) |
| **Scope** | Align Amsha with current CrewAI (docs v1.15.18) capabilities |

## 0. Scope change: Mongo/DB backend removed (2026-09-02)

Out-of-band from the original proposal set: the entire MongoDB/DB-backend code path — `crew_forge/repo/`, `crew_forge/sync/`, `crew_forge/dependency/{mongo,crew_forge}_container.py`, `crew_forge/orchestrator/db/`, `database_seeder.py`, `atomic_db_builder.py`, `config_sync_service.py`, `crew_blueprint_service.py`, the `RepoBackend` enum, and `pymongo` as a dependency — was deleted. Amsha is now file-config-only. This was a direct instruction, not a proposal-driven decision, but it affects any proposal above that mentioned the Mongo path as an option (see the update note in [05](05-checkpointing-consolidation.md)). The file-based orchestrator (`AtomicYamlBuilderService`, `FileCrewOrchestrator`, `AmshaCrewFileApplication`) was untouched in capability — one incidental fix was needed in `AtomicCrewFileManager`, which had been using the now-deleted `CrewForgeContainer` purely for DI wiring around `AtomicYamlBuilderService`; replaced with direct instantiation (no container needed for a single-implementation file path).

## 1. Why this exists

Amsha was built against `crewai==0.201.1`. CrewAI crossed 0.x → 1.x on **2025-10-20** and has since shipped roughly one release every 1–2 weeks (currently at `1.15.18` for `crewai-core`/`crewai-cli`, `1.15.16` for `crewai-tools`; the umbrella `crewai` package itself lags at `1.14.6`, see [01-crewai-version-migration](01-crewai-version-migration.md)). In that time CrewAI added several capability categories Amsha has no concept of at all — Flows, unified Memory, Checkpointing, Skills, Files, a real event bus — while Amsha's own domain models (`AgentRequest`, `TaskRequest`) only expose `role/goal/backstory` and `name/description/expected_output`, blocking access to most of what CrewAI 1.x agents/tasks can do even *without* a version bump.

Separately, Amsha depends on a git-sourced sibling library, **Nibandha**, purely for logging/log-rotation/output-directory bookkeeping. It is not a core Amsha capability and its git-dependency nature (`Nibandha[export] @ git+...`) is exactly the kind of thing that turns a routine `pip install -U crewai` into a dependency-resolution fight. It should come out before touching the CrewAI version.

## 2. Current state (verified against source, not memory)

- **Pinned versions** (`pyproject.toml`): `crewai==0.201.1`, `crewai-tools==0.75.0`.
- **Crew assembly** (`CrewBuilderService`): builds plain `Agent(role, goal, backstory, llm, tools)` and `Task(name, description, expected_output, agent)`. No `memory`, `planning`, `reasoning`, `guardrail`, `context`, `human_input`, `async_execution`, `allow_delegation`, `max_iter`, `output_pydantic`, `checkpoint`, or `multimodal` anywhere in the codebase.
- **Domain models** (`AgentRequest`/`TaskRequest`): four fields each (`role/goal/backstory/usecase`, `name/description/expected_output/usecase`). This is the actual bottleneck — even after a version bump, these Pydantic models can't carry the new fields through to `Agent`/`Task` construction.
- **Knowledge**: `AmshaCrewDoclingSource` wraps `docling` to convert PDF/DOCX/HTML/XLSX/PPTX/images to markdown for `BaseKnowledgeSource`. No JSON support — but CrewAI 1.x ships JSON as a **native, built-in** knowledge source type, so Amsha doesn't need docling for this at all (see [06](06-knowledge-json-native-support.md)).
- **Orchestration**: `BaseCrewOrchestrator` + `RuntimeEngine` (thread pool, sync/async submit) + `StateManager` (in-memory execution state, status enum, save/get). This is a bespoke, parallel implementation of roughly what CrewAI 1.x now offers natively via `Crew(checkpoint=...)`/`Flow(checkpoint=...)` and `@persist()`. No `Flow` usage anywhere in the codebase.
- **Monitoring**: `CrewPerformanceMonitor` — manual before/after `psutil`/`pynvml` snapshots plus post-hoc parsing of `result.token_usage`. No use of CrewAI's event bus (`CrewAIEventsBus`), which now exposes ~100+ granular lifecycle events including LLM streaming chunks, tool calls, memory ops, and guardrail validation.
- **Logging**: `amsha.common.logger` is a thin wrapper around `nibandha.core.nibandha_app.Nibandha`, used only for structured logging + log rotation + output-folder scaffolding (`.Nibandha/`, `output/final`, `output/intermediate`). No other Amsha module depends on Nibandha's actual feature set beyond logging.

## 3. Gap matrix

| Capability | CrewAI 1.x | Amsha today | Gap | Proposal |
|---|---|---|---|---|
| Flows (event-driven orchestration) | Core, flow-first is now the recommended pattern | None — bespoke `RuntimeEngine`/`StateManager` instead | High | [03](03-flows-adoption.md) |
| Memory | Unified `Memory` class, scope-tree, LanceDB | None (`memory=` never set) | High | [04](04-memory-adoption.md) |
| Checkpointing | Native `checkpoint=` on Crew/Flow/Agent, fork/resume | Bespoke `StateManager` (status only, no resume) | High (overlap + gap) | [05](05-checkpointing-consolidation.md) |
| Knowledge — JSON | Native, built-in source | Not supported (docling has no JSON path) | Medium, easy win | [06](06-knowledge-json-native-support.md) |
| Skills | Net-new concept, `SKILL.md` directories | None | Medium | [07](07-skills-adoption.md) |
| Agent/Task capability surface | reasoning, planning, guardrails, context, human_input, async_execution, output_pydantic, files, apps/MCP | 4-field domain models, none of the above reachable | High, blocks everything else | [08](08-agent-task-capability-expansion.md) |
| Event Listener system | ~100+ events, real-time bus | Manual pre/post snapshot monitoring | Medium | [09](09-event-observability-upgrade.md) |
| Production architecture | Flow-first, LLM Hooks, fork/lineage | Ad hoc orchestrator + thread pool | Medium | [10](10-production-architecture-alignment.md) |
| Crafting good agents/tasks | Documented heuristics (crafting-effective-agents guide) | Nothing enforces or teaches this | Low effort, high leverage | [11](11-agent-task-crafting-skill.md) |
| CrewAI version | 1.15.18 (core/cli), 1.15.16 (tools) | 0.201.1 / 0.75.0 | Structural (monorepo split, breaking changes) | [02](02-crewai-version-migration.md) |
| Nibandha dependency | n/a | Logging/rotation only, git dependency | Migration friction risk | [01](01-nibandha-removal.md) |

## 4. Recommended sequencing

Doing these in the wrong order compounds risk. Recommended phase order:

1. **[01 — Remove Nibandha](01-nibandha-removal.md). ✅ Done (2026-09-02).** Independent of CrewAI entirely. Removed the git-sourced dependency before it could complicate `pip`/`uv` resolution during the CrewAI bump — logger rewritten to stdlib, 45 logger-dependent tests passing. Pre-existing unrelated test failures remain (see execution log in 01) and are unaffected by this change.
2. **[02 — CrewAI version migration](02-crewai-version-migration.md).** Get onto 1.x before building anything new against 1.x-only APIs. Everything below assumes this is done.
3. **[08 — Agent/Task capability expansion](08-agent-task-capability-expansion.md). ✅ Done (2026-09-02).** `AgentRequest`/`TaskRequest` extended with optional execution/capability/prompt fields (backward-compatible), `CrewBuilderService` passes them through to CrewAI 1.15.18 constructors conditionally, `TaskRequest.context` resolves names to `Task` objects, and `CrewParser` now forwards new YAML fields instead of silently dropping them. Unblocks memory, skills, reasoning, planning, guardrails.
4. **[06 — Knowledge JSON support](06-knowledge-json-native-support.md)** ✅ Done (2026-09-02) and **[07 — Skills](07-skills-adoption.md)** ✅ Done (2026-09-02) — additive, low-risk, done in parallel once (3) landed. JSON knowledge routes to CrewAI's native JSON source; skills resolve by name from a `skills/` directory convention.
5. **[04 — Memory](04-memory-adoption.md)** and **[05 — Checkpointing consolidation](05-checkpointing-consolidation.md)** — these two should be designed together since CrewAI's native checkpoint already snapshots memory state; Amsha's `StateManager` needs to either delegate to or be replaced by it. **✅ Done (2026-09-02), together.** Crew-level `memory:`/`checkpoint:` now opt in per crew from `job_config.yaml`; builder passes them to CrewAI 1.15.18; `run_crew` records the checkpoint location on `ExecutionState` and `resume_crew` resumes via CrewAI's native `from_checkpoint` restore. Memory storage stays at CrewAI's default path for now (see 04 log). Follow-up flagged in 05: a durable `IStateRepository` so recorded checkpoints survive process restarts.
6. **[03 — Flows adoption](03-flows-adoption.md)** and **[10 — Production architecture alignment](10-production-architecture-alignment.md)** — the bigger architectural shift; do this once the smaller pieces are stable, since Flow-first changes how `BaseCrewOrchestrator` fits in.
7. **[09 — Event observability upgrade](09-event-observability-upgrade.md)** — replace/augment `CrewPerformanceMonitor` once Flows/Memory land, since new event categories (memory ops, flow methods) only exist once those are in use.
8. **[11 — Agent/Task crafting skill](11-agent-task-crafting-skill.md)** — can actually be done *first* or in parallel with anything above; it's a Claude Code skill, not a code change to Amsha, and is most useful once (3) gives it real fields to work with.

## 5. Non-goals

- No proposal here suggests deleting `RuntimeEngine`/`StateManager`/`CrewPerformanceMonitor` outright before CrewAI's native equivalents are verified to cover the same use cases in Amsha's actual orchestrator/file/db modes. See [05](05-checkpointing-consolidation.md) and [09](09-event-observability-upgrade.md) for the specific consolidation decision points.
- No proposal here changes Amsha's MongoDB sync / YAML config-as-code model (`SyncCrewConfigManager`, `crew_forge.seeding`) — that's orthogonal to CrewAI's own feature set.
