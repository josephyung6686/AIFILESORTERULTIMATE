# src/evidence_shape/schema.py
"""P4's three tables. They live inside P1's single local SQLite database (§0: "Each
part owns its own tables within it"); P1 owns the handle, the transaction boundary,
`files` and `events`, and P4 creates none of them and modifies no P1 file.

One column is not a published field. P1's `mark_superseded` and `chain` are
`... WHERE record_id = ?`, and P4's published primary key is `observation_id`.
`record_id` is a VIRTUAL generated projection of it: it stores nothing, cannot
diverge, does not appear in `PRAGMA table_info`, and lets P1's tested supersede
functions be reused verbatim instead of written a second time under a second name.

The foreign keys run one way. Nothing references P1's `files`, and since 2026-08-20
that is a CONSEQUENCE of an answer rather than the absence of one: Open question 2 --
whether an observation is owned by the content hash or by the file record -- is
closed, and the content hash owns it. A foreign key to `files` would say the file
record owns it, which is now the wrong answer, not merely a premature one. `file_id`
stays on the row as the convenience handle §8.2's explanations render; identity is
`content_hash` (P1 R1).

Kept from the open-question era, and still true: P4 must be buildable and testable
with no `files` row in existence, which is what lets P6 be built entirely against
P4's fixtures with no extractor and no scan.
"""
from __future__ import annotations

import sqlite3

#: The one column that is not a published observation field. See the module docstring.
SUPERSEDE_ADAPTER_COLUMN = "record_id"

EXTRACTION_RUNS_DDL = """
CREATE TABLE IF NOT EXISTS extraction_runs (
    run_id             TEXT PRIMARY KEY,
    file_id            TEXT NOT NULL,
    content_hash       TEXT NOT NULL,
    extractor_name     TEXT NOT NULL,
    extractor_version  TEXT NOT NULL,
    source_type        TEXT NOT NULL,
    analysis_tier      TEXT NOT NULL,
    config             TEXT NOT NULL,
    config_fingerprint TEXT NOT NULL,
    completeness       TEXT NOT NULL,
    coverage           TEXT,
    observation_count  INTEGER NOT NULL DEFAULT 0,
    started_at         TEXT NOT NULL,
    finished_at        TEXT,
    failure_reason     TEXT
);
-- §3.4: "the content hash and the exact process that produced it". Not unique: a
-- re-run at the same key is legal and supersedes rather than replaces (§8.2).
CREATE INDEX IF NOT EXISTS extraction_runs_cache_key
    ON extraction_runs (content_hash, extractor_name, extractor_version,
                        config_fingerprint);
CREATE INDEX IF NOT EXISTS extraction_runs_file ON extraction_runs (file_id);
CREATE TRIGGER IF NOT EXISTS extraction_runs_no_delete
BEFORE DELETE ON extraction_runs
BEGIN SELECT RAISE(ABORT, 'a run is superseded by a later run, never removed (§8.2)'); END;
"""

EVIDENCE_DDL = """
CREATE TABLE IF NOT EXISTS evidence (
    observation_id     TEXT PRIMARY KEY,
    record_id          TEXT GENERATED ALWAYS AS (observation_id) VIRTUAL,
    observation_key    TEXT NOT NULL,
    file_id            TEXT NOT NULL,
    content_hash       TEXT NOT NULL,
    extractor_name     TEXT NOT NULL,
    extractor_version  TEXT NOT NULL,
    source_type        TEXT NOT NULL,
    raw_value          TEXT NOT NULL,
    normalized_value   TEXT,
    location           TEXT NOT NULL,
    context_before     TEXT,
    context_after      TEXT,
    context_truncated  INTEGER NOT NULL,
    occurrence_count   INTEGER NOT NULL,
    observed_at        TEXT NOT NULL,
    reliability        TEXT NOT NULL,
    run_id             TEXT NOT NULL REFERENCES extraction_runs (run_id),
    confidence         REAL,
    signal_tier        INTEGER,
    supersedes         TEXT,
    superseded_by      TEXT,
    supersede_reason   TEXT
);
-- Deliberately NOT unique (MINOR 8): two extractor versions carry one key, which is
-- the mechanism §8.5's cross-version diff runs on.
CREATE INDEX IF NOT EXISTS evidence_key ON evidence (observation_key);
CREATE INDEX IF NOT EXISTS evidence_run ON evidence (run_id);
CREATE INDEX IF NOT EXISTS evidence_file ON evidence (file_id);
CREATE INDEX IF NOT EXISTS evidence_content ON evidence (content_hash);
CREATE TRIGGER IF NOT EXISTS evidence_no_delete
BEFORE DELETE ON evidence
-- RAISE takes one string literal, so the reason is short here and long above:
-- §8.7 requires a rejected proposal to keep the evidence that produced it.
BEGIN SELECT RAISE(ABORT, 'observations are superseded, never removed (§8.2, §8.7)'); END;
-- RAW-2, over exactly the SPEC's seven never-overwritten fields. The three supersede
-- columns are outside it: supersession is the one legal write to an existing row.
CREATE TRIGGER IF NOT EXISTS evidence_never_overwritten
BEFORE UPDATE OF raw_value, location, occurrence_count, observed_at, extractor_name,
                 extractor_version, run_id ON evidence
BEGIN SELECT RAISE(ABORT, 'RAW-2: never updated; a better extractor emits a new observation and a new run (§8.2)'); END;
"""

TEXT_UNITS_DDL = """
CREATE TABLE IF NOT EXISTS text_units (
    run_id         TEXT NOT NULL REFERENCES extraction_runs (run_id),
    container_path TEXT NOT NULL,
    unit_locator   TEXT NOT NULL,
    text           TEXT NOT NULL,
    length         INTEGER NOT NULL,
    truncated      INTEGER NOT NULL,
    -- Keyed by (run_id, container_path), in the canonical string form of that path.
    PRIMARY KEY (run_id, unit_locator)
);
CREATE TRIGGER IF NOT EXISTS text_units_no_delete
BEFORE DELETE ON text_units
BEGIN SELECT RAISE(ABORT, 'a text unit is superseded by a later run, never removed (rule 7, §8.2)'); END;
CREATE TRIGGER IF NOT EXISTS text_units_no_rewrite
BEFORE UPDATE ON text_units
BEGIN SELECT RAISE(ABORT, 'superseding a run never rewrites an earlier run''s units (rule 4, §8.2)'); END;
"""


def create_evidence_schema(conn: sqlite3.Connection) -> None:
    """Create every P4-owned table. Idempotent. P1's `create_schema` runs first."""
    conn.executescript(EXTRACTION_RUNS_DDL)
    conn.executescript(EVIDENCE_DDL)
    conn.executescript(TEXT_UNITS_DDL)
