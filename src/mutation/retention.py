"""What `66` says about a move once it has happened.

Three things, and they live together because they are one moment for the person:
the run has finished, and now they want to know what happened, what did not, and
what they can still take back.

* **`66` §11 -- how long undo is offered.** *"The recommended default undo
  retention period is 90 days. The user should be able to select 30 days, 90
  days, one year, or retention until manually cleared."* The four choices are
  `66`'s and are closed in `vocabulary.py`. **The duration each one means is
  injected and has no default here.** The 90 days is a product recommendation
  that belongs in `cli.py`, the composition root, and A7 admits no numeric
  literal in this package in any case. Absent means refuse.
* **§8.6 -- run legibility.** *"An apply run reports applied / refused / stale /
  paused / failed counts, so deferred work is visible rather than presented as
  completed."* The five are never summed into one number and a plan nobody
  attempted is reported as not attempted rather than quietly dropped.
* **`66` §9 -- the activity list.** *"Every completed action appears in a
  reviewable activity list with the source path, destination path, evidence
  summary, policy that authorized it, collision behavior, move time, current
  status, and undo availability."*

**Two judgements, both recorded rather than buried.**

`74` §8 **Q8** is the owner's: `66` §11 fixes the retention period and says
nothing about whether adopting a new plan version ends undo. So retention here
governs what is **offered** and nothing else -- past the period `undo_offered`
answers False, and `undo.undo()` does not consult it and does not start refusing.
No sentence anywhere says a late reversal must be refused, and the journal is
never purged: *"the product should never silently purge active-policy history in
a way that makes a recent move impossible to understand or review"* (`66` §11).

`66` §9 wants *"the policy that authorized it"* and **no filing policy exists** --
the filing-policy layer is item 5 of `66` §22's release order, after P12. So
`ActivityRow.authorizing_policy` reports the plan's `Required review policy` and
`filing_policy_present` says the filing policy is absent. The gap is carried, not
filled, and never rendered as a blank column.

**No numeric literal beyond 0 and 1 appears in this file.**
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta

from database_agent.supersede import mark_superseded
from evidence_shape.canonical import canonical_json

from mutation.execute import JournalEntry
from mutation.vocabulary import (
    APPLIED, ENTRY_APPLIED, FAILED, PAUSED, REFUSED, RESULT_KINDS, STALE,
    UNBOUNDED_RETENTION, UNDO_RETENTION_CHOICES, check, decline_message,
)


class RetentionPeriodRequired(RuntimeError):
    """A retention choice whose period is absent, or present where it may not be.

    NOT a refusal class. A refusal describes a move that could not run and
    carries a sentence for the person; this is the composition root having failed
    to state how long its own promise lasts.
    """


class NoRetentionSetting(RuntimeError):
    """Nobody has said how long undo is offered for. Absence is never a default."""


@dataclass(frozen=True)
class UndoRetention:
    """One of `66` §11's four choices, and what the root says it means."""

    choice: str
    #: `None` only for `until_manually_cleared`, where "no expiry" is the answer
    #: rather than a missing one.
    period: timedelta | None

    def __post_init__(self) -> None:
        check(self.choice, UNDO_RETENTION_CHOICES, name="undo retention choice")
        if self.choice == UNBOUNDED_RETENTION:
            if self.period is not None:
                raise RetentionPeriodRequired(
                    "`until manually cleared` and an expiry are two different "
                    "promises; a choice cannot carry both")
            return
        if not isinstance(self.period, timedelta) or self.period <= timedelta():
            raise RetentionPeriodRequired(
                f"{self.choice!r} is one of `66` §11's four names and how long "
                "it lasts is the composition root's to state; P12 has no "
                "default for it")

    @property
    def expires(self) -> bool:
        return self.period is not None


def _moment(stamp: str) -> datetime:
    """One parse for every timestamp this module compares.

    Every clock in P12 is injected and every stamp is ISO 8601, so this is the
    only place the two are turned into something subtractable.
    """
    return datetime.fromisoformat(stamp)


def set_undo_retention(conn: sqlite3.Connection, retention: UndoRetention, *,
                       user_id: str | None, set_at: str, record_id: str) -> str:
    """Record the person's choice. The previous one is superseded, never edited.

    The supersede link is made BEFORE the new row is inserted, which is the
    reverse of the usual order and is forced by `schema.py`'s
    `one_current_undo_retention` index: at most one row may be current, so the
    old one has to stop being current first. The new row therefore carries its
    own `supersedes` in the INSERT rather than receiving it afterwards.
    """
    old = conn.execute(
        "SELECT record_id FROM undo_retention WHERE superseded_by IS NULL"
    ).fetchone()
    if old is not None:
        mark_superseded(conn, "undo_retention", old_id=old["record_id"],
                        new_id=record_id,
                        reason=f"the person selected {retention.choice}")
    conn.execute(
        "INSERT INTO undo_retention (record_id, retention_choice, set_at, "
        "set_by, payload, supersedes) VALUES (?,?,?,?,?,?)",
        (record_id, retention.choice, set_at, user_id,
         canonical_json({
             "choice": retention.choice,
             "period_seconds": (None if retention.period is None
                                else retention.period.total_seconds())}),
         None if old is None else old["record_id"]))
    return record_id


def current_undo_retention(conn: sqlite3.Connection) -> UndoRetention | None:
    """The setting in force, or `None` when nobody has stated one.

    `None` is the honest answer and the caller's problem. Returning `66`'s
    recommended 90 days from here would make the part package the author of a
    promise it is only supposed to keep.
    """
    row = conn.execute(
        "SELECT payload FROM undo_retention WHERE superseded_by IS NULL"
    ).fetchone()
    if row is None:
        return None
    payload = json.loads(row[0])
    seconds = payload["period_seconds"]
    return UndoRetention(
        choice=payload["choice"],
        period=None if seconds is None else timedelta(seconds=seconds))


def undo_offered(entry: JournalEntry, *, retention: UndoRetention | None,
                 at: str) -> bool:
    """Is undo still on offer for this entry at time `at`?

    This answers `66` §9's *"undo availability"* column and nothing more. It is
    not a permission check and `undo.undo()` never calls it: `74` §8 Q8 is open
    on whether elapsed time ends the ability to reverse, and P12 stops OFFERING
    without starting to REFUSE.
    """
    if retention is None:
        raise NoRetentionSetting(
            "how long undo is offered for is `66` §11's setting and the "
            "composition root's to state; P12 will not assume one")
    if not retention.expires:
        return True
    return _moment(at) - _moment(entry.time_of_execution) <= retention.period


# ---------------------------------------------------------------------------
# §8.6's run legibility.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ApplyRunReport:
    """What one apply run did, with deferred work visible as deferred (§8.6)."""

    applied: int
    refused: int
    stale: int
    paused: int
    failed: int
    refusals_by_class: Mapping[str, int]
    stale_by_trigger: Mapping[str, int]
    paused_by_reason: Mapping[str, int]
    failed_by_class: Mapping[str, int]
    #: One `66` §10 sentence per plan that did not apply, in plan order.
    declines: tuple[tuple[str, str], ...]
    #: Plans that were handed to the run and produced no execution record at
    #: all. Named rather than omitted: a plan nobody attempted is exactly the
    #: work §8.6 says must not be presented as completed.
    not_attempted: tuple[str, ...]

    @property
    def total(self) -> int:
        return (self.applied + self.refused + self.stale + self.paused
                + self.failed)


def apply_report(conn: sqlite3.Connection, *,
                 plan_ids: Sequence[str]) -> ApplyRunReport:
    """One line per plan -- its latest execution record -- never one per attempt.

    A plan that went stale and was refreshed becomes a NEW plan with a new id
    (`plan.supersede_plan`), so the retained stale record still belongs to the
    old id and still appears in a report over both. Counting every attempt under
    one id would instead let a single file be both deferred and completed, which
    is the one thing §8.6 asks a run report not to say.
    """
    counts = {kind: 0 for kind in RESULT_KINDS}
    details: dict[str, dict[str, int]] = {kind: {} for kind in RESULT_KINDS}
    declines: list[tuple[str, str]] = []
    missing: list[str] = []

    for plan_id in plan_ids:
        row = conn.execute(
            "SELECT result FROM execution_records WHERE plan_id = ? "
            "ORDER BY record_id DESC LIMIT 1", (plan_id,)).fetchone()
        if row is None:
            missing.append(plan_id)
            continue
        result = row[0]
        kind, _, detail = result.partition(":")
        counts[kind] += 1
        if detail:
            details[kind][detail] = details[kind].get(detail, 0) + 1
        if kind != APPLIED:
            # `66` §10's sentence for whichever outcome it was. A refusal is
            # keyed by its bare class and the other three by `<kind>:<detail>`,
            # which is how `DECLINE_MESSAGES` is keyed.
            declines.append((plan_id, decline_message(
                detail if kind == REFUSED else result)))

    return ApplyRunReport(
        applied=counts[APPLIED], refused=counts[REFUSED], stale=counts[STALE],
        paused=counts[PAUSED], failed=counts[FAILED],
        refusals_by_class=dict(details[REFUSED]),
        stale_by_trigger=dict(details[STALE]),
        paused_by_reason=dict(details[PAUSED]),
        failed_by_class=dict(details[FAILED]),
        declines=tuple(declines), not_attempted=tuple(missing))


# ---------------------------------------------------------------------------
# `66` §9's activity list.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ActivityRow:
    """One completed action, with `66` §9's eight attributes.

    *"Every completed action appears in a reviewable activity list with the
    source path, destination path, evidence summary, policy that authorized it,
    collision behavior, move time, current status, and undo availability."*
    """

    plan_id: str
    journal_entry_id: str
    source_path: str
    destination_path: str
    reason_and_evidence_summary: str
    #: The plan's `Required review policy`. `66` §8 makes the authorizing policy
    #: a FILING policy and no such record exists yet, which is what the flag
    #: below says out loud.
    authorizing_policy: str
    filing_policy_present: bool
    collision_behaviour: str
    moved_at: str
    status: str
    undo_available: bool
    #: When the move was reversed, or `None`. This is what separates *"you have
    #: already undone this"* from *"the period has passed"*, which are two
    #: different things to tell a person about the same unavailable button.
    reversed_at: str | None


def activity(conn: sqlite3.Connection, *, retention: UndoRetention | None,
             at: str) -> tuple[ActivityRow, ...]:
    """Every applied journal entry, newest last, with undo availability answered.

    An entry that has since been undone STAYS in the list. `66` §9 asks for every
    completed action, and a move the person reversed is still something that
    happened to their files.
    """
    if retention is None:
        raise NoRetentionSetting(
            "the activity list shows undo availability, and how long undo is "
            "offered for is the composition root's to state (`66` §11)")

    rows: list[ActivityRow] = []
    for record in conn.execute(
            "SELECT payload FROM move_journal WHERE entry_kind = ? "
            "ORDER BY record_id", (ENTRY_APPLIED,)):
        payload = json.loads(record[0])
        payload["directories_created_by_this_action"] = tuple(
            payload["directories_created_by_this_action"])
        entry = JournalEntry(**payload)
        plan = conn.execute(
            "SELECT payload FROM move_plans WHERE plan_id = ? "
            "ORDER BY record_id LIMIT 1", (entry.plan_id,)).fetchone()
        if plan is None:
            # A journal entry whose plan record is not in this database. It is
            # still a move that happened, so it is not dropped; what cannot be
            # read is left absent rather than invented.
            continue
        planned = json.loads(plan[0])
        execution = conn.execute(
            "SELECT payload FROM execution_records WHERE plan_id = ? "
            "ORDER BY record_id DESC LIMIT 1", (entry.plan_id,)).fetchone()
        outcome = json.loads(execution[0]) if execution is not None else None
        reversal = conn.execute(
            "SELECT time_of_execution FROM move_journal "
            "WHERE reverses_entry_id = ? ORDER BY record_id LIMIT 1",
            (entry.entry_id,)).fetchone()

        rows.append(ActivityRow(
            plan_id=entry.plan_id, journal_entry_id=entry.entry_id,
            source_path=entry.original_source_path,
            destination_path=entry.destination_path,
            reason_and_evidence_summary=planned["reason_and_evidence_summary"],
            authorizing_policy=planned["required_review_policy"],
            filing_policy_present=False,
            collision_behaviour=entry.collision_behaviour,
            moved_at=(entry.time_of_execution if outcome is None
                      else outcome["finished_at"]),
            status=(entry.post_move_verification_result if outcome is None
                    else outcome["result"]),
            undo_available=(reversal is None
                            and undo_offered(entry, retention=retention, at=at)),
            reversed_at=None if reversal is None else reversal[0]))
    return tuple(rows)
