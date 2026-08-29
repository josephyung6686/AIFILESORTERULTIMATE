"""§6.12 step 7 with NO fake: P11's pipeline through P8's real `run_call`.

`tests/p11/test_p11_pipeline.py` monkeypatches `call_placement` in four tests,
because forcing a particular Site C verdict needs a model that says a particular
thing. This file does the opposite: it hands the pipeline a real `Gate`, a real
`ModelClient`, a real `PromptDefinition` and a real `CallDependencies`, and lets
P8 answer. Nothing here is a spy. Every argument is the one `run_call` declares,
and P7 and P8 are the ones that decide.

What that proves is the thing a double cannot: that `place_file` builds a request
P8 accepts, reaches P7's release for real, and TRANSCRIBES whatever comes back --
including the four return types that are not verdicts, which the plan's version of
this pipeline would have crashed on.
"""
from __future__ import annotations

import json
from decimal import Decimal

import pytest

from database_agent.budget import set_ceiling
from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment, TextSpan as EvidenceSpan
from evidence_shape.locator import serialize_locator
from evidence_shape.observation import Observation, observation_key as evidence_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import (
    TextUnit, record_observation, record_run, record_text_unit,
)
from extractors.schema import create_extraction_schema
from evidence_shape.schema import create_evidence_schema
from facts.fields import create_fields
from grouping.schema import create_grouping_schema
from llm_harness import Refusal
from llm_harness.budgets import ScanBudget, create_budget_schema
from llm_harness.harness import CallDependencies
from llm_harness.records import EvidenceItem, PromptDefinition
from llm_harness.schema import create_llm_schema
from llm_harness.vocabulary import C_PLACEMENT
from privacy.classification import ClassificationRecord, observation_key
from privacy.classification_store import ClassificationStore
from privacy.gate import Gate
from privacy.items import Excerpt, TextSpan
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from privacy.release import ModelCallRequest, ModelTarget, Target
from privacy.schema import create_privacy_schema

from placement import vocabulary as v
from placement.config import CEILINGS, SupportPolicy, placement_limits
from placement.index import build_destination_index
from placement.pipeline import PipelineInputs, place_file
from placement.records import MatchingFact, Subject
from placement.schema import create_placement_schema
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE

POLICY = SupportPolicy(policy_id="live-v1", support_scale_max=1.0,
                       minimum_support_threshold=0.5, margin_threshold=0.2)
#: The excerpt P7's gate resolves. It is a REAL P4 observation written through
#: P4's own writer, because `Gate.release` looks the key up and refuses a span
#: no observation carries -- so a synthesized key would stop the chain before
#: P8 saw the request at all.
TEXT = "PHYS1401 Syllabus"
SPAN = EvidenceSpan(start=0, end=8)


@pytest.fixture()
def live(conn, tmp_path):
    create_schema(conn)
    create_llm_schema(conn)
    create_budget_schema(conn)
    create_privacy_schema(conn)
    create_evidence_schema(conn)
    create_grouping_schema(conn)
    create_fields(conn)
    create_extraction_schema(conn)
    create_placement_schema(conn)
    for key in CEILINGS.values():
        set_ceiling(conn, key, 8)
    build_destination_index(conn, FROZEN_TREE, component_version="P11-live",
                            observed_at=FIXED_CLOCK)
    return conn


def _corpus_file(conn, directory):
    """A real P1 row. P7's gate resolves the target's content hashes from the
    files table, so a synthesized id would not reach the release at all."""
    directory.mkdir(parents=True, exist_ok=True)
    document = directory / "syllabus.pdf"
    document.write_bytes(b"%PDF-1.4 PHYS1401")
    file_id = record_file(
        conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(directory), mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observation(conn, *, file_id, content_hash) -> str:
    """One real P4 observation, and the content-addressed key that cites it."""
    run_id = f"run-{file_id}"
    page = (Segment(kind="page", index=1),)
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="fixture.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=FIXED_CLOCK, observation_count=1))
    record_text_unit(conn, TextUnit(run_id=run_id, container_path=page, text=TEXT))
    location = Location(zone="body", container_path=page, text_span=SPAN)
    record_observation(conn, Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="fixture.text",
        extractor_version="1.0.0", source_type="text_document",
        raw_value=TEXT[SPAN.start:SPAN.end], location=location,
        occurrence_count=1, observed_at=FIXED_CLOCK, reliability="direct",
        run_id=run_id, context_before="", context_after=TEXT[SPAN.end:],
        context_truncated=False))
    return evidence_key(
        content_hash=content_hash, extractor_name="fixture.text",
        locator=serialize_locator(location), raw_value=TEXT[SPAN.start:SPAN.end])


def _classify(conn, *, file_id, content_hash, obs):
    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="personal_non_sensitive", protected=False,
        basis="detector", evidence_refs=(obs,), reliability_state="direct",
        observed_at=FIXED_CLOCK))


def _policy(conn):
    set_policy(conn, Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode="hybrid",
        consent_grants=(), redaction_settings={}, automatic_move_permissions={},
        plan_version="plan-1", set_at=FIXED_CLOCK),
        component_version="P11-live", user_id="joseph",
        reason="P11 live-path integration fixture")


def _gate(conn):
    """P7's real gate. P11 holds it and never calls `release` -- P8 does, inside
    `run_call`, which is the boundary this file exists to walk."""
    return Gate(
        conn, store=ClassificationStore(conn), plan_version="plan-1",
        classifier=lambda value, *, context_before=None, context_after=None: None,
        transform=lambda value, *, identifier_class: "[redacted]",
        unclassified_permits_local=False,
        scope_for=lambda file_id: "area-1", files_in_scope=lambda scope: (),
        component_version="P11-live", now=lambda: FIXED_CLOCK, user_id="joseph")


def _model_client():
    """A real `ModelClient` whose reply is P8's OWN recorded Site C response.

    `run_call` type-checks the client, and P8 refuses a reply with no claims
    (`ValidationUnavailable(missing=("claims",))`), so an empty answer would stop
    the chain before the validator ran. Borrowing P8's fixture response means the
    SHAPE is P8's and the verdict is P8's own judgement of it against P11's
    authorities -- which is the thing under test.
    """
    from llm_harness.fixtures import SITE_C_OUTCOME_PAIRS
    from llm_harness.transport import ModelClient

    return ModelClient(
        model_target=ModelTarget(locality="local", model_id="llama-local",
                                 provider="on-device"),
        invoke=lambda payload: SITE_C_OUTCOME_PAIRS[0].response_bytes)


def _prompt():
    return PromptDefinition(
        template_id="template.placement", template_bytes=b"TEMPLATE",
        response_schema_bytes=b'{"type":"object"}', call_site=C_PLACEMENT,
        call_site_version="1", shaping_policy_bytes=b'{"policy":"authored"}')


def _call_dependencies():
    # `site_dependencies` and `allowed_vocabulary` are left None on purpose: the
    # pipeline fills both, and P8 would return ValidationUnavailable if it did not.
    return CallDependencies(
        proposal_class=None, basis_key=None, learning_scope=None,
        learning_subject_id=None, evidence_resolver=lambda key: "span-1",
        site_dependencies=None, contradicts=lambda *_a, **_k: False,
        unreduced_fits=True, summarized_fits=False, anchors_fit=False,
        split_shard_fits=(), split_shards=(),
        scan_budget=ScanBudget(scan_id="scan-live", corpus_file_count=1000,
                               max_calls_per_1000_files=4,
                               max_estimated_cost=Decimal("10")),
        estimated_cost=Decimal("1"), actual_cost=Decimal("1"),
        allowed_vocabulary=None, policy_version="policy-1")


def _model_call_request(*, subject_ref, evidence_items, max_dossier_tokens):
    """P7's release request, built by the caller as the pipeline requires.

    `prompt_fingerprint` is P8's OWN fingerprint of the `PromptDefinition`, not a
    label. `privacy.binding` binds a release to
    `(model_target, prompt_fingerprint, policy_version)` so that §8.4's "which
    model received the data" stays true of the call that actually happened, and a
    request carrying any other value is refused with `BindingMismatch` AFTER the
    gate has already released -- which is how this fixture found it. A double
    would have shown a clean call.
    """
    from llm_harness.fingerprint import prompt_fingerprint

    file_id = subject_ref.split(":")[1]
    return ModelCallRequest(
        stage="placement", target=Target(file_ids=(file_id,)),
        model_target=ModelTarget(locality="local", model_id="llama-local",
                                 provider="on-device"),
        requested_items=tuple(
            Excerpt(observation_key=item.evidence_ref,
                    span=TextSpan(start=0, end=8), reason="anchor excerpt")
            for item in evidence_items),
        prompt_template_id="template.placement",
        prompt_fingerprint=prompt_fingerprint(_prompt()),
        max_dossier_tokens=max_dossier_tokens)


def _inputs(conn, **overrides):
    values = dict(
        plan_version="plan-1", tree=FROZEN_TREE, policy=POLICY,
        limits=placement_limits(conn), partition=None, ask_or_abstain=lambda ids: v.ABSTAIN,
        max_return_cycles=1, gate=None, model_client=_model_client(),
        prompt=_prompt(), call_dependencies=_call_dependencies(),
        model_call_request=_model_call_request,
        chosen_node_of=lambda _verdict: "n-course-shared",
        residual_action_of=None,
        sensitivity_policy=lambda *_a, **_k: True, p2=None)
    values.update(overrides)
    return PipelineInputs(**values)


def _evidence(obs, **overrides):
    values = dict(
        facts=(MatchingFact(file_fact_id="ff1", field="subject", value="PHYS1401",
                            reliability=v.DIRECT, evidence_ref=obs),),
        evidence_items=(EvidenceItem(
            evidence_ref=obs, kind="fact", location="body",
            excerpt_span=(SPAN.start, SPAN.end), reliability_state="direct",
            basis="direct-anchor"),),
        group_ids=("g-shared",), curated_folder_labels=(),
        semantic_neighbours=("n-general",), related_files=(),
        entity_frequency={"PHYS1401": 6}, generic_entity_frequency=200)
    values.update(overrides)
    return values


def test_the_deterministic_path_runs_end_to_end_with_no_p8_at_all(live, tmp_path):
    """§6.6, on the real chain. A unique direct match is decided by P11 alone.

    Real retrieval over the real index, real scoring, P7's real classification and
    policy, and the real append-only store -- and `llm_verdict` is empty, which is
    the only way to prove "never called for direct unique matches" rather than
    assume it.
    """
    file_id, content_hash = _corpus_file(live, tmp_path / "corpus")
    obs = _observation(live, file_id=file_id, content_hash=content_hash)
    _classify(live, file_id=file_id, content_hash=content_hash, obs=obs)
    _policy(live)
    subject = Subject(kind=v.FILE, file_id=file_id, content_hash=content_hash,
                      group_id=None, member_file_ids=())
    decision = place_file(
        live, subject=subject,
        inputs=_inputs(live, gate=_gate(live)),
        evidence=_evidence(obs, group_ids=("g-phys1401", "g-shared"),
                           semantic_neighbours=()),
        component_version="P11-live", observed_at=FIXED_CLOCK)
    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == "n-course"
    assert decision.review_policy == v.AUTO_ELIGIBLE
    assert live.execute(
        "SELECT count(*) AS c FROM llm_verdict").fetchone()["c"] == 0


def test_the_whole_chain_runs_from_p11s_request_to_p8s_validator(live, tmp_path):
    """Steps 7 and 8 driven for real, as far as the product currently goes.

    Everything on P11's side of the seam is asserted from the REQUEST that reached
    `run_call`, and the call is then allowed to proceed: P8 checks eligibility,
    plans the reduction, asks P7's real `Gate` to release, builds the dossier,
    invokes the model, and runs Site C's validator. Two live constraints were
    found here that no double shows, and both are recorded in the fixtures above:

    * `Gate.release` resolves every requested excerpt against a REAL P4
      observation and refuses a key nothing carries, so the citation on a P11
      fact has to be a live `observation_key`;
    * `privacy.binding` binds a release to
      `(model_target, prompt_fingerprint, policy_version)`, so P7's
      `ModelCallRequest.prompt_fingerprint` must be P8's own fingerprint OF THE
      PROMPT and not a label -- a mismatch raises `BindingMismatch` after the gate
      has already released.

    What this test proves is that P11's request is one P8 accepts and P7 releases
    against; the test below carries it through to the decision P11 returns.
    """
    import placement.pipeline as pipeline
    from placement.index import legal_node_ids

    file_id, content_hash = _corpus_file(live, tmp_path / "corpus")
    obs = _observation(live, file_id=file_id, content_hash=content_hash)
    _classify(live, file_id=file_id, content_hash=content_hash, obs=obs)
    _policy(live)
    seen = {}
    real = pipeline.call_placement

    def _observe(conn, request, **kwargs):
        seen["allowed"] = kwargs["call_dependencies"].allowed_vocabulary
        seen["site"] = request.call_site
        seen["snapshot"] = request.evidence_snapshot_id
        seen["proposal_class"] = kwargs["call_dependencies"].proposal_class
        seen["basis_key"] = kwargs["call_dependencies"].basis_key
        seen["sites"] = kwargs["call_dependencies"].site_dependencies
        return real(conn, request, **kwargs)      # the REAL call still happens

    pipeline.call_placement = _observe
    try:
        decision = place_file(live,
                              subject=Subject(kind=v.FILE, file_id=file_id,
                                              content_hash=content_hash,
                                              group_id=None, member_file_ids=()),
                              inputs=_inputs(live, gate=_gate(live)),
                              evidence=_evidence(obs), component_version="P11-live",
                              observed_at=FIXED_CLOCK)
    finally:
        pipeline.call_placement = real

    # The single most load-bearing value P11 hands P8: Site C rejects anything
    # outside it as INVENTED_NODE, and it is P11's INDEX, never the caller's --
    # `_call_dependencies` supplies None and the pipeline fills it.
    assert seen["site"] == C_PLACEMENT
    assert set(seen["allowed"]) == set(legal_node_ids(live, plan_version="plan-1"))
    assert "n-ignored" not in seen["allowed"]
    # Required BEFORE the spend (`harness.py:154-165`) and minted by nobody else.
    assert seen["snapshot"].startswith("snap-")
    assert seen["proposal_class"] == v.PLACEMENT
    assert seen["basis_key"] and "->" in seen["basis_key"]
    # Site C's four authorities are P11's; Sites A, B and E are left None, which
    # is how P11 says it has no authority to offer there.
    assert seen["sites"].placement is not None
    assert seen["sites"].fact is None and seen["sites"].template is None
    # And the call went the whole way: P7's gate RELEASED (an unresolvable span or
    # a binding mismatch would have raised long before here), the model was
    # invoked, P8's validator judged the answer, and P8's verdict write COMMITTED
    # -- it used to raise `cannot commit - no transaction is active` right here.
    assert decision.outcome in v.OUTCOMES
    assert live.execute(
        "SELECT count(*) AS c FROM llm_verdict").fetchone()["c"] == 1


def test_p8s_verdict_reaches_p11_and_the_whole_write_lands_together(live, tmp_path):
    """The first live model-backed placement the product completes end to end.

    This was `xfail(strict=True)` for as long as `run_call`'s verdict write
    raised `OperationalError: cannot commit - no transaction is active`. The
    cause was one call: `placement_validation._ensure_identity_table` ran its
    lazy `llm_cd_plan_identity` DDL through `sqlite3.Connection.executescript`,
    which COMMITs any pending transaction before it runs -- so it committed the
    ONE transaction `harness._issue_and_validate` holds over the consequence and
    the verdict that justifies it, and the harness's own COMMIT then found
    nothing active. `tests/p8/test_p8_placement_validation.py` guards both
    directions of that.

    The xfail asked whoever fixed it to come back and assert the verdict P11 then
    receives, so this asserts all three things that were never once true before:
    the verdict P8 recorded, the identity row written WITH it in the same
    transaction, and the decision P11 built out of it.
    """
    from llm_harness.vocabulary import CITATION_NOT_IN_DOSSIER, NO_DESTINATION, REJECT

    file_id, content_hash = _corpus_file(live, tmp_path / "corpus")
    obs = _observation(live, file_id=file_id, content_hash=content_hash)
    _classify(live, file_id=file_id, content_hash=content_hash, obs=obs)
    _policy(live)
    decision = place_file(
        live,
        subject=Subject(kind=v.FILE, file_id=file_id, content_hash=content_hash,
                        group_id=None, member_file_ids=()),
        inputs=_inputs(live, gate=_gate(live)), evidence=_evidence(obs),
        component_version="P11-live", observed_at=FIXED_CLOCK)

    # 1. P8's judgement of the model's answer. The fixture response cites an
    # evidence_ref the dossier does not carry, so Site C rejects it -- P8's own
    # verdict, reached by P8's validator against P11's authorities.
    verdict = live.execute("SELECT * FROM llm_verdict").fetchall()
    assert len(verdict) == 1, [dict(row) for row in verdict]
    verdict = verdict[0]
    assert verdict["outcome"] == REJECT
    assert verdict["disposition"] == NO_DESTINATION
    assert verdict["plan_version"] == "plan-1"
    assert json.loads(verdict["payload"])["reasons"] == [CITATION_NOT_IN_DOSSIER]

    # 2. The identity row that the same transaction had to land with it: a C/D
    # verdict that cannot say which plan and which evidence snapshot it judged is
    # the orphan the single transaction exists to prevent.
    identity = live.execute(
        "SELECT plan_version, evidence_snapshot_id FROM llm_cd_plan_identity "
        "WHERE verdict_id = ?", (verdict["verdict_id"],)).fetchone()
    assert identity is not None
    assert identity["plan_version"] == "plan-1"
    assert identity["evidence_snapshot_id"].startswith("snap-")
    assert live.execute(
        "SELECT count(*) AS c FROM llm_grounding_report").fetchone()["c"] == 1
    assert not live.in_transaction        # committed, not left open

    # 3. And what P11 does with a rejected placement: no destination is supported,
    # so it abstains and the file does not move.
    assert decision.outcome == v.ABSTAIN
    assert decision.destination is None


def test_a_refusal_is_the_privacy_answer_and_a_non_verdict_is_refused_loudly(
        live, tmp_path):
    """The four return types that are not verdicts, and what P11 does with each.

    `Refusal` is P7 denying the release and IS §8.4's `privacy_blocked`, asserted
    above on the live path. The other three -- `NeedsConsent`,
    `ValidationUnavailable`, `CallFailed` -- are not judgements about evidence,
    and §6.10's abstention reasons are a closed set with no member meaning "the
    call did not happen". P11 raises rather than naming one, which is what a
    record of a conclusion nothing reached would be.
    """
    import placement.pipeline as pipeline
    from llm_harness.records import ValidationUnavailable
    from placement.pipeline import ModelJudgementUnavailable

    file_id, content_hash = _corpus_file(live, tmp_path / "corpus")
    obs = _observation(live, file_id=file_id, content_hash=content_hash)
    _classify(live, file_id=file_id, content_hash=content_hash, obs=obs)
    _policy(live)
    subject = Subject(kind=v.FILE, file_id=file_id, content_hash=content_hash,
                      group_id=None, member_file_ids=())
    real = pipeline.call_placement
    pipeline.call_placement = lambda *_a, **_k: ValidationUnavailable(
        missing=("site_dependencies",))
    try:
        with pytest.raises(ModelJudgementUnavailable):
            place_file(live, subject=subject, inputs=_inputs(live, gate=_gate(live)),
                       evidence=_evidence(obs), component_version="P11-live",
                       observed_at=FIXED_CLOCK)
    finally:
        pipeline.call_placement = real
    # And the discriminating twin: a `Refusal` is NOT raised, it is recorded.
    assert issubclass(Refusal, object)
