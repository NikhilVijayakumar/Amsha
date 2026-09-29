---
type: Reference
title: "Contract: LLM factory build result"
description: The return shape the LLM factory hands back, and how provider configuration reaches it.
tags: [amsha, contract, interface, llm-factory]
generated: { by: "opencode/big-pickle", at: 2026-09-29T00:00:00Z }
stale_after: 2027-03-29T00:00:00Z
sources:
  - id: llm-factory-src
    resource: ../../src/nikhil/amsha/llm_factory
    title: LLM Factory source tree
    author: team:amsha
  - id: llm-config
    resource: ../../src/nikhil/amsha/configuration/domain/models/amsha_llm_config.py
    title: AmshaLLMConfig schema
    author: team:amsha
---

# Contract: LLM factory build result

## Input

`AmshaLLMConfig`, loaded through
[`Configuration`](../features/configuration.md). Per model:
`model` (required), `base_url`, `api_key`, `api_key_env`, `api_version`,
`output_config`. Grouped by `LLMTypeSection` — creative versus evaluation.

Secrets arrive by reference, not by value: `api_key_env` names an environment
variable, so a config file can be committed without embedding a credential.

## Output

`llm_factory/domain/model/llm_build_result.py` defines the result the builder
returns. Its supporting types are `llm_model_config.py`,
`llm_model_capabilities.py`, `llm_parameters.py`, and `llm_output_config.py`.

A client consumes the returned instance through the CrewAI adapter
(`adapters/crewai_adapter.py`); `adapters/lmstudio_lifecycle_client.py`
handles lifecycle-managed local endpoints.

## Rules

**Factory providers, not constructors.** Per
[`AGENTS.md`](../../AGENTS.md) §3, LLM instances are created by factory
providers in `dependency/llm_container.py`. `service/llm_builder.py` depends
on the container; it does not own it. This is the DI rule applied to the one
object type that is expensive and side-effecting to construct.

**Purpose is configuration, not code.** `LLMType` is selected by the caller
— `AmshaCrewFileApplication(..., llm_type)` — and defaults are resolved from
configuration. A client should never branch on LLM type in orchestration code.

**Provider-specific code stays in `adapters/`.** Capability differences
between providers are described in the domain models and implemented in
adapters, so adding a provider does not touch the builder.

## Deprecation

`utils/deprecated_compat.py` preserves older construction call sites across a
minor version. Under [`AGENTS.md`](../../AGENTS.md) §9, a deprecated method
survives one minor version and is removed only in a major bump.

## Related

- [LLM Factory](../features/llm-factory.md)
- [Configuration](../features/configuration.md)
