# tests/p9/test_p9_failure_points.py
"""P9 Task 12a — three failure stages, kept apart.

§4.8 is emphatic that a bad group can fail for three different reasons — the graph
retrieved irrelevant neighbours, the LLM overgeneralised from a good
neighbourhood, or the label was simply not useful — and that the product "must log
and evaluate these failure points separately rather than treating all mistakes as
'AI classification errors'".

So the test that matters is the one where ONE candidate fails at all three, and
three rows come back with three stages, three causes and three references. A
collapsed error class cannot tell them apart, and a team that cannot tell them
apart fixes the wrong one.

Consent is not a failure. It is a question the product has not asked yet.
"""
from __future__ import annotations

import sqlite3

import pytest

from grouping.failure_points import LOGGED_STAGES, failures_for_group, record_failure
from grouping.schema import create_grouping_schema
from grouping.vocabulary import (
    GRAPH,
    INTERPRETATION,
    LABEL,
    OutOfVocabulary,
    RETRIEVAL,
    USER,
    USER_REJECTION,
    VALIDATION,
    VALIDATOR,
)

T0 = "2026-08-27T00:00:00Z"
GROUP = "group-1"


@pytest.fixture()
def failure_conn(conn):
    create_grouping_schema(conn)
    return conn


def _record(conn, **overrides):
    values = dict(
        group_id=GROUP, stage=RETRIEVAL, cause_code="irrelevant_neighbours",
        detected_by=VALIDATOR, created_at=T0, dossier_id=None,
        membership_id=None, evidence_ref="sha256:" + "a" * 64,
    )
    values.update(overrides)
    return record_failure(conn, **values)


# --- Done-means 8: one candidate, three independent failures ---------------------


def test_one_candidate_failing_three_ways_is_three_rows(failure_conn):
    _record(failure_conn, stage=RETRIEVAL, cause_code="irrelevant_neighbours",
            evidence_ref="sha256:" + "1" * 64)
    _record(failure_conn, stage=INTERPRETATION, cause_code="overgeneralised",
            evidence_ref="verdict-7", dossier_id="dossier-1")
    _record(failure_conn, stage=LABEL, cause_code="label_not_useful",
            evidence_ref="sha256:" + "3" * 64, detected_by=USER)

    failures = failures_for_group(failure_conn, GROUP)
    assert len(failures) == 3
    assert [item.stage for item in failures] == [RETRIEVAL, INTERPRETATION, LABEL]
    assert len({item.cause_code for item in failures}) == 3
    assert len({item.evidence_ref for item in failures}) == 3


def test_the_three_stages_do_not_collapse_into_one_error_class(failure_conn):
    """The point of the stage field: a reader asking "why did this group fail"
    gets three different answers rather than one that covers all of them."""
    for stage, cause in (
        (RETRIEVAL, "irrelevant_neighbours"),
        (INTERPRETATION, "overgeneralised"),
        (LABEL, "label_not_useful"),
    ):
        _record(failure_conn, stage=stage, cause_code=cause)
    rows = list(failure_conn.execute(
        "SELECT stage, count(*) AS c FROM group_failure_points GROUP BY stage"))
    assert {row["stage"]: row["c"] for row in rows} == {
        RETRIEVAL: 1, INTERPRETATION: 1, LABEL: 1}


def test_an_interpretation_failure_carries_p8s_result_identity(failure_conn):
    """P9 does not emit the `llm_interpretation` P2 stage: that stage measures the
    model call and P8 makes it. What P9 records is a reference to P8's result."""
    _record(failure_conn, stage=INTERPRETATION, cause_code="call_failed",
            evidence_ref="verdict-7", dossier_id="dossier-1")
    failure = failures_for_group(failure_conn, GROUP)[0]
    assert failure.evidence_ref == "verdict-7"
    assert failure.dossier_id == "dossier-1"


# --- the log is append-only ------------------------------------------------------


def test_a_failure_row_is_never_updated_in_place(failure_conn):
    _record(failure_conn)
    with pytest.raises(sqlite3.IntegrityError):
        failure_conn.execute(
            "UPDATE group_failure_points SET cause_code = 'something else'")


def test_a_failure_row_is_never_deleted(failure_conn):
    _record(failure_conn)
    with pytest.raises(sqlite3.IntegrityError):
        failure_conn.execute("DELETE FROM group_failure_points")


# --- the closed stage set --------------------------------------------------------


def test_the_logged_stages_are_the_three_the_design_names():
    assert LOGGED_STAGES == (RETRIEVAL, INTERPRETATION, LABEL)


@pytest.mark.parametrize("stage", [GRAPH, VALIDATION, USER_REJECTION, "consent"])
def test_a_stage_outside_the_three_is_refused(failure_conn, stage):
    """`graph`, `validation` and `user-rejection` are in the record's vocabulary
    and have their own writers. Consent is not a failure at all: it is a question
    the product has not asked yet."""
    with pytest.raises(OutOfVocabulary):
        _record(failure_conn, stage=stage)
    assert failures_for_group(failure_conn, GROUP) == ()


def test_a_failure_names_who_detected_it(failure_conn):
    _record(failure_conn, detected_by=USER, stage=LABEL,
            cause_code="label_not_useful")
    assert failures_for_group(failure_conn, GROUP)[0].detected_by == USER
