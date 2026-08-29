"""Closed eligibility and the P1 learning-record suppression seam.

Direct unique matches are not detected here. A caller that already knows the
subject is a unique match uses `not_reserved_for_llm`. `assess_call` only
accepts reasons from P8's per-site closed lists.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from database_agent.learning import learning_records

from llm_harness.records import DossierRequest, PreCallAbstention, ValidationUnavailable
from llm_harness.vocabulary import (
    ELIGIBILITY_BY_SITE,
    NOT_ELIGIBLE_FOR_MODEL,
    REJECT,
    USER_REJECTED_EQUIVALENT,
)


@dataclass(frozen=True, slots=True)
class Eligible:
    """The request is a closed-list bounded ambiguity and is not suppressed."""


def not_reserved_for_llm(*, call_site: str, subject_ref: str) -> PreCallAbstention:
    """Caller-injected unique match: the model is not reserved for this subject."""
    return PreCallAbstention(
        reason=NOT_ELIGIBLE_FOR_MODEL,
        call_site=call_site,
        subject_ref=subject_ref,
    )


def suppressed_by_learning(
    conn: sqlite3.Connection, *,
    scope: str,
    subject_id: str,
    proposal_class: str,
    basis_key: str,
) -> bool:
    """True when a current P1 reject of this exact equivalent still stands.

    Cutoff is P1's: `learning_records` already drops rows at or below the reset.
    This adapter matches `proposal_class` and `basis_key` exactly and treats only
    `polarity == reject` as suppression. It is not a second store.
    """
    for row in learning_records(conn, scope, subject_id):
        if row["proposal_class"] != proposal_class:
            continue
        if row["basis_key"] != basis_key:
            continue
        if row["polarity"] == REJECT:
            return True
    return False


def assess_call(
    request: DossierRequest, *,
    conn: sqlite3.Connection | None,
    learning_scope: str | None,
    learning_subject_id: str | None,
    proposal_class: str | None,
    basis_key: str | None,
) -> Eligible | PreCallAbstention | ValidationUnavailable:
    allowed = ELIGIBILITY_BY_SITE.get(request.call_site, ())
    if request.eligibility_reason not in allowed:
        return PreCallAbstention(
            reason=NOT_ELIGIBLE_FOR_MODEL,
            call_site=request.call_site,
            subject_ref=request.subject_ref,
        )
    missing: list[str] = []
    if conn is None:
        missing.append("conn")
    if not learning_scope:
        missing.append("learning_scope")
    if not learning_subject_id:
        missing.append("learning_subject_id")
    if not proposal_class:
        missing.append("proposal_class")
    if not basis_key:
        missing.append("basis_key")
    if missing:
        return ValidationUnavailable(missing=tuple(missing))
    if suppressed_by_learning(
        conn,
        scope=learning_scope,
        subject_id=learning_subject_id,
        proposal_class=proposal_class,
        basis_key=basis_key,
    ):
        return PreCallAbstention(
            reason=USER_REJECTED_EQUIVALENT,
            call_site=request.call_site,
            subject_ref=request.subject_ref,
        )
    return Eligible()
