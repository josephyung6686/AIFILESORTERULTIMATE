"""When lives are declared, undeclared recognitions (e.g. photos capture) stay unplaced."""
from __future__ import annotations

from pathlib import Path

from database_agent.db import open_database
from items.identity import reconcile_tree
from items.schema import create_items_schema
from items.typing import project_typing
from questions.profile import apply_profile
from questions.schema import create_questions_schema
from recognition.detector import Recognition


def test_undeclared_photos_recognition_is_unplaced(tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "pic.jpg").write_bytes(b"x")
    conn = open_database(tmp_path / "db.sqlite", scan_roots=[str(root)])
    create_items_schema(conn)
    create_questions_schema(conn)
    reconcile_tree(conn, root)
    apply_profile(
        conn, user_id="ada", recorded_at="2026-10-02T00:00:00+00:00",
        lives=("coursework=academic",),
    )

    def explain(c, file_id, content_hash):
        # Simulates Detector._capture returning photos despite the allow-list.
        return Recognition(schema_id="photos", matches=(), evidence_refs=("m1",))

    project_typing(conn, explain=explain, classify=lambda *a: None)
    row = conn.execute(
        "SELECT typing_state, type_schema FROM items WHERE item_type='file'"
    ).fetchone()
    assert row["typing_state"] == "unplaced"
    assert row["type_schema"] is None


def test_declared_academic_still_types(tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.pdf").write_bytes(b"x")
    conn = open_database(tmp_path / "db.sqlite", scan_roots=[str(root)])
    create_items_schema(conn)
    create_questions_schema(conn)
    reconcile_tree(conn, root)
    apply_profile(
        conn, user_id="ada", recorded_at="2026-10-02T00:00:00+00:00",
        lives=("coursework=academic",),
    )

    def explain(c, file_id, content_hash):
        return Recognition(schema_id="academic", matches=(), evidence_refs=("e1",))

    project_typing(conn, explain=explain, classify=lambda *a: None)
    row = conn.execute(
        "SELECT typing_state, type_schema FROM items WHERE item_type='file'"
    ).fetchone()
    assert row["typing_state"] == "typed"
    assert row["type_schema"] == "academic"
