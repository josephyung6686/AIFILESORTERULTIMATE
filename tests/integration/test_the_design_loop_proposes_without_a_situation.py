"""The product route on a folder nobody has named a situation for.

Amendment 2 of 14 Sep is the route: parse, the gist, a proposed structure,
then filing. Amendment 25 withholds child folders under an unjudged default.
It does not withhold the proposal, and it does not move a file.

This corpus is the two PHYS 1401 files the rest of the suite already uses.
No `--situation`, no `--answer`, no model. A plain run must reach the
proposal. A run that accepts the groups and stops at the tree must write
that tree and place nothing. The files stay where they were.
"""
from __future__ import annotations

import io
import shlex
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402
from placement.store import decisions_for_plan  # noqa: E402
from tree_design.store import latest_plan_version, nodes_for_version  # noqa: E402


def _corpus(tmp_path: Path) -> Path:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr Lee. Credits: 3.\n")
    (corpus / "PHYS 1401 homework 3.txt").write_text(
        "PHYS 1401 Homework 3\n\nSpring 2026 lecture notes.\n")
    return corpus


def _bytes_in(corpus: Path) -> dict[str, bytes]:
    return {path.relative_to(corpus).as_posix(): path.read_bytes()
            for path in corpus.rglob("*") if path.is_file()}


def _branch_the_freeze_named(report: str) -> str | None:
    """The branch `--freeze` told the person to move, from its own line."""
    for line in report.splitlines():
        if "--apply" not in line:
            continue
        parts = shlex.split(line)
        if "--apply" in parts:
            at = parts.index("--apply")
            if at + 1 < len(parts):
                return parts[at + 1]
    return None


def _run(corpus: Path, database: Path, *extra: str) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main([str(corpus), "--user", "jy", "--database", str(database),
                     *extra], out=out)
    return code, out.getvalue()


def test_a_folder_with_no_situation_still_proposes_and_moves_nothing(tmp_path):
    corpus = _corpus(tmp_path)
    before = sorted(path.name for path in corpus.iterdir())
    code, report = _run(corpus, tmp_path / "plan.sqlite")

    assert code == 0, report
    assert "This run was refused" not in report, report
    assert "What you have" in report, report
    assert ("These groups are proposed" in report
            or "The structure being proposed" in report), report
    proposal_at = report.find("These groups are proposed")
    if proposal_at < 0:
        proposal_at = report.find("The structure being proposed")
    question_at = report.find("Which of these is")
    assert question_at < 0 or proposal_at < question_at, report
    # The life the files drew, in the question under the outline. The answer
    # key stays the kind. A hold and a professional domain are not options.
    assert "The structure being proposed" in report, report
    assert "Education -- 2 file(s)" in report, report
    # The first screen is the folders the files already named. Accepting the
    # groups is what writes the outline file. This run has not accepted them,
    # and it has not moved a file.
    for folder in ("Spring2026", "PHYS1401", "syllabus", "homework"):
        assert folder in report, report
    assert "read as academic" not in report, report
    assert "Which of these is Education?" in report, report
    assert "Which of these is academic?" not in report, report
    assert "2 files sit under Education" in report, report
    assert "academic.coursework" not in report, report
    assert "k12-schooling" not in report, report
    assert "homeschool" not in report, report
    assert "--answer situation:academic=" in report, report
    assert sorted(path.name for path in corpus.iterdir()) == before


def test_accepting_groups_writes_the_tree_and_places_nothing(tmp_path):
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    code, report = _run(corpus, database, "--accept-groups",
                        "--stop-after", cli.STOP_AFTER_TREE)

    assert code == 0, report
    assert "Stopped at the proposed structure" in report, report
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        version = latest_plan_version(conn)
        assert version is not None, report
        assert nodes_for_version(conn, version), report
        assert not list(decisions_for_plan(conn, plan_version=version)), report
    finally:
        conn.close()
    assert (corpus / "PHYS 1401 syllabus.txt").is_file()
    assert (corpus / "PHYS 1401 homework 3.txt").is_file()
    outline = (database.parent / "proposed-structure.txt").read_text(
        encoding="utf-8")
    assert "Education" in outline, outline
    # The files already named these. The outline is those folders, under the
    # life, with no situation id on the screen and nothing moved.
    def _row(label: str) -> str:
        return next((line for line in outline.splitlines()
                     if f"{label}  [" in line), "")

    assert "2 files" in _row("Education"), outline
    assert "2 files" in _row("Spring2026"), outline
    assert "2 files" in _row("PHYS1401"), outline
    assert "1 file" in _row("homework"), outline
    assert "1 file" in _row("syllabus"), outline
    assert "academic.coursework" not in report, report
    assert "academic.coursework" not in outline, outline


def test_the_proposed_folders_file_without_a_situation_id(tmp_path):
    """Freeze and apply the folders the files already named.

    No `--answer` and no `--situation`. The person accepts the groups, the
    outline is the life and the levels the files carry, freeze names a
    branch, apply moves a file into it, undo puts the bytes back.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    before = _bytes_in(corpus)

    code, report = _run(corpus, database, "--accept-groups")
    assert code == 0, report
    assert _bytes_in(corpus) == before, report
    outline = (database.parent / "proposed-structure.txt").read_text(
        encoding="utf-8")
    for folder in ("Education", "Spring2026", "PHYS1401"):
        assert folder in outline, outline

    code, report = _run(corpus, database, "--freeze")
    assert code == 0, report
    branch = _branch_the_freeze_named(report)
    assert branch, report

    code, report = _run(corpus, database, "--apply", branch)
    moved = [path.relative_to(corpus).as_posix()
             for path in corpus.rglob("*") if path.is_file()]
    assert code == 0, report
    assert any("/" in name for name in moved), report
    assert any("PHYS1401" in name or "Spring2026" in name for name in moved), (
        report, moved)

    code, report = _run(corpus, database, "--undo-everything")
    assert code == 0, report
    assert _bytes_in(corpus) == before, report


def test_the_person_can_answer_freeze_move_one_file_and_undo(tmp_path):
    """A folder nobody named still has a way through.

    Propose, answer the life at the kind's key, accept, freeze, move one
    branch, undo. The corpus is a copy in the test's own directory. Nothing
    here reads the owner's folder.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    before = _bytes_in(corpus)

    code, report = _run(corpus, database)
    assert code == 0, report
    assert "Which of these is Education?" in report, report

    code, report = _run(
        corpus, database, "--answer", "situation:academic=academic.coursework",
        "--accept-groups")
    assert code == 0, report
    assert _bytes_in(corpus) == before, report

    code, report = _run(corpus, database, "--freeze")
    assert code == 0, report
    branch = _branch_the_freeze_named(report)
    assert branch, report

    code, report = _run(corpus, database, "--apply", branch)
    moved = [path.relative_to(corpus).as_posix()
             for path in corpus.rglob("*") if path.is_file()]
    assert code == 0, report
    assert any("/" in name for name in moved), report

    code, report = _run(corpus, database, "--undo-everything")
    assert code == 0, report
    assert _bytes_in(corpus) == before, report
