# Proposal 01 — MCP Server Foundation (Phase 1: Knowledge Server)

| | |
|---|---|
| **Status** | Proposed |
| **Priority** | High — everything in `00-overview-and-roadmap.md` Phases 2–4 builds on this |
| **Risk** | Low — read-only, no crew execution, no mutation |
| **Effort** | Small |
| **Depends on** | Nothing (first proposal in the `mcp/` series) |

## Goal

A minimal stdio MCP server, installable independently of the root Amsha package, that answers: *what is Amsha, what modules does it have, how do I install it, how do I configure feature X, and what's the design methodology I should follow before I write crew YAML.*

Out of scope for this proposal: anything that reads or validates a *user's* crew YAML (that's Phase 3), anything that executes a crew (Phase 4), anything beyond stdio transport.

## Package layout

```text
mcp/
├── pyproject.toml
├── src/
│   └── amsha_mcp/
│       ├── __init__.py
│       ├── server.py            # stdio entrypoint, tool registration
│       ├── docs_loader.py       # reads mcp/docs/, ../docs/, ../README.md etc. from disk
│       └── tools/
│           ├── __init__.py
│           ├── modules.py       # list_amsha_modules, explain_module
│           ├── install.py       # get_install_instructions, get_quickstart
│           ├── methodology.py   # get_prerequisite_stage, get_implementation_guide
│           └── search.py        # search_amsha_docs
└── tests/
```

Independent `pyproject.toml` — this is a separate installable/runnable package, not a subpackage of `nikhil.amsha`. It may declare `Amsha`'s repo as a sibling on disk (relative path reads via `docs_loader.py`) but does not import `crew_forge` in Phase 1.

## `pyproject.toml` sketch

```toml
[project]
name = "amsha-mcp"
version = "0.1.0"
description = "MCP server exposing Amsha's features, modules, and crew-design methodology."
requires-python = ">=3.12,<3.14"
dependencies = [
    "mcp>=1.0.0",   # official MCP Python SDK — confirm exact pin at implementation time
]

[project.scripts]
amsha-mcp = "amsha_mcp.server:main"
```

## Data source: read from disk, don't duplicate

`docs_loader.py` resolves paths relative to the `mcp/` package root and reads content live from:

- `../README.md`, `../USER_GUIDE.md`, `../AGENTS.md`, `../pyproject.toml` (install/deps)
- `../docs/` (feature, reference, integration-guide)
- `./docs/prerequisite/00-*.md` … `09-*.md`
- `./docs/implementation/00-*.md` … `23-*.md`

No content gets copied into Python source. If a doc changes, the server's answers change on next call — no rebuild step, no drift between "what the docs say" and "what the tool returns."

## Initial tool surface

| Tool | Input | Returns |
|---|---|---|
| `list_amsha_modules` | — | Every module under `src/nikhil/amsha/` (`crew_forge`, `crew_monitor`, `execution_runtime`, `execution_state`, `llm_factory`, `output_process`, `utils`) with a one-line purpose pulled from README's Key Features section |
| `explain_module` | `module_name` | Detailed explanation, relevant config keys, and a pointer to the matching `docs/` section |
| `get_install_instructions` | — | `pip install amsha`, optional `docling` extra, Python version constraint (`>=3.12,<3.14`) |
| `get_quickstart` | — | The Quick Start code block from `README.md` |
| `get_prerequisite_stage` | `stage` (`00`–`09`) | Full or summarized content of that prerequisite doc |
| `get_implementation_guide` | `topic` (`00`–`23`) | Full or summarized content of that implementation doc |
| `search_amsha_docs` | `query` | Keyword matches across `mcp/docs/` + `docs/` + top-level `.md` files, with file/line references |

`get_prerequisite_stage` and `get_implementation_guide` are the seam Phase 2 builds on — Phase 2 doesn't replace them, it adds *sequencing* tools that call these in the right order and track where in the methodology the current session is.

## Testing bar

Matches the standard the main Amsha repo already holds itself to (`docs/proposal/00-overview-and-roadmap.md`, "Non-negotiables carried over from Round 1"): verify against a **real stdio client**, not just unit tests calling the Python functions directly. A tool that returns correct data when called in-process but breaks over the actual stdio transport (encoding, framing, subprocess lifecycle) is not done. Minimum bar: connect an actual MCP client (the `mcp` SDK's stdio client, or Claude Code itself configured against `amsha-mcp`), list tools, call each one, confirm real responses.

## Why this scope and not more

Ponytail check: could Phase 1 also do doc *embedding search* instead of keyword grep? Skipped — `mcp/docs/` + `docs/` is ~15k lines total, well within what keyword search over a handful of files handles adequately. Add embeddings only if `search_amsha_docs` demonstrably returns bad results at this scale, not preemptively.

Could Phase 1 also expose crew-YAML validation? Skipped — that needs `crew_forge`'s real schemas and the Phase 2 methodology as validation rules, neither of which exist yet in tool form. Building it now means guessing at rules Phase 2/3 will define properly.
