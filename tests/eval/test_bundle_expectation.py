# tests/eval/test_bundle_expectation.py
import sqlite3

import pytest

from eval_harness.bundle import (
    accepted_groups, add_accepted_group, add_expectation, expectation_for,
    expectations, open_bundle, seal_bundle,
)
from eval_harness.store import EVAL_TABLES, create_eval_schema
from eval_harness.vocabulary import DIMENSIONS, UnknownDimension


def _bundle(conn):
    return open_bundle(conn, corpus_form="snapshot", source_scan_ref="scan-fixture",
                       pinned_plan_id="plan-fixture", pinned_plan_version="1",
                       policy_settings={})


def test_an_accepted_group_is_stored_as_p9_resolved_it(eval_conn):
    # P9 owns the per-version resolution; P2 stores the row it is handed.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    row = {"group_id": "g-columbia", "plan_version": "1", "review_state": "accepted",
           "members": ["file-1", "file-2"]}
    add_accepted_group(eval_conn, bundle_id, group_id="g-columbia", acceptance_row=row)
    assert accepted_groups(eval_conn, bundle_id) == [row]


def test_every_dimension_can_carry_an_expectation(eval_conn):
    # Done-means 2: all ten have a distinct assertion record; none is collapsed.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    for dimension in DIMENSIONS:
        add_expectation(eval_conn, bundle_id, dimension=dimension,
                        subject_ref=f"subject-{dimension}",
                        expected_value={"fixture": dimension},
                        expected_outcome_kind="produced", source="hand-labelled")
    assert len({r["dimension"] for r in expectations(eval_conn, bundle_id)}) == 10


def test_a_dimension_outside_the_ten_is_rejected(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    with pytest.raises(UnknownDimension):
        add_expectation(eval_conn, bundle_id, dimension="candidate_node_retrieval",
                        subject_ref="x", expected_value={},
                        expected_outcome_kind="produced", source="hand-labelled")


def test_the_columbia_screenshot_is_representable(eval_conn):
    # Done-means 12 / §7.8's worked example: the correct outcome is retrieval of
    # the accepted Columbia application group and a RETURN TO PLACEMENT, not a
    # residual destination. The vocabulary is P11's; P2 stores it, validates none.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    add_expectation(
        eval_conn, bundle_id, dimension="residual", subject_ref="file-screenshot",
        expected_value={"outcome": "return_to_placement",
                        "return_target": {"kind": "confirmed_domain_group",
                                          "id": "g-columbia"}},
        expected_outcome_kind="produced", source="hand-labelled",
    )
    stored = expectation_for(eval_conn, bundle_id, "residual", "file-screenshot")
    assert stored["expected_value"]["outcome"] == "return_to_placement"
    assert stored["expected_value"]["return_target"]["kind"] == "confirmed_domain_group"


def test_all_eight_of_7_7s_actions_are_representable(eval_conn):
    # Done-means 12: "Dimension 10 can express all eight of §7.7's actions."
    # These strings are P11's published vocabulary, quoted in a test fixture, not
    # declared as a P2 enum in src/.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    eight = [
        {"outcome": "return_to_placement",
         "return_target": {"kind": "confirmed_domain_group"}},
        {"outcome": "return_to_placement",
         "return_target": {"kind": "accepted_graph_or_purpose_packet"}},
        {"outcome": "place", "destination": {"node_role": "residual"}},
        {"outcome": "place", "destination": {"node_role": "ordinary"},
         "decision_depth": {"unsupported_levels": ["term"]}},
        {"outcome": "mark_review_later"},
        {"outcome": "leave_in_place"},
        {"outcome": "mark_state", "marked_state": "protected"},
        {"outcome": "abstain", "abstention_reason": "no_supported_destination"},
    ]
    for i, value in enumerate(eight):
        add_expectation(eval_conn, bundle_id, dimension="residual",
                        subject_ref=f"file-{i}", expected_value=value,
                        expected_outcome_kind=(
                            "abstained" if value["outcome"] == "abstain" else "produced"),
                        source="hand-labelled")
    stored = expectations(eval_conn, bundle_id, dimension="residual")
    assert len(stored) == 8
    assert {r["expected_value"]["outcome"] for r in stored} == {
        "return_to_placement", "place", "mark_review_later", "leave_in_place",
        "mark_state", "abstain"}


def test_an_abstention_is_an_expectable_outcome(eval_conn):
    # §6.10: correct abstention is a successful outcome, so it must be expressible
    # as an EXPECTATION, not only as an observation.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    add_expectation(eval_conn, bundle_id, dimension="fact",
                    subject_ref="file-1::field-a", expected_value=None,
                    expected_outcome_kind="abstained", source="hand-labelled")
    assert expectation_for(eval_conn, bundle_id, "fact",
                           "file-1::field-a")["expected_outcome_kind"] == "abstained"


def test_expected_outcome_kind_and_source_are_closed(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    with pytest.raises(ValueError):
        add_expectation(eval_conn, bundle_id, dimension="fact", subject_ref="x",
                        expected_value={}, expected_outcome_kind="maybe",
                        source="hand-labelled")
    with pytest.raises(ValueError):
        add_expectation(eval_conn, bundle_id, dimension="fact", subject_ref="y",
                        expected_value={}, expected_outcome_kind="produced",
                        source="guessed")


def test_there_is_no_bulk_apply_path(eval_conn):
    # §8.7 scope discipline: a file-scoped correction is an expectation for that
    # file only. P2 must not generalise one into a dimension-wide expectation.
    import inspect

    from eval_harness import bundle as bundle_module
    for name, fn in inspect.getmembers(bundle_module, inspect.isfunction):
        if "expectation" in name:
            params = inspect.signature(fn).parameters
            assert "subject_refs" not in params, name
            assert "apply_to_all" not in params, name


def test_a_sealed_bundle_takes_no_further_expectation(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    seal_bundle(eval_conn, bundle_id)
    from eval_harness.bundle import BundleSealed
    with pytest.raises(BundleSealed):
        add_expectation(eval_conn, bundle_id, dimension="fact", subject_ref="x",
                        expected_value={}, expected_outcome_kind="produced",
                        source="hand-labelled")


def _placeholder_row(conn, table: str, bundle_id: str) -> None:
    """Insert one row into `table` using only the schema, no writer.

    Column types come from PRAGMA, so this works for a bundle table added later
    without being taught its shape — which is the point of the test below.
    """
    columns = list(conn.execute(f"PRAGMA table_info({table})"))
    values = [bundle_id if c["name"] == "bundle_id"
              else (0 if c["type"] == "INTEGER" else "x") for c in columns]
    conn.execute(
        f"INSERT INTO {table} ({', '.join(c['name'] for c in columns)}) "
        f"VALUES ({', '.join('?' * len(columns))})", values)


def test_every_bundle_table_is_sealed_against_all_three_writes(eval_conn):
    # Task 5's claim is that after `sealed_at` every INSERT, UPDATE and DELETE on
    # a CHILD ROW raises — not just on the two tables Task 5 itself created. The
    # Python writers all call `_require_open`, but a writer check is bypassed by
    # anything holding the connection, which is precisely what a replay adapter
    # and a shadow adapter are. This enumerates the tables rather than naming
    # them, so a bundle table added later without its three triggers fails here
    # instead of being immutable in the prose only.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    children = [t for t in EVAL_TABLES
                if t.startswith("bundle_") and t != "bundle_manifest"]
    # 8 since `bundle_recording` (§8.5's corpus snapshot and the recording's
    # name). The count is here so a table added without its three triggers
    # fails loudly rather than being enumerated silently past.
    assert len(children) == 8, children
    # One row each while the bundle is still open, so UPDATE and DELETE have
    # something to match — a trigger no statement reaches proves nothing.
    for table in children:
        _placeholder_row(eval_conn, table, bundle_id)
    seal_bundle(eval_conn, bundle_id)
    for table in children:
        have = {r["name"] for r in eval_conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'trigger' AND tbl_name = ?",
            (table,))}
        assert have == {f"{table}_sealed_no_insert", f"{table}_sealed_no_update",
                        f"{table}_sealed_no_delete"}, f"{table}: {sorted(have)}"
        with pytest.raises(sqlite3.IntegrityError):
            _placeholder_row(eval_conn, table, bundle_id)
        with pytest.raises(sqlite3.IntegrityError):
            eval_conn.execute(f"UPDATE {table} SET bundle_id = bundle_id "
                              f"WHERE bundle_id = ?", (bundle_id,))
        with pytest.raises(sqlite3.IntegrityError):
            eval_conn.execute(f"DELETE FROM {table} WHERE bundle_id = ?", (bundle_id,))
        # nothing got through
        assert eval_conn.execute(
            f"SELECT count(*) AS c FROM {table}").fetchone()["c"] == 1
