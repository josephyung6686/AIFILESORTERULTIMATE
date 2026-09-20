"""Freezing again supersedes the plan before it, and the database says so.

`00` amendment 38, the owner's ruling of 2026-09-20. `110`'s Decision 5 --
recorded as unruled and deliberately out of scope by
`test_a_freeze_that_approved_nothing.py`'s docstring, which this file is the
sequel to -- is ruled: THE LATEST FREEZE GOVERNS, AND IT SAYS SO IN THE DATABASE.

**`--apply` already behaved this way and only by accident.** `latest_freeze` is
`MAX(created_at)` over `move_plans` and two invocations cannot share a timestamp,
so the newer batch won by the clock. Nothing DECLARED it, and two defects grew in
that gap: a re-freeze that wrote no plans left the earlier batch governing while
the screen said it was replaced, and one file could hold two destinations inside
one version because `freeze()` alone never took `placement.versions._current`.

So the assertion below is in two halves and both are needed. **The disk half
passes today** -- it is the regression pin that says the ruling changed which
plan governs in the database and not which files move. **The
`plan_versions.state` half is the ruling**, and it is the half that was red.

**THE WORLD HERE IS BIGGER THAN `conftest.py`'s IN EXACTLY ONE WAY: two plan
versions, with rows in `plan_versions`.** The shared fixture freezes twice under
one constant `PLAN_VERSION`, which is a shape a real run cannot produce --
`cli.py`'s `run_token` mints a fresh version per run -- and a version cannot
supersede itself, which is why nothing there is superseded and why P10's tables
are not in that conftest. They are created here, in the one file that needs them.
"""
from __future__ import annotations

import dataclasses

from mutation import vocabulary as v

from tree_design.records import PlanVersion
from tree_design.schema import create_tree_schema
from tree_design.store import freeze_version, write_plan_version

from apply_run.freeze import frozen_plans

from .test_apply_and_undo import _apply
from .test_freeze import _freeze

#: The two runs. Two ids because `cli.py` mints one per run, and the whole
#: question this file asks is what the second does to the first.
FIRST = "plan-first-sitting"
SECOND = "plan-second-sitting"


def _a_version(conn, plan_version_id: str) -> None:
    """One plan version, written the way the product writes one: draft, frozen.

    DRAFT FIRST AND FROZEN AFTER, which is `tests/integration/
    test_the_sort_is_frozen_and_applied_on_a_copy.py`'s reason at the same seam:
    a tree is built and then approved, and `write_node` refuses a frozen version
    outright. Nothing is built into this one -- `freeze` is handed its nodes --
    but the state a row arrives in is the product's own order and not a shortcut.
    """
    write_plan_version(conn, PlanVersion(
        plan_version_id=plan_version_id, predecessor_id=None, state="draft",
        created_at="2026-09-20T00:00:00Z", cross_folder_moves=True,
        selection_id=f"selection-{plan_version_id}"))
    freeze_version(conn, plan_version_id)


def _under(decisions, plan_version: str):
    return tuple(dataclasses.replace(decision, plan_version=plan_version)
                 for decision in decisions)


def _state(conn, plan_version_id: str) -> str:
    return conn.execute(
        "SELECT state FROM plan_versions WHERE plan_version_id = ?",
        (plan_version_id,)).fetchone()["state"]


def test_freezing_again_supersedes_the_plan_before_it_in_the_database(
        world, ids, clock):
    """Two sittings, and the database says which one governs.

    The `state` assertions are the ruling. The disk assertions beneath them are
    what the ruling is ABOUT: a claim about which plan governs is only true or
    false against what the apply gesture then does, which is the rule
    `test_a_freeze_that_approved_nothing.py` set for this question.
    """
    create_tree_schema(world.conn)
    _a_version(world.conn, FIRST)
    _a_version(world.conn, SECOND)

    first = _freeze(world, _under(world.decisions, FIRST), ids=ids, clock=clock)
    world.conn.commit()
    assert len(first.plans) == 4, "the premise: a first sitting approved four"

    # The second sitting approves ONE of the same four -- the article -- so the
    # two batches overlap rather than being about different files. A person who
    # froze everything and then froze one thing meant the one thing.
    article = tuple(decision for decision in world.decisions
                    if decision.destination.node_id == "n-read")
    second = _freeze(world, _under(article, SECOND), ids=ids, clock=clock)
    world.conn.commit()
    assert len(second.plans) == 1, "the premise: a second sitting approved one"

    # --- THE RULING. Stated in the database, not derived from a clock.
    assert _state(world.conn, FIRST) == "superseded", (
        "the plan before it is still called frozen; amendment 38 says freezing "
        "again supersedes it AND SAYS SO IN THE DATABASE")
    assert _state(world.conn, SECOND) == "frozen", (
        "the freeze superseded the version it had just written into")

    # --- THE DISK. Which set `--apply` then acts on, file for file.
    live = frozen_plans(world.conn)
    assert {plan.plan_id for plan in live} == {second.plans[0].plan_id}
    outcome = _apply(world, live, ids=ids, clock=clock)
    assert [item.result for item in outcome.outcomes] == [v.APPLIED]
    assert (world.documents / "Reading Inbox" / "saved article.pdf").exists()
    # And not one file of the superseded batch moved.
    for name in ("Syllabus.pdf", "Homework 3.pdf", "passport scan.pdf"):
        assert (world.inbox / name).exists(), (
            f"{name} moved under a plan the database calls superseded")
    assert not (world.documents / "Coursework").exists()


def test_a_freeze_that_approved_nothing_supersedes_nothing(world, ids, clock):
    """The 20 Sep defect, read against the ruling that closed its root cause.

    A freeze that writes no plans replaces nothing -- `MAX(created_at)` does not
    move when no row is written, and the earlier batch is still the approved set
    and still what `--apply` acts on. The ruling does not change that and must
    not: superseding on a freeze that approved nothing would take a person's
    approved plan away and leave them with none.

    `test_a_freeze_that_approved_nothing.py` owns the screen and the disk for
    this case. What is asserted HERE is the one fact that file could not assert
    because the ruling did not exist: the database is not marked either.
    """
    from placement.vocabulary import BLOCKED_PENDING_USER

    create_tree_schema(world.conn)
    _a_version(world.conn, FIRST)
    _a_version(world.conn, SECOND)

    first = _freeze(world, _under(world.decisions, FIRST), ids=ids, clock=clock)
    world.conn.commit()
    assert len(first.plans) == 4

    nothing_was_looked_at = tuple(
        dataclasses.replace(decision, review_policy=BLOCKED_PENDING_USER)
        for decision in _under(world.decisions, SECOND))
    second = _freeze(world, nothing_was_looked_at, ids=ids, clock=clock)
    world.conn.commit()
    assert second.plans == (), "the premise: this freeze approved nothing"

    assert _state(world.conn, FIRST) == "frozen", (
        "a freeze that approved nothing called the earlier plan superseded; it "
        "is still the approved set and still what --apply moves")
    assert {plan.plan_id for plan in frozen_plans(world.conn)} == {
        plan.plan_id for plan in first.plans}
