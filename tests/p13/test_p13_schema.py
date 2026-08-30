"""P13's three tables, inside P1's one database, append-only."""
from __future__ import annotations

import sqlite3

import pytest

from review_surface.schema import REVIEW_TABLES, create_review_schema


def _tables(conn) -> set[str]:
    return {row["name"] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}


def test_p13_owns_exactly_three_tables(p13_conn):
    assert REVIEW_TABLES == (
        "review_actions", "review_approvals", "review_presentations")
    assert set(REVIEW_TABLES) <= _tables(p13_conn)


def test_creating_the_schema_twice_is_a_no_op(p13_conn):
    before = _tables(p13_conn)
    create_review_schema(p13_conn)
    assert _tables(p13_conn) == before


def test_p13_creates_no_table_belonging_to_another_part(conn):
    """A fresh connection with ONLY P1 and P13 must gain exactly three tables."""
    from database_agent.db import create_schema
    create_schema(conn)
    before = _tables(conn)
    create_review_schema(conn)
    assert _tables(conn) - before == set(REVIEW_TABLES)


def _seed(conn, table: str) -> None:
    """One row per table, written with raw SQL rather than through a writer.

    A trigger only fires over a row, so an UPDATE against an empty table proves
    nothing at all -- it succeeds by affecting nothing. This is the same reason
    P11's conftest creates P9's tables: a check against an absent thing measures
    the absence, not the check.
    """
    columns = [row["name"] for row in conn.execute(f"PRAGMA table_info({table})")]
    placeholders = ", ".join("?" for _ in columns)
    conn.execute(f"INSERT INTO {table} VALUES ({placeholders})",
                 tuple("seed" for _ in columns))


@pytest.mark.parametrize("table", ("review_actions", "review_approvals",
                                   "review_presentations"))
def test_every_p13_table_refuses_an_update_and_a_delete(p13_conn, table):
    """§8.2 is append-only and P13 owns no supersedable record."""
    p13_conn.execute("PRAGMA foreign_keys = OFF")
    _seed(p13_conn, table)
    columns = [row["name"] for row in
               p13_conn.execute(f"PRAGMA table_info({table})")]
    first = columns[0]
    with pytest.raises(sqlite3.IntegrityError):
        p13_conn.execute(f"UPDATE {table} SET {first} = {first}")
    with pytest.raises(sqlite3.IntegrityError):
        p13_conn.execute(f"DELETE FROM {table}")


def test_no_p13_table_carries_a_supersede_column(p13_conn):
    """A supersede column with no writer is the defect class this project has
    paid for most often. P13 owns no supersedable record, so there is none."""
    for table in REVIEW_TABLES:
        for row in p13_conn.execute(f"PRAGMA table_info({table})"):
            assert "supersede" not in row["name"], (
                f"{table}.{row['name']} implies P13 revises a record it owns")


def test_no_p13_column_names_a_path_or_a_score(p13_conn):
    """B3: P13 shows a node and its ancestor labels, never a resolved path.

    `undo_conflict` paths are carried on an item record built from P12's own
    record, never stored in a P13 table -- see the SPEC's apply and undo-conflict
    items, which is the one place §8.3 demands the four path fields.
    """
    forbidden = ("path", "score", "confidence_value", "threshold", "weight")
    for table in REVIEW_TABLES:
        for row in p13_conn.execute(f"PRAGMA table_info({table})"):
            for substring in forbidden:
                assert substring not in row["name"], (
                    f"{table}.{row['name']} contains {substring!r}")
