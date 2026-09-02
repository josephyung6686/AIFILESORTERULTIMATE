"""AP-05, AP-06 and AP-07: three that lose no file and still say something untrue."""
from __future__ import annotations

import sqlite3

import pytest

from mutation import vocabulary as v
from mutation.execute import ExecutionRecord, JournalEntry


def _entry(entry_id: str, stamp: str) -> JournalEntry:
    return JournalEntry(
        entry_id=entry_id, entry_kind=v.ENTRY_APPLIED, reverses_entry_id=None,
        plan_id=f"p-{entry_id}", plan_version="pv", file_id=f"f-{entry_id}",
        hash_algorithm="sha256", original_source_path=f"/s/{entry_id}",
        destination_path=f"/d/{entry_id}", content_hash_at_movement="h",
        collision_behaviour=v.STOP_AND_ASK,
        post_move_verification_result="match",
        source_volume="vol", destination_volume="vol",
        execution_mode=v.ATOMIC_RENAME,
        directories_created_by_this_action=(),
        intended_display_name=entry_id, filesystem_safe_name=entry_id,
        time_of_execution=stamp)


# --------------------------------------------------------------------- AP-05


def test_take_back_runs_newest_first_even_when_the_clock_cannot_tell_them_apart():
    """`take_back`'s docstring states the property and its sort did not have it.

    Newest first because a folder made for a later move may sit inside one made
    for an earlier move, and `mutation.directories` will only remove a folder
    nothing else references. Python's sort is stable, so entries sharing a
    `time_of_execution` kept their INPUT order -- and `applied_entries` supplies
    them `ORDER BY j.time_of_execution, j.record_id` ASCENDING. Ties therefore
    ran oldest-first, the exact order the docstring forbids.

    With the production clock at microsecond resolution a real tie is close to
    impossible. It becomes real the moment anyone injects a coarser one, and the
    suite's own `clock` fixture is per-minute.
    """
    from apply_run.run import undo_order

    tied = [_entry("a", "T1"), _entry("b", "T1"), _entry("c", "T1")]
    assert [e.entry_id for e in undo_order(tied)] == ["c", "b", "a"]

    # And the ordinary case is unchanged: distinct stamps still sort by time.
    mixed = [_entry("old", "T1"), _entry("new", "T3"), _entry("mid", "T2")]
    assert [e.entry_id for e in undo_order(mixed)] == ["new", "mid", "old"]

    # A tie WITHIN a mixed run stays newest-first across both keys.
    both = [_entry("a", "T1"), _entry("b", "T1"), _entry("c", "T2")]
    assert [e.entry_id for e in undo_order(both)] == ["c", "b", "a"]


# --------------------------------------------------------------------- AP-06


def test_a_cross_volume_stop_is_subject_to_the_halt_rule_like_any_other():
    """`UnverifiedCopyDispositionRequired` was caught, an outcome appended, and
    the handler `continue`d -- skipping the `halt_on` check, which ran only on
    the non-exception path. A run whose plans all cross a volume reported every
    one and never halted, whatever `halt_on` said.

    Today `CROSS_VOLUME_UNRULED` is deliberately not a member of `RESULT_KINDS`,
    so `_HALT_ON` cannot name it and this is unreachable from the CLI. It is
    fixed anyway because it means the halt rule had a shape the composition root
    could not express, which is `74` §8 Q6's own question.
    """
    from apply_run.run import CROSS_VOLUME_UNRULED, halts

    assert halts(CROSS_VOLUME_UNRULED, frozenset({"not_attempted"}))
    assert not halts(CROSS_VOLUME_UNRULED, frozenset({v.FAILED}))
    assert halts(f"{v.FAILED}:{v.V3_HASH_MISMATCH}", frozenset({v.FAILED}))
    assert not halts(v.APPLIED, frozenset({v.FAILED}))


# --------------------------------------------------------------------- AP-07


def test_the_execution_record_carries_the_detail_the_refusal_travelled_on():
    """`protection_verdict`'s docstring promises the P7 reason "travels on the
    detail" so that "this file is protected and no policy permits it" and
    "nothing has looked at this file" can be told apart. It travelled as far as
    the EVENT and no further: `ExecutionRecord` had no `detail` field, so a
    person whose file nothing had classified was told it was protected -- which
    on a corpus with no detector is the ORDINARY state, and the most confusing
    possible thing to say about it.
    """
    record = ExecutionRecord(
        plan_id="p1", mode=None, hash_at_preparation=None,
        hash_immediately_before_move=None, hash_after_completion=None,
        destination_confirmed_pre_removal=None,
        result=f"{v.REFUSED}:{v.PROTECTED_WITHOUT_POLICY}",
        final_destination_path=None, directories_created_by_this_action=(),
        started_at="T1", finished_at="T2",
        detail={"privacy_reason": "no classification has been made"})
    assert record.detail["privacy_reason"] == "no classification has been made"

    # It survives the round trip through the store, and a row written before
    # the field existed still reads back.
    from mutation.execute import executions_for, record_execution
    from mutation.schema import create_mutation_schema
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_mutation_schema(conn)
    record_execution(conn, record, plan_version="pv", record_id="r1")
    read_back, = executions_for(conn, "p1")
    assert read_back == record

    # A row written before the field existed: the payload simply has no key.
    # Inserted rather than updated, because the store refuses to rewrite a row
    # -- which is `record_execution`'s append-only guarantee doing its job.
    import json
    legacy = json.loads(
        conn.execute("SELECT payload FROM execution_records").fetchone()[0])
    legacy.pop("detail")
    conn.execute(
        "INSERT INTO execution_records (record_id, plan_id, plan_version, "
        "result, mode, final_destination_path, finished_at, payload) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("r0", "p0", "pv", legacy["result"], None, None, "T2",
         json.dumps(legacy)))
    older, = executions_for(conn, "p0")
    assert older.detail == {}, "a row from before the field reads back empty"
