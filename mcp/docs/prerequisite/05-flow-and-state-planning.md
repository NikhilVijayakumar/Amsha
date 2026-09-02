# Amsha Prerequisite: Flow and State Planning

## Purpose

The Process architecture defines **what meaningful work must happen**.

This document defines how those approved Processes become an **executable workflow structure** by determining:

- execution order
- transitions
- conditions
- iterations
- parallel execution
- state requirements
- Process outputs that must be retained
- information required between Processes
- human approval gates
- runtime control boundaries
- recovery-relevant state

The objective is to design the workflow **before implementing it with CrewAI Flow, Python, Crews, Agents, Tasks, Tools, Knowledge, Memory, or MCP**.

The output of this stage is a **Flow and State Plan**.

---

# 1. Position in the Architecture Process

The prerequisite sequence is:

```text
00 Problem Definition
        ↓
01 Goal & Boundary Definition
        ↓
02 Process Decomposition
        ↓
03 Process Contracts & Atomicity
        ↓
04 Process Validation & Human Review
        ↓
05 Flow & State Planning
        ↓
06 Corner Cases & Failure Planning
        ↓
07 Capability Selection
        ↓
08 Architecture Validation
````

This stage assumes that the Process architecture has already been validated.

The question now changes from:

> "What work must happen?"

to:

> "How must that approved work move through the workflow, and what state must exist to control it?"

Still avoid deciding prematurely:

* which Agent performs the Process
* which Crew performs the Process
* which Task implements the Process
* which LLM is used
* which Tool is used
* which MCP server is used

Those decisions belong to later stages.

---

# 2. Flow as Execution Architecture

A Flow is the execution structure that connects approved Processes.

Conceptually:

```text
Approved Process Architecture
            ↓
     Flow & State Plan
            ↓
     Executable Workflow
```

A Flow determines:

```text
START
  ↓
Process
  ↓
Transition
  ↓
Process
  ↓
Decision
 ├── Branch A
 └── Branch B
  ↓
Iteration / Parallelism / Human Gate
  ↓
END
```

The Flow therefore answers:

* What executes first?
* What executes next?
* What conditions control transitions?
* What information moves between Processes?
* What state must be retained?
* When can execution stop?
* When can execution resume?
* Where can execution branch or iterate?

---

# 3. Process vs Flow

Process and Flow are related but different abstractions.

## Process

Describes meaningful work:

```text
Analyze Source
Generate Draft
Evaluate Draft
Approve Draft
```

## Flow

Describes execution control:

```text
Analyze
   ↓
Generate
   ↓
Evaluate
   ↓
Pass?
 ├── NO → Improve → Evaluate
 └── YES → Approve
```

Therefore:

> **Process defines work. Flow defines how work is orchestrated.**

A Process should remain understandable without knowing its eventual Flow implementation.

---

# 4. Flow Planning Inputs

Flow planning consumes:

```text
Problem Definition
        +
Goal & Boundary
        +
Validated Processes
        +
Process Contracts
        +
Process Relationships
        +
Human Review Requirements
        ↓
Flow & State Planning
```

Important inputs include:

* start condition
* end condition
* Process IDs
* Process dependencies
* Process inputs
* Process outputs
* conditional relationships
* iteration requirements
* parallel relationships
* human approval boundaries
* external dependencies
* termination conditions

---

# 5. Flow Planning Principles

Amsha should follow these principles.

## 5.1 Preserve Process Architecture

Do not redesign Processes merely to fit a preferred Flow implementation.

```text
Process Architecture
       ↓
Flow Architecture
```

not:

```text
Preferred CrewAI API
       ↓
Force Processes into it
```

---

## 5.2 Make Control Explicit

Important transitions should be visible.

Bad:

```text
Process A
then somehow Process B
```

Good:

```text
A
 ↓
condition
 ↓
B
```

---

## 5.3 Keep State Minimal

Only retain state that is required to:

* continue execution
* make decisions
* satisfy downstream contracts
* support recovery
* support required observability
* preserve explicitly required workflow history

Do not store every intermediate value merely because it exists.

---

## 5.4 Separate State from Knowledge

Current execution state is not domain knowledge.

```text
State:
current_process = evaluate_chapter
draft_id = 42
evaluation_status = failed

Knowledge:
story rules
character history
world rules
editorial guidelines
```

Knowledge answers:

> What information is known?

State answers:

> Where is the workflow and what has happened?

---

# 6. What Is Flow State?

Flow state represents the information required to control the current execution.

Typical state may include:

```yaml
flow_state:
  workflow_id: ""
  status: ""
  current_process: ""
  inputs: {}
  outputs: {}
  decisions: {}
  approvals: {}
  iteration: {}
  errors: []
```

The exact structure depends on the workflow.

The key principle is:

> State should represent the execution context necessary to continue and reason about the workflow.

---

# 7. State Categories

State can be divided into several categories.

```text
Flow State
├── Input State
├── Execution State
├── Process State
├── Decision State
├── Output State
├── Approval State
├── Iteration State
└── Error / Recovery State
```

## Input State

Information supplied when execution begins.

Example:

```yaml
input:
  source_document: ""
  chapter_number: 12
```

## Execution State

Current workflow position.

```yaml
execution:
  current_process: "evaluate_chapter"
  status: "running"
```

## Process State

Information produced or required by Processes.

```yaml
process:
  generate_chapter:
    status: "completed"
    output_ref: ""
```

## Decision State

Results controlling transitions.

```yaml
decisions:
  evaluation_passed: true
```

## Output State

Final or intermediate outputs that must remain available.

## Approval State

Human decisions.

```yaml
approval:
  status: "approved"
```

## Iteration State

Information required to control loops.

```yaml
iteration:
  revision_count: 2
  max_revisions: 3
```

## Error / Recovery State

Information needed to handle failures.

Detailed failure design belongs to `06-corner-cases-and-failure-planning.md`, but the Flow plan should identify state that will eventually be required for recovery.

---

# 8. State Should Follow Data Dependencies

State should be derived from actual Process contracts.

If:

```text
P1 Output
    ↓
P2 Input
```

and P2 executes later, the required P1 output must remain accessible.

Example:

```text
P1 Analyze Source
      ↓
analysis
      ↓
P2 Generate Draft
```

The Flow needs access to:

```yaml
state:
  analysis: {}
```

But if a Process produces information that is never consumed and is not needed for:

* final output
* decisions
* recovery
* observability

it generally does not need to become persistent Flow state.

---

# 9. State Is Not a Dump of Everything

A common architectural mistake is:

```text
Every Process output
        ↓
Put everything into Flow state
```

This creates:

* large state objects
* unnecessary serialization
* token overhead
* unclear ownership
* stale information
* harder recovery
* difficult debugging

Instead:

> Persist the minimum sufficient state required by the workflow.

---

# 10. State Ownership

Every important state field should have a logical owner.

For example:

```text
source_analysis
    owner → P1 Analyze Source

chapter_requirements
    owner → P2 Define Requirements

draft
    owner → P3 Generate Draft

evaluation
    owner → P4 Evaluate Draft

approval
    owner → Human Review
```

Ownership helps prevent unrelated Processes from arbitrarily modifying shared state.

A useful rule is:

> A Process should primarily produce or update state associated with its own contract.

---

# 11. Immutable vs Mutable State

Not all state should be freely modified.

Prefer immutable or append-only treatment for information that represents historical facts.

Example:

```yaml
inputs:
  source_document: "source-001"
```

should generally not change during execution.

Similarly:

```yaml
decisions:
  - process: "evaluate"
    result: "failed"
```

may be retained as execution history.

Mutable state is appropriate for values such as:

```yaml
current_process: ""
status: ""
```

The architecture should distinguish:

```text
Current State
        vs
Execution History
```

when both are needed.

---

# 12. State vs Memory

Flow state and Memory are not interchangeable.

## Flow State

Represents:

> What is happening in this execution?

Example:

```text
current_process
draft
evaluation
approval_status
iteration_count
```

## Memory

Represents:

> What should be retained for future context or future executions?

Example:

```text
previously approved preferences
historical interactions
learned information
past decisions
```

A Flow should not use Memory merely because it needs to pass information from Process A to Process B.

That is normally state or Process output context.

---

# 13. State vs Knowledge

Knowledge represents relatively stable reference information.

Example:

```text
Story Bible
Character Definitions
World Rules
Production Guidelines
```

State represents current execution information.

Example:

```text
Current Chapter
Current Draft
Evaluation Result
Revision Count
Approval Status
```

Therefore:

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

Every Process relationship should become an explicit transition rule.

Example:

```text
P1
 ↓
P2
```

means:

```text
When P1 completes successfully,
execute P2.
```

Conditional:

```text
P2
 ↓
evaluation
 ├── pass → P3
 └── fail → P4
```

means the Flow must evaluate a defined decision value.

The architecture should not depend on implicit interpretation.

---

# 16. Transition Types

Recommended conceptual transition types:

```text
SEQUENTIAL
CONDITIONAL
PARALLEL
ITERATIVE
HUMAN_GATE
TERMINAL
FAILURE
```

## Sequential

```text
A → B
```

## Conditional

```text
A → condition → B / C
```

## Parallel

```text
       ┌→ B
A ─────┤
       └→ C
```

## Iterative

```text
A → B → condition
      ↖     │
       ─────┘
```

## Human Gate

```text
A → Human Decision → B / C
```

## Terminal

```text
A → END
```

## Failure

```text
A → FAILURE HANDLER
```

Detailed failure paths are designed in the next prerequisite stage.

---

# 17. Sequential Flow

Use sequential execution when a genuine dependency exists.

```text
P1
 ↓
P2
 ↓
P3
```

This should mean:

```text
P2 requires P1
P3 requires P2
```

Do not create sequential execution merely because the Processes were listed in that order.

---

# 18. Parallel Flow

Parallel execution should be planned when Processes are independent.

Example:

```text
             ┌── P2 ──┐
P1 ──────────┤        ├── P4
             └── P3 ──┘
```

P2 and P3 may execute independently if:

* both require only P1's output
* neither modifies shared state required by the other
* their outputs can be safely combined
* downstream P4 can consume both

Parallelism should therefore be based on contract and state independence.

---

# 19. Parallel State Considerations

Parallel Processes introduce state ownership concerns.

Bad:

```text
P2 ──┐
     ├── modifies same field
P3 ──┘
```

when the final value depends on execution order.

Better:

```text
P2 → result_a
P3 → result_b
       ↓
     P4 Merge
```

The merge becomes an explicit Process or Flow operation when necessary.

This avoids hidden race conditions and ambiguous state ownership.

---

# 20. Conditional Flow

A conditional transition must have an explicit decision source.

Example:

```text
Evaluate
   ↓
score >= threshold?
 ├── YES → Approve
 └── NO  → Improve
```

The Flow plan should define:

```yaml
decision:
  id: evaluation_passed
  source: evaluation
  condition: "evaluation meets acceptance criteria"
  true_transition: approve
  false_transition: improve
```

The actual implementation may use Python, deterministic logic, or another mechanism later.

The architectural condition must exist independently of implementation.

---

# 21. Iterative Flow

Iterations should be represented explicitly.

Example:

```text
Generate
   ↓
Evaluate
   ↓
Pass?
 ├── YES → Continue
 └── NO  → Improve
              ↓
           Generate
```

The Flow plan must define:

* iteration trigger
* success condition
* retry/revision transition
* iteration counter
* maximum or bounded behavior
* terminal behavior if the limit is reached

Example:

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

Human approval should be represented as a first-class transition.

Example:

```text
Generate
   ↓
Validate
   ↓
Human Review
   ↓
Decision
 ├── APPROVE → END
 ├── REVISE  → Improve
 └── REJECT  → END
```

The Flow must retain the decision because downstream execution depends on it.

Example:

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

The Flow plan must define exactly what starts execution.

Possible triggers include:

```text
User request
File arrival
API request
Scheduled event
External event
Manual execution
Another workflow
```

At this stage, record the trigger semantically.

Do not prematurely decide which technical trigger implementation will be used.

Example:

```yaml
start:
  condition: "validated chapter request received"
```

---

# 24. Flow End

The Flow must define explicit terminal states.

Typical outcomes:

```text
SUCCESS
REJECTED
FAILED
CANCELLED
ABORTED
```

Not every workflow requires all of them.

The important requirement is that the end state is unambiguous.

Example:

```yaml
termination:
  success: "approved chapter produced"
  rejection: "human rejects chapter"
  failure: "workflow cannot produce valid chapter"
```

---

# 25. State and Termination

Termination conditions should be expressible using state.

Example:

```text
approval.status == "approved"
```

may establish successful completion.

Another workflow may require:

```text
evaluation.status == "passed"
AND
artifact.exists == true
AND
approval.status == "approved"
```

The Flow should not terminate simply because the final Process returned.

Execution completion and goal completion remain different concepts.

---

# 26. State and Human Review

When a human gate pauses execution, the Flow must preserve sufficient state to resume.

Example:

```text
Generate
   ↓
Validate
   ↓
WAITING_FOR_HUMAN
```

State should preserve:

```yaml
flow_state:
  status: waiting_for_human
  current_process: human_review
  artifact_ref: ""
  validation_result: {}
```

After approval:

```text
WAITING_FOR_HUMAN
        ↓
APPROVED
        ↓
Continue
```

The workflow should not need to reconstruct the previous execution merely to continue.

---

# 27. Flow Checkpoints

A checkpoint is a recoverable representation of execution state.

Conceptually:

```text
P1
 ↓
CHECKPOINT
 ↓
P2
 ↓
CHECKPOINT
 ↓
P3
```

Checkpoint planning should identify important recovery boundaries.

Good checkpoint candidates include:

* after expensive Processes
* after major artifact generation
* before human approval
* after human approval
* before iteration
* after major external operations
* at meaningful workflow boundaries

The detailed checkpoint and recovery design belongs later in implementation engineering, but the Flow plan should identify where state continuity matters.

---

# 28. State Lifetime

Not every state value needs the same lifetime.

Useful conceptual categories:

```text
Ephemeral
Process-scoped
Flow-scoped
Persistent
Historical
```

### Ephemeral

Needed only during one operation.

### Process-scoped

Needed while a Process executes.

### Flow-scoped

Needed by multiple Processes during one execution.

### Persistent

Must survive beyond the current Flow execution.

### Historical

Retained for audit, analysis, or future context.

State planning should assign the minimum necessary lifetime.

---

# 29. State Size and Token Efficiency

State can become a major source of unnecessary token consumption.

Avoid repeatedly passing large state objects to every LLM operation.

Instead:

```text
Flow State
    ↓
Relevant Context Selection
    ↓
Process
```

A Process should receive only the state relevant to its contract.

Bad:

```text
Every Agent receives entire Flow state.
```

Better:

```text
Flow State
   ↓
Relevant fields
   ↓
Process
   ↓
Minimal context
```

This principle is important to Amsha because:

> **Execution state and LLM context are not necessarily the same object.**

---

# 30. State and Context

Flow state determines what information exists.

Context selection determines what information is provided to a specific Process or Agent.

Example:

```text
Flow State
├── source_analysis
├── character_data
├── previous_drafts
├── evaluation
├── approval
└── execution_metadata
```

A generation Process may need:

```text
source_analysis
character_data
current_requirements
```

It may not need:

```text
execution_metadata
previous unrelated evaluations
approval history
```

Therefore:

```text
State ≠ Context
```

Context is a projection of state and other relevant information.

---

# 31. Flow State and External Systems

A Flow may interact with external systems.

Examples:

```text
Flow
 ├── Python
 ├── Crew
 ├── External API
 ├── ComfyUI
 └── Unreal Engine
```

The Flow should track the logical result of external operations.

For example:

```yaml
external_operation:
  status: "completed"
  operation_id: ""
  artifact_ref: ""
```

Do not store entire external-system responses in state unless required.

Prefer references where possible.

---

# 32. Artifacts vs State

Large outputs should generally not be embedded directly into Flow state when an artifact/reference is sufficient.

Instead of:

```yaml
state:
  generated_video:
    # enormous content
```

prefer:

```yaml
state:
  generated_video:
    artifact_ref: "video-001"
```

State controls the workflow.

Artifacts contain large outputs.

This separation helps:

* reduce memory usage
* reduce token transfer
* improve checkpointing
* simplify recovery
* improve observability

---

# 33. Flow and Python

Python may be used for deterministic orchestration logic.

Examples:

```text
validate schema
calculate score
select branch
merge results
transform data
check conditions
manage state
```

However, Python operations should remain appropriately scoped.

Avoid:

```text
One giant Python function
    ↓
implements the entire workflow
```

Prefer:

```text
Flow
 ├── Python: validate
 ├── Process
 ├── Python: calculate
 ├── Crew
 ├── Python: select branch
 └── Process
```

The Flow remains the orchestration layer.

---

# 34. Flow and Crew

A Process may later be implemented by a Crew when collaboration among multiple professional roles is justified.

Conceptually:

```text
Flow
  ↓
Process
  ↓
Crew
  ├── Agent
  ├── Agent
  └── Agent
```

The Flow should not care about internal Crew composition at this stage.

It only needs to know:

```text
Input
  ↓
Process
  ↓
Output
```

This preserves architectural separation.

---

# 35. Flow and Agent/Task

Likewise, a Process may later be implemented with:

```text
Agent
  ↓
Task
```

or:

```text
Agent
  ↓
multiple Tasks
```

The Process contract remains the stable boundary.

This prevents implementation details from leaking into the prerequisite architecture.

---

# 36. Flow State Ownership Model

A useful conceptual model is:

```text
                  Flow State
                      │
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
     Process A     Process B     Process C
        │             │             │
        ↓             ↓             ↓
     output_a      output_b      output_c
        └─────────────┼─────────────┘
                      ↓
                    State
```

Processes should interact with state through defined contracts rather than arbitrary shared mutation.

---

# 37. State Transition Model

The Flow can be understood as:

```text
Current State
     +
Process Result
     ↓
Transition Decision
     ↓
Next State
     ↓
Next Process
```

Formally:

```text
S(n) + Result(Pn)
        ↓
Transition
        ↓
S(n+1)
```

This is the core mechanism behind deterministic Flow orchestration.

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

The output of this stage is:

```text
Validated Process Architecture
        ↓
Flow Structure
        +
State Model
        +
Transition Model
        +
Decision Model
        +
Human Gates
        +
Iteration Model
        +
Parallelism Model
        ↓
Flow & State Plan
```

This plan becomes an input to:

```text
06-corner-cases-and-failure-planning.md
```

The next stage will test what happens when the planned Flow does **not** follow the happy path.

---

# 42. Core Amsha Rules

### Rule 1

> **Process defines meaningful work; Flow defines execution control.**

### Rule 2

> **Do not create Flow structure before the Process architecture is validated.**

### Rule 3

> **State should contain the minimum information required to execute, decide, and recover the workflow.**

### Rule 4

> **Flow state is not Knowledge and is not Memory.**

### Rule 5

> **State should follow Process contracts and data dependencies.**

### Rule 6

> **Transitions must represent explicit logical conditions, not accidental execution order.**

### Rule 7

> **Parallel execution requires logical independence and safe state ownership.**

### Rule 8

> **Every iteration requires a meaningful success condition and bounded termination behavior.**

### Rule 9

> **Human decisions must be explicit workflow boundaries.**

### Rule 10

> **Large artifacts should normally be referenced rather than copied into Flow state.**

### Rule 11

> **Flow state and LLM context are different abstractions.**

### Rule 12

> **Implementation mechanisms are selected only after the Flow and State architecture is understood.**

---

# 43. Final Architecture Boundary

At the end of this stage, Amsha should understand:

```text
WHAT
    ↓
Processes

WHAT EACH PROCESS NEEDS/PRODUCES
    ↓
Process Contracts

WHETHER THE PROCESS ARCHITECTURE IS VALID
    ↓
Process Validation

HOW PROCESSES EXECUTE
    ↓
Flow

WHAT MUST BE RETAINED
    ↓
State

HOW EXECUTION DECISIONS ARE MADE
    ↓
Transitions / Conditions

WHERE EXECUTION CAN ITERATE
    ↓
Loops

WHERE EXECUTION CAN BRANCH
    ↓
Conditions

WHERE EXECUTION CAN RUN IN PARALLEL
    ↓
Parallel Groups

WHERE HUMANS DECIDE
    ↓
Human Gates
```

Only after this should Amsha reason about:

```text
Python
Agent
Task
Crew
Tool
Knowledge
Memory
MCP
```

The central principle is:

> **Design the workflow and its state model first; choose the implementation capabilities second.**

```
```
