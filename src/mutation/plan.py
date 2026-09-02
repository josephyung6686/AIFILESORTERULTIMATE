"""§8.3's move plan record, and the refusals that stop one being built.

*"A plan should not store only source and destination paths. It should capture
the complete expected precondition"* (`00`:156). The thirteen names in
`PLAN_PRECONDITION_FIELDS` are `00`:158-170's own list, in `00`'s own order, and
a plan missing any one of them is rejected at construction rather than executed
with a gap.

**A plan is a proposal. Creating one mutates nothing** -- no directory, no file,
not even a `stat` of the destination. Everything below reads P1's row, P10's
frozen tree and P11's decision, and composes.

Two things this module deliberately does NOT do:

* It does not refuse a decision whose `review_policy` demands review. §8.3 fixes
  the order -- *"first create a plan, show it to the user where policy requires
  review, validate that the plan is still current"* -- so the plan is built and
  carries the policy in `required_review_policy`. What P12 refuses is to EXECUTE
  it, at the pre-apply gate, and the record that lifts that refusal is P13's
  `review_approval`. Refusing here would leave the review step with nothing to
  show and P13 with nothing to render.
* It does not create, follow or record a link. `74` §8 Q9 -- *"does the
  shared-material convention require P12 to CREATE a link?"* -- is the owner's
  and is open. §8.3 says only not to FOLLOW symbolic links during mutation, so
  the plan record carries no link field and no link instruction. When Q9 closes,
  the answer lands in a new carried field; inventing one now would be P12
  answering it.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

from database_agent.events import append_event
from database_agent.files_table import get_file
from database_agent.supersede import mark_superseded
from evidence_shape.canonical import canonical_json
from placement.records import PlacementDecision
from placement.vocabulary import (
    LEAVE_IN_PLACE_DISPOSITION, PLACE, RESIDUAL_ROLE, REVIEW_ONLY,
)
from tree_design.records import Node

from mutation.constraints import FilesystemConstraints
from mutation.names import resolve_name
from mutation.resolution import (
    PathResolution, ResolutionRefused, record_resolution, resolve_destination,
)
from mutation.vocabulary import (
    COLLISION_BEHAVIOURS, NODE_NOT_IN_FROZEN_TREE, NODE_REFUSES_PLACEMENT,
    PLANNED_MOVE, SOURCE_OR_DESTINATION_UNAVAILABLE, SUBSYSTEM, check,
)

#: `00`:158-170's thirteen, in `00`'s order. The order is part of the assertion:
#: the field list is quoted from the design, not assembled from what the code
#: happened to need.
PLAN_PRECONDITION_FIELDS: tuple[str, ...] = (
    "plan_id", "file_id", "expected_content_hash", "expected_source_path",
    "expected_source_volume", "expected_size_and_modification_state",
    "requested_destination_node", "resolved_destination_path", "collision_policy",
    "sensitivity_and_consent_state", "reason_and_evidence_summary",
    "required_review_policy", "creation_time_and_expiration_state",
)

#: Contract out §1's "carried alongside, each traced". Kept as a second tuple
#: rather than folded into the first because Done-means 2 is a statement about
#: THIRTEEN fields, and a test that counted twenty-three would not be testing it.
PLAN_CARRIED_FIELDS: tuple[str, ...] = (
    "organization_plan_version", "placement_decision_reference",
    "group_plan_reference", "intended_display_name", "filesystem_safe_name",
    "expected_destination_volume", "path_resolution_reference",
    "destination_root_anchor", "source_high_level_folder",
    "cross_folder_movement_permission",
)

#: Two carried fields are legitimately absent and are NOT subject to the
#: completeness check: a file that belongs to no group has no `group_plan_id`,
#: and a source sitting under none of the §1.1 folders the person named has no
#: high-level folder. Forcing either would make a real state unstorable.
_NULLABLE: frozenset[str] = frozenset(
    {"group_plan_reference", "source_high_level_folder"})

#: Not a string, so the emptiness test does not apply to it. §1.1's recorded
#: setting is True or False and never a blank.
_BOOLEAN: str = "cross_folder_movement_permission"


class PlanRefused(RuntimeError):
    """One of Contract out §5's ten classes, raised at plan construction."""

    def __init__(self, refusal_class: str, message: str, *,
                 detail: Mapping[str, object]) -> None:
        super().__init__(message)
        self.refusal_class = refusal_class
        self.detail = dict(detail)


class IncompletePlan(ValueError):
    """A plan missing one of §8.3's thirteen. Rejected, never executed."""


class NoSuchPlan(KeyError):
    """Asked to supersede a plan id that has no current record.

    NOT a refusal class: a refusal describes a plan that could not execute, and
    this is a caller naming something that does not exist. Dressing it as
    `node_not_in_frozen_tree` would put a message about the person's folder plan
    in front of what is a programming error.
    """


@dataclass(frozen=True)
class MovePlan:
    plan_id: str
    file_id: str
    expected_content_hash: str
    expected_source_path: str
    expected_source_volume: str
    expected_size_and_modification_state: str
    requested_destination_node: str
    resolved_destination_path: str
    collision_policy: str
    sensitivity_and_consent_state: str
    reason_and_evidence_summary: str
    required_review_policy: str
    creation_time_and_expiration_state: str
    organization_plan_version: str
    placement_decision_reference: str
    group_plan_reference: str | None
    intended_display_name: str
    filesystem_safe_name: str
    expected_destination_volume: str
    path_resolution_reference: str
    destination_root_anchor: str
    source_high_level_folder: str | None
    cross_folder_movement_permission: bool

    def __post_init__(self) -> None:
        for name in (*PLAN_PRECONDITION_FIELDS, *PLAN_CARRIED_FIELDS):
            if name in _NULLABLE or name == _BOOLEAN:
                continue
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise IncompletePlan(
                    f"{name} is empty. §8.3 requires the COMPLETE expected "
                    "precondition; a plan with a gap is rejected at "
                    "construction, not executed")
        check(self.collision_policy, COLLISION_BEHAVIOURS, name="collision_policy")
        if not isinstance(self.cross_folder_movement_permission, bool):
            raise IncompletePlan(
                f"{_BOOLEAN} is §1.1's recorded setting, True or False, never "
                "absent and never a word")


def _refuse_destination(node_id: str, nodes: Sequence[Node],
                        legal_destination_ids: frozenset[str]) -> Node:
    """The freeze guarantee, in P12's terms.

    P10 states it for P11 AND P12: the legal destination set is exactly
    `{node_id : plan_version = frozen version, accepts_placement = true}`, and
    §6.12 forbids any component inventing a destination after freeze.

    Absence from the tree and refusal by the tree are two different answers to
    the person -- *"that folder is not in your plan"* against *"that folder is
    not one you approved as a destination"* -- so they are two classes.

    `legal_destination_ids` is the caller's copy of the freeze record's set and
    `accepts_placement` is the flag on the node. Both are checked: a caller
    passing a wider set does not widen the tree, and a node whose flag was
    derived False is illegal even if the set says otherwise.
    """
    by_id = {item.node_id: item for item in nodes}
    node = by_id.get(node_id)
    if node is None:
        raise PlanRefused(
            NODE_NOT_IN_FROZEN_TREE,
            "no node with that id exists in this frozen tree",
            detail={"node_id": node_id})
    if node_id not in legal_destination_ids or not node.accepts_placement:
        raise PlanRefused(
            NODE_REFUSES_PLACEMENT,
            "that node is not a legal destination in this frozen tree",
            detail={"node_id": node_id,
                    "accepts_placement": node.accepts_placement,
                    "in_legal_destination_ids": node_id in legal_destination_ids})
    if node.node_role == RESIDUAL_ROLE and node.disposition in (
            REVIEW_ONLY, LEAVE_IN_PLACE_DISPOSITION):
        # §7.4. `accepts_placement` is deliberately True for all three
        # dispositions -- the disposition governs what happens WHEN a node is
        # chosen, not whether it can be -- so the write-target refusal lives
        # here, where the write is being planned, and not in P10's derivation.
        raise PlanRefused(
            NODE_REFUSES_PLACEMENT,
            "that residual node is a review queue or a leave-in-place branch, "
            "not a write target (§7.4)",
            detail={"node_id": node_id, "disposition": node.disposition})
    return node


def _source_high_level_folder(source_path: Path,
                              high_level_folders: Mapping[str, Path]) -> str | None:
    """Which §1.1 folder the source lives under. Longest match wins."""
    best: str | None = None
    best_depth = -1
    for name, folder in high_level_folders.items():
        try:
            source_path.relative_to(folder)
        except ValueError:
            continue
        depth = len(folder.parts)
        if depth > best_depth:
            best, best_depth = name, depth
    return best


def build_plan(conn: sqlite3.Connection, decision: PlacementDecision, *,
               nodes: Sequence[Node],
               legal_destination_ids: frozenset[str],
               cross_folder_moves: bool,
               constraints: FilesystemConstraints,
               high_level_folders: Mapping[str, Path],
               volume_of: Callable[[Path], str],
               protected_handling_classes: frozenset[str],
               protected_label_classes: Mapping[str, str],
               collision_policy: str,
               expiration_state: str,
               now: Callable[[], str],
               mint_id: Callable[[], str],
               ) -> tuple[MovePlan, PathResolution] | None:
    """One plan for one `place` decision, or `None` for any other outcome.

    `None` is not a refusal. P11's other six outcomes produce no plan at all:
    `abstain` is a SUCCESSFUL outcome (§6.10), `leave_in_place` and `mark_state`
    are decisions not to move (§7.7), and recording one of them as a P12 refusal
    would make the apply run's refused count describe decisions that were never
    asked to move.

    `protected_label_classes` is passed straight through to `resolve_destination`,
    where its own guard states why it exists and why `Node.handling_class` is not
    it (`94` F1). It is a required keyword here for the same reason it is one
    there: a caller that forgot it would compose a path through a name it had
    never asked about.

    `collision_policy` and `expiration_state` are injected with NO default.
    §8.3 names the collision field and its four behaviours but never says which
    a person has chosen, and it names an expiration state and states no expiry
    rule anywhere -- a default here would be P12 deciding when someone's pending
    move goes stale by the clock. Both are the composition root's (A7).

    `NameUnresolvable` propagates. Contract out §5 has ten refusal classes and
    none of them means *"no safe name exists"*; mapping it onto
    `node_path_collision` would tell the person something untrue and minting an
    eleventh class would be P12 authoring the SPEC. Flagged, not closed.
    """
    check(collision_policy, COLLISION_BEHAVIOURS, name="collision_policy")
    if decision.outcome != PLACE or decision.destination is None:
        return None

    _refuse_destination(decision.destination.node_id, nodes,
                        legal_destination_ids)

    row = get_file(conn, decision.subject.file_id)
    if row is None:
        # There is no source to move. `source_or_destination_unavailable` is the
        # truest of the ten: the other nine describe the destination, the
        # policy or the plan, and this is the source not being there at all.
        raise PlanRefused(
            SOURCE_OR_DESTINATION_UNAVAILABLE,
            "the decision names a file P1 has no record of, so there is no "
            "source to move",
            detail={"file_id": decision.subject.file_id})
    source_path = Path(row["current_path"])

    try:
        resolution = resolve_destination(
            plan_version=decision.plan_version,
            node_id=decision.destination.node_id, nodes=nodes,
            source_path=source_path, high_level_folders=high_level_folders,
            constraints=constraints, cross_folder_moves=cross_folder_moves,
            volume_of=volume_of, mint_resolution_id=mint_id,
            protected_handling_classes=protected_handling_classes,
            protected_label_classes=protected_label_classes)
    except ResolutionRefused as refused:
        raise PlanRefused(refused.refusal_class, str(refused),
                          detail=refused.detail) from refused

    name = resolve_name(
        row["filename"], constraints=constraints,
        directory_byte_length=len(
            resolution.resolved_destination_directory.encode("utf-8")),
        has_extension=True)

    plan = MovePlan(
        plan_id=mint_id(),
        file_id=decision.subject.file_id,
        expected_content_hash=decision.subject.content_hash,
        expected_source_path=str(source_path),
        # NOT `row["volume_id"]`. P1's OQ9 is open and `volume_id_for` prefixes
        # its answer with a per-process observation session precisely so that
        # two values recorded in different sessions can never accidentally
        # compare equal. The scan that wrote that row ran in an earlier process,
        # so comparing it with a volume computed now would report every move as
        # cross-volume. `volume_of` is the injected oracle that also produced
        # `expected_destination_volume`, so the two ends are comparable because
        # they come from one authority.
        expected_source_volume=volume_of(source_path),
        # §1.2's stat semantics, the ones the scan cache uses: size and
        # modification time, with change in EITHER direction treated as change.
        expected_size_and_modification_state=canonical_json({
            "observed_size": row["observed_size"],
            "observed_timestamps": row["observed_timestamps"]}),
        requested_destination_node=decision.destination.node_id,
        resolved_destination_path=str(
            Path(resolution.resolved_destination_directory)
            / name.filesystem_safe_name),
        collision_policy=collision_policy,
        sensitivity_and_consent_state=canonical_json({
            "handling_class": decision.privacy.handling_class,
            "protected": decision.privacy.protected,
            "model_eligibility": decision.privacy.model_eligibility,
            "consent_audit_ref": decision.privacy.consent_audit_ref}),
        reason_and_evidence_summary=canonical_json({
            "explanation": decision.explanation,
            "evidence_type": decision.evidence_type,
            "confidence_class": decision.confidence_class,
            "matching_facts": [asdict(fact) for fact in decision.matching_facts],
            "group_support": (asdict(decision.group_support)
                              if decision.group_support is not None else None),
            "decision_depth": asdict(decision.decision_depth)}),
        required_review_policy=decision.review_policy,
        creation_time_and_expiration_state=canonical_json({
            "created_at": now(), "expiration_state": expiration_state}),
        organization_plan_version=decision.plan_version,
        placement_decision_reference=decision.decision_id,
        group_plan_reference=decision.group_plan_id,
        intended_display_name=name.intended_display_name,
        filesystem_safe_name=name.filesystem_safe_name,
        expected_destination_volume=resolution.target_volume,
        path_resolution_reference=resolution.resolution_id,
        destination_root_anchor=resolution.root_anchor,
        source_high_level_folder=_source_high_level_folder(
            source_path, high_level_folders),
        cross_folder_movement_permission=cross_folder_moves,
    )
    return plan, resolution


def record_plan(conn: sqlite3.Connection, plan: MovePlan,
                resolution: PathResolution, *, created_at: str,
                component_version: str) -> str:
    """Append the plan, its resolution, and one `planned move` event."""
    record_id = f"{plan.plan_id}:0"
    record_resolution(conn, resolution, created_at=created_at,
                      record_id=f"{resolution.resolution_id}:0")
    conn.execute(
        "INSERT INTO move_plans (record_id, plan_id, plan_version, decision_ref, "
        "group_plan_ref, file_id, node_id, required_review_policy, created_at, "
        "payload) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (record_id, plan.plan_id, plan.organization_plan_version,
         plan.placement_decision_reference, plan.group_plan_reference,
         plan.file_id, plan.requested_destination_node,
         plan.required_review_policy, created_at, canonical_json(asdict(plan))))
    append_event(
        conn, event_type=PLANNED_MOVE, file_id=plan.file_id,
        content_hash=plan.expected_content_hash,
        old_path=plan.expected_source_path,
        new_path=plan.resolved_destination_path, subsystem=SUBSYSTEM,
        component_version=component_version, observed_at=created_at,
        explanation=canonical_json({
            "plan_id": plan.plan_id,
            "decision_ref": plan.placement_decision_reference,
            "plan_version": plan.organization_plan_version,
            "required_review_policy": plan.required_review_policy,
            "path_resolution_reference": plan.path_resolution_reference}))
    return record_id


def _from_payload(payload: str) -> MovePlan:
    return MovePlan(**json.loads(payload))


def current_plan(conn: sqlite3.Connection, plan_id: str) -> MovePlan | None:
    row = conn.execute(
        "SELECT payload FROM move_plans WHERE plan_id = ? "
        "AND superseded_by IS NULL", (plan_id,)).fetchone()
    return None if row is None else _from_payload(row[0])


def plans_in_group(conn: sqlite3.Connection,
                   group_plan_ref: str) -> tuple[MovePlan, ...]:
    """Every current member plan of one §6.8 group plan, so the set can be
    presented as one coherent group plan rather than several unrelated moves."""
    rows = conn.execute(
        "SELECT payload FROM move_plans WHERE group_plan_ref = ? "
        "AND superseded_by IS NULL ORDER BY created_at, plan_id",
        (group_plan_ref,)).fetchall()
    return tuple(_from_payload(row[0]) for row in rows)


def supersede_plan(conn: sqlite3.Connection, old_plan_id: str,
                   new_plan: MovePlan, resolution: PathResolution, *,
                   reason: str, created_at: str, component_version: str) -> str:
    """A stale plan is never edited in place (§8.2).

    A refreshed plan is a NEW record that supersedes it, and `reason` carries
    the trigger so the retained record can say what made it stale rather than
    only that something did.
    """
    old = conn.execute(
        "SELECT record_id FROM move_plans WHERE plan_id = ? "
        "AND superseded_by IS NULL", (old_plan_id,)).fetchone()
    if old is None:
        raise NoSuchPlan(
            f"no current move plan with id {old_plan_id!r} to supersede")
    record_id = record_plan(conn, new_plan, resolution, created_at=created_at,
                            component_version=component_version)
    mark_superseded(conn, "move_plans", old_id=old["record_id"],
                    new_id=record_id, reason=reason)
    return record_id
