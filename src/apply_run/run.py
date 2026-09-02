"""Applying what was frozen, and taking it back.

This is the gesture that moves a person's real files. Everything else the
product does is reversible by ignoring it; this is not, so the module is written
so that every stop leaves the disk exactly as it was and every stop is named.

**One plan at a time, never `apply_batch`.** `00`:155 offers *"one action at a
time or in a safely bounded batch"* and `74` §8 Q6 -- the bound and the halt
rule -- is unruled. Taking the first of the two options is not choosing Q6's
answer; it is declining to need one. What IS injected, with no default, is
`halt_on`: which result kinds end the run rather than being reported and
stepped past. That is the halt half of Q6 and it belongs to the composition
root, so it arrives as a parameter and is flagged wherever this is wired.

**Nothing here decides Q3, Q5, Q7 or Q8 either.** Q3: the plans carry
`stop_and_ask`, so `suffix_for` is never reached, and the function passed for it
raises rather than composing a suffix nobody has approved. Q7: the disposition
for an unconfirmed cross-volume copy is passed as `None`, so `apply_plan` raises
before it touches anything and the person is told with a sentence the
composition root wrote. Q8: `undo_offered` and `activity` both raise on an
unset retention period, so neither is called; `undo` itself has no retention
check, and `apply_report` needs none.

**The sentences are P12's, not this module's.** `mutation.vocabulary` already
carries `66` §10's one-distinct-sentence-per-outcome table, so `sentence_for` is
a lookup. The single exception is the cross-volume refusal, which has no entry
because the question behind it is open -- and that one is injected.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from mutation.constraints import FilesystemConstraints
from mutation.cross_volume import UnverifiedCopyDispositionRequired
from mutation.execute import ExecutionRecord, JournalEntry, apply_plan
from mutation.plan import MovePlan
from mutation.undo import UndoVerdict, undo
from mutation.vocabulary import (
    APPLIED, DECLINABLE_OUTCOMES, ENTRY_APPLIED, REFUSED, decline_message,
)

#: The one result a run can produce that P12's table has no sentence for,
#: because the question it reports is open. It is not a member of
#: `RESULT_KINDS`: no move was attempted, no execution record was written, and
#: calling it `refused` would put it in a count P12 defines.
CROSS_VOLUME_UNRULED: str = "not_attempted:cross_volume_unruled"


def halts(result: str, halt_on: frozenset[str]) -> bool:
    """Whether a run stops after this result. One decision, in one place.

    It was inline and inside ONE of the two branches: a cross-volume stop
    appended its outcome and `continue`d, skipping the check entirely, so a run
    whose plans all crossed a volume reported every one and never halted
    whatever `halt_on` said. The halt rule therefore had a shape the composition
    root could not express, which is `74` §8 Q6's own question.

    The kind is the half before the colon, because `halt_on` names KINDS and a
    result is `<kind>:<detail>`. `CROSS_VOLUME_UNRULED` has its own prefix,
    `not_attempted`, and is matched the same way -- it is not a member of
    `RESULT_KINDS`, so `_HALT_ON` cannot name it today, but the shape is now
    sayable rather than silently unreachable.
    """
    return result.partition(":")[0] in halt_on


def undo_order(entries: Sequence[JournalEntry]) -> tuple[JournalEntry, ...]:
    """Newest first, including when the clock cannot tell two entries apart.

    The ordering, and why a plain reverse sort does not give it, is
    `undo_order`'s -- including what happens when two entries share a timestamp.

    **A plain `sorted(..., reverse=True)` does not have that property.** Python's
    sort is stable, so entries sharing a `time_of_execution` keep their INPUT
    order -- and `applied_entries` supplies them `ORDER BY j.time_of_execution,
    j.record_id` ASCENDING. Ties ran oldest-first: the exact order the paragraph
    above forbids, in the function whose docstring claims it.

    Reversing the input first is the whole fix. Stability then puts tied entries
    in the reverse of the order they arrived in, which for `applied_entries`'
    ascending `(time, record_id)` is descending `record_id` -- newest first
    within the tie, by the journal's own ordering rather than by a second guess
    at what "newest" means.

    With the production clock at microsecond resolution a real tie is close to
    impossible and the consequence is leftover empty directories, not lost data.
    It becomes real the moment anyone injects a coarser clock, and the suite's
    own is per-minute.
    """
    return tuple(sorted(reversed(tuple(entries)),
                        key=lambda item: item.time_of_execution, reverse=True))


def suffix_refused(stem: str, attempt: int) -> str:
    """`74` §8 Q3 is unruled, so there is no suffix format to compose.

    Passed wherever `mutation` demands a `suffix_for`. Every frozen plan carries
    `stop_and_ask`, which is one of `00`:172's own four behaviours and writes
    nothing, so a collision pauses for the person before this is reached. If it
    ever is reached, raising is the only honest answer: inventing " (1)" would
    put a spelling nobody approved into the name of somebody's file.
    """
    raise NotImplementedError(
        "`74` §8 Q3 -- the deterministic collision suffix format -- has not "
        "been ruled on, so no suffix may be composed. A collision under this "
        "build stops and asks."
    )


def sentence_for(result: str, *, cross_volume: str) -> str | None:
    """`66` §10's sentence for one result, or `None` when it was applied.

    `apply_plan` spells a refusal `refused:<class>` while the message table is
    keyed on the bare class, because the event log records the tail. The prefix
    is stripped here rather than a second copy of the sentence being written.
    """
    if result == APPLIED:
        return None
    if result == CROSS_VOLUME_UNRULED:
        return cross_volume
    kind, _, tail = result.partition(":")
    key = tail if kind == REFUSED and tail in DECLINABLE_OUTCOMES else result
    return decline_message(key)


# ---------------------------------------------------------------------------
# Selecting.
# ---------------------------------------------------------------------------


def plans_under(plans: Sequence[MovePlan],
                node_ids: frozenset[str]) -> tuple[MovePlan, ...]:
    """The plans whose destination is one of these nodes, in their frozen order."""
    return tuple(plan for plan in plans
                 if plan.requested_destination_node in node_ids)


def already_applied(conn: sqlite3.Connection,
                    plans: Sequence[MovePlan]) -> frozenset[str]:
    """The plan ids that already moved a file and have not been taken back.

    A frozen plan stays in the approved set after it runs, so typing the same
    `--apply` twice is an ordinary thing for a person to do. Handing an
    already-applied plan back to `apply_plan` produces a truthful-but-wrong
    sentence -- the source is gone, so §8.1's object inspection refuses with
    *"the drive or folder this move needs is not available"* -- and a person
    who has just filed those files would read that as a fault. The fact that
    they are already filed is in the journal, so it is read from there and
    said plainly instead.
    """
    if not plans:
        return frozenset()
    wanted = {plan.plan_id for plan in plans}
    return frozenset(
        plan_id for _, plan_id in (
            (entry, entry.plan_id) for entry, _ in applied_entries(conn))
        if plan_id in wanted)


def applied_entries(
        conn: sqlite3.Connection) -> tuple[tuple[JournalEntry, str], ...]:
    """Every applied journal entry not yet reversed, with its destination node.

    Read from the journal and not from the frozen set, because what can be taken
    back is what actually happened -- a person who re-froze after applying has
    not thereby lost the ability to undo the move they already made.
    """
    rows = conn.execute(
        "SELECT j.payload, p.node_id FROM move_journal AS j "
        "JOIN move_plans AS p ON p.plan_id = j.plan_id "
        "WHERE j.entry_kind = ? AND j.entry_id NOT IN ("
        "  SELECT reverses_entry_id FROM move_journal "
        "  WHERE reverses_entry_id IS NOT NULL) "
        "ORDER BY j.time_of_execution, j.record_id", (ENTRY_APPLIED,)).fetchall()
    return tuple(
        (_entry(row[0]), row[1]) for row in rows)


def _entry(payload: str) -> JournalEntry:
    raw = json.loads(payload)
    raw["directories_created_by_this_action"] = tuple(
        raw["directories_created_by_this_action"])
    return JournalEntry(**raw)


# ---------------------------------------------------------------------------
# Applying.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MoveOutcome:
    """What happened to one file, and the sentence the person is owed."""

    plan_id: str
    file_id: str
    source_path: str
    intended_destination_path: str
    final_path: str | None
    result: str
    sentence: str | None
    record: ExecutionRecord | None


@dataclass(frozen=True)
class ApplyOutcome:
    outcomes: tuple[MoveOutcome, ...]
    #: The plan the run stopped after, when `halt_on` matched. `None` means
    #: every selected plan was attempted -- which is not the same as every one
    #: having moved, and the report must not conflate them.
    halted_after: str | None
    #: The plans never attempted because the run halted. Named, so a halt does
    #: not read as a set of files that quietly did not exist.
    not_attempted: tuple[MovePlan, ...]

    @property
    def applied(self) -> tuple[MoveOutcome, ...]:
        return tuple(item for item in self.outcomes if item.result == APPLIED)

    @property
    def stopped(self) -> tuple[MoveOutcome, ...]:
        return tuple(item for item in self.outcomes if item.result != APPLIED)


def apply_selected(conn: sqlite3.Connection,
                   plans: Sequence[MovePlan], *,
                   legal_destination_ids: frozenset[str],
                   source_root: Path,
                   destination_root: Path,
                   extra_protected: Callable[[Path], bool] | None,
                   conflict_copies: Callable[[Path], tuple[str, ...]],
                   dataless_of: Callable[[Path], bool],
                   approval_for: Callable[[str], object],
                   constraints: FilesystemConstraints,
                   normalize_filename: Callable[[str], str],
                   unruled_cross_volume_sentence: str,
                   halt_on: frozenset[str],
                   scan_state: str,
                   materialized: bool,
                   component_version: str,
                   user_id: str | None,
                   now: Callable[[], str],
                   mint_id: Callable[[], str]) -> ApplyOutcome:
    """Apply each plan in turn, reporting every one.

    An empty `plans` applies nothing and reports nothing. It is reachable only
    when a branch the person named holds no frozen plan, because
    `branches.branches_named` refuses an empty selection outright: an absent
    argument may never widen into everything.
    """
    outcomes: list[MoveOutcome] = []
    halted_after: str | None = None
    remaining: list[MovePlan] = []

    for index, plan in enumerate(plans):
        if halted_after is not None:
            remaining.append(plan)
            continue
        try:
            record = apply_plan(
                conn, plan, legal_destination_ids=legal_destination_ids,
                source_root=source_root, destination_root=destination_root,
                extra_protected=extra_protected,
                conflict_copies=conflict_copies, dataless_of=dataless_of,
                approval_for=approval_for, constraints=constraints,
                suffix_for=suffix_refused, max_suffix_attempts=0,
                normalize_filename=normalize_filename,
                # `74` §8 Q7: no disposition exists, so `apply_plan` raises
                # before it touches anything rather than making a copy nobody
                # has said what to do with.
                unverified_copy_disposition=None,
                scan_state=scan_state, materialized=materialized,
                component_version=component_version, user_id=user_id,
                now=now, mint_id=mint_id)
        except UnverifiedCopyDispositionRequired:
            # Nothing was touched: `apply_plan` demands the disposition before
            # it inspects anything. The outcome is reported and then falls
            # through to the SAME halt decision every other outcome reaches --
            # it used to `continue` past it.
            outcomes.append(MoveOutcome(
                plan_id=plan.plan_id, file_id=plan.file_id,
                source_path=plan.expected_source_path,
                intended_destination_path=plan.resolved_destination_path,
                final_path=None, result=CROSS_VOLUME_UNRULED,
                sentence=unruled_cross_volume_sentence, record=None))
            if halts(CROSS_VOLUME_UNRULED, halt_on):
                halted_after = plan.plan_id
            continue
        outcomes.append(MoveOutcome(
            plan_id=plan.plan_id, file_id=plan.file_id,
            source_path=plan.expected_source_path,
            intended_destination_path=plan.resolved_destination_path,
            final_path=record.final_destination_path, result=record.result,
            sentence=sentence_for(record.result,
                                  cross_volume=unruled_cross_volume_sentence),
            record=record))
        if halts(record.result, halt_on):
            halted_after = plan.plan_id

    return ApplyOutcome(outcomes=tuple(outcomes), halted_after=halted_after,
                        not_attempted=tuple(remaining))


# ---------------------------------------------------------------------------
# Taking it back.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class UndoOutcome:
    verdict: UndoVerdict
    sentence: str | None


@dataclass(frozen=True)
class TakeBackOutcome:
    outcomes: tuple[UndoOutcome, ...]

    @property
    def reversed_entries(self) -> tuple[UndoOutcome, ...]:
        return tuple(item for item in self.outcomes
                     if item.verdict.reversed_successfully)


def take_back(conn: sqlite3.Connection,
              entries: Sequence[JournalEntry], *,
              constraints: FilesystemConstraints,
              normalize_filename: Callable[[str], str],
              scan_state: str,
              materialized: bool,
              component_version: str,
              user_id: str | None,
              now: Callable[[], str],
              mint_id: Callable[[], str]) -> TakeBackOutcome:
    """Reverse each entry, newest first, reporting every one.

    The ordering, and why a plain reverse sort does not give it, is
    `undo_order`'s -- including what happens when two entries share a timestamp.

    `undo` is called with `unverified_copy_disposition=None` for the same reason
    the apply run does: `74` §8 Q7 is open, and a reversal that crosses a volume
    raises before touching anything rather than leaving a copy behind.
    """
    outcomes: list[UndoOutcome] = []
    for entry in undo_order(entries):
        verdict = undo(
            conn, entry.entry_id, constraints=constraints,
            unverified_copy_disposition=None,
            normalize_filename=normalize_filename, scan_state=scan_state,
            materialized=materialized, component_version=component_version,
            user_id=user_id, now=now, mint_id=mint_id)
        outcomes.append(UndoOutcome(
            verdict=verdict,
            sentence=(None if verdict.reversed_successfully
                      else decline_message(verdict.verdict))))
    return TakeBackOutcome(outcomes=tuple(outcomes))
