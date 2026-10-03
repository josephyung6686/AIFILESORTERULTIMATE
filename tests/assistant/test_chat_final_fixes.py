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


# -- 1. the offline router ---------------------------------------------------

CLOCK = "2026-10-03T12:00:00+00:00"


def a_question(qid, **kw):
    from questions.records import QuestionOption, StructuralQuestion
    from questions.vocabulary import STRUCTURAL
    fields = dict(
        question_id=qid, answer_class=STRUCTURAL,
        prompt="What kind of material is Columbia?",
        evidence_context="Four files mention Columbia.",
        unlocks="This decides which folder layout is offered.",
        will_not_do="It will not move, rename or delete anything.",
        scope="organization:columbia",
        handling_class="personal_non_sensitive",
        options=(QuestionOption("study", "I study there",
                                activates_schema="academic"),
                 QuestionOption("not_mine", "It is not about me")),
        evidence_refs=("sha256:" + "cd" * 32,))
    fields.update(kw)
    return StructuralQuestion(**fields)


def out_of_credit(*a, **k):
    raise RuntimeError("402 Insufficient Balance")


def test_after_the_model_fails_find_and_where_still_answer(lib):
    conn, _ = lib
    out = []
    s = Session(conn, provider_turn=out_of_credit, emit=out.append)
    s.say("find resume")
    assert isinstance(out[0], ev.Error) and "out of credit" in out[0].text
    found = [e for e in out if isinstance(e, ev.Message) and e.citations]
    assert found and found[-1].citations[0].name == "Resume 2026.docx"
    out.clear()
    s.say("where is my resume?")
    assert not any(isinstance(e, ev.Error) for e in out)
    assert out[-1].citations[0].name == "Resume 2026.docx"


def test_question_counts_agree_everywhere(lib, monkeypatch):
    import assistant.session as session_mod
    from items.suggest import suggestions
    from questions.schema import create_questions_schema
    from questions.store import record_question
    conn, _ = lib
    create_questions_schema(conn)
    record_question(conn, a_question("q.askable"), asked_at=CLOCK)
    # About a folder's unreadable files: nothing a person could name.
    record_question(conn, a_question("q.unnamed", scope="folder:Nowhere"),
                    asked_at=CLOCK)
    conn.commit()
    monkeypatch.setattr(session_mod, "_counts", lambda c: IndexCounts(
        2, 0, 0, 0, 0, 2))
    out = []
    Session(conn, provider_turn=turns(), emit=out.append).open()
    counts = [e for e in out if isinstance(e, ev.Counts)]
    assert counts[0].open_questions == 1
    assert any("I have 1 question" in t for t in said(out))
    waiting = [i["text"] for i in suggestions(conn)
               if i["kind"] == "open_questions"]
    assert waiting == ["1 question is waiting for an answer."]


# -- 2. no id leak, no junk tail ------------------------------------------------

def test_an_id_fragment_line_never_reaches_the_screen(lib):
    conn, _ = lib
    out = []
    s = Session(conn, provider_turn=turns(
        text("Your resume is on the Desktop.\nCite: -56b1-4793-9f82-")),
        emit=out.append)
    s.say("where is my resume?")
    assert said(out) == ["Your resume is on the Desktop."]


def test_a_find_answer_shows_the_named_file_not_the_junk_tail(lib):
    conn, root = lib
    for folder in ("cache", "Old page_files", "notes"):
        (root / folder).mkdir()
        for i in range(3):
            (root / folder / f"resume part {i}.txt").write_text(
                "resume words", encoding="utf-8")
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.commit()
    out = []
    s = Session(conn, provider_turn=turns(
        tool("find_files", {"query": "resume"}),
        text("Your resume is Resume 2026.docx on the Desktop.")),
        emit=out.append)
    s.say("where is my resume?")
    shown = [c.name for e in out if isinstance(e, ev.Message)
             for c in e.citations]
    assert shown == ["Resume 2026.docx"]


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


# -- 9. suggestions leave out caches, saved pages and archives ----------------

def test_suggestions_skip_junk_and_archive_folders(lib):
    from items.suggest import files_for
    conn, root = lib
    (root / "essay copy.txt").write_text("an essay", encoding="utf-8")
    for folder in ("cache", "_archive/old", "Page_files"):
        (root / folder).mkdir(parents=True)
        (root / folder / "report.txt").write_text("same", encoding="utf-8")
        (root / folder / "report copy.txt").write_text("same",
                                                       encoding="utf-8")
        (root / folder / "setup.dmg").write_bytes(b"x")
    reconcile_tree(conn, root)
    conn.commit()
    assert [f["display_label"] for f in files_for(conn, "copies")] == [
        "essay copy.txt"]
    assert files_for(conn, "installers") == []


# -- 4. say only what is on the screen ----------------------------------------

def test_the_model_is_told_the_question_exactly_as_printed(lib):
    import io
    from assistant.terminal import TerminalRenderer
    conn, _ = lib
    q = ev.Question(question_id="q1", text="Where should the 4 files in "
                    "Education (e.g. a.pdf, b.pdf, c.pdf) go?",
                    why="They share a course name.", changes="",
                    options=(ev.Option("o1", "Education/Fall"),
                             ev.Option("o2", "Education/Spring")),
                    files_preview=("a.pdf", "b.pdf", "c.pdf"), count=4,
                    index=1, of=3)
    screen = io.StringIO()
    TerminalRenderer(screen)(q)
    s = Session(conn, provider_turn=turns(), emit=lambda e: None)
    s.asking = q
    told = s.screen_state()
    for line in screen.getvalue().splitlines():
        assert line.strip() in told


def test_a_branch_question_names_files_from_the_folder_on_disk(lib):
    from types import SimpleNamespace
    from assistant.engine_tools import _question_files
    conn, root = lib
    (root / "Education").mkdir()
    for name in ("syllabus.pdf", "notes.txt"):
        (root / "Education" / name).write_text(name, encoding="utf-8")
    reconcile_tree(conn, root)
    conn.commit()
    names = _question_files(conn, SimpleNamespace(scope="branch:Education"))
    assert sorted(names) == ["notes.txt", "syllabus.pdf"]


def test_organise_after_a_yes_shows_question_one_now(lib, monkeypatch):
    import assistant.engine_tools as engine
    from questions.schema import create_questions_schema
    from questions.store import record_question
    conn, root = lib
    create_questions_schema(conn)
    record_question(conn, a_question("q.askable"), asked_at=CLOCK)
    conn.commit()

    def organised(conn, kind, ref, context=None):
        context.ask_questions_after_turn = True
        return {"ok": True, "moved": False, "undo_token": None,
                "text": "I've looked through the folder. Nothing moved. "
                        "I have 1 question first."}
    monkeypatch.setattr(engine, "execute_confirmed", organised)
    out = []
    s = Session(conn, provider_turn=turns(), emit=out.append)
    s._propose({"kind": "cloud", "ref": str(root), "moves": []})
    s.confirm(s.on_screen, True)
    assert isinstance(out[-1], ev.Question)


# -- 6. folders by name ---------------------------------------------------------

def test_list_folders_shows_two_levels_and_hides_what_it_must(lib,
                                                              monkeypatch):
    import assistant.organize_tools as organize
    from types import SimpleNamespace
    from assistant.engine_tools import run
    conn, root = lib
    for rel in ("外泌體/page_files", "外泌體/photos",
                "Chinese University Application Materials/Forms",
                "my-project/src", "Tool.app/Contents", "cache"):
        (root / rel).mkdir(parents=True)
    monkeypatch.setattr(organize, "_set_aside_folders",
                        lambda c: [root / "my-project"])
    result = run(conn, "list_folders", {},
                 context=SimpleNamespace(chosen_folders={root}))
    blob = json.dumps(result, ensure_ascii=False)
    names = {f["name"]: f["inside"] for f in result["folders"]}
    assert names["外泌體"] == ["photos"]
    assert names["Chinese University Application Materials"] == ["Forms"]
    assert "my-project" not in blob and "Tool.app" not in blob
    assert "cache" not in names
    assert result["protected_folders"] == 1
    assert result["set_aside_projects"] == 1


def test_list_folders_is_a_tool_the_model_has():
    from assistant.registry import ENGINE_TOOLS
    assert "list_folders" in ENGINE_TOOLS
