"""Live P6↔P8 Site A seam: FactRequest in, apply_verdict consequence out."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_observation, record_run
from facts.domains import ActivationSignal, ActivationSignals
from facts.fields import create_fields
from facts.file_facts import LLM_INTERPRETATION, facts_for_file, write_fact
from facts.llm_seam import FOUR_CHECKS, Proposal, Verdict, build_request
from facts.states import LLM_SUPPORTED, VALIDATED
from facts.unresolved import unresolved_for_file
from facts.values import VALUE_ORIGINS, ensure_value
from llm_harness.fact_validation import (
    FactValidationDependencies,
    p6_verdict_from_p8,
    validate_fact_proposal,
)
from llm_harness.records import P8Verdict, ValidationUnavailable
from llm_harness.vocabulary import ACCEPT_DIRECT

CLOCK = "2026-08-19T12:00:00+00:00"
MODEL = "test-model-1"
PROMPT = "sha256:prompt-fingerprint"
POLICY = "policy-1"
DOSSIER = "dossier-address-1"


def _signals(*schema_ids: str) -> ActivationSignals:
    return ActivationSignals(signals=tuple(
        ActivationSignal(schema_id=schema_id, activates=lambda rows: True)
        for schema_id in schema_ids))


def _record(conn, tmp_path, *, name, body):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, label="heading"):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location("heading", (Segment("field", label=label),)),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id=run_id, context_before="Syllabus — ")
    record_observation(conn, observation)
    return observation.observation_key


@pytest.fixture()
def seam_conn(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    return conn


@pytest.fixture()
def subject_file(seam_conn, tmp_path):
    file_id, content_hash = _record(
        seam_conn, tmp_path, name="Syllabus.pdf",
        body=b"BUSIB 4300 Syllabus, Spring 2026")
    key = _observe(
        seam_conn, run_id="r-1", file_id=file_id,
        content_hash=content_hash, raw="BUSIB 4300")
    return file_id, content_hash, key


def _request(conn, subject_file):
    file_id, content_hash, _ = subject_file
    return build_request(
        conn, file_id=file_id, content_hash=content_hash,
        activation_signals=_signals("academic"),
        normalizers={"subject": lambda raw: (_ for _ in ()).throw(
            AssertionError("request.normalizers is not the Site A callback"))})


def _fixture_normalize(field, raw):
    if "??" in raw:
        return None
    return raw.strip()


def _fixture_contradicts(proposal, row):
    return row["canonical_value"] != proposal.value


def _deps(*, normalize=_fixture_normalize, contradicts=_fixture_contradicts):
    return FactValidationDependencies(normalize=normalize, contradicts=contradicts)


def _released_dossier(request):
    """The dossier P7 released for this request, transparent: what the model saw
    is exactly what the store holds. These tests probe the P6 seam, not redaction.
    """
    from llm_harness.records import Dossier, EvidenceItem, ReleasedEvidence
    from llm_harness.vocabulary import (
        A_FACT,
        DIRECT_ANCHOR,
        REDUCTION_NONE,
        REMAINS_AMBIGUOUS,
    )

    return Dossier(
        dossier_id=DOSSIER,
        call_site=A_FACT,
        subject_ref=request.file_id,
        eligibility_reason=REMAINS_AMBIGUOUS,
        plan_version=None,
        policy_version=POLICY,
        allowed_vocabulary=tuple(request.allowlist),
        evidence_items=tuple(
            EvidenceItem(
                evidence_ref=o.observation_key, kind="excerpt",
                location="heading", excerpt_span=(0, len(o.raw_value)),
                reliability_state="direct", basis=DIRECT_ANCHOR,
            )
            for o in request.citable_observations
        ),
        conflicts=(),
        released_evidence=tuple(
            ReleasedEvidence(
                observation_key=o.observation_key,
                address=f"0:{len(o.raw_value)}", value=o.raw_value,
                zone="heading", context_before=None, context_after=None,
                context_truncated=False,
            )
            for o in request.citable_observations
        ),
        max_dossier_tokens=4000,
        reduction_rung=REDUCTION_NONE,
        release_id="rel-1",
    )


def _quoting(proposal, dossier):
    from llm_harness.records import Citation

    by_key = {item.observation_key: item for item in dossier.released_evidence}
    keys = proposal.citations if proposal.citations is not None else ()
    return tuple(
        Citation(
            evidence_ref=key,
            cited_span=by_key[key].value if key in by_key else "unreleased",
            metadata_field_name=None, why_it_supports="fixture",
        )
        for key in keys
    )


def _validate(conn, request, proposal, *, dependencies=None):
    dossier = _released_dossier(request)
    return validate_fact_proposal(
        conn, request, proposal,
        dependencies=dependencies if dependencies is not None else _deps(),
        model_identifier=MODEL,
        prompt_fingerprint=PROMPT,
        policy_version=POLICY,
        dossier=dossier,
        citations=_quoting(proposal, dossier),
        evidence_resolver=lambda key: "the store still holds it",
    )


def _reasons(conn, request):
    return [row["reason"] for row in unresolved_for_file(
        conn, request.file_id, request.content_hash)]


def test_build_request_then_validate_writes_one_llm_supported_fact(
        subject_file, seam_conn):
    request = _request(seam_conn, subject_file)
    key = subject_file[2]
    proposal = Proposal(
        field_key="subject", value="BUSIB 4300", citations=(key,), unknown=False)
    result = _validate(seam_conn, request, proposal)
    assert isinstance(result, P8Verdict)
    assert type(result) is not Verdict
    assert result.outcome == ACCEPT_DIRECT
    rows = [
        row for row in facts_for_file(
            seam_conn, request.file_id, request.content_hash)
        if row["field_key"] == "subject"
    ]
    assert len(rows) == 1
    assert rows[0]["reliability_state"] == LLM_SUPPORTED
    assert rows[0]["origin"] == LLM_INTERPRETATION
    assert rows[0]["model_identifier"] == MODEL
    assert rows[0]["prompt_fingerprint"] == PROMPT
    assert json.loads(rows[0]["evidence_refs"]) == [key]
    assert unresolved_for_file(
        seam_conn, request.file_id, request.content_hash) == []


def test_missing_normalize_writes_no_fact_and_no_unresolved(subject_file, seam_conn):
    request = _request(seam_conn, subject_file)
    proposal = Proposal(
        field_key="subject", value="BUSIB 4300",
        citations=(subject_file[2],), unknown=False)
    result = _validate(
        seam_conn, request, proposal,
        dependencies=FactValidationDependencies(
            normalize=None, contradicts=_fixture_contradicts),
    )
    assert isinstance(result, ValidationUnavailable)
    assert result.missing == ("normalize",)
    assert facts_for_file(seam_conn, request.file_id, request.content_hash) == []
    assert unresolved_for_file(
        seam_conn, request.file_id, request.content_hash) == []


def test_four_failures_use_p6_unresolved_reasons_not_p8_spellings(
        subject_file, seam_conn):
    key = subject_file[2]
    request = _request(seam_conn, subject_file)

    cases = [
        (Proposal(field_key="event", value="Graduation",
                  citations=(key,), unknown=False),
         "field_not_in_active_schema", FOUR_CHECKS[0]),
        (Proposal(field_key="subject", value="BUSIB 4300",
                  citations=("sha256:" + "b" * 64,), unknown=False),
         "citation_absent_from_evidence", FOUR_CHECKS[1]),
        (Proposal(field_key="subject", value="  ??  ",
                  citations=(key,), unknown=False),
         "normalization_failed", FOUR_CHECKS[2]),
    ]
    for proposal, reason, check in cases:
        before = len(unresolved_for_file(
            seam_conn, request.file_id, request.content_hash))
        result = _validate(seam_conn, request, proposal)
        assert isinstance(result, P8Verdict)
        assert result.outcome == "reject"
        mapped = p6_verdict_from_p8(result)
        assert mapped.failed_check is check
        after = unresolved_for_file(
            seam_conn, request.file_id, request.content_hash)
        assert len(after) == before + 1
        assert after[-1]["reason"] == reason
        assert facts_for_file(
            seam_conn, request.file_id, request.content_hash) == []


def test_stronger_fact_contradiction_keeps_the_existing_row(subject_file, seam_conn):
    file_id, content_hash, key = subject_file
    value_id = ensure_value(
        seam_conn, field_key="subject", canonical_value="BUSIB 4300",
        first_evidence_ref=key, origin=VALUE_ORIGINS[0])
    write_fact(
        seam_conn, file_id=file_id, content_hash=content_hash,
        field_key="subject", value_id=value_id,
        reliability_state=VALIDATED, origin="rule",
        evidence_refs=(key,), cache_key="sha256:the-native-pass-slot", active=True)
    request = _request(seam_conn, subject_file)
    proposal = Proposal(
        field_key="subject", value="ECON 1010", citations=(key,), unknown=False)
    result = _validate(seam_conn, request, proposal)
    assert result.outcome == "reject"
    subjects = [
        row for row in facts_for_file(seam_conn, file_id, content_hash)
        if row["field_key"] == "subject"
    ]
    assert [row["canonical_value"] for row in subjects] == ["BUSIB 4300"]
    assert _reasons(seam_conn, request) == ["contradicted_by_stronger_fact"]


def test_unknown_is_p6_model_returned_unknown(subject_file, seam_conn):
    request = _request(seam_conn, subject_file)
    proposal = Proposal(
        field_key="subject", value=None, citations=(), unknown=True)
    result = _validate(seam_conn, request, proposal)
    assert result.outcome == "abstain"
    assert facts_for_file(seam_conn, request.file_id, request.content_hash) == []
    assert _reasons(seam_conn, request) == ["model_returned_unknown"]


def test_p8_does_not_write_facts_itself(subject_file, seam_conn):
    request = _request(seam_conn, subject_file)
    proposal = Proposal(
        field_key="subject", value="BUSIB 4300",
        citations=(subject_file[2],), unknown=False)
    _validate(seam_conn, request, proposal)
    rows = facts_for_file(seam_conn, request.file_id, request.content_hash)
    assert len(rows) == 1
    assert rows[0]["origin"] == LLM_INTERPRETATION
    assert rows[0]["reliability_state"] == LLM_SUPPORTED


def test_callbacks_are_fixtures_not_p6_exports():
    import facts
    from facts import llm_seam

    assert not hasattr(llm_seam, "normalize")
    assert not hasattr(llm_seam, "contradicts")
    assert not hasattr(facts, "normalize")
    assert not hasattr(facts, "contradicts")
    assert "facts" not in _fixture_normalize.__module__
    assert "llm_harness" not in _fixture_normalize.__module__
    assert _fixture_normalize.__module__ == _fixture_contradicts.__module__
    assert _fixture_normalize.__module__.startswith("test_p8_p6")
