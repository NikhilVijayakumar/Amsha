# Python and Tools

## Purpose

Defines how Python, deterministic code, Tools, and external capabilities should be selected and engineered.

> **Use deterministic Python or a Tool whenever the required operation can be reliably expressed as an explicit computation or action. Use an Agent only when professional semantic judgment is actually required.**

## Core Distinction

```text
Python = deterministic computation/control logic     Tool  = bounded callable capability or action
Agent  = professional semantic capability             Crew  = multi-specialist collaboration
Flow   = workflow orchestration
```
Decision order: deterministic computation? → Python. Bounded external/action capability? → Tool. Professional semantic work? → Agent. Multi-specialist collaboration? → Crew. Workflow control? → Flow. This should happen *before* considering Reasoning, Planning, Crew, or MCP.

## Why Python Matters

Python is a **capability-selection primitive**, not just an implementation language. It's usually correct for: calculations, transformations, routing, validation, schema checks, data manipulation, state updates, file operations, deterministic decisions, serialization, artifact management, retry/iteration counters, policy checks. If Python can reliably solve it, an Agent is unnecessary — these operations shouldn't consume LLM tokens.

**Deterministic-first pipeline**: can this be expressed deterministically? → Python. Does it need a callable capability? → Tool. Does it need professional semantic judgment? → Agent. Only then consider Reasoning/Planning/Crew/MCP.

**Where Python fits**:
- **Workflow control** — `if evaluation_status == "APPROVED": next_process = "approval" ...` beats asking an Agent "decide what runs next" when the decision is already architecturally defined.
- **State management** — `state["revision_number"] += 1` — the Flow owns state semantics, Python implements the mechanics.
- **Validation** — required field exists, enum valid, reference exists, schema matches, dependency exists, transition target exists, retry/revision count within limit, artifact reference valid — always before semantic evaluation. Boundary: "does the JSON have required fields?" → Python; "does this chapter preserve emotional trajectory?" → Agent. **Structural correctness → Python. Semantic correctness → Agent.**
- **Deterministic transformation / data prep** — normalize, dedupe, sort, parse, filter, index — should stay Python; don't use an Agent for mechanical transformation unless interpretation is genuinely required. Python can also assemble the structured context (required inputs + relevant state + artifact refs + known metadata) an Agent then receives, instead of the Agent getting raw system state — this significantly cuts context/token usage.

**Python shouldn't become a God Component** — avoid one giant `orchestrator.py` doing routing + business logic + prompt construction + Agent behavior + Tool execution + validation + persistence + recovery. Same architectural discipline applies: one coherent responsibility, clear input/output, clear failure boundary, clear ownership.

```yaml
python_component:
  id: "" 
  purpose: ""
  inputs: { required: [], optional: [] }
  transformation: ""
  outputs: { name: "", format: "", schema: {} }
  deterministic: true
  side_effects: []
  failure: { retryable: false, max_attempts: 0 }
  permissions: []
  traceability: { processes: [], requirements: [] }
```

A Process can be pure Python (e.g. `validate_architecture: architecture.json → validation_result.json`, no Agent), or a Python/Agent hybrid (`Python: extract relevant evidence → Agent: semantic interpretation → Python: validate structured result`) — often better than giving the Agent the whole Process.

## Tools

A Tool is a bounded callable capability (DB query, file retrieval, search, image/audio generation, HTTP request, calculator, repository op, artifact storage, external API). Answers "what action can this component invoke?"

**Tool vs Python**: Python = internal deterministic computation ("calculate score"); Tool = explicit callable capability ("query external database," "publish to external service"). Reading a local structured file could go either way depending on architecture.

**Scope every Tool narrowly** — `search_sources`, `fetch_document`, `store_artifact`, `publish_document`, not a generic `system_tool: "perform anything."` Narrow scope improves security, observability, testing, predictability, validation.

```yaml
tool:
  id: search_sources
  purpose: "Search approved external sources."
  input: { query: { type: string } }
  output: { format: json, schema: { results: [] } }
```

**Side effects** must be explicit — categories: `none | read | write | external_write | delete | publish | financial | irreversible`. Write Tools need stronger permission/recovery than read Tools. **Idempotency** must be declared for side-effecting Tools (`idempotent: true, idempotency_key: execution_id`) — if not idempotent, a retry may duplicate the side effect; flag this during failure validation.

**Failure & timeout**: Tool failures are independent of the Agent — the architecture decides whether to retry the Tool/Task/Agent, fail the Crew/Process, recover the Flow, or escalate to a human; never automatically retry the entire workflow. External Tools need explicit bounded timeouts.

**Permissions & assignment**: least privilege (a Research Agent gets read-only search; only a Publisher Agent gets publish capability). Attach a Tool to the smallest component that needs it, not every Agent by default. Ask: does this Task actually need this Tool? does the professional role reasonably require this capability? (a Continuity Editor needing source lookup is plausible; needing production deployment access needs strong justification). The Flow should control *when* a Process runs, not directly wield the Tool — prefer `Flow → Research Process → Research Agent → Search Tool` over the Flow doing the search itself, unless the search is deterministic Flow infrastructure.

## Selection Matrix

| Requirement | Preferred |
|---|---|
| Calculation, sorting/filtering, schema validation, state update, file transformation, internal deterministic transform | Python |
| Routing | Python / Flow |
| External API call, DB query, search, artifact publication | Tool |
| Semantic interpretation, professional judgment | Agent |
| Dynamic action selection | Agent + Planning |
| Complex inference | Agent + Reasoning |
| Multi-specialist work | Crew |

**Pattern**: `INPUT → Python validation → Python normalization → Agent semantic work → Python output validation → OUTPUT` — keeps deterministic work outside the LLM. Existence of a Tool doesn't mean an Agent should call it ("retrieve a known document by ID" needs no Agent); likewise not every Agent needs Tools — if inputs + Knowledge + Skill are enough, don't add Tools just to increase capability.

**Tool selection criteria**: necessity, scope, permission, reliability, latency, cost, side effects, idempotency, failure behavior, data access, security — the most powerful Tool is not automatically the best one. Prefer the narrowest capability (`read_document` over `filesystem_admin`/`shell`/`database_admin`). General-purpose execution (shell, dynamic code execution, filesystem/DB admin) is high-power and needs strong justification — distinguish predefined deterministic Python from Agent-generated arbitrary code execution, which carries much greater security/nondeterminism/resource/observability/permission risk.

**Tool output handling**: pass a structured, relevant extraction to the Agent, not the complete raw response; large results become artifacts with references, not inline context. Validate Tool output (schema, then semantic if needed) before it becomes trusted context — malformed external data shouldn't silently become trusted. Preserve provenance (`tool_id, execution_id, timestamp, source, request/output reference`).

**Reliability practices**: retry only failure classes likely to be transient (network timeout, not invalid authorization); use circuit breaking to stop indefinite retry loops (mark capability unavailable → recover/fallback/escalate/terminate); make fallbacks explicit (Primary Search → Fallback Search → Human escalation), never silently swap to an unrelated capability; sequence dependent Tools explicitly in the Flow/Process rather than relying on Agent memory (`create_artifact → validate_artifact → publish_artifact`); parallelize only independent, rate-limit-safe, order-independent calls with defined merge behavior.

**Security**: least privilege, credential scope, data access, side effects, input/output validation, auditability, timeouts, rate limits — availability doesn't imply authorization. Never embed credentials in Agent prompts, Task descriptions, Knowledge, Skills, Memory, or Flow state — use secure runtime configuration. Validate Agent-generated Tool inputs before they hit the external system; treat external Tool output as untrusted until validated/sanitized (especially since it may contain unexpected or adversarial content). Expose only the Tools a given Task needs (2 of 50 available), not the whole set — reduces context cost, decision complexity, accidental selection, and security surface.

## Combined Validation

```yaml
process_capabilities:
  process_id: ""
  python: { enabled: false, components: [] }
  tools: { enabled: false, tools: [] }
  agents: { enabled: false, agents: [] }
  crew: { enabled: false, crew_id: "" }
  flow: { enabled: false, flow_id: "" }
  reasoning: false
  planning: false
  rationale: { deterministic: "", tools: "", semantic: "", collaboration: "", orchestration: "" }
```
```yaml
python_validation:
  component_id: "" 
  process_id: ""
  purpose: ""
  deterministic: false
  input: { valid: false, schema: "" }
  output: { valid: false, schema: "" }
  side_effects: { declared: false, idempotent: null }
  failure: { defined: false, retryable: false, max_attempts: 0 }
  security: { permissions: [], valid: false }
  efficiency: { runtime: "", resource_usage: "" }
  observability: { enabled: false }
  traceability: { requirements: [], processes: [] }
  findings: []
  approved: false
```
```yaml
tool_validation:
  tool_id: "" 
  process_id: "" 
  agent_id: "" 
  task_id: ""
  purpose: ""
  necessity: false
  contract: { input_valid: false, output_valid: false }
  scope: { minimal: false, excessive: false }
  permissions: { valid: false, least_privilege: false }
  side_effects: { declared: false, idempotent: null }
  reliability: { timeout_defined: false, failure_defined: false, retry_defined: false }
  security: { valid: false, findings: [] }
  efficiency: { latency: "", cost: "" }
  observability: { enabled: false }
  traceability: { requirements: [], processes: [] }
  findings: [{ id: "", severity: "", category: "", message: "", recommendation: "" }]
  approved: false
```
```yaml
capability_validation:
  process_id: ""
  deterministic: { python_sufficient: false }
  tools: { required: [], unnecessary: [], excessive: [] }
  agents: { required: [], unnecessary: [] }
  reasoning: { required: false, justified: false }
  planning: { required: false, justified: false }
  crew: { required: false, justified: false }
  flow: { required: false, justified: false }
  security: { valid: false }
  efficiency: { token: "", runtime: "", latency: "", resource: "" }
  findings: []
  decision: { status: "", action: "", rationale: "" }
  approved: false
```

## Recommended Pattern & Example

```text
PROCESS → { Python: deterministic work | Agent: professional judgment | Tool: external system } → Structured Output → Flow
```
E.g. Chapter Evaluation: `Flow → Evaluate Chapter Process → Python(validate input, load artifact refs, assemble context) → Evaluation Crew (Narrative/Character/Continuity Editors, optional source-lookup Tool) → Python(validate Crew result, persist report, update Flow state) → Flow → APPROVED/NEEDS_REVISION`. Flow orchestrates, Python handles mechanics, Crew collaborates, Agent judges, Tool reaches external systems, Artifacts hold large results.

## Anti-Patterns

- **LLM for arithmetic** — Agent calculating totals; use Python.
- **LLM for routing** — Agent deciding `status == APPROVED`; use deterministic Flow logic.
- **Python for semantic judgment** — Python trying to determine if a character arc "feels authentic"; not reliably deterministic, needs a professional semantic capability.
- **Giant Tool** — a `tool: "manage everything"` instead of bounded capabilities.
- **Tool for internal computation** — calling an external Tool for work Python could do locally (unnecessary latency/failure).
- **Tool everywhere** — every Agent gets every Tool (unnecessary capability/security surface).
- **Agent as Tool router** — Agent choosing among dozens of Tools when Flow/Python can route deterministically.
- **Tool as workflow engine** — a Tool silently implementing the entire application workflow instead of just its capability.
- **Python as God Flow** — one Python function hiding processes, transitions, agents, crews, human gates, recovery.
- **Dynamic code execution everywhere** — arbitrary code execution as the default instead of predefined bounded components.

## Escalation Rule

```text
Deterministic → Python
External action → Tool
Professional semantic work → Agent
Semantic inference → Agent + Reasoning
Dynamic action sequence → Agent + Planning
Multi-specialist collaboration → Crew
Workflow orchestration → Flow
```
Don't skip directly to the most powerful mechanism.

---

## Final Rules

1. Deterministic work stays deterministic whenever possible. 2. Python for internal deterministic computation/control logic. 3. Tools for bounded callable capabilities and external actions. 4. Agents for professional semantic work. 5. Crews for genuine multi-specialist collaboration. 6. Flows for explicit workflow orchestration. 7. Don't use Agents for arithmetic, schema checks, routing, or mechanical transforms. 8. Don't use Tools when local Python reliably solves it. 9. Don't expose unnecessary Tools to Agents. 10. Every Tool needs an explicit input/output contract. 11. Tool permissions follow least privilege. 12. Side effects must be explicit. 13. Side-effecting operations define idempotency where applicable. 14. External failures need bounded retry/recovery. 15. Tool results validated before becoming trusted context. 16. Large Tool outputs become artifacts or filtered context. 17. Python components have coherent responsibility boundaries. 18. Python should not become a hidden God Flow. 19. Dynamic code execution needs stronger security/resource controls. 20. MCP is an external capability boundary, not unrestricted access. 21. Reasoning/Planning don't grant permissions. 22. Capability selection minimizes token/runtime/latency/security overhead. 23. Every capability traces to a Process requirement. 24. Use the least powerful mechanism that reliably satisfies the requirement.

## Final Principle

```text
PYTHON: "Can this be computed or controlled deterministically?"
TOOL:   "Is there a bounded capability or external action to invoke?"
AGENT:  "Does this require professional semantic judgment?"
REASONING: "Does the Agent need deliberate inference?"
PLANNING:  "Does the Agent need to dynamically determine actions?"
CREW: "Do multiple professionals need to collaborate?"
FLOW: "How should the known workflow execute?"
```

> Amsha should escalate from deterministic code to external capabilities to semantic capabilities only when the requirement demands it. Do not ask an intelligent system to perform work that a deterministic mechanism can perform more reliably, cheaply, and observably. Conversely, do not force deterministic code to perform work whose correctness depends on genuine professional semantic judgment. This boundary is fundamental to building minimal, reliable, secure, and cost-efficient Amsha architectures.
