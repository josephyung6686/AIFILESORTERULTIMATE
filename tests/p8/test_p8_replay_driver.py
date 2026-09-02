# tests/p8/test_p8_replay_driver.py
"""P8 driven by P2's replay driver, end to end and without a model call.

Every test here runs the real chain: `evaluate_bundle` -> `replay_bundle` ->
P8's `replay_stage_adapter` -> `replay_recorded_response` -> `dispatch` ->
Site A's real `FactRequest` -> `record_stage_output` -> `assert_run` ->
`verdict_for`. Nothing is stubbed between the driver and the verdict, so a
reference chain between the two cannot pass for a working seam.
"""
from __future__ import annotations

import pytest

from eval_harness.assertions import assertions
from eval_harness.bundle import add_expectation, open_bundle, seal_bundle
from eval_harness.driver import evaluate_bundle
from eval_harness.stage_output import dimension_values, stage_outputs
from eval_harness.store import create_eval_schema
from evidence_shape.schema import create_evidence_schema
from llm_harness.records import EvidenceItem
from llm_harness.schema import create_llm_schema
from llm_harness.stage_output import DIMENSION, RecordedCall, replay_stage_adapter
from llm_harness.store import record_dossier, record_response
from llm_harness.vocabulary import ACCEPT_DIRECT, DIRECT_ANCHOR

from database_agent.db import create_schema
from p8.conftest import (
    FIXED_CLOCK,
    RELEASED_MATERIAL,
    empty_site_dependencies,
    make_dossier,
    make_fact_bundle,
    make_released_evidence,
    record_subject,
)
from llm_harness.fixtures import FIXTURE_HANDLE_KEY

MODEL_ID = "fixture-model"
PROMPT_FP = "fp-p8-driver"

#: A stored response citing one real P4 observation key.
DIRECT_BYTES = (
    b'{"claims":[{"claim_ref":"c1","payload":{"field":"school","value":"Columbia"},'
    b'"citations":[{"evidence_ref":"KEY","cited_span":"Columbia University",'
    b'"why_it_supports":"names the school"}]}]}'
)

#: The grounding value P8 publishes for a call whose one citation held.
ONE_CITATION_HELD = {
    "outcome": ACCEPT_DIRECT, "citations_checked": 1,
    "citations_resolved": 1, "citations_span_matched": 1,
}


def _bytes_citing(key: str) -> bytes:
    return DIRECT_BYTES.replace(b"KEY", key.encode("ascii"))


def _tuple():
    return dict(
        extractor_versions={}, graph_algorithm_version=None,
        prompt_fingerprint=PROMPT_FP, model_identifier=MODEL_ID,
        template_library_version=None, placement_scorer_version=None,
        analysis_tiers_enabled=["llm"],
    )


def _resolver(released, key):
    def resolve(observation_key: str):
        return released if observation_key == key else None
    return resolve


def _never_contradicts(*_a, **_k):
    return False


def _dossier(key, *, dossier_id="dossier-1", subject_ref="file-1"):
    return make_dossier(
        dossier_id=dossier_id,
        subject_ref=subject_ref,
        evidence_items=(EvidenceItem(
            evidence_ref=key, kind="excerpt", location="body",
            excerpt_span=(0, len(RELEASED_MATERIAL)),
            reliability_state="direct", basis=DIRECT_ANCHOR),),
        released_evidence=(make_released_evidence(
            observation_key=key, address=f"0:{len(RELEASED_MATERIAL)}",
            value=RELEASED_MATERIAL),),
    )


@pytest.fixture()
def driver_conn(conn):
    from facts.fields import create_fields

    create_schema(conn)
    create_evidence_schema(conn)
    create_llm_schema(conn)
    create_eval_schema(conn)
    create_fields(conn)
    return conn


def _sealed_bundle(conn, expectations):
    bundle_id = open_bundle(
        conn, corpus_form="snapshot", source_scan_ref="scan-driver",
        pinned_plan_id="plan-fixture", pinned_plan_version="1", policy_settings={})
    for subject_ref, expected_value, kind in expectations:
        add_expectation(conn, bundle_id, dimension=DIMENSION,
                        subject_ref=subject_ref, expected_value=expected_value,
                        expected_outcome_kind=kind, source="hand-labelled")
    seal_bundle(conn, bundle_id)
    return bundle_id


def _drive(conn, bundle_id, calls):
    return evaluate_bundle(
        conn, bundle_id, version_tuple=_tuple(), budget_ceilings={},
        run_settings={"model_enabled": False, "embeddings_enabled": False},
        adapters={"llm_interpretation": replay_stage_adapter(
            calls, dossier_builder="fixture", policy_version="policy-1", handle_key=FIXTURE_HANDLE_KEY)},
    )


def _recorded(conn, subject, *, dossier_id="dossier-1", subject_ref=None,
              released=RELEASED_MATERIAL, site_dependencies=None):
    file_id, _content_hash, key = subject
    dossier = _dossier(key, dossier_id=dossier_id,
                       subject_ref=subject_ref or file_id)
    record_dossier(conn, dossier, observed_at=FIXED_CLOCK)
    record_response(
        conn, dossier_id=dossier.dossier_id, response_bytes=_bytes_citing(key),
        model_id=MODEL_ID, prompt_fingerprint=PROMPT_FP, release_audit_id=17,
        release_id="release-fixture", observed_at=FIXED_CLOCK)
    return RecordedCall(
        dossier=dossier,
        subject_ref=dossier.subject_ref,
        inputs=(key,),
        evidence_resolver=_resolver(released, key),
        site_dependencies=(make_fact_bundle(conn, subject)
                           if site_dependencies is None else site_dependencies),
        contradicts=_never_contradicts,
    )


def test_the_driver_scores_a_recorded_p8_call_without_calling_a_model(
        driver_conn, tmp_path):
    """The whole point: P2's judgement reached from a live composition rather
    than assembled inside a test."""
    subject = record_subject(driver_conn, tmp_path)
    call = _recorded(driver_conn, subject)
    bundle_id = _sealed_bundle(
        driver_conn, [(call.subject_ref, ONE_CITATION_HELD, "produced")])

    driven = _drive(driver_conn, bundle_id, [call])

    assert driven.assertions_written == 1
    assert driven.verdicts == {"match": 1}
    assert driven.attribution == {}
    row = stage_outputs(driver_conn, driven.run_id,
                        stage_id="llm_interpretation")[0]
    assert row["outcome"] == "produced"
    assert row["inputs"] == f'["{subject[2]}"]'


def test_the_same_recorded_bytes_diverge_when_the_citation_stops_resolving(
        driver_conn, tmp_path):
    """The negative twin of the run above, and the reason a replay exists at all.

    Same bundle, same expectation, same stored bytes, same P6 authority. Only
    the evidence store has moved: the observation the response cited no longer
    resolves. A driver that returned the stored verdict, or that failed to
    re-validate, would still report `match`.
    """
    subject = record_subject(driver_conn, tmp_path)
    call = _recorded(driver_conn, subject, released=None)
    bundle_id = _sealed_bundle(
        driver_conn, [(call.subject_ref, ONE_CITATION_HELD, "produced")])

    driven = _drive(driver_conn, bundle_id, [call])

    assert driven.verdicts == {"divergent": 1}
    assert driven.attributed == 1
    assert driven.attribution == {"llm_interpretation": 1}
    assert assertions(driver_conn, driven.run_id)[0]["verdict"] == "divergent"


def test_an_unavailable_validator_leaves_every_other_subjects_row_standing(
        driver_conn, tmp_path):
    """The `ValidationUnavailable` fix, measured where it matters.

    Unmapped, `emit_stage_output` raised out of the adapter, and
    `replay_bundle` records an adapter exception as ONE `error` row keyed on the
    bundle id -- so the healthy subject in the same stage lost its row too, and
    `verdict_for` scores an absent row `not_run`: §8.5's word for the stage that
    did not run at all. Two subjects, one of each, in one run.
    """
    subject = record_subject(driver_conn, tmp_path)
    good = _recorded(driver_conn, subject, dossier_id="dossier-good")
    blocked = _recorded(
        driver_conn, subject, dossier_id="dossier-blocked",
        subject_ref="file-blocked", site_dependencies=empty_site_dependencies())
    bundle_id = _sealed_bundle(driver_conn, [
        (good.subject_ref, ONE_CITATION_HELD, "produced"),
        (blocked.subject_ref, ONE_CITATION_HELD, "produced"),
    ])

    driven = _drive(driver_conn, bundle_id, [good, blocked])

    outcomes = {row["subject_ref"]: row["outcome"] for row in dimension_values(
        driver_conn, driven.run_id, dimension=DIMENSION)}
    assert outcomes == {good.subject_ref: "produced", "file-blocked": "error"}
    assert driven.verdicts == {"match": 1, "unverdicted": 1}
    scored = {row["subject_ref"]: (row["verdict"], row["no_verdict_reason"])
              for row in assertions(driver_conn, driven.run_id)}
    assert scored[good.subject_ref] == ("match", None)
    assert scored["file-blocked"] == (None, "stage_error")


def test_a_subject_with_no_recorded_call_is_not_run(driver_conn, tmp_path):
    """The absent row still means what it always meant. The fix above did not
    turn `not_run` into an unreachable verdict."""
    subject = record_subject(driver_conn, tmp_path)
    call = _recorded(driver_conn, subject)
    bundle_id = _sealed_bundle(driver_conn, [
        (call.subject_ref, ONE_CITATION_HELD, "produced"),
        ("file-never-called", ONE_CITATION_HELD, "produced"),
    ])

    driven = _drive(driver_conn, bundle_id, [call])

    scored = {row["subject_ref"]: row["verdict"]
              for row in assertions(driver_conn, driven.run_id)}
    assert scored == {call.subject_ref: "match", "file-never-called": "not_run"}


def test_the_adapter_replays_a_stored_response_and_writes_no_second_p6_row(
        driver_conn, tmp_path):
    """A replay re-validates; it does not re-apply. Site A's `apply_verdict` is
    the one place P8 writes into another part's store, and `write_unresolved` is
    always an INSERT -- so a driver that applied consequences would leave P6
    saying the model had decided twice."""
    from facts.unresolved import unresolved_for_file

    file_id, content_hash, _key = subject = record_subject(driver_conn, tmp_path)
    call = _recorded(driver_conn, subject)
    bundle_id = _sealed_bundle(
        driver_conn, [(call.subject_ref, ONE_CITATION_HELD, "produced")])

    _drive(driver_conn, bundle_id, [call])
    _drive(driver_conn, bundle_id, [call])

    assert unresolved_for_file(driver_conn, file_id, content_hash) == []
    assert driver_conn.execute(
        "SELECT count(*) AS n FROM llm_verdict").fetchone()["n"] == 0


def test_a_call_that_was_never_recorded_is_loud_rather_than_measured(
        driver_conn, tmp_path):
    """The distinction the `ValidationUnavailable` mapping rests on.

    A missing `llm_response` row is not a P8 outcome -- it means the caller asked
    to replay a call nothing ever made -- so `replay_recorded_response` raises
    and P2's runner records the stage as one `error` row keyed on the BUNDLE,
    which is its deliberate treatment of a crashed adapter. That whole-stage
    collapse is correct here and was wrong for `ValidationUnavailable`, which P8
    RETURNS from ordinary paths for one subject at a time.
    """
    file_id, _content_hash, key = subject = record_subject(driver_conn, tmp_path)
    # The dossier exists; nothing ever recorded a response against it.
    dossier = _dossier(key, dossier_id="dossier-unrecorded", subject_ref=file_id)
    record_dossier(driver_conn, dossier, observed_at=FIXED_CLOCK)
    call = RecordedCall(
        dossier=dossier, subject_ref=file_id, inputs=(key,),
        evidence_resolver=_resolver(RELEASED_MATERIAL, key),
        site_dependencies=make_fact_bundle(driver_conn, subject),
        contradicts=_never_contradicts)
    bundle_id = _sealed_bundle(
        driver_conn, [(call.subject_ref, ONE_CITATION_HELD, "produced")])

    driven = _drive(driver_conn, bundle_id, [call])

    rows = stage_outputs(driver_conn, driven.run_id, stage_id="llm_interpretation")
    assert [row["outcome"] for row in rows] == ["error"]
    assert rows[0]["subject_ref"] == bundle_id
    assert "no stored response" in rows[0]["payload"]
    assert dimension_values(driver_conn, driven.run_id, dimension=DIMENSION) == []
    assert driven.verdicts == {"not_run": 1}
