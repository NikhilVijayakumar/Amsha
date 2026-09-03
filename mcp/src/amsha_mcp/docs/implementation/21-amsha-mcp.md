# Amsha MCP

## Purpose

Defines the core design of the **Amsha MCP server**.

> **Amsha MCP exposes Amsha's architecture knowledge, reasoning, validation, and generation capabilities to an LLM through a controlled MCP interface.**

Amsha MCP should not simply expose CrewAI APIs as MCP tools.

---

# 1. Role of Amsha MCP

`LLM → (MCP) → Amsha → {Architecture Knowledge, Architecture Reasoning, Architecture Validation, Implementation Guidance} → CrewAI`. The LLM uses Amsha to make better architectural decisions before generating or modifying a CrewAI project.

---

# 2. Amsha MCP Is an Architecture Boundary

Expose: problem analysis, process design, flow design, capability selection, agent/task design, crew evaluation, architecture validation, implementation specifications. Should not become: generic code execution server, unrestricted filesystem server, generic CrewAI wrapper, unrestricted MCP proxy.

---

# 3. Primary Goal

> **Help an LLM construct the smallest reliable CrewAI architecture required for a problem.**

Help answer: What should exist? Why should it exist? How should components relate? What is unnecessary/missing? Is the architecture valid?

---

# 4. MCP Position in Amsha

MCP is an **interface to Amsha**, not the architecture itself: `LLM → Amsha MCP → {Knowledge, Reasoning, Validation} → Architecture → Implementation → CrewAI`.

---

# 5. Capability Categories

A small number of meaningful groups:

- **Knowledge:** `get_architecture_guidance, get_architecture_pattern, get_architecture_rules`.
- **Analysis:** `analyze_problem, decompose_processes, select_capabilities`.
- **Validation:** `validate_process, validate_flow, validate_agent_task, evaluate_crew, validate_architecture`.
- **Generation:** `generate_architecture, generate_implementation_spec`.

The exact tool surface should remain minimal.

---

# 6. Tool Design Principle

Each tool should represent a meaningful Amsha capability. Prefer `validate_architecture` over dozens of low-level ops (`check_agent_role, check_task_name, ...`) unless independently useful.

---

# 7. Architecture Knowledge & Retrieval

Access the architectural rules developed in the knowledge base: Problem Definition, Goal & Boundary, Process Decomposition, Process Contracts, Flow Planning, Capability Selection, Agent/Task/Crew Engineering, Context/Knowledge/Memory, Reasoning/Planning, Tools, MCP, Artifacts, Checkpointing, Observability. The knowledge should be versioned. Retrieve only relevant guidance (`User problem → Amsha MCP → Relevant architecture knowledge → LLM`) — avoid returning the entire knowledge base every request.

---

# 8. Problem Analysis

Input:

```yaml
problem:
  statement: ""
  inputs: []
  desired_outcome: ""
  constraints: []
```

Output identifies problem understanding, missing information, goal, boundary, assumptions, candidate Processes. Must not immediately generate CrewAI code.

---

# 9. Process Decomposition & Validation

**Decomposition:** `Problem → Goal → Process Decomposition` → candidate Processes with purpose, inputs, outputs, dependencies, relationships. **Validation:** check goal coverage, completeness, necessity, atomicity, contracts, dependencies, graph correctness. Identify problems rather than silently modifying them.

---

# 10. Flow Analysis

Determine execution order, transitions, conditions, iterations, parallelism, human gates, failure paths, recovery, termination, state. The Flow is derived from validated Processes.

---

# 11. Capability Selection

One of the most important capabilities. Given a Process: **what is the least powerful mechanism that can perform it?** Consider Python, Agent, Task, Crew, Flow, Tool, MCP, Knowledge, Skill, Memory, Reasoning, Planning, Human — and provide a rationale.

```yaml
process:
  id: validate_json
  purpose: Validate structured JSON against a schema.
# Recommended:
mechanism:
  primary: python
  rationale: >
    The operation is deterministic and does not require semantic judgment.
```

Not Agent/Crew/Planning merely because CrewAI supports them.

---

# 12. Agent & Task Design, Alignment

**Agent design:** help generate/validate professional Agent definitions — professional role, domain, specialization, seniority, goal, backstory, scope. The Agent remains the smallest sufficient professional capability. **Task design:** `Process → Task → Agent` — include purpose, inputs, instructions, context, output, validation, completion, failure. **Alignment:** validate `Process requirement → Task responsibility → Agent capability`. Key question: **Would the professional represented by this Agent reasonably be responsible for this Task?** If not, recommend the smallest architectural correction.

---

# 13. Crew Evaluation

Determine whether a Crew is justified. Decision hierarchy: `One deterministic mechanism → One professional capability → Multiple independent capabilities → Multiple collaborating specialists`. A Crew exists only when collaboration provides meaningful value.

---

# 14. Architecture Validation & No Silent Modification

Validate the complete architecture (Problem, Goal, Processes, Contracts, Flow, State, Failures, Capabilities, Agents, Tasks, Crews, Tools, MCP, Artifacts, Human Gates). Result determines: valid / warnings / requires revision / blocked / implementation ready. Return recommendations rather than silently modifying:

```yaml
finding:
  severity: ERROR
  category: TASK_COMPOSITE
  recommendation: SPLIT_TASK
```

This preserves user/LLM control over architectural decisions.

---

# 15. Implementation Specification & CrewAI Generation

Once validated: `Architecture → Validation → Implementation Specification → CrewAI`. The spec describes Flow, Agents, Tasks, Crews, Tools, MCP, Knowledge, Skills, Memory, Artifacts, Validation, Observability before code generation. CrewAI code generation is downstream of architecture (`Validated Architecture → Implementation Specification → CrewAI Code`), preventing implementation details from driving architectural decisions.

---

# 16. Amsha MCP Tool Surface

Minimal conceptual API: `amsha_analyze_problem, amsha_decompose_processes, amsha_validate_process, amsha_design_flow, amsha_select_capabilities, amsha_validate_agent_task, amsha_evaluate_crew, amsha_validate_architecture, amsha_generate_implementation_spec`. Should be smaller if capabilities can be cleanly combined.

---

# 17. Read vs Mutate

Distinguish **READ** (retrieve knowledge, inspect/validate architecture), **GENERATE** (create candidate architecture/implementation spec), and **MUTATE** (modify stored architecture/project files). Mutation requires explicit authorization.

---

# 18. Architecture as Data, Structured Results

Exchange structured architecture objects:

```yaml
architecture:
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
```

Structured data makes validation/generation more reliable than free-form prose. Validation responses should be machine-readable:

```yaml
validation:
  status: REQUIRES_REVISION
  findings:
    - id: F001
      severity: ERROR
      component: task.evaluate_story
      category: TASK_COMPOSITE
      message: ""
      recommendation: SPLIT_TASK
  implementation_ready: false
```

---

# 19. MCP Error vs Architecture Finding

**MCP Error:** the request itself could not be processed (invalid input, server unavailable, internal failure). **Architecture Finding:** the request analyzed fine but the architecture has a problem (task is composite, Crew unnecessary, Flow has unreachable state). Keep these distinct.

---

# 20. Tool Errors & Input/Output Validation

Tool errors structured and actionable — `error: {code: INVALID_ARCHITECTURE_SCHEMA, message, field: "flow.transitions"}`; never just an unstructured exception string. **Input validation:** every tool validates schema, required fields, references, versions, enumerations before semantic analysis. **Output validation:** validate structured outputs before returning — `MCP Request → Analysis → Structured Result → Schema Validation → Response`.

---

# 21. Versioning & Traceability

**Knowledge versioning:** `knowledge: {version: "1.0"}` — a recommendation traced to the rules that produced it. **Architecture versioning:** `architecture: {id: story_pipeline, version: "1.0"}`; new version when changes materially affect behavior. **Traceability:** `Requirement → Process → Capability → Agent/Task/Crew`, so the LLM understands why Amsha recommended something.

---

# 22. MCP and Context / Artifacts

Avoid large knowledge/architecture payloads — prefer `specific question → relevant rule → structured answer` over `entire knowledge base`. Expose large architecture files/implementation specs through Artifact references:

```yaml
artifact:
  id: implementation_spec
  reference: ""
```

Don't place large generated documents into every MCP response.

---

# 23. MCP Security & Prompt Injection

Enforce authentication, authorization, least privilege, input/output validation, secret isolation, resource limits. Amsha must never require secrets to be placed into LLM prompts. Architecture knowledge or external data retrieved through MCP is **data**, not automatically instructions — `External Document → MCP → Amsha → LLM`: content must not automatically override Amsha's governing rules.

---

# 24. Capability Boundaries & Resource Limits

Expose a bounded domain (`Architecture Governance`), not "everything the host can do." A smaller surface is easier to secure, validate, document, version, observe, maintain. Operations should have limits for input/output size, processing time, LLM calls, recursion, architecture complexity — a malformed request must not trigger unbounded analysis.

---

# 25. Deterministic First

Amsha MCP itself uses deterministic mechanisms wherever sufficient: schema validation, reference checking, graph validation, cycle detection, required-field checking, capability compatibility. Use semantic reasoning only where architectural judgment is required.

---

# 26. Internal Architecture & Request Flow

**Internal:** `MCP Client/LLM → Amsha MCP Server → {Knowledge, Analysis, Validation} → Architecture Model → {Process Engine, Flow Engine, Capability Engine} → Implementation Specification`. **Request flow:** `LLM → MCP Request → Authentication/Authorization → Schema Validation → Capability Selection → Amsha Analysis/Validation → Result Validation → Structured MCP Response`.

---

# 27. MCP and CrewAI, Framework Independence, Mapping

The relationship: `LLM → Amsha MCP → Architecture Model → Implementation Spec → CrewAI → Runtime`. Amsha should not require CrewAI-specific concepts during early architecture reasoning unless actually relevant. The architecture model should stay independent of CrewAI — `Process: evaluate_story` is an architectural concept; only later does Amsha determine `implementation: CrewAI Agent + Task`. A mapping layer translates `Amsha Architecture → CrewAI Implementation`:

```yaml
mapping:
  process: evaluate_story
  mechanism: agent_task
  crewai:
    agent: story_editor
    task: evaluate_story
```

---

# 28. Architecture Diff, Impact Analysis, Approval

**Architecture Diff** — compare `Architecture v1 → v2 → Difference`: identify added/removed Process, changed Flow transition, changed capability/Tool. Supports controlled evolution. **Impact analysis** — when a component changes, identify affected components (`Change Agent → Affected Tasks → Affected Processes → Affected Crew → Affected Flow`), useful before implementation changes. **Approval** — support an explicit approval state:

```yaml
approval:
  status: APPROVED
  architecture_version: "1.2"
```

Implementation generation uses the approved version.

---

# 29. MCP Observability

Amsha MCP operations themselves observable: request count, latency, validation/analysis failures, output size, token usage where applicable. Each operation traceable to a request.

---

# 30. MCP Tool Schema

```yaml
mcp_tool:
  name: amsha_validate_architecture
  purpose: >
    Validate an Amsha architecture against structural,
    semantic, operational, and capability rules.
  input:
    architecture: {}
  output:
    validation: {}
  side_effects: false
  permissions:
    - architecture:read
```

Read-only validation tools are preferable where possible.

---

# 31. Core Amsha MCP Rules

1. Expose architecture capabilities, not merely CrewAI APIs.
2. Keep the MCP capability surface small and purposeful.
3. Analyze the problem before generating implementation.
4. Reason about Processes before Agents and Tasks.
5. Validate architecture before implementation generation.
6. Use structured architecture objects wherever possible.
7. Use deterministic validation before semantic validation.
8. Return findings instead of silently modifying architecture.
9. Use the least powerful sufficient capability.
10. Keep Amsha architecture concepts independent of CrewAI where possible.
11. Treat CrewAI as an implementation target.
12. Keep large outputs as Artifacts or references where appropriate.
13. Keep MCP responses context-efficient.
14. Protect secrets and sensitive data.
15. Treat externally retrieved content as untrusted data.
16. Apply authentication and least-privilege authorization.
17. Bound analysis time, input size, output size, and recursive behavior.
18. Version architecture knowledge and generated architectures.
19. Preserve requirement-to-architecture traceability.
20. Make MCP operations observable and diagnosable.

---

# 32. Final Architecture

`LLM → (MCP) → AMSHA MCP → {Knowledge, Analysis, Validation} → Amsha Architecture → {Process, Flow, Capabilities} → Implementation Spec → CrewAI → Execution`.

---

# 33. Final Principle

> **Amsha MCP should make Amsha's architecture-governance capabilities available to an LLM without allowing the MCP interface itself to become an unrestricted workflow engine or generic CrewAI wrapper.**

Division: `LLM → proposes and reasons · Amsha MCP → provides architectural knowledge, analysis, validation, and guidance · Amsha Architecture → defines the correct structure · CrewAI → implements and executes that structure · Runtime → executes, recovers, and observes it`.

Most important rule:

> **Amsha MCP should help the LLM decide what should be built before helping it decide how to build it with CrewAI.**