"""§8.3's conditional undo. Reverse, or surface a conflict and touch nothing.

*"Undo must be conditional rather than destructive. ... Before reversing a move,
the system checks that the file at the destination is still the expected content
and that restoring it will not overwrite a newer or unrelated file. If the user
manually edited or moved the file after the product acted, undo should surface a
conflict rather than forcing a rollback"* (`00`:175).

The shape of this module is that sentence read as an order. Four questions are
asked before anything is touched, and any of them can end the attempt with an
answer:

1. **Is everything available?** An unmounted volume or a detached folder makes
   every later answer meaningless, so it is asked first -- and it is a REFUSAL
   rather than a conflict, because nothing about the file itself is in doubt.
2. **Is the file still where P12 put it?** `conflict:destination_missing_or_moved`.
3. **Is it still the bytes P12 moved?** `conflict:destination_content_changed`.
4. **Would restoring it write over something?** `conflict:source_path_occupied`.
   Asked with `find_collision` rather than `Path.exists()`, because on a folding
   volume `Resume.pdf` and `resume.pdf` are one path, and it is exactly the twin
   a person cannot tell apart that must not be overwritten.

**A conflict performs no mutation.** Not "no net mutation" -- none at all. That
is why every question above is asked before the first `rename`, and why the
`_conflict` helper is the only way out of those four branches. `66` §11: the
product should *"say that the move requires review because the file changed
after it was filed, show the relevant paths and hashes, and let the user
decide"*, and a rollback performed before noticing would have thrown away
whatever the person did in the meantime.

**A reversal is itself a mutation and runs the full discipline** -- V1 and V2
before, V3 after, V4 where it crosses volumes -- because a reversal that skipped
verification would be the one unverified write in the product. Its journal entry
is APPENDED; the original entry is never edited or removed (§8.2).

**Retention is not asked here.** `66` §11 fixes how long undo is *offered*
(`retention.py`), and no sentence anywhere says a late reversal must be refused.
`74` §8 Q8 -- whether adopting a new plan version ends undo -- is the owner's and
is open, so nothing in this module consults a plan version to decide.

**No numeric literal beyond 0 and 1 appears in this file.** Every clock, name and
policy arrives injected; absent means refuse (A7).
"""
from __future__ import annotations

import json
import os
import sqlite3
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from database_agent.events import append_event
from database_agent.files_table import get_file, observe_path
from database_agent.identity import hash_file
from database_agent.verify import VerificationPoint, verify_content
from evidence_shape.canonical import canonical_json
from scan_agent.basic_record import parent_folder_context

from mutation.collision import find_collision
from mutation.constraints import FilesystemConstraints
from mutation.cross_volume import copy_and_confirm
from mutation.directories import reverse_directories
from mutation.events import record_failed_move
from mutation.execute import JournalEntry, record_journal_entry
from mutation.vocabulary import (
    ATOMIC_RENAME, CONFLICT_DESTINATION_CONTENT_CHANGED,
    CONFLICT_DESTINATION_MISSING_OR_MOVED, CONFLICT_SOURCE_PATH_OCCUPIED,
    CROSS_VOLUME_COPY_AND_DELETE, ENTRY_APPLIED, ENTRY_REVERSAL, REVERSED,
    STOP_AND_ASK, SUBSYSTEM, UNDO, UNDO_REFUSED_UNAVAILABLE, UNDO_VERDICTS,
    V4_DESTINATION_UNCONFIRMED, check, decline_message,
)

#: The keys the `undo` event carries in its own right. Everything else in the
#: explanation is the verdict's `detail`, which is what makes the reconstruction
#: in `undo_verdicts_for` exact rather than approximate.
_OWN_KEYS: frozenset[str] = frozenset({
    "entry_id", "plan_id", "verdict", "reversal_entry_id",
    "observed_destination_hash", "occupant_at_source_hash",
    "directory_outcomes"})

_NO_DETAIL: Mapping[str, object] = MappingProxyType({})


class NoSuchEntry(KeyError):
    """No journal entry with that id.

    NOT a refusal class, for the reason `plan.NoSuchPlan` is not one: a refusal
    describes a move that could not be reversed and carries a sentence for the
    person, and this is a caller naming something that does not exist.
    """


class AlreadyReversed(RuntimeError):
    """A reversal entry already reverses this one. Undo is not idempotent."""


class NotAnAppliedEntry(ValueError):
    """Only an `applied` entry can be undone; a reversal is not a move."""


class ReversalUnverified(RuntimeError):
    """A cross-volume reversal whose copy V4 would not confirm.

    The one state Contract out §7's five undo verdicts cannot express, and it is
    `74` §8 Q7 seen from the other direction. §8.2 forbids removing the file at
    its destination and §7.11 forbids removing the unconfirmed copy, so BOTH
    exist afterwards. None of the five verdicts is true of that -- the
    destination did not change, it is not missing, and the source path was free
    when it was checked -- so P12 records `failed:v4_destination_unconfirmed`,
    which has its own sentence for the person, and raises rather than filing the
    state under a verdict that would misdescribe it.
    """


@dataclass(frozen=True)
class UndoVerdict:
    """Contract out §7. What was asked, what was found, and what happened."""

    entry_id: str
    verdict: str
    reversal_entry_id: str | None
    destination_path: str
    original_source_path: str
    expected_hash: str
    #: The hash of what was actually at the destination, or `None` when there
    #: was nothing hashable there. `None` is not "unknown": it says the file was
    #: gone, which is the finding.
    observed_destination_hash: str | None
    occupant_at_source_hash: str | None
    directory_outcomes: tuple[tuple[str, str], ...]
    detail: Mapping[str, object]

    def __post_init__(self) -> None:
        check(self.verdict, UNDO_VERDICTS, name="undo verdict")

    @property
    def reversed_successfully(self) -> bool:
        return self.verdict == REVERSED


# ---------------------------------------------------------------------------
# Reading the journal. Append-only, so every read here is a read of history.
# ---------------------------------------------------------------------------


def _from_payload(payload: str) -> JournalEntry:
    raw = json.loads(payload)
    raw["directories_created_by_this_action"] = tuple(
        raw["directories_created_by_this_action"])
    return JournalEntry(**raw)


def entry_by_id(conn: sqlite3.Connection, entry_id: str) -> JournalEntry | None:
    row = conn.execute("SELECT payload FROM move_journal WHERE entry_id = ?",
                       (entry_id,)).fetchone()
    return None if row is None else _from_payload(row[0])


def entries_for_plan(conn: sqlite3.Connection,
                     plan_id: str) -> tuple[JournalEntry, ...]:
    """Every entry for one plan, in the order it was written. Two after an undo."""
    return tuple(
        _from_payload(row[0]) for row in conn.execute(
            "SELECT payload FROM move_journal WHERE plan_id = ? "
            "ORDER BY record_id", (plan_id,)))


def is_reversed(conn: sqlite3.Connection, entry_id: str) -> bool:
    return conn.execute(
        "SELECT COUNT(*) FROM move_journal WHERE reverses_entry_id = ?",
        (entry_id,)).fetchone()[0] > 0


def applied_destinations(conn: sqlite3.Connection, *,
                         excluding: str) -> tuple[str, ...]:
    """Where every still-applied entry other than `excluding` put its file.

    "Still applied" means an `applied` entry that no reversal entry reverses. An
    entry whose own move has since been undone has no file at its destination
    any more and must not hold a directory hostage (Contract out §7).
    """
    return tuple(row[0] for row in conn.execute(
        "SELECT destination_path FROM move_journal WHERE entry_kind = ? "
        "AND entry_id <> ? AND entry_id NOT IN "
        "(SELECT reverses_entry_id FROM move_journal "
        " WHERE reverses_entry_id IS NOT NULL) ORDER BY record_id",
        (ENTRY_APPLIED, excluding)))


# ---------------------------------------------------------------------------
# The four questions, and the reversal.
# ---------------------------------------------------------------------------


def _hash_or_none(path: Path, *, materialized: bool) -> str | None:
    """What is at `path`, hashed, or `None` when nothing hashable is there.

    A symlink is never followed -- §8.3's safe default is about mutation, and
    hashing a link's target to decide whether to overwrite the link would be
    following it in the one place it matters most.
    """
    if path.is_symlink() or not path.is_file():
        return None
    try:
        return hash_file(path, materialized=materialized)
    except OSError:
        return None


def _verdict(entry: JournalEntry, verdict: str, *,
             observed: str | None = None, occupant: str | None = None,
             reversal_entry_id: str | None = None,
             directory_outcomes: tuple[tuple[str, str], ...] = (),
             detail: Mapping[str, object] = _NO_DETAIL) -> UndoVerdict:
    return UndoVerdict(
        entry_id=entry.entry_id, verdict=verdict,
        reversal_entry_id=reversal_entry_id,
        destination_path=entry.destination_path,
        original_source_path=entry.original_source_path,
        expected_hash=entry.content_hash_at_movement,
        observed_destination_hash=observed, occupant_at_source_hash=occupant,
        directory_outcomes=directory_outcomes,
        detail=MappingProxyType({"message": decline_message(verdict), **dict(detail)}
                                if verdict != REVERSED
                                else {**dict(detail)}))


def undo(conn: sqlite3.Connection, entry_id: str, *,
         constraints: FilesystemConstraints,
         unverified_copy_disposition: str | None,
         normalize_filename: Callable[[str], str],
         scan_state: str,
         materialized: bool,
         component_version: str,
         user_id: str | None,
         now: Callable[[], str],
         mint_id: Callable[[], str]) -> UndoVerdict:
    """Reverse one applied journal entry, or say why it cannot be reversed.

    Every argument after `entry_id` is injected with no default, for the reason
    `apply_plan`'s are: the constraint table is a platform fact P12 does not
    author, and the clock and the id minter are the composition root's so that
    no record is stamped by chance.
    """
    entry = entry_by_id(conn, entry_id)
    if entry is None:
        raise NoSuchEntry(entry_id)
    if entry.entry_kind != ENTRY_APPLIED:
        raise NotAnAppliedEntry(
            f"{entry_id!r} is a {entry.entry_kind} entry; a reversal is a record "
            "of a move already undone, not a move that can be undone")
    if is_reversed(conn, entry_id):
        raise AlreadyReversed(entry_id)

    destination = Path(entry.destination_path)
    source = Path(entry.original_source_path)

    def answered(verdict: UndoVerdict) -> UndoVerdict:
        _record_attempt(conn, entry, verdict, component_version=component_version,
                        user_id=user_id, observed_at=now())
        return verdict

    # 1. Availability. Nothing below is meaningful if a volume is not mounted.
    for path, which in ((destination.parent, "destination"),
                        (source.parent, "source")):
        if not path.exists():
            return answered(_verdict(
                entry, UNDO_REFUSED_UNAVAILABLE,
                detail={"unavailable": which, "path": str(path)}))

    # 2. Is the file still where P12 put it?
    if destination.is_symlink() or not destination.is_file():
        return answered(_verdict(entry, CONFLICT_DESTINATION_MISSING_OR_MOVED))

    # 3. Is it still the bytes P12 moved?
    observed = _hash_or_none(destination, materialized=materialized)
    if observed != entry.content_hash_at_movement:
        return answered(_verdict(entry, CONFLICT_DESTINATION_CONTENT_CHANGED,
                                 observed=observed))

    # 4. Would restoring it write over something? By collation key, not by
    #    `exists()`: the twin a person cannot tell apart is the one at stake.
    occupied = find_collision(source.parent, source.name, constraints=constraints)
    if occupied is not None:
        return answered(_verdict(
            entry, CONFLICT_SOURCE_PATH_OCCUPIED, observed=observed,
            occupant=_hash_or_none(occupied, materialized=materialized),
            detail={"occupying_path": str(occupied)}))

    # The reversal is a mutation and runs the same discipline as a forward move.
    for point in (VerificationPoint.V1, VerificationPoint.V2):
        verify_content(conn, entry.file_id, entry.content_hash_at_movement,
                       point=point, author=SUBSYSTEM,
                       component_version=component_version,
                       materialized=materialized)

    mode = (ATOMIC_RENAME
            if entry.source_volume == entry.destination_volume
            else CROSS_VOLUME_COPY_AND_DELETE)
    if mode == ATOMIC_RENAME:
        os.rename(destination, source)
    else:
        outcome = copy_and_confirm(
            conn, source=destination, destination=source,
            expected_hash=entry.content_hash_at_movement, constraints=constraints,
            unverified_copy_disposition=unverified_copy_disposition,
            component_version=component_version, materialized=materialized)
        if not outcome.destination_confirmed:
            # Nothing removed, and nothing this vocabulary can name. Both paths
            # go on a `failed move` so the person can be told, and the caller is
            # not handed a verdict that would misdescribe the disk.
            record_failed_move(
                conn, failure_class=V4_DESTINATION_UNCONFIRMED,
                file_id=entry.file_id,
                content_hash=entry.content_hash_at_movement,
                source_path=str(destination), destination_path=str(source),
                observed_at=now(), component_version=component_version,
                user_id=user_id,
                detail={"reverses_entry_id": entry.entry_id,
                        "plan_id": entry.plan_id, "mode": mode,
                        "filed_path_retained": str(destination),
                        "unverified_copy_path": outcome.unverified_copy_path,
                        "unverified_copy_disposition": outcome.disposition})
            raise ReversalUnverified(
                f"V4 would not confirm the copy restored to {source}; the filed "
                f"file at {destination} was left exactly where it was, and the "
                "unconfirmed copy was not removed (§8.2, §7.11)")

    _observe_back(conn, entry, source, normalize_filename=normalize_filename,
                  scan_state=scan_state, materialized=materialized,
                  component_version=component_version)
    after = verify_content(
        conn, entry.file_id, entry.content_hash_at_movement,
        point=VerificationPoint.V3, author=SUBSYSTEM,
        component_version=component_version, materialized=materialized)

    # The file is out of the directories this action created, so they can now be
    # asked Contract out §7's three conditions. This runs on the successful path
    # only: a conflict reverses no directory, because a conflict mutates nothing.
    outcomes = reverse_directories(
        entry,
        other_destinations=applied_destinations(conn, excluding=entry.entry_id))

    reversal_id = mint_id()
    record_journal_entry(conn, JournalEntry(
        entry_id=reversal_id, entry_kind=ENTRY_REVERSAL,
        reverses_entry_id=entry.entry_id, plan_id=entry.plan_id,
        plan_version=entry.plan_version, file_id=entry.file_id,
        hash_algorithm=entry.hash_algorithm,
        original_source_path=entry.destination_path,
        destination_path=entry.original_source_path,
        content_hash_at_movement=entry.content_hash_at_movement,
        # A reversal writes over nothing: an occupied source path ends the
        # attempt at question 4 above. That is `stop_and_ask` exactly -- halt
        # and let the person decide -- and it is the behaviour that was applied,
        # not the one the forward plan happened to carry.
        collision_behaviour=STOP_AND_ASK,
        post_move_verification_result=after,
        source_volume=entry.destination_volume,
        destination_volume=entry.source_volume, execution_mode=mode,
        # A reversal creates no directory. What it did to the ones the forward
        # move created is on the verdict and on the `undo` event.
        directories_created_by_this_action=(),
        intended_display_name=entry.intended_display_name,
        filesystem_safe_name=source.name,
        time_of_execution=now()), record_id=mint_id())

    return answered(_verdict(
        entry, REVERSED, observed=observed, reversal_entry_id=reversal_id,
        directory_outcomes=outcomes,
        detail={"execution_mode": mode,
                "post_move_verification_result": after}))


def _observe_back(conn: sqlite3.Connection, entry: JournalEntry, source: Path, *,
                  normalize_filename: Callable[[str], str], scan_state: str,
                  materialized: bool, component_version: str) -> None:
    """Tell P1 the file is home again. This is what makes V3 answerable.

    Same trap as the forward move: `verify_content` hashes `files.current_path`
    and takes no path, so V3 can only be asked after `observe_path` has moved
    `current_path` back. The descriptive arguments are carried forward from P1's
    own row unchanged -- a rename preserves size and timestamps, and re-encoding
    a stat here would author a format P3 declined to (P3 Q2). `normalize_filename`
    is injected for the same reason: P3 Q1 is open on Unicode form and case
    folding, and P12 may not choose differently from P3.
    """
    row = get_file(conn, entry.file_id)
    observe_path(
        conn, source, author=SUBSYSTEM, component_version=component_version,
        filename=source.name,
        normalized_filename=normalize_filename(source.name),
        extension=row["extension"], observed_size=row["observed_size"],
        observed_timestamps=row["observed_timestamps"],
        parent_folder_context=parent_folder_context(source),
        mime_type=row["mime_type"], detected_format=row["detected_format"],
        scan_state=scan_state, materialized=materialized)


def _record_attempt(conn: sqlite3.Connection, entry: JournalEntry,
                    verdict: UndoVerdict, *, component_version: str,
                    user_id: str | None, observed_at: str) -> None:
    """One `undo` event per attempt, whatever the verdict.

    A conflict is a result and it is recorded. `66` §19 requires every movement
    action to be visible afterwards, and an undo the person tried and could not
    have is exactly the kind of thing that must not vanish.
    """
    append_event(
        conn, event_type=UNDO, file_id=entry.file_id,
        content_hash=entry.content_hash_at_movement,
        old_path=entry.destination_path, new_path=entry.original_source_path,
        subsystem=SUBSYSTEM, component_version=component_version,
        observed_at=observed_at, user_id=user_id,
        explanation=canonical_json({
            "entry_id": entry.entry_id, "plan_id": entry.plan_id,
            "verdict": verdict.verdict,
            "reversal_entry_id": verdict.reversal_entry_id,
            "observed_destination_hash": verdict.observed_destination_hash,
            "occupant_at_source_hash": verdict.occupant_at_source_hash,
            "directory_outcomes": [list(pair)
                                   for pair in verdict.directory_outcomes],
            **dict(verdict.detail)}))


def undo_verdicts_for(conn: sqlite3.Connection,
                      plan_id: str) -> tuple[UndoVerdict, ...]:
    """Every undo attempt on this plan, read back from its `undo` events.

    The verdict has no table of its own: the journal records what happened to the
    file and P1's log records what was attempted, and a third home for the same
    fact is the defect class this repository has paid for most.
    """
    entries = {entry.entry_id: entry for entry in entries_for_plan(conn, plan_id)}
    verdicts: list[UndoVerdict] = []
    for row in conn.execute(
            "SELECT explanation FROM events WHERE event_type = ? "
            "ORDER BY event_id", (UNDO,)):
        payload = json.loads(row[0])
        entry = entries.get(payload["entry_id"])
        if entry is None:
            continue
        verdicts.append(UndoVerdict(
            entry_id=payload["entry_id"], verdict=payload["verdict"],
            reversal_entry_id=payload["reversal_entry_id"],
            destination_path=entry.destination_path,
            original_source_path=entry.original_source_path,
            expected_hash=entry.content_hash_at_movement,
            observed_destination_hash=payload["observed_destination_hash"],
            occupant_at_source_hash=payload["occupant_at_source_hash"],
            directory_outcomes=tuple(
                tuple(pair) for pair in payload["directory_outcomes"]),
            detail=MappingProxyType({key: value for key, value in payload.items()
                                     if key not in _OWN_KEYS})))
    return tuple(verdicts)
