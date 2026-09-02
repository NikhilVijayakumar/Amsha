"""Tools for how to install and get started with Amsha."""
from __future__ import annotations

from .. import docs_loader as dl


def get_install_instructions() -> dict:
    """Return how to install Amsha, including optional extras and version constraints."""
    return {
        "install": "pip install amsha",
        "optional_docling": "pip install docling   # only for document processing (PDF/DOCX/HTML/XLSX/PPTX/images)",
        "python": ">=3.12,<3.14",
        "source": dl.extract_installation() or "See README.md → Installation",
    }


def get_quickstart() -> dict:
    """Return the Quick Start code block from README."""
    return {"quickstart": dl.extract_quickstart() or "See README.md → Quick Start"}