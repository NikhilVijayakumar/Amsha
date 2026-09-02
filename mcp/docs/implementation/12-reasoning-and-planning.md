# Reasoning and Planning

## Purpose

Defines how Reasoning and Planning should be selected, scoped, implemented, and validated. Both are powerful capabilities that should **not be enabled just because an Agent is intelligent or a workflow is complex** — a Flow already provides explicit planning at the architecture level.

> Use Reasoning when the work requires deliberate inference or multi-step judgment. Use Planning when the work requires dynamic decomposition or action sequencing that cannot be adequately defined by the deterministic architecture.

## Core Distinction

```text
Reasoning = How a capability thinks through a problem → "What does this evidence imply?" → judgment/inference
Planning  = How a capability determines what actions to perform → "What should I do next?" → action sequence
```

- **Reasoning** fits: comparing conflicting evidence, inferring motivation, diagnosing inconsistency, evaluating competing interpretations, resolving ambiguous requirements, judging whether evidence supports a conclusion. It's about **reaching a sound conclusion**.
- **Planning** fits: determining which research steps are needed, choosing an investigation sequence, decomposing an unfamiliar objective, adapting actions to intermediate results, deciding which tools to use and in what order. It's about **determining a course of action**.

## Flow vs Planning

`Flow` = explicit architecture-defined execution control. `Planning` = dynamic execution strategy chosen by a capability. **If Amsha already knows the workflow structure, encode it in the Flow** — don't ask an Agent to "dynamically plan" `Analyze→Generate→Evaluate→Revise` when that's already known. Planning becomes useful only when the action sequence genuinely can't be predetermined (e.g. "investigate why an artifact is inconsistent" — inspect source? compare versions? query external system? — the best next action depends on what's discovered).

## Deterministic First

```text
Can deterministic logic solve it?      YES → Python
Does one professional capability solve it? YES → Agent
Does it require deliberate semantic inference? YES → Reasoning
Does it require dynamic action sequencing?     YES → Planning
```
Reasoning and Planning must be justified capabilities, never defaults.

## Reasoning in Practice

Attach Reasoning to a professional Agent role that needs it ("Senior Investigative Editor + Evidence Analysis Skill + Reasoning"), not a generic "Reasoning Agent." Give it a defined purpose, not "the problem is difficult":
```yaml
reasoning: { required: true, purpose: "Compare contradictory evidence and determine which interpretation is best supported.", inputs: [evidence_set, domain_rules], output: [conclusion, evidence_basis, uncertainty] }
```

**Types** (use only where a taxonomy adds clarity, not as forced ceremony): Deductive (rule+facts→conclusion — often better as deterministic validation if fully rule-based), Inductive (pattern across observations→general conclusion, needs semantic judgment), Abductive (best explanation for evidence among several plausible ones — strong candidate for reasoning), Comparative (evaluate alternatives against criteria), Constraint-based (multiple simultaneous constraints — deterministic if checkable, reasoning if interpretation is required), Evidence-based (`Evidence → Interpretation → Candidate conclusions → Evaluation → Conclusion`, provenance preserved, conclusion never an unsupported assertion).

**Output** should be structured, not free-form:
```yaml
reasoning_result: { conclusion: "", confidence: 0.0, evidence: [{reference: "", relevance: ""}], alternatives: [{conclusion: "", reason_rejected: ""}], uncertainty: [] }
```
Don't force a long explanation when the Process only needs `{status, issues}` — put rationale in the output contract only if it's actually needed downstream.

**Reasoning vs deterministic validation**: `score >= 80` or "does required field exist" need no reasoning — use Python/schema validation. Reserve reasoning for genuinely semantic judgment ("does this emotional transformation feel earned?"). Reasoning also doesn't imply autonomous authority — a recommendation can still route to a Flow-owned Human Gate for high-impact decisions (publishing, deletion, irreversible modification, high cost, canon changes, external communication).

## Planning in Practice

```text
Goal → Possible actions → Evaluate actions → Select sequence → Execute → Observe result → Re-plan if necessary
```
This is fundamentally different from a fixed Flow (`A→B→C`, which needs no planning). Planning operates **inside a bounded architectural Process** — never let an Agent dynamically decide the entire application architecture.

**Scope every planning capability explicitly**: goal, available actions, constraints, resources, termination condition, budget, failure behavior, authority.
```yaml
planning:
  enabled: true
  goal: "Determine the minimum research actions required to resolve the source discrepancy."
  available_actions: [inspect_source, compare_versions, query_reference, validate_claim]
  constraints: { max_actions: 6 }
  termination: { success: "discrepancy resolved", failure: "action budget exhausted" }
```
Use a bounded, explicit **action space** ("search, inspect, compare, validate, summarize") rather than "you can do anything" — improves safety, predictability, validation.

**Tools/MCP**: Planning selects and executes but never grants additional permissions — only explicitly authorized capabilities should be exposed; an Agent shouldn't dynamically discover unrestricted capabilities just because Planning is on.

**Knowledge/Skills/Memory feed planning** but don't dictate it: Knowledge constrains ("source hierarchy" → which sources to consult first), Skills supply reusable planning methodology, Memory can inform ("Search A produced nothing before → avoid repeating unless conditions changed") without automatically dictating the current plan.

**Planning + Flow + Crew**: Flow controls the major lifecycle; Planning controls the internal action strategy of one bounded Process. A Crew may contain a planning-enabled specialist, but don't add a planner Agent just because the Crew has multiple Agents — if the collaboration structure is known, use explicit Crew Tasks instead. Planning (dynamic action determination) and Crew (cross-specialist collaboration) solve different problems and are independently justified.

**Planning vs Reasoning**: Reasoning picks a conclusion ("which explanation best fits the evidence?"); Planning picks an action ("which investigation should I do next?") — planning usually needs reasoning, but the concepts stay distinct.

## Bounding the Loop

```text
Goal → Plan → Action → Observation → Evaluate
  → Goal achieved → END
  → More actions → REPLAN
  → Cannot proceed → FAILURE
```
Must define: max actions, max time, token budget, external-call budget, termination condition. **Re-plan only when new information materially changes the strategy** — not just because the Agent can. Watch for **no-progress loops** (`A→B→A→B→...`) via action-count limits, repeated-action detection, state-progress/goal-distance tracking, time/resource budgets.

**Termination outcomes** must be explicit — `SUCCESS` (evidence found), `VALID_NEGATIVE` (evidence doesn't exist), `FAILURE` (sources exhausted), `EXHAUSTED` (budget reached), `ESCALATION` (needs human judgment). "No further ideas" is not a sufficient termination contract.

**Authority & safety**: `Planner → Proposes Action → Permission/Policy Check → Allowed? → Execute | Reject/Re-plan/Escalate`. Be more conservative as side effects increase (read < generate-draft < publish < delete). High-impact/irreversible actions need explicit authorization, human approval, idempotency, transaction boundaries, rollback. If a planner can retry an action, side-effecting operations must be idempotent (execution ID + duplicate detection) or gated behind human approval — a repeated `publish()` shouldn't create duplicates.

**Budgets** should be explicit: `max_actions, max_tool_calls, max_mcp_calls, max_llm_calls, max_tokens, max_duration_seconds`. Reasoning has its own budget dimensions too: token budget, latency, candidate count, evidence-source count, reasoning iterations.

**Reasoning context** should be curated (question + relevant evidence + applicable Knowledge + evaluation criteria + constraints), not "question + entire project + entire memory + all artifacts + all Knowledge" — more information isn't automatically better reasoning. In planning loops, keep only current goal + current plan + relevant observations + decision-relevant history + action results in context; keep large evidence externally referenced (inspect a large research corpus incrementally rather than loading it wholesale).

**Retry ≠ Planning/Reasoning**: a retry repeats the same operation; reasoning performs inference; re-planning determines a new strategy after a failure changes the available options. Don't disguise a plain retry as "reasoning" or "re-planning."

## Selection Aids

| Requirement | Preferred Mechanism |
|---|---|
| Deterministic condition / rule-based validation | Python |
| Semantic interpretation | Agent |
| Complex inference | Agent + Reasoning |
| Fixed sequence | Flow |
| Dynamic action sequence | Planning |
| Multi-specialist collaboration | Crew |
| Dynamic collaboration strategy | Crew + Planning (where justified) |
| High-impact subjective decision | Agent + Human Gate |
| External action | Tool/MCP + policy |
| Historical / domain / reusable-method info | Memory / Knowledge / Skill |

**Before enabling Reasoning, ask**: is the requirement semantic? does it need inference not lookup? can deterministic rules solve it? does ambiguity materially affect the result? is deliberate comparison/diagnosis needed? is the output part of the Process contract? can it be bounded?

**Before enabling Planning, ask**: is the action sequence genuinely unknown? can a deterministic Flow represent it? does the next action depend on observation? is the action space bounded? are tools/capabilities authorized? is there a termination condition and resource limits? is re-planning actually valuable?

## Combined Reasoning + Planning

Justified only when a Process genuinely needs dynamic investigation *and* semantic interpretation together:
```text
Goal → Planner → Select investigation → Tool → Evidence → Reasoning → Interpretation → Planner → Next investigation
```
Recommended embedding:
```text
FLOW → Investigation Process → Planning-enabled Agent
  ├── Planning → Select Action
  ├── Tool/MCP → Observation
  └── Reasoning → Interpretation → Next Action
```
The Flow still owns the Process lifecycle; the planner must not become an unrestricted autonomous workflow engine.

**Structured plan output**:
```yaml
plan:
  goal: "resolve_source_discrepancy"
  actions:
    - { id: action_1, type: inspect_source, target: source_a, reason: "primary source" }
    - { id: action_2, type: compare_source, target: source_b, reason: "resolve conflicting claim" }
  termination: { condition: "claim status resolved" }
```
Before executing a planned action, validate deterministically where possible: action exists, capability available, permission granted, required input available, dependencies satisfied, action safe, budget available, action within Process scope.

**Plan drift**: a plan can go stale after new observations (e.g. "inspect A" becomes invalid if A is unavailable) — the architecture should explicitly permit or prohibit adaptive re-planning. But avoid **plan instability**: frequent unnecessary re-planning raises token cost, latency, and repeated actions, and makes debugging harder — re-plan only when new information materially invalidates or improves the current plan.

**Reproducibility & observability**: for important executions, record initial goal, available actions, constraints, selected actions, observations, re-plans, termination reason. Useful metrics — planning: attempts, actions selected/executed, replans, repeated/failed actions, goal completion, budget exhaustion, duration, tool calls; reasoning: attempts, candidate count, uncertainty, validation failures, human overrides.

**Security invariant**: Reasoning ≠ permission, Planning ≠ permission, Knowledge ≠ permission, Tool visibility ≠ unrestricted authority, MCP discovery ≠ authorization — the execution system enforces permissions independently of what the Agent "knows about."

## Validation Schemas

```yaml
reasoning_validation:
  agent_id: "" 
  task_id: "" 
  process_id: ""
  required: false
  purpose: ""
  semantic_need: { inference_required: false, ambiguity_present: false, deterministic_alternative: "" }
  scope: { inputs: [], constraints: [], output: "" }
  evidence: { required: false, provenance: false, alternatives_required: false, uncertainty_required: false }
  efficiency: { token_budget: null, context_budget: null }
  human: { review_required: false }
  findings: [{ id: "", severity: "", category: "", message: "", recommendation: "" }]
  decision: { status: "", action: "", rationale: "" }
  approved: false
```
```yaml
planning_validation:
  agent_id: "" 
  task_id: "" 
  process_id: ""
  required: false
  purpose: ""
  necessity: { dynamic_sequence_required: false, deterministic_flow_sufficient: false, observation_dependent: false }
  action_space: { defined: false, actions: [], unauthorized_actions: [] }
  constraints: { max_actions: null, max_tool_calls: null, max_llm_calls: null, token_budget: null, time_budget_seconds: null }
  termination: { success: "", failure: "", exhausted: "", bounded: false }
  safety: { permission_checks: false, side_effect_controls: false, idempotency: false }
  replanning: { allowed: false, trigger: "", limit: null }
  observability: { plan_history: false, action_history: false }
  findings: [{ id: "", severity: "", category: "", message: "", recommendation: "" }]
  decision: { status: "", action: "", rationale: "" }
  approved: false
```
Combined (when both enabled): also track `relationship: { reasoning_informs_plan, planning_selects_reasoning_inputs, replanning_after_reasoning }`, boundary scope (process/flow/capability), pooled resource budgets, termination, security, observability, `approved`.

Validate at multiple levels: requirement (is the capability actually necessary?), Process (does it require inference or dynamic planning?), Agent (does the professional role justify it?), Tool (are required actions available and authorized?), Flow (does dynamic execution stay within Flow boundaries?), operational (are budgets/termination/observability/recovery defined?).

---

## Anti-Patterns

- **Reasoning everywhere** — `reasoning=true` on every Agent by default.
- **Planning as a Flow replacement** — a Planner Agent deciding the entire workflow when it's already known.
- **Planning for fixed sequences** — dynamic Planning for `A→B→C`; use Flow.
- **Reasoning for deterministic logic** — asking an Agent "should score 80 pass?"; use Python.
- **Unbounded planning loop** — Goal→Plan→Action→Re-plan→Action→... with no limits.
- **Unrestricted action space** — "you may use any tool necessary."
- **Planning with unrestricted side effects** — a planner gaining independent authority to publish/delete/send/modify external systems.
- **Reasoning output without evidence** — a bare conclusion when evidence/uncertainty was required.
- **Infinite reasoning loop** — repeated semantic evaluation with no termination condition (architectural defect).

## Selection Hierarchy & Combined Pattern

```text
Can Python solve it? YES → Python
Can a fixed Flow solve the action sequence? YES → Flow
Does one professional capability perform the work? YES → Agent
    → requires semantic inference? → Reasoning
    → requires dynamic action selection? → Planning
Multiple capabilities must collaborate? → Crew
Also needs orchestration? → Flow + Crew
```
Reasoning and Planning are **capabilities added to an appropriate Agent**, not replacements for Flow/Crew/Process layers.

```text
FLOW → PROCESS → PROFESSIONAL AGENT
  (Knowledge, Skills, Reasoning, Planning, Tools/MCP, relevant Memory)
  → Structured Process Result → FLOW STATE → Deterministic Transition
```

---

## Final Rules

1. Reasoning is for semantic inference and deliberate judgment. 2. Planning is for dynamic action selection. 3. Flow is for explicit workflow orchestration. 4. Don't use Planning when the Flow already defines the sequence. 5. Don't use Reasoning when deterministic logic is sufficient. 6. Reasoning should attach to a justified professional capability. 7. Planning should operate inside a bounded Process. 8. Planning should use an explicit action space. 9-10. Neither Planning nor Reasoning grants permissions. 11. Tool/MCP access must remain explicitly authorized. 12. Reasoning outputs should be structured when consumed downstream. 13. Important reasoning results should preserve evidence provenance. 14. Uncertainty should be representable when the domain requires it. 15-16. Planning must have explicit termination conditions and resource limits. 17. Re-plan only when justified by new information or failure. 18. Planning loops must be bounded. 19. Side-effecting planned actions need stronger controls and idempotency. 20. Human approval stays an explicit Flow gate. 21. Neither capability should silently redesign the validated architecture. 22. Evaluate both for token/latency/runtime/operational cost. 23. Dynamic behavior stays observable and traceable. 24. Select the least powerful mechanism that reliably satisfies the requirement.

## Final Principle

```text
FLOW: "What happens next?"        PLANNING: "What should I do next?"
REASONING: "What does this mean, and what conclusion follows?"
CREW: "Which professionals need to collaborate?"
AGENT: "Which professional capability performs the work?"
TASK: "What bounded operation must be executed?"
```

> Flow should define known workflow structure; Planning should handle genuinely dynamic action selection; Reasoning should handle genuinely semantic inference. **Do not add Reasoning or Planning because a problem is complex — add them only when the validated Process requires semantic inference or dynamic action selection that deterministic architecture cannot reliably provide.**
