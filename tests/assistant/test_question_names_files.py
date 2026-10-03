"""Every question the person sees names the files it is about.

The judge read "Which of these is?" and "548 files sit under, and nobody has
said…": the prompt's subject was a kind id, the code guard deleted it, and
nothing filled the hole.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from assistant.engine_tools import question_event, wording_problems
from database_agent.db import open_database
from items.hot_index import rebuild_fts
from items.identity import reconcile_tree
from items.schema import create_items_schema
from questions.triggers import (
    DestinationChoice, question_for_situation, question_for_unreadable_folder)

SITUATIONS = ("business_operations.market-research",
              "business_operations.risk-register")


@pytest.fixture()
def lib(tmp_path):
    root = tmp_path / "Desktop"
    course = root / "School" / "AP"
    course.mkdir(parents=True)
    for name in ("AP world notes.txt", "stroke paper.txt", "essay draft.txt"):
        (course / name).write_text("words", encoding="utf-8")
    (course / "id.pem").write_text("-----BEGIN", encoding="utf-8")
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.commit()
    yield conn
    conn.close()


def _all_text(event) -> str:
    return " ".join([event.text, event.why, event.changes,
                     *(o.label for o in event.options)])


def test_a_kind_id_subject_becomes_the_files_themselves(lib):
    q = question_for_situation(
        branch_label="business_operations", situations=SITUATIONS,
        file_count=3, unjudged_menu_of="business_operations",
        scope_label="default:business_operations")
    event = question_event(q, 1, 1, lib)
    assert "is?" not in event.text and "under," not in event.why
    assert event.text.startswith("These 3 files (e.g. ")
    assert any(name in event.text for name in
               ("AP world notes.txt", "stroke paper.txt", "essay draft.txt"))
    assert event.count == 3 and 1 <= len(event.files_preview) <= 3
    assert wording_problems(_all_text(event)) == []
    assert [o.label for o in event.options] == [
        "Market research", "Risk register"]


def test_a_folder_question_shows_example_files(lib):
    q = question_for_unreadable_folder(
        folder="School/AP", file_count=3, protected_count=0,
        choices=(DestinationChoice("n1", "School"),
                 DestinationChoice("n2", "Archive")))
    event = question_event(q, 1, 1, lib)
    assert "School/AP" in event.text
    assert event.files_preview
    assert set(event.files_preview) <= {
        "AP world notes.txt", "stroke paper.txt", "essay draft.txt"}


def test_a_protected_file_is_never_named(lib):
    for q in (question_for_unreadable_folder(
            folder="School/AP", file_count=4, protected_count=0,
            choices=(DestinationChoice("n1", "School"),
                     DestinationChoice("n2", "Archive"))),
              question_for_situation(
                  branch_label="business_operations", situations=SITUATIONS,
                  file_count=4, unjudged_menu_of="business_operations",
                  scope_label="default:business_operations")):
        event = question_event(q, 1, 1, lib)
        assert "id.pem" not in _all_text(event)
        assert "id.pem" not in event.files_preview


def test_without_a_database_a_blank_subject_still_has_a_count():
    q = question_for_situation(
        branch_label="business_operations", situations=SITUATIONS,
        file_count=548, unjudged_menu_of="business_operations",
        scope_label="default:business_operations")
    event = question_event(q, 1, 1)
    assert event.text.startswith("These 548 files")
    assert "is?" not in event.text
    assert wording_problems(_all_text(event)) == []
