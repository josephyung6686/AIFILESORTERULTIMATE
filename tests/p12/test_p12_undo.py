"""F1 -- §8.3's conditional undo. A conflict mutates nothing and reports both sides.

*"Undo must be conditional rather than destructive. ... If the user manually
edited or moved the file after the product acted, undo should surface a conflict
rather than forcing a rollback"* (`00`:175). That sentence has a quiet half and a
loud half. The loud half is the message. The quiet half is that a conflict must
leave the disk exactly as it found it -- and "exactly" is not something an
assertion about a return value can establish, because an implementation that
renamed the file back and THEN noticed the hash had changed would return the same
verdict and would have destroyed the person's edit.

So the twin here does not read the verdict at all. It records every mutating
system call this process makes during a conflicted undo and requires the list to
be empty, and it compares the whole fixture tree byte for byte across the
attempt. A rollback forced over a changed destination is caught at the `rename`,
before anyone has to notice what it cost.
"""
from __future__ import annotations

import builtins
import json
import os
from contextlib import contextmanager
from pathlib import Path

import pytest

from mutation import cross_volume
from mutation import vocabulary as v
from mutation.execute import apply_plan
from mutation.undo import (
    AlreadyReversed, NoSuchEntry, NotAnAppliedEntry, ReversalUnverified,
    entries_for_plan, entry_by_id, is_reversed, undo, undo_verdicts_for,
)

from .conftest import CONSTRAINTS, plan_a_move

#: The composition root's sentence about a copy V4 could not confirm (`74` §8
#: Q7, still open). Stated in the test rather than in `src/` for the reason E2
#: states it there: nothing in the part package carries an answer to an open
#: question.
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


@pytest.fixture()
def applied(p12_conn, planned, fixture_root, clock, ids):
    """One file, moved. Every test below starts from a move that worked."""
    plan, source = planned
    record = _apply(p12_conn, plan, fixture_root, clock, ids)
    assert record.result == v.APPLIED
    entry = entry_by_id(p12_conn, _entry_id(p12_conn, plan.plan_id))
    return plan, source, record, entry


def _entry_id(conn, plan_id: str) -> str:
    row = conn.execute(
        "SELECT entry_id FROM move_journal WHERE plan_id = ? AND entry_kind = ?",
        (plan_id, v.ENTRY_APPLIED)).fetchone()
    assert row is not None, "the applied move appended no journal entry"
    return row[0]


# ---------------------------------------------------------------------------
# The two instruments the twin needs: a recorder of mutating system calls, and a
# byte-for-byte snapshot of the fixture tree.
# ---------------------------------------------------------------------------

#: Every way this process can change what is on disk. `rename` and `replace` are
#: the two moves, `link`/`symlink` the two ways to make a second name, `unlink`
#: and `remove` the removals, `rmdir`/`removedirs` the directory removals,
#: `mkdir`/`makedirs` the creations, and `truncate`/`chmod` the in-place edits.
#: Patching them on the `os` module catches `pathlib` and `shutil` too, because
#: both look the name up on the module at call time.
_MUTATORS = ("rename", "replace", "link", "symlink", "unlink", "remove",
             "rmdir", "removedirs", "mkdir", "makedirs", "truncate", "chmod")

#: An `open` mode that can write. `"r"` and `"rb"` cannot.
_WRITING = set("wax+")


@contextmanager
def _recording_mutations():
    """Record every mutating filesystem call made inside the block.

    Runtime introspection, not a text search: an implementation that forced the
    rollback through `shutil.move` or `Path.replace` contains neither the string
    `os.rename` nor the string `unlink`, and is caught here anyway.
    """
    calls: list[tuple[str, str]] = []
    originals = {name: getattr(os, name) for name in _MUTATORS}
    original_open = builtins.open

    def wrap(label, function):
        def recorder(path, *args, **kwargs):
            calls.append((label, str(path)))
            return function(path, *args, **kwargs)
        return recorder

    def recording_open(path, mode="r", *args, **kwargs):
        if _WRITING & set(mode):
            calls.append((f"open({mode})", str(path)))
        return original_open(path, mode, *args, **kwargs)

    for name, function in originals.items():
        setattr(os, name, wrap(f"os.{name}", function))
    builtins.open = recording_open
    try:
        yield calls
    finally:
        for name, function in originals.items():
            setattr(os, name, function)
        builtins.open = original_open


def _snapshot(root: Path) -> dict[str, object]:
    """Every path beneath `root`, with the bytes of every file."""
    out: dict[str, object] = {}
    for path in sorted(root.rglob("*")):
        key = str(path.relative_to(root))
        out[key] = path.read_bytes() if path.is_file() else "<dir>"
    return out


def _under(calls, root: Path):
    prefix = str(root)
    return [call for call in calls
            if call[1] == prefix or call[1].startswith(f"{prefix}{os.sep}")]


# ---------------------------------------------------------------------------
# F1's named test and its negative twin.
# ---------------------------------------------------------------------------


def _make_content_changed(record, source):
    Path(record.final_destination_path).write_bytes(b"the user edited it later")
    return v.CONFLICT_DESTINATION_CONTENT_CHANGED


def _make_destination_missing(record, source):
    Path(record.final_destination_path).rename(
        Path(record.final_destination_path).parent / "Moved by hand.pdf")
    return v.CONFLICT_DESTINATION_MISSING_OR_MOVED


def _make_source_occupied(record, source):
    source.write_bytes(b"an unrelated file now lives here")
    return v.CONFLICT_SOURCE_PATH_OCCUPIED


CONFLICT_SETUPS = (_make_content_changed, _make_destination_missing,
                   _make_source_occupied)


@pytest.mark.parametrize("setup", CONFLICT_SETUPS,
                         ids=[fn.__name__ for fn in CONFLICT_SETUPS])
def test_a_conflict_performs_no_mutation_and_reports_the_paths_and_hashes(
        p12_conn, applied, fixture_root, clock, ids, setup):
    plan, source, record, entry = applied
    expected_verdict = setup(record, source)
    before = _snapshot(fixture_root)

    verdict = _undo(p12_conn, entry.entry_id, clock, ids)

    assert verdict.verdict == expected_verdict
    assert _snapshot(fixture_root) == before, (
        "a conflict must leave the disk exactly as it found it")
    # Both paths, and both hashes where a hash could be taken. `66` §11: the
    # product must "show the relevant paths and hashes" rather than force a
    # rollback.
    assert verdict.destination_path == record.final_destination_path
    assert verdict.original_source_path == str(source)
    assert verdict.expected_hash == plan.expected_content_hash
    assert verdict.detail["message"] == v.decline_message(expected_verdict)
    assert verdict.reversal_entry_id is None
    assert is_reversed(p12_conn, entry.entry_id) is False
    assert entry_by_id(p12_conn, entry.entry_id) == entry
    assert len(entries_for_plan(p12_conn, plan.plan_id)) == 1


@pytest.mark.parametrize("setup", CONFLICT_SETUPS,
                         ids=[fn.__name__ for fn in CONFLICT_SETUPS])
def test_no_undo_path_forces_a_rollback_over_a_changed_destination(
        p12_conn, applied, fixture_root, clock, ids, setup):
    """The twin. It never reads the verdict.

    An implementation that renamed the file home and only then compared the
    hashes would satisfy every assertion above -- same verdict, same paths, same
    absent reversal entry, and, if it renamed the file back on noticing, the
    same tree byte for byte. What distinguishes the two is whether a mutating
    system call happened AT ALL, so that is what this measures, once per
    conflict class so that no one branch can be the unguarded one.
    """
    plan, source, record, entry = applied
    setup(record, source)
    before = _snapshot(fixture_root)

    with _recording_mutations() as calls:
        verdict = _undo(p12_conn, entry.entry_id, clock, ids)

    assert _under(calls, fixture_root) == [], (
        "a conflicted undo touched the person's disk: "
        f"{_under(calls, fixture_root)}")
    assert _snapshot(fixture_root) == before
    assert not verdict.reversed_successfully


# ---------------------------------------------------------------------------
# The reversal that does happen.
# ---------------------------------------------------------------------------


def test_undo_of_an_untouched_move_restores_byte_identical_content(
        p12_conn, applied, clock, ids):
    plan, source, record, entry = applied
    verdict = _undo(p12_conn, entry.entry_id, clock, ids)

    assert verdict.verdict == v.REVERSED
    assert verdict.reversed_successfully is True
    assert source.read_bytes() == b"PHYS1401 syllabus"
    assert not Path(record.final_destination_path).exists()
    assert verdict.observed_destination_hash == plan.expected_content_hash


def test_a_reversal_runs_v1_v2_and_v3_like_any_other_mutation(
        p12_conn, applied, clock, ids):
    _, _, record, entry = applied
    before = p12_conn.execute(
        "SELECT COUNT(*) FROM events WHERE event_type = 'hashing'").fetchone()[0]
    _undo(p12_conn, entry.entry_id, clock, ids)
    points = [json.loads(row[0])["point"] for row in p12_conn.execute(
        "SELECT explanation FROM events WHERE event_type = 'hashing' "
        "ORDER BY event_id")][before:]
    assert points == ["V1", "V2", "V3"]


def test_undo_appends_a_reversal_entry_and_never_edits_the_original(
        p12_conn, applied, clock, ids):
    plan, source, record, entry = applied
    verdict = _undo(p12_conn, entry.entry_id, clock, ids)

    assert entry_by_id(p12_conn, entry.entry_id) == entry
    reversal = entry_by_id(p12_conn, verdict.reversal_entry_id)
    assert reversal.entry_kind == v.ENTRY_REVERSAL
    assert reversal.reverses_entry_id == entry.entry_id
    assert reversal.original_source_path == entry.destination_path
    assert reversal.destination_path == entry.original_source_path
    assert reversal.directories_created_by_this_action == ()
    assert is_reversed(p12_conn, entry.entry_id) is True
    assert len(entries_for_plan(p12_conn, plan.plan_id)) == 2


def test_undo_appends_one_undo_event_with_both_paths(
        p12_conn, applied, clock, ids):
    _, source, record, entry = applied
    _undo(p12_conn, entry.entry_id, clock, ids)
    rows = p12_conn.execute(
        "SELECT subsystem, old_path, new_path FROM events WHERE event_type = ?",
        (v.UNDO,)).fetchall()
    assert [tuple(row) for row in rows] == [
        (v.SUBSYSTEM, record.final_destination_path, str(source))]


def test_a_conflicted_undo_is_recorded_too(p12_conn, applied, clock, ids):
    """`66` §19: every movement action is visible afterwards. An undo the person
    tried and could not have is exactly the kind of thing that must not vanish."""
    _, source, record, entry = applied
    Path(record.final_destination_path).write_bytes(b"edited")
    _undo(p12_conn, entry.entry_id, clock, ids)
    row = p12_conn.execute(
        "SELECT explanation FROM events WHERE event_type = ?",
        (v.UNDO,)).fetchone()
    payload = json.loads(row[0])
    assert payload["verdict"] == v.CONFLICT_DESTINATION_CONTENT_CHANGED
    assert payload["reversal_entry_id"] is None


def test_undo_puts_p1s_current_path_back_to_the_original(
        p12_conn, applied, clock, ids):
    plan, source, _, entry = applied
    _undo(p12_conn, entry.entry_id, clock, ids)
    assert p12_conn.execute(
        "SELECT current_path FROM files WHERE file_id = ?",
        (plan.file_id,)).fetchone()[0] == str(source)


def test_an_unavailable_source_folder_refuses_rather_than_conflicting(
        p12_conn, applied, clock, ids):
    """A detached volume is not a conflict: nothing about the file is in doubt,
    the drive is simply not there."""
    _, source, record, entry = applied
    source.parent.rmdir()
    verdict = _undo(p12_conn, entry.entry_id, clock, ids)
    assert verdict.verdict == v.UNDO_REFUSED_UNAVAILABLE
    assert Path(record.final_destination_path).exists()


def test_a_case_folding_twin_at_the_source_path_conflicts(
        p12_conn, applied, clock, ids):
    """`Syllabus.pdf` and `syllabus.pdf` are one path on a folding volume, and it
    is exactly the twin a person cannot tell apart that must not be written over.
    `Path.exists()` would answer the machine's question; the collation key
    answers §8.3's."""
    from .conftest import FOLDING_CONSTRAINTS
    _, source, record, entry = applied
    (source.parent / source.name.lower()).write_bytes(b"a different file")
    verdict = _undo(p12_conn, entry.entry_id, clock, ids,
                    constraints=FOLDING_CONSTRAINTS)
    assert verdict.verdict == v.CONFLICT_SOURCE_PATH_OCCUPIED
    assert Path(record.final_destination_path).exists()


# ---------------------------------------------------------------------------
# Across two volumes.
# ---------------------------------------------------------------------------


def _two_volumes(landscape):
    documents = landscape["root_documents"]
    return lambda path: ("vol-archive" if Path(path) == documents
                         else "vol-home")


def test_a_reversal_across_volumes_confirms_at_v4_before_removing_the_copy(
        p12_conn, landscape, fixture_root, clock, ids):
    plan, source = plan_a_move(p12_conn, landscape, ids,
                               volume_of=_two_volumes(landscape))
    record = _apply(p12_conn, plan, fixture_root, clock, ids)
    assert record.mode == v.CROSS_VOLUME_COPY_AND_DELETE

    entry = entry_by_id(p12_conn, _entry_id(p12_conn, plan.plan_id))
    verdict = _undo(p12_conn, entry.entry_id, clock, ids)

    assert verdict.verdict == v.REVERSED
    assert source.read_bytes() == b"PHYS1401 syllabus"
    assert not Path(record.final_destination_path).exists()
    points = [json.loads(row[0])["point"] for row in p12_conn.execute(
        "SELECT explanation FROM events WHERE event_type = 'hashing' "
        "ORDER BY event_id")]
    assert points.count("V4") == 2


def test_a_cross_volume_reversal_needs_the_open_questions_answer(
        p12_conn, landscape, fixture_root, clock, ids):
    """`74` §8 Q7 again, on the way back. A reversal that crosses volumes can
    leave a copy nobody confirmed, so the disposition is required here too."""
    from mutation.cross_volume import UnverifiedCopyDispositionRequired
    plan, source = plan_a_move(p12_conn, landscape, ids,
                               volume_of=_two_volumes(landscape))
    record = _apply(p12_conn, plan, fixture_root, clock, ids)
    entry = entry_by_id(p12_conn, _entry_id(p12_conn, plan.plan_id))
    with pytest.raises(UnverifiedCopyDispositionRequired):
        _undo(p12_conn, entry.entry_id, clock, ids,
              unverified_copy_disposition=None)
    assert Path(record.final_destination_path).exists()


def test_an_unconfirmed_reversal_copy_removes_nothing_and_is_recorded(
        p12_conn, landscape, fixture_root, clock, ids, monkeypatch):
    """The one state Contract out §7's five verdicts cannot express.

    V4 said no on the way back: the filed file is still at its destination, the
    copy P12 made at the source path is unverified, and §8.2 forbids removing
    the first while §7.11 forbids removing the second. P12 records
    `failed:v4_destination_unconfirmed` -- which has its own sentence -- and
    raises rather than dressing the state as one of the five undo verdicts.
    """
    plan, source = plan_a_move(p12_conn, landscape, ids,
                               volume_of=_two_volumes(landscape))
    record = _apply(p12_conn, plan, fixture_root, clock, ids)
    entry = entry_by_id(p12_conn, _entry_id(p12_conn, plan.plan_id))
    monkeypatch.setattr(cross_volume, "confirm_cross_volume_copy",
                        lambda conn, **kwargs: False)

    with pytest.raises(ReversalUnverified):
        _undo(p12_conn, entry.entry_id, clock, ids)

    assert Path(record.final_destination_path).exists()
    assert source.exists()
    assert is_reversed(p12_conn, entry.entry_id) is False
    row = p12_conn.execute(
        "SELECT explanation FROM events WHERE event_type = ? "
        "ORDER BY event_id DESC LIMIT 1", (v.FAILED_MOVE,)).fetchone()
    payload = json.loads(row[0])
    assert payload["failure_class"] == v.V4_DESTINATION_UNCONFIRMED
    assert payload["reverses_entry_id"] == entry.entry_id


# ---------------------------------------------------------------------------
# What undo refuses to be asked.
# ---------------------------------------------------------------------------


def test_undoing_twice_raises_rather_than_reversing_a_reversal(
        p12_conn, applied, clock, ids):
    _, _, _, entry = applied
    _undo(p12_conn, entry.entry_id, clock, ids)
    with pytest.raises(AlreadyReversed):
        _undo(p12_conn, entry.entry_id, clock, ids)


def test_undoing_a_reversal_entry_is_refused(p12_conn, applied, clock, ids):
    _, _, _, entry = applied
    verdict = _undo(p12_conn, entry.entry_id, clock, ids)
    with pytest.raises(NotAnAppliedEntry):
        _undo(p12_conn, verdict.reversal_entry_id, clock, ids)


def test_undoing_an_unknown_entry_raises(p12_conn, applied, clock, ids):
    with pytest.raises(NoSuchEntry):
        _undo(p12_conn, "no-such-entry", clock, ids)


def test_every_undo_verdict_that_declines_has_its_own_sentence():
    declining = tuple(item for item in v.UNDO_VERDICTS if item != v.REVERSED)
    sentences = {v.decline_message(item) for item in declining}
    assert len(sentences) == len(declining)


def test_undo_verdicts_are_readable_back_per_plan(p12_conn, applied, clock, ids):
    plan, _, _, entry = applied
    verdict = _undo(p12_conn, entry.entry_id, clock, ids)
    assert undo_verdicts_for(p12_conn, plan.plan_id) == (verdict,)
