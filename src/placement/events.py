"""P11's §8.2 appends. One function per registered event name.

P1 writes; P11 authors (M8), so `subsystem` is filled here and never by P1. Every
append carries §8.2's required fields, and `prompt_fingerprint` is set only where
a model was actually used -- a fingerprint on a deterministic decision would claim
a model call that did not happen.
"""
from __future__ import annotations

import json

from database_agent.events import append_event

from placement.vocabulary import (
    CANDIDATE_RETRIEVAL, GROUP_PLAN_EMITTED, INDEX_ENTRY_BUILT,
    RECOMMENDATION_EMITTED, RESIDUAL_RECOMMENDATION_EMITTED,
    RESIDUAL_SET_DECIDED, RESIDUAL_SET_SURFACED, RETURN_ISSUED, REVIEW_DECISION,
)

SUBSYSTEM: str = "P11"


def _append(conn, event_type, *, component_version, observed_at, explanation,
            file_id=None, content_hash=None, prompt_fingerprint=None,
            user_id=None, correction_scope=None, correction_subject=None,
            polarity=None, proposal_class=None, basis_key=None) -> int:
    fields = dict(
        event_type=event_type, subsystem=SUBSYSTEM,
        component_version=component_version, observed_at=observed_at,
        explanation=explanation,
    )
    optional = dict(
        file_id=file_id, content_hash=content_hash,
        prompt_fingerprint=prompt_fingerprint, user_id=user_id,
        correction_scope=correction_scope, correction_subject=correction_subject,
        polarity=polarity, proposal_class=proposal_class, basis_key=basis_key,
    )
    fields.update({k: value for k, value in optional.items() if value is not None})
    return append_event(conn, **fields)


def index_entry_built(conn, *, node_id, plan_version, component_version,
                      observed_at) -> int:
    return _append(
        conn, INDEX_ENTRY_BUILT, component_version=component_version,
        observed_at=observed_at,
        explanation=json.dumps({"node_id": node_id, "plan_version": plan_version},
                               sort_keys=True),
    )


def candidate_retrieval(conn, *, subject_ref, plan_version, retrieved,
                        suppressed, component_version, observed_at,
                        file_id=None, content_hash=None) -> int:
    # §8.2 requires the retrieved AND the suppressed ids: a review surface that
    # cannot show what was ruled out cannot answer "why not that folder?".
    return _append(
        conn, CANDIDATE_RETRIEVAL, component_version=component_version,
        observed_at=observed_at, file_id=file_id, content_hash=content_hash,
        explanation=json.dumps({
            "subject_ref": subject_ref, "plan_version": plan_version,
            "retrieved": list(retrieved), "suppressed": list(suppressed),
        }, sort_keys=True),
    )


def recommendation_emitted(conn, decision, *, component_version, observed_at,
                           prompt_fingerprint=None) -> int:
    event_type = (RESIDUAL_RECOMMENDATION_EMITTED
                  if decision.residual is not None else RECOMMENDATION_EMITTED)
    return _append(
        conn, event_type, component_version=component_version,
        observed_at=observed_at, file_id=decision.subject.file_id,
        content_hash=decision.subject.content_hash,
        prompt_fingerprint=prompt_fingerprint,
        explanation=decision.explanation,
    )


def group_plan_emitted(conn, *, group_plan_id, group_id, shared_parent_node_id,
                       component_version, observed_at) -> int:
    return _append(
        conn, GROUP_PLAN_EMITTED, component_version=component_version,
        observed_at=observed_at,
        explanation=json.dumps({
            "group_plan_id": group_plan_id, "group_id": group_id,
            "shared_parent_node_id": shared_parent_node_id,
        }, sort_keys=True),
    )


def residual_set_surfaced(conn, *, set_id, label, file_count, reason_not_placed,
                          component_version, observed_at) -> int:
    return _append(
        conn, RESIDUAL_SET_SURFACED, component_version=component_version,
        observed_at=observed_at,
        explanation=json.dumps({
            "set_id": set_id, "label": label, "file_count": file_count,
            "reason_not_placed": reason_not_placed,
        }, sort_keys=True),
    )


def residual_set_decided(conn, *, set_id, choice, node_id, component_version,
                         observed_at, user_id) -> int:
    return _append(
        conn, RESIDUAL_SET_DECIDED, component_version=component_version,
        observed_at=observed_at, user_id=user_id,
        explanation=json.dumps({"set_id": set_id, "choice": choice,
                                "node_id": node_id}, sort_keys=True),
    )


def return_issued(conn, *, residual_decision_id, placement_decision_id,
                  component_version, observed_at, file_id, content_hash) -> int:
    # The link is the event's whole content: §7.9 requires both records to persist
    # and the second to point at the first.
    return _append(
        conn, RETURN_ISSUED, component_version=component_version,
        observed_at=observed_at, file_id=file_id, content_hash=content_hash,
        explanation=json.dumps({
            "residual_decision_id": residual_decision_id,
            "placement_decision_id": placement_decision_id,
        }, sort_keys=True),
    )


def review_decision(conn, *, subject_ref, action, component_version, observed_at,
                    user_id, correction_scope, correction_subject, polarity,
                    proposal_class, basis_key, explanation,
                    file_id=None, content_hash=None) -> int:
    return _append(
        conn, REVIEW_DECISION, component_version=component_version,
        observed_at=observed_at, user_id=user_id, file_id=file_id,
        content_hash=content_hash, correction_scope=correction_scope,
        correction_subject=correction_subject, polarity=polarity,
        proposal_class=proposal_class, basis_key=basis_key,
        explanation=json.dumps({"subject_ref": subject_ref, "action": action,
                                "basis": explanation}, sort_keys=True),
    )
