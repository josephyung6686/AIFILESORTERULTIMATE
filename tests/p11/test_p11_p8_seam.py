"""P11 supplies authorities and reads a verdict. It writes no Site C check."""
from __future__ import annotations

import ast
import dataclasses
import inspect
import json
from pathlib import Path

import pytest

from llm_harness.fixtures import SITE_C_OUTCOME_PAIRS, SITE_C_REASON_PAIRS
from llm_harness.harness import CallDependencies, run_call
from llm_harness.placement_validation import (
    PlacementDependencies, ResidualDependencies, record_cd_verdict,
    revalidate_for_plan, validate_placement_response,
)
from llm_harness.records import Conflict as P8Conflict, P8Verdict
from llm_harness.records import ValidationUnavailable
from llm_harness.sites import SiteDependencies, dispatch
from llm_harness.vocabulary import (
    ABSTAIN, ACCEPT_DIRECT, BUDGET_EXHAUSTED, INVENTED_NODE, REJECT,
    SCOPE_NODE, SITE_C_REASON_CODES,
)

from placement import vocabulary as v
from placement.config import SupportPolicy
from placement.index import build_destination_index
from placement.p8_seam import (
    EvidenceSnapshotRequired, ModelPathUnavailable, call_placement,
    evidence_snapshot_id_for, placement_authorities, residual_authorities,
    site_dependencies, to_p8_conflicts, transcribe,
)
from placement.records import ConflictConsidered
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE

POLICY = SupportPolicy(policy_id="fixture-v1", support_scale_max=1.0,
                       minimum_support_threshold=0.5, margin_threshold=0.2)
PLACEMENT_SOURCES = Path(__file__).resolve().parents[2] / "src" / "placement"


@pytest.fixture()
def indexed(p11_conn):
    build_destination_index(p11_conn, FROZEN_TREE,
                            component_version="P11-test", observed_at=FIXED_CLOCK)
    return p11_conn


def _permissive(*_a, **_k):
    """The exact shape a caller must not be able to smuggle past a site check."""
    return True


def _legal_node_id() -> str:
    return next(node.node_id for node in FROZEN_TREE.nodes if node.accepts_placement)


# --- the authorities ---------------------------------------------------------------

def test_the_four_placement_authorities_are_exactly_p8s_fields(indexed):
    deps = placement_authorities(indexed, plan_version="plan-1", policy=POLICY,
                                 sensitivity_policy=_permissive)
    assert isinstance(deps, PlacementDependencies)
    assert {f.name for f in dataclasses.fields(PlacementDependencies)} == {
        "node_exists", "support_threshold", "margin_predicate",
        "sensitivity_policy"}
    assert deps.support_threshold == POLICY.minimum_support_threshold
    assert deps.margin_predicate(0.9, 0.5) is True
    assert deps.margin_predicate(0.9, 0.8) is False


def test_node_exists_is_p11s_index_and_answers_p8s_two_argument_call(indexed):
    deps = placement_authorities(indexed, plan_version="plan-1", policy=POLICY,
                                 sensitivity_policy=_permissive)
    assert deps.node_exists(_legal_node_id(), "plan-1") is True
    assert deps.node_exists("n-never-frozen", "plan-1") is False
    # A dossier stamped with another plan version is not a legal decision (§8.8).
    assert deps.node_exists(_legal_node_id(), "plan-2") is False


def test_the_three_residual_authorities_are_exactly_p8s_fields(indexed):
    deps = residual_authorities(indexed, plan_version="plan-1",
                                approved_target_ids=["n-residual"],
                                sensitivity_policy=_permissive)
    assert isinstance(deps, ResidualDependencies)
    assert {f.name for f in dataclasses.fields(ResidualDependencies)} == {
        "node_exists", "sensitivity_policy", "approved_target_ids"}
    assert deps.approved_target_ids == ("n-residual",)


def test_an_absent_sensitivity_authority_refuses_rather_than_defaulting(indexed):
    # P7 owns whether this release is permitted. A P11 default would be P11
    # answering a privacy question with a placement answer.
    with pytest.raises(ModelPathUnavailable):
        placement_authorities(indexed, plan_version="plan-1", policy=POLICY,
                              sensitivity_policy=None)
    with pytest.raises(ModelPathUnavailable):
        residual_authorities(indexed, plan_version="plan-1",
                             approved_target_ids=(), sensitivity_policy=None)


def test_an_unsettled_support_policy_refuses_rather_than_reaching_p8(indexed):
    # §6.10's threshold and margin are SPEC Open question 1 and are injected.
    # Handing P8 a threshold nobody chose would make every verdict in the corpus
    # rest on a number with no policy id to audit it by.
    from placement.config import ConfigurationRequired

    with pytest.raises(ConfigurationRequired):
        placement_authorities(indexed, plan_version="plan-1", policy=None,
                              sensitivity_policy=_permissive)


def test_the_bundle_leaves_the_sites_p11_does_not_own_empty(indexed):
    bundle = site_dependencies(placement=placement_authorities(
        indexed, plan_version="plan-1", policy=POLICY,
        sensitivity_policy=_permissive))
    assert isinstance(bundle, SiteDependencies)
    assert bundle.fact is None and bundle.template is None
    assert bundle.residual is None


def test_the_bundle_is_accepted_by_p8s_own_call_dependencies(indexed):
    # The seam bound against the live shape: P11's bundle and P11's legal set go
    # into the record `run_call` actually reads, not into a lookalike.
    from decimal import Decimal

    from llm_harness.budgets import ScanBudget
    from placement.index import legal_node_ids

    deps = CallDependencies(
        proposal_class=v.PLACEMENT, basis_key="f1->n-course",
        learning_scope="file", learning_subject_id="f1",
        evidence_resolver=lambda key: "span-1",
        site_dependencies=site_dependencies(placement=placement_authorities(
            indexed, plan_version="plan-1", policy=POLICY,
            sensitivity_policy=_permissive)),
        contradicts=lambda *_a, **_k: False, unreduced_fits=True,
        summarized_fits=False, anchors_fit=False, split_shard_fits=(),
        split_shards=(),
        scan_budget=ScanBudget(scan_id="scan-p11", corpus_file_count=1000,
                               max_calls_per_1000_files=4,
                               max_estimated_cost=Decimal("10"),
                               min_calls_per_scan=0),
        estimated_cost=Decimal("1"), actual_cost=Decimal("1"),
        allowed_vocabulary=tuple(sorted(
            legal_node_ids(indexed, plan_version="plan-1"))),
        policy_version="policy-1")
    assert deps.site_dependencies.placement is not None
    assert _legal_node_id() in deps.allowed_vocabulary


# --- P8 still refuses, because the checks are P8's --------------------------------

def test_a_permissive_sensitivity_authority_cannot_pass_an_invented_node(indexed):
    # The point of the whole task: authorities are not acceptance. P8 still
    # refuses, and P11 writes none of the checks that do the refusing.
    pair = next(p for p in SITE_C_OUTCOME_PAIRS if p.name == "direct_accept")
    body = json.loads(pair.response_bytes)
    body["claims"][0]["payload"]["destination"] = "n-invented"
    deps = site_dependencies(placement=PlacementDependencies(
        node_exists=lambda *_a: True, support_threshold=0.0,
        margin_predicate=_permissive, sensitivity_policy=_permissive))
    verdicts, _ = dispatch(
        None, pair.dossier, json.dumps(body, separators=(",", ":")).encode(),
        site_dependencies=deps, evidence_resolver=lambda key: "span-1",
        contradicts=lambda *_a, **_k: False, model_id="fixture-model",
        prompt_fingerprint="fp-1", dossier_builder="p11-test",
        release_audit_id=17, policy_version="policy-1", apply_consequence=False,
    )
    assert verdicts[0].outcome == REJECT
    assert INVENTED_NODE in verdicts[0].reasons


def test_omitting_an_authority_is_unavailable_and_never_a_pass():
    pair = SITE_C_OUTCOME_PAIRS[0]
    result = validate_placement_response(
        pair.dossier, pair.response_bytes,
        evidence_resolver=lambda key: "span-1",
        contradicts=lambda *_a, **_k: False, dependencies=None,
        model_id="m", prompt_fingerprint="fp", dossier_builder="p11-test",
        release_audit_id=17)
    assert isinstance(result, ValidationUnavailable)
    assert "support_threshold" in result.missing


def test_p11_writes_no_site_c_reason_code():
    # Every one of P8's eleven Site C codes belongs to P8. A P11 module spelling
    # one would be a second validator with a second opinion.
    offenders = []
    for path in sorted(PLACEMENT_SOURCES.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and node.value in SITE_C_REASON_CODES:
                offenders.append((path.name, node.lineno, node.value))
    assert offenders == []


def test_p11_constructs_no_dossier_and_imports_no_model_client():
    banned = {"Dossier", "ModelClient", "Gate"}
    offenders = []
    for path in sorted(PLACEMENT_SOURCES.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                offenders += [(path.name, node.lineno, a.name)
                              for a in node.names if a.name in banned]
    assert offenders == []


# --- the conversions ----------------------------------------------------------------

def test_a_p11_conflict_becomes_p8s_two_field_shape():
    # Three records wear the word "conflict": P9's, P8's and P11's. The
    # conversion runs one way, here, so nothing downstream has to guess which.
    mine = ConflictConsidered(kind="subject", conflicting_value="PHYS1402",
                              suppressed_node_ids=("n-course",),
                              evidence_ref="obs-2")
    converted = to_p8_conflicts((mine,))
    assert all(isinstance(item, P8Conflict) for item in converted)
    assert converted[0].kind == "subject"
    assert converted[0].conflict_id


def test_two_different_conflicts_never_share_one_id():
    # Site C rejects a response that ignored a dossier conflict, matching on the
    # id. Two conflicts collapsing to one id would let a model ignore one of them
    # and still be accepted.
    a = ConflictConsidered(kind="subject", conflicting_value="PHYS1402",
                           suppressed_node_ids=("n-a",), evidence_ref="obs-2")
    b = ConflictConsidered(kind="subject", conflicting_value="PHYS1403",
                           suppressed_node_ids=("n-a",), evidence_ref="obs-2")
    first, second = to_p8_conflicts((a, b))
    assert first.conflict_id != second.conflict_id
    assert to_p8_conflicts((a,))[0].conflict_id == first.conflict_id


def test_the_evidence_snapshot_id_is_a_content_address():
    # Required at C and D before the spend and minted by nobody else. Two
    # dossiers over the same evidence share one id, which is what makes a replay
    # recognisable as a replay.
    first = evidence_snapshot_id_for(plan_version="plan-1",
                                     observation_keys=("obs-2", "obs-1"))
    second = evidence_snapshot_id_for(plan_version="plan-1",
                                      observation_keys=("obs-1", "obs-2"))
    third = evidence_snapshot_id_for(plan_version="plan-2",
                                     observation_keys=("obs-1", "obs-2"))
    fourth = evidence_snapshot_id_for(plan_version="plan-1",
                                      observation_keys=("obs-1", "obs-3"))
    assert first == second
    assert len({first, third, fourth}) == 3
    assert first


def test_a_snapshot_of_no_evidence_is_refused_rather_than_addressed():
    # An id over an empty citation set would be shared by every evidence-free
    # dossier in the corpus, and `revalidate_for_plan` keys a re-validation on a
    # CHANGED snapshot: they would all look like replays of one another.
    with pytest.raises(EvidenceSnapshotRequired):
        evidence_snapshot_id_for(plan_version="plan-1", observation_keys=())


# --- the verdict, transcribed ------------------------------------------------------

def _verdict_for(pair, **dep_overrides):
    values = dict(node_exists=lambda node_id, _plan: node_id != "absent",
                  support_threshold=0.0, margin_predicate=lambda *_a: True,
                  sensitivity_policy=_permissive)
    values.update(dep_overrides)
    return validate_placement_response(
        pair.dossier, pair.response_bytes,
        evidence_resolver=lambda key: "span-1",
        contradicts=lambda *_a, **_k: False,
        dependencies=PlacementDependencies(**values),
        model_id="m", prompt_fingerprint="fp", dossier_builder="p11-test",
        release_audit_id=17)[0][0]


def test_the_verdict_vocabulary_is_carried_unchanged_into_the_record():
    # MINOR 7: P8's `outcome` IS the record's `verdict`. No mapping table.
    pair = next(p for p in SITE_C_OUTCOME_PAIRS if p.name == "direct_accept")
    verdict = _verdict_for(pair)
    assert verdict.outcome == ACCEPT_DIRECT
    outcome, reason, deferred = transcribe(verdict, assessment=None)
    assert outcome == v.PLACE
    assert reason is None and deferred is None


def test_a_context_supported_accept_is_still_a_placement():
    pair = next(p for p in SITE_C_OUTCOME_PAIRS if p.name == "context_accept")
    outcome, reason, deferred = transcribe(_verdict_for(pair), assessment=None)
    assert outcome == v.PLACE
    assert reason is None and deferred is None


def test_a_weak_verdict_becomes_an_abstention_with_a_named_reason():
    pair = next(p for p in SITE_C_REASON_PAIRS
                if p.expected_reasons == ("INSUFFICIENT_MARGIN",))
    verdict = _verdict_for(pair, node_exists=lambda *_a: True,
                           margin_predicate=lambda *_a: False)
    outcome, reason, deferred = transcribe(verdict, assessment=None)
    assert outcome == v.ABSTAIN
    assert reason == v.LOW_MARGIN
    assert deferred is None


def _pre_call_budget_verdict() -> P8Verdict:
    return P8Verdict(
        verdict_id="pre-call:C_placement:f1:BUDGET_EXHAUSTED",
        dossier_id="pre-call:C_placement:f1", claim_ref="pre-call",
        outcome=ABSTAIN, disposition=ABSTAIN, reasons=(BUDGET_EXHAUSTED,),
        may_propose=False, requires_review=False, citations_checked=(),
        scope=SCOPE_NODE, validator_version="v", policy_version="p",
        plan_version="plan-1")


def test_a_budget_exhausted_verdict_defers_and_never_abstains_evidentially():
    # §8.6, Done-means 14. `BUDGET_EXHAUSTED` is a pre-call terminal P8 persists
    # as an `abstain` verdict; P11 must not read that as a judgement about
    # evidence, because none was made.
    outcome, reason, deferred = transcribe(_pre_call_budget_verdict(),
                                           assessment=None)
    assert outcome == v.ABSTAIN
    assert reason == v.BUDGET_DEFERRED
    assert deferred == v.PLACEMENT_SCORING


def test_a_budget_deferral_transcribes_into_a_record_the_contract_accepts():
    # The record refuses `budget_deferred` without a deferred stage. A
    # transcription that dropped the stage would build a decision that cannot be
    # constructed, which is a failure one task later and one task away.
    from p11.test_p11_records import _decision

    outcome, reason, deferred = transcribe(_pre_call_budget_verdict(),
                                           assessment=None)
    built = _decision(outcome=outcome, destination=None, abstention_reason=reason,
                      deferred_stage=deferred)
    assert built.deferred_stage == v.PLACEMENT_SCORING


def test_an_unmapped_refusal_falls_back_to_the_scorers_own_reason():
    pair = next(p for p in SITE_C_REASON_PAIRS
                if p.expected_reasons == ("NODE_NOT_IN_FROZEN_TREE",))
    verdict = _verdict_for(pair, node_exists=lambda *_a: False)

    class _Assessment:
        abstention_reason = v.CONFLICTING_FACTS

    outcome, reason, _ = transcribe(verdict, assessment=_Assessment())
    assert outcome == v.ABSTAIN
    assert reason == v.CONFLICTING_FACTS


def test_an_unmapped_refusal_with_no_assessment_says_no_supported_destination():
    pair = next(p for p in SITE_C_REASON_PAIRS
                if p.expected_reasons == ("NODE_NOT_IN_FROZEN_TREE",))
    verdict = _verdict_for(pair, node_exists=lambda *_a: False)
    outcome, reason, _ = transcribe(verdict, assessment=None)
    assert outcome == v.ABSTAIN
    assert reason == v.NO_SUPPORTED_DESTINATION


def test_an_outcome_outside_p8s_vocabulary_is_a_load_error():
    # P8's own record refuses the value at construction, so the only way to reach
    # `transcribe` with one is a stand-in -- which is exactly what a future caller
    # passing something verdict-shaped would be. Falling through to the abstention
    # branch would report an unknown outcome as a considered abstention.
    from llm_harness.records import MalformedVerdict

    with pytest.raises(MalformedVerdict):
        dataclasses.replace(_pre_call_budget_verdict(), outcome="probably_fine",
                            reasons=())

    class _NotAVerdict:
        outcome = "probably_fine"
        reasons = ()

    with pytest.raises(ValueError):
        transcribe(_NotAVerdict(), assessment=None)


def test_every_abstention_reason_transcribe_can_return_is_in_p11s_closed_set():
    for reason in (v.LOW_MARGIN, v.NO_SUPPORTED_DESTINATION, v.GENERIC_HUB_ONLY,
                   v.BUDGET_DEFERRED):
        assert reason in v.ABSTENTION_REASONS


# --- the model path ------------------------------------------------------------------

def test_the_model_path_refuses_rather_than_running_without_its_injections(indexed):
    with pytest.raises(ModelPathUnavailable):
        call_placement(indexed, request=None, gate=None, model_client=None,
                       prompt=None, call_dependencies=None,
                       observed_at=lambda: FIXED_CLOCK)


def test_the_model_path_names_every_injection_it_is_missing(indexed):
    with pytest.raises(ModelPathUnavailable) as raised:
        call_placement(indexed, request=object(), gate=object(),
                       model_client=None, prompt=None,
                       call_dependencies=object(),
                       observed_at=lambda: FIXED_CLOCK)
    assert "model_client" in str(raised.value)
    assert "prompt" in str(raised.value)


def test_call_placement_supplies_exactly_the_keywords_run_call_requires():
    required = {name for name, p in inspect.signature(run_call).parameters.items()
                if p.kind is p.KEYWORD_ONLY and p.default is p.empty}
    source = inspect.getsource(call_placement)
    call = next(node for node in ast.walk(ast.parse(source.strip()))
                if isinstance(node, ast.Call)
                and getattr(node.func, "id", None) == "run_call")
    assert {kw.arg for kw in call.keywords} == required


def test_p11_reuses_p8s_revalidation_rather_than_remapping_a_decision():
    # Done-means 16 and §8.8. P8 already appends a new verdict and supersedes the
    # old one when the plan or the snapshot changes.
    assert callable(revalidate_for_plan)
    assert callable(record_cd_verdict)
