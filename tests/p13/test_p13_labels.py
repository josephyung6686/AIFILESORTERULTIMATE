"""B3: a node and its ancestor labels. Never a path, never a separator.

P12 alone composes paths. This module's chain is a TUPLE of labels and never a
string, because a joined string is a path in every way that matters: it acquires
a separator, it gets logged, and the next reader treats it as one.
"""
from __future__ import annotations

import pytest

from tree_design.records import Node

from review_surface.labels import (
    AncestorCycle,
    LabelIsAPath,
    NodeNotInVersion,
    label_chain,
    refuse_path_separator,
)


def _node(node_id, label, parent=None, *, version="plan-1") -> Node:
    return Node(
        node_id=node_id, plan_version_id=version, node_type="proposed",
        display_label=label, parent_node_id=parent, root_anchor="root",
        ordinal=0, associated_group_ids=(), explanation="fixture",
        node_role="ordinary", accepts_placement=True,
        handling_class="public_low", origin_node_id=node_id,
        template_context=None, dimension_role=None, dimension=None,
        expected_values=(), existing_path=None, disposition=None,
        refinement_disposition=None, refinement_reason=None,
        protected_movement_permitted=False)


ACADEMICS = _node("n-1", "Academics")
COLUMBIA = _node("n-2", "Columbia", "n-1")
SPRING = _node("n-3", "2026-Spring", "n-2")
TREE = (ACADEMICS, COLUMBIA, SPRING)


def test_a_node_renders_as_its_ancestor_label_chain_and_never_as_a_path():
    """`74` §6 A2's named test. B3, in one assertion per half.

    The chain is root-first, it is a tuple, and no element carries a separator.
    A tuple cannot be mistaken for a path by anything downstream, which is the
    whole reason the return type is not a string.
    """
    chain = label_chain(TREE, "n-3")
    assert chain == ("Academics", "Columbia", "2026-Spring")
    assert isinstance(chain, tuple)
    for label in chain:
        assert "/" not in label and "\\" not in label, (
            "B3: this is a display label, not a path fragment")


def test_a_chain_carrying_a_path_separator_is_refused():
    """`74` §6 A2's negative twin, against a deliberately permissive walker.

    Note what this twin does NOT do. P10's own `Node` already refuses a
    `display_label` holding a separator (`tree_design/records.py`, the same
    resolution B3), so the poisoned tree cannot be built at all -- the sabotage
    has to be a WALKER, not a node. That is the honest shape anyway: P13's
    exposure is a chain assembled by something other than a live `Node`, which
    is every caller that hands `LocationElement` a chain of its own.

    The sabotage walks the parents and returns the labels unexamined. It
    produces a chain whose second element IS a path fragment, and the real guard
    rejects exactly that chain. Asserting only that clean chains pass would hold
    just as well if the guard's separator list were empty.
    """
    def _permissive(labels):
        """The sabotage: assemble a chain, check nothing."""
        return tuple(labels)

    sabotaged = _permissive(["Academics", "Columbia/2026-Spring"])
    assert sabotaged == ("Academics", "Columbia/2026-Spring")
    with pytest.raises(LabelIsAPath):
        refuse_path_separator(sabotaged)
    assert refuse_path_separator(("Academics", "Columbia")) == (
        "Academics", "Columbia")


def test_a_backslash_is_refused_for_the_same_reason_as_a_slash():
    with pytest.raises(LabelIsAPath):
        refuse_path_separator(("Academics", "Columbia\\Spring"))


def test_the_refusal_names_the_node_and_never_repeats_the_label():
    """A refusal that prints the offending label has printed a path fragment
    into whatever reads the message. It names the node instead."""
    with pytest.raises(LabelIsAPath) as caught:
        refuse_path_separator(("Columbia/Spring",), node_id="n-2")
    assert "n-2" in str(caught.value)
    assert "Columbia/Spring" not in str(caught.value)


def test_the_chain_walker_applies_the_guard_to_every_ancestor():
    """The guard is not decoration on the return value: it runs per node as the
    chain is walked, so a poisoned ancestor is refused even when the leaf is
    clean. Proved by monkeypatching P10's own validation away -- which is the
    only way this state is reachable, and it IS reachable through any node
    record P13 did not read out of `tree_nodes` itself."""
    import dataclasses

    poisoned = dataclasses.replace(COLUMBIA)
    object.__setattr__(poisoned, "display_label", "Columbia/2026-Spring")
    with pytest.raises(LabelIsAPath):
        label_chain((ACADEMICS, poisoned, SPRING), "n-3")


def test_a_root_node_is_a_chain_of_one():
    assert label_chain(TREE, "n-1") == ("Academics",)


def test_a_node_absent_from_the_version_raises_rather_than_returning_empty():
    """An empty chain would read as "at the root", which is a lie about a node
    the version does not contain."""
    with pytest.raises(NodeNotInVersion):
        label_chain(TREE, "n-missing")


def test_a_dangling_parent_raises_rather_than_truncating():
    orphan = _node("n-9", "Orphan", "n-gone")
    with pytest.raises(NodeNotInVersion):
        label_chain((*TREE, orphan), "n-9")


def test_a_cycle_raises_instead_of_looping_forever():
    a = _node("c-1", "A", "c-2")
    b = _node("c-2", "B", "c-1")
    with pytest.raises(AncestorCycle):
        label_chain((a, b), "c-1")


def test_the_chain_reads_from_the_version_it_was_asked_for(p13_conn):
    """§8.8 mints node ids per version, so the version is not optional: the same
    label sits under a different id per draft."""
    from tree_design.records import PlanVersion
    from tree_design.store import write_node, write_plan_version

    from review_surface.labels import label_chain_for_version

    write_plan_version(p13_conn, PlanVersion(
        plan_version_id="plan-1", predecessor_id=None, state="draft",
        created_at="2026-08-29T00:00:00Z", cross_folder_moves=False,
        selection_id="sel-1"))
    for node in TREE:
        write_node(p13_conn, node)
    assert label_chain_for_version(
        p13_conn, plan_version="plan-1", node_id="n-3") == (
            "Academics", "Columbia", "2026-Spring")


def test_there_is_no_function_here_that_returns_a_joined_string():
    """B3, checked by introspection rather than by reading. Every public callable
    in `labels` returns a tuple or raises; a `str` return would be a path."""
    import review_surface.labels as module

    for name in dir(module):
        if name.startswith("_"):
            continue
        value = getattr(module, name)
        if callable(value) and getattr(value, "__module__", None) == module.__name__:
            annotation = getattr(value, "__annotations__", {}).get("return")
            assert annotation != "str", (
                f"{name} is annotated to return a string; B3 gives P13 label "
                "chains and gives P12 the paths")
