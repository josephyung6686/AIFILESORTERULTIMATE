"""The deadline view shows witnessed links and keeps the gap visible."""
from __future__ import annotations

import io
import uuid
from pathlib import Path

from items.deadline_view import deadline_view, render_html
from items.identity import reconcile_tree
from items.schema import create_items_schema

import cli


def _item(conn, *, item_type, label, file_id=None, path=None, typing="unplaced",
          schema=None):
    item_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO items ("
        "item_id, item_type, display_label, file_id, open_target, external_key, "
        "presence, typing_state, type_schema, profile_id, created_at, superseded_by"
        ") VALUES (?, ?, ?, ?, ?, NULL, 'live', ?, ?, NULL, 't', NULL)",
        (item_id, item_type, label, file_id, path, typing, schema),
    )
    return item_id


def _link(conn, from_id, to_id, *, confidence, state):
    conn.execute(
        "INSERT INTO relationships ("
        "relationship_id, rel_type, from_item_id, to_item_id, confidence, "
        "source, state, evidence_refs, basis_key, created_at, supersedes, "
        "superseded_by) VALUES (?, 'occurs-on', ?, ?, ?, 'person', ?, '[]', ?, "
        "'t', NULL, NULL)",
        (str(uuid.uuid4()), from_id, to_id, confidence, state,
         f"{from_id}:{to_id}:{confidence}:{state}"),
    )


def test_a_deadline_lists_witnessed_files_and_names_the_gap(conn, tmp_path: Path):
    root = tmp_path / "library"
    root.mkdir()
    (root / "notes.txt").write_bytes(b"notes")
    (root / "essay.txt").write_bytes(b"essay")
    reconcile_tree(conn, root)
    create_items_schema(conn)
    files = conn.execute(
        "SELECT item_id, display_label FROM items WHERE item_type = 'file' "
        "ORDER BY display_label"
    ).fetchall()
    by_name = {row["display_label"]: row["item_id"] for row in files}
    event = _item(conn, item_type="event", label="Office hours")
    conn.execute(
        "INSERT INTO item_headers ("
        "item_id, kind, external_id, thread_id, account_label, happened_at, "
        "ended_at, address_from, address_to, calendar_id, status, "
        "attachment_names, attachment_hashes"
        ") VALUES (?, 'event', 'evt-1', '', 'local', ?, '', '', '', 'primary', "
        "'confirmed', '[]', '[]')",
        (event, "2026-10-03T15:00:00+00:00"),
    )
    _link(conn, by_name["notes.txt"], event, confidence="witnessed", state="proposed")
    _link(conn, by_name["essay.txt"], event, confidence="inferred", state="proposed")
    view = deadline_view(conn, expected={event: [by_name["essay.txt"]]})
    deadline = view["deadlines"][0]
    linked = {item["label"] for item in deadline["linked"]}
    missing = {item["label"] for item in deadline["missing"]}
    assert linked == {"notes.txt"}
    assert missing == {"essay.txt"}
    assert view["wrong_links_shown"] == 0
    assert view["hidden_inferred"] == 1
    assert view["unplaced"] >= 2
    page = render_html(view)
    assert "Office hours" in page
    assert "notes.txt" in page
    assert "essay.txt" in page
    assert "<script" not in page
    essay = conn.execute(
        "SELECT item_id FROM items WHERE item_id = ?",
        (by_name["essay.txt"],),
    ).fetchone()
    assert essay is not None

    html_path = tmp_path / "deadlines.html"
    out = io.StringIO()
    code = cli.main([
        "view", "deadlines", "--database", str(tmp_path / "agent.sqlite"),
        "--expect", f"{event}={by_name['essay.txt']}",
        "--html", str(html_path),
    ], out=out)
    text = out.getvalue()
    assert code == 0, text
    assert "linked  notes.txt" in text
    assert "missing  essay.txt" in text
    assert "Unplaced files:" in text
    assert "Nothing was moved" in text
    written = html_path.read_text(encoding="utf-8")
    assert "Office hours" in written
    assert "essay.txt" in written
