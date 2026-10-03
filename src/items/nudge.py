"""Nudge: local warnings from profile required pairs. No writes to approvals.

Uses the canonical relationship projection. Cancelled/declined events and
unrelated future events are excluded; selected event evidence is attached.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from items.profile_loader import ProfilePackage
from items.relationship_service import (
    CANCELLED_STATUSES,
    project_relationships,
)
from items.schema import create_items_schema


def warnings(
        conn: sqlite3.Connection, *,
        profile: ProfilePackage | None,
        now: str | None = None) -> list[dict]:
    """Return warning dicts. Does not insert relationships or move files."""
    create_items_schema(conn)
    moment = now or datetime.now(timezone.utc).isoformat()
    pairs = []
    if profile is not None:
        pairs = list(profile.raw.get("required_pairs") or [])
    if not pairs:
        # Default student pair: course expects academic member-of before event.
        pairs = [{
            "hub_type": "course",
            "need_rel": "member-of",
            "need_type_schema": "academic",
            "with_future_event": True,
        }]
    out: list[dict] = []
    for pair in pairs:
        out.extend(_check_pair(conn, pair, moment))
    return out


def _check_pair(conn, pair: dict, moment: str) -> list[dict]:
    hub_type = pair.get("hub_type", "course")
    need_rel = pair.get("need_rel", "member-of")
    need_schema = pair.get("need_type_schema")
    with_event = bool(pair.get("with_future_event"))
    hubs = conn.execute(
        "SELECT item_id, display_label FROM items "
        "WHERE item_type = ? AND presence = 'live' AND superseded_by IS NULL "
        "ORDER BY display_label",
        (hub_type,),
    ).fetchall()
    events = []
    if with_event:
        events = conn.execute(
            "SELECT i.item_id, i.display_label, h.happened_at, h.status "
            "FROM items i JOIN item_headers h ON h.item_id = i.item_id "
            "WHERE i.item_type = 'event' AND h.happened_at >= ? "
            "ORDER BY h.happened_at",
            (moment,),
        ).fetchall()
        events = [
            e for e in events
            if (e["status"] or "").strip().casefold() not in CANCELLED_STATUSES
        ]
        if not events:
            return []
    found = []
    for hub in hubs:
        if _has_member(conn, hub["item_id"], need_rel, need_schema):
            continue
        related = _related_future_event(conn, hub["item_id"], events) if events else None
        # Urgency clock: any non-cancelled future event arms the warning.
        # Only a hub-related event is named and attached as evidence.
        soonest = events[0] if events else None
        chosen = related if related is not None else None
        message = (
            f"{hub_type} {hub['display_label']} has no {need_schema or 'typed'} "
            f"file linked as {need_rel}."
        )
        evidence = [f"hub:{hub['item_id']}"]
        event_id = None
        if chosen is not None:
            event_id = chosen["item_id"]
            message += (
                f" Next event {chosen['display_label']} at "
                f"{chosen['happened_at']}."
            )
            evidence.append(f"event:{event_id}")
            if chosen["status"]:
                evidence.append(f"status:{chosen['status']}")
        elif soonest is not None:
            # Eligible future events exist but none are related — do not name them.
            evidence.append("future_events:present_unrelated")
        message += " Nothing was moved."
        found.append({
            "kind": "missing_member_of",
            "hub_item_id": hub["item_id"],
            "hub": hub["display_label"],
            "event_item_id": event_id,
            "message": message,
            "evidence_refs": evidence,
        })
    return found


def _related_future_event(conn, hub_id: str, events: list) -> sqlite3.Row | None:
    """Soonest future event linked to this hub; skip unrelated calendars."""
    linked_ids = set()
    for edge in project_relationships(conn, surface="nudge", item_id=hub_id):
        other = (
            edge["to_item_id"] if edge["from_item_id"] == hub_id
            else edge["from_item_id"]
        )
        linked_ids.add(other)
    for event in events:
        if event["item_id"] in linked_ids:
            return event
    return None


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


def render(rows: list[dict]) -> str:
    if not rows:
        return "No suggestions. Nothing was moved. No network call was made."
    lines = [row["message"] for row in rows]
    lines.append(
        f"Warnings: {len(rows)}. Nothing was moved. No network call was made."
    )
    return "\n".join(lines)
