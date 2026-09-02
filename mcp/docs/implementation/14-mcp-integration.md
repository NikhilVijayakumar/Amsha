# MCP Integration

## Purpose

Defines how MCP (Model Context Protocol) should be selected, integrated, scoped, secured, and validated. MCP is an **external capability integration boundary** — not another Tool, and not a substitute for Flow, Crew, Agent, Task, Knowledge, or Memory.

> **Use MCP when an Amsha Process or capability needs access to an external system or externally hosted capability through a standardized integration boundary. Expose only the specific capabilities required by the architecture.**

## What MCP Is — and Isn't

```text
Amsha → Flow → Process → Agent/Crew → MCP Client → MCP Server → {Tool, Resource, Prompt} → External Capability
```
`Tool = callable capability. MCP = standardized external integration boundary through which capabilities can be exposed.` MCP sits at the integration boundary, not the core architectural responsibility layer.

- **Not a Process** — a Process is a meaningful transformation ("Research historical source"); MCP just supplies the external capability the Agent uses to do it.
- **Not a Crew** — a Crew is professional collaboration; MCP is an external capability boundary (`Research Agent → MCP Search`, `Historian Agent → MCP Archive` is fine when those Agents genuinely need those capabilities, but MCP itself isn't the collaboration).
- **Not an Agent** — MCP retrieves; the Agent interprets (`MCP Search → Research Evidence → Historian Agent → Historical Interpretation`).
- **Not Knowledge** — an MCP server may *retrieve* Knowledge but is not itself the Knowledge layer.
- **Not Memory** — an external memory system might be accessed *through* MCP, but MCP remains the access mechanism, not the semantic information type.
- **Not Flow** — Flow controls execution, MCP provides capabilities (`Flow → Process → Agent → MCP capability`); never let an MCP server become a hidden workflow engine.

## When MCP Is Valuable — and When It Isn't

Valuable when the capability is external, independently deployed/maintained, shared across applications, or accessed through a common protocol (external search, DB/repository access, document systems, project management systems, specialized services, external Knowledge/Memory systems, third-party APIs).

Unnecessary when a local deterministic implementation suffices — e.g. "calculate a checksum" should be Python, not Python→MCP→checksum-server. If a local Tool already covers it without a meaningful external boundary, MCP just adds complexity.

**Before introducing MCP, ask**: is the capability external and independently managed? does it need standardized integration? is it reusable across Agents/apps? is the external boundary operationally justified? can a local Tool or Python solve it instead? No architectural benefit → don't introduce it.

## Capability Filtering & Server Boundaries

An MCP server may expose many capabilities (`search, fetch, create, update, delete`) — expose only what's required (`Research Agent → search✓, fetch✓, create✕, update✕, delete✕`). This improves security, context efficiency, Tool selection, predictability, observability. **Least privilege**: expose read-only if that's all the Process needs, even if write/delete/admin are technically available.

Server boundaries should represent a meaningful external system/domain — a `Git MCP` with `read_repository/search_code/create_branch` is coherent; a grab-bag `Utility MCP` with `calculator/weather/database/publishing/shell` usually isn't, unless one external system genuinely owns all of it.

## Connection, Retry, Idempotency, Timeouts

Track connection lifecycle explicitly (connect, discover, initialize, execute, disconnect, reconnect, shutdown) and make it observable/recoverable for persistent integrations. Choose on-demand vs. persistent connections based on frequency, latency, resource use, concurrency, reliability — don't keep expensive connections alive without justification.

**Failure modes**: connection/init/auth failure, timeout, server unavailable, transport failure, capability discovery failure, Tool execution failure, malformed response — all map into the Process failure architecture. **Retry** at the smallest boundary (retry the failed Tool call, not the whole Flow) unless architecture explicitly needs broader recovery. Retry safety varies by operation: reads (search/fetch/inspect) are usually safe to retry; writes (create/update/publish) need idempotency or stronger safeguards; deletes need particularly strong control. Never assume MCP operations are idempotent — declare it explicitly (`side_effect: {type: external_write, idempotent: false}`).

**Timeouts** must be bounded and explicit (`connect_seconds`, `operation_seconds`). **Rate limits** matter especially for a Crew with many Agents, which can unintentionally multiply MCP requests — account for request/concurrency/burst limits and backoff.

## Data Handling

**Results → context**: pass a structured, relevant extraction to the Agent, not the whole raw response. **Results → artifacts**: store large results as artifacts with references (`mcp_result: {status, external_id, artifact_reference}`) rather than embedding full payloads in Flow state.

**Data trust**: external MCP data is not automatically authoritative — track source identity/authority, retrieval time, version, validation status, provenance. The Agent should know when information is external and potentially unverified.

**Prompt injection risk**: content retrieved via MCP is *data*, not instruction — a document containing "ignore previous instructions..." must not become an Agent instruction. Maintain `SYSTEM/ARCHITECTURE INSTRUCTIONS ≠ EXTERNAL DATA`; treat external content as untrusted unless explicitly validated.

**Input/output validation**: validate Agent-generated MCP parameters before sending (don't rely solely on the Agent to produce safe parameters) and validate/sanitize Tool responses before they become context (`MCP Server → Response → Schema validation → Sanitization → Context`).

## Security

Authentication (who are we?) and authorization (what can we do?) are separate — validate authorization independently of Agent reasoning (`Agent → Requested capability → Authorization check → Allowed?→execute | Reject`). Never embed credentials in Agent role/goal/backstory, Task description, Knowledge, Skill, Memory, or Flow state — use secure runtime configuration; secrets should never appear as normal context. Tool discovery ≠ authorization. For multi-tenant Amsha deployments, scope MCP access by tenant/project/user/execution/Agent/Process as appropriate.

## Governance & Traceability

Track capability ownership:
```yaml
mcp_capability: { server_id: "", capability_id: "", owner: "", purpose: "", consumers: [] }
```
Maintain the dependency graph (`Process → Agent → MCP Server → Tool → External System`) so Amsha can answer "which Process depends on this external system?" and "what breaks if this server goes down?" MCP should form an explicit failure boundary — a failure there shouldn't automatically contaminate unrelated Processes.

**Availability policy** per dependency: `mandatory | optional | fallback-capable`. If optional, degraded behavior must be explicitly defined — never silently ignore a missing external capability. Fallbacks should be intentional and ordered (e.g. Primary: Search MCP → Fallback: Local Knowledge → Fallback: Human Research).

## Interaction With Other Capabilities

- **+ Knowledge**: MCP can retrieve Knowledge (`Knowledge Requirement → MCP Search → External Source → Validated Evidence → Context`) but doesn't become the Knowledge layer itself.
- **+ Memory**: same pattern — MCP is the access mechanism, Memory is the semantic information type.
- **+ Planning**: the Planner selects MCP actions only from an explicitly authorized action space (`Planner → Select allowed MCP action → MCP Tool → Observation → Reasoning → Re-plan`).
- **+ Reasoning**: MCP results become evidence for Reasoning; preserve provenance when the conclusion matters.
- **+ Human Gate**: high-impact MCP actions (irreversible writes, external communication, deletes) should route through an explicit Flow-owned human gate before execution.
- **+ Side effects**: classify explicitly — read-only, reversible write, irreversible write, publish, delete, external communication — the more consequential, the stronger the required controls.
- **+ Checkpointing**: for expensive/consequential external operations, checkpoint before and after (`Before MCP Write → Checkpoint → MCP Write → Result → Checkpoint`), per the recovery architecture.
- **+ Observability**: preserve `execution_id, process_id, agent_id, task_id, mcp_server_id, capability_id, request status, duration, retry count, failure, result reference` — makes external dependencies traceable.
- **Cost model**: connection overhead, network latency, Tool execution, external service cost, retry cost, data transfer, context cost — MCP isn't free just because it's standardized. Filter to relevant Tools only, since a server with many capabilities inflates the Agent's effective Tool context.
- **Versioning/compatibility**: track `id, version, protocol_version, capability_version`; validate reachability, protocol compatibility, capability availability, Tool schema compatibility, auth validity, response schema compatibility before relying on it — external capability changes can silently change system behavior.

## Contract & Validation Schemas

```yaml
mcp_integration:
  id: ""
  server: { name: "", endpoint: "", transport: "", version: "" }
  capability: { name: "", purpose: "", type: "" }
  contract: { input: { schema: {} }, output: { schema: {} } }
  access: { processes: [], agents: [], tasks: [] }
  permissions: { scope: [], read_only: false }
  reliability: { timeout_seconds: null, retryable: false, max_attempts: 0 }
  side_effects: { type: "", idempotent: null }
  fallback: { enabled: false, capability: "" }
  observability: { enabled: true }
```
```yaml
mcp_validation:
  integration_id: "" 
  process_id: "" 
  agent_id: "" 
  task_id: ""
  structural: { server_defined: false, capability_defined: false, contract_defined: false, references_valid: false }
  necessity: { required: false, external_dependency_justified: false, local_alternative: "" }
  capability: { purpose: "", scope: "", minimal: false, excessive: false }
  permissions: { authenticated: false, authorized: false, least_privilege: false }
  contract: { input_valid: false, output_valid: false }
  reliability: { timeout_defined: false, retry_defined: false, failure_defined: false, fallback_defined: false }
  side_effects: { declared: false, idempotent: null }
  security: { secret_isolation: false, input_validation: false, output_validation: false, external_data_untrusted: true, findings: [] }
  observability: { enabled: false, correlation: false }
  efficiency: { tool_surface: "", context_cost: "", latency: "", external_cost: "" }
  traceability: { requirements: [], processes: [] }
  findings: [{ id: "", severity: "", category: "", message: "", recommendation: "" }]
  decision: { status: "", action: "", rationale: "" }
  approved: false
```

**Review sequence before approving an MCP integration**: requirement justification → external dependency justification → capability minimality → Agent/Task alignment → permission validation → I/O contract → failure/retry/recovery → side-effect safety → security → observability → cost/latency → version compatibility.

## Example Architecture

```text
FLOW
 ├── Analyze Source (Python)
 ├── Research (Research Agent → Research MCP: search, fetch)
 ├── Evaluate (Evaluation Crew: Narrative Agent, Continuity Agent)
 ├── Human Approval
 └── Publish (Publisher Agent → Publishing MCP)
```
Flow controls lifecycle, Python does deterministic work, Agent does professional work, Crew collaborates, MCP provides external capabilities.

## Anti-Patterns

- **MCP everywhere** — introduced just because it's available.
- **MCP for local deterministic work** — externalizing what Python can do reliably.
- **Unrestricted MCP server** — exposing every server capability to every Agent.
- **MCP as workflow engine** — hiding Process sequencing/branching/iteration/human gates/recovery inside MCP instead of Flow.
- **MCP as Knowledge dump / Memory dump** — treating every response as permanent Knowledge, or injecting entire external history into every Agent.
- **MCP as permission** — Tool discovery treated as authorization.
- **MCP without failure policy / timeout / side-effect declaration / provenance / version awareness** — each of these left undefined lets a single external dependency silently degrade or corrupt the whole workflow.

## Selection Hierarchy

```text
Can Python solve it? YES → Python
Is a local bounded Tool sufficient? YES → Tool
Is the capability external and does MCP provide a useful integration boundary? YES → MCP
Otherwise → reconsider architecture
```
MCP is an **integration decision**, not an automatic capability escalation. (Local Tool and MCP Tool both expose callable actions — the difference is purely the integration boundary: local capability vs. external system.)

Because Amsha itself is meant to become an MCP-facing architecture system, treat MCP integration as governed: be able to answer why a server is required, which Process/Agent uses it, what's exposed, what permissions exist, what external system is affected, what happens on failure, what data crosses the boundary, and what it costs.

---

## Final Rules

1. MCP is an external capability integration boundary. 2-7. MCP is not a Process, Crew, Agent, Knowledge, Memory, or Flow. 8. Use MCP when an external capability needs a meaningful standardized integration boundary. 9. Use Python when local deterministic implementation suffices. 10. Use a local Tool when an external boundary is unnecessary. 11. Expose only the MCP capabilities the Process requires. 12. Apply least privilege to MCP capability access. 13. Tool discovery must not be treated as authorization. 14. MCP credentials stay outside normal Agent/Task context. 15. External MCP data is data, not instructions. 16-17. Validate MCP Tool inputs before execution and outputs before trusting them. 18. Declare external side effects explicitly. 19. Define idempotency for side-effecting operations where applicable. 20-21. Define timeout, failure, and retry behavior. 22. Don't restart an entire Flow for a local MCP failure unless architecture requires it. 23. Large MCP results should be referenced as artifacts. 24. MCP dependencies should be observable and traceable. 25. Track MCP capability versions where relevant. 26. Required external dependencies need explicit availability/fallback behavior. 27. High-impact external actions need stronger authorization, potentially human approval. 28. Planning may select MCP actions only from an explicitly authorized action space. 29. Evaluate MCP integration for token, latency, runtime, external cost, and operational complexity. 30. Every MCP dependency must trace back to a validated Process requirement.

## Final Principle

```text
PYTHON: "Can I compute this deterministically?"
TOOL:   "Can I invoke this bounded capability?"
MCP:    "Does this capability belong behind an external standardized integration boundary?"
AGENT:  "Does a professional need to interpret or decide?"
CREW:   "Do multiple professionals need to collaborate?"
FLOW:   "How does the workflow execute?"
```

> MCP should make external capabilities accessible without allowing external capability access to blur the architectural boundaries of Amsha.

```text
FLOW → PROCESS → AGENT/CREW → MCP INTEGRATION → MCP SERVER → EXTERNAL CAPABILITY
```
with Python for deterministic work, Tool for bounded callable capability, MCP for the external integration boundary, Agent for professional semantic capability, Reasoning for semantic inference, Planning for dynamic action selection, Crew for professional collaboration, Flow for workflow orchestration.

> Use MCP to cross an external capability boundary, not to compensate for poor architecture. The Process defines why the capability is needed, the Agent/Task defines who and what needs it, permissions define what may be done, and the Flow defines when it happens.
