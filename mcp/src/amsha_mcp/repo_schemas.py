"""Load Amsha's real crew schemas from the registered target repo, once, at startup.

This is the Phase-4 deadlock guard, parameterized: the schema modules are
imported exactly once in the MAIN thread before ``mcp.run()``, from the
registered repo's ``src`` tree. Because they land in ``sys.modules``, the tools'
deferred ``from amsha...import ...`` calls (verification.py, smoke.py, the
smoke subprocess) become no-op re-imports instead of lazy imports inside a
FastMCP worker thread — the thing that deadlocked the stdio server.

``ensure_imported()`` returns whether the real schemas could be loaded at all
(no repo registered, or that repo has no importable ``amsha.crew_forge``). Tools
consult ``available()`` and report a clear "cannot verify" instead of importing a
coincidental venv copy of Amsha.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

from . import docs_loader as dl

_SCHEMA_MODULES = (
    "amsha.crew_forge.domain.models.agent_data",
    "amsha.crew_forge.domain.models.task_data",
)

_available = False


def ensure_imported() -> bool:
    """Insert the target repo's src onto ``sys.path`` and eager-import the real
    schema modules in the current (main) thread. Idempotent. Returns True iff the
    real schemas are importable from the registered repo."""
    global _available
    if _available:
        return True
    repo = dl.repo_root()
    if not repo:
        return False
    src_pkg = repo / "src" / "nikhil"
    if not (src_pkg / "amsha").is_dir():
        return False
    if str(src_pkg) not in sys.path:
        sys.path.insert(0, str(src_pkg))
    try:
        for mod in _SCHEMA_MODULES:
            importlib.import_module(mod)
    except Exception:
        _available = False
        return False
    _available = True
    return True


def available() -> bool:
    return _available
