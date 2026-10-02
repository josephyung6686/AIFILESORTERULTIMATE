"""Local suggestions. They are printed. They do not approve a link or move a file.

A course item with a future event and no witnessed or approved academic
member-of is one warning. The warning names the course and the event. It does
not create the missing file.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from items.schema import create_items_schema


def proposals(conn: sqlite3.Connection, *, now: str | None = None) -> list[dict]:
    """Read items and relationships. Write nothing."""
    create_items_schema(conn)
    moment = now or datetime.now(timezone.utc).isoformat()
    courses = conn.execute(
        "SELECT item_id, display_label FROM items "
        "WHERE item_type = 'course' AND presence = 'live' "
        "ORDER BY display_label"
    ).fetchall()
    events = conn.execute(
        "SELECT i.item_id, i.display_label, h.happened_at "
        "FROM items i JOIN item_headers h ON h.item_id = i.item_id "
        "WHERE i.item_type = 'event' AND h.happened_at >= ? "
        "ORDER BY h.happened_at",
        (moment,),
    ).fetchall()
    if not courses or not events:
        return []
    soonest = events[0]
    found = []
    for course in courses:
        if _academic_member(conn, course["item_id"]):
            continue
        found.append({
            "course_item_id": course["item_id"],
            "course": course["display_label"],
            "event_item_id": soonest["item_id"],
            "event": soonest["display_label"],
            "start": soonest["happened_at"],
            "action": "none",
        })
    return found


def _academic_member(conn, course_id: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM relationships r "
        "JOIN items f ON f.item_id = r.from_item_id "
        "WHERE r.to_item_id = ? AND r.rel_type = 'member-of' "
        "AND r.superseded_by IS NULL AND r.state != 'rejected' "
        "AND (r.confidence = 'witnessed' OR r.state = 'approved') "
        "AND f.item_type = 'file' AND f.type_schema = 'academic' "
        "LIMIT 1",
        (course_id,),
    ).fetchone()
    return row is not None


def render(rows: list[dict]) -> str:
    if not rows:
        return (
            "No suggestions. Nothing was moved. No network call was made."
        )
    lines = []
    for row in rows:
        lines.append(
            f"Suggestion: course {row['course']} has event {row['event']} "
            f"at {row['start']} and no academic file linked as member-of. "
            "Nothing was moved."
        )
    lines.append(
        f"Proposals: {len(rows)}. Nothing was moved. No network call was made."
    )
    return "\n".join(lines)
