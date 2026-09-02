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
`Released`, the builder's `DossierRequest`, the injected `PromptDefinition`, or
`library/field_glossary.json` -- and that file authors none either: every meaning
in it is quoted from something already ratified, and names the source it was
quoted from.
"""
from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path

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
from llm_harness.wire_handles import WIRE_HANDLE_KEY, wire_handle, wire_ref
from privacy.release import Released


GLOSSARY_FILE = Path(__file__).resolve().parent / "library" / "field_glossary.json"


class GlossaryRequired(RuntimeError):
    """The shipped glossary is missing or is not the shape its consumer reads."""


@lru_cache(maxsize=1)
def _meanings() -> Mapping[str, str]:
    """Every authored field meaning, by key. No fallback and no empty default.

    An empty glossary would silently restore the state the owner ruled against: a
    model shown 56 bare keys, guessing or declining. It would also do so invisibly,
    because a dossier with no meanings is well-formed. So a missing file refuses.
    """
    if not GLOSSARY_FILE.is_file():
        raise GlossaryRequired(
            f"{GLOSSARY_FILE} is not on disk; this package ships no default meaning")
    loaded = json.loads(GLOSSARY_FILE.read_text(encoding="utf-8"))
    fields = loaded.get("fields")
    if not isinstance(fields, dict) or not fields:
        raise GlossaryRequired(f"{GLOSSARY_FILE} carries no field meanings")
    return {key: entry["meaning"] for key, entry in fields.items()}


def field_glossary(allowed_vocabulary: Sequence[str]) -> dict[str, str]:
    """What each field key of THIS call means -- and nothing about this file.

    `76` §10.1 records the glossary decision as owed and names three options; the
    owner chose the one where the dossier carries the meanings. The defence `82`
    §7.1 would otherwise have relied on was rule 2 -- *"if a key's meaning is not
    plain from the key itself, decline that field"* -- which is safe and costs real
    coverage on `subject`, `work_type`, `purpose`, `record_type`, `project` and
    `duplicate_family`, the fields that matter most. Told, the model need neither
    guess nor decline.

    **The vocabulary is the only input, and that is the whole bound.** A meaning
    defines a FIELD; it is never a hint about the FILE. Because nothing about the
    file, the person or the corpus can reach this function, no entry can vary
    between two files and nothing in §8.4's always-local set has a route in.

    A field with no authored meaning is ABSENT, never filled: `library/
    field_glossary.json` records those in `owed`, and for them `82` rule 2's
    fail-closed position still holds -- which is what it was for.
    """
    meanings = _meanings()
    return {field: meanings[field] for field in allowed_vocabulary
            if field in meanings}


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


def _evidence_item_body(item: EvidenceItem, *, handle_key: bytes) -> dict:
    return {
        "basis": item.basis,
        "evidence_ref": wire_ref(item.evidence_ref, key=handle_key),
        "excerpt_span": list(item.excerpt_span) if item.excerpt_span else None,
        "kind": item.kind,
        "location": item.location,
        "reliability_state": item.reliability_state,
    }


def _released_body(item: ReleasedEvidence, *, handle_key: bytes) -> dict:
    """The model-visible bytes for one released item, and only what P7 released.

    This wrote the raw text on either side of the requested span beside the
    redacted value, so an 8-character span put its whole text unit in front of
    the model. §8.4 keeps "complete extracted text" local; the local audit
    manifest still carries it.

    `observation_key` is keyed here rather than printed. It is a digest of the
    file's bytes, of the locator and of the raw value, and the locator is printed
    in the clear as `address` one line above -- so the un-keyed key was a
    dictionary attack on the value beside it, and the value beside it is the one
    redaction had already removed.
    """
    return {
        "address": item.address,
        "observation_key": wire_handle(item.observation_key, key=handle_key),
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
    handle_key: bytes,
) -> bytes:
    """One canonical form. `dossier_id`, `release_id` and `audit_id` are absent.

    **This is the only function in the product that writes an identifier into
    model-visible bytes**, which is why the keying lives here and nowhere else.
    Four slots carry one, and each is keyed by `wire_handles` before it is
    written: `subject_ref`, every `conflict_id`, every released
    `observation_key`, and every `evidence_ref` that is a P4 key. Everything
    upstream -- the `Dossier` record, the `llm_dossier` payload, the audit, the
    resolver -- keeps the identifiers it always had.
    """
    return canonical_json({
        "allowed_vocabulary": list(allowed_vocabulary),
        "call_site": call_site,
        # `conflict_id` is `f"{group_id}:{kind}"` at P9's seam, so it carried the
        # same reversible group digest `subject_ref` did. Keyed, not parsed apart:
        # P8 does not know what a producer put in an id and must not have to.
        "conflicts": [
            {"conflict_id": wire_handle(item.conflict_id, key=handle_key),
             "kind": item.kind}
            for item in conflicts
        ],
        "eligibility_reason": eligibility_reason,
        "evidence_items": [
            _evidence_item_body(item, handle_key=handle_key)
            for item in evidence_items
        ],
        # Built from `allowed_vocabulary` and nothing else, deliberately: it is the
        # one key here whose content is the same on every file in every corpus.
        "field_glossary": field_glossary(allowed_vocabulary),
        "max_dossier_tokens": max_dossier_tokens,
        "plan_version": plan_version,
        "policy_version": policy_version,
        "reduction_rung": reduction_rung,
        "released_evidence": [
            _released_body(item, handle_key=handle_key)
            for item in released_evidence
        ],
        "response_schema": _as_text(
            prompt.response_schema_bytes, name="response_schema_bytes"),
        "shaping_policy": _as_text(
            prompt.shaping_policy_bytes, name="shaping_policy_bytes"),
        # Keyed WHOLE, never parsed. `records.DossierRequest` validates nothing
        # about `subject_ref`; today's producers pass a group id, but the field is
        # a free string and the next producer's could be a title or a path.
        "subject_ref": wire_handle(subject_ref, key=handle_key),
    }).encode("utf-8")


def canonical_dossier_bytes(
    dossier: Dossier, prompt: PromptDefinition, *, handle_key: bytes,
) -> bytes:
    """The model-visible dossier bytes for an already-materialised `Dossier`.

    `handle_key` has no default. A caller with no key gets `WireHandleKeyRequired`
    and not a set of bytes a recipient could reverse.
    """
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
        handle_key=handle_key,
    )


def dossier_address(
    dossier: Dossier, prompt: PromptDefinition, *, handle_key: bytes,
) -> str:
    """The content address of a dossier's model-visible bytes."""
    return dossier_content_address(
        canonical_dossier_bytes(dossier, prompt, handle_key=handle_key),
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
    handle_key: bytes,
) -> Dossier | ValidationUnavailable:
    """Materialise one dossier from a live release. Fails closed, before egress.

    Three key sets must agree: what the builder requested of P7, what P7 released,
    and what the builder described. A released key nobody requested is a forged or
    mismatched release; a released key with no builder metadata means P8 would have
    to invent `kind`, `location`, `reliability_state` and `basis`, which §1 forbids.

    A missing `handle_key` is one of the three, and it is checked first: every
    identifier below reaches a model keyed, and there is no unkeyed fallback to
    fall back to.
    """
    if not isinstance(handle_key, (bytes, bytearray)) or not handle_key:
        return ValidationUnavailable(missing=(WIRE_HANDLE_KEY,))
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
        handle_key=handle_key,
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
