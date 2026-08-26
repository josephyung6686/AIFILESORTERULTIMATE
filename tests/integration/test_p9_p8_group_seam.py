# tests/integration/test_p9_p8_group_seam.py
"""P9 -> P8 through the frozen public surface, with the live implementation.

The gate here is G-P8: recorded fixtures do not close this task. What is proved
is that P9's reference-only `DossierRequest` survives P7's release, P8's dossier
construction, P8's Site B validation and P8's verdict, and comes back as a P9
membership — without P9 having built a `Dossier`, called a gate, or run a
validator of its own.

The adversarial half matters more than the happy path. P8 rejects a member the
dossier did not carry, and P9 must map that rejection rather than write the
membership anyway.
"""
from __future__ import annotations

import inspect
import json
from decimal import Decimal

import pytest

import llm_harness
from database_agent.budget import set_ceiling
from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_observation, record_run
from grouping.p8_seam import GroupDecision, apply_p8_verdict, build_dossier_request
from grouping.records import AnchorFact, Group
from grouping.schema import create_grouping_schema
from grouping.store import memberships_for_group, record_group
from grouping.vocabulary import CANDIDATE, RULES, STRONGLY_IDENTIFIED_FILE
from llm_harness.records import P8Verdict
from llm_harness.schema import create_llm_schema
from privacy.release import ModelTarget

T0 = "2026-08-27T00:00:00Z"
GROUP = "fixture-course-group"
LOCAL = ModelTarget(locality="local", model_id="fixture", provider="fixture")


def test_p9_consumes_exactly_the_eight_frozen_p8_names():
    """The connection contract freezes P8's public surface at eight names. P9
    importing a ninth would be P9 reaching past the contract into P8's insides."""
    assert llm_harness.__all__ == [
        "run_call", "DossierRequest", "Dossier", "P8Verdict", "Refusal",
        "CallFailed", "ValidationUnavailable", "NeedsConsent",
    ]
    parameters = inspect.signature(llm_harness.run_call).parameters
    assert "gate" in parameters
    assert "model_client" in parameters


def test_p9_never_imports_run_calls_neighbours():
    """`run_call` is the only function that speaks to a model. P9 importing
    `issue`, a `ModelClient` or a `Gate` would be a second route to one."""
    import ast
    import pathlib

    import grouping

    root = pathlib.Path(grouping.__file__).resolve().parent
    offenders = []
    for path in sorted(root.glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.ImportFrom) and node.module in {
                "llm_harness.transport", "llm_harness.harness",
                "llm_harness.sites", "llm_harness.validation",
                "llm_harness.group_validation", "privacy.gate",
            }:
                offenders.append(f"{path.name}:{node.lineno}:{node.module}")
    assert offenders == [], offenders


@pytest.fixture()
def seam_conn(conn):
    from facts.fields import create_fields
    from privacy.schema import create_privacy_schema

    create_schema(conn)
    create_evidence_schema(conn)
    create_privacy_schema(conn)
    create_llm_schema(conn)
    create_grouping_schema(conn)
    create_fields(conn)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    return conn


def _group() -> Group:
    return Group(
        group_id=GROUP, seed_ref="seed-1", seed_kind=STRONGLY_IDENTIFIED_FILE,
        proposed_basis="PHYS1401 course materials",
        anchor_facts=(AnchorFact(
            field="subject", value="PHYS1401", file_ids=("lecture-08",),
            reliability_state="validated",
            observation_key="sha256:" + "e" * 64),),
        pre_model_signals={}, anchor_count=1, coherence_verdict=None,
        coherence_citations=(), group_category=None, display_label=None,
        label_source=None, conflicts=(), stop_rule_hits=(), state=CANDIDATE,
        sensitivity_state="none", dossier_id=None, llm_response_ref=None,
        validation_verdict_ref=None, created_by=RULES, created_at=T0)


def _request():
    from grouping.fixtures import course_dossier_fixture

    return build_dossier_request(
        course_dossier_fixture(),
        model_target=LOCAL,
        prompt_template_id="template.grouping",
        prompt_fingerprint="sha256:fp-group",
        max_dossier_tokens=4000,
    )


def test_the_request_p9_builds_is_accepted_by_p8s_own_record():
    """`DossierRequest.__post_init__` is P8's, and it refuses a request with no
    builder evidence metadata, a bad call site, or a missing subject."""
    request = _request()
    assert isinstance(request, llm_harness.DossierRequest)
    assert request.call_site == "B_group"
    assert request.subject_ref == GROUP
    assert request.plan_version is None


def test_site_b_rejects_a_member_the_dossier_did_not_carry(seam_conn):
    """P8's own Site B check, reached through P9's request. P9 writes nothing when
    P8 says the model invented a member -- and it does not look at the response
    bytes to find that out."""
    from llm_harness.group_validation import validate_group_response
    from llm_harness.vocabulary import INVENTED_MEMBERSHIP, REJECT

    from grouping.fixtures import course_dossier_fixture

    request = _request()
    response = json.dumps({"claims": [{
        "claim_ref": "coherence",
        "payload": {"coherent": True, "members": ["a-file-nobody-retrieved"]},
        "citations": [{
            "evidence_ref": request.evidence_items[-1].evidence_ref,
            "cited_span": "PHYS1401", "why_it_supports": "states the course",
        }],
    }]}).encode("utf-8")

    dossier = _materialise(request)
    verdicts, _report = validate_group_response(
        dossier, response,
        evidence_resolver=lambda key: "PHYS1401",
        contradicts=lambda *_a, **_k: False,
        model_id="fixture", prompt_fingerprint="sha256:fp-group",
        dossier_builder="P9", release_audit_id=17,
    )
    assert verdicts[0].outcome == REJECT
    assert INVENTED_MEMBERSHIP in verdicts[0].reasons

    record_group(seam_conn, _group())
    decision = apply_p8_verdict(
        seam_conn, group=_group(),
        dossier=course_dossier_fixture(),
        result=verdicts[0], plan_version_id="plan-2", created_at=T0)
    assert isinstance(decision, GroupDecision)
    assert memberships_for_group(seam_conn, GROUP) == ()


def _materialise(request):
    """P8's own dossier builder, over a release P7 would have granted.

    This is the one place a test stands in for the gate, and it stands in by
    calling P8's builder with a real `Released` -- not by constructing a `Dossier`,
    which is the thing P9 must never do and P8's one-writer guard enforces.
    """
    from llm_harness.dossier import build_dossier
    from llm_harness.vocabulary import REDUCTION_NONE
    from privacy.redaction import RedactionManifest
    from privacy.release import Released
    from privacy.resolve import Materialised

    released = Released(
        release_id="rel-1", audit_id=17, policy_version="policy-1",
        materialised_items=tuple(
            Materialised(
                observation_key=item.observation_key, span="0:8",
                value="PHYS1401", zone="heading", context_before=None,
                context_after=None, context_truncated=False, unit_length=64,
            )
            for item in request.model_call_request.requested_items
        ),
        redaction_manifest=RedactionManifest(entries=()),
        model_target=LOCAL,
    )
    dossier = build_dossier(
        request, released, reduction_rung=REDUCTION_NONE,
        allowed_vocabulary=("coherent",),
        prompt=_prompt(),
    )
    assert not isinstance(dossier, llm_harness.ValidationUnavailable), dossier
    return dossier


def _prompt():
    from llm_harness.records import PromptDefinition

    return PromptDefinition(
        template_id="template.grouping", template_bytes=b"TEMPLATE",
        response_schema_bytes=b'{"type":"object"}', call_site="B_group",
        call_site_version="1", shaping_policy_bytes=b'{"policy":"authored"}')


def test_a_grounded_group_verdict_becomes_a_p9_membership(seam_conn):
    """The whole seam: P9's references -> P8's dossier -> P8's Site B -> a P9
    membership, with no P9 validator anywhere in it."""
    from llm_harness.group_validation import validate_group_response
    from llm_harness.vocabulary import ACCEPT_DIRECT

    from grouping.fixtures import course_dossier_fixture

    request = _request()
    dossier = _materialise(request)
    members = [
        item.evidence_ref for item in dossier.evidence_items
        if item.kind == "member"
    ]
    response = json.dumps({"claims": [{
        "claim_ref": "coherence",
        "payload": {"coherent": True, "members": members},
        "citations": [{
            "evidence_ref": dossier.released_evidence[0].observation_key,
            "cited_span": "PHYS1401", "why_it_supports": "states the course",
        }],
    }]}).encode("utf-8")

    verdicts, report = validate_group_response(
        dossier, response,
        evidence_resolver=lambda key: "PHYS1401",
        contradicts=lambda *_a, **_k: False,
        model_id="fixture", prompt_fingerprint="sha256:fp-group",
        dossier_builder="P9", release_audit_id=17,
    )
    assert isinstance(verdicts[0], P8Verdict)
    assert verdicts[0].outcome == ACCEPT_DIRECT, verdicts[0].reasons

    record_group(seam_conn, _group())
    decision = apply_p8_verdict(
        seam_conn, group=_group(), dossier=course_dossier_fixture(),
        result=verdicts[0], plan_version_id="plan-2", created_at=T0)
    memberships = memberships_for_group(seam_conn, GROUP)
    assert memberships
    assert decision.membership_ids == tuple(
        item.membership_id for item in memberships)
    assert all(
        item.validation_verdict_ref == verdicts[0].verdict_id
        for item in memberships)
    assert report.claims_total == 1
