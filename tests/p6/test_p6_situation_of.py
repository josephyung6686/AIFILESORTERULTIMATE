"""`00` amendment 5 of 15 Sep: "the person corrects it in one structure edit".

The reader existed and nothing wrote to it. `record_the_situation` skips a
`USER_CONFIRMED` row rather than superseding it (`llm_seam.py`, "THE PERSON'S OWN
ANSWER IS NOT OVERRULED BY A RE-RUN"), so a person's word about one file's
situation would outlive every re-run -- if anything could put one there.
`--confirm` cannot: it needs a standing row at that value (`confirm_claim`), and
the judge's alternative lands on `situation_alternative`, which the partition
does not read.

`104` §18.110 is why this is built first: a protected record is shown to no
model, ever, and is filed by the person one at a time. This writer is the
person's word about what such a file IS, and the store keeps it against the
file and the value, so a re-run, a re-shaped tree or a library update cannot
lose it.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from facts.file_facts import USER_CORRECTION
from facts.learning import assert_situation
from facts.llm_seam import SITUATION_FIELD, record_the_situation
from facts.states import USER_CONFIRMED
from facts.supersede import preferred_fact

# `p6_conn` is `tests/p6/conftest.py`'s; `subject_file` is the llm-seam suite's
# own one-file, one-observation fixture, imported by name the way the
# integration suite imports `dark_level_stage`.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_p6_llm_seam import subject_file  # noqa: E402,F401

T0 = "2026-09-17T00:00:00Z"


def _value_of(conn, row):
    return conn.execute('select canonical_value from "values" where value_id = ?',
                        (row["value_id"],)).fetchone()[0]


def test_the_persons_situation_is_written_user_confirmed_and_preferred(
        p6_conn, subject_file):
    file_id, content_hash, key = subject_file
    record_the_situation(p6_conn, file_id=file_id, content_hash=content_hash,
                         situation="academic.coursework", alternatives=(),
                         evidence_refs=(key,), cache_key="call_1")
    assert_situation(p6_conn, file_id=file_id, content_hash=content_hash,
                     situation="academic.teaching", user_id="t", observed_at=T0)
    row = preferred_fact(p6_conn, file_id=file_id, field_key=SITUATION_FIELD)
    assert row["reliability_state"] == USER_CONFIRMED
    assert row["origin"] == USER_CORRECTION
    assert _value_of(p6_conn, row) == "academic.teaching"


def test_a_file_the_judge_never_named_takes_the_persons_word(p6_conn, subject_file):
    """THE PROTECTED CASE (`104` §18.110): no model row exists for the file and
    none ever will. `confirm_claim` would refuse for want of a standing row; this
    writer is the one that does not need one."""
    file_id, content_hash, _key = subject_file
    assert preferred_fact(p6_conn, file_id=file_id, field_key=SITUATION_FIELD) is None
    assert_situation(p6_conn, file_id=file_id, content_hash=content_hash,
                     situation="career.employment-records", user_id="t",
                     observed_at=T0)
    row = preferred_fact(p6_conn, file_id=file_id, field_key=SITUATION_FIELD)
    assert row is not None and row["reliability_state"] == USER_CONFIRMED
    assert _value_of(p6_conn, row) == "career.employment-records"


def test_a_re_run_does_not_take_the_persons_situation_back(p6_conn, subject_file):
    """SABOTAGE: write the person's row `llm_supported` instead of
    `user_confirmed` -- the next `record_the_situation` supersedes it as it
    supersedes any model row, and the person's correction lasts one run."""
    file_id, content_hash, key = subject_file
    assert_situation(p6_conn, file_id=file_id, content_hash=content_hash,
                     situation="academic.teaching", user_id="t", observed_at=T0)
    record_the_situation(p6_conn, file_id=file_id, content_hash=content_hash,
                         situation="academic.coursework", alternatives=(),
                         evidence_refs=(key,), cache_key="call_2")
    row = preferred_fact(p6_conn, file_id=file_id, field_key=SITUATION_FIELD)
    assert _value_of(p6_conn, row) == "academic.teaching"


def test_saying_it_again_is_the_same_word_not_a_second_one(p6_conn, subject_file):
    file_id, content_hash, _key = subject_file
    first = assert_situation(p6_conn, file_id=file_id, content_hash=content_hash,
                             situation="academic.teaching", user_id="t",
                             observed_at=T0)
    again = assert_situation(p6_conn, file_id=file_id, content_hash=content_hash,
                             situation="academic.teaching", user_id="t",
                             observed_at="2026-09-17T00:00:01Z")
    assert first == again


def test_changing_their_mind_retires_the_earlier_word_and_the_slot_still_reads(
        p6_conn, subject_file):
    """THE TRACE THAT BROKE THE FIRST DRAFT OF THIS WRITER. Run 1: the person says
    X (U1). Run 2: the judge writes M beside it and leaves U1 alone. Run 3: the
    person says Y. If the writer retired M and left U1, the slot holds two live
    `user_confirmed` rows with two values, `preferred_of_slot` finds no pointer,
    and the person's own correction makes the file's situation unreadable.
    SABOTAGE: skip `user_confirmed` rows in the retirement loop -- `preferred_fact`
    below answers `None`."""
    file_id, content_hash, key = subject_file
    first = assert_situation(p6_conn, file_id=file_id, content_hash=content_hash,
                             situation="academic.teaching", user_id="t",
                             observed_at=T0)
    record_the_situation(p6_conn, file_id=file_id, content_hash=content_hash,
                         situation="academic.coursework", alternatives=(),
                         evidence_refs=(key,), cache_key="call_3")
    second = assert_situation(p6_conn, file_id=file_id, content_hash=content_hash,
                              situation="academic.k12", user_id="t",
                              observed_at="2026-09-17T00:00:02Z")
    row = preferred_fact(p6_conn, file_id=file_id, field_key=SITUATION_FIELD)
    assert row is not None and row["fact_id"] == second
    old = p6_conn.execute("SELECT superseded_by FROM file_facts WHERE fact_id = ?",
                          (first,)).fetchone()
    assert old["superseded_by"] == second
