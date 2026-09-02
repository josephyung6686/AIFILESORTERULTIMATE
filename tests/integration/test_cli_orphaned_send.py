"""What happens to a `--send-set` answer the next time the person runs the command.

Found by an outsider using the product, and every step they took was the
product's own instruction: the screen printed `--send-set "Not yet placed
(1 of 7)=Review Later"`, so they typed it, and it worked. Then they deleted
twenty unrelated photos, re-ran, and their decision was gone with nothing said.

TWO DIFFERENT THINGS ARE HAPPENING AND ONLY ONE OF THEM IS A DEFECT. Measured
before anything here was written:

1. The answer is not carried to the next run **whether or not anything was
   deleted**. That is a live standing decision, not an oversight, and
   `act_on_residual_sets` states it with its reason: a set answer belongs to the
   plan version it was given in, because a later run's set may hold different
   files and applying it unseen "would be this product filing material against a
   screen nobody read." Every run mints a new plan version, so
   `require_set_decision`, keyed on `(plan_version, set_id)`, cannot match. **A
   test asserting the answer survives would be asserting against that decision,
   and there is none here.**

2. What IS wrong is that nothing says so, and that deleting unrelated files turns
   yesterday's command into a run-killer. The row stays in
   `residual_set_decisions` forever and, until `prior_set_decisions`, nothing
   ever read one again -- so a person sees a plan with no trace of the answer and
   no sentence about it. `84` §6: a decision that no longer applies is named out
   loud, never silently omitted.

THE STALE COMMAND IS THE WORSE HALF. Review sets are named by position in an
arbitrary chunking -- `(1 of 4)` … `(4 of 4)` at a ceiling of eight. Delete files
anywhere and they renumber, so a name that was correct yesterday names nothing
today, and `ResidualSendRefused` propagates out of `run()` to `main()`'s
`except REFUSALS`, which throws away a plan that had already been computed. One
stale line in shell history and there is no plan at all, which makes scripts and
notes-to-self actively dangerous for a command-line product.

Refusing is right -- §6's ruling is that a gesture acting on something other than
what the person named is worse than one that stops and asks, and a renumbered
`(1 of 4)` is a different set of files. Refusing by destroying the run is not,
especially when the refusal already knows and prints the names it DID surface.

**`src/cli.py` belongs to the lead**, so the two xfails below name the defects
rather than fixing them; the hunks are in `scratchpad/learning/CLI-PATCH.txt`.
The reader they need, `placement.residual.prior_set_decisions`, is landed and
tested in `tests/p11/test_p11_orphaned_set_decision.py`.
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

#: Twenty-four photographs and two coursework files. The photographs are what a
#: person actually has a lot of and cannot classify; the two coursework files
#: exist so a tree gets built at all, because a corpus that designs no tree
#: refuses before it can surface a review set. At the deployment ceiling of
#: eight this chunks into four sets, which is the smallest corpus that can
#: renumber.
PHOTOS = 24
DELETED = 8

#: What the screen prints, and therefore what the person types.
FIRST_LABEL = "Not yet placed (1 of 4)"
FIRST_SET = f"{FIRST_LABEL}=Review Later"

#: The words the missing sentence has to carry. Asserted as a phrase rather than
#: as a whole line because the exact wording is the lead's to settle in
#: `src/cli.py`; what cannot vary is that the run SAYS the earlier answer is not
#: being applied. Matching only the set label would prove nothing -- every run
#: prints every set label anyway, which is how the first draft of this test
#: XPASSed against a product that says nothing at all.
NOT_CARRIED = "does not carry"


def _corpus(tmp_path: Path) -> Path:
    """Under `holder/corpus`, never directly under the pytest-named directory --
    `84` §4's warning about a directory name above the corpus root."""
    corpus = tmp_path / "holder" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "week 3.pdf.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Ross.\n")
    (corpus / "notes.txt").write_text("PHYS 1401 lecture notes, week 3.\n")
    for index in range(PHOTOS):
        (corpus / f"photo {index:03d}.txt").write_text(
            f"A holiday snapshot, number {index}.\n")
    return corpus


def _run(corpus: Path, *extra: str) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Coursework", "--user", "jy",
                     "--database", str(corpus.parent / "plan.sqlite"),
                     "--residual", "Review Later", *extra], out=out)
    # The `Plan database:` line carries the full tmp_path, and pytest names
    # tmp_path after the test function -- so a test whose own name contains
    # "placed" or "review" finds its own name in the text it is asserting on.
    # `84` §4, arriving through the screen rather than through classification.
    return code, "\n".join(line for line in out.getvalue().splitlines()
                           if not line.startswith("Plan database:"))


def _delete_unrelated(corpus: Path) -> None:
    """The last eight photographs -- none of them in the set that was sent."""
    for index in range(PHOTOS - DELETED, PHOTOS):
        (corpus / f"photo {index:03d}.txt").unlink()


def _decisions_stored(corpus: Path) -> int:
    conn = sqlite3.connect(corpus.parent / "plan.sqlite")
    try:
        return conn.execute(
            "SELECT COUNT(*) FROM residual_set_decisions").fetchone()[0]
    finally:
        conn.close()


def test_the_screen_prints_a_send_command_and_typing_it_works(tmp_path):
    """The control for everything below: the gesture is real and it does
    something. It is also the step the person took, quoted from the screen.
    """
    corpus = _corpus(tmp_path)

    _, first = _run(corpus)
    # Quote style is the reporter's; the instruction is what matters.
    assert "--send-set" in first, first
    assert FIRST_SET in first, first

    _, second = _run(corpus, "--send-set", FIRST_SET)
    assert "Would go into Review Later" in second, second


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "`src/cli.py` -- nothing prints the §7.6 answers an earlier run recorded, so "
    "a decision that is no longer honoured vanishes with nothing said. The scope "
    "is deliberate (`act_on_residual_sets`: a set answer belongs to its plan "
    "version) and is not what this asks to change; the silence is. `84` §6 -- "
    "never silently omitted. The reader is landed as "
    "`placement.residual.prior_set_decisions`; the printing hunk is in "
    "`scratchpad/learning/CLI-PATCH.txt` HUNK 3."))
def test_a_decision_the_next_run_cannot_honour_is_named_rather_than_dropped(
        tmp_path):
    """Nothing is deleted here, on purpose.

    The answer is not carried forward for a reason that stands, so this does not
    ask for it back. It asks for the ONE sentence that turns a vanished block
    into a decision the person can see was not applied.
    """
    corpus = _corpus(tmp_path)
    _run(corpus)
    _run(corpus, "--send-set", FIRST_SET)

    _, later = _run(corpus)

    # The label alone proves nothing -- this run surfaces a set by that name
    # too, in the files section further up. What must be there is the product
    # SAYING the earlier answer is not being applied, and naming it; so the
    # search is the passage that begins at that statement, not the whole screen
    # and not one line of it (the statement heads a block and the labels sit
    # under it).
    assert NOT_CARRIED in later, later
    passage = later[later.index(NOT_CARRIED):]
    passage = passage[:passage.index("Nothing was moved.")]
    assert FIRST_LABEL in passage, passage


def test_the_answer_is_still_in_the_database_that_nothing_reads(tmp_path):
    """The written-never-read control, and the reason the xfail above is about a
    missing sentence rather than a missing record.

    Passes today. The person's decision is durable and intact; it simply stopped
    having any effect and stopped being mentioned. Reading the table rather than
    the screen is what separates "the product forgot" from "the product went
    quiet", and it is the second of those.
    """
    corpus = _corpus(tmp_path)
    _run(corpus)
    _run(corpus, "--send-set", FIRST_SET)
    assert _decisions_stored(corpus) == 1

    _, later = _run(corpus)

    assert "Would go into Review Later" not in later, later
    assert _decisions_stored(corpus) == 1


def test_yesterdays_command_still_works_when_nothing_on_the_disk_changed(
        tmp_path):
    """The control that proves the deletion is what breaks it.

    Same command, twice, with an untouched disk: the set names are the same, so
    the second one applies exactly as the first did. Nothing about re-typing a
    `--send-set` is wrong on its own.
    """
    corpus = _corpus(tmp_path)
    _run(corpus)
    _run(corpus, "--send-set", FIRST_SET)

    code, again = _run(corpus, "--send-set", FIRST_SET)

    assert code == 0, again
    assert "Would go into Review Later" in again, again


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "`src/cli.py` -- `ResidualSendRefused` propagates out of `run()` into "
    "`main()`'s `except REFUSALS`, which discards a plan that had already been "
    "computed, so one stale line in shell history leaves the person with no plan "
    "at all. Refusing is right; refusing by destroying the run is not, and the "
    "refusal already names the sets it DID surface. Review sets are named by "
    "position in a chunking, so deleting files ANYWHERE renumbers them and a "
    "name that was correct yesterday names nothing today. Hunk in "
    "`scratchpad/learning/CLI-PATCH.txt` HUNK 4; the naming question itself is "
    "HUNK 5 and is the owner's."))
def test_a_stale_send_leaves_the_person_a_plan_and_a_way_forward(tmp_path):
    """Delete files that are in no sent set, re-type yesterday's exact command.

    The answer this asks for is not "apply it anyway" -- the renumbered set holds
    different files and applying it would be the thing `84` §6 forbids. It is:
    say the name is stale, say what the sets are called now, and still print the
    plan that was already computed.
    """
    corpus = _corpus(tmp_path)
    _run(corpus)
    _run(corpus, "--send-set", FIRST_SET)
    _delete_unrelated(corpus)

    code, stale = _run(corpus, "--send-set", FIRST_SET)

    assert code == 0, stale
    assert "No plan was made" not in stale, stale
    # The plan itself, and the refusal beside it rather than instead of it.
    assert "Folders in this plan" in stale, stale
    assert "Not yet placed (1 of 3)" in stale, stale


def test_today_that_stale_command_destroys_the_whole_run(tmp_path):
    """The measurement behind the xfail above, recorded as it is rather than as
    it should be, so the two cannot drift apart.

    Passes today and is meant to. It goes red the moment the hunk lands, next to
    the xfail turning into an XPASS -- two signals for one change.
    """
    corpus = _corpus(tmp_path)
    _run(corpus)
    _run(corpus, "--send-set", FIRST_SET)
    _delete_unrelated(corpus)

    code, stale = _run(corpus, "--send-set", FIRST_SET)

    assert code != 0, stale
    assert "No plan was made" in stale, stale
    assert "is not a review set this run surfaced" in stale, stale
    # It already knows enough to help: the current names are in the refusal.
    assert "Not yet placed (1 of 3)" in stale, stale
    # And there is no plan anywhere on the screen.
    assert "Folders in this plan" not in stale, stale
