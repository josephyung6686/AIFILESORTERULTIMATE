"""Naming a branch: the one gesture that must never guess.

`84` §6: *"a gesture that acts on something other than what the person named is
worse than one that stops and asks."* Applied three times already in this repo
to gestures that only WRITE A ROW. Here it decides which of a person's files
move, so the refusals are the point of the module and are tested before the
happy path is.
"""
from __future__ import annotations

import pytest
from tree_design.records import Node

from apply_run.branches import BranchRefused, branches_named, labels_offered


def _node(node_id, label, parent, *, accepts=True):
    return Node(
        node_id=node_id, plan_version_id="v1", node_type="proposed",
        display_label=label, parent_node_id=parent,
        root_anchor="root_documents", ordinal=0, associated_group_ids=(),
        explanation="test", node_role="ordinary",
        accepts_placement=accepts, handling_class="personal_non_sensitive",
        origin_node_id=node_id)


TREE = (
    _node("n-a", "Coursework", None),
    _node("n-a1", "PHYS1401", "n-a"),
    _node("n-a2", "Homework", "n-a1"),
    _node("n-b", "Reading Inbox", None),
)

#: Two branches under different parents wearing the same label. A real tree does
#: this the moment two courses both have a Homework folder.
AMBIGUOUS = TREE + (_node("n-c", "Applications", None),
                    _node("n-c1", "Homework", "n-c"))


def test_a_top_level_label_selects_it_and_everything_under_it():
    assert branches_named(("Coursework",), nodes=TREE) == frozenset(
        {"n-a", "n-a1", "n-a2"})


def test_a_deep_label_selects_only_its_own_subtree():
    assert branches_named(("PHYS1401",), nodes=TREE) == frozenset(
        {"n-a1", "n-a2"})


def test_several_branches_are_the_union():
    assert branches_named(("PHYS1401", "Reading Inbox"), nodes=TREE) == frozenset(
        {"n-a1", "n-a2", "n-b"})


def test_a_label_that_names_two_branches_refuses_and_prints_both_paths():
    with pytest.raises(BranchRefused) as raised:
        branches_named(("Homework",), nodes=AMBIGUOUS)
    message = str(raised.value)
    assert "Coursework/PHYS1401/Homework" in message
    assert "Applications/Homework" in message
    # And it does not pick one.
    assert "moved" not in message


def test_the_qualified_path_the_refusal_printed_is_itself_acceptable():
    """The refusal names alternatives, so the alternatives must be typeable.

    `84` §6's other standing rule -- what the screen tells a person to type has
    to be true -- applied to the sentence the first rule produces.
    """
    assert branches_named(("Coursework/PHYS1401/Homework",),
                          nodes=AMBIGUOUS) == frozenset({"n-a2"})
    assert branches_named(("Applications/Homework",),
                          nodes=AMBIGUOUS) == frozenset({"n-c1"})


def test_an_unknown_label_refuses_and_lists_what_there_is():
    with pytest.raises(BranchRefused) as raised:
        branches_named(("Courswork",), nodes=TREE)
    message = str(raised.value)
    assert "Courswork" in message
    for label in ("Coursework", "PHYS1401", "Homework", "Reading Inbox"):
        assert label in message


def test_no_branch_named_is_a_refusal_not_an_empty_selection():
    """An empty tuple must never quietly mean "all of it"."""
    with pytest.raises(BranchRefused):
        branches_named((), nodes=TREE)


def test_labels_offered_is_every_branch_by_its_full_path():
    assert labels_offered(AMBIGUOUS) == (
        "Applications", "Applications/Homework", "Coursework",
        "Coursework/PHYS1401", "Coursework/PHYS1401/Homework", "Reading Inbox")
