"""P10 Task 15 — the §6.1 destination profile is P10's alone (resolution B4).

Every §6.1 ingredient — template, expected field values, accepted group
memberships, user-selected label, known exclusions, privacy restrictions — is a
value P10 already holds at freeze. None is produced by placement. P11 receives
the profile, builds the §6.2 retrieval index over it, and carries no profile of
its own.

Excerpts are cited by `observation_key`, P4's durable citation handle, not by
`observation_id`: an id that changes between runs cannot bind a citation to what
was actually released.
"""
from __future__ import annotations

import pytest

from tree_design.profiles import (
    AnchorExcerpt,
    NodeContext,
    Restrictions,
    build_profiles,
    redacted_for_egress,
)
from tree_design.records import ExpectedValue, Node, PlanVersion, TemplateContext
from tree_design.schema import create_tree_schema
from tree_design.store import write_node, write_plan_version
from tree_design.upstream import AcceptedGroup, GroupMember

T0 = "2026-08-27T00:00:00Z"

GROUP = AcceptedGroup(
    group_id="g_phys", label="PHYS 1401 course", domain="academic",
    members=(GroupMember("lecture", "h_lecture", "direct-anchor"),
             GroupMember("hw", "h_hw", "context-supported")),
    anchor_facts=("fact_g_phys",), excluded_members=("duke-essay",),
)


def _node(node_id, label, *, parent=None, role="ordinary", node_type="proposed",
          handling="personal_non_sensitive", groups=("g_phys",), dimension=None,
          dimension_role=None, expected=(), context=None, disposition=None,
          accepts=None, protected_ok=False):
    from tree_design.records import derive_accepts_placement

    return Node(
        node_id=node_id, plan_version_id="plan_1", node_type=node_type,
        display_label=label, parent_node_id=parent, root_anchor="root_documents",
        ordinal=0, associated_group_ids=groups,
        explanation=f"{label} appeared from the accepted groups beneath it.",
        node_role=role,
        accepts_placement=(derive_accepts_placement(
            node_type, protected_movement_permitted=protected_ok)
            if accepts is None else accepts),
        handling_class=handling, origin_node_id=node_id,
        dimension=dimension, dimension_role=dimension_role,
        expected_values=expected, template_context=context,
        disposition=disposition, protected_movement_permitted=protected_ok,
        refinement_disposition="refined",
        refinement_reason="The course groups justify the split.",
    )


@pytest.fixture()
def seeded(conn):
    create_tree_schema(conn)
    write_plan_version(conn, PlanVersion(
        plan_version_id="plan_1", predecessor_id=None, state="draft",
        created_at=T0, cross_folder_moves=False, selection_id="sel_1"))
    write_node(conn, _node("n_root", "Academics", groups=()))
    write_node(conn, _node(
        "n_course", "PHYS1401", parent="n_root", dimension="subject",
        dimension_role="course",
        expected=(ExpectedValue(field="subject", value="PHYS1401"),),
        context=TemplateContext(
            binding_id="tb_academic", template_id="academic-coursework",
            template_version=1, dimension_index=2)))
    return conn


def _profiles(conn, **over):
    kwargs = dict(
        plan_version_id="plan_1", groups_by_id={"g_phys": GROUP},
        document_types_by_node={"n_course": ("syllabus", "homework")},
        anchor_excerpts_by_node={
            "n_course": (AnchorExcerpt(observation_key="obs:lecture:1",
                                       node_id="n_course"),)},
        user_edits_by_node={"n_course": ("renamed from PHYS 1401",)},
        node_scoped_rejections={"n_course": ("duke-essay",)},
    )
    kwargs.update(over)
    return {p.node_id: p for p in build_profiles(conn, **kwargs)}


def test_every_node_in_the_version_gets_exactly_one_profile(seeded):
    profiles = _profiles(seeded)
    assert set(profiles) == {"n_root", "n_course"}


def test_the_profile_carries_6_1s_ingredients_from_values_p10_already_holds(seeded):
    profile = _profiles(seeded)["n_course"]
    assert profile.display_label == "PHYS1401"
    assert profile.domains == ("academic",)
    assert profile.template_binding == "tb_academic"
    assert profile.template_fields == ("subject",)
    assert profile.expected_values == (
        ExpectedValue(field="subject", value="PHYS1401"),)
    assert profile.accepted_group_ids == ("g_phys",)
    assert profile.group_labels == ("PHYS 1401 course",)
    assert profile.known_document_types == ("syllabus", "homework")
    assert profile.user_edits == ("renamed from PHYS 1401",)


def test_parent_and_child_meanings_travel_with_the_node(seeded):
    """§6.1 asks for "parent and child meanings" — a node's own label is not
    enough to place into, because `2026` under `Columbia` and `2026` under
    `Receipts` are different destinations."""
    profiles = _profiles(seeded)
    assert profiles["n_course"].parent_context == (
        NodeContext(node_id="n_root", display_label="Academics",
                    dimension=None, expected_values=()),)
    assert profiles["n_root"].child_context == (
        NodeContext(node_id="n_course", display_label="PHYS1401",
                    dimension="subject",
                    expected_values=(ExpectedValue("subject", "PHYS1401"),)),)


def test_known_exclusions_carry_the_groups_own_negative_evidence(seeded):
    """§6.1's "known exclusions". A file the user removed from the group is the
    strongest evidence the node does NOT want it, and §8.7 requires the negative
    to be stored with the evidence that produced it."""
    profile = _profiles(seeded)["n_course"]
    assert "duke-essay" in profile.known_exclusions


def test_an_excerpt_is_cited_by_p4s_durable_handle_never_by_a_run_local_id(seeded):
    profile = _profiles(seeded)["n_course"]
    assert profile.anchor_excerpts[0].observation_key == "obs:lecture:1"
    assert not hasattr(profile.anchor_excerpts[0], "observation_id")


def test_the_restrictions_carry_the_flag_p11_reads_and_nothing_derived(seeded):
    profile = _profiles(seeded)["n_course"]
    assert profile.restrictions == Restrictions(
        handling_class="personal_non_sensitive", accepts_placement=True,
        node_role="ordinary", disposition=None)


def test_no_profile_field_holds_a_composed_path(seeded):
    """DM11. P10 publishes `root_anchor` plus the label chain; P12 composes."""
    for profile in _profiles(seeded).values():
        for value in (profile.display_label, *profile.group_labels,
                      *profile.representative_files):
            assert "/" not in value and "\\" not in value


# --- the boundary: what may leave for a model prompt ----------------------------


def test_a_protected_profile_is_redacted_and_an_ordinary_one_beside_it_is_not(
        seeded):
    """The product owner's standing rule reaches the egress boundary here:
    protected material "must not cause filenames or content to be exposed in
    model prompts" (§7.3, Protected Records).

    The second half of this test is the one that makes it a test. Redacting
    EVERY profile would satisfy "the protected one is redacted" and would also
    destroy the product: P11 could place nothing. The discriminating case is that
    the ordinary node beside it keeps its filenames and its excerpts.
    """
    write_node(seeded, _node(
        "n_private", "Passport", parent="n_root",
        handling="highly_sensitive_credential_bearing", groups=()))
    profiles = _profiles(
        seeded,
        document_types_by_node={"n_course": ("syllabus",), "n_private": ("scan",)},
        anchor_excerpts_by_node={
            "n_course": (AnchorExcerpt("obs:lecture:1", "n_course"),),
            "n_private": (AnchorExcerpt("obs:passport:1", "n_private"),)},
        user_edits_by_node={}, node_scoped_rejections={})

    protected = redacted_for_egress(
        profiles["n_private"],
        protected_handling_classes=frozenset({
            "highly_sensitive_credential_bearing"}))
    assert protected.representative_files == ()
    assert protected.anchor_files == ()
    assert protected.anchor_excerpts == ()
    # MARKED AND COUNTED, NEVER OPENED: it is still a profile, still identified,
    # still placeable-or-not by its own restrictions. Not omitted.
    assert protected.node_id == "n_private"
    assert protected.display_label == "Passport"
    assert protected.restrictions.handling_class == (
        "highly_sensitive_credential_bearing")

    ordinary = redacted_for_egress(
        profiles["n_course"],
        protected_handling_classes=frozenset({
            "highly_sensitive_credential_bearing"}))
    assert ordinary.anchor_excerpts == profiles["n_course"].anchor_excerpts
    assert ordinary.representative_files == profiles["n_course"].representative_files
    assert ordinary.representative_files != ()


def test_redaction_needs_the_protected_classes_and_invents_none(seeded):
    """P7 owns `HANDLING_CLASSES` and publishes no ordering, so P10 cannot decide
    which classes are protected. Absent means refuse, never guess."""
    from tree_design.config import ConfigurationRequired

    with pytest.raises(ConfigurationRequired):
        redacted_for_egress(_profiles(seeded)["n_course"],
                            protected_handling_classes=None)
