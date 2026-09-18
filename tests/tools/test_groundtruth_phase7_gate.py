# tests/tools/test_groundtruth_phase7_gate.py
"""`106` Phase 7 §F's gate, exercised over one real run database.

One offline run over a two-file corpus (the shape `tests/test_cli.py`'s residual
tests use): a course syllabus and a file about nothing. The second is a leftover
no branch can hold, so the run surfaces a review set for it, mints the home that
set is offered under `98 Review and Unsorted` (`106` Phase 7 §D.4), and freezes
again. The gate must read THAT version, find the home, and count nothing wrong.

Nothing under the owner's disk is read; the corpus is written into `tmp_path`.
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402
from tools.groundtruth import phase7_gate  # noqa: E402


def _one_run(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr Lee. Credits: 3.\n")
    (corpus / "misc.txt").write_text("Nothing in particular about anything.\n")
    database = tmp_path / "plan.sqlite"
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Papers", "--user", "jy", "--accept-groups",
                     "--database", str(database)], out=out)
    assert code == 0, out.getvalue()
    return database, out.getvalue()


def test_the_gate_reads_the_latest_frozen_version_and_finds_every_offered_home(tmp_path):
    """SABOTAGE: read the sets off the latest version alone -- they name the
    version they were surfaced against, one re-freeze earlier, and every
    home reads as missing."""
    database, printed = _one_run(tmp_path)
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        found = phase7_gate.measure(conn)
        surfaced_against = {row[0] for row in conn.execute(
            "SELECT DISTINCT plan_version FROM residual_sets")}
    finally:
        conn.close()
    assert found["frozen_version"] is not None
    # The premise of the sabotage above, checked: the sets name a version
    # EARLIER than the one the homes were frozen onto.
    assert surfaced_against and found["frozen_version"] not in surfaced_against
    assert 0 in found["depth_histogram"]
    assert found["single_child_runs"] == 0
    assert found["single_file_roots"] == 0
    # The leftover set was offered `Review Later` and the home was minted.
    assert found["unhomed_ordinary_sets"] == 0
    assert "Offered home: 98 Review and Unsorted / Review Later" in printed


def test_the_script_prints_counts_only_and_exits_zero_on_a_clean_run(tmp_path, capsys):
    database, _printed = _one_run(tmp_path)
    assert phase7_gate.main(str(database)) == 0
    said = capsys.readouterr().out
    assert "depth distribution" in said
    assert "observable only after Phase 6" in said
    # Aggregates only: no name from the corpus reaches the screen.
    assert "syllabus" not in said.lower() and "misc" not in said.lower()
