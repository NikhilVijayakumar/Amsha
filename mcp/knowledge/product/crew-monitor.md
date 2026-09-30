---
type: Module
title: "Crew Monitor"
description: "Observes running crews — resource usage, event lifecycle, per-agent contribution, and Excel reporting."
tags: [amsha, mcp, product, crew-monitor]
status: stable
module: "crew_monitor"
kebab_name: crew-monitor
spec: "openspec/specs/crew-monitor/spec.md"
concept_source: "knowledge/features/crew-monitor.md"
generated: { by: "process:project-product-knowledge", at: 2026-09-30T00:00:00Z }
---

# Crew Monitor

Observes running crews — resource usage, event lifecycle, per-agent contribution, and Excel reporting.

## Why it exists

Observes crew executions that are already running: resource consumption, event lifecycle, and how much each agent contributed to the result. This capability covers what a monitor records, how it attaches to a running execution, and how observations are turned into reports.

## Provenance

Generated from the Amsha concept [`crew-monitor`](../../../knowledge/features/crew-monitor.md) and the
behavioural requirements in [`crew-monitor` spec](../../../openspec/specs/crew-monitor/spec.md). Edit those sources,
then re-run `scripts/project_product_knowledge.py`.

## Source of truth

The MCP server serves this concept for `list_amsha_modules` and
`explain_module`. A registered target repository may additionally supply the
module's real file list; it is not required to answer.
