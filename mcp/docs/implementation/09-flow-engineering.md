# Flow Engineering

## Purpose

Flow engineering builds an executable Flow from an already-validated Flow/State architecture. A Flow is the **execution-control layer**: it decides when a Process starts, what runs next, how decisions/branches/iterations/parallel work/human decisions/failure routing/recovery/state/termination are handled.

> **A Flow controls execution. It does not perform the professional work of the Processes it orchestrates.** `Process = meaningful work. Flow = execution control.`

Position: after Flow & State Planning and Architecture Validation, before Implementation. Full chain: `Problem → Goal/Boundary → Process Decomposition → Contracts → Validation → Flow/State Planning → Corner Cases/Failure Planning → Capability Selection → Architecture Validation → Process Engineering → Agent/Task Engineering → Crew Engineering → Flow Engineering → Implementation`. Derive the Flow from the already-approved Processes, Contracts, Transitions, State, Failure Policies, Human Gates, Capabilities, Termination Conditions.

## Core Definition

A Flow: **an executable control structure coordinating validated Processes, state transitions, decisions, iterations, parallelism, human gates, failure handling, and termination.** `Start → State → Process → Output → Decision → Transition → Next Process → ... → Terminal State`. It never redefines what a Process means.

## Flow vs Process vs Crew vs Agent vs Planning

- **Process** = what meaningful work happens. **Flow** = when/under what conditions it happens. E.g. Process "Evaluate Chapter" produces a result; Flow decides that `APPROVED → Continue`, `REVISE → Revise Chapter`.
- **Crew** = professional collaboration; **Flow** = orchestration. A Flow may call a Crew inside a Process step, but the Crew performs the work, the Flow controls the lifecycle.
- **Agent** should not become the primary workflow controller just because it can decide things — don't let an Agent "decide which Process to run, update state, handle retries, determine terminal state." Prefer explicit Flow structure (`Process A → Decision → Process B/C`). Agents make professional judgments; the Flow implements execution control.
- **Planning** is for unknown/dynamically-determined action sequences. If the structure is known (`A → B → C`), that's a Flow problem — don't replace an explicit Flow with Agent planning just because there are multiple steps.

## Flow as a State Machine

`State → Action/Process → Result → Transition Condition → Next State`. E.g. `START → DRAFTING → EVALUATING → {APPROVED→APPROVAL→SUCCESS | REVISE→REVISING→EVALUATING}`. Explicit states/transitions make execution understandable and testable.

## Engineering Principles

1. Flow derives from validated architecture. 2. Every transition has an explicit reason. 3. State is minimal. 4. Processes stay bounded. 5. Flow doesn't duplicate Process logic. 6. Decisions have explicit inputs. 7. Iterations are bounded. 8. Parallel execution has explicit dependencies. 9. Human gates are explicit. 10. Failure routes are explicit. 11. Terminal states are explicit. 12. Recovery boundaries are explicit. 13. Large artifacts are referenced, not copied into state. 14. Deterministic routing uses deterministic code. 15. Semantic decisions use semantic capability only when required. 16. Flow complexity must be justified by workflow requirements.

## State

Flow state = information required to control/continue execution (e.g. `chapter_id, current_process, revision_number, evaluation_status, approval_status`). Must be minimal, explicit, owned, traceable, serializable when recovery needs it, sufficient for continuation.

- **Ownership**: each field has a clear owner and source (`revision_number: owner=flow, source=revision_process, required_for=[revision_limit, termination]`). Avoid multiple components mutating the same field without contract.
- **Lifetime**: `process | flow | iteration | execution | checkpoint | persistent`. Don't retain info longer than required.
- **State ≠ Context**: project only the relevant fields into a Process/Task's prompt, not the entire Flow state.
- **State ≠ Memory**: state is current execution info (`revision_number = 3`); Memory is retained historical info across executions.
- **State ≠ Knowledge**: Knowledge is reference info (world rules); State is current execution info (approval status).

Also define **entry inputs** separately from Process inputs, Flow state, Knowledge, Memory, Artifacts — don't treat all available info as Flow input.

## Process Entry/Exit & Transitions

Each Process gets an explicit entry condition when needed (`entry_condition: "evaluation_status == NEEDS_REVISION"`) rather than a condition hidden in an Agent prompt, and explicit exit outcomes (`outcomes: [APPROVED, NEEDS_REVISION, REJECTED]`) the Flow routes on.

Every transition defines `source, target, type, condition, required state, reason`:
```yaml
transition: { from: evaluate_chapter, to: revise_chapter, type: conditional, condition: "evaluation_status == NEEDS_REVISION" }
```
Types: `sequential | conditional | parallel | merge | iteration | human_gate | failure | recovery | terminal`.

- **Sequential**: B always follows successful A, only when a real dependency exists.
- **Conditional**: route on an explicit decision value (`status: APPROVED→Publish, REVISE→Revise, REJECTED→Terminate`).
- **Deterministic routing**: if the value is structured (`status == APPROVED`), use deterministic Flow logic — don't ask an Agent "what should happen next?" when the architecture already defines the transition (improves determinism, cost, latency, testability, observability).
- **Semantic routing**: only when the decision genuinely requires professional judgment (e.g. "does this revision need structural or character rewriting?") — the judgment still becomes explicit Flow state before the transition fires.

## Parallelism & Merge

Parallel branches need: input availability, logical independence, safe state ownership, mergeable outputs, explicit failure behavior. Validate before parallelizing. Avoid two branches mutating the same state field — prefer each branch producing its own result (`result_a`, `result_b`) merged deterministically, or explicit synchronized ownership.

**Merge points** are required whenever downstream work depends on multiple branches; mechanism can be Python, deterministic aggregation, Agent, Crew, or Flow logic — pick the least powerful one sufficient.

## Iteration

Explicit trigger, condition, loop target, counter, max iterations, success condition, exhaustion behavior:
```yaml
iteration: { id: chapter_revision, loop_to: revise_chapter, condition: "status == NEEDS_REVISION", counter: revision_number, limit: 3 }
```
After the limit, `EXHAUSTED` must be an explicit outcome.

**Retry ≠ Iteration**: Retry recovers from execution failure ("Agent execution failed → retry"); Iteration deliberately repeats a workflow cycle ("Evaluation says NEEDS_REVISION → iteration"). Don't implement revision loops as retries.

## Human Gates

Explicit boundary with outcomes (`APPROVE | REVISE | REJECT | ESCALATE`), decision retained in state (`approval: { status, reviewer, notes }`) — never hidden inside an Agent. If a gate can go unresolved, define timeout behavior (`pending | timeout | escalate | cancel | resume`) — don't invent it ad hoc; return to failure planning if undefined.

## Failure, Recovery, Termination

Failures route explicitly: `Process A → FAILURE → {Retry | Recover | Escalate | Terminate}`, per the approved failure plan. Not every negative outcome is a failure — a `REJECTED` evaluation may legitimately route to Revision or Terminal rather than the technical-failure path.

**Recovery** happens at explicit checkpoints/restart boundaries (checkpoint after Analyze Source and after Generate Draft, so a failed Evaluate can resume from the last safe point instead of restarting everything). Checkpoint data holds only the minimum state to resume:
```yaml
checkpoint: { execution_id: "", process_id: "", state: { revision_number: 0, artifact_reference: "", evaluation_status: "" } }
```

**Cancellation** (for long-running Flows): define `CANCELLED | PARTIALLY_COMPLETED | CLEANUP_REQUIRED | SAFE_TO_RESUME`, accounting for external side effects — never leave the workflow in an ambiguous state.

**Termination**: minimum `SUCCESS | FAILURE`; commonly also `REJECTED | CANCELLED | EXHAUSTED | ESCALATED | PARTIAL`. Distinguish successful completion from other terminal outcomes explicitly:
```yaml
start: { condition: "", inputs: [] }
terminal_states: { success: "", failure: "", alternate: [] }
```

**State invariants** should be checked deterministically, e.g. `revision_number <= revision_limit`, or `approval_status == APPROVED ⇒ evaluation_status == PASS`. A violated invariant routes to an explicit failure/recovery path.

## Artifacts, Tools, MCP, Knowledge, Memory, Context

- **Artifacts**: store a reference, not the content (`artifacts: [{ name: chapter, reference: "artifacts/chapter_07.json", produced_by, consumed_by }]`).
- **Tools/MCP**: invoked by the Process/Agent that needs them; the Flow orchestrates the Process, it doesn't become a pile of Tool-specific code.
- **Knowledge/Memory**: not Flow state. The Flow picks the Process; the Process/Agent decides what Knowledge or historical Memory it needs. Don't inject the whole Knowledge system or Memory store via the Flow.
- **Context**: `Flow → Select Process → Build relevant Process context → Execute`. Don't use the Flow to blindly propagate all prior outputs.

## Flow Implementation Specification

```yaml
flow:
  id: chapter_production
  version: "1.0"
  purpose: "Generate, evaluate, revise, and approve a chapter."
  start: { condition: "chapter request is available", inputs: [chapter_requirements, story_context] }
  state:
    fields:
      - { name: current_process, owner: flow, lifetime: execution }
      - { name: revision_number, owner: flow, lifetime: execution }
      - { name: evaluation_status, owner: evaluation_process, lifetime: execution }
  processes:
    - { id: generate_chapter, entry_condition: "start" }
    - { id: evaluate_chapter, entry_condition: "chapter exists" }
    - { id: revise_chapter, entry_condition: "evaluation_status == NEEDS_REVISION" }
  transitions:
    - { from: generate_chapter, to: evaluate_chapter, type: sequential }
    - { from: evaluate_chapter, to: revise_chapter, type: conditional, condition: "evaluation_status == NEEDS_REVISION" }
    - { from: evaluate_chapter, to: approval, type: conditional, condition: "evaluation_status == APPROVED" }
    - { from: revise_chapter, to: evaluate_chapter, type: iteration }
  iterations: [{ id: revision_loop, counter: revision_number, limit: 3 }]
  human_gates: [{ id: final_approval, outcomes: [APPROVE, REVISE, REJECT] }]
  terminal_states: { success: "chapter approved", failure: "workflow failed", alternate: [revision_limit_exhausted, human_rejected] }
  checkpoints: [{ after_process: generate_chapter, reason: "expensive artifact generation" }]
  observability: { metrics: [duration, outcome, retries, revisions] }
```

## Flow State & Transition Schemas

```yaml
flow_state:
  execution_id: ""
  flow_id: ""
  flow_version: ""
  current_process: ""
  status: ""
  inputs: {}
  process_outputs: {}
  decisions: {}
  iteration: { counters: {}, limits: {} }
  approvals: { status: "", reviewer: "", decision: "", notes: [] }
  artifacts: { references: [] }
  failures: { current: null, history: [] }
  checkpoints: { last: "" }
  timestamps: { started_at: "", updated_at: "" }
  termination: { status: "", reason: "" }
```
```yaml
transition:
  id: "" 
  from: "" 
  to: "" 
  type: ""
  condition: { expression: "", source: "" }
  required_state: []
  priority: null
  failure_behavior: ""
  rationale: ""
  traceability: { process: "", requirement: "" }
```
Implement only the fields the Flow actually needs; explicit transition IDs improve traceability.

---

## Checklist

**Architecture**: derives from validated Flow/State architecture · Process boundaries preserved · no silent Process add/remove · capabilities architecture-authorized.
**Start/End**: start condition and required inputs explicit · success/failure/alternate terminal states explicit.
**State**: fields necessary, owned, lifetime-defined, minimal · not confused with Context/Knowledge/Memory.
**Processes**: every executable Process represented · entry/exit conditions explicit · outputs correctly propagated · large artifacts referenced.
**Transitions**: dependencies and conditions explicit · deterministic routing uses deterministic logic, semantic routing uses semantic capability only where needed · no unreachable Process, no unintended transition.
**Parallelism**: branches genuinely independent · state ownership and side effects safe · merge points explicit · partial-failure behavior defined.
**Iteration**: condition/target/counter/limit explicit · exhaustion behavior defined · not confused with retry.
**Human Gates**: decisions and outcomes explicit · state retained · timeout/escalation defined where required.
**Failure/Recovery**: transitions explicit · retry bounded and safe · recovery boundaries explicit · checkpoints where required · cancellation defined where required.
**Capabilities**: Agent execution stays Process-scoped · Crew stays collaboration-scoped · Tools/MCP appropriately scoped · Knowledge/Memory not treated as state · Planning not used where Flow suffices.
**Operations**: observability sufficient · execution IDs traceable · outcomes and failures recorded · runtime feasibility acceptable.

## Anti-Patterns

- **God Flow** — Flow contains prompt construction, DB ops, audio processing, file parsing, model calls, business logic instead of orchestrating.
- **Hidden workflow** — Agent internally decides generate/review/revise/publish instead of using explicit Flow Processes.
- **Implicit transitions** — `if something seems wrong: do something else` instead of explicit testable transitions.
- **Unbounded loop** — `while not good: revise()` with no limit/terminal condition.
- **State dumping** — every output copied into global Flow state (memory/serialization/recovery cost).
- **Context dumping** — every Process gets the entire Flow state.
- **LLM routing for deterministic decisions** — an Agent evaluating `status == APPROVED`.
- **Flow as a Crew** — multiple professional Agents placed in a Flow without real collaboration.
- **Crew as a Flow** — entire workflow lifecycle hidden inside a Crew.
- **Capability creep** — Memory/Planning/MCP/Tools/Reasoning added without architectural justification.

## Complexity, Observability, Metrics, Versioning

**Complexity is acceptable** when the underlying workflow is genuinely complex (many states/transitions/branches/parallel groups/iterations/gates/routes/checkpoints/state fields/external deps); it's a problem when it exists because implementation boundaries were poorly designed. Prefer explicit, deterministic, bounded, traceable, minimal over implicit, autonomous, unbounded, highly dynamic, over-generalized — when both satisfy the architecture.

**Observability** minimum: execution ID, flow ID/version, current Process, state transition, Process outcome, decision, iteration/retry counts, failure, terminal state:
```yaml
event: { execution_id: "", flow_id: chapter_production, event: PROCESS_COMPLETED, process_id: evaluate_chapter, outcome: NEEDS_REVISION, next_process: revise_chapter }
```

**Metrics**: execution success/failure rate, terminal outcome distribution, avg/P95/P99 duration, transition counts, branch frequency, iteration/retry counts, checkpoint recovery rate, human approval/rejection rate, token usage, LLM cost, Tool/MCP usage.

**Traceability**: `Requirement → Process → Transition → State → Capability → Outcome`.

**Versioning**: version every Flow; changes to transitions/state/Process mapping/iteration limits/human gates/failure handling/terminal conditions trigger revalidation. Identify all potentially-affected components (Flow, State, Failure handling, Process completion, Checkpointing, Observability) rather than assuming isolation.

**Validation pipeline**: `Architecture → Flow Specification → Generated Flow → Structural → Transition → State → Termination → Failure Validation → Execution Simulation`. Simulate representative scenarios (normal success, revision, revision exhaustion, human rejection) before expensive Agent execution — this exposes unreachable states and incorrect transitions early. Test invariants deterministically (`revision_number <= revision_limit`; `APPROVAL cannot occur before evaluation`; `PUBLISH cannot occur unless approval valid`; `SUCCESS cannot occur without required output`; `RETRY count cannot exceed retry limit`).

---

## Final Model & Principle

```text
Validated Flow Architecture → Identify States → Map Processes → Define Process Entry/Exit → Define Transitions
  → Define Decisions → Define Parallel Groups → Define Iterations → Define Human Gates
  → Define Failure/Recovery Routes → Define Checkpoints → Define Terminal States → Define Minimal State
  → Map Capabilities → Generate Flow Specification → Generate Implementation → Simulate → Validate
```

The Flow is the **control plane**. It answers "what happens next, why, on what state, and when does execution terminate?" — never "how does a professional Agent perform the underlying work?" (that belongs to Process/Agent/Task/Crew/Tool).

> Keep workflow control explicit in the Flow, meaningful work inside Processes, professional capability inside Agents, bounded operations inside Tasks, collaboration inside Crews, and deterministic control logic in Python whenever sufficient. A Flow should be no more autonomous, stateful, or complex than the validated workflow actually requires.
