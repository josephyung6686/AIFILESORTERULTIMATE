"""Contract out §6 — one local SQLite database, transactional and inspectable (§0)."""
from __future__ import annotations

import sqlite3
import uuid
from collections.abc import Iterable
from contextlib import contextmanager
from pathlib import Path

SCHEMA_VERSION = 1


class DatabaseInsideCorpus(Exception):
    """11-ops-runtime.md §2 — the database is never created inside a scanned root."""


def default_database_path(bundle_id: str) -> Path:
    """11-ops-runtime.md §2 — Application Support / bundle identifier / agent.sqlite.

    The bundle identifier is NOT specified by `11` and is not invented here: the
    application that launches P1 supplies it. P1 composes the path and nothing else.
    """
    return Path.home() / "Library" / "Application Support" / bundle_id / "agent.sqlite"


def open_database(path: Path, *, scan_roots: Iterable[Path] = ()) -> sqlite3.Connection:
    """Open (creating if absent) the single local database (§0).

    `scan_roots` are the roots the caller has selected (P3 owns them, §1.1). The
    database may not live inside any of them (11-ops-runtime.md §2), so P3's
    exclusion rules never have to special-case it.
    """
    resolved = path.expanduser().resolve()
    for root in scan_roots:
        root = Path(root).expanduser().resolve()
        if resolved == root or root in resolved.parents:
            raise DatabaseInsideCorpus(
                f"{resolved} is inside the declared root {root}; the database is "
                "never created inside a scan root (11-ops-runtime.md §2)"
            )
    path = resolved
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    # R6 is "INSERT only ... no row rewrite". SQLite's REPLACE conflict resolution
    # deletes the conflicting row WITHOUT firing delete triggers unless recursive
    # triggers are on, so `INSERT OR REPLACE` would rewrite any event row in place
    # with no error — forging the one log §8.4's audit and §8.7's evidence read.
    conn.execute("PRAGMA recursive_triggers = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = FULL")
    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    # Contract out §6 publishes "one local SQLite database ... transactional and
    # inspectable" — a handle whose tables do not exist is not that. create_schema
    # stays public and idempotent for callers that want it explicitly, but no
    # neighbour has to remember a second call to get a usable database.
    create_schema(conn)
    conn.set_authorizer(_deny_events_history_loss)
    return conn


_PROTECTED_TRIGGERS = frozenset({
    "events_no_update", "events_no_delete", "events_no_replace",
})


def _deny_events_history_loss(action, arg1, arg2, dbname, source):
    """R6: DROP TABLE events and dropping the append-only triggers are truncation."""
    if action == sqlite3.SQLITE_DROP_TABLE and arg1 == "events":
        return sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_DROP_TRIGGER and arg1 in _PROTECTED_TRIGGERS:
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK


@contextmanager
def transaction(conn: sqlite3.Connection):
    """Explicit transaction boundary. Reentrant: nested callers use a SAVEPOINT
    so they cannot roll back an outer scope's work.
    """
    in_flight = conn.in_transaction
    name = f"p1_{uuid.uuid4().hex}"
    if in_flight:
        conn.execute(f"SAVEPOINT {name}")
        try:
            yield conn
        except Exception:
            conn.execute(f"ROLLBACK TO SAVEPOINT {name}")
            conn.execute(f"RELEASE SAVEPOINT {name}")
            raise
        conn.execute(f"RELEASE SAVEPOINT {name}")
        return
    conn.execute("BEGIN")
    try:
        yield conn
    except Exception:
        conn.execute("ROLLBACK")
        raise
    conn.execute("COMMIT")


FILES_DDL = """
CREATE TABLE IF NOT EXISTS files (
    file_id                   TEXT PRIMARY KEY,
    current_path              TEXT NOT NULL,
    filename                  TEXT NOT NULL,
    normalized_filename       TEXT NOT NULL,
    extension                 TEXT NOT NULL,
    directory_position        TEXT,
    volume_id                 TEXT,          -- nullable: P1 OQ9 is OPEN (Task 2)
    content_hash              TEXT NOT NULL,
    hash_algorithm            TEXT NOT NULL,
    observed_size             INTEGER NOT NULL,
    observed_timestamps       TEXT NOT NULL,
    mime_type                 TEXT,
    detected_format           TEXT,
    scan_state                TEXT NOT NULL,
    extraction_status_by_tier TEXT NOT NULL DEFAULT '{}',
    sensitivity_state         TEXT
);
CREATE INDEX IF NOT EXISTS files_content_hash ON files (content_hash);
"""


EVENTS_DDL = """
CREATE TABLE IF NOT EXISTS events (
    event_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type         TEXT NOT NULL,
    base_event_type    TEXT,
    file_id            TEXT,
    content_hash       TEXT,
    old_path           TEXT,
    new_path           TEXT,
    subsystem          TEXT NOT NULL,
    component_version  TEXT,
    prompt_fingerprint TEXT,
    user_id            TEXT,
    observed_at        TEXT NOT NULL,
    explanation        TEXT,
    -- §8.7 columns. Not among §8.2's eleven fields (MINOR 1); on user-action events only.
    correction_scope   TEXT,
    correction_subject TEXT,
    polarity           TEXT,
    proposal_class     TEXT,
    basis_key          TEXT
);
CREATE TRIGGER IF NOT EXISTS events_no_update
BEFORE UPDATE ON events
BEGIN SELECT RAISE(ABORT, 'events is append-only (R6, 8.2)'); END;
CREATE TRIGGER IF NOT EXISTS events_no_delete
BEFORE DELETE ON events
BEGIN SELECT RAISE(ABORT, 'events is append-only (R6, 8.2)'); END;
CREATE TRIGGER IF NOT EXISTS events_no_replace
BEFORE INSERT ON events
WHEN EXISTS (SELECT 1 FROM events WHERE event_id = NEW.event_id)
BEGIN SELECT RAISE(ABORT, 'events is append-only (R6, 8.2)'); END;
"""


SCAN_USAGE_DDL = """
CREATE TABLE IF NOT EXISTS scan_resource_usage (
    scan_id         TEXT PRIMARY KEY,   -- minted by P1, deliberately not on events
    elapsed_time    TEXT,               -- every counter: JSON, or NULL for unavailable
    memory          TEXT,
    cpu_accelerator TEXT,
    storage         TEXT,
    network         TEXT,
    llm_cost        TEXT,               -- written by P8 (O9), never sampled here
    started_at      TEXT NOT NULL,      -- (mechanics) so elapsed_time is computable
    baseline        TEXT NOT NULL,      -- (mechanics) at-start samples, for deltas
    observed_at     TEXT
);
"""

# Inlined rather than imported from vectors.py, to avoid a circular import.
VECTORS_DDL = """
CREATE TABLE IF NOT EXISTS vector_arrays (
    subject_key      TEXT PRIMARY KEY,
    array_bytes      BLOB NOT NULL,
    producer_version TEXT NOT NULL
);
"""

# Inlined rather than imported from budget.py, to avoid a circular import.
BUDGET_DDL = """
CREATE TABLE IF NOT EXISTS budget_ceilings (
    key           TEXT PRIMARY KEY,
    value         INTEGER NOT NULL,
    object_version INTEGER NOT NULL DEFAULT 1
);
"""

LEARNING_DDL = """
CREATE TABLE IF NOT EXISTS learning_resets (
    scope       TEXT NOT NULL,
    subject_id  TEXT NOT NULL,
    event_id    INTEGER NOT NULL,
    reset_at    TEXT NOT NULL,
    PRIMARY KEY (scope, subject_id, event_id)
);
"""


def create_schema(conn: sqlite3.Connection) -> None:
    """Create every P1-owned table. Idempotent."""
    conn.executescript(FILES_DDL)
    conn.executescript(EVENTS_DDL)
    conn.executescript(LEARNING_DDL)
    conn.executescript(BUDGET_DDL)
    conn.executescript(VECTORS_DDL)
    conn.executescript(SCAN_USAGE_DDL)
