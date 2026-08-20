# tests/p5/test_p5_shape.py
"""P4's shape, built by P5. Conformance rules 1, 2, 3, 4, 6, 7, 10, 11."""
import pytest

from extractors.shape import (
    ANALYSIS_TIERS, EXTRACTOR_RELIABILITY, LOCATION_FIELDS, OBSERVATION_FIELDS,
    P5_ANALYSIS_TIERS, RUN_FIELDS, TEXT_UNIT_FIELDS, ForbiddenAnalysisTier,
    ForbiddenReliability, canonical_json, context_for, fingerprint,
    location, normalize_mechanical, observation, run, segment, text_unit,
)
from extractors.sink import ExtractionResult

from p4_stub import locator_for, parse_locator, validate_observation

NOW = "2026-08-19T12:00:00+00:00"


def an_observation(**overrides):
    fields = dict(
        file_id="f1", content_hash="sha256:abc", extractor_name="pdf.text",
        extractor_version="0.1.0", source_type="text_document",
        raw_value="BUSIB 4300",
        location=location(zone="heading",
                          container_path=(segment("page", index=1),
                                          segment("heading", index=2,
                                                  label="Course Information")),
                          text_span={"start": 0, "end": 10}),
        observed_at=NOW, reliability="possible",
    )
    fields.update(overrides)
    return observation(**fields)


def test_the_observation_carries_every_2_8_field_and_no_extractor_private_one():
    # P4 conformance rule 1. The field list is P4's, in P4's order.
    obs = an_observation()
    assert tuple(obs) == OBSERVATION_FIELDS
    assert OBSERVATION_FIELDS == (
        "file_id", "content_hash", "extractor_name", "extractor_version",
        "source_type", "raw_value", "normalized_value", "location",
        "context_before", "context_after", "context_truncated",
        "occurrence_count", "observed_at", "reliability",
        "confidence", "signal_tier",
    )


def test_surrounding_context_is_three_fields_and_never_one():
    # M5: "P5, P6, P8, P9 and P11 correct their reproduced field lists to name P4's
    # three fields instead of §2.8's single 'surrounding context' line." §8.4 must be
    # able to redact a value without dropping its context.
    obs = an_observation()
    assert "context_before" in obs and "context_after" in obs
    assert "context_truncated" in obs
    assert "surrounding_context" not in obs
    assert "context" not in obs


def test_location_is_the_structured_record_and_never_a_string():
    # P5 OQ1 is CLOSED (04-resolutions.md): "Yes — P4's structured record plus the
    # canonical locator." §2.8's per-source-type examples cannot be a string.
    obs = an_observation()
    assert isinstance(obs["location"], dict)
    assert tuple(obs["location"]) == LOCATION_FIELDS == (
        "zone", "container_path", "text_span", "time_span", "region")


def test_p5_supplies_the_structured_fields_and_p4_derives_the_locator():
    # The locator is redundant with the structured fields by construction, so P5
    # emits no `locator` key: one serialization, one implementation (P4's).
    obs = an_observation()
    assert "locator" not in obs["location"]
    assert locator_for(obs["location"]) == "heading:page=1/heading=2#0-10"
    assert parse_locator("heading:page=1/heading=2#0-10")["zone"] == "heading"


def test_an_extractor_may_write_only_direct_and_possible():
    # P4 D11, conformance rule 3. The other four are fact-layer outcomes (§3.5).
    assert EXTRACTOR_RELIABILITY == ("direct", "possible")
    for forbidden in ("validated", "llm_supported", "user_confirmed", "rejected"):
        with pytest.raises(ForbiddenReliability):
            an_observation(reliability=forbidden)


def test_occurrence_count_is_at_least_one():
    # P4 conformance rule 7.
    assert an_observation()["occurrence_count"] == 1
    with pytest.raises(ValueError):
        an_observation(occurrence_count=0)


def test_signal_tier_is_null_by_default_and_only_ever_one_two_or_three():
    # P4: "null on every observation outside §2.6's image hierarchy"; rule 11.
    assert an_observation()["signal_tier"] is None
    for tier in (1, 2, 3):
        assert an_observation(signal_tier=tier)["signal_tier"] == tier
    for bad in (0, 4, "1"):
        with pytest.raises(ValueError):
            an_observation(signal_tier=bad)


def test_the_observation_carries_no_destination_domain_group_or_plan_reference():
    # P4 conformance rule 6; §2.8's prohibitions.
    obs = an_observation()
    for forbidden in ("path_proposal", "destination", "destination_node", "domain",
                      "category", "field_name", "group_id", "node_id", "template_id",
                      "plan_version", "handling_class", "sensitivity_state",
                      "preferred"):
        assert forbidden not in obs


def test_container_path_indices_are_one_based_and_a_label_kind_has_no_index():
    # P4 D3 and segment-kind rule 2.
    assert segment("page", index=1) == {"kind": "page", "index": 1, "label": None}
    assert segment("field", label="Producer") == {"kind": "field", "index": None,
                                                  "label": "Producer"}
    with pytest.raises(ValueError):
        segment("page", index=0)
    with pytest.raises(ValueError):
        segment("page")
    with pytest.raises(ValueError):
        segment("field", index=1)


def test_normalization_is_mechanical_and_resolves_no_entity():
    # P4 D8 and §2.8's own example: "If a document says `U Chicago`, the raw
    # observation remains exactly that wording, while A RESOLVER may normalize it."
    # The resolver is P6's and runs after extraction (§3.2).
    assert normalize_mechanical("U Chicago") == "U Chicago"
    assert normalize_mechanical("  BUSIB   4300 ") == "BUSIB 4300"
    assert normalize_mechanical("Uni­versity") == "University"
    assert normalize_mechanical("Colum-\nbia") == "Columbia"


def test_raw_value_is_never_normalized_in_place():
    # P4 RAW-1 / RAW-2: raw_value is exactly the source substring.
    obs = an_observation(raw_value="U Chicago",
                         normalized_value=normalize_mechanical("U Chicago"))
    assert obs["raw_value"] == "U Chicago"


def test_a_null_normalized_value_is_always_legal():
    # P4 RAW-3: "An extractor that cannot normalize safely leaves it null."
    assert an_observation()["normalized_value"] is None


def test_context_is_cut_by_a_caller_supplied_window_and_says_so_when_it_was():
    # §8.6: never truncate silently. There is no default window: the value is
    # configuration (P4 Deferred, "the context_before/context_after budget").
    text = "Syllabus — BUSIB 4300 — Spring 2026"
    before, after, truncated = context_for(text, 11, 21, window=11)
    assert before == "Syllabus — " and after == " — Spring 2"
    assert truncated is True
    before, after, truncated = context_for(text, 11, 21, window=40)
    assert before == "Syllabus — " and after == " — Spring 2026"
    assert truncated is False
    with pytest.raises(TypeError):
        context_for(text, 11, 21)


def test_text_offsets_are_counted_in_code_points():
    # P4 D4: Unicode scalar values, not bytes and not UTF-16 code units. §2.7
    # requires CJK, so the unit must be language-stable.
    text = "課程 BUSIB 4300"
    before, after, truncated = context_for(text, 3, 13, window=8)
    assert before == "課程 "
    unit = text_unit(text=text)
    assert unit["length"] == 13


def test_the_run_record_carries_every_p4_field_and_a_config_fingerprint():
    row = run(file_id="f1", content_hash="sha256:abc", extractor_name="pdf.text",
              extractor_version="0.1.0", source_type="text_document",
              analysis_tier="native", config={"reader": "fixture"},
              completeness="complete",
              coverage={"units": "pages", "processed": 2, "total": 2},
              observation_count=1, started_at=NOW, finished_at=NOW)
    assert tuple(row) == RUN_FIELDS
    assert row["config_fingerprint"] == fingerprint({"reader": "fixture"})
    assert row["failure_reason"] is None


def test_p5_never_writes_the_llm_analysis_tier():
    # I4: "P5 owns the vocabulary and writes the first three; P8 is the only writer
    # of `llm`." §3.3's boundary, enforced at the one place P5 could cross it.
    assert ANALYSIS_TIERS == ("filesystem", "native", "ocr", "llm")
    assert P5_ANALYSIS_TIERS == ("filesystem", "native", "ocr")
    with pytest.raises(ForbiddenAnalysisTier):
        run(file_id="f1", content_hash="sha256:abc", extractor_name="x",
            extractor_version="0.1.0", source_type="text_document",
            analysis_tier="llm", config={}, completeness="complete",
            coverage={"units": "files", "processed": 1, "total": 1},
            observation_count=0, started_at=NOW, finished_at=NOW)


def test_a_text_unit_is_keyed_by_container_path_and_records_its_own_length():
    # P4 D12/G1. `container_path: ()` is the whole file (§2.4).
    unit = text_unit(text="page one text", container_path=(segment("page", index=1),))
    assert tuple(unit) == TEXT_UNIT_FIELDS == ("container_path", "text", "length",
                                               "truncated")
    assert unit["length"] == len("page one text")
    assert unit["truncated"] is False
    assert text_unit(text="whole file")["container_path"] == ()


def test_canonical_json_is_stable_across_key_order():
    assert canonical_json({"b": 1, "a": 2}) == canonical_json({"a": 2, "b": 1})
    assert fingerprint({"b": 1, "a": 2}) == fingerprint({"a": 2, "b": 1})
    assert fingerprint({}).startswith("sha256:")


def test_an_extraction_result_is_one_run_and_its_whole_batch(sink):
    result = ExtractionResult(
        run=run(file_id="f1", content_hash="sha256:abc", extractor_name="pdf.text",
                extractor_version="0.1.0", source_type="text_document",
                analysis_tier="native", config={}, completeness="complete",
                coverage={"units": "pages", "processed": 1, "total": 1},
                observation_count=1, started_at=NOW, finished_at=NOW),
        observations=(an_observation(),),
        text_units=(text_unit(text="BUSIB 4300",
                              container_path=(segment("page", index=1),
                                              segment("heading", index=2,
                                                      label="Course Information"))),),
    )
    run_id = sink.write(result)
    assert sink.runs[0]["run_id"] == run_id
    assert sink.observations[0]["run_id"] == run_id
    assert sink.text_units[0]["run_id"] == run_id
    sink.conforms()


def test_the_p4_stub_rejects_a_span_with_no_text_unit():
    # P4 conformance rule 10: "rule 10 fails an observation whose span has no unit".
    with pytest.raises(AssertionError):
        validate_observation(an_observation(), text_units=[])


def test_p5_config_fingerprint_is_byte_identical_to_p4s():
    """P4 owns `config_fingerprint` and validates it; P5 must not compute a second one.

    Both sides canonicalised the same JSON and then hashed it differently — P4's
    `sha256_of` length-prefixes the part before hashing, P5's called `hashlib.sha256`
    directly — so the digests were never equal and P4 rejected every run record P5
    emitted. `config_fingerprint` is in §3.4's cache key and rule 8's four-field
    replay key, so the failure is not only conformance: two runs of one process would
    never match, and replay would report divergence that did not happen.
    """
    from evidence_shape.canonical import sha256_of, canonical_json as p4_canonical
    from extractors.shape import fingerprint
    for config in ({}, {"dpi": 200}, {"lang": ["en", "ja"], "dpi": 200}):
        assert fingerprint(config) == sha256_of(p4_canonical(dict(config))), config
