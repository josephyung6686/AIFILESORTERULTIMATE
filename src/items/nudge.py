"""Nudge: local warnings from profile required pairs. No writes to approvals.

Uses the canonical relationship projection. No dates, no calendar events.
"""
from __future__ import annotations

import sqlite3

from items.profile_loader import ProfilePackage
from items.relationship_service import project_relationships
from items.schema import create_items_schema


def warnings(
        conn: sqlite3.Connection, *,
        profile: ProfilePackage | None) -> list[dict]:
    """Return warning dicts. Does not insert relationships or move files."""
    create_items_schema(conn)
    pairs = []
    if profile is not None:
        pairs = list(profile.raw.get("required_pairs") or [])
    if not pairs:
        # Default student pair: a course expects an academic member-of file.
        pairs = [{
            "hub_type": "course",
            "need_rel": "member-of",
            "need_type_schema": "academic",
        }]
    out: list[dict] = []
    for pair in pairs:
        out.extend(_check_pair(conn, pair))
    return out


def _check_pair(conn, pair: dict) -> list[dict]:
    hub_type = pair.get("hub_type", "course")
    need_rel = pair.get("need_rel", "member-of")
    need_schema = pair.get("need_type_schema")
    hubs = conn.execute(
        "SELECT item_id, display_label FROM items "
        "WHERE item_type = ? AND presence = 'live' AND superseded_by IS NULL "
        "ORDER BY display_label",
        (hub_type,),
    ).fetchall()
    found = []
    for hub in hubs:
        if _has_member(conn, hub["item_id"], need_rel, need_schema):
            continue
        found.append({
            "kind": "missing_member_of",
            "hub_item_id": hub["item_id"],
            "hub": hub["display_label"],
            "message": (
                f"{hub_type} {hub['display_label']} has no "
                f"{need_schema or 'typed'} file linked as {need_rel}."
            ),
            "evidence_refs": [f"hub:{hub['item_id']}"],
        })
    return found


def _has_member(conn, hub_id: str, rel_type: str, type_schema: str | None) -> bool:
    for edge in project_relationships(
            conn, surface="nudge", item_id=hub_id, rel_type=rel_type):
        if edge["to_item_id"] != hub_id and edge["from_item_id"] != hub_id:
            continue
        file_id = (
            edge["from_item_id"] if edge["to_item_id"] == hub_id
            else edge["to_item_id"]
        )
        row = conn.execute(
            "SELECT item_type, type_schema FROM items WHERE item_id = ?",
            (file_id,),
        ).fetchone()
        if row is None or row["item_type"] != "file":
            continue
        if type_schema and row["type_schema"] != type_schema:
            continue
        return True
    return False
