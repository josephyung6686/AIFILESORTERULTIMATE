"""§6.11's trust distinction, on a screen. It was rendered nowhere.

    "The user should see these distinctions in the review interface, because a
    direct placement and a context-supported placement should not demand the
    same level of trust."

`review_surface.items` implements that as a CONTROL and not as a label --
`affordance_for` gives a context-supported match a different acceptance
affordance from an exact fact match, because "two cards that read differently and
accept identically demand identical trust". Nothing called it. What `src/cli.py`
prints for a placement is a destination and a sentence, identical in shape for
every confidence class, so the distinction the design calls contractual was
invisible to the person it was written for.

Two properties carry these tests, and each has a sabotage of its own:

* **Two confidence classes do not read alike.** The sabotage is the shipped
  report: one line per placement with the destination on it and nothing about how
  it was reached.
* **A file that may not be named is COUNTED, never dropped and never named.**
  `name_for` returning `None` is the composition root saying this subject's name
  is not for this screen, and the renderer has no path that receives a protected
  name and hides it -- it never asks for one.
"""
from __future__ import annotations

from evidence_shape.observation import Location, Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from placement.records import (
    DecisionDepth,
    Destination,
    MatchingFact,
    PlacementDecision,
    PrivacyState,
    Subject,
    TwoCondition,
)
from placement.vocabulary import (
    ACCEPT_DIRECT,
    CONTEXT_SUPPORTED_GROUP_MATCH,
    EXACT_FACT_MATCH,
    MARGIN_TRUE_VACUOUS,
    PLACE,
    REVIEW_REQUIRED,
)

from review_surface.citations import resolve_matching_facts

from review_run.review import placement_lines

T0 = "2026-08-29T00:00:00Z"

TWO_CONDITION = TwoCondition(
    support_score=1.0, support_threshold=1.0, meets_threshold=True,
    margin_over_next=None, margin_threshold=0.0,
    meets_margin=MARGIN_TRUE_VACUOUS, verdict=ACCEPT_DIRECT,
    requires_review=True)


#: P13's REAL resolver, not a stand-in. The composition root injects exactly this
#: function, and a fixture returning strings would leave the renderer's
#: unresolved count agreeing with the fixture and disagreeing with production --
#: which is the shape that hid a live defect on this very line.
_resolver = resolve_matching_facts


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
            handling_class="public_low", origin_node_id=node_id))


def _lines(conn, decisions, *, name_for=lambda decision: "week 3.pdf"):
    return placement_lines(conn, decisions, name_for=name_for,
                           resolve_citations=_resolver)


def test_an_exact_match_and_a_context_supported_match_do_not_read_alike(
        p13_conn):
    """§6.11's contractual distinction, as the difference between two blocks.

    The two decisions differ in exactly one field -- `confidence_class` -- and
    the whole rendered block is asserted for each, because a test that only
    compared the two would pass for a renderer that printed the class name and
    offered the same control under both. The control is the half §6.11 is about.
    """
    _tree(p13_conn)
    direct = _decision()
    supported = _decision(decision_id="d2",
                          confidence_class=CONTEXT_SUPPORTED_GROUP_MATCH)

    assert _lines(p13_conn, (direct,)) == (
        "",
        "How each placement was reached, and how much it asks of you:",
        "  week 3.pdf",
        "    placement_state, by exact fact match -- one_step_accept",
        "    into: Academics > Columbia > 2026-Spring",
        "    because: direct subject match",
        "    evidence: 0 cited, 0 of them unresolved",
    )
    assert _lines(p13_conn, (supported,)) == (
        "",
        "How each placement was reached, and how much it asks of you:",
        "  week 3.pdf",
        "    placement_state, by context-supported group match "
        "-- review_each_before_accepting",
        "    into: Academics > Columbia > 2026-Spring",
        "    because: direct subject match",
        "    evidence: 0 cited, 0 of them unresolved",
    )


def test_the_shipped_report_shape_cannot_tell_the_two_apart(p13_conn):
    """The sabotage, and it is the live renderer rather than an invented one.

    `src/cli.py` heads a placement with its destination and its sentence. Run
    over the same two decisions that differ in confidence class, it produces two
    identical strings -- which is the whole finding, and is why a label alone
    would not have closed §6.11 either.
    """
    _tree(p13_conn)
    direct = _decision()
    supported = _decision(decision_id="d2",
                          confidence_class=CONTEXT_SUPPORTED_GROUP_MATCH)

    def shipped(decision) -> str:
        """The sabotage: destination and sentence, as the report prints them."""
        return f"2026-Spring -- {decision.explanation}"

    assert shipped(direct) == shipped(supported)
    assert _lines(p13_conn, (direct,)) != _lines(p13_conn, (supported,))


def test_a_subject_this_screen_may_not_name_is_counted_and_never_named(
        p13_conn):
    """The standing rule: marked and counted, never opened, never omitted.

    `name_for` answering `None` is the composition root saying this subject's
    name is not for this screen -- which is what `--show-protected` already
    decides elsewhere. The renderer never receives the name, so it has no path
    that receives protected content and then hides it; it has a path that
    declines to ask. The whole tuple is asserted: a renderer that silently
    dropped the row would satisfy "the name is absent" and would be the silent
    omission the same rule forbids.
    """
    _tree(p13_conn)
    assert _lines(p13_conn, (_decision(),), name_for=lambda decision: None) == (
        "",
        "How each placement was reached, and how much it asks of you:",
        "  1 file is not named on this screen. Its placement is still counted "
        "and it is still yours to review.",
    )


def test_a_named_file_and_an_unnamed_one_are_both_accounted_in_one_pass(
        p13_conn):
    """The two halves in one call, so neither can be produced by dropping the other.

    A renderer that emitted the aggregate INSTEAD of the named rows, or the named
    rows instead of the aggregate, passes one of the two tests above. It cannot
    pass this one.
    """
    _tree(p13_conn)
    decisions = (
        _decision(),
        _decision(decision_id="d2",
                  subject=Subject(kind="file", file_id="f-2",
                                  content_hash="h-2", group_id=None,
                                  member_file_ids=())),
    )
    lines = _lines(p13_conn, decisions,
                   name_for=lambda decision: ("week 3.pdf"
                              if decision.subject.file_id == "f-1" else None))
    assert lines[2] == "  week 3.pdf"
    assert lines[-1] == (
        "  1 file is not named on this screen. Its placement is still counted "
        "and it is still yours to review.")


HASH_A = "a" * 64


def _seed_observation(conn) -> str:
    """One real observation, so a citation that DOES resolve exists to contrast."""
    record_run(conn, ExtractionRun(
        run_id="run-1", file_id="f-1", content_hash=HASH_A,
        extractor_name="fixture-pdf", extractor_version="1",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=T0, observation_count=1,
        coverage=None, finished_at=T0, failure_reason=None))
    observation = Observation(
        file_id="f-1", content_hash=HASH_A, extractor_name="fixture-pdf",
        extractor_version="1", source_type="text_document",
        raw_value="PHYS1401",
        location=Location(zone="body", container_path=(), text_span=None,
                          time_span=None, region=None),
        occurrence_count=1, observed_at=T0, reliability="direct",
        run_id="run-1", normalized_value="PHYS1401",
        context_before="Course ", context_after=" Spring 2026",
        context_truncated=False, confidence=None, signal_tier=None)
    record_observation(conn, observation)
    return observation.observation_key


def _fact(evidence_ref: str) -> MatchingFact:
    return MatchingFact(file_fact_id="ff-1", field="subject", value="PHYS1401",
                        reliability="direct", evidence_ref=evidence_ref)


def test_a_cited_fact_that_would_not_resolve_is_reported_as_unresolved(
        p13_conn):
    """Done-means 3: an unresolvable citation is rendered, not dropped.

    `review_surface.citations` returns a record for every key precisely so an
    explanation with three citations does not silently become one with two. That
    property is only visible to a person if the renderer says how many did not
    resolve, so the count is on the line rather than in the record alone.

    BOTH states are driven, through the REAL resolver, because the count was
    once taken off `str(resolution)` and was right only about a fixture that
    returned strings: `ResolvedCitation`'s `str()` begins "ResolvedCitation(",
    so every citation in production counted as resolved and the line said "0 of
    them unresolved" over a broken one. A test that only ever cites a missing
    key cannot see that; a test that cites one of each can.
    """
    _tree(p13_conn)
    resolvable = _seed_observation(p13_conn)

    missing = _decision(matching_facts=(_fact("obs-does-not-exist"),))
    assert _lines(p13_conn, (missing,))[-1] == (
        "    evidence: 1 cited, 1 of them unresolved")

    found = _decision(matching_facts=(_fact(resolvable),))
    assert _lines(p13_conn, (found,))[-1] == (
        "    evidence: 1 cited, 0 of them unresolved")

    both = _decision(matching_facts=(_fact(resolvable),
                                     _fact("obs-does-not-exist")))
    assert _lines(p13_conn, (both,))[-1] == (
        "    evidence: 2 cited, 1 of them unresolved")
