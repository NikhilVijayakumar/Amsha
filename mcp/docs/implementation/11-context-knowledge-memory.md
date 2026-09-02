# Context, Knowledge, and Memory

## Purpose

Defines how Context, Knowledge, Skills, Memory, Flow State, Process/Task Inputs, and Artifacts should be separated. All of them "provide information," which makes them easy to conflate — they are not interchangeable.

> **Give each execution component the smallest amount of information it needs, through the mechanism whose semantics match the information's purpose.**

## The Information Architecture

```text
Knowledge = What I know          Memory   = What I remember
Skills    = How I work           Context  = What is relevant now
Input     = What this execution receives
State     = Where the workflow currently is
Artifact  = Where a larger result is stored
```
Persistent info (Knowledge→Skills, Memory) vs. execution-time info (Context→Inputs, State) vs. externally-referenced data (Artifacts). These categories have different lifetimes, ownership, and retrieval behavior — keep them explicit.

## Core Definitions & Distinctions

- **Knowledge** — reference information about the domain ("Arjuna uses the Gandiva bow"; story bible, character facts, world rules, historical facts, specs, terminology, style canon). Answers "what do I need to know about the world?" Not an instruction for *how* to do something.
- **Skill** — how a capability performs a repeatable method ("To evaluate weapon continuity: identify established ownership → compare scene usage → flag contradictions"). Both Knowledge and Skill may live in Markdown files; the difference is semantic (fact vs. methodology), not format.
- **Memory** — retained historical information ("user rejected version 1 because Arjuna behaved inconsistently"). Answers "what happened previously that may matter now?" Knowledge describes the world; Memory records what happened.
- **Context** — information relevant to *this* execution, selected from Knowledge/Memory/State/Inputs/Previous Outputs/Artifacts. Usually a *selection*, not an independent source of truth. E.g. for "evaluate Ch.7 continuity," context = chapter 7 + Arjuna's profile + relevant prior chapter + arc requirements + prior findings, not the entire story universe.
- **Input** — what a Process/Task explicitly receives per its contract (`required: [chapter, character_profile], optional: [previous_review]`). Input answers "what was provided?"; Context answers "what's relevant while executing?" — an input may become context, but don't collapse the concepts.
- **State** — current execution condition of the workflow (`current_process, revision_number, evaluation_status, approval_status, failure_status, checkpoint, selected_branch, termination_status`). Answers "where is the workflow now, and what controls what happens next?" State controls execution; Context supports it. State ≠ Memory: `revision_number=2` (current) vs. "Chapter 7 was revised twice last run" (historical).
- **Artifact** — a potentially large/externally-stored result (screenplay, report, audio, image, JSON dataset, video, corpus). Store a reference (`reference: "reviews/chapter_07.json"`), don't repeatedly embed the full content. An artifact becomes Context only via relevant extraction/reference, never wholesale injection.

## Lifetimes & Ownership

| Mechanism | Typical Lifetime | Typical Owner |
|---|---|---|
| Input, Context | Current execution | Process/Task, execution boundary |
| Task output | Current/downstream execution | Process/Task/Crew |
| Flow State | Current workflow execution | Flow |
| Knowledge | Persistent domain/reference | Knowledge system |
| Skill | Persistent methodology | Capability |
| Memory | Across executions/interactions | Memory system |
| Artifact | Persistent until cleanup | Artifact system |
| Checkpoint | Recovery lifecycle | — |

Ownership means responsibility for defining/controlling access, not necessarily physical storage.

## Scoping Per Layer

- **Flow**: needs orchestration info only — `current_process`, process outputs, decision values, iteration counters, approval/failure state, checkpoint info, artifact references. Not every piece of professional context.
- **Process**: gets what its transformation needs (e.g. chapter + story context + evaluation criteria for `evaluate_chapter`) — not all memory/knowledge/previous outputs/Flow state/artifacts by default.
- **Task**: narrower still — explicit `knowledge`, `skills`, `state`, `previous_outputs`, `artifacts` lists derived from the Task contract.
- **Agent**: enough for its professional capability (Knowledge, Skills, Task inputs, relevant state/outputs/artifacts, allowed tools, relevant memory) — but shouldn't become a generic repository for the whole system.
- **Crew**: shared context (chapter, requirements, criteria) + specialist-specific context (Narrative Agent gets Narrative Knowledge, etc.) — specialization without over-propagation.

**Propagation** should follow explicit dependency edges (`Process A → relevant output → Process B`), never "entire execution history → every downstream Process."

## Context Minimality & Relevance

More context ≠ better results — it can add irrelevant info, contradictions, retrieval noise, token cost, latency, reduced attention, ambiguity, accidental capability coupling. Goal: **maximum relevance, minimum unnecessary context.**

Relevance test per item: is it required for this execution? which part of the task requires it? what decision/transformation does it support? could a smaller representation, a reference, or just-in-time retrieval work instead? No good answer → remove it. Model context as an explicit dependency graph (`Task requires → Character Profile, Current Chapter, Evaluation Skill; optionally → Previous Review`), not "Task receives everything."

**Context completeness** (everything required is available) and **context minimality** (nothing unnecessary included) are both required — not "everything," and not "shortest prompt" either. The real optimization target is *minimum sufficient information for reliable execution* — a slightly larger but highly relevant context can outperform a shorter, incomplete one.

## Knowledge & Skill Practice

**Retrieval**: Task Requirement → Knowledge Requirement → Relevant Knowledge → Context → Agent (never "treat a Knowledge source as universally applicable"). **Scope** narrowest-sufficient: System (shared domain) → Crew (collaboration-specific) → Agent (specialization) → Task (operation-specific reference). **Avoid duplication** — don't repeat the same fact across Agent backstory + goal + Task description + Crew context + Knowledge source (e.g. a character's full biography shouldn't live in the Agent backstory if it's already in the Character Knowledge source; backstory = professional identity, Knowledge source = domain facts).

**Skills** attach where the methodology is actually used (Character Editor gets Character Arc Analysis + Behavioral Consistency Analysis; Continuity Editor gets Timeline Verification + Canon Consistency) — not every Skill on every Agent. A Skill provides reusable methodology; the Task still defines the current specific operation.

## Memory Practice

Introduce Memory only when historical information materially improves execution. Scope it (user / Agent / Crew / workflow / project / execution-history) to match intended lifetime/ownership. Retrieve *relevant* memory, not the entire store. Memory *can* interact with Knowledge (a past execution's finding can later be retrieved) but must never silently override authoritative Knowledge.

**Authority hierarchy** when sources conflict (app-specific, but a reasonable default): Explicit Current Input → Authoritative Domain Knowledge → Validated Current State → Validated Process Outputs → Relevant Memory → Unverified Historical/Derived Information. Rule: **historical information must not silently become authoritative domain truth.** If current input contradicts canonical Knowledge (e.g. "for this alternate timeline, age=40" vs. canon age=35), don't resolve silently — apply explicit precedence or surface the conflict. Likewise, current Flow State should never be overwritten by an older value just because Memory contains it.

Memory should never be used to construct an Agent's core professional identity ("You are a Senior Continuity Editor..." belongs in the Agent definition, not Memory).

## Structured Context, Provenance, Freshness

Prefer structured context over prose dumps:
```yaml
context: { chapter_id: "chapter_07", revision_number: 2, evaluation_status: "NEEDS_REVISION", required_focus: [character_consistency, continuity] }
```
Preserve provenance for important items:
```yaml
context_item: { name: character_profile, source: { type: knowledge, reference: characters/arjuna.md }, authority: canonical, required: true }
```
Track freshness: `static | versioned | current | historical | temporary` (story canon = versioned, Flow State = current, previous evaluation = historical, Task context = execution-scoped).

Compress large source material only when semantic fidelity survives — use structured summaries for browsing, but keep the source artifact when exact evidence matters.

## Isolation, Leakage, Security

Information shouldn't cross component boundaries by default — Agent A's private reasoning stays private unless explicitly shared as output; within a Crew, share only intentional common context, not every intermediate result; across a Flow, pass Process A's output to Process C only if C actually needs it.

**Context leakage** to flag: entire Flow State → every Agent; entire Knowledge Base → every Task; entire Crew Output → Flow State; entire Memory → every Process; all MCP schemas → every Agent.

**Capability leakage**: having context *about* a capability (e.g. Publishing API docs as Knowledge) does not grant the *capability* (the actual publish Tool) — reading about something isn't permission to do it.

**Security**: least privilege applies to information, not just tools. Ask who can see this, why, whether it's sensitive, whether it can be minimized/referenced/redacted. For genuinely sensitive data, use architectural access control (classification, access scope, redaction, retention, provenance) — don't rely on Agent instructions like "don't reveal this."

Human gates should receive a decision summary + key findings + relevant artifact + the required decision — not the entire internal execution history.

## Iterative Workflows & Recovery

In a Generate→Evaluate→Revise loop, give each iteration the *current* draft + evaluation + relevant prior constraints + revision number — don't accumulate every prior draft/evaluation in full unless historical comparison is explicitly required.

Recovery needs checkpoint state + relevant Process input + artifact references + failure info + required historical context — not a full reconstruction of the previous execution's context. Checkpointing should preserve workflow state, execution metadata, artifact references, recovery info — not arbitrary prompt dumps; prompt reconstruction should be deterministic where possible.

## Failure Modes

- **Context**: missing, stale, irrelevant, conflicting, oversized, unauthorized, mis-attributed provenance, duplicate, leaked, incorrectly retrieved.
- **Knowledge**: unavailable, version mismatch, conflicting canonical sources, stale, mis-retrieved, insufficient → responses: retry retrieval, pick authoritative source, request human resolution, mark Process inconclusive, terminate (per Process contract).
- **Memory**: unavailable, retrieval failure, irrelevant, contradictory, stale, wrong scope — never treat Memory as mandatory just because it exists.
- **Skill**: missing, wrongly selected, incompatible with Agent, conflicting methodologies, outdated — validate Skill–Agent–Task alignment.

## Information Selection Matrix

| Information | Primary Question | Typical Owner | Typical Lifetime |
|---|---|---|---|
| Input | What was provided? | Process/Task | Execution |
| Context | What is relevant now? | Execution boundary | Execution |
| State | Where are we? | Flow | Execution |
| Knowledge | What is known? | Knowledge system | Persistent |
| Skill | How should we work? | Capability | Persistent |
| Memory | What happened before? | Memory system | Historical |
| Artifact | Where is the large result? | Artifact system | Persistent |
| Output | What did this execution produce? | Process/Task/Crew | Execution/downstream |

**Mechanism selection**: domain facts→Knowledge · reusable methodology→Skill · previous history→Memory · workflow position→Flow State · current execution input→Input · relevant assembled info→Context · large result→Artifact · deterministic transform→Python/Tool · professional semantic work→Agent · specialist collaboration→Crew.

## Context Assembly & Validation Contracts

```yaml
context_assembly:
  execution_id: "" 
  process_id: "" 
  task_id: "" 
  agent_id: ""
  inputs: { required: [], optional: [] }
  state: { required: [] }
  knowledge: { required: [], optional: [] }
  skills: { required: [], optional: [] }
  memory: { required: [], optional: [] }
  previous_outputs: { required: [], optional: [] }
  artifacts: { required: [], optional: [] }
  selection: { rationale: "", filters: [], exclusions: [] }
  validation: { complete: false, conflicts: [], unauthorized: [], stale: [] }
  budget: { token_limit: null, estimated_tokens: null }
  provenance: { enabled: true }
```
```yaml
context_validation:
  status: ""
  completeness: { required_inputs: "", required_state: "", required_knowledge: "", required_skills: "", required_memory: "", required_artifacts: "" }
  relevance: { unnecessary_items: [], excessive_items: [] }
  consistency: { conflicts: [], authority_resolution: [] }
  security: { unauthorized_items: [], redactions: [] }
  freshness: { stale_items: [] }
  efficiency: { token_estimate: null, budget_exceeded: false }
  findings: [{ id: "", severity: "", category: "", message: "", recommendation: "" }]
  approved: false
```
Every important dependency should trace: `Requirement → Process → Task → Required Context → Knowledge/Skill/Memory/State` — this lets Amsha answer "why was this given to this Agent?" and "why was this retained?"

When context is excessive, optimize in order: remove irrelevant → remove duplicated → remove info already available via reliable reference → reduce unnecessary historical context → narrow Knowledge retrieval → narrow Skill attachment → replace embedded artifacts with references → use structured representations → retrieve just-in-time → compress only with fidelity preserved. Never strip *required* information just to cut tokens. Don't assume a larger-context model removes the need for context discipline.

## Crew+Flow / Agent+Task Application

```text
FLOW (minimal execution state) → PROCESS INPUT (relevant requirements/context) → CREW
  (shared context + Agent-specific Knowledge/Skills + relevant Memory) → CREW RESULT → FLOW STATE
```
This mirrors the boundary in `10-crew-flow-architecture.md`. At the Agent+Task level: Agent = persistent professional capability, Task = current bounded operation, Context = information the current operation needs — Task context should never redefine the Agent's professional identity.

**Backstory vs Knowledge vs Skill vs Context** — keep these separate to avoid duplicated prompts: Backstory = who is this professional / experience / perspective; Knowledge = what's true/established in the domain; Skill = how the professional performs the methodology; Context = what matters for *this* execution.

**Static vs dynamic**: Agent role/goal/backstory, Skills, and stable Knowledge are static (configure once); Task input, Flow state, current context, previous outputs, current memory retrieval, artifact references are dynamic (don't bake these into static Agent definitions, and don't regenerate static info dynamically every time).

## Versioning & Reproducibility

Version Knowledge, Skills, Memory references, and architecture (`knowledge: {source: story_bible, version: "3.2"}`, etc.). For important/production executions, be able to reconstruct: architecture version, Agent/Task config, Knowledge/Skill versions, relevant Memory references, Input, Flow State, Artifact references, model configuration.

---

## Final Validation Checklist

**Input**: required inputs available · schema valid · provenance known.
**Context**: complete · relevant · minimal · authorized · consistent · within budget.
**Knowledge**: appropriate · available · authoritative · version-compatible.
**Skills**: appropriate · compatible · available · not duplicated.
**Memory**: relevant · historical · properly scoped · not treated as canonical truth without justification.
**State**: current · owned by Flow · minimal · valid.
**Artifacts**: accessible · correct version · properly referenced · not unnecessarily embedded.

## Anti-Patterns

- **God Context** — everything passed everywhere.
- **God Knowledge** — one massive source serving every capability.
- **Memory as Knowledge** / **Knowledge as Memory** — historical info treated as canon, or domain facts stored only as execution history.
- **Skill as Task** / **Task as Skill** — reusable methodology duplicated into every Task, or a one-off operation treated as reusable methodology.
- **State as Context** / **Context as State** — workflow control info dumped into prompts, or large info objects used to control the workflow.
- **Artifact as Context** — entire files repeatedly injected into prompts.
- **Context without provenance/authority/scope** — Agent can't tell where info came from; conflicts resolved implicitly; everything given to everyone.
- **Memory Dump / Knowledge Dump** — entire historical record or domain corpus injected without retrieval.
- **Capability by Information** — giving info about a tool interpreted as granting permission to use it.

## Final Rules

1. Knowledge = what the system knows about the domain. 2. Skills = reusable ways of working. 3. Memory = retained historical information. 4. Context = relevant information assembled for the current execution. 5. Input = defined by the Process/Task contract. 6. Flow State = current workflow condition. 7. Artifacts = large/persistent execution outputs. 8. Context should be sufficient but minimal. 9. Information crosses boundaries only through explicit dependencies. 10-11. Knowledge/Skills shouldn't be duplicated into Agent identity / every Task unnecessarily. 12. Memory should not silently become canonical Knowledge. 13. State should not become a prompt dump. 14. Artifacts should normally be referenced, not repeatedly embedded. 15. Context should preserve provenance where important. 16. Conflicting authoritative information should be surfaced or resolved by explicit precedence. 17. Security applies to information access as well as tool access. 18. Current state shouldn't be reconstructed from historical Memory unless explicitly required. 19. Narrow large context before compressing it. 20. Prefer deterministic structured context. 21. Every important context dependency should trace to a Process/Task/Agent requirement. 22. Select information mechanisms by semantics, not convenience.

## Final Principle

```text
Knowledge: "What is known?"        Skill: "How should this capability work?"
Memory: "What happened before?"    Input: "What was provided for this execution?"
State: "Where is the workflow now?" Context: "What information matters right now?"
Artifact: "Where is the larger result?"
```

> Amsha should never solve a context problem simply by adding more context. First determine what kind of information is required, where it belongs, how long it should live, who should access it, and whether the current execution actually needs it.

`Right Information → Right Mechanism → Right Scope → Right Time → Right Capability → Minimum Sufficient Context → Reliable Execution`. Context, Knowledge, Skills, Memory, State, Inputs, and Artifacts are explicit architectural primitives, not interchangeable prompt content.
