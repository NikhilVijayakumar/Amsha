# Proposal 11 — A Claude Code Skill for Crafting Good Amsha Agents/Tasks

| | |
|---|---|
| **Priority** | Can start anytime — no code dependency, most useful after [08](08-agent-task-capability-expansion.md) |
| **Risk** | None — it's a documentation/tooling skill, not a code change |
| **Effort** | Small |
| **Depends on** | Nothing required; richer once [08](08-agent-task-capability-expansion.md) exists |

## The ask

CrewAI's own docs include a dedicated guide, `guides/agents/crafting-effective-agents`, with concrete, non-obvious heuristics for writing good agents and tasks. CrewAI 1.x also has its own "Skills" concept (a `SKILL.md`-based format modeled directly on Claude's Agent Skills — see [07](07-skills-adoption.md)). The user wants a Claude Code skill in *this* repo (`.claude/skills/`) that helps a developer craft good Amsha agent/task YAML definitions, informed by CrewAI's own best-practice guide.

## Heuristics to encode (pulled directly from CrewAI's guide, verified via docs research)

- **80/20 rule**: most design effort should go into task definitions, not agent persona polish.
- **Role**: specific job titles, not generic ones — "Technical Documentation Specialist," not "Writer."
- **Goal**: outcome-focused, embeds quality/success criteria — not just a restatement of the activity.
- **Backstory**: establishes credibility (concrete experience, a stated methodology); must cohere with role/goal — no irrelevant flavor text padding it out.
- **Tasks**: single purpose, single output per task; explicit input/output spec; state *why* the task matters, not just what to do; specify output format explicitly (JSON/markdown/table); include process steps and quality criteria; example outputs where feasible.
- **Common pitfalls table** (directly reusable as a lint checklist): vague instructions → be explicit; "god tasks" doing multiple things → split them; description/output mismatch → align them; assigning tasks the designer hasn't done manually themselves first → do it manually, document the actual process, then encode it; jumping straight to hierarchical process → start sequential, escalate only if genuinely needed; generic agent definitions → produce generic output, so specificity is a functional requirement, not polish.
- **Collaboration design**: complementary (not overlapping) agent skillsets; explicit handoff points between agents in multi-agent tasks.

## Proposal

Create `.claude/skills/craft-amsha-agent/SKILL.md` (or extend the existing `docs/reference/agent/skills/` set — check for naming collision with CrewAI's own "Skills" concept per [07](07-skills-adoption.md)'s warning) that:

1. Supports two modes: a **quick/`--auto` path** that generates a draft immediately from the use-case description (sensible defaults, no interview) for when speed matters, and an **interactive path** that asks clarifying questions first — e.g. what's the single output this task produces, has the developer done this task manually at least once, is this genuinely multi-step (justifying multiple agents) or should it be one agent. Default to quick; interactive is opt-in (`--interview` or similar). Forcing every generation through a Socratic interview undercuts the skill's own value — the discipline (pitfalls checklist) still applies to the quick path's output, it's just applied after generation instead of before.
2. Generates `*_agent.yaml`/`*_task.yaml` pairs matching Amsha's existing `FR-STRUCT` file-naming convention (`agents/*_agent.yaml`, `tasks/*_task.yaml`), pre-filled with role/goal/backstory/description/expected_output written to the standard above — not generic placeholders.
3. Runs the pitfalls checklist above against a *draft* the developer already wrote, when asked to review rather than generate from scratch — "review this agent/task pair" should be a supported mode, not just "generate one."
4. Once [08](08-agent-task-capability-expansion.md) lands, the skill should also know when to recommend the new fields — e.g. suggest `guardrail` when a task's expected_output has a strict format requirement, suggest `context` when a task's description references another task's output, suggest `human_input: true` for tasks the pitfalls table flags as high-stakes/hard-to-automate-safely.
5. Optionally generate a starter CrewAI-native `SKILL.md` (the [07](07-skills-adoption.md) concept) alongside the agent/task YAML when the use case calls for injected domain instructions beyond what fits in a backstory — e.g. a fixed style guide or compliance checklist the agent should always have in context.

## What NOT to do

- Don't make this skill auto-generate and commit files without developer review — per this session's own operating principles, generation should produce a draft the developer inspects before it's treated as final, especially since "assigning tasks you haven't done yourself" is literally one of the pitfalls this skill is meant to catch — the skill should ask the developer whether *they've* done the task manually, not assume its own output is correct because it followed a template.
