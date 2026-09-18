"""`--stop-after tree`: propose the structure, write the outline, place nothing.

`00` amendment 2 of 14 Sep, the owner's flow: the tree is "shown to the person as
something they edit ... BEFORE any file is placed under it". Until `106` Phase 5
the product could not stop there: `run_production_p8_p11` designs and places in
one call, and placement spends a model call per file on a tree the person is
about to edit.

The groups gate already exists (a run without `--accept-groups` stops before the
tree) and so does the placement gate (`--freeze`). This is the one between them.
It REQUIRES `--accept-groups`, because a tree is built from accepted groups and
nothing else.
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cli  # noqa: E402
from placement.store import decisions_for_plan  # noqa: E402
from tree_design.store import latest_plan_version, nodes_for_version  # noqa: E402

from test_cli_stop_after_facts import _corpus  # noqa: E402


def _stopped_at_the_tree(tmp_path, *extra):
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Papers", "--user", "jy",
                     "--database", str(database), "--accept-groups",
                     "--stop-after", cli.STOP_AFTER_TREE, *extra], out=out)
    return code, out.getvalue(), database


def test_the_stages_are_the_gate_the_facts_and_the_tree_in_the_runs_own_order():
    assert cli.STOP_AFTER_STAGES == (
        cli.STOP_AFTER_GATE, cli.STOP_AFTER_FACTS, cli.STOP_AFTER_TREE)


def test_a_run_stopped_at_the_tree_writes_the_tree_and_places_nothing(tmp_path):
    """SABOTAGE: return from `run_production_p8_p11` AFTER `run_corpus` instead of
    before it -- the count of decisions below becomes non-zero, and the person's
    model budget was spent on a tree they had not yet read."""
    code, printed, database = _stopped_at_the_tree(tmp_path)
    assert code == 0, printed
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        version = latest_plan_version(conn)
        assert version is not None, printed
        assert nodes_for_version(conn, version), "no tree was written"
        assert not list(decisions_for_plan(conn, plan_version=version)), (
            "the run placed files it was told to stop before placing")
    finally:
        conn.close()


def test_a_run_stopped_at_the_tree_says_so_and_writes_the_outline(tmp_path):
    """What tells a person their run ended early is that it SAYS so
    (`_print_stopped_after_facts`'s rule), and the outline is what they were
    stopped for. SABOTAGE: print the outline and not the sentence -- a screen
    that stops after an outline is indistinguishable from one that crashed
    before placement."""
    code, printed, database = _stopped_at_the_tree(tmp_path)
    assert code == 0, printed
    assert "Stopped at the proposed structure" in printed, printed
    assert "The structure being proposed, and yours to change:" in printed, printed
    assert "--freeze" not in printed, printed
    outline = database.parent / cli.STRUCTURE_FILENAME
    assert outline.exists(), printed
    assert "# plan:" in outline.read_text(encoding="utf-8")


def test_the_tree_stop_still_refuses_a_freeze_beside_it(tmp_path):
    """The rule for the gestures that need placement is kept; only
    `--accept-groups` is let through, because this stage needs it."""
    code, printed, _ = _stopped_at_the_tree(tmp_path, "--freeze")
    assert code == 2, printed
    assert "two things at once" in printed, printed
