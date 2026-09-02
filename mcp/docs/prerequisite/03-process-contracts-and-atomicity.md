# Amsha Prerequisite: Process Contracts and Atomicity

## 1. Purpose

This document defines how Amsha establishes a precise contract for every
Process identified during Process Decomposition and verifies that each
Process is sufficiently atomic.

The preceding stages establish:

```text
00 Problem Definition
        ↓
01 Goal and Boundary Definition
        ↓
02 Process Decomposition
        ↓
03 Process Contracts and Atomicity
````

`02-process-decomposition.md` determines:

> What meaningful Processes are required?

This document determines:

> What exactly does each Process accept, transform, and produce?

and:

> Is each Process sufficiently atomic to be independently understood,
> validated, implemented, and composed?

The result is a set of **contracted and validated candidate Processes**
ready for Process Validation and Human Review.

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

A Process contract must remain independent of implementation.

For example:

```text
Process:
Evaluate Chapter
```

Its contract may be:

```text
Input:
Generated chapter

Transformation:
Evaluate the chapter against approved criteria

Output:
Chapter evaluation
```

The implementation could later be:

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

or another appropriate mechanism.

The Process contract should remain unchanged.

Therefore:

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

Each Process must have a stable identifier.

Example:

```yaml
id: analyze_chapter
```

The ID should:

* be unique within the workflow
* remain stable during refinement
* describe the Process rather than its implementation

Prefer:

```text
analyze_chapter
evaluate_chapter
generate_chapter
approve_chapter
```

Avoid:

```text
agent_1
crew_step_2
gpt_process
llm_task
mcp_step
```

Implementation should not be encoded into the Process identity.

---

# 6. Process Name

The name should communicate the meaningful transformation.

Prefer:

```text
Analyze Chapter
Define Chapter Specification
Generate Chapter
Evaluate Chapter
Improve Chapter
Approve Chapter
```

Avoid:

```text
Step 1
Process Data
Execute
Worker
Agent Process
LLM Step
```

A Process name should remain understandable even if the implementation is completely replaced.

---

# 7. Purpose

The purpose explains why the Process exists.

Example:

```yaml
purpose: >
  Analyze the chapter to identify its narrative function,
  character contribution, thematic contribution, and
  requirements for subsequent development.
```

The purpose should contain the **responsibility**, not implementation instructions.

### Good

```text
Evaluate the generated chapter against approved quality criteria.
```

### Bad

```text
Ask an LLM evaluator Agent to score the chapter.
```

---

# 8. Input Contract

The Input Contract defines what the Process accepts.

Example:

```yaml
input:
  required:
    - chapter

  optional:
    - story_context
    - character_profiles
```

The input contract should answer:

> **What information must this Process receive to perform its responsibility?**

---

# 9. Required Inputs

Required inputs are necessary for the Process to perform its purpose.

Example:

```yaml
input:
  required:
    - chapter
    - evaluation_criteria
```

If a required input is missing, the Process should not silently invent it.

The later failure-planning stage determines how missing inputs are handled.

---

# 10. Optional Inputs

Optional inputs may improve execution but are not required by the Process contract.

Example:

```yaml
input:
  required:
    - chapter

  optional:
    - story_bible
    - previous_evaluation
```

Optional inputs should not become implicit mandatory context.

This supports:

> **Minimum sufficient context.**

Only information that is required or genuinely relevant should cross the Process boundary.

---

# 11. Input Source

Where useful, identify where each input originates.

Example:

```yaml
input:
  required:
    - name: chapter
      source: workflow_input

    - name: chapter_specification
      source: previous_process

  optional:
    - name: story_context
      source: knowledge
```

Possible logical sources include:

```text
Workflow Input
Previous Process
User
Configuration
External System
Knowledge
Memory
```

At this stage, the source is described logically.

Do not automatically decide the technical mechanism.

---

# 12. Input Scope

A Process should receive the minimum information necessary to perform its responsibility.

Avoid:

```text
Process
   ↓
Entire Workflow State
   ↓
Entire Project
   ↓
Every Previous Output
   ↓
All Available Knowledge
```

Prefer:

```text
Process
   ↓
Required Inputs
   +
Relevant Context
```

This improves:

* clarity
* token efficiency
* reliability
* reproducibility
* maintainability
* validation

---

# 13. Transformation Contract

The transformation defines the meaningful change performed by the Process.

Example:

```yaml
transformation: >
  Analyze the supplied chapter and identify its narrative
  function, character contribution, thematic contribution,
  and development requirements.
```

The transformation should describe the **work**, not the implementation.

It should not contain:

```text
Use Agent
Use Crew
Call LLM
Use GPT
Call MCP
Use Tool X
Use Memory
```

unless these are explicit external constraints imposed by the user.

---

# 14. One Primary Transformation

A Process should have one primary transformation.

### Atomic

```text
Chapter
   ↓
Chapter Analysis
```

### Not Atomic

```text
Chapter
   ↓
Analyze
   ↓
Generate
   ↓
Evaluate
   ↓
Revise
   ↓
Publish
   ↓
Final Project
```

The second contains several independent transformations.

They should normally become separate Processes.

---

# 15. Output Contract

The Output Contract defines the meaningful result produced by the Process.

Example:

```yaml
output:
  name: chapter_analysis

  structure:
    narrative_role: ""
    character_contribution: ""
    thematic_contribution: ""
    requirements: []
```

The output should be explicit enough that a downstream Process can declare it as an input.

---

# 16. One Coherent Output

Atomicity does not require the output to contain only one field.

For example:

```yaml
output:
  name: chapter_analysis

  structure:
    narrative_role: ""
    plot_contribution: ""
    character_contribution: ""
    thematic_contribution: ""
```

This remains one coherent output because all fields collectively represent:

```text
Chapter Analysis
```

Therefore:

```text
One coherent output
≠
One primitive value
```

The question is whether the output represents **one meaningful result**.

---

# 17. Multiple Independent Outputs

Multiple independent deliverables usually indicate that a Process should be decomposed.

### Potentially non-atomic

```text
Generate:

- screenplay chapter
- character design
- concept art
- music specification
```

These are separate deliverables with different purposes.

Prefer:

```text
Generate Screenplay Chapter
Generate Character Design
Generate Concept Art
Generate Music Specification
```

unless the user's actual goal defines them as one inseparable production package.

---

# 18. Output Consumers

Identify which downstream Process consumes the output.

Example:

```yaml
output:
  name: chapter_analysis

  consumers:
    - define_chapter_specification
```

This helps validate the Process graph.

If an output has no consumer, ask why it exists.

Legitimate exceptions include:

```text
Human review artifact
Audit artifact
Persistent record
Observability artifact
Final workflow output
```

These should be intentional.

---

# 19. Postconditions

Postconditions define what is guaranteed after successful Process completion.

Example:

```yaml
postconditions:
  - chapter_analysis_exists
  - required_fields_are_present
  - output_schema_is_valid
```

Postconditions should describe a state that downstream Processes can rely upon.

---

# 20. Completion Condition

A Process must define what successful completion means.

Example:

```yaml
completion:
  success: >
    A complete and structurally valid chapter analysis
    has been produced.
```

This distinguishes:

```text
Process executed
```

from:

```text
Process successfully completed
```

Returning a response does not automatically mean the Process succeeded.

---

# 21. Preconditions

Preconditions define what must be true before the Process can begin.

Example:

```yaml
preconditions:
  - chapter_exists
  - chapter_is_readable
```

Preconditions should be meaningful to the Process.

Do not add technical conditions merely because they are convenient for implementation.

---

# 22. Dependencies

A Process may depend on another Process.

Example:

```yaml
dependencies:
  - analyze_chapter
```

This means:

```text
Analyze Chapter
       ↓
Define Chapter Specification
```

Dependencies should be explicit.

They should not be hidden inside Process descriptions.

---

# 23. Contract Compatibility

The output contract of one Process must be compatible with the input contract of the next.

Example:

```text
P1
Output:
chapter_analysis
        ↓
P2
Input:
chapter_analysis
```

The contracts should agree on:

* identity
* structure
* semantics
* required fields
* data type
* status/lifecycle where relevant

Conceptually:

```text
Producer Output
      ↓
Contract Boundary
      ↓
Consumer Input
```

---

# 24. Contract Compatibility Example

### Producer

```yaml
process:
  id: analyze_chapter

  output:
    name: chapter_analysis

    structure:
      narrative_role: ""
      character_contribution: ""
      thematic_contribution: ""
```

### Consumer

```yaml
process:
  id: define_chapter_specification

  input:
    required:
      - chapter_analysis
```

The consumer can rely on the producer's contract.

If the consumer additionally requires:

```text
plot_contribution
```

but the producer does not provide it, the contract is incomplete.

Amsha should detect this before implementation.

---

# 25. Contract Completeness

A Process contract is complete when the following can be answered:

```text
What enters?
Why is it needed?
What transformation occurs?
What leaves?
What does successful completion mean?
What can downstream Processes rely on?
```

If these cannot be answered clearly, the Process is not ready for validation.

---

# 26. Atomicity

Atomicity is a property of the Process boundary.

Amsha defines an atomic Process as:

> **A Process with one coherent responsibility, one primary transformation, and one coherent output that can be independently understood and validated.**

Atomicity does not mean:

```text
one line
one function
one instruction
one LLM call
one Task
```

It means:

```text
One meaningful responsibility
        +
One coherent transformation
        +
One coherent result
        +
Clear boundary
```

---

# 27. Atomicity Test 1 — Purpose

Ask:

> **Does the Process have one clear primary purpose?**

### Atomic

```text
Evaluate Chapter
```

### Non-atomic

```text
Analyze Chapter,
rewrite Chapter,
generate concept art,
and publish Chapter.
```

The second contains multiple purposes.

---

# 28. Atomicity Test 2 — Transformation

Ask:

> **Does the Process perform one coherent transformation?**

### Atomic

```text
Chapter Summary
       ↓
Chapter Analysis
```

### Non-atomic

```text
Chapter Summary
       ↓
Analysis
       ↓
Generation
       ↓
Evaluation
       ↓
Revision
```

Those are separate transformations.

---

# 29. Atomicity Test 3 — Output

Ask:

> **Does the Process produce one coherent result?**

### Atomic

```text
Evaluate Chapter
       ↓
Chapter Evaluation
```

### Potentially non-atomic

```text
Generate Chapter
+
Generate Character Design
+
Generate Marketing Copy
```

These should normally be separate Processes.

---

# 30. Atomicity Test 4 — Responsibility

Ask:

> **Does a substantial portion of the Process represent a different responsibility?**

Example:

```text
Analyze Screenplay
+
Develop Marketing Strategy
```

These represent different responsibilities.

They should normally be separate.

However, do not split a Process merely because several techniques are used internally.

---

# 31. Atomicity Test 5 — Independent Validation

Ask:

> **Can the Process result be meaningfully evaluated independently?**

For example:

```text
Analyze Chapter
```

can be independently evaluated.

But:

```text
Generate + Evaluate + Improve Chapter
```

contains multiple lifecycle stages and should normally be decomposed.

---

# 32. Atomicity Test 6 — Independent Completion

Ask:

> **Can this Process reach a meaningful completion state without completing unrelated work?**

Example:

```text
Evaluate Chapter
```

has a clear completion state:

```text
Evaluation produced and valid
```

Whereas:

```text
Create Final Production
```

may contain several unrelated completion conditions.

That suggests decomposition.

---

# 33. Atomicity Test 7 — Different Validation Criteria

Substantially different validation criteria are a strong signal for decomposition.

Example:

```text
Generate Screenplay
```

might require:

```text
Narrative quality
Character consistency
Dialogue quality
Pacing
```

while:

```text
Generate Concept Art
```

requires:

```text
Visual consistency
Composition
Style
Character appearance
```

These should normally be separate Processes.

---

# 34. Atomicity Test 8 — Different Failure Domains

Substantially different failure modes may indicate a Process boundary.

Example:

```text
Generate Chapter
```

versus:

```text
Publish Chapter
```

Generation failure and publishing failure have different responsibilities and recovery behavior.

They should normally be separate Processes.

Detailed failure handling is defined later in:

```text
06-corner-cases-and-failure-planning.md
```

---

# 35. Atomicity Test 9 — Human Decision Boundary

A distinct human decision may justify a Process boundary.

Example:

```text
Generate Story Concept
        ↓
Human Approval
        ↓
Generate Screenplay
```

The human approval creates a meaningful workflow boundary.

Do not hide a significant approval decision inside an otherwise unrelated Process.

---

# 36. Atomicity Test 10 — Implementation Leakage

A Process is suspicious when its definition is dominated by implementation details.

### Bad

```text
Call GPT,
parse the response,
call another Agent,
run a Python function,
call MCP,
save JSON.
```

This describes implementation.

### Better

```text
Evaluate the generated chapter against approved criteria.
```

Implementation is determined later.

---

# 37. Internal Complexity Does Not Break Atomicity

An atomic Process may contain several internal operations.

For example:

```text
Process:
Evaluate Chapter
```

Internally:

```text
1. Inspect structure
2. Check continuity
3. Check characterization
4. Evaluate pacing
5. Calculate scores
6. Produce evaluation
```

This can still be one atomic Process because all operations contribute to one coherent responsibility:

```text
Evaluate Chapter
```

Do not create a separate Process for every internal operation.

---

# 38. Implementation Detail vs Meaningful Process

A useful question is:

> **Would a user or domain expert recognize this as meaningful work, or is it merely an implementation operation?**

### Likely Process

```text
Evaluate Chapter
```

### Likely implementation detail

```text
Parse JSON
```

### Likely Process

```text
Prepare Chapter for Evaluation
```

if preparation itself is a meaningful transformation with an independently useful result.

The distinction depends on the problem domain and workflow boundary.

---

# 39. Over-Decomposition

Do not create Processes for every technical operation.

### Bad

```text
P1 Open File
P2 Read File
P3 Parse File
P4 Extract Text
P5 Store Text
P6 Create Object
P7 Pass Object
```

If these collectively represent one meaningful preparation operation, they should remain implementation details.

Possible Process:

```text
Prepare Source Material
```

---

# 40. Under-Decomposition

Do not hide an entire workflow inside one Process.

### Bad

```text
P1 Create Final Chapter
```

where P1 actually means:

```text
Analyze
Define
Generate
Evaluate
Improve
Approve
Publish
```

These are distinct transformations.

They should normally become separate Processes.

---

# 41. Minimum Sufficient Atomicity

Amsha seeks:

> **The minimum number of meaningful Processes necessary to preserve clear responsibility, validation, composition, and control.**

Conceptually:

```text
Too Coarse
     ↓
God Process
     ↓
──────────────
TARGET
Minimum Sufficient
Atomic Processes
──────────────
     ↓
Too Fine
     ↓
Micro-process Explosion
```

Do not optimize for the smallest possible number of Processes.

Do not optimize for the largest possible number either.

Optimize for **meaningful boundaries**.

---

# 42. Process Atomicity vs Task Atomicity

Process atomicity and Task atomicity are related but operate at different levels.

A Process describes a workflow-level transformation.

A Task describes a unit of work assigned within an Agent/Crew implementation.

Example:

```text
Process:
Evaluate Chapter
        ↓
Crew
        ├── Task: Evaluate Narrative Structure
        ├── Task: Evaluate Character Consistency
        └── Task: Produce Evaluation
```

The Process may therefore contain multiple Tasks while remaining atomic at the Process level.

Therefore:

```text
Process Atomicity
        ≠
Task Atomicity
```

The boundaries should be evaluated independently.

---

# 43. Process Atomicity vs Crew

A Crew may implement one Process:

```text
Process
   ↓
Crew
   ↓
Agents / Tasks
```

But a Crew should not automatically determine the Process boundary.

The logical Process comes first.

The implementation is derived later.

---

# 44. Process Atomicity vs Python

If a Process is implemented using Python, the Python implementation should preserve the Process boundary.

Avoid creating a monolithic function:

```python
def execute_everything():
    ...
```

Instead, implementation may use smaller deterministic operations:

```python
def validate_input(...):
    ...

def transform_data(...):
    ...

def validate_output(...):
    ...
```

The exact Python architecture belongs to the later implementation stage.

The important principle is:

> **Atomicity applies to deterministic code as well as LLM-based work.**

---

# 45. Process Contract and Context

A Process contract should not automatically include every available context source.

Distinguish:

```text
Input
Context
Knowledge
Memory
```

At this stage, define what information is logically required.

Later Capability Selection determines whether that information should come from:

```text
direct input
Flow state
Knowledge
Memory
Tool
MCP
```

The Process contract should describe the **information requirement**, not unnecessarily prescribe the mechanism.

---

# 46. Process Contract and Validation

The contract provides the foundation for deterministic validation.

Possible checks include:

```text
Required input exists
Input structure valid
Required fields present
Output exists
Output structure valid
Output type valid
Postconditions satisfied
```

Where semantic quality cannot be determined deterministically, later evaluation mechanisms may be introduced.

Do not use an LLM for a validation problem that can be reliably solved with deterministic validation.

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

```text
P1 Read File
P2 Parse File
P3 Extract Text
P4 Normalize Text
P5 Create Object
P6 Save Object
```

These may represent one meaningful transformation:

```text
Prepare Source Material
```

unless the intermediate results have independent value or represent meaningful workflow boundaries.

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

This document should not prematurely determine:

```text
Agent
Task
Crew
Flow implementation
LLM
Model
Python implementation
Tool
MCP
Knowledge implementation
Memory implementation
Skill implementation
```

Those decisions belong to later stages.

The current stage answers:

```text
WHAT DOES THIS PROCESS DO?
```

The implementation stages answer:

```text
HOW WILL THIS PROCESS DO IT?
```

---

# 54. Relationship to Previous Stage

`02-process-decomposition.md` identifies the candidate Process graph:

```text
P1 → P2 → P3 → P4
```

This document turns each candidate into a contract:

```text
P1
 ├── Input
 ├── Transformation
 ├── Output
 └── Completion

P2
 ├── Input
 ├── Transformation
 ├── Output
 └── Completion
```

Therefore:

```text
02 Process Decomposition
        ↓
Candidate Processes
        ↓
03 Process Contracts & Atomicity
        ↓
Contracted Atomic Processes
```

---

# 55. Relationship to Next Stage

The next document:

```text
04-process-validation-and-human-review.md
```

will validate the complete Process architecture.

It should evaluate:

```text
Problem
   ↓
Goal
   ↓
Process Graph
   ↓
Process Contracts
   ↓
Atomicity
   ↓
Dependencies
   ↓
Coverage
   ↓
Completeness
   ↓
Human Review
```

Only after that validation should Amsha proceed toward Flow and implementation design.

---

# 56. Amsha Rules

### Rule 1

> Every Process must have an explicit contract.

```text
Input
  ↓
Transformation
  ↓
Output
```

### Rule 2

> Every Process must have one primary responsibility.

### Rule 3

> Atomicity is semantic, not technical.

```text
Atomic ≠ one line
Atomic ≠ one function
Atomic ≠ one LLM call
Atomic ≠ one Task
```

### Rule 4

> Do not promote implementation details to Process boundaries without a meaningful reason.

### Rule 5

> Do not hide multiple meaningful transformations inside one Process.

### Rule 6

> Producer outputs and consumer inputs must be contract-compatible.

### Rule 7

> Prefer minimum sufficient input and context.

### Rule 8

> A Process must be independently understandable and meaningfully evaluable.

### Rule 9

> Deterministic validation should be preferred where it is sufficient.

### Rule 10

> Process design precedes implementation design.

---

# 57. Final Principle

> **An Amsha Process is atomic when it represents one meaningful responsibility, performs one coherent transformation, produces one coherent result, and has a clear contract that can be independently validated and composed with other Processes.**

The prerequisite architecture is therefore:

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
HUMAN REVIEW
      ↓
FLOW DESIGN
      ↓
CAPABILITY SELECTION
      ↓
IMPLEMENTATION
```

At this stage Amsha should know:

```text
WHAT must happen
WHAT enters each Process
WHAT leaves each Process
WHERE each Process begins and ends
WHETHER each Process is atomic
```

It should deliberately **not yet decide how the Process is implemented**.
