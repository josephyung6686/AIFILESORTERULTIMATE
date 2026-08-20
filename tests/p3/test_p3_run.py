# tests/p3/test_p3_run.py
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.events import EVENT_FIELDS

from scan_agent.run import finish_scan_run, get_scan_run, start_scan_run
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection


@pytest.fixture()
def selection(conn, tmp_path: Path):
    create_schema(conn)
    create_scan_schema(conn)
    return record_selection(conn, sources=[tmp_path], candidate_roots=[],
                            cross_folder_moves=False, selected_by=None)


def test_a_run_brackets_a_start_and_an_end(conn, selection):
    scan_run_id = start_scan_run(conn, selection)
    assert get_scan_run(conn, scan_run_id)["started_at"]
    assert get_scan_run(conn, scan_run_id)["completed_at"] is None
    finish_scan_run(conn, scan_run_id)
    assert get_scan_run(conn, scan_run_id)["completed_at"]


def test_the_run_handle_is_never_written_to_events(conn, selection):
    # OQ16 closed the PUBLICATION question, not the event-row question. P1 §10 keeps
    # the scan identifier off `events`; §8.2's record keeps its eleven fields
    # (MINOR 1). This test is what stops the closure being over-read.
    start_scan_run(conn, selection)
    assert "scan_run_id" not in EVENT_FIELDS
    assert "scan_id" not in EVENT_FIELDS
    columns = [r["name"] for r in conn.execute("PRAGMA table_info(events)")]
    assert "scan_run_id" not in columns


def test_p3_publishes_the_scan_identity_and_p1_adopts_it(conn, selection):
    # OQ16 closed 2026-08-20: P3 owns the scan, so P3 owns its name. P1 keys
    # `scan_resource_usage` on the value P3 hands it and mints none of its own.
    from database_agent.scan_usage import scan_resource_usage

    scan_run_id = start_scan_run(conn, selection)
    assert scan_resource_usage(conn, scan_run_id)["scan_id"] == scan_run_id


def test_the_six_counters_land_against_the_published_identity(conn, selection):
    # P3-H is lifted: sampling was blocked only by the absence of a shared key.
    from database_agent.scan_usage import RESOURCE_COUNTERS, scan_resource_usage

    scan_run_id = start_scan_run(conn, selection)
    finish_scan_run(conn, scan_run_id)
    row = scan_resource_usage(conn, scan_run_id)
    assert set(RESOURCE_COUNTERS) <= set(row.keys())
    assert row["elapsed_time"] is not None   # P1 samples five of the six
    assert row["llm_cost"] is None           # the sixth is P8's (O9), never P3's


def test_a_run_names_the_selection_it_scanned(conn, selection):
    scan_run_id = start_scan_run(conn, selection)
    assert get_scan_run(conn, scan_run_id)["selection_id"] == selection


def test_a_run_cannot_reference_a_selection_that_does_not_exist(conn, selection):
    import sqlite3
    with pytest.raises(sqlite3.IntegrityError):
        start_scan_run(conn, "no-such-selection")
