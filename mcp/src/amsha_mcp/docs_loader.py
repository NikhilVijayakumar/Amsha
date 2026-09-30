"""Read Amsha documentation and source metadata from disk at query time.

Two distinct sources:

1. **Bundled methodology docs** — `amsha_mcp`'s own prerequisite/implementation
    material, shipped inside the package (`amsha_mcp/docs/`). In a source checkout
    with no packaged docs yet materialized, the loader falls back to the MCP-local
    OKF bundle in `mcp/knowledge/` and strips frontmatter at read time. These never
    depend on an outer-repo layout; a standalone wheel carries them.
2. **The target repo** — the Amsha-shaped repo this server instance was pointed
   at (an env var or `register_repo()`), from which we serve live README/docs and
   import the real crew schemas. `None` means "no repo registered": docs-serving
   tools return empty and schema tools report they cannot verify.

No authored content is copied into Python source: the OKF bundle stays the
single source of truth. If a doc changes, the server's answers change on the
next call in a source checkout, and on the next build for packaged artifacts.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent  # the installed amsha_mcp package dir
_SOURCE_MCP_ROOT = PACKAGE_ROOT.parent.parent

# Bundled methodology docs ship with the package (see pyproject package-data).
_DOCS = PACKAGE_ROOT / "docs"
_AUTHORED_DOCS = _SOURCE_MCP_ROOT / "knowledge" / "methodology"
# Frontmatter is stripped for any authored knowledge file, methodology or product.
_AUTHORED_KNOWLEDGE = _SOURCE_MCP_ROOT / "knowledge"

# Process-global target repo. Set at startup from AMSHA_MCP_TARGET_REPO (or a
# source-checkout default), and re-set by the register_repo tool. `None` = no repo.
_REPO_ROOT: Path | None = None
# Distinguishes "never resolved yet" from "explicitly configured to None" —
# repo_root() self-initializes on first access so any caller works correctly
# whether or not amsha_mcp.server (which also eagerly resolves at import time,
# for the deadlock guard) has been imported in this process.
_repo_resolved = False


def configure_repo_root(root: str | Path | None) -> None:
    """Point the loader at a (different) target repo root, or clear it (None)."""
    global _REPO_ROOT, _repo_resolved
    _REPO_ROOT = None if root is None else Path(root)
    _repo_resolved = True


def repo_root() -> Path | None:
    if not _repo_resolved:
        resolve_default_repo()
    return _REPO_ROOT


def resolve_default_repo() -> Path | None:
    """Set the target repo and return it: AMSHA_MCP_TARGET_REPO env var, else
    the enclosing Amsha checkout when running from a source tree (dev loop),
    else None (standalone install, no repo registered). Idempotent — safe to
    call eagerly (server.py, for the deadlock guard) and lazily (repo_root(),
    for any caller that imports tools directly without going through server.py)."""
    env = os.environ.get("AMSHA_MCP_TARGET_REPO")
    if env:
        configure_repo_root(Path(env).expanduser())
        return _REPO_ROOT
    checkout = PACKAGE_ROOT.parent.parent.parent  # mcp/src/amsha_mcp -> repo root
    if (checkout / "src" / "nikhil" / "amsha").is_dir():
        configure_repo_root(checkout)
        return _REPO_ROOT
    configure_repo_root(None)
    return None


def _read(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    try:
        path.relative_to(_AUTHORED_KNOWLEDGE)
    except ValueError:
        return text
    try:
        return _strip_frontmatter(text)
    except ValueError:
        return None


def _strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        raise ValueError("no OKF frontmatter block")
    lines = text.split("\n")
    for i, line in enumerate(lines[1:], start=1):
        if line.rstrip() == "---":
            return "\n".join(lines[i + 1:])
    raise ValueError("unterminated OKF frontmatter block")


def read_text(path: Path) -> str | None:
    """Read one doc, stripping OKF frontmatter for authored methodology files."""
    return _read(path)


def _docs_under(relative_dir: str, authored_relative_dir: str, pattern: str = "*.md") -> dict[str, Path]:
    """Return {filename: path} from packaged docs, else authored OKF sources.

    `relative_dir` is the packaged path under `docs/`; `authored_relative_dir` is
    the path under `knowledge/` (e.g. `methodology/prerequisite`, `product`).
    """
    base = _DOCS / relative_dir
    if base.is_dir():
        return {p.name: p for p in sorted(base.glob(pattern))}
    authored_base = _AUTHORED_KNOWLEDGE / authored_relative_dir
    return {p.name: p for p in sorted(authored_base.glob(pattern))} if authored_base.is_dir() else {}


def read_prerequisite() -> dict[str, Path]:
    """Bundled prerequisite/*.md keyed by filename (00-problem-definition.md ...)."""
    return _docs_under("prerequisite", "methodology/prerequisite")


def read_implementation() -> dict[str, Path]:
    """Bundled implementation/*.md keyed by filename."""
    return _docs_under("implementation", "methodology/implementation")


def read_product() -> dict[str, Path]:
    """Packaged Amsha product knowledge: module concepts + install/quickstart.

    This is the product plane -- it ships in the wheel so the server can answer
    what Amsha is, what its modules do, and how to install and start it, with no
    repository registered.
    """
    return _docs_under("product", "product")


def read_top_level_markdown() -> dict[str, Path]:
    """Target-repo root markdown we serve: README, USER_GUIDE, AGENTS."""
    root = repo_root()
    if not root:
        return {}
    names = ["README.md", "USER_GUIDE.md", "AGENTS.md", "DEPENDENCIES.md"]
    return {n: root / n for n in names if (root / n).is_file()}


def read_features_docs() -> dict[str, Path]:
    """Target-repo docs/feature/*/About.md keyed by module name (flat)."""
    root = repo_root()
    if not root:
        return {}
    base = root / "docs" / "feature"
    if not base.is_dir():
        return {}
    result: dict[str, Path] = {}
    for about in base.glob("*/*.md"):
        result[f"{about.parent.name}/{about.name}"] = about
    return dict(sorted(result.items()))


def read_knowledge_bundle() -> dict[str, Path]:
    """Target-repo knowledge/ OKF bundle, keyed by bundle-relative concept id.

    Repo plane only. The OKF bundle is repository knowledge by definition, so
    it is never part of the packaged plane and the standalone wheel is
    unaffected by its absence. A repo with no knowledge/ directory simply
    contributes nothing, exactly like a repo with no docs/feature/.
    """
    root = repo_root()
    if not root:
        return {}
    base = root / "knowledge"
    if not base.is_dir():
        return {}
    result: dict[str, Path] = {}
    for md in base.rglob("*.md"):
        if any(part.startswith(".") for part in md.relative_to(base).parts):
            continue
        result[str(md.relative_to(base))] = md
    return dict(sorted(result.items()))


# ---------------------------------------------------------------------------
# Module inventory (source of truth = the real src tree, not a hand list)
# ---------------------------------------------------------------------------

# Public runtime modules under src/nikhil/amsha, in dependency order.
#
# `common` is deliberately NOT listed: it holds cross-cutting internals
# (the logger, rotation helpers) rather than a capability a user selects, so
# `list_amsha_modules()` would offer it as something to inspect. The
# exclusion is intentional and its rationale lives here. `integration_tests`
# is not a runtime module and is likewise not served.
RUNTIME_MODULES = [
    "configuration",
    "crew_forge",
    "crew_monitor",
    "execution_runtime",
    "execution_state",
    "llm_factory",
    "output_process",
    "utils",
]

_MODULE_PURPOSE = {
    "configuration": "Layered config loading and validation (YAML, env, pydantic-settings) for crews, jobs, and LLMs.",
    "crew_forge": "Parse YAML/MongoDB crew definitions, build CrewAI crews/flows, and execute them.",
    "crew_monitor": "Real-time CPU/GPU/memory tracking, event-lifecycle logs, contribution analysis, and Excel reports.",
    "execution_runtime": "Runtime coordination and services shared by crew/flows during execution.",
    "execution_state": "State model for CrewAI flows and per-execution state tracking.",
    "llm_factory": "Unified LLM configuration for all providers with Creative vs Evaluation purpose profiles.",
    "output_process": "Post-processing of structured outputs (e.g. clean JSON).",
    "utils": "Shared helpers used across modules.",
}


def runtime_modules() -> dict[str, str]:
    """{module_name: one-line purpose} from the packaged product knowledge.

    The inventory comes from `docs/product/`, which ships in the wheel, so this
    answers with no repository registered. A registered repo is only used to
    *narrow* the list to modules actually present in that repo's source tree --
    a target repo may legitimately be an older or newer Amsha than the server.
    """
    purposes = {m: p for m, p in _packaged_module_purposes().items()}
    if not purposes:
        # Packaged knowledge unavailable (unusual: only reachable in a stripped
        # install). Fall back to the code-side table so the server still answers.
        purposes = dict(_MODULE_PURPOSE)
    root = repo_root()
    if not root:
        return purposes
    src = root / "src" / "nikhil" / "amsha"
    if not src.is_dir():
        return purposes
    present = {
        d.name
        for d in src.iterdir()
        if d.is_dir() and not d.name.startswith("__") and d.name != "integration_tests"
    }
    return {m: p for m, p in purposes.items() if m in present}


def product_concept(module: str) -> Path | None:
    """Path to a packaged product concept for a module, if one exists."""
    kebab = module.replace("_", "-")
    path = read_product().get(f"{kebab}.md")
    return path


def _packaged_module_purposes() -> dict[str, str]:
    """{module: purpose} from the packaged product concepts.

    Works from either origin: frontmatter in a source checkout, the packaged
    manifest in a wheel. Falls back to the concept's own first prose line, so a
    module is still described even if both are missing.
    """
    meta = product_metadata()
    out: dict[str, str] = {}
    for name, path in read_product().items():
        if name == "index.md":
            continue
        entry = meta.get(name, {})
        # A `section` marks a procedure reference (Installation, Quick Start), not
        # a module concept. Without this, filename-derivation would invent
        # "installation" and "quickstart" modules.
        if entry.get("section"):
            continue
        module = entry.get("module") or path.stem.replace("-", "_")
        if module not in RUNTIME_MODULES:
            continue
        purpose = entry.get("purpose") or entry.get("description")
        if not purpose:
            text = _read(path) or ""
            body = re.split(r"\n#\s+[^\n]*\n", text, maxsplit=1)
            for line in (body[1] if len(body) > 1 else "").splitlines():
                line = line.strip()
                if line and not line.startswith(("#", ">", "-", "|", "*", "`")):
                    purpose = line
                    break
        if purpose:
            out[module] = purpose
    return out


def _frontmatter_of(path: Path) -> dict[str, str]:
    """Parse the trivial `key: value` OKF frontmatter the product concepts use.

    Reads the file raw: `_read()` deliberately strips frontmatter for authored
    knowledge, so parsing it through `_read()` would always see no frontmatter.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {}
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    out: dict[str, str] = {}
    for line in text[4:end].split("\n"):
        if not line or line[:1] in (" ", "\t", "-"):
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip().strip('"')
    return out


def product_metadata() -> dict[str, dict[str, str]]:
    """Per-document machine facts for the product plane, keyed by filename.

    Prefers each concept's OKF frontmatter, which is what a source checkout has.
    Falls back to the packaged `manifest.json`, because the build strips
    frontmatter -- and the Python constraint cannot be re-derived from a concept
    body at all, as it originates in `pyproject.toml`.
    """
    docs = read_product()
    meta: dict[str, dict[str, str]] = {}
    for name, path in docs.items():
        if not name.endswith(".md"):
            continue
        front = _frontmatter_of(path)
        if front.get("module") or front.get("section"):
            meta[name] = dict(front)
    if meta:
        return meta
    manifest = _DOCS / "product" / "manifest.json"
    if not manifest.is_file():
        return {}
    try:
        documents = json.loads(manifest.read_text(encoding="utf-8")).get("documents", {})
    except (OSError, ValueError):
        return {}
    return {n: dict(d) for n, d in documents.items() if n in docs or not docs}


def _packaged_section(title: str) -> str:
    """Body of a packaged product concept for a README section, minus its H1.

    The concept body is the source section verbatim, so everything after the H1
    is what gets served -- there is no preamble to strip and no sub-heading
    boundary to guess at.
    """
    meta = product_metadata()
    for name, path in read_product().items():
        if meta.get(name, {}).get("section") != title:
            continue
        text = _read(path) or ""
        m = re.search(r"\n#\s+[^\n]*\n(.*)\Z", text, re.S)
        return m.group(1).strip() if m else ""
    return ""


def packaged_install_facts() -> dict[str, str]:
    """Structured install facts from the packaged concept: command, extra, Python floor."""
    for entry in product_metadata().values():
        if entry.get("section") != "Installation":
            continue
        return {
            "install": entry.get("install_command", ""),
            "optional_docling": entry.get("optional_extra", ""),
            "python": entry.get("requires_python", ""),
        }
    return {}


def source_files_for(module: str) -> list[str]:
    """Relative paths of every non-pyc .py file under a module's src dir."""
    base = repo_root()
    if not base:
        return []
    root = base / "src" / "nikhil" / "amsha" / module
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
    """The Quick Start procedure: target repo README if present, else packaged.

    The packaged concept is generated from the Amsha README's `## Quick Start`
    section, so a standalone install still gets real instructions instead of a
    pointer to a README it does not have.
    """
    root = repo_root()
    if root:
        text = _read(root / "README.md")
        if text:
            m = re.search(r"## Quick Start[^\n]*\n(.*?)(?=\n## |\Z)", text, re.S)
            if m:
                return m.group(1).strip()
    return _packaged_section("Quick Start")


def extract_installation() -> str:
    """The Installation procedure: target repo README if present, else packaged."""
    root = repo_root()
    if root:
        text = _read(root / "README.md")
        if text:
            m = re.search(r"## Installation[^\n]*\n(.*?)(?=\n## |\Z)", text, re.S)
            if m:
                return m.group(1).strip()
    return _packaged_section("Installation")


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
