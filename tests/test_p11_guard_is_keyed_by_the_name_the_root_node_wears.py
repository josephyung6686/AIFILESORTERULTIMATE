# tests/test_p11_guard_is_keyed_by_the_name_the_root_node_wears.py
"""A guard that silently stops matching is worse than no guard.

**THE REGRESSION, AND THE LEAD CAUSED IT ON 18 Sep (commit `9b85210f`).**
`the_situation_each_branch_carries` is handed to P11 so it can leave alone the
folders of a branch whose situation is settled. Its own comment says it is keyed
*"by the label their root node wears, which is the name `_grouped_by_branch` put
on the accepted group"* -- and P11 matches it against the root node's
`display_label` (`placement/pipeline.py:1790`).

`_grouped_by_branch` now names that draft from `branch.folder_name`, because the
owner ruled that a folder must be spelled the way a person would spell it. The map
was still keyed by `branch.label`. The two are equal only when a branch has no
authored display name -- which is true of the DEFAULT branch and false of every
branch site G opens. So P11's guard went quietly inert for exactly the branches
the model discovered, and the whole suite stayed green, because the tests that
exercise the guard use the typed-`--label` default branch.

**Caught by an analyst reading the code, not by a test.** That is what this file
is for.

**THE INVARIANT:** the key of `the_situation_each_branch_carries` is whatever
`_grouped_by_branch` names the branch's draft. One source of truth, asserted here
so the two cannot drift apart again.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from branch_situation import Branch  # noqa: E402
from cli import the_situation_each_branch_carries  # noqa: E402


def _branch(label, *, display_name="", situation="academic.coursework"):
    return Branch(label=label, schema="academic", display_name=display_name,
                  situation=situation, is_default=False,
                  anchor_file_ids=(), file_ids=("f1",))


def test_a_branch_with_an_authored_name_is_keyed_by_that_name():
    """The defect, stated as an assertion.

    SABOTAGE: key by `branch.label`. Red here, and P11 stops recognising every
    branch site G opened -- while every existing test stays green.
    """
    got = the_situation_each_branch_carries(
        (_branch("career", display_name="Career and recruiting"),))

    assert got == {"Career and recruiting": "academic.coursework"}, (
        "P11 matches the root node's display_label, and that is what "
        "`_grouped_by_branch` writes from `folder_name`")


def test_a_branch_with_no_authored_name_is_unchanged():
    """The default branch, and every caller that passes no name table.

    SABOTAGE: always use `display_name`. It is empty here, so the key becomes
    `""` and the guard matches nothing at all.
    """
    got = the_situation_each_branch_carries((_branch("Coursework"),))

    assert got == {"Coursework": "academic.coursework"}


def test_an_unsettled_branch_names_nothing():
    """Unchanged behaviour, pinned. A branch whose situation the person has not
    settled tells P11 nothing, and P11 leaves its folders alone.

    SABOTAGE: include `None`. P11 would read a settled situation of `None` as an
    answer rather than as silence.
    """
    got = the_situation_each_branch_carries(
        (_branch("career", display_name="Career and recruiting", situation=None),
         _branch("Coursework"),))

    assert got == {"Coursework": "academic.coursework"}


def test_the_key_is_exactly_what_the_draft_is_named():
    """The invariant itself, asserted against `Branch.folder_name` rather than
    against a string spelled here -- so re-authoring a name cannot split them.

    SABOTAGE: spell the expected key literally in this test. It would then pass
    while the product and the guard disagreed.
    """
    branches = (_branch("career", display_name="Career and recruiting"),
                _branch("Coursework"),
                _branch("research", display_name="Research"))

    got = the_situation_each_branch_carries(branches)

    assert set(got) == {b.folder_name for b in branches}
