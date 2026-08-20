# src/eval_harness/shadow.py
"""Contract out §8 — shadow mode.

§8.5: "A new model or algorithm can generate parallel recommendations without
changing the user-visible tree or move plan." The three things that must stay
empty are columns, checked by `assert_shadow_wrote_nothing`, not promises.

P2 chooses no selection criterion (SPEC Open question 12), promotes no
adjudication into an §8.7 correction (Open question 10), and adds no shadow budget
key (Open question 8).
"""
from __future__ import annotations

import json
import sqlite3
from typing import Callable, Iterable, Mapping, Sequence

# EVAL_TABLES is what `foreign_table_counts` subtracts to get "every table P2 does
# not own". Importing it, rather than restating the list here, is the same
# one-owner rule the rest of this plan follows: a table added to store.py and not
# to this import would silently become a table the shadow proof stops watching.
from eval_harness.store import EVAL_TABLES, canonical_json

SHADOW_DDL = """
CREATE TABLE IF NOT EXISTS shadow_run (
    shadow_run_id          TEXT PRIMARY KEY REFERENCES run_manifest (run_id),
    live_run_id            TEXT NOT NULL REFERENCES run_manifest (run_id),
    comparison_id          TEXT NOT NULL,
    shadow_namespace       TEXT NOT NULL,
    plan_version_writes    TEXT NOT NULL DEFAULT '[]',   -- MUST be empty (§8.8)
    move_plan_entries      TEXT NOT NULL DEFAULT '[]',   -- MUST be empty (§8.3)
    user_visible_tree_delta TEXT NOT NULL DEFAULT '[]',  -- MUST be empty (§8.5)
    surfaced_examples      TEXT NOT NULL,
    model_call_audit_refs  TEXT NOT NULL,                -- P7's audit ids (§8.4)
    foreign_table_counts   TEXT NOT NULL                 -- row counts of every table
                                                         -- P2 does not own, at open
);
CREATE TABLE IF NOT EXISTS review_adjudication (
    adjudication_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    shadow_run_id    TEXT NOT NULL REFERENCES shadow_run (shadow_run_id),
    subject_ref      TEXT NOT NULL,
    dimension        TEXT NOT NULL,
    reviewer_verdict TEXT NOT NULL,
    note             TEXT
);
"""

#: The three columns §8.5, §8.3 and §8.8 require to stay empty.
EMPTY_COLUMNS: tuple[str, ...] = (
    "plan_version_writes", "move_plan_entries", "user_visible_tree_delta",
)


class UnauditedModelCall(Exception):
    """A model-enabled shadow run carried no §8.4 audit reference."""


class ShadowWroteLiveState(Exception):
    """A shadow run changed the user-visible tree, a plan version, or the move plan."""


def run_shadow(conn: sqlite3.Connection, bundle_id: str, *, version_tuple: dict,
               budget_ceilings: Mapping[str, int], run_settings: Mapping[str, bool],
               adapters: Mapping[str, object], live_run_id: str,
               select: Callable[[list], Sequence],
               model_call_audit_refs: Iterable[str] = ()) -> str:
    """Run a bundle in shadow and compare it with the live run. Returns the run id.

    `select` has no default. §8.5 surfaces "only selected examples for human
    review" and states no criterion; SPEC Open question 12 is open, and a default
    here would answer it.

    The same `budget_ceilings` a replay takes: §8.6's list has no shadow entry and
    P2 adds no key (Open question 8).
    """
    from eval_harness.assertions import assert_run
    from eval_harness.attribution import attribute_run
    from eval_harness.comparison import compare_runs, get_comparison
    from eval_harness.replay import replay_bundle

    # Taken BEFORE any adapter runs: this is the baseline `assert_shadow_wrote_nothing`
    # diffs against, and a snapshot taken afterwards would prove nothing.
    opened_counts = foreign_table_counts(conn)

    refs = list(model_call_audit_refs)
    if run_settings.get("model_enabled") and not refs:
        raise UnauditedModelCall(
            "a shadow model call is still a model call: §8.4 records every one in "
            "the consent-aware audit record. P2 does not write that record; it "
            "requires the reference and links to it."
        )
    shadow_run_id = replay_bundle(
        conn, bundle_id, version_tuple=version_tuple,
        budget_ceilings=budget_ceilings, run_settings=run_settings,
        adapters=adapters, run_kind="shadow",
    )
    assert_run(conn, shadow_run_id)
    attribute_run(conn, shadow_run_id)
    comparison_id = compare_runs(conn, live_run_id, shadow_run_id)
    disagreements = get_comparison(conn, comparison_id)["disagreements"]
    surfaced = list(select(disagreements))
    conn.execute(
        "INSERT INTO shadow_run (shadow_run_id, live_run_id, comparison_id, "
        "shadow_namespace, surfaced_examples, model_call_audit_refs, "
        "foreign_table_counts) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (shadow_run_id, live_run_id, comparison_id, shadow_run_id,
         canonical_json(surfaced), canonical_json(refs),
         canonical_json(opened_counts)),
    )
    return shadow_run_id


def shadow_record(conn: sqlite3.Connection, shadow_run_id: str) -> dict:
    from eval_harness.comparison import get_comparison

    row = conn.execute("SELECT * FROM shadow_run WHERE shadow_run_id = ?",
                       (shadow_run_id,)).fetchone()
    if row is None:
        raise KeyError(shadow_run_id)
    return {
        "shadow_run_id": row["shadow_run_id"],
        "live_run_id": row["live_run_id"],
        "shadow_namespace": row["shadow_namespace"],
        "plan_version_writes": json.loads(row["plan_version_writes"]),
        "move_plan_entries": json.loads(row["move_plan_entries"]),
        "user_visible_tree_delta": json.loads(row["user_visible_tree_delta"]),
        "disagreement_set": get_comparison(conn, row["comparison_id"])["disagreements"],
        "surfaced_examples": json.loads(row["surfaced_examples"]),
        "model_call_audit_refs": json.loads(row["model_call_audit_refs"]),
        "foreign_table_counts": json.loads(row["foreign_table_counts"]),
    }


def foreign_table_counts(conn: sqlite3.Connection) -> dict[str, int]:
    """Row counts for every table P2 does not own.

    P2 owns `EVAL_TABLES`. Everything else in the database belongs to another
    part — P1's `files` and `events` today, P10's plan versions and P12's move
    plan when they land. A shadow run must leave all of it byte-for-byte alone.
    """
    names = [r["name"] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
    ) if r["name"] not in EVAL_TABLES]
    return {n: conn.execute(f"SELECT count(*) AS c FROM {n}").fetchone()["c"] for n in names}


def assert_shadow_wrote_nothing(conn: sqlite3.Connection, shadow_run_id: str) -> None:
    """Done-means 9. Raises rather than reporting.

    Two checks, and the second is the one that is actually a proof.

    The three columns are self-reported: a shadow adapter that writes a plan
    version straight into P10's table never touches them, so on their own they
    prove only that a well-behaved adapter behaved well. That is an honour system
    wearing the shape of an assertion.

    So the run also snapshots the row count of EVERY table P2 does not own, at
    open, and this compares. Any foreign table that grew or shrank during the run
    fails, whether or not the adapter admitted to it. It works today against P1's
    `files` and `events`, and it covers P10's plan versions and P12's move plan on
    the day those tables exist — without this function being edited, which is the
    point: the check must not depend on remembering to extend it.
    """
    record = shadow_record(conn, shadow_run_id)
    non_empty = [name for name in EMPTY_COLUMNS if record[name]]
    if non_empty:
        raise ShadowWroteLiveState(
            f"shadow run {shadow_run_id} wrote {non_empty}; §8.5 requires parallel "
            "recommendations WITHOUT changing the user-visible tree or move plan"
        )

    # `shadow_record` already decodes every JSON column it returns, this one
    # included — decoding again here would be a second `json.loads` over a dict.
    opened = record["foreign_table_counts"]
    now = foreign_table_counts(conn)
    changed = {n: (opened.get(n), now[n]) for n in now if opened.get(n) != now[n]}
    changed.update({n: (opened[n], None) for n in opened if n not in now})
    if changed:
        raise ShadowWroteLiveState(
            f"shadow run {shadow_run_id} changed tables it does not own: {changed}; "
            "§8.5 requires parallel recommendations WITHOUT changing user-visible state"
        )


def record_adjudication(conn: sqlite3.Connection, shadow_run_id: str, *,
                        subject_ref: str, dimension: str, reviewer_verdict: str,
                        note: str | None = None) -> int:
    """The reviewer's verdict on one surfaced disagreement, at RUN scope.

    It judges a candidate algorithm, not a file. It is not promoted into an §8.7
    correction and there is no function here that would: SPEC Open question 10 is
    open, and promotion would give shadow mode a path into user-visible state.
    """
    from eval_harness.vocabulary import check_dimension

    check_dimension(dimension)
    cursor = conn.execute(
        "INSERT INTO review_adjudication (shadow_run_id, subject_ref, dimension, "
        "reviewer_verdict, note) VALUES (?, ?, ?, ?, ?)",
        (shadow_run_id, subject_ref, dimension, reviewer_verdict, note),
    )
    return cursor.lastrowid


def adjudications(conn: sqlite3.Connection, shadow_run_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM review_adjudication WHERE shadow_run_id = ? "
        "ORDER BY adjudication_id", (shadow_run_id,)).fetchall()
