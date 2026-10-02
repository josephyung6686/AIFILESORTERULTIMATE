"""The terminal questionnaire writes a profile the scan gate accepts."""
from __future__ import annotations

import io
import json
from pathlib import Path

from database_agent.db import open_database
from onboarding.answers import model_context
from onboarding.gate import REFUSAL, allow_scan
from questions.store import profile_wording

import cli

NAME = "Ada Localname"
WORDING = "keep the lab notes together"
SCHOOL = "Example School"

LINES = [
    NAME,
    "academic, career",
    "business_operations",
    "academic.coursework",
    "",
    SCHOOL,
    "CHEM 101",
    "Chemistry",
    "2026 Fall",
    "",
    "Example Lab",
    "",
    WORDING,
    "",
    "yes",
]


def _run(tmp_path, monkeypatch, lines):
    monkeypatch.delenv("FILESORTER_ONBOARDING_OPTIONAL", raising=False)
    folder = tmp_path / "inbox"
    folder.mkdir()
    (folder / "hours.txt").write_text("office hours Tuesday\n")
    database = tmp_path / "plan.sqlite"
    written = tmp_path / "answers.json"
    out = io.StringIO()
    monkeypatch.setattr(
        "onboarding.ask.default_ask", lambda _prompt: next(lines))
    code = cli.main([
        "onboard", "--folder", str(folder), "--database", str(database),
        "--write", str(written), "--user", "t",
    ], out=out)
    return code, out.getvalue(), folder, database, written


def test_onboard_writes_a_record_the_scan_accepts(tmp_path, monkeypatch):
    code, said, folder, database, written = _run(tmp_path, monkeypatch, iter(LINES))
    assert code == 0, said
    assert NAME not in said
    assert WORDING not in said
    assert "filesorter providers" in said
    assert "Profile stored" in said
    assert "--understand" not in said
    assert "do you want" not in said.lower()
    assert "use ai" not in said.lower()
    consent = open_database(database, scan_roots=[folder.resolve()])
    try:
        cloud = consent.execute(
            "SELECT decision FROM cloud_consent").fetchone()
        understood = consent.execute(
            "SELECT statement FROM understanding_consent").fetchone()
    finally:
        consent.close()
    assert cloud is not None and cloud[0] == "enabled"
    assert understood is not None and understood[0]
    data = json.loads(written.read_text(encoding="utf-8"))
    assert data["confirmed"] is True
    assert data["person_name"] == NAME
    note = model_context(data)
    assert NAME not in note
    assert WORDING not in note
    assert SCHOOL in note
    assert "CHEM 101" in note
    conn = open_database(database, scan_roots=[folder.resolve()])
    cli._bootstrap(conn)
    assert allow_scan(
        conn, corpus_root=str(folder.resolve()), answers=None,
        user_id="t", recorded_at="2026-10-01T00:00:00+00:00") is None
    stored = " ".join(profile_wording(conn))
    assert WORDING in stored
    assert NAME not in stored
    conn.close()
    scan = io.StringIO()
    scan_code = cli.main(
        [str(folder), "--database", str(database), "--user", "t"], out=scan)
    scanned = scan.getvalue()
    assert REFUSAL not in scanned
    assert "Nothing was scanned" not in scanned
    assert "Plan database:" in scanned
    assert scan_code in (0, 1)


def test_skip_is_refused_unless_onboarding_is_optional(tmp_path, monkeypatch):
    code, said, folder, database, written = _run(
        tmp_path, monkeypatch, iter(["skip"]))
    assert code == 2
    assert "refused" in said
    assert not written.exists()
    conn = open_database(database, scan_roots=[folder.resolve()])
    try:
        cli._bootstrap(conn)
        assert allow_scan(
            conn, corpus_root=str(folder.resolve()), answers=None,
            user_id="t", recorded_at="2026-10-01T00:00:00+00:00") == REFUSAL
    finally:
        conn.close()

    monkeypatch.setenv("FILESORTER_ONBOARDING_OPTIONAL", "1")
    out = io.StringIO()
    monkeypatch.setattr("onboarding.ask.default_ask", lambda _prompt: "skip")
    code = cli.main([
        "onboard", "--folder", str(folder), "--database", str(database),
        "--user", "t",
    ], out=out)
    assert code == 0, out.getvalue()
    assert "skipped" in out.getvalue()
    assert NAME not in out.getvalue()


def test_a_pipe_does_not_hang(tmp_path, monkeypatch):
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    folder = tmp_path / "inbox"
    folder.mkdir()
    out = io.StringIO()
    from onboarding.ask import main as onboard_main
    code = onboard_main(
        ["--folder", str(folder), "--database", str(tmp_path / "plan.sqlite")],
        out=out)
    assert code == 2
    assert "--answers" in out.getvalue()
