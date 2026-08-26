# tests/p9/test_p9_membership.py
"""P9 Task 10 — P9 maps P8's verdict. It does not re-decide it.

P8 owns the only function that speaks to a model and the only validator that says
whether the model's answer held. P9's job at this seam is a mapping: an
authoritative outcome in, a membership and an acceptance obligation out. Every
check P8 already ran — invented member, citation grounding, contradiction, schema
— is absent here on purpose, and a test reads this package's imports to prove it.

The rule that costs the most if it is wrong: an `accept_context_supported`
membership and its `pending-review` acceptance row are written in ONE transaction.
A context-supported member is a file the model was not sure about; making it
visible without the review obligation that makes it safe is how an uncertain
guess becomes a silent decision.

SR5 is mapped here and nowhere earlier. It means P8 could not explain the group
with valid citations, and only P8's returned reasons can say that.
"""
from __future__ import annotations

import pytest

from grouping.acceptance import (
    AcceptanceStateAbsent,
    membership_review_state_as_of,
)
from grouping.p8_seam import (
    DossierDeferred,
    GroupDecision,
    apply_p8_verdict,
    build_dossier_request,
)
from grouping.records import AnchorFact, Group
from grouping.schema import create_grouping_schema
from grouping.store import memberships_for_group, record_group
from grouping.vocabulary import (
    CANDIDATE,
    CONTEXT_SUPPORTED,
    DIRECT_ANCHOR,
    INTERPRETATION,
    LLM,
    NO_GROUP,
    PENDING_REVIEW,
    RULES,
    SR5,
    STRONGLY_IDENTIFIED_FILE,
    UNCERTAIN,
    VALIDATION,
)
from llm_harness.records import CallFailed, P8Verdict, Refusal, ValidationUnavailable
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    CITATION_NOT_IN_DOSSIER,
    CONTEXT_SUPPORTED_MEMBERSHIP,
    DIRECT_MEMBERSHIP,
    REJECT,
    REJECTED,
    WEAK,
)

T0 = "2026-08-27T00:00:00Z"
GROUP = "fixture-course-group"
PLAN = "plan-2"
KEY = "sha256:" + "d" * 64


@pytest.fixture()
def seam_conn(conn):
    from database_agent.db import create_schema

    create_schema(conn)
    create_grouping_schema(conn)
    return conn


def _group(**overrides) -> Group:
    values = dict(
        group_id=GROUP, seed_ref="seed-1", seed_kind=STRONGLY_IDENTIFIED_FILE,
        proposed_basis="subject=PHYS1401",
        anchor_facts=(AnchorFact(
            field="subject", value="PHYS1401", file_ids=("file-1",),
            reliability_state="validated", observation_key=KEY),),
        pre_model_signals={}, anchor_count=1, coherence_verdict=None,
        coherence_citations=(), group_category=None, display_label=None,
        label_source=None, conflicts=(), stop_rule_hits=(), state=CANDIDATE,
        sensitivity_state="none", dossier_id=None, llm_response_ref=None,
        validation_verdict_ref=None, created_by=RULES, created_at=T0,
    )
    values.update(overrides)
    return Group(**values)


def _dossier():
    from grouping.fixtures import course_dossier_fixture

    return course_dossier_fixture()


def _verdict(outcome=ACCEPT_DIRECT, **overrides) -> P8Verdict:
    disposition = {
        ACCEPT_DIRECT: DIRECT_MEMBERSHIP,
        ACCEPT_CONTEXT_SUPPORTED: CONTEXT_SUPPORTED_MEMBERSHIP,
        WEAK: "possible",
        REJECT: REJECTED,
        ABSTAIN: ABSTAIN,
    }[outcome]
    values = dict(
        verdict_id="verdict-1", dossier_id="dossier-1", claim_ref="claim-1",
        outcome=outcome, disposition=disposition, reasons=(),
        may_propose=outcome in (ACCEPT_DIRECT, ACCEPT_CONTEXT_SUPPORTED),
        requires_review=outcome == ACCEPT_CONTEXT_SUPPORTED,
        citations_checked=(), scope="group", validator_version="P8/0.1.0",
        policy_version="policy-1", plan_version=None,
    )
    values.update(overrides)
    return P8Verdict(**values)


def _apply(conn, result, *, group=None, dossier=None, plan_version_id=PLAN):
    return apply_p8_verdict(
        conn, group=group or _group(), dossier=dossier or _dossier(),
        result=result, plan_version_id=plan_version_id, created_at=T0,
    )


def _request(dossier):
    """P9 supplies neither the model target nor the prompt; both are P8's, chosen
    by the caller that owns the run."""
    from privacy.release import ModelTarget

    return build_dossier_request(
        dossier,
        model_target=ModelTarget(
            locality="local", model_id="fixture", provider="fixture"),
        prompt_template_id="template.grouping",
        prompt_fingerprint="sha256:fp",
        max_dossier_tokens=4000,
    )


# --- P9 converts references and never materialises ------------------------------


def test_the_request_is_reference_only_and_is_not_a_p8_dossier():
    from llm_harness.records import DossierRequest

    request = _request(_dossier())
    assert isinstance(request, DossierRequest)
    assert request.subject_ref == GROUP
    assert request.evidence_items
    assert all(item.evidence_ref for item in request.evidence_items)
    for item in request.model_call_request.requested_items:
        assert hasattr(item, "observation_key")


def test_every_dossier_member_arrives_as_a_member_kind_reference():
    """Site B rejects a member the dossier did not carry as `kind == "member"`.
    A candidate P9 sends as an excerpt reference is a member P8 will call
    invented."""
    dossier = _dossier()
    request = _request(dossier)
    members = {
        item.evidence_ref for item in request.evidence_items
        if item.kind == "member"
    }
    expected = {
        item.file_id for item in (*dossier.anchor_files, *dossier.candidate_files)
    }
    assert members == expected


def test_p9_imports_no_gate_no_transport_and_no_materialised_dossier():
    import ast
    import pathlib

    import grouping

    root = pathlib.Path(grouping.__file__).resolve().parent
    banned_modules = {"privacy.gate", "privacy.binding", "privacy.resolve"}
    banned_names = {"Dossier", "ModelClient", "issue", "Gate", "Verdict"}
    offenders = []
    for path in sorted(root.glob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module in banned_modules:
                    offenders.append(f"{path.name}:{node.lineno}:{node.module}")
                for alias in node.names:
                    if alias.name in banned_names:
                        offenders.append(f"{path.name}:{node.lineno}:{alias.name}")
    assert offenders == [], offenders

    # And nothing compares or computes with a token count.
    for node in ast.walk(tree):
        if isinstance(node, (ast.Compare, ast.BinOp)):
            for inner in ast.walk(node):
                if isinstance(inner, ast.Name) and "token" in inner.id.lower():
                    offenders.append(f"{node.lineno}:{inner.id}")
                if isinstance(inner, ast.Attribute) and "token" in inner.attr.lower():
                    offenders.append(f"{node.lineno}:{inner.attr}")
    assert offenders == [], offenders


# --- accept_direct ---------------------------------------------------------------


def test_accept_direct_writes_an_included_direct_anchor_membership(seam_conn):
    record_group(seam_conn, _group())
    decision = _apply(seam_conn, _verdict(ACCEPT_DIRECT))
    assert isinstance(decision, GroupDecision)
    memberships = memberships_for_group(seam_conn, GROUP)
    assert memberships
    assert all(item.basis == DIRECT_ANCHOR for item in memberships)
    assert all(item.decision_source == LLM for item in memberships)
    assert decision.stop_rule_outcome is None


def test_accept_direct_needs_no_review_obligation(seam_conn):
    record_group(seam_conn, _group())
    _apply(seam_conn, _verdict(ACCEPT_DIRECT))
    membership = memberships_for_group(seam_conn, GROUP)[0]
    with pytest.raises(AcceptanceStateAbsent):
        membership_review_state_as_of(
            seam_conn, membership_id=membership.membership_id,
            plan_version_id=PLAN)


# --- accept_context_supported: membership and obligation, or neither -------------


def test_a_context_membership_and_its_review_obligation_land_together(seam_conn):
    record_group(seam_conn, _group())
    _apply(seam_conn, _verdict(ACCEPT_CONTEXT_SUPPORTED))
    memberships = memberships_for_group(seam_conn, GROUP)
    assert memberships
    for membership in memberships:
        assert membership.basis == CONTEXT_SUPPORTED
        assert membership.decision == UNCERTAIN
        assert membership_review_state_as_of(
            seam_conn, membership_id=membership.membership_id,
            plan_version_id=PLAN) == PENDING_REVIEW


def test_a_context_membership_without_a_plan_version_writes_nothing(seam_conn):
    """The obligation is per plan version. Without one there is nowhere to record
    the review, and a membership visible without its review is the failure."""
    record_group(seam_conn, _group())
    with pytest.raises(ValueError) as excinfo:
        _apply(seam_conn, _verdict(ACCEPT_CONTEXT_SUPPORTED), plan_version_id=None)
    # The record would refuse a blank `plan_version_id` too, and the transaction
    # would roll the membership back -- but only after writing it, and with a
    # message about a missing field rather than about a missing review.
    assert "plan version" in str(excinfo.value)
    assert "review" in str(excinfo.value)
    assert memberships_for_group(seam_conn, GROUP) == ()


def test_a_failed_acceptance_write_leaves_no_membership_behind(seam_conn, monkeypatch):
    """One transaction. A membership that became visible while its review
    obligation failed to record is an uncertain guess wearing a decision."""
    import grouping.p8_seam as seam

    record_group(seam_conn, _group())

    def boom(*_a, **_k):
        raise RuntimeError("the acceptance write failed")

    monkeypatch.setattr(seam, "record_context_review_pending", boom)
    with pytest.raises(RuntimeError):
        _apply(seam_conn, _verdict(ACCEPT_CONTEXT_SUPPORTED))
    assert memberships_for_group(seam_conn, GROUP) == ()


# --- everything else cannot make a supported group -------------------------------


@pytest.mark.parametrize("outcome", [WEAK, REJECT, ABSTAIN])
def test_a_non_accepting_outcome_creates_no_membership(seam_conn, outcome):
    record_group(seam_conn, _group())
    decision = _apply(seam_conn, _verdict(outcome))
    assert memberships_for_group(seam_conn, GROUP) == ()
    assert decision.group_state != "supported"


def test_a_may_propose_false_verdict_is_refused_even_if_it_says_accept(seam_conn):
    """`may_propose` is P8's own answer to "may this become a proposal". A verdict
    whose outcome and flag disagree is not one P9 resolves in the model's favour.
    """
    record_group(seam_conn, _group())
    with pytest.raises(ValueError):
        _apply(seam_conn, _verdict(ACCEPT_DIRECT, may_propose=False))
    assert memberships_for_group(seam_conn, GROUP) == ()


def test_a_refusal_records_a_validation_failure_and_no_membership(seam_conn):
    from privacy.denial import RemedyOption
    from privacy.release import Denied

    record_group(seam_conn, _group())
    decision = _apply(seam_conn, Refusal(
        denied=Denied(
            reason="unclassified", explanation="no classification is stored",
            remedy_options=(RemedyOption(action="classify", detail="classify first"),),
            evidence_refs=(KEY,)),
        validator_version="P8/0.1.0", policy_version="policy-1"))
    assert memberships_for_group(seam_conn, GROUP) == ()
    assert decision.failure_stage == VALIDATION


def test_a_call_failure_records_the_interpretation_stage_and_nothing_else(seam_conn):
    record_group(seam_conn, _group())
    decision = _apply(seam_conn, CallFailed(
        request_identity="dossier-1", release_id="rel-1", audit_id=17,
        explanation="the client raised", validator_version="P8/0.1.0",
        policy_version="policy-1"))
    assert decision.failure_stage == INTERPRETATION
    assert memberships_for_group(seam_conn, GROUP) == ()
    assert seam_conn.execute(
        "SELECT count(*) AS c FROM group_acceptance").fetchone()["c"] == 0
    assert seam_conn.execute(
        "SELECT stage FROM group_failure_points").fetchone()["stage"] == INTERPRETATION


def test_validation_unavailable_writes_nothing_and_is_not_an_abstention(seam_conn):
    record_group(seam_conn, _group())
    decision = _apply(seam_conn, ValidationUnavailable(missing=("contradicts",)))
    assert memberships_for_group(seam_conn, GROUP) == ()
    assert decision.failure_stage == VALIDATION
    assert decision.stop_rule_outcome is None


def test_needs_consent_is_returned_unchanged_and_writes_nothing(seam_conn):
    from privacy.consent import ConsentRequirement
    from privacy.release import NeedsConsent

    record_group(seam_conn, _group())
    needs = NeedsConsent(requirement=ConsentRequirement(
        file_ids=("file-1",), handling_class="sensitive_personal",
        items=((KEY, "0:4"),), why="the packet carries a sensitive record"),
        consent_request_id="consent-1")
    assert _apply(seam_conn, needs) is needs
    assert memberships_for_group(seam_conn, GROUP) == ()
    for table in ("group_acceptance", "group_failure_points", "memberships"):
        assert seam_conn.execute(
            f"SELECT count(*) AS c FROM {table}").fetchone()["c"] == 0


# --- SR5 is mapped from P8's reasons, never re-derived ---------------------------


def test_a_citation_failure_from_p8_maps_to_sr5(seam_conn):
    """P9 does not inspect citations. It reads the authoritative reason codes."""
    record_group(seam_conn, _group())
    decision = _apply(seam_conn, _verdict(
        REJECT, reasons=(CITATION_NOT_IN_DOSSIER,)))
    assert decision.stop_rule_outcome is not None
    assert decision.stop_rule_outcome.rules_fired == (SR5,)
    assert decision.stop_rule_outcome.outcome == NO_GROUP


def test_a_rejection_for_another_reason_is_not_sr5(seam_conn):
    from llm_harness.vocabulary import CONTRADICTED_BY_STRONGER

    record_group(seam_conn, _group())
    decision = _apply(seam_conn, _verdict(
        REJECT, reasons=(CONTRADICTED_BY_STRONGER,)))
    assert decision.stop_rule_outcome is None


def test_p9_reads_no_citation_and_runs_no_second_validator():
    import ast
    import pathlib

    import grouping.p8_seam as module

    text = pathlib.Path(module.__file__).read_text()
    for banned in ("citations_checked", "span_matched", "resolved",
                   "evidence_resolver", "contradicts", "normalize"):
        assert banned not in text, banned
    tree = ast.parse(text)
    called = {
        node.func.id for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "validate_response" not in called
    assert "dispatch" not in called


# --- a budget-deferred result is not P9's ladder to run --------------------------


def test_a_budget_deferred_p8_result_maps_to_dossier_deferred(seam_conn):
    from llm_harness.vocabulary import BUDGET_EXHAUSTED

    record_group(seam_conn, _group())
    decision = _apply(seam_conn, _verdict(
        ABSTAIN, reasons=(BUDGET_EXHAUSTED,)))
    assert isinstance(decision.deferred, DossierDeferred)
    assert memberships_for_group(seam_conn, GROUP) == ()


def test_p9_never_runs_the_reduction_ladder():
    """M9's summarize -> preserve anchors -> split/defer ladder is P8's `run_call`.
    Checked over identifiers and string literals, since the docstring has to be
    able to name the thing it is refusing to do."""
    import ast
    import pathlib

    import grouping.p8_seam as module

    # `max_dossier_tokens` is P8's own field and P9 passes it through untouched.
    # What is banned is a P9 decision about it.
    banned = {"summarize", "summarise", "split_shard", "reduction"}
    tree = ast.parse(pathlib.Path(module.__file__).read_text())
    docstrings = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)) and body:
            first = body[0]
            if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docstrings.add(id(first.value))
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and any(
                word in node.id.lower() for word in banned):
            offenders.append(f"{node.lineno}:{node.id}")
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and id(node) not in docstrings):
            for word in banned:
                if word in node.value.lower():
                    offenders.append(f"{node.lineno}:{word}")
    assert offenders == [], offenders
