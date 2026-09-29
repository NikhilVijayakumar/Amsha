---
type: Playbook
title: "Methodology: prerequisite design stages"
description: What the ten prerequisite stages are for, when an agent walks them, and what each one must produce.
tags: [amsha, methodology, design, mcp]
generated: { by: "opencode/big-pickle", at: 2026-09-29T00:00:00Z }
stale_after: 2026-12-29T00:00:00Z
sources:
  - id: prereq-docs
    resource: ../../mcp/src/amsha_mcp/docs/prerequisite
    title: Packaged prerequisite documents (stages 00-09)
    author: team:amsha
    last_modified: 2026-09-29T00:00:00Z
---

# Methodology: prerequisite design stages

**This concept describes the methodology. It does not contain it.** The
authoritative text is the packaged set under
`mcp/src/amsha_mcp/docs/prerequisite/`, which ships inside the
`amsha-mcp` wheel and is read through the `get_prerequisite_stage` MCP tool.
Copying it here would create a second copy that goes stale on the next
`amsha-mcp` release — the exact duplication this bundle exists to remove.

## What the stages are for

Amsha requires a crew to be **designed before it is written**. The ten
prerequisite stages are that design process, walked in order. They exist
because the expensive failure in a CrewAI project is not a crew that fails to
run — it is a crew that runs and produces the wrong thing, discovered after
the orchestration, prompts, and evaluation are already built.

Each stage produces one artifact. The artifacts accumulate into a validated
design, and only then does YAML get written.

## When an agent walks them

An agent enters these stages from `begin_architecture_session`, which takes a
problem statement and returns a session id plus the first stage to fill. From
there the loop is:

1. `get_prerequisite_stage(stage)` — read what this stage must contain
2. `submit_stage_artifact(stage, artifact)` — submit the artifact
3. On acceptance, `write_prerequisite_stage_doc` persists it to the repository
4. `current_stage(session_id)` — report where the session now stands

Stage 07, capability selection, is **deferred**: it is not submitted
mechanically but chosen deliberately, via
`get_least_powerful_capability`, which refuses until stages 00–06 have passed.
The ladder runs deterministic → Task → Agent → Crew → Flow, and the point of
the tool is to present that as a decision rather than a menu.

## The stages

| Stage | Artifact | Purpose |
|---|---|---|
| 00 | Problem definition | What problem is being solved, for whom |
| 01 | Goal and boundary | The goal, and explicitly what is out of scope |
| 02 | Process decomposition | The work broken into processes |
| 03 | Process contracts and atomicity | Inputs, outputs, and atomicity per process |
| 04 | Process validation and human review | Human confirmation the decomposition is right |
| 05 | Flow and state planning | How the processes compose into a flow, and what state moves between them |
| 06 | Corner cases and failure planning | What happens when each process fails |
| 07 | Capability selection | Which capability each process needs (deferred) |
| 08 | Architecture validation | Does the assembled design hold together |
| 09 | Handoff checklist | Final gate before implementation |

Stages 03, 05, and 06 are the ones that change behaviour most often. Stage 03
fixes the data contracts that everything downstream depends on; a contract
changed after implementation is expensive. Stage 06 is where failure handling
is decided, and it is the stage most often under-specified.

## Validation

`verify_prerequisite_artifacts` checks a set of artifacts for completeness
and cross-stage consistency — that the process decomposition, the contracts,
and the flow actually agree with one another. `verify_user_plan` extends this
semantically, checking the goal stays inside the declared boundary and that
every stated goal step is covered by the decomposition.

Both are structural, and deliberately so: they judge form and agreement, not
design quality. Design quality is Phase 3 of the MCP methodology, scored
separately by `evaluate_design`.

## Relationship to the other two methodologies

- [Prerequisites](./prerequisite.md) decide *what* to build. This concept.
- [Implementation](./implementation.md) decides *how* to build it — topics
  00–23 cover the authoring rules per component type.
- [Proposals](./proposal.md) record *why* a change was made, and are the
  durable history this bundle draws on.

A crew is designed here first, implemented per the implementation guide, and
changes to either are recorded as proposals.

## Note on a resolved defect

`_stage_content()` in `architecture.py` reconstructed a path into
`mcp/docs/prerequisite/`, a directory that does not exist, and swallowed the
resulting `OSError` as an empty string. Every architecture session therefore
received blank stage guidance. Fixed under the OpenSpec change
`mcp/openspec/changes/fix-mcp-documentation-discovery/`, which routes through
the loader accessor instead.
