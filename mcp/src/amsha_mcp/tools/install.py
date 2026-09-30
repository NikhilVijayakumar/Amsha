"""Tools for how to install and get started with Amsha."""
from __future__ import annotations

from .. import docs_loader as dl

# Last-resort values, used only if the packaged product knowledge is unavailable
# (a stripped install). The maintained source is the packaged concept, which is
# generated from the Amsha README's Installation section and `requires-python`.
_FALLBACK = {
    "install": "pip install amsha",
    "optional_docling": "pip install docling   # only for document processing (PDF/DOCX/HTML/XLSX/PPTX/images)",
    "python": ">=3.12,<3.14",
}


def get_install_instructions() -> dict:
    """Return how to install Amsha, including optional extras and version constraints."""
    facts = dl.packaged_install_facts() or _FALLBACK
    return {
        "install": facts.get("install") or _FALLBACK["install"],
        "optional_docling": facts.get("optional_docling") or _FALLBACK["optional_docling"],
        "python": facts.get("python") or _FALLBACK["python"],
        "source": dl.extract_installation() or "See README.md → Installation",
    }


def get_quickstart() -> dict:
    """Return the Quick Start procedure: repo README if registered, else packaged."""
    return {"quickstart": dl.extract_quickstart() or "See README.md → Quick Start"}
