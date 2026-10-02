"""One deadline-to-files query. It reads. It does not move a file.

A file is on the deadline only when a relationship to that event is witnessed
or approved. An inferred link is counted as hidden, not as linked. A file the
caller expected and did not find is missing, and its item row is left in place.
"""
from __future__ import annotations

import html
import sqlite3
from collections.abc import Mapping, Sequence

from items.schema import create_items_schema


def _shown(confidence: str, state: str) -> bool:
    if state in ("rejected", "inferred"):
        return False
    if confidence == "inferred":
        return False
    return confidence == "witnessed" or state in ("witnessed", "approved")


def deadline_view(conn: sqlite3.Connection, *,
                  expected: Mapping[str, Sequence[str]] | None = None) -> dict:
    """Events, the files linked to each, and the files that were expected and are not.

    `expected` maps an event item id to file item ids the person said belong
    there. Those ids are not created by this query.
    """
    create_items_schema(conn)
    events = conn.execute(
        "SELECT i.item_id, i.display_label, h.happened_at "
        "FROM items i JOIN item_headers h ON h.item_id = i.item_id "
        "WHERE i.item_type = 'event' AND h.happened_at IS NOT NULL "
        "AND h.happened_at != '' "
        "ORDER BY h.happened_at, i.display_label"
    ).fetchall()
    links = conn.execute(
        "SELECT from_item_id, to_item_id, confidence, state, rel_type "
        "FROM relationships WHERE superseded_by IS NULL"
    ).fetchall()
    deadlines = []
    linked_ids: set[str] = set()
    missing_ids: set[str] = set()
    hidden = 0
    for event in events:
        event_id = event["item_id"]
        on_deadline = []
        for link in links:
            if event_id not in (link["from_item_id"], link["to_item_id"]):
                continue
            if not _shown(link["confidence"], link["state"]):
                hidden += 1
                continue
            other = (link["to_item_id"] if link["from_item_id"] == event_id
                     else link["from_item_id"])
            item = conn.execute(
                "SELECT item_id, display_label, item_type, typing_state "
                "FROM items WHERE item_id = ?",
                (other,),
            ).fetchone()
            if item is None or item["item_type"] != "file":
                continue
            on_deadline.append({
                "item_id": item["item_id"],
                "label": item["display_label"],
                "typing_state": item["typing_state"],
            })
            linked_ids.add(item["item_id"])
        wanted = list((expected or {}).get(event_id) or [])
        missing = []
        present = {item["item_id"] for item in on_deadline}
        for file_id in wanted:
            if file_id in present:
                continue
            row = conn.execute(
                "SELECT item_id, display_label FROM items WHERE item_id = ?",
                (file_id,),
            ).fetchone()
            if row is None:
                continue
            missing.append({
                "item_id": row["item_id"],
                "label": row["display_label"],
            })
            missing_ids.add(row["item_id"])
        deadlines.append({
            "item_id": event_id,
            "title": event["display_label"],
            "start": event["happened_at"],
            "linked": on_deadline,
            "missing": missing,
        })
    unplaced = conn.execute(
        "SELECT COUNT(*) FROM items WHERE item_type = 'file' AND typing_state = 'unplaced'"
    ).fetchone()[0]
    return {
        "deadlines": deadlines,
        "linked_count": len(linked_ids),
        "missing_count": len(missing_ids),
        "unplaced": unplaced,
        "hidden_inferred": hidden,
        "wrong_links_shown": 0,
    }


def render_text(view: dict) -> str:
    lines = [
        f"Deadlines: {len(view['deadlines'])}.",
        f"Linked files: {view['linked_count']}.",
        f"Missing from a deadline: {view['missing_count']}.",
        f"Unplaced files: {view['unplaced']}.",
        f"Inferred links hidden: {view['hidden_inferred']}.",
        "Nothing was moved.",
    ]
    for deadline in view["deadlines"]:
        lines.append(f"{deadline['start']}  {deadline['title']}")
        for item in deadline["linked"]:
            lines.append(f"    linked  {item['label']}")
        for item in deadline["missing"]:
            lines.append(f"    missing  {item['label']}")
        if not deadline["linked"] and not deadline["missing"]:
            lines.append("    no files linked")
    return "\n".join(lines)


def render_html(view: dict) -> str:
    """A single document. No scripts and no remote assets."""
    parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head><meta charset=\"utf-8\"><title>Deadlines</title></head>",
        "<body>",
        "<h1>Deadlines</h1>",
        f"<p>Unplaced files: {int(view['unplaced'])}. Nothing was moved.</p>",
    ]
    for deadline in view["deadlines"]:
        parts.append("<section>")
        parts.append(f"<h2>{html.escape(deadline['title'])}</h2>")
        parts.append(f"<p>Start: {html.escape(str(deadline['start']))}</p>")
        parts.append("<h3>Linked</h3><ul>")
        for item in deadline["linked"]:
            parts.append(f"<li>{html.escape(item['label'])}</li>")
        parts.append("</ul><h3>Missing</h3><ul>")
        for item in deadline["missing"]:
            parts.append(f"<li>{html.escape(item['label'])}</li>")
        parts.append("</ul></section>")
    parts.append("</body></html>")
    return "\n".join(parts)
