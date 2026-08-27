"""§6.2 — an index over P10's profiles, built only for legal destinations."""
from __future__ import annotations

from dataclasses import replace

import pytest

from placement import vocabulary as v
from placement.index import (
    FrozenTreeRequired, build_destination_index, entries_for_plan, entry_for,
    legal_node_ids, node_exists,
)
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE, tree_with

BUILD = dict(component_version="P11-test", observed_at=FIXED_CLOCK)


def test_an_ignored_node_is_never_retrievable(p11_conn):
    # §5.10's guarantee, held at the retrieval layer and not only at validation:
    # a file that looks like it belongs in a folder the user marked `ignored`
    # cannot even be offered it.
    build_destination_index(p11_conn, FROZEN_TREE, **BUILD)
    legal = legal_node_ids(p11_conn, plan_version="plan-1")
    assert "n-ignored" not in legal
    assert entry_for(p11_conn, plan_version="plan-1", node_id="n-ignored") is None
    assert {"n-course", "n-course-alt", "n-course-shared", "n-academics",
            "n-general", "n-review-later"} == legal


def test_node_exists_is_the_authority_p8_receives(p11_conn):
    # The same source answers P11's legality test and P8's
    # NODE_NOT_IN_FROZEN_TREE check. Two sources would let them disagree.
    build_destination_index(p11_conn, FROZEN_TREE, **BUILD)
    oracle = node_exists(p11_conn, plan_version="plan-1")
    assert oracle("n-course", "plan-1") is True
    assert oracle("n-ignored", "plan-1") is False
    assert oracle("n-invented", "plan-1") is False
    assert oracle("n-course", "plan-2") is False


def test_a_review_only_residual_node_is_still_a_legal_destination(p11_conn):
    # SPEC:147-150: what `review-only` changes is that no mutation follows, not
    # whether a decision may name it.
    build_destination_index(p11_conn, FROZEN_TREE, **BUILD)
    entry = entry_for(p11_conn, plan_version="plan-1", node_id="n-review-later")
    assert entry.node_role == v.RESIDUAL_ROLE
    assert entry.disposition == v.REVIEW_ONLY


def test_the_index_carries_no_path_even_where_the_node_has_one(p11_conn):
    # B3. `existing_path` is an observed fact about the corpus and is P12's input,
    # not a destination P11 may name.
    build_destination_index(p11_conn, FROZEN_TREE, **BUILD)
    entry = entry_for(p11_conn, plan_version="plan-1", node_id="n-review-later")
    assert not hasattr(entry, "existing_path")
    assert entry.ancestor_labels == ()
    assert entry.root_anchor == "root_documents"


def test_depth_and_ancestor_labels_come_from_the_parent_chain(p11_conn):
    build_destination_index(p11_conn, FROZEN_TREE, **BUILD)
    course = entry_for(p11_conn, plan_version="plan-1", node_id="n-course")
    assert course.depth == 1
    assert course.ancestor_labels == ("Academics",)
    root = entry_for(p11_conn, plan_version="plan-1", node_id="n-academics")
    assert root.depth == 0


def test_a_shallow_by_choice_branch_says_so_in_the_index(p11_conn):
    # P10 already holds the user's answer to "is this branch shallow on purpose?".
    # §6.7 is a decision about that, so P11 reads it rather than re-deriving it.
    build_destination_index(p11_conn, FROZEN_TREE, **BUILD)
    assert entry_for(p11_conn, plan_version="plan-1",
                     node_id="n-academics").refinement_disposition == "shallow-by-choice"
    assert entry_for(p11_conn, plan_version="plan-1",
                     node_id="n-course").refinement_disposition == "refined"


def test_a_node_with_no_profile_fails_closed(p11_conn):
    # Done-means 3: the profile is present for EVERY frozen node before the first
    # file is placed. A missing one is a broken freeze, not an empty entry.
    tree = tree_with(profiles=FROZEN_TREE.profiles[1:])
    with pytest.raises(FrozenTreeRequired):
        build_destination_index(p11_conn, tree, **BUILD)


def test_a_missing_shared_material_policy_fails_closed(p11_conn):
    # §6.9 requires the frozen tree to carry one; without it a multi-home file
    # has no rule and P11 would have to choose an institution.
    with pytest.raises(FrozenTreeRequired):
        build_destination_index(p11_conn, tree_with(shared_material_policy=""), **BUILD)


def test_the_index_is_provably_the_freeze_records_projection(p11_conn):
    # §4.4 of the seam contract: ONE legality authority. P10's
    # `freeze_record.legal_destination_ids` decides; P11's index projects. Two
    # sources that can disagree is the defect the contract forbids, so a tree
    # whose record and nodes disagree fails closed rather than publishing a
    # second opinion.
    record = replace(FROZEN_TREE.freeze_record,
                     legal_destination_ids=frozenset({"n-course"}))
    with pytest.raises(FrozenTreeRequired):
        build_destination_index(p11_conn, tree_with(freeze_record=record), **BUILD)


def test_a_refinement_disposition_is_required_on_a_frozen_node(p11_conn):
    # P10's `Node` allows `None` because a DRAFT node has not been approved yet.
    # `frozen_tree` guarantees it non-`None`, and the index declares the field a
    # `str` on the strength of that guarantee -- so it verifies the guarantee
    # rather than storing a null under a non-null type.
    unapproved = replace(FROZEN_TREE.nodes[0], refinement_disposition=None,
                         refinement_reason=None)
    tree = tree_with(nodes=(unapproved,) + FROZEN_TREE.nodes[1:])
    with pytest.raises(FrozenTreeRequired):
        build_destination_index(p11_conn, tree, **BUILD)


def test_nothing_is_indexed_when_any_node_fails(p11_conn):
    # A partial index is worse than none: the nodes that made it in are
    # retrievable and the rest are silently unreachable, which reads to a user as
    # "the agent never considered that folder".
    tree = tree_with(profiles=FROZEN_TREE.profiles[1:])
    with pytest.raises(FrozenTreeRequired):
        build_destination_index(p11_conn, tree, **BUILD)
    assert legal_node_ids(p11_conn, plan_version="plan-1") == frozenset()
    assert p11_conn.execute(
        "SELECT COUNT(*) AS n FROM events").fetchone()["n"] == 0


def test_an_entry_carries_the_lineage_task_17_matches_on(p11_conn):
    # P10 mints a new `node_id` per plan version (its OQ5) and records lineage in
    # `origin_node_id`. Matching a decision across versions on `node_id` would
    # mark EVERY decision for renewed review after any tree edit, including a
    # pure rename — which §8.8 forbids. The lineage must reach the index.
    build_destination_index(p11_conn, FROZEN_TREE, **BUILD)
    entry = entry_for(p11_conn, plan_version="plan-1", node_id="n-course")
    assert entry.origin_node_id == "n-course"


def test_lineage_survives_a_new_plan_version_that_mints_new_node_ids(p11_conn):
    # The cross-version match is on `origin_node_id`, never on `node_id`. This is
    # the shape Task 17 diffs: same origin, new id, new version.
    build_destination_index(p11_conn, FROZEN_TREE, **BUILD)
    renamed = tuple(
        replace(node, node_id=f"{node.node_id}-v2", plan_version_id="plan-2",
                parent_node_id=(None if node.parent_node_id is None
                                else f"{node.parent_node_id}-v2"))
        for node in FROZEN_TREE.nodes
    )
    record = replace(
        FROZEN_TREE.freeze_record, plan_version_id="plan-2",
        node_ids=tuple(node.node_id for node in renamed),
        legal_destination_ids=frozenset(
            node.node_id for node in renamed if node.accepts_placement))
    from p11.p10_fixtures import _profile
    build_destination_index(
        p11_conn,
        tree_with(plan_version_id="plan-2", freeze_record=record, nodes=renamed,
                  profiles=tuple(_profile(node) for node in renamed)),
        **BUILD)
    v2 = entry_for(p11_conn, plan_version="plan-2", node_id="n-course-v2")
    assert v2.node_id == "n-course-v2"
    assert v2.origin_node_id == "n-course"
    assert {e.origin_node_id for e in entries_for_plan(p11_conn, plan_version="plan-2")} == {
        e.origin_node_id for e in entries_for_plan(p11_conn, plan_version="plan-1")}


def test_building_an_entry_appends_its_event(p11_conn):
    build_destination_index(p11_conn, FROZEN_TREE, **BUILD)
    rows = p11_conn.execute(
        "SELECT explanation FROM events WHERE event_type = ?",
        (v.INDEX_ENTRY_BUILT,)).fetchall()
    assert len(rows) == len(legal_node_ids(p11_conn, plan_version="plan-1"))
    assert "n-course" in " ".join(r["explanation"] for r in rows)
