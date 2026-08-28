"""The multi-life person: one disk, three lives, and what the chain does with it.

`59` §2 calls this "the single most consequential finding in the document" and
"upstream of almost every other one". The owner's standing north star is the
reason: *"If I were a user, a human being, what would I want to do? If I'm a
lawyer or a student or a researcher, **or I am multiple**."*

Multiplicity exists at exactly one place upstream — `facts.domains.active_domains`
is keyed on `(file_id, content_hash)`, several schemas may be true at once, and
its docstring is exactly right: "Activation adds; it never chooses." Everything
below runs the whole chain over a corpus where three schemas are true at once and
asserts what survives.

Every property here has its negative twin beside it. The positive half of a
monotone property cannot detect substitution: "the multi-domain corpus yields
branches covering every group" stays green under a fix that simply stopped
refusing, and C6 not firing at all would destroy the promise the product is for.
So each guard is paired with the case that must still refuse.
"""
from __future__ import annotations

import pytest

from evidence_shape.schema import create_evidence_schema
from grouping.schema import create_grouping_schema
from tree_design.config import TreeLimits
from tree_design.schema import create_tree_schema
from tree_design.vocabulary import (
    PRIMARY_HOME, REFINED, REVIEW_LATER, REVIEW_ONLY, SHALLOW_BY_CHOICE,
)

from p10.multi_life_corpus import (
    ACADEMIC_GROUP, ACADEMIC_LABEL, LAW_GROUP, LAW_LABEL, MEDICAL_GROUP,
    MEDICAL_LABEL, seed_multi_life_corpus, three_life_catalogue,
)
from p10.seam_corpus import ORDINARY_CLASS, PLAN_0, PROTECTED_CLASS, ROOT_ANCHOR

T0 = "2026-08-27T00:00:00Z"
ALL_GROUPS = (ACADEMIC_GROUP, LAW_GROUP, MEDICAL_GROUP)
ALL_DOMAINS = ("academic", "law_practice", "medical")
#: What this corpus's three lives RECOGNISE. `three_life_catalogue`'s rows all
#: cite it, so a branch carrying it selects on schema exactly as the fixture
#: intends; these tests are about coverage across lives, not about selection.
MULTI_LIFE_SIGNALS = frozenset({"signal.multi-life"})


@pytest.fixture()
def corpus(conn, tmp_path):
    create_evidence_schema(conn)
    create_grouping_schema(conn)
    create_tree_schema(conn)
    return seed_multi_life_corpus(conn, tmp_path)


def limits(**over) -> TreeLimits:
    values = dict(max_folder_proposals=5, max_depth=5, max_dossier_tokens=4000,
                  excessive_depth_warning=4, tiny_folder_max_files=1,
                  tiny_folder_count_warning=4,
                  materially_improves_retrieval=lambda _option: True)
    values.update(over)
    return TreeLimits(**values)


def authorities(corpus, **over):
    from tree_design.pipeline import TreeDesignAuthorities

    counter = iter(range(10_000))
    protected = corpus.group_file_ids(MEDICAL_GROUP)
    values = dict(
        catalogue=three_life_catalogue(),
        group_reader=corpus.reader(),
        limits=limits(),
        root_anchor=ROOT_ANCHOR,
        selection_id=corpus.selection_id,
        scan_run_id=corpus.scan_run_id,
        active_domains=ALL_DOMAINS,
        sensitive_group_ids=frozenset({MEDICAL_GROUP}),
        privacy_rank=lambda floor: 0,
        satisfies_purpose_profile=lambda ref, groups: True,
        detection_signals_for=lambda group: MULTI_LIFE_SIGNALS,
        rank_candidates=lambda candidates: list(candidates),
        handling_class_for_member=lambda member: (
            PROTECTED_CLASS if member.file_id in protected else ORDINARY_CLASS),
        collapse_handling_classes=lambda classes: (
            PROTECTED_CLASS if PROTECTED_CLASS in classes else ORDINARY_CLASS),
        handling_class_for_area=lambda area: PROTECTED_CLASS,
        protected_handling_classes=frozenset({PROTECTED_CLASS}),
        collector_field_keys=frozenset({"authored_by", "our_firm"}),
        value_discloses_protected_material=lambda field_ref, value: False,
        template_context_for=lambda field_ref, order_index: None,
        mint_node_id=lambda: f"n_{next(counter)}",
        mint_version_id=lambda: f"plan_{next(counter)}",
    )
    values.update(over)
    return TreeDesignAuthorities(**values)


def decisions(**over):
    from tree_design.fixtures import residual_library_fixture
    from tree_design.pipeline import SharedMaterialAnswer, TreeDesignDecisions
    from tree_design.residuals import ResidualChoice

    library, _ = residual_library_fixture()
    values = dict(
        from_plan_version=PLAN_0,
        branch_group_ids=ALL_GROUPS,
        choose_option=lambda candidate, options: options[0].option_id,
        refinement_for=lambda node: (
            (REFINED, "The levels beneath this node are populated from settled "
                      "facts.")
            if node.parent_node_id is None else
            (SHALLOW_BY_CHOICE, "This branch holds few enough files that a "
                                "further split would not help retrieval.")),
        shared_material=SharedMaterialAnswer(
            parent_origin_id=None, policy=PRIMARY_HOME,
            reason="A file claimed by two lives gets one home and is referenced "
                   "from the other.",
            display_label="Shared Material", policy_scope=None),
        residual_library=library,
        residual_choices=(ResidualChoice(
            template_name=REVIEW_LATER, action="enable",
            disposition=REVIEW_ONLY, display_label=REVIEW_LATER,
            parent_node_id=None, root_anchor=ROOT_ANCHOR, merge_into=None,
            replaces_node_id=None),),
        residual_configuration={REVIEW_LATER: REVIEW_ONLY},
        residual_refinement=(SHALLOW_BY_CHOICE,
                             "§7.2 caps a residual template's depth."),
        residual_handling_class=lambda name: ORDINARY_CLASS,
        created_at=T0, user_id="jy", component_version="p10-multi-life",
    )
    values.update(over)
    return TreeDesignDecisions(**values)


def design(corpus, *, auth=None, dec=None):
    from tree_design.pipeline import design_tree

    return design_tree(corpus.conn, authorities=auth or authorities(corpus),
                       decisions=dec or decisions())


# --- the finding ---------------------------------------------------------------------


def test_a_corpus_that_spans_three_lives_produces_a_branch_for_each(corpus):
    """The headline. Three schemas true at once is not an error, it is three
    branches — and the two coverable ones are split by their OWN recipe."""
    result = design(corpus)

    labels = {node.display_label for node in result.tree.nodes}
    assert {ACADEMIC_LABEL, LAW_LABEL, MEDICAL_LABEL} <= labels
    # Each coverable life split by the recipe authored for it, and by no other.
    assert {"BUSIB 4300", "PHYS1401", "Syllabus", "Homework"} <= labels
    assert {"Acme Industries", "Pleading", "Retainer"} <= labels


def test_every_accepted_group_reaches_a_branch(corpus):
    """Nothing is dropped. Every group the user accepted is associated with a
    node in the frozen tree, including the one no template covers."""
    result = design(corpus)

    associated = {group_id for node in result.tree.nodes
                  for group_id in node.associated_group_ids}
    assert set(ALL_GROUPS) <= associated


def test_each_life_is_split_by_its_own_recipe_and_by_no_other(corpus):
    """The collapse, stated as a property of the tree. `client` is the law
    recipe's level and `subject` is the degree's; a chain that had merged the two
    lives would put one branch's dimension under the other's."""
    result = design(corpus)
    by_id = {node.node_id: node for node in result.tree.nodes}

    def area_of(node):
        while node.parent_node_id is not None:
            node = by_id[node.parent_node_id]
        return node.display_label

    dimensions: dict[str, set[str]] = {}
    for node in result.tree.nodes:
        if node.dimension:
            dimensions.setdefault(area_of(node), set()).add(node.dimension)

    assert dimensions[ACADEMIC_LABEL] == {"subject", "work_type"}
    assert dimensions[LAW_LABEL] == {"client", "work_type"}
    # The uncoverable life is split by nothing at all, which is not the same as
    # being split by somebody else's recipe.
    assert MEDICAL_LABEL not in dimensions


# --- nothing is dropped, and nothing is silent ---------------------------------------


def test_a_group_whose_domain_did_not_activate_still_reaches_the_canvas(corpus):
    """The silent omission this fix closes.

    `horizontal_candidates` used to `continue` past any group whose domain was
    outside `active_domains`. A lawyer whose matters P9 categorised
    `law_practice`, on a corpus where that schema did not activate, lost every
    matter they own from the canvas — no branch, no card, no refusal, nothing to
    click and nothing to read.
    """
    from tree_design.candidates import horizontal_candidates
    from tree_design.upstream import accepted_groups

    groups = accepted_groups(corpus.reader(), plan_version_id=PLAN_0)
    candidates = {c.subject_id: c for c in horizontal_candidates(
        corpus.conn, accepted=groups, existing_folders=(), user_labels=(),
        active_domains=("academic",), sensitive_group_ids=frozenset())}

    assert set(ALL_GROUPS) <= set(candidates)
    # And it SAYS SO. A card that appeared with no explanation would be a
    # different failure of the same rule.
    assert "did not activate" in candidates[LAW_GROUP].why_suggested
    assert "did not activate" not in candidates[ACADEMIC_GROUP].why_suggested


def test_the_whole_chain_still_designs_every_life_when_one_domain_is_inactive(corpus):
    """The same property through `design_tree`, because a candidate that reaches
    the canvas and not the tree has been dropped one stage later."""
    result = design(corpus, auth=authorities(corpus, active_domains=("academic",)))

    labels = {node.display_label for node in result.tree.nodes}
    assert {ACADEMIC_LABEL, LAW_LABEL, MEDICAL_LABEL} <= labels


def test_a_branch_the_user_rejected_does_not_come_back(corpus):
    """The discriminating twin of the two above.

    "Nothing is dropped" is satisfied trivially by a surface that filters
    nothing, and §8.7 requires one filter by name: "Rejected groups, rejected
    destination matches, rejected labels ... must be stored with the evidence
    that produced them. Otherwise the system will repeatedly resurface the same
    attractive but incorrect grouping."
    """
    from tree_design.candidates import horizontal_candidates
    from tree_design.provenance import branch_basis_key, record_tree_edit
    from tree_design.upstream import accepted_groups

    record_tree_edit(
        corpus.conn, action="delete", node_id="n_law", plan_version_id=PLAN_0,
        before={"display_label": LAW_LABEL}, after={},
        explanation=f"User deleted the suggested {LAW_LABEL} area.",
        observed_at=T0, user_id="jy", component_version="p10-multi-life",
        correction_scope="node", correction_subject="__root__",
        polarity="reject",
        basis_key=branch_basis_key(parent_node_id=None,
                                   dimension_or_label=LAW_LABEL))

    groups = accepted_groups(corpus.reader(), plan_version_id=PLAN_0)
    subjects = {c.subject_id for c in horizontal_candidates(
        corpus.conn, accepted=groups, existing_folders=(), user_labels=(),
        active_domains=ALL_DOMAINS, sensitive_group_ids=frozenset())}

    assert LAW_GROUP not in subjects
    assert {ACADEMIC_GROUP, MEDICAL_GROUP} <= subjects


# --- the life no recipe covers -------------------------------------------------------


def test_a_group_no_template_covers_becomes_its_own_visible_unsplit_branch(corpus):
    """`medical` is one of `00` §3.15's safety domains: recognised, field-less,
    and covered by no template. The group is still real and still the user's, so
    it becomes its own branch, keeps every file, is split by nothing, and the
    reason is on the option the user was offered rather than inferred from an
    absence."""
    from tree_design.candidates import NO_SPLIT

    result = design(corpus)
    branch = next(b for b in result.branches
                  if b.candidate.subject_id == MEDICAL_GROUP)

    assert branch.chosen_option_id == "opt_no_split"
    assert [option.kind for option in branch.options] == [NO_SPLIT]
    assert "no applicable recipe resolved" in branch.options[0].summary
    assert "nothing is invented" in branch.options[0].summary
    # Named, not merely empty: the refusal says which domains found no row.
    assert branch.routing.candidates == ()
    assert [c.gate for c in branch.routing.conflicts] == ["C3"]
    assert "medical" in " ".join(branch.routing.conflicts[0].conflicting)

    # It keeps every file. "Its own branch" would be no better than a drop if
    # the material did not travel with it.
    assert set(branch.options[0].example_members) == \
        corpus.group_file_ids(MEDICAL_GROUP)
    node = next(n for n in result.tree.nodes
                if n.display_label == MEDICAL_LABEL)
    assert node.associated_group_ids == (MEDICAL_GROUP,)


# --- one branch holding several lives: `59` §2's own scenario ------------------------
#
# `BranchContext.accepted_groups` is plural, `BranchCandidate.accepted_group_ids`
# is plural, `Node.associated_group_ids` is plural, and §5.3's card is plural:
# "Academics, 201 files: ... includes five accepted course groups". So a branch
# holding a practice beside a degree beside a child's health records is a shape
# the records describe and a user reaches by merging two areas or dragging a
# group into one. The groups below are the corpus's REAL ones, read through
# P10's own seam function, because a hand-built literal proves only that the test
# and the module agree.


def branch_over_every_life(corpus):
    from tree_design.routing import BranchContext
    from tree_design.upstream import accepted_groups

    groups = accepted_groups(corpus.reader(), plan_version_id=PLAN_0)
    assert len(groups) == 3
    return groups, BranchContext(
        branch_node_id="n_one_branch", domains=ALL_DOMAINS,
        accepted_groups=groups,
        member_file_ids=frozenset(m.file_id for g in groups for m in g.members),
        handling_classes=frozenset({ORDINARY_CLASS, PROTECTED_CLASS}),
        detection_signals=MULTI_LIFE_SIGNALS)


def route(corpus, context):
    from tree_design.routing import route_branch

    return route_branch(
        corpus.conn, three_life_catalogue(), context, limits=limits(),
        privacy_rank=lambda floor: 0,
        satisfies_purpose_profile=lambda ref, groups: True,
        rank_candidates=lambda candidates: list(candidates))


def test_a_branch_holding_three_lives_yields_a_candidate_per_coverable_life(corpus):
    """`59` §2, verbatim: this "is not a two-branch outcome. It is a HARD ERROR
    on every candidate." It is now a candidate per life the library speaks for."""
    groups, context = branch_over_every_life(corpus)
    report = route(corpus, context)

    covered = {frozenset(candidate.covered_file_ids)
               for candidate in report.candidates}
    assert covered == {corpus.group_file_ids(ACADEMIC_GROUP),
                       corpus.group_file_ids(LAW_GROUP)}
    # And each candidate is the recipe for the life it covers, not a merge.
    fields = {frozenset(d.field_ref for d in c.resolved_dimensions)
              for c in report.candidates}
    assert fields == {frozenset({"subject", "work_type"}),
                      frozenset({"client", "work_type"})}


def test_the_life_no_recipe_covers_is_one_named_c6_refusal_not_a_dead_branch(corpus):
    """C6 keeps its teeth and changes what it kills.

    It used to refuse EVERY candidate, so a branch spanning three lives produced
    nothing at all. It now refuses once, names the files by id and the area by
    the user's own label, and leaves the candidates that cover the rest standing.
    """
    groups, context = branch_over_every_life(corpus)
    report = route(corpus, context)

    assert [conflict.gate for conflict in report.conflicts] == ["C6"]
    conflict = report.conflicts[0]
    assert set(conflict.conflicting) == set(corpus.group_file_ids(MEDICAL_GROUP))
    assert MEDICAL_LABEL in str(conflict)
    # Non-overridable, and read off the gate rather than restated here.
    assert report.refusals == (conflict,)
    assert report.resolvable == ()
    assert report.candidates


def test_every_member_is_covered_by_a_candidate_or_named_in_the_refusal(corpus):
    """The partition, asserted as one. A file that is in neither set has been
    silently dropped, which is the whole failure C6 exists to prevent."""
    groups, context = branch_over_every_life(corpus)
    report = route(corpus, context)

    reached = frozenset().union(
        *(candidate.covered_file_ids for candidate in report.candidates))
    named = frozenset(
        file_id for conflict in report.conflicts
        for file_id in conflict.conflicting)
    assert reached | named == context.member_file_ids
    assert not (reached & named), (
        "a file both covered and refused would let the surface show it "
        "placed and lost at once")


# --- the negative twin: a genuine silent drop STILL raises C6 ------------------------


def test_a_composition_asked_to_cover_a_life_it_cannot_still_raises_c6(corpus):
    """The half the property above cannot see.

    "The multi-domain corpus yields candidates covering every group" stays green
    under a fix that simply stopped refusing, and a C6 that never fires destroys
    the promise the product is for: material dropped from a preview the user
    approved. So the gate itself is unchanged — hand one composition a group its
    rows do not reach and it refuses, exactly as before.
    """
    from tree_design.routing import evaluate_composition
    from tree_design.templates import CompositionConflict

    catalogue = three_life_catalogue()
    groups, context = branch_over_every_life(corpus)

    with pytest.raises(CompositionConflict) as excinfo:
        evaluate_composition(
            corpus.conn, catalogue, context,
            catalogue.rows_for_schema("academic"),
            privacy_rank=lambda floor: 0,
            satisfies_purpose_profile=lambda ref, gs: True)
    assert excinfo.value.gate == "C6"
    dropped = set(excinfo.value.conflicting)
    assert corpus.group_file_ids(LAW_GROUP) <= dropped
    assert corpus.group_file_ids(MEDICAL_GROUP) <= dropped


def test_no_recorded_approval_turns_a_c6_refusal_into_a_preference():
    """The other half of "do not weaken C6": it is not overridable at the point
    where an override would be WRITTEN DOWN, not merely where it is honoured."""
    from tree_design.routing import CompositionOverride
    from tree_design.templates import CompositionConflict

    with pytest.raises(CompositionConflict) as excinfo:
        CompositionOverride(gate="C6", approved_by="ra_user_said_yes")
    assert "not overridable" in str(excinfo.value)


def test_a_recipe_that_covers_none_of_this_branch_is_not_a_refusal(corpus):
    """The third state, kept apart from the other two. A recipe eligible for a
    schema this branch has no group in dropped nothing — there was nothing here
    for it to hold — so it is absent from the candidates and absent from the
    conflicts, rather than reported as a failure the user should act on."""
    from tree_design.routing import BranchContext
    from tree_design.upstream import accepted_groups

    groups = accepted_groups(corpus.reader(), plan_version_id=PLAN_0)
    law = next(group for group in groups if group.group_id == LAW_GROUP)
    context = BranchContext(
        branch_node_id="n_law_only", domains=ALL_DOMAINS,
        accepted_groups=(law,),
        member_file_ids=frozenset(m.file_id for m in law.members),
        handling_classes=frozenset({ORDINARY_CLASS}),
        detection_signals=MULTI_LIFE_SIGNALS)
    report = route(corpus, context)

    assert len(report.candidates) == 1
    assert report.conflicts == ()
    assert frozenset(report.candidates[0].covered_file_ids) == \
        corpus.group_file_ids(LAW_GROUP)


# --- the branch that names no group, and the branch that names several ---------------


def test_an_existing_folder_adopted_as_a_branch_designs_rather_than_crashes(corpus):
    """§5.10's folder is a branch candidate with NO accepted group, and §5.3's
    card may name several. Both are `BranchCandidate.accepted_group_ids`, plural.

    The chain read `by_id[candidate.subject_id]` — one group per branch, keyed on
    a field that is a group id only for group-derived candidates. A folder or a
    user label raised `KeyError`, and a candidate naming three groups was
    designed from one while its node still claimed all three.
    """
    result = design(corpus, dec=decisions(
        branch_group_ids=(corpus.existing_folder_path,)))

    node = next(n for n in result.tree.nodes
                if n.display_label == corpus.existing_folder_label)
    assert node.associated_group_ids == ()
    assert node.parent_node_id is None
    # It routed and refused BY NAME rather than not routing at all.
    branch = result.branches[0]
    assert branch.routing.candidates == ()
    assert [c.gate for c in branch.routing.conflicts] == ["C3"]


def test_a_branch_designed_from_several_groups_counts_every_one_of_their_files(corpus):
    """The seam the plural field describes, driven through the chain's own
    branch builder rather than through a hand-built candidate.

    `_design_one_branch` is given the candidate's whole group set; the branch's
    members are the union, deduplicated, and the options the user chooses from
    are computed over all of them.
    """
    import dataclasses

    from tree_design.pipeline import _design_one_branch, _open_first_draft
    from tree_design.upstream import accepted_groups

    auth, dec = authorities(corpus), decisions()
    groups = accepted_groups(corpus.reader(), plan_version_id=PLAN_0)
    by_id = {group.group_id: group for group in groups}
    version = _open_first_draft(corpus.conn, auth, dec, False)

    from tree_design.candidates import horizontal_candidates

    candidate = next(
        c for c in horizontal_candidates(
            corpus.conn, accepted=groups, existing_folders=(), user_labels=(),
            active_domains=ALL_DOMAINS, sensitive_group_ids=frozenset())
        if c.subject_id == ACADEMIC_GROUP)
    # The user merged their practice into the same area as their degree. The
    # record has always been able to say so; the chain now designs from it.
    merged = dataclasses.replace(
        candidate, accepted_group_ids=(ACADEMIC_GROUP, LAW_GROUP))

    _version, design_ = _design_one_branch(
        corpus.conn, auth, dec, candidate=merged,
        groups=tuple(by_id[g] for g in merged.accepted_group_ids),
        version=version)

    every_file = (corpus.group_file_ids(ACADEMIC_GROUP)
                  | corpus.group_file_ids(LAW_GROUP))
    # `example_members` is a SAMPLE per `00`:99; `member_count` is the whole
    # number, and it is the number that has to account for both lives.
    assert design_.options[0].member_count == len(every_file)
    assert set(design_.options[0].example_members) <= every_file
    # Two lives in one branch is two options, not one refusal, and no file of
    # either is missing from the pair.
    covered = frozenset().union(
        *(frozenset(c.covered_file_ids) for c in design_.routing.candidates))
    assert covered == every_file
    assert design_.routing.conflicts == ()


# --- the standing security constraint, through a multi-life corpus -------------------


def test_protected_material_survives_the_branching_marked_and_counted(corpus):
    """The owner's standing rule, verbatim: a protected container is MARKED AND
    COUNTED, NEVER OPENED — present-but-untouched, with a reachable explanation,
    never silently omitted, and never described as "understood and found
    unimportant".

    Asserted on a corpus that spans three lives, because the branching is what
    could lose it: material that only ever travelled through a single-branch run
    proves nothing about a run that forms several.
    """
    from tree_design.vocabulary import PROTECTED

    result = design(corpus)

    # P3's protected container. Present, explained, and no destination.
    area = next(node for node in result.tree.nodes
                if node.display_label == corpus.protected_label)
    assert area.node_type == PROTECTED
    assert area.accepts_placement is False
    assert "never opened" in area.explanation and "moved" in area.explanation
    assert area.node_id in result.tree.freeze_record.node_ids
    assert area.node_id not in result.tree.freeze_record.legal_destination_ids

    # P7's protected FILE. Still a member of its own branch, still counted, and
    # the branch wears the class its material requires rather than the ordinary
    # one — marked, not removed.
    branch = next(b for b in result.branches
                  if b.candidate.subject_id == MEDICAL_GROUP)
    assert set(branch.options[0].example_members) == \
        corpus.group_file_ids(MEDICAL_GROUP)
    node = next(node for node in result.tree.nodes
                if node.display_label == MEDICAL_LABEL)
    assert node.handling_class == PROTECTED_CLASS


def _one_more_marked_area(area):
    """A second marked area the tree has no node for."""
    import dataclasses

    return dataclasses.replace(area, path=area.path + "/Unrepresented.app",
                               display_label="Unrepresented.app")


def test_a_marked_area_that_reached_no_node_is_refused_at_freeze(corpus):
    """The negative twin. "Present and counted" is satisfied trivially by a tree
    that happens to contain the area; the guard is that a run which LOST it
    cannot be frozen at all."""
    from tree_design.freeze import FreezeRefused, freeze

    result = design(corpus)
    with pytest.raises(FreezeRefused) as excinfo:
        freeze(corpus.conn, plan_version_id=result.tree.plan_version_id,
               created_at=T0, user_id="jy", component_version="p10-multi-life",
               residual_configuration={REVIEW_LATER: REVIEW_ONLY},
               approved_branch_ids=(), profiles=result.tree.profiles,
               protected_areas=result.protected_areas + (
                   _one_more_marked_area(result.protected_areas[0]),))
    assert any("protected" in reason.lower() for reason in excinfo.value.reasons)
