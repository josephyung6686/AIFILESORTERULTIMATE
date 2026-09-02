"""Freezing: the proposal becomes an approved destination tree.

`00`:51 -- *"the user edits and freezes those proposals into an approved
destination tree"*; `00`:102 -- *"When the user is satisfied, they freeze the
tree."* What is durable afterwards is `00`:156-170's plan, one per file, holding
the complete expected precondition. That is why applying does not re-run the
pipeline: the plan is the record of what the person approved.
"""
from __future__ import annotations

import dataclasses
import json

from mutation.plan import current_plan

from apply_run.freeze import (
    ALREADY_AT_DESTINATION, AWAITING_APPROVAL, REFUSED_AT_CONSTRUCTION,
    freeze, frozen_plans,
)

from conftest import COLLISION_POLICY, CONSTRAINTS, LEGAL, NODES, PROTECTED_CLASSES


def _freeze(world, decisions, *, ids, clock, volume=lambda path: "vol-main"):
    return freeze(
        world.conn, decisions, nodes=NODES, legal_destination_ids=LEGAL,
        cross_folder_moves=True, constraints=CONSTRAINTS,
        high_level_folders={"root_documents": world.documents},
        volume_of=volume, protected_handling_classes=PROTECTED_CLASSES,
        collision_policy=COLLISION_POLICY,
        expiration_state="no expiry configured",
        component_version="apply-test", now=clock, mint_id=ids)


def test_freezing_writes_one_plan_per_placement_and_nothing_moves(
        world, ids, clock):
    proposal = _freeze(world, world.decisions, ids=ids, clock=clock)

    assert len(proposal.plans) == 4
    assert proposal.held == ()
    # The disk is exactly as it was. Freeze is a promise, not an action.
    for source in world.sources.values():
        assert source.exists()
    assert not (world.documents / "Coursework").exists()

    destinations = {plan.resolved_destination_path for plan in proposal.plans}
    assert str(world.documents / "Coursework" / "PHYS1401" / "Syllabus.pdf") \
        in destinations
    assert str(world.documents / "Coursework" / "PHYS1401" / "Homework"
               / "Homework 3.pdf") in destinations
    assert str(world.documents / "Reading Inbox" / "saved article.pdf") \
        in destinations


def test_a_frozen_plan_can_be_read_back_without_re_running_anything(
        world, ids, clock):
    """The point of the whole design: `--apply` is a second invocation.

    The tree's plan version is a fresh uuid on every run (`cli.py`'s
    `run_token`), so "run it again and compare" cannot work. What survives
    between the two commands is these rows.
    """
    proposal = _freeze(world, world.decisions, ids=ids, clock=clock)
    world.conn.commit()

    read_back = frozen_plans(world.conn)
    assert {plan.plan_id for plan in read_back} == {
        plan.plan_id for plan in proposal.plans}
    one = current_plan(world.conn, proposal.plans[0].plan_id)
    assert one == proposal.plans[0]


def test_the_collision_behaviour_frozen_into_every_plan_is_stop_and_ask(
        world, ids, clock):
    """`74` §8 Q3 is unruled, so no plan may carry a behaviour needing a suffix."""
    proposal = _freeze(world, world.decisions, ids=ids, clock=clock)
    assert {plan.collision_policy for plan in proposal.plans} == {"stop_and_ask"}


def test_a_placement_awaiting_an_approval_is_held_and_named_not_dropped(
        world, review_required, ids, clock):
    proposal = _freeze(world, review_required, ids=ids, clock=clock)

    assert len(proposal.plans) == 3
    assert [(item.reason, item.detail) for item in proposal.held] == [
        (AWAITING_APPROVAL, "review_required")]
    assert proposal.held[0].file_id in world.sources


def test_a_file_already_at_its_destination_is_held_rather_than_moved_onto_itself(
        world, ids, clock):
    """A no-op move is not a move, and counting it as one makes the screen lie."""
    settled = world.documents / "Reading Inbox"
    settled.mkdir(parents=True)
    article = next(path for path in world.sources.values()
                   if path.name == "saved article.pdf")
    moved = settled / article.name
    article.rename(moved)
    file_id = next(key for key, path in world.sources.items() if path == article)
    world.conn.execute("UPDATE files SET current_path = ? WHERE file_id = ?",
                       (str(moved), file_id))

    proposal = _freeze(world, world.decisions, ids=ids, clock=clock)
    assert len(proposal.plans) == 3
    assert [item.reason for item in proposal.held] == [ALREADY_AT_DESTINATION]


def test_a_decision_naming_a_node_outside_the_frozen_tree_is_held_with_its_class(
        world, ids, clock):
    stray = dataclasses.replace(
        world.decisions[0],
        destination=dataclasses.replace(world.decisions[0].destination,
                                        node_id="n-phys"))
    assert len(_freeze(world, (stray,), ids=ids, clock=clock).plans) == 1

    proposal = freeze(
        world.conn, (stray,), nodes=NODES,
        legal_destination_ids=frozenset({"n-read"}),
        cross_folder_moves=True, constraints=CONSTRAINTS,
        high_level_folders={"root_documents": world.documents},
        volume_of=lambda path: "vol-main",
        protected_handling_classes=PROTECTED_CLASSES,
        collision_policy=COLLISION_POLICY,
        expiration_state="no expiry configured",
        component_version="apply-test", now=clock, mint_id=ids)
    assert proposal.plans == ()
    assert proposal.held[0].reason == REFUSED_AT_CONSTRUCTION
    assert proposal.held[0].detail == "node_refuses_placement"


def test_only_place_decisions_become_plans(world, ids, clock):
    from placement.fixtures import CORRECT_ABSTENTION

    abstained = dataclasses.replace(
        CORRECT_ABSTENTION, plan_version="plan-under-test",
        subject=world.decisions[0].subject)
    proposal = _freeze(world, (abstained,), ids=ids, clock=clock)
    # Not a refusal and not a hold: `00`:114 makes correct abstention a
    # successful outcome, and it was already reported by the run.
    assert (proposal.plans, proposal.held) == ((), ())


def test_freezing_again_replaces_the_earlier_proposal(world, ids, clock):
    first = _freeze(world, world.decisions, ids=ids, clock=clock)
    world.conn.commit()
    second = _freeze(world, world.decisions[:1], ids=ids, clock=clock)
    world.conn.commit()

    assert second.replaces is not None
    assert second.replaces.frozen_at == first.frozen_at
    assert second.replaces.count == 4
    # And reading back gives the second proposal only.
    assert {plan.plan_id for plan in frozen_plans(world.conn)} == {
        second.plans[0].plan_id}


def test_the_plan_carries_the_precondition_the_design_names(world, ids, clock):
    """`00`:158-170's list, spot-checked on the fields a stale plan turns on."""
    plan = _freeze(world, world.decisions[:1], ids=ids, clock=clock).plans[0]
    source = world.sources[plan.file_id]

    assert plan.expected_source_path == str(source)
    assert plan.expected_content_hash
    state = json.loads(plan.expected_size_and_modification_state)
    assert state["observed_size"] == source.stat().st_size
    assert json.loads(plan.creation_time_and_expiration_state)["expiration_state"]
