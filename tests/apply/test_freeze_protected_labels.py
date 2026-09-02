"""Where a freeze learns which node NAMES came from protected material.

`74` §5.6 / `69` §3 blocker 3: a client's passport number reached a group's
`display_label` and printed as a proposed FOLDER NAME. P12 refuses to compose a
directory out of such a label, and it cannot answer the question itself -- the
only privacy field on a `Node` is `handling_class`, which P10 collapses to the
strongest class among a branch's MEMBERS. That is the floor for what may be filed
there, and reading it as provenance is `94` F1.

So the join is made here, once, over records this run already wrote, and handed
down. These two tests are the pair: the passport-named node still refuses, and
the ordinary branch under a protected floor still freezes. A build that made only
the first pass is where this started; a build that made only the second is the
leak `69` recorded.
"""
from __future__ import annotations

import dataclasses
import json

from tree_design.records import Node

from apply_run.freeze import REFUSED_AT_CONSTRUCTION, freeze

from .conftest import COLLISION_POLICY, CONSTRAINTS, PLAN_VERSION, PROTECTED_CLASSES

#: The label from `69` §3 blocker 3, in the shape the report printed it.
PASSPORT_LABEL = "X12345678"
GROUP_ID = "group:subject:passport"


def _node(node_id, label, parent, *, groups=(), handling="personal_non_sensitive"):
    return Node(
        node_id=node_id, plan_version_id=PLAN_VERSION, node_type="proposed",
        display_label=label, parent_node_id=parent,
        root_anchor="root_documents", ordinal=0,
        associated_group_ids=tuple(groups), explanation="fixture",
        node_role="ordinary", accepts_placement=True,
        handling_class=handling, origin_node_id=node_id)


def _group(conn, *, label, file_id):
    """One coherent group whose label IS its anchor value, as `naming` mints it."""
    conn.execute(
        "INSERT INTO groups (group_id, seed_ref, seed_kind, proposed_basis, "
        "anchor_facts, pre_model_signals, anchor_count, coherence_verdict, "
        "coherence_citations, group_category, display_label, label_source, "
        "conflicts, stop_rule_hits, state, sensitivity_state, created_by, "
        "created_at) VALUES (?, 'seed', 'file', 'basis', ?, '[]', 1, "
        "'coherent', '[]', NULL, ?, 'engine', '[]', '[]', 'supported', "
        "'none', 'fixture', '2026-09-02T00:00:00Z')",
        (GROUP_ID,
         json.dumps([{"field": "subject", "value": label,
                      "file_ids": [file_id],
                      "reliability_state": "direct",
                      "observation_key": "obs-passport"}]),
         label))


def _no_approval(plan, at):
    raise AssertionError(
        f"{plan.plan_id} asked for an approval and no test here has a person "
        "at the screen to give one")


def _freeze(world, decisions, nodes, *, ids, clock):
    return freeze(
        world.conn, decisions, nodes=nodes,
        legal_destination_ids=frozenset(node.node_id for node in nodes),
        cross_folder_moves=True, constraints=CONSTRAINTS,
        high_level_folders={"root_documents": world.documents},
        volume_of=lambda path: "vol-main",
        protected_handling_classes=PROTECTED_CLASSES,
        collision_policy=COLLISION_POLICY,
        expiration_state="no expiry configured",
        shown_file_ids=frozenset(world.sources), approve_reviewed=_no_approval,
        component_version="apply-test", now=clock, mint_id=ids)


def _protected_file(world):
    """The world's passport, and a decision placing it under the tree below."""
    return next(decision for decision in world.decisions
                if decision.privacy.protected)


def test_a_node_named_after_a_protected_group_refuses_at_construction(
        world, ids, clock):
    """The guard `69` §3 blocker 3 asked for, reached through the live join.

    The group's label is its anchor value and its anchor file is the passport, so
    the node that carries that label carries protected material as its NAME. The
    refusal is asserted as the held row's reason and detail together: a run that
    held it for any other reason has not refused for this one.
    """
    _group(world.conn, label=PASSPORT_LABEL,
           file_id=_protected_file(world).subject.file_id)
    nodes = (_node("n-course", "Coursework", None),
             _node("n-pass", PASSPORT_LABEL, "n-course", groups=(GROUP_ID,)))
    ordinary = dataclasses.replace(
        world.decisions[0],
        destination=dataclasses.replace(world.decisions[0].destination,
                                        node_id="n-pass"))

    proposal = _freeze(world, (ordinary,), nodes, ids=ids, clock=clock)
    assert proposal.plans == ()
    assert [(item.reason, item.detail) for item in proposal.held] == [
        (REFUSED_AT_CONSTRUCTION, "protected_without_policy")]
    # The label is the protected material and must not travel into the record.
    assert PASSPORT_LABEL not in str([dataclasses.asdict(item)
                                      for item in proposal.held])


def test_a_branch_whose_floor_one_protected_member_raised_still_freezes(
        world, ids, clock):
    """`94` F1, at the seam that computes the answer.

    `Coursework` holds the passport, so P10 writes `sensitive_personal` on it --
    the FLOOR, which is right and stays. Nothing about the name `Coursework` came
    from the passport, and the group that authored it is not in the provenance,
    so the ordinary file under it freezes. The plan's whole destination path is
    asserted: a freeze that produced a plan pointing somewhere else would satisfy
    "it froze" and would move a person's file to a folder nobody approved.
    """
    _group(world.conn, label=PASSPORT_LABEL,
           file_id=_protected_file(world).subject.file_id)
    nodes = (_node("n-course", "Coursework", None, groups=(GROUP_ID,),
                   handling="sensitive_personal"),
             _node("n-phys", "PHYS1401", "n-course", groups=(GROUP_ID,)))
    ordinary = dataclasses.replace(
        world.decisions[0],
        destination=dataclasses.replace(world.decisions[0].destination,
                                        node_id="n-phys"))

    proposal = _freeze(world, (ordinary,), nodes, ids=ids, clock=clock)
    assert proposal.held == ()
    assert len(proposal.plans) == 1
    assert proposal.plans[0].resolved_destination_path == str(
        world.documents / "Coursework" / "PHYS1401" / "Syllabus.pdf")
