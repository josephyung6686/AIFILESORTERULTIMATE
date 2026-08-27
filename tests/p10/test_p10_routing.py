"""P10 Task 7 — the eight composition gates, one falsifying fixture each.

Domain is one applicability signal, never a one-template ownership key. One
definition may serve two domains through two independent one-schema rows; one
domain may offer two structurally different recipes; a purpose packet may
combine compatible fragments across domains without unioning anyone's fact
allow-list. Every one of those is a test below, because each is a failure case
the design names explicitly.

AMENDMENT (owner ruling): the eight gates do NOT share one consequence. Six
REFUSE and cannot be overridden — a missing artefact, a minted field, evidence
that does not support the recipe, silently dropped material, a weakened privacy
floor, a self-activating template. Two WARN and are resolved by the user saying
which of the offered options they want: C4's ambiguous role mapping and C5's
disagreeing partial orders. Making them uniform is wrong in both directions, so
the split is tested from both sides.
"""
from __future__ import annotations

import dataclasses
import json

import pytest

from tree_design.catalogue import load_catalogue
from tree_design.config import tree_limits
from tree_design.routing import (
    BranchContext,
    CompositionOverride,
    eligible_rows,
    evaluate_composition,
    route_branch,
)
from tree_design.templates import (
    CompositionConflict,
    DimensionOrder,
    FragmentRef,
    PurposeProfileRef,
    RoleBinding,
    TemplateApplicability,
    TemplateDefinition,
    TemplateDimension,
    TemplateFragment,
)
from tree_design.upstream import AcceptedGroup, GroupMember
from tree_design.vocabulary import (
    BUILT_IN,
    COMPOSITION_GATES,
    CROSS_DOMAIN,
    GATE_REFUSE,
    GATE_WARN,
    NON_OVERRIDABLE_GATES,
    OVERRIDABLE_GATES,
    PUBLISHED,
    REQUIRED,
)

RANK = {"policy.public": 0, "policy.sensitive": 1}.__getitem__
ALWAYS = lambda profile, groups: True
NEVER = lambda profile, groups: False
FIRST = lambda candidates: candidates


def _fragment(fragment_id, roles, order=(), floor="policy.public", imports=(),
              values=None):
    return TemplateFragment(
        fragment_id=fragment_id, fragment_version=1, roles=tuple(roles),
        relative_order=tuple(order), imports=tuple(imports), optional_roles=(),
        metadata_only_roles=(), allowed_values=values or {}, privacy_floor=floor,
        provenance=("row:fixture",),
    )


def _orders(roles):
    """Candidate orders for a fixture recipe: the recommended nesting and, when
    there is more than one dimension, its reverse. §5.3 and §5.8 make the choice
    the end user's, so a fixture with two dimensions has to offer two."""
    roles = tuple(roles)
    forward = DimensionOrder(
        order_id="forward", is_default=True,
        rationale="The recommended nesting for this fixture.",
        dimensions=tuple(
            TemplateDimension(role, index, REQUIRED, False, "fixture rationale")
            for index, role in enumerate(roles)),
    )
    if len(roles) == 1:
        return (forward,)
    reverse = DimensionOrder(
        order_id="reverse", is_default=False,
        rationale="The alternative nesting, for the other retrieval habit.",
        dimensions=tuple(
            TemplateDimension(role, index, REQUIRED, False, "fixture rationale")
            for index, role in enumerate(reversed(roles))),
    )
    return (forward, reverse)


def _definition(template_id, fragment_refs, roles, scope=CROSS_DOMAIN):
    return TemplateDefinition(
        template_id=template_id, template_version=1, origin_kind=BUILT_IN,
        scope_kind=scope, publication_state=PUBLISHED,
        fragment_refs=tuple(fragment_refs), candidate_orders=_orders(roles),
        optional_branch_patterns=(), sensitivity_policy_ref="policy.public",
        validation_constraints=(), example_label_chains=(),
    )


def _row(applicability_id, template_id, schema, bindings, profile=None):
    return TemplateApplicability(
        applicability_id=applicability_id, applicability_version=1,
        template_id=template_id, template_version=1, uses_schema=schema,
        purpose_profile_ref=profile,
        allowed_fields=tuple(field for _, field in bindings),
        detection_signal_refs=("signal.fixture",),
        role_bindings=tuple(RoleBinding(role, field) for role, field in bindings),
        exclusions=(), provenance=("row:fixture",),
    )


def _catalogue(fragments, definitions, rows):
    manifest = {
        "release_id": "rel-1",
        "fragments": [dataclasses.asdict(f) for f in fragments],
        "definitions": [dataclasses.asdict(d) for d in definitions],
        "applicabilities": [dataclasses.asdict(r) for r in rows],
    }
    return load_catalogue(lambda: json.dumps(manifest))


def _group(group_id, domain, files):
    return AcceptedGroup(
        group_id=group_id, label=group_id, domain=domain,
        members=tuple(GroupMember(f, f"h_{f}", "direct-anchor") for f in files),
        anchor_facts=(f"fact_{group_id}",), excluded_members=(),
    )


def _context(domains, groups, classes=frozenset({"personal_non_sensitive"}),
             profiles=()):
    files = frozenset(m.file_id for g in groups for m in g.members)
    return BranchContext(
        branch_node_id="n_branch", domains=tuple(domains),
        accepted_groups=tuple(groups), member_file_ids=files,
        handling_classes=classes, purpose_profile_refs=tuple(profiles),
    )


SUBJECT = _fragment("subject", ("subject",))
KIND = _fragment("artifact-kind", ("artifact_kind",))
COURSEWORK = _definition(
    "coursework", (FragmentRef("subject", 1), FragmentRef("artifact-kind", 1)),
    ("subject", "artifact_kind"))


# --- one falsifying fixture per gate --------------------------------------------


def test_c1_an_unresolvable_version_creates_no_node(conn):
    catalogue = _catalogue((SUBJECT,), (COURSEWORK,), (
        _row("a1", "coursework", "academic",
             (("subject", "subject"), ("artifact_kind", "work_type"))),
    ))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    with pytest.raises(CompositionConflict) as excinfo:
        evaluate_composition(
            conn, catalogue, context, catalogue.rows_for_schema("academic"),
            privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
    assert excinfo.value.gate == "C1"
    assert "artifact-kind@1" in " ".join(excinfo.value.conflicting)


def test_c2_a_role_that_maps_to_no_live_p6_field_fails_closed(conn):
    catalogue = _catalogue((SUBJECT, KIND), (COURSEWORK,), (
        _row("a1", "coursework", "academic",
             (("subject", "subject"), ("artifact_kind", "not_a_field"))),
    ))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    with pytest.raises(CompositionConflict) as excinfo:
        evaluate_composition(
            conn, catalogue, context, catalogue.rows_for_schema("academic"),
            privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
    assert excinfo.value.gate == "C2"


def test_c2_is_exercised_against_a_seeded_field_catalogue(conn):
    """If `conftest` stopped seeding `create_fields`, EVERY role would fail C2
    and the test above would pass while proving nothing."""
    from tree_design.upstream import resolve_role_to_field

    assert resolve_role_to_field(conn, role_ref="subject", field_ref="subject") \
        == "subject"


def test_c3_a_domain_label_alone_does_not_satisfy_a_purpose_binding(conn):
    profile = PurposeProfileRef("pp.grad-application", 1)
    catalogue = _catalogue(
        (SUBJECT,),
        (_definition("apps", (FragmentRef("subject", 1),), ("subject",)),),
        (_row("a1", "apps", "academic", (("subject", "subject"),), profile=profile),))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    with pytest.raises(CompositionConflict) as excinfo:
        evaluate_composition(
            conn, catalogue, context, catalogue.rows_for_schema("academic"),
            privacy_rank=RANK, satisfies_purpose_profile=NEVER)
    assert excinfo.value.gate == "C3"
    assert "pp.grad-application" in " ".join(excinfo.value.conflicting)


def test_c4_two_rows_binding_one_role_to_two_fields_is_surfaced_not_picked(conn):
    catalogue = _catalogue(
        (SUBJECT,),
        (_definition("t", (FragmentRef("subject", 1),), ("subject",)),),
        (_row("a1", "t", "academic", (("subject", "subject"),)),
         _row("a2", "t", "academic", (("subject", "term"),))))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    with pytest.raises(CompositionConflict) as excinfo:
        evaluate_composition(
            conn, catalogue, context, catalogue.rows_for_schema("academic"),
            privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
    assert excinfo.value.gate == "C4"
    assert "subject" in " ".join(excinfo.value.conflicting)


def test_c5_two_fragments_with_opposite_order_are_a_cycle(conn):
    left = _fragment("l", ("subject", "artifact_kind"), (("subject", "artifact_kind"),))
    right = _fragment("r", ("subject", "artifact_kind"), (("artifact_kind", "subject"),))
    definition = _definition("t", (FragmentRef("l", 1), FragmentRef("r", 1)),
                             ("subject", "artifact_kind"))
    catalogue = _catalogue((left, right), (definition,), (
        _row("a1", "t", "academic",
             (("subject", "subject"), ("artifact_kind", "work_type"))),
    ))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    with pytest.raises(CompositionConflict) as excinfo:
        evaluate_composition(
            conn, catalogue, context, catalogue.rows_for_schema("academic"),
            privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
    assert excinfo.value.gate == "C5"


def test_c6_a_composition_that_would_drop_a_member_is_refused(conn):
    """"Hiding dropped or unresolved files in a 'successful' preview" is a
    failure case the design names outright."""
    catalogue = _catalogue(
        (SUBJECT,),
        (_definition("t", (FragmentRef("subject", 1),), ("subject",)),),
        (_row("a1", "t", "academic", (("subject", "subject"),)),))
    academic = _group("g1", "academic", ("f1",))
    photos = _group("g2", "photos", ("f2",))
    context = _context(("academic", "photos"), (academic, photos))
    with pytest.raises(CompositionConflict) as excinfo:
        evaluate_composition(
            conn, catalogue, context, catalogue.rows_for_schema("academic"),
            privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
    assert excinfo.value.gate == "C6"
    assert "f2" in " ".join(excinfo.value.conflicting)


def test_c7_the_combined_floor_is_never_weaker_than_an_included_one(conn):
    strict = _fragment("strict", ("artifact_kind",), floor="policy.sensitive")
    definition = _definition("t", (FragmentRef("subject", 1), FragmentRef("strict", 1)),
                             ("subject", "artifact_kind"))
    catalogue = _catalogue((SUBJECT, strict), (definition,), (
        _row("a1", "t", "academic",
             (("subject", "subject"), ("artifact_kind", "work_type"))),
    ))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    candidate = evaluate_composition(
        conn, catalogue, context, catalogue.rows_for_schema("academic"),
        privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
    assert candidate.privacy_floor == "policy.sensitive"
    assert "C7" in candidate.gates_passed


def test_c8_a_passing_candidate_creates_no_node(conn):
    catalogue = _catalogue((SUBJECT, KIND), (COURSEWORK,), (
        _row("a1", "coursework", "academic",
             (("subject", "subject"), ("artifact_kind", "work_type"))),
    ))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    candidate = evaluate_composition(
        conn, catalogue, context, catalogue.rows_for_schema("academic"),
        privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
    assert candidate.gates_passed == ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8")
    assert not hasattr(candidate, "nodes")
    assert conn.execute(
        "SELECT count(*) AS n FROM sqlite_master WHERE name = 'tree_nodes'"
    ).fetchone()["n"] in (0, 1)


# --- the consequence split (owner ruling) ---------------------------------------


def test_every_gate_carries_exactly_one_consequence_and_the_two_partition_it():
    from tree_design import vocabulary as v

    assert set(v.COMPOSITION_GATE_CONSEQUENCE) == set(COMPOSITION_GATES)
    assert set(NON_OVERRIDABLE_GATES) | set(OVERRIDABLE_GATES) == set(COMPOSITION_GATES)
    assert not set(NON_OVERRIDABLE_GATES) & set(OVERRIDABLE_GATES)
    assert set(OVERRIDABLE_GATES) == {"C4", "C5"}
    assert v.COMPOSITION_GATE_CONSEQUENCE["C7"] == GATE_REFUSE
    assert v.COMPOSITION_GATE_CONSEQUENCE["C4"] == GATE_WARN


def test_a_privacy_or_safety_gate_cannot_be_overridden_at_all():
    """Not "is refused when overridden" — CANNOT BE CONSTRUCTED. An override for
    C7 that exists anywhere in the codebase is a click away from being honoured,
    so the record refuses to hold one."""
    for gate in NON_OVERRIDABLE_GATES:
        with pytest.raises(CompositionConflict) as excinfo:
            CompositionOverride(gate=gate, approved_by="ra_1")
        assert excinfo.value.gate == gate
        assert not excinfo.value.overridable


def test_an_override_names_the_recorded_user_action_that_authorised_it():
    with pytest.raises(CompositionConflict):
        CompositionOverride(gate="C4", approved_by="")


def test_c4_is_resolved_by_the_user_choosing_which_field(conn):
    """The WARN half. C4 refuses to PICK; it does not refuse to proceed once the
    person who knows has said which field they meant."""
    catalogue = _catalogue(
        (SUBJECT,),
        (_definition("t", (FragmentRef("subject", 1),), ("subject",)),),
        (_row("a1", "t", "academic", (("subject", "subject"),)),
         _row("a2", "t", "academic", (("subject", "term"),))))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    override = CompositionOverride(
        gate="C4", approved_by="ra_1", role_choices={"subject": "term"})
    candidate = evaluate_composition(
        conn, catalogue, context, catalogue.rows_for_schema("academic"),
        privacy_rank=RANK, satisfies_purpose_profile=ALWAYS,
        overrides=(override,))
    assert candidate.overridden_gates == ("C4",)
    assert {d.role_ref: d.field_ref for d in candidate.resolved_dimensions} == {
        "subject": "term"}


def test_a_c4_override_may_not_choose_a_field_no_row_offered(conn):
    """An override resolves an ambiguity the rows created. It is not a second
    door into binding a role to a field no applicability row allows — that would
    be C2's refusal reached through C4's warning."""
    catalogue = _catalogue(
        (SUBJECT,),
        (_definition("t", (FragmentRef("subject", 1),), ("subject",)),),
        (_row("a1", "t", "academic", (("subject", "subject"),)),
         _row("a2", "t", "academic", (("subject", "term"),))))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    override = CompositionOverride(
        gate="C4", approved_by="ra_1", role_choices={"subject": "school"})
    with pytest.raises(CompositionConflict) as excinfo:
        evaluate_composition(
            conn, catalogue, context, catalogue.rows_for_schema("academic"),
            privacy_rank=RANK, satisfies_purpose_profile=ALWAYS,
            overrides=(override,))
    assert excinfo.value.gate == "C4"


def test_c5s_order_cycle_is_resolved_by_the_user_choosing_an_order(conn):
    left = _fragment("l", ("subject", "artifact_kind"), (("subject", "artifact_kind"),))
    right = _fragment("r", ("subject", "artifact_kind"), (("artifact_kind", "subject"),))
    definition = _definition("t", (FragmentRef("l", 1), FragmentRef("r", 1)),
                             ("subject", "artifact_kind"))
    catalogue = _catalogue((left, right), (definition,), (
        _row("a1", "t", "academic",
             (("subject", "subject"), ("artifact_kind", "work_type"))),
    ))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    override = CompositionOverride(
        gate="C5", approved_by="ra_1", role_order=("artifact_kind", "subject"))
    candidate = evaluate_composition(
        conn, catalogue, context, catalogue.rows_for_schema("academic"),
        privacy_rank=RANK, satisfies_purpose_profile=ALWAYS,
        overrides=(override,))
    assert candidate.overridden_gates == ("C5",)
    assert [d.role_ref for d in candidate.resolved_dimensions] == [
        "artifact_kind", "subject"]


def test_c5s_empty_value_intersection_is_not_rescued_by_an_order(conn):
    """The two C5 failures are not one thing. No ordering the user picks can make
    two disjoint allowed-value sets agree, so that half stays a refusal even
    though the gate is WARN-class."""
    left = _fragment("l", ("artifact_kind",), values={"artifact_kind": ["Exam"]})
    right = _fragment("r", ("artifact_kind",), values={"artifact_kind": ["Photo"]})
    definition = _definition("t", (FragmentRef("l", 1), FragmentRef("r", 1)),
                             ("artifact_kind",))
    catalogue = _catalogue((left, right), (definition,), (
        _row("a1", "t", "academic", (("artifact_kind", "work_type"),)),
    ))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    override = CompositionOverride(
        gate="C5", approved_by="ra_1", role_order=("artifact_kind",))
    with pytest.raises(CompositionConflict) as excinfo:
        evaluate_composition(
            conn, catalogue, context, catalogue.rows_for_schema("academic"),
            privacy_rank=RANK, satisfies_purpose_profile=ALWAYS,
            overrides=(override,))
    assert excinfo.value.gate == "C5"
    assert "intersect to nothing" in str(excinfo.value)


def test_the_report_separates_refusals_from_choices_the_user_may_resolve(conn):
    catalogue = _catalogue(
        (SUBJECT,),
        (_definition("t", (FragmentRef("subject", 1),), ("subject",)),),
        (_row("a1", "t", "academic", (("subject", "subject"),)),
         _row("a2", "t", "academic", (("subject", "term"),))))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    report = route_branch(
        conn, catalogue, context, limits=None, privacy_rank=RANK,
        satisfies_purpose_profile=ALWAYS, rank_candidates=FIRST)
    assert report.candidates == ()
    assert [c.gate for c in report.resolvable] == ["C4"]
    assert report.refusals == ()


# --- the many-to-many seam ------------------------------------------------------


def test_one_definition_serves_two_domains_without_duplication(conn):
    catalogue = _catalogue((SUBJECT, KIND), (COURSEWORK,), (
        _row("a-academic", "coursework", "academic",
             (("subject", "subject"), ("artifact_kind", "work_type"))),
        _row("a-research", "coursework", "research",
             (("subject", "subject"), ("artifact_kind", "artifact_type"))),
    ))
    assert len(catalogue.definitions) == 1
    for schema, expected in (("academic", "work_type"), ("research", "artifact_type")):
        context = _context((schema,), (_group("g", schema, ("f1",)),))
        candidate = evaluate_composition(
            conn, catalogue, context, catalogue.rows_for_schema(schema),
            privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
        resolved = {d.role_ref: d.field_ref for d in candidate.resolved_dimensions}
        assert resolved["artifact_kind"] == expected


def test_one_domain_offers_two_structurally_different_recipes(conn):
    flat = _definition("flat", (FragmentRef("subject", 1),), ("subject",))
    catalogue = _catalogue((SUBJECT, KIND), (COURSEWORK, flat), (
        _row("a-deep", "coursework", "academic",
             (("subject", "subject"), ("artifact_kind", "work_type"))),
        _row("a-flat", "flat", "academic", (("subject", "subject"),)),
    ))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    rows = eligible_rows(catalogue, context)
    assert {row.template_id for row in rows} == {"coursework", "flat"}


def test_a_mixed_domain_purpose_packet_keeps_every_member_and_both_schemas(conn):
    profile = PurposeProfileRef("pp.grad-application", 1)
    counterpart = _fragment("counterpart", ("counterpart",))
    definition = _definition("packet", (FragmentRef("counterpart", 1),),
                             ("counterpart",))
    catalogue = _catalogue((counterpart,), (definition,), (
        _row("a-apps", "packet", "college_applications",
             (("counterpart", "target_school"),), profile=profile),
        _row("a-academic", "packet", "academic",
             (("counterpart", "subject"),), profile=profile),
    ))
    apps = _group("g_apps", "college_applications", ("transcript",))
    academic = _group("g_academic", "academic", ("recommendation",))
    context = _context(("college_applications", "academic"), (apps, academic),
                       profiles=(profile,))
    rows = catalogue.rows_for_schema("college_applications") + \
        catalogue.rows_for_schema("academic")
    override = CompositionOverride(
        gate="C4", approved_by="ra_1", role_choices={"counterpart": "target_school"})
    candidate = evaluate_composition(
        conn, catalogue, context, rows,
        privacy_rank=RANK, satisfies_purpose_profile=ALWAYS,
        overrides=(override,))
    assert candidate.covered_file_ids == {"transcript", "recommendation"}
    # Two rows, two schemas, no union: each row still allows only its own fields.
    assert len(candidate.applicability_refs) == 2
    allowed = [set(catalogue.applicability(ref).allowed_fields)
               for ref in candidate.applicability_refs]
    assert allowed[0] != allowed[1]


def test_the_router_returns_a_bounded_ranked_set_not_every_match(conn):
    """The composable-template design: "The router returns a small explained
    candidate set, not every superficially matching template. Candidate ceilings
    and ranking weights remain injected configuration."
    """
    from database_agent.budget import set_ceiling

    set_ceiling(conn, "tree.max_folder_proposals_and_depth", 1)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    limits = tree_limits(
        conn, excessive_depth_warning=6, tiny_folder_max_files=3,
        tiny_folder_count_warning=12,
        materially_improves_retrieval=lambda preview: None)
    flat = _definition("flat", (FragmentRef("subject", 1),), ("subject",))
    catalogue = _catalogue((SUBJECT, KIND), (COURSEWORK, flat), (
        _row("a-deep", "coursework", "academic",
             (("subject", "subject"), ("artifact_kind", "work_type"))),
        _row("a-flat", "flat", "academic", (("subject", "subject"),)),
    ))
    context = _context(("academic",), (_group("g1", "academic", ("f1",)),))
    report = route_branch(
        conn, catalogue, context, limits=limits, privacy_rank=RANK,
        satisfies_purpose_profile=ALWAYS, rank_candidates=FIRST)
    assert len(report.candidates) == 1
    assert report.deferred == 1


def test_a_missing_binding_produces_a_conflict_not_a_generic_fallback(conn):
    catalogue = _catalogue((SUBJECT,), (COURSEWORK,), ())
    context = _context(("finance",), (_group("g1", "finance", ("f1",)),))
    report = route_branch(
        conn, catalogue, context,
        limits=None, privacy_rank=RANK, satisfies_purpose_profile=ALWAYS,
        rank_candidates=FIRST)
    assert report.candidates == ()
    assert report.conflicts
    assert report.conflicts[0].gate == "C3"
    assert report.refusals == report.conflicts
