"""§8.7: negative feedback is stored WITH the evidence that produced it.

`74` §6 B6's negative twin is
`test_a_rejection_stored_without_its_evidence_is_refused`. It is a twin in the
house sense: it goes red against a `rejections.py` that reassembles a prior
rejection from whatever the decision says TODAY instead of from the presentation
the user actually acted against, and against a `collect` that lets an action be
stored with no presentation at all.

SPEC:308-312 says what the evidence IS on a P13 record: `presented_state_ref`
plus the decision's `matching_facts[]` and `observation_key` citations. This is
what makes §7.10's worked case work -- PDFs rejected out of Receipts and
Confirmations BECAUSE THEY ARE ACTUALLY SCHOOL FORMS must route future similar
files back toward Academic or Applications review, and "because" is only in the
record if the evidence is.
"""
from __future__ import annotations

import pytest

from evidence_shape.observation import Location, Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from privacy.display import RedactionSettings

from review_surface.citations import UNRESOLVABLE
from review_surface.collect import PresentationRequired, collect
from review_surface.presentation import record_presentation
from review_surface.rejections import prior_rejections
from review_surface.store import record_action
from review_surface.vocabulary import (
    ACTION_ACCEPT,
    ACTION_REJECT,
    SURFACE_PLACEMENT,
)

T0 = "2026-08-29T00:00:00Z"
HASH_A = "a" * 64
SHOWN = RedactionSettings(names="shown", previews="shown", thumbnails="shown",
                          ocr_text="shown", location_data="shown")
REDACTED = RedactionSettings(names="redacted", previews="shown",
                             thumbnails="shown", ocr_text="redacted",
                             location_data="shown")


def _obs(conn) -> str:
    record_run(conn, ExtractionRun(
        run_id="run-1", file_id="f-1", content_hash=HASH_A,
        extractor_name="fixture-pdf", extractor_version="1",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=T0, observation_count=1,
        coverage=None, finished_at=T0, failure_reason=None))
    observation = Observation(
        file_id="f-1", content_hash=HASH_A, extractor_name="fixture-pdf",
        extractor_version="1", source_type="text_document",
        raw_value="Columbia University",
        location=Location(zone="body", container_path=(), text_span=None,
                          time_span=None, region=None),
        occurrence_count=1, observed_at=T0, reliability="direct",
        run_id="run-1", normalized_value="Columbia University",
        context_before="School form for ", context_after=".",
        context_truncated=False, confidence=None, signal_tier=None)
    record_observation(conn, observation)
    return observation.observation_key


def _reject(conn, key, *, settings=SHOWN, action_id="a-rej", acted_at=T0):
    ref = record_presentation(
        conn, surface=SURFACE_PLACEMENT, subject_ref="d1",
        plan_version="plan-1", session_id="s-1", settings=settings,
        evidence_refs=(key,), user_id="jy", component_version="p13-1",
        rendered_at=acted_at).presented_state_ref
    record_action(conn, collect(
        conn, action_id=action_id, surface=SURFACE_PLACEMENT,
        subject_ref="d1", plan_version="plan-1", session_id="s-1",
        action=ACTION_REJECT, correction_scope="node",
        presented_state_ref=ref, user_id="jy", acted_at=acted_at,
        component_version="p13-1",
        payload={"node_id": "n-receipts",
                 "reason": "these are actually school forms"}))


def test_a_rejection_stored_without_its_evidence_is_refused(p13_conn):
    """`74` §6 B6's negative twin. Two halves, and both must hold.

    First: an action cannot be collected at all without a recorded presentation,
    because a gesture with no record of what was shown carries no evidence.
    Second: the prior rejection that IS reassembled carries the evidence the user
    saw -- the keys shown and the policy they were shown under -- rather than the
    decision as it stands today. A decision superseded since the rejection would
    otherwise re-attribute the user's "no" to evidence they never saw.
    """
    with pytest.raises(PresentationRequired):
        collect(p13_conn, action_id="a-orphan", surface=SURFACE_PLACEMENT,
                subject_ref="d1", plan_version="plan-1", session_id="s-1",
                action=ACTION_REJECT, correction_scope="node",
                presented_state_ref="never-minted", user_id="jy", acted_at=T0,
                component_version="p13-1")
    key = _obs(p13_conn)
    _reject(p13_conn, key, settings=REDACTED)
    prior = prior_rejections(p13_conn, subject_ref="d1")[0]
    assert prior.citations[0].observation_key == key
    assert prior.presented_state.redaction_policy["ocr_text"] == "redacted"
    assert prior.presented_state.redaction_policy["names"] == "redacted"
    assert prior.explanation


def test_a_rejection_is_stored_with_its_resolvable_evidence(p13_conn):
    """Done-means 10, first clause."""
    key = _obs(p13_conn)
    _reject(p13_conn, key)
    priors = prior_rejections(p13_conn, subject_ref="d1")
    assert len(priors) == 1
    assert priors[0].citations[0].observation_key == key
    assert priors[0].citations[0].excerpt == "Columbia University"


def test_re_presenting_the_same_subject_shows_the_prior_rejection(p13_conn):
    """Done-means 10, second clause. The reason the user gave is in the record."""
    key = _obs(p13_conn)
    _reject(p13_conn, key)
    prior = prior_rejections(p13_conn, subject_ref="d1")[0]
    assert prior.correction_scope == "node"
    assert "school forms" in prior.explanation


def test_an_acceptance_is_not_a_rejection(p13_conn):
    key = _obs(p13_conn)
    ref = record_presentation(
        p13_conn, surface=SURFACE_PLACEMENT, subject_ref="d2",
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=(key,), user_id="jy", component_version="p13-1",
        rendered_at=T0).presented_state_ref
    record_action(p13_conn, collect(
        p13_conn, action_id="a-ok", surface=SURFACE_PLACEMENT,
        subject_ref="d2", plan_version="plan-1", session_id="s-1",
        action=ACTION_ACCEPT, correction_scope="file",
        presented_state_ref=ref, user_id="jy", acted_at=T0,
        component_version="p13-1"))
    assert prior_rejections(p13_conn, subject_ref="d2") == ()


def test_two_rejections_are_both_kept_oldest_first(p13_conn):
    """P13 owns no supersedable record: a later gesture is a later row, and the
    prior one stays inspectable."""
    key = _obs(p13_conn)
    _reject(p13_conn, key, action_id="a-1", acted_at=T0)
    _reject(p13_conn, key, action_id="a-2", acted_at="2026-08-29T00:05:00Z")
    priors = prior_rejections(p13_conn, subject_ref="d1")
    assert [p.action_id for p in priors] == ["a-1", "a-2"]


def test_a_rejection_whose_evidence_no_longer_resolves_still_shows_the_failure(
        p13_conn):
    """M14 again: the negative example survives an extractor upgrade AS a record,
    and a broken citation is visible rather than a shorter list."""
    _reject(p13_conn, "obs-key-gone")
    prior = prior_rejections(p13_conn, subject_ref="d1")[0]
    assert prior.citations[0].state == UNRESOLVABLE
