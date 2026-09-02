#  Amsha Prerequisite: Process Validation and Human Review

## Purpose

Process decomposition identifies the work that must happen.

Process contracts define what each Process accepts, transforms, and produces.

This document defines how those Processes are **validated before they become an executable workflow**.

The objective is to ensure that:

- all required work is represented
- every Process has a valid purpose
- Process boundaries are appropriate
- inputs and outputs are compatible
- dependencies are correct
- unnecessary Processes are removed
- missing Processes are identified
- human decisions are explicitly represented
- the Process graph can achieve the defined end goal
- the architecture is understandable and reviewable before implementation

The output of this stage is a **validated Process architecture** that can be used for Flow and state planning.

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

This stage is intentionally before Flow, Crew, Agent, Task, Tool, Knowledge, Memory, or MCP design.

The question is still:

> "Is this the correct work structure?"

Not:

> "How should this be implemented?"

---

# 2. What Process Validation Means

Process validation verifies that the proposed Process architecture is logically capable of achieving the defined goal.

A Process architecture is valid when:

1. the workflow starts from a valid start condition
2. required inputs are available
3. every necessary transformation is represented
4. Process contracts are internally coherent
5. Process dependencies are valid
6. outputs satisfy downstream inputs
7. the Process graph can reach the desired end state
8. no critical work is missing
9. no unnecessary work is included
10. Process boundaries remain understandable
11. human decisions are explicitly represented where required
12. termination conditions are meaningful
13. the architecture remains independent of implementation technology

Process validation is therefore a **logical architecture review**, not a CrewAI configuration review.

---

# 3. Validation Inputs

Process validation consumes the outputs of the previous prerequisite stages.

```text
Problem Definition
        +
Goal & Boundary Definition
        +
Process Decomposition
        +
Process Contracts & Atomicity
        ↓
Process Validation
```

The validator should have access to:

* problem statement
* start condition
* required inputs
* desired end state
* success conditions
* workflow boundaries
* included/excluded scope
* Process list
* Process relationships
* Process contracts
* Process dependencies
* Process outputs
* Process consumers
* human approval requirements
* assumptions

The validator should not require:

* Agent definitions
* Task definitions
* Crew definitions
* Flow implementation
* LLM selection
* model configuration
* tool selection
* MCP configuration
* Python implementation

Those belong to later stages.

---

# 4. Validation Dimensions

Process validation should evaluate the architecture from multiple independent perspectives.

```text
                    Process Architecture
                           │
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
   Goal Coverage      Contract Validity   Dependency Validity
        │                  │                  │
        ↓                  ↓                  ↓
   Boundary Fit       Atomicity Fit      Graph Reachability
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ↓
                    Human Review
                           ↓
                 Validated Architecture
```

The primary validation dimensions are:

1. Goal Coverage
2. Boundary Compliance
3. Process Necessity
4. Process Completeness
5. Contract Validity
6. Contract Compatibility
7. Dependency Validity
8. Graph Reachability
9. Atomicity
10. Responsibility Separation
11. Human Decision Placement
12. Termination
13. Reviewability

---

# 5. Goal Coverage

Every Process must contribute to achieving the defined goal.

For each Process ask:

> Why does this Process exist?

Then ask:

> How does its output contribute to the final goal?

A Process that cannot establish a meaningful relationship with the goal is suspicious.

Example:

```text
Goal:
Produce a validated chapter draft.

Processes:

P1 Analyze Source
P2 Define Chapter Requirements
P3 Generate Chapter
P4 Evaluate Chapter
P5 Improve Chapter
```

The relationship is clear:

```text
Source
  ↓
Analysis
  ↓
Requirements
  ↓
Draft
  ↓
Evaluation
  ↓
Improvement
  ↓
Validated Chapter
```

A Process such as:

```text
P6 Generate Random Metadata
```

would require justification if that metadata does not contribute to the goal.

---

# 6. Process Necessity

Every Process should pass the necessity test.

Ask:

> If this Process were removed, could the workflow still achieve its goal with the remaining Processes?

There are three possible outcomes.

### Necessary

Removing the Process makes the workflow unable to satisfy the goal.

```text
P1 → P2 → P3
```

If P2 is required for P3 to operate correctly, P2 is necessary.

### Conditionally Necessary

The Process is required only under specific conditions.

```text
P1
 ↓
Decision
 ├── P2
 └── P3
```

This is valid when the condition is meaningful.

### Unnecessary

The Process does not materially contribute to the goal.

It should normally be removed.

---

# 7. Process Completeness

Necessity alone is not enough.

The architecture must also identify missing work.

Ask:

> What must happen between the start condition and the end condition?

Then trace the transformation forward.

```text
START
  ↓
Required Transformation 1
  ↓
Required Transformation 2
  ↓
Required Transformation 3
  ↓
END
```

If an essential transformation is missing, the Process architecture is incomplete.

For example:

```text
Input
  ↓
Generate Output
  ↓
END
```

may be insufficient when the goal requires:

```text
Input
  ↓
Analyze
  ↓
Generate
  ↓
Validate
  ↓
Approve
  ↓
END
```

The validator must distinguish between:

* genuinely missing work
* optional work
* work that belongs inside an existing Process
* work that is implementation detail

Do not create a new Process merely because a missing action can be described as a separate technical step.

---

# 8. Start-to-End Traceability

The entire architecture must be traceable from the defined start condition to the defined end condition.

A basic trace should answer:

```text
What enters the workflow?
        ↓
What happens to it?
        ↓
What changes?
        ↓
What information is produced?
        ↓
Where does that information go?
        ↓
What eventually establishes the goal?
```

Every terminal Process should contribute to a valid termination condition.

Every required Process should be reachable from the start.

Every required output should have a meaningful consumer or contribute directly to the final goal.

---

# 9. Contract Validation

Each Process contract must be checked independently.

Validate:

```text
Purpose
Input
Transformation
Output
Preconditions
Postconditions
Completion
Dependencies
Consumers
```

The validator should detect problems such as:

* missing required input
* undefined output
* vague transformation
* contradictory preconditions
* impossible postconditions
* completion criteria unrelated to the Process
* dependency on unavailable information
* output without a consumer
* consumer requiring information that the Process does not produce

A Process should not be considered valid merely because its description sounds reasonable.

Its contract must be executable as a logical specification.

---

# 10. Contract Compatibility

Producer and consumer contracts must be compatible.

For every dependency:

```text
Producer Output
       ↓
Consumer Input
```

validate:

```text
Producer produces what Consumer requires?
        ↓
YES → valid dependency
NO  → architecture problem
```

Compatibility includes:

* required information
* semantic meaning
* structure
* completeness
* availability
* timing

Example:

```text
P1 Output:
character_analysis

P2 Input:
character_analysis
```

is compatible.

But:

```text
P1 Output:
character_names

P2 Input:
complete_character_psychology
```

is not automatically compatible.

The architecture must either:

* change P1's output
* change P2's input
* introduce the missing transformation
* or establish that P2 can derive the required information from another valid source

---

# 11. Dependency Validation

Dependencies should represent genuine logical requirements.

Valid:

```text
P2 depends on P1
```

when P2 cannot correctly operate without P1's output.

Invalid:

```text
P2 depends on P1
```

when P2 could operate independently.

Unnecessary dependencies reduce:

* parallelism
* flexibility
* fault isolation
* execution efficiency

Therefore:

> Dependency must represent necessity, not convenience.

---

# 12. Parallelism Validation

Processes should be independent when their work is independent.

Example:

```text
             ┌── P2 ──┐
P1 ──────────┤         ├── P4
             └── P3 ──┘
```

If P2 and P3 require only P1's output and do not depend on each other, they may be parallel.

Do not introduce artificial sequential ordering:

```text
P1 → P2 → P3 → P4
```

when the actual dependency graph is:

```text
P1 → P2 ──┐
          ├→ P4
P1 → P3 ──┘
```

However, parallelism should be established from logical dependency, not from a desire to optimize execution prematurely.

---

# 13. Conditional Process Validation

Conditional branches must have explicit reasons.

Valid:

```text
P1
 ↓
Decision
 ├── valid → P2
 └── invalid → P3
```

The decision must specify:

* what condition is evaluated
* what determines each branch
* what each branch means
* whether branches eventually converge
* whether a branch can terminate the workflow

Avoid vague branches such as:

```text
if needed
if appropriate
if necessary
```

unless "needed", "appropriate", or "necessary" has a defined evaluation criterion.

---

# 14. Iteration Validation

Iterations must have a meaningful purpose and termination condition.

Valid:

```text
Generate
   ↓
Evaluate
   ↓
Meets Criteria?
   ├── YES → Continue
   └── NO  → Improve
                ↓
             Generate
```

The architecture should define:

* what is evaluated
* what constitutes success
* what causes another iteration
* maximum or otherwise bounded iteration behavior
* what happens if the criteria are never satisfied

Do not allow an implicit infinite loop.

---

# 15. Process Atomicity Revalidation

Atomicity was defined during Process Contract design.

Validation should verify that the proposed boundaries still make sense when viewed as a complete architecture.

Ask:

1. Does the Process still have one primary responsibility?
2. Does it still perform one coherent transformation?
3. Does it produce one coherent primary result?
4. Can it be evaluated independently?
5. Does it contain unrelated responsibilities?
6. Does it create an unnecessary dependency between unrelated activities?

A Process may initially appear atomic but become questionable when its relationship with neighboring Processes is examined.

---

# 16. Responsibility Separation

Two Processes should not perform substantially overlapping responsibilities unless the overlap is intentional.

Example:

```text
P2 Analyze Character
P3 Evaluate Character
```

may be valid if:

```text
Analysis = understand the character
Evaluation = determine whether the character satisfies defined criteria
```

But:

```text
P2 Analyze Character
P3 Analyze Character Again
```

requires justification.

Overlap can indicate:

* duplicated work
* unclear boundaries
* missing specialization of responsibilities
* accidental repeated processing

---

# 17. Human Review

Human review is an explicit architecture mechanism.

It should not be represented as an informal instruction such as:

```text
Someone should check this later.
```

Instead, define the review boundary explicitly.

```text
Process A
   ↓
Human Review
   ↓
Approved?
 ├── YES → Process B
 └── NO  → Revision
```

A human review point should identify:

* what is being reviewed
* why human judgment is required
* what information the human receives
* what decision the human makes
* possible decisions
* what happens after each decision
* whether the review is mandatory or optional

---

# 18. When Human Review Is Appropriate

Human review is particularly valuable when correctness cannot be adequately determined through deterministic validation or when the decision carries meaningful subjective or external consequences.

Examples include:

* creative approval
* final editorial judgment
* ambiguous interpretation
* high-impact decisions
* acceptance of externally visible output
* approval of major architecture changes
* resolving conflicts between valid alternatives

Human review should not be added merely because automation feels uncertain.

The purpose is to place human judgment at a meaningful decision boundary.

---

# 19. Human Review vs Validation

These are different mechanisms.

### Automated Validation

Answers:

> Does the output satisfy defined rules or criteria?

Example:

```text
Required fields present?
Schema valid?
References valid?
Length within limits?
```

### Human Review

Answers:

> Is this acceptable given human judgment, intent, taste, context, or responsibility?

Example:

```text
Does this chapter feel emotionally correct?
Is this creative direction acceptable?
Does this interpretation reflect the intended meaning?
```

They may coexist.

```text
Process
  ↓
Automated Validation
  ↓
Pass?
  ├── NO  → Revision
  └── YES
       ↓
Human Review
       ↓
Approved?
  ├── NO  → Revision
  └── YES → Continue
```

Prefer deterministic validation wherever deterministic validation is sufficient.

Use human review where human judgment provides meaningful additional value.

---

# 20. Human Review as a Process Boundary

A human review can create a real workflow boundary.

For example:

```text
P1 Analyze Source
      ↓
P2 Generate Proposal
      ↓
H1 Human Review
      ↓
P3 Produce Approved Output
```

The human review is not necessarily an implementation Process.

It is a **decision boundary** in the Process architecture.

The architecture must nevertheless represent its inputs, decision, and consequences.

---

# 21. Design Review vs Runtime Review

Two different kinds of human review should be distinguished.

## Design Review

Occurs before execution.

Purpose:

```text
Validate the proposed Process architecture
```

Typical questions:

* Are these the correct Processes?
* Is anything missing?
* Are boundaries appropriate?
* Are dependencies correct?
* Is the workflow understandable?
* Are human approval points correctly placed?

This review validates the architecture itself.

## Runtime Review

Occurs during workflow execution.

Purpose:

```text
Validate or approve an actual Process output
```

Example:

```text
Generate Chapter
      ↓
Human Review
      ↓
Approve / Reject / Revise
```

Do not confuse these two.

---

# 22. Human Review Should Be Explicit

Avoid architectures that depend on hidden human intervention.

Bad:

```text
Generate Output
↓
Someone checks it
↓
Continue
```

Better:

```text
Generate Output
      ↓
Human Review
      ↓
Decision
 ├── Approve
 ├── Request Revision
 └── Reject
```

The explicit form makes the workflow:

* understandable
* testable
* auditable
* implementable
* recoverable

---

# 23. Review Outcomes

Human review should define meaningful outcomes.

Typical outcomes are:

```text
APPROVE
REVISE
REJECT
ESCALATE
```

Not every workflow needs all of them.

For example:

```text
Human Review
     ↓
 ┌───────────┐
 │ Decision  │
 └───────────┘
      │
 ┌────┴────┐
 ↓         ↓
Approve   Revise
 ↓         ↓
Next      Revision
          Process
```

The important requirement is that each outcome has a defined consequence.

---

# 24. Validation Severity

Validation findings should be classified.

Recommended levels:

```text
ERROR
WARNING
NOTE
```

### ERROR

The architecture cannot reliably achieve its goal.

Examples:

* missing required Process
* broken contract
* unreachable terminal Process
* incompatible producer/consumer contracts
* impossible dependency
* undefined required decision
* missing termination condition

Execution should not proceed until resolved.

### WARNING

The architecture may work but has a meaningful design concern.

Examples:

* unnecessary dependency
* questionable Process boundary
* duplicate transformation
* excessive Process granularity
* weak validation criteria

The designer should review the finding.

### NOTE

An informational observation.

Examples:

* possible parallelism
* optional simplification
* possible future optimization

A note does not necessarily require change.

---

# 25. Validation Should Be Deterministic Where Possible

Process validation should prefer explicit rules over LLM judgment whenever the condition can be expressed deterministically.

Examples:

```text
Every Process has an ID
Every Process has a purpose
Every Process has required inputs
Every Process has outputs
Every dependency references an existing Process
Every consumer references an existing Process
No circular dependency unless explicitly iterative
All terminal paths have termination semantics
```

These should be implemented as deterministic validation.

Semantic questions may require LLM evaluation.

Examples:

```text
Does this Process actually contribute to the goal?
Are these two Processes unnecessarily overlapping?
Is this Process boundary conceptually coherent?
Is the human review point meaningful?
```

A good validator combines both.

```text
Deterministic Validation
        +
Semantic Validation
        ↓
Process Architecture Assessment
```

---

# 26. LLM Validation Should Not Replace Structural Validation

Do not ask an LLM to validate properties that can be checked directly.

Bad:

```text
LLM:
"Check whether every dependency points to a valid Process."
```

Better:

```text
Python:
Validate Process IDs and dependencies.
```

Then use an LLM only where semantic reasoning is required.

This reduces:

* token usage
* latency
* nondeterminism
* validation ambiguity
* unnecessary model calls

It also makes the architecture validator easier to test.

---

# 27. Validation Order

Validation should proceed from structural correctness toward semantic correctness.

Recommended sequence:

```text
1. Schema Validation
       ↓
2. Reference Validation
       ↓
3. Contract Validation
       ↓
4. Dependency Validation
       ↓
5. Graph Validation
       ↓
6. Goal Coverage
       ↓
7. Completeness
       ↓
8. Atomicity
       ↓
9. Responsibility Separation
       ↓
10. Human Review Validation
       ↓
11. Overall Architecture Review
```

There is little value in performing expensive semantic evaluation when the Process graph is structurally invalid.

---

# 28. Human Review of the Process Architecture

After automated validation, the Process architecture should be presented for human review when the workflow is sufficiently important or complex.

The reviewer should be able to understand:

```text
START
  ↓
Process 1
  ↓
Process 2
  ├── Process 3
  └── Process 4
  ↓
Human Review
  ↓
Process 5
  ↓
END
```

without needing to inspect CrewAI implementation.

The review should focus on:

### Goal

Does this workflow actually achieve the intended goal?

### Completeness

Is any meaningful work missing?

### Necessity

Is any Process unnecessary?

### Boundaries

Are Process boundaries natural and understandable?

### Dependencies

Are dependencies logically correct?

### Human Decisions

Are human judgment points correctly placed?

### Failure Awareness

Are obvious alternate outcomes represented?

Detailed failure analysis is handled in the next prerequisite stage.

---

# 29. Review Questions

A reviewer should be able to answer:

### Goal

* What is the workflow trying to achieve?
* What establishes successful completion?

### Start

* What starts the workflow?
* Are required inputs available?

### Processes

* What does each Process accomplish?
* Why does each Process exist?

### Contracts

* What enters each Process?
* What does it produce?
* Who consumes the output?

### Dependencies

* Why does each dependency exist?
* Could any dependency be removed?

### Boundaries

* Are any Processes too broad?
* Are any Processes unnecessarily small?
* Are responsibilities clearly separated?

### Graph

* Can the workflow reach the goal?
* Are there unreachable Processes?
* Are there dead ends?
* Are conditional paths meaningful?

### Human Review

* Where is human judgment actually required?
* Is the decision explicit?
* Does every review outcome have a defined consequence?

### Termination

* How does the workflow end successfully?
* What happens when the goal cannot be achieved?

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

Recommended overall states:

```text
DRAFT
VALIDATING
FAILED
REVIEW_REQUIRED
APPROVED
CHANGES_REQUIRED
```

Example:

```text
DRAFT
  ↓
VALIDATING
  ↓
 ┌───────────────┐
 │ Structural OK │
 └───────────────┘
       ↓
Semantic Review
       ↓
REVIEW_REQUIRED
       ↓
Human Decision
   ┌───┴────┐
   ↓        ↓
APPROVED  CHANGES_REQUIRED
```

Do not mark an architecture as approved merely because validation completed successfully.

Validation completion and approval are different concepts.

---

# 32. Human Approval Gate

When human approval is required:

```text
Process Architecture
        ↓
Automated Validation
        ↓
Semantic Validation
        ↓
Human Review
        ↓
Approval Gate
```

Possible outcomes:

```text
APPROVE
    ↓
Proceed to Flow & State Planning

CHANGES_REQUIRED
    ↓
Modify Process Architecture
    ↓
Validate Again
```

This creates an explicit architectural gate.

---

# 33. Iterative Validation

Process architecture should be treated as iterative.

```text
Draft
  ↓
Validate
  ↓
Review
  ↓
Modify
  ↓
Validate Again
  ↓
Approve
```

Do not assume that the first decomposition is correct.

Validation exists partly to discover problems that were not obvious during decomposition.

---

# 34. Validation Does Not Redesign Silently

The validator may identify problems and recommend changes.

It should not silently modify the architecture unless explicitly operating in an authorized auto-correction mode.

For example:

```text
Finding:
P3 requires character_profile,
but no upstream Process produces character_profile.

Recommendation:
Modify P2 output or introduce a Process that produces character_profile.
```

The validator should not silently insert a new Process.

This preserves architectural traceability and human control.

---

# 35. Process Approval Contract

Once approved, the Process architecture becomes the basis for the next stage.

Approval means:

```text
Problem understood
        +
Goal bounded
        +
Processes identified
        +
Contracts defined
        +
Atomicity reviewed
        +
Dependencies validated
        +
Human review points defined
        ↓
Process Architecture Approved
```

Only after this gate should implementation architecture be designed.

---

# 36. What This Stage Must Not Decide

Process validation must not prematurely decide:

* how many Agents are required
* which Agent performs a Process
* how many Tasks are required
* whether a Crew is required
* whether a Flow method is required
* which LLM is used
* which model provider is used
* which Python library is used
* which Tool is selected
* which MCP server is used
* how Knowledge is stored
* how Memory is configured

Those decisions belong to later capability and implementation stages.

The Process architecture should remain stable even if the implementation mechanism changes.

---

# 37. Example

Consider:

```text
Goal:
Produce an approved chapter for a story.

Processes:

P1 Analyze Source
P2 Define Chapter Requirements
P3 Generate Chapter
P4 Evaluate Chapter
P5 Improve Chapter
H1 Human Approval
```

The proposed architecture:

```text
P1
 ↓
P2
 ↓
P3
 ↓
P4
 ↓
Pass?
 ├── NO → P5 → P4
 └── YES
       ↓
      H1
       ↓
   Approved?
    ├── YES → END
    └── NO  → P5
```

Validation checks:

### Goal Coverage

All Processes contribute to producing the approved chapter.

### Contract Compatibility

```text
P1 output → P2 input
P2 output → P3 input
P3 output → P4 input
P4 output → P5 input
P5 output → P4 input
P4 output → H1 input
```

must all be compatible.

### Iteration

P4 → P5 → P4 is intentional and has an evaluation criterion.

### Human Review

H1 represents final creative approval rather than automated quality checking.

### Termination

The workflow terminates when:

```text
Evaluation passes
AND
Human approves
```

### Atomicity

Each Process has a distinct responsibility.

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

## 39.1 Validating Implementation Instead of Architecture

Bad:

```text
Is this a good Crew?
```

At this stage the question is:

```text
Is this the correct Process?
```

---

## 39.2 LLM-Only Validation

Bad:

```text
Send the entire architecture to an LLM
and ask "Is this valid?"
```

This wastes tokens and creates unnecessary nondeterminism.

Use deterministic validation first.

---

## 39.3 Silent Auto-Repair

Bad:

```text
Validator notices missing Process
→ silently adds Process
```

Better:

```text
Validator
→ identifies finding
→ explains required change
→ waits for authorized modification
→ validates again
```

---

## 39.4 Hidden Human Approval

Bad:

```text
Generate
→ human probably checks it
→ continue
```

Better:

```text
Generate
→ Human Review
→ Decision
→ explicit transition
```

---

## 39.5 Human Review Everywhere

Human review should not be used as a substitute for good architecture or deterministic validation.

Bad:

```text
Every Process
   ↓
Human Approval
```

This creates unnecessary friction.

Use human review at meaningful decision boundaries.

---

## 39.6 Over-Validation

Do not repeatedly validate the same property at every layer.

For example:

```text
Process validation
Crew validation
Agent validation
Task validation
Flow validation
```

should each validate properties appropriate to their abstraction level.

Process validation should focus on Process architecture.

---

# 40. Amsha Principle

The purpose of Process Validation is to establish a reliable boundary between **problem reasoning** and **implementation reasoning**.

```text
USER PROBLEM
     ↓
GOAL
     ↓
PROCESSES
     ↓
PROCESS CONTRACTS
     ↓
PROCESS VALIDATION
     ↓
HUMAN APPROVAL
     ↓
APPROVED ARCHITECTURE
     ↓
IMPLEMENTATION DESIGN
```

This prevents a common failure mode:

```text
User Problem
     ↓
Immediately create Agents
     ↓
Create Tasks
     ↓
Create Crew
     ↓
Discover later that the workflow itself was wrong
```

Amsha should instead enforce:

> **Do not implement an unvalidated Process architecture.**

---

# 41. Output of This Stage

The output is:

```text
Validated Process Architecture
```

containing:

* approved Processes
* validated contracts
* validated dependencies
* validated Process graph
* identified human review points
* validation findings
* accepted assumptions
* required changes, if any
* approval status

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

This artifact becomes an input to:

```text
05-flow-and-state-planning.md
```

---

# 42. Core Rule

> **Validate the work architecture before designing the implementation architecture.**

A correct Agent, Task, Crew, Flow, Tool, Knowledge source, Memory configuration, or MCP integration cannot compensate for an incorrectly decomposed workflow.

The Process architecture must therefore be:

```text
Defined
    ↓
Contracted
    ↓
Validated
    ↓
Human-reviewed when required
    ↓
Approved
```

before implementation begins.

```
```
