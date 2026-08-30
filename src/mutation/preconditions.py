"""§8.3's recheck, evaluated twice: at V1 (prepare) and at V2 (immediately before).

`00`:171: *"Immediately before applying an action, the system should recheck the
source file. If its content hash differs, if the source path has changed, if the
destination changed, if the file disappeared, or if permission is no longer
available, the action should be marked stale and removed from automatic
execution. The product must ask the user to refresh the plan rather than applying
an old decision to a changed file."*

Those five conditions are the five triggers, and the refresh prompt is `66` §10's
distinct sentence for whichever one fired.

**Evaluating is not mutating.** Nothing here writes to the filesystem, creates a
directory, or touches the destination beyond hashing whatever already sits at it.

**The trigger order is fixed, and it is the whole substance of this module.**
`source_path_changed` -> `source_vanished` -> `permission_lost` ->
`content_hash_differs` -> `destination_changed`. P1's `verify_content` hashes
`files.current_path` and turns an `OSError` into `"mismatch"`
(`database_agent/verify.py:45-49`), so asking for the hash before asking whether
the file is still there, still at that path, and still readable would collapse
three distinct triggers -- three distinct things to tell a person, with three
distinct things they can do about it -- into one wrong one. A file can satisfy
several at once, and a verdict that varied with evaluation order would make the
retained stale record untrustworthy.
"""
from __future__ import annotations

import os
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from database_agent.events import append_event
from database_agent.files_table import get_file
from database_agent.identity import hash_file
from database_agent.verify import VerificationPoint, verify_content
from evidence_shape.canonical import canonical_json

from mutation.plan import MovePlan
from mutation.vocabulary import (
    CHECKPOINTS, CONTENT_HASH_DIFFERS, DESTINATION_CHANGED,
    EXTERNAL_MODIFICATION_DETECTION, FRESH, PERMISSION_LOST, PRE_APPLY, PREPARE,
    SOURCE_PATH_CHANGED, SOURCE_VANISHED, STALENESS_TRIGGERS, SUBSYSTEM, check,
    decline_message,
)

#: Contract out §2's two evaluation points are §8.2's first two verification
#: points. One mapping, so a checkpoint can never be recorded under the other's
#: name.
_POINT = {PREPARE: VerificationPoint.V1, PRE_APPLY: VerificationPoint.V2}


@dataclass(frozen=True)
class PreconditionVerdict:
    plan_id: str
    checkpoint: str
    #: `fresh`, or `stale:<trigger>`.
    verdict: str
    trigger: str | None
    observed_source_path: str | None
    observed_size_and_modification_state: str | None
    destination_occupant_hash: str | None
    #: P1's answer, `match` or `mismatch`, or `None` when a structural trigger
    #: fired first and the hash was never asked for. `None` is not "unknown":
    #: it says the question was not put, which is what the ordering guarantees.
    hash_result: str | None
    checkpoint_hash: str | None

    def __post_init__(self) -> None:
        check(self.checkpoint, CHECKPOINTS, name="checkpoint")
        if self.trigger is not None:
            check(self.trigger, STALENESS_TRIGGERS, name="staleness trigger")

    @property
    def is_fresh(self) -> bool:
        return self.verdict == FRESH


def _occupant_hash(path: Path, *, materialized: bool) -> str | None:
    """The hash of whatever currently sits at the destination path, or `None`.

    A directory, a broken link or an unreadable entry is an occupant P12 cannot
    hash; `None` says so and the collision and special-object checks decide what
    it means. A symlink is never followed here -- only what is at the path.
    """
    if path.is_symlink() or not path.is_file():
        return None
    try:
        return hash_file(path, materialized=materialized)
    except OSError:
        return None


def _nearest_existing(directory: Path) -> Path:
    """The deepest ancestor of `directory` that exists.

    The destination directory of a fresh plan is designed structure and not yet
    a folder on disk (§5.1, §5.12), so the writability question has to be asked
    of the deepest ancestor that is really there.
    """
    current = directory
    while not current.exists() and current != current.parent:
        current = current.parent
    return current


def evaluate_preconditions(conn: sqlite3.Connection, plan: MovePlan, *,
                           checkpoint: str,
                           legal_destination_ids: frozenset[str],
                           occupant_at_prepare: str | None,
                           component_version: str,
                           materialized: bool,
                           now: Callable[[], str]) -> PreconditionVerdict:
    """`fresh`, or `stale:<trigger>` with no mutation and one recorded observation.

    `occupant_at_prepare` comes from the V1 verdict rather than off the plan,
    which carries no such field: an occupied destination is not by itself
    `destination_changed`, because §8.3 gives collisions their own policy and
    their own four behaviours, and if occupancy alone were a staleness trigger
    that policy would be unreachable. What the trigger means at the recheck is
    that occupancy CHANGED between the two checkpoints. Its other half is §8.8's
    *"require renewed review because their previous destination no longer
    exists"* -- the node is gone from the current version's legal set.
    """
    check(checkpoint, CHECKPOINTS, name="checkpoint")
    row = get_file(conn, plan.file_id)
    observed_path = None if row is None else row["current_path"]
    observed_state = None if row is None else canonical_json({
        "observed_size": row["observed_size"],
        "observed_timestamps": row["observed_timestamps"]})
    expected = Path(plan.expected_source_path)
    destination = Path(plan.resolved_destination_path)
    occupant = _occupant_hash(destination, materialized=materialized)

    trigger: str | None = None
    hash_result: str | None = None

    if row is not None and observed_path != plan.expected_source_path:
        # P1 knows the file by another path now. That is a move somebody else
        # made, and it is a different sentence from "it changed".
        trigger = SOURCE_PATH_CHANGED
    elif row is None or not expected.exists():
        trigger = SOURCE_VANISHED
    elif not os.access(expected, os.R_OK) or not os.access(
            _nearest_existing(destination.parent), os.W_OK):
        trigger = PERMISSION_LOST
    else:
        hash_result = verify_content(
            conn, plan.file_id, plan.expected_content_hash,
            point=_POINT[checkpoint], author=SUBSYSTEM,
            component_version=component_version, materialized=materialized)
        if hash_result != "match":
            trigger = CONTENT_HASH_DIFFERS
        elif plan.requested_destination_node not in legal_destination_ids:
            trigger = DESTINATION_CHANGED
        elif checkpoint == PRE_APPLY and occupant != occupant_at_prepare:
            trigger = DESTINATION_CHANGED

    verdict = PreconditionVerdict(
        plan_id=plan.plan_id, checkpoint=checkpoint,
        verdict=FRESH if trigger is None else f"stale:{trigger}",
        trigger=trigger, observed_source_path=observed_path,
        observed_size_and_modification_state=observed_state,
        destination_occupant_hash=occupant, hash_result=hash_result,
        checkpoint_hash=(plan.expected_content_hash if hash_result == "match"
                         else None))

    if trigger is not None:
        # The observation is recorded even though no mutation occurs. P12 claims
        # authorship of its OWN detections only -- P3 detects the same condition
        # at §1.2's re-scan and is the other author of this type.
        append_event(
            conn, event_type=EXTERNAL_MODIFICATION_DETECTION,
            file_id=plan.file_id, content_hash=plan.expected_content_hash,
            old_path=plan.expected_source_path,
            new_path=plan.resolved_destination_path, subsystem=SUBSYSTEM,
            component_version=component_version, observed_at=now(),
            explanation=canonical_json({
                "plan_id": plan.plan_id, "checkpoint": checkpoint,
                "trigger": trigger, "verdict": verdict.verdict,
                "observed_source_path": observed_path,
                "observed_size_and_modification_state": observed_state,
                "destination_occupant_hash": occupant,
                "detected_by": SUBSYSTEM,
                "message": decline_message(verdict.verdict)}))
    return verdict


def refresh_prompt(verdict: PreconditionVerdict) -> str:
    """`66` §10's sentence for the trigger that fired.

    A fresh plan has no prompt, and raises rather than returning a reassuring
    sentence: §8.3 asks the person to refresh a plan that went stale, and a
    sixth message in a table whose whole property is that its members are
    distinct would be a message for something that did not happen.
    """
    if verdict.is_fresh:
        raise ValueError(
            "a fresh plan is not asking to be refreshed; there is nothing to "
            "tell the person")
    return decline_message(verdict.verdict)
