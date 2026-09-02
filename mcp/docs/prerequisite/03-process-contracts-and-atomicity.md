# Amsha Prerequisite: Process Contracts and Atomicity

## 1. Purpose

This document establishes a precise contract for every Process identified during Process Decomposition and verifies that each is sufficiently atomic.

`02-process-decomposition.md` answers "What meaningful Processes are required?" This document answers "What exactly does each Process accept, transform, and produce?" and "Is each Process sufficiently atomic to be independently understood, validated, implemented, and composed?"

---

# 2. Core Principle

An Amsha Process is represented as:

```text
Input
  ↓
Meaningful Transformation
  ↓
Output
```

A Process contract makes these boundaries explicit:

```text
┌──────────────────────────────────────────┐
│                 PROCESS                  │
│                                          │
│  Preconditions                           │
│        ↓                                 │
│  Input Contract                          │
│        ↓                                 │
│  Transformation                          │
│        ↓                                 │
│  Output Contract                         │
│        ↓                                 │
│  Postconditions                          │
│        ↓                                 │
│  Completion Condition                    │
└──────────────────────────────────────────┘
```

The contract describes **what the Process guarantees**.

It does not describe how the Process is implemented.

---

# 3. Process Contract vs Implementation

A Process contract must remain independent of implementation. A Process may later be implemented with Python, Agent + Task, Crew, or another mechanism, but the contract should remain unchanged.

> **A Process contract defines the logical responsibility; implementation defines how that responsibility is executed.**

---

# 4. Required Process Contract

Every Process should define at least:

```text
Process ID
Process Name
Purpose
Input
Transformation
Output
Completion Condition
```

A more complete contract should also define:

```text
Preconditions
Postconditions
Dependencies
Consumers
```

Recommended structure:

```yaml
process:
  id: ""

  name: ""

  purpose: ""

  input:
    required: []
    optional: []

  transformation: ""

  output:
    name: ""
    structure: {}

  preconditions: []

  postconditions: []

  completion:
    success: ""

  dependencies: []

  consumers: []
```

---

# 5. Process Identity

Each Process must have a stable identifier. The ID should be unique within the workflow, remain stable during refinement, and describe the Process rather than its implementation. Prefer `analyze_chapter`, `evaluate_chapter`; avoid `agent_1`, `crew_step_2`, `gpt_process`, `mcp_step`.

---

# 6. Process Name

The name should communicate the meaningful transformation (e.g. `Analyze Chapter`, `Evaluate Chapter`), and remain understandable even if the implementation is completely replaced. Avoid `Step 1`, `Process Data`, `Agent Process`, `LLM Step`.

---

# 7. Purpose

The purpose explains why the Process exists and should contain the **responsibility**, not implementation instructions. *Good:* "Evaluate the generated chapter against approved quality criteria." *Bad:* "Ask an LLM evaluator Agent to score the chapter."

---

# 8. Input Contract

The Input Contract defines what the Process accepts: **What information must this Process receive to perform its responsibility?**

```yaml
input:
  required:
    - chapter
  optional:
    - story_context
    - character_profiles
```

---

# 9. Required Inputs

Required inputs are necessary for the Process to perform its purpose. If a required input is missing, the Process should not silently invent it — the later failure-planning stage determines how missing inputs are handled.

---

# 10. Optional Inputs

Optional inputs may improve execution but are not required by the Process contract. They should not become implicit mandatory context. This supports **minimum sufficient context** — only information that is required or genuinely relevant should cross the Process boundary.

---

# 11. Input Source

Where useful, identify where each input originates (workflow input, previous process, user, configuration, external system, knowledge, memory). At this stage the source is described logically — do not decide the technical mechanism.

---

# 12. Input Scope

A Process should receive the minimum information necessary to perform its responsibility — required inputs + relevant context, not the entire workflow state, project, or all available knowledge. This improves clarity, token efficiency, reliability, reproducibility, maintainability, and validation.

---

# 13. Transformation Contract

The transformation defines the meaningful change performed by the Process. It should describe the **work**, not the implementation — it should not contain `Use Agent`, `Call LLM`, `Use Tool X`, `Call MCP`, `Use Memory`, unless these are explicit external constraints imposed by the user.

---

# 14. One Primary Transformation

A Process should have one primary transformation. A chain like Chapter → Analyze → Generate → Evaluate → Revise → Publish → Final Project contains several independent transformations — they should normally become separate Processes.

---

# 15. Output Contract

The Output Contract defines the meaningful result produced by the Process. It should be explicit enough that a downstream Process can declare it as an input.

```yaml
output:
  name: chapter_analysis
  structure:
    narrative_role: ""
    character_contribution: ""
    thematic_contribution: ""
    requirements: []
```

---

# 16. One Coherent Output

Atomicity does not require the output to contain only one field. An output with `narrative_role`, `plot_contribution`, `character_contribution`, `thematic_contribution` remains one coherent output if all fields collectively represent "Chapter Analysis". The question is whether the output represents **one meaningful result**: `One coherent output ≠ One primitive value`.

---

# 17. Multiple Independent Outputs

Multiple independent deliverables usually indicate a Process should be decomposed. If a Process generates a chapter, character design, concept art, and music specification together, these normally become separate Processes (unless the user's actual goal defines them as one inseparable production package).

---

# 18. Output Consumers

Identify which downstream Process consumes the output. If an output has no consumer, ask why it exists. Legitimate exceptions include human-review artifacts, audit artifacts, persistent records, observability artifacts, and final workflow output — these should be intentional.

---

# 19. Postconditions

Postconditions define what is guaranteed after successful Process completion (e.g. `chapter_analysis_exists`, `required_fields_are_present`, `output_schema_is_valid`). They describe a state that downstream Processes can rely upon.

---

# 20. Completion Condition

A Process must define what successful completion means. This distinguishes "Process executed" from "Process successfully completed" — returning a response does not automatically mean the Process succeeded.

---

# 21. Preconditions

Preconditions define what must be true before the Process can begin. They should be meaningful to the Process — do not add technical conditions merely because they are convenient for implementation.

---

# 22. Dependencies

A Process may depend on another Process (e.g. `define_chapter_specification` depends on `analyze_chapter`). Dependencies should be explicit, not hidden inside Process descriptions.

---

# 23. Contract Compatibility

The output contract of one Process must be compatible with the input contract of the next. The contracts should agree on identity, structure, semantics, required fields, data type, and status/lifecycle where relevant.

```text
Producer Output → Contract Boundary → Consumer Input
```

---

# 24. Contract Compatibility Example

If the producer `analyze_chapter` outputs `chapter_analysis` (with `narrative_role`, `character_contribution`, `thematic_contribution`) and the consumer `define_chapter_specification` requires it, the consumer can rely on the producer's contract. If the consumer additionally requires `plot_contribution` that the producer does not provide, the contract is incomplete — Amsha should detect this before implementation.

---

# 25. Contract Completeness

A Process contract is complete when these can be answered: What enters? Why is it needed? What transformation occurs? What leaves? What does successful completion mean? What can downstream Processes rely on? If these cannot be answered clearly, the Process is not ready for validation.

---

# 26. Atomicity

Atomicity is a property of the Process boundary: **A Process with one coherent responsibility, one primary transformation, and one coherent output that can be independently understood and validated.**

Atomicity does not mean one line, one function, one instruction, one LLM call, or one Task. It means one meaningful responsibility + one coherent transformation + one coherent result + a clear boundary.

---

# 27. Atomicity Tests

Apply these tests to each Process:

**Test 1 — Purpose:** Does the Process have one clear primary purpose? *Non-atomic:* "Analyze Chapter, rewrite Chapter, generate concept art, and publish Chapter."

**Test 2 — Transformation:** Does the Process perform one coherent transformation? *Non-atomic:* Chapter Summary → Analysis → Generation → Evaluation → Revision.

**Test 3 — Output:** Does the Process produce one coherent result? *Non-atomic:* "Generate Chapter + Generate Character Design + Generate Marketing Copy."

**Test 4 — Responsibility:** Does a substantial portion represent a different responsibility? *Non-atomic:* "Analyze Screenplay + Develop Marketing Strategy." (But do not split merely because several techniques are used internally.)

**Test 5 — Independent Validation:** Can the result be meaningfully evaluated independently? "Analyze Chapter" can; "Generate + Evaluate + Improve Chapter" contains multiple lifecycle stages.

**Test 6 — Independent Completion:** Can the Process reach a meaningful completion state without completing unrelated work? "Evaluate Chapter" has a clear completion (evaluation produced and valid); "Create Final Production" has several unrelated completion conditions.

**Test 7 — Different Validation Criteria:** Substantially different validation criteria signal decomposition (e.g. "Generate Screenplay" requires narrative quality, character consistency, pacing; "Generate Concept Art" requires visual consistency, composition, style).

**Test 8 — Different Failure Domains:** Substantially different failure modes may indicate a Process boundary (e.g. generation failure vs publishing failure have different recovery behavior). Detailed failure handling is in `06-corner-cases-and-failure-planning.md`.

**Test 9 — Human Decision Boundary:** A distinct human approval decision justifies a Process boundary (Generate Story Concept → Human Approval → Generate Screenplay). Do not hide a significant approval inside an unrelated Process.

**Test 10 — Implementation Leakage:** A Process is suspicious when its definition is dominated by implementation details. *Bad:* "Call GPT, parse the response, call another Agent, run Python, call MCP, save JSON." *Better:* "Evaluate the generated chapter against approved criteria."

---

# 37. Internal Complexity Does Not Break Atomicity

An atomic Process may contain several internal operations (inspect structure, check continuity, check characterization, evaluate pacing, calculate scores) and still be one atomic Process as long as all operations contribute to one coherent responsibility like "Evaluate Chapter". Do not create a separate Process for every internal operation.

---

# 38. Implementation Detail vs Meaningful Process

A useful question: **Would a user or domain expert recognize this as meaningful work, or is it merely an implementation operation?**

* Likely Process: "Evaluate Chapter"; likely implementation detail: "Parse JSON"; "Prepare Chapter for Evaluation" may be a Process if preparation is a meaningful transformation with an independently useful result. The distinction depends on the problem domain and workflow boundary.

---

# 39. Over-Decomposition

Do not create Processes for every technical operation. If open/read/parse/extract/store operations collectively represent one meaningful preparation operation, they should remain implementation details — possibly a single "Prepare Source Material" Process.

---

# 40. Under-Decomposition

Do not hide an entire workflow inside one Process. If "P1 Create Final Chapter" actually means analyze, define, generate, evaluate, improve, approve, publish, these are distinct transformations that should normally become separate Processes.

---

# 41. Minimum Sufficient Atomicity

Amsha seeks **the minimum number of meaningful Processes necessary to preserve clear responsibility, validation, composition, and control**. Too coarse → God Process; too fine → micro-process explosion. Optimize for **meaningful boundaries**, not the smallest or largest possible number.

---

# 42. Process Atomicity vs Task Atomicity

Process atomicity and Task atomicity operate at different levels. A Process describes a workflow-level transformation; a Task describes a unit of work assigned within an Agent/Crew implementation. A Process (e.g. "Evaluate Chapter") may contain multiple Tasks (evaluate narrative structure, evaluate character consistency) while remaining atomic at the Process level. `Process Atomicity ≠ Task Atomicity` — evaluate each boundary independently.

---

# 43. Process Atomicity vs Crew

A Crew may implement one Process (Process → Crew → Agents/Tasks), but a Crew should not determine the Process boundary. The logical Process comes first; the implementation is derived later.

---

# 44. Process Atomicity vs Python

If a Process is implemented using Python, the implementation should preserve the Process boundary. Avoid a monolithic `execute_everything()` function; prefer smaller deterministic operations (`validate_input`, `transform_data`, `validate_output`). **Atomicity applies to deterministic code as well as LLM-based work.**

---

# 45. Process Contract and Context

A Process contract should not automatically include every available context source. Distinguish input, context, knowledge, and memory. Define what information is logically required here; later Capability Selection determines whether it comes from direct input, Flow state, Knowledge, Memory, Tool, or MCP. The contract describes the **information requirement**, not the mechanism.

---

# 46. Process Contract and Validation

The contract provides the foundation for deterministic validation: required input exists, input structure valid, required fields present, output exists, output structure/type valid, postconditions satisfied. Where semantic quality cannot be determined deterministically, later evaluation mechanisms may be introduced. Do not use an LLM for a validation problem that deterministic validation can reliably solve.

---

# 47. Example: Valid Atomic Process

```yaml
process:
  id: analyze_chapter

  name: Analyze Chapter

  purpose: >
    Identify the chapter's narrative function,
    character contribution, thematic contribution,
    and major development requirements.

  input:
    required:
      - chapter_summary

    optional:
      - story_context
      - character_profiles

  transformation: >
    Analyze the supplied chapter information and produce
    a structured narrative analysis.

  output:
    name: chapter_analysis

    structure:
      narrative_role: ""
      plot_contribution: ""
      character_contribution: ""
      thematic_contribution: ""
      requirements: []

  preconditions:
    - chapter_summary_exists

  postconditions:
    - chapter_analysis_exists
    - required_fields_present

  completion:
    success: >
      A structurally valid chapter analysis has been produced.

  dependencies: []

  consumers:
    - define_chapter_specification
```

Atomicity rationale:

```text
One purpose
One transformation
One coherent output
Independent completion
Independent validation
Clear boundary
```

---

# 48. Example: Non-Atomic Process

```yaml
process:
  id: create_final_chapter

  purpose: >
    Analyze the chapter, define objectives, generate the chapter,
    evaluate it, improve it, obtain approval, and publish it.
```

This contains multiple responsibilities:

```text
Analyze
Define
Generate
Evaluate
Improve
Approve
Publish
```

It should be decomposed.

---

# 49. Example: Potentially Over-Decomposed Process

A chain of `P1 Read File` through `P6 Save Object` may represent one meaningful transformation: "Prepare Source Material" — unless the intermediate results have independent value or represent meaningful workflow boundaries.

---

# 50. Process Contract Validation

Before a Process is considered ready, verify:

### Identity

* [ ] Unique ID
* [ ] Meaningful name
* [ ] Implementation-independent naming

### Purpose

* [ ] One clear primary purpose
* [ ] Purpose explains why the Process exists

### Input

* [ ] Required inputs identified
* [ ] Optional inputs identified
* [ ] Input scope is bounded
* [ ] Sources are identifiable where necessary

### Transformation

* [ ] Transformation is meaningful
* [ ] Transformation is implementation-neutral
* [ ] Transformation represents one primary responsibility

### Output

* [ ] Output is explicitly defined
* [ ] Output is coherent
* [ ] Structure is known where appropriate
* [ ] Consumers are identifiable

### Completion

* [ ] Preconditions defined where necessary
* [ ] Postconditions defined where necessary
* [ ] Success condition is observable

### Atomicity

* [ ] One purpose
* [ ] One primary transformation
* [ ] One coherent result
* [ ] Independently understandable
* [ ] Independently evaluable
* [ ] No unrelated responsibilities
* [ ] No implementation leakage
* [ ] Not unnecessarily decomposed

---

# 51. Contract Compatibility Validation

For every Process transition:

```text
Process A
   ↓
Output Contract
   ↓
Process B
   ↓
Input Contract
```

verify:

* [ ] Output exists
* [ ] Output structure is compatible
* [ ] Required fields exist
* [ ] Semantics are compatible
* [ ] Data types are compatible
* [ ] Required status/state is compatible

An incompatible transition should block architecture validation until resolved.

---

# 52. Recommended Final Process Specification

After this stage, a Process should be represented conceptually as:

```yaml
process:
  id: ""

  name: ""

  purpose: ""

  input:
    required: []
    optional: []

  transformation: ""

  output:
    name: ""
    structure: {}

  preconditions: []

  postconditions: []

  completion:
    success: ""

  dependencies: []

  consumers: []

  atomicity:
    status: ""
    rationale: ""
```

This is the **logical Process contract**.

It is not yet a CrewAI implementation.

---

# 53. What This Stage Must Not Decide

This document should not prematurely determine Agent, Task, Crew, Flow implementation, LLM, Model, Python implementation, Tool, MCP, Knowledge/Memory/Skill implementation. This stage answers "WHAT does this Process do?"; the implementation stages answer "HOW will it do it?"

---

# 54. Relationship to Previous Stage

`02-process-decomposition.md` identifies the candidate Process graph; this document turns each candidate into a contract (Input, Transformation, Output, Completion).

---

# 55. Relationship to Next Stage

**Next:** `04-process-validation-and-human-review.md` validates the complete Process architecture (problem, goal, Process graph, contracts, atomicity, dependencies, coverage, completeness, human review). Only after that validation should Amsha proceed toward Flow and implementation design.

---

# 56. Amsha Rules

1. Every Process must have an explicit contract (Input → Transformation → Output).
2. Every Process must have one primary responsibility.
3. Atomicity is semantic, not technical (`Atomic ≠ one line / function / LLM call / Task`).
4. Do not promote implementation details to Process boundaries without a meaningful reason.
5. Do not hide multiple meaningful transformations inside one Process.
6. Producer outputs and consumer inputs must be contract-compatible.
7. Prefer minimum sufficient input and context.
8. A Process must be independently understandable and meaningfully evaluable.
9. Deterministic validation should be preferred where it is sufficient.
10. Process design precedes implementation design.

---

# 57. Final Principle

> **An Amsha Process is atomic when it represents one meaningful responsibility, performs one coherent transformation, produces one coherent result, and has a clear contract that can be independently validated and composed with other Processes.**

At this stage Amsha should know: WHAT must happen, WHAT enters each Process, WHAT leaves it, WHERE each begins and ends, and WHETHER each is atomic. It should deliberately **not yet decide how the Process is implemented**.
