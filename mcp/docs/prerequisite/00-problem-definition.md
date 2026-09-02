# Amsha Prerequisite: Problem Definition

## 1. Purpose

This document defines the first step in designing an Amsha workflow:

> **Understand and formalize the user's problem before designing any Process, Flow, Crew, Agent, Task, Tool, Knowledge source, Memory, or MCP integration.**

Amsha must not begin by asking:

- How many agents are needed?
- How many tasks are needed?
- Should this use a Crew?
- Should this use a Flow?
- Which LLM should be used?
- Which tools should be attached?
- Should MCP be used?

Those are implementation and architecture questions.

The first question is:

> **What problem is the system actually expected to solve?**

The problem definition becomes the foundation from which the later Process, Flow, Crew, Agent, Task, and capability architecture is derived.

---

# 2. Core Principle

Amsha follows this principle:

> **Define the problem before defining the architecture.**

The correct direction is:

```text
User Problem
     ↓
Problem Definition
     ↓
Start / End Goals
     ↓
Process Decomposition
     ↓
Process Contracts
     ↓
Flow Design
     ↓
Capability Selection
     ↓
Crew / Agent / Task Design
     ↓
Implementation
````

The incorrect direction is:

```text
User Problem
     ↓
Create Agents
     ↓
Create Tasks
     ↓
Create Crew
     ↓
Create Flow
     ↓
Try to fit the problem into the architecture
```

The second approach encourages unnecessary agents, oversized tasks, unnecessary Crews, excessive context, and monolithic workflows.

---

# 3. What Is a Problem?

A problem is the meaningful transformation the user wants the system to accomplish.

A problem should describe:

1. What exists now.
2. What needs to change.
3. What the desired result is.
4. What constitutes completion.
5. What constraints matter.

A problem is **not** an implementation plan.

### Bad

```text
Create three CrewAI agents using a sequential Crew
and connect them through a Flow.
```

This describes an implementation.

### Good

```text
Given a screenplay chapter summary and its surrounding
story context, produce a validated chapter development
package that identifies the chapter's narrative role,
goal, character contribution, and thematic contribution.
```

This describes the actual problem.

---

# 4. Problem Definition Is Architecture-Neutral

At this stage, do not decide whether the solution requires:

* Python
* Agent
* Task
* Crew
* Flow
* Tool
* MCP
* Knowledge
* Memory
* Skill
* a particular LLM
* a particular CrewAI process

Those decisions belong to later stages.

The problem definition should remain valid even if the eventual implementation changes.

For example:

```text
Problem:
Evaluate a generated screenplay chapter against
defined narrative quality criteria.
```

The implementation might eventually be:

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

The problem definition should not change merely because the implementation changes.

---

# 5. Required Problem Definition

A complete Amsha problem definition should establish at least:

```text
Problem
Start Condition
Desired End Condition
Primary Objective
Constraints
Success Definition
```

Conceptually:

```text
                 PROBLEM
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
      START STATE          END STATE
          │                   │
          └─────────┬─────────┘
                    ▼
                OBJECTIVE
                    │
                    ▼
               CONSTRAINTS
                    │
                    ▼
             SUCCESS CRITERIA
```

---

# 6. Problem Statement

The problem statement should be concise but meaningful.

It should answer:

> **What transformation does the user need?**

### Example

```yaml
problem:
  statement: >
    Transform an existing chapter summary into a structured
    chapter development specification that clearly defines
    the chapter's narrative role, objective, character contribution,
    and thematic contribution.
```

The statement should describe the desired transformation without prescribing implementation.

---

# 7. Start Condition

The start condition defines what must exist before the workflow can begin.

It answers:

> **What is available when this problem starts?**

Example:

```yaml
start:
  condition: >
    A chapter summary, relevant story context,
    and narrative-structure information are available.
```

More explicitly:

```yaml
start:
  inputs:
    - chapter_summary
    - story_context
    - narrative_stage
```

The start condition should distinguish between:

### Required inputs

Information without which the problem cannot reasonably begin.

### Optional inputs

Information that can improve the result but is not mandatory.

Example:

```yaml
start:
  required:
    - chapter_summary

  optional:
    - story_context
    - character_profiles
    - narrative_stage
```

---

# 8. End Condition

The end condition defines what constitutes completion.

It answers:

> **When can we say that the problem has been successfully solved?**

Example:

```yaml
end:
  condition: >
    A validated chapter development specification exists
    and satisfies the required quality criteria.
```

Do not define completion as:

```text
Crew completed.
```

or:

```text
Agent returned an answer.
```

Technical execution completion is not necessarily problem completion.

The system should distinguish:

```text
Execution completed
```

from:

```text
Problem successfully solved
```

---

# 9. Start State and End State

For more complex problems, define the states explicitly.

Example:

```yaml
start_state:
  chapter:
    status: "summary_available"

end_state:
  chapter:
    status: "development_specification_validated"
```

Conceptually:

```text
START
Summary Available
       │
       │
       ▼
   PROCESSING
       │
       ▼
END
Validated Development Specification
```

This provides the foundation for later Flow state design.

---

# 10. Primary Objective

The primary objective describes the main outcome.

It should answer:

> **What is the most important thing this system must accomplish?**

Example:

```yaml
objective: >
  Produce a coherent and validated chapter development
  specification that advances the overall narrative.
```

The objective should not become a list of implementation instructions.

### Bad

```yaml
objective: >
  Ask an LLM to analyze the chapter, call three agents,
  compare their answers, use memory, then ask an evaluator
  to score the result.
```

### Good

```yaml
objective: >
  Produce a validated chapter development specification
  aligned with the overall narrative.
```

---

# 11. Secondary Objectives

Some problems have supporting objectives.

These may include:

* consistency
* quality
* accuracy
* completeness
* efficiency
* traceability
* safety
* format compliance

Example:

```yaml
secondary_objectives:
  - preserve established story continuity
  - maintain character consistency
  - preserve narrative intent
  - produce structured output
```

Secondary objectives should not obscure the primary objective.

---

# 12. Constraints

Constraints define boundaries within which the problem must be solved.

Examples:

```yaml
constraints:
  - preserve established character motivations
  - do not contradict the story bible
  - output must conform to the defined schema
  - existing story facts must not be invented
  - output must remain compatible with the next process
```

Constraints can be:

### Data constraints

```text
Required input format
Required fields
Allowed values
```

### Quality constraints

```text
Minimum quality score
Accuracy requirements
Consistency requirements
```

### Operational constraints

```text
Maximum iterations
Maximum execution time
Maximum cost
```

### Human constraints

```text
Human approval required
Human review required before proceeding
```

Do not prematurely convert constraints into implementation mechanisms.

For example:

```text
"Maximum three iterations"
```

is a problem constraint.

Whether that becomes a Flow loop, retry mechanism, or another implementation mechanism is decided later.

---

# 13. Success Definition

The problem must have an observable definition of success.

Ask:

> **What evidence would demonstrate that the desired outcome has been achieved?**

Example:

```yaml
success:
  conditions:
    - output_schema_valid
    - narrative_role_defined
    - chapter_goal_defined
    - contribution_defined
    - no critical continuity conflicts
    - quality_score >= minimum_threshold
```

Success criteria should be measurable whenever practical.

Avoid:

```text
The output should be good.
```

Prefer:

```text
The output must satisfy all required structural checks
and achieve the minimum evaluation threshold.
```

---

# 14. Problem vs Process

Do not confuse the overall problem with its Processes.

Example problem:

```text
Produce a validated screenplay chapter.
```

Possible Processes:

```text
P1: Analyze source material
P2: Define chapter objectives
P3: Generate chapter
P4: Evaluate chapter
P5: Improve chapter
P6: Approve chapter
```

The problem is the **overall desired transformation**.

The Processes are the **meaningful transformations required to achieve it**.

At this stage, do not yet determine whether P1 is Python, an Agent, or a Crew.

That comes later.

---

# 15. Problem vs Task

A problem can contain many Tasks.

For example:

```text
Problem:
Produce a validated chapter.

Process:
Evaluate chapter.

Task:
Evaluate character consistency.
```

Therefore:

```text
Problem
   ↓
Processes
   ↓
Implementation
   ↓
Crew
   ↓
Tasks
```

Do not jump directly from the problem to Tasks.

---

# 16. Problem vs Flow

A problem describes **what must be achieved**.

A Flow describes **how execution moves between Processes**.

Example:

```text
Problem:
Produce a validated chapter.
```

Later:

```text
Flow:

Analyze
   ↓
Generate
   ↓
Evaluate
   ↓
 ┌─┴─────────┐
 │           │
PASS        FAIL
 │           │
 ▼           ▼
Approve    Improve
             │
             └──► Evaluate
```

The Flow should be derived from the problem and Process architecture.

It should not be invented before those are understood.

---

# 17. Problem Definition Should Be Implementation-Neutral

The following should normally NOT appear in the initial problem definition:

```text
GPT-5
CrewAI
Crew
Agent
Task
Flow
MCP
Ollama
Python
Knowledge
Memory
```

unless the user explicitly imposes one as a requirement or constraint.

For example:

```text
User requirement:
"The system must run locally using Ollama."
```

That is a legitimate constraint.

But:

```text
Use three agents and one Crew.
```

should not automatically become the architecture.

Amsha should first determine whether that architecture is actually justified.

---

# 18. Handling Ambiguous Problems

User requests are often underspecified.

Example:

```text
"Build a system that improves my screenplay."
```

This is insufficient.

Amsha should identify missing information:

```text
What does "improve" mean?

Story structure?
Character development?
Dialogue?
Pacing?
Grammar?
Genre?
Continuity?
All of the above?
```

The system should not invent critical requirements.

Instead:

```text
Ambiguous requirement
       ↓
Identify missing information
       ↓
Ask targeted clarification
       ↓
Complete problem definition
```

Only non-critical assumptions may be explicitly recorded.

---

# 19. Assumptions

If assumptions are necessary, record them separately.

Example:

```yaml
assumptions:
  - chapter summaries are written in structured text
  - the story bible is authoritative for established facts
  - evaluation criteria are supplied by the user
```

Never silently turn assumptions into facts.

A later validation stage can inspect assumptions.

---

# 20. Out of Scope

A strong problem definition should sometimes explicitly state what is not part of the problem.

Example:

```yaml
out_of_scope:
  - final publishing
  - audiobook generation
  - image generation
  - marketing copy
```

This prevents Process decomposition from expanding indefinitely.

---

# 21. Problem Granularity

A problem should be large enough to represent a meaningful user objective but bounded enough to have a recognizable completion condition.

### Too broad

```text
Build an entire entertainment production platform.
```

### Better

```text
Produce a validated screenplay chapter from
an approved chapter specification.
```

### Too narrow

```text
Change one punctuation mark.
```

The correct granularity depends on the user's actual objective.

Amsha should not artificially enlarge or fragment the problem.

---

# 22. Problem Definition Output

Amsha should produce a structured Problem Definition before proceeding.

Recommended structure:

```yaml
problem_definition:

  problem:
    statement: ""

  start:
    condition: ""
    required_inputs: []
    optional_inputs: []

  end:
    condition: ""

  objective:
    primary: ""
    secondary: []

  constraints:
    data: []
    quality: []
    operational: []
    human: []

  success:
    conditions: []

  assumptions: []

  out_of_scope: []
```

This is a conceptual specification, not yet a CrewAI implementation.

---

# 23. Example

## User Request

```text
I want a system that takes a chapter summary
and creates a better chapter.
```

### Insufficient Definition

```yaml
problem:
  statement: "Create a better chapter."
```

This is ambiguous because "better" is undefined.

Amsha should identify questions such as:

```text
What does "better" mean?

- More detailed?
- Better character development?
- Better pacing?
- Better suspense?
- Better prose?
- Better continuity?
- Better genre alignment?
```

---

## Refined Definition

Suppose the user clarifies:

```text
The system should expand the chapter while preserving
the established story, strengthening character development,
and increasing suspense. The result must be evaluated
before it is accepted.
```

Amsha can now create:

```yaml
problem_definition:

  problem:
    statement: >
      Transform an existing chapter summary into a richer
      chapter while preserving established story continuity,
      strengthening character development, and increasing
      narrative suspense.

  start:
    condition: >
      A chapter summary and relevant story reference
      information are available.

    required_inputs:
      - chapter_summary

    optional_inputs:
      - story_bible
      - character_profiles
      - previous_evaluation

  end:
    condition: >
      A revised chapter has been produced and satisfies
      the defined evaluation criteria.

  objective:
    primary: >
      Produce a richer chapter that preserves narrative
      continuity while improving character development
      and suspense.

    secondary:
      - maintain established character behavior
      - preserve important story facts
      - maintain genre consistency

  constraints:
    data:
      - established story facts must be preserved

    quality:
      - character motivations must remain coherent
      - suspense must support the existing narrative

    operational: []

    human:
      - final approval may be required before publication

  success:
    conditions:
      - chapter is structurally valid
      - continuity requirements are satisfied
      - character development requirements are satisfied
      - suspense requirements are satisfied
      - evaluation threshold is achieved

  assumptions: []

  out_of_scope:
    - final publishing
    - marketing
    - unrelated chapters
```

Only after this definition is accepted should Amsha proceed to Process Decomposition.

---

# 24. Validation Checklist

Before leaving the Problem Definition stage, Amsha should verify:

### Problem

* [ ] Is the problem clearly stated?
* [ ] Does it describe the desired transformation?
* [ ] Is it implementation-neutral?
* [ ] Is the problem bounded?

### Start

* [ ] Is the starting condition known?
* [ ] Are required inputs identified?
* [ ] Are optional inputs distinguished?

### End

* [ ] Is the desired end state explicit?
* [ ] Is completion observable?
* [ ] Is technical completion distinguished from successful completion?

### Objective

* [ ] Is there one clear primary objective?
* [ ] Are secondary objectives genuinely secondary?

### Constraints

* [ ] Are important constraints identified?
* [ ] Are assumptions separated from facts?
* [ ] Is out-of-scope work identified where necessary?

### Success

* [ ] Can success be evaluated?
* [ ] Are quality requirements measurable where practical?

### Architecture Independence

* [ ] No unnecessary Agent decisions?
* [ ] No unnecessary Task decisions?
* [ ] No premature Crew decisions?
* [ ] No premature Flow decisions?
* [ ] No premature Tool/MCP decisions?

If these checks fail, the problem definition should be revised before Process Decomposition.

---

# 25. Anti-Patterns

## 25.1 Architecture-first thinking

### Bad

```text
We need a CrewAI Flow with four agents.
What should they do?
```

### Good

```text
What problem needs to be solved?
What Processes are required?
What architecture best implements those Processes?
```

---

## 25.2 Vague success

### Bad

```text
Produce a high-quality result.
```

### Good

```text
Produce a result satisfying the required schema,
quality criteria, and minimum evaluation threshold.
```

---

## 25.3 Hidden assumptions

### Bad

```text
The user obviously wants three rounds of revision.
```

### Good

```yaml
assumptions:
  - maximum revision rounds are currently unspecified
```

Then resolve the requirement or establish it as a later constraint.

---

## 25.4 Mixing implementation into the problem

### Bad

```text
Use a senior writer Agent with a research Tool
inside a sequential Crew.
```

### Good

```text
Produce a chapter that satisfies the defined
narrative requirements.
```

The implementation is derived later.

---

## 25.5 Defining completion by execution

### Bad

```text
The Crew completed successfully.
```

### Good

```text
The required output was produced, validated,
and passed the required quality gate.
```

---

# 26. Relationship to the Next Prerequisite

This document should end at the problem boundary.

It should **not** perform Process decomposition.

The next document:

```text
01-goal-and-boundary-definition.md
```

will take the validated Problem Definition and establish the precise:

```text
START
   ↓
BOUNDARY
   ↓
END
```

Then:

```text
02-process-decomposition.md
```

will derive:

```text
Process 1
Process 2
...
Process N
```

Therefore the prerequisite chain is:

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
```

---

# 27. Amsha Rule

The final rule of this document is:

> **Never design the CrewAI implementation before the problem has been sufficiently defined.**

The Amsha decision hierarchy is:

```text
WHAT PROBLEM?
      ↓
WHAT GOAL?
      ↓
WHAT PROCESSES?
      ↓
WHAT FLOW?
      ↓
WHAT CAPABILITIES?
      ↓
WHAT CREW?
      ↓
WHAT AGENTS?
      ↓
WHAT TASKS?
      ↓
WHAT IMPLEMENTATION?
```

**Problem first. Architecture second. Implementation last.**