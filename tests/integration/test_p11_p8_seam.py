"""G-P8: P11's authorities against the real harness, end to end.

P8 ships, so this runs. It is the test that would fail if P11 ever grew a second
opinion about a Site C check, because it exercises P8's own recorded pairs
through P11's authorities rather than through P8's fixtures' own.
"""
from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

import json

from database_agent.db import create_schema
from database_agent.files_table import record_file
from llm_harness.budgets import ScanBudget, create_budget_schema
from llm_harness.fixtures import FIXTURE_HANDLE_KEY, SITE_C_OUTCOME_PAIRS
from llm_harness.harness import CallDependencies, run_call
from llm_harness.placement_validation import (
    record_cd_verdict, revalidate_for_plan, validate_placement_response,
)
from llm_harness.records import (
    DossierRequest, EvidenceItem, P8Verdict, PromptDefinition,
    ValidationUnavailable,
)
from llm_harness.transport import ModelClient
from llm_harness import CallFailed, NeedsConsent, Refusal
from llm_harness.schema import create_llm_schema
from llm_harness.vocabulary import C_PLACEMENT
from evidence_shape.schema import create_evidence_schema
from privacy.classification_store import ClassificationStore
from privacy.gate import Gate
from privacy.items import Excerpt, TextSpan
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from privacy.schema import create_privacy_schema
from privacy.release import ModelCallRequest, ModelTarget, Target

from placement.config import SupportPolicy
from placement.records import Destination
from placement.store import record_decision
from placement.versions import reproject
from placement.index import build_destination_index, legal_node_ids
from placement.p8_seam import (
    evidence_snapshot_id_for, placement_authorities, site_dependencies,
)
from placement.schema import create_placement_schema
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE, next_version
from p11.test_p11_records import _decision

POLICY = SupportPolicy(policy_id="integration-v1", support_scale_max=1.0,
                       minimum_support_threshold=0.0, margin_threshold=0.0)


@pytest.fixture()
def p11_conn(conn):
    # `tests/p11/conftest.py` is not on this directory's fixture path, so the
    # database is built here the way every other integration test builds its own.
    create_schema(conn)
    # P8's tables, because `record_cd_verdict` is a real write and a seam test
    # against an absent table would prove nothing about the seam.
    create_llm_schema(conn)
    create_budget_schema(conn)
    create_privacy_schema(conn)
    create_evidence_schema(conn)
    create_placement_schema(conn)
    return conn


@pytest.fixture()
def indexed(p11_conn):
    build_destination_index(p11_conn, FROZEN_TREE,
                            component_version="P11-integration",
                            observed_at=FIXED_CLOCK)
    return p11_conn


def _call_dependencies(conn, *, plan_version):
    return CallDependencies(
        proposal_class="placement", basis_key="f1->n-course",
        learning_scope="file", learning_subject_id="f1",
        evidence_resolver=lambda key: "span-1",
        site_dependencies=site_dependencies(placement=placement_authorities(
            conn, plan_version=plan_version, policy=POLICY,
            sensitivity_policy=lambda *_a, **_k: True)),
        contradicts=lambda *_a, **_k: False, unreduced_fits=True,
        summarized_fits=False, anchors_fit=False, split_shard_fits=(),
        split_shards=(),
        scan_budget=ScanBudget(scan_id="scan-p11", corpus_file_count=1000,
                               max_calls_per_1000_files=4,
                               max_estimated_cost=Decimal("10"),
                               min_calls_per_scan=0),
        estimated_cost=Decimal("1"), actual_cost=Decimal("1"),
        allowed_vocabulary=tuple(sorted(
            legal_node_ids(conn, plan_version=plan_version))),
        policy_version="policy-1", wire_handle_key=FIXTURE_HANDLE_KEY)


#: A real P7 release request. `DossierRequest` refuses anything else, which is
#: what makes this a binding against the live seam rather than a lookalike.
def _corpus_file(conn, directory):
    """A real P1 row. P7's gate resolves the target's content hashes from the
    files table, so a synthesized id would not reach the release at all."""
    directory.mkdir(parents=True, exist_ok=True)
    document = directory / "syllabus.pdf"
    document.write_bytes(b"%PDF-1.4 PHYS1401")
    return record_file(
        conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(directory), mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)


def _model_call_request(file_id="f1"):
    return ModelCallRequest(
        stage="placement", target=Target(file_ids=(file_id,)),
        model_target=ModelTarget(locality="local", model_id="llama-local",
                                 provider="on-device"),
        requested_items=(Excerpt(observation_key="obs-1",
                                 span=TextSpan(start=0, end=8),
                                 reason="anchor excerpt"),),
        prompt_template_id="template.placement",
        prompt_fingerprint="fp-canonical", max_dossier_tokens=4000)


#: Real injections. `run_call` type-checks the prompt and the model client, so
#: stand-ins would be rejected before P8 ever looked at the request -- and a test
#: that stopped there would prove nothing about the request P11 built.
def _prompt():
    return PromptDefinition(
        template_id="template.placement", template_bytes=b"TEMPLATE",
        response_schema_bytes=b'{"type":"object"}', call_site=C_PLACEMENT,
        call_site_version="1", shaping_policy_bytes=b'{"policy":"authored"}')


def _model_client():
    return ModelClient(
        model_target=ModelTarget(locality="local", model_id="llama-local",
                                 provider="on-device"),
        invoke=lambda payload: b'{"claims": []}')


def _policy(conn):
    """A real P7 policy in force. The gate refuses to invent one, which is the
    behaviour P11's own Task 10 carry depends on."""
    return set_policy(conn, Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode="hybrid",
        consent_grants=(), redaction_settings={},
        automatic_move_permissions={}, plan_version="plan-1",
        set_at=FIXED_CLOCK), component_version="P11-integration",
        user_id="joseph", reason="P11 P8-seam integration fixture")


def _gate(conn):
    """P7's real gate. P11 holds it and never calls `release` -- P8 does, inside
    `run_call`, which is the boundary this test exists to walk."""
    return Gate(
        conn, store=ClassificationStore(conn), plan_version="plan-1",
        classifier=lambda value, *, context_before=None, context_after=None: None,
        transform=lambda value, *, identifier_class: "[redacted]",
        unclassified_permits_local=False,
        scope_for=lambda file_id: "area-1", files_in_scope=lambda scope: (),
        component_version="P11-integration", now=lambda: FIXED_CLOCK,
        user_id="joseph")


def _request(*, evidence_snapshot_id, file_id="f1"):
    return DossierRequest(
        call_site=C_PLACEMENT, subject_ref=f"file:{file_id}:h1",
        eligibility_reason="several_legal_nodes_plausible",
        evidence_items=(EvidenceItem(
            evidence_ref="obs-1", kind="fact", location="page-1",
            excerpt_span=(0, 8), reliability_state="direct",
            basis="direct-anchor"),),
        conflicts=(), model_call_request=_model_call_request(file_id),
        plan_version="plan-1",
        evidence_snapshot_id=evidence_snapshot_id)


def test_a_c_verdict_binds_p11s_plan_version_and_snapshot(indexed):
    pair = SITE_C_OUTCOME_PAIRS[0]
    deps = placement_authorities(
        indexed, plan_version=pair.dossier.plan_version, policy=POLICY,
        sensitivity_policy=lambda *_a, **_k: True)
    result = validate_placement_response(
        pair.dossier, pair.response_bytes,
        evidence_resolver=lambda key: "span-1" if key.startswith("obs-") else None,
        contradicts=lambda *_a, **_k: False, dependencies=deps,
        model_id="fixture-model", prompt_fingerprint="fp-canonical",
        dossier_builder="p11-integration", release_audit_id=17, handle_key=FIXTURE_HANDLE_KEY)
    verdict = result[0][0]
    assert isinstance(verdict, P8Verdict)
    record_cd_verdict(
        indexed, verdict, evidence_snapshot_id=pair.evidence_snapshot_id,
        model_id="fixture-model", prompt_fingerprint="fp-canonical",
        release_audit_id=17, observed_at=FIXED_CLOCK)
    identity = indexed.execute(
        "SELECT plan_version, evidence_snapshot_id FROM llm_cd_plan_identity "
        "WHERE verdict_id = ?", (verdict.verdict_id,)).fetchone()
    assert identity["plan_version"] == pair.dossier.plan_version


def test_p11s_authorities_reach_the_real_run_call(indexed):
    """The seam bound end to end rather than by reference.

    `run_call` refuses a C request with no `evidence_snapshot_id` BEFORE the
    spend, so this drives P11's real bundle through P8's real entry point and
    lands on P8's own pre-call refusal. Nothing about it is a spy: the arguments
    are the ones `run_call` declares, and P8 is the one that answered.
    """
    from placement.p8_seam import call_placement

    result = call_placement(
        indexed, _request(evidence_snapshot_id=None),
        gate=_gate(indexed), model_client=_model_client(), prompt=_prompt(),
        call_dependencies=_call_dependencies(indexed, plan_version="plan-1"),
        observed_at=lambda: FIXED_CLOCK)
    assert isinstance(result, ValidationUnavailable)
    assert "evidence_snapshot_id" in result.missing


def test_the_snapshot_p11_mints_satisfies_p8s_pre_call_check(indexed, tmp_path):
    from placement.p8_seam import call_placement

    _policy(indexed)
    file_id = _corpus_file(indexed, tmp_path / "corpus")
    minted = evidence_snapshot_id_for(plan_version="plan-1",
                                      observation_keys=("obs-1",))
    result = call_placement(
        indexed, _request(evidence_snapshot_id=minted, file_id=file_id),
        gate=_gate(indexed), model_client=_model_client(), prompt=_prompt(),
        call_dependencies=_call_dependencies(indexed, plan_version="plan-1"),
        observed_at=lambda: FIXED_CLOCK)
    # The snapshot check is behind us: `run_call` went on to the eligibility,
    # reduction and release steps and came back with one of the five types it
    # declares. P7's gate refuses this unclassified fixture, which is P7's answer
    # and not P11's -- the point is that P11's bundle reached it.
    assert "evidence_snapshot_id" not in getattr(result, "missing", ())
    # It went the whole way: eligibility, reduction, and then P7's own
    # `Gate.release`, which refused an unclassified file in §8.4's own words.
    # That refusal is P7's answer, arrived at through P8, using P11's bundle --
    # and it is the same rule `placement.privacy` carries on the deterministic
    # side, reached here from the opposite direction.
    assert isinstance(result, Refusal), result
    assert result.denied.reason == "unclassified"


def _stored_verdict(conn, pair):
    """A real P8 verdict in the table, produced by P8's own validator.

    `revalidate_for_plan` raises `KeyError` on a `previous_verdict_id` that is not
    in `llm_verdict`, so a synthesized id would never reach the revalidation at
    all and the test would prove nothing about the seam.
    """
    deps = placement_authorities(
        conn, plan_version=pair.dossier.plan_version, policy=POLICY,
        sensitivity_policy=lambda *_a, **_k: True)
    result = validate_placement_response(
        pair.dossier, pair.response_bytes,
        evidence_resolver=lambda key: "span-1" if key.startswith("obs-") else None,
        contradicts=lambda *_a, **_k: False, dependencies=deps,
        model_id="fixture-model", prompt_fingerprint="fp-canonical",
        dossier_builder="p11-integration", release_audit_id=17, handle_key=FIXTURE_HANDLE_KEY)
    verdict = result[0][0]
    return record_cd_verdict(
        conn, verdict, evidence_snapshot_id=pair.evidence_snapshot_id,
        model_id="fixture-model", prompt_fingerprint="fp-canonical",
        release_audit_id=17, observed_at=FIXED_CLOCK)


def _revalidation_inputs(pair, conn, *, verdict_id, plan_version):
    """Exactly the keywords `revalidate_for_plan` declares, and no others.

    P11 stores no `verdict_id`, dossier or response bytes -- `PlacementDecision`'s
    thirty fields carry none of them -- so they arrive from the caller that made
    the call. Binding them here is what proves the injected mapping is the live
    signature's and not a shape P11 invented.
    """
    return {
        "previous_verdict_id": verdict_id,
        "dossier": pair.dossier,
        "response_bytes": pair.response_bytes,
        "evidence_resolver": lambda key: ("span-1" if key.startswith("obs-")
                                          else None),
        "contradicts": lambda *_a, **_k: False,
        "dependencies": placement_authorities(
            conn, plan_version=plan_version, policy=POLICY,
            sensitivity_policy=lambda *_a, **_k: True),
        "model_id": "fixture-model",
        "prompt_fingerprint": "fp-canonical",
        "dossier_builder": "p11-integration",
        "release_audit_id": 17,
        "observed_at": FIXED_CLOCK,
    }


def _v2_tree(*, rename_course_to=None):
    """plan-2, minted P10's way: every node gets a new id, lineage in origin."""
    tree = next_version(plan_version_id="plan-2", suffix="@2")
    if rename_course_to is None:
        return tree
    old_id = next(node.node_id for node in tree.nodes
                  if node.origin_node_id == "n-course")
    nodes = tuple(replace(node, node_id=rename_course_to)
                  if node.node_id == old_id else node for node in tree.nodes)
    profiles = tuple(replace(profile, node_id=rename_course_to)
                     if profile.node_id == old_id else profile
                     for profile in tree.profiles)
    return replace(
        tree, nodes=nodes, profiles=profiles,
        freeze_record=replace(
            tree.freeze_record,
            node_ids=tuple(node.node_id for node in nodes),
            legal_destination_ids=frozenset(
                node.node_id for node in nodes if node.accepts_placement)))


def _place_d1(conn):
    record_decision(
        conn, _decision(decision_id="d1",
                        destination=Destination(node_id="n-course",
                                                node_role="ordinary")),
        component_version="P11-integration", observed_at=FIXED_CLOCK)


def test_p11_reuses_p8s_revalidation_rather_than_remapping_a_decision(indexed):
    # Done-means 16 and §8.8, driven end to end rather than by reference. P8
    # already appends a new verdict and supersedes the old one when the plan or
    # the snapshot changes; P11 calling this is what keeps "never silently
    # reclassify" true at the verdict layer too. The node here SURVIVES -- P10
    # minted it a new id and `reproject` followed the lineage -- so the only
    # remaining question is whether the model's judgement about it still holds,
    # and P8 is the one that answers.
    pair = SITE_C_OUTCOME_PAIRS[0]
    assert pair.expected_outcome == "accept_direct"
    verdict_id = _stored_verdict(indexed, pair)
    _place_d1(indexed)
    node_id = pair.dossier.allowed_vocabulary[0]
    build_destination_index(indexed, _v2_tree(rename_course_to=node_id),
                            component_version="P11-integration",
                            observed_at=FIXED_CLOCK)
    before = indexed.execute(
        "SELECT count(*) AS c FROM llm_verdict").fetchone()["c"]
    diff = reproject(
        indexed, from_plan_version="plan-1", to_plan_version="plan-2",
        revalidation_inputs={"d1": _revalidation_inputs(
            pair, indexed, verdict_id=verdict_id, plan_version="plan-2")})
    assert diff.carried_unchanged == ("d1",)
    assert diff.requiring_renewed_review == ()
    # P8 really ran: it wrote the fresh verdict itself, stamped with the new plan
    # version. P11 records no verdict of its own, so a second row here would be
    # P11 writing P8's fact twice.
    after = indexed.execute(
        "SELECT plan_version FROM llm_verdict WHERE verdict_id = ?",
        (f"{verdict_id}::plan-2::" + evidence_snapshot_id_for(
            plan_version="plan-2", observation_keys=("obs-1",)),)).fetchone()
    assert after["plan_version"] == "plan-2"
    assert indexed.execute(
        "SELECT count(*) AS c FROM llm_verdict").fetchone()["c"] == before + 1


def test_a_surviving_node_whose_verdict_no_longer_holds_goes_back_to_the_user(
        indexed):
    # The negative twin, and the half that makes the test above discriminating.
    # The lineage check passes identically -- `n-course` still has a successor in
    # plan-2 -- but the destination the model named is not in the new legal set,
    # so P8's own NODE_NOT_IN_FROZEN_TREE fires and the decision is marked rather
    # than carried. A `_revalidates` that returned True unconditionally would pass
    # the test above and fail here.
    pair = SITE_C_OUTCOME_PAIRS[0]
    verdict_id = _stored_verdict(indexed, pair)
    _place_d1(indexed)
    build_destination_index(indexed, _v2_tree(),
                            component_version="P11-integration",
                            observed_at=FIXED_CLOCK)
    assert pair.dossier.allowed_vocabulary[0] not in legal_node_ids(
        indexed, plan_version="plan-2")
    diff = reproject(
        indexed, from_plan_version="plan-1", to_plan_version="plan-2",
        revalidation_inputs={"d1": _revalidation_inputs(
            pair, indexed, verdict_id=verdict_id, plan_version="plan-2")})
    assert diff.requiring_renewed_review == ("d1",)
    assert diff.carried_unchanged == ()
    # Marked, not remapped: the plan-1 row is untouched and nothing names the
    # surviving lookalike.
    row = indexed.execute(
        "SELECT node_id, superseded_by FROM placement_decisions "
        "WHERE record_id = 'd1'").fetchone()
    assert (row["node_id"], row["superseded_by"]) == ("n-course", None)


def test_a_decision_with_no_model_verdict_needs_no_revalidation(indexed):
    # `revalidation_inputs` is SPARSE on purpose: a deterministic decision has no
    # P8 verdict, so there is nothing to re-validate and the node's survival is
    # the whole question. An empty mapping must not read as "every verdict
    # failed", which would send a clean corpus back to the user wholesale.
    _place_d1(indexed)
    build_destination_index(indexed, _v2_tree(),
                            component_version="P11-integration",
                            observed_at=FIXED_CLOCK)
    diff = reproject(indexed, from_plan_version="plan-1",
                     to_plan_version="plan-2")
    assert diff.carried_unchanged == ("d1",)
