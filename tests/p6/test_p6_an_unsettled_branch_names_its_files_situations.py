# tests/p6/test_p6_an_unsettled_branch_names_its_files_situations.py
"""`106` Phase 2: an unsettled branch stops going flat.

**THE DEFECT, TRACED IN `104` §18.100.** `_signals_for_branch` answers the
template router one signal per BRANCH. A branch whose situation the person has
not settled returned `frozenset()` -- no signal at all -- and an empty signal set
selects no applicability row, which is a C3 conflict, which is no recipe, which
is A FLAT ROOT. So a branch the judge had plenty to say about got no folder
levels for want of a word from the person.

**WHAT CHANGED UNDERNEATH IT.** Until 16 September the judge's answer lived only
in memory (`104` §18.95), so there was nothing an unsettled branch could be asked
about. It is now a fact on every file it named -- 222 of the owner's 371 -- and
`00` amendment 11 rules that the sort reads it. An unsettled branch is therefore
no longer silent: its FILES were judged even though its label was not settled.

**THIS DOES NOT SETTLE THE BRANCH**, and that is the line the tests below hold.
The person's word still decides what the branch IS; `candidate_situations` is
still what they choose from; `104` §17.9's ordering stands -- the model's answer
is a refinement of the person's and never a replacement. All this changes is that
the router stops being told NOTHING when the run in fact knows something.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from branch_situation import Branch  # noqa: E402
from cli import signals_for_branch  # noqa: E402


def _branch(situation, file_ids=("f1", "f2")):
    return Branch(label="Education", life="Education", schemas=("academic",),
                  situations=(), situation=situation, is_default=False,
                  anchor_file_ids=(), file_ids=file_ids)


def test_a_settled_branch_names_its_own_situation_and_nothing_else():
    """Unchanged behaviour, pinned so the fix cannot widen it.

    SABOTAGE: read the files' situations even when the branch is settled. The
    person's settled word would be diluted by whatever the judge said about
    individual files, which is `104` §17.9's ordering inverted.
    """
    got = signals_for_branch(_branch("academic.coursework"),
                             situations_of=lambda ids: {"academic.records"},
                             run_signal="recognition:academic.records")

    assert got == frozenset({"recognition:academic.coursework"})


def test_an_unsettled_branch_names_the_situations_its_files_were_judged_to_be():
    """The fix.

    SABOTAGE: return `frozenset()` for the unsettled case, which is what it did.
    The branch goes back to selecting no applicability row, and a branch with no
    recipe has no levels -- the flat root of `104` §18.100.
    """
    got = signals_for_branch(
        _branch(None),
        situations_of=lambda ids: {"academic.coursework", "academic.records"},
        run_signal="recognition:academic.records")

    assert got == frozenset({"recognition:academic.coursework",
                             "recognition:academic.records"})


def test_an_unsettled_branch_whose_files_were_never_judged_is_still_silent():
    """Silence is the honest answer when the run really does know nothing.

    SABOTAGE: fall back to the run's typed situation here. That is the
    typed-default leak `104` §18.100 records run 14 dying of -- every branch
    wearing the word the person typed at the command line, whatever its files
    are. `00` amendment 9 forbids exactly that.
    """
    got = signals_for_branch(_branch(None),
                             situations_of=lambda ids: set(),
                             run_signal="recognition:academic.records")

    assert got == frozenset()


def test_a_branchless_group_still_gets_the_runs_own_signal():
    """`None` for the branch is not the same as an unsettled branch.

    A group accepted outside the partition is the typed situation's, as it always
    was. SABOTAGE: collapse the two `None` cases. A group with no branch goes
    silent and loses the one signal it legitimately has.
    """
    got = signals_for_branch(None,
                             situations_of=lambda ids: {"academic.coursework"},
                             run_signal="recognition:academic.records")

    assert got == frozenset({"recognition:academic.records"})


def test_the_files_asked_about_are_the_branchs_own():
    """The situations read are THIS branch's files', not the corpus's.

    SABOTAGE: pass the whole roster. Every unsettled branch would then name every
    situation in the run and select every recipe, which is worse than selecting
    none -- a branch would get levels belonging to material it does not hold.
    """
    seen = []

    def situations_of(ids):
        seen.append(tuple(ids))
        return {"academic.coursework"}

    signals_for_branch(_branch(None, file_ids=("f7", "f8", "f9")),
                       situations_of=situations_of,
                       run_signal="recognition:academic.records")

    assert seen == [("f7", "f8", "f9")]
