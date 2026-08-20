# tests/p4/test_p4_authorship.py
import pytest

from database_agent.events import EVENT_FIELDS, RESERVED_EVENT_TYPES, append_event

from evidence_shape.authorship import (
    EXTRACTION_EVENT, OCR_ANALYSIS_TIER, OCR_EVENT, RUN_EVENT_TYPES, UnauthoredEvent,
    check_author, event_defaults, run_event_type,
)


def test_the_two_run_events_are_8_2s_own_names():
    # MINOR 2 (05-minor-resolutions.md): "§8.2 spells it `OCR`." P1's writer
    # validates against that vocabulary, so a lowercase name fails at runtime.
    assert RUN_EVENT_TYPES == ("extraction", "OCR")
    assert EXTRACTION_EVENT == "extraction"
    assert OCR_EVENT == "OCR"


def test_both_run_events_are_reserved_8_2_names_so_p4_registers_nothing():
    # P1 Contract out §3, rule 4: registration is a spec-level act. Both names are
    # already in P1's frozen table; P4 declares neither.
    assert set(RUN_EVENT_TYPES) <= set(RESERVED_EVENT_TYPES)


def test_p4_publishes_no_registration_call_and_no_subsystem_of_its_own():
    # M8: the acting part authors; P1 writes; P4 supplies the writer and names nobody.
    import evidence_shape.authorship as module
    assert not [n for n, v in vars(module).items()
                if callable(v) and n.lower().startswith("register")]
    assert not [n for n in vars(module) if n == "SUBSYSTEM"]


def test_the_ocr_event_name_and_the_ocr_vocabulary_value_are_different_strings():
    # Same word, three vocabularies: §8.2's event name, I4's analysis tier, §2.9's
    # source-type family. P4 keeps each spelling as its owner spells it.
    assert OCR_EVENT == "OCR"
    assert OCR_ANALYSIS_TIER == "ocr"
    assert OCR_EVENT != OCR_ANALYSIS_TIER
    assert OCR_EVENT.lower() == OCR_ANALYSIS_TIER


def test_an_ocr_tier_run_appends_the_OCR_event_and_every_other_tier_appends_extraction():
    # SPEC, Cross-cutting answers -> Provenance: "`extraction`, or `OCR` when the
    # extractor is OCR". I4 makes "the extractor is OCR" the value `ocr`.
    assert run_event_type("ocr") == "OCR"
    assert run_event_type("native") == "extraction"
    assert run_event_type("filesystem") == "extraction"
    assert run_event_type("llm") == "extraction"


def test_the_caller_must_name_itself():
    assert check_author("P5") == "P5"
    with pytest.raises(UnauthoredEvent):
        check_author("")
    with pytest.raises(UnauthoredEvent):
        check_author(None)


def test_p1_may_never_be_named_as_the_author_of_an_extraction():
    # M8: "P1 appends no event on its own initiative." A log whose subsystem names
    # the storage substrate cannot reconstruct who read the document (§8.2).
    with pytest.raises(UnauthoredEvent):
        check_author("P1")


def test_event_defaults_fill_in_8_2s_authorship_fields():
    fields = event_defaults(author="P5", component_version="pdf.text/3.1.0",
                            event_type="extraction", file_id="f1",
                            content_hash="sha256:abc", explanation="{}")
    assert fields["subsystem"] == "P5"
    assert fields["component_version"] == "pdf.text/3.1.0"
    assert fields["event_type"] == "extraction"
    assert fields["file_id"] == "f1"
    assert fields["observed_at"]


def test_event_defaults_refuse_an_event_type_p4_supplies_no_writer_for():
    # P3 authors `hashing` and `stat observation`; P12 authors the move events.
    # P4 supplies a writer for exactly two.
    with pytest.raises(UnauthoredEvent):
        event_defaults(author="P5", component_version="v", event_type="hashing")


def test_event_defaults_refuse_a_field_outside_8_2s_eleven():
    # MINOR 1: §8.2 lists eleven event fields. P4 adds none.
    with pytest.raises(UnauthoredEvent):
        event_defaults(author="P5", component_version="v", event_type="extraction",
                       observation_key="sha256:deadbeef")
    assert len(EVENT_FIELDS) == 11


def test_what_event_defaults_produces_is_accepted_by_p1s_writer(conn):
    # The contract is only real if P1 takes it. `events.file_id` carries no foreign
    # key, so this needs no `files` row and no extractor.
    event_id = append_event(conn, **event_defaults(
        author="P5", component_version="ocr.apple_vision/2.4.1", event_type="OCR",
        file_id="f1", content_hash="sha256:abc", explanation='{"run_id": "r1"}'))
    row = conn.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
    assert row["event_type"] == "OCR"
    assert row["subsystem"] == "P5"
