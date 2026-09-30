---
type: Module
title: "Configuration"
description: "Loads and validates the job, app, and LLM configuration schemas that every other module reads."
tags: [amsha, mcp, product, configuration]
status: stable
module: "configuration"
kebab_name: configuration
spec: "openspec/specs/configuration/spec.md"
concept_source: "knowledge/features/configuration.md"
generated: { by: "process:project-product-knowledge", at: 2026-09-30T00:00:00Z }
---

# Configuration

Loads and validates the job, app, and LLM configuration schemas that every other module reads.

## Why it exists

Defines the declarative schema of an Amsha run — the application, job, and LLM configurations that every other module reads instead of declaring its own inputs. This capability covers what those schemas require, how they are loaded from dict, JSON, and YAML, and how invalid configuration is reported.

## Provenance

Generated from the Amsha concept [`configuration`](../../../knowledge/features/configuration.md) and the
behavioural requirements in [`configuration` spec](../../../openspec/specs/configuration/spec.md). Edit those sources,
then re-run `scripts/project_product_knowledge.py`.

## Source of truth

The MCP server serves this concept for `list_amsha_modules` and
`explain_module`. A registered target repository may additionally supply the
module's real file list; it is not required to answer.
