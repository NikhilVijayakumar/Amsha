#  Amsha Prerequisite: Architecture Validation

## Purpose

The prerequisite stages establish the architecture progressively: `Problem → Goal & Boundary → Process Decomposition → Process Contracts & Atomicity → Process Validation & Human Review → Flow & State Planning → Corner Cases & Failure Planning → Capability Selection → Architecture Validation`.

This document defines the **final validation gate before implementation engineering**. It determines whether the complete architecture is: correct enough to implement, complete enough to execute, internally consistent, appropriately scoped, operationally feasible, sufficiently resilient, minimal without being insufficient, understandable by humans, and implementable using the selected capabilities.

The central question:

> **Does the selected architecture reliably transform the defined starting condition into the defined successful end state, including meaningful alternate and failure paths, using the minimum sufficient capabilities?**

This is not yet code validation — it is **architecture validation**.

> Stage 04 validates the *process graph alone* (before Flow and capabilities exist). Stage 08 validates the *complete architecture* (processes + flow + state + capability selection together). They serve different purposes in the prerequisite pipeline.

---

# Complexity Threshold

For simple workflows, the full prerequisite pipeline may be compressed. After completing stages 00–03, teams may skip directly to stage 07 (Capability Selection) if ALL are true: Process graph is sequential (no branching); no iteration or retry paths required; no human approval gates; no parallel execution; all processes deterministic or single-LLM-call.

Stages 04–06 add significant value for complex workflows but are overhead for simple ones. The minimum viable path: `00 → 01 → 02 → 03 → 07 → 08`. When in doubt, complete all stages.

---

# 1. Position in the Architecture Lifecycle

The complete prerequisite layer is `00 Problem Definition → 01 Goal & Boundary → 02 Process Decomposition → 03 Process Contracts & Atomicity → 04 Process Validation & Human Review → 05 Flow & State Planning → 06 Corner Cases & Failure Planning → 07 Capability Selection → 08 Architecture Validation`, then **IMPLEMENTATION ENGINEERING** (Agent, Task, Crew, Flow, Knowledge, Memory, Tools, MCP, Files, Reasoning, Planning, Checkpointing, Observability → Implementation).

The critical boundary:

> **No implementation architecture should be considered final until the prerequisite architecture passes this validation stage.**

---

# 2. What Architecture Validation Means

Architecture validation verifies that all previous decisions work together — the relationship between `Problem, Goal, Processes, Contracts, Flow, State, Failure Handling, Capabilities`. A locally valid Process, Flow, or Agent is not enough; the complete architecture must be coherent.

Example:

```text
Process requires: "character_profile"
but Flow provides: "character_names"
```

Each component may appear reasonable, yet the architecture is invalid because the contracts do not connect.

---

# 3. Architecture as a Transformation

The architecture should be understandable as: `START CONDITION → INPUT → TRANSFORMATIONS → DECISIONS → ITERATIONS / BRANCHES → VALIDATION / HUMAN REVIEW → SUCCESS STATE`. The validator must verify the complete structure can actually establish the defined end goal.

A useful conceptual model:

```text
Start → Can execution begin? → Can every required transformation occur? →
Can every required decision be made? → Can failures be handled? →
Can the workflow terminate correctly? → Does termination establish the goal?
```

---

# 4. Architecture Validation Dimensions

The final validation should cover:

```text
1. Problem Alignment            6. Flow Correctness        11. Capability Sufficiency     16. Observability
2. Goal Alignment               7. State Correctness       12. Capability Minimality      17. Recoverability
3. Boundary Alignment           8. Transition Correctness  13. Determinism                18. Termination
4. Process Completeness         9. Failure Coverage        14. Resource Feasibility       19. Traceability
5. Contract Consistency        10. Human Review Correctness 15. Security / Permissions    20. Overall Simplicity
```

Not every dimension must have equal depth — the validator should be proportional to the architecture's complexity and risk.

---

# 5. Validation Layers

Architecture validation should proceed in layers:

```text
Structural → Contract → Graph → Semantic → Failure → Capability → Operational → Human Review → Final Approval
```

The principle:

> **Cheap, deterministic checks should run before expensive semantic evaluation.**

---

# 6. Layer 1 — Structural Validation

Structural validation verifies the architecture is well formed. Check: required architecture sections exist; Process IDs unique; capability IDs valid; references resolve; required fields exist; transitions reference valid nodes; state fields valid; human gates reference valid transitions; failure cases reference valid Processes; capability mappings reference valid elements.

Example: `Process P3 depends_on: P9` — if P9 does not exist → **ERROR**; the architecture should not proceed to expensive semantic validation.

---

# 7. Layer 2 — Problem Alignment

Verify the architecture still solves the original problem. Ask "What problem does this architecture solve?" then "Can every major architectural decision be traced back to that problem?" Detect architecture solving a different problem, unnecessary scope expansion, missing problem requirements, capabilities unrelated to the problem, Processes that do not contribute. The architecture must not drift during decomposition.

---

# 8. Layer 3 — Goal Alignment

Verify the architecture can establish the defined goal. Trace `Start State → Process Outputs → Flow Decisions → Final State`, then ask "Does the final state actually satisfy the goal?" — stronger than asking whether the final Process completed.

Example: `Process: Generate Chapter`, `Goal: Produce an approved chapter`. Generating is not sufficient; the architecture may require `Generate → Validate → Evaluate → Human Approval → Approved Chapter`.

---

# 9. Layer 4 — Boundary Alignment

Verify the architecture stays within the approved boundary: included work is implemented, excluded work is not accidentally implemented. Also verify external dependencies. Example: workflow owns `Chapter generation` but not `Publishing final book` — the architecture should not silently expand into publishing.

---

# 10. End-to-End Traceability

Every important requirement should have a trace: `Requirement → Process → Contract → Flow → Capability → Validation → Outcome`.

Example: `Requirement: Chapter must satisfy character continuity → Process: Evaluate Chapter → Contract: character_consistency_result → Flow: failure → improve chapter → Capability: Character specialist / evaluation Crew → Outcome: Approved chapter`. If a requirement has no implementation path, the architecture is incomplete.

---

# 11. Process-to-Flow Consistency

Every approved Process should have a valid place in the Flow: `Process exists → Flow invokes it → Required inputs available → Output stored/consumed → Completion transition defined`. Detect:

- **Orphan Process** — Process exists but Flow never executes it.
- **Missing Process** — Flow expects work but no Process provides it.
- **Duplicate Process** — same responsibility twice without architectural justification.

---

# 12. Contract Consistency

Verify the entire producer-consumer chain (`P1 Output → P2 Input → P2 Output → P3 Input`). Check structure, semantics, required fields, completeness, naming, ownership, availability. **A downstream Process must never depend on information the architecture cannot provide.**

---

# 13. Flow Correctness

The Flow must correctly represent sequence, conditions, parallelism, iterations, human gates, termination, and recovery boundaries. Example: `Evaluate → Pass? {YES → Approve, NO → Improve}` — the condition must be derived from a valid state value. If `Pass?` has no defined source, the Flow is incomplete.

---

# 14. State Correctness

State should be validated against the Flow. Ask: Does every required transition have the state it needs? Can state become contradictory? Are important fields owned? Are large artifacts unnecessarily embedded? Is state larger than necessary? Can the workflow resume from required checkpoints? Is current state distinguishable from historical state?

Example invariant: `If current_process = evaluate then chapter_draft exists`. If this cannot hold reliably, the architecture requires correction.

---

# 15. State and Context Consistency

Do not confuse `Flow State` with `LLM Context`. Validate that each Process receives the information required by its contract without automatically receiving the entire state: `Flow State → Relevant Context Selection → Process`. This protects token efficiency, relevance, privacy, and reasoning quality.

---

# 16. Failure Coverage

Every important Process and transition should have meaningful failure behavior. The validator should ask: What happens if this Process fails? Output invalid? Dependency unavailable? Decision cannot be made? Iteration never succeeds? A failure path should eventually reach `Recovery / Retry / Fallback / Human Review / Escalation / Terminal Failure`, rather than becoming undefined execution.

---

# 17. Failure Completeness

Failure planning need not cover every theoretical exception; verify meaningful failure classes are covered — required input unavailable, LLM unavailable, Tool unavailable, external service timeout, invalid output, contract violation, human rejection, iteration exhaustion, state inconsistency, cancellation. The required set depends on the architecture.

---

# 18. Retry Safety

Every retryable operation should be checked for retryability, idempotency, side effects, maximum attempts, termination behavior. Example: `External Create Operation → Timeout → Retry?` — the architecture must determine whether the original operation may already have succeeded; blind retrying may create duplicates.

---

# 19. Human Review Consistency

Verify every required human decision has a clear trigger, defined input, explicit decision, defined outcomes, state representation, and continuation behavior. Example: `Human Review → {YES → Next, REV → Loop, NO → Reject}`. The architecture should not contain an implicit human dependency.

---

# 20. Capability Sufficiency

The selected capabilities must be sufficient to implement the approved architecture. For each requirement ask: `Requirement → Selected capability → Can it actually satisfy the requirement?` Example: `Multi-specialist collaboration → Agent only` may be insufficient; `Deterministic score calculation → Crew` may be unnecessarily powerful but technically sufficient. The validator should distinguish `INSUFFICIENT / SUFFICIENT / OVERPOWERED / UNNECESSARY`.

---

# 21. Capability Minimality

After checking sufficiency, check whether capabilities can be removed. For each: `Remove capability → Does any requirement become unsatisfied?` If NO, the capability may be unnecessary. Example: `Planning` selected but the Flow sequence is completely predefined → Planning may have no architectural justification.

---

# 22. Capability Conflicts

Some combinations create unnecessary complexity and should be flagged for review: `Flow + autonomous Planning` when the workflow is deterministic; `Memory + Flow State` where Memory only passes current execution data; `Crew + single professional capability` where no collaboration is required.

---

# 23. Determinism Validation

Prefer deterministic mechanisms for validation, calculation, routing, state transitions, schema checking, threshold decisions, data transformation. Prefer LLM-based capabilities for interpretation, generation, creative reasoning, semantic judgment, professional analysis. The architecture should not introduce probabilistic behavior where deterministic behavior is sufficient.

---

# 24. Probabilistic Boundary

LLM behavior should have explicit architectural boundaries:

```text
LLM → Structured Output → Deterministic Validation → Flow Decision
```

rather than:

```text
LLM → LLM interprets result → LLM decides branch → LLM decides next step
```

The latter creates unnecessary uncertainty. Amsha should prefer:

> **Probabilistic intelligence inside deterministic orchestration.**

---

# 25. Context Efficiency Validation

Validate that the architecture does not unnecessarily move large amounts of information between Processes. Check: unnecessary context duplication, repeated large Knowledge injection, unnecessary historical context, repeated artifact content, excessive Flow state, redundant Task examples, unnecessary Agent backstory detail. The objective is not minimum text at any cost — it is **minimum sufficient information for reliable execution**.

---

# 26. Resource Feasibility

The architecture should be operationally plausible. Consider LLM calls, token usage, expected iterations, tool calls, external operations, latency, storage, GPU/CPU requirements, concurrency, human waiting periods. Example: `Maximum revisions = 20` may be technically valid but operationally expensive — if `expected LLM calls per iteration = 8`, then `20 × 8 = 160 calls` requires architectural review. Exact budgeting can be handled later, but obvious runaway execution should be caught here.

---

# 27. Unbounded Execution

The validator should reject or flag `while condition: continue` when no meaningful termination condition exists. Every retry, loop, autonomous planning cycle, polling operation, human wait, and recursive execution should have appropriate bounds or an explicit externally controlled termination mechanism.

---

# 28. External Capability Validation

For each external dependency: `External Requirement → Tool / MCP → Capability Available? → Failure Path? → Recovery?`. Validate: dependency exists, capability sufficient, permissions appropriate, timeout behavior exists, failure behavior exists, side effects understood, retry behavior safe. The architecture should not depend on an external capability that has not been accounted for.

---

# 29. Security and Permission Validation

Capability selection should be reviewed for excessive authority. `Agent → Tool → Delete Production Asset` requires stronger controls than `Agent → Read Documentation`. Validate capability scope, data access, write access, destructive operations, external boundaries, human approval requirements. The principle:

> **A capability should have no more authority than its Process requires.**

---

# 30. Observability Validation

The architecture should define enough observability to understand execution: workflow/Process execution, state transitions, failures, retries, human decisions, LLM calls, tool calls, external operations, artifacts, latency, token/cost. Observability should support debugging, evaluation, performance analysis, failure investigation, and architecture improvement. Do not instrument everything indiscriminately — observe what is useful.

---

# 31. Recoverability Validation

For workflows requiring recovery, verify `Checkpoint → State → Resume Boundary → Process`. Ask: What happens after process failure? What state is preserved? Can execution resume? Can external operations be reconciled? Can a human continue a paused workflow? Can a failed Process be restarted independently? **A workflow that claims to be resumable must retain sufficient state to actually resume.**

---

# 32. Termination Validation

Every path should eventually terminate meaningfully: success, failure, rejection, cancellation, iteration exhaustion, human timeout, external dependency exhaustion — each with defined semantics. Detect dead ends, infinite loops, undefined branches, unhandled failures, and approval states with no continuation.

---

# 33. Architecture Simplicity

Review for unnecessary complexity. Ask "Can this architecture be simplified without losing required behavior?" Potential simplifications: remove Agent/Crew/Flow/Memory/Knowledge/Tool/MCP/Planning, merge unnecessary Processes, remove unnecessary state/transitions. Simplification is not minimizing everything — the target is `Minimum sufficient architecture`, not `Minimum possible architecture`.

---

# 34. Minimum Sufficient Architecture

A good architecture satisfies `Correctness + Completeness + Reliability + Required intelligence + Required orchestration + Required external access + Required human judgment` with `minimum unnecessary complexity`. Conceptually: `Required Capability → Minimum sufficient mechanism → Validated Architecture`.

---

# 35. Architecture Consistency Matrix

A useful validation artifact is a cross-layer matrix ensuring no requirement is represented in only one layer (columns can evolve):

| Requirement        | Process | Flow          | State          | Failure Plan    | Capability  | Validation    |
| ------------------ | ------- | ------------- | -------------- | --------------- | ----------- | ------------- |
| Source analysis    | P1      | P1 transition | analysis       | retry/fail      | Agent       | semantic      |
| Chapter generation | P3      | P3 transition | draft          | regenerate      | Agent       | schema        |
| Quality evaluation | P4      | decision      | evaluation     | retry           | Crew        | semantic      |
| Revision           | P5      | loop          | revision count | max iterations  | Agent       | quality       |
| Final approval     | H1      | human gate    | approval       | timeout/reject  | Human       | human         |
| Final artifact     | P6      | terminal      | artifact ref   | storage failure | Python/Tool | deterministic |

---

# 36. Cross-Layer Traceability

Every important requirement should have a complete chain: `Requirement → Process → Contract → Flow → State → Failure Handling → Capability → Validation`.

Example: `Requirement: Final chapter must be approved → Process: Generate/Evaluate Chapter → Flow: Evaluation → Human Approval → State: approval.status → Failure: Human rejection → Revision → Capability: Human Review → Validation: approval.status == approved`. This is a strong architectural trace.

---

# 37. Architecture Validation Findings

Findings should be structured with severity:

- **ERROR** — architecture must change before implementation (missing required capability, broken contract, unreachable goal, undefined transition, unhandled terminal path, insufficient state).
- **WARNING** — may work but deserves review (unnecessary Crew, large context, questionable retry, unnecessary dependency, weak recovery strategy).
- **NOTE** — informational observation (possible simplification, possible parallelism, future optimization).

---

# 38. Overall Architecture Status

Recommended states: `DRAFT → VALIDATING → {Findings} → ERROR? {YES → CHANGES_REQUIRED, NO → Human Review Required? {YES → REVIEW_REQUIRED → APPROVAL, NO → APPROVED}}`.

---

# 39. Human Architecture Review

For meaningful architectures, Amsha should support a final human review. The reviewer should see `Problem, Goal, Process Graph, Flow Graph, State Model, Failure Plan, Capability Map, Validation Findings` — not implementation code. The key question:

> **Would I approve this architecture for implementation?**

---

# 40. Architecture Approval

Approval should mean all of: Problem understood, Goal bounded, Processes complete, Contracts valid, Flow coherent, State sufficient, Failure paths planned, Capabilities sufficient, Capabilities minimal, Architecture feasible, Required human review complete → **APPROVED FOR IMPLEMENTATION**. Approval should be explicit.

---

# 41. No Silent Architecture Changes

Once validation begins, the validator should not silently redesign the architecture. If it finds `P3 requires character_profile but no Process produces it`, it should report:

```yaml
finding:
  severity: ERROR
  category: contract
  message: "Required input character_profile has no valid producer."
  recommendation: "Modify an upstream contract or introduce the missing transformation."
```

It should not silently add a Process. This preserves traceability, human control, reproducibility, and architecture history.

---

# 42. Auto-Correction

Amsha may eventually support explicitly authorized architecture correction as a **separate mode**: `VALIDATE → FINDING → PROPOSE CHANGE → AUTHORIZED? → APPLY → VALIDATE AGAIN`. Never `VALIDATE → SILENTLY MODIFY → APPROVED`.

---

# 43. Architecture Versioning

Validated architectures should be versionable:

```yaml
architecture:
  id: "chapter-generation"
  version: "1.2"
  status: "approved"
```

If an approved Process changes: `v1.0 → Change → Validation → v1.1`. Do not treat implementation changes as architecture changes automatically; only changes affecting architectural behavior require architectural revalidation.

---

# 44. Change Impact

When architecture changes, determine what must be revalidated. Example: `Change: P4 evaluation contract changed` → potential impact includes P5 input, Flow decision, State, Failure paths, Capability mapping, Validation criteria. Amsha should eventually support dependency-aware revalidation: `Changed Component → Dependency Graph → Affected Components → Selective Revalidation`. This avoids revalidating the entire architecture for every minor change.

---

# 45. Architecture Validation Output

The final artifact should be machine-readable:

```yaml
architecture_validation:
  status: ""
  architecture:
    problem_id: ""
    version: ""
  structural:
    valid: false
    findings: []
  alignment:
    problem: ""
    goal: ""
    boundary: ""
  processes:
    completeness: ""
    contracts: ""
    atomicity: ""
  flow:
    valid: false
    transitions: ""
    termination: ""
  state:
    valid: false
    invariants: []
    sufficiency: ""
    minimality: ""
  failures:
    coverage: ""
    recovery: ""
    retry_safety: ""
  human_review:
    required: false
    completed: false
    decision: ""
  capabilities:
    sufficient: false
    minimal: false
    rejected: []
  operational:
    resource_feasibility: ""
    observability: ""
    recoverability: ""
  security:
    status: ""
    findings: []
  traceability:
    requirements: []
    uncovered: []
  findings:
    - id: ""
      severity: ""
      category: ""
      component: ""
      message: ""
      recommendation: ""
  approval:
    status: ""
    reviewer: ""
    notes: []
  implementation_ready: false
```

The schema is conceptual and should evolve with Amsha implementation requirements.

---

# 46. Architecture Readiness Gate

The most important output is `implementation_ready: true`, only possible when all mandatory requirements pass: `Architecture Validation → Mandatory checks pass? → Required human review complete? → No unresolved ERROR findings? → Capability set sufficient? → Termination valid? → IMPLEMENTATION READY`.

---

# 47. What Implementation-Ready Means

Implementation-ready does **not** mean code already exists, every implementation detail is predetermined, every CrewAI API selected, every Agent prompt written, every Task written. It means:

> **The problem and execution architecture are sufficiently understood that implementation can begin without discovering fundamental workflow-design problems.**

Implementation engineering can still make local decisions.

---

# 48. What This Stage Must Not Do

Architecture validation must not become implementation generation. Do not generate Agent prompts, Task descriptions, Crew YAML, Flow Python, select exact LLM models, or write MCP server code — unless explicitly requested as a later implementation step. This document establishes the gate before those activities.

---

# 49. Example — Final Validation

Consider `Goal: Produce an approved chapter`. Architecture: `P1 Analyze Source → P2 Define Requirements → P3 Generate Chapter → P4 Evaluate → Pass? {NO → P5 Improve → P3, YES → H1 Human Approval → {APPROVE? YES → SUCCESS, REVISE → P5, REJECT → REJECTED}}`.

State:

```yaml
current_process: ""
analysis: {}
requirements: {}
draft_ref: ""
evaluation: {}
revision_count: 0
approval_status: ""
```

Capabilities: `Flow, Agent + Task, Crew, Python, Knowledge, Human Review, Observability`.

Validation asks: Does this solve the stated chapter-production problem? Does SUCCESS mean an approved chapter actually exists? Are analysis, requirements, generation, evaluation, improvement, and approval represented? Does every Process receive what it needs? Are revision and approval branches explicit? Can the workflow resume after human approval? What happens if generation fails? What happens after maximum revisions? Is Crew genuinely required for evaluation? Is Memory actually required (if not → remove)? Can the pass/fail threshold be evaluated with Python (if yes → `LLM routing remove, Python decision use`)? If all mandatory checks pass → **APPROVED FOR IMPLEMENTATION**.

---

# 50. Full Prerequisite Architecture

The complete Amsha prerequisite layer:

```text
00 Problem Definition     What problem must be solved?
01 Goal & Boundary        What is the desired end state and scope?
02 Process Decomposition  What meaningful work must happen?
03 Process Contracts      What does each Process require/produce?
04 Process Validation     Is the Process architecture correct?
05 Flow & State           How does execution move and what persists?
06 Corner Cases & Failure What happens when the path breaks?
07 Capability Selection   What is the minimum sufficient mechanism?
08 Architecture Validation Does everything work as one architecture?
        ↓
IMPLEMENTATION READY
```

---

# 51. Architecture Governor Model

This prerequisite layer establishes an important role for Amsha: it should not merely generate CrewAI code — it should act as an **Architecture Governor**.

```text
User Problem → Amsha Architecture Reasoning → Problem → Goal → Processes →
Contracts → Flow → State → Failure → Capabilities → Architecture Validation →
IMPLEMENTATION CONTRACT → CrewAI / Amsha Engineering
```

This prevents the implementation layer from becoming the place where fundamental architecture decisions are accidentally made.

---

# 52. Boundary Between Prerequisite and Engineering

The prerequisite layer answers **"WHAT SHOULD EXIST?"**; the engineering layer answers **"HOW SHOULD IT BE IMPLEMENTED?"**

Example: Prerequisite states `Process: Evaluate Chapter, Requirement: Multiple independent professional perspectives`. Engineering then produces `Crew: Story Evaluation Crew, Agents: Story Editor / Character Specialist / Continuity Specialist, Tasks: ...`. The second should only be generated after the first is approved.

---

# 53. Core Amsha Rules

1. > Validate the complete architecture, not isolated components.
2. > The architecture must trace from the original problem to the successful end state.
3. > Every important requirement must have an architectural path to implementation and validation.
4. > Every Process must have a valid place in the Flow.
5. > Every Process contract must be compatible with its producers and consumers.
6. > State must be sufficient but minimal.
7. > Meaningful failure paths must be explicitly handled.
8. > Retries and iterations must be bounded and semantically justified.
9. > Selected capabilities must be sufficient and no more powerful than necessary.
10. > Deterministic behavior should remain deterministic whenever possible.
11. > Probabilistic intelligence should be bounded by deterministic architecture.
12. > External capabilities require explicit dependency and failure reasoning.
13. > Human decisions must be explicit architectural boundaries.
14. > Architecture validation must not silently redesign the architecture.
15. > No unresolved critical architecture finding should pass the implementation gate.
16. > Implementation readiness is an explicit architectural state.
17. > Capability selection should optimize for minimum sufficient complexity, not minimum feature count.
18. > The architecture must remain understandable without requiring implementation details.

---

# 54. Final Prerequisite Contract

After `08-architecture-validation.md`, Amsha should be able to produce an architecture contract approximately equivalent to:

```yaml
architecture:
  problem: {}
  goal_boundary: {}
  processes:
    decomposition: {}
    contracts: {}
    validation: {}
  flow:
    structure: {}
    transitions: {}
  state:
    model: {}
    invariants: {}
  failures:
    cases: {}
    recovery: {}
  capabilities:
    selected: {}
    rejected: {}
  validation:
    status: approved
    findings: []
  approval:
    status: approved
  implementation_ready: true
```

This becomes the **source of truth for implementation engineering**.

---

# 55. Final Principle

The complete prerequisite methodology can be summarized as:

```text
UNDERSTAND → BOUND → DECOMPOSE → CONTRACT → VALIDATE → ORCHESTRATE →
PLAN STATE → PLAN FAILURE → SELECT CAPABILITIES → VALIDATE AGAIN →
APPROVE → IMPLEMENT
```

Or, more simply:

> **Understand the problem before designing the workflow.
> Design the workflow before selecting capabilities.
> Select capabilities before implementing them.
> Validate the complete architecture before writing production code.**

This completes the **Amsha prerequisite architecture layer**. The next layer can therefore begin with the implementation-engineering rules for **Agent, Task, Crew, Process, and Flow**, using the validated architecture as its input rather than rediscovering the architecture during implementation.