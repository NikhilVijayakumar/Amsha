# Proposal 04 — Adopt CrewAI's Unified Memory

| | |
|---|---|
| **Priority** | Phase 5 |
| **Risk** | Low (pure adoption, nothing to migrate away from) |
| **Effort** | Small-Medium |
| **Depends on** | [02](02-crewai-version-migration.md), [08](08-agent-task-capability-expansion.md) |

## What changed in CrewAI

0.x had separate `ShortTermMemory`/`LongTermMemory`/`EntityMemory`/contextual/external memory classes. CrewAI 1.x replaces all of that with **one unified `Memory` class**: an LLM analyzes content at write-time to infer scope/category/importance, storage is a hierarchical **scope tree** (e.g. `/project/alpha`, `/agent/researcher`), and retrieval uses a composite score (`semantic_weight×similarity + recency_weight×decay + importance_weight×importance`). Default backend is **LanceDB** at `./.crewai/memory` (a change from ChromaDB-only), pluggable via a custom `StorageBackend`.

## Current state in Amsha

`Crew(memory=...)` is never set anywhere in `CrewBuilderService.build()`. Because there was no old memory API in use, **this is a zero-cost migration** — nothing to break, purely additive.

## Proposal

1. Add a `memory: bool = False` field (default off, to keep existing behavior unchanged for current consumers) to `CrewData` (`crew_forge/domain/models/crew_data.py`), threaded through to `Crew(memory=data.memory)` in `CrewBuilderService.build()`.
2. For agent-level entity/contextual memory needs, expose it via `AgentRequest` once [08](08-agent-task-capability-expansion.md) generalizes that model — don't bolt it onto the current 4-field model as a one-off.
3. Storage location: default LanceDB path `./.crewai/memory` will land inside whatever `output_dir_path` Amsha's caller configures unless explicitly redirected — decide whether Amsha should namespace this per-module (mirroring the existing `output/{module_name}/output_{timestamp}/` convention in `CrewBuilderService._create_output_dir`) or leave it at CrewAI's default. Recommend namespacing it the same way output files are, for consistency and to avoid cross-crew memory bleed between different `module_name`s sharing a process.
4. **Gotcha to document**: memory's write-time LLM analysis means every memory write costs an extra LLM call unless queries are short (<200 chars, which skip LLM analysis per CrewAI's docs). This has cost implications Amsha should surface in its own docs/config validation rather than let users discover it via an unexpected token-usage spike (which `crew_performance_monitor.py` would otherwise silently attribute to the crew's normal execution).

## What NOT to do

- Don't wire memory on by default — it changes cost and latency characteristics; existing Amsha consumers upgrading CrewAI shouldn't get a surprise bill.
- Don't attempt to bridge old-style `ShortTermMemory`/`EntityMemory` APIs — there's no old code in Amsha using them, so there's nothing to bridge.
