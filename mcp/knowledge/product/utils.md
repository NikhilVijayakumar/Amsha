---
type: Module
title: "Utils"
description: "Small format helpers for JSON, YAML, and UTF-8 handling, shared across modules."
tags: [amsha, mcp, product, utils]
status: stable
module: "utils"
kebab_name: utils
spec: "openspec/specs/utils/spec.md"
concept_source: "knowledge/features/utils.md"
generated: { by: "process:project-product-knowledge", at: 2026-09-30T00:00:00Z }
---

# Utils

Small format helpers for JSON, YAML, and UTF-8 handling, shared across modules.

## Why it exists

Holds the small, dependency-light helpers Amsha uses to read and write the file formats its configurations and outputs are expressed in. This capability covers JSON reading and writing, YAML reading, and in-place text-encoding conversion.

## Provenance

Generated from the Amsha concept [`utils`](../../../knowledge/features/utils.md) and the
behavioural requirements in [`utils` spec](../../../openspec/specs/utils/spec.md). Edit those sources,
then re-run `scripts/project_product_knowledge.py`.

## Source of truth

The MCP server serves this concept for `list_amsha_modules` and
`explain_module`. A registered target repository may additionally supply the
module's real file list; it is not required to answer.
