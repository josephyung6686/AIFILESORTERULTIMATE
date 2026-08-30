"""What was shown, under the policy then in force. §8.2 + §8.4 + §8.7.

`74` §6 B1's named test is
`test_presented_state_ref_records_the_redaction_policy_in_force_at_presentation`
and its negative twin is `test_a_ref_that_replays_under_a_later_policy_is_refused`.
The twin is a twin in the house sense (`tests/p10/test_p10_no_invention.py`:13-16):
it fails against a `assert_still_current` that reads the ref and not the policy,
which is the one plausible way to write this function wrongly.
"""
from __future__ import annotations

import sqlite3

import pytest

from privacy.display import DISPLAY_FACETS, RedactionSettings

from review_surface.presentation import (
    PresentationPolicyMismatch,
    assert_still_current,
    policy_of,
    presented_state,
    record_presentation,
)
from review_surface.vocabulary import (
    EVENT_PRESENTATION,
    SUBSYSTEM,
    SURFACE_PLACEMENT,
    OutOfVocabulary,
)

SHOWN = RedactionSettings(names="shown", previews="shown", thumbnails="shown",
                          ocr_text="shown", location_data="shown")
NAMES_REDACTED = RedactionSettings(
    names="redacted", previews="shown", thumbnails="shown",
    ocr_text="shown", location_data="shown")


def _record(conn, *, settings=SHOWN, refs=("obs-1",), subject="d1"):
    return record_presentation(
        conn, surface=SURFACE_PLACEMENT, subject_ref=subject,
        plan_version="plan-1", session_id="s-1", settings=settings,
        evidence_refs=refs, user_id="jy", component_version="p13-1",
        rendered_at="2026-08-29T00:00:00Z")


def test_presented_state_ref_records_the_redaction_policy_in_force_at_presentation(
        p13_conn):
    """`74` §6 B1's named test. The policy is part of the record, not context."""
    state = _record(p13_conn, settings=NAMES_REDACTED)
    stored = presented_state(p13_conn, state.presented_state_ref)
    assert stored == state
    assert tuple(stored.redaction_policy) == DISPLAY_FACETS
    assert stored.redaction_policy["names"] == "redacted"
    assert stored.redaction_policy["ocr_text"] == "shown"
    row = p13_conn.execute(
        "SELECT event_type, subsystem, user_id, explanation FROM events "
        "WHERE event_id = ?", (state.event_id,)).fetchone()
    assert row["event_type"] == EVENT_PRESENTATION
    assert row["subsystem"] == SUBSYSTEM
    assert row["user_id"] == "jy"
    assert "names" in row["explanation"] and "redacted" in row["explanation"]
    assert "obs-1" in row["explanation"]


def test_a_ref_that_replays_under_a_later_policy_is_refused(p13_conn):
    """`74` §6 B1's negative twin, and Done-means 14's second clause.

    Three halves, and the third is what makes it a twin rather than a smoke test:

    * the ref asserts clean under the policy it was minted under;
    * it is REFUSED under a later policy, naming the facet that moved;
    * a ref this database never minted is a mismatch, not a silent pass.

    An implementation that only looked the ref up would pass the first and third
    and fail the second; one that returned the row whenever it existed would pass
    the first and fail both others.
    """
    state = _record(p13_conn, settings=SHOWN)
    assert assert_still_current(
        p13_conn, state.presented_state_ref, settings=SHOWN) == state
    with pytest.raises(PresentationPolicyMismatch) as caught:
        assert_still_current(p13_conn, state.presented_state_ref,
                             settings=NAMES_REDACTED)
    assert "names" in str(caught.value)
    with pytest.raises(PresentationPolicyMismatch):
        assert_still_current(p13_conn, "never-minted", settings=SHOWN)


def test_a_presentation_is_stored_and_read_back_whole(p13_conn):
    state = _record(p13_conn)
    again = presented_state(p13_conn, state.presented_state_ref)
    assert again == state
    assert again.evidence_refs == ("obs-1",)
    assert again.surface == SURFACE_PLACEMENT


def test_a_presentation_with_no_evidence_shown_is_recorded_not_refused(p13_conn):
    """A residual card, a progress line and a protected aggregate cite nothing.

    An empty tuple is a real answer -- "nothing evidential was displayed" -- and
    refusing it would make the only surfaces that show no evidence unrecordable.
    """
    state = _record(p13_conn, refs=())
    assert presented_state(p13_conn, state.presented_state_ref).evidence_refs == ()


def test_an_unknown_ref_reads_as_none_rather_than_raising(p13_conn):
    assert presented_state(p13_conn, "never-minted") is None


def test_two_presentations_of_one_subject_under_two_policies_are_two_refs(p13_conn):
    """The ref is a claim about a policy as well as about a subject.

    If one subject under two policies minted one ref, `assert_still_current`
    could never distinguish them and Done-means 14's second clause would have no
    mechanism at all.
    """
    shown = _record(p13_conn, settings=SHOWN)
    redacted = _record(p13_conn, settings=NAMES_REDACTED)
    assert shown.presented_state_ref != redacted.presented_state_ref


def test_a_presentation_row_cannot_be_updated_or_deleted(p13_conn):
    state = _record(p13_conn)
    with pytest.raises(sqlite3.IntegrityError):
        p13_conn.execute(
            "UPDATE review_presentations SET surface = 'canvas' WHERE "
            "presented_state_ref = ?", (state.presented_state_ref,))
    with pytest.raises(sqlite3.IntegrityError):
        p13_conn.execute(
            "DELETE FROM review_presentations WHERE presented_state_ref = ?",
            (state.presented_state_ref,))


def test_an_unknown_surface_is_refused_before_anything_is_written(p13_conn):
    before = p13_conn.execute(
        "SELECT count(*) AS c FROM review_presentations").fetchone()["c"]
    with pytest.raises(OutOfVocabulary):
        record_presentation(
            p13_conn, surface="dashboard", subject_ref="d1",
            plan_version="plan-1", session_id="s-1", settings=SHOWN,
            evidence_refs=(), user_id="jy", component_version="p13-1",
            rendered_at="2026-08-29T00:00:00Z")
    assert p13_conn.execute(
        "SELECT count(*) AS c FROM review_presentations").fetchone()["c"] == before


def test_policy_of_is_a_plain_mapping_over_p7_s_facets():
    assert policy_of(NAMES_REDACTED) == {
        "names": "redacted", "previews": "shown", "thumbnails": "shown",
        "ocr_text": "shown", "location_data": "shown"}
