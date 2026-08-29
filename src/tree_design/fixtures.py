# src/tree_design/fixtures.py
"""Golden P10 fixtures. P11 and P12 build against these before P10 runs.

Everything here is hand-authored and deterministic. Nothing reads a database,
scans a directory, or calls a model — a fixture that needed the pipeline to
exist would not be usable by the parts waiting for it.

**Why this is in `src/` rather than in a consumer's test tree.** P11 was
hand-building P10's records in `tests/p11/p10_fixtures.py`, and not merely their
values: that module declares its own `FrozenTree`, `DestinationProfile`,
`FreezeRecord`, `Restrictions` and `NodeContext`. Two definitions of one record
agree until they do not, and nothing says when. MINOR 6 settles the ownership —
P10 owns the tree, so P10 publishes what its consumers build against.

Every record below is built by P10's OWN constructor. That is the property that
makes these worth publishing: a fixture violating a P10 invariant cannot be
built at all, so these cannot drift from the records they stand for.

`store_fixture_tree` is the other half. It writes this same tree through the
real store and reads it back through `freeze.frozen_tree`, which is how the
suite proves the published fixture and the live read are the same record —
`tests/p10/test_p10_fixtures.py` compares them field by field.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping, Sequence

from tree_design.catalogue import TemplateCatalogue, load_catalogue
from tree_design.freeze import FreezeRecord, FrozenTree
from tree_design.profiles import (
    AnchorExcerpt,
    DestinationProfile,
    NodeContext,
    Restrictions,
)
from tree_design.records import (
    ExpectedValue,
    Node,
    PlanVersion,
    SharedMaterialPolicy,
)
from tree_design.residuals import ResidualChoice, ResidualTemplate, build_library
from tree_design.schema import create_tree_schema
from tree_design.store import (
    set_shared_material_policy,
    write_node,
    write_plan_version,
)
from tree_design.vocabulary import (
    BUILT_IN,
    EXISTING,
    CROSS_DOMAIN,
    IGNORED,
    LEAVE_IN_PLACE,
    ORDINARY,
    PHYSICAL_DESTINATION,
    PRIMARY_HOME,
    PROPOSED,
    PROTECTED,
    PROTECTED_RECORDS,
    PUBLISHED,
    REQUIRED,
    RESIDUAL,
    RESIDUAL_DEFAULT_PARENTS,
    REFINE_LATER,
    REFINED,
    RESIDUAL_TEMPLATE_NAMES,
    REVIEW_LATER,
    REVIEW_ONLY,
    SURFACE_CANVAS,
    TEMPORARY_SCREENSHOTS,
    TREATMENT_RETAINED,
    SHALLOW_BY_CHOICE,
)

PLAN_1: str = "plan_1"
PLAN_2: str = "plan_2"
ROOT: str = "root_documents"
CREATED_AT: str = "2026-08-27T00:00:00Z"
SELECTION_ID: str = "sel_fixture"

#: The handling class every ordinary fixture node carries. P7 owns the set and
#: publishes no ordering, so this NAMES one member rather than choosing a rank.
ORDINARY_CLASS: str = "personal_non_sensitive"
PROTECTED_CLASS: str = "highly_sensitive_credential_bearing"


def _node(node_id: str, label: str, *, node_type: str = PROPOSED,
          role: str = ORDINARY, parent: str | None = None, ordinal: int = 0,
          version: str = PLAN_1, explanation: str | None = None,
          origin: str | None = None, **extra) -> Node:
    """One node, through `Node.__post_init__`. Nothing here bypasses a check."""
    return Node(
        node_id=node_id,
        plan_version_id=version,
        node_type=node_type,
        display_label=label,
        parent_node_id=parent,
        root_anchor=ROOT,
        ordinal=ordinal,
        associated_group_ids=extra.pop("associated_group_ids", ()),
        explanation=explanation or (
            f"{label} appeared because the accepted groups beneath it share "
            "validated facts."),
        node_role=role,
        accepts_placement=extra.pop(
            "accepts_placement", node_type not in (IGNORED, PROTECTED)),
        handling_class=extra.pop("handling_class", ORDINARY_CLASS),
        origin_node_id=origin or node_id,
        **extra,
    )


def walking_skeleton_tree() -> tuple[Node, ...]:
    """DM2(a). TWO hand-authored nodes, no template context, no groups.

    Two and not one: resolution B8(b) requires the skeleton to EXERCISE §6.10's
    margin condition rather than bypass it, and with a single candidate
    `margin_over_next` has nothing to be a margin over — a scorer that never
    compared anything would look correct on a one-node tree.
    """
    return (
        _node("skel_1", "Academics", ordinal=0,
              refinement_disposition=SHALLOW_BY_CHOICE,
              refinement_reason="The skeleton is one level on purpose; no "
                                "template produced it and nothing under it has "
                                "been split.",
              explanation="Hand-authored skeleton node; no template produced it."),
        _node("skel_2", "Finance", ordinal=1,
              refinement_disposition=SHALLOW_BY_CHOICE,
              refinement_reason="The skeleton is one level on purpose; no "
                                "template produced it and nothing under it has "
                                "been split.",
              explanation="The second skeleton node exists so §6.10's margin "
                          "has a runner-up to be measured against."),
    )


def realistic_tree() -> tuple[Node, ...]:
    """DM2(b). A tree carrying every node kind P11 must actually handle.

    A fixture of nothing but `proposed` nodes would let P11 ship without ever
    meeting a node it may NOT place into — and `protected` and `ignored` are
    exactly those. Both are present, in the tree and counted, which is the
    standing rule: marked, never removed.
    """
    school = ExpectedValue(field="school", value="Columbia")
    subject = ExpectedValue(field="subject", value="PHYS1401")
    return (
        _node("n_academics", "Academics", ordinal=0,
              associated_group_ids=("g_phys1401",),
              refinement_disposition=REFINED,
              refinement_reason="The school and course levels beneath this area "
                                "are populated, so it is split as far as the "
                                "evidence supports.",
              explanation="The accepted PHYS 1401 course-material group "
                          "produced this area."),
        _node("n_columbia", "Columbia", parent="n_academics", ordinal=0,
              associated_group_ids=("g_phys1401",),
              dimension_role="school", dimension="school",
              expected_values=(school,),
              refinement_disposition=REFINED,
              refinement_reason="The course level beneath this school is "
                                "populated from settled facts.",
              explanation="3 of this branch's files record their School as "
                          "'Columbia'. P6 settled that value."),
        _node("n_phys", "PHYS1401", parent="n_columbia", ordinal=0,
              associated_group_ids=("g_phys1401",),
              dimension_role="subject", dimension="subject",
              expected_values=(school, subject),
              refinement_disposition=SHALLOW_BY_CHOICE,
              refinement_reason="The user chose to keep this branch shallow; "
                                "eleven files do not need a further split.",
              explanation="11 of this branch's files record their Course as "
                          "'PHYS1401'. P6 settled that value."),
        _node("n_review", REVIEW_LATER, parent="n_academics", ordinal=1,
              role=RESIDUAL, disposition=REVIEW_ONLY,
              refinement_disposition=SHALLOW_BY_CHOICE,
              refinement_reason="§7.2 caps a residual template's depth; a review "
                                "queue that grew levels would stop being one.",
              explanation="Files that reached no course branch are queued here "
                          "for review rather than moved."),
        _node("n_protected", "Passports and IDs", parent="n_academics",
              ordinal=2, node_type=PROTECTED, handling_class=PROTECTED_CLASS,
              explanation="The scan marked this area as protected. It is shown "
                          "and counted here and no file in it is opened or "
                          "moved."),
        _node("n_ignored", "Old Backups", parent="n_academics", ordinal=3,
              node_type=IGNORED,
              explanation="An existing folder the user chose to leave "
                          "untouched (§5.10). It is shown and is not a "
                          "destination."),
        # `existing_path` belongs to an `existing` node and to no other kind —
        # it is an observed fact about the corpus, never a composition. The
        # record refuses it anywhere else, which is how this fixture found its
        # own first mistake.
        _node("n_existing", "Coursework", parent="n_academics", ordinal=4,
              node_type=EXISTING, existing_path="Documents/Coursework",
              refinement_disposition=REFINE_LATER,
              refinement_reason="The user kept their existing folder and has not "
                                "yet decided how, or whether, to split it.",
              explanation="A folder the corpus already contains; P10 observed "
                          "it rather than proposing it."),
    )


def _profile(node: Node) -> DestinationProfile:
    """§6.1's profile for one fixture node, through P10's own record."""
    return DestinationProfile(
        node_id=node.node_id,
        display_label=node.display_label,
        domains=("academic",),
        template_binding=None,
        template_fields=tuple(v.field for v in node.expected_values),
        expected_values=node.expected_values,
        parent_context=(),
        child_context=(),
        accepted_group_ids=node.associated_group_ids,
        group_labels=tuple(f"group {gid}" for gid in node.associated_group_ids),
        representative_files=(),
        anchor_files=(),
        anchor_excerpts=(AnchorExcerpt(observation_key="obs_fixture",
                                       node_id=node.node_id),),
        known_document_types=("syllabus",),
        known_exclusions=(),
        user_edits=(),
        restrictions=Restrictions(
            handling_class=node.handling_class,
            accepts_placement=node.accepts_placement,
            node_role=node.node_role,
            disposition=node.disposition,
        ),
    )


#: What the fixture freeze declares for each §7.4 residual slot. Named here
#: rather than at each call site so the fixture tree and the stored tree cannot
#: disagree about the configuration they were frozen under.
RESIDUAL_CONFIGURATION: Mapping[str, str] = {REVIEW_LATER: REVIEW_ONLY}
SHARED_MATERIAL_POLICY: str = PRIMARY_HOME
SHARED_MATERIAL_POLICY_ID: str = "smp_fixture"


def _freeze_record(nodes: Sequence[Node]) -> FreezeRecord:
    return FreezeRecord(
        plan_version_id=PLAN_1,
        created_at=CREATED_AT,
        node_ids=tuple(node.node_id for node in nodes),
        # Present and legal to SEE is not legal to PLACE INTO. The protected and
        # ignored nodes are in `node_ids` above and out of this set.
        legal_destination_ids=frozenset(
            node.node_id for node in nodes if node.accepts_placement),
        template_bindings=(),
        labels_and_aliases={node.node_id: (node.display_label,)
                            for node in nodes},
        residual_configuration=dict(RESIDUAL_CONFIGURATION),
        shared_material_policy_ids=(SHARED_MATERIAL_POLICY_ID,),
        cross_folder_moves=False,
        selection_id=SELECTION_ID,
    )


def frozen_tree_fixture() -> FrozenTree:
    """DM2(e). The record P11's G-P10 gate reads, as a value.

    It returns `FrozenTree` and NOT `FreezeRecord`, and that is what makes the
    P11 swap one line: `freeze.frozen_tree` returns the same type, so replacing
    this call with that one reshapes no P11 test. A fixture returning an id list
    against a live read returning a bundle would turn the swap into a rewrite of
    every P11 test that touches a node or a profile.
    """
    nodes = realistic_tree()
    return FrozenTree(
        plan_version_id=PLAN_1,
        freeze_record=_freeze_record(nodes),
        nodes=nodes,
        profiles=tuple(_profile(node) for node in nodes),
        shared_material_policy=SHARED_MATERIAL_POLICY,
        shared_material_policy_scope=None,
    )


def two_version_pair() -> tuple[tuple[Node, ...], tuple[Node, ...]]:
    """DM2(d). One tree in two plan versions, with lineage and without shared ids.

    SPEC open question 5 — whether a `node_id` is stable across plan versions —
    is OPEN. P10 mints per version and records `origin_node_id`, so a fixture
    that reused ids across the pair would quietly settle a question the design
    deliberately left open, and P11 would build on the answer.
    """
    first = realistic_tree()
    second = tuple(
        _node(f"{node.node_id}_v2", node.display_label,
              node_type=node.node_type, role=node.node_role,
              parent=None if node.parent_node_id is None
              else f"{node.parent_node_id}_v2",
              ordinal=node.ordinal, version=PLAN_2,
              explanation=node.explanation, origin=node.origin_node_id,
              associated_group_ids=node.associated_group_ids,
              handling_class=node.handling_class,
              accepts_placement=node.accepts_placement,
              dimension_role=node.dimension_role, dimension=node.dimension,
              expected_values=node.expected_values,
              existing_path=node.existing_path,
              disposition=node.disposition,
              refinement_disposition=node.refinement_disposition,
              refinement_reason=node.refinement_reason)
        for node in first
    )
    return first, second


def residual_library_fixture() -> tuple[Mapping[str, ResidualTemplate],
                                        tuple[ResidualChoice, ...]]:
    """DM2(c). §7.4's library with all THREE dispositions represented.

    All three produce legal nodes and differ in what happens WHEN one is chosen,
    so a fixture covering one would hide the other two from P11 entirely — and
    `leave-in-place` in particular is the one whose files never move.
    """
    # §7.3 fixes the NINE names and §7.2 the eight attributes; `build_library`
    # refuses a partial library, and rightly — a residual slot P10 filled in
    # itself would be P10 authoring the user's vocabulary. So the fixture states
    # all nine explicitly rather than letting any default appear.
    library = build_library({
        name: {
            "display_name": name,
            # Only four of the nine have a published default parent. The
            # other five have NONE, which is absent configuration rather than
            # an oversight — so this fixture states a location of its own for
            # them and does not reach for a P10 default that does not exist.
            "default_parent_location": RESIDUAL_DEFAULT_PARENTS.get(name, (name,)),
            "accepted_evidence_patterns": ("fixture-pattern",),
            "expected_file_types": ("fixture-type",),
            "sensitivity_restrictions": (),
            "optional_shallow_subfolders": (),
            "max_permitted_depth": 1,
            "treatment": TREATMENT_RETAINED,
        }
        for name in RESIDUAL_TEMPLATE_NAMES
    })
    choices = (
        ResidualChoice(template_name=REVIEW_LATER, action="enable",
                       disposition=REVIEW_ONLY, display_label=REVIEW_LATER,
                       parent_node_id="n_academics", root_anchor=ROOT,
                       merge_into=None, replaces_node_id=None),
        ResidualChoice(template_name=TEMPORARY_SCREENSHOTS, action="enable",
                       disposition=PHYSICAL_DESTINATION,
                       display_label=TEMPORARY_SCREENSHOTS,
                       parent_node_id="n_academics", root_anchor=ROOT,
                       merge_into=None, replaces_node_id=None),
        ResidualChoice(template_name=PROTECTED_RECORDS, action="enable",
                       disposition=LEAVE_IN_PLACE,
                       display_label=PROTECTED_RECORDS,
                       parent_node_id="n_academics", root_anchor=ROOT,
                       merge_into=None, replaces_node_id=None),
    )
    return library, choices


def template_library_fixture() -> TemplateCatalogue:
    """A one-release catalogue, built through the REAL loader.

    `load_catalogue` rather than a hand-built object, so a fixture release the
    live loader would reject cannot be published — the same reason every record
    above goes through its own constructor.
    """
    manifest = {
        "release_id": "rel-fixture",
        "fragments": [{
            "fragment_id": "coursework", "fragment_version": 1,
            "roles": ["subject"], "relative_order": [], "imports": [],
            "optional_roles": [], "metadata_only_roles": [],
            "allowed_values": {}, "privacy_floor": "policy.public",
            "provenance": ["row:fixture"],
        }],
        "definitions": [{
            "template_id": "t.academic", "template_version": 1,
            "origin_kind": BUILT_IN, "scope_kind": CROSS_DOMAIN,
            "publication_state": PUBLISHED,
            "fragment_refs": [{"fragment_id": "coursework",
                               "fragment_version": 1}],
            "candidate_orders": [{
                "order_id": "subject_first", "is_default": True,
                "rationale": "The recommended nesting for coursework.",
                "dimensions": [{
                    "role_ref": "subject", "order_index": 0,
                    "requirement": REQUIRED, "metadata_only": False,
                    "retrieval_rationale": "Users look for a course by name.",
                }],
            }],
            "optional_branch_patterns": [],
            "sensitivity_policy_ref": "policy.public",
            "validation_constraints": [], "example_label_chains": [],
        }],
        "applicabilities": [{
            "applicability_id": "a.academic", "applicability_version": 1,
            "template_id": "t.academic", "template_version": 1,
            "uses_schema": "academic", "purpose_profile_ref": None,
            "allowed_fields": ["subject"],
            "detection_signal_refs": ["signal.fixture"],
            "role_bindings": [{"role_ref": "subject", "field_ref": "subject",
                               "label": "Course"}],
            "exclusions": [], "provenance": ["row:fixture"],
        }],
    }
    return load_catalogue(lambda: json.dumps(manifest))


def store_fixture_tree(conn: sqlite3.Connection) -> FrozenTree:
    """Write `frozen_tree_fixture()`'s tree through the REAL store and read it
    back through `freeze.frozen_tree`.

    This is what turns "the fixture looks like the live record" into a checked
    fact. The suite compares the two field by field, so the published fixture
    and the live read cannot drift without a P10 test failing — which is the
    whole reason these moved out of P11's test tree.
    """
    from tree_design.freeze import freeze, frozen_tree

    create_tree_schema(conn)
    write_plan_version(conn, PlanVersion(
        plan_version_id=PLAN_1, predecessor_id=None, state="draft",
        created_at=CREATED_AT, cross_folder_moves=False,
        selection_id=SELECTION_ID))
    nodes = realistic_tree()
    for node in nodes:
        write_node(conn, node)
    # §6.9's gate is UNCONDITIONAL and that is correct: multi-home-ness is
    # discovered at placement, not decidable at freeze, so every frozen version
    # states a rule in advance. Without it P11 would have to pick an institution
    # for a transcript belonging to two application packets.
    set_shared_material_policy(conn, SharedMaterialPolicy(
        policy_id=SHARED_MATERIAL_POLICY_ID,
        plan_version_id=PLAN_1,
        policy=SHARED_MATERIAL_POLICY,
        policy_scope=None,
        reason="Fixture policy: a shared file gets one primary home and the "
               "other branches reference it."))
    # `freeze` and NOT `store.freeze_version`: the latter marks the version
    # frozen, and `frozen_tree` reads a frozen BUNDLE. Marking without writing
    # the bundle is the state `NotFrozen` exists to name, and reaching for the
    # cheaper call is how a fixture ends up standing for a tree P11 could never
    # actually read.
    freeze(
        conn,
        plan_version_id=PLAN_1,
        created_at=CREATED_AT,
        user_id="fixture-user",
        component_version="p10-fixture",
        # The fixture stands for a tree a person adopted, which is the state P11
        # reads. `SURFACE_UNATTENDED` would make it stand for the shipped
        # command's run instead, and P11's tests are not about that run.
        surface=SURFACE_CANVAS,
        residual_configuration=dict(RESIDUAL_CONFIGURATION),
        approved_branch_ids=tuple(
            node.node_id for node in nodes
            if node.refinement_disposition is not None),
        profiles=tuple(_profile(node) for node in nodes),
    )
    return frozen_tree(conn, plan_version=PLAN_1)
