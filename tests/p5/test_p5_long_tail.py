# tests/p5/test_p5_long_tail.py
"""E3's §2.9 half: six families, one shape, and SPEC Open questions 5 and 7 held
open."""
from pathlib import Path

import pytest

from database_agent.db import create_schema

from extractors.long_tail import (
    LONG_TAIL_SOURCE_TYPES, LongTailEntry, LongTailFile, LongTailResult, LongTailText,
    LongTailValue, POTENTIALLY_SENSITIVE, SensitivitySignal,
    UnauthorizedTranscription, DuplicateUnit,
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


def a_roster() -> LongTailFile:
    """A header row and one data row, as the reader reports them: cell by cell."""
    header = ("Institution", "Award", "Term")
    data = ("Wash U", "Dean's List", "Spring 2026")
    return LongTailFile(
        entries=(LongTailEntry(kind="sheet", index=1, label="Applications"),),
        texts=tuple(LongTailText(zone="table", text=value, entry_ordinal=1,
                                 row=1, column=n, column_header=value)
                    for n, value in enumerate(header, 1))
        + tuple(LongTailText(zone="table", text=value, entry_ordinal=1,
                             row=2, column=n, column_header=header[n - 1])
                for n, value in enumerate(data, 1)),
        cells_total=6)


def test_a_spreadsheet_locates_by_sheet_and_row_and_its_unit_is_the_whole_row(sink):
    """A SPREADSHEET'S UNIT IS A ROW (13 Sep 2026, the owner's corpus).

    SABOTAGE: put the `column` segment back in `_text_path`, or drop the
    `_rows_from_cells` fold at `extract_long_tail`. Either restores the reading
    measured on the corpus -- a dataset file reaching the cloud situation judge as
    twelve to fourteen released readings of 5 to 30 characters, which the judge
    described in its own words as *"only a table header row of column names"*.

    The three claims together are the whole change. ONE UNIT PER ROW, so a roster
    of two rows is two units and not six. THE ROW'S OWN CELLS, joined in column
    order by a tab, so the unit is a line a person would read. AND NO COLUMN IN
    THE ADDRESS, because a row is what is being addressed -- `docx.py` still
    writes `table=T/row=R/column=C` for a table cell and is a different extractor.
    """
    result, _ = run_it(a_roster(), "spreadsheet")
    run_id = sink.write(result.extraction)

    units = {unit_locator_for(u["container_path"]): u["text"]
             for u in sink.units_for(run_id)}
    assert units == {"sheet=1/row=1": "Institution\tAward\tTerm",
                     "sheet=1/row=2": "Wash U\tDean's List\tSpring 2026"}, (
        "one unit per row, cells joined in column order; a cell of its own is the "
        "reading the situation judge could not read")

    table = [o for o in sink.observations_for(run_id)
             if o["location"]["zone"] == "table"]
    assert [locator_for(o["location"]) for o in table] == [
        "table:sheet=1/row=1#0-22", "table:sheet=1/row=2#0-30"], (
        "the row observation spans its whole unit and carries no column segment")
    assert not any(s["kind"] == "column" for o in table
                   for s in o["location"]["container_path"])


def test_the_cells_go_away_rather_than_sit_beside_the_rows(sink):
    """Two readings over the same characters would double-count the file.

    SABOTAGE: emit the cells as well as the rows. Every count that reads
    `evidence` -- the release, the recogniser, the scoreboard -- then sees a
    six-cell roster twice, once as six readings and once as two.
    """
    result, _ = run_it(a_roster(), "spreadsheet")
    run_id = sink.write(result.extraction)
    values = [o["raw_value"] for o in sink.observations_for(run_id)
              if o["location"]["zone"] == "table"]
    assert values == ["Institution\tAward\tTerm", "Wash U\tDean's List\tSpring 2026"]
    assert "Institution" not in values


def test_the_cell_coverage_still_counts_cells_and_not_rows(sink):
    """A fold is not a read. The reader's ceiling is a CELL ceiling and
    `cells_total` is a count of cells, so counting the emitted rows would report
    two of six cells read on a file where every cell was read -- and §8.6's
    unfinished-work count is computed off exactly this column."""
    result, _ = run_it(a_roster(), "spreadsheet")
    assert result.extraction.run["coverage"] == {
        "units": "cells", "processed": 6, "total": 6}
    assert result.extraction.run["completeness"] == "complete"


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


def test_a_slides_body_is_a_unit_AND_a_whole_unit_observation(sink):
    """`104` §18.2 gap 17, loss (b), on the presentation half.

    `test_a_slide_keeps_its_title_body_and_notes_as_three_zones` above reads its
    zones out of the observations, and the body was never in that dictionary -- the
    test's own name says three zones and it could only ever check two. §2.9 asks a
    presentation for "slide titles, TEXT BOXES, speaker notes", and a deck's text
    boxes are where the argument of the deck lives; the title and the notes reached
    the recogniser and the slide itself did not.

    SABOTAGE: delete the `else` arm in `extract_long_tail`'s text loop.
    """
    result, _ = run_it(a_deck(), "presentation")
    run_id = sink.write(result.extraction)
    zones = {o["raw_value"]: o["location"]["zone"]
             for o in sink.observations_for(run_id)}
    assert zones["Two cohorts."] == "body", zones
    body = [o for o in sink.observations_for(run_id)
            if o["raw_value"] == "Two cohorts."][0]
    assert body["location"]["text_span"] is None
    assert "#" not in locator_for(body["location"])
    # The unit stands at exactly the path the reading names (P4 rule 10), so §8.6's
    # ceiling can measure this reading and SF-1's "whole document" arm can bound it.
    units = {unit_locator_for(u["container_path"]): u["text"]
             for u in sink.units_for(run_id)}
    assert units[locator_for(body["location"]).split(":", 1)[1]] == "Two cohorts."


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


def test_a_message_body_is_a_unit_AND_a_whole_unit_observation(sink):
    """`104` §18.2 gap 17, loss (b). THIS TEST USED TO ASSERT THE DEFECT.

    It was `test_a_message_body_is_a_unit_and_not_an_observation` and its reason was
    G1's "a page of text is not a located value" -- which says a body carries no
    SPAN, and was read here as though it said a body carries no ROW. The difference
    is everything: `recognition/detector.py` scans observations only, deliberately
    ("a detector that pulled whole text units would be a second materialisation
    locus"), so with no row the entire body of every `.eml` and every `.pptx` on a
    disk was extracted, stored, and read by nothing. E1, E2, E3 and E6 all emit the
    span-less whole-unit observation this asserted must not exist.

    SABOTAGE: delete the `else` arm in `extract_long_tail`'s text loop, or move
    `body` into `WHOLE_TEXT_ZONES` -- the first takes the row away again, the second
    gives it a span, and the span assertion below is what catches the second.
    """
    result, _ = run_it(an_email(), "email")
    run_id = sink.write(result.extraction)
    body = [u for u in sink.units_for(run_id)
            if u["text"] == "Please send your transcript."]
    assert len(body) == 1
    rows = [o for o in sink.observations_for(run_id)
            if o["raw_value"] == "Please send your transcript."]
    assert len(rows) == 1, "the message body reaches the evidence table"
    assert rows[0]["location"]["zone"] == "body"
    # NO SPAN, and no `#` in the locator with it. A `body#0-27` locator is the space
    # the shipped deployment's direct slot claims, so a span here would let a whole
    # message become a `subject` fact -- which is to say a folder name.
    assert rows[0]["location"]["text_span"] is None
    assert "#" not in locator_for(rows[0]["location"])
    # P4 rule 10: the unit stands at exactly the path the reading names, so
    # `store.unit_length_for_observation` can measure the reading against it and
    # §8.6's ceiling can bound it (SF-1). Compared as strings rather than spelled,
    # because the locator's escaping is P4's and not this test's business.
    assert (locator_for(rows[0]["location"])
            == "body:" + unit_locator_for(body[0]["container_path"]))


def test_email_addresses_and_message_content_carry_the_sensitivity_signal(sink):
    """`104` §18.2 gap 17, loss (b), read through §2.9's privacy clause.

    The title always said "and message content", and until the body had a row there
    was nothing for that half of the sentence to land on -- §2.9 asks for email to be
    handled "while treating addresses and message content as potentially sensitive",
    and only the addresses were flagged because only the addresses were observed.

    SABOTAGE: drop `sensitive_basis=body_basis` from the `else` arm and the body
    arrives as an unflagged row, which is worse than the row not existing: P7
    redacts against the signal, so an unflagged message body is one that has been
    made reachable without being made handleable.
    """
    result, _ = run_it(an_email(), "email",
                       finder=lambda text: ())
    run_id = sink.write(result.extraction)
    flagged = {result.extraction.observations[s.observation_index]["raw_value"]
               for s in result.sensitivity}
    assert flagged == {"dean@wustl.edu", "Please send your transcript."}
    assert {s.signal for s in result.sensitivity} == {POTENTIALLY_SENSITIVE}
    bases = {result.extraction.observations[s.observation_index]["raw_value"]: s.basis
             for s in result.sensitivity}
    assert "message content" in bases["Please send your transcript."]
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
    # TWO ROWS SINCE `104` §18.2 gap 17: the From address and the message body. It
    # was one because the body had no observation to hang a signal on.
    assert [r["signal"] for r in rows] == [POTENTIALLY_SENSITIVE] * 2
    assert all(r["basis"] for r in rows)
    # keyed on P4's handle, which is what P7 redacts against and what survives a re-run
    assert rows[0]["observation_key"] in keys


def test_audio_stops_at_container_metadata_without_the_policy(sink):
    """B6 and NEEDS JOSEPH 7: no speech-to-text without P7's explicit policy.

    THE CAPTION IS NOW EVIDENCE AND THE TRANSCRIPT STILL IS NOT, and that is the
    distinction `104` §18.2 gap 17 restores rather than erases. §2.9 asks audio and
    video for "subtitles or captions where present" UNCONDITIONALLY and gates only
    the speech-to-text transcript, so an embedded caption track had a unit, no row,
    and no reader -- the same silent loss as the message body. What the policy gates
    is `from_speech`, which `UnauthorizedTranscription` still refuses outright, and
    `test_speech_to_text_without_the_policy_is_refused` is that guard.

    SABOTAGE: make the `else` arm skip `time_span` -- a caption addressed by a text
    offset it does not have is a citation into the wrong medium (P4 publishes
    `text_span` and `time_span` as alternatives, and §2.8's own audio example is a
    time).
    """
    result, seen = run_it(a_video(with_speech=False), "audio_video",
                          authorized=NEVER)
    run_id = sink.write(result.extraction)
    assert seen["transcribe"] is False          # no recognition was even attempted
    assert [o["raw_value"] for o in sink.observations_for(run_id)] == ["00:41:12",
                                                                      "[music]"]
    # Embedded captions are §2.9's unconditional half and are still extracted.
    assert [u["text"] for u in sink.units_for(run_id)] == ["[music]"]
    caption = [o for o in sink.observations_for(run_id)
               if o["raw_value"] == "[music]"][0]
    assert caption["location"]["time_span"] == {"start_ms": 0, "end_ms": 2000}
    assert caption["location"]["text_span"] is None


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


# --------------------------------------------------- D10 renumbers; the signal follows
def a_repeated_address(*slots: str) -> LongTailFile:
    """One message whose named header slots all carry the SAME address.

    An ordinary `.eml`: `From` and `Reply-To` are the same person, and a `Cc` to
    oneself makes three. Every slot emits at zone `metadata` with the same
    `raw_value`, so D10 (`ExtractionResult.__post_init__`) merges them into one row.
    `Subject` follows, which is what the signal used to land on.
    """
    return LongTailFile(
        entries=(LongTailEntry(kind="entry", label="<msg-2@example.edu>"),),
        values=tuple(LongTailValue(name=slot, value="same@example.com",
                                   entry_ordinal=1, kind="address")
                     for slot in slots)
        + (LongTailValue(name="Subject", value="Quarterly review",
                         entry_ordinal=1),))


def test_a_signal_survives_the_collapse_of_a_duplicate_address(sink):
    """D10 collapses on `(zone, raw_value)` and RENUMBERS. `long_tail` recorded the
    signal against the PRE-collapse position, so an email whose From and Reply-To
    share an address filed §2.9's sensitivity signal against the next observation --
    the Subject, which is neither an address nor message content."""
    result, _ = run_it(a_repeated_address("From", "Reply-To"), "email")

    assert len(result.extraction.observations) == 2      # the two addresses merged
    flagged = {result.extraction.observations[s.observation_index]["raw_value"]
               for s in result.sensitivity}
    assert flagged == {"same@example.com"}
    assert "Quarterly review" not in flagged
    # §8.5 reads this number through `stage_output.py`; the batch is what it counts.
    assert result.extraction.run["observation_count"] == 2
    sink.write(result.extraction)
    sink.conforms()


def test_three_copies_do_not_end_the_scan(conn):
    """`record_sensitivity_signals` raises IndexError for a position past the
    collapsed batch, and nothing catches it -- the scan ends on an ordinary email."""
    create_schema(conn)
    create_extraction_schema(conn)
    result, _ = run_it(a_repeated_address("From", "Reply-To", "Cc"), "email")

    keys = [f"k{i}" for i in range(len(result.extraction.observations))]
    stored = record_sensitivity_signals(conn, run_id="run-1",
                                        signals=result.sensitivity,
                                        observation_keys=keys, now=FIXED_CLOCK)
    assert stored == 1
    rows = sensitivity_signals_for(conn, "run-1")
    assert [r["observation_key"] for r in rows] == ["k0"]


def test_a_signal_past_the_end_of_the_batch_is_refused_at_construction():
    """The class of bug, refused where the two halves are held together.

    A `LongTailResult` is the only place a batch position and the batch it indexes
    into exist side by side, so it is the only place the claim is checkable before
    `record_sensitivity_signals` is reached with a database open.
    """
    result, _ = run_it(an_email(), "email")
    with pytest.raises(ValueError):
        LongTailResult(
            extraction=result.extraction,
            sensitivity=(SensitivitySignal(
                observation_index=len(result.extraction.observations),
                signal=POTENTIALLY_SENSITIVE, basis="a position past the end"),))


def test_one_located_value_gets_one_row_whatever_two_reasons_it_had(conn):
    """An address quoted in a heading and again in the body is ONE observation once
    D10 collapses, and the signal table is UNIQUE on (run_id, observation_key).

    The two emissions carry different bases -- §2.9 calls a heading address an
    address and a body address message content -- so keeping both reasons writes two
    rows for one key and the INSERT raises. The first reason in document order is the
    one kept, matching the occurrence `location` already addresses (D10).
    """
    create_schema(conn)
    create_extraction_schema(conn)
    quoted = LongTailFile(
        entries=(LongTailEntry(kind="entry", label="<msg-3@example.edu>"),),
        texts=(LongTailText(zone="heading", text="see admin@example.com",
                            entry_ordinal=1, region=1),
               LongTailText(zone="body", text="mail admin@example.com",
                            entry_ordinal=1, region=2)))

    def find_address(text: str):
        at = text.find("admin@example.com")
        return ((StructuredString(kind="email", start=at, end=at + 17),)
                if at != -1 else ())

    result, _ = run_it(quoted, "email", finder=find_address)

    merged = [o for o in result.extraction.observations
              if o["raw_value"] == "admin@example.com"]
    assert len(merged) == 1 and merged[0]["location"]["zone"] == "link"
    keys = [f"k{i}" for i in range(len(result.extraction.observations))]
    stored = record_sensitivity_signals(conn, run_id="run-1",
                                        signals=result.sensitivity,
                                        observation_keys=keys, now=FIXED_CLOCK)
    rows = sensitivity_signals_for(conn, "run-1")
    assert stored == len(rows)
    assert len({r["observation_key"] for r in rows}) == len(rows)


# --------------------------------------------------------------------------- #
# §8.6's ceiling on a spreadsheet, and the word that has to follow it
# --------------------------------------------------------------------------- #

def test_a_spreadsheet_that_was_not_capped_still_reads_complete():
    """The ordinary case, pinned first so the change below cannot quietly widen.

    A workbook the reader finished is `complete`, and its coverage is now in CELLS
    rather than entries -- which is a truer statement about a spreadsheet than "1 of
    1 entries" ever was.
    """
    document = LongTailFile(
        entries=(LongTailEntry(kind="sheet", index=1, label="Data"),),
        texts=(LongTailText(zone="table", text="A", entry_ordinal=1, row=1, column=1),
               LongTailText(zone="table", text="B", entry_ordinal=1, row=1, column=2)),
        cells_total=2)
    result, _ = run_it(document, "spreadsheet")
    assert result.extraction.run["completeness"] == "complete"
    assert result.extraction.run["coverage"] == {
        "units": "cells", "processed": 2, "total": 2}


def test_a_capped_spreadsheet_says_capped_and_not_complete():
    """§2.4's rule, on the one family that had no way to obey it.

    Every long-tail run was `completeness="complete"` with
    `coverage("entries", n, n)` -- a literal, unconditional word. A `.csv` of a
    million cells read to its first ten thousand recorded exactly what a `.csv` of
    ten thousand cells recorded, and nothing downstream could tell them apart. §8.6's
    "89 scanned PDFs deferred after the OCR limit" is computed off this column, and a
    truncated read hiding inside `complete` is the "silently an empty document"
    defect wearing a full count.
    """
    document = LongTailFile(
        entries=(LongTailEntry(kind="sheet", index=1, label="Data"),),
        texts=(LongTailText(zone="table", text="A", entry_ordinal=1, row=1, column=1),),
        cells_total=5000, capped=True)
    result, _ = run_it(document, "spreadsheet")
    assert result.extraction.run["completeness"] == "capped"
    assert result.extraction.run["coverage"] == {
        "units": "cells", "processed": 1, "total": 5000}


def test_the_capped_run_is_counted_as_unfinished_work():
    """§8.6 needs unfinished work to stay VISIBLE as unfinished, and P5 publishes
    exactly one place that decides which runs those are."""
    from extractors.budgets import DEFERRED_COMPLETENESS, UNREADABLE_COMPLETENESS

    document = LongTailFile(
        entries=(LongTailEntry(kind="sheet", index=1),),
        texts=(LongTailText(zone="table", text="A", entry_ordinal=1, row=1, column=1),),
        cells_total=99, capped=True)
    word = run_it(document, "spreadsheet")[0].extraction.run["completeness"]
    assert word in DEFERRED_COMPLETENESS
    assert word not in UNREADABLE_COMPLETENESS, (
        "a ceiling is not damage; §8.6 keeps the two counts disjoint")


def test_a_family_with_no_cells_keeps_counting_entries():
    """An email, a calendar and a contact card have no cells and must not be given
    a cell coverage. The reader says so by reporting no cell total; nothing here
    guesses from the source type, so a format that grows cells later needs no edit."""
    result, _ = run_it(a_deck(), "presentation")
    assert result.extraction.run["coverage"]["units"] == "entries"
    assert result.extraction.run["completeness"] == "complete"


def test_the_processed_count_is_the_texts_that_arrived_not_the_readers_word():
    """The processed half of a coverage is a fact this extractor can check, so it
    checks it. Taking both numbers from the reader would let a reader that stored
    ten cells claim it stored a thousand, and `coverage` would accept it as long as
    the total was larger."""
    document = LongTailFile(
        entries=(LongTailEntry(kind="sheet", index=1),),
        texts=tuple(LongTailText(zone="table", text=f"c{n}", entry_ordinal=1,
                                 row=1, column=n) for n in range(1, 4)),
        cells_total=900, capped=True)
    result, _ = run_it(document, "spreadsheet")
    assert result.extraction.run["coverage"]["processed"] == 3
