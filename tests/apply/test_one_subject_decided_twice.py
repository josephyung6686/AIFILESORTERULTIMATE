"""One subject decided twice in one pass becomes ONE plan: the later decision.

`00` amendment 38 read at the smaller scale. THE LATEST FREEZE GOVERNS is a rule
about which decision stands, and dropping a row the run itself withdrew is that
same rule inside one pass instead of across two freezes.

**`freeze` WAS THE ONLY READER OF THE DECISION LIST THAT DID NOT FIRST TAKE
`placement.versions._current`.** `carry_onto` and `scoped_general_demand` both do,
and `_current`'s own docstring names the shape exactly: *"a subject can be decided
twice in one pass -- a group member placed by its packet and then resolved again
as shared material is the shape that does it."* So the freeze wrote a plan for the
withdrawn placement beside the one that stands, and `--apply` then had two
contradicting instructions for one of somebody's files. Measured before the guard
existed, the run moved the file under the first plan, met the second, and printed
that file as MOVED and, four lines lower, as needing a drive reconnected that was
never disconnected.

**THE ASSERTION IS WHICH, NOT HOW MANY.** A count of one proves the duplicate is
gone and says nothing about whether the run kept the decision it withdrew. The
surviving row has to be the LATER one -- in the database and then on the disk --
because that is the ruling; one plan carrying the abandoned destination would be
the same defect with a tidier screen.

**NOTHING IS SILENTLY OMITTED, and no hold reason is minted for the withdrawn
row.** `84` §1's rule is that a file is marked and counted, never dropped without
a sentence. The file IS counted: it is named once, under the decision the run
ended on. It was being counted TWICE, which is the count being wrong rather than
generous, and a person adding `Frozen` to the not-frozen block would have got back
more files than they gave it.
"""
from __future__ import annotations

import dataclasses

from mutation import vocabulary as v

from .conftest import NODES
from .test_apply_and_undo import _apply
from .test_freeze import _freeze

#: Where the run first put the syllabus, and where it put it when it reached the
#: same subject again. Two branches that do not share a parent, so "two
#: destinations" cannot be read as "one destination and its parent".
FIRST_ANSWER = "n-phys"
LATER_ANSWER = "n-read"


def _decided_twice(decisions):
    """The pass's own output: the syllabus decided, then decided again.

    `run_corpus` returns what it decided IN THE ORDER IT DECIDED IT, so the twin
    goes on the end -- which is what makes the second one later. Same `Subject`,
    a new `decision_id`, a different destination: the row the run withdrew, still
    in the list, which is the whole premise.
    """
    syllabus = next(decision for decision in decisions
                    if decision.destination.node_id == FIRST_ANSWER)
    later = dataclasses.replace(
        syllabus, decision_id="decision-resolved-again",
        destination=dataclasses.replace(syllabus.destination,
                                        node_id=LATER_ANSWER))
    return tuple(decisions) + (later,), syllabus.subject.file_id


def _rows_for(conn, file_id):
    return conn.execute(
        "SELECT node_id FROM move_plans WHERE file_id = ? "
        "AND superseded_by IS NULL ORDER BY record_id", (file_id,)).fetchall()


def test_a_subject_decided_twice_is_frozen_once_as_the_later_decision(
        world, ids, clock):
    """The database: one row, and it carries the destination the run ended on."""
    decisions, file_id = _decided_twice(world.decisions)

    proposal = _freeze(world, decisions, ids=ids, clock=clock)
    world.conn.commit()

    for_the_file = [plan for plan in proposal.plans if plan.file_id == file_id]
    assert len(for_the_file) == 1, (
        "the freeze approved one file for two folders: "
        f"{[plan.resolved_destination_path for plan in for_the_file]}")
    assert for_the_file[0].requested_destination_node == LATER_ANSWER, (
        "the surviving plan carries the destination the run WITHDREW")

    rows = _rows_for(world.conn, file_id)
    assert [row["node_id"] for row in rows] == [LATER_ANSWER]

    # And every other file is untouched by the deduplication: four subjects went
    # in, four came out, one row each.
    assert len(proposal.plans) == 4
    assert proposal.held == ()


def test_the_file_lands_where_the_later_decision_said_and_nowhere_else(
        world, ids, clock):
    """The disk, because a plan is a promise and the promise is kept in bytes."""
    decisions, file_id = _decided_twice(world.decisions)
    proposal = _freeze(world, decisions, ids=ids, clock=clock)
    world.conn.commit()

    outcome = _apply(world, [plan for plan in proposal.plans
                             if plan.file_id == file_id], ids=ids, clock=clock)

    # ONE OUTCOME, AND IT IS `applied`. The second plan is what produced the
    # measured defect: the file had already moved under the first, so the second
    # met no source and came back
    # `refused:source_or_destination_unavailable` -- the same file reported as
    # moved and, four lines lower, as needing a drive nobody had disconnected.
    assert [item.result for item in outcome.outcomes] == [v.APPLIED], (
        [(item.file_id, item.result) for item in outcome.outcomes])
    assert (world.documents / "Reading Inbox" / "Syllabus.pdf").exists(), (
        "the file is not where the run's last decision put it")
    assert not (world.documents / "Coursework" / "PHYS1401"
                / "Syllabus.pdf").exists(), (
        "the withdrawn placement reached the disk")


def test_the_count_a_person_reads_adds_up_to_the_corpus(world, ids, clock):
    """`84` §1: marked and counted, and counted ONCE.

    The freeze block's promise is that `Frozen` plus the files listed as still
    exactly where they are gives back the number of files a person handed in.
    A subject frozen twice broke that promise upward, which is the direction
    nobody checks.
    """
    decisions, _ = _decided_twice(world.decisions)
    proposal = _freeze(world, decisions, ids=ids, clock=clock)

    named = ({plan.file_id for plan in proposal.plans}
             | {item.file_id for item in proposal.held})
    assert named == set(world.sources)
    assert len(proposal.plans) + len(proposal.held) == len(world.sources)
    assert len(NODES) == 4, "the world this counts against"
