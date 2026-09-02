# Proposal 05 — User Plan Verification & Component Discovery (Phase 3, addendum)

| | |
|---|---|
| **Status** | Proposed |
| **Priority** | High — closes the loop the user described: "verify the user's prerequisite plan and find the right agent/task/crew/flow/skill/knowledge" |
| **Risk** | Low—Medium — read/verify only; no execution |
| **Effort** | Medium |
| **Depends on** | 02 (artifact data model), 03 (verification engine) |

## Goal

Two capabilities the user explicitly called for:

1. **Verify the user's prerequisite plan.** A user arrives with a partially-formed idea (a natural-language goal, a sketch, a half-written set of prerequisite artifacts). Verify not just that artifacts are *well-formed* (Phase 3 does that) but that the *plan itself* is coherent: is the goal achievable within the stated boundary? Is the decomposition complete? Does the flow/state plan match the contracts?

2. **Find the right component for the user's situation.** Given where the user is in the plan, surface the correct Amsha capability — the specific Agent, Task, Crew, Flow, Skill, Knowledge, Tool, or MCP configuration that best implements the validated step — *grounded in what Amsha already ships*, not invented ad hoc.

## Capability 1: verify the user's prerequisite plan

Extends Phase 3's `verify_prerequisite_artifacts` from *structural* to *semantic* verification:

| Tool | Input | Returns |
|---|---|---|
| `verify_user_plan` | prerequisites (artifacts and/or natural-language plan) | Coherence findings: goal vs boundary, decomposition completeness, contract/flow agreement, failure-plan coverage (per `prerequisite/06`) |

The working rule: a plan passes when its goal, boundary, decomposition, contracts, and failure planning **mutually agree** and its decomposition covers the stated goal within the boundary. Findings cite the prerequisite doc + section, like Phase 3.

This is read-only: it returns findings, never rewrites the user's plan.

## Capability 2: component discovery / recommendation

After a plan passes, the user needs "which piece of Amsha realizes *this* step." This is a **discovery** tool, not an executor:

| Tool | Input | Returns |
|---|---|---|
| `recommend_components` | validated step / responsibility | The Amsha-native components that fit, each with: purpose, config keys, matching `docs/` + `implementation/` reference, and the least-powerful option flagged first |
| `find_agent` / `find_task` / `find_flow` | capability needs (e.g. "summarize documents") | Existing Amsha patterns / YAML templates embodying that capability, plus where to wire them |

Rules:

- **Least-powerful first.** Recommendations are ordered Task-only → Agent → Crew → Flow, exactly like the methodology's capability selection. A plain `Task` that can call a tool is recommended before an `Agent` wrapping it.
- **Grounded in Amsha.** Recommendations reference real Amsha knowledge sources (`amsha_crew_docling_source`, `amsha_json_knowledge_source`), real tool registry entries (`tool_registry.py`), and real MCP config (`McpServerConfig`). No invented capabilities.
- **Reference before methodology.** `implementation/11` distinguishes looking things up (reference) from embedding them (methodology). Discovery recommends *references* — pointers to the docs and the real schema — never silently memorizing a person or stuffing knowledge into the agent.

## Relationship to the rest

- Depends on Phase 3's artifacts + verification so discovery only runs on a *validated* plan (avoid recommending against a broken decomposition).
- Feeds Phase 4: what discovery recommends is what `suggest_fixes` drafts and `smoke_test` later runs.

## Non-negotiable

- Discovery is **read-only** and returns findings/recommendations + references. It never writes a crew, never edits a plan, never applies a fix. The user or calling agent does the writing.

## Testing bar

- A clearly-incoherent plan (goal exceeds boundary; decomposition omits a stated goal's step) must be rejected with findings naming the mismatch.
- Discovery on "summarize a directory of PDFs" must recommend Task-with-Docling (least-powerful) ahead of any Agent, and cite `crew_forge/knowledge/amsha_crew_docling_source.py` + the relevant `implementation/` doc.
- Read-only assertions: calling any verify/recommend tool against a plan must leave the plan bytes untouched.

## Why this scope and not more

Ponytail check: could discovery just return a raw YAML template to copy? Skipped — a bare template is a trap (silently embeds a design the user didn't validate). Discovery returns the *component + reference + reason*, and the user decides. Templates belong in Phase 4's `suggest_fixes` as drafts, where they are explicitly reviewed.