"""§6.11: a direct placement and a context-supported one do not demand the same trust.

    "The user should see these distinctions in the review interface, because a
    direct placement and a context-supported placement should not demand the
    same level of trust."

SPEC Open question 1 is UNRESOLVED -- whether §6.11's four labels are an
enumeration or four examples. Live `placement.vocabulary.CONFIDENCE_CLASSES` is a
closed tuple of four, so P11 has already built the closed reading. Every test
here asserts against THAT TUPLE and never against the four literals, so the day a
fifth class is ratified this file fails loudly instead of a fifth class quietly
rendering like the fourth.
"""
from __future__ import annotations

import pytest

from placement.records import (
    Ask,
    DecisionDepth,
    Destination,
    MatchingFact,
    PlacementDecision,
    PrivacyState,
    Subject,
    TwoCondition,
)
from placement.vocabulary import (
    ABSTAIN,
    ABSTAIN_NO_SUPPORTED_DESTINATION,
    ACCEPT_DIRECT,
    ASK_USER,
    BUDGET_DEFERRED,
    MARGIN_TRUE_VACUOUS,
    PLACEMENT_SCORING,
    CONFIDENCE_CLASSES,
    CONTEXT_SUPPORTED_GROUP_MATCH,
    EXACT_FACT_MATCH,
    NO_SUPPORTED_DESTINATION,
    PLACE,
    REVIEW_REQUIRED,
    SHARED_MATERIAL_DECISION,
)

from review_surface.items import (
    AFFORDANCE_NONE,
    AFFORDANCE_ONE_STEP,
    AFFORDANCE_REVIEW_REQUIRED,
    RENDER_ABSTENTION,
    RENDER_ASK,
    RENDER_BUDGET_DEFERRAL,
    RENDER_PLACEMENT,
    RENDER_SHARED_MATERIAL,
    UnrenderableDecision,
    affordance_for,
    placement_review_item,
    render_state_for,
)

T0 = "2026-08-29T00:00:00Z"

#: P11's §6.10 arithmetic, carried whole. P13 shows these figures and both
#: thresholds; it recomputes nothing, which is why this fixture is built once
#: and asserted by identity below.
TWO_CONDITION = TwoCondition(
    support_score=1.0, support_threshold=1.0, meets_threshold=True,
    margin_over_next=None, margin_threshold=0.0,
    meets_margin=MARGIN_TRUE_VACUOUS, verdict=ACCEPT_DIRECT,
    requires_review=True)


def _resolver(conn, matching_facts):
    """The citation resolver P13's composition root injects.

    Task 4 (`review_surface.citations`) is the real one; it is Wave B's and is
    not built here. `placement_review_item` takes it as a REQUIRED keyword with
    no default, so this seam refuses rather than guessing when it is absent.
    """
    return tuple((fact, f"unresolved:{fact.evidence_ref}")
                 for fact in matching_facts)


def _decision(**overrides) -> PlacementDecision:
    values = dict(
        decision_id="d1", plan_version="plan-1", supersedes=None,
        superseded_by=None, supersede_reason=None, created_at=T0,
        origin_stage="placement", returned_from=None,
        subject=Subject(kind="file", file_id="f-1", content_hash="h-1",
                        group_id=None, member_file_ids=()),
        group_plan_id=None, outcome=PLACE,
        destination=Destination(node_id="n-3", node_role="ordinary"),
        return_target=None, marked_state=None, ask=None,
        decision_depth=DecisionDepth(node_depth=3, supported_depth=3,
                                     unsupported_levels=()),
        evidence_type="direct", confidence_class=EXACT_FACT_MATCH,
        matching_facts=(), group_support=None, graph_anchors=(),
        conflicts_considered=(), alternatives=(),
        two_condition=TWO_CONDITION,
        abstention_reason=None, deferred_stage=None,
        privacy=PrivacyState(handling_class="public_low", protected=False,
                             model_eligibility="local_only",
                             consent_audit_ref=None),
        review_policy=REVIEW_REQUIRED, explanation="direct subject match",
        residual=None)
    values.update(overrides)
    return PlacementDecision(**values)


def _tree(conn):
    from tree_design.records import Node, PlanVersion
    from tree_design.store import write_node, write_plan_version

    write_plan_version(conn, PlanVersion(
        plan_version_id="plan-1", predecessor_id=None, state="draft",
        created_at=T0, cross_folder_moves=False, selection_id="sel-1"))
    for node_id, label, parent in (("n-1", "Academics", None),
                                   ("n-2", "Columbia", "n-1"),
                                   ("n-3", "2026-Spring", "n-2")):
        write_node(conn, Node(
            node_id=node_id, plan_version_id="plan-1", node_type="proposed",
            display_label=label, parent_node_id=parent, root_anchor="root",
            ordinal=0, associated_group_ids=(), explanation="fixture",
            node_role="ordinary", accepts_placement=True,
            handling_class="public_low", origin_node_id=node_id,
            template_context=None, dimension_role=None, dimension=None,
            expected_values=(), existing_path=None, disposition=None,
            refinement_disposition=None, refinement_reason=None,
            protected_movement_permitted=False))


def _decision_per_class():
    """One decision per live confidence class, built from the TUPLE."""
    built = {}
    for klass in CONFIDENCE_CLASSES:
        abstaining = klass.startswith(ABSTAIN)
        built[klass] = _decision(
            confidence_class=klass,
            outcome=ABSTAIN if abstaining else PLACE,
            destination=None if abstaining else Destination(
                node_id="n-3",
                node_role=("shared-material"
                           if klass == SHARED_MATERIAL_DECISION
                           else "ordinary")),
            abstention_reason=NO_SUPPORTED_DESTINATION if abstaining else None)
    return built


def _abstention():
    """An evidential abstention: §6.10's own state, with no ceiling involved."""
    return _decision(outcome=ABSTAIN, destination=None,
                     confidence_class=ABSTAIN_NO_SUPPORTED_DESTINATION,
                     abstention_reason=NO_SUPPORTED_DESTINATION)


def _deferral():
    """A budget deferral: the work was cut short, and nothing was concluded."""
    return _decision(outcome=ABSTAIN, destination=None,
                     confidence_class=ABSTAIN_NO_SUPPORTED_DESTINATION,
                     abstention_reason=BUDGET_DEFERRED,
                     deferred_stage=PLACEMENT_SCORING)


def _treatments(decisions, *, affordance=affordance_for,
                render_state=render_state_for):
    """What each class actually presents: a state AND a control, as one pair."""
    return {klass: (render_state(decision), affordance(decision))
            for klass, decision in decisions.items()}


def _collisions(treatments):
    """Classes that present identically. Empty is the only acceptable answer."""
    seen: dict[tuple[str, str], list[str]] = {}
    for klass, treatment in treatments.items():
        seen.setdefault(treatment, []).append(klass)
        seen[treatment].sort()
    return sorted(names for names in seen.values() if len(names) > 1)


# --------------------------------------------------------------------------
# `74` §6 A3: the named failing test and its negative twin.
# --------------------------------------------------------------------------

def test_a_direct_match_and_a_context_supported_match_do_not_present_the_same_affordance():
    """`74` §6 A3's named test. Done-means 1.

    A label alone satisfies "distinguishable" and does NOT satisfy "should not
    demand the same level of trust": two cards that read differently and accept
    identically demand identical trust. So the assertion is over the CONTROL.
    """
    direct = _decision()
    context = _decision(confidence_class=CONTEXT_SUPPORTED_GROUP_MATCH,
                        evidence_type="context-supported")
    assert affordance_for(direct) == AFFORDANCE_ONE_STEP
    assert affordance_for(context) == AFFORDANCE_REVIEW_REQUIRED
    assert affordance_for(direct) != affordance_for(context)


def test_an_item_that_renders_both_classes_with_one_word_fails():
    """`74` §6 A3's negative twin, against two sabotaged renderers.

    Sabotage 1 collapses the CONTROL: every class accepts in one step, which is
    the version of this feature that ships as a label and changes nothing.
    Sabotage 2 collapses the STATE: one word for every class.

    Both must be reported as collisions, and the real pair must report none.
    A distinctness check asserted only against the real implementation passes
    just as well when it compares nothing.
    """
    decisions = _decision_per_class()

    assert _collisions(_treatments(decisions)) == []

    one_control = _treatments(decisions,
                              affordance=lambda decision: AFFORDANCE_ONE_STEP)
    assert _collisions(one_control), (
        "a renderer that offers one-step acceptance for every class must be "
        "reported as collapsing §6.11's distinction")

    one_word = _treatments(decisions,
                           render_state=lambda decision: RENDER_PLACEMENT,
                           affordance=lambda decision: AFFORDANCE_ONE_STEP)
    assert len(_collisions(one_word)) == 1
    assert sorted(_collisions(one_word)[0]) == sorted(CONFIDENCE_CLASSES)


def test_every_confidence_class_has_a_distinguishable_treatment():
    """Asserted against P11's live tuple, so a fifth class fails here loudly
    rather than quietly rendering like the fourth. SPEC Open question 1 is OPEN."""
    treatments = _treatments(_decision_per_class())
    assert len(set(treatments.values())) == len(CONFIDENCE_CLASSES), (
        f"two confidence classes render identically: {treatments}")


# --------------------------------------------------------------------------
# The other two contractual rendering obligations.
# --------------------------------------------------------------------------

def test_an_abstention_and_a_budget_deferral_are_visibly_different_states():
    """Done-means 2. Neither renders as a placement."""
    abstention = _abstention()
    deferral = _deferral()
    assert render_state_for(abstention) == RENDER_ABSTENTION
    assert render_state_for(deferral) == RENDER_BUDGET_DEFERRAL
    assert render_state_for(abstention) != render_state_for(deferral)
    for decision in (abstention, deferral):
        assert render_state_for(decision) != RENDER_PLACEMENT


def test_a_deferral_is_read_before_its_abstention_reason():
    """Reading `abstention_reason` first would render every deferral as an
    ordinary abstention, which is the conflation Done-means 2 forbids.

    P11's own record already refuses the mixed shape -- `deferred_stage` is
    present exactly when the reason is `budget_deferred` -- so the state has to
    be forced past that validation to test the ORDER at all. Both halves are
    asserted: that P11 refuses it, and that P13 reads the more specific claim
    first anyway. P13 does not rely on an upstream invariant it cannot see.
    """
    from placement.records import MalformedPlacementRecord

    with pytest.raises(MalformedPlacementRecord):
        _decision(outcome=ABSTAIN, destination=None,
                  confidence_class=ABSTAIN_NO_SUPPORTED_DESTINATION,
                  abstention_reason=NO_SUPPORTED_DESTINATION,
                  deferred_stage=PLACEMENT_SCORING)

    forced = _deferral()
    object.__setattr__(forced, "abstention_reason", NO_SUPPORTED_DESTINATION)
    assert render_state_for(forced) == RENDER_BUDGET_DEFERRAL


def test_no_accept_anyway_affordance_is_offered_over_a_deferred_subject():
    """Cost exhaustion never turns into lower-quality automatic classification,
    and it never turns into a lower-quality PRESENTATION either."""
    assert affordance_for(_deferral()) == AFFORDANCE_NONE


def test_an_ask_user_decision_reaches_a_surface_and_is_not_auto_resolved():
    """Done-means 4."""
    ask = _decision(
        outcome=ASK_USER, destination=None,
        # P11 requires a confidence class on EVERY decision, and §6.11's four
        # are placement labels -- none of them describes a question. The
        # abstain label is the only member that does not assert a placement.
        # Flagged, not resolved: see the report on this task.
        confidence_class=ABSTAIN_NO_SUPPORTED_DESTINATION,
        ask=Ask(question="Which application packet?",
                options=("Columbia", "NYU")))
    assert render_state_for(ask) == RENDER_ASK
    assert affordance_for(ask) == AFFORDANCE_NONE


def test_a_shared_material_decision_reaches_a_surface_and_is_not_hidden():
    """Done-means 4."""
    shared = _decision(confidence_class=SHARED_MATERIAL_DECISION,
                       destination=Destination(node_id="n-3",
                                               node_role="shared-material"))
    assert render_state_for(shared) == RENDER_SHARED_MATERIAL


def test_the_destination_is_a_label_chain_and_never_a_path(p13_conn):
    _tree(p13_conn)
    item = placement_review_item(p13_conn, _decision(),
                                 resolve_citations=_resolver)
    assert item.destination_label_chain == (
        "Academics", "Columbia", "2026-Spring")
    for label in item.destination_label_chain:
        assert "/" not in label


def test_the_levels_deliberately_unfilled_are_named_and_are_not_a_second_role(p13_conn):
    """MINOR 6: there is no `destination.kind`; §6.7's deliberately shallower
    parent is a non-empty `decision_depth.unsupported_levels[]` naming the levels
    left unfilled, and that is what P13 renders."""
    _tree(p13_conn)
    decision = _decision(decision_depth=DecisionDepth(
        node_depth=2, supported_depth=2,
        unsupported_levels=("work_type", "term")))
    item = placement_review_item(p13_conn, decision,
                                 resolve_citations=_resolver)
    assert item.levels_deliberately_unfilled == ("work_type", "term")
    assert item.destination_node_role == "ordinary"
    assert not hasattr(item, "destination_kind")


def test_the_explanation_and_its_citations_arrive_together(p13_conn):
    """So §6.4's "must not claim evidence the file does not carry" is checkable
    by the person reading it. The explanation is never carried alone."""
    _tree(p13_conn)
    decision = _decision(matching_facts=(
        MatchingFact(file_fact_id="ff-1", field="subject", value="PHYS1401",
                     reliability="direct", evidence_ref="obs-1"),))
    item = placement_review_item(p13_conn, decision,
                                 resolve_citations=_resolver)
    assert item.explanation == "direct subject match"
    assert len(item.cited_facts) == len(decision.matching_facts)
    assert item.cited_facts[0][0].file_fact_id == "ff-1"


def test_the_citation_resolver_is_injected_and_absent_means_refuse(p13_conn):
    """"Absent means refuse, never guess." P13 resolves no citation of its own;
    `review_surface.citations` is Wave B's and the seam has NO default, so a
    caller that forgot it gets a TypeError rather than an item with no evidence."""
    import inspect

    _tree(p13_conn)
    parameter = inspect.signature(placement_review_item).parameters[
        "resolve_citations"]
    assert parameter.default is inspect.Parameter.empty
    with pytest.raises(TypeError):
        placement_review_item(p13_conn, _decision())


def test_a_place_decision_with_no_destination_is_refused_not_rendered_blank(p13_conn):
    """Rendering a blank destination would present a placement to nowhere as a
    placement.

    P11's record refuses this shape at construction, so the state has to be
    forced past that validation to reach P13 at all. Both halves are asserted,
    for the same reason as the deferral ordering above: P13 does not rely on an
    upstream invariant it cannot see, and every decision P13 renders in a replay
    bundle was rebuilt by something other than P11's constructor.
    """
    from placement.records import MalformedPlacementRecord

    with pytest.raises(MalformedPlacementRecord):
        _decision(destination=None)

    forced = _decision()
    object.__setattr__(forced, "destination", None)
    with pytest.raises(UnrenderableDecision):
        placement_review_item(p13_conn, forced, resolve_citations=_resolver)


def test_the_item_carries_the_two_condition_figures_whole_and_computes_nothing(p13_conn):
    """§6.11 requires the FIGURES AND BOTH THRESHOLDS to be presentable. P13
    shows P11's arithmetic; it does not repeat it. There is no score in this
    module, which the guard below states by introspection."""
    import ast
    import pathlib

    import review_surface.items as module

    _tree(p13_conn)
    item = placement_review_item(p13_conn, _decision(),
                                 resolve_citations=_resolver)
    assert item.two_condition is TWO_CONDITION

    tree = ast.parse(pathlib.Path(module.__file__).read_text())
    scoring_ops = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod,
                   ast.Pow)
    ordering_ops = (ast.Lt, ast.LtE, ast.Gt, ast.GtE)
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, scoring_ops):
            offenders.append(f"{node.lineno} arithmetic")
        if isinstance(node, ast.Compare) and any(
                isinstance(op, ordering_ops) for op in node.ops):
            offenders.append(f"{node.lineno} comparison")
    assert offenders == [], (
        f"items.py scores or ranks at {offenders}; P13 has no scoring or "
        "classification code at all -- equality, membership and identity are "
        "how it reads a vocabulary, and ordering is how it would rank one")
