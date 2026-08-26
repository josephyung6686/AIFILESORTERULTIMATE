# tests/p9/test_p9_acceptance.py
"""P9 Task 9 — acceptance is per plan version; everything else is shared.

M15. A group, its memberships, its dossier and its edges live in the shared
evidence database and survive every plan version. What a plan version has to say
about them — accepted, rejected, still under review, deferred — lives in one table
and nowhere else. Putting the version on `groups` would duplicate the group, its
dossier, its model response and every line of its evidence per version.

`accepted` and `rejected` are therefore NOT members of `GROUP_STATES`. They are
resolved as of a plan version through an accessor, because a consumer looking for
`rejected` in an enum that does not contain it is a consumer about to invent one.

Absence is not a state. A membership with no acceptance row in a plan version
raises rather than reporting `pending-review`: `pending-review` is something a
writer recorded, and deriving it from `Membership.basis` would manufacture a
review nobody asked for.
"""
from __future__ import annotations

import pytest

from grouping.acceptance import (
    AcceptanceStateAbsent,
    group_state_as_of,
    membership_review_state_as_of,
    record_acceptance,
    record_context_review_pending,
)
from grouping.records import (
    AnchorFact,
    Group,
    GroupAcceptance,
    Membership,
    Support,
)
from grouping.schema import create_grouping_schema
from grouping.vocabulary import (
    ACCEPTED,
    CANDIDATE,
    COMPATIBLE_DOCUMENT_TYPE,
    CONTEXT_SUPPORTED,
    DEFERRED,
    DIRECT_ANCHOR,
    INCLUDED,
    LLM,
    LLM_PROPOSED,
    NOT_REQUIRED,
    PENDING_REVIEW,
    REJECTED,
    RULES,
    SHARED_VALIDATED_FACT,
    STRONGLY_IDENTIFIED_FILE,
    SUPPORTED,
    USER,
    USER_ACCEPTED,
    USER_REJECTED,
)

T0 = "2026-08-27T00:00:00Z"
T1 = "2026-08-27T01:00:00Z"
GROUP = "group-1"
MEMBERSHIP = "membership-context"
KEY = "sha256:" + "b" * 64


@pytest.fixture()
def acceptance_conn(conn):
    create_grouping_schema(conn)
    return conn


def _group(**overrides) -> Group:
    values = dict(
        group_id=GROUP, seed_ref="seed-1", seed_kind=STRONGLY_IDENTIFIED_FILE,
        proposed_basis="subject=PHYS1401",
        anchor_facts=(AnchorFact(
            field="subject", value="PHYS1401", file_ids=("file-1",),
            reliability_state="validated", observation_key=KEY),),
        pre_model_signals={}, anchor_count=1, coherence_verdict=None,
        coherence_citations=(), group_category=None, display_label=None,
        label_source=None, conflicts=(), stop_rule_hits=(), state=SUPPORTED,
        sensitivity_state="none", dossier_id=None, llm_response_ref=None,
        validation_verdict_ref=None, created_by=RULES, created_at=T0,
    )
    values.update(overrides)
    return Group(**values)


def _acceptance(**overrides) -> GroupAcceptance:
    values = dict(
        acceptance_id="acc-1", plan_version_id="plan-2", group_id=GROUP,
        membership_id=None, acceptance=ACCEPTED, review_state=NOT_REQUIRED,
        user_edited_label=None, aliases=(), review_decision_ref=None,
        decided_by=USER, created_at=T0,
    )
    values.update(overrides)
    return GroupAcceptance(**values)


# --- one shared group, many plan opinions ----------------------------------------


def test_accepting_then_rejecting_leaves_one_group_and_two_opinions(acceptance_conn):
    record_acceptance(acceptance_conn, _acceptance(
        acceptance_id="acc-v2", plan_version_id="plan-2", acceptance=ACCEPTED))
    record_acceptance(acceptance_conn, _acceptance(
        acceptance_id="acc-v3", plan_version_id="plan-3", acceptance=REJECTED))

    assert group_state_as_of(
        acceptance_conn, group_id=GROUP, plan_version_id="plan-2") == ACCEPTED
    assert group_state_as_of(
        acceptance_conn, group_id=GROUP, plan_version_id="plan-3") == REJECTED
    assert acceptance_conn.execute(
        "SELECT count(*) AS c FROM group_acceptance").fetchone()["c"] == 2


def test_the_stored_group_state_never_becomes_accepted_or_rejected(acceptance_conn):
    """`GROUP_STATES` has four members and neither of these is one of them."""
    from grouping.vocabulary import GROUP_STATES

    assert ACCEPTED not in GROUP_STATES
    assert REJECTED not in GROUP_STATES
    with pytest.raises(Exception):
        _group(state=ACCEPTED)


def test_a_group_with_no_plan_opinion_reports_its_shared_lifecycle(acceptance_conn):
    """The fallback is the SHARED state, never `pending-review` or `deferred`.
    A plan version that has not spoken about a group has not put it under review."""
    from grouping.store import record_group

    record_group(acceptance_conn, _group(state=CANDIDATE))
    assert group_state_as_of(
        acceptance_conn, group_id=GROUP, plan_version_id="plan-9") == CANDIDATE


def test_a_deferred_plan_opinion_does_not_become_a_shared_lifecycle_state(
    acceptance_conn,
):
    from grouping.store import record_group

    record_group(acceptance_conn, _group(state=SUPPORTED))
    record_acceptance(acceptance_conn, _acceptance(
        plan_version_id="plan-2", acceptance=DEFERRED, review_state=DEFERRED))
    assert group_state_as_of(
        acceptance_conn, group_id=GROUP, plan_version_id="plan-2") == SUPPORTED


# --- a membership's review state is stored, never derived ------------------------


def test_absence_raises_rather_than_reporting_pending_review(acceptance_conn):
    with pytest.raises(AcceptanceStateAbsent):
        membership_review_state_as_of(
            acceptance_conn, membership_id=MEMBERSHIP, plan_version_id="plan-4")


def test_a_recorded_membership_review_state_is_returned(acceptance_conn):
    record_acceptance(acceptance_conn, _acceptance(
        acceptance_id="acc-m", plan_version_id="plan-2", membership_id=MEMBERSHIP,
        acceptance=PENDING_REVIEW, review_state=PENDING_REVIEW))
    assert membership_review_state_as_of(
        acceptance_conn, membership_id=MEMBERSHIP,
        plan_version_id="plan-2") == PENDING_REVIEW


def test_the_membership_accessor_has_no_basis_derived_fallback(acceptance_conn):
    """A `context-supported` membership does not imply a pending review. Deriving
    one from the basis would manufacture a review nobody recorded, in a plan
    version that never asked for it."""
    from grouping.store import record_membership

    record_membership(acceptance_conn, Membership(
        membership_id=MEMBERSHIP, group_id=GROUP, file_id="file-2",
        content_hash="h-2", basis=CONTEXT_SUPPORTED,
        support=(Support(support_kind=COMPATIBLE_DOCUMENT_TYPE,
                         observation_key=KEY, quote_or_field=None,
                         location=None, edge_ref=None),),
        decision=INCLUDED, decision_source=LLM, insufficient_evidence=False,
        insufficiency_statement=None, conflicts=(), outlier_flag="none",
        validation_verdict_ref=None, created_at=T0))
    with pytest.raises(AcceptanceStateAbsent):
        membership_review_state_as_of(
            acceptance_conn, membership_id=MEMBERSHIP, plan_version_id="plan-2")


def test_the_pending_review_writer_materialises_the_row_it_reads(acceptance_conn):
    """Task 10 calls this inside the membership-write transaction. The accessor
    reads a row a writer put there; there is no path where it invents one."""
    with pytest.raises(AcceptanceStateAbsent):
        membership_review_state_as_of(
            acceptance_conn, membership_id=MEMBERSHIP, plan_version_id="plan-2")
    record_context_review_pending(
        acceptance_conn, plan_version_id="plan-2", group_id=GROUP,
        membership_id=MEMBERSHIP, created_at=T0)
    assert membership_review_state_as_of(
        acceptance_conn, membership_id=MEMBERSHIP,
        plan_version_id="plan-2") == PENDING_REVIEW
    assert membership_review_state_as_of(
        acceptance_conn, membership_id=MEMBERSHIP,
        plan_version_id="plan-2") == PENDING_REVIEW


def test_a_pending_review_row_is_written_per_plan_version(acceptance_conn):
    record_context_review_pending(
        acceptance_conn, plan_version_id="plan-2", group_id=GROUP,
        membership_id=MEMBERSHIP, created_at=T0)
    with pytest.raises(AcceptanceStateAbsent):
        membership_review_state_as_of(
            acceptance_conn, membership_id=MEMBERSHIP, plan_version_id="plan-3")


# --- revision appends and supersedes ---------------------------------------------


def test_a_revision_supersedes_and_keeps_both_rows(acceptance_conn):
    first = record_acceptance(acceptance_conn, _acceptance(
        acceptance_id="acc-1", plan_version_id="plan-2",
        acceptance=PENDING_REVIEW, review_state=PENDING_REVIEW))
    second = record_acceptance(acceptance_conn, _acceptance(
        acceptance_id="acc-2", plan_version_id="plan-2", acceptance=ACCEPTED,
        review_state=USER_ACCEPTED, created_at=T1,
        supersedes=first, supersede_reason="the user accepted it"))
    assert group_state_as_of(
        acceptance_conn, group_id=GROUP, plan_version_id="plan-2") == ACCEPTED
    rows = list(acceptance_conn.execute(
        "SELECT acceptance_id, superseded_by FROM group_acceptance ORDER BY rowid"))
    assert [row["acceptance_id"] for row in rows] == [first, second]
    assert rows[0]["superseded_by"] == second
    assert rows[1]["superseded_by"] is None


def test_a_second_current_row_for_one_key_is_refused(acceptance_conn):
    """The unique index is over unsuperseded rows. Two current opinions in one plan
    version about one group is two answers to one question."""
    import sqlite3

    record_acceptance(acceptance_conn, _acceptance(acceptance_id="acc-1"))
    with pytest.raises(sqlite3.IntegrityError):
        record_acceptance(acceptance_conn, _acceptance(acceptance_id="acc-2"))


def test_a_revision_naming_no_predecessor_is_refused(acceptance_conn):
    record_acceptance(acceptance_conn, _acceptance(acceptance_id="acc-1"))
    with pytest.raises(AcceptanceStateAbsent):
        record_acceptance(acceptance_conn, _acceptance(
            acceptance_id="acc-2", supersedes="acc-nonexistent",
            supersede_reason="the user changed their mind"))


def test_a_supersession_with_no_reason_is_refused(acceptance_conn):
    """A later reader has only the reason to explain the change with."""
    first = record_acceptance(acceptance_conn, _acceptance(acceptance_id="acc-1"))
    with pytest.raises(ValueError):
        record_acceptance(acceptance_conn, _acceptance(
            acceptance_id="acc-2", supersedes=first, supersede_reason=None))


# --- the user's label lives here, and only here ----------------------------------


def test_the_user_edited_label_never_overwrites_the_proposed_one(acceptance_conn):
    """`Group.display_label` keeps what the engine or the model proposed. What the
    user typed is a plan-version fact, and overwriting the proposal would erase the
    thing a later evaluation compares the edit against."""
    from grouping.store import record_group

    record_group(acceptance_conn, _group(
        coherence_verdict="coherent", display_label="PHYS1401 materials",
        label_source=LLM_PROPOSED, group_category="course"))
    record_acceptance(acceptance_conn, _acceptance(
        plan_version_id="plan-2", acceptance=ACCEPTED, review_state=USER_ACCEPTED,
        user_edited_label="Physics I"))
    stored = acceptance_conn.execute(
        "SELECT display_label FROM groups WHERE group_id = ?", (GROUP,),
    ).fetchone()["display_label"]
    assert stored == "PHYS1401 materials"
    assert acceptance_conn.execute(
        "SELECT user_edited_label FROM group_acceptance WHERE plan_version_id = ?",
        ("plan-2",),
    ).fetchone()["user_edited_label"] == "Physics I"


def test_plan_version_id_is_on_exactly_one_p9_table(acceptance_conn):
    from grouping.schema import P9_TABLES

    carrying = [
        table for table in P9_TABLES
        if "plan_version_id" in {
            row["name"] for row in acceptance_conn.execute(
                f"PRAGMA table_info({table})")
        }
    ]
    assert carrying == ["group_acceptance"]
