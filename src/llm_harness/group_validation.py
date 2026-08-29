"""Site B group validation over fixture/P9 payloads.

P8 validates a proposed conclusion. It does not retrieve neighbours, create a
group, or accept membership on P9's behalf.
"""
from __future__ import annotations

import dataclasses
from collections.abc import Mapping, Sequence

from llm_harness.records import Dossier, P8Verdict, ValidationUnavailable
from llm_harness.validation import validate_response
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    CONFLICTING_TARGET_INSTITUTION,
    CONTEXT_ONLY_SUPPORT,
    CONTEXT_SUPPORTED,
    CONTEXT_SUPPORTED_MEMBERSHIP,
    DIRECT_MEMBERSHIP,
    FOLDER_HIERARCHY_PROPOSED,
    GENERIC_SIMILARITY_ONLY,
    INVENTED_DATE,
    INVENTED_MEMBERSHIP,
    INVENTED_PROJECT,
    INVENTED_PURPOSE,
    LABEL_WITHOUT_COHERENCE,
    REJECT,
    REJECTED,
    SCHEMA_INVALID,
    TERM_MERGE_UNSUPPORTED,
    UNRESOLVED,
    WEAK,
)


def _payload_of(raw: object) -> Mapping[str, object]:
    if not isinstance(raw, Mapping):
        return {}
    payload = raw.get("payload")
    if isinstance(payload, Mapping):
        return payload
    return {}


def _rewrite(
    verdict: P8Verdict,
    *,
    outcome: str | None = None,
    disposition: str | None = None,
    reasons: tuple[str, ...] | None = None,
    may_propose: bool | None = None,
    requires_review: bool | None = None,
) -> P8Verdict:
    new_outcome = verdict.outcome if outcome is None else outcome
    new_review = verdict.requires_review if requires_review is None else requires_review
    if new_outcome == ACCEPT_CONTEXT_SUPPORTED:
        new_review = True
    new_propose = verdict.may_propose if may_propose is None else may_propose
    if new_outcome == WEAK:
        new_propose = False
    return dataclasses.replace(
        verdict,
        outcome=new_outcome,
        disposition=verdict.disposition if disposition is None else disposition,
        reasons=verdict.reasons if reasons is None else reasons,
        may_propose=new_propose,
        requires_review=new_review,
    )


def _reject(verdict: P8Verdict, reason: str, disposition: str) -> P8Verdict:
    return _rewrite(
        verdict,
        outcome=REJECT,
        disposition=disposition,
        reasons=(reason,),
        may_propose=False,
        requires_review=False,
    )


def _dossier_members(dossier: Dossier) -> set[str]:
    return {
        item.evidence_ref for item in dossier.evidence_items if item.kind == "member"
    }


def _included_members(payload: Mapping[str, object]) -> tuple[str, ...] | None:
    if "members" not in payload:
        return ()
    raw = payload["members"]
    if isinstance(raw, (str, bytes)) or not isinstance(raw, Sequence):
        return None
    found: list[str] = []
    for item in raw:
        if isinstance(item, str):
            if not item:
                return None
            found.append(item)
        elif isinstance(item, Mapping):
            file_id = item.get("file_id")
            if not isinstance(file_id, str) or not file_id:
                return None
            found.append(file_id)
        else:
            return None
    return tuple(found)


def _conflicting_institution(dossier: Dossier, payload: Mapping[str, object]) -> bool:
    if not any(item.kind == "target_institution" for item in dossier.conflicts):
        return False
    included_members = _included_members(payload)
    if included_members is None:
        return False
    included = set(included_members)
    outliers = payload.get("outliers")
    if not isinstance(outliers, Sequence) or isinstance(outliers, (str, bytes)):
        return False
    for item in outliers:
        if not isinstance(item, Mapping):
            continue
        if item.get("conflict_kind") == "target_institution" and item.get("file_id") in included:
            return True
    return False


def _group_site(dossier: Dossier, raw: object, verdict: P8Verdict) -> P8Verdict | None:
    payload = _payload_of(raw)
    vocab = set(dossier.allowed_vocabulary)
    if "hierarchy" in payload or "folder_path" in payload:
        return _reject(verdict, FOLDER_HIERARCHY_PROPOSED, REJECTED)
    coherent = payload.get("coherent")
    if payload.get("label") and coherent != "yes":
        return _reject(verdict, LABEL_WITHOUT_COHERENCE, REJECTED)
    members = _included_members(payload)
    if members is None:
        return _reject(verdict, SCHEMA_INVALID, REJECTED)
    for file_id in members:
        if file_id not in _dossier_members(dossier):
            return _reject(verdict, INVENTED_MEMBERSHIP, REJECTED)
    if "date" in payload and payload["date"] not in vocab:
        return _reject(verdict, INVENTED_DATE, REJECTED)
    if "project" in payload and payload["project"] not in vocab:
        return _reject(verdict, INVENTED_PROJECT, REJECTED)
    if "purpose" in payload and payload["purpose"] not in vocab:
        return _reject(verdict, INVENTED_PURPOSE, REJECTED)
    merge_terms = payload.get("merge_terms")
    if isinstance(merge_terms, Sequence) and not isinstance(merge_terms, (str, bytes)):
        if len(set(merge_terms)) > 1:
            return _reject(verdict, TERM_MERGE_UNSUPPORTED, REJECTED)
    if _conflicting_institution(dossier, payload):
        return _reject(verdict, CONFLICTING_TARGET_INSTITUTION, REJECTED)
    if payload.get("basis") == "generic-similarity":
        return _reject(verdict, GENERIC_SIMILARITY_ONLY, UNRESOLVED)
    if payload.get("basis") == CONTEXT_SUPPORTED:
        return _rewrite(
            verdict,
            outcome=ACCEPT_CONTEXT_SUPPORTED,
            disposition=CONTEXT_SUPPORTED_MEMBERSHIP,
            reasons=(CONTEXT_ONLY_SUPPORT,),
            may_propose=True,
            requires_review=True,
        )
    if coherent == "insufficient":
        return _rewrite(
            verdict,
            outcome=WEAK,
            disposition=UNRESOLVED,
            reasons=(),
            may_propose=False,
            requires_review=False,
        )
    return None


def _group_disposition(verdict: P8Verdict) -> P8Verdict:
    if GENERIC_SIMILARITY_ONLY in verdict.reasons:
        disposition = UNRESOLVED
    elif CONTEXT_ONLY_SUPPORT in verdict.reasons:
        disposition = CONTEXT_SUPPORTED_MEMBERSHIP
    elif verdict.outcome == ACCEPT_DIRECT:
        disposition = DIRECT_MEMBERSHIP
    elif verdict.outcome == ACCEPT_CONTEXT_SUPPORTED:
        disposition = CONTEXT_SUPPORTED_MEMBERSHIP
    elif verdict.outcome == WEAK:
        disposition = UNRESOLVED
    elif verdict.outcome == REJECT:
        disposition = REJECTED
    elif verdict.outcome == ABSTAIN:
        disposition = UNRESOLVED
    else:
        disposition = verdict.disposition
    return _rewrite(verdict, disposition=disposition)


def validate_group_response(
    dossier: Dossier,
    response_bytes: bytes,
    *,
    evidence_resolver,
    contradicts,
    model_id: str,
    prompt_fingerprint: str,
    dossier_builder: str,
    release_audit_id: int | None,
) -> tuple[tuple[P8Verdict, ...], object] | ValidationUnavailable:
    result = validate_response(
        dossier,
        response_bytes,
        evidence_resolver=evidence_resolver,
        site_validator=_group_site,
        contradicts=contradicts,
        model_id=model_id,
        prompt_fingerprint=prompt_fingerprint,
        dossier_builder=dossier_builder,
        release_audit_id=release_audit_id,
    )
    if isinstance(result, ValidationUnavailable):
        return result
    verdicts, report = result
    return tuple(_group_disposition(item) for item in verdicts), report
