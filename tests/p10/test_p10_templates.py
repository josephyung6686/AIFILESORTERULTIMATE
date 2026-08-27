"""P10 Task 6 — four records that must not collapse into one.

The composable-template design is explicit: "P10 must not collapse these objects
into a single 'template' row." A fragment is reusable organization logic with no
values and no field mappings. A definition composes exact fragment versions. An
applicability row maps roles to live P6 fields for exactly ONE `uses_schema`. A
branch binding records what one branch in one draft actually chose.

Applicability is never nested inside a definition, because nesting is what turns
"one recipe, two domains" into two copies that drift.

TWO AMENDMENTS TO THE PLAN, both owner rulings, both tested below:

1. **Dimension order is a RUNTIME choice** (§5.3, §5.8). The plan gave
   `TemplateDefinition` a single `dimensions` tuple, which makes the ordering the
   recipe's decision. It is not: the definition offers CANDIDATE orders and names
   one default, and the end user picks per branch. `candidate_orders` replaces
   `dimensions`; `definition.dimensions` survives as the default order's
   dimensions so a reader still has one recommended shape.
2. **`purpose_profile_ref` is ENFORCED distinct** from a P6 purpose value and
   from a runtime P9 group id, not merely documented as such. A bare string is
   refused because neither of those carries a version, and the authored namespace
   is refused to anything shaped like P6's field key or P9's live mint.
"""
from __future__ import annotations

import dataclasses
import json

import pytest

from tree_design.catalogue import load_catalogue
from tree_design.templates import (
    ApplicabilityRef,
    BranchTemplateBinding,
    CompositionConflict,
    DimensionOrder,
    FragmentRef,
    MalformedTemplateRecord,
    PurposeProfileRef,
    ResolvedDimension,
    RoleBinding,
    TemplateApplicability,
    TemplateDefinition,
    TemplateDimension,
    TemplateFragment,
    branch_dimension_roles,
    merge_fragment_constraints,
    resolve_fragment_imports,
)
from tree_design.vocabulary import (
    ACTION_ADDED,
    ACTION_RENAMED,
    ACTION_SELECTED,
    BUILT_IN,
    DOMAIN_FOCUSED,
    PUBLISHED,
    REFINED,
    REQUIRED,
    SCOPE_SCHEMA_FIELD,
    WORKFLOW_APPROVED,
    WORKFLOW_DRAFT,
)

ARTIFACT_KIND = TemplateFragment(
    fragment_id="artifact-kind", fragment_version=1, roles=("artifact_kind",),
    relative_order=(), imports=(), optional_roles=(), metadata_only_roles=(),
    allowed_values={}, privacy_floor="policy.public", provenance=("row:academic-01",),
)
SUBJECT_STAGE = TemplateFragment(
    fragment_id="subject-stage", fragment_version=1,
    roles=("subject", "lifecycle_stage"),
    relative_order=(("subject", "lifecycle_stage"),), imports=(),
    optional_roles=("lifecycle_stage",), metadata_only_roles=(),
    allowed_values={}, privacy_floor="policy.public", provenance=("row:research-02",),
)

SUBJECT_FIRST = DimensionOrder(
    order_id="subject-first", is_default=True,
    rationale="Users search by the course before the kind of work.",
    dimensions=(
        TemplateDimension(role_ref="subject", order_index=0, requirement=REQUIRED,
                          metadata_only=False,
                          retrieval_rationale="The course is the level users search by."),
        TemplateDimension(role_ref="artifact_kind", order_index=1,
                          requirement=REQUIRED, metadata_only=False,
                          retrieval_rationale="Homework and exams are looked for apart."),
    ),
)
KIND_FIRST = DimensionOrder(
    order_id="kind-first", is_default=False,
    rationale="A user revising for exams across every course wants kind first.",
    dimensions=(
        TemplateDimension(role_ref="artifact_kind", order_index=0,
                          requirement=REQUIRED, metadata_only=False,
                          retrieval_rationale="Exams across courses are one study session."),
        TemplateDimension(role_ref="subject", order_index=1, requirement=REQUIRED,
                          metadata_only=False,
                          retrieval_rationale="The course still separates the material."),
    ),
)
ONLY_SUBJECT = DimensionOrder(
    order_id="subject-only", is_default=True,
    rationale="One dimension has one order; there is nothing to choose between.",
    dimensions=(
        TemplateDimension(role_ref="subject", order_index=0, requirement=REQUIRED,
                          metadata_only=False,
                          retrieval_rationale="The course is the level users search by."),
    ),
)


def _catalogue(*extra):
    manifest = {
        "release_id": "rel-1",
        "fragments": [dataclasses.asdict(f) for f in (ARTIFACT_KIND, SUBJECT_STAGE, *extra)],
        "definitions": [],
        "applicabilities": [],
    }
    return load_catalogue(lambda: json.dumps(manifest))


def test_a_fragment_carries_no_user_value_and_no_field_mapping():
    with pytest.raises(TypeError):
        TemplateFragment(
            fragment_id="bad", fragment_version=1, roles=("subject",),
            relative_order=(), imports=(), optional_roles=(),
            metadata_only_roles=(), allowed_values={}, privacy_floor="policy.public",
            provenance=(), field_bindings=(("subject", "subject"),),
        )


def test_a_definition_pins_exact_fragment_versions_and_never_nests_applicability():
    definition = TemplateDefinition(
        template_id="academic-coursework", template_version=1,
        origin_kind=BUILT_IN, scope_kind=DOMAIN_FOCUSED,
        publication_state=PUBLISHED,
        fragment_refs=(FragmentRef("artifact-kind", 1),),
        candidate_orders=(SUBJECT_FIRST, KIND_FIRST),
        optional_branch_patterns=(), sensitivity_policy_ref="policy.public",
        validation_constraints=(),
        example_label_chains=(("Academics", "Columbia", "PHYS1401"),),
    )
    assert definition.fragment_refs[0].fragment_version == 1
    assert not hasattr(definition, "uses_schema")
    assert not hasattr(definition, "role_bindings")
    assert not hasattr(definition, "applicability")


# --- amendment 1: dimension order is the end user's choice, per branch ----------


def test_a_definition_offers_candidate_orders_and_names_one_default():
    """§5.3 and §5.8: the ordering is a RUNTIME decision, so the recipe offers
    alternatives and recommends one. A single `dimensions` tuple would make the
    recipe's author the one who decided, which is the whole thing the owner
    ruling rejects."""
    definition = TemplateDefinition(
        template_id="academic-coursework", template_version=1,
        origin_kind=BUILT_IN, scope_kind=DOMAIN_FOCUSED,
        publication_state=PUBLISHED, fragment_refs=(),
        candidate_orders=(SUBJECT_FIRST, KIND_FIRST),
        optional_branch_patterns=(), sensitivity_policy_ref="policy.public",
        validation_constraints=(), example_label_chains=(),
    )
    assert definition.default_order is SUBJECT_FIRST
    assert [d.role_ref for d in definition.dimensions] == ["subject", "artifact_kind"]
    assert [o.order_id for o in definition.candidate_orders] == [
        "subject-first", "kind-first"]
    assert "dimensions" not in {f.name for f in dataclasses.fields(TemplateDefinition)}


def test_a_multi_dimension_recipe_that_offers_one_order_is_refused():
    """The floor, not a ceiling. Offering one order for a recipe with two
    dimensions is the single-`dimensions` shape wearing a new field name, and the
    user would have nothing to pick between. No maximum is enforced, because a
    ceiling on how many orders a recipe may offer is a number the design does not
    state."""
    with pytest.raises(MalformedTemplateRecord) as excinfo:
        TemplateDefinition(
            template_id="t", template_version=1, origin_kind=BUILT_IN,
            scope_kind=DOMAIN_FOCUSED, publication_state=PUBLISHED,
            fragment_refs=(), candidate_orders=(SUBJECT_FIRST,),
            optional_branch_patterns=(), sensitivity_policy_ref="policy.public",
            validation_constraints=(), example_label_chains=(),
        )
    assert "candidate order" in str(excinfo.value)


def test_a_one_dimension_recipe_needs_only_one_order():
    """One dimension has exactly one ordering. Demanding a second would force an
    author to invent a choice that does not exist."""
    definition = TemplateDefinition(
        template_id="flat", template_version=1, origin_kind=BUILT_IN,
        scope_kind=DOMAIN_FOCUSED, publication_state=PUBLISHED, fragment_refs=(),
        candidate_orders=(ONLY_SUBJECT,), optional_branch_patterns=(),
        sensitivity_policy_ref="policy.public", validation_constraints=(),
        example_label_chains=(),
    )
    assert definition.default_order is ONLY_SUBJECT


def test_exactly_one_candidate_order_is_the_default():
    two_defaults = dataclasses.replace(KIND_FIRST, is_default=True)
    with pytest.raises(MalformedTemplateRecord):
        TemplateDefinition(
            template_id="t", template_version=1, origin_kind=BUILT_IN,
            scope_kind=DOMAIN_FOCUSED, publication_state=PUBLISHED,
            fragment_refs=(), candidate_orders=(SUBJECT_FIRST, two_defaults),
            optional_branch_patterns=(), sensitivity_policy_ref="policy.public",
            validation_constraints=(), example_label_chains=(),
        )
    no_default = dataclasses.replace(SUBJECT_FIRST, is_default=False)
    with pytest.raises(MalformedTemplateRecord):
        TemplateDefinition(
            template_id="t", template_version=1, origin_kind=BUILT_IN,
            scope_kind=DOMAIN_FOCUSED, publication_state=PUBLISHED,
            fragment_refs=(), candidate_orders=(no_default, KIND_FIRST),
            optional_branch_patterns=(), sensitivity_policy_ref="policy.public",
            validation_constraints=(), example_label_chains=(),
        )


def test_every_candidate_order_covers_the_same_roles():
    """An order that drops a role is a different RECIPE, not a different order.
    Allowing it would let the user's ordering choice silently change what the
    branch organizes by."""
    shorter = dataclasses.replace(
        KIND_FIRST, dimensions=KIND_FIRST.dimensions[:1])
    with pytest.raises(MalformedTemplateRecord) as excinfo:
        TemplateDefinition(
            template_id="t", template_version=1, origin_kind=BUILT_IN,
            scope_kind=DOMAIN_FOCUSED, publication_state=PUBLISHED,
            fragment_refs=(), candidate_orders=(SUBJECT_FIRST, shorter),
            optional_branch_patterns=(), sensitivity_policy_ref="policy.public",
            validation_constraints=(), example_label_chains=(),
        )
    assert "same roles" in str(excinfo.value)


def test_an_order_must_be_a_contiguous_position_list_and_state_why():
    with pytest.raises(MalformedTemplateRecord):
        DimensionOrder(
            order_id="gap", is_default=True, rationale="why",
            dimensions=(
                TemplateDimension("subject", 0, REQUIRED, False, "why"),
                TemplateDimension("artifact_kind", 2, REQUIRED, False, "why"),
            ),
        )
    with pytest.raises(MalformedTemplateRecord):
        DimensionOrder(
            order_id="no-reason", is_default=True, rationale="",
            dimensions=(TemplateDimension("subject", 0, REQUIRED, False, "why"),),
        )


def test_a_binding_records_which_candidate_order_the_user_took():
    """Without it, "the user accepted the kind-first candidate" and "the user
    hand-reordered into the same shape" are indistinguishable, and §8.8 requires
    ordering choices be captured per plan version."""
    common = dict(
        binding_id="btb_1", plan_version_id="plan_1", branch_node_id="n_1",
        applicability_refs=(ApplicabilityRef("a", 1),), resolved_dimensions=(),
        accepted_group_ids=("g_1",), state=WORKFLOW_DRAFT, depth_disposition=REFINED,
        refinement_reason="reason", validation_report_ref="vr_1",
        approval_action_ref=None, justification_fact_refs=("f_1",),
    )
    took_candidate = BranchTemplateBinding(**common, chosen_order_id="kind-first")
    assert took_candidate.chosen_order_id == "kind-first"
    hand_built = BranchTemplateBinding(**common, chosen_order_id=None)
    assert hand_built.chosen_order_id is None


# --- the remaining three records ------------------------------------------------


def test_a_definition_may_not_carry_branch_specific_justification():
    """§5.7's `justification_fact_refs` belong to the validation report and the
    branch binding. In an immutable reusable definition they would be one
    branch's evidence presented as the recipe's own."""
    assert "justification_fact_refs" not in {
        f.name for f in dataclasses.fields(TemplateDefinition)
    }
    assert "justification_fact_refs" in {
        f.name for f in dataclasses.fields(BranchTemplateBinding)
    }


def test_an_example_label_chain_is_labels_and_never_a_path():
    with pytest.raises(MalformedTemplateRecord) as excinfo:
        TemplateDefinition(
            template_id="t", template_version=1, origin_kind=BUILT_IN,
            scope_kind=DOMAIN_FOCUSED, publication_state=PUBLISHED,
            fragment_refs=(), candidate_orders=(ONLY_SUBJECT,),
            optional_branch_patterns=(), sensitivity_policy_ref="policy.public",
            validation_constraints=(),
            example_label_chains=(("Academics/Columbia",),),
        )
    assert "separator" in str(excinfo.value)


def test_an_applicability_row_names_exactly_one_schema_and_carries_provenance():
    row = TemplateApplicability(
        applicability_id="academic-coursework--academic", applicability_version=1,
        template_id="academic-coursework", template_version=1,
        uses_schema="academic", purpose_profile_ref=None,
        allowed_fields=("subject", "work_type"),
        detection_signal_refs=("signal.syllabus_header",),
        role_bindings=(RoleBinding("subject", "subject"),
                       RoleBinding("artifact_kind", "work_type")),
        exclusions=(), provenance=("row:academic-01", "memo:academic-reuse"),
    )
    assert row.uses_schema == "academic"
    assert row.provenance
    with pytest.raises(MalformedTemplateRecord):
        dataclasses.replace(row, uses_schema="")
    with pytest.raises(MalformedTemplateRecord) as excinfo:
        dataclasses.replace(row, provenance=())
    assert "provenance" in str(excinfo.value)


def test_a_role_binding_must_target_a_field_the_row_allows():
    with pytest.raises(MalformedTemplateRecord):
        TemplateApplicability(
            applicability_id="a", applicability_version=1, template_id="t",
            template_version=1, uses_schema="academic", purpose_profile_ref=None,
            allowed_fields=("subject",), detection_signal_refs=(),
            role_bindings=(RoleBinding("artifact_kind", "work_type"),),
            exclusions=(), provenance=("row:x",),
        )


def test_a_purpose_profile_ref_is_authored_and_versioned():
    """It is neither P6's Applications-only `purpose` field nor a runtime P9
    group id, and it creates no universal purpose taxonomy."""
    ref = PurposeProfileRef(purpose_profile_id="pp.grad-application",
                            purpose_profile_version=1)
    row = TemplateApplicability(
        applicability_id="a", applicability_version=1, template_id="t",
        template_version=1, uses_schema="college_applications",
        purpose_profile_ref=ref, allowed_fields=("target_school",),
        detection_signal_refs=(), role_bindings=(RoleBinding("counterpart", "target_school"),),
        exclusions=(), provenance=("row:apps-01",),
    )
    assert row.purpose_profile_ref.purpose_profile_version == 1
    with pytest.raises(MalformedTemplateRecord):
        dataclasses.replace(row, purpose_profile_ref="g_columbia_app")


# --- amendment 2: the distinctness is enforced, not documented ------------------


def test_p6s_live_purpose_field_key_cannot_be_a_purpose_profile_id():
    """Read from P6's own catalogue, so this test breaks if P6 renames the field
    rather than quietly passing against a string P10 remembered."""
    from facts.fields import FIELD_ROWS

    live = {row.field_key for row in FIELD_ROWS if row.field_key == "purpose"}
    assert live == {"purpose"}, "P6 no longer publishes a `purpose` field key"
    with pytest.raises(MalformedTemplateRecord) as excinfo:
        PurposeProfileRef(purpose_profile_id="purpose", purpose_profile_version=1)
    assert "authored" in str(excinfo.value)


def test_a_runtime_p9_group_id_cannot_be_a_purpose_profile_id():
    """P9 mints `group:{file_id}:{seed_kind}` (`src/grouping/pipeline.py:323`).
    A purpose profile is authored once and reviewed; a group id is minted per run
    per file. Storing one where the other belongs would tie a reusable recipe to
    one user's run."""
    with pytest.raises(MalformedTemplateRecord):
        PurposeProfileRef(purpose_profile_id="group:f1:direct-anchor",
                          purpose_profile_version=1)
    with pytest.raises(MalformedTemplateRecord):
        PurposeProfileRef(purpose_profile_id="g_columbia_app",
                          purpose_profile_version=1)


def test_an_unversioned_purpose_profile_is_refused_at_the_record():
    """A P6 purpose value and a P9 group id are both bare strings. Requiring the
    versioned record is what makes "distinct" structural rather than a naming
    convention nobody checks."""
    with pytest.raises(MalformedTemplateRecord):
        PurposeProfileRef(purpose_profile_id="pp.grad-application",
                          purpose_profile_version=0)


def test_a_branch_binding_records_all_six_dimension_actions():
    binding = BranchTemplateBinding(
        binding_id="btb_1", plan_version_id="plan_1", branch_node_id="n_academics",
        applicability_refs=(ApplicabilityRef("academic-coursework--academic", 1),),
        resolved_dimensions=(
            ResolvedDimension(role_ref="subject", field_ref="subject",
                              action=ACTION_SELECTED, order_index=0,
                              display_label=None, scope=SCOPE_SCHEMA_FIELD),
            ResolvedDimension(role_ref="artifact_kind", field_ref="work_type",
                              action=ACTION_RENAMED, order_index=1,
                              display_label="Assignments", scope=SCOPE_SCHEMA_FIELD),
            ResolvedDimension(role_ref="term", field_ref="term",
                              action=ACTION_ADDED, order_index=2,
                              display_label=None, scope=SCOPE_SCHEMA_FIELD),
        ),
        accepted_group_ids=("g_phys1401",), state=WORKFLOW_APPROVED,
        depth_disposition=REFINED,
        refinement_reason="The accepted course groups justify the split.",
        validation_report_ref="vr_1", approval_action_ref="ra_1",
        justification_fact_refs=("fact_g_phys1401",), chosen_order_id="subject-first",
    )
    assert {d.action for d in binding.resolved_dimensions} == {
        ACTION_SELECTED, ACTION_RENAMED, ACTION_ADDED,
    }


def test_an_approved_binding_requires_a_recorded_user_action():
    """C8 and §5.7: validity is not activation. A binding that reached
    `approved` without an approval action is a template that activated itself."""
    common = dict(
        binding_id="btb_1", plan_version_id="plan_1", branch_node_id="n_1",
        applicability_refs=(ApplicabilityRef("a", 1),), resolved_dimensions=(),
        accepted_group_ids=("g_1",), depth_disposition=REFINED,
        refinement_reason="reason", validation_report_ref="vr_1",
        justification_fact_refs=("f_1",), chosen_order_id=None,
    )
    with pytest.raises(MalformedTemplateRecord) as excinfo:
        BranchTemplateBinding(**common, state=WORKFLOW_APPROVED,
                              approval_action_ref=None)
    assert "approval" in str(excinfo.value)
    draft = BranchTemplateBinding(**common, state=WORKFLOW_DRAFT,
                                  approval_action_ref=None)
    assert draft.state == WORKFLOW_DRAFT


def test_fragment_imports_resolve_as_an_acyclic_exact_version_graph():
    composed = TemplateFragment(
        fragment_id="course-work", fragment_version=1, roles=("term",),
        relative_order=(("term", "artifact_kind"),),
        imports=(FragmentRef("artifact-kind", 1), FragmentRef("subject-stage", 1)),
        optional_roles=(), metadata_only_roles=(), allowed_values={},
        privacy_floor="policy.public", provenance=("row:academic-01",),
    )
    catalogue = _catalogue(composed)
    resolved = resolve_fragment_imports(catalogue, FragmentRef("course-work", 1))
    assert [f.fragment_id for f in resolved] == [
        "artifact-kind", "subject-stage", "course-work",
    ]


def test_a_cyclic_import_is_a_reported_conflict_not_a_recursion_error():
    left = dataclasses.replace(ARTIFACT_KIND, imports=(FragmentRef("subject-stage", 1),))
    right = dataclasses.replace(SUBJECT_STAGE, imports=(FragmentRef("artifact-kind", 1),))
    manifest = {
        "release_id": "rel-1",
        "fragments": [dataclasses.asdict(left), dataclasses.asdict(right)],
        "definitions": [], "applicabilities": [],
    }
    catalogue = load_catalogue(lambda: json.dumps(manifest))
    with pytest.raises(CompositionConflict) as excinfo:
        resolve_fragment_imports(catalogue, FragmentRef("artifact-kind", 1))
    assert excinfo.value.gate == "C1"
    assert "artifact-kind" in " ".join(excinfo.value.conflicting)


def test_an_unresolvable_fragment_version_fails_closed_at_c1():
    catalogue = _catalogue()
    with pytest.raises(CompositionConflict) as excinfo:
        resolve_fragment_imports(catalogue, FragmentRef("artifact-kind", 2))
    assert excinfo.value.gate == "C1"


def test_allowed_values_merge_by_intersection_and_an_empty_result_is_a_conflict():
    left = dataclasses.replace(
        ARTIFACT_KIND, allowed_values={"artifact_kind": ["Homework", "Exam"]})
    right = dataclasses.replace(
        ARTIFACT_KIND, fragment_id="artifact-kind-narrow",
        allowed_values={"artifact_kind": ["Exam"]})
    merged = merge_fragment_constraints(
        (left, right), privacy_rank=lambda ref: 0)
    assert merged.allowed_values["artifact_kind"] == ("Exam",)

    disjoint = dataclasses.replace(
        ARTIFACT_KIND, fragment_id="artifact-kind-other",
        allowed_values={"artifact_kind": ["Photo"]})
    with pytest.raises(CompositionConflict) as excinfo:
        merge_fragment_constraints((left, disjoint), privacy_rank=lambda ref: 0)
    assert excinfo.value.gate == "C5"
    assert "omit one fragment" in " ".join(excinfo.value.choices)


def test_privacy_merges_to_the_strongest_included_restriction():
    strict = dataclasses.replace(ARTIFACT_KIND, privacy_floor="policy.sensitive")
    rank = {"policy.public": 0, "policy.sensitive": 1}.__getitem__
    merged = merge_fragment_constraints((ARTIFACT_KIND, strict), privacy_rank=rank)
    assert merged.privacy_floor == "policy.sensitive"


def test_an_unrankable_privacy_ref_refuses_rather_than_guessing():
    """G-KNOWLEDGE. A privacy ordering P10 invented would silently pick a weaker
    floor than an included fragment requires, which is C7's whole failure mode."""
    from tree_design.config import ConfigurationRequired

    def rank(ref):
        raise KeyError(ref)

    with pytest.raises(ConfigurationRequired):
        merge_fragment_constraints((ARTIFACT_KIND,), privacy_rank=rank)


def test_the_catalogue_round_trips_all_four_records():
    """DM1. The manifest is the compiler's only output shape, so a record that
    cannot survive `asdict` -> JSON -> load is a record the library cannot ship."""
    definition = TemplateDefinition(
        template_id="academic-coursework", template_version=1,
        origin_kind=BUILT_IN, scope_kind=DOMAIN_FOCUSED,
        publication_state=PUBLISHED,
        fragment_refs=(FragmentRef("artifact-kind", 1),),
        candidate_orders=(SUBJECT_FIRST, KIND_FIRST),
        optional_branch_patterns=(), sensitivity_policy_ref="policy.public",
        validation_constraints=(),
        example_label_chains=(("Academics", "PHYS1401"),),
    )
    row = TemplateApplicability(
        applicability_id="academic-coursework--academic", applicability_version=1,
        template_id="academic-coursework", template_version=1,
        uses_schema="academic",
        purpose_profile_ref=PurposeProfileRef("pp.coursework", 1),
        allowed_fields=("subject", "work_type"), detection_signal_refs=("signal.x",),
        role_bindings=(RoleBinding("subject", "subject"),
                       RoleBinding("artifact_kind", "work_type")),
        exclusions=(), provenance=("row:academic-01",),
    )
    manifest = {
        "release_id": "rel-1",
        "fragments": [dataclasses.asdict(ARTIFACT_KIND)],
        "definitions": [dataclasses.asdict(definition)],
        "applicabilities": [dataclasses.asdict(row)],
    }
    catalogue = load_catalogue(lambda: json.dumps(manifest))
    assert catalogue.release_id == "rel-1"
    assert catalogue.fragment(FragmentRef("artifact-kind", 1)) == ARTIFACT_KIND
    loaded = catalogue.definitions[("academic-coursework", 1)]
    assert loaded == definition
    assert loaded.default_order.order_id == "subject-first"
    assert catalogue.applicability(
        ApplicabilityRef("academic-coursework--academic", 1)) == row
    assert catalogue.rows_for_schema("academic") == (row,)
    assert catalogue.rows_for_schema("photos") == ()


def test_the_catalogue_loads_through_an_injected_reader_and_scans_nothing():
    import ast
    from pathlib import Path

    source = (Path(__file__).resolve().parents[2]
              / "src" / "tree_design" / "catalogue.py").read_text()
    imported = {
        node.module for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert not any(name.startswith("planning") for name in imported)
    assert "pathlib" not in imported and "glob" not in imported


def test_an_empty_release_is_configuration_required_not_an_empty_catalogue():
    from tree_design.config import ConfigurationRequired

    with pytest.raises(ConfigurationRequired):
        load_catalogue(lambda: json.dumps(
            {"fragments": [], "definitions": [], "applicabilities": []}))
    with pytest.raises(ConfigurationRequired):
        load_catalogue(None)


# --- the reader of the order the user actually took ------------------------------


def _definition(*orders):
    return TemplateDefinition(
        template_id="academic-coursework", template_version=1,
        origin_kind=BUILT_IN, scope_kind=DOMAIN_FOCUSED,
        publication_state=PUBLISHED, fragment_refs=(),
        candidate_orders=orders, optional_branch_patterns=(),
        sensitivity_policy_ref="policy.public", validation_constraints=(),
        example_label_chains=(),
    )


def _binding(*, chosen_order_id, resolved_dimensions=()):
    return BranchTemplateBinding(
        binding_id="btb_1", plan_version_id="plan_1", branch_node_id="n_1",
        applicability_refs=(ApplicabilityRef("a", 1),),
        resolved_dimensions=resolved_dimensions, accepted_group_ids=("g_1",),
        state=WORKFLOW_DRAFT, depth_disposition=REFINED,
        refinement_reason="reason", validation_report_ref="vr_1",
        approval_action_ref=None, justification_fact_refs=("f_1",),
        chosen_order_id=chosen_order_id,
    )


def test_the_order_a_branch_nests_by_is_the_one_the_user_took(): 
    """§5.3, §5.8 and the owner ruling. `chosen_order_id` has to have a READER,
    or the field records a decision nothing acts on.

    The recipe RECOMMENDS subject-first. This branch took kind-first. Every
    downstream reader — the §5.9 warnings above all — must see kind-first, because
    a warning computed against the recommendation describes a tree the user never
    asked for.
    """
    definition = _definition(SUBJECT_FIRST, KIND_FIRST)
    assert definition.default_order.order_id == "subject-first"
    roles = branch_dimension_roles(_binding(chosen_order_id="kind-first"), definition)
    assert roles == ("artifact_kind", "subject")
    # And the recommendation is NOT what came back.
    assert roles != tuple(d.role_ref for d in definition.dimensions)


def test_a_hand_composed_order_is_read_off_the_binding_not_off_the_recipe():
    """`chosen_order_id is None` means the user composed an order of their own.
    Falling back to the recipe's default there would substitute a recommendation
    for a decision — the same defect as reading the default outright."""
    definition = _definition(SUBJECT_FIRST, KIND_FIRST)
    binding = _binding(
        chosen_order_id=None,
        resolved_dimensions=(
            ResolvedDimension(role_ref="subject", field_ref="subject",
                              action=ACTION_SELECTED, order_index=1,
                              display_label=None, scope=SCOPE_SCHEMA_FIELD),
            ResolvedDimension(role_ref="artifact_kind", field_ref="artifact_kind",
                              action=ACTION_SELECTED, order_index=0,
                              display_label=None, scope=SCOPE_SCHEMA_FIELD),
        ),
    )
    assert branch_dimension_roles(binding, definition) == ("artifact_kind", "subject")


def test_a_binding_naming_an_order_the_recipe_does_not_offer_is_refused():
    """Not silently fallen back to the default. A binding pointing at a retired
    or misspelled order is a branch whose ordering nobody can reconstruct, and
    answering it with the recommendation would hide that."""
    definition = _definition(SUBJECT_FIRST, KIND_FIRST)
    with pytest.raises(MalformedTemplateRecord) as excinfo:
        branch_dimension_roles(_binding(chosen_order_id="term-first"), definition)
    assert "term-first" in str(excinfo.value)


def test_a_hand_composed_binding_with_no_resolved_dimensions_is_refused():
    """`None` plus an empty composition says the user chose their own order and
    then chose nothing. Returning `()` would let a caller read "this branch nests
    by nothing" as a fact rather than as the missing record it is."""
    with pytest.raises(MalformedTemplateRecord):
        branch_dimension_roles(_binding(chosen_order_id=None),
                               _definition(SUBJECT_FIRST, KIND_FIRST))
