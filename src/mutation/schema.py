"""P12's six tables inside P1's single database. Append-only by trigger (§8.2).

Every table carries a `payload` column holding the record as canonical JSON, and
that column is the record's ONE home. The named columns beside it are the
addresses the reads P12 actually performs need -- by plan, by file, by journal
entry, by plan version -- and never a second home for a value.

`move_journal` deliberately has NO `one_current` index. A journal is a log: an
undo APPENDS a reversal entry and the original stays exactly as it was written
(Contract out §6). A "current" row would be a claim that one of the two entries
replaced the other, which is the opposite of what the record means.
"""
from __future__ import annotations

import sqlite3

from database_agent.supersede import SUPERSEDE_COLUMNS

_COLUMNS: dict[str, tuple[tuple[str, str], ...]] = {
    "move_plans": (
        ("record_id", "TEXT PRIMARY KEY"),
        ("plan_id", "TEXT NOT NULL"),
        ("plan_version", "TEXT NOT NULL"),
        ("decision_ref", "TEXT NOT NULL"),
        ("group_plan_ref", "TEXT"),
        ("file_id", "TEXT NOT NULL"),
        ("node_id", "TEXT NOT NULL"),
        ("required_review_policy", "TEXT"),
        ("created_at", "TEXT NOT NULL"),
        ("payload", "TEXT NOT NULL"),
    ),
    "path_resolutions": (
        ("record_id", "TEXT PRIMARY KEY"),
        ("resolution_id", "TEXT NOT NULL"),
        ("plan_version", "TEXT NOT NULL"),
        ("node_id", "TEXT NOT NULL"),
        ("cross_folder_verdict", "TEXT NOT NULL"),
        ("created_at", "TEXT NOT NULL"),
        ("payload", "TEXT NOT NULL"),
    ),
    "execution_records": (
        ("record_id", "TEXT PRIMARY KEY"),
        ("plan_id", "TEXT NOT NULL"),
        ("plan_version", "TEXT NOT NULL"),
        ("result", "TEXT NOT NULL"),
        ("mode", "TEXT"),
        ("final_destination_path", "TEXT"),
        ("finished_at", "TEXT NOT NULL"),
        ("payload", "TEXT NOT NULL"),
    ),
    "collision_resolutions": (
        ("record_id", "TEXT PRIMARY KEY"),
        ("plan_id", "TEXT NOT NULL"),
        ("colliding_destination_path", "TEXT NOT NULL"),
        ("collision_kind", "TEXT NOT NULL"),
        ("behaviour_applied", "TEXT NOT NULL"),
        ("outcome", "TEXT NOT NULL"),
        ("created_at", "TEXT NOT NULL"),
        ("payload", "TEXT NOT NULL"),
    ),
    "move_journal": (
        ("record_id", "TEXT PRIMARY KEY"),
        ("entry_id", "TEXT NOT NULL"),
        ("entry_kind", "TEXT NOT NULL"),
        ("reverses_entry_id", "TEXT"),
        ("plan_id", "TEXT NOT NULL"),
        ("plan_version", "TEXT NOT NULL"),
        ("file_id", "TEXT NOT NULL"),
        ("original_source_path", "TEXT NOT NULL"),
        ("destination_path", "TEXT NOT NULL"),
        ("content_hash", "TEXT NOT NULL"),
        ("time_of_execution", "TEXT NOT NULL"),
        ("payload", "TEXT NOT NULL"),
    ),
    "undo_retention": (
        ("record_id", "TEXT PRIMARY KEY"),
        ("retention_choice", "TEXT NOT NULL"),
        ("set_at", "TEXT NOT NULL"),
        ("set_by", "TEXT"),
        ("payload", "TEXT NOT NULL"),
    ),
}

P12_TABLES: tuple[str, ...] = tuple(_COLUMNS)

_SUPERSEDE = ", ".join(f"{name} TEXT" for name in SUPERSEDE_COLUMNS)

_INDEXES = """
CREATE UNIQUE INDEX IF NOT EXISTS one_current_move_plan
    ON move_plans (plan_id) WHERE superseded_by IS NULL;
CREATE INDEX IF NOT EXISTS move_plans_by_file ON move_plans (file_id, plan_version);
CREATE INDEX IF NOT EXISTS move_plans_by_group ON move_plans (group_plan_ref);

CREATE UNIQUE INDEX IF NOT EXISTS one_current_path_resolution
    ON path_resolutions (resolution_id) WHERE superseded_by IS NULL;
CREATE INDEX IF NOT EXISTS path_resolutions_by_node
    ON path_resolutions (plan_version, node_id);

CREATE INDEX IF NOT EXISTS execution_records_by_plan ON execution_records (plan_id);
CREATE INDEX IF NOT EXISTS collision_resolutions_by_plan
    ON collision_resolutions (plan_id);

CREATE UNIQUE INDEX IF NOT EXISTS one_journal_row_per_entry
    ON move_journal (entry_id);
CREATE INDEX IF NOT EXISTS move_journal_by_plan ON move_journal (plan_id);
CREATE INDEX IF NOT EXISTS move_journal_by_file ON move_journal (file_id);
CREATE INDEX IF NOT EXISTS move_journal_reversals
    ON move_journal (reverses_entry_id);

CREATE UNIQUE INDEX IF NOT EXISTS one_current_undo_retention
    ON undo_retention (retention_choice IS NOT NULL) WHERE superseded_by IS NULL;
"""


def _create_table(table: str) -> str:
    body = ",\n    ".join(f"{name:<26} {kind}" for name, kind in _COLUMNS[table])
    return f"CREATE TABLE IF NOT EXISTS {table} (\n    {body},\n    {_SUPERSEDE}\n);"


MUTATION_DDL = "\n".join(_create_table(table) for table in P12_TABLES) + _INDEXES

# §8.2 in SQL, in P11's idiom. `BEFORE UPDATE OF` names every column that is NOT a
# supersede link, so `mark_superseded` -- which writes exactly the three P1
# publishes -- passes, while a writer correcting a payload, a result or a path in
# place fails rather than losing the original. A blanket `BEFORE UPDATE` would make
# supersession impossible; a trigger on `payload` alone would leave `result`
# rewritable, and `result` is the field a caller would most want to "fix".
_GUARDS = "\n".join(
    f"""
CREATE TRIGGER IF NOT EXISTS {table}_no_delete
BEFORE DELETE ON {table}
BEGIN SELECT RAISE(ABORT, '{table} is append-only (§8.2)'); END;

CREATE TRIGGER IF NOT EXISTS {table}_never_overwritten
BEFORE UPDATE OF {", ".join(name for name, _ in _COLUMNS[table])} ON {table}
BEGIN SELECT RAISE(ABORT, '{table} rewrites nothing but its supersede link'); END;
"""
    for table in P12_TABLES
)


def create_mutation_schema(conn: sqlite3.Connection) -> None:
    """Create P12's tables. Idempotent; safe on an existing database."""
    conn.executescript(MUTATION_DDL)
    conn.executescript(_GUARDS)
