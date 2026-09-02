"""Append, supersede and read. Nothing here rewrites a decision.

A revised decision is a NEW row whose `supersedes` names the prior one; the prior
row keeps its evidence, its alternatives and its two-condition figures and gains
`superseded_by` and `supersede_reason`. P1's `mark_superseded` writes both halves
and refuses a second supersede of the same row, so the chain is followable forward
-- which §8.8's version diff needs and `supersedes` alone cannot give.
"""
from __future__ import annotations

import dataclasses
import json
import sqlite3

from database_agent.db import transaction
from database_agent.supersede import mark_superseded

from placement import events as placement_events
from placement.records import DECISION_FIELDS, PlacementDecision
from placement.vocabulary import FILE

#: The named columns beside `payload`. Every one is either an address derived from
#: the record (`record_id`, `subject_ref`) or a field of it, so no column here can
#: hold a concept the record does not have. Task 4's test pins that.
PROJECTION_COLUMNS: tuple[str, ...] = (
    "record_id", "subject_ref", "plan_version", "origin_stage", "outcome",
    "node_id", "group_plan_id", "returned_from", "review_policy", "created_at",
)


class AmbiguousCurrentDecision(RuntimeError):
    """More than one live row for one subject. Refused before any write."""


def subject_ref_of(subject) -> str:
    """One address for one subject. A file version, or a group.

    The file form carries the content hash because §8.8 versions the plan and §8.2
    versions the file: a decision about `f1` at one hash is not a decision about
    `f1` after it was edited.
    """
    if subject.kind == FILE:
        return f"{FILE}:{subject.file_id}:{subject.content_hash}"
    return f"{subject.kind}:{subject.group_id}"


def _payload(decision: PlacementDecision) -> str:
    return json.dumps(dataclasses.asdict(decision), sort_keys=True)


def _from_row(row: sqlite3.Row) -> PlacementDecision:
    from placement import records as r

    body = json.loads(row["payload"])
    nested = {
        "subject": r.Subject, "destination": r.Destination,
        "return_target": r.ReturnTarget, "ask": r.Ask,
        "decision_depth": r.DecisionDepth, "group_support": r.GroupSupport,
        "two_condition": r.TwoCondition, "privacy": r.PrivacyState,
        "residual": r.ResidualContext,
    }
    for name, cls in nested.items():
        if body.get(name) is not None:
            body[name] = cls(**body[name])
    sequences = {
        "matching_facts": r.MatchingFact, "graph_anchors": r.GraphAnchor,
        "conflicts_considered": r.ConflictConsidered, "alternatives": r.Alternative,
    }
    for name, cls in sequences.items():
        body[name] = tuple(cls(**item) for item in body.get(name, ()))
    # The supersede link lives on the ROW, not in the payload: it is written after
    # the record was built, by `mark_superseded`, and the payload is never rewritten.
    for name in ("superseded_by", "supersede_reason"):
        body[name] = row[name]
    return PlacementDecision(**{name: body[name] for name in DECISION_FIELDS})


def record_decision(conn: sqlite3.Connection, decision: PlacementDecision, *,
                    component_version: str, observed_at: str,
                    supersede_reason: str | None = None) -> str:
    """Link the predecessor, append the decision, and log it. ONE transaction.

    The supersede, the row and the event commit together, and the order inside
    is forced by the partial unique index rather than chosen (see the comment
    below). Two transactions where one is needed is a defect this project has
    shipped before: a decision row with no event is a placement §8.2 cannot
    explain, an event with no row is a claim about a decision that does not
    exist, and a supersede that committed without its replacement leaves a
    subject with no current decision at all.
    """
    subject_ref = subject_ref_of(decision.subject)
    with transaction(conn):
        live = conn.execute(
            "SELECT record_id FROM placement_decisions WHERE plan_version = ? "
            "AND subject_ref = ? AND superseded_by IS NULL",
            (decision.plan_version, subject_ref),
        ).fetchall()
        if len(live) > 1:
            raise AmbiguousCurrentDecision(
                f"{len(live)} live decisions for {subject_ref!r} in "
                f"{decision.plan_version!r}; the store refuses to add a third "
                "rather than pick one"
            )
        if decision.supersedes is not None and not supersede_reason:
            raise ValueError(
                "superseding a decision requires the reason it was superseded "
                "(§8.2); the prior row stays readable and says why"
            )
        # SUPERSEDE FIRST, THEN INSERT. `one_current_placement_decision` is a
        # partial unique index over UNSUPERSEDED rows, so inserting the new row
        # while the old one is still live puts two current decisions for one
        # subject in the table for the length of one statement -- and SQLite
        # refuses the very insert that was about to resolve it.
        #
        # This is P9's rule, in P9's own words at `grouping/acceptance.py:77-80`:
        # "Supersede first. The unique index is over unsuperseded rows, so
        # linking after the insert would mean two current opinions existed for
        # the length of one statement."
        #
        # `mark_superseded` still writes BOTH halves and still runs every guard
        # -- reason required, no self-supersede, predecessor exists, predecessor
        # not already superseded, no cycle. Its `UPDATE ... SET supersedes` on
        # the not-yet-inserted new row is a no-op, and the INSERT below carries
        # `supersedes` in the payload, so the forward link §8.8's diff walks is
        # established either way. P11 writes no supersession logic of its own.
        if decision.supersedes is not None:
            mark_superseded(
                conn, "placement_decisions", old_id=decision.supersedes,
                new_id=decision.decision_id, reason=supersede_reason,
            )
        conn.execute(
            "INSERT INTO placement_decisions (record_id, subject_ref, plan_version, "
            "origin_stage, outcome, node_id, group_plan_id, returned_from, "
            "review_policy, created_at, payload, supersedes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                decision.decision_id, subject_ref, decision.plan_version,
                decision.origin_stage, decision.outcome,
                decision.destination.node_id if decision.destination else None,
                decision.group_plan_id, decision.returned_from,
                decision.review_policy, decision.created_at, _payload(decision),
                decision.supersedes,
            ),
        )
        placement_events.recommendation_emitted(
            conn, decision, component_version=component_version,
            observed_at=observed_at,
        )
    return decision.decision_id


def current_decision(conn: sqlite3.Connection, *, plan_version: str,
                     subject_ref: str) -> PlacementDecision | None:
    row = conn.execute(
        "SELECT * FROM placement_decisions WHERE plan_version = ? AND "
        "subject_ref = ? AND superseded_by IS NULL", (plan_version, subject_ref),
    ).fetchone()
    return None if row is None else _from_row(row)


def decision_history(conn: sqlite3.Connection, *,
                     subject_ref: str) -> tuple[PlacementDecision, ...]:
    """Every decision ever made about this subject, oldest first, across versions."""
    rows = conn.execute(
        "SELECT * FROM placement_decisions WHERE subject_ref = ? "
        "ORDER BY created_at, record_id", (subject_ref,),
    ).fetchall()
    return tuple(_from_row(row) for row in rows)


def decisions_for_plan(conn: sqlite3.Connection, *,
                       plan_version: str) -> tuple[PlacementDecision, ...]:
    rows = conn.execute(
        "SELECT * FROM placement_decisions WHERE plan_version = ? AND "
        "superseded_by IS NULL ORDER BY created_at, record_id", (plan_version,),
    ).fetchall()
    return tuple(_from_row(row) for row in rows)

