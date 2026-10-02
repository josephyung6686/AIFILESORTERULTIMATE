"""local_only=True must answer find questions without cloud when FM missing."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from assistant.chat import ask
from database_agent.db import open_database
from items.hot_index import rebuild_fts
from items.identity import reconcile_tree
from items.schema import create_items_schema


def test_local_only_find_uses_index_not_cloud(tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "Joint PMFs.pdf").write_text("lecture notes", encoding="utf-8")
    db = tmp_path / "t.sqlite"
    conn = open_database(db, scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.commit()

    with patch("assistant.chat.chat_turn") as ct:
        answer = ask(conn, "where is Joint PMFs?", local_only=True)
    assert ct.call_count == 0, "must not call cloud"
    assert answer.moved is False
    assert answer.provider == "local"
    assert answer.citations, "should cite find hits"
    assert "Joint" in answer.text or "PMFs" in answer.text
    conn.close()
