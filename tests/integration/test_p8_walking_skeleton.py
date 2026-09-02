"""P8 repair R5: one connected P7 -> P8 -> P6 -> P2 walk, driven by `run_call`.

The old skeleton hand-assembled the middle of the path: it called `Gate.release`
itself, built a `Dossier` literal, called `issue` itself, validated with a
permissive site callback, and then called `validate_fact_proposal` a second time
so a P6 fact would exist. Every step was real, and the *composition* was the
test's, not P8's -- so the thing the skeleton was supposed to prove was the one
thing it did not exercise.

This walk calls `run_call` once. Everything between the request and the P6 fact
is P8's own composition:

    Gate.release -> canonical dossier -> transport.issue -> site dispatcher
    -> P6 consequence -> P2 stage output
"""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal

import pytest

import test_p8_p6_fact_seam as seam
import test_p8_p7_egress as egress
from eval_harness.run import VERSION_TUPLE_FIELDS, get_version_tuple, start_run
from eval_harness.stage_output import stage_outputs
from eval_harness.store import create_eval_schema
from facts.fields import create_fields
from facts.file_facts import LLM_INTERPRETATION, facts_for_file
from facts.llm_seam import build_request
from facts.schema import create_facts_schema
from facts.states import LLM_SUPPORTED
from llm_harness.authorship import (
    MODEL_CALL_ISSUED,
    MODEL_RESPONSE_RECEIVED,
    VALIDATION_VERDICT,
)
from llm_harness.budgets import ScanBudget, create_budget_schema
from llm_harness.dossier import canonical_dossier_bytes
from llm_harness.fact_validation import FactValidationDependencies
from llm_harness.harness import CallDependencies, run_call
from llm_harness.records import DossierRequest, EvidenceItem, P8Verdict
from llm_harness.sites import FactSiteDependencies, SiteDependencies
from llm_harness.stage_output import (
    emit_stage_output,
    record_p8_version_tuple,
    replay_recorded_response,
)
from llm_harness.vocabulary import (
    A_FACT,
    ACCEPT_DIRECT,
    DIRECT_ANCHOR,
    REDUCTION_NONE,
    REMAINS_AMBIGUOUS,
)
from p8.test_p8_transport import Recorder, _spent
from llm_harness.records import Refusal
from privacy.release import NeedsConsent
from llm_harness.fixtures import FIXTURE_HANDLE_KEY

RAW_EXCERPT = "Columbia University"
#: What P7 actually releases: the egress fixture redacts every classified
#: value, so the model is shown this and may cite nothing else (R4).
RELEASED_VALUE = "[redacted]"
SKELETON_TEXT = "Columbia University - redacted dossier excerpt for the applicant."
CONTENT_HASH = "hash-skeleton"
OBSERVED_AT = "2026-08-22T09:00:00Z"


def _direct_bytes(key: str, *, span: str = RELEASED_VALUE) -> bytes:
    return json.dumps({
        "claims": [{
            "claim_ref": "c1",
            "payload": {"field": "subject", "value": RAW_EXCERPT},
            "citations": [{
                "evidence_ref": key,
                "cited_span": span,
                "why_it_supports": "names the school",
            }],
        }],
    }, separators=(",", ":")).encode("utf-8")


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
    create_budget_schema(conn)
    return conn


@pytest.fixture()
def walk(skeleton_conn, monkeypatch):
    """Everything `run_call` needs, and nothing it should have to build itself."""
    monkeypatch.setattr(egress, "TEXT", SKELETON_TEXT)
    monkeypatch.setattr(egress, "SPAN", egress.TextSpan(start=0, end=19))
    conn = skeleton_conn
    file_id, key = egress._seed_classified(
        conn, name="syllabus.pdf", content_hash=CONTENT_HASH,
    )
    policy = egress._store_policy(conn, "hybrid")
    prompt = egress._prompt()
    fingerprint = egress.prompt_fingerprint(prompt)
    request = DossierRequest(
        call_site=A_FACT,
        subject_ref=file_id,
        eligibility_reason=REMAINS_AMBIGUOUS,
        evidence_items=(
            EvidenceItem(
                evidence_ref=key, kind="excerpt", location="heading",
                excerpt_span=(egress.SPAN.start, egress.SPAN.end),
                reliability_state="direct", basis=DIRECT_ANCHOR,
            ),
        ),
        conflicts=(),
        model_call_request=egress._request(
            items=(egress.Excerpt(
                observation_key=key, span=egress.SPAN, reason="heading",
            ),),
            model_target=egress.CLOUD, file_ids=(file_id,),
            fingerprint=fingerprint,
        ),
        plan_version=None,
        evidence_snapshot_id="snap-skeleton",
    )
    digest = hashlib.sha256(CONTENT_HASH.encode()).hexdigest()
    dependencies = CallDependencies(
        proposal_class="fixture-class",
        basis_key=json.dumps({"file_id": file_id, "field_key": "subject"}),
        learning_scope="file",
        learning_subject_id=file_id,
        evidence_resolver=lambda observation_key: (
            SKELETON_TEXT if observation_key == key else None
        ),
        site_dependencies=SiteDependencies(
            fact=FactSiteDependencies(
                fact_request=build_request(
                    conn, file_id=file_id, content_hash=digest,
                    activation_signals=seam._signals("academic"),
                    normalizers={"subject": str.strip},
                ),
                fact_dependencies=FactValidationDependencies(
                    normalize=seam._fixture_normalize,
                    contradicts=seam._fixture_contradicts,
                ),
            ),
            placement=None, residual=None, template=None,
        ),
        contradicts=lambda *_a, **_k: False,
        unreduced_fits=True,
        summarized_fits=False,
        anchors_fit=False,
        split_shard_fits=(),
        split_shards=(),
        scan_budget=ScanBudget(
            scan_id="scan-skeleton", corpus_file_count=1000,
            max_calls_per_1000_files=1, max_estimated_cost=Decimal("10"),
            min_calls_per_scan=0,
        ),
        estimated_cost=Decimal("1"),
        actual_cost=Decimal("1"),
        allowed_vocabulary=("subject",),
        policy_version=policy.policy_version, wire_handle_key=FIXTURE_HANDLE_KEY,
    )
    return conn, file_id, key, digest, prompt, fingerprint, policy, request, dependencies


def _p8_events(conn) -> list[str]:
    return [
        row["event_type"]
        for row in conn.execute(
            "SELECT event_type FROM events WHERE subsystem = 'P8' ORDER BY event_id"
        )
    ]


def _run(conn, request, dependencies, *, prompt, reply):
    recorder = Recorder(reply=reply)
    result = run_call(
        conn, request,
        gate=egress._gate(conn),
        model_client=egress.ModelClient(
            model_target=egress.CLOUD, invoke=recorder,
        ),
        prompt=prompt,
        validation_dependencies=dependencies,
        observed_at=lambda: OBSERVED_AT,
    )
    return result, recorder


def test_one_run_call_walks_p7_to_p8_to_p6_to_p2(walk):
    conn, file_id, key, digest, prompt, fingerprint, policy, request, deps = walk
    before = conn.execute("SELECT count(*) AS c FROM events").fetchone()["c"]

    verdict, recorder = _run(
        conn, request, deps, prompt=prompt, reply=_direct_bytes(key),
    )

    # P8's own composition produced a verdict, and the model was called once.
    assert isinstance(verdict, P8Verdict)
    assert verdict.outcome == ACCEPT_DIRECT, verdict.reasons
    assert len(recorder.calls) == 1

    # The dossier is addressed by content and is what the model saw. The release
    # that paid for this call is on the call's own row, not on the content.
    row = conn.execute(
        "SELECT dossier_id, payload FROM llm_dossier"
    ).fetchone()
    release_id = conn.execute(
        "SELECT release_id FROM llm_response WHERE dossier_id = ?",
        (row["dossier_id"],),
    ).fetchone()["release_id"]
    assert row["dossier_id"] != release_id
    assert verdict.dossier_id == row["dossier_id"]
    # R4 end to end: the model was shown P7's redacted value, and only that.
    assert RELEASED_VALUE.encode("utf-8") in recorder.calls[0]
    assert RAW_EXCERPT.encode("utf-8") not in recorder.calls[0]
    assert SKELETON_TEXT.encode("utf-8") not in recorder.calls[0]
    assert release_id.encode("utf-8") not in recorder.calls[0]

    # P7's release was spent exactly once, by P8's transport.
    assert _spent(conn, release_id) is not None

    # P6 holds the consequence. `run_call` reached it through the dispatcher.
    facts = [
        fact for fact in facts_for_file(conn, file_id, digest)
        if fact["field_key"] == "subject"
    ]
    assert len(facts) == 1
    assert facts[0]["reliability_state"] == LLM_SUPPORTED
    assert facts[0]["origin"] == LLM_INTERPRETATION
    assert facts[0]["prompt_fingerprint"] == fingerprint

    events = _p8_events(conn)
    assert MODEL_CALL_ISSUED in events
    assert MODEL_RESPONSE_RECEIVED in events
    assert VALIDATION_VERDICT in events
    assert conn.execute("SELECT count(*) AS c FROM events").fetchone()["c"] > before

    # P2 receives the verdict in its own envelope.
    axes = {name: None for name in VERSION_TUPLE_FIELDS}
    axes["extractor_versions"] = {}
    axes["prompt_fingerprint"] = fingerprint
    axes["model_identifier"] = egress.CLOUD.model_id
    axes["analysis_tiers_enabled"] = ["llm"]
    ref = record_p8_version_tuple(conn, **axes)
    run_id = start_run(
        conn, bundle_id="bundle-skeleton", run_kind="replay",
        version_tuple_ref=ref, budget_ceilings={},
        run_settings={"model_enabled": True, "embeddings_enabled": False},
        pinned_plan_id="plan-fixture", pinned_plan_version="1",
    )
    emit_stage_output(
        conn, run_id=run_id, subject_ref=file_id,
        result=verdict, inputs=(key,), version_tuple_ref=ref,
    )
    stage_row = stage_outputs(conn, run_id, stage_id="llm_interpretation")[0]
    assert stage_row["outcome"] == "produced"
    assert stage_row["budget_state"] == "within_ceiling"
    assert "validator_version" in stage_row["payload"]
    assert policy.policy_version in stage_row["payload"]
    stored = get_version_tuple(conn, ref)
    assert stored["prompt_fingerprint"] == fingerprint
    assert "validator_version" not in VERSION_TUPLE_FIELDS
    assert "policy_version" not in VERSION_TUPLE_FIELDS


def test_replay_of_the_walk_uses_the_same_dispatcher_and_calls_no_model(walk):
    conn, file_id, key, digest, prompt, fingerprint, policy, request, deps = walk
    live, _recorder = _run(
        conn, request, deps, prompt=prompt, reply=_direct_bytes(key),
    )
    assert isinstance(live, P8Verdict)

    dossier_id = conn.execute("SELECT dossier_id FROM llm_dossier").fetchone()[0]

    # Rebuild the exact dossier from a SECOND release of the same content. A
    # different release id must not be a different dossier: the address is the
    # content's, so replay can find the response the first call stored.
    from llm_harness.dossier import build_dossier

    released = egress._gate(conn).release(request.model_call_request)
    dossier = build_dossier(
        request, released, reduction_rung=REDUCTION_NONE,
        allowed_vocabulary=("subject",), prompt=prompt, handle_key=FIXTURE_HANDLE_KEY,
    )
    assert released.release_id != dossier_id
    assert dossier.dossier_id == dossier_id, (
        "a second release of identical content produced a different address"
    )
    assert canonical_dossier_bytes(dossier, prompt, handle_key=FIXTURE_HANDLE_KEY)

    replayed, report = replay_recorded_response(
        conn, dossier,
        evidence_resolver=deps.evidence_resolver,
        site_dependencies=deps.site_dependencies,
        contradicts=deps.contradicts,
        dossier_builder="p8-skeleton",
        policy_version=policy.policy_version, handle_key=FIXTURE_HANDLE_KEY,
    )
    assert replayed[0].outcome == live.outcome
    assert report.citations_span_matched == 1


def test_the_walk_fails_closed_when_the_gate_denies(walk, monkeypatch):
    conn, file_id, key, digest, prompt, fingerprint, policy, request, deps = walk
    # An unclassified file. A classification is superseded, never removed, so the
    # denial is staged with a second file rather than by deleting the first one's.
    other_id = egress._file(conn, "unclassified.pdf", "hash-unclassified")
    other_key = egress._evidence(conn, other_id, "hash-unclassified")
    import dataclasses

    denied_request = dataclasses.replace(
        request,
        subject_ref=other_id,
        evidence_items=(dataclasses.replace(
            request.evidence_items[0], evidence_ref=other_key,
        ),),
        model_call_request=egress._request(
            items=(egress.Excerpt(
                observation_key=other_key, span=egress.SPAN, reason="heading",
            ),),
            model_target=egress.CLOUD, file_ids=(other_id,),
            fingerprint=fingerprint,
        ),
    )
    result, recorder = _run(
        conn, denied_request,
        dataclasses.replace(deps, learning_subject_id=other_id),
        prompt=prompt, reply=_direct_bytes(other_key),
    )
    assert isinstance(result, Refusal)
    assert recorder.calls == []
    assert conn.execute("SELECT count(*) AS c FROM llm_verdict").fetchone()["c"] == 0
    assert [
        fact for fact in facts_for_file(conn, file_id, digest)
        if fact["field_key"] == "subject"
    ] == []


def test_the_walk_returns_needs_consent_unchanged_and_writes_nothing(walk):
    conn, file_id, key, digest, prompt, fingerprint, policy, request, deps = walk
    egress._store_policy(conn, "offline")
    result, recorder = _run(
        conn, request, deps, prompt=prompt, reply=_direct_bytes(key),
    )
    assert isinstance(result, (NeedsConsent, Refusal))
    assert recorder.calls == []
    assert conn.execute("SELECT count(*) AS c FROM llm_verdict").fetchone()["c"] == 0
