"""P10 Task 17 — what P11 and P12 build against before P10 has a pipeline.

**Why these live in `src/` and not in `tests/p11/`.** P11 currently hand-builds
P10's records in `tests/p11/p10_fixtures.py` — and not merely their values: that
module DECLARES its own `FrozenTree`, `DestinationProfile`, `FreezeRecord`,
`Restrictions` and `NodeContext` classes. So P11's suite can be green against a
shape P10 no longer has, and nothing would say so. MINOR 6 settles the
ownership: P10 owns the tree, so P10 publishes the fixtures its consumers build
against, and the consumers import them.

The guarantee that makes the swap one line is the LAST test here:
`frozen_tree_fixture()` and `freeze.frozen_tree(conn, plan_version=...)` return
the same record, field for field, built by the same constructors. If the fixture
and the live read ever drift, the failure surfaces here rather than as a P11
rewrite.
"""
from __future__ import annotations

import dataclasses

import pytest

from tree_design.fixtures import (
    frozen_tree_fixture,
    realistic_tree,
    residual_library_fixture,
    template_library_fixture,
    two_version_pair,
    walking_skeleton_tree,
)
from tree_design.freeze import FrozenTree, is_legal_destination
from tree_design.records import Node
from tree_design.vocabulary import (
    IGNORED,
    PROTECTED,
    RESIDUAL,
    RESIDUAL_TEMPLATE_NAMES,
)


def test_the_walking_skeleton_is_two_nodes_with_no_template_and_no_group():
    """Resolution B8(b): the skeleton must EXERCISE §6.10's margin condition
    rather than bypass it, and a one-node tree leaves `margin_over_next` with no
    second candidate to have a margin over."""
    nodes = walking_skeleton_tree()
    assert len(nodes) == 2
    assert all(node.template_context is None for node in nodes)
    assert all(node.associated_group_ids == () for node in nodes)
    assert all(node.accepts_placement for node in nodes)


def test_every_fixture_node_is_a_real_record_and_not_a_look_alike():
    """The whole point of moving these into `src/`. Each node is built by P10's
    own constructor, so a fixture that violates an invariant cannot be built —
    which is exactly what a hand-written mirror in another part's test tree can
    do without noticing."""
    for tree in (walking_skeleton_tree(), realistic_tree()):
        assert tree, "a fixture tree with no nodes demonstrates nothing"
        assert all(isinstance(node, Node) for node in tree)


def test_no_fixture_node_carries_a_path():
    """DM11. A fixture is where a path separator would most easily slip in, and
    `Node.__post_init__` refuses one — so this asserts the fixtures actually
    exercise that rather than merely coexist with it."""
    for tree in (walking_skeleton_tree(), realistic_tree()):
        for node in tree:
            assert "/" not in node.display_label
            assert "\\" not in node.display_label


def test_the_realistic_tree_covers_the_node_types_p11_must_handle():
    """A fixture that only contained `proposed` nodes would let P11 ship without
    ever meeting a protected or ignored one, and those are the two that are NOT
    legal destinations."""
    kinds = {node.node_type for node in realistic_tree()}
    assert PROTECTED in kinds and IGNORED in kinds
    roles = {node.node_role for node in realistic_tree()}
    assert RESIDUAL in roles


def test_a_protected_node_is_present_and_is_not_a_legal_destination():
    """The standing rule, as a fixture P11 cannot avoid meeting: protected
    material is MARKED and COUNTED, never removed — so the node is IN the tree —
    and it is not somewhere P11 may place into."""
    tree = frozen_tree_fixture()
    protected = [n for n in tree.nodes if n.node_type == PROTECTED]
    assert protected, "the fixture must contain protected material to be useful"
    for node in protected:
        assert node.node_id in tree.freeze_record.node_ids
        assert not is_legal_destination(tree.freeze_record, node.node_id)


def test_an_ordinary_node_IS_a_legal_destination():
    """The discriminating twin of the test above. Without it, a freeze record
    whose `legal_destination_ids` was empty would pass — right answer, wrong
    reason."""
    tree = frozen_tree_fixture()
    ordinary = [n for n in tree.nodes
                if n.accepts_placement and n.node_type not in (PROTECTED, IGNORED)]
    assert ordinary
    assert any(is_legal_destination(tree.freeze_record, n.node_id)
               for n in ordinary)


def test_the_residual_library_fixture_names_only_published_templates():
    """§7.4's nine names are a closed set. A fixture inventing a tenth would
    teach P11 to handle a residual template that cannot exist."""
    library, choices = residual_library_fixture()
    assert set(library) <= set(RESIDUAL_TEMPLATE_NAMES)
    assert choices, "a library with no choices exercises no disposition"
    assert {c.template_name for c in choices} <= set(library)


def test_the_residual_choices_cover_all_three_dispositions():
    """All three §7.4 dispositions produce LEGAL nodes and differ in what
    happens WHEN one is chosen. A fixture covering one would hide the other
    two from P11 entirely."""
    _, choices = residual_library_fixture()
    assert len({c.disposition for c in choices}) == 3


def test_the_template_library_fixture_is_a_loadable_release():
    """Built through `load_catalogue`, so a fixture catalogue that the real
    loader would reject cannot be published."""
    catalogue = template_library_fixture()
    assert catalogue.rows_for_schema("academic")


def test_two_versions_share_lineage_without_sharing_node_ids():
    """SPEC open question 5 is open, so P10 mints `node_id` per version and
    records `origin_node_id`. A fixture pair that reused ids would quietly
    settle the question P10 deliberately left open."""
    first, second = two_version_pair()
    assert {n.plan_version_id for n in first} != {n.plan_version_id for n in second}
    assert not ({n.node_id for n in first} & {n.node_id for n in second})
    assert ({n.origin_node_id for n in first}
            & {n.origin_node_id for n in second})


def test_the_frozen_tree_fixture_is_the_p11_swap_boundary(conn):
    """**The deliverable of this task.**

    `frozen_tree_fixture()` and `freeze.frozen_tree(conn, plan_version=...)`
    must return the same record, field for field. That is what makes P11's swap
    one changed import rather than a rewrite of every test that touches a node
    or a profile — and it is asserted by comparing FIELD NAMES, so a field added
    to `FrozenTree` later fails here until the fixture carries it.
    """
    from tree_design.fixtures import store_fixture_tree

    fixture = frozen_tree_fixture()
    live = store_fixture_tree(conn)

    assert isinstance(fixture, FrozenTree) and isinstance(live, FrozenTree)
    fields = [f.name for f in dataclasses.fields(FrozenTree)]
    assert fields, "FrozenTree has no fields to compare"
    for name in fields:
        assert getattr(fixture, name) == getattr(live, name), (
            f"{name!r} differs between the published fixture and the live "
            "`frozen_tree` read; P11's swap would not be one import")
