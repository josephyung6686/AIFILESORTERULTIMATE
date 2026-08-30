"""F2 -- Contract out §7's directory reversal. Conditional, deepest-first, never
a conflict, and never able to remove anything of the person's.

Creating a folder for a frozen node is a mutation P12 performed, so §8.3 makes it
reversible too -- but on the same conditional terms as the file, and with a much
narrower licence. A created directory is removed **only** when all three hold:
this journal entry recorded creating it, it is still empty, and no other journal
entry that is still applied moved a file into it or beneath it.

The twin is about the third word in *"a directory P12 did not create is never a
candidate"*. An implementation that simply walked upward removing empty parents
would pass every assertion about the chain it did create -- the chain would be
gone, the file would be home, the verdict would read `reversed` -- and would have
removed a folder the person made. So the twin watches `os.rmdir` at run time and
requires every path it was ever handed to be one of the paths the journal entry
itself records.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from mutation import vocabulary as v
from mutation.execute import apply_plan
from mutation.undo import entry_by_id, undo

from .conftest import CONSTRAINTS, plan_a_move

DISPOSITION = ("The copy on the other drive was kept and is listed below; "
               "nothing was removed.")


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


def _undo(conn, entry_id, clock, ids, **overrides):
    kwargs = dict(
        constraints=CONSTRAINTS, unverified_copy_disposition=DISPOSITION,
        normalize_filename=lambda name: name, scan_state="included",
        materialized=True, component_version="p12-test", user_id=None,
        now=clock, mint_id=ids)
    kwargs.update(overrides)
    return undo(conn, entry_id, **kwargs)


def _entry(conn, plan_id):
    row = conn.execute(
        "SELECT entry_id FROM move_journal WHERE plan_id = ? AND entry_kind = ?",
        (plan_id, v.ENTRY_APPLIED)).fetchone()
    assert row is not None
    return entry_by_id(conn, row[0])


@pytest.fixture()
def applied(p12_conn, planned, fixture_root, clock, ids):
    """One move that created a two-level chain: `Coursework/PHYS1401`."""
    plan, source = planned
    record = _apply(p12_conn, plan, fixture_root, clock, ids)
    assert record.result == v.APPLIED
    shallow, deep = record.directories_created_by_this_action
    return plan, source, record, _entry(p12_conn, plan.plan_id), Path(shallow), \
        Path(deep)


def _second_move_into(conn, landscape, fixture_root, clock, ids):
    """A second file, filed into the same deep directory by its own entry."""
    plan, source = plan_a_move(conn, landscape, ids,
                               volume_of=lambda path: "vol-main",
                               name="Homework.pdf")
    record = _apply(conn, plan, fixture_root, clock, ids)
    assert record.result == v.APPLIED
    return plan, record


# ---------------------------------------------------------------------------
# F2's named test.
# ---------------------------------------------------------------------------


def test_a_created_directory_is_removed_only_when_empty_and_unreferenced(
        p12_conn, applied, landscape, fixture_root, clock, ids):
    """The three conditions, one at a time, each on its own fixture.

    All three hold -> `removed`. Something else is in the folder -> `not_empty`.
    Another applied entry filed a file beneath it -> `referenced_by_other_entry`.
    In every case the FILE reversal succeeded, because a retained folder is a
    fact about the folder and not a failure of the undo.
    """
    plan, source, record, entry, shallow, deep = applied

    verdict = _undo(p12_conn, entry.entry_id, clock, ids)
    assert verdict.verdict == v.REVERSED
    assert verdict.directory_outcomes[0] == (str(deep), v.DIR_REMOVED)
    assert verdict.directory_outcomes[1] == (str(shallow), v.DIR_REMOVED)
    assert not deep.exists() and not shallow.exists()
    assert source.read_bytes() == b"PHYS1401 syllabus"


def test_a_directory_that_has_since_received_a_file_is_retained_with_its_reason(
        p12_conn, applied, clock, ids):
    plan, source, record, entry, shallow, deep = applied
    keeper = deep / "Someone elses notes.pdf"
    keeper.write_bytes(b"not P12's")

    verdict = _undo(p12_conn, entry.entry_id, clock, ids)

    assert verdict.verdict == v.REVERSED, (
        "a retained directory is never a conflict; the file reversal succeeded")
    assert verdict.directory_outcomes[0] == (str(deep), v.DIR_RETAINED_NOT_EMPTY)
    assert keeper.read_bytes() == b"not P12's"
    assert source.read_bytes() == b"PHYS1401 syllabus"


def test_a_directory_another_applied_entry_filed_beneath_is_retained_as_referenced(
        p12_conn, applied, landscape, fixture_root, clock, ids):
    """`retained:referenced_by_other_entry` is reachable, and this is how.

    The reference is asked BEFORE emptiness, which is what gives the outcome a
    life of its own: asked afterwards it would be shadowed by `not_empty` in
    every case that can arise, and a vocabulary member nothing can produce is
    indistinguishable from one that does not work.
    """
    plan, source, record, entry, shallow, deep = applied
    _second_move_into(p12_conn, landscape, fixture_root, clock, ids)

    verdict = _undo(p12_conn, entry.entry_id, clock, ids)

    assert verdict.verdict == v.REVERSED
    assert verdict.directory_outcomes[0] == (str(deep), v.DIR_RETAINED_REFERENCED)
    assert deep.exists()


def test_a_reference_from_an_entry_that_has_itself_been_undone_does_not_retain(
        p12_conn, applied, landscape, fixture_root, clock, ids):
    """An entry whose own move has been undone has no file there any more, so it
    must not go on holding a directory."""
    plan, source, record, entry, shallow, deep = applied
    second_plan, _ = _second_move_into(p12_conn, landscape, fixture_root, clock,
                                       ids)
    _undo(p12_conn, _entry(p12_conn, second_plan.plan_id).entry_id, clock, ids)

    verdict = _undo(p12_conn, entry.entry_id, clock, ids)

    assert verdict.directory_outcomes[0] == (str(deep), v.DIR_REMOVED)
    assert not deep.exists()


def test_removal_stops_at_the_first_directory_that_fails_a_condition(
        p12_conn, applied, clock, ids):
    plan, source, record, entry, shallow, deep = applied
    (shallow / "stray.txt").write_bytes(b"in the parent, not the child")

    verdict = _undo(p12_conn, entry.entry_id, clock, ids)

    assert verdict.directory_outcomes[0] == (str(deep), v.DIR_REMOVED)
    assert verdict.directory_outcomes[1] == (str(shallow),
                                             v.DIR_RETAINED_NOT_EMPTY)
    assert len(verdict.directory_outcomes) == len(
        entry.directories_created_by_this_action)
    assert shallow.exists()


def test_the_boundary_directory_is_reported_rather_than_the_report_just_ending(
        p12_conn, applied, landscape, clock, ids):
    """The whole chain went, and the walk stopped at a folder P12 did not make.
    Saying so is what makes the stopping point legible."""
    plan, source, record, entry, shallow, deep = applied
    verdict = _undo(p12_conn, entry.entry_id, clock, ids)
    assert verdict.directory_outcomes[-1] == (
        str(landscape["root_documents"]), v.DIR_RETAINED_NOT_CREATED)
    assert landscape["root_documents"].exists()


def test_a_conflicted_undo_reverses_no_directory_at_all(
        p12_conn, applied, clock, ids):
    plan, source, record, entry, shallow, deep = applied
    Path(record.final_destination_path).write_bytes(b"edited after filing")

    verdict = _undo(p12_conn, entry.entry_id, clock, ids)

    assert verdict.verdict == v.CONFLICT_DESTINATION_CONTENT_CHANGED
    assert verdict.directory_outcomes == ()
    assert deep.exists() and shallow.exists()


def test_the_outcomes_are_recorded_on_the_undo_event(p12_conn, applied, clock,
                                                     ids):
    plan, source, record, entry, shallow, deep = applied
    verdict = _undo(p12_conn, entry.entry_id, clock, ids)
    payload = json.loads(p12_conn.execute(
        "SELECT explanation FROM events WHERE event_type = ?",
        (v.UNDO,)).fetchone()[0])
    assert [tuple(pair) for pair in payload["directory_outcomes"]] == list(
        verdict.directory_outcomes)


def test_every_directory_reversal_outcome_is_reachable_from_this_suite():
    """The four are a closed set and each of the first three is produced above;
    a member nothing can produce would be a member that does not work."""
    assert set(v.DIRECTORY_REVERSAL_OUTCOMES) == {
        v.DIR_REMOVED, v.DIR_RETAINED_NOT_EMPTY, v.DIR_RETAINED_REFERENCED,
        v.DIR_RETAINED_NOT_CREATED}


# ---------------------------------------------------------------------------
# The negative twin.
# ---------------------------------------------------------------------------


def test_a_directory_p12_did_not_create_is_never_a_candidate_for_removal(
        p12_conn, applied, landscape, fixture_root, clock, ids, monkeypatch):
    """Watched at the system call, not asserted about the outcome list.

    An implementation that walked upward removing every empty parent would
    produce the same outcomes for the chain it did create, and would take the
    person's own empty folder with it on the way past. What separates the two is
    the set of paths `os.rmdir` was ever handed, so that is what this records --
    and it must be a subset of the paths this journal entry itself claims to
    have created.
    """
    plan, source, record, entry, shallow, deep = applied
    mine = set(entry.directories_created_by_this_action)

    # A folder the person made, empty, sitting where an upward walk would meet it.
    theirs = landscape["root_documents"] / "Scans"
    theirs.mkdir()
    # And one the person made INSIDE the chain P12 created, so that a walk which
    # trusted the filesystem rather than the record would find it first.
    inside = deep / "Old versions"
    inside.mkdir()

    removed: list[str] = []
    real_rmdir = os.rmdir

    def watched(path, *args, **kwargs):
        removed.append(str(path))
        return real_rmdir(path, *args, **kwargs)

    monkeypatch.setattr(os, "rmdir", watched)
    verdict = _undo(p12_conn, entry.entry_id, clock, ids)

    assert set(removed) <= mine, (
        f"undo tried to remove a directory P12 did not create: "
        f"{sorted(set(removed) - mine)}")
    assert theirs.exists() and inside.exists()
    assert verdict.verdict == v.REVERSED
    assert verdict.directory_outcomes[0] == (str(deep), v.DIR_RETAINED_NOT_EMPTY)


def test_no_user_file_is_ever_removed_by_a_directory_reversal(
        p12_conn, applied, clock, ids):
    """§7.11 is untouched: an empty directory contains no file, and `os.rmdir`
    refuses a non-empty one at the system call rather than at the check above it.
    """
    plan, source, record, entry, shallow, deep = applied
    keeper = deep / "important.txt"
    keeper.write_bytes(b"a user file")

    _undo(p12_conn, entry.entry_id, clock, ids)

    assert keeper.read_bytes() == b"a user file"
