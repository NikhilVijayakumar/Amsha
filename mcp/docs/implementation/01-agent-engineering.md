# Agent Engineering

## 1. Purpose

This document defines how Amsha should engineer CrewAI Agents from a validated architecture. An Agent is an implementation of a **professional semantic capability** — the smallest sufficient professional capability required by the Processes and Tasks assigned to it. The objective is not to create the most capable Agent possible, but the **most appropriate Agent for the required work**.

---

# 2. Agent Engineering Position

Agent engineering occurs after the prerequisite pipeline: `Problem Definition → Goal & Boundary → Process Decomposition → Process Contracts → Process Validation → Flow & State Planning → Failure Planning → Capability Selection → Architecture Validation → Agent Engineering`.

Agent engineering must therefore **implement an existing architectural requirement** — it must not invent the requirement.

---

# 3. What an Agent Represents

> A bounded professional capability capable of performing semantic work within a defined domain.

An Agent may provide domain expertise, professional judgment, interpretation, reasoning, analysis, generation, evaluation, creative work, and contextual decision-making.

An Agent should not primarily represent a workflow step, a technical function, a generic LLM, a tool, a data structure, a Flow, or a Task.

---

# 4. Agent Identity Model

```text
Agent
 ├── Role
 ├── Goal
 └── Backstory
```

These fields answer different questions and should complement one another rather than duplicate one another:

- **Role** — Who am I professionally?
- **Goal** — What professional responsibility do I pursue?
- **Backstory** — Why do I have this expertise and perspective?

---

# 5–6. Role Engineering & Structure

The Agent `role` should identify a recognizable professional archetype with appropriate specialization. Prefer `role: "Senior Narrative Continuity Editor"` over `"Story Agent"` or `"Continuity Processing Agent"` — the first describes a professional; the latter two describe software behavior.

A useful role pattern is `[Seniority] + [Professional Discipline] + [Specialization]`, e.g. `Senior Narrative Editor`, `Veteran Historical Researcher`, `Senior Character Psychologist`, `Forensic Financial Analyst`, `Lead Dialogue Editor`. Not every role requires all three components — `Narrative Editor` may be sufficient when specialization or seniority adds no meaningful value.

---

# 7. Professional Archetype

The role should correspond to a profession a real specialist could plausibly hold.

- **Good:** Narrative Editor, Screenwriter, Historical Researcher, Forensic Accountant, Legal Researcher, Character Psychologist, Music Producer, Dialogue Editor.
- **Weak:** Analysis Agent, Reasoning Agent, Creative Agent, Processing Agent, Research Agent, Output Agent.

Technical labels describe implementation; professional labels establish expertise.

---

# 8. Seniority

Seniority should be used when it contributes to the desired behavior — e.g. `Junior, Associate, Specialist, Senior, Lead, Principal, Veteran, Expert, Master`. It should not be added merely to sound impressive. `Senior Narrative Continuity Editor` is useful when the Process requires experienced editorial judgment; `World-Class Universal Everything Expert` is not a meaningful professional boundary.

---

# 9. Specialization

Specialization should narrow the Agent to the domain that actually matters — `Writer` vs `Screenplay Dialogue Editor` vs `Senior Screenplay Dialogue Editor`. The right level depends on the Tasks. Too broad: `Story Expert`. Too narrow: `Scene 14 Dialogue Checker`. Appropriate: `Screenplay Dialogue Editor`.

> The smallest professional scope that naturally covers the Agent's assigned Tasks.

---

# 10. Agent Goal

The `goal` should describe the Agent's enduring professional responsibility: outcome-oriented, stable across Tasks, professionally meaningful, aligned with the role, broad enough to cover related Tasks, narrow enough to preserve specialization.

```yaml
goal: >
  Preserve narrative continuity and identify contradictions
  across characters, events, timelines, and story structure.
```

---

# 11. Goal Is Not a Task

Avoid embedding Task-specific instructions into the Agent goal. Bad: `read the screenplay, compare every scene..., produce JSON, send results to next Task` — this mixes Agent responsibility + Task instructions + Output contract + Workflow behavior. The Task should define the current operation; the Flow should define what happens next.

---

# 12. Goal Stability

The Agent goal should stay relatively stable across executions: `Narrative Continuity Editor` may perform Task 1 (character), Task 2 (timeline), Task 3 (plot), Task 4 (cross-chapter) while its professional goal remains stable. This creates `Agent = enduring capability`, `Task = current bounded responsibility`.

---

# 13. Backstory Engineering

The `backstory` should establish the professional perspective: experience, expertise, professional history, methodology, working style, professional values, relevant perspective.

```yaml
backstory: >
  A veteran narrative editor with extensive experience in
  long-form serialized fiction. Known for tracing continuity
  across complex timelines, character arcs, and interdependent
  plot events while preserving the author's intended structure.
```

---

# 14. Backstory Is Not a Capability Dump

Avoid a backstory that lists unbounded capabilities (`Expert in Python, SQL, APIs..., image generation...`). It does not create professional identity. If a capability is required, represent it through `Tool / Knowledge / Skill / Task / Flow / Python / MCP`, not through the backstory.

---

# 15. Backstory Is Not Knowledge

Do not put dynamic or reference information in the backstory (`The protagonist is Arjun, born in 1985...`). That is story/domain data and belongs in `Knowledge / Context / Memory / Task Input`. The backstory describes the professional, not the current project.

---

# 16. Backstory Is Not Task Instructions

Do not hide operational instructions in the backstory (`Always read chapters 1–10, output JSON, call the database...`). These are workflow and Task instructions — keep them explicit.

---

# 17. Agent Scope

```yaml
agent_scope:
  domain: "Narrative continuity"
  responsibilities:
    - character continuity
    - timeline continuity
    - event continuity
  exclusions:
    - prose rewriting
    - screenplay generation
    - production scheduling
```

Exclusions are especially useful when ambiguity could cause capability expansion. The representation may vary by implementation, but the conceptual boundary should remain explicit.

---

# 18. Smallest Sufficient Agent

```text
What Tasks must this Agent perform?
        ↓
What professional capability covers those Tasks?
        ↓
What is the smallest coherent professional scope?
```

The Agent should be broad enough to perform related work without requiring multiple artificial Agents. Tasks: evaluate character/timeline/event continuity → `Senior Narrative Continuity Editor`. No `Character/Timeline/Event Continuity Agent` unless the architecture identifies meaningful specialist differences.

---

# 19. When to Split an Agent

Consider multiple Agents when there are meaningful differences in:

- **Professional discipline** — Historian vs Forensic Accountant.
- **Expertise** — Dialogue Editor vs Cinematographer.
- **Perspective** — Narrative Editor vs Character Psychologist.
- **Evaluation criteria** — Story Quality vs Legal Compliance Specialist.
- **Failure domain** — substantially different failure/validation characteristics may improve isolation.
- **Human responsibility** — distinct responsibilities mapping to distinct human review boundaries.

---

# 20. Do Not Split an Agent Merely Because Tasks Differ

An Agent can perform multiple Tasks within the same professional responsibility — one `Senior Historical Researcher` handles research, verify, and plausibility. Do not create `Research/Verification/Plausibility Agent` without a meaningful architectural reason.

---

# 21–22. Agent-to-Task Alignment

Every Task assigned to an Agent should be professionally appropriate: `Agent Role / Goal / Backstory` aligned with `Task Purpose / Inputs / Output`.

**Alignment test:** Would a real professional represented by this Agent reasonably be responsible for this Task? If no, one of these may be wrong: Agent role, specialization, Task assignment, Process decomposition, capability selection. Do not solve alignment problems by making the Agent increasingly generic.

---

# 23. One Agent, Multiple Tasks

Often the preferred pattern when Tasks belong to the same domain: `Senior Narrative Editor` → Analyze narrative structure, Evaluate character arc, Identify continuity issues. This keeps professional context stable while Tasks remain independently bounded.

---

# 24. Multiple Agents, One Task

Appropriate when a Task genuinely requires multiple professional perspectives (e.g. `Evaluate historical screenplay accuracy` → Historical Researcher + Cultural Historian + Narrative Editor). This should usually be represented architecturally as collaboration — the implementation may require a Crew — rather than simply attaching unrelated Agents to a Task.

---

# 25. Agent vs Crew

An Agent is sufficient when one professional capability can reliably perform the Process. Use a Crew when the Process genuinely benefits from multiple specialists, independent perspectives, specialist critique, collaboration, delegation, or synthesis across disciplines. Do not create a Crew merely because a Process contains multiple internal steps.

---

# 26. Agent Configuration Principle

```yaml
agent:
  id: ""
  role: ""
  goal: ""
  backstory: ""
  llm: ""
  tools: []
  knowledge: []
  memory: null
  reasoning: false
  planning: false
```

Not every field should be populated — optional capabilities should be enabled only when required.

---

# 27. LLM Selection

Select the LLM according to the work's requirements: reasoning, generation quality, context, latency, cost, structured output, local vs external execution, privacy, operational constraints. Do not select the most powerful model automatically.

> Minimum sufficient model capability for the required quality.

---

# 28. Model Specialization

Different Agents may legitimately use different models: a deterministic classifier → small/efficient model or Python; narrative generation → higher-quality generative model; complex semantic evaluation → strong reasoning model. Model selection follows Process requirements rather than project-wide uniformity by default.

---

# 29. Tools

Give an Agent only the tools required by its responsibilities (`Historical Researcher → Research Tool`; `File Analyst → File Reading Tool`; `Database Specialist → Database Tool`). Avoid giving every Agent all tools — tool availability expands the Agent's effective capability and behavioral search space.

---

# 30. Tool Permission Boundary

Treat tool access as a permission boundary. For every Agent: `Tool → Why does this Agent need it? → Which Task requires it? → What operations are permitted?` If no clear answer exists, the tool should not be automatically attached.

---

# 31. Knowledge Assignment

Select knowledge sources according to the Agent's actual domain responsibilities: `Narrative Continuity Editor → Story Bible, Character Reference, World Rules`; `Financial Analyst → Financial Policy, Accounting Reference`. Do not attach every project knowledge source to every Agent.

---

# 32. Knowledge vs Agent Backstory

- **Backstory** → professional perspective (`Veteran historian experienced in South Indian medieval history`).
- **Knowledge** → domain/reference information (`Historical chronology, source records, regional terminology`).

This separation lets the same professional Agent architecture operate across different projects.

---

# 33. Skills Assignment

Skills provide reusable methodologies (methodology, procedure, evaluation framework, heuristics, quality criteria) the Agent may apply across Tasks (`Narrative Continuity Editor → continuity-analysis skill`). The Agent provides professional identity; the Task defines the current operation.

---

# 34. Memory Assignment

Attach Memory only when historical retention is required (learning from prior interactions, maintaining persistent preferences, retaining previous decisions, preserving historical execution info). Do not attach Memory merely because the Agent should "remember" during one Task. Current Task info → input/context; current execution info → Flow state; stable reference info → Knowledge.

---

# 35. Reasoning Configuration

Enable Reasoning when the Process benefits materially (complex analysis, multi-factor judgment, difficult semantic inference, ambiguity resolution, complex evaluation). Do not enable by default — a simple classification Task may not require it.

---

# 36. Planning Configuration

Enable Planning only when the Agent must dynamically determine its own action sequence (`Research objective → Agent determines research plan → Execute research actions`). Not required for a known sequence `Flow → Task A → B → C`.

---

# 37. Agent Prompt Footprint

```text
Agent Footprint =
    Role + Goal + Backstory + Skill Instructions + Knowledge Context
  + Memory Context + Task Context + Tool/MCP Descriptions + Other Runtime Context
```

The Agent itself should remain concise enough that its static identity does not dominate the prompt.

---

# 38. Avoid Redundant Identity

Do not repeat the same information across `Role, Goal, Backstory, Task Description, Skill`. If `role: "Senior Narrative Continuity Editor"`, don't rewrite `You are a senior narrative continuity editor...` everywhere. Redundancy increases token cost without necessarily improving behavior.

---

# 39. Professional Persona Without Theater

Backstories should establish useful behavioral priors without theatrical biographies.

- **Weak:** *After surviving countless impossible assignments across seven continents, this legendary genius has mastered every form of storytelling...*
- **Better:** *A veteran narrative editor experienced in complex serialized fiction, with a disciplined approach to continuity, causality, character development, and timeline consistency.*

The objective is useful professional conditioning, not literary decoration.

---

# 40. Agent Instructions vs Task Instructions

```text
Agent: Professional identity + responsibility + perspective
Task:  Current input + operation + constraints + expected output
```

This lets the same Agent execute multiple related Tasks without repeatedly redefining its identity.

---

# 41. Dynamic Information Must Stay Dynamic

Do not place execution-specific information in static Agent configuration (`The current screenplay contains 47 scenes...`). `Flow State / Task Context / Artifact Reference` should carry it. Static Agent configuration should remain reusable.

---

# 42. Agent Output Responsibility

An Agent performs semantic work; the Task defines the expected output. `Agent → capability`, `Task → output contract`. An Agent should not implicitly produce every output format it may encounter — the current Task determines the required result.

---

# 43. Agent Quality Criteria

Evaluate each Agent against: professional clarity, domain specialization, appropriate seniority, goal clarity, backstory relevance, professional plausibility, scope sufficiency, scope minimality, agent–task alignment, knowledge relevance, skill relevance, tool minimality, memory necessity, reasoning necessity, planning necessity, context efficiency, token efficiency, security/permission correctness, architectural traceability, overall simplicity.

---

# 44. Agent Validation

```yaml
agent_validation:
  agent_id: ""
  status: ""
  identity:
    role_valid: false
    goal_valid: false
    backstory_valid: false
  scope:
    sufficient: false
    minimal: false
    overlap_with_other_agents: []
  alignment:
    tasks: []
    valid: false
  capabilities:
    tools: []
    knowledge: []
    skills: []
    memory: null
    reasoning: false
    planning: false
  efficiency:
    prompt_footprint: ""
    context_efficiency: ""
    capability_minimality: ""
  security:
    valid: false
    findings: []
  findings:
    - id: ""
      severity: ""
      category: ""
      message: ""
      recommendation: ""
  traceability:
    processes: []
    requirements: []
  approved: false
```

This is a conceptual schema; the final implementation schema may evolve with Amsha.

---

# 45. Agent Validation Rules

Reject or flag an Agent when: role is vague (`AI Assistant`); role is purely technical (`JSON Processing Agent`) unless intentionally technical; goal duplicates the Task; backstory contains large irrelevant info; backstory contains dynamic project state; Agent too broad; Agent unnecessarily narrow; unrelated tools; unnecessary Knowledge; Memory without an architectural requirement; Reasoning enabled without justification; Planning enabled for a deterministic workflow; no traceable architectural responsibility.

---

# 46. Agent Overlap

Detect significant responsibility overlap (Agent A `Senior Narrative Editor` → continuity/structure/character arcs vs Agent B `Story Expert` → continuity/structure/character arcs). This may indicate unnecessary duplication. Evaluate overlap on actual responsibilities, not merely names.

---

# 47. Agent Boundary Matrix

```yaml
agent_boundaries:
  - agent_id: continuity_editor
    owns:
      - character continuity
      - timeline continuity
      - event continuity
    does_not_own:
      - prose rewriting
      - visual direction
      - production scheduling
```

---

# 48. Agent Collaboration Boundary

When Agents collaborate, each should contribute a distinct professional perspective — `Historical Researcher → evidence`, `Narrative Editor → narrative implications`, `Cultural Historian → cultural plausibility`. Weak: `Research Agent A/B/C` all performing the same responsibility. Collaboration should produce complementary expertise, not duplicated expertise.

---

# 49. Agent Creation Decision Process

```text
Does the Process require semantic capability?
    ├── No → use deterministic mechanism
    └── Yes
         ↓
Can one professional capability perform it?
    ├── Yes → Define smallest sufficient Agent
    └── No  → Identify distinct specialists → Evaluate Crew
```

This prevents unnecessary Agent proliferation.

---

# 50. Agent Engineering Workflow

```text
Validated Process → Assigned Tasks → Required Professional Capability →
Professional Archetype → Specialization → Appropriate Seniority → Role →
Enduring Professional Goal → Relevant Professional Backstory → Required
Knowledge/Skills → Required Tools → Memory/Reasoning/Planning Evaluation →
Context Requirements → Token Footprint Evaluation → Agent Validation
```

Only after validation should the Agent be considered implementation-ready.

---

# 51. Agent Specification

```yaml
agent:
  id: ""
  role: ""
  goal: ""
  backstory: ""
  scope:
    domain: ""
    responsibilities: []
    exclusions: []
  tasks: []
  llm:
    provider: ""
    model: ""
    parameters: {}
  capabilities:
    tools: []
    knowledge: []
    skills: []
    memory: false
    reasoning: false
    planning: false
  context:
    required: []
    excluded: []
  permissions:
    tools: []
    data: []
  constraints:
    token_budget: null
    latency_target: null
  traceability:
    processes: []
    requirements: []
  validation:
    status: ""
```

This specification should remain independent from generated Python wherever possible.

---

# 52. Example

Architecture: `Process: Evaluate screenplay continuity`, inputs `screenplay, character records, timeline records`, output `continuity report`. Implementation reasoning:

```text
Required capability: Semantic continuity analysis
Professional: Senior Narrative Continuity Editor
Agent:
    Role:     Senior Narrative Continuity Editor
    Goal:     Preserve continuity across characters, events,
              timelines, and story structure.
    Backstory: Veteran narrative editor experienced in
              complex serialized fiction and continuity analysis.
Task: Analyze the supplied screenplay against the provided
      continuity references and produce the defined continuity report.
```

The separation: `Agent → professional capability`, `Task → current operation`, `Knowledge → continuity references`, `Flow → decides when evaluation occurs`, `Python → validates the report structure`.

---

# 53. Anti-Patterns

- **Generic Agent** — `role: "General AI Assistant", goal: "Help with anything"`: no specialization, weak responsibility boundary, difficult Task alignment, capability leakage.
- **Task Embedded in Goal** — `Read input, analyze, write JSON, validate, send to next Task`: mixes responsibilities, reduces reusability, duplicates workflow logic.
- **Biography Backstory** — huge fictional biography with little relevance: token waste, weak signal-to-noise.
- **Capability Dump** — `Expert in Python, SQL, APIs...`: artificial generalist, obscures identity, expands capability.
- **Dynamic Knowledge in Backstory** — static config becomes project-specific, poor reuse, prompt duplication.
- **Tool Overloading** — one Agent with 30 unrelated tools: excessive capability, larger tool context/decision space, security concerns.
- **Agent Per Task** — `Task A→Agent A...`: Tasks may belong to one professional capability.
- **One Agent for Everything** — research/writing/evaluation/programming/publishing/admin: no specialization, difficult evaluation, poor boundaries.

---

# 54. Optimization Order

When an Agent is too expensive or ineffective, optimize in order: remove irrelevant context → remove redundant prompt content → improve Task definition → improve structured output → remove unnecessary tools → remove unnecessary capabilities → evaluate model choice → reconsider Agent scope → reconsider architecture if necessary. Do not immediately increase model size.

---

# 55. Agent Engineering Principle

A strong Agent is not the one with the most capabilities. It is: professionally coherent + architecturally necessary + task-aligned + sufficiently capable + minimal in scope + efficient in context + explicitly bounded.

---

# 56. Final Rule

> **Create an Agent only when the architecture requires a genuine professional semantic capability, define it as the smallest coherent professional role that can satisfy its assigned Tasks, and give it only the knowledge, skills, tools, memory, reasoning, planning, context, and model capability required to perform that responsibility reliably.**

```text
Process defines the work.
Capability selection defines whether an Agent is needed.
Agent defines the professional capability.
Task defines the bounded operation.
Flow defines when and how it executes.
Validation determines whether it is correct.
```

**An Agent is a professional capability, not a workflow step.**
