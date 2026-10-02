"""Witnessed life links. Semantic neighbours stay in `group_edges`.

Stage 2 of the item-relationship model. A relationship row is a projection a
person can approve or reject. It is not a float weight and it is not a
grouping channel.

Projected:

- equal `content_hash` on two live file items → `duplicate-of` (source `scan`)
- live `group_edges` of type `duplicate` / `version-family` with non-empty
  `evidence_ref` → `duplicate-of` / `version-of` (source `grouping`)

Refused:

- `mutual-semantic-retrieval` and `bounded-session` (already non-anchoring)
- any edge whose `evidence_ref` is empty
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone

from grouping.vocabulary import DUPLICATE, VERSION_FAMILY
from items.decisions import basis_is_rejected
from items.schema import create_items_schema

REL_DUPLICATE = "duplicate-of"
REL_VERSION = "version-of"

_EDGE_TO_REL = {
    DUPLICATE: REL_DUPLICATE,
    VERSION_FAMILY: REL_VERSION,
}

CONFIDENCE_WITNESSED = "witnessed"
STATE_PROPOSED = "proposed"
SOURCE_SCAN = "scan"
SOURCE_GROUPING = "grouping"


def project_witnessed_links(conn: sqlite3.Connection) -> int:
    """Insert proposed witnessed links. Returns how many new rows were written."""
    if not _items_installed(conn):
        return 0
    create_items_schema(conn)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    written = 0
    written += _project_hash_duplicates(conn, now)
    if _group_edges_installed(conn):
        written += _project_group_edges(conn, now)
    return written


def _items_installed(conn: sqlite3.Connection) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'items'"
    ).fetchone()
    return row is not None


def _group_edges_installed(conn: sqlite3.Connection) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'group_edges'"
    ).fetchone()
    return row is not None


def _project_hash_duplicates(conn: sqlite3.Connection, now: str) -> int:
    rows = conn.execute(
        "SELECT i.item_id, f.content_hash FROM items i "
        "JOIN files f ON f.file_id = i.file_id "
        "WHERE i.item_type = 'file' AND i.presence = 'live' "
        "AND i.superseded_by IS NULL AND f.content_hash IS NOT NULL "
        "ORDER BY f.content_hash, i.item_id"
    ).fetchall()
    by_hash: dict[str, list[str]] = {}
    for row in rows:
        by_hash.setdefault(row["content_hash"], []).append(row["item_id"])
    written = 0
    for content_hash, item_ids in by_hash.items():
        if len(item_ids) < 2:
            continue
        # Pair each live twin with the earliest item_id so the basis is stable.
        anchor = item_ids[0]
        for other in item_ids[1:]:
            if _insert_link(
                    conn,
                    rel_type=REL_DUPLICATE,
                    left=anchor,
                    right=other,
                    source=SOURCE_SCAN,
                    evidence_refs=["content_hash", content_hash],
                    now=now,
            ):
                written += 1
    return written


def _project_group_edges(conn: sqlite3.Connection, now: str) -> int:
    edges = conn.execute(
        "SELECT edge_id, from_file_id, to_file_id, edge_type, evidence_ref "
        "FROM group_edges WHERE superseded_by IS NULL "
        "AND edge_type IN (?, ?)",
        (DUPLICATE, VERSION_FAMILY),
    ).fetchall()
    written = 0
    for edge in edges:
        evidence = (edge["evidence_ref"] or "").strip()
        if not evidence:
            continue
        rel_type = _EDGE_TO_REL[edge["edge_type"]]
        left = _item_for_file(conn, edge["from_file_id"])
        right = _item_for_file(conn, edge["to_file_id"])
        if left is None or right is None or left == right:
            continue
        if _insert_link(
                conn,
                rel_type=rel_type,
                left=left,
                right=right,
                source=SOURCE_GROUPING,
                evidence_refs=[edge["edge_id"], evidence],
                now=now,
        ):
            written += 1
    return written


def _item_for_file(conn: sqlite3.Connection, file_id: str) -> str | None:
    row = conn.execute(
        "SELECT item_id FROM items WHERE file_id = ? AND item_type = 'file' "
        "AND superseded_by IS NULL ORDER BY created_at LIMIT 1",
        (file_id,),
    ).fetchone()
    return None if row is None else row["item_id"]


def _insert_link(
        conn: sqlite3.Connection, *, rel_type: str, left: str, right: str,
        source: str, evidence_refs: list[str], now: str) -> bool:
    a, b = sorted((left, right))
    fingerprint = sorted(evidence_refs)
    basis = json.dumps(
        {"rel_type": rel_type, "from": a, "to": b, "evidence": fingerprint},
        sort_keys=True,
    )
    if basis_is_rejected(conn, basis):
        return False
    existing = conn.execute(
        "SELECT relationship_id FROM relationships WHERE basis_key = ? "
        "AND superseded_by IS NULL",
        (basis,),
    ).fetchone()
    if existing is not None:
        return False
    if not fingerprint or any(not ref for ref in fingerprint):
        raise ValueError("a witnessed link refuses empty evidence")
    conn.execute(
        "INSERT INTO relationships ("
        "relationship_id, rel_type, from_item_id, to_item_id, confidence, "
        "source, state, evidence_refs, basis_key, created_at, supersedes, "
        "superseded_by"
        ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL)",
        (
            str(uuid.uuid4()), rel_type, a, b, CONFIDENCE_WITNESSED, source,
            STATE_PROPOSED, json.dumps(fingerprint, sort_keys=True), basis, now,
        ),
    )
    return True
