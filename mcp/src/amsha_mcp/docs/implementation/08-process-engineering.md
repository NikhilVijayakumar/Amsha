# Process Engineering

## Purpose

Process engineering builds an executable implementation from an already-validated Process architecture. The Process defines **what meaningful transformation must occur**; Process engineering decides **how that validated transformation is implemented reliably**.

Implementation may be: deterministic Python, one Agent+Task, multiple Tasks, a Crew, Flow-controlled Crew execution, a Tool, an MCP capability, a Human Review boundary, or a combination.

> **A Process is an architectural responsibility, not a CrewAI component.** There is no fixed rule `Process = Agent/Task/Crew` — instead: `Validated Process → Capability requirements → Implementation mechanism → Executable Process`.

Position: after Architecture Validation, before Agent/Task/Crew Engineering. Full chain: `Problem → Goal/Boundary → Process Decomposition → Contracts → Validation → Flow/State → Failure Planning → Capability Selection → Architecture Validation → Process Engineering → Agent Engineering → Task Engineering → Crew Engineering → Crew Evaluation → Flow Engineering → Implementation`. Process engineering is the bridge between architecture and implementation.

## Core Principle

The Process architecture is authoritative. Implementation must preserve: purpose, boundary, input/output contracts, pre/postconditions, completion conditions, dependencies, failure semantics, human decision boundaries, traceability — never silently change the Process's meaning. If implementation reveals the Process can't be reliably implemented, go back to architecture (revise → revalidate → re-engineer) rather than papering over it with implementation complexity.

A Process = `Inputs → Meaningful Transformation → Outputs`. Things like "call LLM," "parse JSON," "run function," "load file," "call Tool," "invoke MCP," "create Task" are implementation details — they must not redefine the Process boundary.

## Process Contract (preserved by implementation)

`Preconditions → Input Contract → Transformation → Output Contract → Postconditions → Completion`

## Process vs Task vs Agent vs Crew

- **Process** = meaningful architectural responsibility ("what needs to happen"). **Task** = bounded implementation-level operation. One Process may map to one Task, several Tasks, or a whole Crew of Tasks — don't force a 1:1 mapping.
- **Agent** = professional capability that performs semantic work. The Agent implements part of the Process; it doesn't redefine it.
- **Crew** is appropriate only when the Process needs meaningful multi-specialist collaboration. If one Agent suffices, use Agent+Task. If deterministic processing suffices, use Python. Process engineering precedes Crew engineering.

## Implementation Mechanism Selection

Not a strict ladder — select by requirement, from least to most powerful: `Deterministic Python → Single Agent+Task → Multiple Tasks → Crew → Flow+Crew`. A Tool, MCP, Human Review, Knowledge, or Memory may support any level.

- **Deterministic**: schema validation, filtering, sorting, aggregation, calculations, state checks, routing, formatting. Don't introduce an Agent just because the surrounding architecture uses LLMs (e.g. "calculate aggregate score" → Python).
- **Semantic (Agent)**: narrative evaluation, expert interpretation, creative generation, contextual judgment, qualitative/evidence-based analysis (e.g. "evaluate character motivation" → Senior Character Development Editor + Task).
- **Collaborative (Crew)**: multiple professional capabilities must meaningfully collaborate (e.g. "evaluate chapter quality" → Crew of Narrative/Character/Continuity Editors), still bounded by the Process contract.
- **Orchestrated (Flow)**: branching, iteration, parallel work, human gates, retries, recovery, checkpoints. Flow controls execution; the Process remains the meaningful work unit.

**Least-powerful-mechanism rule**: e.g. "validate JSON schema" → Python (not Agent/Crew); "assess emotional consistency" → Agent (not Python); "evaluate narrative+character+continuity via independent perspectives" → Crew (not single Agent). Implementation should never be more complex than the Process requires.

## Process Implementation Specification

```yaml
process:
  id: evaluate_chapter
  name: Evaluate Chapter
  purpose: >
    Evaluate a generated chapter against narrative, character, and continuity requirements.
  input:
    required: [chapter, story_bible]
    optional: [previous_review]
  transformation: >
    Produce a structured quality assessment using specialized professional review.
  implementation:
    mechanism: crew
    crew_id: chapter_quality_review
  output:
    name: chapter_quality_review
    format: json
    schema: {}
  completion:
    success: "A valid consolidated evaluation satisfying the Process output contract is produced."
  failure:
    retryable: true
    max_attempts: 2
  traceability:
    requirements: []
```

`process_mapping` (per Process): `process_id, mechanism ∈ {python, agent_task, multi_task, crew, flow_controlled, tool, mcp, human, hybrid}, components, rationale` — mechanism always needs a rationale.

## Inputs & Context

Preserve the validated input contract. Separate Required / Optional / Derived inputs, Context, State, Knowledge, Memory, Artifacts — don't treat all available information as Process input.

**Input preparation** may be deterministic (raw artifact → Python parsing → relevant extraction → Agent Task); the Process should receive only the representation its transformation needs. Large source artifacts should be referenced/selectively retrieved, not blindly embedded.

**Context construction**: `Process Requirements → Required Context → Relevant Context → Minimal Context`. Avoid global context injection (every Process getting entire project + all Knowledge + all Memory + all previous outputs + all Flow state) — give each Process only what it needs.

**State interaction**: Flow State (current execution info) ≠ Process (meaningful transformation) ≠ Knowledge (reference info) ≠ Memory (retained history). A Process shouldn't own global workflow state unless explicitly required.

## Outputs & Validation

Output must define name, format, structure, schema, semantic requirements, downstream compatibility. Validate in order: deterministic (schema, required fields, types, references, ranges, enums) → semantic (quality, coherence, evidence support, professional correctness) → human, only as required.

**Completion vs success**: execution completion ("Agent executed, output generated, schema valid") ≠ Process success (semantic evaluation may still `FAIL`). Distinguish `SUCCESS | VALID_NEGATIVE_RESULT | RETRYABLE_FAILURE | RECOVERABLE_FAILURE | TERMINAL_FAILURE` — a `REJECTED` evaluation can be a valid Process result, not a technical failure.

## Failure Handling

Derive from the approved failure plan — don't invent recovery behavior during implementation; if undefined and materially important, return to the failure-planning layer.

`Failure → Classification → Response → Retry / Recovery / Escalation / Termination`

**Retry boundary**: retry at the smallest safe boundary (retry the failed MCP request or the one failed specialist, not the whole Crew/Process).

**Idempotency**: any Process with external side effects (create file, update DB, publish, send message, trigger job) must know whether repeating it is safe; if not, use an idempotency mechanism or isolate the side effect at a controlled boundary.

## Dependencies, Parallelism, Iteration

**Dependencies** should follow actual data/execution dependencies — never because Processes are listed in order, share an Agent/Crew, or were designed together.

**Parallelism**: independent Processes may run in parallel when inputs are available, no data dependency exists, state ownership is safe, outputs mergeable, failure behavior defined. Derive from architecture, don't add merely for speed.

**Iteration** needs explicit trigger, condition, loop target, success condition, max count, terminal behavior — never an unbounded loop.

## Human Review & Checkpoints

If the architecture has a human decision boundary, implementation must preserve it explicitly (Flow/execution boundary retains the decision state) — never hide it inside an Agent prompt.

Checkpoint when: long-running execution, expensive computation, human gates, external side effects, recovery/resumability requirements. Capture the minimum state needed to resume safely — don't checkpoint every transient value.

## Artifact Handling

Large artifacts (screenplay, audio, video, image, large JSON, DB export, generated doc) should be referenced and selectively retrieved, not copied into Flow state or every Agent prompt. The Process contract may reference an artifact rather than duplicating it.

## Composition Granularity

A Process may contain internal implementation steps (load → normalize → extract → analyze → produce findings) as long as they collectively form one meaningful transformation — that's not automatically five Processes. Test: **does the internal decomposition create meaningful independent architectural boundaries?** If not, keep it internal.

- **Avoid micro-Process engineering**: don't turn "load file / parse file / read line / call model / parse response / validate field / write field" into separate Processes when they're one "Analyze Source."
- **Avoid God Processes**: don't hide unrelated responsibilities (Research + Writing + Continuity + Image Gen + Audio + Publishing + Analytics) inside one "Produce Complete Episode" Process — split into separate meaningful Processes.

## Mapping to CrewAI Components

Every Task and Crew must stay traceable to its Process:

```yaml
process: { id: evaluate_chapter, implementation: { mechanism: crew } }
tasks:
  - { id: evaluate_narrative, process_id: evaluate_chapter }
  - { id: evaluate_character, process_id: evaluate_chapter }
  - { id: evaluate_continuity, process_id: evaluate_chapter }
  - { id: synthesize_review, process_id: evaluate_chapter }
```

When Flow is required, it owns lifecycle/transitions while Process implementations stay bounded:
```text
Flow → Analyze Source → Generate Draft → Evaluate Draft (Crew) → Decision → {Revise | Approve} → Publish
```

## Observability & Metrics

Per-Process: start, completion, duration, outcome, failure, retries, I/O (where appropriate), downstream transition, resource usage.

```yaml
observability: { process_id: "", execution_id: "", status: "", started_at: "", completed_at: "", duration_ms: 0, outcome: "", attempts: 0, failure_type: "" }
```

Useful metrics: success/failure rate, valid-negative-result rate, retry rate, avg/P95/P99 duration, token usage, LLM cost, Tool/MCP calls, validation failure rate, human rejection rate, iteration count, recovery rate. Don't auto-log sensitive content.

**Design-time vs runtime**: Process engineering asks "can this be implemented correctly?" Runtime evaluation asks "did it actually perform well?" — runtime findings (insufficient Agent capability, poor Task boundary, missing Knowledge, excessive context, unnecessary Crew complexity, poor failure handling, wrong Process assumptions) may trigger architecture revision.

## Versioning & Change Control

Version every Process (`version: "1.2"`). Meaningful changes (I/O contract, Tasks, Agents, Crew, Flow, validation, failure handling) trigger impact analysis and revalidation. If implementation discovers a need for an unauthorized capability (Memory, MCP, Planning, new Tool), route it through: discovery → capability change request → architecture review → revalidation → implementation update. Never silently add capabilities.

**Traceability**: `Requirement → Process → Implementation mechanism → Agent/Task/Crew/Python/Tool → Output` — lets Amsha explain why each component exists.

---

## Checklist

**Contract**: purpose/boundary/inputs/outputs/pre-post-conditions/completion all preserved.
**Mechanism**: justified · deterministic used where sufficient · Agent only for semantic work · Crew only for collaboration · Flow for orchestration · Tools/MCP only where required.
**Inputs/Context**: required available · optional handled explicitly · context relevant and minimal · state correctly scoped · large artifacts referenced.
**Outputs**: contract implemented · schema/semantic validation as appropriate · downstream compatibility · provenance where required.
**Failure**: classifications preserved · retry bounded and safe · idempotency where required · recovery explicit · human escalation preserved.
**Execution**: dependencies correct · parallelism safe · iterations bounded · human gates explicit · checkpoints where required · termination explicit.
**Efficiency**: no unnecessary Agents/Tasks/Crew/capabilities · context efficient · token/runtime cost acceptable.
**Operations**: observability sufficient · recovery possible · security/least-privilege preserved · traceability complete · version recorded.

## Process Implementation Schema

```yaml
process_implementation:
  process_id: ""
  process_version: ""
  purpose: ""
  contract:
    input: { required: [], optional: [] }
    transformation: ""
    output: { name: "", format: "", schema: {} }
    preconditions: []
    postconditions: []
    completion: { success: "", valid_negative_result: "" }
  implementation: { mechanism: "", components: [], rationale: "" }
  context: { knowledge: [], skills: [], state: [], previous_outputs: [], artifacts: [] }
  execution: { dependencies: [], parallel: false, iteration: false, human_gate: false, checkpoint: false }
  validation: { deterministic: [], semantic: [], human: false }
  failure: { outcomes: [], retryable: false, max_attempts: 0, recovery: [] }
  capabilities: { agents: [], tasks: [], crew: "", tools: [], mcp: [], reasoning: false, planning: false, memory: false }
  observability: { enabled: true, metrics: [], events: [] }
  security: { permissions: [], external_side_effects: [] }
  traceability: { requirements: [], architecture_version: "" }
  implementation_ready: false
```

## Decision Model

```text
Validated Process
  → deterministic transformation? YES → Deterministic implementation
  → NO → one professional capability suffices? YES → Agent + Task
  → NO → multiple capabilities required? NO → reconsider Process/Task boundary
  → YES → collaboration required? NO → separate Agents/Tasks + Flow
  → YES → Crew
  → orchestration required? YES → Flow + Process implementation
```
Supporting capabilities (Knowledge, Skill, Tool, MCP, Memory, Reasoning, Planning, Human Review, Checkpointing, Observability) are added only when justified.

## Worked Examples

| Process | Implementation |
|---|---|
| Validate Generated JSON | Python only — no Agent/Crew |
| Evaluate Character Motivation | Senior Character Development Editor + Task — no Crew |
| Evaluate Chapter Quality | Chapter Quality Crew (Narrative/Character/Continuity Editors + Review Lead) |
| Full production Flow | `Flow → Generate Draft → Evaluate Draft (Crew) → Decision → Revise Draft → Final Approval`; Flow owns iteration/decision/state/approval, Crew owns collaborative evaluation |

## Anti-Patterns

- **Process = Agent** — not every Process automatically gets one Agent; some are deterministic or collaborative.
- **Process = Crew** — Crew only for genuine collaboration.
- **Agent as workflow controller** — an Agent deciding what runs next / updating Flow state / picking terminal states moves orchestration into a professional capability; use Flow instead.
- **God Process** — one Process, multiple unrelated transformations.
- **Micro-Process explosion** — every implementation function becomes a Process.
- **Capability creep** — Memory/Planning/Reasoning/Tools/MCP added without architecture justification.
- **Hidden human gate** — approval buried in an Agent prompt instead of represented explicitly.
- **Hidden failure recovery** — implementation invents recovery behavior absent from the validated architecture.
- **Context dumping** — entire project state injected into every Process.
- **LLM for deterministic work** — Agents used for calculations, schema checks, routing, or simple transforms Python handles reliably.

---

## Final Rule

```text
Validated Process → Preserve Contract → Identify Transformation → Separate Deterministic vs Semantic Work
  → Identify Professional Capability → Identify Collaboration Requirement → Select Implementation Mechanism
  → Map Agents/Tasks/Crews/Python/Tools → Define Inputs & Context → Define Outputs & Validation
  → Define Failure & Recovery → Define Execution Boundaries → Define Observability → Validate Implementation
```

> Process engineering translates a validated meaningful responsibility into the smallest reliable executable mechanism without changing the responsibility itself. The Process defines the work. The implementation mechanism serves the Process. CrewAI components must never become the architecture merely because they are available.
