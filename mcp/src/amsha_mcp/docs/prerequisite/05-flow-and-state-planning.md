# Amsha Prerequisite: Flow and State Planning

## Purpose

The Process architecture defines **what meaningful work must happen**. This document defines how those approved Processes become an **executable workflow structure** by determining: execution order, transitions, conditions, iterations, parallel execution, state requirements, outputs that must be retained, information required between Processes, human approval gates, runtime control boundaries, and recovery-relevant state.

The objective is to design the workflow **before implementing it with CrewAI Flow, Python, Crews, Agents, Tasks, Tools, Knowledge, Memory, or MCP**. The output is a **Flow and State Plan**.

---

# 1. Position in the Architecture Process

This stage assumes the Process architecture is validated. The question changes from "What work must happen?" to "How must that approved work move through the workflow, and what state must exist to control it?". Still avoid deciding which Agent/Crew/Task implements a Process, which LLM, which Tool, which MCP server — those belong later.

**Prerequisite chain:** See `00-problem-definition.md` §2.

---

# 2. Flow as Execution Architecture

A Flow is the execution structure that connects approved Processes: `Approved Process Architecture → Flow & State Plan → Executable Workflow`. It determines what executes first/next, what conditions control transitions, what information moves between Processes, what state is retained, when execution can stop/resume, and where it can branch or iterate.

---

# 3. Process vs Flow

Process and Flow are related but different abstractions. **Process** describes meaningful work (Analyze Source, Generate Draft, Evaluate Draft, Approve Draft). **Flow** describes execution control (Analyze → Generate → Evaluate → Pass? NO→Improve→Evaluate / YES→Approve).

> **Process defines work. Flow defines how work is orchestrated.**

A Process should remain understandable without knowing its eventual Flow implementation.

---

# 4. Flow Planning Inputs

Flow planning consumes: start condition, end condition, Process IDs, Process dependencies, inputs/outputs, conditional relationships, iteration requirements, parallel relationships, human approval boundaries, external dependencies, and termination conditions — derived from the validated Process architecture and its contracts.

---

# 5. Flow Planning Principles

- **5.1 Preserve Process Architecture** — do not redesign Processes to fit a preferred Flow implementation (`Process Architecture → Flow Architecture`, not `Preferred API → Force Processes into it`).
- **5.2 Make Control Explicit** — bad: `` Process A then somehow Process B ``, good: `A → condition → B`.
- **5.3 Keep State Minimal** — retain only state required to continue, decide, satisfy downstream contracts, support recovery and observability, or preserve required history. Do not store every intermediate value merely because it exists.
- **5.4 Separate State from Knowledge** — current execution state (current_process, draft_id, evaluation_status) is not domain knowledge (story rules, character history, world rules). Knowledge answers "What is known?"; state answers "Where is the workflow and what has happened?".

---

# 6. What Is Flow State?

Flow state represents the information required to control the current execution (see the full schema in §14). The exact structure depends on the workflow. The key principle:

> State should represent the execution context necessary to continue and reason about the workflow.

---

# 7. State Categories

State categories: Input, Execution, Process, Decision, Output, Approval, Iteration, Error/Recovery.

- **Input State** — supplied when execution begins (`input: {source_document, chapter_number}`).
- **Execution State** — current workflow position (`execution: {current_process, status}`).
- **Process State** — information produced/required by Processes (`process: {generate_chapter: {status, output_ref}}`).
- **Decision State** — results controlling transitions (`decisions: {evaluation_passed: true}`).
- **Output State** — final/intermediate outputs that must remain available.
- **Approval State** — human decisions (`approval: {status: "approved"}`).
- **Iteration State** — controls loops (`iteration: {revision_count, max_revisions}`).
- **Error/Recovery State** — information needed to handle failures; detailed design belongs to `06-corner-cases-and-failure-planning.md`, but identify recovery-relevant state here.

---

# 8. State Should Follow Data Dependencies

State should be derived from actual Process contracts. If `P1 Output → P2 Input` and P2 executes later, the required P1 output must remain accessible. But a Process output that is never consumed and not needed for final output, decisions, recovery, or observability generally does not need to become persistent Flow state.

---

# 9. State Is Not a Dump of Everything

A common mistake is putting every Process output into Flow state. This creates large state objects, unnecessary serialization, token overhead, unclear ownership, stale information, harder recovery, and difficult debugging. Instead:

> Persist the minimum sufficient state required by the workflow.

---

# 10. State Ownership

Every important state field should have a logical owner: source_analysis → P1, chapter_requirements → P2, draft → P3, evaluation → P4, approval → Human Review. Ownership prevents unrelated Processes from arbitrarily modifying shared state. A useful rule:

> A Process should primarily produce or update state associated with its own contract.

---

# 11. Immutable vs Mutable State

Not all state should be freely modified. Prefer immutable or append-only treatment for historical facts — inputs (`source_document`) should generally not change, and decisions may be retained as execution history. Mutable state is appropriate for `current_process`/`status`. Distinguish **Current State** vs **Execution History** when both are needed.

---

# 12. State vs Memory

Flow state and Memory are not interchangeable. **Flow State** answers "What is happening in this execution?" (current_process, draft, evaluation, approval_status, iteration_count). **Memory** answers "What should be retained for future context or future executions?" (previously approved preferences, historical interactions, learned information, past decisions). A Flow should not use Memory merely to pass information from Process A to Process B — that is normally state or Process output context.

---

# 13. State vs Knowledge

Knowledge represents relatively stable reference information (Story Bible, Character Definitions, World Rules, Production Guidelines); State represents current execution information (Current Chapter, Current Draft, Evaluation Result, Revision Count, Approval Status).

```text
Knowledge = reference
State     = execution
Memory    = retained history
```

---

# 14. Flow State Schema

A conceptual Flow state may look like:

```yaml
flow_state:
  workflow:
    id: ""
    status: ""
    current_process: ""

  input:
    required: {}
    optional: {}

  process_outputs: {}

  decisions: {}

  approvals: {}

  iteration:
    counters: {}
    limits: {}

  execution:
    started_at: ""
    updated_at: ""

  recovery:
    checkpoint: ""
    resumable: false

  errors: []
```

This is a planning model, not a mandatory implementation schema.

The implementation may use a different structure as long as the required semantics are preserved.

---

# 15. Transition Planning

Every Process relationship should become an explicit transition rule. `P1 → P2` means "when P1 completes successfully, execute P2". `P2 → evaluation → pass/P3, fail/P4` means the Flow must evaluate a defined decision value. The architecture should not depend on implicit interpretation.

# 16. Transition Types

Recommended conceptual transition types: `SEQUENTIAL`, `CONDITIONAL`, `PARALLEL`, `ITERATIVE`, `HUMAN_GATE`, `TERMINAL`, `FAILURE`.

- **Sequential** — `A → B`.
- **Conditional** — `A → condition → B / C`.
- **Parallel** — `A → [B, C]`.
- **Iterative** — `` A → B → condition ↖ loop back ``.
- **Human Gate** — `A → Human Decision → B / C`.
- **Terminal** — `A → END`.
- **Failure** — `A → FAILURE HANDLER` (detailed failure paths are designed in the next stage).

---

# 17. Sequential Flow

Use sequential execution when a genuine dependency exists (`P2 requires P1`, `P3 requires P2`). Do not create sequential execution merely because the Processes were listed in that order.

# 18. Parallel Flow

Plan parallel execution when Processes are independent: both require only P1's output, neither modifies shared state required by the other, outputs can be safely combined, and downstream P4 consumes both. Parallelism is based on contract and state independence.

---

# 19. Parallel State Considerations

Parallel Processes introduce state ownership concerns. Bad: P2 and P3 both modify the same field when the final value depends on order. Better: `P2 → result_a`, `P3 → result_b`, merged by an explicit `P4 Merge` Process or Flow operation. This avoids hidden race conditions and ambiguous state ownership.

---

# 20. Conditional Flow

A conditional transition must have an explicit decision source. E.g. `Evaluate → score >= threshold? YES→Approve / NO→Improve`. Define:

```yaml
decision:
  id: evaluation_passed
  source: evaluation
  condition: "evaluation meets acceptance criteria"
  true_transition: approve
  false_transition: improve
```

The implementation may later use Python, deterministic logic, or another mechanism, but the architectural condition must exist independently of implementation.

# 21. Iterative Flow

Iterations should be represented explicitly. The Flow plan must define: iteration trigger, success condition, retry/revision transition, iteration counter, maximum/bounded behavior, and terminal behavior if the limit is reached.

```yaml
iteration:
  id: chapter_revision
  condition: "evaluation_failed"
  loop_to: generate_chapter
  counter: revision_count
  limit: 3
```

---

# 22. Human-Gated Flow

Human approval should be a first-class transition: `Generate → Validate → Human Review → Decision {APPROVE→END, REVISE→Improve, REJECT→END}`. The Flow must retain the decision because downstream execution depends on it:

```yaml
approval:
  status: pending
  reviewer_decision: ""
```

After review:

```yaml
approval:
  status: completed
  reviewer_decision: "approved"
```

---

# 23. Flow Start

The Flow plan must define exactly what starts execution. Possible triggers: user request, file arrival, API request, scheduled/external event, manual execution, or another workflow. Record the trigger semantically (`start: {condition: "validated chapter request received"}`); do not decide the technical trigger implementation prematurely.

# 24. Flow End

The Flow must define explicit terminal states — `SUCCESS`, `REJECTED`, `FAILED`, `CANCELLED`, `ABORTED` — not all required, but the end state must be unambiguous:

```yaml
termination:
  success: "approved chapter produced"
  rejection: "human rejects chapter"
  failure: "workflow cannot produce valid chapter"
```

# 25. State and Termination

Termination conditions should be expressible using state — `approval.status == "approved"`, or a conjunction like `evaluation.status == "passed" AND artifact.exists == true AND approval.status == "approved"`. The Flow should not terminate simply because the final Process returned; execution completion and goal completion are different concepts.

---

# 26. State and Human Review

When a human gate pauses execution, the Flow must preserve sufficient state to resume:

```yaml
flow_state:
  status: waiting_for_human
  current_process: human_review
  artifact_ref: ""
  validation_result: {}
```

After approval the workflow continues from `WAITING_FOR_HUMAN → APPROVED → Continue`; it should not need to reconstruct the previous execution merely to continue.

# 27. Flow Checkpoints

A checkpoint is a recoverable representation of execution state placed between Processes. Good candidates: after expensive Processes, after major artifact generation, before/after human approval, before iteration, after major external operations, and at meaningful workflow boundaries. Detailed checkpoint/recovery design belongs to implementation engineering, but the Flow plan should identify where state continuity matters.

---

# 28. State Lifetime

Not every state value needs the same lifetime. Conceptual categories: **Ephemeral** (one operation), **Process-scoped** (while a Process executes), **Flow-scoped** (multiple Processes in one execution), **Persistent** (survives the current execution), **Historical** (audit/analysis/future context). State planning should assign the minimum necessary lifetime.

# 29. State Size and Token Efficiency

State can be a major source of unnecessary token consumption; avoid repeatedly passing large state objects to every LLM operation. Instead: `Flow State → Relevant Context Selection → Process`. A Process should receive only the state relevant to its contract — not the entire Flow state. This matters to Amsha because:

> **Execution state and LLM context are not necessarily the same object.**

# 30. State and Context

Flow state determines what information exists; context selection determines what is provided to a specific Process or Agent. A generation Process may need source_analysis/character_data/current_requirements but not execution_metadata, unrelated evaluations, or approval history. Therefore `State ≠ Context` — context is a projection of state and other relevant information.

---

# 31. Flow State and External Systems

A Flow may interact with external systems (Python, Crew, External API, ComfyUI, Unreal Engine). Track the logical result of external operations (`external_operation: {status, operation_id, artifact_ref}`); do not store entire external-system responses in state — prefer references where possible.

# 32. Artifacts vs State

Large outputs should generally not be embedded directly into Flow state when a reference suffices. Instead of embedding `generated_video` content, store `generated_video: {artifact_ref: "video-001"}`. State controls the workflow; artifacts contain large outputs. This separation reduces memory, token transfer, and speeds checkpointing, recovery, and observability.

---

# 33. Flow and Python

Python may be used for deterministic orchestration logic (validate schema, calculate score, select branch, merge results, transform data, check conditions, manage state). Avoid one giant Python function implementing the entire workflow; prefer a Flow interleaving scoped Python steps with Processes. The Flow remains the orchestration layer.

# 34. Flow and Crew

A Process may later be implemented by a Crew when collaboration among multiple professional roles is justified. The Flow should not care about internal Crew composition at this stage — it only needs `Input → Process → Output`, preserving architectural separation.

# 35. Flow and Agent/Task

Likewise, a Process may later be implemented with `Agent → Task` or `Agent → multiple Tasks`. The Process contract remains the stable boundary, preventing implementation details from leaking into the prerequisite architecture.

---

# 36. Flow State Ownership Model

Processes should interact with state through defined contracts (`Flow State → Process A/B/C → output_a/b/c → State`) rather than arbitrary shared mutation.

# 37. State Transition Model

The Flow can be understood as `Current State + Process Result → Transition Decision → Next State → Next Process`; formally `S(n) + Result(Pn) → Transition → S(n+1)`. This is the core mechanism behind deterministic Flow orchestration.

---

# 38. Example: Complete Flow Plan

Suppose the validated Process architecture is:

```text
P1 Analyze Source
P2 Define Requirements
P3 Generate Chapter
P4 Evaluate Chapter
P5 Improve Chapter
H1 Human Approval
```

Flow:

```text
START
  ↓
P1 Analyze Source
  ↓
P2 Define Requirements
  ↓
P3 Generate Chapter
  ↓
P4 Evaluate Chapter
  ↓
Pass?
 ├── NO → P5 Improve Chapter
 │          ↓
 │        P4 Evaluate Chapter
 │
 └── YES
       ↓
    H1 Human Approval
       ↓
    Approved?
     ├── YES → SUCCESS
     └── NO  → P5 Improve Chapter
```

State:

```yaml
flow_state:
  workflow:
    status: running
    current_process: evaluate_chapter

  input:
    source_ref: ""

  process_outputs:
    source_analysis: {}
    chapter_requirements: {}
    chapter_draft: {}
    evaluation: {}

  decisions:
    evaluation_passed: false

  approval:
    status: pending

  iteration:
    revision_count: 0
    max_revisions: 3
```

The Flow does not need to know whether:

```text
P1 = Python
P2 = Agent + Task
P3 = Crew
P4 = Python
P5 = Crew
H1 = Human interface
```

Those decisions happen later.

---

# 39. Flow Planning Validation

Before moving to the next stage, validate:

## Start

* [ ] Start condition is explicit.
* [ ] Required initial inputs are defined.

## Transitions

* [ ] Every required Process has an incoming transition.
* [ ] Every Process has defined completion behavior.
* [ ] Every transition has a logical reason.
* [ ] Conditional transitions have explicit conditions.

## State

* [ ] Required state is identified.
* [ ] State fields have logical ownership.
* [ ] State does not duplicate unnecessary information.
* [ ] Large artifacts use references where appropriate.
* [ ] State and Knowledge are separated.
* [ ] State and Memory are separated.

## Parallelism

* [ ] Parallel Processes are genuinely independent.
* [ ] Shared-state conflicts are avoided.
* [ ] Merge behavior is defined where necessary.

## Iteration

* [ ] Loop conditions are explicit.
* [ ] Iteration counters or limits are identified.
* [ ] Termination is defined.

## Human Gates

* [ ] Human approval points are explicit.
* [ ] Approval state is retained.
* [ ] Every human outcome has a transition.

## Termination

* [ ] Success state is explicit.
* [ ] Failure/rejection states are identifiable.
* [ ] No successful path ends without establishing the goal.

---

# 40. Conceptual Output Schema

The Flow and State Plan can be represented as:

```yaml
flow_state_plan:
  flow:
    name: ""
    purpose: ""

    start:
      condition: ""
      inputs: []

    terminal_states:
      success: ""
      failure: ""
      alternate: []

    processes:
      - process_id: ""
        entry_condition: ""
        exit_condition: ""

    transitions:
      - from: ""
        to: ""
        type: ""
        condition: ""

  state:
    fields:
      - name: ""
        purpose: ""
        source: ""
        owner: ""
        lifetime: ""
        required_for: []

  decisions:
    - id: ""
      source: ""
      condition: ""
      transitions: []

  iterations:
    - id: ""
      condition: ""
      loop_to: ""
      counter: ""
      limit: null

  parallel_groups:
    - id: ""
      processes: []
      merge_at: ""

  human_gates:
    - id: ""
      purpose: ""
      decision: ""
      outcomes: []

  checkpoints:
    - after_process: ""
      reason: ""

  artifacts:
    - name: ""
      reference: ""
      produced_by: ""
      consumed_by: []
```

This is a conceptual architecture schema.

It should evolve only when implementation requirements justify additional structure.

---

# 41. Flow Planning Output

The output is a **Flow & State Plan** combining the validated Process architecture with the Flow Structure, State Model, Transition Model, Decision Model, Human Gates, Iteration Model, and Parallelism Model. This plan becomes an input to **06-corner-cases-and-failure-planning.md**, which tests what happens when the planned Flow does **not** follow the happy path.

---

# 42. Core Amsha Rules

1. > Process defines meaningful work; Flow defines execution control.
2. > Do not create Flow structure before the Process architecture is validated.
3. > State should contain the minimum information required to execute, decide, and recover the workflow.
4. > Flow state is not Knowledge and is not Memory.
5. > State should follow Process contracts and data dependencies.
6. > Transitions must represent explicit logical conditions, not accidental execution order.
7. > Parallel execution requires logical independence and safe state ownership.
8. > Every iteration requires a meaningful success condition and bounded termination behavior.
9. > Human decisions must be explicit workflow boundaries.
10. > Large artifacts should normally be referenced rather than copied into Flow state.
11. > Flow state and LLM context are different abstractions.
12. > Implementation mechanisms are selected only after the Flow and State architecture is understood.

---

# 43. Final Architecture Boundary

At the end of this stage, Amsha should understand: **WHAT** (Processes), **WHAT EACH PROCESS NEEDS/PRODUCES** (Process Contracts), **WHETHER THE ARCHITECTURE IS VALID** (Process Validation), **HOW PROCESSES EXECUTE** (Flow), **WHAT MUST BE RETAINED** (State), **HOW EXECUTION DECISIONS ARE MADE** (Transitions/Conditions), **WHERE EXECUTION CAN ITERATE** (Loops), **WHERE IT CAN BRANCH** (Conditions), **WHERE IT RUNS IN PARALLEL** (Parallel Groups), and **WHERE HUMANS DECIDE** (Human Gates). Only after this should Amsha reason about Python, Agent, Task, Crew, Tool, Knowledge, Memory, and MCP.

> **Design the workflow and its state model first; choose the implementation capabilities second.**
