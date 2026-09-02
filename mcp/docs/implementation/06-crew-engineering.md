# Amsha Crew Engineering

## Purpose

Defines how Amsha determines when and how to engineer a **CrewAI Crew** from an already-validated architecture. A Crew is not simply a collection of Agents; it is a **meaningful multi-specialist collaboration boundary** in which multiple professional capabilities work together to complete a Process or a bounded set of related work.

> **Use a Crew when a Process genuinely requires collaboration between multiple professional capabilities. Do not use a Crew merely because the work is large, complex, or contains multiple Tasks.**

---

# 1. Position in the Amsha Architecture

Crew engineering occurs after Process, Flow, capability, Agent, Task, atomicity, and Agent–Task validation, before Crew Validation and Implementation. Preceding chain: Problem → Goal & Boundary → Process Decomposition → Process Contracts → Process Validation → Flow & State → Failure Planning → Capability Selection → Architecture Validation → Agent Engineering → Task Engineering → Atomic Task Validation → Agent–Task Validation → **Crew Engineering** → Crew Validation → Implementation.

Crew engineering must preserve the already-validated architecture and must not silently introduce new professional responsibilities, Tasks, Processes, or capabilities.

---

# 2. Core Definition

> **A bounded collaboration of multiple professional Agents whose combined capabilities are required to satisfy a meaningful Process or execution requirement.**

Chain: `Process Requirement → Multiple Professional Responsibilities → Multiple Agents → Collaboration Contract → Crew`. The condition is `Multiple Agents AND Meaningful collaboration requirement`, not simply multiple Agents.

---

# 3. Crew vs Agent

`Agent = who performs a professional responsibility`; `Crew = how multiple professional responsibilities collaborate to complete a bounded piece of work`. Example Crew `Narrative Quality Review` with `Senior Narrative Editor`, `Senior Character Development Editor`, `Senior Continuity Editor` — justified when the Process requires these perspectives to interact or contribute jointly.

---

# 4. Crew vs Process

`Process = what meaningful transformation must happen`; `Crew = which professional capabilities collaborate to perform it`. Chain: `Process → Capability analysis → Crew decision → Crew`. A Process should never be defined merely as "Run a Crew"; it must exist independently of CrewAI terminology.

---

# 5. Crew vs Flow

`Flow = orchestration and execution control`; `Crew = professional collaboration`. Flow controls execution order, transitions, conditions, iterations, state, parallelism, human gates, recovery. Crew handles specialist collaboration, delegation where appropriate, multi-Agent execution, collaborative completion of a bounded objective. They can be combined: a Flow runs `Process A → Python`, `Process B → Crew {Agent A, Agent B, Agent C}`, `Process C → Python`. Flow stays responsible for orchestration; Crew for collaboration.

---

# 6. When a Crew Is Justified

Consider a Crew when one or more hold: 1) Process requires multiple distinct professional disciplines; 2) different professional perspectives must contribute to the same outcome; 3) specialist outputs must be combined into a shared result; 4) one specialist's output materially informs another; 5) delegation between professional roles is required work; 6) the Process cannot be reliably performed by one sufficient Agent; 7) collaboration materially improves correctness/quality; 8) different professional validation responsibilities must be represented; 9) the architecture explicitly requires multi-specialist judgment. Example: `Evaluate screenplay historical authenticity` needs historical, narrative, and cultural expertise → a Crew may be appropriate.

---

# 7. When a Crew Is Not Justified

Do not create a Crew merely because: the Process has many steps; the Task is long; the output is large; the workflow is complicated; multiple Python functions or LLM calls are required; one Agent has multiple Tasks; the project is large; parallel execution exists; the implementation has multiple components. Example: `Generate a chapter` (Draft, Format, Validate JSON) does not need a Crew — use `Agent → Draft Task → Python validation → Formatting`. Use the least powerful mechanism that reliably satisfies the Process.

---

# 8. Crew Decision Test

> **Would the Process materially require more than one professional capability to achieve its intended outcome?**

No → do not create a Crew; use one Agent or deterministic mechanism. Yes → are responsibilities meaningfully distinct? Yes → do they need collaboration within the same bounded Process? Yes → Crew is justified. If specialists operate independently and are later coordinated by a Flow, a Crew may not be necessary.

---

# 9. Crew Decision Tree

`Is the Process deterministic?` Yes → use Python/deterministic. No → `Does one professional capability suffice?` Yes → one Agent. No → `Are multiple professional capabilities required?` No → reconsider Task/Process boundary. Yes → `Do they need meaningful collaboration?` No → separate Agents controlled by Flow. Yes → **Crew**.

---

# 10. Crew as a Collaboration Boundary

The Crew should answer: **What collaborative outcome is this group responsible for producing?** Good: Crew `Screenplay Quality Review`, purpose "Produce a consolidated quality assessment using narrative, character, and continuity expertise." Poor: `All Story Agents`. A Crew must not become a container for unrelated Agents.

---

# 11. Crew Purpose

One meaningful collaborative purpose. Good: "Review a screenplay for narrative, character, and continuity quality and produce a consolidated review." Poor: "Do everything required for the project." The purpose stays bounded even when internal collaboration is complex.

---

# 12. Crew Scope

Scope derives from the Process boundary (`Process boundary → Crew boundary`). The Crew should not absorb unrelated Processes, project phases, operational responsibilities, or global workflow orchestration. Good: `Evaluate Chapter → Chapter Evaluation Crew {Narrative, Character, Continuity Editor}`. Poor: `Production Crew {Writer, Historian, Image Generator, Audio Engineer, DBA, Deployment Engineer, Publisher}` — a project-wide God Crew.

---

# 13. Crew Agent Composition

Every Agent must have a justified professional responsibility. For each ask: **What unique professional capability does this Agent contribute to the Crew?** Each Agent in `Narrative Evaluation` (structure/pacing/coherence; character motivation/arc/behavior; continuity vs. story facts) has a meaningful contribution.

---

# 14. Agent Duplication

Do not include Agents providing essentially the same capability without justification. Poor: `Narrative Expert`, `Senior Narrative Expert`, `Master Narrative Expert`, `Advanced Story Expert` with identical responsibilities → unnecessary duplication. Correction: `MERGE_AGENTS` or define meaningful specialization.

---

# 15. Agent Diversity

Diversity comes from professional responsibility, not artificial personality. Do not split Agents merely for different writing styles, names, tones, prompts, or LLM temperatures. Meaningful distinctions: discipline, specialization, expertise, professional perspective, validation responsibility, permission boundary, capability requirement.

---

# 16. Crew Collaboration Models

**16.1 Sequential Specialist** — `Agent A → Agent B → Agent C → Consolidated Result`; use when each specialist depends on the previous output (Research → Historical Review → Narrative Integration).

**16.2 Parallel Specialist Review** — `Input → {Agent A, Agent B, Agent C} → Consolidation`; use when specialists independently evaluate the same input (Chapter → Character/Continuity/Pacing evaluation → consolidated review).

**16.3 Specialist + Synthesizer** — `{Agent A, B, C} → Synthesizer Agent`; use when findings must be combined into one coherent result. The synthesizer must have a meaningful responsibility, not merely exist because there are multiple Agents.

**16.4 Delegated Collaboration** — `Lead Agent delegates → {Specialist A, B, C}`; use only when delegation is genuinely part of the Process. Never to look sophisticated.

---

# 17. Collaboration vs Orchestration

`Flow: "Agent B runs after Agent A"` (execution control) vs `Crew: "Agent B's professional contribution is part of the collaborative solution"`. If primarily execution control, prefer Flow; if professional collaboration, Crew may be appropriate.

---

# 18. Crew Inputs

Explicitly define inputs:

```yaml
inputs:
  required:
    - chapter_text
    - story_bible
  optional:
    - previous_review
```

Do not automatically pass all Flow state or Knowledge into every Agent; receive the minimum needed to accomplish the Process.

---

# 19. Crew Outputs

Produce a meaningful Process-level output:

```yaml
output:
  name: chapter_quality_review
  format: json
  schema:
    overall_status: ""
    findings: []
    recommendations: []
```

Output should satisfy the Process contract, not merely be a raw collection of Agent responses unless the Process explicitly requires it.

---

# 20. Crew-Level Output Contract

Define: output name, format, schema, required fields, semantic expectations, completion condition, validation requirements, downstream consumers. Chain: `Agent outputs → Collaboration → Crew output → Process output contract → Downstream Process`.

---

# 21. Agent Output vs Crew Output

Different levels: individual Agent outputs (character/continuity/pacing findings) support collaboration; the Crew output (consolidated chapter quality assessment) satisfies the Process-level collaborative contract.

---

# 22. Crew Context

Carefully controlled. Relevant: Process input, required Knowledge, relevant Skills, prior specialist outputs, Flow state, relevant artifacts, decisions, previous evaluation results. Do not give every Agent every other Agent's output automatically; use only the context the collaboration pattern requires.

---

# 23. Context Isolation

Professional boundaries are useful. `Historical Consultant → historical evidence`; `Narrative Editor → narrative analysis`; `Synthesizer → relevant outputs from both`. The Historical Consultant may not need the Narrative Editor's entire context. Minimal context improves relevance, token efficiency, reasoning clarity, privacy, reproducibility.

---

# 24. Knowledge at Crew Level

Attach Knowledge at the smallest useful scope: `Crew | Agent | Task`. Crew-level when all participants genuinely need the same reference; Agent-level when only one specialist needs it. Avoid duplicating large Knowledge resources across every Agent.

---

# 25. Skills at Crew Level

Skills represent methodologies for one or more participants. Shared: `Narrative Evaluation` / `Structured Narrative Evaluation Framework`. When only one Agent needs a methodology (Historical Consultant / Historical Source Evaluation Skill), scope it there. Do not attach every Skill globally.

---

# 26. Tools and MCP

Scope to the Agent that needs them: `Historical Consultant → Research Tool`; `Narrative Editor → no external tool`. Avoid `Every Agent → all available tools`. Crew-level capability exposure stays minimal and explicit.

---

# 27. Reasoning and Planning

Justify at the smallest appropriate level. A Crew does not automatically require `reasoning = true, planning = true`. A specialist may need reasoning while another does not; a Lead Agent may need dynamic planning while others execute bounded Tasks. Capability selection remains requirement-driven.

---

# 28. Memory

Crew-level Memory only when collaboration genuinely requires retained history: repeated collaborative sessions, long-running projects, persistent team decisions, historical collaboration context. Do not substitute Memory for Flow state, current Task context, Knowledge, or previous Task outputs.

---

# 29. Flow State and Crew State

Flow owns workflow state; Crew consumes the relevant projection (`Flow State → Relevant Crew Context → Agents`). The Crew should not become an alternative workflow-state manager unless explicitly required. A Crew needing `chapter_id, revision, chapter content, relevant review context` does not need unrelated Flow state.

---

# 30. Crew Collaboration Contract

Define how Agents interact:

```yaml
collaboration:
  model: ""
  participants: []
  dependencies: []
  shared_inputs: []
  intermediate_outputs: []
  synthesis: ""
```

Models: `sequential`, `parallel`, `delegated`, `specialist_synthesis`, `review_and_reconcile`. The model reflects the actual Process requirement.

---

# 31. Crew Completion

Explicitly defined. Execution completion ("all required Agents completed") is not necessarily Process success. If all reviewers complete but the consolidated review fails schema validation, the Crew executed but did not successfully complete its Process contract. `Crew execution completion ≠ Crew success`.

---

# 32. Crew Validation

Validate at the Process boundary. **Deterministic**: schema validation, required fields, Agent references, output presence, dependency correctness, duplicate outputs, state validity. **Semantic**: quality of synthesis, consistency between findings, evidence support, professional coherence. **Human**: final editorial approval, high-impact judgment, unresolved specialist disagreement. Use deterministic first.

---

# 33. Specialist Disagreement

Treat disagreement as an explicit outcome when meaningful.

```yaml
disagreement:
  detected: true
  areas:
    - topic: character_motivation
      positions:
        - agent: character_editor
          conclusion: "consistent"
        - agent: continuity_editor
          conclusion: "inconsistent"
```

Responses: `SYNTHESIZE`, `RECONCILE`, `REQUEST_MORE_EVIDENCE`, `ESCALATE_TO_HUMAN`. Do not silently discard disagreement.

---

# 34. Crew Failure Boundaries

Distinguish `Agent failure → Task failure → Crew failure → Process failure`. A single Agent failure does not force the whole Crew to fail. With three independent reviewers where Agent B fails retryably, retry Agent B without restarting the Crew. But if Agent B provides an essential capability, the Crew may need to fail or escalate. Contain failure at the smallest safe boundary.

---

# 35. Retry vs Collaboration Iteration

`Retry` = recovering from an execution failure (Agent call failed → Retry). `Collaboration iteration` = deliberately repeating work for improvement or another evaluation cycle (Review result = NEEDS_REVISION → Writer revises → Review again) — a Process/Flow iteration. Do not confuse them.

---

# 36. Crew Side Effects

If a Crew or Agent performs external side effects (create file, send message, modify database, publish content, deploy artifact), the architecture must define ownership, authorization, idempotency, retry behavior, failure handling, audit requirements. Do not grant a Crew broad side-effect permissions just because it contains multiple Agents.

---

# 37. Crew Parallelism

Parallel specialist execution appropriate when: inputs available; specialists logically independent; they don't mutate shared state unsafely; outputs merge safely; downstream waits for required outputs. `Chapter → {Character, Continuity, Pacing Review} → Synthesis`. Parallelism is an architectural property, not merely an optimization.

---

# 38. Crew Sequential Dependencies

Sequential collaboration when later work depends on earlier work (`Historical Research → Historical Interpretation → Narrative Integration`). Do not make independent work sequential merely because the Agents share a Crew.

---

# 39. Crew Synthesis

When multiple specialist outputs must become one Process output, synthesis must be explicit (`Specialist outputs → Synthesis responsibility → Consolidated result`). The synthesizer may be an existing specialist, a dedicated specialist, deterministic Python, Flow logic, or another explicit mechanism. Do not automatically create a "Synthesizer Agent"; if deterministic merging suffices, use deterministic code.

---

# 40. Crew and Deterministic Processing

A Crew should not do work Python reliably performs. `Agent outputs {score 8, 7, 9}` — averaging is deterministic Python, not semantic judgment. Agents judge; Python aggregates. Preserves reliability, cost, reproducibility, token efficiency.

---

# 41. Crew Resource Minimality

For every Crew, evaluate Agents, Knowledge, Skills, Tools, MCP, Reasoning, Planning, Memory, Context. Each resource needs a reason.

```yaml
resource:
  type: tool
  name: repository_reader
  used_by:
    - historical_consultant
  reason: "Retrieve referenced historical source."
```

Remove unused resources.

---

# 42. Crew Token Efficiency

Crews can create significant token overhead: multiple Agent prompts + repeated Knowledge + repeated context + Agent outputs + delegation messages + synthesis context + tool/MCP schemas. Evaluate whether collaboration provides enough value to justify the cost. The question is not "Can multiple Agents improve this?" but **Does the additional professional capability provide enough value to justify the additional execution and context cost?**

---

# 43. Crew Cost Evaluation

Consider LLM calls, context size, Agent/Task counts, tool/MCP calls, latency, retries, iterations, synthesis overhead, memory and Knowledge retrieval. Prefer a simpler architecture when quality and reliability remain sufficient.

---

# 44. Crew Scope Anti-Patterns

- **God Crew** — one Crew handles the entire application.
- **Decorative Crew** — exists only because CrewAI is being used.
- **Crew for Sequential Flow** — Agents exist only to execute A → B → C; if no collaboration, Flow is more appropriate.
- **Agent Collection** — multiple unrelated Agents in one Crew.
- **Capability Dump** — every Agent gets every Tool, Knowledge, Skill, Memory source, MCP server.
- **Infinite Collaboration** — Agents discuss without a bounded completion condition.
- **Hidden Workflow** — Crew internally performs unrelated Processes the Flow should represent explicitly.

---

# 45. Crew Implementation Specification

Produce an implementation-neutral Crew spec before generating code:

```yaml
crew:
  id: chapter_quality_review
  process_id: evaluate_chapter
  purpose: >
    Produce a consolidated quality assessment of a chapter
    using narrative, character, and continuity expertise.

  inputs:
    required:
      - chapter
      - story_bible
    optional:
      - previous_review

  agents:
    - id: narrative_editor
      responsibility: >
        Evaluate narrative structure, pacing, and coherence.

    - id: character_editor
      responsibility: >
        Evaluate character motivation, behavior, and arc consistency.

    - id: continuity_editor
      responsibility: >
        Evaluate consistency with established story facts.

  collaboration:
    model: parallel_then_synthesis
    shared_inputs:
      - chapter
      - story_bible

  output:
    name: chapter_quality_review
    format: json
    schema: {}

  validation:
    deterministic: []
    semantic: []
    human: false

  failure:
    retryable: true
    max_attempts: 2
    outcomes: []

  traceability:
    process_id: evaluate_chapter
    requirements: []
```

This spec must exist before CrewAI code is generated.

---

# 46. Crew Validation Schema

```yaml
crew_validation:
  crew_id: ""
  process_id: ""

  status: ""

  purpose:
    valid: false
    clear: ""
    bounded: false

  composition:
    agents: []
    agent_count: 0
    professional_diversity: ""
    duplication: []
    missing_capabilities: []

  collaboration:
    required: false
    model: ""
    dependencies: []
    collaboration_value: ""

  inputs:
    required_complete: false
    minimal: false
    findings: []

  outputs:
    contract_defined: false
    structured: false
    schema_valid: false
    process_compatible: false

  resources:
    knowledge: []
    skills: []
    tools: []
    mcp: []
    reasoning: false
    planning: false
    memory: false
    unnecessary: []

  context:
    relevant: false
    minimal: false
    isolation: ""
    findings: []

  execution:
    parallelism: ""
    sequencing: ""
    synthesis: ""
    state_dependencies: []

  failure:
    defined: false
    retry_safe: false
    containment: ""
    recovery: ""

  efficiency:
    token_footprint: ""
    runtime_cost: ""
    latency: ""
    capability_minimality: ""

  security:
    permissions: []
    excessive_permissions: []
    findings: []

  traceability:
    process_id: ""
    requirements: []
    architecture_version: ""

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

# 47. Crew-Level Decision Categories

`APPROVED`, `CONDITIONALLY_APPROVED`, `REMOVE_CREW`, `USE_SINGLE_AGENT`, `REFINE_CREW_SCOPE`, `REFINE_AGENT_SCOPE`, `ADD_AGENT`, `REMOVE_AGENT`, `MERGE_AGENTS`, `SPLIT_AGENT`, `CHANGE_COLLABORATION_MODEL`, `USE_FLOW_INSTEAD`, `USE_DETERMINISTIC_PROCESSING`, `ADD_KNOWLEDGE`, `ADD_SKILL`, `ADD_TOOL`, `ADD_MCP`, `REDUCE_CONTEXT`, `REDUCE_CAPABILITY`, `REDUCE_AGENT_COUNT`, `REJECT`.

---

# 48. Crew Engineering Checklist

**Purpose:** [ ] one bounded collaborative purpose; [ ] maps to a validated Process; [ ] does not absorb unrelated Processes.

**Collaboration:** [ ] multiple professional capabilities genuinely required; [ ] provides architectural value; [ ] model explicit; [ ] not merely sequential orchestration.

**Agents:** [ ] every Agent has justified responsibility; [ ] Agent–Task aligned; [ ] no unnecessary duplicates; [ ] no missing required capability; [ ] no Agent unnecessarily broad.

**Tasks:** [ ] atomic; [ ] map to appropriate Agents; [ ] outputs compatible; [ ] boundaries meaningful.

**Inputs/Context:** [ ] required inputs exist; [ ] context relevant; [ ] context minimal; [ ] large artifacts referenced appropriately; [ ] Flow state not confused with Knowledge/Memory.

**Resources:** [ ] Knowledge/Skills/Tools/MCP/Reasoning/Planning/Memory each justified.

**Execution:** [ ] dependencies explicit; [ ] parallelism safe; [ ] sequencing meaningful; [ ] synthesis explicit; [ ] completion defined.

**Failure:** [ ] Agent failure boundaries understood; [ ] Crew failure conditions defined; [ ] retries bounded; [ ] external side effects retry-safe; [ ] recovery boundaries explicit.

**Security:** [ ] permissions sufficient; [ ] permissions minimal; [ ] external capabilities scoped.

**Efficiency:** [ ] Crew adds enough value to justify cost; [ ] context not unnecessarily duplicated; [ ] Agents don't receive unnecessary resources; [ ] deterministic work not delegated to LLM Agents unnecessarily.

**Traceability:** [ ] Crew maps to a Process; [ ] Agents map to Tasks; [ ] Tasks map to requirements; [ ] architecture version recorded.

---

# 49. Example: No Crew Required

`Generate chapter draft` — one professional writer suffices. Architecture: `Flow → Senior Narrative Writer → Generate Chapter Task → Python schema validation`. A Crew would add complexity without meaningful collaboration. Decision: `USE_SINGLE_AGENT`.

---

# 50. Example: Crew Required

`Evaluate chapter quality` requires narrative structure, character development, and continuity perspectives. Architecture: `Flow → Chapter Evaluation Crew {Senior Narrative Editor, Senior Character Development Editor, Senior Continuity Editor} → Consolidated Review → Flow`. Justified because multiple professional perspectives contribute to one bounded collaborative outcome.

---

# 51. Example: Flow Instead of Crew

Research source → Generate draft → Validate draft → Publish artifact — separate Processes with different capabilities; no team collaboration on one bounded outcome. Better: `Flow {Research Agent, Writing Agent, Python Validation, Publishing Tool}` than one large Crew.

---

# 52. Example: Crew + Flow

A complex workflow may legitimately combine both: `Flow → Analyze Source → Agent`; `→ Evaluate Draft → Crew {Narrative, Character, Continuity Editor}`; `→ Revision → Agent`; `→ Approval → Human Gate`. Often preferable to putting the whole workflow in one Crew. Flow controls the lifecycle; Crew handles the collaborative Process.

---

# 53. Architecture Rule for Crew Creation

Decision hierarchy: Can deterministic processing solve it → use it. No → can one professional Agent → use one. No → are multiple capabilities required? No → reconsider Process/Task boundaries. Yes → do they need meaningful collaboration within the same bounded Process? No → separate capabilities with Flow orchestration. Yes → **Create Crew**.

---

# 54. Final Principle

Never begin with "How many Agents should this Crew contain?" Begin with **"What professional collaboration does this Process actually require?"** Then determine: `Process → Professional responsibilities → Agents → Collaboration requirement → Crew → Tasks → Inputs/Context/Resources → Output contract → Failure and recovery → Validation`.

> **A Crew is not a container for complexity. It is a bounded professional collaboration mechanism.**

And:

> **Use a Crew only when multiple professional capabilities must meaningfully collaborate to satisfy a Process; otherwise use the simpler mechanism that reliably satisfies the architecture.**