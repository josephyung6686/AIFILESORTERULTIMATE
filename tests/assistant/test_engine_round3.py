"""Round-3 engine follow-ups: reads that never commit, the app's opening,
plain words, encrypted databases, protection before organising, freeze."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from assistant import events as ev
from assistant.session import Session
from database_agent.db import open_database


def _uncommitted_row_survives_rollback(conn, read) -> bool:
    conn.execute("CREATE TABLE IF NOT EXISTS probe (v TEXT)")
    conn.execute("BEGIN")
    conn.execute("INSERT INTO probe VALUES ('x')")
    read(conn)
    conn.execute("ROLLBACK")
    return conn.execute("SELECT COUNT(*) FROM probe").fetchone()[0] == 1


def test_reading_a_setting_never_commits_the_callers_transaction(conn):
    from assistant.engine_tools import get_setting
    assert not _uncommitted_row_survives_rollback(
        conn, lambda c: get_setting(c, "permission_level", "1"))


def test_reading_recent_conversations_never_commits(conn):
    from assistant.conversation_store import recent
    assert not _uncommitted_row_survives_rollback(conn, recent)


def _encrypted_shared_db(tmp_path, monkeypatch):
    import database_agent.db as db
    key = tmp_path / "agent.key"
    path = tmp_path / "shared.sqlite"
    conn = open_database(path, encryption=True, encryption_key_file=key)
    conn.execute("CREATE TABLE marker (v TEXT)")
    conn.close()
    monkeypatch.setattr(db, "shared_database_path", lambda: path)
    monkeypatch.delenv("DATABASE_AGENT_KEY_FILE", raising=False)
    return key


def test_chat_on_an_encrypted_database_without_a_key_is_one_line(
        tmp_path, monkeypatch, capsys):
    import io
    from database_agent.entrypoint import main
    _encrypted_shared_db(tmp_path, monkeypatch)
    out = io.StringIO()
    assert main(["where is my cv"], out=out) == 2
    shown = out.getvalue() + capsys.readouterr().err
    assert shown.strip() == (
        "This database is encrypted. Set DATABASE_AGENT_KEY_FILE to your key "
        "file, then run database-agent again.")


def test_chat_on_an_encrypted_database_opens_with_the_key_file(
        tmp_path, monkeypatch):
    import io
    from assistant import terminal
    from database_agent.entrypoint import main
    key = _encrypted_shared_db(tmp_path, monkeypatch)
    monkeypatch.setenv("DATABASE_AGENT_KEY_FILE", str(key))
    seen = []

    def once(conn, text, **_):
        seen.append(conn.execute("SELECT COUNT(*) FROM marker").fetchone()[0])
        return 0
    monkeypatch.setattr(terminal, "run_once", once)
    assert main(["where is my cv"], out=io.StringIO()) == 0
    assert seen == [0]


def _events(out) -> list[dict]:
    return [json.loads(line) for line in out.getvalue().splitlines()]


def test_the_app_is_greeted_without_sending_an_action(conn):
    import io
    from assistant.terminal import run_events
    out = io.StringIO()
    run_events(conn, stdin=io.StringIO(""), stdout=out,
               provider_turn=lambda *a, **k: None)
    events = _events(out)
    assert events and "which folder" in events[-1]["text"].lower()


def test_an_extra_open_action_is_harmless(conn):
    import io
    from assistant.terminal import run_events
    out = io.StringIO()
    run_events(conn, stdin=io.StringIO(json.dumps({"action": "open"}) + "\n"),
               stdout=out, provider_turn=lambda *a, **k: None)
    events = _events(out)
    asked = [e for e in events if "which folder" in e.get("text", "").lower()]
    assert len(asked) == 1
    assert not [e for e in events if e["type"] == "error"]


# -- organise -> freeze -> apply -> undo, through the real sorter -------------

def _course(tmp_path: Path) -> Path:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "PHYS 1403 homework 2.txt").write_text(
        "PHYS 1403 Homework 2\n\nSpring 2026. Due 2026-03-01. "
        "Solve the following.\n")
    (corpus / "PHYS 1403 syllabus.txt").write_text(
        "PHYS 1403 Syllabus\n\nSpring 2026. Instructor: A. Raymer.\n")
    return corpus


def _files(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file()}


class _Model:
    """A provider that plays the next queued reply; the test queues the
    next tool call once it has read what the person was shown."""

    def __init__(self) -> None:
        self.queue: list[dict] = []
        self.seen: list[str] = []

    def __call__(self, messages, tools, config=None, **_):
        self.seen.append(json.dumps(messages))
        return self.queue.pop(0)

    def then(self, name, args, reply="OK."):
        self.queue += [_tool(name, args), {"role": "assistant",
                                           "content": reply}]


def test_organise_freeze_apply_and_undo_in_the_conversation(tmp_path,
                                                            monkeypatch):
    from items.schema import create_items_schema
    monkeypatch.delenv("ASSISTANT_ENABLE_APPLY", raising=False)
    corpus = _course(tmp_path)
    before = _files(corpus)
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[])
    create_items_schema(conn)
    out: list = []
    model = _Model()
    s = Session(conn, provider_turn=model, emit=out.append)
    s.chosen_folders.add(corpus.resolve())

    def confirm_last(yes=True):
        confirm = [e for e in out if isinstance(e, ev.Confirm)][-1]
        s.confirm(confirm.confirm_id, yes)
        return confirm

    # Apply before any freeze is refused plainly.
    model.then("apply_branch", {"branch": "Education", "folder": str(corpus)})
    s.say("move the Education folder")
    assert "lock in" in model.seen[-1]

    model.then("organise_folder", {"folder": str(corpus)})
    s.say("organise my course folder")
    assert _files(corpus) == before

    model.then("freeze_plan", {"folder": str(corpus)})
    s.say("lock in the plan")
    asked = confirm_last()
    assert "lock in the plan" in asked.summary and not asked.moves
    assert _files(corpus) == before
    locked = [e for e in out if isinstance(e, ev.Message)][-1].text
    assert locked.startswith("Locked in: 2 files ready to move")
    branches = [line.strip() for line in locked.splitlines()[1:]]
    assert branches and all(b.startswith("Education/") for b in branches)

    # Naming the parent moves every branch under it.
    model.then("apply_branch", {"branch": "Education", "folder": str(corpus)})
    s.say("move Education")
    assert confirm_last().undo_available
    moved = _files(corpus)
    assert sorted(moved.values()) == sorted(before.values())
    assert all(p.startswith("Education/") for p in moved), moved

    model.then("undo_last", {})
    s.say("undo that")
    confirm_last()
    assert _files(corpus) == before
    conn.close()


# -- protect / release before organising ---------------------------------------

def test_protect_works_before_any_organise_and_release_says_why_not(lib):
    from assistant.engine_tools import execute_confirmed
    from items.file_identity import item_is_sensitive
    item = lib.execute("SELECT item_id FROM items WHERE display_label = "
                       "'bank essay.txt'").fetchone()[0]
    assert not item_is_sensitive(lib, item)
    done = execute_confirmed(lib, "protection", f"hold:{item}")
    assert done["ok"], done
    assert item_is_sensitive(lib, item)
    assert "protected now" in done["text"]
    # Releasing widens what may leave the Mac, so it keeps needing the
    # sorter's own record: a plain sentence, nothing changed.
    undone = execute_confirmed(lib, "protection", f"release:{item}")
    assert item_is_sensitive(lib, item)
    assert not undone["ok"]
    assert undone["text"] == ("Nothing changed — organise this folder first, "
                              "then I can treat it as an ordinary file.")


# -- plain words --------------------------------------------------------------

def test_the_model_is_told_to_speak_plainly(conn):
    turn = _scripted({"role": "assistant", "content": "Hello."})
    Session(conn, provider_turn=turn, emit=lambda e: None).say("hi")
    assert "not sorted yet" in turn.seen[0] and "unplaced" in turn.seen[0]


def test_internal_words_the_model_emits_are_replaced(conn):
    out = []
    turn = _scripted({"role": "assistant", "content": (
        "3 files are unplaced and 2 are held under academic.coursework "
        "(version_e496ca34_12). You typed my_resume.pdf, which I held off "
        "moving.")})
    Session(conn, provider_turn=turn, emit=out.append).say("what's left?")
    said = [e.text for e in out if isinstance(e, ev.Message)][-1]
    assert "not sorted yet" in said and "2 are protected" in said
    for code in ("unplaced", "academic.coursework", "version_e496ca34_12"):
        assert code not in said
    # Ordinary English and a person's own file name are left alone.
    assert "You typed my_resume.pdf, which I held off moving." in said


# -- protected names never reach the model (spec §3) -------------------------

def _scripted(*replies):
    seen = []
    it = iter(replies)

    def turn(messages, tools, config=None, **_):
        seen.append(json.dumps(messages))
        return next(it)
    turn.seen = seen
    return turn


def _tool(name, args):
    return {"role": "assistant", "content": None, "tool_calls": [
        {"id": "c1", "type": "function",
         "function": {"name": name, "arguments": json.dumps(args)}}]}


@pytest.fixture()
def lib(tmp_path):
    from items.hot_index import rebuild_fts
    from items.identity import reconcile_tree
    from items.schema import create_items_schema
    root = tmp_path / "lib"
    root.mkdir()
    (root / "bank statement.pem").write_text("-----BEGIN", encoding="utf-8")
    (root / "bank essay.txt").write_text("essay on banks", encoding="utf-8")
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.commit()
    yield conn
    conn.close()


def test_a_protected_name_is_absent_from_every_model_request(lib):
    out = []
    turn = _scripted(_tool("find_files", {"query": "bank"}),
                     {"role": "assistant", "content": "Found them."},
                     _tool("find_files", {"query": "bank statement"}),
                     {"role": "assistant", "content": "Still there."})
    s = Session(lib, provider_turn=turn, emit=out.append)
    s.say("where are my bank files?")
    s.say("and the other one?")
    item = lib.execute("SELECT item_id FROM items WHERE display_label = "
                       "'bank statement.pem'").fetchone()[0]
    for request in turn.seen:
        assert "statement.pem" not in request
        assert item not in request
    assert "1 protected file matched" in turn.seen[1]
    shown = [c.name for e in out if isinstance(e, ev.Message)
             for c in e.citations]
    assert "bank statement.pem" in shown
