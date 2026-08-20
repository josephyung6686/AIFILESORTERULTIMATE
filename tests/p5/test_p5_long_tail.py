# tests/p5/test_p5_long_tail.py
"""E3's §2.9 half: six families, one shape, and SPEC Open questions 5 and 7 held
open."""
from pathlib import Path

import pytest

from database_agent.db import create_schema

from extractors.long_tail import (
    LONG_TAIL_SOURCE_TYPES, LongTailEntry, LongTailFile, LongTailText, LongTailValue,
    POTENTIALLY_SENSITIVE, UnauthorizedTranscription, DuplicateUnit,
    extract_long_tail, record_sensitivity_signals, sensitivity_signals_for,
)
from extractors.reading import StructuredString
from extractors.router import HANDLER_BY_SOURCE_TYPE
from extractors.safety import ProtectedContainerRefused, SafetyPolicy
from extractors.schema import create_extraction_schema
from extractors.structured_text import STRUCTURED_TEXT_SOURCE_TYPES

from conftest import FIXED_CLOCK
from p4_stub import locator_for, unit_locator_for

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
FILE_ROW = {"file_id": "f-lt", "content_hash": "751d1abc2d16b803289d9eb0ac7f8b7cf540c7c5f48fe9dca0b2f19260cfca74", "filename": "thing"}

NEVER = lambda: False
ALWAYS = lambda: True


def run_it(document, source_type, *, authorized=NEVER, finder=lambda text: ()):
    seen = {}

    def reader(path, *, transcribe):
        seen["transcribe"] = transcribe
        return document

    result = extract_long_tail(
        file_row=FILE_ROW, path=Path("/corpus/thing"), policy=OPEN_POLICY,
        source_type=source_type, read_long_tail=reader,
        find_structured_strings=finder, transcription_authorized=authorized,
        now=FIXED_CLOCK, context_window=20)
    return result, seen


def a_workbook() -> LongTailFile:
    return LongTailFile(
        entries=(LongTailEntry(kind="sheet", index=1, label="Applications"),),
        values=(LongTailValue(name="creator", value="Numbers"),),
        texts=(LongTailText(zone="table", text="Wash U", entry_ordinal=1, row=2,
                            column=1, column_header="Institution"),),
    )


def a_deck() -> LongTailFile:
    return LongTailFile(
        entries=(LongTailEntry(kind="slide", index=3, label=None),),
        texts=(LongTailText(zone="heading", text="Results", entry_ordinal=1, region=1),
               LongTailText(zone="body", text="Two cohorts.", entry_ordinal=1,
                            region=2),
               LongTailText(zone="notes", text="Mention the funding.",
                            entry_ordinal=1, region=3)),
    )


def an_email() -> LongTailFile:
    return LongTailFile(
        entries=(LongTailEntry(kind="entry", label="<msg-1@example.edu>"),),
        values=(LongTailValue(name="From", value="dean@wustl.edu",
                              entry_ordinal=1, kind="address"),
                LongTailValue(name="Subject", value="Your application",
                              entry_ordinal=1)),
        texts=(LongTailText(zone="body", text="Please send your transcript.",
                            entry_ordinal=1, region=1),),
    )


def a_video(*, with_speech: bool) -> LongTailFile:
    texts = [LongTailText(zone="transcript", text="[music]", region=1,
                          time_span={"start_ms": 0, "end_ms": 2000})]
    if with_speech:
        texts.append(LongTailText(zone="transcript", text="Welcome to the lecture.",
                                  region=2, from_speech=True,
                                  time_span={"start_ms": 2000, "end_ms": 6000}))
    return LongTailFile(values=(LongTailValue(name="duration", value="00:41:12"),),
                        texts=tuple(texts))


def find_lecture(text: str):
    at = text.find("lecture")
    return (StructuredString(kind="identifier", start=at, end=at + 7),) if at != -1 else ()


def test_the_two_halves_of_e3_partition_the_routers_set():
    routed = {name for name, handler in HANDLER_BY_SOURCE_TYPE.items()
              if handler == "text.structured"}
    assert set(STRUCTURED_TEXT_SOURCE_TYPES) | set(LONG_TAIL_SOURCE_TYPES) == routed
    assert not set(STRUCTURED_TEXT_SOURCE_TYPES) & set(LONG_TAIL_SOURCE_TYPES)


def test_every_family_conforms_to_p4s_shape(sink):
    for document, source_type in ((a_workbook(), "spreadsheet"),
                                  (a_deck(), "presentation"),
                                  (an_email(), "email"),
                                  (a_video(with_speech=False), "audio_video")):
        result, _ = run_it(document, source_type)
        sink.write(result.extraction)
    sink.conforms()


def test_a_spreadsheet_cell_locates_by_sheet_row_and_column(sink):
    result, _ = run_it(a_workbook(), "spreadsheet")
    run_id = sink.write(result.extraction)
    cell = [o for o in sink.observations_for(run_id) if o["raw_value"] == "Wash U"][0]
    assert locator_for(cell["location"]) == "table:sheet=1/row=2/column=1#0-6"
    header = cell["location"]["container_path"][-1]["label"]
    assert header == "Institution"


def test_a_slide_keeps_its_title_body_and_notes_as_three_zones(sink):
    result, _ = run_it(a_deck(), "presentation")
    run_id = sink.write(result.extraction)
    zones = {o["raw_value"]: o["location"]["zone"]
             for o in sink.observations_for(run_id)}
    assert zones["Results"] == "heading"
    assert zones["Mention the funding."] == "notes"
    # §2.9's "slide-level page boundaries" are the slide segment itself.
    assert all(o["location"]["container_path"][0] == {"kind": "slide", "index": 3,
                                                      "label": None}
               for o in sink.observations_for(run_id))


def test_a_slides_three_texts_are_three_units(sink):
    result, _ = run_it(a_deck(), "presentation")
    run_id = sink.write(result.extraction)
    paths = [unit_locator_for(u["container_path"]) for u in sink.units_for(run_id)]
    assert len(paths) == len(set(paths)) == 3
    assert set(paths) == {"slide=3/region=1", "slide=3/region=2", "slide=3/region=3"}


def test_two_texts_at_one_container_path_are_refused():
    # G1's key is (run_id, container_path); a collision would silently lose a unit.
    collide = LongTailFile(
        entries=(LongTailEntry(kind="slide", index=1),),
        texts=(LongTailText(zone="body", text="a", entry_ordinal=1),
               LongTailText(zone="notes", text="b", entry_ordinal=1)))
    with pytest.raises(DuplicateUnit):
        run_it(collide, "presentation")


def test_a_message_body_is_a_unit_and_not_an_observation(sink):
    # G1: "a page of text is not a located value". The same is true of a body.
    result, _ = run_it(an_email(), "email")
    run_id = sink.write(result.extraction)
    body = [u for u in sink.units_for(run_id)
            if u["text"] == "Please send your transcript."]
    assert len(body) == 1
    assert not [o for o in sink.observations_for(run_id)
                if o["raw_value"] == "Please send your transcript."]


def test_email_addresses_and_message_content_carry_the_sensitivity_signal(sink):
    result, _ = run_it(an_email(), "email",
                       finder=lambda text: ())
    run_id = sink.write(result.extraction)
    flagged = {result.extraction.observations[s.observation_index]["raw_value"]
               for s in result.sensitivity}
    assert flagged == {"dean@wustl.edu"}
    assert {s.signal for s in result.sensitivity} == {POTENTIALLY_SENSITIVE}
    # The subject is neither an address nor message content, so it carries nothing.
    assert "Your application" not in flagged


def test_every_vcf_value_carries_the_signal():
    card = LongTailFile(
        entries=(LongTailEntry(kind="entry", label="uid-1"),),
        values=(LongTailValue(name="FN", value="A. Dean", entry_ordinal=1),
                LongTailValue(name="TEL", value="+1-314-555-0100", entry_ordinal=1)))
    result, _ = run_it(card, "contacts")
    assert len(result.sensitivity) == len(result.extraction.observations) == 2


def test_p5_supplies_the_signal_and_assigns_no_class():
    # SPEC Open question 7 stays open: §8.4 puts handling-class assignment in P7.
    result, _ = run_it(an_email(), "email")
    assert all(s.signal == POTENTIALLY_SENSITIVE for s in result.sensitivity)
    assert all(not hasattr(s, "handling_class") for s in result.sensitivity)


def test_the_signal_is_stored_and_read_back(conn):
    create_schema(conn)
    create_extraction_schema(conn)
    result, _ = run_it(an_email(), "email")
    keys = [f"k{i}" for i in range(len(result.extraction.observations))]
    record_sensitivity_signals(conn, run_id="run-1", signals=result.sensitivity,
                               observation_keys=keys, now=FIXED_CLOCK)
    rows = sensitivity_signals_for(conn, "run-1")
    assert [r["signal"] for r in rows] == [POTENTIALLY_SENSITIVE]
    assert rows[0]["basis"]
    # keyed on P4's handle, which is what P7 redacts against and what survives a re-run
    assert rows[0]["observation_key"] in keys


def test_audio_stops_at_container_metadata_without_the_policy(sink):
    result, seen = run_it(a_video(with_speech=False), "audio_video",
                          authorized=NEVER)
    run_id = sink.write(result.extraction)
    assert seen["transcribe"] is False          # no recognition was even attempted
    assert [o["raw_value"] for o in sink.observations_for(run_id)] == ["00:41:12"]
    # Embedded captions are §2.9's unconditional half and are still extracted.
    assert [u["text"] for u in sink.units_for(run_id)] == ["[music]"]


def test_a_transcript_smuggled_past_the_policy_is_refused():
    with pytest.raises(UnauthorizedTranscription):
        run_it(a_video(with_speech=True), "audio_video", authorized=NEVER)


def test_an_authorized_transcript_locates_by_time_span(sink):
    result, seen = run_it(a_video(with_speech=True), "audio_video", authorized=ALWAYS,
                          finder=find_lecture)
    run_id = sink.write(result.extraction)
    assert seen["transcribe"] is True
    spoken = [o for o in sink.observations_for(run_id) if o["raw_value"] == "lecture"]
    assert spoken[0]["location"]["zone"] == "transcript"
    assert spoken[0]["location"]["time_span"] == {"start_ms": 2000, "end_ms": 6000}
    assert spoken[0]["location"]["text_span"] is None
    assert spoken[0]["context_before"]        # the offset still produced the context
    sink.conforms()


def test_a_spreadsheet_with_no_reader_is_unsupported(sink):
    # SPEC Open question 5: ship dedicated support, or ship `unsupported`. The
    # caller decides by supplying a reader or not; P5 decides nothing.
    result, _ = run_it(None, "spreadsheet")
    run_id = sink.write(result.extraction)
    assert sink.run_for(run_id)["completeness"] == "unsupported"
    assert sink.observations_for(run_id) == []
    assert result.sensitivity == ()


def test_no_extractor_is_reachable_inside_a_protected_container():
    policy = SafetyPolicy(is_protected_container=lambda path: True,
                          is_dataless=lambda path: False)
    with pytest.raises(ProtectedContainerRefused):
        extract_long_tail(
            file_row=FILE_ROW, path=Path("/Applications/Mail.app/Contents/a.eml"),
            policy=policy, source_type="email",
            read_long_tail=lambda path, *, transcribe: pytest.fail("reader reached"),
            find_structured_strings=lambda text: (),
            transcription_authorized=NEVER, now=FIXED_CLOCK, context_window=20)
