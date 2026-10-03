"""Item tables. Additive, and not part of P1's `FILES_DDL`.

`user_version` stays P1's. This package records its own version in `items_meta`
so an old database gains the tables without a P1 version bump.
"""
from __future__ import annotations

import sqlite3

ITEMS_SCHEMA_VERSION = 5

ITEMS_DDL = """
CREATE TABLE IF NOT EXISTS items_meta (
    version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS items (
    item_id            TEXT PRIMARY KEY,
    item_type          TEXT NOT NULL,
    display_label      TEXT NOT NULL,
    file_id            TEXT,
    open_target        TEXT,
    external_key       TEXT,
    presence           TEXT NOT NULL,
    typing_state       TEXT NOT NULL,
    type_schema        TEXT,
    profile_id         TEXT,
    created_at         TEXT NOT NULL,
    superseded_by      TEXT,
    content_hash       TEXT,
    size               INTEGER,
    mtime_ns           INTEGER,
    st_dev             INTEGER,
    st_ino             INTEGER,
    last_seen_at       TEXT,
    last_indexed_hash  TEXT,
    freshness_state    TEXT NOT NULL DEFAULT 'dirty'
);

CREATE TABLE IF NOT EXISTS item_versions (
    item_id        TEXT NOT NULL,
    file_id        TEXT NOT NULL,
    content_hash   TEXT NOT NULL,
    became_live_at TEXT NOT NULL,
    PRIMARY KEY (item_id, file_id)
);

CREATE INDEX IF NOT EXISTS items_by_type ON items(item_type);
CREATE INDEX IF NOT EXISTS items_by_file_id ON items(file_id);
CREATE INDEX IF NOT EXISTS items_by_external_key ON items(external_key);

CREATE TABLE IF NOT EXISTS item_headers (
    item_id            TEXT PRIMARY KEY,
    kind               TEXT NOT NULL,
    external_id        TEXT NOT NULL,
    thread_id          TEXT,
    account_label      TEXT,
    happened_at        TEXT,
    ended_at           TEXT,
    address_from       TEXT,
    address_to         TEXT,
    calendar_id        TEXT,
    status             TEXT,
    attachment_names   TEXT,
    attachment_hashes  TEXT
);

CREATE TABLE IF NOT EXISTS relationships (
    relationship_id TEXT PRIMARY KEY,
    rel_type        TEXT NOT NULL,
    from_item_id    TEXT NOT NULL,
    to_item_id      TEXT NOT NULL,
    confidence      TEXT NOT NULL,
    source          TEXT NOT NULL,
    state           TEXT NOT NULL,
    evidence_refs   TEXT NOT NULL,
    basis_key       TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    supersedes      TEXT,
    superseded_by   TEXT
);

CREATE INDEX IF NOT EXISTS relationships_from_type
    ON relationships(from_item_id, rel_type, state);
CREATE INDEX IF NOT EXISTS relationships_to_type
    ON relationships(to_item_id, rel_type, state);
CREATE INDEX IF NOT EXISTS relationships_by_basis
    ON relationships(basis_key);

-- Link decisions stay in this package. `CORRECTION_SCOPES` is a frozen
-- closed vocabulary in P1; adding `link` there is an owner edit. Until that
-- edit lands, polarity for a basis_key is recorded here and read exactly.
CREATE TABLE IF NOT EXISTS relationship_decisions (
    decision_id            TEXT PRIMARY KEY,
    basis_key              TEXT NOT NULL,
    polarity               TEXT NOT NULL,
    relationship_id        TEXT NOT NULL,
    user_id                TEXT NOT NULL,
    created_at             TEXT NOT NULL,
    evidence_ids           TEXT,
    item_content_versions  TEXT,
    session_id             TEXT,
    approval_hash          TEXT
);
CREATE INDEX IF NOT EXISTS relationship_decisions_by_basis
    ON relationship_decisions(basis_key, created_at);
CREATE INDEX IF NOT EXISTS relationship_decisions_by_rel
    ON relationship_decisions(relationship_id, created_at);

-- Append-only identity / freshness transitions for diagnosing stale search.
CREATE TABLE IF NOT EXISTS item_identity_events (
    event_id      TEXT PRIMARY KEY,
    item_id       TEXT NOT NULL,
    from_state    TEXT,
    to_state      TEXT NOT NULL,
    reason        TEXT NOT NULL,
    path          TEXT,
    content_hash  TEXT,
    st_dev        INTEGER,
    st_ino        INTEGER,
    details       TEXT,
    observed_at   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS item_identity_events_by_item
    ON item_identity_events(item_id, observed_at);
CREATE TRIGGER IF NOT EXISTS item_identity_events_no_update
BEFORE UPDATE ON item_identity_events
BEGIN SELECT RAISE(ABORT, 'item_identity_events is append-only'); END;
CREATE TRIGGER IF NOT EXISTS item_identity_events_no_delete
BEFORE DELETE ON item_identity_events
BEGIN SELECT RAISE(ABORT, 'item_identity_events is append-only'); END;
"""

#: Columns added after the first items release. `CREATE TABLE IF NOT EXISTS` is a
#: no-op on an existing table, so these ALTER paths reach migrated databases.
ITEMS_ADDED_COLUMNS: tuple[tuple[str, str], ...] = (
    ("content_hash", "TEXT"),
    ("size", "INTEGER"),
    ("mtime_ns", "INTEGER"),
    ("st_dev", "INTEGER"),
    ("st_ino", "INTEGER"),
    ("last_seen_at", "TEXT"),
    ("last_indexed_hash", "TEXT"),
    ("freshness_state", "TEXT NOT NULL DEFAULT 'dirty'"),
)

DECISION_ADDED_COLUMNS: tuple[tuple[str, str], ...] = (
    ("evidence_ids", "TEXT"),
    ("item_content_versions", "TEXT"),
    ("session_id", "TEXT"),
    ("approval_hash", "TEXT"),
)


def _migrate_items_columns(conn: sqlite3.Connection) -> None:
    present = {row[1] for row in conn.execute("PRAGMA table_info(items)")}
    if not present:
        return
    for column, column_type in ITEMS_ADDED_COLUMNS:
        if column not in present:
            conn.execute(
                f"ALTER TABLE items ADD COLUMN {column} {column_type}"
            )


def _migrate_decision_columns(conn: sqlite3.Connection) -> None:
    present = {
        row[1] for row in conn.execute("PRAGMA table_info(relationship_decisions)")
    }
    if not present:
        return
    for column, column_type in DECISION_ADDED_COLUMNS:
        if column not in present:
            conn.execute(
                f"ALTER TABLE relationship_decisions "
                f"ADD COLUMN {column} {column_type}"
            )


def create_items_schema(conn: sqlite3.Connection) -> None:
    """Create the item tables if they are absent. Safe to call on every run."""
    conn.executescript(ITEMS_DDL)
    _migrate_items_columns(conn)
    _migrate_decision_columns(conn)
    # Indexes/triggers that depend on migrated columns or tables added after v3.
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS item_identity_events (
            event_id      TEXT PRIMARY KEY,
            item_id       TEXT NOT NULL,
            from_state    TEXT,
            to_state      TEXT NOT NULL,
            reason        TEXT NOT NULL,
            path          TEXT,
            content_hash  TEXT,
            st_dev        INTEGER,
            st_ino        INTEGER,
            details       TEXT,
            observed_at   TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS item_identity_events_by_item
            ON item_identity_events(item_id, observed_at);
        CREATE INDEX IF NOT EXISTS items_by_freshness ON items(freshness_state);
        CREATE INDEX IF NOT EXISTS relationship_decisions_by_rel
            ON relationship_decisions(relationship_id, created_at);
        CREATE TRIGGER IF NOT EXISTS item_identity_events_no_update
        BEFORE UPDATE ON item_identity_events
        BEGIN SELECT RAISE(ABORT, 'item_identity_events is append-only'); END;
        CREATE TRIGGER IF NOT EXISTS item_identity_events_no_delete
        BEFORE DELETE ON item_identity_events
        BEGIN SELECT RAISE(ABORT, 'item_identity_events is append-only'); END;
        CREATE TRIGGER IF NOT EXISTS relationship_decisions_no_update
        BEFORE UPDATE ON relationship_decisions
        BEGIN SELECT RAISE(ABORT, 'relationship_decisions is append-only'); END;
        CREATE TRIGGER IF NOT EXISTS relationship_decisions_no_delete
        BEFORE DELETE ON relationship_decisions
        BEGIN SELECT RAISE(ABORT, 'relationship_decisions is append-only'); END;
        """
    )
    existing = conn.execute("SELECT version FROM items_meta").fetchone()
    if existing is None:
        conn.execute(
            "INSERT INTO items_meta (version) VALUES (?)",
            (ITEMS_SCHEMA_VERSION,),
        )
    elif existing[0] < ITEMS_SCHEMA_VERSION:
        conn.execute(
            "UPDATE items_meta SET version = ?",
            (ITEMS_SCHEMA_VERSION,),
        )
