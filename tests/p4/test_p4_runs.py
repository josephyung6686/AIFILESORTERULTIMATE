# tests/p4/test_p4_runs.py
import pytest

from evidence_shape.canonical import canonical_json
from evidence_shape.runs import (
    Coverage, ExtractionRun, MalformedRun, RUN_FIELDS, config_fingerprint,
    run_from_mapping,
)
from evidence_shape.vocabulary import NotInVocabulary

#: The SPEC's own worked run: an OCR pass that stopped at a ceiling.
OCR_RUN = dict(
    run_id="r1", file_id="f1", content_hash="sha256:abc",
    extractor_name="ocr.apple_vision", extractor_version="2.4.1", source_type="ocr",
    analysis_tier="ocr",
    config={"dpi": 200, "languages": ["en", "zh-Hans"], "recognition": "accurate"},
    completeness="capped",
    coverage=Coverage(units="pages", processed=40, total=312),
    observation_count=118, started_at="2026-08-19T14:00:00+00:00",
    finished_at="2026-08-19T14:03:22+00:00",
)


def test_the_record_carries_the_specs_fifteen_fields_in_order():
    assert RUN_FIELDS == (
        "run_id", "file_id", "content_hash", "extractor_name", "extractor_version",
        "source_type", "analysis_tier", "config", "config_fingerprint",
        "completeness", "coverage", "observation_count", "started_at", "finished_at",
        "failure_reason",
    )


def test_runs_carry_no_supersede_columns():
    # A later extractor produces a NEW run; the earlier run and its text units stay
    # readable (§8.2). Supersession is on the observation.
    for column in ("supersedes", "superseded_by", "supersede_reason", "preferred"):
        assert column not in RUN_FIELDS


def test_the_ocr_run_builds_and_fingerprints_its_configuration():
    run = ExtractionRun(**OCR_RUN)
    assert run.completeness == "capped"
    assert run.coverage.processed == 40
    assert run.config_fingerprint.startswith("sha256:")
    assert run.config_fingerprint == config_fingerprint(OCR_RUN["config"])


def test_the_fingerprint_depends_on_the_configuration_and_not_on_key_order():
    # §3.4's cache key and §8.5's diff must be able to tell two configurations apart,
    # and must not report a change when nothing changed.
    reordered = {"recognition": "accurate", "languages": ["en", "zh-Hans"], "dpi": 200}
    assert config_fingerprint(reordered) == config_fingerprint(OCR_RUN["config"])
    changed = {**OCR_RUN["config"], "dpi": 300}
    assert config_fingerprint(changed) != config_fingerprint(OCR_RUN["config"])
    dropped = {"dpi": 200, "recognition": "accurate"}
    assert config_fingerprint(dropped) != config_fingerprint(OCR_RUN["config"])


def test_an_empty_configuration_still_fingerprints():
    assert config_fingerprint({}).startswith("sha256:")
    assert ExtractionRun(**{**OCR_RUN, "config": {}}).config_fingerprint == \
        config_fingerprint({})


def test_all_nine_completeness_values_are_constructible():
    # B1 settled eight; C4 added the ninth, `dataless`, on 2026-08-20 for exactly the
    # iCloud case this test used to say P4 must not name.
    for value in ("complete", "capped", "partial", "metadata_only", "deferred",
                  "unsupported", "unreadable", "failed"):
        payload = {**OCR_RUN, "completeness": value, "observation_count": 0}
        if value in ("unreadable", "failed"):
            payload["failure_reason"] = "password-protected"
        assert ExtractionRun(**payload).completeness == value


def test_2_4s_distinction_is_expressible_on_this_record_and_nowhere_else():
    # "an empty extraction result is different from an extractor that does not yet
    # exist." Both produce zero observations; only the run record separates them.
    empty = ExtractionRun(**{**OCR_RUN, "completeness": "complete",
                             "observation_count": 0, "coverage": None})
    missing = ExtractionRun(**{**OCR_RUN, "completeness": "unsupported",
                               "observation_count": 0, "coverage": None})
    policy = ExtractionRun(**{**OCR_RUN, "completeness": "metadata_only",
                              "observation_count": 0, "coverage": None})
    assert len({empty.completeness, missing.completeness, policy.completeness}) == 3


def test_completeness_source_type_and_analysis_tier_are_closed():
    with pytest.raises(NotInVocabulary):
        ExtractionRun(**{**OCR_RUN, "completeness": "extracted_empty"})
    with pytest.raises(NotInVocabulary):
        ExtractionRun(**{**OCR_RUN, "source_type": "pdf"})
    with pytest.raises(NotInVocabulary):
        ExtractionRun(**{**OCR_RUN, "analysis_tier": "vision"})


def test_i4s_four_tiers_are_all_accepted_including_the_one_only_p8_writes():
    # I4: "P8 is the only writer of `llm` runs -- P4 accepts the value; P5 never
    # emits it." P4 does not police who calls it; it polices the vocabulary.
    for tier in ("filesystem", "native", "ocr", "llm"):
        assert ExtractionRun(**{**OCR_RUN, "analysis_tier": tier}).analysis_tier == tier


def test_coverage_units_are_caller_supplied_because_8_6_names_no_vocabulary():
    for units in ("pages", "regions", "bytes", "entries"):
        assert Coverage(units=units, processed=1, total=2).units == units


def test_coverage_counts_are_non_negative_and_processed_never_exceeds_total():
    assert Coverage("pages", 0, 0).processed == 0
    with pytest.raises(MalformedRun):
        Coverage("pages", -1, 10)
    with pytest.raises(MalformedRun):
        Coverage("pages", 11, 10)


def test_coverage_is_optional_because_no_conformance_rule_requires_it():
    # §8.6 wants it on a capped run and the twelve rules do not make it a rule. P4
    # stores what it is handed rather than repairing a shortfall out of sight.
    assert ExtractionRun(**{**OCR_RUN, "coverage": None}).coverage is None


def test_a_failure_reason_belongs_to_unreadable_and_failed_and_to_nothing_else():
    assert ExtractionRun(**{**OCR_RUN, "completeness": "failed",
                            "failure_reason": "extractor raised"}).failure_reason
    assert ExtractionRun(**{**OCR_RUN, "completeness": "unreadable",
                            "failure_reason": "password-protected"}).failure_reason
    for wrong in ("complete", "capped", "partial", "metadata_only", "deferred",
                  "unsupported"):
        with pytest.raises(MalformedRun):
            ExtractionRun(**{**OCR_RUN, "completeness": wrong,
                             "failure_reason": "something went wrong"})


def test_observation_count_is_never_negative():
    with pytest.raises(MalformedRun):
        ExtractionRun(**{**OCR_RUN, "observation_count": -1})


def test_the_mapping_form_round_trips():
    run = ExtractionRun(**OCR_RUN)
    mapping = run.to_mapping()
    assert list(mapping) == list(RUN_FIELDS)
    assert mapping["config"] == OCR_RUN["config"]
    assert mapping["coverage"] == {"units": "pages", "processed": 40, "total": 312}
    assert run_from_mapping(mapping) == run


def test_the_mapping_form_rejects_a_field_the_record_does_not_publish():
    mapping = ExtractionRun(**OCR_RUN).to_mapping()
    for forbidden in ("plan_version_id", "handling_class", "domain", "node_id"):
        with pytest.raises(MalformedRun):
            run_from_mapping({**mapping, forbidden: "x"})


def test_a_stored_fingerprint_that_does_not_match_its_config_is_rejected():
    mapping = ExtractionRun(**OCR_RUN).to_mapping()
    with pytest.raises(MalformedRun):
        run_from_mapping({**mapping, "config_fingerprint": "sha256:0"})


def test_the_config_is_stored_as_handed_and_p4_defines_no_schema_for_it():
    # §2.7 names "languages, configuration" and no schema for either.
    exotic = {"engine": {"model": "x", "beams": 4}, "languages": [], "strict": True}
    run = ExtractionRun(**{**OCR_RUN, "config": exotic})
    assert run.config == exotic
    assert canonical_json(run.to_mapping()["config"]) == canonical_json(exotic)


def test_a_run_is_frozen():
    run = ExtractionRun(**OCR_RUN)
    with pytest.raises(Exception):
        run.completeness = "complete"
