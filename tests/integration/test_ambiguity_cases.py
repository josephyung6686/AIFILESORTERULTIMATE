"""Ambiguity and overlap: the cases where two domains claim one file.

Every persona pass so far assumed one person living one life. This suite drives
the REAL code for the cases where that assumption breaks: a transcript two
application packets both want, a passport a visa application needs, a CAD drawing
that is an engineering deliverable and a contract exhibit, a résumé that is mine
on Monday and a candidate's on Tuesday.

The corpus said where the overlap lives before any of this was written: 358 rows
in `planning/domains/nodes/*.json` carry 2409 `collides_with` edges (1339 of them
crossing schemas) and 309 `also_holds_with` edges (277 crossing schemas). This
file does not restate those edges. It asks whether the built system honours them.

Nothing here is a regression test for a rule the product already keeps. Each test
is a claim about what a real person would see, and several of them PASS by
asserting that the product does the wrong thing — the assertion is the evidence,
and the day one starts failing is the day that case got fixed.

Companion document: `planning/55-AMBIGUITY-AND-OVERLAP.md`.
"""
from __future__ import annotations

import dataclasses
import json
import pathlib
import re

import pytest

# --- P10, the tree side ---------------------------------------------------------
from tree_design.candidates import vertical_options
from tree_design.materialise import (
    MaterialisationRefused,
    materialise_branch,
    project_branch_nodes,
)
from tree_design.records import Node
from tree_design.routing import (
    BranchContext,
    CompositionCandidate,
    RoutingReport,
    evaluate_composition,
)
from tree_design.templates import CompositionConflict
from tree_design.upstream import AcceptedGroup, GroupMember
from tree_design.validation import run_checks
from tree_design.vocabulary import ORDINARY, PROPOSED

# --- P11, the placement side ----------------------------------------------------
from placement import vocabulary as pv
from placement.config import PlacementLimits, SupportPolicy
from placement.index import build_destination_index, entry_for
from placement.records import MatchingFact, Subject
from placement.retrieval import ACCEPTED_GROUP, DIRECT_FACT, retrieve
from placement.scoring import assess

REPO = pathlib.Path(__file__).resolve().parents[2]
SRC = REPO / "src"


# --------------------------------------------------------------------------------
# Shared fixtures and helpers
# --------------------------------------------------------------------------------


@pytest.fixture()
def p10_conn(conn, tmp_path):
    """P1's tables plus every upstream table the tree side reads."""
    from evidence_shape.schema import create_evidence_schema
    from facts.fields import create_fields
    from privacy.schema import create_privacy_schema
    from scan_agent.schema import create_scan_schema

    create_fields(conn)
    create_scan_schema(conn)
    create_privacy_schema(conn)
    create_evidence_schema(conn)
    return conn


@pytest.fixture()
def p11_conn(conn):
    from database_agent.db import create_schema
    from eval_harness.store import create_eval_schema
    from facts.fields import create_fields
    from grouping.schema import create_grouping_schema
    from placement.schema import create_placement_schema
    from privacy.schema import create_privacy_schema

    create_schema(conn)
    create_eval_schema(conn)
    create_grouping_schema(conn)
    create_fields(conn)
    create_privacy_schema(conn)
    create_placement_schema(conn)
    return conn


CLOCK = "2026-08-28T00:00:00Z"

LIMITS = PlacementLimits(
    max_retrieved_neighbors=8, max_local_graph_neighborhood=8,
    max_candidate_cluster_size=6, max_residual_files_per_batch=50,
    max_dossier_tokens=4000, max_llm_calls_per_thousand_files=100,
    max_cost_per_scan=5,
)

# The same policy `tests/p11/test_p11_scoring.py` derives: `_MAX_WEIGHT` is 7, so a
# direct-fact-only candidate scores 3/7 = 0.4285…, an accepted-group-only candidate
# scores 2/7 = 0.2857…, and a threshold of 0.4 separates them.
POLICY = SupportPolicy(policy_id="ambiguity-v1", support_scale_max=1.0,
                       minimum_support_threshold=0.4, margin_threshold=0.2)


def _src_text() -> dict[str, str]:
    """Every `src/**/*.py` file, for the producer-and-reader scans below.

    A grep in prose is an opinion. A grep in a test is evidence that keeps
    working: the day someone wires one of these concepts up, the test that says
    "nothing produces it" fails and has to be deleted deliberately.
    """
    return {
        str(path.relative_to(REPO)): path.read_text(encoding="utf-8")
        for path in sorted(SRC.rglob("*.py"))
    }


# --------------------------------------------------------------------------------
# CASE 1 — Transcript.pdf belongs to two application packets (§6.9's own example)
# --------------------------------------------------------------------------------


def _application_tree():
    """A frozen tree shaped like §6.9: two institutions and a shared branch.

    `applications.undergraduate-packet` (launch=full) recommends
    target_university first, and its `collides_with` row against
    `academic.transcripts-credentials` is the one that names this exact file:
    "One transcript is both an official academic record and a packet supporting
    document." The shared branch is §6.9's own `Applications/Shared Application
    Materials`.
    """
    from p11.p10_fixtures import FROZEN_TREE, ExpectedValue, tree_with

    base = FROZEN_TREE.nodes[0]
    columbia = dataclasses.replace(
        base, node_id="n-columbia", origin_node_id="n-columbia",
        display_label="Columbia", ordinal=1, associated_group_ids=("g-columbia",),
        dimension="target_university", dimension_role="target_university",
        expected_values=(
            ExpectedValue(field="target_university", value="Columbia"),),
        explanation="Nine files in the accepted Columbia packet name it.")
    duke = dataclasses.replace(
        columbia, node_id="n-duke", origin_node_id="n-duke", display_label="Duke",
        ordinal=2, associated_group_ids=("g-duke",),
        expected_values=(ExpectedValue(field="target_university", value="Duke"),),
        explanation="Seven files in the accepted Duke packet name it.")
    shared = dataclasses.replace(
        base, node_id="n-shared", origin_node_id="n-shared",
        display_label="Shared Application Materials", ordinal=3,
        associated_group_ids=("g-shared",),
        node_role=pv.SHARED_MATERIAL, dimension=None, dimension_role=None,
        expected_values=(),
        explanation="§6.9's shared branch: material every packet reuses.",
        refinement_disposition="shallow-by-choice",
        refinement_reason="Shared material is one level by design (§6.9).")

    nodes = (columbia, duke, shared, FROZEN_TREE.nodes[3])
    profiles = []
    for node in nodes:
        origin = FROZEN_TREE.profiles[0]
        profiles.append(dataclasses.replace(
            origin, node_id=node.node_id, display_label=node.display_label,
            expected_values=node.expected_values,
            accepted_group_ids=node.associated_group_ids,
            template_fields=("target_university",), anchor_excerpts=(),
            representative_files=("f-transcript",),
            restrictions=dataclasses.replace(
                origin.restrictions, node_role=node.node_role,
                accepts_placement=node.accepts_placement,
                handling_class=node.handling_class,
                disposition=node.disposition)))
    return tree_with(
        nodes=nodes, profiles=tuple(profiles),
        freeze_record=dataclasses.replace(
            FROZEN_TREE.freeze_record,
            node_ids=tuple(n.node_id for n in nodes),
            legal_destination_ids=frozenset(
                n.node_id for n in nodes if n.accepts_placement)))


def _transcript_facts():
    """A transcript accepted into BOTH packets: two live values, one field.

    §6.9: "If `Transcript.pdf` has accepted membership in both Columbia and Duke
    application packets but contains no institution-specific fact…". Here it does
    carry both, which is the harder and commoner shape: the packet memberships
    wrote an addressee each.
    """
    return (
        MatchingFact(file_fact_id="ff-col", field="target_university",
                     value="Columbia", reliability=pv.DIRECT, evidence_ref="obs-1"),
        MatchingFact(file_fact_id="ff-duke", field="target_university",
                     value="Duke", reliability=pv.DIRECT, evidence_ref="obs-2"),
    )


def test_two_packets_claim_one_transcript_and_the_shared_branch_ranks_last(p11_conn):
    """§6.9 says PREFER the shared branch. The engine ranks it below both rivals.

    The user has done everything the design asks: they created
    `Applications/Shared Application Materials`, and the transcript is an accepted
    member of it. §6.9: "the engine should retrieve and prefer that node."

    It retrieves it and prefers nothing. `node_role` is carried into the index
    (`placement/index.py:109`) and read by no scorer: `placement/scoring.py`'s
    `_CHANNEL_WEIGHT` scores channels, and `shared-material` is not a channel.
    The shared branch is reached through `accepted_group` (weight 2) while both
    institution branches are reached through `direct_fact` (weight 3), so the one
    node §6.9 names is ranked BELOW the two nodes §6.9 forbids choosing between.
    """
    tree = _application_tree()
    build_destination_index(p11_conn, tree, component_version="ambiguity",
                            observed_at=CLOCK)
    subject = Subject(kind=pv.FILE, file_id="f-transcript", content_hash="h1",
                      group_id=None, member_file_ids=())
    retrieval = retrieve(
        p11_conn, subject=subject, plan_version="plan-1", limits=LIMITS,
        facts=_transcript_facts(), group_ids=("g-shared",),
        curated_folder_labels=(), semantic_neighbours=(),
        component_version="ambiguity", observed_at=CLOCK)

    by_id = {c.node_id: c for c in retrieval.candidates}
    assert set(by_id) == {"n-columbia", "n-duke", "n-shared"}
    assert by_id["n-columbia"].channels == (DIRECT_FACT,)
    assert by_id["n-duke"].channels == (DIRECT_FACT,)
    assert by_id["n-shared"].channels == (ACCEPTED_GROUP,)

    result = assess(retrieval, {}, policy=POLICY)
    ranked = [s.node_id for s in result.scored]
    # The shared branch is LAST. This is the failure, asserted.
    assert ranked[-1] == "n-shared"
    assert result.scored[-1].support_score < result.scored[0].support_score

    # And the index did carry the role, so the information was there to use.
    entry = entry_for(p11_conn, plan_version="plan-1", node_id="n-shared")
    assert entry.node_role == pv.SHARED_MATERIAL


def test_the_transcript_abstains_but_names_the_wrong_reason_and_asks_nothing(p11_conn):
    """§6.9's outcome is right; §6.9's account of it is missing.

    "It should abstain or ask the user to choose a primary home." It abstains —
    two direct matches tie, the margin fails, and nothing is moved. Good.

    But the record says `low_margin`, and P11 publishes `no_shared_branch`
    (`placement/vocabulary.py:171`) and `shared-material decision`
    (`:148`) for exactly this moment. Neither is ever written. A user reading the
    review queue is told "the two best destinations were too close together",
    which is a scoring complaint, not the sentence "this file belongs to two of
    your packets; which is its home?" — and no `Ask` is offered, because nothing
    in `src/` constructs one.
    """
    tree = _application_tree()
    build_destination_index(p11_conn, tree, component_version="ambiguity",
                            observed_at=CLOCK)
    subject = Subject(kind=pv.FILE, file_id="f-transcript", content_hash="h1",
                      group_id=None, member_file_ids=())
    retrieval = retrieve(
        p11_conn, subject=subject, plan_version="plan-1", limits=LIMITS,
        facts=_transcript_facts(), group_ids=("g-shared",),
        curated_folder_labels=(), semantic_neighbours=(),
        component_version="ambiguity", observed_at=CLOCK)
    result = assess(retrieval, {}, policy=POLICY)

    assert result.two_condition.meets_margin == pv.MARGIN_FALSE
    assert result.two_condition.requires_review is True
    assert result.unique_direct_match is False

    assert result.abstention_reason == pv.LOW_MARGIN
    assert result.abstention_reason != pv.NO_SHARED_BRANCH
    assert result.confidence_class == pv.ABSTAIN_NO_SUPPORTED_DESTINATION
    assert result.confidence_class != pv.SHARED_MATERIAL_DECISION


def test_the_shared_material_rule_is_implemented_and_its_shared_branch_cannot_exist():
    """§6.9's RULE now exists. The branch three of its four policies need does not.

    `placement/groups.py:resolve_multi_home` landed while this suite was being
    written, and it is a good implementation: it branches on WHICH of the four
    policies is in force, it refuses a `shared_branch_node_id` that is one of the
    competing homes, and it has no code path that returns a competing node at all.

    But `shared-branch`, `primary-home` and `reference-or-alias` — the three in
    `_BRANCH_BEARING` (`groups.py:63-65`) — only place when a
    `shared_branch_node_id` is supplied, and NOTHING IN `src/` CAN MINT ONE. The
    `shared-material` node role is in both vocabularies and assigned by no
    module: `materialise.py:383` writes `ORDINARY`, `candidates.py:179` writes
    `ORDINARY`, `residuals.py:243,274` write `RESIDUAL`, and there is no fourth
    writer. There is no `add-shared-branch` in `BRANCH_ACTIONS` either.

    So a user who picks `shared-branch` gets, in practice, `mandatory-review`:
    the tree offers no shared node, `_BRANCH_BEARING` cannot fire, and the file
    falls through to the ask-or-abstain selector. Three of the four settings
    collapse onto the fourth.

    `scoped-general` is in exactly the same state, which matters because §5.9
    makes the scoped `General` branch the design's answer to "clearly part of
    `Academics/Columbia/2026-Spring` but no recoverable work type" — the single
    commonest ambiguity there is.
    """
    text = _src_text()

    written = {
        role: {name for name, body in text.items()
               if re.search(rf"node_role\s*=\s*{role}\b", body)}
        for role in ("ORDINARY", "RESIDUAL", "SCOPED_GENERAL", "SHARED_MATERIAL")
    }
    assert written["ORDINARY"], "the ordinary role has writers"
    assert written["RESIDUAL"], "the residual role has writers"
    # The two roles that exist to answer ambiguity have none.
    assert written["SHARED_MATERIAL"] == set()
    assert written["SCOPED_GENERAL"] == set()

    from tree_design.vocabulary import BRANCH_ACTIONS, NODE_ROLES
    assert set(NODE_ROLES) == {
        "ordinary", "scoped-general", "residual", "shared-material"}
    assert not any("shared" in action for action in BRANCH_ACTIONS)

    # And §6.9's rule is real, so this is a plumbing gap and not a design gap.
    from placement.groups import _BRANCH_BEARING, resolve_multi_home
    assert len(_BRANCH_BEARING) == 3
    outcome, payload = resolve_multi_home(
        candidate_node_ids=("n-columbia", "n-duke"),
        shared_material_policy="shared-branch", shared_branch_node_id="n-shared",
        ask_or_abstain=lambda ids: pv.ABSTAIN)
    assert (outcome, payload) == (pv.PLACE, "n-shared")


def test_the_six_nine_rule_is_reached_and_its_decision_has_somewhere_to_go():
    """GAP CLOSED. `resolve_multi_home` now has a caller and its result a record.

    This test was written as the negative: the rule was built, tested, and called
    by nothing in `src/`; `SHARED_MATERIAL_DECISION` — §6.11's own label for this
    outcome, "a transcript shared across application packets might be labeled
    `shared-material decision`" — lived only in `placement/vocabulary.py`; and
    `placement.records.Ask`, the shape of the question §6.9 says to put to the
    user, had no constructor anywhere. It failed the moment a producer appeared,
    which is what it was for.

    The producer is `placement/pipeline.py`. `run_corpus` reads P9's memberships
    across every accepted group and detects a file with membership in two packets
    BEFORE either group plan places it — because placing it inside one plan and
    correcting afterwards means the arbitrary choice was made and then withdrawn,
    which is not the same as never making it. It then calls `resolve_multi_home`
    with the two plans' shared parents as the competing candidates and writes one
    decision: a shared branch, an `Ask`, or a `no_shared_branch` abstention.
    """
    text = _src_text()

    callers = {name for name, body in text.items()
               if "resolve_multi_home(" in body
               and not name.endswith("groups.py")}
    assert callers == {"src/placement/pipeline.py"}

    homes = {name for name, body in text.items()
             if "SHARED_MATERIAL_DECISION" in body}
    assert homes == {"src/placement/pipeline.py",
                     "src/placement/vocabulary.py"}

    ask_builders = {name for name, body in text.items()
                    if re.search(r"(?<![A-Za-z_])Ask\(", body)}
    assert ask_builders == {"src/placement/pipeline.py"}


def test_a_tree_with_no_shared_material_policy_refuses_at_freeze_not_later(
        full_conn):
    """FIXED. This test previously asserted the DEFECT and was right to.

    `build_destination_index` (`src/placement/index.py:143-148`) fails closed —
    "without one a transcript belonging to two packets has no rule and P11 would
    have to pick an institution" — but `validate_for_freeze` did not check it and
    `_shared_material` returned `None` rather than refusing. So the user designed
    a tree, reviewed it, approved it, pressed freeze, IT FROZE, and the refusal
    arrived at the next stage as a contract violation about a policy nobody had
    asked them to choose.

    The gate is now at freeze, where the user can still act, and it is
    UNCONDITIONAL because P11's precondition is: `resolve_multi_home` takes
    `candidate_node_ids` computed during placement from retrieval, so whether a
    file will belong to two homes is not knowable at freeze by anyone. The
    refusal names §6.9's four answers rather than demanding a particular one.
    """
    from tree_design.freeze import FreezeRefused, freeze

    _seed_plan(full_conn, with_policy=False)
    with pytest.raises(FreezeRefused) as excinfo:
        freeze(
            full_conn, plan_version_id="plan_1", created_at=CLOCK, user_id="u1",
            component_version="ambiguity", residual_configuration={},
            approved_branch_ids=("n_course",),
            profiles=_plan_profiles(full_conn))
    assert any("shared-material" in reason for reason in excinfo.value.reasons)
    # The user is told what to choose, not merely that something is missing.
    assert "mandatory-review" in str(excinfo.value)
    # And nothing was frozen: the version is still theirs to edit.
    state = full_conn.execute(
        "SELECT state FROM plan_versions WHERE plan_version_id = 'plan_1'"
    ).fetchone()["state"]
    assert state == "draft"


def test_the_policy_survives_freeze_and_stops_at_the_index(full_conn):
    """The value reaches P11 and then goes no further than a non-empty check.

    `set_shared_material_policy` writes it, `freeze` resolves the tree-global row
    to a VALUE (`freeze.py:265-274`), `FrozenTree` carries it, and
    `placement/index.py:143` asks only whether it is non-empty. The `IndexEntry`
    does not carry it, so the one module that DOES branch on it
    (`placement/groups.py`) has to be handed it by a caller that does not exist.

    Two ends of a wire, both finished, with no wire.
    """
    from tree_design.freeze import freeze
    from tree_design.vocabulary import SHARED_MATERIAL_POLICIES
    from placement.index import build_destination_index

    assert len(SHARED_MATERIAL_POLICIES) == 4
    _seed_plan(full_conn, with_policy=True)
    bundle = freeze(
        full_conn, plan_version_id="plan_1", created_at=CLOCK, user_id="u1",
        component_version="ambiguity", residual_configuration={},
        approved_branch_ids=("n_course",), profiles=_plan_profiles(full_conn))
    assert bundle.shared_material_policy == "primary-home"

    entries = build_destination_index(
        full_conn, bundle, component_version="ambiguity", observed_at=CLOCK)
    assert entries
    assert not any(hasattr(entry, "shared_material_policy") for entry in entries)
    # Nor does any node in the frozen tree carry the shared-material role, so a
    # caller could not find the shared branch even if one wanted to.
    assert not any(node.node_role == pv.SHARED_MATERIAL for node in bundle.nodes)


@pytest.fixture()
def full_conn(conn):
    """Every schema the freeze -> index seam touches, in one database."""
    from database_agent.db import create_schema
    from eval_harness.store import create_eval_schema
    from facts.fields import create_fields
    from grouping.schema import create_grouping_schema
    from placement.schema import create_placement_schema
    from privacy.schema import create_privacy_schema
    from tree_design.schema import create_tree_schema

    create_schema(conn)
    create_eval_schema(conn)
    create_grouping_schema(conn)
    create_fields(conn)
    create_privacy_schema(conn)
    create_placement_schema(conn)
    create_tree_schema(conn)
    return conn


_PLAN_GROUP = AcceptedGroup(
    group_id="g_shared", label="Shared application materials", domain="academic",
    members=(GroupMember("f-transcript", "h1", "direct-anchor"),),
    anchor_facts=("fact_g_shared",), excluded_members=())


def _seed_plan(conn, *, with_policy: bool):
    from tree_design.records import PlanVersion, SharedMaterialPolicy
    from tree_design.records import derive_accepts_placement
    from tree_design.store import (
        set_shared_material_policy, write_node, write_plan_version,
    )
    from tree_design.vocabulary import PRIMARY_HOME

    write_plan_version(conn, PlanVersion(
        plan_version_id="plan_1", predecessor_id=None, state="draft",
        created_at=CLOCK, cross_folder_moves=False, selection_id="sel_1"))
    for node_id, label, parent, groups in (
            ("n_root", "Applications", None, ()),
            ("n_course", "Shared Application Materials", "n_root", ("g_shared",))):
        write_node(conn, Node(
            node_id=node_id, plan_version_id="plan_1", node_type=PROPOSED,
            display_label=label, parent_node_id=parent,
            root_anchor="root_documents", ordinal=0, associated_group_ids=groups,
            explanation=f"{label} appeared from the accepted groups beneath it.",
            node_role=ORDINARY,
            accepts_placement=derive_accepts_placement(
                PROPOSED, protected_movement_permitted=False),
            handling_class="personal_non_sensitive", origin_node_id=node_id,
            refinement_disposition="refined",
            refinement_reason="The accepted groups justify this level."))
    if with_policy:
        set_shared_material_policy(conn, SharedMaterialPolicy(
            policy_id="smp_1", plan_version_id="plan_1", policy=PRIMARY_HOME,
            policy_scope=None,
            reason="A transcript lives in one packet and is referenced elsewhere."))


def _plan_profiles(conn):
    from tree_design.profiles import build_profiles

    return build_profiles(
        conn, plan_version_id="plan_1", groups_by_id={"g_shared": _PLAN_GROUP},
        document_types_by_node={}, anchor_excerpts_by_node={},
        user_edits_by_node={}, node_scoped_rejections={})


# --------------------------------------------------------------------------------
# CASE 2 — the same ambiguity one stage earlier: the file gets no folder at all
# --------------------------------------------------------------------------------


def test_a_file_pulled_two_ways_gets_no_branch_and_the_screen_says_so(
        p10_conn, tmp_path):
    """The transcript at tree-design time: it vanishes, and nothing says so.

    `preferred_fact` (`src/facts/supersede.py:180-209`) returns `None` when a file
    holds two simultaneous live values for one field — P6's OQ6 is open and a
    reader that picked one would close it. `preferred_value_for` carries the
    `None` through and `materialise_branch` records the file in
    `BranchEvidence.unresolved_by_field`. That is all correct.

    The failure is one layer up. `vertical_options` computes the unresolved list
    the user actually reads from `candidate.covered_file_ids`
    (`src/tree_design/candidates.py:382-385`) — C6's group-coverage set — and
    never reads `evidence.unresolved_by_field`. C6 already refused any candidate
    that dropped a member, so for every surviving option that list is empty.

    FIXED. This test previously asserted the DEFECT and was right to: a file
    that two branches both wanted got no folder AND was reported as nothing,
    because the option's unresolved list was computed from `covered_file_ids` —
    C6 routing coverage — which holds the whole branch. The engine knew and the
    screen did not say.

    `00`:99 requires the picker to show "unresolved files", and the honest test
    is whether the file reaches a FOLDER, not whether routing covered it. The
    option now reports both kinds: never covered by the routing, and covered but
    settling no value at any level.
    """
    from p10.p6_fixtures import seed_academics
    from p10.test_p10_materialise import (
        ALWAYS_ORDINARY, NO_CONTEXT, ONE_CLASS, _candidate,
    )

    corpus = seed_academics(p10_conn, tmp_path)
    # `lab` already carries subject = PHYS1401. A second live value makes it the
    # file two branches both claim.
    corpus.add("lab", "subject", "PHYS1402")
    members = corpus.members("syllabus", "hw3", "lab")
    lab = corpus.file_id("lab")

    candidate = _candidate(("subject", "subject"))
    materialised, evidence = materialise_branch(
        p10_conn, candidate, branch_node_id="n_academics", members=members,
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)

    # The engine knows.
    assert lab in evidence.unresolved_by_field["subject"]
    assert lab not in {f for files in evidence.levels[0].members_by_value.values()
                       for f in files}

    # And now the screen says so too. C6 covered every member, so
    # `covered_file_ids` holds the whole branch — the file is surfaced because it
    # reached no NODE, which is the question the user is actually asking.
    covered = dataclasses.replace(
        candidate, covered_file_ids=frozenset(m.file_id for m in members))
    options = vertical_options(
        RoutingReport(candidates=(covered,), conflicts=(), deferred=0),
        branch_members=[m.file_id for m in members],
        materialise=lambda _c: evidence,
        validate=lambda _c: None,
        limits=_limits(p10_conn),
        preview=lambda _c, ev: _preview(ev),
    )
    assert options[0].unresolved_file_ids == (lab,)
    assert "1 file(s) would stay unresolved and visible" in options[0].summary


def _limits(conn):
    from tree_design.config import tree_limits

    from database_agent.budget import set_ceiling

    set_ceiling(conn, "tree.max_folder_proposals_and_depth", 6)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    return tree_limits(
        conn, excessive_depth_warning=5, tiny_folder_max_files=2,
        tiny_folder_count_warning=3,
        materially_improves_retrieval=lambda counts: None)


def _parent(label="Academics", node_id="n_academics", handling="personal_non_sensitive"):
    return Node(
        node_id=node_id, plan_version_id="plan_1", node_type=PROPOSED,
        display_label=label, parent_node_id=None, root_anchor="root_documents",
        ordinal=0, associated_group_ids=("g_1",),
        explanation="An accepted group produced this area.",
        node_role=ORDINARY, accepts_placement=True,
        handling_class=handling, origin_node_id=node_id)


def _preview(evidence):
    from tree_design.materialise import project_branch_preview
    from tree_design.validation import ValidationReport

    return project_branch_preview(
        evidence, ValidationReport(report_id="vr", passed=("V1",), failures=()),
        parent=_parent(), plan_version_id="plan_1", mint_node_id=_ids(),
        handling_class_for=lambda classes: "personal_non_sensitive",
        template_context_for=lambda field, index: None)


def _ids():
    counter = iter(range(10_000))
    return lambda: f"n_{next(counter)}"


# --------------------------------------------------------------------------------
# CASE 3 — protected material inside an unprotected workflow (the sharpest class)
# --------------------------------------------------------------------------------


PROTECTED_CLASSES = frozenset({
    "sensitive_personal", "highly_sensitive_credential_bearing"})
CHECK_ARGS = dict(
    collector_field_keys=frozenset({"target_school", "client", "authored_by"}),
    # V5 asks whether the VALUE STRING discloses protected material. No value in
    # this packet does — `UChicago` and `Rice` are institution names. The
    # PASSPORT is the protected thing, and it is isolated by `materialise_branch`
    # rather than used to condemn the folder it sits in.
    value_discloses_protected_material=lambda field_ref, value: False,
)


def test_one_passport_in_a_visa_packet_is_marked_and_the_branch_still_builds(
        p10_conn, tmp_path):
    """FIXED. This test previously asserted the DEFECT and was right to.

    V5 walked `handling_classes_by_value`, which `materialise_branch` filled with
    the UNION of the handling classes of every member contributing that value. The
    passport was one member of the UChicago packet, so the VALUE "UChicago" — an
    institution name, not sensitive at all — inherited the passport's class, V5
    refused the level, and `project_branch_nodes` refused the whole candidate.
    The user asked for `Applications/UChicago` and got no Applications branch,
    because one file inside it was a passport. Protection did not run first; it
    ran INSTEAD.

    `00`:120 has `Protected Records` "represent sensitive isolated material such
    as passport scans ... visas", and `00`:101 asks tree health to show "where
    sensitive material has been ISOLATED". Isolate the FILE, build the BRANCH.

    So now: the branch builds, the institution names are clean, and the passport
    is MARKED AND COUNTED — still a member, still under UChicago, still in the
    numbers the user reads — rather than removed. Removing it would be the
    silent omission the standing rule forbids. P7's `may_move_automatically` is
    what stops it being moved, and it already did.
    """
    subjects = _seed_packet(p10_conn, tmp_path)
    from p10.test_p10_materialise import _candidate

    members = tuple(subjects[name]
                    for name in ("essay", "form", "passport", "rice_essay"))
    materialised, evidence = materialise_branch(
        p10_conn, _candidate(("target_university", "target_university")),
        branch_node_id="n_applications", members=members,
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=lambda m: (
            "highly_sensitive_credential_bearing"
            if m.file_id == subjects["passport"].file_id
            else "personal_non_sensitive"),
        protected_handling_classes=PROTECTED_CLASSES)

    # Marked, and COUNTED: still a member, still under UChicago.
    assert evidence.protected_file_ids == frozenset({subjects["passport"].file_id})
    assert subjects["passport"].file_id in evidence.member_file_ids
    assert subjects["passport"].file_id in evidence.levels[0].members_by_value[
        "UChicago"]

    level = evidence.levels[0]
    assert level.values == ("Rice", "UChicago")
    # `UChicago` still carries the passport's class in the union -- and that no
    # longer refuses anything, because V5 asks about the VALUE STRING now.
    assert "highly_sensitive_credential_bearing" in level.handling_classes_by_value[
        "UChicago"]
    assert level.handling_classes_by_value["Rice"] == frozenset({
        "personal_non_sensitive"})

    report = run_checks(materialised, report_id="vr_v5",
                        limits=_limits(p10_conn), **CHECK_ARGS)
    assert report.accepted, [f.check for f in report.failures]

    nodes = project_branch_nodes(
        evidence, report, parent=_parent("Applications", "n_applications"),
        plan_version_id="plan_1", mint_node_id=_ids(),
        handling_class_for=lambda classes: "personal_non_sensitive",
        template_context_for=lambda field, index: None)
    assert [node.display_label for node in nodes] == ["Rice", "UChicago"]


def test_removing_the_passport_restores_the_branch_which_is_the_whole_problem(
        p10_conn, tmp_path):
    """The same branch, same files, minus the passport: it builds.

    This is the control that makes the previous test a finding rather than a
    coincidence. Nothing about `UChicago` changed; the only difference is whether
    a protected file sits under it. So the product's answer to "I need my
    passport for this application" is "then you may not have this application
    folder", and the two available workarounds are both losses: mark the level
    metadata-only and get no institution folders at all (§5.4), or leave the
    passport out of the packet and lose the packet's completeness.
    """
    subjects = _seed_packet(p10_conn, tmp_path)
    from p10.test_p10_materialise import _candidate

    members = tuple(subjects[name] for name in ("essay", "form", "rice_essay"))
    materialised, evidence = materialise_branch(
        p10_conn, _candidate(("target_university", "target_university")),
        branch_node_id="n_applications", members=members,
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=lambda m: "personal_non_sensitive",
        protected_handling_classes=PROTECTED_CLASSES)
    report = run_checks(materialised, report_id="vr_ok",
                        limits=_limits(p10_conn), **CHECK_ARGS)
    assert report.accepted
    nodes = project_branch_nodes(
        evidence, report, parent=_parent("Applications", "n_applications"),
        plan_version_id="plan_1", mint_node_id=_ids(),
        handling_class_for=lambda classes: "personal_non_sensitive",
        template_context_for=lambda field, index: None)
    assert [node.display_label for node in nodes] == ["Rice", "UChicago"]


def _seed_packet(conn, tmp_path):
    """Three files of one application packet, one of them a passport scan."""
    from p10.p6_fixtures import _fact, _subject
    from tree_design.upstream import GroupMember
    from grouping.vocabulary import DIRECT_ANCHOR

    rows = (
        ("essay", "Why UChicago - final", (("target_university", "UChicago"),)),
        ("form", "UChicago supplement form", (("target_university", "UChicago"),)),
        ("passport", "Passport biographical page",
         (("target_university", "UChicago"),)),
        # A second institution, so the level has two children and V2 (the
        # one-child check) cannot be what refuses the branch.
        ("rice_essay", "Rice supplement", (("target_university", "Rice"),)),
    )
    out = {}
    for name, raw, facts in rows:
        file_id, content_hash, key = _subject(conn, tmp_path, name, raw)
        for field_key, value in facts:
            _fact(conn, file_id, content_hash, key, field_key, value)
        out[name] = GroupMember(file_id=file_id, content_hash=content_hash,
                                basis=DIRECT_ANCHOR)
    return out


def test_a_protected_area_is_marked_and_counted_and_the_producer_is_wired():
    """The standing rule holds, and it is now wired to the freeze path.

    This test previously asserted the DEFECT — that `protected_area_nodes` had
    no caller in `src/` — and it was right: `protected_areas` read P3's exclusion
    verdicts, `protected_area_nodes` turned them into nodes, and nothing joined
    the two, so a protected container was pruned by the scan and then absent from
    the tree. Silently omitted, the one outcome the rule names.

    `freeze.represent_protected_areas` is that join, and
    `validate_for_freeze` now REFUSES a version in which a marked area has no
    node. The assertion is inverted to match: the caller must exist.
    """
    from tree_design.candidates import protected_area_nodes
    from tree_design.upstream import ProtectedArea

    area = ProtectedArea(
        path="/Users/x/Applications/Mail.app", display_label="Mail.app",
        rule_subject="directory", applies_to="subtree", label=None,
        observed_at=CLOCK)
    nodes = protected_area_nodes(
        (area,), plan_version_id="plan_1", root_anchor="root_applications",
        mint_node_id=_ids(),
        handling_class_for=lambda a: "personal_non_sensitive")
    assert len(nodes) == 1
    assert nodes[0].node_type == "protected"
    assert nodes[0].accepts_placement is False
    assert "never opened" in nodes[0].explanation

    text = _src_text()
    callers = {
        name for name, body in text.items()
        if "protected_area_nodes(" in body and not name.endswith("candidates.py")
    }
    assert callers, "the producer is wired to nothing; a marked area is omitted"
    assert any(name.endswith("freeze.py") for name in callers)


# --------------------------------------------------------------------------------
# CASE 4 — one file, two domains: the CAD drawing that is also a contract exhibit
# --------------------------------------------------------------------------------


def _fixture_recipe():
    from p10.test_p10_routing import _catalogue, _definition, _fragment, _row
    from tree_design.templates import FragmentRef

    return _catalogue, _definition, _fragment, _row, FragmentRef


def test_a_branch_holding_two_domains_is_refused_by_every_single_schema_recipe(
        p10_conn):
    """`engineering.cad-model` and `law_practice.evidence-exhibits` on one branch.

    The corpus carries this overlap directly: `engineering.invention-disclosure`
    holds `also_holds_with` edges to `legal.practice-matter-file` and
    `research.manuscript-publication`; `construction_property.variation-claim`
    holds them to `legal`, `finance` and `business_operations`. A drawing in a
    construction dispute is an engineering deliverable AND a contract exhibit,
    and the person wants one folder for the dispute.

    C6 (`src/tree_design/routing.py:288-300`) compares each accepted group's
    SINGLE `domain` against the schemas of the rows under evaluation. Two
    single-schema recipes are evaluated separately, so each one drops the other
    domain's files and refuses. The branch produces no composition at all.
    """
    _catalogue, _definition, _fragment, _row, FragmentRef = _fixture_recipe()
    from p10.test_p10_routing import ALWAYS, RANK, _context, _group

    subject = _fragment("subject", ("subject",))
    engineering = _definition("eng", (FragmentRef("subject", 1),), ("subject",))
    catalogue = _catalogue(
        (subject,), (engineering,),
        (_row("a-eng", "eng", "academic", (("subject", "subject"),)),))

    drawings = _group("g-drawings", "academic", ("f-cad",))
    exhibits = _group("g-exhibits", "photos", ("f-exhibit",))
    context = _context(("academic", "photos"), (drawings, exhibits))

    with pytest.raises(CompositionConflict) as excinfo:
        evaluate_composition(
            p10_conn, catalogue, context, catalogue.rows_for_schema("academic"),
            privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
    assert excinfo.value.gate == "C6"
    assert "f-exhibit" in " ".join(excinfo.value.conflicting)
    assert excinfo.value.overridable is False


def test_the_cross_domain_escape_exists_and_needs_a_catalogue_that_does_not(
        p10_conn):
    """One recipe with a row in each schema clears C6. Nothing ships one.

    This is the design's real answer to the CAD-drawing case, and it works: one
    `TemplateDefinition` with two `TemplateApplicability` rows covers both
    schemas, `schemas` becomes both, and no member is dropped.

    The catch is upstream. `load_catalogue` (`src/tree_design/catalogue.py:117`)
    reads a compiled manifest, and no such manifest exists in this repository —
    `load_catalogue` has no caller in `src/` at all. Every cross-domain recipe the
    corpus's 277 cross-schema `also_holds_with` edges would justify is a recipe
    nobody has compiled, so on a real run C6 refuses and there is no escape.
    """
    _catalogue, _definition, _fragment, _row, FragmentRef = _fixture_recipe()
    from p10.test_p10_routing import ALWAYS, RANK, _context, _group

    subject = _fragment("subject", ("subject",))
    both = _definition("dispute", (FragmentRef("subject", 1),), ("subject",))
    catalogue = _catalogue(
        (subject,), (both,),
        (_row("a-eng", "dispute", "academic", (("subject", "subject"),)),
         _row("a-law", "dispute", "photos", (("subject", "subject"),))))

    drawings = _group("g-drawings", "academic", ("f-cad",))
    exhibits = _group("g-exhibits", "photos", ("f-exhibit",))
    context = _context(("academic", "photos"), (drawings, exhibits))

    rows = (catalogue.rows_for_schema("academic")
            + catalogue.rows_for_schema("photos"))
    candidate = evaluate_composition(
        p10_conn, catalogue, context, rows,
        privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
    assert candidate.covered_file_ids == frozenset({"f-cad", "f-exhibit"})
    assert "C6" in candidate.gates_passed

    text = _src_text()
    callers = {name for name, body in text.items()
               if "load_catalogue(" in body and not name.endswith("catalogue.py")}
    # `fixtures.py` is excluded, and the gap this test characterises is NOT
    # closed by it. The gap is that no PRODUCTION path loads a catalogue,
    # because the authored 200-300 template library does not exist yet.
    # `tree_design.fixtures.template_library_fixture` builds a one-release
    # fixture through the real loader precisely so a fixture release the loader
    # would reject cannot be published — it is deterministic sample data P11
    # imports, not the library. Narrowing the exclusion rather than deleting the
    # assertion keeps the real gap characterised: if a pipeline module ever
    # calls `load_catalogue`, this still fires.
    assert callers == {"src/tree_design/fixtures.py"}


def test_a_group_the_engine_could_not_categorise_is_refused_by_c6(p10_conn):
    """`AcceptedGroup.domain = None` drops every member and refuses.

    P9's `groups` table permits a coherent group with a NULL `group_category`
    (`src/grouping/schema.py:56-59` only forces the NULL when the group is NOT
    coherent). C6 tests `if group.domain in schemas`, and `None` is in no schema
    set, so an accepted, coherent, labelled group whose category never resolved
    drops all of its files and refuses every recipe.

    This is the ambiguous group's most likely fate: the multi-domain situations
    in the corpus — a household budget that is also sole-trader bookkeeping
    (`business_operations.budget-forecast` also_holds_with
    `finance.small-business-bookkeeping`) — are exactly the ones a categoriser
    is least likely to resolve to one label.
    """
    _catalogue, _definition, _fragment, _row, FragmentRef = _fixture_recipe()
    from p10.test_p10_routing import ALWAYS, RANK, _context

    subject = _fragment("subject", ("subject",))
    catalogue = _catalogue(
        (subject,), (_definition("t", (FragmentRef("subject", 1),), ("subject",)),),
        (_row("a1", "t", "academic", (("subject", "subject"),)),))
    uncategorised = AcceptedGroup(
        group_id="g-budget", label="2026 budget", domain=None,
        members=(GroupMember("f-budget", "h", "direct-anchor"),),
        anchor_facts=("fact-1",), excluded_members=())
    context = _context(("academic",), (uncategorised,))

    with pytest.raises(CompositionConflict) as excinfo:
        evaluate_composition(
            p10_conn, catalogue, context, catalogue.rows_for_schema("academic"),
            privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
    assert excinfo.value.gate == "C6"
    assert "f-budget" in " ".join(excinfo.value.conflicting)


# --------------------------------------------------------------------------------
# CASE 5 — same file type, opposite side of the table
# --------------------------------------------------------------------------------


def test_no_destination_field_expresses_which_side_of_the_table_you_are_on(conn):
    """An NDA I signed and an NDA I issued cannot be told apart by any folder.

    §3.8 is explicit that roles must be separated — "The system must separate
    roles that happen to contain the same entity type" — and P6 does carry the
    four role fields. But D9 makes the two AUTHORSHIP-side roles
    destination-ineligible (`src/facts/fields.py:27-32`), so `authored_by` and
    `our_firm` can never become a folder level. What survives as a dimension is
    the COUNTERPARTY (`client`, `target_school`), which is the same value on both
    sides of the table.

    Consequence for a real person: an invoice I sent to Acme and an invoice Acme
    sent me both settle `client = Acme` and nothing distinguishes them. A résumé
    that is mine (`career`) and a résumé I am screening (`hr`) both carry the
    same fields — which is precisely what
    `applications.undergraduate-packet`'s collision with `career.recruiting` says:
    "Resume, personal statement, interview record and reference request appear on
    both sides… the same file can sit in both folders."
    """
    from facts.fields import FIELD_ROWS, create_fields, get_field

    create_fields(conn)
    assert get_field(conn, "authored_by")["destination_eligible"] == 0
    assert get_field(conn, "our_firm")["destination_eligible"] == 0

    eligible = {row.field_key for row in FIELD_ROWS if row.destination_eligible}
    # Not one of them names a direction, a side, or a party role.
    assert not eligible & {
        "direction", "party_role", "counterparty_role", "issued_or_received",
        "side", "our_role",
    }
    assert eligible == {
        "target_school", "client", "school", "term", "subject", "work_type",
        "target_university", "application_cycle", "application_document_type",
        "purpose", "project", "stage", "artifact_type", "lab", "venue",
        "institution", "account_type", "tax_year", "record_type",
        "capture_year", "event", "location", "media_type", "repository",
        # `60` §4's nineteen, minus the four it seeds ineligible.
        "site", "asset", "product", "supplier", "issuing_body", "record_period",
        "property", "design_item", "authorization", "consignment", "people_cycle",
        "recruiting_cycle", "employer", "target_employer", "job_title",
    }

    # NARROWED BY `60`, NOT CLOSED. One axis now has a direction: `employer` and
    # `target_employer` are a reciprocal `role_split` (§4), so a résumé addressed to
    # a firm and an employment record from a firm no longer settle the same key.
    from facts.fields import DOMAIN_FIELDS
    employer_row = next(r for r in FIELD_ROWS if r.field_key == "employer")
    assert "target_employer" in employer_row.role_split
    assert {"employer", "target_employer"} <= set(DOMAIN_FIELDS["career"])

    # The invoice case survives untouched. `client` is still the only counterparty
    # key either side can fill, its `role_split` partner `our_firm` is still
    # ineligible (D9), and `supplier` — the one new counterparty key — carries the
    # supplier role on ONE side by definition, so it cannot say which side we are on
    # for a document that names both parties.
    assert {"client", "supplier"} <= eligible
    assert "our_firm" not in eligible
    assert not eligible & {"consignor", "consignee", "issued_by", "received_from"}


def test_two_opposite_side_folders_tie_and_every_such_file_abstains(p11_conn):
    """`Invoices/Sent/Acme` and `Invoices/Received/Acme`, both expecting client=Acme.

    Because no field says which side, the user's only way to build both folders is
    to give them the same expected value. Retrieval then matches both on
    `direct_fact`, the scores are identical, the margin is zero, and every invoice
    in the corpus abstains. The tree the user designed makes the product WORSE at
    deciding than a tree with one folder would have been.
    """
    from p11.p10_fixtures import FROZEN_TREE, ExpectedValue, tree_with

    base = FROZEN_TREE.nodes[0]
    sent = dataclasses.replace(
        base, node_id="n-sent", origin_node_id="n-sent", display_label="Sent",
        ordinal=1, associated_group_ids=(), dimension="client",
        dimension_role="client",
        expected_values=(ExpectedValue(field="client", value="Acme"),),
        explanation="Invoices issued to Acme.")
    received = dataclasses.replace(
        sent, node_id="n-received", origin_node_id="n-received",
        display_label="Received", ordinal=2,
        explanation="Invoices received from Acme.")
    nodes = (sent, received, FROZEN_TREE.nodes[3])
    profiles = tuple(
        dataclasses.replace(
            FROZEN_TREE.profiles[0], node_id=n.node_id,
            display_label=n.display_label, expected_values=n.expected_values,
            accepted_group_ids=(), group_labels=(), anchor_excerpts=(),
            template_fields=("client",))
        for n in nodes)
    tree = tree_with(
        nodes=nodes, profiles=profiles,
        freeze_record=dataclasses.replace(
            FROZEN_TREE.freeze_record,
            node_ids=tuple(n.node_id for n in nodes),
            legal_destination_ids=frozenset(
                n.node_id for n in nodes if n.accepts_placement)))
    build_destination_index(p11_conn, tree, component_version="ambiguity",
                            observed_at=CLOCK)

    subject = Subject(kind=pv.FILE, file_id="f-invoice", content_hash="h1",
                      group_id=None, member_file_ids=())
    retrieval = retrieve(
        p11_conn, subject=subject, plan_version="plan-1", limits=LIMITS,
        facts=(MatchingFact(file_fact_id="ff-1", field="client", value="Acme",
                            reliability=pv.DIRECT, evidence_ref="obs-1"),),
        group_ids=(), curated_folder_labels=(), semantic_neighbours=(),
        component_version="ambiguity", observed_at=CLOCK)
    assert {c.node_id for c in retrieval.candidates} == {"n-sent", "n-received"}

    result = assess(retrieval, {}, policy=POLICY)
    assert result.scored[0].support_score == result.scored[1].support_score
    assert result.two_condition.margin_over_next == 0.0
    assert result.abstention_reason == pv.LOW_MARGIN


# --------------------------------------------------------------------------------
# CASE 6 — breadth: how much of the corpus the runtime can express at all
# --------------------------------------------------------------------------------


def test_all_twenty_three_corpus_schemas_now_have_a_runtime_identity():
    """GAP CLOSED. A lawyer, an engineer and a nurse now have a schema id.

    This test was written as the negative: P6 recognised ten schema ids while the
    corpus carried 358 rows across 23, so the thirteen professional schemas — which
    hold most of the cross-schema overlap the seed cases are about, `law_practice`
    alone holding 37 rows and 45 cross-schema `also_holds_with` edges — had no
    runtime identity. A group whose category was one of those thirteen had no
    applicability row, so C3 refused before C6 was reached.

    `planning/60-VOCABULARY-RULINGS.md` J-1 closes it: "All 23 roster schemas become
    schemas the product recognises." `60` §5 gives twenty of them a field set, and
    the three that keep none are §3.15's out-of-scope safety domains.
    """
    from facts.domains import FIELD_LESS_SCHEMA_IDS, SCHEMA_IDS

    corpus_schemas = set()
    total = 0
    for path in sorted((REPO / "planning" / "domains" / "nodes").glob("*.json")):
        row = json.loads(path.read_text(encoding="utf-8"))
        corpus_schemas.add(row["schema_id"])
        total += 1

    assert total == 358
    assert len(corpus_schemas) == 23
    assert len(SCHEMA_IDS) == 23
    assert set(SCHEMA_IDS) == corpus_schemas
    assert corpus_schemas - set(SCHEMA_IDS) == set()
    # The thirteen that used to be missing, named so the closure is legible.
    assert {
        "business_operations", "clinical_practice", "construction_property",
        "creative", "engineering", "government", "hr", "law_practice",
        "logistics", "manufacturing", "nonprofit", "resource_operations",
        "retail_hospitality",
    } <= set(SCHEMA_IDS)
    # And only §3.15's three safety domains carry no fields, so they can be activated
    # and still build nothing. `career` has left that tuple: `60` J-3 declares both
    # `work_type` and `record_type` on it, paying D1's "Career is owed before P10".
    assert set(FIELD_LESS_SCHEMA_IDS) == {"identity", "medical", "legal"}


def test_placement_now_records_a_decision_about_every_one_of_these(p11_conn):
    """GAP CLOSED. Every verdict above now reaches a written decision.

    This test was written as the negative: `PlacementDecision` was constructed in
    exactly one place in `src/` — `placement/store.py`, which REHYDRATES a stored
    row — so `confidence_class`, `abstention_reason`, `review_policy` and `Ask`
    were computed or defined and then dropped on the floor, and none of the cases
    in this file could be answered end to end however the scoring went.

    `placement/pipeline.py` is the author: it runs §6.12's nine steps and writes
    a decision for every outcome, including the abstentions. `placement/fixtures.py`
    is the second builder — five golden records P12 and P13 build against, made
    through the live constructor so a shape change breaks them at import.
    """
    text = _src_text()
    builders = {
        name for name, body in text.items()
        if re.search(r"(?<![A-Za-z_])PlacementDecision\(", body)
    }
    assert builders == {"src/placement/fixtures.py",
                        "src/placement/pipeline.py",
                        "src/placement/store.py"}
