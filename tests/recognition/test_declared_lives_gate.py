"""Declared lives gate the term detector. Undeclared schemas cannot win.

The texts below are synthetic. They are not files from anyone's Downloads.
The shipped library is the rule set, so a term added to a node row can move
a count, and the assertions are about which schema wins, not about a private
list of words.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from cli import HANDLING_POLICY
from database_agent.db import create_schema
from database_agent.files_table import record_file
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import RunWriter
from extractors.runs import coverage
from extractors.schema import create_extraction_schema
from extractors.shape import location, observation, run
from extractors.sink import ExtractionResult
from privacy.classification import ClassificationRecord
from recognition.detector import Abstention, Detector, Recognition
from recognition.rules import load_rules

CLOCK = "2026-09-30T12:00:00+00:00"
MANIFEST = (Path(__file__).resolve().parents[2] / "src" / "recognition"
            / "library" / "recognition.json")

# Professional vocabulary plus real coursework words. Without a profile the
# business catalogue is strictly ahead. With academic declared, academic is
# the only life left in the count and it has more than one term.
COURSEWORK = (
    "Lecture notes on the first law. Agenda. Action items. Assumptions. "
    "Annual plan. Budget holder. This homework is a problem set."
)
# No academic term. The same professional words, and nothing else.
BUSINESS_ONLY = (
    "Annual plan and budget holder and action items and assumptions."
)
RESUME = "Resume and cover letter for the internship."
LECTURE = "Lecture notes and office hours."
TIED = (
    "Lecture notes. Office hours. Resume. Cover letter. Offer letter."
)
PASSPORT = "Passport number. National identity card."

DECLARED = frozenset({
    "academic", "career", "college_applications", "code"})


@pytest.fixture()
def db(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    return conn


def _file(db, tmp_path, filename: str, body: str):
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


def _detector(**kwargs):
    rules = load_rules(MANIFEST.read_text)
    return Detector(rules, handling_for=HANDLING_POLICY, now=lambda: CLOCK,
                    **kwargs)


def _explain(db, tmp_path, filename, body, **kwargs):
    file_id, content_hash = _file(db, tmp_path, filename, body)
    return _detector(**kwargs).explain(db, file_id, content_hash), file_id, content_hash


def test_without_a_profile_a_professional_leader_still_wins(db, tmp_path):
    outcome, _, _ = _explain(db, tmp_path, "week.pdf", COURSEWORK)
    assert isinstance(outcome, Recognition)
    assert outcome.schema_id == "business_operations"


def test_a_declared_coursework_life_keeps_the_file_out_of_business(db, tmp_path):
    outcome, _, _ = _explain(
        db, tmp_path, "week.pdf", COURSEWORK,
        declared_lives=lambda: DECLARED)
    assert isinstance(outcome, Recognition)
    assert outcome.schema_id == "academic"
    # An abstention is what the gist refuses to print as a kind. A recognition
    # of academic is the coursework life, not Business operations.


def test_a_file_with_no_declared_term_abstains_and_cites_the_would_be_winner(
        db, tmp_path):
    outcome, _, _ = _explain(
        db, tmp_path, "memo.pdf", BUSINESS_ONLY,
        declared_lives=lambda: DECLARED)
    assert isinstance(outcome, Abstention)
    assert outcome.reason == "outside_declared_lives"
    assert outcome.schema_id is None
    assert "business_operations" not in (
        outcome.schema_id, *outcome.tied_schema_ids)
    cited = {schema_id for schema_id, _terms in outcome.matched_terms}
    assert "business_operations" in cited


def test_a_declaration_does_not_label_a_file_that_matched_no_academic_term(
        db, tmp_path):
    outcome, _, _ = _explain(
        db, tmp_path, "memo.pdf", BUSINESS_ONLY,
        declared_lives=lambda: frozenset({"academic"}))
    assert not isinstance(outcome, Recognition)


def test_declared_career_and_academic_still_recognise_their_own_files(
        db, tmp_path):
    resume, _, _ = _explain(
        db, tmp_path, "application.pdf", RESUME,
        declared_lives=lambda: DECLARED)
    lecture, _, _ = _explain(
        db, tmp_path, "class.pdf", LECTURE,
        declared_lives=lambda: DECLARED)
    assert isinstance(resume, Recognition) and resume.schema_id == "career"
    assert isinstance(lecture, Recognition) and lecture.schema_id == "academic"


def test_a_tie_between_two_declared_lives_abstains_unless_one_was_settled(
        db, tmp_path):
    tied, _, _ = _explain(
        db, tmp_path, "both.pdf", TIED, declared_lives=lambda: DECLARED)
    assert isinstance(tied, Abstention)
    assert tied.reason == "ambiguous"

    settled, _, _ = _explain(
        db, tmp_path, "both-settled.pdf", TIED,
        declared_lives=lambda: DECLARED,
        settled_by_user=lambda: frozenset({"academic"}))
    assert isinstance(settled, Recognition)
    assert settled.schema_id == "academic"


def test_an_identity_document_stays_held_when_identity_is_not_a_declared_life(
        db, tmp_path):
    file_id, content_hash = _file(db, tmp_path, "Passport.pdf", PASSPORT)
    open_detector = _detector()
    gated = _detector(declared_lives=lambda: DECLARED)
    before = open_detector.explain(db, file_id, content_hash)
    assert isinstance(before, Recognition) and before.schema_id == "identity"
    after = gated.explain(db, file_id, content_hash)
    assert isinstance(after, Abstention)
    assert after.schema_id != "identity"
    record = gated(db, file_id, content_hash)
    assert isinstance(record, ClassificationRecord)
    assert record.protected is True
    assert record.basis == "safety_domain"


def test_an_empty_declaration_leaves_recognition_unchanged(db, tmp_path):
    file_id, content_hash = _file(db, tmp_path, "week.pdf", COURSEWORK)
    plain = _detector().explain(db, file_id, content_hash)
    empty = _detector(declared_lives=lambda: frozenset()).explain(
        db, file_id, content_hash)
    assert isinstance(plain, Recognition) and isinstance(empty, Recognition)
    assert plain.schema_id == empty.schema_id == "business_operations"
