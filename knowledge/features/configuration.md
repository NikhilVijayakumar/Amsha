---
type: Module
title: Configuration
description: Loads and validates the job, app, and LLM configuration schemas that every other module reads.
tags: [amsha, capability, configuration, pydantic]
generated: { by: "opencode/big-pickle", at: 2026-09-29T00:00:00Z }
stale_after: 2027-03-29T00:00:00Z
sources:
  - id: configuration-src
    resource: ../../src/nikhil/amsha/configuration
    title: Configuration source tree
    author: team:amsha
---

# Configuration

Defines what an Amsha run *is* — the schemas that describe the application,
the job, and the LLM. Every other module reads configuration rather than
declaring it, which is what makes Amsha applications declarative: a client
app supplies YAML, and the library decides what runs.

## Layer structure

| Layer | Files | Role |
|---|---|---|
| `domain/models` | 3 | `AmshaAppConfig`, `AmshaJobConfig`, `AmshaLLMConfig` |
| `application` | 1 | `ConfigurationManager` |
| `infrastructure` | 1 | `strict_validator` |
| `exceptions` | 1 | `AmshaConfigurationException` |

This is the cleanest Clean Architecture layering in the codebase — a strict
inner-to-outer chain with no adapters and no protocol definitions, because
configuration is pure data and needs none.

## Schemas

**`AmshaAppConfig`** — where things live. `domain_root_path` (e.g.
`crew_configs`) and `output_dir_path` are both required.

**`AmshaJobConfig`** — what runs. A list of `CrewDefinition`s, each holding
`steps` (a list of `CrewStep` pairing a `task_key` with an `agent_key`), plus
optional `knowledge_sources`, `input`, and `memory`.

**`AmshaLLMConfig`** — per-model provider settings: `model` (required),
`base_url`, `api_key`, `api_key_env`, `api_version` (for Azure OpenAI), and
`output_config`. Note `api_key` and `api_key_env` are alternatives, letting
config reference an environment variable instead of embedding a secret.

## Loading

`ConfigurationManager` exposes three static entry points, all taking the model
class as a parameter and all raising `AmshaConfigurationException` on
failure: `load_from_dict`, `load_from_json`, `load_from_yaml`.

`infrastructure/strict_validator` is the validation layer. It is named for
strictness deliberately — a malformed config fails at load time rather than
surfacing as a confusing runtime error deep in an orchestration run.

## Related

- [Crew Forge](./crew-forge.md) — consumes `AmshaJobConfig`
- [LLM Factory](./llm-factory.md) — consumes `AmshaLLMConfig`
