"""P13's three tables, inside P1's single database.

§0: "A local SQLite database acts as the durable working memory of the product."
One table per part is this project's convention, written plainly rather than
cited.

P13 owns no supersedable record: it never edits a decision, plan, verdict, fact
or observation. So every table here refuses UPDATE and DELETE by TRIGGER, not by
convention, and there is no `superseded_by` column anywhere -- a supersede column
with no writer is the defect class this project has paid for most often.

NO COLUMN HOLDS A PATH. B3: P13 shows a node and its ancestor `display_label`
chain, and P12 alone composes paths. The undo-conflict item carries P12's paths
because §8.3's own sentence demands them; it is built and shown, never stored
here.
"""
from __future__ import annotations

import sqlite3

REVIEW_TABLES: tuple[str, ...] = (
    "review_actions", "review_approvals", "review_presentations")

_DDL = """
CREATE TABLE IF NOT EXISTS review_presentations (
    presented_state_ref TEXT PRIMARY KEY,
    event_id            INTEGER NOT NULL,
    surface             TEXT NOT NULL,
    subject_ref         TEXT NOT NULL,
    plan_version        TEXT NOT NULL,
    session_id          TEXT NOT NULL,
    redaction_policy    TEXT NOT NULL,
    evidence_refs       TEXT NOT NULL,
    user_id             TEXT,
    rendered_at         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS review_actions (
    action_id           TEXT PRIMARY KEY,
    surface             TEXT NOT NULL,
    subject_ref         TEXT NOT NULL,
    plan_version        TEXT NOT NULL,
    session_id          TEXT NOT NULL,
    action              TEXT NOT NULL,
    bulk_member_refs    TEXT NOT NULL,
    bulk_basis          TEXT,
    correction_scope    TEXT NOT NULL,
    routed_to           TEXT NOT NULL,
    presented_state_ref TEXT NOT NULL
        REFERENCES review_presentations (presented_state_ref),
    payload             TEXT NOT NULL,
    user_id             TEXT NOT NULL,
    acted_at            TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS review_approvals (
    approval_id            TEXT PRIMARY KEY,
    plan_id                TEXT NOT NULL,
    placement_decision_ref TEXT NOT NULL,
    plan_version           TEXT NOT NULL,
    required_review_policy TEXT NOT NULL,
    verdict                TEXT NOT NULL,
    presented_state_ref    TEXT NOT NULL
        REFERENCES review_presentations (presented_state_ref),
    user_id                TEXT NOT NULL,
    decided_at             TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS review_actions_by_subject
    ON review_actions (subject_ref, plan_version);
CREATE INDEX IF NOT EXISTS review_approvals_by_plan
    ON review_approvals (plan_id, plan_version);
CREATE INDEX IF NOT EXISTS review_presentations_by_subject
    ON review_presentations (subject_ref, surface);
"""

_APPEND_ONLY = """
CREATE TRIGGER IF NOT EXISTS {table}_no_update
BEFORE UPDATE ON {table}
BEGIN
    SELECT RAISE(ABORT, '{table} is append-only: P13 owns no supersedable record');
END;

CREATE TRIGGER IF NOT EXISTS {table}_no_delete
BEFORE DELETE ON {table}
BEGIN
    SELECT RAISE(ABORT, '{table} is append-only: P13 owns no supersedable record');
END;
"""


def create_review_schema(conn: sqlite3.Connection) -> None:
    """Create P13's three tables and their append-only triggers. Idempotent."""
    conn.executescript(_DDL)
    for table in REVIEW_TABLES:
        conn.executescript(_APPEND_ONLY.format(table=table))
    conn.commit()
