"""A scan waits for a completed answers file. The name stays on this machine."""
from __future__ import annotations

import io
import json
import sqlite3
from pathlib import Path

from database_agent.db import open_database
from onboarding.answers import model_context, problems_in
from onboarding.gate import REFUSAL, allow_scan
from questions.store import declared_lives

import cli

TEMPLATE = Path(__file__).resolve().parents[2] / "profiles" / "answers.alana.json"

SECRET = "sk-onboarding-name-must-stay-local"

FILLED = {
    "person_name": SECRET,
    "lives": ["academic", "career"],
    "not_lives": ["business_operations"],
    "situations": {"academic": "academic.coursework"},
    "school": "Example School",
    "courses": [{"code": "CHEM 101", "name": "Chemistry", "term": "2026 Fall"}],
    "companies": ["Example Lab"],
    "projects": [],
    "leave_alone": [],
    "private_areas": ["medical"],
    "confirmed": True,
}


def test_the_shipped_template_is_not_a_completed_profile():
    problems = problems_in(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    text = " ".join(problems)
    assert "confirmed" in text
    assert "TODO" in text


def test_the_model_sentence_omits_the_persons_name():
    note = model_context(FILLED)
    assert SECRET not in note
    assert "Example School" in note
    assert "CHEM 101" in note
    assert "Example Lab" in note
    assert "academic" in note
    assert "needs_review" in note


def _files(database: Path) -> int:
    conn = sqlite3.connect(database)
    try:
        return conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    except sqlite3.OperationalError:
        return 0
    finally:
        conn.close()


def test_a_scan_without_answers_refuses_before_it_reads(tmp_path, monkeypatch):
    monkeypatch.delenv("FILESORTER_ONBOARDING_OPTIONAL", raising=False)
    folder = tmp_path / "inbox"
    folder.mkdir()
    (folder / "hours.txt").write_text("office hours Tuesday\n")
    database = tmp_path / "plan.sqlite"
    out = io.StringIO()
    code = cli.main(
        [str(folder), "--database", str(database), "--user", "t"], out=out)
    said = out.getvalue()
    assert code == 2
    assert REFUSAL in said
    assert _files(database) == 0


def test_a_template_does_not_scan(tmp_path, monkeypatch):
    monkeypatch.delenv("FILESORTER_ONBOARDING_OPTIONAL", raising=False)
    folder = tmp_path / "inbox"
    folder.mkdir()
    (folder / "hours.txt").write_text("office hours Tuesday\n")
    database = tmp_path / "plan.sqlite"
    out = io.StringIO()
    code = cli.main(
        [str(folder), "--database", str(database), "--user", "t",
         "--answers", str(TEMPLATE)], out=out)
    said = out.getvalue()
    assert code == 2
    assert "Nothing was scanned" in said
    assert "confirmed" in said
    assert _files(database) == 0


def test_filled_answers_open_the_allow_list_and_a_later_scan_may_proceed(tmp_path):
    folder = (tmp_path / "inbox").resolve()
    folder.mkdir()
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(FILLED), encoding="utf-8")
    conn = open_database(tmp_path / "plan.sqlite", scan_roots=[folder])
    cli._bootstrap(conn)
    assert allow_scan(
        conn, corpus_root=str(folder), answers=answers,
        user_id="t", recorded_at="2026-10-01T00:00:00+00:00") is None
    lives = declared_lives(conn)
    assert "academic" in lives
    assert "business_operations" not in lives
    assert allow_scan(
        conn, corpus_root=str(folder), answers=None,
        user_id="t", recorded_at="2026-10-01T00:00:01+00:00") is None
    conn.close()


def test_understand_with_a_fake_transport_exits_clean_and_audits(tmp_path, monkeypatch):
    """One ordinary file, no live API. The prompt carries the profile, not the name."""
    folder = tmp_path / "smoke"
    folder.mkdir()
    (folder / "hours.txt").write_text("office hours Tuesday\n")
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(FILLED), encoding="utf-8")
    database = tmp_path / "plan.sqlite"
    calls = []

    class Fake:
        def provider_name(self):
            return "fake"

        def locality(self):
            return "cloud"

        def complete(self, request):
            calls.append(request.prompt)
            assert SECRET not in request.prompt
            return {
                "choices": [{
                    "finish_reason": "stop",
                    "message": {"content": json.dumps({
                        "kind": "note",
                        "life_area": "academic",
                        "course": "CHEM 101",
                        "term": "2026 Fall",
                        "company": None,
                        "project": None,
                        "concerns": ["user"],
                        "confidence": 0.9,
                        "evidence_quote": "office hours",
                    })},
                }],
                "usage": {"prompt_tokens": 12, "completion_tokens": 8},
            }

    monkeypatch.setattr(cli, "_understanding_provider", lambda out: Fake())
    monkeypatch.setattr(cli, "_understanding_model_id", lambda out, role="fast": "deepseek-flash")
    out = io.StringIO()
    code = cli.main([
        str(folder), "--database", str(database), "--user", "t",
        "--answers", str(answers),
        "--enable-cloud", "--accept-cloud-understanding", "--understand",
    ], out=out)
    said = out.getvalue()
    assert code == 0, said[-800:]
    conn = sqlite3.connect(database)
    try:
        rows = conn.execute("SELECT COUNT(*) FROM understanding_audit").fetchone()[0]
    finally:
        conn.close()
    assert rows >= 1, said[-800:]
    assert calls, said[-800:]
    assert SECRET not in calls[0]
    assert "Example School" in calls[0]
    assert "office hours" in calls[0]


def test_optional_mode_without_a_file_does_not_refuse(tmp_path, monkeypatch):
    monkeypatch.setenv("FILESORTER_ONBOARDING_OPTIONAL", "1")
    folder = (tmp_path / "inbox").resolve()
    folder.mkdir()
    conn = open_database(tmp_path / "plan.sqlite", scan_roots=[folder])
    cli._bootstrap(conn)
    assert allow_scan(
        conn, corpus_root=str(folder), answers=None,
        user_id="t", recorded_at="2026-10-01T00:00:00+00:00") is None
    conn.close()
