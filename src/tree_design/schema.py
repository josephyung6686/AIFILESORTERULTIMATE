# src/tree_design/schema.py
"""P10's own SQLite tables, inside P1's single database. Idempotent and additive.

`plan_version_id` appears on tree state and on branch bindings, and NOWHERE on
the shared template library. A fragment, a definition and an applicability row
are release-keyed records shared across plans; copying them per version would
make a library update look like a tree edit and would let two versions of one
recipe drift apart silently.

No column here holds a composed filesystem path. `nodes.existing_path` is the one
observed path, and it is an observation about the corpus, not a destination.
"""
from __future__ import annotations

import sqlite3

#: Every table P10 owns. The first four are tree state; the rest arrive with the
#: tasks that need them and are listed here so one module names the whole set.
P10_TABLES: tuple[str, ...] = (
    "plan_versions",
    "tree_nodes",
    "shared_material_policies",
    "node_expected_values",
    "frozen_trees",
)

TREE_DDL = """
CREATE TABLE IF NOT EXISTS plan_versions (
    plan_version_id     TEXT PRIMARY KEY,
    predecessor_id      TEXT REFERENCES plan_versions (plan_version_id),
    state               TEXT NOT NULL CHECK (state IN ('draft','frozen','superseded')),
    created_at          TEXT NOT NULL,
    -- §1.1, recorded by P3 as `cross_folder_moves`, stored here under §8.8's
    -- "Placement policy settings", enforced by P12 at mutation time.
    cross_folder_moves  INTEGER NOT NULL CHECK (cross_folder_moves IN (0, 1)),
    selection_id        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tree_nodes (
    node_id                      TEXT NOT NULL,
    plan_version_id              TEXT NOT NULL
                                 REFERENCES plan_versions (plan_version_id),
    -- Minted per version; `origin_node_id` carries the lineage. SPEC open
    -- question 5 decides whether these ever become the same value.
    origin_node_id               TEXT NOT NULL,
    node_type                    TEXT NOT NULL,
    display_label                TEXT NOT NULL,
    parent_node_id               TEXT,
    root_anchor                  TEXT NOT NULL,
    ordinal                      INTEGER NOT NULL,
    associated_group_ids         TEXT NOT NULL,   -- canonical JSON
    explanation                  TEXT NOT NULL,
    node_role                    TEXT NOT NULL,
    accepts_placement            INTEGER NOT NULL CHECK (accepts_placement IN (0, 1)),
    protected_movement_permitted INTEGER NOT NULL DEFAULT 0,
    handling_class               TEXT NOT NULL,
    template_context             TEXT,            -- canonical JSON or NULL
    dimension_role               TEXT,
    dimension                    TEXT,
    existing_path                TEXT,            -- only when node_type='existing'
    disposition                  TEXT,            -- only when node_role='residual'
    refinement_disposition       TEXT,
    refinement_reason            TEXT,
    PRIMARY KEY (plan_version_id, node_id),
    CHECK (existing_path IS NULL OR node_type = 'existing'),
    CHECK ((disposition IS NULL) = (node_role <> 'residual')),
    CHECK ((refinement_disposition IS NULL) = (refinement_reason IS NULL)),
    CHECK ((dimension_role IS NULL) = (dimension IS NULL))
);

CREATE INDEX IF NOT EXISTS tree_nodes_parent
    ON tree_nodes (plan_version_id, parent_node_id, ordinal);

CREATE INDEX IF NOT EXISTS tree_nodes_legal
    ON tree_nodes (plan_version_id, accepts_placement);

CREATE INDEX IF NOT EXISTS tree_nodes_lineage
    ON tree_nodes (origin_node_id);

CREATE TABLE IF NOT EXISTS node_expected_values (
    plan_version_id TEXT NOT NULL,
    node_id         TEXT NOT NULL,
    field_key       TEXT NOT NULL,
    value           TEXT NOT NULL,
    PRIMARY KEY (plan_version_id, node_id, field_key, value),
    FOREIGN KEY (plan_version_id, node_id)
        REFERENCES tree_nodes (plan_version_id, node_id)
);

CREATE TABLE IF NOT EXISTS shared_material_policies (
    policy_id       TEXT PRIMARY KEY,
    plan_version_id TEXT NOT NULL REFERENCES plan_versions (plan_version_id),
    policy          TEXT NOT NULL,
    -- NULL means tree-global. SPEC open question 9 is open; the column answers
    -- it per record instead of forcing one reading into the schema.
    policy_scope    TEXT,
    reason          TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS one_global_shared_material_policy
    ON shared_material_policies (plan_version_id)
    WHERE policy_scope IS NULL;

-- Task 16's. The hand-over bundle P11 reads back through
-- `tree_design.freeze.frozen_tree`. It exists because §8.8 makes a frozen
-- version immutable and P11's DM3 promise is that legality is decidable
-- "without consulting facts, templates or the filesystem": rebuilding the §6.1
-- profiles at read time would consult all three, and would consult them against
-- a P9/P4/P6 state that has moved on since freeze. Freeze writes the bundle
-- once; every later reader gets the version that was actually adopted.
CREATE TABLE IF NOT EXISTS frozen_trees (
    plan_version_id TEXT PRIMARY KEY REFERENCES plan_versions (plan_version_id),
    created_at      TEXT NOT NULL,
    freeze_record   TEXT NOT NULL,   -- canonical JSON
    profiles        TEXT NOT NULL    -- canonical JSON, one object per node
);
"""


def create_tree_schema(conn: sqlite3.Connection) -> None:
    """Create every P10-owned table. Idempotent; touches no P1 table."""
    conn.executescript(TREE_DDL)
