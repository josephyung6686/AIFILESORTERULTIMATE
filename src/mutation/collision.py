"""§8.3's collision policy. *"The engine should never silently overwrite an
existing file."* (`00`:172)

The four behaviours here are exactly the four user-approved ones the design
lists, and **none of them writes**. Each chooses an outcome and, where a file is
to be written, a destination path that has been checked free. The executor is the
only writer, and it never receives an occupied path -- which is what makes *"no
path exists through the code that overwrites an existing file"* a property of the
code's shape rather than of anyone's care at the call site.

*"The collision rule must distinguish exact duplicates from different files that
happen to share a filename. A content-hash match supports deduplication review; a
filename match alone does not."* That sentence is why
`MERGE_ONLY_IF_HASHES_IDENTICAL` RAISES on a `name_only` collision instead of
quietly falling back to a suffix. The fallback looks harmless and is not: the
merge outcome is *"merged, no write"*, so two unrelated documents sharing a name
would end with the incoming one never arriving and nobody told.

**`74` §8 Q3 is the owner's and is open.** §8.3 requires *"a deterministic
suffix"* and names no form, and the form is user-visible in every filename it
touches. `suffix_for` and `max_suffix_attempts` are therefore injected with no
default and no module-level constant stands in for either -- a constant here
would be the answer, and the answer was not P12's to give.
"""
from __future__ import annotations

import os
import sqlite3
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path

from database_agent.events import append_event
from database_agent.identity import hash_file
from evidence_shape.canonical import canonical_json

from mutation.constraints import FilesystemConstraints
from mutation.names import collation_key, resolve_name
from mutation.plan import MovePlan
from mutation.vocabulary import (
    COLLISION_BEHAVIOURS, COLLISION_KINDS, COLLISION_OUTCOMES,
    CONTENT_HASH_MATCH, FILENAME_COLLISION_RESOLUTION, HALTED_AWAITING_USER,
    MERGE_ONLY_IF_HASHES_IDENTICAL, MERGED_NO_WRITE, NAME_ONLY,
    OLDER_SENT_TO_VERSION_FAMILY_REVIEW, PRESERVE_BOTH_DETERMINISTIC_SUFFIX,
    RETAIN_NEWER_OLDER_TO_VERSION_FAMILY_REVIEW, STOP_AND_ASK, SUBSYSTEM,
    SUFFIXED_PATH, check,
)


class MergeRefused(ValueError):
    """`merge_only_if_hashes_identical` selected for two different files."""


class SuffixExhausted(RuntimeError):
    """No free suffixed name inside the caller's attempt bound.

    Stopping is the point. Going on past the bound would mean choosing a name
    by a rule nobody stated, and §8.3 asks for a name a person can predict.
    """


@dataclass(frozen=True)
class CollisionResolution:
    plan_id: str
    colliding_destination_path: str
    collision_kind: str
    incumbent_content_hash: str | None
    incoming_content_hash: str
    behaviour_applied: str
    outcome: str
    #: Where the incoming file may be written, or `None` when this behaviour
    #: writes nothing. Whatever is here has been checked free.
    final_destination_path: str | None
    version_family_review_ref: str | None

    def __post_init__(self) -> None:
        check(self.collision_kind, COLLISION_KINDS, name="collision_kind")
        check(self.behaviour_applied, COLLISION_BEHAVIOURS,
              name="collision behaviour")
        check(self.outcome, COLLISION_OUTCOMES, name="collision outcome")


def find_collision(directory: Path, safe_name: str, *,
                   constraints: FilesystemConstraints) -> Path | None:
    """The entry already in `directory` that `safe_name` would collide with.

    Compares `collation_key`s over the real listing rather than calling
    `Path.exists()`, because `exists()` answers the volume's question and not
    §8.3's: on a case-SENSITIVE volume it returns False for an NFC/NFD pair a
    person cannot tell apart, and it cannot say WHICH entry collided, which the
    collision record needs.

    Only names are read here, never targets, so a symlinked entry is reported
    as a collision by name and the special-object check decides what a symlink
    means.
    """
    if not directory.is_dir():
        return None
    wanted = collation_key(safe_name, constraints=constraints)
    with os.scandir(directory) as entries:
        for entry in entries:
            if collation_key(entry.name, constraints=constraints) == wanted:
                return directory / entry.name
    return None


def _split_extension(safe_name: str) -> tuple[str, str]:
    head, dot, tail = safe_name.rpartition(".")
    if dot and head:
        return head, f".{tail}"
    return safe_name, ""


def _free_suffixed_path(incumbent: Path, safe_name: str, *,
                        constraints: FilesystemConstraints,
                        suffix_for: Callable[[str, int], str],
                        max_suffix_attempts: int) -> Path:
    """The first suffixed name no entry in the directory collides with.

    The suffixed candidate is put back through `resolve_name`, because the
    suffix lengthens the component and a name that fit the volume's budget
    before may not after.
    """
    directory = incumbent.parent
    stem, extension = _split_extension(safe_name)
    for attempt in range(1, max_suffix_attempts + 1):
        candidate = resolve_name(
            f"{suffix_for(stem, attempt)}{extension}", constraints=constraints,
            directory_byte_length=len(str(directory).encode("utf-8")),
            has_extension=bool(extension)).filesystem_safe_name
        if find_collision(directory, candidate, constraints=constraints) is None:
            return directory / candidate
    raise SuffixExhausted(
        f"no free name after {max_suffix_attempts} attempts; the product stops "
        "rather than choosing a name nobody can predict")


def resolve_collision(plan: MovePlan, *, incumbent: Path, incoming_path: Path,
                      incoming_hash: str, behaviour: str,
                      constraints: FilesystemConstraints,
                      suffix_for: Callable[[str, int], str],
                      max_suffix_attempts: int,
                      materialized: bool,
                      mint_id: Callable[[], str]) -> CollisionResolution:
    """One of §8.3's four behaviours, applied. Writes nothing, ever."""
    check(behaviour, COLLISION_BEHAVIOURS, name="collision behaviour")
    try:
        incumbent_hash: str | None = hash_file(incumbent,
                                               materialized=materialized)
    except OSError:
        # An incumbent whose bytes cannot be read is not a proven duplicate,
        # and `None` never equals `incoming_hash`, so it falls to `name_only` --
        # which is the declining reading and the one that cannot merge.
        incumbent_hash = None
    kind = CONTENT_HASH_MATCH if incumbent_hash == incoming_hash else NAME_ONLY

    final: str | None = None
    review_ref: str | None = None

    if behaviour == MERGE_ONLY_IF_HASHES_IDENTICAL:
        if kind != CONTENT_HASH_MATCH:
            raise MergeRefused(
                f"merge_only_if_hashes_identical may not be applied to a "
                f"{NAME_ONLY} collision: a filename match alone does not "
                "support deduplication (`00`:172)")
        outcome = MERGED_NO_WRITE
    elif behaviour == PRESERVE_BOTH_DETERMINISTIC_SUFFIX:
        outcome = SUFFIXED_PATH
        final = str(_free_suffixed_path(
            incumbent, plan.filesystem_safe_name, constraints=constraints,
            suffix_for=suffix_for, max_suffix_attempts=max_suffix_attempts))
    elif behaviour == RETAIN_NEWER_OLDER_TO_VERSION_FAMILY_REVIEW:
        outcome = OLDER_SENT_TO_VERSION_FAMILY_REVIEW
        review_ref = mint_id()
        # Whichever file is OLDER goes to review; NEITHER is removed, because
        # §7.11 forbids deleting a user file and the incumbent is one. When the
        # incoming file is the newer one it is written beside the incumbent
        # under a deterministic suffix; when the incumbent is the newer one,
        # nothing is written. Both files survive in both branches, which is
        # what "never silently overwrite" requires.
        if incoming_path.stat().st_mtime > incumbent.stat().st_mtime:
            final = str(_free_suffixed_path(
                incumbent, plan.filesystem_safe_name, constraints=constraints,
                suffix_for=suffix_for,
                max_suffix_attempts=max_suffix_attempts))
    else:
        check(behaviour, (STOP_AND_ASK,), name="collision behaviour")
        outcome = HALTED_AWAITING_USER

    return CollisionResolution(
        plan_id=plan.plan_id, colliding_destination_path=str(incumbent),
        collision_kind=kind, incumbent_content_hash=incumbent_hash,
        incoming_content_hash=incoming_hash, behaviour_applied=behaviour,
        outcome=outcome, final_destination_path=final,
        version_family_review_ref=review_ref)


def record_collision(conn: sqlite3.Connection, resolution: CollisionResolution,
                     *, file_id: str, created_at: str, component_version: str,
                     record_id: str) -> str:
    """Append the collision record and its §8.2 event."""
    conn.execute(
        "INSERT INTO collision_resolutions (record_id, plan_id, "
        "colliding_destination_path, collision_kind, behaviour_applied, "
        "outcome, created_at, payload) VALUES (?,?,?,?,?,?,?,?)",
        (record_id, resolution.plan_id, resolution.colliding_destination_path,
         resolution.collision_kind, resolution.behaviour_applied,
         resolution.outcome, created_at, canonical_json(asdict(resolution))))
    append_event(
        conn, event_type=FILENAME_COLLISION_RESOLUTION, file_id=file_id,
        content_hash=resolution.incoming_content_hash,
        old_path=resolution.colliding_destination_path,
        new_path=resolution.final_destination_path, subsystem=SUBSYSTEM,
        component_version=component_version, observed_at=created_at,
        explanation=canonical_json(asdict(resolution)))
    return record_id
