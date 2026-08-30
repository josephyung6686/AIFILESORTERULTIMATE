"""E1 -- the same-volume transaction: V1, V2, the move, V3, and the journal.

The trap this suite exists for is P1's, and it is not obvious from either SPEC.
`verify_content(conn, file_id, expected_hash)` hashes whatever sits at
`files.current_path` (`database_agent/verify.py:45-49`). It takes NO path. So V3
-- *"after completing the action"* (§8.2) -- can only be asked once P1 has been
told the file lives at the destination. Ask it a moment earlier and P1 hashes the
source path that the rename just emptied, `hash_file` raises `OSError`,
`verify_content` swallows it and returns `"mismatch"`, and a move that completed
perfectly is recorded as `failed:v3_hash_mismatch`.

`test_v3_before_observe_path_reports_a_false_mismatch` reproduces exactly that
against P1's own primitives, so the trap is demonstrated rather than asserted,
and then requires the real executor not to have fallen into it.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, observe_path
from database_agent.verify import VerificationPoint, verify_content

from mutation import vocabulary as v
from mutation.execute import ExecutionRecord, JournalEntry, apply_plan

from .conftest import CONSTRAINTS


def _apply(conn, plan, **overrides):
    kwargs = dict(
        legal_destination_ids=frozenset({plan.requested_destination_node}),
        constraints=CONSTRAINTS,
        suffix_for=lambda stem, attempt: f"{stem} ({attempt})",
        max_suffix_attempts=8,
        extra_protected=None,
        conflict_copies=lambda path: (),
        dataless_of=lambda path: False,
        normalize_filename=lambda name: name,
        scan_state="included",
        materialized=True,
        component_version="p12-test",
        user_id=None,
    )
    kwargs.update(overrides)
    return apply_plan(conn, plan, **kwargs)


def _hashing_events(conn):
    return [
        (row["event_id"], json.loads(row["explanation"]))
        for row in conn.execute(
            "SELECT event_id, explanation FROM events WHERE event_type = 'hashing' "
            "ORDER BY event_id")
    ]


def _point(conn, name: str) -> int:
    for event_id, explanation in _hashing_events(conn):
        if explanation.get("point") == name:
            return event_id
    raise AssertionError(f"no {name} verification was recorded at all")


def _stat_observation(conn) -> int:
    row = conn.execute(
        "SELECT event_id FROM events WHERE event_type = 'stat observation' "
        "ORDER BY event_id DESC LIMIT 1").fetchone()
    assert row is not None, "P1 never observed the file at its new path"
    return row["event_id"]


# --- E1's named test --------------------------------------------------------


def test_v3_runs_after_observe_path_has_moved_current_path_to_the_destination(
        p12_conn, planned, fixture_root, clock, ids):
    plan, source = planned
    record = _apply(p12_conn, plan, source_root=fixture_root,
                    destination_root=fixture_root, now=clock, mint_id=ids)

    assert record.result == v.APPLIED
    assert record.mode == v.ATOMIC_RENAME
    assert record.hash_after_completion == "match"
    assert not source.exists()
    assert Path(record.final_destination_path).read_bytes() == b"PHYS1401 syllabus"

    # P1 knows the file at its new home, and knew it BEFORE V3 was asked.
    assert get_file(p12_conn, plan.file_id)["current_path"] == (
        record.final_destination_path)
    assert _stat_observation(p12_conn) < _point(p12_conn, "V3")


def test_v3_before_observe_path_reports_a_false_mismatch(
        p12_conn, planned, fixture_root, clock, ids):
    """The negative twin. Half demonstration, half requirement.

    The demonstration runs first, on a second file, so that the mismatch is
    something this suite has actually seen P1 produce for a byte-identical file
    rather than something a comment asserts. The requirement is the last line.
    """
    plan, source = planned

    # -- the demonstration: a move P1 has not been told about --
    decoy = fixture_root / "Decoy.txt"
    decoy.write_bytes(b"unchanged bytes")
    stat = decoy.stat()
    decoy_id = observe_path(
        p12_conn, decoy, author="p12-test", component_version="p12-test",
        filename="Decoy.txt", normalized_filename="Decoy.txt", extension=".txt",
        observed_size=stat.st_size, observed_timestamps=str(stat.st_mtime),
        parent_folder_context=str(fixture_root), mime_type="text/plain",
        detected_format=None, scan_state="included", materialized=True)
    decoy_hash = get_file(p12_conn, decoy_id)["content_hash"]
    moved = fixture_root / "DecoyMoved.txt"
    decoy.rename(moved)
    assert moved.read_bytes() == b"unchanged bytes"
    assert verify_content(
        p12_conn, decoy_id, decoy_hash, point=VerificationPoint.V3,
        author="p12-test", component_version="p12-test",
        materialized=True) == "mismatch", (
        "if this ever returns 'match', the trap has gone away and this twin "
        "is no longer guarding anything")

    # -- the requirement: the real executor did not fall into it --
    record = _apply(p12_conn, plan, source_root=fixture_root,
                    destination_root=fixture_root, now=clock, mint_id=ids)
    assert record.hash_after_completion == "match"
    assert record.result == v.APPLIED, (
        "a completed same-volume rename was recorded as a failure; V3 was "
        "asked before P1 was told where the file went")


# --- the rest of E1 ---------------------------------------------------------


def test_the_directories_this_action_created_are_recorded_and_no_others(
        p12_conn, planned, fixture_root, clock, ids, landscape):
    plan, _ = planned
    destination = Path(plan.resolved_destination_path).parent
    assert not destination.exists()

    record = _apply(p12_conn, plan, source_root=fixture_root,
                    destination_root=fixture_root, now=clock, mint_id=ids)

    created = [Path(item) for item in record.directories_created_by_this_action]
    assert created and all(item.is_dir() for item in created)
    # The §1.1 folder the person already had is never claimed as P12's.
    assert landscape["root_documents"] not in created
    # Shallowest first, so a reversal can walk it deepest-first.
    assert created == sorted(created, key=lambda item: len(item.parts))


def test_v1_and_v2_are_both_recorded_for_an_applied_action(
        p12_conn, planned, fixture_root, clock, ids):
    plan, _ = planned
    record = _apply(p12_conn, plan, source_root=fixture_root,
                    destination_root=fixture_root, now=clock, mint_id=ids)
    assert record.hash_at_preparation == plan.expected_content_hash
    assert record.hash_immediately_before_move == plan.expected_content_hash
    assert _point(p12_conn, "V1") < _point(p12_conn, "V2") < _point(p12_conn, "V3")


def test_the_journal_entry_carries_836s_five_and_what_reversal_needs(
        p12_conn, planned, fixture_root, clock, ids):
    plan, source = planned
    record = _apply(p12_conn, plan, source_root=fixture_root,
                    destination_root=fixture_root, now=clock, mint_id=ids)
    entry = JournalEntry.for_plan(p12_conn, plan.plan_id)
    assert entry is not None
    assert entry.original_source_path == str(source)
    assert entry.destination_path == record.final_destination_path
    assert entry.content_hash_at_movement == plan.expected_content_hash
    assert entry.collision_behaviour == plan.collision_policy
    assert entry.post_move_verification_result == "match"
    assert entry.entry_kind == v.ENTRY_APPLIED
    assert entry.reverses_entry_id is None
    assert entry.execution_mode == v.ATOMIC_RENAME
    assert entry.directories_created_by_this_action == (
        record.directories_created_by_this_action)


def test_an_applied_action_appends_executed_move_and_never_failed_move(
        p12_conn, planned, fixture_root, clock, ids):
    plan, _ = planned
    _apply(p12_conn, plan, source_root=fixture_root,
           destination_root=fixture_root, now=clock, mint_id=ids)
    types = [row["event_type"] for row in p12_conn.execute(
        "SELECT event_type FROM events ORDER BY event_id")]
    assert v.EXECUTED_MOVE in types
    assert v.FAILED_MOVE not in types
    assert v.REFUSED_MOVE not in types


def test_a_stale_plan_is_not_moved_and_never_reaches_v2(
        p12_conn, planned, fixture_root, clock, ids):
    plan, source = planned
    source.write_bytes(b"somebody else edited this")
    record = _apply(p12_conn, plan, source_root=fixture_root,
                    destination_root=fixture_root, now=clock, mint_id=ids)
    assert record.result == f"{v.STALE}:{v.CONTENT_HASH_DIFFERS}"
    assert record.mode is None
    assert source.exists()
    assert not Path(plan.resolved_destination_path).exists()
    assert record.directories_created_by_this_action == ()
    with pytest.raises(AssertionError):
        _point(p12_conn, "V2")


def test_a_run_is_bounded_and_the_bound_has_no_default(
        p12_conn, planned, fixture_root, clock, ids):
    """`74` §8 Q6 is open. The bound is injected; absent means refuse."""
    from mutation.execute import BatchPolicyRequired, apply_batch

    plan, _ = planned
    shared = dict(
        legal_destination_ids=frozenset({plan.requested_destination_node}),
        constraints=CONSTRAINTS,
        suffix_for=lambda stem, attempt: f"{stem} ({attempt})",
        max_suffix_attempts=8, extra_protected=None,
        conflict_copies=lambda path: (), dataless_of=lambda path: False,
        normalize_filename=lambda name: name, scan_state="included",
        materialized=True, component_version="p12-test", user_id=None,
        source_root=fixture_root, destination_root=fixture_root,
        now=clock, mint_id=ids)

    with pytest.raises(BatchPolicyRequired):
        apply_batch(p12_conn, (plan,), batch_bound=None,
                    halts_run=lambda record: False, **shared)
    with pytest.raises(BatchPolicyRequired):
        apply_batch(p12_conn, (plan,), batch_bound=1, halts_run=None, **shared)
    with pytest.raises(BatchPolicyRequired):
        apply_batch(p12_conn, (plan, plan), batch_bound=1,
                    halts_run=lambda record: False, **shared)

    records = apply_batch(p12_conn, (plan,), batch_bound=1,
                          halts_run=lambda record: False, **shared)
    assert [item.result for item in records] == [v.APPLIED]
    assert isinstance(records[0], ExecutionRecord)
