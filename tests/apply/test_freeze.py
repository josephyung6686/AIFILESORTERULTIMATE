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

from placement.records import Ask, ReturnTarget
from placement.vocabulary import (
    ABSTAIN, ASK_USER, BLOCKED_PENDING_USER, CONFIRMED_DOMAIN_GROUP,
    MARK_STATE, OUTCOMES, PLACE, RETURN_TO_PLACEMENT, UNSUPPORTED,
)

from apply_run.freeze import (
    ALREADY_AT_DESTINATION, AWAITING_CLASSIFICATION, NOT_A_MOVE, NOT_SHOWN,
    PROTECTED_NEEDS_PERMISSION, REFUSED_AT_CONSTRUCTION, freeze, frozen_plans,
)

from .conftest import COLLISION_POLICY, CONSTRAINTS, LEGAL, NODES, PROTECTED_CLASSES


def _no_approval(plan, at):
    """Every world below is auto-eligible, so nothing here needs an approval.

    A stub that quietly returned would let a plan needing consent be frozen with
    none, and the tests would still be green. This raises instead: the day a
    fixture here grows a reviewable placement, the test says so.
    """
    raise AssertionError(
        f"{plan.plan_id} asked for an approval, and no test in this file has a "
        "person at the screen to give one")


def _freeze(world, decisions, *, ids, clock, volume=lambda path: "vol-main",
            shown=None, approve=_no_approval):
    return freeze(
        world.conn, decisions, nodes=NODES, legal_destination_ids=LEGAL,
        cross_folder_moves=True, constraints=CONSTRAINTS,
        high_level_folders={"root_documents": world.documents},
        volume_of=volume, protected_handling_classes=PROTECTED_CLASSES,
        collision_policy=COLLISION_POLICY,
        expiration_state="no expiry configured",
        # The report named every file in these worlds, which is what the freeze
        # run does. `tests/apply/test_freeze_approval.py` is where the set is
        # narrowed and where the guard that reads it is proved.
        shown_file_ids=frozenset(world.sources) if shown is None
        else frozenset(shown),
        approve_reviewed=approve,
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


def test_a_placement_the_person_never_saw_is_held_and_named_not_dropped(
        world, review_required, ids, clock):
    """A reviewable placement the screen did not name is not the freeze's to approve.

    This test used to say that NO reviewable placement could be frozen, because
    P13 had no surface. The owner ruled on 2026-09-02 that `--freeze` is that
    surface, so what is left of the rule is the half that still binds: an
    approval covers what the person was shown and nothing else. The held file is
    still named rather than dropped, which was always the point.
    """
    unseen = next(d.subject.file_id for d in review_required
                  if d.review_policy == "review_required")
    proposal = _freeze(world, review_required, ids=ids, clock=clock,
                       shown=frozenset(world.sources) - {unseen})

    assert len(proposal.plans) == 3
    assert [(item.reason, item.detail) for item in proposal.held] == [
        (NOT_SHOWN, "review_required")]
    assert proposal.held[0].file_id == unseen


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
        shown_file_ids=frozenset(world.sources), approve_reviewed=_no_approval,
        component_version="apply-test", now=clock, mint_id=ids)
    assert proposal.plans == ()
    assert proposal.held[0].reason == REFUSED_AT_CONSTRUCTION
    assert proposal.held[0].detail == "node_refuses_placement"


#: The one extra field each outcome's RECORD shape requires.
#: `PlacementDecision` enforces every pairing both ways -- `mark_state` names the
#: state, `ask_user` carries the question, `return_to_placement` names what it
#: goes back to -- so this table is the record contract and not decoration, and a
#: decision built without it does not exist to be dropped.
_SHAPE = {
    MARK_STATE: {"marked_state": UNSUPPORTED},
    ASK_USER: {"ask": Ask(question="Which of these is its home?",
                          options=("n-phys", "n-read"))},
    RETURN_TO_PLACEMENT: {"return_target": ReturnTarget(
        kind=CONFIRMED_DOMAIN_GROUP, id="group-1")},
}


def _outcome_decisions(world):
    """One decision per outcome P11 publishes that is not `place`.

    Driven off `OUTCOMES` rather than off a list written here, so an outcome P11
    adds tomorrow is in this test the day it is added rather than the day
    somebody remembers to add it. `return_to_placement` starts from the residual
    fixture because §7.9 emits it only on that path and the record says so.
    """
    from placement.fixtures import CORRECT_ABSTENTION, RESIDUAL_LEAVE_IN_PLACE

    made = []
    for index, outcome in enumerate(o for o in OUTCOMES if o != PLACE):
        base = (RESIDUAL_LEAVE_IN_PLACE if outcome == RETURN_TO_PLACEMENT
                else CORRECT_ABSTENTION)
        made.append(dataclasses.replace(
            base, plan_version="plan-under-test",
            decision_id=f"decision-{outcome}", outcome=outcome,
            subject=world.decisions[index % len(world.decisions)].subject,
            # An abstention names why and no other outcome may (§6.10).
            abstention_reason=(CORRECT_ABSTENTION.abstention_reason
                               if outcome == ABSTAIN else None),
            **_SHAPE.get(outcome, {})))
    return tuple(made)


def test_only_place_decisions_become_plans(world, ids, clock):
    """Still true of the PLANS, which is the half `00`:114 was ever about.

    A correct abstention is a successful outcome and `00`:112's leave-in-place is
    a decision not to move, so neither may become a plan in the approved set.
    Neither may vanish off the screen either -- that is the test below.
    """
    proposal = _freeze(world, _outcome_decisions(world), ids=ids, clock=clock)
    assert proposal.plans == ()


def test_every_decision_that_is_not_a_move_is_still_named_with_a_reason(
        world, ids, clock):
    """`94` F22, over every outcome at once.

    Four files in one folder: two frozen, one listed as not frozen, and the
    fourth -- a plain text file with no extension -- named NOWHERE in the block.
    It had reached a decision (`abstain`, under `blocked_pending_user`) and the
    skip that kept a correct abstention out of the withheld list took it with it.
    `84` §1's rule is not only about protected material: marked and counted,
    never silently omitted. A person counting their files against that block
    found one missing and had nothing to search for.

    The detail is the outcome itself, so `report` can say what was decided
    instead of printing one sentence over six different things.
    """
    decisions = _outcome_decisions(world)
    proposal = _freeze(world, decisions, ids=ids, clock=clock)

    assert len(proposal.held) == len(decisions)
    assert {(item.reason, item.detail) for item in proposal.held} == {
        (NOT_A_MOVE, decision.outcome) for decision in decisions}
    # No destination is claimed for a decision that named none.
    assert {item.destination_node for item in proposal.held} == {None}


def test_a_freeze_accounts_for_every_decision_it_was_given(world, ids, clock):
    """The property, not the number: plans + holds == what went in.

    This is what a person does with the block -- add the two counts and compare
    them to the size of their folder -- and it is the assertion that holds for
    any corpus rather than for the four files that happened to find the bug.
    """
    decisions = world.decisions + _outcome_decisions(world)
    proposal = _freeze(world, decisions, ids=ids, clock=clock)

    assert len(proposal.plans) + len(proposal.held) == len(decisions)
    assert len(proposal.plans) == len(world.decisions)


def test_an_unclassified_file_that_never_reached_a_placement_says_so(
        world, ids, clock):
    """`blocked_pending_user` is the truer sentence than the outcome's name.

    It is what the file in `94` F22 actually carried. Nothing has looked inside
    it, which is true whatever the outcome, and it is the same reason -- so the
    same sentence -- that a `place` decision under that policy is held under.
    A person reading the block sees one fact, once, for both.
    """
    from placement.fixtures import CORRECT_ABSTENTION

    unclassified = dataclasses.replace(
        CORRECT_ABSTENTION, plan_version="plan-under-test",
        review_policy=BLOCKED_PENDING_USER,
        subject=world.decisions[0].subject)
    proposal = _freeze(world, (unclassified,), ids=ids, clock=clock)

    assert [(item.reason, item.detail) for item in proposal.held] == [
        (AWAITING_CLASSIFICATION, BLOCKED_PENDING_USER)]


def test_a_protected_file_that_abstained_is_still_counted_and_named_as_protected(
        world, ids, clock):
    """`94` F16. The rule above is right for an abstention and wrong for a passport.

    Five files in the corpus and the freeze block said *"Not frozen, and still
    exactly where they are -- 4 file(s)"*: the passport reached an `abstain`, and
    the skip that keeps a correct abstention out of the withheld list took it
    with it. `84` §1's standing rule has no exception -- protected material is
    marked and counted and NEVER silently omitted -- and the freeze block is
    exactly the screen a person reads to ask what happened to their files.

    The whole held row is asserted, reason and detail and destination together: a
    row under any other reason is a different sentence on the screen, and a row
    naming a destination would claim the run had chosen one when it declined to.
    """
    from placement.fixtures import CORRECT_ABSTENTION

    passport = next(decision for decision in world.decisions
                    if decision.privacy.protected)
    abstained = dataclasses.replace(
        CORRECT_ABSTENTION, plan_version="plan-under-test",
        subject=passport.subject, privacy=passport.privacy)

    proposal = _freeze(world, (abstained,), ids=ids, clock=clock)
    assert proposal.plans == ()
    assert [(item.file_id, item.reason, item.detail, item.destination_node)
            for item in proposal.held] == [
        (passport.subject.file_id, PROTECTED_NEEDS_PERMISSION,
         "highly_sensitive_credential_bearing", None)]


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
