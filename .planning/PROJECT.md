# Amsha — Project Definition

> **Project Type:** Research Library (Brownfield)  
> **Analysis Date:** 2026-04-10

---

## What This Is

Amsha is a standalone Python library for LLM and agent management using CrewAI, with integrated monitoring and evaluation capabilities. The project includes both the implementation (`src/`) and research framework (`research/`) for empirical validation, with the goal of publishing a hybrid technical/empirical research paper.

---

## Core Value

A production-ready CrewAI orchestration library with dual-backend support (YAML + MongoDB), multi-provider LLM abstraction, built-in resource monitoring, and evaluation pipeline — designed for enterprise deployment and research benchmarking.

---

## Context

### Existing Codebase
- **Location:** `/home/dell/PycharmProjects/Amsha`
- **Implementation:** `src/nikhil/amsha/` — Clean Architecture with DI
- **Research:** `research/` — Benchmark experiments and scripts
- **Documentation:** `docs/paper/` — Pre-structured paper modules
- **Version:** 2.0.9 (from pyproject.toml)

### Library Architecture (Validated)
- **Crew Forge** — Dual orchestration modes (File-based YAML, DB-based MongoDB)
- **LLM Factory** — Multi-provider support (Google Gemini, Azure OpenAI, OpenRouter, LM Studio local)
- **Crew Monitor** — CPU/GPU/RAM monitoring, contribution analysis, Excel reporting
- **Output Process** — JSON sanitization, rubric scoring, Z-score relative grading
- **Configuration** — YAML-driven configuration with strict validation
- **Knowledge** — Docling-based document ingestion

### Research Framework (Validated)
- 6 sub-experiments mapped to paper sections
- 6+ local models tested (Qwen3, GPT-OSS, Llama, etc.)
- 4 cloud providers (Gemini, Azure, OpenRouter, LM Studio)
- Master aggregation results in `research/results/MASTER_AGGREGATION.json`

### Paper Structure (Pre-existing)
- **User inputs:** `app_execution_results.md`, `practical_implications.md`
- **Modules:** crew_forge, llm_factory, crew_monitor, output_process, cross_module
- **Each module:** architecture, novelty, mathematics, gaps, summary

---

## Requirements

### Validated

- ✅ Crew Forge dual-backend orchestration (YAML + MongoDB)
- ✅ LLM Factory with 4 provider tiers (10+ models)
- ✅ Crew Monitor with resource profiling and contribution analysis
- ✅ Output Process with JSON sanitization and Z-score grading
- ✅ Configuration management via YAML files
- ✅ Knowledge management via Docling
- ✅ Research framework with benchmark scripts
- ✅ 6 sub-experiments for empirical validation
- ✅ Pre-structured paper documentation

### Active

- [ ] Complete empirical data collection (fill in 📝 markers in app_execution_results.md)
- [ ] Verify practical implications claims (confirm/reject/modify in practical_implications.md)
- [ ] Break circular dependency (output_process → crew_forge)
- [ ] Add Pydantic models to output_process module
- [ ] Finalize cross-module integration analysis

### Out of Scope

- [New provider integrations beyond current 4 tiers] — Not required for paper
- [Web UI or CLI interface] — Library-only focus
- [Multi-agent parallel execution within single crew] — Sequential/hierarchical only

---

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Paper type: Hybrid (Technical + Empirical) | Existing implementation has solid technical depth; benchmark data enables empirical validation | — In Progress |
| Timeline: No rush | Thoroughness prioritized over speed | — Ongoing |
| Research execution: Already completed | Benchmark data exists in research/results/ | — Needs analysis |

---

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---

*Last updated: 2026-04-10 after initialization*