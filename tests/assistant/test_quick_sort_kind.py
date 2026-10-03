"""A one-off sort of a suggestion's whole set: the count the greeting says is
the count the move shows."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from assistant import events as ev
from assistant.engine_tools import quick_sort
from assistant.session import Session
from database_agent.db import open_database
from items.hot_index import rebuild_fts
from items.identity import reconcile_tree
from items.schema import create_items_schema
from items.suggest import files_for, suggestions


@pytest.fixture(autouse=True)
def _apply_flag_unset(monkeypatch):
    monkeypatch.delenv("ASSISTANT_ENABLE_APPLY", raising=False)


@pytest.fixture()
def desk(tmp_path: Path):
    root = (tmp_path / "Desktop").resolve()
    root.mkdir()
    for i in range(13):
        (root / f"Screenshot 2024-05-{i + 10} at 1.0{i % 10}.00 PM.png"
         ).write_bytes(b"png%d" % i)
    (root / "Real picture").mkdir()
    (root / "Real picture" / "Screenshot (1).png").write_bytes(b"deep")
    (root / "essay.docx").write_bytes(b"essay")
    (root / "Zoom.pkg").write_bytes(b"pkg")
    conn = open_database(tmp_path / "x.sqlite", scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.commit()
    yield conn, root
    conn.close()


def greeting_count(conn, kind):
    item = next(i for i in suggestions(conn) if i["kind"] == kind)
    return int(re.match(r"\d+", item["text"]).group())


def test_the_greeting_and_the_move_agree(desk):
    conn, root = desk
    n = greeting_count(conn, "screenshots")
    assert n == 13 == len(files_for(conn, "screenshots"))
    result = quick_sort(conn, [], kind="screenshots")
    moves = result["needs_confirmation"]["moves"]
    assert len(moves) == n
    assert all(Path(m["to"]).parent == root / "Screenshots" for m in moves)
    assert "Move 13 files into Screenshots" in \
        result["needs_confirmation"]["summary"]


def test_installers_by_kind(desk):
    conn, root = desk
    moves = quick_sort(conn, [], kind="installers")["needs_confirmation"][
        "moves"]
    assert [Path(m["to"]) for m in moves] == [root / "Installers" / "Zoom.pkg"]


def test_put_my_screenshots_in_a_folder_moves_them_all(desk):
    conn, root = desk
    it = iter([
        {"role": "assistant", "content": None, "tool_calls": [
            {"id": "c0", "type": "function", "function": {
                "name": "quick_sort", "arguments": json.dumps(
                    {"kind": "screenshots", "destination": "Screenshots"})}}]},
        {"role": "assistant", "content": "Here they are."}])
    out = []
    s = Session(conn, provider_turn=lambda **k: next(it), emit=out.append)
    s.say("put my screenshots into a Screenshots folder")
    s.say("yes")
    assert len(list((root / "Screenshots").iterdir())) == 13
    assert [e.text for e in out if isinstance(e, ev.Message)][-1] == (
        "Moved 13 files into Screenshots. Say undo to put them back.")
    assert (root / "Real picture" / "Screenshot (1).png").exists()


def test_the_prompt_tells_one_off_from_standing_rule():
    from assistant.session import PLAIN_WORDS
    assert "quick_sort" in PLAIN_WORDS and "remember_rule" in PLAIN_WORDS
