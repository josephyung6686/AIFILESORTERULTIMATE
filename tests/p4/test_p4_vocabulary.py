# tests/p4/test_p4_vocabulary.py
import pytest

from evidence_shape.vocabulary import (
    ANALYSIS_TIERS, COMPLETENESS, EXTRACTOR_RELIABILITY_STATES, INDEXED_SEGMENT_KINDS,
    LABEL_SEGMENT_KINDS, OPEN_QUESTIONS, REGION_UNITS, RELIABILITY_STATES,
    SEGMENT_KINDS, SHAPE_VERSION, SIGNAL_TIERS, SOURCE_TYPES,
    ZERO_OBSERVATION_COMPLETENESS, ZONES, NotInVocabulary, check,
)


def test_the_fifteen_zones_are_the_specs_fifteen_in_order():
    # Every zone is a place the design names as carrying evidence; the SPEC's table
    # carries the § for each. Nothing here is invented and nothing is missing.
    assert ZONES == (
        "filename", "path", "metadata", "title", "heading", "body", "table",
        "header_footer", "notes", "link", "annotation", "reference_list",
        "manifest", "ocr", "transcript",
    )


def test_the_fifteen_segment_kinds_split_into_twelve_indexed_and_three_label():
    # Segment-kind rule 2: an indexed kind is addressed by its index; a
    # label-addressed kind (field | entry | key) has no index.
    assert INDEXED_SEGMENT_KINDS == (
        "page", "slide", "sheet", "heading", "paragraph", "table", "row", "column",
        "cell", "region", "layer", "artboard",
    )
    assert LABEL_SEGMENT_KINDS == ("field", "entry", "key")
    assert SEGMENT_KINDS == INDEXED_SEGMENT_KINDS + LABEL_SEGMENT_KINDS
    assert not set(INDEXED_SEGMENT_KINDS) & set(LABEL_SEGMENT_KINDS)


def test_the_fourteen_source_types_are_2_9s_format_families():
    # D6: taking §2.9's bullet list verbatim avoids inventing a taxonomy.
    assert SOURCE_TYPES == (
        "filesystem", "text_document", "spreadsheet", "presentation", "image", "ocr",
        "email", "calendar", "contacts", "code_structured", "audio_video",
        "design_creative", "archive", "opaque_binary",
    )


def test_reliability_is_3_13s_six_and_extractors_may_write_two_of_them():
    # D11. §3.13 defines six states for file facts; P4 reuses them rather than
    # minting a parallel set (Open question 3), and restricts what an extractor
    # may write to the two that describe a source slot.
    assert RELIABILITY_STATES == (
        "user_confirmed", "direct", "validated", "llm_supported", "possible", "rejected",
    )
    assert EXTRACTOR_RELIABILITY_STATES == ("direct", "possible")
    assert set(EXTRACTOR_RELIABILITY_STATES) < set(RELIABILITY_STATES)


def test_completeness_is_the_nine_values():
    # B1 settled eight; C4 added the ninth on 2026-08-20. None of the eight meant
    # "the bytes are not on this machine": `deferred` is a budget, `unreadable` is
    # damage, `unsupported` is a missing extractor. A dataless file is none of those,
    # so §8.6's progress line could not name the bucket at all.
    assert COMPLETENESS == (
        "complete", "capped", "partial", "metadata_only", "deferred", "unsupported",
        "unreadable", "failed", "dataless",
    )


def test_five_completeness_values_forbid_observations():
    # M3: `unreadable` and `partial` runs DO carry the metadata-level rows §2.9
    # requires -- "recorded as indexed-but-unreadable rather than silently treated
    # as empty". `metadata_only` does NOT: settled 2026-08-20, because rule 9's note
    # and this SPEC's own worked example 19 said opposite things and six extractors
    # would have run the gate. Example 19 is the frozen reading -- the stopping
    # extractor emits nothing and the file stays indexed through its `filesystem`
    # observations. `dataless` joins it (C4): nothing was opened, so nothing was seen.
    assert ZERO_OBSERVATION_COMPLETENESS == (
        "unsupported", "deferred", "failed", "metadata_only", "dataless")
    assert set(ZERO_OBSERVATION_COMPLETENESS) < set(COMPLETENESS)
    for still_allowed in ("unreadable", "partial", "complete", "capped"):
        assert still_allowed not in ZERO_OBSERVATION_COMPLETENESS


def test_the_four_analysis_tiers_are_i4s_four():
    assert ANALYSIS_TIERS == ("filesystem", "native", "ocr", "llm")


def test_analysis_tier_and_source_type_overlap_in_words_and_are_not_one_field():
    # I4: "`source_type` is not the tier." They share two words and mean different
    # things; merging them would lose the distinction between a native PDF run's
    # heading and an OCR run's heading.
    assert set(ANALYSIS_TIERS) & set(SOURCE_TYPES) == {"filesystem", "ocr"}
    assert ANALYSIS_TIERS != SOURCE_TYPES
    assert "native" not in SOURCE_TYPES
    assert "text_document" not in ANALYSIS_TIERS


def test_signal_tier_is_2_6s_three_levels_and_region_units_are_the_specs_two():
    assert SIGNAL_TIERS == (1, 2, 3)
    assert REGION_UNITS == ("px", "norm")


def test_check_rejects_and_never_coerces():
    assert check("heading", ZONES, name="zone") == "heading"
    with pytest.raises(NotInVocabulary):
        check("Heading", ZONES, name="zone")          # no case folding
    with pytest.raises(NotInVocabulary):
        check(" heading", ZONES, name="zone")         # no stripping
    with pytest.raises(NotInVocabulary):
        check("h1", ZONES, name="zone")               # no nearest match
    with pytest.raises(NotInVocabulary):
        check("epub_chapter", ZONES, name="zone")     # D2: an extractor may not add one


def test_every_vocabulary_is_an_immutable_tuple():
    for vocabulary in (ZONES, SEGMENT_KINDS, INDEXED_SEGMENT_KINDS, LABEL_SEGMENT_KINDS,
                       SOURCE_TYPES, RELIABILITY_STATES, EXTRACTOR_RELIABILITY_STATES,
                       COMPLETENESS, ZERO_OBSERVATION_COMPLETENESS, ANALYSIS_TIERS,
                       SIGNAL_TIERS, REGION_UNITS):
        assert isinstance(vocabulary, tuple)


def test_a_shape_version_exists_because_the_contract_says_adding_a_kind_bumps_one():
    # Segment-kind rule 5 and D2 both say a vocabulary addition is "a shape-version
    # bump". A bump needs something to bump.
    assert isinstance(SHAPE_VERSION, int)


def test_the_one_open_question_is_published_and_the_settled_ones_are_gone():
    # OQ1 (the extractor-tier vocabulary) closed as I4; its four values are
    # ANALYSIS_TIERS. The other five are unsettled by the design and stay open.
    assert set(OPEN_QUESTIONS) == {"OQ4"}
    assert "OQ1" not in OPEN_QUESTIONS   # closed as I4
    assert "OQ2" not in OPEN_QUESTIONS   # closed 2026-08-20: the content hash owns
    for question in OPEN_QUESTIONS.values():
        assert question.strip().endswith("?")


def test_open_questions_cannot_be_edited_at_runtime():
    with pytest.raises(TypeError):
        OPEN_QUESTIONS["OQ6"] = "answered"
