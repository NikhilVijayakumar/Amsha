# Architecture Handoff Checklist

## Purpose

This document bridges the prerequisite architecture layer and the implementation engineering layer. After completing stages 00–08, the approved architecture contract becomes the source of truth for implementation. This checklist verifies the architecture is complete enough to begin building. It is not a new prerequisite stage — it is a handoff artifact.

## Handoff Artifact

The source of truth is the architecture contract defined in `08-architecture-validation.md` section 54. The architecture YAML must include:

```yaml
architecture:
  problem: {}
  goal_boundary: {}
  processes:
    decomposition: {}
    contracts: {}
    validation: {}
  flow:
    structure: {}
    transitions: {}
  state:
    model: {}
    invariants: {}
  failures:
    cases: {}
    recovery: {}
  capabilities:
    selected: {}
    rejected: {}
  validation:
    status: approved
    findings: []
  approval:
    status: approved
  implementation_ready: true
```

All sections must be populated. `implementation_ready` must be `true`.

---

## Pre-Implementation Checklist

Verify each item before handing the architecture to the implementation team.

| # | Check | Prerequisite Stage |
|---|-------|--------------------|
| 1 | Problem definition exists and is approved | 00 |
| 2 | Start and end boundaries are defined | 01 |
| 3 | Scope exclusions are documented | 01 |
| 4 | All processes are identified and decomposed | 02 |
| 5 | Every process has a contract (input, transformation, output) | 03 |
| 6 | Atomicity tests are satisfied for each process | 03 |
| 7 | Process graph is validated (no missing dependencies, no dead ends) | 04 |
| 8 | Semantic validation is complete (LLM-dependent processes) | 04 |
| 9 | Human review gate is passed (if applicable) | 04 |
| 10 | Flow transitions and state model are defined | 05 |
| 11 | Context vs. state boundaries are clear | 05 |
| 12 | Failure paths and recovery strategies are planned | 06 |
| 13 | Corner cases are identified and addressed | 06 |
| 14 | Capabilities are selected with architectural justification | 07 |
| 15 | Rejected capabilities are documented with reasons | 07 |
| 16 | Complete architecture is validated (no ERROR findings) | 08 |
| 17 | `implementation_ready: true` in architecture YAML | 08 |

All 17 items must be checked before implementation begins.

---

## What to Hand the Implementation Team

Hand: **Architecture YAML** (from 08 §54, the source of truth), **this checklist** (all 17 items checked), **accepted assumptions** (documented during prerequisite stages), **WARNING findings** (non-blocking issues that carry forward).

Do not hand: draft or rejected architecture versions, incomplete process contracts, unresolved ERROR-severity findings.

---

## Cross-References

| Document | What It Covers |
|----------|----------------|
| 00-problem-definition.md | Problem definition |
| 01-goal-and-boundary-definition.md | Goals and boundaries |
| 02-process-decomposition.md | Process decomposition |
| 03-process-contracts-and-atomicity.md | Process contracts |
| 04-process-validation-and-human-review.md | Process validation |
| 05-flow-and-state-planning.md | Flow and state |
| 06-corner-cases-and-failure-planning.md | Failures and corner cases |
| 07-capability-selection.md | Capability selection |
| 08-architecture-validation.md | Architecture validation (section 54 for YAML schema) |
| ../implementation/00-amsha-agent-workflow-engineering-principles.md | Implementation boundary (what happens after handoff) |
