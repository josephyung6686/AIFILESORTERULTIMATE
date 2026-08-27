"""Seeds REAL P9 rows for P11's group tests. TESTS ONLY.

This is NOT a stand-in for a P9 read. P9's acceptance read shipped:
`grouping.acceptance.group_state_as_of(conn, *, group_id, plan_version_id)`
(`acceptance.py:154`) returns `accepted` or `rejected` as of a plan version, and
`grouping.store.memberships_for_group(conn, group_id)` (`store.py:266`) returns
the members. `placement/groups.py` calls both directly.

What this module does is build P9's own records -- `Group`, `Membership`,
`GroupAcceptance`, imported and never restated -- and write them through P9's own
writers (`record_group`, `record_membership`, `record_acceptance`), so a P11 test
runs against rows a real P9 run would have produced. A shape change in P9 breaks
this at import, which is the point.

`src/placement/` may never import this module and a test asserts it does not: the
prohibition is about a SOURCE module importing test code, and it stands whether or
not the part it seeds exists.
"""
from __future__ import annotations

from facts.states import VALIDATED
from grouping.acceptance import record_acceptance
from grouping.records import (
    AnchorFact, Conflict, Group, GroupAcceptance, Membership, Support,
)
from grouping.store import record_group, record_membership
from grouping.vocabulary import (
    ACCEPTED, CONTEXT_SUPPORTED, COHERENT, DIRECT_ANCHOR, ENGINE, ENGINE_FLAGGED,
    INCLUDED, NOT_FLAGGED, NO_SENSITIVITY, PENDING_REVIEW, RULES,
    SHARED_VALIDATED_FACT, STRONGLY_IDENTIFIED_FILE, SUPPORTED, USER,
    USER_ATTACHED,
)

T0 = "2026-08-27T00:00:00Z"

# `VALIDATED` is P6's reliability state and is imported from `facts.states`.
# `grouping.vocabulary` does NOT publish it -- it has `VALIDATED_SHARED_FACT`
# (a seed kind) and `VALIDATION` (a failure stage), and importing either as
# `AnchorFact.reliability_state` would put a seed kind in a reliability field.
#
# `NO_SENSITIVITY` is P9's own `sensitivity_state`, and it is NOT a P7 handling
# class. `Group.__post_init__` only requires the field to be non-empty
# (`grouping/records.py:178`), so a P7 class such as `personal_non_sensitive`
# would be stored unchallenged and read back as a P9 sensitivity state that P9
# never defines -- a value meaning something its own vocabulary does not say.


def _membership(file_id, *, basis=DIRECT_ANCHOR, outlier=NOT_FLAGGED,
                conflicts=()) -> Membership:
    return Membership(
        membership_id=f"m-{file_id}", group_id="g-columbia", file_id=file_id,
        content_hash=f"h-{file_id}", basis=basis, decision=INCLUDED,
        decision_source=RULES,
        support=(Support(support_kind=SHARED_VALIDATED_FACT,
                         observation_key=f"obs-{file_id}",
                         quote_or_field="target_school", location="body",
                         edge_ref=None),),
        insufficient_evidence=False, insufficiency_statement=None,
        conflicts=conflicts, outlier_flag=outlier,
        validation_verdict_ref=None, created_at=T0)


COLUMBIA_GROUP = Group(
    group_id="g-columbia", seed_ref="seed-1", seed_kind=STRONGLY_IDENTIFIED_FILE,
    proposed_basis="target_school = Columbia",
    anchor_facts=(AnchorFact(field="target_school", value="Columbia",
                             file_ids=("f-essay", "f-transcript"),
                             reliability_state=VALIDATED,
                             observation_key="obs-f-essay"),),
    pre_model_signals={}, anchor_count=2, coherence_verdict=COHERENT,
    coherence_citations=("obs-f-essay",), group_category="application",
    display_label="Columbia application", label_source=ENGINE, conflicts=(),
    stop_rule_hits=(), state=SUPPORTED, sensitivity_state=NO_SENSITIVITY,
    dossier_id=None, llm_response_ref=None, validation_verdict_ref=None,
    created_by=RULES, created_at=T0)

MEMBERSHIPS = (
    _membership("f-essay"),
    _membership("f-transcript", basis=CONTEXT_SUPPORTED),
    _membership("f-scan", basis=USER_ATTACHED),
    _membership("f-duke-essay", outlier=ENGINE_FLAGGED,
                conflicts=(Conflict(kind="target_school",
                                    competing_values=("Columbia", "Duke"),
                                    file_ids=("f-duke-essay",)),)),
)

ACCEPTANCE = GroupAcceptance(
    acceptance_id="acc-1", plan_version_id="plan-1", group_id="g-columbia",
    membership_id=None, acceptance=ACCEPTED, review_state=PENDING_REVIEW,
    user_edited_label=None, aliases=(), review_decision_ref=None,
    decided_by=USER, created_at=T0)

GROUP_ID: str = COLUMBIA_GROUP.group_id


def seed_accepted_columbia(conn) -> str:
    """Write the group, its four memberships and its acceptance THROUGH P9.

    Nothing here is a stand-in read. After this call,
    `grouping.acceptance.group_state_as_of(conn, group_id=GROUP_ID,
    plan_version_id="plan-1")` returns `accepted` and
    `grouping.store.memberships_for_group(conn, GROUP_ID)` returns the four
    members -- which is precisely what `placement.groups` consumes.
    """
    record_group(conn, COLUMBIA_GROUP)
    for membership in MEMBERSHIPS:
        record_membership(conn, membership)
    record_acceptance(conn, ACCEPTANCE)
    return GROUP_ID
