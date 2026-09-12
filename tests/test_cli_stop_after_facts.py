# tests/test_cli_stop_after_facts.py
"""`--stop-after facts`: read every file, write what you found, and stop there.

The run the owner asked for reaches site A -- the model fact pass -- and goes no
further: no template question, no group observation, no tree, no placement. What
distinguishes it from a run that crashed halfway is that it SAYS so, which is what
the sentence at the bottom of this screen is for.

None of these tests types `ACCEPTS_THE_PROPOSAL`. That is deliberate and it is not
the drafts rule showing through: `--accept-groups` is one of the four gestures this
flag refuses, because a run that ends at the facts proposes no group to accept.
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cli  # noqa: E402


def _corpus(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir(exist_ok=True)
    (corpus / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr Lee. Credits: 3.\n")
    (corpus / "PHYS 1401 homework 3.txt").write_text(
        "PHYS 1401 Homework 3\n\nSpring 2026 lecture notes.\n")
    return corpus


def _counts(database, *tables) -> dict[str, int]:
    """Row counts read on a FRESH connection, so what is counted is what persisted.

    The table is looked up in `sqlite_master` first and its absence is a failure
    rather than a zero: "no rows in `tree_nodes`" and "no `tree_nodes`" read the
    same in an assertion and only one of them is this flag working.
    """
    conn = sqlite3.connect(database)
    try:
        found: dict[str, int] = {}
        for table in tables:
            exists = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
                (table,)).fetchone()
            assert exists, f"{table} is not a table in {database}"
            found[table] = conn.execute(
                f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        return found
    finally:
        conn.close()


def _stopped_run(tmp_path, *extra):
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Papers", "--user", "jy",
                     "--database", str(database),
                     "--stop-after", cli.STOP_AFTER_FACTS, *extra], out=out)
    return code, out.getvalue(), database


def test_a_run_stopped_after_the_facts_keeps_them_and_designs_nothing(tmp_path):
    """The whole of what the flag promises, in one run.

    The scan happened -- `extraction_runs` holds what the readers did -- and the
    three blocks that report it printed. What did not happen is everything site A
    hands on to: no group, no tree node, no placement decision.
    """
    code, printed, database = _stopped_run(tmp_path)

    assert code == 0, printed
    # The report of what the scan found still prints: the fact pass's own closed
    # sum over the roster is part of what this run did, not part of the proposal.
    assert "Coverage:" in printed, printed
    assert "Stopped after the fact pass" in printed, printed
    assert "nothing was grouped and nothing was placed" in printed, printed
    # And the proposal was not printed under it. `report` draws the tree and
    # invites the freeze, and `report` is what the early return in `main` skips.
    assert "--freeze" not in printed, printed

    counts = _counts(database, "extraction_runs", "text_units",
                     "classifications", "file_facts", "groups", "tree_nodes",
                     "placement_decisions")
    assert counts["extraction_runs"] > 0, counts
    assert counts["text_units"] > 0, counts
    assert counts["classifications"] > 0, counts
    assert counts["file_facts"] > 0, counts
    assert counts["groups"] == 0, counts
    assert counts["tree_nodes"] == 0, counts
    assert counts["placement_decisions"] == 0, counts


def test_the_pass_says_it_did_not_run_and_the_run_still_stops_cleanly(tmp_path):
    """No key and no local model is an ORDINARY way for this run to go.

    `tests/conftest.py` takes both away from every test in this suite, so this is
    the run a person on an unconfigured machine gets. The fact pass returns early
    with a reason, `_reconcile_the_roster` prints that reason against the files it
    covers, and the stop sentence comes after it rather than instead of it: a
    person is told what the pass did AND that the run ended where they asked.
    """
    code, printed, _ = _stopped_run(tmp_path)

    assert code == 0, printed
    assert cli.NOT_RUN_NO_MODEL in printed, printed
    assert printed.index(cli.NOT_RUN_NO_MODEL) < printed.index(
        "Stopped after the fact pass"), printed


def test_stopping_after_the_facts_and_freezing_is_refused(tmp_path):
    """Two answers to one question, and neither is guessed.

    A freeze turns a proposal into a plan, and a run that ends at the facts makes
    no proposal. Honouring the stop would leave a person believing they had a plan
    they do not have; honouring the freeze would run the pipeline they asked it not
    to. `84` §6: refuse, and say which two things were asked for.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Papers", "--user", "jy",
                     "--database", str(database),
                     "--stop-after", cli.STOP_AFTER_FACTS, "--freeze"], out=out)
    printed = out.getvalue()

    assert code == 2, printed
    assert "--stop-after facts" in printed, printed
    assert "--freeze" in printed, printed
    # Refused BEFORE the scan, which is the difference between a refusal and a
    # rollback: the database the run would have written was never opened.
    assert not database.exists(), printed


def test_every_gesture_that_needs_the_proposal_is_refused_beside_it(tmp_path):
    """The other three, each on its own, so a person who typed one sees that one.

    `--apply` is `action="append"` and the other two are switches, so the check
    reads three different shapes of "was this typed"; a list comprehension that got
    one of them wrong would let that flag through silently.
    """
    corpus = _corpus(tmp_path)
    for flag in ("--apply-everything", "--accept-groups"):
        out = io.StringIO()
        code = cli.main([str(corpus), "--situation", "academic.coursework",
                         "--label", "Papers", "--user", "jy",
                         "--database", str(tmp_path / "plan.sqlite"),
                         "--stop-after", cli.STOP_AFTER_FACTS, flag], out=out)
        assert code == 2, out.getvalue()
        assert flag in out.getvalue(), out.getvalue()

    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Papers", "--user", "jy",
                     "--database", str(tmp_path / "plan.sqlite"),
                     "--stop-after", cli.STOP_AFTER_FACTS,
                     "--apply", "Papers"], out=out)
    assert code == 2, out.getvalue()
    assert "--apply" in out.getvalue(), out.getvalue()
