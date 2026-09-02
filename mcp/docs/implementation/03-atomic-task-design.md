# Atomic Task Design

## 1. Purpose

This document defines how Amsha determines whether a Task is genuinely atomic and how it should split, merge, or retain Task boundaries during CrewAI implementation. It finds the correct boundary between too much responsibility in one Task and unnecessary fragmentation across many Tasks.

> **One Task should represent one coherent, independently understandable, independently evaluable unit of work.**

Atomicity is a design property, not a measure of Task size.

---

# 2. Position in the Amsha Architecture

Atomic Task design occurs after `Problem → Goal & Boundary → Process Decomposition → Process Contracts → Flow/State → Failure Planning → Capability Selection → Agent Engineering → Task Engineering → Atomic Task Design → Task Validation`. Task atomicity must stay consistent with the validated Process architecture; if the analysis reveals the Process itself is mis-bounded, return to Process Decomposition rather than forcing Task-level fixes.

---

# 3. Definition of an Atomic Task

> A Task containing one coherent responsibility, one primary transformation, one meaningful completion boundary, and one coherent output contract.

```text
Input → One Coherent Transformation → One Primary Result → Validation → Completion
```

Atomic does not mean one instruction, sentence, function, LLM call, field, or reasoning step. A Task can contain substantial internal work and still be atomic.

---

# 4. The Atomicity Test

Evaluate a Task against: 1. one primary purpose, 2. one coherent transformation, 3. one coherent result, 4. one meaningful completion boundary, 5. coherence of success criteria, 6. natural fit to one professional capability, 7. clear input/output contract, 8. coherent failure domain, 9. independent understandability, 10. whether splitting improves architecture rather than merely adds components. Predominantly yes → likely atomic.

---

# 5. Atomicity Is Not Task Size

`Evaluate a screenplay chapter for narrative continuity` may internally read the chapter, compare character/timeline/event references, identify contradictions, classify findings, and produce a report — all serve one purpose (evaluate continuity), so it can remain one atomic Task.

---

# 6. Coherent Transformation

The most important criterion is the transformation: `What is being transformed into what?` (e.g. `Source Material → Narrative Analysis → Analysis Report`; `Story Requirements → Scene Draft → Screenplay Scene`; `Chapter + Continuity References → Continuity Evaluation → Continuity Findings`). Multiple unrelated transformations → atomicity is questionable.

---

# 7. One Primary Purpose

A Task should have one primary purpose. `Evaluate character continuity` (good) vs `Evaluate character continuity and rewrite the scene` (questionable — contains Evaluation + Generation with different objectives, outputs, validation criteria, failure modes, professional responsibilities; usually separated).

---

# 8. One Coherent Output

Atomic Tasks normally produce one coherent primary output. `Continuity Evaluation Report` containing summary, findings, severity, evidence, confidence is still one output. A Task producing `continuity report`, `revised screenplay`, and `production schedule` has three independent deliverables and should normally be split.

---

# 9. One Output Does Not Mean One Field

An output with multiple fields is still atomic:

```yaml
output:
  continuity_report:
    summary: ""
    findings: []
    confidence: ""
    recommendations: []
```

Atomicity concerns semantic coherence, not field count.

---

# 10. One Completion Boundary

A Task should have a meaningful completion point. `Evaluate Chapter → Continuity Report Produced → Task Complete`. If a Task instead chains `Generate → Evaluate → Revise → Approve → Publish`, there are multiple completion boundaries — a strong signal it contains multiple Processes.

---

# 11. Independent Evaluation

> Can the Task's result be evaluated independently?

`Generate Scene` can be evaluated against scene/character requirements, format, continuity, narrative purpose — one coherent boundary. `Research → Write → Evaluate → Publish` has multiple evaluation boundaries.

---

# 12. Responsibility Coherence

A Task should represent work that naturally belongs together: `Extract characters + Extract character attributes + Normalize character references` may be one coherent extraction/normalization (one character dataset). But `Extract characters + Write dialogue` is not one natural responsibility.

---

# 13. Professional Coherence

Evaluate atomicity against Agent specialization: `Would the same professional naturally perform all this work as one responsibility?` Good: `Historical Researcher → Research and verify historical evidence`. Questionable: one Researcher also writing scenes and publishing assets. Differing professional boundaries strongly signal decomposition.

---

# 14. Validation Coherence

A Task is more atomic when its outputs share one coherent validation strategy. `Extract character records` validated via schema/required fields/unique IDs/references is coherent. `Research history + write scene + evaluate accuracy` requiring research/creative/historical validation suggests multiple Tasks.

---

# 15. Failure-Domain Coherence

Failure is a key atomicity signal. `Research historical sources` fails through source unavailability/insufficient evidence/retrieval failure; `Generate screenplay scene` fails through generation/structure/narrative issues. Different failure domains combined into one Task make recovery harder.

---

# 16. Human Decision Boundary

A human approval boundary strongly signals Task/Process separation. `Generate Draft → Human Approval → Publish` creates a meaningful boundary — do not hide the entire sequence inside one Task.

---

# 17. Data Boundary

A meaningful change in data ownership/artifact type can indicate a Task boundary: `Research Notes → Research Report`, then `Research Report → Screenplay Scene` — the transformation changes substantially; these are naturally separate Tasks.

---

# 18. State Boundary

A Task should not normally own unrelated Flow state. A proposed Task requiring `research_state, draft_state, approval_state, publishing_state` may be hiding several workflow stages; state boundaries can reveal incorrect Task boundaries.

---

# 19. Dependency Boundary

If part of a Task can execute independently of another, consider separation. `Evaluate dialogue` and `Evaluate historical accuracy` independent → `Chapter → Evaluate dialogue | Evaluate historical accuracy` may beat one combined Task where parallel execution is useful. But independence alone does not force a split — architectural purpose matters.

---

# 20. Split Signals

Flag for decomposition when strong signals exist: multiple independent purposes, outputs, professional disciplines, completion boundaries, human decisions, failure domains, validation criteria, data transformations, execution dependencies; different retry strategies, resource requirements, capability requirements. More signals = stronger case.

---

# 21–25. Strong Split Signal Examples

- **Multiple outputs** — `Analyze screenplay and create: continuity report, dialogue rewrite, production schedule` → split into `Evaluate Continuity`, `Rewrite Dialogue`, `Create Production Schedule`.
- **Multiple professional roles** — `Research historical facts, evaluate legal implications, and rewrite the screenplay` needs Historical Researcher, Legal Researcher, Screenplay Editor.
- **Multiple validation models** — `Generate a scene and verify historical accuracy, legal compliance, narrative quality, JSON schema` → `Generate Scene → Structural Validation → Historical Evaluation → Legal Evaluation → Narrative Evaluation`.
- **Different failure policies** — Research retries 3x while Publishing never auto-retries and needs human approval; combining makes failure semantics ambiguous.
- **Human gate** — `Generate Draft → Human Review → Publish`; the Task normally ends before the gate.

---

# 26. Do Not Split Merely Because There Are Steps

`Evaluate continuity: 1. identify entities, 2. compare references, 3. detect contradictions, 4. classify, 5. generate report` is one coherent semantic operation. Converting to 5 Tasks increases prompt overhead, orchestration complexity, context transfer, latency, and failure points without improving architecture.

---

# 27–30. Do Not Split for Implementation Metrics

- **LLM calls** — one Task may need one or many internal model interactions; atomicity is responsibility/contract, not call count.
- **Python functions** — `normalize(), validate(), classify(), serialize()` can still be one atomic Task if they collectively implement one coherent transformation.
- **Instruction count** — ten instructions contributing to the same transformation may still be atomic.
- **Output field count** — many fields in one coherent report (summary, findings, severity_distribution, confidence, affected_characters, affected_events) is still one output; do not create a Task per field.

---

# 31. Merge Signals

Detect unnecessarily fragmented Tasks when: same Agent, same Process, same purpose, same input, same output artifact, same completion condition, same validation criteria, no independent reuse, no meaningful failure boundary, no human decision boundary, no meaningful parallelism. When these hold, merging may improve simplicity.

---

# 32. Example: Unnecessary Fragmentation

Bad: `Task 1 → identify characters`, `Task 2 → identify character attributes`, `Task 3 → identify relationships`, `Task 4 → identify character conflicts`. If the Process is `Extract Character Model` and all results form one coherent model, one Task with characters/attributes/relationships/conflicts as fields of one structured output is better.

---

# 33. Merge vs Split Decision

```text
Are the operations semantically one responsibility?
    ├── Yes → Can they share one output contract?
    │       ├── Yes → consider one Task
    │       └── No  → consider split
    └── No → consider split
```

Also weigh professional alignment, validation/failure/human/data boundaries, execution independence, reuse, parallelism, cost.

---

# 34. Atomicity Scoring

```yaml
atomicity:
  purpose_coherence: ""
  transformation_coherence: ""
  output_coherence: ""
  completion_coherence: ""
  validation_coherence: ""
  professional_coherence: ""
  failure_coherence: ""
  dependency_coherence: ""
  human_boundary_coherence: ""
  assessment: ""
```

This supports reasoning, not a simplistic numerical rule.

---

# 35. Binary Atomicity Is Often Insufficient

Avoid `atomic = true/false`. Better classification: `ATOMIC, LIKELY_ATOMIC, REVIEW, LIKELY_COMPOSITE, COMPOSITE`, distinguishing obvious from ambiguous cases.

---

# 36. Atomicity Findings

A finding should explain the architectural reason, not just `Task too large.`:

```yaml
finding:
  severity: medium
  category: multiple_responsibilities
  message: >
    The Task combines narrative evaluation and screenplay
    rewriting, which have different output and validation boundaries.
  recommendation: >
    Consider separating evaluation and rewriting into distinct Tasks.
```

---

# 37. Task Boundary Quality

The objective is not merely atomicity. A boundary should also be meaningful, stable, reusable where appropriate, observable, testable, recoverable, and contract-driven. A perfectly atomic Task with a meaningless boundary is still poor architecture.

---

# 38. Boundary Stability

Task boundaries should not depend on incidental implementation details. Bad: `Task = whatever fits inside one LLM call` or `Task = one Python function`. Better: `Task = evaluate narrative continuity` — the semantic operation should remain stable even if the implementation changes.

---

# 39–40. Task Reusability

Reusability can influence but not dominate atomicity. A Task is reusable when `same operation + different inputs + same output contract` (e.g. `Evaluate Character Continuity` across chapters). Do not generalize so aggressively that purpose becomes vague, and do not split merely to make each piece theoretically reusable — architecture takes precedence over abstract reuse.

---

# 41. Atomicity and Parallelism

Parallelism justifies splitting when independent operations give meaningful execution benefit: `Chapter → Evaluate continuity | Evaluate historical accuracy | Evaluate dialogue`. But if parallelism adds no benefit, splitting for theoretical concurrency creates unnecessary complexity.

---

# 42. Atomicity and Context

Splitting increases context-transfer cost. `One Task → 1 context construction → 1 output` vs `Task A → context; Task B → context + A output; Task C → context + B output` — the second may increase tokens, serialization, latency, failure points. Balance atomicity against context efficiency.

---

# 43. Atomicity and Token Cost

Each additional Task may introduce task instructions, expected output, context transfer, agent invocation, validation, tracing. More Tasks do not automatically mean better architecture — decompose only when the additional boundary provides meaningful architectural value.

---

# 44. Atomicity and Failure Isolation

Splitting can reduce failure impact. `Research + Generation + Evaluation` as one Task means a generation failure may repeat research work. Separating `Research → Generate → Evaluate` enables failure isolation and recovery — an important reason to split even when operations are related.

---

# 45. Atomicity and Recovery

A useful boundary creates a recovery point: `Research Complete → Checkpoint → Generate` — if generation fails, resume from the research result. Boundaries can support checkpointing, resumability, retry isolation, debugging when they correspond to meaningful work.

---

# 46. Atomicity and Human Review

Align Task boundaries with human review boundaries. `Generate Draft → Human Review → Revise Draft` — the draft Task should end before the human gate; do not hide human interaction inside an apparently atomic autonomous Task.

---

# 47. Atomicity and Crew Design

Multiple specialists for one Process → Task boundaries may exist inside a Crew. `Process: Evaluate Historical Screenplay Accuracy` → Crew of Historical Researcher (research evidence), Cultural Historian (evaluate cultural context), Narrative Editor (synthesize implications). Each Task is atomic relative to its professional responsibility; the Crew provides collaboration.

---

# 48. Atomicity and Flow Design

Flow should not compensate for poor Task boundaries. Bad: one giant Task with Flow manually interpreting internal phases. Better: `Task A → Flow → Task B → Flow → Task C` when phases represent meaningful boundaries.

---

# 49. Atomicity Decision Matrix

| Signal                                   | Keep One Task | Consider Split |
| ---------------------------------------- | ------------- | -------------- |
| One purpose                              | Yes           |                |
| One coherent output                      | Yes           |                |
| Multiple unrelated outputs               |               | Strong         |
| Same professional capability             | Yes           |                |
| Different professional disciplines       |               | Strong         |
| Same validation criteria                 | Yes           |                |
| Different validation criteria            |               | Strong         |
| Same failure policy                      | Yes           |                |
| Different failure policies               |               | Strong         |
| Same human boundary                      | Yes           |                |
| Different human boundaries               |               | Strong         |
| Internal steps are tightly coupled       | Yes           |                |
| Independent operations                   |               | Consider       |
| Parallel execution materially useful     |               | Consider       |
| Large token/context overhead from split  | Keep one      |                |
| Meaningful checkpoint between operations |               | Consider       |
| Different artifact ownership             |               | Consider       |

The matrix is guidance, not an automatic decomposition algorithm.

---

# 50. Atomic Task Design Algorithm

```text
Candidate Task
  ↓ Identify Purpose, Transformation, Output, Completion Boundary,
     Professional Responsibility, Validation Criteria, Failure Domain,
     Human Boundaries, Dependencies
  ↓ Evaluate Independence
  ↓ Evaluate Context / Token Cost
  ↓ Evaluate Split Signals
  ↓ Evaluate Merge Signals
  ↓ ATOMIC / SPLIT / MERGE / REVIEW
```

---

# 51. Recommended Split Procedure

When a Task is composite: identify responsibilities → group related operations → identify output per group → identify professional owner → validation boundary → failure boundary → dependencies → create candidate Tasks → validate new boundaries. Split by semantic responsibility, not mechanically by sentence or instruction.

---

# 52. Recommended Merge Procedure

When Tasks are fragmented: compare purpose, inputs, output, Agent capability, validation, failure domain, dependencies → evaluate context/token savings → merge if coherence improves. After merging, revalidate atomicity.

---

# 53. Example: Composite Task

`Create a screenplay scene by researching the historical event, writing the scene, checking historical accuracy, revising the scene, and preparing it for publication.` Atomicity analysis shows multiple transformations, completion boundaries, validation criteria, potential specialists, failure domains, and external side effects. Recommended: `Research Historical Material → Generate Scene → Evaluate Historical Accuracy → Revise Scene → Approve/Publish`.

---

# 54. Example: Correctly Atomic Task

`Evaluate a screenplay chapter for continuity contradictions against the supplied character and timeline references.` Internal operations (identify entities, compare references, detect contradictions, classify findings, produce report) all coherent — purpose/transformation/output/completion/validation/professional responsibility/failure domain coherent. Result: `ATOMIC`.

---

# 55. Example: Micro-Task Fragmentation

Over-decomposed: `Task 1 → extract names`, `Task 2 → extract ages`, `Task 3 → extract relationships`, `Task 4 → extract motivations`, `Task 5 → extract conflicts`. Unless independently valuable, better is one `Extract Character Model → Structured Character Dataset` with all fields in the output schema.

---

# 56. Atomic Task Specification

```yaml
task:
  id: ""
  process_id: ""
  agent_id: ""
  purpose: ""
  transformation: ""
  input:
    required: []
    optional: []
  output:
    name: ""
    structure: {}
  completion:
    success: ""
  atomicity:
    status: ""
    rationale: ""
    split_signals: []
    merge_signals: []
  validation:
    criteria: []
  failure:
    domain: ""
    retryable: false
  dependencies: []
  context:
    required: []
```

---

# 57. Atomicity Validation Result

```yaml
atomic_task_validation:
  task_id: ""
  status: ""
  coherence:
    purpose: ""
    transformation: ""
    output: ""
    completion: ""
    validation: ""
    professional: ""
    failure: ""
  split_analysis:
    required: false
    signals: []
  merge_analysis:
    recommended: false
    signals: []
  findings:
    - id: ""
      severity: ""
      category: ""
      message: ""
      recommendation: ""
  decision:
    action: ""
    rationale: ""
  approved: false
```

---

# 58. Atomicity Does Not Override Architecture

A Task may appear composite implementation-wise while correctly representing a single architectural Process. Distinguish `Task-level complexity` from `Architectural compositeness`. Do not split simply because internal implementation is non-trivial; the key question is whether the Task represents one coherent responsibility.

---

# 59. Atomicity Does Not Override User Intent

Decomposition exists to improve reliable execution. Do not decompose a coherent Task merely because it looks long, has many instructions/output fields, or uses several functions/model interactions. If decomposition makes the workflow less reliable, more expensive, or harder to understand without a meaningful boundary, keep the Task intact.

---

# 60. Atomicity Optimization Objective

```text
Find the smallest meaningful Task boundaries that preserve:
    semantic coherence | contract integrity | professional alignment |
    failure isolation | recoverability | testability | execution efficiency
```

This differs from both minimizing and maximizing Task count — the goal is **optimal decomposition**.

---

# 61. Final Atomic Task Rules

1. A Task must have one primary purpose.
2. A Task should perform one coherent transformation.
3. A Task should produce one coherent primary output.
4. A Task should have one meaningful completion boundary.
5. Atomicity is semantic, not syntactic.
6. Atomic does not mean one sentence, function, or LLM call.
7. Multiple internal steps can exist within one atomic Task.
8. Multiple unrelated responsibilities are a strong split signal.
9. Multiple independent outputs are a strong split signal.
10. Different professional disciplines are a strong split signal.
11. Different validation criteria may justify splitting.
12. Different failure domains may justify splitting.
13. Different human decision boundaries strongly suggest splitting.
14. Meaningful recovery boundaries may justify splitting.
15. Meaningful parallelism may justify splitting.
16. Do not split merely because a Task contains multiple instructions.
17. Do not split merely because a Task uses multiple functions.
18. Do not split merely because a Task uses multiple model calls.
19. Do not split merely because an output contains multiple fields.
20. Do not create micro-Tasks without architectural value.
21. Detect unnecessary fragmentation and merge where appropriate.
22. Task boundaries should remain independent of incidental implementation details.
23. Task boundaries should follow meaningful semantic responsibilities.
24. Context and token costs must be considered when splitting.
25. Failure isolation and recovery benefits must be considered when splitting.
26. Agent professional boundaries must be considered.
27. Flow orchestration must remain outside Tasks when it is a workflow concern.
28. Task atomicity must remain traceable to Process architecture.
29. Ambiguous cases should be reviewed rather than mechanically split.
30. The final objective is optimal decomposition, not maximum or minimum Task count.

---

# 62. Core Amsha Principle

PROCESS → Meaningful Work → Task Boundary → (one coherent responsibility → ONE TASK | multiple distinct responsibilities → SPLIT TASKS) → Contract Validation → Flow Execution.

> **A Task is atomic when its purpose, transformation, output, completion condition, professional responsibility, validation criteria, and failure boundary form one coherent unit of work.**

Do not ask "How small can this Task be?" Ask: "What is the smallest meaningful responsibility that should be independently executed, evaluated, and recovered?"

**Atomicity is about meaningful boundaries, not small size.**
