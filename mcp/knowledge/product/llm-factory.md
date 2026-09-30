---
type: Module
title: "LLM Factory"
description: "Builds LLM instances for any provider from one configuration, with purpose profiles for creative versus evaluation work."
tags: [amsha, mcp, product, llm-factory]
status: stable
module: "llm_factory"
kebab_name: llm-factory
spec: "openspec/specs/llm-factory/spec.md"
concept_source: "knowledge/features/llm-factory.md"
generated: { by: "process:project-product-knowledge", at: 2026-09-30T00:00:00Z }
---

# LLM Factory

Builds LLM instances for any provider from one configuration, with purpose profiles for creative versus evaluation work.

## Why it exists

Builds configured language-model instances for any supported provider from a single configuration, so that no module other than this one needs to know how a provider is addressed. This capability covers the purpose profiles that distinguish creative from evaluation work, the provider-independent build contract, and the boundary that keeps provider specifics in adapters.

## Provenance

Generated from the Amsha concept [`llm-factory`](../../../knowledge/features/llm-factory.md) and the
behavioural requirements in [`llm-factory` spec](../../../openspec/specs/llm-factory/spec.md). Edit those sources,
then re-run `scripts/project_product_knowledge.py`.

## Source of truth

The MCP server serves this concept for `list_amsha_modules` and
`explain_module`. A registered target repository may additionally supply the
module's real file list; it is not required to answer.
