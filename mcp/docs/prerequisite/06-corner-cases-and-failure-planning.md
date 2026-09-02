#  Amsha Prerequisite: Corner Cases and Failure Planning

## Purpose

The Process architecture defines **what meaningful work must happen**; the Flow and State Plan defines **how that work executes during the expected path**. This document defines how Amsha reasons about what happens when execution does **not** follow the expected path — covering invalid/missing/malformed inputs, empty or unexpected outputs, Process/validation/conditional failures, iteration exhaustion, human rejection/timeout, external system and tool failures, partial completion, state corruption, unavailable dependencies, duplicate execution, cancellation, recovery, and unrecoverable termination.

The goal is not to predict every imaginable failure, but:

> **Identify failures that can materially affect correctness, execution, state, cost, safety, or termination, and define what the workflow should do about them.**

---

# 1. Position in the Architecture Process

This stage consumes the approved Problem Definition, Goal and Boundary, Process Architecture, Process Contracts, Flow Structure, State Model, Transition Model, Human Gates, Iteration Model, and Termination Conditions. It then asks: **What happens when assumptions fail?**

**Prerequisite chain:** See `00-problem-definition.md` §2.

---

# 2. Happy Path Is Not Enough

A workflow designed only around successful execution is incomplete. A real workflow must also account for invalid/missing/incomplete inputs, Analyze failing or producing unusable output, Generate failing or producing invalid output, Evaluate failing or rejecting, and Approve approving / requesting revision / rejecting / not responding.

> **Every meaningful Process boundary is also a potential failure boundary.**

# 3. Failure Planning Is Not Failure Prediction

Amsha should not attempt to predict every possible runtime failure. **Failure prediction** asks "What might happen?"; **failure planning** asks "If this happens, what should the architecture do?" — the second is the important architectural requirement.

---

# 4. Failure Categories

Failures should be classified to make reasoning systematic: `Input`, `Contract`, `Process`, `Output`, `Validation`, `Decision`, `Iteration`, `Human`, `State`, `External`, `Tool`, `Resource`, `Timeout`, `Concurrency`, `Recovery`, `System`. Categories can overlap — e.g. "External API timeout" is `External + Timeout + Recovery`.

# 5. Input Failures

Input failures occur before or at the beginning of a Process: missing required input, invalid format, malformed data, unsupported type, incomplete/contradictory information, empty input, unexpected input size, invalid reference. The architecture should determine whether Reject / Repair / Request clarification / Use default / Skip optional path / Escalate is appropriate. Do not silently invent critical missing information.

---

# 6. Required vs Optional Input Failure

Required and optional inputs must behave differently. If `source_document` (required) is missing: cannot execute the Process. If `style_reference` (optional) is missing: continue without it, unless the Process contract specifies otherwise. This distinction should be explicit.

# 7. Input Validation Boundary

Input validation should happen before expensive downstream execution (`START → Validate Input → Valid? NO→Input Error / YES→Process`). Do not allow malformed inputs to propagate through multiple Processes before discovering the problem. Where validation is deterministic (schema validation, file existence, required fields, type/range checking, reference existence), prefer deterministic validation.

---

# 8. Process Failure

A Process can fail even when its inputs are valid: runtime exception, LLM failure, invalid tool response, external dependency failure, resource exhaustion, unexpected internal state. The Flow must distinguish `Process succeeded`, `Process produced a valid negative result`, and `Process failed to execute` — these are not the same.

# 9. Failure vs Negative Result

This distinction is critical. `Evaluate Chapter` producing `evaluation_passed = false` is a **valid Process result** that transitions to `Improve Chapter`. But an evaluator crash is a **Process failure** that follows a failure path (`Evaluator → FAILED → Recovery/Retry/Escalation`). Do not treat runtime failure as a domain-level rejection.

# 10. Failure Taxonomy

A useful model of Process outcome: **SUCCESS** (completed with a valid successful result), **VALID NEGATIVE RESULT** (completed correctly but result does not satisfy the desired condition, e.g. `Evaluation = failed`), **RETRYABLE FAILURE** (temporary, may succeed on retry, e.g. temporary network failure), **RECOVERABLE FAILURE** (cannot continue directly but can recover through another path, e.g. invalid generated artifact), **TERMINAL FAILURE** (cannot continue meaningfully, e.g. required source does not exist).

---

# 11. Retry Planning

Retries should be intentional — do not automatically retry every failure. A retry is appropriate when the failure is likely transient, retry is safe, retry has a reasonable chance of success, retry cost is acceptable, and repeated execution does not create harmful side effects. (External Service → Timeout may warrant retry; invalid input retried identically usually does not help.)

# 12. Retry Limits

Every retryable failure should have bounded behavior (`retry: {max_attempts: 3}`): `Attempt 1…3 → Failure → Escalate / Terminal Failure`. Avoid unbounded automatic retries.

# 13. Retry vs Iteration

**Retry**: the Process failed to execute correctly (`Process → Execution Failure → Retry same Process`). **Iteration**: the Process executed successfully but its result requires additional work (`Generate → Evaluate → Not acceptable → Improve → Generate`). Do not confuse execution failure with valid domain-level rejection.

---

# 14. Output Failures

A Process can execute successfully but produce an invalid output (`Generate Chapter → Output → Schema Validation → Invalid`). The Flow must determine whether to retry generation, repair output, return to an earlier Process, request human review, or terminate. Output validation should occur at the Process boundary when the contract requires it.

# 15. Contract Violations

A Process output violates its contract when a required field is missing, or the structure/type/reference is wrong, or the result is incomplete or semantically unexpected. E.g. expected `chapter: {title: string, content: string}` but the Process produces `chapter: {content: ""}`. This should be detected before downstream execution.

---

# 16. Validation Layers

Failure planning should distinguish `Structural → Semantic → Business/Domain → Human Acceptance` validation (Schema Valid? → Semantically Valid? → Meets Domain Criteria? → Human Approved?). Failure at each level can require a different response.

# 17. Decision Failures

A Flow decision may fail because its decision input is missing, invalid, ambiguous, contradictory, or outside the expected range. E.g. an Evaluation Score expected 0–100 but received `null`. The Flow should not silently choose a branch — instead `Decision Failure → Retry / Repair / Escalate`.

# 18. Ambiguous Decisions

Some decisions cannot be safely determined automatically (e.g. two valid creative directions exist). The architecture may route `Automated Evaluation → Ambiguous → Human Review`, creating a controlled fallback from automation to human judgment.

---

# 19. Human Rejection

Human rejection is not necessarily a failure. `Human Review → REVISE` is a valid workflow outcome; `REJECT` may be a valid terminal state. The architecture must define the semantics: `APPROVE → continue`, `REVISE → improvement loop`, `REJECT → terminal rejection`.

# 20. Human Timeout

A human gate may remain unresolved. The architecture should define what happens. Possible policies: wait indefinitely, timeout, escalate, cancel, return to queue, notify. Do not invent a default behavior when the business requirement is unknown; if human responsiveness matters, define it explicitly.

---

# 21. External Dependency Failures

External systems add failure modes: API/MCP server/Tool unavailable, authentication failure, rate limit, network timeout, invalid external response, partial completion. The Flow should distinguish "request failed" from "request succeeded but response was not received" — the second may create a duplicate-execution risk.

# 22. Side Effects and Idempotency

Before retrying an external operation, determine whether it is safe to execute again. `Create Asset` may duplicate assets if blindly retried; better to `Check Operation Status → Already Completed? YES→Use Existing Result / NO→Retry`. Identify Processes with side effects (create, delete, publish, send, charge, deploy, modify, generate external artifact) — these require stronger retry and recovery planning.

# 23. Idempotency

A Process is idempotent when repeating it does not create an unintended additional effect. `Calculate Score` is naturally repeatable; `Publish Asset` may not be. Classify important Processes as `execution: {retryable: bool, idempotent: bool}` when known.

---

# 24. Partial Completion

A Process may perform part of its work before failing (e.g. `Generate Asset → Asset created → Metadata update fails`), leaving the system in a partial state. The architecture must determine whether to Rollback / Resume / Repair / Reuse partial result / Mark incomplete / Escalate. Partial completion is particularly important for external side effects.

# 25. State Failures

State can become invalid or inconsistent: missing/stale/contradictory state, corrupted checkpoint, unexpected state transition, or state from an incompatible workflow version. The Flow should not continue blindly when critical state invariants are violated — e.g. `current_process = evaluate` but `chapter_draft` does not exist is a state consistency failure.

# 26. State Invariants

Important state relationships should be defined as invariants, e.g.: if `current_process = evaluate` then `chapter_draft` must exist; if `approval.status = approved` then `evaluation.status` must be passed; if `revision_count > 0` then a previous evaluation must exist. These can often be validated deterministically.

---

# 27. State Recovery

When state is invalid, recovery may require Checkpoint Restore, Reconstruct State, Replay Process, Restart Process, Restart Workflow, Human Intervention, or Terminal Failure. The correct option depends on the workflow; do not assume restarting the entire Flow is always safe.

# 28. Checkpoint Planning

Failure planning should identify where recovery checkpoints matter. If P3 fails after `P1 → Checkpoint → P2 → Checkpoint → P3`, restore the checkpoint and resume from P3 rather than restarting P1/P2/P3. This is especially valuable for expensive LLM operations, long-running Processes, external operations, human approval boundaries, and large artifact generation.

---

# 29. Cancellation

The workflow should distinguish failure from cancellation (`RUNNING → CANCELLED`). Cancellation may be caused by user request, system shutdown, deadline, resource policy, or external event. The architecture should define whether cancellation stops immediately, finishes the current Process, performs cleanup, persists state, and/or allows resume.

# 30. Timeouts

Every potentially long-running operation (LLM call, External API, MCP operation, Human review, Asset generation, long-running Python operation) should be considered for timeout behavior. Timeout handling should define `timeout → retry? → fallback? → escalate? → terminate?`. Avoid treating timeout as automatically equivalent to failure when the underlying operation may still have completed.

# 31. Resource Failures

Resource failures include out of memory, disk/GPU unavailable, token budget exceeded, rate limit, execution quota exceeded, concurrency limit, storage limit. Identify resource constraints that can materially affect the workflow; possible responses: retry later, reduce workload, use fallback, queue, pause, escalate, terminate.

---

# 32. Token and Cost Failure

For LLM-based workflows, resource failure can include excessive token consumption — e.g. a repeated revision loop exceeding a token budget. The architecture should have a bounded policy: maximum iterations, maximum model calls, maximum context size, maximum workflow budget, human escalation. Cost control should be part of architecture where repeated/autonomous execution can otherwise grow without bound.

# 33. Loop Exhaustion

An iterative workflow must define what happens when the maximum iteration count is reached. Possible outcomes: return best result, human review, escalate, terminal failure. Never leave the result undefined.

# 34. Best-Result Preservation

When an iterative workflow generates progressively different candidates, it may be useful to retain the best valid result (e.g. Iteration scores 72/81/77 → best is Iteration 2). This is only appropriate when the Process contract defines a meaningful comparison criterion. Do not assume the latest result is always the best result.

---

# 35. Failure Severity

Failures should be classified by impact: `INFO`, `WARNING` (execution can continue safely), `RECOVERABLE` (requires recovery before continuing), `ERROR` (current Process cannot complete normally), `CRITICAL` (workflow integrity or correctness is compromised). Severity should be based on workflow impact, not merely technical exception type.

# 36. Failure Response Types

A failure plan can use a controlled set of responses: `IGNORE`, `RETRY`, `REPAIR`, `REPEAT_PROCESS`, `RETURN_TO_PROCESS`, `FALLBACK`, `WAIT`, `HUMAN_REVIEW`, `ESCALATE`, `ROLLBACK`, `RESUME`, `CANCEL`, `TERMINATE`. Choose the actual response according to failure semantics.

# 37. Failure Matrix

A useful planning artifact is a failure matrix making failure behavior explicit:

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

The exact schema can evolve; the important requirement is that failure behavior is explicit.

---

# 38. Failure Planning by Process

Each important Process should be reviewed individually: What can make this Process fail? What can make its output invalid or unusable? What happens if unavailable? Can it be retried? Is retry safe? Can it partially complete or be resumed? Does it require human intervention? What is the terminal failure? E.g. for P3 Generate Chapter, potential failures include model unavailable, invalid structured output, empty output, missing context, generation timeout, content failing validation, generation budget exhausted — each relevant case should have a response.

# 39. Failure Planning by Transition

Transitions also need failure analysis. E.g. for `P4 Evaluate → Pass?`, potential issues are evaluation missing/ambiguous/malformed, score outside expected range, or a condition that cannot be determined. The Flow should define what happens when the transition decision cannot safely be made.

# 40. Failure Planning by State

State should be reviewed for invalid combinations — e.g. `status = approved` but `draft = missing` should be impossible or explicitly recoverable. State invariants should therefore be included in failure planning.

---

# 41. Failure Planning by External Boundary

Every external boundary should be reviewed: What if unavailable, timeout, malformed response, operation succeeded but response lost, authentication fails, rate-limited, partial completion? Can the operation be retried safely? This becomes particularly important for Tools and MCP integrations later.

# 42. Failure Planning Does Not Mean Overengineering

Do not create elaborate recovery mechanisms for insignificant failures — use proportionality. A simple deterministic calculation may only require `exception → terminal Process failure`, whereas expensive external asset generation may require timeout, retry, operation status check, checkpoint, resume, and partial-result handling. The recovery architecture should reflect the consequences of failure.

# 43. Failure Priority

A useful reasoning heuristic is `Impact × Likelihood × Recovery Difficulty` (not necessarily a literal numeric score). Prioritize failures that are likely, expensive, difficult to recover, destructive, capable of corrupting state, capable of producing incorrect final output, or capable of causing unbounded execution.

---

# 44. Safety-Critical or High-Impact Decisions

Some workflows require stronger failure handling around decisions that materially affect people, systems, assets, or irreversible actions. For such decisions, `Automation → Validation → Human Review → Explicit Approval → Irreversible Action` may be preferable to fully autonomous execution. The appropriate level depends on the problem definition and requirements.

# 45. Failure Containment

A failure should affect the smallest appropriate scope. A P2 failure should not necessarily terminate the entire workflow if P2 can be independently retried or recovered. Prefer `Local Failure → Local Recovery → Continue` when safe; escalate to larger scopes only when necessary.

# 46. Failure Propagation

A failure can propagate downstream — e.g. P1's invalid output causes unexpected behavior in P2 then P3. The architecture should detect contract violations at the earliest boundary: prefer `P1 → Output Validation → FAIL` rather than allowing bad state to propagate.

---

# 47. Graceful Degradation

Some workflows can continue with reduced capability. An optional enrichment service unavailable may allow "continue without enrichment", while a required source unavailable may require termination. Classify dependencies as Required / Optional / Fallback-capable during failure planning.

# 48. Fallbacks

Fallback behavior must preserve the goal as much as possible (`Primary Process → Failure → Fallback Process`). A fallback is valid only when its output satisfies the downstream contract or the architecture explicitly accepts degraded output. Do not introduce a fallback simply because one exists.

# 49. Failure Recovery Flow

A generic recovery pattern: `Process → Failure → Classify → Retryable? YES→Retry (Success?→Continue / NO→Escalate) / NO→Recoverable? YES→Recovery / NO→Terminal Failure`. This is conceptual — each workflow should define only the branches it actually needs.

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

- **Happy-Path-Only Architecture** — `Input → Process → Success` with no failure paths considered.
- **Retry Everything** — any failure retried forever; causes infinite execution, unnecessary cost, duplicate side effects, resource exhaustion.
- **Treating Rejection as Failure** — "Evaluation failed" may be a valid result; do not automatically classify it as an execution error.
- **Silent Recovery** — something failed then the system silently does something else; recovery behavior should be explicit and traceable.
- **Giant Error Handler** — any error funneled into one generic recovery mechanism; different failures require different responses.
- **Failure Handling Inside Every Process** — don't duplicate the entire recovery framework inside every Process; separate `Process Contract` from `Flow-level failure policy` while retaining Process-specific recovery requirements.
- **Overengineering** — don't design distributed recovery infrastructure for a simple deterministic Process; recovery complexity should be proportional to Failure Impact + Likelihood + Recovery Difficulty.

---

# 55. Relationship to Later Capability Selection

Failure planning helps determine which capabilities are actually required: need deterministic validation → Python may be sufficient; need external system recovery/status → Tool/MCP may be required; need human approval → human interaction mechanism required; need persistent recovery → checkpointing/persistence required. However, this stage should identify the **requirement**, not prematurely choose the implementation. The next stage, `07-capability-selection.md`, makes those decisions.

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

At the end of this stage, Amsha should understand not only "what happens when everything works?" but also what happens when input is invalid, Process fails, output is invalid, validation rejects, decision is ambiguous, iteration never succeeds, human rejects or does not respond, external system fails, operation partially completes, state becomes inconsistent, retry is unsafe, a checkpoint must be restored, or the workflow is cancelled.

The resulting architecture becomes: `Problem → Goal → Processes → Contracts → Validation → Flow → State → Corner Cases → Failure Paths → Recovery / Escalation / Termination`. Only after this should Amsha determine the minimum implementation capabilities required.

The next stage is **07-capability-selection.md**, which answers:

> **Given the validated Process, Flow, State, and Failure architecture, what is the least powerful implementation mechanism required for each part?**
