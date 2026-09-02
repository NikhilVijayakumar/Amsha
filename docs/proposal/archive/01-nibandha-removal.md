# Proposal 01 — Remove the Nibandha Dependency

| | |
|---|---|
| **Status** | ✅ Done (2026-09-02) |
| **Priority** | Do first |
| **Risk** | Low |
| **Effort** | Small (~half a day) |
| **Blocks** | Nothing downstream depends on keeping Nibandha |
| **Blocked by** | Nothing |

## Execution log

- `logger.py` rewritten to pure stdlib `logging` (`RotatingFileHandler`, 50MB × 30 backups, plus console). Public API preserved (`get_logger`, `log_execution`, `MetricsLogger`, `reset_logger`); the four rotation-inspection helpers and `.Nibandha/` folder scaffolding were dropped as planned (net -207/+56 lines).
- Deleted: `rotation_setup.py`, `tests/test_nibandha_rotation.py`, `export_paper.py`.
- `pyproject.toml`: removed `Nibandha[export] @ git+...`.
- `docs/reference/Nibandha/` archived to `docs/archived/Nibandha/` rather than deleted (per this proposal's suggestion to archive, not hard-delete, since Nibandha is the user's own separate project).
- Verified: clean import with no Nibandha installed, `extra={}` still formats as `key=value`, all logger-dependent service tests pass (45 passed) including crew_builder/sync/execution_state/runtime.
- Suite has ~40-45 pre-existing failures unrelated to this change (mock arity, tuple-unpack drift, GPU/pynvml env, two tests importing non-existent modules) — these predate this change; the old logger couldn't even import without Nibandha installed in this env, so this rewrite is what makes the suite runnable at all, not what broke it.
- Deferred: LMStudio/gpt-oss checks — out of scope for a pure logging refactor, folded into [02](02-crewai-version-migration.md).

## Current state

`pyproject.toml` declares:

```
"Nibandha[export] @ git+https://github.com/NikhilVijayakumar/Nibandha.git@main",
```

A git dependency with no version pin (`@main` — floats). It is used in exactly two files:

- `src/nikhil/amsha/common/logger.py` — wraps `nibandha.core.nibandha_app.Nibandha` to provide `get_logger()`, a `StructuredFormatter`, `MetricsLogger`, and log-rotation helpers (`should_rotate`, `rotate_logs`, `cleanup_old_archives`, `get_rotation_config`). On first call it also silently creates `.Nibandha/config/rotation_config.yaml` and scaffolds `output/final`, `output/intermediate`, `execution/state` folders.
- `src/nikhil/amsha/common/rotation_setup.py` — presumably configuration helpers for the same rotation system (not read in detail here, but it's Nibandha-only).

Every other module that logs (`base_crew_orchestrator.py`, `crew_performance_monitor.py`, `crew_builder_service.py`, etc.) does so through `amsha.common.logger.get_logger()` — i.e. through this one wrapper, not through Nibandha directly. That's the whole surface area.

## Why remove it

1. **Not a core Amsha feature.** Amsha's stated purpose (`docs/feature/crew_forge/functional.md`) is CrewAI configuration/orchestration. Log rotation and output-folder bookkeeping is infrastructure, not the product.
2. **Git dependency floating on `@main`** is a supply-chain and reproducibility risk independent of CrewAI — a build today and a build next month can silently pull different Nibandha code.
3. **Directly named as a migration blocker** — an unpinned git dependency is exactly the kind of thing that produces confusing resolver errors when `crewai`'s own dependency tree shifts across the 0.x→1.x boundary (see [02](02-crewai-version-migration.md)). Removing it first means the CrewAI upgrade has one less variable.
4. Everything Nibandha provides here — leveled loggers, an `extra={}`-friendly formatter, size/time-based rotation — is a solved problem in the Python standard library (`logging`, `logging.handlers.RotatingFileHandler` / `TimedRotatingFileHandler`).

## Proposal

Replace `amsha.common.logger` internals with stdlib `logging`, keeping the **existing public function signatures** (`get_logger`, `MetricsLogger`, `log_execution`) so callers (`base_crew_orchestrator.py`, `crew_performance_monitor.py`, `crew_builder_service.py`, tests) need zero changes.

```python
# amsha/common/logger.py (sketch)
import logging
import os
from logging.handlers import TimedRotatingFileHandler

_configured = False

def _configure_root():
    global _configured
    if _configured:
        return
    level = os.getenv("AMSHA_LOG_LEVEL", "INFO")
    root = logging.getLogger("Amsha")
    root.setLevel(level)

    handler = TimedRotatingFileHandler(
        "logs/amsha.log", when="midnight", backupCount=30, encoding="utf-8"
    )
    handler.setFormatter(StructuredFormatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    root.addHandler(handler)

    console = logging.StreamHandler()
    console.setFormatter(handler.formatter)
    root.addHandler(console)
    _configured = True

def get_logger(module_name=None, log_level=None):
    _configure_root()
    return logging.getLogger(f"Amsha.{module_name}" if module_name else "Amsha")
```

- `StructuredFormatter` (the `extra={}` → `key=value` formatter) is already pure stdlib code in the current file — keep it verbatim.
- `MetricsLogger` and `log_execution` are already pure stdlib code (they only call `self.logger.info/.error`) — keep verbatim, zero changes needed.
- `should_rotate`/`rotate_logs`/`cleanup_old_archives`/`get_rotation_config` — `TimedRotatingFileHandler`/`RotatingFileHandler` handle rotation and retention automatically (`backupCount`); these four functions become unnecessary. If a caller outside this repo actually invokes them, keep thin no-op-compatible stubs for one release with a deprecation warning; otherwise delete.
- Delete `.Nibandha/` config scaffolding (`_ensure_default_rotation_config`) — no longer applicable.
- Delete `rotation_setup.py` once confirmed nothing external imports it (`grep -r rotation_setup` across any downstream consumers of the Amsha package, not just this repo).

## Migration steps

1. Rewrite `amsha/common/logger.py` per the sketch above, preserving the public API.
2. Remove `Nibandha[export] @ git+...` from `pyproject.toml` dependencies.
3. Delete or stub `rotation_setup.py` (check external usage first — Amsha is published as a library, so check for downstream consumers before hard-deleting a public module).
4. Run the existing test suite (`src/nikhil/amsha/integration_tests/crew_forge/test_json_retry_workflow.py` references Nibandha — update/remove that reference) to confirm nothing else silently depended on Nibandha's folder scaffolding (`output/final`, `output/intermediate`, `execution/state`).
5. Update `docs/reference/Nibandha/*` — either archive it (move under `docs/archived/`) or delete, since it will no longer describe a real dependency of this repo.

## Open question for the user

Nibandha is your own project. If it's still actively maintained and used elsewhere, this proposal only removes it *as an Amsha dependency* — it doesn't suggest deprecating Nibandha itself.
