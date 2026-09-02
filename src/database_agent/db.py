"""Contract out §6 — one local SQLite database, transactional and inspectable (§0)."""
from __future__ import annotations

import sqlite3
import uuid
from collections.abc import Iterable
from contextlib import contextmanager
from pathlib import Path

# IMPORTED, not inlined the way `BUDGET_DDL` below is. That one is a copy to avoid
# a circular import; `cloud_consent` imports nothing from this module, so there is
# no cycle to avoid and no reason to keep two spellings of one table.
from database_agent.cloud_consent import CLOUD_CONSENT_DDL

#: 2 added `st_dev`/`st_ino` to `files` (see FILES_DDL). `create_schema` migrates
#: an existing database in place, so the bump records the change rather than gating it.
SCHEMA_VERSION = 2


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


@contextmanager
def batched_writes(conn: sqlite3.Connection, *, size: int):
    """A write transaction that commits every `size` completed units of work.

    Yields a callable; the caller invokes it once per unit finished. Every `size`
    invocations the transaction commits and the next one opens, so the writes of a
    long loop are grouped instead of each one standing alone.

    **Why it exists.** `open_database` opens the connection in autocommit
    (`isolation_level=None`), so without an explicit boundary every statement is
    its own transaction — and at `synchronous = FULL` every one of those is an
    fsync. A scan writes five rows per file admitted, and on macOS that fsync is
    `F_FULLFSYNC`, a flush of the whole device write cache, which stalls the NEXT
    file's `open()` as well as the write it was asked to durably record — a
    cProfile of the scan blamed `_io.open` for 79% of the run, and the same
    profile with one transaction held open showed `_io.open` fall by 5x without
    one line of the hashing changing. Measured over
    `tests/integration/test_scale_stress.py`'s disk-shaped corpus: 13.7 ms per
    file as shipped against 2.2 ms with a boundary, so 11.5 ms of every 13.7 was
    fsync.

    **This trades away no durability.** `synchronous` is untouched: a batch that
    has committed is on the platter exactly as before. What changes is how much a
    power cut can lose — the units completed since the last commit, at most `size`
    of them. Losing those is not corruption and not silent: they are units that
    were never recorded, which is the same state as a run stopped before it
    reached them, and re-running records them. Relaxing `synchronous` instead
    would buy the same speed by making the database itself damageable, which is a
    different thing entirely and is not what this does.

    **Why a batch and not one transaction round the whole loop.** In WAL mode the
    log cannot checkpoint while a write transaction is open, so a single
    transaction over a 500,000-file scan grows a WAL holding every page it wrote,
    and a crash then loses all of it rather than the last `size` units. The batch
    bounds both, and the fsync it still pays amortises to `1/size` of a file.

    Reentrant in the same sense as `transaction`: if a transaction is already in
    flight the caller has already chosen the boundary, so nothing is committed
    here and the yielded callable does nothing.
    """
    if conn.in_transaction:
        yield lambda: None
        return

    pending = 0

    def recorded() -> None:
        nonlocal pending
        pending += 1
        if pending >= size:
            conn.execute("COMMIT")
            conn.execute("BEGIN")
            pending = 0

    conn.execute("BEGIN")
    try:
        yield recorded
    except BaseException:
        # BaseException, not Exception: a scan is long enough to be interrupted by
        # hand, and the batch in flight should be rolled back rather than left
        # half-written for the next statement to commit by accident. Every batch
        # that already committed survives.
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
    sensitivity_state         TEXT,
    -- The inode of `current_path` as `lstat` reported it when this row last wrote
    -- the path, or NULL if the path could not be stat'd. NOT a second identity:
    -- R1 keeps the content hash as the identity of a file version and nothing
    -- reads these two columns except `observe_path`'s identity resolution, which
    -- treats a match as a CANDIDATE and confirms it against the filesystem before
    -- believing it. Inodes are recycled, so a stored pair can name a file that no
    -- longer exists; only `lstat` of the recorded path can say otherwise.
    -- `lstat`, never `stat`: a symlink's own inode, so a link and its target stay
    -- two rows (test_a_symlink_and_its_target_are_recorded_as_two_file_versions).
    st_dev                    INTEGER,
    st_ino                    INTEGER
);
CREATE INDEX IF NOT EXISTS files_content_hash ON files (content_hash);
-- `observe_path` asks `WHERE current_path = ?` twice for every file it
-- admits, and `scan_agent.watch` and `stat_cache` ask it again. Unindexed,
-- each of those is a full pass over every file already recorded, which makes
-- the scan quadratic in the size of the corpus. Not UNIQUE: a superseded row
-- (R3) keeps its path while the new version records the same one.
CREATE INDEX IF NOT EXISTS files_current_path ON files (current_path);
"""

#: Added after the columns exist, because a database created before SCHEMA_VERSION 2
#: reaches `create_schema` without them and `CREATE INDEX` on a missing column errors.
#:
#: `st_dev, st_ino` leads and `content_hash` trails deliberately. `observe_path` asks
#: this index one question -- "is any row for these bytes the inode I am looking at?"
#: -- with all three columns fixed, so column order costs it nothing; but a leading
#: `content_hash` would make this index a candidate for the `WHERE content_hash = ?
#: ORDER BY rowid` probe as well, and SQLite would then sort the whole duplicate
#: family to answer a query that `files_content_hash` already answers in rowid order.
FILES_INODE_DDL = """
CREATE INDEX IF NOT EXISTS files_inode ON files (st_dev, st_ino, content_hash);
"""


#: (column, type) pairs added to `files` after its first release. `CREATE TABLE IF NOT
#: EXISTS` is a no-op on a database that already has the table, so a column added to
#: FILES_DDL never reaches an existing database; these do, and ALTER TABLE ADD COLUMN
#: appends in declaration order, so a migrated table has the same column order as a
#: fresh one (P7 pins that equality against FILES_COLUMNS).
FILES_ADDED_COLUMNS: tuple[tuple[str, str], ...] = (
    ("st_dev", "INTEGER"),
    ("st_ino", "INTEGER"),
)


def _migrate_files(conn: sqlite3.Connection) -> None:
    present = {row["name"] for row in conn.execute("PRAGMA table_info(files)")}
    for column, column_type in FILES_ADDED_COLUMNS:
        if column not in present:
            conn.execute(f"ALTER TABLE files ADD COLUMN {column} {column_type}")


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
-- `events` grows about three rows per file, and two per-file questions are asked
-- of it by `file_id`: P3's "has this file been discovered?" (`basic_record.py:38`)
-- and `file_path_history`. Unindexed, each is a pass over three times the corpus
-- for every file admitted -- the largest single term in the scan's cost. An index
-- adds no way to update or delete a row, so R6's append-only guarantee is untouched.
CREATE INDEX IF NOT EXISTS events_file_id ON events (file_id);
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

# Inlined rather than imported from vector_versions.py, to avoid a circular
# import. Additive: the legacy overwrite table above is untouched.
VECTOR_VERSIONS_DDL = """
CREATE TABLE IF NOT EXISTS vector_embeddings (
    embedding_id      TEXT PRIMARY KEY,
    file_id           TEXT NOT NULL,
    content_hash      TEXT NOT NULL,
    scope             TEXT NOT NULL,
    embedding_model_id TEXT NOT NULL,
    embedding_version TEXT NOT NULL,
    dimension         INTEGER NOT NULL CHECK (dimension > 0),
    encoding          TEXT NOT NULL,
    array_bytes       BLOB NOT NULL,
    created_at        TEXT NOT NULL,
    supersedes        TEXT,
    superseded_by     TEXT,
    supersede_reason  TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS one_current_vector_embedding
    ON vector_embeddings (
        file_id, content_hash, scope, embedding_model_id, embedding_version
    ) WHERE superseded_by IS NULL;
CREATE INDEX IF NOT EXISTS vector_embedding_version
    ON vector_embeddings (file_id, content_hash, scope);
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
    _migrate_files(conn)
    conn.executescript(FILES_INODE_DDL)
    conn.executescript(EVENTS_DDL)
    conn.executescript(LEARNING_DDL)
    conn.executescript(BUDGET_DDL)
    conn.executescript(VECTORS_DDL)
    conn.executescript(VECTOR_VERSIONS_DDL)
    conn.executescript(SCAN_USAGE_DDL)
    # HERE and not in a part's own bootstrap: a person typing the gesture that
    # turns cloud sending OFF must never be stopped because an earlier run refused
    # before it reached a bootstrap step. The table that records a withdrawal
    # exists as soon as the database does.
    conn.executescript(CLOUD_CONSENT_DDL)
