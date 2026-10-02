"""--local-only ask path refuses cloud when FM adapter missing."""
from __future__ import annotations

from pathlib import Path

from assistant.chat import ask
from database_agent.db import open_database
from items.identity import reconcile_tree
from items.schema import create_items_schema


def test_local_only_ask_refuses_without_cloud(tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.txt").write_text("hi", encoding="utf-8")
    db = tmp_path / "t.sqlite"
    conn = open_database(db, scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    conn.commit()
    answer = ask(conn, "where is a?", local_only=True)
    assert answer.moved is False
    assert answer.provider == "local"
    assert "Nothing was sent to the cloud" in answer.text
    assert answer.egress_bytes == 0
    # No ledger rows for refused local-only
    n = conn.execute("SELECT COUNT(*) AS n FROM sqlite_master "
                     "WHERE name='egress_ledger'").fetchone()["n"]
    if n:
        rows = conn.execute("SELECT COUNT(*) AS c FROM egress_ledger").fetchone()
        assert rows["c"] == 0
    conn.close()
