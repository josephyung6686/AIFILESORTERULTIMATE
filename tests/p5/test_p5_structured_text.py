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
    assert not cli.DIRECT_SLOTS.slots[0].names(locator), locator
