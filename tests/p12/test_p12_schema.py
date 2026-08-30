"""P12's six tables. Append-only by trigger, not by convention (§8.2)."""
from __future__ import annotations

import sqlite3

import pytest

from database_agent.supersede import SUPERSEDE_COLUMNS
from mutation.schema import P12_TABLES, create_mutation_schema


def _columns(conn, table):
    return tuple(row[1] for row in conn.execute(f"PRAGMA table_info({table})"))


def test_p12_owns_exactly_six_tables(p12_conn):
    assert P12_TABLES == (
        "move_plans", "path_resolutions", "execution_records",
        "collision_resolutions", "move_journal", "undo_retention",
    )
    live = {row[0] for row in p12_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    assert set(P12_TABLES) <= live


def test_creating_the_schema_twice_is_safe(conn):
    create_mutation_schema(conn)
    create_mutation_schema(conn)


def test_every_p12_table_carries_the_supersede_columns(p12_conn):
    for table in P12_TABLES:
        assert set(SUPERSEDE_COLUMNS) <= set(_columns(p12_conn, table))


#: One row per table, so the delete guard is tested against a table that HAS
#: something to lose. `DELETE FROM` an empty table fires no BEFORE DELETE trigger
#: at all, so the seed is what makes the assertion mean anything. This is
#: `tests/p11/test_p11_store.py:245`'s idiom, for the same reason.
_SEED: dict[str, tuple[str, tuple[str, ...]]] = {
    "move_plans": (
        "(record_id, plan_id, plan_version, decision_ref, file_id, node_id, "
        "created_at, payload) VALUES (?,?,?,?,?,?,?,?)",
        ("seed", "p-seed", "plan_1", "d1", "f1", "n1", "2026-08-29T00:00:00Z", "{}")),
    "path_resolutions": (
        "(record_id, resolution_id, plan_version, node_id, cross_folder_verdict, "
        "created_at, payload) VALUES (?,?,?,?,?,?,?)",
        ("seed", "res-seed", "plan_1", "n1", "within_root",
         "2026-08-29T00:00:00Z", "{}")),
    "execution_records": (
        "(record_id, plan_id, plan_version, result, finished_at, payload) "
        "VALUES (?,?,?,?,?,?)",
        ("seed", "p-seed", "plan_1", "applied", "2026-08-29T00:00:00Z", "{}")),
    "collision_resolutions": (
        "(record_id, plan_id, colliding_destination_path, collision_kind, "
        "behaviour_applied, outcome, created_at, payload) VALUES (?,?,?,?,?,?,?,?)",
        ("seed", "p-seed", "/fixture/a.pdf", "name_only", "stop_and_ask",
         "halted awaiting user", "2026-08-29T00:00:00Z", "{}")),
    "move_journal": (
        "(record_id, entry_id, entry_kind, plan_id, plan_version, file_id, "
        "original_source_path, destination_path, content_hash, time_of_execution, "
        "payload) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        ("seed", "j-seed", "applied", "p-seed", "plan_1", "f1", "/fixture/a.pdf",
         "/fixture/b/a.pdf", "hash", "2026-08-29T00:00:00Z", "{}")),
    "undo_retention": (
        "(record_id, retention_choice, set_at, payload) VALUES (?,?,?,?)",
        ("seed", "thirty_days", "2026-08-29T00:00:00Z", "{}")),
}


def test_every_p12_table_refuses_a_delete(p12_conn):
    assert set(_SEED) == set(P12_TABLES)
    for table, (columns, params) in _SEED.items():
        p12_conn.execute(f"INSERT INTO {table} {columns}", params)
    for table in P12_TABLES:
        assert p12_conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        with pytest.raises(sqlite3.IntegrityError):
            p12_conn.execute(f"DELETE FROM {table}")


def test_every_p12_table_refuses_an_overwrite_but_permits_its_supersede_link(p12_conn):
    p12_conn.execute(
        "INSERT INTO move_plans (record_id, plan_id, plan_version, decision_ref, "
        "file_id, node_id, created_at, payload) VALUES (?,?,?,?,?,?,?,?)",
        ("r1", "p1", "plan_1", "d1", "f1", "n1", "2026-08-29T00:00:00Z", "{}"))
    with pytest.raises(sqlite3.IntegrityError):
        p12_conn.execute("UPDATE move_plans SET payload = ? WHERE record_id = ?",
                         ('{"changed": true}', "r1"))
    p12_conn.execute("UPDATE move_plans SET superseded_by = ? WHERE record_id = ?",
                     ("r2", "r1"))
    assert p12_conn.execute(
        "SELECT superseded_by FROM move_plans WHERE record_id = ?",
        ("r1",)).fetchone()[0] == "r2"


def test_one_current_plan_per_plan_id(p12_conn):
    p12_conn.execute(
        "INSERT INTO move_plans (record_id, plan_id, plan_version, decision_ref, "
        "file_id, node_id, created_at, payload) VALUES (?,?,?,?,?,?,?,?)",
        ("r1", "p1", "plan_1", "d1", "f1", "n1", "2026-08-29T00:00:00Z", "{}"))
    with pytest.raises(sqlite3.IntegrityError):
        p12_conn.execute(
            "INSERT INTO move_plans (record_id, plan_id, plan_version, decision_ref, "
            "file_id, node_id, created_at, payload) VALUES (?,?,?,?,?,?,?,?)",
            ("r2", "p1", "plan_1", "d1", "f1", "n1", "2026-08-29T00:01:00Z", "{}"))


def test_the_journal_has_no_current_row_concept_because_it_is_a_log(p12_conn):
    indexes = {row[1] for row in p12_conn.execute("PRAGMA index_list(move_journal)")}
    assert not any(name.startswith("one_current") for name in indexes)


def test_only_one_undo_retention_row_is_current_at_a_time(p12_conn):
    """F10 — `66` §11's retention is a corpus-wide setting today, and a later
    per-policy setting (`66` §8) will have to reconcile with it. The index says
    so: one un-superseded row for the whole database."""
    p12_conn.execute(
        "INSERT INTO undo_retention (record_id, retention_choice, set_at, payload) "
        "VALUES (?,?,?,?)", ("r1", "thirty_days", "2026-08-29T00:00:00Z", "{}"))
    with pytest.raises(sqlite3.IntegrityError):
        p12_conn.execute(
            "INSERT INTO undo_retention (record_id, retention_choice, set_at, "
            "payload) VALUES (?,?,?,?)",
            ("r2", "ninety_days", "2026-08-29T00:01:00Z", "{}"))
