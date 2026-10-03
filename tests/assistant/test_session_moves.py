"""Confirmations, permission levels, quick sort, apply and undo in a Session."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from assistant.engine_tools import level_allows
from assistant.events import Confirm, Done, Error, Message
from assistant.session import Session
from assistant.tools import ToolRuntime
from database_agent.db import open_database
from items.hot_index import rebuild_fts
from items.identity import reconcile_tree
from items.schema import create_items_schema


@pytest.fixture(autouse=True)
def _apply_flag_unset(monkeypatch):
    # A confirmed move needs no flag: the person's yes is the approval.
    monkeypatch.delenv("ASSISTANT_ENABLE_APPLY", raising=False)


@pytest.fixture()
def lib(tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    for name in ("a.png", "b.png", "c.png", "id.pem"):
        (root / name).write_bytes(name.encode() * 10)
    conn = open_database(tmp_path / "x.sqlite", scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.commit()
    yield conn, root
    conn.close()


def calls(*tool_calls, reply="Here you go."):
    """A provider that makes the given tool calls once, then replies."""
    script = [{"role": "assistant", "content": None, "tool_calls": [
        {"id": f"c{i}", "type": "function",
         "function": {"name": name, "arguments": json.dumps(args)}}
        for i, (name, args) in enumerate(tool_calls)]},
        {"role": "assistant", "content": reply}]
    it = iter(script)

    def turn(messages, tools, config=None, **_):
        return next(it)
    return turn


def session(conn, turn, out):
    return Session(conn, provider_turn=turn, emit=out.append)


def sort_ab(conn, out, files=("a.png", "b.png")):
    s = session(conn, calls(("quick_sort", {"files": list(files),
                                            "destination": "Screenshots"})),
                out)
    s.say("put those into Screenshots")
    return s


def test_level_1_asks_and_no_moves_nothing(lib):
    conn, root = lib
    out = []
    s = sort_ab(conn, out)
    confirm = [e for e in out if isinstance(e, Confirm)][-1]
    assert len(confirm.moves) == 2 and not confirm.sensitive
    assert (root / "a.png").exists() and (root / "b.png").exists()
    s.confirm(confirm.confirm_id, False)
    assert isinstance(out[-1], Message) and out[-1].text == "Cancelled. Nothing moved."
    assert (root / "a.png").exists()


def test_yes_moves_and_undo_asks_then_puts_back(lib):
    conn, root = lib
    out = []
    s = sort_ab(conn, out)
    confirm = [e for e in out if isinstance(e, Confirm)][-1]
    s.confirm(confirm.confirm_id, True)
    done = [e for e in out if isinstance(e, Done)][-1]
    assert done.moved is True and done.undo_token
    assert (root / "Screenshots" / "a.png").exists()
    assert not (root / "a.png").exists()
    s.undo(done.undo_token)
    undo_confirm = out[-1]
    assert isinstance(undo_confirm, Confirm)
    assert (root / "Screenshots" / "a.png").exists()
    s.confirm(undo_confirm.confirm_id, True)
    assert (root / "a.png").exists() and (root / "b.png").exists()


def test_level_2_small_ordinary_sort_runs_at_once(lib):
    conn, root = lib
    out = []
    session(conn, calls(), out).set_level(2)
    sort_ab(conn, out, files=("a.png", "b.png", "c.png"))
    assert not [e for e in out if isinstance(e, Confirm)]
    assert [e for e in out if isinstance(e, Done)][-1].moved is True
    assert (root / "Screenshots" / "c.png").exists()


def test_level_2_with_a_protected_file_still_asks(lib):
    conn, root = lib
    out = []
    session(conn, calls(), out).set_level(2)
    sort_ab(conn, out, files=("a.png", "id.pem"))
    confirm = [e for e in out if isinstance(e, Confirm)][-1]
    assert confirm.sensitive is True
    assert "protected" in confirm.summary
    assert all("id.pem" not in m.src for m in confirm.moves)
    assert (root / "a.png").exists() and (root / "id.pem").exists()


def test_branch_undo_protection_and_settings_always_ask():
    for kind in ("branch", "undo", "protection", "settings", "rule", "folder"):
        assert level_allows(3, kind, 1, False) is False
    assert level_allows(3, "plan", 500, False) is True
    assert level_allows(2, "plan", 21, False) is False
    assert level_allows(1, "plan", 1, False) is False


def test_file_changed_after_yes_refuses_and_moves_nothing(lib):
    conn, root = lib
    out = []
    s = sort_ab(conn, out)
    confirm = [e for e in out if isinstance(e, Confirm)][-1]
    (root / "a.png").write_bytes(b"edited since")
    s.confirm(confirm.confirm_id, True)
    assert isinstance(out[-1], Error)
    assert "changed since" in out[-1].text and out[-1].changed is False
    assert (root / "a.png").exists() and (root / "b.png").exists()
    assert not (root / "Screenshots").exists()


def test_kill_switch_refuses_even_a_confirmed_move(lib, monkeypatch):
    conn, root = lib
    monkeypatch.setenv("ASSISTANT_ENABLE_APPLY", "0")
    out = []
    s = sort_ab(conn, out)
    confirm = [e for e in out if isinstance(e, Confirm)][-1]
    s.confirm(confirm.confirm_id, True)
    assert isinstance(out[-1], Error)
    assert out[-1].text == "Moving files is switched off on this Mac. Nothing moved."
    assert (root / "a.png").exists()


def test_model_never_sees_the_move_paths_and_cannot_confirm(lib):
    conn, root = lib
    rt = ToolRuntime(conn, engine=True)
    result = rt.execute("quick_sort", {"files": ["a.png"]})
    assert result.payload["waiting_for_person"] is True
    assert str(root) not in json.dumps(result.payload)
    assert rt.pending_confirmations and not (root / "Images").exists()


def test_destination_must_be_a_folder_name(lib):
    conn, _ = lib
    rt = ToolRuntime(conn, engine=True)
    for bad in ("../x", "/tmp/x", ".ssh", "a/b"):
        assert rt.execute("quick_sort", {"files": ["a.png"],
                                         "destination": bad}).ok is False
    assert not rt.pending_confirmations


def test_engine_tools_are_absent_outside_a_session(lib):
    conn, _ = lib
    rt = ToolRuntime(conn)
    names = {s["function"]["name"] for s in rt.schemas()}
    assert "quick_sort" not in names
    assert rt.execute("quick_sort", {"files": ["a.png"]}).ok is False
