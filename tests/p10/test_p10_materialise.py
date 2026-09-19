"""P10 Task 12 — §5.4's populate step, and the counts §5.5 shows before committing.

The rule that makes this correct is that a child value is nested under a parent
value only when the SAME files carry both. A cartesian product of three schools
by five terms by twelve courses would be 180 branches, and §5.5 says the
interface states "three schools, five terms, and twelve course branches". Twelve
is the number of (school, term, course) combinations the evidence actually
contains. Every count here is an intersection, never a product.
"""
from __future__ import annotations

import dataclasses

import pytest

from tree_design.config import ConfigurationRequired
from tree_design.materialise import (
    BranchEvidence,
    LevelEvidence,
    MaterialisationRefused,
    branch_expectations,
    child_counts,
    materialise_branch,
    project_branch_nodes,
    project_branch_preview,
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
#: P7 owns which classes are protected and publishes no ordering, so every
#: caller states it. Isolation is what keeps a protected file out of the
#: branch WITHOUT destroying the branch (`00`:101, `00`:120).
PROTECTED_CLASSES = frozenset({"highly_sensitive_credential_bearing"})
NO_DISCLOSING_VALUES = lambda field_ref, value: False


def test_the_levels_carry_p6s_real_values_and_p10_composes_none(seeded):
    conn = seeded.conn
    materialised, evidence = materialise_branch(
        conn, _candidate(("school", "school"), ("subject", "subject")),
        branch_node_id="n_academics",
        members=seeded.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
    assert [lvl.field_ref for lvl in evidence.levels] == ["school", "subject"]
    assert evidence.levels[0].values == ("Columbia",)
    assert evidence.levels[1].values == ("BUSIB 4300", "PHYS1401")
    # Not one invented name. Every string came out of P6's `values` table.
    assert materialised.levels[1].members_by_value == {"BUSIB 4300": 2, "PHYS1401": 1}


# --- `104` §11.2 step 2: a level whose value the group carries -----------------


def _course_group(seeded, *, anchors, members):
    """One accepted group: its anchors state the basis, its members are carried."""
    from tree_design.upstream import AcceptedGroup, GroupMember
    from grouping.vocabulary import CONTEXT_SUPPORTED, DIRECT_ANCHOR

    def _member(name, basis):
        file_id, content_hash, _key = seeded.subjects[name]
        return GroupMember(file_id=file_id, content_hash=content_hash, basis=basis)

    return AcceptedGroup(
        group_id="g_busib", label="BUSIB 4300", domain="academic",
        members=tuple(
            [_member(name, DIRECT_ANCHOR) for name in anchors]
            + [_member(name, CONTEXT_SUPPORTED) for name in members]),
        anchor_facts=(), excluded_members=())


def _group_reader(*groups):
    """`group_value_for_member` as `tree_design.pipeline` builds one."""
    from tree_design.upstream import group_level_value

    def read(conn):
        by_file = {}
        for group in groups:
            for member in group.members:
                by_file.setdefault(member.file_id, group)

        def value_for(member, field_ref):
            group = by_file.get(member.file_id)
            if group is None:
                return None
            return group_level_value(conn, group=group, field_ref=field_ref)
        return value_for
    return read


def test_an_essay_in_a_course_group_inherits_the_groups_school(seeded, tmp_path):
    """`104` §11.2 step 2's own test, first half. `00`:57 is the sentence.

    The syllabus states the school; the essay states the course and nothing else,
    which is the sparse member the design describes ("HW 3.pdf may contain only
    equations and the phrase 'Homework 3'"). The school level is the COURSE's, so
    the essay lands under it -- and the essay never had to be asked what school it
    was for, which is the question that filed five university essays under a high
    school (`104` §11.1).
    """
    conn = seeded.conn
    seeded.add_subject(tmp_path, "essay", "BUSIB 4300 Essay 2",
                       (("subject", "BUSIB 4300"),))
    group = _course_group(seeded, anchors=("syllabus",), members=("essay",))

    _, evidence = materialise_branch(
        conn, _candidate(("holder_institution", "school")),
        branch_node_id="n_academics",
        members=seeded.members("syllabus", "essay"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES,
        group_level_roles=frozenset({"holder_institution"}),
        group_value_for_member=_group_reader(group)(conn))

    assert evidence.levels[0].values == ("Columbia",)
    assert evidence.levels[0].members_by_value["Columbia"] == frozenset(
        {seeded.file_id("syllabus"), seeded.file_id("essay")})
    assert evidence.unresolved_by_field["school"] == frozenset()


def test_an_essay_outside_any_group_gets_no_school_level(seeded, tmp_path):
    """The second half, and it is the half that stops the collector coming back.

    This essay carries a `school` fact of its own -- the school it MENTIONS, which
    is `00`:44's "authored_by-class metadata" and never a level. In no group, it
    contributes no value at a group-level dimension and is unresolved there, which
    §5.11 permits and which reaches the person as a file waiting on them.
    """
    conn = seeded.conn
    seeded.add_subject(tmp_path, "loose", "Essay 2 Final Draft",
                       (("school", "Georgetown Prep"),))

    _, evidence = materialise_branch(
        conn, _candidate(("holder_institution", "school")),
        branch_node_id="n_academics", members=seeded.members("loose"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES,
        group_level_roles=frozenset({"holder_institution"}),
        group_value_for_member=_group_reader()(conn))

    assert evidence.levels[0].values == ()
    assert "Georgetown Prep" not in evidence.levels[0].display_labels
    assert evidence.unresolved_by_field["school"] == frozenset(
        {seeded.file_id("loose")})


def test_a_group_level_dimension_with_no_reader_is_refused_not_filled_per_file(
        seeded):
    """Absent means refuse. Falling back to `preferred_value_for` here is exactly
    the collector `104` §11.1 measured, and it would be silent: every level would
    be built and every essay filed under the school it happened to mention."""
    with pytest.raises(ConfigurationRequired):
        materialise_branch(
            seeded.conn, _candidate(("holder_institution", "school")),
            branch_node_id="n_academics", members=seeded.members("syllabus"),
            ancestor_field_refs=(), ancestor_depth=0,
            handling_class_for_member=ONE_CLASS,
            protected_handling_classes=PROTECTED_CLASSES,
            group_level_roles=frozenset({"holder_institution"}))


def test_two_anchors_naming_two_schools_leave_the_group_unresolved(seeded, tmp_path):
    """`preferred_value_for`'s multiplicity posture, one level up.

    Two syllabi naming two schools is a real state, and picking between them would
    close P6's OQ6 by accident at the group grain. The members become unresolved at
    that level rather than filed under whichever anchor sorted first.
    """
    conn = seeded.conn
    seeded.add_subject(tmp_path, "other", "BUSIB 4300 Syllabus (transfer)",
                       (("school", "Barnard"), ("subject", "BUSIB 4300")))
    seeded.add_subject(tmp_path, "essay", "BUSIB 4300 Essay 2",
                       (("subject", "BUSIB 4300"),))
    group = _course_group(seeded, anchors=("syllabus", "other"), members=("essay",))

    _, evidence = materialise_branch(
        conn, _candidate(("holder_institution", "school")),
        branch_node_id="n_academics",
        members=seeded.members("syllabus", "other", "essay"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES,
        group_level_roles=frozenset({"holder_institution"}),
        group_value_for_member=_group_reader(group)(conn))

    assert evidence.levels[0].values == ()
    assert evidence.unresolved_by_field["school"] == frozenset(
        seeded.file_id(name) for name in ("syllabus", "other", "essay"))


def test_a_file_with_no_settled_value_is_unresolved_and_gets_no_branch(seeded):
    conn = seeded.conn
    _, evidence = materialise_branch(
        conn, _candidate(("work_type", "work_type")),
        branch_node_id="n_academics", members=seeded.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
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
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
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
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
    assert child_counts(evidence) == {"school": 1, "subject": 2}


def test_the_projection_nests_by_shared_files_and_never_multiplies(seeded):
    conn = seeded.conn
    _, evidence = materialise_branch(
        conn, _candidate(("school", "school"), ("subject", "subject"),
                         ("work_type", "work_type")),
        branch_node_id="n_academics", members=seeded.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
    nodes = project_branch_nodes(
        evidence, ACCEPTED, parent=_parent(), plan_version_id="plan_1",
        mint_node_id=_ids(), handling_class_for=ALWAYS_ORDINARY,
        template_context_for=NO_CONTEXT)
    by_label = {n.display_label: n for n in nodes}
    # No `Columbia`: all three files are at one school, so the `school` level
    # DIVIDES NOTHING and is measured rather than built (`LevelEvidence.divides`).
    # It used to be built, and V2 then refused the whole candidate for producing
    # a one-child level -- so this shape was unreachable in a real run and only a
    # unit test ever saw it. What this test pins is unchanged: nesting is by
    # SHARED FILES and never a product.
    # `00` AMENDMENT 27 PUT THEM BACK. Phase 7 §B.1 measured `Syllabus` and
    # `Homework` under `BUSIB 4300` rather than building them, reading them as
    # `00`:98's two-file packet; the owner ruled on 19 Sep that a level every
    # value splits IS built even where every folder holds one file. The comment
    # here used to end "(Before Phase 7 both were nodes here.)" -- they are again.
    #
    # ASSERTED AS THE PROPERTY AND NOT AS A LABEL SET, because the label set is
    # what moved twice now: what this test is named for is that nesting follows
    # SHARED FILES, so BUSIB 4300's two kinds hang under BUSIB 4300 and nowhere
    # else.
    assert {"BUSIB 4300", "PHYS1401"} <= set(by_label)
    under_busib = {n.display_label for n in nodes
                   if n.parent_node_id == by_label["BUSIB 4300"].node_id}
    assert under_busib == {"Syllabus", "Homework"}, under_busib
    assert "would have had a folder of its own" not in (
        by_label["BUSIB 4300"].explanation)
    # PHYS1401's only file has no work_type, so PHYS1401 gets no children and
    # no fold is said against it: the intersection, not the product -- a
    # kind-of-work measured under PHYS1401 would be the multiplication this
    # test is named for.
    assert [n.display_label for n in nodes
            if n.parent_node_id == by_label["PHYS1401"].node_id] == []
    assert "was not made a folder" not in by_label["PHYS1401"].explanation


def test_every_node_carries_the_ancestor_chain_as_expected_values(seeded):
    conn = seeded.conn
    _, evidence = materialise_branch(
        conn, _candidate(("school", "school"), ("subject", "subject"),
                         ("work_type", "work_type")),
        branch_node_id="n_academics", members=seeded.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
    nodes = project_branch_nodes(
        evidence, ACCEPTED, parent=_parent(), plan_version_id="plan_1",
        mint_node_id=_ids(), handling_class_for=ALWAYS_ORDINARY,
        template_context_for=NO_CONTEXT)
    # `106` Phase 7 §B.1: `Homework` is no longer a node on this corpus (one
    # folder per file beneath `BUSIB 4300` is folded), so the chain is read
    # off the folder that kept the files. A §B.1 fold appends NOTHING to it --
    # the folded values differ per file, so no one of them is the folder's
    # claim. The full-chain case on a fold that does append is pinned by
    # `test_the_folded_values_are_claimed_by_the_folder_that_keeps_the_files`
    # in `test_p10_candidates.py`.
    busib = next(n for n in nodes if n.display_label == "BUSIB 4300")
    assert busib.expected_values == (
        ExpectedValue(field="subject", value="BUSIB 4300"),
    )
    # §6.1's worked example is exactly this shape: the Homework node's expected
    # values are the whole chain, not its own level alone.
    #
    # The chain no longer opens with `school = Columbia`, and that is the point
    # rather than a loss: all three files are at one school, so the level divides
    # nothing, is not built, and a node may not claim an ancestor that does not
    # exist. An expected value for a level the tree does not contain would make
    # P11 match files against a folder nobody proposed.


def test_every_node_explains_itself_from_counted_evidence_and_shows_no_score(seeded):
    conn = seeded.conn
    _, evidence = materialise_branch(
        conn, _candidate(("subject", "subject")),
        branch_node_id="n_academics", members=seeded.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
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
        protected_handling_classes=PROTECTED_CLASSES,
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
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
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
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
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
            handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
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
        # Two subjects, not one: a level with a single value divides nothing, is
        # not built, and this test would then assert over an empty node list --
        # passing without ever carrying a class to a node.
        members=seeded.members("syllabus", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=unclassified,
        protected_handling_classes=PROTECTED_CLASSES)
    assert evidence.levels[0].handling_classes_by_value == {
        "BUSIB 4300": frozenset({"unreadable_unclassified"}),
        "PHYS1401": frozenset({"unreadable_unclassified"})}
    nodes = project_branch_nodes(
        evidence, ACCEPTED, parent=_parent(), plan_version_id="plan_1",
        mint_node_id=_ids(), handling_class_for=lambda c: sorted(c)[0],
        template_context_for=NO_CONTEXT)
    assert nodes, "no node was built, so no class could reach one"
    assert {n.handling_class for n in nodes} == {"unreadable_unclassified"}


def test_a_projected_node_carries_its_key_as_origin_and_a_fresh_id(seeded):
    """OQ5 is CLOSED (`106` Phase 5.1): ids are minted per version and the origin
    is the node's key, so a re-run reads as the same tree. `Node.__post_init__`
    still rejects an empty `origin_node_id`, so it is bound at construction.

    Two levels and three members, because a single one-valued level divides
    nothing and builds no child (`LevelEvidence.divides`): the earlier shape of
    this pin got back only the fixture parent, whose origin IS its id, and
    passed on that alone."""
    conn = seeded.conn
    _, evidence = materialise_branch(
        conn, _candidate(("subject", "subject"), ("work_type", "work_type")),
        branch_node_id="n_academics",
        members=seeded.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
    nodes = project_branch_nodes(
        evidence, ACCEPTED, parent=_parent(), plan_version_id="plan_1",
        mint_node_id=_ids(), handling_class_for=ALWAYS_ORDINARY,
        template_context_for=NO_CONTEXT)
    children = [n for n in nodes if n.node_id != "n_academics"]
    assert children, "no child was built, so nothing below is about a key"
    assert all(n.origin_node_id != n.node_id for n in children)
    assert all(n.origin_node_id.startswith("n_academics/") for n in children)
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
        protected_handling_classes=PROTECTED_CLASSES,
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
        # `lab` as well, so the `subject` level really has two values and is
        # BUILT. With two files of one course it divides nothing, is not
        # built, and the assertion below would pass on an empty chain --
        # proving nothing about what a template-local level contributes.
        members=seeded.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES,
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
            handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)


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
        protected_handling_classes=PROTECTED_CLASSES,
        group_label_for_member=_labels(seeded))
    counts = child_counts(evidence)
    assert None not in counts, "a level the user is shown a count for has no name"
    assert set(counts) == {"subject", "matter_number", "phase"}


def test_the_protected_class_set_is_injected_and_never_defaulted(seeded):
    """Same discipline as `handling_class_for` and V5's own test: P7 owns
    `HANDLING_CLASSES` and publishes no ordering, so a set chosen here would let
    P10 decide which of a user's material is isolated out of their tree. Absent
    means refuse."""
    from tree_design.config import ConfigurationRequired

    with pytest.raises(ConfigurationRequired):
        materialise_branch(
            seeded.conn, _candidate(("subject", "subject")),
            branch_node_id="n_academics",
            members=seeded.members("syllabus", "hw3"),
            ancestor_field_refs=(), ancestor_depth=0,
            handling_class_for_member=ONE_CLASS,
            protected_handling_classes=None)


def test_a_protected_file_stays_a_counted_member_and_is_marked(seeded):
    """RULING: isolation is MARKING, not removal.

    An earlier version of this kept protected members OUT of the level's values
    so the branch could still be built. That was wrong in the direction the
    standing rule forbids: a file dropped from the evidence is UNCOUNTED, and
    "marked and counted, never opened, never silently omitted" is not satisfied
    by omitting it. Counted-and-marked is what the rule asks for.

    The safety property does not depend on removal and never did:
    `placement.privacy.automatic_move_permitted_for` delegates to P7's
    `may_move_automatically`, which refuses a protected file (and an unclassified
    one) unless an explicit policy permits it. P11 already will not move it.
    """
    conn = seeded.conn
    passport = seeded.file_id("hw3")
    _, evidence = materialise_branch(
        conn, _candidate(("school", "school"), ("subject", "subject")),
        branch_node_id="n_academics",
        members=seeded.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=lambda m: (
            "highly_sensitive_credential_bearing"
            if m.file_id == passport else "personal_non_sensitive"),
        protected_handling_classes=PROTECTED_CLASSES)

    # Counted: still a member, still under its value, still in the counts.
    assert passport in evidence.member_file_ids
    assert passport in evidence.levels[0].members_by_value["Columbia"]
    # Marked: named, so the picker can say the branch holds it and it will not move.
    assert evidence.protected_file_ids == frozenset({passport})


def test_a_branch_with_no_protected_file_marks_none(seeded):
    """The discriminating half: marking everything would be as useless as
    marking nothing."""
    conn = seeded.conn
    _, evidence = materialise_branch(
        conn, _candidate(("subject", "subject")),
        branch_node_id="n_academics", members=seeded.members("syllabus", "hw3"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
    assert evidence.protected_file_ids == frozenset()
    assert len(evidence.member_file_ids) == 2


def test_a_branch_whose_levels_divide_nothing_states_their_values_on_itself(seeded):
    """§5.4 measures every level and builds only the ones that divide. What it
    did with the measurement was nothing at all.

    `_top_level_node` says a proposed branch's "expectations are composed by
    `_project` from the branch's evidence", and `_project` composed them onto
    CHILDREN only -- so a branch that built no child stated nothing, and a fact
    naming that very branch had no expected value to match. One file at one
    school on one course is the shape: three levels, three single values, no
    folder worth building, and a destination that cannot be reached by any of the
    three facts that describe it.
    """
    conn = seeded.conn
    _, evidence = materialise_branch(
        conn, _candidate(("school", "school"), ("subject", "subject"),
                         ("work_type", "work_type")),
        branch_node_id="n_academics", members=seeded.members("syllabus"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
    assert [level.divides for level in evidence.levels] == [False, False, False]
    assert branch_expectations(evidence) == (
        ExpectedValue(field="school", value="Columbia"),
        ExpectedValue(field="subject", value="BUSIB 4300"),
        ExpectedValue(field="work_type", value="Syllabus"),
    )
    # And the projection hands the store the branch itself, so the values are
    # written rather than computed and dropped. No FOLDER is created: the one
    # node is the branch that already existed.
    nodes = project_branch_nodes(
        evidence, ACCEPTED, parent=_parent(), plan_version_id="plan_1",
        mint_node_id=_ids(), handling_class_for=ALWAYS_ORDINARY,
        template_context_for=NO_CONTEXT)
    assert [node.node_id for node in nodes] == ["n_academics"]
    assert nodes[0].expected_values == branch_expectations(evidence)


def test_a_branch_that_builds_a_child_states_nothing_on_itself(seeded):
    """The discriminating half, and the reason this is not applied to the chain.

    Two courses divide, so `subject` becomes folders and each one carries its own
    expected value. `school` divides nothing here too -- but adding `Columbia` to
    the branch beside two reachable children would give one file two direct-fact
    destinations where the evidence names one, and adding it to the CHILDREN
    would make a level deliberately not built discriminate after all.
    """
    conn = seeded.conn
    _, evidence = materialise_branch(
        conn, _candidate(("school", "school"), ("subject", "subject")),
        branch_node_id="n_academics",
        members=seeded.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
    preview = project_branch_preview(
        evidence, ACCEPTED, parent=_parent(), plan_version_id="plan_1",
        mint_node_id=_ids(), handling_class_for=ALWAYS_ORDINARY,
        template_context_for=NO_CONTEXT)
    assert preview.branch_expectations == ()
    assert preview.parent.expected_values == ()
    assert {node.display_label for node in preview.nodes} == {
        "BUSIB 4300", "PHYS1401"}
    for node in preview.nodes:
        assert [value.field for value in node.expected_values] == ["subject"]


def test_a_value_only_protected_files_carry_is_not_stated_on_the_branch(seeded):
    """The same rule `_project` applies to a folder NAME, applied to an
    expectation.

    A name carried by nothing but protected material publishes that material, and
    an expected value is published in the same places: the placement index, the
    dossier, and every sentence that names a destination. The file stays a
    member, stays counted and stays marked -- what it loses is a claim of its own.
    """
    conn = seeded.conn
    _, evidence = materialise_branch(
        conn, _candidate(("school", "school"), ("subject", "subject")),
        branch_node_id="n_academics", members=seeded.members("syllabus"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=lambda member: (
            "highly_sensitive_credential_bearing"),
        protected_handling_classes=PROTECTED_CLASSES)
    assert evidence.protected_file_ids == evidence.member_file_ids
    assert branch_expectations(evidence) == ()
    # Counted, not omitted: the member is still in the branch's evidence.
    assert len(evidence.member_file_ids) == 1


def test_the_branch_keeps_the_expectations_it_already_observed(seeded):
    """An adopted folder already states what its contents agree on (§6.2), read
    off a directory that exists. A measured level may add to that and may never
    restate a field the observation already answered, or P11 would match one file
    against two values of one field on one node."""
    conn = seeded.conn
    _, evidence = materialise_branch(
        conn, _candidate(("school", "school"), ("subject", "subject")),
        branch_node_id="n_academics", members=seeded.members("syllabus"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
    observed = dataclasses.replace(
        _parent(), expected_values=(
            ExpectedValue(field="subject", value="BUSIB 4300"),))
    preview = project_branch_preview(
        evidence, ACCEPTED, parent=observed, plan_version_id="plan_1",
        mint_node_id=_ids(), handling_class_for=ALWAYS_ORDINARY,
        template_context_for=NO_CONTEXT)
    assert preview.parent.expected_values == (
        ExpectedValue(field="subject", value="BUSIB 4300"),
        ExpectedValue(field="school", value="Columbia"),
    )


def test_a_level_that_divides_never_contributes_a_value_to_the_branch():
    """Asked of the function directly, because the projection's own guard hides
    it: `branch_expectations` runs only where no node was built, and a level that
    divides normally builds one.

    Normally. A level whose every value is carried by protected files alone
    builds nothing, and so does one whose values reach none of the parent's
    remaining members -- and in either case a level with two values has no single
    value to state. Taking `values[0]` would file every file in the branch under
    whichever name sorts first, which is the invention §5.4 exists to prevent.
    """
    divided = LevelEvidence(
        dimension_role="subject", field_ref="subject", order_index=0,
        metadata_only=False, display_labels={},
        members_by_value={"BUSIB 4300": frozenset({"f2"}),
                          "PHYS1401": frozenset({"f1"})},
        handling_classes_by_value={
            "BUSIB 4300": frozenset({"personal_non_sensitive"}),
            "PHYS1401": frozenset({"personal_non_sensitive"})})
    agreed = LevelEvidence(
        dimension_role="school", field_ref="school", order_index=1,
        metadata_only=False, display_labels={},
        members_by_value={"Columbia": frozenset({"f1", "f2"})},
        handling_classes_by_value={
            "Columbia": frozenset({"personal_non_sensitive"})})
    evidence = BranchEvidence(
        branch_node_id="n_branch", levels=(divided, agreed),
        member_file_ids=frozenset({"f1", "f2"}), unresolved_by_field={})
    assert branch_expectations(evidence) == (
        ExpectedValue(field="school", value="Columbia"),)
