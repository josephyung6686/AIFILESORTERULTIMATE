"""Point at a folder, preview the sort, apply it, undo it.

No situation flag and no model. The homework sheet prints a due year beside
the course code; that year must not steal the course. The syllabus and the
homework land in different leaves of the same course. Nothing moves until
apply, and undo puts the bytes back.
"""
from __future__ import annotations

import io
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402


def _corpus(tmp_path: Path) -> Path:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "PHYS 1403 homework 2.txt").write_text(
        "PHYS 1403 Homework 2\n\nSpring 2026. Due 2026-03-01. "
        "Solve the following.\n")
    (corpus / "PHYS 1403 syllabus.txt").write_text(
        "PHYS 1403 Syllabus\n\nSpring 2026. Instructor: A. Raymer.\n")
    return corpus


def _bytes_in(corpus: Path) -> dict[str, bytes]:
    return {path.relative_to(corpus).as_posix(): path.read_bytes()
            for path in corpus.rglob("*") if path.is_file()}


def _paths(corpus: Path) -> set[str]:
    return {path.relative_to(corpus).as_posix()
            for path in corpus.rglob("*") if path.is_file()}


def _run(corpus: Path, database: Path, *extra: str) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main([str(corpus), "--user", "student", "--database", str(database),
                     *extra], out=out)
    return code, out.getvalue()


def _branches_the_freeze_named(report: str) -> list[str]:
    found: list[str] = []
    for line in report.splitlines():
        if "--apply" not in line:
            continue
        parts = shlex.split(line)
        if "--apply" not in parts:
            continue
        at = parts.index("--apply")
        if at + 1 < len(parts):
            found.append(parts[at + 1])
    return found


def test_preview_apply_and_undo_file_the_course_and_put_it_back(tmp_path):
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    before = _bytes_in(corpus)

    code, report = _run(corpus, database, "--accept-groups")
    assert code == 0, report
    assert _bytes_in(corpus) == before
    outline = (database.parent / "proposed-structure.txt").read_text(
        encoding="utf-8")
    for folder in ("PHYS1403", "homework", "syllabus"):
        assert folder in outline, outline

    code, report = _run(corpus, database, "--freeze")
    assert code == 0, report
    assert _bytes_in(corpus) == before
    branches = _branches_the_freeze_named(report)
    assert branches, report
    # Freeze prints one leaf per line. Applying the parent is not offered;
    # each printed branch is what moves that leaf.
    apply_args: list[str] = []
    for name in branches:
        apply_args.extend(("--apply", name))

    code, report = _run(corpus, database, *apply_args)
    assert code == 0, report
    placed = _paths(corpus)
    homework = next(path for path in placed if path.endswith("homework 2.txt"))
    syllabus = next(path for path in placed if path.endswith("syllabus.txt"))
    assert homework.endswith("PHYS1403/homework/PHYS 1403 homework 2.txt"), placed
    assert syllabus.endswith("PHYS1403/syllabus/PHYS 1403 syllabus.txt"), placed

    code, report = _run(corpus, database, "--undo-everything")
    assert code == 0, report
    assert _bytes_in(corpus) == before
