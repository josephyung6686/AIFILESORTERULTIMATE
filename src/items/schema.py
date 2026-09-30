"""Item tables. Additive, and not part of P1's `FILES_DDL`.

`user_version` stays P1's. This package records its own version in `items_meta`
so an old database gains the tables without a P1 version bump.
"""
from __future__ import annotations

import sqlite3

ITEMS_SCHEMA_VERSION = 1

ITEMS_DDL = """
CREATE TABLE IF NOT EXISTS items_meta (
    version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS items (
    item_id        TEXT PRIMARY KEY,
    item_type      TEXT NOT NULL,
    display_label  TEXT NOT NULL,
    file_id        TEXT,
    open_target    TEXT,
    external_key   TEXT,
    presence       TEXT NOT NULL,
    typing_state   TEXT NOT NULL,
    type_schema    TEXT,
    profile_id     TEXT,
    created_at     TEXT NOT NULL,
    superseded_by  TEXT
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
"""


def create_items_schema(conn: sqlite3.Connection) -> None:
    """Create the item tables if they are absent. Safe to call on every run."""
    conn.executescript(ITEMS_DDL)
    existing = conn.execute("SELECT version FROM items_meta").fetchone()
    if existing is None:
        conn.execute(
            "INSERT INTO items_meta (version) VALUES (?)",
            (ITEMS_SCHEMA_VERSION,),
        )
