# tests/test_cli_the_judges_kinds_name_the_folder.py
"""On an untyped run the default branch's kind is the one the JUDGE named most
often, ahead of the anchor and the recogniser.

Measured on a 33-file Desktop: one resume's `work_type` anchor named `career`
over sixteen files site G named `photos`. The whole Desktop was asked "Which of
these is career?", the answer (`career.recruiting`) was promoted to the run's
own situation, and the proposal grew a top-level "Career and recruiting" beside
the life branch "Career".

`00` amendment 7 (12 Sep): the rules' top-1 was 32 %, so a file the rules
settle is still asked; `branch_situation.partition_by_branch` already reads
site G's name AHEAD of the anchor per file. The folder's vote takes the same
order: the judge, then the anchors, then the readings.
"""
from __future__ import annotations

from cli import the_kind_the_folder_names


def test_the_judges_kinds_outvote_one_anchor():
    assert the_kind_the_folder_names((
        ("judge", {"photos": 16, "career": 1}),
        ("facts", {"career": 1}),
        ("readings", {"academic": 3}),
    )) == ("photos", "judge")


def test_with_no_judgement_the_anchors_decide_as_before():
    assert the_kind_the_folder_names((
        ("judge", {}),
        ("facts", {"academic": 4}),
        ("readings", {}),
    )) == ("academic", "facts")


def test_a_tie_among_the_judges_kinds_falls_to_the_next_vote():
    assert the_kind_the_folder_names((
        ("judge", {"photos": 2, "career": 2}),
        ("facts", {"career": 1}),
    )) == ("career", "facts")


def test_nothing_named_is_none():
    assert the_kind_the_folder_names((("judge", {}), ("facts", {}))) == (None, None)
