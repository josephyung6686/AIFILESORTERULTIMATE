# tests/eval/test_store.py
import sqlite3
from pathlib import Path

from database_agent.db import open_database

from eval_harness.store import (
    EVAL_SCHEMA_VERSION, EVAL_TABLES, canonical_json, content_ref, create_eval_schema,
)


def _table_names(conn: sqlite3.Connection) -> set[str]:
    return {r["name"] for r in
            conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}


def test_eval_tables_names_every_table_p2_will_own(eval_conn):
    # EVAL_TABLES is the manifest of P2's surface. Tasks 3-15 each add the DDL
    # for one or more of these names; this list is what Task 16's column guard
    # walks, so a table missing from it escapes the no-aggregate scan.
    # 19 since `bundle_recording`, added with EVAL_SCHEMA_VERSION 2.
    assert len(EVAL_TABLES) == len(set(EVAL_TABLES)) == 19
    assert EVAL_TABLES[0] == "eval_schema_meta"


def test_create_eval_schema_creates_the_tables_wired_so_far(eval_conn):
    # At Task 1 only the meta table is wired. From Task 3 onward each task's own
    # test asserts its table exists; test_no_aggregate.py (Task 16) asserts at the
    # end that every EVAL_TABLES name has been created.
    create_eval_schema(eval_conn)
    assert "eval_schema_meta" in _table_names(eval_conn)


def test_create_eval_schema_is_idempotent(eval_conn):
    create_eval_schema(eval_conn)
    create_eval_schema(eval_conn)
    assert "eval_schema_meta" in _table_names(eval_conn)


def test_p2_creates_no_p1_table(eval_conn):
    # §0: each part owns its own tables. P2 does not create, alter, or shadow
    # `files` or `events`; P1's create_schema is the only thing that makes them.
    #
    # The check is a DELTA, not an absence. P1's `open_database` calls its own
    # `create_schema`, so `files` and `events` exist before P2 runs at all —
    # asserting they are absent would test P1's wiring, not P2's restraint. What
    # P2 must prove is that ITS schema call adds nothing outside its own set.
    before = _table_names(eval_conn)
    create_eval_schema(eval_conn)
    added = _table_names(eval_conn) - before
    assert added <= set(EVAL_TABLES), f"P2 created tables it does not own: {added - set(EVAL_TABLES)}"
    assert "files" not in added
    assert "events" not in added


def test_no_bundle_table_references_the_live_files_table(eval_conn):
    # A bundle must load into a database whose `files` table is empty (§8.5
    # "without touching a live filesystem"; SPEC OQ5 on export). A foreign key
    # into P1's table would decide OQ5 by making that impossible.
    create_eval_schema(eval_conn)
    created = _table_names(eval_conn) & set(EVAL_TABLES)
    for table in created:
        targets = {r["table"] for r in
                   eval_conn.execute(f"PRAGMA foreign_key_list({table})")}
        assert "files" not in targets and "events" not in targets, table


def test_schema_version_is_recorded_separately_from_p1s(eval_conn):
    create_eval_schema(eval_conn)
    row = eval_conn.execute(
        "SELECT value FROM eval_schema_meta WHERE key = 'eval_schema_version'"
    ).fetchone()
    assert int(row["value"]) == EVAL_SCHEMA_VERSION


def test_canonical_json_is_order_independent():
    # Value comparison in Task 10 is exact equality over this form, so the form
    # must not depend on key order. No tolerance, no rounding (SPEC OQ2 open).
    assert canonical_json({"b": 1, "a": [2, 3]}) == canonical_json({"a": [2, 3], "b": 1})
    assert canonical_json({"a": 1}) != canonical_json({"a": 1.0000001})


def test_content_ref_is_stable_and_distinguishing():
    assert content_ref(canonical_json({"a": 1})) == content_ref(canonical_json({"a": 1}))
    assert content_ref(canonical_json({"a": 1})) != content_ref(canonical_json({"a": 2}))
    assert len(content_ref("x")) == 71 and content_ref("x").startswith("sha256:")
