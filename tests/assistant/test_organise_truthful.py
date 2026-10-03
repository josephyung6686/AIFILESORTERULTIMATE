"""Organising a whole folder tells the person only what is true.

The judge's run said "Moved the files for X" when nothing on disk had changed:
the sorter exited 0 having moved nothing, and the exit code was read as moves.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from assistant import events as ev
from assistant.session import Session
from database_agent.db import open_database


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


def _tool(name, args):
    return {"role": "assistant", "content": None, "tool_calls": [
        {"id": "c0", "type": "function",
         "function": {"name": name, "arguments": json.dumps(args)}}]}


class _Model:
    def __init__(self) -> None:
        self.queue: list[dict] = []
        self.seen: list[str] = []

    def __call__(self, messages, tools, config=None, **_):
        self.seen.append(json.dumps(messages))
        return self.queue.pop(0)

    def then(self, name, args, reply="OK."):
        self.queue += [_tool(name, args), {"role": "assistant",
                                           "content": reply}]


@pytest.fixture()
def organised(tmp_path, monkeypatch):
    from items.schema import create_items_schema
    monkeypatch.delenv("ASSISTANT_ENABLE_APPLY", raising=False)
    corpus = _course(tmp_path)
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

    model.then("organise_folder", {"folder": str(corpus)})
    s.say("organise my course folder")
    model.then("freeze_plan", {"folder": str(corpus)})
    s.say("lock in the plan")
    confirm_last()
    yield corpus, s, model, out, confirm_last
    conn.close()


def _last_text(out) -> str:
    return [e for e in out if isinstance(e, (ev.Message, ev.Error))][-1].text


def test_a_real_move_reports_the_count_moved(organised):
    corpus, s, model, out, confirm_last = organised
    model.then("apply_branch", {"branch": "Education", "folder": str(corpus)})
    s.say("move Education")
    confirm_last()
    assert _last_text(out).startswith("Moved 2 files")
    assert all(p.startswith("Education/") for p in _files(corpus))


def test_applying_again_says_zero_moved_and_why(organised):
    corpus, s, model, out, confirm_last = organised
    model.then("apply_branch", {"branch": "Education", "folder": str(corpus)})
    s.say("move Education")
    confirm_last()
    after = _files(corpus)
    done_before = len([e for e in out if isinstance(e, ev.Done)])

    model.then("apply_branch", {"branch": "Education", "folder": str(corpus)})
    s.say("move Education again")
    confirm_last()
    assert _files(corpus) == after
    text = _last_text(out)
    assert text.startswith("0 files moved — "), text
    assert "already" in text
    done = [e for e in out if isinstance(e, ev.Done)][done_before:]
    assert not any(d.moved for d in done)


def test_a_file_moved_away_by_hand_is_not_reported_moved(organised):
    corpus, s, model, out, confirm_last = organised
    before = _files(corpus)
    for p in list(corpus.glob("*.txt")):
        p.rename(corpus.parent / p.name)       # the person moved them away
    model.then("apply_branch", {"branch": "Education", "folder": str(corpus)})
    s.say("move Education")
    confirm_last()
    text = _last_text(out)
    assert text.startswith("0 files moved — "), text
    assert not _files(corpus)
    assert before


def test_a_refused_lock_in_says_which_folder_and_why(tmp_path, monkeypatch):
    import cli
    from assistant.engine_tools import _freeze

    def refuses(args, out=None, **_):
        out.write("No plan was made for /x, and this is why:\n"
                  "  ReviewActionRefused: accepting 'branch:Technology' "
                  "produced no node. §5.4 populates a template\n")
        return 1
    monkeypatch.setattr(cli, "main", refuses)
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[])
    result = _freeze(conn, str(tmp_path), None)
    assert not result["ok"] and not result["moved"]
    assert "Technology" in result["text"]
    assert "ReviewActionRefused" not in result["text"]
    assert "branch:" not in result["text"]
    conn.close()


def test_a_lock_in_that_froze_nothing_is_not_offered_again(tmp_path,
                                                           monkeypatch):
    # Live run, 3 Oct: lock-in reran the sorter (and its model calls),
    # froze nothing, and the next "move AP world" offered the same yes/no.
    import cli
    from types import SimpleNamespace
    from assistant.engine_tools import _freeze, freeze_plan
    from assistant.engine_tools import put_setting

    def freezes_nothing(args, out=None, **_):
        out.write("Nothing was frozen: no file is ready to move.\n")
        return 0
    monkeypatch.setattr(cli, "main", freezes_nothing)
    corpus = _course(tmp_path).resolve()
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[])
    put_setting(conn, f"lock_in_blocked:{corpus}", "")
    result = _freeze(conn, str(corpus), None)
    assert not result["ok"]
    ctx = SimpleNamespace(chosen_folders={corpus}, emit=None)
    again = freeze_plan(conn, str(corpus), ctx)
    assert "needs_confirmation" not in again
    assert again["ok"] is False and again["error"] == result["text"]
    conn.close()


def test_a_refused_organise_says_so_and_offers_no_lock_in(tmp_path,
                                                          monkeypatch):
    # Judge 2: the organise run's refusal was thrown away, and the lock-in
    # yes/no was offered twice for a plan the sorter had already refused.
    import cli
    from types import SimpleNamespace
    from assistant.engine_tools import freeze_plan, run_organise

    def refuses(args, out=None, **_):
        out.write("No plan was made for /x, and this is why:\n"
                  "  ReviewActionRefused: accepting 'branch:Technology' "
                  "produced no node. §5.4 populates a template\n")
        return 1
    monkeypatch.setattr(cli, "main", refuses)
    corpus = _course(tmp_path)
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[])
    ctx = SimpleNamespace(chosen_folders={corpus.resolve()}, emit=None)
    result = run_organise(conn, corpus.resolve(), ctx, cloud=False)
    assert not result["ok"] and "Technology" in result["error"]
    frozen = freeze_plan(conn, str(corpus), ctx)
    assert "needs_confirmation" not in frozen
    assert "Technology" in frozen["error"]
    conn.close()


def test_an_answer_in_the_words_shown_changes_the_next_proposal(tmp_path):
    # Judge 2: "8 go straight into Photos and Media" was saved as free text
    # (the shown label matched no raw label), so the next run ignored it.
    from types import SimpleNamespace
    from assistant.engine_tools import (
        open_questions, question_event, run, run_organise)
    from assistant.organize_tools import show_tree
    from items.schema import create_items_schema
    corpus = tmp_path / "corpus"
    for course, names in (("CHEM1500", ("Lab Report.txt", "Syllabus.txt")),
                          ("PHYS1401", ("Problem Set 2.txt",
                                        "Lecture Notes.txt"))):
        (corpus / "Uni" / course).mkdir(parents=True)
        for name in names:
            (corpus / "Uni" / course / name).write_text(
                f"{course} {name[:-4]}\nColumbia University, Spring 2026\n"
                "Instructor: Dr. Ramirez\n")
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[])
    create_items_schema(conn)
    ctx = SimpleNamespace(chosen_folders={corpus.resolve()}, emit=None)
    run_organise(conn, corpus.resolve(), ctx, cloud=False)
    before = {f["path"] for f in show_tree(conn)["folders"]}
    shape = next(q for q in open_questions(conn)
                 if q.scope == "branch:Education")
    keep = question_event(shape, 1, 1, conn).options[-1].label
    assert keep == "Keep this branch as it is."
    said = run(conn, "answer_question", {"answer": keep},
               context=SimpleNamespace(question_queue=[shape], asking=None))
    assert said["recorded"] == "choice"
    run_organise(conn, corpus.resolve(), ctx, cloud=False)
    after = {f["path"] for f in show_tree(conn)["folders"]}
    assert "Education/Spring2026" in before
    assert "Education/Spring2026" not in after
    conn.close()


# -- organise says a little, and only what the database holds -----------------

def test_organise_streams_a_few_plain_lines_and_tells_the_model_counts(
        tmp_path):
    from items.schema import create_items_schema
    corpus = _course(tmp_path)
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[])
    create_items_schema(conn)
    out: list = []
    model = _Model()
    s = Session(conn, provider_turn=model, emit=out.append)
    s.chosen_folders.add(corpus.resolve())
    model.then("organise_folder", {"folder": str(corpus)})
    s.say("organise my course folder")

    progress = [e for e in out if isinstance(e, ev.Progress)]
    assert 1 <= len(progress) <= 4, [p.line for p in progress]
    shown = " ".join(e.text for e in out if isinstance(e, ev.Message))
    shown += " ".join(p.line for p in progress)
    to_model = model.seen[-1]
    for leak in ("--stop-after", "--answer", "--enable-cloud", ".sqlite",
                 "Plan database", "last_lines", "situation:"):
        assert leak not in shown, leak
        assert leak not in to_model, leak
    reply = json.loads(json.loads(to_model)[-1]["content"])
    for key in ("folders_proposed", "files_to_move",
                "files_already_in_place", "loose_files",
                "loose_files_to_move", "open_questions", "held", "set_aside"):
        assert isinstance(reply["summary"][key], int), key
    assert isinstance(reply["summary"]["top_folders"], list)
    # The proposal says where files go, not only which folders exist: the
    # judge's run "placed no loose files" because organise stopped at the
    # tree. Both loose course files get a place.
    assert reply["summary"]["loose_files"] == 2
    assert reply["summary"]["loose_files_to_move"] == 2
    assert reply["summary"]["top_folders"][0]["files_moving_in"] == 2
    conn.close()
