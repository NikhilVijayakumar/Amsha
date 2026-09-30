"""Search tool over Amsha's docs, README, and methodology."""
from __future__ import annotations

from pathlib import Path

from .. import docs_loader as dl


def search_amsha_docs(query: str) -> dict:
    """Keyword search across packaged methodology and repo knowledge.

    The packaged groups are always available. The repo groups contribute
    nothing when no repository is registered, which keeps this tool working in
    a standalone install.
    """
    merged: dict[str, Path] = {}
    for group in (
        dl.read_prerequisite(),
        dl.read_implementation(),
        dl.read_top_level_markdown(),
        dl.read_features_docs(),
        dl.read_knowledge_bundle(),
    ):
        merged.update(group)
    # Namespaced: product concepts and the repo knowledge bundle both contain an
    # `index.md`, so merging on bare filenames would let one mask the other and
    # mis-attribute hits.
    for name, path in dl.read_product().items():
        merged[f"product/{name}"] = path
    hits = dl.search(merged, query)
    return {
        "query": query,
        "count": len(hits),
        "note": "Keyword line matches; file+line references for follow-up reading.",
        "hits": hits,
    }