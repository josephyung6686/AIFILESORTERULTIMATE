# src/eval_harness/comparison.py
"""Contract out §7 — the run-to-run comparison record.

It has no aggregate accuracy field and the renderer must not compute one. §8.5:
"A single overall 'accuracy' number hides the mechanism that needs repair." Every
dimension gets a block, always, including an empty one.

Deferral is reported separately from divergence, so a run whose only change is a
different ceiling produces zero new divergences (§8.6).
"""
from __future__ import annotations

import json
import sqlite3
import uuid

from eval_harness.run import VERSION_AXES, VERSION_TUPLE_FIELDS
from eval_harness.store import canonical_json
from eval_harness.vocabulary import DIMENSIONS

COMPARISON_DDL = """
CREATE TABLE IF NOT EXISTS comparison (
    comparison_id           TEXT PRIMARY KEY,
    baseline_run_id         TEXT NOT NULL REFERENCES run_manifest (run_id),
    candidate_run_id        TEXT NOT NULL REFERENCES run_manifest (run_id),
    bundle_id               TEXT NOT NULL,
    version_tuple_delta     TEXT NOT NULL,
    ceilings_differ         INTEGER NOT NULL,
    ceilings_differing_keys TEXT NOT NULL,
    disagreements           TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS comparison_dimension (
    comparison_id         TEXT NOT NULL REFERENCES comparison (comparison_id),
    dimension             TEXT NOT NULL,
    newly_matching        TEXT NOT NULL,
    newly_divergent       TEXT NOT NULL,
    unchanged_count       INTEGER NOT NULL,
    deferral_changed      TEXT NOT NULL,
    attribution_histogram TEXT NOT NULL,
    PRIMARY KEY (comparison_id, dimension)
);
"""


class DifferentBundles(Exception):
    """§8.5 compares THE SAME bundle across versions. Two corpora is not that."""


def _verdicts(conn: sqlite3.Connection, run_id: str) -> dict[tuple[str, str], sqlite3.Row]:
    return {(r["dimension"], r["subject_ref"]): r for r in conn.execute(
        "SELECT dimension, subject_ref, verdict, attributed_stage FROM assertion "
        "WHERE run_id = ?", (run_id,))}


def compare_runs(conn: sqlite3.Connection, baseline_run_id: str,
                 candidate_run_id: str) -> str:
    """Compare two runs over one bundle. Returns the comparison_id."""
    from eval_harness.assertions import PASSING_VERDICTS
    from eval_harness.run import get_run, get_version_tuple, run_ceilings

    baseline, candidate = get_run(conn, baseline_run_id), get_run(conn, candidate_run_id)
    if baseline["bundle_id"] != candidate["bundle_id"]:
        raise DifferentBundles(
            f"{baseline['bundle_id']} vs {candidate['bundle_id']}: §8.5 compares "
            "the same bundle re-processed, not two corpora"
        )

    base_tuple = get_version_tuple(conn, baseline["version_tuple_ref"])
    cand_tuple = get_version_tuple(conn, candidate["version_tuple_ref"])
    delta = {}
    for field in VERSION_TUPLE_FIELDS:
        if base_tuple.get(field) != cand_tuple.get(field):
            delta[field] = {"baseline": base_tuple.get(field),
                            "candidate": cand_tuple.get(field),
                            # six of the seven are §8.5's named axes; the seventh
                            # is I4's tier set and is reported as what it is.
                            "is_8_5_axis": field in VERSION_AXES}

    base_ceilings, cand_ceilings = run_ceilings(conn, baseline_run_id), run_ceilings(
        conn, candidate_run_id)
    differing_keys = sorted(
        k for k in set(base_ceilings) | set(cand_ceilings)
        if base_ceilings.get(k) != cand_ceilings.get(k))
    # Labelled, not refused, and not interpreted: §8.6 supplies no polarity for a
    # ceiling, so P2 does not decide that one run's ceiling was "lower".

    base_verdicts, cand_verdicts = _verdicts(conn, baseline_run_id), _verdicts(
        conn, candidate_run_id)
    comparison_id = str(uuid.uuid4())
    disagreements = []
    blocks = {d: {"newly_matching": [], "newly_divergent": [], "unchanged_count": 0,
                  "deferral_changed": [], "attribution_histogram": {}}
              for d in DIMENSIONS}

    for key in sorted(set(base_verdicts) | set(cand_verdicts)):
        dimension, subject_ref = key
        before = base_verdicts.get(key)
        after = cand_verdicts.get(key)
        before_verdict = None if before is None else before["verdict"]
        after_verdict = None if after is None else after["verdict"]
        block = blocks[dimension]
        if before_verdict == after_verdict:
            block["unchanged_count"] += 1
            continue
        disagreements.append({"subject_ref": subject_ref, "dimension": dimension,
                              "baseline_verdict": before_verdict,
                              "candidate_verdict": after_verdict,
                              "attributed_stage": (None if after is None
                                                   else after["attributed_stage"])})
        if "deferred" in (before_verdict, after_verdict):
            # §8.6 — a budget event, reported as one and never as a regression.
            block["deferral_changed"].append(subject_ref)
            continue
        # A move between two FAILING verdicts falls through both branches on
        # purpose: it did not newly diverge, it did not newly match, and it is not
        # a deferral. It is in `disagreements` and in none of the four counts, so
        # the four are a floor on a dimension's subjects and never a total. See
        # the task prose; do not add a fifth bucket to make the sum close.
        if after_verdict in PASSING_VERDICTS and before_verdict not in PASSING_VERDICTS:
            block["newly_matching"].append(subject_ref)
        elif before_verdict in PASSING_VERDICTS and after_verdict not in PASSING_VERDICTS:
            block["newly_divergent"].append(subject_ref)
        if after is not None and after["attributed_stage"]:
            histogram = block["attribution_histogram"]
            histogram[after["attributed_stage"]] = histogram.get(
                after["attributed_stage"], 0) + 1

    conn.execute(
        "INSERT INTO comparison (comparison_id, baseline_run_id, candidate_run_id, "
        "bundle_id, version_tuple_delta, ceilings_differ, ceilings_differing_keys, "
        "disagreements) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (comparison_id, baseline_run_id, candidate_run_id, baseline["bundle_id"],
         canonical_json(delta), 1 if differing_keys else 0,
         canonical_json(differing_keys), canonical_json(disagreements)),
    )
    for dimension in DIMENSIONS:                 # every one, always
        block = blocks[dimension]
        conn.execute(
            "INSERT INTO comparison_dimension (comparison_id, dimension, "
            "newly_matching, newly_divergent, unchanged_count, deferral_changed, "
            "attribution_histogram) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (comparison_id, dimension, canonical_json(block["newly_matching"]),
             canonical_json(block["newly_divergent"]), block["unchanged_count"],
             canonical_json(block["deferral_changed"]),
             canonical_json(block["attribution_histogram"])),
        )
    return comparison_id


def get_comparison(conn: sqlite3.Connection, comparison_id: str) -> dict:
    """The comparison record. No aggregate field exists to return."""
    row = conn.execute("SELECT * FROM comparison WHERE comparison_id = ?",
                       (comparison_id,)).fetchone()
    if row is None:
        raise KeyError(comparison_id)
    per_dimension = {}
    for block in conn.execute(
            "SELECT * FROM comparison_dimension WHERE comparison_id = ?",
            (comparison_id,)):
        per_dimension[block["dimension"]] = {
            "newly_matching": json.loads(block["newly_matching"]),
            "newly_divergent": json.loads(block["newly_divergent"]),
            "unchanged_count": block["unchanged_count"],
            "deferral_changed": json.loads(block["deferral_changed"]),
            "attribution_histogram": json.loads(block["attribution_histogram"]),
        }
    return {
        "comparison_id": row["comparison_id"],
        "baseline_run_id": row["baseline_run_id"],
        "candidate_run_id": row["candidate_run_id"],
        "bundle_id": row["bundle_id"],
        "version_tuple_delta": json.loads(row["version_tuple_delta"]),
        "ceilings_differ": bool(row["ceilings_differ"]),
        "ceilings_differing_keys": json.loads(row["ceilings_differing_keys"]),
        "per_dimension": per_dimension,
        "disagreements": json.loads(row["disagreements"]),
    }
