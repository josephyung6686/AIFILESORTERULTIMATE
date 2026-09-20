"""The constraint table a run uses describes the VOLUME, not the process.

`mutation.constraints.measure_case_sensitivity` has existed, fully tested against
a real directory (`test_p12_volume_measurement.py`), and been called from nowhere.
This file is about the composition root's half: `cli._constraints_for`, the one
place a run turns the declared per-platform table into a table about the disk in
front of it.

**Which half of the proof is real and which is injected, stated once here.**

* REAL: the FOLD. Every test below that touches a volume touches a real one --
  a real directory on the disk the suite is running on, with `_constraints_for`
  running the real probe against it: a real `mkdir`, a real lookup, a real
  `rmdir`. The move tests move real bytes with the real `apply_plan`. The last
  test in the file touches no volume at all; it reads code objects.
* INJECTED: `sys.platform`, and only that. An exFAT stick, an NTFS partition and
  an SMB share cannot be mounted from inside a test, so the state they produce is
  reached from the other side: the table is built as a LINUX process would build
  it -- `case_sensitive=True` -- and the disk underneath it is a macOS one that
  folds. That is byte-for-byte the state the brief's Linux user is in, and it is
  the same substitution `test_p12_file_loss.py` already makes.

Tests that need a folding volume skip where the volume does not fold, and say so:
a Linux CI runner cannot be put into the mis-declared state by any amount of
patching, because there the declaration is TRUE.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

import cli
from apply_run.run import suffix_refused

from mutation import vocabulary as v
from mutation.collision import find_collision
from mutation.constraints import VolumeUnmeasurable
from mutation.execute import apply_plan, result_of

from .conftest import plan_a_move


def _linux_table(monkeypatch):
    """The table a Linux process builds, built by the function that builds it.

    Not typed out here. A literal `FilesystemConstraints` in a test is a second
    copy of the platform table, and the defect this whole file is about is a
    value that is true of one machine written down as if it were true of every
    one -- so the test does not get to author one either.
    """
    monkeypatch.setattr(sys, "platform", "linux")
    table = cli._filesystem_constraints()
    monkeypatch.setattr(cli, "_FILESYSTEM_CONSTRAINTS", table)
    return table


def _apply(conn, plan, **overrides):
    """`apply_plan` with the composition root's own answers, as `cli` passes them."""
    kwargs = dict(
        legal_destination_ids=frozenset({plan.requested_destination_node}),
        suffix_for=suffix_refused, max_suffix_attempts=0,
        extra_protected=None, conflict_copies=lambda path: (),
        dataless_of=lambda path: False, normalize_filename=lambda name: name,
        approval_for=lambda plan_id: None, unverified_copy_disposition=None,
        scan_state="included", materialized=True, component_version="probe",
        user_id=None)
    kwargs.update(overrides)
    return apply_plan(conn, plan, **kwargs)


# ---------------------------------------------------------------------------
# The measurement reaches the table
# ---------------------------------------------------------------------------


def test_the_table_takes_the_volumes_answer_over_the_platforms(
        monkeypatch, fixture_root, case_insensitive_root):
    """`sys.platform` is a fact about the process. The file goes on the disk.

    A Linux process declares `case_sensitive=True`; this volume folds; the table
    the run uses says what the volume said. Every other field is the platform's,
    untouched -- a path budget and a prohibited set are not things a directory
    can be asked about, and nothing here pretends otherwise.
    """
    if not case_insensitive_root:
        pytest.skip("this volume does not fold case, so there is no "
                    "disagreement here to resolve")
    declared = _linux_table(monkeypatch)

    used, note = cli._constraints_for(fixture_root)

    assert declared.case_sensitive is True
    assert used.case_sensitive is False
    assert note is not None
    for field in ("unicode_form", "max_component_bytes", "max_path_bytes",
                  "prohibited_characters", "reserved_names",
                  "replacement_character"):
        assert getattr(used, field) == getattr(declared, field), field


def test_a_volume_that_agrees_with_the_platform_changes_nothing_and_says_nothing(
        monkeypatch, fixture_root, case_insensitive_root):
    """The other direction, and the one that must stay quiet. `84` §6 cuts both
    ways: a screen that announced the filesystem on every ordinary run would be
    a screen nobody reads by the third time."""
    if not case_insensitive_root:
        pytest.skip("this volume does not fold, so darwin's declaration is the "
                    "one that disagrees here")
    monkeypatch.setattr(sys, "platform", "darwin")
    declared = cli._filesystem_constraints()
    monkeypatch.setattr(cli, "_FILESYSTEM_CONSTRAINTS", declared)

    used, note = cli._constraints_for(fixture_root)

    assert used == declared
    assert note is None


def test_the_probe_runs_once_and_leaves_the_folder_as_it_found_it(
        monkeypatch, fixture_root):
    """It runs in the person's own corpus root, before they asked for any
    mutation. One directory, gone before the call returns -- and ONE, not one
    per file: the table is measured for a destination root and handed to a whole
    batch, so a move of two hundred files makes no two hundred probe folders."""
    _linux_table(monkeypatch)
    before = sorted(path.name for path in fixture_root.iterdir())
    probes = []
    cli._constraints_for(fixture_root,
                         measure=lambda root: probes.append(root) or True)
    cli._constraints_for(fixture_root)
    assert probes == [fixture_root]
    assert sorted(path.name for path in fixture_root.iterdir()) == before


# ---------------------------------------------------------------------------
# A volume that will not answer
# ---------------------------------------------------------------------------


def test_a_volume_that_cannot_be_asked_does_not_crash_the_run(
        monkeypatch, tmp_path):
    """A read-only destination is a real case and it is not an error here. The
    probe raises `VolumeUnmeasurable`; the run does not.

    This one needs no folding volume: what it exercises is the branch, and the
    branch is reached by the `mkdir` being refused.
    """
    _linux_table(monkeypatch)
    read_only = tmp_path / "read-only"
    read_only.mkdir()
    read_only.chmod(0o500)
    try:
        with pytest.raises(VolumeUnmeasurable):
            cli.measure_case_sensitivity(read_only)
        used, note = cli._constraints_for(read_only)
    finally:
        read_only.chmod(0o700)

    assert used.case_sensitive is False, (
        "an unaskable volume takes the safe error -- see a collision that is "
        "not there and stop -- rather than the one that misses one")
    assert note is not None, "and it is not silent about having done so"


def test_the_unaskable_and_the_measured_do_not_say_the_same_thing(
        monkeypatch, fixture_root, case_insensitive_root, tmp_path):
    """Both land on `case_sensitive=False` and they are not the same fact. One
    read the disk; the other could not. `84` §6 is about the sentence, so the
    two sentences are different sentences."""
    if not case_insensitive_root:
        pytest.skip("this volume does not fold case")
    _linux_table(monkeypatch)
    read_only = tmp_path / "read-only"
    read_only.mkdir()
    read_only.chmod(0o500)
    try:
        _, unaskable = cli._constraints_for(read_only)
    finally:
        read_only.chmod(0o700)
    _, measured = cli._constraints_for(fixture_root)

    assert unaskable != measured


# ---------------------------------------------------------------------------
# And what it does to a file
# ---------------------------------------------------------------------------


def test_a_measured_table_reaches_the_collision_branch_and_a_declared_one_does_not(
        p12_conn, landscape, ids, fixture_root, clock, case_insensitive_root,
        monkeypatch):
    """The whole point, at the only place it can be seen: a file.

    The syscall already keeps the bytes -- `test_p12_file_loss.py` proves that
    and this asserts it again rather than assuming it. What a declared table
    costs is the SENTENCE and the RECORD. Under `case_sensitive=True` the twin
    is invisible to `find_collision`, the move reaches `move_onto_free_path`,
    which refuses, and the person is told *"The destination changed after the
    preview"* -- which is false, nothing changed -- with no collision record
    naming what it collided with, and no route by which running again could ever
    say anything else. Measured, the same twin reaches the COLLISION branch,
    where it is recorded, named, and paused on for a decision.
    """
    if not case_insensitive_root:
        pytest.skip("this volume does not fold case, so a Linux declaration is "
                    "not a mis-declaration here")
    declared = _linux_table(monkeypatch)

    plan, source = plan_a_move(p12_conn, landscape, ids,
                               volume_of=lambda path: "vol-main",
                               collision_policy=v.STOP_AND_ASK)
    destination = Path(plan.resolved_destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    incumbent = destination.parent / destination.name.swapcase()
    incumbent.write_bytes(b"THE PERSON'S ONLY COPY")

    used, note = cli._constraints_for(fixture_root)

    # The discriminator, pinned before anything moves: the two tables disagree
    # about this exact pair of names, and only one of them is right about the
    # disk they are both describing.
    assert find_collision(destination.parent, destination.name,
                          constraints=declared) is None
    assert find_collision(destination.parent, destination.name,
                          constraints=used) is not None

    record = _apply(p12_conn, plan, source_root=fixture_root,
                    destination_root=fixture_root, now=clock, mint_id=ids,
                    constraints=used)

    assert incumbent.read_bytes() == b"THE PERSON'S ONLY COPY"
    assert source.exists(), "nothing moved, so the file is still where it was"
    assert record.result == result_of(v.PAUSED, v.AWAITING_COLLISION_DECISION)
    recorded = p12_conn.execute(
        "SELECT colliding_destination_path FROM collision_resolutions "
        "WHERE plan_id = ?", (plan.plan_id,)).fetchall()
    assert [row[0] for row in recorded] == [str(incumbent)], (
        "the collision is on the record and names the file it collided with; a "
        "staleness names nothing a person can act on")
    assert note is not None


def test_an_ordinary_move_onto_a_measured_volume_still_files_the_file(
        p12_conn, landscape, ids, fixture_root, clock, monkeypatch):
    """The control, and it runs on every volume. A fix that made the product
    refuse everything would satisfy every assertion above."""
    _linux_table(monkeypatch)
    plan, source = plan_a_move(p12_conn, landscape, ids,
                               volume_of=lambda path: "vol-main",
                               collision_policy=v.STOP_AND_ASK)
    used, _ = cli._constraints_for(fixture_root)

    record = _apply(p12_conn, plan, source_root=fixture_root,
                    destination_root=fixture_root, now=clock, mint_id=ids,
                    constraints=used)

    assert record.result == v.APPLIED, record.result
    assert Path(record.final_destination_path).read_bytes() == (
        b"PHYS1401 syllabus")
    assert not source.exists()


# ---------------------------------------------------------------------------
# And that the run actually uses it
# ---------------------------------------------------------------------------


def _reached(function) -> set[str]:
    """Every global name the function's code reaches, nested code included.

    The lambdas matter: `normalize_filename` is a lambda closed over a table,
    and a lambda still reading the import-time constant would be a second table
    inside a run that had measured one. `test_p12_no_invention.py` inspects code
    objects for the same reason -- some properties are about which name a call
    site reaches, and there is no value to assert on.
    """
    seen: set[str] = set()
    stack = [function.__code__]
    while stack:
        code = stack.pop()
        seen.update(code.co_names)
        stack.extend(const for const in code.co_consts
                     if hasattr(const, "co_names"))
    return seen


@pytest.mark.parametrize("gesture", ["_move_frozen_files", "main"])
def test_no_mutation_gesture_reaches_the_import_time_table(gesture):
    """`_FILESYSTEM_CONSTRAINTS` is what the PLATFORM declared, and a run that
    has measured its volume must not still be holding it. The three call sites
    that hand a table to a mutation -- `apply_selected`, `take_back`, `freeze` --
    all live in these two functions."""
    reached = _reached(getattr(cli, gesture))
    assert "_FILESYSTEM_CONSTRAINTS" not in reached
    assert "_constraints_for" in reached
