# Methodology

The 34 active methodology documents: 10 prerequisite stages (`00`-`09`) and 24
implementation topics (`00`-`23`). These are the corpus `amsha-mcp` serves as
reference material to an agent designing a crew.

## Prerequisite (`prerequisite/`)

The design-time sequence. A caller supplies a problem statement and works
through the stages before writing any crew YAML.

| Stage | Document | Stage | Document |
|---|---|---|---|
| 00 | Problem Definition | 05 | Flow and State Planning |
| 01 | Goal and Boundary Definition | 06 | Corner Cases and Failure Planning |
| 02 | Process Decomposition | 07 | Capability Selection |
| 03 | Process Contracts and Atomicity | 08 | Architecture Validation |
| 04 | Process Validation and Human Review | 09 | Architecture Handoff Checklist |

## Implementation (`implementation/`)

The build-time engineering guidance, one topic per capability area.

| Topic | Document | Topic | Document |
|---|---|---|---|
| 00 | Agent Workflow Engineering Principles | 12 | Reasoning and Planning |
| 01 | Agent Engineering | 13 | Python and Tools |
| 02 | Task Engineering | 14 | MCP Integration |
| 03 | Atomic Task Design | 15 | Files and Artifacts |
| 04 | Agent-Task Alignment | 16 | Streaming and Execution |
| 05 | Agent-Task Validation | 17 | Checkpointing and Recovery |
| 06 | Crew Engineering | 18 | Event Listeners |
| 07 | Crew Evaluation | 19 | Observability and Tracing |
| 08 | Process Engineering | 20 | Amsha Architecture |
| 09 | Flow Engineering | 21 | Amsha MCP |
| 10 | Crew-Flow Architecture | 22 | Amsha Project Generation |
| 11 | Context, Knowledge, Memory | 23 | Anti-Patterns and Checklists |

## Ordering is load-bearing

The prerequisite documents encode a strict order, and topics 00-23 assume the
prerequisite sequence has been completed. `records/proposal-archive/02-*.md`
records why the server exposes them as sequenced tools rather than a flat
document dump.
