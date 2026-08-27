"""P10 Task 10 — nine fixed names, eight slots, and the nodes that never exist.

§7.2 names the failure this library prevents: the LLM creating arbitrary folders
such as `Random PDF Things`, `Important Screenshot`, `Miscellaneous Documents`,
or `Travel/Gate B12`, which "may sound plausible but would fragment the user's
filesystem and create unmaintainable structure". A residual template is a
CONSTRAINT on the model's choices, not a suggestion.

The enforcement mechanism is a single sentence long: a template the user did not
enable has no node, so no placement decision can name it and no model can return
it. Everything else here is bookkeeping around that.
"""
from __future__ import annotations

import pytest

from tree_design.config import ConfigurationRequired
from tree_design.records import Node
from tree_design.residuals import (
    ResidualChoice,
    ResidualTemplate,
    build_library,
    project_residual_nodes,
)
from tree_design.vocabulary import (
    DISABLE,
    ENABLE,
    LEAVE_IN_PLACE,
    MERGE_RESIDUAL,
    PHYSICAL_DESTINATION,
    RELOCATE,
    RENAME_RESIDUAL,
    REPLACE_WITH_EXISTING,
    RESIDUAL,
    RESIDUAL_DEFAULT_PARENTS,
    RESIDUAL_SLOTS,
    RESIDUAL_TEMPLATE_NAMES,
    REVIEW_ONLY,
    TREATMENT_RETAINED,
    TREATMENT_REVIEWED,
)

SLOTS = {
    name: {
        "display_name": name,
        "default_parent_location": RESIDUAL_DEFAULT_PARENTS.get(name),
        "accepted_evidence_patterns": ("pattern.fixture",),
        "expected_file_types": ("image/png",),
        "sensitivity_restrictions": (),
        "optional_shallow_subfolders": (),
        "max_permitted_depth": 1,
        "treatment": TREATMENT_REVIEWED,
    }
    for name in RESIDUAL_TEMPLATE_NAMES
}


def _ids():
    counter = iter(range(len(RESIDUAL_TEMPLATE_NAMES) * 2))
    return lambda: f"n_res_{next(counter)}"


def _classes(name):
    return "sensitive_personal" if name == "Protected Records" else "personal_non_sensitive"


def test_the_library_holds_exactly_the_nine_and_every_one_defines_eight_slots():
    library = build_library(SLOTS)
    assert tuple(library) == RESIDUAL_TEMPLATE_NAMES
    for template in library.values():
        for slot in RESIDUAL_SLOTS:
            assert hasattr(template, slot), slot


def test_only_the_first_four_have_a_stated_default_parent():
    """§7.3 states a default parent location for four templates. The remaining
    five have none stated, and inventing one would be P10 authoring §7.3."""
    library = build_library(SLOTS)
    stated = {n for n, t in library.items() if t.default_parent_location is not None}
    assert stated == {
        "Temporary Screenshots", "One-Off Images", "Reference Clips",
        "Independent Records",
    }
    assert library["Review Later"].default_parent_location is None


def test_a_default_parent_is_a_label_chain_and_never_a_path():
    library = build_library(SLOTS)
    assert library["Temporary Screenshots"].default_parent_location == (
        "Photos", "Temporary Screenshots")
    for template in library.values():
        for label in template.default_parent_location or ():
            assert "/" not in label and "\\" not in label


def test_a_missing_slot_value_refuses_rather_than_defaulting():
    for slot in RESIDUAL_SLOTS:
        if slot == "default_parent_location":
            continue  # None is a real value for five of the nine
        broken = {name: dict(values) for name, values in SLOTS.items()}
        del broken["Review Later"][slot]
        with pytest.raises(ConfigurationRequired) as excinfo:
            build_library(broken)
        assert slot in str(excinfo.value)


def test_the_product_ships_no_user_defined_residual_area():
    """§7.3 requires the library to SUPPORT user-defined areas such as Things to
    Read, Ideas, Shopping Research, Memes, Travel, Receipts to Process, Clips or
    Stuff to Sort, "because residual organization is highly personal and should
    not be dictated by a universal taxonomy". Those are illustrations of user
    freedom; the product ships none of them."""
    library = build_library(SLOTS)
    assert not any(t.user_defined for t in library.values())
    for illustration in ("Things to Read", "Ideas", "Shopping Research", "Memes",
                         "Travel", "Receipts to Process", "Clips", "Stuff to Sort"):
        assert illustration not in library


def test_a_user_defined_area_joins_the_library_with_the_same_eight_slots():
    mine = ResidualTemplate(
        template_name="Shopping Research", display_name="Shopping Research",
        default_parent_location=None, accepted_evidence_patterns=("pattern.user",),
        expected_file_types=("text/html",), sensitivity_restrictions=(),
        optional_shallow_subfolders=(), max_permitted_depth=1,
        treatment=TREATMENT_RETAINED, user_defined=True,
    )
    library = build_library(SLOTS, user_defined=(mine,))
    assert library["Shopping Research"].user_defined
    assert len(library) == len(RESIDUAL_TEMPLATE_NAMES) + 1


def test_a_disabled_template_creates_no_node(conn):
    library = build_library(SLOTS)
    choices = tuple(
        ResidualChoice(template_name=name, action=DISABLE, disposition=None,
                       display_label=None, parent_node_id=None, root_anchor=None,
                       merge_into=None, replaces_node_id=None)
        for name in RESIDUAL_TEMPLATE_NAMES
    )
    nodes = project_residual_nodes(
        library, choices, plan_version_id="plan_1",
        handling_class_for_template=_classes, mint_node_id=_ids(),
        existing_nodes={})
    assert nodes == ()


def test_an_enabled_template_becomes_an_ordinary_residual_node(conn):
    library = build_library(SLOTS)
    choices = (ResidualChoice(
        template_name="Review Later", action=ENABLE,
        disposition=PHYSICAL_DESTINATION, display_label=None,
        parent_node_id=None, root_anchor="root_documents", merge_into=None,
        replaces_node_id=None),)
    node, = project_residual_nodes(
        library, choices, plan_version_id="plan_1",
        handling_class_for_template=_classes, mint_node_id=_ids(),
        existing_nodes={})
    assert isinstance(node, Node)
    assert node.node_role == RESIDUAL
    assert node.disposition == PHYSICAL_DESTINATION
    assert node.accepts_placement is True
    assert node.display_label == "Review Later"
    assert node.existing_path is None


def test_rename_changes_the_label_and_not_the_template_identity(conn):
    library = build_library(SLOTS)
    choices = (ResidualChoice(
        template_name="Review Later", action=RENAME_RESIDUAL,
        disposition=REVIEW_ONLY, display_label="To Triage",
        parent_node_id=None, root_anchor="root_documents", merge_into=None,
        replaces_node_id=None),)
    node, = project_residual_nodes(
        library, choices, plan_version_id="plan_1",
        handling_class_for_template=_classes, mint_node_id=_ids(),
        existing_nodes={})
    assert node.display_label == "To Triage"
    assert library["Review Later"].template_name == "Review Later"


def test_relocate_moves_the_node_off_the_templates_default_parent(conn):
    library = build_library(SLOTS)
    choices = (ResidualChoice(
        template_name="Temporary Screenshots", action=RELOCATE,
        disposition=PHYSICAL_DESTINATION, display_label=None,
        parent_node_id="n_desktop", root_anchor="root_desktop", merge_into=None,
        replaces_node_id=None),)
    node, = project_residual_nodes(
        library, choices, plan_version_id="plan_1",
        handling_class_for_template=_classes, mint_node_id=_ids(),
        existing_nodes={})
    assert node.parent_node_id == "n_desktop"
    assert node.root_anchor == "root_desktop"


def test_two_merged_templates_resolve_to_one_node(conn):
    library = build_library(SLOTS)
    choices = (
        ResidualChoice(template_name="Reading Inbox", action=ENABLE,
                       disposition=REVIEW_ONLY, display_label=None,
                       parent_node_id=None, root_anchor="root_documents",
                       merge_into=None, replaces_node_id=None),
        ResidualChoice(template_name="Review Later", action=MERGE_RESIDUAL,
                       disposition=REVIEW_ONLY, display_label=None,
                       parent_node_id=None, root_anchor="root_documents",
                       merge_into="Reading Inbox", replaces_node_id=None),
    )
    nodes = project_residual_nodes(
        library, choices, plan_version_id="plan_1",
        handling_class_for_template=_classes, mint_node_id=_ids(),
        existing_nodes={})
    assert len(nodes) == 1
    assert nodes[0].display_label == "Reading Inbox"


def test_replace_with_existing_maps_review_later_onto_an_existing_to_sort(conn):
    """§7.4's own case: a user who "already has an existing `To Sort` folder"
    gets Review Later mapped onto it "rather than inventing a new one"."""
    library = build_library(SLOTS)
    existing = Node(
        node_id="n_to_sort", plan_version_id="plan_1", node_type="existing",
        display_label="To Sort", parent_node_id=None,
        root_anchor="root_documents", ordinal=0, associated_group_ids=(),
        explanation="An existing folder the scan found, with 42 files.",
        node_role="ordinary", accepts_placement=True,
        handling_class="personal_non_sensitive", origin_node_id="n_to_sort",
        existing_path="/Users/jy/Documents/To Sort",
    )
    choices = (ResidualChoice(
        template_name="Review Later", action=REPLACE_WITH_EXISTING,
        disposition=PHYSICAL_DESTINATION, display_label=None,
        parent_node_id=None, root_anchor=None, merge_into=None,
        replaces_node_id="n_to_sort"),)
    node, = project_residual_nodes(
        library, choices, plan_version_id="plan_1",
        handling_class_for_template=_classes, mint_node_id=_ids(),
        existing_nodes={"n_to_sort": existing})
    assert node.node_id == "n_to_sort"
    assert node.node_type == "existing"
    assert node.node_role == RESIDUAL
    assert node.existing_path == "/Users/jy/Documents/To Sort"


def test_all_three_dispositions_reach_a_node(conn):
    library = build_library(SLOTS)
    choices = (
        ResidualChoice("Receipts and Confirmations", ENABLE, PHYSICAL_DESTINATION,
                       None, None, "root_documents", None, None),
        ResidualChoice("Reading Inbox", ENABLE, REVIEW_ONLY, None, None,
                       "root_documents", None, None),
        ResidualChoice("Unsupported or Encrypted", ENABLE, LEAVE_IN_PLACE, None,
                       None, "root_documents", None, None),
    )
    nodes = project_residual_nodes(
        library, choices, plan_version_id="plan_1",
        handling_class_for_template=_classes, mint_node_id=_ids(),
        existing_nodes={})
    assert {n.disposition for n in nodes} == {
        PHYSICAL_DESTINATION, REVIEW_ONLY, LEAVE_IN_PLACE}


def test_an_enabled_template_without_a_disposition_is_refused(conn):
    library = build_library(SLOTS)
    choices = (ResidualChoice("Review Later", ENABLE, None, None, None,
                              "root_documents", None, None),)
    with pytest.raises(ConfigurationRequired):
        project_residual_nodes(
            library, choices, plan_version_id="plan_1",
            handling_class_for_template=_classes, mint_node_id=_ids(),
            existing_nodes={})


def test_protected_records_carries_its_class_onto_the_node(conn):
    """§7.3 and §8.4: Protected Records "should normally remain local-only and
    must not cause filenames or content to be exposed in model prompts". That is
    expressed through the node's handling class, not through special-casing in
    P11."""
    library = build_library(SLOTS)
    choices = (ResidualChoice("Protected Records", ENABLE, REVIEW_ONLY, None,
                              None, "root_documents", None, None),)
    node, = project_residual_nodes(
        library, choices, plan_version_id="plan_1",
        handling_class_for_template=_classes, mint_node_id=_ids(),
        existing_nodes={})
    assert node.handling_class == "sensitive_personal"


def test_a_choice_naming_a_template_the_library_does_not_hold_is_refused(conn):
    library = build_library(SLOTS)
    choices = (ResidualChoice("Random PDF Things", ENABLE, PHYSICAL_DESTINATION,
                              None, None, "root_documents", None, None),)
    with pytest.raises(ConfigurationRequired) as excinfo:
        project_residual_nodes(
            library, choices, plan_version_id="plan_1",
            handling_class_for_template=_classes, mint_node_id=_ids(),
            existing_nodes={})
    assert "Random PDF Things" in str(excinfo.value)
