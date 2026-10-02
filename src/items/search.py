"""Read-only hybrid meaning search over the local item index.

Delegates to ``hot_index.find_files`` (FTS5 + vectors + RRF). Never moves a
file. Never writes a relationship row. Protected paths are counted as
present-but-unopened.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from items.hot_index import find_files


@dataclass(frozen=True)
class SearchHit:
    item_id: str
    display_label: str
    open_target: str | None
    typing_state: str
    score: float
    channel: str
    protected: bool


@dataclass(frozen=True)
class SearchResult:
    hits: tuple[SearchHit, ...]
    protected_count: int
    moved: bool = False
    fts_ms: float = 0.0
    vector_ms: float = 0.0
    total_ms: float = 0.0


def meaning_search(conn: sqlite3.Connection, query: str, *,
                   limit: int = 25,
                   model_dir: Path | None = None) -> SearchResult:
    """Search live items. Writes nothing. Embeddings alone invent no links."""
    raw = find_files(conn, query, limit=limit, model_dir=model_dir)
    hits = tuple(
        SearchHit(
            item_id=h.item_id,
            display_label=h.display_label,
            open_target=h.open_target,
            typing_state=h.typing_state,
            score=h.score,
            channel="+".join(h.channels) if h.channels else "none",
            protected=h.protected,
        )
        for h in raw.hits
    )
    return SearchResult(
        hits=hits,
        protected_count=raw.protected_count,
        moved=False,
        fts_ms=raw.fts_ms,
        vector_ms=raw.vector_ms,
        total_ms=raw.total_ms,
    )
