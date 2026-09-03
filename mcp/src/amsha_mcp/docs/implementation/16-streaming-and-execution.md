# Streaming and Execution

## Purpose

Defines how **Execution, Streaming, Events, Progress, Results, and Runtime Observation** are modeled and engineered within Amsha.

> **Execution is the runtime realization of an approved architecture. Streaming exposes execution progress and events without changing workflow semantics.**

Streaming is an **observability and interaction mechanism**, not an alternative orchestration model.

Extends: `05`, `06`, `08`, `09`, `10`, `13`, `15`.

---

# 1. Execution

Execution is the runtime process performing an approved architecture: `Architecture → Implementation → Execution → Processes → Outputs/Artifacts → Completion`. Answers: "What is happening right now as the architecture runs?"

**Execution ≠ Architecture.** Architecture defines what should happen, why, what components are required, how they relate, what success means, how failure is handled. Execution determines what is happening now, what completed/is waiting/failed/running, what outputs exist.

**Execution ≠ Flow.** A Flow defines execution control; Execution is the runtime instance (`Flow Definition → Execution Instance → Runtime State`). Flow `chapter_production` is reusable; Execution `execution_2026_001` is one instance.

**Identity:** every meaningful execution has an id:

```yaml
execution:
  id: execution_001
  flow_id: chapter_production
  flow_version: "1.0"
```

**Lifecycle:** `CREATED → INITIALIZING → RUNNING → WAITING → RUNNING → COMPLETED`; failure paths `FAILED, CANCELLED, TIMED_OUT, ABORTED`. Not every execution needs every state.

**State** holds only what's needed to understand/control the current run: execution_id, flow_id/version, current_process, status, inputs, process outputs/references, decisions, iteration counters, approval/failure/termination state, checkpoint, timestamps. Not a general-purpose runtime database.

**Current State vs Event History:** State answers "What is true now?" (`current_process = evaluate_chapter, status = RUNNING`); Event History answers "What happened?" (chapter_generation_started/completed, evaluation_started/completed, revision_requested).

---

# 2. Events

An Event represents something that happened (execution_started, process_started/completed/failed, task_started, agent_started, tool_called/completed, artifact_created, human_approval_requested/received, execution_completed). Events should be explicit and structured.

**Event ≠ State:** an event (`evaluation_completed`) is a transition, not the complete state. `Event → State transition → Current State`. Critical for recovery and observability.

**Event ≠ Output:** a Process output is data (`chapter_review.json`, may become an Artifact); an Event is runtime information (`evaluate_chapter completed successfully`, belongs to execution history).

---

# 3. Streaming

Streaming exposes runtime info incrementally: `Execution → {Event, Event, ... , Final Result}` instead of `Execution → Final Result`.

**Streaming is an observation layer** beside execution:

```
FLOW → EXECUTION → {State, Events → Streaming}
```

It does not replace Flow, Process, Crew, Task, Agent, Python, Tool, or MCP.

**Streaming does not change workflow semantics.** A workflow yields the same logical result whether streamed or awaited, unless interactive behavior is explicitly architectural. It must not accidentally introduce hidden orchestration.

**Execution modes** (modes, not different architectures): synchronous, asynchronous, streaming, background, resumable, interactive.

- **Synchronous:** `request → execute → wait → result`; when short, no progress UI, no human gate.
- **Streaming:** `request → starts → events → progress → final result`; for long-running, interactive apps, CLI, UI progress, debugging, human-facing execution.
- **Asynchronous:** `request → created → execution_id returned → background → status/events/result`; when execution may outlive the request.

**Streaming + async often combine:** `Client → Start Execution → execution_id → Subscribe/retrieve events → Execution continues → Final result`. The architecture must distinguish `execution lifetime, connection lifetime, stream lifetime` — they don't necessarily coincide.

---

# 4. Connection Handling

**Connection failure:** a stream may disappear while execution continues. Never automatically interpret `stream disconnected` as `execution failed` unless explicitly designed that way.

**Execution status vs stream status** are separate:

```yaml
runtime:
  execution:
    status: RUNNING
  stream:
    status: DISCONNECTED
```

The execution may continue even if the stream is unavailable.

**Reconnection:** a resumable stream lets the client reconnect using `execution_id, event sequence, checkpoint, cursor`. A client should not restart the execution just because it lost the stream.

---

# 5. Event Ordering, Identity, Schema

**Ordering:** sequence number is more reliable than timestamps:

```yaml
event:
  execution_id: execution_001
  sequence: 42
  timestamp: "..."
```

**Identity** prevents duplicate processing on reconnect:

```yaml
event:
  id: event_00142
  execution_id: execution_001
  sequence: 42
```

**General event schema:**

```yaml
event:
  id: ""
  execution_id: ""
  sequence: 0
  timestamp: ""
  type: ""
  source:
    component_type: ""
    component_id: ""
  process_id: ""
  task_id: ""
  agent_id: ""
  crew_id: ""
  status: ""
  payload: {}
  artifact_references: []
  error: null
  metadata: {}
```

Only relevant fields get populated.

---

# 6. Event Vocabulary

**Categories:** `EXECUTION, PROCESS, TASK, AGENT, CREW, TOOL, MCP, ARTIFACT, HUMAN, CHECKPOINT, FAILURE, FLOW`. Example names: `execution.started`, `process.started`, `task.completed`, `tool.called`, `artifact.created`, `human.approval_requested`.

- **Execution:** created, started, waiting, resumed, cancelled, completed, failed, timed_out.
- **Flow:** started, transition.evaluated/taken, parallel.started/completed, iteration.started/completed, terminated.
- **Process:** started, waiting, completed, failed, retrying, skipped.
- **Task:** started, completed, failed, retrying — expose only when useful; don't emit excess events.
- **Agent:** started, thinking, tool_called, completed, failed. Internal reasoning should not be automatically streamed.
- **Tool:** started, completed, failed, timeout.
- **MCP:** requested, completed, failed, timeout — same security rules as `14-mcp-integration.md`; never expose credentials/secrets.
- **Artifact:** created, validating, valid, invalid, versioned, superseded, archived, deleted. Never include large content; use references.
- **Human:** approval_requested, approval_received, revision_requested, rejected, timeout.
- **Failure:** structured (category, retryable, message). Avoid dumping arbitrary exception traces to user streams; keep diagnostics in logs.

---

# 7. Internal Reasoning

Distinguish **execution event** from **private/internal model reasoning**. Do not expose hidden chain-of-thought merely because an Agent streams. A useful event instead carries: status, high-level action, tool invocation, decision result, confidence, structured explanation — where appropriate.

---

# 8. Streaming Detail Levels & Visibility

**Detail levels:** `MINIMAL` (process started/completed, execution failed), `NORMAL` (process, task, artifact, high-level progress), `DEBUG` (tool calls, timings, internal metadata) — debug respects security boundaries.

**User-facing vs internal events:** not every internal event is exposed. A public projection may remove secrets, internal prompts, private reasoning, sensitive metadata, implementation details.

**Event projection:** `Internal Event → Security/Policy Filter → Public Event → Stream`, preferable to exposing raw runtime events.

---

# 9. Progress

Progress derives from meaningful state, not fake precision.

**Process-level progress:** `processes completed/running/pending/failed` — e.g. `progress: {completed: 3, running: 1, pending: 2}`. Avoid `73.42% complete` unless the architecture justifies it.

**Weighted progress** (`Research 10%, Generation 20%, Rendering 60%, Validation 10%`) only when weights are meaningful — don't invent weights just to make a percentage.

**Nested progress:** preserve meaningful hierarchy (`Flow → Process → Crew → Task → Tool`); don't present every nested event as independent top-level progress.

**Progress ≠ completion:** 100% steps completed doesn't mean success — final Process/Flow validation determines outcome.

---

# 10. Results & Termination

**Execution result** is separate from the event stream:

```yaml
execution_result:
  execution_id: ""
  status: ""
  outputs: []
  artifacts: []
  errors: []
  termination_reason: ""
```

**Final result vs final event:** `execution.completed` indicates lifecycle completion; the final result contains actual outputs, artifact references, validation status, termination info. Don't conflate.

**Completion statuses:** `SUCCESS, VALID_NEGATIVE_RESULT, FAILURE, REJECTED, CANCELLED, TIMEOUT, EXHAUSTED`.

**Successful negative result** (no matching records, no issues detected, no candidate, nothing to publish) is not necessarily failure — preserve that distinction in streaming and final results.

**Cancellation** is explicit: `RUNNING → CANCELLATION_REQUESTED → CANCELLED`. Define what happens to active Tasks/Tools, external operations, temp artifacts, checkpoints. Cancellation cannot always undo an external side effect (`publish → side effect → cancel`) — it must not falsely imply rollback; define compensation where required.

**Timeouts** at several levels (execution, process, task, tool, MCP, human gate) — not identical. A tool timeout doesn't imply the whole Flow failed; it may lead to retry, alternate Tool, Process failure, or human escalation per the failure plan.

**Retry events** should be visible and the count explicit (`process.failed → process.retrying → process.started`):

```yaml
retry:
  attempt: 2
  max_attempts: 3
```

**Retry ≠ iteration.** Retry re-attempts the same operation after execution failure (`Task → failure → retry`). Iteration deliberately repeats a Process for another cycle (`Generate → Evaluate → Revise → Evaluate`). Streaming exposes these differently.

---

# 11. Checkpoint & Recovery

**Checkpointing:** long runs create checkpoints (`Process A → Checkpoint → Process B → Checkpoint → Process C`); the stream may expose `checkpoint.created / restored` where useful.

**Recovery** is based on architecture-defined boundaries (`Execution → failure → restore checkpoint → resume Process B`). The stream communicates recovery without pretending the workflow restarted from the beginning.

**Resume** may retain execution_id, flow_id/version, completed outputs, artifact references, checkpoint, iteration counters, decisions.

---

# 12. Streaming & Artifacts / Context / Memory / Knowledge / State

**Large outputs** are not streamed as repeated raw content — use `artifact.created → artifact_reference`, and the consumer retrieves separately. **Small structured results** may be included directly (`process.completed → {status: NEEDS_REVISION, issue_count: 4}`) with a bounded payload. Large results go `Event → Artifact Reference → Artifact Store`, not `Event → 10 MB payload`.

**Streaming ≠ context** — don't accumulate execution history into Agent context (`every event → Agent context`). Events belong to observability unless a Process explicitly requires them.

**Streaming ≠ memory/knowledge/state:** events don't automatically become Memory, Knowledge (which must be intentionally created/validated/versioned), or the entire State representation. Some events cause state updates (`process.completed → state update`) but the event isn't the state.

---

# 13. Observability Model

A broader architecture: `Execution → {State, Events, Logs, Metrics, Traces, Artifacts, Final Result}`.

- **Events vs Logs:** Events are structured runtime facts for machine consumption (`process.completed`); Logs are diagnostics (`loaded configuration, parsed 47 records`).
- **Events vs Metrics:** Events give occurrences (`process.completed`); Metrics give aggregated measurements (`process_duration_seconds = 14.2`).
- **Events vs Traces:** a Trace represents execution relationships/timing (`Flow → Process → Crew → {Task A, Task B}`); streaming events may derive from or associate with the trace.

**Correlation:** all runtime info should be correlatable via `execution_id, flow_id, process_id, task_id, agent_id, crew_id, tool_id, mcp_id, artifact_id, event_id`.

**Correlation hierarchy** stays consistent with the architecture: `Execution → {Flow, Process → {Crew → {Agent, Task}, Tool/MCP}, Artifact}`.

---

# 14. Backpressure, Priority, Delivery

**Backpressure:** when producers outrun consumers, consider buffering, dropping low-value events, sampling, batching, flow control, consumer limits. Not every event needs equal delivery guarantees.

**Event priority:** `CRITICAL, HIGH, NORMAL, DEBUG` — `execution.failed` outranks `task.progress` when the system can't deliver everything.

**Delivery guarantees:** distinguish `best effort, at least once, exactly once`. Don't claim exactly-once unless infrastructure provides it.

**Duplicate events** (from reconnection) identified via `event_id, sequence, execution_id`.

**Missing events** (network/consumer failure, buffer overflow, restart) — execution correctness must not depend solely on a live stream. State and durable records remain authoritative.

---

# 15. Durable Execution Record & Stream-as-View

For important workflows, maintain a durable execution record: execution identity, current status, flow version, state, terminal result, artifact references, failure info, checkpoint info.

**Stream as a view:** `Durable Execution → {Current State, Event History, Stream View}`. The stream is a delivery mechanism over runtime info, not the sole source of truth.

---

# 16. Interactive Execution & Human Gates

Some workflows require human interaction (`Generate → Evaluate → Human Review → Approve/Revise/Reject`). Streaming exposes `human.approval_requested`; execution becomes `WAITING_FOR_HUMAN` until the decision arrives.

**Human gate event:**

```yaml
event:
  type: human.approval_requested
  payload:
    decision_required: true
    outcomes:
      - APPROVE
      - REVISE
      - REJECT
  artifact_references:
    - chapter_07_v3
```

Don't embed unnecessary sensitive information.

---

# 17. Execution API, Request, Response, Streaming

**Conceptual API:** `start_execution(), get_execution(), stream_execution(), cancel_execution(), resume_execution(), get_result(), get_artifacts()`.

**Request:**

```yaml
execution_request:
  flow_id: ""
  flow_version: ""
  inputs: {}
  options:
    streaming: false
    timeout_seconds: null
```

Validate inputs before entering the main workflow.

**Response:** sync returns `{execution_id, status, outputs, artifacts, termination_reason}`; async returns the execution id first.

**Streaming response:**

```yaml
stream_event:
  execution_id: ""
  sequence: 0
  type: ""
  timestamp: ""
  source: {}
  status: ""
  payload: {}
  artifacts: []
```

---

# 18. Input Validation, Preflight, Budgets

**Input validation:** `Request → Schema Validation → Architecture Compatibility → Authorization → Resource Validation → Execution`. Don't start expensive execution before basic validation succeeds.

**Preflight** verifies: Flow exists, Flow version exists, required inputs/artifacts exist, capabilities exist, permissions valid, config valid, resource constraints acceptable.

**Resource budgets:** tokens, LLM calls, tool calls, MCP calls, time, memory, storage, cost, iterations, retries — inherited from architecture where appropriate.

**Budget events:** `budget.warning, budget.exhausted` (don't expose sensitive exact values):

```yaml
event:
  type: budget.warning
  payload:
    resource: token
    remaining: 12000
```

---

# 19. Termination, Invariants, Simulation

**Termination** must be explicit; a terminal execution must not silently continue. Terminal states: `SUCCESS, VALID_NEGATIVE_RESULT, FAILURE, REJECTED, CANCELLED, TIMEOUT, EXHAUSTED`.

**Terminal event:**

```yaml
event:
  type: execution.completed
  status: SUCCESS
  payload:
    termination_reason: goal_satisfied
  artifact_references:
    - final_output
```

**Invariants:** terminal execution can't transition to RUNNING; cancelled can't silently resume; artifact references stay valid for recovery; iteration/retry counters can't exceed limits; unauthorized Tools can't execute; human gates can't be bypassed.

**Simulation / dry run** validates Flow behavior without expensive Agent execution — preflight transitions, references, inputs, capabilities, permissions, artifact deps, termination paths. **A dry run must not side-effect** (publish, delete, send, purchase, modify external data) unless explicitly requested; Tools should support dry-run mode where meaningful.

---

# 20. Security

**Execution security:** runtime events can leak credentials, tokens, private paths/prompts, sensitive user data, external responses, internal config. Streaming applies the same security model as execution.

**Prompt security:** don't stream system prompts, private Agent instructions, embedded secrets, or hidden reasoning just because debug is on.

**Tool result security:** Tool outputs (esp. MCP/external) may be untrusted — sanitize before streaming: `Tool Output → Validation/Sanitization → Public Event`.

**Execution cost:** streaming itself costs (serialization, network, storage, event processing, UI rendering). Don't emit high-frequency events without a meaningful consumer.

---

# 21. Sampling & Aggregation

**Event sampling:** for high-frequency ops, `1000 internal events → sample/aggregate → 10 public events`. Execution semantics unchanged.

**Event aggregation:** instead of 100 `tool.call` events, a consumer may get `tool_batch.completed {count: 100, failures: 2}` when individual events aren't useful.

---

# 22. Streaming & Token Efficiency / Context

Streaming doesn't inherently raise Agent token usage, but careless design can create unnecessary context. Avoid `runtime events → Agent context → repeated every Task`. Prefer `runtime events → observability`, injecting only selected execution info when required.

**Execution context:** at runtime a Process may need current inputs, relevant state, required Knowledge/Skills, selected Memory, previous outputs, Artifact references (assembled per `11-context-knowledge-memory.md`).

**Context updates:** a Process output becomes available downstream, but only relevant information enters downstream context (`Process A → Large Artifact → Reference → Process B → Relevant extraction → Context`).

---

# 23. Execution & Flow / Crew / Agent / Planning / Python / MCP / Artifacts

**Flow State** remains the authoritative execution-control representation: `Execution → {Flow State, Process Outputs, Artifact References, Events, Final Result}`.

**Crew:** `Flow → Process → Crew → Tasks/Agents → Crew Result → Process Output → Flow State`. Streaming may expose Crew progress, but the Crew is not the workflow controller.

**Agent:** execution stays bounded by its assigned Task/Process. Streaming Agent progress must not turn it into an autonomous controller unless Planning is part of the architecture.

**Planning** may produce dynamic actions; stream `plan.created, plan.action_started/completed, plan.replanned` but not private reasoning. Planning stays bounded by action/tool/time budget, permission boundary, termination condition.

**Python** handles deterministic runtime ops: state updates, validation, routing, artifact registration, serialization, event construction, budget checks. Don't put the entire engine in one giant Python function.

**MCP:** expose at appropriate abstraction (`mcp.requested, mcp.completed`), not raw protocol details; keep protocol info in debug diagnostics.

**Artifacts** maintain execution lineage:

```yaml
artifact:
  id: chapter_review_v3
  produced_by:
    execution_id: exec_001
    process_id: evaluate_chapter
```

**Execution lineage** reconstructs `Execution → Process → Task/Agent/Crew → Tool/MCP → Artifact` — valuable for debugging, audit, reproducibility, quality/cost/failure analysis.

---

# 24. Schemas: Execution Record, Event, Streaming Config, Validation

**Execution record:**

```yaml
execution:
  id: ""
  flow: { id: "", version: "" }
  status: ""
  start: { condition: "", inputs: {} }
  current: { process_id: "", state: {} }
  outputs:
    process_outputs: {}
    artifacts: []
  decisions: {}
  iterations: { counters: {}, limits: {} }
  failures: { current: null, history: [] }
  checkpoints: { last: "" }
  timing: { started_at: "", updated_at: "", completed_at: "" }
  termination: { status: "", reason: "" }
  observability: { event_count: 0 }
```

**Execution event:**

```yaml
execution_event:
  id: ""
  execution_id: ""
  sequence: 0
  timestamp: ""
  type: ""
  source: { type: "", id: "" }
  hierarchy:
    flow_id: ""
    process_id: ""
    crew_id: ""
    task_id: ""
    agent_id: ""
    tool_id: ""
    mcp_id: ""
  status: ""
  payload: {}
  artifacts: { references: [] }
  error: { category: "", retryable: false, message: "" }
  visibility: { public: true, level: "" }
```

**Streaming config:**

```yaml
streaming:
  enabled: false
  mode: ""
  event_level: ""
  include:
    execution: true
    flow: true
    process: true
    task: false
    agent: false
    tool: true
    mcp: true
    artifact: true
    human: true
    debug: false
  delivery:
    ordering: true
    replay: false
    buffering: true
  security:
    redact_sensitive: true
    expose_prompts: false
    expose_reasoning: false
```

**Execution validation:**

```yaml
execution_validation:
  execution_id: ""
  preflight:
    flow_valid: false
    version_valid: false
    inputs_valid: false
    artifacts_valid: false
    capabilities_available: false
    permissions_valid: false
    resources_available: false
  runtime:
    state_valid: false
    transitions_valid: false
    invariants_valid: false
    termination_reachable: false
  failures:
    current: null
    recoverable: false
    recovery_available: false
  outputs:
    valid: false
    artifacts_valid: false
  final:
    status: ""
    success: false
    termination_reason: ""
  findings:
    - id: ""
      severity: ""
      category: ""
      message: ""
      recommendation: ""
  approved: false
```

---

# 25. Recommended Runtime Sequence

`Execution Request → Preflight Validation → Create Execution → execution.started → Initialize State → Select Next Process → process.started → Execute Process → Validate Output → Create/Register Artifact → process.completed → Update State → Evaluate Transition → Next Process {Retry, Iteration, Parallel, Human Gate, Failure/Recovery, Terminal} → Final Validation → execution.completed → Final Result`.

---

# 26. Design Principle

The engine stays correct even if the stream is disabled, the client disconnects, events are delayed/duplicated, the UI crashes, or a consumer reconnects. **Streaming is not the execution engine.**

---

# 27. Anti-Patterns

1. **Stream as Workflow Controller** — `stream event → hidden workflow decision` unless explicitly architectural.
2. **Stream as State Store** — the live stream isn't the only source of current state.
3. **Stream as Artifact Store** — don't repeatedly stream large files; use references.
4. **Stream as Agent Memory** — don't auto-feed event history back into Agents.
5. **Exposing Private Reasoning** — no internal chain-of-thought as a stream feature.
6. **Fake Progress** — no precise percentages without a meaningful basis.
7. **One Event Per Internal Operation** — don't expose every low-level op.
8. **Stream Disconnect = Execution Failure** — a disconnected client isn't a failed execution.
9. **Restart on Reconnect** — don't restart execution because a consumer reconnects.
10. **Unbounded Event Payloads** — no large outputs in event payloads; use references.
11. **Raw Internal Events to Users** — apply security/visibility filtering.
12. **Retry Hidden as Progress** — a retry should be identifiable as a retry.
13. **Iteration Hidden as Retry** — a deliberate revision cycle isn't a failure retry.
14. **Cancellation Without Side-Effect Policy** — don't claim cancellation reverses external effects unless compensation is implemented.

---

# 28. Runtime Engineering Checklist

**Execution:** stable identifier · flow version recorded · current state explicit · terminal states defined · cancellation defined · timeout behavior defined · recovery boundaries defined.

**Events:** controlled types · execution correlation · ordering defined · duplicate handling defined · structured failure events · artifact references supported · sensitive info filtered.

**Streaming:** optional where appropriate · connection lifetime separate from execution · reconnection defined · backpressure considered · event volume controlled · public/internal events separated.

**Artifacts:** large outputs use references · lifecycle defined · versions preserved where required · provenance preserved · checkpoints retain required references.

**Security:** secrets never streamed · private prompts/reasoning not streamed · external data by trust level · Tool/MCP output sanitized.

**Efficiency:** event volume justified · payloads bounded · large content referenced · debug events disableable · streaming doesn't inflate Agent context.

---

# 29. Amsha Runtime Principle

```
FLOW:     "What should happen next?"
EXECUTION: "What is happening now?"
STATE:    "What is true now?"
EVENT:    "What happened?"
STREAM:   "How do I receive runtime information?"
ARTIFACT: "What meaningful data was produced?"
RESULT:   "What was the final outcome?"
```

The preferred architecture routes APPROVED ARCHITECTURE → FLOW → EXECUTION → {STATE, EVENTS, ARTIFACTS} (control / observation / data) → PROCESSES → {Python, Agent, Crew} → OUTPUT → VALIDATION → STATE UPDATE → TRANSITION → {Next Process, Iteration, Retry, Human Gate, Recovery, Terminal}.

> **Execution must remain correct independently of streaming. Streaming should expose meaningful runtime events and progress without becoming workflow control, state storage, artifact storage, Agent memory, or a substitute for durable execution.**