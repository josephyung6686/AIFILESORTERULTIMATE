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
