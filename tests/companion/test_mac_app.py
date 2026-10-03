"""The Mac window's engine calls.

A scan refuses when answers are unfinished or folder access is missing.
A normal scan does not move or rename files. An empty folder is one with
zero files on disk, and it is removed only on an explicit yes.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from onboarding.answers import load_answers
from companion.service import (
    CompanionService, build_scan_argv, empty_briefing, resolve_granted,
)

ROOT = Path(__file__).resolve().parents[2]


def _ready(folders=("Documents",)) -> dict:
    return {
        "schemaVersion": 1,
        "finished": True,
        "profile": "student",
        "personName": "Example Person",
        "school": "Example School",
        "folderAccess": {"state": "granted", "folders": list(folders)},
        "categories": [{"id": "c1", "name": "Courses"}],
        "refusedCategories": [],
        "context": {"courses": "", "companies": "", "projects": ""},
        "leaveAlone": [],
        "unmatched": "unplaced",
        "sensitiveMaterial": "held",
        "fileOperations": "read-only",
    }


def _service(tmp_path: Path) -> CompanionService:
    home = tmp_path / "home"
    home.mkdir()
    support = tmp_path / "support"
    support.mkdir()
    return CompanionService(
        home=home,
        answers=support / "answers.json",
        database=support / "plan.sqlite",
    )


def test_unfinished_answers_do_not_start_a_scan(tmp_path: Path):
    service = _service(tmp_path)
    docs = service.home / "Documents"
    docs.mkdir()
    (docs / "notes.txt").write_text("keep me\n", encoding="utf-8")
    service.answers.write_text('{"confirmed": false}\n', encoding="utf-8")
    snapshot = _ready()
    snapshot["finished"] = False
    result = service.scan(snapshot)
    assert result["ok"] is False
    assert "Finish onboarding" in result["error"]
    assert json.loads(service.answers.read_text(encoding="utf-8"))["confirmed"] is False
    assert not service.database.exists()
    assert result["briefing"] == empty_briefing()
    assert (docs / "notes.txt").read_text(encoding="utf-8") == "keep me\n"


def test_missing_folder_access_does_not_start_a_scan(tmp_path: Path):
    service = _service(tmp_path)
    service.answers.write_text('{"confirmed": false}\n', encoding="utf-8")
    missing = _ready()
    missing["folderAccess"] = {"state": "not-requested", "folders": ["Documents"]}
    result = service.scan(missing)
    assert result["ok"] is False
    assert "Allow folder access" in result["error"]
    assert json.loads(service.answers.read_text(encoding="utf-8"))["confirmed"] is False
    assert not service.database.exists()

    denied = _ready()
    denied["folderAccess"] = {"state": "denied", "folders": ["Documents"]}
    result = service.scan(denied)
    assert result["ok"] is False
    assert "denied" in result["error"].lower()
    assert not service.database.exists()
    assert result["briefing"]["found"] is None
    assert result["briefing"]["complete"] is False


def test_saving_a_finished_snapshot_writes_the_answers_file_atomically(tmp_path: Path):
    service = _service(tmp_path)
    saved = service.save_answers(_ready())
    assert saved["ok"] is True
    loaded = load_answers(service.answers)
    assert loaded["confirmed"] is True
    assert loaded["lives"] == ["academic"]
    assert "finance" not in loaded["lives"]
    assert not list(service.answers.parent.glob(".answers.json.*.tmp"))
    raw = service.answers.read_text(encoding="utf-8")
    assert raw.endswith("\n")
    assert json.loads(raw)["person_name"] == "Example Person"


def test_a_normal_scan_does_not_move_or_rename(tmp_path: Path):
    service = _service(tmp_path)
    docs = service.home / "Documents"
    docs.mkdir()
    original = docs / "notes.txt"
    original.write_text("office hours\n", encoding="utf-8")
    before = original.read_bytes()
    where = original.resolve()
    result = service.scan(_ready())
    assert original.resolve() == where
    assert original.read_bytes() == before
    assert "--apply" not in service.last_argv
    assert "--undo" not in service.last_argv
    assert "--undo-everything" not in service.last_argv
    assert "--apply-everything" not in service.last_argv
    assert str(service.database.resolve()) in service.last_argv
    assert service.last_argv.count("--database") == 1
    assert result["ok"] is True, result
    assert result["briefing"]["complete"] is True
    assert result["briefing"]["found"] == 1
    others = list(service.database.parent.glob("*.sqlite"))
    assert others == [service.database]


def test_the_paid_move_path_stays_off(tmp_path: Path):
    service = _service(tmp_path)
    docs = service.home / "Documents"
    docs.mkdir()
    (docs / "notes.txt").write_text("stay\n", encoding="utf-8")
    result = service.scan(_ready(), paid_moves=True)
    assert result["ok"] is False
    assert "paid" in result["error"].lower()
    assert service.last_argv == []
    assert not service.database.exists()
    assert (docs / "notes.txt").read_text(encoding="utf-8") == "stay\n"
    try:
        build_scan_argv(
            [docs], database=service.database, answers=service.answers,
            user="you", paid_moves=True)
    except Exception as refused:
        assert "paid" in str(refused).lower()
    else:
        raise AssertionError("the paid path must refuse")


def test_downloads_is_resolved_under_the_given_home(tmp_path: Path):
    home = tmp_path / "home"
    downloads = home / "Downloads"
    downloads.mkdir(parents=True)
    roots = resolve_granted(
        {"folderAccess": {"state": "granted", "folders": ["Downloads"]}},
        home=home,
    )
    assert roots == [downloads.resolve()]
    assert roots[0] != Path.home() / "Downloads"


def test_empty_means_zero_files_and_removal_needs_yes(tmp_path: Path):
    service = _service(tmp_path)
    docs = service.home / "Documents"
    empty = docs / "EmptyNest"
    holding = docs / "HasFile"
    empty.mkdir(parents=True)
    holding.mkdir()
    kept = holding / "page.txt"
    kept.write_text("still here\n", encoding="utf-8")
    snapshot = _ready()
    view = service.workspace(snapshot)
    listed = {row["path"] for row in view["emptyFolders"]}
    assert str(empty.resolve()) in listed
    assert str(holding.resolve()) not in listed
    assert str(docs.resolve()) not in listed

    refused = service.remove_empty(str(empty), "no", snapshot)
    assert refused["removed"] is False
    assert empty.is_dir()

    blocked = service.remove_empty(str(holding), "yes", snapshot)
    assert blocked["removed"] is False
    assert kept.read_text(encoding="utf-8") == "still here\n"

    removed = service.remove_empty(str(empty), "yes", snapshot)
    assert removed["removed"] is True
    assert not empty.exists()
    assert kept.resolve().is_file()


def test_briefing_counts_stay_empty_without_a_finished_scan(tmp_path: Path):
    service = _service(tmp_path)
    assert service.workspace(_ready())["outline"] == ""
    assert service.workspace(_ready())["review"] == []
    assert empty_briefing()["found"] is None


def test_the_command_opens_a_mac_window_not_a_browser_page():
    if sys.platform == "darwin":
        return
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    proc = subprocess.run(
        [sys.executable, "-m", "companion"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 2
    assert "Mac window" in proc.stderr
    assert "index.html" not in proc.stdout
    assert "open index.html" not in proc.stderr


def test_the_six_screens_are_the_onboarding_flow():
    page = (ROOT / "src" / "onboarding" / "ui" / "source" / "ui.html").read_text(
        encoding="utf-8")
    for label in (
        "Folder access", "Your profile", "Areas of work", "Your categories",
        "Local scan", "Archive briefing",
    ):
        assert label in page
    assert "Needs review" in page
    assert 'value="student"' in page
    assert "checked" not in page


_OLD_PALETTE = ("#364C84", "#95B1EE", "#D9E3FA", "#E7F1A8", "#087bff", "#0069ff", "#2497ff")


def test_primary_action_uses_design_blue_and_ember_is_limited():
    ui = ROOT / "src" / "onboarding" / "ui"
    tokens = (ui / "tokens.css").read_text(encoding="utf-8")
    components = (ui / "components.css").read_text(encoding="utf-8")
    styles = (ui / "source" / "styles.css").read_text(encoding="utf-8")
    surfaces = (ui / "source" / "folder-surfaces.css").read_text(encoding="utf-8")
    page = (ui / "source" / "ui.html").read_text(encoding="utf-8")
    script = (ui / "source" / "controller.js").read_text(encoding="utf-8")
    built = (ui / "index.html").read_text(encoding="utf-8")
    assert "--blue-600: #1F5BE0" in tokens
    assert "Manrope" in tokens and "JetBrains Mono" in tokens
    primary = components.split(".fc-btn--primary", 1)[1].split("}", 1)[0]
    assert "var(--blue-600)" in primary
    assert 'class="fc-btn fc-btn--primary" id="fc-next"' in page
    real = components.split(".fc-btn--real{", 1)[1].split("}", 1)[0]
    assert "var(--ember-600)" in real
    ground = components.split(".fc-empty__pip{", 1)[1].split("}", 1)[0]
    assert "var(--ember-500)" in ground
    assert "--ember-500: #FF5A36" in tokens
    assert "--ember-600: #D4401C" in tokens
    assert "fc-empty__pip" in page
    assert "tuck-carry.svg" in page
    assert "tuck-idle.svg" in page
    assert "tuck-rest" in script
    assert "move-real-files" not in page
    assert "move-real-files" not in script
    assert page.count("fc-btn--real") == 0
    assert script.count("fc-btn--real") == 1
    removal = script.split("case 'remove-empty'", 1)[1].split("case ", 1)[0]
    assert "fc-btn--real" not in removal
    assert ",true)" in removal
    assert "ember" not in styles.lower()
    assert "ember" not in surfaces.lower()
    visible = "\n".join((tokens, components, styles, surfaces, page, script, built))
    for old in _OLD_PALETTE:
        assert old.lower() not in visible.lower()
