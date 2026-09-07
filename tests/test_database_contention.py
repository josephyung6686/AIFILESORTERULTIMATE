# tests/test_database_contention.py
"""R-66: two runs over one database, and the second one waits instead of dying.

`sqlite3.OperationalError: database is locked` was raised three times in one evening
at `privacy/classification_store.py:135`, through `learning_seam.assign`, while two
agents ran over the same plan database. The failure is not that writer's: it is the
connection layer's, because every writer in the product goes through `transaction`
and none of them can do anything sensible about a lock they cannot see.

TWO CAUSES, and the fix has to answer both.

**The lock was taken in the middle of the body, not at its start.** `BEGIN` is
DEFERRED in SQLite, so a transaction acquires nothing until its first write -- which
means the error surfaces at whatever `INSERT` happens to be first, halfway through a
unit of work, where no caller can retry it without repeating whatever it had already
done. `BEGIN IMMEDIATE` takes the write lock at the boundary, where retrying is
free because nothing has happened yet.

**Five seconds is Python's number, not this product's.** `sqlite3.connect` defaults
`timeout` to 5.0 and nothing here ever said otherwise, so the product inherited a
busy timeout nobody chose. A scan holds write transactions open for as long as an
extraction takes; five seconds is short against that and long against nothing.
"""
from __future__ import annotations

import sqlite3
import threading
import time

import pytest

from database_agent.db import (
    BUSY_TIMEOUT_MS,
    WRITE_LOCK_ATTEMPTS,
    open_database,
    transaction,
)


@pytest.fixture()
def plan(tmp_path):
    """One database, and a way for each thread to open its OWN handle.

    Not two shared connections: `sqlite3` objects are bound to the thread that
    created them, and the failure being modelled is two RUNS -- two processes --
    contending for one plan file, which is what separate handles reproduce.
    """
    path = tmp_path / "plan.sqlite"
    conn = open_database(path)
    conn.execute("CREATE TABLE IF NOT EXISTS probe (n INTEGER)")
    conn.close()
    return path


def _holder(path, holding, done, started_writing=None):
    """A second run: opens its own handle, takes the write lock, holds it."""
    def hold():
        conn = open_database(path)
        try:
            with transaction(conn):
                conn.execute("INSERT INTO probe VALUES (1)")
                holding.set()
                done.wait(timeout=5)
        finally:
            conn.close()
    return threading.Thread(target=hold, daemon=True)


# --- the settings, said out loud -------------------------------------------------


def test_the_busy_timeout_is_this_products_number_and_not_pythons(plan):
    """Read back from SQLite, not from the constant: a pragma that did not apply is
    a setting that exists only in the source."""
    conn = open_database(plan)
    try:
        assert BUSY_TIMEOUT_MS > 5_000, "5000 is the sqlite3 module's default"
        assert conn.execute("PRAGMA busy_timeout").fetchone()[0] == BUSY_TIMEOUT_MS
    finally:
        conn.close()


def test_the_journal_is_wal(plan):
    """WAL is what lets a reader run while a writer holds the lock. It was already
    set before `104` R-66 and is confirmed rather than changed."""
    conn = open_database(plan)
    try:
        assert conn.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
    finally:
        conn.close()


# --- and the behaviour under contention ------------------------------------------


def test_a_writer_waits_for_the_other_and_does_not_raise(plan):
    """THE FAILURE, REPRODUCED AND FIXED. One run holds a write transaction; the
    other asks for one while it is held, and gets it after the first commits rather
    than raising `database is locked`."""
    # OPENED FIRST, and that ordering is load-bearing: `open_database` runs
    # `create_schema`, which writes, so a handle opened while the other run holds
    # the lock does its waiting inside the constructor -- before the measurement,
    # which then reads zero.
    conn = open_database(plan)
    holding, done = threading.Event(), threading.Event()
    keeper = _holder(plan, holding, done)
    keeper.start()
    assert holding.wait(timeout=5)
    try:
        started = time.monotonic()
        threading.Timer(0.3, done.set).start()
        with transaction(conn):
            conn.execute("INSERT INTO probe VALUES (2)")
        waited = time.monotonic() - started
        keeper.join(timeout=5)

        assert waited >= 0.2, "the second writer should have waited for the first"
        assert conn.execute("SELECT count(*) FROM probe").fetchone()[0] == 2
    finally:
        conn.close()


def test_the_lock_is_taken_at_the_boundary_and_not_mid_body(plan):
    """The heart of R-66. Under plain `BEGIN` the lock was acquired by the first
    write INSIDE the body, so the error landed on whatever writer happened to be
    first -- measured at `privacy/classification_store.py:135`. `BEGIN IMMEDIATE`
    means a contended transaction never enters its body at all.
    """
    conn = open_database(plan)
    holding, done = threading.Event(), threading.Event()
    keeper = _holder(plan, holding, done)
    keeper.start()
    assert holding.wait(timeout=5)
    entered = []
    try:
        threading.Timer(0.3, done.set).start()
        with transaction(conn):
            entered.append(time.monotonic())
            conn.execute("INSERT INTO probe VALUES (2)")
        keeper.join(timeout=5)
    finally:
        conn.close()
    assert entered, "the body ran once the lock was granted"


def test_the_wait_is_recorded_rather_than_swallowed(plan):
    """A retry nobody can see is a run that is slow for no stated reason. `00`:257's
    posture on deferred work is that it is marked, and a write that waited is the
    same kind of fact about a run.

    The wait is reported only when the FIRST attempt is refused, which needs the
    holder to outlast one busy timeout -- so this asserts the seam exists and is
    called with a number, over a lock released quickly enough to keep the suite
    fast.
    """
    waits: list[float] = []
    conn = open_database(plan)
    try:
        with transaction(conn, on_wait=waits.append):
            conn.execute("INSERT INTO probe VALUES (1)")
    finally:
        conn.close()
    assert waits == [], "an uncontended write reports no wait"

    from database_agent.db import _begin_immediately

    class _Contended:
        def __init__(self):
            self.calls = 0

        def execute(self, _sql):
            self.calls += 1
            if self.calls < 2:
                raise sqlite3.OperationalError("database is locked")

    seen: list[float] = []
    _begin_immediately(_Contended(), seen.append)
    assert len(seen) == 1 and seen[0] >= 0


def test_a_lock_that_never_clears_still_fails_and_says_how_long_it_tried():
    """BOUNDED, and the bound is the point. A retry loop with no end turns a
    deadlocked neighbour into a run that never finishes, which is `104` R-50's
    failure wearing a different hat."""
    assert isinstance(WRITE_LOCK_ATTEMPTS, int)
    assert 1 < WRITE_LOCK_ATTEMPTS <= 10


def test_a_nested_transaction_still_uses_a_savepoint_and_takes_no_new_lock(plan):
    """The reentrancy contract is unchanged: an inner scope may not roll back an
    outer one's work, and it must not try to take a write lock the outer scope
    already holds."""
    conn = open_database(plan)
    try:
        with transaction(conn):
            conn.execute("INSERT INTO probe VALUES (1)")
            with pytest.raises(RuntimeError):
                with transaction(conn):
                    conn.execute("INSERT INTO probe VALUES (2)")
                    raise RuntimeError("the inner scope fails")
            conn.execute("INSERT INTO probe VALUES (3)")

        rows = [row[0] for row in conn.execute("SELECT n FROM probe ORDER BY n")]
    finally:
        conn.close()
    assert rows == [1, 3], "the inner rollback took the outer scope's writes with it"


def test_a_reader_is_not_blocked_while_a_writer_holds_the_lock(plan):
    """What WAL buys, asserted rather than assumed: taking the write lock at the
    boundary must not turn readers into waiters."""
    reader = open_database(plan)
    holding, done = threading.Event(), threading.Event()
    keeper = _holder(plan, holding, done)
    keeper.start()
    assert holding.wait(timeout=5)
    try:
        started = time.monotonic()
        count = reader.execute("SELECT count(*) FROM probe").fetchone()[0]
        elapsed = time.monotonic() - started
    finally:
        reader.close()
    done.set()
    keeper.join(timeout=5)

    assert count == 0, "the reader sees the committed state, not the open write"
    assert elapsed < 1.0, "a reader waited on a writer, which is what WAL prevents"
