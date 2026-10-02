"""Opt-in scan timing. Off unless a run asks, and a report only then."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from database_agent.db import open_database
from database_agent.identity import hash_file
from scan_profile import (
    active_scan_profile,
    arm_scan_profile,
    describe_reader,
    statement_prefix,
)


def test_nothing_is_armed_until_a_run_asks():
    assert active_scan_profile() is None


def test_a_connection_is_not_wrapped_until_a_run_asks(tmp_path):
    conn = open_database(tmp_path / "agent.sqlite")
    original = conn.execute
    conn.execute("SELECT 1")
    assert conn.execute == original
    assert active_scan_profile() is None
    conn.close()


def test_statement_prefix_groups_the_same_query_and_keeps_commit():
    stamp = (
        "SELECT COUNT(*), IFNULL(MAX(rowid), 0) FROM evidence "
        "WHERE file_id = ? AND content_hash = ?"
    )
    again = (
        "SELECT  COUNT(*),\nIFNULL(MAX(rowid), 0) FROM evidence\n"
        "WHERE file_id = 'abc'"
    )
    assert statement_prefix(stamp) == statement_prefix(again)
    assert statement_prefix(stamp).upper().startswith("SELECT")
    assert "WHERE" not in statement_prefix(stamp).upper()
    assert statement_prefix("COMMIT") == "COMMIT"
    assert statement_prefix("BEGIN IMMEDIATE") == "BEGIN IMMEDIATE"


def test_armed_counts_executes_and_commits_by_phase_and_prefix(tmp_path):
    conn = open_database(tmp_path / "agent.sqlite")
    profile = arm_scan_profile(conn)
    try:
        assert active_scan_profile() is profile
        conn.execute("CREATE TABLE profile_probe (name TEXT)")
        with profile.phase("scan_record"):
            conn.execute("SELECT COUNT(*) FROM files WHERE current_path = ?", ("a",))
            conn.execute("SELECT COUNT(*) FROM files WHERE current_path = ?", ("b",))
            conn.execute("BEGIN")
            conn.execute("INSERT INTO profile_probe (name) VALUES (?)", ("a",))
            conn.execute("COMMIT")
        with profile.phase("recognise_explain"):
            conn.execute("BEGIN")
            conn.execute("SELECT COUNT(*) FROM files WHERE current_path = ?", ("c",))
            conn.execute("COMMIT")
    finally:
        profile.disarm()
    assert active_scan_profile() is None
    # The wrapper is gone. A later statement is not counted.
    conn.execute("SELECT 1")

    scan = profile.sql_phase("scan_record")
    explain = profile.sql_phase("recognise_explain")
    assert scan["commits"] == 1
    assert explain["commits"] == 1
    assert scan["executes"] >= 3
    prefix = statement_prefix(
        "SELECT COUNT(*) FROM files WHERE current_path = ?")
    assert scan["by_prefix"][prefix] == 2
    assert explain["by_prefix"][prefix] == 1
    assert scan["by_prefix"]["COMMIT"] == 1
    conn.close()


def test_hash_and_a_file_are_recorded_only_while_armed(tmp_path):
    path = tmp_path / "note.txt"
    path.write_text("hello")
    first = hash_file(path, materialized=True)
    assert active_scan_profile() is None

    conn = open_database(tmp_path / "agent.sqlite")
    profile = arm_scan_profile(conn)
    try:
        second = hash_file(path, materialized=True)
        profile.note_file(path=str(path), extension=".txt", size=path.stat().st_size)
        profile.add_time("walk_stat", 0.25)
        profile.note_extraction(
            path=str(path), extension=".txt", size=5,
            blocked_s=1.5, work_s=1.0, ocr_s=0.0,
            readers=("pdfium text layer (readers.pdf_pdfium.pdfium_reader)",))
        profile.note_explain(file_id="file-1", seconds=0.4, path=str(path))
    finally:
        profile.disarm()
    assert first == second
    report = profile.report(wall_s=4.0)
    assert report["stages"]["hash"]["seconds"] > 0
    assert report["stages"]["walk_stat"]["seconds"] == pytest.approx(0.25)
    assert report["stages"]["walk_stat"]["share_of_wall"] == pytest.approx(0.25 / 4.0)
    assert report["stages"]["extraction_pool_blocked"]["seconds"] == pytest.approx(1.5)
    assert report["stages"]["extraction_work"]["seconds"] == pytest.approx(1.0)
    assert report["pool"]["parent_blocked_beyond_file_work_seconds"] == pytest.approx(0.5)
    ext = report["by_extension"][".txt"]
    assert ext["files"] == 1
    assert ext["p50"] == ext["p95"] == ext["max"]
    reader = report["by_reader"][
        "pdfium text layer (readers.pdf_pdfium.pdfium_reader)"]
    assert reader["p50"] == pytest.approx(1.0)
    assert report["slowest_files"][0]["extension"] == ".txt"
    assert report["slowest_files"][0]["size"] == 5
    assert report["slowest_files"][0]["path"] == str(path)
    conn.close()


def test_a_crashed_scan_is_marked_partial(tmp_path):
    """The report is written from a finally. A crash must not look finished."""
    conn = open_database(tmp_path / "plan.sqlite")
    profile = arm_scan_profile(conn)
    try:
        profile.mark_partial()
        written = profile.write(tmp_path / "plan.sqlite")
        body = json.loads(written["json"].read_text(encoding="utf-8"))
        assert body["partial"] is True
    finally:
        profile.disarm()
        conn.close()


def test_a_finished_scan_is_not_partial(tmp_path):
    conn = open_database(tmp_path / "finished.sqlite")
    profile = arm_scan_profile(conn)
    try:
        written = profile.write(tmp_path / "finished.sqlite")
        body = json.loads(written["json"].read_text(encoding="utf-8"))
        assert body["partial"] is False
    finally:
        profile.disarm()
        conn.close()


def test_report_files_land_beside_the_database_and_name_the_pdf_reader(tmp_path):
    db = tmp_path / "plan.sqlite"
    conn = open_database(db)
    profile = arm_scan_profile(conn)

    def read_pdf(path: Path):
        return path

    read_pdf.__module__ = "readers.pdf_pdfium"
    read_pdf.__qualname__ = "pdfium_reader.<locals>.read_pdf"
    profile.note_production_readers(read_pdf=read_pdf, ocr_engine=None)
    profile.add_time("p8_p11", 3.0)
    profile.add_time("recognise_explain", 1.0)
    for index in range(30):
        profile.note_file(
            path=str(tmp_path / f"f{index}.pdf"), extension=".pdf", size=100 + index)
        profile.note_extraction(
            path=str(tmp_path / f"f{index}.pdf"), extension=".pdf",
            size=100 + index, blocked_s=0.01 * index, work_s=0.01 * index,
            ocr_s=0.0,
            readers=("pdfium text layer (readers.pdf_pdfium.pdfium_reader)",))
    try:
        written = profile.write(db, wall_s=10.0)
    finally:
        profile.disarm()
    payload = json.loads(written["json"].read_text())
    assert written["json"].parent == db.parent
    assert written["json"].name == "plan.scan-profile.json"
    assert written["csv"].name == "plan.scan-profile.csv"
    assert payload["pdf_reader"]["production"].startswith("pdfium text layer")
    assert "pdfium_reader" in payload["pdf_reader"]["production"]
    assert payload["sqlite_version"] == sqlite3.sqlite_version
    assert len(payload["slowest_files"]) == 25
    assert payload["slowest_files"][0]["size"] == 129
    text = written["csv"].read_text()
    assert "walk_stat" in text or "p8_p11" in text
    assert "COMMIT" in text or "by_prefix" in text or "section" in text
    # The local report is allowed to name paths. Nothing here is committed.
    assert str(tmp_path / "f29.pdf") in written["json"].read_text()
    conn.close()


def test_percentiles_use_each_files_own_time():
    from scan_profile import ScanProfile
    profile = ScanProfile()
    for seconds, name in ((1.0, "a"), (2.0, "b"), (3.0, "c"), (4.0, "d")):
        path = f"/tmp/{name}.txt"
        profile.note_file(path=path, extension=".txt", size=10)
        profile.note_hash(path, seconds)
    summary = profile.by_extension()[".txt"]
    assert summary["files"] == 4
    assert summary["p50"] == pytest.approx(2.0)
    assert summary["max"] == pytest.approx(4.0)
    assert summary["p95"] == pytest.approx(4.0)


def test_describe_reader_names_pdfium_ocr_and_cocoa():
    def read_pdf(path):
        return path

    read_pdf.__module__ = "readers.pdf_pdfium"
    read_pdf.__qualname__ = "pdfium_reader.<locals>.read_pdf"

    def read_ocr(path):
        return path

    read_ocr.__module__ = "readers.ocr_vision"
    read_ocr.__qualname__ = "vision_ocr.<locals>.recognize"

    def read_doc(path):
        return path

    read_doc.__module__ = "readers.doc_cocoa"
    read_doc.__qualname__ = "cocoa_doc_reader.<locals>.read_doc"

    assert "pdfium" in describe_reader(read_pdf)
    assert "text layer" in describe_reader(read_pdf)
    assert "ocr" in describe_reader(read_ocr)
    assert "cocoa" in describe_reader(read_doc)
    assert describe_reader(None) == "none"


def test_a_profiled_scan_records_the_walk_and_the_hash(tmp_path):
    from scan_agent.corpus_source import FilesystemCorpusSource
    from scan_agent.scan import scan
    from scan_agent.schema import create_scan_schema
    from scan_agent.selection import record_selection

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "a.txt").write_text("alpha")
    (corpus / "b.txt").write_text("beta")
    conn = open_database(tmp_path / "agent.sqlite")
    create_scan_schema(conn)
    profile = arm_scan_profile(conn)
    try:
        selection = record_selection(
            conn, sources=[corpus], candidate_roots=[],
            cross_folder_moves=False, selected_by=None)
        scan(conn, selection, source=FilesystemCorpusSource(),
             mime_type_for=lambda path: None, scan_state="included",
             budget_exhausted=lambda: False)
        report = profile.report(wall_s=profile.elapsed())
    finally:
        profile.disarm()
    assert report["stages"]["walk_stat"]["seconds"] > 0
    assert report["stages"]["hash"]["seconds"] > 0
    assert report["stages"]["db_writes"]["seconds"] > 0
    assert profile.sql_phase("scan_record")["executes"] > 0
    assert report["by_extension"][".txt"]["files"] == 2
    conn.close()


def test_annotate_extraction_names_pdfium_and_ocr_separately():
    from types import SimpleNamespace

    from extraction_pool import DISPATCHED, ExtractionOutcome
    from scan_profile import annotate_extraction

    def read_pdf(path):
        return path

    read_pdf.__module__ = "readers.pdf_pdfium"
    read_pdf.__qualname__ = "pdfium_reader.<locals>.read_pdf"

    def read_ocr(path):
        return path

    read_ocr.__module__ = "readers.ocr_vision"
    read_ocr.__qualname__ = "vision_ocr.<locals>.recognize"
    readers = SimpleNamespace(read_pdf=read_pdf, ocr_engine=read_ocr)
    outcome = ExtractionOutcome(
        DISPATCHED,
        SimpleNamespace(
            ocr_seconds=0.25,
            results=(
                SimpleNamespace(run={"analysis_tier": "native",
                                     "extractor_name": "pdf.text"}),
                SimpleNamespace(run={"analysis_tier": "ocr",
                                     "extractor_name": "ocr.vision"}),
            ),
        ),
    )
    annotated = annotate_extraction(outcome, readers, 1.0)
    assert annotated.work_seconds == pytest.approx(1.0)
    assert any("pdfium" in label for label in annotated.readers)
    assert any("ocr" in label for label in annotated.readers)
    untouched = ExtractionOutcome(DISPATCHED, None)
    assert untouched.work_seconds == 0.0
    assert untouched.readers == ()


def test_disarm_restores_execute(tmp_path):
    conn = open_database(tmp_path / "agent.sqlite")
    original = conn.execute
    profile = arm_scan_profile(conn)
    assert conn.execute != original
    profile.disarm()
    assert conn.execute == original
    conn.close()
