"""A freeze that approves nothing must not say the earlier plan is gone.

`84` §6 -- *"What the screen tells a person to type has to be true."* The screen
this file is about told a person two things at once:

    This replaces the 4 file(s) you froze on 2026-09-02T00:00:00Z. Anything
    from that plan you had already filed stays filed and can still be taken
    back.

    Nothing was frozen: no placement in this run is ready to move.

Both sentences came out of `freeze_lines`, one after the other, and the first is
FALSE. `apply_run.freeze.latest_freeze` is `MAX(created_at)` over `move_plans`,
nothing in `src/` ever writes `superseded_by` on a move plan (`grep -rn "UPDATE
move_plans" src/` returns nothing), and a freeze that writes no rows does not
move `MAX(created_at)`. So the earlier batch is not replaced by a freeze that
approved nothing -- it is STILL the approved set, and it is what `--apply` reads.

The person reads "your earlier plan is replaced" and "nothing was frozen this
time" and concludes there is nothing on the table. Then the apply gesture moves
the earlier batch's files. That is the whole defect, and it is why both tests
below end on the disk rather than on a string: a sentence about which plan
governs is only true or false against what the apply gesture actually does.

WHAT WAS NOT IN SCOPE, and is not fixed here. Which plan governs after a second
freeze was `110` §5 Decision 5 and the owner's, unruled when this was written.
Nothing in this file or in the change it drove writes `superseded_by`, writes
`plan_versions.state = 'superseded'`, deletes or hides the earlier batch, or
adds a gesture that would choose between the two. Reporting which plan governs
is not choosing which plan governs.

RULED LATER THE SAME DAY, and this file is untouched by it. `00` amendment 38
makes a freeze that approved plans of its own mark the versions it replaced
`'superseded'` -- and a freeze that approved NOTHING still marks nothing, which
is why every assertion below still holds and why it must. Superseding here would
take a person's approved plan away and leave them with none, which is a worse
screen than the false sentence this file closed.
`tests/apply/test_the_latest_freeze_governs.py` is the sequel and pins both
halves; what it adds for this case is the one fact this file could not assert,
that the database is not marked either.
"""
from __future__ import annotations

import dataclasses

from mutation import vocabulary as v

from placement.vocabulary import BLOCKED_PENDING_USER

from apply_run.freeze import frozen_plans
from apply_run.report import freeze_lines

from .conftest import NODES
from .test_apply_and_undo import _apply
from .test_freeze import _freeze
# One definition of the rule, and it is that test's: no line this package
# composes may spell a flag. `test_freeze_prints_the_command_it_was_given_and_
# invents_no_flag` runs it over a FIRST freeze, where `replaces` is `None` and
# the branch this file is about never executes -- so the guard is re-run here
# rather than assumed to have covered it.
from .test_report import _FLAG

#: Handed in by the composition root and never composed inside the package, so
#: a line offering the person a command can be told apart from a line that
#: merely mentions one.
APPLY_EVERYTHING = "THE-COMMAND-FOR-EVERYTHING"


def _screen(proposal, world) -> str:
    """The freeze block exactly as a person reads it, as one string."""
    return "\n".join(freeze_lines(
        proposal,
        names={file_id: path.name for file_id, path in world.sources.items()},
        nodes=NODES,
        apply_command=lambda branch: f"THE-COMMAND-FOR[{branch}]",
        apply_everything_command=APPLY_EVERYTHING))


def _nothing_was_looked_at(decisions):
    """The same corpus on a run whose privacy pass classified none of it.

    The smallest honest way to a freeze that writes zero plans.
    `apply_run.freeze._withheld` holds a `blocked_pending_user` placement under
    `awaiting_classification` -- `placement.privacy.blocked_policy`'s own
    distinction, that nothing has looked inside the file, so there is nothing
    there for a person to approve. Every decision withheld, every decision held,
    no `move_plans` row written.
    """
    return tuple(
        dataclasses.replace(decision, review_policy=BLOCKED_PENDING_USER)
        for decision in decisions)


def test_a_freeze_that_approved_nothing_does_not_call_the_earlier_plan_replaced(
        world, ids, clock):
    """Freeze, freeze again approving nothing, then move everything.

    The assertion is not that a particular sentence reads well. It is that the
    screen and the disk say the same thing: the plan the screen names as the one
    in force is the plan the apply gesture then acts on, file for file.
    """
    first = _freeze(world, world.decisions, ids=ids, clock=clock)
    world.conn.commit()
    assert len(first.plans) == 4

    second = _freeze(world, _nothing_was_looked_at(world.decisions),
                     ids=ids, clock=clock)
    world.conn.commit()
    assert second.plans == (), "the premise: this freeze approved nothing"
    assert len(second.held) == 4

    screen = _screen(second, world)

    # --- THE DISK. What the apply gesture does after that screen was printed.
    live = frozen_plans(world.conn)
    assert {plan.plan_id for plan in live} == {
        plan.plan_id for plan in first.plans}, (
        "the earlier batch is still the approved set: nothing supersedes it")
    outcome = _apply(world, live, ids=ids, clock=clock)
    moved = {item.file_id for item in outcome.outcomes
             if item.result == v.APPLIED}
    assert (world.documents / "Coursework" / "PHYS1401" / "Syllabus.pdf"
            ).exists()
    assert (world.documents / "Reading Inbox" / "saved article.pdf").exists()
    assert len(moved) == 3

    # --- THE SCREEN, against that.
    # The false sentence. It said the earlier plan was replaced; the three files
    # above moved under it.
    assert "This replaces" not in screen, (
        "the screen called the earlier plan replaced, and the apply gesture "
        "then moved it:\n" + screen)
    # And not silently omitted either, which is the other half: the plan that
    # governs is named, with the count and the moment it was frozen, and the
    # line that acts on it is on the screen.
    assert first.frozen_at in screen, screen
    assert "4 file(s)" in screen, screen
    assert APPLY_EVERYTHING in screen, screen
    assert _FLAG.search(screen) is None, _FLAG.search(screen).group(0)


def test_a_freeze_that_approved_fewer_files_still_replaces_the_earlier_one(
        world, ids, clock):
    """The companion that must stay green, and the case the sentence was for.

    A second freeze over one file really does replace a first over four: the
    other three are no longer approved and `--apply` will not move them. Buying
    honesty in the zero case by dropping the sentence everywhere would take this
    with it -- the person would never be told the other three had fallen out of
    the plan. So this ends on the disk too: the one file moves, and the three
    the earlier batch had approved are still in the folder they started in.
    """
    first = _freeze(world, world.decisions, ids=ids, clock=clock)
    world.conn.commit()
    second = _freeze(world, world.decisions[:1], ids=ids, clock=clock)
    world.conn.commit()
    assert len(second.plans) == 1

    screen = _screen(second, world)
    assert "This replaces the 4 file(s) you froze on " + first.frozen_at \
        in " ".join(screen.split()), screen

    live = frozen_plans(world.conn)
    assert {plan.plan_id for plan in live} == {second.plans[0].plan_id}
    outcome = _apply(world, live, ids=ids, clock=clock)
    assert [item.result for item in outcome.outcomes] == [v.APPLIED]
    assert (world.documents / "Coursework" / "PHYS1401" / "Syllabus.pdf"
            ).exists()
    # The three the earlier batch approved and this one did not are untouched.
    for name in ("Homework 3.pdf", "saved article.pdf", "passport scan.pdf"):
        assert (world.inbox / name).exists()
