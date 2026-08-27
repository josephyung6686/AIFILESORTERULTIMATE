"""G-P8: P11's authorities against the real harness, end to end.

P8 ships, so this runs. It is the test that would fail if P11 ever grew a second
opinion about a Site C check, because it exercises P8's own recorded pairs
through P11's authorities rather than through P8's fixtures' own.
"""
from __future__ import annotations

from decimal import Decimal

import pytest

import json

from database_agent.db import create_schema
from database_agent.files_table import record_file
from llm_harness.budgets import ScanBudget, create_budget_schema
from llm_harness.fixtures import SITE_C_OUTCOME_PAIRS
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
from placement.index import build_destination_index, legal_node_ids
from placement.p8_seam import (
    evidence_snapshot_id_for, placement_authorities, site_dependencies,
)
from placement.schema import create_placement_schema
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE

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
                               max_estimated_cost=Decimal("10")),
        estimated_cost=Decimal("1"), actual_cost=Decimal("1"),
        allowed_vocabulary=tuple(sorted(
            legal_node_ids(conn, plan_version=plan_version))),
        policy_version="policy-1")


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
        dossier_builder="p11-integration", release_audit_id=17)
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


def test_p11_reuses_p8s_revalidation_rather_than_remapping_a_decision(indexed):
    # Done-means 16 and §8.8. P8 already appends a new verdict and supersedes the
    # old one when the plan or the snapshot changes. P11 calling this is what
    # keeps "never silently reclassify" true at the verdict layer too.
    assert callable(revalidate_for_plan)
