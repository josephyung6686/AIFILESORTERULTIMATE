"""The last chat fixes from judge 3's run: each test is one thing a person
saw that was wrong. Only scripted providers; no real model is called."""
from __future__ import annotations

import json
from dataclasses import dataclass

import pytest

from assistant import events as ev
from assistant.session import Session
from database_agent.db import open_database
from items.hot_index import rebuild_fts
from items.identity import reconcile_tree
from items.schema import create_items_schema


@dataclass(frozen=True)
class IndexCounts:
    indexed: int
    set_aside: int
    set_aside_folders: int
    protected: int
    held: int
    open_questions: int


@pytest.fixture(autouse=True)
def _apply_flag_unset(monkeypatch):
    monkeypatch.delenv("ASSISTANT_ENABLE_APPLY", raising=False)


@pytest.fixture()
def lib(tmp_path, monkeypatch):
    import assistant.session as session_mod
    root = tmp_path / "Desktop"
    root.mkdir()
    (root / "Resume 2026.docx").write_text("work history", encoding="utf-8")
    (root / "essay.txt").write_text("an essay", encoding="utf-8")
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.commit()
    monkeypatch.setattr(session_mod, "_counts", lambda c: IndexCounts(
        2, 0, 0, 0, 0, 0))
    yield conn, root
    conn.close()


def turns(*replies):
    seen = []
    it = iter(replies)

    def turn(messages, tools, config=None, **_):
        seen.append(messages)
        return next(it)
    turn.seen = seen
    return turn


def tool(name, args):
    return {"role": "assistant", "content": None, "tool_calls": [
        {"id": "c1", "type": "function",
         "function": {"name": name, "arguments": json.dumps(args)}}]}


def text(reply):
    return {"role": "assistant", "content": reply}


def said(out):
    return [e.text for e in out if isinstance(e, (ev.Message, ev.Error))]


# -- 3. one pending rule for every yes/no -----------------------------------

def test_an_undo_prompt_is_reminded_once_then_dropped(lib):
    conn, _ = lib
    out = []
    s = Session(conn, provider_turn=turns(text("It's in Desktop."),
                                          text("Sure."), text("Fine.")),
                emit=out.append)
    s._propose({"kind": "undo", "ref": "plan:x", "moves": [],
                "summary": "Put 20 files back where they were."})
    s.say("where is my essay")
    assert sum("Still waiting" in t for t in said(out)) == 1
    s.say("thanks")
    assert "Not done — ask again if you still want it." in said(out)
    assert s.on_screen is None and not s.pending
    s.say("and my resume?")
    assert sum("Still waiting" in t for t in said(out)) == 1


# -- 7. rendering ------------------------------------------------------------

@pytest.mark.parametrize("raw, want", [
    ("A folder **03 code**, inside ****, within **tencent**.",
     "A folder **03 code**, within **tencent**."),
    ("It sits inside **** on the Desktop.", "It sits on the Desktop."),
    ("Nothing ** ** here.", "Nothing here."),
])
def test_empty_emphasis_never_reaches_the_screen(conn, raw, want):
    from assistant.session import plain_reply
    assert plain_reply(conn, raw) == want


def _resume_is_protected(monkeypatch):
    import assistant.tools as tools_mod
    real = tools_mod.item_is_sensitive

    def sensitive(c, item_id):
        row = c.execute("SELECT display_label FROM items WHERE item_id = ?",
                        (item_id,)).fetchone()
        return bool(row and "Resume" in row[0]) or real(c, item_id)
    monkeypatch.setattr(tools_mod, "item_is_sensitive", sensitive)


def test_a_protected_match_says_it_cannot_be_read_then_shows_it(lib,
                                                                monkeypatch):
    conn, _ = lib
    _resume_is_protected(monkeypatch)
    out = []
    s = Session(conn, provider_turn=turns(
        tool("find_files", {"query": "resume"}),
        text("Your resume is protected, so I can't point to a location. "
             "It is shown on your screen.")), emit=out.append)
    s.say("where is my resume?")
    lines = said(out)
    assert not any("point to a location" in t for t in lines)
    assert ("I can't read it or send it to the AI — here it is for you:"
            in lines)


# -- 8. what was sent says when its list is cut --------------------------------

def test_a_long_sent_list_says_how_many_more(tmp_path):
    from assistant.egress import PersistentEgress
    from assistant.engine_tools import what_was_sent
    root = tmp_path / "Desktop"
    root.mkdir()
    for i in range(25):
        (root / f"note {i:02}.txt").write_text(f"n{i}", encoding="utf-8")
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    conn.commit()
    ids = [r[0] for r in conn.execute("SELECT item_id FROM items WHERE "
                                      "item_type = 'file'")]
    PersistentEgress(conn).add_provider_request(
        provider="deepseek", model="m", request_envelope={"x": 1},
        response_envelope={"y": 2}, item_ids=ids)
    shown = []

    class Context:
        def show_locally(self, event):
            shown.append(event)
    what_was_sent(conn, Context())
    listed = sum(len(e.citations) for e in shown)
    assert listed == 20
    assert "and 5 more" in " ".join(e.text for e in shown)
    conn.close()


# -- 10. lock-in is never silent -------------------------------------------------

def test_lock_in_shows_the_same_stage_lines_as_organise(lib, monkeypatch):
    import cli
    from assistant.engine_tools import _freeze
    conn, root = lib
    monkeypatch.setattr(cli, "main", lambda args, out=None, **_: 0)
    out = []

    class Context:
        cancel_requested = False

        def emit(self, event):
            out.append(event)
    _freeze(conn, str(root), Context())
    lines = [e.line for e in out if isinstance(e, ev.Progress)]
    assert "Reading and grouping your files…" in lines
    assert any("take several minutes" in e.text for e in out
               if isinstance(e, ev.Message))
