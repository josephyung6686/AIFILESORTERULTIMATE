"""`104` §18.2 gap 11b: the model may take the shallower parent, and the General.

`00`:111 is one paragraph and it asks for two things this package could not do.

*"If the system cannot distinguish Spring 2025 from Spring 2026 but a parent path
such as `Academics/Columbia/PHYS1401/Homework` exists, the model should choose the
approved shallower path."* Gap 11a put the ancestor back on the shortlist so the
model could name it. What was still missing is the DECISION: a model that named it
was recorded exactly as a model that named a fully-supported child, because every
one of the six decision writers set `unsupported_levels=()`. The record could not
tell the two apart, which is the one distinction §6.7 exists to publish.

*"If the only available deeper path would require inventing a term, it should
choose an approved General fallback under the meaningful parent or abstain."* The
General was in the tree, described in the prompt, and on no shortlist ever sent:
it states no expected value, joins no group and wears a label nothing matches, so
none of §6.3's six channels can reach it. The model was asked for an answer the
menu could not contain.

Both halves are the model's decision and neither is a rule. The engine offers and
describes; nothing here files a file in a General or in a parent on its own.

**The helpers are `test_p11_pipeline`'s own**, imported rather than re-made: the
model path needs a ratified prompt, a gate, a call request and a verdict, and a
second set of those would be a second opinion about what a wired run looks like.
"""
from __future__ import annotations

from dataclasses import replace

import placement.pipeline as pipeline
from placement import vocabulary as v
from p11.conftest import FIXED_CLOCK, NO_CANONICAL_RULE
from p11.p10_fixtures import (
    ExpectedValue, FREEZE_RECORD, FROZEN_TREE, _node, _profile, tree_with,
)
from p11.test_p11_pipeline import (  # noqa: F401  -- `skeleton` is a fixture
    PLACING_GROUPS, SUBJECT, _as_steps, _evidence, _model_inputs, _place,
    _verdict, skeleton,
)


def _index(conn, tree):
    """This file's own tree indexed, with P7's policy for its own plan version.

    The policy is not decoration: §8.4 refuses to answer about a file under a
    plan version nobody set an operation mode for, which is the right refusal --
    whether anything may leave the device is an answer per install and P11 will
    not assume one.
    """
    from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy

    from placement.index import build_destination_index

    set_policy(conn, Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode="hybrid",
        consent_grants=(), redaction_settings={},
        automatic_move_permissions={},
        plan_version=tree.plan_version_id, set_at=FIXED_CLOCK),
        component_version="P7-test", user_id="u1",
        reason="the scoped-General fixture's own plan version")
    build_destination_index(conn, tree, component_version="P11-test",
                            observed_at=FIXED_CLOCK, canonical=NO_CANONICAL_RULE)
    return tree


#: This file's own plan version. `skeleton` has already indexed `FROZEN_TREE`
#: under `plan-1`, and an index is keyed on `(plan_version, node_id)`: a second
#: tree filed under the same version is a second answer to "what did the person
#: approve", which SQLite refuses and which the product would be right to.
GENERAL_PLAN = "plan-general"


def _tree_of(nodes):
    nodes = tuple(replace(node, plan_version_id=GENERAL_PLAN) for node in nodes)
    return tree_with(
        plan_version_id=GENERAL_PLAN,
        nodes=nodes,
        profiles=tuple(_profile(node) for node in nodes),
        freeze_record=replace(
            FREEZE_RECORD, plan_version_id=GENERAL_PLAN,
            node_ids=tuple(node.node_id for node in nodes),
            legal_destination_ids=frozenset(
                node.node_id for node in nodes if node.accepts_placement)))


def _answering(node_id, monkeypatch, seen=None):
    """Site C wired to a verdict that names `node_id`, with the call observed."""
    def _fake_call(conn, request, **kwargs):
        if seen is not None:
            seen["allowed"] = tuple(kwargs["call_dependencies"]
                                    .allowed_vocabulary)
        return _verdict()

    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(_fake_call))


# --- the shallower approved path ---------------------------------------------------


def test_the_model_taking_the_offered_ancestor_is_a_placement_at_that_depth(
        skeleton, monkeypatch):
    """`00`:111's first sentence, end to end.

    The rules build `Academics/PHYS1401` -- the course is a direct fact match and
    a group reaches it -- and gap 11a keeps `Academics` on the shortlist beside
    it, ranked below with the reason that a folder further down the same chain is
    also on the list. The model reads both and takes the shallower one.

    That is a PLACEMENT and not an abstention. A run that answered the model's
    own choice with `no_supported_destination` would be the rules overruling the
    judgement they asked for, which is §13.5 inverted.
    """
    _answering("n-academics", monkeypatch)
    decision = _place(
        skeleton,
        inputs=_model_inputs(skeleton,
                             chosen_node_of=lambda _verdict: "n-academics"),
        evidence=_evidence(group_ids=PLACING_GROUPS,
                           semantic_neighbours=("n-academics",)))

    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == "n-academics"
    assert decision.decided_by == v.DECIDED_BY_MODEL
    # AT THAT DEPTH: the record's depth is the chosen node's own, not the leaf's.
    assert decision.decision_depth.node_depth == 0


def test_the_shallow_placement_names_the_level_the_leaf_needed(
        skeleton, monkeypatch):
    """And the record says WHY it is shallower, which is gap 11b's whole point.

    `unsupported_levels` is SPEC:401-404's field and had no writer: every
    decision this package wrote said `()`, so a file filed on `Academics` because
    its course could not be settled was byte-identical to a file filed on
    `Academics` because `Academics` was all there was. `subject` is the level the
    rules' own leaf bound and the model declined to fill.

    `supported_depth` stays at the node's own depth on purpose. The model was
    shown the deeper folder and struck it -- it judged that level unsupported --
    so claiming the evidence reached deeper would be the opposite of what
    happened.
    """
    _answering("n-academics", monkeypatch)
    decision = _place(
        skeleton,
        inputs=_model_inputs(skeleton,
                             chosen_node_of=lambda _verdict: "n-academics"),
        evidence=_evidence(group_ids=PLACING_GROUPS,
                           semantic_neighbours=("n-academics",)))

    assert decision.decision_depth.unsupported_levels == ("subject",)
    assert decision.decision_depth.supported_depth == 0
    # Said to the person in the level's own word, with no field name and no
    # section number (`84` §6).
    assert "subject" in decision.explanation
    assert "on a guess" in decision.explanation


def test_a_file_placed_on_the_leaf_names_no_unfilled_level(
        skeleton, monkeypatch):
    """The control, and the distinction the field exists to publish.

    Same corpus, same shortlist, same model -- and the model takes the deepest
    folder. Nothing was left unfilled, so the record says nothing, exactly as it
    did before a producer existed.
    """
    _answering("n-course", monkeypatch)
    decision = _place(
        skeleton,
        inputs=_model_inputs(skeleton,
                             chosen_node_of=lambda _verdict: "n-course"),
        evidence=_evidence(group_ids=PLACING_GROUPS,
                           semantic_neighbours=("n-academics",)))

    assert decision.destination.node_id == "n-course"
    assert decision.decision_depth.unsupported_levels == ()


def test_a_node_on_another_branch_is_not_a_shallow_decision(
        skeleton, monkeypatch):
    """A model that named a folder off the chain has not filed anything short.

    `n-course-shared` is not an ancestor of the leaf; it is a different home. The
    levels of a chain this node is not on would be a sentence about folders this
    file was never between, so the walk refuses to write one.
    """
    _answering("n-course-shared", monkeypatch)
    decision = _place(
        skeleton,
        inputs=_model_inputs(skeleton,
                             chosen_node_of=lambda _v: "n-course-shared"),
        evidence=_evidence(group_ids=PLACING_GROUPS,
                           semantic_neighbours=("n-academics",)))

    assert decision.destination.node_id == "n-course-shared"
    assert decision.decision_depth.unsupported_levels == ()


# --- and the scoped General --------------------------------------------------------


#: `00`:111's second sentence as a tree: a course with a General inside it, and
#: one term folder beside the General. A file that settles the course and not the
#: term is the case the design names.
def _course_with_a_general():
    nodes = (
        _node(node_id="n-academics", display_label="Academics",
              parent_node_id=None, ordinal=0, associated_group_ids=(),
              dimension_role=None, dimension=None, expected_values=(),
              refinement_disposition="shallow-by-choice",
              refinement_reason="The top of this branch is flat by design."),
        _node(node_id="n-course", display_label="PHYS1401", ordinal=1),
        _node(node_id="n-term", display_label="Spring2026",
              parent_node_id="n-course", ordinal=2, associated_group_ids=(),
              dimension_role="period", dimension="term",
              expected_values=(ExpectedValue(field="term",
                                             value="Spring2026"),)),
        _node(node_id="n-course-general", display_label="General",
              parent_node_id="n-course", ordinal=3, node_role="scoped-general",
              associated_group_ids=(), dimension_role=None, dimension=None,
              expected_values=(), refinement_disposition="shallow-by-choice",
              refinement_reason="§5.9's scoped fallback under this course."),
    )
    return _tree_of(nodes)


def test_the_parents_own_general_is_on_the_menu_when_no_leaf_is_supported(
        skeleton, monkeypatch):
    """`00`:111's second sentence: the option reaches the shortlist.

    The file settles the course and says nothing about the term, so `PHYS1401` is
    the deepest folder its evidence reaches and `Spring2026` is a level that would
    have to be invented. That is the case the design answers with the General --
    and until this the General was unreachable by every one of §6.3's channels,
    so the model was asked a question whose answer was not on the list.

    Asserted on `allowed_vocabulary`, which IS the list P8 holds the model to: an
    id absent from it comes back `INVENTED_NODE` however right it is.
    """
    tree = _index(skeleton, _course_with_a_general())
    seen = {}
    _answering("n-course", monkeypatch, seen)
    _place(skeleton,
           inputs=_model_inputs(skeleton, tree=tree,
                                plan_version=GENERAL_PLAN,
                                chosen_node_of=lambda _v: "n-course"),
           evidence=_evidence(group_ids=PLACING_GROUPS))

    assert "n-course-general" in seen["allowed"]
    assert "n-course" in seen["allowed"]


def test_the_general_is_not_offered_when_a_leaf_under_it_is_supported(
        skeleton, monkeypatch):
    """And nowhere else. `00`: "never fill a missing slot", read from the front.

    The same corpus with the term settled: `Spring2026` is now the contender and
    `PHYS1401` is ranked below it as its own ancestor. A General offered here
    would be an invitation to file the file one level short of the home its
    evidence actually reached, which is the failure the design's sentence is
    guarding against rather than an application of it.
    """
    tree = _index(skeleton, _course_with_a_general())
    seen = {}
    _answering("n-term", monkeypatch, seen)
    _place(skeleton,
           inputs=_model_inputs(skeleton, tree=tree,
                                plan_version=GENERAL_PLAN,
                                chosen_node_of=lambda _v: "n-term"),
           evidence=_evidence(
               group_ids=PLACING_GROUPS,
               facts=_evidence()["facts"] + (
                   replace(_evidence()["facts"][0], file_fact_id="ff-term",
                           field="term", value="Spring2026"),)))

    assert "n-term" in seen["allowed"]
    assert "n-course-general" not in seen["allowed"]


def test_a_file_filed_in_the_general_records_the_levels_it_did_not_fill(
        skeleton, monkeypatch):
    """The General is a shallow decision too, and the record says so.

    A General node is on the chain to nothing, so the ancestor walk finds no
    levels and would report a fully-supported child -- a file in
    `PHYS1401/General` reading exactly like a file in `PHYS1401/Spring2026`. What
    was not filled is what the folders BESIDE it bind, which is the same question
    asked of the branch instead of of a candidate.
    """
    tree = _index(skeleton, _course_with_a_general())
    _answering("n-course-general", monkeypatch)
    decision = _place(
        skeleton,
        inputs=_model_inputs(skeleton, tree=tree,
                                plan_version=GENERAL_PLAN,
                             chosen_node_of=lambda _v: "n-course-general"),
        evidence=_evidence(group_ids=PLACING_GROUPS))

    assert decision.outcome == v.PLACE
    assert decision.destination.node_role == v.SCOPED_GENERAL
    assert decision.decision_depth.unsupported_levels == ("term",)


def test_an_offline_run_never_files_anything_in_a_general(skeleton):
    """The safety of offering rather than ranking, measured.

    `Retrieval.candidates` is §6.10's deterministic path -- `00`'s own fallback
    "with no model configured" -- and a General on it would tie or beat every
    folder it stood beside, because it contradicts nothing. A run with no model
    would then file the corpus into catch-alls. As a `SetAside` it cannot: the
    scorer never sees it.
    """
    from placement.pipeline import place_file
    from p11.test_p11_pipeline import _inputs

    tree = _index(skeleton, _course_with_a_general())
    decision = place_file(skeleton, subject=SUBJECT,
                          inputs=_inputs(skeleton, tree=tree,
                                         plan_version=GENERAL_PLAN),
                          evidence=_evidence(group_ids=PLACING_GROUPS),
                          component_version="P11-test",
                          observed_at=FIXED_CLOCK)

    assert decision.destination is None or (
        decision.destination.node_id != "n-course-general")
