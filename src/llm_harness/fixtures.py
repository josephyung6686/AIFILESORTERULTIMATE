"""P8-owned recorded dossier/response pairs for Sites B–E.

Content-free contract witnesses. Neighbour producers swap at dossier
construction later; this module does not import P9, P10, or P11.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from llm_harness.records import Conflict, Dossier, EvidenceItem
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE,
    ACTION_NOT_IN_CONTROLLED_SET,
    B_GROUP,
    BELOW_SUPPORT_THRESHOLD,
    C_PLACEMENT,
    CHOOSE_RESIDUAL_DESTINATION,
    COHERENCE_JUDGEMENT,
    CONFLICT_IGNORED,
    CONFLICTING_TARGET_INSTITUTION,
    CONTEXT_ONLY_SUPPORT,
    CONTEXT_SUPPORTED,
    CONTEXT_SUPPORTED_MEMBERSHIP,
    D_RESIDUAL,
    DESTINATION_NOT_IN_FROZEN_TREE,
    DIRECT_ANCHOR,
    DIRECT_MEMBERSHIP,
    E_TEMPLATE,
    EVIDENCE_NOT_IN_FILE_RECORD,
    FOLDER_HIERARCHY_PROPOSED,
    GENERIC_HUB_ONLY,
    GENERIC_SIMILARITY_ONLY,
    INSUFFICIENT_MARGIN,
    INVENTED_DATE,
    INVENTED_FOLDER,
    INVENTED_INSTITUTION,
    INVENTED_MEMBERSHIP,
    INVENTED_NODE,
    INVENTED_PROJECT,
    INVENTED_PURPOSE,
    LABEL_WITHOUT_COHERENCE,
    LEAVE_IN_PLACE,
    MARK_REVIEW_LATER,
    MOVE_PLAN_ELIGIBLE,
    NO_DESTINATION,
    NO_SUPPORTED_DESTINATION,
    NODE_NOT_IN_FROZEN_TREE,
    REDUCTION_NONE,
    REJECT,
    REJECTED,
    RESIDUAL_ACTIONS,
    RESIDUAL_DESTINATION,
    RESIDUAL_DESTINATION_REVIEW,
    RETURN_TO_PLACEMENT,
    REVIEW_LATER,
    SENSITIVITY_POLICY_VIOLATION,
    SENSITIVITY_RESTRICTION_IGNORED,
    SEVERAL_LEGAL_NODES_PLAUSIBLE,
    SLOT_FILLED_WITHOUT_EVIDENCE,
    STRONGER_RELATIONSHIP_OVERLOOKED,
    TERM_MERGE_UNSUPPORTED,
    UNRESOLVED,
    USER_OPTED_RESIDUAL_SET_INTO_AI_REVIEW,
    VALID_REVIEW_REQUIRED,
    WEAK,
)

SPAN = "span-1"
OBS = "obs-1"
PLAN_V1 = "plan-v1"
SNAP_1 = "snap-1"
POLICY = "policy-1"
RELEASE = "rel-1"


@dataclass(frozen=True, slots=True)
class RecordedPair:
    site: str
    name: str
    dossier: Dossier
    response_bytes: bytes
    expected_outcome: str
    expected_reasons: tuple[str, ...]
    expected_disposition: str
    expected_may_propose: bool
    expected_requires_review: bool
    evidence_snapshot_id: str | None = None
    frozen_absent_nodes: tuple[str, ...] = ()
    sensitivity_ok: bool = True
    schema_ok: bool = True
    approved_target_ids: tuple[str, ...] = ()


def _excerpt(*, ref: str = OBS, basis: str = DIRECT_ANCHOR,
             location: str = "body") -> EvidenceItem:
    return EvidenceItem(
        evidence_ref=ref,
        kind="excerpt",
        location=location,
        excerpt_span=(0, 6),
        reliability_state="direct",
        basis=basis,
    )


def _member(file_id: str, *, basis: str = DIRECT_ANCHOR) -> EvidenceItem:
    return EvidenceItem(
        evidence_ref=file_id,
        kind="member",
        location=file_id,
        excerpt_span=None,
        reliability_state="direct",
        basis=basis,
    )


def _dossier(
    call_site: str,
    eligibility_reason: str,
    *,
    dossier_id: str,
    subject_ref: str,
    plan_version: str | None,
    allowed_vocabulary: tuple[str, ...],
    evidence_items: tuple[EvidenceItem, ...],
    conflicts: tuple[Conflict, ...] = (),
) -> Dossier:
    return Dossier(
        dossier_id=dossier_id,
        call_site=call_site,
        subject_ref=subject_ref,
        eligibility_reason=eligibility_reason,
        plan_version=plan_version,
        policy_version=POLICY,
        allowed_vocabulary=allowed_vocabulary,
        evidence_items=evidence_items,
        conflicts=conflicts,
        max_dossier_tokens=4000,
        reduction_rung=REDUCTION_NONE,
        release_id=RELEASE,
    )


def _bytes(payload: dict, *, cited: bool = True, unknown: str | None = None) -> bytes:
    claim: dict[str, object] = {"claim_ref": "c1", "payload": payload}
    if unknown is not None:
        claim["unknown"] = {"insufficiency_statement": unknown}
    elif cited:
        claim["citations"] = [{
            "evidence_ref": OBS,
            "cited_span": SPAN,
            "why_it_supports": "supports the recorded claim",
        }]
    else:
        claim["citations"] = []
    return json.dumps({"claims": [claim]}, separators=(",", ":")).encode("utf-8")


def _pair(
    site: str,
    name: str,
    dossier: Dossier,
    payload: dict,
    *,
    outcome: str,
    reasons: tuple[str, ...] = (),
    disposition: str,
    may_propose: bool,
    requires_review: bool,
    cited: bool = True,
    unknown: str | None = None,
    evidence_snapshot_id: str | None = None,
    frozen_absent_nodes: tuple[str, ...] = (),
    sensitivity_ok: bool = True,
    schema_ok: bool = True,
    approved_target_ids: tuple[str, ...] = (),
) -> RecordedPair:
    return RecordedPair(
        site=site,
        name=name,
        dossier=dossier,
        response_bytes=_bytes(payload, cited=cited, unknown=unknown),
        expected_outcome=outcome,
        expected_reasons=reasons,
        expected_disposition=disposition,
        expected_may_propose=may_propose,
        expected_requires_review=requires_review,
        evidence_snapshot_id=evidence_snapshot_id,
        frozen_absent_nodes=frozen_absent_nodes,
        sensitivity_ok=sensitivity_ok,
        schema_ok=schema_ok,
        approved_target_ids=approved_target_ids,
    )


_B_VOCAB = ("cat-academic", "date-2026", "project-x", "purpose-apply", "label-ok")


def _b_dossier(dossier_id: str, *, basis: str = DIRECT_ANCHOR,
               conflicts: tuple[Conflict, ...] = ()) -> Dossier:
    items = (
        _excerpt(basis=basis),
        _member("file-a", basis=basis),
        _member("file-b", basis=basis),
    )
    return _dossier(
        B_GROUP, COHERENCE_JUDGEMENT,
        dossier_id=dossier_id, subject_ref="group-1", plan_version=None,
        allowed_vocabulary=_B_VOCAB, evidence_items=items, conflicts=conflicts,
    )


def _b_members(*file_ids: str) -> list[dict[str, str]]:
    return [{"file_id": file_id, "decision": "include"} for file_id in file_ids]


def _b_ok_payload(**extra: object) -> dict:
    body: dict[str, object] = {
        "coherent": "yes",
        "basis": DIRECT_ANCHOR,
        "members": _b_members("file-a", "file-b"),
    }
    body.update(extra)
    return body


_B_BASE = dict(site=B_GROUP, may_propose=False, requires_review=False)

SITE_B_REASON_PAIRS: tuple[RecordedPair, ...] = (
    _pair(
        **_B_BASE, name=TERM_MERGE_UNSUPPORTED, dossier=_b_dossier("b-term"),
        payload=_b_ok_payload(merge_terms=["term-a", "term-b"]),
        outcome=REJECT, reasons=(TERM_MERGE_UNSUPPORTED,), disposition=REJECTED,
    ),
    _pair(
        **_B_BASE, name=CONFLICTING_TARGET_INSTITUTION,
        dossier=_b_dossier(
            "b-institution",
            conflicts=(Conflict("institution-conflict", "target_institution"),),
        ),
        payload=_b_ok_payload(
            outliers=[{"file_id": "file-b", "conflict_kind": "target_institution"}],
        ),
        outcome=REJECT, reasons=(CONFLICTING_TARGET_INSTITUTION,),
        disposition=REJECTED,
    ),
    _pair(
        **_B_BASE, name=INVENTED_DATE, dossier=_b_dossier("b-date"),
        payload=_b_ok_payload(date="date-invented"),
        outcome=REJECT, reasons=(INVENTED_DATE,), disposition=REJECTED,
    ),
    _pair(
        **_B_BASE, name=INVENTED_PROJECT, dossier=_b_dossier("b-project"),
        payload=_b_ok_payload(project="project-invented"),
        outcome=REJECT, reasons=(INVENTED_PROJECT,), disposition=REJECTED,
    ),
    _pair(
        **_B_BASE, name=INVENTED_PURPOSE, dossier=_b_dossier("b-purpose"),
        payload=_b_ok_payload(purpose="purpose-invented"),
        outcome=REJECT, reasons=(INVENTED_PURPOSE,), disposition=REJECTED,
    ),
    _pair(
        **_B_BASE, name=INVENTED_MEMBERSHIP, dossier=_b_dossier("b-member"),
        payload=_b_ok_payload(members=_b_members("file-a", "file-invented")),
        outcome=REJECT, reasons=(INVENTED_MEMBERSHIP,), disposition=REJECTED,
    ),
    _pair(
        **_B_BASE, name=LABEL_WITHOUT_COHERENCE, dossier=_b_dossier("b-label"),
        payload=_b_ok_payload(
            coherent="no",
            label={"display_label": "Packet", "category": "cat-academic"},
        ),
        outcome=REJECT, reasons=(LABEL_WITHOUT_COHERENCE,), disposition=REJECTED,
    ),
    _pair(
        **_B_BASE, name=FOLDER_HIERARCHY_PROPOSED, dossier=_b_dossier("b-hierarchy"),
        payload=_b_ok_payload(hierarchy=["root", "branch"]),
        outcome=REJECT, reasons=(FOLDER_HIERARCHY_PROPOSED,), disposition=REJECTED,
    ),
    _pair(
        B_GROUP, CONTEXT_ONLY_SUPPORT,
        _b_dossier("b-context-reason", basis=CONTEXT_SUPPORTED),
        _b_ok_payload(basis=CONTEXT_SUPPORTED),
        outcome=ACCEPT_CONTEXT_SUPPORTED, reasons=(CONTEXT_ONLY_SUPPORT,),
        disposition=CONTEXT_SUPPORTED_MEMBERSHIP,
        may_propose=True, requires_review=True,
    ),
    _pair(
        **_B_BASE, name=GENERIC_SIMILARITY_ONLY, dossier=_b_dossier("b-generic"),
        payload=_b_ok_payload(basis="generic-similarity"),
        outcome=REJECT, reasons=(GENERIC_SIMILARITY_ONLY,), disposition=UNRESOLVED,
    ),
)

SITE_B_OUTCOME_PAIRS: tuple[RecordedPair, ...] = (
    _pair(
        B_GROUP, "direct_accept", _b_dossier("b-direct"), _b_ok_payload(),
        outcome=ACCEPT_DIRECT, disposition=DIRECT_MEMBERSHIP,
        may_propose=True, requires_review=False,
    ),
    _pair(
        B_GROUP, "context_accept", _b_dossier("b-context", basis=CONTEXT_SUPPORTED),
        _b_ok_payload(),
        outcome=ACCEPT_CONTEXT_SUPPORTED, disposition=CONTEXT_SUPPORTED_MEMBERSHIP,
        may_propose=True, requires_review=True,
    ),
    _pair(
        B_GROUP, "weak", _b_dossier("b-weak"),
        _b_ok_payload(coherent="insufficient"),
        outcome=WEAK, disposition=UNRESOLVED,
        may_propose=False, requires_review=False,
    ),
    _pair(
        B_GROUP, "reject", _b_dossier("b-reject"), _b_ok_payload(),
        outcome=REJECT, disposition=REJECTED,
        may_propose=False, requires_review=False, cited=False,
    ),
    _pair(
        B_GROUP, "unknown", _b_dossier("b-unknown"), {},
        outcome=ABSTAIN, disposition=UNRESOLVED,
        may_propose=False, requires_review=False, unknown="insufficient evidence",
    ),
)

_C_VOCAB = ("node-legal", "node-alt", "node-hub", "date-2026", "inst-1", "proj-1")


def _c_dossier(dossier_id: str, *, basis: str = DIRECT_ANCHOR,
               conflicts: tuple[Conflict, ...] = ()) -> Dossier:
    return _dossier(
        C_PLACEMENT, SEVERAL_LEGAL_NODES_PLAUSIBLE,
        dossier_id=dossier_id, subject_ref="file-1", plan_version=PLAN_V1,
        allowed_vocabulary=_C_VOCAB,
        evidence_items=(_excerpt(basis=basis),),
        conflicts=conflicts,
    )


def _c_payload(destination: str | None = "node-legal", **extra: object) -> dict:
    body: dict[str, object] = {
        "destination": destination,
        "per_dimension_support": [
            {"dimension": "date", "value": "date-2026", "support": "direct"},
        ],
        "alternatives": ["node-alt"],
        "conflicts_considered": [],
        "support": 0.9,
        "next_support": 0.1,
    }
    body.update(extra)
    return body


_C_SNAP = dict(evidence_snapshot_id=SNAP_1)
_C_BASE = dict(site=C_PLACEMENT, may_propose=False, requires_review=False, **_C_SNAP)

SITE_C_REASON_PAIRS: tuple[RecordedPair, ...] = (
    _pair(
        **_C_BASE, name=NODE_NOT_IN_FROZEN_TREE, dossier=_c_dossier("c-missing"),
        payload=_c_payload(),
        outcome=REJECT, reasons=(NODE_NOT_IN_FROZEN_TREE,), disposition=NO_DESTINATION,
        frozen_absent_nodes=("node-legal",),
    ),
    _pair(
        **_C_BASE, name=INVENTED_DATE, dossier=_c_dossier("c-date"),
        payload=_c_payload(per_dimension_support=[
            {"dimension": "date", "value": "date-invented", "support": "direct"},
        ]),
        outcome=REJECT, reasons=(INVENTED_DATE,), disposition=NO_DESTINATION,
    ),
    _pair(
        **_C_BASE, name=INVENTED_INSTITUTION, dossier=_c_dossier("c-inst"),
        payload=_c_payload(per_dimension_support=[
            {"dimension": "institution", "value": "inst-invented", "support": "direct"},
        ]),
        outcome=REJECT, reasons=(INVENTED_INSTITUTION,), disposition=NO_DESTINATION,
    ),
    _pair(
        **_C_BASE, name=INVENTED_PROJECT, dossier=_c_dossier("c-project"),
        payload=_c_payload(per_dimension_support=[
            {"dimension": "project", "value": "proj-invented", "support": "direct"},
        ]),
        outcome=REJECT, reasons=(INVENTED_PROJECT,), disposition=NO_DESTINATION,
    ),
    _pair(
        **_C_BASE, name=INVENTED_NODE, dossier=_c_dossier("c-node"),
        payload=_c_payload(destination="node-hallucinated"),
        outcome=REJECT, reasons=(INVENTED_NODE,), disposition=NO_DESTINATION,
    ),
    _pair(
        **_C_BASE, name=SLOT_FILLED_WITHOUT_EVIDENCE, dossier=_c_dossier("c-slot"),
        payload=_c_payload(per_dimension_support=[
            {"dimension": "date", "value": "date-2026", "support": "unsupported"},
        ]),
        outcome=REJECT, reasons=(SLOT_FILLED_WITHOUT_EVIDENCE,),
        disposition=NO_DESTINATION,
    ),
    _pair(
        **_C_BASE, name=CONFLICT_IGNORED,
        dossier=_c_dossier("c-conflict", conflicts=(Conflict("c1", "stronger_fact"),)),
        payload=_c_payload(conflicts_considered=[]),
        outcome=REJECT, reasons=(CONFLICT_IGNORED,), disposition=NO_DESTINATION,
    ),
    _pair(
        **_C_BASE, name=SENSITIVITY_POLICY_VIOLATION,
        dossier=_c_dossier("c-sensitivity"), payload=_c_payload(),
        outcome=REJECT, reasons=(SENSITIVITY_POLICY_VIOLATION,),
        disposition=NO_DESTINATION, sensitivity_ok=False,
    ),
    _pair(
        **_C_BASE, name=BELOW_SUPPORT_THRESHOLD, dossier=_c_dossier("c-below"),
        payload=_c_payload(support=0.3, next_support=0.0),
        outcome=WEAK, reasons=(BELOW_SUPPORT_THRESHOLD,), disposition=UNRESOLVED,
    ),
    _pair(
        **_C_BASE, name=INSUFFICIENT_MARGIN, dossier=_c_dossier("c-margin"),
        payload=_c_payload(support=0.8, next_support=0.75),
        outcome=WEAK, reasons=(INSUFFICIENT_MARGIN,), disposition=UNRESOLVED,
    ),
    _pair(
        **_C_BASE, name=GENERIC_HUB_ONLY, dossier=_c_dossier("c-hub"),
        payload=_c_payload(destination="node-hub", generic_hub=True),
        outcome=WEAK, reasons=(GENERIC_HUB_ONLY,), disposition=UNRESOLVED,
    ),
)

SITE_C_OUTCOME_PAIRS: tuple[RecordedPair, ...] = (
    _pair(
        C_PLACEMENT, "direct_accept", _c_dossier("c-direct"), _c_payload(),
        outcome=ACCEPT_DIRECT, disposition=MOVE_PLAN_ELIGIBLE,
        may_propose=True, requires_review=False, **_C_SNAP,
    ),
    _pair(
        C_PLACEMENT, "context_accept",
        _c_dossier("c-context", basis=CONTEXT_SUPPORTED), _c_payload(),
        outcome=ACCEPT_CONTEXT_SUPPORTED, disposition=VALID_REVIEW_REQUIRED,
        may_propose=True, requires_review=True, **_C_SNAP,
    ),
    _pair(
        C_PLACEMENT, "weak", _c_dossier("c-weak"),
        _c_payload(weak_retrieval=True),
        outcome=WEAK, disposition=UNRESOLVED,
        may_propose=False, requires_review=False, **_C_SNAP,
    ),
    _pair(
        C_PLACEMENT, "reject", _c_dossier("c-reject"), _c_payload(),
        outcome=REJECT, disposition=NO_DESTINATION,
        may_propose=False, requires_review=False, cited=False, **_C_SNAP,
    ),
    _pair(
        C_PLACEMENT, "unknown", _c_dossier("c-unknown"), {},
        outcome=ABSTAIN, disposition=NO_SUPPORTED_DESTINATION,
        may_propose=False, requires_review=False,
        unknown="no supported destination", **_C_SNAP,
    ),
)

_D_VOCAB = RESIDUAL_ACTIONS + ("node-legal", "node-parent", "group-1")
_D_APPROVED = ("node-legal", "node-parent", "group-1")


def _d_dossier(dossier_id: str, *, basis: str = DIRECT_ANCHOR, location: str = "file-1",
               conflicts: tuple[Conflict, ...] = ()) -> Dossier:
    return _dossier(
        D_RESIDUAL, USER_OPTED_RESIDUAL_SET_INTO_AI_REVIEW,
        dossier_id=dossier_id, subject_ref="file-1", plan_version=PLAN_V1,
        allowed_vocabulary=_D_VOCAB,
        evidence_items=(_excerpt(basis=basis, location=location),),
        conflicts=conflicts,
    )


def _d_payload(action: str = CHOOSE_RESIDUAL_DESTINATION,
               target: str | None = "node-legal", **extra: object) -> dict:
    body: dict[str, object] = {
        "action": action, "target": target, "stop_reason": "recorded",
    }
    body.update(extra)
    return body


_D_SNAP = dict(evidence_snapshot_id=SNAP_1, approved_target_ids=_D_APPROVED)
_D_BASE = dict(site=D_RESIDUAL, may_propose=False, requires_review=False, **_D_SNAP)

SITE_D_REASON_PAIRS: tuple[RecordedPair, ...] = (
    _pair(
        **_D_BASE, name=ACTION_NOT_IN_CONTROLLED_SET, dossier=_d_dossier("d-action"),
        payload=_d_payload(action="invent_destination"),
        outcome=REJECT, reasons=(ACTION_NOT_IN_CONTROLLED_SET,), disposition=REJECTED,
    ),
    _pair(
        **_D_BASE, name=DESTINATION_NOT_IN_FROZEN_TREE, dossier=_d_dossier("d-tree"),
        payload=_d_payload(target="node-legal"),
        outcome=REJECT, reasons=(DESTINATION_NOT_IN_FROZEN_TREE,),
        disposition=REJECTED, frozen_absent_nodes=("node-legal",),
    ),
    _pair(
        **_D_BASE, name=EVIDENCE_NOT_IN_FILE_RECORD,
        dossier=_d_dossier("d-file", location="file-other"),
        payload=_d_payload(),
        outcome=REJECT, reasons=(EVIDENCE_NOT_IN_FILE_RECORD,), disposition=REJECTED,
    ),
    _pair(
        **_D_BASE, name=SENSITIVITY_RESTRICTION_IGNORED,
        dossier=_d_dossier("d-sensitivity"), payload=_d_payload(),
        outcome=REJECT, reasons=(SENSITIVITY_RESTRICTION_IGNORED,),
        disposition=REJECTED, sensitivity_ok=False,
    ),
    _pair(
        **_D_BASE, name=STRONGER_RELATIONSHIP_OVERLOOKED,
        dossier=_d_dossier(
            "d-stronger",
            conflicts=(Conflict("rel-1", "stronger_relationship"),),
        ),
        payload=_d_payload(relationships_considered=[]),
        outcome=REJECT, reasons=(STRONGER_RELATIONSHIP_OVERLOOKED,),
        disposition=RETURN_TO_PLACEMENT,
    ),
    _pair(
        **_D_BASE, name=INVENTED_FOLDER, dossier=_d_dossier("d-folder"),
        payload=_d_payload(target="Travel/Flight-Gate"),
        outcome=REJECT, reasons=(INVENTED_FOLDER,), disposition=REJECTED,
    ),
)

SITE_D_OUTCOME_PAIRS: tuple[RecordedPair, ...] = (
    _pair(
        D_RESIDUAL, "direct_accept", _d_dossier("d-direct"), _d_payload(),
        outcome=ACCEPT_DIRECT, disposition=RESIDUAL_DESTINATION,
        may_propose=True, requires_review=False, **_D_SNAP,
    ),
    _pair(
        D_RESIDUAL, "context_accept",
        _d_dossier("d-context", basis=CONTEXT_SUPPORTED), _d_payload(),
        outcome=ACCEPT_CONTEXT_SUPPORTED, disposition=RESIDUAL_DESTINATION_REVIEW,
        may_propose=True, requires_review=True, **_D_SNAP,
    ),
    _pair(
        D_RESIDUAL, "weak", _d_dossier("d-weak"),
        _d_payload(action=MARK_REVIEW_LATER, target=None),
        outcome=WEAK, disposition=REVIEW_LATER,
        may_propose=False, requires_review=False, **_D_SNAP,
    ),
    _pair(
        D_RESIDUAL, "reject", _d_dossier("d-reject"), _d_payload(),
        outcome=REJECT, disposition=REJECTED,
        may_propose=False, requires_review=False, cited=False, **_D_SNAP,
    ),
    _pair(
        D_RESIDUAL, "unknown", _d_dossier("d-unknown"), {},
        outcome=ABSTAIN, disposition=LEAVE_IN_PLACE,
        may_propose=False, requires_review=False,
        unknown="no residual destination", **_D_SNAP,
    ),
)

SITE_D_SUPPORT_RULE_PAIR = _pair(
    D_RESIDUAL, "site_d_support_rule", _d_dossier("d-q3"),
    _d_payload(support=0.4, next_support=0.3),
    outcome=ABSTAIN, disposition=UNRESOLVED,
    may_propose=False, requires_review=False, **_D_SNAP,
)

_E_VOCAB = ("year", "event")


def _e_dossier(dossier_id: str, *, basis: str = DIRECT_ANCHOR) -> Dossier:
    return _dossier(
        E_TEMPLATE, ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE,
        dossier_id=dossier_id, subject_ref="group-1", plan_version=PLAN_V1,
        allowed_vocabulary=_E_VOCAB,
        evidence_items=(_excerpt(basis=basis),),
    )


def _e_payload(*dimension_names: str, justify: bool = True) -> dict:
    dimensions = [
        {"name": name, "values": ["v1"], "evidence_ref": OBS}
        for name in dimension_names
    ]
    levels = [{"dimension": name} for name in dimension_names]
    if justify:
        for level in levels:
            level["retrieval_justification"] = "cited file fact"
    return {"dimensions": dimensions, "levels": levels}


SITE_E_OUTCOME_PAIRS: tuple[RecordedPair, ...] = (
    _pair(
        E_TEMPLATE, "direct_accept", _e_dossier("e-direct"),
        _e_payload("year", "event"),
        outcome=ACCEPT_DIRECT, disposition=DIRECT_MEMBERSHIP,
        may_propose=True, requires_review=False,
    ),
    _pair(
        E_TEMPLATE, "context_accept",
        _e_dossier("e-context", basis=CONTEXT_SUPPORTED),
        _e_payload("year", "event"),
        outcome=ACCEPT_CONTEXT_SUPPORTED, disposition=CONTEXT_SUPPORTED_MEMBERSHIP,
        may_propose=True, requires_review=True,
    ),
    _pair(
        E_TEMPLATE, "weak", _e_dossier("e-weak"), _e_payload("year", justify=False),
        outcome=WEAK, disposition=UNRESOLVED,
        may_propose=False, requires_review=False,
    ),
    _pair(
        E_TEMPLATE, "reject", _e_dossier("e-reject"),
        _e_payload("year", "invented-dim"),
        outcome=REJECT, disposition=REJECTED,
        may_propose=False, requires_review=False,
    ),
    _pair(
        E_TEMPLATE, "unknown", _e_dossier("e-unknown"), {},
        outcome=ABSTAIN, disposition=ABSTAIN,
        may_propose=False, requires_review=False, unknown="no template dimensions",
    ),
)
