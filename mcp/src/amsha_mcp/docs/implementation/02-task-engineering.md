# Task Engineering

## 1. Purpose

This document defines how Amsha should engineer CrewAI Tasks from validated Processes and Agent capabilities. A Task is the **implementation-level bounded unit of work** executed by an Agent or Crew. It should translate an architectural Process contract into an executable instruction and output contract without changing the Process's meaning.

> **A Task should define one coherent operation with explicit inputs, executable instructions, and a validated output contract.**

Task engineering must optimize for: correctness, clarity, atomicity, Agent–Task alignment, contract fidelity, structured output, deterministic validation, minimal context, minimal token footprint, predictable failure behavior, downstream compatibility, testability.

---

# 2. Task Engineering Position

Task engineering occurs after the architecture and Agent capability are established: `Problem → Goal & Boundary → Process → Process Contract → Flow/State → Failure Plan → Capability Selection → Agent Engineering → Task Engineering`.

Task engineering must not compensate for missing architectural analysis. If a Task appears to require multiple unrelated responsibilities, multiple independent outputs, unrelated specialists, complex orchestration, hidden workflow decisions, or extensive state management, the problem may belong at the Process, Crew, or Flow level rather than inside the Task.

---

# 3. What a Task Represents

> A bounded operation that an Agent or Crew performs to produce a defined result.

```text
Task: Purpose | Inputs | Instructions | Constraints | Expected Output | Completion/Validation
     connects: Process Contract → Executable Instructions → Output Contract
```

---

# 4. Process vs Task

Process = meaningful architectural work. Task = executable implementation unit. A Process may map to one Task, multiple Tasks, or a Crew with multiple Tasks — the mapping depends on the Process contract and selected capabilities.

---

# 5. Task Atomicity

A Task should normally have: one primary purpose, one coherent transformation, one coherent output, one clear completion condition, one understandable responsibility boundary.

Atomic does **not** mean one sentence, function, LLM call, reasoning step, instruction, or output field. A Task may contain multiple internal actions when they form one coherent professional operation.

---

# 6. Meaningful Atomicity

`Analyze screenplay continuity` may involve reading material, comparing characters/timelines/events, identifying contradictions, classifying severity, producing a report — multiple internal operations that still form one coherent Task, atomic because the operation has one purpose, one transformation, one output, one evaluation boundary.

---

# 7. When a Task Should Be Split

Consider splitting when a Task contains multiple independent responsibilities. Strong signals:

- **Multiple primary outputs** — `Character report`, `Financial report`, `Production schedule`.
- **Multiple unrelated responsibilities** — Research + Writing + Database administration.
- **Different professional expertise** — Historical analysis vs Legal analysis.
- **Different validation criteria** — Creative quality vs Schema validation vs Security validation.
- **Different failure domains** — one portion can fail independently requiring different recovery.
- **Different human decisions** — separate approval boundaries.

---

# 8. Do Not Over-Split

Do not create artificial micro-Tasks (`Task 1 → read paragraph`... `Task 4 → identify entity`) when one coherent Task suffices, or a Task merely because a sentence can be a separate instruction. The objective is meaningful atomicity, not maximum fragmentation.

---

# 9. Task Purpose

Every Task should have a clear purpose, traceable to a Process:

```yaml
purpose: >
  Evaluate screenplay continuity against the established
  character and timeline references.
```

---

# 10. Task Naming

Prefer operation-describing names: `analyze_source`, `evaluate_character_arc`, `validate_continuity`, `generate_scene`, `classify_findings`, `summarize_evidence`. Avoid `task_1`, `task_a`, `process_task`, `agent_task`, `execute`, `do_work`, `final_task`. A Task name should remain meaningful in logs, traces, debugging, validation reports, Flow definitions, and generated code.

---

# 11. Task Input Contract

Every Task should identify the information it actually requires:

```yaml
input:
  required:
    - screenplay
    - character_reference
    - timeline_reference
  optional:
    - previous_findings
```

Inputs should be explicit, typed where possible, relevant, minimal, traceable, and available at execution time.

---

# 12. Required vs Optional Inputs

**Required** → the Task cannot reliably execute without it. **Optional** → the Task can execute correctly without it but it may improve the result. This distinction affects validation, branching, error handling, context construction, and reuse.

---

# 13. Missing Input Handling

Missing required input needs explicit behavior — `reject`, `request input`, `route to recovery`, or `use approved fallback`. Do not silently invent missing information unless the architecture explicitly permits inference.

---

# 14. Input Context vs Task Definition

Task definitions should remain stable; dynamic input provided at execution time. Avoid embedding project data in static descriptions: bad `Analyze the 47-scene screenplay for Project X revision 12...`; better `Analyze the supplied screenplay against the relevant continuity references.`

---

# 15. Task Instructions

Instructions should be executable, telling the Agent what to examine, what transformation to perform, what constraints to follow, what evidence/criteria to apply, and what to produce. Example:

```text
Analyze the supplied screenplay against the provided character and
timeline references. Identify continuity contradictions supported by
available evidence. For each finding, determine: contradiction category,
affected entities, supporting evidence, severity, confidence. Return only
findings supported by the supplied material and conform to the defined
output schema.
```

---

# 16. Instruction Specificity

Specific enough to constrain behavior without verbosity. Too vague: `Analyze the screenplay carefully.` Too prescriptive: `Perform exactly 37 reasoning steps...`. Prefer: `Compare the screenplay against the supplied continuity references and identify evidence-supported contradictions.` Define the operation; do not micromanage internal thought.

---

# 17. Outcome-Oriented Instructions

Emphasize the outcome: prefer `Identify contradictions supported by evidence.` over `Think very deeply...`; `Produce a structured continuity report.` over `Give a detailed and useful answer.` Outcome-oriented instructions are easier to validate.

---

# 18. Task Constraints

Constraints are explicit when they materially affect correctness (use only supplied material, do not invent facts, preserve entity identifiers, report uncertainty, avoid misclassification). Include when needed, not repeated mechanically.

---

# 19. Knowledge and Task Instructions

Knowledge → reference material; Task → operation applied to it. Do not convert the entire Knowledge base into Task instructions.

---

# 20. Skill and Task Instructions

Skill → how this class of work is performed (`continuity-analysis methodology`); Task → perform this operation now (`Evaluate Chapter 8 using the continuity-analysis methodology.`). This reduces repeated instructional text.

---

# 21. Context Engineering

A Task should receive the minimum context required. Sources: Task Input, Knowledge, Skill, Flow State, Previous Task Output, Memory, Artifact References, User Decisions. Amsha should not automatically pass all available context.

---

# 22. Relevant Context Projection

Prefer `Full Execution State → Relevant Information Selection → Task Context → Agent` over `Full Execution State → Every Task`. This reduces token usage, irrelevant information, ambiguity, attention dilution, and accidental contamination from unrelated outputs.

---

# 23. Context Must Be Traceable

Amsha should know where important context came from:

```yaml
context:
  - name: character_reference
    source: knowledge.character_reference
  - name: previous_findings
    source: process.evaluate_continuity.output
  - name: chapter
    source: flow.input.chapter
```

---

# 24. Previous Task Context

Pass previous outputs only when relevant (Task B needs only Output A2, not every output of Task A). Context should follow information dependencies.

---

# 25. Task Output Contract

A Task defines what a successful output looks like:

```yaml
output:
  name: continuity_report
  structure:
    findings: []
    summary: ""
```

The contract should specify structure, required fields, types, allowed values, required relationships, and semantic completion conditions where applicable.

---

# 26. Structured Output

When downstream needs predictable data, prefer `Task → Structured Result → Deterministic Validation → Flow` over `Task → Free-form Text → Parser → Guessing → Flow`. Structured outputs improve reliability, validation, interoperability, traceability, token efficiency.

---

# 27. Schema Validation

Validate machine-readable output contracts deterministically where possible (required field exists, type/enum valid, arrays/objects valid, identifiers unique, references exist, numeric ranges valid, nesting valid). Do not use an LLM to validate simple structural requirements Python can validate.

---

# 28. Semantic Output Validation

Properties not fully structurally validatable — factual relevance, coherence, quality, plausibility, usefulness, professional/creative judgment — require `LLM Evaluation` or `Human Review`. The validation method should match the requirement.

---

# 29. Expected Output vs Validation

`expected_output` explains what the Task must produce; validation determines whether the result satisfies it (`Expected Output → Output Contract → Actual Output → Validation → PASS/REVISE/FAIL`). These should not be conflated.

---

# 30. Completion Criteria

A Task should define successful completion (e.g. `A valid continuity report containing only evidence-supported findings and satisfying the output schema.`). Completion describes a successful outcome, not merely execution.

---

# 31. Execution Completion vs Successful Completion

`Task executed` = Agent returned a result. `Task succeeded` = the result satisfies the contract (`Execution → Output → Validation → Success/Failure/Revision`). A completed LLM call is not automatically a successful Task.

---

# 32. Guardrails and Validation

Task-level validation for requirements local to the Task (`Task → Output → Task Guardrail → PASS/RETRY/FAIL`); Flow-level validation for broader workflow conditions (`Task outputs → Flow validation → Transition decision`). Do not put workflow orchestration logic into Task-level validation.

---

# 33. Task Failure Semantics

Classify failures per the architecture: `SUCCESS`, `VALID NEGATIVE RESULT`, `RETRYABLE FAILURE`, `RECOVERABLE FAILURE`, `TERMINAL FAILURE`. A validation Task finding no contradiction is a VALID NEGATIVE RESULT, not a failure; malformed structured output after allowed retries may be TERMINAL.

---

# 34. Retry

Retry only meaningfully retryable failures — transient model/API failure, temporary external service failure, malformed output where regeneration likely succeeds. Do not retry invalid user requirements, permanently missing input, deterministic schema/config bugs, policy violations, or logically impossible operations. Retries must be bounded.

---

# 35. Task Retry vs Process Iteration

Task retry (`Task → Execution failure → Retry same Task`) addresses execution failure. Process iteration (`Generate → Evaluate → Needs improvement? → Improve/Continue`) addresses an unsatisfactory but valid result. Keep them distinct.

---

# 36. Task Idempotency

If a Task performs external side effects (writing records, sending messages, publishing artifacts, modifying persistent data, triggering external jobs), retry behavior must consider idempotency. Do not blindly repeat side effects; use idempotency keys, state checks, transactional boundaries, explicit recovery, or human approval.

---

# 37. Task Dependencies

Tasks may depend on previous outputs; dependencies should be explicit and identify the actual information required, not merely reference the previous Task:

```yaml
dependencies:
  - task_id: analyze_source
    required_outputs:
      - source_summary
```

---

# 38. Sequential Task Dependencies

`Analyze Source → Generate Requirements → Generate Draft` — each Task consumes a meaningful output from the previous. The dependency should follow the data contract.

---

# 39. Parallel Tasks

Tasks may execute in parallel when inputs are available, they are logically independent, they create no unsafe shared-state conflicts, and outputs merge safely (e.g. Chapter → Evaluate continuity / Evaluate dialogue / Evaluate historical accuracy). The Flow controls parallel execution; the Tasks remain independent.

---

# 40. Task Output Ownership

Every significant output should have a clear producer (`Task A → output_a`, `Task B → output_b`). Avoid multiple Tasks implicitly owning the same mutable result; define an explicit aggregation/synthesis Process for combined results.

---

# 41. Task Context and Artifacts

Reference large artifacts rather than copying them into Task prompts (`Task → artifact_reference` over `Task prompt → entire large artifact`). When an artifact must be supplied, still avoid unnecessary duplication across Tasks.

---

# 42. Task Token Footprint

The effective footprint includes Task Description + Instructions + Expected Output + Examples + Dynamic Input + Knowledge + Skill + Previous Outputs + Flow Context + Tool Information. But optimization must consider the entire execution context — a concise description can still be expensive if it receives excessive context.

---

# 43. Token Optimization

1. Remove irrelevant context. 2. Remove duplicate instructions. 3. Remove unnecessary examples. 4. Reduce verbose output requirements. 5. Use structured schemas. 6. Retrieve only relevant Knowledge. 7. Pass only required previous outputs. 8. Move reusable methodology into Skills. 9. Move stable reference info into Knowledge. 10. Re-evaluate whether the Task needs an Agent at all. Do not remove information required for reliable execution merely to reduce tokens.

---

# 44. Example Usage

Examples improve consistency when the output/reasoning pattern is hard to describe — unusual classification rules, domain-specific output patterns, ambiguous cases, structured output examples. Avoid examples that merely repeat the schema; prefer one representative example.

---

# 45. Example Discipline

A Task example should be small, representative, correct, directly relevant, and consistent with the output schema. Bad examples can be worse than none (Agent may learn the wrong pattern). Validate examples against the same output contract as actual outputs.

---

# 46. Task Prompt Composition

Construct Task execution context as `Task Definition + Relevant Skill + Relevant Knowledge + Required Dynamic Input + Relevant Prior Outputs + Required State + Output Contract`, including only the required components.

---

# 47. Task and Agent Separation

Keep `Agent → Who / professional responsibility / professional perspective` separate from `Task → What to do now / with what input / under what constraints / produce what result`. This lets an Agent execute multiple Tasks without redefining its identity.

---

# 48. Task and Flow Separation

Task = perform the operation. Flow = decide when and why the operation executes. Avoid embedding `if X then Task B else Task C` in a Task unless it is part of the semantic operation; prefer an explicit `Task A → Flow Decision → Task B | Task C`.

---

# 49. Task and Python Separation

Use Python for deterministic logic (schema validation, severity enum, referenced entity IDs). Do not ask the Agent to perform deterministic bookkeeping Python can do reliably.

---

# 50. Task and Tool Separation

Task defines the desired operation (`research historical event`); Tool provides the external action (`query approved source`). Do not turn tool mechanics into the Task's primary purpose.

---

# 51. Task and MCP Separation

If an external capability comes through MCP: Task → defines required operation, Agent → determines/uses the capability, MCP → provides the external capability. The Task should not become an MCP implementation manual unless the operation requires explicit tool-selection instructions.

---

# 52. Task Quality Criteria

Evaluate each Task across: purpose clarity, Process traceability, input completeness, input minimality, instruction clarity, instruction executability, constraint correctness, output clarity, output structure, completion criteria, Agent–Task alignment, atomicity, dependency correctness, context relevance, token efficiency, validation strategy, failure semantics, retry safety, downstream compatibility, overall simplicity.

---

# 53. Task Validation

```yaml
task_validation:
  task_id: ""
  process_id: ""
  agent_id: ""
  status: ""
  purpose:
    valid: false
    clear: ""
  inputs:
    required_complete: false
    minimal: false
    findings: []
  instructions:
    executable: false
    ambiguity: ""
    unnecessary_detail: ""
  output:
    contract_defined: false
    structured: false
    schema_valid: false
    downstream_compatible: false
  atomicity:
    status: ""
    rationale: ""
  alignment:
    agent_aligned: false
    findings: []
  context:
    relevant: false
    minimal: false
    sources: []
  failure:
    defined: false
    retry_safe: false
  efficiency:
    token_footprint: ""
    optimization_findings: []
  findings:
    - id: ""
      severity: ""
      category: ""
      message: ""
      recommendation: ""
  traceability:
    requirements: []
    processes: []
  approved: false
```

Conceptual representation; may evolve with the Amsha implementation.

---

# 54. Task Engineering Workflow

Generate Tasks through: `Validated Process → Process Contract → Assigned Agent Capability → Task Boundary → Task Purpose → Required Inputs → Executable Instructions → Constraints → Expected Output → Output Schema → Completion Criteria → Validation Strategy → Failure/Retry Behavior → Context Construction → Token Footprint Evaluation → Task Validation`. Only then emit as CrewAI configuration/code.

---

# 55. Task Specification

```yaml
task:
  id: ""
  name: ""
  process_id: ""
  agent_id: ""
  purpose: ""
  input:
    required: []
    optional: []
  instructions: []
  constraints: []
  context:
    knowledge: []
    skills: []
    state: []
    previous_outputs: []
    artifacts: []
  output:
    name: ""
    format: ""
    schema: {}
    expected: ""
  completion:
    success: ""
    valid_negative_result: ""
  validation:
    deterministic: []
    semantic: []
    human: false
  failure:
    retryable: false
    max_attempts: 0
    outcomes: []
  dependencies: []
  traceability:
    requirements: []
    processes: []
  constraints_runtime:
    token_budget: null
    latency_target: null
```

This intermediate specification should be independent from the final generated CrewAI source code.

---

# 56. Example: Narrative Evaluation Task

Architecture `Process: Evaluate Chapter`, inputs `chapter, character reference, story requirements`, output `evaluation report`; Agent `Senior Narrative Editor`. Task:

```yaml
task:
  id: evaluate_chapter
  name: evaluate_chapter
  process_id: evaluate_chapter
  agent_id: senior_narrative_editor
  purpose: >
    Evaluate the chapter against the established narrative
    requirements and identify meaningful issues.
  input:
    required:
      - chapter
      - character_reference
      - story_requirements
  instructions:
    - Evaluate the supplied chapter against the relevant narrative requirements.
    - Identify only issues supported by the supplied material.
    - Classify each issue by category and severity.
    - Provide evidence for each finding.
    - Return the result using the defined evaluation schema.
  output:
    name: chapter_evaluation
    format: structured
    schema:
      findings:
        type: array
      summary:
        type: string
  validation:
    deterministic:
      - schema_valid
      - required_fields_present
      - severity_values_valid
```

The Agent provides professional capability; the Task provides the current bounded operation; Python validates structure; the Flow determines what happens after evaluation.

---

# 57. Example: Task That Should Be Split

`Research the historical event, write a screenplay scene, evaluate its historical accuracy, revise it, and publish it.` contains multiple responsibilities (Research → Writing → Evaluation → Revision → Publishing) that should become distinct Processes/Tasks with explicit transitions (`Research Historical Material → Generate Scene → Evaluate Historical Accuracy → Revise Scene → Approve/Publish`). The Flow controls iteration; the Tasks remain bounded.

---

# 58. Example: Task That Should Not Be Split

`Analyze a chapter for continuity contradictions` may internally inspect characters/events/timeline, compare references, identify contradictions, classify findings. If all operations contribute to one `Continuity Evaluation Report`, one Task is appropriate. Internal steps do not automatically require Task decomposition.

---

# 59. Task Design Decision Process

```text
Does this work belong to one Process?
    ├── No → Return to Process decomposition
    └── Yes → Does it have one coherent transformation?
         ├── No → Consider splitting
         └── Yes → Can one Agent capability perform it?
              ├── No → Reconsider Agent / Crew design
              └── Yes → Define Task
```

---

# 60. Anti-Patterns

- **God Task** — `Research → Generate → Evaluate → Revise → Approve → Publish`: multiple responsibilities, multiple outputs, hidden orchestration, difficult failure/evaluation.
- **Micro Task** — `Extract protagonist name` followed by `age`, then `location`, when one coherent extraction Task suffices.
- **Vague Task** — `Do a good analysis.`: no clear operation, no measurable output, difficult validation.
- **Output Ambiguity** — `Return useful findings.`: downstream consumers cannot reliably interpret the result.
- **Hidden Workflow** — `If the result is poor, improve it. If good, continue. If the user disagrees, ask again.` inside the Task when these are Flow decisions.
- **Context Dump** — passing entire story, all characters, all previous outputs, all Flow state, all memory, all tools to every Task: token waste, noise, reduced focus, increased failure risk.
- **Prompt Duplication** — repeating Agent identity, Knowledge, Skill methodology, Task instructions inside the Task: unnecessary token usage, conflicting instructions.
- **LLM Schema Validation** — asking an LLM to check whether `severity` is in `LOW, MEDIUM, HIGH` when Python can do it deterministically.

---

# 61. Optimization Strategy

When a Task underperforms, optimize in order: 1. Verify Process boundary, 2. Verify Agent alignment, 3. Verify Task atomicity, 4. Verify input completeness, 5. Remove irrelevant context, 6. Improve instructions, 7. Improve output schema, 8. Add targeted examples if justified, 9. Add deterministic validation, 10. Re-evaluate model. Do not immediately increase model capability.

---

# 62. Task Implementation Principle

The Task should be: small enough to understand + large enough to represent meaningful work + specific enough to execute + structured enough to validate + bounded enough to recover. This is the desired balance.

---

# 63. Final Task Engineering Rules

1. Every Task must trace to a Process.
2. Every Task must have one primary purpose.
3. A Task should represent one coherent transformation.
4. Atomic does not mean artificially tiny.
5. Do not use Tasks to hide Flow orchestration.
6. Do not use Tasks to compensate for poor Process decomposition.
7. Inputs must be explicit.
8. Required and optional inputs must be distinguished.
9. Missing required inputs must have defined behavior.
10. Instructions must be executable and outcome-oriented.
11. Avoid unnecessary prompt verbosity.
12. Use Knowledge for reference information.
13. Use Skills for reusable methodology.
14. Use State for current execution information.
15. Use Memory for retained historical information.
16. Pass only relevant context.
17. Expected output must be explicit.
18. Prefer structured outputs for machine-consumed results.
19. Validate deterministic properties deterministically.
20. Use semantic evaluation only where necessary.
21. Define successful completion separately from execution completion.
22. Distinguish valid negative results from failures.
23. Retries must be bounded and justified.
24. Retry is not Process iteration.
25. External side effects require idempotency reasoning.
26. Task dependencies must follow data dependencies.
27. Parallel Tasks require safe independence.
28. Large artifacts should be referenced rather than unnecessarily copied.
29. Token footprint must be treated as an engineering metric.
30. Task output must remain compatible with downstream consumers.
31. Task logic must not silently change the Process contract.
32. Task implementation must remain traceable to architecture.
33. Use the simplest Task structure that reliably satisfies the Process.

---

# 64. Core Amsha Task Principle

```text
Process = meaningful work
Agent   = professional capability
Task    = bounded operation
Input   = required information
Context = only relevant supporting information
Output Contract = required result
Validation = is the result acceptable
Flow    = what happens next
```

> **A Task is not a miniature workflow. It is a bounded implementation unit that performs one coherent operation and produces a clearly defined result under an explicit contract.**
