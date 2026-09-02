"""Read Amsha documentation and source metadata from disk at query time.

No content is copied into Python source: docs stay the single source of truth.
If a doc changes, the server's answers change on the next call.
"""
from __future__ import annotations

import re
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent  # mcp/src/amsha_mcp
MCP_ROOT = PACKAGE_ROOT.parent.parent            # mcp/
REPO_ROOT = MCP_ROOT.parent                      # the Amsha repo root

# Resolved in __init__ so tests can point REPO at a fixture if needed.
_REPO_ROOT: Path = REPO_ROOT
_MCP_ROOT: Path = MCP_ROOT


def configure_repo_root(root: Path) -> None:
    """Point the loader at an alternative repo root (used by tests)."""
    global _REPO_ROOT, _MCP_ROOT
    _REPO_ROOT = root
    _MCP_ROOT = root / "mcp"


def repo_root() -> Path:
    return _REPO_ROOT


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _docs_under(relative_dir: str, pattern: str = "*.md") -> dict[str, Path]:
    """Return {filename: path} for direct children of an mcp/docs subdir."""
    base = _MCP_ROOT / "docs" / relative_dir
    return {p.name: p for p in sorted(base.glob(pattern))} if base.is_dir() else {}


def read_prerequisite() -> dict[str, Path]:
    """mcp/docs/prerequisite/*.md keyed by filename (00-problem-definition.md ...)."""
    return _docs_under("prerequisite")


def read_implementation() -> dict[str, Path]:
    """mcp/docs/implementation/*.md keyed by filename."""
    return _docs_under("implementation")


def read_proposal() -> dict[str, Path]:
    """mcp/docs/proposal/*.md keyed by filename."""
    return _docs_under("proposal")


def read_top_level_markdown() -> dict[str, Path]:
    """Repo-root markdown we serve: README, USER_GUIDE, AGENTS."""
    names = ["README.md", "USER_GUIDE.md", "AGENTS.md", "DEPENDENCIES.md"]
    return {n: _REPO_ROOT / n for n in names if (_REPO_ROOT / n).is_file()}


def read_features_docs() -> dict[str, Path]:
    """docs/feature/*/About.md keyed by module name (turn the tree flat)."""
    base = _REPO_ROOT / "docs" / "feature"
    if not base.is_dir():
        return {}
    result: dict[str, Path] = {}
    for about in base.glob("*/*.md"):
        result[f"{about.parent.name}/{about.name}"] = about
    return dict(sorted(result.items()))


# ---------------------------------------------------------------------------
# Module inventory (source of truth = the real src tree, not a hand list)
# ---------------------------------------------------------------------------

# Public runtime modules under src/nikhil/amsha. `integration_tests` and
# `common` are not user-facing capabilities, so they're listed separately.
RUNTIME_MODULES = [
    "crew_forge",
    "crew_monitor",
    "execution_runtime",
    "execution_state",
    "llm_factory",
    "output_process",
    "utils",
]

_MODULE_PURPOSE = {
    "crew_forge": "Parse YAML/MongoDB crew definitions, build CrewAI crews/flows, and execute them.",
    "crew_monitor": "Real-time CPU/GPU/memory tracking, event-lifecycle logs, contribution analysis, and Excel reports.",
    "execution_runtime": "Runtime coordination and services shared by crew/flows during execution.",
    "execution_state": "State model for CrewAI flows and per-execution state tracking.",
    "llm_factory": "Unified LLM configuration for all providers with Creative vs Evaluation purpose profiles.",
    "output_process": "Post-processing of structured outputs (e.g. clean JSON).",
    "utils": "Shared helpers used across modules.",
}


def runtime_modules() -> dict[str, str]:
    """{module_name: one-line purpose} from the real src dir + README purposes."""
    src = _REPO_ROOT / "src" / "nikhil" / "amsha"
    present = {
        d.name
        for d in (src.iterdir() if src.is_dir() else [])
        if d.is_dir() and not d.name.startswith("__") and not d.name == "integration_tests"
    }
    names = [m for m in RUNTIME_MODULES if m in present]
    return {n: _MODULE_PURPOSE[n] for n in names}


def source_files_for(module: str) -> list[str]:
    """Relative paths of every non-pyc .py file under a module's src dir."""
    root = _REPO_ROOT / "src" / "nikhil" / "amsha" / module
    if not root.is_dir():
        return []
    files = [str(p.relative_to(root)) for p in sorted(root.rglob("*.py")) if not p.name.endswith(".pyc")]
    return files


# ---------------------------------------------------------------------------
# Content helpers
# ---------------------------------------------------------------------------

def get_preview(path: Path, max_lines: int = 15) -> str:
    """Return the leading prose of a file: headers, then non-empty text lines."""
    text = _read(path)
    if not text:
        return ""
    lines = [ln.rstrip() for ln in text.splitlines()]
    out: list[str] = []
    for ln in lines:
        if ln.startswith("#"):
            out.append(ln)
        elif ln.strip() and not ln.lstrip().startswith(("|", "```")):
            out.append(ln)
        if len(out) >= max_lines:
            break
    return "\n".join(out)


def extract_quickstart() -> str:
    """Return the `## Quick Start` code block from README, if present."""
    text = _read(_REPO_ROOT / "README.md")
    if not text:
        return ""
    m = re.search(r"## Quick Start[^\n]*\n(.*?)(?=\n## |\Z)", text, re.S)
    return m.group(1).strip() if m else ""


def extract_installation() -> str:
    """Return the `## Installation` section from README, if present."""
    text = _read(_REPO_ROOT / "README.md")
    if not text:
        return ""
    m = re.search(r"## Installation[^\n]*\n(.*?)(?=\n## |\Z)", text, re.S)
    return m.group(1).strip() if m else ""


def search(paths: dict[str, Path], query: str, max_hits: int = 20) -> list[dict]:
    """Case-insensitive keyword match over the given files, grouping by file.

    Each hit records the file, how many lines matched, and their (1-based) line
    numbers. Limit is by number of matching files, capped at max_hits.
    """
    q = query.lower()
    hits: list[dict] = []
    for name, path in sorted(paths.items()):
        text = _read(path)
        if not text:
            continue
        matched: list[int] = []
        for i, ln in enumerate(text.splitlines(), 1):
            if q in ln.lower():
                matched.append(i)
        if matched:
            hits.append({"file": name, "lines": matched[:8], "matches": len(matched), "path": str(path)})
    return hits[:max_hits]