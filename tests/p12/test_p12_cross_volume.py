"""E2 -- copy and delete across two volumes, and what V4 is actually for.

§8.2: *"for a cross-volume move, the destination copy must be hashed and
confirmed before the source can be removed."* That sentence is a rule about
ORDER, and the order is the only thing standing between a person and a lost
file: a source removed on the strength of a copy nobody hashed is a file the
product cannot prove it still has.

The unverified copy is the harder half, and it is `74` §8 **Q7**, which is open.
Two rules bind at once and both say the same thing: §8.2 forbids removing the
source, §7.11 forbids deleting a user's file. So BOTH paths survive, and where
the copy then lives, what it is called and how the person sees it is the
composition root's to state. P12 refuses to begin a cross-volume copy at all
until it has been told, because a file it creates and cannot account for is
worse than a move it did not make.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mutation import cross_volume
from mutation import vocabulary as v
from mutation.cross_volume import UnverifiedCopyDispositionRequired
from mutation.execute import JournalEntry, apply_plan

from .conftest import CONSTRAINTS, plan_a_move

#: The disposition sentence the composition root owes P12 (`74` §8 Q7). It is a
#: STAND-IN: this suite states one so that the seam can be exercised, and states
#: it here rather than in `src/` so that nothing in the part package carries an
#: answer to an open question.
DISPOSITION = ("The copy on the other drive was kept and is listed below; "
               "nothing was removed.")


def _two_volumes(landscape):
    """The oracle, stated rather than derived. `Documents` is the destination
    anchor and answers one volume; everything else answers the other."""
    documents = landscape["root_documents"]
    return lambda path: "vol-archive" if Path(path) == documents else "vol-home"


@pytest.fixture()
def planned_across_volumes(p12_conn, landscape, ids):
    return plan_a_move(p12_conn, landscape, ids,
                       volume_of=_two_volumes(landscape))


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


def _refuse_v4(monkeypatch):
    """Make V4 answer `False` without touching the bytes on disk.

    Only a real I/O fault produces a byte-identical copy that fails its own
    hash, so the UNVERIFIED condition is injected at P1's answer -- which is the
    input this twin is about -- and everything downstream of it is the real code.
    """
    monkeypatch.setattr(
        cross_volume, "confirm_cross_volume_copy",
        lambda conn, **kwargs: False)


# --- E2's named test --------------------------------------------------------


def test_the_source_is_not_removed_until_confirm_cross_volume_copy_returned_true(
        p12_conn, planned_across_volumes, fixture_root, clock, ids,
        monkeypatch):
    plan, source = planned_across_volumes
    assert plan.expected_source_volume != plan.expected_destination_volume

    seen: list[str] = []
    real = cross_volume.confirm_cross_volume_copy

    def watched(conn, **kwargs):
        seen.append("v4")
        assert source.exists(), (
            "the source was already gone when V4 was asked; V4 exists to be "
            "asked BEFORE the removal, not to report on one")
        return real(conn, **kwargs)

    monkeypatch.setattr(cross_volume, "confirm_cross_volume_copy", watched)
    record = _apply(p12_conn, plan, fixture_root, clock, ids)

    assert seen == ["v4"]
    assert record.mode == v.CROSS_VOLUME_COPY_AND_DELETE
    assert record.destination_confirmed_pre_removal is True
    assert record.result == v.APPLIED
    assert not source.exists()
    assert Path(record.final_destination_path).read_bytes() == (
        b"PHYS1401 syllabus")


def test_an_unverified_destination_copy_leaves_both_paths_intact_and_records_the_state(
        p12_conn, planned_across_volumes, fixture_root, clock, ids,
        monkeypatch):
    """The negative twin. §8.2 forbids removing the source; §7.11 forbids
    deleting a file. Both bind, so both paths are still there afterwards."""
    plan, source = planned_across_volumes
    _refuse_v4(monkeypatch)

    record = _apply(p12_conn, plan, fixture_root, clock, ids)

    assert record.result == f"{v.FAILED}:{v.V4_DESTINATION_UNCONFIRMED}"
    assert record.destination_confirmed_pre_removal is False
    assert source.exists(), "§8.2: the source is not removed on an unconfirmed copy"
    assert source.read_bytes() == b"PHYS1401 syllabus"

    copy = Path(plan.resolved_destination_path)
    assert copy.exists(), "§7.11: the copy P12 made is not deleted either"

    # And the state is RECORDED, not merely survived. The execution record
    # carries Contract out §5's own field list and no more -- `Final
    # destination path` names the copy, `Destination confirmed pre-removal` is
    # False, and the source path is on the plan the record joins to, so adding
    # a fourteenth field here would be P12 rewriting the SPEC to say something
    # the plan already says. What the PERSON reads is the event, and the event
    # carries both paths and the composition root's sentence.
    assert record.final_destination_path == str(copy)
    stored = p12_conn.execute(
        "SELECT payload FROM execution_records WHERE plan_id = ?",
        (plan.plan_id,)).fetchone()
    assert str(copy) in stored[0]
    assert plan.expected_source_path == str(source)
    failed = p12_conn.execute(
        "SELECT explanation FROM events WHERE event_type = ?",
        (v.FAILED_MOVE,)).fetchall()
    assert len(failed) == 1
    assert DISPOSITION in failed[0][0]
    assert str(source) in failed[0][0] and str(copy) in failed[0][0]


# --- the rest of E2 ---------------------------------------------------------


def test_q7s_disposition_has_no_default_and_absence_refuses_before_any_copy(
        p12_conn, planned_across_volumes, fixture_root, clock, ids):
    plan, source = planned_across_volumes
    with pytest.raises(UnverifiedCopyDispositionRequired):
        _apply(p12_conn, plan, fixture_root, clock, ids,
               unverified_copy_disposition=None)
    assert source.exists()
    assert not Path(plan.resolved_destination_path).exists()
    assert not Path(plan.resolved_destination_path).parent.exists(), (
        "not one directory was created either; the refusal lands before any "
        "mutation, not part-way through one")
    assert p12_conn.execute(
        "SELECT COUNT(*) FROM execution_records").fetchone()[0] == 0


def test_a_same_volume_plan_never_asks_v4_at_all(
        p12_conn, planned, fixture_root, clock, ids, monkeypatch):
    """`destination_confirmed_pre_removal` is `None` on a rename, and `None`
    is not a failure to confirm -- it is a question that was never put."""
    plan, _ = planned
    monkeypatch.setattr(
        cross_volume, "confirm_cross_volume_copy",
        lambda conn, **kwargs: pytest.fail("V4 was asked about a rename"))
    record = _apply(p12_conn, plan, fixture_root, clock, ids,
                    unverified_copy_disposition=None)
    assert record.mode == v.ATOMIC_RENAME
    assert record.destination_confirmed_pre_removal is None
    assert record.result == v.APPLIED


def test_a_confirmed_cross_volume_move_journals_its_mode_and_reaches_v3(
        p12_conn, planned_across_volumes, fixture_root, clock, ids):
    plan, source = planned_across_volumes
    record = _apply(p12_conn, plan, fixture_root, clock, ids)
    entry = JournalEntry.for_plan(p12_conn, plan.plan_id)
    assert entry is not None
    assert entry.execution_mode == v.CROSS_VOLUME_COPY_AND_DELETE
    assert entry.source_volume == plan.expected_source_volume
    assert entry.destination_volume == plan.expected_destination_volume
    assert entry.original_source_path == str(source)
    assert record.hash_after_completion == "match"


def test_an_unverified_run_writes_no_journal_entry(
        p12_conn, planned_across_volumes, fixture_root, clock, ids,
        monkeypatch):
    """Nothing moved, so there is nothing to reverse. The journal is the undo
    record for a move that happened, and inventing an entry for one that did not
    would offer the person an undo that would delete their surviving copy."""
    plan, _ = planned_across_volumes
    _refuse_v4(monkeypatch)
    _apply(p12_conn, plan, fixture_root, clock, ids)
    assert JournalEntry.for_plan(p12_conn, plan.plan_id) is None
