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
from placement.vocabulary import (
    AUTO_ELIGIBLE, BLOCKED_PENDING_USER, PLACE, REVIEW_REQUIRED,
)
from review_run.structure import (
    protected_label_classes, protected_label_provenance,
)
from tree_design.records import Node

from mutation.constraints import FilesystemConstraints
from mutation.names import NameUnresolvable
from mutation.plan import MovePlan, PlanRefused, build_plan, record_plan

#: Why a placement the run decided on did not become a frozen plan. Closed, and
#: every member is printed to the person: `84` §1's rule that protected material
#: is never silently omitted is the same rule for every held file. A held file
#: that no sentence names is a file that vanished.
AWAITING_APPROVAL: str = "awaiting_approval"
#: `placement.privacy.blocked_policy`'s own distinction, kept: *"a reviewer can
#: act on a decision that merely needs confirming, and cannot act on one whose
#: subject nothing has classified."* A freeze is a reviewer, so it may not
#: collapse the two either -- and the sentence a person reads for this one is
#: about classification rather than about approval, because that is what is true.
AWAITING_CLASSIFICATION: str = "awaiting_classification"
#: The person's screen never named this file, so their freeze cannot have
#: approved it. §8.7 requires a decision to be stored with the evidence that
#: produced it, and there is no evidence that this one was ever displayed.
NOT_SHOWN: str = "not_shown"
#: Protected, and no policy permits moving it. `84` §1: marked and counted, never
#: opened -- and never swept into a bulk approval, which is what freezing every
#: reviewable placement would make of a passport.
PROTECTED_NEEDS_PERMISSION: str = "protected_needs_permission"
ALREADY_AT_DESTINATION: str = "already_at_destination"
REFUSED_AT_CONSTRUCTION: str = "refused_at_construction"
NO_SAFE_NAME: str = "no_safe_name"
HOLD_REASONS: tuple[str, ...] = (
    AWAITING_APPROVAL, AWAITING_CLASSIFICATION, NOT_SHOWN,
    PROTECTED_NEEDS_PERMISSION, ALREADY_AT_DESTINATION,
    REFUSED_AT_CONSTRUCTION, NO_SAFE_NAME)


@dataclass(frozen=True)
class Held:
    """One placement that will not move, and the reason a person is owed."""

    file_id: str
    source_path: str | None
    #: `None` when the decision named none. A protected file that ABSTAINED is
    #: held and counted (`84` §1), and it has no destination to name -- writing
    #: one in would be inventing the answer the run declined to give.
    destination_node: str | None
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



def _withheld(decision: PlacementDecision,
              shown_file_ids: frozenset[str]) -> tuple[str, str] | None:
    """Why this placement is not the person's to approve, or `None`.

    Three refusals and a fallback, and none of them is about tidiness.

    The **protected** one is first because it is the one a mistake costs most.
    `placement.privacy.review_policy_for`'s third rule puts a protected file with
    no permitting policy into `review_required`, which is the queue a freeze now
    empties -- so without this line the single word `--freeze` would be consent
    to move a passport. Only `74` Wave B9's surface can grant that, one named
    file at a time.

    The **unshown** one is what makes the approval informed rather than assumed.
    §8.7 wants a decision stored with the evidence that produced it, and P13's
    `approve` refuses an approval whose presentation is missing; this is the same
    rule one step earlier, where the file can still be named to the person.

    The **unclassified** one keeps `placement.privacy`'s two obligations apart.
    A file nothing has looked at is not a file waiting for a nod.

    The fallback catches a `review_policy` P11 adds after this was written. It
    holds rather than approving, because a policy this build has no rule for is
    not one it may treat as satisfied.
    """
    if decision.review_policy == AUTO_ELIGIBLE:
        return None
    if decision.privacy.protected:
        return PROTECTED_NEEDS_PERMISSION, decision.privacy.handling_class
    if decision.review_policy == BLOCKED_PENDING_USER:
        return AWAITING_CLASSIFICATION, decision.review_policy
    if decision.subject.file_id not in shown_file_ids:
        return NOT_SHOWN, decision.review_policy
    if decision.review_policy == REVIEW_REQUIRED:
        return None
    return AWAITING_APPROVAL, decision.review_policy


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
           shown_file_ids: frozenset[str],
           approve_reviewed: Callable[[MovePlan, str], None],
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

    **Protected material is the one exception, and `94` F16 is why.** That rule
    is right for an ordinary abstention and wrong for a passport: `84` §1 says
    protected material is marked and counted and NEVER SILENTLY OMITTED, and
    `93` §4 puts the count on the screen in both views. A five-file corpus whose
    fifth file was a passport scan reported *"Not frozen, and still exactly where
    they are -- 4 file(s)"*, and the missing one was the file the standing rule
    exists for. So a protected subject is held whatever its outcome, under the
    reason it is already held under when it reaches a `place` decision, and
    `report` prints it as a count with no name and no command.

    **The provenance of every node's NAME is joined here, once, and handed down.**
    P12 refuses to compose a directory out of a label that IS protected material
    (`74` §5.6) and cannot answer that from the tree: `Node.handling_class` is
    P10's floor, raised for a whole branch by one protected member, and reading
    it as provenance is `94` F1 -- a passport scan in a folder made every
    ordinary file beside it unfilable and named the coursework as the protected
    thing. `review_run.structure` owns the join, the same one P13's tree printer
    asks, so the screen and the path agree about which names came from where.
    It is a read over records this run already wrote, not a policy: nothing is
    chosen here that `src/cli.py` has not already decided.
    """
    frozen_at = now()
    label_classes = protected_label_classes(
        nodes,
        provenance=protected_label_provenance(
            conn,
            group_ids=tuple(dict.fromkeys(
                group_id for node in nodes
                for group_id in node.associated_group_ids))))
    replaces = _previous(conn)
    plans: list[MovePlan] = []
    held: list[Held] = []

    for decision in decisions:
        if decision.outcome != PLACE or decision.destination is None:
            if decision.privacy.protected:
                # `94` F16. Counted, named as protected, and NOT named by
                # filename -- the same row `_withheld` writes for a protected
                # placement, so the two arrive at `report` as one reason and one
                # sentence. `destination_node` is `None` because the decision
                # named none: this is the run declining to move it, not a plan
                # that failed.
                held.append(Held(
                    file_id=decision.subject.file_id, source_path=None,
                    destination_node=None, reason=PROTECTED_NEEDS_PERMISSION,
                    detail=decision.privacy.handling_class))
            continue
        node_id = decision.destination.node_id
        withheld = _withheld(decision, shown_file_ids)
        if withheld is not None:
            held.append(Held(
                file_id=decision.subject.file_id, source_path=None,
                destination_node=node_id, reason=withheld[0],
                detail=withheld[1]))
            continue
        try:
            built = build_plan(
                conn, decision, nodes=nodes,
                legal_destination_ids=legal_destination_ids,
                cross_folder_moves=cross_folder_moves, constraints=constraints,
                high_level_folders=high_level_folders, volume_of=volume_of,
                protected_handling_classes=protected_handling_classes,
                protected_label_classes=label_classes,
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
        if plan.required_review_policy == REVIEW_REQUIRED:
            # BEFORE `record_plan`, and the order is load-bearing. Writing the
            # plan first and the approval second would leave a plan in the
            # approved set with no approval the moment P13's writer refuses --
            # a file every apply run must then decline, which is the state this
            # whole change exists to end. The approval refuses loudly instead.
            approve_reviewed(plan, frozen_at)
        record_plan(conn, plan, resolution, created_at=frozen_at,
                    component_version=component_version)
        plans.append(plan)

    versions = {plan.organization_plan_version for plan in plans}
    return FrozenProposal(
        frozen_at=frozen_at,
        plan_version=versions.pop() if len(versions) == 1 else None,
        plans=tuple(plans), held=tuple(held), replaces=replaces)
