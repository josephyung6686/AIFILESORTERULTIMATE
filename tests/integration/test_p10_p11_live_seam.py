"""The P10 → P11 seam, driven by P10's own output and never by a fixture of P11's.

What existed before this file, exactly: `tests/p11/p10_fixtures.py` is a small
tree hand-built with P10's constructors, which proves the RECORDS agree, and
`tests/integration/test_p11_p10_tree.py` writes hand-authored nodes through
P10's real `write_node` / `build_profiles` / `freeze`, which proves the WRITERS
agree. Neither takes a corpus. So nothing anywhere asked whether the tree P10
DERIVES — from P6's settled values, P9's accepted groups and P3's verdicts, by
routing, materialisation, validation and the user's recorded decisions — crosses
into P11 at all.

The first run that did found that P10's own published `frozen_tree_fixture()` —
the record the connection contract designates as "the P11 swap boundary", the one
that makes the swap "one line" — was refused outright by
`build_destination_index`, and that no tree P10's real chain built could be
indexed either, because nothing in P10 ever wrote §5.8's refinement disposition.

Every test below starts from `tree_design.pipeline.design_tree` over a real
corpus: real P1 rows, real P4 observations, real P6 facts, real P9 groups written
through P9's writers, a real P3 exclusion verdict produced by P3's own rule, and
real P7 classifications. Nothing between P10's output and P11's input is
hand-assembled, so a `FrozenTree` literal appearing here would be the defect the
file exists to catch rather than a shortcut.

The seven concepts each get a section, and each section answers one question:
does this cross, and what would fail if the producer were removed.
"""
from __future__ import annotations

import pytest

from database_agent.budget import set_ceiling
from database_agent.db import create_schema
from evidence_shape.schema import create_evidence_schema
from grouping.schema import create_grouping_schema
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from tree_design.schema import create_tree_schema

from placement import vocabulary as v
from placement.config import CEILINGS, SupportPolicy, placement_limits
from placement.index import (
    build_destination_index, entries_for_plan, legal_node_ids, node_exists,
)
from placement.schema import create_placement_schema

from p10.seam_corpus import ORDINARY_CLASS, seed_seam_corpus, two_dimension_catalogue
from p10.test_p10_pipeline import authorities, decisions

T0 = "2026-08-27T00:00:00Z"

#: 0.50 sits above a direct fact alone (3/7) and below a direct fact plus an
#: accepted group (5/7), which is the band `tests/p11/test_p11_pipeline.py` uses.
#: The arithmetic is P11's and unchanged; what differs here is that the nodes
#: being scored were built by P10 out of P6's values rather than written by hand.
POLICY = SupportPolicy(policy_id="seam-v1", support_scale_max=1.0,
                       minimum_support_threshold=0.5, margin_threshold=0.2)


# --- one real corpus, one real design run ------------------------------------------


@pytest.fixture()
def corpus(conn, tmp_path):
    # `tests/integration/` has no conftest, so `conn` is the ROOT fixture: P1's
    # eight tables and nothing else. Every other part's schema is this test's to
    # create, the way `tests/integration/test_p10_p6_materialise.py` layers its
    # own — and each one below is here because a real read fails without it.
    _bootstrap(conn)
    return seed_seam_corpus(conn, tmp_path)


def _bootstrap(conn) -> None:
    from eval_harness.store import create_eval_schema
    from facts.fields import create_fields
    from privacy.schema import create_privacy_schema
    from scan_agent.schema import create_scan_schema

    create_schema(conn)
    create_fields(conn)          # P6's catalogue: `is_destination_eligible`
    create_scan_schema(conn)     # P3's selection, scan run and exclusion verdicts
    create_privacy_schema(conn)  # P7's classifications and policy
    create_eval_schema(conn)
    create_evidence_schema(conn)  # P4's observations
    create_grouping_schema(conn)  # P9's groups, memberships and acceptances
    create_tree_schema(conn)
    create_placement_schema(conn)
    for key in CEILINGS.values():
        set_ceiling(conn, key, 8)


def run_p10(corpus, *, auth_over=None, dec_over=None):
    """P10's whole chain over the corpus. THE fixture-free half of the seam."""
    from tree_design.pipeline import design_tree

    return design_tree(
        corpus.conn,
        authorities=authorities(corpus, **(auth_over or {})),
        decisions=decisions(**(dec_over or {})))


def index(corpus, result):
    """P11's index over P10's REAL bundle, and P7's policy for that version."""
    set_policy(corpus.conn, Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode="hybrid",
        consent_grants=(), redaction_settings={}, automatic_move_permissions={},
        plan_version=result.tree.plan_version_id, set_at=T0),
        component_version="seam", user_id="jy",
        reason="P10-P11 live seam fixture")
    return build_destination_index(corpus.conn, result.tree,
                                   component_version="seam", observed_at=T0)


def entry_labelled(entries, label: str):
    return next(e for e in entries if e.display_label == label)


def node_labelled(tree, label: str):
    return next(n for n in tree.nodes if n.display_label == label)


# --- the published hand-over fixtures, against the consumer that reads them --------


def test_p10s_published_frozen_tree_fixture_is_one_p11_can_index(corpus):
    """DM2(e) and connection-contract §9: `frozen_tree_fixture()` is the record
    P11's G-P10 gate reads, and "the P11 swap is one line" because it returns the
    same `FrozenTree` the live read returns.

    Nothing had ever handed it to `build_destination_index`. It refused —
    `'n_academics' is in a frozen tree and carries no §5.8 refinement
    disposition` — so the swap the contract calls one line could not have been
    made at all. A hand-over fixture the consumer refuses is not a hand-over.
    """
    from tree_design.fixtures import frozen_tree_fixture

    tree = frozen_tree_fixture()
    entries = build_destination_index(corpus.conn, tree, component_version="seam",
                                      observed_at=T0)
    assert {e.node_id for e in entries} == set(
        tree.freeze_record.legal_destination_ids)


def test_p10s_walking_skeleton_is_one_p11_can_index(corpus):
    """DM2(a). The skeleton is the FIRST tree P11 builds against, and B8(b) gives
    it two nodes so §6.10's margin has a runner-up. Both are legal destinations,
    so both need §5.8's answer for the same reason as any other."""
    from tree_design.fixtures import (
        SHARED_MATERIAL_POLICY, _freeze_record, _profile, walking_skeleton_tree,
    )
    from tree_design.freeze import FrozenTree

    nodes = walking_skeleton_tree()
    tree = FrozenTree(
        plan_version_id="plan_1", freeze_record=_freeze_record(nodes),
        nodes=nodes, profiles=tuple(_profile(node) for node in nodes),
        shared_material_policy=SHARED_MATERIAL_POLICY,
        shared_material_policy_scope=None)
    assert len(build_destination_index(
        corpus.conn, tree, component_version="seam", observed_at=T0)) == 2


# --- the backbone: a real file placed into a real P10-built node -------------------


def _subject(corpus, name: str):
    from placement.records import Subject

    file_id, content_hash, _key = corpus.files[name]
    return Subject(kind=v.FILE, file_id=file_id, content_hash=content_hash,
                   group_id=None, member_file_ids=())


def _evidence(corpus, name: str, **over):
    from llm_harness.records import EvidenceItem
    from placement.records import MatchingFact

    _file_id, _hash, key = corpus.files[name]
    subject_value = {"syllabus": "BUSIB 4300", "hw3": "BUSIB 4300",
                     "lab": "PHYS1401"}[name]
    values = dict(
        facts=(MatchingFact(file_fact_id=f"ff_{name}", field="subject",
                            value=subject_value, reliability=v.DIRECT,
                            evidence_ref=key),),
        evidence_items=(EvidenceItem(
            evidence_ref=key, kind="fact", location="heading",
            excerpt_span=(0, 8), reliability_state="direct",
            basis="direct-anchor"),),
        group_ids=("g_columbia_coursework",), curated_folder_labels=(),
        semantic_neighbours=(), related_files=(),
        entity_frequency={subject_value: 6}, generic_entity_frequency=200)
    values.update(over)
    return values


def _inputs(corpus, result, **over):
    from placement.pipeline import PipelineInputs

    values = dict(
        plan_version=result.tree.plan_version_id, tree=result.tree,
        policy=POLICY, limits=placement_limits(corpus.conn), partition=None,
        ask_or_abstain=lambda ids: v.ABSTAIN, max_return_cycles=1, gate=None,
        model_client=None, prompt=None, call_dependencies=None,
        model_call_request=None, chosen_node_of=None, residual_action_of=None,
        sensitivity_policy=None, p2=None)
    values.update(over)
    return PipelineInputs(**values)


def test_a_file_is_placed_into_a_node_p10_built_out_of_p6s_own_values(corpus):
    """The seam, walked. No fixture tree anywhere in this call.

    §5.4's sentence is what this asserts end to end: "The system does not invent
    PHYS1401 ... those names emerge from validated facts". P6 settled the value,
    P9's accepted group carried the file, P10's router chose the nesting,
    `materialise_branch` made it a level and `project_branch_nodes` made it a
    node — and P11 retrieved that node, scored it and placed the file there. The
    check below reads the destination's label back out of P6's own `values` table
    rather than comparing it to a string this file chose.
    """
    from placement.pipeline import place_file

    result = run_p10(corpus)
    index(corpus, result)
    decision = place_file(
        corpus.conn, subject=_subject(corpus, "lab"),
        inputs=_inputs(corpus, result), evidence=_evidence(corpus, "lab"),
        component_version="seam", observed_at=T0)

    assert decision.outcome == v.PLACE
    node = node_labelled(result.tree, "PHYS1401")
    # The label is P6's canonical value, verbatim — not a composition, not a
    # normalisation P10 applied, and not a literal this test supplied. Read
    # through P6's own `values_in_field`, so a schema change breaks here rather
    # than being papered over by a SELECT this file wrote.
    from facts.values import values_in_field

    assert node.display_label in {
        row["canonical_value"] for row in values_in_field(corpus.conn, "subject")}
    assert decision.destination.node_id == node.node_id
    assert decision.destination.node_role == v.ORDINARY
    assert decision.confidence_class == v.EXACT_FACT_MATCH
    # §6.10's margin is VACUOUS here, and that is the correct reading rather than
    # a bypass. This line used to assert `MARGIN_TRUE`, on the grounds that "the
    # branch's own top-level node is retrievable through the accepted group" --
    # but that node is this file's own ANCESTOR, and an ancestor was never a
    # rival home. Filing the file under `PHYS1401` files it under the branch too.
    # Step 6's `identify_child_parent_fallback_or_none` now drops it before the
    # margin is taken, so there is genuinely no next-best to measure against, and
    # B8(b) says exactly that case is recorded vacuous so a reviewer and a replay
    # can tell it from a measured one.
    #
    # A MEASURED margin needs two homes on DIFFERENT branches, which is the §6.10
    # ambiguity the model call exists for; `tests/p11/` exercises that separately.
    assert decision.two_condition.meets_margin == v.MARGIN_TRUE_VACUOUS
    assert decision.two_condition.margin_over_next is None
    assert decision.review_policy == v.AUTO_ELIGIBLE


# --- concept 4: `candidate_orders` --------------------------------------------------


def test_the_recipes_recommended_order_decides_the_tree_p11_indexes(corpus):
    """`candidate_orders` crosses, and this is the only shape in which it can.

    The definition SHIPS both nestings and recommends one (§5.3, §5.8: ordering
    is the end user's decision per branch). Nothing about that record travels to
    P11 as a field — what travels is the tree it produced. So the discriminating
    test is a substitution: identical corpus, identical facts, identical groups,
    and only `is_default` moved between the two orders.

    Under `course_first` the courses are the first level and `lab` — which
    carries a subject and no work type — gets a `PHYS1401` node. Under
    `work_type_first` the first level is the work type, `lab` is unresolved
    there (§5.11), and **no PHYS1401 node exists at all**. The legal set P11
    indexes is different, and so is where a file can go.
    """
    course_first = run_p10(corpus)
    labels = {e.display_label for e in index(corpus, course_first)}
    assert {"BUSIB 4300", "PHYS1401", "Syllabus", "Homework"} <= labels

    # A second corpus, because a frozen version is immutable and the second run
    # must be a fresh design rather than an edit of the first.
    other = _fresh(corpus)
    work_type_first = run_p10(
        other, auth_over={"catalogue": two_dimension_catalogue(
            default_order_id="work_type_first")})
    other_labels = {e.display_label for e in index(other, work_type_first)}

    assert "PHYS1401" not in other_labels, (
        "the recommended order made no difference to the tree, which is what a "
        "chain ignoring `candidate_orders` would produce")
    assert {"Syllabus", "Homework", "BUSIB 4300"} <= other_labels


def test_the_two_orders_nest_the_same_two_dimensions_the_other_way_round(corpus):
    """The other half, read off `IndexEntry.ancestor_labels` — which is what P12
    composes a path from, so this is the field the difference actually lands in."""
    course_first = index(corpus, run_p10(corpus))
    homework = entry_labelled(course_first, "Homework")
    assert homework.ancestor_labels[-1] == "BUSIB 4300"

    other = _fresh(corpus)
    work_type_first = index(other, run_p10(other, auth_over={
        "catalogue": two_dimension_catalogue(default_order_id="work_type_first")}))
    nested_course = next(e for e in work_type_first
                         if e.display_label == "BUSIB 4300" and e.depth == 2)
    assert nested_course.ancestor_labels[-1] in {"Homework", "Syllabus"}


# --- concept 7: `ResolvedDimension.display_label` -----------------------------------


def test_the_authored_level_name_reaches_p11_on_the_node_and_nowhere_else(corpus):
    """It crosses on `Node.explanation`, and the index deliberately drops it.

    `RoleBinding.label` is the per-schema name of a LEVEL — "Course" to a
    student, "Figure or draft" to a researcher — carried by
    `ResolvedDimension.display_label` and read by `materialise._label_of` into
    every node's §5.12 explanation. So it does cross: it is in `FrozenTree.nodes`
    and a P13 canvas reads it there.

    It reaches no `IndexEntry` field, and **wiring one today would be wrong**.
    §6.2 lists "template fields" as what retrieval scores on, not level names;
    `IndexEntry` is a placement mechanism and the authored word is a display
    concern belonging to the surface that shows the tree. The assertion below is
    the guard: it fails the day a level name appears on an index entry, so the
    decision is re-made deliberately rather than drifting.
    """
    result = run_p10(corpus)
    node = node_labelled(result.tree, "Homework")
    assert "Assignment type" in node.explanation
    assert "work_type" not in node.explanation, (
        "the internal role key reached the user-visible sentence; the authored "
        "per-schema name is what `_label_of` exists to prefer")

    entries = index(corpus, result)
    entry = entry_labelled(entries, "Homework")
    carried = [name for name, value in vars(entry).items()
               if isinstance(value, str) and "Assignment type" in value]
    assert carried == [], (
        f"{carried} now carries the authored level name. That is a real decision "
        "about what §6.2 scores on — make it deliberately and update this guard")


def test_a_different_authored_label_changes_the_node_and_not_the_tree(corpus):
    """The negative twin. Swap the authored name and the explanation follows it;
    the STRUCTURE does not move, which is what says the label is a display string
    and not a level identity."""
    result = run_p10(corpus)
    baseline = {n.display_label for n in result.tree.nodes}

    other = _fresh(corpus)
    renamed = run_p10(other, auth_over={
        "catalogue": two_dimension_catalogue(work_type_label="Kind of work")})
    node = node_labelled(renamed.tree, "Homework")
    assert "Kind of work" in node.explanation
    assert {n.display_label for n in renamed.tree.nodes} == baseline


# --- concept 3: `node_type = PROTECTED` --------------------------------------------


def test_the_protected_area_p3_marked_is_in_the_tree_and_out_of_the_legal_set(corpus):
    """MARKED AND COUNTED, NEVER OPENED — end to end, from P3's own verdict.

    `exclusion_for` produced the verdict, `upstream.protected_areas` read it,
    `represent_protected_areas` wrote the node and `freeze` published it. On
    P11's side it is present in `tree.nodes`, absent from `legal_node_ids`, and
    absent from the `allowed_vocabulary` P8's Site C validates against — so no
    model can name it and no placement can reach it.
    """
    result = run_p10(corpus)
    entries = index(corpus, result)

    node = node_labelled(result.tree, corpus.protected_label)
    assert node.node_type == v.PROTECTED_NODE
    assert node.node_id in result.tree.freeze_record.node_ids   # counted
    assert node.explanation.strip()                             # explained
    assert node.accepts_placement is False
    assert node.node_id not in result.tree.freeze_record.legal_destination_ids
    assert node.node_id not in legal_node_ids(
        corpus.conn, plan_version=result.tree.plan_version_id)
    assert node.node_id not in {e.node_id for e in entries}
    # Present, not merely absent: something the user can be shown.
    assert corpus.protected_label in {n.display_label for n in result.tree.nodes}


def test_removing_the_producer_refuses_the_freeze_rather_than_omitting_the_area(
        corpus, monkeypatch):
    """The negative twin, and the one the standing rule turns on.

    "Never silently omitted" is only a guarantee if the omission is detectable.
    With `represent_protected_areas` neutered, the marked area has no node and
    `validate_for_freeze` refuses — the tree cannot be adopted at all. A product
    that dropped the area would reach P11 with a smaller `node_ids` and nothing
    anywhere would say a container had gone missing.
    """
    import tree_design.pipeline as pipeline
    from tree_design.freeze import FreezeRefused

    monkeypatch.setattr(pipeline, "represent_protected_areas",
                        lambda *a, **k: ())
    with pytest.raises(FreezeRefused) as excinfo:
        run_p10(corpus)
    assert any(corpus.protected_label in reason
               for reason in excinfo.value.reasons)


def test_p11_holds_no_reader_for_a_protected_node_and_needs_none(corpus):
    """The concept crosses as a deliberate EXCLUSION, which is the whole of what
    P11 owes it.

    §8.4's protected rule reaches placement two ways and neither is a node read:
    `accepts_placement = false` keeps the node out of the index, and P7's
    `ClassificationRecord.protected` gates the FILE at `place_file`. Showing the
    area present-but-untouched is P13's, off `FrozenTree.nodes`. So there is
    nothing to wire, and the guard is that the exclusion is total.
    """
    result = run_p10(corpus)
    entries = index(corpus, result)
    protected = node_labelled(result.tree, corpus.protected_label)
    assert not [e for e in entries if e.node_id == protected.node_id]
    assert not [e for e in entries if e.display_label == protected.display_label]
    # And a file that looks exactly like it still abstains rather than landing
    # there, because the node was never retrievable in the first place (§5.10's
    # mechanism, applied to §8.4's node kind).
    from placement.pipeline import place_file

    decision = place_file(
        corpus.conn, subject=_subject(corpus, "lab"),
        inputs=_inputs(corpus, result),
        evidence=_evidence(corpus, "lab", facts=(), group_ids=(),
                           curated_folder_labels=(corpus.protected_label,)),
        component_version="seam", observed_at=T0)
    assert decision.outcome == v.ABSTAIN
    assert decision.destination is None


# --- concept 2: `IndexEntry.disposition` -------------------------------------------


def test_the_residual_nodes_74_disposition_reaches_the_index(corpus):
    """It crosses. P10's `Review Later` node carries `review-only` and the entry
    P11 builds carries the same value; every other node carries `None`, which
    `_entry` refuses to let be anything else (§7.4: the disposition is required on
    a residual node and meaningless on every other role)."""
    from tree_design.vocabulary import REVIEW_LATER

    result = run_p10(corpus)
    entries = index(corpus, result)
    review_later = entry_labelled(entries, REVIEW_LATER)
    assert review_later.node_role == v.RESIDUAL_ROLE
    assert review_later.disposition == v.REVIEW_ONLY
    assert all(e.disposition is None for e in entries
               if e.node_role != v.RESIDUAL_ROLE)


def test_the_disposition_p10_wrote_is_what_decides_p11s_review_policy(corpus):
    """The consumer, bound to P10's real value against its live signature.

    `review_policy_for` is called on every §6 and §7 decision and takes
    `destination_disposition` with NO default. Both calls below are identical
    except for that argument, and each argument is read off a real entry P10
    produced — so the difference in the answer is attributable to P10's
    disposition and to nothing else. 00:121's word is "never": a review-only
    category never moves files automatically, and no confidence clears it.
    """
    from tree_design.vocabulary import REVIEW_LATER
    from placement.privacy import moves_files, privacy_state_for, review_policy_for
    from placement.records import TwoCondition

    result = run_p10(corpus)
    entries = index(corpus, result)
    residual = entry_labelled(entries, REVIEW_LATER)
    ordinary = entry_labelled(entries, "PHYS1401")

    clean = TwoCondition(
        support_score=1.0, support_threshold=0.5, meets_threshold=True,
        margin_over_next=0.5, margin_threshold=0.2,
        meets_margin=v.MARGIN_TRUE, verdict=v.ACCEPT_DIRECT,
        requires_review=False)
    # P7's real answer about a real file, so the only hand-made value in either
    # call is the scoring, and it is IDENTICAL between them.
    file_id, content_hash, _key = corpus.files["hw3"]
    privacy = privacy_state_for(corpus.conn, file_id=file_id,
                                content_hash=content_hash,
                                plan_version=result.tree.plan_version_id)
    assert privacy.handling_class == ORDINARY_CLASS and privacy.protected is False
    common = dict(privacy_state=privacy, two_condition=clean, group_support=None,
                  unique_direct_match=True, automatic_move_permitted=False)

    assert review_policy_for(destination_disposition=ordinary.disposition,
                             **common) == v.AUTO_ELIGIBLE
    assert review_policy_for(destination_disposition=residual.disposition,
                             **common) == v.REVIEW_REQUIRED
    assert moves_files(residual.disposition) is False


def test_the_74_disposition_survives_a_real_77_placement_into_that_node(corpus):
    """End to end through §7.7, so the value is read by the pipeline and not only
    by the predicate: `run_residual_file` looks the node up in P11's index and
    hands `entry.disposition` to `review_policy_for` itself."""
    from tree_design.vocabulary import REVIEW_LATER
    from llm_harness.vocabulary import CHOOSE_RESIDUAL_DESTINATION
    from placement.pipeline import run_residual_file
    from placement.residual import ResidualSetDecision, record_set_decision

    result = run_p10(corpus)
    entries = index(corpus, result)
    review_later = entry_labelled(entries, REVIEW_LATER)

    record_set_decision(
        corpus.conn,
        ResidualSetDecision(set_id="set-1",
                            plan_version=result.tree.plan_version_id,
                            choice=v.REVIEW_WITH_MODEL, node_id=None,
                            decided_at=T0),
        component_version="seam", observed_at=T0, user_id="jy")
    decision = run_residual_file(
        corpus.conn, subject=_subject(corpus, "hw3"), set_id="set-1",
        inputs=_inputs(corpus, result), evidence=_evidence(corpus, "hw3"),
        action=CHOOSE_RESIDUAL_DESTINATION, target=review_later.node_id,
        component_version="seam", observed_at=T0)

    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == review_later.node_id
    assert decision.destination.node_role == v.RESIDUAL_ROLE
    assert decision.review_policy == v.REVIEW_REQUIRED


def test_the_one_path_where_the_disposition_alone_decides_is_unreachable_today(
        corpus):
    """Recorded rather than assumed, because it bounds what the test above proves.

    `review_policy_for` returns `auto_eligible` only on §6's deterministic unique
    direct match; every §7 and §6.9 decision already carries
    `requires_review=True` from `_flat_two_condition`, so on those paths the
    disposition gate is a second lock on a door that is already bolted. For the
    gate to be the deciding one, a residual node would have to be RETRIEVED — and
    a residual node P10's chain builds has no `expected_values` and no
    `accepted_group_ids`, so `retrieve` can reach it only on the two
    non-deciding channels.

    This fails the day a residual node gains a deciding channel, which is exactly
    when the gate becomes live and wants an end-to-end test of its own.
    """
    from tree_design.vocabulary import REVIEW_LATER

    result = run_p10(corpus)
    entries = index(corpus, result)
    residual = entry_labelled(entries, REVIEW_LATER)
    assert residual.expected_values == ()
    assert residual.accepted_group_ids == ()


# --- concept 5: `SHARED_MATERIAL` and §6.9's policy value ---------------------------


def test_p11s_own_reader_finds_the_shared_branch_p10_minted(corpus):
    """`_shared_branch_of` is the function `run_corpus` calls, and it scans
    `tree.nodes` for `node_role == shared-material` with `accepts_placement`.
    Here it is reading P10's real bundle: the node was created by
    `apply_review_action(set-shared-material-policy)` and its id was minted by
    the draft that action opened."""
    from placement.pipeline import _shared_branch_of

    result = run_p10(corpus)
    node = node_labelled(result.tree, "Shared Course Material")
    assert node.node_role == v.SHARED_MATERIAL
    assert _shared_branch_of(result.tree) == node.node_id


def test_69s_four_policies_are_spelled_the_same_on_both_sides_of_the_seam(corpus):
    """Connection contract §5.3: P10 hyphenates and an early P11 draft
    underscored, and `resolve_multi_home` compares the tree's value against
    P11's tuple — so every multi-home file would have fallen through every
    branch and §6.9 would be unenforced in the one case it exists for. Nothing
    raises on a mismatch, which is why it has to be driven.

    The value here is the one P10 wrote into `shared_material_policies` and read
    back through `frozen_tree`, and the consumer is P11's live function.
    """
    from placement.groups import resolve_multi_home

    result = run_p10(corpus)
    node = node_labelled(result.tree, "Shared Course Material")
    competing = tuple(sorted(
        n.node_id for n in result.tree.nodes
        if n.display_label in {"BUSIB 4300", "PHYS1401"}))
    assert len(competing) == 2

    outcome, payload = resolve_multi_home(
        candidate_node_ids=competing,
        shared_material_policy=result.tree.shared_material_policy,
        shared_branch_node_id=node.node_id,
        ask_or_abstain=lambda ids: v.ASK_USER)
    assert outcome == v.PLACE
    assert payload == node.node_id


def test_a_mandatory_review_run_mints_no_branch_and_p11_asks_instead(corpus):
    """The negative twin, and it detects substitution in both directions.

    `mandatory-review` is the one §6.9 policy that resolves to no destination, so
    P10 mints no `shared-material` node, `_shared_branch_of` answers None and
    `resolve_multi_home` falls to the user. If P11 were matching the policy
    string loosely — or ignoring the tree's node roles — this run would be
    indistinguishable from the one above.
    """
    from placement.groups import resolve_multi_home
    from placement.pipeline import _shared_branch_of
    from tree_design.pipeline import SharedMaterialAnswer
    from tree_design.vocabulary import MANDATORY_REVIEW

    result = run_p10(corpus, dec_over={"shared_material": SharedMaterialAnswer(
        policy=MANDATORY_REVIEW,
        reason="The user would rather decide packet by packet.")})
    assert not [n for n in result.tree.nodes
                if n.node_role == v.SHARED_MATERIAL]
    assert _shared_branch_of(result.tree) is None

    competing = tuple(sorted(
        n.node_id for n in result.tree.nodes
        if n.display_label in {"BUSIB 4300", "PHYS1401"}))
    outcome, _payload = resolve_multi_home(
        candidate_node_ids=competing,
        shared_material_policy=result.tree.shared_material_policy,
        shared_branch_node_id=None,
        ask_or_abstain=lambda ids: v.ASK_USER)
    assert outcome == v.ASK_USER


# --- concept 6: `SCOPED_GENERAL` ----------------------------------------------------


def test_a_scoped_general_node_is_legal_and_carries_p10s_role_into_a_decision(
        corpus):
    """It crosses — as data on the decision, which is all P11 owes it.

    `00`:99 asks for "a scoped General or Other branch within a meaningful
    parent"; P10 mints it and P11 places into it like any other legal node. P11
    SPEC:405 says the outcome is `place` with `node_role = scoped-general`, and
    MINOR 6 says P11 carries P10's vocabulary rather than publishing a parallel
    one — so there is deliberately no branch in placement that tests for this
    value, and adding one would be the `destination.kind` field the SPEC removed.

    §7.7 action 4 — "choose an approved broad parent" — is the design's own route
    to it, and it is the route driven here.
    """
    from llm_harness.vocabulary import CHOOSE_BROAD_PARENT
    from placement.pipeline import run_residual_file
    from placement.residual import ResidualSetDecision, record_set_decision

    result = run_p10(corpus)
    entries = index(corpus, result)
    general = entry_labelled(entries, "General")
    assert general.node_role == v.SCOPED_GENERAL
    assert general.node_id in legal_node_ids(
        corpus.conn, plan_version=result.tree.plan_version_id)
    # Scoped, never global: `00`:99's other half.
    assert general.parent_node_id is not None
    assert general.depth == 1
    # `00`:111 — "it should choose an approved General fallback under the
    # meaningful parent or abstain" — is a sentence about the MODEL, and the
    # mechanism that lets a model name this node is P8's own `node_exists`
    # authority, closed over P11's index over P10's tree. Asked here directly.
    assert node_exists(corpus.conn,
                       plan_version=result.tree.plan_version_id)(
        general.node_id, result.tree.plan_version_id) is True
    protected = node_labelled(result.tree, corpus.protected_label)
    assert node_exists(corpus.conn,
                       plan_version=result.tree.plan_version_id)(
        protected.node_id, result.tree.plan_version_id) is False

    record_set_decision(
        corpus.conn,
        ResidualSetDecision(set_id="set-g",
                            plan_version=result.tree.plan_version_id,
                            choice=v.REVIEW_WITH_MODEL, node_id=None,
                            decided_at=T0),
        component_version="seam", observed_at=T0, user_id="jy")
    decision = run_residual_file(
        corpus.conn, subject=_subject(corpus, "lab"), set_id="set-g",
        inputs=_inputs(corpus, result), evidence=_evidence(corpus, "lab"),
        action=CHOOSE_BROAD_PARENT, target=general.node_id,
        component_version="seam", observed_at=T0)
    assert decision.outcome == v.PLACE
    assert decision.destination.node_role == v.SCOPED_GENERAL


def test_the_scoped_general_role_survives_the_round_trip_through_the_store(corpus):
    """The negative twin for a value that is CARRIED rather than branched on.

    A carried value fails silently: nothing raises if P11 stores `ordinary` where
    P10 said `scoped-general`, and every assertion made against an in-memory
    decision would still pass. So the check is made against the stored row, read
    back through P11's own reader.
    """
    from llm_harness.vocabulary import CHOOSE_BROAD_PARENT
    from placement.pipeline import run_residual_file
    from placement.residual import ResidualSetDecision, record_set_decision
    from placement.store import current_decision, subject_ref_of

    result = run_p10(corpus)
    entries = index(corpus, result)
    general = entry_labelled(entries, "General")
    record_set_decision(
        corpus.conn,
        ResidualSetDecision(set_id="set-g",
                            plan_version=result.tree.plan_version_id,
                            choice=v.REVIEW_WITH_MODEL, node_id=None,
                            decided_at=T0),
        component_version="seam", observed_at=T0, user_id="jy")
    subject = _subject(corpus, "lab")
    run_residual_file(
        corpus.conn, subject=subject, set_id="set-g",
        inputs=_inputs(corpus, result), evidence=_evidence(corpus, "lab"),
        action=CHOOSE_BROAD_PARENT, target=general.node_id,
        component_version="seam", observed_at=T0)

    stored = current_decision(corpus.conn,
                              plan_version=result.tree.plan_version_id,
                              subject_ref=subject_ref_of(subject))
    assert stored.destination.node_role == v.SCOPED_GENERAL
    # P11 publishes no parallel vocabulary: the constant it stored IS P10's.
    from tree_design.vocabulary import SCOPED_GENERAL as P10_SCOPED_GENERAL

    assert stored.destination.node_role == P10_SCOPED_GENERAL


# --- concept 1: `parent_concepts` ---------------------------------------------------


def test_parent_concepts_is_computed_by_the_chain_and_reaches_no_p11_reader(corpus):
    """It does NOT cross, and wiring a P11 consumer today would be wrong.

    `health.parent_concepts_for` maps each node to the dimensions its ANCESTORS
    express, and its one consumer is `warnings_for` — §5.9's canvas warnings,
    which the chain now computes for every option the user is shown. It affects
    what the user is WARNED about before approving; it changes no node and no
    field of the frozen tree, so there is nothing for `IndexEntry` to project.

    The consumer that would read it does not exist: §6.7's broad-parent case is
    the only P11 question about which ancestor levels are supported, and
    `DecisionDepth.unsupported_levels` is `()` at every construction site in
    `placement/pipeline.py` — P11 never produces that case at all. Wiring a
    producer to an absent consumer is what this codebase calls a reference chain.

    So it stays unwired WITH a guard, following `evidence_gap_file_ids`: this
    fails the day `placement/` names it, which is the day the decision is worth
    re-making.
    """
    from pathlib import Path

    from tree_design.health import parent_concepts_for

    result = run_p10(corpus)
    concepts = parent_concepts_for(result.tree.nodes)
    course = node_labelled(result.tree, "Homework")
    assert concepts[course.node_id] == ("subject",), (
        "the chain's ancestors express the course level, read off stored state")
    # The chain ran §5.9's warnings over the real preview, which is the only
    # thing `parent_concepts_for` feeds.
    assert result.branches[0].warnings is not None

    placement_src = Path(__file__).resolve().parents[2] / "src" / "placement"
    naming_it = sorted(
        module.name for module in placement_src.rglob("*.py")
        if "parent_concept" in module.read_text())
    assert naming_it == [], (
        f"{naming_it} now names §5.9's parent concepts. P11 gained a consumer — "
        "decide deliberately whether the index should project it, and update "
        "this guard either way")

    # And the guard on the CONSUMER, so the two cannot drift apart quietly:
    # §6.7's broad-parent case is the only P11 question about which ancestor
    # levels the evidence supports, and P11 does not produce it. Every
    # `DecisionDepth` the pipeline builds passes `unsupported_levels=()`. The day
    # one does not, §6.7 is live and the ancestors' dimensions become a question
    # P11 asks — which is exactly when wiring `parent_concepts` is worth deciding.
    import ast

    pipeline_src = placement_src / "pipeline.py"
    filled = []
    for node in ast.walk(ast.parse(pipeline_src.read_text())):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "DecisionDepth"):
            for keyword in node.keywords:
                if keyword.arg == "unsupported_levels" and not (
                        isinstance(keyword.value, ast.Tuple)
                        and not keyword.value.elts):
                    filled.append(node.lineno)
    assert filled == [], (
        f"pipeline.py:{filled} now fills §6.7's `unsupported_levels`. P11 has "
        "started producing the broad-parent case; re-decide whether the index "
        "should carry §5.9's parent concepts")


def test_a_tree_that_repeats_a_parent_dimension_fires_59s_warning(corpus):
    """The positive half, so the guard above is not asserting an empty machine.

    A monotone "nothing reads it" test cannot tell an unwired concept from a
    broken one. This drives `parent_concepts_for` through `warnings_for` on a
    tree whose child level repeats its parent's dimension and watches the
    warning fire.
    """
    from tree_design.health import (
        BranchCounts, parent_concepts_for, warnings_for,
    )
    from tree_design.vocabulary import WARN_REPEATED_PARENT

    result = run_p10(corpus)
    nodes = result.tree.nodes
    course = node_labelled(result.tree, "BUSIB 4300")
    child = node_labelled(result.tree, "Homework")
    import dataclasses

    repeated = tuple(
        dataclasses.replace(node, dimension="subject", dimension_role="subject")
        if node.node_id == child.node_id else node
        for node in nodes)
    counts = {node.node_id: BranchCounts(
        node_id=node.node_id, child_count=2, descendant_count=2, member_count=1,
        example_members=(), unresolved_file_ids=(), evidence_gap_file_ids=(),
        sensitive_isolated=False, stale=False) for node in repeated}
    fired = warnings_for(repeated, counts,
                         limits=authorities(corpus).limits,
                         parent_concepts=parent_concepts_for(repeated))
    assert any(w.kind == WARN_REPEATED_PARENT and w.node_id == child.node_id
               for w in fired), [(w.kind, w.node_id) for w in fired]
    assert course.dimension == "subject"


# --- §8.8: the identity contract ---------------------------------------------------


def test_no_node_id_survives_a_p10_re_version(corpus):
    """The premise the whole contract rests on, measured on a real re-version.

    P10 answered its OQ5 by minting a new `node_id` per plan version
    (`open_draft`), so a P11 path matching decisions to nodes on `node_id` finds
    NOTHING after any edit — including a pure rename, which §8.8 forbids being
    treated as a removal. This asserts the premise rather than assuming it.
    """
    from tree_design.diff import diff_versions

    result = run_p10(corpus)
    after = _re_version(corpus, result, new_label="Physics 1401")

    before_ids = {n.node_id for n in result.tree.nodes}
    after_ids = {n.node_id for n in after.nodes}
    assert before_ids & after_ids == set(), (
        "some node id survived the re-version, which would make the id-matching "
        "bug undetectable")
    # And the lineage DOES survive, which is what makes a correct match possible.
    assert ({n.origin_node_id for n in result.tree.nodes}
            == {n.origin_node_id for n in after.nodes})
    assert diff_versions(corpus.conn, before=result.tree.plan_version_id,
                         after=after.plan_version_id)


def test_a_placement_carries_across_a_re_version_because_reproject_uses_lineage(
        corpus):
    """THE discriminating test. Matching on `node_id` FAILS; `origin_node_id`
    succeeds.

    A file is placed against version A. P10 then re-versions the tree with a pure
    rename — §8.8's own example, "Applications was renamed to Admissions" — and
    every node gets a new id. `reproject` resolves
    `decision.destination.node_id → version-A entry → origin_node_id → version-B
    entry`, so the decision carries and produces no review.

    The second half is what makes it discriminating rather than merely green: the
    same lookup performed on `node_id` — which is what P11's plan assumed and
    what this contract corrected — finds no successor for this decision, so an
    implementation matching that way would have marked it for renewed review.
    """
    from placement.pipeline import place_file
    from placement.versions import reproject

    result = run_p10(corpus)
    index(corpus, result)
    decision = place_file(
        corpus.conn, subject=_subject(corpus, "lab"),
        inputs=_inputs(corpus, result), evidence=_evidence(corpus, "lab"),
        component_version="seam", observed_at=T0)
    assert decision.outcome == v.PLACE

    after = _re_version(corpus, result, new_label="Physics 1401")
    build_destination_index(corpus.conn, after, component_version="seam",
                            observed_at=T0)
    # The rename really happened, so "carried unchanged" is not trivially true
    # of a version identical to its predecessor.
    assert "Physics 1401" in {n.display_label for n in after.nodes}
    assert "PHYS1401" not in {n.display_label for n in after.nodes}

    diff = reproject(corpus.conn,
                     from_plan_version=result.tree.plan_version_id,
                     to_plan_version=after.plan_version_id)
    assert decision.decision_id in diff.carried_unchanged
    assert diff.requiring_renewed_review == ()
    assert diff.renewed_review_count == 0

    # The negative twin, computed the way the corrected plan would have: no node
    # id from the old version appears in the new one, so an id match finds
    # nothing and every decision would be marked.
    after_ids = {entry.node_id for entry in entries_for_plan(
        corpus.conn, plan_version=after.plan_version_id)}
    assert decision.destination.node_id not in after_ids
    origins = {entry.origin_node_id for entry in entries_for_plan(
        corpus.conn, plan_version=after.plan_version_id)}
    old = next(e for e in entries_for_plan(
        corpus.conn, plan_version=result.tree.plan_version_id)
        if e.node_id == decision.destination.node_id)
    assert old.origin_node_id in origins


def test_a_decision_whose_node_is_really_gone_is_marked_for_renewed_review(corpus):
    """The other half of §8.8, so "carried" is not the only answer the function
    can give. The node is IGNORED in the new version — §5.10's own gesture — which
    removes it from the legal set, and the decision that named it is marked."""
    from placement.pipeline import place_file
    from placement.versions import reproject

    result = run_p10(corpus)
    index(corpus, result)
    decision = place_file(
        corpus.conn, subject=_subject(corpus, "lab"),
        inputs=_inputs(corpus, result), evidence=_evidence(corpus, "lab"),
        component_version="seam", observed_at=T0)

    after = _re_version(corpus, result, ignore_label="PHYS1401")
    build_destination_index(corpus.conn, after, component_version="seam",
                            observed_at=T0)
    diff = reproject(corpus.conn,
                     from_plan_version=result.tree.plan_version_id,
                     to_plan_version=after.plan_version_id)
    assert diff.requiring_renewed_review == (decision.decision_id,)
    assert diff.removed_node_ids == (decision.destination.node_id,)


def test_learned_preferences_survive_a_re_version_on_lineage_too(corpus):
    """§8.8: "preferences carry across versions", filtered by node existence.

    Same identity rule, second consumer. A suppression recorded against version
    A names A's `node_id`, which per-version minting guarantees is absent from B
    — so a filter on `node_id` alone would silently drop EVERY learned preference
    at the first tree edit.
    """
    from placement.versions import learned_preferences_still_applicable

    result = run_p10(corpus)
    index(corpus, result)
    node = node_labelled(result.tree, "PHYS1401")
    after = _re_version(corpus, result, new_label="Physics 1401")
    build_destination_index(corpus.conn, after, component_version="seam",
                            observed_at=T0)

    class _Suppression:
        def __init__(self, node_id):
            self.node_id = node_id

    kept = learned_preferences_still_applicable(
        corpus.conn, plan_version=after.plan_version_id,
        suppressions=(_Suppression(node.node_id),))
    assert len(kept) == 1

    # The negative twin: a preference about a node the new version really
    # dropped is preserved as a record and NOT applied, because there is nothing
    # left for it to suppress. Without this, "keep everything" would pass too.
    gone = _fresh(corpus)
    gone_result = run_p10(gone)
    index(gone, gone_result)
    dropped = node_labelled(gone_result.tree, "PHYS1401")
    gone_after = _re_version(gone, gone_result, ignore_label="PHYS1401")
    build_destination_index(gone.conn, gone_after, component_version="seam",
                            observed_at=T0)
    assert learned_preferences_still_applicable(
        gone.conn, plan_version=gone_after.plan_version_id,
        suppressions=(_Suppression(dropped.node_id),)) == ()


# --- helpers ------------------------------------------------------------------------


def _re_version(corpus, result, *, new_label: str | None = None,
                ignore_label: str | None = None):
    """One P10 edit on the frozen tree, through P10's own writer, then frozen.

    `apply_review_action` opens a draft from the adopted version and mints a new
    `node_id` for every node it copies, which is the condition under test. The
    action's `subject_ref` is an ORIGIN id, because that is the only identity
    that spans the two versions — matching on `node_id` here would fail to find
    the very node the user acted on, one layer below where §8.8 bites for P11.
    """
    from tree_design.freeze import freeze, frozen_tree
    from tree_design.profiles import build_profiles
    from tree_design.store import apply_review_action, nodes_for_version
    from tree_design.vocabulary import SURFACE_CANVAS
    from tree_design.upstream import accepted_groups

    from p10 import p13_fixtures

    target = node_labelled(result.tree, "PHYS1401")
    # P13's own published gestures, not a third copy of its record shape:
    # `subject_ref` is an ORIGIN id because that is the only identity spanning
    # the two versions, and `apply_review_action` matches on it for exactly the
    # reason §8.8 bites for P11 one layer up.
    action = (
        p13_fixtures.ignore_existing(target.origin_node_id,
                                     plan_version=result.tree.plan_version_id)
        if ignore_label else
        p13_fixtures.rename(target.origin_node_id,
                            plan_version=result.tree.plan_version_id,
                            new_label=new_label))
    counter = iter(range(5_000))
    new_version = apply_review_action(
        corpus.conn, action, new_version_id="plan_after", created_at=T0,
        mint_node_id=lambda: f"after_{next(counter)}",
        component_version="seam")

    groups = {g.group_id: g for g in accepted_groups(
        corpus.reader(), plan_version_id="plan_0")}
    profiles = build_profiles(
        corpus.conn, plan_version_id=new_version, groups_by_id=groups,
        document_types_by_node={}, anchor_excerpts_by_node={},
        user_edits_by_node={}, node_scoped_rejections={})
    freeze(corpus.conn, plan_version_id=new_version, created_at=T0, user_id="jy",
           component_version="seam", surface=SURFACE_CANVAS,
           residual_configuration={},
           approved_branch_ids=tuple(
               n.node_id for n in nodes_for_version(corpus.conn, new_version)
               if n.accepts_placement),
           profiles=profiles, protected_areas=result.protected_areas)
    return frozen_tree(corpus.conn, plan_version=new_version)


def _fresh(corpus):
    """A second, independent corpus in a second database.

    A frozen plan version is immutable (§8.8), so the two-run experiments above
    cannot re-design the same database — the second run has to be a second
    design, over the same evidence, differing only in the one input under test.
    """
    import tempfile
    from pathlib import Path

    from database_agent.db import open_database

    root = Path(tempfile.mkdtemp())
    conn = open_database(root / "agent.sqlite")
    _bootstrap(conn)
    return seed_seam_corpus(conn, root)


# --- the break this file found, and the part that owned it closed --------------------


def test_the_acceptance_the_user_gave_is_visible_under_the_version_it_was_given_in(
        corpus):
    """The positive half, so the xfail below is about a version boundary and not
    about a missing row.

    P9's acceptance is real, recorded through `record_acceptance`, and
    `group_state_as_of` answers `accepted` for the plan version the user gave it
    in. Nothing about the row is wrong.
    """
    from grouping.acceptance import group_state_as_of

    from p10.seam_corpus import GROUP_ID, PLAN_0

    assert group_state_as_of(corpus.conn, group_id=GROUP_ID,
                             plan_version_id=PLAN_0) == "accepted"


def test_an_accepted_group_is_still_accepted_as_of_the_version_p10_froze(corpus):
    """§6.8's group pass, over a tree the user has edited three times.

    THE SAME identity problem as §8.8's, one part further up, and it is the reason
    this file exists. `group_acceptance` is keyed on `plan_version_id`. P10's chain
    opens a NEW plan version for every recorded edit (§8.8: "When the user edits
    the tree, the product should create a draft plan version"), so by the time the
    tree is frozen the acceptance names an ANCESTOR of the adopted version and not
    the adopted version itself. Resolved on the exact id, `group_state_as_of` fell
    back to the SHARED `Group.state` -- `supported`, which is what the group IS and
    not what any version decided -- and `accepted_group_as_of` refused. Every group
    placement raised `GroupNotAcceptedInVersion`, so `place_group` and
    `run_corpus`'s §6.8 pass could not run against a real P10 tree at all.

    Fixed in P9, which is the part that owns "as of a plan version".
    `grouping.acceptance` now resolves the nearest opinion along the version's own
    ancestry (`plan_versions.predecessor_id`), which is §5.12's "the user can
    change the visual organization without destroying the underlying evidence"
    and §8.9's "evolve without destabilizing accepted structure" made operative.
    The other two candidate sites stayed shut: P10 writing P9's table is what
    `test_freeze_is_a_view_over_the_evidence` forbids by name, and P11 asking as of
    an earlier version would have put the version's definition of itself in the
    consumer.

    The chain this corpus actually builds is `plan_0 -> plan_6 -> plan_12 ->
    plan_19(frozen)`, and the acceptance is on `plan_0`. Measured, not inferred:
    the test above reads it under `plan_0`, this one reads it three edits later.
    """
    from placement.groups import accepted_group_as_of

    from p10.seam_corpus import GROUP_ID, PLAN_0

    result = run_p10(corpus)
    index(corpus, result)
    frozen = result.tree.plan_version_id
    # The premise, asserted rather than assumed: the version P10 froze is not the
    # version the user accepted in. Without this the test would still pass the day
    # P10 stopped minting, and would then be proving nothing.
    assert frozen != PLAN_0
    group = accepted_group_as_of(corpus.conn, group_id=GROUP_ID,
                                 plan_version=frozen)
    assert len(group.memberships) == 3
