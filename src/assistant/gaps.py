"""File/profile nudges — list_gaps + deadline enrichment."""
from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_DATE_IN_NAME = re.compile(
    r"(20\d{2}[-_/]?(0[1-9]|1[0-2])[-_/]?(0[1-9]|[12]\d|3[01]))"
)


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

    return {
        "ok": True,
        "gaps": gaps[:limit],
        "moved": False,
        "note": "file/profile gaps only",
    }


def filename_date_hints(
        conn: sqlite3.Connection, *, limit: int = 20,
) -> list[dict[str, Any]]:
    """Deadlines inferred from YYYY-MM-DD-ish names (weak signal)."""
    out: list[dict[str, Any]] = []
    for row in conn.execute(
        "SELECT item_id, display_label FROM items "
        "WHERE presence='live' AND item_type='file' "
        "ORDER BY created_at DESC LIMIT 400"
    ):
        label = row["display_label"] or ""
        m = _DATE_IN_NAME.search(label)
        if not m:
            continue
        raw = m.group(1).replace("_", "-").replace("/", "-")
        if len(raw) == 8 and raw.isdigit():
            raw = f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
        out.append({
            "item_id": row["item_id"],
            "display_label": label,
            "hint_date": raw,
            "source": "filename",
            "weak": True,
        })
        if len(out) >= limit:
            break
    return out


def enriched_deadlines(
        conn: sqlite3.Connection, *, limit: int = 15,
) -> dict[str, Any]:
    """Merge fixture deadline_view with filename date hints."""
    rows: list[Any] = []
    try:
        from items.deadline_view import deadline_view
        view = deadline_view(conn)
        rows = list(view.get("deadlines") or [])
    except Exception:
        rows = []
    hints = filename_date_hints(conn, limit=limit)
    return {
        "deadlines": rows[:limit],
        "filename_date_hints": hints,
        "as_of": datetime.now(timezone.utc).isoformat(),
        "moved": False,
    }
