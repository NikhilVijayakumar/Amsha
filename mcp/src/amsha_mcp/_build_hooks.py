"""Build helpers for packaging the MCP methodology documents.

Source checkouts author methodology in ``mcp/knowledge/`` with OKF
frontmatter. Builds materialize the runtime product plane under the installed
``amsha_mcp/docs`` package path with that frontmatter removed.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from setuptools.command.build_py import build_py as _build_py

MCP_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE = MCP_ROOT / "knowledge"
STAGED_PACKAGE_DOCS = MCP_ROOT / "build" / "package-docs" / "amsha_mcp" / "docs"

# Product-plane methodology only. Historical records remain repo knowledge and
# are no longer packaged for runtime search/lookup.
MAPPING: tuple[tuple[str, str], ...] = (
    ("methodology/prerequisite", "prerequisite"),
    ("methodology/implementation", "implementation"),
)

EXCLUDED_NAMES = {"index.md"}


def strip_frontmatter(text: str) -> str:
    """Return ``text`` without its leading OKF frontmatter block."""
    if not text.startswith("---\n"):
        raise ValueError("no OKF frontmatter block")
    lines = text.split("\n")
    for i, line in enumerate(lines[1:], start=1):
        if line.rstrip() == "---":
            return "\n".join(lines[i + 1:])
    raise ValueError("unterminated OKF frontmatter block")


def authored_doc_mappings() -> dict[Path, Path]:
    """Return {source concept: packaged relative path under docs/}."""
    mapping: dict[Path, Path] = {}
    for src_rel, dst_rel in MAPPING:
        src_dir = KNOWLEDGE / src_rel
        if not src_dir.is_dir():
            raise SystemExit(f"sync: missing bundle directory {src_dir}")
        concepts = sorted(
            p for p in src_dir.glob("*.md") if p.name not in EXCLUDED_NAMES
        )
        if not concepts:
            raise SystemExit(f"sync: no concepts found in {src_dir}")
        for concept in concepts:
            mapping[concept] = Path(dst_rel) / concept.name
    return mapping


def packaged_doc_relpaths() -> list[Path]:
    """Return packaged doc paths relative to the package root."""
    return [Path("docs") / rel for rel in authored_doc_mappings().values()]


def render_authored_doc(concept: Path) -> str:
    try:
        return strip_frontmatter(concept.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise SystemExit(f"sync: {concept.name}: {exc}") from exc


def materialize_package_docs(target_docs_root: Path, clean: bool = True) -> int:
    """Write the packaged methodology docs into ``target_docs_root``."""
    expected = {
        target_docs_root / rel: render_authored_doc(src)
        for src, rel in authored_doc_mappings().items()
    }

    if clean and target_docs_root.is_dir():
        for existing in sorted(target_docs_root.rglob("*.md")):
            if existing not in expected:
                existing.unlink()

    for dst, body in sorted(expected.items()):
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(body, encoding="utf-8")

    if clean and target_docs_root.is_dir():
        for directory in sorted(target_docs_root.rglob("*"), reverse=True):
            if directory.is_dir() and not any(directory.iterdir()):
                shutil.rmtree(directory)

    return len(expected)


class build_py(_build_py):
    """Materialize packaged methodology docs into the build output."""

    def run(self) -> None:
        super().run()
        package_root = Path(self.build_lib) / "amsha_mcp"
        count = materialize_package_docs(package_root / "docs")
        self.announce(
            f"materialized {count} methodology docs into {package_root / 'docs'}",
            level=2,
        )

    def get_outputs(self, include_bytecode: bool = True) -> list[str]:
        outputs = super().get_outputs(include_bytecode=include_bytecode)
        package_root = Path(self.build_lib) / "amsha_mcp"
        outputs.extend(str(package_root / rel) for rel in packaged_doc_relpaths())
        return outputs