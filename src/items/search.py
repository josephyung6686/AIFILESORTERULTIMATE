"""Read-only hybrid meaning search over the local item index.

Combines label/path text hits with optional embedding neighbours when versioned
vectors exist. Never moves a file. Never writes a relationship row. Protected
paths are counted as present-but-unopened.
"""
from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass

from items.mailbox import path_is_protected


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


_TOKEN = re.compile(r"[A-Za-z0-9_./-]+")


def meaning_search(conn: sqlite3.Connection, query: str, *,
                   limit: int = 25) -> SearchResult:
    """Search live items. Writes nothing. Embeddings alone invent no links."""
    if limit <= 0:
        raise ValueError("limit must be positive")
    tokens = [t.casefold() for t in _TOKEN.findall(query or "") if t.strip()]
    if not tokens:
        return SearchResult(hits=(), protected_count=0)

    scored: dict[str, SearchHit] = {}
    protected_count = 0
    rows = conn.execute(
        "SELECT item_id, display_label, open_target, typing_state, item_type "
        "FROM items WHERE presence = 'live' AND superseded_by IS NULL"
    ).fetchall()
    for row in rows:
        label = (row["display_label"] or "").casefold()
        target = (row["open_target"] or "").casefold()
        hay = f"{label} {target}"
        hits = sum(1 for token in tokens if token in hay)
        if hits == 0:
            continue
        protected = bool(row["open_target"] and path_is_protected(row["open_target"]))
        if protected:
            protected_count += 1
        scored[row["item_id"]] = SearchHit(
            item_id=row["item_id"],
            display_label=row["display_label"],
            open_target=None if protected else row["open_target"],
            typing_state=row["typing_state"],
            score=float(hits),
            channel="text",
            protected=protected,
        )

    # Optional: boost with any current vector neighbour already stored as a
    # mutual-semantic group edge — read-only, never projected into relationships.
    if _group_edges_installed(conn):
        for item_id, hit in list(scored.items()):
            file_id = conn.execute(
                "SELECT file_id FROM items WHERE item_id = ?", (item_id,)
            ).fetchone()
            if file_id is None or file_id["file_id"] is None:
                continue
            neighbours = conn.execute(
                "SELECT to_file_id AS other FROM group_edges "
                "WHERE from_file_id = ? AND edge_type = 'mutual-semantic-retrieval' "
                "AND superseded_by IS NULL "
                "UNION "
                "SELECT from_file_id AS other FROM group_edges "
                "WHERE to_file_id = ? AND edge_type = 'mutual-semantic-retrieval' "
                "AND superseded_by IS NULL",
                (file_id["file_id"], file_id["file_id"]),
            ).fetchall()
            for neighbour in neighbours:
                other = conn.execute(
                    "SELECT item_id, display_label, open_target, typing_state "
                    "FROM items WHERE file_id = ? AND presence = 'live' "
                    "AND superseded_by IS NULL LIMIT 1",
                    (neighbour["other"],),
                ).fetchone()
                if other is None:
                    continue
                protected = bool(
                    other["open_target"] and path_is_protected(other["open_target"]))
                if protected:
                    protected_count += 1
                prior = scored.get(other["item_id"])
                score = (prior.score if prior else 0.0) + 0.5
                scored[other["item_id"]] = SearchHit(
                    item_id=other["item_id"],
                    display_label=other["display_label"],
                    open_target=None if protected else other["open_target"],
                    typing_state=other["typing_state"],
                    score=score,
                    channel="hybrid" if prior else "semantic",
                    protected=protected,
                )

    ordered = sorted(scored.values(), key=lambda h: (-h.score, h.display_label))
    return SearchResult(
        hits=tuple(ordered[:limit]),
        protected_count=protected_count,
        moved=False,
    )


def _group_edges_installed(conn: sqlite3.Connection) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'group_edges'"
    ).fetchone() is not None
