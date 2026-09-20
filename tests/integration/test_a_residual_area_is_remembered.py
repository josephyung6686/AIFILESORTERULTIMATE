"""A catch-all area you turned on stays on, and `--answer ...=revoke` turns it off.

`110` §2.4, item 1. `residual_library_choices` ran on FLAGS ALONE: everything the
person settled about §7.4's nine areas lived in one invocation's argv and nothing
else, so somebody who had decided that Review Later belongs in their plan had to
re-type `--residual "Review Later"` on every run for ever, and a run that forgot it
quietly built a different plan. §3.1's list of what a control change preserves ends
with "**Residual choices** -- today, nothing".

The other four answers this product keeps live in `structural_questions` /
`structural_answers`, keyed by question id and scope and never by plan version. A
residual choice is now one of them: a `residual:<area>` question at corpus scope,
answered `enable` or `disable`. `--answer "residual:Review Later=revoke"` withdraws
it through the gesture that already withdraws every other answer, and
`--explain "residual:Review Later"` reads it back through the surface that already
explains every other answer. Neither needed anything built for it.

**Three runs, because two cannot tell the fact from the flag.** Run one names the
area. Run two names NOTHING and is the whole assertion: the area is in the plan
because the product remembers, not because argv said so. Run three revokes.
"""
from __future__ import annotations

import io
import sqlite3
from pathlib import Path

import cli

AREA = "Review Later"
ORIGIN = "residual:Review Later"
QUESTION = "residual:Review Later"

CORPUS = {
    "phys ps1.txt": "PHYS 1401 problem set 1\nMechanics homework, due "
                    "2024-02-10.\nStudent: jy\n",
    "phys ps2.txt": "PHYS 1401 problem set 2\nMechanics homework, due "
                    "2024-02-17.\nStudent: jy\n",
}


def _run(corpus: Path, database: Path, *extra: str) -> str:
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Uni", "--user", "jy",
                     "--database", str(database), "--accept-groups", *extra],
                    out=out)
    printed = out.getvalue()
    assert code == 0, printed
    return printed


def _corpus(tmp_path: Path) -> tuple[Path, Path]:
    corpus = tmp_path / "Uni"
    corpus.mkdir()
    for name, body in CORPUS.items():
        (corpus / name).write_text(body)
    return corpus, tmp_path / "plan.sqlite"


def _area_is_in_the_newest_plan(database: Path) -> bool:
    """Read off the tree the run wrote, not off the words it printed.

    The origin key is `residual:<template name>` (`node_key.residual_key`), which
    is the area's identity and not its display label -- a person who renames the
    area still has the same area, and a test that looked for the label would be
    asserting about the name rather than about the memory.
    """
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        newest = conn.execute(
            "SELECT plan_version_id FROM plan_versions "
            "ORDER BY created_at DESC, plan_version_id DESC LIMIT 1").fetchone()
        assert newest is not None
        return bool(conn.execute(
            "SELECT 1 FROM tree_nodes WHERE plan_version_id = ? "
            "AND origin_node_id = ?", (newest[0], ORIGIN)).fetchone())
    finally:
        conn.close()


def test_an_area_named_on_one_run_is_still_in_the_plan_on_the_next(tmp_path):
    """SABOTAGE: drop the stored read and run two builds a plan without it."""
    corpus, database = _corpus(tmp_path)
    _run(corpus, database, "--residual", AREA)
    assert _area_is_in_the_newest_plan(database), "the first run built no area"

    _run(corpus, database)
    assert _area_is_in_the_newest_plan(database), (
        "the area was named once and the next run built a plan without it")


def test_an_area_nobody_ever_named_is_not_in_the_plan(tmp_path):
    """The negative half, without which the test above passes on a product that
    enables all nine: `00` says these templates "are not automatically created"."""
    corpus, database = _corpus(tmp_path)
    _run(corpus, database)
    assert not _area_is_in_the_newest_plan(database)


def test_revoking_the_answer_turns_the_area_off(tmp_path):
    """§12 requires an answer to be "edited, revoked, or re-run", and this one is
    withdrawn by the gesture that withdraws the other four -- `--answer
    <question>=revoke`, which `live_answer` has honoured since P15 shipped."""
    corpus, database = _corpus(tmp_path)
    _run(corpus, database, "--residual", AREA)
    _run(corpus, database, "--answer", f"{QUESTION}=revoke")
    assert not _area_is_in_the_newest_plan(database), (
        "the answer was revoked and the area is still in the plan")


def test_the_choice_can_be_explained_like_every_other_answer(tmp_path):
    """`110` §2.4: "`--explain residual:Review Later` then works for free"."""
    corpus, database = _corpus(tmp_path)
    _run(corpus, database, "--residual", AREA)
    out = io.StringIO()
    code = cli.main(["--database", str(database), "--user", "jy",
                     "--explain", QUESTION, str(corpus)], out=out)
    printed = out.getvalue()
    assert code == 0, printed
    # NOT a containment test on the area's name: the refusal `--explain` prints
    # for a question nobody raised quotes the id back, so "Review Later" is in
    # the output either way and the first draft of this test was green against a
    # product that stored nothing at all.
    assert "is not a question" not in printed, printed
    assert "catch-all area" in printed, printed
    assert "enable" in printed, printed


def _answers_for(database: Path, question_id: str) -> list[tuple[str, str]]:
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        return [(row["option_id"], row["recorded_at"]) for row in conn.execute(
            "SELECT option_id, recorded_at FROM structural_answers "
            "WHERE question_id = ? ORDER BY recorded_at", (question_id,))]
    finally:
        conn.close()


def test_typing_the_same_flag_again_is_not_a_new_decision(tmp_path):
    """`84` §6: what the record says has to be true of the person.

    This writer is unlike `declare_role`, which somebody invokes when they have
    something to say: it runs on every command carrying the flag. Writing
    unconditionally would append one superseding answer per run, each of them
    saying "the person decided this area again", and `--explain` would date a
    decision made in June to this morning. A standing answer that already says
    this is left where it is.
    """
    corpus, database = _corpus(tmp_path)
    _run(corpus, database, "--residual", AREA)
    after_one = _answers_for(database, QUESTION)
    assert len(after_one) == 1, after_one

    _run(corpus, database, "--residual", AREA)
    _run(corpus, database, "--residual", AREA)
    assert _answers_for(database, QUESTION) == after_one


def test_changing_your_mind_does_write_a_second_answer(tmp_path):
    """The other half, without which the test above is satisfied by a writer
    that never writes twice at all -- including when the answer changed."""
    corpus, database = _corpus(tmp_path)
    _run(corpus, database, "--residual", AREA)
    _run(corpus, database, "--residual-library", f"disable:{AREA}")
    options = [option for option, _ in _answers_for(database, QUESTION)]
    assert options == ["enable", "disable"], options
    assert not _area_is_in_the_newest_plan(database)


def test_an_area_you_named_yourself_is_named_when_it_cannot_be_rebuilt(tmp_path):
    """`84` §1 again, at the other end of the same memory.

    `--define-residual` lets a person name an area of their own and say what it
    does with a file. The enablement is remembered; the DEFINITION is not, because
    it is not an answer to a question -- it is the area itself. So a later command
    that does not carry `--define-residual` holds a settled name with no template
    behind it, and building one would be this run inventing a treatment for a
    folder the person authored. It is named and said, not skipped.
    """
    corpus, database = _corpus(tmp_path)
    _run(corpus, database, "--define-residual", "Boat Papers=retained",
         "--residual", "Boat Papers")
    printed = _run(corpus, database)
    flat = " ".join(printed.split())
    assert "Settled on an earlier run and not applied now" in flat, printed
    assert "Boat Papers" in flat, printed
    assert "--define-residual" in flat, printed


def test_naming_your_own_area_again_brings_it_back_without_retyping_residual(
        tmp_path):
    """The half that makes the sentence above actionable rather than an apology:
    the run says to add `--define-residual`, and adding it is enough -- the
    enablement is already remembered, so `--residual` is not typed again."""
    corpus, database = _corpus(tmp_path)
    _run(corpus, database, "--define-residual", "Boat Papers=retained",
         "--residual", "Boat Papers")
    printed = _run(corpus, database, "--define-residual", "Boat Papers=retained")
    assert "Settled on an earlier run" not in printed, printed
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        newest = conn.execute(
            "SELECT plan_version_id FROM plan_versions "
            "ORDER BY created_at DESC, plan_version_id DESC LIMIT 1").fetchone()
        assert conn.execute(
            "SELECT 1 FROM tree_nodes WHERE plan_version_id = ? "
            "AND origin_node_id = ?",
            (newest[0], "residual:Boat Papers")).fetchone(), printed
    finally:
        conn.close()


def test_an_action_that_carries_a_name_is_not_remembered_and_says_so(tmp_path):
    """`84` §1: what is not kept is named, never silently dropped.

    Four of §7.4's six actions carry an argument the person supplied -- the name
    for a rename, the folder for a relocate, the area for a merge, the node for a
    replace -- and a `QuestionOption` has nowhere to put one. `residual_action`
    holds a member of a closed vocabulary; `StructuralAnswer.raw_wording` is the
    only free-text field in the record and it is REFUSED beside a chosen option
    ("an answer carrying both a chosen option and a sentence has two answers in
    it that need never agree", `records.py`). So those choices are not
    remembered, and the run says which ones were not rather than leaving the
    person to find out on the next run.
    """
    corpus, database = _corpus(tmp_path)
    printed = _run(corpus, database,
                   "--residual-library", f"rename:{AREA}=Later On")
    flat = " ".join(printed.split())
    assert "Not remembered for next time" in flat, printed
    assert AREA in printed, printed
    assert "type it again" in flat, printed
