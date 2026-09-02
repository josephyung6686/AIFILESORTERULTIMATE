# tests/p11/test_p11_orphaned_set_decision.py
"""The set answers an earlier run recorded and this run cannot honour.

§7.6's decision is scoped to a plan version, and that is a live decision rather
than an oversight: `act_on_residual_sets` states it with its reason -- a later
run's set may hold different files, so applying an old answer unseen "would be
this product filing material against a screen nobody read." Every run mints a new
plan version, so `require_set_decision`, which reads `(plan_version, set_id)`,
can never match a previous run's row. It is not supposed to.

WHAT IS WRONG IS THE SILENCE, NOT THE SCOPE. The rows stay in
`residual_set_decisions` forever and nothing ever reads them again. A person who
filed eight photos into Review Later yesterday, and re-runs today, is shown a
plan with no trace of that answer and no sentence saying it was not carried
forward. Measured: the "Would go into Review Later" block is simply absent, and
the row is still in the table. `84` §6 -- a decision that no longer applies is
said out loud, never silently omitted.

So the missing piece is a READER, and this is it. It answers "what did they
decide last time that this run is not honouring?", in the words they read on the
screen -- which is why it joins `residual_sets` for the LABEL rather than
reporting `set_id`, a string that carries a plan version nobody has ever seen.

SCOPE: THE LAST RUN THAT DECIDED ANYTHING, AND NOT EVERY RUN EVER. A person who
has used this command for a month has a month of set answers in that table, and
naming all of them on every run would be a wall of text that says less than one
line. `plan_versions.predecessor_id` cannot be walked for this -- each run of
this command starts a fresh lineage root, measured -- so the ordering available
is `decided_at`, and the rule is the single most recent plan version other than
this one that carries any decision at all.
"""
from __future__ import annotations

import pytest

from database_agent.db import open_database
from placement.records import _require  # noqa: F401  (schema import side-effects)
from placement.residual import (
    ResidualSetDecision,
    prior_set_decisions,
    record_set_decision,
)
from placement.schema import create_placement_schema
from placement.vocabulary import LEAVE_IN_PLACE, SEND_TO_APPROVED_NODE

T1 = "2026-09-01T10:00:00+00:00"
T2 = "2026-09-02T10:00:00+00:00"
T3 = "2026-09-03T10:00:00+00:00"
VERSION = "version_aaa_2"


@pytest.fixture()
def db(tmp_path):
    conn = open_database(tmp_path / "holder" / "plan.sqlite")
    create_placement_schema(conn)
    yield conn
    conn.close()


def _surface(conn, *, plan_version: str, label: str, set_id: str) -> None:
    """One row in `residual_sets`, which is where the person-facing label lives.

    Written directly rather than through `surface_residual_sets`, because that
    function needs a whole placement pass to have run; what is under test here is
    the read, and the read's contract is the two columns it joins on.
    """
    conn.execute(
        "INSERT INTO residual_sets (record_id, plan_version, label, payload, "
        "created_at) VALUES (?, ?, ?, ?, ?)",
        (set_id, plan_version, label, "{}", T1))


def _decide(conn, *, plan_version: str, label: str, index: int, at: str,
            choice: str = SEND_TO_APPROVED_NODE, node_id: str | None = "node_1"):
    set_id = f"{plan_version}:{label}-{index}"
    _surface(conn, plan_version=plan_version, label=label, set_id=set_id)
    record_set_decision(
        conn,
        ResidualSetDecision(set_id=set_id, plan_version=plan_version,
                            choice=choice, node_id=node_id, decided_at=at),
        component_version="test", observed_at=at, user_id="jy")
    return set_id


def test_an_answer_from_the_last_run_is_named_with_the_words_it_was_given_in(db):
    """The whole point: the person gets back the label they typed, not a set_id."""
    _decide(db, plan_version="version_old_2", label="Not yet placed (1 of 8)",
            index=1, at=T1)

    prior = prior_set_decisions(db, plan_version=VERSION)

    assert [row.label for row in prior] == ["Not yet placed (1 of 8)"]
    assert prior[0].choice == SEND_TO_APPROVED_NODE
    assert prior[0].node_id == "node_1"
    assert prior[0].decided_at == T1


def test_this_runs_own_answers_are_not_reported_as_uncarried(db):
    """THE TWIN. A decision belonging to THIS plan version is being honoured right
    now, and naming it as not carried forward would be the product telling a
    person their answer was ignored on the very run that applied it.
    """
    _decide(db, plan_version=VERSION, label="Not yet placed (1 of 8)",
            index=1, at=T2)

    assert prior_set_decisions(db, plan_version=VERSION) == ()


def test_only_the_most_recent_earlier_run_is_named_not_every_run_ever(db):
    """A month of use must not become a month of lines on today's screen."""
    _decide(db, plan_version="version_jan_2", label="Not yet placed (1 of 8)",
            index=1, at=T1)
    _decide(db, plan_version="version_feb_2", label="Not yet placed (2 of 6)",
            index=2, at=T2)

    prior = prior_set_decisions(db, plan_version=VERSION)

    assert [row.label for row in prior] == ["Not yet placed (2 of 6)"]


def test_every_answer_from_that_one_run_is_named_and_none_is_dropped(db):
    """Not "the last decision" -- the last RUN's decisions. A person who sent
    three sets somewhere yesterday told the product three things.
    """
    _decide(db, plan_version="version_old_2", label="Not yet placed (1 of 8)",
            index=1, at=T1)
    _decide(db, plan_version="version_old_2", label="Not yet placed (2 of 8)",
            index=2, at=T1)
    _decide(db, plan_version="version_old_2", label="Protected, and not filed",
            index=3, at=T1, choice=LEAVE_IN_PLACE, node_id=None)

    prior = prior_set_decisions(db, plan_version=VERSION)

    assert [row.label for row in prior] == [
        "Not yet placed (1 of 8)", "Not yet placed (2 of 8)",
        "Protected, and not filed"]


def test_a_database_with_no_earlier_answer_reports_nothing_rather_than_raising(db):
    """The first run a person ever makes goes through this too."""
    assert prior_set_decisions(db, plan_version=VERSION) == ()


def test_a_superseded_answer_is_not_named_as_though_it_still_stood(db):
    """§8.2 keeps the old row readable; it does not keep it in force. Reporting a
    replaced answer as "what you decided last time" would name a decision the
    person had already taken back.

    TWO decisions in that run and only one superseded, which is the whole shape
    of the test. With a single superseded row the outer lookup that picks the
    previous plan version finds nothing and returns `()` for a reason that has
    nothing to do with the filter under test -- the first draft did exactly that
    and stayed green when the filter was deleted. A standing sibling keeps the
    version selectable, so the surviving row is the one thing this can be about.
    """
    superseded = _decide(db, plan_version="version_old_2",
                         label="Not yet placed (1 of 8)", index=1, at=T1)
    _decide(db, plan_version="version_old_2",
            label="Not yet placed (2 of 8)", index=2, at=T1)
    db.execute(
        "UPDATE residual_set_decisions SET superseded_by = ? WHERE set_id = ?",
        ("later", superseded))

    prior = prior_set_decisions(db, plan_version=VERSION)

    assert [row.label for row in prior] == ["Not yet placed (2 of 8)"]
