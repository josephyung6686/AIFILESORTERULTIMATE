# src/eval_harness/assertions.py
"""Contract out §6 — the per-stage assertion record.

Seven verdicts, and P2 mints no eighth. Two cases §8.5 does not define a verdict
for — a stage `error`, and an expectation whose kind is `not-applicable` — are
written with a NULL verdict and a named reason: a NULL reads as "no verdict is
defined for this", a fabricated verdict reads as an answer.

There is no threshold and no tolerance anywhere in this module. §8.5 states none,
and SPEC Open question 2 is open.
"""
from __future__ import annotations

import json
import sqlite3

from eval_harness.store import canonical_json
from eval_harness.vocabulary import VERDICTS, check_dimension

#: Done-means 5 — `abstained_correctly` is reported as a pass, not as a miss (§6.10).
PASSING_VERDICTS: frozenset[str] = frozenset({"match", "abstained_correctly"})

ASSERTION_DDL = """
CREATE TABLE IF NOT EXISTS assertion (
    assertion_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id            TEXT NOT NULL REFERENCES run_manifest (run_id),
    dimension         TEXT NOT NULL,
    subject_ref       TEXT NOT NULL,
    expected          TEXT,
    observed          TEXT,
    verdict           TEXT,               -- NULL only for the two undefined cases
    no_verdict_reason TEXT,               -- 'stage_error' | 'expectation_not_applicable'
    attributed_stage  TEXT,               -- filled by Task 11
    evidence_ref      TEXT,               -- a P4 observation_key, never an observation_id
    UNIQUE (run_id, dimension, subject_ref)
);
"""


class ObservationIdRefused(Exception):
    """An assertion cited a per-row observation id instead of the content-addressed key."""


def verdict_for(*, expected_outcome_kind: str, expected_value,
                observed_outcome: str | None,
                observed_value) -> tuple[str | None, str | None]:
    """One verdict, or (None, reason) where §8.5 defines none.

    No tolerance parameter exists, and none can be added without answering SPEC
    Open question 2. Comparison is exact equality over canonical JSON.
    """
    if expected_outcome_kind == "not-applicable":
        return None, "expectation_not_applicable"
    if observed_outcome is None:
        # No stage produced a value for this subject. The stage that would have
        # is absent, or did not decide about it.
        return "not_run", None
    if observed_outcome == "not_implemented":
        return "not_run", None
    if observed_outcome == "error":
        return None, "stage_error"
    if observed_outcome == "deferred":
        # §8.6: a budget event. Never `divergent`, for any dimension.
        return "deferred", None
    if observed_outcome == "abstained":
        if expected_outcome_kind == "abstained":
            return "abstained_correctly", None
        return "abstained_incorrectly", None
    if observed_outcome == "produced":
        if expected_outcome_kind == "abstained":
            return "asserted_incorrectly", None
        if canonical_json(expected_value) == canonical_json(observed_value):
            return "match", None
        return "divergent", None
    raise ValueError(f"unhandled observed outcome {observed_outcome!r}")


def write_assertion(conn: sqlite3.Connection, *, run_id: str, dimension: str,
                    subject_ref: str, expected: str | None, observed: str | None,
                    verdict: str | None, no_verdict_reason: str | None,
                    evidence_ref: str | None) -> int:
    check_dimension(dimension)
    if verdict is not None and verdict not in VERDICTS:
        raise ValueError(f"verdict {verdict!r} is not one of {VERDICTS}")
    if evidence_ref is not None and evidence_ref.startswith("observation_id"):
        raise ObservationIdRefused(
            "an assertion cites a P4 observation by `observation_key`, which is "
            "content-addressed and survives an extractor upgrade; `observation_id` "
            "is per-row and dies on exactly the version change §8.5 measures (§8.7)"
        )
    cursor = conn.execute(
        "INSERT INTO assertion (run_id, dimension, subject_ref, expected, observed, "
        "verdict, no_verdict_reason, evidence_ref) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (run_id, dimension, subject_ref, expected, observed, verdict,
         no_verdict_reason, evidence_ref),
    )
    return cursor.lastrowid


def assert_run(conn: sqlite3.Connection, run_id: str) -> int:
    """Write one assertion per expectation in the run's bundle. Returns the count."""
    from eval_harness.bundle import expectations
    from eval_harness.run import get_run

    bundle_id = get_run(conn, run_id)["bundle_id"]
    observed_rows = {
        (r["dimension"], r["subject_ref"]): r
        for r in conn.execute(
            "SELECT dimension, subject_ref, outcome, value FROM "
            "stage_dimension_value WHERE run_id = ?", (run_id,))
    }
    written = 0
    for expectation in expectations(conn, bundle_id):
        key = (expectation["dimension"], expectation["subject_ref"])
        observed = observed_rows.get(key)
        observed_outcome = None if observed is None else observed["outcome"]
        observed_value = (None if observed is None or observed["value"] is None
                          else json.loads(observed["value"]))
        verdict, reason = verdict_for(
            expected_outcome_kind=expectation["expected_outcome_kind"],
            expected_value=expectation["expected_value"],
            observed_outcome=observed_outcome, observed_value=observed_value,
        )
        write_assertion(
            conn, run_id=run_id, dimension=expectation["dimension"],
            subject_ref=expectation["subject_ref"],
            expected=(None if expectation["expected_value"] is None
                      else canonical_json(expectation["expected_value"])),
            observed=None if observed is None else observed["value"],
            # NULL, and deliberately: Contract out §4's envelope publishes no
            # evidence-ref field, and the observation key that would fill this
            # lives inside `payload`, which §4 makes opaque to P2. Fabricating one
            # or parsing the payload are the only two ways to put a value here,
            # and both are worse than an honest NULL. See the task prose and
            # Known gaps.
            verdict=verdict, no_verdict_reason=reason, evidence_ref=None,
        )
        written += 1
    return written


def assertions(conn: sqlite3.Connection, run_id: str, *,
               dimension: str | None = None) -> list[sqlite3.Row]:
    if dimension is None:
        return conn.execute(
            "SELECT * FROM assertion WHERE run_id = ? ORDER BY dimension, subject_ref",
            (run_id,)).fetchall()
    return conn.execute(
        "SELECT * FROM assertion WHERE run_id = ? AND dimension = ? "
        "ORDER BY subject_ref", (run_id, check_dimension(dimension))).fetchall()


def verdict_counts(conn: sqlite3.Connection, run_id: str) -> dict[str, int]:
    """Per-verdict counts, with the two undefined cases under `unverdicted`.

    §8.6's legibility requirement, applied to evaluation: completed versus
    deferred work is visible, and a partial evaluation is reported as partial.
    There is no total, no ratio, and no aggregate (Done-means 3).
    """
    counts: dict[str, int] = {}
    for row in conn.execute(
            "SELECT verdict, count(*) AS n FROM assertion WHERE run_id = ? "
            "GROUP BY verdict", (run_id,)):
        counts[row["verdict"] or "unverdicted"] = row["n"]
    return counts
