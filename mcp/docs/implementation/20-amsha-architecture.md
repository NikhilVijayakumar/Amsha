# Amsha Architecture

## Purpose

Defines the **core architecture of Amsha** as an architecture-governance layer around CrewAI.

> **Amsha determines the right architecture for a problem before generating or executing CrewAI components.**

Amsha should not be merely a CrewAI code generator.

---

# 1. Amsha's Role

Amsha sits above the implementation framework: `User Problem → Amsha → Architecture → CrewAI Implementation → Execution`. CrewAI becomes the execution implementation.

Amsha answers: What needs to happen? What Processes are required? What should the Flow control? Which capabilities are actually necessary? Which Agents/Tasks are required? Is a Crew justified? Which Tools/MCP integrations are required? How should failure and recovery work? Is the architecture valid?

---

# 2. Amsha Is an Architecture Governor

Amsha should govern: Problem, Goal, Boundary, Process, Process Contract, Flow, State, Capability, Agent, Task, Crew, Tool, MCP, Knowledge, Skill, Memory, Artifact, Failure, Recovery, Observability. Its purpose is to prevent the LLM from jumping directly from `User request → Agents + Tasks + Crew` without first understanding the required architecture.

---

# 3. Core Amsha Pipeline

`USER PROBLEM → PROBLEM DEFINITION → GOAL & BOUNDARY → PROCESS DECOMPOSITION → PROCESS CONTRACTS → PROCESS VALIDATION → FLOW & STATE → FAILURE/CORNER CASES → CAPABILITY SELECTION → ARCHITECTURE VALIDATION → IMPLEMENTATION ENGINEERING → CREWAI IMPLEMENTATION → EXECUTION → OBSERVABILITY`.

---

# 4. Architecture Before Implementation

Don't begin with "Which Agent should I create?" Begin with "What transformation does the user actually require?" Then determine the minimum architecture required to perform that transformation reliably.

---

# 5. Problem-to-Implementation Model

`Problem → Goal → Processes → Contracts → Flow → Capabilities → Agents/Tasks/Crews → Tools/MCP → Implementation`. Each layer justified by the layer above it.

---

# 6. Core Architectural Layers

Six major layers: `1. Architecture Reasoning · 2. Process & Flow Design · 3. Capability Design · 4. CrewAI Engineering · 5. Validation · 6. Runtime Governance`.

---

# 7. Architecture Reasoning Layer

Determines: problem, goal, boundary, processes, dependencies, success/failure conditions. It should exist independently of CrewAI implementation details.

---

# 8. Process, Flow, Capability Layers

**Process Layer:** a Process represents meaningful transformations — `Process → {Purpose, Inputs, Transformation, Outputs, Preconditions, Postconditions, Completion}`. The Process is the primary architectural unit of work.

**Flow Layer:** Flow controls execution — `Flow → {State, Processes, Transitions, Conditions, Iterations, Parallelism, Human Gates, Recovery, Termination}`. Flow should control execution rather than perform professional work itself.

**Capability Layer:** Amsha selects the **least powerful sufficient capability** — escalating `Deterministic logic → Python → Agent → Crew → Flow + Crew`. Supporting capabilities: Knowledge, Skill, Memory, Tool, MCP, Reasoning, Planning, Human Review, Checkpointing. Don't introduce a capability merely because it is available.

---

# 9. Agent, Task, Crew Layers

**Agent** = professional semantic capability — `Agent → {Professional Role, Goal, Backstory, Specialization, Knowledge, Skills, Tools, Optional Reasoning/Planning}`. Agents should be the smallest sufficient professional capability. **Task** = bounded operation performed by an Agent or Crew — `Task → {Purpose, Inputs, Instructions, Context, Output, Validation, Completion}`. Tasks stay coherent and atomic at the semantic level. **Crew** = genuine multi-specialist collaboration — `Crew → {Process, Agents, Tasks, Collaboration Model, Intermediate Results, Synthesis, Final Output}`. Crew should not be used simply because multiple Agents exist.

---

# 10. Crew vs Flow

```
FLOW = orchestration
CREW = collaboration
PROCESS = meaningful work
```

Use `Flow → Process → Crew → Agents/Tasks` when a Process genuinely requires collaboration.

---

# 11. Tool, MCP Layers

**Tool** = bounded callable capability (`database, search, image/audio generation, repository, publishing, calculation, file operations`) with explicit input/output, limited permissions, failure behavior, timeout, side-effect policy. **MCP** = external capability boundary — `Amsha → CrewAI/MCP Client → MCP Server → External Capability`. Introduce MCP when an external capability or independently managed integration justifies it.

---

# 12. Knowledge / Skill / Memory / Context

Keep distinct: `Knowledge = what is known · Skill = how a professional works · Memory = what has been retained historically`. Don't use interchangeably. **Context** = information selected for the current execution — Inputs + relevant State + relevant Knowledge + relevant Skills + selected Memory + previous Outputs + Artifact information. Optimize for **sufficiency and minimality**.

---

# 13. Artifact, Validation, Deterministic-First

**Artifact:** large/persistent outputs become Artifacts (`Process → Artifact → Reference → Next Process`); don't repeatedly copy large artifact contents into Flow State, Agent prompts, Task context, Events, Memory. **Validation** exists at multiple levels — Process, Agent, Task, Agent–Task, Crew Evaluation, Architecture, Execution, Artifact — to catch architectural problems before runtime failures. **Deterministic first:** prefer deterministic validation/execution wherever sufficient (schema validation, routing, state updates, arithmetic, file validation, artifact registration, dependency checks, retry counting); use LLM reasoning only when semantic judgment is required.

---

# 14. Runtime Layer

`Flow → Execution → Process → Python/Agent/Crew/Tool → Output → Validation → Artifact → State Update → Next Transition`. Runtime concerns: execution, events, listeners, checkpointing, recovery, observability.

---

# 15. Human-in-the-Loop

Human decisions should be explicit architectural boundaries (design/quality approval, high-impact decision, final publication, ambiguous requirement, exception handling). Prefer `Flow → Human Gate → Decision → Transition` over hiding human interaction inside an Agent prompt.

---

# 16. Architecture Governance, No Silent Redesign

**Governance:** Amsha should inspect an architecture and determine: problem understood? goal clear? Processes complete? contract valid? Flow valid? state sufficient? failure paths covered? capabilities justified? Agents scoped? Tasks atomic? Crew necessary? permissions safe? implementable?

**No Silent Redesign:** validation may identify architectural problems but should not silently redesign. `Task too broad` should produce `SPLIT_TASK` / `REFINE_AGENT` guidance, not silently modify the user's architecture.

---

# 17. Traceability, Versioning, Architecture Object

**Traceability:** every implementation component traces upward — `Requirement → Goal → Process → Task → Agent → Implementation`; also `Process → Flow Transition` and `Process → Artifact`. Allows Amsha to explain why a component exists. **Versioning:** an Amsha architecture is versioned (`architecture: {id, version}`); changes to Process/Flow/Agent/Task/Capability/Knowledge/Skill traceable when they materially affect execution.

**Architecture object:**

```yaml
amsha_architecture:
  id: ""
  version: ""
  problem: {}
  goal: {}
  processes: []
  flow: {}
  capabilities: {}
  agents: []
  tasks: []
  crews: []
  tools: []
  mcp: []
  knowledge: []
  skills: []
  memory: {}
  artifacts: []
  failures: {}
  checkpoints: []
  human_gates: []
  observability: {}
  validation: {}
```

The actual schema can evolve as Amsha matures.

---

# 18. Architecture Generation & Validation Gate

**Generation:** `User Request → Architecture Analysis → Architecture Specification → Architecture Validation → Implementation Specification → CrewAI Generation`. Don't generate implementation first and infer architecture afterward. **Validation gate:** `Architecture → Validation → {PASS → Implementation | REVISE}`. Implementation should not proceed when architectural blocking issues remain.

---

# 19. CrewAI as Implementation Target

CrewAI is the implementation framework, not the architecture definition. `AMSHA → Architecture → Implementation Spec → CrewAI → {Agent → Task, Crew → Task, Flow → State}`. Amsha's architectural reasoning stays framework-independent where practical.

---

# 20. Amsha MCP

The future Amsha MCP server should expose **architecture capabilities**, not merely CrewAI code templates — capability groups: Architecture Knowledge → Architecture Analysis → Architecture Generation → Architecture Validation → Implementation Specification → CrewAI Generation. An LLM should be able to ask: What architecture does this problem require? Should this Process use Python or an Agent? Does this Task fit this Agent? Does this Process require a Crew? Is this Flow sufficient? What capabilities are unnecessary? Is this architecture implementation-ready? The MCP server returns structured architectural guidance.

---

# 21. Amsha as a Governor

`LLM → AMSHA → {Architecture, Validation} → CrewAI Design → CrewAI Runtime`. **The LLM proposes; Amsha reasons and validates; CrewAI executes.**

---

# 22. Minimality as a Core Principle

Continuously ask: **Can this requirement be satisfied with less architecture?** `No semantic reasoning → Python · One professional capability → Agent · One bounded operation → Task · Multiple independent Processes → Flow · Multiple specialists needing collaboration → Crew · External capability → Tool/MCP`. This reduces token cost, runtime cost, latency, failure surface, maintenance complexity.

---

# 23. Complexity Should Be Earned

Every additional component needs a reason: Agent → professional semantic capability; Task → bounded operation; Crew → collaboration; Flow → explicit orchestration; Planning → dynamic action selection; Memory → retained history; MCP → external capability boundary. No capability exists merely because CrewAI supports it.

---

# 24. Core Amsha Decision Model

```
Requirement
  → Can deterministic logic solve it?  YES → Python/deterministic mechanism
  → Requires one professional capability? YES → Agent + Task
  → Do multiple specialists need collaboration? YES → Crew
  → Can Flow coordinate independent capabilities? YES → Flow
  → Add only the capability actually required
```

A guiding decision model, not a rigid algorithm.

---

# 25. Amsha Non-Goals

Should not become: generic autonomous agent framework, unrestricted code generator, generic workflow engine, replacement for CrewAI, unrestricted filesystem manager, unbounded MCP proxy. Its purpose is architectural reasoning, governance, validation, and controlled implementation generation.

---

# 26. Core Architecture Rules

1. Problem before implementation.
2. Goal before Process decomposition.
3. Process before Agent/Task design.
4. Process contracts before executable implementation.
5. Flow before hidden orchestration.
6. Capability selection before component generation.
7. Deterministic mechanisms before LLM mechanisms when sufficient.
8. Agent = professional capability.
9. Task = bounded operation.
10. Crew = genuine collaboration.
11. Flow = orchestration.
12. Tool = bounded callable capability.
13. MCP = external capability boundary.
14. Knowledge, Skill, Memory, Context, State, and Artifact remain distinct.
15. Large artifacts move through references rather than prompt duplication.
16. Failure and recovery are designed before implementation.
17. Human decisions are explicit.
18. Validation occurs before implementation and at important runtime boundaries.
19. No silent architectural redesign.
20. Every important implementation component should be traceable to a requirement and Process.
21. Additional complexity must be justified.
22. Execution and observability must remain separate from architectural control.

---

# 27. Final Amsha Architecture

`USER → PROBLEM DEFINITION → GOAL & BOUNDARY → PROCESS ARCHITECTURE → FLOW & STATE DESIGN → FAILURE/RECOVERY → CAPABILITY SELECTION → ARCHITECTURE VALIDATION → IMPLEMENTATION ENGINEERING → {CREWAI FLOW, CREWAI CREW} → EXECUTION → {Events, Checkpoints, Artifacts} → OBSERVABILITY`.

---

# 28. Final Principle

> **Amsha is an architecture-governance layer that transforms an ambiguous user problem into a validated, minimal, traceable execution architecture, and only then maps that architecture onto CrewAI.**

The most important separation:

```
AMSHA → decides what architecture is required
CREWAI → implements and executes that architecture
RUNTIME → executes, recovers, and observes it
```

Core Amsha philosophy:

> **Do not ask "How do I build this with CrewAI?" first. Ask "What is the smallest reliable architecture that solves the user's problem?" Then use CrewAI only where that architecture requires it.**