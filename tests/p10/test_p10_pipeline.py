"""P10's design chain end to end, over a real corpus. The P10 half of the seam.

`placement.pipeline.run_corpus` is the model. P11 has had one entry point that
takes a corpus and runs §6 and §7 over it since it shipped; P10 had none, and the
consequence was that every P10 test drove one module — `route_branch` here,
`materialise_branch` there, `freeze` somewhere else — with the module before it
replaced by a literal. Eleven modules, each green, and nothing that ran them in
order.

The first thing that did found two defects in an hour, both invisible from any
single module: `open_draft` dropped §6.9's policy so a tree edited after the user
chose one could not be frozen, and freeze happily published a tree whose legal
nodes carried no §5.8 answer, which `build_destination_index` then refuses whole.

Everything the user decides arrives on `TreeDesignDecisions` and everything the
DESIGN leaves open arrives on `TreeDesignAuthorities`. Neither has a default, for
the reason `tree_design.config` gives about limits: a default here would be P10
answering a question the design assigns to somebody else.
"""
from __future__ import annotations

import pytest

from evidence_shape.schema import create_evidence_schema
from grouping.schema import create_grouping_schema
from tree_design.config import TreeLimits
from tree_design.schema import create_tree_schema
from tree_design.vocabulary import (
    REFINED, REVIEW_LATER, REVIEW_ONLY, SHALLOW_BY_CHOICE, SHARED_BRANCH,
)

from p10.seam_corpus import (
    ORDINARY_CLASS, PLAN_0, PROTECTED_CLASS, ROOT_ANCHOR,
    seed_seam_corpus, two_dimension_catalogue,
)

T0 = "2026-08-27T00:00:00Z"


@pytest.fixture()
def corpus(conn, tmp_path):
    create_evidence_schema(conn)
    create_grouping_schema(conn)
    create_tree_schema(conn)
    return seed_seam_corpus(conn, tmp_path)


def limits(**over) -> TreeLimits:
    values = dict(max_folder_proposals_and_depth=5, max_dossier_tokens=4000,
                  excessive_depth_warning=4, tiny_folder_max_files=1,
                  tiny_folder_count_warning=2,
                  materially_improves_retrieval=lambda _option: True)
    values.update(over)
    return TreeLimits(**values)


def authorities(corpus, **over):
    from tree_design.pipeline import TreeDesignAuthorities

    counter = iter(range(10_000))
    values = dict(
        catalogue=two_dimension_catalogue(),
        group_reader=corpus.reader(),
        limits=limits(),
        root_anchor=ROOT_ANCHOR,
        selection_id=corpus.selection_id,
        scan_run_id=corpus.scan_run_id,
        active_domains=("academic",),
        sensitive_group_ids=frozenset(),
        privacy_rank=lambda floor: 0,
        satisfies_purpose_profile=lambda ref, groups: True,
        rank_candidates=lambda candidates: list(candidates),
        handling_class_for_member=lambda member: ORDINARY_CLASS,
        collapse_handling_classes=lambda classes: ORDINARY_CLASS,
        handling_class_for_area=lambda area: PROTECTED_CLASS,
        protected_handling_classes=frozenset({PROTECTED_CLASS}),
        # §3.8's author/organization roles. V4 refuses an EMPTY set outright —
        # P6 owns which fields collect — so this names two that plainly are and
        # no count: the schema vocabulary is being widened by another part and a
        # test that pinned its size would break on work that has nothing to do
        # with this seam.
        collector_field_keys=frozenset({"authored_by", "organization"}),
        value_discloses_protected_material=lambda field_ref, value: False,
        template_context_for=lambda field_ref, order_index: None,
        mint_node_id=lambda: f"n_{next(counter)}",
        mint_version_id=lambda: f"plan_{next(counter)}",
    )
    values.update(over)
    return TreeDesignAuthorities(**values)


def decisions(**over):
    from tree_design.pipeline import (
        ScopedGeneralAnswer, SharedMaterialAnswer, TreeDesignDecisions,
    )
    from tree_design.fixtures import residual_library_fixture
    from tree_design.residuals import ResidualChoice

    library, _ = residual_library_fixture()
    values = dict(
        from_plan_version=PLAN_0,
        branch_group_ids=("g_columbia_coursework",),
        choose_option=lambda candidate, options: options[0].option_id,
        refinement_for=lambda node: (
            (REFINED, "The levels beneath this node are populated from settled "
                      "facts.")
            if node.parent_node_id is None else
            (SHALLOW_BY_CHOICE, "This branch holds few enough files that a "
                                "further split would not help retrieval.")),
        shared_material=SharedMaterialAnswer(
            parent_origin_id=None, policy=SHARED_BRANCH,
            reason="Material shared across two courses belongs above both.",
            display_label="Shared Course Material", policy_scope=None),
        scoped_general=(ScopedGeneralAnswer(
            parent_origin_id=None, display_label="General"),),
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
        created_at=T0, user_id="jy", component_version="p10-pipeline",
    )
    values.update(over)
    return TreeDesignDecisions(**values)


def design(corpus, *, auth=None, dec=None):
    from tree_design.pipeline import design_tree

    return design_tree(corpus.conn, authorities=auth or authorities(corpus),
                       decisions=dec or decisions())


# --- the spine ---------------------------------------------------------------------


def test_the_chain_names_5s_steps_in_5s_order():
    from tree_design.pipeline import STEPS

    assert STEPS[0].startswith("read_upstream")
    assert STEPS[-1].startswith("freeze")
    assert len(STEPS) == len(set(STEPS))


def test_every_step_names_a_callee_the_module_actually_calls():
    """AST reachability, not a reference chain. The rule this codebase runs on is
    that a name in two files proves nothing, so each step names the function the
    chain must CALL and this asserts the call site exists."""
    import ast
    import inspect

    from tree_design import pipeline

    called = set()
    for node in ast.walk(ast.parse(inspect.getsource(pipeline))):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                called.add(func.id)
            elif isinstance(func, ast.Attribute):
                called.add(func.attr)
    for step, function in (
            ("read_upstream_evidence", "accepted_groups"),
            ("offer_top_level_branches", "horizontal_candidates"),
            ("route_each_branch", "route_branch"),
            ("materialise_from_facts", "materialise_branch"),
            ("validate_against_v1_v6", "run_checks"),
            ("offer_vertical_options", "vertical_options"),
            ("apply_the_users_decisions", "apply_review_action"),
            ("enable_the_residual_library", "project_residual_nodes"),
            ("represent_protected_areas", "represent_protected_areas"),
            ("profile_each_node", "build_profiles"),
            ("freeze_the_approved_tree", "freeze")):
        assert function in called, (step, function)


# --- the tree that comes out -------------------------------------------------------


def test_a_real_corpus_produces_a_frozen_tree_built_from_its_own_facts(corpus):
    """Not one invented name. Every label below came out of P6's `values` table
    by way of the accepted group, and §5.4's sentence is the whole test: "The
    system does not invent PHYS1401, UChicago, Spring 2026, or PVA/RDP"."""
    result = design(corpus)

    labels = {node.display_label for node in result.tree.nodes}
    assert {"BUSIB 4300", "PHYS1401"} <= labels
    assert {"Syllabus", "Homework"} <= labels
    # And the two the user asked for by gesture rather than by evidence.
    assert {"Shared Course Material", "General", REVIEW_LATER} <= labels
    # The protected area P3 marked, present and counted.
    assert corpus.protected_label in labels


def test_the_frozen_tree_is_read_back_through_p10s_own_seam_function(corpus):
    """`freeze.frozen_tree(conn, plan_version=...)` is the spelling P11 imports,
    so the chain's result must BE what that returns and not a value assembled on
    the way past it."""
    from tree_design.freeze import frozen_tree

    result = design(corpus)
    assert result.tree == frozen_tree(corpus.conn,
                                      plan_version=result.tree.plan_version_id)


def test_every_legal_node_carries_the_users_58_answer(corpus):
    """The precondition P11's index states, satisfied by the chain rather than by
    a fixture. `refinement_for` is the user's answer and the chain applies it;
    without it `freeze` refuses, which is the guard the freeze gate now carries."""
    result = design(corpus)
    legal = [node for node in result.tree.nodes if node.accepts_placement]
    assert legal
    assert all(node.refinement_disposition for node in legal)
    assert all(node.refinement_reason for node in legal)


def test_a_chain_that_answers_58_for_nothing_is_refused_at_freeze(corpus):
    """The negative twin. Remove the producer and the chain must FAIL — a guard
    that only ever sees the answer present cannot tell it is load-bearing."""
    from tree_design.freeze import FreezeRefused

    with pytest.raises(FreezeRefused) as excinfo:
        design(corpus, dec=decisions(refinement_for=lambda node: None))
    assert any("refinement disposition" in reason
               for reason in excinfo.value.reasons)


def test_the_versions_are_a_chain_and_only_the_last_one_is_frozen(corpus):
    """§8.8: every edit opens a draft, and the adopted version is the last one."""
    result = design(corpus)
    assert len(result.plan_version_ids) > 1
    states = dict(corpus.conn.execute(
        "SELECT plan_version_id, state FROM plan_versions").fetchall())
    assert states[result.tree.plan_version_id] == "frozen"
    for version in result.plan_version_ids[:-1]:
        assert states[version] == "draft"


def test_the_chain_carries_p3s_movement_permission_into_the_freeze_record(corpus):
    """§1.1's `cross_folder_moves` is P3's, stored by P10 under §8.8's placement
    policy settings. The chain reads it from the selection rather than taking it
    as an argument, which is what stops it being restated."""
    result = design(corpus)
    assert result.tree.freeze_record.cross_folder_moves is False
    assert result.tree.freeze_record.selection_id == corpus.selection_id


def test_the_run_carries_55s_options_and_57s_report_for_the_branch(corpus):
    """`BranchDesign` is what a review surface reads, so every field on it is
    asserted rather than merely returned.

    §8.6 requires showing "the difference between completed work and deferred
    work", and §5.5 requires the user to see what each option WOULD create before
    committing — so the option set the user chose from has to survive the run,
    not be recomputed by whoever renders it.
    """
    result = design(corpus)
    branch = result.branches[0]

    assert branch.chosen_option_id == "opt_0"
    # One option per routed candidate, and §5.5's no-split always last.
    assert [o.option_id for o in branch.options] == ["opt_0", "opt_no_split"]
    assert branch.options[0].resulting_child_counts == {"subject": 2,
                                                        "work_type": 2}
    assert branch.options[0].validation.accepted            # V1-V6 ran, and passed
    assert branch.routing.candidates and branch.routing.conflicts == ()
    # §5.11, and the two senses of "unresolved" kept apart. `lab` settles no work
    # type, so it is unresolved AT THAT LEVEL and gets no work-type folder — but
    # it did reach a course folder, so it is not unplaced and the option reports
    # no unresolved file. A test that conflated the two would read a populated
    # branch as a failed one.
    assert branch.evidence is not None
    assert branch.evidence.unresolved_by_field["work_type"] == frozenset(
        {corpus.file_id("lab")})
    assert branch.options[0].unresolved_file_ids == ()


def test_a_no_split_branch_writes_no_child_and_is_not_an_error(corpus):
    """§5.5's `opt_no_split` is a design, not a failure. The branch stays as it
    is, the run still freezes, and P11 gets a one-node area."""
    result = design(corpus, dec=decisions(
        choose_option=lambda candidate, options: "opt_no_split"))
    assert result.branches[0].evidence is None
    labels = {node.display_label for node in result.tree.nodes}
    assert "BUSIB 4300" not in labels
    assert "Columbia coursework" in labels


def test_an_option_the_chain_never_offered_is_refused(corpus):
    """The negative twin for `choose_option`: a decision naming an option that
    was never on the canvas chose nothing, and silently taking the first would be
    the chain deciding for the user."""
    from tree_design.config import ConfigurationRequired

    with pytest.raises(ConfigurationRequired) as excinfo:
        design(corpus, dec=decisions(
            choose_option=lambda candidate, options: "opt_invented"))
    assert "opt_invented" in str(excinfo.value)


def test_a_group_that_is_not_a_branch_candidate_is_refused_by_name(corpus):
    """`NothingToDesign` rather than an empty frozen tree. §5.3 builds the top
    level out of accepted groups, existing folders and user labels; naming none
    of them is a caller error and `validate_for_freeze`'s "holds no node" would
    describe the symptom a stage later."""
    from tree_design.pipeline import NothingToDesign

    with pytest.raises(NothingToDesign):
        design(corpus, dec=decisions(branch_group_ids=("g_not_accepted",)))


# --- the chain against the SHIPPED launch library ----------------------------------


def launch_catalogue():
    """`src/tree_design/library/`, through the real loader.

    The seam tests use `two_dimension_catalogue` because `candidate_orders` can
    only be observed by flipping a recipe's recommendation, which a shipped file
    cannot do. This is the other direction: the chain against the data the
    product actually ships.
    """
    import json
    from pathlib import Path

    from tree_design.catalogue import load_catalogue

    library = Path(__file__).resolve().parents[2] / "src" / "tree_design" / "library"
    manifest = {"release_id": "rel-launch"}
    for name in ("fragments", "definitions", "applicabilities"):
        manifest[name] = json.loads((library / f"{name}.json").read_text())[name]
    return load_catalogue(lambda: json.dumps(manifest))


def test_the_launch_library_either_designs_a_tree_or_refuses_by_name(corpus):
    """P11 never receives an empty tree because nothing routed.

    Run over the shipped library today, this corpus REFUSES, and the refusal is
    worth recording because it is not the chain's:

    * eleven `academic` applicability rows are grouped by template, and the four
      that share `def.subject-work-record` — coursework, continuing education,
      online course, study abroad — bind `holder_institution` to `school` under
      four different names ("My school", "Course provider", "Course platform",
      "Host university"). `evaluate_composition` raises C4 on that, so the ONE
      recipe a student's coursework wants is refused outright;
    * a `CompositionOverride(gate=C4, ...)` cannot rescue it. The override
      carries `role_choices` — role to FIELD — and the raise here is about the
      LABEL, and happens after the override has been applied. So the definition
      is unreachable rather than merely contested;
    * the five candidates that do survive are teaching, homeschooling,
      transcripts, K-12 and recommendation letters, and the first of them wants a
      `term` this corpus never settles, so accepting it writes no node.

    That is the template layer's to answer, not the seam's, so this test asserts
    only the property the seam owes: the outcome is a designed tree or a NAMED
    refusal, never a silent empty one. It keeps passing when the library is
    fixed.
    """
    from tree_design.store import ReviewActionRefused
    from tree_design.materialise import MaterialisationRefused
    from tree_design.freeze import FreezeRefused
    from tree_design.pipeline import NothingToDesign
    from tree_design.templates import CompositionConflict

    try:
        result = design(corpus, auth=authorities(corpus,
                                                 catalogue=launch_catalogue()))
    except (ReviewActionRefused, MaterialisationRefused, FreezeRefused,
            NothingToDesign, CompositionConflict) as refusal:
        assert str(refusal).strip(), "a refusal with no reason is a silent one"
        return
    assert [n for n in result.tree.nodes if n.accepts_placement], (
        "the chain froze a tree with no legal destination; P11 would index "
        "nothing and every file would abstain with no reason the user can see")


def test_the_launch_librarys_academic_rows_reach_the_router_at_all(corpus):
    """The discriminating half of the test above.

    "Refuses by name" is satisfied trivially by a catalogue nothing matches, so
    this asserts the corpus does reach real applicability rows: the group's
    `academic` category selects rows, they resolve dimensions against P6's live
    fields, and C1-C8 are judged on real evidence. The refusal above is a
    judgement, not an absence.
    """
    from tree_design.routing import BranchContext, route_branch
    from tree_design.upstream import accepted_groups

    groups = accepted_groups(corpus.reader(), plan_version_id=PLAN_0)
    report = route_branch(
        corpus.conn, launch_catalogue(),
        BranchContext(branch_node_id="n_probe", domains=("academic",),
                      accepted_groups=groups,
                      member_file_ids=frozenset(
                          m.file_id for m in groups[0].members),
                      handling_classes=frozenset({ORDINARY_CLASS})),
        limits=limits(), privacy_rank=lambda floor: 0,
        satisfies_purpose_profile=lambda ref, gs: True,
        rank_candidates=lambda cs: list(cs))
    assert report.candidates or report.conflicts
    resolved = {dimension.field_ref
                for candidate in report.candidates
                for dimension in candidate.resolved_dimensions}
    assert resolved <= {"school", "term", "subject", "work_type"}
    assert resolved, "no shipped academic row resolved a single P6 field"
