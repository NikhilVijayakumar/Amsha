#  Amsha Prerequisite: Corner Cases and Failure Planning

## Purpose

The Process architecture defines **what meaningful work must happen**.

The Flow and State Plan defines **how that work executes during the expected path**.

This document defines how Amsha reasons about what happens when execution does **not** follow the expected path.

The objective is to identify and explicitly plan for:

- invalid inputs
- missing inputs
- malformed inputs
- empty results
- unexpected outputs
- Process failures
- validation failures
- conditional failures
- iteration exhaustion
- human rejection
- human timeout
- external system failures
- tool failures
- partial completion
- state corruption
- unavailable dependencies
- duplicate execution
- cancellation
- recovery
- unrecoverable termination

The goal is not to predict every imaginable failure.

The goal is:

> **Identify failures that can materially affect correctness, execution, state, cost, safety, or termination, and define what the workflow should do about them.**

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

This stage consumes the approved:

* Problem Definition
* Goal and Boundary Definition
* Process Architecture
* Process Contracts
* Flow Structure
* State Model
* Transition Model
* Human Gates
* Iteration Model
* Termination Conditions

It then asks:

> What happens when assumptions fail?

---

# 2. Happy Path Is Not Enough

A workflow designed only around successful execution is incomplete.

Example:

```text
Input
  ↓
Analyze
  ↓
Generate
  ↓
Evaluate
  ↓
Approve
  ↓
Success
```

This describes only the happy path.

A real workflow must also account for:

```text
Input
  ├── invalid
  ├── missing
  └── incomplete

Analyze
  ├── fails
  └── produces unusable output

Generate
  ├── fails
  └── produces invalid output

Evaluate
  ├── fails
  └── rejects output

Approve
  ├── approves
  ├── requests revision
  ├── rejects
  └── does not respond
```

Therefore:

> **Every meaningful Process boundary is also a potential failure boundary.**

---

# 3. Failure Planning Is Not Failure Prediction

Amsha should not attempt to predict every possible runtime failure.

Instead distinguish:

```text
Failure Prediction
        vs
Failure Planning
```

Failure prediction asks:

> What might happen?

Failure planning asks:

> If this happens, what should the architecture do?

The second is the important architectural requirement.

---

# 4. Failure Categories

Failures should be classified to make reasoning systematic.

Recommended categories:

```text
Input
Contract
Process
Output
Validation
Decision
Iteration
Human
State
External
Tool
Resource
Timeout
Concurrency
Recovery
System
```

These categories can overlap.

For example:

```text
External API timeout
```

may be:

```text
External
+
Timeout
+
Recovery
```

---

# 5. Input Failures

Input failures occur before or at the beginning of a Process.

Examples:

```text
Missing required input
Invalid format
Malformed data
Unsupported type
Incomplete information
Contradictory information
Empty input
Unexpected input size
Invalid reference
```

The architecture should determine whether the input:

```text
Reject
Repair
Request clarification
Use default
Skip optional path
Escalate
```

is appropriate.

Do not silently invent critical missing information.

---

# 6. Required vs Optional Input Failure

Required and optional inputs must behave differently.

Example:

```yaml
input:
  required:
    - source_document

  optional:
    - style_reference
```

If `source_document` is missing:

```text
Cannot execute Process
```

If `style_reference` is missing:

```text
Continue without style reference
```

unless the Process contract specifies another behavior.

This distinction should be explicit.

---

# 7. Input Validation Boundary

Input validation should happen before expensive downstream execution.

Conceptually:

```text
START
  ↓
Validate Input
  ↓
Valid?
 ├── NO  → Input Error
 └── YES
       ↓
     Process
```

Do not allow malformed inputs to propagate through multiple Processes before discovering the problem.

Where validation is deterministic, prefer deterministic validation.

Examples:

```text
schema validation
file existence
required fields
type checking
range checking
reference existence
```

---

# 8. Process Failure

A Process can fail even when its inputs are valid.

Examples:

```text
runtime exception
LLM failure
invalid tool response
external dependency failure
resource exhaustion
unexpected internal state
```

The Flow must distinguish:

```text
Process succeeded
Process produced a valid negative result
Process failed to execute
```

These are not the same.

---

# 9. Failure vs Negative Result

This distinction is critical.

Example:

```text
Evaluate Chapter
```

may produce:

```text
Result A:
evaluation_passed = false
```

This is a **valid Process result**.

It should normally transition to:

```text
Improve Chapter
```

But:

```text
Evaluator crashed
```

is a **Process failure**.

It should follow a failure path:

```text
Evaluator
   ↓
FAILED
   ↓
Recovery / Retry / Escalation
```

Do not treat runtime failure as a domain-level rejection.

---

# 10. Failure Taxonomy

A useful model is:

```text
PROCESS OUTCOME
├── SUCCESS
├── VALID NEGATIVE RESULT
├── RETRYABLE FAILURE
├── RECOVERABLE FAILURE
└── TERMINAL FAILURE
```

### SUCCESS

Process completed and produced a valid successful result.

### VALID NEGATIVE RESULT

Process completed correctly but its result does not satisfy the desired condition.

Example:

```text
Evaluation = failed
```

### RETRYABLE FAILURE

Temporary failure may succeed if retried.

Example:

```text
temporary network failure
```

### RECOVERABLE FAILURE

The current execution cannot continue directly but can recover through another path.

Example:

```text
invalid generated artifact
```

### TERMINAL FAILURE

The workflow cannot continue meaningfully.

Example:

```text
required source does not exist
```

---

# 11. Retry Planning

Retries should be intentional.

Do not automatically retry every failure.

A retry is appropriate when:

* failure is likely transient
* retry is safe
* retry has a reasonable chance of success
* retry cost is acceptable
* repeated execution does not create harmful side effects

Example:

```text
External Service
     ↓
Timeout
     ↓
Retry
```

But:

```text
Invalid input
     ↓
Retry same input
```

usually does not solve the problem.

---

# 12. Retry Limits

Every retryable failure should have bounded behavior.

Example:

```yaml
retry:
  max_attempts: 3
```

Conceptually:

```text
Attempt 1
   ↓
Failure
   ↓
Attempt 2
   ↓
Failure
   ↓
Attempt 3
   ↓
Failure
   ↓
Escalate / Terminal Failure
```

Avoid unbounded automatic retries.

---

# 13. Retry vs Iteration

Retries and workflow iterations are different.

## Retry

The Process failed to execute correctly.

```text
Process
  ↓
Execution Failure
  ↓
Retry same Process
```

## Iteration

The Process executed successfully but its result requires additional work.

```text
Generate
  ↓
Evaluate
  ↓
Not acceptable
  ↓
Improve
  ↓
Generate
```

Do not confuse:

```text
execution failure
```

with:

```text
valid domain-level rejection
```

---

# 14. Output Failures

A Process can execute successfully but produce an invalid output.

Example:

```text
Generate Chapter
       ↓
Output
       ↓
Schema Validation
       ↓
Invalid
```

The Flow must determine whether to:

* retry generation
* repair output
* return to an earlier Process
* request human review
* terminate

Output validation should occur at the Process boundary when the contract requires it.

---

# 15. Contract Violations

A Process output violates its contract when:

```text
required field missing
wrong structure
wrong type
invalid reference
incomplete result
unexpected semantic content
```

Example:

```yaml
expected:
  chapter:
    title: string
    content: string
```

but the Process produces:

```yaml
chapter:
  content: ""
```

This should be detected before downstream execution.

---

# 16. Validation Layers

Failure planning should distinguish:

```text
Structural Validation
        ↓
Semantic Validation
        ↓
Business / Domain Validation
        ↓
Human Acceptance
```

Example:

```text
Generated Artifact
       ↓
Schema Valid?
       ↓
Semantically Valid?
       ↓
Meets Domain Criteria?
       ↓
Human Approved?
```

Failure at each level can require a different response.

---

# 17. Decision Failures

A Flow decision may fail because its decision input is:

* missing
* invalid
* ambiguous
* contradictory
* outside expected range

Example:

```text
Evaluation Score
```

Expected:

```text
0–100
```

Received:

```text
null
```

The Flow should not silently choose a branch.

Instead:

```text
Decision Failure
      ↓
Retry / Repair / Escalate
```

---

# 18. Ambiguous Decisions

Some decisions cannot be safely determined automatically.

Example:

```text
Two valid creative directions exist.
```

The architecture may require:

```text
Automated Evaluation
        ↓
Ambiguous
        ↓
Human Review
```

This creates a controlled fallback from automation to human judgment.

---

# 19. Human Rejection

Human rejection is not necessarily a failure.

Example:

```text
Human Review
     ↓
REVISE
```

is a valid workflow outcome.

Similarly:

```text
Human Review
     ↓
REJECT
```

may be a valid terminal state.

The architecture must define the semantics.

For example:

```text
APPROVE
  → continue

REVISE
  → improvement loop

REJECT
  → terminal rejection
```

---

# 20. Human Timeout

A human gate may remain unresolved.

Example:

```text
WAITING_FOR_HUMAN
        ↓
No response
```

The architecture should define what happens.

Possible policies:

```text
Wait indefinitely
Timeout
Escalate
Cancel
Return to queue
Notify
```

Do not invent a default behavior when the business requirement is unknown.

If human responsiveness is important to the workflow, it should be explicitly defined.

---

# 21. External Dependency Failures

External systems introduce additional failure modes.

Examples:

```text
API unavailable
MCP server unavailable
Tool unavailable
Authentication failure
Rate limit
Network timeout
Invalid external response
External operation partially completed
```

The Flow should distinguish:

```text
Request failed
```

from:

```text
Request succeeded but response was not received
```

The second case may create a duplicate-execution risk.

---

# 22. Side Effects and Idempotency

Before retrying an external operation, determine whether it is safe to execute again.

Example:

```text
Create Asset
```

may create duplicate assets if blindly retried.

Better:

```text
Check Operation Status
        ↓
Already Completed?
 ├── YES → Use Existing Result
 └── NO  → Retry
```

The architecture should identify Processes with side effects.

Examples:

```text
create
delete
publish
send
charge
deploy
modify
generate external artifact
```

These require stronger retry and recovery planning.

---

# 23. Idempotency

A Process is idempotent when repeating it does not create an unintended additional effect.

Example:

```text
Calculate Score
```

is usually naturally repeatable.

Whereas:

```text
Publish Asset
```

may not be.

Failure planning should therefore classify important Processes as:

```yaml
execution:
  retryable: true
  idempotent: true
```

or:

```yaml
execution:
  retryable: false
  idempotent: false
```

when known.

---

# 24. Partial Completion

A Process may perform part of its work before failing.

Example:

```text
Generate Asset
    ↓
Asset created
    ↓
Metadata update fails
```

The system is now in a partial state.

The architecture must determine whether to:

```text
Rollback
Resume
Repair
Reuse partial result
Mark incomplete
Escalate
```

Partial completion is particularly important for external side effects.

---

# 25. State Failures

State can become invalid or inconsistent.

Examples:

```text
missing state field
stale state
contradictory state
corrupted checkpoint
unexpected state transition
state from incompatible workflow version
```

The Flow should not continue blindly when critical state invariants are violated.

Example:

```text
current_process = evaluate
but chapter_draft does not exist
```

This is a state consistency failure.

---

# 26. State Invariants

Important state relationships should be defined as invariants.

Example:

```text
If current_process = evaluate
then chapter_draft must exist.
```

Another:

```text
If approval.status = approved
then evaluation.status must be passed.
```

Another:

```text
If revision_count > 0
then a previous evaluation must exist.
```

These invariants can often be validated deterministically.

---

# 27. State Recovery

When state is invalid, recovery may require:

```text
Checkpoint Restore
Reconstruct State
Replay Process
Restart Process
Restart Workflow
Human Intervention
Terminal Failure
```

The correct option depends on the workflow.

Do not assume that restarting the entire Flow is always safe.

---

# 28. Checkpoint Planning

Failure planning should identify where recovery checkpoints matter.

Example:

```text
P1
 ↓
Checkpoint
 ↓
P2
 ↓
Checkpoint
 ↓
P3
```

If P3 fails:

```text
Restore checkpoint
        ↓
Resume from P3
```

rather than:

```text
Restart P1
Restart P2
Restart P3
```

This is especially valuable for:

* expensive LLM operations
* long-running Processes
* external operations
* human approval boundaries
* large artifact generation

---

# 29. Cancellation

The workflow should distinguish failure from cancellation.

```text
RUNNING
   ↓
CANCELLED
```

Cancellation may be caused by:

* user request
* system shutdown
* deadline
* resource policy
* external event

The architecture should define whether cancellation:

```text
Stops immediately
Finishes current Process
Performs cleanup
Persists state
Allows resume
```

---

# 30. Timeouts

Every potentially long-running operation should be considered for timeout behavior.

Examples:

```text
LLM call
External API
MCP operation
Human review
Asset generation
Long-running Python operation
```

Timeout handling should define:

```text
timeout
  ↓
retry?
  ↓
fallback?
  ↓
escalate?
  ↓
terminate?
```

Avoid treating timeout as automatically equivalent to failure when the underlying operation may still have completed.

---

# 31. Resource Failures

Resource failures include:

```text
Out of memory
Disk unavailable
GPU unavailable
Token budget exceeded
Rate limit
Execution quota exceeded
Concurrency limit
Storage limit
```

The architecture should identify resource constraints that can materially affect the workflow.

Possible responses:

```text
Retry later
Reduce workload
Use fallback
Queue
Pause
Escalate
Terminate
```

---

# 32. Token and Cost Failure

For LLM-based workflows, resource failure can include excessive token consumption.

Example:

```text
Repeated revision loop
        ↓
Token budget exceeded
```

The architecture should have a bounded policy.

Possible controls:

```text
maximum iterations
maximum model calls
maximum context size
maximum workflow budget
human escalation
```

Cost control should be part of architecture where repeated or autonomous execution can otherwise grow without bound.

---

# 33. Loop Exhaustion

An iterative workflow must define what happens when the maximum iteration count is reached.

Example:

```text
Generate
  ↓
Evaluate
  ↓
Fail
  ↓
Improve
  ↓
Generate
  ↓
...
  ↓
Max Iterations
```

Possible outcomes:

```text
Return best result
Human review
Escalate
Terminal failure
```

Never leave the result undefined.

---

# 34. Best-Result Preservation

When an iterative workflow generates progressively different candidates, it may be useful to retain the best valid result.

Example:

```text
Iteration 1 → score 72
Iteration 2 → score 81
Iteration 3 → score 77
```

At iteration limit:

```text
Best Result = Iteration 2
```

This is only appropriate when the Process contract defines a meaningful comparison criterion.

Do not assume that the latest result is always the best result.

---

# 35. Failure Severity

Failures should be classified by impact.

Recommended levels:

```text
INFO
WARNING
RECOVERABLE
ERROR
CRITICAL
```

### WARNING

Execution can continue safely.

### RECOVERABLE

Requires recovery before continuing.

### ERROR

Current Process cannot complete normally.

### CRITICAL

Workflow integrity or correctness is compromised.

Severity should be based on workflow impact, not merely technical exception type.

---

# 36. Failure Response Types

A failure plan can use a controlled set of responses:

```text
IGNORE
RETRY
REPAIR
REPEAT_PROCESS
RETURN_TO_PROCESS
FALLBACK
WAIT
HUMAN_REVIEW
ESCALATE
ROLLBACK
RESUME
CANCEL
TERMINATE
```

The actual response should be chosen according to failure semantics.

---

# 37. Failure Matrix

A useful planning artifact is a failure matrix.

Example:

```yaml
failure_cases:
  - id: missing_source
    category: input
    trigger: "required source is missing"
    severity: error
    response: request_input
    retryable: false

  - id: evaluator_timeout
    category: timeout
    trigger: "evaluation exceeds timeout"
    severity: recoverable
    response: retry
    retryable: true
    max_attempts: 3

  - id: evaluation_failed
    category: domain_result
    trigger: "chapter does not satisfy evaluation criteria"
    severity: warning
    response: revise
    retryable: false

  - id: human_rejection
    category: human
    trigger: "reviewer rejects output"
    severity: warning
    response: revise
```

The exact schema can evolve.

The important requirement is to make failure behavior explicit.

---

# 38. Failure Planning by Process

Each important Process should be reviewed individually.

For each Process ask:

```text
What can make this Process fail?
What can make its output invalid?
What can make its output unusable?
What happens if it is unavailable?
Can it be retried?
Is retry safe?
Can it partially complete?
Can it be resumed?
Does it require human intervention?
What is the terminal failure?
```

Example:

```text
P3 Generate Chapter

Potential failures:
- model unavailable
- invalid structured output
- empty output
- context missing
- generation timeout
- content fails validation
- generation budget exhausted
```

Each relevant case should have a response.

---

# 39. Failure Planning by Transition

Transitions also need failure analysis.

Example:

```text
P4 Evaluate
   ↓
Pass?
```

Potential issues:

```text
evaluation missing
evaluation ambiguous
evaluation malformed
score outside expected range
condition cannot be determined
```

The Flow should define what happens when the transition decision cannot safely be made.

---

# 40. Failure Planning by State

State should be reviewed for invalid combinations.

Example:

```text
status = approved
draft = missing
```

This should be impossible or explicitly recoverable.

State invariants should therefore be included in failure planning.

---

# 41. Failure Planning by External Boundary

Every external boundary should be reviewed.

```text
Flow
 ↓
External System
 ↓
Result
```

Ask:

* What if unavailable?
* What if timeout occurs?
* What if response is malformed?
* What if operation succeeded but response was lost?
* What if authentication fails?
* What if rate-limited?
* What if partial completion occurs?
* Can operation be retried safely?

This becomes particularly important for Tools and MCP integrations later.

---

# 42. Failure Planning Does Not Mean Overengineering

Do not create elaborate recovery mechanisms for insignificant failures.

Use proportionality.

For example:

```text
Simple deterministic calculation
```

may only require:

```text
exception → terminal Process failure
```

Whereas:

```text
Expensive external asset generation
```

may require:

```text
timeout
retry
operation status check
checkpoint
resume
partial-result handling
```

The recovery architecture should reflect the consequences of failure.

---

# 43. Failure Priority

A useful priority model is:

```text
Impact × Likelihood × Recovery Difficulty
```

This does not need to be a literal numeric score.

It is a reasoning heuristic.

Prioritize failures that are:

* likely
* expensive
* difficult to recover
* destructive
* capable of corrupting state
* capable of producing incorrect final output
* capable of causing unbounded execution

---

# 44. Safety-Critical or High-Impact Decisions

Some workflows require stronger failure handling around decisions that materially affect people, systems, assets, or irreversible actions.

For such decisions:

```text
Automation
    ↓
Validation
    ↓
Human Review
    ↓
Explicit Approval
    ↓
Irreversible Action
```

may be preferable to fully autonomous execution.

The appropriate level depends on the problem definition and requirements.

---

# 45. Failure Containment

A failure should affect the smallest appropriate scope.

For example:

```text
P2 failure
```

should not necessarily terminate:

```text
entire workflow
```

if P2 can be independently retried or recovered.

Prefer:

```text
Local Failure
    ↓
Local Recovery
    ↓
Continue
```

when safe.

Escalate to larger scopes only when necessary.

---

# 46. Failure Propagation

A failure can propagate downstream.

Example:

```text
P1
 ↓
invalid output
 ↓
P2
 ↓
unexpected behavior
 ↓
P3
```

The architecture should detect contract violations at the earliest boundary.

Prefer:

```text
P1
 ↓
Output Validation
 ↓
FAIL
```

rather than allowing bad state to propagate.

---

# 47. Graceful Degradation

Some workflows can continue with reduced capability.

Example:

```text
Optional enrichment service unavailable
```

may allow:

```text
Continue without enrichment
```

while:

```text
Required source unavailable
```

may require termination.

Therefore classify dependencies as:

```text
Required
Optional
Fallback-capable
```

during failure planning.

---

# 48. Fallbacks

Fallback behavior must preserve the goal as much as possible.

Example:

```text
Primary Process
     ↓
Failure
     ↓
Fallback Process
```

A fallback is valid only when its output satisfies the downstream contract or when the architecture explicitly accepts degraded output.

Do not introduce a fallback simply because one exists.

---

# 49. Failure Recovery Flow

A generic recovery pattern is:

```text
Process
   ↓
Failure
   ↓
Classify
   ↓
Retryable?
 ├── YES → Retry
 │          ↓
 │        Success?
 │        ├── YES → Continue
 │        └── NO  → Escalate
 │
 └── NO
       ↓
Recoverable?
 ├── YES → Recovery
 └── NO  → Terminal Failure
```

This is a conceptual pattern.

Each workflow should define only the branches it actually needs.

---

# 50. Failure State Model

The Flow state may include:

```yaml
failure:
  status: ""
  process_id: ""
  category: ""
  severity: ""
  attempts: 0
  max_attempts: 0
  recoverable: false
  retryable: false
  last_error: ""
  recovery_action: ""
```

This should not become a dumping ground for arbitrary exception details.

Retain information that supports:

* recovery
* debugging
* observability
* audit requirements

---

# 51. Failure History

For workflows where history matters, retain meaningful failure events.

Example:

```yaml
failure_history:
  - process_id: "evaluate"
    category: "timeout"
    attempt: 1
    action: "retry"

  - process_id: "evaluate"
    category: "timeout"
    attempt: 2
    action: "retry"
```

History is different from current failure state.

```text
Current State
    ≠
Historical Events
```

---

# 52. Failure Planning Output

The output should be a structured failure plan.

Conceptual schema:

```yaml
failure_plan:
  policies:
    default_failure: ""
    default_retry_limit: 0

  cases:
    - id: ""
      process_id: ""
      category: ""
      trigger: ""
      severity: ""
      outcome_type: ""
      response: ""
      retryable: false
      max_attempts: null
      idempotent: null
      human_required: false

  state_invariants:
    - condition: ""
      violation_response: ""

  recovery:
    checkpoints: []
    resumable_processes: []
    restart_boundaries: []

  human_escalations:
    - trigger: ""
      decision: ""

  termination:
    failure: ""
    exhausted: ""
    cancelled: ""
```

---

# 53. Failure Validation

Before proceeding, validate:

## Inputs

* [ ] Required input failures are considered.
* [ ] Optional input behavior is defined.
* [ ] Invalid input does not silently propagate.

## Processes

* [ ] Important Process failures are identified.
* [ ] Negative results are distinguished from execution failures.
* [ ] Output contract violations are handled.

## Transitions

* [ ] Invalid decision inputs have a defined response.
* [ ] Conditional branches cannot become undefined.

## Iterations

* [ ] Maximum iteration behavior is defined.
* [ ] Retry limits are defined.
* [ ] Loop exhaustion has a defined outcome.

## External Systems

* [ ] Timeouts are considered.
* [ ] External unavailability is considered.
* [ ] Retry safety is considered.
* [ ] Partial completion is considered.
* [ ] Idempotency is considered where relevant.

## State

* [ ] Important state invariants are defined.
* [ ] State corruption has a recovery strategy.
* [ ] Checkpoint boundaries are identified where necessary.

## Human

* [ ] Human rejection is defined.
* [ ] Human timeout behavior is defined where relevant.
* [ ] Escalation paths are explicit.

## Termination

* [ ] Terminal failures are defined.
* [ ] Cancellation is defined where required.
* [ ] No failure path can loop indefinitely.

---

# 54. Anti-Patterns

## 54.1 Happy-Path-Only Architecture

```text
Input
 ↓
Process
 ↓
Success
```

No failure paths are considered.

---

## 54.2 Retry Everything

```text
Any failure
 ↓
Retry forever
```

This causes:

* infinite execution
* unnecessary cost
* duplicate side effects
* resource exhaustion

---

## 54.3 Treating Rejection as Failure

```text
Evaluation failed
```

may be a valid result.

Do not automatically classify it as an execution error.

---

## 54.4 Silent Recovery

```text
Something failed
 ↓
System silently does something else
```

Recovery behavior should be explicit and traceable.

---

## 54.5 Giant Error Handler

Avoid:

```text
Any error
 ↓
One generic recovery mechanism
```

Different failures require different responses.

---

## 54.6 Failure Handling Inside Every Process

Do not duplicate the entire recovery framework inside every Process.

Separate:

```text
Process Contract
```

from:

```text
Flow-level failure policy
```

while retaining Process-specific recovery requirements.

---

## 54.7 Overengineering

Do not design distributed recovery infrastructure for a simple deterministic Process.

Recovery complexity should be proportional to:

```text
Failure Impact
+
Failure Likelihood
+
Recovery Difficulty
```

---

# 55. Relationship to Later Capability Selection

Failure planning helps determine which capabilities are actually required.

For example:

```text
Need deterministic validation
        ↓
Python may be sufficient
```

or:

```text
Need external system recovery/status
        ↓
Tool / MCP may be required
```

or:

```text
Need human approval
        ↓
Human interaction mechanism required
```

or:

```text
Need persistent recovery
        ↓
Checkpointing / persistence required
```

However, this stage should identify the **requirement**, not prematurely choose the implementation.

The next stage, `07-capability-selection.md`, makes those decisions.

---

# 56. Example

Consider:

```text
Generate Chapter
      ↓
Evaluate Chapter
      ↓
Pass?
 ├── YES → Human Approval
 └── NO  → Improve Chapter
              ↓
           Generate
```

Failure planning expands this into:

```text
START
  ↓
Validate Input
  ├── invalid → REQUEST INPUT
  └── valid
       ↓
Generate
  ├── timeout → RETRY
  ├── invalid output → REGENERATE
  └── valid
       ↓
Evaluate
  ├── timeout → RETRY
  ├── execution failure → ESCALATE
  └── valid
       ↓
Pass?
 ├── NO → Improve
 │          ↓
 │       iteration limit?
 │        ├── YES → HUMAN REVIEW
 │        └── NO  → Generate
 │
 └── YES
       ↓
Human Approval
 ├── APPROVE → SUCCESS
 ├── REVISE  → Improve
 └── REJECT  → REJECTED
```

This is a much more complete execution architecture.

---

# 57. Failure Planning Principles

### Rule 1

> **Design the workflow for meaningful failure paths, not only successful execution.**

### Rule 2

> **Distinguish execution failure from a valid negative domain result.**

### Rule 3

> **Retry only when retry is meaningful and safe.**

### Rule 4

> **All automatic retries and iterations must be bounded.**

### Rule 5

> **Do not silently invent recovery behavior for unresolved requirements.**

### Rule 6

> **Validate outputs at Process boundaries before invalid state propagates downstream.**

### Rule 7

> **External side effects require explicit retry and idempotency reasoning.**

### Rule 8

> **State invariants should be validated where they materially protect workflow correctness.**

### Rule 9

> **Failures should be contained at the smallest safe scope.**

### Rule 10

> **Human rejection is not automatically a technical failure.**

### Rule 11

> **Recovery complexity should be proportional to failure impact and recovery cost.**

### Rule 12

> **Failure planning should identify requirements; capability selection decides implementation mechanisms.**

---

# 58. Final Architecture Boundary

At the end of this stage, Amsha should understand not only:

```text
What happens when everything works?
```

but also:

```text
What happens when:
    input is invalid?
    Process fails?
    output is invalid?
    validation rejects?
    decision is ambiguous?
    iteration never succeeds?
    human rejects?
    human does not respond?
    external system fails?
    operation partially completes?
    state becomes inconsistent?
    retry is unsafe?
    checkpoint must be restored?
    workflow is cancelled?
```

The resulting architecture becomes:

```text
Problem
   ↓
Goal
   ↓
Processes
   ↓
Contracts
   ↓
Validation
   ↓
Flow
   ↓
State
   ↓
Corner Cases
   ↓
Failure Paths
   ↓
Recovery / Escalation / Termination
```

Only after this should Amsha determine the minimum implementation capabilities required.

The next stage is:

```text
07-capability-selection.md
```

Its purpose is to answer:

> **Given the validated Process, Flow, State, and Failure architecture, what is the least powerful implementation mechanism required for each part?**

```
```
