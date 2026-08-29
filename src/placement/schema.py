"""P11's own SQLite tables inside P1's single database. Append-only by trigger.

`plan_version` is on every table here, and that is the opposite of P9's rule for a
reason §8.8 states outright: a placement decision, a group plan, a residual set
decision and the whole §6.2 index are *projections of one frozen tree*, and a
projection whose tree changed is a different projection. Facts, observations,
files and accepted groups stay in the shared evidence database and are not
duplicated per version.

The `payload` column stores the record as canonical JSON and is its ONE home. The
named columns beside it are the addresses and keys the reads P11 actually performs
need -- current-by-subject, history, by-plan-version, by-node -- and never a second
home for a value: `store._from_row` rebuilds the record from `payload` alone, so a
named column that disagreed with it would be unreachable rather than merely wrong.

A field added to `PlacementDecision` therefore cannot be silently unstored:
`dataclasses.asdict` puts it in the payload and `_from_row` reads it back by
`DECISION_FIELDS`, which is derived from the record itself. `tests/p11/
test_p11_store.py::test_every_record_field_survives_the_round_trip` is the proof.
"""
from __future__ import annotations

import sqlite3

from database_agent.supersede import SUPERSEDE_COLUMNS

#: Every table P11 owns, mapped to its columns. All carry `plan_version`. The
#: guards below are GENERATED from these lists, so a column added to a table is
#: immutable by construction rather than by a second list somebody has to update.
_COLUMNS: dict[str, tuple[tuple[str, str], ...]] = {
    "placement_decisions": (
        ("record_id", "TEXT PRIMARY KEY"),
        ("subject_ref", "TEXT NOT NULL"),
        ("plan_version", "TEXT NOT NULL"),
        ("origin_stage", "TEXT NOT NULL"),
        ("outcome", "TEXT NOT NULL"),
        ("node_id", "TEXT"),
        ("group_plan_id", "TEXT"),
        ("returned_from", "TEXT"),
        ("review_policy", "TEXT"),
        ("created_at", "TEXT NOT NULL"),
        ("payload", "TEXT NOT NULL"),
    ),
    "placement_index_entries": (
        ("record_id", "TEXT PRIMARY KEY"),
        ("plan_version", "TEXT NOT NULL"),
        ("node_id", "TEXT NOT NULL"),
        ("payload", "TEXT NOT NULL"),
        ("created_at", "TEXT NOT NULL"),
    ),
    # §6.2's index, as an INDEX. `placement_index_entries` is the record store --
    # one payload per node, read whole when a caller wants a node's profile. This
    # is the inverted projection `retrieve` reads: one row per (node, term), so a
    # subject's stated fields, group ids and folder labels select the nodes that
    # can possibly matter instead of every node the user froze. `00`:105 is the
    # reason it exists at all: "the engine retrieves the few most relevant
    # approved destination nodes, RATHER THAN SEARCHING THE ENTIRE FILESYSTEM".
    #
    # `source_field` names the `IndexEntry` FIELD the term was projected from, not
    # the §6.3 channel it drives -- because an `expected_values` term drives a
    # channel when it MATCHES and a suppression when it contradicts, and calling
    # it `direct_fact` would name only half of its job. The channel vocabulary
    # stays in `retrieval.py`, which is the module that owns the concept.
    "placement_index_terms": (
        ("record_id", "TEXT PRIMARY KEY"),
        ("plan_version", "TEXT NOT NULL"),
        ("node_id", "TEXT NOT NULL"),
        ("source_field", "TEXT NOT NULL"),
        ("term_key", "TEXT NOT NULL"),
        ("term_value", "TEXT NOT NULL"),
        ("ordinal", "INTEGER NOT NULL"),
        ("created_at", "TEXT NOT NULL"),
    ),
    # How many rows the table above holds for one term key, written by the one
    # writer of that table, in the one transaction that writes it.
    #
    # This exists so that "how many nodes state this field?" is not a question
    # whose ANSWER is the size of the tree. §6.3 rules out every node that states
    # a field the subject states with a different value, and the record has to say
    # how many were ruled out (SPEC:502-504) -- but counting them per subject is
    # the O(files x nodes) read `planning/58-SCALE-STRESS.md` §2 measured, and a
    # `COUNT(*)` is that same read with a smaller constant.
    #
    # It is a materialised aggregate and therefore a second home for a value,
    # which `placement_index_entries` deliberately avoids. The reason it is
    # tolerable here and nowhere else is that it is DERIVED FROM AN APPEND-ONLY
    # TABLE THAT ONE FUNCTION WRITES ONCE PER PLAN VERSION, and
    # `tests/p11/test_p11_retrieval_scale.py` asserts row-for-row that the stored
    # count equals a live `COUNT(*)`, so drift fails a test rather than quietly
    # under-counting a suppression.
    "placement_index_term_counts": (
        ("record_id", "TEXT PRIMARY KEY"),
        ("plan_version", "TEXT NOT NULL"),
        ("source_field", "TEXT NOT NULL"),
        ("term_key", "TEXT NOT NULL"),
        ("row_count", "INTEGER NOT NULL"),
        ("created_at", "TEXT NOT NULL"),
    ),
    "placement_group_plans": (
        ("record_id", "TEXT PRIMARY KEY"),
        ("plan_version", "TEXT NOT NULL"),
        ("group_id", "TEXT NOT NULL"),
        ("shared_parent_node_id", "TEXT"),
        ("payload", "TEXT NOT NULL"),
        ("created_at", "TEXT NOT NULL"),
    ),
    "residual_sets": (
        ("record_id", "TEXT PRIMARY KEY"),
        ("plan_version", "TEXT NOT NULL"),
        ("label", "TEXT NOT NULL"),
        ("payload", "TEXT NOT NULL"),
        ("created_at", "TEXT NOT NULL"),
    ),
    "residual_set_decisions": (
        ("record_id", "TEXT PRIMARY KEY"),
        ("plan_version", "TEXT NOT NULL"),
        ("set_id", "TEXT NOT NULL"),
        ("choice", "TEXT NOT NULL"),
        ("node_id", "TEXT"),
        ("decided_at", "TEXT NOT NULL"),
        ("payload", "TEXT NOT NULL"),
    ),
}

P11_TABLES: tuple[str, ...] = tuple(_COLUMNS)

_SUPERSEDE = ", ".join(f"{name} TEXT" for name in SUPERSEDE_COLUMNS)

_INDEXES = """
CREATE INDEX IF NOT EXISTS placement_decisions_plan
    ON placement_decisions (plan_version, subject_ref);
CREATE INDEX IF NOT EXISTS placement_decisions_node
    ON placement_decisions (plan_version, node_id);
CREATE UNIQUE INDEX IF NOT EXISTS one_current_placement_decision
    ON placement_decisions (plan_version, subject_ref)
    WHERE superseded_by IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS one_current_index_entry
    ON placement_index_entries (plan_version, node_id)
    WHERE superseded_by IS NULL;

CREATE INDEX IF NOT EXISTS placement_index_terms_lookup
    ON placement_index_terms (plan_version, source_field, term_key, term_value);

-- The other direction. The lookup above answers "which nodes carry this term?";
-- this one answers "which terms does this node carry?", which is the question
-- §6.3's suppression asks once the four channels have named the nodes the
-- subject's own evidence reaches. Without it that read is a scan of every term
-- in the plan, which is the cost the narrowing exists to remove.
CREATE INDEX IF NOT EXISTS placement_index_terms_by_node
    ON placement_index_terms (plan_version, source_field, node_id, term_key);

CREATE UNIQUE INDEX IF NOT EXISTS one_current_term_count
    ON placement_index_term_counts (plan_version, source_field, term_key)
    WHERE superseded_by IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS one_current_group_plan
    ON placement_group_plans (plan_version, group_id)
    WHERE superseded_by IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS one_current_set_decision
    ON residual_set_decisions (plan_version, set_id)
    WHERE superseded_by IS NULL;
"""


def _create_table(table: str) -> str:
    body = ",\n    ".join(f"{name:<22} {kind}" for name, kind in _COLUMNS[table])
    return f"CREATE TABLE IF NOT EXISTS {table} (\n    {body},\n    {_SUPERSEDE}\n);"


#: §8.2 in SQL, in P9's idiom (`grouping/schema.py:157-178`). `BEFORE UPDATE OF`
#: names every column that is NOT a supersede link, so `mark_superseded` -- which
#: writes exactly the three P1 publishes -- passes, and a writer correcting an
#: outcome, a payload or a plan version in place fails rather than losing the
#: original. A blanket `BEFORE UPDATE` would make supersession impossible; a
#: trigger conditioned only on `payload` would leave `outcome` rewritable.
PLACEMENT_DDL = "\n".join(_create_table(table) for table in P11_TABLES) + _INDEXES

_GUARDS = "\n".join(
    f"""
CREATE TRIGGER IF NOT EXISTS {table}_no_delete
BEFORE DELETE ON {table}
BEGIN SELECT RAISE(ABORT, '{table} is append-only (§8.2)'); END;

CREATE TRIGGER IF NOT EXISTS {table}_never_overwritten
BEFORE UPDATE OF {", ".join(name for name, _ in _COLUMNS[table])} ON {table}
BEGIN SELECT RAISE(ABORT, '{table} rewrites nothing but its supersede link'); END;
"""
    for table in P11_TABLES
)


def create_placement_schema(conn: sqlite3.Connection) -> None:
    """Create P11's tables. Idempotent; safe on an existing database."""
    conn.executescript(PLACEMENT_DDL)
    conn.executescript(_GUARDS)
