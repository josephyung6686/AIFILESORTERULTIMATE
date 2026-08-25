"""Site A fact validation through explicit P6-domain dependencies."""
from __future__ import annotations

import ast
import dataclasses
import importlib
import inspect
import json
import pkgutil
from pathlib import Path

import pytest

import facts
import llm_harness
from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from facts import llm_seam
from facts.domains import ActivationSignal, ActivationSignals
from facts.file_facts import facts_for_file, write_fact
from facts.llm_seam import (
    FOUR_CHECKS,
    FactRequest,
    Proposal,
    Verdict,
    apply_verdict,
    build_request,
)
from facts.states import LLM_SUPPORTED, POSSIBLE, VALIDATED
from facts.unresolved import unresolved_for_file
from facts.values import VALUE_ORIGINS, ensure_value
from llm_harness.authorship import COMPONENT_VERSION
from llm_harness.fact_validation import (
    FactValidationDependencies,
    p6_verdict_from_p8,
    proposal_state_from_p8,
    validate_fact_proposal,
)
from llm_harness.records import P8Verdict, ValidationUnavailable
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    CITATION_NOT_FOUND,
    CONTRADICTED_BY_STRONGER,
    FIELD_NOT_IN_ACTIVE_SCHEMA,
    REJECT,
    SEARCH_HINT_ONLY,
    VALUE_NOT_NORMALIZABLE,
    WEAK,
)

CLOCK = "2026-08-19T12:00:00+00:00"
MODEL = "test-model-1"
PROMPT = "sha256:prompt-fingerprint"
POLICY = "policy-1"
SRC = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "llm_harness"
    / "fact_validation.py"
)


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
def p6_conn(conn):
    from database_agent.db import create_schema
    from evidence_shape.schema import create_evidence_schema
    from facts.fields import create_fields

    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    return conn


@pytest.fixture()
def subject_file(p6_conn, tmp_path):
    file_id, content_hash = _record(
        p6_conn, tmp_path, name="Syllabus.pdf",
        body=b"BUSIB 4300 Syllabus, Spring 2026")
    key = _observe(
        p6_conn, run_id="r-1", file_id=file_id,
        content_hash=content_hash, raw="BUSIB 4300")
    return file_id, content_hash, key


def _boom_normalizer(_raw):
    raise AssertionError("FactRequest.normalizers is carried, not called")


def _request(conn, subject_file) -> FactRequest:
    file_id, content_hash, _ = subject_file
    return build_request(
        conn, file_id=file_id, content_hash=content_hash,
        activation_signals=_signals("academic"),
        normalizers={"subject": _boom_normalizer})


def _pass_normalize(field, raw):
    return raw


def _never_contradicts(proposal, row):
    return False


def _deps(*, normalize=_pass_normalize, contradicts=_never_contradicts):
    return FactValidationDependencies(normalize=normalize, contradicts=contradicts)


def _proposal(subject_file, *, field_key="subject", value="BUSIB 4300",
              citations=None, unknown=False):
    key = subject_file[2]
    if unknown:
        return Proposal(field_key=field_key, value=None, citations=(), unknown=True)
    if citations is None:
        citations = (key,)
    return Proposal(
        field_key=field_key, value=value, citations=citations, unknown=False)


def _validate(conn, request, proposal, *, dependencies=None, **kwargs):
    return validate_fact_proposal(
        conn, request, proposal,
        dependencies=dependencies if dependencies is not None else _deps(),
        model_identifier=MODEL,
        prompt_fingerprint=PROMPT,
        policy_version=POLICY,
        **kwargs,
    )


def _reasons(conn, request, field_key=None):
    return [row["reason"] for row in unresolved_for_file(
        conn, request.file_id, request.content_hash, field_key=field_key)]


def _code_strings(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and body:
            first = body[0]
            if (isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docstrings.add(id(first.value))
    return {
        node.value for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        and id(node) not in docstrings
    }


def test_live_facts_publishes_neither_normalize_nor_contradicts():
    for owner in (llm_seam, facts):
        assert not hasattr(owner, "normalize")
        assert not hasattr(owner, "contradicts")
    for info in pkgutil.iter_modules(facts.__path__):
        module = importlib.import_module(f"facts.{info.name}")
        assert not hasattr(module, "normalize"), info.name
        assert not hasattr(module, "contradicts"), info.name


def test_dependency_type_is_frozen_and_names_both_callbacks():
    fields = [item.name for item in dataclasses.fields(FactValidationDependencies)]
    assert fields == ["normalize", "contradicts"]
    deps = _deps()
    assert dataclasses.is_dataclass(deps) and deps.__dataclass_params__.frozen
    with pytest.raises(dataclasses.FrozenInstanceError):
        deps.normalize = _pass_normalize  # type: ignore[misc]


def test_public_surface_is_unchanged_and_site_a_is_not_exported():
    assert llm_harness.__all__ == [
        "Dossier",
        "P8Verdict",
        "Refusal",
        "ValidationUnavailable",
        "NeedsConsent",
    ]
    assert not hasattr(llm_harness, "validate_fact_proposal")
    assert not hasattr(llm_harness, "FactValidationDependencies")
    assert not hasattr(llm_harness, "Verdict")
    assert "Verdict" not in llm_harness.__all__


def test_omitting_dependencies_is_type_error_not_a_default(subject_file, p6_conn):
    request = _request(p6_conn, subject_file)
    proposal = _proposal(subject_file)
    with pytest.raises(TypeError):
        validate_fact_proposal(
            p6_conn, request, proposal,
            model_identifier=MODEL,
            prompt_fingerprint=PROMPT,
            policy_version=POLICY,
        )


def test_omitted_normalize_is_unavailable_and_writes_nothing(subject_file, p6_conn):
    request = _request(p6_conn, subject_file)
    proposal = _proposal(subject_file)
    result = _validate(
        p6_conn, request, proposal,
        dependencies=FactValidationDependencies(
            normalize=None, contradicts=_never_contradicts,
        ),
    )
    assert isinstance(result, ValidationUnavailable)
    assert result.missing == ("normalize",)
    assert not isinstance(result, P8Verdict)
    assert facts_for_file(p6_conn, request.file_id, request.content_hash) == []
    assert unresolved_for_file(p6_conn, request.file_id, request.content_hash) == []


def test_omitted_contradicts_is_unavailable_and_writes_nothing(subject_file, p6_conn):
    request = _request(p6_conn, subject_file)
    proposal = _proposal(subject_file)
    result = _validate(
        p6_conn, request, proposal,
        dependencies=FactValidationDependencies(
            normalize=_pass_normalize, contradicts=None,
        ),
    )
    assert isinstance(result, ValidationUnavailable)
    assert result.missing == ("contradicts",)
    assert facts_for_file(p6_conn, request.file_id, request.content_hash) == []
    assert unresolved_for_file(p6_conn, request.file_id, request.content_hash) == []


def test_omitted_both_callbacks_names_both_and_makes_no_callback(subject_file, p6_conn):
    request = _request(p6_conn, subject_file)
    proposal = _proposal(subject_file)
    result = _validate(
        p6_conn, request, proposal,
        dependencies=FactValidationDependencies(normalize=None, contradicts=None),
    )
    assert isinstance(result, ValidationUnavailable)
    assert result.missing == ("normalize", "contradicts")
    assert facts_for_file(p6_conn, request.file_id, request.content_hash) == []
    assert unresolved_for_file(p6_conn, request.file_id, request.content_hash) == []


def test_none_dependencies_is_unavailable(subject_file, p6_conn):
    request = _request(p6_conn, subject_file)
    proposal = _proposal(subject_file)
    result = validate_fact_proposal(
        p6_conn, request, proposal,
        dependencies=None,
        model_identifier=MODEL,
        prompt_fingerprint=PROMPT,
        policy_version=POLICY,
    )
    assert isinstance(result, ValidationUnavailable)
    assert result.missing == ("normalize", "contradicts")
    assert facts_for_file(p6_conn, request.file_id, request.content_hash) == []


def test_missing_deps_does_not_call_injected_oracles(subject_file, p6_conn):
    request = _request(p6_conn, subject_file)
    proposal = _proposal(subject_file)
    calls: list[str] = []

    def normalize(field, raw):
        calls.append("normalize")
        return raw

    result = _validate(
        p6_conn, request, proposal,
        dependencies=FactValidationDependencies(
            normalize=normalize, contradicts=None,
        ),
    )
    assert isinstance(result, ValidationUnavailable)
    assert calls == []


def test_field_outside_allowlist_fails_check_one_and_skips_later(
        subject_file, p6_conn):
    request = _request(p6_conn, subject_file)
    assert "event" not in request.allowlist
    calls: list[str] = []

    def normalize(field, raw):
        calls.append("normalize")
        return raw

    def contradicts(proposal, row):
        calls.append("contradicts")
        return False

    proposal = _proposal(subject_file, field_key="event", value="Graduation")
    result = _validate(
        p6_conn, request, proposal,
        dependencies=_deps(normalize=normalize, contradicts=contradicts),
    )
    assert isinstance(result, P8Verdict)
    assert result.outcome == REJECT
    assert result.reasons == (FIELD_NOT_IN_ACTIVE_SCHEMA,)
    assert result.may_propose is False
    assert calls == []
    assert _reasons(p6_conn, request) == ["field_not_in_active_schema"]
    assert facts_for_file(p6_conn, request.file_id, request.content_hash) == []


def test_citation_absent_from_citable_observations_fails_check_two(
        subject_file, p6_conn):
    request = _request(p6_conn, subject_file)
    calls: list[str] = []

    def normalize(field, raw):
        calls.append("normalize")
        return raw

    def contradicts(proposal, row):
        calls.append("contradicts")
        return False

    missing = "sha256:" + "b" * 64
    proposal = _proposal(subject_file, citations=(missing,))
    result = _validate(
        p6_conn, request, proposal,
        dependencies=_deps(normalize=normalize, contradicts=contradicts),
    )
    assert isinstance(result, P8Verdict)
    assert result.outcome == REJECT
    assert result.reasons == (CITATION_NOT_FOUND,)
    assert result.citations_checked[0].citation_ref == missing
    assert result.citations_checked[0].resolved is False
    assert calls == []
    assert _reasons(p6_conn, request) == ["citation_absent_from_evidence"]


def test_empty_citations_fail_check_two(subject_file, p6_conn):
    request = _request(p6_conn, subject_file)
    proposal = Proposal(
        field_key="subject", value="BUSIB 4300", citations=(), unknown=False)
    result = _validate(p6_conn, request, proposal)
    assert result.outcome == REJECT
    assert result.reasons == (CITATION_NOT_FOUND,)
    assert _reasons(p6_conn, request) == ["citation_absent_from_evidence"]


def test_normalization_none_fails_check_three_and_skips_contradicts(
        subject_file, p6_conn):
    request = _request(p6_conn, subject_file)
    calls: list[str] = []

    def normalize(field, raw):
        calls.append(("normalize", field, raw))
        return None

    def contradicts(proposal, row):
        calls.append("contradicts")
        return False

    proposal = _proposal(subject_file, value="  ??  ")
    result = _validate(
        p6_conn, request, proposal,
        dependencies=_deps(normalize=normalize, contradicts=contradicts),
    )
    assert result.outcome == REJECT
    assert result.reasons == (VALUE_NOT_NORMALIZABLE,)
    assert calls == [("normalize", "subject", "  ??  ")]
    assert _reasons(p6_conn, request) == ["normalization_failed"]


def test_contradiction_oracle_fails_check_four(subject_file, p6_conn):
    file_id, content_hash, key = subject_file
    value_id = ensure_value(
        p6_conn, field_key="subject", canonical_value="BUSIB 4300",
        first_evidence_ref=key, origin=VALUE_ORIGINS[0])
    write_fact(
        p6_conn, file_id=file_id, content_hash=content_hash,
        field_key="subject", value_id=value_id,
        reliability_state=VALIDATED, origin="rule",
        evidence_refs=(key,), cache_key="sha256:the-native-pass-slot", active=True)
    request = _request(p6_conn, subject_file)
    assert request.existing_facts

    seen_rows: list[object] = []

    def contradicts(proposal, row):
        seen_rows.append(row)
        return True

    proposal = _proposal(subject_file, value="ECON 1010")
    result = _validate(
        p6_conn, request, proposal,
        dependencies=_deps(contradicts=contradicts),
    )
    assert result.outcome == REJECT
    assert result.reasons == (CONTRADICTED_BY_STRONGER,)
    assert len(seen_rows) == 1
    assert _reasons(p6_conn, request) == ["contradicted_by_stronger_fact"]
    subjects = [
        row for row in facts_for_file(p6_conn, file_id, content_hash)
        if row["field_key"] == "subject"
    ]
    assert [row["canonical_value"] for row in subjects] == ["BUSIB 4300"]


def test_passing_proposal_writes_llm_supported_via_apply_verdict(
        subject_file, p6_conn):
    request = _request(p6_conn, subject_file)
    proposal = _proposal(subject_file)
    result = _validate(p6_conn, request, proposal)
    assert isinstance(result, P8Verdict)
    assert result.outcome == ACCEPT_DIRECT
    assert result.disposition == LLM_SUPPORTED
    assert result.may_propose is True
    assert result.requires_review is False
    assert result.reasons == ()
    assert result.scope == "file"
    assert result.validator_version == COMPONENT_VERSION
    assert result.plan_version is None
    assert result is not llm_seam.Verdict
    assert type(result) is P8Verdict
    rows = [
        row for row in facts_for_file(
            p6_conn, request.file_id, request.content_hash)
        if row["field_key"] == "subject"
    ]
    assert len(rows) == 1
    assert rows[0]["reliability_state"] == LLM_SUPPORTED
    assert unresolved_for_file(
        p6_conn, request.file_id, request.content_hash) == []


def test_unknown_skips_checks_and_preserves_p6_unresolved(subject_file, p6_conn):
    request = _request(p6_conn, subject_file)
    calls: list[str] = []

    def normalize(field, raw):
        calls.append("normalize")
        return raw

    def contradicts(proposal, row):
        calls.append("contradicts")
        return False

    proposal = _proposal(subject_file, unknown=True)
    result = _validate(
        p6_conn, request, proposal,
        dependencies=_deps(normalize=normalize, contradicts=contradicts),
    )
    assert result.outcome == ABSTAIN
    assert result.reasons == ()
    assert result.may_propose is False
    assert calls == []
    assert facts_for_file(p6_conn, request.file_id, request.content_hash) == []
    assert _reasons(p6_conn, request) == ["model_returned_unknown"]


def test_unknown_for_field_outside_allowlist_is_still_unknown(subject_file, p6_conn):
    request = _request(p6_conn, subject_file)
    proposal = _proposal(subject_file, field_key="event", unknown=True)
    result = _validate(p6_conn, request, proposal)
    assert result.outcome == ABSTAIN
    assert _reasons(p6_conn, request) == ["model_returned_unknown"]


def test_mapped_p6_verdict_uses_four_checks_members_not_copied_strings(
        subject_file, p6_conn, monkeypatch):
    request = _request(p6_conn, subject_file)
    captured: dict[str, object] = {}

    def capture(conn, *, request, proposal, verdict, proposal_state,
                model_identifier, prompt_fingerprint):
        captured["verdict"] = verdict
        captured["proposal_state"] = proposal_state
        captured["model_identifier"] = model_identifier
        captured["prompt_fingerprint"] = prompt_fingerprint
        return apply_verdict(
            conn, request=request, proposal=proposal, verdict=verdict,
            proposal_state=proposal_state,
            model_identifier=model_identifier,
            prompt_fingerprint=prompt_fingerprint)

    monkeypatch.setattr(
        "llm_harness.fact_validation.apply_verdict", capture)

    result = _validate(
        p6_conn, request, _proposal(subject_file, field_key="event",
                                    value="Graduation"))
    p6_verdict = captured["verdict"]
    assert type(p6_verdict) is Verdict
    assert type(result) is P8Verdict
    assert P8Verdict is not Verdict
    assert p6_verdict.passed is False
    assert p6_verdict.failed_check == FOUR_CHECKS[0]
    assert p6_verdict.failed_check is FOUR_CHECKS[0]
    assert captured["model_identifier"] == MODEL
    assert captured["prompt_fingerprint"] == PROMPT


def test_p6_verdict_mapping_covers_each_failed_check():
    def reject(*reasons):
        return P8Verdict(
            verdict_id="v1", dossier_id="d1", claim_ref="subject",
            outcome=REJECT, disposition="rejected", reasons=reasons,
            may_propose=False, requires_review=False, citations_checked=(),
            scope="file", validator_version=COMPONENT_VERSION,
            policy_version=POLICY, plan_version=None,
        )

    mapped = [
        p6_verdict_from_p8(reject(FIELD_NOT_IN_ACTIVE_SCHEMA)),
        p6_verdict_from_p8(reject(CITATION_NOT_FOUND)),
        p6_verdict_from_p8(reject(VALUE_NOT_NORMALIZABLE)),
        p6_verdict_from_p8(reject(CONTRADICTED_BY_STRONGER)),
    ]
    assert [item.failed_check for item in mapped] == list(FOUR_CHECKS)
    assert all(item.failed_check is FOUR_CHECKS[i] for i, item in enumerate(mapped))
    accept = P8Verdict(
        verdict_id="v1", dossier_id="d1", claim_ref="subject",
        outcome=ACCEPT_DIRECT, disposition=LLM_SUPPORTED, reasons=(),
        may_propose=True, requires_review=False, citations_checked=(),
        scope="file", validator_version=COMPONENT_VERSION,
        policy_version=POLICY, plan_version=None,
    )
    assert p6_verdict_from_p8(accept) == Verdict(passed=True, failed_check=None)


def test_proposal_state_mapping_uses_p6_states():
    def verdict(outcome, *, disposition, may_propose, requires_review, reasons=()):
        return P8Verdict(
            verdict_id="v1", dossier_id="d1", claim_ref="subject",
            outcome=outcome, disposition=disposition, reasons=reasons,
            may_propose=may_propose, requires_review=requires_review,
            citations_checked=(), scope="file",
            validator_version=COMPONENT_VERSION, policy_version=POLICY,
            plan_version=None,
        )

    assert proposal_state_from_p8(verdict(
        ACCEPT_DIRECT, disposition=LLM_SUPPORTED,
        may_propose=True, requires_review=False,
    )) is LLM_SUPPORTED
    assert proposal_state_from_p8(verdict(
        ACCEPT_CONTEXT_SUPPORTED, disposition="llm_supported_review",
        may_propose=True, requires_review=True,
    )) is LLM_SUPPORTED
    assert proposal_state_from_p8(verdict(
        WEAK, disposition=POSSIBLE, may_propose=False, requires_review=False,
        reasons=(SEARCH_HINT_ONLY,),
    )) is POSSIBLE


def test_weak_mapping_writes_possible_not_a_duplicate_writer(
        subject_file, p6_conn):
    request = _request(p6_conn, subject_file)
    weak = P8Verdict(
        verdict_id="v1", dossier_id=request.file_id, claim_ref="subject",
        outcome=WEAK, disposition=POSSIBLE, reasons=(SEARCH_HINT_ONLY,),
        may_propose=False, requires_review=False, citations_checked=(),
        scope="file", validator_version=COMPONENT_VERSION,
        policy_version=POLICY, plan_version=None,
    )
    assert proposal_state_from_p8(weak) is POSSIBLE
    assert p6_verdict_from_p8(weak) == Verdict(passed=True)

    apply_verdict(
        p6_conn, request=request, proposal=_proposal(subject_file),
        verdict=p6_verdict_from_p8(weak),
        proposal_state=proposal_state_from_p8(weak),
        model_identifier=MODEL, prompt_fingerprint=PROMPT)
    rows = facts_for_file(p6_conn, request.file_id, request.content_hash)
    assert [row["reliability_state"] for row in rows] == [POSSIBLE]


def test_request_normalizers_are_not_called(subject_file, p6_conn):
    request = _request(p6_conn, subject_file)
    assert callable(request.normalizers["subject"])
    result = _validate(p6_conn, request, _proposal(subject_file))
    assert result.outcome == ACCEPT_DIRECT


def test_apply_verdict_kwargs_have_no_proposal_state_default():
    signature = inspect.signature(validate_fact_proposal)
    assert "proposal_state" not in signature.parameters
    for name in ("dependencies", "model_identifier", "prompt_fingerprint",
                 "policy_version"):
        parameter = signature.parameters[name]
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
        assert parameter.default is inspect.Parameter.empty
    deps = inspect.signature(FactValidationDependencies.__init__).parameters
    assert deps["normalize"].default is inspect.Parameter.empty
    assert deps["contradicts"].default is inspect.Parameter.empty


def test_module_does_not_import_transport_or_duplicate_p6_writers():
    tree = ast.parse(SRC.read_text())
    imported: set[str] = set()
    from_imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
            from_imported |= {alias.name for alias in node.names}
    joined = " ".join(sorted(imported))
    assert "transport" not in joined
    assert "llm_harness.transport" not in imported
    assert "write_fact" not in from_imported
    assert "write_unresolved" not in from_imported
    assert "apply_verdict" in from_imported
    assert "FOUR_CHECKS" in from_imported
    strings = _code_strings(SRC)
    for member in FOUR_CHECKS:
        assert member not in strings, member
    assert "llm_supported" not in strings
    assert "possible" not in strings


def test_does_not_ship_a_domain_catalogue_or_default_oracles():
    source = SRC.read_text()
    tree = ast.parse(source)
    assert "planning/domains" not in source
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in {
            "normalize", "contradicts",
        }:
            pytest.fail(f"shipped {node.name} implementation")
    strings = _code_strings(SRC)
    assert "BUSIB 4300" not in strings
    assert "UChicago" not in strings
    assert "University of Chicago" not in strings
