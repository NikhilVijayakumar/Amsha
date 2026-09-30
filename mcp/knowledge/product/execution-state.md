---
type: Module
title: "Execution State"
description: "Models the lifecycle of a single run and persists it through an injected state repository."
tags: [amsha, mcp, product, execution-state]
status: stable
module: "execution_state"
kebab_name: execution-state
spec: "openspec/specs/execution-state/spec.md"
concept_source: "knowledge/features/execution-state.md"
generated: { by: "process:project-product-knowledge", at: 2026-09-30T00:00:00Z }
---

# Execution State

Models the lifecycle of a single run and persists it through an injected state repository.

## Why it exists

Models the lifecycle of a single Amsha execution and persists it through an injected repository, so that any component can read what a run is currently doing without holding a reference to the orchestrator. This capability covers the status set, the state aggregate, and the repository boundary that makes the backing store swappable.

## Provenance

Generated from the Amsha concept [`execution-state`](../../../knowledge/features/execution-state.md) and the
behavioural requirements in [`execution-state` spec](../../../openspec/specs/execution-state/spec.md). Edit those sources,
then re-run `scripts/project_product_knowledge.py`.

## Source of truth

The MCP server serves this concept for `list_amsha_modules` and
`explain_module`. A registered target repository may additionally supply the
module's real file list; it is not required to answer.
