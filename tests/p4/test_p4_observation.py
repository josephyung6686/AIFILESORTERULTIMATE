# tests/p4/test_p4_observation.py
import pytest

from database_agent.supersede import SUPERSEDE_COLUMNS

from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import (
    ADDED_FIELDS, MalformedObservation, NULLABLE_FIELDS, OBSERVATION_FIELDS,
    OBSERVATION_ROW_FIELDS, Observation, SECTION_2_8_FIELDS, SECTION_2_8_LINES,
    collapse_key, observation_from_mapping, observation_key,
)
from evidence_shape.vocabulary import NotInVocabulary

#: SPEC fixture 1: §2.8's "page 1, heading 2", which is also §3.2's worked syllabus
#: and the walking skeleton's one observation.
FIXTURE_1 = dict(
    file_id="f1", content_hash="sha256:abc", extractor_name="pdf.text",
    extractor_version="3.1.0", source_type="text_document", raw_value="BUSIB 4300",
    location=Location("heading", (Segment("page", 1),
                                  Segment("heading", 2, label="Course Information"))),
    occurrence_count=3, observed_at="2026-08-19T14:03:22+00:00", reliability="possible",
    run_id="r1", normalized_value="BUSIB 4300", context_before="Syllabus — ",
    context_after=" — Spring 2026", context_truncated=False,
)


def test_2_8s_eleven_lines_become_fourteen_field_names():
    # MINOR 1's counting discipline: §2.8 prints eleven lines. "Extractor name and
    # version" is one line and two fields; "Surrounding context" is one line and,
    # under M5, three fields -- of which two are §2.8's and `context_truncated` is
    # §8.6's addition.
    assert len(SECTION_2_8_LINES) == 11
    assert len(SECTION_2_8_FIELDS) == 13
    assert "context_before" in SECTION_2_8_FIELDS
    assert "context_after" in SECTION_2_8_FIELDS
    assert "context_truncated" in ADDED_FIELDS
    assert "surrounding_context" not in OBSERVATION_ROW_FIELDS


def test_the_emitted_field_set_and_the_row_field_set_partition_cleanly():
    assert set(SECTION_2_8_FIELDS) | set(ADDED_FIELDS) == set(OBSERVATION_ROW_FIELDS)
    assert not set(SECTION_2_8_FIELDS) & set(ADDED_FIELDS)
    assert len(OBSERVATION_FIELDS) == 18
    assert len(OBSERVATION_ROW_FIELDS) == 22


def test_the_row_adds_exactly_the_id_and_p1s_three_supersede_columns():
    # M1: P1 publishes the set; P4 adopts three of the four. `preferred` is the one
    # P4 does not take -- §8.2 gives preference to the resolver and §3.2 places the
    # resolver after extraction, so it lives on P6's `file_facts`.
    assert set(OBSERVATION_ROW_FIELDS) - set(OBSERVATION_FIELDS) == \
        {"observation_id", *SUPERSEDE_COLUMNS}
    assert SUPERSEDE_COLUMNS == ("supersedes", "superseded_by", "supersede_reason")
    assert "preferred" not in OBSERVATION_ROW_FIELDS


def test_minor_3s_spelling_is_the_one_that_survived():
    assert "supersede_reason" in OBSERVATION_ROW_FIELDS
    assert "supersession_reason" not in OBSERVATION_ROW_FIELDS


def test_only_five_fields_are_nullable():
    assert NULLABLE_FIELDS == frozenset(
        {"normalized_value", "context_before", "context_after", "confidence",
         "signal_tier"})
    assert "raw_value" not in NULLABLE_FIELDS
    assert "location" not in NULLABLE_FIELDS


def test_fixture_1_builds_and_carries_its_locator():
    observation = Observation(**FIXTURE_1)
    assert observation.locator == "heading:page=1/heading=2"
    assert observation.zone == "heading"
    assert observation.observation_key.startswith("sha256:")


def test_the_key_is_stable_across_extractor_versions():
    # MINOR 8, stated in one sentence so nobody "fixes" it into a bug: P4 excludes
    # `extractor_version` from `observation_key` SO THAT §8.5's replay diff across
    # extractor versions has something to diff against.
    first = Observation(**FIXTURE_1)
    upgraded = Observation(**{**FIXTURE_1, "extractor_version": "4.0.0"})
    assert first.observation_key == upgraded.observation_key
    assert first.extractor_version != upgraded.extractor_version


def test_the_key_moves_when_any_of_its_four_inputs_moves():
    first = Observation(**FIXTURE_1)
    for changed in ({"raw_value": "BUSIB 4301"},
                    {"content_hash": "sha256:def"},
                    {"extractor_name": "ocr.apple_vision"},
                    {"location": Location("body", (Segment("page", 1),))}):
        assert Observation(**{**FIXTURE_1, **changed}).observation_key != \
            first.observation_key


def test_the_key_function_takes_the_four_inputs_the_spec_names():
    observation = Observation(**FIXTURE_1)
    assert observation_key(content_hash="sha256:abc", extractor_name="pdf.text",
                           locator="heading:page=1/heading=2",
                           raw_value="BUSIB 4300") == observation.observation_key


def test_the_key_is_not_the_row_id():
    # M14: `observation_id` is per-row and dies on extractor upgrade; §8.7 requires a
    # negative example recorded today to still resolve after that upgrade.
    assert "observation_id" not in OBSERVATION_FIELDS
    assert "observation_key" in OBSERVATION_FIELDS


def test_the_mapping_form_round_trips_in_the_specs_field_order():
    observation = Observation(**FIXTURE_1)
    mapping = observation.to_mapping()
    assert list(mapping) == list(OBSERVATION_FIELDS)
    assert observation_from_mapping(mapping) == observation


def test_a_single_surrounding_context_field_fails_conformance_rule_1():
    # M5: a consumer or extractor author reproducing §2.8's list must name P4's three
    # fields, not one. §8.4 must be able to redact a value without dropping its
    # context, or the reverse.
    mapping = Observation(**FIXTURE_1).to_mapping()
    collapsed = {name: value for name, value in mapping.items()
                 if name not in ("context_before", "context_after", "context_truncated")}
    collapsed["surrounding_context"] = "Syllabus — BUSIB 4300 — Spring 2026"
    with pytest.raises(MalformedObservation):
        observation_from_mapping(collapsed)


def test_an_extractor_may_write_two_reliability_states_and_no_other():
    # D11. The other four are fact-layer outcomes (§3.5); §2.8 forbids extraction
    # from treating model output as proof.
    assert Observation(**{**FIXTURE_1, "reliability": "direct"}).reliability == "direct"
    for fact_state in ("validated", "llm_supported", "user_confirmed", "rejected"):
        with pytest.raises(NotInVocabulary):
            Observation(**{**FIXTURE_1, "reliability": fact_state})


def test_the_location_is_the_structured_record_and_never_a_string():
    # P5 OQ1, closed: §2.8's per-source-type examples cannot be expressed by a string.
    with pytest.raises(MalformedObservation):
        Observation(**{**FIXTURE_1, "location": "page 1, heading 2"})


def test_occurrence_count_is_at_least_one():
    # Conformance rule 7. An observation records presence; a count of zero is an
    # absence, and absence lives on the run record or nowhere (§2.6).
    assert Observation(**{**FIXTURE_1, "occurrence_count": 1}).occurrence_count == 1
    for absent in (0, -1):
        with pytest.raises(MalformedObservation):
            Observation(**{**FIXTURE_1, "occurrence_count": absent})


def test_raw_value_is_never_empty():
    with pytest.raises(MalformedObservation):
        Observation(**{**FIXTURE_1, "raw_value": ""})


def test_normalized_value_may_always_be_null():
    # RAW-3: an extractor that cannot normalize safely leaves it null rather than
    # guessing (§3.10 forbids fuzzy date parsing).
    assert Observation(**{**FIXTURE_1, "normalized_value": None}).normalized_value is None


def test_signal_tier_is_2_6s_three_levels_or_null():
    for tier in (1, 2, 3, None):
        assert Observation(**{**FIXTURE_1, "signal_tier": tier}).signal_tier == tier
    with pytest.raises(NotInVocabulary):
        Observation(**{**FIXTURE_1, "signal_tier": 4})


def test_confidence_carries_no_range_because_2_7_names_no_scale():
    # §3.13: the number is "not comparable across extractors". A range invented here
    # would silently rescale one provider's numbers into another's.
    for value in (0.92, 0, 1, 87, None):
        assert Observation(**{**FIXTURE_1, "confidence": value}).confidence == value


def test_the_record_refuses_a_field_it_does_not_publish():
    # Conformance rule 6's structural half: no destination, domain, field name,
    # group, node, template or plan reference can be attached, because the record is
    # a closed field set and an unknown key is a rejection.
    mapping = Observation(**FIXTURE_1).to_mapping()
    for forbidden in ("proposed_path", "domain", "field_name", "group_id", "node_id",
                      "template_id", "plan_version_id", "handling_class"):
        with pytest.raises(MalformedObservation):
            observation_from_mapping({**mapping, forbidden: "x"})


def test_a_stored_key_that_does_not_match_its_observation_is_rejected():
    mapping = Observation(**FIXTURE_1).to_mapping()
    with pytest.raises(MalformedObservation):
        observation_from_mapping({**mapping, "observation_key": "sha256:0"})


def test_an_observation_is_frozen():
    # RAW-2: `raw_value` is never updated, ever. Improvement is insert + supersede.
    observation = Observation(**FIXTURE_1)
    with pytest.raises(Exception):
        observation.raw_value = "BUSIB 4301"


def test_the_same_value_in_two_zones_is_two_observations_with_two_counts():
    # D10, and the reason §2.2's rule works at all: a page-one heading outweighs a
    # page-eighteen reference list, which is only expressible if they are two rows.
    heading = Observation(**{**FIXTURE_1, "raw_value": "Columbia"})
    body = Observation(**{**FIXTURE_1, "raw_value": "Columbia",
                          "location": Location("body", (Segment("page", 18),),
                                               text_span=TextSpan(12043, 12051))})
    assert collapse_key(heading) == ("r1", "Columbia", "heading")
    assert collapse_key(body) == ("r1", "Columbia", "body")
    assert collapse_key(heading) != collapse_key(body)


def test_collapsing_is_on_exact_raw_match_because_p4_judges_no_normalization():
    # `Columbia` and `columbia` are two observations. Cross-form aggregation is P6's
    # (§3.7 word-boundary matching and ranking).
    upper = Observation(**{**FIXTURE_1, "raw_value": "Columbia"})
    lower = Observation(**{**FIXTURE_1, "raw_value": "columbia"})
    assert collapse_key(upper) != collapse_key(lower)
    assert upper.observation_key != lower.observation_key
