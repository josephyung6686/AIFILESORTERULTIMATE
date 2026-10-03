"""A repeated explain is the same frozen answer until the inputs change.

The texts are synthetic. They are not files from anyone's Downloads.
"""
from __future__ import annotations

from pathlib import Path

from cli import HANDLING_POLICY
from database_agent.db import create_schema
from database_agent.files_table import record_file
from evidence_shape.observation import observation_from_mapping
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import RunWriter, record_observation, supersede_observation
from extractors.runs import coverage
from extractors.schema import create_extraction_schema
from extractors.shape import location, observation, run
from extractors.sink import ExtractionResult
from recognition.detector import Abstention, Detector, Recognition
from recognition.rules import load_rules

CLOCK = "2026-09-30T12:00:00+00:00"
MANIFEST = (Path(__file__).resolve().parents[2] / "src" / "recognition"
            / "library" / "recognition.json")

COURSEWORK = (
    "Lecture notes on the first law. Agenda. Action items. Assumptions. "
    "Annual plan. Budget holder. This homework is a problem set."
)


def _db(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    return conn


def _file(db, tmp_path, filename, body):
    path = tmp_path / filename
    path.write_bytes(filename.encode())
    file_id = record_file(
        db, path, filename=filename, normalized_filename=filename.casefold(),
        extension=".pdf", observed_size=path.stat().st_size,
        observed_timestamps="{}", parent_folder_context=str(tmp_path),
        mime_type=None, detected_format=None, scan_state="scanned",
        materialized=True)
    content_hash = db.execute(
        "SELECT content_hash FROM files WHERE file_id = ?", (file_id,)
    ).fetchone()["content_hash"]
    observations = (
        observation(
            file_id=file_id, content_hash=content_hash,
            extractor_name="filesystem.record", extractor_version="0.1.0",
            source_type="filesystem", raw_value=filename,
            location=location(zone="filename"),
            observed_at=CLOCK, reliability="possible"),
        observation(
            file_id=file_id, content_hash=content_hash,
            extractor_name="pdf.text", extractor_version="0.1.0",
            source_type="text_document", raw_value=body,
            location=location(zone="body"),
            observed_at=CLOCK, reliability="possible"),
    )
    RunWriter(db, author="P5").write(ExtractionResult(
        run=run(file_id=file_id, content_hash=content_hash,
                extractor_name="filesystem.record", extractor_version="0.1.0",
                source_type="filesystem", analysis_tier="filesystem", config={},
                completeness="complete", coverage=coverage("files", 1, 1),
                observation_count=len(observations), started_at=CLOCK,
                finished_at=CLOCK),
        observations=observations))
    return file_id, content_hash


def _add_body(db, file_id, content_hash, raw_value):
    run_id = db.execute(
        "SELECT run_id FROM extraction_runs WHERE file_id = ?", (file_id,)
    ).fetchone()["run_id"]
    row = observation(
        file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="0.1.0",
        source_type="text_document", raw_value=raw_value,
        location=location(zone="body"),
        observed_at=CLOCK, reliability="possible")
    return record_observation(
        db, observation_from_mapping({**row, "run_id": run_id}))


def _detector(**kwargs):
    rules = load_rules(MANIFEST.read_text)
    return Detector(rules, handling_for=HANDLING_POLICY, now=lambda: CLOCK,
                    **kwargs)


def test_a_second_explain_is_the_same_answer(conn, tmp_path):
    db = _db(conn)
    file_id, content_hash = _file(db, tmp_path, "week.pdf", COURSEWORK)
    detector = _detector()
    first = detector.explain(db, file_id, content_hash)
    second = detector.explain(db, file_id, content_hash)
    assert isinstance(first, Recognition)
    assert second is first


def test_declaring_a_life_after_the_first_explain_changes_the_answer(conn, tmp_path):
    db = _db(conn)
    file_id, content_hash = _file(db, tmp_path, "week.pdf", COURSEWORK)
    lives: set[str] = set()
    detector = _detector(declared_lives=lambda: lives)
    first = detector.explain(db, file_id, content_hash)
    assert isinstance(first, Recognition)
    assert first.schema_id == "business_operations"
    lives.update({"academic"})
    second = detector.explain(db, file_id, content_hash)
    assert second is not first
    assert isinstance(second, Recognition)
    assert second.schema_id == "academic"


def test_a_new_observation_is_not_answered_from_the_previous_explain(conn, tmp_path):
    db = _db(conn)
    file_id, content_hash = _file(db, tmp_path, "week.pdf", "Syllabus")
    detector = _detector()
    first = detector.explain(db, file_id, content_hash)
    _add_body(db, file_id, content_hash,
              "Passport number and national identity card.")
    second = detector.explain(db, file_id, content_hash)
    assert second is not first
    assert isinstance(second, Recognition)
    assert second.schema_id == "identity"


def test_superseding_the_body_drops_the_cached_reading(conn, tmp_path):
    db = _db(conn)
    file_id, content_hash = _file(db, tmp_path, "week.pdf", COURSEWORK)
    detector = _detector()
    first = detector.explain(db, file_id, content_hash)
    assert isinstance(first, Recognition)
    body_id = db.execute(
        "SELECT observation_id FROM evidence WHERE file_id = ? AND raw_value = ?",
        (file_id, COURSEWORK)).fetchone()["observation_id"]
    replacement = _add_body(db, file_id, content_hash, "zzzz")
    supersede_observation(db, old_observation_id=body_id,
                          new_observation_id=replacement,
                          reason="the body was replaced")
    second = detector.explain(db, file_id, content_hash)
    assert second is not first
    assert not isinstance(second, Recognition)


def test_moving_the_path_under_an_app_bundle_is_not_the_cached_reading(
        conn, tmp_path):
    db = _db(conn)
    file_id, content_hash = _file(db, tmp_path, "week.pdf", COURSEWORK)
    detector = _detector()
    first = detector.explain(db, file_id, content_hash)
    assert isinstance(first, Recognition)
    hidden = tmp_path / "Secret.app" / "week.pdf"
    db.execute("UPDATE files SET current_path = ? WHERE file_id = ?",
               (str(hidden), file_id))
    second = detector.explain(db, file_id, content_hash)
    assert isinstance(second, Abstention)
    assert second.reason == "protected_container"
    assert second is not first


def test_a_changed_corroborating_answer_is_not_the_cached_reading(conn, tmp_path):
    db = _db(conn)
    file_id, content_hash = _file(db, tmp_path, "plain.pdf", "Syllabus today")
    keys: list[str] = []

    def corroborating(_conn, _file_id, _content_hash):
        return tuple(keys)

    detector = _detector(corroborating_observations=corroborating)
    first = detector.explain(db, file_id, content_hash)
    assert isinstance(first, Abstention)
    keys.append("sha256:" + "ab" * 32)
    second = detector.explain(db, file_id, content_hash)
    assert second is not first
    assert isinstance(second, Recognition)
    assert second.schema_id == "academic"


def test_two_detectors_on_one_connection_keep_their_own_answers(conn, tmp_path):
    db = _db(conn)
    file_id, content_hash = _file(db, tmp_path, "week.pdf", COURSEWORK)
    open_detector = _detector()
    gated = _detector(declared_lives=lambda: frozenset({"academic"}))
    before = open_detector.explain(db, file_id, content_hash)
    after = gated.explain(db, file_id, content_hash)
    assert isinstance(before, Recognition)
    assert before.schema_id == "business_operations"
    assert isinstance(after, Recognition)
    assert after.schema_id == "academic"
    assert after is not before
