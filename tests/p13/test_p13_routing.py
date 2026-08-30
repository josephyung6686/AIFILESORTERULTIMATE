"""Routing is the whole contract. One gesture, possibly two parts.

P13 hands the action to the owning part and THAT part decides what it means. An
action may route to more than one part; it is still ONE collected gesture, which
is precisely why P13's `review action routed` event exists: §7.10's "create a
custom folder" during residual review is both a residual decision (P11) and a
tree edit (P10), and without P13's event the two records lose the fact that they
were one user action.
"""
from __future__ import annotations

import pytest

from review_surface.routing import ACTION_ROUTING, PARTS, ROUTING, Unroutable, route
from review_surface.vocabulary import (
    ACTION_ACCEPT,
    ACTION_ADOPT_VERSION,
    ACTION_APPROVE_FOR_APPLY,
    ACTION_CREATE_CUSTOM_FOLDER,
    ACTION_MARK_PRIVATE,
    ACTION_REFRESH_PLAN,
    ACTION_RESET_LEARNING,
    ACTION_SELECT_CONSENT_OPTION,
    ACTION_SET_REDACTION,
    ACTIONS,
    SURFACE_APPLY,
    SURFACE_CONSENT,
    SURFACE_GROUP_PLAN,
    SURFACE_LEARNING,
    SURFACE_PLACEMENT,
    SURFACE_PLAN_VERSION,
    SURFACE_RESIDUAL_SET,
    SURFACES,
)


def test_every_surface_routes_somewhere():
    """A surface with no owning part would collect gestures that silently mean
    nothing."""
    for surface in SURFACES:
        assert ROUTING[surface], f"{surface} routes to no part"
        assert set(ROUTING[surface]) <= set(PARTS)


def test_placement_and_residual_surfaces_route_to_p11():
    for surface in (SURFACE_PLACEMENT, SURFACE_GROUP_PLAN, SURFACE_RESIDUAL_SET):
        assert "P11" in route(surface, ACTION_ACCEPT)


def test_a_group_change_on_a_group_plan_also_reaches_p9():
    assert "P9" in ROUTING[SURFACE_GROUP_PLAN]


def test_a_custom_folder_created_during_residual_review_reaches_both_p11_and_p10():
    """One gesture, two records, and P13's event is what keeps them one user
    action. A tree edit produces a new plan version (§8.8); it is never the model
    inventing a destination (§7.4)."""
    parts = route(SURFACE_RESIDUAL_SET, ACTION_CREATE_CUSTOM_FOLDER)
    assert "P11" in parts and "P10" in parts


def test_a_reclassification_to_private_reaches_both_p7_and_p6():
    parts = route(SURFACE_PLACEMENT, ACTION_MARK_PRIVATE)
    assert "P7" in parts and "P6" in parts


def test_consent_and_redaction_route_to_p7():
    assert route(SURFACE_CONSENT, ACTION_SELECT_CONSENT_OPTION) == ("P7",)
    assert "P7" in route(SURFACE_CONSENT, ACTION_SET_REDACTION)


def test_refresh_and_apply_approval_route_to_p12():
    assert "P12" in route(SURFACE_APPLY, ACTION_REFRESH_PLAN)
    assert "P12" in route(SURFACE_APPLY, ACTION_APPROVE_FOR_APPLY)


def test_a_version_action_routes_to_p10():
    assert "P10" in route(SURFACE_PLAN_VERSION, ACTION_ADOPT_VERSION)


def test_a_reset_routes_to_p1():
    assert route(SURFACE_LEARNING, ACTION_RESET_LEARNING) == ("P1",)


def test_the_parts_named_are_the_seven_the_spec_s_table_names():
    assert PARTS == ("P1", "P6", "P7", "P9", "P10", "P11", "P12")


def test_an_unknown_surface_or_action_is_unroutable_and_not_silently_dropped():
    with pytest.raises(Unroutable):
        route("dashboard", ACTION_ACCEPT)
    with pytest.raises(Unroutable):
        route(SURFACE_PLACEMENT, "delete_everything")


def test_routing_is_deterministic_and_ordered():
    """A set is not an answer: two runs must hand the same gesture to the same
    parts in the same order, or a replay cannot reproduce the routing."""
    assert route(SURFACE_PLACEMENT, ACTION_MARK_PRIVATE) == route(
        SURFACE_PLACEMENT, ACTION_MARK_PRIVATE)
    for surface in SURFACES:
        for action in ACTIONS:
            try:
                parts = route(surface, action)
            except Unroutable:
                continue
            assert list(parts) == sorted(parts, key=PARTS.index)
            assert len(set(parts)) == len(parts)


def test_the_action_table_names_only_actions_p13_publishes():
    assert set(ACTION_ROUTING) <= set(ACTIONS)


def test_p2_is_not_a_routing_target():
    """P13 emits no `stage_output` and is not one of §8.5's ten attribution
    stages; inventing an eleventh would corrupt P2's closed enumeration. SPEC
    Open question 9 -- whether an evaluation adjudication is an §8.7 correction
    -- is OPEN, and P2 is not in the SPEC's routing table either way."""
    assert "P2" not in PARTS
    for surface in SURFACES:
        assert "P2" not in ROUTING[surface]
