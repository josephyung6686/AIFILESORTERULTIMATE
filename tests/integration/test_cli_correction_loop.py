"""A person corrects the product, runs it again, and sees a different answer.

This is `84` §5's whole method applied to the one promise that matters most after
the privacy rule: **a correction a person makes has to change what they see the
next time.** `facts/learning.py` had no caller once, so every correction was
forgotten; that was fixed. This file asks whether it is fixed END TO END, from a
typed gesture to a different screen, and it asks by running the shipped command
rather than by building both sides of the seam itself. A test that constructs its
own producer and its own reader is exactly how the original defect passed.

**What is already true, and is the control below.** `--reject` reaches
`facts.learning.reject_claim`, which does both halves in one transaction: it
supersedes the standing `file_facts` row with a `rejected` one carrying the same
evidence, and it stores the §8.7 record that stops the claim being proposed
again. `facts.direct.direct_facts` asks `is_suppressed` before it writes. Commit
`8260f46` then stopped P9 handing back a membership whose fact had been retracted
and stopped P11 placing an excluded member. All of that is on the live path and
all of it holds.

**What is not.** `8260f46`'s own message names the stage it could not reach:

    "The third stage is `src/cli.py`'s `evidence_for`, which selects on `active`
    and `superseded_by` -- exactly what P6's new `rejected` row satisfies -- and
    labels it `direct`. The diff for that goes to the owner of that file."

That diff was never applied. `src/cli.py:1547`'s `evidence_for` selects
`active = 1 AND superseded_by IS NULL`, which is precisely the shape of the
retraction row P6 writes, and then hands it to `MatchingFact` with
`reliability=pv.DIRECT` hardcoded. `MatchingFact.__post_init__` checks
`reliability` against `EVIDENCE_TYPES`, from which `rejected` is deliberately
absent -- the guard `8260f46` added for this -- and a caller that reports every
row as `direct` makes that guard unable to fire. So P11 scores the placement on
the claim the person rejected and prints `exact fact match` beside it.

Measured on the three-file corpus below, without the hunk: the person rejects the
subject of one file, and runs two AND three come back with that file still filed
under the folder that subject built. `84` §5: *"a correction that changes nothing
the person can see is a correction the product did not make."*

**`src/cli.py` is the composition root and belongs to the lead**, so this file
names the defect rather than fixing it. The hunk is written out in
`scratchpad/learning/CLI-PATCH.txt`. Under that hunk every assertion below
passes, the whole suite is unchanged (identical failure set across a patched and
an unpatched twin of the same snapshot), and the corrected file moves to "Waiting
for you to say what these are" on run two and stays there on run three. When it
lands, the xfail turns into a failure and should be UNMARKED, not deleted.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

#: Three files, which is the smallest corpus that can tell a correction apart
#: from a sweep. Two of them carry the SAME subject, so a rejection aimed at one
#: has a sibling to wrongly take with it; the third is protected material, which
#: keeps the tree the shape that places the other two.
CORPUS = {
    "week 3.pdf.txt":
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Ross.\n",
    "notes.txt":
        "PHYS 1401 lecture notes, week 3.\n",
    "invoice 20261.txt":
        "Invoice INV20261\n\nAmount due 400.00 on 2026-03-01.\n",
}

#: The claim the person rejects, in the three words they have: the file, the
#: field, and the value the product printed beside it.
GESTURE = "week 3.pdf.txt:subject=PHYS1401"


def _corpus(tmp_path: Path) -> Path:
    """Under `holder/corpus`, never directly under the pytest-named directory.

    `84` §4's warning: a directory name ABOVE the corpus root once changed
    classification, and pytest names `tmp_path` after the test function -- so a
    test's own name once changed what the product decided about its own corpus.
    The database goes in `holder/`, beside the corpus and not inside it.
    """
    corpus = tmp_path / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in CORPUS.items():
        (corpus / name).write_text(body)
    return corpus


def _run(corpus: Path, *extra: str) -> str:
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(corpus.parent / "plan.sqlite"), *extra], out=out)
    return out.getvalue()


def _section_holding(printed: str, filename: str) -> str:
    """The heading of the block this file is listed under, in the words on screen.

    The report groups files under sentences a person reads, not under ids, so the
    heading IS the outcome: "Ready to file into PHYS1401" and "Waiting for you to
    say what these are" are the two different answers this whole file is about.
    """
    heading = "ABSENT"
    for line in printed.splitlines():
        text = line.strip()
        if (text.startswith("Ready to file into")
                or text.startswith("Waiting for you to say")
                or text.startswith("Ready for you to approve")
                or text.startswith("Would go into")):
            heading = text
        elif text == filename:
            return heading
    return "ABSENT"


@pytest.mark.xfail(strict=True, reason=(
    "`src/cli.py:1547` -- `evidence_for` selects `active = 1 AND superseded_by "
    "IS NULL`, which is the exact shape of the `rejected` row P6 writes when a "
    "person types `--reject`, and then passes `reliability=pv.DIRECT` for every "
    "row it read. `rejected` is deliberately absent from P11's `EVIDENCE_TYPES` "
    "and `MatchingFact` checks against it, so hardcoding `direct` makes that "
    "guard unable to fire and the retracted claim scores the placement. Named "
    "but not fixed by `8260f46`, which says the diff goes to the owner of that "
    "file. The hunk is in `scratchpad/learning/CLI-PATCH.txt`."))
def test_a_rejected_conclusion_is_gone_from_the_next_run_and_the_one_after(tmp_path):
    """Three runs, not two. A gesture that survives one run and not two is worse
    than one that never worked, because the person has already started trusting
    it by the time it forgets.
    """
    corpus = _corpus(tmp_path)

    first = _run(corpus)
    assert _section_holding(first, "week 3.pdf.txt").startswith(
        "Ready to file into PHYS1401"), first

    second = _run(corpus, "--reject", GESTURE)
    assert _section_holding(second, "week 3.pdf.txt").startswith(
        "Waiting for you to say"), second

    third = _run(corpus)
    assert _section_holding(third, "week 3.pdf.txt").startswith(
        "Waiting for you to say"), third


def test_the_other_file_that_carries_the_same_value_is_left_exactly_where_it_was(
        tmp_path):
    """§8.7's own reason for keeping the scope narrow: one transcript belonging
    in a Columbia packet "must not teach the engine that all transcripts belong
    there". `notes.txt` carries the same `subject = PHYS1401` and nobody said
    anything against it, so it must still be filed under PHYS1401 afterwards.

    NOT xfailed, and that is the point of it: it passes today *because* the
    rejection currently does nothing at all, and it must go on passing under the
    hunk. It is the twin a sweep-shaped fix fails -- a fix that dropped the
    group, or every membership in it, would satisfy the test above and break
    this one. Marking it xfail was the first thing tried here and `strict=True`
    caught it as an XPASS, which is `84` §5's "a guard that has never failed is
    not a guard" arriving from the other side.
    """
    corpus = _corpus(tmp_path)
    _run(corpus)

    after = _run(corpus, "--reject", GESTURE)

    assert _section_holding(after, "notes.txt").startswith(
        "Ready to file into PHYS1401"), after


def test_the_correction_is_stored_even_though_the_run_does_not_yet_honour_it(
        tmp_path):
    """The control, and the reason the two xfails above are about ONE stage.

    Everything up to `evidence_for` works: P6 supersedes the standing row with a
    `rejected` one and stores the §8.7 record. This test reads the database
    rather than the screen, so it passes today -- which is exactly what makes the
    defect a composition defect and not a missing part. Unmark the xfails when
    the hunk lands; do not weaken this one, it is what proves the halves exist.
    """
    import sqlite3

    corpus = _corpus(tmp_path)
    _run(corpus)
    _run(corpus, "--reject", GESTURE)

    conn = sqlite3.connect(corpus.parent / "plan.sqlite")
    conn.row_factory = sqlite3.Row
    retractions = conn.execute(
        "SELECT ff.reliability_state, ff.origin FROM file_facts ff "
        "JOIN files f ON f.file_id = ff.file_id "
        "WHERE f.filename = 'week 3.pdf.txt' AND ff.field_key = 'subject' "
        "AND ff.superseded_by IS NULL").fetchall()
    assert [(row["reliability_state"], row["origin"]) for row in retractions] == [
        ("rejected", "user_correction")], [dict(row) for row in retractions]

    # And the §8.7 record beside it, which is what stops the NEXT proposal.
    stored = conn.execute(
        "SELECT COUNT(*) FROM events WHERE polarity = 'reject'").fetchone()[0]
    assert stored == 1, stored
    conn.close()


def test_pressing_up_arrow_and_running_it_again_is_one_correction_not_two(
        tmp_path):
    """A person does not re-run this command by editing one flag off the end of
    it; they press up-arrow and press return, `--reject` and all. §8.5 counts
    decisions, and the second identical gesture must not read as a second one.

    Passes today. It is here because it is the same gesture as the xfails above
    and it would be the first thing a fix could break.
    """
    import sqlite3

    corpus = _corpus(tmp_path)
    _run(corpus)
    _run(corpus, "--reject", GESTURE)
    _run(corpus, "--reject", GESTURE)

    conn = sqlite3.connect(corpus.parent / "plan.sqlite")
    stored = conn.execute(
        "SELECT COUNT(*) FROM events WHERE polarity = 'reject'").fetchone()[0]
    conn.close()
    assert stored == 1, stored


def test_rejecting_something_the_product_never_said_is_refused_by_name(tmp_path):
    """`84` §6: a gesture that acts on something other than what the person named
    is worse than one that stops and asks. Nothing is written on the refused path
    and the refusal says the filename the person typed, never a uuid they have
    never seen.
    """
    corpus = _corpus(tmp_path)
    _run(corpus)

    printed = _run(corpus, "--reject", "week 3.pdf.txt:subject=CHEM1500")

    assert "This run was refused" in printed, printed
    assert "carries no subject of 'CHEM1500'" in printed, printed
    assert "'week 3.pdf.txt'" in printed, printed


#: §8.7's reset half, part by part, checked with the census instrument
#: `test_composition_root` already uses rather than with a grep.
#:
#: `reset_cutoff` is listed and IS reachable -- `learning_records` calls it on
#: every read, so the cutoff is honoured the moment one exists. That is the shape
#: of this gap and the reason it is worth naming: the reading side is wired and
#: waiting, and the three that would ever WRITE a cutoff, or show a person what
#: they have taught the product, are wired to nothing.
RESET_HALF = (
    ("database_agent.learning", "reset_preferences"),   # the P1 writer
    ("database_agent.learning", "reset_cutoff"),        # the cutoff every read honours
    ("review_surface.learning_view", "learning_view"),  # "inspectable"
    ("review_surface.learning_view", "collect_reset"),  # "resettable"
)


def _census() -> "frozenset[tuple[str, str]]":
    """`test_composition_root`'s own reachability instrument, by file path.

    By path and not `from tests.integration.test_composition_root import ...`:
    there is no `tests/__init__.py`, so the dotted form raises ModuleNotFoundError
    -- and under a bare `xfail` that import error counted as the expected failure.
    The first draft of the test below "xfailed" for that reason and not for its
    assertion, which is `84` §5's guard-that-cannot-fail committed while hunting
    for guards that cannot fail. `raises=AssertionError` on the marker is the
    other half of the fix: it can now only xfail for the reason it claims.
    """
    import importlib.util

    path = Path(__file__).with_name("test_composition_root.py")
    spec = importlib.util.spec_from_file_location("_census_probe", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._reachable_from_cli_main()


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "§8.7's reset half is complete, tested and unreachable from anything a "
    "person can type: `reset_preferences`, `learning_view` and `collect_reset` "
    "have no caller in `src/`, and `learning_resets` is never written on a live "
    "run -- while `reset_cutoff`, the read side, is called on every single "
    "`learning_records` query and is waiting for a cutoff that can never arrive. `facts/learning.py`'s docstring gives the reason -- "
    "'still owed to P13's wave' -- and `84` §5.4 retires it: P13 Wave A and all "
    "fourteen of Wave B have landed. Needs an owner decision on the gesture's "
    "name and route before a hunk can be written; see "
    "`scratchpad/learning/CLI-PATCH.txt` HUNK 2."))
def test_a_person_can_take_back_a_correction_as_well_as_make_one(tmp_path):
    """`--reject` is one-way. There is no gesture to undo it and none to see it.

    This is the asymmetry, not a missing nicety. §8.7's requirement is quoted
    inside `collect_reset` itself: learned preferences must be "INSPECTABLE as
    well as resettable". Today a person can tell the product it is wrong and can
    never tell it that it was right after all, and cannot see what they have
    already told it. `--help` names no such option and the report prints no such
    word after a rejection -- both measured.

    It is inside `test_composition_root`'s count of 235 unreachable mechanisms,
    which is a number rather than a name; this says which four they are and what
    a person loses. Asserted with that file's own census instrument so the two
    cannot disagree.
    """
    reachable = _census()
    unreachable = [f"{module}.{name}" for module, name in RESET_HALF
                   if (module, name) not in reachable]
    assert unreachable == [], unreachable


def test_the_reset_half_is_wired_to_nothing_and_the_table_stays_empty(tmp_path):
    """The measurement behind the xfail above, so it rests on a run and not a grep.

    Passes today and is meant to: it records the state a person is actually in.
    It goes red the moment a reset gesture lands, next to the xfail turning into
    an XPASS -- two signals for one change, which is what stops this being
    quietly re-forgotten.
    """
    import sqlite3

    corpus = _corpus(tmp_path)
    _run(corpus)
    printed = _run(corpus, "--reject", GESTURE)

    # Nothing on the screen tells them the correction can be seen or undone.
    #
    # The `Plan database:` line is dropped before scanning, and that is `84` §4's
    # warning arriving in a new place rather than fastidiousness: pytest names
    # `tmp_path` after the test function, the report prints the database's full
    # path, and the first draft of this test found the word "reset" in its OWN
    # NAME echoed back at it. A test that reads the screen has to read the part
    # of the screen the product wrote.
    report = "\n".join(line for line in printed.splitlines()
                       if not line.startswith("Plan database:"))
    for word in ("undo", "reset", "take it back", "corrections you"):
        assert word not in report.lower(), (word, report)

    conn = sqlite3.connect(corpus.parent / "plan.sqlite")
    resets = conn.execute("SELECT COUNT(*) FROM learning_resets").fetchone()[0]
    conn.close()
    assert resets == 0, resets
