# Event Listeners

## Purpose

Defines the core rules for **Event Listeners** in Amsha.

> **Event Listeners observe runtime events and perform bounded side effects or reactions without becoming the workflow controller.**

Event Listeners are an **event-driven reaction mechanism**, not a replacement for Flow transitions.

---

# 1. Event Listener

An Event Listener waits for a specific runtime event and reacts when it occurs: `Execution → Event → Event Listener → Bounded Reaction`. Examples: `process.completed, artifact.created, execution.failed, human.approval_received`.

---

# 2. Listener vs Flow

**Flow** (`Process A → condition → Process B`) determines **what Process executes next**. **Event Listener** (`Process A completed → Listener → record metric/notify/audit`) determines **what should react to an event**. `Flow = execution control; Listener = event reaction`.

---

# 3. Listener Must Not Become Hidden Flow

Avoid `Event → Listener → hidden workflow → Process → another hidden workflow`. If the reaction determines the main workflow path, it belongs in the **Flow**.

---

# 4. Appropriate Listener Uses

logging, metrics, notifications, audit records, observability, artifact indexing, lightweight state-independent reactions, external monitoring, execution lifecycle hooks. Example: `execution.completed → Listener → send completion notification`.

---

# 5. Inappropriate Listener Uses

Do not use listeners to secretly implement: retry policy, main workflow transitions, complex iteration, business-critical branching, hidden orchestration, large semantic processing. These belong in the appropriate Process/Flow architecture.

---

# 6. Event Listener Lifecycle

`REGISTERED → WAITING → EVENT RECEIVED → FILTER → REACTION → COMPLETED`. Possible failures: `REACTION_FAILED, TIMEOUT, DISABLED`.

---

# 7. Listener Contract

A Listener should define: event source, event type, filter, reaction, inputs, permissions, failure behavior, idempotency, observability.

```yaml
listener:
  id: notify_on_completion
  event: { type: execution.completed }
  filter: { expression: "status == SUCCESS" }
  reaction: { type: notification, target: "" }
  idempotent: true
```

---

# 8. Event Filtering

React only to relevant events — prefer `filter: "process_id == evaluate_chapter"` over registering for every event and filtering in arbitrary application code.

---

# 9. Listener Scope

Explicit scope: `execution, flow, process, crew, task, artifact, system`. `execution.completed` may be execution-scoped; `artifact.created` artifact-scoped.

---

# 10. Listener Inputs

Receive only the info required for the reaction:

```yaml
listener:
  event: { type: artifact.created }
  input:
    required:
      - execution_id
      - artifact_id
      - artifact_version
```

Do not automatically pass complete execution state.

---

# 11. Listener Context

Listeners need much less context than Agents. A notification listener needs only `execution_id, status, artifact reference` — not the entire story bible, all Agent context, or complete execution history.

---

# 12. Listener Side Effects

A Listener may send notification, write audit record, update monitoring system, index artifact, emit external event. Side effects must be explicitly declared.

---

# 13. Listener Idempotency

Listeners may receive the same event more than once, so side-effecting listeners should be idempotent where possible (`event_42 → notification sent → delivered again → no duplicate`). Use `event_id, execution_id, sequence, deduplication key` as appropriate.

---

# 14. Listener Failure

A Listener failure normally stays separate from the primary workflow unless the architecture requires otherwise. `Process completed → Notification Listener → notification failed` should not automatically become `Process failed`.

---

# 15. Critical vs Non-Critical Listeners

**Non-critical** (metrics, logging, analytics, notification): failure generally must not block execution. **Critical** (e.g. artifact registration if downstream execution depends on it): only if the architecture explicitly requires the reaction for correctness; needs explicit failure and recovery behavior.

---

# 16. Listener Failure Policy

```yaml
listener:
  failure:
    critical: false
    retryable: true
    max_attempts: 3
    workflow_impact: none
```

Possible workflow impact: `none, pause, fail, escalate`. The choice must be architectural.

---

# 17. Listener Retry

Retry should be bounded, explicit, safe, idempotent where necessary: `Listener → failure → retry × 3 → give up`. Don't create infinite event-reaction loops.

---

# 18. Listener Loops

Dangerous pattern: `Event A → Listener → produces Event B → Listener → produces Event A` (infinite loop). Amsha should detect or prevent uncontrolled listener cycles.

---

# 19. Listener Triggering Another Process

Valid only when intentionally asynchronous and outside the main Flow (`artifact.created → Listener → index artifact`). If indexing is part of the required workflow, use `artifact.created → Flow transition → index_artifact Process`.

---

# 20. Listener vs Callback

Callback: "run this when this operation finishes" (attached to a specific operation). Listener: "react whenever this event occurs" (event-oriented). Amsha may support both, but don't confuse them conceptually.

---

# 21. Listener vs Hook

A Hook executes at a defined lifecycle boundary (`before_process, after_process`); a Listener reacts to an emitted Event (`process.completed`). A lifecycle Hook may produce an Event a Listener consumes.

---

# 22. Event Listener Architecture

`EXECUTION → EVENT → Event Dispatcher → {Listener A → Metrics, Listener B → Audit, Listener C → Notify}`. The dispatcher should not become a workflow engine.

---

# 23. Event Dispatcher

`Event → Dispatcher → Match listeners → Apply filters → Invoke reactions`. The Dispatcher handles event delivery, not business workflow design.

---

# 24. Listener Registration

Global, per Flow, per execution, per Process, or per artifact type. Scope should be explicit.

---

# 25. Listener Ordering / Parallelism

Independent listeners should not depend on execution order and can run in parallel (`process.completed → metrics, audit, notification`); failures isolated unless explicitly coupled. If ordering is business-critical, the behavior likely belongs in the Flow.

---

# 26. Listener Timeout

Listeners need bounded execution time (`listener.timeout_seconds: 30`). A monitoring/notification listener must not block an entire execution indefinitely.

---

# 27. Listener Permissions / Security

Use least privilege: Notification → notification permission; Audit → audit-write; Artifact Indexer → artifact-read + index-write. Don't grant broad permissions just because the listener receives runtime events. Events may contain sensitive info — listeners should not automatically get secrets, credentials, private prompts/reasoning, unnecessary user data. Control event visibility.

---

# 28. Listener and Artifacts / MCP

**Artifacts:** react to artifact events (`artifact.created → register index`); use the Artifact reference, not the complete artifact, unless required. **MCP:** may invoke an MCP capability when justified (`execution.completed → MCP notification service`), still following least privilege, timeout, retry limits, side-effect controls, output validation.

---

# 29. Listener and Python / Agent / Crew

**Python** is appropriate for deterministic reactions: update metric, write audit record, transform/validate event, update index. **Agent:** most listeners should not require an Agent — `artifact.created → Python → update index` beats `→ Agent →`, when no semantic judgment is required. **Crew:** almost never use a Crew directly as a simple event reaction; if an event needs substantial multi-specialist work, `Event → Flow/Process → Crew` is clearer than hiding the Crew inside a Listener.

---

# 30. Listener and Flow

`Flow: controls required workflow progression; Listener: reacts to emitted runtime events`. If removing the Listener would change the required workflow path, consider whether that behavior belongs in the Flow.

---

# 31. Event Listener Schema

```yaml
event_listener:
  id: ""
  name: ""
  scope: ""
  trigger:
    event_type: ""
    filter: ""
  input:
    required: []
    optional: []
  reaction:
    mechanism: ""
    purpose: ""
    target: ""
  execution:
    asynchronous: false
    timeout_seconds: null
  failure:
    critical: false
    retryable: false
    max_attempts: 0
    workflow_impact: ""
  side_effects:
    declared: []
    idempotent: null
  permissions:
    required: []
  observability:
    enabled: true
  traceability:
    requirements: []
    processes: []
```

**Listener validation:**

```yaml
event_listener_validation:
  listener_id: ""
  status: ""
  trigger: { event_defined: false, filter_valid: false }
  scope: { valid: false }
  reaction: { defined: false, bounded: false, necessary: false }
  execution: { timeout_defined: false, asynchronous: false }
  failure: { defined: false, retry_safe: false, workflow_impact_defined: false }
  security: { permissions_valid: false, least_privilege: false, sensitive_data_protected: false }
  side_effects: { declared: false, idempotent: null }
  loop_safety: { cycle_detected: false, bounded: true }
  findings:
    - id: ""
      severity: ""
      category: ""
      message: ""
      recommendation: ""
  decision: { status: "", action: "", rationale: "" }
  approved: false
```

---

# 32. Core Validation Questions

**Trigger:** Event clearly defined? filter necessary? scope correct? **Reaction:** bounded? actually event-driven? should it be part of the Flow? **Reliability:** failure behavior defined? retry bounded? reaction idempotent? **Security:** permissions minimal? sensitive event data protected? **Architecture:** does it create hidden orchestration? an event loop? duplicate an existing Flow Process?

---

# 33. Anti-Patterns

**Listener as Workflow Engine** — don't hide major workflow logic inside listeners. **Listener as Agent** — no Agent for deterministic event handling. **Listener as Storage** — don't turn listeners into an unstructured runtime database. **Unbounded Retry** — never retry forever. **Event Loop** — prevent listener-triggered cycles. **Unnecessary Context** — don't pass the entire execution context to every listener. **Unrestricted Permissions** — only what reactions require. **Criticality Ambiguity** — don't leave unclear whether listener failure affects the workflow.

---

# 34. Final Rules

1. Listeners react to Events; they do not replace Flow orchestration.
2. Every Listener has an explicit trigger.
3. Event filters should be explicit and bounded.
4. Listeners receive only required event data.
5. Large artifacts are passed by reference.
6. Listener side effects must be declared.
7. Side-effecting listeners should be idempotent where possible.
8. Listener retries must be bounded.
9. Listener failure must have explicit workflow impact.
10. Critical and non-critical listeners should be distinguished.
11. Listeners must not expose secrets or private reasoning.
12. Listeners should use deterministic mechanisms whenever sufficient.
13. Agents introduced only when semantic reasoning is actually required.
14. Major business workflow logic belongs in Processes and Flows.
15. Listener-triggered event cycles must be prevented or bounded.
16. Listener permissions must follow least privilege.
17. Listener execution should have timeout and observability where appropriate.
18. Execution correctness must not depend on non-critical listeners.

---

# 35. Final Principle

```
FLOW → Controls what happens next
EXECUTION → Runs the workflow
EVENT → Records what happened
LISTENER → Reacts to what happened
ARTIFACT → Stores meaningful output
OBSERVABILITY → Measures and exposes execution
```

> **Use Event Listeners for bounded reactions to runtime events. If the reaction determines the required workflow path, model it explicitly as a Process and Flow transition instead.**