# Amsha Prerequisite: Process Decomposition

## 1. Purpose

This document defines how Amsha decomposes a validated problem and its bounded goal into a set of meaningful, manageable Processes.

> **What meaningful transformations must occur between the defined start state and the desired end state?**

At this stage, Amsha determines **what needs to happen**, not **how it will be implemented**. Implementation decisions such as Agent, Task, Crew, Tool, Knowledge, Memory, and Flow are deliberately deferred.

---

# 2. Core Principle

> **Decompose the goal into the smallest set of meaningful Processes required to transform the start state into the desired end state.**

The decomposition should be complete enough to achieve the goal, small enough to understand, meaningful enough to validate, independently describable, composable, coupled, and free from unnecessary implementation details.

---

# 3. Process Is a Logical Transformation

A Process represents a meaningful transformation of information, state, artifact, decision, or result — not merely a verb like `Analyze`, `Generate`, or `Review`, but a meaningful unit of work like "Analyze the chapter's narrative function".

---

# 4. Process Decomposition Is Implementation-Neutral

Do not determine implementation during decomposition.

```text
# Incorrect — these are implementation decisions
Process 1: Use Agent A with Task A.
Process 2: Use Crew B with three agents.
Process 3: Call ComfyUI through MCP.

# Correct — these describe logical work
Process 1: Analyze source material.
Process 2: Generate the required artifact.
Process 3: Evaluate the artifact.
Process 4: Improve the artifact based on evaluation.
```

---

# 5. Start With the End Goal

Process decomposition begins from the validated end goal. Ask: **What must happen for the start state to become the desired end state?** Work backward: to produce a validated chapter, a chapter must be evaluated; before evaluation it must be generated, and so on. This may produce a chain like P1 Analyze Source → P2 Define Requirements → P3 Generate → P4 Evaluate → P5 Improve → P6 Approve.

---

# 6. Do Not Assume a Sequential Process

Processes do not always form a simple sequence. The logical structure may contain sequential, parallel, conditional, iterative, and optional Processes, and human-approval boundaries. At this stage, identify the logical relationship; detailed Flow implementation belongs to the later Flow design stage.

---

# 7. Process Decomposition Should Follow Meaningful Boundaries

Create a new Process when there is a meaningful change in objective, transformation, output, validation requirement, responsibility, dependency, decision boundary, or human-approval boundary.

---

# 8. Do Not Decompose Arbitrarily

Do not create Processes merely because an operation contains several steps. A chain of open/read/extract/store/send/parse operations that collectively represent one meaningful transformation should stay one Process (e.g. "Prepare Source Material"), not seven. Process decomposition is about **meaningful work boundaries**, not line-by-line execution.

---

# 9. Avoid God Processes

A Process should not contain an entire workflow (analyze, generate, evaluate, revise, approve, publish, notify in one). Each Process should have a distinct responsibility.

---

# 10. Process Granularity

The objective is **minimum sufficient decomposition**. Too coarse ("Create Everything") hides the work; too fine (read/parse/copy/transform/save) fragments one transformation. The correct question: **Can this unit be understood, validated, and replaced as one meaningful transformation?** If yes, it may be an appropriate Process.

---

# 11. Process Independence

A Process should have a recognizable responsibility, but complete independence is not required — it may depend on previous results. **Process independence means clear responsibility, not absence of dependencies.**

---

# 12. Process Inputs

During decomposition, identify what information each Process requires. Inputs may come from the workflow start input, previous Process outputs, approved external information, or user-provided information. Do not automatically pass every previous output into every Process — only required information should cross the Process boundary.

---

# 13. Process Outputs

Each Process should produce a meaningful result. Avoid vague outputs (`"some data"`, `"result"`, `"response"`); prefer explicit domain outputs like `chapter_analysis`, `chapter_specification`, `evaluation_report`, `approved_chapter`. The output becomes the input contract for downstream Processes.

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

For larger problems, represent Processes as a directed graph (e.g. P1 → {P2, P3} → P4 → P5, where P4 requires outputs from both P2 and P3). The graph should be logically valid before Flow implementation begins.

---

# 16. Parallel Processes

Processes may be parallel when they have independent inputs, do not modify the same required state in conflicting ways, do not depend on each other's output, and can safely execute independently. Do not make Processes parallel merely to increase apparent complexity.

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

Some Processes are only required under certain conditions (e.g. P1 Evaluate → PASS → P3 Approve, else P2 Improve). The condition belongs to the logical architecture; the exact Flow routing implementation belongs later.

---

# 19. Iterative Processes

Some problems require repeated improvement (e.g. Generate → Evaluate → FAIL → Improve → loop back to Evaluate). Identify the iteration at this stage, but defer implementation details (`@router`, loop, Flow listener, retry decorator) to Flow Engineering.

---

# 20. Human Review Processes

Human review may be a Process or a boundary between Processes depending on its role. If the review is a meaningful decision boundary that materially affects workflow progression, model it explicitly rather than hiding it inside another Process.

---

# 21. Process Outputs Should Enable the Next Process

The composition test: **Can the output of one Process meaningfully become the input to another Process?** If a Process produces an output that nobody uses, question whether the Process is necessary.

---

# 22. Avoid Unnecessary Intermediate Processes

Not every transformation deserves a Process. A detail like JSON conversion inside a larger transformation is an implementation detail, not necessarily a Process. A Process should exist because it represents **meaningful work**, not because a programmer can identify another function.

---

# 23. Process Reuse

A Process may be reusable across workflows (e.g. "Evaluate Narrative Consistency" used by chapter, novel, screenplay, and character workflows). Reusable Processes should remain domain-appropriate and have clear contracts — do not make them so generic that their purpose becomes ambiguous.

---

# 24. Process Naming

Process names should describe meaningful work (e.g. `analyze_source`, `define_requirements`, `evaluate_draft`). Avoid generic or implementation-encoded names (`step1`, `process_data`, `do_work`, `gpt_generation_process`, `crew_evaluation_process`). Prefer domain names like `generate_visual_asset`, `evaluate_visual_asset`, `render_scene`.

---

# 25. Process Description

Each Process should have a concise description explaining what it accomplishes, why it exists, and what meaningful transformation occurs. It should not contain implementation instructions.

---

# 26. Process Decomposition From the Goal

Given START (chapter summary exists) → END (validated chapter exists), work backward: what must happen before the final chapter can be validated? (a chapter must exist) → before generation? (requirements defined) → before requirements? (source understood). This produces P1 Analyze → P2 Define Requirements → P3 Generate → P4 Evaluate, with a FAIL → Improve → re-Evaluate path. This is a logical Process architecture; implementation is decided later.

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

For every Process, ask: **Is this Process necessary to achieve the goal?** If removing it does not materially affect the outcome, question whether it belongs. This prevents process inflation.

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

Every Process should have a recognizable boundary. Ask: **What enters this Process? What meaningful transformation occurs? What leaves this Process?** If these cannot be answered clearly, the Process may be too broad, too vague, unnecessary, a collection of Processes, or an implementation detail.

---

# 31. No Implementation Leakage

During Process Decomposition, avoid introducing implementation terms (Agent, Task, Crew, Tool, MCP, Knowledge, Memory, Skill, LLM, model name, temperature, prompt) unless one is explicitly part of the user's problem constraint. A constraint like "must use an existing Unreal Engine MCP server" can be recorded as a dependency, but Amsha should still determine **where and why** that capability is needed.

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

Process Decomposition identifies candidate Processes; the next document establishes whether each is sufficiently atomic.

```text
02 Process Decomposition → Candidate Processes → 03 Process Contracts & Atomicity → Validated Processes
```

Do not solve every atomicity question during initial decomposition — first establish the logical work boundaries, then formally test each boundary.

---

# 37. Process Decomposition and Flow

Process Decomposition defines **what work exists**; Flow Design later defines **how work moves** (state, transitions, routing, iteration, gates, recovery). Do not mix Flow implementation with Process decomposition.

---

# 38. Process Decomposition and Crew Design

A Process may later be implemented using Python, Agent + Task, Crew, Crew + Tools, or Crew + MCP. The Process does not determine the implementation automatically — Capability Selection and Crew Engineering make that decision later.

---

# 39. Amsha Decision Rule

```text
Understand END GOAL → Identify required transformations → Group meaningful work
→ Define candidate Processes → Connect dependencies → Identify sequential/parallel/conditional/iterative
relationships → Check completeness → Check necessity → Check boundaries → Pass to Process Atomicity
```

---

# 40. Final Amsha Rule

> **Do not design Agents, Tasks, Crews, Tools, Knowledge, Memory, Skills, MCP, or Flow implementation until the required logical Processes have been identified and their relationships understood.**

The fundamental question at this stage: **"What meaningful work must happen between the defined start state and the desired end state?"** — not **"Which CrewAI components should I create?"**
