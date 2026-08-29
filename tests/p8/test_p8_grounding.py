"""Grounding reports for every P8 call attempt, including pre-egress terminals."""
from __future__ import annotations

import inspect

import pytest

import llm_harness
from llm_harness.authorship import COMPONENT_VERSION
from llm_harness.records import (
    CallFailed,
    Dossier,
    DossierRequest,
    EvidenceItem,
    GroundingReport,
    PreCallAbstention,
    Refusal,
)
from llm_harness.validation import (
    report_for_call_failure,
    report_for_pre_call_terminal,
    report_for_refusal,
    validate_response,
)
from llm_harness.vocabulary import (
    A_FACT,
    BUDGET_EXHAUSTED,
    DEFERRED,
    DIRECT_ANCHOR,
    NOT_ELIGIBLE_FOR_MODEL,
    PRIVACY_GATE_REFUSED,
    REDUCTION_NONE,
    REMAINS_AMBIGUOUS,
    USER_REJECTED_EQUIVALENT,
)
from privacy.consent import ConsentRequirement
from privacy.denial import RemedyOption
from privacy.items import CandidateLabel
from privacy.release import Denied, ModelCallRequest, ModelTarget, NeedsConsent, Target
from p8.conftest import make_evidence_item


DIRECT_BYTES = (
    b'{"claims":[{"claim_ref":"c1","payload":{"field":"school","value":"Columbia"},'
    b'"citations":[{"evidence_ref":"obs-key-1","cited_span":"Columbia University",'
    b'"why_it_supports":"names the school"}]}]}'
)
RELEASED_MATERIAL = "Columbia University — redacted dossier excerpt"


def _model_target() -> ModelTarget:
    return ModelTarget(locality="local", model_id="fixture-model", provider="fixture")


def _model_call_request() -> ModelCallRequest:
    return ModelCallRequest(
        stage="grouping",
        target=Target(file_ids=("file-1",)),
        model_target=_model_target(),
        requested_items=(CandidateLabel(label="Passport"),),
        prompt_template_id="template.grouping",
        prompt_fingerprint="fingerprint.grouping",
        max_dossier_tokens=4000,
    )


def _denied() -> Denied:
    return Denied(
        reason="unclassified",
        explanation="no classification is stored for this file",
        remedy_options=(RemedyOption(action="classify", detail="classify first"),),
        evidence_refs=("obs-key-1",),
    )


def _request() -> DossierRequest:
    return DossierRequest(
        call_site=A_FACT,
        subject_ref="file-1",
        eligibility_reason=REMAINS_AMBIGUOUS,
        evidence_items=(make_evidence_item(),),
        conflicts=(),
        model_call_request=_model_call_request(),
        plan_version=None,
        evidence_snapshot_id="snap-1",
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


def _zero_counters(report: GroundingReport) -> None:
    assert report.citations_total == 0
    assert report.citations_resolved == 0
    assert report.citations_span_matched == 0
    assert report.claims_total == 0
    assert report.claims_abstained == 0
    assert report.claims_accepted_direct == 0
    assert report.claims_accepted_context == 0
    assert report.claims_weak == 0
    assert report.claims_rejected == 0


def test_report_for_refusal_fills_spec_fields_and_zero_counts():
    request = _request()
    refusal = Refusal(denied=_denied(), validator_version="P8/0.1.0", policy_version="policy-1")
    report = report_for_refusal(
        request, refusal, validator_version=COMPONENT_VERSION,
    )
    assert report.dossier_id
    assert report.call_site == request.call_site
    assert report.model_id == request.model_call_request.model_target.model_id
    assert report.prompt_fingerprint == request.model_call_request.prompt_fingerprint
    assert report.validator_version == COMPONENT_VERSION
    assert report.reduction_rung
    assert report.dossier_builder
    assert report.release_audit_id is None
    _zero_counters(report)
    assert dict(report.reasons_histogram) == {PRIVACY_GATE_REFUSED: 1}
    assert refusal.reason == PRIVACY_GATE_REFUSED


def test_gate_denied_gets_zero_count_refusal_report():
    report = report_for_refusal(
        _request(), Refusal(denied=_denied(), validator_version="P8/0.1.0", policy_version="policy-1"), validator_version=COMPONENT_VERSION,
    )
    assert report.reasons_histogram[PRIVACY_GATE_REFUSED] == 1
    assert report.release_audit_id is None


def test_ineligibility_gets_pre_call_report():
    terminal = PreCallAbstention(
        reason=NOT_ELIGIBLE_FOR_MODEL, call_site=A_FACT, subject_ref="file-1",
    )
    report = report_for_pre_call_terminal(
        _request(), terminal, validator_version=COMPONENT_VERSION,
    )
    _zero_counters(report)
    assert report.release_audit_id is None
    assert dict(report.reasons_histogram) == {NOT_ELIGIBLE_FOR_MODEL: 1}
    assert report.call_site == A_FACT
    assert report.model_id == "fixture-model"
    assert report.prompt_fingerprint == "fingerprint.grouping"
    assert report.reduction_rung == REDUCTION_NONE


def test_suppression_gets_pre_call_report():
    terminal = PreCallAbstention(
        reason=USER_REJECTED_EQUIVALENT, call_site=A_FACT, subject_ref="file-1",
    )
    report = report_for_pre_call_terminal(
        _request(), terminal, validator_version=COMPONENT_VERSION,
    )
    assert dict(report.reasons_histogram) == {USER_REJECTED_EQUIVALENT: 1}
    assert report.release_audit_id is None
    _zero_counters(report)


def test_budget_exhaustion_gets_pre_call_report():
    terminal = PreCallAbstention(
        reason=BUDGET_EXHAUSTED, call_site=A_FACT, subject_ref="file-1",
    )
    report = report_for_pre_call_terminal(
        _request(), terminal, validator_version=COMPONENT_VERSION,
    )
    assert dict(report.reasons_histogram) == {BUDGET_EXHAUSTED: 1}
    assert report.release_audit_id is None
    assert report.reduction_rung == DEFERRED
    _zero_counters(report)


def test_needs_consent_emits_neither_report_nor_event():
    assert not hasattr(llm_harness.validation, "report_for_needs_consent")
    assert "NeedsConsent" not in inspect.signature(report_for_pre_call_terminal).parameters
    with pytest.raises(TypeError):
        report_for_pre_call_terminal(
            _request(), _needs_consent(), validator_version=COMPONENT_VERSION,
        )
    with pytest.raises(TypeError):
        report_for_refusal(
            _request(), _needs_consent(), validator_version=COMPONENT_VERSION,
        )


def test_issued_call_failure_has_real_audit_id_and_empty_histogram():
    failed = CallFailed(
        request_identity="dossier-1",
        release_id="rel-1",
        audit_id=17,
        explanation="client raised",
        validator_version="P8/0.1.0",
        policy_version="policy-1",
    )
    report = report_for_call_failure(
        _request(), failed, validator_version=COMPONENT_VERSION,
    )
    _zero_counters(report)
    assert report.release_audit_id == 17
    assert dict(report.reasons_histogram) == {}
    assert report.dossier_id
    assert report.call_site == A_FACT
    assert report.model_id == "fixture-model"
    assert report.prompt_fingerprint == "fingerprint.grouping"
    assert report.validator_version == COMPONENT_VERSION
    assert report.reduction_rung
    assert report.dossier_builder


def test_pre_call_report_derives_solely_from_request_and_terminal():
    request = _request()
    terminal = PreCallAbstention(
        reason=NOT_ELIGIBLE_FOR_MODEL, call_site=A_FACT, subject_ref="file-1",
    )
    report = report_for_pre_call_terminal(
        request, terminal, validator_version=COMPONENT_VERSION,
    )
    assert report.call_site == request.call_site
    assert report.model_id == request.model_call_request.model_target.model_id
    assert report.prompt_fingerprint == request.model_call_request.prompt_fingerprint
    assert report.reasons_histogram[terminal.reason] == 1


def test_response_bearing_report_derives_from_verdict_and_citation_results():
    dossier = Dossier(
        dossier_id="dossier-1",
        call_site=A_FACT,
        subject_ref="file-1",
        eligibility_reason=REMAINS_AMBIGUOUS,
        plan_version=None,
        policy_version="policy-1",
        allowed_vocabulary=("school",),
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
        conflicts=(),
        released_evidence=(),
        max_dossier_tokens=4000,
        reduction_rung=REDUCTION_NONE,
        release_id="rel-1",
    )

    def resolve(key: str) -> str | None:
        return RELEASED_MATERIAL if key == "obs-key-1" else None

    verdicts, report = validate_response(
        dossier,
        DIRECT_BYTES,
        evidence_resolver=resolve,
        site_validator=lambda *_a, **_k: None,
        contradicts=lambda *_a, **_k: False,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        dossier_builder="fixture",
        release_audit_id=17,
    )
    assert report.claims_total == len(verdicts)
    assert report.claims_accepted_direct == sum(
        1 for verdict in verdicts if verdict.outcome == "accept_direct"
    )
    checked = [item for verdict in verdicts for item in verdict.citations_checked]
    assert report.citations_total == len(checked)
    assert report.citations_resolved == sum(1 for item in checked if item.resolved)
    assert report.citations_span_matched == sum(
        1 for item in checked if item.span_matched
    )
    histogram: dict[str, int] = {}
    for verdict in verdicts:
        for reason in verdict.reasons:
            histogram[reason] = histogram.get(reason, 0) + 1
    assert dict(report.reasons_histogram) == histogram
    assert report.dossier_id == dossier.dossier_id
    assert report.call_site == dossier.call_site
    assert report.reduction_rung == dossier.reduction_rung
    assert report.release_audit_id == 17


def test_validation_module_does_not_persist():
    source = inspect.getsource(llm_harness.validation)
    assert "record_grounding_report" not in source
    assert "append_event" not in source
    assert "sqlite3" not in source
