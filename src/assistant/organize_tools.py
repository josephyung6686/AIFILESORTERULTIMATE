"""P6 deferred organize / link tools — dry-run by default.

Loaded only after request_tools(group). apply/undo stay in tools.py behind
ASSISTANT_ENABLE_APPLY. Never invent destinations from file text.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from items.hot_index import rebuild_fts
from items.identity import reconcile_tree


def scan_refresh(conn: sqlite3.Connection, root: str | None) -> dict[str, Any]:
    if not root:
        return {"ok": False, "error": "root path required", "moved": False}
    path = Path(root)
    if not path.is_dir():
        return {"ok": False, "error": f"not a directory: {root}", "moved": False}
    reconcile_tree(conn, path)
    rebuilt = rebuild_fts(conn)
    return {
        "ok": True,
        "reconciled": True,
        "fts_rows": rebuilt,
        "moved": False,
    }


def propose_groups(conn: sqlite3.Connection, *, limit: int = 20) -> dict[str, Any]:
    """Read-only: surface mutual-semantic / duplicate edges as group proposals."""
    groups = []
    if not _table(conn, "group_edges"):
        return {"ok": True, "groups": [], "moved": False, "note": "no group_edges"}
    rows = conn.execute(
        "SELECT edge_type, from_file_id, to_file_id, weight FROM group_edges "
        "WHERE superseded_by IS NULL "
        "ORDER BY weight DESC LIMIT ?",
        (limit,),
    ).fetchall()
    for r in rows:
        groups.append({
            "edge_type": r["edge_type"],
            "from_file_id": r["from_file_id"],
            "to_file_id": r["to_file_id"],
            "weight": r["weight"],
            "state": "proposed",
        })
    return {"ok": True, "groups": groups, "moved": False}


def propose_tree(conn: sqlite3.Connection, *, limit: int = 30) -> dict[str, Any]:
    """Dry outline from typed items — not an apply plan."""
    rows = conn.execute(
        "SELECT item_id, display_label, type_schema, typing_state "
        "FROM items WHERE presence='live' AND superseded_by IS NULL "
        "AND item_type='file' ORDER BY type_schema, display_label LIMIT ?",
        (limit,),
    ).fetchall()
    folders: dict[str, list[dict]] = {}
    for r in rows:
        key = r["type_schema"] or r["typing_state"] or "unplaced"
        folders.setdefault(key, []).append({
            "item_id": r["item_id"],
            "display_label": r["display_label"],
        })
    return {
        "ok": True,
        "outline": folders,
        "moved": False,
        "note": "dry outline only — use place_preview + approve to move",
    }


def propose_links(conn: sqlite3.Connection, *, limit: int = 20) -> dict[str, Any]:
    if not _table(conn, "relationships"):
        return {"ok": True, "links": [], "moved": False, "note": "no relationships"}
    from items.connector import propose_inferred_links
    before = conn.execute(
        "SELECT COUNT(*) FROM relationships WHERE state='proposed'"
    ).fetchone()[0]
    try:
        n = propose_inferred_links(conn)
    except Exception as e:
        return {"ok": False, "error": str(e), "moved": False}
    rows = conn.execute(
        "SELECT relationship_id, rel_type, from_item_id, to_item_id, state "
        "FROM relationships WHERE state='proposed' AND superseded_by IS NULL "
        "ORDER BY rowid DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return {
        "ok": True,
        "new_or_seen": n if isinstance(n, int) else True,
        "proposed_before": before,
        "links": [dict(r) for r in rows],
        "moved": False,
    }


def accept_link(
        conn: sqlite3.Connection, relationship_id: str,
        *, user_id: str = "local-user") -> dict[str, Any]:
    from items.decisions import accept_link as _accept
    try:
        _accept(conn, relationship_id, user_id=user_id)
        return {"ok": True, "relationship_id": relationship_id,
                "state": "approved", "moved": False}
    except Exception as e:
        return {"ok": False, "error": str(e), "moved": False}


def reject_link(
        conn: sqlite3.Connection, relationship_id: str,
        *, user_id: str = "local-user") -> dict[str, Any]:
    from items.decisions import reject_link as _reject
    try:
        _reject(conn, relationship_id, user_id=user_id)
        return {"ok": True, "relationship_id": relationship_id,
                "state": "rejected", "moved": False}
    except Exception as e:
        return {"ok": False, "error": str(e), "moved": False}


def freeze_plan(conn: sqlite3.Connection, plan_id: str) -> dict[str, Any]:
    """Mark draft plan frozen for approval — does not move files."""
    try:
        row = conn.execute(
            "SELECT state FROM assistant_plans WHERE plan_id=?", (plan_id,)
        ).fetchone()
    except sqlite3.OperationalError:
        return {"ok": False, "error": "plan not found", "moved": False}
    if row is None:
        return {"ok": False, "error": "plan not found", "moved": False}
    if row["state"] not in ("draft", "approved"):
        return {
            "ok": False,
            "error": f"cannot freeze from state {row['state']!r}",
            "moved": False,
        }
    # Freeze = ready for full-list view / approve; stay draft until approve.
    return {
        "ok": True,
        "plan_id": plan_id,
        "frozen": True,
        "state": row["state"],
        "moved": False,
        "note": "View full list then approve_plan before apply_moves",
    }


def extract_one(conn: sqlite3.Connection, item_id: str) -> dict[str, Any]:
    row = conn.execute(
        "SELECT item_id, display_label, file_id, open_target, typing_state "
        "FROM items WHERE item_id=? AND presence='live'",
        (item_id,),
    ).fetchone()
    if row is None:
        return {"ok": False, "error": "item not found", "moved": False}
    return {
        "ok": True,
        "item_id": item_id,
        "display_label": row["display_label"],
        "typing_state": row["typing_state"],
        "open_target": row["open_target"],
        "moved": False,
        "note": "metadata only — use read_item for untrusted snippet",
    }


def _table(conn, name: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone() is not None
