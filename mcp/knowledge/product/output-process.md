---
type: Module
title: "Output Process"
description: "Post-processes structured crew output — currently JSON cleaning only; the evaluation and validation subpackages are unbuilt stubs."
tags: [amsha, mcp, product, output-process]
status: stable
module: "output_process"
kebab_name: output-process
spec: "openspec/specs/output-process/spec.md"
concept_source: "knowledge/features/output-process.md"
generated: { by: "process:project-product-knowledge", at: 2026-09-30T00:00:00Z }
---

# Output Process

Post-processes structured crew output — currently JSON cleaning only; the evaluation and validation subpackages are unbuilt stubs.

## Why it exists

Normalises model output into artifacts a caller can consume directly, and documents the boundary of what this capability currently does not provide. It covers stripping decoration from structured output, deriving a safe output location, and the current absence of output evaluation and output validation.

## Provenance

Generated from the Amsha concept [`output-process`](../../../knowledge/features/output-process.md) and the
behavioural requirements in [`output-process` spec](../../../openspec/specs/output-process/spec.md). Edit those sources,
then re-run `scripts/project_product_knowledge.py`.

## Source of truth

The MCP server serves this concept for `list_amsha_modules` and
`explain_module`. A registered target repository may additionally supply the
module's real file list; it is not required to answer.
