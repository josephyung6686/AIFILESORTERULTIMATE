# src/tree_design/provenance.py
"""P10's §8.2 writers and its §8.7 reader.

§8.2's literal list contains two names that are P10's: `template application` and
`destination-tree edit`. Both have been reserved in `database_agent.events` since
P1 shipped and neither has had a producer. This module is the producer, and it is
the ONLY place in P10 that appends an event.

The structured payload rides in `explanation`, after a human sentence and a
newline. §8.2 requires "the acting user, the time, the node identifier, the
before and after state, and the evidence reference or user intent behind it", and
P1's event columns hold five of those; the rest is canonical JSON so replay reads
one form per value. P1 stores it opaquely and interprets none of it, which is the
same discipline P1 applies to `polarity`, `proposal_class` and `basis_key`.
"""
from __future__ import annotations

import sqlite3

from database_agent.events import append_event
from database_agent.learning import learning_records
from evidence_shape.canonical import canonical_json
from tree_design.vocabulary import (
    CORRECTION_SCOPES,
    DESTINATION_TREE_EDIT,
    TEMPLATE_APPLICATION,
    TREE_EDIT_ACTIONS,
    VERSION_ACTIONS,
    check,
)

#: §8.2's "responsible subsystem". Spelled in exactly one place, as P6's brief
#: requires of every part, so a rename is one edit and not a grep.
SUBSYSTEM: str = "P10"

#: §8.7's opaque `proposal_class` for a branch candidate. P1 stores it and
#: interprets nothing; the suppression rule is P10's, applied in P10.
PROPOSAL_CLASS_BRANCH: str = "branch"

#: The `proposal_class` of the two non-branch records this module writes. Named
#: rather than spelled at the call site for the same reason as every other closed
#: value in P10: one home, so a rename is one edit.
PROPOSAL_CLASS_TEMPLATE: str = "template"
PROPOSAL_CLASS_PLAN_VERSION: str = "plan_version"

#: A top-level branch has no parent, and `correction_subject` cannot be empty
#: when a scope is present (`database_agent.events.append_event` refuses it). The
#: root gets a name rather than an empty string, because an empty subject would
#: collide with every other absent subject in the log.
ROOT_SUBJECT: str = "__root__"

ACCEPT_POLARITY: str = "accept"
REJECT_POLARITY: str = "reject"

#: §8.7's two polarities. P1 stores the value and derives nothing from it, so the
#: closed set has to be enforced by the acting part — here.
POLARITIES: tuple[str, ...] = (ACCEPT_POLARITY, REJECT_POLARITY)


def _explanation(sentence: str, payload: dict) -> str:
    """A human sentence, a newline, then the canonical payload.

    An empty sentence returns an empty explanation ON PURPOSE, so P1's own
    required-field check refuses the append. Duplicating that rule here would put
    one contract in two places, and the second copy is the one that drifts.
    """
    if not sentence or not sentence.strip():
        return ""
    return f"{sentence}\n{canonical_json(payload)}"


def record_tree_edit(conn: sqlite3.Connection, *, action: str, node_id: str,
                     plan_version_id: str, before: object, after: object,
                     explanation: str, observed_at: str, user_id: str,
                     correction_scope: str, correction_subject: str,
                     polarity: str, component_version: str,
                     basis_key: str | None = None) -> int:
    """One `destination-tree edit`. Every canvas action that alters the draft.

    §8.2 requires the before and after node state, so a rename keeps its prior
    label and a deleted candidate keeps the evidence that produced it — which is
    exactly what §8.7's no-resurfacing rule reads back.
    """
    check(action, TREE_EDIT_ACTIONS, name="tree edit action")
    check(correction_scope, CORRECTION_SCOPES, name="correction_scope")
    check(polarity, POLARITIES, name="polarity")
    payload = {
        "action": action,
        "node_id": node_id,
        "plan_version_id": plan_version_id,
        "before": before,
        "after": after,
    }
    return append_event(
        conn,
        event_type=DESTINATION_TREE_EDIT,
        subsystem=SUBSYSTEM,
        component_version=component_version,
        observed_at=observed_at,
        explanation=_explanation(explanation, payload),
        user_id=user_id,
        correction_scope=correction_scope,
        correction_subject=correction_subject,
        polarity=polarity,
        proposal_class=PROPOSAL_CLASS_BRANCH,
        basis_key=basis_key,
    )


def record_template_application(conn: sqlite3.Connection, *, node_id: str,
                                plan_version_id: str, template_id: str,
                                template_version: int, binding_id: str,
                                explanation: str, observed_at: str,
                                user_id: str, component_version: str,
                                model_identifier: str | None = None,
                                prompt_fingerprint: str | None = None) -> int:
    """One `template application`, carrying the exact template id and version.

    §8.2 and §3.4: a model-generated template additionally carries the model
    version and the prompt fingerprint. Without both, two runs under different
    prompts look identical to §8.5's replay, and a regression has no cause.
    """
    if model_identifier is not None and not prompt_fingerprint:
        raise ValueError(
            "a model-generated template application records the model version "
            "AND the prompt fingerprint (§8.2, §3.4); one without the other "
            "makes a replay divergence unattributable"
        )
    payload = {
        "node_id": node_id,
        "plan_version_id": plan_version_id,
        "template_id": template_id,
        "template_version": template_version,
        "binding_id": binding_id,
        "model_identifier": model_identifier,
    }
    return append_event(
        conn,
        event_type=TEMPLATE_APPLICATION,
        subsystem=SUBSYSTEM,
        component_version=component_version,
        observed_at=observed_at,
        explanation=_explanation(explanation, payload),
        user_id=user_id,
        prompt_fingerprint=prompt_fingerprint,
        correction_scope="template",
        correction_subject=template_id,
        polarity=ACCEPT_POLARITY,
        proposal_class=PROPOSAL_CLASS_TEMPLATE,
    )


def record_plan_version_adoption(conn: sqlite3.Connection, *,
                                 plan_version_id: str, action: str,
                                 explanation: str, observed_at: str,
                                 user_id: str, component_version: str) -> int:
    """§8.8's adoption record, appended at freeze and at every restore.

    P1 reserves no separate name for it, and coining one would be P10 registering
    an event type outside its SPEC. It is a `destination-tree edit` whose subject
    is the plan version rather than a node, at corpus scope.
    """
    check(action, VERSION_ACTIONS, name="version action")
    payload = {"plan_version_id": plan_version_id, "action": action}
    return append_event(
        conn,
        event_type=DESTINATION_TREE_EDIT,
        subsystem=SUBSYSTEM,
        component_version=component_version,
        observed_at=observed_at,
        explanation=_explanation(explanation, payload),
        user_id=user_id,
        correction_scope="corpus",
        correction_subject=plan_version_id,
        polarity=ACCEPT_POLARITY,
        proposal_class=PROPOSAL_CLASS_PLAN_VERSION,
    )


def branch_basis_key(*, parent_node_id: str | None,
                     dimension_or_label: str) -> str:
    """§8.7's `basis_key` for a branch proposal: (parent, dimension or label).

    The parent is part of the key because rejecting `General` under one course
    says nothing about `General` under another. A key that dropped the parent
    would turn one local correction into a corpus-wide ban.
    """
    return canonical_json([parent_node_id, dimension_or_label])


def suppressed_branch_basis_keys(conn: sqlite3.Connection, *,
                                 parent_node_id: str | None) -> frozenset[str]:
    """The branch proposals this user has already rejected under this parent.

    §8.7: "Otherwise the system will repeatedly resurface the same attractive but
    incorrect grouping." `learning_records` honours a reset as a cutoff and
    deletes nothing (R6), so a reset lifts the suppression while the record and
    the evidence behind it survive.
    """
    subject = ROOT_SUBJECT if parent_node_id is None else parent_node_id
    return frozenset(
        row["basis_key"]
        for row in learning_records(conn, "node", subject)
        if row["proposal_class"] == PROPOSAL_CLASS_BRANCH
        and row["polarity"] == REJECT_POLARITY
        and row["basis_key"]
    )
