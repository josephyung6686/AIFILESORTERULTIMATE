"""P8 Task 9: compose Gate.release branches without collapsing consent."""
from __future__ import annotations

import ast
import inspect
import json
from decimal import Decimal
from pathlib import Path

import pytest

import llm_harness
from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from facts.domains import ActivationSignal, ActivationSignals
from facts.fields import create_fields
from facts.llm_seam import build_request
from evidence_shape.canonical import canonical_json
from evidence_shape.schema import create_evidence_schema
from llm_harness.authorship import COMPONENT_VERSION
from llm_harness.budgets import ScanBudget, create_budget_schema
from llm_harness.eligibility import Eligible
from llm_harness.fingerprint import prompt_fingerprint
from llm_harness.dossier import build_dossier, canonical_dossier_bytes
from llm_harness.harness import run_call
from llm_harness.records import (
    CallFailed,
    DossierRequest,
    P8Verdict,
    PromptDefinition,
    Refusal,
    ValidationUnavailable,
    build_call_payload,
)
from llm_harness.fact_validation import FactValidationDependencies
from llm_harness.schema import create_llm_schema
from llm_harness.sites import FactSiteDependencies, SiteDependencies
from llm_harness.transport import ModelClient
from llm_harness.vocabulary import (
    A_FACT,
    ABSTAIN,
    ACCEPT_DIRECT,
    BUDGET_EXHAUSTED,
    DEFERRED,
    PRESERVED_ANCHORS,
    PRIVACY_GATE_REFUSED,
    REDUCTION_NONE,
    REMAINS_AMBIGUOUS,
    SCHEMA_INVALID,
    SPLIT,
    SUMMARIZED_FACTS,
)
from p8.conftest import FIXED_CLOCK, make_evidence_item
from p8.test_p8_transport import Recorder
from privacy.binding import mint_release
from privacy.consent import ConsentRequirement
from privacy.denial import RemedyOption
from evidence_shape.location import TextSpan
from privacy.items import Excerpt
from privacy.policy import Policy
from privacy.redaction import RedactionManifest
from privacy.release import (
    DECISION_TYPES,
    Denied,
    ModelCallRequest,
    ModelTarget,
    NeedsConsent,
    NoPolicyInForce,
    Released,
    Target,
)
from privacy.resolve import Materialised
from privacy.schema import create_privacy_schema


SRC_HARNESS = Path(__file__).resolve().parents[2] / "src" / "llm_harness" / "harness.py"
HARNESS_ROOT = Path(__file__).resolve().parents[2] / "src" / "llm_harness"
CLOUD = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")
POLICY_VERSION = "policy-1"
PROPOSAL_CLASS = "fixture-class"
BASIS_KEY = '{"file_id":"file-1","field_key":"subject","value_id":"v-1"}'
RELEASED_MATERIAL = "Columbia University — redacted dossier excerpt"
DIRECT_BYTES = (
    b'{"claims":[{"claim_ref":"c1","payload":{"field":"school","value":"Columbia"},'
    b'"citations":[{"evidence_ref":"obs-key-1","cited_span":"Columbia University",'
    b'"why_it_supports":"names the school"}]}]}'
)


def _direct_bytes(key: str) -> bytes:
    """`DIRECT_BYTES` against a real P4 observation key."""
    return DIRECT_BYTES.replace(b"obs-key-1", key.encode("ascii"))
UNKNOWN_BYTES = (
    b'{"claims":[{"claim_ref":"c1","payload":{"field":"school"},'
    b'"unknown":{"insufficiency_statement":"no labeled school"}}]}'
)
MALFORMED_BYTES = b"{not-json"


@pytest.fixture()
def harness_conn(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_privacy_schema(conn)
    create_llm_schema(conn)
    create_budget_schema(conn)
    create_fields(conn)
    return conn


@pytest.fixture()
def subject(harness_conn, tmp_path):
    """A real P1 file with a real P4 observation, so Site A can reach P6."""
    path = tmp_path / "Syllabus.pdf"
    body = b"BUSIB 4300 Syllabus, Spring 2026"
    path.write_bytes(body)
    file_id = record_file(
        harness_conn, path, filename="Syllabus.pdf",
        normalized_filename="syllabus.pdf", extension=".pdf",
        observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(harness_conn, file_id)["content_hash"]
    record_run(harness_conn, ExtractionRun(
        run_id="r-1", file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=FIXED_CLOCK, finished_at=FIXED_CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document",
        raw_value=RELEASED_MATERIAL,
        location=Location("heading", (Segment("field", label="heading"),)),
        occurrence_count=1, observed_at=FIXED_CLOCK, reliability="possible",
        run_id="r-1", context_before="Syllabus - ")
    record_observation(harness_conn, observation)
    return file_id, content_hash, observation.observation_key


def _fact_bundle(conn, subject):
    """Site A's real authorities: P6's own FactRequest plus the C-5 oracles."""
    file_id, content_hash, _ = subject
    return SiteDependencies(
        fact=FactSiteDependencies(
            fact_request=build_request(
                conn, file_id=file_id, content_hash=content_hash,
                activation_signals=ActivationSignals(signals=(
                    ActivationSignal(schema_id="academic", activates=lambda rows: True),
                )),
                normalizers={"subject": lambda raw: raw},
            ),
            fact_dependencies=FactValidationDependencies(
                normalize=lambda field, raw: raw,
                contradicts=lambda proposal, row: False,
            ),
        ),
        placement=None, residual=None, template=None,
    )


def _prompt() -> PromptDefinition:
    return PromptDefinition(
        template_id="template.grouping",
        template_bytes=b"TEMPLATE",
        response_schema_bytes=b'{"type":"object"}',
        call_site=A_FACT,
        call_site_version="1",
        shaping_policy_bytes=b'{"policy":"authored"}',
    )


def _policy() -> Policy:
    return Policy(
        policy_version=POLICY_VERSION, operation_mode="cloud_assisted",
        consent_grants=(("Academics", "cloud_model"),),
        redaction_settings={
            "names": "redacted", "previews": "redacted", "thumbnails": "redacted",
            "ocr_text": "redacted", "location_data": "redacted",
        },
        automatic_move_permissions={}, plan_version="plan-1",
        set_at=FIXED_CLOCK,
    )


def _model_call_request(*, file_id: str = "file-1",
                        fingerprint: str | None = None,
                        key: str = "obs-key-1") -> ModelCallRequest:
    return ModelCallRequest(
        stage="grouping",
        target=Target(file_ids=(file_id,)),
        model_target=CLOUD,
        requested_items=(
            Excerpt(observation_key=key, span=TextSpan(0, 19),
                    reason="names the school"),
        ),
        prompt_template_id="template.grouping",
        prompt_fingerprint=fingerprint or "fingerprint.grouping",
        max_dossier_tokens=4000,
    )


def _request(*, file_id: str = "file-1", fingerprint: str | None = None,
             key: str = "obs-key-1") -> DossierRequest:
    return DossierRequest(
        call_site=A_FACT,
        subject_ref=file_id,
        eligibility_reason=REMAINS_AMBIGUOUS,
        evidence_items=(make_evidence_item(evidence_ref=key),),
        conflicts=(),
        model_call_request=_model_call_request(
            file_id=file_id, fingerprint=fingerprint, key=key),
        plan_version=None,
        evidence_snapshot_id="snap-1",
        budget_context="scan-1",
    )


def _denied() -> Denied:
    return Denied(
        reason="unclassified",
        explanation="no classification is stored for this file",
        remedy_options=(RemedyOption(action="classify", detail="classify first"),),
        evidence_refs=("obs-key-1",),
    )


def _needs_consent() -> NeedsConsent:
    return NeedsConsent(
        consent_request_id="consent-1",
        requirement=ConsentRequirement(
            file_ids=("file-1",),
            handling_class="public_low",
            items=(("obs-key-1", "0:4"),),
            why="sensitive text",
        ),
    )


def _materialised(**overrides) -> Materialised:
    values = dict(
        observation_key="obs-key-1",
        span="0:19",
        value=RELEASED_MATERIAL,
        zone="body",
        context_before=None,
        context_after=None,
        context_truncated=False,
        unit_length=64,
    )
    values.update(overrides)
    return Materialised(**values)


def _budget(*, files: int = 1000, rate: int = 1, cost: str = "10") -> ScanBudget:
    return ScanBudget(
        scan_id="scan-1",
        corpus_file_count=files,
        max_calls_per_1000_files=rate,
        max_estimated_cost=Decimal(cost),
    )


def _deps(**overrides):
    from llm_harness.harness import CallDependencies

    values = dict(
        proposal_class=PROPOSAL_CLASS,
        basis_key=BASIS_KEY,
        learning_scope="file",
        learning_subject_id="file-1",
        # P4's store, as a double. `obs-key-1` is the literal fixture key;
        # `_direct_bytes` cites the real content-addressed one (M14).
        evidence_resolver=lambda key: (
            RELEASED_MATERIAL
            if key == "obs-key-1" or key.startswith("sha256:") else None
        ),
        site_dependencies=SiteDependencies(
            fact=None, placement=None, residual=None, template=None,
        ),
        contradicts=lambda *_a, **_k: False,
        unreduced_fits=True,
        summarized_fits=False,
        anchors_fit=False,
        split_shard_fits=(),
        split_shards=(),
        scan_budget=_budget(),
        estimated_cost=Decimal("1"),
        actual_cost=Decimal("1"),
        allowed_vocabulary=("school",),
        policy_version=POLICY_VERSION,
    )
    values.update(overrides)
    return CallDependencies(**values)


def _events(conn, event_type: str) -> list:
    return list(conn.execute(
        "SELECT event_type, subsystem, prompt_fingerprint, explanation "
        "FROM events WHERE event_type = ? ORDER BY event_id",
        (event_type,),
    ))


def _p8_events(conn) -> list[str]:
    return [
        row["event_type"]
        for row in conn.execute(
            "SELECT event_type FROM events WHERE subsystem = 'P8' ORDER BY event_id"
        )
    ]


def _count(conn, table: str) -> int:
    return conn.execute(f"SELECT count(*) AS c FROM {table}").fetchone()["c"]


class RecordingGate:
    """Fake P7 gate. `.release(request)` is enough except NeedsConsent identity."""

    def __init__(self, conn, *, prompt: PromptDefinition, decision,
                 key: str = "obs-key-1") -> None:
        self.conn = conn
        self.prompt = prompt
        self.decision = decision
        self.key = key
        self.requests: list[ModelCallRequest] = []
        self.released: list[Released] = []

    def release(self, request: ModelCallRequest):
        self.requests.append(request)
        if isinstance(self.decision, BaseException):
            raise self.decision
        if inspect.isclass(self.decision) and issubclass(self.decision, BaseException):
            raise self.decision()
        if self.decision == "released" or self.decision is Released:
            digest = prompt_fingerprint(self.prompt)
            release_id = mint_release(
                self.conn, policy=_policy(), model_target=request.model_target,
                prompt_fingerprint=digest, audit_id=17 + len(self.released),
                minted_at=FIXED_CLOCK,
            )
            granted = Released(
                release_id=release_id,
                audit_id=17 + len(self.released),
                policy_version=POLICY_VERSION,
                materialised_items=(_materialised(observation_key=self.key),),
                redaction_manifest=RedactionManifest(entries=()),
                model_target=request.model_target,
            )
            self.released.append(granted)
            return granted
        return self.decision


def _run(conn, request, *, gate, model_client, prompt, deps):
    return run_call(
        conn, request,
        gate=gate,
        model_client=model_client,
        prompt=prompt,
        validation_dependencies=deps,
        observed_at=lambda: FIXED_CLOCK,
    )


def test_public_surface_now_includes_run_call():
    assert llm_harness.__all__ == [
        "run_call",
        "DossierRequest",
        "Dossier",
        "P8Verdict",
        "Refusal",
        "CallFailed",
        "ValidationUnavailable",
        "NeedsConsent",
    ]
    assert llm_harness.run_call is run_call
    assert llm_harness.DossierRequest is DossierRequest
    assert llm_harness.CallFailed is CallFailed
    assert llm_harness.NeedsConsent is NeedsConsent
    assert "Verdict" not in llm_harness.__all__
    assert not hasattr(llm_harness, "Verdict")


def test_run_call_signature_matches_the_orchestration_boundary():
    parameters = inspect.signature(run_call).parameters
    assert tuple(parameters)[:2] == ("conn", "request")
    for name in (
        "gate", "model_client", "prompt", "validation_dependencies", "observed_at",
    ):
        assert parameters[name].kind is inspect.Parameter.KEYWORD_ONLY, name
        assert parameters[name].default is inspect.Parameter.empty, name


def test_released_issues_once_validates_and_persists(harness_conn, subject):
    key = subject[2]
    bundle = _fact_bundle(harness_conn, subject)
    prompt = _prompt()
    digest = prompt_fingerprint(prompt)
    request = _request(fingerprint=digest, key=key)
    gate = RecordingGate(harness_conn, prompt=prompt, decision="released", key=key)
    recorder = Recorder(reply=_direct_bytes(key))
    result = _run(
        harness_conn, request,
        gate=gate,
        model_client=ModelClient(model_target=CLOUD, invoke=recorder),
        prompt=prompt,
        deps=_deps(site_dependencies=bundle),
    )
    assert isinstance(result, P8Verdict)
    assert result.outcome == ACCEPT_DIRECT
    assert len(gate.requests) == 1
    assert gate.requests[0] is request.model_call_request
    assert isinstance(gate.requests[0], ModelCallRequest)
    assert isinstance(gate.requests[0].requested_items[0], Excerpt)
    assert len(gate.released) == 1
    granted = gate.released[0]
    assert granted.audit_id == 17
    dossier = build_dossier(
        request, granted,
        reduction_rung=REDUCTION_NONE,
        allowed_vocabulary=("school",),
        prompt=prompt,
    )
    assert recorder.calls == [
        build_call_payload(
            prompt, canonical_dossier_bytes(dossier, prompt),
            model_target=CLOUD,
            policy_version=POLICY_VERSION,
            release_id=granted.release_id,
            dossier_id="dossier-address-1",
        ).model_visible_bytes,
    ]
    # The model saw what P7 released — addressed and in context, not a joined blob.
    assert RELEASED_MATERIAL.encode("utf-8") in recorder.calls[0]
    assert b'"address":"0:19"' in recorder.calls[0]
    assert granted.release_id.encode("utf-8") not in recorder.calls[0]
    assert dossier.dossier_id != granted.release_id
    assert harness_conn.execute(
        "SELECT dossier_id FROM llm_dossier"
    ).fetchone()["dossier_id"] == dossier.dossier_id
    assert _count(harness_conn, "llm_response") == 1
    assert _count(harness_conn, "llm_verdict") == 1
    assert _count(harness_conn, "llm_grounding_report") == 1
    assert _count(harness_conn, "llm_dossier") == 1
    report = harness_conn.execute("SELECT * FROM llm_grounding_report").fetchone()
    assert report["release_audit_id"] == granted.audit_id
    assert report["reduction_rung"] == REDUCTION_NONE
    assert "model_call_issued" in _p8_events(harness_conn)
    assert "validation_verdict" in _p8_events(harness_conn)
    spent = harness_conn.execute(
        "SELECT spent_at FROM release_ledger WHERE release_id = ?",
        (granted.release_id,),
    ).fetchone()
    assert spent["spent_at"] is not None
    reserved = harness_conn.execute(
        "SELECT calls_reserved FROM llm_scan_budget WHERE scan_id = ?",
        ("scan-1",),
    ).fetchone()
    assert reserved["calls_reserved"] == 1


def test_denied_returns_gate_only_refusal_and_does_not_call_the_model(harness_conn):
    prompt = _prompt()
    request = _request(fingerprint=prompt_fingerprint(prompt))
    denied = _denied()
    gate = RecordingGate(harness_conn, prompt=prompt, decision=denied)
    recorder = Recorder()
    result = _run(
        harness_conn, request,
        gate=gate,
        model_client=ModelClient(model_target=CLOUD, invoke=recorder),
        prompt=prompt,
        deps=_deps(),
    )
    assert isinstance(result, Refusal)
    assert result.denied is denied
    assert result.reason == PRIVACY_GATE_REFUSED
    assert recorder.calls == []
    assert _count(harness_conn, "llm_refusal") == 1
    assert _count(harness_conn, "llm_grounding_report") == 1
    report = harness_conn.execute(
        "SELECT citations_total, claims_total, reduction_rung, release_audit_id "
        "FROM llm_grounding_report"
    ).fetchone()
    assert report["citations_total"] == 0
    assert report["claims_total"] == 0
    assert report["release_audit_id"] is None
    assert [event["event_type"] for event in _events(harness_conn, "call_refused")] == [
        "call_refused",
    ]
    assert _events(harness_conn, "model_call_issued") == []
    assert _count(harness_conn, "llm_response") == 0
    assert _count(harness_conn, "llm_verdict") == 0
    assert harness_conn.execute(
        "SELECT calls_reserved FROM llm_scan_budget"
    ).fetchone() is None or harness_conn.execute(
        "SELECT calls_reserved FROM llm_scan_budget"
    ).fetchone()["calls_reserved"] == 0


def test_denied_refusal_is_atomic_when_append_event_fails(harness_conn, monkeypatch):
    from llm_harness import store as store_mod

    prompt = _prompt()
    request = _request(fingerprint=prompt_fingerprint(prompt))
    gate = RecordingGate(harness_conn, prompt=prompt, decision=_denied())
    recorder = Recorder()

    def boom(*_a, **_k):
        raise RuntimeError("event log down")

    monkeypatch.setattr(store_mod, "append_event", boom)
    with pytest.raises(RuntimeError, match="event log down"):
        _run(
            harness_conn, request,
            gate=gate,
            model_client=ModelClient(model_target=CLOUD, invoke=recorder),
            prompt=prompt,
            deps=_deps(),
        )
    assert recorder.calls == []
    assert _count(harness_conn, "llm_refusal") == 0
    assert _count(harness_conn, "llm_grounding_report") == 0


def test_needs_consent_is_returned_unchanged_with_no_p8_write(harness_conn):
    prompt = _prompt()
    request = _request(fingerprint=prompt_fingerprint(prompt))
    consent = _needs_consent()
    gate = RecordingGate(harness_conn, prompt=prompt, decision=consent)
    recorder = Recorder()
    result = _run(
        harness_conn, request,
        gate=gate,
        model_client=ModelClient(model_target=CLOUD, invoke=recorder),
        prompt=prompt,
        deps=_deps(),
    )
    assert result is consent
    assert type(result) is NeedsConsent
    assert result is not Refusal(denied=_denied())
    assert recorder.calls == []
    assert _p8_events(harness_conn) == []
    assert _count(harness_conn, "llm_refusal") == 0
    assert _count(harness_conn, "llm_verdict") == 0
    assert _count(harness_conn, "llm_grounding_report") == 0
    assert _count(harness_conn, "llm_response") == 0
    assert _count(harness_conn, "llm_pre_call_abstention") == 0
    assert _count(harness_conn, "llm_dossier") == 0


def test_nopolicyinforce_propagates_unchanged_and_writes_no_p8_result(harness_conn):
    prompt = _prompt()
    request = _request(fingerprint=prompt_fingerprint(prompt))
    live = NoPolicyInForce("no policy is stored for this plan version")
    gate = RecordingGate(harness_conn, prompt=prompt, decision=live)
    recorder = Recorder()
    with pytest.raises(NoPolicyInForce) as raised:
        _run(
            harness_conn, request,
            gate=gate,
            model_client=ModelClient(model_target=CLOUD, invoke=recorder),
            prompt=prompt,
            deps=_deps(),
        )
    assert raised.value is live
    assert type(raised.value) is NoPolicyInForce
    assert recorder.calls == []
    assert _p8_events(harness_conn) == []
    assert _count(harness_conn, "llm_refusal") == 0
    assert _count(harness_conn, "llm_verdict") == 0
    assert _count(harness_conn, "llm_grounding_report") == 0
    assert _count(harness_conn, "llm_pre_call_abstention") == 0


def test_missing_configuration_is_unavailable_with_no_gate_or_model_call(harness_conn):
    prompt = _prompt()
    request = _request(fingerprint=prompt_fingerprint(prompt))
    gate = RecordingGate(harness_conn, prompt=prompt, decision="released")
    recorder = Recorder()
    result = _run(
        harness_conn, request,
        gate=gate,
        model_client=ModelClient(model_target=CLOUD, invoke=recorder),
        prompt=None,
        deps=_deps(),
    )
    assert isinstance(result, ValidationUnavailable)
    assert "prompt" in result.missing
    assert gate.requests == []
    assert recorder.calls == []

    result = _run(
        harness_conn, request,
        gate=gate,
        model_client=ModelClient(model_target=CLOUD, invoke=recorder),
        prompt=prompt,
        deps=None,
    )
    assert isinstance(result, ValidationUnavailable)
    assert result.missing
    assert gate.requests == []
    assert recorder.calls == []


def test_missing_proposal_identity_is_unavailable_before_the_gate(harness_conn):
    prompt = _prompt()
    request = _request(fingerprint=prompt_fingerprint(prompt))
    gate = RecordingGate(harness_conn, prompt=prompt, decision="released")
    recorder = Recorder()
    result = _run(
        harness_conn, request,
        gate=gate,
        model_client=ModelClient(model_target=CLOUD, invoke=recorder),
        prompt=prompt,
        deps=_deps(proposal_class=None, basis_key=None),
    )
    assert isinstance(result, ValidationUnavailable)
    assert "proposal_class" in result.missing
    assert "basis_key" in result.missing
    assert gate.requests == []
    assert recorder.calls == []


def test_model_error_persists_failure_report_and_invents_neither_response_nor_verdict(
    harness_conn,
):
    prompt = _prompt()
    request = _request(fingerprint=prompt_fingerprint(prompt))
    gate = RecordingGate(harness_conn, prompt=prompt, decision="released")
    recorder = Recorder(error=RuntimeError("provider down"))
    result = _run(
        harness_conn, request,
        gate=gate,
        model_client=ModelClient(model_target=CLOUD, invoke=recorder),
        prompt=prompt,
        deps=_deps(),
    )
    assert isinstance(result, CallFailed)
    assert result.release_id == gate.released[0].release_id
    assert result.audit_id == gate.released[0].audit_id
    assert "provider down" in result.explanation
    assert len(recorder.calls) == 1
    assert _count(harness_conn, "llm_call_failure") == 1
    assert _count(harness_conn, "llm_response") == 0
    assert _count(harness_conn, "llm_verdict") == 0
    assert _count(harness_conn, "llm_grounding_report") == 1
    report = harness_conn.execute(
        "SELECT citations_total, claims_total, release_audit_id, payload "
        "FROM llm_grounding_report"
    ).fetchone()
    assert report["citations_total"] == 0
    assert report["claims_total"] == 0
    assert report["release_audit_id"] == gate.released[0].audit_id
    assert json.loads(report["payload"])["reasons_histogram"] == {}
    assert _events(harness_conn, "model_response_received") == []
    assert _events(harness_conn, "call_refused") == []
    assert len(_events(harness_conn, "model_call_issued")) == 1
    assert _events(harness_conn, "invented_failure") == []


def test_retry_is_disabled_on_call_failed_and_on_schema_invalid(harness_conn, subject):
    key = subject[2]
    bundle = _fact_bundle(harness_conn, subject)
    prompt = _prompt()
    digest = prompt_fingerprint(prompt)
    request = _request(fingerprint=digest, key=key)
    failing = Recorder(error=RuntimeError("once"))
    gate = RecordingGate(harness_conn, prompt=prompt, decision="released", key=key)
    failed = _run(
        harness_conn, request,
        gate=gate,
        model_client=ModelClient(model_target=CLOUD, invoke=failing),
        prompt=prompt,
        deps=_deps(site_dependencies=bundle),
    )
    assert isinstance(failed, CallFailed)
    assert len(failing.calls) == 1
    assert len(gate.released) == 1

    second_gate = RecordingGate(harness_conn, prompt=prompt, decision="released", key=key)
    invalid = Recorder(reply=MALFORMED_BYTES)
    verdict = _run(
        harness_conn, _request(file_id="file-2", fingerprint=digest, key=key),
        gate=second_gate,
        model_client=ModelClient(model_target=CLOUD, invoke=invalid),
        prompt=prompt,
        deps=_deps(site_dependencies=bundle, learning_subject_id="file-2", scan_budget=_budget(files=2000)),
    )
    assert isinstance(verdict, P8Verdict)
    assert SCHEMA_INVALID in verdict.reasons
    assert len(invalid.calls) == 1
    assert len(second_gate.released) == 1


def test_initially_fitting_call_records_none_and_releases_once(harness_conn, subject):
    key = subject[2]
    bundle = _fact_bundle(harness_conn, subject)
    prompt = _prompt()
    request = _request(fingerprint=prompt_fingerprint(prompt), key=key)
    gate = RecordingGate(harness_conn, prompt=prompt, decision="released", key=key)
    recorder = Recorder(reply=UNKNOWN_BYTES)
    result = _run(
        harness_conn, request,
        gate=gate,
        model_client=ModelClient(model_target=CLOUD, invoke=recorder),
        prompt=prompt,
        deps=_deps(site_dependencies=bundle, 
            unreduced_fits=True,
            summarized_fits=True,
            anchors_fit=True,
            split_shard_fits=(True, True),
        ),
    )
    assert isinstance(result, P8Verdict)
    assert len(gate.requests) == 1
    assert len(recorder.calls) == 1
    assert harness_conn.execute(
        "SELECT reduction_rung FROM llm_dossier"
    ).fetchone()["reduction_rung"] == REDUCTION_NONE
    assert harness_conn.execute(
        "SELECT calls_reserved FROM llm_scan_budget"
    ).fetchone()["calls_reserved"] == 1


def test_oversized_intermediate_forms_spend_nothing_until_a_fitting_rung(harness_conn, subject):
    key = subject[2]
    bundle = _fact_bundle(harness_conn, subject)
    prompt = _prompt()
    digest = prompt_fingerprint(prompt)
    request = _request(fingerprint=digest, key=key)
    gate = RecordingGate(harness_conn, prompt=prompt, decision="released", key=key)
    recorder = Recorder(reply=UNKNOWN_BYTES)
    result = _run(
        harness_conn, request,
        gate=gate,
        model_client=ModelClient(model_target=CLOUD, invoke=recorder),
        prompt=prompt,
        deps=_deps(site_dependencies=bundle, 
            unreduced_fits=False,
            summarized_fits=True,
            anchors_fit=True,
            split_shard_fits=(True,),
        ),
    )
    assert isinstance(result, P8Verdict)
    assert len(gate.requests) == 1
    assert len(recorder.calls) == 1
    assert harness_conn.execute(
        "SELECT reduction_rung FROM llm_dossier"
    ).fetchone()["reduction_rung"] == SUMMARIZED_FACTS

    anchors_gate = RecordingGate(harness_conn, prompt=prompt, decision="released", key=key)
    anchors_recorder = Recorder(reply=UNKNOWN_BYTES)
    _run(
        harness_conn, _request(file_id="file-anchors", fingerprint=digest, key=key),
        gate=anchors_gate,
        model_client=ModelClient(model_target=CLOUD, invoke=anchors_recorder),
        prompt=prompt,
        deps=_deps(site_dependencies=bundle, 
            learning_subject_id="file-anchors",
            unreduced_fits=False,
            summarized_fits=False,
            anchors_fit=True,
            split_shard_fits=(True, True),
            scan_budget=_budget(files=3000, cost="20"),
        ),
    )
    assert len(anchors_gate.requests) == 1
    assert len(anchors_recorder.calls) == 1
    rungs = {
        row["reduction_rung"]
        for row in harness_conn.execute("SELECT reduction_rung FROM llm_dossier")
    }
    assert PRESERVED_ANCHORS in rungs


def test_each_fitting_split_shard_gets_a_distinct_request_release_reservation_and_call(
    harness_conn, subject,
):
    key = subject[2]
    bundle = _fact_bundle(harness_conn, subject)
    prompt = _prompt()
    digest = prompt_fingerprint(prompt)
    parent = _request(fingerprint=digest, key=key)
    shard_a = _request(file_id="file-a", fingerprint=digest, key=key)
    shard_b = _request(file_id="file-b", fingerprint=digest, key=key)
    deferred = _request(file_id="file-deferred", fingerprint=digest, key=key)
    gate = RecordingGate(harness_conn, prompt=prompt, decision="released", key=key)
    recorder = Recorder(reply=UNKNOWN_BYTES)
    result = _run(
        harness_conn, parent,
        gate=gate,
        model_client=ModelClient(model_target=CLOUD, invoke=recorder),
        prompt=prompt,
        deps=_deps(
            site_dependencies=bundle,
            unreduced_fits=False,
            summarized_fits=False,
            anchors_fit=False,
            split_shard_fits=(True, False, True),
            split_shards=(shard_a, deferred, shard_b),
            scan_budget=_budget(files=3000, cost="20"),
        ),
    )
    assert isinstance(result, P8Verdict)
    assert [item.target.file_ids for item in gate.requests] == [
        ("file-a",), ("file-b",),
    ]
    assert gate.requests[0] is shard_a.model_call_request
    assert gate.requests[1] is shard_b.model_call_request
    assert len(gate.released) == 2
    assert gate.released[0].release_id != gate.released[1].release_id
    assert len(recorder.calls) == 2
    reservations = list(harness_conn.execute(
        "SELECT reservation_id FROM llm_budget_reservation ORDER BY rowid"
    ))
    assert len(reservations) == 2
    assert reservations[0]["reservation_id"] != reservations[1]["reservation_id"]
    rungs = list(harness_conn.execute("SELECT DISTINCT reduction_rung FROM llm_dossier"))
    assert [row["reduction_rung"] for row in rungs] == [SPLIT]


def test_deferred_split_emits_pre_call_abstention_and_spends_nothing(harness_conn):
    prompt = _prompt()
    request = _request(fingerprint=prompt_fingerprint(prompt))
    gate = RecordingGate(harness_conn, prompt=prompt, decision="released")
    recorder = Recorder()
    result = _run(
        harness_conn, request,
        gate=gate,
        model_client=ModelClient(model_target=CLOUD, invoke=recorder),
        prompt=prompt,
        deps=_deps(
            unreduced_fits=False,
            summarized_fits=False,
            anchors_fit=False,
            split_shard_fits=(False, False),
            split_shards=(
                _request(file_id="file-x"),
                _request(file_id="file-y"),
            ),
        ),
    )
    assert isinstance(result, P8Verdict)
    assert result.outcome == ABSTAIN
    assert result.reasons == (BUDGET_EXHAUSTED,)
    assert gate.requests == []
    assert recorder.calls == []
    assert _count(harness_conn, "llm_pre_call_abstention") == 1
    assert _count(harness_conn, "llm_grounding_report") == 1
    row = harness_conn.execute(
        "SELECT citations_total, claims_total, reduction_rung, release_audit_id "
        "FROM llm_grounding_report"
    ).fetchone()
    assert row["citations_total"] == 0
    assert row["claims_total"] == 0
    assert row["reduction_rung"] == DEFERRED
    assert row["release_audit_id"] is None
    abstention = harness_conn.execute(
        "SELECT reason FROM llm_pre_call_abstention"
    ).fetchone()
    assert abstention["reason"] == BUDGET_EXHAUSTED
    assert [event["event_type"] for event in _events(harness_conn, "call_refused")] == [
        "call_refused",
    ]
    assert _count(harness_conn, "llm_response") == 0
    assert _count(harness_conn, "llm_dossier") == 0
    assert harness_conn.execute("SELECT count(*) AS c FROM llm_budget_reservation").fetchone()["c"] == 0


def test_d14_links_events_with_released_audit_id_and_spends_released_release_id(
    harness_conn, subject,
):
    key = subject[2]
    bundle = _fact_bundle(harness_conn, subject)
    prompt = _prompt()
    request = _request(fingerprint=prompt_fingerprint(prompt), key=key)
    gate = RecordingGate(harness_conn, prompt=prompt, decision="released", key=key)
    recorder = Recorder(reply=UNKNOWN_BYTES)
    _run(
        harness_conn, request,
        gate=gate,
        model_client=ModelClient(model_target=CLOUD, invoke=recorder),
        prompt=prompt,
        deps=_deps(site_dependencies=bundle),
    )
    granted = gate.released[0]
    issued = _events(harness_conn, "model_call_issued")[0]
    body = json.loads(issued["explanation"])
    assert body["audit_id"] == granted.audit_id
    assert body["release_id"] == granted.release_id
    source = SRC_HARNESS.read_text()
    assert "AuditRecord" not in source
    assert "released.audit_id" in source
    assert "released.release_id" in source


def test_exactly_three_p7_branches_and_needs_consent_has_no_conversion_path():
    assert DECISION_TYPES == (Released, Denied, NeedsConsent)
    assert not issubclass(NoPolicyInForce, tuple(DECISION_TYPES))
    source = inspect.getsource(run_call)
    assert "NeedsConsent" in source
    assert "NoPolicyInForce" in source
    tree = ast.parse(SRC_HARNESS.read_text())
    refusal_from_consent = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "Refusal":
                for keyword in node.keywords:
                    if keyword.arg == "denied" and isinstance(keyword.value, ast.Name):
                        if keyword.value.id in {"consent", "needs_consent", "outcome"}:
                            refusal_from_consent = True
    assert refusal_from_consent is False
    assert "needs_consent" not in inspect.signature(run_call).parameters


def test_request_stays_reference_only_until_release(harness_conn):
    prompt = _prompt()
    request = _request(fingerprint=prompt_fingerprint(prompt))
    requested = request.model_call_request.requested_items[0]
    assert isinstance(requested, Excerpt)
    assert not hasattr(request, "materialised_items")
    assert not any(hasattr(item, "value") for item in request.evidence_items)
    gate = RecordingGate(harness_conn, prompt=prompt, decision=_denied())
    _run(
        harness_conn, request,
        gate=gate,
        model_client=ModelClient(model_target=CLOUD, invoke=Recorder()),
        prompt=prompt,
        deps=_deps(),
    )
    assert gate.requests[0] is request.model_call_request
    payload = canonical_json({
        "requested_items": [{"observation_key": requested.observation_key}],
        "evidence_items": [item.evidence_ref for item in request.evidence_items],
    })
    assert "Columbia University" not in payload


def test_harness_does_not_invoke_the_client_itself():
    tree = ast.parse(SRC_HARNESS.read_text())
    invokes = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "invoke"
    ]
    assert invokes == []
    source = SRC_HARNESS.read_text()
    assert "from llm_harness.transport import" in source
    assert "issue(" in source
    assert "def normalize(" not in source
    assert "def contradicts(" not in source


def test_eligible_marker_is_not_a_public_run_call_branch():
    assert Eligible not in (P8Verdict, Refusal, NeedsConsent, ValidationUnavailable, CallFailed)
    assert "Eligible" not in llm_harness.__all__


# --- R6: the P6 consequence and the P8 verdict are one write --------------------


def test_a_failed_p8_verdict_write_does_not_leave_a_p6_fact_behind(
    harness_conn, subject, monkeypatch,
):
    """Site A writes twice: P6's fact, then P8's verdict row about it.

    Unsplit, a failure between them leaves P6 holding an `llm_supported` fact whose
    judgement no P8 verdict records -- a fact with no provenance, which is the exact
    shape `record_cd_verdict` was repaired for.
    """
    import sqlite3

    import llm_harness.harness as harness_module
    from facts.file_facts import facts_for_file

    key = subject[2]
    bundle = _fact_bundle(harness_conn, subject)
    prompt = _prompt()
    request = _request(fingerprint=prompt_fingerprint(prompt), key=key)
    gate = RecordingGate(harness_conn, prompt=prompt, decision="released", key=key)

    def explode(*_a, **_k):
        raise sqlite3.IntegrityError("verdict row refused")

    monkeypatch.setattr(harness_module, "record_verdict", explode)
    with pytest.raises(sqlite3.IntegrityError):
        _run(
            harness_conn, request,
            gate=gate,
            model_client=ModelClient(
                model_target=CLOUD, invoke=Recorder(reply=_direct_bytes(key)),
            ),
            prompt=prompt,
            deps=_deps(site_dependencies=bundle),
        )

    file_id, content_hash, _key = subject
    assert [
        row for row in facts_for_file(harness_conn, file_id, content_hash)
        if row["field_key"] == "school"
    ] == []
    assert harness_conn.execute(
        "SELECT count(*) AS c FROM llm_verdict"
    ).fetchone()["c"] == 0
