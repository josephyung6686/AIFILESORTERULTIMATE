"""A sorter question reads as one plain sentence about named files.

Judge 2 read "This option would create 2 term.", "warning: \"2 of this
level's children hold 1 file(s) or fewer\"", the same option three times,
and "Where should the files in Desktop go?" naming no file.
"""
from __future__ import annotations

import pytest

from assistant.engine_tools import display_name, question_event
from database_agent.db import open_database
from items.hot_index import rebuild_fts
from items.identity import reconcile_tree
from items.schema import create_items_schema
from questions.triggers import (
    DestinationChoice, NestingChoice, question_for_nesting,
    question_for_unreadable_folder)

ENGINE_WORDS = ("warning", "would create", "records no values",
                "library carries", "kind-of-file word", "no model has judged",
                "file(s)", "unresolved")


@pytest.fixture()
def lib(tmp_path):
    root = tmp_path / "Desktop"
    course = root / "School" / "AP"
    course.mkdir(parents=True)
    for name in ("AP world notes.txt", "stroke paper.txt", "essay draft.txt"):
        (course / name).write_text("words", encoding="utf-8")
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.commit()
    yield conn
    conn.close()


def _text(event) -> str:
    return " ".join([event.text, event.why, event.changes,
                     *(o.label for o in event.options)])


def _nesting():
    warn = ("2 of this level's children hold 1 file(s) or fewer",)
    return question_for_nesting(
        branch_label="Education", file_count=5, choices=(
            NestingChoice(("term",), "This option would create 2 term. 3 "
                          "file(s) would stay unresolved and visible.",
                          (("Education/Fall2024", 1),
                           ("Education/Spring2020", 1)), warn),
            NestingChoice(("subject",), "This option would create 2 subject.",
                          (("Education/APMA E2000", 1),
                           ("Education/Python-1006", 1)), warn),
            NestingChoice(("subject", "term"), "This option would create 2 "
                          "subject.", (("Education/APMA E2000", 1),
                                       ("Education/Python-1006", 1)), warn)))


def test_a_shape_question_drops_engine_sentences_and_duplicate_options():
    event = question_event(_nesting(), 1, 1)
    text = _text(event)
    assert not any(w in text for w in ENGINE_WORDS), text
    labels = [o.label for o in event.options]
    assert labels == ["Fall2024, Spring2020",
                      "APMA E2000, Python-1006"]
    assert event.options[1].id == "subject"        # the first id is kept
    assert "Education" in event.text and "5 files" in event.text


def test_an_option_with_no_subfolders_says_so_plainly():
    q = question_for_nesting(branch_label="Photos and Media", file_count=8,
                             choices=(
        NestingChoice(("a",), "This option would create no child branches. "
                      "8 file(s) would stay unresolved and visible.", (), ()),
        NestingChoice(("b",), "This option would create no child branches. "
                      "8 file(s) would stay unresolved and visible.", (), ())))
    event = question_event(q, 1, 1)
    assert [o.label for o in event.options] == [
        "No subfolders: all of them go straight into Photos and Media"]
    assert not any(w in _text(event) for w in ENGINE_WORDS)


def test_a_folder_question_names_the_folder_files_and_count(lib):
    q = question_for_unreadable_folder(
        folder="School/AP", file_count=3, protected_count=0,
        choices=(DestinationChoice("n1", "98 Review and Unsorted"),
                 DestinationChoice("n2", "Archive")))
    event = question_event(q, 1, 1, lib)
    assert "School/AP" in event.text and "3 files" in event.text
    assert any(n in event.text for n in ("AP world notes.txt",
                                         "stroke paper.txt"))
    assert [o.label for o in event.options] == ["Review and Unsorted",
                                                "Archive"]
    assert event.options[0].id == "98 Review and Unsorted"


def test_ordering_numbers_are_display_only():
    assert display_name("98 Review and Unsorted/Review Later") == (
        "Review and Unsorted/Review Later")
    assert display_name("4 AUG 2023 Stroke paper") == "4 AUG 2023 Stroke paper"
    assert display_name("2024-RCC form") == "2024-RCC form"


def _record(conn, *qs):
    from questions.schema import create_questions_schema
    from questions.store import record_question
    create_questions_schema(conn)
    for q in qs:
        record_question(conn, q, asked_at="2026-10-04T00:00:00+00:00")
    conn.commit()


def test_a_question_naming_no_file_is_not_asked_but_counted(lib):
    from assistant.engine_tools import askable_questions, open_questions
    nameless = question_for_unreadable_folder(
        folder="School", file_count=2, protected_count=0,
        choices=(DestinationChoice("n1", "Archive"),
                 DestinationChoice("n2", "Other")))
    named = question_for_unreadable_folder(
        folder="School/AP", file_count=3, protected_count=0,
        choices=(DestinationChoice("n1", "Archive"),
                 DestinationChoice("n2", "Other")))
    _record(lib, nameless, named)
    asked, skipped = askable_questions(lib)
    assert [q.question_id for q in asked] == [named.question_id]
    assert skipped["unnamed_files"] == 2
    assert open_questions(lib) == asked


def test_a_question_inside_a_set_aside_project_is_skipped(lib, monkeypatch):
    from pathlib import Path
    from assistant import organize_tools
    from assistant.engine_tools import askable_questions
    root = Path(lib.execute("SELECT sources FROM corpus_selections"
                            ).fetchone()[0].strip('[]"'))
    monkeypatch.setattr(organize_tools, "_set_aside_folders",
                        lambda c: [root / "School"])
    _record(lib, question_for_unreadable_folder(
        folder="School/AP", file_count=3, protected_count=0,
        choices=(DestinationChoice("n1", "Archive"),
                 DestinationChoice("n2", "Other"))))
    asked, skipped = askable_questions(lib)
    assert asked == () and skipped["inside_projects"] == 1


@pytest.mark.parametrize("said", [
    "APMA E2000, Python-1006", "2", "option 2"])
def test_an_answer_in_the_words_shown_selects_that_option(lib, said):
    # Judge 2's model answered with the label it had been shown; it matched
    # no raw label, was saved as free text, and the shape was never built.
    from types import SimpleNamespace
    from assistant.engine_tools import run
    from questions.schema import create_questions_schema
    from questions.store import record_question

    create_questions_schema(lib)
    q = _nesting()
    record_question(lib, q, asked_at="2026-10-04T00:00:00+00:00")
    lib.commit()
    result = run(lib, "answer_question", {"answer": said},
                 context=SimpleNamespace(question_queue=[q], asking=None))
    assert result["recorded"] == "choice"
    row = lib.execute("SELECT option_id FROM structural_answers").fetchone()
    assert row[0] == "subject"
