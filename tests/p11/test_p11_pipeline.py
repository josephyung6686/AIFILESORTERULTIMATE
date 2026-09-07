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
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE
from llm_harness.fixtures import FIXTURE_HANDLE_KEY

#: 0.50 sits ABOVE a direct fact alone (3/7 = 0.4286) and BELOW a direct fact plus
#: an accepted group (5/7 = 0.7143). Both halves are asserted below, so a threshold
#: moved out of that band fails loudly instead of turning every placement into an
#: abstention.
POLICY = SupportPolicy(policy_id="skeleton-v1", support_scale_max=1.0,
                       minimum_support_threshold=0.5, margin_threshold=0.2)

OBS = observation_key(content_hash="h1", extractor_name="fixture",
                      locator="page-1", raw_value="PHYS1401")

SUBJECT = Subject(kind=v.FILE, file_id="f1", content_hash="h1", group_id=None,
                  member_file_ids=())

#: The evidence that makes the skeleton place, and the arithmetic that makes it
#: place. `assess` normalises by `_MAX_WEIGHT = 3 + 2 + 1 + 1 = 7`:
#:
#:   n-course        direct_fact(3) + accepted_group(2) = 5/7 = 0.7143
#:   n-course-shared                  accepted_group(2) = 2/7 = 0.2857
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
                            observed_at=FIXED_CLOCK)
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
        the_folder_each_file_is_in={},
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
            ("judge_bounded_ambiguity", "call_placement"),
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
    assert two.margin_over_next == pytest.approx(3 / 7)   # 5/7 - 2/7
    assert two.support_score == pytest.approx(5 / 7)
    assert two.meets_threshold is True
    assert [a.node_id for a in decision.alternatives] == [
        "n-course", "n-course-shared"]
    # The suppressed node is visible, so the review surface can answer
    # "why not PHYS1402?" (§6.3, Done-means 4).
    assert "n-course-alt" in {node for conflict in decision.conflicts_considered
                              for node in conflict.suppressed_node_ids}


def test_the_direct_fact_alone_does_not_clear_the_threshold(skeleton):
    # The other half of the arithmetic, asserted rather than assumed. A threshold
    # the strongest available evidence cannot reach would make every placement in
    # this part unreachable, and this test is what would catch it.
    decision = _place(skeleton, evidence=_evidence())
    assert decision.outcome == v.ABSTAIN
    assert decision.two_condition.support_score == pytest.approx(3 / 7)
    assert decision.two_condition.meets_threshold is False


def test_a_mathematical_looking_file_never_produces_math_stuff(skeleton):
    decision = _place(skeleton,
                      evidence=_evidence(facts=(), semantic_neighbours=()))
    assert decision.outcome == v.ABSTAIN
    assert decision.destination is None
    assert decision.abstention_reason == v.NO_SUPPORTED_DESTINATION


#: A policy whose support threshold two candidates can clear at once. The
#: fixture's own POLICY sits at 0.50, above every score `FROZEN_TREE` can
#: produce, so "more than one home cleared it" is unreachable there -- and a
#: sentence about two homes cannot be tested against a tree where one is
#: arithmetically impossible.
TWO_HOMES_POLICY = SupportPolicy(policy_id="two-homes-v1", support_scale_max=1.0,
                                 minimum_support_threshold=0.25,
                                 margin_threshold=0.2)


def test_a_file_with_two_supported_homes_is_told_it_has_two_homes(skeleton):
    """§3a of `planning/59-FINAL-UX-EVALUATION.md`, in the sentence the user reads.

    The direct fact reaches `n-course` (3/7) and the accepted group reaches
    `n-course-shared` (2/7). Both clear 0.25 on their own; the margin between
    them is 1/7, inside the 0.2 band. Nothing moves -- and the record says why in
    the person's terms, naming the destinations rather than complaining about the
    evidence that produced them.
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
                            observed_at=FIXED_CLOCK)
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
        evidence_for=lambda file_id: _evidence(
            group_ids=PLACING_GROUPS if file_id == "f1" else ()),
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
    file_id, content_hash = _real_file(skeleton, tmp_path / "corpus")
    _classify(skeleton, file_id=file_id, content_hash=content_hash,
              protected=True, handling_class="sensitive_personal")
    subject = Subject(kind=v.FILE, file_id=file_id, content_hash=content_hash,
                      group_id=None, member_file_ids=())
    decision = _place(skeleton, subject=subject)
    assert decision.outcome == v.PLACE
    assert decision.privacy.protected is True
    assert decision.review_policy == v.REVIEW_REQUIRED


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


#: A bounded ambiguity, in the arithmetic. The direct fact reaches n-course
#: (3/7 = 0.4286, BELOW the 0.50 threshold), the accepted group reaches
#: n-course-shared (2/7 = 0.2857) and the semantic channel reaches n-general
#: (0/7). No candidate clears the threshold and the margin is 1/7 = 0.1429,
#: inside the 0.20 band -- so `unique_direct_match` is False, `needs_model_call`
#: is True, and the deterministic answer alone would be `low_margin`.
AMBIGUOUS = dict(group_ids=("g-shared",), semantic_neighbours=("n-general",))


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

    monkeypatch.setattr(pipeline, "call_placement", _fake_call)
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


def test_a_model_choice_outside_the_frozen_tree_places_nothing(skeleton,
                                                               monkeypatch):
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement",
                        lambda *_a, **_k: _verdict())
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

    monkeypatch.setattr(pipeline, "call_placement", _never)
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

    monkeypatch.setattr(pipeline, "call_placement",
                        lambda *_a, **_k: pytest.fail("§8.4 gates first"))
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

    monkeypatch.setattr(pipeline, "call_placement", _fake_call)
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

    monkeypatch.setattr(pipeline, "call_placement",
                        lambda *_a, **_k: pytest.fail("§8.4 gates first"))
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
    """(c) The standing rule: read on this device and shown to no model."""
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement",
                        lambda *_a, **_k: pytest.fail("§8.4 gates first"))
    _policy(skeleton, mode="local_model")
    subject = _protected_subject(skeleton, tmp_path, name="passport-r118.pdf")
    decision = _place(skeleton, subject=subject, inputs=_model_inputs(skeleton),
                      evidence=_evidence(**AMBIGUOUS))

    assert decision.outcome == v.ABSTAIN
    assert decision.abstention_reason == v.PRIVACY_BLOCKED
    assert "protected material" in decision.explanation
    assert v.PROTECTED_REASON in decision.privacy.local_only_reasons


def test_r118_an_unclassified_file_stays_off_a_local_model_with_the_flag_as_it_is(
        skeleton, monkeypatch, tmp_path):
    """(d) Open question 5 is the owner's, and P11's pinned answer is still no."""
    import placement.pipeline as pipeline
    from placement import privacy as p11_privacy

    assert p11_privacy.LOCAL_CALLS_ON_UNCLASSIFIED is False
    monkeypatch.setattr(pipeline, "call_placement",
                        lambda *_a, **_k: pytest.fail("§8.4 gates first"))
    _policy(skeleton, mode="local_model")
    subject = _ordinary_subject(skeleton, tmp_path, name="scan-r118.pdf",
                                classify=False)
    decision = _place(skeleton, subject=subject, inputs=_model_inputs(skeleton),
                      evidence=_evidence(**AMBIGUOUS))

    assert decision.outcome == v.ABSTAIN
    assert decision.abstention_reason == v.PRIVACY_BLOCKED
    assert "has not been classified" in decision.explanation
    assert v.UNCLASSIFIED_REASON in decision.privacy.local_only_reasons


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
    """
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement",
                        lambda *_a, **_k: pytest.fail("§8.4 gates first"))
    file_id, content_hash = _real_file(skeleton, tmp_path / "corpus",
                                       name="scan.pdf", body=b"%PDF-1.4 u")
    # Deliberately NOT classified: P7's detector declined to say anything.
    subject = Subject(kind=v.FILE, file_id=file_id, content_hash=content_hash,
                      group_id=None, member_file_ids=())
    decision = _place(skeleton, subject=subject,
                      inputs=_model_inputs(skeleton),
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
        evidence_for=lambda file_id: _evidence(
            group_ids=PLACING_GROUPS if file_id == "f1" else ()),
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

    kwargs = dict(subjects=(SUBJECT,), group_ids=(),
                  inputs=_inputs(conn, partition=_partition),
                  evidence_for=lambda file_id: _evidence(),
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
                  evidence_for=lambda file_id: _evidence(),
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

    monkeypatch.setattr(pipeline, "call_placement", _fake_call)
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


def _second_group(conn, *, group_id, file_ids):
    """A second ACCEPTED P9 group, written through P9's own writers.

    Nothing here is a stand-in: `group_state_as_of` and `memberships_for_group`
    read these rows, and `place_group` calls both.
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
            file_id=file_id, content_hash=f"h-{file_id}", basis=DIRECT_ANCHOR,
            decision=INCLUDED, decision_source=RULES,
            support=(Support(support_kind=SHARED_VALIDATED_FACT,
                             observation_key=f"obs-{file_id}",
                             quote_or_field="subject", location="body",
                             edge_ref=None),),
            insufficient_evidence=False, insufficiency_statement=None,
            conflicts=(), outlier_flag=NOT_FLAGGED,
            validation_verdict_ref=None, created_at=FIXED_CLOCK))
        _classify(conn, file_id=file_id, content_hash=f"h-{file_id}")
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
def _two_home_evidence(file_id):
    if file_id in ("f-duke-x", "f-shared"):
        return _evidence(
            facts=(MatchingFact(file_fact_id="ff2", field="subject",
                                value="PHYS1402", reliability=v.DIRECT,
                                evidence_ref=OBS),),
            group_ids=("g-phys1402",))
    return _evidence(group_ids=("g-phys1401",))


def _two_homes(conn, tree=None):
    from placement.pipeline import run_corpus

    group_a = _seeded(conn)
    _second_group(conn, group_id="g-phys1402-packet",
                  file_ids=("f-duke-x", "f-shared"))
    # `f-shared` joins group A too, so it has accepted membership in both.
    from grouping.records import Membership, Support
    from grouping.store import record_membership
    from grouping.vocabulary import (
        DIRECT_ANCHOR, INCLUDED, NOT_FLAGGED, RULES, SHARED_VALIDATED_FACT,
    )

    record_membership(conn, Membership(
        membership_id="m-columbia-f-shared", group_id=group_a,
        file_id="f-shared", content_hash="h-f-shared", basis=DIRECT_ANCHOR,
        decision=INCLUDED, decision_source=RULES,
        support=(Support(support_kind=SHARED_VALIDATED_FACT,
                         observation_key="obs-f-shared",
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
        inputs=inputs, evidence_for=_two_home_evidence,
        component_version="P11-test", observed_at=FIXED_CLOCK)


def _multi_home(result):
    return next(d for d in result.decisions if d.subject.file_id == "f-shared")


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


def _two_homes_asking(conn):
    """The same corpus under the asking selector. A second run supersedes the
    first decision about each subject, which is §8.2's own rule."""
    from placement.pipeline import run_corpus

    # A distinct set label, because `surface_residual_sets` addresses a set as
    # `plan_version:label` with no supersede link -- so a second surfacing of the
    # same label in one version collides on the primary key. Reported as a gap;
    # it is `residual.py`'s address to change, not this test's to work around
    # silently.
    inputs = _inputs(conn,
                     partition=lambda ids: _partition(ids, label="Asked"),
                     ask_or_abstain=lambda ids: v.ASK_USER)
    return run_corpus(
        conn, subjects=(), group_ids=("g-columbia", "g-phys1402-packet"),
        inputs=inputs, evidence_for=_two_home_evidence,
        component_version="P11-test", observed_at="2026-08-27T01:00:00Z")


def test_a_shared_branch_takes_the_file_and_the_packets_still_do_not(skeleton):
    # §6.9's other answer: a tree that froze a shared-material branch places the
    # file ABOVE the competition. `resolve_multi_home` refuses a branch that IS
    # one of the competitors, so this can never become an arbitrary pick.
    from p11.p10_fixtures import tree_with
    from tree_design.vocabulary import SHARED_BRANCH

    decision = _multi_home(
        _two_homes(skeleton, tree=tree_with(shared_material_policy=SHARED_BRANCH)))
    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == "n-course-shared"
    assert decision.confidence_class == v.SHARED_MATERIAL_DECISION
    assert decision.review_policy == v.REVIEW_REQUIRED


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
                            observed_at=FIXED_CLOCK)
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
    monkeypatch.setattr(pipeline, "call_placement", _budgeted_call)
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

    monkeypatch.setattr(pipeline, "call_placement", _capture)
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

    monkeypatch.setattr(pipeline, "call_placement",
                        lambda *_a, **_k: _verdict())
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
    """
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement",
                        lambda *_a, **_k: pytest.fail("§8.4 gates first"))
    file_id, content_hash = _real_file(skeleton, tmp_path / "corpus",
                                       name="syllabus.pdf", body=b"%PDF-1.4 s")
    subject = Subject(kind=v.FILE, file_id=file_id, content_hash=content_hash,
                      group_id=None, member_file_ids=())
    decision = _place(skeleton, subject=subject,
                      inputs=_model_inputs(skeleton),
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

    monkeypatch.setattr(pipeline, "call_placement", _fake_call)


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

    monkeypatch.setattr(pipeline, "call_placement", _never)
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


def test_r74_a_protected_file_the_rules_could_place_keeps_its_home(
        skeleton, monkeypatch, tmp_path):
    """The file the model was going to be asked about, and could not be.

    Nothing is sent and nothing is assembled -- `call_placement` raising is the
    assertion that the gate still comes first. What changes is only what the run
    does with the refusal it already had: it places the file on the unique direct
    match, exactly as the same run without a model configured would.
    """
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement", lambda *_a, **_k: pytest.fail(
        "§8.4 gates before any dossier, and R-74 does not move that"))
    subject = _protected_subject(skeleton, tmp_path)
    decision = _place(skeleton, subject=subject,
                      inputs=_model_inputs(skeleton))

    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == "n-course"
    assert decision.confidence_class == v.EXACT_FACT_MATCH


def test_r74_the_record_says_the_rules_placed_it_and_names_neither_model_nor_person(
        skeleton, monkeypatch, tmp_path):
    """`104` R-28's actor rule. No model saw this file and nobody was asked, so a
    record that credited either would be claiming an act that never happened."""
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement",
                        lambda *_a, **_k: pytest.fail("§8.4 gates first"))
    subject = _protected_subject(skeleton, tmp_path, name="passport-2.pdf")
    decision = _place(skeleton, subject=subject,
                      inputs=_model_inputs(skeleton))

    assert "placed by the rules" in decision.explanation
    assert "may be assembled for a model" in decision.explanation
    assert "hierarchical destination judge" not in decision.explanation
    assert " you " not in decision.explanation


def test_r74_a_protected_file_the_rules_could_not_place_still_abstains(
        skeleton, monkeypatch, tmp_path):
    """The twin, and the half that keeps this from being a widening. A bounded
    ambiguity has no deterministic answer to fall back TO: an offline run abstains
    on it too, so `privacy_blocked` is still what the record says."""
    import placement.pipeline as pipeline

    monkeypatch.setattr(pipeline, "call_placement",
                        lambda *_a, **_k: pytest.fail("§8.4 gates first"))
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
    monkeypatch.setattr(pipeline, "call_placement", lambda *_a, **_k: Refusal(
        denied=denied, validator_version="vv", policy_version="pv"))
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

    monkeypatch.setattr(pipeline, "call_placement", _fake_call)
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
    assert set(groups) == {"g-shared"}
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


# --- `104` R-O at site C --------------------------------------------------------


def test_a_refusal_at_site_c_leaves_the_deterministic_placement_standing(
        skeleton, monkeypatch):
    """A refused call is not a judgement about the file, so it does not take the
    file's home away.

    `104` §13.5's Q-A clause is the rule: *"Q-A governs whenever a model is
    configured; with no model configured the deterministic path remains the
    fallback."* A call that could not be made is the same position as no model at
    all for THIS file -- and the alternative, which is what the code did, is a
    `ModelJudgementUnavailable` out of `_require_verdict` that ends the whole run
    on the file after it as well.
    """
    import placement.pipeline as pipeline
    from privacy.resolve import UnresolvableSpan

    def _refuse(conn, request, **kwargs):
        raise UnresolvableSpan(
            "observation 'sha256:3ea4' belongs to a file outside request.target")

    monkeypatch.setattr(pipeline, "call_placement", _refuse)
    refused = _place(skeleton, inputs=_model_inputs(skeleton))
    offline = _place(skeleton)

    assert refused.outcome == offline.outcome == v.PLACE
    assert refused.destination.node_id == offline.destination.node_id
    assert refused.confidence_class == offline.confidence_class


def test_a_programming_error_at_site_c_still_surfaces(skeleton, monkeypatch):
    import placement.pipeline as pipeline

    def _bug(conn, request, **kwargs):
        raise AttributeError("'NoneType' object has no attribute 'locality'")

    monkeypatch.setattr(pipeline, "call_placement", _bug)
    with pytest.raises(AttributeError):
        _place(skeleton, inputs=_model_inputs(skeleton))
