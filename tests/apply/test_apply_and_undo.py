"""Moving a person's real files, and taking it back.

Real bytes, a real database, real directories. Everything the run needs that is
a number, a sentence or a platform fact is passed in from here, because here is
standing in for `src/cli.py`.
"""
from __future__ import annotations

from mutation import vocabulary as v

from apply_run.branches import branches_named
from apply_run.run import (
    CROSS_VOLUME_UNRULED, already_applied, applied_entries, apply_selected,
    plans_under, sentence_for, take_back,
)

from .conftest import CONSTRAINTS, LEGAL, NODES
from .test_freeze import _freeze

#: `74` §8 Q7 is unruled, so the composition root supplies the sentence rather
#: than a default living inside the package. This is the test's copy of it.
CROSS_VOLUME_SENTENCE = (
    "This move would cross to another drive, and what happens to a copy that "
    "cannot be confirmed is not settled yet, so nothing was moved.")

#: `74` §8 Q6 is unruled. The halt set is injected; this is the reading the
#: tests exercise -- keep going past every stop that left the disk untouched,
#: stop at one that did not.
HALT_ON = frozenset({v.FAILED})


def _apply(world, plans, *, ids, clock, volume=lambda path: "vol-main"):
    return apply_selected(
        world.conn, plans, legal_destination_ids=LEGAL,
        source_root=world.root, destination_root=world.root,
        extra_protected=None, conflict_copies=lambda path: (),
        dataless_of=lambda path: False, approval_for=lambda plan_id: None,
        constraints=CONSTRAINTS, normalize_filename=lambda name: name,
        unruled_cross_volume_sentence=CROSS_VOLUME_SENTENCE,
        halt_on=HALT_ON, scan_state="included", materialized=True,
        component_version="apply-test", user_id="user-1",
        now=clock, mint_id=ids)


def _take_back(world, entries, *, ids, clock):
    return take_back(
        world.conn, entries, constraints=CONSTRAINTS,
        normalize_filename=lambda name: name, scan_state="included",
        materialized=True, component_version="apply-test", user_id="user-1",
        now=clock, mint_id=ids)


def _selected(plans, *names):
    return plans_under(plans, branches_named(names, nodes=NODES))


# --- what a branch selects ---------------------------------------------------


def test_one_branch_moves_and_the_other_does_not(world, ids, clock):
    plans = _freeze(world, world.decisions, ids=ids, clock=clock).plans
    article = world.documents / "Reading Inbox" / "saved article.pdf"

    outcome = _apply(world, _selected(plans, "Reading Inbox"), ids=ids,
                     clock=clock)

    assert [item.result for item in outcome.outcomes] == [v.APPLIED]
    assert article.read_bytes() == b"an article saved to read later"
    # Nothing else was touched, and no folder for another branch was made.
    for name in ("Syllabus.pdf", "Homework 3.pdf", "passport scan.pdf"):
        assert (world.inbox / name).exists()
    assert not (world.documents / "Coursework").exists()


def test_naming_a_parent_moves_its_whole_subtree(world, ids, clock):
    plans = _freeze(world, world.decisions, ids=ids, clock=clock).plans
    outcome = _apply(world, _selected(plans, "Coursework"), ids=ids, clock=clock)

    applied = [item for item in outcome.outcomes if item.result == v.APPLIED]
    assert len(applied) == 2
    assert (world.documents / "Coursework" / "PHYS1401"
            / "Syllabus.pdf").exists()
    assert (world.documents / "Coursework" / "PHYS1401" / "Homework"
            / "Homework 3.pdf").exists()


def test_naming_a_deep_branch_leaves_its_siblings_alone(world, ids, clock):
    plans = _freeze(world, world.decisions, ids=ids, clock=clock).plans
    _apply(world, _selected(plans, "Homework"), ids=ids, clock=clock)

    assert (world.documents / "Coursework" / "PHYS1401" / "Homework"
            / "Homework 3.pdf").exists()
    assert (world.inbox / "Syllabus.pdf").exists()


# --- the standing rules ------------------------------------------------------


def test_a_protected_file_is_refused_by_name_and_never_silently_skipped(
        world, ids, clock):
    """`84` §1: marked and counted, never opened, never silently omitted."""
    plans = _freeze(world, world.decisions, ids=ids, clock=clock).plans
    outcome = _apply(world, _selected(plans, "Coursework"), ids=ids, clock=clock)

    refused = [item for item in outcome.outcomes if item.result != v.APPLIED]
    assert len(refused) == 1
    assert refused[0].result == f"{v.REFUSED}:{v.PROTECTED_WITHOUT_POLICY}"
    assert refused[0].sentence == "This item is protected by your privacy policy."
    # It is in the outcome list at all -- that is what "never silently omitted"
    # means here -- and its bytes are where they were.
    assert (world.inbox / "passport scan.pdf").read_bytes() == \
        b"passport number redacted"


def test_a_file_changed_after_the_freeze_is_stale_and_the_others_still_move(
        world, ids, clock):
    """`00`:171 -- a plan whose file changed is not applied to the new file."""
    plans = _freeze(world, world.decisions, ids=ids, clock=clock).plans
    (world.inbox / "Syllabus.pdf").write_bytes(b"a completely different syllabus")

    outcome = _apply(world, _selected(plans, "Coursework"), ids=ids, clock=clock)

    by_name = {item.source_path.rsplit("/", 1)[-1]: item
               for item in outcome.outcomes}
    assert by_name["Syllabus.pdf"].result == f"{v.STALE}:{v.CONTENT_HASH_DIFFERS}"
    assert by_name["Syllabus.pdf"].sentence == "This file changed after the preview."
    assert (world.inbox / "Syllabus.pdf").exists()
    # And the run did not stop: the homework beside it still moved.
    assert by_name["Homework 3.pdf"].result == v.APPLIED


def test_a_move_that_would_cross_a_drive_refuses_with_the_injected_sentence(
        world, ids, clock):
    """`74` §8 Q7 is unruled. Nothing here decides it; the move stops."""
    volumes = {str(world.inbox): "vol-a"}
    plans = _freeze(world, world.decisions, ids=ids, clock=clock,
                    volume=lambda path: volumes.get(str(path.parent), "vol-b")).plans

    outcome = _apply(world, _selected(plans, "Reading Inbox"), ids=ids,
                     clock=clock)

    assert outcome.outcomes[0].result == CROSS_VOLUME_UNRULED
    assert outcome.outcomes[0].sentence == CROSS_VOLUME_SENTENCE
    # The disk is untouched: `apply_plan` demands the disposition BEFORE it
    # touches anything, so there is no half-made copy to account for.
    assert (world.inbox / "saved article.pdf").exists()
    assert not (world.documents / "Reading Inbox").exists()


def test_a_plan_that_already_ran_is_known_to_have_run_not_retried(
        world, ids, clock):
    """Typing the same `--apply` twice is an ordinary thing for a person to do.

    A frozen plan stays in the approved set after it runs. Handing it back to
    `apply_plan` gets a sentence about an unavailable drive, which is true of
    the source path and false about the person's situation.
    """
    plans = _freeze(world, world.decisions, ids=ids, clock=clock).plans
    selected = _selected(plans, "Reading Inbox")
    assert _apply(world, selected, ids=ids, clock=clock).outcomes[0].result == \
        v.APPLIED
    world.conn.commit()

    assert already_applied(world.conn, selected) == {selected[0].plan_id}
    # And after it is taken back, it is applicable again.
    entries = [entry for entry, _ in applied_entries(world.conn)]
    _take_back(world, entries, ids=ids, clock=clock)
    world.conn.commit()
    assert already_applied(world.conn, selected) == frozenset()


def test_selecting_no_plans_is_an_empty_run_and_not_a_silent_everything(
        world, ids, clock):
    _freeze(world, world.decisions, ids=ids, clock=clock)
    outcome = _apply(world, (), ids=ids, clock=clock)
    assert outcome.outcomes == ()
    assert not (world.documents / "Coursework").exists()
    assert not (world.documents / "Reading Inbox").exists()


# --- taking it back ----------------------------------------------------------


def test_undo_puts_the_bytes_back_and_removes_only_the_folders_it_made(
        world, ids, clock):
    plans = _freeze(world, world.decisions, ids=ids, clock=clock).plans
    _apply(world, _selected(plans, "Coursework"), ids=ids, clock=clock)
    world.conn.commit()

    entries = [entry for entry, _ in applied_entries(world.conn)]
    assert len(entries) == 2

    outcome = _take_back(world, entries, ids=ids, clock=clock)
    assert [item.verdict.verdict for item in outcome.outcomes] == [
        v.REVERSED, v.REVERSED]

    assert (world.inbox / "Syllabus.pdf").read_bytes() == b"PHYS1401 syllabus"
    assert (world.inbox / "Homework 3.pdf").read_bytes() == \
        b"problem 1: a block on a ramp"
    # Every folder the product made is gone; every folder the person made stays.
    assert not (world.documents / "Coursework").exists()
    assert world.inbox.exists() and world.documents.exists()


def test_undoing_one_branch_keeps_a_parent_the_other_branch_still_needs(
        world, ids, clock):
    """`mutation.directories` refuses to remove a folder another entry uses."""
    plans = _freeze(world, world.decisions, ids=ids, clock=clock).plans
    _apply(world, _selected(plans, "Coursework"), ids=ids, clock=clock)
    world.conn.commit()

    homework = [entry for entry, node in applied_entries(world.conn)
                if node == "n-hw"]
    outcome = _take_back(world, homework, ids=ids, clock=clock)

    assert outcome.outcomes[0].verdict.verdict == v.REVERSED
    assert (world.inbox / "Homework 3.pdf").exists()
    assert not (world.documents / "Coursework" / "PHYS1401"
                / "Homework").exists()
    # The syllabus is still filed, so its folders are still there.
    assert (world.documents / "Coursework" / "PHYS1401"
            / "Syllabus.pdf").exists()


def test_undoing_a_file_the_person_edited_afterwards_refuses_and_says_why(
        world, ids, clock):
    """`00`:175 -- undo surfaces a conflict rather than forcing a rollback."""
    plans = _freeze(world, world.decisions, ids=ids, clock=clock).plans
    _apply(world, _selected(plans, "Reading Inbox"), ids=ids, clock=clock)
    world.conn.commit()
    filed = world.documents / "Reading Inbox" / "saved article.pdf"
    filed.write_bytes(b"the article, with my notes added")

    entries = [entry for entry, _ in applied_entries(world.conn)]
    outcome = _take_back(world, entries, ids=ids, clock=clock)

    assert outcome.outcomes[0].verdict.verdict == \
        v.CONFLICT_DESTINATION_CONTENT_CHANGED
    assert outcome.outcomes[0].sentence == (
        "This action cannot be undone automatically because the file changed "
        "after it was moved.")
    assert filed.read_bytes() == b"the article, with my notes added"
    assert not (world.inbox / "saved article.pdf").exists()


def test_an_entry_already_reversed_is_reported_not_reversed_twice(
        world, ids, clock):
    plans = _freeze(world, world.decisions, ids=ids, clock=clock).plans
    _apply(world, _selected(plans, "Reading Inbox"), ids=ids, clock=clock)
    world.conn.commit()
    entries = [entry for entry, _ in applied_entries(world.conn)]
    _take_back(world, entries, ids=ids, clock=clock)
    world.conn.commit()

    # `applied_entries` no longer offers it, which is the real guard.
    assert applied_entries(world.conn) == ()


# --- the sentences -----------------------------------------------------------


def test_every_stop_a_run_can_produce_has_a_sentence(world, ids, clock):
    for result in (f"{v.REFUSED}:{v.PROTECTED_WITHOUT_POLICY}",
                   f"{v.STALE}:{v.CONTENT_HASH_DIFFERS}",
                   f"{v.PAUSED}:{v.AWAITING_COLLISION_DECISION}",
                   f"{v.FAILED}:{v.V3_HASH_MISMATCH}"):
        assert sentence_for(result, cross_volume=CROSS_VOLUME_SENTENCE)


def test_applied_has_no_stop_sentence():
    assert sentence_for(v.APPLIED, cross_volume=CROSS_VOLUME_SENTENCE) is None


def test_the_one_result_p12_has_no_sentence_for_uses_the_injected_one():
    """`74` §8 Q7's stop is not in P12's table, because the question is open."""
    assert sentence_for(CROSS_VOLUME_UNRULED,
                        cross_volume=CROSS_VOLUME_SENTENCE) == \
        CROSS_VOLUME_SENTENCE
