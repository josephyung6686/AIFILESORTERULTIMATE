# tests/p4/test_p4_supersession.py
import pytest

from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import (
    get_observation, observation_row, observations_by_key, record_observation,
    record_run, record_text_unit, supersede_chain, supersede_observation,
    text_unit_at,
)
from evidence_shape.text_units import TextUnit

GARBLED = "Y0ur C0Iumb1a Un1vers1ty"
RECOVERED = "Your Columbia University"


def _ocr_run(run_id, version):
    return ExtractionRun(
        run_id=run_id, file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
        extractor_name="ocr.apple_vision", extractor_version=version,
        source_type="ocr", analysis_tier="ocr", config={"dpi": 200},
        completeness="complete", started_at="2026-08-19T14:00:00+00:00",
        finished_at="2026-08-19T14:03:22+00:00")


def _ocr_observation(run_id, version, raw_value):
    return Observation(
        file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124", extractor_name="ocr.apple_vision",
        extractor_version=version, source_type="ocr", raw_value=raw_value,
        location=Location("ocr", (Segment("page", 4), Segment("region", 2)),
                          text_span=TextSpan(0, len(raw_value))),
        occurrence_count=1, observed_at="2026-08-19T14:03:22+00:00",
        reliability="possible", run_id=run_id, confidence=0.41)


@pytest.fixture()
def two_passes(p4_conn):
    """§8.2's own example: a first OCR pass produces unreadable text and a later
    improved engine recovers a university name."""
    record_run(p4_conn, _ocr_run("r1", "2.4.1"))
    record_text_unit(p4_conn, TextUnit(
        run_id="r1", container_path=(Segment("page", 4), Segment("region", 2)),
        text=GARBLED))
    first = record_observation(p4_conn, _ocr_observation("r1", "2.4.1", GARBLED))

    record_run(p4_conn, _ocr_run("r2", "3.0.0"))
    record_text_unit(p4_conn, TextUnit(
        run_id="r2", container_path=(Segment("page", 4), Segment("region", 2)),
        text=RECOVERED))
    second = record_observation(p4_conn, _ocr_observation("r2", "3.0.0", RECOVERED))
    return first, second


def test_the_old_row_keeps_every_never_overwritten_field(two_passes, p4_conn):
    # Done-means 7: raw_value, location, occurrence_count, observed_at and
    # extractor_version are untouched.
    first, second = two_passes
    before = get_observation(p4_conn, first)
    supersede_observation(p4_conn, old_observation_id=first,
                          new_observation_id=second,
                          reason="a later improved OCR engine recovered the name")
    after = get_observation(p4_conn, first)

    assert after.raw_value == before.raw_value == GARBLED
    assert after.location == before.location
    assert after.occurrence_count == before.occurrence_count
    assert after.observed_at == before.observed_at
    assert after.extractor_version == before.extractor_version == "2.4.1"


def test_the_supersede_pointers_are_set_on_both_rows(two_passes, p4_conn):
    first, second = two_passes
    supersede_observation(p4_conn, old_observation_id=first,
                          new_observation_id=second,
                          reason="a later improved OCR engine recovered the name")
    old_row = observation_row(p4_conn, first)
    new_row = observation_row(p4_conn, second)

    assert old_row["superseded_by"] == second
    assert old_row["supersede_reason"] == \
        "a later improved OCR engine recovered the name"
    assert new_row["supersedes"] == first
    assert new_row["superseded_by"] is None


def test_both_extraction_records_remain_available(two_passes, p4_conn):
    # §8.2's own words: "both extraction records should remain available."
    first, second = two_passes
    supersede_observation(p4_conn, old_observation_id=first,
                          new_observation_id=second, reason="improved engine")
    links = supersede_chain(p4_conn, first)
    assert [row["observation_id"] for row in links] == [first, second]
    assert [row["raw_value"] for row in links] == [GARBLED, RECOVERED]


def test_both_runs_text_units_stay_readable(two_passes, p4_conn):
    # Rule 4: superseding never rewrites or deletes the earlier run's units.
    first, second = two_passes
    supersede_observation(p4_conn, old_observation_id=first,
                          new_observation_id=second, reason="improved engine")
    path = (Segment("page", 4), Segment("region", 2))
    assert text_unit_at(p4_conn, "r1", path).text == GARBLED
    assert text_unit_at(p4_conn, "r2", path).text == RECOVERED


def test_a_reason_is_required(two_passes, p4_conn):
    # §8.2: "retaining the old observation AND THE REASON it was superseded."
    first, second = two_passes
    with pytest.raises(ValueError):
        supersede_observation(p4_conn, old_observation_id=first,
                              new_observation_id=second, reason="")


def test_the_first_reason_is_never_overwritten(two_passes, p4_conn):
    first, second = two_passes
    supersede_observation(p4_conn, old_observation_id=first,
                          new_observation_id=second, reason="improved engine")
    with pytest.raises(ValueError):
        supersede_observation(p4_conn, old_observation_id=first,
                              new_observation_id=second, reason="a different story")
    assert observation_row(p4_conn, first)["supersede_reason"] == "improved engine"


def test_a_record_cannot_supersede_itself(two_passes, p4_conn):
    first, _ = two_passes
    with pytest.raises(ValueError):
        supersede_observation(p4_conn, old_observation_id=first,
                              new_observation_id=first, reason="x")


def test_superseding_does_not_change_the_citation_handles(two_passes, p4_conn):
    # The two readings are different raw values, so they are different observations
    # with different keys -- and §8.7's negative examples still resolve to both.
    first, second = two_passes
    supersede_observation(p4_conn, old_observation_id=first,
                          new_observation_id=second, reason="improved engine")
    old_key = get_observation(p4_conn, first).observation_key
    new_key = get_observation(p4_conn, second).observation_key
    assert old_key != new_key
    assert len(observations_by_key(p4_conn, old_key)) == 1
    assert observations_by_key(p4_conn, old_key)[0].raw_value == GARBLED


def test_no_preferred_column_exists_anywhere(two_passes, p4_conn):
    # M1: §8.2 says "the resolver may mark the newer value as preferred", and §3.2
    # places the resolver after extraction. Preference is P6's `file_facts`.
    columns = {row["name"] for row in p4_conn.execute("PRAGMA table_xinfo(evidence)")}
    assert "preferred" not in columns
