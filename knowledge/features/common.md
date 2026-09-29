---
type: Module
title: Common
description: Cross-cutting internal infrastructure — structured logging and execution metrics. Not a user-facing capability.
tags: [amsha, internal, logging, infrastructure]
generated: { by: "opencode/big-pickle", at: 2026-09-29T00:00:00Z }
stale_after: 2027-03-29T00:00:00Z
sources:
  - id: common-src
    resource: ../../src/nikhil/amsha/common
    title: Common source tree
    author: team:amsha
---

# Common

Two files, one public surface:

```python
from amsha.common.logger import get_logger, reset_logger, log_execution, MetricsLogger
```

Internal cross-cutting infrastructure rather than a capability a user selects.
That distinction is why the MCP server excludes it from its module inventory —
see [Methodology: prerequisite](../methodology/prerequisite.md) for the
capability-selection rule and
[`docs_loader.RUNTIME_MODULES`](../../mcp/src/amsha_mcp/docs_loader.py) for the
code that encodes it.

## Logging

`StructuredFormatter` renders log records as key-value pairs rather than free
prose, so entries stay machine-parseable. `_configure()` is the one-time
handler setup.

`get_logger(module_name=None, log_level=None)` is the accessor every module
uses. It is process-global and idempotent, so calling it from several modules
yields the same configured logger.

`reset_logger()` exists for tests that need to re-run configuration after
changing level.

`log_execution(logger, operation_name)` is a decorator factory. It wraps an
operation to log entry, exit, duration, and failure — the standard shape for
timing any call Amsha wants to measure.

## Metrics

`MetricsLogger` records structured counters and timings. It is separate from
`StructuredFormatter` because emission (formatting, routing) and collection
(what is counted) are different concerns that change for different reasons.

## Related

- [AGENTS.md: DI and SOLID](../../AGENTS.md) — the standards this module
  exists to serve
