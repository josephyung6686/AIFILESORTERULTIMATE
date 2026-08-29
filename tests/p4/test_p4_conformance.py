# tests/p4/test_p4_conformance.py
import pytest

from evidence_shape.conformance import (
    CONFORMANCE_RULES, NonConforming, Violation, check_observation,
    validate_observation,
)
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import MalformedObservation, Observation
from evidence_shape.vocabulary import NotInVocabulary

FIXTURE_1 = dict(
    file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124", extractor_name="pdf.text",
    extractor_version="3.1.0", source_type="text_document", raw_value="BUSIB 4300",
    location=Location("heading", (Segment("page", 1),
                                  Segment("heading", 2, label="Course Information"))),
    occurrence_count=3, observed_at="2026-08-19T14:03:22+00:00", reliability="possible",
    run_id="r1", normalized_value="BUSIB 4300", context_before="Syllabus — ",
    context_after=" — Spring 2026", context_truncated=False,
)


def _mapping(**overrides):
    """Overrides go through the record, so `observation_key` is the key of the row
    that comes back. Rule 1 requires the handle be derivable from the row it names,
    and a helper that changed `raw_value` and left the fixture's key behind would be
    testing itself rather than the rule under test.

    Overrides the record rejects are the deliberately malformed ones. Those are
    applied to the mapping afterwards and the stale key is dropped with them: a
    malformed row has no derivable key, an emitted observation carries none either,
    and rule 1 exempts an absent one.
    """
    try:
        return Observation(**{**FIXTURE_1, **overrides}).to_mapping()
    except (TypeError, MalformedObservation, NotInVocabulary):
        mapping = Observation(**FIXTURE_1).to_mapping()
        mapping.update(overrides)
        mapping.pop("observation_key", None)
        return mapping


def _rules(violations):
    return sorted({violation.rule for violation in violations})


def test_all_twelve_rules_are_published_and_numbered():
    assert sorted(CONFORMANCE_RULES) == list(range(1, 13))
    for text in CONFORMANCE_RULES.values():
        assert text.strip()


def test_a_conforming_observation_passes_and_comes_back_constructed():
    observation = Observation(**FIXTURE_1)
    assert check_observation(observation) == ()
    assert validate_observation(observation) is observation
    assert validate_observation(observation.to_mapping()) == observation


def test_rule_1_a_missing_field_is_reported():
    mapping = _mapping()
    del mapping["occurrence_count"]
    assert 1 in _rules(check_observation(mapping))


def test_rule_1_a_single_surrounding_context_field_fails():
    # M5: three fields, not one, so §8.4 can redact a value without dropping its
    # context or the reverse.
    mapping = _mapping()
    for name in ("context_before", "context_after", "context_truncated"):
        del mapping[name]
    mapping["surrounding_context"] = "Syllabus — BUSIB 4300 — Spring 2026"
    violations = check_observation(mapping)
    assert 1 in _rules(violations)
    assert 6 in _rules(violations)


def test_rule_1_a_null_in_a_non_nullable_field_is_reported():
    assert 1 in _rules(check_observation(_mapping(raw_value=None)))
    assert 1 in _rules(check_observation(_mapping(observed_at=None)))
    # ...and the five nullable ones are fine.
    assert check_observation(_mapping(normalized_value=None, context_before=None,
                                      context_after=None, confidence=None,
                                      signal_tier=None)) == ()


def test_rule_2_a_zone_outside_the_closed_vocabulary_is_reported():
    mapping = _mapping()
    mapping["location"] = {**mapping["location"], "zone": "h1", "locator": "h1"}
    assert 2 in _rules(check_observation(mapping))


def test_rule_2_a_segment_kind_outside_the_closed_vocabulary_is_reported():
    mapping = _mapping()
    mapping["location"] = {"zone": "body",
                           "container_path": [{"kind": "chapter", "index": 2}],
                           "text_span": None, "time_span": None, "region": None}
    assert 2 in _rules(check_observation(mapping))


def test_rule_2_a_source_type_outside_2_9s_families_is_reported():
    assert 2 in _rules(check_observation(_mapping(source_type="pdf")))


def test_rule_3_an_extractor_may_not_write_a_fact_layer_state():
    # D11, and §2.8's "does not treat model output as proof".
    for fact_state in ("validated", "llm_supported", "user_confirmed", "rejected"):
        assert 3 in _rules(check_observation(_mapping(reliability=fact_state)))


def test_rule_3_direct_and_possible_both_pass():
    for allowed in ("direct", "possible"):
        assert check_observation(_mapping(reliability=allowed)) == ()


def test_rule_4_a_locator_that_does_not_round_trip_is_reported():
    mapping = _mapping()
    mapping["location"] = {**mapping["location"], "locator": "title:page=1"}
    assert 4 in _rules(check_observation(mapping))


def test_rule_4_holds_for_a_label_that_needed_escaping():
    member = "docs/2026=final#draft/提出書類.pdf"
    observation = Observation(**{**FIXTURE_1, "source_type": "archive",
                                 "reliability": "direct", "raw_value": member,
                                 "location": Location(
                                     "manifest", (Segment("entry", label=member),))})
    assert check_observation(observation) == ()
    assert observation.locator.startswith("manifest:entry=")


def test_rule_6_a_destination_domain_group_node_or_plan_reference_is_reported():
    # §2.8: "Extraction does not create a final folder path, invent domains, merge
    # all files that share one string, or treat model output as proof."
    for forbidden in ("proposed_path", "destination_node", "domain", "field_name",
                      "group_id", "node_id", "template_id", "plan_version_id"):
        assert 6 in _rules(check_observation(_mapping(**{forbidden: "x"})))


def test_rule_6_an_observation_references_exactly_one_file():
    # "There is no multi-file observation, and two files sharing a raw value share
    # nothing structurally -- that link, if any, is P6's or P9's."
    assert 6 in _rules(check_observation(_mapping(file_id=["f1", "f2"])))


def test_rule_7_an_occurrence_count_below_one_is_reported():
    for absent in (0, -1):
        assert 7 in _rules(check_observation(_mapping(occurrence_count=absent)))


def test_rule_11_a_signal_tier_outside_2_6s_three_levels_is_reported():
    image = _mapping(source_type="image", reliability="direct",
                     raw_value="2026:07:17 14:03:22")
    assert 11 in _rules(check_observation({**image, "signal_tier": 4}))
    assert 11 in _rules(check_observation({**image, "signal_tier": 0}))


def test_rule_11_a_signal_tier_outside_2_6s_image_hierarchy_is_reported():
    # §2.6's hierarchy is entirely about images. The field is "null on every
    # observation outside §2.6's image hierarchy".
    assert 11 in _rules(check_observation(_mapping(signal_tier=1)))
    assert 11 in _rules(check_observation(
        _mapping(source_type="ocr", signal_tier=2)))


def test_rule_11_all_three_tiers_pass_on_an_image_observation():
    for tier in (1, 2, 3):
        assert check_observation(_mapping(
            source_type="image", reliability="direct",
            raw_value="2026:07:17 14:03:22", signal_tier=tier)) == ()


def test_rule_12_a_conflict_pair_in_one_row_is_reported():
    # §2.6's conflicting signals are TWO observations with two signal_tier values,
    # never a third "conflict" row. An observation is a reading, not a comparison of
    # readings.
    assert 12 in _rules(check_observation(
        _mapping(raw_value=["Canon EOS R6", "1920x1080"])))


def test_rule_12_two_locations_in_one_row_are_reported():
    mapping = _mapping()
    mapping["location"] = [mapping["location"], mapping["location"]]
    assert 12 in _rules(check_observation(mapping))


def test_rule_12_states_the_half_p4_cannot_check():
    # An absence written INSIDE raw_value as a string is undetectable without a list
    # of forbidden strings, and authoring one would be inventing a vocabulary. P5
    # carries that obligation; M2 already moved "no EXIF" onto extraction_runs.
    assert "P5" in CONFORMANCE_RULES[12]


def test_the_validator_reports_every_violation_before_raising():
    mapping = _mapping(reliability="validated", occurrence_count=0,
                       source_type="pdf")
    violations = check_observation(mapping)
    assert {2, 3, 7} <= set(_rules(violations))
    with pytest.raises(NonConforming) as raised:
        validate_observation(mapping)
    assert len(raised.value.violations) == len(violations)


def test_the_validator_fails_rather_than_coercing():
    # Done-means 2. Nothing comes back repaired.
    with pytest.raises(NonConforming):
        validate_observation(_mapping(reliability="VALIDATED"))
    with pytest.raises(NonConforming):
        validate_observation(_mapping(source_type="Text_Document"))


def test_a_violation_names_its_rule_and_says_something_useful():
    violation = check_observation(_mapping(reliability="llm_supported"))[0]
    assert isinstance(violation, Violation)
    assert violation.rule == 3
    assert "llm_supported" in violation.message
