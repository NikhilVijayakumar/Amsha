---
name: craft-amsha-agent
description: >-
  Craft, review, or refine Amsha agent/task YAML definitions
  (agents/*_agent.yaml + tasks/*_task.yaml pairs) informed by CrewAI's
  crafting-effective-agents heuristics. Use when the user says "write an
  agent", "draft a task", "make me an agent for <use case>", "review this
  agent/task", "improve my agent definitions", or is about to add a new
  crew to job_config.yaml. Generates drafts (never auto-commits) that follow
  Amsha's file conventions and the 80/20 discipline: most design effort goes
  into the task definition, not agent persona polish.
---

# Craft Amsha Agents & Tasks

A Claude Code skill for producing good Amsha agent/task definitions in
Amsha's file-config format. It encodes CrewAI's own
`crafting-effective-agents` heuristics so drafts are specific by design, and
it reviews drafts the developer already wrote instead of only generating new
ones.

**Naming note (collision with CrewAI Skills):** Amsha 1.x also has a runtime
"Skills" concept — `SKILL.md` directories injected into agents via the
`skills:` YAML field (see `docs/proposal/07-skills-adoption.md`). This skill
is a **Claude Code (dev-time) skill**, not a CrewAI runtime skill. When
generating a CrewAI-native `SKILL.md` (see step 5 below), that file is meant
for the *runtime* agent; never confuse the two.

## Where Amsha configs live

- `<domain_root_path>/<module_name>/` — the module's crew root (from
  `app_config.yaml` `domain_root_path` + `job_config.yaml` `module_name`).
- `agents/<stem>_agent.yaml` — one agent file; top-level `agent:` key.
- `tasks/<stem>_task.yaml` — one task file; top-level `task:` key.
- `skills/<skill_name>/SKILL.md` — optional CrewAI-native runtime skills dir.
- `job_config.yaml` — `crews.<crew_key>.steps[].{task_key, agent_key}` are the
  filename stems: `agent_key: copywriter_agent` resolves to
  `agents/copywriter_agent.yaml`.

A companion crew is a **pair**: the task is what earns the tokens, the agent
is what carries them. Never write one without looking at both.

## The 80/20 rule

Most design effort goes into **task definitions**, not agent persona polish.
A crisp task with an explicit input/output spec and quality criteria elevates
a mediocre agent; a polished backstory cannot rescue a vague task. Sequence a
draft as: use case → task spec → agent that serves it (not the reverse).

## Modes

Default is **quick** — generate a draft immediately from the use case, apply
the discipline afterward. `--interview` opts into a short clarifying pass
first. `review` lints a draft the developer already wrote.

| Flag | Behaviour |
|---|---|
| *(none)* | Draft straight from the use case with sensible defaults. |
| `--interview` | Ask the 3 clarifying questions first, then draft. |
| `review [path]` | Run the pitfalls checklist against existing `*_agent.yaml`/`*_task.yaml` (or a pasted draft); report findings, propose edits. |

Interview questions (only when `--interview`):
1. What is the **single output** this task produces, and in what format (JSON / markdown / table)?
2. Have you **done this task manually** at least once? (If no, do it once, document the real process, then encode it — this is a pitfall, not a nicety.)
3. Is this genuinely **multi-step**, warranting multiple agents with explicit handoffs, or is one agent enough? (Default: one. Escalate to hierarchical only if forced.)

## Crafting rules (encode these into every draft)

- **Role** = specific job title, not a generic label. "Technical Documentation Specialist" not "Writer".
- **Goal** = outcome-focused, embeds quality/success criteria. Not a restatement of the activity.
- **Backstory** = establishes credibility (concrete experience, a stated methodology) and **coheres with role/goal**. No irrelevant flavor text.
- **Task description** = single purpose, single output; explicit input spec; state *why* it matters, not just what to do; include process steps and quality criteria. Reference another task's output by name in `context:` when it depends on one.
- **expected_output** = the exact format (JSON schema shape / markdown structure / table columns), so the task is verifiable.
- One task = one deliverable. If it does two things, split it into two tasks.

## Draft templates

### `agents/<stem>_agent.yaml`
```yaml
agent:
  role: "<specific job title>"
  goal: "<outcome + success criteria>"
  backstory: "<credible, role-aligned experience + methodology, minimal flavor>"
  # Optional (omit to use CrewAI defaults):
  # max_iter: 25
  # allow_delegation: true
  # respect_context_window: true
  # reasoning: true
  # max_reasoning_attempts: 3
  # skills: ["<runtime-skill-name>"]   # resolved to <module>/skills/<name>
```

### `tasks/<stem>_task.yaml`
```yaml
task:
  name: "<one phrase naming the deliverable>"
  description: >
    "<single purpose; explicit input; why it matters; process steps; quality criteria>"
  expected_output: "<exact format — JSON shape / markdown structure / table columns>"
  # Optional (see step 4 for when to suggest these):
  # markdown: true
  # guardrail: "<strict-format rule>"
  # guardrail_max_retries: 2
  # human_input: true
  # context: ["<earlier_task_stem_a>", "<earlier_task_stem_b>"]
  # async_execution: false
```

### `job_config.yaml` wiring
```yaml
crews:
  <crew_key>:
    steps:
      - task_key: "<task_stem>"
        agent_key: "<agent_stem>"
```

## Pitfalls checklist (lint target; use for `review` too)

| Pitfall | Fix |
|---|---|
| Vague instructions ("improve the text") | Be explicit: what change, judged by what. |
| "God task" doing multiple things | Split into one-output-per-task steps; chain with `context:`. |
| Description/expected_output mismatch | Align them — verification reads the pair together. |
| Task the designer hasn't done manually | Do it once manually, document the real process, encode it. |
| Jumps straight to hierarchical/multi-agent | Start sequential and single-agent; escalate only if genuinely forced. |
| Generic agent definition | Specificity is a functional requirement, not polish — generic agents produce generic output. |
| Overlapping agent skillsets in multi-agent teams | Complementary skills; explicit handoff points in each task's description. |
| Backstory not coherent with role/goal | Rewrite to surface concrete experience + method that supports the goal. |

## Step 4 — when to recommend 08-era fields

After drafting, scan for these triggers and suggest the field explicitly:

- **guardrail** — when `expected_output` has a strict format requirement (schema, enum, length). Set `guardrail_max_retries` for LLM-judged guards.
- **context** — when the description references another task's output; wire it by that task's stem.
- **human_input** — for high-stakes / hard-to-automate-safely tasks (money, legal, irreversible side effects).
- **reasoning + max_reasoning_attempts** — for tasks where run-before-saying improves quality materially (multi-hop analysis, contradictions).
- **allow_delegation** — only when another agent could plausibly help; leave off by default.
- **skills** — when the agent needs injected domain instructions beyond backstory space (style guide, compliance checklist).

## Step 5 — optional CrewAI-native `SKILL.md`

Generate `<module>/skills/<skill_name>/SKILL.md` **only** when the use case calls for a fixed body of injected domain instructions (a style guide, compliance checklist, canned methodology) that is too long or too stable to live in a backstory. Keep `SKILL.md` concise (the runtime injects it into the agent's context on every task). Reference its name via the agent's `skills:` field.

## Rules of engagement

- **Never auto-commit or finalize the generated files.** Write them as a draft, summarize what was generated (paths + the 2–3 highest-risk choices), and let the developer review — generation produces a candidate, not a truth. "Assigning tasks you haven't done yourself" is literally one of the pitfalls this skill exists to catch, so don't assume template output is correct because it followed a template.
- Don't invent Amsha keys. If a field isn't in the templates above and isn't verified in `CrewParser`/`CrewBuilderService`, don't emit it.
- If the developer pastes a use case with no module context, ask where the crew root is (`<domain_root_path>/<module_name>/`) before writing files.
- Run the pitfalls checklist on the draft's output *after* quick-mode generation — the discipline applies to the quick path too, it's just applied post-hoc instead of via interview.