#  Amsha Prerequisite: Process Validation and Human Review

## Purpose

Process decomposition identifies the work; Process contracts define what each accepts, transforms, and produces. This document defines how those Processes are **validated before they become an executable workflow** — ensuring work is complete, boundaries appropriate, inputs/outputs compatible, dependencies correct, unnecessary Processes removed, missing ones identified, human decisions explicit, and the graph can achieve the goal.

The output is a **validated Process architecture** ready for Flow and state planning.

---

# 1. Position in the Architecture Process

This stage is intentionally before Flow, Crew, Agent, Task, Tool, or MCP design. The question is still "Is this the correct work structure?" — not "How should this be implemented?"

**Prerequisite chain:** See `00-problem-definition.md` §2.

---

# 2. What Process Validation Means

Process validation verifies that the proposed Process architecture is logically capable of achieving the defined goal. A Process architecture is valid when: the workflow starts from a valid start condition, required inputs are available, every necessary transformation is represented, contracts are coherent, dependencies are valid, outputs satisfy downstream inputs, the graph reaches the end state, no critical work is missing, no unnecessary work is included, boundaries remain understandable, human decisions are explicit, termination conditions are meaningful, and the architecture is implementation-independent.

It is a **logical architecture review**, not a CrewAI configuration review.

---

# 3. Validation Inputs

Process validation consumes the outputs of the previous stages: problem statement, start condition, required inputs, desired end state, success conditions, boundaries, scope, Process list, relationships, contracts, dependencies, outputs, consumers, human-approval requirements, and assumptions. It should **not** require Agent/Task/Crew definitions, Flow implementation, LLM selection, model config, tool selection, MCP config, or Python implementation.

---

# 4. Validation Dimensions

The primary validation dimensions: Goal Coverage, Boundary Compliance, Process Necessity, Process Completeness, Contract Validity, Contract Compatibility, Dependency Validity, Graph Reachability, Atomicity, Responsibility Separation, Human Decision Placement, Termination, and Reviewability.

---

# 5. Goal Coverage

Every Process must contribute to achieving the defined goal. For each Process ask: **Why does this Process exist?** then **How does its output contribute to the final goal?** A Process that cannot establish a meaningful relationship with the goal is suspicious (e.g. "P6 Generate Random Metadata" would require strong justification).

---

# 6. Process Necessity

Every Process must pass the necessity test: **If this Process were removed, could the workflow still achieve its goal?** Three outcomes:

- **Necessary** — removing it makes the workflow unable to satisfy the goal (e.g. `P1 → P2 → P3`, P2 required for P3).
- **Conditionally Necessary** — required only under specific conditions (e.g. a `Decision` splitting `P2`/`P3`); valid when the condition is meaningful.
- **Unnecessary** — does not materially contribute; normally removed.

---

# 7. Process Completeness

Necessity alone is not enough — the architecture must also identify missing work. Ask: **What must happen between the start condition and the end condition?** Trace the transformation forward; if an essential transformation is missing, the architecture is incomplete. E.g. `Input → Generate → END` may be insufficient when the goal requires `Input → Analyze → Generate → Validate → Approve → END`.

Distinguish genuinely missing work from optional work, work that belongs inside an existing Process, and implementation detail. Do **not** create a new Process merely because a missing action can be described as a separate technical step.

---

# 8. Start-to-End Traceability

The entire architecture must be traceable from start to end condition: what enters, what happens to it, what changes, what information is produced, where it goes, and what eventually establishes the goal. Every terminal Process contributes to a valid termination condition; every required Process is reachable from the start; every required output has a consumer or contributes directly to the goal.

---

# 9. Contract Validation

Each Process contract must be checked independently: Purpose, Input, Transformation, Output, Preconditions, Postconditions, Completion, Dependencies, Consumers. Detect: missing required input, undefined output, vague transformation, contradictory preconditions, impossible postconditions, completion criteria unrelated to the Process, dependency on unavailable information, output without a consumer, consumer requiring unproduced information. A Process is not valid merely because it sounds reasonable — its contract must be executable as a logical specification.

---

# 10. Contract Compatibility

Producer and consumer contracts must be compatible. Compatibility includes required information, semantic meaning, structure, completeness, availability, and timing.

`P1 → character_analysis → P2` is compatible; `P1 → character_names → P2 (complete_character_psychology)` is not automatically. Fix by: changing P1's output, changing P2's input, introducing the missing transformation, or establishing that P2 derives the required information from another valid source.

---

# 11. Dependency Validation

Dependencies should represent genuine logical requirements. `P2 depends on P1` is valid only when P2 cannot correctly operate without P1's output; invalid when P2 could operate independently. Unnecessary dependencies reduce parallelism, flexibility, fault isolation, and efficiency. **Dependency must represent necessity, not convenience.**

---

# 12. Parallelism Validation

Processes should be independent when their work is independent. If P2 and P3 require only P1's output and not each other, they may be parallel — do not introduce artificial sequential ordering (`P1→P2→P3→P4`) when the actual graph is `P1→P2, P1→P3 → P4`. However, establish parallelism from logical dependency, not from a desire to optimize execution prematurely.

---

# 13. Conditional Process Validation

Conditional branches must have explicit reasons. The decision must specify: what condition is evaluated, what determines each branch, what each branch means, whether branches converge, and whether a branch can terminate. Avoid vague branches (`if needed`, `if appropriate`, `if necessary`) unless the criterion has a defined evaluation.

---

# 14. Iteration Validation

Iterations must have a meaningful purpose and termination condition. The architecture should define: what is evaluated, what constitutes success, what causes another iteration, maximum/bounded iteration behavior, and what happens if the criteria are never satisfied. Do not allow an implicit infinite loop.

---

# 15. Process Atomicity Revalidation

Validation verifies that proposed boundaries still make sense when viewed as a whole architecture: Does the Process still have one primary responsibility? one coherent transformation? one coherent primary result? Can it be evaluated independently? Does it contain unrelated responsibilities? Does it create an unnecessary dependency between unrelated activities? A Process may appear atomic alone but questionable beside its neighbors.

---

# 16. Responsibility Separation

Two Processes should not perform substantially overlapping responsibilities unless intentional. `P2 Analyze Character` + `P3 Evaluate Character` may be valid (understand vs. judge against criteria), but `P2 Analyze Character` + `P3 Analyze Character Again` requires justification. Overlap can indicate duplicated work, unclear boundaries, missing specialization, or accidental repeated processing.

---

# 17. Human Review

Human review is an explicit architecture mechanism, not an informal instruction ("someone should check this later"). Define the review boundary explicitly (`Process A → Human Review → Approved? YES→Process B / NO→Revision`). A human review point should identify: what is reviewed, why human judgment is required, what information the human receives, what decision they make, possible decisions, what happens after each, and whether review is mandatory or optional.

---

# 18. When Human Review Is Appropriate

Human review is valuable when correctness cannot be adequately determined through deterministic validation, or the decision carries meaningful subjective or external consequences. Examples: creative approval, final editorial judgment, ambiguous interpretation, high-impact decisions, acceptance of externally visible output, approval of major architecture changes, resolving conflicts between valid alternatives. Do not add human review merely because automation feels uncertain — place it at a meaningful decision boundary.

---

# 19. Human Review vs Validation

These are different mechanisms. **Automated Validation** answers "Does the output satisfy defined rules or criteria?" (fields present, schema valid, references valid, length within limits). **Human Review** answers "Is this acceptable given human judgment, intent, taste, context, or responsibility?" (does this feel emotionally correct, is this creative direction acceptable). They may coexist (`Process → Automated Validation → Pass? NO→Revision / YES → Human Review → Approved? NO→Revision / YES→Continue`). Prefer deterministic validation wherever sufficient; use human review where judgment adds value.

---

# 20. Human Review as a Process Boundary

A human review can create a real workflow boundary (`P1 Analyze Source → P2 Generate Proposal → H1 Human Review → P3 Produce Approved Output`). The review is not necessarily an implementation Process — it is a **decision boundary** in the architecture — but the architecture must still represent its inputs, decision, and consequences.

---

# 21. Design Review vs Runtime Review

Two different kinds of human review must be distinguished. **Design Review** occurs before execution, validating the architecture itself (correct Processes, missing work, appropriate boundaries, correct dependencies, understandability, correctly placed approval points). **Runtime Review** occurs during execution, validating/approving an actual Process output (approve/reject/revise). Do not confuse the two.

---

# 22. Human Review Should Be Explicit

Avoid architectures that depend on hidden human intervention. Bad: `Generate Output → Someone checks it → Continue`. Better: `Generate Output → Human Review → Decision {Approve / Request Revision / Reject}`. The explicit form makes the workflow understandable, testable, auditable, implementable, and recoverable.

---

# 23. Review Outcomes

Human review should define meaningful outcomes: `APPROVE`, `REVISE`, `REJECT`, `ESCALATE`. Not every workflow needs all of them — the important requirement is that each outcome has a defined consequence.

---

# 24. Validation Severity

Validation findings should be classified: **ERROR** (architecture cannot reliably achieve its goal — missing required Process, broken contract, unreachable terminal, incompatible contracts, impossible dependency, undefined required decision, missing termination; execution should not proceed), **WARNING** (may work but has a meaningful design concern — unnecessary dependency, questionable boundary, duplicate transformation, excessive granularity, weak criteria; reviewer should examine), **NOTE** (informational — possible parallelism, optional simplification, possible optimization; no change required).

---

# 25. Validation Should Be Deterministic Where Possible

Prefer explicit rules over LLM judgment whenever the condition can be expressed deterministically — e.g. every Process has an ID/purpose/required inputs/outputs, every dependency and consumer references an existing Process, no circular dependency unless explicitly iterative, all terminal paths have termination semantics. Implement these as deterministic validation. Semantic questions (does this Process contribute? are two unnecessarily overlapping? is the boundary coherent? is the review point meaningful?) may require LLM evaluation. A good validator combines both.

---

# 26. LLM Validation Should Not Replace Structural Validation

Do not ask an LLM to validate properties that can be checked directly (e.g. don't ask an LLM "does every dependency point to a valid Process" — validate IDs and dependencies in Python). Use an LLM only where semantic reasoning is required. This reduces token usage, latency, nondeterminism, validation ambiguity, and unnecessary model calls, and makes the validator easier to test.

---

# 27. Validation Order

Validation proceeds from structural toward semantic correctness: 1 Schema → 2 Reference → 3 Contract → 4 Dependency → 5 Graph → 6 Goal Coverage → 7 Completeness → 8 Atomicity → 9 Responsibility Separation → 10 Human Review → 11 Overall Architecture Review. There is little value in expensive semantic evaluation when the graph is structurally invalid.

---

# 28. Human Review of the Process Architecture

After automated validation, the architecture should be presented for human review when the workflow is important or complex. The reviewer should be able to understand the workflow (start → processes → branches → human review → end) without inspecting CrewAI implementation. Review should focus on: **Goal** (does it achieve the intended goal?), **Completeness** (missing work?), **Necessity** (unnecessary Processes?), **Boundaries** (natural and understandable?), **Dependencies** (logically correct?), **Human Decisions** (correctly placed?), **Failure Awareness** (obvious alternate outcomes represented?). Detailed failure analysis happens in the next stage.

---

# 29. Review Questions

A reviewer should be able to answer: **Goal** (what is the workflow trying to achieve? what establishes successful completion?), **Start** (what starts it? are required inputs available?), **Processes** (what does each accomplish? why does each exist?), **Contracts** (what enters each? what does it produce? who consumes the output?), **Dependencies** (why does each exist? could any be removed?), **Boundaries** (too broad? unnecessarily small? responsibilities separate?), **Graph** (can it reach the goal? unreachable Processes? dead ends? meaningful conditional paths?), **Human Review** (where is judgment actually required? is the decision explicit? does every outcome have a consequence?), **Termination** (how does it end successfully? what happens when the goal can't be achieved?).

---

# 30. Validation Result

The validation stage should produce a structured result rather than only prose.

Conceptual structure:

```yaml
process_validation:
  status: ""
  summary: ""

  structural:
    schema_valid: false
    references_valid: false
    contracts_valid: false
    dependencies_valid: false
    graph_valid: false

  semantic:
    goal_coverage: ""
    completeness: ""
    necessity: ""
    atomicity: ""
    responsibility_separation: ""

  human_review:
    required: false
    status: ""
    decision: ""
    reviewer_notes: []

  findings:
    - id: ""
      severity: ""
      process_id: ""
      category: ""
      message: ""
      recommendation: ""

  approved_processes: []

  rejected_processes: []

  required_changes: []

  assumptions: []
```

The exact schema can evolve with implementation.

The important principle is that validation should produce machine-readable results that Amsha can consume.

---

# 31. Validation Status

Recommended overall states: `DRAFT`, `VALIDATING`, `FAILED`, `REVIEW_REQUIRED`, `APPROVED`, `CHANGES_REQUIRED` — proceeding from draft through structural then semantic validation to a human decision of APPROVED or CHANGES_REQUIRED. Do **not** mark an architecture approved merely because validation completed successfully; validation completion and approval are different concepts.

---

# 32. Human Approval Gate

When approval is required: `Process Architecture → Automated Validation → Semantic Validation → Human Review → Approval Gate`. Outcomes: **APPROVE** → proceed to Flow & State Planning; **CHANGES_REQUIRED** → modify architecture → validate again. This creates an explicit architectural gate.

---

# 33. Iterative Validation

Process architecture should be treated as iterative: `Draft → Validate → Review → Modify → Validate Again → Approve`. Do not assume the first decomposition is correct; validation exists partly to discover problems not obvious during decomposition.

---

# 34. Validation Does Not Redesign Silently

The validator may identify problems and recommend changes, but should not silently modify the architecture unless in an authorized auto-correction mode. E.g. a finding "P3 requires character_profile but no upstream Process produces it" should recommend modifying P2 or introducing a producer — not silently insert a Process. This preserves traceability and human control.

---

# 35. Process Approval Contract

Once approved, the Process architecture becomes the basis for the next stage. Approval means: problem understood, goal bounded, Processes identified, contracts defined, atomicity reviewed, dependencies validated, human review points defined → **Process Architecture Approved**. Only after this gate should implementation architecture be designed.

---

# 36. What This Stage Must Not Decide

Process validation must not prematurely decide: how many Agents, which Agent performs a Process, how many Tasks, whether a Crew/Flow method is required, which LLM/provider, which Python library, which Tool, which MCP server, how Knowledge is stored, or how Memory is configured. Those belong to later stages. The Process architecture should remain stable even if the implementation mechanism changes.

---

# 37. Example

Goal: produce an approved chapter for a story. Processes: P1 Analyze Source, P2 Define Chapter Requirements, P3 Generate Chapter, P4 Evaluate Chapter, P5 Improve Chapter, H1 Human Approval. Flow: `P1→P2→P3→P4 → Pass? NO→P5→P4 / YES→H1 → Approved? YES→END / NO→P5`.

Validation checks — **Goal Coverage**: all contribute to the approved chapter. **Contract Compatibility**: P1→P2→P3→P4, P5→P4, P4→H1 outputs all compatible. **Iteration**: P4→P5→P4 is intentional with an evaluation criterion. **Human Review**: H1 is final creative approval, not automated QC. **Termination**: workflow ends when evaluation passes AND human approves. **Atomicity**: each Process has a distinct responsibility.

The architecture is therefore a candidate for approval.

---

# 38. Process Validation Checklist

Before approval, verify:

## Problem and Goal

* [ ] Problem definition exists.
* [ ] Start condition is defined.
* [ ] End goal is defined.
* [ ] Success condition is defined.
* [ ] Workflow boundary is defined.

## Process Coverage

* [ ] Every necessary transformation is represented.
* [ ] No unnecessary Process exists.
* [ ] Every Process contributes to the goal.
* [ ] No important work is hidden as an assumption.

## Contracts

* [ ] Every Process has a purpose.
* [ ] Required inputs are defined.
* [ ] Outputs are defined.
* [ ] Preconditions are meaningful.
* [ ] Postconditions are meaningful.
* [ ] Completion criteria are defined.

## Compatibility

* [ ] Producer outputs satisfy consumer inputs.
* [ ] Dependencies reference valid Processes.
* [ ] No unjustified dependencies exist.
* [ ] Required information has a producer or valid external source.

## Graph

* [ ] Start Processes are reachable.
* [ ] Required Processes are reachable.
* [ ] Terminal Processes are valid.
* [ ] No accidental dead ends exist.
* [ ] Conditional paths are meaningful.
* [ ] Iterations have termination conditions.

## Boundaries

* [ ] Processes are atomic enough.
* [ ] Processes are not artificially fragmented.
* [ ] God Processes do not exist.
* [ ] Responsibilities do not unnecessarily overlap.

## Human Review

* [ ] Required design review is identified.
* [ ] Required runtime approval points are identified.
* [ ] Human decisions are explicit.
* [ ] Review outcomes have defined consequences.

## Approval

* [ ] Structural validation passes.
* [ ] Semantic validation passes or has accepted findings.
* [ ] Human review is complete when required.
* [ ] Architecture is explicitly approved.

---

# 39. Anti-Patterns

- **39.1 Validating Implementation Instead of Architecture** — asking "is this a good Crew?" instead of "is this the correct Process?".
- **39.2 LLM-Only Validation** — sending the entire architecture to an LLM and asking "is this valid?" wastes tokens and creates nondeterminism; use deterministic validation first.
- **39.3 Silent Auto-Repair** — validator silently adding a missing Process. Better: identify finding → explain required change → wait for authorized modification → validate again.
- **39.4 Hidden Human Approval** — `` Generate → human probably checks it → continue ``. Better: `` Generate → Human Review → Decision → explicit transition ``.
- **39.5 Human Review Everywhere** — human review is not a substitute for good architecture or deterministic validation; every Process → Human Approval creates unnecessary friction. Use it at meaningful decision boundaries.
- **39.6 Over-Validation** — don't repeatedly validate the same property at every layer. Process/Crew/Agent/Task/Flow validation should each validate properties appropriate to their abstraction level.

---

# 40. Amsha Principle

The purpose of Process Validation is to establish a reliable boundary between **problem reasoning** and **implementation reasoning**: `USER PROBLEM → GOAL → PROCESSES → PROCESS CONTRACTS → PROCESS VALIDATION → HUMAN APPROVAL → APPROVED ARCHITECTURE → IMPLEMENTATION DESIGN`.

This prevents a common failure mode — *User Problem → immediately create Agents/Tasks/Crew → discover later the workflow itself was wrong*. Amsha should instead enforce:

> **Do not implement an unvalidated Process architecture.**

---

# 41. Output of This Stage

The output is a **Validated Process Architecture** containing: approved Processes, validated contracts, validated dependencies, validated Process graph, identified human review points, validation findings, accepted assumptions, required changes (if any), and approval status.

Conceptually:

```yaml
validated_process_architecture:
  status: approved
  processes: []
  relationships: []
  human_review_points: []
  validation:
    structural: {}
    semantic: {}
    findings: []
  approval:
    status: approved
    notes: []
  assumptions: []
```

This artifact becomes an input to **05-flow-and-state-planning.md**.

---

# 42. Core Rule

> **Validate the work architecture before designing the implementation architecture.**

A correct Agent, Task, Crew, Flow, Tool, Knowledge source, Memory configuration, or MCP integration cannot compensate for an incorrectly decomposed workflow. The Process architecture must therefore be **Defined → Contracted → Validated → Human-reviewed when required → Approved** before implementation begins.

```
```
