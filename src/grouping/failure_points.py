# src/grouping/failure_points.py
"""The append-only failure log, kept apart stage by stage.

§4.8 is emphatic: a bad group can fail because retrieval brought irrelevant
neighbours, because the model overgeneralised from a good neighbourhood, or
because the label was simply not useful, and the product "must log and evaluate
these failure points separately rather than treating all mistakes as 'AI
classification errors'". A collapsed error class cannot tell them apart, and a
team that cannot tell them apart fixes the wrong one.

A row is never updated. The same candidate failing three ways is three rows, each
with its own cause and its own reference.

Consent is not a failure point. `NeedsConsent` is a question the product has not
asked yet, and logging it as a failure would measure P9 for a decision the user
has not made.
"""
from __future__ import annotations

import sqlite3

from grouping.records import FailurePoint
from grouping.store import record_failure_point as _write
from grouping.vocabulary import INTERPRETATION, LABEL, RETRIEVAL, check

#: The three stages this log accepts. `graph`, `validation` and `user-rejection`
#: are in the record's own vocabulary and are written where they happen -- the
#: graph builder, the P8 seam, and the review receiver.
LOGGED_STAGES: tuple[str, ...] = (RETRIEVAL, INTERPRETATION, LABEL)


def record_failure(
    conn: sqlite3.Connection,
    *,
    group_id: str,
    stage: str,
    cause_code: str,
    detected_by: str,
    created_at: str,
    dossier_id: str | None = None,
    membership_id: str | None = None,
    evidence_ref: str | None = None,
) -> str:
    """One failure, at one stage, appended and never updated.

    An interpretation failure carries P8's result identity as its evidence
    reference. P9 does not emit the `llm_interpretation` P2 stage for it: that
    stage measures the model call, P8 makes the call, and a second emitter would
    double-count every one of them in the replay.
    """
    check(stage, LOGGED_STAGES, name="stage")
    return _write(conn, FailurePoint(
        group_id=group_id,
        dossier_id=dossier_id,
        membership_id=membership_id,
        stage=stage,
        cause_code=cause_code,
        evidence_ref=evidence_ref,
        detected_by=detected_by,
    ), created_at=created_at)


def failures_for_group(
    conn: sqlite3.Connection, group_id: str,
) -> tuple[FailurePoint, ...]:
    return tuple(
        FailurePoint(
            group_id=row["group_id"], dossier_id=row["dossier_id"],
            membership_id=row["membership_id"], stage=row["stage"],
            cause_code=row["cause_code"], evidence_ref=row["evidence_ref"],
            detected_by=row["detected_by"],
        )
        for row in conn.execute(
            "SELECT * FROM group_failure_points WHERE group_id = ? ORDER BY rowid",
            (group_id,),
        )
    )
