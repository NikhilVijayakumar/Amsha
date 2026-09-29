---
type: Module
title: LLM Factory
description: Builds LLM instances for any provider from one configuration, with purpose profiles for creative versus evaluation work.
tags: [amsha, capability, llm, crewai]
generated: { by: "opencode/big-pickle", at: 2026-09-29T00:00:00Z }
stale_after: 2027-03-29T00:00:00Z
sources:
  - id: llm-factory-src
    resource: ../../src/nikhil/amsha/llm_factory
    title: LLM Factory source tree
    author: team:amsha
  - id: llm-factory-docs
    resource: ../../docs/feature/llm_factory
    title: LLM Factory feature documentation
---

# LLM Factory

The only module that talks to model providers. Everything else asks this
factory for an already-configured LLM rather than constructing one, which is
what keeps provider-specific configuration out of the orchestration code.

## Layer structure

| Layer | Files | Role |
|---|---|---|
| `domain` | 10 | Model, parameter, capability, and use-case types |
| `adapters` | 2 | `crewai_adapter`, `lmstudio_lifecycle_client` |
| `utils` | 2 | `llm_utils`, `deprecated_compat` |
| `service` | 1 | `llm_builder` |
| `settings` | 1 | `llm_settings` |
| `dependency` | 1 | `llm_container` — the DI wiring point |

This is the densest `domain` layer in Amsha (10 non-empty files), which fits
its position: provider configuration is the widest surface area in the
library and the easiest to get subtly wrong.

## Purpose profiles

`LLMType` distinguishes *creative* from *evaluation* work. A creative profile
optimises for generation quality; an evaluation profile optimises for
deterministic, cheap, well-structured output. Choosing between them is a
configuration decision, not a code change, which is why `AmshaCrewFileApplication`
takes `llm_type` as a constructor argument.

## Dependency injection

Per the DI rule in [`AGENTS.md`](../../AGENTS.md), LLM instances are created
by factory providers in `dependency/llm_container.py`, not by services that
construct their own models. `llm_builder` depends on the container; it does
not own it.

## Deprecation shim

`utils/deprecated_compat.py` exists to keep older call sites working across a
minor version. Under the deprecation policy in
[`AGENTS.md`](../../AGENTS.md) §9, a deprecated method survives one minor
version before removal in a major bump — this module is where that window is
implemented for LLM construction.

## Related

- [Configuration](./configuration.md) — `AmshaLLMConfig` is the input schema
- [Crew Forge](./crew-forge.md) — the primary consumer
- [Contracts: LLM Factory build result](../contracts/llm-factory-build-result.md)
