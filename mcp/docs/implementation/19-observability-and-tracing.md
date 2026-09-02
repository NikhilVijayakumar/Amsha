# Observability and Tracing

## Purpose

Defines the core rules for **Observability, Metrics, Logs, Events, and Tracing** in Amsha.

> **Observability makes execution understandable, measurable, and diagnosable without changing the workflow's behavior.**

Observability should answer: What happened? Where? How long? What did it cost? Did it succeed? Why did it fail? What produced the result?

---

# 1. Observability

The ability to understand runtime behavior from recorded execution information. Amsha should observe Flow, Process, Crew, Task, Agent, Tool, MCP, Artifact, Human Gate, Execution — but only at a level that provides useful information.

---

# 2. Core Observability Layers

`Events → what happened · Logs → diagnostic details · Metrics → numerical measurements · Traces → execution relationships and timing · Artifacts → produced data · State → current execution condition`. Complementary, not interchangeable.

---

# 3. Observability Must Not Control Execution

Observability should be `execution → observation`, not `execution → observation → hidden workflow decision`. Business-critical decisions belong in Flow/Process logic.

---

# 4. Events, Logs

**Events** describe meaningful runtime occurrences (`execution.started, process.started/completed/failed, task.completed, tool.called, artifact.created, human.approval_received, execution.completed`) — detailed in `18-event-listeners.md`. **Logs** provide diagnostics (`loading configuration, artifact validation failed, retrying external request, MCP connection timeout`) and may contain more implementation detail than public Events, but sensitive info must still be protected.

---

# 5. Metrics Inventory

**Core:** execution_duration, process_duration, task_duration, retry_count, failure_count, token_usage, llm_call_count, tool_call_count, mcp_call_count, artifact_count.

**Execution (minimum):** duration, outcome, failure count, retry count; for LLM: calls, tokens, model, latency. **Process:** duration, success/failure rate, retry/iteration count, validation failures (identify problem boundaries). **Agent:** invocation count, latency, tokens, Task success rate, tool usage, failure rate (is the Agent useful and scoped?). **Task:** execution count, duration, success/failure rate, retry count, validation failure rate, tokens. **Crew:** duration, Agent/Task count, LLM calls, tokens, collaboration/synthesis duration, failure rate (detect unnecessary complexity). **Tool:** call count, latency, failure/timeout/retry count, cost (reveal runtime-dominating external deps). **MCP:** request count, latency, failure/timeout/retry count, external cost — associated with the calling Process/Task. **Artifact:** count, creation/validation duration, size, storage usage, version count. Avoid metrics with no operational value.

**Token metrics** (critical for Amsha): input/output/total tokens, context tokens, reasoning tokens where available — used to find unnecessary context, oversized prompts, unnecessary Agents/Tasks, excessive iterations. **Cost:** LLM, Tool, MCP, storage, execution cost — associated with the appropriate Process/Task/Agent. **Latency** at meaningful boundaries (execution, process, task, agent, tool, MCP, human gate) — identifies the actual bottleneck. **Human gate:** approval wait time, approval/revision/rejection/timeout rate (reveal human-interaction bottlenecks).

---

# 6. Failure, Retry, Iteration Metrics

**Failure:** preserve categories — `PROCESS_FAILURE, VALIDATION_FAILURE, TOOL_FAILURE, MCP_FAILURE, TIMEOUT, PERMISSION_FAILURE, HUMAN_TIMEOUT, RESOURCE_EXHAUSTION`. A single generic `failure_count` is often insufficient. **Retry:** track `retry_count, attempt_number, retry_reason, retry_success, retry_exhaustion` — distinguishes temporary infrastructure problems from systematic architectural problems. **Iteration:** track intentional workflow iterations separately from retries — `revision_count = 2, retry_count = 0` tells a different story than `revision_count = 0, retry_count = 2`.

---

# 7. Tracing

A Trace represents relationship/timing between runtime operations (`Execution → Flow → Process → Crew → {Task A → Tool, Task B}`). Answers: "What happened inside this execution, and how were the operations related?" **Trace vs Event:** an Event (`process.completed`) describes an occurrence; a Trace shows operations and their timing/relationships.

**Trace identity** — associated with an execution:

```yaml
trace:
  trace_id: ""
  execution_id: ""
  flow_id: ""
  flow_version: ""
```

Nested operations share the same trace. **Spans:** meaningful execution units in a hierarchy (`Execution Span → Process Span → Crew Span → Task Span → Tool/MCP Span`); not every internal operation needs a span. **Span boundaries:** Flow, Process, Crew, Task execution; Tool/MCP/Artifact invocation. Avoid spans for trivial internal functions unless needed for diagnostics.

**Correlation IDs:** `execution_id, trace_id, span_id, flow_id, process_id, crew_id, task_id, agent_id, tool_id, mcp_id, artifact_id` — reconstructs execution lineage.

---

# 8. Provenance, Versions, Reproducibility

**Artifacts:** observability should reference important artifacts (`trace.artifact: {id, role}`); don't embed large artifact contents into logs/traces. **Provenance:** `Execution → Process → Agent/Crew/Tool → Artifact` answers "Which execution produced this artifact?" **Architecture version:** record `flow_id, flow_version` for comparing executions across changes. **Model version:** record provider/name/version to explain quality/latency/cost changes. **Configuration version:** only versions relevant to reproducibility (Agent/Task/Skill/Knowledge/Tool/MCP/Flow versions). **Reproducibility:** preserve what architecture ran, what inputs/resources/capabilities were used, what outputs were produced. Exact reproducibility may be impossible for nondeterministic LLM execution, but provenance should still be preserved.

---

# 9. Runtime vs Quality Metrics

**Runtime:** latency, tokens, cost, retries, failures. **Quality:** correctness, coherence, consistency, human approval, evaluation score. Preserve the distinction. Semantic quality metrics (narrative coherence, character consistency, factual accuracy, image/audio quality) are **evaluation metrics**, not ordinary runtime metrics — from deterministic validation, Agent evaluation, or human review.

**Observability and evaluation:** `Execution → Runtime Metrics + Output → Quality Evaluation → Evaluation Metrics`. Runtime success does not imply output quality. **Observability and validation:** validation events should be observable (`process.completed → output.validation_started → output.validation_failed`) to tell whether failures originate from execution or output quality.

---

# 10. Schemas

**Observability:**

```yaml
observability:
  execution_id: ""
  trace_id: ""
  outcome: { status: "", duration_ms: 0 }
  metrics:
    llm_calls: 0
    tool_calls: 0
    mcp_calls: 0
    retries: 0
    iterations: 0
  resources:
    input_tokens: 0
    output_tokens: 0
    total_tokens: 0
    estimated_cost: null
  quality:
    validation_status: ""
    human_approval: null
  artifacts:
    produced: []
    consumed: []
  failures:
    count: 0
    categories: []
  architecture:
    flow_id: ""
    flow_version: ""
```

**Trace:**

```yaml
trace:
  trace_id: ""
  execution_id: ""
  spans:
    - span_id: ""
      parent_span_id: ""
      component_type: ""
      component_id: ""
      operation: ""
      started_at: ""
      ended_at: ""
      status: ""
      attributes: {}
```

**Observability validation:**

```yaml
observability_validation:
  execution_id: ""
  correlation: { execution_id: true, trace_id: true, component_ids: true }
  coverage:
    execution: true
    process: true
    task: false
    agent: false
    crew: false
    tools: true
    mcp: true
    artifacts: true
  metrics:
    duration: true
    failures: true
    retries: true
    tokens: true
    cost: false
  provenance: { artifacts: true, architecture_version: true }
  security: { secrets_redacted: true, private_reasoning_excluded: true }
  efficiency: { event_volume: "", storage_cost: "" }
  findings: []
  approved: false
```

---

# 11. Minimality, Debug vs Production, Overhead, Sampling

**Minimality:** don't instrument everything by default. Ask "Will this help diagnose, measure, validate, or improve the architecture?" If not, don't collect it. **Debug vs Production:** production collects execution status, important events, core metrics, errors, trace relationships, artifact provenance; debug additionally collects detailed Tool timing, Task diagnostics, config metadata, extra events. Sensitive info stays protected in both. **Overhead:** observability consumes CPU, storage, network, processing — justify high-frequency instrumentation. **Sampling:** for high-volume systems, sample detailed traces while retaining important failures and terminal executions (`Normal execution → sampled trace; Failed execution → full diagnostic trace`). Sampling policy is implementation-specific.

---

# 12. Security

**Logs and sensitive data:** never log API keys, passwords, auth tokens, private credentials. Avoid logging private user data, private prompts, sensitive artifact contents. **LLM prompt observability:** treat carefully — possible metadata (prompt size, token count, template/version id, Knowledge/Skill versions) gives diagnostics without storing complete private prompts. **Reasoning observability:** don't treat private model reasoning as an ordinary payload; record useful structured info (decision, confidence, selected action, evidence references, validation result) when the architecture requires it.

---

# 13. Trace Example

```
execution: exec_001
├── flow: chapter_production
├── process: generate_chapter
│   └── task: write_chapter
│       └── agent: narrative_writer
├── process: evaluate_chapter
│   └── crew: chapter_quality_review
│       ├── task: evaluate_narrative
│       ├── task: evaluate_character
│       └── task: evaluate_continuity
└── process: approval
    └── human_gate
```

A useful execution map without unnecessary internal details.

---

# 14. Anti-Patterns

**Observability as Workflow Control** — don't let metrics/tracing secretly control the Flow. **Log Everything** — noise, cost, security risk. **Store Entire Artifacts in Logs** — use references. **Store Private Reasoning** — don't expose hidden model reasoning. **No Correlation IDs** — hard to debug distributed execution. **One Generic Failure Metric** — preserve failure categories. **Runtime Success = Quality Success** — they differ. **No Architecture Version** — unreliable historical comparison. **Instrument Every Function** — observe meaningful boundaries.

---

# 15. Core Checklist

- [ ] Execution can be identified.
- [ ] Flow and architecture versions are recorded.
- [ ] Important Process boundaries are observable.
- [ ] Failures are categorized.
- [ ] Retries and iterations are distinguishable.
- [ ] Important Tool/MCP calls are measurable.
- [ ] Important Artifacts have provenance.
- [ ] Runtime and quality metrics are separated.
- [ ] Token/cost measurements exist where useful.
- [ ] Trace relationships are reconstructable.
- [ ] Sensitive data is protected.
- [ ] Private reasoning is not exposed.
- [ ] Observability overhead is reasonable.
- [ ] Observability does not become hidden workflow control.

---

# 16. Final Principle

```
STATE → what is true now
EVENT → what happened
LOG → diagnostic detail
METRIC → numerical measurement
TRACE → how execution components relate
ARTIFACT → what data was produced
EVALUATION → how good the result was
```

> **Observe meaningful architectural boundaries, correlate runtime information to executions and artifacts, measure both operational cost and outcome quality where useful, and keep observability independent from workflow control.**