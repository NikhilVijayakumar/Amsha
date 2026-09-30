"""Tools for enumerating and explaining Amsha's modules."""
from __future__ import annotations

from .. import docs_loader as dl

# Per-module "About" docs that exist only in the Amsha repository. They are an
# enhancement, not a requirement: a registered target repo may provide them.
_POINTER_DOC = {
    "crew_forge": "docs/feature/crew_forge/About.md",
    "crew_monitor": "docs/feature/crew_monitor/About.md",
    "llm_factory": "docs/feature/llm_factory/About.md",
}


def list_amsha_modules() -> dict:
    """Return every runtime module of Amsha with a one-line purpose.

    Answers from the packaged product knowledge, so it works with no repository
    registered. A registered repo narrows the list to the modules that repo
    actually contains.
    """
    return {"modules": dl.runtime_modules()}


def explain_module(module_name: str) -> dict:
    """Explain one module: purpose, documentation, and its source files.

    `docs` comes from the module's packaged product concept, so it is available
    standalone. A registered repository may add a richer "About" page, which
    takes precedence when present.
    """
    modules = dl.runtime_modules()
    if module_name not in modules:
        known = ", ".join(sorted(modules)) or "none discovered"
        return {"error": f"Unknown module '{module_name}'. Known modules: {known}"}

    result: dict = {"module": module_name, "purpose": modules[module_name]}

    preview = ""
    root = dl.repo_root()
    pointer = _POINTER_DOC.get(module_name)
    if root and pointer:
        preview = dl.get_preview(root / pointer)
    if not preview:
        concept = dl.product_concept(module_name)
        if concept is not None:
            preview = dl.get_preview(concept, max_lines=20)
    if preview:
        result["docs"] = preview

    # Source file lists are inherently repository-specific: they describe a
    # checkout, so with no repo registered this stays empty by design.
    result["source_files"] = dl.source_files_for(module_name)
    result["spec"] = dl.product_concept(module_name)
    if result["spec"] is not None:
        result["spec"] = str(result["spec"].name)
    return result
