import json

from database_agent.db import create_schema
from database_agent.events import EVENT_FIELDS
from database_agent.scan_usage import (
    RESOURCE_COUNTERS, record_llm_cost, sample_scan_resources, scan_resource_usage,
    start_scan,
)


def test_the_six_resources_are_the_six_8_6_names():
    assert RESOURCE_COUNTERS == (
        "elapsed_time", "memory", "cpu_accelerator", "storage", "network", "llm_cost",
    )


def test_a_completed_scan_yields_one_row_carrying_all_six(conn):
    create_schema(conn)
    scan_id = start_scan(conn, scan_run_id="p3-scan-fixture")
    sample_scan_resources(conn, scan_id)
    record_llm_cost(conn, scan_id, {"currency": "USD", "amount": "0"}, author="P8")

    rows = conn.execute("SELECT * FROM scan_resource_usage").fetchall()
    assert len(rows) == 1
    row = scan_resource_usage(conn, scan_id)
    for counter in RESOURCE_COUNTERS:
        assert counter in row.keys()
    assert row["observed_at"]


def test_p1_samples_five_and_p8_writes_the_sixth(conn):
    # SPEC §10: llm_cost is written by P8, "the only part that can know it" (O9).
    create_schema(conn)
    scan_id = start_scan(conn, scan_run_id="p3-scan-fixture")
    sample_scan_resources(conn, scan_id)
    assert scan_resource_usage(conn, scan_id)["llm_cost"] is None
    record_llm_cost(conn, scan_id, {"currency": "USD", "amount": "1.25"}, author="P8")
    assert json.loads(scan_resource_usage(conn, scan_id)["llm_cost"])["amount"] == "1.25"


def test_an_unsampled_counter_reads_as_unavailable_never_as_zero(conn):
    # There is no network byte counter, no portable current-RSS reading and no
    # accelerator time in the standard library. Each reads as null, not 0.
    create_schema(conn)
    scan_id = start_scan(conn, scan_run_id="p3-scan-fixture")
    sample_scan_resources(conn, scan_id)
    row = scan_resource_usage(conn, scan_id)

    assert row["network"] is None
    assert json.loads(row["memory"])["current_bytes"] is None
    assert json.loads(row["cpu_accelerator"])["accelerator_seconds"] is None
    for counter in RESOURCE_COUNTERS:
        assert row[counter] != 0
        assert row[counter] != "0"


def test_what_could_be_sampled_is_a_number(conn):
    create_schema(conn)
    scan_id = start_scan(conn, scan_run_id="p3-scan-fixture")
    sample_scan_resources(conn, scan_id)
    row = scan_resource_usage(conn, scan_id)
    assert json.loads(row["elapsed_time"])["seconds"] >= 0
    assert json.loads(row["memory"])["peak_bytes"] > 0
    assert json.loads(row["cpu_accelerator"])["cpu_seconds"] >= 0
    assert json.loads(row["storage"])["database_bytes"] > 0


def test_p1_rejects_no_operation_for_any_value_of_any_counter(conn):
    # Done-means 16's negative test. Recording six counters gives P1 no ceiling on
    # any of them: there is no threshold to hit.
    create_schema(conn)
    scan_id = start_scan(conn, scan_run_id="p3-scan-fixture")
    record_llm_cost(conn, scan_id, {"currency": "USD", "amount": "999999999"},
                    author="P8")
    sample_scan_resources(conn, scan_id)          # still samples
    assert scan_resource_usage(conn, scan_id) is not None
    # and the module holds no threshold to compare against
    import database_agent.scan_usage as module
    assert not [n for n in dir(module)
                if any(t in n.lower() for t in ("max_", "limit", "ceiling", "threshold"))]


def test_scan_id_is_on_none_of_the_event_fields(conn):
    # Done-means 16's second negative test, and MINOR 1.
    create_schema(conn)
    assert len(EVENT_FIELDS) == 11
    assert "scan_id" not in EVENT_FIELDS
    columns = [r["name"] for r in conn.execute("PRAGMA table_info(events)")]
    assert "scan_id" not in columns
