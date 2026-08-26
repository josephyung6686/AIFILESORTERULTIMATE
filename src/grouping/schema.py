# src/grouping/schema.py
"""P9's own SQLite tables. Idempotent, additive, and separate from P1's.

`plan_version_id` appears on exactly one table. Groups, memberships, dossiers and
edges live in the shared evidence database and survive every plan version;
`group_acceptance` records the state a plan version has about them. Putting the
version on `groups` would force the group, its dossier, its model response and
every line of its evidence to be duplicated per version.

List and map fields are stored as canonical JSON so two equal records serialise
one way. `display_label` and `group_category` are SQL NULL unless coherence holds,
which is the same rule the record enforces at construction.

No column here names a destination, node, path, folder or tree. Those are P10's
and P11's, and a P9 column carrying one would be P9 deciding where a file goes.
"""
from __future__ import annotations

import sqlite3

#: Every table P9 owns. Only the last carries `plan_version_id`.
P9_TABLES: tuple[str, ...] = (
    "groups",
    "memberships",
    "group_dossiers",
    "group_edges",
    "stop_rule_outcomes",
    "group_failure_points",
    "group_acceptance",
)

_SUPERSEDE = "supersedes TEXT, superseded_by TEXT, supersede_reason TEXT"

GROUPING_DDL = f"""
CREATE TABLE IF NOT EXISTS groups (
    group_id               TEXT PRIMARY KEY,
    seed_ref               TEXT NOT NULL,
    seed_kind              TEXT NOT NULL,
    proposed_basis         TEXT NOT NULL,
    anchor_facts           TEXT NOT NULL,
    pre_model_signals      TEXT NOT NULL,
    anchor_count           INTEGER NOT NULL CHECK (anchor_count >= 0),
    coherence_verdict      TEXT,
    coherence_citations    TEXT NOT NULL,
    group_category         TEXT,
    display_label          TEXT,
    label_source           TEXT,
    conflicts              TEXT NOT NULL,
    stop_rule_hits         TEXT NOT NULL,
    state                  TEXT NOT NULL,
    sensitivity_state      TEXT NOT NULL,
    dossier_id             TEXT,
    llm_response_ref       TEXT,
    validation_verdict_ref TEXT,
    created_by             TEXT NOT NULL,
    created_at             TEXT NOT NULL,
    {_SUPERSEDE},
    CHECK (
        (coherence_verdict = 'coherent')
        OR (display_label IS NULL AND group_category IS NULL)
    )
);
CREATE INDEX IF NOT EXISTS groups_state ON groups (state);
CREATE INDEX IF NOT EXISTS groups_current ON groups (group_id) WHERE superseded_by IS NULL;

CREATE TABLE IF NOT EXISTS memberships (
    membership_id          TEXT PRIMARY KEY,
    group_id               TEXT NOT NULL,
    file_id                TEXT NOT NULL,
    content_hash           TEXT NOT NULL,
    basis                  TEXT NOT NULL,
    decision               TEXT NOT NULL,
    decision_source        TEXT NOT NULL,
    support                TEXT NOT NULL,
    insufficient_evidence  INTEGER NOT NULL CHECK (insufficient_evidence IN (0, 1)),
    insufficiency_statement TEXT,
    conflicts              TEXT NOT NULL,
    outlier_flag           TEXT NOT NULL,
    validation_verdict_ref TEXT,
    created_at             TEXT NOT NULL,
    {_SUPERSEDE}
);
CREATE INDEX IF NOT EXISTS memberships_group ON memberships (group_id);
CREATE INDEX IF NOT EXISTS memberships_file ON memberships (file_id, content_hash);

CREATE TABLE IF NOT EXISTS group_dossiers (
    dossier_id             TEXT PRIMARY KEY,
    group_id               TEXT NOT NULL,
    proposed_basis         TEXT NOT NULL,
    payload                TEXT NOT NULL,
    dossier_fingerprint    TEXT NOT NULL,
    created_at             TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS group_dossiers_group ON group_dossiers (group_id);
CREATE INDEX IF NOT EXISTS group_dossiers_fingerprint
    ON group_dossiers (dossier_fingerprint);

CREATE TABLE IF NOT EXISTS group_edges (
    edge_id                TEXT PRIMARY KEY,
    from_file_id           TEXT NOT NULL,
    to_file_id             TEXT NOT NULL,
    edge_type              TEXT NOT NULL,
    evidence_ref           TEXT NOT NULL,
    weight                 REAL,
    bridge_entity_ref      TEXT,
    hub_suppressed         INTEGER NOT NULL CHECK (hub_suppressed IN (0, 1)),
    created_at             TEXT NOT NULL,
    {_SUPERSEDE},
    CHECK (from_file_id <> to_file_id)
);
CREATE INDEX IF NOT EXISTS group_edges_from ON group_edges (from_file_id);
CREATE INDEX IF NOT EXISTS group_edges_to ON group_edges (to_file_id);

CREATE TABLE IF NOT EXISTS stop_rule_outcomes (
    outcome_id             TEXT PRIMARY KEY,
    group_id               TEXT NOT NULL,
    rules_fired            TEXT NOT NULL,
    evidence_refs          TEXT NOT NULL,
    outcome                TEXT NOT NULL,
    created_at             TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS stop_rule_outcomes_group ON stop_rule_outcomes (group_id);

CREATE TABLE IF NOT EXISTS group_failure_points (
    failure_id             TEXT PRIMARY KEY,
    group_id               TEXT NOT NULL,
    dossier_id             TEXT,
    membership_id          TEXT,
    stage                  TEXT NOT NULL,
    cause_code             TEXT NOT NULL,
    evidence_ref           TEXT,
    detected_by            TEXT NOT NULL,
    created_at             TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS group_failure_points_stage
    ON group_failure_points (stage);
CREATE INDEX IF NOT EXISTS group_failure_points_group
    ON group_failure_points (group_id);

CREATE TABLE IF NOT EXISTS group_acceptance (
    acceptance_id          TEXT PRIMARY KEY,
    plan_version_id        TEXT NOT NULL,
    group_id               TEXT NOT NULL,
    membership_id          TEXT,
    acceptance             TEXT NOT NULL,
    review_state           TEXT NOT NULL,
    user_edited_label      TEXT,
    aliases                TEXT NOT NULL,
    review_decision_ref    TEXT,
    decided_by             TEXT NOT NULL,
    created_at             TEXT NOT NULL,
    {_SUPERSEDE}
);
CREATE INDEX IF NOT EXISTS group_acceptance_plan
    ON group_acceptance (plan_version_id, group_id);
CREATE UNIQUE INDEX IF NOT EXISTS one_current_group_acceptance
    ON group_acceptance (
        plan_version_id, group_id, COALESCE(membership_id, '')
    ) WHERE superseded_by IS NULL;
"""


def create_grouping_schema(conn: sqlite3.Connection) -> None:
    """Create P9's tables. Idempotent; safe to call on an existing database."""
    conn.executescript(GROUPING_DDL)
