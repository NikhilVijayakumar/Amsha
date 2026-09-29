"""Search tool over Amsha's docs, README, and methodology."""
from __future__ import annotations

from pathlib import Path

from .. import docs_loader as dl


def search_amsha_docs(query: str) -> dict:
    """Keyword search across the packaged methodology, mcp/docs/, and repo knowledge.

    The packaged groups are always available. The repo groups contribute
    nothing when no repository is registered, which keeps this tool working in
    a standalone install.
    """
    merged: dict[str, Path] = {}
    for group in (
        dl.read_prerequisite(),
        dl.read_implementation(),
        dl.read_proposal(),
        dl.read_top_level_markdown(),
        dl.read_features_docs(),
        dl.read_knowledge_bundle(),
    ):
        merged.update(group)
    hits = dl.search(merged, query)
    return {
        "query": query,
        "count": len(hits),
        "note": "Keyword line matches; file+line references for follow-up reading.",
        "hits": hits,
    }