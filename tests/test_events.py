import sqlite3

import pytest

from database_agent.db import create_schema
from database_agent.events import CORRECTION_FIELDS, EVENT_FIELDS, append_event


def _minimal(**overrides):
    row = dict(
        event_type="discovery", file_id="f1", content_hash="abc",
        subsystem="P3", component_version="p3-fixture",
        observed_at="2026-08-19T00:00:00+00:00", explanation="fixture",
    )
    row.update(overrides)
    return row


def test_there_are_exactly_eleven_event_fields():
    # §8.2's event record, MINOR 1. The §8.7 columns are separate and do not count.
    assert len(EVENT_FIELDS) == 11
    assert not set(EVENT_FIELDS) & set(CORRECTION_FIELDS)


def test_event_carries_the_eleven_fields(conn):
    create_schema(conn)
    event_id = append_event(conn, **_minimal())
    row = conn.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
    for field in EVENT_FIELDS:
        assert field in row.keys()
    # "where applicable" fields legitimately empty (Done-means 7) ...
    assert row["old_path"] is None
    assert row["new_path"] is None
    assert row["prompt_fingerprint"] is None
    assert row["user_id"] is None
    # ... and every other field populated. component_version is not optional.
    for field in EVENT_FIELDS:
        if field in ("old_path", "new_path", "prompt_fingerprint", "user_id"):
            continue
        assert row[field] is not None, f"Done-means 7: {field} must be populated"


def test_update_against_events_fails(conn):
    create_schema(conn)
    append_event(conn, **_minimal())
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE events SET explanation = 'rewritten'")


def test_delete_against_events_fails(conn):
    create_schema(conn)
    append_event(conn, **_minimal())
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM events")


def test_a_correction_is_a_new_event_not_an_edit(conn):
    create_schema(conn)
    append_event(conn, **_minimal(explanation="first"))
    append_event(conn, **_minimal(explanation="corrected"))
    rows = conn.execute("SELECT explanation FROM events ORDER BY event_id").fetchall()
    assert [r["explanation"] for r in rows] == ["first", "corrected"]


from database_agent.events import (
    EVENT_TYPES, REGISTERED_EVENT_TYPES, RESERVED_EVENT_TYPES, UnregisteredEventType,
)


def test_the_nineteen_reserved_names_are_present():
    assert len(RESERVED_EVENT_TYPES) == 19
    for name in ("discovery", "stat observation", "hashing", "extraction", "OCR",
                 "undo", "external modification detection", "planned move"):
        assert name in RESERVED_EVENT_TYPES


def test_registered_names_never_shadow_a_reserved_name():
    # Rule 1: the nineteen may not be redefined, narrowed, or reused.
    assert not set(REGISTERED_EVENT_TYPES) & set(RESERVED_EVENT_TYPES)


def test_the_registered_table_matches_the_declaring_specs():
    # Rule 2: the declaration is the definition, and it lives in the authoring
    # part's SPEC. Counts are P1 SPEC Contract out §3's table.
    p7 = {"classification_assigned", "classification_superseded", "policy_set",
          "consent_granted", "consent_revoked", "model_release",
          "model_release_denied", "consent_requested"}
    p8 = {"model_call_issued", "model_response_received", "validation_verdict",
          "verdict_superseded", "call_refused"}
    p13 = {"review presentation", "review action routed", "apply review approval"}
    p11 = {"placement_index_entry_built", "candidate_destination_retrieval",
           "placement_recommendation_emitted", "group_plan_emitted",
           "residual_set_surfaced", "residual_set_decision_recorded",
           "residual_recommendation_emitted", "return_to_placement_issued",
           "placement_review_decision"}
    assert len(p7) == 8 and len(p8) == 5 and len(p13) == 3 and len(p11) == 9
    assert set(REGISTERED_EVENT_TYPES) == p7 | p8 | p13 | p11
    # 19 + 8 + 5 + 3 + 9.
    assert len(EVENT_TYPES) == 44


def test_the_table_cannot_be_mutated_at_run_time():
    # Rule 4: a part cannot mint a type at run time.
    with pytest.raises(TypeError):
        EVENT_TYPES["invented at runtime"] = None
    with pytest.raises(TypeError):
        REGISTERED_EVENT_TYPES["invented at runtime"] = None


def test_the_module_publishes_no_registration_call():
    # There is no run-time registration path at all — not a guarded one.
    import database_agent.events as events_module
    assert not [n for n, v in vars(events_module).items()
                if callable(v) and n.lower().startswith("register")]


def test_writer_accepts_a_type_declared_by_another_part(conn):
    # Done-means 11's fixture: P13's `apply review approval`, accepted with no
    # registration call because the declaration is in P13's SPEC.
    create_schema(conn)
    event_id = append_event(conn, **_minimal(event_type="apply review approval",
                                             subsystem="P13", user_id="u1"))
    assert event_id


def test_writer_rejects_an_undeclared_type(conn):
    create_schema(conn)
    with pytest.raises(UnregisteredEventType):
        append_event(conn, **_minimal(event_type="invented at runtime"))


def test_a_specialization_stores_its_reserved_base_type(conn):
    # The mechanism, driven off the frozen table rather than a name typed here.
    create_schema(conn)
    specializations = [(n, b) for n, b in EVENT_TYPES.items() if b is not None]
    for name, base in specializations:
        event_id = append_event(conn, **_minimal(event_type=name, subsystem="P11"))
        row = conn.execute("SELECT * FROM events WHERE event_id = ?",
                           (event_id,)).fetchone()
        assert row["base_event_type"] == base


def test_p11s_nine_specializations_are_registered_under_one_base():
    # The gap this replaces was P1's standing record that P11 had published no
    # identifiers. It is closed by P11 printing them, not by P1 inventing one.
    p11 = {n for n, b in EVENT_TYPES.items() if b == "placement recommendation"}
    assert p11 == {
        "placement_index_entry_built",
        "candidate_destination_retrieval",
        "placement_recommendation_emitted",
        "group_plan_emitted",
        "residual_set_surfaced",
        "residual_set_decision_recorded",
        "residual_recommendation_emitted",
        "return_to_placement_issued",
        "placement_review_decision",
    }
    assert len(p11) == 9


def test_a_surfaced_residual_set_is_a_different_event_from_a_decided_one(conn):
    # §7.6 gates model spend on a set decision, so a set that was shown and never
    # decided must be distinguishable from one that was decided. A shared name
    # could not say which happened.
    create_schema(conn)
    for name in ("residual_set_surfaced", "residual_set_decision_recorded"):
        append_event(conn, **_minimal(event_type=name, subsystem="P11"))
    rows = conn.execute(
        "SELECT event_type, base_event_type FROM events ORDER BY event_id"
    ).fetchall()
    assert [r["event_type"] for r in rows] == [
        "residual_set_surfaced", "residual_set_decision_recorded",
    ]
    assert {r["base_event_type"] for r in rows} == {"placement recommendation"}


def test_p11_registers_no_name_that_shadows_a_reserved_one():
    p11 = {n for n, b in EVENT_TYPES.items() if b == "placement recommendation"}
    assert not p11 & RESERVED_EVENT_TYPES


def test_two_parts_may_author_the_same_reserved_type(conn):
    # M8: external modification detection has two authors, separable by subsystem.
    create_schema(conn)
    append_event(conn, **_minimal(event_type="external modification detection", subsystem="P12"))
    append_event(conn, **_minimal(event_type="external modification detection", subsystem="P3"))
    rows = conn.execute(
        "SELECT subsystem FROM events WHERE event_type = 'external modification detection'"
    ).fetchall()
    assert sorted(r["subsystem"] for r in rows) == ["P12", "P3"]
