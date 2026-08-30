"""A rejection, stored with the evidence that produced it, and re-presented.

    §8.7 requires negative feedback stored "with the evidence that produced them".

P13 SPEC:308-312 says what that evidence IS on a P13 record: `presented_state_ref`
plus the decision's `matching_facts[]` and `observation_key` citations. So a prior
rejection is reassembled from the STORED PRESENTATION -- which carries the keys
actually shown and the policy they were shown under -- and never from the decision
as it stands today. A decision superseded since the rejection would otherwise
re-attribute the user's "no" to evidence they never saw.

This is what makes §7.10's worked case work: PDFs rejected out of Receipts and
Confirmations BECAUSE THEY ARE ACTUALLY SCHOOL FORMS must route future similar
files back toward Academic or Applications review, and "because" is only in the
record if the evidence is.

P13 applies none of this. It renders the prior and collects the next gesture; the
learning is P1's scoped projection and the meaning belongs to the routed part.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from privacy.vocabulary import REDACTED

from review_surface.citations import ResolvedCitation, resolve_citation
from review_surface.presentation import PresentedState, presented_state
from review_surface.store import actions_for
from review_surface.vocabulary import ACTION_REJECT


@dataclass(frozen=True)
class PriorRejection:
    """One prior "no", with what the user was looking at when they said it."""

    action_id: str
    subject_ref: str
    plan_version: str
    correction_scope: str
    acted_at: str
    presented_state: PresentedState
    citations: tuple[ResolvedCitation, ...]
    explanation: str


def prior_rejections(conn: sqlite3.Connection, *,
                     subject_ref: str) -> tuple[PriorRejection, ...]:
    """Every prior rejection of this subject, oldest first, with its evidence.

    A rejection whose presentation is missing is skipped rather than shown
    evidence-less: `collect` refuses an action without one and the table is
    append-only, so this branch is unreachable through P13's own writer -- and a
    rejection reassembled without its evidence is precisely what §8.7 forbids, so
    it must not be manufactured here either.
    """
    priors: list[PriorRejection] = []
    for action in actions_for(conn, subject_ref=subject_ref):
        if action.action != ACTION_REJECT:
            continue
        state = presented_state(conn, action.presented_state_ref)
        if state is None:
            continue
        reason = str(action.payload.get("reason", ""))
        hidden = sorted(facet for facet, value
                        in state.redaction_policy.items() if value == REDACTED)
        priors.append(PriorRejection(
            action_id=action.action_id, subject_ref=action.subject_ref,
            plan_version=action.plan_version,
            correction_scope=action.correction_scope,
            acted_at=action.acted_at, presented_state=state,
            citations=tuple(resolve_citation(conn, key)
                            for key in state.evidence_refs),
            explanation=(
                f"rejected on {action.acted_at} at "
                f"{action.correction_scope} scope"
                + (f": {reason}" if reason else "")
                + f"; shown with {len(state.evidence_refs)} evidence "
                  f"reference(s), with {hidden} redacted")))
    return tuple(priors)
