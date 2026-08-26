"""P8 Task 12: one live P7→P8→P6→P2 walk with neighbour-fixture oracles."""
from __future__ import annotations

import json

import pytest

import test_p8_p6_fact_seam as seam
import test_p8_p7_egress as egress
from eval_harness.run import VERSION_TUPLE_FIELDS, get_version_tuple, start_run
from eval_harness.stage_output import stage_outputs
from eval_harness.store import create_eval_schema
from facts.fields import create_fields
from facts.file_facts import LLM_INTERPRETATION, facts_for_file
from facts.llm_seam import Proposal, build_request
from facts.schema import create_facts_schema
from facts.states import LLM_SUPPORTED
from llm_harness.authorship import (
    MODEL_CALL_ISSUED,
    MODEL_RESPONSE_RECEIVED,
    VALIDATION_VERDICT,
)
from llm_harness.fact_validation import (
    FactValidationDependencies,
    validate_fact_proposal,
)
from llm_harness.fingerprint import dossier_content_address
from llm_harness.records import Dossier, EvidenceItem
from llm_harness.stage_output import emit_stage_output, record_p8_version_tuple
from llm_harness.store import record_dossier, record_grounding_report, record_verdict
from llm_harness.transport import ModelClient, issue
from llm_harness.validation import validate_response
from llm_harness.vocabulary import (
    A_FACT,
    ACCEPT_DIRECT,
    DIRECT_ANCHOR,
    REDUCTION_NONE,
    REMAINS_AMBIGUOUS,
)
from p8.test_p8_transport import Recorder, _spent
from privacy.binding import ReleaseAlreadySpent
from privacy.release import Released


CITED = "Columbia University"
SKELETON_TEXT = "Columbia University — redacted dossier excerpt for the applicant."
DIRECT_BYTES = (
    b'{"claims":[{"claim_ref":"c1","payload":{"field":"subject","value":'
    b'"Columbia University"},"citations":[{"evidence_ref":"OBS",'
    b'"cited_span":"Columbia University","why_it_supports":"names the school"}]}]}'
)


@pytest.fixture()
def skeleton_conn(conn):
    egress.create_schema(conn)
    egress.create_evidence_schema(conn)
    egress.create_extraction_schema(conn)
    egress.create_privacy_schema(conn)
    egress.create_llm_schema(conn)
    create_fields(conn)
    create_facts_schema(conn)
    create_eval_schema(conn)
    return conn


def _p8_events(conn) -> list[str]:
    return [
        row["event_type"]
        for row in conn.execute(
            "SELECT event_type FROM events WHERE subsystem = 'P8' "
            "ORDER BY event_id"
        )
    ]


def test_p7_release_then_p8_validate_then_p6_fact_then_p2_envelope(skeleton_conn, monkeypatch):
    conn = skeleton_conn
    monkeypatch.setattr(egress, "TEXT", SKELETON_TEXT)
    file_id, key = egress._seed_classified(
        conn, name="syllabus.pdf", content_hash="hash-skeleton",
    )
    policy = egress._store_policy(conn, "hybrid")
    prompt = egress._prompt()
    fingerprint = egress.prompt_fingerprint(prompt)

    before = [
        row["event_id"]
        for row in conn.execute("SELECT event_id FROM events ORDER BY event_id")
    ]
    decision = egress._gate(conn).release(egress._request(
        items=(egress.Excerpt(observation_key=key, span=egress.SPAN, reason="heading"),),
        model_target=egress.CLOUD, file_ids=(file_id,),
        fingerprint=fingerprint,
    ))
    after = [
        row["event_id"]
        for row in conn.execute("SELECT event_id FROM events ORDER BY event_id")
    ]
    assert isinstance(decision, Released)
    assert len(after) > len(before)

    payload = egress._payload_from(decision, prompt)
    reply = DIRECT_BYTES.replace(b"OBS", key.encode("ascii"))
    recorder = Recorder(reply=reply)
    result = issue(
        conn, decision, payload,
        model_client=ModelClient(model_target=egress.CLOUD, invoke=recorder),
    )
    assert recorder.calls == [payload.model_visible_bytes]
    assert _spent(conn, decision.release_id) is not None
    with pytest.raises(ReleaseAlreadySpent):
        issue(
            conn, decision, payload,
            model_client=ModelClient(model_target=egress.CLOUD, invoke=recorder),
        )
    assert len(recorder.calls) == 1

    dossier = Dossier(
        dossier_id="skeleton-dossier",
        call_site=A_FACT,
        subject_ref=file_id,
        eligibility_reason=REMAINS_AMBIGUOUS,
        plan_version=None,
        policy_version=decision.policy_version,
        allowed_vocabulary=("subject",),
        evidence_items=(
            EvidenceItem(
                evidence_ref=key, kind="excerpt", location="body",
                excerpt_span=(egress.SPAN.start, egress.SPAN.end),
                reliability_state="direct", basis=DIRECT_ANCHOR,
            ),
        ),
        conflicts=(),
        max_dossier_tokens=4000,
        reduction_rung=REDUCTION_NONE,
        release_id=decision.release_id,
    )
    record_dossier(conn, dossier, observed_at=egress.OBSERVED_AT)
    checked = validate_response(
        dossier, result.response_bytes,
        evidence_resolver=lambda obs: CITED if obs == key else None,
        site_validator=lambda *_a, **_k: None,
        contradicts=lambda *_a, **_k: False,
        model_id=result.model_id,
        prompt_fingerprint=fingerprint,
        dossier_builder="p8-skeleton",
        release_audit_id=decision.audit_id,
    )
    verdicts, report = checked
    assert verdicts[0].outcome == ACCEPT_DIRECT
    record_verdict(conn, verdicts[0], model_id="fixture-model", prompt_fingerprint="fp-fixture", release_audit_id=1, observed_at=egress.OBSERVED_AT)
    record_grounding_report(conn, report, observed_at=egress.OBSERVED_AT)

    events = _p8_events(conn)
    assert MODEL_CALL_ISSUED in events
    assert MODEL_RESPONSE_RECEIVED in events
    assert VALIDATION_VERDICT in events
    issued_id = conn.execute(
        "SELECT event_id FROM events WHERE event_type = ?",
        (MODEL_CALL_ISSUED,),
    ).fetchone()["event_id"]
    assert after[len(before)] < issued_id

    import hashlib
    digest = hashlib.sha256(b"hash-skeleton").hexdigest()
    fact_request = build_request(
        conn, file_id=file_id, content_hash=digest,
        activation_signals=seam._signals("academic"),
        normalizers={"subject": str.strip},
    )
    p8 = validate_fact_proposal(
        conn, fact_request,
        Proposal(
            field_key="subject", value="Columbia University",
            citations=(key,), unknown=False,
        ),
        dependencies=FactValidationDependencies(
            normalize=seam._fixture_normalize,
            contradicts=seam._fixture_contradicts,
        ),
        model_identifier=result.model_id,
        prompt_fingerprint=fingerprint,
        policy_version=policy.policy_version,
    )
    assert p8.outcome == ACCEPT_DIRECT
    rows = [
        row for row in facts_for_file(conn, file_id, digest)
        if row["field_key"] == "subject"
    ]
    assert len(rows) == 1
    assert rows[0]["reliability_state"] == LLM_SUPPORTED
    assert rows[0]["origin"] == LLM_INTERPRETATION
    assert rows[0]["model_identifier"] == result.model_id
    assert rows[0]["prompt_fingerprint"] == fingerprint

    axes = {name: None for name in VERSION_TUPLE_FIELDS}
    axes["extractor_versions"] = {}
    axes["prompt_fingerprint"] = fingerprint
    axes["model_identifier"] = result.model_id
    axes["analysis_tiers_enabled"] = ["llm"]
    ref = record_p8_version_tuple(conn, **axes)
    stored = get_version_tuple(conn, ref)
    assert stored["prompt_fingerprint"] == fingerprint
    assert stored["model_identifier"] == result.model_id
    assert "validator_version" not in VERSION_TUPLE_FIELDS
    assert "policy_version" not in VERSION_TUPLE_FIELDS
    run_id = start_run(
        conn, bundle_id="bundle-skeleton", run_kind="replay",
        version_tuple_ref=ref, budget_ceilings={},
        run_settings={"model_enabled": True, "embeddings_enabled": False},
        pinned_plan_id="plan-fixture", pinned_plan_version="1",
    )
    emit_stage_output(
        conn, run_id=run_id, subject_ref=file_id,
        result=verdicts[0], inputs=(key,), version_tuple_ref=ref,
    )
    row = stage_outputs(conn, run_id, stage_id="llm_interpretation")[0]
    assert row["outcome"] == "produced"
    assert row["budget_state"] == "within_ceiling"
    blob = row["payload"]
    assert "validator_version" in blob
    assert policy.policy_version in blob

    released = b"\n".join(
        item.value.encode("utf-8") for item in decision.materialised_items
    )
    address = dossier_content_address(
        released,
        allowed_vocabulary=("subject",),
        allowed_schema_bytes=prompt.response_schema_bytes,
        evidence_snapshot_id="snap-a",
        release_id=decision.release_id,
        audit_id=decision.audit_id,
    )
    assert address == dossier_content_address(
        released,
        allowed_vocabulary=("subject",),
        allowed_schema_bytes=prompt.response_schema_bytes,
        evidence_snapshot_id="snap-b",
        release_id="other",
        audit_id=0,
    )
    assert address != dossier_content_address(
        released + b"x",
        allowed_vocabulary=("subject",),
        allowed_schema_bytes=prompt.response_schema_bytes,
    )
    assert conn.execute("SELECT count(*) AS c FROM llm_verdict").fetchone()["c"] == 1
    assert conn.execute(
        "SELECT count(*) AS c FROM llm_grounding_report"
    ).fetchone()["c"] == 1
    assert json.loads(rows[0]["evidence_refs"]) == [key]
