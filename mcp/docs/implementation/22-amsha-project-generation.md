# Amsha Project Generation

## Purpose

Defines how **Amsha generates a CrewAI project from a validated architecture**.

> **Project generation is a compilation step from approved architecture to executable CrewAI implementation.**

Amsha should not design the architecture while generating code.

---

# 1. Generation Pipeline

`USER PROBLEM → AMSHA ARCHITECTURE → ARCHITECTURE VALIDATION → APPROVED ARCHITECTURE → IMPLEMENTATION SPECIFICATION → PROJECT GENERATION → CREWAI PROJECT → STRUCTURAL VALIDATION → READY FOR EXECUTION`. Project generation begins only when the architecture is sufficiently validated.

---

# 2. Generation Input

Primary input is the approved Amsha architecture, containing as applicable: Problem, Goal, Processes, Process Contracts, Flow, State, Failure/Recovery, Capabilities, Agents, Tasks, Crews, Tools, MCP, Knowledge, Skills, Memory, Artifacts, Human Gates, Observability. The architecture version must be recorded.

---

# 3. Implementation Specification

Generate an implementation specification before source code: `Approved Architecture → Implementation Specification → Source Code`. It maps architectural concepts to CrewAI constructs:

```yaml
process:
  id: evaluate_story
implementation:
  mechanism: crew
  crew: { id: story_evaluation_crew }
  agents:
    - story_editor
    - continuity_editor
  tasks:
    - evaluate_narrative
    - evaluate_continuity
```

---

# 4. Architecture-to-CrewAI Mapping

Follow the capability decisions already made — these are **mappings, not automatic one-to-one conversions**:

| Amsha concept | Typical CrewAI implementation |
| ------------- | ----------------------------- |
| Process | Python / Agent+Task / Crew / hybrid |
| Flow | CrewAI Flow |
| Agent | CrewAI Agent |
| Task | CrewAI Task |
| Crew | Crew |
| Tool | CrewAI Tool or external integration |
| MCP | MCP integration |
| Knowledge | Knowledge source / retrieval layer |
| Skill | Prompt/instruction/resource layer |
| Memory | Memory mechanism |
| Human Gate | Flow-controlled approval |
| Artifact | File/object/artifact layer |
| Validation | Python / deterministic validator / semantic evaluator |

---

# 5. Generation Rules

**Rule 1 — Preserve architecture:** generated code implements the approved architecture, not a reinterpretation. **Rule 2 — No silent redesign:** if the architecture can't be implemented as specified, `Generation → Implementation conflict → Generation stops → Architecture revision required`; don't silently introduce Agents, Crews, Tools, or Flow states. **Rule 3 — Prefer simple implementations:** deterministic Python Process → no Agent; one Agent sufficient → no Crew; explicit Flow logic sufficient → no autonomous Planning.

---

# 6. Project Structure

Generated project reflects the architecture without unnecessary abstraction:

```
project/
├── src/
│   ├── flows/  crews/  agents/  tasks/  tools/
│   ├── knowledge/  skills/  artifacts/  validation/
├── tests/
├── config/
├── pyproject.toml
└── README.md
```

Reduce the structure when the project doesn't require all components.

---

# 7. Do Not Generate Empty Layers

Don't create directories/abstractions merely because Amsha supports them. `1 Flow, 2 Agents, 3 Tasks, 0 Tools, 0 MCP, 0 Memory` → no placeholder implementations for Tools/MCP/Memory.

> **Generate what the architecture requires, not what the framework makes possible.**

---

# 8. Flow Generation

A Flow implements the validated execution graph, explicitly representing start, state, process execution, transitions, conditions, parallelism, iterations, human gates, failure handling, recovery, termination. It should not contain the professional work itself unless that work is explicitly deterministic orchestration logic.

---

# 9. Crew Generation

A Crew represents the approved collaboration boundary, preserving Crew purpose, Agents, Tasks, task dependencies, collaboration model, inputs, outputs, validation, failure behavior. Don't move workflow control into the Crew merely because it's convenient in code.

---

# 10. Agent Generation

Each approved Agent becomes a professional CrewAI Agent, preserving role, goal, backstory, model, tools, knowledge, memory, reasoning, planning — **only where those capabilities were approved**. A generated Agent should not gain capabilities merely because CrewAI makes them available.

---

# 11. Task Generation & Prompt Generation

Each approved Task preserves purpose, instructions, inputs, context, expected output/schema, validation, dependencies. Task descriptions stay concise; don't repeat architecture rules inside every Task prompt. **Prompts** assemble from `Agent identity + approved Skills + relevant Knowledge + required Context + Task instructions` — avoiding duplicated architecture docs, full story/project state, irrelevant Knowledge, other Agent instructions. Objective: a **minimum sufficient prompt footprint**.

---

# 12. Context Generation

Context generated from the Process/Task contract: `Architecture → Required inputs → Relevant state → Relevant previous outputs → Relevant Knowledge/Skills → Task context`. Don't inject the complete Flow state or complete Knowledge base into every Agent.

---

# 13. Tool / MCP Generation

**Tool:** generated only when the approved architecture requires a callable external capability; define name, purpose, input, output, permissions, timeout, failure behavior, side effects, idempotency. Avoid generic high-power tools when a narrow tool suffices. **MCP:** if architecture requires it, generated config identifies server, required capabilities, authentication, permissions, inputs/outputs, failure behavior. Amsha should not automatically expose every capability available from an MCP server.

---

# 14. Knowledge / Skills / Memory / Artifacts

Preserve distinction: `Knowledge → reference information · Skills → reusable methodology`. Include Knowledge only where required, Skills only where they materially improve execution; avoid embedding large Knowledge docs directly into prompts when retrieval/reference is appropriate. **Memory** generated only when explicitly justified — not as a substitute for Flow state, Knowledge, Task context, or Artifacts; clearly define what Memory retains. **Artifacts:** large/persistent outputs represented as artifacts (`Task → Artifact → Reference → Next Process`); generated code passes references where practical instead of repeatedly passing large content through Flow state.

---

# 15. Validation Generation

Every important architectural boundary has corresponding validation. Prefer deterministic validation for schema, required fields, references, types, formats, ranges, graph structure, state invariants, artifact integrity. Use semantic evaluation only where deterministic validation cannot determine quality.

---

# 16. Failure / Recovery / Checkpointing Generation

Implement approved failure behavior: for each relevant operation, `success, valid negative result, retryable failure, recoverable failure, terminal failure` must remain distinguishable. Retry limits explicit; side-effecting ops have idempotency/recovery handling. **Checkpointing** only if part of the architecture — checkpoint at approved recovery boundaries, referencing execution, Flow version, state, outputs, artifacts, decisions, iterations, approvals. Don't add global checkpointing when the architecture doesn't require it.

---

# 17. Observability, Configuration

**Observability:** expose meaningful runtime info where applicable — execution ID, Flow ID/version, Process, Task, Agent/Crew, Tool/MCP calls, failures, retries, artifacts, duration, token/cost. Must not alter workflow behavior. **Configuration:** separate from architecture logic — LLM/model, credentials, environment settings, timeouts, resource limits, paths, external endpoints. Secrets must never be generated into source code or prompts.

---

# 18. Tests

Generate tests proportional to architectural complexity: architecture schema validation, Flow transition tests, state invariant tests, Process contract tests, Tool input/output tests, failure-path tests, checkpoint recovery tests, artifact tests. Semantic Agent behavior evaluated separately from deterministic structural tests.

---

# 19. Structural Validation & Traceability

After generation, verify the project structurally matches the architecture (`Approved Architecture → Generated Project → Architecture ↔ Implementation Check`): Processes implemented, Flows/Agents/Tasks/Crews present, dependencies and capabilities preserved, required validation present. **Traceability:** retain architecture identifiers (`architecture: {version}`; `process/task/agent: {id}`) so `Requirement → Process → Task → Agent → Source Code` stays traceable.

---

# 20. Generation Metadata, Regeneration, Modes

**Metadata:** record source architecture — `amsha: {architecture_id, architecture_version, generated_at, generator_version}` — makes regeneration/debugging easier. **Regeneration:** repeatable; a changed architecture produces a new implementation version rather than silently overwriting architectural history. **Modes** (future): `generate_new, update_existing, regenerate, validate_existing, generate_patch`; initial implementation can support only the smallest required subset.

---

# 21. Existing Project Handling, Generation Failure

**Existing project:** first determine current architecture, current implementation, architecture/implementation version, differences; don't blindly overwrite files. **Generation failure:** on an architectural conflict, return a structured BLOCKED result rather than approximate code:

```yaml
generation:
  status: BLOCKED
  reason:
    category: IMPLEMENTATION_CONFLICT
    message: ""
  action:
    type: ARCHITECTURE_REVISION_REQUIRED
```

---

# 22. Project Generation Contract & Quality Criteria

**Contract:**

```yaml
project_generation:
  architecture_id: ""
  architecture_version: ""
  input: { validated: true }
  implementation:
    framework: crewai
    specification: {}
  output:
    project_path: ""
    files: []
  validation:
    architecture_alignment: ""
    structural: ""
    tests: ""
  status: ""
```

**Quality criteria:** architectural fidelity, functional completeness, component correctness, minimality, prompt efficiency, configuration correctness, failure handling, security, testability, observability, traceability, maintainability. Most important:

> **Does the generated project faithfully implement the approved architecture?**

---

# 23. Final Generation Pipeline

`APPROVED ARCHITECTURE → IMPLEMENTATION SPEC → COMPONENT MAPPING → {FLOW → AGENTS, CREW → TASKS, PYTHON → TOOLS} → PROJECT GENERATION → STRUCTURAL VALIDATION → ARCHITECTURE ALIGNMENT → {PASS → EXECUTE | FAIL → REVISE ARCHITECTURE}`.

---

# 24. Core Rules

1. Architecture comes before code.
2. Generate only from a validated architecture.
3. Treat generation as compilation, not redesign.
4. Preserve Process and Flow boundaries.
5. Map capabilities according to approved decisions.
6. Do not generate unused CrewAI mechanisms.
7. Keep prompts and context minimal.
8. Preserve structured contracts and schemas.
9. Generate deterministic validation wherever possible.
10. Implement approved failure and recovery behavior.
11. Keep secrets outside generated source and prompts.
12. Preserve architecture traceability.
13. Record architecture and generator versions.
14. Validate generated code against the source architecture.
15. If implementation requires architectural changes, stop and return to architecture design.

> **Amsha Project Generation is the final translation from architectural intent into CrewAI implementation—not the place where architectural decisions are made.**