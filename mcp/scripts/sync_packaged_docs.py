#!/usr/bin/env python3
"""Materialize build-staged methodology docs from the MCP-local OKF bundle.

The runtime methodology documents are authored once, in `mcp/knowledge/`, as
OKF concepts. This script materializes the frontmatter-free product form into a
build staging tree. Package builds then copy the same content into the wheel at
`amsha_mcp/docs/`.

Authored:  mcp/knowledge/methodology/**/*.md                (with frontmatter)
Staged:    mcp/build/package-docs/amsha_mcp/docs/**/*.md    (body only)

Usage:
    python3 scripts/sync_packaged_docs.py            # write staged docs
    python3 scripts/sync_packaged_docs.py --check    # validate generation and staged tree if present
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from amsha_mcp._build_hooks import MCP_ROOT, STAGED_PACKAGE_DOCS, authored_doc_mappings, materialize_package_docs, render_authored_doc


def check(mapping: dict[Path, Path]) -> int:
    """Validate generation and compare against the staged tree when present."""
    expected = {dst: render_authored_doc(src) for src, dst in mapping.items()}

    if not STAGED_PACKAGE_DOCS.is_dir():
        print(f"sync --check: bundle is build-ready; no staged tree at {STAGED_PACKAGE_DOCS}")
        return 0

    actual = {p for p in STAGED_PACKAGE_DOCS.rglob("*.md") if p.is_file()}
    drifted: list[Path] = []
    for dst, body in expected.items():
        if dst not in actual:
            drifted.append(dst)
        elif dst.read_text(encoding="utf-8") != body:
            drifted.append(dst)
    extra = sorted(actual - set(expected))

    if drifted or extra:
        for path in sorted(drifted):
            print(f"FAIL diverges from bundle: {path.relative_to(MCP_ROOT)}", file=sys.stderr)
        for path in extra:
            print(f"FAIL not produced by bundle: {path.relative_to(MCP_ROOT)}", file=sys.stderr)
        print(
            f"sync --check: {len(drifted)} diverging, {len(extra)} unexpected "
            f"(of {len(expected)} expected)",
            file=sys.stderr,
        )
        return 1

    print(f"sync --check: {len(expected)} files match the bundle")
    return 0


def write(mapping: dict[Path, Path]) -> int:
    """Regenerate the staged tree. Remove anything the bundle no longer produces."""
    expected = {dst: render_authored_doc(src) for src, dst in mapping.items()}

    if STAGED_PACKAGE_DOCS.is_dir():
        for existing in sorted(STAGED_PACKAGE_DOCS.rglob("*.md")):
            if existing not in expected:
                existing.unlink()
                print(f"  removed stale {existing.relative_to(MCP_ROOT)}")

    for dst, body in sorted(expected.items()):
        changed = not dst.is_file() or dst.read_text(encoding="utf-8") != body
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(body, encoding="utf-8")
        if changed:
            print(f"  wrote {dst.relative_to(MCP_ROOT)}")

    if STAGED_PACKAGE_DOCS.is_dir():
        for directory in sorted(STAGED_PACKAGE_DOCS.rglob("*"), reverse=True):
            if directory.is_dir() and not any(directory.iterdir()):
                shutil.rmtree(directory)

    materialize_package_docs(STAGED_PACKAGE_DOCS)
    print(f"sync: {len(expected)} documents generated into {STAGED_PACKAGE_DOCS}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the packaged tree matches the bundle; write nothing; "
             "exit non-zero on drift, absence, or unexpected files",
    )
    args = parser.parse_args(argv)
    mapping = {src: STAGED_PACKAGE_DOCS / rel for src, rel in authored_doc_mappings().items()}
    return check(mapping) if args.check else write(mapping)


if __name__ == "__main__":
    raise SystemExit(main())
