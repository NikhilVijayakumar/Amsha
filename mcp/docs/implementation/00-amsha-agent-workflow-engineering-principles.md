# Amsha Agent & Workflow Engineering Principles

## 1. Purpose

Prerequisite architecture answers "what problem, what must happen, what architecture is required?" This document defines the engineering principles Amsha uses to translate that validated architecture into an executable CrewAI implementation, preserving architectural intent while selecting the smallest sufficient set of implementation mechanisms.

Amsha is not primarily a CrewAI code generator — it is an **architecture-governed CrewAI implementation system**.

---

# 2. Implementation Boundary

Implementation begins only after the architecture passes the prerequisite validation gate (`Problem → Goal & Boundary → Process Decomposition → Contracts → Process Validation → Flow & State → Failure Planning → Capability Selection → Architecture Validation → implementation_ready=true → Implementation Engineering`).

Implementation must not silently redesign the architecture. If it reveals the architecture is insufficient, inconsistent, or infeasible: `Implementation Finding → Architecture Change Required → Return to Architecture Layer → Revalidate → Resume Implementation`. Do not compensate for architectural defects with arbitrary agents, tasks, tools, memory, reasoning, or orchestration complexity.

---

# 3. Core Principle

> **Implement the validated architecture using the least complex mechanism that reliably satisfies its contracts.**

Optimize for: correctness, architectural fidelity, deterministic behavior where possible, semantic quality where necessary, minimal token/runtime/implementation cost, explicit boundaries, testability, recoverability, observability, maintainability.

Not "use as many CrewAI capabilities as possible" — **use exactly the capabilities required to reliably achieve the validated architecture.**

---

# 4. Architecture Before Components

Never begin with "how many agents?" or "Crew or Flow?" First identify the validated requirement: `Requirement → Meaningful Process → Process Contract → Execution Requirement → Capability Selection → CrewAI Component`. Only then choose among Python, Agent, Task, Crew, Flow, Tool, Knowledge, Memory, Reasoning, Planning, MCP, Human Review, Checkpointing, Observability. **A CrewAI component is an implementation mechanism, not an architectural requirement.**

---

# 5. Process Is the Primary Implementation Unit

A Process represents meaningful work; an implementation component exists to execute it. `Architecture Process → Implementation Mapping → Python / Agent+Task / Crew(Agents+Tasks) / Flow-controlled Crew`. There is no requirement that `1 Process = 1 Agent` or `1 Process = 1 Task` — the mapping is determined by the Process contract and selected capability.

---

# 6. Least-Powerful-Mechanism Principle

Evaluate from simplest reliable option toward more powerful ones — a reasoning preference, not a mandatory hierarchy: `Deterministic Python → Task → Agent+Task → Multiple Agents → Crew → Flow → Flow+Crew → advanced capabilities`.

- **Deterministic transformation** (`input → deterministic transformation → output`) → Python. Don't introduce an LLM agent merely because CrewAI is available.
- **Semantic transformation** (interpretation, judgment, reasoning, creative generation, domain expertise, semantic evaluation) → Agent.
- **Multi-specialist collaboration** (genuine benefit from multiple professional perspectives / coordinated specialist work) → Crew.
- **Explicit orchestration** (state, transitions, branching, iteration, parallelism, human gates, recovery, checkpoints, deterministic control) → Flow.

---

# 7. Flow and Crew Have Different Responsibilities

`Flow = orchestration. Crew = collaboration.` Flow determines what happens next, when, under what condition, what state is carried, when iteration ends, when human approval occurs, how failures route. Crew determines which specialists collaborate, who does what, how tasks execute, how outputs combine.

Known execution structure → Flow. Need for autonomous specialist collaboration → Crew. Combined:
```text
Flow
 ├── deterministic orchestration
 ├── Process → Crew { Specialist A, Specialist B, Specialist C }
 └── next transition
```
Don't use Crew as a replacement for deterministic workflow control, or Flow as a substitute for genuine specialist collaboration.

---

# 8. Agent Engineering Principle

An Agent represents a professional capability — not a technical component, generic LLM wrapper, workflow step, tool, task, or implementation mechanism. Prefer `Senior Narrative Editor`, `Forensic Financial Analyst`, `Historical Research Specialist` over `Analysis Agent`, `Processing Agent`, `LLM Agent`, `Task Agent`. The agent needs a recognizable professional identity and a clearly bounded domain.

## Role, Goal, Backstory

- **Role** — "who is this professional?" Communicates profession, specialization, seniority (`role: "Senior Narrative Continuity Editor"`).
- **Goal** — "what enduring professional responsibility?" Outcome-oriented, stable. Should not become a hidden Task description (don't write "read the screenplay, compare every scene, identify contradictions, produce JSON..." as a goal — that belongs to the Task).
- **Backstory** — "why should this specialist reason like this?" Communicates experience, expertise, perspective, discipline, working style, values. Should not become a capability inventory, task instruction manual, tool list, repeated knowledge base, or dynamic story information.

## Smallest Sufficient Agent

Broad enough for related atomic work, narrow enough for clear professional responsibility. Too narrow: `Scene 14 Date Checker` (agent proliferation). Too broad: `Universal Story Expert` (vague, weakly specialized). Prefer `Narrative Continuity Editor`.

---

# 9. Task Engineering Principle

A Task is a bounded executable unit: `Clear input → Clear instructions → Clear transformation → Clear expected output`, with one primary purpose, one coherent output, explicit inputs, executable instructions, measurable completion criteria. Atomicity ≠ one sentence/function/LLM call/reasoning step — a Task may contain multiple internal operations forming one coherent transformation.

**Task vs Process**: Process is architectural, Task is implementation. `Process → one Task` is valid; `Process → multiple Tasks` may also be correct; `Process → Crew → multiple Tasks` may be required for specialist collaboration. The Process contract must be preserved regardless of mapping.

**Task descriptions** should explain what must be done without repeating Agent role/goal/backstory, Knowledge, Memory, Flow state, Context, or Input data — don't restate the Agent's identity inside every Task; focus on the current operation.

**Task instructions must be executable** — answer: what input, what transformation, what constraints, what must be produced, what makes a valid result. Prefer concrete instructions with an explicit output structure over vague ones like "analyze carefully and provide useful feedback."

**Expected output is a contract** — describe the required result, not restate the Task. Prefer structured schemas (`expected_output: {type, fields: [...]}`) over natural-language output instructions, paired with deterministic validation, whenever the consumer needs machine-readable information.

**Structured output first**: `Task → Structured Output → Schema Validation → Flow Transition`, not `Task → Free-form text → LLM interpretation → Parsing → Guessing`. Reduces parsing ambiguity, token waste, downstream failures, validation complexity, agent-to-agent misunderstanding.

---

# 10. Deterministic Validation First

Validate deterministically whenever possible — required field exists, type correct, ID unique, reference exists, enum valid, dependency exists, graph reachable, schema valid, iteration count within limit, state invariant holds — all via Python. Reserve LLM evaluation for narrative quality, semantic coherence, plausibility, tone, creativity, professional judgment, contextual quality.

> Never spend an LLM call to validate something Python can validate reliably.

---

# 11. Context, State, Knowledge, Skills, Memory

**Context engineering** — contain only what the current Process/Task needs (`Relevant Context → Task → Output`), not the entire project/story bible/history (`Entire Project → Every Agent`). Excess context increases token usage, latency, cognitive noise, contradiction risk, attention dilution.

**State is not Context** — Flow state (`current_process, iteration, approval_status, artifact_reference, execution_status`) is execution state; Context is what's supplied to the LLM for the current operation, a *relevant projection* of state (`artifact_reference, relevant findings, required constraints`) — not the complete Flow state exposed just because it exists.

**Knowledge** — relatively stable reference information (domain rules, story bible, character definitions, world rules, terminology, policies, reference docs). Answers "what should the Agent know/retrieve?" Not a hidden Task instruction system.

**Skills** — repeatable ways of working (narrative analysis methodology, continuity analysis procedure, editorial evaluation framework, research methodology, QA procedure). Answers "how should this professional perform a class of work?" `Knowledge = what I know. Skill = how I work.` Both may be Markdown, but keep the semantics separated.

**Memory** — introduce only when historical retention is actually required. Answers "what should persist beyond the immediate execution context?" Not a substitute for current Flow state, Task input, Knowledge, or large artifact storage.

---

# 12. Tools, MCP, Reasoning, Planning

**Tools** represent callable actions: clear purpose, narrow scope, predictable contract, explicit permissions, appropriate failure behavior. Drive access by Process/Task requirement (`Research Process → Research Tool`, `File Analysis Process → File Tool`), not `Every Agent → Every Available Tool`.

**MCP** is an external capability boundary (`Agent/Flow → MCP → External Capability/System`) — introduce only when the architecture requires access to an external system/capability, never merely because an MCP server exists.

**Reasoning and Planning** are optional, enabled only when architecture requires them. Reasoning: useful when the task needs substantial semantic reasoning or intermediate reasoning materially improves quality — not automatic for every Agent. Planning: useful when the execution sequence must be dynamically determined; unnecessary when the workflow is already explicitly known (`P1→P2→P3→P4` → use Flow instead). Don't replace deterministic workflow design with autonomous planning just because planning is available.

---

# 13. Human Review, Failure, Retry, Idempotency

**Human review** stays an explicit architectural boundary: `Process → Validation → Human Gate → APPROVE/REVISE/REJECT/ESCALATE → Flow Transition`. Don't encode approval as an implied agent decision when architecture requires human judgment; don't add a human gate when deterministic validation suffices.

**Failure engineering** — preserve the architecture's failure behavior. At minimum distinguish `SUCCESS | VALID NEGATIVE RESULT | RETRYABLE FAILURE | RECOVERABLE FAILURE | TERMINAL FAILURE`. A `REJECTED` validation result may be a valid domain result; an LLM request failure is an execution failure — these follow different paths.

**Retry discipline** — intentional, bounded, safe, appropriate to the failure, compatible with side effects. Before retrying: is the failure transient? is retry useful? is the operation idempotent? what's the max attempt count? what happens when exhausted? Never let retry become an infinite loop.

**Iteration is not retry** — Retry repeats an execution because it *failed* (`Task → Failure → Retry`). Iteration repeats a Process because its result doesn't yet satisfy the success condition (`Generate → Evaluate → Needs improvement? Yes→Improve→Evaluate / No→Continue`). Preserve this distinction.

**Side effects and idempotency** — sending messages, creating records, modifying files, triggering jobs, publishing artifacts, mutating external APIs all need explicit duplicate-execution handling. Before retry/recovery, determine idempotency; if not idempotent, use idempotency keys, state checks, transactional boundaries, explicit recovery logic, or human confirmation. Never silently repeat potentially destructive operations.

---

# 14. Artifacts, Token Footprint, Prompt Content

**Artifact handling** — large artifacts shouldn't be copied through every Task/Flow state. Prefer `Artifact → Reference → Consumer` over threading the full content through Flow State → Task Context → Agent → Next Task. Reduces memory pressure, token usage, serialization overhead, accidental duplication.

**Token footprint is an engineering metric** — effective prompt footprint = Role + Goal + Backstory + Task Description + Expected Output + Examples + Knowledge + Retrieved Context + Flow Context + Memory + Tool/MCP info. A short Task description doesn't mean a small prompt — minimize redundant static and dynamic context.

**Static vs dynamic**: static = Role, Goal, Backstory, stable methodology/domain knowledge (configure once); dynamic = current input, state, artifacts, findings, iteration-specific info, current user decisions. Don't repeatedly re-encode dynamic information into static Agent definitions, and don't bake large reference material into prompts when retrieval fits better.

**Examples** cost tokens — use them only when they materially improve output structure, reasoning pattern, classification consistency, or domain interpretation. Prefer one representative example over many redundant ones, unless evaluation shows the extra cost is worth it.

---

# 15. Alignment and Separation of Concerns

**Agent-to-Task alignment** — every Task assigned to an Agent whose professional capability fits it. Ask "can this professional reasonably perform this work?", not "is this Agent available?" Validate Role/Goal/Backstory against Task Purpose/Inputs/Output. Misalignment example: a Financial Analyst writing character dialogue, or a Narrative Editor administering database infrastructure — unless the role was intentionally designed for that.

**No capability leakage** — don't make an Agent responsible for capabilities that belong elsewhere. Often cleaner to split `Agent → semantic work` from `Python → deterministic validation`, and keep `Flow → orchestration` distinct from `Crew → collaboration`, rather than combining them inside one component (combining is fine only when the architecture intentionally requires it).

**Separation of concerns** — each layer has one job and shouldn't silently absorb another's:
```text
Problem → why · Process → meaningful work · Flow → execution control · Agent → professional capability
Task → bounded execution · Knowledge → reference info · Memory → retained history · Tool → callable actions
MCP → external capabilities · Python → deterministic computation/control · Observability → execution records
```

---

# 16. Configuration, Deterministic Boundaries, Contracts

**Configuration over hard-coding** for stable, project-specific values (model selection, temperature, retry limits, tool permissions, knowledge sources, memory settings, execution policies) — but configuration must not hide architectural decisions; important behavior stays explicit and inspectable.

**Deterministic control around LLMs**: `Validate Input → Prepare Context → LLM Process → Validate Output → Update State → Transition`, not `LLM decides everything → LLM interprets its own output → LLM determines workflow → LLM determines success` — unless autonomous behavior is explicitly required.

**Implementation must preserve contracts**: `Input Contract → Implementation → Output Contract`, without silently changing input meaning, adding undocumented requirements, producing incompatible output, removing required information, changing completion semantics, or bypassing required validation/human review. If the contract can't be satisfied, revisit the architecture.

**Traceability**: `Problem Requirement → Goal → Process → Process Contract → Capability → Implementation Component → Test/Validation` — should let Amsha explain why every Agent, Task, Crew, Flow transition, Tool, or Memory exists. If it can't be traced, question the component.

---

# 17. Avoiding Implementation-Driven Architecture, God/Micro Components

**Don't let CrewAI features drive architecture.** Bad: `CrewAI supports Memory → Add Memory`. Correct: `Architecture requires historical retention → Evaluate Memory → Select if sufficient and appropriate`. Same logic applies to Planning and any other capability.

**God components** to actively detect and split:
- God Agent — one Agent doing research + analysis + writing + validation + orchestration + DB ops + publishing.
- God Task — one Task doing research + generate + evaluate + revise + approve + publish.
- God Flow — one enormous Flow method holding business logic, prompting, parsing, validation, persistence, retry handling, external integration.

The fix is restoring meaningful responsibility boundaries, not automatically adding more components.

**Micro-components** — the opposite failure: separate Agents each checking one field when Python validation or one coherent validation Process would do. Component count is not a quality metric; meaningful responsibility is.

---

# 18. Quality Dimensions and Validation Layers

Evaluate implementations across: Architectural Fidelity, Process Coverage, Contract Compliance, Agent Specialization, Agent–Task Alignment, Task Atomicity, Flow Correctness, State Correctness, Failure Handling, Deterministic Validation, Context Efficiency, Token Efficiency, Capability Minimality, Runtime Feasibility, Security/Permissions, Observability, Recoverability, Testability, Maintainability, Overall Simplicity. A functionally correct implementation can still be architecturally poor if unnecessarily complex, expensive, opaque, or hard to validate.

**Validate progressively** (cheap deterministic checks before expensive LLM evaluation): `Configuration → Component Schema → Agent–Task Alignment → Process Mapping → Contract → Flow → State → Failure → Capability → Integration → Execution → Quality Evaluation`.

**Testing strategy** across levels: Unit (validation, transformations, routing, state updates, parsing, invariant checks), Component (Agent/Task config, tool interfaces, Knowledge/Memory config), Process (`Input → Process → Expected Output Contract`), Flow (transitions, branching, iteration, termination, failure routing, human gates, checkpoint recovery), End-to-End (`Problem Input → Complete Workflow → Expected Goal State`).

**Evaluation must match the requirement:**

| Requirement | Preferred Evaluation |
|---|---|
| Schema correctness, field presence, reference validity, state invariant, graph validity, retry limit | Deterministic |
| Output completeness | Deterministic + semantic if required |
| Narrative quality, creativity, tone, professional judgment | LLM / human |
| User acceptance | Human |

Don't use a single evaluation method for every quality dimension.

---

# 19. Observability, Security, Recovery, Versioning, Change Management

**Observability** — expose enough to understand execution: Flow/Process/Task/Agent execution, LLM/Tool/MCP calls, failures, retries, iterations, state transitions, human decisions, latency, token usage, cost, artifacts — without unnecessarily exposing sensitive information.

**Security** — least privilege; an Agent gets only the tools/MCP/files/knowledge/permissions its Process needs (`Agent A → Tool A`, not `Every Agent → All Tools`). External systems need explicit boundaries; sensitive data shouldn't land in prompts or logs unnecessarily.

**Recovery/checkpointing** — introduce for long-running execution, expensive computation, human approval, external side effects, resumability, failure recovery, multi-stage workflows. Checkpoints correspond to meaningful recovery boundaries — don't checkpoint every trivial operation just because checkpointing exists.

**Versioning** — track Architecture, Implementation, Model, and Configuration versions independently; behavior can change when any of them changes. Architecture changes trigger revalidation.

**Change management** — trace `Change → Affected Component → Contract → Process → Flow → Architecture`, classify as implementation-only or architecture-affecting; if the latter, `Change → Architecture Revalidation → Implementation Update`. Never let an implementation change silently redefine the architecture.

---

# 20. Generation Workflow and Specifications

Conceptual generation sequence: `Validated Architecture → Process-to-Capability Mapping → Component Spec → Agent Spec → Task Spec → Crew Spec → Flow Spec → Tools/Knowledge/Memory/MCP → State/Failure/Recovery → Configuration → Code Generation → Static Validation → Execution Tests → Semantic Evaluation → Implementation Validation`. Code generation is near the end, not the beginning.

Before generating Python code, represent the implementation as an intermediate specification:
```yaml
implementation:
  architecture_version: ""
  processes:
    - process_id: ""
      implementation: { type: "", components: [] }
  agents:
    - { id: "", role: "", goal: "", backstory: "" }
  tasks:
    - { id: "", process_id: "", agent_id: "", inputs: [], expected_output: "" }
  crews: []
  flows: []
  tools: []
  knowledge: []
  memory: []
  mcp: []
  validation: {}
```
This separation (`Architecture → Implementation Specification → Source Code`) means the same architecture can potentially produce different implementations without changing the architectural model.

**Generated code must be inspectable** — explicit structure, clear names, small functions, meaningful classes, limited indirection, visible Flow transitions and Agent/Task definitions, explicit configuration, deterministic validation functions. Avoid opaque abstraction layers added merely to look sophisticated. A developer should be able to see what happens, why, by which component, on what data, producing what, and what happens on failure.

**Naming** should reflect architectural meaning — `analyze_source`, `evaluate_character_arc`, `generate_scene`, `validate_continuity`, `approve_revision`, not `process_1`, `agent_2`, `task_a`, `handler_x`. Stable names support tracing, debugging, validation, versioning, human review.

---

# 21. Simplicity and No Silent Capability Changes

**Simplicity is a quality attribute** — a more sophisticated implementation isn't automatically better. If a 1-Agent/2-Task/Python-validation implementation satisfies the architecture as well as a 3-Agent/8-Task/2-Crew/Memory/Planning/MCP one, prefer the simpler one. Complexity must be justified by requirements.

**No silent capability addition** — don't silently add Agents, Tasks, Crews, Memory, Knowledge, Planning, Reasoning, Tools, MCP, human gates, retries, or fallback systems unless the architecture or implementation validation explicitly justifies them. A missed capability during architecture planning should be reported as an **Architecture Gap**, not silently patched in.

**No silent capability removal** — if the architecture requires Human Approval or Checkpointing, implementation must not drop it because autonomous execution looks easier, without an explicit architecture change.

**Minimum sufficient context**: `Task Requirement → Required Knowledge → Relevant State → Relevant Memory → Required Artifact References` — provide only what's actually needed; this is both a quality and cost optimization.

**Minimum sufficient capability**: for every Process ask what capability is required, what's the least powerful mechanism, can it satisfy the contract, can it be validated, what's its cost — result should be *minimum sufficient capability*, not *maximum available capability*.

---

# 22. Traceability Matrix and Architecture Governor Role

Maintain a mapping `Requirement → Goal → Process → Contract → Capability → Component → Code → Test`, e.g. `R-03 → G-01 → P-04 validate_continuity → C-04 continuity_report → Python+Agent → continuity_validator → Flow.validate_continuity() → test_continuity_contract`. This makes generated systems explainable and maintainable.

Amsha behaves as a **governor**, not a passive generator: `UNDERSTAND → DECOMPOSE → VALIDATE → SELECT → IMPLEMENT → VERIFY`, actively rejecting or flagging violations — God Agent (reject/decompose), Unnecessary Crew (reject/simplify), Unbounded Retry (reject), Missing Failure Path (reject), Invalid Contract (reject), Unnecessary Memory/Planning (recommend removal), Oversized Context (recommend reduction), Missing Human Gate (reject), Unvalidated Output where the contract requires validation (reject).

**Decision hierarchy** — never reversed: `Problem Requirements → Goal and Boundaries → Process Contracts → Flow and State Requirements → Failure Requirements → Capability Selection → CrewAI Implementation → Optimization`. CrewAI feature availability must never drive problem architecture.

**Implementation readiness** (`implementation_ready: true` from architecture validation) means the architecture is sufficiently understood and validated to implement — not that every code detail, model choice, or configuration value is predetermined. Implementation engineering still determines concrete classes, functions, configuration, CrewAI APIs, model parameters, project structure, tests, integration details — but these must stay consistent with the validated architecture.

---

# 23. Final Engineering Principles

1. Architecture before implementation. 2. Process before CrewAI components. 3. Use the least powerful mechanism that reliably works. 4. Use deterministic Python where sufficient. 5. Use Agents for genuine professional semantic capability. 6. Use Tasks for bounded units of work. 7. Use Crews for genuine specialist collaboration. 8. Use Flows for explicit orchestration and state control. 9. Keep Flow and Crew responsibilities distinct. 10. Keep Agent identity separate from Task instructions. 11. Keep Knowledge separate from Skills semantically. 12. Keep State separate from Context and Memory. 13. Use structured outputs whenever downstream contracts require them. 14. Validate deterministically whenever possible. 15. Treat token footprint as an engineering concern. 16. Provide minimum sufficient context. 17. Provide minimum sufficient capability. 18. Make failure behavior explicit and bounded. 19. Distinguish retry from iteration. 20. Protect external side effects with idempotency/recovery reasoning. 21. Keep human decisions explicit. 22. Apply least privilege to tools and external capabilities. 23. Preserve Process contracts during implementation. 24. Maintain architecture-to-code traceability. 25. Do not silently change architecture during implementation. 26. Prefer simple implementations over unnecessarily sophisticated ones. 27. Validate generated implementations before production execution. 28. Make generated code inspectable and maintainable. 29. Treat implementation failures that reveal architectural problems as architecture feedback. 30. Optimize for reliable problem completion, not maximum CrewAI feature usage.

---

# 24. Core Amsha Principle

```text
Understand the problem → Define the goal → Decompose meaningful work → Define Process contracts
→ Design execution and state → Plan failures and recovery → Select minimum sufficient capabilities
→ Validate architecture → Engineer Agents/Tasks/Crews/Flows → Validate implementation
→ Execute → Observe → Evaluate
```

> **Amsha should never ask "How can I use CrewAI to solve this?" before asking "What is the smallest reliable architecture that solves the problem?"**

CrewAI is the implementation substrate. **Amsha is the architecture governor.**
