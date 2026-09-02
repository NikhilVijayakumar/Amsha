# Amsha Prerequisite: Goal and Boundary Definition

## 1. Purpose

This document defines the second step in Amsha workflow design:

> **Establish a precise start boundary, desired end state, and scope of responsibility before decomposing the problem into Processes.**

The Problem Definition establishes what the user wants to accomplish.

Goal and Boundary Definition determines:

- where the workflow begins
- what the workflow is responsible for
- where the workflow ends
- what constitutes completion
- what is inside the workflow
- what is outside the workflow
- what must be passed to or received from external systems or workflows

This document must be completed before Process Decomposition.

---

# 2. Core Principle

Amsha follows:

> **A workflow must have a clearly defined beginning, responsibility boundary, and completion boundary.**

The architectural sequence is:

```text
Problem
   ↓
Start Boundary
   ↓
End Goal
   ↓
Scope Boundary
   ↓
Process Decomposition
````

Do not begin Process Decomposition until the start and end boundaries are sufficiently clear.

---

# 3. Problem vs Goal vs Boundary

These concepts must remain separate.

### Problem

Describes what needs to be solved.

```text
Transform an existing chapter summary into
a validated chapter development specification.
```

### Goal

Describes the desired end state.

```text
A validated chapter development specification exists.
```

### Boundary

Defines what the workflow owns and where its responsibility stops.

```text
START:
Chapter summary is available.

END:
Validated chapter development specification is produced.

OUTSIDE:
Final screenplay publication.
```

Conceptually:

```text
                  PROBLEM
                     │
                     ▼
              ┌─────────────┐
              │    START    │
              │   BOUNDARY  │
              └──────┬──────┘
                     │
                 WORKFLOW
                  SCOPE
                     │
                     ▼
              ┌─────────────┐
              │     END     │
              │   BOUNDARY  │
              └─────────────┘
```

---

# 4. Start Boundary

The start boundary defines the condition under which the workflow is allowed to begin.

It answers:

> **What must be true before execution starts?**

Examples:

```text
A chapter summary is available.
```

```text
A customer request has been submitted.
```

```text
A source document has been uploaded.
```

```text
An approved image-generation specification exists.
```

The start boundary should describe a meaningful state, not an implementation detail.

### Bad

```text
The Flow object has been initialized.
```

### Good

```text
A validated chapter specification is available for generation.
```

---

# 5. Start Preconditions

The start boundary may require preconditions.

For example:

```yaml
start:
  condition: >
    A chapter summary is available for analysis.

  preconditions:
    - chapter_summary_exists
    - chapter_summary_is_readable
```

Preconditions should answer:

> **What must be true for the workflow to safely begin?**

Possible preconditions include:

* required input exists
* required fields are present
* input is readable
* input has the expected format
* required external dependency is available
* required approval has been obtained
* required configuration exists

Do not add preconditions merely because they are technically convenient.

They should protect the actual workflow boundary.

---

# 6. Required and Optional Inputs

Start-boundary inputs should be classified.

```yaml
start:
  required_inputs:
    - chapter_summary

  optional_inputs:
    - story_bible
    - character_profiles
    - previous_evaluation
```

### Required input

Without it, the workflow cannot reasonably perform its intended responsibility.

### Optional input

The workflow can still execute without it, although the result may be improved by its presence.

Do not silently treat optional information as mandatory.

Likewise, do not make every available piece of information a required input.

---

# 7. End Goal

The end goal defines the desired state of the workflow.

It answers:

> **What must exist when the workflow has successfully completed?**

Example:

```yaml
end:
  condition: >
    A validated chapter development specification exists.
```

The end goal should describe the result rather than the implementation.

### Bad

```text
The Crew has completed all its tasks.
```

### Good

```text
A validated chapter development specification satisfying
the required quality criteria exists.
```

A Crew, Agent, Task, Python function, or Flow completing does not automatically mean the user's goal has been achieved.

---

# 8. End State

For complex workflows, represent the desired end state explicitly.

Example:

```yaml
end:
  state:
    chapter:
      status: validated
      artifact: chapter_development_specification
```

Conceptually:

```text
START
  │
  │
  ▼
Workflow Execution
  │
  │
  ▼
END STATE

chapter.status = validated
```

The end state should be observable.

Avoid end conditions such as:

```text
The chapter should be good.
```

Prefer:

```text
The chapter satisfies all required validation criteria
and passes the minimum quality threshold.
```

---

# 9. Success vs Completion

Amsha must distinguish between **execution completion** and **successful completion**.

### Execution completion

The workflow reached a terminal execution state.

```text
Flow finished.
```

### Successful completion

The workflow reached the desired business/domain outcome.

```text
Output was produced, validated,
and passed the required quality gate.
```

Therefore:

```text
Execution completed
        ≠
Goal achieved
```

This distinction becomes important later when designing Flow states and evaluation gates.

---

# 10. Workflow Scope

The scope defines what the workflow is responsible for.

Example:

```yaml
scope:
  included:
    - analyze chapter summary
    - develop chapter objectives
    - generate chapter specification
    - evaluate chapter specification
    - improve failed results

  excluded:
    - screenplay publication
    - marketing
    - audiobook generation
    - image generation
```

The scope should prevent unrelated work from entering the Process graph.

---

# 11. In-Scope vs Out-of-Scope

Every significant workflow should identify its boundaries.

### In scope

Work required to achieve the defined goal.

### Out of scope

Work that may be related but is not required for this workflow to achieve its goal.

For example:

```text
Goal:
Produce a validated screenplay chapter.

In scope:
- chapter analysis
- chapter generation
- chapter evaluation
- chapter improvement

Out of scope:
- publishing
- marketing
- audiobook production
- social-media promotion
```

This prevents scope expansion during Process Decomposition.

---

# 12. Boundary Ownership

A workflow should clearly define what it owns.

For example:

```text
                    External System
                         │
                         ▼
                  ┌─────────────┐
                  │    START    │
                  ├─────────────┤
                  │             │
                  │   AM SHA    │
                  │  WORKFLOW   │
                  │             │
                  ├─────────────┤
                  │     END     │
                  └─────────────┘
                         │
                         ▼
                    External System
```

Amsha should not automatically absorb every activity surrounding the goal.

The boundary should be based on responsibility, not on what technically could be automated.

---

# 13. External Dependencies

A workflow may depend on external systems.

Examples:

```text
Database
File system
ComfyUI
Unreal Engine
External API
MCP server
Human approval
```

At this stage, identify the dependency but do not yet decide how it will be implemented.

Example:

```yaml
dependencies:
  - source_data
  - human_approval
  - external_rendering_system
```

Later, Capability Selection determines whether the dependency requires:

```text
Python
Tool
MCP
Knowledge
Memory
Human Gate
```

Do not prematurely convert dependencies into implementation decisions.

---

# 14. Goal Granularity

The goal must be large enough to represent a meaningful user outcome.

### Too broad

```text
Create an entire AI entertainment production platform.
```

This would contain many independent workflows.

### Appropriate

```text
Produce a validated screenplay chapter.
```

### Too narrow

```text
Change one character's name in a JSON object.
```

That may be a Task or deterministic operation rather than an entire workflow.

Amsha should identify the appropriate workflow boundary from the user's actual objective.

---

# 15. One Workflow, One Meaningful Goal

A workflow should normally have one primary end goal.

### Bad

```text
Workflow:
Write a screenplay,
generate concept art,
create music,
build Unreal scenes,
publish the project,
and generate marketing material.
```

This contains multiple independent objectives.

### Better

```text
Workflow A:
Produce validated screenplay.

Workflow B:
Produce validated concept art.

Workflow C:
Produce validated music.

Workflow D:
Build validated Unreal scene.
```

A higher-level system may later orchestrate these workflows, but each workflow should retain a coherent responsibility.

---

# 16. Goal Hierarchy

Complex projects may have multiple levels of goals.

For example:

```text
PROJECT
   │
   ├── Produce screenplay
   │      │
   │      ├── Produce chapter
   │      ├── Evaluate chapter
   │      └── Approve chapter
   │
   ├── Produce visual assets
   │
   └── Produce audio assets
```

The current workflow should clearly identify which goal it owns.

Do not mix project-level goals with Process-level goals.

---

# 17. Goal Dependencies

A goal may depend on another approved result.

Example:

```text
Story Architecture
        ↓
Chapter Specification
        ↓
Chapter Generation
        ↓
Chapter Evaluation
        ↓
Chapter Approval
```

The start boundary of a downstream workflow may therefore be:

```text
An approved chapter specification exists.
```

rather than:

```text
The project has started.
```

This creates explicit workflow boundaries.

---

# 18. Human Approval as a Boundary

Some workflows require human approval.

For example:

```text
Process A
   ↓
Output
   ↓
Human Review
   ↓
Approved
   ↓
Workflow continues
```

The approval may represent:

* design approval
* content approval
* quality approval
* safety approval
* business approval
* production approval

Human approval should be explicitly defined if it is part of the goal or workflow contract.

Do not assume every workflow needs human approval.

---

# 19. Design-Time Review vs Runtime Approval

These are different.

### Design-time review

The user approves the architecture before implementation.

```text
Problem
   ↓
Goals
   ↓
Processes
   ↓
Human approves architecture
```

### Runtime approval

A human approves an actual execution result.

```text
Process
   ↓
Generated output
   ↓
Human review
   ↓
Approved
```

Both may exist, but they serve different purposes.

---

# 20. Termination Conditions

A workflow must have a defined termination condition.

At minimum:

```text
SUCCESS
FAILURE
```

For iterative workflows, additional terminal conditions may exist:

```text
QUALITY_THRESHOLD_REACHED
MAX_ITERATIONS_REACHED
HUMAN_REVIEW_REQUIRED
UNRECOVERABLE_FAILURE
```

Example:

```text
Evaluate
   │
   ├── score >= threshold
   │        ↓
   │      SUCCESS
   │
   ├── score < threshold
   │        ↓
   │     Improve
   │        ↓
   │     Evaluate
   │
   └── iteration >= maximum
            ↓
       HUMAN REVIEW
```

These are later implemented by the Flow, but the termination requirements should be established at the architecture level.

---

# 21. Boundary Conditions

The workflow should explicitly consider boundary conditions.

Examples:

```text
No input
Partial input
Unexpected input
Already-completed input
Invalid input
Output already exists
Dependency unavailable
Human rejects output
Maximum iterations reached
```

These conditions do not yet need implementation details.

The important question at this stage is:

> **Does this condition belong inside this workflow, or should it be handled before/after the workflow?**

Detailed failure handling belongs in the later Corner-Case and Failure Planning stage.

---

# 22. Problem Boundary vs Process Boundary

Do not confuse the two.

The workflow boundary might be:

```text
START
Chapter summary available
        │
        ▼
       ...
        │
        ▼
END
Validated chapter
```

Inside it, individual Processes have their own boundaries:

```text
P1
Input → Analysis

P2
Analysis → Specification

P3
Specification → Draft

P4
Draft → Evaluation
```

Therefore:

```text
Workflow Boundary
        │
        ├── Process Boundary
        ├── Process Boundary
        ├── Process Boundary
        └── Process Boundary
```

Process boundaries will be formally defined in the next stages.

---

# 23. Boundary Stability

A good boundary should remain stable when implementation changes.

For example:

```text
Goal:
Produce a validated chapter evaluation.
```

This should remain valid whether evaluation is implemented using:

```text
Python
```

or:

```text
Agent + Task
```

or:

```text
Evaluation Crew
```

The boundary belongs to the problem, not the implementation.

---

# 24. Goal Definition Output

Amsha should produce a structured Goal and Boundary Definition.

Recommended structure:

```yaml
goal_boundary_definition:

  start:
    condition: ""
    required_inputs: []
    optional_inputs: []
    preconditions: []

  goal:
    primary: ""
    success_state: ""

  scope:
    included: []
    excluded: []

  dependencies: []

  human:
    design_review_required: false
    runtime_approval_required: false

  termination:
    success: ""
    failure: ""
    alternate: []

  assumptions: []
```

This specification becomes an input to Process Decomposition.

---

# 25. Example

Assume the Problem Definition is:

```text
Transform an existing chapter summary into a richer,
validated chapter while preserving continuity,
strengthening character development, and increasing suspense.
```

The Goal and Boundary Definition could be:

```yaml
goal_boundary_definition:

  start:
    condition: >
      A chapter summary and required story context
      are available.

    required_inputs:
      - chapter_summary

    optional_inputs:
      - story_bible
      - character_profiles
      - previous_evaluation

    preconditions:
      - chapter_summary_exists
      - chapter_summary_is_readable

  goal:
    primary: >
      Produce a validated chapter that preserves established
      narrative continuity while strengthening character
      development and suspense.

    success_state: >
      A completed chapter satisfies all required quality
      criteria and passes the defined validation gate.

  scope:
    included:
      - chapter analysis
      - chapter development
      - chapter generation
      - chapter evaluation
      - chapter improvement

    excluded:
      - publishing
      - marketing
      - audiobook production
      - unrelated chapters

  dependencies:
    - established story information
    - evaluation criteria

  human:
    design_review_required: true
    runtime_approval_required: true

  termination:
    success: >
      Chapter passes the required quality threshold
      and receives required approval.

    failure: >
      Required output cannot be produced or validated.

    alternate:
      - maximum iterations reached
      - human review required

  assumptions: []
```

Notice that this still does **not** say:

```text
Use Crew
Use Agent
Use three Tasks
Use Memory
Use MCP
Use GPT
Use Python
```

Those decisions come later.

---

# 26. Validation Checklist

Before proceeding to Process Decomposition, Amsha should verify:

## Start Boundary

* [ ] Is the start condition explicit?
* [ ] Are required inputs identified?
* [ ] Are optional inputs distinguished?
* [ ] Are important preconditions identified?
* [ ] Can we determine whether the workflow is ready to start?

## Goal

* [ ] Is there one clear primary goal?
* [ ] Is the desired end state explicit?
* [ ] Is successful completion observable?
* [ ] Is success distinguishable from execution completion?

## Scope

* [ ] Is the workflow responsibility clear?
* [ ] Is important out-of-scope work identified?
* [ ] Is the workflow bounded enough to decompose?

## Dependencies

* [ ] Are important external dependencies identified?
* [ ] Are dependencies separated from implementation choices?

## Human

* [ ] Is design-time review required?
* [ ] Is runtime approval required?
* [ ] If required, is the approval boundary clear?

## Termination

* [ ] Is success defined?
* [ ] Is failure defined?
* [ ] Are alternate terminal states identified?
* [ ] Is an iterative process bounded?

## Architecture Independence

* [ ] No unnecessary Agent decisions?
* [ ] No unnecessary Task decisions?
* [ ] No premature Crew decisions?
* [ ] No premature Flow implementation decisions?
* [ ] No premature Tool/MCP decisions?

If these checks pass, the problem has a sufficiently defined boundary for Process Decomposition.

---

# 27. Anti-Patterns

## 27.1 No explicit end goal

### Bad

```text
Process the document until it looks good.
```

### Good

```text
Produce a validated document satisfying
the defined quality criteria.
```

---

## 27.2 Technical start condition

### Bad

```text
The Flow object starts.
```

### Good

```text
The required input artifact is available and valid.
```

---

## 27.3 Scope explosion

### Bad

```text
Produce a screenplay, images, music, animation,
marketing and final distribution.
```

### Good

```text
Produce a validated screenplay.
```

---

## 27.4 Implementation-defined boundary

### Bad

```text
The workflow ends when all Crew tasks finish.
```

### Good

```text
The workflow ends when the required result
passes its validation criteria.
```

---

## 27.5 Hidden human dependency

### Bad

```text
The system generates the final result.
```

when human approval is actually required.

### Good

```text
The system generates and validates the result,
then waits for required human approval.
```

---

## 27.6 Unlimited iteration

### Bad

```text
Keep improving until the result is good.
```

### Good

```text
Iterate until the minimum quality threshold is reached
or the maximum iteration limit is reached.
```

---

# 28. Relationship to the Next Stage

This document does not decompose the workflow into Processes.

It establishes the boundaries within which Process Decomposition must operate.

The prerequisite sequence is:

```text
00 Problem Definition
        │
        ▼
01 Goal & Boundary Definition
        │
        ▼
02 Process Decomposition
        │
        ▼
03 Process Contracts & Atomicity
        │
        ▼
04 Process Validation & Human Review
        │
        ▼
05 Flow & State Planning
        │
        ▼
06 Corner Cases & Failure Planning
        │
        ▼
07 Capability Selection
        │
        ▼
08 Architecture Validation
```

The next document, `02-process-decomposition.md`, should therefore answer:

> **Given the validated problem, start boundary, end goal, and scope, what meaningful Processes must occur between the start and end states?**

It should **not yet decide whether those Processes are implemented with Agents, Tasks, Crews, Python, Tools, Knowledge, Memory, Skills, or MCP.**

---

# 29. Amsha Rule

> **Every Amsha workflow must have a defined start boundary, a single primary end goal, a bounded scope, and an observable completion condition before Process Decomposition begins.**

The design progression is:

```text
WHAT IS THE PROBLEM?
        ↓
WHERE DOES IT START?
        ↓
WHAT MUST IT ACHIEVE?
        ↓
WHERE DOES OUR RESPONSIBILITY END?
        ↓
WHAT PROCESSES ARE REQUIRED?
```

**Do not design the implementation until these boundaries are sufficiently clear.**
