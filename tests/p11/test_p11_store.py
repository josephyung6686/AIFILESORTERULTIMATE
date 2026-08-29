"""Append-only decisions: the old row stays readable and the chain runs both ways."""
from __future__ import annotations

import pytest

from placement import vocabulary as v
from placement.records import (
    Alternative, ConflictConsidered, DECISION_FIELDS, GraphAnchor, GroupSupport,
    PrivacyState,
)
from placement.schema import P11_TABLES
from placement.store import (
    AmbiguousCurrentDecision, PROJECTION_COLUMNS, current_decision,
    decision_history, decisions_for_plan, record_decision, subject_ref_of,
)
from p11.conftest import FIXED_CLOCK
from p11.test_p11_records import _decision

#: One minimal row per table `record_decision` does not write, so the delete guard
#: is proved by FIRING it rather than by reading the DDL back. A `BEFORE DELETE`
#: trigger on an empty table never runs, and a `pytest.raises` around a no-op
#: delete asserts nothing at all.
#:
#: `residual_sets` and `residual_set_decisions` DO have production writers now
#: (`residual.surface_residual_sets` and `residual.record_set_decision`); the
#: direct seed stays because this test is about the trigger, not the writer, and
#: standing up a whole §7.5 surfacing to delete one row would test the surfacing.
#: `placement_index_entries`, `placement_index_terms`,
#: `placement_index_term_counts` and `placement_group_plans` have no writer whose
#: absence this test could stand in for -- `index.py` writes the first three
#: together, and this seeds them separately for the same reason as the rest: the
#: subject is the trigger, not the writer.
_SEED: dict[str, tuple[str, tuple]] = {
    "placement_index_entries":
        ("(record_id, plan_version, node_id, payload, created_at) "
         "VALUES (?, ?, ?, ?, ?)",
         ("i1", "plan-1", "n1", "{}", FIXED_CLOCK)),
    "placement_index_terms":
        ("(record_id, plan_version, node_id, source_field, term_key, term_value, "
         "ordinal, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
         ("t1", "plan-1", "n1", "expected_values", "subject", "PHYS1401", 0,
          FIXED_CLOCK)),
    "placement_index_term_counts":
        ("(record_id, plan_version, source_field, term_key, row_count, "
         "created_at) VALUES (?, ?, ?, ?, ?, ?)",
         ("tc1", "plan-1", "expected_values", "subject", 1, FIXED_CLOCK)),
    "placement_group_plans":
        ("(record_id, plan_version, group_id, payload, created_at) "
         "VALUES (?, ?, ?, ?, ?)",
         ("gp1", "plan-1", "g1", "{}", FIXED_CLOCK)),
    "residual_sets":
        ("(record_id, plan_version, label, payload, created_at) "
         "VALUES (?, ?, ?, ?, ?)",
         ("s1", "plan-1", "Unsorted", "{}", FIXED_CLOCK)),
    "residual_set_decisions":
        ("(record_id, plan_version, set_id, choice, decided_at, payload) "
         "VALUES (?, ?, ?, ?, ?, ?)",
         ("sd1", "plan-1", "s1", v.LEAVE_IN_PLACE, FIXED_CLOCK, "{}")),
}


def _write(conn, decision, **overrides):
    values = dict(component_version="P11-test", observed_at=FIXED_CLOCK)
    values.update(overrides)
    return record_decision(conn, decision, **values)


def test_every_record_field_survives_the_round_trip(p11_conn):
    # The invariant is that no field is silently unstored, and `payload` is the
    # record's ONE home -- so the proof is a round trip through the store, not a
    # column count. A field added to `PlacementDecision` reaches the payload
    # through `dataclasses.asdict` and comes back through `DECISION_FIELDS`; one
    # that did not would fail here on the first read.
    original = _decision(
        decision_id="d1", group_plan_id="gp1",
        group_support=GroupSupport(group_id="g1", membership="context-supported"),
        graph_anchors=(GraphAnchor(edge_type="same_course", from_file_id="f1",
                                   to_file_id="f2", anchor_file_id="f2"),),
        conflicts_considered=(ConflictConsidered(
            kind="subject", conflicting_value="PHYS1402",
            suppressed_node_ids=("n2",), evidence_ref="obs-2"),),
        alternatives=(Alternative(node_id="n2", support_score=0.4, rank=1),),
        review_policy=v.REVIEW_REQUIRED,
        privacy=PrivacyState(handling_class="personal_non_sensitive", protected=False,
                             model_eligibility=v.LOCAL_ONLY, consent_audit_ref=7))
    _write(p11_conn, original)
    restored = current_decision(p11_conn, plan_version="plan-1",
                                subject_ref=subject_ref_of(original.subject))
    for name in DECISION_FIELDS:
        assert getattr(restored, name) == getattr(original, name), name
    assert restored == original


def test_no_named_column_is_a_second_home_for_a_value(p11_conn):
    # A column beside `payload` is either an address the reads need or a field of
    # the record. A third concept there would be a value with no home in the
    # record and no writer that could keep it true.
    columns = {row["name"] for row in
               p11_conn.execute("PRAGMA table_info(placement_decisions)")}
    assert set(PROJECTION_COLUMNS) <= columns
    assert {"record_id", "subject_ref", "payload"} <= columns
    derived = {"record_id", "subject_ref", "node_id"}
    assert set(PROJECTION_COLUMNS) - derived <= set(DECISION_FIELDS)


def test_a_revision_appends_and_the_prior_row_stays_readable(p11_conn):
    first = _decision(decision_id="d1")
    _write(p11_conn, first)
    second = _decision(decision_id="d2", supersedes="d1",
                       outcome=v.ABSTAIN, destination=None,
                       abstention_reason=v.CONFLICTING_FACTS)
    _write(p11_conn, second, supersede_reason="a direct term fact arrived")

    history = decision_history(p11_conn, subject_ref=subject_ref_of(first.subject))
    assert [d.decision_id for d in history] == ["d1", "d2"]
    assert history[0].outcome == v.PLACE
    assert history[0].superseded_by == "d2"
    assert history[0].supersede_reason == "a direct term fact arrived"
    assert history[1].supersedes == "d1"
    assert current_decision(
        p11_conn, plan_version="plan-1",
        subject_ref=subject_ref_of(first.subject)).decision_id == "d2"


def test_the_chain_is_followable_forward(p11_conn):
    # §8.8's diff walks FROM a superseded decision TO its replacement, which
    # `supersedes` alone cannot express (M1).
    _write(p11_conn, _decision(decision_id="d1"))
    _write(p11_conn, _decision(decision_id="d2", supersedes="d1"),
           supersede_reason="plan version 2 removed the node")
    row = p11_conn.execute(
        "SELECT superseded_by, supersede_reason FROM placement_decisions "
        "WHERE record_id = ?", ("d1",)).fetchone()
    assert row["superseded_by"] == "d2"
    assert row["supersede_reason"] == "plan version 2 removed the node"


def test_a_stored_decision_cannot_be_updated_or_deleted(p11_conn):
    _write(p11_conn, _decision(decision_id="d1"))
    for statement, params in (
        ("UPDATE placement_decisions SET outcome = ? WHERE record_id = ?",
         (v.ABSTAIN, "d1")),
        ("UPDATE placement_decisions SET payload = ? WHERE record_id = ?",
         ("{}", "d1")),
        ("DELETE FROM placement_decisions WHERE record_id = ?", ("d1",)),
    ):
        with pytest.raises(Exception):
            p11_conn.execute(statement, params)


def test_supersession_columns_are_the_only_mutable_thing(p11_conn):
    # `mark_superseded` writes them, so the append-only trigger must permit that
    # exact update and nothing else.
    _write(p11_conn, _decision(decision_id="d1"))
    _write(p11_conn, _decision(decision_id="d2", supersedes="d1"),
           supersede_reason="corrected")
    assert current_decision(p11_conn, plan_version="plan-1",
                            subject_ref="file:f1:h1").decision_id == "d2"


def test_a_second_current_row_for_one_subject_cannot_commit(p11_conn):
    _write(p11_conn, _decision(decision_id="d1"))
    with pytest.raises(Exception):
        p11_conn.execute(
            "INSERT INTO placement_decisions (record_id, subject_ref, plan_version, "
            "outcome, origin_stage, created_at, payload) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("illegal", "file:f1:h1", "plan-1", v.PLACE, v.PLACEMENT,
             FIXED_CLOCK, "{}"))


def test_an_ambiguous_prior_state_is_refused_before_any_write(p11_conn):
    _write(p11_conn, _decision(decision_id="d1"))
    p11_conn.execute("DROP INDEX one_current_placement_decision")
    p11_conn.execute(
        "INSERT INTO placement_decisions (record_id, subject_ref, plan_version, "
        "outcome, origin_stage, created_at, payload) VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("d-bad", "file:f1:h1", "plan-1", v.PLACE, v.PLACEMENT, FIXED_CLOCK, "{}"))
    with pytest.raises(AmbiguousCurrentDecision):
        _write(p11_conn, _decision(decision_id="d3", supersedes="d1"),
               supersede_reason="repair attempt")
    assert p11_conn.execute(
        "SELECT COUNT(*) AS n FROM placement_decisions WHERE record_id = ?",
        ("d3",)).fetchone()["n"] == 0


def test_the_write_and_its_supersede_commit_together(p11_conn):
    # ONE transaction, proved by making the INSERT fail AFTER `mark_superseded`
    # has already written both halves. A supersede that committed without its
    # replacement leaves the subject with no current decision at all, which is
    # worse than either half failing: `current_decision` would return None for a
    # file the user has already reviewed.
    _write(p11_conn, _decision(decision_id="d1"))
    _write(p11_conn, _decision(decision_id="d2", plan_version="plan-2"))
    before = p11_conn.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"]

    with pytest.raises(Exception):
        # `mark_superseded` succeeds -- `d1` is live and `d2` exists and is
        # unsuperseded -- and then the INSERT collides with `d2`'s primary key.
        _write(p11_conn, _decision(decision_id="d2", supersedes="d1"),
               supersede_reason="a revision that cannot be stored")

    assert p11_conn.execute(
        "SELECT superseded_by FROM placement_decisions WHERE record_id = ?",
        ("d1",)).fetchone()["superseded_by"] is None
    assert p11_conn.execute(
        "SELECT supersedes FROM placement_decisions WHERE record_id = ?",
        ("d2",)).fetchone()["supersedes"] is None
    assert p11_conn.execute(
        "SELECT COUNT(*) AS n FROM events").fetchone()["n"] == before
    assert current_decision(p11_conn, plan_version="plan-1",
                            subject_ref="file:f1:h1").decision_id == "d1"


def test_writing_a_decision_appends_its_event(p11_conn):
    _write(p11_conn, _decision(decision_id="d1"))
    row = p11_conn.execute(
        "SELECT event_type, base_event_type, subsystem, file_id, content_hash, "
        "explanation FROM events ORDER BY event_id DESC LIMIT 1").fetchone()
    assert row["event_type"] == v.RECOMMENDATION_EMITTED
    assert row["base_event_type"] == "placement recommendation"
    assert row["subsystem"] == "P11"
    assert row["file_id"] == "f1"
    assert row["content_hash"] == "h1"
    assert "PHYS1401" in row["explanation"]


def test_an_abstention_is_logged_as_a_decision_not_as_silence(p11_conn):
    # SPEC:686: "any `outcome`, including `abstain` -- an abstention is a decision
    # and is logged as one".
    _write(p11_conn, _decision(decision_id="d1", outcome=v.ABSTAIN,
                               destination=None,
                               abstention_reason=v.NO_SUPPORTED_DESTINATION))
    row = p11_conn.execute(
        "SELECT event_type FROM events ORDER BY event_id DESC LIMIT 1").fetchone()
    assert row["event_type"] == v.RECOMMENDATION_EMITTED


def test_decisions_are_scoped_to_a_plan_version(p11_conn):
    _write(p11_conn, _decision(decision_id="d1", plan_version="plan-1"))
    _write(p11_conn, _decision(decision_id="d2", plan_version="plan-2"))
    assert {d.decision_id for d in decisions_for_plan(p11_conn, plan_version="plan-1")} == {"d1"}
    assert {d.decision_id for d in decisions_for_plan(p11_conn, plan_version="plan-2")} == {"d2"}


def test_every_p11_table_refuses_a_delete(p11_conn):
    _write(p11_conn, _decision(decision_id="d1"))
    for table, (columns, params) in _SEED.items():
        p11_conn.execute(f"INSERT INTO {table} {columns}", params)
    for table in P11_TABLES:
        assert p11_conn.execute(
            f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"] > 0
        with pytest.raises(Exception):
            p11_conn.execute(f"DELETE FROM {table}")
