# tests/p5/test_p5_docx.py
"""E2 - §2.3. Done-means 6: "DOCX table cells and heading zones are present and
distinguishable from body text.\""""
from pathlib import Path

import pytest

from extractors.docx import (
    DocxAnnotation, DocxCell, DocxDocument, DocxLink, DocxParagraph, EXTRACTOR_NAME,
    extract_docx,
)
from extractors.reading import StructuredString
from extractors.safety import ProtectedContainerRefused, SafetyPolicy

from conftest import FIXED_CLOCK
from p4_stub import locator_for

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
FILE_ROW = {"file_id": "f1", "content_hash": "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124", "filename": "Wash U.docx"}

PROMPT = "Please tell us what you are interested in studying at college and why."


def a_wash_u_docx() -> DocxDocument:
    """The SPEC's `wash-u.docx`: an unhelpful filename, a decisive heading, and the
    data in table cells."""
    return DocxDocument(
        core_properties={"title": "", "creator": "python-docx",
                         "lastModifiedBy": "J. Yung",
                         "created": "2026-07-17T14:03:22Z"},
        iso_dates={"created": "2026-07-17T14:03:22+00:00"},
        paragraphs=(
            DocxParagraph(index=1, text="Application Essay", zone="heading",
                          heading_path=((1, "Application Essay"),)),
            DocxParagraph(index=2, text=PROMPT, zone="heading",
                          heading_path=((1, "Application Essay"), (1, PROMPT))),
            DocxParagraph(index=3, text="I want to study economics at Wash U.",
                          zone="body",
                          heading_path=((1, "Application Essay"), (1, PROMPT))),
            DocxParagraph(index=4, text="Page 1 of 2", zone="header_footer"),
        ),
        cells=(DocxCell(table=3, row=1, column=1, text="Institution",
                        column_header="Field"),
               DocxCell(table=3, row=2, column=1, text="Wash U",
                        column_header="Field")),
        links=(DocxLink(target="https://admissions.wustl.edu", paragraph=3),),
        relationships=("word/document.xml", "word/footer1.xml"),
        annotations=(DocxAnnotation(name="comment", text="tighten this",
                                    paragraph=3),),
    )


def find_wash_u(text: str):
    at = text.find("Wash U")
    return (StructuredString(kind="identifier", start=at, end=at + 6),) if at != -1 else ()


def run_it(document=None, finder=find_wash_u):
    return extract_docx(file_row=FILE_ROW, path=Path("/corpus/Wash U.docx"),
                        policy=OPEN_POLICY,
                        read_docx=lambda path: document or a_wash_u_docx(),
                        find_structured_strings=finder, now=FIXED_CLOCK,
                        context_window=40)


def test_every_observation_conforms_to_p4s_shape(sink):
    sink.write(run_it())
    sink.conforms()


def test_a_heading_a_table_cell_and_body_text_are_three_distinguishable_zones(sink):
    # §2.3: "The extractor must preserve the difference between a heading, a table
    # label, a filename, and ordinary body text, because those locations carry
    # different evidentiary weight."
    sink.write(run_it())
    zones = {o["location"]["zone"] for o in sink.observations}
    assert {"heading", "table", "header_footer"} <= zones
    heading = [o for o in sink.observations if o["raw_value"] == PROMPT][0]
    assert heading["location"]["zone"] == "heading"
    cell = [o for o in sink.observations
            if o["raw_value"] == "Wash U" and o["location"]["zone"] == "table"][0]
    assert locator_for(cell["location"]) == "table:table=3/row=2/column=1#0-6"


def test_the_decisive_heading_survives_the_unhelpful_filename(sink):
    # §2.3's own worked case. The filename says nothing; the heading says everything,
    # and the heading's zone is what makes that difference visible to P6.
    sink.write(run_it())
    prompts = [o for o in sink.observations if o["raw_value"] == PROMPT]
    assert len(prompts) == 1
    assert prompts[0]["location"]["zone"] == "heading"
    assert prompts[0]["reliability"] == "possible"


def test_heading_level_is_the_container_paths_depth(sink):
    # §2.3 requires heading levels; P4 has one `heading` zone and no level field, and
    # its segment table addresses `heading` by "ordinal within parent". Depth is the
    # level.
    sink.write(run_it())
    top = [o for o in sink.observations
           if o["raw_value"] == "Application Essay"][0]
    nested = [o for o in sink.observations if o["raw_value"] == PROMPT][0]
    assert len(top["location"]["container_path"]) == 1
    assert len(nested["location"]["container_path"]) == 2
    assert locator_for(nested["location"]) == f"heading:heading=1/heading=1#0-{len(PROMPT)}"


def test_every_cell_and_paragraph_has_its_own_addressable_unit(sink):
    # P4 conformance rule 10.
    run_id = sink.write(run_it())
    paths = {locator_for({"zone": "x", "container_path": u["container_path"],
                          "text_span": None, "time_span": None})
             for u in sink.units_for(run_id)}
    assert "x:table=3/row=2/column=1" in paths
    assert "x:heading=1/heading=1/paragraph=3" in paths
    assert not [u for u in sink.units_for(run_id) if u["container_path"] == ()]


def test_a_body_paragraph_is_not_a_located_value(sink):
    """G1's reasoning, applied to §2.3: a paragraph of body text is not a LOCATED value.

    NARROWED to what that sentence actually says, on the owner's ruling, after the
    measured defect below. It used to assert that no observation carried the
    paragraph's text AT ALL, and on a one-paragraph fixture those two statements are
    indistinguishable -- so it also forbade the document's prose from being evidence
    anywhere, which is not what G1 says and not what the design wants.

    Measured over the owner's 199-file baseline: 20,819 text units and 150 `body`
    observations, of which 134 were `find_structured_strings` matches averaging eight
    characters. The other 16 were whole documents from E3 -- every `.txt`, `.html`
    and `.md`, and not one of the 33 `.docx`. The recogniser scans observations only
    (`recognition/detector.py`), so a Word document reached the model with its
    headings and its `last_modified_by` and nothing it said.

    `structured_text.py` had carried the fix since E3's ratification here
    (`test_p5_structured_text.py`: "The document's own words are evidence. This makes
    them evidence.") and E2 never got it. What G1 forbids is a paragraph becoming an
    ADDRESSABLE value -- one a citation points at, and one a folder could be named
    after. So that is what is asserted: no observation is located AT a paragraph
    path. The prose observation beside it has `container_path=()` and no span, and
    `test_the_prose_observation_is_not_addressable` is the other half.
    """
    run_id = sink.write(run_it())
    body_text = "I want to study economics at Wash U."
    assert any(u["text"] == body_text for u in sink.units_for(run_id))

    # A value FOUND INSIDE a paragraph is located there and should be -- that is
    # `find_structured_strings` doing its job, and the test below this one asserts
    # it. What G1 forbids is the paragraph ITSELF becoming the addressable value.
    whole_paragraph_as_a_value = [
        o for o in sink.observations
        if any(s["kind"] == "paragraph" for s in o["location"]["container_path"])
        and o["raw_value"] == body_text
    ]
    assert not whole_paragraph_as_a_value, whole_paragraph_as_a_value


def test_the_prose_observation_is_not_addressable(sink):
    """The other half, and the reason the first half is safe to narrow.

    A deployment turns an observation into a FACT by claiming its locator, and a fact
    is what a folder is named after. This one is addressed `body` with NO container
    and NO span, so its locator is bare `body` -- and `cli.reads_a_structured_string`
    admits a text-zone locator only when it carries a `#`. So the recogniser can read
    the document while nothing in it can name a folder.

    The span is also not merely a preference: P4 rule 10 anchors a span-carrying
    observation to a text unit at exactly its path, and the whole body is a unit at
    no path -- giving this one a span raises `NonConforming`.
    """
    run_id = sink.write(run_it())
    prose = [o for o in sink.observations
             if o["location"]["zone"] == "body"
             and o["location"]["container_path"] == ()]

    assert len(prose) == 1, [o["raw_value"] for o in sink.observations]
    assert prose[0]["location"]["text_span"] is None
    assert "I want to study economics at Wash U." in prose[0]["raw_value"]


def test_a_value_inside_body_text_arrives_through_the_injected_finder(sink):
    sink.write(run_it())
    found = [o for o in sink.observations
             if o["raw_value"] == "Wash U" and o["location"]["zone"] == "body"]
    assert len(found) == 1
    assert found[0]["location"]["container_path"][-1]["kind"] == "paragraph"


def test_the_column_header_is_carried_on_the_column_segment(sink):
    # P4's segment table: "`column` | index | column header text".
    sink.write(run_it())
    cell = [o for o in sink.observations
            if o["raw_value"] == "Wash U" and o["location"]["zone"] == "table"][0]
    assert cell["location"]["container_path"][-1]["label"] == "Field"


def test_hyperlinks_relationships_and_comments_are_all_emitted(sink):
    # §2.3: "hyperlinks, document relationships, and available revision or comment
    # metadata."
    sink.write(run_it())
    by_zone = {}
    for o in sink.observations:
        by_zone.setdefault(o["location"]["zone"], []).append(o["raw_value"])
    assert "https://admissions.wustl.edu" in by_zone["link"]
    assert "word/footer1.xml" in by_zone["metadata"]
    assert "tighten this" in by_zone["annotation"]


def test_the_hyperlink_target_keeps_its_position_and_carries_no_span(sink):
    # The target is a machine slot, not a substring of the paragraph, so there is
    # nothing for a span to index - P4 rule 4's coarser address.
    sink.write(run_it())
    link = [o for o in sink.observations
            if o["raw_value"] == "https://admissions.wustl.edu"][0]
    assert link["location"]["text_span"] is None
    assert link["reliability"] == "direct"
    assert link["location"]["container_path"][-1]["kind"] == "paragraph"


def test_the_author_metadata_is_supporting_information_with_no_marker(sink):
    # §2.3: "DOCX author metadata should remain supporting information only." M4: the
    # discount rule is P6's and there is no marker on the record.
    from extractors.shape import OBSERVATION_FIELDS
    sink.write(run_it())
    creator = [o for o in sink.observations
               if locator_for(o["location"]) == "metadata:field=creator"][0]
    assert creator["raw_value"] == "python-docx"
    assert creator["reliability"] == "direct"
    assert tuple(k for k in creator if k != "run_id") == OBSERVATION_FIELDS


def test_an_empty_core_property_produces_no_row(sink):
    # An observation records presence, never absence.
    sink.write(run_it())
    assert not [o for o in sink.observations
                if locator_for(o["location"]) == "title:field=title"]


def test_neither_the_filename_nor_the_extension_is_re_emitted_here(sink):
    # O5: they are the `filesystem` run's, and two homes for one value is the defect.
    sink.write(run_it())
    assert not [o for o in sink.observations
                if o["location"]["zone"] in ("filename", "path")]


def test_the_run_is_native_and_names_the_docx_extractor(sink):
    run_id = sink.write(run_it())
    row = sink.run_for(run_id)
    assert row["extractor_name"] == EXTRACTOR_NAME == "docx.structure"
    assert row["source_type"] == "text_document"
    assert row["analysis_tier"] == "native"
    assert row["completeness"] == "complete"
    assert row["coverage"]["units"] == "paragraphs"


def test_e2_refuses_a_protected_path_before_it_calls_its_reader():
    calls = []
    policy = SafetyPolicy(is_protected_container=lambda path: True,
                          is_dataless=lambda path: False)
    with pytest.raises(ProtectedContainerRefused):
        extract_docx(file_row=FILE_ROW, path=Path("/Applications/T.app/x.docx"),
                     policy=policy,
                     read_docx=lambda path: calls.append(path) or a_wash_u_docx(),
                     find_structured_strings=find_wash_u, now=FIXED_CLOCK,
                     context_window=40)
    assert calls == []
