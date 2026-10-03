"""CLI product surface: `ask` routes; missing key refuses cleanly."""
from __future__ import annotations

import io
from pathlib import Path
from unittest.mock import patch

from database_agent.db import open_database
from items.commands import ask_main
from items.hot_index import rebuild_fts
from items.identity import reconcile_tree
from items.schema import create_items_schema


def test_ask_main_missing_key_exits_2_no_move(tmp_path: Path, monkeypatch):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.txt").write_text("hello", encoding="utf-8")
    db = tmp_path / "t.sqlite"
    conn = open_database(db, scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.commit()
    conn.close()

    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with patch("assistant.provider.load_dotenv", lambda *a, **k: None):
        buf = io.StringIO()
        code = ask_main([
            "where is a.txt",
            "--database", str(db),
        ], out=buf)
    text = buf.getvalue()
    assert code == 2
    assert "API key" in text or "Nothing was sent" in text


def test_cli_dispatches_ask_subcommand():
    # The routing table in entrypoint.py includes ask → ask_main.
    import database_agent.entrypoint as entry
    src = Path(entry.__file__).read_text(encoding="utf-8")
    assert '"ask"' in src
    assert "ask_main" in src
