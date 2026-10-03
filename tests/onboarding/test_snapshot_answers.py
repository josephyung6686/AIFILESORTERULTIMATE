"""A finished onboarding snapshot is the answers file a scan already reads.

The snapshot is the setup screen's proposed model. It is not an engine API.
Unfinished answers, or folders whose access was never granted, do not start a scan
and do not leave an answers file behind.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import cli
from database_agent.db import open_database
from onboarding.answers import load_answers, model_context
from onboarding.gate import allow_scan
from onboarding.snapshot import ScanRefused, prepare_engine_scan

SECRET = "snapshot-name-stays-on-this-mac"


def _finished() -> dict:
    return {
        "schemaVersion": 1,
        "finished": True,
        "profile": "student",
        "personName": SECRET,
        "school": "Example School",
        "folderAccess": {"state": "granted", "folders": ["Documents"]},
        "categories": [{"id": "c1", "name": "Courses"}],
        "refusedCategories": [
            {"id": "c2", "name": "Projects"},
            {"id": "c3", "name": "finance"},
        ],
        "context": {
            "courses": "Thermodynamics",
            "companies": "Example Lab",
            "projects": "Solar car",
        },
        "leaveAlone": ["Taxes"],
        "unmatched": "unplaced",
        "sensitiveMaterial": "held",
        "fileOperations": "read-only",
    }


def test_a_finished_snapshot_writes_the_engine_answers_file(tmp_path: Path):
    folder = (tmp_path / "inbox").resolve()
    folder.mkdir()
    path = tmp_path / "answers.json"
    prepare_engine_scan(_finished(), path)

    loaded = load_answers(path)
    assert loaded["confirmed"] is True
    assert loaded["lives"] == ["academic"]
    assert loaded["person_name"] == SECRET
    assert loaded["school"] == "Example School"
    assert loaded["courses"] == [
        {"code": "", "name": "Thermodynamics", "term": ""}
    ]
    assert loaded["companies"] == []
    assert loaded["projects"] == []
    assert loaded["leave_alone"] == ["Taxes"]
    assert "finance" not in loaded["lives"]
    assert "identity" not in loaded["lives"]
    assert "medical" not in loaded["lives"]
    assert "legal" not in loaded["lives"]
    for held in ("medical", "identity", "legal", "finance"):
        assert held in loaded["private_areas"]
        assert held in loaded["not_lives"]
    assert "academic" not in loaded["not_lives"]
    assert SECRET not in model_context(loaded)
    assert "Example School" in model_context(loaded)
    assert "Thermodynamics" in model_context(loaded)

    conn = open_database(tmp_path / "plan.sqlite", scan_roots=[folder])
    cli._bootstrap(conn)
    try:
        refusal = allow_scan(
            conn, corpus_root=str(folder), answers=path, user_id="t",
            recorded_at="2026-10-03T00:00:00+00:00")
    finally:
        conn.close()
    assert refusal is None

    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["confirmed"] is True
    assert "found" not in raw
    assert "fileCount" not in raw


def test_unfinished_or_missing_access_cannot_start_a_scan(tmp_path: Path):
    path = tmp_path / "answers.json"
    path.write_text('{"confirmed": false}\n', encoding="utf-8")
    unfinished = _finished()
    unfinished["finished"] = False
    with pytest.raises(ScanRefused, match="Finish onboarding"):
        prepare_engine_scan(unfinished, path)
    assert json.loads(path.read_text(encoding="utf-8"))["confirmed"] is False

    missing = _finished()
    missing["folderAccess"] = {"state": "not-requested", "folders": ["Documents"]}
    with pytest.raises(ScanRefused, match="Allow folder access"):
        prepare_engine_scan(missing, path)
    assert json.loads(path.read_text(encoding="utf-8"))["confirmed"] is False

    denied = _finished()
    denied["folderAccess"] = {"state": "denied", "folders": ["Documents"]}
    with pytest.raises(ScanRefused, match="denied"):
        prepare_engine_scan(denied, path)
    assert not (tmp_path / "answers.json.tmp").exists()
