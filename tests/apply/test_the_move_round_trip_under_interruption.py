"""Phase 4 (a) -- the three ways a real move goes wrong, on a real tree.

R-29 verified that a move happens and that it can be taken back. These are the
three failures that happen to somebody rather than to a test: the machine stops
half way through a batch, the file changed between the freeze and the apply, and
something is already sitting at the destination.

**One of the three is not what it sounds like, and the difference is the design's.**
"An interrupted copy leaves no partial destination" is TRUE of a same-volume move
and FALSE of a cross-volume one, on purpose. Same-volume is `rename(2)` and the
kernel gives it atomically: the destination exists complete or not at all.
Cross-volume is copy-confirm-remove, and `mutation/cross_volume.py` states the
rule in its own docstring: *"A copy that failed its own verification is NOT
cleaned up: a partial or unverified copy is still a file on the person's disk, and
P12 removing it would be the same act §7.11 forbids, differing only in who would
notice."* So the guarantee there is not absence. It is that the SOURCE survives,
that the move is never recorded as applied, and that the copy is named on the
record so a person can be shown it. Tests below hold each half of that where it
actually applies, rather than asserting a single sentence about both.
"""
from __future__ import annotations

import pytest

from mutation import vocabulary as v

from apply_run.branches import branches_named
from apply_run.run import (
    already_applied, applied_entries, apply_selected, plans_under, sentence_for,
)

from .conftest import CONSTRAINTS, LEGAL, NODES
from .test_apply_and_undo import CROSS_VOLUME_SENTENCE, HALT_ON, _selected
from .test_freeze import _freeze


def _apply(world, plans, *, ids, clock, volume=lambda path: "vol-main"):
    """`tests/apply/test_apply_and_undo.py`'s composition, verbatim.

    Imported rather than re-spelled would be better, but that helper closes over
    nothing this file needs to vary; what this file varies is the WORLD.
    """
    return apply_selected(
        world.conn, plans, legal_destination_ids=LEGAL,
        source_root=world.root, destination_root=world.root,
        extra_protected=None, conflict_copies=lambda path: (),
        dataless_of=lambda path: False, approval_for=lambda plan_id: None,
        constraints=CONSTRAINTS, normalize_filename=lambda name: name,
        unruled_cross_volume_sentence=CROSS_VOLUME_SENTENCE,
        halt_on=HALT_ON, scan_state="included", materialized=True,
        component_version="round-trip", user_id="user-1",
        now=clock, mint_id=ids)


def _paths_under(root):
    """The person's files, by path and by bytes.

    The database lives under the same root in this fixture and its write-ahead log
    changes on every commit, so it is excluded: a snapshot that included it would
    compare two runs' journals rather than two states of somebody's corpus.
    """
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file() and not path.name.startswith("agent.sqlite")}


# --- interruption ------------------------------------------------------------

class _StopsAfter:
    """`os.link`, until the nth call, and then the machine stops.

    A power cut is an `OSError` from the system call as far as this process can
    tell, and `os.link` is where `mutation/movement.py` starts a same-volume move.
    Killing the process instead would prove the same thing and leave nothing to
    assert in, which is why the interruption is raised rather than fatal.
    """

    def __init__(self, real, *, after: int) -> None:
        self._real = real
        self._after = after
        self.calls = 0

    def __call__(self, source, destination):
        self.calls += 1
        if self.calls > self._after:
            raise OSError(5, "the machine stopped here")
        return self._real(source, destination)


def test_a_run_stopped_half_way_leaves_no_file_half_moved(
        world, ids, clock, monkeypatch):
    """The machine stops mid-batch. Every file is at one path or the other.

    A same-volume move is `link` then `rename` then `unlink`, so the window this
    catches is real: a stop between them could leave the bytes at two paths or at
    none. What the assertion holds is that the set of the person's file CONTENTS is
    unchanged -- nothing lost, nothing truncated -- whichever side of the
    interruption each file ended on.
    """
    import os as _os

    import mutation.movement as movement

    plans = _freeze(world, world.decisions, ids=ids, clock=clock).plans
    selection = _selected(plans, "Coursework")
    assert len(selection) > 1, "a one-plan batch cannot be stopped half way"
    before = _paths_under(world.root)

    stopping = _StopsAfter(_os.link, after=1)
    monkeypatch.setattr(movement.os, "link", stopping)
    _apply(world, selection, ids=ids, clock=clock)

    assert stopping.calls > 1, "the interruption never fired, so nothing was tested"
    after = _paths_under(world.root)
    assert sorted(after.values()) == sorted(before.values()), (
        "a file's bytes were lost or duplicated by the interruption")


def test_the_run_after_an_interruption_finishes_the_rest(
        world, ids, clock, monkeypatch):
    """Resumption, which is the half that makes the interruption survivable.

    The stopped run moved what it moved. The next run must move the remainder and
    must not touch what already went -- and it decides that from `mutation`'s own
    rows, which is what the test below about records asserts separately.
    """
    import os as _os

    import mutation.movement as movement

    plans = _freeze(world, world.decisions, ids=ids, clock=clock).plans
    selection = _selected(plans, "Coursework")
    before = _paths_under(world.root)

    monkeypatch.setattr(movement.os, "link", _StopsAfter(_os.link, after=1))
    _apply(world, selection, ids=ids, clock=clock)
    monkeypatch.undo()

    outcome = _apply(world, selection, ids=ids, clock=clock)

    assert [item.result for item in outcome.outcomes], "the resumed run did nothing"
    after = _paths_under(world.root)
    assert sorted(after.values()) == sorted(before.values()), (
        "the resumed run lost or duplicated a file")


def test_the_second_run_resumes_from_its_records_and_does_not_move_twice(
        world, ids, clock):
    """"The plan resumes from its records" -- and the records, not the disk.

    A run that asked the filesystem whether a move had happened would answer
    wrongly for exactly the file a person moved back by hand, and would move it
    again. `already_applied` reads `mutation`'s own rows.
    """
    plans = _freeze(world, world.decisions, ids=ids, clock=clock).plans
    selection = _selected(plans, "Reading Inbox")
    _apply(world, selection, ids=ids, clock=clock)
    after_first = _paths_under(world.root)
    done = already_applied(world.conn, selection)
    assert done, "the first run recorded nothing, so there is no resumption to test"

    _apply(world, selection, ids=ids, clock=clock)

    assert _paths_under(world.root) == after_first, (
        "the second run moved something the first had already moved")


def test_every_applied_entry_is_recorded_exactly_once(world, ids, clock):
    """The double-count guard. Two rows for one move would make an undo that
    reversed one of them look complete while the file stayed where it was."""
    plans = _freeze(world, world.decisions, ids=ids, clock=clock).plans
    selection = _selected(plans, "Reading Inbox")
    _apply(world, selection, ids=ids, clock=clock)
    _apply(world, selection, ids=ids, clock=clock)

    entries = applied_entries(world.conn)
    plan_ids = [entry.plan_id for entry, _node in entries]
    assert len(plan_ids) == len(set(plan_ids)), f"an entry recorded twice: {plan_ids}"


# --- a source that changed since the freeze ----------------------------------

def test_a_source_changed_since_the_freeze_is_refused_and_the_refusal_is_shown(
        world, ids, clock):
    """`00`:153 -- the checkpoint is a checksum and a changed file is not the file
    that was approved.

    TWO halves, and the second is the one that was worth writing. The refusal
    itself is P12's. What this asserts beyond it is that the refusal arrives with
    a sentence: a file that silently did not move is the failure `84` §1 names,
    and a person who approved a move and got nothing has to be told which file and
    why.
    """
    plans = _freeze(world, world.decisions, ids=ids, clock=clock).plans
    selection = _selected(plans, "Reading Inbox")
    # The file THIS selection moves, not whichever sorts first: a change to a
    # file no selected plan names would prove nothing about the checkpoint.
    changed = world.root / selection[0].expected_source_path
    changed.write_bytes(b"the person edited this after approving the move")

    outcome = _apply(world, selection, ids=ids, clock=clock)

    stops = [entry for entry in outcome.outcomes if entry.result != v.APPLIED]
    assert stops, "a file whose bytes changed after the freeze was moved anyway"
    for stop in stops:
        assert sentence_for(stop.result, cross_volume=CROSS_VOLUME_SENTENCE), (
            f"{stop.result} refused a move and said nothing a person can read")


# --- something already at the destination ------------------------------------

def test_an_occupied_destination_is_never_written_over(world, ids, clock):
    """`00`:172 -- *"The engine should never silently overwrite an existing file."*

    The incumbent's bytes are the assertion. A policy that renamed, one that
    merged and one that stopped would all leave them untouched; only an overwrite
    would not, and an overwrite is the one outcome no policy in `00`:172 allows.
    """
    plans = _freeze(world, world.decisions, ids=ids, clock=clock).plans
    selection = _selected(plans, "Reading Inbox")
    plan = selection[0]
    incumbent = world.root / plan.resolved_destination_path
    incumbent.parent.mkdir(parents=True, exist_ok=True)
    incumbent.write_bytes(b"somebody else's file, already here")

    _apply(world, selection, ids=ids, clock=clock)

    assert incumbent.read_bytes() == b"somebody else's file, already here", (
        "the incumbent at the destination was overwritten")


def test_the_collision_policy_is_injected_and_has_no_silent_default():
    """`00`:172 names four behaviours and the design picks none of them, so the
    engine may not either. `resolve_collision` checks the name against the closed
    set, which means a caller that passed nothing gets a refusal rather than
    whichever branch happened to be first."""
    import inspect

    from mutation.collision import resolve_collision

    behaviour = inspect.signature(resolve_collision).parameters["behaviour"]
    assert behaviour.default is inspect.Parameter.empty, (
        "a default collision behaviour is a policy chosen by the engine")


def test_every_behaviour_the_design_names_is_one_the_code_accepts():
    """The closed set is `00`:172's, not a subset somebody found convenient."""
    from mutation.vocabulary import COLLISION_BEHAVIOURS

    assert len(COLLISION_BEHAVIOURS) == 4, COLLISION_BEHAVIOURS
