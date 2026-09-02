# Crew-Flow Architecture

## Purpose

Defines how Amsha combines Crews and Flows when a workflow needs both explicit orchestration and multi-specialist collaboration.

```text
Flow = controls execution
Crew = performs collaborative professional work
```

> **Use Flow to control the lifecycle of work and Crew to perform bounded multi-specialist collaboration within that lifecycle.** They should never compete for the same responsibility.

Simply placing a Crew inside a Flow doesn't automatically produce a sound architecture. Amsha must decide: which responsibilities belong to Flow vs Crew, which state belongs to Flow vs which context belongs to Crew, which decisions are deterministic vs need professional judgment, where collaboration begins/ends, where failure/recovery/iteration/human-decision boundaries sit, what the Crew returns to the Flow, and what conditions drive the Flow to continue/branch/retry/recover/terminate.

## Core Architecture & Separation

```text
Flow
 ├── Process A
 ├── Process B → Crew → Agent A/Task A, Agent B/Task B, Agent C/Task C
 ├── Decision
 └── Process C
```
Flow owns: lifecycle, state, transitions, routing, iteration, parallelism, human gates, recovery, termination.
Crew owns: collaboration, specialist responsibilities, Agent coordination, Task execution, specialist outputs, synthesis, collaborative result.
**Neither should silently absorb the other's responsibilities.**

**Flow = control plane** (what executes, when, which transition follows, whether iteration/approval/recovery/termination happens) — it should not reason about the Crew's internal professional judgment.

**Crew = collaboration plane** (which specialists participate, how their work relates, how outputs combine, how disagreement is handled) — it should not become the application's global workflow controller.

**Process is the bridge**: `Flow → Process → Crew → Agents/Tasks → Process Output → Flow`. Full responsibility hierarchy: `Requirement → Goal → Process → [Flow: Execution Control] → [Crew: Professional Collaboration] → [Agent: Professional Capability] → [Task: Bounded Operation]`, supported by Python/Tools/MCP/Knowledge/Skills/Memory/Reasoning/Planning/Human Review/Checkpointing/Observability.

## When to Combine Them

**Flow + Crew justified** when both: (1) the workflow needs explicit orchestration, AND (2) at least one bounded Process needs genuine multi-specialist collaboration. E.g. Generate→Evaluate(Crew: Narrative/Character/Continuity)→Decision→{Approved | Revise→Evaluate again} — Flow manages generation/evaluation lifecycle/revision loop/termination, Crew manages specialist evaluation.

**Flow alone is better** if no meaningful collaboration is needed — e.g. `Flow: Research → Writing → Validation → Publishing` beats one giant Crew holding every Agent. Don't create a Crew just because multiple Agents exist.

**Crew alone may suffice** if a bounded Process needs collaboration but has no meaningful external lifecycle (no branching/iteration/human gates/workflow state/recovery/checkpointing needed) — `Input → Crew → Output` standalone. Use the simplest architecture that satisfies requirements.

## The Boundary Contract

The Flow tells the Crew "run chapter evaluation" (a Process input contract); the Crew tells the Flow "evaluation = NEEDS_REVISION" (a structured result), not internal orchestration detail like "Narrative Agent should critique motivation, then ask Continuity to check timeline..." — that belongs inside the Crew's own collaboration model unless it's itself the point.

**Crew entry contract** — Flow gives the Crew an explicit input, never arbitrary global state:
```yaml
crew_entry: { process_id: evaluate_chapter, inputs: { required: [chapter, story_bible], optional: [previous_review] }, state: [revision_number], artifacts: [chapter_reference] }
```
**Crew exit contract** — structured result the Flow can route on deterministically:
```yaml
crew_result: { process_id: evaluate_chapter, status: "NEEDS_REVISION", output: { review_reference: "reviews/chapter_07.json" }, findings: { count: 4 }, next_action: { recommended: "REVISE" } }
```

**Crew output ≠ Flow state**: a Crew may produce a 40-page evaluation with 150 findings; the Flow only needs `evaluation_status = NEEDS_REVISION` + a reference. Prefer artifact-oriented flow: `Crew → Large Artifact → Artifact Store → Reference → Flow State`.

**State ownership**: Flow owns workflow state; Crew results update it only through an explicit contract (`Crew → Process Result → Flow State Update → Transition`) — avoid unrestricted Agent mutation of global state. Crew-internal execution info (Agent/Task status, intermediate outputs, collaboration/synthesis state, specialist findings) stays internal; only the relevant result crosses into Flow state.

## Context, Knowledge, Skill, Tool/MCP Boundaries

Flow provides Process inputs, relevant state, artifact references, required context. The Crew builds its own Agent-specific context, Task-specific context, specialist Knowledge, relevant Skills — the Flow should not build every Agent's prompt.

Attach Knowledge and Skills at the smallest useful scope (Narrative Editor gets Narrative Knowledge; Continuity Editor gets the Story Bible) rather than injecting everything into every Agent. Tools/MCP normally live inside the Process/Crew/Agent boundary — the Flow controls *when* the Process runs, the specialist consumes the external capability.

## Decision Boundaries

**Deterministic**: if Crew returns `status: APPROVED`, the Flow routes on it directly (`status == APPROVED → Approval`) — don't add another Agent just to interpret a structured status.

**Semantic**: if the Crew itself must judge something ("does this need structural or character revision?"), it returns a structured decision (`{ type: revision_type, value: character_revision, confidence: 0.86, rationale_reference }`) and the Flow transitions on that value. The judgment belongs to the Crew; the transition belongs to the Flow.

## Iteration & Failure Across the Boundary

**Iteration**: `Generate → Crew Evaluation → Decision → {PASS→Continue | REVISE→Revision→Crew Evaluation}`. The Flow owns the loop and its counter/limit (`revision_number < revision_limit`); the Crew doesn't independently control the global iteration count.

**Failure propagation is explicit and distinct at each level**: Agent failure → Task failure → Crew failure → Process failure → Flow failure — a failure should propagate only as far as necessary (e.g. a Continuity Agent failing and being retried successfully never becomes a Flow failure). `Crew failure → {Retry Crew | Retry failed Agent | Recover | Escalate | Terminate Flow}` per the validated failure architecture.

**Partial Crew failure**: if a mandatory specialist fails, `Crew = FAILED`; if an optional one fails and degraded execution is authorized, `Crew = PARTIAL` — the architecture must explicitly say which is true.

**Retry scope**: minimize it — retry the failed MCP request or repair the bad synthesis, don't restart the entire Flow or unrelated Processes.

**Human gates belong to the Flow, not the Crew** — `Generate → Evaluation Crew → Human Review → {APPROVE|REVISE|REJECT|ESCALATE}`. Never bury "ask the user for approval" inside an Agent; keep the approval state explicit and observable.

## Structural Patterns

**Parallel independent Crews** are fine when Processes are independent — no need to nest them inside one larger Crew:
```text
Input → { Narrative Review Crew | Character Review Crew | Continuity Review Crew } → Merge
```
**Mixed-mechanism parallel branches** are fine too — each Process keeps its own implementation (Crew, Python, another Crew).

**Avoid unnecessary nested Crews** (`Crew A → Crew B → Crew C`) — this obscures responsibility and complicates failure/context/state propagation. Prefer `Flow → { Crew A, Crew B, Crew C }` or one bounded Crew, unless multiple genuine collaboration levels are required with explicit boundaries.

**Preferred mental model**: `Process → implementation = Crew` (not `Flow → implementation = giant Crew`), which preserves architecture instead of hiding workflow boundaries. Recommended pattern:
```text
FLOW
 ├── Process: Analyze Source (Agent)
 ├── Process: Generate Draft (Agent)
 ├── Process: Evaluate Draft (Crew: Narrative/Character/Continuity Agents)
 ├── Decision
 ├── Process: Revise Draft (Agent)
 └── Human Approval
```
This cleanly separates workflow control, professional collaboration, professional execution, and human decision.

## Crew Result Contract

```yaml
crew_result:
  status: { type: enum, values: [PASS, NEEDS_REVISION, REJECTED, INCONCLUSIVE, FAILED] }
  output_reference: { type: artifact_reference }
  findings_count: { type: integer }
  required_action: { type: enum, values: [CONTINUE, REVISE, ESCALATE, TERMINATE] }
```
Derive the exact contract from the Process. Keep it small enough for Flow control — project the large Crew output down to a structured result, don't copy it wholesale into global state. Similarly, the Crew's rich collaboration context (chapter, character/continuity facts, criteria, specialist findings, evidence) stays with the Crew; the Flow only retains what it needs (`evaluation_status`, `review_reference`). Within the Crew, scope context per specialist rather than sharing everything.

## Security & Observability Across Boundaries

**Security**: Flow controls which Process executes, when external capabilities are invoked, which state is exposed, which human gates apply. Crew controls which Agents have which capabilities/Tools/MCP servers/Knowledge access. `Flow → Authorized Process → Crew → Agent → Scoped Tool` — least privilege at every layer. Side effects (e.g. publishing) belong to their own explicit Process boundary — a review Crew should never unexpectedly publish content.

**Observability**: preserve correlation across the whole stack — `execution_id, flow_id, process_id, crew_id, agent_id, task_id` — so a Crew failure can be traced to the specific Process/Agent/Task/capability/retry/transition involved, instead of a generic "workflow failed."

**Cost model**: Flow orchestration cost + Crew collaboration cost + Agent execution cost + Task context cost + Synthesis cost + Tool/MCP cost + Retry cost — evaluate whether collaboration value justifies the total. When optimizing an expensive Crew+Flow system, work in this order: remove unnecessary Processes → unnecessary Crews → unnecessary Agents → merge unnecessary Tasks → reduce context → reduce Knowledge/Skills → move deterministic Agent work to Python → reduce synthesis → optimize parallelism → optimize model selection → optimize retries → optimize external capability usage. Never optimize by weakening required professional capability first.

## Anti-Patterns

- **Giant Crew inside giant Flow** — both boundaries too broad (Writer+Researcher+Image+Audio+Publisher+DevOps in one Crew).
- **Crew used as workflow engine** — Crew internally decides Generate→Review→Revise→Approve→Publish; these are Processes, use Flow.
- **Flow used as professional team** — Flow contains large blocks of Agent-specific reasoning; move that into Agents/Tasks/Crews.
- **Flow state dump / Crew context dump** — every output becomes global state / every Agent gets all Flow state and all Crew outputs; use dependency-based propagation and store only decision-relevant info.
- **Hidden human approval** — inside an Agent prompt instead of an explicit Flow gate.
- **Agent-controlled global state** — Agents freely mutate workflow state instead of going through explicit Process-output→state-update contracts.
- **Unbounded Crew↔Flow loop** — no explicit iteration limits/termination.
- **Crew for independent Processes** — unrelated Processes grouped into one Crew instead of Flow orchestration.
- **Flow for specialist collaboration** — specialists that need to genuinely reason together are just run sequentially by the Flow instead of collaborating in a Crew.

## Implementation Specification

```yaml
crew_flow:
  flow: { id: chapter_production, version: "1.0" }
  process: { id: evaluate_chapter, purpose: "Evaluate a chapter using multiple professional perspectives." }
  crew:
    id: chapter_quality_review
    agents:
      - { id: narrative_editor, responsibility: "Evaluate narrative structure and pacing." }
      - { id: character_editor, responsibility: "Evaluate character motivation and behavioral consistency." }
      - { id: continuity_editor, responsibility: "Evaluate consistency with established story facts." }
    tasks:
      - { id: evaluate_narrative, agent_id: narrative_editor }
      - { id: evaluate_character, agent_id: character_editor }
      - { id: evaluate_continuity, agent_id: continuity_editor }
    collaboration: { model: parallel_then_synthesis }
    output: { name: chapter_review, format: json, schema: {} }
  flow_contract:
    crew_input: [chapter, story_bible, revision_number]
    crew_output: [evaluation_status, review_reference]
    transitions:
      - { condition: "evaluation_status == APPROVED", to: approval }
      - { condition: "evaluation_status == NEEDS_REVISION", to: revise_chapter }
  iteration: { counter: revision_number, limit: 3 }
```

## Combined Validation

`Flow Validation → Process Validation → Crew Validation → Agent–Task Validation → Boundary Validation → Integration Validation`. Central question: **does the Flow correctly orchestrate the Crew without leaking responsibilities across architectural boundaries?**

```yaml
crew_flow_validation:
  flow_valid: false
  crew_valid: false
  process_alignment: ""
  boundary_alignment: ""
  input_contract: ""
  output_contract: ""
  state: { ownership: "", minimality: "", propagation: "" }
  transitions: { correctness: "", determinism: "", reachability: "" }
  collaboration: { necessity: "", model: "", coherence: "" }
  failure: { propagation: "", containment: "", recovery: "" }
  iteration: { bounded: false, termination: "" }
  human: { gates: [] }
  capabilities: { sufficient: false, minimal: false }
  efficiency: { context: "", token: "", runtime: "" }
  observability: { traceability: "", metrics: "" }
  findings: []
  decision: { status: "", action: "", rationale: "" }
  approved: false
```

**Integration test scenarios** to run: (1) normal success — Crew PASS → next Process → SUCCESS; (2) revision — NEEDS_REVISION → Revision → Crew PASS → SUCCESS; (3) revision exhaustion — repeated NEEDS_REVISION until limit → EXHAUSTED; (4) partial specialist failure — behavior depends on whether the failed Agent is mandatory; (5) human rejection — Crew PASS → Human Gate REJECT → REJECTED; (6) external capability failure — MCP failure inside the Crew → Retry/Recovery/Escalation per the failure plan.

**Hierarchical observability trace**: `Flow Execution → Process Execution → Crew Execution → {Agent Execution → Task Execution} × N → Synthesis → Transition` — enables debugging at the smallest meaningful boundary.

## Architecture Change Rules

If runtime shows the Crew is unnecessary → reconsider Crew selection. If the Flow is unnecessarily complex → reconsider Flow boundaries. If the Crew can't satisfy the Process → reconsider Agent/Task/Crew composition. If the Flow can't correctly control execution → reconsider state/transitions. Route changes back to the appropriate architecture layer rather than accumulating patches.

---

## Final Rules

1. Flow owns orchestration. 2. Crew owns professional collaboration. 3. Process defines the meaningful work boundary. 4. Agent represents professional capability. 5. Task represents bounded execution work. 6. Flow state represents current workflow state. 7. Crew context represents information required for collaboration. 8. Structured Crew results should drive deterministic Flow transitions whenever possible. 9. Semantic decisions should be made by semantic capabilities only when necessary. 10. Human decisions remain explicit Flow gates. 11. Crew failures should not automatically become Flow failures. 12. Failure propagates only as far as necessary. 13. Iterations belong to Flow control. 14. Collaboration belongs to Crew. 15. Large Crew outputs should remain artifacts when possible. 16. Only decision-relevant information enters Flow state. 17. Knowledge, Memory, Context, and State remain distinct. 18. Deterministic work stays deterministic whenever sufficient. 19. Crew complexity must be justified by collaboration value. 20. Flow complexity must be justified by orchestration requirements. 21. No component silently absorbs another's responsibility. 22. Every boundary stays traceable to the validated architecture.

```text
FLOW:  "What happens next?"
CREW:  "Which professionals need to work together?"
PROCESS: "What meaningful work needs to happen?"
AGENT: "Which professional capability performs it?"
TASK:  "What bounded operation does that capability execute?"
```

> Use Flow for lifecycle and control, Crew for bounded professional collaboration, Process for meaningful work, Agent for professional capability, and Task for bounded execution. Do not put a Crew inside a Flow merely because the workflow is complex — put it there when the workflow requires explicit orchestration AND one or more bounded Processes genuinely require multi-specialist collaboration.

The result: explicit boundaries + minimal sufficient capability + controlled collaboration + deterministic orchestration where possible + bounded failure/iteration + minimal context/state + complete traceability. This is the preferred **Crew + Flow architecture pattern for Amsha**.
