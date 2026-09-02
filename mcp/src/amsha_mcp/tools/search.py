"""Search tool over Amsha's docs, README, and methodology."""
from __future__ import annotations

from .. import docs_loader as dl


def search_amsha_docs(query: str) -> dict:
    """Keyword search across mcp/docs/ + docs/ (features) + top-level markdown."""
    merged: dict[str, Path] = {}
    for group in (
        dl.read_prerequisite(),
        dl.read_implementation(),
        dl.read_proposal(),
        dl.read_top_level_markdown(),
        dl.read_features_docs(),
    ):
        merged.update(group)
    hits = dl.search(merged, query)
    return {
        "query": query,
        "count": len(hits),
        "note": "Keyword line matches; file+line references for follow-up reading.",
        "hits": hits,
    }