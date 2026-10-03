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


def _route(monkeypatch, tmp_path, argv, *, tty):
    """Which of the conversation, the one-shot answer or the sorter `main`
    picks for `argv`."""
    import database_agent.entrypoint as entry
    import assistant.terminal as terminal
    seen = []
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setattr(entry, "_stdin_is_a_terminal", lambda: tty)
    monkeypatch.setattr(terminal, "run_terminal",
                        lambda conn, **kw: seen.append(("chat", kw)) or 0)
    monkeypatch.setattr(terminal, "run_events",
                        lambda conn, **kw: seen.append(("events", kw)) or 0)
    monkeypatch.setattr(terminal, "run_once",
                        lambda conn, text, **kw: seen.append(("once", text)) or 0)
    monkeypatch.setattr(cli, "main",
                        lambda args, **kw: seen.append(("sorter", args)) or 0)
    assert entry.main(argv) == 0
    return seen


def test_a_folder_alone_in_a_terminal_opens_the_chat(monkeypatch, tmp_path):
    folder = tmp_path / "Desk"
    folder.mkdir()
    seen = _route(monkeypatch, tmp_path, [str(folder)], tty=True)
    assert seen[0][0] == "chat" and seen[0][1]["folder"] == folder


def test_a_folder_with_flags_is_the_sorter(monkeypatch, tmp_path):
    folder = tmp_path / "Desk"
    folder.mkdir()
    seen = _route(monkeypatch, tmp_path,
                  [str(folder), "--stop-after", "tree"], tty=True)
    assert seen == [("sorter", [str(folder), "--stop-after", "tree"])]


def test_a_folder_without_a_terminal_is_the_sorter(monkeypatch, tmp_path):
    folder = tmp_path / "Desk"
    folder.mkdir()
    seen = _route(monkeypatch, tmp_path, [str(folder)], tty=False)
    assert seen[0][0] == "sorter"


def test_no_arguments_open_the_chat_and_words_get_one_answer(monkeypatch,
                                                             tmp_path):
    assert _route(monkeypatch, tmp_path, [], tty=True)[0][0] == "chat"
    seen = _route(monkeypatch, tmp_path, ["where is my CV"], tty=True)
    assert seen == [("once", "where is my CV")]
    assert _route(monkeypatch, tmp_path, ["--events"],
                  tty=False)[0][0] == "events"
