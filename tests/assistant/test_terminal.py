"""The terminal renderer and the JSON-lines app contract."""
from __future__ import annotations

import io
import json
import re
import sys
import types
from dataclasses import dataclass
from pathlib import Path

import pytest

from assistant.terminal import run_events, run_terminal


@dataclass(frozen=True)
class IndexCounts:  # the Index agent's shape, stubbed until it lands
    indexed: int
    set_aside: int
    set_aside_folders: int
    protected: int
    held: int
    open_questions: int


@pytest.fixture()
def fake_indexing(monkeypatch):
    """`items.indexing` as the Index agent will provide it: index the folder
    (here with the existing reconcile) and report counts."""
    from items.hot_index import rebuild_fts
    from items.identity import reconcile_tree
    from items.schema import create_items_schema

    def counts(conn):
        try:
            n = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        except Exception:
            n = 0
        return IndexCounts(n, 0, 0, 0, 0, 0)

    def index_folder(conn, root, *, on_progress=None):
        create_items_schema(conn)
        reconcile_tree(conn, Path(root))
        rebuild_fts(conn)
        if on_progress:
            on_progress("done", 1, 1)
        return counts(conn)

    module = types.ModuleType("items.indexing")
    module.counts = counts
    module.index_folder = index_folder
    monkeypatch.setitem(sys.modules, "items.indexing", module)


@pytest.fixture(autouse=True)
def _apply_flag_unset(monkeypatch):
    monkeypatch.delenv("ASSISTANT_ENABLE_APPLY", raising=False)


def scripted(*replies):
    it = iter(replies)

    def turn(messages, tools, config=None, **_):
        return next(it)
    return turn


def tool(name, args):
    return {"role": "assistant", "content": None, "tool_calls": [
        {"id": "c1", "type": "function",
         "function": {"name": name, "arguments": json.dumps(args)}}]}


def _desk(tmp_path):
    desk = tmp_path / "Desk"
    desk.mkdir()
    (desk / "a.png").write_bytes(b"a" * 20)
    (desk / "b.png").write_bytes(b"b" * 20)
    return desk


def test_a_first_run_in_the_terminal(conn, tmp_path, fake_indexing):
    desk = _desk(tmp_path)
    stdin = io.StringIO(f"{desk}\nput a.png and b.png in Screenshots\n1\nquit\n")
    stdout = io.StringIO()
    code = run_terminal(conn, folder=None, stdin=stdin, stdout=stdout,
                        provider_turn=scripted(
                            tool("quick_sort", {"files": ["a.png", "b.png"],
                                                "destination": "Screenshots"}),
                            {"role": "assistant", "content": "Shall I?"}))
    shown = stdout.getvalue()
    assert code == 0
    assert "which folder" in shown.lower()
    assert "Indexed" in shown or "indexed" in shown
    assert "Go ahead? 1) Yes  2) No" in shown
    assert "Moved 2 files" in shown
    assert (desk / "Screenshots" / "a.png").exists()
    for bad in ("Traceback", "item_id", "plan_id"):
        assert bad not in shown
    assert not re.search(r"\b[0-9a-f]{8,}\b", shown)


def test_events_round_trip(conn, tmp_path, fake_indexing):
    # Something is indexed, so the opening greets instead of asking for a
    # folder, and the say is a turn.
    sys.modules["items.indexing"].index_folder(conn, _desk(tmp_path))
    stdin = io.StringIO(json.dumps({"action": "say", "text": "hi"}) + "\n")
    stdout = io.StringIO()
    run_events(conn, stdin=stdin, stdout=stdout, provider_turn=scripted(
        {"role": "assistant", "content": "hello"}))
    lines = [json.loads(line) for line in stdout.getvalue().splitlines()]
    assert lines[-1] == {"type": "message", "text": "hello", "citations": []}


def test_events_confirm_round_trip(conn, tmp_path, fake_indexing):
    desk = _desk(tmp_path)
    sys.modules["items.indexing"].index_folder(conn, desk)
    out = io.StringIO()
    actions = [{"action": "say", "text": "sort them"}]
    stdin = io.StringIO("\n".join(json.dumps(a) for a in actions) + "\n")
    run_events(conn, stdin=stdin, stdout=out, provider_turn=scripted(
        tool("quick_sort", {"files": ["a.png", "b.png"]}),
        {"role": "assistant", "content": "ok"}))
    confirm = [json.loads(line) for line in out.getvalue().splitlines()
               if json.loads(line)["type"] == "confirm"][-1]
    assert {"from", "to"} <= set(confirm["moves"][0])
    out2 = io.StringIO()
    # A new process sees no pending confirmation and says so plainly.
    run_events(conn, stdin=io.StringIO(json.dumps(
        {"action": "confirm", "confirm_id": confirm["confirm_id"],
         "yes": True}) + "\n"), stdout=out2)
    assert json.loads(out2.getvalue().splitlines()[-1])["type"] == "message"


def test_a_bad_action_line_is_an_error_event(conn):
    out = io.StringIO()
    run_events(conn, stdin=io.StringIO("not json\n"), stdout=out)
    last = json.loads(out.getvalue().splitlines()[-1])
    assert last["type"] == "error" and "Traceback" not in last["text"]
