# tests/p4/test_p4_determinism.py
"""Done-means 8, and conformance rule 8's compared observation set."""
import pytest

from evidence_shape.determinism import (
    COMPARED_FIELDS, EXCLUDED_FROM_COMPARISON, NotDeterministic, REPLAY_KEY_FIELDS,
    assert_identical_observation_sets, compared_form, observation_set_digest,
    replay_key,
)
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import OBSERVATION_FIELDS, Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import observations_for_run, record_observation, record_run

CONFIG = {"languages": ["en", "zh-Hans"], "recognition": "accurate"}


def _run(run_id, *, version="3.1.0", config=CONFIG, name="pdf.text"):
    return ExtractionRun(
        run_id=run_id, file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124", extractor_name=name,
        extractor_version=version, source_type="text_document",
        analysis_tier="native", config=config, completeness="complete",
        started_at="2026-08-19T14:00:00+00:00")


def _observation(run_id, *, version="3.1.0", name="pdf.text",
                 raw_value="BUSIB 4300", heading=2, observed_at="2026-08-19T14:03:22+00:00"):
    return Observation(
        file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124", extractor_name=name,
        extractor_version=version, source_type="text_document", raw_value=raw_value,
        location=Location("heading", (Segment("page", 1), Segment("heading", heading))),
        occurrence_count=3, observed_at=observed_at, reliability="possible",
        run_id=run_id, normalized_value=raw_value, context_before="Syllabus — ",
        context_after=" — Spring 2026", context_truncated=False)


def test_the_compared_set_is_every_emitted_field_but_three():
    # `file_id` joined the exclusions when OQ2 closed: the content hash owns the
    # observation, so two copies of one file must compare equal.
    assert EXCLUDED_FROM_COMPARISON == ("run_id", "observed_at", "file_id")
    assert COMPARED_FIELDS == tuple(
        name for name in OBSERVATION_FIELDS if name not in EXCLUDED_FROM_COMPARISON)


def test_two_runs_of_the_same_process_produce_one_digest(p4_conn):
    # Done-means 8, through the store, which is where a real extractor would land.
    first, second = _run("r1"), _run("r2")
    record_run(p4_conn, first)
    record_run(p4_conn, second)
    record_observation(p4_conn, _observation("r1"))
    record_observation(p4_conn, _observation("r2", observed_at="2026-08-20T09:15:00+00:00"))

    assert (observation_set_digest(observations_for_run(p4_conn, "r1"))
            == observation_set_digest(observations_for_run(p4_conn, "r2")))
    assert_identical_observation_sets(
        first, observations_for_run(p4_conn, "r1"),
        second, observations_for_run(p4_conn, "r2"))


def test_the_run_id_and_the_observation_time_are_the_two_fields_outside_it():
    # Rule 8's premise is TWO RUNS. A comparison that carried either of these would
    # report every row as changed on every re-run.
    base = _observation("r1")
    assert (observation_set_digest([base])
            == observation_set_digest([_observation("r9", observed_at="2027-01-01T00:00:00+00:00")]))


def test_a_different_reading_changes_the_digest():
    assert (observation_set_digest([_observation("r1")])
            != observation_set_digest([_observation("r1", raw_value="BUSIB 4301")]))


def test_a_different_location_changes_the_digest():
    assert (observation_set_digest([_observation("r1")])
            != observation_set_digest([_observation("r1", heading=3)]))


def test_the_digest_does_not_depend_on_emission_order():
    one, two = _observation("r1"), _observation("r1", heading=3)
    assert observation_set_digest([one, two]) == observation_set_digest([two, one])


def test_two_identical_readings_are_not_collapsed():
    # D10's collapse key is (run_id, raw_value, zone) and Task 6 enforces no
    # uniqueness on it. A digest that collapsed them would disagree with the table.
    one = _observation("r1")
    assert observation_set_digest([one]) != observation_set_digest([one, one])


def test_a_missing_observation_is_reported_with_the_row_that_went_missing():
    first, second = _run("r1"), _run("r2")
    with pytest.raises(NotDeterministic) as raised:
        assert_identical_observation_sets(
            first, [_observation("r1"), _observation("r1", heading=3)],
            second, [_observation("r2")])
    assert "heading=3" in str(raised.value)


def test_two_configurations_are_not_one_replay_key():
    with pytest.raises(NotDeterministic) as raised:
        assert_identical_observation_sets(
            _run("r1"), [], _run("r2", config={"recognition": "fast"}), [])
    assert "replay key" in str(raised.value)


def test_two_extractor_versions_are_not_one_replay_key_but_share_one_citation_handle():
    # MINOR 8: `observation_key` excludes `extractor_version` so §8.5's cross-version
    # diff has something to diff against. Rule 8 asks the narrower question.
    old = _observation("r1", version="3.1.0")
    new = _observation("r2", version="4.0.0")
    assert old.observation_key == new.observation_key
    with pytest.raises(NotDeterministic):
        assert_identical_observation_sets(
            _run("r1", version="3.1.0"), [old], _run("r2", version="4.0.0"), [new])


def test_the_replay_key_carries_the_extractor_name_rule_8_omits():
    # SPEC vs design, reported not hidden: rule 8 lists three fields; §3.4 asks for
    # "the content hash and the exact process that produced it" and Task 9's cache
    # index carries four. Two different extractors at one version can never produce
    # one set, because `observation_key` includes `extractor_name`.
    assert REPLAY_KEY_FIELDS == ("content_hash", "extractor_name", "extractor_version",
                                 "config_fingerprint")
    assert (replay_key(_run("r1", name="pdf.text"))
            != replay_key(_run("r2", name="ocr.apple_vision")))


def test_the_compared_form_accepts_a_stored_row_and_a_record_alike():
    observation = _observation("r1")
    assert compared_form(observation) == compared_form(observation.to_mapping())
