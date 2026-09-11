# tests/p5/test_p5_structured_text.py
"""E3's §2.4 half. SPEC Done-means 1: "`unsupported` is distinguishable from
`complete`-with-zero-observations in a query."
"""
from pathlib import Path

import pytest

from extractors.reading import Region, StructuredString
from extractors.safety import DatalessRefused, ProtectedContainerRefused, SafetyPolicy
from extractors.structured_text import (
    EXTRACTOR_NAME, STRUCTURAL_MARKER_KINDS, StructuralMarker, TextDocument,
    UnknownMarkerKind, WrongFamily, extract_structured_text,
)

from conftest import FIXED_CLOCK
from p4_stub import locator_for

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
FILE_ROW = {"file_id": "f-readme", "content_hash": "c4b68614329771504e26f782d73842637dfa7ece1ad2bc377faae5c296806a0b",
            "filename": "README.md"}

BODY = "This project belongs to U Chicago and ships from src.\n"
HEADING = "Setup"


def a_readme() -> TextDocument:
    text = HEADING + "\n" + BODY
    return TextDocument(
        text=text,
        language="Markdown",
        headings=(Region(zone="heading", start=0, end=len(HEADING), ordinal=1,
                         label=HEADING),),
        markers=(StructuralMarker(kind="README file", value="README.md"),
                 StructuralMarker(kind="package manifest", value="package.json")),
    )


def find_u_chicago(text: str):
    at = text.find("U Chicago")
    return (StructuredString(kind="identifier", start=at, end=at + 9),) if at != -1 else ()


def run_it(document="default", source_type="text_document", finder=find_u_chicago):
    body = a_readme() if document == "default" else document
    return extract_structured_text(
        file_row=FILE_ROW, path=Path("/corpus/README.md"), policy=OPEN_POLICY,
        source_type=source_type, read_text_document=lambda path: body,
        find_structured_strings=finder, now=FIXED_CLOCK, context_window=20)


def test_every_observation_conforms_to_p4s_shape(sink):
    sink.write(run_it())
    sink.conforms()


def test_the_full_text_is_one_whole_file_unit(sink):
    # §2.4 + G1: "the full text to P4's `text_units` as one whole-file unit,
    # `container_path: []`".
    run_id = sink.write(run_it())
    whole = [u for u in sink.units_for(run_id) if u["container_path"] == ()]
    assert len(whole) == 1
    assert whole[0]["text"] == HEADING + "\n" + BODY
    assert whole[0]["length"] == len(HEADING + "\n" + BODY)


def test_a_heading_is_both_a_zone_and_an_address(sink):
    run_id = sink.write(run_it())
    heading = [o for o in sink.observations if o["raw_value"] == HEADING][0]
    assert locator_for(heading["location"]) == "heading:heading=1#0-5"
    # P4 conformance rule 10: the span indexes into a unit at exactly that path.
    paths = [u["container_path"] for u in sink.units_for(run_id)]
    assert heading["location"]["container_path"] in paths


def test_language_is_the_readers_value_and_p5_detected_nothing(sink):
    sink.write(run_it())
    language = [o for o in sink.observations
                if o["location"]["container_path"]
                and o["location"]["container_path"][0]["label"] == "language"][0]
    assert language["raw_value"] == "Markdown"
    assert language["location"]["zone"] == "metadata"
    assert language["reliability"] == "direct"


def test_structural_indicators_land_under_section_2_4s_own_class_names(sink):
    sink.write(run_it())
    markers = {o["location"]["container_path"][0]["label"]: o["raw_value"]
               for o in sink.observations
               if o["location"]["container_path"]
               and o["location"]["container_path"][0]["label"] in STRUCTURAL_MARKER_KINDS}
    assert markers == {"README file": "README.md",
                       "package manifest": "package.json"}


def test_a_marker_kind_section_2_4_does_not_name_is_refused():
    # The four CLASSES are §2.4's words; their MEMBERS are Deferred. A reader that
    # coins a fifth class would be authoring vocabulary P5 does not own.
    document = TextDocument(text="x", markers=(StructuralMarker(kind="project vibe",
                                                               value="good"),))
    with pytest.raises(UnknownMarkerKind):
        run_it(document=document)


def test_e3_reads_no_code_and_infers_no_project(sink):
    # §2.4: structural evidence, "rather than forcing semantic analysis to infer a
    # project from arbitrary code text". With no finder and no markers, source code
    # produces its text unit and nothing else.
    source = TextDocument(text="import os\n\n\ndef main():\n    return os.getcwd()\n")
    run_id = sink.write(run_it(document=source, source_type="code_structured",
                               finder=lambda text: ()))
    assert sink.observations_for(run_id) == []
    assert sink.units_for(run_id)[0]["text"] == source.text
    assert sink.run_for(run_id)["completeness"] == "complete"


def test_an_unsupported_format_is_not_an_empty_document(sink):
    # §2.4's whole point, and Done-means 1. Two runs, two values, one query apart.
    empty = sink.write(run_it(document=TextDocument(text="")))
    absent = sink.write(run_it(document=None))

    assert sink.run_for(empty)["completeness"] == "complete"
    assert sink.run_for(absent)["completeness"] == "unsupported"
    assert sink.observations_for(empty) == sink.observations_for(absent) == []
    assert sink.run_for(absent)["extractor_name"] == EXTRACTOR_NAME
    sink.conforms()


def test_an_unsupported_run_stores_no_text_unit(sink):
    run_id = sink.write(run_it(document=None))
    assert sink.units_for(run_id) == []


def test_raw_is_the_source_substring_untouched(sink):
    # SPEC Done-means 3: "A document saying `U Chicago` keeps that exact wording."
    sink.write(run_it())
    found = [o for o in sink.observations if o["raw_value"] == "U Chicago"]
    assert len(found) == 1
    assert found[0]["normalized_value"] == "U Chicago"


def test_the_same_content_produces_the_same_observations(sink):
    # P4 conformance rule 8 / §8.5's replay diff.
    first, second = sink.write(run_it()), sink.write(run_it())
    strip = lambda rows: [{k: v for k, v in r.items() if k != "run_id"} for r in rows]
    assert strip(sink.observations_for(first)) == strip(sink.observations_for(second))


def test_a_source_type_from_the_other_half_of_e3_is_refused():
    with pytest.raises(WrongFamily):
        run_it(source_type="email")


def test_no_extractor_is_reachable_inside_a_protected_container():
    policy = SafetyPolicy(is_protected_container=lambda path: True,
                          is_dataless=lambda path: False)
    with pytest.raises(ProtectedContainerRefused):
        extract_structured_text(
            file_row=FILE_ROW, path=Path("/Applications/Thing.app/Contents/README.md"),
            policy=policy, source_type="text_document",
            read_text_document=lambda path: pytest.fail("the reader was reached"),
            find_structured_strings=lambda text: (), now=FIXED_CLOCK,
            context_window=20)


def test_a_dataless_file_is_never_read():
    policy = SafetyPolicy(is_protected_container=lambda path: False,
                          is_dataless=lambda path: True)
    with pytest.raises(DatalessRefused):
        extract_structured_text(
            file_row=FILE_ROW, path=Path("/corpus/README.md"), policy=policy,
            source_type="text_document",
            read_text_document=lambda path: pytest.fail("the reader was reached"),
            find_structured_strings=lambda text: (), now=FIXED_CLOCK,
            context_window=20)


def test_the_readable_text_is_an_observation_the_recogniser_can_scan(sink):
    """`00`:35 -- text documents "should yield full text ... and structural
    information" -- and until now the full text reached `text_units` and NOTHING
    else.

    That is not an academic gap. The shipped recogniser holds 8,907 authored
    terms (`syllabus`, `problem set`, `office hours`) and reads OBSERVATIONS
    only, deliberately: `detector._matches` -- "a detector that pulled whole text
    units would be a second materialisation locus". So on every live run it saw
    the filename, the path, the extension, the MIME type and one identifier, and
    abstained on every file with `no_corroboration` -- it had matched one term
    from the FILENAME and its own rule is that one signal never activates a
    schema. The corroborating words were in the document, stored, and unreachable.

    The document's own words are evidence. This makes them evidence.
    """
    run_id = sink.write(run_it())
    text = HEADING + "\n" + BODY
    body = [o for o in sink.observations
            if o["raw_value"] == text
            and o["location"]["zone"] == "body"
            and o["location"]["container_path"] == ()]
    assert len(body) == 1, [o["raw_value"] for o in sink.observations]


def test_the_readable_text_does_not_become_a_folder_name(sink):
    """The other half, and the reason the first half is safe to do.

    A deployment turns observations into FACTS by claiming a locator, and a fact
    is what a folder gets named after. `65` §2.2 recorded widening extraction as
    a privacy trade-off for exactly this reason -- but it is two knobs, not one:
    what the product SEES and what the product ASSERTS.

    The whole-text observation is addressed `body` with no container, and the
    shipped deployment's one direct slot claims `body#...` and `heading...`. So
    the recogniser can read the document while nothing in it can name a folder.
    A future slot that claimed this locator would be choosing otherwise, and this
    test is what tells it that it did.
    """
    import sys
    from pathlib import Path as _Path
    sys.path.insert(0, str(_Path(__file__).resolve().parents[2] / "src"))
    import cli

    run_id = sink.write(run_it())
    text = HEADING + "\n" + BODY
    body = [o for o in sink.observations if o["raw_value"] == text][0]
    locator = locator_for(body["location"])
    assert not locator.startswith("body#")
    # NO SHIPPED PRODUCER CLAIMS IT, which is the property this test is about, and
    # after 2026-09-04 that is TWO statements rather than one. `DIRECT_SLOTS` is
    # empty -- the deployment ships no direct slot at all -- so the locator half is
    # asked of the whole set, and `subject` is now filled by §3.5's rule, which sees
    # no locator and is held off a whole zone by anchoring its pattern to the entire
    # reading. Both are asserted, because a future slot could re-open the first door
    # and a de-anchored pattern the second.
    assert not any(slot.names(locator) for slot in cli.DIRECT_SLOTS.slots), locator
    assert cli.SUBJECT_RULE.pattern.search(text) is None, text


# --- `104` R-164: the document is read one paragraph at a time -------------------

#: Three paragraphs of prose, each carrying the line terminator its last line ends
#: with -- that is what "the paragraph verbatim" means, and it is what makes the
#: paragraphs and the separators add back up to the file.
PARAGRAPHS = (
    "PHYS 1401 course outline, autumn term.\n",
    "Office hours are Tuesday afternoons in room 214, and the teaching assistant\n"
    "holds a second session on Thursday morning.\n",
    "Grading is 40% exams, 30% labs and 30% homework, and late work is accepted\n"
    "for one week with a penalty.\n",
)
#: The separators are the DOCUMENT's and deliberately not alike: one empty line, then
#: a run of two lines that hold only whitespace. Neither is a shape this module
#: recognises; both are blank lines, which is all the split is allowed to know.
SEPARATORS = ("\n", "   \n\t\n")
PROSE = (PARAGRAPHS[0] + SEPARATORS[0] + PARAGRAPHS[1] + SEPARATORS[1]
         + PARAGRAPHS[2])


def three_paragraphs() -> TextDocument:
    return TextDocument(text=PROSE)


def find_room(text: str):
    at = text.find("room 214")
    return ((StructuredString(kind="identifier", start=at, end=at + len("room 214")),)
            if at != -1 else ())


def body_readings(sink, run_id) -> list:
    """Every SPAN-LESS `body` observation of a run, in emission order.

    Span-less is the filter that matters and zone alone is not enough: a structured
    string found outside a heading also lands in `body` at the empty path, WITH a
    span (`ZONE_BY_STRUCTURED_KIND` has no entry for `identifier`), and it is a
    reading of eight characters rather than of a paragraph.
    """
    return [o for o in sink.observations_for(run_id)
            if o["location"]["zone"] == "body"
            and o["location"]["text_span"] is None]


def paragraph_units(sink, run_id) -> list:
    return [u for u in sink.units_for(run_id)
            if u["container_path"] and u["container_path"][0]["kind"] == "paragraph"]


def test_a_prose_document_is_read_one_paragraph_at_a_time(sink):
    """`104` R-164. E3 made ONE unit of a whole text file and one span-less `body`
    reading over it, and `104` §16.1 measured what that cost: a reading the size of
    a document is refused as the whole of its unit, so a 39,000-character `.txt`
    reached the model as its headings and its file extension. The words were
    extracted, stored, and shown to nobody.

    A paragraph is a reading a dossier ceiling can admit. The split is the
    document's own blank lines -- `docx.py` has located a Word file's paragraphs
    since E2 and this is the same address for the same thing.
    """
    run_id = sink.write(run_it(document=three_paragraphs(), finder=lambda text: ()))
    readings = body_readings(sink, run_id)

    assert [o["raw_value"] for o in readings] == list(PARAGRAPHS)
    assert [locator_for(o["location"]) for o in readings] == [
        "body:paragraph=1", "body:paragraph=2", "body:paragraph=3"]
    assert all(o["reliability"] == "possible" for o in readings)
    sink.conforms()


def test_the_paragraphs_are_the_documents_own_and_add_back_up_to_it(sink):
    """The only thing the split may consult is the file's structure. So: the units
    are in the document's order, each is the document's own characters, and what
    lies between them is blank -- which together means nothing was dropped,
    reordered, trimmed or invented."""
    run_id = sink.write(run_it(document=three_paragraphs(), finder=lambda text: ()))
    units = paragraph_units(sink, run_id)

    assert [u["container_path"][0]["index"] for u in units] == [1, 2, 3]
    assert [u["container_path"][0]["label"] for u in units] == [None, None, None]
    texts = [u["text"] for u in units]
    assert texts == list(PARAGRAPHS)

    at, gaps = 0, []
    for text in texts:
        start = PROSE.index(text, at)
        gaps.append(PROSE[at:start])
        at = start + len(text)
    gaps.append(PROSE[at:])
    assert all(gap.strip() == "" for gap in gaps), gaps
    assert "".join(gap + text for gap, text in zip(gaps, texts)) + gaps[-1] == PROSE


def test_the_whole_document_reading_is_not_emitted_beside_the_paragraphs(sink):
    """The reading no ceiling can ever admit is not sent twice.

    Emitting it beside the paragraphs would duplicate every character of the file in
    a reading that `items.is_whole_document` refuses by construction -- the shape
    `104` R-164 exists to remove. The UNIT at the empty path stays, and is a
    different thing: P4 rule 10 anchors the heading and structured-string spans to
    it, and it is what a whole-document refusal is measured against.
    """
    run_id = sink.write(run_it(document=three_paragraphs(), finder=lambda text: ()))

    assert [o for o in body_readings(sink, run_id) if o["raw_value"] == PROSE] == []
    whole = [u for u in sink.units_for(run_id) if u["container_path"] == ()]
    assert len(whole) == 1 and whole[0]["text"] == PROSE


def test_a_one_paragraph_document_is_read_exactly_as_before(sink):
    """The README has no blank line, so it is one paragraph and nothing about it
    changes: one span-less `body` reading at the empty path, measured against the
    unit that was always there. A `paragraph=1` unit beside it would be the same
    characters stored twice under a second address."""
    run_id = sink.write(run_it())
    readings = body_readings(sink, run_id)

    assert len(readings) == 1
    assert readings[0]["raw_value"] == HEADING + "\n" + BODY
    assert readings[0]["location"]["container_path"] == ()
    assert paragraph_units(sink, run_id) == []


def test_headings_and_structured_strings_are_read_against_the_whole_document(sink):
    """Unchanged by the split, and both halves matter.

    A heading is located by its own ordinal and its span indexes into its own unit.
    A structured string found outside every heading is located at the empty path
    with a span into the WHOLE text -- so it stays anchored to the whole-document
    unit, at offsets counted from the start of the file, not from the start of a
    paragraph.
    """
    heading = PARAGRAPHS[0].rstrip("\n")
    document = TextDocument(
        text=PROSE,
        headings=(Region(zone="heading", start=0, end=len(heading), ordinal=1,
                         label=heading),))
    run_id = sink.write(run_it(document=document, finder=find_room))

    found = [o for o in sink.observations_for(run_id)
             if o["raw_value"] == "room 214"]
    assert len(found) == 1
    span = found[0]["location"]["text_span"]
    assert found[0]["location"]["container_path"] == ()
    assert PROSE[span["start"]:span["end"]] == "room 214"

    head = [o for o in sink.observations_for(run_id)
            if o["location"]["zone"] == "heading"]
    assert len(head) == 1 and head[0]["raw_value"] == heading
    assert locator_for(head[0]["location"]) == f"heading:heading=1#0-{len(heading)}"
    sink.conforms()


def test_a_paragraph_reading_does_not_become_a_folder_name(sink):
    """`test_the_readable_text_does_not_become_a_folder_name`'s property, asked of
    the new locator, because the new locator is the one that could break it.

    A paragraph reading is addressed `body:paragraph=N`. It still carries no span,
    so it still does not serialise into the `body#...` space a direct slot claims,
    and the deployment still ships no direct slot at all. What the product may READ
    widened; what it may ASSERT did not.
    """
    import sys
    from pathlib import Path as _Path
    sys.path.insert(0, str(_Path(__file__).resolve().parents[2] / "src"))
    import cli

    run_id = sink.write(run_it(document=three_paragraphs(), finder=lambda text: ()))
    readings = body_readings(sink, run_id)
    assert len(readings) > 1
    for reading in readings:
        locator = locator_for(reading["location"])
        assert not locator.startswith("body#"), locator
        assert not any(slot.names(locator) for slot in cli.DIRECT_SLOTS.slots), locator


def test_a_paragraph_repeated_in_the_file_collapses_under_p4s_own_rule(sink):
    """Plain text repeats itself -- a rule, a prompt, a `Question:` before every
    answer -- so the split meets P4 D10 constantly, and D10 is what decides.

    D10 is one observation per (run, exact raw value, zone), applied for every
    extractor at `sink.ExtractionResult`. Two identical paragraphs are therefore ONE
    `body` reading, addressed at the FIRST of them in document order and carrying
    `occurrence_count: 2` -- not two rows, and not one row that silently lost a
    sibling. Nothing here is R-164's to decide; this test is what says the split
    does not quietly opt out of the rule the way six extractors once did.

    Every paragraph still gets its UNIT. Units are not collapsed, the text of the
    repeat is stored at its own address, and a reading of it can still be minted.
    """
    repeated = "Question:\n"
    document = TextDocument(
        text=repeated + "\n" + PARAGRAPHS[1] + "\n" + repeated)
    run_id = sink.write(run_it(document=document, finder=lambda text: ()))

    readings = body_readings(sink, run_id)
    assert [o["raw_value"] for o in readings] == [repeated, PARAGRAPHS[1]]
    assert [o["occurrence_count"] for o in readings] == [2, 1]
    assert locator_for(readings[0]["location"]) == "body:paragraph=1"
    assert [u["container_path"][0]["index"] for u in paragraph_units(sink, run_id)] \
        == [1, 2, 3]


#: `104` R-160. A notebook as `readers/text_documents._notebook` reports one: the
#: cells joined by a blank line, a markdown cell reported as a `body` region carrying
#: the NOTEBOOK'S own cell number, and the code cell beside it reported as nothing at
#: all. The markdown cell is the SECOND, which is what makes the ordinal an assertion
#: rather than a coincidence.
NOTEBOOK_CODE = "import math\nmass = 0.51\n"
NOTEBOOK_PROSE = "# Air track lab\n\nCart mass was 0.51 kg.\n"


def a_notebook() -> TextDocument:
    text = NOTEBOOK_CODE + "\n\n" + NOTEBOOK_PROSE
    start = text.index(NOTEBOOK_PROSE)
    return TextDocument(
        text=text,
        headings=(Region(zone="heading", start=start, end=start + 15, ordinal=1,
                         label="Air track lab"),),
        cells=(Region(zone="body", start=start, end=start + len(NOTEBOOK_PROSE),
                      ordinal=2),),
    )


def cell_units(sink, run_id) -> list:
    return [u for u in sink.units_for(run_id)
            if u["container_path"] and u["container_path"][0]["kind"] == "cell"]


def test_a_notebooks_markdown_cell_is_a_body_unit_at_its_own_address(sink):
    """`104` R-160, the half that is E3's.

    The cell-aware reader landed and a notebook STILL showed the model nothing it was
    about: `.ipynb` is `code_structured`, the whole-text body reading is emitted for
    `text_document` only, and the recogniser reads observations. So eleven of the
    owner's notebooks produced headings, three metadata markers and zero evidence of
    their own prose -- the words were extracted, stored, and shown to nobody, which
    is R-164's failure one family further along.

    A markdown cell is not "arbitrary code text". §2.4's exclusion is about source,
    and this is the paragraph a person typed into a prose cell. It is emitted
    whatever the family says, because the READER is what decided this stretch was
    prose -- E3 asks nothing about the format.

    `cell=2` IS THE NOTEBOOK'S OWN ADDRESS (P4 D3 rule 3), and the unit standing at
    exactly that path holds exactly those characters, so P4 rule 10 is satisfied by
    construction and the reading is measured against the cell it is the whole of --
    a cell-sized reading is one §8.6's ceiling can admit, where the 118,000-character
    notebook `104` §16.1 measured was a reading nothing could.
    """
    run_id = sink.write(run_it(document=a_notebook(), source_type="code_structured",
                               finder=lambda text: ()))

    readings = body_readings(sink, run_id)
    assert [o["raw_value"] for o in readings] == [NOTEBOOK_PROSE], (
        "a notebook's prose is still invisible to everything that reads evidence")
    assert locator_for(readings[0]["location"]) == "body:cell=2"
    assert [u["text"] for u in cell_units(sink, run_id)] == [NOTEBOOK_PROSE]
    sink.conforms()


def test_a_notebook_cell_reading_does_not_become_a_folder_name(sink):
    """`test_a_paragraph_reading_does_not_become_a_folder_name`'s property, asked of
    the newest locator, because the newest locator is the one that could break it.

    A cell reading is addressed `body:cell=N` and carries no span, so it does not
    serialise into the `body#...` space a direct slot claims. What the product may
    READ widened; what it may ASSERT did not.
    """
    import sys
    from pathlib import Path as _Path
    sys.path.insert(0, str(_Path(__file__).resolve().parents[2] / "src"))
    import cli

    run_id = sink.write(run_it(document=a_notebook(), source_type="code_structured",
                               finder=lambda text: ()))
    for reading in body_readings(sink, run_id):
        locator = locator_for(reading["location"])
        assert not locator.startswith("body#"), locator
        assert not any(slot.names(locator) for slot in cli.DIRECT_SLOTS.slots), locator


def test_a_notebooks_code_cell_is_not_read_as_prose(sink):
    """§2.4 asks code for structural evidence "rather than forcing semantic analysis
    to infer a project from arbitrary code text", and P4 publishes no `code` zone to
    put a code cell in. `test_e3_reads_no_code_and_infers_no_project` asks this of a
    whole source file; this asks it of the code cell sitting beside prose that IS
    read, which is the one place the two could be confused.

    The guard is the reader's REPORT and not a judgement here: E3 reads
    `document.cells` and nothing else, so a cell the reader does not report reaches
    no observation and no unit. The day P4 publishes a zone for code, the reader
    reports code cells and this is the test that has to be re-argued.
    """
    run_id = sink.write(run_it(document=a_notebook(), source_type="code_structured",
                               finder=lambda text: ()))

    assert not [o for o in sink.observations_for(run_id)
                if NOTEBOOK_CODE in o["raw_value"]], (
        "a code cell reached the evidence as prose")
    assert NOTEBOOK_CODE not in [u["text"] for u in cell_units(sink, run_id)]


def test_a_document_with_no_cells_is_read_exactly_as_it_was(sink):
    """R-160 is a notebook's row and must be nothing else's. A `.txt` and a `.md`
    have no cells, their reader reports none, and the loop that emits them does not
    run -- so R-164's paragraph split and the whole-file unit are untouched.
    """
    run_id = sink.write(run_it(document=three_paragraphs(), finder=lambda text: ()))

    assert cell_units(sink, run_id) == []
    assert [u["container_path"][0]["index"] for u in paragraph_units(sink, run_id)] \
        == [1, 2, 3]
