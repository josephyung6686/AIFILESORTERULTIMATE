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


def create_questions_schema(conn: sqlite3.Connection) -> None:
    """Create P15's tables if they are absent. Safe to call on every run."""
    conn.executescript(QUESTIONS_DDL)
