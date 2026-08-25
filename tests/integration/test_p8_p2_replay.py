"""P8→P2 replay: stored response bytes re-validate without a model call."""
from __future__ import annotations

import pytest

from llm_harness.records import EvidenceItem
from llm_harness.schema import create_llm_schema
from llm_harness.stage_output import (
    emit_stage_output,
    record_p8_version_tuple,
    replay_recorded_response,
)
from llm_harness.store import record_dossier, record_response
from llm_harness.transport import ModelClient
from llm_harness.vocabulary import (
    ACCEPT_DIRECT,
    CITATION_NOT_FOUND,
    DIRECT_ANCHOR,
    REJECT,
)
from p8.conftest import FIXED_CLOCK, make_dossier, make_verdict
from privacy.release import ModelTarget

from database_agent.db import create_schema
from eval_harness.run import VERSION_TUPLE_FIELDS, get_version_tuple, start_run
from eval_harness.stage_output import stage_outputs
from eval_harness.store import create_eval_schema
from evidence_shape.schema import create_evidence_schema

DIRECT_BYTES = (
    b'{"claims":[{"claim_ref":"c1","payload":{"field":"school","value":"Columbia"},'
    b'"citations":[{"evidence_ref":"obs-key-1","cited_span":"Columbia University",'
    b'"why_it_supports":"names the school"}]}]}'
)
RELEASED_MATERIAL = "Columbia University — redacted dossier excerpt"
PROMPT_FP = "fp-p8-replay"
MODEL_ID = "fixture-model"


def _axes():
    return dict(
        extractor_versions={},
        graph_algorithm_version=None,
        prompt_fingerprint=PROMPT_FP,
        model_identifier=MODEL_ID,
        template_library_version=None,
        placement_scorer_version=None,
        analysis_tiers_enabled=["llm"],
    )


def _resolver(released: str | None):
    def resolve(observation_key: str) -> str | None:
        if observation_key == "obs-key-1":
            return released
        return None
    return resolve


def _noop_site(*_a, **_k):
    return None


def _never_contradicts(*_a, **_k):
    return False


class _Trap:
    def __init__(self):
        self.calls = []

    def __call__(self, payload: bytes) -> bytes:
        self.calls.append(payload)
        raise AssertionError("replay must not invoke ModelClient")


@pytest.fixture()
def replay_conn(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_llm_schema(conn)
    create_eval_schema(conn)
    return conn


def _dossier():
    return make_dossier(
        evidence_items=(
            EvidenceItem(
                evidence_ref="obs-key-1",
                kind="excerpt",
                location="body",
                excerpt_span=(0, 4),
                reliability_state="direct",
                basis=DIRECT_ANCHOR,
            ),
        ),
    )


def test_fixture_records_version_tuple_then_starts_run_then_emits(replay_conn):
    ref = record_p8_version_tuple(replay_conn, **_axes())
    run_id = start_run(
        replay_conn, bundle_id="bundle-replay", run_kind="replay",
        version_tuple_ref=ref, budget_ceilings={},
        run_settings={"model_enabled": False, "embeddings_enabled": False},
        pinned_plan_id="plan-fixture", pinned_plan_version="1",
    )
    output_id = emit_stage_output(
        replay_conn, run_id=run_id, subject_ref="file-1",
        result=make_verdict(), inputs=("obs-key-1",), version_tuple_ref=ref,
    )
    row = stage_outputs(replay_conn, run_id, stage_id="llm_interpretation")[0]
    assert row["stage_output_id"] == output_id
    assert row["outcome"] == "produced"
    assert row["budget_state"] == "within_ceiling"
    stored = get_version_tuple(replay_conn, ref)
    assert tuple(stored) == VERSION_TUPLE_FIELDS or set(stored) == set(VERSION_TUPLE_FIELDS)
    assert stored["prompt_fingerprint"] == PROMPT_FP
    assert stored["model_identifier"] == MODEL_ID
    assert "validator_version" not in stored
    assert "policy_version" not in stored


def test_replay_revalidates_stored_bytes_without_a_model_call(replay_conn):
    trap = _Trap()
    client = ModelClient(
        model_target=ModelTarget(locality="local", model_id=MODEL_ID, provider="fixture"),
        invoke=trap,
    )
    dossier = _dossier()
    record_dossier(replay_conn, dossier, observed_at=FIXED_CLOCK)
    record_response(
        replay_conn, dossier_id=dossier.dossier_id, response_bytes=DIRECT_BYTES,
        model_id=MODEL_ID, prompt_fingerprint=PROMPT_FP, release_audit_id=17,
        observed_at=FIXED_CLOCK,
    )
    ref = record_p8_version_tuple(replay_conn, **_axes())
    run_id = start_run(
        replay_conn, bundle_id="bundle-replay", run_kind="replay",
        version_tuple_ref=ref, budget_ceilings={},
        run_settings={"model_enabled": False, "embeddings_enabled": False},
        pinned_plan_id="plan-fixture", pinned_plan_version="1",
    )
    verdicts, report = replay_recorded_response(
        replay_conn, dossier,
        evidence_resolver=_resolver(RELEASED_MATERIAL),
        site_validator=_noop_site,
        contradicts=_never_contradicts,
        dossier_builder="fixture",
    )
    assert trap.calls == []
    assert client.invoke is trap
    assert len(verdicts) == 1
    assert verdicts[0].outcome == ACCEPT_DIRECT
    assert report.claims_accepted_direct == 1
    emit_stage_output(
        replay_conn, run_id=run_id, subject_ref=dossier.subject_ref,
        result=verdicts[0], inputs=("obs-key-1",), version_tuple_ref=ref,
    )
    row = stage_outputs(replay_conn, run_id, stage_id="llm_interpretation")[0]
    assert row["outcome"] == "produced"
    assert trap.calls == []


def test_replay_does_not_trust_cached_validation(replay_conn):
    trap = _Trap()
    ModelClient(
        model_target=ModelTarget(locality="local", model_id=MODEL_ID, provider="fixture"),
        invoke=trap,
    )
    dossier = _dossier()
    record_dossier(replay_conn, dossier, observed_at=FIXED_CLOCK)
    record_response(
        replay_conn, dossier_id=dossier.dossier_id, response_bytes=DIRECT_BYTES,
        model_id=MODEL_ID, prompt_fingerprint=PROMPT_FP, release_audit_id=17,
        observed_at=FIXED_CLOCK,
    )
    first, _ = replay_recorded_response(
        replay_conn, dossier,
        evidence_resolver=_resolver(RELEASED_MATERIAL),
        site_validator=_noop_site,
        contradicts=_never_contradicts,
        dossier_builder="fixture",
    )
    assert first[0].outcome == ACCEPT_DIRECT
    stored_outcome = replay_conn.execute(
        "SELECT outcome FROM llm_verdict WHERE dossier_id = ?",
        (dossier.dossier_id,),
    ).fetchone()
    assert stored_outcome is None
    second, report = replay_recorded_response(
        replay_conn, dossier,
        evidence_resolver=_resolver(None),
        site_validator=_noop_site,
        contradicts=_never_contradicts,
        dossier_builder="fixture",
    )
    assert trap.calls == []
    assert second[0].outcome == REJECT
    assert second[0].reasons == (CITATION_NOT_FOUND,)
    assert report.claims_rejected == 1
    assert first[0].outcome != second[0].outcome
