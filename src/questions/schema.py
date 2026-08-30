# src/questions/schema.py
"""P15's own SQLite tables, inside P1's single database. Idempotent and additive.

**Why a table and not only the event log.** `src/privacy/consent.py` keeps §8.4's
consent question in the log alone, and says why: its Done-means is "the audit log
holds a `consent_requested` event and no `model_release` for that request until a
choice is recorded", so the log IS the state. P15's contract is different. `66`
§13 requires that a person "should be able to INSPECT a structural answer and see:
what it controls, where it applies, when it was supplied, whether it was inferred
or explicitly confirmed, and how to change it." That is a query, over an answer
that outlives the run that asked for it, and reconstructing it by folding the
whole event log is how two readers come to disagree about what the person said.

**Answers are append-only.** §12 requires an answer to be "edited, revoked, or
re-run"; an edit that overwrote the row would lose that the person once said
something else, and a revocation that deleted it would lose that they ever
answered. So the key includes the recording time, superseding is a new row, and
`answers_now` reads the live one -- the same supersession discipline P1 applies to
content versions and P9 to groups.
"""
from __future__ import annotations

import sqlite3

#: Every table P15 owns.
P15_TABLES: tuple[str, ...] = (
    "structural_questions",
    "structural_answers",
)

QUESTIONS_DDL = """
-- One question the product actually raised, with the evidence that raised it.
-- Recorded even when nobody answers, because "we asked and were declined" and "we
-- never asked" are different states and §14 makes the first one first-class.
CREATE TABLE IF NOT EXISTS structural_questions (
    question_id       TEXT PRIMARY KEY,
    answer_class      TEXT NOT NULL
                      CHECK (answer_class IN ('structural','contextual')),
    prompt            TEXT NOT NULL,
    -- §14: the person "can see why the question arose".
    evidence_context  TEXT NOT NULL,
    -- §12: "explain the exact decision it unlocks".
    unlocks           TEXT NOT NULL,
    -- §12: "state what it will not affect".
    will_not_do       TEXT NOT NULL,
    scope             TEXT NOT NULL,
    -- §21's "data classifications", for the data the QUESTION holds. One of P7's
    -- five §8.4 classes, minus `unreadable_unclassified`, which is a gate outcome
    -- and never a statement about what a question collects.
    handling_class    TEXT NOT NULL
                      CHECK (handling_class IN ('public_low',
                                                'personal_non_sensitive',
                                                'sensitive_personal',
                                    'highly_sensitive_credential_bearing')),
    -- The options, as canonical JSON. A second table would let a question exist
    -- with no options, which `StructuralQuestion` already refuses to construct.
    options           TEXT NOT NULL,
    -- P4 observation keys, as canonical JSON.
    evidence_refs     TEXT NOT NULL,
    first_asked_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS structural_answers (
    answer_id        TEXT PRIMARY KEY,
    question_id      TEXT NOT NULL REFERENCES structural_questions (question_id),
    -- NULL for `skipped` and `not_applicable`: skipping is not choosing.
    option_id        TEXT,
    state            TEXT NOT NULL
                     CHECK (state IN ('confirmed','skipped','not_applicable',
                                      'revoked')),
    -- §21's "allowed answer types". `choice` is every row written before
    -- 2026-08-30; `free_text` selects no option and therefore reaches no
    -- consequence, which is §16's "an unmatched answer must remain unmatched".
    answer_type      TEXT NOT NULL DEFAULT 'choice'
                     CHECK (answer_type IN ('choice','free_text')),
    -- §16:555: "store the raw user wording". NULL on every `choice` row.
    raw_wording      TEXT,
    -- §16:543: a role has "a scope and possibly a time period".
    applies_from     TEXT,
    applies_until    TEXT,
    -- §13: an answer must not be "reused outside its stated scope".
    scope            TEXT NOT NULL,
    user_id          TEXT NOT NULL,
    recorded_at      TEXT NOT NULL,
    -- §13: the person can see "whether it was inferred or explicitly confirmed".
    -- §12 forbids a structural answer being inferred at all, so this is 0 on
    -- every row P15 will write; the column exists so the record can SAY so.
    inferred         INTEGER NOT NULL CHECK (inferred IN (0, 1)),
    supersedes       TEXT REFERENCES structural_answers (answer_id),
    supersede_reason TEXT
);

-- The live answer for one question and scope is the one nothing supersedes.
CREATE INDEX IF NOT EXISTS structural_answers_live
    ON structural_answers (question_id, scope, recorded_at);
"""


#: (column, type) pairs added to `structural_questions` after its first release.
#: `CREATE TABLE IF NOT EXISTS` is a no-op on a database that already has the table,
#: so a column added to QUESTIONS_DDL never reaches an existing database. This is the
#: same mechanism `database_agent.db` uses on `files`, for the same reason.
#:
#: The added column is nullable where the fresh DDL says NOT NULL, and that asymmetry
#: is deliberate: SQLite requires a non-null DEFAULT on an added NOT NULL column, and
#: there is no default handling class to give. Absence must refuse rather than guess,
#: so a row written before this column existed rehydrates through
#: `StructuralQuestion`, which refuses an empty `handling_class` by name. An old
#: question becomes visibly unreadable instead of silently reclassified.
QUESTIONS_ADDED_COLUMNS: tuple[tuple[str, str], ...] = (
    ("handling_class", "TEXT"),
)

#: The same, for `structural_answers`. `answer_type` carries a DEFAULT where
#: `handling_class` deliberately does not, and the difference is the whole reason
#: one is safe and the other is not: every answer written before this column existed
#: IS a choice, so the default states a fact rather than guessing one.
ANSWERS_ADDED_COLUMNS: tuple[tuple[str, str], ...] = (
    ("answer_type", "TEXT NOT NULL DEFAULT 'choice'"),
    ("raw_wording", "TEXT"),
    ("applies_from", "TEXT"),
    ("applies_until", "TEXT"),
)


def _migrate(conn: sqlite3.Connection, table: str,
             columns: tuple[tuple[str, str], ...]) -> None:
    present = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
    if not present:
        return
    for column, column_type in columns:
        if column not in present:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")


def create_questions_schema(conn: sqlite3.Connection) -> None:
    """Create P15's tables if they are absent. Safe to call on every run."""
    _migrate(conn, "structural_questions", QUESTIONS_ADDED_COLUMNS)
    _migrate(conn, "structural_answers", ANSWERS_ADDED_COLUMNS)
    conn.executescript(QUESTIONS_DDL)
