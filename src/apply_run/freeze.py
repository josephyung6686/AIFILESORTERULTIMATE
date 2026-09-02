"""Turning a proposal into an approved destination tree.

`00`:51 -- *"the user edits and freezes those proposals into an approved
destination tree."* `00`:102 -- *"When the user is satisfied, they freeze the
tree. Freeze records the approved hierarchy and prevents later systems from
inventing new destinations outside it."*

**What is durable afterwards is the plan, not the proposal.** `00`:156-170 lists
the complete expected precondition a plan must capture -- the file's identity,
its expected hash, its expected source path and volume, its expected size and
modification state, the destination node, the resolved path, the collision
policy, the sensitivity state, the reason, the review policy, and the creation
and expiration state -- and `mutation.plan.record_plan` writes exactly that. So
applying does not re-run the pipeline and compare: it reads back what the person
approved. That is not a shortcut. The tree's plan version is a fresh uuid on
every run, so a re-run produces a structurally identical tree under names that
have never been seen before, and "compare the two" has nothing to compare.

**Freeze is a promise, never an action.** Nothing here touches a disk. Every
directory the plans name is still absent when this returns.

**A freeze is the set of plans written at one instant.** `created_at` is
sampled once for the whole call and stamped on every plan, so the latest freeze
is the plans carrying the latest `created_at`. That is why re-freezing does not
have to supersede anything: the older plans stay exactly as they were written
(§8.2 makes these tables append-only anyway), and they are simply no longer the
approved set. `replaces` on the result is how the person is told.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from placement.records import PlacementDecision
from placement.vocabulary import PLACE, AUTO_ELIGIBLE
from tree_design.records import Node

from mutation.constraints import FilesystemConstraints
from mutation.names import NameUnresolvable
from mutation.plan import MovePlan, PlanRefused, build_plan, record_plan

#: Why a placement the run decided on did not become a frozen plan. Closed, and
#: every member is printed to the person: `84` §1's rule that protected material
#: is never silently omitted is the same rule for every held file. A held file
#: that no sentence names is a file that vanished.
AWAITING_APPROVAL: str = "awaiting_approval"
ALREADY_AT_DESTINATION: str = "already_at_destination"
REFUSED_AT_CONSTRUCTION: str = "refused_at_construction"
NO_SAFE_NAME: str = "no_safe_name"
HOLD_REASONS: tuple[str, ...] = (
    AWAITING_APPROVAL, ALREADY_AT_DESTINATION, REFUSED_AT_CONSTRUCTION,
    NO_SAFE_NAME)


@dataclass(frozen=True)
class Held:
    """One placement that will not move, and the reason a person is owed."""

    file_id: str
    source_path: str | None
    destination_node: str
    reason: str
    #: The refusal class, the review policy, or whatever narrower fact the
    #: reason needs to be legible. One field because a reason has one detail.
    detail: str


@dataclass(frozen=True)
class Replaced:
    """The proposal this freeze supersedes, so a person is told it is gone."""

    frozen_at: str
    count: int


@dataclass(frozen=True)
class FrozenProposal:
    frozen_at: str
    plan_version: str | None
    plans: tuple[MovePlan, ...]
    held: tuple[Held, ...]
    replaces: Replaced | None


def latest_freeze(conn: sqlite3.Connection) -> str | None:
    """When the current approved set was frozen, or `None` if none has been."""
    row = conn.execute(
        "SELECT MAX(created_at) FROM move_plans WHERE superseded_by IS NULL"
    ).fetchone()
    return None if row is None else row[0]


def frozen_plans(conn: sqlite3.Connection) -> tuple[MovePlan, ...]:
    """Every plan in the approved set, oldest-minted first."""
    frozen_at = latest_freeze(conn)
    if frozen_at is None:
        return ()
    rows = conn.execute(
        "SELECT payload FROM move_plans WHERE created_at = ? "
        "AND superseded_by IS NULL ORDER BY record_id", (frozen_at,)).fetchall()
    return tuple(MovePlan(**json.loads(row[0])) for row in rows)


def _previous(conn: sqlite3.Connection) -> Replaced | None:
    frozen_at = latest_freeze(conn)
    if frozen_at is None:
        return None
    count = conn.execute(
        "SELECT COUNT(*) FROM move_plans WHERE created_at = ? "
        "AND superseded_by IS NULL", (frozen_at,)).fetchone()[0]
    return Replaced(frozen_at=frozen_at, count=count)


def freeze(conn: sqlite3.Connection,
           decisions: Sequence[PlacementDecision], *,
           nodes: Sequence[Node],
           legal_destination_ids: frozenset[str],
           cross_folder_moves: bool,
           constraints: FilesystemConstraints,
           high_level_folders: Mapping[str, Path],
           volume_of: Callable[[Path], str],
           protected_handling_classes: frozenset[str],
           collision_policy: str,
           expiration_state: str,
           component_version: str,
           now: Callable[[], str],
           mint_id: Callable[[], str]) -> FrozenProposal:
    """Record one plan per placement that can move, and name every one that cannot.

    `collision_policy` and `expiration_state` are passed straight through and
    chosen nowhere in this package -- `mutation.plan.build_plan`'s docstring is
    explicit that both are the composition root's, and nothing here has more
    right to pick them than P12 did.

    A decision whose outcome is not `place` produces neither a plan nor a hold.
    `00`:114 makes correct abstention a successful outcome and `00`:112's
    leave-in-place is a decision not to move; recording either as something
    withheld would tell a person that files were kept back when in fact they
    were decided.
    """
    frozen_at = now()
    replaces = _previous(conn)
    plans: list[MovePlan] = []
    held: list[Held] = []

    for decision in decisions:
        if decision.outcome != PLACE or decision.destination is None:
            continue
        node_id = decision.destination.node_id
        if decision.review_policy != AUTO_ELIGIBLE:
            # `mutation.approval` is explicit that absence of a `ReviewApproval`
            # IS the refusal and that P13 -- the surface that would collect one
            # -- is unbuilt. Freezing such a plan would put a file in the
            # approved set that every apply run must then decline, which reads
            # to a person as a product that keeps failing rather than one that
            # is waiting for a screen it does not have yet.
            held.append(Held(
                file_id=decision.subject.file_id, source_path=None,
                destination_node=node_id, reason=AWAITING_APPROVAL,
                detail=decision.review_policy))
            continue
        try:
            built = build_plan(
                conn, decision, nodes=nodes,
                legal_destination_ids=legal_destination_ids,
                cross_folder_moves=cross_folder_moves, constraints=constraints,
                high_level_folders=high_level_folders, volume_of=volume_of,
                protected_handling_classes=protected_handling_classes,
                collision_policy=collision_policy,
                expiration_state=expiration_state, now=now, mint_id=mint_id)
        except PlanRefused as refused:
            held.append(Held(
                file_id=decision.subject.file_id, source_path=None,
                destination_node=node_id, reason=REFUSED_AT_CONSTRUCTION,
                detail=refused.refusal_class))
            continue
        except NameUnresolvable as refused:
            # `build_plan` states that this propagates because none of Contract
            # out §5's ten refusal classes means "no safe name exists" and
            # minting an eleventh would be P12 authoring its own SPEC. It is
            # caught HERE, where a run can name the file and carry on, rather
            # than being allowed to end a freeze over the corpus.
            held.append(Held(
                file_id=decision.subject.file_id, source_path=None,
                destination_node=node_id, reason=NO_SAFE_NAME,
                detail=str(refused)))
            continue
        if built is None:
            continue
        plan, resolution = built
        if plan.expected_source_path == plan.resolved_destination_path:
            # Not a move. Freezing it would put a file in the approved set whose
            # application can only be a no-op, and the count on the screen would
            # promise an action the person then cannot see having happened.
            held.append(Held(
                file_id=plan.file_id, source_path=plan.expected_source_path,
                destination_node=node_id, reason=ALREADY_AT_DESTINATION,
                detail=plan.resolved_destination_path))
            continue
        record_plan(conn, plan, resolution, created_at=frozen_at,
                    component_version=component_version)
        plans.append(plan)

    versions = {plan.organization_plan_version for plan in plans}
    return FrozenProposal(
        frozen_at=frozen_at,
        plan_version=versions.pop() if len(versions) == 1 else None,
        plans=tuple(plans), held=tuple(held), replaces=replaces)
