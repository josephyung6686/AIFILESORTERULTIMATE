# tests/p4/test_p4_location.py
import pytest

from evidence_shape.location import (
    Location, MalformedLocation, Region, Segment, TextSpan, TimeSpan,
)
from evidence_shape.vocabulary import NotInVocabulary


def test_2_8s_own_pdf_example_is_expressible():
    # §2.8: "A PDF match may be located at page 1, heading 2".
    location = Location(
        zone="heading",
        container_path=(Segment("page", 1),
                        Segment("heading", 2, label="Course Information")),
        text_span=TextSpan(0, 10),
    )
    assert location.zone == "heading"
    assert location.container_path[0].index == 1
    assert location.container_path[1].label == "Course Information"


def test_2_8s_own_docx_exif_and_manifest_examples_are_expressible():
    # "table 3, row 2, column 1"; "EXIF DateTimeOriginal"; "a manifest path".
    assert Location("table", (Segment("table", 3), Segment("row", 2),
                              Segment("column", 1))).container_path[2].index == 1
    assert Location("metadata", (Segment("field", label="DateTimeOriginal"),))
    assert Location("manifest", (Segment("entry", label="docs/transcript.pdf"),))


def test_a_caption_carries_a_time_span_and_no_page():
    # §2.9 audio/video: captions and transcripts have no page and no document offset.
    location = Location("transcript", time_span=TimeSpan(252_500, 255_200))
    assert location.container_path == ()
    assert location.text_span is None


def test_container_path_accepts_any_sequence_and_stores_a_tuple():
    assert Location("body", [Segment("page", 4)]) == Location("body", (Segment("page", 4),))
    assert isinstance(Location("body", [Segment("page", 4)]).container_path, tuple)


def test_a_location_is_frozen_and_hashable():
    # RAW-2 in miniature: nothing about a recorded observation is edited in place.
    location = Location("body", (Segment("page", 18),), text_span=TextSpan(12043, 12051))
    with pytest.raises(Exception):
        location.zone = "title"
    assert {location, Location("body", (Segment("page", 18),),
                               text_span=TextSpan(12043, 12051))} == {location}


def test_the_zone_and_the_kind_come_from_the_closed_vocabularies():
    with pytest.raises(NotInVocabulary):
        Location("h1")
    with pytest.raises(NotInVocabulary):
        Location("body", (Segment("chapter", 2),))


def test_indices_are_1_based():
    # D3: §2.8's examples are 1-based and appear in user-visible explanations (§8.2).
    assert Segment("page", 1).index == 1
    with pytest.raises(MalformedLocation):
        Segment("page", 0)
    with pytest.raises(MalformedLocation):
        Segment("page", -1)


def test_an_indexed_kind_needs_an_index_and_a_label_kind_needs_a_label():
    # Segment-kind rule 2.
    with pytest.raises(MalformedLocation):
        Segment("page")                                  # indexed, no index
    with pytest.raises(MalformedLocation):
        Segment("field")                                 # label kind, no label
    with pytest.raises(MalformedLocation):
        Segment("field", 3, label="DateTimeOriginal")    # label kind with an index
    with pytest.raises(MalformedLocation):
        Segment("entry", 1)


def test_a_label_is_allowed_on_an_indexed_kind_because_rule_3_puts_one_there():
    # Rule 3: "a spreadsheet cell is `sheet=2/row=7/column=3` with `label: "C7"` on
    # the column segment, not a separate `cell` kind."
    assert Segment("column", 3, label="C7").label == "C7"
    assert Segment("slide", 6, label="Timeline").label == "Timeline"
    assert Segment("page", 4).label is None


def test_a_boolean_is_not_an_index():
    with pytest.raises(MalformedLocation):
        Segment("page", True)


def test_text_spans_are_0_based_and_half_open():
    assert TextSpan(0, 10).start == 0
    assert TextSpan(7, 7).end == 7                       # empty span is well-formed
    with pytest.raises(MalformedLocation):
        TextSpan(-1, 4)
    with pytest.raises(MalformedLocation):
        TextSpan(10, 4)                                  # end before start


def test_time_spans_are_integer_milliseconds_from_media_start():
    assert TimeSpan(252_500, 255_200).end_ms == 255_200
    with pytest.raises(MalformedLocation):
        TimeSpan(-1, 10)
    with pytest.raises(MalformedLocation):
        TimeSpan(255_200, 252_500)
    with pytest.raises(MalformedLocation):
        TimeSpan(1.5, 2.5)                               # milliseconds, not seconds


def test_a_location_carries_one_span_or_the_other_never_both():
    # The locator grammar is `[ "#" text_span | "@" time_span ]`; a record carrying
    # both would serialize to a string that cannot round-trip.
    with pytest.raises(MalformedLocation):
        Location("transcript", text_span=TextSpan(0, 4), time_span=TimeSpan(0, 10))


def test_a_bounding_box_carries_one_of_2_7s_two_units():
    assert Region(0, 0, 100, 40, "px").unit == "px"
    assert Region(0.1, 0.2, 0.3, 0.4, "norm").w == 0.3
    with pytest.raises(NotInVocabulary):
        Region(0, 0, 1, 1, "percent")


def test_the_region_segment_kind_and_the_region_bounding_box_are_not_one_thing():
    # §2.8's "an OCR region" is an addressing step; §2.7's "bounding boxes where
    # available" is a rectangle. Both are published as `region` and they are
    # structurally distinct: one is a Segment, one is a Region.
    location = Location("ocr", (Segment("page", 4), Segment("region", 2)),
                        text_span=TextSpan(0, 24),
                        region=Region(12, 40, 300, 22, "px"))
    assert isinstance(location.container_path[1], Segment)
    assert isinstance(location.region, Region)
    assert location.container_path[1].index == 2
    assert location.region.w == 300


def test_unknown_structure_degrades_to_a_coarser_path_and_invents_no_kind():
    # Segment-kind rule 4. An extractor that can locate a value on a page but not
    # within it emits `[{page, 4}]` -- there is no `other` kind and no free-text
    # segment, because the first extractor that needed one would take it.
    coarse = Location("body", (Segment("page", 4),))
    assert coarse.container_path == (Segment("page", 4),)
    with pytest.raises(NotInVocabulary):
        Segment("other", 1)
    with pytest.raises(NotInVocabulary):
        Segment("unknown", label="somewhere on page 4")


def test_every_prefix_of_a_valid_path_is_itself_a_valid_coarser_address():
    # Segment-kind rule 1.
    full = (Segment("page", 4), Segment("table", 3), Segment("row", 2),
            Segment("column", 1))
    for length in range(len(full) + 1):
        assert Location("table", full[:length]).container_path == full[:length]


def test_a_container_path_holds_segments_and_not_raw_tuples():
    with pytest.raises(MalformedLocation):
        Location("body", (("page", 4),))
