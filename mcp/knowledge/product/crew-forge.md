---
type: Module
title: "Crew Forge"
description: "Turns crew definitions into runnable CrewAI crews and flows, and executes them."
tags: [amsha, mcp, product, crew-forge]
status: stable
module: "crew_forge"
kebab_name: crew-forge
spec: "openspec/specs/crew-forge/spec.md"
concept_source: "knowledge/features/crew-forge.md"
generated: { by: "process:project-product-knowledge", at: 2026-09-30T00:00:00Z }
---

# Crew Forge

Turns crew definitions into runnable CrewAI crews and flows, and executes them.

## Why it exists

Turns declarative crew definitions into runnable CrewAI crews and flows, and executes them. This is the capability client applications build on: it covers parsing crew definitions from their storage, assembling agents and tasks into a crew, the file-backed orchestration base class, and the repository boundaries through which a client supplies stored definitions.

## Provenance

Generated from the Amsha concept [`crew-forge`](../../../knowledge/features/crew-forge.md) and the
behavioural requirements in [`crew-forge` spec](../../../openspec/specs/crew-forge/spec.md). Edit those sources,
then re-run `scripts/project_product_knowledge.py`.

## Source of truth

The MCP server serves this concept for `list_amsha_modules` and
`explain_module`. A registered target repository may additionally supply the
module's real file list; it is not required to answer.
