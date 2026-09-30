---
type: Module
title: "Execution Runtime"
description: "Submits work to a bounded thread pool and returns a cancellable, awaitable handle."
tags: [amsha, mcp, product, execution-runtime]
status: stable
module: "execution_runtime"
kebab_name: execution-runtime
spec: "openspec/specs/execution-runtime/spec.md"
concept_source: "knowledge/features/execution-runtime.md"
generated: { by: "process:project-product-knowledge", at: 2026-09-30T00:00:00Z }
---

# Execution Runtime

Submits work to a bounded thread pool and returns a cancellable, awaitable handle.

## Why it exists

Provides Amsha's concurrency boundary: a bounded worker pool that accepts callables and returns a handle the caller can poll, await, or cancel. This capability covers submission, handle semantics, and the execution modes that decide how submitted work is scheduled.

## Provenance

Generated from the Amsha concept [`execution-runtime`](../../../knowledge/features/execution-runtime.md) and the
behavioural requirements in [`execution-runtime` spec](../../../openspec/specs/execution-runtime/spec.md). Edit those sources,
then re-run `scripts/project_product_knowledge.py`.

## Source of truth

The MCP server serves this concept for `list_amsha_modules` and
`explain_module`. A registered target repository may additionally supply the
module's real file list; it is not required to answer.
