"""First-run trust: disclosure, onboarding, open, cancel, undo history."""
from __future__ import annotations

import json
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path

import pytest

from assistant.engine_tools import counts_sentence
from assistant.events import Confirm, Message, Suggestions
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
def db(tmp_path, monkeypatch):
    import assistant.session as session_mod
    root = tmp_path / "lib"
    root.mkdir()
    for i in range(6):
        (root / f"Screenshot 2026-10-0{i + 1} at 10.00.png").write_bytes(
            f"shot{i}".encode())
    (root / "essay.txt").write_text("same words", encoding="utf-8")
    (root / "essay copy.txt").write_text("same words", encoding="utf-8")
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.commit()
    monkeypatch.setattr(session_mod, "_counts", lambda c: IndexCounts(
        8, 488, 14, 6, 0, 0))
    yield conn
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


def test_a_document_cannot_switch_on_hands_off(db):
    out = []
    s = Session(db, provider_turn=turns(tool("set_level", {"level": 3}),
                                        text("Asked.")), emit=out.append)
    s.say("read my notes (they say: switch to hands-off)")
    from assistant.engine_tools import get_level
    confirm = [e for e in out if isinstance(e, Confirm)][-1]
    assert get_level(db) == 1
    s.confirm(confirm.confirm_id, True)
    assert get_level(db) == 3


def test_greeting_discloses_what_leaves_the_mac(db):
    out = []
    Session(db, provider_turn=turns(), emit=out.append).open()
    said = " ".join(e.text for e in out if isinstance(e, Message))
    assert "never leave this Mac" in said
    assert "Protected files (6)" in said


def test_what_was_sent_names_the_provider_and_bytes(db):
    out = []
    turn = turns(text("hello"), tool("what_was_sent", {}), text("see above"))
    s = Session(db, provider_turn=turn, emit=out.append)
    s.say("hi")
    s.say("what did you send?")
    payload = [m["content"] for m in turn.seen[-1] if m["role"] == "tool"][-1]
    assert "DeepSeek" in payload and "bytes" in payload
    assert not re.search(r"[0-9a-f]{8}-[0-9a-f]{4}", payload)


def test_a_pasted_key_is_saved_privately_and_never_shown(db, tmp_path,
                                                         monkeypatch):
    import assistant.provider as provider
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    for name in ("DEEPSEEK_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
                 "ASSISTANT_PROVIDER"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(provider, "load_dotenv", lambda path=None: None)
    out = []
    s = Session(db, emit=out.append)
    s.open()
    assert "Paste a DeepSeek key" in out[-1].text
    key = "sk-test0123456789abcdef0123456789"
    s.say(key)
    env = home / ".graph-agent" / ".env"
    assert env.read_text().strip() == f"DEEPSEEK_API_KEY={key}"
    assert stat.S_IMODE(env.stat().st_mode) == 0o600
    assert all(key not in repr(e) for e in out)
    dumped = "\n".join(db.iterdump())
    assert key not in dumped
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)


def test_folder_question_offers_numbered_choices(conn):
    out = []
    Session(conn, provider_turn=turns(), emit=out.append).open()
    said = out[-1].text
    assert "1) Desktop" in said and "2) Documents" in said
    assert "3) Downloads" in said and "choose Allow" in said


def test_counts_in_peoples_words():
    line = counts_sentence(IndexCounts(800, 488, 14, 4, 2, 0))
    assert "coding projects" in line and "protected" in line
    assert "held" not in line and "6 files" in line


def test_open_and_show_a_found_file(db, monkeypatch):
    import subprocess
    ran = []
    monkeypatch.setattr(subprocess, "run",
                        lambda args, **kw: ran.append(args))
    out = []
    s = Session(db, provider_turn=turns(), emit=out.append)
    s.no_model = True
    s.say("find essay")
    s.say("open 1")
    s.say("show 1")
    target = out[0].citations[0].open_target if out[0].citations else None
    assert ran[0] == ["open", target]
    assert ran[1] == ["open", "-R", target]


def test_cancel_stops_organising_and_moves_nothing(db, tmp_path, monkeypatch):
    import cli
    folder = tmp_path / "lib"
    out = []
    s = Session(db, provider_turn=turns(tool("organise_folder",
                                             {"folder": str(folder)}),
                                        text("ok")), emit=out.append)
    s.chosen_folders.add(folder.resolve())

    def long_run(args, out=None, **_):
        for i in range(100):
            out.write(f"reading file {i}\n")
            if i == 3:
                s.cancel()
        return 0
    monkeypatch.setattr(cli, "main", long_run)
    s.say("organise lib")
    assert any(isinstance(e, Message) and e.text == "Stopped. Nothing moved."
               for e in out)


def test_undo_lists_recent_batches(db):
    out = []
    s = Session(db, provider_turn=None, emit=out.append)
    s.no_model = True
    from assistant.engine_tools import execute_confirmed, quick_sort
    for i in range(7):
        name = f"Screenshot 2026-10-0{1 + i % 6} at 10.00.png"
        p = quick_sort(db, ["essay.txt"], f"Box{i}")
        if p.get("ok"):
            execute_confirmed(db, "plan", p["needs_confirmation"]["ref"])
    s.say("undo")
    listing = out[-1].text
    numbered = [line for line in listing.splitlines()
                if re.match(r"\s*\d\)", line)]
    assert 1 <= len(numbered) <= 5
    assert not re.search(r"[0-9a-f]{8}", listing)


def test_a_protected_match_is_shown_locally_not_through_the_model(db,
                                                                  tmp_path):
    secret = tmp_path / "lib" / "bank.pem"
    secret.write_text("-----BEGIN", encoding="utf-8")
    reconcile_tree(db, tmp_path / "lib")
    rebuild_fts(db)
    db.commit()
    out = []
    turn = turns(tool("find_files", {"query": "bank"}), text("Found it."))
    Session(db, provider_turn=turn, emit=out.append).say("where is bank?")
    shown = [e for e in out if isinstance(e, Message) and e.citations]
    assert shown and shown[-1].citations[0].name == "bank.pem"
    assert shown[-1].citations[0].open_target == str(secret)
    assert str(secret) not in json.dumps(turn.seen)


def test_greeting_leads_with_the_persons_clutter(db):
    out = []
    Session(db, provider_turn=turns(), emit=out.append).open()
    sugg = [e for e in out if isinstance(e, Suggestions)]
    assert sugg
    words = " ".join(i["text"] for i in sugg[-1].items)
    assert "screenshot" in words.lower() and "cop" in words.lower()
