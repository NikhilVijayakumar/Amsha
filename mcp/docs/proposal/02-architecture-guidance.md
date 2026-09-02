# Proposal 02 — Architecture Guidance (Phase 2)

| | |
|---|---|
| **Status** | Proposed |
| **Priority** | High — this is the design-time governance core of Amsha MCP |
| **Risk** | Low — read-only, no crew execution, no mutation |
| **Effort** | Medium |
| **Depends on** | [01-mcp-server-foundation.md](01-mcp-server-foundation.md) (Phase 1 tool surface) |

## Goal

Drive an LLM through the **prerequisite → implementation** discipline stage-by-stage before it writes a single line of crew YAML. Phase 1 (`get_prerequisite_stage`, `get_implementation_guide`) answers *"give me the content of doc N."* Phase 2 turns that content into a *sequence* with session position, so the assistant can never skip "identify the problem" and jump straight to "create three agents."

## Why this exists

The prerequisite docs (00–09) and implementation docs (00–23) encode a strict order:

```text
Problem definition (00)
  → Goal & boundary (01)
  → Process decomposition (02)
  → Contracts & atomicity (03)
  → Flow & state planning (05)
  → Corner cases & failure planning (06)
  → then capability selection: the least-powerful mechanism that suffices
```

An LLM given only Phase 1 tools can *read* those docs, but nothing enforces the order. Phase 2 adds **sequencing**: a session has a position, each stage gates the next, and capability selection is deferred until the decomposition is validated.

## Design

### Session position, not free-form

Phase 2 maintains a per-conversation cursor (in-memory; no persistence needed in Phase 2). Tools:

| Tool | Input | Returns |
|---|---|---|
| `begin_architecture_session` | `problem_statement` (free text) | `session_id`, the FIRST prerequisite stage (`00`), and its checklist |
| `submit_stage_artifact` | `session_id`, `stage` | Validates the filled artifact structurally; if valid, returns the NEXT stage + checklist; if not, returns which checklist items are unmet |
| `current_stage` | `session_id` | Where in the methodology the session is, plus history of completed stages |
| `get_least_powerful_capability` | `session_id` | After decomposition stages pass, returns the capability-selection guidance (Task-only → Agent wrapping → Crew orchestrator → Flow/CrewFlow) as a decision, not a menu |

The characteristic move: `submit_stage_artifact` **gates** — a session cannot advance to dependency selection before its Process decomposition and atomicity checks pass.

### Reuse, don't rewrite

- Stage artifacts and their composite `problem_definition` / `goal_boundary_definition` schemas are exactly those defined inside `prerequisite/00–09`.
- Stage checklists are the ones already embedded in each prerequisite/implementation doc.
- `get_prerequisite_stage` / `get_implementation_guide` from Phase 1 remain the underlying readers; Phase 2 adds order and state on top (the seam 01 explicitly left open for this).

### Deferred capability selection

The methodology's core discipline (see "What Amsha MCP governs" in 00) is that capability selection is the **last** design decision. Phase 2 reflects this: the LLM is not offered "Task vs Agent vs Crew vs Flow" until decomposition + contracts + failure planning pass. `get_least_powerful_capability` presents the selection as a *conclusion derived from the validated decomposition*, not a free choice among equal options.

## What verification exists in Phase 2 (before Phase 3 tools land)

Phase 2 does *structural* validation only — it checks that a filled artifact exists and has the required fields and that checklists are self-reported as met. It does NOT judge whether a decomposition is *good* (that is Phase 3). This is intentional: Phase 2 wires the sequence and the data model; Phase 3 wires the judgment.

## Testing bar

- End-to-end: a full scripted session from `problem_statement` → each stage → least-powerful capability, exercised over the stdio transport with a real MCP client.
- Negative: attempting to request capability selection before the decomposition stages pass must be refused with a pointer to the unmet stages.
- Reuse Phase 1's test harness rather than starting a second one.

## Out of scope

- Verifying design quality (Phase 3).
- Executing or rerunning anything (Phase 4).
- Persisting sessions across restarts (in-memory cursor is sufficient at this stage).

## Why this scope and not more

Ponytail check: could Phase 2 also *auto-fill* a user's artifacts from their natural-language problem statement? Skipped — auto-filling is exactly the kind of silent rewrite the methodology forbids (the artifacts are the user's design commitments, not machine guesses). Phase 2 asks the user to author them, guided by checklists, and only validates structure. If auto-authoring is wanted later, it belongs in Phase 4's improve loop as an *explicit, reviewed* suggestion — never a silent fill.