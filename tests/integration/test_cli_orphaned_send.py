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

THE STALE COMMAND IS THE WORSE HALF. Review sets are named by position in a
chunking the person did not choose -- `(1 of 2)` and `(2 of 2)` at one screen of
25 (`104` R-93; it was `(1 of 4)` … `(4 of 4)` at the spend ceiling's eight).
Delete files anywhere and they renumber, so a name that was correct yesterday
names nothing today, and `ResidualSendRefused` propagates out of `run()` to
`main()`'s `except REFUSALS`, which throws away a plan that had already been
computed. One stale line in shell history and there is no plan at all, which
makes scripts and notes-to-self actively dangerous for a command-line product.

R-93 does not fix this and narrows it: at 25 a hold that fits on one screen is
UNNUMBERED, so it has no index to go stale. The corpus below is one file over
that, which is where the numbering still exists and can still be orphaned --
and deleting that one file makes the remainder a single unnumbered set, which
is the same defect arriving as a name that disappears rather than one that
moves.

Refusing is right -- §6's ruling is that a gesture acting on something other than
what the person named is worse than one that stops and asks, and a renumbered
`(1 of 2)` is a different set of files. Refusing by destroying the run is not,
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

#: Twenty-six photographs and two coursework files. The photographs are what a
#: person actually has a lot of and cannot classify; the two coursework files
#: exist so a tree gets built at all, because a corpus that designs no tree
#: refuses before it can surface a review set. At `104` R-93's screenful of 25
#: the photographs chunk into two sets, which is the smallest corpus that can
#: renumber -- twenty-five of them would be one unnumbered set with no index to
#: go stale.
#:
#: TWENTY-SIX AND NOT TWENTY-FOUR since `9e7152e`. The two coursework files used
#: to land in the review sets as well -- their branch stated nothing, so nothing
#: could be filed into it -- and twenty-four photographs plus those two made the
#: twenty-six this chunking wants. They are filed now, which is the whole point
#: of that commit, so the photographs have to supply the whole population on
#: their own. The count is the only thing that changed here: a review set is
#: about a file NOTHING can place, and a photograph carrying no fact is that
#: file, where a syllabus whose subject named its own branch never was.
PHOTOS = 26
#: ONE, AND IT IS THE WHOLE SECOND SET. `_delete_unrelated` takes the last
#: photographs by name and the sets are named in that order, so the deleted file
#: is the only member of `(2 of 2)` and none of the sent set's files are touched
#: -- which is the premise of the stale-name test below. At the old ceiling of
#: eight this was eight files out of four sets; it is one out of two now for the
#: same reason, and the arithmetic is asserted rather than assumed by
#: `test_a_stale_send_leaves_the_person_a_plan_and_a_way_forward`.
DELETED = 1

#: What the screen prints, and therefore what the person types.
#:
#: NAMED BY ITS REASON SINCE `104` R-115, and the `(i of n)` is unchanged. The
#: sets used to be one pile called "Not yet placed" cut into eight-file batches;
#: they are now divided by the reason the screen already prints over each group,
#: and the screenful then splits each of those. Twenty-six photographs that no
#: folder matched are one reason and two batches since R-93 raised the split from
#: eight to 25 -- which is why every assertion in this file still holds and only
#: the index moved. The control test below asserts this string IS what the screen
#: offers, so a further rename fails there first rather than as five stale
#: comparisons.
FIRST_LABEL = "No folder matched (1 of 2)"
FIRST_SET = f"{FIRST_LABEL}=Review Later"

#: And what the screen offers AFTER the deletion, when twenty-five photographs
#: are one screen and the set is unnumbered. `104` R-93's second clause on the
#: one screen where a person feels it: the name they typed yesterday is not the
#: name of anything today.
CURRENT_SET = "No folder matched=Review Later"

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
                     "--accept-groups",
                     "--residual", "Review Later", *extra], out=out)
    # The `Plan database:` line carries the full tmp_path, and pytest names
    # tmp_path after the test function -- so a test whose own name contains
    # "placed" or "review" finds its own name in the text it is asserting on.
    # `84` §4, arriving through the screen rather than through classification.
    return code, "\n".join(line for line in out.getvalue().splitlines()
                           if not line.startswith("Plan database:"))


def _delete_unrelated(corpus: Path) -> None:
    """The last photograph -- not in the set that was sent."""
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
    # AND IT MUST NOT ALSO BE CALLED UNCARRIED. Up-arrow is how people re-run, so
    # this records a new decision under this run's plan version for a set with
    # the same label, while the earlier run's row is still the most recent one
    # belonging to another version. The first version of the reader named it, and
    # the screen said both things about one set at once -- "Would go into Review
    # Later" in the file list and "which this plan does not carry" below it.
    # Caught by review, not by this test, which is why the assertion is here now.
    if NOT_CARRIED in again:
        passage = again[again.index(NOT_CARRIED):]
        assert FIRST_LABEL not in passage, passage


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
    # WHAT THE SETS ARE CALLED NOW, which since `104` R-93 is a name with no
    # index at all: the twenty-five that are left fit on one screen, so the
    # split -- and the `(1 of 2)` the person typed -- is gone. Asserted through
    # the gesture rather than through the label, because the stale label the
    # refusal quotes back contains "No folder matched" too, and a bare substring
    # would pass against a screen that only echoed the name that failed.
    assert f"--send-set '{CURRENT_SET}'" in stale, stale
    assert "(1 of 2)" in stale, (
        "the refusal does not quote back the name the person actually typed")


#: The sentence that is true only when the area really is unenabled. Named once
#: so the three tests below cannot drift into asserting three near-misses of it.
AREA_ADVICE = "`--residual` enables an area for the run it is typed in"

#: AN AREA THIS CORPUS NEITHER ENABLES NOR MINTS, which since `00` amendment 13
#: is a smaller set of areas than it used to be and is why Case A below had to
#: move. `Archive` is `REVIEW_HOME_FOR_SET`'s home for possible duplicates
#: (`cli.py`), and this corpus has no duplicates set -- twenty-six photographs
#: that no folder matched and two coursework files that are filed. So nothing
#: mints it, `--residual` is the only thing that could, and the advice is true.
#:
#: MEASURED, not reasoned: sending this set to `Archive` prints the refusal, the
#: advice and the plan, which is the three-part promise Case A exists to hold.
UNMINTED_AREA = "Archive"
SEND_TO_UNMINTED = f"{FIRST_LABEL}={UNMINTED_AREA}"


def _first_run(corpus: Path) -> None:
    """One run with the area enabled, so review sets exist to be named."""
    _run(corpus)


def test_a_mistyped_set_name_is_not_told_to_enable_an_area_it_already_has(
        tmp_path):
    """Case B. The area IS enabled, in this very command; only the set is wrong.

    The advice would tell them to add a flag that is already there, which is the
    most visible possible way for a screen to be wrong.
    """
    corpus = _corpus(tmp_path)
    _first_run(corpus)

    _, printed = _run(corpus, "--send-set", "Nonsense set=Review Later")

    assert "is not a review set this run surfaced" in printed, printed
    assert AREA_ADVICE not in printed, printed


def test_an_unenabled_area_still_gets_the_paste_able_command_and_a_plan(
        tmp_path):
    """Case A. `--residual` was NOT typed in this command, so the advice is
    true and is the one thing that explains the refusal: an area is enabled for
    the run it is named in.

    All three are asserted together on purpose. Keeping the plan and losing the
    sentence would be trading one real improvement for one real regression,
    which is exactly what the lead caught in the first version of this hunk.

    **RE-AIMED, 20 SEP, AND THE PREVIOUS AIM HAD GONE FALSE.** This case used to
    send `FIRST_SET` -- a `No folder matched` set bound for `Review Later` -- and
    `00` amendment 13 ended the world it was written for. `No folder matched`
    maps to `Review Later` in `REVIEW_HOME_FOR_SET`, the home is now minted on
    demand for a person who did not type `--residual`, and with the policy in
    force the send is HONOURED: the screen prints the plan and there is no
    refusal to advise about. The assertion did not fail because the product
    regressed. It failed because the product got better and the test still
    described the old world.

    **RE-AIMED RATHER THAN RETIRED, and that was the lead's call.** The promise
    underneath -- a refusal still hands the person a command they can paste and
    does not cost them their plan -- is `84` §6 and is still live for every area
    amendment 13 does NOT mint. `mint_review_homes_on_demand` excludes two kinds
    (`cli.py`: `not item.protected and item.set_key in REVIEW_HOME_FOR_SET`), so
    such areas exist and nothing else in this file reaches one. Retiring the case
    would have deleted the only coverage of a promise that still holds; moving it
    keeps the coverage and points it at the world as it is now.

    SABOTAGE: send `FIRST_SET` again. The send is honoured, no refusal is
    printed, and the advice assertion goes red -- which is the failure this
    re-aim is the answer to, and it is worth seeing once.
    """
    corpus = _corpus(tmp_path)
    _first_run(corpus)

    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Coursework", "--user", "jy",
                     "--database", str(corpus.parent / "plan.sqlite"),
                     "--accept-groups",
                     "--send-set", SEND_TO_UNMINTED], out=out)
    printed = "\n".join(line for line in out.getvalue().splitlines()
                        if not line.startswith("Plan database:"))

    assert code == 0, printed
    assert "Folders in this plan" in printed, printed
    assert AREA_ADVICE in printed, printed
    assert f"--residual {UNMINTED_AREA}" in printed, printed


def test_the_area_amendment_13_does_mint_needs_no_flag_and_is_honoured(
        tmp_path):
    """The other half of the re-aim above, and the reason it was needed.

    `No folder matched` IS in `REVIEW_HOME_FOR_SET`, so amendment 13 mints
    `Review Later` on demand and the send succeeds with no `--residual` in the
    command. Without this test the re-aim above would look like coverage moving
    sideways; with it, the behaviour that displaced the old assertion is pinned
    by an assertion of its own, so a regression that un-mints the home fails
    HERE rather than silently restoring the old screen.

    SABOTAGE: make `mint_review_homes_on_demand` skip its mint. The refusal and
    the advice come back and both assertions below go red.
    """
    corpus = _corpus(tmp_path)
    _first_run(corpus)

    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Coursework", "--user", "jy",
                     "--database", str(corpus.parent / "plan.sqlite"),
                     "--accept-groups",
                     "--send-set", FIRST_SET], out=out)
    printed = "\n".join(line for line in out.getvalue().splitlines()
                        if not line.startswith("Plan database:"))

    assert code == 0, printed
    assert "That answer was refused" not in printed, printed
    assert AREA_ADVICE not in printed, printed


#: The columns of `privacy_policies` that decide whether anything about a file
#: may leave the device: the operation mode, the consent the person gave, the
#: per-file `--file-held` grants and the always-local kinds a policy suspends.
#: `policy_version`, `plan_version` and `set_at` differ between two rows of one
#: run by construction and say nothing about egress, so they are left out --
#: comparing whole rows would be comparing the clock.
EGRESS_COLUMNS = ("operation_mode", "consent_grants",
                  "automatic_move_permissions", "suspended_item_kinds")


def _live_policies(corpus: Path) -> dict[str, tuple]:
    """plan version -> its egress answer, for every policy standing right now."""
    conn = sqlite3.connect(corpus.parent / "plan.sqlite")
    conn.row_factory = sqlite3.Row
    try:
        return {row["plan_version"]: tuple(row[name] for name in EGRESS_COLUMNS)
                for row in conn.execute("SELECT * FROM privacy_policies "
                                        "WHERE superseded_by IS NULL")}
    finally:
        conn.close()


def _the_set_decision(corpus: Path) -> tuple[str, str]:
    """(the version the answer was acted under, the version that printed the set).

    Both read off the product's own row rather than recomputed here: the answer
    records the plan version it was given in, and `set_id` is prefixed with the
    version whose screen named the set. A test that derived either would be
    asserting against its own arithmetic.
    """
    conn = sqlite3.connect(corpus.parent / "plan.sqlite")
    conn.row_factory = sqlite3.Row
    try:
        rows = list(conn.execute(
            "SELECT plan_version, set_id FROM residual_set_decisions"))
    finally:
        conn.close()
    assert len(rows) == 1, [dict(row) for row in rows]
    return rows[0]["plan_version"], rows[0]["set_id"].split(":")[0]


def test_a_set_answer_acts_under_a_version_this_run_put_a_policy_on(tmp_path):
    """Which plan a gesture acts under, and that the gate can be asked about it.

    MEASURED, because the call path is not the one it reads like. A `--send-set`
    is not acted on before the design: `cli.run` designs the tree, `production.py`
    puts the policy in force for every version the design minted, and only then
    does `act_on_residual_sets` ask `placement.privacy.privacy_state_for` about
    `placement_inputs(result.tree).plan_version`. The answer to "which plan" is
    written in `cli.run` beside the call that decides it -- the version the sets
    are answered against "is the one that holds the homes" -- and it is the right
    answer: the set is this run's set, the screen offering it is this run's
    screen, and `act_on_residual_sets` already refuses to carry an answer across
    versions because a later run's set may hold different files.

    WHAT WAS WRONG WAS THAT ONE VERSION OF THE RUN HAD NO POLICY. `00` amendment
    13 mints the review home on demand for a person who did not type
    `--residual`, and `mint_review_homes_on_demand` takes a fresh
    `design_authorities`, whose `run_token` is minted per call -- so the home
    lands on a plan version of its own, minted AFTER `production.py`'s loop had
    already returned. The gate was then asked about a version nothing had
    answered for and refused, which is the gate working: `PolicyRequired` says
    the operation mode decides whether anything may leave the device and P11
    assumes none. The run died and threw away a plan it had already computed.

    SO THIS PINS TWO THINGS AT ONCE, and the second is why the fix is
    bookkeeping rather than a decision about egress: every version of one run
    carries the SAME answer. The operation mode and the consent grants come from
    the person's command; a version minted later in the same command cannot mean
    a different answer to "may anything about this file leave the device", and
    if it ever did, this run would be widening what the person agreed to
    somewhere they could not see.

    SABOTAGE: drop the loop in `cli.run` that puts the policy in force for the
    versions minted after the design. The first `--send-set` typed without
    `--residual` dies `PolicyRequired` on a plan version the person was never
    shown, and `code == 0` below fails with no plan printed at all.

    SABOTAGE 2: write the later version a policy of its own choosing -- a
    different operation mode, or grants read from somewhere other than this
    command. The run survives and the last assertion fails, which is the only
    assertion here that is about egress rather than about a crash.
    """
    corpus = _corpus(tmp_path)
    _first_run(corpus)

    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Coursework", "--user", "jy",
                     "--database", str(corpus.parent / "plan.sqlite"),
                     "--accept-groups",
                     "--send-set", FIRST_SET], out=out)
    printed = "\n".join(line for line in out.getvalue().splitlines()
                        if not line.startswith("Plan database:"))

    # The gate was reached and answered, rather than taking the run down.
    assert code == 0, printed
    assert "Would go into Review Later" in printed, printed

    acted_under, printed_the_set = _the_set_decision(corpus)
    standing = _live_policies(corpus)
    assert acted_under in standing, (acted_under, sorted(standing))
    assert printed_the_set in standing, (printed_the_set, sorted(standing))
    # THE SAME ANSWER, NOT A WIDER ONE. Both versions belong to this one
    # command, so anything but equality here would be a second egress answer
    # nobody typed.
    assert standing[acted_under] == standing[printed_the_set], (
        acted_under, printed_the_set, standing)
