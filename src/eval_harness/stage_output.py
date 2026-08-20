# src/eval_harness/stage_output.py
"""Contract out §4 — the one record every measured part emits.

P2 owns the envelope; the producing part owns `payload`, which is stored verbatim
and never parsed. The envelope's vocabulary and the producing part's record
vocabulary are different vocabularies, and a part's own values are refused here.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Sequence

from eval_harness.store import canonical_json
from eval_harness.vocabulary import (
    BUDGET_STATES, OUTCOMES, check_dimension, check_stage,
)

#: Contract out §4, in order. Nine.
ENVELOPE_FIELDS: tuple[str, ...] = (
    "run_id", "stage_id", "subject_ref", "outcome", "payload",
    "version_tuple_ref", "inputs", "budget_state", "produced_at",
)

#: Values that belong to a producing part's OWN record and may never appear in the
#: envelope. P11's SPEC publishes this rule and this list; P2 enforces it so a
#: mis-mapped run fails at the writer instead of during comparison. This is not
#: P2 adopting P11's vocabulary — nothing here is ever WRITTEN, only refused.
_FOREIGN_OUTCOMES = frozenset({
    "place", "return_to_placement", "mark_review_later", "leave_in_place",
    "mark_state", "abstain", "ask_user",
})

STAGE_DDL = """
CREATE TABLE IF NOT EXISTS stage_output (
    stage_output_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id            TEXT NOT NULL REFERENCES run_manifest (run_id),
    stage_id          TEXT NOT NULL,
    subject_ref       TEXT NOT NULL,
    outcome           TEXT NOT NULL,
    payload           TEXT,               -- opaque; never parsed by P2
    version_tuple_ref TEXT NOT NULL,
    inputs            TEXT NOT NULL,      -- canonical JSON array of subject_refs
    budget_state      TEXT NOT NULL,
    produced_at       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS stage_output_run ON stage_output (run_id, stage_id);
CREATE INDEX IF NOT EXISTS stage_output_subject ON stage_output (run_id, subject_ref);

CREATE TABLE IF NOT EXISTS stage_dimension_value (
    run_id          TEXT NOT NULL REFERENCES run_manifest (run_id),
    stage_output_id INTEGER NOT NULL REFERENCES stage_output (stage_output_id),
    stage_id        TEXT NOT NULL,        -- the EMITTING stage, which names itself
    dimension       TEXT NOT NULL,
    subject_ref     TEXT NOT NULL,
    outcome         TEXT NOT NULL,
    value           TEXT,                 -- canonical JSON, or NULL when nothing was produced
    PRIMARY KEY (run_id, dimension, subject_ref)
);
"""


class ForeignVocabulary(Exception):
    """A producing part's own record value was written into P2's envelope."""


@dataclass(frozen=True)
class DimensionValue:
    """One measured value the producing part hands P2 alongside its opaque payload.

    Each carries its own `outcome`: one stage output may produce for one subject
    and abstain for another, and §8.5 measures abstention as an outcome.
    """
    dimension: str
    subject_ref: str
    outcome: str
    value: Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _check_outcome(outcome: str) -> str:
    if outcome in _FOREIGN_OUTCOMES:
        raise ForeignVocabulary(
            f"{outcome!r} is a producing part's own record value and may not be "
            f"written into stage_output; the envelope's outcomes are {OUTCOMES}"
        )
    if outcome not in OUTCOMES:
        raise ValueError(f"outcome {outcome!r} is not one of {OUTCOMES}")
    return outcome


def record_stage_output(conn: sqlite3.Connection, *, run_id: str, stage_id: str,
                        subject_ref: str, outcome: str, payload: str | None,
                        version_tuple_ref: str, inputs: Sequence[str],
                        budget_state: str,
                        dimension_values: Sequence[DimensionValue] = ()) -> int:
    """Write one envelope, plus the dimension values the stage hands over.

    §8.6: a budget deferral is `deferred` with `ceiling_reached` and is never
    `abstained`. The pairing is enforced here, because P2 Done-means 6 depends on
    it: a run whose only change is a lower ceiling must produce zero new
    divergences, which is only true if a deferral never reaches a quality verdict.
    """
    check_stage(stage_id)
    _check_outcome(outcome)
    if budget_state not in BUDGET_STATES:
        raise ValueError(f"budget_state {budget_state!r} is not one of {BUDGET_STATES}")
    if outcome == "deferred" and budget_state != "ceiling_reached":
        raise ValueError("outcome 'deferred' requires budget_state 'ceiling_reached' (§8.6)")
    if budget_state == "ceiling_reached" and outcome == "abstained":
        raise ValueError(
            "a ceiling-reached stage is 'deferred', never 'abstained': §8.6 forbids "
            "cost exhaustion becoming a judgement about evidence"
        )
    for value in dimension_values:
        check_dimension(value.dimension)
        _check_outcome(value.outcome)

    cursor = conn.execute(
        "INSERT INTO stage_output (run_id, stage_id, subject_ref, outcome, payload, "
        "version_tuple_ref, inputs, budget_state, produced_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (run_id, stage_id, subject_ref, outcome, payload, version_tuple_ref,
         canonical_json(list(inputs)), budget_state, _now()),
    )
    stage_output_id = cursor.lastrowid
    for value in dimension_values:
        conn.execute(
            "INSERT INTO stage_dimension_value (run_id, stage_output_id, stage_id, "
            "dimension, subject_ref, outcome, value) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (run_id, stage_output_id, stage_id, value.dimension, value.subject_ref,
             value.outcome,
             None if value.value is None else canonical_json(value.value)),
        )
    return stage_output_id


def stage_outputs(conn: sqlite3.Connection, run_id: str, *,
                  stage_id: str | None = None) -> list[sqlite3.Row]:
    if stage_id is None:
        return conn.execute(
            "SELECT * FROM stage_output WHERE run_id = ? ORDER BY stage_output_id",
            (run_id,)).fetchall()
    return conn.execute(
        "SELECT * FROM stage_output WHERE run_id = ? AND stage_id = ? "
        "ORDER BY stage_output_id", (run_id, check_stage(stage_id))).fetchall()


def dimension_values(conn: sqlite3.Connection, run_id: str, *,
                     dimension: str | None = None) -> list[sqlite3.Row]:
    if dimension is None:
        return conn.execute(
            "SELECT * FROM stage_dimension_value WHERE run_id = ? "
            "ORDER BY dimension, subject_ref", (run_id,)).fetchall()
    return conn.execute(
        "SELECT * FROM stage_dimension_value WHERE run_id = ? AND dimension = ? "
        "ORDER BY subject_ref", (run_id, check_dimension(dimension))).fetchall()


def stage_payload(conn: sqlite3.Connection, stage_output_id: int) -> str | None:
    """The payload exactly as it was handed over. P2 has never parsed it."""
    row = conn.execute("SELECT payload FROM stage_output WHERE stage_output_id = ?",
                       (stage_output_id,)).fetchone()
    return None if row is None else row["payload"]
