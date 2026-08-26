# tests/p8/conftest.py
"""P8's test fixtures.

`p8_conn` is P1's root `conn` fixture with P8's Task 3 tables added. `tests/conftest.py`
is not modified — P1 owns it. Budget tables are Task 4 and are not created here.

Nothing in this file may be a name another part's conftest also defines: `tests/`
carries no `__init__.py`, so pytest puts each test directory on `sys.path`.
`RecordingSink` lives in p5. Only P8 fixtures and tiny record builders live here —
and `tests/p8/__init__.py` makes this file `p8.conftest` rather than the top-level
module `conftest`.
"""
from __future__ import annotations

import pytest

from database_agent.db import create_schema

from llm_harness.records import (
    Conflict,
    Dossier,
    EvidenceItem,
    GroundingReport,
    P8Verdict,
    PreCallAbstention,
    Refusal,
    ReleasedEvidence,
)
from llm_harness.vocabulary import (
    A_FACT,
    ACCEPT_DIRECT,
    DIRECT_ANCHOR,
    LLM_SUPPORTED,
    NOT_ELIGIBLE_FOR_MODEL,
    REDUCTION_NONE,
    REMAINS_AMBIGUOUS,
    SCOPE_FILE,
)
from privacy.denial import RemedyOption
from privacy.release import Denied

#: Injectable clock so equality assertions on stored timestamps are possible.
FIXED_CLOCK = "2026-08-25T12:00:00+00:00"

TASK3_TABLES = (
    "llm_dossier",
    "llm_response",
    "llm_verdict",
    "llm_grounding_report",
    "llm_verdict_supersession",
    "llm_refusal",
    "llm_pre_call_abstention",
    "llm_call_failure",
)

BUDGET_TABLES = ("llm_scan_budget", "llm_budget_reservation")


@pytest.fixture()
def p8_conn(conn):
    """P1's database with P8's Task 3 tables. Tests call `create_llm_schema` here."""
    from llm_harness.schema import create_llm_schema

    create_schema(conn)
    create_llm_schema(conn)
    return conn


def make_dossier(**overrides) -> Dossier:
    values = dict(
        dossier_id="dossier-1",
        call_site=A_FACT,
        subject_ref="file-1",
        eligibility_reason=REMAINS_AMBIGUOUS,
        plan_version=None,
        policy_version="policy-1",
        allowed_vocabulary=("school",),
        evidence_items=(),
        conflicts=(),
        released_evidence=(),
        max_dossier_tokens=4000,
        reduction_rung=REDUCTION_NONE,
        release_id="rel-1",
    )
    values.update(overrides)
    return Dossier(**values)


def make_evidence_item(**overrides) -> EvidenceItem:
    """Builder-owned reference metadata. P8 never synthesises these six fields."""
    values = dict(
        evidence_ref="obs-key-1",
        kind="excerpt",
        location="body",
        excerpt_span=None,
        reliability_state="direct",
        basis=DIRECT_ANCHOR,
    )
    values.update(overrides)
    return EvidenceItem(**values)


def make_released_evidence(**overrides) -> ReleasedEvidence:
    values = dict(
        observation_key="obs-key-1",
        address="0:19",
        value="Columbia University",
        zone="body",
        context_before=None,
        context_after=None,
        context_truncated=False,
    )
    values.update(overrides)
    return ReleasedEvidence(**values)


def make_verdict(**overrides) -> P8Verdict:
    values = dict(
        verdict_id="verdict-1",
        dossier_id="dossier-1",
        claim_ref="claim-1",
        outcome=ACCEPT_DIRECT,
        disposition=LLM_SUPPORTED,
        reasons=(),
        may_propose=False,
        requires_review=False,
        citations_checked=(),
        scope=SCOPE_FILE,
        validator_version="P8/0.1.0",
        policy_version="policy-1",
        plan_version=None,
    )
    values.update(overrides)
    return P8Verdict(**values)


def make_zero_report(**overrides) -> GroundingReport:
    values = dict(
        dossier_id="dossier-1",
        call_site=A_FACT,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        validator_version="P8/0.1.0",
        citations_total=0,
        citations_resolved=0,
        citations_span_matched=0,
        claims_total=0,
        claims_abstained=0,
        claims_accepted_direct=0,
        claims_accepted_context=0,
        claims_weak=0,
        claims_rejected=0,
        reasons_histogram={},
        reduction_rung=REDUCTION_NONE,
        release_audit_id=None,
        dossier_builder="fixture",
    )
    values.update(overrides)
    return GroundingReport(**values)


def make_issued_report(**overrides) -> GroundingReport:
    values = dict(
        citations_total=1,
        citations_resolved=1,
        citations_span_matched=1,
        claims_total=1,
        claims_accepted_direct=1,
        release_audit_id=17,
    )
    values.update(overrides)
    return make_zero_report(**values)


def make_refusal() -> Refusal:
    return Refusal(
        denied=Denied(
            reason="unclassified",
            explanation="no classification is stored for this file",
            remedy_options=(RemedyOption(action="classify", detail="classify first"),),
            evidence_refs=("obs-key-1",),
        )
    )


def make_abstention(**overrides) -> PreCallAbstention:
    values = dict(
        reason=NOT_ELIGIBLE_FOR_MODEL,
        call_site=A_FACT,
        subject_ref="file-1",
    )
    values.update(overrides)
    return PreCallAbstention(**values)
