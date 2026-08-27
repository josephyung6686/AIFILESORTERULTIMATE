# src/llm_harness/dossier.py
"""The canonical post-release dossier: the exact bytes the model is shown.

SPEC §1: the dossier is the only input to a model call, and it is closed-world.
That is only true if the bytes carry everything the response is judged against —
the envelope, the allowed vocabulary, what P7 actually released (address, value,
zone), the builder's reference metadata, the conflicts, and
the authored response schema and shaping policy.

`dossier_id` is the content address of those bytes. It is deliberately NOT
`release_id`: a release id is a single-use spend capability, so using it as the
identity meant two calls over identical content had two identities and no call
could be recognised as a replay of another.

This module authors no content. Every value it serialises comes from P7's
`Released`, the builder's `DossierRequest`, or the injected `PromptDefinition`.
"""
from __future__ import annotations

from collections.abc import Sequence

from evidence_shape.canonical import canonical_json
from llm_harness.fingerprint import dossier_content_address
from llm_harness.records import (
    Dossier,
    DossierRequest,
    EvidenceItem,
    MalformedRecord,
    PromptDefinition,
    ReleasedEvidence,
    ValidationUnavailable,
)
from privacy.release import Released


def _requested_keys(request: DossierRequest) -> frozenset[str]:
    """Observation keys the builder asked P7 for. Not every item kind carries one."""
    return frozenset(
        item.observation_key
        for item in request.model_call_request.requested_items
        if getattr(item, "observation_key", None)
    )


def _released_evidence(released: Released) -> tuple[ReleasedEvidence, ...]:
    return tuple(
        ReleasedEvidence(
            observation_key=item.observation_key,
            address=item.span,
            value=item.value,
            zone=item.zone,
        )
        for item in released.materialised_items
    )


def _evidence_item_body(item: EvidenceItem) -> dict:
    return {
        "basis": item.basis,
        "evidence_ref": item.evidence_ref,
        "excerpt_span": list(item.excerpt_span) if item.excerpt_span else None,
        "kind": item.kind,
        "location": item.location,
        "reliability_state": item.reliability_state,
    }


def _released_body(item: ReleasedEvidence) -> dict:
    """The model-visible bytes for one released item, and only what P7 released.

    This wrote the raw text on either side of the requested span beside the
    redacted value, so an 8-character span put its whole text unit in front of
    the model. §8.4 keeps "complete extracted text" local; the local audit
    manifest still carries it.
    """
    return {
        "address": item.address,
        "observation_key": item.observation_key,
        "value": item.value,
        "zone": item.zone,
    }


def _as_text(raw: bytes, *, name: str) -> str:
    """An injected authority, as the model sees it.

    These were emitted as hex into what this module calls the exact bytes the
    model is shown. Hex is right in `prompt_fingerprint`, where `canonical_json`
    cannot encode raw bytes; in the model-visible body it renders the two
    authorities meant to constrain the answer unreadable to the model. P8 authors
    neither and does not repair them: bytes that are not text cannot constrain
    anything, and that is a caller contract failure, not a fallback.
    """
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise MalformedRecord(
            f"{name} is shown to the model and must be text it can read"
        ) from exc


def _body(
    *,
    call_site: str,
    subject_ref: str,
    eligibility_reason: str,
    plan_version: str | None,
    policy_version: str,
    max_dossier_tokens: int,
    reduction_rung: str,
    allowed_vocabulary: Sequence[str],
    evidence_items: Sequence[EvidenceItem],
    conflicts: Sequence,
    released_evidence: Sequence[ReleasedEvidence],
    prompt: PromptDefinition,
) -> bytes:
    """One canonical form. `dossier_id`, `release_id` and `audit_id` are absent."""
    return canonical_json({
        "allowed_vocabulary": list(allowed_vocabulary),
        "call_site": call_site,
        "conflicts": [
            {"conflict_id": item.conflict_id, "kind": item.kind} for item in conflicts
        ],
        "eligibility_reason": eligibility_reason,
        "evidence_items": [_evidence_item_body(item) for item in evidence_items],
        "max_dossier_tokens": max_dossier_tokens,
        "plan_version": plan_version,
        "policy_version": policy_version,
        "reduction_rung": reduction_rung,
        "released_evidence": [_released_body(item) for item in released_evidence],
        "response_schema": _as_text(
            prompt.response_schema_bytes, name="response_schema_bytes"),
        "shaping_policy": _as_text(
            prompt.shaping_policy_bytes, name="shaping_policy_bytes"),
        "subject_ref": subject_ref,
    }).encode("utf-8")


def canonical_dossier_bytes(dossier: Dossier, prompt: PromptDefinition) -> bytes:
    """The model-visible dossier bytes for an already-materialised `Dossier`."""
    return _body(
        call_site=dossier.call_site,
        subject_ref=dossier.subject_ref,
        eligibility_reason=dossier.eligibility_reason,
        plan_version=dossier.plan_version,
        policy_version=dossier.policy_version,
        max_dossier_tokens=dossier.max_dossier_tokens,
        reduction_rung=dossier.reduction_rung,
        allowed_vocabulary=dossier.allowed_vocabulary,
        evidence_items=dossier.evidence_items,
        conflicts=dossier.conflicts,
        released_evidence=dossier.released_evidence,
        prompt=prompt,
    )


def dossier_address(dossier: Dossier, prompt: PromptDefinition) -> str:
    """The content address of a dossier's model-visible bytes."""
    return dossier_content_address(
        canonical_dossier_bytes(dossier, prompt),
        allowed_vocabulary=dossier.allowed_vocabulary,
        allowed_schema_bytes=prompt.response_schema_bytes,
    )


def build_dossier(
    request: DossierRequest,
    released: Released,
    *,
    reduction_rung: str,
    allowed_vocabulary: Sequence[str],
    prompt: PromptDefinition,
) -> Dossier | ValidationUnavailable:
    """Materialise one dossier from a live release. Fails closed, before egress.

    Three key sets must agree: what the builder requested of P7, what P7 released,
    and what the builder described. A released key nobody requested is a forged or
    mismatched release; a released key with no builder metadata means P8 would have
    to invent `kind`, `location`, `reliability_state` and `basis`, which §1 forbids.
    """
    released_evidence = _released_evidence(released)
    missing: list[str] = []
    if not released_evidence:
        missing.append("released_evidence")
    released_keys = {item.observation_key for item in released_evidence}
    if released_keys - _requested_keys(request):
        missing.append("released_key_not_requested")
    if released_keys - {item.evidence_ref for item in request.evidence_items}:
        missing.append("builder_evidence_metadata")
    if missing:
        return ValidationUnavailable(missing=tuple(missing))

    body = _body(
        call_site=request.call_site,
        subject_ref=request.subject_ref,
        eligibility_reason=request.eligibility_reason,
        plan_version=request.plan_version,
        policy_version=released.policy_version,
        max_dossier_tokens=request.model_call_request.max_dossier_tokens,
        reduction_rung=reduction_rung,
        allowed_vocabulary=allowed_vocabulary,
        evidence_items=request.evidence_items,
        conflicts=request.conflicts,
        released_evidence=released_evidence,
        prompt=prompt,
    )
    return Dossier(
        dossier_id=dossier_content_address(
            body,
            allowed_vocabulary=allowed_vocabulary,
            allowed_schema_bytes=prompt.response_schema_bytes,
        ),
        call_site=request.call_site,
        subject_ref=request.subject_ref,
        eligibility_reason=request.eligibility_reason,
        plan_version=request.plan_version,
        policy_version=released.policy_version,
        allowed_vocabulary=tuple(allowed_vocabulary),
        evidence_items=request.evidence_items,
        conflicts=request.conflicts,
        released_evidence=released_evidence,
        max_dossier_tokens=request.model_call_request.max_dossier_tokens,
        reduction_rung=reduction_rung,
        release_id=released.release_id,
    )
