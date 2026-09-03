# Amsha Agent–Task Validation

## Purpose

Defines how Amsha validates the relationship between an engineered **Agent** and the **Tasks** assigned to it. The objective is not merely whether a Task can technically be executed, but whether: the Agent is the correct professional capability, the Task is a coherent responsibility, capability is sufficient and not unnecessarily broad, required knowledge/skills/tools/reasoning/planning/memory/permissions are appropriate, output satisfies the downstream contract, the Process architecture is preserved, and no Process/Task/Crew boundary problem is hidden.

> **Validate the Agent–Task relationship, not the Agent and Task in isolation.**

---

# 1. Position in the Amsha Architecture

Agent–Task validation occurs after Agent and Task engineering, before Crew engineering. The preceding chain: Problem → Goal & Boundary → Process Decomposition → Process Contracts → Process Validation → Flow & State → Failure Planning → Capability Selection → Architecture Validation → Agent Engineering → Task Engineering → Atomic Task Validation → **Agent–Task Alignment → Agent–Task Validation** → Crew Engineering → Implementation.

It operates within an already-approved architecture and must not silently redesign the Process. If validation finds a structural problem, correct the smallest incorrect architectural boundary and revalidate the affected layers.

---

# 2. Core Principle

An Agent should get a Task only when it represents the smallest sufficient professional capability for that Task: `Process Requirement → Task Responsibility → Professional Capability → Agent`. The relationship must be coherent in both directions:

- **Task → Agent:** Does this Agent possess the professional responsibility, expertise, perspective, and capabilities the Task requires?
- **Agent → Task:** Is this Task reasonably within the enduring professional responsibility this Agent represents?

Both must be true.

---

# 3. Agent and Task are Different Architectural Objects

`Agent = who is professionally responsible`; `Task = what bounded operation must be performed`. An Agent (e.g. Senior Narrative Continuity Editor) can legitimately serve many related Tasks (evaluate character continuity; evaluate timeline continuity; identify contradictions vs. the story bible) because they share professional responsibility. Agents and Tasks are not interchangeable.

---

# 4. Validation Objectives

Amsha validates these dimensions:

| Dimension | Question |
|-----------|----------|
| Role | Does the Agent represent the correct profession? |
| Domain | Does the Agent operate in the required domain? |
| Specialization | Is the specialization appropriate? |
| Seniority | Is the level of expertise sufficient? |
| Goal | Is the Task consistent with the Agent's enduring responsibility? |
| Perspective | Does the Agent have the appropriate professional viewpoint? |
| Purpose | Does the Task have a responsibility the Agent should perform? |
| Transformation | Can the Agent perform the required transformation? |
| Inputs | Does the Agent have the information required by the Task? |
| Outputs | Can the Agent produce the required output? |
| Knowledge | Is required reference knowledge available? |
| Skills | Are required methodologies available? |
| Tools | Are required actions/tools available? |
| Reasoning | Is reasoning capability justified and sufficient? |
| Planning | Is planning capability justified and sufficient? |
| Memory | Is retained historical information required? |
| Failure | Are Agent and Task failure boundaries compatible? |
| Validation | Can the Agent produce output satisfying validation criteria? |
| Permissions | Does the Agent have appropriate permissions? |
| Scope | Is the Agent neither too narrow nor unnecessarily broad? |
| Context | Does the Task receive appropriate context? |
| Efficiency | Is the assignment resource-efficient? |
| Traceability | Can the assignment be traced to the Process and requirements? |

---

# 5. Professional Responsibility Test

> **Would a real professional represented by this Agent reasonably be responsible for performing this Task?**

Strong alignment: Agent `Senior Narrative Continuity Editor` / Task `Identify contradictions between a new scene and established character history`. Weak: same Agent / Task `Generate a WAV audio file from a text prompt` — requires audio-generation capability, not narrative-continuity expertise. Do not fix by making the Agent generic; correct the boundary.

---

# 6. Validation Layers

Layered, cheap deterministic checks before expensive semantic evaluation: Structural → Professional Alignment → Capability Alignment → Input/Output → Context → Failure → Permission → Scope → Efficiency → Traceability → Final Decision.

---

# 7. Structural Validation

Verify: Agent exists; Task exists; Process exists; Task references the correct Agent; Task references a valid Process; required Agent/Task config and fields exist; referenced resources exist; no broken references; no unintentional duplicate assignment; no Task silently unassigned; no required Agent unused without explanation.

```yaml
structural:
  agent_exists: true
  task_exists: true
  process_exists: true
  references_valid: true
  resources_valid: true
```

Structural validity does not imply semantic alignment.

---

# 8. Role Alignment

Role should be a recognizable professional identity. Strong: `Senior Character Development Editor` / evaluate character actions vs. established motivation. Weak: `AI Content Specialist` for the same Task — technically vague, no strong capability boundary. Prefer meaningful professional identity.

---

# 9. Domain Alignment

Agent domain must match Task domain. Aligned: `Narrative analysis` / `Narrative continuity`. Mismatch: `Audio engineering` / `Character motivation analysis` → decision `REFINE_AGENT` or `REASSIGN_TASK` depending on the broader architecture.

---

# 10. Specialization Alignment

Agent may be in the right general domain but lack the required specialization. `Senior Narrative Editor` / `Verify historical legal procedures in a nineteenth-century setting` may need historical/legal research. Solutions: 1) provide appropriate Knowledge, 2) provide an appropriate Skill, 3) introduce a specialized Agent, 4) split the Task if research is independently meaningful. Do not automatically broaden the Agent.

---

# 11. Seniority Alignment

Seniority should be sufficient, not inflated. Making final continuity judgments across a complex multi-season narrative may justify senior/expert. Avoid `World-Class Ultimate Expert`, `Master Genius`, `Universal Superintelligence` when unneeded.

> **Sufficient professional capability, not maximum capability.**

---

# 12. Goal Alignment

Goal is an enduring responsibility; the Task must be compatible. Aligned: Goal `Maintain narrative continuity, coherence, and consistency across the story` / Task `Check whether a generated chapter contradicts established character history`. Poor: Goal `Write compelling dialogue` / Task `Perform database schema migration`. Surface the mismatch, don't hide it.

---

# 13. Backstory Alignment

Backstory (experience, expertise, perspective, methodology, working style, values) should support Task performance but **must not smuggle Task instructions** into the Agent. `You are responsible for Task X. First read file Y. Then generate JSON. ...` are Task/implementation instructions. Distinguish `Professional identity ≠ Task instructions`.

---

# 14. Professional Perspective Alignment

Two Agents can share technical knowledge yet differ in perspective (`Narrative Editor`, `Character Psychologist`, `Historical Consultant`, `Game Designer`, `Legal Consultant`). Assign by the professional perspective the Process requires — especially for judgment, not deterministic transformation.

---

# 15. Task Purpose Alignment

Task purpose must fit the Agent's professional responsibility (`Task purpose → Agent professional responsibility`). Ask: 1) Is this a responsibility the Agent should perform? 2) Within its specialization? 3) Does it require a different profession? 4) Is the Task actually composite? 5) Is another Agent more appropriate?

---

# 16. Transformation Alignment

Validate the actual transformation. `Input: Generated scene + story bible → Transformation: Evaluate continuity → Output: Continuity findings`. The Agent must be capable of the semantic transformation; a matching title alone is insufficient.

---

# 17. Input Alignment

Assignment must provide what the Task needs: required inputs available; optional inputs correctly identified; input sources valid; format compatible; required Knowledge/Skills available; relevant state available; required previous outputs available; artifacts accessible. Do not compensate for missing inputs by injecting unrelated global context.

---

# 18. Output Alignment

Agent must be able to produce the Task's required output while satisfying `Task output contract → Agent capability → Output validation → Downstream consumer`.

```yaml
output:
  format: json
  schema:
    findings: []
    severity: ""
```

The Agent produces semantic content; deterministic validation checks structural correctness.

---

# 19. Knowledge Alignment

Attach Knowledge only when required. Aligned: Task checks chapter vs. world rules, required `World Bible`. Avoid attaching the whole project Knowledge base to every Agent. Check: Knowledge exists; relevant; not unnecessarily duplicated; scope appropriate; dynamic state is not stored as Knowledge.

---

# 20. Skill Alignment

Skills are repeatable methodologies/procedures. Aligned: Task `Perform structured narrative continuity analysis` / Skill `Narrative Continuity Evaluation Methodology`. Distinguish `Knowledge = reference information`, `Skill = methodology/procedure`, `Task = operation`. A Task should not duplicate a complete Skill unnecessarily.

---

# 21. Tool Alignment

Tools exist only when the Task requires an external/callable action. Aligned: `Retrieve a referenced document from a repository` / repository access tool. Not: `Analyze provided text for contradictions` / no external tool. Flag unnecessary tools — a capability and security concern.

---

# 22. MCP Alignment

When a capability is exposed through MCP, validate: required MCP capability exists; correct MCP server selected; required tool available; permissions sufficient; no unnecessary MCP tools exposed; external side effects understood. Do not introduce MCP when a deterministic or local capability suffices.

---

# 23. Reasoning Alignment

Enable reasoning when: multi-factor semantic judgment; evidence weighing; competing interpretations; explicit reasoning materially improves reliability. Not merely because the Agent is "smart."

> Does this Task require reasoning capability beyond ordinary execution?

---

# 24. Planning Alignment

Planning is for dynamically determining action sequence. If the sequence is known (`Flow: A → B → C`), planning may be unnecessary. If dynamic (`Determine which investigative actions are necessary based on the discovered evidence`), it may be justified. `Known workflow → Flow`; `Dynamic action selection → Planning`.

---

# 25. Memory Alignment

Memory only when the Task genuinely needs retained history beyond current context. `Use long-term historical interaction information to maintain continuity across independent sessions` may justify it; `Evaluate the current chapter against the supplied story bible` does not. Current information normally comes via context or Knowledge.

---

# 26. Context Alignment

Context must be what the Agent needs now: `Required → Relevant → Minimal → Task execution`. Avoid `Entire project state / story / Knowledge base / all previous outputs / all available tools` when a small subset suffices. Identify: missing, irrelevant, duplicated, oversized, stale context; incorrectly classified state; Knowledge injected as dynamic context.

---

# 27. State Alignment

State is current execution information, explicitly identified.

```yaml
state:
  current_chapter: "chapter_07"
  revision_number: 2
  approval_status: "pending"
```

Not to be confused with Knowledge, Memory, or Task context. Check the Task receives only the state it actually requires.

---

# 28. Failure Alignment

Agent and Task failure boundaries must be compatible: `Task failure domain → Agent responsibility → Retry boundary → Recovery boundary`. Ask: 1) Can the Agent meaningfully retry? 2) Is the failure semantic or technical? 3) Does it have enough info to recover? 4) Is a Task boundary at fault? 5) Is another professional capability required? A rejected artifact (e.g. chapter fails continuity) is a **VALID NEGATIVE RESULT**, not an Agent execution failure — don't mark the Agent failed for a rejected output.

---

# 29. Validation Alignment

Agent must be able to produce output satisfying the Task's validation (deterministic, semantic, or human). Example: Task `Produce structured continuity findings` — deterministic: JSON schema; semantic: are findings supported by evidence?; human: final editorial approval only. Don't give an Agent a validation standard belonging to another professional role unless the architecture requires it.

---

# 30. Permission Alignment

Permissions sufficient but minimal (`Task requirement → Required capability → Required permission → Granted permission`). Task `Read project documents` needs read, not delete/write/deploy. Mismatch classifications: `PERMISSION_MISSING`, `PERMISSION_EXCESSIVE`, `PERMISSION_CONFLICT`. Least privilege is part of correctness, not just deployment security.

---

# 31. Scope Validation

![Too Narrow] Agent `Character Name Validator` handling character-motivation analysis, character arcs, emotional continuity, relationship review → better boundary: `Senior Character Development Editor`.

![Too Broad] Agent `Senior Creative AI Specialist` with character analysis, legal research, audio engineering, database admin, game balancing, deployment → a God Agent. Solution is not a larger backstory; separate by meaningful professional boundaries.

---

# 32. Shared Agent Validation

Multiple Tasks may share an Agent when they share professional discipline, domain, specialization, perspective, capability/knowledge requirements, similar validation standards, and compatible failure boundaries/permissions. `Senior Narrative Continuity Editor`: T1 character continuity, T2 timeline continuity, T3 world-rule contradiction — a shared Agent is appropriate.

---

# 33. Agent Separation Validation

Separate Agents when Tasks differ meaningfully in discipline, specialization, expertise, perspective, permissions, capability requirements, validation criteria, failure domain, or human responsibility. `Senior Narrative Continuity Editor` vs `Senior Historical Consultant` is justified when professional responsibilities materially differ.

---

# 34. Do Not Fix Task Problems by Broadening the Agent

Critical rule. If `Agent ↔ Task` is misaligned, do not immediately make the Agent generic. Inspect: Is the Task composite? Is the Process boundary correct? Is another professional capability required? Is a Crew required? Is a Skill/Tool/Knowledge missing? Preferred correction order: `Correct Task boundary → Correct Process boundary → Correct Agent specialization → Add required supporting capability → Introduce additional Agent/Crew`. The exception depends on root cause.

---

# 35. Task Composite Detection

An apparent Agent mismatch may be a composite Task. `Research historical facts, write a scene, verify legal accuracy, generate an image, publish the result` contains several independent responsibilities. Consider `SPLIT_TASK` before `REFINE_AGENT`.

---

# 36. Crew Detection

If a single Process genuinely requires multiple professional perspectives, the answer may be a Crew. `Process: Evaluate historical authenticity of a screenplay` → `Flow → Crew {Historical Consultant, Narrative Editor, Cultural Consultant}`. Multiple Tasks alone do not justify a Crew; the reason must be genuine multi-specialist collaboration.

---

# 37. Token and Context Efficiency

Validate total prompt footprint: `Agent static config + Task instructions + examples + Knowledge + Skills + dynamic context + previous outputs + state + tool info + output schema`. A technically aligned relationship can still be inefficient. Identify duplicated instructions/identity, unnecessary backstory/context/Knowledge/skills/tools/examples, redundant output descriptions.

> **Minimum sufficient semantic and operational capability** — not simply minimum character count.

---

# 38. Alignment Severity

Findings carry explicit severity: `INFO` (optimization/observation, no correctness issue), `WARNING` (potential inefficiency/ambiguity), `ERROR` (incorrect but repairable), `BLOCKING` (cannot reliably satisfy architecture).

```yaml
severity: BLOCKING
category: DOMAIN_MISMATCH
```

---

# 39. Alignment Categories

`ROLE_MISMATCH`, `DOMAIN_MISMATCH`, `SPECIALIZATION_MISMATCH`, `SENIORITY_MISMATCH`, `GOAL_MISMATCH`, `BACKSTORY_MISMATCH`, `PERSPECTIVE_MISMATCH`, `SCOPE_TOO_NARROW`, `SCOPE_TOO_BROAD`, `TASK_COMPOSITE`, `PROCESS_MISMATCH`, `INPUT_MISMATCH`, `OUTPUT_MISMATCH`, `VALIDATION_MISMATCH`, `KNOWLEDGE_MISMATCH`, `SKILL_MISMATCH`, `TOOL_MISMATCH`, `MCP_MISMATCH`, `CAPABILITY_MISMATCH`, `REASONING_MISMATCH`, `PLANNING_MISMATCH`, `MEMORY_MISMATCH`, `CONTEXT_MISMATCH`, `STATE_MISMATCH`, `FAILURE_BOUNDARY_MISMATCH`, `PERMISSION_MISMATCH`, `TOKEN_OVERHEAD`, `CONTEXT_OVERHEAD`, `TRACEABILITY_MISMATCH`.

---

# 40. Validation Decisions

`ALIGNED`, `CONDITIONALLY_ALIGNED`, `REASSIGN_TASK`, `REFINE_AGENT`, `SPLIT_TASK`, `SPLIT_PROCESS`, `INTRODUCE_CREW`, `ADD_KNOWLEDGE`, `ADD_SKILL`, `ADD_TOOL`, `ADD_MCP`, `ADD_REASONING`, `ADD_PLANNING`, `ADD_MEMORY`, `REDUCE_CAPABILITY`, `REDUCE_CONTEXT`, `REDUCE_SCOPE`, `REJECT`. A decision should always include a rationale.

---

# 41. Root-Cause Principle

> **Fix the smallest architectural boundary that resolves the mismatch.**

Task needs a known methodology → add a Skill, don't create an Agent. Task combines research + narrative evaluation → Task is composite, don't broaden the Agent. Process needs three genuinely different perspectives → Crew, not one generic Agent.

---

# 42. Agent–Task Validation Schema

```yaml
agent_task_validation:
  agent_id: ""
  task_id: ""
  process_id: ""

  status: ""

  structural:
    agent_exists: false
    task_exists: false
    process_exists: false
    references_valid: false
    resources_valid: false

  alignment:
    role: ""
    domain: ""
    specialization: ""
    seniority: ""
    goal: ""
    backstory: ""
    perspective: ""

    purpose: ""
    transformation: ""

    input: ""
    output: ""
    validation: ""

    knowledge: ""
    skills: ""
    tools: ""
    mcp: ""

    reasoning: ""
    planning: ""
    memory: ""

    context: ""
    state: ""
    failure: ""
    permissions: ""

  scope:
    sufficient: false
    excessive: false
    too_narrow: false
    too_broad: false

  efficiency:
    prompt_footprint: ""
    context_efficiency: ""
    capability_minimality: ""
    findings: []

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

  traceability:
    requirements: []
    processes: []
    architecture_version: ""

  approved: false
```

---

# 43. Multi-Agent Validation

Must operate at the collection level, catching problems invisible in a single pair.

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
  duplicate_capabilities: []

  final_status: ""
```

---

# 44. Overloaded Agent Detection

An Agent is overloaded when assigned Tasks spanning unrelated professional responsibilities. `Senior Creative Production Specialist`: character psychology, historical research, SQL optimization, audio mastering, legal review.

```yaml
overloaded_agents:
  - agent_id: creative_specialist
    reason: "Tasks span unrelated professional disciplines."
```

Respond with decomposition, not a larger prompt.

---

# 45. Underused Agent Detection

An Agent may be unnecessarily specialized if it performs one trivial Task belonging to another Agent. `Agent B: Narrative Sentence Checker` for a grammar check, when `Agent A: Senior Narrative Editor` exists — if not an independent meaningful capability, Agent B may be unnecessary. Possible recommendations: `MERGE_AGENT`, `USE_DETERMINISTIC_VALIDATION`, `USE_EXISTING_AGENT`.

---

# 46. Uncovered Task Detection

Every executable Task needs an Agent or explicit execution mechanism (`Task → Agent`, or `Task → Deterministic Python`, or another selected capability). A Task with no valid execution capability is a blocking architecture issue.

---

# 47. Duplicate Capability Detection

Multiple Agents may represent the same capability (`Senior Narrative Editor`, `Expert Story Editor`, `Professional Narrative Reviewer` doing the same work). Compare role, specialization, goals, perspectives, Tasks, Knowledge, Skills, permissions, outputs. Possible results: `MERGE_AGENTS`, `REDEFINE_SPECIALIZATION`, `INTRODUCE_CLEAR_RESPONSIBILITY_BOUNDARIES`.

---

# 48. Agent–Task Matrix

| Task | Agent A | Agent B | Agent C |
|------|:-------:|:-------:|:-------:|
| Character continuity | ✓ | | |
| Timeline continuity | ✓ | | |
| Historical verification | | ✓ | |
| Audio validation | | | ✓ |

Makes visible: uncovered Tasks, overloaded Agents, duplicate assignments, unnecessary Agents, ambiguous ownership, specialization gaps.

---

# 49. Validation Sequence

1 Validate references → 2 Agent identity → 3 Task atomicity → 4 professional responsibility → 5 domain/specialization → 6 Agent goal/perspective → 7 Task transformation → 8 inputs → 9 outputs → 10 Knowledge/Skills → 11 Tools/MCP → 12 Reasoning/Planning/Memory → 13 context/state → 14 failure boundary → 15 permissions → 16 Agent scope → 17 efficiency → 18 traceability → 19 produce findings → 20 produce decision.

---

# 50. Deterministic vs Semantic Validation

Use deterministic wherever possible.

**Deterministic** examples: Agent reference exists; Task reference exists; Process reference exists; required fields exist; required Knowledge resource exists; tool reference exists; output schema valid; Task has one assigned Agent; no duplicate IDs; permissions structurally valid; required inputs declared.

**Semantic** examples: Agent professionally appropriate; specialization matches; Task belongs to the Agent's responsibility; Agent scope too broad; backstory supports role; context genuinely relevant; two Agents overlap meaningfully; Task semantically composite.

Use semantic evaluation only where deterministic cannot establish correctness.

---

# 51. Human Review

Required for subjective or high-impact decisions: final creative role boundaries, sensitive professional responsibility, high-impact approvals, ambiguous organizational ownership, security-sensitive permissions. Human review must produce an explicit decision.

```yaml
human_review:
  required: true
  decision: "APPROVE"
  notes: []
```

Do not silently treat absence of human review as approval.

---

# 52. Correction Rules

The validator identifies problems; it must not silently modify the architecture. Flow: `Validation → Finding → Recommendation → Human/Architecture Decision → Correction → Revalidation`.

```yaml
finding:
  severity: ERROR
  category: SPECIALIZATION_MISMATCH
  message: "Task requires historical research expertise."
  recommendation: "Assign to a historical consultant or split the research responsibility."
```

---

# 53. Revalidation After Correction

Any meaningful correction triggers revalidation. Agent changed → revalidate Agent, Agent–Task alignment, affected Tasks, Crew if applicable. Task split → validate new Tasks, Agent assignments, revalidate Process contract. New Agent introduced → validate Agent, all assignments, Crew architecture. Architecture validation remains the final gate.

---

# 54. Example: Valid Assignment

```yaml
agent:
  id: continuity_editor
  role: Senior Narrative Continuity Editor
  goal: Maintain narrative continuity and consistency across the story.
  backstory: >
    An experienced narrative editor specializing in long-form
    serialized storytelling and continuity management.

task:
  id: evaluate_character_continuity
  purpose: >
    Evaluate whether the generated chapter is consistent with
    established character history and motivation.
  output:
    format: json
    schema:
      findings: []
      status: ""

validation:
  decision:
    status: ALIGNED
    action: ""
  approved: true
```

Why: Professional responsibility → narrative continuity; Task responsibility → character continuity evaluation. Strong alignment.

---

# 55. Example: Task Too Broad

Agent `Senior Narrative Continuity Editor` with a Task that reads the source, researches historical facts, writes the chapter, generates images, evaluates continuity, creates audio, publishes the episode → should not be approved. Findings: `TASK_COMPOSITE`, `SCOPE_TOO_BROAD`, `CAPABILITY_MISMATCH`, `FAILURE_BOUNDARY_MISMATCH`. Possible architecture: separate Research, Writing, Continuity Evaluation, Image Generation, Audio, Publishing Processes — each receiving the appropriate implementation mechanism.

---

# 56. Example: Missing Skill Rather Than New Agent

Agent `Senior Narrative Editor`, Task `Perform structured three-act narrative analysis` — correct identity, but the methodology isn't available. Add `Skill: Three-Act Narrative Analysis Methodology` instead of creating another Agent.

---

# 57. Example: Missing Knowledge Rather Than Agent

Agent `Senior Narrative Continuity Editor`, Task `Verify that the chapter respects established world rules` — correct capability, but world rules unavailable. Add `Knowledge: World Bible`. Do not create another Agent for missing reference information.

---

# 58. Example: Crew Required

Process `Evaluate historical authenticity of a screenplay` with Tasks: historical accuracy, narrative integration, cultural authenticity evaluation. If these need genuinely different professional perspectives → `Crew {Senior Historical Consultant, Senior Narrative Editor, Cultural Authenticity Consultant}`. The Crew exists for professional collaboration, not because there are multiple Tasks.

---

# 59. Quality Criteria

A high-quality assignment has: clear professional responsibility AND clear Task purpose AND sufficient specialization AND sufficient capabilities AND sufficient inputs AND compatible outputs AND meaningful validation AND coherent failure boundaries AND appropriate permissions AND minimal relevant context AND appropriate Agent scope AND no unnecessary attached capability AND preserved traceability.

---

# 60. Final Validation Rule

Approve the relationship only when: Agent is the correct professional capability + Task is a coherent bounded responsibility + Agent capabilities sufficient + capabilities minimal + inputs sufficient + outputs satisfy the contract + failure boundaries compatible + permissions appropriate + context relevant and minimal + assignment traceable to the Process.

> **Do not make the Agent generic to fit the Task. Make the Agent and Task boundaries correct.**

And:

> **If an Agent–Task mismatch appears, identify the smallest architectural boundary responsible for the mismatch and correct that boundary rather than compensating with a larger prompt or broader Agent.**