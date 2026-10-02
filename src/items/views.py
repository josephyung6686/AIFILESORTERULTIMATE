"""Five read-only queries over items and live relationships.

None of these functions import or call `mutation.execute`. Semantic and
session edges never appear. Inferred links are omitted from the default graph
and counted as hidden.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePath

from items.profile_loader import ProfilePackage

DRAWABLE = frozenset({"approved"})
DRAWABLE_WITNESSED = frozenset({"duplicate-of", "attached-to"})
INFERRED = "inferred"


@dataclass(frozen=True)
class GraphView:
    nodes: tuple[dict, ...]
    edges: tuple[dict, ...]
    hidden_count: int
    cap: int


def folder_view(conn: sqlite3.Connection) -> list[dict]:
    """Live file/folder items grouped by the parent of `open_target`."""
    rows = conn.execute(
        "SELECT item_id, item_type, display_label, open_target, typing_state "
        "FROM items WHERE presence = 'live' AND superseded_by IS NULL "
        "AND item_type IN ('file', 'folder') ORDER BY open_target"
    ).fetchall()
    out = []
    for row in rows:
        target = row["open_target"] or ""
        parent = str(PurePath(target).parent) if target else ""
        out.append({
            "item_id": row["item_id"],
            "item_type": row["item_type"],
            "display_label": row["display_label"],
            "open_target": target,
            "parent": parent,
            "typing_state": row["typing_state"],
        })
    return out


def table_view(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT item_id, item_type, display_label, typing_state, open_target "
        "FROM items WHERE presence = 'live' AND superseded_by IS NULL "
        "ORDER BY display_label, item_id"
    ).fetchall()
    out = []
    for row in rows:
        links = conn.execute(
            "SELECT COUNT(*) AS n FROM relationships "
            "WHERE state = 'approved' AND superseded_by IS NULL "
            "AND (from_item_id = ? OR to_item_id = ?)",
            (row["item_id"], row["item_id"]),
        ).fetchone()["n"]
        out.append({
            "item_id": row["item_id"],
            "item_type": row["item_type"],
            "display_label": row["display_label"],
            "typing_state": row["typing_state"],
            "open_target": row["open_target"],
            "approved_links": links,
        })
    return out


def board_view(conn: sqlite3.Connection) -> dict[str, list[dict]]:
    """Columns per declared project/course; Unplaced for untyped files."""
    columns: dict[str, list[dict]] = {}
    hubs = conn.execute(
        "SELECT item_id, display_label FROM items "
        "WHERE presence = 'live' AND superseded_by IS NULL "
        "AND item_type IN ('project', 'course') ORDER BY display_label"
    ).fetchall()
    for hub in hubs:
        columns[hub["display_label"]] = []
    columns["Unplaced"] = []
    members = conn.execute(
        "SELECT r.from_item_id, r.to_item_id, i.item_id, i.display_label, "
        "i.typing_state, i.item_type "
        "FROM relationships r "
        "JOIN items i ON i.item_id = r.from_item_id "
        "WHERE r.rel_type = 'member-of' AND r.superseded_by IS NULL "
        "AND r.state IN ('approved', 'proposed') "
        "AND r.confidence IN ('witnessed', 'declared', 'corroborated')"
    ).fetchall()
    hub_ids = {h["item_id"]: h["display_label"] for h in hubs}
    placed: set[str] = set()
    for row in members:
        label = hub_ids.get(row["to_item_id"])
        if label is None:
            continue
        columns[label].append({
            "item_id": row["item_id"],
            "display_label": row["display_label"],
            "typing_state": row["typing_state"],
        })
        placed.add(row["item_id"])
    for row in conn.execute(
        "SELECT item_id, display_label, typing_state FROM items "
        "WHERE presence = 'live' AND superseded_by IS NULL "
        "AND item_type = 'file' AND typing_state = 'unplaced'"
    ):
        if row["item_id"] in placed:
            continue
        columns["Unplaced"].append({
            "item_id": row["item_id"],
            "display_label": row["display_label"],
            "typing_state": row["typing_state"],
        })
    return columns


def timeline_view(conn: sqlite3.Connection, *,
                  days: int = 90) -> list[dict]:
    if days <= 0:
        raise ValueError("days must be positive")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime(
        "%Y-%m-%dT%H:%M:%S+00:00")
    rows = conn.execute(
        "SELECT i.item_id, i.item_type, i.display_label, h.happened_at, h.ended_at "
        "FROM items i JOIN item_headers h ON h.item_id = i.item_id "
        "WHERE i.presence = 'live' AND i.superseded_by IS NULL "
        "AND h.happened_at IS NOT NULL AND h.happened_at >= ? "
        "ORDER BY h.happened_at",
        (cutoff,),
    ).fetchall()
    return [dict(r) for r in rows]


def graph_view(conn: sqlite3.Connection, *,
               center_item_id: str | None = None,
               profile: ProfilePackage | None = None) -> GraphView:
    """Neighborhood capped by the profile (default 40). Semantic edges never drawn."""
    cap = 40 if profile is None else profile.graph_cap
    if center_item_id:
        node_ids = _neighborhood(conn, center_item_id, cap)
    else:
        node_ids = _hubs_and_members(conn, cap)
    nodes = []
    for item_id in node_ids:
        row = conn.execute(
            "SELECT item_id, item_type, display_label, typing_state "
            "FROM items WHERE item_id = ?",
            (item_id,),
        ).fetchone()
        if row is not None:
            nodes.append(dict(row))
    edges = []
    hidden = 0
    if node_ids:
        placeholders = ",".join("?" * len(node_ids))
        rels = conn.execute(
            f"SELECT * FROM relationships WHERE superseded_by IS NULL "
            f"AND from_item_id IN ({placeholders}) "
            f"AND to_item_id IN ({placeholders})",
            (*node_ids, *node_ids),
        ).fetchall()
        for rel in rels:
            if rel["confidence"] == INFERRED:
                hidden += 1
                continue
            if rel["state"] == "approved" or (
                    rel["confidence"] == "witnessed"
                    and rel["rel_type"] in DRAWABLE_WITNESSED
                    and rel["state"] == "proposed"):
                edges.append({
                    "relationship_id": rel["relationship_id"],
                    "rel_type": rel["rel_type"],
                    "from_item_id": rel["from_item_id"],
                    "to_item_id": rel["to_item_id"],
                    "state": rel["state"],
                    "confidence": rel["confidence"],
                })
            elif rel["state"] == "proposed":
                hidden += 1
    # Semantic edges live only in group_edges — never counted here as drawn.
    return GraphView(
        nodes=tuple(nodes[:cap]),
        edges=tuple(edges),
        hidden_count=hidden,
        cap=cap,
    )


def _hubs_and_members(conn: sqlite3.Connection, cap: int) -> list[str]:
    ids: list[str] = []
    for row in conn.execute(
        "SELECT item_id FROM items WHERE presence = 'live' "
        "AND superseded_by IS NULL AND item_type IN ('project', 'course') "
        "ORDER BY display_label"
    ):
        ids.append(row["item_id"])
    for row in conn.execute(
        "SELECT from_item_id FROM relationships "
        "WHERE rel_type = 'member-of' AND state = 'approved' "
        "AND superseded_by IS NULL"
    ):
        if row["from_item_id"] not in ids:
            ids.append(row["from_item_id"])
        if len(ids) >= cap:
            break
    return ids[:cap]


def _neighborhood(conn: sqlite3.Connection, center: str, cap: int) -> list[str]:
    ids = [center]
    for row in conn.execute(
        "SELECT from_item_id, to_item_id FROM relationships "
        "WHERE superseded_by IS NULL "
        "AND (from_item_id = ? OR to_item_id = ?)",
        (center, center),
    ):
        for end in (row["from_item_id"], row["to_item_id"]):
            if end not in ids:
                ids.append(end)
            if len(ids) >= cap:
                return ids[:cap]
    return ids[:cap]


def paths_match_files_table(conn: sqlite3.Connection) -> bool:
    """Folder view open_target equals files.current_path for live file items."""
    rows = conn.execute(
        "SELECT i.open_target, f.current_path FROM items i "
        "JOIN files f ON f.file_id = i.file_id "
        "WHERE i.item_type = 'file' AND i.presence = 'live'"
    ).fetchall()
    return all(r["open_target"] == r["current_path"] for r in rows)
