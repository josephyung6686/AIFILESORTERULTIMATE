"""Lists the person asks for are built on this Mac from the database: the
protected files (never sent), the same-content copies, what went to the AI."""
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
    (root / "id.pem").write_text("-----BEGIN", encoding="utf-8")
    (root / "essay.txt").write_text("my essay", encoding="utf-8")
    (root / "notes.txt").write_text("same words", encoding="utf-8")
    (root / "notes (1).txt").write_text("same words", encoding="utf-8")
    (root / "other copy.txt").write_text("different", encoding="utf-8")
    conn = open_database(tmp_path / "x.sqlite", scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.commit()
    yield conn, root
    conn.close()


def tool_call(name, args=None, i=0):
    return {"role": "assistant", "content": None, "tool_calls": [
        {"id": f"c{i}", "type": "function",
         "function": {"name": name, "arguments": json.dumps(args or {})}}]}


def recording(*replies):
    seen = []
    it = iter(replies)

    def turn(messages, tools, config=None, **_):
        seen.append(json.dumps(messages, ensure_ascii=False))
        return next(it)
    turn.seen = seen
    return turn


def text(reply):
    return {"role": "assistant", "content": reply}


def shown(out):
    return [e for e in out if isinstance(e, ev.Message) and e.citations]


def test_protected_files_are_listed_locally_with_a_reason(lib):
    conn, _ = lib
    out = []
    turn = recording(tool_call("show_protected"), text("There they are."))
    Session(conn, provider_turn=turn, emit=out.append).say(
        "show me the list of protected files")
    listing = shown(out)[-1]
    assert [c.name for c in listing.citations] == ["id.pem"]
    assert listing.citations[0].note == "a key or password file"
    assert all("id.pem" not in sent for sent in turn.seen)
    assert 'shown_to_person\\": 1' in turn.seen[-1]


def test_a_file_the_person_protected_says_so(lib):
    conn, _ = lib
    out = []
    s = Session(conn, provider_turn=recording(
        tool_call("mark_sensitive", {"file": "essay.txt"}), text("Asked."),
        tool_call("show_protected", i=1), text("Listed.")), emit=out.append)
    s.say("protect essay.txt")
    s.say("yes")
    s.say("which files are protected?")
    notes = {c.name: c.note for c in shown(out)[-1].citations}
    assert notes["essay.txt"] == "you protected it"


def test_copies_are_the_same_content_pairs(lib):
    conn, _ = lib
    out = []
    turn = recording(tool_call("show_copies"), text("Those two."))
    Session(conn, provider_turn=turn, emit=out.append).say(
        "which files are the copies?")
    listing = shown(out)[-1]
    assert sorted(c.name for c in listing.citations) == ["notes (1).txt",
                                                         "notes.txt"]
    assert "other copy.txt" not in json.dumps(
        [c.name for c in listing.citations])


def test_what_was_sent_names_the_files_and_claims_nothing_more(lib):
    conn, _ = lib
    out = []
    s = Session(conn, provider_turn=recording(
        tool_call("find_files", {"query": "essay"}), text("Found it."),
        tool_call("what_was_sent", i=1), text("See above.")), emit=out.append)
    s.say("where is my essay")
    s.say("what did you send to the AI?")
    said = "\n".join(e.text for e in out if isinstance(e, ev.Message))
    report = [e for e in out if isinstance(e, ev.Message)
              and "requests" in e.text][-1]
    assert "essay.txt" in [c.name for c in report.citations]
    assert "id.pem" not in said
    assert "nothing else" not in said.lower()
