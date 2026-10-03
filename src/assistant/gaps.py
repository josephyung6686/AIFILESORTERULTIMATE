"""File/profile gaps — list_gaps."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


def list_gaps(conn: sqlite3.Connection, *, limit: int = 30) -> dict[str, Any]:
    """Surface unplaced / held / missing-on-disk / lonely (no live edges)."""
    limit = max(1, min(limit, 50))
    gaps: list[dict[str, Any]] = []

    for row in conn.execute(
        "SELECT item_id, display_label, typing_state, open_target "
        "FROM items WHERE presence='live' AND item_type='file' "
        "AND typing_state IN ('unplaced','held') "
        "ORDER BY created_at DESC LIMIT ?",
        (limit,),
    ):
        gaps.append({
            "kind": "typing",
            "item_id": row["item_id"],
            "display_label": row["display_label"],
            "detail": f"typing_state={row['typing_state']}",
        })

    # Missing on disk
    for row in conn.execute(
        "SELECT item_id, display_label, open_target FROM items "
        "WHERE presence='live' AND item_type='file' "
        "AND open_target IS NOT NULL LIMIT 200"
    ):
        p = Path(row["open_target"])
        if not p.is_file():
            gaps.append({
                "kind": "missing_on_disk",
                "item_id": row["item_id"],
                "display_label": row["display_label"],
                "detail": f"open_target gone: {row['open_target']}",
            })
        if len(gaps) >= limit * 2:
            break

    # No relationships (if table exists)
    has = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='relationships'"
    ).fetchone()
    if has:
        for row in conn.execute(
            "SELECT i.item_id, i.display_label FROM items i "
            "WHERE i.presence='live' AND i.item_type='file' "
            "AND NOT EXISTS ("
            "  SELECT 1 FROM relationships r "
            "  WHERE r.superseded_by IS NULL "
            "  AND (r.from_item_id=i.item_id OR r.to_item_id=i.item_id)"
            ") LIMIT ?",
            (limit,),
        ):
            gaps.append({
                "kind": "no_links",
                "item_id": row["item_id"],
                "display_label": row["display_label"],
                "detail": "no live relationships",
            })

    from items.identity import excluded_areas
    return {
        "ok": True,
        "gaps": gaps[:limit],
        "excluded_areas": excluded_areas(conn),
        "moved": False,
        "note": "file/profile gaps only",
    }
