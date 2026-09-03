# Crew Evaluation

## Purpose

Crew engineering builds a Crew. Crew evaluation asks: **is this Crew actually capable of satisfying its Process contract, and is it the right architecture for doing so?** Successful Agent execution alone does not imply Crew success.

Position: after Crew Engineering, before implementation is considered complete. Full chain: `Problem → Goal/Boundary → Process Decomposition → Contracts → Validation → Flow/State → Failure Planning → Capability Selection → Architecture Validation → Process/Agent/Task Engineering → Agent-Task Alignment → Crew Engineering → Crew Evaluation → Flow Engineering → Implementation → Execution → Observability`. Crew evaluation is design-time; runtime metrics add evidence but don't replace it.

**Engineering** decides what Crew should exist. **Evaluation** decides whether it's sufficient, coherent, minimal, and operationally viable — five properties: sufficiency, correctness, coherence, minimality, operational viability.

---

## Evaluation Layers (cheap → expensive)

1. Structural — 2. Process Alignment — 3. Agent Coverage — 4. Task Coverage — 5. Collaboration — 6. I/O — 7. Context — 8. Capability — 9. Failure — 10. Security — 11. Efficiency — 12. Traceability — 13. Final Decision

## 1. Structural

Crew ID, Process ID, Agent/Task references, collaboration model, input/output/validation contracts, failure policy, resource references — all must exist and resolve. Structural correctness does not imply semantic quality.

## 2. Process Alignment & Coverage

Trace: Process purpose → Crew purpose → Crew output → Process output. Ask: does the Crew fully implement the intended Process, without omitting or adding unrelated work? A Crew is not approved just because its name resembles the Process. Under-coverage (e.g. Crew checks only dates when Process needs full historical authenticity) and over-coverage (Crew absorbs unrelated Processes like writing+audio+publishing) are both findings — `PROCESS_COVERAGE_GAP` (blocking) or `SPLIT_PROCESSES` recommendation respectively.

## 3. Agent Coverage & Quality

Map Process requirements → professional responsibilities → Agents. Flag: missing specialist, duplicate specialist, unnecessary specialist, incorrectly scoped specialist.

**Contribution test**: what does this Agent contribute that the rest of the Crew doesn't? Retain only if necessary, materially useful, professionally distinct, or explicitly required.

**Diversity** is measured by discipline/specialization/expertise/perspective — never by name, personality, tone, prompt wording, or temperature.

**Duplication**: compare role, goal, specialization, perspective, Tasks, Knowledge, Skills, Tools, permissions, outputs. Not automatically an error — independent/adversarial review, isolation, or differing permissions can justify two similar Agents. Distinguish intentional redundancy from accidental duplication.

## 4. Task Coverage & Atomicity

Every Crew responsibility → Task → Agent. Flag missing, out-of-scope, duplicate, composite, orphan, or misassigned Tasks. Reuse `03-atomic-task-design.md`'s atomicity model (one responsibility + one transformation + one completion boundary + one coherent output) rather than reinventing one.

## 5. Agent–Task Alignment

Reuse alignment results: professional fit, capability sufficiency, input sufficiency, output/validation/failure compatibility, permissions. A blocking mismatch should normally block Crew approval.

## 6. Collaboration Evaluation

**Necessity** — the single most important dimension. Ask: does collaboration provide architectural value?
- `ESSENTIAL` — Process cannot be satisfied without specialist collaboration.
- `USEFUL` — materially improves quality/reliability.
- `OPTIONAL` — a simpler architecture could work.
- `UNNECESSARY` — Crew exists because multiple Agents were available → recommend `USE_SINGLE_AGENT` or `USE_FLOW_INSTEAD`.

**Coherence** — Agents should collaborate toward one bounded outcome (e.g. Narrative/Character/Continuity Editors → Consolidated Review), not an unrelated grab-bag (Writer + DB Engineer + Audio + Marketing + DevOps).

**Model** — must match the dependency structure: `parallel` (independent Tasks), `sequential` (later depends on earlier), `specialist_synthesis` (independent findings → one result), `review_and_reconcile` (disagreement must resolve), `delegated` (lead delegates). Never chosen for implementation convenience.

**Dependency** — verify each `A → B` edge means B genuinely needs A's output; avoid artificial chains `A→B→C→D` that could run independently (adds latency, coupling, failure propagation, context size).

**Parallelism** — valid only when inputs are available, work is logically independent, state ownership is safe, outputs mergeable, downstream deps explicit.

**Synthesis** — if multiple specialist outputs merge into one result, make explicit: who synthesizes, what's synthesized, criteria, conflict handling, output contract, validation. Mechanism can be Agent, Python, Flow logic, deterministic aggregation, or human review — not automatically an Agent.

**Disagreement** — valuable, not automatically an error. Define whether the Crew reconciles, requests evidence, preserves both findings, escalates, or sends to human review. Never silently discard conflicting output.

**Consensus ≠ evidence ≠ correctness.** Prioritize evidence, explicit criteria, deterministic checks, domain Knowledge, professional reasoning, human review over agreement-counting.

## 7. Input / Context Evaluation

Check required/optional inputs, sources, formats, state deps, artifacts, Knowledge, Skills exist. Missing required input is blocking unless recovery is defined.

**Minimality**: having all required info ≠ needing to receive everything. Flag `FULL_PROJECT_CONTEXT`, `ALL_KNOWLEDGE`, `ALL_PREVIOUS_OUTPUTS`, `ALL_TOOLS`, `ALL_FLOW_STATE` when only a subset is needed.

**Propagation** should follow actual data dependencies (Agent B receives only Agent A's output it needs), not a blanket "every Agent gets everything."

## 8. Capability Evaluation

- **Knowledge** — relevant, sufficient, correctly scoped, minimally exposed; ask if every Agent truly needs it or if it's actually dynamic state.
- **Skills** — correctly attached to the Agent/Task that needs the reusable methodology, not embedded redundantly.
- **Tools** — every Tool must trace to a specific Agent+Task+reason; unjustified Tools removed.
- **MCP** — server/tool existence, minimal exposure, permissions, side effects, failure behavior, latency. Availability of an MCP server is not evidence it's needed.
- **Reasoning** — justified by Task requirement, not "enabled by default." Findings: `UNNECESSARY_REASONING` / `INSUFFICIENT_REASONING` / `CORRECT_REASONING_SCOPE`.
- **Planning** — only if specialist involvement/actions must be decided dynamically; if the sequence is known (`A→B→C`), Flow suffices. Findings: `UNNECESSARY_PLANNING` / `MISSING_PLANNING` / `CORRECT_PLANNING_SCOPE`.
- **Memory** — only if retained info can't come from current Knowledge/context/Flow state. Never a substitute for good context design.

## 9. Output Evaluation

Existence, format, schema validity, required fields, semantic requirements, downstream compatibility, provenance. Intermediate outputs justified only if they feed another Agent, support synthesis/validation/recovery, or provide evidence — otherwise they're pure token/storage overhead.

**Provenance** (source Agent + evidence per finding) matters when specialists disagree, human review is needed, or auditability/verification matters — not everywhere by default.

## 10. Completion & Success

Distinguish: Agent completed ≠ Agent output produced ≠ Crew execution completed ≠ Crew output validated ≠ Process succeeded. Example: all Agents complete, synthesis completes, schema validation fails → Crew execution complete but `success = false`. Success criteria live at the Process-contract level ("produce a valid consolidated review with all required findings"), never "all Agents returned successfully."

## 11. Failure Evaluation

Distinguish Agent / Task / Collaboration / Synthesis / Validation / External-capability / Process failure — each needs its own response.

**Containment**: fail at the smallest safe boundary. Optional specialist fails → retry/degrade/continue. Mandatory specialist fails → Crew cannot satisfy contract.

**Retry**: bounded attempts, explicit retry scope, idempotency, cost, escalation. Never retry forever, and never use retry to paper over bad prompts, wrong Agent assignment, missing Knowledge, broken Task boundaries, or deterministic validation failures.

**Iteration** (Generate→Evaluate→Revise→Evaluate): needs explicit trigger, success condition, max iterations, terminal behavior, retained state. No unconstrained Agent back-and-forth.

## 12. Security & Efficiency

**Security**: Agent/Tool/MCP permissions, file access, external side effects, secrets, data boundaries. No capability merely because an Agent could theoretically use it — least privilege at Agent and Tool level.

**Efficiency**: Agent/Task count, LLM calls, context size, Knowledge retrieval, Tool/MCP calls, retries, iterations, Memory ops, latency. More specialists isn't automatically better — cost must be justified by value.

**Token footprint** = sum of Agent+Task prompts, Knowledge, Skills, dynamic context, previous outputs, Tool/MCP schemas, synthesis context. Prefer giving each Agent only its relevant slice over repeatedly injecting full project context.

**Deterministic work** delegated to Agents (e.g. three Agents score 8/7/9, then an Agent "calculates the mean") should move to Python — arithmetic, schema validation, sorting, filtering, counting, aggregation, routing, state checks.

## 13. Operational

**Runtime feasibility**: token budget, latency target, memory, Tool/MCP availability, parallelism, retry limits, expected workload, artifact size. A semantically correct Crew that can't execute within constraints isn't production-ready.

**Observability**: Crew/Agent/Task status, LLM latency, token usage, Tool/MCP calls, retries, failures, validation results, output sizes, human decisions — enough to diagnose without over-exposing sensitive data.

**Traceability chain**: Requirement → Process → Crew → Agent → Task → Output. Should answer "why does this Agent/Task/Crew exist, and which requirement does this output satisfy?"

---

## Evaluation Score vs Gate

A numeric quality score is useful for comparison but must never override a blocking architectural condition (`Score=92` does not excuse `BLOCKING: required responsibility uncovered`). **Hard constraints beat aggregate scores.**

## Evaluation Dimensions (schema keys)

`process_alignment, process_coverage, agent_coverage, agent_quality, task_coverage, task_atomicity, collaboration_necessity, collaboration_coherence, dependency_correctness, parallelism, synthesis, disagreement_handling, input_sufficiency, context_efficiency, knowledge_alignment, skill_alignment, tool_alignment, mcp_alignment, reasoning_alignment, planning_alignment, memory_alignment, output_quality, output_contract, failure_handling, retry_safety, security, resource_efficiency, token_efficiency, runtime_feasibility, observability, recoverability, traceability, simplicity`

## Status & Severity

Status: `NOT_EVALUATED | PASS | PASS_WITH_WARNINGS | REQUIRES_REVISION | BLOCKED | REJECTED` (REJECTED = fundamentally wrong mechanism for the Process, not just flawed).
Severity: `INFO | WARNING | ERROR | BLOCKING`.

## Crew Evaluation Schema

```yaml
crew_evaluation:
  crew_id: ""
  process_id: ""
  architecture_version: ""
  status: ""
  structural: { schema_valid: false, references_valid: false, process_reference_valid: false, agents_valid: false, tasks_valid: false, collaboration_defined: false }
  process: { alignment: "", coverage: "", scope: "", contract_compatibility: "" }
  agents: { coverage: "", quality: "", duplication: [], missing_capabilities: [], unnecessary_agents: [], overloaded_agents: [] }
  tasks: { coverage: "", atomicity: "", alignment: "", orphan_tasks: [], composite_tasks: [] }
  collaboration: { necessary: false, value: "", model: "", coherence: "", dependencies: "", parallelism: "", sequencing: "", synthesis: "", disagreement_handling: "" }
  inputs: { sufficiency: "", minimality: "", compatibility: "" }
  outputs: { contract_defined: false, schema_valid: false, semantic_quality: "", downstream_compatible: false, provenance: "" }
  context: { relevance: "", minimality: "", propagation: "", isolation: "" }
  capabilities: { knowledge: "", skills: "", tools: "", mcp: "", reasoning: "", planning: "", memory: "", unnecessary: [] }
  failure: { coverage: "", containment: "", retry_safety: "", iteration_safety: "", recovery: "" }
  security: { permissions: "", least_privilege: "", external_side_effects: "", findings: [] }
  efficiency: { agent_count: 0, task_count: 0, token_footprint: "", context_cost: "", llm_cost: "", tool_cost: "", latency: "", resource_efficiency: "" }
  operational: { runtime_feasibility: "", observability: "", recoverability: "", termination: "" }
  traceability: { requirements: [], processes: [], agents: [], tasks: [], uncovered: [] }
  findings: [{ id: "", severity: "", category: "", component: "", message: "", recommendation: "" }]
  decision: { status: "", action: "", rationale: "" }
  approved: false
```

## Worked Examples

| Scenario | Verdict | Reasoning |
|---|---|---|
| Chapter Quality Crew: Narrative/Character/Continuity Editors + Review Lead synthesizing | **PASS** | Full coverage, essential collaboration, valid parallelism, explicit synthesis, sound output contract |
| JSON Validation Crew (JSON/Schema/Validation "Experts") for pure schema validation | **REMOVE_CREW → USE_DETERMINISTIC_PROCESSING** | No semantic judgment required |
| Content Production Crew (Writer, Historian, Image Gen, Audio, Publisher, DB Engineer) for "Evaluate Chapter" | **FAIL — scope over-broad** | Absorbs unrelated Processes → `SPLIT_PROCESSES`, `USE_FLOW`, `CREATE_BOUNDED_CREWS` |
| Narrative Review Crew: 3 Agents (Senior Narrative Editor / Expert Story Reviewer / Master Narrative Specialist) doing the same thing | **MERGE_AGENTS** | High duplication, no independent-review requirement |
| Historical-authenticity Process with only Narrative + Continuity Editors, no historical verification | **BLOCKED** | Agent/process coverage incomplete → `ADD_AGENT: Senior Historical Consultant`, re-evaluate |
| Synthesis Agent whose only job is averaging 3 numeric scores | **REMOVE_SYNTHESIS_AGENT → USE_DETERMINISTIC_PROCESSING** | Deterministic work, no professional responsibility |
| Historical/Narrative/Continuity specialists genuinely disagree on one event | **NOT a failure** | Represent conflict explicitly (`status: NEEDS_REVIEW`, per-dimension verdicts), route to Revision or Human Review — reward explicit conflict over forced consensus |

---

## Checklist

**Process**: maps to validated Process · responsibility fully covered · no unrelated absorption · output satisfies contract.
**Agents**: every capability represented · every Agent contributes value · Agent–Task alignment passes · no unnecessary duplication/breadth · no missing specialist.
**Tasks**: atomic · correctly assigned · explicit I/O · explicit completion/validation criteria.
**Collaboration**: genuinely required · model explicit · dependencies valid · parallelism safe · sequencing justified · synthesis explicit · disagreement handling defined.
**Context**: required, relevant, minimal · propagation follows data deps · state not confused with Knowledge/Memory.
**Capabilities**: Knowledge/Skills/Tools/MCP/Reasoning/Planning/Memory each justified · deterministic work not delegated to Agents.
**Failure**: Agent vs Crew vs Process failure distinguished · retry bounded and safe · iterations bounded · recovery explicit · termination defined.
**Security**: permissions sufficient and minimal · external capabilities scoped · side effects explicit.
**Efficiency**: Agent/Task count, context, token footprint, runtime cost, latency all justified.
**Operations**: runtime feasibility established · observability sufficient · recovery boundaries defined · traceability preserved.

---

## Final Principle

Don't ask "does this Crew contain good Agents?" Ask: **"does this Crew form the smallest sufficient professional collaboration capable of reliably satisfying its Process contract?"**

Evaluation chain: `Process Requirement → Crew Responsibility → Professional Coverage → Agent Coverage → Task Coverage → Collaboration → Output Contract → Validation → Failure/Recovery → Efficiency → Operational Feasibility`.

> A Crew is approved only when its combined professional capabilities are sufficient, its collaboration is meaningful, its boundaries are coherent, its output satisfies the Process contract, and no simpler architecture can reliably provide the same capability.
> Crew complexity must be justified by collaboration value, not by the complexity of the problem alone.
