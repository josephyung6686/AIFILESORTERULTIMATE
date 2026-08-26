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
DOSSIER = "dossier-address-1"
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


def _released_dossier(request, *, dossier_id=DOSSIER):
    """A dossier that released every observation P6 says is citable, verbatim.

    These tests probe P6's four checks, so the release is made transparent: what
    the model saw is exactly what the store holds. The tests that probe the
    release binding itself withhold and redact deliberately.
    """
    return _site_a_dossier(
        evidence_items=tuple(
            _item(o.observation_key) for o in request.citable_observations),
        released_evidence=tuple(
            _release(o.observation_key, o.raw_value)
            for o in request.citable_observations),
        allowed=tuple(request.allowlist),
        dossier_id=dossier_id,
        subject_ref=request.file_id,
    )


def _quoting(proposal, dossier):
    """Each citation quotes its own release exactly."""
    from llm_harness.records import Citation

    by_key = {item.observation_key: item for item in dossier.released_evidence}
    keys = proposal.citations if proposal.citations is not None else ()
    return tuple(
        Citation(
            evidence_ref=key,
            cited_span=by_key[key].value if key in by_key else "unreleased",
            metadata_field_name=None,
            why_it_supports="fixture",
        )
        for key in keys
    )


def _validate(conn, request, proposal, *, dependencies=None, dossier=None,
              citations=None, resolver=None, apply_consequence=True, **kwargs):
    if dossier is None:
        dossier = _released_dossier(request)
    if citations is None:
        citations = _quoting(proposal, dossier)
    return validate_fact_proposal(
        conn, request, proposal,
        dependencies=dependencies if dependencies is not None else _deps(),
        model_identifier=MODEL,
        prompt_fingerprint=PROMPT,
        policy_version=POLICY,
        dossier=dossier,
        citations=citations,
        evidence_resolver=resolver if resolver is not None
        else (lambda key: "the store still holds it"),
        apply_consequence=apply_consequence,
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
        "run_call",
        "DossierRequest",
        "Dossier",
        "P8Verdict",
        "Refusal",
        "CallFailed",
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
        dossier=_released_dossier(request),
        citations=_quoting(proposal, _released_dossier(request)),
        evidence_resolver=lambda key: "the store still holds it",
        apply_consequence=True,
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


def test_string_allowlist_does_not_accept_a_substring_field(subject_file, p6_conn):
    request = dataclasses.replace(
        _request(p6_conn, subject_file), allowlist="target_school")
    assert "school" in request.allowlist
    proposal = _proposal(subject_file, field_key="school", value="Booth")
    result = _validate(p6_conn, request, proposal)
    assert isinstance(result, ValidationUnavailable)
    assert result.missing == ("allowlist",)
    schools = [
        row for row in facts_for_file(
            p6_conn, request.file_id, request.content_hash)
        if row["field_key"] == "school"
    ]
    assert schools == []


def test_none_citations_is_not_an_uncaught_type_error(subject_file, p6_conn):
    request = _request(p6_conn, subject_file)
    proposal = Proposal(
        field_key="subject", value="BUSIB 4300", citations=None, unknown=False)
    result = _validate(p6_conn, request, proposal)
    assert isinstance(result, ValidationUnavailable)
    assert result.missing == ("citations",)
    assert facts_for_file(p6_conn, request.file_id, request.content_hash) == []


def test_contradicts_none_is_not_treated_as_no_conflict(subject_file, p6_conn):
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

    proposal = _proposal(subject_file, value="ECON 1010")
    result = _validate(
        p6_conn, request, proposal,
        dependencies=_deps(contradicts=lambda *a, **k: None),
    )
    assert not isinstance(result, P8Verdict) or result.outcome != ACCEPT_DIRECT
    assert isinstance(result, ValidationUnavailable)
    assert result.missing == ("contradicts",)
    subjects = [
        row for row in facts_for_file(p6_conn, file_id, content_hash)
        if row["field_key"] == "subject"
    ]
    assert [row["canonical_value"] for row in subjects] == ["BUSIB 4300"]


# --- R3: a Site A verdict is addressed to the dossier it judged ------------------


def test_site_a_verdict_carries_the_dossier_id_not_the_file_id(p6_conn, subject_file):
    """SPEC's verdict record is `verdict_id, dossier_id, claim_ref`.

    `dossier_id=request.file_id` put a P6 file id in a P8 dossier address field, so
    a verdict could not say which dossier it judged and two dossiers over one file
    were indistinguishable.
    """
    request = _request(p6_conn, subject_file)
    verdict = _validate(
        p6_conn, request, _proposal(subject_file),
        dossier=_released_dossier(request, dossier_id="dossier-address-1"),
    )
    assert verdict.dossier_id == "dossier-address-1"
    assert verdict.dossier_id != request.file_id


def test_two_dossiers_over_one_file_do_not_collide_on_verdict_id(p6_conn, subject_file):
    """`verdict_id` is a PRIMARY KEY; `file_id:field_key` repeats on re-validation."""
    request = _request(p6_conn, subject_file)
    first = _validate(
        p6_conn, request, _proposal(subject_file),
        dossier=_released_dossier(request, dossier_id="dossier-address-1"),
    )
    second = _validate(
        p6_conn, request, _proposal(subject_file),
        dossier=_released_dossier(request, dossier_id="dossier-address-2"),
    )
    assert first.verdict_id != second.verdict_id


def test_validate_fact_proposal_requires_the_dossier_it_judged(p6_conn, subject_file):
    """A bare `dossier_id` could not be checked against anything. The dossier is
    the authority for both the address and what was released, and it has no
    default: a Site A call with no dossier is `ValidationUnavailable`, never a
    pass."""
    parameters = inspect.signature(validate_fact_proposal).parameters
    assert "dossier_id" not in parameters
    for name in ("dossier", "citations", "evidence_resolver",
                 "apply_consequence"):
        assert parameters[name].kind is inspect.Parameter.KEYWORD_ONLY, name
        assert parameters[name].default is inspect.Parameter.empty, name

    request = _request(p6_conn, subject_file)
    result = validate_fact_proposal(
        p6_conn, request, _proposal(subject_file), dependencies=_deps(),
        model_identifier=MODEL, prompt_fingerprint=PROMPT, policy_version=POLICY,
        dossier=None, citations=(), evidence_resolver=lambda key: "x",
        apply_consequence=True,
    )
    assert isinstance(result, ValidationUnavailable)
    assert result.missing == ("dossier",)
    assert facts_for_file(p6_conn, request.file_id, request.content_hash) == []


# --- Site A's citations are bound to what P7 released ----------------------------
#
# `195da8c` split the two citation sources for sites B-E: the released dossier
# excerpt matches the span, the store only confirms the key still resolves. Site A
# never went through `_check_citation` at all -- it took `citable_observations`
# from P6's `FactRequest`, which is every observation for the file version, and
# synthesised `span_matched` as a copy of `resolved`. A model citing a key P7
# withheld, with a span it invented, was accepted and the fact was written.


def _site_a_dossier(*, evidence_items, released_evidence, allowed=("subject",),
                    dossier_id=DOSSIER, subject_ref="file-1"):
    from llm_harness.records import Dossier
    from llm_harness.vocabulary import A_FACT, REDUCTION_NONE, REMAINS_AMBIGUOUS

    return Dossier(
        dossier_id=dossier_id,
        call_site=A_FACT,
        subject_ref=subject_ref,
        eligibility_reason=REMAINS_AMBIGUOUS,
        plan_version=None,
        policy_version=POLICY,
        allowed_vocabulary=allowed,
        evidence_items=evidence_items,
        conflicts=(),
        released_evidence=released_evidence,
        max_dossier_tokens=4000,
        reduction_rung=REDUCTION_NONE,
        release_id="rel-1",
    )


def _item(key):
    from llm_harness.records import EvidenceItem
    from llm_harness.vocabulary import DIRECT_ANCHOR

    return EvidenceItem(
        evidence_ref=key, kind="excerpt", location="heading",
        excerpt_span=(0, 10), reliability_state="direct", basis=DIRECT_ANCHOR,
    )


def _release(key, value):
    from llm_harness.records import ReleasedEvidence

    return ReleasedEvidence(
        observation_key=key, address="0:10", value=value, zone="heading",
        context_before=None, context_after=None, context_truncated=False,
    )


def _claim_bytes(key, span):
    return json.dumps({"claims": [{
        "claim_ref": "c1",
        "payload": {"field": "subject", "value": "BUSIB 4300"},
        "citations": [{
            "evidence_ref": key, "cited_span": span,
            "why_it_supports": "names the subject",
        }],
    }]}, separators=(",", ":")).encode("utf-8")


@pytest.fixture()
def two_observations(p6_conn, tmp_path):
    """One observation P7 released, one it withheld. Both are P6-citable."""
    file_id, content_hash = _record(
        p6_conn, tmp_path, name="Syllabus.pdf",
        body=b"BUSIB 4300 Syllabus, Spring 2026")
    released = _observe(
        p6_conn, run_id="r-1", file_id=file_id, content_hash=content_hash,
        raw="BUSIB 4300", label="heading")
    withheld = _observe(
        p6_conn, run_id="r-2", file_id=file_id, content_hash=content_hash,
        raw="Prof. Jane Roe", label="instructor")
    assert released != withheld
    return file_id, content_hash, released, withheld


def _dispatch_site_a(conn, dossier, response_bytes, request):
    from llm_harness.sites import FactSiteDependencies, SiteDependencies, dispatch

    return dispatch(
        conn, dossier, response_bytes,
        site_dependencies=SiteDependencies(
            fact=FactSiteDependencies(
                fact_request=request, fact_dependencies=_deps()),
            placement=None, residual=None, template=None,
        ),
        evidence_resolver=lambda key: "BUSIB 4300",
        contradicts=_never_contradicts,
        model_id=MODEL, prompt_fingerprint=PROMPT, dossier_builder="fixture",
        release_audit_id=17, policy_version=POLICY, apply_consequence=True,
    )


def _only_verdict(result):
    assert not isinstance(result, ValidationUnavailable), result
    verdicts, _report = result
    assert len(verdicts) == 1, verdicts
    return verdicts[0]


def test_site_a_rejects_a_citation_to_an_observation_p7_withheld(
    p6_conn, two_observations,
):
    """P6 says the key is citable. P7 did not release it. The model never saw it."""
    from llm_harness.vocabulary import CITATION_NOT_IN_DOSSIER

    file_id, content_hash, released, withheld = two_observations
    request = build_request(
        p6_conn, file_id=file_id, content_hash=content_hash,
        activation_signals=_signals("academic"),
        normalizers={"subject": _boom_normalizer})
    assert withheld in {o.observation_key for o in request.citable_observations}

    dossier = _site_a_dossier(
        evidence_items=(_item(released),),
        released_evidence=(_release(released, "BUSIB 4300"),),
        subject_ref=file_id,
    )
    verdict = _only_verdict(_dispatch_site_a(
        p6_conn, dossier, _claim_bytes(withheld, "Prof. Jane Roe"), request))

    assert verdict.outcome == REJECT
    assert CITATION_NOT_IN_DOSSIER in verdict.reasons
    assert verdict.may_propose is False
    assert facts_for_file(p6_conn, file_id, content_hash) == []


def test_site_a_rejects_a_span_that_is_not_in_the_released_value(
    p6_conn, two_observations,
):
    """A real released key quoted with text the release does not contain."""
    from llm_harness.vocabulary import CITATION_SPAN_MISMATCH

    file_id, content_hash, released, _withheld = two_observations
    request = build_request(
        p6_conn, file_id=file_id, content_hash=content_hash,
        activation_signals=_signals("academic"),
        normalizers={"subject": _boom_normalizer})
    dossier = _site_a_dossier(
        evidence_items=(_item(released),),
        released_evidence=(_release(released, "BUSIB 4300"),),
        subject_ref=file_id,
    )
    verdict = _only_verdict(_dispatch_site_a(
        p6_conn, dossier, _claim_bytes(released, "ECON 1105"), request))

    assert verdict.outcome == REJECT
    assert CITATION_SPAN_MISMATCH in verdict.reasons
    assert facts_for_file(p6_conn, file_id, content_hash) == []


def test_site_a_span_matching_source_is_the_release_and_not_the_store(
    p6_conn, two_observations,
):
    """With redaction on, the store holds the raw text and the model saw the
    redacted one. Matching against the store accepts a quotation the model could
    not have read, and rejects the one it did."""
    from llm_harness.vocabulary import CITATION_SPAN_MISMATCH

    file_id, content_hash, released, _withheld = two_observations
    request = build_request(
        p6_conn, file_id=file_id, content_hash=content_hash,
        activation_signals=_signals("academic"),
        normalizers={"subject": _boom_normalizer})
    dossier = _site_a_dossier(
        evidence_items=(_item(released),),
        released_evidence=(_release(released, "[REDACTED] 4300"),),
        subject_ref=file_id,
    )
    quoting_the_store = _only_verdict(_dispatch_site_a(
        p6_conn, dossier, _claim_bytes(released, "BUSIB 4300"), request))
    assert quoting_the_store.outcome == REJECT
    assert CITATION_SPAN_MISMATCH in quoting_the_store.reasons

    quoting_the_release = _only_verdict(_dispatch_site_a(
        p6_conn, dossier, _claim_bytes(released, "[REDACTED] 4300"), request))
    assert quoting_the_release.outcome == ACCEPT_DIRECT


def test_site_a_records_a_real_span_result_and_not_a_copy_of_resolved(
    p6_conn, two_observations,
):
    """`span_matched` was `resolved` under another name, so no span was ever
    compared. A resolved key with a bad span must differ on the two flags."""
    file_id, content_hash, released, _withheld = two_observations
    request = build_request(
        p6_conn, file_id=file_id, content_hash=content_hash,
        activation_signals=_signals("academic"),
        normalizers={"subject": _boom_normalizer})
    dossier = _site_a_dossier(
        evidence_items=(_item(released),),
        released_evidence=(_release(released, "BUSIB 4300"),),
        subject_ref=file_id,
    )
    verdict = _only_verdict(_dispatch_site_a(
        p6_conn, dossier, _claim_bytes(released, "ECON 1105"), request))
    checked = verdict.citations_checked[0]
    assert checked.resolved is True
    assert checked.span_matched is False


def test_site_a_still_writes_the_fact_when_the_citation_is_grounded(
    p6_conn, two_observations,
):
    file_id, content_hash, released, _withheld = two_observations
    request = build_request(
        p6_conn, file_id=file_id, content_hash=content_hash,
        activation_signals=_signals("academic"),
        normalizers={"subject": _boom_normalizer})
    dossier = _site_a_dossier(
        evidence_items=(_item(released),),
        released_evidence=(_release(released, "BUSIB 4300"),),
        subject_ref=file_id,
    )
    verdict = _only_verdict(_dispatch_site_a(
        p6_conn, dossier, _claim_bytes(released, "BUSIB 4300"), request))
    assert verdict.outcome == ACCEPT_DIRECT
    assert [row["field_key"] for row in facts_for_file(
        p6_conn, file_id, content_hash)] == ["subject"]


def test_two_citation_shapes_that_disagree_are_unavailable(p6_conn, two_observations):
    """P6's `Proposal` carries bare keys and cannot carry a span, so Site A hands
    both shapes down. Two lists built from one claim that name different keys are
    two answers to the same question, and whichever one the release check reads
    would be checking a different citation from the one P6 records."""
    from llm_harness.records import Citation

    file_id, content_hash, released, withheld = two_observations
    request = build_request(
        p6_conn, file_id=file_id, content_hash=content_hash,
        activation_signals=_signals("academic"),
        normalizers={"subject": _boom_normalizer})
    dossier = _released_dossier(request)
    proposal = Proposal(
        field_key="subject", value="BUSIB 4300", citations=(released,),
        unknown=False)

    result = _validate(
        p6_conn, request, proposal, dossier=dossier,
        citations=(Citation(
            evidence_ref=withheld, cited_span="Prof. Jane Roe",
            metadata_field_name=None, why_it_supports="fixture"),),
    )
    assert isinstance(result, ValidationUnavailable)
    assert result.missing == ("citations",)
    assert facts_for_file(p6_conn, file_id, content_hash) == []


def test_a_citation_that_is_not_a_p8_record_is_unavailable(p6_conn, two_observations):
    file_id, content_hash, released, _withheld = two_observations
    request = build_request(
        p6_conn, file_id=file_id, content_hash=content_hash,
        activation_signals=_signals("academic"),
        normalizers={"subject": _boom_normalizer})
    proposal = Proposal(
        field_key="subject", value="BUSIB 4300", citations=(released,),
        unknown=False)
    result = _validate(
        p6_conn, request, proposal, citations=(released,),
    )
    assert isinstance(result, ValidationUnavailable)
    assert result.missing == ("citations",)


# --- the dossier and the P6 request must describe the same file ------------------


def test_a_dossier_for_one_file_cannot_write_a_fact_onto_another(
    p6_conn, two_observations, tmp_path,
):
    """The model's closed world is the dossier. The consequence lands wherever
    the `FactRequest` points, and nothing checked that they agree -- so a dossier
    describing one file wrote a fact onto a different file, cited to observations
    the second file never had.
    """
    file_id, content_hash, released, _withheld = two_observations
    other_id, other_hash = _record(
        p6_conn, tmp_path, name="Other.pdf", body=b"ECON 1105 Syllabus")
    assert other_id != file_id

    request = build_request(
        p6_conn, file_id=other_id, content_hash=other_hash,
        activation_signals=_signals("academic"),
        normalizers={"subject": _boom_normalizer})
    dossier = _site_a_dossier(
        evidence_items=(_item(released),),
        released_evidence=(_release(released, "BUSIB 4300"),),
        subject_ref=file_id,
    )
    assert dossier.subject_ref != request.file_id

    result = _validate(
        p6_conn, request,
        Proposal(field_key="subject", value="BUSIB 4300",
                 citations=(released,), unknown=False),
        dossier=dossier,
    )
    assert isinstance(result, ValidationUnavailable)
    assert result.missing == ("subject_ref",)
    assert facts_for_file(p6_conn, other_id, other_hash) == []
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    assert _reasons(p6_conn, request) == []


def test_a_dossier_whose_subject_is_the_request_file_is_validated(
    p6_conn, two_observations,
):
    file_id, content_hash, released, _withheld = two_observations
    request = build_request(
        p6_conn, file_id=file_id, content_hash=content_hash,
        activation_signals=_signals("academic"),
        normalizers={"subject": _boom_normalizer})
    dossier = _site_a_dossier(
        evidence_items=(_item(released),),
        released_evidence=(_release(released, "BUSIB 4300"),),
        subject_ref=file_id,
    )
    verdict = _validate(
        p6_conn, request,
        Proposal(field_key="subject", value="BUSIB 4300",
                 citations=(released,), unknown=False),
        dossier=dossier,
    )
    assert verdict.outcome == ACCEPT_DIRECT


# --- replay validates; it does not append a second P6 consequence ---------------


def test_replay_validates_without_appending_a_second_p6_consequence(
    p6_conn, two_observations,
):
    """`write_unresolved` is always an INSERT, never de-duplicated. Re-validating
    the same stored bytes wrote a second `unresolved` row saying the model had
    declined twice, for one thing it declined once."""
    file_id, content_hash, released, _withheld = two_observations
    request = build_request(
        p6_conn, file_id=file_id, content_hash=content_hash,
        activation_signals=_signals("academic"),
        normalizers={"subject": _boom_normalizer})
    dossier = _site_a_dossier(
        evidence_items=(_item(released),),
        released_evidence=(_release(released, "BUSIB 4300"),),
        subject_ref=file_id,
    )
    unknown = Proposal(
        field_key="subject", value=None, citations=(), unknown=True)

    live = _validate(p6_conn, request, unknown, dossier=dossier)
    assert live.outcome == ABSTAIN
    assert _reasons(p6_conn, request) == ["model_returned_unknown"]

    replayed = validate_fact_proposal(
        p6_conn, request, unknown, dependencies=_deps(),
        model_identifier=MODEL, prompt_fingerprint=PROMPT,
        policy_version=POLICY, dossier=dossier, citations=(),
        evidence_resolver=lambda key: "the store still holds it",
        apply_consequence=False,
    )
    assert replayed.outcome == ABSTAIN
    assert replayed.verdict_id == live.verdict_id
    assert _reasons(p6_conn, request) == ["model_returned_unknown"]


def test_applying_the_consequence_is_an_explicit_decision(p6_conn, subject_file):
    """No default. A caller that does not say which it is gets a TypeError, not a
    silent P6 write."""
    parameters = inspect.signature(validate_fact_proposal).parameters
    assert parameters["apply_consequence"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parameters["apply_consequence"].default is inspect.Parameter.empty


# --- one verdict record per claim, at Site A too ---------------------------------


def _claims_bytes(*claims):
    return json.dumps({"claims": list(claims)}, separators=(",", ":")).encode("utf-8")


def _claim(field, value, key, span):
    return {
        "claim_ref": field,
        "payload": {"field": field, "value": value},
        "citations": [{
            "evidence_ref": key, "cited_span": span,
            "why_it_supports": f"names the {field}",
        }],
    }


def test_site_a_validates_every_claim_and_not_only_the_first(
    p6_conn, two_observations,
):
    """SPEC: *"One verdict record per claim."* Site A required exactly one and
    discarded anything else as schema-invalid -- a well-formed two-field response
    became one REJECT, `apply_verdict` was never called, and P6 recorded neither a
    fact nor an `unresolved` row for either field. The model's whole answer
    vanished, and the one-claim rule was P8's, not the injected schema's.
    """
    file_id, content_hash, released, withheld = two_observations
    request = build_request(
        p6_conn, file_id=file_id, content_hash=content_hash,
        activation_signals=_signals("academic"),
        normalizers={"subject": _boom_normalizer})
    dossier = _site_a_dossier(
        evidence_items=(_item(released), _item(withheld)),
        released_evidence=(
            _release(released, "BUSIB 4300"),
            _release(withheld, "Prof. Jane Roe"),
        ),
        allowed=tuple(request.allowlist),
        subject_ref=file_id,
    )
    result = _dispatch_site_a(
        p6_conn, dossier,
        _claims_bytes(
            _claim("subject", "BUSIB 4300", released, "BUSIB 4300"),
            _claim("instructor", "Prof. Jane Roe", withheld, "Prof. Jane Roe"),
        ),
        request,
    )
    assert not isinstance(result, ValidationUnavailable), result
    verdicts, report = result
    assert [v.claim_ref for v in verdicts] == ["subject", "instructor"]
    assert [v.outcome for v in verdicts] == [ACCEPT_DIRECT, ACCEPT_DIRECT]
    assert len({v.verdict_id for v in verdicts}) == 2
    assert sorted(row["field_key"] for row in facts_for_file(
        p6_conn, file_id, content_hash)) == ["instructor", "subject"]
    assert report.claims_total == 2


def test_site_a_records_each_claim_of_a_mixed_response(p6_conn, two_observations):
    """One accepted, one rejected. Both reach P6, with their own reasons."""
    from llm_harness.vocabulary import CITATION_SPAN_MISMATCH

    file_id, content_hash, released, withheld = two_observations
    request = build_request(
        p6_conn, file_id=file_id, content_hash=content_hash,
        activation_signals=_signals("academic"),
        normalizers={"subject": _boom_normalizer})
    dossier = _site_a_dossier(
        evidence_items=(_item(released), _item(withheld)),
        released_evidence=(
            _release(released, "BUSIB 4300"),
            _release(withheld, "Prof. Jane Roe"),
        ),
        allowed=tuple(request.allowlist),
        subject_ref=file_id,
    )
    verdicts, _report = _dispatch_site_a(
        p6_conn, dossier,
        _claims_bytes(
            _claim("subject", "BUSIB 4300", released, "BUSIB 4300"),
            _claim("instructor", "Dr Nobody", withheld, "Dr Nobody"),
        ),
        request,
    )
    assert [v.outcome for v in verdicts] == [ACCEPT_DIRECT, REJECT]
    assert CITATION_SPAN_MISMATCH in verdicts[1].reasons
    assert [row["field_key"] for row in facts_for_file(
        p6_conn, file_id, content_hash)] == ["subject"]
    assert _reasons(p6_conn, request, "instructor") == [
        "citation_absent_from_evidence"]


def test_two_claims_about_one_field_are_schema_invalid(p6_conn, two_observations):
    """`claim_ref` is what tells two verdicts apart, and Site A's is the field key.
    Two claims about one field are indistinguishable, and P8 does not choose which
    of the model's two answers it meant."""
    from llm_harness.vocabulary import SCHEMA_INVALID

    file_id, content_hash, released, _withheld = two_observations
    request = build_request(
        p6_conn, file_id=file_id, content_hash=content_hash,
        activation_signals=_signals("academic"),
        normalizers={"subject": _boom_normalizer})
    dossier = _site_a_dossier(
        evidence_items=(_item(released),),
        released_evidence=(_release(released, "BUSIB 4300"),),
        allowed=tuple(request.allowlist),
        subject_ref=file_id,
    )
    verdicts, _report = _dispatch_site_a(
        p6_conn, dossier,
        _claims_bytes(
            _claim("subject", "BUSIB 4300", released, "BUSIB 4300"),
            _claim("subject", "ECON 1105", released, "BUSIB 4300"),
        ),
        request,
    )
    assert len(verdicts) == 1
    assert SCHEMA_INVALID in verdicts[0].reasons
    assert facts_for_file(p6_conn, file_id, content_hash) == []


def test_a_response_with_no_claims_at_all_is_schema_invalid(p6_conn, two_observations):
    from llm_harness.vocabulary import SCHEMA_INVALID

    file_id, content_hash, released, _withheld = two_observations
    request = build_request(
        p6_conn, file_id=file_id, content_hash=content_hash,
        activation_signals=_signals("academic"),
        normalizers={"subject": _boom_normalizer})
    dossier = _site_a_dossier(
        evidence_items=(_item(released),),
        released_evidence=(_release(released, "BUSIB 4300"),),
        allowed=tuple(request.allowlist), subject_ref=file_id,
    )
    verdicts, _report = _dispatch_site_a(
        p6_conn, dossier, _claims_bytes(), request)
    assert len(verdicts) == 1
    assert SCHEMA_INVALID in verdicts[0].reasons
