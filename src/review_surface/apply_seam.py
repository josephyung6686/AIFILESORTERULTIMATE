"""§8.3's three moments: the plan shown for review, the stale plan, the undo conflict.

**What this task actually found.** `74` §6 G1 reads *"re-point P13's `apply_seam`
at the real P12 records and delete `tests/p13/p12_fixtures.py`"*. There was no
apply seam and there has never been a `p12_fixtures.py` -- `git log --all` over
that path is empty. What `src/review_surface/` carried was `SURFACE_APPLY` and
`SURFACE_UNDO_CONFLICT` in the vocabulary, both routed to P12 in `routing.py`,
and nothing anywhere that could construct either. Two live surfaces reachable by
nothing is the defect this project keeps paying for, and it was sitting in the
middle of the seam. So this module builds the seam rather than re-pointing it.

**Three items, and each one is defined by a control it must not have.**

* **The apply review item** carries §8.3's thirteen precondition fields as P12
  wrote them, plus the intended display name beside the filesystem-safe name so a
  person can see that the two differ and why. It resolves nothing: the two paths
  on it are P12's own strings, and `74` §4.3 names the apply and undo-conflict
  items as exactly where §8.3 requires them.
* **The stale plan item** names WHICH of §8.3's five triggers fired and shows the
  expected value beside the observed one. An item showing only one of them says
  *"something changed"*, which is a shrug; showing both says *"this changed"*,
  which a person can act on. **It offers a refresh and nothing that applies it.**
  §8.3: refresh the plan *"rather than applying an old decision to a changed
  file"* -- so there is no control here that runs it anyway, and
  `controls_that_would_apply_a_stale_plan` exists so that is a checked property
  rather than a promise.
* **The undo conflict item** carries the design's own sentence with both paths
  and both hashes, for manual resolution. **It offers no action at all.** §8.3
  says undo must not force a rollback; a "force" control would be the product
  overruling a person's file with a button, and
  `controls_offered_on_an_undo_conflict` is what makes its absence checkable.

**Every sentence a person reads comes from P12.** `sentence` is injected on the
stale item and read off the undo verdict's own detail, because `66` §10's table
of distinct refusal messages is P12's one home for them. P13 writing a sixth
would put a second spelling of *"this file changed after the preview"* in the
product, and the whole property of that table is that no two of its members read
alike.
"""
from __future__ import annotations

import ast
import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol

from review_surface.labels import label_chain_for_version
from review_surface.vocabulary import (
    ACTION_ACCEPT,
    ACTION_ACCEPT_BULK,
    ACTION_APPROVE_FOR_APPLY,
    ACTION_REFRESH_PLAN,
    SURFACE_APPLY,
    SURFACE_UNDO_CONFLICT,
)

#: The actions that would RUN a plan. A stale plan may offer none of them.
#: `approve_for_apply` is the one that matters most and is the easiest to forget:
#: it is the action that reaches P12's gate.
APPLYING_ACTIONS: tuple[str, ...] = (
    ACTION_ACCEPT, ACTION_ACCEPT_BULK, ACTION_APPROVE_FOR_APPLY)


class MovePlanShape(Protocol):
    """What the apply item needs of P12's move plan. Structural, never imported.

    P13 may not import a mutation surface (Done-means 22), and stating the shape
    here also states the contract: a field P12 renames breaks the item loudly
    instead of leaving it silently blank.
    """

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
    intended_display_name: str
    filesystem_safe_name: str


class PreconditionVerdictShape(Protocol):
    """What the stale item needs of P12's precondition verdict."""

    plan_id: str
    trigger: str | None
    observed_source_path: str | None
    observed_size_and_modification_state: str | None
    hash_result: str | None


class UndoVerdictShape(Protocol):
    """What the conflict item needs of P12's undo verdict."""

    entry_id: str
    verdict: str
    destination_path: str
    original_source_path: str
    expected_hash: str
    observed_destination_hash: str | None
    detail: Mapping[str, object]


class NotAStalePlan(ValueError):
    """A fresh verdict offered as a stale-plan item. There is nothing to refresh."""


class NotAnUndoConflict(ValueError):
    """A verdict that is not a conflict offered as a conflict item."""


class SentenceRequired(ValueError):
    """No sentence for the person. `66` §10's messages are P12's, not P13's."""


@dataclass(frozen=True)
class ApplyReviewItem:
    """§8.3's plan, shown where policy requires review. It adds no field of its own.

    There is no `force`, no `apply_anyway` and no `override`. The item is what a
    person looks at; the record that lets the move run is `review_approval`, and
    it is collected by `review_surface.approvals` under its own §8.2 event.
    """

    surface: str
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
    plan_version: str
    placement_decision_reference: str
    #: Beside each other on purpose. §8.3 records the name a person meant
    #: separately from the name a filesystem will accept, and a surface showing
    #: only the second would present a normalization as the person's own choice.
    intended_display_name: str
    filesystem_safe_name: str
    #: B3's chain, read out of P10's store. The resolved path above is §8.3's
    #: own field; this is how the destination is NAMED to a person.
    destination_label_chain: tuple[str, ...]


@dataclass(frozen=True)
class StalePlanItem:
    """§8.3's stale plan: which trigger, expected against observed, and a refresh."""

    surface: str
    plan_id: str
    trigger: str
    sentence: str
    expected_content_hash: str
    observed_hash_result: str | None
    expected_source_path: str
    observed_source_path: str | None
    expected_size_and_modification_state: str
    observed_size_and_modification_state: str | None
    offered_actions: tuple[str, ...]


@dataclass(frozen=True)
class UndoConflictItem:
    """§8.3's undo conflict: the sentence, both paths, both hashes, no control.

    `observed_content_hash` is `None` when there was nothing hashable at the
    destination, and `None` there is a finding rather than an unknown: it says
    the file is gone. P12 draws that distinction on its own verdict and P13
    carries it rather than flattening it into a blank.
    """

    surface: str
    entry_id: str
    verdict: str
    sentence: str
    original_source_path: str
    destination_path: str
    expected_content_hash: str
    observed_content_hash: str | None
    occupant_at_source_hash: str | None
    offered_actions: tuple[str, ...]


def apply_review_item(conn: sqlite3.Connection,
                      plan: MovePlanShape) -> ApplyReviewItem:
    """Project one move plan into what §8.3 requires be shown before it runs."""
    return ApplyReviewItem(
        surface=SURFACE_APPLY,
        plan_id=plan.plan_id,
        file_id=plan.file_id,
        expected_content_hash=plan.expected_content_hash,
        expected_source_path=plan.expected_source_path,
        expected_source_volume=plan.expected_source_volume,
        expected_size_and_modification_state=(
            plan.expected_size_and_modification_state),
        requested_destination_node=plan.requested_destination_node,
        resolved_destination_path=plan.resolved_destination_path,
        collision_policy=plan.collision_policy,
        sensitivity_and_consent_state=plan.sensitivity_and_consent_state,
        reason_and_evidence_summary=plan.reason_and_evidence_summary,
        required_review_policy=plan.required_review_policy,
        creation_time_and_expiration_state=(
            plan.creation_time_and_expiration_state),
        plan_version=plan.organization_plan_version,
        placement_decision_reference=plan.placement_decision_reference,
        intended_display_name=plan.intended_display_name,
        filesystem_safe_name=plan.filesystem_safe_name,
        destination_label_chain=label_chain_for_version(
            conn, plan_version=plan.organization_plan_version,
            node_id=plan.requested_destination_node))


def stale_plan_item(verdict: PreconditionVerdictShape, plan: MovePlanShape, *,
                    sentence: str) -> StalePlanItem:
    """§8.3's stale moment. `sentence` is P12's own and has no default here.

    A fresh verdict raises. §8.3's refresh exists for a plan that WENT stale, and
    an item built from a fresh one would put "this changed" in front of a person
    about a file nothing touched.
    """
    if verdict.trigger is None:
        raise NotAStalePlan(
            f"the precondition verdict for {verdict.plan_id!r} named no "
            "staleness trigger, so there is nothing to refresh and nothing to "
            "tell the person")
    if not sentence:
        raise SentenceRequired(
            "`66` §10's distinct refusal messages are P12's one home for them. "
            "P13 renders the sentence P12 wrote for this trigger and writes no "
            "sentence of its own")
    return StalePlanItem(
        surface=SURFACE_APPLY,
        plan_id=verdict.plan_id,
        trigger=verdict.trigger,
        sentence=sentence,
        expected_content_hash=plan.expected_content_hash,
        observed_hash_result=verdict.hash_result,
        expected_source_path=plan.expected_source_path,
        observed_source_path=verdict.observed_source_path,
        expected_size_and_modification_state=(
            plan.expected_size_and_modification_state),
        observed_size_and_modification_state=(
            verdict.observed_size_and_modification_state),
        # One action, and it is the one §8.3 names. Nothing here runs the plan.
        offered_actions=(ACTION_REFRESH_PLAN,))


def undo_conflict_item(verdict: UndoVerdictShape) -> UndoConflictItem:
    """§8.3's conflict. The sentence is read off P12's verdict, never composed.

    `offered_actions` is empty and is a field rather than an omission, so
    `controls_offered_on_an_undo_conflict` has something to look at. An absence
    nothing can inspect is indistinguishable from an absence nobody checked.
    """
    sentence = verdict.detail.get("message")
    if not isinstance(sentence, str) or not sentence:
        raise SentenceRequired(
            f"the undo verdict for {verdict.entry_id!r} carries no message. "
            "§8.3's own sentence is P12's, and P13 has no path that writes one "
            "when P12 did not")
    return UndoConflictItem(
        surface=SURFACE_UNDO_CONFLICT,
        entry_id=verdict.entry_id,
        verdict=verdict.verdict,
        sentence=sentence,
        original_source_path=verdict.original_source_path,
        destination_path=verdict.destination_path,
        expected_content_hash=verdict.expected_hash,
        observed_content_hash=verdict.observed_destination_hash,
        occupant_at_source_hash=getattr(
            verdict, "occupant_at_source_hash", None),
        offered_actions=())


def controls_that_would_apply_a_stale_plan(
        items: Sequence[object]) -> list[str]:
    """Every item offering a control that would run a plan §8.3 called stale.

    Takes the items as an argument so it can be pointed at a sabotaged one. A
    guard only ever run over items that cannot carry the thing it looks for
    passes exactly as well when it cannot find anything at all.
    """
    return [f"{getattr(item, 'plan_id', item)}.{action}"
            for item in items
            for action in getattr(item, "offered_actions", ())
            if action in APPLYING_ACTIONS]


def controls_offered_on_an_undo_conflict(
        items: Sequence[object]) -> list[str]:
    """Every control offered on a conflict. §8.3 permits none, forcing least of all.

    ANY action is reported, not only a "force" one: P13's action vocabulary has
    no force member, so a guard looking for one would look for something that
    cannot exist and would never fire. What §8.3 forbids is the product acting on
    a conflict at all; the person resolves it themselves.
    """
    return [f"{getattr(item, 'entry_id', getattr(item, 'plan_id', item))}.{action}"
            for item in items
            for action in getattr(item, "offered_actions", ())]


def fixture_imports(sources: Sequence[tuple[str, str]]) -> list[str]:
    """Every import of a fixture module in `sources`. Parsed, never grepped.

    `74` §6 G1's negative twin. The task said to delete `tests/p13/p12_fixtures.py`;
    it has never existed, so the property worth holding is not that it was removed
    but that nothing like it can arrive: `src/review_surface/` renders what other
    parts really publish, and a package that imported a tests-only stand-in would
    be rendering a shape nothing produces.

    Parsed rather than searched because a text search matches comments and
    docstrings, and this docstring names three fixture modules. Sources are passed
    in rather than read from a fixed path, so the guard can be driven against a
    module that genuinely imports one.
    """
    offenders: list[str] = []
    for name, source in sources:
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.ImportFrom) and node.module:
                if "fixtures" in node.module or node.module.startswith("tests"):
                    offenders.append(f"{name} imports {node.module}")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if ("fixtures" in alias.name
                            or alias.name.startswith("tests")):
                        offenders.append(f"{name} imports {alias.name}")
    return offenders
