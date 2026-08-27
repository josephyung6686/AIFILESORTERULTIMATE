import sqlite3
from pathlib import Path

import pytest

from database_agent.db import (
    DatabaseInsideCorpus, default_database_path, open_database, transaction,
)


def test_default_location_is_application_support(tmp_path: Path):
    # 11-ops-runtime.md §2: Application Support / bundle identifier / agent.sqlite
    path = default_database_path("example.bundle.identifier")
    assert path.parts[-4:] == ("Library", "Application Support",
                               "example.bundle.identifier", "agent.sqlite")
    assert path.is_absolute()


def test_database_is_refused_inside_a_scan_root(tmp_path: Path):
    # 11-ops-runtime.md §2: never created inside a scan root, a candidate root,
    # or the destination tree. P3's exclusion rules never have to special-case it.
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    with pytest.raises(DatabaseInsideCorpus):
        open_database(corpus / "agent.sqlite", scan_roots=[corpus])


def test_database_outside_every_declared_root_is_allowed(tmp_path: Path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    conn = open_database(tmp_path / "support" / "agent.sqlite", scan_roots=[corpus])
    conn.close()


def test_open_database_creates_one_file(tmp_path: Path):
    db_path = tmp_path / "agent.sqlite"
    conn = open_database(db_path)
    assert db_path.exists()
    assert isinstance(conn, sqlite3.Connection)
    conn.close()


def test_foreign_keys_are_enforced(tmp_path: Path):
    conn = open_database(tmp_path / "agent.sqlite")
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    conn.close()


def test_transaction_rolls_back_on_error(tmp_path: Path):
    conn = open_database(tmp_path / "agent.sqlite")
    conn.execute("CREATE TABLE t (x INTEGER)")
    conn.commit()
    try:
        with transaction(conn):
            conn.execute("INSERT INTO t VALUES (1)")
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    assert conn.execute("SELECT count(*) FROM t").fetchone()[0] == 0
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Query plans. The scan's cost per file must not grow with the corpus.
# ─────────────────────────────────────────────────────────────────────────────

def _plan(conn: sqlite3.Connection, sql: str, *params) -> list[str]:
    return [row[3] for row in conn.execute("EXPLAIN QUERY PLAN " + sql, params)]


def test_identity_lookups_by_path_search_an_index_instead_of_scanning(
        tmp_path: Path):
    """`observe_path` asks `WHERE current_path = ?` twice for every file it admits
    (`files_table.py:258` and `:283`), and `scan_agent.watch` and `stat_cache` ask
    the same question again. Without an index on `current_path` each of those is a
    full pass over every file already recorded, so the scan — the first thing the
    product does — costs O(corpus²) before any content is read.

    This asserts the property rather than the schema text: what matters is that
    SQLite reaches the row by SEARCH, not that a particular `CREATE INDEX` string
    appears in the DDL.
    """
    from database_agent.db import create_schema

    conn = open_database(tmp_path / "agent.sqlite")
    create_schema(conn)

    for sql in (
        # files_table.observe_path — the path-taken guard and the R3 supersede lookup
        "SELECT 1 FROM files WHERE current_path = ? AND scan_state != ?",
        "SELECT file_id FROM files WHERE current_path = ? AND scan_state != ?",
    ):
        steps = _plan(conn, sql, "/some/path", "superseded_content")
        assert all("SCAN files" not in step for step in steps), (
            f"{sql!r} plans as {steps}. Every file observed costs a full pass over "
            "every file already recorded, which makes the scan quadratic in the "
            "size of the corpus. `files` needs an index on `current_path`."
        )
        assert any(step.startswith("SEARCH files") for step in steps), steps
    conn.close()


def test_the_per_file_event_lookups_search_an_index_instead_of_scanning(
        tmp_path: Path):
    """`scan_agent.basic_record` asks whether this file already has a discovery
    event once per file admitted (`basic_record.py:38`), and `file_path_history`
    asks the same table the same way (`files_table.py:329`). `events` grows about
    three rows per file, so an unindexed `WHERE file_id = ?` costs a pass over
    three times the corpus for every file — the largest single term in the scan's
    cost, larger than either `current_path` lookup.

    `events` is append-only and protected against DROP; an index over it changes
    nothing about that.
    """
    from database_agent.db import create_schema

    conn = open_database(tmp_path / "agent.sqlite")
    create_schema(conn)

    for sql, params in (
        ("SELECT 1 FROM events WHERE file_id = ? AND event_type = 'discovery' "
         "LIMIT 1", ("f1",)),
        ("SELECT event_id FROM events WHERE file_id = ? AND (new_path IS NOT NULL "
         "OR old_path IS NOT NULL) ORDER BY event_id", ("f1",)),
    ):
        steps = _plan(conn, sql, *params)
        assert all("SCAN events" not in step for step in steps), (
            f"{sql!r} plans as {steps}. `events` carries no index on `file_id`, so "
            "every file admitted reads every event already appended. This is the "
            "dominant quadratic in the scan."
        )
        assert any(step.startswith("SEARCH events") for step in steps), steps
    conn.close()
