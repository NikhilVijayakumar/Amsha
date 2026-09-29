---
type: Playbook
title: "Methodology: implementation guides"
description: What the twenty-four implementation topics cover, how they apply per component type, and how authoring rules are enforced.
tags: [amsha, methodology, implementation, mcp]
generated: { by: "opencode/big-pickle", at: 2026-09-29T00:00:00Z }
stale_after: 2026-12-29T00:00:00Z
sources:
  - id: impl-docs
    resource: ../../mcp/src/amsha_mcp/docs/implementation
    title: Packaged implementation documents (topics 00-23)
    author: team:amsha
    last_modified: 2026-09-29T00:00:00Z
---

# Methodology: implementation guides

**This concept describes the guides. It does not contain them.** The
authoritative text is the packaged set under
`mcp/src/amsha_mcp/docs/implementation/` (24 topics), read through the
`get_implementation_guide` MCP tool. Both `get_prerequisite_stage` and
`get_implementation_guide` accept a `summarize` flag that keeps headers and
checklist lines — the structure an agent needs to navigate a long document
without loading all of it.

## What they are for

The implementation guides turn a validated design into files. Where the
[prerequisite stages](./prerequisite.md) decide what to build, these topics
carry the rules for building it: how to write an agent YAML, how to write a
task YAML, how to wire knowledge sources, how to configure tools, how to
structure a crew, and how to run a flow.

## The 80/20 discipline

The single most important convention in this methodology: **most design effort
belongs in the task definition, not in the agent persona.** An elaborate
persona with a vague task produces predictable, mediocre output. A plain
persona with a precise task produces good output. Guidance on agent files
therefore stays short, and guidance on task files carries the detail.

Practically: if an agent definition is growing long while its task is not,
effort is in the wrong place.

## Reading order

Topics 00–09 establish the shared foundations — process, configuration,
structure, the component catalogue. Topics 10+ are per-component-type: agent
authoring, task authoring, tools, knowledge sources, skills, MCP servers, then
crew, flow, evaluation, and observability. An agent that already knows the
foundations can jump straight to the component type it is writing.

`recommend_components` applies this ladder least-powerful-first: deterministic
code before a Task, a Task before an Agent, an Agent before a Crew, a Crew
before a Flow. Each recommendation cites a real reference from the repository
rather than describing an idealised component.

## Verification and the 80/20 discipline in practice

The guide rules are not prose advice. `verify_component` judges one
component — agent, task, crew, flow, knowledge source, skill, tool, or MCP
server — against the methodology rules and returns findings with a severity,
the rule id, the rule's source, a message, and a suggested fix. It is a judge,
not a generator: it never rewrites a component.

`verify_alignment` then checks the relationships: unassigned tasks, unused
agents, domain mismatch, capability gaps, and overlap between components. A
crew can pass every per-component check and still be misallocated, and this
is the check that catches that.

`score_crew` produces a 0–100 rubric score with per-component breakdown, and
`evaluate_design` combines prerequisite completeness with crew checks to
answer whether the assembled crew faithfully realises the validated design —
the join between Phase 2 and Phase 3.

## Writing new material

`suggest_fixes` turns findings into one draft fix per finding, and
`apply_fixes` applies only the approved subset by index. Drafts are proposed,
never written silently — the agent cannot quietly edit a crew on its own
judgement.

## Related

- [Prerequisite](./prerequisite.md) — the design that precedes implementation
- [Proposal](./proposal.md) — how changes to either get recorded
- [Contracts](../contracts/) — the interfaces implementation must satisfy
