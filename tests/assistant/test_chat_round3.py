"""Round-3 chat fixes, each driven by a scripted fake provider: what the
model is told and what the person reads both come from code state."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from assistant import events as ev
from assistant.engine_tools import execute_confirmed, mark_sensitive, quick_sort
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
    (root / "Vaccination_Card.pdf").write_bytes(b"%PDF-1.4 x")
    (root / "essay.txt").write_text("my essay", encoding="utf-8")
    (root / "Screenshot 1.png").write_bytes(b"png one")
    (root / "Screenshot 2.png").write_bytes(b"png two")
    conn = open_database(tmp_path / "x.sqlite", scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.commit()
    yield conn, root
    conn.close()


def protect(conn, name):
    proposal = mark_sensitive(conn, name)["needs_confirmation"]
    assert execute_confirmed(conn, proposal["kind"], proposal["ref"])["ok"]


def tool_call(name, args=None, i=0):
    return {"role": "assistant", "content": None, "tool_calls": [
        {"id": f"c{i}", "type": "function",
         "function": {"name": name, "arguments": json.dumps(args or {})}}]}


def recording(*replies):
    seen = []
    it = iter(replies)

    def turn(messages, tools, config=None, **_):
        seen.append(json.loads(json.dumps(messages, default=str)))
        return next(it)
    turn.seen = seen
    return turn


def text(reply):
    return {"role": "assistant", "content": reply}


def said(out):
    return [e.text for e in out if isinstance(e, ev.Message)]


# -- 1. protected matches are never "not found" -----------------------------

def test_a_protected_match_tells_the_model_it_is_protected(lib):
    conn, _ = lib
    protect(conn, "Vaccination_Card.pdf")
    turn = recording(tool_call("find_files", {"query": "vaccination card"}),
                     text("It's protected — say open 1."))
    out = []
    Session(conn, provider_turn=turn, emit=out.append).say(
        "where is my vaccination card")
    tool_msg = [m for m in turn.seen[1] if m["role"] == "tool"][-1]["content"]
    assert "1 protected file matched this search" in tool_msg
    assert "vaccination card the person asked for" in tool_msg
    assert "never say not found" in tool_msg
    assert "open 1" in tool_msg
    assert "Vaccination_Card" not in json.dumps(turn.seen)


def test_a_not_found_reply_over_a_protected_match_is_corrected(lib):
    conn, _ = lib
    protect(conn, "Vaccination_Card.pdf")
    turn = recording(tool_call("find_files", {"query": "vaccination card"}),
                     text("I didn't find a vaccination card in what's "
                          "indexed. Anything else?"))
    out = []
    Session(conn, provider_turn=turn, emit=out.append).say(
        "where is my vaccination card")
    reply = said(out)[0]
    assert "didn't find" not in reply
    assert "protected" in reply and "open 1" in reply
    shown = [e for e in out if isinstance(e, ev.Message) and e.citations]
    assert shown[-1].citations[0].name == "Vaccination_Card.pdf"


def test_moving_a_protected_file_says_it_is_protected(lib):
    conn, _ = lib
    protect(conn, "Vaccination_Card.pdf")
    result = quick_sort(conn, ["vaccination card"])
    assert result["ok"] is False
    assert result["error"] == "That file is protected, so I won't move it."
    assert "Vaccination" not in json.dumps(result)


# -- 6b. a protected file left alone is said so, not "touches" ---------------

def test_quick_sort_leaving_a_protected_file_alone_says_so(lib):
    conn, _ = lib
    protect(conn, "Vaccination_Card.pdf")
    result = quick_sort(conn, ["Screenshot 1.png", "Vaccination_Card.pdf"])
    proposal = result["needs_confirmation"]
    assert proposal["summary"].endswith("1 protected file is left alone.")
    assert "Vaccination" not in json.dumps(result)
    import io
    from assistant.terminal import TerminalRenderer
    screen = io.StringIO()
    TerminalRenderer(screen)(ev.Confirm(
        confirm_id="x", summary=proposal["summary"], moves=(),
        sensitive=proposal["sensitive"], undo_available=True))
    assert "1 protected file is left alone." in screen.getvalue()
    assert "touches protected" not in screen.getvalue()


# -- 3. a folder this product already indexed counts as chosen ---------------

def test_organise_on_an_indexed_folder_does_not_ask_to_read_it(lib):
    from assistant.engine_tools import check_folder
    conn, root = lib
    s = Session(conn, provider_turn=recording(), emit=lambda e: None)
    path, refusal = check_folder(conn, str(root), s, "organise")
    assert refusal is None and path == root.resolve()


def test_an_unindexed_folder_still_asks(lib, tmp_path):
    from assistant.engine_tools import check_folder
    conn, _ = lib
    new = tmp_path / "new"
    new.mkdir()
    s = Session(conn, provider_turn=recording(), emit=lambda e: None)
    path, refusal = check_folder(conn, str(new), s, "organise")
    assert path is None and refusal["needs_confirmation"]["kind"] == "folder"


# -- 2. forgetting is true in the next session --------------------------------

def test_the_next_session_is_told_memory_was_cleared(lib):
    conn, _ = lib
    Session(conn, provider_turn=recording(text("ok")),
            emit=lambda e: None).say("remember my essay")
    out = []
    s = Session(conn, provider_turn=recording(
        tool_call("forget_conversations"), text("Asked.")), emit=out.append)
    s.say("forget our conversations")
    confirm = [e for e in out if isinstance(e, ev.Confirm)][-1]
    s.confirm(confirm.confirm_id, True)
    later = recording(text("You cleared it."))
    Session(conn, provider_turn=later, emit=lambda e: None).say(
        "what did we talk about?")
    system = later.seen[0][0]["content"]
    assert "The person cleared conversation memory on " in system
    assert "you have no record before that" in system
    assert "remember my essay" not in json.dumps(later.seen)


def test_a_session_with_no_forget_says_nothing_about_it(lib):
    conn, _ = lib
    turn = recording(text("hi"))
    Session(conn, provider_turn=turn, emit=lambda e: None).say("hello")
    assert "cleared conversation memory" not in turn.seen[0][0]["content"]


# -- 4. the AI permission names the provider and what no does ----------------

def test_the_cloud_question_names_the_provider_and_what_no_does(lib):
    conn, root = lib
    out = []
    s = Session(conn, provider_turn=recording(), emit=out.append)
    s._propose({"kind": "cloud", "ref": str(root), "summary": "Allow?",
                "moves": [], "sensitive": False,
                "on_no": {"kind": "organise_offline", "ref": str(root)}})
    confirm = [e for e in out if isinstance(e, ev.Confirm)][-1]
    assert "DeepSeek" in confirm.summary
    assert confirm.summary.endswith(
        "No: I'll organise without the AI; the result will be rougher.")
    assert s.pending[confirm.confirm_id]["summary"] == confirm.summary


# -- 6. polish ------------------------------------------------------------------

def test_undo_with_one_batch_asks_once_without_a_picker(lib, monkeypatch):
    from assistant import engine_tools
    conn, _ = lib
    monkeypatch.setattr(engine_tools, "recent_batches", lambda c: [
        {"token": "plan:p1", "text": "2 files into Images (3 Oct 14:05)"}])
    monkeypatch.setattr(engine_tools, "undo_proposal", lambda c, t: {
        "ok": True, "needs_confirmation": {
            "kind": "undo", "ref": t, "summary": "Put 2 files back?",
            "moves": [], "sensitive": False}})
    out = []
    Session(conn, provider_turn=recording(), emit=out.append).say("undo")
    assert [e.summary for e in out if isinstance(e, ev.Confirm)] == [
        "Put 2 files back?"]
    assert not any("Which batch" in t for t in said(out))


def test_undo_batches_are_listed_in_local_time(lib):
    from datetime import datetime, timezone
    from assistant.engine_tools import recent_batches
    from assistant.plans import ensure_plans_schema
    conn, _ = lib
    ensure_plans_schema(conn)
    utc = datetime(2026, 10, 3, 12, 0, tzinfo=timezone.utc)
    cols = [r[1] for r in conn.execute("PRAGMA table_info(assistant_plans)")]
    row = {c: "x" for c in cols}
    row.update(plan_id="p1", created_ts=utc.isoformat(), state="applied")
    conn.execute(f"INSERT INTO assistant_plans ({', '.join(row)}) VALUES "
                 f"({', '.join('?' * len(row))})", tuple(row.values()))
    line = recent_batches(conn)[0]["text"]
    assert "UTC" not in line
    assert utc.astimezone().strftime("%H:%M") in line


def test_a_pending_rule_is_reminded_once_then_dropped(lib):
    conn, _ = lib
    out = []
    s = Session(conn, provider_turn=recording(
        tool_call("remember_rule", {"text": "Always put PDFs in PDFs"}),
        text("Want me to remember that?"),
        text("Your essay is in lib."), text("Sure.")), emit=out.append)
    s.say("always put PDFs in PDFs")
    s.say("where is my essay")
    assert sum("Still waiting for your yes or no" in t for t in said(out)) == 1
    s.say("thanks")
    assert said(out)[-2:] == ["Not saved — say it again if you want that "
                              "rule.", "Sure."]
    assert s.on_screen is None and not s.pending
    assert sum("Still waiting for your yes or no" in t for t in said(out)) == 1


def test_the_copies_reply_does_not_disown_the_list_it_shows(lib):
    conn, root = lib
    (root / "essay (1).txt").write_text("my essay", encoding="utf-8")
    reconcile_tree(conn, root)
    conn.commit()
    out = []
    Session(conn, provider_turn=recording(
        tool_call("show_copies"),
        text("Here are the copies, listed below. I don't see those names "
             "myself; they stay on your Mac.")), emit=out.append).say(
        "show me copies")
    assert "don't see those names" not in said(out)[0]
    assert "Here are the copies" in said(out)[0]


def test_progress_off_a_terminal_prints_start_end_and_every_tenth():
    import io
    from assistant.terminal import TerminalRenderer
    screen = io.StringIO()
    render = TerminalRenderer(screen)
    for done in range(0, 201):
        render(ev.Progress(stage="index", done=done, total=200,
                           line=f"Indexing {done} of 200"))
    lines = screen.getvalue().splitlines()
    assert lines[0].strip() == "Indexing 0 of 200"
    assert lines[-1].strip() == "Indexing 200 of 200"
    assert len(lines) == 11


def test_a_model_question_is_not_dressed_as_a_choice_prompt(lib):
    conn, _ = lib
    out = []
    Session(conn, provider_turn=recording(
        tool_call("ask_user", {"question": "Which folder, Desktop or "
                                           "Documents?"})),
        emit=out.append).say("what should I look at?")
    assert not said(out)[0].startswith("Need your answer")
    assert said(out)[0] == "Which folder, Desktop or Documents?"


def test_a_new_confirm_hides_the_old_question_until_it_is_answered(lib):
    conn, _ = lib
    out = []
    s = Session(conn, provider_turn=recording(
        tool_call("set_level", {"level": 2}), text("Asked.")),
        emit=out.append)
    s.asking = ev.Question(question_id="q1", text="Where do essays go?",
                           why="", changes="",
                           options=(ev.Option(id="a", label="School"),))
    s.say("move without asking")
    after = out[[i for i, e in enumerate(out)
                 if isinstance(e, ev.Confirm)][-1]:]
    assert not any(isinstance(e, ev.Question) for e in after)
    out.clear()
    s.say("yes")
    assert isinstance(out[-1], ev.Question)


# -- 5. less is sent per question ----------------------------------------------

def test_a_find_turn_stays_small_however_long_the_chat(lib):
    conn, root = lib
    for i in range(40):
        (root / f"essay draft {i}.txt").write_text("my essay " * 100)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.commit()
    sizes, tool_sizes = [], []

    def turn(messages, tools, config=None, **_):
        sizes.append(len(json.dumps({"messages": messages, "tools": tools},
                                    default=str).encode()))
        tool_sizes.extend(len(m["content"].encode()) for m in messages
                          if m["role"] == "tool"
                          and m["content"] != "[earlier result dropped]")
        if messages[-1]["role"] == "user":
            return tool_call("find_files", {"query": "essay", "limit": 20})
        return text("Found your essays.")
    s = Session(conn, provider_turn=turn, emit=lambda e: None)
    for q in range(6):
        s.say(f"where is my essay {q}")
    assert max(tool_sizes) <= 6_000
    assert max(sizes) < 25_000, sizes
    # Earlier results are not resent: a turn adds only its own words.
    assert (sizes[-1] - sizes[1]) / 5 < 500, sizes
