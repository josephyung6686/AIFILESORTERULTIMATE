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


# --- a real Site A bundle -------------------------------------------------------
#
# R3 removed the injectable `site_validator`, so any test that reaches Site A now
# needs P6's own `FactRequest` over a real P1 file and P4 observation. One
# definition, used by `tests/p8` and `tests/integration` alike.

RELEASED_MATERIAL = "Columbia University - redacted dossier excerpt"


def record_subject(conn, tmp_path, *, released: str = RELEASED_MATERIAL):
    """A real P1 file with one real P4 observation. Returns the P6 identity triple."""
    import json

    from database_agent.files_table import get_file, record_file
    from evidence_shape.location import Location, Segment
    from evidence_shape.observation import Observation
    from evidence_shape.runs import ExtractionRun
    from evidence_shape.store import record_observation, record_run

    path = tmp_path / "Syllabus.pdf"
    body = b"BUSIB 4300 Syllabus, Spring 2026"
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename="Syllabus.pdf", normalized_filename="syllabus.pdf",
        extension=".pdf", observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    record_run(conn, ExtractionRun(
        run_id="r-1", file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=FIXED_CLOCK, finished_at=FIXED_CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=released,
        location=Location("heading", (Segment("field", label="heading"),)),
        occurrence_count=1, observed_at=FIXED_CLOCK, reliability="possible",
        run_id="r-1", context_before="Syllabus - ")
    record_observation(conn, observation)
    return file_id, content_hash, observation.observation_key


def make_fact_bundle(conn, subject):
    """Site A's real authorities: P6's own FactRequest plus the C-5 oracles."""
    from facts.domains import ActivationSignal, ActivationSignals
    from facts.llm_seam import build_request
    from llm_harness.fact_validation import FactValidationDependencies
    from llm_harness.sites import FactSiteDependencies, SiteDependencies

    file_id, content_hash, _ = subject
    return SiteDependencies(
        fact=FactSiteDependencies(
            fact_request=build_request(
                conn, file_id=file_id, content_hash=content_hash,
                activation_signals=ActivationSignals(signals=(
                    ActivationSignal(schema_id="academic", activates=lambda rows: True),
                )),
                normalizers={"school": lambda raw: raw},
            ),
            fact_dependencies=FactValidationDependencies(
                normalize=lambda field, raw: raw,
                contradicts=lambda proposal, row: False,
            ),
        ),
        placement=None, residual=None, template=None,
    )


def empty_site_dependencies():
    """No site authorities at all. Reaching a site with this is unavailable."""
    from llm_harness.sites import SiteDependencies

    return SiteDependencies(fact=None, placement=None, residual=None, template=None)
