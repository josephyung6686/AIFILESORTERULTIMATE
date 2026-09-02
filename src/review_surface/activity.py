"""`66` §9's activity list: what moved, where, why, when, and can it be undone.

    "Every completed action appears in a reviewable activity list with the source
    path, destination path, evidence summary, policy that authorized it,
    collision behavior, move time, current status, and undo availability. The
    product must not present automatic movement as an invisible background fact."

Eight attributes. **Six have a producer and two do not, and the two are carried
as explicit, named absences rather than filled.** That is the whole design of this
module and it is deliberate:

* **`authorizing_policy` has no producer anywhere in the product.** There is no
  filing-policy record in any part's Contract-out (`74` §10); "keep this folder
  organized" is item 5 of `66` §22's release order and P12 is item 4. Three
  plausible values sit one attribute away from this field at the moment a row is
  built -- the plan's `required_review_policy`, the approval's copy of it, and
  P7's `permitting_policy` -- and **none of them is what §9 asks for.** The first
  two name the policy that DEMANDED REVIEW, which is the opposite claim: a plan
  under review was authorized by a person, not by a policy. The third is §8.4's
  permission to move a protected file at all, which is a privacy exemption and
  not a filing authority. Rendering any of them here would answer the person's
  question *"what decided to move this?"* wrongly, which is worse than not
  answering it: a wrong answer ends the enquiry and a named absence continues it.
* **`undo_availability` HAS a producer, and it is still injected.** `66` §11's
  retention period and its four choices are P12's, and `mutation.retention.undo_offered`
  answers exactly this column. This module still holds no answer of its own:
  what a producer says is shown, and when there is none the row says so.
  Guessing `66` §11's ninety-day default here would put a number this package
  has no authority to choose in front of a person as a promise about their
  files, and the composition root joining the two is not the same thing as this
  package knowing one.

  *This paragraph used to read "has no producer YET ... P12's retention module
  is a later wave". F3 landed one commit before the wave that wrote it, so the
  reason was expired on arrival and the eighth attribute rendered as "the
  product cannot say yet" on a product that could. `84` §5.4. The join is
  exercised end to end by* `test_undo_availability_is_answered_by_p12s_own_retention_module`.

**On the two paths.** `74` §4.3 says P13 renders no resolved filesystem path
outside §8.3's own apply and undo-conflict fields. `66` §9 requires the source
and destination paths on every row of this list, and `66` outranks `74`
(authority order, `69` §0). The rule's PURPOSE survives intact: B3 is about who
RESOLVES a path, and P13 resolves nothing here. Both strings are read off P12's
journal entry exactly as P12 wrote them.

**A row is one action.** The three records it is built from -- the journal entry,
the execution record and the move plan -- must name the same plan, or the row is
refused. A row stitched from three different actions would be a confident,
readable lie, and it is the shape a caller reaching for `[-1]` three times
produces by accident.

This module performs no query. The composition root reads P12's three records
through P12's own published readers and hands them here, because P13 may not
import a mutation surface (Done-means 22) and P12 may not import P13 (A5).
"""
from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Protocol

#: `66` §9's own list, in `66` §9's own order. Spelled once. A renderer walks
#: this rather than eight attribute names of its own, so an attribute dropped
#: from a surface is caught by the list rather than by nobody.
ACTIVITY_ATTRIBUTES: tuple[str, ...] = (
    "source_path", "destination_path", "evidence_summary",
    "authorizing_policy", "collision_behaviour", "move_time", "status",
    "undo_availability",
)

#: What the row says instead of a policy. It names what is missing and why, so a
#: reader is not left to wonder whether the product forgot or whether nothing
#: authorized the move.
AUTHORIZING_POLICY_HAS_NO_PRODUCER: str = (
    "No filing policy authorized this move: the product has no filing policy "
    "yet, and every move so far was set going by a person. The policy that "
    "demanded review is a different thing and is not shown here as this one.")

#: The same, for undo. `66` §11 fixes the retention period and its four choices;
#: nothing in the product yet records which one is in force.
UNDO_AVAILABILITY_HAS_NO_PRODUCER: str = (
    "The product cannot say yet how long this move stays undoable: no undo "
    "retention period has been recorded.")


class ActionNotOneAction(ValueError):
    """Three records naming three different plans, offered as one row."""


class UndoAvailabilityRequired(ValueError):
    """No answer, and no producer of one, about whether this can still be undone."""


class JournalEntryShape(Protocol):
    """What this module needs of P12's journal entry, and nothing more.

    Structural rather than imported: P13 may not import a mutation surface, and
    stating the shape here is also what makes the requirement legible -- these
    eight names are the contract, and a field P12 renames breaks the row rather
    than silently emptying it.
    """

    entry_id: str
    plan_id: str
    plan_version: str
    file_id: str
    original_source_path: str
    destination_path: str
    collision_behaviour: str
    time_of_execution: str


class ExecutionShape(Protocol):
    """What this module needs of P12's execution record: the current status."""

    plan_id: str
    result: str
    finished_at: str


class PlanShape(Protocol):
    """What this module needs of P12's move plan: the evidence summary."""

    plan_id: str
    reason_and_evidence_summary: str


@dataclass(frozen=True)
class CompletedAction:
    """One completed action, as its three P12 records.

    Three arguments rather than a bag, so a caller cannot hand over two and have
    the third quietly default to nothing.
    """

    journal_entry: JournalEntryShape
    execution: ExecutionShape
    plan: PlanShape


@dataclass(frozen=True)
class ActivityEntry:
    """One row of `66` §9's list. It adds no judgement and no value of its own.

    **`authorizing_policy` is a property and not a field, and that is the point.**
    A field could be set. A property that always returns `None` cannot, so there
    is no parameter anywhere on this record or on its builder through which a
    plausible-looking policy could be supplied by a caller in a hurry -- which is
    the same construction `mutation.names.resolve_name` uses to make semantic
    renaming unreachable rather than merely forbidden.
    """

    entry_id: str
    plan_id: str
    plan_version: str
    file_id: str
    source_path: str
    destination_path: str
    evidence_summary: str
    collision_behaviour: str
    move_time: str
    status: str
    undo_availability: str | None
    undo_availability_absence: str | None

    @property
    def authorizing_policy(self) -> None:
        """Always `None`. `66` §9's attribute, with nothing in the product to fill it."""
        return None

    @property
    def authorizing_policy_absence(self) -> str:
        """Why it is `None`, in words a person can act on."""
        return AUTHORIZING_POLICY_HAS_NO_PRODUCER


def activity_entry(action: CompletedAction, *,
                   undo_availability: str | None) -> ActivityEntry:
    """One row from one completed action. Renders; decides nothing; resolves nothing.

    There is no `authorizing_policy` parameter and no `policy` parameter. That
    absence is the guard: `faked_authorizations` can catch a row that carries one,
    and this signature is why no row built here ever will.
    """
    entry = action.journal_entry
    named = {entry.plan_id, action.execution.plan_id, action.plan.plan_id}
    if len(named) > 1:
        raise ActionNotOneAction(
            f"a row was offered as one action but its journal entry, execution "
            f"record and move plan name {len(named)} different plans "
            f"{sorted(named)}. One row is one action; three records from three "
            "actions read as a single history that never happened")
    return ActivityEntry(
        entry_id=entry.entry_id,
        plan_id=entry.plan_id,
        plan_version=entry.plan_version,
        file_id=entry.file_id,
        # P12's own two strings, as P12 wrote them. Nothing here composes,
        # normalizes, joins or shortens either.
        source_path=entry.original_source_path,
        destination_path=entry.destination_path,
        evidence_summary=action.plan.reason_and_evidence_summary,
        collision_behaviour=entry.collision_behaviour,
        move_time=entry.time_of_execution,
        status=action.execution.result,
        undo_availability=undo_availability,
        undo_availability_absence=(UNDO_AVAILABILITY_HAS_NO_PRODUCER
                                   if undo_availability is None else None))


def activity_list(actions: Sequence[CompletedAction], *,
                  undo_availability_for: Callable[[CompletedAction], str | None] | None,
                  ) -> tuple[ActivityEntry, ...]:
    """`66` §9's list, oldest move first.

    `undo_availability_for` is injected with NO default and `None` refuses. §9
    lists undo availability among the eight and `66` §11 fixes the retention that
    decides it, and neither is P13's to answer: a package that supplied its own
    answer here would be telling a person how long their files stay recoverable
    on its own authority.

    Ordered by when the move happened rather than by the order the caller
    assembled them, because `66` §9's own use for this list -- *"see what moved
    today, this week, or under a particular policy"* -- is a question about time,
    and a list whose order came from a query plan answers it differently on
    different days. `entry_id` breaks a tie so the order is total.
    """
    if undo_availability_for is None:
        raise UndoAvailabilityRequired(
            "`66` §9 puts undo availability on every row and `66` §11 makes the "
            "retention period the user's own choice out of four. P13 has no "
            "answer of its own and will not invent one: the composition root "
            "supplies the producer, and until one exists it supplies a callable "
            "that says so")
    rows = tuple(
        activity_entry(action, undo_availability=undo_availability_for(action))
        for action in actions)
    return tuple(sorted(rows, key=lambda row: (row.move_time, row.entry_id)))


def faked_authorizations(entries: Sequence[object]) -> list[str]:
    """Every row claiming an authorizing policy. There is no such policy to claim.

    Takes the rows as an argument rather than reading a package-level list, so it
    can be pointed at a deliberately faked row. A guard only ever run over rows
    that cannot carry the thing it looks for passes exactly as well when it is
    unable to find anything at all -- and four guards on this project had quietly
    reached that state.

    An empty string counts as a fake. `""` renders as *authorized by nothing in
    particular*, which is a claim; `None` beside
    `AUTHORIZING_POLICY_HAS_NO_PRODUCER` is an admission.
    """
    return [str(getattr(entry, "entry_id", entry))
            for entry in entries
            if getattr(entry, "authorizing_policy", None) is not None]
