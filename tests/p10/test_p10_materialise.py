"""P10 Task 12 — §5.4's populate step, and the counts §5.5 shows before committing.

The rule that makes this correct is that a child value is nested under a parent
value only when the SAME files carry both. A cartesian product of three schools
by five terms by twelve courses would be 180 branches, and §5.5 says the
interface states "three schools, five terms, and twelve course branches". Twelve
is the number of (school, term, course) combinations the evidence actually
contains. Every count here is an intersection, never a product.
"""
from __future__ import annotations

import pytest

from tree_design.config import ConfigurationRequired
from tree_design.materialise import (
    BranchEvidence,
    LevelEvidence,
    MaterialisationRefused,
    child_counts,
    materialise_branch,
    project_branch_nodes,
)
from tree_design.records import ExpectedValue, Node
from tree_design.routing import CompositionCandidate, ResolvedDimension
from tree_design.upstream import UpstreamUnavailable
from tree_design.validation import CheckFailure, ValidationReport
from tree_design.vocabulary import (
    ACTION_SELECTED,
    ORDINARY,
    PROPOSED,
    SCOPE_SCHEMA_FIELD,
    SCOPE_TEMPLATE_LOCAL,
)

@pytest.fixture()
def seeded(conn, tmp_path) -> "SeededCorpus":
    """P10's `conn` plus §5.5's three files as real P1/P4/P6 rows.

    `create_evidence_schema` is P4's and is not in `tests/p10/conftest.py` because
    Task 12 is the only suite that needs an observation: every other P10 test
    reads facts through a fixture or not at all.
    """
    from evidence_shape.schema import create_evidence_schema

    from p10.p6_fixtures import seed_academics

    create_evidence_schema(conn)
    return seed_academics(conn, tmp_path)


ACCEPTED = ValidationReport(report_id="vr_1", passed=("V1",), failures=())
REFUSED = ValidationReport(
    report_id="vr_2", passed=(),
    failures=(CheckFailure(check="V3", reason="too deep", affected=("subject",)),))


def _ids():
    counter = iter(range(1000))
    return lambda: f"n_{next(counter)}"


def _parent():
    return Node(
        node_id="n_academics", plan_version_id="plan_1", node_type=PROPOSED,
        display_label="Academics", parent_node_id=None, root_anchor="root_documents",
        ordinal=0, associated_group_ids=("g_phys1401",),
        explanation="The accepted PHYS 1401 course-material group produced this area.",
        node_role=ORDINARY, accepts_placement=True,
        handling_class="personal_non_sensitive", origin_node_id="n_academics")


def _candidate(*pairs):
    """A routed candidate. A `field` of None makes that level template-local —
    the Contract W5 pairing, so one helper covers both tiers and materialisation
    never needs a second entry point for the novel-domain path."""
    return CompositionCandidate(
        applicability_refs=(), privacy_floor="policy.public",
        covered_file_ids=frozenset(), gates_passed=("C1",),
        overridden_gates=(),
        explanation="The academic coursework recipe matched this branch.",
        resolved_dimensions=tuple(
            ResolvedDimension(
                role_ref=role, field_ref=field, action=ACTION_SELECTED,
                order_index=index, display_label=None,
                scope=SCOPE_SCHEMA_FIELD if field else SCOPE_TEMPLATE_LOCAL)
            for index, (role, field) in enumerate(pairs)))


ALWAYS_ORDINARY = lambda classes: "personal_non_sensitive"
NO_CONTEXT = lambda field_ref, order_index: None
ONE_CLASS = lambda member: "personal_non_sensitive"


def test_the_levels_carry_p6s_real_values_and_p10_composes_none(seeded):
    conn = seeded.conn
    materialised, evidence = materialise_branch(
        conn, _candidate(("school", "school"), ("subject", "subject")),
        branch_node_id="n_academics",
        members=seeded.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS)
    assert [lvl.field_ref for lvl in evidence.levels] == ["school", "subject"]
    assert evidence.levels[0].values == ("Columbia",)
    assert evidence.levels[1].values == ("BUSIB 4300", "PHYS1401")
    # Not one invented name. Every string came out of P6's `values` table.
    assert materialised.levels[1].members_by_value == {"BUSIB 4300": 2, "PHYS1401": 1}


def test_a_file_with_no_settled_value_is_unresolved_and_gets_no_branch(seeded):
    conn = seeded.conn
    _, evidence = materialise_branch(
        conn, _candidate(("work_type", "work_type")),
        branch_node_id="n_academics", members=seeded.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS)
    # `lab` carries no work_type. §5.11: a tree "can be accepted even if some files
    # remain unresolved"; the alternative is inventing a work type for it.
    assert evidence.unresolved_by_field["work_type"] == frozenset({seeded.file_id("lab")})
    assert set(evidence.levels[0].values) == {"Syllabus", "Homework"}


def test_two_simultaneous_values_leave_the_file_unresolved_never_assigned(seeded):
    """P6's OQ6 (multiplicity) is open. `preferred_fact` returns `None` rather than
    choosing, and P10 must not choose either — picking one here would close an open
    P6 question inside a P10 module."""
    conn = seeded.conn
    seeded.add("lab", "work_type", "Lab Report")
    seeded.add("lab", "work_type", "Lab Notes")
    _, evidence = materialise_branch(
        conn, _candidate(("work_type", "work_type")),
        branch_node_id="n_academics", members=seeded.members("lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS)
    assert evidence.levels[0].values == ()
    assert evidence.unresolved_by_field["work_type"] == frozenset({seeded.file_id("lab")})


def test_child_counts_are_intersections_not_a_cartesian_product(seeded):
    """§5.5's promise: "The user sees the actual branch counts before committing."
    One school and two courses is three branches, not two."""
    conn = seeded.conn
    _, evidence = materialise_branch(
        conn, _candidate(("school", "school"), ("subject", "subject")),
        branch_node_id="n_academics", members=seeded.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS)
    assert child_counts(evidence) == {"school": 1, "subject": 2}


def test_the_projection_nests_by_shared_files_and_never_multiplies(seeded):
    conn = seeded.conn
    _, evidence = materialise_branch(
        conn, _candidate(("school", "school"), ("subject", "subject"),
                         ("work_type", "work_type")),
        branch_node_id="n_academics", members=seeded.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS)
    nodes = project_branch_nodes(
        evidence, ACCEPTED, parent=_parent(), plan_version_id="plan_1",
        mint_node_id=_ids(), handling_class_for=ALWAYS_ORDINARY,
        template_context_for=NO_CONTEXT)
    by_label = {n.display_label: n for n in nodes}
    assert set(by_label) == {"Columbia", "BUSIB 4300", "PHYS1401",
                             "Syllabus", "Homework"}
    # PHYS1401's only file has no work_type, so PHYS1401 gets no children at all.
    assert [n.display_label for n in nodes
            if n.parent_node_id == by_label["PHYS1401"].node_id] == []
    # Syllabus and Homework hang under BUSIB 4300, not under Columbia.
    assert by_label["Syllabus"].parent_node_id == by_label["BUSIB 4300"].node_id
    assert by_label["Homework"].parent_node_id == by_label["BUSIB 4300"].node_id


def test_every_node_carries_the_ancestor_chain_as_expected_values(seeded):
    conn = seeded.conn
    _, evidence = materialise_branch(
        conn, _candidate(("school", "school"), ("subject", "subject"),
                         ("work_type", "work_type")),
        branch_node_id="n_academics", members=seeded.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS)
    nodes = project_branch_nodes(
        evidence, ACCEPTED, parent=_parent(), plan_version_id="plan_1",
        mint_node_id=_ids(), handling_class_for=ALWAYS_ORDINARY,
        template_context_for=NO_CONTEXT)
    homework = next(n for n in nodes if n.display_label == "Homework")
    assert homework.expected_values == (
        ExpectedValue(field="school", value="Columbia"),
        ExpectedValue(field="subject", value="BUSIB 4300"),
        ExpectedValue(field="work_type", value="Homework"),
    )
    # §6.1's worked example is exactly this shape: the Homework node's expected
    # values are the whole chain, not its own level alone.


def test_every_node_explains_itself_from_counted_evidence_and_shows_no_score(seeded):
    conn = seeded.conn
    _, evidence = materialise_branch(
        conn, _candidate(("subject", "subject")),
        branch_node_id="n_academics", members=seeded.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS)
    nodes = project_branch_nodes(
        evidence, ACCEPTED, parent=_parent(), plan_version_id="plan_1",
        mint_node_id=_ids(), handling_class_for=ALWAYS_ORDINARY,
        template_context_for=NO_CONTEXT)
    for node in nodes:
        assert node.explanation.strip()
        assert not any(token in node.explanation.lower()
                       for token in ("confidence", "score", "probability", "%"))
    busib = next(n for n in nodes if n.display_label == "BUSIB 4300")
    assert "subject" in busib.explanation and "BUSIB 4300" in busib.explanation


def test_a_metadata_only_dimension_produces_no_node(seeded):
    conn = seeded.conn
    candidate = _candidate(("subject", "subject"), ("work_type", "work_type"))
    _, evidence = materialise_branch(
        conn, candidate, branch_node_id="n_academics",
        members=seeded.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        metadata_only_roles=frozenset({"work_type"}))
    nodes = project_branch_nodes(
        evidence, ACCEPTED, parent=_parent(), plan_version_id="plan_1",
        mint_node_id=_ids(), handling_class_for=ALWAYS_ORDINARY,
        template_context_for=NO_CONTEXT)
    assert {n.display_label for n in nodes} == {"BUSIB 4300", "PHYS1401"}
    # The dimension is still measured — §5.4 calls these "metadata only", not absent.
    assert evidence.levels[1].metadata_only is True
    assert evidence.levels[1].values == ("Homework", "Syllabus")


def test_a_refused_validation_report_produces_no_node(seeded):
    """§5.7 gates the build, not just the preview. A V-check that fails and still
    leaves nodes in the tree is a check with no consequence."""
    conn = seeded.conn
    _, evidence = materialise_branch(
        conn, _candidate(("subject", "subject")), branch_node_id="n_academics",
        members=seeded.members("syllabus"), ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS)
    with pytest.raises(MaterialisationRefused) as excinfo:
        project_branch_nodes(
            evidence, REFUSED, parent=_parent(), plan_version_id="plan_1",
            mint_node_id=_ids(), handling_class_for=ALWAYS_ORDINARY,
            template_context_for=NO_CONTEXT)
    assert "V3" in str(excinfo.value)


def test_the_privacy_ordering_is_injected_and_has_no_default(seeded):
    """G-KNOWLEDGE. P10 does not rank `sensitive_personal` against
    `highly_sensitive_credential_bearing`; P7 owns that ordering and has not
    published one. A default here could silently give a branch a weaker floor
    than one of its files requires."""
    conn = seeded.conn
    _, evidence = materialise_branch(
        conn, _candidate(("subject", "subject")), branch_node_id="n_academics",
        members=seeded.members("syllabus"), ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS)
    with pytest.raises(ConfigurationRequired):
        project_branch_nodes(
            evidence, ACCEPTED, parent=_parent(), plan_version_id="plan_1",
            mint_node_id=_ids(), handling_class_for=None,
            template_context_for=NO_CONTEXT)


def test_a_role_that_resolves_to_no_live_p6_field_never_reaches_a_node(seeded):
    """C2 is re-checked at the point of use, not only when Task 7 routes.

    Without this, a dimension naming a field P6 does not define reads no values,
    produces an empty level, and the folder simply never appears — a missing
    branch with no error, which is the quietest possible way to break §3.12's
    "should not invent new fields automatically"."""
    conn = seeded.conn
    with pytest.raises(UpstreamUnavailable) as excinfo:
        materialise_branch(
            conn, _candidate(("vibe", "vibe")), branch_node_id="n_academics",
            members=seeded.members("syllabus"), ancestor_field_refs=(), ancestor_depth=0,
            handling_class_for_member=ONE_CLASS)
    assert "vibe" in str(excinfo.value)


def test_the_class_p7_actually_produces_today_reaches_the_node(seeded):
    """P7 writes NO classification in production: nothing in `src/privacy/` calls
    `record_classification`, so `ClassificationStore.current` returns `None` for
    every file and `upstream.handling_class_for` maps that to
    `unreadable_unclassified`. That — not `personal_non_sensitive` — is what a
    live branch's members carry today, and the projection has to survive it.

    `ONE_CLASS` above is the forward-looking case; this is the live one. Both
    exist so the day P7 ships its classifier neither is a surprise."""
    conn = seeded.conn
    unclassified = lambda member: "unreadable_unclassified"
    _, evidence = materialise_branch(
        conn, _candidate(("subject", "subject")), branch_node_id="n_academics",
        members=seeded.members("syllabus"), ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=unclassified)
    assert evidence.levels[0].handling_classes_by_value == {
        "BUSIB 4300": frozenset({"unreadable_unclassified"})}
    nodes = project_branch_nodes(
        evidence, ACCEPTED, parent=_parent(), plan_version_id="plan_1",
        mint_node_id=_ids(), handling_class_for=lambda c: sorted(c)[0],
        template_context_for=NO_CONTEXT)
    assert [n.handling_class for n in nodes] == ["unreadable_unclassified"]


def test_a_projected_node_is_its_own_lineage_origin(seeded):
    """OQ5 is open: ids are minted per version and lineage is recorded. A freshly
    minted node is its own origin, and `Node.__post_init__` rejects an empty
    `origin_node_id`, so it is bound at construction rather than patched after."""
    conn = seeded.conn
    _, evidence = materialise_branch(
        conn, _candidate(("subject", "subject")), branch_node_id="n_academics",
        members=seeded.members("syllabus"), ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS)
    nodes = project_branch_nodes(
        evidence, ACCEPTED, parent=_parent(), plan_version_id="plan_1",
        mint_node_id=_ids(), handling_class_for=ALWAYS_ORDINARY,
        template_context_for=NO_CONTEXT)
    assert all(n.origin_node_id == n.node_id for n in nodes)
    assert all(n.node_type == PROPOSED and n.node_role == ORDINARY for n in nodes)
    assert all(n.root_anchor == "root_documents" for n in nodes)


# --- Contract W5 / anchor H: the template-local level through materialisation ---


def _local_candidate():
    """One schema-field level, then one template-local level beneath it."""
    return _candidate(("subject", "subject"), ("matter_number", None))


def _labels(seeded):
    """Each member's accepted P9 group and its label — where a template-local
    level's children come from, since it has no P6 field to read values off."""
    names = {seeded.file_id(n): n for n in ("syllabus", "hw3", "lab")}
    return lambda member: (f"g_{names[member.file_id]}",
                           f"Matter {names[member.file_id]}")


def test_a_template_local_level_reaches_materialisation_without_calling_c2(seeded):
    """Contract W5: "For a `template-local` dimension, `ResolvedDimension.field_ref`
    is null and C2 is NOT called — calling it would be asking P6 to define
    something that is deliberately not a field."

    Before this, materialisation called `resolve_role_to_field` unconditionally,
    so a novel-domain level died at the one gate the design says must not run for
    it, and the whole layer-2 path stopped one step short of a node.
    """
    _candidate_obj, evidence = materialise_branch(
        seeded.conn, _local_candidate(), branch_node_id="n_academics",
        members=seeded.members("syllabus", "hw3"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        group_label_for_member=_labels(seeded))
    local = evidence.levels[1]
    assert local.field_ref is None
    assert local.values == ("g_hw3", "g_syllabus")
    assert local.display_labels["g_hw3"] == "Matter hw3"


def test_a_template_local_level_contributes_no_expected_value(seeded):
    """Contract W4.3: "There is no `field` to write, so the node's
    `expected_values` is [] and its `dimension` is null."

    A node under a template-local level carries only the expected values its
    SCHEMA-FIELD ancestors settled. The local level adds none, because a group
    label is not a fact value and writing one would assert a fact P6 never made.
    """
    _candidate_obj, evidence = materialise_branch(
        seeded.conn, _local_candidate(), branch_node_id="n_academics",
        members=seeded.members("syllabus", "hw3"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        group_label_for_member=_labels(seeded))
    nodes = project_branch_nodes(
        evidence, ACCEPTED, parent=_parent(), plan_version_id="plan_1",
        mint_node_id=_ids(), handling_class_for=ALWAYS_ORDINARY,
        template_context_for=NO_CONTEXT)
    leaves = [n for n in nodes if n.display_label.startswith("Matter")]
    assert leaves, "the template-local level produced no node"
    for leaf in leaves:
        assert leaf.dimension is None
        assert [e.field for e in leaf.expected_values] == ["subject"]


def test_a_template_local_level_without_group_labels_refuses(seeded):
    """A template-local level's children come from accepted P9 groups. With no
    way to reach them there is nothing to build the level from, and inventing a
    label would be P10 authoring the user's vocabulary — absent configuration is
    `ConfigurationRequired`, never a default."""
    with pytest.raises(ConfigurationRequired):
        materialise_branch(
            seeded.conn, _local_candidate(), branch_node_id="n_academics",
            members=seeded.members("syllabus", "hw3"),
            ancestor_field_refs=(), ancestor_depth=0,
            handling_class_for_member=ONE_CLASS)


def test_child_counts_keeps_one_entry_per_template_local_level(seeded):
    """§5.5: "The user sees the actual branch counts before committing."

    A template-local level has no `field_ref`, so keying the counts on it alone
    puts every such level under the same `None` key and the second one silently
    overwrites the first. Two template-local levels are a legal shape — V1 exists
    precisely to tell two of them apart from a repeated role — so the user would
    be shown one count for two levels, which is the §5.5 promise broken by a
    dict key. `unresolved_by_field` already keys `field_ref or role_ref`; the
    counts the user actually reads must do the same.
    """
    _candidate_obj, evidence = materialise_branch(
        seeded.conn,
        _candidate(("subject", "subject"), ("matter_number", None), ("phase", None)),
        branch_node_id="n_academics", members=seeded.members("syllabus", "hw3"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        group_label_for_member=_labels(seeded))
    counts = child_counts(evidence)
    assert None not in counts, "a level the user is shown a count for has no name"
    assert set(counts) == {"subject", "matter_number", "phase"}
