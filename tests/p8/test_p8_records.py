"""Immutable P8 contracts: dossiers, payloads, claims, verdicts, and terminals."""
from __future__ import annotations

import dataclasses

import pytest

import llm_harness
from facts.llm_seam import Verdict as SeamVerdict
from llm_harness.records import (
    CallFailed,
    CallPayload,
    CallResult,
    CheckedCitation,
    Citation,
    Claim,
    Conflict,
    Dossier,
    DossierRequest,
    EvidenceItem,
    GroundingReport,
    MalformedRecord,
    MalformedVerdict,
    P8Verdict,
    PreCallAbstention,
    PromptDefinition,
    Refusal,
    Unknown,
    ValidationUnavailable,
    assemble,
    build_call_payload,
)
from llm_harness.vocabulary import (
    A_FACT,
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    ALL_REASON_CODES,
    B_GROUP,
    BUDGET_EXHAUSTED,
    C_PLACEMENT,
    D_RESIDUAL,
    DIRECT_ANCHOR,
    E_TEMPLATE,
    LLM_SUPPORTED,
    NOT_ELIGIBLE_FOR_MODEL,
    OUTCOMES,
    PRIVACY_GATE_REFUSED,
    REDUCTION_NONE,
    REMAINS_AMBIGUOUS,
    SCHEMA_INVALID,
    SCOPE_FILE,
    USER_OPTED_RESIDUAL_SET_INTO_AI_REVIEW,
    WEAK,
)
from privacy.consent import ConsentRequirement
from privacy.denial import RemedyOption
from privacy.items import CandidateLabel
from privacy.release import Denied, ModelCallRequest, ModelTarget, NeedsConsent, Target


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


def _prompt() -> PromptDefinition:
    return PromptDefinition(
        template_id="template.grouping",
        template_bytes=b"TEMPLATE",
        response_schema_bytes=b'{"type":"object"}',
        call_site=A_FACT,
        call_site_version="1",
        shaping_policy_bytes=b'{"policy":"authored"}',
    )


def _evidence_item() -> EvidenceItem:
    return EvidenceItem(
        evidence_ref="obs-key-1",
        kind="excerpt",
        location="body",
        excerpt_span=(0, 4),
        reliability_state="direct",
        basis=DIRECT_ANCHOR,
    )


def _citation() -> Citation:
    return Citation(
        evidence_ref="obs-key-1",
        cited_span="quote",
        metadata_field_name=None,
        why_it_supports="names the field",
    )


def _denied() -> Denied:
    return Denied(
        reason="unclassified",
        explanation="no classification is stored for this file",
        remedy_options=(RemedyOption(action="classify", detail="classify first"),),
        evidence_refs=("obs-key-1",),
    )


VERDICT_BASE = dict(
    verdict_id="verdict-1",
    dossier_id="dossier-1",
    claim_ref="claim-1",
    disposition=LLM_SUPPORTED,
    reasons=(),
    may_propose=False,
    citations_checked=(),
    scope=SCOPE_FILE,
    validator_version="P8/0.1.0",
    policy_version="policy-1",
    plan_version=None,
)


def _field_names(cls: type) -> tuple[str, ...]:
    return tuple(field.name for field in dataclasses.fields(cls))


def test_public_surface_is_exactly_the_task_1_exports():
    assert llm_harness.__all__ == [
        "Dossier",
        "P8Verdict",
        "Refusal",
        "ValidationUnavailable",
        "NeedsConsent",
    ]
    assert llm_harness.Dossier is Dossier
    assert llm_harness.P8Verdict is P8Verdict
    assert llm_harness.Refusal is Refusal
    assert llm_harness.ValidationUnavailable is ValidationUnavailable
    assert "Verdict" not in llm_harness.__all__
    assert not hasattr(llm_harness, "Verdict")
    assert "run_call" not in llm_harness.__all__
    assert not hasattr(llm_harness, "run_call")


def test_needs_consent_is_p7s_exact_class():
    assert llm_harness.NeedsConsent is NeedsConsent


def test_p8_verdict_is_not_the_p6_seam_verdict():
    assert P8Verdict is not SeamVerdict
    assert llm_harness.P8Verdict is not SeamVerdict


def test_dossier_request_is_frozen_reference_only():
    request = DossierRequest(
        call_site=A_FACT,
        subject_ref="file-1",
        eligibility_reason=REMAINS_AMBIGUOUS,
        evidence_refs=("obs-key-1",),
        model_call_request=_model_call_request(),
        plan_version=None,
        evidence_snapshot_id="snap-1",
        budget_context="scan-1",
    )
    assert dataclasses.is_dataclass(request)
    assert request.__dataclass_params__.frozen
    assert hasattr(request, "__slots__")
    assert _field_names(DossierRequest) == (
        "call_site",
        "subject_ref",
        "eligibility_reason",
        "evidence_refs",
        "model_call_request",
        "plan_version",
        "evidence_snapshot_id",
        "budget_context",
    )
    assert isinstance(request.model_call_request, ModelCallRequest)
    forbidden_content_fields = {
        "excerpt", "body", "observation", "content", "text", "raw",
        "excerpt_span", "raw_value", "observation_body",
    }
    assert not (set(_field_names(DossierRequest)) & forbidden_content_fields)
    with pytest.raises(dataclasses.FrozenInstanceError):
        request.subject_ref = "other"  # type: ignore[misc]


def test_prompt_definition_is_frozen_and_carries_exact_bytes():
    prompt = _prompt()
    assert prompt.__dataclass_params__.frozen
    assert hasattr(prompt, "__slots__")
    assert _field_names(PromptDefinition) == (
        "template_id",
        "template_bytes",
        "response_schema_bytes",
        "call_site",
        "call_site_version",
        "shaping_policy_bytes",
    )
    assert prompt.template_bytes == b"TEMPLATE"
    assert prompt.response_schema_bytes == b'{"type":"object"}'
    assert prompt.shaping_policy_bytes == b'{"policy":"authored"}'


def test_build_call_payload_assembles_model_visible_bytes_from_sources():
    prompt = _prompt()
    dossier_bytes = b"DOSSIER"
    payload = build_call_payload(
        prompt,
        dossier_bytes,
        model_target=_model_target(),
        prompt_fingerprint="fp-injected",
        policy_version="policy-1",
        release_id="rel-1",
    )
    assert isinstance(payload, CallPayload)
    assert payload.__dataclass_params__.frozen
    assert hasattr(payload, "__slots__")
    assert _field_names(CallPayload) == (
        "prompt_definition",
        "canonical_dossier_bytes",
        "model_visible_bytes",
        "model_target",
        "prompt_fingerprint",
        "policy_version",
        "release_id",
    )
    assert payload.prompt_definition is prompt
    assert payload.canonical_dossier_bytes == dossier_bytes
    assert payload.model_visible_bytes == assemble(prompt, dossier_bytes)
    assert payload.model_visible_bytes == prompt.template_bytes + dossier_bytes
    assert isinstance(payload.model_target, ModelTarget)
    for provenance in (payload.release_id, payload.policy_version,
                       payload.prompt_fingerprint, payload.model_target.model_id):
        assert provenance.encode("utf-8") not in payload.model_visible_bytes


def test_call_payload_rejects_mismatched_preassembled_bytes():
    prompt = _prompt()
    with pytest.raises(MalformedRecord):
        CallPayload(
            prompt_definition=prompt,
            canonical_dossier_bytes=b"DOSSIER",
            model_visible_bytes=b"OTHER",
            model_target=_model_target(),
            prompt_fingerprint="fp",
            policy_version="policy-1",
            release_id="rel-1",
        )


def test_evidence_item_and_conflict_are_frozen():
    item = _evidence_item()
    conflict = Conflict(conflict_id="c1", kind="suppressed_candidate")
    assert item.__dataclass_params__.frozen
    assert conflict.__dataclass_params__.frozen
    assert _field_names(EvidenceItem) == (
        "evidence_ref", "kind", "location", "excerpt_span",
        "reliability_state", "basis",
    )
    assert _field_names(Conflict) == ("conflict_id", "kind")
    assert item.basis == DIRECT_ANCHOR


def test_evidence_item_rejects_unknown_basis():
    with pytest.raises((MalformedRecord, ValueError)):
        EvidenceItem(
            evidence_ref="obs-key-1",
            kind="excerpt",
            location="body",
            excerpt_span=(0, 4),
            reliability_state="direct",
            basis="direct",
        )


def test_citation_takes_span_or_metadata_field_not_both():
    span = Citation(
        evidence_ref="obs-key-1",
        cited_span="quote",
        metadata_field_name=None,
        why_it_supports="supports the value",
    )
    meta = Citation(
        evidence_ref="obs-key-1",
        cited_span=None,
        metadata_field_name="page_count",
        why_it_supports="the named field",
    )
    assert span.__dataclass_params__.frozen
    assert _field_names(Citation) == (
        "evidence_ref", "cited_span", "metadata_field_name", "why_it_supports",
    )
    assert meta.metadata_field_name == "page_count"
    with pytest.raises(MalformedRecord):
        Citation(
            evidence_ref="obs-key-1",
            cited_span="quote",
            metadata_field_name="page_count",
            why_it_supports="both",
        )
    with pytest.raises(MalformedRecord):
        Citation(
            evidence_ref="obs-key-1",
            cited_span=None,
            metadata_field_name=None,
            why_it_supports="neither",
        )


def test_claim_requires_exactly_one_of_citations_or_unknown():
    cited = Claim(
        payload={"field": "school", "value": "UChicago"},
        citations=(_citation(),),
        unknown=None,
    )
    unknown = Claim(
        payload={"field": "school"},
        citations=(),
        unknown=Unknown(insufficiency_statement="no labeled school"),
    )
    assert cited.__dataclass_params__.frozen
    assert unknown.__dataclass_params__.frozen
    assert _field_names(Claim) == ("payload", "citations", "unknown")
    assert _field_names(Unknown) == ("insufficiency_statement",)
    with pytest.raises(MalformedRecord):
        Claim(
            payload={"field": "school"},
            citations=(_citation(),),
            unknown=Unknown(insufficiency_statement="both"),
        )
    with pytest.raises(MalformedRecord):
        Claim(payload={"field": "school"}, citations=(), unknown=None)


def test_dossier_is_frozen_closed_world_and_content_bearing_after_release():
    dossier = Dossier(
        dossier_id="dossier-1",
        call_site=A_FACT,
        subject_ref="file-1",
        eligibility_reason=REMAINS_AMBIGUOUS,
        plan_version=None,
        policy_version="policy-1",
        allowed_vocabulary=("school",),
        evidence_items=(_evidence_item(),),
        conflicts=(Conflict(conflict_id="c1", kind="stronger_fact"),),
        max_dossier_tokens=4000,
        reduction_rung=REDUCTION_NONE,
        release_id="rel-1",
    )
    assert dossier.__dataclass_params__.frozen
    assert hasattr(dossier, "__slots__")
    assert _field_names(Dossier) == (
        "dossier_id",
        "call_site",
        "subject_ref",
        "eligibility_reason",
        "plan_version",
        "policy_version",
        "allowed_vocabulary",
        "evidence_items",
        "conflicts",
        "max_dossier_tokens",
        "reduction_rung",
        "release_id",
    )
    assert dossier.reduction_rung == "none"
    assert dossier.evidence_items[0].basis == DIRECT_ANCHOR


def test_plan_version_is_required_at_placement_residual_and_template():
    kwargs = dict(
        dossier_id="dossier-1",
        subject_ref="file-1",
        plan_version=None,
        policy_version="policy-1",
        allowed_vocabulary=(),
        evidence_items=(),
        conflicts=(),
        max_dossier_tokens=4000,
        reduction_rung=REDUCTION_NONE,
        release_id="rel-1",
    )
    for site, eligibility in (
        (C_PLACEMENT, "several_legal_nodes_plausible"),
        (D_RESIDUAL, USER_OPTED_RESIDUAL_SET_INTO_AI_REVIEW),
        (E_TEMPLATE, "accepted_group_fits_no_existing_template"),
    ):
        with pytest.raises(MalformedRecord):
            Dossier(call_site=site, eligibility_reason=eligibility, **kwargs)
    Dossier(
        call_site=C_PLACEMENT,
        eligibility_reason="several_legal_nodes_plausible",
        **{**kwargs, "plan_version": "plan-1"},
    )
    Dossier(
        call_site=A_FACT,
        eligibility_reason=REMAINS_AMBIGUOUS,
        **kwargs,
    )
    Dossier(
        call_site=B_GROUP,
        eligibility_reason="coherence_judgement",
        **kwargs,
    )


def test_dossier_rejects_unknown_vocabulary_members():
    with pytest.raises((MalformedRecord, ValueError)):
        Dossier(
            dossier_id="dossier-1",
            call_site="Z_invented",
            subject_ref="file-1",
            eligibility_reason=REMAINS_AMBIGUOUS,
            plan_version=None,
            policy_version="policy-1",
            allowed_vocabulary=(),
            evidence_items=(),
            conflicts=(),
            max_dossier_tokens=4000,
            reduction_rung=REDUCTION_NONE,
            release_id="rel-1",
        )


def test_p8_verdict_constructs_with_spec_fields():
    checked = CheckedCitation(
        citation_ref="obs-key-1", resolved=True, span_matched=True,
    )
    base = {key: value for key, value in VERDICT_BASE.items()
            if key != "citations_checked"}
    verdict = P8Verdict(
        outcome=ACCEPT_DIRECT,
        requires_review=False,
        citations_checked=(checked,),
        **base,
    )
    assert verdict.__dataclass_params__.frozen
    assert hasattr(verdict, "__slots__")
    assert _field_names(P8Verdict) == (
        "verdict_id",
        "dossier_id",
        "claim_ref",
        "outcome",
        "disposition",
        "reasons",
        "may_propose",
        "requires_review",
        "citations_checked",
        "scope",
        "validator_version",
        "policy_version",
        "plan_version",
    )
    assert _field_names(CheckedCitation) == (
        "citation_ref", "resolved", "span_matched",
    )


def test_context_acceptance_always_requires_review():
    with pytest.raises(MalformedVerdict):
        P8Verdict(outcome=ACCEPT_CONTEXT_SUPPORTED, requires_review=False, **VERDICT_BASE)


def test_weak_may_not_propose():
    with pytest.raises(MalformedVerdict):
        P8Verdict(
            outcome=WEAK,
            requires_review=False,
            **{**VERDICT_BASE, "may_propose": True},
        )


def test_p8_verdict_rejects_unknown_vocabulary_members():
    with pytest.raises(MalformedVerdict):
        P8Verdict(outcome="invented_outcome", requires_review=False, **VERDICT_BASE)
    with pytest.raises(MalformedVerdict):
        P8Verdict(
            outcome=ACCEPT_DIRECT,
            requires_review=False,
            **{**VERDICT_BASE, "disposition": "invented_disposition"},
        )
    with pytest.raises(MalformedVerdict):
        P8Verdict(
            outcome=ACCEPT_DIRECT,
            requires_review=False,
            **{**VERDICT_BASE, "reasons": ("NOT_A_REASON",)},
        )
    with pytest.raises(MalformedVerdict):
        P8Verdict(
            outcome=ACCEPT_DIRECT,
            requires_review=False,
            **{**VERDICT_BASE, "scope": "invented_scope"},
        )


def test_p8_verdict_accepts_a_registered_reason():
    verdict = P8Verdict(
        outcome=ACCEPT_DIRECT,
        requires_review=False,
        **{**VERDICT_BASE, "reasons": (SCHEMA_INVALID,)},
    )
    assert verdict.reasons == (SCHEMA_INVALID,)
    assert SCHEMA_INVALID in ALL_REASON_CODES


def test_grounding_report_carries_the_spec_measurement_fields():
    report = GroundingReport(
        dossier_id="dossier-1",
        call_site=A_FACT,
        model_id="fixture-model",
        prompt_fingerprint="fp",
        validator_version="P8/0.1.0",
        citations_total=1,
        citations_resolved=1,
        citations_span_matched=1,
        claims_total=1,
        claims_abstained=0,
        claims_accepted_direct=1,
        claims_accepted_context=0,
        claims_weak=0,
        claims_rejected=0,
        reasons_histogram={SCHEMA_INVALID: 0},
        reduction_rung=REDUCTION_NONE,
        release_audit_id=17,
        dossier_builder="fixture",
    )
    assert report.__dataclass_params__.frozen
    assert _field_names(GroundingReport) == (
        "dossier_id",
        "call_site",
        "model_id",
        "prompt_fingerprint",
        "validator_version",
        "citations_total",
        "citations_resolved",
        "citations_span_matched",
        "claims_total",
        "claims_abstained",
        "claims_accepted_direct",
        "claims_accepted_context",
        "claims_weak",
        "claims_rejected",
        "reasons_histogram",
        "reduction_rung",
        "release_audit_id",
        "dossier_builder",
    )
    assert report.release_audit_id == 17
    with pytest.raises((MalformedRecord, ValueError)):
        GroundingReport(
            dossier_id="dossier-1",
            call_site=A_FACT,
            model_id="fixture-model",
            prompt_fingerprint="fp",
            validator_version="P8/0.1.0",
            citations_total=0,
            citations_resolved=0,
            citations_span_matched=0,
            claims_total=0,
            claims_abstained=0,
            claims_accepted_direct=0,
            claims_accepted_context=0,
            claims_weak=0,
            claims_rejected=0,
            reasons_histogram={},
            reduction_rung="invented_rung",
            release_audit_id=None,
            dossier_builder="fixture",
        )


def test_refusal_is_gate_only_and_constructed_from_denied():
    denied = _denied()
    refusal = Refusal(denied=denied)
    assert refusal.__dataclass_params__.frozen
    assert _field_names(Refusal) == ("denied",)
    assert refusal.denied is denied
    assert refusal.reason == PRIVACY_GATE_REFUSED
    assert refusal.explanation == denied.explanation
    assert refusal.denial_reason == denied.reason
    assert not isinstance(refusal, NeedsConsent)
    with pytest.raises(MalformedRecord):
        Refusal(denied="not-a-denied")  # type: ignore[arg-type]


def test_pre_call_abstention_uses_a_pre_call_reason_code():
    abstention = PreCallAbstention(
        reason=NOT_ELIGIBLE_FOR_MODEL,
        call_site=A_FACT,
        subject_ref="file-1",
    )
    assert abstention.__dataclass_params__.frozen
    assert _field_names(PreCallAbstention) == ("reason", "call_site", "subject_ref")
    PreCallAbstention(
        reason=BUDGET_EXHAUSTED, call_site=A_FACT, subject_ref="file-1",
    )
    with pytest.raises(MalformedRecord):
        PreCallAbstention(
            reason=SCHEMA_INVALID, call_site=A_FACT, subject_ref="file-1",
        )


def test_call_failed_carries_request_and_release_identity():
    failed = CallFailed(
        request_identity="fingerprint.grouping",
        release_id="rel-1",
        audit_id=17,
        explanation="client raised",
    )
    assert failed.__dataclass_params__.frozen
    assert _field_names(CallFailed) == (
        "request_identity", "release_id", "audit_id", "explanation",
    )
    missing_audit = CallFailed(
        request_identity="fingerprint.grouping",
        release_id="rel-1",
        audit_id=None,
        explanation="unknown audit",
    )
    assert missing_audit.audit_id is None


def test_call_result_holds_a_p8_branch_and_not_consent():
    verdict = P8Verdict(
        outcome=ACCEPT_DIRECT, requires_review=False, **VERDICT_BASE,
    )
    result = CallResult(value=verdict)
    assert result.__dataclass_params__.frozen
    assert _field_names(CallResult) == ("value",)
    CallResult(value=Refusal(denied=_denied()))
    CallResult(value=PreCallAbstention(
        reason=NOT_ELIGIBLE_FOR_MODEL, call_site=A_FACT, subject_ref="file-1",
    ))
    CallResult(value=CallFailed(
        request_identity="fp", release_id="rel-1", audit_id=None, explanation="x",
    ))
    needs = NeedsConsent(
        consent_request_id="consent-1",
        requirement=ConsentRequirement(
            file_ids=("file-1",),
            handling_class="public_low",
            items=(("obs-key-1", "0:4"),),
            why="sensitive text",
        ),
    )
    with pytest.raises(MalformedRecord):
        CallResult(value=needs)  # type: ignore[arg-type]
    assert "needs_consent" not in OUTCOMES


def test_validation_unavailable_names_missing_capabilities_and_is_not_abstain():
    unavailable = ValidationUnavailable(missing=("normalize", "contradicts"))
    assert unavailable.__dataclass_params__.frozen
    assert _field_names(ValidationUnavailable) == ("missing",)
    assert unavailable.missing == ("normalize", "contradicts")
    assert ABSTAIN not in unavailable.missing
    assert unavailable.missing != (ABSTAIN,)
    with pytest.raises(MalformedRecord):
        ValidationUnavailable(missing=())


def test_dossier_request_rejects_bare_string_evidence_refs():
    with pytest.raises(MalformedRecord):
        DossierRequest(
            call_site=A_FACT,
            subject_ref="file-1",
            eligibility_reason=REMAINS_AMBIGUOUS,
            evidence_refs="obs-key-1",
            model_call_request=_model_call_request(),
            plan_version=None,
            evidence_snapshot_id="snap-1",
            budget_context="scan-1",
        )


def test_dossier_request_freezes_evidence_refs_against_caller_mutation():
    refs = ["obs-key-1"]
    request = DossierRequest(
        call_site=A_FACT,
        subject_ref="file-1",
        eligibility_reason=REMAINS_AMBIGUOUS,
        evidence_refs=refs,
        model_call_request=_model_call_request(),
        plan_version=None,
        evidence_snapshot_id="snap-1",
        budget_context="scan-1",
    )
    refs.append("mutated")
    assert request.evidence_refs == ("obs-key-1",)
    assert isinstance(request.evidence_refs, tuple)


def test_validation_unavailable_rejects_bare_string_missing():
    with pytest.raises(MalformedRecord):
        ValidationUnavailable(missing="normalize")


def test_dossier_request_requires_plan_version_at_placement():
    with pytest.raises(MalformedRecord):
        DossierRequest(
            call_site=C_PLACEMENT,
            subject_ref="file-1",
            eligibility_reason="several_legal_nodes_plausible",
            evidence_refs=(),
            model_call_request=_model_call_request(),
            plan_version=None,
            evidence_snapshot_id=None,
            budget_context=None,
        )


def test_evidence_item_rejects_unknown_reliability_state_as_malformed_record():
    with pytest.raises(MalformedRecord):
        EvidenceItem(
            evidence_ref="obs-key-1",
            kind="excerpt",
            location="body",
            excerpt_span=(0, 4),
            reliability_state="invented",
            basis=DIRECT_ANCHOR,
        )
