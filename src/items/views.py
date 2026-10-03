"""Five read-only queries over items and live relationships.

None of these functions import or call `mutation.execute`. Semantic and
session edges never appear. Inferred links are omitted from the default graph
and counted as hidden.

Graph and Board draw through `relationship_service.project_relationships`.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import PurePath

from items.profile_loader import ProfilePackage
from items.relationship_service import (
    project_relationships,
    projection_hidden_count,
)


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
        approved = sum(
            1 for e in project_relationships(
                conn, surface="list_related", item_id=row["item_id"])
            if e["state"] == "approved"
        )
        out.append({
            "item_id": row["item_id"],
            "item_type": row["item_type"],
            "display_label": row["display_label"],
            "typing_state": row["typing_state"],
            "open_target": row["open_target"],
            "approved_links": approved,
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
    members = project_relationships(conn, surface="board", rel_type="member-of")
    hub_ids = {h["item_id"]: h["display_label"] for h in hubs}
    placed: set[str] = set()
    for row in members:
        label = hub_ids.get(row["to_item_id"])
        if label is None:
            continue
        item = conn.execute(
            "SELECT item_id, display_label, typing_state, item_type "
            "FROM items WHERE item_id = ?",
            (row["from_item_id"],),
        ).fetchone()
        if item is None:
            continue
        columns[label].append({
            "item_id": item["item_id"],
            "display_label": item["display_label"],
            "typing_state": item["typing_state"],
        })
        placed.add(item["item_id"])
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
    if node_ids:
        node_set = set(node_ids)
        for rel in project_relationships(conn, surface="graph"):
            if (rel["from_item_id"] in node_set
                    and rel["to_item_id"] in node_set):
                edges.append({
                    "relationship_id": rel["relationship_id"],
                    "rel_type": rel["rel_type"],
                    "from_item_id": rel["from_item_id"],
                    "to_item_id": rel["to_item_id"],
                    "state": rel["state"],
                    "confidence": rel["confidence"],
                })
        hidden = projection_hidden_count(
            conn, surface="graph", among=node_ids)
    else:
        hidden = 0
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
    for edge in project_relationships(
            conn, surface="list_related", rel_type="member-of"):
        if edge["state"] != "approved":
            continue
        if edge["from_item_id"] not in ids:
            ids.append(edge["from_item_id"])
        if len(ids) >= cap:
            break
    return ids[:cap]


def _neighborhood(conn: sqlite3.Connection, center: str, cap: int) -> list[str]:
    ids = [center]
    for edge in project_relationships(
            conn, surface="list_related", item_id=center):
        for end in (edge["from_item_id"], edge["to_item_id"]):
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
