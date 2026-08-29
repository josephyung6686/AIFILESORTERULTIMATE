# src/eval_harness/attribution.py
"""Contract out §6 — `attributed_stage`.

§8.5: "identify whether the error BEGAN with extraction, factual validation,
retrieval, graph construction, LLM interpretation, grouping, template generation,
tree design, candidate-node retrieval, or placement scoring."

The traversal walks whatever `inputs[]` edges the emitting parts recorded. It does
NOT require cross-subject edges and does not forbid them — SPEC Open question 3
asks whether attribution should follow them, and this module answers it neither
way: given cross-subject edges it follows them, given none it stays inside the
subject's own chain.
"""
from __future__ import annotations

import json
import sqlite3

from eval_harness.vocabulary import stage_order

#: SPEC Contract out §6, verbatim: the verdicts that make an ANCESTOR the origin.
ANCESTOR_VERDICTS: frozenset[str] = frozenset({"divergent", "asserted_incorrectly"})

#: Done-means 4: every wrong terminal outcome yields exactly one attributed stage.
#: An incorrect abstention is a wrong terminal outcome; a deferral and a `not_run`
#: are not, and are attributed to nothing.
FAILING_VERDICTS: frozenset[str] = ANCESTOR_VERDICTS | {"abstained_incorrectly"}


def _stage_verdicts(conn: sqlite3.Connection, run_id: str) -> dict[str, set[str]]:
    """(stage_id, subject_ref) -> the verdicts of assertions on values it emitted."""
    out: dict[str, set[str]] = {}
    for row in conn.execute(
            "SELECT v.stage_id, v.subject_ref, a.verdict "
            "FROM stage_dimension_value v JOIN assertion a "
            "  ON a.run_id = v.run_id AND a.dimension = v.dimension "
            "     AND a.subject_ref = v.subject_ref "
            "WHERE v.run_id = ?", (run_id,)):
        out.setdefault((row["stage_id"], row["subject_ref"]), set()).add(row["verdict"])
    return out


def _edges(conn: sqlite3.Connection, run_id: str):
    """subject_ref -> the stage outputs that carry it, and their inputs[]."""
    by_subject: dict[str, list[tuple[str, list[str]]]] = {}
    for row in conn.execute(
            "SELECT stage_id, subject_ref, inputs FROM stage_output WHERE run_id = ?",
            (run_id,)):
        by_subject.setdefault(row["subject_ref"], []).append(
            (row["stage_id"], json.loads(row["inputs"])))
    return by_subject


def attribute_run(conn: sqlite3.Connection, run_id: str) -> int:
    """Fill `assertion.attributed_stage` for this run. Returns rows attributed.

    Exactly one stage per wrong terminal outcome: among every qualifying stage
    reachable on the chain — including the emitting stage itself — the attributed
    one is the smallest `stage_order`, which is §8.5's list order and therefore
    §4.10's and §6.12's pipeline order. `stage_order` is injective over the ten,
    so the minimum is unique.
    """
    verdicts = _stage_verdicts(conn, run_id)
    by_subject = _edges(conn, run_id)
    emitters = {
        (row["dimension"], row["subject_ref"]): row["stage_id"]
        for row in conn.execute(
            "SELECT dimension, subject_ref, stage_id FROM stage_dimension_value "
            "WHERE run_id = ?", (run_id,))
    }

    attributed = 0
    for row in conn.execute(
            "SELECT assertion_id, dimension, subject_ref, verdict FROM assertion "
            "WHERE run_id = ?", (run_id,)).fetchall():
        if row["verdict"] not in FAILING_VERDICTS:
            continue
        emitting_stage = emitters.get((row["dimension"], row["subject_ref"]))
        if emitting_stage is None:
            continue
        candidates = {emitting_stage}
        seen: set[tuple[str, str]] = set()
        frontier = [(emitting_stage, row["subject_ref"])]
        while frontier:
            stage_id, subject_ref = frontier.pop()
            if (stage_id, subject_ref) in seen:
                continue          # a cycle in inputs[] is a defect upstream, not a hang here
            seen.add((stage_id, subject_ref))
            for candidate_stage, inputs in by_subject.get(subject_ref, []):
                if candidate_stage != stage_id:
                    continue
                for input_ref in inputs:
                    for ancestor_stage, _ in by_subject.get(input_ref, []):
                        if verdicts.get((ancestor_stage, input_ref), set()) & ANCESTOR_VERDICTS:
                            candidates.add(ancestor_stage)
                        frontier.append((ancestor_stage, input_ref))
        earliest = min(candidates, key=stage_order)
        conn.execute("UPDATE assertion SET attributed_stage = ? WHERE assertion_id = ?",
                     (earliest, row["assertion_id"]))
        attributed += 1
    return attributed


def attribution_histogram(conn: sqlite3.Connection, run_id: str) -> dict[str, int]:
    """attributed_stage -> count. A count per stage and no total: §8.5 forbids the
    single number, and a total over ten stages is the shape that invites one."""
    return {row["attributed_stage"]: row["n"] for row in conn.execute(
        "SELECT attributed_stage, count(*) AS n FROM assertion "
        "WHERE run_id = ? AND attributed_stage IS NOT NULL "
        "GROUP BY attributed_stage", (run_id,))}
