"""Universal deterministic validation: one recorded-bytes fixture per reason/outcome."""
from __future__ import annotations

import dataclasses
from collections.abc import Mapping

import pytest

import llm_harness
from evidence_shape.canonical import canonical_json
from llm_harness.authorship import COMPONENT_VERSION
from llm_harness.records import (
    ReleasedEvidence,
    Conflict,
    Dossier,
    EvidenceItem,
    P8Verdict,
    ValidationUnavailable,
)
from llm_harness.validation import validate_response
from llm_harness.vocabulary import (
    A_FACT,
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    CITATION_NOT_FOUND,
    CITATION_NOT_IN_DOSSIER,
    CITATION_SPAN_MISMATCH,
    CONTEXT_SUPPORTED,
    CONTRADICTED_BY_STRONGER,
    DIRECT_ANCHOR,
    REDUCTION_NONE,
    REMAINS_AMBIGUOUS,
    SCHEMA_INVALID,
    SEARCH_HINT_ONLY,
    UNCITED_CLAIM,
    WEAK,
)

# Recorded response bytes. Later site validators reuse this shape:
# {"claims":[{"claim_ref": str, "payload": object,
#             "citations": [{"evidence_ref", "cited_span"|"metadata_field_name",
#                            "why_it_supports"}] | [],
#             "unknown": {"insufficiency_statement"} | omitted}]}
DIRECT_BYTES = (
    b'{"claims":[{"claim_ref":"c1","payload":{"field":"school","value":"Columbia"},'
    b'"citations":[{"evidence_ref":"obs-key-1","cited_span":"Columbia University",'
    b'"why_it_supports":"names the school"}]}]}'
)
UNKNOWN_BYTES = (
    b'{"claims":[{"claim_ref":"c1","payload":{},'
    b'"unknown":{"insufficiency_statement":"no labeled school"}}]}'
)
UNCITED_BYTES = (
    b'{"claims":[{"claim_ref":"c1","payload":{"field":"school","value":"Columbia"},'
    b'"citations":[]}]}'
)
OUTSIDE_BYTES = (
    b'{"claims":[{"claim_ref":"c1","payload":{"field":"school","value":"Columbia"},'
    b'"citations":[{"evidence_ref":"obs-outside","cited_span":"Columbia University",'
    b'"why_it_supports":"names the school"}]}]}'
)
NOT_FOUND_BYTES = DIRECT_BYTES
SPAN_MISMATCH_BYTES = (
    b'{"claims":[{"claim_ref":"c1","payload":{"field":"school","value":"Columbia"},'
    b'"citations":[{"evidence_ref":"obs-key-1","cited_span":"RAW SECRET TEXT",'
    b'"why_it_supports":"names the school"}]}]}'
)
MALFORMED_BYTES = b"{not-json"

RELEASED_MATERIAL = "Columbia University — redacted dossier excerpt"
RAW_STORE_TEXT = "RAW SECRET TEXT Columbia University confidential"


def _evidence(basis: str = DIRECT_ANCHOR, ref: str = "obs-key-1") -> EvidenceItem:
    return EvidenceItem(
        evidence_ref=ref,
        kind="excerpt",
        location="body",
        excerpt_span=(0, 4),
        reliability_state="direct",
        basis=basis,
    )


def _released(ref: str = "obs-key-1", *,
              value: str = RELEASED_MATERIAL) -> ReleasedEvidence:
    return ReleasedEvidence(
        observation_key=ref,
        address="0:4",
        value=value,
        zone="body",
        context_before=None,
        context_after=None,
        context_truncated=False,
    )


def _dossier(*, basis: str = DIRECT_ANCHOR, extra_items=(),
             released_evidence=None) -> Dossier:
    if released_evidence is None:
        released_evidence = (_released(),) + tuple(
            _released(item.evidence_ref) for item in extra_items
        )
    return Dossier(
        dossier_id="dossier-1",
        call_site=A_FACT,
        subject_ref="file-1",
        eligibility_reason=REMAINS_AMBIGUOUS,
        plan_version=None,
        policy_version="policy-1",
        allowed_vocabulary=("school",),
        evidence_items=(_evidence(basis=basis),) + tuple(extra_items),
        conflicts=(Conflict(conflict_id="c1", kind="stronger_fact"),),
        released_evidence=tuple(released_evidence),
        max_dossier_tokens=4000,
        reduction_rung=REDUCTION_NONE,
        release_id="rel-1",
    )


def _resolver(released: str = RELEASED_MATERIAL, found: frozenset[str] | None = None):
    keys = found if found is not None else frozenset({"obs-key-1"})

    def resolve(observation_key: str) -> str | None:
        if observation_key in keys:
            return released
        return None

    return resolve


def _noop_site(*_a, **_k):
    return None


def _never_contradicts(*_a, **_k):
    return False


def _validate(dossier, response_bytes, *, evidence_resolver=None, site_validator=None,
              contradicts=None, **kwargs):
    return validate_response(
        dossier,
        response_bytes,
        evidence_resolver=evidence_resolver if evidence_resolver is not None else _resolver(),
        site_validator=site_validator if site_validator is not None else _noop_site,
        contradicts=contradicts if contradicts is not None else _never_contradicts,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        dossier_builder="fixture",
        release_audit_id=17,
        **kwargs,
    )


def _jsonable(value):
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _jsonable(getattr(value, field.name))
            for field in dataclasses.fields(value)
        }
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def test_public_surface_is_unchanged_and_validation_is_not_exported():
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
    assert not hasattr(llm_harness, "validate_response")


def test_malformed_schema_rejects_with_schema_invalid():
    verdicts, report = _validate(_dossier(), MALFORMED_BYTES)
    assert len(verdicts) == 1
    assert verdicts[0].outcome == "reject"
    assert verdicts[0].reasons == (SCHEMA_INVALID,)
    assert report.claims_rejected == 1
    assert report.claims_total == 1
    assert report.reasons_histogram[SCHEMA_INVALID] == 1
    assert report.citations_total == 0


def test_uncited_claim_is_rejected_not_softened():
    verdicts, report = _validate(_dossier(), UNCITED_BYTES)
    assert verdicts[0].outcome == "reject"
    assert verdicts[0].reasons == (UNCITED_CLAIM,)
    assert verdicts[0].may_propose is False
    assert report.claims_rejected == 1
    assert report.claims_accepted_direct == 0
    assert report.reasons_histogram[UNCITED_CLAIM] == 1


def test_citation_outside_dossier_is_rejected():
    verdicts, report = _validate(_dossier(), OUTSIDE_BYTES)
    assert verdicts[0].outcome == "reject"
    assert CITATION_NOT_IN_DOSSIER in verdicts[0].reasons
    assert report.reasons_histogram[CITATION_NOT_IN_DOSSIER] == 1
    checked = verdicts[0].citations_checked
    assert checked[0].citation_ref == "obs-outside"
    assert checked[0].resolved is False


def test_unresolved_observation_key_is_not_found():
    verdicts, report = _validate(
        _dossier(),
        NOT_FOUND_BYTES,
        evidence_resolver=_resolver(found=frozenset()),
    )
    assert verdicts[0].outcome == "reject"
    assert CITATION_NOT_FOUND in verdicts[0].reasons
    assert report.reasons_histogram[CITATION_NOT_FOUND] == 1
    assert verdicts[0].citations_checked[0].resolved is False
    assert verdicts[0].citations_checked[0].citation_ref == "obs-key-1"


def test_span_absent_from_released_material_mismatches():
    verdicts, report = _validate(_dossier(), SPAN_MISMATCH_BYTES)
    assert verdicts[0].outcome == "reject"
    assert CITATION_SPAN_MISMATCH in verdicts[0].reasons
    assert report.reasons_histogram[CITATION_SPAN_MISMATCH] == 1
    assert verdicts[0].citations_checked[0].resolved is True
    assert verdicts[0].citations_checked[0].span_matched is False


def test_span_matches_released_material_not_raw_store_text():
    # Resolver returns redacted material. The raw SQLite string is never consulted.
    def resolve(observation_key: str) -> str | None:
        assert RAW_STORE_TEXT not in RELEASED_MATERIAL
        if observation_key == "obs-key-1":
            return RELEASED_MATERIAL
        return None

    verdicts, report = _validate(
        _dossier(), DIRECT_BYTES, evidence_resolver=resolve,
    )
    assert verdicts[0].outcome == ACCEPT_DIRECT
    assert verdicts[0].citations_checked[0].span_matched is True
    assert report.citations_span_matched == 1

    mismatched, mismatch_report = _validate(
        _dossier(), SPAN_MISMATCH_BYTES, evidence_resolver=resolve,
    )
    assert mismatched[0].outcome == "reject"
    assert CITATION_SPAN_MISMATCH in mismatched[0].reasons
    assert mismatch_report.citations_span_matched == 0


def test_citations_resolve_by_p4_observation_key():
    verdicts, report = _validate(_dossier(), DIRECT_BYTES)
    assert verdicts[0].citations_checked[0].citation_ref == "obs-key-1"
    assert verdicts[0].citations_checked[0].resolved is True
    assert report.citations_resolved == 1


def test_stronger_contradiction_from_injected_oracle():
    verdicts, report = _validate(
        _dossier(), DIRECT_BYTES, contradicts=lambda *_a, **_k: True,
    )
    assert verdicts[0].outcome == "reject"
    assert CONTRADICTED_BY_STRONGER in verdicts[0].reasons
    assert report.reasons_histogram[CONTRADICTED_BY_STRONGER] == 1
    assert report.claims_rejected == 1


def test_omitted_contradiction_oracle_is_unavailable_when_check_four_is_needed():
    result = validate_response(
        _dossier(),
        DIRECT_BYTES,
        evidence_resolver=_resolver(),
        site_validator=_noop_site,
        contradicts=None,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        dossier_builder="fixture",
        release_audit_id=17,
    )
    assert isinstance(result, ValidationUnavailable)
    assert "contradicts" in result.missing


def test_contradicts_none_does_not_fall_back_to_resolver_attribute():
    class CombinedResolver:
        def __init__(self) -> None:
            self.contradicts = lambda *_a, **_k: False

        def __call__(self, observation_key: str) -> str | None:
            if observation_key == "obs-key-1":
                return RELEASED_MATERIAL
            return None

    result = validate_response(
        _dossier(),
        DIRECT_BYTES,
        evidence_resolver=CombinedResolver(),
        site_validator=_noop_site,
        contradicts=None,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        dossier_builder="fixture",
        release_audit_id=17,
    )
    assert isinstance(result, ValidationUnavailable)
    assert result.missing == ("contradicts",)


def test_an_empty_released_value_matches_nothing_whatever_the_store_returns():
    """R4: the released value is the span source. An empty release grounds nothing."""
    def resolve(observation_key: str) -> Mapping[str, object] | None:
        if observation_key == "obs-key-1":
            return {"text": "Columbia University", "released": "extra secret"}
        return None

    dossier = _dossier(released_evidence=(_released(value=""),))
    verdicts, report = _validate(dossier, DIRECT_BYTES, evidence_resolver=resolve)
    assert verdicts[0].outcome != ACCEPT_DIRECT
    assert verdicts[0].outcome == "reject"
    assert CITATION_SPAN_MISMATCH in verdicts[0].reasons
    assert report.claims_accepted_direct == 0
    assert verdicts[0].citations_checked[0].span_matched is False


def test_raw_store_material_cannot_rescue_a_span_the_release_does_not_carry():
    """R4: whatever shape the store answers in, it answers presence only."""
    class RawRow:
        def __str__(self) -> str:
            return "RAW SECRET TEXT Columbia University confidential"

    def resolve(observation_key: str) -> object:
        if observation_key == "obs-key-1":
            return RawRow()
        return None

    dossier = _dossier(released_evidence=(_released(value="[REDACTED] excerpt"),))
    verdicts, _report = validate_response(
        dossier,
        DIRECT_BYTES,
        evidence_resolver=resolve,
        site_validator=_noop_site,
        contradicts=_never_contradicts,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        dossier_builder="fixture",
        release_audit_id=17,
    )
    assert verdicts[0].outcome == "reject"
    assert verdicts[0].reasons == (CITATION_SPAN_MISMATCH,)


def test_numeric_cited_span_is_schema_invalid():
    numeric_span = (
        b'{"claims":[{"claim_ref":"c1","payload":{"field":"school","value":"Columbia"},'
        b'"citations":[{"evidence_ref":"obs-key-1","cited_span":123,'
        b'"why_it_supports":"names the school"}]}]}'
    )
    verdicts, report = _validate(_dossier(), numeric_span)
    assert verdicts[0].outcome == "reject"
    assert verdicts[0].reasons == (SCHEMA_INVALID,)
    assert report.reasons_histogram[SCHEMA_INVALID] == 1
    assert report.claims_rejected == 1


def test_explicit_unknown_abstains_and_is_not_a_failure():
    verdicts, report = _validate(_dossier(), UNKNOWN_BYTES)
    assert verdicts[0].outcome == ABSTAIN
    assert verdicts[0].reasons == ()
    assert verdicts[0].may_propose is False
    assert report.claims_abstained == 1
    assert report.claims_rejected == 0
    assert report.claims_total == 1
    assert SCHEMA_INVALID not in report.reasons_histogram
    assert UNCITED_CLAIM not in report.reasons_histogram


def test_direct_acceptance_requires_direct_anchor_evidence():
    verdicts, report = _validate(_dossier(basis=DIRECT_ANCHOR), DIRECT_BYTES)
    assert verdicts[0].outcome == ACCEPT_DIRECT
    assert verdicts[0].requires_review is False
    assert verdicts[0].may_propose is True
    assert verdicts[0].validator_version == COMPONENT_VERSION
    assert report.claims_accepted_direct == 1
    assert report.claims_accepted_context == 0
    assert report.citations_total == 1
    assert report.citations_resolved == 1
    assert report.citations_span_matched == 1
    assert report.release_audit_id == 17


def test_context_acceptance_always_requires_review():
    verdicts, report = _validate(
        _dossier(basis=CONTEXT_SUPPORTED), DIRECT_BYTES,
    )
    assert verdicts[0].outcome == ACCEPT_CONTEXT_SUPPORTED
    assert verdicts[0].requires_review is True
    assert report.claims_accepted_context == 1
    assert report.claims_accepted_direct == 0


def test_weak_forbids_may_propose():
    def make_weak(dossier, claim, verdict: P8Verdict) -> P8Verdict:
        return P8Verdict(
            verdict_id=verdict.verdict_id,
            dossier_id=verdict.dossier_id,
            claim_ref=verdict.claim_ref,
            outcome=WEAK,
            disposition="possible",
            reasons=(SEARCH_HINT_ONLY,),
            may_propose=False,
            requires_review=False,
            citations_checked=verdict.citations_checked,
            scope=verdict.scope,
            validator_version=verdict.validator_version,
            policy_version=verdict.policy_version,
            plan_version=verdict.plan_version,
        )

    verdicts, report = _validate(
        _dossier(), DIRECT_BYTES, site_validator=make_weak,
    )
    assert verdicts[0].outcome == WEAK
    assert verdicts[0].may_propose is False
    assert SEARCH_HINT_ONLY in verdicts[0].reasons
    assert report.claims_weak == 1
    assert report.claims_accepted_direct == 0


def test_omitting_site_validator_fails_closed():
    with pytest.raises(TypeError):
        validate_response(
            _dossier(),
            DIRECT_BYTES,
            evidence_resolver=_resolver(),
            contradicts=_never_contradicts,
            model_id="fixture-model",
            prompt_fingerprint="fp-canonical",
            dossier_builder="fixture",
            release_audit_id=17,
        )


def test_validation_is_byte_identical_across_one_hundred_runs():
    dossier = _dossier()
    first_verdicts, first_report = _validate(dossier, DIRECT_BYTES)
    first_v = canonical_json(_jsonable(first_verdicts))
    first_r = canonical_json(_jsonable(first_report)).encode("utf-8")
    for _ in range(100):
        verdicts, report = _validate(dossier, DIRECT_BYTES)
        assert canonical_json(_jsonable(verdicts)) == first_v
        assert canonical_json(_jsonable(report)).encode("utf-8") == first_r


def test_response_bytes_are_not_round_tripped():
    raw = DIRECT_BYTES + b""
    _validate(_dossier(), raw)
    assert raw == DIRECT_BYTES
