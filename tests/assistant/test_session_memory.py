"""Rules, conversation memory and the no-model router."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from assistant.conversation_store import forget, recent, save_turn
from assistant.events import Confirm, Error, Message
from assistant.session import Session, route_without_model
from database_agent.db import open_database
from items.hot_index import rebuild_fts
from items.identity import reconcile_tree
from items.schema import create_items_schema


@pytest.fixture()
def db(tmp_path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "essay.txt").write_text("my essay", encoding="utf-8")
    (root / "id.pem").write_text("-----BEGIN", encoding="utf-8")
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.commit()
    yield conn
    conn.close()


def recording(*replies):
    seen = []
    it = iter(replies)

    def turn(messages, tools, config=None, **_):
        seen.append(messages)
        return next(it)
    turn.seen = seen
    return turn


def text(reply):
    return {"role": "assistant", "content": reply}


def tool(name, args):
    return {"role": "assistant", "content": None, "tool_calls": [
        {"id": "c1", "type": "function",
         "function": {"name": name, "arguments": json.dumps(args)}}]}


def test_a_new_session_remembers_the_last_one(db):
    Session(db, provider_turn=recording(text("hi Ada")),
            emit=lambda e: None).say("my name is Ada")
    second = recording(text("Ada"))
    Session(db, provider_turn=second, emit=lambda e: None).say("who am I?")
    users = [m["content"] for m in second.seen[0] if m["role"] == "user"]
    assert users == ["my name is Ada", "who am I?"]


def test_forget_conversations_empties_memory(db):
    Session(db, provider_turn=recording(text("ok")),
            emit=lambda e: None).say("remember me")
    assert recent(db)
    out = []
    s = Session(db, provider_turn=recording(tool("forget_conversations", {}),
                                            text("Asked.")), emit=out.append)
    s.say("forget our conversations")
    confirm = [e for e in out if isinstance(e, Confirm)][-1]
    s.confirm(confirm.confirm_id, True)
    assert recent(db) == []


def test_forget_clears_this_sessions_history_at_once(db):
    turn = recording(text("We talked about your essay."),
                     tool("forget_conversations", {}), text("Asked."),
                     text("Nothing yet."))
    s = Session(db, provider_turn=turn, emit=lambda e: None)
    s.say("my essay is late")
    s.say("forget our conversations")
    s.say("yes")
    s.say("what were we talking about?")
    sent = [m for m in turn.seen[-1] if m["role"] != "system"]
    assert sent[:2] == [
        {"role": "assistant",
         "content": "I've forgotten our past conversations."},
        {"role": "user", "content": "what were we talking about?"}]
    assert recent(db) == [
        {"role": "user", "content": "what were we talking about?"},
        {"role": "assistant", "content": "Nothing yet."}]


def test_a_line_naming_a_protected_file_is_not_stored(db):
    assert save_turn(db, "s1", "assistant", "Your key is id.pem in lib") is False
    assert save_turn(db, "s1", "assistant", "Your essay is essay.txt") is True
    assert [m["content"] for m in recent(db)] == ["Your essay is essay.txt"]
    assert forget(db) == 1


def test_remember_rule_asks_then_steers_the_next_prompt(db):
    out = []
    turn = recording(
        tool("remember_rule", {"text": "always put screenshots in Screenshots"}),
        text("I'll ask you."), text("ok"))
    s = Session(db, provider_turn=turn, emit=out.append)
    s.say("always put screenshots in Screenshots")
    confirm = [e for e in out if isinstance(e, Confirm)][-1]
    from assistant.memory_v1 import list_rules
    assert list_rules(db) == []
    s.confirm(confirm.confirm_id, True)
    assert [r["rule_text"] for r in list_rules(db)] == [
        "always put screenshots in Screenshots"]
    s.say("tidy my screenshots")
    assert "always put screenshots in Screenshots" in turn.seen[-1][0]["content"]


def test_provider_failure_then_the_router_answers_find(db):
    def boom(*a, **k):
        raise ConnectionError("network down")
    out = []
    s = Session(db, provider_turn=boom, emit=out.append)
    s.say("hello")
    assert isinstance(out[-1], Error)
    s.say("where is essay")
    assert isinstance(out[-1], Message)
    assert [c.name for c in out[-1].citations] == ["essay.txt"]


def test_router_shows_a_protected_match_locally_by_name(db):
    events = route_without_model(db, "find id.pem")
    message = events[-1]
    assert any(c.name == "id.pem" for c in message.citations)
    assert "protected" in message.text


def test_router_help_and_status(db):
    assert "find" in route_without_model(db, "help")[-1].text.lower()
    assert route_without_model(db, "status")[-1].text
