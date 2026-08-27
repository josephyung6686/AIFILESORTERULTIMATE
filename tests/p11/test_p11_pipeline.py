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

import pytest

from database_agent.budget import set_ceiling
from database_agent.files_table import get_file, record_file
from llm_harness.budgets import create_budget_schema
from llm_harness.harness import CallDependencies
from llm_harness.records import EvidenceItem, P8Verdict
from llm_harness.schema import create_llm_schema
from llm_harness.vocabulary import (
    ACCEPT_CONTEXT_SUPPORTED, CHOOSE_RESIDUAL_DESTINATION,
    LEAVE_IN_CURRENT_LOCATION, LEAVE_IN_PLACE as P8_LEAVE_IN_PLACE,
    RETURN_CONFIRMED_GROUP, RETURN_TO_PLACEMENT as P8_RETURN_TO_PLACEMENT,
    VALID_REVIEW_REQUIRED,
)
from privacy.classification import ClassificationRecord, observation_key
from privacy.classification_store import ClassificationStore
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy

from placement import vocabulary as v
from placement.config import CEILINGS, SupportPolicy, placement_limits
from placement.index import build_destination_index
from placement.learning import basis_key_for, record_correction
from placement.records import MatchingFact, Subject
from placement.residual import ResidualSetDecision, record_set_decision
from placement.store import current_decision
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE

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
        call_dependencies=None, model_call_request=None, chosen_node_of=None,
        residual_action_of=None, sensitivity_policy=None, p2=None,
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
    # P7's detector does not exist, so this is the ordinary path on a real corpus:
    # no classification means blocked, never a default to public.
    from placement.privacy import ClassificationRequired

    for key in CEILINGS.values():
        set_ceiling(p11_conn, key, 8)
    _policy(p11_conn)
    build_destination_index(p11_conn, FROZEN_TREE, component_version="P11-test",
                            observed_at=FIXED_CLOCK)
    with pytest.raises(ClassificationRequired):
        _place(p11_conn)


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
             disposition=VALID_REVIEW_REQUIRED, reasons=()) -> P8Verdict:
    return P8Verdict(
        verdict_id="vd-1", dossier_id="ds-1", claim_ref="claim-1",
        outcome=outcome, disposition=disposition, reasons=tuple(reasons),
        may_propose=True, requires_review=True, citations_checked=(),
        scope="file", validator_version="1", policy_version="policy-1",
        plan_version="plan-1")


def _model_call_request(*, subject_ref, evidence_items, max_dossier_tokens):
    """A real P7 release request. `DossierRequest` refuses anything else, which
    is what makes the assertions below a binding against the live seam."""
    from privacy.items import Excerpt, TextSpan
    from privacy.release import ModelCallRequest, ModelTarget, Target

    return ModelCallRequest(
        stage="placement", target=Target(file_ids=(subject_ref.split(":")[1],)),
        model_target=ModelTarget(locality="local", model_id="llama-local",
                                 provider="on-device"),
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
                               max_estimated_cost=Decimal("10")),
        estimated_cost=Decimal("1"), actual_cost=Decimal("1"),
        allowed_vocabulary=None, policy_version="policy-1")


def _model_inputs(conn, **overrides):
    values = dict(gate=object(), model_client=object(), prompt=object(),
                  call_dependencies=_call_dependencies(),
                  model_call_request=_model_call_request,
                  chosen_node_of=lambda _verdict: "n-course-shared",
                  sensitivity_policy=lambda *_a, **_k: True)
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
                                 observation_key=f"obs-{group_id}"),),
        pre_model_signals={}, anchor_count=len(file_ids),
        coherence_verdict=COHERENT, coherence_citations=(f"obs-{group_id}",),
        group_category="course", display_label="PHYS1402 packet",
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
