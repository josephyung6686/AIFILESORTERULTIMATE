"""Contract out §6 — one local SQLite database, transactional and inspectable (§0)."""
from __future__ import annotations

import sqlite3
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
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = FULL")
    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    return conn


@contextmanager
def transaction(conn: sqlite3.Connection):
    """Explicit transaction boundary. P1 publishes this; each part owns its tables."""
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
"""


def create_schema(conn: sqlite3.Connection) -> None:
    """Create every P1-owned table. Idempotent."""
    conn.executescript(FILES_DDL)
    conn.executescript(EVENTS_DDL)
