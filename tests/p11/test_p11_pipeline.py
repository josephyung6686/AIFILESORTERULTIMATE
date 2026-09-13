"""§6.12's nine steps, driven end to end over the real chain.

Every seam here is the live one. Retrieval is `placement.retrieval.retrieve`,
scoring is `placement.scoring.assess`, the privacy gate is P7's own
`ClassificationStore` and `current_policy`, the acceptance read is P9's
`group_state_as_of`, the destination index is built from P10's frozen tree, and
the decisions land in the real append-only table under the real unique index.

The one fake in this file is `call_placement`, monkeypatched in four tests so a
Site C verdict can be forced without a live model. `run_call` needs a released
transport, and P8's own answer is exercised for real in
`tests/integration/test_p11_p8_seam.py` and
`tests/integration/test_p11_pipeline_live.py`, which drive this same pipeline
through P8's real entry point with no fake at all.
"""
from __future__ import annotations

import dataclasses
import json
from decimal import Decimal

import pytest
from types import SimpleNamespace

from database_agent.budget import set_ceiling
from database_agent.files_table import get_file, record_file
from llm_harness.budgets import create_budget_schema
from llm_harness.harness import CallDependencies
from llm_harness.records import EvidenceItem, P8Verdict
from llm_harness.schema import create_llm_schema
from llm_harness.vocabulary import (
    ABSTAIN as P8_ABSTAIN, ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT as P8_ACCEPT_DIRECT, CHOOSE_RESIDUAL_DESTINATION,
    LEAVE_IN_CURRENT_LOCATION, LEAVE_IN_PLACE as P8_LEAVE_IN_PLACE,
    MOVE_PLAN_ELIGIBLE as P8_MOVE_PLAN_ELIGIBLE,
    NO_SUPPORTED_DESTINATION as P8_NO_SUPPORTED_DESTINATION,
    RETURN_CONFIRMED_GROUP, RETURN_TO_PLACEMENT as P8_RETURN_TO_PLACEMENT,
    VALID_REVIEW_REQUIRED,
)
from evidence_shape.observation import observation_key
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from privacy.release import ModelTarget

from placement import vocabulary as v
from placement.config import CEILINGS, SupportPolicy, placement_limits
from placement.index import build_destination_index
from placement.learning import basis_key_for, record_correction
from placement.records import MatchingFact, Subject
from placement.residual import ResidualSetDecision, record_set_decision
from placement.store import current_decision
from p11.conftest import FIXED_CLOCK, NO_CANONICAL_RULE
from p11.p10_fixtures import FROZEN_TREE
from llm_harness.fixtures import FIXTURE_HANDLE_KEY

#: 0.50 sits BELOW a direct fact alone (3/5 = 0.6) and ABOVE an accepted group
#: alone (2/5 = 0.4). Both halves are asserted below, so a threshold moved out of
#: that band fails loudly instead of turning every placement into an abstention.
#:
#: **THE BAND MOVED WITH `104` §18.2 GAP 13 AND THE NUMBER DID NOT.** It used to
#: read "ABOVE a direct fact alone (3/7 = 0.4286)", which is the defect stated as
#: an intention: the scorer divided by all four deciding weights while retrieval
#: produced two of them, so facts alone could not place and `00`:110's unique
#: direct match needed a group membership to be reachable at all.
def _as_steps(answer):
    """A stub for Site C's call, which since `104` §18.15 is a generator.

    The round trip is a suspension point now -- `pipeline` reaches the seam with
    `yield from`, so the cloud lane can hold several files' calls at once -- and a
    stub that answers outright is not iterable. This makes one out of it: the
    unreachable `yield` is what turns the function into a generator, and `return`
    inside one is exactly what `yield from` hands back. Everything each stub below
    says about the call it stands for is unchanged, including the ones that raise:
    the raise happens on the first advance, which is where the call was made.
    """

    def steps(*args, **kwargs):
        return answer(*args, **kwargs)
        yield  # pragma: no cover - unreachable, and what makes this a generator

    return steps


POLICY = SupportPolicy(policy_id="skeleton-v2", support_scale_max=1.0,
                       minimum_support_threshold=0.5, margin_threshold=0.2)

OBS = observation_key(content_hash="h1", extractor_name="fixture",
                      locator="page-1", raw_value="PHYS1401")

SUBJECT = Subject(kind=v.FILE, file_id="f1", content_hash="h1", group_id=None,
                  member_file_ids=())

#: The evidence that makes the skeleton place, and the arithmetic that makes it
#: place. `assess` normalises by `producible_weight(PRODUCED_CHANNELS)` -- the
#: weights of the channels retrieval can actually produce, `3 + 2 = 5` -- and not
#: by the four-channel constant `104` §18.2 gap 13 removed:
#:
#:   n-course        direct_fact(3) + accepted_group(2) = 5/5 = 1.0
#:   n-course-shared                  accepted_group(2) = 2/5 = 0.4
#:   n-course-alt    expects subject = PHYS1402, which contradicts the file's
#:                   PHYS1401, so retrieval SUPPRESSES it -- a conflict, not a
#:                   candidate, and it populates `conflicts_considered`.
PLACING_GROUPS: tuple[str, ...] = ("g-phys1401", "g-shared")


def _classify(conn, *, file_id="f1", content_hash="h1", protected=False,
              handling_class="personal_non_sensitive"):
    """One P7 classification. Absent, `place_file` blocks -- which is correct."""
    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class=handling_class, protected=protected,
        basis="detector", evidence_refs=(OBS,), reliability_state="direct",
        observed_at=FIXED_CLOCK))


def _policy(conn, *, mode="hybrid", permissions=None):
    set_policy(conn, Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode=mode,
        consent_grants=(), redaction_settings={},
        automatic_move_permissions=permissions or {},
        plan_version="plan-1", set_at=FIXED_CLOCK),
        component_version="P7-test", user_id="u1",
        reason="skeleton fixture policy")


def _real_file(conn, directory, *, name="passport.pdf", body=b"%PDF-1.4 x"):
    """A real P1 row. `may_move_automatically` resolves the content hash by file
    id, so a synthesized id would not exercise P7's predicate at all."""
    directory.mkdir(parents=True, exist_ok=True)
    document = directory / name
    document.write_bytes(body)
    file_id = record_file(
        conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(directory), mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _partition(file_ids, *, protected=False, label="Unassociated"):
    """§7.5's partition, injected. P11 invents no set names (Open question 10)."""
    if not file_ids:
        return ()
    return (
        {"label": label, "member_file_ids": tuple(file_ids),
         "representative_examples": tuple(file_ids[:1]),
         "file_type_distribution": (("pdf", len(file_ids)),),
         "age_range": ("2026-01-01", "2026-08-01"),
         "evidence_availability": "ocr_present",
         "sensitivity_status": "public_low", "protected": protected,
         "weak_graph_neighbours": (),
         "reason_not_placed": "no direct fact reached any legal destination"},
    )


@pytest.fixture()
def skeleton(p11_conn):
    # P8's tables, because the zero-model-call assertions read `llm_verdict` and a
    # count against an absent table would prove nothing.
    create_llm_schema(p11_conn)
    create_budget_schema(p11_conn)
    for key in CEILINGS.values():
        set_ceiling(p11_conn, key, 8)
    _classify(p11_conn)
    _policy(p11_conn)
    build_destination_index(p11_conn, FROZEN_TREE,
                            component_version="P11-test",
                            observed_at=FIXED_CLOCK, canonical=NO_CANONICAL_RULE)
    return p11_conn


def _inputs(conn, **overrides):
    from placement.pipeline import PipelineInputs

    # Every model injection is None: this is a DETERMINISTIC-ONLY run, which §6.6
    # makes a legal run, and `model_path_available()` returns False so step 7 is
    # skipped rather than attempted and failed.
    values = dict(
        plan_version="plan-1", tree=FROZEN_TREE, policy=POLICY,
        limits=placement_limits(conn),
        partition=None, ask_or_abstain=lambda ids: v.ABSTAIN,
        max_return_cycles=1, gate=None, model_client=None, prompt=None,
        residual_prompt=None,
        call_dependencies=None, model_call_request=None, chosen_node_of=None,
        residual_action_of=None, sensitivity_policy=None, model_target=None,
        route_for=None, usage_recorder=None,
        # `104` §18.15: one at a time, which is what this pass did before the
        # lane existed. Stated rather than defaulted, like every field here.
        calls_at_once=1,
        # Nothing to ask about and nothing already answered. Both are
        # required with no default, so a fixture states its position
        # rather than inheriting one.
        ask_about_file=lambda subject: None,
        chosen_by_user=lambda subject: None,
        # The fixture states its position on §6.3's third suppression rather
        # than inheriting one: these are P11's own tests, and the fields this
        # deployment's catalogue binds to a what-or-when role are the fields
        # `_without_kind_only_moves` refuses to move a file on.
        fields_that_cannot_anchor_a_move=frozenset({"work_type", "term"}),
        their_own_folder_made_for_what_it_holds={},
        canonical_value=NO_CANONICAL_RULE,
        the_folder_each_file_is_in={},
        # `00` amendment 7. The fixture states its position: this run names no
        # situation per file and knows no branch's, so the branch rule is inert.
        situation_of=lambda file_id: None,
        the_situation_each_branch_carries={},
        a_move_the_person_has_not_permitted=None,
        p2=None,
    )
    values.update(overrides)
    return PipelineInputs(**values)


def _evidence(**overrides):
    values = dict(
        facts=(MatchingFact(file_fact_id="ff1", field="subject", value="PHYS1401",
                            reliability=v.DIRECT, evidence_ref=OBS),),
        # P8's reference-only metadata, from the dossier builder. P11 holds a
        # field, a value and an observation key and never a location, a span or a
        # basis, so these arrive rather than being synthesised.
        evidence_items=(EvidenceItem(
            evidence_ref=OBS, kind="fact", location="page-1",
            excerpt_span=(0, 8), reliability_state="direct",
            basis="direct-anchor"),),
        group_ids=(), curated_folder_labels=(), semantic_neighbours=(),
        related_files=(), entity_frequency={"PHYS1401": 6},
        generic_entity_frequency=200,
    )
    values.update(overrides)
    return values


def _place(conn, **overrides):
    from placement.pipeline import place_file

    kwargs = dict(subject=SUBJECT, inputs=_inputs(conn),
                  evidence=_evidence(group_ids=PLACING_GROUPS),
                  component_version="P11-test", observed_at=FIXED_CLOCK)
    kwargs.update(overrides)
    return place_file(conn, **kwargs)


# --- the spine ------------------------------------------------------------------


def test_the_pipeline_names_612s_nine_steps_in_612s_order():
    from placement.pipeline import STEPS

    assert len(STEPS) == 9
    assert STEPS[0].startswith("freeze")
    assert STEPS[-1].startswith("reviewable_plan")


def test_every_step_p11_owns_names_a_caller_that_is_actually_invoked():
    """AST reachability, not a reference chain: imported-but-never-called fails.

    Steps 1-2 are P10's and step 8 runs inside P8; 3, 4, 5, 6, 7 and 9 are P11's,
    and each one names the function the pipeline must actually CALL.
    """
    import ast
    import inspect

    from placement import pipeline

    tree = ast.parse(inspect.getsource(pipeline))
    called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                called.add(func.id)
            elif isinstance(func, ast.Attribute):
                called.add(func.attr)
    for step, function in (
            ("retrieve_legal_candidates", "retrieve"),
            ("build_local_graph", "build_node_local_graph"),
            ("suppress_impossible_nodes", "suppressed_nodes"),
            ("identify_child_parent_fallback_or_none", "assess"),
            # `104` §18.15: the seam's suspendable form, which is what the
            # per-file pass drives on the cloud lane; `call_placement` is the
            # same call driven inline and is what `place_group` reaches.
            ("judge_bounded_ambiguity", "call_placement_steps"),
            ("reviewable_plan_of_placements", "surface_residual_sets")):
        assert function in called, (step, function)


# --- §6.6 and §6.10: the deterministic path ---------------------------------------


def test_a_unique_direct_match_is_placed_with_zero_model_calls(skeleton):
    decision = _place(skeleton)
    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == "n-course"
    assert decision.destination.node_role == v.ORDINARY
    assert decision.confidence_class == v.EXACT_FACT_MATCH
    assert decision.review_policy == v.AUTO_ELIGIBLE
    assert skeleton.execute(
        "SELECT count(*) AS c FROM llm_verdict").fetchone()["c"] == 0


def test_the_skeletons_margin_is_measured_and_never_vacuous(skeleton):
    decision = _place(skeleton)
    two = decision.two_condition
    assert two.meets_margin == v.MARGIN_TRUE          # measured, not true_vacuous
    assert two.margin_over_next == 0.6                # (5 - 2) / 5, exactly
    assert two.support_score == 1.0                   # 5/5: all the support
                                                      # this run can produce
    assert two.meets_threshold is True
    assert [a.node_id for a in decision.alternatives] == [
        "n-course", "n-course-shared"]
    # The suppressed node is visible, so the review surface can answer
    # "why not PHYS1402?" (§6.3, Done-means 4).
    assert "n-course-alt" in {node for conflict in decision.conflicts_considered
                              for node in conflict.suppressed_node_ids}


def test_the_direct_fact_alone_clears_the_threshold_and_places(skeleton):
    """`104` §18.2 GAP 13, AND THIS TEST USED TO ASSERT THE DEFECT.

    It was `test_the_direct_fact_alone_does_not_clear_the_threshold`, and what it
    pinned was arithmetic nobody chose: `assess` divided by the sum of all four
    deciding weights (7) while `placement/retrieval.py` produced two of them, so a
    file whose validated facts matched exactly one frozen path scored 3/7 = 0.429
    against a 0.50 bar and abstained. `00`:110 -- "if a file's validated facts
    uniquely match one frozen path, deterministic matching is faster, cheaper and
    more stable" -- was unreachable without an accepted group the file had no
    reason to have, and the screen read "not yet placed" for the strongest
    evidence this product collects.

    Normalised over the channels retrieval declares it produces the same evidence
    is 3/5 = 0.6, above the same unmoved 0.50, and the file places on its facts as
    a direct match with no model call. The two-condition record is unchanged in
    shape: the threshold is still 0.50, still recorded, still binding on the
    accepted-group-alone case the test below keeps.

    SABOTAGE: restore the denominator to the sum of all four weights (7) -- this
    file scores 0.4286, `meets_threshold` goes False, the outcome goes back to
    `abstain`, and `unique_direct_match` is unreachable again.
    """
    decision = _place(skeleton, evidence=_evidence())
    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == "n-course"
    assert decision.two_condition.support_score == 0.6
    assert decision.two_condition.meets_threshold is True
    assert decision.confidence_class == v.EXACT_FACT_MATCH


def test_an_accepted_group_alone_still_does_not_clear_the_threshold(skeleton):
    """The other half of the arithmetic, and the half that keeps the bar a bar.

    `104` §18.2 gap 13 raised the whole producible scale, so a test that only
    proved facts now place would be satisfied by a denominator of 3 -- or of 1 --
    which would place everything. What holds the derivation honest is that group
    membership WITHOUT a fact is 2/5 = 0.4 and still falls short: the weights'
    relative order (`direct fact > accepted group`) is expressed in the outcome
    and not only in the numerator, which is the first time it ever has been.

    SABOTAGE: derive the denominator from the DECIDING channels a candidate
    happens to carry rather than from what the retrieval can produce -- this file
    scores 2/2 = 1.0 and an accepted group with no fact anywhere places
    automatically.
    """
    decision = _place(skeleton, evidence=_evidence(facts=(),
                                                   group_ids=("g-shared",)))
    assert decision.outcome == v.ABSTAIN
    assert decision.two_condition.support_score == 0.4
    assert decision.two_condition.meets_threshold is False


def test_a_mathematical_looking_file_never_produces_math_stuff(skeleton):
    decision = _place(skeleton,
                      evidence=_evidence(facts=(), semantic_neighbours=()))
    assert decision.outcome == v.ABSTAIN
    assert decision.destination is None
    assert decision.abstention_reason == v.NO_SUPPORTED_DESTINATION


#: A policy under which two of this tree's candidates clear the support bar AND
#: neither clears the margin. Both halves have to be arranged, because a sentence
#: about two homes cannot be tested against a tree where one is arithmetically
#: impossible.
#:
#: **BOTH NUMBERS ARE THE FIXTURE'S AND `104` §18.2 GAP 13 MOVED THE SECOND ONE.**
#: Before gap 13 only the threshold needed lowering: every score was over seven,
#: `n-course` reached 3/7 = 0.4286 and `n-course-shared` 2/7 = 0.2857, so 0.25
#: admitted both and their 1/7 = 0.1429 gap failed the 0.2 margin on its own. On
#: the producible scale the same two are 0.6 and 0.4 and the gap is exactly 0.2,
#: which CLEARS a 0.2 margin -- gap 13 working, and the reason `n-course` now
#: places on its facts. So the margin is the number that moves here: at 0.3 the
#: same pair is two supported homes the evidence does not separate, which is the
#: state the sentence under test is about. The threshold stays at 0.25 so that
#: `n-course-shared` is a SUPPORTED home rather than a rival nothing backs --
#: that distinction is the whole point of `multiple_supported_homes` against
#: `low_margin`.
TWO_HOMES_POLICY = SupportPolicy(policy_id="two-homes-v2", support_scale_max=1.0,
                                 minimum_support_threshold=0.25,
                                 margin_threshold=0.3)


def test_a_file_with_two_supported_homes_is_told_it_has_two_homes(skeleton):
    """§3a of `planning/59-FINAL-UX-EVALUATION.md`, in the sentence the user reads.

    The direct fact reaches `n-course` (3/5 = 0.6) and the accepted group reaches
    `n-course-shared` (2/5 = 0.4). Both clear 0.25 on their own; the margin
    between them is 0.2, inside `TWO_HOMES_POLICY`'s 0.3 band. Nothing moves --
    and the record says why in the person's terms, naming the destinations rather
    than complaining about the evidence that produced them.
    """
    decision = _place(skeleton,
                      inputs=_inputs(skeleton, policy=TWO_HOMES_POLICY),
                      evidence=_evidence(group_ids=("g-shared",)))
    assert decision.outcome == v.ABSTAIN
    assert decision.abstention_reason == v.MULTIPLE_SUPPORTED_HOMES
    assert "n-course" in decision.explanation
    assert "n-course-shared" in decision.explanation
    assert "more than one" in decision.explanation
    # The old sentence is false about this file and must be gone: two legal
    # destinations DID clear §6.10's support condition.
    assert "No legal destination cleared" not in decision.explanation


def test_an_ordinary_abstention_still_says_nothing_matched(skeleton):
    # The negative twin of the two tests above and below. A file nothing supports
    # is told so plainly; a fix that gave every abstention a reassuring new voice
    # would pass those two and erase the one honest report of a genuine evidence
    # failure. `104` R-M took the section number out of this sentence and left
    # the finding in it: no folder was a supported home.
    decision = _place(skeleton,
                      evidence=_evidence(facts=(), semantic_neighbours=()))
    assert decision.abstention_reason == v.NO_SUPPORTED_DESTINATION
    assert decision.explanation.startswith(
        "No folder in this plan matched it well enough")
    assert "§" not in decision.explanation
    assert "protected" not in decision.explanation
    assert "more than one" not in decision.explanation


def test_a_file_resembling_an_ignored_folder_abstains(skeleton):
    # Done-means 2's concrete case, §5.10: the user left `Old Downloads` alone, so
    # a file that looks like it belongs there is not placed there -- and the node
    # was never even retrievable.
    decision = _place(skeleton, evidence=_evidence(
        facts=(), curated_folder_labels=("Old Downloads",)))
    assert decision.outcome == v.ABSTAIN
    assert "n-ignored" not in {a.node_id for a in decision.alternatives}


def test_the_decision_is_stored_and_its_event_appended(skeleton):
    decision = _place(skeleton)
    row = skeleton.execute(
        "SELECT record_id, node_id FROM placement_decisions").fetchone()
    assert row["record_id"] == decision.decision_id
    assert row["node_id"] == "n-course"
    events = [r["event_type"] for r in skeleton.execute(
        "SELECT event_type FROM events")]
    assert v.CANDIDATE_RETRIEVAL in events
    assert v.RECOMMENDATION_EMITTED in events


def test_an_unclassified_file_is_blocked_and_not_placed(p11_conn):
    # P7's detector abstains often and by design, so this is the ORDINARY path on
    # a real corpus: no classification means blocked, never a default to public --
    # and blocked means a decision the person can see, not a refusal.
    from privacy.classification import UNREADABLE_UNCLASSIFIED

    for key in CEILINGS.values():
        set_ceiling(p11_conn, key, 8)
    _policy(p11_conn)
    build_destination_index(p11_conn, FROZEN_TREE, component_version="P11-test",
                            observed_at=FIXED_CLOCK, canonical=NO_CANONICAL_RULE)
    decision = _place(p11_conn)
    assert decision.privacy.handling_class == UNREADABLE_UNCLASSIFIED
    assert decision.review_policy == v.BLOCKED_PENDING_USER
    # Not protected. `protected` is P7's FLAG and an absent record carries none;
    # inventing one here would file a file nobody read alongside a passport.
    assert decision.privacy.protected is False
    # It is on disk like any other decision, which is what stops it being the
    # silent omission the standing rule forbids.
    assert current_decision(
        p11_conn, plan_version="plan-1",
        subject_ref="file:f1:h1").review_policy == v.BLOCKED_PENDING_USER


def test_one_unclassified_file_does_not_refuse_the_corpus_it_arrived_in(skeleton):
    """The break itself: one abstention used to take down the whole run.

    `privacy_state_for` raised `ClassificationRequired` and `run_corpus` did not
    catch it, so a person with ten thousand files and one ambiguous scan got a
    traceback and no plan at all. The detector declining to guess is CORRECT --
    `00` requires abstention where the evidence does not support a reading -- and
    a product built to abstain cannot let one abstention refuse everything else.
    """
    from placement.pipeline import run_corpus
    from privacy.classification import UNREADABLE_UNCLASSIFIED

    unknown = Subject(kind=v.FILE, file_id="f-unclassified", content_hash="h-u",
                      group_id=None, member_file_ids=())
    result = run_corpus(
        skeleton, subjects=(SUBJECT, unknown), group_ids=(),
        inputs=_inputs(skeleton, partition=_partition),
        # f1 places on the full producible support; every group member gets the
        # ambiguous shape so §7 has something left to surface.
        evidence_for=lambda file_id: (
            _evidence(group_ids=PLACING_GROUPS) if file_id == "f1"
            else _evidence(**AMBIGUOUS)),
        component_version="P11-test", observed_at=FIXED_CLOCK)

    by_file = {d.subject.file_id: d for d in result.decisions}
    # BOTH files came back. The unclassified one is present and counted, and the
    # classified one placed exactly as it would have on its own.
    assert set(by_file) == {"f1", "f-unclassified"}
    assert by_file["f1"].outcome == v.PLACE
    assert by_file["f1"].privacy.handling_class == "personal_non_sensitive"
    # And the one nothing looked at is blocked -- present, explained, and not
    # actionable until somebody says what it is.
    blocked = by_file["f-unclassified"]
    assert blocked.review_policy == v.BLOCKED_PENDING_USER
    assert blocked.privacy.handling_class == UNREADABLE_UNCLASSIFIED
    assert blocked.privacy.protected is False


# --- §8.7: the user's own correction, before any `place` --------------------------


def test_a_destination_the_user_rejected_is_never_resurfaced(skeleton):
    placed = _place(skeleton)
    record_correction(
        skeleton, decision=placed, action=v.ACTION_REJECT,
        polarity=v.POLARITY_REJECT, scope=v.FILE, subject_id="f1",
        basis_key=basis_key_for(subject_id="f1", node_id="n-course"),
        user_id="u1", component_version="P11-test", observed_at=FIXED_CLOCK,
        explanation="not this course")
    again = _place(skeleton)
    # n-course is gone, and n-course-shared alone scores 2/7 -- below 0.50.
    assert again.outcome == v.ABSTAIN
    assert "n-course" not in {a.node_id for a in again.alternatives}


def test_the_suppression_is_read_and_not_assumed(skeleton):
    # The negative twin. Without the correction the same call places, so the test
    # above is measuring the suppression rather than a pipeline that always fails.
    assert _place(skeleton).outcome == v.PLACE


# --- §8.4 and Design:185: protected material -------------------------------------


def test_protected_material_is_never_automatically_moved(skeleton, tmp_path):
    """`104` §18.2 gap 4. The outcome is not a placement at all.

    It used to be `place` with `review_policy=review_required` -- a held proposal
    -- and `tools.groundtruth.score.protected_verdict` counts that as `filed`:
    "a protected file sitting on screen under 'we suggest this folder; confirm' is
    the product having decided about protected material on its own". §18.7 says
    protected material is never filed automatically and is filed one at a time by
    the person, so the run leaves it exactly where it is.

    This file is the deterministic path's own unique direct match: no model is
    configured, no gate is met, and it is still not filed.
    """
    file_id, content_hash = _real_file(skeleton, tmp_path / "corpus")
    _classify(skeleton, file_id=file_id, content_hash=content_hash,
              protected=True, handling_class="sensitive_personal")
    subject = Subject(kind=v.FILE, file_id=file_id, content_hash=content_hash,
                      group_id=None, member_file_ids=())
    decision = _place(skeleton, subject=subject)
    assert decision.outcome == v.ABSTAIN
    assert decision.destination is None
    assert decision.abstention_reason == v.PRIVACY_BLOCKED
    assert decision.privacy.protected is True
    assert "protected material" in decision.explanation


def test_a_policy_that_explicitly_permits_the_move_is_read_from_p7(skeleton,
                                                                   tmp_path):
    # The discriminating twin: the same protected file, and a P7 policy that names
    # it. Without this, `review_policy_for`'s protected gate would look like a rule
    # nothing could ever satisfy -- and `may_move_automatically` would never run.
    file_id, content_hash = _real_file(skeleton, tmp_path / "corpus")
    _classify(skeleton, file_id=file_id, content_hash=content_hash,
              protected=True, handling_class="sensitive_personal")
    _policy(skeleton, permissions={file_id: True})
    subject = Subject(kind=v.FILE, file_id=file_id, content_hash=content_hash,
                      group_id=None, member_file_ids=())
    decision = _place(skeleton, subject=subject)
    assert decision.review_policy == v.AUTO_ELIGIBLE


# --- §6.12 step 7: the model, and only for a bounded ambiguity --------------------


def _verdict(outcome=ACCEPT_CONTEXT_SUPPORTED,
             disposition=VALID_REVIEW_REQUIRED, reasons=(),
             requires_review=True) -> P8Verdict:
    return P8Verdict(
        verdict_id="vd-1", dossier_id="ds-1", claim_ref="claim-1",
        outcome=outcome, disposition=disposition, reasons=tuple(reasons),
        may_propose=True, requires_review=requires_review, citations_checked=(),
        scope="file", validator_version="1", policy_version="policy-1",
        plan_version="plan-1")


#: The two targets a placement run can be configured with. `_model_inputs`
#: names the local one by default; a test that asks what a CLOUD target may be
#: given overrides `model_target` with the other.
LOCAL_TARGET = ModelTarget(locality="local", model_id="llama-local",
                           provider="on-device")
CLOUD_TARGET = ModelTarget(locality="cloud", model_id="cloud-judge",
                           provider="provider")


def _model_call_request(*, subject_ref, evidence_items, max_dossier_tokens):
    """A real P7 release request. `DossierRequest` refuses anything else, which
    is what makes the assertions below a binding against the live seam."""
    from privacy.items import Excerpt, TextSpan
    from privacy.release import ModelCallRequest, Target

    return ModelCallRequest(
        stage="placement", target=Target(file_ids=(subject_ref.split(":")[1],)),
        model_target=LOCAL_TARGET,
        requested_items=tuple(
            Excerpt(observation_key=item.evidence_ref,
                    span=TextSpan(start=0, end=8), reason="anchor excerpt")
            for item in evidence_items),
        prompt_template_id="template.placement",
        prompt_fingerprint="fp-canonical",
        max_dossier_tokens=max_dossier_tokens)


def _call_dependencies():
    """A real `CallDependencies` with the two P11 fills left None on purpose, so
    the assertions below prove the pipeline set them."""
    from decimal import Decimal

    from llm_harness.budgets import ScanBudget

    return CallDependencies(
        proposal_class=None, basis_key=None, learning_scope=None,
        learning_subject_id=None, evidence_resolver=lambda key: "span-1",
        site_dependencies=None, contradicts=lambda *_a, **_k: False,
        unreduced_fits=True, summarized_fits=False, anchors_fit=False,
        split_shard_fits=(), split_shards=(),
        scan_budget=ScanBudget(scan_id="scan-p11", corpus_file_count=1000,
                               max_calls_per_1000_files=4,
                               max_estimated_cost=Decimal("10"),
                               min_calls_per_scan=0),
        estimated_cost=Decimal("1"), actual_cost=Decimal("1"),
        allowed_vocabulary=None, folder_levels=(), policy_version="policy-1",
        wire_handle_key=FIXTURE_HANDLE_KEY)


def _model_inputs(conn, **overrides):
    # `ratified=True`: these tests mean the model path to APPLY. A bare stand-in
    # answers `False` to `prompt.ratified`, which is the observe abstention and
    # the safe default -- a prompt that says nothing is not acted on.
    # TWO PROMPTS, one per placement site. `_judge_with_model` serves C and D and
    # reads `prompt_for(call_site)`, so a fixture that supplied only C's would send
    # every residual call under C's text -- which is the defect the field exists to
    # remove, re-created in the fixture.
    values = dict(gate=object(), model_client=object(),
                  prompt=SimpleNamespace(ratified=True),
                  residual_prompt=SimpleNamespace(ratified=True),
                  call_dependencies=_call_dependencies(),
                  model_call_request=_model_call_request,
                  chosen_node_of=lambda _verdict: "n-course-shared",
                  sensitivity_policy=lambda *_a, **_k: True,
                  # The target `_model_call_request` names, stated once more
                  # where §8.4's gate can read it BEFORE the request is built
                  # (`104` R-118).
                  model_target=LOCAL_TARGET)
    values.update(overrides)
    return _inputs(conn, **values)


#: A bounded ambiguity, in the arithmetic. TWO accepted groups reach two
#: different nodes -- `g-phys1401` reaches `n-course` and `g-shared` reaches
#: `n-course-shared`, both 2/5 = 0.4 -- and the semantic channel reaches
#: `n-general` (0). Neither clears the 0.50 threshold, the margin between them is
#: exactly 0.0, and so `unique_direct_match` is False, `needs_model_call` is True,
#: and the deterministic answer alone would be `low_margin`.
#:
#: **IT USED TO BE A DIRECT FACT AGAINST AN ACCEPTED GROUP, and `104` §18.2 gap
#: 13 is why it cannot be any more.** Over the old denominator of seven that pair
#: was 0.4286 against 0.2857: neither cleared 0.50 and their 0.1429 gap was inside
#: the margin, so it read as ambiguous. It was never ambiguity -- it was a scale
#: that put the strongest evidence this product collects below its own bar. On
#: the producible scale the same pair is 0.6 against 0.4, the direct match wins by
#: exactly the margin, and asking a model about it would be the round trip §6.6
#: forbids. Genuine ambiguity is two candidates the evidence reaches EQUALLY, so
#: that is what this fixture now is. No fact is stated, which is also truer to the
#: case the model path exists for: `00`:110 calls a model in when a file "is an
#: accepted context member but lacks a key branch-level fact".
AMBIGUOUS = dict(facts=(), group_ids=("g-phys1401", "g-shared"),
                 semantic_neighbours=("n-general",))


def test_the_model_path_is_reached_when_the_deterministic_one_is_ambiguous(
        skeleton, monkeypatch):
    import placement.pipeline as pipeline

    seen = {}

    def _fake_call(conn, request, **kwargs):
        seen["site"] = request.call_site
        seen["allowed"] = kwargs["call_dependencies"].allowed_vocabulary
        seen["snapshot"] = request.evidence_snapshot_id
        seen["proposal_class"] = kwargs["call_dependencies"].proposal_class
        return _verdict()

    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(_fake_call))
    decision = _place(skeleton, inputs=_model_inputs(skeleton),
                      evidence=_evidence(**AMBIGUOUS))

    assert seen["site"] == "C_placement"
    # The single most load-bearing value P11 hands P8: Site C rejects anything
    # outside it as INVENTED_NODE, and it is P11's index, never the caller's.
    assert "n-course" in seen["allowed"]
    assert "n-ignored" not in seen["allowed"]
    # Required BEFORE the spend (harness.py:154-165) and minted by nobody else.
    assert seen["snapshot"].startswith("snap-")
    assert seen["proposal_class"] == v.PLACEMENT
    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == "n-course-shared"
    assert decision.confidence_class == v.CONTEXT_SUPPORTED_GROUP_MATCH
    assert decision.review_policy == v.REVIEW_REQUIRED


# --- `104` R-77: §13.6's schema half, the projection half ------------------------
#
# The amended C row's line 33: *"folder_levels lists, for each candidate node, the
# levels of the tree that node sits under, each by its name and the value that
# names its folder."* The projection is a read of the frozen tree's index entries
# and is set beside `allowed_vocabulary`, because it is a projection OF it.


def _folder_levels_seen(skeleton, monkeypatch, *, prompt):
    import placement.pipeline as pipeline

    seen = {}

    def _fake_call(conn, request, **kwargs):
        seen["allowed"] = kwargs["call_dependencies"].allowed_vocabulary
        seen["levels"] = kwargs["call_dependencies"].folder_levels
        return _verdict()

    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(_fake_call))
    _place(skeleton, inputs=_model_inputs(skeleton, prompt=prompt),
           evidence=_evidence(**AMBIGUOUS))
    return seen


def test_under_a_row_that_lists_no_levels_the_c_call_projects_nothing(
        skeleton, monkeypatch):
    """The row site C observes today says `folder_levels` is EMPTY at this site,
    and the builder is told so by `PromptDefinition.lists_folder_levels`. This is
    why `tests/integration/test_r37_single_branch_is_byte_identical.py` needs no
    recapture: the dossier this call assembles is the one it always assembled."""
    seen = _folder_levels_seen(skeleton, monkeypatch,
                               prompt=SimpleNamespace(ratified=True))

    assert seen["levels"] == ()


def test_under_the_amended_row_each_candidate_carries_its_own_levels(
        skeleton, monkeypatch):
    """MEASURED: every offered node's chain, by the level's own field key and the
    value that named the folder, read off the frozen tree and nothing else.

    SABOTAGE: point the projection at anything but `IndexEntry.expected_values`
    and these pairs stop being P10's. `n-course` is `subject=PHYS1401` because
    `p10_fixtures` wrote that `ExpectedValue` on it; no line of P11 composes it.
    """
    seen = _folder_levels_seen(
        skeleton, monkeypatch,
        prompt=SimpleNamespace(ratified=True, lists_folder_levels=True))
    levels = seen["levels"]

    assert levels
    # Every level belongs to a node the model may actually answer with: the two
    # are one computation, and `dossier._folder_levels_body` refuses the call
    # outright when they disagree.
    assert {level.node for level in levels} <= set(seen["allowed"])
    assert ("n-course", "subject", "PHYS1401") in {
        (level.node, level.level, level.value) for level in levels}


def test_a_node_the_tree_named_no_level_for_is_listed_with_no_levels(
        skeleton, monkeypatch):
    """R-17's still-open half, pinned as the silence it is rather than as an
    assertion. `n-general` is a scoped fallback and `n-academics` is a root
    branch; `p10_fixtures` gives each of them `expected_values=()`, because a
    level with no P6 field behind it writes no `ExpectedValue` (Contract W4.3)
    and a branch whose values went to its children keeps none of its own. The
    projection says nothing about such a node, which is what P10 gave it to say.
    """
    seen = _folder_levels_seen(
        skeleton, monkeypatch,
        prompt=SimpleNamespace(ratified=True, lists_folder_levels=True))

    assert "n-general" in seen["allowed"]
    assert not [level for level in seen["levels"] if level.node == "n-general"]


# --- `104` R-165: the record says WHO chose the destination ----------------------
#
# READ OFF THE STORED BODY AND NOT THE RETURNED OBJECT, in every one of these. The
# defect R-165 names is that the pipeline KNEW and the scoreboard could not read
# it, so an assertion against the dataclass in hand would pass against a field that
# never reached the table `tools.groundtruth` opens. `store._payload` is
# `asdict(decision)`, and this is the shape the harness parses.


def _stored_body(conn, decision):
    row = conn.execute(
        "SELECT payload FROM placement_decisions WHERE record_id = ?",
        (decision.decision_id,)).fetchone()
    return json.loads(row["payload"])


def test_the_deterministic_path_records_that_the_rules_decided(skeleton):
    """No model is configured here, so §13.5's fallback placed this file.

    The same run as `test_a_unique_direct_match_is_placed_with_zero_model_calls`,
    asked the question that test cannot: an empty `llm_verdict` says no call was
    made, and this says the DECISION admits it -- which is the half a reader
    holding one row can act on.
    """
    decision = _place(skeleton)
    assert decision.outcome == v.PLACE
    assert _stored_body(skeleton, decision)["decided_by"] == v.DECIDED_BY_RULE


def test_a_model_chosen_destination_is_recorded_as_the_models(skeleton,
                                                              monkeypatch):
    """A site C verdict P8 validated named this node, and the row says so.

    Sabotage twin for the test above: a `decided_by` hard-coded to either word
    passes one of the two and fails this pair. That is the whole of R-165 -- until
    the field existed these two runs were indistinguishable on every stored value
    except the prose of `explanation`.
    """
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(lambda *_a, **_k: _verdict()))
    decision = _place(skeleton, inputs=_model_inputs(skeleton),
                      evidence=_evidence(**AMBIGUOUS))

    assert decision.destination.node_id == "n-course-shared"
    assert _stored_body(skeleton, decision)["decided_by"] == v.DECIDED_BY_MODEL


def test_a_destination_the_person_named_is_recorded_as_theirs(skeleton):
    """§13's fourth consequence: an answer is read before retrieval runs at all.

    Neither of the other two words would be true here, and both would be worse
    than silence: `model` credits a judge nobody consulted, and `rule` says the
    engine decided what the person had just told it.
    """
    decision = _place(skeleton, inputs=_inputs(
        skeleton, chosen_by_user=lambda subject: "n-course-shared"))

    assert decision.outcome == v.PLACE
    assert decision.evidence_type == v.USER_CONFIRMED
    assert _stored_body(skeleton, decision)["decided_by"] == v.DECIDED_BY_USER


def test_an_abstention_names_no_decider_at_all(skeleton):
    """Nothing was placed, so there is no destination anybody could have chosen.

    The record refuses the other shape outright, and that is what keeps the
    scoreboard's arithmetic honest: a decider on an abstention would be counted
    among placements that never happened.
    """
    decision = _place(skeleton, evidence=_evidence(
        facts=(), evidence_items=(), entity_frequency={}))
    assert decision.outcome == v.ABSTAIN
    assert _stored_body(skeleton, decision)["decided_by"] is None


def test_a_model_choice_outside_the_frozen_tree_places_nothing(skeleton,
                                                               monkeypatch):
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(lambda *_a, **_k: _verdict()))
    with pytest.raises(ValueError):
        _place(skeleton,
               inputs=_model_inputs(skeleton,
                                    chosen_node_of=lambda _v: "n-invented"),
               evidence=_evidence(**AMBIGUOUS))


def test_a_deterministic_only_run_skips_step_seven_rather_than_failing(skeleton):
    # §6.6: a run with no model injections is a CORRECT run. The same ambiguous
    # evidence that reaches the model above abstains here, and issues no call.
    decision = _place(skeleton, evidence=_evidence(**AMBIGUOUS))
    assert decision.outcome == v.ABSTAIN
    assert skeleton.execute(
        "SELECT count(*) AS c FROM llm_verdict").fetchone()["c"] == 0


def test_a_local_only_file_abstains_before_any_dossier_is_assembled(skeleton,
                                                                    monkeypatch,
                                                                    tmp_path):
    import placement.pipeline as pipeline

    def _never(*_a, **_k):
        raise AssertionError("§8.4's gate must be asked BEFORE the dossier")

    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(_never))
    file_id, content_hash = _real_file(skeleton, tmp_path / "corpus",
                                       name="secret.pdf", body=b"%PDF-1.4 s")
    _classify(skeleton, file_id=file_id, content_hash=content_hash,
              protected=True, handling_class="sensitive_personal")
    subject = Subject(kind=v.FILE, file_id=file_id, content_hash=content_hash,
                      group_id=None, member_file_ids=())
    decision = _place(skeleton, subject=subject,
                      inputs=_model_inputs(skeleton),
                      evidence=_evidence(**AMBIGUOUS))
    assert decision.outcome == v.ABSTAIN
    assert decision.abstention_reason == v.PRIVACY_BLOCKED
    # `00` on this material: sensitive personal material is not the same thing as
    # `Numbers.app`. A passport is never a low-confidence extraction; it is
    # material the product declined to place ON PURPOSE, and the record has to
    # say that, because a person told their passport "failed to place" concludes
    # the product is broken rather than careful.
    assert "protected material" in decision.explanation
    assert "left exactly where it is" in decision.explanation
    assert "No legal destination cleared" not in decision.explanation


def test_an_offline_install_says_so_rather_than_naming_the_file_sensitive(
        skeleton, monkeypatch, tmp_path):
    """The negative twin of the passport. Same `privacy_blocked`, different cause.

    §8.4's gate closes for two unrelated reasons: this file is protected, or this
    install may send nothing anywhere. Telling an ordinary spreadsheet that it is
    "protected material" would be as wrong in the other direction, so the record
    reads `privacy.protected` and says which of the two happened.

    A CLOUD target, since `104` R-118: the mode forbids the cloud and nothing
    else, so a local model may now be asked about this file and the sentence
    below would be false of it. The install this test describes is one whose
    only configured model is off the device.
    """
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(lambda *_a, **_k: pytest.fail("§8.4 gates first")))
    file_id, content_hash = _real_file(skeleton, tmp_path / "corpus",
                                       name="budget.pdf", body=b"%PDF-1.4 b")
    _classify(skeleton, file_id=file_id, content_hash=content_hash,
              protected=False, handling_class="public_low")
    _policy(skeleton, mode="offline")
    subject = Subject(kind=v.FILE, file_id=file_id, content_hash=content_hash,
                      group_id=None, member_file_ids=())
    decision = _place(skeleton, subject=subject,
                      inputs=_model_inputs(skeleton, model_target=CLOUD_TARGET),
                      evidence=_evidence(**AMBIGUOUS))
    assert decision.abstention_reason == v.PRIVACY_BLOCKED
    assert "protected material" not in decision.explanation
    # `104` R-M: the same distinction, said without citing §8.4 at the person.
    assert "privacy settings do not let one be asked" in decision.explanation
    assert "§" not in decision.explanation


# --- `104` R-118: a local model gets a dossier the mode alone kept from it ---------
#
# Measured on the owner's corpus with qwen3:8b configured: 199 placement decisions,
# 176 `abstain privacy_blocked`, 0 site-C dossiers. `privacy_state_for` asked only
# whether the CLOUD was forbidden, and under a local-only mode it always is, so
# every file was `local_only` and `may_assemble_dossier` refused them all without
# knowing the target was on this device. §8.4 in P7's own words: "A LOCAL model is
# permitted under both". The five cases below are the seam, end to end.


def _ordinary_subject(conn, tmp_path, *, name, handling_class="personal_non_sensitive",
                      classify=True):
    file_id, content_hash = _real_file(conn, tmp_path / "corpus",
                                       name=name, body=b"%PDF-1.4 o")
    if classify:
        _classify(conn, file_id=file_id, content_hash=content_hash,
                  protected=False, handling_class=handling_class)
    return Subject(kind=v.FILE, file_id=file_id, content_hash=content_hash,
                   group_id=None, member_file_ids=())


def test_r118_a_local_model_is_asked_about_a_file_the_mode_alone_kept_local(
        skeleton, monkeypatch, tmp_path):
    """(a) `local_model` mode, LOCAL target, `personal_non_sensitive` file: the
    dossier is assembled, site C is asked, and its verdict is what places it."""
    import placement.pipeline as pipeline

    seen = {}

    def _fake_call(conn, request, **kwargs):
        seen["site"] = request.call_site
        seen["target"] = request.model_call_request.model_target.locality
        return _verdict()

    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(_fake_call))
    _policy(skeleton, mode="local_model")
    subject = _ordinary_subject(skeleton, tmp_path, name="notes.pdf")
    decision = _place(skeleton, subject=subject, inputs=_model_inputs(skeleton),
                      evidence=_evidence(**AMBIGUOUS))

    assert seen == {"site": "C_placement", "target": "local"}
    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == "n-course-shared"
    assert decision.confidence_class == v.CONTEXT_SUPPORTED_GROUP_MATCH
    assert decision.privacy.model_eligibility == v.LOCAL_ONLY
    assert decision.privacy.local_only_reasons == (v.MODE_FORBIDS_CLOUD,)


def test_r118_the_same_file_is_still_kept_from_a_cloud_target(
        skeleton, monkeypatch, tmp_path):
    """(b) The twin: the mode forbids the cloud, and a cloud target is refused
    before any dossier exists."""
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(lambda *_a, **_k: pytest.fail("§8.4 gates first")))
    _policy(skeleton, mode="local_model")
    subject = _ordinary_subject(skeleton, tmp_path, name="notes-2.pdf")
    decision = _place(skeleton, subject=subject,
                      inputs=_model_inputs(skeleton, model_target=CLOUD_TARGET),
                      evidence=_evidence(**AMBIGUOUS))

    assert decision.outcome == v.ABSTAIN
    assert decision.abstention_reason == v.PRIVACY_BLOCKED
    assert "privacy settings do not let one be asked" in decision.explanation
    assert skeleton.execute(
        "SELECT count(*) AS c FROM llm_verdict").fetchone()["c"] == 0


def test_r118_protected_material_is_shown_to_no_model_local_included(
        skeleton, monkeypatch, tmp_path):
    """(c) The standing rule, amended `104` §18.7: read on this device, shown to
    the local model only, and to no model off it."""
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(lambda *_a, **_k: pytest.fail("§8.4 gates first")))
    _policy(skeleton, mode="local_model")
    subject = _protected_subject(skeleton, tmp_path, name="passport-r118.pdf")
    decision = _place(skeleton, subject=subject, inputs=_model_inputs(skeleton),
                      evidence=_evidence(**AMBIGUOUS))

    assert decision.outcome == v.ABSTAIN
    assert decision.abstention_reason == v.PRIVACY_BLOCKED
    assert "protected material" in decision.explanation
    assert v.PROTECTED_REASON in decision.privacy.local_only_reasons


def test_r121_a_local_model_is_asked_about_an_unclassified_file(
        skeleton, monkeypatch, tmp_path):
    """(d) Open question 5, answered by the owner in `104` §15.3 (R-121).

    THIS TEST USED TO ASSERT THE OPPOSITE. As
    `test_r118_an_unclassified_file_stays_off_a_local_model_with_the_flag_as_it_is`
    it read P11's own `LOCAL_CALLS_ON_UNCLASSIFIED = False` while `cli.py` pinned
    `True` for the gate and the fact route -- one question answered twice, which
    is R-121 and `104` R-02's shape again. The ruling: an unclassified file MAY
    reach a LOCAL model and never a cloud one, so the 86 unclassified files of the
    owner's local run stop being refused before the gate is asked.

    The dossier gate is what moved. `review_policy_for` still answers
    `blocked_pending_user` for an unclassified subject -- a model naming a folder
    is not a classification -- so the file is placed and held for a person, which
    is the outcome the ruling intends and not a widening of what may be moved.
    """
    import placement.pipeline as pipeline
    from privacy.denial import UNCLASSIFIED_PERMITS_LOCAL

    assert UNCLASSIFIED_PERMITS_LOCAL is True
    seen = {}

    def _fake_call(conn, request, **kwargs):
        seen["site"] = request.call_site
        seen["target"] = request.model_call_request.model_target.locality
        return _verdict()

    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(_fake_call))
    _policy(skeleton, mode="local_model")
    subject = _ordinary_subject(skeleton, tmp_path, name="scan-r121.pdf",
                                classify=False)
    decision = _place(skeleton, subject=subject, inputs=_model_inputs(skeleton),
                      evidence=_evidence(**AMBIGUOUS))

    assert seen == {"site": "C_placement", "target": "local"}
    assert decision.outcome == v.PLACE
    assert v.UNCLASSIFIED_REASON in decision.privacy.local_only_reasons
    # The review policy is untouched by the ruling: nothing has said what kind of
    # material this is, and a model's answer about WHERE it goes does not say.
    assert decision.review_policy == v.BLOCKED_PENDING_USER


def test_r121_the_same_unclassified_file_is_still_refused_a_cloud_target(
        skeleton, monkeypatch, tmp_path):
    """The other half of the ruling: never a cloud one, and not by a knob.

    `unclassified_denies` answers True for `locality="cloud"` before it reads the
    answer to question 5 at all, so nothing about an unclassified file can leave
    the device however that question is answered.
    """
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(lambda *_a, **_k: pytest.fail("§8.4 gates first")))
    _policy(skeleton, mode="hybrid")
    subject = _ordinary_subject(skeleton, tmp_path, name="scan-r121-cloud.pdf",
                                classify=False)
    decision = _place(skeleton, subject=subject,
                      inputs=_model_inputs(skeleton, model_target=CLOUD_TARGET),
                      evidence=_evidence(**AMBIGUOUS))

    assert decision.outcome == v.ABSTAIN
    assert decision.abstention_reason == v.PRIVACY_BLOCKED
    assert v.UNCLASSIFIED_REASON in decision.privacy.local_only_reasons
    assert skeleton.execute(
        "SELECT count(*) AS c FROM llm_verdict").fetchone()["c"] == 0


def test_r118_with_no_model_configured_nothing_changes_and_the_sentence_is_honest(
        skeleton, tmp_path):
    """(e) The offline path. No target, so no dossier and the same abstention as
    before -- and the sentence no longer claims the settings forbid ANY model,
    because they do not: one on this device could be asked, and none is set up."""
    _policy(skeleton, mode="local_model")
    subject = _ordinary_subject(skeleton, tmp_path, name="notes-3.pdf")
    decision = _place(skeleton, subject=subject, inputs=_inputs(skeleton),
                      evidence=_evidence(**AMBIGUOUS))

    assert decision.outcome == v.ABSTAIN
    assert decision.abstention_reason == v.PRIVACY_BLOCKED
    assert "only let one that runs on this device be asked" in decision.explanation
    assert "none is set up" in decision.explanation
    assert "do not let one be asked" not in decision.explanation
    assert "protected material" not in decision.explanation
    assert "§" not in decision.explanation
    assert skeleton.execute(
        "SELECT count(*) AS c FROM llm_verdict").fetchone()["c"] == 0


def test_r118_the_record_says_why_a_file_was_local_only(skeleton, tmp_path):
    """The `privacy` payload carries the reasons, and they survive the store."""
    _policy(skeleton, mode="local_model")
    subject = _protected_subject(skeleton, tmp_path, name="passport-r118-2.pdf")
    decision = _place(skeleton, subject=subject, inputs=_inputs(skeleton),
                      evidence=_evidence(**AMBIGUOUS))

    assert set(decision.privacy.local_only_reasons) == {
        v.MODE_FORBIDS_CLOUD, v.PROTECTED_REASON}
    stored = current_decision(skeleton, plan_version="plan-1",
                              subject_ref=f"file:{subject.file_id}:{subject.content_hash}")
    assert stored.privacy == decision.privacy
    assert stored.privacy.local_only_reasons == decision.privacy.local_only_reasons
    payload = json.loads(skeleton.execute(
        "SELECT payload FROM placement_decisions WHERE plan_version = ? AND "
        "subject_ref = ? AND superseded_by IS NULL",
        ("plan-1", f"file:{subject.file_id}:{subject.content_hash}"),
    ).fetchone()["payload"])
    assert set(payload["privacy"]["local_only_reasons"]) == {
        v.MODE_FORBIDS_CLOUD, v.PROTECTED_REASON}


def test_an_unclassified_file_does_not_read_as_a_passport_or_as_thin_evidence(
        skeleton, monkeypatch, tmp_path):
    """The third cause of `privacy_blocked`, and the sentence a person gets for it.

    `00`: "sensitive personal material is not the same thing as `Numbers.app`" --
    and neither is the same thing as a file nothing has been able to read. Telling
    this person their file is "protected material" claims a finding P7 never made;
    telling them "no legal destination cleared §6.10" blames the evidence for a
    gate that never opened. The record says which of the three happened.

    THE TARGET IS A CLOUD ONE SINCE `104` R-121, and the sentence under test is
    unchanged. The owner's ruling in `104` §15.3 lets an unclassified file reach a
    LOCAL model, so a local target no longer reaches this abstention at all; a
    cloud target still does, because `unclassified_denies` refuses every cloud
    release of an unclassified file before it reads that answer. The explanation
    branch is keyed on `is_unclassified` and not on the target, so this is the
    same sentence for the same reason.
    """
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(lambda *_a, **_k: pytest.fail("§8.4 gates first")))
    file_id, content_hash = _real_file(skeleton, tmp_path / "corpus",
                                       name="scan.pdf", body=b"%PDF-1.4 u")
    # Deliberately NOT classified: P7's detector declined to say anything.
    subject = Subject(kind=v.FILE, file_id=file_id, content_hash=content_hash,
                      group_id=None, member_file_ids=())
    decision = _place(skeleton, subject=subject,
                      inputs=_model_inputs(skeleton, model_target=CLOUD_TARGET),
                      evidence=_evidence(**AMBIGUOUS))
    assert decision.abstention_reason == v.PRIVACY_BLOCKED
    assert "has not been classified" in decision.explanation
    assert "protected material" not in decision.explanation
    assert "No legal destination cleared" not in decision.explanation
    # The decision is blocked rather than merely awaiting a confirmation, because
    # there is nothing yet for a reviewer to confirm it against.
    assert decision.review_policy == v.BLOCKED_PENDING_USER


# --- §6.8 and §6.9: the group plan ------------------------------------------------


def _seeded(conn):
    from p11.p9_fixtures import GROUP_ID, seed_accepted_columbia

    seed_accepted_columbia(conn)
    for file_id in ("f-essay", "f-transcript", "f-scan", "f-duke-essay"):
        _classify(conn, file_id=file_id, content_hash=f"h-{file_id}")
    return GROUP_ID


def test_run_corpus_places_groups_before_files_and_surfaces_the_rest(skeleton):
    from placement.pipeline import run_corpus

    group_id = _seeded(skeleton)
    result = run_corpus(
        skeleton, subjects=(SUBJECT,), group_ids=(group_id,),
        inputs=_inputs(skeleton, partition=_partition),
        # f1 places on the full producible support; every group member gets the
        # ambiguous shape so §7 has something left to surface.
        evidence_for=lambda file_id: (
            _evidence(group_ids=PLACING_GROUPS) if file_id == "f1"
            else _evidence(**AMBIGUOUS)),
        component_version="P11-test", observed_at=FIXED_CLOCK)

    # §6.8 ran: one plan, and the outlier P9 flagged is excluded and explained.
    assert len(result.group_plans) == 1
    assert {o.file_id for o in result.group_plans[0].excluded_outliers} == {
        "f-duke-essay"}
    # Every member decision carries the plan's id, so a review surface shows ONE
    # plan and not four unrelated file moves (§6.8).
    assert {d.group_plan_id for d in result.group_plans[0].member_decisions} == {
        result.group_plans[0].group_plan_id}
    # §6 ran for the standalone file too, and it placed.
    assert any(d.outcome == v.PLACE and d.subject.file_id == "f1"
               for d in result.decisions)
    # §7.5 ran SECOND, over exactly what §6 could not place.
    assert result.residual_sets
    assert set(result.unplaced_file_ids) <= {
        d.subject.file_id for d in result.decisions if d.outcome != v.PLACE}


def test_the_group_plan_is_persisted_and_not_only_returned(skeleton):
    from placement.pipeline import run_corpus

    group_id = _seeded(skeleton)
    result = run_corpus(
        skeleton, subjects=(), group_ids=(group_id,),
        inputs=_inputs(skeleton, partition=_partition),
        evidence_for=lambda file_id: _evidence(group_ids=()),
        component_version="P11-test", observed_at=FIXED_CLOCK)
    row = skeleton.execute(
        "SELECT record_id, group_id FROM placement_group_plans").fetchone()
    assert row is not None, "placement_group_plans had no writer at all"
    assert row["record_id"] == result.group_plans[0].group_plan_id
    assert row["group_id"] == group_id
    events = [r["event_type"] for r in skeleton.execute(
        "SELECT event_type FROM events")]
    assert v.GROUP_PLAN_EMITTED in events


# --- §7: the residual stage -------------------------------------------------------


def _corpus(conn, **overrides):
    from placement.pipeline import run_corpus

    # `AMBIGUOUS` AND NOT THE PLAIN FACT, and `104` §18.2 gap 13 is why. This
    # helper exists for the §7 residual pass, which needs a file §6 did NOT place;
    # the default evidence was a direct fact alone, which used to score 3/7 = 0.429
    # against a 0.50 bar and abstain. It now scores 0.6 and places -- correctly --
    # so every test below it was reading an empty residual set. `AMBIGUOUS` is the
    # shape that still cannot be settled deterministically: two accepted groups
    # reaching two nodes, tied at 0.4, neither supported.
    kwargs = dict(subjects=(SUBJECT,), group_ids=(),
                  inputs=_inputs(conn, partition=_partition),
                  evidence_for=lambda file_id: _evidence(**AMBIGUOUS),
                  component_version="P11-test", observed_at=FIXED_CLOCK)
    kwargs.update(overrides)
    return run_corpus(conn, **kwargs)


def _decide(conn, set_id, choice=None, node_id=None):
    record_set_decision(
        conn, ResidualSetDecision(
            set_id=set_id, plan_version="plan-1",
            choice=choice or v.REVIEW_WITH_MODEL, node_id=node_id,
            decided_at=FIXED_CLOCK),
        component_version="P11-test", observed_at=FIXED_CLOCK, user_id="u1")


def _review(conn, result, **overrides):
    from placement.pipeline import review_residual_sets

    kwargs = dict(result=result, inputs=_model_inputs(conn, partition=_partition),
                  evidence_for=lambda file_id: _evidence(**AMBIGUOUS),
                  component_version="P11-test", observed_at=FIXED_CLOCK)
    kwargs.update(overrides)
    return review_residual_sets(conn, **kwargs)


def _sites(monkeypatch, verdict):
    """Record every call site the run reached, so a test can assert a call did
    NOT happen without also forbidding the §6 pass its own legitimate one."""
    import placement.pipeline as pipeline

    seen = []

    def _fake_call(conn, request, **kwargs):
        seen.append((request.call_site,
                     kwargs["call_dependencies"].proposal_class))
        return verdict

    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(_fake_call))
    return seen


def test_a_surfaced_set_with_no_decision_issues_no_model_call(skeleton,
                                                              monkeypatch):
    # §7.6, SPEC:545-547. Surfaced-and-undecided is the state the gate exists to
    # make visible, and the review pass must leave it alone rather than proceed.
    seen = _sites(monkeypatch, _verdict())
    result = _corpus(skeleton)
    assert result.residual_sets
    assert _review(skeleton, result) == ()
    assert "D_residual" not in {site for site, _ in seen}


def test_a_set_the_user_left_in_place_issues_no_model_call(skeleton, monkeypatch):
    seen = _sites(monkeypatch, _verdict())
    result = _corpus(skeleton)
    _decide(skeleton, result.residual_sets[0].set_id, choice=v.LEAVE_IN_PLACE)
    assert _review(skeleton, result) == ()
    assert "D_residual" not in {site for site, _ in seen}


def test_a_protected_residual_set_is_counted_and_never_opened(skeleton,
                                                              monkeypatch):
    """The standing rule, structurally: marked and counted, never opened.

    `require_model_call_permitted` refuses a protected set BEFORE it looks at the
    decision, so a set of reports and system files cannot be opened by deciding
    it. The set still appears with its count and its reason.
    """
    from placement.residual import ProtectedSetNotReadable

    seen = _sites(monkeypatch, _verdict())
    protected = lambda ids: _partition(ids, protected=True, label="Reports")
    result = _corpus(skeleton, inputs=_inputs(skeleton, partition=protected))
    assert result.residual_sets[0].protected is True
    assert result.residual_sets[0].file_count == 1
    assert result.residual_sets[0].reason_not_placed
    _decide(skeleton, result.residual_sets[0].set_id)
    with pytest.raises(ProtectedSetNotReadable):
        _review(skeleton, result,
                inputs=_model_inputs(skeleton, partition=protected))
    assert "D_residual" not in {site for site, _ in seen}


def test_an_undecided_protected_set_is_left_alone_rather_than_refused(skeleton,
                                                                      monkeypatch):
    # The discriminating twin. A protected set nobody decided is not an error --
    # it is the ordinary state of the review screen -- so the refusal above is
    # measuring "somebody asked to open it" and not "the set exists".
    _sites(monkeypatch, _verdict())
    protected = lambda ids: _partition(ids, protected=True, label="Reports")
    result = _corpus(skeleton, inputs=_inputs(skeleton, partition=protected))
    assert _review(skeleton, result,
                   inputs=_model_inputs(skeleton, partition=protected)) == ()


def test_a_decided_set_reaches_site_d_and_records_one_decision(skeleton,
                                                               monkeypatch):
    seen = _sites(monkeypatch, _verdict(disposition=P8_LEAVE_IN_PLACE))
    result = _corpus(skeleton)
    _decide(skeleton, result.residual_sets[0].set_id)
    written = _review(skeleton, result, inputs=_model_inputs(
        skeleton, partition=_partition,
        residual_action_of=lambda _v: (LEAVE_IN_CURRENT_LOCATION, None)))
    assert ("D_residual", v.RESIDUAL) in seen
    assert len(written) == 1
    assert written[0].origin_stage == v.RESIDUAL
    assert written[0].outcome == v.LEAVE_IN_PLACE
    assert written[0].residual.set_id == result.residual_sets[0].set_id
    # ONE shape: a consumer parses this with no residual-specific branch.
    assert written[0].two_condition.support_threshold == pytest.approx(0.5)


def test_a_residual_place_lands_on_the_review_only_node_the_model_chose(
        skeleton, monkeypatch):
    # This is NOT the §7.4 disposition's own test, and saying so is the point.
    # Every residual decision carries `requires_review=True` on its two-condition
    # figures, so `review_policy_for` would answer `review_required` here even if
    # the disposition were dropped -- a sabotage of the disposition argument in
    # `_residual_decision` leaves this test GREEN.
    # `test_a_review_only_destination_blocks_an_otherwise_automatic_placement`
    # below is where the disposition is actually measured, on the §6 path, where
    # nothing else forces review.
    _sites(monkeypatch, _verdict())
    result = _corpus(skeleton)
    _decide(skeleton, result.residual_sets[0].set_id)
    written = _review(skeleton, result, inputs=_model_inputs(
        skeleton, partition=_partition,
        residual_action_of=lambda _v: (CHOOSE_RESIDUAL_DESTINATION,
                                       "n-review-later")))
    assert written[0].destination.node_id == "n-review-later"
    assert written[0].review_policy == v.REVIEW_REQUIRED
    # `104` R-165 on the §7 path. A site D verdict chose this node and P8 validated
    # it exactly as it validates site C's, so `rule` here would under-count the
    # model's share by every set a person sent to review.
    assert written[0].decided_by == v.DECIDED_BY_MODEL


def test_a_residual_destination_outside_the_frozen_tree_places_nothing(skeleton,
                                                                       monkeypatch):
    _sites(monkeypatch, _verdict())
    result = _corpus(skeleton)
    _decide(skeleton, result.residual_sets[0].set_id)
    with pytest.raises(ValueError):
        _review(skeleton, result, inputs=_model_inputs(
            skeleton, partition=_partition,
            residual_action_of=lambda _v: (CHOOSE_RESIDUAL_DESTINATION,
                                           "n-invented")))


def test_a_site_d_verdict_p8_rejected_is_never_acted_on(skeleton, monkeypatch):
    from llm_harness.vocabulary import REJECT as P8_REJECT

    _sites(monkeypatch, _verdict(outcome=P8_REJECT, disposition="rejected"))
    result = _corpus(skeleton)
    _decide(skeleton, result.residual_sets[0].set_id)
    written = _review(skeleton, result, inputs=_model_inputs(
        skeleton, partition=_partition,
        residual_action_of=lambda _v: (CHOOSE_RESIDUAL_DESTINATION, "n-course")))
    assert written[0].outcome == v.ABSTAIN
    assert written[0].destination is None


def test_a_site_d_verdict_that_abstains_is_never_acted_on(skeleton, monkeypatch):
    """The twin of the rejection above, and site D's half of the observe lever.

    `_observed_only` rewrites an unratified site's verdict to `abstain` and says
    both callers then take "their existing abstention path without consulting a
    resolver". That was true at C, where `transcribe` turns every non-`place`
    outcome into an abstention, and false here: `abstain` is not `reject`, so the
    resolver was consulted and an unratified D ended the run on the first file of a
    set the person had sent to a model.

    A RATIFIED D IS UNCHANGED BY THE SAME GUARD, which is why it is a guard rather
    than a new outcome: `_residual_site` rewrites the model's own `abstain` action
    to exactly this verdict, and `outcome_for_action` answers
    `(abstain, no_supported_destination)` for it -- the decision written below is
    the decision the resolver path wrote.
    """
    def _never_reached(_verdict):
        raise AssertionError(
            "an abstaining Site D verdict has no action to apply, and consulting "
            "a resolver about one is how the observe lever leaked at this site")

    _sites(monkeypatch, _verdict(outcome=P8_ABSTAIN, disposition=P8_ABSTAIN,
                                 requires_review=False))
    result = _corpus(skeleton)
    _decide(skeleton, result.residual_sets[0].set_id)
    written = _review(skeleton, result, inputs=_model_inputs(
        skeleton, partition=_partition, residual_action_of=_never_reached))

    assert len(written) == 1
    assert written[0].outcome == v.ABSTAIN
    assert written[0].abstention_reason == v.NO_SUPPORTED_DESTINATION
    assert written[0].destination is None


def test_a_site_d_weak_verdict_still_reaches_the_resolver(skeleton, monkeypatch):
    """The discrimination the guard above has to make, asserted from the other side.

    `mark_review_later` arrives as `weak` -- `_residual_site` rewrites it there --
    and it IS one of §7.7's eight actions, so it is read from the response like any
    other. A guard that swept `weak` in with `abstain` would turn every request to
    look at a file later into "no supported destination".
    """
    from llm_harness.vocabulary import (
        MARK_REVIEW_LATER as P8_MARK_REVIEW_LATER,
        REVIEW_LATER as P8_REVIEW_LATER, WEAK as P8_WEAK,
    )

    # `may_propose` is False by the record's own rule: `weak` forbids True, and a
    # request to look at a file later proposes no move.
    _sites(monkeypatch, dataclasses.replace(
        _verdict(), outcome=P8_WEAK, disposition=P8_REVIEW_LATER,
        requires_review=False, may_propose=False))
    result = _corpus(skeleton)
    _decide(skeleton, result.residual_sets[0].set_id)
    written = _review(skeleton, result, inputs=_model_inputs(
        skeleton, partition=_partition,
        residual_action_of=lambda _v: (P8_MARK_REVIEW_LATER, None)))

    assert written[0].outcome == v.MARK_REVIEW_LATER


def test_the_residual_action_is_refused_when_no_resolver_was_injected(skeleton,
                                                                      monkeypatch):
    # §7.7's action lives in the model's response, which P8 validates and P11
    # never holds. Absent means refuse rather than read the verdict's own coarser
    # `disposition` as if it were one of the eight.
    from placement.pipeline import ResidualActionUnavailable

    _sites(monkeypatch, _verdict())
    result = _corpus(skeleton)
    _decide(skeleton, result.residual_sets[0].set_id)
    with pytest.raises(ResidualActionUnavailable):
        _review(skeleton, result, inputs=_model_inputs(
            skeleton, partition=_partition, residual_action_of=None))


# --- §7.9: the loop back into §6 --------------------------------------------------


def test_a_return_hands_the_file_back_to_placement_and_links_the_loop(
        skeleton, monkeypatch):
    _sites(monkeypatch, _verdict(disposition=P8_RETURN_TO_PLACEMENT))
    result = _corpus(skeleton)
    _decide(skeleton, result.residual_sets[0].set_id)
    written = _review(
        skeleton, result,
        inputs=_model_inputs(skeleton, partition=_partition,
                             residual_action_of=lambda _v: (
                                 RETURN_CONFIRMED_GROUP, "g-phys1401")),
        evidence_for=lambda file_id: _evidence(group_ids=PLACING_GROUPS))

    returned = [d for d in written if d.outcome == v.RETURN_TO_PLACEMENT]
    assert len(returned) == 1
    assert returned[0].return_target.kind == v.CONFIRMED_DOMAIN_GROUP
    # §7.9: the file actually went back through §6, and the second decision names
    # the residual one that handed it back.
    live = current_decision(skeleton, plan_version="plan-1",
                            subject_ref="file:f1:h1")
    assert live.returned_from == returned[0].decision_id
    assert live.outcome == v.PLACE
    events = [r["event_type"] for r in skeleton.execute(
        "SELECT event_type FROM events")]
    assert v.RETURN_ISSUED in events


def test_the_return_loop_refuses_without_the_injected_bound(skeleton,
                                                            monkeypatch):
    # SPEC Open question 8 is open: an unbounded loop is a replay that never
    # terminates, so absent means refuse rather than loop.
    from placement.residual import ReturnCycleLimitRequired

    _sites(monkeypatch, _verdict(disposition=P8_RETURN_TO_PLACEMENT))
    result = _corpus(skeleton)
    _decide(skeleton, result.residual_sets[0].set_id)
    with pytest.raises(ReturnCycleLimitRequired):
        _review(
            skeleton, result,
            inputs=_model_inputs(skeleton, partition=_partition,
                                 max_return_cycles=None,
                                 residual_action_of=lambda _v: (
                                     RETURN_CONFIRMED_GROUP, "g-phys1401")),
            evidence_for=lambda file_id: _evidence(group_ids=PLACING_GROUPS))


# --- §8.5: P2 measures the run ----------------------------------------------------


def test_a_p2_run_records_both_stages_with_their_dimensions(skeleton,
                                                            p11_version_tuple,
                                                            p2_run_id):
    from placement.pipeline import P2Run

    _place(skeleton, inputs=_inputs(skeleton, p2=P2Run(
        run_id=p2_run_id, version_tuple_ref=p11_version_tuple,
        upstream_stage_refs=())))
    stages = {row["stage_id"] for row in skeleton.execute(
        "SELECT stage_id FROM stage_output")}
    assert v.CANDIDATE_NODE_RETRIEVAL in stages
    assert v.PLACEMENT_SCORING in stages
    dimensions = {row["dimension"] for row in skeleton.execute(
        "SELECT dimension FROM stage_dimension_value")}
    assert v.DIMENSION_RETRIEVAL in dimensions
    assert v.DIMENSION_PLACEMENT in dimensions


def test_a_run_with_no_p2_injection_writes_no_stage_row(skeleton):
    # The negative twin. P2 measures replays, shadows and adversarial runs; an
    # ordinary run emits nothing, and the test above measures the wiring rather
    # than a fixture that always writes.
    _place(skeleton)
    assert skeleton.execute(
        "SELECT count(*) AS c FROM stage_output").fetchone()["c"] == 0


def test_half_a_p2_injection_refuses_rather_than_silently_skipping(skeleton,
                                                                   p2_run_id):
    from placement.pipeline import P2Run

    with pytest.raises(ValueError):
        P2Run(run_id=p2_run_id, version_tuple_ref="", upstream_stage_refs=())


# --- §6.9: a file with two accepted homes ------------------------------------------


def _protect(conn, *, file_id, content_hash):
    """P7 says this file is protected, SUPERSEDING what the fixture already said.

    `_second_group` classifies every member `personal_non_sensitive`, and a second
    live record for one `(file_id, content_hash)` is `AmbiguousCurrentClassification`
    -- P7's own refusal to hold two current answers about one file (§8.2). So the
    later record supersedes the earlier one, which is how P7 changes its mind
    everywhere else too.
    """
    store = ClassificationStore(conn)
    was = store.current_fact_id(file_id, content_hash)
    now = store.write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="sensitive_personal", protected=True,
        basis="detector", evidence_refs=(OBS,), reliability_state="direct",
        observed_at=FIXED_CLOCK))
    if was is not None:
        store.supersede(was, now, "P7 re-read this file and it is protected")


def _second_group(conn, *, group_id, file_ids, hash_of=lambda fid: f"h-{fid}"):
    """A second ACCEPTED P9 group, written through P9's own writers.

    Nothing here is a stand-in: `group_state_as_of` and `memberships_for_group`
    read these rows, and `place_group` calls both.

    `hash_of` exists because one caller needs a member that is a REAL P1 file:
    `may_move_automatically` resolves a protected file's content hash BY FILE ID
    out of the `files` table, so a synthesized id has no row and the protected
    branch cannot run at all. Everything else keeps the synthetic `h-<file_id>`.
    """
    from facts.states import VALIDATED
    from grouping.acceptance import record_acceptance
    from grouping.records import AnchorFact, Group, GroupAcceptance, Membership, Support
    from grouping.store import record_group, record_membership
    from grouping.vocabulary import (
        ACCEPTED, COHERENT, DIRECT_ANCHOR, ENGINE, INCLUDED, NOT_FLAGGED,
        NO_SENSITIVITY, PENDING_REVIEW, RULES, SHARED_VALIDATED_FACT,
        STRONGLY_IDENTIFIED_FILE, SUPPORTED, USER,
    )

    record_group(conn, Group(
        group_id=group_id, seed_ref=f"seed-{group_id}",
        seed_kind=STRONGLY_IDENTIFIED_FILE, proposed_basis="subject = PHYS1402",
        anchor_facts=(AnchorFact(field="subject", value="PHYS1402",
                                 file_ids=tuple(file_ids),
                                 reliability_state=VALIDATED,
                                 observation_key=f"obs-{group_id}",
                                 # `104` R-97: each stating file cites its own.
                                 observation_keys=tuple(
                                     f"obs-{one}" for one in file_ids)),),
        pre_model_signals={}, anchor_count=len(file_ids),
        coherence_verdict=COHERENT, coherence_citations=(f"obs-{group_id}",),
        # `academic` and not `course`: P9 refuses a category outside
        # `facts.domains.SCHEMA_IDS`, and a group no live P9 run could produce
        # would make this seam test prove nothing about the real one.
        group_category="academic", display_label="PHYS1402 packet",
        label_source=ENGINE, conflicts=(), stop_rule_hits=(), state=SUPPORTED,
        sensitivity_state=NO_SENSITIVITY, dossier_id=None,
        llm_response_ref=None, validation_verdict_ref=None, created_by=RULES,
        created_at=FIXED_CLOCK))
    for file_id in file_ids:
        record_membership(conn, Membership(
            membership_id=f"m-{group_id}-{file_id}", group_id=group_id,
            file_id=file_id, content_hash=hash_of(file_id),
            basis=DIRECT_ANCHOR,
            decision=INCLUDED, decision_source=RULES,
            support=(Support(support_kind=SHARED_VALIDATED_FACT,
                             observation_key=f"obs-{file_id}",
                             quote_or_field="subject", location="body",
                             edge_ref=None),),
            insufficient_evidence=False, insufficiency_statement=None,
            conflicts=(), outlier_flag=NOT_FLAGGED,
            validation_verdict_ref=None, created_at=FIXED_CLOCK))
        _classify(conn, file_id=file_id, content_hash=hash_of(file_id))
    record_acceptance(conn, GroupAcceptance(
        acceptance_id=f"acc-{group_id}", plan_version_id="plan-1",
        group_id=group_id, membership_id=None, acceptance=ACCEPTED,
        review_state=PENDING_REVIEW, user_edited_label=None, aliases=(),
        review_decision_ref=None, decided_by=USER, created_at=FIXED_CLOCK))
    return group_id


#: Group A's members carry PHYS1401 and reach `n-course`; group B's carry
#: PHYS1402 and reach `n-course-alt`, which suppresses `n-course` as a conflict.
#: So the two packets settle on DIFFERENT shared parents, which is what makes the
#: file that belongs to both a genuine §6.9 case rather than an agreement.
#: The file that belongs to both packets. A pair, because one caller replaces it
#: with a real P1 file (see `_second_group`'s `hash_of`).
SHARED = ("f-shared", "h-f-shared")


def _two_home_evidence_for(shared_file_id):
    def _evidence_for(file_id):
        if file_id in ("f-duke-x", shared_file_id):
            return _evidence(
                facts=(MatchingFact(file_fact_id="ff2", field="subject",
                                    value="PHYS1402", reliability=v.DIRECT,
                                    evidence_ref=OBS),),
                group_ids=("g-phys1402",))
        return _evidence(group_ids=("g-phys1401",))
    return _evidence_for


def _two_homes(conn, tree=None, shared=SHARED):
    from placement.pipeline import run_corpus

    shared_file_id, shared_hash = shared
    group_a = _seeded(conn)
    _second_group(conn, group_id="g-phys1402-packet",
                  file_ids=("f-duke-x", shared_file_id),
                  hash_of=lambda fid: (shared_hash if fid == shared_file_id
                                       else f"h-{fid}"))
    # The shared file joins group A too, so it has accepted membership in both.
    from grouping.records import Membership, Support
    from grouping.store import record_membership
    from grouping.vocabulary import (
        DIRECT_ANCHOR, INCLUDED, NOT_FLAGGED, RULES, SHARED_VALIDATED_FACT,
    )

    record_membership(conn, Membership(
        membership_id=f"m-columbia-{shared_file_id}", group_id=group_a,
        file_id=shared_file_id, content_hash=shared_hash, basis=DIRECT_ANCHOR,
        decision=INCLUDED, decision_source=RULES,
        support=(Support(support_kind=SHARED_VALIDATED_FACT,
                         observation_key=f"obs-{shared_file_id}",
                         quote_or_field="target_school", location="body",
                         edge_ref=None),),
        insufficient_evidence=False, insufficiency_statement=None,
        conflicts=(), outlier_flag=NOT_FLAGGED, validation_verdict_ref=None,
        created_at=FIXED_CLOCK))

    inputs = _inputs(conn, partition=_partition)
    if tree is not None:
        inputs = dataclasses.replace(inputs, tree=tree)
    return run_corpus(
        conn, subjects=(), group_ids=(group_a, "g-phys1402-packet"),
        inputs=inputs, evidence_for=_two_home_evidence_for(shared_file_id),
        component_version="P11-test", observed_at=FIXED_CLOCK)


def _multi_home(result, file_id=SHARED[0]):
    return next(d for d in result.decisions if d.subject.file_id == file_id)


def test_the_two_packets_really_do_settle_on_different_parents(skeleton):
    # The premise, asserted rather than assumed. Without two DIFFERENT shared
    # parents there is no competition, `resolve_multi_home` is never reached, and
    # every §6.9 assertion below would be measuring nothing.
    result = _two_homes(skeleton)
    assert {p.shared_parent_node_id for p in result.group_plans} == {
        "n-course", "n-course-alt"}


def test_a_file_with_two_accepted_homes_never_gets_one_of_them(skeleton):
    # §6.9, `00`:1255-1259: "the system should not arbitrarily choose one
    # university". The file is in neither plan's member list and its own decision
    # names neither competing parent.
    result = _two_homes(skeleton)
    decision = _multi_home(result)
    assert decision.outcome == v.ABSTAIN
    assert decision.abstention_reason == v.NO_SHARED_BRANCH
    assert decision.destination is None
    for plan in result.group_plans:
        assert "f-shared" not in {d.subject.file_id for d in plan.member_decisions}


def test_the_user_can_be_asked_which_packet_is_the_primary_home(skeleton):
    # SPEC Open question 6 is open, so the selector is injected and both answers
    # are legal. This is the other one, and it is the only constructor of `Ask`.
    result = _two_homes(skeleton)
    conn = skeleton
    del result
    # A fresh run under the asking selector, on a second plan version's worth of
    # evidence is unnecessary -- the same corpus, a different injected answer.
    decision = _multi_home(_two_homes_asking(conn))
    assert decision.outcome == v.ASK_USER
    assert set(decision.ask.options) == {"n-course", "n-course-alt"}


def _two_homes_asking(conn, shared=SHARED, tree=None):
    """The same corpus under the asking selector. A second run supersedes the
    first decision about each subject, which is §8.2's own rule."""
    from placement.pipeline import run_corpus

    # A distinct set label, because `surface_residual_sets` addresses a set as
    # `plan_version:label` with no supersede link -- so a second surfacing of the
    # same label in one version collides on the primary key. Reported as a gap;
    # it is `residual.py`'s address to change, not this test's to work around
    # silently.
    # THE SAME SHAPE THE COMPOSITION ROOT WIRES since `104` §18.2 gap 15 --
    # `cli._ask_when_there_are_two_homes_to_offer` -- rather than an
    # unconditional yes, so this fixture and the deployment cannot drift apart on
    # the one condition that decides whether a question is legal at all.
    inputs = _inputs(conn,
                     partition=lambda ids: _partition(ids, label="Asked"),
                     ask_or_abstain=lambda ids: (
                         v.ASK_USER if len(tuple(ids)) >= 2 else v.ABSTAIN))
    if tree is not None:
        inputs = dataclasses.replace(inputs, tree=tree)
    return run_corpus(
        conn, subjects=(), group_ids=("g-columbia", "g-phys1402-packet"),
        inputs=inputs, evidence_for=_two_home_evidence_for(shared[0]),
        component_version="P11-test", observed_at="2026-08-27T01:00:00Z")


def test_the_two_homes_question_reaches_the_review_surface_as_a_question(skeleton):
    """`104` §18.2 GAP 15: the Ask is emitted into the review screen, with its evidence.

    The gap was never that the record did not exist. `placement/records.py` has
    required two options for an `Ask` since it was written, `_multi_home_decision`
    has minted one since it was written, and `review_surface.items` has rendered
    `ask_user_state` since it was written. What did not exist was a caller that
    ever returned `ask_user`: the composition root wired
    `lambda node_ids: pv.ABSTAIN`, so a file in two packets was told "the files
    these belong with are spread out" -- a sentence about missing evidence, over a
    file with more evidence than most.

    So this runs the corpus under `cli._ask_when_there_are_two_homes_to_offer`'s
    own contract and follows the decision all the way to the projection a person
    reads: the render state is the question's, the two packets ARE the options,
    and the alternatives and explanation ride along so the screen can say why each
    one fits. Nothing moves and nothing is chosen -- `resolve_multi_home` has no
    branch that returns a competing packet -- which is the difference between
    asking somebody and deciding for them.

    SABOTAGE: return `v.ABSTAIN` from the injected selector -- the render state
    goes back to `abstention_state`, `ask` is None, and the person sees a file
    with no home instead of a file with two.
    """
    from review_surface.items import RENDER_ASK, render_state_for

    # `_two_homes` seeds the two packets; `_two_homes_asking` re-runs the same
    # corpus under the asking selector, superseding the first decision (§8.2).
    _two_homes(skeleton)
    decision = _multi_home(_two_homes_asking(skeleton))
    assert decision.outcome == v.ASK_USER
    assert decision.ask is not None
    assert set(decision.ask.options) == {"n-course", "n-course-alt"}
    assert len(decision.ask.options) >= 2
    # The screen's own record: this is what a review surface renders, and it is
    # the state `ask_user` has of its own rather than an abstention's.
    assert render_state_for(decision) == RENDER_ASK
    # An `ask_user` carries no abstention reason -- the record enforces it -- so
    # the reason a file was not placed can never read as the reason it was asked.
    assert decision.abstention_reason is None
    assert decision.destination is None
    # And the evidence for each: the explanation names the competition rather than
    # complaining about the readings that produced it.
    assert "more than one packet" in decision.explanation


def test_a_protected_file_in_two_packets_is_never_turned_into_a_question(
        skeleton, tmp_path):
    """The second lock, and `104` §18.2 gap 15 is what made it necessary.

    `_asking` refuses outright to build an `ask_user` for protected material and
    says why: a review surface LISTS what it holds, and `00`:201 says a visible
    list of protected specifics may not be safe to have on a screen somebody else
    can see. `_multi_home_decision` mints its own `Ask` without going through
    `_asking`, and the injected selector is handed node ids and nothing else -- so
    it cannot tell a passport from a transcript. Before gap 15 that did not matter
    because the selector always abstained; the moment it asks, it does.

    The answer is §6.9's own abstention rather than a traceback: nothing is broken
    when a protected file turns out to belong to two packets, and the file is not
    lost by it -- `_protected_among` puts it in the protected review set before any
    reason is read, so it is still named and still counted. What does not happen is
    an `Ask` naming two packets beside a passport scan.

    SABOTAGE: pass `inputs.ask_or_abstain` straight through regardless of
    `privacy.protected` -- this decision comes back `ask_user` carrying an `Ask`
    whose options are the two packets, and the protected file's competing homes
    are printed on a screen.
    """
    # A REAL P1 file, because the protected branch resolves the content hash by
    # file id out of the `files` table (`privacy.moves.may_move_automatically`)
    # and a synthesized id has no row to resolve.
    shared = _real_file(skeleton, tmp_path / "packets", name="passport.pdf")
    _two_homes(skeleton, shared=shared)
    _protect(skeleton, file_id=shared[0], content_hash=shared[1])
    decision = _multi_home(_two_homes_asking(skeleton, shared=shared),
                           file_id=shared[0])
    assert decision.outcome == v.ABSTAIN
    assert decision.ask is None
    assert decision.abstention_reason == v.NO_SHARED_BRANCH
    assert decision.privacy.protected is True


def test_gap14_a_frozen_shared_branch_is_no_longer_a_rules_placement(skeleton):
    """RE-ARGUED BY `104` §18.2 gap 14's finding, and it used to assert the defect.

    It read: "a tree that froze a shared-material branch places the file ABOVE the
    competition", and it measured `place` at `n-course-shared` with
    `decided_by=rule`. `00`'s Amendments say *"every placement goes through the
    model"*, and a file two packets claim is the case a judge is most needed for --
    so `run_corpus` hands `resolve_multi_home` no branch to place on, asks site C
    between the two homes, and keeps §6.9's other two answers for when it gets no
    reply.

    THIS RUN HAS NO MODEL PATH (`_inputs` wires every model injection to `None`),
    which is exactly the condition §13.5 calls the deterministic fallback -- and
    the fallback is now the selector's answer rather than the branch. Under this
    fixture's selector that answer is the abstention; the twin below asks instead.

    SABOTAGE: hand `_shared_branch_of(inputs.tree)` back to `resolve_multi_home` --
    this comes back `place` at `n-course-shared` with no model call anywhere, and
    the amendment is unenforced in the one case §6.9 exists for.
    """
    from p11.p10_fixtures import tree_with
    from tree_design.vocabulary import SHARED_BRANCH

    decision = _multi_home(
        _two_homes(skeleton, tree=tree_with(shared_material_policy=SHARED_BRANCH)))
    assert decision.outcome == v.ABSTAIN
    assert decision.destination is None
    assert decision.abstention_reason == v.NO_SHARED_BRANCH


def test_gap14_a_frozen_shared_branch_does_not_take_the_question_away_either(
        skeleton):
    """The discriminating twin. Without it the test above could be passing because
    the branch-bearing policy stopped reaching `resolve_multi_home` at all.

    Under the asking selector the same tree produces the PERSON's question, and
    its options are the two packets -- never the branch, which nobody was asked
    about.
    """
    from p11.p10_fixtures import tree_with
    from tree_design.vocabulary import SHARED_BRANCH

    branch_bearing = tree_with(shared_material_policy=SHARED_BRANCH)
    _two_homes(skeleton, tree=branch_bearing)
    result = _two_homes_asking(skeleton, tree=branch_bearing)
    decision = _multi_home(result)
    assert decision.outcome == v.ASK_USER
    assert set(decision.ask.options) == {"n-course", "n-course-alt"}


# --- §7.4's disposition, where it is the only thing that can force review ---------


def _review_only_tree():
    """The same frozen tree with `To Sort` given a fact of its own.

    §7.4's `review-only` disposition only ever decides anything when NOTHING ELSE
    forces review, and on the residual path something always does. So the node is
    made reachable by a unique direct match on the §6 path, where `requires_review`
    is False, the file is not protected, and the disposition is the single
    remaining gate.
    """
    from dataclasses import replace

    from tree_design.records import ExpectedValue

    from p11.p10_fixtures import FROZEN_TREE

    expected = (ExpectedValue(field="subject", value="TOSORT"),)
    nodes = tuple(
        replace(node, expected_values=expected,
                associated_group_ids=("g-tosort",))
        if node.node_id == "n-review-later" else node
        for node in FROZEN_TREE.nodes)
    profiles = tuple(
        replace(profile, expected_values=expected,
                accepted_group_ids=("g-tosort",))
        if profile.node_id == "n-review-later" else profile
        for profile in FROZEN_TREE.profiles)
    return replace(FROZEN_TREE, nodes=nodes, profiles=profiles)


@pytest.fixture()
def review_only(p11_conn):
    create_llm_schema(p11_conn)
    create_budget_schema(p11_conn)
    for key in CEILINGS.values():
        set_ceiling(p11_conn, key, 8)
    _classify(p11_conn)
    _policy(p11_conn)
    build_destination_index(p11_conn, _review_only_tree(),
                            component_version="P11-test",
                            observed_at=FIXED_CLOCK, canonical=NO_CANONICAL_RULE)
    return p11_conn


def _tosort_evidence():
    return _evidence(
        facts=(MatchingFact(file_fact_id="ff3", field="subject", value="TOSORT",
                            reliability=v.DIRECT, evidence_ref=OBS),),
        group_ids=("g-tosort",))


def test_a_review_only_destination_blocks_an_otherwise_automatic_placement(
        review_only):
    # `00`:121: a review-only category "never moves files automatically". Every
    # other gate in `review_policy_for` is open here -- the verdict is
    # `accept_direct`, the match is unique and direct, the file is not protected
    # -- so the §7.4 disposition is the only thing that can produce
    # `review_required`, and dropping it turns this test red.
    decision = _place(review_only, inputs=_inputs(review_only),
                      evidence=_tosort_evidence())
    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == "n-review-later"
    assert decision.confidence_class == v.EXACT_FACT_MATCH
    assert decision.two_condition.requires_review is False
    assert decision.privacy.protected is False
    assert decision.review_policy == v.REVIEW_REQUIRED


def test_the_same_placement_onto_an_ordinary_node_is_automatic(skeleton):
    # The discriminating twin. Identical arithmetic, identical privacy state, a
    # node with no §7.4 disposition -- and the answer flips. Without this the test
    # above would pass against a `review_policy_for` that always reviewed.
    decision = _place(skeleton)
    assert decision.two_condition.requires_review is False
    assert decision.privacy.protected is False
    assert decision.review_policy == v.AUTO_ELIGIBLE


# --- §8.6: the two ceilings that bound what a scan may SPEND -----------------------


def _budgeted_call(conn, request, **kwargs):
    """`call_placement` reduced to the one step these tests are about.

    `harness.py:425-437` reserves against `deps.scan_budget` before the gate is
    asked and before any spend, and turns `BudgetExhausted` into a
    `PreCallAbstention(BUDGET_EXHAUSTED)` which `_pre_call_verdict` returns as an
    `abstain` verdict carrying that reason. This does the same two lines with
    P8's own `reserve_call`, so the accounting under test is P8's and not a
    re-implementation of it. The whole of `run_call` is driven for real against
    this same pipeline in `tests/integration/test_p11_pipeline_live.py`.
    """
    from llm_harness.budgets import BudgetExhausted, reserve_call
    from llm_harness.vocabulary import ABSTAIN, BUDGET_EXHAUSTED

    deps = kwargs["call_dependencies"]
    try:
        reserve_call(conn, deps.scan_budget, estimated_cost=deps.estimated_cost)
    except BudgetExhausted:
        return dataclasses.replace(
            _verdict(), outcome=ABSTAIN, disposition=ABSTAIN,
            reasons=(BUDGET_EXHAUSTED,), may_propose=False, requires_review=False)
    return _verdict()


def _spend(skeleton, monkeypatch, *, calls_per_1000, cost, attempts=3):
    """`attempts` model-path placements under P1's two spend ceilings."""
    import placement.pipeline as pipeline

    set_ceiling(skeleton, CEILINGS["max_llm_calls_per_thousand_files"],
                calls_per_1000)
    set_ceiling(skeleton, CEILINGS["max_cost_per_scan"], cost)
    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(_budgeted_call))
    return [
        _place(skeleton, inputs=_model_inputs(skeleton),
               evidence=_evidence(**AMBIGUOUS))
        for _ in range(attempts)
    ]


def test_p11_puts_p1s_two_spend_ceilings_on_the_budget_p8_reserves_against(
        skeleton, monkeypatch):
    """§8.6's `model.max_llm_calls_per_thousand_files` and `model.max_cost_per_scan`.

    `planning/58-SCALE-STRESS.md` item 8: both were read into `PlacementLimits`
    and referenced by no module in `src/placement/`, so the only thing bounding
    what a scan spent was whatever number the caller happened to construct. The
    caller's budget below says four calls per thousand files and a cost of ten;
    P1 says eight and eight, and eight and eight is what P8 reserves against.

    The scan's own coordinates are NOT overridden. `scan_id` and
    `corpus_file_count` describe the run and belong to it; P11 knows the ceilings
    and not how many files the disk holds.
    """
    import placement.pipeline as pipeline

    seen = {}

    def _capture(conn, request, **kwargs):
        seen["budget"] = kwargs["call_dependencies"].scan_budget
        return _verdict()

    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(_capture))
    caller = _call_dependencies().scan_budget
    assert (caller.max_calls_per_1000_files, caller.max_estimated_cost) == (
        4, Decimal("10"))
    _place(skeleton, inputs=_model_inputs(skeleton),
           evidence=_evidence(**AMBIGUOUS))
    assert seen["budget"].max_calls_per_1000_files == 8
    assert seen["budget"].max_estimated_cost == Decimal(8)
    assert seen["budget"].scan_id == caller.scan_id
    assert seen["budget"].corpus_file_count == caller.corpus_file_count


def test_the_calls_per_thousand_files_ceiling_stops_the_run_and_defers(
        skeleton, monkeypatch):
    """§8.6: "If the budget is exhausted, the product should retain extracted
    evidence, mark the deferred stage, and leave the file or group in review
    rather than guessing. Cost exhaustion must never turn into lower-quality
    automatic classification."

    Two calls per thousand files over a thousand-file corpus is two calls. The
    third placement is a DEFERRAL, not an abstention about evidence: SPEC:280-288
    keeps the two apart so P2 cannot grade a ceiling-truncated run as though a
    judgement had been made.
    """
    decisions = _spend(skeleton, monkeypatch, calls_per_1000=2, cost=99)
    assert [d.outcome for d in decisions] == [v.PLACE, v.PLACE, v.ABSTAIN]
    stopped = decisions[-1]
    assert stopped.abstention_reason == v.BUDGET_DEFERRED
    assert stopped.deferred_stage == v.PLACEMENT_SCORING
    # Never a cheaper placement: the deterministic path had a best candidate and
    # §8.6 forbids falling back to it.
    assert stopped.destination is None
    # And the evidence it gathered is still on the record, which is the "retain
    # extracted evidence" half of the same sentence.
    assert stopped.alternatives
    assert stopped.two_condition is not None


def test_a_run_under_the_calls_ceiling_is_untouched(skeleton, monkeypatch):
    """The negative twin. A ceiling that always fires is as broken as one that
    never does, and without this the test above would pass against a P11 that
    deferred every model call."""
    decisions = _spend(skeleton, monkeypatch, calls_per_1000=8, cost=99)
    assert [d.outcome for d in decisions] == [v.PLACE] * 3
    assert all(d.abstention_reason is None for d in decisions)
    assert all(d.deferred_stage is None for d in decisions)
    assert all(d.destination.node_id == "n-course-shared" for d in decisions)


def test_the_cost_per_scan_ceiling_stops_the_run_and_defers(skeleton, monkeypatch):
    """The second ceiling, fired on its own.

    The call ceiling is set to ninety-nine here so the deferral cannot be the
    other one: what runs out is the two units of estimated cost, at one unit a
    call. Two ceilings tested only together are one ceiling with two names.
    """
    decisions = _spend(skeleton, monkeypatch, calls_per_1000=99, cost=2)
    assert [d.outcome for d in decisions] == [v.PLACE, v.PLACE, v.ABSTAIN]
    assert decisions[-1].abstention_reason == v.BUDGET_DEFERRED
    assert decisions[-1].deferred_stage == v.PLACEMENT_SCORING


def test_a_model_call_with_no_scan_to_charge_against_is_refused(skeleton,
                                                                monkeypatch):
    """§8.6's ceilings are per SCAN. P11 supplies the two numbers; the caller
    supplies the run they are numbers about, and a request naming no scan would
    reserve against nothing and spend without a bound."""
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(lambda *_a, **_k: _verdict()))
    deps = dataclasses.replace(_call_dependencies(), scan_budget=None)
    with pytest.raises(pipeline.ScanBudgetRequired):
        _place(skeleton, inputs=_model_inputs(skeleton, call_dependencies=deps),
               evidence=_evidence(**AMBIGUOUS))


def test_an_unclassified_file_is_not_told_that_nothing_could_read_it(
        skeleton, monkeypatch, tmp_path):
    """`65` §4.1: the refusal described the one step that WORKED.

    On the first real run all four files had a `direct` subject fact in
    `file_facts` and zero rows in `classifications`. Reading succeeded and
    classification declined, and the sentence blamed reading -- "nothing has been
    able to read enough of it". `66` §4 forbids exactly this: "protected",
    "unreadable", "unsupported format", "still indexing" and "no strong match"
    are five states that may never share one message, and this was two of them
    sharing one.

    P11 knows that nothing classified this file. It does NOT know whether the
    file was readable -- P4's `extraction_runs` is that record (B1) and P11 never
    reads it. So the sentence claims the first and stops claiming the second.

    A CLOUD target since `104` R-121, for the reason the test above records: the
    owner's answer to Open question 5 lets a LOCAL model be asked about an
    unclassified file, and the cloud refusal that still produces this sentence is
    not a knob. The wording under test did not change.
    """
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(lambda *_a, **_k: pytest.fail("§8.4 gates first")))
    file_id, content_hash = _real_file(skeleton, tmp_path / "corpus",
                                       name="syllabus.pdf", body=b"%PDF-1.4 s")
    subject = Subject(kind=v.FILE, file_id=file_id, content_hash=content_hash,
                      group_id=None, member_file_ids=())
    decision = _place(skeleton, subject=subject,
                      inputs=_model_inputs(skeleton, model_target=CLOUD_TARGET),
                      evidence=_evidence(**AMBIGUOUS))

    assert decision.abstention_reason == v.PRIVACY_BLOCKED
    # Still says the true thing.
    assert "has not been classified" in decision.explanation
    # And no longer says the untrue one, in any of its spellings.
    assert "read enough" not in decision.explanation
    assert "unreadable" not in decision.explanation
    assert "able to read" not in decision.explanation


# --- R-19 (Q-A): the model decides, the rules validate ----------------------------
#
# `104` §13.5, and `00`'s placement amendment in the same words: "A unique direct
# match and the score-and-margin threshold no longer place a file without a model
# call. Every placement goes through the model... A unique direct match is the
# top-ranked candidate, not a bypass. This governs whenever a model is configured;
# with no model configured, the deterministic path remains the fallback."
#
# The three worlds a run can be in, and this section pins all three: no model path
# at all (the offline default, unchanged); a model path whose text nobody ratified
# (the answer is recorded and applied to nothing, so the deterministic placement
# stands); and a model path under a ratified text (the model decides).


def _asking(monkeypatch, verdict=None, seen=None):
    """Site C answered by a stub, with a note of whether it was asked at all."""
    import placement.pipeline as pipeline

    def _fake_call(conn, request, **kwargs):
        if seen is not None:
            seen["asked"] = seen.get("asked", 0) + 1
            seen["allowed"] = kwargs["call_dependencies"].allowed_vocabulary
        return _verdict() if verdict is None else verdict

    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(_fake_call))


def _accepts_directly():
    # `requires_review=False` WITH THE OUTCOME, and the pairing is the record's own.
    # `_verdict`'s default is `accept_context_supported`, where `P8Verdict` REQUIRES
    # review; an `accept_direct` that still asked for one is a different answer, and
    # a fixture that overrode the outcome and not the flag was describing that other
    # answer while its callers read it as "the model confirmed, cleanly". `104` R-75
    # makes the flag load-bearing at P11, so the fixture has to mean what it says.
    return _verdict(outcome=P8_ACCEPT_DIRECT, disposition=P8_MOVE_PLAN_ELIGIBLE,
                    requires_review=False)


def test_r19_a_unique_direct_match_is_asked_when_a_model_decides(skeleton,
                                                                 monkeypatch):
    seen: dict = {}
    _asking(monkeypatch, verdict=_accepts_directly(), seen=seen)
    decision = _place(skeleton,
                      inputs=_model_inputs(skeleton,
                                           chosen_node_of=lambda _v: "n-course"))
    assert seen["asked"] == 1
    assert "n-course" in seen["allowed"]
    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == "n-course"


def test_r19_a_model_that_confirms_the_top_candidate_records_the_match_it_is(
        skeleton, monkeypatch):
    """The record does not get worse for having been checked. The deterministic
    path called this an exact fact match; a model asked to confirm it and
    confirming it does not turn the facts into context, and `evidence_type`
    would otherwise say `direct` beside a `confidence_class` saying the
    opposite."""
    _asking(monkeypatch, verdict=_accepts_directly())
    decided = _place(skeleton,
                     inputs=_model_inputs(skeleton,
                                          chosen_node_of=lambda _v: "n-course"))
    offline = _place(skeleton)
    assert decided.destination.node_id == offline.destination.node_id
    assert decided.confidence_class == offline.confidence_class == v.EXACT_FACT_MATCH
    assert decided.evidence_type == offline.evidence_type == v.DIRECT
    assert decided.review_policy == offline.review_policy == v.AUTO_ELIGIBLE
    assert decided.two_condition.requires_review is False


def test_r19_a_model_that_chooses_another_node_is_a_context_supported_placement(
        skeleton, monkeypatch):
    """The other half of the same predicate: the deterministic winner WAS a
    unique direct match, the model chose somewhere else, and the record must not
    describe the answer nobody took."""
    _asking(monkeypatch)
    decision = _place(
        skeleton,
        inputs=_model_inputs(skeleton,
                             chosen_node_of=lambda _v: "n-course-shared"))
    assert decision.destination.node_id == "n-course-shared"
    assert decision.confidence_class == v.CONTEXT_SUPPORTED_GROUP_MATCH
    assert decision.evidence_type == v.CONTEXT_SUPPORTED
    assert decision.review_policy == v.REVIEW_REQUIRED
    assert decision.two_condition.requires_review is True


def test_r19_a_model_abstention_on_a_unique_direct_match_places_nothing(
        skeleton, monkeypatch):
    """"The model decides" has to mean this too, or it means nothing: the file
    the deterministic path would have placed is not placed when the model
    declines it. `00`:114 -- correct abstention is a successful outcome."""
    _asking(monkeypatch,
            verdict=_verdict(outcome=P8_ABSTAIN,
                             disposition=P8_NO_SUPPORTED_DESTINATION))
    decision = _place(skeleton, inputs=_model_inputs(skeleton))
    assert decision.outcome == v.ABSTAIN


def test_r19_an_unratified_prompt_leaves_the_deterministic_placement_alone(
        skeleton, monkeypatch):
    """A site running under text nobody ratified applies nothing, so it must not
    take the deterministic answer away either. Widening the routing on the
    strength of a model whose answer is discarded would turn every exact
    placement into an abstention -- `_observed_only` rewrites the verdict to
    `abstain`, and `transcribe` reads that as a file with no home."""
    import placement.pipeline as pipeline

    def _never(*_a, **_k):
        raise AssertionError("an unratified prompt decides nothing, so a file "
                             "the deterministic path settles is not sent")

    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(_never))
    decision = _place(skeleton,
                      inputs=_model_inputs(skeleton,
                                           prompt=SimpleNamespace(ratified=False)))
    offline = _place(skeleton)
    assert decision.outcome == offline.outcome == v.PLACE
    assert decision.destination.node_id == offline.destination.node_id
    assert decision.confidence_class == offline.confidence_class


def test_r19_an_unratified_prompt_still_observes_the_ambiguous_file(skeleton,
                                                                    monkeypatch):
    """And the observe path is NOT narrowed: the files §6.6 already sent are
    still sent, still recorded, and still applied to nothing."""
    seen: dict = {}
    _asking(monkeypatch, seen=seen)
    decision = _place(skeleton,
                      inputs=_model_inputs(skeleton,
                                           prompt=SimpleNamespace(ratified=False)),
                      evidence=_evidence(**AMBIGUOUS))
    assert seen["asked"] == 1
    assert decision.outcome == v.ABSTAIN


def test_r19_with_no_model_configured_nothing_about_the_offline_run_changes(
        skeleton):
    """The fallback `00`'s amendment keeps: "with no model configured, the
    deterministic path remains the fallback and places only what it can
    validate"."""
    decision = _place(skeleton)
    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == "n-course"
    assert decision.confidence_class == v.EXACT_FACT_MATCH
    assert decision.review_policy == v.AUTO_ELIGIBLE
    assert skeleton.execute(
        "SELECT count(*) AS c FROM llm_verdict").fetchone()["c"] == 0


def test_r19_deciding_is_the_path_and_the_ratification_together(skeleton):
    ratified = _model_inputs(skeleton)
    assert ratified.model_path_available() is True
    assert ratified.model_decides() is True
    draft = _model_inputs(skeleton, prompt=SimpleNamespace(ratified=False))
    assert draft.model_path_available() is True
    assert draft.model_decides() is False
    offline = _inputs(skeleton)
    assert offline.model_path_available() is False
    assert offline.model_decides() is False


# --- R-74: a gate refusal returns the file to the deterministic path --------------
#
# R-19 sends every placeable file to site C, so a PROTECTED file with a unique
# direct match reaches §8.4's gate for the first time -- and the gate refuses,
# correctly, and the file abstained `privacy_blocked` where an offline run placed
# it. `104` §13.5's own clause is the answer: "with no model configured the
# deterministic path remains the fallback". A refusal is that condition arriving one
# step later, so the file takes the placement the rules can defend rather than
# losing its home to a question nobody was able to ask.


def _protected_subject(conn, tmp_path, *, name="passport.pdf"):
    file_id, content_hash = _real_file(conn, tmp_path / "corpus",
                                       name=name, body=b"%PDF-1.4 s")
    _classify(conn, file_id=file_id, content_hash=content_hash,
              protected=True, handling_class="sensitive_personal")
    return Subject(kind=v.FILE, file_id=file_id, content_hash=content_hash,
                   group_id=None, member_file_ids=())


def test_a_protected_file_the_rules_could_place_is_still_not_filed(
        skeleton, monkeypatch, tmp_path):
    """`104` §18.2 gap 4, on the route R-74 opened.

    This is the file R-74 was written about: a unique direct match, sent to site C
    by R-19, turned away by §8.4, and filed on the rules' answer on the way out.
    Nothing is sent and nothing is assembled -- `call_placement` raising is the
    assertion that the gate still comes first -- and the file is left where it is
    rather than placed, because a gate refusal decides what may be SENT and
    §18.7 decides what may be MOVED.

    R-74's own arm survives on every other file the door turns away; the twin
    below is that arm.
    """
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(lambda *_a, **_k: pytest.fail(
        "§8.4 gates before any dossier, and R-74 does not move that")))
    subject = _protected_subject(skeleton, tmp_path)
    decision = _place(skeleton, subject=subject,
                      inputs=_model_inputs(skeleton))

    assert decision.outcome == v.ABSTAIN
    assert decision.destination is None
    assert decision.abstention_reason == v.PRIVACY_BLOCKED


def test_the_protected_file_is_told_it_is_protected_and_nobody_is_credited(
        skeleton, monkeypatch, tmp_path):
    """`104` R-28's actor rule, over the sentence gap 4 leaves standing.

    No model saw this file and nobody was asked, so the record credits neither --
    and what it says instead is the one fact that governs the outcome, which
    `_abstention_explanation` already ranks above every other true sentence about
    a protected file.
    """
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(lambda *_a, **_k: pytest.fail("§8.4 gates first")))
    subject = _protected_subject(skeleton, tmp_path, name="passport-2.pdf")
    decision = _place(skeleton, subject=subject,
                      inputs=_model_inputs(skeleton))

    assert "protected material" in decision.explanation
    assert "left exactly where it is" in decision.explanation
    assert "placed by the rules" not in decision.explanation
    assert "hierarchical destination judge" not in decision.explanation


def test_a_protected_file_the_person_gave_a_policy_for_is_still_placed(
        skeleton, tmp_path):
    """Design:185's own carve-out, and the discriminating twin of gap 4.

    "Should not be moved automatically WITHOUT a user policy that explicitly
    permits it" -- P7 holds that policy per file and P11 already reads it. A
    person who named this file in it has done the filing §18.7 reserves for them,
    so the guard reads that flag rather than the protected flag alone. Without
    this test gap 4 would look like a rule and be a constant.
    """
    file_id, content_hash = _real_file(skeleton, tmp_path / "corpus",
                                       name="passport-permitted.pdf")
    _classify(skeleton, file_id=file_id, content_hash=content_hash,
              protected=True, handling_class="sensitive_personal")
    _policy(skeleton, permissions={file_id: True})
    subject = Subject(kind=v.FILE, file_id=file_id, content_hash=content_hash,
                      group_id=None, member_file_ids=())
    decision = _place(skeleton, subject=subject)

    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == "n-course"


def test_r74_a_protected_file_the_rules_could_not_place_still_abstains(
        skeleton, monkeypatch, tmp_path):
    """The twin, and the half that keeps this from being a widening. A bounded
    ambiguity has no deterministic answer to fall back TO: an offline run abstains
    on it too, so `privacy_blocked` is still what the record says."""
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(lambda *_a, **_k: pytest.fail("§8.4 gates first")))
    subject = _protected_subject(skeleton, tmp_path, name="passport-3.pdf")
    decision = _place(skeleton, subject=subject,
                      inputs=_model_inputs(skeleton),
                      evidence=_evidence(**AMBIGUOUS))

    assert decision.outcome == v.ABSTAIN
    assert decision.abstention_reason == v.PRIVACY_BLOCKED
    assert "protected material" in decision.explanation


def test_r74_a_release_the_gate_denies_lands_in_the_same_place(
        skeleton, monkeypatch, tmp_path):
    """The refusal arriving from inside `run_call` rather than before it. P7 can
    deny at either point and the file's evidence is the same either way, so the
    two answers have to be the same answer."""
    import placement.pipeline as pipeline
    from llm_harness.records import Refusal
    from privacy.denial import RemedyOption, deny

    denied = deny("protected_cloud_target",
                  explanation="this file is protected and the target is cloud",
                  remedy_options=(RemedyOption(action="use_local_model",
                                               detail="ask a model on this device"),),
                  evidence_refs=())
    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(lambda *_a, **_k: Refusal(
        denied=denied, validator_version="vv", policy_version="pv")))
    decision = _place(skeleton, inputs=_model_inputs(skeleton))

    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == "n-course"
    assert "placed by the rules" in decision.explanation


# --- R-75: the rules validate the model's answer, they do not reclassify it -------


def test_r75_a_model_that_asks_for_review_gets_one_on_a_unique_direct_match(
        skeleton, monkeypatch):
    """`104` R-75. P11 never read `verdict.requires_review`.

    `p8_seam.transcribe` is explicit that `accept_direct` and
    `accept_context_supported` are both placements and "the difference between them
    is `requires_review`, which gates `review_policy` and not the outcome". P11
    computed the review class from its OWN two-condition and dropped the model's,
    so a model that confirmed the top node and said its support was context came
    out `auto_eligible`: it asked for a look and the record said none was needed.

    The evidence half is untouched, and deliberately: the facts that made this a
    unique direct match are still the facts, so `evidence_type` and
    `confidence_class` stay what R-19 established. One record, one review class,
    and the model's.
    """
    _asking(monkeypatch, verdict=_verdict())  # accept_context_supported
    decision = _place(skeleton,
                      inputs=_model_inputs(skeleton,
                                           chosen_node_of=lambda _v: "n-course"))

    assert decision.destination.node_id == "n-course"
    assert decision.confidence_class == v.EXACT_FACT_MATCH
    assert decision.evidence_type == v.DIRECT
    assert decision.two_condition.requires_review is True
    assert decision.review_policy == v.REVIEW_REQUIRED


def test_r75_a_clean_confirmation_still_needs_no_review(skeleton, monkeypatch):
    """The other direction, and it is what makes the read a READ. A model that
    accepts directly and asks for no review leaves the deterministic answer where
    it was; `104` §13.5's "rules validate" does not become "rules add a review"."""
    _asking(monkeypatch, verdict=_accepts_directly())
    decision = _place(skeleton,
                      inputs=_model_inputs(skeleton,
                                           chosen_node_of=lambda _v: "n-course"))

    assert decision.two_condition.requires_review is False
    assert decision.review_policy == v.AUTO_ELIGIBLE


def test_r75_the_rules_own_reasons_for_review_are_not_cleared_by_the_model(
        skeleton, monkeypatch):
    """OR, never assignment. A model answering `accept_direct` with no review
    request must not clear the review a DIFFERENT node already required -- rules
    that could take a review away would be validating in the wrong direction."""
    _asking(monkeypatch, verdict=_accepts_directly())
    decision = _place(
        skeleton,
        inputs=_model_inputs(skeleton,
                             chosen_node_of=lambda _v: "n-course-shared"))

    assert decision.destination.node_id == "n-course-shared"
    assert decision.two_condition.requires_review is True
    assert decision.review_policy == v.REVIEW_REQUIRED


# --- R-17 and packet G3: a ranked shortlist, each entry with its profile ----------
#
# `00`:110 -- the model "receives a placement dossier containing ... the small set
# of top legal destination candidates, EACH CANDIDATE'S NODE PROFILE, representative
# files already accepted in those nodes" -- and `104` §13.5: "Deterministic scores
# rank and shortlist the candidates the model is shown". What it received instead
# was every legal node id in the plan, alphabetically, with nothing said about any
# of them: `field_glossary` maps a node id to nothing and `Dossier` has no profile
# field (packet §7, G3). A model shown `node_f1d70c8a_3` and `node_f1d70c8a_5` is
# not choosing between two folders; it is guessing between two strings.


def _asked(monkeypatch, verdict=None):
    """Site C or D answered by a stub, with the request and the deps it was given."""
    import placement.pipeline as pipeline

    seen: dict = {}

    def _fake_call(conn, request, **kwargs):
        seen["request"] = request
        seen["allowed"] = kwargs["call_dependencies"].allowed_vocabulary
        seen["basis_key"] = kwargs["call_dependencies"].basis_key
        seen["items"] = tuple(request.evidence_items)
        return _verdict() if verdict is None else verdict

    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(_fake_call))
    return seen


def _items_of(seen, kind):
    return {item.evidence_ref: item.location
            for item in seen["items"] if item.kind == kind}


def test_r17_the_model_is_shown_the_ranking_and_not_the_whole_frozen_tree(
        skeleton, monkeypatch):
    seen = _asked(monkeypatch)
    _place(skeleton, inputs=_model_inputs(skeleton),
           evidence=_evidence(**AMBIGUOUS))
    # The three candidates §6.3 actually retrieved, in `assess`'s order, the
    # deterministic winner first. A LIST and not a set: position is what "ranked"
    # means, and `sorted(legal_node_ids(...))` threw it away.
    assert list(seen["allowed"]) == ["n-course", "n-course-shared", "n-general"]
    # Legal, and not retrieved for this file. Offering them is what made
    # `allowed_vocabulary` an answer to "which nodes exist" instead of "which
    # nodes might this file belong to".
    assert "n-academics" not in seen["allowed"]
    assert "n-review-later" not in seen["allowed"]
    # Suppressed by §6.3 as a conflict (`n-course-alt` expects PHYS1402). A
    # candidate the rules ruled out is not a candidate the model reconsiders.
    assert "n-course-alt" not in seen["allowed"]


def test_r17_every_node_the_model_may_answer_with_arrives_with_its_profile(
        skeleton, monkeypatch):
    seen = _asked(monkeypatch)
    _place(skeleton, inputs=_model_inputs(skeleton),
           evidence=_evidence(**AMBIGUOUS))
    candidates = _items_of(seen, "candidate")
    # The C draft: "its `evidence_ref` is an identifier from `allowed_vocabulary`,
    # and its `location` describes that folder, from the top of the tree down".
    assert set(candidates) == set(seen["allowed"])
    assert candidates["n-course"].startswith("Academics > PHYS1401")
    assert "expects subject=PHYS1401" in candidates["n-course"]
    assert "holds syllabus" in candidates["n-course"]
    assert "scoped fallback" in candidates["n-general"]
    assert "shared branch" in candidates["n-course-shared"]


# --- `104` §18.2 gaps 2 and 11: the rules rank, and the shortlist says so --------


#: `n-academics` is `n-course`'s parent in `FROZEN_TREE` and carries no expected
#: value, so nothing but a semantic neighbour reaches it. That is what makes it the
#: ancestor case: two candidates on one chain, and the shallower one is the option
#: `00`:111 and the prompt both offer.
ANCESTOR_TOO = dict(semantic_neighbours=("n-academics",))


def test_gap11_the_shallower_approved_parent_reaches_the_shortlist(
        skeleton, monkeypatch):
    """SABOTAGE: the ancestor is deleted again and the parent cannot be chosen.

    `104` §18.2 gap 11's first half. `_without_superseded_ancestors` dropped every
    strict ancestor of a candidate, so `00`:111's own instruction -- "if the system
    cannot distinguish Spring 2025 from Spring 2026 but a parent path such as
    `Academics/Columbia/PHYS1401/Homework` exists, the model should choose the
    approved shallower path" -- named an option the menu could not contain, and so
    did the prompt: "if a shallower candidate on the same chain has all its levels
    supported, that shallower one stands"
    (`c_placement_template.eliminate-v2.txt`:43).

    The parent is on `allowed_vocabulary`, it is described like any other folder,
    and the deepest node is still FIRST -- the rule kept its ordering and lost only
    its veto.
    """
    seen = _asked(monkeypatch)
    _place(skeleton, inputs=_model_inputs(skeleton),
           evidence=_evidence(**ANCESTOR_TOO))

    assert "n-academics" in seen["allowed"], (
        "the shallower approved parent was struck before the model could choose "
        "it, which is the option `00`:111 and the prompt both offer")
    allowed = list(seen["allowed"])
    assert allowed.index("n-course") < allowed.index("n-academics")
    assert seen["basis_key"].endswith("n-course")


def test_gap2_a_folder_the_rules_ranked_below_carries_its_reason_to_the_model(
        skeleton, monkeypatch):
    """SABOTAGE: the folder is offered with nothing said about why it is last.

    `104` §18.2 gap 2's channel. The C template's key inventory is closed ("the
    dossier has these keys and no others"), so the reason cannot be a new key and
    it cannot be a new field on a `candidate` item; it goes inside `location`,
    which is the same string that already tells the model "the file sits in this
    folder now". Order carries no meaning in the dossier by the template's own
    words, so this sentence is the ENTIRE flag -- offering the folder silently
    would tell the model the engine had no opinion, which is false.
    """
    seen = _asked(monkeypatch)
    _place(skeleton, inputs=_model_inputs(skeleton),
           evidence=_evidence(**ANCESTOR_TOO))

    candidates = _items_of(seen, "candidate")
    assert set(candidates) == set(seen["allowed"])
    assert "further down this same chain" in candidates["n-academics"]
    # And the profile is still a profile: the reason is added to the description,
    # never in place of it.
    assert candidates["n-academics"].startswith("Academics")
    # A contender says nothing of the kind.
    assert "ranked this folder below" not in candidates["n-course"]


def test_gap2_a_file_whose_every_candidate_was_ranked_below_still_reaches_the_model(
        skeleton, monkeypatch):
    """SABOTAGE: the rules answer for the model when they disagree with everything.

    THE CASE `104` §18.2 GAP 2 IS OPENED FOR, in its purest form. When step 6
    refused every candidate the assessment was empty, `needs_model_call`'s first
    clause turned the file away ("nothing for a model to CHOOSE between"), and the
    file abstained on the rules' say-so without anybody being asked. There IS
    something to choose between -- frozen, approved destinations, each with the
    engine's reason attached -- and `00`'s amendment gives that choice to the
    model.

    `subject` is declared un-anchoring here and the file's own folder is one the
    person made for what it holds, so `_a_folder_made_for_this_keeps_it` sets the
    only candidate aside. Nothing about the OFFLINE path moves: `model_decides` is
    what opens this door, and `test_gap2_an_offline_run_still_abstains_...` below
    is the other side of it.
    """
    seen = _asked(monkeypatch)
    decision = _place(
        skeleton,
        inputs=_model_inputs(
            skeleton,
            fields_that_cannot_anchor_a_move=frozenset({"subject"}),
            their_own_folder_made_for_what_it_holds={"f1": "n-review-later"},
            chosen_node_of=lambda _verdict: "n-course"),
        evidence=_evidence())

    assert list(seen["allowed"]) == ["n-course"]
    assert "n-course" in _items_of(seen, "candidate")
    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == "n-course"
    # A folder the rules ranked below is never `scored[0]`, so the placement
    # cannot be `auto_eligible` and the reason the rules gave is in the record a
    # person reads.
    assert decision.review_policy != v.AUTO_ELIGIBLE
    assert "ranked this folder below the others" in decision.explanation


def test_gap2_an_offline_run_still_abstains_when_every_candidate_was_ranked_below(
        skeleton):
    """The other side of the door, and it is what keeps the change safe.

    SABOTAGE: the set-aside shortlist starts placing files with no model in the
    run. `00`'s amendment ends "with no model configured, the deterministic path
    remains the fallback and PLACES ONLY WHAT IT CAN VALIDATE" -- and what it can
    validate is `assess`, which never sees a folder step 6 ranked below. So an
    offline install gets exactly the routing, the abstention and the reason it had
    before gap 2 was built.
    """
    decision = _place(
        skeleton,
        inputs=_inputs(
            skeleton,
            fields_that_cannot_anchor_a_move=frozenset({"subject"}),
            their_own_folder_made_for_what_it_holds={"f1": "n-review-later"}),
        evidence=_evidence())

    assert decision.outcome == v.ABSTAIN
    assert decision.destination is None


def test_r17_a_candidate_item_is_reference_only_and_names_no_span(
        skeleton, monkeypatch):
    # `records.py`: "P8 does not synthesise kind, location, reliability or basis".
    # A node profile is not an excerpt of the file, so it carries no span and it
    # never enters `released_evidence` -- P7 releases the file's text and a folder
    # the person approved is not the file's text.
    seen = _asked(monkeypatch)
    _place(skeleton, inputs=_model_inputs(skeleton),
           evidence=_evidence(**AMBIGUOUS))
    for item in seen["items"]:
        if item.kind == "candidate":
            assert item.excerpt_span is None
            assert "/" not in item.location


def test_r17_the_candidate_the_file_already_sits_in_says_so(skeleton,
                                                            monkeypatch):
    # §13.8's split is the model's to name and the draft asks it to
    # ("deeper_in_own_folder" / "out_of_own_folder"); it can only name it if the
    # dossier says which candidate is the folder the file is in now.
    seen = _asked(monkeypatch)
    _place(skeleton,
           inputs=_model_inputs(skeleton,
                                the_folder_each_file_is_in={"f1": "n-course"}),
           evidence=_evidence(**AMBIGUOUS))
    candidates = _items_of(seen, "candidate")
    assert "the file sits in this folder now" in candidates["n-course"]
    assert "sits in this folder now" not in candidates["n-course-shared"]


def test_r17_an_accepted_group_arrives_as_an_item_of_its_own(skeleton,
                                                             monkeypatch):
    # The C draft's second kind: "an `accepted_group` item names a group the
    # person has already accepted this file into ... that is context that can
    # support a folder even when the file's own text does not name the course".
    # `_invented_dimension` exempts a `context` level from grounding precisely
    # because the dossier used to carry nothing to ground one against.
    seen = _asked(monkeypatch)
    _place(skeleton, inputs=_model_inputs(skeleton),
           evidence=_evidence(**AMBIGUOUS))
    groups = _items_of(seen, "accepted_group")
    # BOTH of `AMBIGUOUS`'s groups, because since `104` §18.2 gap 13 the fixture's
    # ambiguity IS two accepted groups reaching two nodes -- a direct fact against
    # a group is no longer a close thing. The rule under test is unchanged: each
    # accepted group arrives as an item of its own rather than being folded into
    # the candidate that carries it.
    assert set(groups) == {"g-phys1401", "g-shared"}
    assert "accepted" in groups["g-shared"]


def test_r17_the_shortlist_and_its_head_are_the_scores_and_not_retrieval_order(
        skeleton, monkeypatch):
    """`104` §13.5 gives the ranking to the deterministic SCORES.

    Retrieval and scoring agree on this fixture -- both read the same six
    channels -- so the two orders are pinned apart deliberately here. What the
    model is shown, and what a past rejection is keyed on, are the ASSESSMENT's
    order: `basis_key_for` read `retrieval.candidates[0]`, which is the order six
    channels happened to answer in and not a ranking of anything.
    """
    import placement.pipeline as pipeline

    real = pipeline.assess

    def _reversed(*args, **kwargs):
        out = real(*args, **kwargs)
        return dataclasses.replace(out, scored=tuple(reversed(out.scored)))

    monkeypatch.setattr(pipeline, "assess", _reversed)
    seen = _asked(monkeypatch)
    _place(skeleton, inputs=_model_inputs(skeleton),
           evidence=_evidence(**AMBIGUOUS))
    assert list(seen["allowed"]) == ["n-general", "n-course-shared", "n-course"]
    assert seen["basis_key"] == basis_key_for(subject_id="f1",
                                              node_id="n-general")


def test_r17_the_basis_key_names_the_ranked_winner(skeleton, monkeypatch):
    # The unreversed control, so the test above measures the ordering and not a
    # pipeline that always names the last node.
    seen = _asked(monkeypatch)
    _place(skeleton, inputs=_model_inputs(skeleton),
           evidence=_evidence(**AMBIGUOUS))
    assert seen["basis_key"] == basis_key_for(subject_id="f1",
                                              node_id="n-course")


def test_r17_site_d_describes_every_home_it_offers(skeleton, monkeypatch):
    """The D draft says every id in `allowed_vocabulary` is described in
    `evidence_items`, and the live builder described none of them.

    §7.7 runs no `assess`, so D has no ranking of its own; what it offers is
    `00`:120's approved residual library plus the branches retrieval reached, in
    the draft's own two kinds. `approved_target_ids` stays the whole legal set, so
    the validator accepts exactly what it accepted before -- only what the model is
    SHOWN narrows.
    """
    seen = _asked(monkeypatch, verdict=_verdict(disposition=P8_LEAVE_IN_PLACE))
    result = _corpus(skeleton)
    _decide(skeleton, result.residual_sets[0].set_id)
    _review(skeleton, result, inputs=_model_inputs(
        skeleton, partition=_partition,
        residual_action_of=lambda _v: (LEAVE_IN_CURRENT_LOCATION, None)))

    described = {item.evidence_ref: item for item in seen["items"]
                 if item.kind in ("residual_area", "branch")}
    assert set(seen["allowed"]) == set(described)
    # The person's residual library is offered whether or not retrieval reached it.
    assert "n-review-later" in described
    assert described["n-review-later"].kind == "residual_area"
    assert "residual area" in described["n-review-later"].location
    assert v.REVIEW_ONLY in described["n-review-later"].location
    # And no site-C kind at a site whose text names two others.
    assert not [item for item in seen["items"] if item.kind == "candidate"]


# --- `104` R-O and §18.2 gap 1 at site C ------------------------------------------
#
# R-O, R-136 and R-173 each ruled that one refused, unbuilt or failed call must not
# end the corpus run, and each left the file on the deterministic placement on the
# way out. That fallback was never ruled: R-136's own row says closing it "needs a
# reason word that is true of a call that happened and failed, with the file in a
# review set". `no_model_judgement` is that word, and these are the five states it
# is true of.


def _no_verdict(kind: str):
    """Site C's five ways of coming back with no judgement about this file."""
    from llm_harness.records import CallFailed, PreCallAbstention, ValidationUnavailable
    from llm_harness.vocabulary import BUDGET_EXHAUSTED, C_PLACEMENT
    from privacy.resolve import UnresolvableSpan

    def call(conn, request, **kwargs):
        if kind == "refused":
            # Raised inside the call and caught by `_judged_or_refused_steps`,
            # which turns it into P8's own `CallRefused` -- the R-O door.
            raise UnresolvableSpan(
                "observation 'sha256:3ea4' belongs to a file outside "
                "request.target")
        if kind == "budget_exhausted":
            return PreCallAbstention(reason=BUDGET_EXHAUSTED,
                                     call_site=C_PLACEMENT,
                                     subject_ref=request.subject_ref)
        if kind == "failed":
            return CallFailed(
                request_identity="rq-1", release_id="rel-1", audit_id=None,
                explanation="the provider closed the connection",
                validator_version="1", policy_version="policy-1")
        assert kind == "unvalidatable", kind
        return ValidationUnavailable(missing=("prompt",))
    return call


@pytest.mark.parametrize(
    "kind", ["refused", "budget_exhausted", "failed", "unvalidatable"])
def test_a_call_that_produced_no_verdict_places_nothing_and_names_why(
        skeleton, monkeypatch, kind):
    """§13.5: the model decides wherever one is configured, and none decided here.

    The file is the skeleton's own unique direct match, deliberately: the rules
    HAD an answer for it and filed it on that answer until now, with
    `decided_by=rule` on the row. That is §6.10's arithmetic overruling a judge
    that was asked and did not answer, and it is what the reason word closes.
    """
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(_no_verdict(kind)))
    decision = _place(skeleton, inputs=_model_inputs(skeleton))

    assert decision.outcome == v.ABSTAIN
    assert decision.abstention_reason == v.NO_MODEL_JUDGEMENT
    assert decision.destination is None
    # The sentence claims nothing about the evidence and calls nothing correct:
    # a call that did not come back is a failure, and `66` §4 forbids describing
    # it as a deliberate decline.
    assert "no answer about it came back" in decision.explanation
    assert "supported home" not in decision.explanation
    assert "the right answer" not in decision.explanation


def test_the_file_with_no_verdict_is_on_the_row_and_the_run_carries_on(
        skeleton, monkeypatch):
    """The coverage half R-O, R-136 and R-173 were each ruled for, unchanged.

    The abstention is DURABLE -- the point of a reason word is that a reader of
    the run can count these -- and the next file is still judged. Before the three
    rulings the first of these ended the run; the fix must not have traded that
    back for a record.
    """
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(_no_verdict("failed")))
    first = _place(skeleton, inputs=_model_inputs(skeleton))

    stored = current_decision(skeleton, plan_version="plan-1",
                              subject_ref=f"{v.FILE}:f1:h1")
    assert stored.decision_id == first.decision_id
    assert stored.abstention_reason == v.NO_MODEL_JUDGEMENT

    # A second file, judged for real behind the one that got no answer.
    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(lambda *_a, **_k: _verdict()))
    second = Subject(kind=v.FILE, file_id="f2", content_hash="h2", group_id=None,
                     member_file_ids=())
    _classify(skeleton, file_id="f2", content_hash="h2")
    after = _place(skeleton, subject=second,
                   inputs=_model_inputs(skeleton),
                   evidence=_evidence(**AMBIGUOUS))
    assert after.outcome == v.PLACE
    assert after.destination.node_id == "n-course-shared"


def test_a_file_the_call_was_never_built_for_is_the_same_answer(skeleton,
                                                                monkeypatch):
    """R-136's own state, which reaches the same door: the model is not asked.

    A file with no settled fact has no `evidence_items`, so `_judge_with_model`
    abstains before a request is built. The pre-call row still says the model was
    not reserved for it (`test_the_file_that_is_not_asked_records_why_in_p8s_own_
    row`); what changes is that the DECISION no longer files it by rule.
    """
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(lambda *_a, **_k: pytest.fail(
                            "a file with nothing to send is not asked")))
    decision = _place(skeleton, inputs=_model_inputs(skeleton),
                      evidence=_evidence(evidence_items=(),
                                         group_ids=PLACING_GROUPS))

    assert decision.outcome == v.ABSTAIN
    assert decision.abstention_reason == v.NO_MODEL_JUDGEMENT


def test_with_no_model_configured_the_same_file_is_still_placed_by_the_rules(
        skeleton):
    """`104` R-74's narrow arm, exactly as ruled, and the half that keeps gap 1
    from being a coverage loss.

    §13.5: *"Q-A governs whenever a model is configured; with no model configured
    the deterministic path remains the fallback."* Nothing above narrows that
    sentence -- it narrows what a run WITH a model may do when its model says
    nothing -- and without this test the two would be indistinguishable.
    """
    decision = _place(skeleton)

    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == "n-course"
    assert decision.confidence_class == v.EXACT_FACT_MATCH


def test_a_programming_error_at_site_c_still_surfaces(skeleton, monkeypatch):
    import placement.pipeline as pipeline

    def _bug(conn, request, **kwargs):
        raise AttributeError("'NoneType' object has no attribute 'locality'")

    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(_bug))
    with pytest.raises(AttributeError):
        _place(skeleton, inputs=_model_inputs(skeleton))


# --- `104` R-136: a file with nothing to send does not end the run --------------

def test_a_file_with_no_settled_fact_abstains_instead_of_ending_the_run(
        skeleton, monkeypatch):
    """The r4 crash, as one file.

    Site C's evidence is `cli.evidence_for` -- the file's settled `file_facts` --
    so a file with none has no `evidence_items`. That state raised
    `ModelJudgementUnavailable`, which is not in `REFUSAL_EXCEPTIONS`, so
    `_judged_or_refused` did not catch it and the corpus run died at that file:
    measured on the C-live run r4, 67.5 minutes, 50 placements, 0 site-C
    dossiers, on a corpus whose `subject` was right on 2 files and missing on 19.
    Most coursework files are that file.

    The model is not asked, the decision comes back, and the run goes on.
    """
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(lambda *_a, **_k: pytest.fail(
                            "a file with nothing to send is not asked")))
    decision = _place(skeleton, inputs=_model_inputs(skeleton),
                      evidence=_evidence(**AMBIGUOUS, evidence_items=()))

    assert decision is not None


def test_the_file_that_is_not_asked_records_why_in_p8s_own_row(skeleton,
                                                               monkeypatch):
    """A pre-call abstention, in the table site A's exhausted budget writes to.

    The reason is P8's own word and no new one is minted:
    `NOT_ELIGIBLE_FOR_MODEL` is what `eligibility.not_reserved_for_llm` returns
    for a subject the model is not reserved for, and a file with nothing to send
    is exactly that. §6.10's abstention reasons are untouched -- none of them
    means "the call did not happen", which is what `_require_verdict` says in its
    own words.
    """
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(lambda *_a, **_k: pytest.fail("not asked")))
    _place(skeleton, inputs=_model_inputs(skeleton),
           evidence=_evidence(**AMBIGUOUS, evidence_items=()))

    # P8's vocabulary, from P8. `placement.vocabulary` is §6.10's closed set and
    # this word is deliberately not a member of it.
    from llm_harness.vocabulary import C_PLACEMENT, NOT_ELIGIBLE_FOR_MODEL

    rows = [dict(row) for row in skeleton.execute(
        "SELECT reason, call_site, subject_ref, dossier_id "
        "FROM llm_pre_call_abstention")]
    assert len(rows) == 1
    assert rows[0]["reason"] == NOT_ELIGIBLE_FOR_MODEL
    assert rows[0]["call_site"] == C_PLACEMENT
    # Addressed the way every pre-call row is, so one query finds it beside site
    # A's. `pre_call_address` is P8's, not spelled again here.
    assert rows[0]["dossier_id"].startswith("pre-call:")


def test_the_file_that_is_not_asked_reserves_no_budget(skeleton, monkeypatch):
    """The abstention is decided BEFORE `reserve_call`, so the slot stays.

    `104` R-131's merge gave the observe and placement sites a ledger of their
    own; this is the other half of not wasting it. A call that cannot be built
    must not charge the run for the attempt, or a corpus of files with no settled
    fact would spend the placement budget on questions nobody could ask.
    """
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(lambda *_a, **_k: pytest.fail("not asked")))
    _place(skeleton, inputs=_model_inputs(skeleton),
           evidence=_evidence(**AMBIGUOUS, evidence_items=()))

    reserved = list(skeleton.execute("SELECT * FROM llm_budget_reservation"))
    assert reserved == []


def test_the_next_file_is_still_judged_after_one_is_not_asked(skeleton,
                                                              monkeypatch):
    """The corpus loop's own property, which is what r4 lost.

    Three files in the order the run reads them: the first is judged, the middle
    one has no settled fact, and the third is judged. Before this, the middle one
    ended the run and the third was never reached at all -- the run died after 50
    placements rather than reporting on them.
    """
    import placement.pipeline as pipeline

    asked: list[str] = []

    def judge(*_args, **kwargs):
        asked.append("call")
        return _verdict()

    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(judge))
    inputs = _model_inputs(skeleton)

    first = _place(skeleton, inputs=inputs, evidence=_evidence(**AMBIGUOUS))
    middle = _place(skeleton, inputs=inputs,
                    evidence=_evidence(**AMBIGUOUS,
                                       evidence_items=()))
    third = _place(skeleton, inputs=inputs, evidence=_evidence(**AMBIGUOUS))

    assert first is not None and middle is not None and third is not None
    # Two calls, not three: the middle file was not asked, and not asking it did
    # not stop the third being asked.
    assert len(asked) == 2


def test_a_subject_with_no_matching_fact_is_asked_on_the_items_it_does_carry(
        skeleton, monkeypatch):
    """`104` R-148, on the state `104` R-143 built a door for.

    R-143 read the snapshot's keys off `evidence["facts"]`, and `MatchingFact`
    forbids an empty `evidence_ref` -- so that tuple was empty in exactly one
    case, a subject with NO matching fact, and every one of those was turned away
    as `NOT_ELIGIBLE_FOR_MODEL`. That is the second half of R-148 and 103 of the
    owner's 199 files on r12: `cli.evidence_for` now offers a factless file its
    own releasable readings, and this is the gate that would still have refused
    to build the call.

    The keys come off the ITEMS, which is what the paragraph above that line has
    said since the function was written -- "the keys the DOSSIER cites" -- and is
    what `model_call_request` is actually handed. So a dossier carrying a
    neighbour's context line, or this file's own words, is addressable and is
    sent.

    R-143's own guarantee is untouched and is the reason its branch stays: an
    `EvidenceSnapshotRequired` raised here is outside `REFUSAL_EXCEPTIONS` and
    ends the corpus run, measured on r11 at 113 minutes in with 0 site-C
    dossiers.
    """
    import placement.pipeline as pipeline

    seen: dict = {}

    def judge(_conn, request, **_kwargs):
        seen["snapshot"] = request.evidence_snapshot_id
        seen["refs"] = tuple(item.evidence_ref
                             for item in request.evidence_items)
        return _verdict()

    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(judge))
    decision = _place(skeleton, inputs=_model_inputs(skeleton),
                      evidence=_evidence(**AMBIGUOUS))

    assert decision is not None
    assert seen["snapshot"], "a dossier whose items carry addresses is minted one"
    assert OBS in seen["refs"]
    # And nothing was recorded as a file the model is not reserved for.
    assert not skeleton.execute(
        "SELECT 1 FROM llm_pre_call_abstention").fetchall()


def test_the_snapshot_addresses_the_items_and_not_the_facts(skeleton,
                                                            monkeypatch):
    """Two subjects whose dossiers carry the same items and different facts are
    one question asked twice, and the content address says so.

    `evidence_snapshot_id_for` is what a replay is recognised by and what
    `revalidate_for_plan` keys a re-validation on, so it has to address what was
    SENT. Keyed on the matched facts it addressed a different set from the one in
    the dossier -- and refused to mint at all for a call whose candidates were
    reached by group evidence.
    """
    import placement.pipeline as pipeline

    minted: list[str] = []
    monkeypatch.setattr(
        pipeline, "call_placement_steps",
        _as_steps(lambda _conn, request, **_kw: (
            minted.append(request.evidence_snapshot_id), _verdict())[1]))
    inputs = _model_inputs(skeleton)

    _place(skeleton, inputs=inputs, evidence=_evidence(**AMBIGUOUS))
    _place(skeleton, inputs=inputs, evidence=_evidence(**AMBIGUOUS))

    assert len(minted) == 2
    assert minted[0] == minted[1]


def test_the_next_file_is_judged_after_one_carries_no_matching_fact(
        skeleton, monkeypatch):
    """The corpus property r11 lost, kept for R-148's state.

    Under R-143 the middle file was not asked; it is now, and the run still
    reaches the third. What r11 lost was the run, not the call.
    """
    import placement.pipeline as pipeline

    asked: list[str] = []
    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(lambda *_a, **_k: (asked.append("call"), _verdict())[1]))
    inputs = _model_inputs(skeleton)
    middle = _place(skeleton, inputs=inputs,
                    evidence=_evidence(**AMBIGUOUS))
    third = _place(skeleton, inputs=inputs, evidence=_evidence(**AMBIGUOUS))

    assert middle is not None and third is not None
    assert len(asked) == 2


# --- `104` R-149: a request the builder cannot form is a pre-call abstention -----

#: The state R-149 is about, as a builder. `model_placement.releasable_excerpts`
#: applies P7's five refusals a step early, and the first of them drops every
#: reading whose zone is always-local -- so a file whose only cited reading is its
#: own filename leaves the request with NO items and P7's
#: `ModelCallRequest.__post_init__` refuses it: *"a request with no items has
#: nothing to release"*.
#:
#: THE RAISE IS THE REAL ONE. Only the excerpt selection is short-circuited here;
#: `tests/integration/test_model_placement.py` drives the same state through the
#: live `releasable_excerpts` over a real filename-zone observation, which is
#: where the drop itself is pinned.
def _nothing_left_to_release(*, subject_ref, evidence_items, max_dossier_tokens):
    from privacy.release import ModelCallRequest, Target

    return ModelCallRequest(
        stage="placement", target=Target(file_ids=(subject_ref.split(":")[1],)),
        model_target=LOCAL_TARGET, requested_items=(),
        prompt_template_id="template.placement",
        prompt_fingerprint="fp-canonical",
        max_dossier_tokens=max_dossier_tokens)


def _refused_call_events(conn) -> list[str]:
    from llm_harness.authorship import CALL_REFUSED

    return [row["explanation"] for row in conn.execute(
        "SELECT explanation FROM events WHERE event_type = ? ORDER BY event_id",
        (CALL_REFUSED,))]


def test_a_file_with_nothing_releasable_records_the_abstention_and_falls_back(
        skeleton, monkeypatch):
    """`104` R-149: the silent site-C loss, made a row.

    Measured on the six-file stub corpus of
    `tests/integration/test_local_model_fact_pass.py` before R-148: a file whose
    one fact cited only a `filename`-zone reading had that reading dropped by
    `releasable_excerpts`, `ModelCallRequest.__post_init__` raised, and
    `_judged_or_refused` caught it into the deterministic fallback --
    `llm_pre_call_abstention` gained no row and `llm_refusal` gained no row, so
    r12's 104 `NOT_ELIGIBLE_FOR_MODEL` was a floor on the site-C losses and not
    the total.

    **R-148 does not make this state unreachable.** It offers a factless file its
    own releasable readings, and a file with NO body readings at all -- every
    reading it has sits in an always-local zone -- still arrives here with
    nothing to send. This fixture is that file: the evidence is supplied
    directly, so `cli.evidence_for` and R-148's readings are not in the path at
    all, and the only question asked is what P11 does when the builder refuses.

    Both halves are asserted: the row, and the placement the deterministic path
    had already earned.
    """
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(lambda *_a, **_k: pytest.fail(
                            "a request that cannot be built is not sent")))
    inputs = _model_inputs(skeleton,
                           model_call_request=_nothing_left_to_release)

    unbuilt = _place(skeleton, inputs=inputs, evidence=_evidence(**AMBIGUOUS))
    offline = _place(skeleton, evidence=_evidence(**AMBIGUOUS))

    # §13.5's own clause: "with no model configured the deterministic path
    # remains the fallback". The file keeps the home the rules could defend.
    assert unbuilt.outcome == offline.outcome
    assert unbuilt.confidence_class == offline.confidence_class
    assert (unbuilt.destination is None) == (offline.destination is None)
    if offline.destination is not None:
        assert unbuilt.destination.node_id == offline.destination.node_id


def test_the_unbuildable_request_is_recorded_in_p8s_own_pre_call_row(
        skeleton, monkeypatch):
    """R-136's row, for R-136's reason, at the third door into it.

    `NOT_ELIGIBLE_FOR_MODEL` is P8's own word -- `eligibility.
    not_reserved_for_llm` returns it for a subject the model is not reserved for
    -- and it is true of a file with nothing releasable to send. No member is
    added to any vocabulary: §6.10's abstention reasons stay closed, and
    `PRE_CALL_REASON_CODES` gains nothing.
    """
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(lambda *_a, **_k: pytest.fail("not asked")))
    _place(skeleton,
           inputs=_model_inputs(skeleton,
                                model_call_request=_nothing_left_to_release),
           evidence=_evidence(**AMBIGUOUS))

    from llm_harness.vocabulary import C_PLACEMENT, NOT_ELIGIBLE_FOR_MODEL

    rows = [dict(row) for row in skeleton.execute(
        "SELECT reason, call_site, subject_ref, dossier_id "
        "FROM llm_pre_call_abstention")]
    assert len(rows) == 1
    assert rows[0]["reason"] == NOT_ELIGIBLE_FOR_MODEL
    assert rows[0]["call_site"] == C_PLACEMENT
    # Addressed the way every pre-call row is, so one query finds it beside site
    # A's exhausted-budget rows and R-136's.
    assert rows[0]["dossier_id"].startswith("pre-call:")


def test_the_unbuilt_call_is_an_abstention_and_not_a_refusal(skeleton,
                                                             monkeypatch):
    """One non-call, one record. `record_unbuilt_call_abstention` says why in its
    own words: *"nothing was ever grounded, and nothing refused a call that was
    never built"* -- the gate never saw this request, so a `call_refused` event
    beside the row would be one reader counting the same non-call twice.

    `llm_refusal` is P7's `Denied` row and is empty for the same reason: §8.4
    denied nothing here.
    """
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(lambda *_a, **_k: pytest.fail("not asked")))
    _place(skeleton,
           inputs=_model_inputs(skeleton,
                                model_call_request=_nothing_left_to_release),
           evidence=_evidence(**AMBIGUOUS))

    assert _refused_call_events(skeleton) == []
    assert not skeleton.execute("SELECT 1 FROM llm_refusal").fetchall()
    # And no budget was reserved: the abstention is decided before `reserve_call`,
    # so a corpus of such files does not spend the placement budget on questions
    # nobody could ask.
    assert not skeleton.execute(
        "SELECT 1 FROM llm_budget_reservation").fetchall()


def test_a_malformed_request_from_inside_the_call_is_still_a_refusal(
        skeleton, monkeypatch):
    """The negative twin, and it is what keeps R-149 from widening R-O's catch.

    `MalformedRequest` is raised in two places at this site: by the BUILDER,
    before anything exists, and by P7 inside `run_call`, which is a request the
    gate could not evaluate. Only the first is a pre-call abstention. A catch
    that could not tell them apart would file every gate refusal as "the model
    was not reserved for this file", which is a different sentence about a
    different actor.
    """
    import placement.pipeline as pipeline
    from privacy.release import MalformedRequest

    def _refuse_inside_the_call(conn, request, **kwargs):
        raise MalformedRequest("the gate cannot evaluate this request")

    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(_refuse_inside_the_call))
    decision = _place(skeleton, inputs=_model_inputs(skeleton),
                      evidence=_evidence(**AMBIGUOUS))

    assert decision is not None
    assert not skeleton.execute(
        "SELECT 1 FROM llm_pre_call_abstention").fetchall()
    explanations = _refused_call_events(skeleton)
    assert explanations, "a refusal raised inside the call is still an event"
    assert "MalformedRequest" in explanations[-1]


def test_a_residual_file_the_model_is_not_asked_about_does_not_end_the_run(
        skeleton, monkeypatch):
    """Site D reads a pre-call abstention, which until `104` R-149 it could not.

    `_judge_with_model` serves C and D alike, so every door R-136 opened to a
    `PreCallAbstention` -- no evidence items, no retrievable candidate, no
    resolvable address -- opened at site D too. D read `Refusal` and `CallRefused`
    and nothing else, so `_require_verdict` raised `ModelJudgementUnavailable` and
    the run died on the whole residual set. A file the user asked to have reviewed
    is exactly the file most likely to have nothing settled about it.

    The file abstains with the qualifier D's own refusal already carries: D
    proposes a destination, and a call that was never built proposed none.
    """
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement_steps",
                        _as_steps(lambda *_a, **_k: pytest.fail(
                            "a file with nothing to send is not asked")))
    result = _corpus(skeleton)
    assert result.residual_sets, "the file must reach §7 for this to test anything"
    _decide(skeleton, result.residual_sets[0].set_id)

    written = _review(skeleton, result,
                      evidence_for=lambda file_id: _evidence(
                          facts=(), evidence_items=()))

    assert [d.outcome for d in written] == [v.ABSTAIN]
    assert written[0].abstention_reason == v.NO_SUPPORTED_DESTINATION
    # And it is P8's pre-call row that says why the model was not asked, at D's
    # own call site.
    from llm_harness.vocabulary import D_RESIDUAL, NOT_ELIGIBLE_FOR_MODEL

    rows = [dict(row) for row in skeleton.execute(
        "SELECT reason, call_site FROM llm_pre_call_abstention")]
    assert rows == [{"reason": NOT_ELIGIBLE_FOR_MODEL, "call_site": D_RESIDUAL}]


# --- `00`:110's missing fields and deterministic scores, per candidate -----------
#
# *"...known conflicts, MISSING FIELDS, and DETERMINISTIC SCORES."* Neither key
# existed: rank reached the model as list order alone, and no candidate said which
# of the levels it fixes this file states no fact for. Gated by the row's own flag
# for R-77's reason, so the observed row's bytes do not move.


def _candidate_items_seen(skeleton, monkeypatch, *, prompt):
    import placement.pipeline as pipeline

    seen = {}

    def _fake_call(conn, request, **kwargs):
        seen["items"] = {item.evidence_ref: item
                         for item in request.evidence_items}
        seen["allowed"] = kwargs["call_dependencies"].allowed_vocabulary
        return _verdict()

    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(_fake_call))
    _place(skeleton, inputs=_model_inputs(skeleton, prompt=prompt),
           evidence=_evidence(**AMBIGUOUS))
    return seen


def test_under_a_row_that_names_no_scores_the_candidate_items_carry_none(
        skeleton, monkeypatch):
    """The row site C observes today describes a candidate item by six fields, and
    the builder is told so by `PromptDefinition.lists_candidate_scores`. This is
    why `tests/integration/test_r37_single_branch_is_byte_identical.py` needs no
    recapture: the dossier this call assembles is the one it always assembled."""
    seen = _candidate_items_seen(skeleton, monkeypatch,
                                 prompt=SimpleNamespace(ratified=True))
    item = seen["items"]["n-course"]

    assert item.missing_fields == ()
    assert item.score is None
    assert item.margin is None


def test_under_the_amended_row_each_candidate_carries_its_score_and_the_leader_its_margin(
        skeleton, monkeypatch):
    """MEASURED: the figure `score_candidates` produced for each offered node, and
    the ONE margin this engine computes, on the candidate the margin is about.

    SABOTAGE: put `margin` on every candidate -- the record starts claiming a
    comparison `_exact_margin` makes exactly once, against a runner-up most of the
    list never had.
    """
    seen = _candidate_items_seen(
        skeleton, monkeypatch,
        prompt=SimpleNamespace(ratified=True, lists_candidate_scores=True))
    scored = [item for item in seen["items"].values()
              if item.score is not None]

    assert scored, "no candidate carried a deterministic score"
    with_margin = [item for item in scored if item.margin is not None]
    assert len(with_margin) == 1, "the margin belongs to the leader alone"
    leader = with_margin[0]
    assert leader.score == max(item.score for item in scored)


def test_under_the_amended_row_a_candidate_names_the_levels_this_file_has_no_fact_for(
        skeleton, monkeypatch):
    """`00`:111's own question, answered per candidate: *"a file may have sufficient
    evidence for a broad branch but not for every deeper level."*

    The levels come off `IndexEntry.expected_values` -- the chain P10 wrote, read
    verbatim the way `_candidate_levels` reads it -- and what is missing is a field
    on that chain the SUBJECT states no fact for. `AMBIGUOUS` gives this file no
    `subject` fact at all, so the node whose chain fixes `subject` names it.

    SABOTAGE: ask the matched facts instead of the file's own -- a level goes
    "missing" because the folder did not happen to use it.
    """
    seen = _candidate_items_seen(
        skeleton, monkeypatch,
        prompt=SimpleNamespace(ratified=True, lists_candidate_scores=True))

    assert seen["items"]["n-course"].missing_fields == ("subject",)
    # And a node the tree fixes no level on says nothing, which is what P10 gave
    # it to say -- the same silence `_candidate_levels` keeps.
    assert seen["items"]["n-course-shared"].missing_fields == ()


# --- the C dossier's `conflicts` key, measured end to end ------------------------


def test_the_c_dossier_carries_the_conflicts_this_files_own_values_caused(
        skeleton, monkeypatch):
    """The ratified C text's line 31: *"each is a disagreement the engine found
    between something this file states and a folder it was being pulled towards."*

    MEASURED at the request: this file states `subject = PHYS1401`, `n-course-alt`
    expects `PHYS1402`, §6.3 suppresses it, and the suppression reaches the judge
    as a `conflicts` entry whose kind is the field. Nothing here was injected --
    `retrieve` reads the frozen tree through the deployment's own canonicaliser and
    `to_p8_conflicts` addresses the result by content.
    """
    import placement.pipeline as pipeline

    seen = {}

    def _fake_call(conn, request, **kwargs):
        seen["conflicts"] = request.conflicts
        return _verdict()

    monkeypatch.setattr(pipeline, "call_placement_steps", _as_steps(_fake_call))
    decision = _place(skeleton,
                      inputs=_model_inputs(skeleton,
                                           prompt=SimpleNamespace(ratified=True)),
                      evidence=_evidence(group_ids=PLACING_GROUPS))
    assert decision is not None
    assert [c.kind for c in seen["conflicts"]] == ["subject"]


# --- `00` amendment 7: one branch is one situation -------------------------------


def _two_situation_tree(*, contradicting=True):
    """The skeleton's tree with a SECOND top-level branch beside `Academics`.

    `n-paper` under `research` expects the same `subject = PHYS1401` the file
    states, so both branches hold a folder the file's own fact reaches and the
    only thing that can separate them is which situation the file is under. That
    is the measurement `00` amendment 7 is about: at HEAD placement read no
    situation at all, so a research paper in a coursework run was retrieved
    against the coursework tree and filed into a course.

    `contradicting=False` drops `n-course-alt`, whose expected `PHYS1402`
    contradicts the file. It is a CONFLICT rather than a candidate, and a run with
    no candidate left abstains `conflicting_facts` while one exists -- which is a
    true sentence about a different thing than the one under test.
    """
    from dataclasses import replace

    from p11.p10_fixtures import FROZEN_TREE

    by_id = {node.node_id: node for node in FROZEN_TREE.nodes}
    profiles = {profile.node_id: profile for profile in FROZEN_TREE.profiles}
    root = replace(by_id["n-academics"], node_id="n-research",
                   origin_node_id="n-research", display_label="research",
                   ordinal=5)
    paper = replace(by_id["n-course"], node_id="n-paper",
                    origin_node_id="n-paper", display_label="Papers",
                    parent_node_id="n-research", ordinal=1,
                    associated_group_ids=())
    nodes = tuple(node for node in FROZEN_TREE.nodes
                  if contradicting or node.node_id != "n-course-alt")
    nodes += (root, paper)
    kept = tuple(profile for profile in FROZEN_TREE.profiles
                 if contradicting or profile.node_id != "n-course-alt")
    kept += (replace(profiles["n-academics"], node_id="n-research",
                     display_label="research"),
             replace(profiles["n-course"], node_id="n-paper",
                     display_label="Papers", accepted_group_ids=()))
    freeze = replace(
        FROZEN_TREE.freeze_record,
        node_ids=tuple(node.node_id for node in nodes),
        legal_destination_ids=frozenset(node.node_id for node in nodes
                                        if node.accepts_placement))
    return replace(FROZEN_TREE, nodes=nodes, profiles=kept,
                   freeze_record=freeze)


#: The two branches this run proposed, by the label their ROOT node wears, which
#: is what `branch_situation.Branch.label` puts on the accepted group P10 builds a
#: branch from (`test_r37_per_branch_situation` reads them back as `Coursework`
#: and `career`).
TWO_SITUATIONS = {"Academics": "academic.coursework",
                  "research": "academic.research"}


@pytest.fixture()
def two_situations(p11_conn):
    """`skeleton` without the index, because each pin here indexes its own tree.

    `placement_index_entries` is unique on `(plan_version, node_id)`, so a fixture
    that indexed one tree and a test that indexed another would refuse.
    """
    create_llm_schema(p11_conn)
    create_budget_schema(p11_conn)
    for key in CEILINGS.values():
        set_ceiling(p11_conn, key, 8)
    _classify(p11_conn)
    _policy(p11_conn)
    return p11_conn


def _indexed(conn, tree):
    build_destination_index(conn, tree, component_version="P11-test",
                            observed_at=FIXED_CLOCK, canonical=NO_CANONICAL_RULE)
    return tree


def test_the_same_file_and_tree_are_filed_by_the_situation_alone(two_situations):
    """`00` amendment 7: the branch is the file's situation's, not the run's.

    One corpus, one tree, one fact -- and the destination changes with nothing but
    the situation site G named. A coursework file goes to the course under
    `Academics`; a research file with the same `subject = PHYS1401` goes to the
    folder under `research`, which before this rule was a rival it outscored and
    never a branch it belonged to.
    """
    tree = _indexed(two_situations, _two_situation_tree())
    coursework = _place(
        two_situations,
        inputs=_inputs(two_situations, tree=tree,
                       situation_of=lambda file_id: "academic.coursework",
                       the_situation_each_branch_carries=TWO_SITUATIONS),
        evidence=_evidence(group_ids=PLACING_GROUPS))
    research = _place(
        two_situations,
        inputs=_inputs(two_situations, tree=tree,
                       situation_of=lambda file_id: "academic.research",
                       the_situation_each_branch_carries=TWO_SITUATIONS),
        evidence=_evidence(group_ids=PLACING_GROUPS))

    assert coursework.outcome == v.PLACE
    assert coursework.destination.node_id == "n-course"
    assert research.outcome == v.PLACE
    assert research.destination.node_id == "n-paper"


def test_a_file_whose_situations_branch_has_no_folder_abstains(two_situations):
    """And it abstains with the word the empty candidate set already has.

    A situation this run built no branch for. Every folder in the tree is another
    life's, nothing is left to score, and `assess` says `no_supported_destination`
    -- the honest sentence: the run had no destination this file's evidence could
    support, not a folder it disliked.

    THE TREE HERE CARRIES NO CONTRADICTING NODE, deliberately. `n-course-alt`
    expects `PHYS1402` and is suppressed as a conflict, and an empty candidate set
    beside a conflict is `conflicting_facts` -- a true sentence about the fact and
    not about the branch.
    """
    conn = two_situations
    tree = _indexed(conn, _two_situation_tree(contradicting=False))
    decision = _place(
        conn,
        inputs=_inputs(conn, tree=tree,
                       situation_of=lambda file_id: "career.recruiting",
                       the_situation_each_branch_carries=TWO_SITUATIONS),
        evidence=_evidence(group_ids=PLACING_GROUPS))

    assert decision.outcome == v.ABSTAIN
    assert decision.abstention_reason == v.NO_SUPPORTED_DESTINATION
    assert decision.destination is None


def test_a_branch_the_partition_never_named_is_left_alone(two_situations):
    """The person's own top-level folders are branches too (`00`:100).

    They are nobody's situation, and a rule that refused every root it could not
    name would take away the folders the person already made. `research` is named
    here and `Academics` is not, so only `research`'s folders are another
    situation's and the coursework file keeps the course it always had.
    """
    tree = _indexed(two_situations, _two_situation_tree())
    decision = _place(
        two_situations,
        inputs=_inputs(two_situations, tree=tree,
                       situation_of=lambda file_id: "academic.coursework",
                       the_situation_each_branch_carries={
                           "research": "academic.research"}),
        evidence=_evidence(group_ids=PLACING_GROUPS))

    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == "n-course"


def test_a_groups_answer_in_another_situations_branch_does_not_carry_a_member(
        two_situations):
    """`00` amendment 7, on the group path: a research file whose group answered
    a coursework folder sits apart from that answer and is placed on its own,
    under its own branch -- the same finding step 6 drops a candidate on."""
    from placement.pipeline import GroupAnswer

    tree = _indexed(two_situations, _two_situation_tree())
    decision = _place(
        two_situations,
        inputs=_inputs(two_situations, tree=tree,
                       situation_of=lambda file_id: "academic.research",
                       the_situation_each_branch_carries=TWO_SITUATIONS),
        evidence=_evidence(group_ids=PLACING_GROUPS),
        group_answer=GroupAnswer(group_id=PLACING_GROUPS[0], node_id="n-course",
                                 membership="member"))

    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == "n-paper", decision
    assert not decision.group_support, decision
