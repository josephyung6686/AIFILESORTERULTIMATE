"""§8.5: a review screen reconstructed for a past run, from a bundle alone.

`74` §6 B14's named test is
`test_every_surface_renders_from_a_replay_bundle_with_no_live_database` and its
negative twin is `test_a_surface_that_reads_outside_the_bundle_is_detected`.

P13 SPEC:400-407 sets out what P13 owes P2 and what it does not: it emits no
`stage_output` -- it is not one of §8.5's ten attribution stages and an eleventh
would corrupt P2's closed enumeration -- and it does owe that every surface is
renderable from a replay bundle, with `presented_state_ref` serializing into and
re-asserting from one.

The twin is a real tripwire, not a promise: it drives SQLite's own authorizer over
a builder that genuinely reads outside the bundle, so the guard is shown firing
rather than merely finding nothing.
"""
from __future__ import annotations

import json

import pytest

from database_agent.db import create_schema, open_database
from placement.groups import ExcludedOutlier, GroupPlan
from placement.records import (
    DecisionDepth,
    Destination,
    PlacementDecision,
    PrivacyState,
    Subject,
    TwoCondition,
)
from placement.residual import ResidualSet
from placement.vocabulary import (
    ACCEPT_DIRECT,
    EXACT_FACT_MATCH,
    MARGIN_TRUE_VACUOUS,
    PLACE,
    REVIEW_REQUIRED,
    ROUTED_TO_NODE,
)
from placement.schema import create_placement_schema
from privacy.display import RedactionSettings
from tree_design.records import Node, PlanVersion
from tree_design.schema import P10_TABLES, create_tree_schema
from tree_design.store import write_node, write_plan_version

from review_surface.citations import resolve_matching_facts
from review_surface.items import group_plan_review_item, placement_review_item
from review_surface.labels import label_chain_for_version
from review_surface.locations import (
    CURRENT_LOCATION,
    LocationElement,
    six_state_view,
)
from review_surface.presentation import record_presentation
from review_surface.replay import (
    NoStageOutputHere,
    NotRenderableFromABundle,
    assert_reads_only,
    deserialize_presented_state,
    reassert_presented_state,
    serialize_presented_state,
    stage_output,
    tables_read,
)
from review_surface.residual import residual_screen
from review_surface.schema import REVIEW_TABLES, create_review_schema
from review_surface.vocabulary import SURFACE_PLACEMENT

T0 = "2026-08-29T00:00:00Z"
SHOWN = RedactionSettings(names="shown", previews="shown", thumbnails="shown",
                          ocr_text="shown", location_data="shown")

#: The tables a P13 replay bundle carries: P10's tree, because every destination
#: is rendered through its ancestor chain, and P13's own three. Taken from P10's
#: own published list rather than named here, so a table P10 adds joins the bundle
#: instead of tripping the guard for the wrong reason. Nothing else -- a surface
#: reaching for a live `files` row is what the twin below detects.
BUNDLE_TABLES: tuple[str, ...] = P10_TABLES + REVIEW_TABLES

TWO_CONDITION = TwoCondition(
    support_score=1.0, support_threshold=1.0, meets_threshold=True,
    margin_over_next=None, margin_threshold=0.0,
    meets_margin=MARGIN_TRUE_VACUOUS, verdict=ACCEPT_DIRECT,
    requires_review=True)


def _tree(conn):
    write_plan_version(conn, PlanVersion(
        plan_version_id="plan-1", predecessor_id=None, state="draft",
        created_at=T0, cross_folder_moves=False, selection_id="sel-1"))
    for node_id, label, parent in (("n-1", "Applications", None),
                                   ("n-2", "Columbia", "n-1"),
                                   ("n-9", "Review Queue", None)):
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


def _decision(file_id="f-1", decision_id="d1") -> PlacementDecision:
    return PlacementDecision(
        decision_id=decision_id, plan_version="plan-1", supersedes=None,
        superseded_by=None, supersede_reason=None, created_at=T0,
        origin_stage="placement", returned_from=None,
        subject=Subject(kind="file", file_id=file_id, content_hash="h",
                        group_id="g-1", member_file_ids=()),
        group_plan_id="gp-1", outcome=PLACE,
        destination=Destination(node_id="n-2", node_role="ordinary"),
        return_target=None, marked_state=None, ask=None,
        decision_depth=DecisionDepth(node_depth=2, supported_depth=2,
                                     unsupported_levels=()),
        evidence_type="direct", confidence_class=EXACT_FACT_MATCH,
        matching_facts=(), group_support=None, graph_anchors=(),
        conflicts_considered=(), alternatives=(),
        two_condition=TWO_CONDITION, abstention_reason=None,
        deferred_stage=None,
        privacy=PrivacyState(handling_class="public_low", protected=False,
                             model_eligibility="local_only",
                             consent_audit_ref=None),
        review_policy=REVIEW_REQUIRED, explanation="direct match",
        residual=None)


def _residual_set() -> ResidualSet:
    count = 3
    return ResidualSet(
        set_id="set-1", plan_version="plan-1",
        label="screenshots with no accepted project", file_count=count,
        representative_examples=("f-a", "f-b"),
        file_type_distribution=(("png", count),),
        age_range=("2024-03", "2026-08"),
        evidence_availability="OCR text available for 2 of 3",
        sensitivity_status="none flagged", protected=False,
        weak_graph_neighbours=("none",),
        reason_not_placed="no fact reached a legal destination",
        member_file_ids=tuple(f"f-{n}" for n in range(count)))


@pytest.fixture()
def live(conn):
    """The database the original run happened in."""
    create_schema(conn)
    create_tree_schema(conn)
    create_placement_schema(conn)
    create_review_schema(conn)
    _tree(conn)
    return conn


@pytest.fixture()
def bundle(tmp_path):
    """A separate database standing in for the replay bundle. No live records."""
    replay = open_database(tmp_path / "bundle.sqlite")
    create_schema(replay)
    create_tree_schema(replay)
    create_review_schema(replay)
    _tree(replay)
    yield replay
    replay.close()


def test_every_surface_renders_from_a_replay_bundle_with_no_live_database(
        live, bundle):
    """`74` §6 B14's named test, and Done-means 23 in both its clauses.

    The presentation is minted in the live database, serialized, and re-asserted
    into a bundle database that has never seen the run -- and comes back with the
    same ref, because the ref is a digest of the moment rather than a row id.
    Then four surfaces are built entirely from the bundle, each under SQLite's own
    authorizer, so "renders from a bundle" is a checked fact rather than a claim.
    """
    state = record_presentation(
        live, surface=SURFACE_PLACEMENT, subject_ref="d1",
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=("obs-1", "obs-2"), user_id="jy",
        component_version="p13-1", rendered_at=T0)
    payload = json.loads(json.dumps(serialize_presented_state(state)))
    assert deserialize_presented_state(payload) == state

    replayed = reassert_presented_state(bundle, payload)
    assert replayed.presented_state_ref == state.presented_state_ref
    assert replayed.redaction_policy == state.redaction_policy
    assert replayed.evidence_refs == state.evidence_refs

    decision = _decision()
    item = assert_reads_only(
        bundle, BUNDLE_TABLES,
        lambda: placement_review_item(bundle, decision,
                                      resolve_citations=lambda c, f: ()))
    assert item.destination_label_chain == ("Applications", "Columbia")

    plan = GroupPlan(
        group_plan_id="gp-1", plan_version="plan-1", group_id="g-1",
        shared_parent_node_id="n-2",
        member_decisions=(_decision(), _decision("f-2", "d2")),
        excluded_outliers=(ExcludedOutlier(
            file_id="f-3", conflicting_fact="target_school=NYU",
            evidence_ref="obs-nyu", routed_to=ROUTED_TO_NODE,
            node_id="n-9"),))
    group_item = assert_reads_only(
        bundle, BUNDLE_TABLES,
        lambda: group_plan_review_item(
            bundle, plan, resolve_citations=lambda c, f: ()))
    assert group_item.shared_parent_label_chain == ("Applications", "Columbia")
    assert group_item.excluded_outliers[0][1] == ("Review Queue",)

    chain = assert_reads_only(
        bundle, BUNDLE_TABLES,
        lambda: label_chain_for_version(bundle, plan_version="plan-1",
                                        node_id="n-2"))
    assert chain == ("Applications", "Columbia")

    # Two surfaces that touch no table at all still render, which is the point:
    # they are projections over records the bundle already carries.
    screen = residual_screen((_residual_set(),), plan_version="plan-1")
    assert screen.cards[0].set_id == "set-1"
    view = six_state_view(
        subject_ref="d1", plan_version="plan-1",
        current=LocationElement(
            state=CURRENT_LOCATION, label_chain=("Downloads",), node_id=None,
            relationship_ref=None, shared_policy=None,
            opaque_current_location="downloads", explanation="where it is now"),
        filed_home=None, also_related_to=(), shared_material=(), historical=(),
        possible=())
    assert view.by_state(CURRENT_LOCATION)[0].label_chain == ("Downloads",)


def test_a_surface_that_reads_outside_the_bundle_is_detected(live, bundle):
    """`74` §6 B14's negative twin, driven until the tripwire fires.

    A surface reaching for a live row outside the bundle renders today's answer
    under a past run's heading -- which looks like a faithful reconstruction and
    is not one. The authorizer records what was actually read, so the check is a
    fact about the query rather than a promise about the code.
    """
    def reads_outside():
        return bundle.execute("SELECT count(*) FROM files").fetchone()

    with pytest.raises(NotRenderableFromABundle) as caught:
        assert_reads_only(bundle, BUNDLE_TABLES, reads_outside)
    assert "files" in str(caught.value)

    # The same builder is fine when the bundle actually carries that table, so
    # the guard is about the BUNDLE's contents and not about a table denylist.
    assert assert_reads_only(bundle, BUNDLE_TABLES + ("files",), reads_outside)

    # And the mechanism reports what it saw, in both directions.
    _, read = tables_read(bundle, reads_outside)
    assert "files" in read
    _, none_read = tables_read(bundle, lambda: None)
    assert none_read == ()

    # The authorizer is removed afterwards, so a later query on this connection
    # behaves normally. An authorizer left installed is a silent global change.
    assert bundle.execute("SELECT count(*) FROM tree_nodes").fetchone()[0] == 3


def test_a_tampered_bundle_payload_does_not_re_assert(live, bundle):
    """The ref covers the redaction policy, which is the alteration §8.4 makes
    consequential. A payload whose ref does not match its content is not that
    moment, and re-asserting it would put a past screen under a policy the user
    never saw it under."""
    state = record_presentation(
        live, surface=SURFACE_PLACEMENT, subject_ref="d1",
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=("obs-1",), user_id="jy", component_version="p13-1",
        rendered_at=T0)
    payload = serialize_presented_state(state)
    payload["redaction_policy"] = dict(payload["redaction_policy"])
    payload["redaction_policy"]["names"] = "redacted"
    with pytest.raises(NotRenderableFromABundle):
        reassert_presented_state(bundle, payload)
    # Nothing was written by the refused re-assertion.
    assert bundle.execute(
        "SELECT count(*) AS c FROM review_presentations").fetchone()["c"] == 0


def test_re_asserting_the_same_payload_twice_is_idempotent(live, bundle):
    """A bundle replayed twice is the same bundle. P13's tables refuse UPDATE, so
    a second insert of one moment would be an error rather than a no-op."""
    state = record_presentation(
        live, surface=SURFACE_PLACEMENT, subject_ref="d1",
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=("obs-1",), user_id="jy", component_version="p13-1",
        rendered_at=T0)
    payload = serialize_presented_state(state)
    first = reassert_presented_state(bundle, payload)
    second = reassert_presented_state(bundle, payload)
    assert first.presented_state_ref == second.presented_state_ref
    assert bundle.execute(
        "SELECT count(*) AS c FROM review_presentations").fetchone()["c"] == 1


def test_p13_emits_no_stage_output():
    """P13 SPEC:400-404: inventing an eleventh stage would corrupt P2's closed
    `stage_id` enumeration."""
    with pytest.raises(NoStageOutputHere) as caught:
        stage_output()
    assert "eleventh" in str(caught.value)
