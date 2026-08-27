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


# --- audit against §7.2-§7.4, derived from the design rather than from the plan --


def _enable(name, disposition, **over):
    kwargs = dict(template_name=name, action=ENABLE, disposition=disposition,
                  display_label=None, parent_node_id=None,
                  root_anchor="root_documents", merge_into=None,
                  replaces_node_id=None)
    kwargs.update(over)
    return ResidualChoice(**kwargs)


def _project(choices, existing_nodes=None):
    return project_residual_nodes(
        build_library(SLOTS), tuple(choices), plan_version_id="plan_1",
        handling_class_for_template=_classes, mint_node_id=_ids(),
        existing_nodes=existing_nodes or {})


def test_all_three_dispositions_yield_a_LEGAL_node(conn):
    """RULING (`00`:121): "Once the user approves the desired residual branches,
    those branches become legal nodes in the frozen destination tree. The LLM may
    choose among them later."

    All three dispositions produce legal nodes and the model may choose among all
    of them. `accepts_placement` answers "is this a legal node the model may
    choose", so it is True for all three. Deriving it from the disposition would
    have made a review-only branch ILLEGAL, contradicting that sentence.

    What the disposition governs is what happens WHEN a node is chosen, not
    WHETHER it can be: "never moves files AUTOMATICALLY" is a statement about
    automation, and `00`:120's "represent without moving" is a first-class
    outcome in this design, not an absence of one.
    """
    for disposition in (PHYSICAL_DESTINATION, REVIEW_ONLY, LEAVE_IN_PLACE):
        node, = _project([_enable("Review Later", disposition)])
        assert node.accepts_placement is True, (
            f"a {disposition!r} residual must still be a node the model may "
            "choose among (00:121)")
        assert node.disposition == disposition


def test_the_disposition_survives_onto_the_node_for_the_review_policy(conn):
    """The guard that stops the disposition being dropped at the seam.

    Legality and movability are different questions, and P11's review policy is
    what reads the second one. If the disposition did not reach the node, the
    only value that distinguishes "move it" from "represent it without moving"
    would be gone before any policy could consult it — and every residual branch
    would behave like a physical destination.
    """
    for disposition in (PHYSICAL_DESTINATION, REVIEW_ONLY, LEAVE_IN_PLACE):
        node, = _project([_enable("Reading Inbox", disposition)])
        assert node.node_role == RESIDUAL
        assert node.disposition == disposition

    existing = Node(
        node_id="n_to_sort", plan_version_id="plan_1", node_type="existing",
        display_label="To Sort", parent_node_id=None, root_anchor="root_documents",
        ordinal=0, associated_group_ids=(),
        explanation="An existing folder the scan found, with 42 files.",
        node_role="ordinary", accepts_placement=True,
        handling_class="personal_non_sensitive", origin_node_id="n_to_sort",
        existing_path="/Users/jy/Documents/To Sort")
    mapped, = _project(
        [ResidualChoice(template_name="Review Later", action=REPLACE_WITH_EXISTING,
                        disposition=REVIEW_ONLY, display_label=None,
                        parent_node_id=None, root_anchor=None, merge_into=None,
                        replaces_node_id="n_to_sort")],
        existing_nodes={"n_to_sort": existing})
    assert mapped.node_id == "n_to_sort"
    assert mapped.disposition == REVIEW_ONLY
    assert mapped.accepts_placement is True


def test_disable_is_the_only_action_that_creates_no_node(conn):
    """`project_residual_nodes` carried TWO checks doing this one job — an
    explicit `action == DISABLE` skip, and a second `action not in
    _CREATING_ACTIONS` skip. `RESIDUAL_LIBRARY_ACTIONS` has six members and
    `_CREATING_ACTIONS` is the five that are not `disable`, so each check made the
    other unreachable and deleting EITHER ONE ALONE left the suite green.

    Two guards that mask each other are worse than one, because neither can be
    tested and a reader cannot tell which is load-bearing.
    """
    from tree_design.vocabulary import RESIDUAL_LIBRARY_ACTIONS

    creating = [a for a in RESIDUAL_LIBRARY_ACTIONS if a != DISABLE]
    assert len(creating) == 5
    assert _project([_enable("Review Later", PHYSICAL_DESTINATION,
                             action=DISABLE)]) == ()
    # and every other action does reach a node
    made = _project([_enable("Review Later", PHYSICAL_DESTINATION)])
    assert len(made) == 1


def test_two_decisions_for_one_template_are_refused_not_doubled(conn):
    """§7.4 is one decision per template. Two produced two branches with the same
    name under different anchors, and the user would see `Review Later` twice with
    no way to tell which one P11 will use."""
    with pytest.raises(ConfigurationRequired) as excinfo:
        _project([_enable("Review Later", PHYSICAL_DESTINATION),
                  _enable("Review Later", PHYSICAL_DESTINATION,
                          action=RELOCATE, root_anchor="root_photos")])
    assert "Review Later" in str(excinfo.value)


def test_an_enabled_template_with_no_root_anchor_is_refused_by_name(conn):
    """`root_anchor=choice.root_anchor or ""` is a placeholder that exists only to
    satisfy the type. The refusal then happened by accident downstream, in
    `Node.__post_init__`, as "Node.root_anchor is required" — a message that names
    neither the template nor the decision the user has to revisit."""
    with pytest.raises(ConfigurationRequired) as excinfo:
        _project([_enable("Review Later", PHYSICAL_DESTINATION, root_anchor=None)])
    assert "Review Later" in str(excinfo.value)


def test_an_absent_default_parent_slot_is_filled_only_where_7_3_states_one(conn):
    """The fixture always PASSED `default_parent_location`, so the fallback was
    never taken and inventing one there was invisible. This drops the slot
    entirely: §7.3's four are filled from §7.3, and the five it leaves unstated
    stay unstated."""
    without = {name: {k: v for k, v in values.items()
                      if k != "default_parent_location"}
               for name, values in SLOTS.items()}
    library = build_library(without)
    assert library["Temporary Screenshots"].default_parent_location == (
        "Photos", "Temporary Screenshots")
    for name in ("Receipts and Confirmations", "Reading Inbox", "Review Later",
                 "Unsupported or Encrypted", "Protected Records"):
        assert library[name].default_parent_location is None, (
            f"{name} got a parent location §7.3 does not state")


def test_a_default_parent_holding_a_path_separator_is_refused(conn):
    """The old test only OBSERVED that the fixture held no separator. It never
    built one, so the guard could be deleted with the suite still green."""
    with pytest.raises(ConfigurationRequired):
        ResidualTemplate(
            template_name="Review Later", display_name="Review Later",
            default_parent_location=("Personal/Review Later",),
            accepted_evidence_patterns=(), expected_file_types=(),
            sensitivity_restrictions=(), optional_shallow_subfolders=(),
            max_permitted_depth=1, treatment=TREATMENT_REVIEWED,
            user_defined=False)


def test_an_authored_area_offered_without_the_user_defined_flag_is_refused(conn):
    """The flag is how a shipped template is told from an authored one. Nothing
    drove the refusal, so it could be deleted silently."""
    unflagged = ResidualTemplate(
        template_name="Shopping Research", display_name="Shopping Research",
        default_parent_location=None, accepted_evidence_patterns=(),
        expected_file_types=(), sensitivity_restrictions=(),
        optional_shallow_subfolders=(), max_permitted_depth=1,
        treatment=TREATMENT_RETAINED, user_defined=False)
    with pytest.raises(ConfigurationRequired) as excinfo:
        build_library(SLOTS, user_defined=(unflagged,))
    assert "Shopping Research" in str(excinfo.value)


def test_merging_into_a_template_that_was_never_enabled_is_refused(conn):
    """Nothing drove this path. With the check gone, `by_name` takes a `None`
    value and the merged template silently resolves to nothing."""
    with pytest.raises(ConfigurationRequired) as excinfo:
        _project([ResidualChoice(
            template_name="Review Later", action=MERGE_RESIDUAL,
            disposition=REVIEW_ONLY, display_label=None, parent_node_id=None,
            root_anchor="root_documents", merge_into="Reading Inbox",
            replaces_node_id=None)])
    assert "Reading Inbox" in str(excinfo.value)


def test_replacing_a_node_that_is_not_in_the_version_is_refused(conn):
    """Nothing drove this path either; with the check gone it is an
    `AttributeError` on `None`, which tells the user nothing."""
    with pytest.raises(ConfigurationRequired) as excinfo:
        _project([ResidualChoice(
            template_name="Review Later", action=REPLACE_WITH_EXISTING,
            disposition=PHYSICAL_DESTINATION, display_label=None,
            parent_node_id=None, root_anchor=None, merge_into=None,
            replaces_node_id="n_absent")])
    assert "n_absent" in str(excinfo.value)
