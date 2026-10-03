"""Every prompt the chat mentions is one the app printed; replies to it are
mapped by code, and nothing is cancelled silently."""
from __future__ import annotations

import io
import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from assistant import events as ev
from assistant.conversation_store import recent
from assistant.session import Session
from assistant.terminal import TerminalRenderer, run_events
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
    for name in ("a.png", "b.png", "c.png"):
        (root / name).write_bytes(name.encode() * 10)
    conn = open_database(tmp_path / "x.sqlite", scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.commit()
    yield conn, root
    conn.close()


def tool_call(name, args, i=0):
    return {"role": "assistant", "content": None, "tool_calls": [
        {"id": f"c{i}", "type": "function",
         "function": {"name": name, "arguments": json.dumps(args)}}]}


def text(reply):
    return {"role": "assistant", "content": reply}


def recording(*replies):
    seen = []
    it = iter(replies)

    def turn(messages, tools, config=None, **_):
        seen.append([dict(m) for m in messages])
        return next(it)
    turn.seen = seen
    return turn


def confirms(out):
    return [e for e in out if isinstance(e, ev.Confirm)]


def messages(out):
    return [e.text for e in out if isinstance(e, ev.Message)]


def rule_session(conn, out, *more):
    turn = recording(tool_call("remember_rule", {
        "text": "Always put installers in an Installers folder"}),
        text("Asked you to confirm."), *more)
    s = Session(conn, provider_turn=turn, emit=out.append)
    s.say("always put installers in an Installers folder")
    return s, turn


KINDS = ("rule", "settings", "folder", "freeze", "branch", "plan", "undo",
         "protection")


@pytest.mark.parametrize("kind", KINDS)
def test_every_confirmation_kind_is_printed(lib, kind):
    conn, _ = lib
    out = []
    s = Session(conn, provider_turn=recording(), emit=out.append)
    s._propose({"kind": kind, "ref": "x", "summary": "Do the thing?",
                "moves": [], "sensitive": False})
    shown = confirms(out)
    assert len(shown) == 1 and shown[0].summary == "Do the thing?"
    screen = io.StringIO()
    TerminalRenderer(screen)(shown[0])
    assert "Go ahead? 1) Yes  2) No" in screen.getvalue()
    assert json.loads(ev.to_json(shown[0]))["type"] == "confirm"


def test_the_model_is_told_exactly_what_was_shown(lib):
    conn, _ = lib
    out = []
    _, turn = rule_session(conn, out)
    tool_reply = [m for m in turn.seen[1] if m["role"] == "tool"][-1]
    assert ("A yes/no prompt is now on the person's screen: Remember this "
            "rule") in tool_reply["content"]
    assert len(confirms(out)) == 1


def test_another_message_keeps_the_prompt_and_says_so(lib):
    conn, _ = lib
    out = []
    s, turn = rule_session(conn, out, text("You have no rules yet."))
    s.say("what are my rules?")
    assert not any("Cancelled" in t for t in messages(out))
    system = turn.seen[-1][0]["content"]
    assert "Remember this rule" in system and "screen" in system
    assert "Still waiting for your yes or no" in messages(out)[-1]
    s.say("1")
    assert messages(out)[-1] == "Got it — I'll remember that."
    from assistant.memory_v1 import list_rules
    assert len(list_rules(conn)) == 1


@pytest.mark.parametrize("reply", ["yes", "y", "ok", "sure", "go ahead",
                                   "1", "ok actually yes move them"])
def test_natural_yes_answers_the_prompt(lib, reply):
    conn, root = lib
    out = []
    s = Session(conn, provider_turn=recording(
        tool_call("quick_sort", {"files": ["a.png"],
                                 "destination": "Screenshots"}),
        text("Shall I?")), emit=out.append)
    s.say("put a.png in Screenshots")
    s.say(reply)
    assert (root / "Screenshots" / "a.png").exists()
    assert messages(out)[-1].startswith("Moved 1 file")


@pytest.mark.parametrize("reply", ["no", "n", "2", "nope", "cancel", "stop"])
def test_no_and_cancel_say_so(lib, reply):
    conn, root = lib
    out = []
    s = Session(conn, provider_turn=recording(
        tool_call("quick_sort", {"files": ["a.png"],
                                 "destination": "Screenshots"}),
        text("Shall I?")), emit=out.append)
    s.say("put a.png in Screenshots")
    s.say(reply)
    assert messages(out)[-1] == "Cancelled. Nothing moved."
    assert (root / "a.png").exists()


def test_a_new_request_replaces_the_old_prompt_out_loud(lib):
    conn, _ = lib
    out = []
    s, _ = rule_session(conn, out, tool_call("quick_sort", {
        "files": ["a.png"], "destination": "Screenshots"}, 1),
        text("Here is the move."))
    s.say("move a.png into Screenshots now")
    said = messages(out)
    assert any(t.startswith("Cancelled: Remember this rule") for t in said)
    assert len(confirms(out)) == 2
    s.say("yes")
    assert messages(out)[-1].startswith("Moved 1 file")


def test_a_claimed_prompt_that_was_never_shown_is_removed(lib):
    conn, _ = lib
    out = []
    s = Session(conn, provider_turn=recording(text(
        "Asked you to confirm again. It's waiting on your screen — say yes "
        "and it sticks. Installers are .dmg files.")), emit=out.append)
    s.say("always put installers in an Installers folder")
    reply = messages(out)[-1]
    assert "screen" not in reply and "confirm" not in reply
    assert "Installers are .dmg files." in reply
    assert not confirms(out)


def test_the_outcome_is_remembered_so_nothing_goes_stale(lib):
    conn, root = lib
    out = []
    s = Session(conn, provider_turn=recording(
        tool_call("quick_sort", {"files": ["a.png"],
                                 "destination": "Screenshots"}),
        text("It's on your screen.")), emit=out.append)
    s.say("put a.png in Screenshots")
    s.say("yes")
    said = [m["content"] for m in recent(conn)]
    assert any("Move 1 file into Screenshots" in t for t in said)
    assert said[-2] == "yes" and said[-1].startswith("Moved 1 file")


def test_events_say_yes_answers_the_prompt(lib):
    conn, root = lib
    stdin = io.StringIO(
        json.dumps({"action": "say", "text": "put a.png in Screenshots"})
        + "\n" + json.dumps({"action": "say", "text": "yes"}) + "\n")
    stdout = io.StringIO()
    run_events(conn, stdin=stdin, stdout=stdout, provider_turn=recording(
        tool_call("quick_sort", {"files": ["a.png"],
                                 "destination": "Screenshots"}),
        text("Shall I?")))
    kinds = [json.loads(line)["type"] for line in stdout.getvalue().splitlines()]
    assert "confirm" in kinds and "done" in kinds
    assert (root / "Screenshots" / "a.png").exists()


def test_terminal_other_words_do_not_cancel(lib):
    from assistant.terminal import run_terminal
    conn, _ = lib
    stdout = io.StringIO()
    run_terminal(conn, folder=None, stdin=io.StringIO(
        "always put installers in an Installers folder\n"
        "what are my rules?\nyes\nquit\n"), stdout=stdout,
        provider_turn=recording(
            tool_call("remember_rule", {"text": "Installers go in Installers"}),
            text("Asked."), text("None yet.")))
    shown = stdout.getvalue()
    assert "Cancelled" not in shown
    assert "Got it — I'll remember that." in shown


def test_a_result_that_needs_another_yes_shows_that_prompt(lib, monkeypatch):
    import assistant.engine_tools as et
    conn, _ = lib
    ran = []

    def fake(conn, kind, ref, context=None):
        ran.append((kind, ref))
        if kind == "folder":
            return {"ok": True, "needs_confirmation": {
                "kind": "cloud", "ref": "here", "summary": "Use the cloud?",
                "moves": [], "sensitive": False,
                "on_no": {"kind": "organise_offline", "ref": "here"}}}
        return {"ok": True, "moved": False, "undo_token": None,
                "text": f"Ran {kind}."}
    monkeypatch.setattr(et, "execute_confirmed", fake)
    out = []
    s = Session(conn, provider_turn=recording(), emit=out.append)
    s._propose({"kind": "folder", "ref": "x", "summary": "Organise?",
                "moves": [], "sensitive": False})
    s.say("yes")
    assert confirms(out)[-1].summary == "Use the cloud?"
    assert not [e for e in out if isinstance(e, ev.Done)]
    s.say("no")
    assert ran[-1] == ("organise_offline", "here")
    assert messages(out)[-1] == "Ran organise_offline."
    assert et.level_allows(3, "cloud", 0, False) is False


# -- the sorter's questions ---------------------------------------------------

@dataclass(frozen=True)
class IndexCounts:
    indexed: int
    set_aside: int
    set_aside_folders: int
    protected: int
    held: int
    open_questions: int


def _question_session(conn, monkeypatch, turn):
    from questions.records import QuestionOption, StructuralQuestion
    from questions.schema import create_questions_schema
    from questions.store import record_question
    from questions.vocabulary import STRUCTURAL
    create_questions_schema(conn)
    record_question(conn, StructuralQuestion(
        question_id="reading.organization:columbia",
        answer_class=STRUCTURAL, prompt="What is Columbia to you?",
        evidence_context="Four files mention Columbia.",
        unlocks="This decides the layout.",
        will_not_do="It will not move anything.",
        scope="organization:columbia",
        handling_class="personal_non_sensitive",
        options=(QuestionOption("study", "I study there",
                                activates_schema="academic"),
                 QuestionOption("not_mine", "It is not about me")),
        evidence_refs=("sha256:" + "cd" * 32,)),
        asked_at="2026-10-03T12:00:00+00:00")
    conn.commit()
    import assistant.session as session_mod
    monkeypatch.setattr(session_mod, "_counts", lambda c: IndexCounts(
        5, 0, 0, 0, 0, 1))
    out = []
    s = Session(conn, provider_turn=turn, emit=out.append)
    s.open()
    s.say("yes")
    assert isinstance(out[-1], ev.Question)
    return s, out


def _answers(conn):
    return conn.execute("SELECT option_id, answer_type FROM "
                        "structural_answers").fetchall()


def test_a_question_back_is_not_recorded_as_an_answer(conn, monkeypatch):
    turn = recording(text("It's about four files that mention Columbia."))
    s, out = _question_session(conn, monkeypatch, turn)
    s.say("which file is it?")
    assert _answers(conn) == []
    assert "What is Columbia to you?" in turn.seen[-1][0]["content"]
    assert isinstance(out[-1], ev.Question)  # asked again, still open
    s.say("1")
    assert [tuple(r) for r in _answers(conn)] == [("study", "choice")]


def test_cancel_stops_the_questions_and_records_nothing(conn, monkeypatch):
    s, out = _question_session(conn, monkeypatch, recording())
    s.say("cancel")
    assert _answers(conn) == []
    assert "Stopped" in messages(out)[-1]
    assert s.asking is None
