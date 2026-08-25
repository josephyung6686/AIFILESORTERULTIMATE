"""Sites C/D placement and residual validation.

Tree/policy oracles are required injections with no defaults. The residual
controlled-action set is P8's Task 1 `RESIDUAL_ACTIONS`. Q3's two-condition
rule is Site C only.
"""
from __future__ import annotations

import dataclasses
import json
import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from llm_harness.records import CheckedCitation, Dossier, P8Verdict, ValidationUnavailable
from llm_harness.store import record_verdict, supersede_verdict
from llm_harness.validation import validate_response
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    ACTION_NOT_IN_CONTROLLED_SET,
    BELOW_SUPPORT_THRESHOLD,
    C_PLACEMENT,
    CHOOSE_BROAD_PARENT,
    CHOOSE_RESIDUAL_DESTINATION,
    CONFLICT_IGNORED,
    D_RESIDUAL,
    DESTINATION_NOT_IN_FROZEN_TREE,
    EVIDENCE_NOT_IN_FILE_RECORD,
    GENERIC_HUB_ONLY,
    INSUFFICIENT_MARGIN,
    INVENTED_DATE,
    INVENTED_FOLDER,
    INVENTED_INSTITUTION,
    INVENTED_NODE,
    INVENTED_PROJECT,
    LEAVE_IN_PLACE,
    MARK_REVIEW_LATER,
    MOVE_PLAN_ELIGIBLE,
    NO_DESTINATION,
    NO_SUPPORTED_DESTINATION,
    NODE_NOT_IN_FROZEN_TREE,
    REJECT,
    REJECTED,
    RESIDUAL_ACTIONS,
    RESIDUAL_DESTINATION,
    RESIDUAL_DESTINATION_REVIEW,
    RETURN_ACCEPTED_PACKET,
    RETURN_CONFIRMED_GROUP,
    RETURN_TO_PLACEMENT,
    REVIEW_LATER,
    SCHEMA_INVALID,
    SENSITIVITY_POLICY_VIOLATION,
    SENSITIVITY_RESTRICTION_IGNORED,
    SLOT_FILLED_WITHOUT_EVIDENCE,
    STRONGER_RELATIONSHIP_OVERLOOKED,
    UNRESOLVED,
    VALID_REVIEW_REQUIRED,
    WEAK,
)

_TARGET_ACTIONS = frozenset({
    RETURN_CONFIRMED_GROUP,
    RETURN_ACCEPTED_PACKET,
    CHOOSE_RESIDUAL_DESTINATION,
    CHOOSE_BROAD_PARENT,
})

_IDENTITY_DDL = """
CREATE TABLE IF NOT EXISTS llm_cd_plan_identity (
    verdict_id TEXT PRIMARY KEY,
    plan_version TEXT NOT NULL,
    evidence_snapshot_id TEXT NOT NULL
);
"""


@dataclass(frozen=True, slots=True)
class PlacementDependencies:
    node_exists: Callable[[str, str], bool]
    support_threshold: object
    margin_predicate: Callable[[object, object], bool]
    sensitivity_policy: Callable[[Dossier, Mapping[str, object]], bool]


@dataclass(frozen=True, slots=True)
class ResidualDependencies:
    node_exists: Callable[[str, str], bool]
    sensitivity_policy: Callable[[Dossier, Mapping[str, object]], bool]
    approved_target_ids: tuple[str, ...]


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
    verdict_id: str | None = None,
    plan_version: str | None = None,
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
        verdict_id=verdict.verdict_id if verdict_id is None else verdict_id,
        outcome=new_outcome,
        disposition=verdict.disposition if disposition is None else disposition,
        reasons=verdict.reasons if reasons is None else reasons,
        may_propose=new_propose,
        requires_review=new_review,
        plan_version=verdict.plan_version if plan_version is None else plan_version,
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


def _weak(verdict: P8Verdict, reason: str) -> P8Verdict:
    return _rewrite(
        verdict,
        outcome=WEAK,
        disposition=UNRESOLVED,
        reasons=(reason,),
        may_propose=False,
        requires_review=False,
    )


def _missing_placement(dependencies: PlacementDependencies | None) -> tuple[str, ...]:
    names = (
        "node_exists", "support_threshold", "margin_predicate", "sensitivity_policy",
    )
    if dependencies is None:
        return names
    missing = [name for name in names if getattr(dependencies, name) is None]
    return tuple(missing)


def _missing_residual(dependencies: ResidualDependencies | None) -> tuple[str, ...]:
    names = ("node_exists", "sensitivity_policy", "approved_target_ids")
    if dependencies is None:
        return names
    missing = [name for name in names if getattr(dependencies, name) is None]
    return tuple(missing)


def _dimensions(payload: Mapping[str, object]) -> tuple[Mapping[str, object], ...]:
    raw = payload.get("per_dimension_support")
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        return ()
    return tuple(item for item in raw if isinstance(item, Mapping))


def _real_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _invented_dimension(payload: Mapping[str, object], vocab: set[str]) -> str | None:
    for item in _dimensions(payload):
        value = item.get("value")
        dimension = item.get("dimension")
        if value in vocab:
            continue
        if dimension == "date":
            return INVENTED_DATE
        if dimension == "institution":
            return INVENTED_INSTITUTION
        if dimension == "project":
            return INVENTED_PROJECT
    return None


def _placement_site(
    dossier: Dossier,
    raw: object,
    verdict: P8Verdict,
    dependencies: PlacementDependencies,
) -> P8Verdict | None:
    payload = _payload_of(raw)
    destination = payload.get("destination")
    vocab = set(dossier.allowed_vocabulary)
    plan_version = dossier.plan_version or ""
    if destination in (None, "none"):
        return _rewrite(
            verdict,
            outcome=ABSTAIN,
            disposition=NO_SUPPORTED_DESTINATION,
            reasons=(),
            may_propose=False,
            requires_review=False,
        )
    destination = str(destination)
    if destination not in vocab:
        return _reject(verdict, INVENTED_NODE, NO_DESTINATION)
    if not dependencies.node_exists(destination, plan_version):
        return _reject(verdict, NODE_NOT_IN_FROZEN_TREE, NO_DESTINATION)
    invented = _invented_dimension(payload, vocab)
    if invented is not None:
        return _reject(verdict, invented, NO_DESTINATION)
    if any(item.get("support") == "unsupported" for item in _dimensions(payload)):
        return _reject(verdict, SLOT_FILLED_WITHOUT_EVIDENCE, NO_DESTINATION)
    considered = payload.get("conflicts_considered")
    considered_ids = set(considered) if isinstance(considered, Sequence) and not isinstance(
        considered, (str, bytes),
    ) else set()
    if dossier.conflicts and any(
        item.conflict_id not in considered_ids for item in dossier.conflicts
    ):
        return _reject(verdict, CONFLICT_IGNORED, NO_DESTINATION)
    if not dependencies.sensitivity_policy(dossier, payload):
        return _reject(verdict, SENSITIVITY_POLICY_VIOLATION, NO_DESTINATION)
    if payload.get("generic_hub") is True or destination == "node-hub":
        return _weak(verdict, GENERIC_HUB_ONLY)
    if "support" not in payload:
        return _weak(verdict, BELOW_SUPPORT_THRESHOLD)
    support = payload["support"]
    if not _real_number(support):
        return _reject(verdict, SCHEMA_INVALID, NO_DESTINATION)
    if float(support) < float(dependencies.support_threshold):
        return _weak(verdict, BELOW_SUPPORT_THRESHOLD)
    if "next_support" not in payload:
        return _weak(verdict, INSUFFICIENT_MARGIN)
    next_support = payload["next_support"]
    if not _real_number(next_support):
        return _reject(verdict, SCHEMA_INVALID, NO_DESTINATION)
    if not dependencies.margin_predicate(support, next_support):
        return _weak(verdict, INSUFFICIENT_MARGIN)
    if payload.get("weak_retrieval") is True:
        return _rewrite(
            verdict,
            outcome=WEAK,
            disposition=UNRESOLVED,
            reasons=(),
            may_propose=False,
            requires_review=False,
        )
    return None


def _placement_disposition(verdict: P8Verdict) -> P8Verdict:
    if verdict.outcome == ACCEPT_DIRECT:
        disposition = MOVE_PLAN_ELIGIBLE
    elif verdict.outcome == ACCEPT_CONTEXT_SUPPORTED:
        disposition = VALID_REVIEW_REQUIRED
    elif verdict.outcome == WEAK:
        disposition = UNRESOLVED
    elif verdict.outcome == REJECT:
        disposition = NO_DESTINATION
    elif verdict.outcome == ABSTAIN:
        disposition = NO_SUPPORTED_DESTINATION
    else:
        disposition = verdict.disposition
    return _rewrite(verdict, disposition=disposition)


def _same_file_evidence(dossier: Dossier, raw: object) -> bool:
    if not isinstance(raw, Mapping):
        return True
    citations = raw.get("citations")
    if not isinstance(citations, Sequence) or isinstance(citations, (str, bytes)):
        return True
    by_ref = {item.evidence_ref: item for item in dossier.evidence_items}
    for citation in citations:
        if not isinstance(citation, Mapping):
            continue
        ref = citation.get("evidence_ref")
        item = by_ref.get(str(ref))
        if item is None:
            continue
        if item.location != dossier.subject_ref:
            return False
    return True


def _residual_site(
    dossier: Dossier,
    raw: object,
    verdict: P8Verdict,
    dependencies: ResidualDependencies,
) -> P8Verdict | ValidationUnavailable | None:
    payload = _payload_of(raw)
    if "support" in payload and "next_support" in payload:
        return ValidationUnavailable(missing=("site_d_support_rule",))
    action = payload.get("action")
    if action not in RESIDUAL_ACTIONS:
        return _reject(verdict, ACTION_NOT_IN_CONTROLLED_SET, REJECTED)
    target = payload.get("target")
    if isinstance(target, str) and "/" in target:
        return _reject(verdict, INVENTED_FOLDER, REJECTED)
    plan_version = dossier.plan_version or ""
    if action in _TARGET_ACTIONS:
        if not isinstance(target, str) or not target:
            return _reject(verdict, DESTINATION_NOT_IN_FROZEN_TREE, REJECTED)
        approved = set(dependencies.approved_target_ids)
        if not dependencies.node_exists(target, plan_version):
            return _reject(verdict, DESTINATION_NOT_IN_FROZEN_TREE, REJECTED)
        if target not in approved and target not in dossier.allowed_vocabulary:
            return _reject(verdict, DESTINATION_NOT_IN_FROZEN_TREE, REJECTED)
    if not _same_file_evidence(dossier, raw):
        return _reject(verdict, EVIDENCE_NOT_IN_FILE_RECORD, REJECTED)
    if not dependencies.sensitivity_policy(dossier, payload):
        return _reject(verdict, SENSITIVITY_RESTRICTION_IGNORED, REJECTED)
    considered = payload.get("relationships_considered")
    considered_ids = set(considered) if isinstance(considered, Sequence) and not isinstance(
        considered, (str, bytes),
    ) else set()
    if any(
        item.kind == "stronger_relationship" and item.conflict_id not in considered_ids
        for item in dossier.conflicts
    ):
        return _reject(verdict, STRONGER_RELATIONSHIP_OVERLOOKED, RETURN_TO_PLACEMENT)
    if action == MARK_REVIEW_LATER:
        return _rewrite(
            verdict,
            outcome=WEAK,
            disposition=REVIEW_LATER,
            reasons=(),
            may_propose=False,
            requires_review=False,
        )
    return None


def _residual_disposition(verdict: P8Verdict, raw: object | None = None) -> P8Verdict:
    if STRONGER_RELATIONSHIP_OVERLOOKED in verdict.reasons:
        return _rewrite(verdict, disposition=RETURN_TO_PLACEMENT)
    payload = _payload_of(raw) if raw is not None else {}
    action = payload.get("action")
    if verdict.outcome == ACCEPT_DIRECT:
        if action in {RETURN_CONFIRMED_GROUP, RETURN_ACCEPTED_PACKET}:
            disposition = RETURN_TO_PLACEMENT
        else:
            disposition = RESIDUAL_DESTINATION
    elif verdict.outcome == ACCEPT_CONTEXT_SUPPORTED:
        disposition = RESIDUAL_DESTINATION_REVIEW
    elif verdict.outcome == WEAK:
        disposition = REVIEW_LATER if action == MARK_REVIEW_LATER else LEAVE_IN_PLACE
    elif verdict.outcome == REJECT:
        disposition = REJECTED
    elif verdict.outcome == ABSTAIN:
        disposition = LEAVE_IN_PLACE
    else:
        disposition = verdict.disposition
    return _rewrite(verdict, disposition=disposition)


def _finish(result, *, adjust):
    if isinstance(result, ValidationUnavailable):
        return result
    verdicts, report = result
    return tuple(adjust(item) for item in verdicts), report


def validate_placement_response(
    dossier: Dossier,
    response_bytes: bytes,
    *,
    evidence_resolver,
    contradicts,
    dependencies: PlacementDependencies | None,
    model_id: str,
    prompt_fingerprint: str,
    dossier_builder: str,
    release_audit_id: int | None,
):
    missing = _missing_placement(dependencies)
    if missing:
        return ValidationUnavailable(missing=missing)

    def site(dossier_arg, raw, verdict):
        return _placement_site(dossier_arg, raw, verdict, dependencies)

    result = validate_response(
        dossier,
        response_bytes,
        evidence_resolver=evidence_resolver,
        site_validator=site,
        contradicts=contradicts,
        model_id=model_id,
        prompt_fingerprint=prompt_fingerprint,
        dossier_builder=dossier_builder,
        release_audit_id=release_audit_id,
    )
    return _finish(result, adjust=_placement_disposition)


def validate_residual_response(
    dossier: Dossier,
    response_bytes: bytes,
    *,
    evidence_resolver,
    contradicts,
    dependencies: ResidualDependencies | None,
    model_id: str,
    prompt_fingerprint: str,
    dossier_builder: str,
    release_audit_id: int | None,
):
    missing = _missing_residual(dependencies)
    if missing:
        return ValidationUnavailable(missing=missing)

    def site(dossier_arg, raw, verdict):
        return _residual_site(dossier_arg, raw, verdict, dependencies)

    result = validate_response(
        dossier,
        response_bytes,
        evidence_resolver=evidence_resolver,
        site_validator=site,
        contradicts=contradicts,
        model_id=model_id,
        prompt_fingerprint=prompt_fingerprint,
        dossier_builder=dossier_builder,
        release_audit_id=release_audit_id,
    )
    if isinstance(result, ValidationUnavailable):
        return result
    verdicts, report = result
    try:
        parsed = json.loads(response_bytes)
        raws = parsed.get("claims") if isinstance(parsed, dict) else []
    except (ValueError, TypeError, UnicodeDecodeError):
        raws = []
    if not isinstance(raws, list):
        raws = []
    adjusted = []
    for index, verdict in enumerate(verdicts):
        raw = raws[index] if index < len(raws) else {}
        adjusted.append(_residual_disposition(verdict, raw))
    return tuple(adjusted), report


def _ensure_identity_table(conn: sqlite3.Connection) -> None:
    conn.executescript(_IDENTITY_DDL)


def record_cd_verdict(
    conn: sqlite3.Connection,
    verdict: P8Verdict,
    *,
    evidence_snapshot_id: str,
    observed_at: str,
) -> str:
    if not evidence_snapshot_id:
        raise ValueError("evidence_snapshot_id is required for C/D verdicts")
    if not verdict.plan_version:
        raise ValueError("C/D verdicts require plan_version")
    _ensure_identity_table(conn)
    record_verdict(conn, verdict, observed_at=observed_at)
    conn.execute(
        "INSERT INTO llm_cd_plan_identity ("
        "verdict_id, plan_version, evidence_snapshot_id"
        ") VALUES (?, ?, ?)",
        (verdict.verdict_id, verdict.plan_version, evidence_snapshot_id),
    )
    return verdict.verdict_id


def _verdict_from_payload(payload: Mapping[str, object]) -> P8Verdict:
    checked = tuple(
        CheckedCitation(
            citation_ref=str(item["citation_ref"]),
            resolved=bool(item["resolved"]),
            span_matched=bool(item["span_matched"]),
        )
        for item in payload["citations_checked"]
    )
    return P8Verdict(
        verdict_id=str(payload["verdict_id"]),
        dossier_id=str(payload["dossier_id"]),
        claim_ref=str(payload["claim_ref"]),
        outcome=str(payload["outcome"]),
        disposition=str(payload["disposition"]),
        reasons=tuple(payload["reasons"]),
        may_propose=bool(payload["may_propose"]),
        requires_review=bool(payload["requires_review"]),
        citations_checked=checked,
        scope=str(payload["scope"]),
        validator_version=str(payload["validator_version"]),
        policy_version=str(payload["policy_version"]),
        plan_version=payload["plan_version"],
    )


def revalidate_for_plan(
    conn: sqlite3.Connection,
    *,
    current_plan_version: str,
    current_evidence_snapshot_id: str,
    previous_verdict_id: str,
    dossier: Dossier,
    response_bytes: bytes,
    evidence_resolver,
    contradicts,
    dependencies: PlacementDependencies | ResidualDependencies | None,
    observed_at: str,
    model_id: str,
    prompt_fingerprint: str,
    dossier_builder: str,
    release_audit_id: int | None,
) -> P8Verdict | ValidationUnavailable:
    _ensure_identity_table(conn)
    row = conn.execute(
        "SELECT payload, plan_version FROM llm_verdict WHERE verdict_id = ?",
        (previous_verdict_id,),
    ).fetchone()
    if row is None:
        raise KeyError(f"unknown verdict {previous_verdict_id!r}")
    identity = conn.execute(
        "SELECT plan_version, evidence_snapshot_id FROM llm_cd_plan_identity "
        "WHERE verdict_id = ?",
        (previous_verdict_id,),
    ).fetchone()
    stored_plan = identity["plan_version"] if identity is not None else row["plan_version"]
    stored_snapshot = (
        identity["evidence_snapshot_id"] if identity is not None else None
    )
    if (
        stored_plan == current_plan_version
        and stored_snapshot == current_evidence_snapshot_id
    ):
        return _verdict_from_payload(json.loads(row["payload"]))

    if dossier.call_site == C_PLACEMENT:
        missing = _missing_placement(
            dependencies if isinstance(dependencies, PlacementDependencies) else None
        )
    else:
        missing = _missing_residual(
            dependencies if isinstance(dependencies, ResidualDependencies) else None
        )
    if missing:
        return ValidationUnavailable(missing=missing)

    updated = dataclasses.replace(dossier, plan_version=current_plan_version)
    if dossier.call_site == C_PLACEMENT:
        result = validate_placement_response(
            updated,
            response_bytes,
            evidence_resolver=evidence_resolver,
            contradicts=contradicts,
            dependencies=dependencies,
            model_id=model_id,
            prompt_fingerprint=prompt_fingerprint,
            dossier_builder=dossier_builder,
            release_audit_id=release_audit_id,
        )
    else:
        result = validate_residual_response(
            updated,
            response_bytes,
            evidence_resolver=evidence_resolver,
            contradicts=contradicts,
            dependencies=dependencies,
            model_id=model_id,
            prompt_fingerprint=prompt_fingerprint,
            dossier_builder=dossier_builder,
            release_audit_id=release_audit_id,
        )
    if isinstance(result, ValidationUnavailable):
        return result
    fresh = result[0][0]
    stamped = _rewrite(
        fresh,
        verdict_id=(
            f"{previous_verdict_id}::{current_plan_version}::"
            f"{current_evidence_snapshot_id}"
        ),
        plan_version=current_plan_version,
    )
    record_cd_verdict(
        conn, stamped,
        evidence_snapshot_id=current_evidence_snapshot_id,
        observed_at=observed_at,
    )
    supersede_verdict(
        conn, previous_verdict_id, stamped.verdict_id,
        reason="plan_or_snapshot_changed",
        observed_at=observed_at,
    )
    return stamped
