---
type: Module
title: Crew Monitor
description: Observes running crews — resource usage, event lifecycle, per-agent contribution, and Excel reporting.
tags: [amsha, capability, observability, reporting]
generated: { by: "opencode/big-pickle", at: 2026-09-29T00:00:00Z }
stale_after: 2027-03-29T00:00:00Z
sources:
  - id: crew-monitor-src
    resource: ../../src/nikhil/amsha/crew_monitor
    title: Crew Monitor source tree
    author: team:amsha
  - id: crew-monitor-docs
    resource: ../../docs/feature/crew_monitor
    title: Crew Monitor feature documentation
---

# Crew Monitor

Answers "what happened, and what did it cost" for a crew run. It is the only
module concerned with observation rather than execution.

## Services

All four classes live in `service/`; there is no domain layer, because
monitoring produces reports rather than holding state.

| Class | Lines | Responsibility |
|---|---|---|
| `AmshaEventListener` | 237 | Subscribes to the CrewAI event bus, records start/finish events and durations |
| `CrewPerformanceMonitor` | 165 | Samples CPU/GPU/memory while a crew runs; `start_monitoring`, `stop_monitoring`, `log_usage`, `get_metrics` |
| `ReportingTool` | 164 | Generates and combines per-job Excel reports |
| `ContributionAnalyzer` | 109 | Attributes job output to individual agents/steps |

## Integration points

`AmshaEventListener` subclasses CrewAI's `BaseEventListener` and binds to a
`CrewAIEventsBus` via `setup_listeners`. This is a **direct dependency on
CrewAI's event bus**, not a protocol — Crew Monitor is the one place where
Amsha is coupled to a specific CrewAI version's event surface.

`CrewPerformanceMonitor` takes an optional `model_name`; the same monitor
class therefore covers both machine-resource sampling and per-model usage
accounting.

## Reporting

`ReportingTool` and `ContributionAnalyzer` are separate tools that both take
a `config_path` and both write to Excel, with `ReportingTool` orchestrating
generate-then-combine across jobs. The split exists so contribution analysis
can be re-run over existing reports without regenerating them.

## Related

- [Execution State](./execution-state.md) — the state this module observes
- [Configuration](./configuration.md) — supplies both tools' `config_path`
