# tests/p4/test_p4_locator.py
import pytest

from evidence_shape.location import (
    Location, MalformedLocation, Region, Segment, TextSpan, TimeSpan,
)
from evidence_shape.locator import (
    MalformedLocator, addressing, escape_label, location_from_mapping,
    location_to_mapping, parse_container_path, parse_locator,
    serialize_container_path, serialize_locator, unescape_label,
)
from evidence_shape.vocabulary import NotInVocabulary

#: The SPEC's own worked locators, plus the four zones its nineteen fixtures do not
#: reach. Every one of these round-trips; none of them is invented syntax.
GOLDEN_LOCATORS = (
    "filename",                                 # the filename itself
    "filename#0-6",                             # first six code points of the filename
    "path",                                     # §2.9 parent-folder context
    "title:page=1",                             # the document title
    "heading:page=1/heading=2",                 # §2.8's "page 1, heading 2"
    "heading:page=1/heading=1",                 # §2.3's Wash U.docx heading
    "table:page=4/table=3/row=2/column=1",      # §2.8's "table 3, row 2, column 1"
    "table:sheet=2/row=7/column=3",             # a spreadsheet cell
    "metadata:field=DateTimeOriginal",          # §2.8's EXIF example
    "metadata:field=dc%3Atitle",                # colon escaped
    "metadata:field=Producer",                  # §2.2's tool-generated producer
    "metadata:field=Subject",                   # §2.9 email
    "metadata:field=DTSTART",                   # §2.9 calendar
    "metadata:key=dependencies/field=name",     # §2.9 package manifests
    "metadata:layer=3",                         # §2.9 design/creative
    "manifest:entry=docs%2Ftranscript.pdf",     # §2.8's "a manifest path"
    "manifest:field=file_count",                # §2.5's "file count"
    "ocr:page=4/region=2#0-24",                 # §2.8's "an OCR region"
    "body:page=18#12043-12051",                 # §2.2's page-eighteen reference
    "notes:slide=6#0-42",                       # §2.9 presentations
    "transcript@252500-255200",                 # a caption at 04:12.5-04:15.2
    "link:page=1#40-72",                        # §2.2, §2.3 URLs and email addresses
    "annotation:page=2#0-18",                   # §2.3 comments and revision metadata
    "header_footer:page=1#0-24",                # §2.3, §3.7 "a footer"
    "reference_list:page=18#12000-12100",       # §2.2's reference list
)


@pytest.mark.parametrize("locator", GOLDEN_LOCATORS)
def test_every_golden_locator_round_trips(locator):
    # Conformance rule 4: "`locator` round-trips: serialize -> parse -> structurally
    # equal." Asserted here in the other direction too, which is the one that
    # catches a serializer that silently reorders or drops a segment.
    assert serialize_locator(parse_locator(locator)) == locator


@pytest.mark.parametrize("locator", GOLDEN_LOCATORS)
def test_every_golden_locator_survives_the_mapping_form(locator):
    location = parse_locator(locator)
    assert location_from_mapping(location_to_mapping(location)) == location
    assert location_to_mapping(location)["locator"] == locator


def test_2_8s_pdf_example_serializes_to_2_8s_own_words():
    location = Location("heading",
                        (Segment("page", 1), Segment("heading", 2, label="Course Information")))
    assert serialize_locator(location) == "heading:page=1/heading=2"


def test_addressing_is_what_a_round_trip_reproduces():
    # Conformance rule 4 is written against this projection, because rule 2 keeps a
    # descriptive label out of the string and the grammar has no term for a bounding
    # box. Round-tripping the full record would fail on both, correctly.
    full = Location("heading",
                    (Segment("page", 1), Segment("heading", 2, label="Course Information")),
                    text_span=TextSpan(0, 10), region=Region(1, 2, 3, 4, "px"))
    projected = addressing(full)
    assert projected == Location("heading", (Segment("page", 1), Segment("heading", 2)),
                                 text_span=TextSpan(0, 10))
    assert parse_locator(serialize_locator(full)) == projected
    assert addressing(projected) == projected


def test_addressing_keeps_the_label_on_a_label_addressed_kind():
    # `field`, `entry` and `key` ARE addressed by their label, so it is not
    # descriptive and it does appear in the locator.
    labelled = Location("metadata", (Segment("field", label="DateTimeOriginal"),))
    assert addressing(labelled) == labelled
    assert parse_locator(serialize_locator(labelled)) == labelled


def test_a_descriptive_label_never_appears_in_the_locator():
    # Segment-kind rule 2: "A kind with an index is addressed by its index; its label
    # is descriptive only and never appears in the locator."
    with_label = Location("table", (Segment("sheet", 2), Segment("row", 7),
                                    Segment("column", 3, label="C7")))
    without = Location("table", (Segment("sheet", 2), Segment("row", 7),
                                 Segment("column", 3)))
    assert serialize_locator(with_label) == serialize_locator(without)
    assert "C7" not in serialize_locator(with_label)


def test_the_bounding_box_never_appears_in_the_locator():
    # The grammar has no term for `region: {x, y, w, h, unit}`. Two OCR readings of
    # one raw value in one region path are one observation (D10), not two.
    boxed = Location("ocr", (Segment("page", 4), Segment("region", 2)),
                     text_span=TextSpan(0, 24), region=Region(12, 40, 300, 22, "px"))
    unboxed = Location("ocr", (Segment("page", 4), Segment("region", 2)),
                       text_span=TextSpan(0, 24))
    assert serialize_locator(boxed) == serialize_locator(unboxed) == "ocr:page=4/region=2#0-24"
    assert location_from_mapping(location_to_mapping(boxed)) == boxed


def test_an_archive_member_path_escapes_its_slashes_and_keeps_its_non_ascii():
    # Done-means 3: "a passing escaping test on an archive path containing `/`, `=`,
    # `#` and a non-ASCII segment". The escaping exists because §2.8's own example is
    # a manifest path, and paths contain `/`.
    member = "docs/2026=final#draft/提出書類.pdf"
    location = Location("manifest", (Segment("entry", label=member),))
    serialized = serialize_locator(location)

    assert serialized.split(":", 1)[1].count("/") == 0     # no segment boundary forged
    assert "#" not in serialized                           # no span marker forged
    assert "=" in serialized.split(":", 1)[1][:6]          # only the one addr marker
    assert "提" in serialized                          # non-ASCII stays literal
    assert parse_locator(serialized) == location
    assert parse_locator(serialized).container_path[0].label == member


def test_escaping_covers_every_reserved_character_and_control_characters():
    for reserved in ("%", "/", "=", "#", "@", ":"):
        assert unescape_label(escape_label(reserved)) == reserved
    for reserved in ("/", "=", "#", "@", ":"):
        # `%` is excluded from this half on purpose: its own escape is `%25`, which
        # necessarily contains it. That is the escape marker, not an unescaped char.
        assert reserved not in escape_label(reserved)
    tab = chr(9)
    assert tab not in escape_label(f"a{tab}b")
    assert unescape_label(escape_label(f"a{tab}b")) == f"a{tab}b"


def test_escapes_are_uppercase_hex_over_utf_8_bytes():
    assert escape_label(":") == "%3A"
    assert escape_label("/") == "%2F"
    assert escape_label("%") == "%25"
    assert escape_label("é") == "é"              # not reserved; not escaped


def test_an_emoji_label_round_trips_unescaped():
    location = Location("metadata", (Segment("field", label="Title \U0001F600"),))
    assert parse_locator(serialize_locator(location)) == location


def test_a_container_path_serializes_without_a_zone_prefix():
    # This is the form `text_units.unit_locator` carries (Task 7): the unit's address
    # is a container path, not a located value, so it has no zone.
    path = (Segment("page", 4), Segment("region", 2))
    assert serialize_container_path(path) == "page=4/region=2"
    assert parse_container_path("page=4/region=2") == path
    assert serialize_container_path(()) == ""
    assert parse_container_path("") == ()


def test_parsing_rejects_and_never_repairs():
    for malformed in ("", "heading:", "heading:page", "heading:page=x",
                      "heading:page=1#a-b", "heading:page=1#5",
                      "heading:page=1#0-10@0-10", "metadata:field=%zz",
                      "metadata:field=%2"):
        with pytest.raises((MalformedLocator, MalformedLocation)):
            parse_locator(malformed)


def test_parsing_rejects_a_zone_or_kind_outside_the_closed_vocabulary():
    with pytest.raises(NotInVocabulary):
        parse_locator("h1:page=1")
    with pytest.raises(NotInVocabulary):
        parse_locator("body:chapter=1")


def test_parsing_rejects_a_zero_index_because_indices_are_1_based():
    with pytest.raises(MalformedLocation):
        parse_locator("heading:page=0")


def test_a_locator_carries_one_span_or_the_other_never_both():
    with pytest.raises(MalformedLocator):
        parse_locator("transcript:page=1#0-4@0-10")


def test_the_mapping_form_rejects_a_locator_that_does_not_match_its_fields():
    # The string is redundant with the structured fields by construction. A stored
    # record whose two halves disagree is unusable for a citation check (§3.6, §4.8).
    with pytest.raises(MalformedLocation):
        location_from_mapping({"zone": "body", "container_path": [], "locator": "title"})


def test_the_mapping_form_rejects_an_unknown_field():
    with pytest.raises(MalformedLocation):
        location_from_mapping({"zone": "body", "page_number": 4})
