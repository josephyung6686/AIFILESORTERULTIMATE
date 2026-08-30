"""E4 (amended by `74` §5.2) -- every refusal is visible, and as itself.

`66` §19: *"Every movement action is visible afterward."* `74` §3.3 names eleven
things P12 must refuse and adds *"each with its own distinct language (`66` §10)
and each recorded rather than silent"*. So a refusal that leaves no row is a
bug, and so is a refusal that leaves the WRONG row.

**`refused move` and `failed move` are not two spellings of one event.**
`database_agent/events.py:30-44` records the owner minting the twentieth name on
2026-08-29 for exactly this reason: §8.2 gave P12 `failed move` for a move that
was ATTEMPTED and did not complete -- the disk filled, the destination vanished
mid-write -- and gave it nothing for a move refused or paused BEFORE it was
attempted, where nothing was touched and the cause is a rule rather than an
error. Filing a refusal as a failure tells a person the product broke when in
fact it obeyed one of their own settings, and that is the difference between
*"fix this"* and *"change this if you want to"*.

The negative twin runs in two directions: the writer rejects a refusal handed to
it as a failure, and no refusing path through the real executor appends
`failed move` at all.
"""
from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import pytest

from placement.vocabulary import REVIEW_REQUIRED

from mutation import vocabulary as v
from mutation.events import record_failed_move, record_refused_move
from mutation.execute import apply_plan
from mutation.plan import PlanRefused, build_plan
from mutation.resolution import ResolutionRefused

from .conftest import (
    CONSTRAINTS, FIXTURE_NODES, FOLDING_CONSTRAINTS, LEGAL_DESTINATIONS,
    PROTECTED_CLASSES, fixture_node, plan_a_move,
)

RUNNING_AS_ROOT = hasattr(os, "geteuid") and os.geteuid() == 0

#: How `DECLINABLE_OUTCOMES` divides by the event each outcome belongs on. The
#: partition is asserted exhaustive, so a message added to `66` §10's table
#: without a home here fails this suite rather than quietly landing nowhere.
_FAILED_MOVE_OUTCOMES = tuple(
    f"{v.FAILED}:{name}" for name in v.FAILURE_CLASSES)
_UNDO_OUTCOMES = tuple(name for name in v.UNDO_VERDICTS if name != v.REVERSED)
REFUSED_MOVE_OUTCOMES = tuple(
    name for name in v.DECLINABLE_OUTCOMES
    if name not in _FAILED_MOVE_OUTCOMES and name not in _UNDO_OUTCOMES)

#: `hash_unverifiable` has no producer and this suite says so rather than
#: pretending to cover it. P1's `verify_content` swallows the `OSError` and
#: returns `"mismatch"` (`database_agent/verify.py:45-49`), so *"a checkpoint
#: hash could not be computed"* and *"the hash differs"* arrive at P12 as one
#: answer and P12 cannot tell them apart. Reaching it needs a change in P1, not
#: in P12, and inventing a local `stat`-and-guess would be P12 answering it.
UNREACHABLE_TODAY = {v.HASH_UNVERIFIABLE: "P1 reports it as `mismatch` (V1-V4)"}

#: A FINDING, pinned rather than hidden. `special.inspect_objects` refuses a
#: source that is not on disk as `source_or_destination_unavailable`, and it runs
#: before the precondition evaluation -- it has to, because the protected-
#: container check must be first and must not follow a link. So a file the person
#: DELETED between the preview and the apply is reported as an unavailable drive,
#: and the sentence they read is *"Reconnect it and try again"* rather than
#: §8.3's own *"This file is no longer there."* Both are recorded, both are
#: `refused move`, and the class is the wrong one.
#: `test_a_deleted_source_is_reported_as_an_unavailable_drive_today` pins the
#: behaviour so that whoever fixes `special.py` is told to come back here.
REPORTED_AS_ANOTHER_CLASS_TODAY = {
    f"{v.STALE}:{v.SOURCE_VANISHED}": v.SOURCE_OR_DESTINATION_UNAVAILABLE,
}


def _apply(conn, plan, fixture_root, clock, ids, **overrides):
    kwargs = dict(
        legal_destination_ids=frozenset({plan.requested_destination_node}),
        source_root=fixture_root, destination_root=fixture_root,
        constraints=CONSTRAINTS,
        suffix_for=lambda stem, attempt: f"{stem} ({attempt})",
        max_suffix_attempts=8, extra_protected=None,
        conflict_copies=lambda path: (), dataless_of=lambda path: False,
        normalize_filename=lambda name: name, scan_state="included",
        unverified_copy_disposition=None, approval_for=lambda plan_id: None,
        materialized=True, component_version="p12-test", user_id="jy",
        now=clock, mint_id=ids)
    kwargs.update(overrides)
    return apply_plan(conn, plan, **kwargs)


def _refusals(conn):
    return [json.loads(row[0]) for row in conn.execute(
        "SELECT explanation FROM events WHERE event_type = ? ORDER BY event_id",
        (v.REFUSED_MOVE,))]


def _event_types(conn):
    return [row[0] for row in conn.execute(
        "SELECT event_type FROM events ORDER BY event_id")]


# --- the scenarios, one per reachable outcome -------------------------------
#
# Each returns the outcome string it is meant to produce, and every one drives
# the REAL code. A scenario that recorded the row itself would prove that the
# writer works and nothing about whether P12 ever calls it.


def _via_construction(conn, landscape, ids, *, nodes, constraints,
                      cross_folder_moves, node_id, legal):
    """Build a plan that refuses, and record the refusal the way the
    composition root must: catch, then `record_plan_refusal`."""
    from mutation.events import record_plan_refusal

    plan, source = plan_a_move(conn, landscape, ids,
                               volume_of=lambda path: "vol-main",
                               name="Constructed.pdf")
    from placement.fixtures import GOLDEN_DECISIONS
    from placement.records import Destination, Subject
    from placement.vocabulary import PLACE
    import dataclasses

    golden = next(item for item in GOLDEN_DECISIONS if item.outcome == PLACE)
    decision = dataclasses.replace(
        golden, destination=Destination(node_id=node_id, node_role="ordinary"),
        subject=Subject(kind="file", file_id=plan.file_id,
                        content_hash=plan.expected_content_hash,
                        group_id=None, member_file_ids=()))
    try:
        build_plan(conn, decision, nodes=nodes, legal_destination_ids=legal,
                   cross_folder_moves=cross_folder_moves, constraints=constraints,
                   high_level_folders=landscape,
                   volume_of=lambda path: "vol-main",
                   protected_handling_classes=PROTECTED_CLASSES,
                   collision_policy=v.PRESERVE_BOTH_DETERMINISTIC_SUFFIX,
                   expiration_state="no expiry configured",
                   now=lambda: "2026-08-29T00:00:00Z", mint_id=ids)
    except (PlanRefused, ResolutionRefused) as refusal:
        record_plan_refusal(
            conn, refusal, file_id=plan.file_id,
            content_hash=plan.expected_content_hash,
            source_path=str(source), destination_path=None,
            observed_at="2026-08-29T00:05:00Z",
            component_version="p12-test", user_id="jy")
        return refusal.refusal_class
    raise AssertionError(f"{node_id} was expected to refuse and did not")


def _scenarios(conn, landscape, fixture_root, clock, ids):
    """`{outcome: callable}`. Each callable runs one scenario end to end."""
    def plain(**kwargs):
        return plan_a_move(conn, landscape, ids,
                           volume_of=lambda path: "vol-main", **kwargs)

    def node_not_in_frozen_tree():
        return _via_construction(
            conn, landscape, ids, nodes=FIXTURE_NODES, constraints=CONSTRAINTS,
            cross_folder_moves=True, node_id="n-nowhere",
            legal=LEGAL_DESTINATIONS)

    def node_refuses_placement():
        nodes = FIXTURE_NODES + (
            # A folder the person chose to leave untouched: §5.10 guarantees
            # they may, so P10 derives `accepts_placement = False` for
            # `ignored` and P12 reads the flag rather than re-deriving it.
            fixture_node("n-closed", "Archive", "n-course",
                         node_type="ignored", accepts_placement=False),)
        return _via_construction(
            conn, landscape, ids, nodes=nodes, constraints=CONSTRAINTS,
            cross_folder_moves=True, node_id="n-closed",
            legal=LEGAL_DESTINATIONS | {"n-closed"})

    def node_path_collision():
        nodes = FIXTURE_NODES + (
            fixture_node("n-phys-lower", "phys1401", "n-course"),)
        return _via_construction(
            conn, landscape, ids, nodes=nodes,
            constraints=FOLDING_CONSTRAINTS, cross_folder_moves=True,
            node_id="n-phys", legal=LEGAL_DESTINATIONS | {"n-phys-lower"})

    def cross_folder_not_permitted():
        nodes = (fixture_node("n-course", "Coursework", None,
                              root_anchor="root_downloads"),
                 fixture_node("n-phys", "PHYS1401", "n-course",
                              root_anchor="root_downloads"))
        return _via_construction(
            conn, landscape, ids, nodes=nodes, constraints=CONSTRAINTS,
            cross_folder_moves=False, node_id="n-phys",
            legal=LEGAL_DESTINATIONS)

    def package_bundle_unapproved():
        plan, _ = plain(name="Numbers.app")
        _apply(conn, plan, fixture_root, clock, ids)
        return v.PACKAGE_BUNDLE_UNAPPROVED

    def symlink_not_followed():
        plan, source = plain(name="Linked.pdf")
        elsewhere = source.parent / "Elsewhere.pdf"
        source.rename(elsewhere)
        source.symlink_to(elsewhere)
        _apply(conn, plan, fixture_root, clock, ids)
        return v.SYMLINK_NOT_FOLLOWED

    def source_or_destination_unavailable():
        plan, _ = plain(name="Detached.pdf")
        _apply(conn, plan, fixture_root, clock, ids,
               destination_root=fixture_root / "an-unmounted-drive")
        return v.SOURCE_OR_DESTINATION_UNAVAILABLE

    def protected_without_policy():
        plan, _ = plain(name="Passport.pdf", handling_class="sensitive_personal",
                        protected=True)
        _apply(conn, plan, fixture_root, clock, ids)
        return v.PROTECTED_WITHOUT_POLICY

    def review_policy_unsatisfied():
        plan, _ = plain(name="NeedsReview.pdf", review_policy=REVIEW_REQUIRED)
        _apply(conn, plan, fixture_root, clock, ids)
        return v.REVIEW_POLICY_UNSATISFIED

    def stale_content_hash_differs():
        plan, source = plain(name="Edited.pdf")
        source.write_bytes(b"somebody else edited this")
        _apply(conn, plan, fixture_root, clock, ids)
        return f"{v.STALE}:{v.CONTENT_HASH_DIFFERS}"

    def stale_source_path_changed():
        # P1 knows these bytes at a second live path now -- §2.9's duplicate
        # family, which P1 supports explicitly. The plan's own source is still
        # there, so this reaches the precondition rather than the object check.
        plan, source = plain(name="Moved.pdf")
        elsewhere = source.parent / "MovedAgain.pdf"
        elsewhere.write_bytes(source.read_bytes())
        conn.execute("UPDATE files SET current_path = ? WHERE file_id = ?",
                     (str(elsewhere), plan.file_id))
        _apply(conn, plan, fixture_root, clock, ids)
        return f"{v.STALE}:{v.SOURCE_PATH_CHANGED}"

    def stale_permission_lost():
        plan, source = plain(name="Unreadable.pdf")
        original = source.stat().st_mode
        os.chmod(source, 0)
        try:
            _apply(conn, plan, fixture_root, clock, ids)
        finally:
            os.chmod(source, stat.S_IMODE(original))
        return f"{v.STALE}:{v.PERMISSION_LOST}"

    def stale_destination_changed():
        plan, _ = plain(name="Retargeted.pdf")
        _apply(conn, plan, fixture_root, clock, ids,
               legal_destination_ids=frozenset())
        return f"{v.STALE}:{v.DESTINATION_CHANGED}"

    def paused_cloud_sync_conflict():
        plan, _ = plain(name="Syncing.pdf")
        _apply(conn, plan, fixture_root, clock, ids,
               conflict_copies=lambda path: ("Syncing (conflicted copy).pdf",))
        return f"{v.PAUSED}:{v.CLOUD_SYNC_CONFLICT}"

    def paused_awaiting_collision_decision():
        plan, _ = plain(name="Duplicate.pdf",
                        collision_policy=v.STOP_AND_ASK)
        occupied = Path(plan.resolved_destination_path)
        occupied.parent.mkdir(parents=True, exist_ok=True)
        occupied.write_bytes(b"something already here")
        _apply(conn, plan, fixture_root, clock, ids,
               constraints=CONSTRAINTS)
        return f"{v.PAUSED}:{v.AWAITING_COLLISION_DECISION}"

    scenarios = {
        v.NODE_NOT_IN_FROZEN_TREE: node_not_in_frozen_tree,
        v.NODE_REFUSES_PLACEMENT: node_refuses_placement,
        v.NODE_PATH_COLLISION: node_path_collision,
        v.CROSS_FOLDER_NOT_PERMITTED: cross_folder_not_permitted,
        v.PACKAGE_BUNDLE_UNAPPROVED: package_bundle_unapproved,
        v.SYMLINK_NOT_FOLLOWED: symlink_not_followed,
        v.SOURCE_OR_DESTINATION_UNAVAILABLE: source_or_destination_unavailable,
        v.PROTECTED_WITHOUT_POLICY: protected_without_policy,
        v.REVIEW_POLICY_UNSATISFIED: review_policy_unsatisfied,
        f"{v.STALE}:{v.CONTENT_HASH_DIFFERS}": stale_content_hash_differs,
        f"{v.STALE}:{v.SOURCE_PATH_CHANGED}": stale_source_path_changed,
        f"{v.STALE}:{v.DESTINATION_CHANGED}": stale_destination_changed,
        f"{v.PAUSED}:{v.CLOUD_SYNC_CONFLICT}": paused_cloud_sync_conflict,
        f"{v.PAUSED}:{v.AWAITING_COLLISION_DECISION}":
            paused_awaiting_collision_decision,
    }
    if not RUNNING_AS_ROOT:
        scenarios[f"{v.STALE}:{v.PERMISSION_LOST}"] = stale_permission_lost
    return scenarios


# --- E4's named test --------------------------------------------------------


def test_every_refusal_class_appends_refused_move_with_its_own_explanation(
        p12_conn, landscape, fixture_root, clock, ids):
    scenarios = _scenarios(p12_conn, landscape, fixture_root, clock, ids)

    covered = (set(scenarios) | set(UNREACHABLE_TODAY)
               | set(REPORTED_AS_ANOTHER_CLASS_TODAY))
    if RUNNING_AS_ROOT:
        covered.add(f"{v.STALE}:{v.PERMISSION_LOST}")
    assert covered == set(REFUSED_MOVE_OUTCOMES), (
        "every outcome that belongs on `refused move` is either driven by a "
        "scenario here, named in UNREACHABLE_TODAY, or pinned in "
        "REPORTED_AS_ANOTHER_CLASS_TODAY -- each with its reason")

    seen: dict[str, dict] = {}
    for outcome, run in scenarios.items():
        before = len(_refusals(p12_conn))
        assert run() == outcome
        after = _refusals(p12_conn)
        assert len(after) == before + 1, (
            f"{outcome} appended {len(after) - before} `refused move` rows; "
            "each refusal is recorded exactly once")
        row = after[-1]
        assert row["outcome"] == outcome
        assert row["message"] == v.decline_message(outcome)
        seen[outcome] = row

    # And they are distinct AS THE PERSON READS THEM, not merely as strings.
    keys = [v.reading_key(row["message"]) for row in seen.values()]
    assert len(set(keys)) == len(keys)


def test_a_refusal_recorded_as_failed_move_is_rejected(
        p12_conn, landscape, fixture_root, clock, ids):
    """The negative twin, in both directions.

    A refusal filed as a failure would tell a person the product broke when it
    obeyed one of their own settings.
    """
    # 1. The writer refuses a refusal class, a staleness verdict and a pause.
    for outcome in (v.PROTECTED_WITHOUT_POLICY,
                    f"{v.STALE}:{v.SOURCE_VANISHED}",
                    f"{v.PAUSED}:{v.CLOUD_SYNC_CONFLICT}"):
        with pytest.raises(v.OutOfVocabulary):
            record_failed_move(
                p12_conn, failure_class=outcome, file_id="f", content_hash="h",
                source_path="/a", destination_path="/b",
                observed_at="2026-08-29T00:00:00Z",
                component_version="p12-test", user_id=None, detail={})

    # 2. And the writer in the other direction refuses a failure class, so
    #    neither event can be talked into carrying the other's meaning.
    for failure in v.FAILURE_CLASSES:
        with pytest.raises(v.OutOfVocabulary):
            record_refused_move(
                p12_conn, outcome=failure, file_id="f", content_hash="h",
                source_path="/a", destination_path="/b",
                observed_at="2026-08-29T00:00:00Z",
                component_version="p12-test", user_id=None, detail={})

    # 3. The property that matters: no refusing path through the real executor
    #    appends `failed move` at all.
    for run in _scenarios(p12_conn, landscape, fixture_root, clock, ids).values():
        run()
    types = _event_types(p12_conn)
    assert v.FAILED_MOVE not in types
    assert v.EXECUTED_MOVE not in types
    assert types.count(v.REFUSED_MOVE) > 0


def test_a_refusal_names_what_the_person_can_do_and_never_the_protected_label(
        p12_conn, landscape, fixture_root, clock, ids):
    """`66` §10 asks each message to say what occurred AND what is available."""
    for outcome, row in (
            (outcome, _run_one(p12_conn, landscape, fixture_root, clock, ids,
                               outcome))
            for outcome in (v.PROTECTED_WITHOUT_POLICY,
                            v.REVIEW_POLICY_UNSATISFIED,
                            v.PACKAGE_BUNDLE_UNAPPROVED)):
        assert row["outcome"] == outcome
        assert row["plan_id"] and row["plan_version"]
        assert row["result"].startswith(v.REFUSED)
        # The refusal carries the plan, never the material the plan was about.
        assert "PHYS1401 syllabus" not in json.dumps(row)


def _run_one(conn, landscape, fixture_root, clock, ids, outcome):
    _scenarios(conn, landscape, fixture_root, clock, ids)[outcome]()
    return _refusals(conn)[-1]


def test_a_deleted_source_is_reported_as_an_unavailable_drive_today(
        p12_conn, landscape, fixture_root, clock, ids):
    """A FINDING, pinned. Not a design, and not P12 Wave E's to change.

    §8.3 gives `source_vanished` its own trigger and `66` §10 its own sentence,
    *"This file is no longer there."* Today a file deleted between the preview
    and the apply is refused by `special.inspect_objects` -- which runs first,
    and must, because the protected-container check may not be preceded by
    anything that could follow a link -- as `source_or_destination_unavailable`,
    whose sentence tells the person to reconnect a drive.

    Both classes are §3.3 refusals and both append `refused move`, so E4's
    contract holds. What does not hold is `66` §10's point: the person is told
    to do a thing that will not help. Fixing it belongs in `special.py`, which
    Wave E does not own. When it is fixed, this test fails and says so.
    """
    plan, source = plan_a_move(p12_conn, landscape, ids,
                               volume_of=lambda path: "vol-main",
                               name="Gone.pdf")
    source.unlink()
    record = _apply(p12_conn, plan, fixture_root, clock, ids)

    observed = REPORTED_AS_ANOTHER_CLASS_TODAY[f"{v.STALE}:{v.SOURCE_VANISHED}"]
    assert record.result == f"{v.REFUSED}:{observed}"
    assert _refusals(p12_conn)[-1]["message"] == v.decline_message(observed)
