# Agent–Task Alignment

## 1. Purpose

This document defines how Amsha determines whether an Agent is appropriately matched to the Tasks assigned to it.

> **Is this Task a natural responsibility of this professional Agent?**

Agent–Task alignment connects two concepts: `Agent → professional capability`, `Task → bounded operation`. A strong implementation requires these compatible without making either artificially broad. Alignment should be evaluated before implementation is considered complete.

---

# 2. Position in the Amsha Architecture

Alignment occurs after `Validated Architecture → Capability Selection → Agent Engineering → Task Engineering → Atomic Task Design → Agent–Task Alignment → Validation → Implementation`. It is not merely a config check — it validates whether the selected professional capability can reasonably satisfy the Process and Task contracts.

---

# 3. Core Principle

> **Every Task should be assigned to the smallest professional Agent whose expertise, responsibility, perspective, and capabilities are sufficient to perform that Task reliably.**

This implies two simultaneous requirements — Sufficiency + Minimality: the Agent must be capable enough but not broader than necessary.

---

# 4. Agent and Task Responsibilities

Keep explicit the separation: `Agent → professional identity, domain expertise, enduring responsibility, professional perspective`; `Task → current purpose, inputs, instructions, constraints, expected output`. So `Agent = who can do this kind of work?`, `Task = what must be done now?`.

---

# 5. Alignment Model

`Process Requirement → Task Responsibility → Professional Capability → Agent`. The Task should be a valid instance of work within the Agent's professional scope. Example: `Process: Evaluate screenplay continuity` + `Task: Identify character and timeline contradictions` + `Agent: Senior Narrative Continuity Editor` → naturally aligned.

---

# 6. The Professional Responsibility Test

> **Would a real professional represented by this Agent reasonably be responsible for performing this Task?**

If yes, alignment is strong. If no, investigate Agent scope, Task scope, Process decomposition, Agent specialization, capability selection. Do not solve misalignment simply by making the Agent more generic.

---

# 7. Alignment Dimensions

Evaluate across at least: Role, Domain, Specialization, Goal, Backstory, Professional perspective, Task purpose/transformation/inputs/outputs, Required knowledge/skills/tools/reasoning/planning/memory, Failure responsibility, Validation responsibility, Security permissions, Overall scope. Not every dimension must be independently decisive; the purpose is a coherent professional pairing.

---

# 8. Role Alignment

The Agent's `role` should naturally correspond to the Task. Strong: `Senior Historical Researcher` + `Verify historical claims against approved sources`. Weak: same Agent + `Design the screenplay's visual language` (unless intentionally included).

---

# 9. Domain Alignment

The Task should belong to the Agent's domain. `Forensic Financial Analyst` (domain: financial investigation) + `Analyze suspicious transaction patterns` → aligned; + `Write emotionally nuanced character dialogue` → outside the domain.

---

# 10. Specialization Alignment

Domain alignment alone may be insufficient. `Historian` + `Perform detailed screenplay dialogue editing` — both relate to historical storytelling but specialization does not align. Better: `Screenplay Dialogue Editor` + `Refine dialogue for characterization and dramatic intent`.

---

# 11. Goal Alignment

The Task should contribute directly to the Agent's enduring goal:

```yaml
agent:
  role: "Senior Narrative Continuity Editor"
  goal: >
    Preserve continuity across characters, events,
    timelines, and story structure.
```

Task `Identify contradictions between the current chapter and established character/timeline references.` directly advances the goal.

---

# 12. Backstory Alignment

The backstory should support the expertise needed for the Task — e.g. `Veteran Historical Researcher` with backstory of source criticism, archival research, chronology, evidence evaluation, supporting `Assess whether the screenplay's historical claims are supported by the available sources.` Backstory should not provide missing Task instructions.

---

# 13. Perspective Alignment

Some Tasks require a particular perspective, not just generic knowledge. `Evaluate whether a character's behavior is psychologically plausible` → `Character Psychologist` rather than `General Writer`.

---

# 14. Task Purpose Alignment

The Task purpose should fit the Agent's responsibility. `Narrative Editor` + `Evaluate narrative pacing` strong; `Narrative Editor` + `Configure GPU drivers` strong misalignment.

---

# 15. Task Transformation Alignment

The actual transformation must be compatible: `Input: Screenplay + character references → Transformation: Continuity analysis → Output: Continuity report → Agent: Narrative Continuity Editor` — the entire transformation is professionally coherent.

---

# 16. Input Alignment

The Agent should have the expertise to interpret the inputs. `Historical documents` + `Evaluate source reliability` → `Historical Researcher` aligned. But `Medical research literature` + `Evaluate clinical evidence` requires a suitably qualified domain specialist. The presence of documents alone does not make an Agent capable of interpreting them.

---

# 17. Output Alignment

The expected output should be natural for the professional. `Narrative Editor` + `Narrative Evaluation Report` natural; `Narrative Editor` + `Database Migration Script` requires a different technical capability unless intentionally within scope.

---

# 18. Knowledge Alignment

Assigned Knowledge should support the Tasks: `Narrative Continuity Editor` + Knowledge `Character Reference, World Rules, Story Timeline`. Avoid `Narrative Continuity Editor + entire unrelated project knowledge base`. Knowledge should follow Task relevance.

---

# 19. Skill Alignment

Skills should be methodologies the Agent can apply: `Narrative Continuity Editor` + `Continuity Analysis Methodology` + `Evaluate Chapter 8 for continuity contradictions` strong. Do not attach unrelated Skills just because they exist.

---

# 20–21. Tool Alignment & Scope

A Tool should exist because a Task requires it: `Historical Researcher` + `Retrieve approved historical sources` + `Historical Source Search`. Evaluate excess capability: `Historical Researcher → historical search tool` is preferable to giving it database admin, email, deployment, file deletion, payment API — unless architecture explicitly requires them. Alignment includes both required capability and unnecessary-capability exclusion.

---

# 22. Reasoning Alignment

Enable Reasoning when the Task requires meaningful complex reasoning (`Compare conflicting historical evidence and determine the most defensible interpretation`). `Validate that "severity" is one of LOW/MEDIUM/HIGH` does not — Python performs the deterministic validation.

---

# 23. Planning Alignment

Enable Planning only when the Task/Process requires dynamic planning (`Investigate an open-ended research question and determine which research actions to perform`). `Summarize the supplied research report` normally does not.

---

# 24. Memory Alignment

Use Memory only when the Task benefits from historical retention (`Continue a long-running user collaboration using prior approved editorial preferences`). `Evaluate the supplied chapter using the supplied references` does not automatically require Memory. Current inputs remain current inputs.

---

# 25. Failure Alignment

The Agent should handle the Task's semantic failure conditions. `Evaluate historical evidence` → `Possible semantic outcome: Insufficient evidence` → `Historical Researcher` appropriate. Do not force the Agent to invent certainty; valid uncertainty or negative findings remain valid outputs when the Process contract allows.

---

# 26. Validation Alignment

The Agent performs semantic work; deterministic validation stays outside the Agent when Python can do it (`Agent: Determine whether a narrative contradiction exists`; `Python: validate schema, identifiers, enums, references`). Clean separation of responsibility.

---

# 27. Human Review Alignment

If a Task requires a human decision, the Agent should not silently replace it. `Agent: Generate revised screenplay` + `Flow: Human approval required` — the Agent performs professional work; the human performs the reserved decision.

---

# 28. Agent Scope Sufficiency

The Agent must be sufficiently capable for all its Tasks. `Narrative Editor` + evaluate pacing/structure/character arcs → potentially sufficient. `Narrative Editor` + evaluate screenplay, perform tax analysis, administer database, manage cloud infrastructure → insufficiently coherent. The solution is not a larger backstory; the architecture should identify distinct professional capabilities.

---

# 29. Agent Scope Minimality

The Agent should not be broader than its Tasks require. For Tasks `evaluate character continuity` + `evaluate timeline continuity`, `Senior Narrative Continuity Editor` may suffice — not a `Universal Narrative, Research, Psychology, Production, Legal and Technical Expert`.

---

# 30. Alignment and Atomicity

A Task may appear misaligned because it is composite. `Historical Researcher` + `Research history + write screenplay + publish asset` may appear inadequate, but the deeper issue is multiple responsibilities. After decomposition (`Historical Researcher → research evidence`; `Screenplay Writer → write scene`; `Production Specialist → prepare asset`) alignment becomes clearer. When alignment fails, first determine whether the Task boundary is wrong before expanding the Agent.

---

# 31. Alignment and Process Boundaries

An alignment problem may originate at the Process level. `Produce Final Film Asset` may actually contain Research, Writing, Direction, Editing, Audio, Rendering, Publishing — no single Agent should own the whole. The correct solution may be Process decomposition before Agent engineering.

---

# 32. Alignment Failure Categories

Classify findings: `ROLE_MISMATCH, DOMAIN_MISMATCH, SPECIALIZATION_MISMATCH, GOAL_MISMATCH, PERSPECTIVE_MISMATCH, SCOPE_TOO_NARROW, SCOPE_TOO_BROAD, KNOWLEDGE_MISMATCH, SKILL_MISMATCH, TOOL_MISMATCH, CAPABILITY_MISMATCH, TASK_COMPOSITE, OUTPUT_MISMATCH, VALIDATION_MISMATCH, FAILURE_BOUNDARY_MISMATCH, PERMISSION_MISMATCH`. This makes findings actionable.

---

# 33. Alignment Severity

`INFO` (Agent has additional unused expertise), `WARNING` (Task slightly broader than specialization), `ERROR` (Task requires a capability not represented by the Agent), `BLOCKING` (Agent cannot reasonably perform the Task and no valid implementation path exists).

---

# 34. Alignment Decision

Produce a decision: `ALIGNED, CONDITIONALLY_ALIGNED, REASSIGN_TASK, REFINE_AGENT, SPLIT_TASK, SPLIT_PROCESS, INTRODUCE_CREW, REJECT`, based on the root cause.

---

# 35. Root-Cause Principle

> **Fix the smallest architectural boundary that resolves the mismatch.**

`Task slightly too broad → refine Task`, not `create a much broader Agent`. `Task requires two distinct specialists → split Task / introduce Crew`, not `create one "Universal Expert" Agent`.

---

# 36. Alignment Matrix

| Task                | Agent                 | Domain    | Specialization | Goal     | Tools    | Knowledge  | Result  |
| ------------------- | --------------------- | --------- | -------------- | -------- | -------- | ---------- | ------- |
| Evaluate continuity | Narrative Editor      | Narrative | Continuity     | Aligned  | Relevant | Relevant   | Aligned |
| Verify history      | Historical Researcher | History   | Research       | Aligned  | Relevant | Relevant   | Aligned |
| Write dialogue      | Historical Researcher | Mixed     | Mismatch       | Partial  | None     | Partial    | Review  |
| Database migration  | Narrative Editor      | Technical | Mismatch       | Mismatch | Missing  | Irrelevant | Reject  |

This makes systemic alignment problems visible.

---

# 37. Alignment Graph

For larger systems: `Process → Task A → Agent A (Knowledge A, Skills A, Tools A)`, `Task B → Agent B`, `Task C → Agent A`. This identifies overloaded Agents, underused Agents, duplicated Agents, missing capabilities, unnecessary tools, knowledge leakage.

---

# 38. Many Tasks to One Agent

Valid when Tasks form one professional capability: `Senior Narrative Editor → evaluate pacing, structure, character arc, continuity`. Tasks remain separate (each independently meaningful); Agent remains shared (coherent capability).

---

# 39. One Task to Multiple Specialists

May indicate a Crew. `Evaluate historical screenplay authenticity` needing Historical Researcher, Cultural Historian, Narrative Editor → use a `Crew` rather than forcing one Agent to simulate every discipline.

---

# 40. Multiple Tasks to Multiple Agents

Often natural for larger workflows (`Task A → Agent A`, `Task B → Agent B`, `Task C → Agent C`, `Task D → Agent A`). The important property is clarity of responsibility, not the number of Agents.

---

# 41. Shared Agent vs Separate Agents

Prefer a shared Agent when: same professional discipline, same domain, same perspective, similar capability requirements, no meaningful boundary conflict. Separate Agents when: different discipline, specialist expertise, evaluation perspective, permissions, capability requirements, or a meaningful responsibility boundary.

---

# 42. Permission Alignment

Alignment includes security. An Agent may be professionally capable but lack permission (`Task: Publish final artifact`, `Agent: Production Coordinator`, `Permission: Read-only`). Distinguish `Professional Capability` from `Operational Permission`.

---

# 43. Capability Gap

Occurs when the Task requires something the Agent lacks (`Query financial database` needs Database Tool + Financial Knowledge) — possible responses: Reassign Task, Split Task, Introduce Specialist, Add required capability (only if it remains within the Agent's coherent professional scope).

---

# 44. Capability Overreach

Reverse problem: `Narrative Editor` with screenplay editor, database admin, cloud deployment, email sender, payment API is suspicious even if technically accessible. Ask which assigned Task requires each; unused capabilities should generally be removed.

---

# 45. Alignment and Token Footprint

Poorly scoped Agents carry large backstory, knowledge set, skills, tools, memory into Tasks needing only a subset. Better alignment reduces prompt footprint (`Specialized Agent → smaller relevant context → fewer tools → less prompt noise → lower token cost`).

---

# 46. Alignment and Model Selection

Different Tasks may need different model capabilities. If one Agent is forced to do unrelated Tasks (`Simple classification` vs `Complex narrative reasoning`), it may require an unnecessarily powerful model for all. Separate Agents may be more appropriate — an implementation optimization that can also reveal an architectural boundary.

---

# 47. Alignment and Context Selection

Knowledge, Skills, Tools, Memory, context should follow the Agent–Task relationship: `Task → Required Capability → Agent → Required Resources (Knowledge, Skills, Tools, Memory, Reasoning/Planning)`. Do not expose every resource to every Agent.

---

# 48. Alignment Validation Workflow

Validate through: `Task → Identify Task Responsibility → Identify Required Professional Capability → Inspect Agent Role/Goal/Backstory/Scope/Knowledge-Skills/Tools/Model-Reasoning-Planning/Permissions → Compare Output Responsibility → Compare Failure Boundary → Evaluate Overall Alignment`.

---

# 49. Alignment Optimization Workflow

When alignment is weak: determine root cause → is Task composite? (split) → is Agent too narrow? (refine if coherent) → is Agent too broad? (narrow) → is another specialist required? (reassign/Crew) → check capability/permission gap. Every modification must be revalidated.

---

# 50. Agent–Task Alignment Specification

```yaml
agent_task_alignment:
  agent_id: ""
  task_id: ""
  process_id: ""
  alignment:
    role: ""
    domain: ""
    specialization: ""
    goal: ""
    perspective: ""
    purpose: ""
    transformation: ""
    input: ""
    output: ""
    knowledge: ""
    skills: ""
    tools: ""
    reasoning: ""
    planning: ""
    memory: ""
    failure: ""
    permissions: ""
  scope:
    sufficient: false
    excessive: false
  findings:
    - id: ""
      severity: ""
      category: ""
      message: ""
      recommendation: ""
  decision:
    status: ""
    action: ""
    rationale: ""
  approved: false
```

---

# 51. Multi-Agent Alignment Specification

```yaml
agent_task_alignment:
  assignments:
    - task_id: ""
      agent_id: ""
      responsibility: ""
  conflicts:
    - agent_a: ""
      agent_b: ""
      overlap: ""
      recommendation: ""
  uncovered_tasks: []
  overloaded_agents: []
  unused_agents: []
  capability_gaps: []
  permission_gaps: []
  final_status: ""
```

This validates the system, not only individual Agent–Task pairs.

---

# 52. Example: Strong Alignment

```yaml
agent:
  id: continuity_editor
  role: "Senior Narrative Continuity Editor"
  goal: >
    Preserve continuity across characters, events,
    timelines, and story structure.
task:
  id: evaluate_continuity
  purpose: >
    Identify contradictions between the current chapter
    and established continuity references.
```

Assessment: Role/Domain/Specialization/Goal/Purpose/Transformation/Output/Knowledge aligned, Tools minimal, Scope sufficient. Decision: `ALIGNED`.

---

# 53. Example: Task Too Broad

```yaml
agent:
  role: "Senior Narrative Continuity Editor"
task:
  purpose: >
    Analyze continuity, rewrite dialogue, compose music,
    generate visual prompts, and publish production assets.
```

Assessment: multiple professional disciplines, outputs, failure domains, capability requirements, completion boundaries. Decision: `SPLIT_TASK` → `Continuity Evaluation → Dialogue Revision → Music Composition → Visual Prompt Generation → Production Publishing`, each with an appropriate specialist.

---

# 54. Example: Agent Too Broad

```yaml
agent:
  role: "Universal Creative Production Expert"
  goal: >
    Perform any creative and technical task required by the project.
```

Tasks: historical research, screenplay editing, audio engineering, image generation, deployment. Assessment: scope too broad, identity unclear, boundaries unclear, permissions likely excessive. Decision: `REFINE_AGENT` and likely `INTRODUCE_SPECIALISTS`.

---

# 55. Example: Agent Too Narrow

```yaml
agent:
  role: "Character Name Validator"
```

Tasks: validate character names, relationships, continuity, evaluate character arcs. The role is too narrow. Refinement: `Senior Character Continuity Editor`. The goal is not four Agents; it is the smallest professional role that naturally covers the Tasks.

---

# 56. Example: Capability Gap

`Narrative Editor` + `Retrieve records from external project database`. If the Task genuinely belongs to the Agent, add an `Approved Database Tool`. But if the database operation is a distinct technical Process, the better architecture may be `Database Retrieval Specialist → Structured Data → Narrative Editor`. The decision depends on the Process contract.

---

# 57. Alignment Does Not Mean Identical Expertise

An Agent need not be perfectly specialized to one Task; a professional naturally performs a family of related responsibilities (`Senior Narrative Editor → pacing, structural, character arc, continuity evaluation`). Alignment is about meaningful professional fit, not exact name matching.

---

# 58. Alignment Does Not Mean Maximum Expertise

A Task should not automatically go to the most specialized/powerful Agent. `Check whether a required field exists` → a deterministic validator may be preferable to any Agent. `Evaluate narrative pacing` → Narrative Editor. The right Agent is the minimum sufficient professional capability.

---

# 59. Alignment and Architecture Governance

Alignment is an architecture-governance mechanism: `Why does this Agent exist? → Which Tasks justify it? → Which Process requires those Tasks? → Which requirement requires the Process?`. This creates Requirement → Process → Task → Agent traceability.

---

# 60. Final Agent–Task Alignment Rules

1. Every Task must have an appropriate professional owner.
2. The Agent must be capable of performing the Task.
3. The Agent should be the smallest sufficient professional capability.
4. Role must align with Task responsibility.
5. Domain must align with Task domain.
6. Specialization must align with Task specialization.
7. Goal must support the Task purpose.
8. Backstory must support the required professional expertise.
9. Knowledge must be relevant to the Task.
10. Skills must be relevant to the Task.
11. Tools must be justified by the Task.
12. Tool permissions must be appropriate to the Task.
13. Reasoning must be justified by Task complexity.
14. Planning must be justified by dynamic execution requirements.
15. Memory must be justified by historical retention requirements.
16. The Agent must have sufficient scope for all assigned Tasks.
17. The Agent should not have unnecessary scope.
18. Composite Tasks should not be solved by creating generic Agents.
19. Agent overlap should be detected and justified.
20. Capability gaps must be explicit.
21. Permission gaps must be explicit.
22. Task outputs must be compatible with the Agent's professional responsibility.
23. Failure responsibilities must remain coherent.
24. Human decision boundaries must remain explicit.
25. Deterministic work should not be assigned to an Agent unnecessarily.
26. Alignment must be evaluated semantically, not by name matching alone.
27. Alignment failures should be fixed at the smallest appropriate architectural boundary.
28. Changes to Agent or Task boundaries require revalidation.
29. Every Agent–Task assignment should remain traceable to a Process.
30. Professional coherence is more important than maximizing Agent reuse.

---

# 61. Core Amsha Principle

`Requirement → Process → Task → (requires) Professional Capability → Agent → (Knowledge, Skills, Tools, Memory, Reasoning, Planning)`.

> **Would this professional naturally and sufficiently perform this Task, with the required knowledge, skills, tools, permissions, and reasoning capability, without making the Agent broader than necessary?**

If yes → `AGENT–TASK ALIGNED`. If no → determine whether the problem belongs to Task boundary, Agent boundary, Process boundary, Crew design, or capability selection.

> **Do not make the Agent generic to fit the Task. Make the Agent and Task boundaries correct.**
