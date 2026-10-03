"""User-judge round 4: each test is one thing a person saw that was wrong.
Only scripted providers; no real model is called."""
from __future__ import annotations

import json
import threading
from pathlib import Path

import pytest

from assistant import events as ev
from assistant.session import Session
from database_agent.db import open_database
from items.hot_index import find_files, rebuild_fts
from items.identity import reconcile_tree
from items.schema import create_items_schema

NAMES = ("Joseph Yung-Resume.docx", "Joseph Yung vaccination card.jpg",
         "Screenshot 2024-05-31 at 11.31.12 PM.png",
         "Screenshot 2026-06-06 at 1.19.04 AM.png", "AP history quiz.pdf",
         "a.png", "b.png")
HELD = ("Joseph Yung vaccination card.jpg",
        "Screenshot 2026-06-06 at 1.19.04 AM.png")


@pytest.fixture(autouse=True)
def _apply_flag_unset(monkeypatch):
    monkeypatch.delenv("ASSISTANT_ENABLE_APPLY", raising=False)


@pytest.fixture()
def lib(tmp_path: Path):
    root = tmp_path / "Desktop"
    root.mkdir()
    for name in NAMES:
        (root / name).write_bytes(name.encode() * 4)
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    conn.executemany("UPDATE items SET typing_state = 'held' "
                     "WHERE display_label = ?", [(n,) for n in HELD])
    rebuild_fts(conn)
    conn.commit()
    yield conn, root
    conn.close()


def turns(*replies):
    it = iter(replies)
    return lambda *a, **k: next(it)


def tool(name, args):
    return {"role": "assistant", "content": None, "tool_calls": [
        {"id": "c1", "type": "function",
         "function": {"name": name, "arguments": json.dumps(args)}}]}


def text(reply):
    return {"role": "assistant", "content": reply}


def said(out):
    return [e.text for e in out if isinstance(e, (ev.Message, ev.Error))]


def listed(out):
    return [c.name for e in out if isinstance(e, ev.Message)
            for c in e.citations]


# -- 1. a dropped yes/no says what was dropped ---------------------------------

def test_a_dropped_rule_prompt_names_the_rule(lib):
    conn, _ = lib
    out = []
    s = Session(conn, provider_turn=turns(
        tool("remember_rule", {"text": "Name folders in lowercase"}),
        text("Want me to remember that?"),
        text("Nothing saved yet."), text("Sure.")), emit=out.append)
    s.say("remember that i like lowercase folder names")
    s.say("what do you remember?")
    s.say("what have you sent to the cloud?")
    dropped = [t for t in said(out) if "ask again" in t.lower()
               or "say it again" in t.lower()]
    assert len(dropped) == 1
    assert "Name folders in lowercase" in dropped[0]
    assert "Nothing changed" in dropped[0]
    assert s.on_screen is None and not s.pending


def test_a_reply_emptied_by_its_own_list_is_not_ok(lib):
    conn, _ = lib
    out = []
    s = Session(conn, provider_turn=turns(
        tool("what_was_sent", {}),
        text("It's all on your screen.")), emit=out.append)
    s.say("what have you sent to the cloud so far?")
    assert "OK." not in said(out)
    assert any(t.startswith("Today:") for t in said(out))


# -- 3. a protected file is shown only when it really matches ------------------

def _protected_hits(conn, query):
    return [h.display_label for h in find_files(conn, query).hits
            if h.protected]


def test_a_protected_file_matching_one_word_of_many_is_not_shown(lib):
    conn, _ = lib
    assert _protected_hits(conn, "Joseph Yung resume") == []
    assert _protected_hits(conn, "screenshot may 31 2024") == []


def test_a_protected_file_the_person_names_is_still_shown(lib):
    conn, _ = lib
    assert _protected_hits(conn, "vaccination card") == [
        "Joseph Yung vaccination card.jpg"]
    assert _protected_hits(conn, "Joseph Yung") == [
        "Joseph Yung vaccination card.jpg"]


# -- 4. the list under a reply is what the reply names ------------------------

def test_a_not_found_reply_lists_nothing(lib):
    conn, _ = lib
    out = []
    s = Session(conn, provider_turn=turns(
        tool("find_files", {"query": "history quiz"}),
        text("I don't see a tax return. The only hit was a history quiz, "
             "which isn't it.")), emit=out.append)
    s.say("find my tax return")
    assert listed(out) == []


def test_a_reply_that_names_no_file_lists_none(lib):
    conn, _ = lib
    out = []
    s = Session(conn, provider_turn=turns(
        tool("find_files", {"query": "2024"}),
        text("Here's the plan for your 2024 screenshots.")), emit=out.append)
    s.say("put my screenshots from 2024 in a folder")
    assert listed(out) == []


# -- 5. background reading never splices into a reply; it names what it hid ----

def test_background_progress_waits_for_the_reply(lib):
    conn, _ = lib
    out = []
    holder = {}

    def provider(*a, **k):
        t = threading.Thread(target=lambda: holder["s"].emit(ev.Progress(
            stage="read", done=1, total=3, line="Reading document text… "
                                                 "2 left")))
        holder["t"] = t
        t.start()
        t.join(0.5)
        return text("Your quiz is AP history quiz.pdf.")
    s = Session(conn, provider_turn=provider, emit=out.append)
    holder["s"] = s
    s.say("where is my quiz?")
    holder["t"].join(5)
    kinds = [type(e).__name__ for e in out]
    assert kinds.index("Progress") > kinds.index("Message")


def test_newly_protected_files_are_named_to_the_person(lib, monkeypatch):
    from items import indexing
    from assistant.session import start_reading
    conn, _ = lib
    card = conn.execute("SELECT item_id FROM items WHERE display_label = ?",
                        (HELD[0],)).fetchone()[0]
    monkeypatch.setattr(indexing, "read_document_text",
                        lambda c, **k: indexing.ReadOutcome(
                            3, protected_items=(card,)))
    out = []
    start_reading(conn, out.append).join(5)
    last = said(out)[-1]
    assert "1 more file looks personal" in last
    assert HELD[0] in last


# -- 6. undo asks once, and its result is not its question ---------------------

def test_undo_that_asks_once_and_says_the_result_plainly(lib):
    conn, root = lib
    out = []
    s = Session(conn, provider_turn=turns(
        tool("quick_sort", {"files": ["a.png", "b.png"],
                            "destination": "Pictures"}),
        text("Shall I?")), emit=out.append)
    s.say("put a.png and b.png in Pictures")
    s.say("yes")
    out.clear()
    s.say("undo that")                     # code, not the model
    asks = [e for e in out if isinstance(e, ev.Confirm)]
    assert len(asks) == 1 and said(out) == []
    s.say("yes")
    assert (root / "a.png").exists()
    assert said(out)[-1] != asks[0].summary
    assert said(out)[-1] == "2 files are back where they were."
