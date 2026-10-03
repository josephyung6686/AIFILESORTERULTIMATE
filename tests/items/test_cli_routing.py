"""CLI reserved words reach the items commands for every shipped view name."""
from __future__ import annotations

import io
from pathlib import Path

import cli
from database_agent.entrypoint import main
from items.identity import reconcile_tree


def _db(tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.txt").write_bytes(b"a")
    db = tmp_path / "agent.sqlite"
    from database_agent.db import open_database
    conn = open_database(db, scan_roots=[str(root)])
    cli._bootstrap(conn)
    reconcile_tree(conn, root)
    conn.close()
    return db


def test_every_view_name_routes(tmp_path: Path):
    db = _db(tmp_path)
    for name in ("folder", "table", "board", "timeline", "graph"):
        out = io.StringIO()
        code = main(["view", name, "--database", str(db)], out=out)
        assert code == 0, (name, out.getvalue())


def test_search_routes(tmp_path: Path):
    db = _db(tmp_path)
    out = io.StringIO()
    code = main(["search", "a.txt", "--database", str(db)], out=out)
    assert code == 0, out.getvalue()
    assert "hit" in out.getvalue().lower()
    line = [x for x in out.getvalue().splitlines() if x.startswith("a.txt")]
    assert line and "\t" not in line[0] and "0." not in line[0]


def test_suggest_refuses_apply(tmp_path: Path):
    db = _db(tmp_path)
    out = io.StringIO()
    code = main(["suggest", "--database", str(db), "--apply"], out=out)
    assert code == 2
    assert "does not move" in out.getvalue()
