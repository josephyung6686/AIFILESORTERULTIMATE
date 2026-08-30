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
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_observation, record_run, record_text_unit
from evidence_shape.text_units import TextUnit
from extractors.schema import create_extraction_schema
from grouping.p8_seam import GroupDecision, apply_p8_verdict, build_dossier_request
from grouping.records import AnchorFact, Group
from grouping.schema import create_grouping_schema
from grouping.store import memberships_for_group, record_group
from grouping.vocabulary import CANDIDATE, RULES, STRONGLY_IDENTIFIED_FILE
from llm_harness.budgets import create_budget_schema
from llm_harness.records import P8Verdict
from llm_harness.schema import create_llm_schema
from privacy.classification_store import ClassificationStore
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
    # P7's gate reads P5's sensitivity signals for every file it is asked to
    # release, so the live path needs P5's tables even though P9 writes none.
    create_extraction_schema(conn)
    create_llm_schema(conn)
    # P8's budget tables are Task 4's and are created separately from
    # `create_llm_schema` (`budgets.py:142`: "Call after `create_llm_schema`").
    # `run_call` reserves against them before it invokes, so the live path needs
    # them; the recorded-fixture half of this file never reached that far.
    create_budget_schema(conn)
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
    from privacy.release import Released, ReleasedItem

    released = Released(
        release_id="rel-1", audit_id=17, policy_version="policy-1",
        materialised_items=tuple(
            ReleasedItem(
                observation_key=item.observation_key, span="0:8",
                value="PHYS1401", zone="heading", unit_length=64,
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


# --- P9 supplies `run_call`'s real dependencies ----------------------------------


#: The bundle fields that are NOT `run_call` keywords, each with its consumer.
#: `model_target` is P7's: it goes into `ModelCallRequest.model_target`, which the
#: gate reads `.locality` off to decide whether bytes may leave the machine. The
#: exception is ENUMERATED rather than the equality below being relaxed, so a
#: seventh field cannot join the bundle without appearing here first.
NOT_RUN_CALL_KEYWORDS = {"model_target"}


def test_the_authorities_bundle_matches_run_calls_real_signature():
    """`pipeline.py` called `p8_run_call(conn, request)`. Live `run_call` has five
    required keyword-only arguments, so the first real call was a `TypeError` --
    invisible because every P9 test injected `None` or a `**kwargs` spy."""
    import dataclasses

    from grouping.pipeline import ModelCallAuthorities

    keyword_only = {
        name for name, p in inspect.signature(llm_harness.run_call).parameters.items()
        if p.kind is inspect.Parameter.KEYWORD_ONLY
    }
    fields = {f.name for f in dataclasses.fields(ModelCallAuthorities)}
    forwarded = fields - NOT_RUN_CALL_KEYWORDS
    assert forwarded == keyword_only, forwarded ^ keyword_only
    # Both directions: a named exception that stops being a field is as much a
    # drift as a field that stops being named.
    assert NOT_RUN_CALL_KEYWORDS <= fields, NOT_RUN_CALL_KEYWORDS - fields

    sentinel = object()
    inspect.signature(llm_harness.run_call).bind(
        sentinel, sentinel, **{name: sentinel for name in forwarded})


def test_the_bundle_is_forwarded_to_run_call_under_its_own_names(
    seam_conn, live_group,
):
    """The bundle existing is not the fix; the call site reading it is. This
    asserts the five values arrive at `run_call` under `run_call`'s own keywords,
    which is the half a signature test cannot see."""
    from grouping.pipeline import ModelCallAuthorities, group_subject

    seen = {}

    def spy(conn, request, **kwargs):
        seen.update(kwargs)
        return None

    bundle = ModelCallAuthorities(
        gate="the-gate", model_client="the-client", prompt="the-prompt",
        validation_dependencies="the-deps", observed_at="the-clock",
        model_target=LOCAL)
    live_group(seam_conn, p8_run_call=spy, p8_authorities=bundle)

    # Exactly the five, and `model_target` is NOT among them: it belongs to the
    # request P7 gates, not to the call P8 makes, and forwarding it here would be
    # an unexpected keyword on the real `run_call`.
    assert seen == {
        "gate": "the-gate", "model_client": "the-client", "prompt": "the-prompt",
        "validation_dependencies": "the-deps", "observed_at": "the-clock",
    }


def test_a_run_call_without_authorities_fails_closed(seam_conn, live_group):
    """`planning/30-p8-p9-connection-contract.md:86`: "missing P8/config -> fail
    closed". A missing bundle is missing config, not an exception, and it must not
    reach `run_call` with five arguments short."""
    from grouping.pipeline import NO_MODEL_CONFIGURED

    result = live_group(
        seam_conn, p8_run_call=llm_harness.run_call, p8_authorities=None)

    assert result.not_implemented_reason == NO_MODEL_CONFIGURED
    assert result.model_result is None


# --- the live path: `group_subject` -> the real `run_call` -> a real verdict ------

CORPUS_VALUE = "PHYS1401"
PLAN_VERSION = "plan-2"


def _live_file(conn, tmp_path, name, *, run_id):
    """One scanned file with one direct P6 fact, through P1/P4/P6's own writers."""
    from facts.file_facts import write_fact
    from facts.values import ensure_value

    body = f"{CORPUS_VALUE} {name}".encode()
    path = tmp_path / name
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=".pdf", observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Coursework", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=T0, finished_at=T0))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document",
        raw_value=CORPUS_VALUE,
        # The span is the whole raw value. `build_dossier_request` asks P7 for
        # `TextSpan(0, len(excerpt.text))`, and P7 refuses a requested span that
        # disagrees with the live location -- correctly. A location with no span
        # cannot be released at all.
        location=Location(
            "heading", (Segment("field", label="heading"),),
            text_span=TextSpan(0, len(CORPUS_VALUE))),
        occurrence_count=1, observed_at=T0, reliability="direct", run_id=run_id)
    record_observation(conn, observation)
    # D12's addressable unit. P7 takes the released substring OUT of this, and
    # refuses outright when a span points at no unit -- "the whole file is not a
    # fallback" (`privacy/resolve.py:201`). P5 emits these in production.
    # Longer than the requested span on purpose: §8.4 refuses a release whose span
    # covers the WHOLE unit ("whole_document_requested"), so a unit equal to the
    # value would make every P9 group call unreleasable.
    record_text_unit(conn, TextUnit(
        run_id=run_id, container_path=observation.location.container_path,
        text=f"{CORPUS_VALUE} {name}"))
    value_id = ensure_value(
        conn, field_key="subject", canonical_value=CORPUS_VALUE,
        first_evidence_ref=observation.observation_key, origin="automatic")
    write_fact(
        conn, file_id=file_id, content_hash=content_hash, field_key="subject",
        value_id=value_id, reliability_state="validated",
        origin="deterministic_extractor",
        evidence_refs=(observation.observation_key,),
        cache_key=f"sha256:{file_id}-subject", active=True)
    # P7's gate reads classifications from its OWN store, not from P9's injected
    # `classification_store`. Without a row here every file resolves to
    # `unreadable_unclassified` and §8.4 refuses the call before any egress --
    # which is correct behaviour, and would have made this test prove nothing
    # about the seam. Written through P7's real writer, so it is not a double.
    ClassificationStore(conn).write(_classification(file_id, content_hash))
    return file_id, content_hash, observation.observation_key


def _classification(file_id, content_hash):
    from privacy.classification import ClassificationRecord

    return ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="public_low", protected=False, basis="detector",
        evidence_refs=("sha256:" + "a" * 64,), reliability_state="direct",
        observed_at=T0)


def _live_limits():
    from grouping.config import GroupingLimits

    return GroupingLimits(
        max_retrieved_neighbors=50, max_graph_nodes=10, max_candidate_members=10,
        max_dossier_tokens=4000, generic_hub_frequency=9,
        minimum_independent_anchors=1, max_excerpt_characters=240)


def _live_knowledge():
    """P9's own injected authorities.

    `embedding_identity` is `None`, which is the honest value with `EmbeddingsOff`:
    retrieval channel 6 is the only consumer (`grouping/retrieval.py:307`, `:350`)
    and it does not run. It briefly held a real `ModelTarget` here, because
    `pipeline.py` passed this retrieval field straight through as
    `build_dossier_request(model_target=...)` and the gate reads `.locality` off
    that. The model target now comes from `ModelCallAuthorities`, so the
    workaround is gone rather than left in place.
    """
    from grouping.pipeline import GroupingKnowledge
    from grouping.retrieval import RetrievalKnowledge

    return GroupingKnowledge(
        retrieval=RetrievalKnowledge(
            document_compatible=None, channel_weights={}, similarity=None,
            similarity_threshold=None, embedding_identity=None, domain=None),
        active_schema_for=lambda c, f, h: ("subject",),
        signal_evaluator_for=lambda domain: True,
        classification_store=_classification,
        conflicts_for=lambda files: (),
        duplicate_or_version=None,
    )


@pytest.fixture()
def live_group(tmp_path):
    """`group_subject` over a real corpus, with only its injected authorities."""
    from grouping.embeddings import EmbeddingsOff
    from grouping.pipeline import group_subject

    state = {}

    def run(conn, *, p8_run_call, p8_authorities, knowledge=None):
        if "file_id" not in state:
            file_id, content_hash, key = _live_file(
                conn, tmp_path, "Syllabus.pdf", run_id="r-seed")
            state.update(file_id=file_id, content_hash=content_hash, key=key)
        return group_subject(
            conn, file_id=state["file_id"], content_hash=state["content_hash"],
            plan_version_id=PLAN_VERSION, limits=_live_limits(),
            knowledge=knowledge or _live_knowledge(),
            user_seed_for=lambda f, h: None,
            p8_run_call=p8_run_call, p8_authorities=p8_authorities,
            embeddings=EmbeddingsOff(), created_at=T0)

    run.state = state
    return run


def _live_gate(conn):
    from privacy.gate import Gate

    return Gate(
        conn,
        store=ClassificationStore(conn),
        plan_version=PLAN_VERSION,
        # Classifies nothing, so P7 releases the span unredacted and the model's
        # citation can name it. A redacting fixture would be testing P7's
        # redaction, which is P7's own test's job.
        classifier=lambda value, *, context_before=None, context_after=None: None,
        transform=lambda value, *, identifier_class: "[redacted]",
        unclassified_permits_local=False,
        scope_for=lambda file_id: "area-1",
        files_in_scope=lambda scope: (),
        component_version="p9-seam",
        now=lambda: T0,
        user_id="joseph",
    )


def _live_policy(conn):
    from privacy.policy import Policy, UNSET_POLICY_VERSION, set_policy

    draft = Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode="hybrid",
        consent_grants=(),
        redaction_settings={"names": "redacted", "previews": "redacted",
                            "thumbnails": "redacted", "ocr_text": "redacted",
                            "location_data": "redacted"},
        automatic_move_permissions={}, plan_version=PLAN_VERSION, set_at=T0)
    version = set_policy(
        conn, draft, component_version="p9-seam", user_id="joseph",
        reason="p9 seam fixture")
    return version


def _live_dependencies(policy_version, key):
    from decimal import Decimal

    from llm_harness.budgets import ScanBudget
    from llm_harness.harness import CallDependencies
    from llm_harness.sites import SiteDependencies

    return CallDependencies(
        proposal_class="group-coherence",
        basis_key=json.dumps({"field_key": "subject", "value": CORPUS_VALUE}),
        learning_scope="group",
        learning_subject_id=GROUP,
        evidence_resolver=lambda observation_key: (
            CORPUS_VALUE if observation_key == key else None),
        # Site B needs no bundle -- the connection contract's own words.
        site_dependencies=SiteDependencies(
            fact=None, placement=None, residual=None, template=None),
        contradicts=lambda *_a, **_k: False,
        unreduced_fits=True,
        summarized_fits=False,
        anchors_fit=False,
        split_shard_fits=(),
        split_shards=(),
        scan_budget=ScanBudget(
            scan_id="scan-p9", corpus_file_count=1000,
            max_calls_per_1000_files=4, max_estimated_cost=Decimal("10"),
            min_calls_per_scan=0),
        estimated_cost=Decimal("1"),
        actual_cost=Decimal("1"),
        allowed_vocabulary=("coherent",),
        policy_version=policy_version,
    )


def test_the_pipeline_reaches_the_real_run_call(seam_conn, live_group):
    """The whole point of the repair. `group_subject` drives the REAL `run_call`
    -- no spy, no wrapper supplying the arguments on P9's behalf -- and comes back
    with a `GroupDecision`. Before the bundle existed this raised
    `TypeError: run_call() missing 5 required keyword-only arguments`."""
    from llm_harness.transport import ModelClient

    from grouping.pipeline import ModelCallAuthorities

    policy_version = _live_policy(seam_conn)
    # Seed the corpus before the gate is built, so the classification is there.
    live_group(seam_conn, p8_run_call=None, p8_authorities=None)
    key = live_group.state["key"]
    file_id = live_group.state["file_id"]

    sent = []

    def invoke(payload: bytes) -> bytes:
        sent.append(payload)
        return json.dumps({"claims": [{
            "claim_ref": "coherence",
            "payload": {"coherent": True, "members": [file_id]},
            "citations": [{
                "evidence_ref": key, "cited_span": CORPUS_VALUE,
                "why_it_supports": "states the course",
            }],
        }]}).encode("utf-8")

    result = live_group(
        seam_conn,
        p8_run_call=llm_harness.run_call,
        p8_authorities=ModelCallAuthorities(
            gate=_live_gate(seam_conn),
            model_client=ModelClient(model_target=LOCAL, invoke=invoke),
            prompt=_prompt(),
            validation_dependencies=_live_dependencies(policy_version, key),
            observed_at=lambda: T0,
            model_target=LOCAL,
        ))

    assert result.not_implemented_reason is None, result.not_implemented_reason
    assert isinstance(result.model_result, GroupDecision), result.model_result
    assert len(sent) == 1, "P8 called the model exactly once"
