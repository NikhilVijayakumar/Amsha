# Proposal 07 — Crew Lifecycle Verification (Phase 3 addendum)

| | |
|---|---|
| **Status** | Proposed |
| **Priority** | Medium — closes the one confirmed gap in crew verification: lifecycle fields (`memory`/`tracing`/`checkpoint`) are completely unverified |
| **Risk** | Low — same shape as the existing guardrail checks; adds a small, faithful ingestion surface; never silently rewrites |
| **Effort** | Small |
| **Depends on** | 03 (Phase 3 verification engine), 3b (05 — crew component checks) |

## Goal

Extend crew verification to cover the **lifecycle** fields (`memory`, `tracing`, `checkpoint`) that the existing `verify_crew_yaml` crew checks ignore. The current crew checks (`crew.single_agent_crew` … `crew.process_hierarchical_no_manager`) all verify *design/architecture* — genuine collaboration, bounded scope, process correctness. None verifies the runtime/lifecycle settings that govern whether a crew retains state, streams telemetry, and can recover. This addendum closes that gap with three checks, following the exact same registry + `_finding` pattern as the guardrail checks shipped in Phase 3/4.

## What gets verified

Three lifecycle concerns with distinct, real rule sources:

| Check | CrewData field | Rule source |
|---|---|---|
| `crew.tracing_enabled_no_warning` | `tracing` | `implementation/19-observability-and-tracing.md` §177 — sensitive/private prompts must stay protected; turning tracing on without acknowledging the privacy/cloud cost is a silent exposure |
| `crew.memory_unjustified` | `memory` | `implementation/11-context-knowledge-memory.md` — "Introduce Memory only when historical information materially improves execution." |
| `crew.checkpoint_no_events` | `checkpoint` | `implementation/17-checkpointing-and-recovery.md` §4 — checkpoints exist at recovery boundaries; a checkpoint with no recovery triggers is inert |

### 1. `crew.tracing_enabled_no_warning`

- **Fires when:** `tracing=true` but nothing in the crew/agent/task text acknowledges the privacy cost (a privacy/cloud opt-in or cost-exposure statement is absent).
- **Severity:** **warning** — tracing is a permitted default behavior; a user may run with a warning. `tracing=true` alone is NOT an error.
- **Grounding:** `CrewData.tracing` description ("Enable CrewAI native tracing (sends full prompt/response content …)") + `implementations/19` §177 ("never log private prompts… sensitive info stays protected") + §203 (anti-pattern "Log Everything — noise, cost, security risk").
- **Fix message:** state that enabling tracing transmits full prompt/response content; require an explicit acknowledgment of the privacy/cloud exposure before enabling, or scope tracing to non-sensitive executions.

### 2. `crew.memory_unjustified`

- **Fires when:** `memory=true` but no cross-execution / historical-retention need is evident in the crew goal or task text (no signals of "across runs," "remember," "previous," "retain," "reject feedback," iterative refinement across executions).
- **Severity:** **warning** — memory is a permitted capability; a crew may keep it on with a warning.
- **Grounding:** `implementation/11` Memory Practice — "Introduce Memory only when historical information materially improves execution." A single-shot crew with no cross-execution need gets retention cost and stale-data risk for nothing.
- **Fix message:** justify the cross-execution retention or turn memory off; a crew that runs once and never re-consumes history does not need a memory system.

### 3. `crew.checkpoint_no_events`

- **Fires when:** `checkpoint` is enabled (bool `true`, or a dict) but the dict has no `on_events` (and the bool form sets no recovery triggers).
- **Severity:** **warning** — a checkpoint without recovery triggers is inert, not fatal.
- **Grounding:** `CrewData.checkpoint` describes the dict form (`enabled`/`on_events`/`provider`/`location`/`max_checkpoints`); `implementation/17` §4 — "Create checkpoints at meaningful recovery boundaries…" A checkpoint captures nothing durable if no `on_events` ever trigger it.
- **Fix message:** declare the `on_events` (e.g. `["task_completed"]`) that mark real recovery boundaries; otherwise the checkpoint cannot resume a workflow and is dead configuration.

## Design

### Where the checks live (the key finding)

**The crew lifecycle fields cannot be read by `verify_crew_yaml` today.** The crew checks run against `_crew_struct(agents, tasks)` (`verification.py:1180`), which holds only `{"agents", "tasks"}` parsed from `crew_dir/agents/*_agent.yaml` and `crew_dir/tasks/*_task.yaml`. Those fields exist solely on `CrewData` (`crew_forge/domain/models/crew_data.py`), which the product hydrates **not** from the agent/task dir but from a **crew block inside `job_config.yaml`**:

```yaml
# example/crew_forge/example_config/job_config.yaml (real source)
crews:
  copy_crew:
    memory: true
    tracing: false
    checkpoint:
      enabled: true
      provider: json
      location: "./.Amsha/execution/checkpoints"
      on_events: ["task_completed"]
      max_checkpoints: 5
```

…read in `atomic_crew_file_manager.py:56-61`:

```python
crew_data = CrewData( llm= self.llm, ...,
    memory= crew_def.get("memory", False),
    checkpoint= crew_def.get("checkpoint"),
    tracing= crew_def.get("tracing"))
```

So the faithful home for these checks is the **crew-def surface** (a `job_config.yaml` `crews[<name>]` block), NOT `verify_crew_yaml`'s agent/task directory. Grounding every check in real Amsha source, we do NOT retrofit lifecycle fields into the agent/task dir layout the product never uses.

### New tool surface

Add one small tool that ingests a crew definition and runs the lifecycle checks:

- **`verify_crew_def(crew_def: dict)`** — accepts a crew block (name + `memory`/`tracing`/`checkpoint`/`steps`), validates it against `CrewData`'s field shapes (bool|dict for `checkpoint`, Optional[bool] for `memory`/`tracing`) via the real `CrewData` schema, then runs the three lifecycle checks. Follows the same "report, never rewrite" contract as every Phase 3+ tool: returns findings with severity/rule/reference/fix; the user or LLM applies them.

Optionally, a **`verify_job_config(job_config_path)`** wrapper that reads a `job_config.yaml`, loops its `crews[*]`, and runs `verify_crew_def` per crew — so the whole file is checked in one call. (Kept separate so a caller can verify a single in-memory crew def without a file.)

### Wiring

Mirrors the Phase 3/4 registry pattern exactly (`verification.py:931-940`):

```python
# _COMPONENT_CHECKS["crew"] additions (or a sibling _CREW_DEF_CHECKS list)
("crew.tracing_enabled_no_warning", "warning", "19 observability-and-tracing §177", "Tracing privacy unacknowledged", _check_tracing_no_warning),
("crew.memory_unjustified",        "warning", "11 context-knowledge-memory",    "Memory unjustified",        _check_memory_unjustified),
("crew.checkpoint_no_events",      "warning", "17 checkpointing-and-recovery §4", "Checkpoint with no events",  _check_checkpoint_no_events),
```

Each `_check_*` uses `_finding(severity, rule, source, message, fix)` and the same string-signal constant style as `_VAGUE_GUARDRAILS` / `_STRICT_OUTPUT_SIGNALS` (`verification.py:526`) for detection (e.g. a `_TRACING_PRIVACY_ACK` / `_MEMORY_RETENTION_NEED` keyword set).

### Reuse, don't reinvent

- Reuse `CrewData` (real schema) for structural validation of the crew-def block — a parallel schema here would drift from what `crew_forge` actually executes, violating the `00-roadmap` rule.
- Reuse `_finding`, the registry-list shape, and the warning/error severity model from Phase 3.
- Reuse `CrewParser`'s job-config conventions where the wrapper reads files.

## Ponytail check

- **Could we just add the checks to `verify_crew_yaml`?** No — that function never reads `job_config.yaml` or `CrewData`, and retrofitting lifecycle flags into the agent/task-dir layout invents a file shape the product doesn't use. The crew-def surface is where the fields actually live.
- **Is a second tool overkill?** `verify_crew_def` alone covers the single-crew case; `verify_job_config` is a thin loop that makes the multi-crew file case one call. Both are small; the loop is a few lines over `verify_crew_def`.
- **Spec-generation / the 60-cell capability matrix:** explicitly OUT of scope. See the "Non-goals" section.

## Non-goals (deliberately deferred, not silently folded in)

- **Spec / architecture generation** (`validation.md` §5/§18/§19, the Propose/Generate columns). This is in direct tension with the methodology's repeated, explicit rule — `02-architecture-guidance.md:76`: *"auto-filling is exactly the kind of silent rewrite the methodology forbids… the artifacts are the user's design commitments, not machine guesses."* Building a spec-generator is a philosophy change requiring a deliberate decision, not a natural next phase. The only legitimate generative affordance is the existing one: Phase 4 `suggest_fixes` *proposes* drafts the user explicitly approves.
- **State-ownership / event-listener event-loop / atomicity-as-category** (`validation.md` §13/§15/§7). Real, but larger; some are runtime concerns, not static-YAML-verification ones. Tracked as future decisions.
- **LLM load/unload/switching.** Verified in `llm_factory` source: Amsha only builds a client pointed at an already-running endpoint; there is no load/unload/dispose concept anywhere. A check for it would invent a capability that doesn't exist — breaks "ground every check in real source." Skipped unless Amsha grows the capability first.
- **The full `Guide/Propose/Validate/Evaluate/Optimize/Generate × 10 stages` matrix.** A planning map, not a build list. Use it to see what's covered (Validate/Evaluate for Agent/Task/Crew — done) vs. empty (Optimize/Propose/Generate almost everywhere — correctly so, per the authoring rule).

## Test plan

- **Unit:** for each check, a crew-def that sets the field the "wrong" way surfaces the specific `rule_id`; a conformant crew-def surfaces none; a crew-def with all three set wrong surfaces all three.
- **Fixture:** a `job_config.yaml`-style crew block (mirroring `example/crew_forge/example_config/job_config.yaml`) — `memory: true` with no retention need, `tracing: true` with no privacy ack, `checkpoint: {enabled: true}` with no `on_events`.
- **In-process group** in `mcp/tests/test_stdio.py`, same style as the guardrail tests (no full CrewAI-spawning server; `crew_def` checks are pure dict logic, so they run fast).
- Verify `verify_job_config` loops multiple crews and reports per-crew findings.

## Summary

Three low-risk, high-value checks (`crew.tracing_enabled_no_warning`, `crew.memory_unjustified`, `crew.checkpoint_no_events`) that close the crew-lifecycle verification gap, placed on the faithful `job_config.yaml` crew-def surface. Same shape as the guardrail fix, same report-never-rewrite contract. Leaves spec-generation and the 60-cell matrix as deliberate future decisions.
