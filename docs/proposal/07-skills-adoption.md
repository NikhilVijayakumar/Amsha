# Proposal 07 — Adopt CrewAI Skills

| | |
|---|---|
| **Priority** | Phase 4 |
| **Risk** | Low — additive, net-new concept |
| **Effort** | Small-Medium |
| **Depends on** | [02](02-crewai-version-migration.md), [08](08-agent-task-capability-expansion.md) |

## What a CrewAI Skill is

A **Skill is not a Tool.** Tools are callable actions ("what to do"); Skills inject instructions/context ("how to think"). A Skill is a directory containing a `SKILL.md` file (YAML frontmatter: `name`, `description` required; optional `license`, `compatibility`, `metadata`) plus markdown instructions — directly modeled on Claude's own Agent Skills format (the same pattern this Claude Code session's `.claude/skills/` directories use). Attached via `Agent(skills=["./skills"], tools=[...])`; can also be set crew-wide, with agent-level skills overriding on a name clash. This is **entirely absent from CrewAI 0.201.1** — genuinely new, not a rename of something Amsha already partially has.

## Current state in Amsha

No concept of this at all — `AgentRequest` has no `skills` field, `CrewBuilderService.add_agent()` has no `skills` parameter.

## Proposal

1. Add `skills: Optional[List[str]] = None` to `AgentRequest` (paths to skill directories), threaded through in `CrewBuilderService.add_agent()` to `Agent(skills=agent_details.skills or [])`.
2. Since Amsha already has a YAML-based "configuration as code" model for agents/tasks (`docs/feature/crew_forge/functional.md`, FR-STRUCT), extend that convention: a `skills/` sibling directory next to `agents/` and `tasks/` within each use-case directory, referenced by name from an agent's YAML rather than a raw filesystem path — consistent with how Amsha already resolves `agents/*_agent.yaml` and `tasks/*_task.yaml` by convention.
3. This pairs directly with [11](11-agent-task-crafting-skill.md) — the proposed Claude Code skill for crafting good Amsha agents/tasks can itself model the SKILL.md pattern, and could even generate starter `SKILL.md` files for domain-specific agent skills as part of scaffolding a new use case.

## What NOT to do

- Don't conflate this with Amsha's own MongoDB "sync" concept or with Amsha's `docs/reference/agent/skills/*.md` (those are Claude Code project-development skills for working *on* Amsha's own codebase — a completely different thing from CrewAI agent Skills, which are runtime capabilities *for the agents Amsha builds*). Naming collision risk — call out clearly in docs which "skill" is meant where.
