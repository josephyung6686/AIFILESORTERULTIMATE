# tests/p6/test_p6_a_kinds_question_reaches_an_anchored_file.py
"""`108` §4's residual regression: whose map decides which kind a file is asked as.

**THE DEFECT, DECLARED IN `e9b7c550` AND NOT CLOSED THERE.**
`cli._each_kinds_question_under` picks a kind's files with
`situation_cell[0].named.get(file_id) == kind` -- **site G's map, and only site
G's**. The judge is silent about every file a deterministic anchor already
settled, so such a file matches no kind, is in no kind's question, and is left
with no situation and no way to acquire one. Before `00` amendment 16 folded
`academic` and `research` into one Education life it sat in a one-kind branch and
was asked there.

**WHY THE BRANCH CAN ANSWER.** `partition_by_branch` computes the reach's per-file
kind for every file it places, anchors included, and `Branch.kind_of` now carries
it (`be8c71c7`). The judge's map is a SUBSET of that; the gap between them is
exactly the regression.

**THE JUDGE STILL WINS WHERE IT SPOKE**, which is what keeps this change from
being a re-decision. Site G runs after the deterministic pass and `104` §17.9
orders them: a later answer refines an earlier one. So the reach is consulted only
where the judge said nothing, every file that is asked today is asked exactly as
it is today, and the only difference is files that were asked nothing at all.

Unit-level for `signals_for_branch`'s reason, and in its module's shape: the rule
is about ONE branch and three inputs, and a corpus that produces a two-kind life
branch from the deterministic pass alone is a fixture nobody has built yet.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from branch_situation import Branch  # noqa: E402
from cli import files_of_kind_still_open  # noqa: E402

#: A two-kind Education life branch: `s` reached academic through its anchor,
#: `packet` through the judge. The shape `00` amendment 16 creates and the shape
#: the residual loses.
EDUCATION = Branch(
    label="Education", life="Education",
    schemas=("academic", "college_applications"), situations=(),
    situation=None, is_default=False, anchor_file_ids=("s",),
    file_ids=("s", "packet"),
    kinds_by_file=(("s", "academic"), ("packet", "college_applications")))

#: Site G named the packet and said nothing about the anchored file.
JUDGED = {"packet": "college_applications"}


def _judged(file_id):
    return JUDGED.get(file_id)


def _open(_file_id):
    """Nothing has answered for either file."""
    return None


def test_a_file_the_judge_left_silent_is_asked_as_the_kind_its_anchor_settled():
    """THE REGRESSION, as one assertion.

    SABOTAGE: read the kind from `judged_kind_of` alone, which is today's code.
    `s` is in no kind's question and the file the anchor settled is asked nothing.
    """
    assert files_of_kind_still_open(
        EDUCATION, "academic", judged_kind_of=_judged,
        situation_under=_open) == ("s",)


def test_the_kind_the_judge_named_is_unchanged():
    """The half that must not move: a judged file is asked exactly as before."""
    assert files_of_kind_still_open(
        EDUCATION, "college_applications", judged_kind_of=_judged,
        situation_under=_open) == ("packet",)


def test_the_judges_word_outranks_the_reach_where_it_spoke():
    """`104` §17.9's ordering, at this seam.

    The reach put `packet` under `college_applications`; site G, which runs after
    the deterministic pass and has read the file, says it is academic. The later
    answer refines the earlier one, so the packet is asked academic's question.

    SABOTAGE: prefer `branch.kind_of`. The judge's reading is silently discarded
    wherever the reach already had an opinion, which is every file it placed.
    """
    judged = {"packet": "academic"}

    assert files_of_kind_still_open(
        EDUCATION, "academic", judged_kind_of=judged.get,
        situation_under=_open) == ("s", "packet")


def test_a_file_whose_situation_is_already_answered_is_not_asked_again():
    """The other half of today's predicate, kept.

    SABOTAGE: drop the `situation_under` check. The person is asked again about a
    file they have already answered for, which `00`:57 calls a question nobody
    should see twice.
    """
    assert files_of_kind_still_open(
        EDUCATION, "academic", judged_kind_of=_judged,
        situation_under=lambda file_id: ("academic.coursework"
                                         if file_id == "s" else None)) == ()
