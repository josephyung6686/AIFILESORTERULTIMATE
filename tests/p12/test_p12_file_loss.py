"""The three ways a person permanently loses a file, each reproduced then closed.

Every test here was RED against `a47370a` and is green only because the move is
performed by a system call that fails on an occupied destination. That is the
point: a test that also passes with `os.rename` under a correct constraint table
is measuring the constraint table, not the syscall. The twin for the primitive is
reverting `move_onto_free_path` to a bare `os.rename` -- these go red, `84` §5's
sabotage step, and `test_the_primitive_is_not_rename` names the property
directly.

The world is deliberately mis-declared in the first two: `CONSTRAINTS` says
`case_sensitive=True` on a volume that folds, which is byte-for-byte the state a
Linux user filing onto exFAT, NTFS or an SMB share is in. The whole point of the
fix is that this state can no longer destroy anything.
"""
from __future__ import annotations

import os
import unicodedata
from pathlib import Path

import pytest

from mutation import undo as undo_module
from mutation import vocabulary as v
from mutation.collision import find_collision
from mutation.execute import apply_plan, result_of
from mutation.movement import move_onto_free_path
from mutation.undo import entries_for_plan, undo

from .conftest import CONSTRAINTS, FOLDING_CONSTRAINTS, plan_a_move


def _apply(conn, plan, **overrides):
    kwargs = dict(
        legal_destination_ids=frozenset({plan.requested_destination_node}),
        constraints=CONSTRAINTS,
        suffix_for=lambda stem, attempt: f"{stem} ({attempt})",
        max_suffix_attempts=8, extra_protected=None,
        conflict_copies=lambda path: (), dataless_of=lambda path: False,
        normalize_filename=lambda name: name, approval_for=lambda plan_id: None,
        unverified_copy_disposition=None, scan_state="included",
        materialized=True, component_version="probe", user_id=None)
    kwargs.update(overrides)
    return apply_plan(conn, plan, **kwargs)


# ---------------------------------------------------------------------------
# Ground truth. Measured, not assumed -- the fix rests on these four answers.
# ---------------------------------------------------------------------------


def test_the_syscall_the_move_rests_on_refuses_an_occupied_destination(
        fixture_root):
    """`os.rename` replaces; `os.link` and `O_EXCL` refuse. Under FOLDING too.

    This is the whole argument for the primitive. It is asserted rather than
    printed because a measurement the fix depends on is a precondition of the
    fix being correct, and on a volume where `os.link` behaved like `os.rename`
    every other test in this file would be vacuous.
    """
    (fixture_root / "Case.txt").write_bytes(b"A")
    if not (fixture_root / "case.txt").exists():
        pytest.skip("this volume does not fold case; the folding claim is "
                    "untestable here and the plain-collision claims below still run")

    incumbent = fixture_root / "sYLLABUS.PDF"
    incumbent.write_bytes(b"THE PERSON'S ONLY COPY")
    incoming = fixture_root / "incoming"
    incoming.write_bytes(b"incoming")

    with pytest.raises(FileExistsError):
        os.link(incoming, fixture_root / "Syllabus.pdf")
    with pytest.raises(FileExistsError):
        os.close(os.open(fixture_root / "Syllabus.pdf",
                         os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600))
    assert incumbent.read_bytes() == b"THE PERSON'S ONLY COPY"

    # And across an NFC/NFD twin, the other fold `find_collision` exists for.
    nfc = unicodedata.normalize("NFC", "café.txt")
    nfd = unicodedata.normalize("NFD", "café.txt")
    (fixture_root / nfc).write_bytes(b"THE PERSON'S ONLY COPY")
    if (fixture_root / nfd).exists():
        with pytest.raises(FileExistsError):
            os.link(incoming, fixture_root / nfd)
        assert (fixture_root / nfc).read_bytes() == b"THE PERSON'S ONLY COPY"


def test_the_primitive_is_not_rename(fixture_root):
    """`move_onto_free_path` refuses an occupied path; `os.rename` does not.

    The sabotage twin, written as a test rather than left to a reader: this is
    the exact call that would still pass if the primitive were reverted, and it
    asserts the difference between the two directly.
    """
    incumbent = fixture_root / "incumbent.txt"
    incumbent.write_bytes(b"THE PERSON'S ONLY COPY")
    incoming = fixture_root / "incoming.txt"
    incoming.write_bytes(b"incoming")

    with pytest.raises(FileExistsError):
        move_onto_free_path(incoming, incumbent)
    assert incumbent.read_bytes() == b"THE PERSON'S ONLY COPY"
    assert incoming.read_bytes() == b"incoming", "the source was not touched"

    free = fixture_root / "free.txt"
    move_onto_free_path(incoming, free)
    assert free.read_bytes() == b"incoming"
    assert not incoming.exists(), "the source name is removed on the way through"


# ---------------------------------------------------------------------------
# AP-01. A mis-declared volume can no longer destroy the incumbent.
# ---------------------------------------------------------------------------


def test_a_wrong_case_sensitivity_declaration_does_not_destroy_the_incumbent(
        p12_conn, landscape, ids, fixture_root, clock, case_insensitive_root):
    """The state a Linux user with an exFAT/NTFS/SMB drive is in: the process
    declares `case_sensitive=True` and the VOLUME folds case.

    `find_collision` is asked under the wrong table and answers `None`, exactly
    as it did before. What changed is that the move then FAILS instead of
    replacing 22 bytes the person cannot get back.
    """
    if not case_insensitive_root:
        pytest.skip("this volume does not fold case, so the mis-declaration "
                    "under test is not a mis-declaration here")

    plan, source = plan_a_move(p12_conn, landscape, ids,
                               volume_of=lambda p: "vol-main")
    destination = Path(plan.resolved_destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    incumbent = destination.parent / destination.name.swapcase()
    incumbent.write_bytes(b"THE PERSON'S ONLY COPY")

    assert find_collision(destination.parent, destination.name,
                          constraints=CONSTRAINTS) is None, (
        "the wrong declaration still misses the collision; if this ever passes "
        "the volume stopped folding and the test below proves nothing")

    record = _apply(p12_conn, plan, source_root=fixture_root,
                    destination_root=fixture_root, now=clock, mint_id=ids,
                    constraints=CONSTRAINTS)

    assert incumbent.read_bytes() == b"THE PERSON'S ONLY COPY"
    assert record.result == result_of(v.STALE, v.DESTINATION_CHANGED)
    assert source.exists(), "nothing moved, so the file is still where it was"


def test_the_person_is_told_the_destination_changed_rather_than_handed_a_traceback(
        p12_conn, landscape, ids, fixture_root, clock, case_insensitive_root):
    """The refusal reaches the report as a sentence `66` §10 already carries.

    Before the fix `_atomic_rename`'s `FileExistsError` was uncaught: it left
    `apply_selected` as a traceback, after `_create_directories` had already
    written to disk, with no execution record and no event. A stop that is not
    recorded is a stop nobody can be told about.
    """
    if not case_insensitive_root:
        pytest.skip("this volume does not fold case")
    plan, source = plan_a_move(p12_conn, landscape, ids,
                               volume_of=lambda p: "vol-main")
    destination = Path(plan.resolved_destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    (destination.parent / destination.name.swapcase()).write_bytes(b"ONLY COPY")

    record = _apply(p12_conn, plan, source_root=fixture_root,
                    destination_root=fixture_root, now=clock, mint_id=ids,
                    constraints=CONSTRAINTS)

    assert v.decline_message(record.result) == (
        "The destination changed after the preview.")
    stored = p12_conn.execute(
        "SELECT COUNT(*) FROM execution_records WHERE plan_id = ?",
        (plan.plan_id,)).fetchone()[0]
    assert stored == 1, "the stop is on the record, not only in a traceback"


def test_a_correctly_declared_folding_volume_still_stops_at_the_collision(
        p12_conn, landscape, ids, fixture_root, clock, case_insensitive_root):
    """The control. A right declaration reaches the COLLISION branch, not the
    syscall -- so the belt has not swallowed the path that was already correct."""
    if not case_insensitive_root:
        pytest.skip("this volume does not fold case")
    plan, source = plan_a_move(p12_conn, landscape, ids,
                               volume_of=lambda p: "vol-main")
    destination = Path(plan.resolved_destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    incumbent = destination.parent / destination.name.swapcase()
    incumbent.write_bytes(b"THE PERSON'S ONLY COPY")

    record = _apply(p12_conn, plan, source_root=fixture_root,
                    destination_root=fixture_root, now=clock, mint_id=ids,
                    constraints=FOLDING_CONSTRAINTS)

    assert incumbent.read_bytes() == b"THE PERSON'S ONLY COPY"
    assert record.result != result_of(v.STALE, v.DESTINATION_CHANGED), (
        "a declared collision must be resolved by the collision policy, not "
        "left to the system call")


# ---------------------------------------------------------------------------
# AP-02. `undo` re-checks at the syscall, not only two file hashes earlier.
# ---------------------------------------------------------------------------


def test_undo_does_not_overwrite_a_file_that_appears_at_the_source(
        p12_conn, landscape, ids, fixture_root, clock, monkeypatch):
    """`undo` asks question 4, then hashes the file twice, then moves it back.

    Anything that lands at the source in that window used to be replaced with no
    record that it had ever been there. The concurrent writer is simulated by
    having the LAST thing `undo` does before the move -- `verify_content` --
    create the file, which is a faithful stand-in for a sync client, an editor
    autosave, or the person reopening the folder they just emptied.

    This one needs no misconfiguration: it was reachable on a correctly declared
    macOS volume, which is why the constraints here are the right ones.
    """
    plan, source = plan_a_move(p12_conn, landscape, ids,
                               volume_of=lambda p: "vol-main")
    record = _apply(p12_conn, plan, source_root=fixture_root,
                    destination_root=fixture_root, now=clock, mint_id=ids,
                    constraints=FOLDING_CONSTRAINTS)
    assert record.result == v.APPLIED, record.result
    assert not source.exists()

    real_verify = undo_module.verify_content
    dropped = {"done": False}

    def racing_verify(*args, **kwargs):
        if not dropped["done"]:
            dropped["done"] = True
            source.write_bytes(b"THE PERSON'S NEW WORK, WRITTEN WHILE UNDO RAN")
        return real_verify(*args, **kwargs)

    monkeypatch.setattr(undo_module, "verify_content", racing_verify)

    entry = entries_for_plan(p12_conn, plan.plan_id)[0]
    verdict = undo(p12_conn, entry.entry_id, constraints=FOLDING_CONSTRAINTS,
                   unverified_copy_disposition=None,
                   normalize_filename=lambda n: n, scan_state="included",
                   materialized=True, component_version="probe", user_id=None,
                   now=clock, mint_id=ids)

    assert source.read_bytes() == b"THE PERSON'S NEW WORK, WRITTEN WHILE UNDO RAN"
    assert not verdict.reversed_successfully
    assert verdict.verdict == v.CONFLICT_SOURCE_PATH_OCCUPIED
    assert Path(entry.destination_path).exists(), (
        "a conflict performs no mutation: the filed file is where it was")


def test_the_undo_conflict_is_recorded_and_has_its_own_sentence(
        p12_conn, landscape, ids, fixture_root, clock, monkeypatch):
    """The person is told what happened, in the words `66` §11 already has."""
    plan, source = plan_a_move(p12_conn, landscape, ids,
                               volume_of=lambda p: "vol-main")
    _apply(p12_conn, plan, source_root=fixture_root,
           destination_root=fixture_root, now=clock, mint_id=ids,
           constraints=FOLDING_CONSTRAINTS)
    real_verify = undo_module.verify_content
    dropped = {"done": False}

    def racing_verify(*args, **kwargs):
        if not dropped["done"]:
            dropped["done"] = True
            source.write_bytes(b"NEW WORK")
        return real_verify(*args, **kwargs)

    monkeypatch.setattr(undo_module, "verify_content", racing_verify)
    entry = entries_for_plan(p12_conn, plan.plan_id)[0]
    verdict = undo(p12_conn, entry.entry_id, constraints=FOLDING_CONSTRAINTS,
                   unverified_copy_disposition=None,
                   normalize_filename=lambda n: n, scan_state="included",
                   materialized=True, component_version="probe", user_id=None,
                   now=clock, mint_id=ids)
    assert v.decline_message(verdict.verdict).startswith(
        "Undoing this would write over a different file")
    assert verdict.detail.get("detected") == (
        "at the move, between the check and the reversal")


# ---------------------------------------------------------------------------
# AP-03. The destination is inside the destination root, checked on the
# RESOLVED path -- `is_relative_to` alone is lexical and would pass a traversal.
# ---------------------------------------------------------------------------


def test_is_relative_to_alone_would_pass_a_traversal(tmp_path):
    """Why the containment check resolves both sides. Asserted, because the
    obvious fix looks like it works and does not."""
    root = tmp_path / "corpus"
    (root / "Documents" / "Coursework").mkdir(parents=True)
    (tmp_path / "OUTSIDE").mkdir()
    escaping = root / "Documents" / "Coursework" / ".." / ".." / ".." / "OUTSIDE" / "x"

    assert escaping.is_relative_to(root), (
        "lexical containment passes it -- this is the trap")
    assert not escaping.resolve().is_relative_to(root.resolve()), (
        "resolving both sides is what catches it")


def test_a_name_made_only_of_dots_is_refused_as_a_name(tmp_path):
    """`resolve_name` used to return `..`, `.`, `...` and `~` unchanged under
    the CLI's own table: `prohibited_characters` is {'/', '\\0', ':'} and
    `reserved_names` is empty, so nothing had an opinion about a name of dots.

    A dots-only component is a path traversal component, not a name, on every
    filesystem -- so this is structural and belongs beside `ALWAYS_PROHIBITED`
    rather than in an injected table.
    """
    from mutation.constraints import FilesystemConstraints
    from mutation.names import NameUnresolvable, resolve_name

    cli_table = FilesystemConstraints(
        unicode_form="NFC", case_sensitive=False, max_component_bytes=255,
        max_path_bytes=1024, prohibited_characters=frozenset({"/", "\0", ":"}),
        reserved_names=frozenset(), replacement_character="_")

    for traversal in ("..", ".", "...", "...."):
        with pytest.raises(NameUnresolvable):
            resolve_name(traversal, constraints=cli_table,
                         directory_byte_length=len(str(tmp_path).encode()),
                         has_extension=False)

    # A name that merely CONTAINS dots is a name and is untouched.
    kept = resolve_name("..hidden.txt", constraints=cli_table,
                        directory_byte_length=len(str(tmp_path).encode()),
                        has_extension=True)
    assert kept.filesystem_safe_name == "..hidden.txt"


def test_a_destination_outside_the_destination_root_is_refused_and_nothing_is_created(
        p12_conn, landscape, ids, fixture_root, clock, tmp_path):
    """The boundary `apply_plan` never had. `destination_root` was passed to
    `inspect_objects`, which used it for `if not root.exists()` and nothing else.

    The check is at the TOP of `apply_plan`, before `inspect_objects`, because
    `_create_directories` would otherwise `mkdir` outside the root before any
    move was attempted -- a refusal that has already built folders in somebody's
    home directory is not a refusal.
    """
    import dataclasses

    outside = fixture_root.parent / "OUTSIDE"
    outside.mkdir()
    plan, source = plan_a_move(p12_conn, landscape, ids,
                               volume_of=lambda p: "vol-main")
    # Enough `..` to leave `fixture_root` entirely and land in a sibling of it
    # -- a directory the person never approved and the run was never pointed at.
    up = Path(plan.resolved_destination_path).parent
    depth = len(up.relative_to(fixture_root).parts) + 1
    escaped = up.joinpath(*([".."] * depth), outside.name, "landed.txt")
    plan = dataclasses.replace(plan, resolved_destination_path=str(escaped))

    record = _apply(p12_conn, plan, source_root=fixture_root,
                    destination_root=fixture_root, now=clock, mint_id=ids)

    assert record.result == result_of(v.REFUSED, v.NODE_REFUSES_PLACEMENT)
    assert list(outside.iterdir()) == [], "nothing was written outside the root"
    assert source.exists(), "the person's file is where it was"
    assert record.directories_created_by_this_action == ()


def test_a_measured_table_files_the_file_and_still_catches_the_twin(
        p12_conn, landscape, ids, fixture_root, clock, truthful_constraints):
    """The state the composition root now puts a person in: the table was READ
    off their volume rather than inferred from `sys.platform`.

    Both halves matter. An ordinary move must still work -- a fix that made the
    product refuse everything would pass every test above -- and a twin the
    person cannot tell apart must still be caught by the COLLISION branch, where
    it can be explained, rather than by the system call, where it can only be
    refused.
    """
    plan, source = plan_a_move(p12_conn, landscape, ids,
                               volume_of=lambda p: "vol-main")
    record = _apply(p12_conn, plan, source_root=fixture_root,
                    destination_root=fixture_root, now=clock, mint_id=ids,
                    constraints=truthful_constraints)
    assert record.result == v.APPLIED
    assert Path(record.final_destination_path).read_bytes() == b"PHYS1401 syllabus"
    assert not source.exists()

    # And the twin, under the same measured table.
    filed = Path(record.final_destination_path)
    twin = filed.parent / filed.name.swapcase()
    assert (find_collision(filed.parent, twin.name,
                           constraints=truthful_constraints) is not None) is (
        not truthful_constraints.case_sensitive), (
        "the measured table and the volume must agree about the twin")
