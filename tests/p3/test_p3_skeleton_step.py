# tests/p3/test_p3_skeleton_step.py
"""The walking skeleton's P3 step (02-segmentation-map.md):
scan a fixture directory; assert the exclusion rules skip node_modules; P3 authors
the discovery and stat-observation events P1 stores.

This test stays in the repository as the integration test every later part must keep
green. It is deterministic: no model, no cloud, no embeddings, no network.
"""
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.identity import hash_file

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.exclusion import RULE_LITERAL_DIRECTORY_NAME
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection
from scan_agent.summary import scan_run_summary

NEVER = lambda: False


def fixture_mime(path: Path) -> str | None:
    return "application/pdf" if path.suffix == ".pdf" else None


def test_skeleton_p3_step(conn, tmp_path: Path):
    create_schema(conn)
    create_scan_schema(conn)

    # A fixture directory: one PDF whose title carries a course code (the skeleton's
    # input file), and one node_modules the exclusion rules must skip.
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    document = corpus / "syllabus-fixture.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    (corpus / "node_modules").mkdir()
    (corpus / "node_modules" / "must-not-be-indexed.pdf").write_bytes(b"%PDF x")

    selection = record_selection(conn, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by="skeleton-user")
    scan_run_id = scan(conn, selection, source=FilesystemCorpusSource(),
                       mime_type_for=fixture_mime, scan_state="fixture-scan-state",
                       budget_exhausted=NEVER)

    # The exclusion rules skip node_modules, and nothing inside it was indexed.
    rows = conn.execute("SELECT * FROM files").fetchall()
    assert [r["current_path"] for r in rows] == [str(document)]
    verdict = conn.execute(
        "SELECT * FROM exclusion_verdicts WHERE scan_run_id = ?", (scan_run_id,)
    ).fetchone()
    assert verdict["path"] == str(corpus / "node_modules")
    assert verdict["rule"] == RULE_LITERAL_DIRECTORY_NAME
    assert verdict["rule_subject"] == "node_modules"

    # The record P1 holds is the one P3 handed over.
    assert rows[0]["content_hash"] == hash_file(document, materialized=True)
    assert rows[0]["mime_type"] == "application/pdf"
    assert rows[0]["directory_position"] == str(corpus)

    # P3 authors the discovery and stat-observation events P1 stores (M8).
    for event_type in ("discovery", "stat observation", "hashing"):
        row = conn.execute(
            "SELECT * FROM events WHERE event_type = ?", (event_type,)
        ).fetchone()
        assert row is not None, event_type
        assert row["subsystem"] == "P3", event_type
        assert row["component_version"]

    # Nothing in the scan half of the skeleton is authored by P1.
    authors = conn.execute("SELECT DISTINCT subsystem FROM events").fetchall()
    assert [r["subsystem"] for r in authors] == ["P3"]

    # And the run is legible (§8.6).
    summary = scan_run_summary(conn, scan_run_id)
    assert summary["files_indexed"] == 1
    assert summary["paths_excluded_by_rule"] == {RULE_LITERAL_DIRECTORY_NAME: 1}
    assert summary["files_deferred"] == 0
