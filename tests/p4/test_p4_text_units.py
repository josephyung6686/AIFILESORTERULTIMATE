# tests/p4/test_p4_text_units.py
import pytest

from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.text_units import (
    MalformedTextUnit, SpanAnchorError, TEXT_UNIT_FIELDS, TextUnit, check_span_anchor,
    raw_value_at, text_unit_from_mapping,
)

PAGE_ONE = "Syllabus — BUSIB 4300 — Spring 2026"


def _observation(**overrides):
    payload = dict(
        file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124", extractor_name="pdf.text",
        extractor_version="3.1.0", source_type="text_document",
        raw_value="BUSIB 4300",
        location=Location("heading", (Segment("page", 1),),
                          text_span=TextSpan(11, 21)),
        occurrence_count=1, observed_at="2026-08-19T14:03:22+00:00",
        reliability="possible", run_id="r1",
    )
    payload.update(overrides)
    return Observation(**payload)


def test_the_record_carries_the_specs_six_fields_in_order():
    assert TEXT_UNIT_FIELDS == (
        "run_id", "container_path", "unit_locator", "text", "length", "truncated")


def test_a_per_page_unit_addresses_itself_with_the_same_vocabulary_the_observation_uses():
    # §2.2 "complete text by page": one row per page.
    unit = TextUnit(run_id="r1", container_path=(Segment("page", 4),), text="…")
    assert unit.unit_locator == "page=4"
    assert unit.container_path == (Segment("page", 4),)


def test_a_whole_file_unit_has_an_empty_path_and_an_empty_locator():
    # §2.4: the full text of a text-bearing file is one row, container_path: [].
    unit = TextUnit(run_id="r1", container_path=(), text="hello")
    assert unit.container_path == ()
    assert unit.unit_locator == ""


def test_a_per_region_ocr_unit_nests_page_and_region():
    # §2.7 "raw recognized text": one row per OCR page or region.
    unit = TextUnit(run_id="r1",
                    container_path=(Segment("page", 4), Segment("region", 2)),
                    text="Your Columbia University")
    assert unit.unit_locator == "page=4/region=2"


def test_length_is_the_stored_length_in_code_points():
    # D4, and rule 5: "`length` is the stored length".
    unit = TextUnit(run_id="r1", container_path=(), text=PAGE_ONE)
    assert unit.length == len(PAGE_ONE)


def test_raw_1_holds_on_the_walking_skeletons_own_fixture():
    # RAW-1: raw_value is byte-for-byte the substring of the stored text unit at that
    # span. This is the anchor for every citation check in §3.6, §4.8, §6.10, §7.9.
    unit = TextUnit(run_id="r1", container_path=(Segment("page", 1),), text=PAGE_ONE)
    observation = _observation()
    assert raw_value_at(unit, observation.location.text_span) == "BUSIB 4300"
    check_span_anchor(observation, unit)


def test_raw_1_holds_on_cjk_where_a_byte_offset_would_not():
    # Done-means 4, and §2.7's CJK requirement. Code points, not bytes.
    text = "課程 BUSIB 4300 春季"
    start, end = 3, 13
    assert text[start:end] == "BUSIB 4300"
    assert len(text.encode("utf-8")) != len(text)      # bytes would disagree
    unit = TextUnit(run_id="r1", container_path=(Segment("page", 1),), text=text)
    check_span_anchor(_observation(location=Location(
        "heading", (Segment("page", 1),), text_span=TextSpan(start, end))), unit)


def test_raw_1_holds_on_an_astral_emoji_where_a_utf_16_offset_would_not():
    # Done-means 4. An astral-plane emoji is ONE code point and TWO UTF-16 units, so
    # a UTF-16 offset would land one short from here on.
    text = "\U0001F600 BUSIB 4300"
    assert len(text) == 12 and len(text.encode("utf-16-le")) // 2 == 13
    unit = TextUnit(run_id="r1", container_path=(Segment("page", 1),), text=text)
    check_span_anchor(_observation(location=Location(
        "heading", (Segment("page", 1),), text_span=TextSpan(2, 12))), unit)


def test_the_anchor_fails_when_the_span_names_different_text():
    unit = TextUnit(run_id="r1", container_path=(Segment("page", 1),), text=PAGE_ONE)
    with pytest.raises(SpanAnchorError):
        check_span_anchor(_observation(raw_value="BUSIB 4301"), unit)


def test_the_anchor_fails_when_the_unit_belongs_to_another_run():
    # Rule 4: text is per run, not per file. A text-layer pass and an OCR pass over
    # the same PDF produce two different texts under two run_ids (§8.2).
    other = TextUnit(run_id="r2", container_path=(Segment("page", 1),), text=PAGE_ONE)
    with pytest.raises(SpanAnchorError):
        check_span_anchor(_observation(), other)


def test_the_anchor_fails_when_the_units_path_is_not_the_observations_path():
    # Rule 10: the unit's container_path must EQUAL the observation's.
    coarser = TextUnit(run_id="r1", container_path=(), text=PAGE_ONE)
    with pytest.raises(SpanAnchorError):
        check_span_anchor(_observation(), coarser)


def test_the_anchor_refuses_an_observation_with_no_span():
    # Rule 10 is scoped to a non-null text_span; a metadata observation has none and
    # is not a rule-10 case at all.
    metadata = _observation(
        location=Location("metadata", (Segment("field", label="Producer"),)),
        raw_value="python-docx", reliability="direct")
    unit = TextUnit(run_id="r1", container_path=(Segment("page", 1),), text=PAGE_ONE)
    with pytest.raises(SpanAnchorError):
        check_span_anchor(metadata, unit)


def test_a_span_beyond_a_truncated_prefix_fails_rather_than_returning_short_text():
    # Rule 5: "an observation whose span lies beyond it is not written." If one is,
    # the anchor says so -- §8.6 forbids a silent truncation that removes evidence.
    cut = TextUnit(run_id="r1", container_path=(Segment("page", 1),),
                   text=PAGE_ONE[:15], truncated=True)
    assert cut.truncated is True
    assert cut.length == 15
    with pytest.raises(SpanAnchorError):
        check_span_anchor(_observation(), cut)


def test_a_span_inside_a_truncated_prefix_is_still_valid():
    # Rule 5: "A truncated unit invalidates no observation whose span lies inside the
    # stored prefix."
    cut = TextUnit(run_id="r1", container_path=(Segment("page", 1),),
                   text=PAGE_ONE[:21], truncated=True)
    check_span_anchor(_observation(), cut)


def test_context_may_cross_the_unit_boundary():
    # Rule 3, and D9's reason for storing context beside raw_value rather than as
    # offsets: a heading at the top of page 4 has context that came from page 3.
    unit = TextUnit(run_id="r1", container_path=(Segment("page", 4),),
                    text="BUSIB 4300 Syllabus")
    observation = _observation(
        location=Location("heading", (Segment("page", 4),), text_span=TextSpan(0, 10)),
        context_before="…continued from page 3. ", context_after=" — Spring 2026")
    check_span_anchor(observation, unit)
    assert observation.context_before not in unit.text
    assert observation.context_after not in unit.text


def test_truncated_defaults_to_false_and_is_always_a_bool():
    assert TextUnit(run_id="r1", container_path=(), text="x").truncated is False
    with pytest.raises(MalformedTextUnit):
        TextUnit(run_id="r1", container_path=(), text="x", truncated=None)


def test_an_empty_unit_is_well_formed_because_a_page_may_carry_no_text():
    # §2.2 requires complete text by page; a blank page is a page.
    unit = TextUnit(run_id="r1", container_path=(Segment("page", 9),), text="")
    assert unit.length == 0


def test_the_mapping_form_round_trips():
    unit = TextUnit(run_id="r1", container_path=(Segment("page", 4), Segment("region", 2)),
                    text="Your Columbia University", truncated=False)
    mapping = unit.to_mapping()
    assert list(mapping) == list(TEXT_UNIT_FIELDS)
    assert mapping["unit_locator"] == "page=4/region=2"
    assert mapping["container_path"] == [{"kind": "page", "index": 4},
                                         {"kind": "region", "index": 2}]
    assert text_unit_from_mapping(mapping) == unit


def test_the_mapping_form_rejects_a_field_the_record_does_not_publish():
    mapping = TextUnit(run_id="r1", container_path=(), text="x").to_mapping()
    for forbidden in ("file_id", "handling_class", "plan_version_id", "sent_to_model"):
        with pytest.raises(MalformedTextUnit):
            text_unit_from_mapping({**mapping, forbidden: "x"})


def test_a_stored_unit_locator_that_does_not_match_its_path_is_rejected():
    mapping = TextUnit(run_id="r1", container_path=(Segment("page", 4),),
                       text="x").to_mapping()
    with pytest.raises(MalformedTextUnit):
        text_unit_from_mapping({**mapping, "unit_locator": "page=9"})


def test_a_text_unit_is_frozen():
    unit = TextUnit(run_id="r1", container_path=(), text="x")
    with pytest.raises(Exception):
        unit.text = "y"
