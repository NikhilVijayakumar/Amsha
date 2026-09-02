# Amsha Prerequisite: Process Decomposition

## 1. Purpose

This document defines how Amsha decomposes a validated problem and its bounded goal into a set of meaningful, manageable Processes.

The preceding stages establish:

```text
00 Problem Definition
        ↓
01 Goal & Boundary Definition
        ↓
02 Process Decomposition
````

The purpose of Process Decomposition is to answer:

> **What meaningful transformations must occur between the defined start state and the desired end state?**

At this stage, Amsha determines **what needs to happen**, not **how it will be implemented**.

Implementation decisions such as Agent, Task, Crew, Python, Tool, Knowledge, Memory, Skill, MCP, and Flow mechanisms are deliberately deferred.

---

# 2. Core Principle

Amsha follows:

> **Decompose the goal into the smallest set of meaningful Processes required to transform the start state into the desired end state.**

The decomposition should be:

* complete enough to achieve the goal
* small enough to understand
* meaningful enough to validate
* independently describable
* composable
* bounded
* free from unnecessary implementation details

Conceptually:

```text
START STATE
     │
     ▼
Process 1
     │
     ▼
Process 2
     │
     ▼
Process 3
     │
     ▼
Process N
     │
     ▼
END STATE
```

The Processes form the **logical work required by the problem**.

---

# 3. Process Is a Logical Transformation

A Process represents a meaningful transformation of information, state, artifact, decision, or result.

Conceptually:

```text
Input State
     │
     ▼
  Process
     │
     ▼
Output State
```

For example:

```text
Chapter Summary
     │
     ▼
Analyze Chapter
     │
     ▼
Chapter Analysis
```

Then:

```text
Chapter Analysis
     │
     ▼
Define Chapter Objectives
     │
     ▼
Chapter Specification
```

A Process is therefore not merely a verb such as:

```text
Analyze
Generate
Review
```

It should represent a meaningful unit of work:

```text
Analyze the chapter's narrative function
```

---

# 4. Process Decomposition Is Implementation-Neutral

Do not determine implementation during decomposition.

### Incorrect

```text
Process 1:
Use Agent A with Task A.

Process 2:
Use Crew B with three agents.

Process 3:
Call ComfyUI through MCP.
```

These are implementation decisions.

### Correct

```text
Process 1:
Analyze source material.

Process 2:
Generate the required artifact.

Process 3:
Evaluate the artifact.

Process 4:
Improve the artifact based on evaluation.
```

Only later should Amsha determine whether each Process requires:

```text
Python
Agent
Task
Crew
Tool
MCP
Knowledge
Memory
Skill
```

---

# 5. Start With the End Goal

Process decomposition begins from the validated end goal.

Ask:

> **What must happen for the start state to become the desired end state?**

Example:

```text
START

Chapter summary exists.

        ↓

END

Validated chapter exists.
```

Work backward conceptually:

```text
What is required to produce a validated chapter?
        ↓
A chapter must be evaluated.

What is required before evaluation?
        ↓
A chapter must be generated.

What is required before generation?
        ↓
The chapter requirements must be understood.

What is required before that?
        ↓
The source material must be analyzed.
```

This may produce:

```text
P1 Analyze Source
        ↓
P2 Define Chapter Requirements
        ↓
P3 Generate Chapter
        ↓
P4 Evaluate Chapter
        ↓
P5 Improve Chapter
        ↓
P6 Approve Chapter
```

---

# 6. Do Not Assume a Sequential Process

Processes do not always form a simple sequence.

The logical structure may contain:

* sequential Processes
* parallel Processes
* conditional Processes
* iterative Processes
* optional Processes
* human approval boundaries

For example:

```text
              ┌── Process A ──┐
START ────────┤               ├── Process C
              └── Process B ──┘
```

Or:

```text
Process A
    ↓
Process B
    ↓
 ┌──┴──────┐
 │         │
PASS      FAIL
 │         │
 ▼         ▼
Process C Process D
```

At this stage, identify the logical relationship.

Detailed Flow implementation belongs to the later Flow design stage.

---

# 7. Process Decomposition Should Follow Meaningful Boundaries

Create a new Process when there is a meaningful change in:

* objective
* transformation
* output
* validation requirement
* responsibility
* dependency
* decision boundary
* human approval boundary

Example:

```text
Analyze Source
       ↓
Generate Draft
```

These are naturally separate because they have different purposes and outputs.

---

# 8. Do Not Decompose Arbitrarily

Do not create Processes merely because an operation contains several steps.

### Over-decomposed

```text
P1 Open file
P2 Read file
P3 Extract text
P4 Store text
P5 Send text
P6 Receive text
P7 Parse response
```

If these operations collectively represent one meaningful transformation, they should not automatically become seven Processes.

Instead:

```text
P1 Prepare Source Material
```

The internal implementation may later contain several Python operations or Tasks.

Process decomposition is about **meaningful work boundaries**, not line-by-line execution.

---

# 9. Avoid God Processes

A Process should not contain an entire workflow.

### Bad

```text
P1:
Analyze the source, generate the artifact,
evaluate it, revise it, approve it,
publish it, and notify the user.
```

This is effectively an entire workflow disguised as one Process.

### Better

```text
P1 Analyze
P2 Generate
P3 Evaluate
P4 Improve
P5 Approve
P6 Publish
```

Each Process has a distinct responsibility.

---

# 10. Process Granularity

The objective is **minimum sufficient decomposition**.

Too coarse:

```text
P1 Create Everything
```

Too fine:

```text
P1 Read
P2 Parse
P3 Copy
P4 Transform
P5 Save
```

Appropriate:

```text
P1 Analyze Source
P2 Generate Result
P3 Evaluate Result
P4 Improve Result
```

The correct question is:

> **Can this unit be understood, validated, and replaced as one meaningful transformation?**

If yes, it may be an appropriate Process.

---

# 11. Process Independence

A Process should have a recognizable responsibility.

A Process does not need to be completely independent from other Processes.

It may depend on previous results.

For example:

```text
P1
Input: Source
Output: Analysis

P2
Input: Analysis
Output: Specification

P3
Input: Specification
Output: Draft
```

The Processes are dependent, but each has a clear boundary.

Therefore:

> **Process independence means clear responsibility, not absence of dependencies.**

---

# 12. Process Inputs

During decomposition, identify what information each Process requires.

Example:

```yaml
process:
  id: generate_chapter

  input:
    - chapter_specification
    - story_context
```

Inputs may come from:

* the workflow start input
* previous Process outputs
* approved external information
* user-provided information

Do not automatically pass every previous output into every Process.

Only required information should cross the Process boundary.

---

# 13. Process Outputs

Each Process should produce a meaningful result.

Example:

```yaml
process:
  id: analyze_chapter

  output:
    - chapter_analysis
```

Avoid outputs such as:

```text
"some data"
"result"
"response"
"information"
```

Prefer explicit domain outputs:

```text
chapter_analysis
chapter_specification
draft_chapter
evaluation_report
revision_feedback
approved_chapter
```

The output becomes the input contract for downstream Processes.

Detailed input/output contracts are defined in:

```text
03-process-contracts-and-atomicity.md
```

---

# 14. Process Dependencies

Identify dependencies between Processes.

Example:

```text
P1 Analyze
 │
 ▼
P2 Specify
 │
 ▼
P3 Generate
 │
 ▼
P4 Evaluate
```

This implies:

```text
P2 depends on P1
P3 depends on P2
P4 depends on P3
```

Dependencies should be explicit rather than hidden inside Process descriptions.

---

# 15. Dependency Graph

For larger problems, represent Processes as a directed graph.

Example:

```text
                 P1
                 │
        ┌────────┴────────┐
        ▼                 ▼
       P2                P3
        │                 │
        └────────┬────────┘
                 ▼
                P4
                 │
                 ▼
                P5
```

This indicates that P4 requires outputs from both P2 and P3.

The graph should be logically valid before Flow implementation begins.

---

# 16. Parallel Processes

Processes may be parallel when they:

1. Have independent inputs.
2. Do not modify the same required state in conflicting ways.
3. Do not depend on each other's output.
4. Can safely execute independently.

Example:

```text
                 P1
                 │
        ┌────────┴────────┐
        ▼                 ▼
   Analyze Plot     Analyze Characters
        │                 │
        └────────┬────────┘
                 ▼
             P4 Integrate
```

Do not make Processes parallel merely to increase apparent complexity.

Parallelism should be justified by actual independence.

---

# 17. Sequential Processes

Processes should be sequential when one depends on the result of another.

Example:

```text
P1 Analyze
   ↓
P2 Generate
   ↓
P3 Evaluate
```

The dependency itself determines the ordering.

Do not introduce artificial sequential dependencies when Processes can safely operate independently.

---

# 18. Conditional Processes

Some Processes are only required under certain conditions.

Example:

```text
P1 Evaluate
     │
     ├── PASS → P3 Approve
     │
     └── FAIL → P2 Improve
```

The condition belongs to the logical Process architecture.

The exact CrewAI Flow routing implementation belongs later.

---

# 19. Iterative Processes

Some problems require repeated improvement.

Example:

```text
P1 Generate
     ↓
P2 Evaluate
     ↓
   ┌─┴─────────────┐
   │               │
 PASS             FAIL
   │               │
   ▼               ▼
 P4 Final       P3 Improve
                   │
                   └──────► P2
```

The Process decomposition should identify the iteration.

However, do not yet define implementation details such as:

```text
@router
while loop
Flow listener
retry decorator
```

Those belong to Flow Engineering.

---

# 20. Human Review Processes

Human review may be a Process or a boundary between Processes depending on its role.

For example:

```text
P1 Generate Specification
        ↓
P2 Validate Specification
        ↓
Human Review
        ↓
P3 Generate Artifact
```

If the human review is itself a meaningful decision boundary, model it explicitly.

Example:

```text
P2 Human Approval
```

The important point is that human approval should not be hidden inside another Process when it materially affects workflow progression.

---

# 21. Process Outputs Should Enable the Next Process

A useful decomposition test is:

> **Can the output of one Process meaningfully become the input to another Process?**

Example:

```text
P1
Input:
Raw chapter

Output:
Chapter analysis

       ↓

P2
Input:
Chapter analysis

Output:
Chapter specification
```

This creates a clear composition.

If a Process produces an output that nobody uses, question whether the Process is necessary.

---

# 22. Avoid Unnecessary Intermediate Processes

Not every transformation deserves a Process.

Example:

```text
P1 Analyze
     ↓
P2 Convert JSON to dictionary
     ↓
P3 Generate
```

If JSON conversion is merely an implementation detail, it should not necessarily become a Process.

Later it might simply be:

```text
Python operation inside P1/P3
```

or another implementation mechanism.

A Process should exist because it represents **meaningful work**, not because a programmer can identify another function.

---

# 23. Process Reuse

A Process may be reusable across workflows.

For example:

```text
Evaluate Narrative Consistency
```

might be used by:

```text
Chapter Workflow
Novel Workflow
Screenplay Workflow
Character Workflow
```

Reusable Processes should remain domain-appropriate and have clear contracts.

Do not make reusable Processes so generic that their purpose becomes ambiguous.

---

# 24. Process Naming

Process names should describe meaningful work.

Prefer:

```text
analyze_source
define_requirements
generate_draft
evaluate_draft
improve_draft
approve_result
```

Avoid:

```text
step1
step2
process_data
do_work
agent_process
crew_process
llm_step
```

Do not encode implementation in the Process name.

### Bad

```text
gpt_generation_process
crew_evaluation_process
mcp_render_process
```

### Good

```text
generate_visual_asset
evaluate_visual_asset
render_scene
```

---

# 25. Process Description

Each Process should have a concise description.

Example:

```yaml
process:
  id: evaluate_chapter

  description: >
    Evaluate the generated chapter against the approved
    narrative, character, continuity, and quality criteria.
```

The description should explain:

* what the Process accomplishes
* why it exists
* what meaningful transformation occurs

It should not contain implementation instructions.

---

# 26. Process Decomposition From the Goal

Given:

```text
START:
Chapter summary exists.

END:
Validated chapter exists.
```

Ask:

### Question 1

What must happen before the final chapter can be validated?

```text
A chapter must exist.
```

### Question 2

What must happen before a chapter can be generated?

```text
Its requirements must be defined.
```

### Question 3

What must happen before requirements can be defined?

```text
The source must be understood.
```

This produces:

```text
P1 Analyze Source
     ↓
P2 Define Chapter Requirements
     ↓
P3 Generate Chapter
     ↓
P4 Evaluate Chapter
```

If evaluation fails:

```text
P4 Evaluate
     │
     ├── PASS → END
     │
     └── FAIL → P5 Improve
                    │
                    └──────► P4
```

This is a logical Process architecture.

Only later do we decide how each Process is implemented.

---

# 27. Completeness Test

The Process graph should be capable of explaining how the start state becomes the end state.

Ask:

> **If I execute these Processes correctly, is there any required transformation missing?**

For example:

```text
START
Chapter Summary
   ↓
P1 Analyze
   ↓
P2 Generate
   ↓
P3 Evaluate
   ↓
END
Validated Chapter
```

If evaluation can fail and no improvement/recovery path exists, the decomposition may be incomplete.

---

# 28. Necessity Test

For every Process, ask:

> **Is this Process necessary to achieve the goal?**

If removing it does not materially affect the outcome, question whether it belongs in the workflow.

Example:

```text
P1 Analyze
P2 Generate
P3 Create Report About Generation
P4 Evaluate
```

If P3 is not required by the goal, it may be unnecessary.

This prevents process inflation.

---

# 29. Sufficiency Test

For the complete Process graph, ask:

> **Are these Processes sufficient to achieve the goal?**

A Process graph should not merely describe some of the work.

It should account for every meaningful transformation required between:

```text
START
```

and:

```text
END
```

---

# 30. Boundary Test

Every Process should have a recognizable boundary.

Ask:

```text
What enters this Process?
What meaningful transformation occurs?
What leaves this Process?
```

If those questions cannot be answered clearly, the Process may be:

* too broad
* too vague
* unnecessary
* actually a collection of Processes
* actually an implementation detail

---

# 31. No Implementation Leakage

During Process Decomposition, avoid introducing:

```text
Agent
Task
Crew
Python
Tool
MCP
Knowledge
Memory
Skill
LLM
model name
temperature
prompt
```

unless one of these is explicitly part of the user's problem constraint.

For example:

```text
User constraint:
The system must use an existing Unreal Engine MCP server.
```

This can be recorded as a constraint/dependency.

But Amsha should still determine **where and why** that capability is needed.

---

# 32. Process Decomposition Output

Amsha should produce a structured Process Definition.

Recommended structure:

```yaml
process_decomposition:

  processes:

    - id: process_1
      name: ""
      purpose: ""
      inputs: []
      outputs: []
      depends_on: []

    - id: process_2
      name: ""
      purpose: ""
      inputs: []
      outputs: []
      depends_on:
        - process_1

  relationships:
    - from: process_1
      to: process_2
      type: sequential

  start_processes:
    - process_1

  terminal_processes:
    - process_n
```

At this stage, the structure describes the **logical workflow**, not its CrewAI implementation.

---

# 33. Example

## Problem

```text
Transform an existing chapter summary into a validated
chapter development specification.
```

## Start

```text
Chapter summary exists.
```

## End

```text
Validated chapter development specification exists.
```

## Process Decomposition

```yaml
process_decomposition:

  processes:

    - id: analyze_chapter
      name: Analyze Chapter
      purpose: >
        Identify the chapter's narrative function,
        character contribution, and thematic requirements.
      inputs:
        - chapter_summary
        - story_context
      outputs:
        - chapter_analysis
      depends_on: []

    - id: define_chapter_specification
      name: Define Chapter Specification
      purpose: >
        Transform the chapter analysis into explicit
        chapter objectives and requirements.
      inputs:
        - chapter_analysis
      outputs:
        - chapter_specification
      depends_on:
        - analyze_chapter

    - id: evaluate_chapter_specification
      name: Evaluate Chapter Specification
      purpose: >
        Determine whether the specification satisfies
        the required narrative and structural criteria.
      inputs:
        - chapter_specification
      outputs:
        - specification_evaluation
      depends_on:
        - define_chapter_specification

    - id: revise_chapter_specification
      name: Revise Chapter Specification
      purpose: >
        Improve the specification using validated
        evaluation feedback.
      inputs:
        - chapter_specification
        - specification_evaluation
      outputs:
        - revised_chapter_specification
      depends_on:
        - evaluate_chapter_specification

  relationships:

    - from: analyze_chapter
      to: define_chapter_specification
      type: sequential

    - from: define_chapter_specification
      to: evaluate_chapter_specification
      type: sequential

    - from: evaluate_chapter_specification
      to: revise_chapter_specification
      type: conditional
      condition: evaluation_failed

    - from: revise_chapter_specification
      to: evaluate_chapter_specification
      type: iterative

  start_processes:
    - analyze_chapter

  terminal_processes:
    - evaluate_chapter_specification
```

This is still **architecture-level reasoning**.

It has not yet said:

```text
analyze_chapter = Agent
define_chapter_specification = Crew
evaluate = Python
```

Those decisions come later.

---

# 34. Process Decomposition Validation

Before proceeding to Process Contracts and Atomicity, Amsha should validate:

## Coverage

* [ ] Every required transformation between start and end is represented.
* [ ] No essential work is missing.

## Necessity

* [ ] Every Process contributes materially to the goal.
* [ ] No Process exists only because it is technically convenient.

## Granularity

* [ ] Processes are meaningful.
* [ ] Processes are not giant workflows.
* [ ] Processes are not trivial implementation operations.

## Boundaries

* [ ] Each Process has a recognizable purpose.
* [ ] Inputs can be identified.
* [ ] Outputs can be identified.

## Dependencies

* [ ] Dependencies are explicit.
* [ ] Ordering is justified by dependencies.
* [ ] Parallel work is genuinely independent.

## Completion

* [ ] The Process graph can reach the desired end state.
* [ ] Terminal Processes are identifiable.
* [ ] Conditional/iterative paths are represented where required.

## Implementation Independence

* [ ] No unnecessary Agent decisions.
* [ ] No unnecessary Task decisions.
* [ ] No unnecessary Crew decisions.
* [ ] No premature Tool decisions.
* [ ] No premature MCP decisions.
* [ ] No premature Knowledge/Memory decisions.

---

# 35. Anti-Patterns

## 35.1 Architecture-first decomposition

### Bad

```text
We need three agents, so create three Processes.
```

### Good

```text
Determine the required transformations first,
then derive the implementation architecture.
```

---

## 35.2 God Process

### Bad

```text
Process:
Analyze, generate, evaluate, improve, approve,
publish and notify.
```

### Good

```text
Analyze
Generate
Evaluate
Improve
Approve
Publish
```

Only include the Processes actually required by the goal.

---

## 35.3 Micro-process explosion

### Bad

```text
Open file
Read file
Parse JSON
Create variable
Call function
Save file
```

### Good

```text
Prepare Source Material
```

if those operations represent one meaningful transformation.

---

## 35.4 Implementation Processes

### Bad

```text
GPT Process
Crew Process
MCP Process
Agent Process
```

### Good

```text
Generate Chapter
Render Visual Asset
Evaluate Chapter
```

---

## 35.5 Hidden Dependencies

### Bad

```text
P1 Analyze
P2 Generate
```

when P2 actually requires P1's output but this dependency is undocumented.

### Good

```text
P1 Analyze
   │
   └── chapter_analysis
          ↓
P2 Generate
```

---

## 35.6 Unused Output

### Bad

```text
P1:
Generate an analysis report.

P2:
Generate chapter.

P2 never uses the analysis.
```

Question whether P1 is necessary or whether its output should influence a downstream Process.

---

## 35.7 Undefined Terminal State

### Bad

```text
Evaluate
   ↓
Improve
   ↓
Evaluate
   ↓
Improve
   ↓
...
```

with no success or termination condition.

### Good

```text
Evaluate
   │
   ├── PASS → END
   │
   └── FAIL → Improve
                 │
                 └── Evaluate

with a defined maximum iteration boundary.
```

Detailed gates belong to later stages, but the need for termination must already be recognized.

---

# 36. Process Decomposition and Atomicity

Process Decomposition identifies the candidate Processes.

The next document establishes whether each candidate Process is sufficiently atomic.

Therefore:

```text
02 Process Decomposition
        ↓
Candidate Processes
        ↓
03 Process Contracts & Atomicity
        ↓
Validated Processes
```

Do not attempt to solve every atomicity question during initial decomposition.

First establish the logical work boundaries.

Then formally test each boundary.

---

# 37. Process Decomposition and Flow

Process Decomposition defines:

```text
WHAT WORK EXISTS
```

Flow Design later defines:

```text
HOW WORK MOVES
```

Therefore:

```text
Process Decomposition
        ↓
P1 → P2 → P3
        ↓
Flow Design
        ↓
state
transitions
routing
iteration
gates
recovery
```

Do not mix Flow implementation with Process decomposition.

---

# 38. Process Decomposition and Crew Design

A Process may later be implemented using:

```text
Python
```

or:

```text
Agent + Task
```

or:

```text
Crew
```

or:

```text
Crew + Tools
```

or:

```text
Crew + MCP
```

The Process does not determine the implementation automatically.

The later Capability Selection and Crew Engineering stages make that decision.

---

# 39. Amsha Decision Rule

The process decomposition stage follows:

```text
START
  ↓
Understand END GOAL
  ↓
Identify required transformations
  ↓
Group meaningful work
  ↓
Define candidate Processes
  ↓
Connect dependencies
  ↓
Identify sequential / parallel / conditional /
iterative relationships
  ↓
Check completeness
  ↓
Check necessity
  ↓
Check boundaries
  ↓
Pass to Process Atomicity
```

---

# 40. Final Amsha Rule

> **Do not design Agents, Tasks, Crews, Tools, Python, Knowledge, Memory, Skills, MCP, or Flow implementation until the required logical Processes have been identified and their relationships understood.**

The hierarchy is:

```text
USER PROBLEM
      ↓
GOAL & BOUNDARY
      ↓
PROCESS DECOMPOSITION
      ↓
PROCESS CONTRACT
      ↓
PROCESS ATOMICITY
      ↓
PROCESS VALIDATION
      ↓
FLOW DESIGN
      ↓
CAPABILITY SELECTION
      ↓
CREW DESIGN
      ↓
AGENT / TASK DESIGN
      ↓
IMPLEMENTATION
```

The fundamental question at this stage is:

> **"What meaningful work must happen between the defined start state and the desired end state?"**

Not:

> **"Which CrewAI components should I create?"**
