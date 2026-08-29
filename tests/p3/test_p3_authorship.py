# tests/p3/test_p3_authorship.py
import pytest

from database_agent.events import RESERVED_EVENT_TYPES

from scan_agent.authorship import (
    AUTHORED_EVENT_TYPES, COMPONENT_VERSION, SUBSYSTEM, event_defaults,
)


def test_p3_names_itself_as_the_author():
    # M8: the acting part authors; P1 writes. There is one value and no default.
    assert SUBSYSTEM == "P3"


def test_p3_authors_exactly_the_four_types_its_spec_names():
    # SPEC Cross-cutting answers -> Provenance: discovery, stat observation,
    # scan-time hashing, external modification detection. No fifth.
    assert AUTHORED_EVENT_TYPES == (
        "discovery",
        "stat observation",
        "hashing",
        "external modification detection",
    )


def test_every_type_p3_authors_is_one_of_8_2s_reserved_nineteen():
    # B5: "P3 registers no new event type." All four are reserved §8.2 names, so
    # P1's frozen table already holds them and P3 declares nothing.
    assert set(AUTHORED_EVENT_TYPES) <= set(RESERVED_EVENT_TYPES)


def test_p3_publishes_no_registration_call():
    # Registration is a spec-level act (P1 Contract out §3, rule 4). P3 mints nothing.
    import scan_agent.authorship as module
    assert not [name for name, value in vars(module).items()
                if callable(value) and name.lower().startswith("register")]


def test_event_defaults_fill_in_8_2s_authorship_fields():
    fields = event_defaults(event_type="discovery", file_id="f1", content_hash="abc")
    assert fields["subsystem"] == "P3"
    assert fields["component_version"] == COMPONENT_VERSION
    assert fields["observed_at"]
    assert fields["event_type"] == "discovery"
    assert fields["file_id"] == "f1"


def test_event_defaults_refuse_a_type_p3_does_not_author():
    # Two authors share `external modification detection` (M8); nothing else is
    # shared. P3 must not put its name on P5's `extraction` or P12's `executed move`.
    with pytest.raises(ValueError):
        event_defaults(event_type="extraction", file_id="f1")


def test_event_defaults_cannot_be_told_to_name_another_subsystem():
    with pytest.raises(ValueError):
        event_defaults(event_type="discovery", file_id="f1", subsystem="P1")
