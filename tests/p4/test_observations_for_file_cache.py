"""Repeated reads of one file's evidence reuse the decoded rows.

A new row, a superseded row, or a rewritten observation key is a different read.
"""
from __future__ import annotations

import pytest

from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import MalformedObservation, Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import (
    observations_for_file, record_observation, record_run, supersede_observation,
)

HASH = "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124"


def _run(**overrides):
    payload = dict(
        run_id="r1", file_id="f1", content_hash=HASH,
        extractor_name="pdf.text", extractor_version="3.1.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at="2026-08-19T14:00:00+00:00",
        finished_at="2026-08-19T14:03:22+00:00",
    )
    payload.update(overrides)
    return ExtractionRun(**payload)


def _observation(**overrides):
    payload = dict(
        file_id="f1", content_hash=HASH, extractor_name="pdf.text",
        extractor_version="3.1.0", source_type="text_document",
        raw_value="BUSIB 4300",
        location=Location("heading", (Segment("page", 1),), text_span=TextSpan(11, 21)),
        occurrence_count=3, observed_at="2026-08-19T14:03:22+00:00",
        reliability="possible", run_id="r1", normalized_value="BUSIB 4300",
        context_before="Syllabus — ", context_after=" — Spring 2026",
        context_truncated=False,
    )
    payload.update(overrides)
    return Observation(**payload)


def test_a_second_read_returns_the_same_observations(p4_conn):
    record_run(p4_conn, _run())
    record_observation(p4_conn, _observation())
    first = observations_for_file(p4_conn, "f1")
    second = observations_for_file(p4_conn, "f1")
    assert first == second
    assert first is not second
    assert first[0] is second[0]


def test_a_new_row_is_visible_on_the_next_read(p4_conn):
    record_run(p4_conn, _run())
    record_observation(p4_conn, _observation())
    before = observations_for_file(p4_conn, "f1")
    record_observation(p4_conn, _observation(raw_value="Spring 2026",
                                             normalized_value="Spring 2026"))
    after = observations_for_file(p4_conn, "f1")
    assert len(before) == 1
    assert len(after) == 2
    assert after[0] == before[0]
    assert {row.raw_value for row in after} == {"BUSIB 4300", "Spring 2026"}


def test_another_files_rows_stay_out_of_the_cache(p4_conn):
    record_run(p4_conn, _run())
    record_run(p4_conn, _run(run_id="r2", file_id="f2"))
    record_observation(p4_conn, _observation())
    record_observation(p4_conn, _observation(file_id="f2", run_id="r2",
                                             raw_value="other"))
    assert [row.raw_value for row in observations_for_file(p4_conn, "f1")] == [
        "BUSIB 4300"]
    assert [row.raw_value for row in observations_for_file(p4_conn, "f2")] == [
        "other"]


def test_superseding_a_row_then_inserting_another_is_visible(p4_conn):
    record_run(p4_conn, _run())
    old = record_observation(p4_conn, _observation())
    observations_for_file(p4_conn, "f1")
    new = record_observation(p4_conn, _observation(
        raw_value="BUSIB 4301", normalized_value="BUSIB 4301"))
    supersede_observation(p4_conn, old_observation_id=old,
                          new_observation_id=new, reason="extractor upgrade")
    found = observations_for_file(p4_conn, "f1")
    assert {row.raw_value for row in found} == {"BUSIB 4300", "BUSIB 4301"}


def test_a_rewritten_observation_key_is_not_served_from_the_previous_read(p4_conn):
    # The reader refuses a key that is not the hash of the row. A cache that
    # ignored the key would hand back the previous observation and hide that.
    record_run(p4_conn, _run())
    observation_id = record_observation(p4_conn, _observation())
    observations_for_file(p4_conn, "f1")
    p4_conn.execute(
        "UPDATE evidence SET observation_key = ? WHERE observation_id = ?",
        ("sha256:" + "cd" * 32, observation_id))
    with pytest.raises(MalformedObservation):
        observations_for_file(p4_conn, "f1")
