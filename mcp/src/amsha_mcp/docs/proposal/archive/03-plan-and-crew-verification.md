# Proposal 03 — Plan & Crew Verification (Phase 3)

| | |
|---|---|
| **Status** | Proposed |
| **Priority** | High — turns the methodology from *guidance* into *enforcement* |
| **Risk** | Medium — must reuse `crew_forge` schemas and never silently rewrite |
| **Effort** | Medium |
| **Depends on** | 01 (Phase 1), 02 (Phase 2 artifact data model) |

## Goal

Given a user's filled prerequisite artifacts **and/or** an actual crew design (as YAML or as a structured plan), judge whether it is correct per Amsha's methodology — and report findings, never silently rewriting. This is the layer between "the LLM wrote YAML" and "something runs."

## What gets verified

Three distinct targets, each with its own rule source:

### 1. Prerequisite artifacts (design intent)

The `problem_definition`, `goal_boundary_definition`, `process_decomposition`, `contracts` and `flow` artifacts from `prerequisite/00–09`. Verified against:

- Well-formedness (schema conformance to the YAML schemas embedded in those docs).
- Completeness (are all processes decomposed? are corner cases enumerated?).
- Internal consistency (goal ↔ boundary ↔ decomposition agree; contracts match the atomicity tests in `03-process-contracts-and-atomicity.md`).

Catching a bad problem definition here is far cheaper than catching a bad Crew after it's built.

### 2. Crew structure (crew_forge YAML)

The final crew YAML as `CrewParser` would read it. Verified against the real `AgentRequest`, `TaskRequest`, `McpServerConfig` schemas (`crew_forge/domain/models/`) — not a parallel schema. Checks:

- Required fields / valid values per the domain models.
- References resolve (task → agent, crew → task/agent, tool → registered tool via `tool_registry.py`).
- Not a God Agent / God Task: bounded responsibility, single-purpose, appropriate delegation.

### 3. Agent / Task / Crew / Flow / Skill / Knowledge verification

Each conceptual component is verified against the professional rules in the implementation docs:

| Component | Rule source |
|---|---|
| Agent | `implementation/01-agent-engineering.md` — bounded persona, no secret/implicit goals, professional capability, correct default (Task-only when a plain function suffices) |
| Task | `implementation/02-task-engineering.md`, `03-atomic-task-design.md` — atomic, single deliverable, context complete, output contract explicit |
| Agent–Task alignment | `implementation/04-agent-task-alignment.md` — the right agent owns the right task; no mismatch |
| Validation | `implementation/05-agent-task-validation.md` — every agent/task validated before assembly |
| Crew | `implementation/06-crew-engineering.md` — genuine collaboration, not a collection of isolatable tasks; `process` param matches what `crew_forge`'s `CrewBuilderService.build()` actually accepts (defaults `Process.sequential` — don't recommend a process type `crew_forge` doesn't wire from YAML) |
| Crew evaluation | `implementation/07-crew-evaluation.md` |
| Flow / CrewFlow | `implementation/09-flow-engineering.md`, `10-crew-flow-architecture.md` — explicit orchestration, no implicit hidden wiring |
| Context / Knowledge / Skills / Memory | `implementation/11-context-knowledge-memory.md` — reference (Knowledge) vs methodology (Skill) use; not stuffing knowledge into agent persona |
| Reasoning & Planning | `implementation/12-reasoning-and-planning.md` |
| Tools / MCP | `implementation/13-python-and-tools.md`, `14-mcp-integration.md` — tool selection least-powerful; MCP config correct |

## Design

### Report, don't rewrite

The absolute rule (mirrors the methodology's own "No Silent Architecture Changes"): a verify tool **returns findings** — severity, rule, reference (doc + section), and a recommended fix — and **never applies them**. An LLM or the user applies fixes. This keeps Phase 3 honest: it is a judge, not a generator.

### Tool surface

| Tool | Input | Returns |
|---|---|---|
| `verify_prerequisite_artifacts` | artifacts (dict or file paths) | Findings per artifact, severity, rule reference |
| `verify_crew_yaml` | crew YAML path or content | Findings vs real `crew_forge` schemas + Crew structure checks |
| `verify_component` | `component_type` (agent/task/crew/flow/skill/knowledge/tool/mcp/llm_model), `definition` | Findings vs the matching implementation doc's checklist |
| `verify_alignment` | agent(s) + task(s) | Agent–Task alignment findings (`04-agent-task-alignment`) |

All return a shared `FindingsReport` shape: list of `{severity, rule_id, rule_source, message, suggested_fix}`.

### Findings are grounded in doc references

Every finding cites its rule source (e.g. "violates `implementation/03-atomic-task-design.md` §composite-task"), so the caller — human or LLM — can read the rule and decide. Findings never stand alone as bare verdicts.

`llm_model` is the one component type sourced from a root `docs/proposal/` doc rather than `mcp/docs/implementation/` — it checks the opt-in `LLMModelConfig.lmstudio_lifecycle` fields against [proposal 14](../../../../docs/proposal/14-llm-lifecycle-management.md) (missing `base_url`, a non-local `base_url`, `model_id`/`model` confusion, unset `context_length`). Added after 14 shipped in `llm_factory`, not part of the original Phase 3 scope.

## Testing bar

- Every check type has a fixture crew (valid) and at least one violating crew (invalid) that must produce the expected findings — no check is untested.
- Negative: a verify call must never mutate the artifact/YAML it reports on (assert file untouched after a call).
- End-to-end over stdio with a real client on a real worst-case crew (God Agent, over-capable agent, misaligned agent/task, implicit flow) — must surface the intended findings.

## Out of scope

- Suggesting fixes autonomously (Phase 4).
- Executing a crew to verify behavior (Phase 4).
- Network/config lateral checks beyond `crew_forge`'s own schemas.

## Why this scope and not more

Ponytail check: could Phase 3 auto-fix violations? Skipped — explicitly forbidden by the methodology (no silent architecture changes). The judge has no red pen.
Ponytail check: could Phase 3 *execute* a crew to verify it runs? No — execution is Phase 4's job, and mixing judgment (should it run right?) with execution (does it run?) muddies both. Keeping them separate matches Phase 2's `verify`/`evaluate` split.