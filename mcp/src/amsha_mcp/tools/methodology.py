"""Tools for the prerequisite/implementation design methodology.

These are the seam Phase 2 builds on: read the raw stage content (possibly
summarized) via the module path shown in proposal 01, ready for a sequencing
layer to call them in order.
"""
from __future__ import annotations

import re
from pathlib import Path

from .. import docs_loader as dl


def _stage_text(path: Path, summarize: bool) -> str:
    text = path.read_text(encoding="utf-8")
    if not summarize:
        return text
    return _summarize(text)


def _summarize(text: str, max_lines: int = 40) -> str:
    """Keep headers + checklist-bearing lines so the crux survives summary."""
    out: list[str] = []
    for ln in text.splitlines():
        stripped = ln.strip()
        if not stripped:
            continue
        if stripped.startswith("#") or stripped.startswith("- [ ]") or stripped.startswith("* [ ]"):
            out.append(stripped)
        elif re.match(r"^\d+\.\s", stripped) and len(out) < max_lines:
            out.append(stripped.rstrip())
        if len(out) >= max_lines:
            break
    return "\n".join(out)


def get_prerequisite_stage(stage: str, summarize: bool = False) -> dict:
    """Return content of one prerequisite doc (stage '00'–'09')."""
    files = dl.read_prerequisite()
    return _read_named(files, stage, "prerequisite", summarize)


def get_implementation_guide(topic: str, summarize: bool = False) -> dict:
    """Return content of one implementation doc (topic '00'–'23')."""
    files = dl.read_implementation()
    return _read_named(files, topic, "implementation", summarize)


def _read_named(files: dict[str, Path], key: str, kind: str, summarize: bool) -> dict:
    if not key.isdigit():
        return {"error": f"Invalid {kind} id '{key}'. Expected a number."}
    prefix = key if len(key) == 2 else key.zfill(2)
    match = [name for name in files if name.startswith(f"{prefix}-")]
    if not match:
        known = "\n".join(files) or "none discovered"
        return {"error": f"Unknown {kind} '{key}'. Available:\n{known}", "kind": kind}
    path = files[match[0]]
    return {"kind": kind, "id": key, "title": path.name, "content": _stage_text(path, summarize)}