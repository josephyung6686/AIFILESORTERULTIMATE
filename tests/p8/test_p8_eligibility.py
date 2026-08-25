"""Closed eligibility, unique-match refusal, and P1 learning suppression."""
from __future__ import annotations

import ast
import dataclasses
import inspect
from pathlib import Path

import pytest

import llm_harness
from database_agent.events import append_event
from database_agent.learning import learning_records, reset_preferences
from llm_harness.eligibility import (
    Eligible,
    assess_call,
    not_reserved_for_llm,
    suppressed_by_learning,
)
from llm_harness.records import (
    DossierRequest,
    PreCallAbstention,
    ValidationUnavailable,
)
from llm_harness.vocabulary import (
    A_FACT,
    ALL_ELIGIBILITY,
    B_GROUP,
    C_PLACEMENT,
    COHERENCE_JUDGEMENT,
    D_RESIDUAL,
    E_TEMPLATE,
    ELIGIBILITY_BY_SITE,
    FACT_ELIGIBILITY,
    GROUP_ELIGIBILITY,
    NOT_ELIGIBLE_FOR_MODEL,
    PLACEMENT_ELIGIBILITY,
    REJECT,
    REMAINS_AMBIGUOUS,
    RESIDUAL_ELIGIBILITY,
    SITES_REQUIRING_PLAN_VERSION,
    TEMPLATE_ELIGIBILITY,
    USER_REJECTED_EQUIVALENT,
)
from privacy.items import CandidateLabel
from privacy.release import ModelCallRequest, ModelTarget, Target

CLOCK = "2026-08-25T12:00:00+00:00"
PROPOSAL_CLASS = "fixture-class"
BASIS_KEY = '{"file_id":"file-1","field_key":"subject","value_id":"v-1"}'
SRC_ELIGIBILITY = Path(__file__).resolve().parents[2] / "src" / "llm_harness" / "eligibility.py"

CLOSED_CASES = tuple(
    (site, reason)
    for site, reasons in ELIGIBILITY_BY_SITE.items()
    for reason in reasons
)


def _model_call_request() -> ModelCallRequest:
    return ModelCallRequest(
        stage="grouping",
        target=Target(file_ids=("file-1",)),
        model_target=ModelTarget(
            locality="local", model_id="fixture-model", provider="fixture",
        ),
        requested_items=(CandidateLabel(label="Passport"),),
        prompt_template_id="template.grouping",
        prompt_fingerprint="fingerprint.grouping",
        max_dossier_tokens=4000,
    )


def _request(call_site: str, eligibility_reason: str, *,
             subject_ref: str = "file-1") -> DossierRequest:
    plan_version = "plan-1" if call_site in SITES_REQUIRING_PLAN_VERSION else None
    return DossierRequest(
        call_site=call_site,
        subject_ref=subject_ref,
        eligibility_reason=eligibility_reason,
        evidence_refs=("obs-key-1",),
        model_call_request=_model_call_request(),
        plan_version=plan_version,
        evidence_snapshot_id="snap-1",
        budget_context="scan-1",
    )


def _unchecked_request(*, call_site: str, eligibility_reason: str,
                       subject_ref: str = "file-1") -> DossierRequest:
    """Bypass construction guards so assess_call can see a mismatched reason."""
    request = object.__new__(DossierRequest)
    object.__setattr__(request, "call_site", call_site)
    object.__setattr__(request, "subject_ref", subject_ref)
    object.__setattr__(request, "eligibility_reason", eligibility_reason)
    object.__setattr__(request, "evidence_refs", ("obs-key-1",))
    object.__setattr__(request, "model_call_request", _model_call_request())
    object.__setattr__(request, "plan_version", None)
    object.__setattr__(request, "evidence_snapshot_id", "snap-1")
    object.__setattr__(request, "budget_context", "scan-1")
    return request


def _seed_correction(conn, *, polarity: str, proposal_class: str = PROPOSAL_CLASS,
                     basis_key: str = BASIS_KEY, scope: str = "file",
                     subject: str = "file-1", user_id: str | None = "user-1") -> int:
    fields = dict(
        event_type="fact rejection",
        subsystem="P8-fixture",
        component_version="0.0.0",
        observed_at=CLOCK,
        explanation="fixture correction",
        correction_scope=scope,
        correction_subject=subject,
        polarity=polarity,
        proposal_class=proposal_class,
        basis_key=basis_key,
    )
    if user_id is not None:
        fields["user_id"] = user_id
    return append_event(conn, **fields)


def _assess(request: DossierRequest, conn, *,
            scope: str | None = "file",
            subject_id: str | None = "file-1",
            proposal_class: str | None = PROPOSAL_CLASS,
            basis_key: str | None = BASIS_KEY):
    return assess_call(
        request,
        conn=conn,
        learning_scope=scope,
        learning_subject_id=subject_id,
        proposal_class=proposal_class,
        basis_key=basis_key,
    )


def test_eligibility_helpers_are_not_on_the_task_1_public_surface():
    assert llm_harness.__all__ == [
        "run_call",
        "Dossier",
        "P8Verdict",
        "Refusal",
        "ValidationUnavailable",
        "NeedsConsent",
    ]
    assert "Eligible" not in llm_harness.__all__
    assert "assess_call" not in llm_harness.__all__
    assert not hasattr(llm_harness, "assess_call")


def test_eligible_is_a_frozen_marker():
    assert dataclasses.is_dataclass(Eligible)
    assert Eligible.__dataclass_params__.frozen
    assert hasattr(Eligible, "__slots__")
    assert Eligible() == Eligible()


def test_assess_call_signature_is_keyword_only_after_the_request():
    parameters = inspect.signature(assess_call).parameters
    assert tuple(parameters)[:4] == (
        "request", "conn", "learning_scope", "learning_subject_id",
    )
    assert parameters["conn"].kind is inspect.Parameter.KEYWORD_ONLY
    assert "proposal_class" in parameters
    assert "basis_key" in parameters
    for name in (
        "conn", "learning_scope", "learning_subject_id", "proposal_class", "basis_key",
    ):
        assert parameters[name].default is inspect.Parameter.empty, name


def test_closed_eligibility_reasons_are_imported_from_p8_vocabulary_not_injected():
    assert FACT_ELIGIBILITY + GROUP_ELIGIBILITY + PLACEMENT_ELIGIBILITY + (
        RESIDUAL_ELIGIBILITY + TEMPLATE_ELIGIBILITY
    ) == ALL_ELIGIBILITY
    assert set(ELIGIBILITY_BY_SITE) == {A_FACT, B_GROUP, C_PLACEMENT, D_RESIDUAL, E_TEMPLATE}
    source = inspect.getsource(assess_call)
    assert "ELIGIBILITY_BY_SITE" in source
    assert "eligibility_reasons=" not in source


@pytest.mark.parametrize("call_site,reason", CLOSED_CASES)
def test_every_closed_eligibility_reason_is_eligible_when_unsuppressed(
    p8_conn, call_site, reason,
):
    result = _assess(_request(call_site, reason), p8_conn)
    assert isinstance(result, Eligible)


def test_a_reason_from_another_site_is_not_eligible_for_model(p8_conn):
    request = _unchecked_request(
        call_site=A_FACT, eligibility_reason=COHERENCE_JUDGEMENT,
    )
    result = _assess(request, p8_conn)
    assert isinstance(result, PreCallAbstention)
    assert result.reason == NOT_ELIGIBLE_FOR_MODEL
    assert result.call_site == A_FACT
    assert result.subject_ref == "file-1"


def test_an_unknown_eligibility_reason_is_not_eligible_for_model(p8_conn):
    request = _unchecked_request(
        call_site=A_FACT, eligibility_reason="direct_unique_match",
    )
    result = _assess(request, p8_conn)
    assert isinstance(result, PreCallAbstention)
    assert result.reason == NOT_ELIGIBLE_FOR_MODEL


def test_a_unique_match_is_not_reserved_for_llm_before_gate_access():
    abstention = not_reserved_for_llm(call_site=A_FACT, subject_ref="file-1")
    assert isinstance(abstention, PreCallAbstention)
    assert abstention.reason == NOT_ELIGIBLE_FOR_MODEL
    assert abstention.call_site == A_FACT
    assert abstention.subject_ref == "file-1"
    source = inspect.getsource(not_reserved_for_llm)
    assert "Gate" not in source
    assert "release" not in source


def test_omitting_conn_returns_validation_unavailable(p8_conn):
    result = assess_call(
        _request(A_FACT, REMAINS_AMBIGUOUS),
        conn=None,
        learning_scope="file",
        learning_subject_id="file-1",
        proposal_class=PROPOSAL_CLASS,
        basis_key=BASIS_KEY,
    )
    assert isinstance(result, ValidationUnavailable)
    assert "conn" in result.missing


@pytest.mark.parametrize("scope,subject", (
    (None, "file-1"),
    ("file", None),
    ("", "file-1"),
    ("file", ""),
))
def test_omitting_scope_or_subject_identity_returns_validation_unavailable(
    p8_conn, scope, subject,
):
    result = assess_call(
        _request(A_FACT, REMAINS_AMBIGUOUS),
        conn=p8_conn,
        learning_scope=scope,
        learning_subject_id=subject,
        proposal_class=PROPOSAL_CLASS,
        basis_key=BASIS_KEY,
    )
    assert isinstance(result, ValidationUnavailable)
    assert result.missing


def test_omitting_proposal_identity_returns_validation_unavailable(p8_conn):
    result = assess_call(
        _request(A_FACT, REMAINS_AMBIGUOUS),
        conn=p8_conn,
        learning_scope="file",
        learning_subject_id="file-1",
        proposal_class=None,
        basis_key=BASIS_KEY,
    )
    assert isinstance(result, ValidationUnavailable)
    assert "proposal_class" in result.missing


def test_an_empty_store_does_not_suppress(p8_conn):
    assert suppressed_by_learning(
        p8_conn, scope="file", subject_id="file-1",
        proposal_class=PROPOSAL_CLASS, basis_key=BASIS_KEY,
    ) is False
    result = _assess(_request(A_FACT, REMAINS_AMBIGUOUS), p8_conn)
    assert isinstance(result, Eligible)


def test_a_current_reject_of_the_same_equivalent_is_suppressed(p8_conn):
    _seed_correction(p8_conn, polarity=REJECT)
    assert suppressed_by_learning(
        p8_conn, scope="file", subject_id="file-1",
        proposal_class=PROPOSAL_CLASS, basis_key=BASIS_KEY,
    ) is True
    result = _assess(_request(A_FACT, REMAINS_AMBIGUOUS), p8_conn)
    assert isinstance(result, PreCallAbstention)
    assert result.reason == USER_REJECTED_EQUIVALENT
    assert result.call_site == A_FACT
    assert result.subject_ref == "file-1"


def test_an_accept_is_not_a_suppression(p8_conn):
    _seed_correction(p8_conn, polarity="accept")
    assert suppressed_by_learning(
        p8_conn, scope="file", subject_id="file-1",
        proposal_class=PROPOSAL_CLASS, basis_key=BASIS_KEY,
    ) is False
    assert isinstance(_assess(_request(A_FACT, REMAINS_AMBIGUOUS), p8_conn), Eligible)


def test_a_different_proposal_class_is_not_this_parts_rejection(p8_conn):
    _seed_correction(p8_conn, polarity=REJECT, proposal_class="placement")
    assert suppressed_by_learning(
        p8_conn, scope="file", subject_id="file-1",
        proposal_class=PROPOSAL_CLASS, basis_key=BASIS_KEY,
    ) is False


def test_a_different_basis_key_is_a_different_equivalent(p8_conn):
    _seed_correction(p8_conn, polarity=REJECT)
    assert suppressed_by_learning(
        p8_conn, scope="file", subject_id="file-1",
        proposal_class=PROPOSAL_CLASS, basis_key='{"other":true}',
    ) is False


def test_a_row_without_user_id_is_ignored_by_learning_records(p8_conn):
    _seed_correction(p8_conn, polarity=REJECT, user_id=None)
    assert learning_records(p8_conn, "file", "file-1") == []
    assert suppressed_by_learning(
        p8_conn, scope="file", subject_id="file-1",
        proposal_class=PROPOSAL_CLASS, basis_key=BASIS_KEY,
    ) is False


def test_a_reset_cutoff_clears_the_suppression(p8_conn):
    _seed_correction(p8_conn, polarity=REJECT)
    reset_preferences(
        p8_conn, "file", "file-1",
        author="P13", component_version="0.0.0", user_id="user-1",
    )
    assert learning_records(p8_conn, "file", "file-1") == []
    assert suppressed_by_learning(
        p8_conn, scope="file", subject_id="file-1",
        proposal_class=PROPOSAL_CLASS, basis_key=BASIS_KEY,
    ) is False
    assert isinstance(_assess(_request(A_FACT, REMAINS_AMBIGUOUS), p8_conn), Eligible)


def test_suppression_is_a_narrow_adapter_over_p1_learning_records():
    source = inspect.getsource(suppressed_by_learning)
    assert "learning_records" in source
    assert "SELECT" not in source
    assert "learning_resets" not in source
    assert "facts.learning" not in source


def test_eligibility_module_does_not_invent_p6_oracles_or_a_second_store():
    tree = ast.parse(SRC_ELIGIBILITY.read_text())
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    assert "facts.learning" not in imported
    assert "facts" not in imported
    assert "database_agent.learning" in imported
    source = SRC_ELIGIBILITY.read_text()
    assert "def normalize(" not in source
    assert "def contradicts(" not in source
    assert "CREATE TABLE" not in source
