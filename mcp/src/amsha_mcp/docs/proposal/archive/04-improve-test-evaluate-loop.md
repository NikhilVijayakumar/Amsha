# Proposal 04 — Improve / Test / Evaluate Loop (Phase 4)

| | |
|---|---|
| **Status** | Proposed |
| **Priority** | Medium — the value multiplier on top of verification |
| **Risk** | Medium+ — executes the real orchestrator, so the failure surface is real crews in real systems |
| **Effort** | Larger |
| **Depends on** | 01, 02, 03 (by design — you can't improve/score a plan before you can verify it) |

## Goal

Close the loop the methodology always intends: build → verify → **run** → **observe** → **improve**. Phase 3 says *what is wrong with the design*. Phase 4 says (a) *here is a concrete fix*, (b) *let's actually run it against the real orchestrator to see if it works*, and (c) *here is how good the result is*.

## The three sub-loops

### 1. Improve — findings → concrete fix suggestions

Phase 3 produces `FindingsReport`. Phase 4's improve tools turn each finding into an actionable, *draft* change:

| Tool | Input | Returns |
|---|---|---|
| `suggest_fixes` | `FindingsReport` | Drafted fix per finding (a corrected YAML fragment, a re-scoped task, a realigned agent) — **proposed, never applied** |
| `apply_fixes` | suggestions (user-approved) | Applies only the fixes the caller explicitly approves; produces a diff |

The line on "auto-authoring": earlier proposals deflected filling artifacts to Phase 4; here it is allowed *only* as an explicit, reviewed suggestion. `apply_fixes` never acts unilaterally.

### 2. Test — smoke-test through the real orchestrator

A smoke test that doesn't exercise `AmshaCrewFileApplication` / `FileCrewOrchestrator` proves nothing about whether the generated crew runs. Phase 4 runs the **real** path:

| Tool | Input | Returns |
|---|---|---|
| `smoke_test` | crew YAML + minimal context | Executes via `AmshaCrewFileApplication` → `FileCrewOrchestrator` with a small, bounded input; returns pass/fail + traceback |
| `dry_run_parse` | crew YAML | Runs `CrewParser` only (no execution) — fastest possible gate: does it even build? |

`smoke_test` is bounded by design — a deliberately small context and hard timeout — so it exercises the plumbing without pretending to be a production run. "Runs at all" ≠ "is well-designed": correctness of the result is evaluated under sub-loop 3.

### 3. Evaluate — score the result

| Tool | Input | Returns |
|---|---|---|
| `score_crew` | crew YAML + (optional) smoke-test output | A score against the evaluation rubric |
| `evaluate_design` | prerequisite artifacts + crew YAML | Design-quality score: does the assembled crew faithfully realize the validated design? (the Phase 3 checks rolled into scores) |

The rubric is drawn from the implementation docs' evaluation content (`implementation/07-crew-evaluation.md` and the checklists throughout 00–23), reused, not redefined.

## Design principles

- **Reuse verified schemas.** Phase 3's validation is the engine; these tools summon it and add fix-draft/test/score on top.
- **Never confuse "runs" with "right."** `smoke_test` and `score_crew` are separate tools for exactly that reason. Passing a smoke test earns no design score by itself.
- **Bounded execution.** Smoke tests always run with a hard timeout and minimal context, described as such in the returned envelope (no partner-API/external-network calls unless the user explicitly opts in).
- **Improve is opt-in-revertible.** `apply_fixes` produces a git-visible diff; nothing is committed silently.

## Testing bar

- A fixture crew that fails `scaffolding` must be caught by `dry_run_parse`.
- A fixture that parses but is structurally broken must be surfaced by `smoke_test`, not silently swallowed.
- `suggest_fixes` on a God-Agent report must produce a valid re-scope draft; `apply_fixes` on an unapproved suggestion must be a no-op (asserts).
- End-to-end over stdio with a real `AmshaCrewFileApplication` run on a fixture crew.

## Out of scope

- Production-grade telemetry/monitoring (that's `crew_monitor`'s domain in the runtime).
- Network-touching capabilities inside a smoke test by default.
- Auto-generating a crew from nothing — Phase 4 improves, scores, tests; it never fabricates a design whole-cloth.

## Why this scope and not more

Ponytail check: could `smoke_test` and `score_crew` be one tool? No — they answer different questions ("does it run?" vs "is it right?"), and conflating them is exactly the failure the methodology warns about. Keep them separate.