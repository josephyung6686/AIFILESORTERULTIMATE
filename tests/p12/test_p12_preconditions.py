"""§8.3's recheck. Five triggers, each independently reproducible by name.

`00`:171: *"Immediately before applying an action, the system should recheck the
source file. If its content hash differs, if the source path has changed, if the
destination changed, if the file disappeared, or if permission is no longer
available, the action should be marked stale and removed from automatic
execution."* Five conditions, five triggers, five distinct sentences.

The negative twin is about the ORDER those five are asked in. P1's
`verify_content` swallows an `OSError` and returns `"mismatch"`, so a source that
vanished, a source that moved and a source that became unreadable all come back
from it as a content-hash difference -- three different things to tell a person,
collapsed into one wrong one. Every structural question is therefore asked first.
"""
from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import pytest

from mutation import vocabulary as v
from mutation.preconditions import (
    PreconditionVerdict, evaluate_preconditions, refresh_prompt,
)

RUNNING_AS_ROOT = hasattr(os, "geteuid") and os.geteuid() == 0


def _evaluate(conn, plan, *, checkpoint=v.PREPARE, legal=None,
              occupant_at_prepare=None):
    return evaluate_preconditions(
        conn, plan, checkpoint=checkpoint,
        legal_destination_ids=frozenset(
            legal if legal is not None else {plan.requested_destination_node}),
        occupant_at_prepare=occupant_at_prepare, component_version="p12-test",
        materialized=True, now=lambda: "2026-08-29T00:10:00Z")


def _detections(conn):
    return conn.execute(
        "SELECT explanation FROM events WHERE event_type = ?",
        (v.EXTERNAL_MODIFICATION_DETECTION,)).fetchall()


# --- the five triggers, one reproduction each -------------------------------
#
# Each returns the verdict, so the pair of tests Wave D2 names can assert over
# all five in one place without five copies of the setup.


def _fire_content_hash_differs(conn, plan, source: Path):
    source.write_bytes(b"different bytes entirely")
    return _evaluate(conn, plan)


def _fire_source_path_changed(conn, plan, source: Path):
    moved = source.parent / "Renamed.pdf"
    source.rename(moved)
    conn.execute("UPDATE files SET current_path = ? WHERE file_id = ?",
                 (str(moved), plan.file_id))
    return _evaluate(conn, plan)


def _fire_source_vanished(conn, plan, source: Path):
    source.unlink()
    return _evaluate(conn, plan)


def _fire_permission_lost(conn, plan, source: Path):
    original = source.stat().st_mode
    os.chmod(source, 0)
    try:
        return _evaluate(conn, plan)
    finally:
        os.chmod(source, stat.S_IMODE(original))


def _fire_destination_changed(conn, plan, source: Path):
    """§8.8's diff case: the node is gone from the current version's legal set,
    so *"their previous destination no longer exists"* and the plan needs
    renewed review rather than a re-resolved path."""
    return _evaluate(conn, plan, legal=frozenset())


FIRE = {
    v.CONTENT_HASH_DIFFERS: _fire_content_hash_differs,
    v.SOURCE_PATH_CHANGED: _fire_source_path_changed,
    v.SOURCE_VANISHED: _fire_source_vanished,
    v.PERMISSION_LOST: _fire_permission_lost,
    v.DESTINATION_CHANGED: _fire_destination_changed,
}

#: Root reads a mode-000 file, so the fifth trigger cannot be made to fire.
UNREPRODUCIBLE_AS_ROOT = (v.PERMISSION_LOST,)


# ---------------------------------------------------------------------------
# The pair Wave D2 names.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("trigger", v.STALENESS_TRIGGERS)
def test_each_of_the_five_staleness_triggers_fires_with_its_own_name(
        p12_conn, planned, trigger):
    """Done-means 3. Each trigger is independently reproducible against a
    fixture and yields `stale:<trigger>`, no mutation, one
    `external modification detection` event, and its own refresh prompt.

    The five are asserted here as a set as well as one at a time: the whole
    point of five names is that a person is told five different things, so the
    test also checks that no two of the five prompts read alike.
    """
    if RUNNING_AS_ROOT and trigger in UNREPRODUCIBLE_AS_ROOT:
        pytest.skip("root reads a mode-000 file, so this trigger cannot fire")
    plan, source = planned
    assert FIRE.keys() == set(v.STALENESS_TRIGGERS)

    verdict = FIRE[trigger](p12_conn, plan, source)
    assert verdict.trigger == trigger
    assert verdict.verdict == f"stale:{trigger}"
    assert verdict.is_fresh is False

    # Removed from automatic execution, and the observation recorded even
    # though nothing moved.
    detections = _detections(p12_conn)
    assert len(detections) == 1
    assert json.loads(detections[0][0])["trigger"] == trigger
    assert not Path(plan.resolved_destination_path).exists()

    # Its own sentence, and it is not shared with any other trigger.
    prompt = refresh_prompt(verdict)
    assert prompt == v.decline_message(f"stale:{trigger}")
    keys = {v.reading_key(v.decline_message(f"stale:{other}"))
            for other in v.STALENESS_TRIGGERS}
    assert len(keys) == len(v.STALENESS_TRIGGERS)


@pytest.mark.skipif(RUNNING_AS_ROOT,
                    reason="root reads a mode-000 file, so no trigger separates")
def test_a_vanished_source_is_not_reported_as_content_hash_differs(p12_conn,
                                                                   planned):
    """The negative twin, and it is about ORDER.

    P1's `verify_content` catches `OSError` and returns `"mismatch"`
    (`src/database_agent/verify.py:45-49`), so a source that vanished, one that
    moved and one that lost its read permission would all be reported as *"this
    file changed after the preview"* if the hash were asked for first. Three
    real situations, three things a person can act on, told as one wrong thing.

    All three are asserted, plus the fact that the hash was never computed at
    all -- a verdict can carry the right trigger and still have paid for a hash
    it should not have asked for.
    """
    plan, source = planned
    original = source.read_bytes()

    vanished = _fire_source_vanished(p12_conn, plan, source)
    assert vanished.trigger == v.SOURCE_VANISHED
    assert vanished.trigger != v.CONTENT_HASH_DIFFERS
    assert vanished.hash_result is None
    source.write_bytes(original)

    moved = _fire_source_path_changed(p12_conn, plan, source)
    assert moved.trigger == v.SOURCE_PATH_CHANGED
    assert moved.hash_result is None
    (source.parent / "Renamed.pdf").rename(source)
    p12_conn.execute("UPDATE files SET current_path = ? WHERE file_id = ?",
                     (str(source), plan.file_id))

    unreadable = _fire_permission_lost(p12_conn, plan, source)
    assert unreadable.trigger == v.PERMISSION_LOST
    assert unreadable.hash_result is None

    # P1 was never asked. A `hashing` event here would mean the structural
    # checks ran but the hash was paid for anyway.
    assert p12_conn.execute(
        "SELECT COUNT(*) FROM events WHERE event_type = 'hashing'"
    ).fetchone()[0] == 0

    # And the guard is not a blanket "everything is structural": a file that
    # really did change still reports the hash difference.
    changed = _fire_content_hash_differs(p12_conn, plan, source)
    assert changed.trigger == v.CONTENT_HASH_DIFFERS
    assert changed.hash_result == "mismatch"


# ---------------------------------------------------------------------------
# The rest of the contract.
# ---------------------------------------------------------------------------


def test_an_untouched_plan_is_fresh_and_appends_no_modification_event(
        p12_conn, planned):
    plan, _ = planned
    verdict = _evaluate(p12_conn, plan)
    assert verdict.verdict == v.FRESH
    assert verdict.is_fresh is True
    assert verdict.trigger is None
    assert verdict.hash_result == "match"
    assert verdict.checkpoint_hash == plan.expected_content_hash
    assert verdict.checkpoint == v.PREPARE
    assert _detections(p12_conn) == []


def test_the_prepare_and_pre_apply_checkpoints_are_recorded_distinctly(
        p12_conn, planned):
    """§8.2's first two verification points. Contract out §2 requires the
    precondition to be evaluated TWICE, and a record that could not say which
    evaluation it was would make the second one unprovable."""
    plan, _ = planned
    assert _evaluate(p12_conn, plan, checkpoint=v.PREPARE).checkpoint == v.PREPARE
    assert _evaluate(p12_conn, plan,
                     checkpoint=v.PRE_APPLY).checkpoint == v.PRE_APPLY
    points = {json.loads(row[0])["point"] for row in p12_conn.execute(
        "SELECT explanation FROM events WHERE event_type = 'hashing'")}
    assert points == {"V1", "V2"}


def test_an_unknown_checkpoint_is_out_of_vocabulary(p12_conn, planned):
    plan, _ = planned
    with pytest.raises(v.OutOfVocabulary):
        _evaluate(p12_conn, plan, checkpoint="after_the_fact")


def test_destination_changed_when_the_occupant_changed_between_checkpoints(
        p12_conn, planned):
    plan, _ = planned
    destination = Path(plan.resolved_destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(b"an unrelated file that arrived after the preview")
    verdict = _evaluate(p12_conn, plan, checkpoint=v.PRE_APPLY,
                        occupant_at_prepare=None)
    assert verdict.trigger == v.DESTINATION_CHANGED
    assert verdict.destination_occupant_hash is not None


def test_an_occupant_present_at_both_checkpoints_is_a_collision_not_staleness(
        p12_conn, planned):
    """§8.3 gives collisions their own policy and their own four behaviours. If
    occupancy alone were a staleness trigger, that policy would be unreachable
    -- so what `destination_changed` means at the recheck is that occupancy
    CHANGED between the two checkpoints."""
    plan, _ = planned
    destination = Path(plan.resolved_destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(b"an incumbent that was already there")
    prepare = _evaluate(p12_conn, plan, checkpoint=v.PREPARE)
    assert prepare.is_fresh
    pre_apply = _evaluate(p12_conn, plan, checkpoint=v.PRE_APPLY,
                          occupant_at_prepare=prepare.destination_occupant_hash)
    assert pre_apply.is_fresh
    assert _detections(p12_conn) == []


def test_a_file_that_both_moved_and_changed_reports_the_path_not_the_hash(
        p12_conn, planned):
    """A file can satisfy several triggers at once, and a verdict that varied
    with evaluation order would make the retained stale record untrustworthy.
    The order is fixed and this is the case that proves it is."""
    plan, source = planned
    moved = source.parent / "Renamed.pdf"
    source.rename(moved)
    moved.write_bytes(b"and different bytes too")
    p12_conn.execute("UPDATE files SET current_path = ? WHERE file_id = ?",
                     (str(moved), plan.file_id))
    assert _evaluate(p12_conn, plan).trigger == v.SOURCE_PATH_CHANGED


def test_a_file_p1_no_longer_has_a_row_for_is_a_vanished_source(p12_conn,
                                                                planned):
    plan, source = planned
    source.unlink()
    p12_conn.execute("DELETE FROM files WHERE file_id = ?", (plan.file_id,))
    verdict = _evaluate(p12_conn, plan)
    assert verdict.trigger == v.SOURCE_VANISHED
    assert verdict.observed_source_path is None


def test_a_stale_verdict_mutates_nothing(p12_conn, planned):
    plan, source = planned
    source.write_bytes(b"changed")
    before = sorted(item.name for item in source.parent.iterdir())
    _evaluate(p12_conn, plan)
    assert sorted(item.name for item in source.parent.iterdir()) == before
    assert not Path(plan.resolved_destination_path).exists()
    assert not Path(plan.resolved_destination_path).parent.exists()


def test_a_fresh_plan_has_no_refresh_prompt(p12_conn, planned):
    """`66` §10 asks for a sentence per DECLINED outcome. A fresh plan was not
    declined, and inventing a reassuring sentence for it would put a sixth
    message in a table whose whole property is that its members are distinct."""
    plan, _ = planned
    with pytest.raises(ValueError):
        refresh_prompt(_evaluate(p12_conn, plan))


def test_a_verdict_refuses_a_trigger_outside_the_five(p12_conn, planned):
    plan, _ = planned
    with pytest.raises(v.OutOfVocabulary):
        PreconditionVerdict(
            plan_id=plan.plan_id, checkpoint=v.PREPARE,
            verdict="stale:the_moon_was_wrong", trigger="the_moon_was_wrong",
            observed_source_path=None, observed_size_and_modification_state=None,
            destination_occupant_hash=None, hash_result=None,
            checkpoint_hash=None)
