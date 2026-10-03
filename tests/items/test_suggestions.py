"""Suggestions lead with the person's clutter; counts on every surface."""
from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

import cli
from database_agent.db import open_database
from database_agent.entrypoint import main
from items.identity import reconcile_tree
from items.suggest import suggestions


def _db(tmp_path: Path, names: dict[str, bytes]):
    root = tmp_path / "lib"
    root.mkdir(exist_ok=True)
    for name, body in names.items():
        (root / name).write_bytes(body)
    db = tmp_path / "agent.sqlite"
    conn = open_database(db, scan_roots=[str(root)])
    cli._bootstrap(conn)
    reconcile_tree(conn, root)
    return conn, db, root


CLUTTER = {
    "Screenshot 2026-01-01 at 9.00.00 AM.png": b"s1",
    "Screenshot 2026-01-02 at 9.00.00 AM.png": b"s2",
    "essay.txt": b"same",
    "essay (1).txt": b"same",
    "Setup.dmg": b"installer",
}


def test_suggestions_lead_with_clutter_in_counted_facts(tmp_path):
    conn, _db_path, _root = _db(tmp_path, CLUTTER)
    rows = suggestions(conn)
    assert [r["kind"] for r in rows[:3]] == ["screenshots", "copies", "installers"]
    assert rows[0]["text"].startswith("2 loose screenshots")
    assert rows[1]["text"].startswith("1 file is a copy")
    assert rows[2]["text"].startswith("1 installer")
    assert all(set(r) == {"kind", "text", "action"} for r in rows)
    assert rows[0]["action"] == "sort screenshots"
    blob = " ".join(r["text"] for r in rows).lower()
    assert "deadline" not in blob and "calendar" not in blob


def test_no_clutter_no_suggestions(tmp_path):
    conn, _db_path, _root = _db(tmp_path, {"notes.txt": b"n"})
    assert suggestions(conn) == []


def test_view_deadlines_is_gone(tmp_path):
    _conn, db, _root = _db(tmp_path, {"a.txt": b"a"})
    with pytest.raises(SystemExit) as exit_:
        main(["view", "deadlines", "--database", str(db)], out=io.StringIO())
    assert exit_.value.code == 2


def test_view_defaults_to_folder_and_prints_counts(tmp_path):
    _conn, db, _root = _db(tmp_path, {"a.txt": b"a"})
    out = io.StringIO()
    assert main(["view", "--database", str(db)], out=out) == 0
    text = out.getvalue()
    assert "Set aside" in text and "Protected" in text
    assert "a.txt" in text


def test_db_check_prints_counts(tmp_path):
    _conn, db, _root = _db(tmp_path, {"a.txt": b"a"})
    out = io.StringIO()
    assert main(["db", "check", "--database", str(db)], out=out) == 0
    report = json.loads(out.getvalue())
    assert "Set aside" in report["summary"] and "Protected" in report["summary"]


def test_view_and_suggest_see_a_file_added_since_the_last_index(tmp_path):
    _conn, db, root = _db(tmp_path, {"a.txt": b"a"})
    (root / "Setup.dmg").write_bytes(b"installer")
    out = io.StringIO()
    assert main(["view", "--database", str(db)], out=out) == 0
    assert "Setup.dmg" in out.getvalue()
    (root / "Other.pkg").write_bytes(b"installer")
    out = io.StringIO()
    assert main(["suggest", "--database", str(db)], out=out) == 0
    assert "2 installers" in out.getvalue()


def test_refresh_failure_is_one_plain_line(tmp_path, monkeypatch):
    _conn, db, _root = _db(tmp_path, {"a.txt": b"a"})

    def broken(*_a, **_k):
        raise OSError("disk went away")

    monkeypatch.setattr("items.refresh.refresh_index", broken)
    for argv in (["view"], ["suggest"]):
        out = io.StringIO()
        assert main([*argv, "--database", str(db)], out=out) == 0
        assert "Could not refresh the index (disk went away)" in out.getvalue()
