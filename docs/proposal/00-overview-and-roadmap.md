# Amsha × CrewAI 1.x — Overview & Roadmap (Round 2)

| | |
|---|---|
| **Status** | In progress — 12 partially done, 13 done |
| **Date** | 2026-09-02 |
| **Author** | Nikhil (compiled with Claude) |
| **Scope** | Round 2 of CrewAI 1.x alignment: capabilities requested after the original 12-proposal roadmap shipped |

## History

The original 12-proposal roadmap (0.201.1 → 1.15.18 migration, Mongo removal, Agent/Task capability expansion, Memory, Checkpointing, Knowledge/Skills, Flows, Event observability, and the agent-crafting skill) is **fully delivered** and archived at `docs/proposal/archive/`. Start there for the history of what shipped, when, and why. This document only covers what's newly proposed since.

## Round 2 — new proposals

| # | Proposal | Status | Why it's here |
|---|---|---|---|
| [12](12-tools-and-mcp-adoption.md) | Tools & MCP Integration (stdio-preferred) | ✅ Partial | Part 1 (Tools) done; Part 2 (MCP) config passthrough done, lifecycle deferred |
| [13](13-observability-tracing.md) | Observability: Native Tracing vs. the Event Bus | ✅ Done | Tracing passthrough wired, default off |

## Sequencing

No hard ordering between 12 and 13 — they're independent capability areas. Both depend on [08](archive/08-agent-task-capability-expansion.md) (done) for the `AgentRequest`/`TaskRequest` extension pattern they reuse.

Within 12 specifically: **Tools before MCP** — MCP tool objects ultimately land in the same `tools=[...]` list Tools support wires up, so getting the registry/resolution pattern right for plain Tools first gives MCP a place to plug into rather than inventing a second mechanism.

## Non-negotiables carried over from Round 1

These constraints from the original roadmap still apply and are relevant to 12/13:

- **Don't touch `BaseCrewOrchestrator`/`FileCrewOrchestrator`** — established in [03](archive/03-flows-adoption.md)/[10](archive/10-production-architecture-alignment.md), still holds. Neither 12 nor 13 requires touching the orchestrator layer.
- **Verify against a real LLM, not just mocks** — every Round 1 proposal was verified with `verify_capability_example.py` plus a live LM Studio (`qwen3.5-9b`) run; the Flow pipeline path specifically caught a real bug (`None` input handling) that only surfaced on an actual run. Same bar applies here — MCP stdio lifecycle and Windows subprocess cleanup in particular need a real run, not just an assertion that a config object built correctly.
