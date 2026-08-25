# src/llm_harness/validation.py
"""Universal deterministic validation and grounding-report construction.

Parse JSON once, keep the raw response bytes untouched, and check claims in
input order. No model is consulted. Contradiction is an injected oracle; this
module does not implement domain contradiction or normalization.

Recorded response shape (stable; later site validators reuse it)::

    {"claims": [
        {"claim_ref": str,                 # optional; default claim-<index>
         "payload": object,
         "citations": [
             {"evidence_ref": str,         # P4 observation_key
              "cited_span": str | None,
              "metadata_field_name": str | None,
              "why_it_supports": str}
         ],
         "unknown": {"insufficiency_statement": str}}
    ]}

Exactly one of a non-empty ``citations`` list or ``unknown`` is valid.
"""
from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from llm_harness.authorship import COMPONENT_VERSION
from llm_harness.records import (
    CallFailed,
    CheckedCitation,
    Citation,
    Dossier,
    DossierRequest,
    GroundingReport,
    MalformedRecord,
    P8Verdict,
    PreCallAbstention,
    Refusal,
    Unknown,
    ValidationUnavailable,
)
from llm_harness.vocabulary import (
    A_FACT,
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    B_GROUP,
    BUDGET_EXHAUSTED,
    C_PLACEMENT,
    CITATION_NOT_FOUND,
    CITATION_NOT_IN_DOSSIER,
    CITATION_SPAN_MISMATCH,
    CONTEXT_SUPPORTED,
    CONTRADICTED_BY_STRONGER,
    D_RESIDUAL,
    DEFERRED,
    E_TEMPLATE,
    LLM_SUPPORTED,
    LLM_SUPPORTED_REVIEW,
    POSSIBLE,
    REDUCTION_NONE,
    REJECT,
    REJECTED,
    SCHEMA_INVALID,
    SCOPE_FILE,
    SCOPE_GROUP,
    SCOPE_NODE,
    SCOPE_TEMPLATE,
    UNCITED_CLAIM,
    WEAK,
)

#: Tag for reports this module constructs when no neighbour built a dossier.
DOSSIER_BUILDER = "p8"

_SCOPE_BY_SITE = {
    A_FACT: SCOPE_FILE,
    B_GROUP: SCOPE_GROUP,
    C_PLACEMENT: SCOPE_NODE,
    D_RESIDUAL: SCOPE_FILE,
    E_TEMPLATE: SCOPE_TEMPLATE,
}

_DISPOSITION_BY_OUTCOME = {
    ACCEPT_DIRECT: LLM_SUPPORTED,
    ACCEPT_CONTEXT_SUPPORTED: LLM_SUPPORTED_REVIEW,
    WEAK: POSSIBLE,
    REJECT: REJECTED,
    ABSTAIN: ABSTAIN,
}

_ZERO_COUNTS = dict(
    citations_total=0,
    citations_resolved=0,
    citations_span_matched=0,
    claims_total=0,
    claims_abstained=0,
    claims_accepted_direct=0,
    claims_accepted_context=0,
    claims_weak=0,
    claims_rejected=0,
)


def _released_view(resolved: object) -> Mapping[str, object] | None:
    if isinstance(resolved, str):
        return {"text": resolved, "metadata": {}}
    if isinstance(resolved, Mapping) and "text" in resolved:
        text = resolved["text"]
        if not isinstance(text, str):
            return None
        metadata = resolved.get("metadata")
        if not isinstance(metadata, Mapping):
            metadata = {}
        return {"text": text, "metadata": metadata}
    return None


def _parse_citation(raw: object) -> Citation | None:
    if not isinstance(raw, Mapping):
        return None
    cited_span = raw.get("cited_span")
    metadata_field_name = raw.get("metadata_field_name")
    if cited_span is not None and not isinstance(cited_span, str):
        return None
    if metadata_field_name is not None and not isinstance(metadata_field_name, str):
        return None
    try:
        return Citation(
            evidence_ref=str(raw.get("evidence_ref") or ""),
            cited_span=cited_span,
            metadata_field_name=metadata_field_name,
            why_it_supports=str(raw.get("why_it_supports") or ""),
        )
    except (MalformedRecord, TypeError, ValueError):
        return None


def _check_citation(
    citation: Citation,
    dossier: Dossier,
    evidence_resolver: Callable[[str], object],
) -> tuple[CheckedCitation, str | None] | ValidationUnavailable:
    refs = {item.evidence_ref for item in dossier.evidence_items}
    if citation.evidence_ref not in refs:
        return (
            CheckedCitation(citation.evidence_ref, False, False),
            CITATION_NOT_IN_DOSSIER,
        )
    resolved = evidence_resolver(citation.evidence_ref)
    if resolved is None:
        return (
            CheckedCitation(citation.evidence_ref, False, False),
            CITATION_NOT_FOUND,
        )
    view = _released_view(resolved)
    if view is None:
        return ValidationUnavailable(missing=("evidence_resolver",))
    text = view["text"]
    if not isinstance(text, str):
        return ValidationUnavailable(missing=("evidence_resolver",))
    if citation.cited_span is not None:
        matched = citation.cited_span in text
    else:
        metadata = view["metadata"]
        matched = isinstance(metadata, Mapping) and citation.metadata_field_name in metadata
    if not matched:
        return (
            CheckedCitation(citation.evidence_ref, True, False),
            CITATION_SPAN_MISMATCH,
        )
    return CheckedCitation(citation.evidence_ref, True, True), None


def _make_verdict(
    *,
    dossier: Dossier,
    claim_ref: str,
    outcome: str,
    reasons: Sequence[str],
    may_propose: bool,
    requires_review: bool,
    citations_checked: Sequence[CheckedCitation],
) -> P8Verdict:
    return P8Verdict(
        verdict_id=f"{dossier.dossier_id}:{claim_ref}",
        dossier_id=dossier.dossier_id,
        claim_ref=claim_ref,
        outcome=outcome,
        disposition=_DISPOSITION_BY_OUTCOME[outcome],
        reasons=tuple(reasons),
        may_propose=may_propose,
        requires_review=requires_review,
        citations_checked=tuple(citations_checked),
        scope=_SCOPE_BY_SITE[dossier.call_site],
        validator_version=COMPONENT_VERSION,
        policy_version=dossier.policy_version,
        plan_version=dossier.plan_version,
    )


def _schema_invalid_verdict(dossier: Dossier, claim_ref: str = "schema") -> P8Verdict:
    return _make_verdict(
        dossier=dossier,
        claim_ref=claim_ref,
        outcome=REJECT,
        reasons=(SCHEMA_INVALID,),
        may_propose=False,
        requires_review=False,
        citations_checked=(),
    )


def _report_from_verdicts(
    dossier: Dossier,
    verdicts: Sequence[P8Verdict],
    *,
    model_id: str,
    prompt_fingerprint: str,
    dossier_builder: str,
    release_audit_id: int | None,
) -> GroundingReport:
    checked = [item for verdict in verdicts for item in verdict.citations_checked]
    histogram: dict[str, int] = {}
    for verdict in verdicts:
        for reason in verdict.reasons:
            histogram[reason] = histogram.get(reason, 0) + 1
    return GroundingReport(
        dossier_id=dossier.dossier_id,
        call_site=dossier.call_site,
        model_id=model_id,
        prompt_fingerprint=prompt_fingerprint,
        validator_version=COMPONENT_VERSION,
        citations_total=len(checked),
        citations_resolved=sum(1 for item in checked if item.resolved),
        citations_span_matched=sum(1 for item in checked if item.span_matched),
        claims_total=len(verdicts),
        claims_abstained=sum(1 for verdict in verdicts if verdict.outcome == ABSTAIN),
        claims_accepted_direct=sum(
            1 for verdict in verdicts if verdict.outcome == ACCEPT_DIRECT
        ),
        claims_accepted_context=sum(
            1 for verdict in verdicts if verdict.outcome == ACCEPT_CONTEXT_SUPPORTED
        ),
        claims_weak=sum(1 for verdict in verdicts if verdict.outcome == WEAK),
        claims_rejected=sum(1 for verdict in verdicts if verdict.outcome == REJECT),
        reasons_histogram=histogram,
        reduction_rung=dossier.reduction_rung,
        release_audit_id=release_audit_id,
        dossier_builder=dossier_builder,
    )


def _zero_report(
    request: DossierRequest,
    *,
    validator_version: str,
    reasons_histogram: Mapping[str, int],
    reduction_rung: str,
    release_audit_id: int | None,
    dossier_id: str,
) -> GroundingReport:
    return GroundingReport(
        dossier_id=dossier_id,
        call_site=request.call_site,
        model_id=request.model_call_request.model_target.model_id,
        prompt_fingerprint=request.model_call_request.prompt_fingerprint,
        validator_version=validator_version,
        reasons_histogram=dict(reasons_histogram),
        reduction_rung=reduction_rung,
        release_audit_id=release_audit_id,
        dossier_builder=DOSSIER_BUILDER,
        **_ZERO_COUNTS,
    )


def _acceptance_outcome(dossier: Dossier, citations: Sequence[Citation]) -> str:
    cited_refs = {item.evidence_ref for item in citations}
    bases = [
        item.basis for item in dossier.evidence_items if item.evidence_ref in cited_refs
    ]
    if bases and all(basis == CONTEXT_SUPPORTED for basis in bases):
        return ACCEPT_CONTEXT_SUPPORTED
    return ACCEPT_DIRECT


def _validate_claim(
    dossier: Dossier,
    raw: object,
    index: int,
    *,
    evidence_resolver: Callable[[str], object],
    site_validator: Callable[..., Any],
    oracle: Callable[..., Any] | None,
) -> P8Verdict | ValidationUnavailable:
    claim_ref = f"claim-{index}"
    if not isinstance(raw, Mapping):
        return _schema_invalid_verdict(dossier, claim_ref)
    if raw.get("claim_ref"):
        claim_ref = str(raw["claim_ref"])
    payload = raw.get("payload")
    if payload is None:
        payload = {}
    if not isinstance(payload, Mapping):
        return _schema_invalid_verdict(dossier, claim_ref)

    unknown_raw = raw.get("unknown")
    citations_raw = raw.get("citations")
    has_unknown = unknown_raw is not None
    if has_unknown:
        if not isinstance(unknown_raw, Mapping):
            return _schema_invalid_verdict(dossier, claim_ref)
        try:
            unknown = Unknown(
                insufficiency_statement=str(
                    unknown_raw.get("insufficiency_statement") or ""
                ),
            )
        except (MalformedRecord, TypeError, ValueError):
            return _schema_invalid_verdict(dossier, claim_ref)
        del unknown
        if isinstance(citations_raw, Sequence) and not isinstance(
            citations_raw, (str, bytes),
        ) and len(citations_raw) > 0:
            return _schema_invalid_verdict(dossier, claim_ref)
        return _make_verdict(
            dossier=dossier,
            claim_ref=claim_ref,
            outcome=ABSTAIN,
            reasons=(),
            may_propose=False,
            requires_review=False,
            citations_checked=(),
        )

    if citations_raw is None or citations_raw == []:
        return _make_verdict(
            dossier=dossier,
            claim_ref=claim_ref,
            outcome=REJECT,
            reasons=(UNCITED_CLAIM,),
            may_propose=False,
            requires_review=False,
            citations_checked=(),
        )
    if not isinstance(citations_raw, Sequence) or isinstance(citations_raw, (str, bytes)):
        return _schema_invalid_verdict(dossier, claim_ref)

    citations: list[Citation] = []
    for item in citations_raw:
        parsed = _parse_citation(item)
        if parsed is None:
            return _schema_invalid_verdict(dossier, claim_ref)
        citations.append(parsed)
    if not citations:
        return _make_verdict(
            dossier=dossier,
            claim_ref=claim_ref,
            outcome=REJECT,
            reasons=(UNCITED_CLAIM,),
            may_propose=False,
            requires_review=False,
            citations_checked=(),
        )

    checked: list[CheckedCitation] = []
    reasons: list[str] = []
    for citation in citations:
        checked_result = _check_citation(citation, dossier, evidence_resolver)
        if isinstance(checked_result, ValidationUnavailable):
            return checked_result
        item, reason = checked_result
        checked.append(item)
        if reason is not None:
            reasons.append(reason)

    if reasons:
        return _make_verdict(
            dossier=dossier,
            claim_ref=claim_ref,
            outcome=REJECT,
            reasons=reasons,
            may_propose=False,
            requires_review=False,
            citations_checked=checked,
        )

    if oracle is None:
        return ValidationUnavailable(missing=("contradicts",))
    if oracle(payload, dossier):
        return _make_verdict(
            dossier=dossier,
            claim_ref=claim_ref,
            outcome=REJECT,
            reasons=(CONTRADICTED_BY_STRONGER,),
            may_propose=False,
            requires_review=False,
            citations_checked=checked,
        )

    outcome = _acceptance_outcome(dossier, citations)
    verdict = _make_verdict(
        dossier=dossier,
        claim_ref=claim_ref,
        outcome=outcome,
        reasons=(),
        may_propose=True,
        requires_review=outcome == ACCEPT_CONTEXT_SUPPORTED,
        citations_checked=checked,
    )
    replacement = site_validator(dossier, raw, verdict)
    if replacement is not None:
        return replacement
    return verdict


def validate_response(
    dossier: Dossier,
    response_bytes: bytes,
    *,
    evidence_resolver,
    site_validator,
    contradicts,
    model_id: str,
    prompt_fingerprint: str,
    dossier_builder: str,
    release_audit_id: int | None,
) -> tuple[tuple[P8Verdict, ...], GroundingReport] | ValidationUnavailable:
    """Validate recorded response bytes against a released dossier.

    ``evidence_resolver`` maps a P4 ``observation_key`` to the released/redacted
    material the model saw, or ``None`` if that key was not shown.
    ``contradicts`` is the injected contradiction oracle; passing ``None`` when a
    cited claim needs that check is ``ValidationUnavailable``, not a pass.
    """
    missing: list[str] = []
    if evidence_resolver is None:
        missing.append("evidence_resolver")
    if site_validator is None:
        missing.append("site_validator")
    if missing:
        return ValidationUnavailable(missing=tuple(missing))

    oracle = contradicts

    def _finished(verdicts: Sequence[P8Verdict]):
        return (
            tuple(verdicts),
            _report_from_verdicts(
                dossier,
                verdicts,
                model_id=model_id,
                prompt_fingerprint=prompt_fingerprint,
                dossier_builder=dossier_builder,
                release_audit_id=release_audit_id,
            ),
        )

    try:
        parsed = json.loads(response_bytes)
    except (ValueError, TypeError, UnicodeDecodeError):
        return _finished((_schema_invalid_verdict(dossier),))

    if not isinstance(parsed, Mapping) or not isinstance(parsed.get("claims"), list):
        return _finished((_schema_invalid_verdict(dossier),))

    verdicts: list[P8Verdict] = []
    for index, raw in enumerate(parsed["claims"]):
        result = _validate_claim(
            dossier,
            raw,
            index,
            evidence_resolver=evidence_resolver,
            site_validator=site_validator,
            oracle=oracle,
        )
        if isinstance(result, ValidationUnavailable):
            return result
        verdicts.append(result)
    return _finished(verdicts)


def report_for_pre_call_terminal(
    request: DossierRequest,
    terminal: Refusal | PreCallAbstention,
    *,
    validator_version: str,
) -> GroundingReport:
    """Zero-count report for a pre-egress Refusal or PreCallAbstention.

    Derived solely from the immutable request and terminal. ``NeedsConsent`` is
    not a terminal and emits neither a report nor an event.
    """
    if not isinstance(terminal, (Refusal, PreCallAbstention)):
        raise TypeError(
            "NeedsConsent emits neither report nor event; "
            "report_for_pre_call_terminal requires Refusal or PreCallAbstention"
        )
    reason = terminal.reason
    rung = DEFERRED if reason == BUDGET_EXHAUSTED else REDUCTION_NONE
    return _zero_report(
        request,
        validator_version=validator_version,
        reasons_histogram={reason: 1},
        reduction_rung=rung,
        release_audit_id=None,
        dossier_id=request.subject_ref,
    )


def report_for_refusal(
    request: DossierRequest,
    refusal: Refusal,
    *,
    validator_version: str,
) -> GroundingReport:
    """Zero-count grounding report for a gate ``Denied`` / ``Refusal``."""
    if not isinstance(refusal, Refusal):
        raise TypeError("report_for_refusal requires a gate Refusal")
    return report_for_pre_call_terminal(
        request, refusal, validator_version=validator_version,
    )


def report_for_call_failure(
    request: DossierRequest,
    failed: CallFailed,
    *,
    validator_version: str,
) -> GroundingReport:
    """Zero-count issued-call report: real ``release_audit_id``, empty histogram."""
    if not isinstance(failed, CallFailed):
        raise TypeError("report_for_call_failure requires CallFailed")
    return _zero_report(
        request,
        validator_version=validator_version,
        reasons_histogram={},
        reduction_rung=REDUCTION_NONE,
        release_audit_id=failed.audit_id,
        dossier_id=failed.request_identity,
    )
