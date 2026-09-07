"""`chain()` addresses `file_facts` through a column no index could find.

`record_id` is a VIRTUAL generated projection of `fact_id`, added so P1's
`mark_superseded` and `chain` -- both `... WHERE record_id = ?` -- can address this
table unchanged. `fact_id` is the primary key and is indexed; `record_id` is not the
primary key and had no index of its own, so **every** link `chain()` walks was a full
scan of `file_facts`.

Measured, P8--P11 over a 1,000-file synthetic corpus, `cProfile`: 78,384 calls to
`database_agent.supersede.chain` and 240,385 `fetchone` calls costing 23.5 of the
106.9 profiled seconds -- 22% of the whole plan-building run spent scanning a
three-thousand-row table for a row its primary key already addresses. The caller is
`facts.supersede._slot`, which P10 reaches 175,892 times through
`preferred_value_for`, and the cost grows with the corpus on both sides: more facts
to scan, and more files to ask about.

This is the one table where it happens. Every other table `chain()` walks declares
`record_id` as a real column -- P4's `evidence` uses the same virtual device and is
read by `chain` too, and is checked below for the same reason.

The fix is an index and nothing else: no threshold moves, no query changes shape, and
the statement returns the row it already returned. What this file asserts is that the
planner can find it.
"""
from __future__ import annotations

import pytest

from facts.schema import create_facts_schema


@pytest.fixture()
def facts_conn(conn):
    create_facts_schema(conn)
    return conn


def _plan(conn, statement: str, parameters=()) -> str:
    return " | ".join(
        str(row[3]) for row in conn.execute(
            f"EXPLAIN QUERY PLAN {statement}", parameters))


def test_the_chain_lookup_searches_rather_than_scans(facts_conn):
    """`chain()`'s own statement, planned. A SCAN here is the defect."""
    plan = _plan(facts_conn, "SELECT * FROM file_facts WHERE record_id = ?", ("x",))
    assert "SCAN" not in plan, (
        f"`chain()` reads file_facts as {plan!r}; `record_id` is a virtual "
        "projection of the primary key and every supersede walk scans the whole "
        "table for a row the key already addresses")
    assert "SEARCH" in plan, plan


def test_the_supersede_walk_searches_too(facts_conn):
    """`mark_superseded`'s cycle guard reads the same column the same way."""
    plan = _plan(facts_conn,
                 "SELECT superseded_by FROM file_facts WHERE record_id = ?", ("x",))
    assert "SCAN" not in plan, plan


def test_the_evidence_table_has_the_same_shape_and_is_not_on_the_measured_path(
        facts_conn):
    """What was checked and deliberately not changed, recorded as a test.

    P4's `evidence` carries the same virtual `record_id` projection and is read by
    the same `chain`, and it plans as a SCAN too. It is NOT fixed here, and the
    reason is measurement rather than tidiness: the 1,000-file profile attributes
    all 78,384 `chain` calls to `facts.supersede._slot` over `file_facts` and none
    to `evidence`, whose walk (`evidence_shape.store.supersede_chain`) is a
    review-surface read of one observation's history. Widening a schema this item
    did not measure would be a change nobody could point at a number for.

    This test asserts the shape is still there, so the day `evidence` DOES appear in
    a profile there is a test naming it rather than a rediscovery.
    """
    from evidence_shape.schema import create_evidence_schema

    create_evidence_schema(facts_conn)
    plan = _plan(facts_conn, "SELECT * FROM evidence WHERE record_id = ?", ("x",))
    assert "SCAN" in plan, (
        f"P4's evidence table now plans as {plan!r}; if somebody indexed it, this "
        "test should record the measurement that justified it")


def test_the_first_wins_read_of_subject_facts_keeps_its_plan(facts_conn):
    """The ordering guard, and the reason it is here rather than in a comment.

    `cli.py`'s protected-subject read has no ORDER BY and takes the FIRST row per
    file (`subject_of.setdefault`), so its result depends on the order SQLite
    returns rows in -- and adding an index is exactly the change that can silently
    reorder such a statement. The plan below must stay a search on
    `file_facts_field`, which is the index that answers `field_key = 'subject'`; a
    new index on `record_id` cannot help that predicate and must not be chosen for
    it.
    """
    plan = _plan(
        facts_conn,
        "SELECT f.file_id FROM file_facts AS f "
        "WHERE f.field_key = 'subject' AND f.active = 1 "
        "AND f.superseded_by IS NULL")
    assert "file_facts_field" in plan, plan
    assert "record_id" not in plan, (
        f"the unordered first-wins read is now planned as {plan!r}; an index chosen "
        "here would change which subject fact a protected file is judged by")
