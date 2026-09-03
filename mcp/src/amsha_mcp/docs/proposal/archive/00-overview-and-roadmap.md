# Amsha MCP — Overview & Roadmap

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-09-03 |
| **Author** | Nikhil (compiled with Claude) |
| **Scope** | What Amsha MCP is, why it exists, what it governs, and the phased build order |
| **Depends on** | Nothing — this is the top-level proposal in the `mcp/` series |

## The problem

Amsha (`E:\Python\Amsha`) is a library: install it, write YAML, call `AmshaCrewFileApplication`, get a running CrewAI crew. Knowing *how* to use it well — which modules exist, what each does, how to configure Tools/MCP/Skills/Knowledge/Memory, and how to *design* a crew correctly rather than just write one — currently means reading `README.md`, `docs/`, `USER_GUIDE.md`, `AGENTS.md`, and the `mcp/docs/` methodology by hand.

Two distinct kinds of knowledge are trapped in markdown:

1. **What Amsha is and how to use it** — the modules (`crew_forge`, `crew_monitor`, `execution_runtime`, `execution_state`, `llm_factory`, `output_process`, `common`, `configuration`, `utils`), installation, configuration, quickstart. Documented in `README.md`, `docs/`, `pyproject.toml`.
2. **How to design a crew correctly** — the methodology: understand the problem, decompose it into Processes, select the least-powerful capability, and only then reach for Agent/Task/Crew/Flow. Documented in `mcp/docs/prerequisite/` (00–09) and `mcp/docs/implementation/` (00–23).

A coding assistant (Claude Code or otherwise) has no structured way to query either. It either has the docs pasted in or it doesn't.

## The proposal

**Amsha MCP** is a bridge that turns both bodies of knowledge into a **queryable, executable governance interface**. It is its own package under `mcp/` (independent `pyproject.toml` + `src/`, stdio transport). It serves Amsha's own documentation at query time, and — crucially — it **walked an LLM through the prerequisite→implementation discipline before the LLM writes a single line of crew YAML**.

The design-time load-bearing idea, stated plainly:

> **`crew_forge` (`src/nikhil/amsha/crew_forge`) is the *runtime* — it parses YAML (`CrewParser`), builds CrewAI objects (`CrewBuilderService`, `AgentRequest`/`TaskRequest`/`McpServerConfig`), and executes them (`FileCrewOrchestrator`, `FlowCrewPipeline`). It has no opinion on whether the crew it builds is well-designed — it will happily build a God Agent if you hand it one.**
>
> **Amsha MCP is the *design-time governance layer* in front of that runtime.** Before any crew is authored, the problem, goal, boundary, and Process decomposition are identified, validated, and approved; capabilities are selected as the least-powerful sufficient mechanism; only then does implementation begin.

So the shape of every Amsha MCP-assisted workflow is:

```text
User problem
   ↓
Amsha MCP — prerequisite guidance (problem → goal → boundary → processes → contracts → flow → capabilities)
   ↓
Validated crew PLAN (prerequisite artifacts)
   ↓
Amsha MCP — implementation guidance (map plan → Agent/Task/Crew/Flow/Skill/Knowledge)
   ↓
crew_forge YAML                          ← the actual runtime schemas, not invented ones
   ↓
AmshaCrewFileApplication → FileCrewOrchestrator → running crew
   ↓
Observe, test, evaluate, improve        ← verify the plan was actually right
```

## What Amsha MCP governs

Amsha MCP covers the full lifecycle of building a crew well, not just "how do I install it":

- **Amsha knowledge** — modules, install, config, quickstart (Phase 1).
- **Architecture guidance** — the prerequisite + implementation methodology, stage by stage, so the LLM designs before it writes (Phase 2).
- **Plan verification** — validate a user's prerequisite artifacts *and* their proposed crew design against the checklists embedded in the methodology (Phase 3).
- **Agent / Task / Crew / Flow / Skill / Knowledge verification** — each component checked against the professional-capability, bounded-operation, genuine-collaboration, explicit-orchestration, and reference-vs-methodology rules in the implementation docs (Phase 3).
- **Improve / Test / Evaluate loop** — turn findings into concrete fix suggestions, smoke-test the generated crew through the real `crew_forge` orchestrator, and score quality (Phase 4).

The common thread: **Amsha MCP makes everything related to building a crew EASIER to build via MCP tools, by encoding the design discipline as tool calls instead of hoping the LLM read the docs.**

## Relationship to `crew_forge`

Amsha MCP and `crew_forge` are complementary, not overlapping:

- `crew_forge` = **runtime** (build + execute). It validates only that YAML *parses and instantiates*; it does not judge design quality.
- Amsha MCP = **design-time governance** (problem → architecture → validated plan → implementation spec). It judges whether a design is *right* before anything is handed to `crew_forge`.

This mirrors the division already laid out in `mcp/docs/implementation/00-amsha-agent-workflow-engineering-principles.md` and the rest of the implementation series: architecture before implementation, validation before generation.

## Package structure

`mcp/` is an independent, installable, deployable package — separate from the root Amsha library. It is a server process, not a dependency `crew_forge` imports. Transport is **stdio**, consistent with Amsha's own stdio-preferred stance for MCP clients.

## Phased roadmap

| Phase | Name | Delivers | Status |
|---|---|---|---|
| 1 | [Knowledge Server](01-mcp-server-foundation.md) | stdio MCP exposing Amsha's own docs — modules, install, config, quickstart, prerequisite/implementation methodology | Proposed |
| 2 | [Architecture Guidance](02-architecture-guidance.md) | Sequencing tools that drive the LLM through prerequisite→implementation stage-by-stage, tracking where in the methodology the session is | Proposed |
| 3 | [Plan & Crew Verification](03-plan-and-crew-verification.md) | Given prerequisite artifacts and/or crew YAML, validate structure + Amsha conventions, including Agent/Task/Crew/Flow/Skill/Knowledge verification against the checklists | Proposed |
| 3b | [User Plan Verification & Component Discovery](05-user-plan-verification-and-component-discovery.md) | Extends Phase 3 from structural to semantic plan verification, plus least-powerful-first component recommendation grounded in real Amsha sources | Proposed |
| 4 | [Improve / Test / Evaluate Loop](04-improve-test-evaluate-loop.md) | Turn Phase 3 findings into concrete fix suggestions; smoke-test through the real `crew_forge` orchestrator; score the result | Proposed |
| 6 | [Project Scaffolding](06-project-scaffolding.md) | New-project generation and existing-project detection/wiring — the "get Amsha into a project" step none of the other phases cover | Proposed |

## Sequencing

Strictly sequential — each phase's tools are built *from* the previous phase's content, not independently:

- **1 before 2** — Phase 2's guidance tools are structured views over the same `mcp/docs/` content Phase 1 already knows how to load and serve.
- **2 before 3** — Phase 3's validation rules are the checklists already embedded in the Phase 2 methodology docs. Don't invent a second rule set.
- **3 before 3b** — component discovery only runs against a plan Phase 3 has already validated; recommending against a broken decomposition is worse than not recommending at all.
- **3 (+3b) before 4** — can't suggest a fix or score a run before there's a validator producing findings to act on.
- **1 and 3 before 6** — scaffolding reads Amsha's real conventions the same way Phase 1 does, and every scaffold self-verifies through Phase 3/4's `dry_run_parse` before being reported as done.

## Non-negotiables

- **Reuse `crew_forge`'s real schemas, don't invent parallel ones.** Phase 3+ validation tools speak in terms of the actual `AgentRequest`, `TaskRequest`, `McpServerConfig` fields (`crew_forge/domain/models/`) and the actual YAML shape `CrewParser` accepts — not a redesigned schema that drifts from what `crew_forge` actually executes.
- **Knowledge tools (Phase 1–2) are read-only.** They serve `mcp/docs/`, `docs/`, `README.md`, `USER_GUIDE.md`, `AGENTS.md` from disk at query time — no copying doc content into Python source, so docs stay the single source of truth.
- **Validation tools (Phase 3+) never silently rewrite a plan or YAML.** Report findings + recommendations; let the user or calling agent apply them. The prerequisite/implementation docs themselves mandate this for validators.
- **Phase 4's test/run tools call the real `crew_forge` orchestrator**, not a simulation — a smoke test that doesn't exercise `AmshaCrewFileApplication`/`FileCrewOrchestrator` proves nothing about whether the generated crew actually runs.
- **stdio only, for now.** HTTP/SSE transports are out of scope until a concrete need appears.

## Open questions

- Should Phase 3 verification run against the *prerequisite artifacts* (the YAML schemas inside `prerequisite/00-09`), the final crew YAML, or both? Leaning toward both — catching a bad problem definition early is cheaper than catching a bad Crew after it's built.
- Should Phase 3 verify *architecture conceptual components* (Agent/Task/Crew/Flow/Skill/Knowledge) as independent objects before they are assembled into YAML, or only as assembled in the final crew? Leaning toward both.
- Does Phase 1 need its own doc-search index, or is plain keyword grep over `mcp/docs/` + `docs/` sufficient (~15k lines)? Starting with grep; revisit if it's not good enough.