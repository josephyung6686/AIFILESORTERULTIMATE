# tests/p6/test_p6_capture_year_slot.py
"""`106` Phase 6 Task 6.1: the EXIF capture time becomes `capture_year`.

`capture_year` is the FIRST level of eight of the library's ten photo situations and
required in seven (`production.folder_levels_for`), and no producer in `src/` has ever
written it. The image reader publishes `DateTimeOriginal` on every camera photograph,
the extractor records it at `metadata:field=DateTimeOriginal`, `facts.fields` declares
the key, and `cli.DIRECT_SLOTS` shipped empty. §3.5 names "an EXIF timestamp" as the
design's own example of a direct fact. The model is no substitute: every EXIF
observation is signalled sensitive and never released to any target.

The slot is the composition root's, exactly as `tests/p6/test_p6_direct.py:121`
declares one -- `facts.direct` spells no tag name and this test spells only the
reader's.
"""
from __future__ import annotations

import json
from pathlib import Path

from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from facts.file_facts import facts_for_file
from facts.states import DIRECT

import cli

CLOCK = "2026-09-18T00:00:00+00:00"


def _photo(conn, tmp_path, name="IMG_4821.heic"):
    path = tmp_path / name
    path.write_bytes(b"\x00photo-bytes")
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=12,
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Photos", mime_type="image/heic",
        detected_format="heic", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _exif(conn, *, run_id, file_id, content_hash, tag, raw):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="image.exif", extractor_version="1.0.0",
        source_type="image", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    record_observation(conn, Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="image.exif",
        extractor_version="1.0.0", source_type="image", raw_value=raw,
        location=Location("metadata", (Segment("field", label=tag),)),
        occurrence_count=1, observed_at=CLOCK, reliability="direct", run_id=run_id))


def _years(conn, file_id, content_hash):
    return [(row["canonical_value"], row["reliability_state"])
            for row in facts_for_file(conn, file_id, content_hash)
            if row["field_key"] == cli.CAPTURE_YEAR_FIELD and row["active"]]


def test_a_camera_photograph_gets_its_capture_year_as_a_direct_fact(p6_conn, tmp_path):
    """SABOTAGE: `DIRECT_SLOTS = DirectSlots(slots=())` -- the stage runs, claims
    nothing, and every photo situation's first level stays empty, silently."""
    file_id, content_hash = _photo(p6_conn, tmp_path)
    _exif(p6_conn, run_id="run-1", file_id=file_id, content_hash=content_hash,
          tag=cli.CAPTURE_TIME_TAG, raw="2024:07:17 14:03:22")
    written = cli._direct_stage(p6_conn, file_id, content_hash)
    assert len(written) == 1
    assert _years(p6_conn, file_id, content_hash) == [("2024", DIRECT)]


def test_a_camera_with_no_clock_writes_no_year(p6_conn, tmp_path):
    """Cameras with an unset clock write `0000:00:00 00:00:00`. SABOTAGE: drop
    `matches` -- `0000` becomes a folder."""
    file_id, content_hash = _photo(p6_conn, tmp_path)
    _exif(p6_conn, run_id="run-1", file_id=file_id, content_hash=content_hash,
          tag=cli.CAPTURE_TIME_TAG, raw="0000:00:00 00:00:00")
    assert cli._direct_stage(p6_conn, file_id, content_hash) == ()
    assert _years(p6_conn, file_id, content_hash) == []


def test_the_files_last_edit_is_not_its_capture_year(p6_conn, tmp_path):
    """`DateTime` is when the file was last written; `DateTimeDigitized` is when a
    scan was made. Neither is when the picture was taken. SABOTAGE: match
    `"DateTime" in locator`.

    ONE TAG PER FILE, deliberately: a single wrong tag is a fixture the `names`
    predicate alone answers, so the sabotage above goes red on the predicate and on
    nothing else (proved red on 18 Sep: the sloppy predicate wrote one fact)."""
    edited, edited_hash = _photo(p6_conn, tmp_path, name="IMG_0001.heic")
    _exif(p6_conn, run_id="run-1", file_id=edited, content_hash=edited_hash,
          tag="DateTime", raw="2026:01:01 09:00:00")
    assert cli._direct_stage(p6_conn, edited, edited_hash) == ()
    scanned, scanned_hash = _photo(p6_conn, tmp_path, name="IMG_0002.heic")
    _exif(p6_conn, run_id="run-2", file_id=scanned, content_hash=scanned_hash,
          tag="DateTimeDigitized", raw="2025:01:01 09:00:00")
    assert cli._direct_stage(p6_conn, scanned, scanned_hash) == ()


def test_the_models_year_is_canonicalised_by_the_same_rule():
    """`normalize_for_model` applies the slot's own `matches` and `canonical` to a
    model's value. A grounded, bare year must survive; a month or a phrase must
    not. SABOTAGE: make `matches` accept only the EXIF form -- a correct model
    answer of `2024` from a scanned document's own text is refused as
    unnormalizable."""
    assert cli.normalize_for_model(cli.CAPTURE_YEAR_FIELD, "2024") == "2024"
    assert cli.normalize_for_model(cli.CAPTURE_YEAR_FIELD, "2024:07:17 14:03:22") == "2024"
    assert cli.normalize_for_model(cli.CAPTURE_YEAR_FIELD, "July 2024") is None
    assert cli.normalize_for_model(cli.CAPTURE_YEAR_FIELD, "0000") is None
