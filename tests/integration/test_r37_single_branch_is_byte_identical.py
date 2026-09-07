# tests/integration/test_r37_single_branch_is_byte_identical.py
"""`104` R-37 / R-100, ruling (4): with ONE branch, offline, nothing changes.

The per-branch situation answers the situation per top-level branch the run
proposes instead of once per folder. On a folder that is all one life -- every
kind-of-file anchor the library owns belongs to the situation the person typed --
the run proposes one branch, and the ruling pins that such a run is byte-identical
to the run before the change: the same screen and the same derived records.

**The fixture was captured at `ec6e46f`, before any of R-37's code existed**, by
running this module as a script (`python3 tests/integration/<this file> capture`).
A fixture captured after the change would prove only that the code agrees with
itself. Every minted id is replaced by what it names, exactly as
`test_two_runs_of_one_folder_agree` replaces them, so what is compared is what the
run concluded and not which uuid it drew.

The corpus is `test_local_model_fact_pass._corpus`'s six files: a syllabus, a
lecture, a homework, a problem set, an application essay and a passport scan. The
anchors the work-type rule finds on it are all academic's, so it is one branch.
"""
from __future__ import annotations

import importlib.util
import io
import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "r37_single_branch_offline.json"

SITUATION = "academic.coursework"
LABEL = "Coursework"

UUID = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
STAMP = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)?")
PLAN_VERSION = re.compile(r"version_[0-9a-f]{6,}_(\d+)")
NODE_ID = re.compile(r"node_[0-9a-f]{6,}_(\d+)")


def _corpus(root: Path) -> Path:
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n")
    (corpus / "Lecture 08.txt").write_text(
        "Lecture 08 - Rotational Dynamics\nPHYS 1401\nTorque and angular momentum.\n")
    (corpus / "HW 3.txt").write_text(
        "Homework 3\n\nProblem 1. A ball is thrown upward...\n")
    (corpus / "BUSIB 4300 Problem Set 4.txt").write_text(
        "Problem Set 4\nFall 2024\n\nProblem 1. Compute the net present value.\n")
    (corpus / "Columbia Essay.txt").write_text(
        "Dear Admissions Committee at Columbia University,\nMy essay follows.\n")
    (corpus / "Passport scan.txt").write_text(
        "Passport\nHong Kong Special Administrative Region\n"
        "Passport No. K12345678\nDate of birth: 1 January 1990\n")
    return corpus


def _normaliser():
    """`test_two_runs_of_one_folder_agree._normalised`, imported by path so there
    is ONE definition of what "the same records" means."""
    spec = importlib.util.spec_from_file_location(
        "two_runs", HERE / "test_two_runs_of_one_folder_agree.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._normalised


def _screen(printed: str, corpus: Path, database: Path) -> list[str]:
    text = printed.replace(str(corpus), "<corpus>").replace(
        str(database), "<database>")
    text = PLAN_VERSION.sub(lambda found: f"<plan:{found.group(1)}>", text)
    text = NODE_ID.sub(lambda found: f"<node:{found.group(1)}>", text)
    text = UUID.sub("<uuid>", text)
    text = STAMP.sub("<stamp>", text)
    return text.splitlines()


def run_and_normalise(root: Path) -> dict:
    corpus = _corpus(root)
    database = root / "holder" / "plan.sqlite"
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", SITUATION, "--label", LABEL,
                     "--user", "t", "--database", str(database)], out=out)
    assert code == 0, out.getvalue()
    return {"screen": _screen(out.getvalue(), corpus, database),
            "tables": _tables(database, root)}


def _tables(database: Path, root: Path) -> dict[str, list[str]]:
    """The shared normaliser, plus the two things that differ ONLY because the
    corpus sits under a different temporary directory each time: the directory
    itself, and the content-addressed key of a `path`-zone observation, which is
    a digest OF that directory. Each is replaced by what it names."""
    import sqlite3
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        keys = {row["observation_key"]: (
            f"<obs:path:{Path(row['current_path']).name}>")
            for row in conn.execute(
                "SELECT e.observation_key, f.current_path FROM evidence e "
                "JOIN files f ON f.file_id = e.file_id "
                "WHERE e.location LIKE '%\"zone\":\"path\"%'")}
    finally:
        conn.close()
    tables = _normaliser()(database)

    def say(row: str) -> str:
        for key, name in keys.items():
            row = row.replace(key, name)
        # The resolved path first: macOS puts a temporary directory under
        # `/var/folders`, which is a symlink to `/private/var/folders`, and the
        # scan records whichever spelling it was handed.
        return row.replace(str(root.resolve()), "<tmp>").replace(
            str(root), "<tmp>")

    return {table: sorted(say(row) for row in rows)
            for table, rows in tables.items()}


def test_a_single_branch_offline_run_is_byte_identical_to_before_r37(tmp_path):
    expected = json.loads(FIXTURE.read_text())
    actual = run_and_normalise(tmp_path)

    assert actual["screen"] == expected["screen"], "\n".join(
        line for line in _diff(expected["screen"], actual["screen"]))
    for table, rows in expected["tables"].items():
        assert actual["tables"].get(table) == rows, (
            table + "\n" + "\n".join(_diff(rows, actual["tables"].get(table, []))))


def _diff(before: list[str], after: list[str]) -> list[str]:
    import difflib
    return list(difflib.unified_diff(before, after, "captured", "now", lineterm=""))


if __name__ == "__main__":
    if sys.argv[1:] != ["capture"]:
        sys.exit("usage: capture")
    import tempfile
    with tempfile.TemporaryDirectory() as scratch:
        FIXTURE.parent.mkdir(exist_ok=True)
        FIXTURE.write_text(json.dumps(run_and_normalise(Path(scratch)),
                                      indent=1, sort_keys=True) + "\n")
    print(f"captured {FIXTURE}")
