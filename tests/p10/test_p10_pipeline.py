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

import dataclasses

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
    values = dict(max_folder_proposals=5, max_depth=5, max_dossier_tokens=4000,
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
        # What this corpus's one life RECOGNISES. `two_dimension_catalogue`'s
        # row cites `signal.seam`; the launch-library tests below override this
        # with the real `recognition:` refs, which is the point of the seam —
        # the chain reads whatever the branch's evidence supported and writes
        # no rule of its own.
        detection_signals_for=lambda group: frozenset({"signal.seam"}),
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

    The refusal this used to record was the router's own: eleven `academic` rows
    were grouped by template, the five sharing `def.subject-work-record` were
    handed to one composition whatever the branch's evidence said, and they bind
    `holder_institution` to `school` under four names — "My school", "Course
    provider", "Course platform", "Host university". C4 refused, correctly, an
    input no branch ever asked for, and no `CompositionOverride` could rescue it
    because `role_choices` answers role-to-FIELD and the raise was about the
    LABEL. The recipe a student's coursework wants was unreachable rather than
    contested.

    With the branch stating which situation it recognises, that is gone: the
    chain routes `ap.academic.coursework`, resolves four live P6 fields and
    reaches MATERIALISATION, where this three-file corpus refuses at V2 —
    §5.7's "meaningless one-child levels", one school and one term and one
    subject. That is a judgement about a tiny corpus rather than a hole in the
    library, and it is the template layer's to answer, not the seam's.

    So this test asserts only the property the seam owes: the outcome is a
    designed tree or a NAMED refusal, never a silent empty one.
    """
    from tree_design.store import ReviewActionRefused
    from tree_design.materialise import MaterialisationRefused
    from tree_design.freeze import FreezeRefused
    from tree_design.pipeline import NothingToDesign
    from tree_design.templates import CompositionConflict

    try:
        result = design(corpus, auth=authorities(
            corpus, catalogue=launch_catalogue(),
            detection_signals_for=lambda group: COURSEWORK_SIGNALS))
    except (ReviewActionRefused, MaterialisationRefused, FreezeRefused,
            NothingToDesign, CompositionConflict) as refusal:
        assert str(refusal).strip(), "a refusal with no reason is a silent one"
        return
    assert [n for n in result.tree.nodes if n.accepts_placement], (
        "the chain froze a tree with no legal destination; P11 would index "
        "nothing and every file would abstain with no reason the user can see")


#: What this corpus's one life recognises, in the shipped library's own
#: vocabulary. `seam_corpus` is a Columbia coursework group — three files, a
#: `school` anchor, a `term` and a `subject` — so the situation it is in is the
#: one `planning/domains/nodes/academic.coursework.json` describes, and
#: `ap.academic.coursework` is the row authored for it. Spelled `recognition:`
#: because a detection signal names a compiled recognition row; the manifest at
#: `src/recognition/library/recognition.json` holds `academic.coursework` and
#: this reference is checked against it below.
COURSEWORK_SIGNALS = frozenset({"recognition:academic.coursework"})


def test_the_launch_librarys_academic_rows_reach_the_router_at_all(corpus):
    """The discriminating half of the test above.

    "Refuses by name" is satisfied trivially by a catalogue nothing matches, so
    this asserts the corpus does reach real applicability rows: the group's
    `academic` category and the situation its evidence recognises select rows,
    they resolve dimensions against P6's live fields, and C1-C8 are judged on
    real evidence. The refusal above is a judgement, not an absence.
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
                      handling_classes=frozenset({ORDINARY_CLASS}),
                      detection_signals=COURSEWORK_SIGNALS),
        limits=limits(), privacy_rank=lambda floor: 0,
        satisfies_purpose_profile=lambda ref, gs: True,
        rank_candidates=lambda cs: list(cs))
    assert report.candidates or report.conflicts
    resolved = {dimension.field_ref
                for candidate in report.candidates
                for dimension in candidate.resolved_dimensions}
    assert resolved <= {"school", "term", "subject", "work_type"}
    assert resolved, "no shipped academic row resolved a single P6 field"




# --- the detection signal, and the rows a branch's evidence actually selects -------
#
# WHAT A DETECTION SIGNAL IS, settled from `00` §5.7 and the launch draft rather
# than from the router. §5.7 fixes the field on the library template — a template
# defines "the domain's allowed fact fields, DETECTION SIGNALS, recommended folder
# dimensions, preferred dimension order..." — and
# `planning/51-LAUNCH-TEMPLATE-DRAFT.md` §5 fixes what the reference points AT:
# *"`detection_signal_refs` point at the node's own `recognition` block — R2 owns
# the actual patterns and this draft writes none."*
#
# So a signal names one of the 358 researched SITUATIONS, and the vocabulary was
# already compiled and shipped: `src/recognition/library/recognition.json` lists
# every non-refused row id per schema. P10 writes no pattern; it reads the
# reference and asks whether the branch's evidence carried it.


def compiled_recognition_rows() -> frozenset[str]:
    """Every row id `src/recognition/` compiled, refused ones included.

    Read through the file rather than restated here, because the point of the
    assertion below is that the two vocabularies are ONE and cannot drift.
    """
    import json
    from pathlib import Path

    manifest = json.loads(
        (Path(__file__).resolve().parents[2] / "src" / "recognition" /
         "library" / "recognition.json").read_text())
    rows: set[str] = set()
    for schema in manifest["schemas"].values():
        rows.update(schema["rows"])
        rows.update(schema["refused_rows"])
    return frozenset(rows)


def test_every_shipped_detection_signal_names_a_compiled_recognition_row():
    """The vocabulary is BOUND, not parallel.

    `detection_signal_refs` had no reader in `src/` at all, which is the state
    in which a second, private vocabulary gets invented by whoever writes the
    first one — and this project has paid for a field with two homes before. So
    the reader binds to the one that already exists: `recognition.compile` emits
    a row id per researched situation, and every signal the library cites is one
    of those ids under the `recognition:` prefix.

    What `src/recognition/` does NOT publish is which row fired. `Detector.
    explain` returns a `Recognition` naming a `schema_id`, because `compile_rules`
    unions every row's `proposed_context_terms` into one per-schema set and a
    term match can no longer be attributed to a row. The vocabulary is upstream;
    the row-level producer is not, which is why the branch CARRIES the signals
    rather than deriving them here.
    """
    compiled = compiled_recognition_rows()
    catalogue = launch_catalogue()
    signals = {signal
               for row in catalogue.applicabilities.values()
               for signal in row.detection_signal_refs}
    assert signals, "the launch library cites no detection signal at all"
    unprefixed = sorted(s for s in signals if not s.startswith("recognition:"))
    assert not unprefixed, (
        f"{unprefixed} name no namespace. A bare signal id is the beginning of a "
        "second detection vocabulary that nothing keeps in step with the "
        "compiled one")
    unknown = sorted(s for s in signals
                     if s.split(":", 1)[1] not in compiled)
    assert not unknown, (
        f"{unknown} name no compiled recognition row. A signal nothing produces "
        "can never be supported, so every row citing it is unreachable — the "
        "defect this reader exists to end, one level down")


#: The (definition, schema) pairs the shipped library cannot compose. PINNED, not
#: derived: the test below fails when this set changes in EITHER direction, which
#: is the point — a fix has to register as a change rather than as the same green.
#:
#: **It was seven, and it is now empty.** Every one of the launch library's 32
#: pairs composes; all 54 applicability rows are reachable, up from 25.
#:
#: What moved is not the library and not the labels — `LABEL_COLLIDING_PAIRS`
#: below is unchanged, and every one of those 60 per-audience names still ships.
#: What moved is WHICH ROWS A BRANCH IS HANDED. `eligible_rows` filtered on
#: `uses_schema` alone, so a branch was handed every row sharing a schema —
#: coursework AND continuing education AND an online course AND a term abroad AND
#: a standardized test — and those five, correctly, call `school` four different
#: things. C4 then refused, correctly, given an input no branch's evidence ever
#: asked for. `detection_signal_refs` is the field that says which situation a
#: row recognises; it now has a reader, and a branch is handed the rows its own
#: evidence selected.
#:
#: `planning/56-TEMPLATE-CONNECTION-AUDIT.md` §6.2 named this fix before it was
#: made: *"stop unioning rows the branch's evidence does not select."*
UNCOMPOSABLE_LAUNCH_PAIRS: dict[tuple[str, str], tuple[str, ...]] = {}

#: The seven pairs whose per-row labels disagree, and the roles they disagree on.
#: A FACT ABOUT THE LIBRARY, unchanged by the fix and pinned so it stays that
#: way: these are the 60 authored per-audience names §5.1 asks for — "reflect the
#: user's vocabulary rather than a universal corporate taxonomy" — and a fix that
#: had worked by flattening them would show up here as a shrinking set.
#:
#: They are also the material for the negative twin: a branch that GENUINELY
#: recognises two of these situations at once is handed two rows that name one
#: field two ways, and C4 must still refuse it.
LABEL_COLLIDING_PAIRS: dict[tuple[str, str], tuple[str, ...]] = {
    ("def.addressee-packet", "college_applications"):
        ("addressed_org", "cycle_period"),
    ("def.capture-time-events", "photos"): ("capture_time", "occasion_anchor"),
    ("def.capture-time-events.third-party", "photos"): ("capture_time",),
    ("def.group-scoped-record", "finance"): ("artifact_kind",),
    ("def.issuer-record", "finance"):
        ("account_kind", "artifact_kind", "issuing_org"),
    ("def.research-lineage", "research"):
        ("artifact_kind", "lifecycle_stage", "subject_anchor"),
    ("def.subject-work-record", "academic"):
        ("artifact_kind", "holder_institution", "subject_anchor"),
}


def _launch_pairs() -> dict[tuple[str, str], list]:
    catalogue = launch_catalogue()
    by_pair: dict[tuple[str, str], list] = {}
    for row in catalogue.applicabilities.values():
        by_pair.setdefault((row.template_id, row.uses_schema), []).append(row)
    return by_pair


def _colliding_roles(rows) -> tuple[str, ...]:
    """The roles these rows name more than one way. C4's label branch, exactly."""
    names: dict[tuple[str, str], set[str]] = {}
    for row in rows:
        for binding in row.role_bindings:
            names.setdefault((binding.role_ref, binding.field_ref),
                             set()).add(binding.label)
    return tuple(sorted(role for (role, _field), labels in names.items()
                        if len(labels) > 1))


def _branch_recognising(schema: str, signals, groups=()):
    """One branch over `schema` whose evidence recognises exactly `signals`."""
    from tree_design.routing import BranchContext

    return BranchContext(
        branch_node_id="n_probe", domains=(schema,),
        accepted_groups=tuple(groups),
        member_file_ids=frozenset(m.file_id for g in groups for m in g.members),
        handling_classes=frozenset({ORDINARY_CLASS}),
        detection_signals=frozenset(signals))


def test_the_shipped_librarys_unroutable_recipes_are_exactly_the_known_set():
    """The half `..._either_designs_a_tree_or_refuses_by_name` cannot see.

    That test asserts the seam property — a designed tree or a NAMED refusal,
    never a silent empty one — and it once held for the wrong reason: the
    refusal was C4-labelled, which reads as one contested mapping rather than as
    54% of the launch library being unroutable. A monotone "it refuses cleanly"
    check stays green whether the number is 1 row or 29.

    So this pins the actual state, and it pins it THROUGH THE ROUTER. The
    version of this test that shipped with the diagnosis measured a proxy — a
    label collision anywhere inside a multi-row pair — because at the time every
    such collision was reached, `eligible_rows` having handed the whole pair to
    one composition. That proxy cannot see this fix at all: the labels are
    library data and the fix does not touch them. So the measurement is now the
    real question, asked of the real function. For every row: a branch whose
    evidence recognises exactly that row's situation is handed that row, and the
    rows it is handed do not name one field two ways.

    Measured over the shipped files: 54 applicability rows across 32
    (definition, schema) pairs, of which 7 hold more than one row. All seven were
    unroutable, putting 29 rows (54%) inside a recipe that could not compose.
    `def.issuer-record` is the launch set's biggest definition at 11 rows and was
    among them. It is now empty.

    Not a count, a SET: a new non-clashing row does not move it, and a fix to any
    one pair does. The message says which way it moved.
    """
    from tree_design.routing import eligible_rows

    catalogue = launch_catalogue()
    by_pair = _launch_pairs()
    # The sweep's own size, asserted so an empty result cannot come from an
    # empty sweep. A fix that stopped selecting rows at all would pass "no pair
    # clashes" trivially, and ship a library that composes nothing.
    assert len(by_pair) == 32
    assert sum(len(rows) for rows in by_pair.values()) == 54
    assert sum(1 for rows in by_pair.values() if len(rows) > 1) == 7

    unroutable: dict[tuple[str, str], tuple[str, ...]] = {}
    for pair, rows in by_pair.items():
        template_id, schema = pair
        failing: list[str] = []
        for row in rows:
            context = _branch_recognising(schema, row.detection_signal_refs)
            selected = [candidate for candidate in eligible_rows(catalogue, context)
                        if candidate.template_id == template_id]
            if row not in selected:
                failing.append(f"{row.applicability_id} selects itself: no")
            elif _colliding_roles(selected):
                failing.append(
                    f"{row.applicability_id} -> {_colliding_roles(selected)}")
        if failing:
            unroutable[pair] = tuple(sorted(failing))

    fixed = sorted(set(UNCOMPOSABLE_LAUNCH_PAIRS) - set(unroutable))
    broken = sorted(set(unroutable) - set(UNCOMPOSABLE_LAUNCH_PAIRS))
    assert unroutable == UNCOMPOSABLE_LAUNCH_PAIRS, (
        f"the launch library's unroutable set moved. Now composable: {fixed}. "
        f"Newly unroutable: {broken}. Update UNCOMPOSABLE_LAUNCH_PAIRS and say "
        "which it was in the commit — this set shrinking is the fix landing.")


def test_every_shipped_row_is_reachable_by_the_situation_it_recognises():
    """The other half of an empty set: 54 of 54, not 0 of 0.

    "No pair is unroutable" is satisfied by a selector that returns nothing, so
    this asserts the positive: every applicability row in the launch library is
    selected — and selected ALONE — by the situation it was authored for. That
    is the product claim `56` §6.2 made: *"A student's coursework branch should
    route `ap.academic.coursework`, not coursework + continuing-education +
    online-course + study-abroad + standardized-testing merged into one recipe
    with four names for `school`."*
    """
    from tree_design.routing import eligible_rows

    catalogue = launch_catalogue()
    unreachable: list[str] = []
    widened: dict[str, tuple[str, ...]] = {}
    for row in catalogue.applicabilities.values():
        context = _branch_recognising(row.uses_schema, row.detection_signal_refs)
        selected = eligible_rows(catalogue, context)
        if row not in selected:
            unreachable.append(row.applicability_id)
            continue
        others = tuple(sorted(other.applicability_id for other in selected
                              if other is not row))
        if others:
            widened[row.applicability_id] = others
    assert not unreachable, (
        f"{len(unreachable)} shipped rows recognise a situation that selects "
        f"them for nothing: {unreachable}")
    assert not widened, (
        "a branch recognising one situation was handed rows authored for "
        f"others: {widened}. Every launch signal is cited by exactly one row, so "
        "this is over-collection returning by another door")


def test_a_branch_that_recognises_two_situations_still_refuses_at_c4(corpus):
    """THE NEGATIVE TWIN. C4 is not weakened; it is finally aimed at something.

    A branch really can hold two situations at once, and when it does it is
    handed both rows — selection narrows the merge, it does not forbid one. If
    those two rows name one field two ways, that is an authoring conflict inside
    the library and C4 must still refuse it, unchanged and non-silently.

    Before the reader, this refusal fired on EVERY multi-row pair, because the
    framework handed every branch every row sharing a schema; it said nothing
    about the library and everything about the router. Here it says what it was
    written to say: this user's evidence supports two situations that disagree
    about what to call `school`, and P10 names neither for them.
    """
    from tree_design.routing import eligible_rows, evaluate_composition
    from tree_design.templates import CompositionConflict
    from tree_design.upstream import accepted_groups

    catalogue = launch_catalogue()
    groups = accepted_groups(corpus.reader(), plan_version_id=PLAN_0)
    both = COURSEWORK_SIGNALS | {"recognition:academic.study-abroad"}
    context = _branch_recognising("academic", both, groups)

    selected = [row for row in eligible_rows(catalogue, context)
                if row.template_id == "def.subject-work-record"]
    assert sorted(row.applicability_id for row in selected) == [
        "ap.academic.coursework", "ap.academic.study-abroad"]

    with pytest.raises(CompositionConflict) as excinfo:
        evaluate_composition(corpus.conn, catalogue, context, selected,
                             privacy_rank=lambda floor: 0,
                             satisfies_purpose_profile=lambda ref, gs: True)
    message = str(excinfo.value)
    assert message.startswith("C4")
    assert "holder_institution" in message
    # The two names, both shipped, both correct for their audience. The refusal
    # quotes them rather than picking one, which is the whole reason it refuses.
    assert "My school" in message and "Host university" in message


def test_the_labels_the_fix_had_to_preserve_are_all_still_there():
    """A guard against the tempting wrong fix, pinned in both directions.

    Deduplicating the labels, or taking the first, would have emptied
    `UNCOMPOSABLE_LAUNCH_PAIRS` too — and destroyed the feature. `RoleBinding`'s
    docstring is explicit that the label is per-row because "one role reads
    differently per schema", and `00` §5.1 asks labels to "reflect the user's
    vocabulary rather than a universal corporate taxonomy". A library where every
    row of a definition must share one name has no audience-specific naming left.

    So: the seven pairs still disagree about their labels, on exactly the roles
    they disagreed about before, and not one of the 503 bindings has decayed into
    its own field key.
    """
    colliding = {pair: _colliding_roles(rows)
                 for pair, rows in _launch_pairs().items()
                 if len(rows) > 1 and _colliding_roles(rows)}
    assert colliding == LABEL_COLLIDING_PAIRS, (
        "the library's per-audience labels moved. This fix must not touch them: "
        "it works by handing a branch fewer rows, not by making more rows agree")

    launch = [binding
              for row in launch_catalogue().applicabilities.values()
              for binding in row.role_bindings]
    assert len(launch) == 123, "the 54 launch rows' authored names"

    # Every row the library holds, waves 2 included, because the claim is about
    # the authored vocabulary and not about which wave shipped it.
    import json
    from pathlib import Path

    library = Path(__file__).resolve().parents[2] / "src" / "tree_design" / "library"
    bindings = [binding
                for path in sorted(library.glob("*.json"))
                for rows in json.loads(path.read_text()).values()
                if isinstance(rows, list)
                for row in rows
                for binding in row.get("role_bindings", ())]
    assert len(bindings) == 503
    echoes = sorted({binding["label"] for binding in bindings
                     if binding["label"] == binding["field_ref"]})
    assert not echoes, (
        f"{echoes} ship the internal field key as the user-visible name; "
        "`RoleBinding.label` exists to end exactly that")


def test_a_row_the_branchs_evidence_does_not_recognise_is_refused_by_name(corpus):
    """The empty case, and it is a NAMED refusal rather than a silent widening.

    A branch whose evidence supports no row for its schema is a real state — an
    `academic` group in a situation the research never wrote a recipe for — and
    the honest answer is C3 naming the rows it declined. Falling back to "every
    row sharing a schema" is what produced the defect; falling back to silence is
    the seam property `..._either_designs_a_tree_or_refuses_by_name` forbids.
    """
    from tree_design.routing import eligible_rows, route_branch

    catalogue = launch_catalogue()
    groups = accepted_groups_for(corpus)
    context = _branch_recognising("academic", (), groups)
    assert eligible_rows(catalogue, context) == ()

    report = route_branch(
        corpus.conn, catalogue, context, limits=limits(),
        privacy_rank=lambda floor: 0,
        satisfies_purpose_profile=lambda ref, gs: True,
        rank_candidates=lambda cs: list(cs))
    assert report.candidates == ()
    assert len(report.conflicts) == 1
    refusal = str(report.conflicts[0])
    assert refusal.startswith("C3")
    # It names the rows it declined, so the reader knows the library HAS
    # academic recipes and this branch recognised none of their situations —
    # which sends them to the recognition rules, not to the catalogue.
    assert "ap.academic.coursework" in refusal
    assert "detection signal" in refusal


def test_a_row_that_names_no_situation_stays_eligible_on_its_schema():
    """The asymmetry, stated as a test because it is a judgement call.

    An empty `detection_signal_refs` is the row saying "wherever this schema is,
    I apply" — not "nothing recognises me". Reading it the second way would
    silently retire every such row, which is a library change made by a router.
    The shipped library has none today; the record permits one, so the reader
    has to answer for it.
    """
    from tree_design.routing import eligible_rows
    from p10.test_p10_routing import _catalogue, _definition, _fragment, _row
    from tree_design.templates import FragmentRef

    subject = _fragment("subject", ("subject",))
    definition = _definition("d", (FragmentRef("subject", 1),), ("subject",))
    silent = dataclasses.replace(
        _row("a-silent", "d", "academic", (("subject", "subject"),)),
        detection_signal_refs=())
    catalogue = _catalogue(
        (subject,), (definition,),
        (_row("a-situated", "d", "academic", (("subject", "subject"),)), silent))

    recognises_nothing = _branch_recognising("academic", ())
    assert [row.applicability_id
            for row in eligible_rows(catalogue, recognises_nothing)] == ["a-silent"]

    recognises_the_situation = _branch_recognising("academic", ("signal.fixture",))
    assert sorted(row.applicability_id
                  for row in eligible_rows(catalogue, recognises_the_situation)) == [
        "a-silent", "a-situated"]


def accepted_groups_for(corpus):
    from tree_design.upstream import accepted_groups

    return accepted_groups(corpus.reader(), plan_version_id=PLAN_0)


def test_the_five_row_academic_recipe_composes_once_the_signal_is_read(corpus):
    """The test that diagnosed this, kept and re-pointed at the fix.

    Its earlier form fed `def.subject-work-record` / `academic` the same
    definition, the same schema and the same corpus ONE ROW AT A TIME — by
    hand, because nothing in `src/` could do it — and recorded that it composed
    cleanly where all five together refused. In its own words: *"what breaks the
    seven is that `evaluate_composition` merges rows the branch's evidence never
    selected, and `eligible_rows` filters on `uses_schema` alone
    (`detection_signal_refs`, the field that says which situation a row
    recognises, has no reader in `src/`)."*

    It has one now, so the hand-picking is gone. The branch states what it
    recognises, `eligible_rows` picks the row, and the five-row recipe — the
    one a student's coursework actually wants — composes.
    """
    from tree_design.routing import eligible_rows, evaluate_composition

    catalogue = launch_catalogue()
    academic = _launch_pairs()[("def.subject-work-record", "academic")]
    assert len(academic) == 5

    groups = accepted_groups_for(corpus)
    context = _branch_recognising("academic", COURSEWORK_SIGNALS, groups)
    selected = [row for row in eligible_rows(catalogue, context)
                if row.template_id == "def.subject-work-record"]
    assert [row.applicability_id for row in selected] == ["ap.academic.coursework"]

    composed = evaluate_composition(
        corpus.conn, catalogue, context, selected,
        privacy_rank=lambda floor: 0,
        satisfies_purpose_profile=lambda ref, gs: True)
    assert [d.field_ref for d in composed.resolved_dimensions] == [
        "school", "term", "subject", "work_type"]
    assert [d.display_label for d in composed.resolved_dimensions] == [
        "My school", "Semester", "Course", "Kind of work"]
