"""§7.10 + §8.2: a bulk acceptance is not one opaque decision over an unnamed population.

`74` §6 B6's named test is
`test_a_bulk_acceptance_expands_to_the_individual_actions_it_stood_for`; its
negative twin lives in `test_p13_rejections.py`. Done-means 8 is the contract:
one `review_action` enumerating every member, with `bulk_basis` naming the
evidence pattern the user was shown, and each member separately inspectable and
separately correctable.
"""
from __future__ import annotations

import pytest

from privacy.display import RedactionSettings

from review_surface.bulk import (
    BulkBasisRequired,
    collect_bulk,
    expand,
    member_is_separately_correctable,
)
from review_surface.collect import BulkMembersRequired, collect
from review_surface.presentation import record_presentation
from review_surface.store import actions_for, record_action
from review_surface.vocabulary import (
    ACTION_ACCEPT_BULK,
    ACTION_CHANGE_DESTINATION,
    SURFACE_RESIDUAL_SET,
)

T0 = "2026-08-29T00:00:00Z"
SHOWN = RedactionSettings(names="shown", previews="shown", thumbnails="shown",
                          ocr_text="shown", location_data="shown")
BASIS = "all three are product screenshots with no accepted project or event"


@pytest.fixture()
def ref(p13_conn):
    return record_presentation(
        p13_conn, surface=SURFACE_RESIDUAL_SET, subject_ref="set-1",
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=("obs-1",), user_id="jy", component_version="p13-1",
        rendered_at=T0).presented_state_ref


def _bulk(conn, ref, **overrides):
    values = dict(
        action_id="a-bulk", surface=SURFACE_RESIDUAL_SET, subject_ref="set-1",
        plan_version="plan-1", session_id="s-1", correction_scope="group",
        presented_state_ref=ref, user_id="jy", acted_at=T0,
        component_version="p13-1", members=("f-a", "f-b", "f-c"),
        bulk_basis=BASIS)
    values.update(overrides)
    return collect_bulk(conn, **values)


def test_a_bulk_acceptance_expands_to_the_individual_actions_it_stood_for(
        p13_conn, ref):
    """`74` §6 B6's named test. Done-means 8, all three clauses.

    One action goes in; every member comes back out, each carrying the basis and
    the presentation the user acted against -- and each findable from the
    MEMBER'S side, which is the property that makes a later per-file correction
    possible at all. A member nothing can query is not separately correctable
    however the docstring puts it.
    """
    action = _bulk(p13_conn, ref)
    assert action.action == ACTION_ACCEPT_BULK
    assert action.bulk_member_refs == ("f-a", "f-b", "f-c")
    assert action.bulk_basis == BASIS
    record_action(p13_conn, action)
    views = expand(p13_conn, action)
    assert [v.member_ref for v in views] == ["f-a", "f-b", "f-c"]
    for view in views:
        assert view.bulk_action_id == "a-bulk"
        assert view.bulk_basis == BASIS
        assert view.presented_state_ref == ref
    for member in ("f-a", "f-b", "f-c"):
        assert member_is_separately_correctable(p13_conn, member_ref=member)
    assert not member_is_separately_correctable(p13_conn, member_ref="f-z")


def test_the_basis_names_the_evidence_pattern_the_user_was_shown(p13_conn, ref):
    """Without it the batch is unexplained and §8.7 has nothing to store."""
    with pytest.raises(BulkBasisRequired):
        _bulk(p13_conn, ref, bulk_basis="")


def test_a_bulk_with_no_members_is_refused(p13_conn, ref):
    """A filter expression cannot be re-read later to say which files a
    reversal applies to."""
    with pytest.raises(BulkMembersRequired):
        _bulk(p13_conn, ref, members=())


def test_a_member_can_carry_its_own_later_action_without_touching_the_bulk_one(
        p13_conn, ref):
    """§8.7: correcting one member is a `file` correction, not a re-decision of
    the batch. The two actions stay two rows on two subjects."""
    bulk = _bulk(p13_conn, ref)
    record_action(p13_conn, bulk)
    single = record_presentation(
        p13_conn, surface=SURFACE_RESIDUAL_SET, subject_ref="f-b",
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=("obs-2",), user_id="jy", component_version="p13-1",
        rendered_at="2026-08-29T00:05:00Z").presented_state_ref
    record_action(p13_conn, collect(
        p13_conn, action_id="a-fix", surface=SURFACE_RESIDUAL_SET,
        subject_ref="f-b", plan_version="plan-1", session_id="s-1",
        action=ACTION_CHANGE_DESTINATION, correction_scope="file",
        presented_state_ref=single, user_id="jy",
        acted_at="2026-08-29T00:05:00Z", component_version="p13-1",
        payload={"node_id": "n-clips"}))
    assert len(actions_for(p13_conn, subject_ref="set-1")) == 1
    assert len(actions_for(p13_conn, subject_ref="f-b")) == 1
    # And the bulk action still names f-b, so the batch stays inspectable too.
    assert "f-b" in actions_for(
        p13_conn, subject_ref="set-1")[0].bulk_member_refs
