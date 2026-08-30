"""An `excluded` membership is not a member, and P11 must not place one.

P9's membership record carries a `decision`, and `excluded` is one of its three
values. It is what P9 writes when the evidence a membership rested on has been
withdrawn -- a person rejecting the claim the folder was built on is the ordinary
cause -- and §8.2 keeps the row rather than deleting it, so a reader can still
see what was concluded and why it stopped being true.

`tree_design.upstream` has always read the field: an `included` row becomes a
`GroupMember` and an `excluded` one becomes `excluded_members`. `placement.groups`
never did. It handed P11 every live row for the group, and `place_group` places
every membership it is handed, so a file P9 had explicitly excluded was still
given a destination in the plan the person reads.

P11's own SPEC decides this. On `evidence_type`: "§3.13's `rejected` is DROPPED:
a rejected fact cannot support a placement, so a record resting on one would be a
contradiction rather than a low-confidence decision -- the correct expression is
`outcome = abstain`." A placement built on a membership P9 has withdrawn is the
same contradiction one record further out.

The twin is the point of the whole fix: `excluded` must reach exactly the file it
was written about. The three other members of this group -- direct-anchor,
context-supported and user-attached -- were never mentioned, and a filter that
took any of them with it would be a correction behaving like a demolition.
"""
from __future__ import annotations

import dataclasses

import pytest

from grouping.store import record_membership
from grouping.vocabulary import EXCLUDED, INCLUDED, RULES

from placement.groups import accepted_group_as_of

from p11.p9_fixtures import GROUP_ID, MEMBERSHIPS, T0, seed_accepted_columbia

WITHDRAWN = "the fact this membership was built on was retracted"


@pytest.fixture()
def seeded(p11_conn):
    seed_accepted_columbia(p11_conn)
    return p11_conn


def _withdraw(conn, file_id: str) -> str:
    """Supersede one member's row with an `excluded` one, as P9 does.

    Through P9's own writer and P9's own supersession columns, so this is the row
    a real run leaves behind rather than a shape invented here.
    """
    original = next(m for m in MEMBERSHIPS if m.file_id == file_id)
    retracted = dataclasses.replace(
        original, membership_id=f"{original.membership_id}:retracted",
        decision=EXCLUDED, decision_source=RULES, created_at=T0,
        supersedes=original.membership_id, superseded_by=None,
        supersede_reason=WITHDRAWN)
    record_membership(conn, retracted)
    return retracted.membership_id


def test_a_withdrawn_member_is_not_handed_to_placement_as_a_member(seeded):
    """The guard. P11 places members; `excluded` says this file is not one."""
    _withdraw(seeded, "f-essay")

    accepted = accepted_group_as_of(seeded, group_id=GROUP_ID,
                                    plan_version="plan-1")

    assert "f-essay" not in {m.file_id for m in accepted.memberships}, (
        "a file P9 excluded from the group was still handed to P11 as a member, "
        "and `place_group` gives every membership it is handed a destination")


def test_the_other_three_members_are_untouched(seeded):
    """The twin, proven on all three bases and not just the one that broke.

    `f-transcript` is context-supported and `f-scan` is user-attached -- a file a
    person themselves put in this group. A filter reaching either of those would
    be P11 overruling a judgement it did not make, on the strength of a
    correction about a different file entirely.
    """
    _withdraw(seeded, "f-essay")

    accepted = accepted_group_as_of(seeded, group_id=GROUP_ID,
                                    plan_version="plan-1")

    assert {m.file_id for m in accepted.memberships} == {
        "f-transcript", "f-scan", "f-duke-essay"}
    assert all(m.decision == INCLUDED for m in accepted.memberships)
    # And the outlier is still there to be excluded by §6.8's own rule, which is
    # a different question with a different answer: P9 flagged it, P11 routes it
    # and explains it. Dropping it here would silently do what §6.8 does visibly.
    outlier = next(m for m in accepted.memberships
                   if m.file_id == "f-duke-essay")
    assert outlier.outlier_flag != "not-flagged", outlier.outlier_flag


def test_nothing_changes_for_a_group_with_no_withdrawal(seeded):
    """The negative twin for the filter itself.

    A guard that has never had to let anything through is not a guard. All four
    memberships are `included`, so the read must return all four -- the same
    answer it gave before this filter existed.
    """
    accepted = accepted_group_as_of(seeded, group_id=GROUP_ID,
                                    plan_version="plan-1")

    assert len(accepted.memberships) == len(MEMBERSHIPS)
    assert {m.file_id for m in accepted.memberships} == {
        m.file_id for m in MEMBERSHIPS}


def test_an_uncertain_member_is_not_swept_up_with_the_excluded_one(seeded):
    """The other twin: the filter is about `excluded` and nothing else.

    `uncertain` is what the P8 seam writes for a context-supported member a model
    was not sure about (`grouping/p8_seam.py`), and it is written in one
    transaction with the `pending-review` acceptance that makes it safe to show.
    §6.11 lists `context-supported group match` among the confidence classes P11
    places and the review interface displays, so an `uncertain` row has a home and
    a review, not neither. A filter written as "keep the included ones" would take
    it, quietly answering the question the review exists to ask.
    """
    from grouping.vocabulary import UNCERTAIN

    unsure = dataclasses.replace(
        next(m for m in MEMBERSHIPS if m.file_id == "f-transcript"),
        membership_id="m-f-transcript:unsure", file_id="f-unsure",
        content_hash="h-f-unsure", decision=UNCERTAIN)
    record_membership(seeded, unsure)
    _withdraw(seeded, "f-essay")

    accepted = accepted_group_as_of(seeded, group_id=GROUP_ID,
                                    plan_version="plan-1")

    assert "f-unsure" in {m.file_id for m in accepted.memberships}, (
        "a member a model was uncertain about was dropped by a filter written "
        "for a member P9 had withdrawn")
    assert "f-essay" not in {m.file_id for m in accepted.memberships}
