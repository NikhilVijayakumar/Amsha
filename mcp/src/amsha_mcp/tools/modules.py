"""Tools for enumerating and explaining Amsha's modules."""
from __future__ import annotations

from .. import docs_loader as dl

_POINTER_DOC = {
    "crew_forge": "docs/feature/crew_forge/About.md",
    "crew_monitor": "docs/feature/crew_monitor/About.md",
    "llm_factory": "docs/feature/llm_factory/About.md",
}


def list_amsha_modules() -> dict:
    """Return every runtime module under src/nikhil/amsha with a one-line purpose."""
    return {"modules": dl.runtime_modules()}


def explain_module(module_name: str) -> dict:
    """Explain one module: purpose, config pointers, and its source files."""
    modules = dl.runtime_modules()
    if module_name not in modules:
        known = ", ".join(sorted(modules)) or "none discovered"
        return {"error": f"Unknown module '{module_name}'. Known modules: {known}"}

    result = {"module": module_name, "purpose": modules[module_name]}
    if module_name in _POINTER_DOC:
        result["docs"] = dl.get_preview(dl.repo_root() / _POINTER_DOC[module_name])
    result["source_files"] = dl.source_files_for(module_name)
    return result