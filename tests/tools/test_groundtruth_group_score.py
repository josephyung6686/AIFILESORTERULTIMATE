# tests/tools/test_groundtruth_group_score.py
"""`104` §18.100: the grouping stage has never been graded.

`tools/groundtruth/labels.py` has carried a hand-keyed `group` per file since
11 September and `tools/groundtruth/score.py` has never read it, so every
statement about grouping quality in this repository -- including the lead's --
rests on nothing. `106` Phases 3 and 4 both change what a group becomes, and
changing an ungraded thing is how `104` §18.99's first failure mode happens
again.

**WHAT THIS MEASURES, AND IT IS NOT PLACEMENT.** Two files the owner put in one
group belong in one group whatever folder the run chooses for them. A run that
splits them has failed at grouping even if it files both correctly, and
`score_sorting` cannot see that because each file is `exact` on its own -- the
same blind spot `family_cohesion` was written for, one stage earlier. So the
number is over the owner's own groups and never touches `destination`.
"""
from __future__ import annotations

from tools.groundtruth.score import group_cohesion


class _Label:
    def __init__(self, group, protected=False):
        self.group = group
        self.protected = protected


class _Obs:
    def __init__(self, group_ids):
        self.group_ids = tuple(group_ids)


def test_two_files_the_owner_grouped_and_the_run_grouped_are_kept_together():
    """The claim, at its smallest.

    SABOTAGE: compare `destination` instead of `group_ids`. That still passes on
    a run that files both files in one folder without grouping them at all, which
    is precisely the number the scorecard must not report.
    """
    labels = {"a": _Label("g1"), "b": _Label("g1")}
    observations = {"a": _Obs(["run-7"]), "b": _Obs(["run-7"])}

    assert group_cohesion(labels, observations) == (1, 1, ())


def test_two_files_the_owner_grouped_and_the_run_split_are_counted_split():
    """SABOTAGE: return `considered` for `together` unconditionally. Red here."""
    labels = {"a": _Label("g1"), "b": _Label("g1")}
    observations = {"a": _Obs(["run-7"]), "b": _Obs(["run-9"])}

    assert group_cohesion(labels, observations) == (0, 1, ("g1",))


def test_a_group_the_run_never_formed_is_counted_and_not_skipped():
    """A file in none of the run's groups is not a file the run got right.

    `00`:259 one stage earlier: a file nobody decided about must not read as a
    file understood and found unimportant, and a group nobody formed must not
    read as a group there was nothing to say about.

    SABOTAGE: `if not observation.group_ids: continue`. Then a run with an empty
    `groups` table scores 0 of 0 and prints as perfect -- and `104` §18.100
    recorded exactly such a database sitting in the same directory as the real
    one.
    """
    labels = {"a": _Label("g1"), "b": _Label("g1")}
    observations = {"a": _Obs([]), "b": _Obs([])}

    assert group_cohesion(labels, observations) == (0, 1, ("g1",))


def test_a_one_member_group_says_nothing_and_is_not_counted():
    """`family_cohesion`'s own rule, for its own reason: a group with one placed
    member cannot demonstrate keeping things together either way.

    SABOTAGE: drop the `len(...) > 1` filter. `considered` inflates with
    singletons and the rate stops meaning anything.
    """
    labels = {"a": _Label("g1"), "b": _Label("g2")}
    observations = {"a": _Obs(["run-7"]), "b": _Obs(["run-9"])}

    assert group_cohesion(labels, observations) == (0, 0, ())


def test_files_sharing_one_group_and_differing_on_another_are_together():
    """`00`:63 permits a file to belong to more than one accepted group -- a
    research abstract that is also part of an application packet is the design's
    own example. So the test is INTERSECTION, not equality: two files that share
    one group and differ on a second have still been kept together.

    SABOTAGE: compare the tuples for equality. This goes red, and the scorecard
    starts punishing the product for a membership the design explicitly allows.
    """
    labels = {"a": _Label("g1"), "b": _Label("g1")}
    observations = {"a": _Obs(["run-7", "run-8"]), "b": _Obs(["run-7"])}

    assert group_cohesion(labels, observations) == (1, 1, ())


def test_protected_files_are_not_graded_on_grouping():
    """The standing rule: protected material is counted, never opened, never
    filed automatically -- so it is not evidence about the grouping stage.

    SABOTAGE: drop the `label.protected` guard. The scorecard then grades the
    product on files it is forbidden to group.
    """
    labels = {"a": _Label("g1", protected=True), "b": _Label("g1", protected=True)}
    observations = {"a": _Obs(["run-7"]), "b": _Obs(["run-9"])}

    assert group_cohesion(labels, observations) == (0, 0, ())


def test_a_file_with_no_observation_at_all_still_counts_against_its_group():
    """A file the run never observed is a file the run did not group.

    SABOTAGE: `if observation is None: continue`. A run that dropped half the
    corpus before grouping would then score on the half it kept.
    """
    labels = {"a": _Label("g1"), "b": _Label("g1")}
    observations = {"a": _Obs(["run-7"])}

    assert group_cohesion(labels, observations) == (0, 1, ("g1",))
