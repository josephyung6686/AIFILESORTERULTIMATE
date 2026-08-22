# tests/p6/test_p6_authorship.py
"""M8: the acting part authors, P1 writes. P6 authors two of §8.2's nineteen."""
import pytest

from database_agent.events import RESERVED_EVENT_TYPES, append_event

from facts.authorship import (
    AUTHORED_EVENT_TYPES, COMPONENT_VERSION, SUBSYSTEM, event_defaults,
)


def test_the_two_event_names_are_8_2s_own_and_carry_a_space():
    # Introspected from P1 on 2026-08-22: RESERVED_EVENT_TYPES contains
    # "fact creation" and "fact rejection". `fact_creation` raises
    # UnregisteredEventType at run time — the MINOR 2 `OCR`/`ocr` defect again.
    assert AUTHORED_EVENT_TYPES == ("fact creation", "fact rejection")
    for name in AUTHORED_EVENT_TYPES:
        assert " " in name
        assert "_" not in name


def test_both_names_are_already_reserved_so_p6_registers_nothing():
    # P1 Contract out §3, rule 4: registration is a spec-level act. Both names are
    # in P1's frozen table of nineteen; P6 declares neither.
    assert set(AUTHORED_EVENT_TYPES) <= set(RESERVED_EVENT_TYPES)
    assert len(RESERVED_EVENT_TYPES) == 19


def test_facts_publishes_no_registration_call():
    import facts.authorship as module
    assert not [n for n, v in vars(module).items()
                if callable(v) and n.lower().startswith("register")]


def test_p6_is_named_in_exactly_one_module_at_this_task():
    # The whole-package version of this is Task 25's. Here it is the two modules
    # that exist: authorship names P6, states names nobody.
    import facts.authorship as authorship
    import facts.states as states
    assert authorship.SUBSYSTEM == "P6"
    assert not hasattr(states, "SUBSYSTEM")


def test_event_defaults_fill_in_8_2s_authorship_fields():
    fields = event_defaults(event_type="fact creation", file_id="f1",
                            content_hash="sha256:abc", explanation='{"field": "subject"}')
    assert fields["subsystem"] == SUBSYSTEM
    assert fields["component_version"] == COMPONENT_VERSION
    assert fields["event_type"] == "fact creation"
    assert fields["file_id"] == "f1"
    assert fields["observed_at"]


def test_a_caller_supplied_observed_at_wins_so_a_replay_can_pin_the_clock():
    # §8.5 replays a run and compares it against a prior result; two readings of the
    # wall clock would be a false diff.
    fields = event_defaults(event_type="fact rejection", explanation="{}",
                            observed_at="2026-08-19T14:03:22+00:00")
    assert fields["observed_at"] == "2026-08-19T14:03:22+00:00"


def test_event_defaults_refuse_an_event_type_p6_does_not_author():
    # P3 authors `hashing` and `stat observation`; P5 authors `extraction` and `OCR`;
    # P12 authors the move events. P6 authors exactly two.
    for foreign in ("hashing", "extraction", "OCR", "planned move", "fact_creation"):
        with pytest.raises(ValueError):
            event_defaults(event_type=foreign, explanation="{}")


def test_event_defaults_refuse_to_name_another_subsystem():
    # M8: a `fact creation` event whose subsystem reads "P8" records that the model
    # harness wrote the fact table. P6 authors its facts; P8 proposes.
    with pytest.raises(ValueError):
        event_defaults(event_type="fact creation", subsystem="P8", explanation="{}")
    # Naming P6 explicitly is not an error — it is a no-op.
    assert event_defaults(event_type="fact creation", subsystem="P6",
                          explanation="{}")["subsystem"] == "P6"


def test_what_event_defaults_produces_is_accepted_by_p1s_live_writer(conn):
    # The contract is only real if P1 takes it. `events.file_id` carries no foreign
    # key, so this needs no `files` row, no observation and no extractor.
    event_id = append_event(conn, **event_defaults(
        event_type="fact creation", file_id="f1", content_hash="sha256:abc",
        explanation='{"field_key": "subject", "evidence_refs": ["sha256:deadbeef"]}'))
    row = conn.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
    assert row["event_type"] == "fact creation"
    assert row["subsystem"] == "P6"
    assert row["component_version"] == COMPONENT_VERSION
    assert row["explanation"]
