# tests/p7/test_p7_authorship.py
"""P7's eight event types are P1's already, and P7's name is written once.

Two things are proved here and they pull in opposite directions. Registration is a
SPEC-level act, so this package must be unable to perform one: the eight names are
asserted present and nothing is added. Authorship is a run-time act, so this package
must perform it in exactly one place: `event_defaults` fills `subsystem` and refuses
to let a caller set it, because M8's "the acting part authors" is unmeetable from a
log where the author is a parameter anyone may set.
"""
import importlib

import pytest

from database_agent.events import (
    CORRECTION_FIELDS, EVENT_FIELDS, EVENT_TYPES, REGISTERED_EVENT_TYPES,
    RESERVED_EVENT_TYPES, MalformedEvent, UnregisteredEventType, append_event,
)

import privacy.authorship as authorship
from privacy.authorship import (
    CLASSIFICATION_ASSIGNED, CLASSIFICATION_SUPERSEDED, COMPONENT_VERSION,
    CONSENT_GRANTED, CONSENT_REQUESTED, CONSENT_REVOKED, MODEL_RELEASE,
    MODEL_RELEASE_DENIED, P7_EVENT_TYPES, POLICY_SET, SUBSYSTEM, event_defaults,
)

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"

#: A ninth name that looks exactly like one of P7's and is registered nowhere. It is
#: the shape of the mistake this test exists to catch: a later author needing an
#: event, inventing a plausible name, and discovering at run time that registration
#: is not something this package can do.
UNREGISTERED = "classification_downgraded"

#: P8's, registered in P1's table and not P7's to author.
ANOTHER_PARTS_EVENT = "model_call_issued"


def an_event(**over):
    fields = dict(event_type=CLASSIFICATION_ASSIGNED, observed_at=FIXED_CLOCK,
                  explanation='{"handling_class": "sensitive_personal"}')
    fields.update(over)
    return fields


# --- the eight names, and the fact that P7 did not add them ------------------

def test_the_eight_are_the_specs_eight_in_the_specs_order():
    # SPEC, Cross-cutting answers -> Provenance, in its own order: "Appends:
    # classification_assigned, classification_superseded (including user
    # reclassification), policy_set, consent_granted, consent_revoked,
    # model_release, model_release_denied, consent_requested."
    assert P7_EVENT_TYPES == (
        "classification_assigned", "classification_superseded", "policy_set",
        "consent_granted", "consent_revoked", "model_release",
        "model_release_denied", "consent_requested",
    )
    assert len(P7_EVENT_TYPES) == 8


def test_each_constant_names_its_own_string():
    assert (CLASSIFICATION_ASSIGNED, CLASSIFICATION_SUPERSEDED, POLICY_SET,
            CONSENT_GRANTED, CONSENT_REVOKED, MODEL_RELEASE, MODEL_RELEASE_DENIED,
            CONSENT_REQUESTED) == P7_EVENT_TYPES


def test_all_eight_are_already_registered_in_p1_with_no_base():
    # src/database_agent/events.py:43-51, under the comment "P7 SPEC, Cross-cutting
    # answers -> Provenance. Eight." P1 compiled them from this SPEC; P7 asserts.
    for name in P7_EVENT_TYPES:
        assert name in REGISTERED_EVENT_TYPES, name
        assert REGISTERED_EVENT_TYPES[name] is None, name


def test_none_of_the_eight_collides_with_the_reserved_names():
    # §8.2's list is reserved and may not be redefined by any part. P1 checks this at
    # IMPORT, so a collision is an ImportError; this asserts the property P1 checked.
    # The reserved table holds twenty, not nineteen: the owner (Joseph) approved `refused move` on
    # 2026-08-29 so P12 can record a move refused BEFORE it was attempted, which
    # `failed move` (a move attempted and broken) cannot say.
    # P7's eight are disjoint from it before and after, which is what this test
    # is for; the count is pinned so P7 cannot grow the table by accident.
    assert len(RESERVED_EVENT_TYPES) == 20
    assert set(P7_EVENT_TYPES).isdisjoint(RESERVED_EVENT_TYPES)


def test_importing_privacy_authorship_registers_nothing():
    # Registration is a spec-level act (P1 Contract out §3, rule 4) and there is no
    # run-time registration call. Reloading the module must not grow P1's table.
    before = len(EVENT_TYPES)
    importlib.reload(authorship)
    from database_agent.events import EVENT_TYPES as after_table
    # The claim is "reloading grew nothing", not a frozen size: P1 owns the table's
    # count and pins it in `tests/test_events.py`. A second copy here went stale the
    # day P11 registered its nine.
    assert len(after_table) == before
    assert not [n for n, v in vars(authorship).items()
                if callable(v) and n.lower().startswith("register")]


def test_p1s_registry_is_a_read_only_mapping_so_p7_could_not_add_one():
    with pytest.raises(TypeError):
        REGISTERED_EVENT_TYPES["classification_downgraded"] = None


# --- authorship: one place, and not a parameter -------------------------------

def test_subsystem_is_p7_and_event_defaults_always_stamps_it():
    assert SUBSYSTEM == "P7"
    for name in P7_EVENT_TYPES:
        assert event_defaults(**an_event(event_type=name))["subsystem"] == SUBSYSTEM


def test_a_caller_may_not_supply_or_override_the_subsystem():
    # M8: "The acting part authors; P1 writes." An author that is a parameter is not
    # an author. This is the check Task 21 counts on when it asserts there is exactly
    # one place in `privacy` where "P7" is written.
    with pytest.raises(MalformedEvent):
        event_defaults(**an_event(subsystem="P7"))
    with pytest.raises(MalformedEvent):
        event_defaults(**an_event(subsystem="P8"))


def test_component_version_defaults_and_a_caller_wins():
    assert event_defaults(**an_event())["component_version"] == COMPONENT_VERSION
    assert event_defaults(**an_event(component_version="9.9.9"))[
        "component_version"] == "9.9.9"


def test_observed_at_defaults_to_now_and_a_caller_supplied_value_wins():
    # §8.5's replay must be able to pin the clock; §8.2 requires "time of observation"
    # on every event, so it can never be absent.
    assert event_defaults(**an_event())["observed_at"] == FIXED_CLOCK
    fields = an_event()
    del fields["observed_at"]
    assert event_defaults(**fields)["observed_at"]


def test_event_defaults_writes_nothing(p7_conn):
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    event_defaults(**an_event())
    assert p7_conn.execute(
        "SELECT count(*) c FROM events").fetchone()["c"] == before
    assert "conn" not in event_defaults.__code__.co_varnames


# --- what the helper accepts, and what it refuses -----------------------------

def test_a_ninth_p7_looking_name_is_refused_here_and_at_p1s_writer(p7_conn):
    with pytest.raises(UnregisteredEventType):
        event_defaults(**an_event(event_type=UNREGISTERED))
    with pytest.raises(UnregisteredEventType):
        append_event(p7_conn, event_type=UNREGISTERED, subsystem=SUBSYSTEM,
                     component_version=COMPONENT_VERSION, observed_at=FIXED_CLOCK,
                     explanation="{}")


def test_another_parts_registered_name_is_refused_by_p7s_helper(p7_conn):
    # P8's event is valid at P1's writer and is not P7's to author. A helper that
    # stamped subsystem="P7" onto it would produce a true-looking row naming the
    # wrong actor.
    assert ANOTHER_PARTS_EVENT in EVENT_TYPES
    with pytest.raises(UnregisteredEventType):
        event_defaults(**an_event(event_type=ANOTHER_PARTS_EVENT))


def test_a_field_p1_has_no_column_for_is_refused():
    # The largest shape decision in this part: §8.4's audit record has thirteen
    # fields `events` has no column for. They go into `explanation` as canonical JSON
    # (Task 10), never into a field name P1 would reject.
    for absent in ("release_id", "audit_id", "policy_version", "outcome"):
        with pytest.raises(MalformedEvent):
            event_defaults(**an_event(**{absent: "x"}))


def test_every_one_of_8_2s_eleven_fields_passes_through():
    passable = [n for n in EVENT_FIELDS
                if n not in ("event_type", "subsystem", "component_version")]
    fields = an_event(**{n: "v" for n in passable if n != "observed_at"})
    defaults = event_defaults(**fields)
    for name in passable:
        assert name in defaults, name


def test_the_five_correction_fields_pass_through():
    # §8.7's columns ride beside §8.2's eleven on a user-action event. Task 16's
    # reclassify needs all five and this helper is its only writer path.
    defaults = event_defaults(**an_event(
        event_type=CLASSIFICATION_SUPERSEDED, correction_scope="file",
        correction_subject="file-1", polarity="reject", proposal_class="privacy",
        basis_key='{"file_id": "file-1"}'))
    for name in CORRECTION_FIELDS:
        assert name in defaults, name


def test_base_event_type_is_refused_because_all_eight_carry_no_base():
    # P1 stores it; P7 refuses it. None of the eight is a typed specialization of one
    # of §8.2's nineteen, so a caller supplying one asserts a relationship the
    # registration does not record.
    with pytest.raises(MalformedEvent):
        event_defaults(**an_event(base_event_type="extraction"))


# --- the round trip, against the real writer ----------------------------------

def test_p1_accepts_an_event_of_each_of_the_eight_types(p7_conn):
    for name in P7_EVENT_TYPES:
        append_event(p7_conn, **event_defaults(**an_event(event_type=name)))
    rows = p7_conn.execute(
        "SELECT event_type, subsystem, base_event_type FROM events "
        "ORDER BY event_id").fetchall()
    assert [r["event_type"] for r in rows] == list(P7_EVENT_TYPES)
    assert {r["subsystem"] for r in rows} == {SUBSYSTEM}
    assert {r["base_event_type"] for r in rows} == {None}


def test_p1_refuses_a_p7_event_with_an_empty_explanation(p7_conn):
    # §8.2's "structured explanation or evidence reference" is where §8.4's
    # consent-aware record lives. P1 rejects None and "", so a P7 event without one
    # is unwritable rather than merely discouraged.
    with pytest.raises(MalformedEvent):
        append_event(p7_conn, **event_defaults(**an_event(explanation="")))
