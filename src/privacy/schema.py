# src/privacy/schema.py
"""P7's tables. They live inside the one local SQLite database the design names --
§0: "A local SQLite database acts as the durable working memory of the product."

One table per part is this project's CONVENTION, not a design quotation. P4's schema
module records what happened the last time that convention acquired quote marks: a
sentence nobody wrote was cited in three PLANs and one module. It is written plainly
here instead.

P1 owns the handle, the transaction boundary, `files` and `events`. P7 creates none
of them and modifies no P1 file. `create_privacy_schema` is the one entry point;
Task 5 adds `privacy_policies` to it.

One column is not a published field. P1's `mark_superseded` and `chain` are
`... WHERE record_id = ?`, and P7's published primary key is `fact_id`. `record_id`
is a VIRTUAL generated projection of it: it stores nothing, cannot diverge, does not
appear in `PRAGMA table_info`, and lets P1's tested supersede functions be reused
verbatim instead of written a second time under a second name. P4 solved this once
(`evidence.record_id`) and P7 copies the solution, not the implementation.

The table is keyed on `(file_id, content_hash)` and the index says so. D2: a
classification is about BYTES. New bytes at a path are a new file version and
inherit nothing, which is what lets "nobody has looked at these bytes" stay
distinguishable from "these bytes were found to carry nothing".
"""
from __future__ import annotations

import sqlite3

#: P7's classification table. Named here so no caller retypes the string.
CLASSIFICATIONS_TABLE = "classifications"

#: The one column that is not a published classification field. See the docstring.
SUPERSEDE_ADAPTER_COLUMN = "record_id"

CLASSIFICATIONS_DDL = f"""
CREATE TABLE IF NOT EXISTS {CLASSIFICATIONS_TABLE} (
    fact_id           TEXT PRIMARY KEY,
    {SUPERSEDE_ADAPTER_COLUMN} TEXT GENERATED ALWAYS AS (fact_id) VIRTUAL,
    file_id           TEXT NOT NULL,
    content_hash      TEXT NOT NULL,
    handling_class    TEXT NOT NULL,
    protected         INTEGER NOT NULL,
    basis             TEXT NOT NULL,
    evidence_refs     TEXT NOT NULL,
    reliability_state TEXT NOT NULL,
    observed_at       TEXT NOT NULL,
    supersedes        TEXT,
    superseded_by     TEXT,
    supersede_reason  TEXT
);
-- Deliberately NOT unique: an early detector and a later one may disagree and both
-- survive (§8.2's OCR example). The resolver is `ClassificationStore.current`.
CREATE INDEX IF NOT EXISTS classifications_version
    ON {CLASSIFICATIONS_TABLE} (file_id, content_hash);
CREATE INDEX IF NOT EXISTS classifications_file
    ON {CLASSIFICATIONS_TABLE} (file_id);
CREATE TRIGGER IF NOT EXISTS classifications_no_delete
BEFORE DELETE ON {CLASSIFICATIONS_TABLE}
BEGIN SELECT RAISE(ABORT, 'a classification is superseded, never removed (§8.2, §8.7)'); END;
-- Over the eight SPEC §2 fields. The three supersede columns are outside it:
-- supersession is the one legal write to an existing row.
CREATE TRIGGER IF NOT EXISTS classifications_never_overwritten
BEFORE UPDATE OF fact_id, file_id, content_hash, handling_class, protected, basis,
                 evidence_refs, reliability_state, observed_at
    ON {CLASSIFICATIONS_TABLE}
BEGIN SELECT RAISE(ABORT, 'a classification is superseded, never overwritten (§8.2)'); END;
"""


#: P7's policy table. One row per policy VERSION; a change supersedes, never mutates.
POLICIES_TABLE = "privacy_policies"

POLICIES_DDL = f"""
CREATE TABLE IF NOT EXISTS {POLICIES_TABLE} (
    policy_version             TEXT PRIMARY KEY,
    {SUPERSEDE_ADAPTER_COLUMN} TEXT GENERATED ALWAYS AS (policy_version) VIRTUAL,
    plan_version               TEXT NOT NULL,
    operation_mode             TEXT NOT NULL,
    consent_grants             TEXT NOT NULL,
    redaction_settings         TEXT NOT NULL,
    automatic_move_permissions TEXT NOT NULL,
    set_at                     TEXT NOT NULL,
    supersedes                 TEXT,
    superseded_by              TEXT,
    supersede_reason           TEXT
);
CREATE INDEX IF NOT EXISTS privacy_policies_plan
    ON {POLICIES_TABLE} (plan_version);
CREATE TRIGGER IF NOT EXISTS privacy_policies_no_delete
BEFORE DELETE ON {POLICIES_TABLE}
BEGIN SELECT RAISE(ABORT, 'a policy is superseded, never removed (§8.2, §8.5 replay)'); END;
-- §8.8's diff needs both sides. The three supersede columns stay writable.
CREATE TRIGGER IF NOT EXISTS privacy_policies_never_overwritten
BEFORE UPDATE OF policy_version, plan_version, operation_mode, consent_grants,
                 redaction_settings, automatic_move_permissions, set_at
    ON {POLICIES_TABLE}
BEGIN SELECT RAISE(ABORT, 'a policy is superseded, never overwritten (§8.2, §8.8)'); END;
"""


def create_privacy_schema(conn: sqlite3.Connection) -> None:
    """Create every P7-owned table. Idempotent. P1's `create_schema` runs first."""
    from privacy.binding import RELEASE_LEDGER_DDL

    conn.executescript(CLASSIFICATIONS_DDL)
    conn.executescript(POLICIES_DDL)
    # Task 12's ledger is what makes `Released` single-use (SPEC §6).
    conn.executescript(RELEASE_LEDGER_DDL)
