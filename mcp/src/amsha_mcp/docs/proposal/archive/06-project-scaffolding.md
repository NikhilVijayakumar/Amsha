# Proposal 06 — Project Scaffolding (New & Existing Projects)

| | |
|---|---|
| **Status** | Proposed |
| **Priority** | High — closes the one confirmed gap in "does Amsha MCP cover everything needed to use Amsha" |
| **Risk** | Medium — writes files into a user's project; must never silently overwrite |
| **Effort** | Medium |
| **Depends on** | 01 (doc/convention reading), 03 (verification — a scaffold must self-verify before being called done) |

## Goal

Phases 1-5 cover *design* (prerequisite methodology), *verification* (does a crew match Amsha's conventions), and *improve/test/evaluate* (does a crew run and score well). None of them help someone **get Amsha into a project in the first place** — pip-installing it and reading the Quick Start is still entirely manual. This proposal adds that missing step for two situations:

1. **New project** — nothing exists yet; generate the config files and directory layout from scratch.
2. **Existing project** — a project already has some structure (maybe even raw CrewAI, no Amsha); detect what's there and wire Amsha in without clobbering it.

## Why this wasn't already covered

`mcp/docs/implementation/22-amsha-project-generation.md` already documents the target shape (`Approved Architecture → Implementation Specification → Project Generation → CrewAI Project`) and is servable today via `get_implementation_guide('22')` — but that's read-only methodology text. Nothing executes it. This proposal is the tool layer on top of that existing doc, the same relationship Phase 2's sequencing tools have to the prerequisite docs.

## Capability 1: New project scaffold

| Tool | Input | Returns |
|---|---|---|
| `scaffold_new_project` | `target_dir`, `module_name`, `llm_provider` (optional) | A **plan** (file list + content), not written files yet |
| `apply_scaffold` | the plan from `scaffold_new_project`, `confirm: bool` | Writes the files only when `confirm=True`; refuses on an existing non-empty target without an explicit `overwrite` flag |

Generates, per `docs/feature/crew_forge/functional.md`'s `FR-STRUCT` conventions (verified against the real spec, not invented):

```text
<target_dir>/
├── config/
│   ├── app_config.yaml
│   ├── job_config.yaml
│   └── llm_config.yaml
└── crew_configs/
    └── <module_name>/
        ├── agents/
        └── tasks/
```

`app_config.yaml`/`job_config.yaml`/`llm_config.yaml` are generated with the minimum valid content the real `AmshaCrewFileApplication` needs to construct without error — not a maximal template dumping every optional field. `llm_provider` (Ollama/LM Studio/OpenRouter/Azure/Gemini) selects which `llm_config.yaml` example block to seed, pulled from the same source `explain_module('llm_factory')` already reads.

**Self-verifying**: `apply_scaffold` runs `dry_run_parse` (Phase 4) against the freshly written directory before reporting success — a scaffold that doesn't parse isn't a valid scaffold, regardless of what it wrote.

## Capability 2: Wire Amsha into an existing project

| Tool | Input | Returns |
|---|---|---|
| `detect_project_state` | `target_dir` | What's already there: Amsha installed? (`pyproject.toml`/`requirements.txt` check), config files present?, existing `agents/`/`tasks/` YAML in Amsha's convention?, raw CrewAI usage with no Amsha wrapper? |
| `add_amsha_to_project` | `target_dir`, `detect_project_state` output | A **plan** for what to add/change — new config files where missing, a suggested `AmshaCrewFileApplication` entry point — never a plan that deletes or rewrites existing user code |

`add_amsha_to_project` only ever proposes **additions** (new files, or a suggested integration snippet to paste) — the same "report, never rewrite" discipline Phase 3/4 already established for verification and fixes. If `detect_project_state` finds raw CrewAI `Agent`/`Task`/`Crew` construction with no Amsha involvement, the plan suggests the equivalent Amsha YAML (using `craft-amsha-agent`'s own generation conventions from `docs/proposal/archive/11-agent-task-crafting-skill.md`) as a **side-by-side draft**, not an automatic migration — the existing code keeps running untouched until the user chooses to switch it over.

## Non-negotiables

- **Never write without an explicit confirm step.** Both `apply_scaffold` and `add_amsha_to_project` return a plan first; a second, explicit call applies it. Mirrors Phase 4's `suggest_fixes` → `apply_fixes` split exactly — this is not a new pattern, it's reusing one already proven.
- **Never overwrite an existing file silently.** A target that already has `config/app_config.yaml` blocks `apply_scaffold` unless `overwrite=True` is passed explicitly, and even then only the specific colliding files, not a directory wipe.
- **Generated config matches the real, current schema** — pull the minimal-valid-shape from the real `AmshaCrewFileApplication`/`FileCrewOrchestrator` constructor requirements and `functional.md`'s `FR-STRUCT`, not a hand-maintained template that can drift from what `crew_forge` actually expects. If `functional.md` changes, this tool's output should change with it (same "read the real thing, don't duplicate it" principle as Phase 1's `docs_loader`).
- **A scaffold is not "done" until it verifies.** `apply_scaffold` chains into `dry_run_parse` (Phase 4) automatically; `add_amsha_to_project`'s output plan should be run through `verify_crew_yaml` before being presented as ready.

## What NOT to do

- Don't auto-migrate raw CrewAI code to Amsha without the user choosing to — that's a bigger, riskier rewrite than this proposal's scope; offering a side-by-side draft is enough.
- Don't generate a maximal config dumping every optional field (memory/checkpoint/tracing/skills/mcp all pre-filled) — a fresh scaffold should be the minimal working shape; Phase 5's `recommend_components` is the tool for "what should I add for this specific need," not this one.
- Don't try to detect and support every possible existing-project shape — start with "no Amsha," "Amsha file-mode already present," and "raw CrewAI, no Amsha." Expand `detect_project_state`'s cases only when a real project shape doesn't fit.

## Testing bar

- `scaffold_new_project` → `apply_scaffold(confirm=True)` on an empty temp dir, then `dry_run_parse` on the result — must report `ok: true` with zero errors.
- `apply_scaffold` on a target with an existing `config/app_config.yaml` and no `overwrite` flag — must refuse, must not touch the file (byte-identical assertion, same pattern as Phase 3's no-mutation test).
- `detect_project_state` against three fixtures: empty dir, dir with a valid Amsha scaffold already, dir with raw CrewAI `Agent(...)`/`Crew(...)` Python and no YAML — each must report the correct state.
- `add_amsha_to_project` on the raw-CrewAI fixture — plan must include a suggested YAML draft and must leave the existing `.py` file untouched.
- End-to-end over stdio, matching every other phase's bar.

## Why this scope and not more

Ponytail check: could this also handle dependency installation (`pip install amsha`)? Skipped — an MCP tool spawning `pip install` inside a user's environment is a much bigger trust/side-effect boundary than writing config files into a project directory the user already pointed the tool at; `get_install_instructions` (Phase 1) already tells the user the one-line command. If a concrete need for automated install appears, it's a separate, explicitly-scoped proposal, not a quiet addition here.
