"""F3 -- `66` §11's undo retention, §8.6's run legibility, `66` §9's activity list.

The three things `66` says about a move once it has happened: how long the person
can still take it back, what a run tells them about what it did and did not do,
and what the list of completed actions has to show.

**The retention period is the composition root's and P12 has no default for it.**
`66` §11 recommends 90 days and offers 30 days, one year, and retention until
manually cleared -- but that recommendation is a product decision that belongs in
`cli.py`, and `74` §8 Q8 is still open on whether adopting a new plan version
ends undo at all. So the four CHOICES are a closed vocabulary here and the
DURATION each one means arrives injected. Absent means refuse. The twin at the
bottom is what keeps that true: it reads the compiled modules of the part package
and fails on any 30, 90 or 365 hiding in one.
"""
from __future__ import annotations

import importlib
import pkgutil
import sqlite3
import types
from datetime import timedelta
from pathlib import Path

import pytest

import mutation
from mutation import vocabulary as v
from mutation.execute import JournalEntry, apply_plan, record_journal_entry
from mutation.retention import (
    ActivityRow, ApplyRunReport, NoRetentionSetting, RetentionPeriodRequired,
    UndoRetention, activity, apply_report, current_undo_retention,
    set_undo_retention, undo_offered,
)
from mutation.undo import entry_by_id, undo

from .conftest import CONSTRAINTS

DISPOSITION = ("The copy on the other drive was kept and is listed below; "
               "nothing was removed.")

#: What the composition root says each of `66` §11's choices means. Stated HERE,
#: in the test, exactly as `74` §6 requires: the 90 days is `66`'s recommended
#: default and belongs in `cli.py`, not in the part package.
PERIODS = {
    v.RETENTION_THIRTY_DAYS: timedelta(days=30),
    v.RETENTION_NINETY_DAYS: timedelta(days=90),
    v.RETENTION_ONE_YEAR: timedelta(days=365),
    v.RETENTION_UNTIL_MANUALLY_CLEARED: None,
}


def _entry(at="2026-05-01T00:00:00Z", **overrides):
    fields = dict(
        entry_id="j-1", entry_kind=v.ENTRY_APPLIED, reverses_entry_id=None,
        plan_id="p-1", plan_version="plan-1", file_id="f-1",
        hash_algorithm="sha256", original_source_path="/a/Syllabus.pdf",
        destination_path="/b/Syllabus.pdf", content_hash_at_movement="h1",
        collision_behaviour=v.PRESERVE_BOTH_DETERMINISTIC_SUFFIX,
        post_move_verification_result="match", source_volume="vol-main",
        destination_volume="vol-main", execution_mode=v.ATOMIC_RENAME,
        directories_created_by_this_action=(),
        intended_display_name="Syllabus.pdf",
        filesystem_safe_name="Syllabus.pdf", time_of_execution=at)
    fields.update(overrides)
    return JournalEntry(**fields)


def _apply(conn, plan, fixture_root, clock, ids, **overrides):
    kwargs = dict(
        legal_destination_ids=frozenset({plan.requested_destination_node}),
        source_root=fixture_root, destination_root=fixture_root,
        constraints=CONSTRAINTS,
        suffix_for=lambda stem, attempt: f"{stem} ({attempt})",
        max_suffix_attempts=8, extra_protected=None,
        conflict_copies=lambda path: (), dataless_of=lambda path: False,
        normalize_filename=lambda name: name, scan_state="included",
        materialized=True, component_version="p12-test", user_id=None,
        approval_for=lambda plan_id: None,
        unverified_copy_disposition=DISPOSITION, now=clock, mint_id=ids)
    kwargs.update(overrides)
    return apply_plan(conn, plan, **kwargs)


# ---------------------------------------------------------------------------
# F3's named test.
# ---------------------------------------------------------------------------


def test_the_retention_period_is_injected_and_absent_means_refuse(p12_conn):
    """Four ways the period can be absent, and all four refuse.

    Nothing here supplies a fallback, because a fallback is what a person would
    later discover their undo window had been silently set to.
    """
    # 1. A database nobody has configured has no retention setting at all --
    #    not a default one.
    assert current_undo_retention(p12_conn) is None

    # 2. Asking whether undo is still offered without one refuses.
    with pytest.raises(NoRetentionSetting):
        undo_offered(_entry(), retention=None, at="2026-08-29T00:00:00Z")

    # 3. A bounded choice with no period is refused at construction. `66` §11
    #    names "30 days"; how long 30 days is is not P12's to know.
    with pytest.raises(RetentionPeriodRequired):
        UndoRetention(choice=v.RETENTION_THIRTY_DAYS, period=None)

    # 4. And the unbounded choice refuses a period, because "until manually
    #    cleared" with an expiry would be two different promises at once.
    with pytest.raises(RetentionPeriodRequired):
        UndoRetention(choice=v.RETENTION_UNTIL_MANUALLY_CLEARED,
                      period=timedelta(days=90))

    # The period the composition root states is the one that governs -- and a
    # different root stating a different period governs differently, which is
    # what "injected" means.
    entry = _entry(at="2026-05-01T00:00:00Z")
    short = UndoRetention(choice=v.RETENTION_THIRTY_DAYS,
                          period=PERIODS[v.RETENTION_THIRTY_DAYS])
    long = UndoRetention(choice=v.RETENTION_ONE_YEAR,
                         period=PERIODS[v.RETENTION_ONE_YEAR])
    assert undo_offered(entry, retention=short, at="2026-08-29T00:00:00Z") is False
    assert undo_offered(entry, retention=long, at="2026-08-29T00:00:00Z") is True


# ---------------------------------------------------------------------------
# The negative twin.
# ---------------------------------------------------------------------------


def _mutation_modules():
    package = Path(mutation.__file__).resolve().parent
    for info in pkgutil.iter_modules([str(package)]):
        yield importlib.import_module(f"mutation.{info.name}")


def _code_objects(value, seen=None):
    """Every code object reachable from a module attribute, nested ones included."""
    seen = set() if seen is None else seen
    stack = [value]
    while stack:
        item = stack.pop()
        code = getattr(item, "__code__", None)
        if code is not None:
            item = code
        if not isinstance(item, types.CodeType) or id(item) in seen:
            continue
        seen.add(id(item))
        yield item
        stack.extend(constant for constant in item.co_consts
                     if isinstance(constant, types.CodeType))


def _numbers_in(module):
    """Every number the compiled module holds, at module level or in any code.

    Runtime introspection over the imported module and its code objects, not a
    text search: a `90` written as `int("9" + "0")` carries no digit a grep would
    find, and a comment mentioning ninety is not a default.
    """
    found: list[tuple[str, object]] = []
    for name, value in vars(module).items():
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            found.append((name, value))
        if isinstance(value, dict):
            found.extend((name, item) for item in value.values()
                         if isinstance(item, (int, float))
                         and not isinstance(item, bool))
        for code in _code_objects(value):
            found.extend(
                (f"{name}:{code.co_name}", constant)
                for constant in code.co_consts
                if isinstance(constant, (int, float))
                and not isinstance(constant, bool))
    return found


def test_no_retention_default_of_ninety_days_is_hard_coded_in_the_part_package():
    """`66` §11's 90 days is the composition root's, and so are 30 and 365.

    Two ways a default could get in: as a number, and as a name. Both are
    checked, because `DEFAULT_UNDO_RETENTION = "ninety_days"` carries no digit
    at all and would set the person's undo window just as firmly.
    """
    periods = {30, 90, 365, 30.0, 90.0, 365.0}
    offenders: list[str] = []
    for module in _mutation_modules():
        offenders.extend(
            f"{module.__name__}.{where} = {number!r}"
            for where, number in _numbers_in(module) if number in periods)
        offenders.extend(
            f"{module.__name__}.{name} names a default retention"
            for name in vars(module)
            if "RETENTION" in name.upper() and (
                "DEFAULT" in name.upper() or "RECOMMENDED" in name.upper()))
    assert offenders == [], (
        "the retention period is `66` §11's recommendation and belongs in "
        f"cli.py, the composition root: {offenders}")


# ---------------------------------------------------------------------------
# The four choices, and the setting the person changes.
# ---------------------------------------------------------------------------


def test_the_four_choices_are_66s_own_four():
    assert v.UNDO_RETENTION_CHOICES == (
        v.RETENTION_THIRTY_DAYS, v.RETENTION_NINETY_DAYS,
        v.RETENTION_ONE_YEAR, v.RETENTION_UNTIL_MANUALLY_CLEARED)


def test_the_person_can_select_each_of_the_four(p12_conn):
    for index, choice in enumerate(v.UNDO_RETENTION_CHOICES):
        retention = UndoRetention(choice=choice, period=PERIODS[choice])
        set_undo_retention(p12_conn, retention, user_id="user-1",
                           set_at=f"2026-08-29T0{index}:00:00Z",
                           record_id=f"ret-{index}")
        assert current_undo_retention(p12_conn) == retention


def test_a_changed_setting_supersedes_and_the_old_row_is_retained(p12_conn):
    for index, choice in enumerate((v.RETENTION_THIRTY_DAYS,
                                    v.RETENTION_ONE_YEAR)):
        set_undo_retention(
            p12_conn, UndoRetention(choice=choice, period=PERIODS[choice]),
            user_id="user-1", set_at=f"2026-08-29T0{index}:00:00Z",
            record_id=f"ret-{index}")
    rows = p12_conn.execute(
        "SELECT retention_choice, supersedes, superseded_by FROM undo_retention "
        "ORDER BY set_at").fetchall()
    assert [row[0] for row in rows] == [v.RETENTION_THIRTY_DAYS,
                                        v.RETENTION_ONE_YEAR]
    assert rows[0]["superseded_by"] == "ret-1"
    assert rows[1]["supersedes"] == "ret-0"
    assert rows[1]["superseded_by"] is None


def test_an_unknown_choice_is_refused(p12_conn):
    with pytest.raises(v.OutOfVocabulary):
        UndoRetention(choice="forever_and_ever", period=timedelta(days=90))


def test_until_manually_cleared_never_expires():
    retention = UndoRetention(choice=v.RETENTION_UNTIL_MANUALLY_CLEARED,
                              period=None)
    assert undo_offered(_entry(at="2019-01-01T00:00:00Z"), retention=retention,
                        at="2026-08-29T00:00:00Z") is True


def test_the_last_day_of_the_period_is_still_inside_it():
    retention = UndoRetention(choice=v.RETENTION_NINETY_DAYS,
                              period=PERIODS[v.RETENTION_NINETY_DAYS])
    assert undo_offered(_entry(at="2026-05-31T00:00:00Z"), retention=retention,
                        at="2026-08-29T00:00:00Z") is True
    assert undo_offered(_entry(at="2026-05-30T00:00:00Z"), retention=retention,
                        at="2026-08-29T00:00:00Z") is False


def test_the_journal_is_never_purged_by_a_shorter_retention(p12_conn):
    """`66` §11: the product *"should never silently purge active-policy history
    in a way that makes a recent move impossible to understand or review."* The
    setting governs what is OFFERED; the record stays either way."""
    record_journal_entry(p12_conn, _entry(at="2019-01-01T00:00:00Z"),
                         record_id="rec-1")
    set_undo_retention(
        p12_conn, UndoRetention(choice=v.RETENTION_THIRTY_DAYS,
                                period=PERIODS[v.RETENTION_THIRTY_DAYS]),
        user_id="user-1", set_at="2026-08-29T00:00:00Z", record_id="ret-0")
    assert p12_conn.execute(
        "SELECT COUNT(*) FROM move_journal").fetchone()[0] == 1
    with pytest.raises(sqlite3.IntegrityError):
        p12_conn.execute("DELETE FROM move_journal")


def test_a_late_undo_is_not_refused_by_the_setting(p12_conn, planned,
                                                   fixture_root, clock, ids):
    """`74` §8 Q8 is the owner's. `66` §11 says how long undo is OFFERED and no
    sentence anywhere says a late reversal must be refused, so P12 stops offering
    and does not start refusing. The judgement is recorded here rather than
    buried in a branch."""
    plan, source = planned
    _apply(p12_conn, plan, fixture_root, clock, ids)
    entry = entry_by_id(p12_conn, p12_conn.execute(
        "SELECT entry_id FROM move_journal WHERE plan_id = ?",
        (plan.plan_id,)).fetchone()[0])
    retention = UndoRetention(choice=v.RETENTION_THIRTY_DAYS,
                              period=PERIODS[v.RETENTION_THIRTY_DAYS])
    assert undo_offered(entry, retention=retention,
                        at="2027-08-29T00:00:00Z") is False
    verdict = undo(p12_conn, entry.entry_id, constraints=CONSTRAINTS,
                   unverified_copy_disposition=DISPOSITION,
                   normalize_filename=lambda name: name, scan_state="included",
                   materialized=True, component_version="p12-test",
                   user_id=None, now=clock, mint_id=ids)
    assert verdict.verdict == v.REVERSED


# ---------------------------------------------------------------------------
# §8.6's run legibility.
# ---------------------------------------------------------------------------


def test_an_applied_run_reports_one_applied_and_nothing_deferred(
        p12_conn, planned, fixture_root, clock, ids):
    plan, _ = planned
    _apply(p12_conn, plan, fixture_root, clock, ids)
    report = apply_report(p12_conn, plan_ids=(plan.plan_id,))
    assert (report.applied, report.refused, report.stale, report.paused,
            report.failed) == (1, 0, 0, 0, 0)
    assert report.total == 1
    assert report.declines == ()


def test_a_stale_run_names_the_trigger_and_carries_its_sentence(
        p12_conn, planned, fixture_root, clock, ids):
    plan, source = planned
    source.write_bytes(b"changed after the preview")
    _apply(p12_conn, plan, fixture_root, clock, ids)
    report = apply_report(p12_conn, plan_ids=(plan.plan_id,))
    assert report.stale == 1
    assert report.stale_by_trigger == {v.CONTENT_HASH_DIFFERS: 1}
    assert report.declines == (
        (plan.plan_id,
         v.decline_message(f"{v.STALE}:{v.CONTENT_HASH_DIFFERS}")),)


def test_deferred_work_is_never_folded_into_the_applied_count(
        p12_conn, planned, fixture_root, clock, ids):
    """§8.6: deferred work is visible rather than presented as completed."""
    plan, source = planned
    source.write_bytes(b"changed after the preview")
    _apply(p12_conn, plan, fixture_root, clock, ids)
    report = apply_report(p12_conn, plan_ids=(plan.plan_id,))
    assert report.applied == 0
    assert report.total == (report.applied + report.refused + report.stale
                            + report.paused + report.failed)


def test_a_plan_that_was_never_attempted_is_absent_rather_than_counted_as_done(
        p12_conn, planned, fixture_root, clock, ids):
    plan, _ = planned
    report = apply_report(p12_conn, plan_ids=(plan.plan_id,))
    assert report.total == 0
    assert report.not_attempted == (plan.plan_id,)


# ---------------------------------------------------------------------------
# `66` §9's activity list.
# ---------------------------------------------------------------------------


def test_every_completed_action_carries_66_9s_eight_attributes(
        p12_conn, planned, fixture_root, clock, ids):
    plan, source = planned
    record = _apply(p12_conn, plan, fixture_root, clock, ids)
    retention = UndoRetention(choice=v.RETENTION_NINETY_DAYS,
                              period=PERIODS[v.RETENTION_NINETY_DAYS])

    rows = activity(p12_conn, retention=retention, at="2026-08-29T02:00:00Z")

    assert len(rows) == 1
    row = rows[0]
    assert row.source_path == str(source)
    assert row.destination_path == record.final_destination_path
    assert row.reason_and_evidence_summary == plan.reason_and_evidence_summary
    assert row.authorizing_policy == plan.required_review_policy
    assert row.collision_behaviour == plan.collision_policy
    assert row.moved_at == record.finished_at
    assert row.status == v.APPLIED
    assert row.undo_available is True
    assert row.reversed_at is None


def test_the_activity_list_says_no_filing_policy_authorized_it_rather_than_faking_one(
        p12_conn, planned, fixture_root, clock, ids):
    """`66` §8 makes the authorizing policy a FILING policy, and the filing-policy
    layer is item 5 of `66` §22's release order -- after P12. The gap is carried,
    not filled."""
    plan, _ = planned
    _apply(p12_conn, plan, fixture_root, clock, ids)
    retention = UndoRetention(choice=v.RETENTION_NINETY_DAYS,
                              period=PERIODS[v.RETENTION_NINETY_DAYS])
    row = activity(p12_conn, retention=retention,
                   at="2026-08-29T02:00:00Z")[0]
    assert row.filing_policy_present is False


def test_an_undone_action_is_still_in_the_list_and_no_longer_offers_undo(
        p12_conn, planned, fixture_root, clock, ids):
    plan, source = planned
    _apply(p12_conn, plan, fixture_root, clock, ids)
    entry = entry_by_id(p12_conn, p12_conn.execute(
        "SELECT entry_id FROM move_journal WHERE plan_id = ?",
        (plan.plan_id,)).fetchone()[0])
    undo(p12_conn, entry.entry_id, constraints=CONSTRAINTS,
         unverified_copy_disposition=DISPOSITION,
         normalize_filename=lambda name: name, scan_state="included",
         materialized=True, component_version="p12-test", user_id=None,
         now=clock, mint_id=ids)
    retention = UndoRetention(choice=v.RETENTION_NINETY_DAYS,
                              period=PERIODS[v.RETENTION_NINETY_DAYS])

    rows = activity(p12_conn, retention=retention, at="2026-08-29T03:00:00Z")

    assert len(rows) == 1, "an undone move is still something that happened"
    assert rows[0].undo_available is False
    assert rows[0].reversed_at is not None


def test_undo_stops_being_offered_once_the_period_has_passed(
        p12_conn, planned, fixture_root, clock, ids):
    plan, _ = planned
    _apply(p12_conn, plan, fixture_root, clock, ids)
    retention = UndoRetention(choice=v.RETENTION_THIRTY_DAYS,
                              period=PERIODS[v.RETENTION_THIRTY_DAYS])
    row = activity(p12_conn, retention=retention,
                   at="2027-08-29T00:00:00Z")[0]
    assert row.undo_available is False
    assert row.reversed_at is None


def test_the_activity_list_refuses_to_render_without_a_retention_setting(
        p12_conn, planned, fixture_root, clock, ids):
    plan, _ = planned
    _apply(p12_conn, plan, fixture_root, clock, ids)
    with pytest.raises(NoRetentionSetting):
        activity(p12_conn, retention=None, at="2026-08-29T02:00:00Z")
