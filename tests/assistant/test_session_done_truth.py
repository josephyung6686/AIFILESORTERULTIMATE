"""What the chat says was moved is what the disk and the journal show; undo
leaves no empty folder the move created."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from assistant import events as ev
from assistant.session import Session
from database_agent.db import open_database
from items.hot_index import rebuild_fts
from items.identity import reconcile_tree
from items.schema import create_items_schema


@pytest.fixture(autouse=True)
def _apply_flag_unset(monkeypatch):
    monkeypatch.delenv("ASSISTANT_ENABLE_APPLY", raising=False)


@pytest.fixture()
def lib(tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    for name in ("a.png", "b.png"):
        (root / name).write_bytes(name.encode() * 10)
    conn = open_database(tmp_path / "x.sqlite", scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.commit()
    yield conn, root
    conn.close()


def sort_into_screenshots(conn, out):
    it = iter([
        {"role": "assistant", "content": None, "tool_calls": [
            {"id": "c0", "type": "function", "function": {
                "name": "quick_sort", "arguments": json.dumps(
                    {"files": ["a.png", "b.png"],
                     "destination": "Screenshots"})}}]},
        {"role": "assistant", "content": "Shall I?"}])
    s = Session(conn, provider_turn=lambda **k: next(it), emit=out.append)
    s.say("put a.png and b.png in Screenshots")
    s.say("yes")
    return s


def texts(out):
    return [e.text for e in out if isinstance(e, (ev.Message, ev.Error))]


def undo_all(s, out):
    done = [e for e in out if isinstance(e, ev.Done)][-1]
    s.undo(done.undo_token)
    s.say("yes")


def test_move_and_undo_report_the_real_count(lib):
    conn, root = lib
    out = []
    s = sort_into_screenshots(conn, out)
    assert texts(out)[-1] == ("Moved 2 files into Screenshots. Say undo to "
                              "put them back.")
    undo_all(s, out)
    assert texts(out)[-1] == "Put 2 files back where they were."
    assert (root / "a.png").exists()


def test_undo_removes_the_empty_folder_the_move_created(lib):
    conn, root = lib
    out = []
    s = sort_into_screenshots(conn, out)
    assert (root / "Screenshots").is_dir()
    undo_all(s, out)
    assert not (root / "Screenshots").exists()


def test_undo_keeps_a_folder_that_existed_before(lib):
    conn, root = lib
    (root / "Screenshots").mkdir()
    out = []
    s = sort_into_screenshots(conn, out)
    undo_all(s, out)
    assert (root / "Screenshots").is_dir()


def test_undo_keeps_a_created_folder_that_is_not_empty(lib):
    conn, root = lib
    out = []
    s = sort_into_screenshots(conn, out)
    (root / "Screenshots" / "mine.txt").write_text("keep me")
    undo_all(s, out)
    assert (root / "Screenshots" / "mine.txt").exists()


def test_undo_in_a_later_session_still_removes_the_folder(lib):
    conn, root = lib
    out = []
    first = sort_into_screenshots(conn, out)
    token = [e for e in out if isinstance(e, ev.Done)][-1].undo_token
    del first
    later = Session(conn, provider_turn=lambda **k: None, emit=out.append)
    later.undo(token)
    later.say("yes")
    assert not (root / "Screenshots").exists()


@pytest.mark.parametrize("kind,ref", [("branch", "/x|Coursework"),
                                      ("plan", "nope")])
def test_a_claimed_move_with_nothing_moved_says_nothing_moved(
        lib, monkeypatch, kind, ref):
    import assistant.engine_tools as et
    conn, _ = lib
    monkeypatch.setattr(et, "execute_confirmed", lambda *a, **k: {
        "ok": True, "moved": True, "undo_token": f"{kind}:{ref}",
        "text": "Moved the files for Coursework. Say undo to put them back."})
    out = []
    s = Session(conn, provider_turn=lambda **k: None, emit=out.append)
    s._propose({"kind": kind, "ref": ref, "summary": "Move them?",
                "moves": [], "sensitive": False})
    s.say("yes")
    assert texts(out)[-1].startswith("Nothing moved")
    done = [e for e in out if isinstance(e, ev.Done)]
    assert not done or done[-1].moved is False
    assert s.last_undo_token is None
