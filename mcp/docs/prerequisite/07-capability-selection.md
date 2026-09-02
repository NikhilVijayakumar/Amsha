#  Amsha Prerequisite: Capability Selection

## Purpose

The previous stages established `Problem → Goal & Boundary → Processes → Process Contracts → Process Validation → Flow & State → Corner Cases & Failure Planning`. This document determines **what capabilities are actually required to implement the approved architecture**.

The central objective:

> **Select the least powerful mechanism that can reliably satisfy each architectural requirement.**

Amsha should not begin with "Should we use Agents, Crews, Flows, Knowledge, Memory, MCP, or Planning?" Instead begin with "What capability does this Process or transition actually require?" Only then select the implementation mechanism.

---

# 1. Position in the Architecture Process

The prerequisite sequence is `00 Problem Definition → 01 Goal & Boundary → 02 Process Decomposition → 03 Process Contracts & Atomicity → 04 Process Validation & Human Review → 05 Flow & State Planning → 06 Corner Cases & Failure Planning → 07 Capability Selection → 08 Architecture Validation`.

This is the first stage where implementation mechanisms are intentionally considered. However, capability selection is still **architecture-level reasoning**, not code generation.

---

# 2. What Is a Capability?

A capability is a mechanism available to implement part of the approved architecture. Examples: deterministic Python, Agent, Task, Crew, Flow, Tool, Knowledge, Memory, Reasoning, Planning, MCP, Human Review, Checkpointing, Observability.

These mechanisms solve different classes of problems. They should not be treated as interchangeable building blocks.

---

# 3. Core Principle: Least Powerful Sufficient Mechanism

Amsha should prefer the **simplest mechanism that reliably satisfies the actual requirement**.

- Requirement `Calculate a score` → use **Python**, not `Agent → Task → Crew`.
- Requirement `Generate a creative interpretation` → may require **Agent + Task**.
- Requirement `Have multiple specialists analyze competing dimensions` → may justify **Crew**.
- Requirement `Coordinate a known multi-step workflow` → may justify **Flow**.

---

# 4. Capability Selection Is Not Capability Maximization

A common architecture failure is enabling every feature (`Flow + Crew + multiple Agents + Planning + Reasoning + Memory + Knowledge + Tools + MCP`) — unnecessarily expensive and hard to maintain. Amsha should instead produce `Problem → Required capabilities → Minimum sufficient architecture`. **Complexity must be justified by requirements.**

---

# 5. Capability Selection Inputs

Capability selection consumes: validated Processes, Process contracts, Flow structure, State model, transition conditions, human review points, failure plan, external dependencies, recovery requirements, quality requirements, determinism requirements.

Conceptually: `Validated Architecture → Capability Analysis → Capability Requirements → Implementation Mechanisms`.

---

# 6. Capability Decision Hierarchy

Use this reasoning order as a **reasoning discipline** (not a rigid execution sequence) that prevents premature complexity:

```text
1. Can deterministic logic solve it?
2. Does it require LLM intelligence?
3. Does it require one professional capability?
4. Does it require multiple collaborating specialists?
5. Does it require workflow orchestration?
6. Does it require persistent domain knowledge?
7. Does it require retained historical information?
8. Does it require explicit reasoning/planning?
9. Does it require external capabilities?
10. Does it require human judgment?
```

---

# 7. Deterministic Python

Use deterministic Python when the requirement can be reliably expressed as deterministic computation or control logic: schema validation, data transformation, sorting, filtering, calculation, aggregation, branch selection, state validation, format conversion, file operations, deterministic business rules.

Example: `Requirement: Determine whether score >= 80.` → `Python`. There is no reason to use an LLM for this.

---

# 8. Agent

An Agent is appropriate when the Process requires an autonomous professional capability involving judgment, interpretation, generation, or reasoning. Typical characteristics: ambiguous information, semantic interpretation, creative generation, domain judgment, complex reasoning, professional perspective.

Example: `Process: Analyze character psychology` → `Specialized professional Agent`.

The Agent should be modeled as a real professional role rather than a generic technical function. `Senior Character Psychologist` is a professional capability; `Character Analyzer Agent` is primarily an implementation label.

---

# 9. Agent Is Not Automatically Required for Every LLM Operation

An LLM call does not necessarily imply a complex Agent architecture. The question: **"Does this operation require a persistent professional capability?"** If not, a simpler LLM-backed Task or deterministic mechanism may be sufficient. Avoid `Every Process → Create Agent`; Agent creation should be justified by capability requirements.

---

# 10. Task

A Task represents a bounded unit of work assigned to an Agent or Crew. Use Task-level decomposition when the work: has a clear input, has a clear output, has a defined purpose, can be evaluated independently.

The Process architecture remains the higher-level semantic boundary: `Process → Implementation → Agent → Task`. A Process may map to one or multiple Tasks depending on implementation needs. Do not redesign the Process simply because it requires multiple Tasks.

---

# 11. Crew

A Crew is justified when one professional capability is insufficient and the Process benefits from multiple specialized roles collaborating. Indicators: multiple distinct expert perspectives, independent analysis, cross-review, debate, specialist synthesis, complex collaborative reasoning.

Example: `Process: Evaluate a screenplay from multiple professional perspectives` → `Crew` with Agents `Story Editor`, `Character Specialist`, `Cinematography Specialist`, `Production Analyst`.

A Crew is not justified merely because the task is large or multiple steps exist — multiple steps alone are normally a Flow or Task concern.

---

# 12. Flow

Flow is appropriate when the architecture requires explicit workflow orchestration. Indicators: multiple Processes, state transitions, conditional branches, iteration, parallel execution, human gates, checkpointing, long-running execution, failure recovery.

Example: `P1 → P2 → Decision → {P3, P4}` is fundamentally a Flow problem. A Crew should not be used as a substitute for deterministic workflow orchestration.

---

# 13. Flow vs Crew

This distinction is fundamental.

- **Flow** controls *when, where, condition, state, transition, iteration, recovery* (execution).
- **Crew** controls *who collaborates, how specialists reason together* (collaboration).

Therefore: `Flow = orchestration`, `Crew = collaboration`. They may be combined (`Flow → Process → Crew`) when the architecture requires both.

---

# 14. Flow + Crew

Use Flow + Crew when the workflow itself is structured **and** one or more Processes require collaborative intelligence.

Example:

```text
Flow
 ├── Python validation
 ├── Crew: Analyze Story
 ├── Python decision
 ├── Crew: Generate Chapter
 └── Human Approval
```

This is often preferable to making the entire workflow a single autonomous Crew.

---

# 15. Knowledge

Knowledge is appropriate when an Agent or Process requires domain/reference information not reliably contained in its static instructions. Examples: story bible, character definitions, world rules, technical documentation, domain reference material, production standards, historical source material.

Knowledge answers **"What reference information should the capability know?"** — not "What should the workflow do next?" (that is Flow/state responsibility).

---

# 16. Knowledge Selection Test

Ask: **"Would the Process still have the necessary domain information if the reference material were not provided?"** If no → Knowledge is likely required. If yes → do not add Knowledge merely because reference material exists. The goal is relevant retrieval, not maximum context.

---

# 17. Knowledge vs Context

Knowledge should not automatically become Process context. Only relevant information should be supplied: `Knowledge Repository → Relevant Retrieval → Process Context`. This prevents excessive token usage, irrelevant context, duplicated information, and degraded reasoning.

---

# 18. Memory

Memory is appropriate when information should be retained across interactions or executions for future use. Examples: historical decisions, past interactions, learned preferences, previously established facts, long-term workflow history.

Memory answers **"What should this capability remember?"** It is not a substitute for Flow state.

---

# 19. Memory Selection Test

Ask: **"Does the workflow need information from previous executions or interactions that cannot be reliably supplied as current input or Knowledge?"** If yes → Memory may be justified. If the information is only needed during the current execution → use Flow state or Process output.

---

# 20. Reasoning

Explicit reasoning capability may be useful when a Process requires structured multi-step reasoning that benefits from deliberate reasoning behavior. However: **do not add reasoning capability merely because the task uses an LLM** — many LLM operations already perform sufficient reasoning implicitly. Use explicit reasoning mechanisms only when the requirement demonstrates meaningful benefit.

---

# 21. Planning

Planning is appropriate when the workflow or Agent must dynamically determine a sequence of actions that cannot be reliably predefined (`Goal → Determine required actions → Choose dynamically → Execute → Evaluate`). This differs from a known deterministic workflow (`P1 → P2 → P3`). If the sequence is already known, use Flow orchestration rather than introducing autonomous planning.

---

# 22. Flow vs Planning

- **Known workflow** (`P1 → P2 → P3`) → use **Flow**.
- **Unknown sequence** (`Goal → Determine actions dynamically → Execute`) → **Planning** may be justified.

> **Do not use autonomous planning where deterministic orchestration is already known.**

---

# 23. Tools

A Tool is appropriate when a Process or Agent must perform an action that cannot be accomplished through reasoning alone: database query, file operation, API call, calculation service, search, asset generation, external command, system operation.

A Tool answers **"What action can this capability perform?"** Tools should be minimal, relevant, appropriately scoped, and permission-controlled. Avoid exposing unnecessary tools to an Agent.

---

# 24. Tool Selection Principle

Use the smallest tool surface that satisfies the Process. Bad: `Agent → 50 unrelated tools`. Better: `Agent → 3 task-relevant tools`. Excessive tool access increases decision complexity, token usage, risk, ambiguity, and potential failure modes.

---

# 25. MCP

MCP should be considered when the required capability belongs to an external system or needs a standardized external tool boundary. Examples: ComfyUI, Unreal Engine, external application, external service, shared enterprise tool system.

Conceptually: `Flow / Agent → MCP → External Capability`. MCP is not simply a replacement word for Tool — it is an integration boundary for accessing external capabilities.

---

# 26. Tool vs MCP

Use a direct Tool when the capability is local, simple, tightly coupled, and owned by the application. Consider MCP when the capability belongs to an external system, multiple clients may consume it, standardized tool exposure is useful, or the system boundary should remain separate. Do not introduce MCP merely because it is available.

---

# 27. Human Capability

Human interaction is itself a capability. Use it when the architecture requires subjective judgment, approval, ambiguous interpretation, high-impact decisions, creative acceptance, or exception handling. Example: `Automated Evaluation → Ambiguous → Human Review`. Human review should be placed at meaningful decision boundaries.

---

# 28. Checkpointing

Checkpointing is appropriate when workflow recovery requires preserving execution state. Indicators: long-running workflow, expensive computation, human pauses, external operations, failure recovery, resumable execution. Example: `P1 → Checkpoint → P2 → Human Review → Checkpoint → P3`. Checkpointing should not be added everywhere.

---

# 29. Observability and Tracing

Observability is required when the workflow needs visibility into execution, latency, errors, Process outcomes, LLM calls, tool calls, state transitions, cost/token usage, performance.

For Amsha, observability should be treated as an engineering capability rather than a reason to introduce an additional orchestration mechanism. The architecture should determine: What must be observed? Where? At what granularity? For what purpose? The implementation then selects the appropriate tracing infrastructure.

---

# 30. Capability Decision Table

A useful initial decision matrix (a starting framework, not a rigid mapping):

| Requirement                      | Preferred Capability |
| -------------------------------- | -------------------- |
| deterministic calculation        | Python               |
| deterministic validation         | Python               |
| deterministic transformation     | Python               |
| semantic interpretation          | Agent / LLM          |
| professional judgment            | Agent                |
| bounded LLM work                 | Agent + Task         |
| multiple specialist perspectives | Crew                 |
| known multi-step orchestration   | Flow                 |
| stateful workflow                | Flow + State         |
| conditional workflow             | Flow                 |
| iteration                        | Flow                 |
| parallel Processes               | Flow                 |
| domain reference information     | Knowledge            |
| historical retained information  | Memory               |
| dynamic action sequencing        | Planning             |
| deliberate complex reasoning     | Reasoning            |
| local external action            | Tool                 |
| external-system capability       | MCP                  |
| subjective approval              | Human Review         |
| resumable long-running workflow  | Checkpointing        |
| execution visibility             | Observability        |

---

# 31. Capability Selection Per Process

Each Process should receive a capability assessment:

```yaml
process_capability:
  process_id: ""
  requirement:
    deterministic: false
    semantic_reasoning: false
    professional_judgment: false
    collaboration: false
    external_action: false
    human_decision: false

  selected:
    primary: ""
    supporting: []

  rationale: ""

  rejected:
    - capability: ""
      reason: ""
```

The `rejected` section is valuable — it records why more powerful mechanisms were intentionally not selected.

---

# 32. Capability Selection Per Transition

Capabilities are not limited to Processes — transitions may require capabilities. `P1 → score >= 80?` can be **Python** rather than **Agent**; `P1 → Is this interpretation acceptable?` may require **Human Review**. Therefore evaluate: Process capability + Transition capability + State capability + External capability.

---

# 33. Capability Selection for State

State requirements may imply capabilities such as state persistence, checkpointing, artifact storage, memory, observability. The question should be **"What state behavior does the architecture require?"** — not "Should we use Memory?" For example, current execution state does not automatically require Memory; it may only require Flow state.

---

# 34. Capability Selection for Failure Handling

Failure planning may create capability requirements: deterministic retry logic → Flow/Python; external operation status → Tool/MCP; resumability → Checkpointing; human escalation → Human Review; dynamic fallback selection → possibly Agent/Planning. Failure architecture therefore contributes directly to capability selection.

---

# 35. Capability Selection for Human Review

If the previous stage identified `Human Approval Required`, the capability requirement is `Human interaction / approval gate`. Do not replace human judgment with an LLM simply because an automated alternative exists. Likewise, do not add human approval when deterministic validation is sufficient.

---

# 36. Capability Escalation Ladder

Amsha should reason from simpler to more powerful mechanisms. A useful conceptual ladder — a measure of **increasing architectural complexity**, not a hierarchy of "better" technologies. Use the lowest level that satisfies the requirement:

```text
Level 0    Deterministic Logic
Level 1    Single LLM Capability
Level 2    Agent + Task
Level 3    Crew
Level 4    Flow
Level 5    Flow + Crew
Additional  Knowledge / Memory / Tools / MCP / Reasoning / Planning / Human / Checkpointing
```

---

# 37. Avoid Capability Cargo Cult

Do not add a capability because it is modern, available, another project uses it, the framework supports it, or the workflow sounds complex. Every capability should answer **"What requirement does this satisfy?"** If there is no good answer → do not select it.

---

# 38. Capability Rejection Is Valuable

A high-quality architecture should record not only what it uses but what it intentionally does not use — this prevents later architecture drift.

```yaml
capabilities:
  selected:
    - Flow
    - Crew
    - Knowledge
    - Python

  rejected:
    - Memory:
        reason: "No cross-execution information is required."
    - Planning:
        reason: "Workflow sequence is deterministic."
    - MCP:
        reason: "No external capability boundary is required."
    - Reasoning:
        reason: "Existing Agent reasoning is sufficient."
```

---

# 39. Capability Minimality

A capability set is minimal when removing any selected capability would cause an architectural requirement to become unsatisfied. `Selected Capabilities → Remove one → Requirement still satisfied?` YES → capability may be unnecessary; NO → capability justified. This is a useful Amsha validation principle.

---

# 40. Capability Sufficiency

Minimality alone is not enough — the selected capabilities must also be sufficient: Can they implement every approved Process? Flow transitions? State requirements? Failure paths? Human/external requirements? If not → the capability set is incomplete.

---

# 41. Capability Complexity Budget

Capability selection should consider the complexity each mechanism introduces.

```text
Python                          complexity: low
Agent                           complexity: moderate
Crew                            complexity: higher
Flow + Crew + Memory + MCP + Planning   complexity: high
```

The exact values are not important. The principle:

> **Additional architectural machinery must provide corresponding value.**

---

# 42. Token and Runtime Cost

Capability selection should also consider prompt tokens, context size, LLM calls, latency, tool calls, memory retrieval, model cost, execution overhead. Example: calculating a deterministic score via LLM introduces unnecessary token cost, latency, and nondeterminism — Python is superior. For LLM-required work, choose the smallest sufficient prompt/context and capability structure.

---

# 43. Reliability Consideration

Prefer deterministic mechanisms for rules, validation, calculations, routing, state transitions, schema checks. Use LLMs where interpretation, generation, semantic reasoning, and creative judgment are genuinely required. This creates `Deterministic Control + Probabilistic Intelligence` rather than an entirely probabilistic workflow.

---

# 44. Security and Permission Boundaries

Capability selection should consider what each capability is allowed to do. `Agent → Tool → External System` creates a permission boundary. Ask: Does the Process really need this capability? What data can it access? What actions can it perform? Can access be restricted? Can destructive operations be isolated? **Least capability is also a security principle.**

---

# 45. Capability Selection Example

Suppose the approved workflow is: `P1 Analyze Source → P2 Define Requirements → P3 Generate Chapter → P4 Evaluate Chapter → P5 Improve Chapter → H1 Human Approval`. Flow: `P1 → P2 → P3 → P4 → Pass? {NO → P5 → P4, YES → H1 → APPROVED → END}`.

Capability analysis:

- **P1 Analyze Source**: semantic analysis → Agent + Task, Knowledge.
- **P2 Define Requirements**: structured reasoning → Agent + Task.
- **P3 Generate Chapter**: creative generation → Agent + Task, Knowledge.
- **P4 Evaluate Chapter**: multi-dimensional evaluation → Crew (if multiple independent specialist perspectives are genuinely required).
- **P5 Improve Chapter**: creative revision → Agent + Task.
- **Pass Decision**: deterministic criteria → Python.
- **Human Approval** → Human Review.
- **Workflow** → Flow. **State** → Flow State.
- **Memory**: not required unless cross-execution history is needed. **Planning**: not required, sequence known. **MCP**: not required unless external systems involved.

The resulting architecture might be:

```text
Flow
 ├── Agent + Task
 ├── Agent + Task
 ├── Agent + Task
 ├── Crew
 ├── Python
 ├── Agent + Task
 └── Human Review

Knowledge
Flow State
Observability
```

rather than automatically enabling every CrewAI capability.

---

# 46. Capability Selection Output

The output should be machine-readable:

```yaml
capability_selection:
  principles:
    minimality: true
    sufficiency: true
    deterministic_first: true

  capabilities:
    - id: ""
      capability: ""
      scope: ""
      reason: ""
      required_for: []

  process_mapping:
    - process_id: ""
      primary: ""
      supporting: []
      rationale: ""

  transition_mapping:
    - transition_id: ""
      capability: ""
      rationale: ""

  state_requirements:
    flow_state: true
    memory: false
    checkpointing: false

  external_requirements:
    tools: []
    mcp: []

  human_requirements:
    gates: []

  rejected:
    - capability: ""
      reason: ""

  cost_considerations:
    token: []
    runtime: []
    operational: []

  open_questions: []
```

---

# 47. Capability Selection Validation

Before proceeding to final architecture validation, verify:

## Sufficiency
- [ ] Every Process has sufficient implementation capability.
- [ ] Every transition can be implemented.
- [ ] State requirements are covered.
- [ ] Human requirements are covered.
- [ ] External dependencies are covered.
- [ ] Failure requirements are covered.

## Minimality
- [ ] No unnecessary Crew exists.
- [ ] No unnecessary Agent exists.
- [ ] No unnecessary Flow exists.
- [ ] No unnecessary Memory exists.
- [ ] No unnecessary Knowledge exists.
- [ ] No unnecessary Planning exists.
- [ ] No unnecessary Reasoning exists.
- [ ] No unnecessary Tool exists.
- [ ] No unnecessary MCP integration exists.

## Determinism
- [ ] Deterministic logic uses deterministic mechanisms where possible.
- [ ] LLMs are used where semantic intelligence is actually required.
- [ ] State transitions are not unnecessarily delegated to LLMs.

## Cost
- [ ] Token-heavy capabilities have justification.
- [ ] Context requirements are minimal.
- [ ] Iterative LLM execution is bounded.
- [ ] Expensive capabilities are used only where necessary.

## Security
- [ ] Tool access is scoped.
- [ ] External access is justified.
- [ ] Destructive capabilities are controlled.
- [ ] Human approval is used where required.

---

# 48. Anti-Patterns

- **Crew for Everything** — `Every Process → Crew`; wrong unless every Process genuinely requires collaboration.
- **Agent for Deterministic Logic** — `Calculate total → Agent`; use Python.
- **Flow for One Simple Operation** — `One calculation → Flow`; a Flow adds unnecessary orchestration.
- **Memory for Current State** — `Pass Process output → Memory`; use Flow state or Process context.
- **Knowledge Dump** — entire knowledge base to every Agent; use relevant retrieval.
- **Planning a Known Workflow** — known `P1 → P2 → P3` implemented with an autonomous planner; use Flow.
- **MCP Everywhere** — `Local function → MCP server`; do not introduce an external integration boundary without a reason.
- **LLM for Routing** — `score = 95 → LLM decides "pass"`; use deterministic logic.
- **Capability by Framework Availability** — bad `CrewAI supports X → Use X`; correct `Architecture requires X → Use X`.

---

# 49. Capability Selection Decision Procedure

For each architectural requirement:

```text
1. What exactly must be done?
2. Is it deterministic?            YES → deterministic mechanism
3. Requires semantic intelligence? NO  → simpler mechanism
4. Requires one professional capability?   YES → Agent / Task
5. Requires multiple specialists collaborating?   YES → Crew
6. Requires explicit orchestration?   YES → Flow
7. Requires external capabilities?    → Tool / MCP
8. Requires reference information?    → Knowledge
9. Requires historical retention?     → Memory
10. Requires dynamic planning?        → Planning
11. Requires explicit human judgment? → Human Review
```

At every step ask: **"Can a simpler mechanism already satisfy the requirement?"**

---

# 50. Relationship to Architecture Validation

Capability selection does not mean the architecture is finished. The next stage must validate `Problem, Goal, Processes, Contracts, Flow, State, Failure Handling, Capabilities` as one coherent architecture. The final validation should detect gaps such as: Process requires Crew but selected Agent; Process requires external capability but no Tool/MCP exists; Flow requires persistent recovery but no checkpoint strategy exists; Workflow requires historical context but Memory is absent; deterministic decision implemented through unnecessary LLM reasoning.

---

# 51. Final Capability Model

At the end of this stage, Amsha should have a mapping `ARCHITECTURAL REQUIREMENT → CAPABILITY REQUIRED → MINIMUM SUFFICIENT MECHANISM`:

```text
Calculate score              → Deterministic computation  → Python
Generate chapter             → Professional creative capability → Agent + Task
Multi-specialist evaluation  → Collaborative expertise    → Crew
Coordinate workflow          → Explicit orchestration     → Flow
Story reference              → Domain knowledge           → Knowledge
Previous decisions           → Historical retention       → Memory
External asset generation    → External capability        → MCP / Tool
Final creative approval      → Human judgment             → Human Review
```

---

# 52. Core Amsha Rules

1. > Select capabilities from requirements, not from framework features.
2. > Use the least powerful mechanism that reliably satisfies the requirement.
3. > Prefer deterministic mechanisms for deterministic work.
4. > Use Agents for professional intelligence, not as generic wrappers around every operation.
5. > Use Crews when genuine multi-specialist collaboration is required.
6. > Use Flow for orchestration, state, transitions, iteration, parallelism, and workflow control.
7. > Do not use Crew as a substitute for Flow.
8. > Do not use Memory as a substitute for Flow state.
9. > Do not use Planning when the workflow sequence is already known.
10. > Do not use LLMs for deterministic routing, validation, or calculation when deterministic logic is sufficient.
11. > Knowledge provides reference information; Context determines what is relevant now.
12. > MCP is an external capability boundary, not automatically a replacement for local Tools.
13. > Human review is a capability for decisions that genuinely require human judgment.
14. > Every selected capability should have an explicit architectural justification.
15. > Intentional non-selection is part of architecture quality.
16. > Capability selection must satisfy the entire Process, Flow, State, and Failure architecture.

---

# 53. Final Architecture Boundary

The prerequisite architecture can now be represented as:

```text
USER PROBLEM → GOAL & BOUNDARY → PROCESS DECOMPOSITION → PROCESS CONTRACTS →
PROCESS VALIDATION → FLOW & STATE → CORNER CASES & FAILURE → CAPABILITY SELECTION
        ↓
┌─────────────────────────────────────┐
│ Minimum Sufficient Implementation   │
│ Python · Agent · Task · Crew · Flow │
│ Knowledge · Memory · Reasoning ·    │
│ Planning · Tools · MCP · Human      │
│ Review · Checkpointing ·            │
│ Observability                       │
└─────────────────────────────────────┘
        ↓
08 Architecture Validation
```

The key architectural transformation:

```text
Problem → Required Work → Required Execution Structure → Required Failure Behavior → Required Capabilities → Minimum Sufficient Architecture
```

This is where Amsha moves from **problem/process reasoning** into **implementation architecture reasoning**. The next stage, `08-architecture-validation.md`, should validate the complete architecture as a whole before Amsha begins Agent, Task, Crew, Flow, Knowledge, Memory, Tool, MCP, and implementation engineering.