# tests/p6/test_p6_llm_seam.py
"""O6 -- Done-means 11 and 12. What P6 hands P8, and the consequence of each verdict."""
from __future__ import annotations

import ast
import dataclasses
import importlib
import inspect
import json
import pkgutil
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.canonical import canonical_json
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from evidence_shape.vocabulary import ANALYSIS_TIERS, NotInVocabulary

import facts
from facts import llm_seam
from facts.cache import fact_cache_key
from facts.domains import ActivationSignal, ActivationSignals, active_field_allowlist
from facts.fields import FieldNotInCatalogue
from facts.file_facts import LLM_INTERPRETATION, RULE, facts_for_file, write_fact
from facts.llm_seam import (
    CHECK_REASONS, FOUR_CHECKS, LLM_STATES, UNKNOWN_REASON, FactRequest, Proposal,
    ProposalStateRefused, Verdict, apply_verdict, build_request, require_llm_state,
)
from facts.states import DIRECT, POSSIBLE, REJECTED, VALIDATED
from facts.unresolved import UNRESOLVED_REASONS, unresolved_for_file
from facts.values import VALUE_ORIGINS, ensure_value

CLOCK = "2026-08-19T12:00:00+00:00"
MODEL = "test-model-1"
PROMPT = "sha256:prompt-fingerprint"

#: Task 13 owns activation and P6 authors no signal, so the test injects its own. The
#: academic schema is the one that carries `subject`; without it in the allowlist the
#: worked case of §3.2 is not reachable and the seam has nothing to hand P8.
def _signals(*schema_ids: str) -> ActivationSignals:
    return ActivationSignals(signals=tuple(
        ActivationSignal(schema_id=schema_id, activates=lambda rows: True)
        for schema_id in schema_ids))


#: The per-field normalizers the request CARRIES. P6 authors none of their contents:
#: "Per-field normalizers and alias tables" is a Deferred row, and `U Chicago ->
#: University of Chicago -> UChicago` is "one worked example, not a table".
NORMALIZERS = {"subject": lambda raw: raw.strip()}


def _code_strings(module) -> set[str]:
    """Every string literal in a module that is NOT a docstring.

    A raw source-text search matches comments and docstrings; the preamble records
    that scanning text for a token has produced a false result on this project nine
    times. This reads the code.
    """
    tree = ast.parse(inspect.getsource(module))
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
    return {node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and id(node) not in docstrings}


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
def subject_file(p6_conn, tmp_path):
    """One file with one citable heading observation."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                                    body=b"BUSIB 4300 Syllabus, Spring 2026")
    key = _observe(p6_conn, run_id="r-1", file_id=file_id,
                   content_hash=content_hash, raw="BUSIB 4300")
    return file_id, content_hash, key


def _fact(conn, *, file_id, content_hash, field_key, value, key, state,
          active=True, cache_key="sha256:the-native-pass-slot"):
    value_id = ensure_value(conn, field_key=field_key, canonical_value=value,
                            first_evidence_ref=key, origin=VALUE_ORIGINS[0])
    return write_fact(conn, file_id=file_id, content_hash=content_hash,
                      field_key=field_key, value_id=value_id,
                      reliability_state=state, origin=RULE,
                      evidence_refs=(key,), cache_key=cache_key, active=active)


def _request(conn, subject_file) -> FactRequest:
    file_id, content_hash, _ = subject_file
    return build_request(conn, file_id=file_id, content_hash=content_hash,
                         activation_signals=_signals("academic"),
                         normalizers=NORMALIZERS)


def _apply(conn, request, proposal, verdict, *, state=LLM_STATES[0],
           canonical_value=None):
    # `canonical_value` is check 3's output and is now what gets STORED. These tests
    # are about the CONSEQUENCE of a verdict, not about canonicalisation, so the
    # default carries the proposal's own value through unchanged -- which is what
    # every one of them asserted before the value stopped being `proposal.value`.
    return apply_verdict(conn, request=request, proposal=proposal, verdict=verdict,
                         proposal_state=state, model_identifier=MODEL,
                         prompt_fingerprint=PROMPT,
                         canonical_value=(proposal.value
                                          if canonical_value is None
                                          else canonical_value))


def _reasons(conn, request, field_key=None):
    return [r["reason"] for r in unresolved_for_file(
        conn, request.file_id, request.content_hash, field_key=field_key)]


# --- the four inputs -----------------------------------------------------------

def test_the_request_carries_the_four_inputs_and_nothing_else(subject_file, p6_conn):
    # O6. The four are the active field allowlist, the citable observation set, the
    # existing stronger facts, and the per-field normalizers.
    file_id, content_hash, key = subject_file
    request = _request(p6_conn, subject_file)
    assert [f.name for f in dataclasses.fields(FactRequest)] == [
        "file_id", "content_hash", "allowlist", "citable_observations",
        "existing_facts", "normalizers"]
    assert request.file_id == file_id and request.content_hash == content_hash
    assert "subject" in request.allowlist
    assert [one.observation_key for one in request.citable_observations] == [key]
    assert request.normalizers is NORMALIZERS
    assert request.existing_facts == ()


def test_the_allowlist_is_task_thirteens_and_not_a_second_computation(
        subject_file, p6_conn):
    # §3.5: the model "may extract only fields allowed by the relevant schema". The
    # skeleton requires that to be ONE computation, so the request holds Task 13's
    # answer rather than a second reading of the catalogue.
    file_id, content_hash, _ = subject_file
    signals = _signals("academic")
    request = build_request(p6_conn, file_id=file_id, content_hash=content_hash,
                            activation_signals=signals, normalizers=NORMALIZERS)
    assert request.allowlist == active_field_allowlist(
        p6_conn, file_id=file_id, content_hash=content_hash,
        activation_signals=signals)
    # And it is genuinely narrower than the catalogue: `event` is the photos schema's
    # and no signal activated it, so check 1 has something to fail on.
    assert "event" not in request.allowlist


def test_the_request_carries_the_stronger_facts_a_contradiction_check_needs(
        subject_file, p6_conn):
    # §3.6 check 4: "no stronger direct or rule-validated fact contradicts it". P6
    # supplies the facts; whether one CONTRADICTS is not computed here (see C-5).
    file_id, content_hash, key = subject_file
    _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="subject",
          value="BUSIB 4300", key=key, state=VALIDATED)
    request = _request(p6_conn, subject_file)
    assert [r["reliability_state"] for r in request.existing_facts] == [VALIDATED]


def test_only_active_ranked_facts_stronger_than_an_llm_conclusion_are_carried(
        subject_file, p6_conn):
    # Three exclusions, each with its own reason to exist:
    #   - `possible` is not stronger than `llm_supported`, so it is not check 4's input
    #   - an inactive fact is not a live claim
    #   - `rejected` is §3.13's EXCLUSION, not a rank: `strength` raises on it, so a
    #     comparison-first filter would end the whole pass with a vocabulary error.
    file_id, content_hash, key = subject_file
    _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="subject",
          value="BUSIB 4300", key=key, state=DIRECT)
    _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="school",
          value="Weak", key=key, state=POSSIBLE, cache_key="sha256:slot-b")
    _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="term",
          value="Retired", key=key, state=VALIDATED, active=False,
          cache_key="sha256:slot-c")
    _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="instructor",
          value="Wrong Person", key=key, state=REJECTED, cache_key="sha256:slot-d")
    request = _request(p6_conn, subject_file)
    assert [(r["field_key"], r["reliability_state"])
            for r in request.existing_facts] == [("subject", DIRECT)]


# --- the four failing verdicts -------------------------------------------------

def test_a_citation_absent_from_evidence_produces_no_fact(subject_file, p6_conn):
    # Done-means 11, and §3.6 check 2.
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="BUSIB 4300",
                        citations=("sha256:" + "b" * 64,), unknown=False)   # well-formed, absent
    verdict = Verdict(passed=False, failed_check=FOUR_CHECKS[1])
    assert _apply(p6_conn, request, proposal, verdict) is None
    assert facts_for_file(p6_conn, request.file_id, request.content_hash) == []
    assert _reasons(p6_conn, request) == ["citation_absent_from_evidence"]


def test_a_field_outside_the_active_schema_produces_no_fact(subject_file, p6_conn):
    # Done-means 11, and §3.6 check 1.
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="event", value="Graduation",
                        citations=(subject_file[2],), unknown=False)
    verdict = Verdict(passed=False, failed_check=FOUR_CHECKS[0])
    assert _apply(p6_conn, request, proposal, verdict) is None
    assert facts_for_file(p6_conn, request.file_id, request.content_hash) == []
    assert _reasons(p6_conn, request) == ["field_not_in_active_schema"]


def test_a_proposal_contradicted_by_a_stronger_fact_produces_no_fact(
        subject_file, p6_conn):
    # Done-means 11, and §3.6 check 4. The stronger fact is real and is in the
    # request; the VERDICT is the fixture, because P6 owns no contradiction oracle.
    file_id, content_hash, key = subject_file
    _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="subject",
          value="BUSIB 4300", key=key, state=VALIDATED)
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="ECON 1010",
                        citations=(key,), unknown=False)
    verdict = Verdict(passed=False, failed_check=FOUR_CHECKS[3])
    assert _apply(p6_conn, request, proposal, verdict) is None
    subjects = [r for r in facts_for_file(p6_conn, file_id, content_hash)
                if r["field_key"] == "subject"]
    assert [r["canonical_value"] for r in subjects] == ["BUSIB 4300"]
    assert _reasons(p6_conn, request) == ["contradicted_by_stronger_fact"]


def test_a_value_that_cannot_be_normalized_produces_no_fact(subject_file, p6_conn):
    # §3.6 check 3: "that the proposed value can be normalized safely".
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="  ??  ",
                        citations=(subject_file[2],), unknown=False)
    verdict = Verdict(passed=False, failed_check=FOUR_CHECKS[2])
    assert _apply(p6_conn, request, proposal, verdict) is None
    assert facts_for_file(p6_conn, request.file_id, request.content_hash) == []
    assert _reasons(p6_conn, request) == ["normalization_failed"]


def test_an_explicit_unknown_is_the_model_declining_and_not_a_failed_check(
        subject_file, p6_conn):
    # §3.6: "A model that cannot cite sufficient evidence must return unknown."
    # Nothing was validated, so no verdict is consulted -- a PASSING verdict here
    # still produces the abstention rather than a fact.
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value=None, citations=(), unknown=True)
    assert _apply(p6_conn, request, proposal,
                  Verdict(passed=True, failed_check=None)) is None
    assert facts_for_file(p6_conn, request.file_id, request.content_hash) == []
    assert _reasons(p6_conn, request) == [UNKNOWN_REASON]
    assert UNKNOWN_REASON == "model_returned_unknown"
    # And "declined" and "proposed" cannot both be true of one record.
    with pytest.raises(ValueError):
        Proposal(field_key="subject", value="BUSIB 4300",
                 citations=("sha256:x",), unknown=True)
    with pytest.raises(ValueError):
        Proposal(field_key="subject", value=None, citations=(), unknown=False)


def test_five_verdicts_have_five_distinct_reasons_and_no_shared_bucket():
    assert FOUR_CHECKS == ("field_in_active_schema", "citation_present_in_evidence",
                           "value_normalizes_safely", "no_stronger_fact_contradicts")
    assert tuple(CHECK_REASONS[check] for check in FOUR_CHECKS) == (
        "field_not_in_active_schema", "citation_absent_from_evidence",
        "normalization_failed", "contradicted_by_stronger_fact")
    reasons = set(CHECK_REASONS.values()) | {UNKNOWN_REASON}
    assert len(reasons) == 5
    assert "rejected" not in reasons
    # Every one is a member of Task 5's closed vocabulary, so P6 has one reason set
    # and this module did not open a second.
    assert reasons <= set(UNRESOLVED_REASONS)
    # The reason follows from the check; P8 does not spell a member of P6's
    # vocabulary, and a check outside the four is refused rather than stored.
    assert Verdict(passed=False, failed_check=FOUR_CHECKS[2]).reason == (
        "normalization_failed")
    with pytest.raises(NotInVocabulary):
        Verdict(passed=False, failed_check="vibes")
    with pytest.raises(ValueError):
        Verdict(passed=True, failed_check=FOUR_CHECKS[0])
    with pytest.raises(ValueError):
        Verdict(passed=False, failed_check=None)


# --- the two passing outcomes --------------------------------------------------

def test_a_passing_verdict_writes_one_llm_supported_fact(subject_file, p6_conn):
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="BUSIB 4300",
                        citations=(subject_file[2],), unknown=False)
    fact_id = _apply(p6_conn, request, proposal, Verdict(passed=True))
    assert fact_id is not None
    rows = [r for r in facts_for_file(p6_conn, request.file_id,
                                      request.content_hash)
            if r["field_key"] == "subject"]
    assert len(rows) == 1
    assert rows[0]["reliability_state"] == LLM_STATES[0] == "llm_supported"
    assert rows[0]["origin"] == LLM_INTERPRETATION
    assert json.loads(rows[0]["evidence_refs"]) == [subject_file[2]]
    assert unresolved_for_file(p6_conn, request.file_id,
                               request.content_hash) == []


def test_a_useful_but_too_weak_proposal_is_possible_and_never_proposal_eligible(
        subject_file, p6_conn):
    # Done-means 12. §3.6: it "may remain a possible clue for review; it must not
    # quietly become a folder proposal or an asserted file property". The exclusion
    # IS the state -- §3.6's proposal-eligible read drops `possible` -- so there is no
    # second switch and nothing to remember to turn off.
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="BUSIB 4300",
                        citations=(subject_file[2],), unknown=False)
    assert _apply(p6_conn, request, proposal, Verdict(passed=True),
                  state=LLM_STATES[1]) is not None
    rows = [r for r in facts_for_file(p6_conn, request.file_id,
                                      request.content_hash)
            if r["field_key"] == "subject"]
    assert [r["reliability_state"] for r in rows] == [POSSIBLE]
    read_surface = pytest.importorskip("facts.read_surface")
    eligible = read_surface.proposal_eligible(p6_conn, file_id=request.file_id,
                                              content_hash=request.content_hash)
    assert [r["field_key"] for r in eligible] == []


def test_no_code_path_can_write_an_llm_fact_at_another_state(subject_file, p6_conn):
    # §3.6's ceiling, attempted rather than inspected -- Task 15's `require_possible`
    # applied to the one other place a state ceiling binds.
    assert LLM_STATES == ("llm_supported", "possible")
    for state in LLM_STATES:
        assert require_llm_state(state) == state
    for state in ("validated", "direct", "user_confirmed", "rejected"):
        with pytest.raises(ProposalStateRefused):
            require_llm_state(state)
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="BUSIB 4300",
                        citations=(subject_file[2],), unknown=False)
    with pytest.raises(ProposalStateRefused):
        _apply(p6_conn, request, proposal, Verdict(passed=True), state="validated")
    # The gate runs before anything is written, so a refused promotion leaves no
    # fact row AND no value row behind.
    assert facts_for_file(p6_conn, request.file_id, request.content_hash) == []
    assert p6_conn.execute('SELECT COUNT(*) FROM "values"').fetchone()[0] == 0


def test_p6_owns_none_of_the_checking(subject_file, p6_conn):
    # O6, and the reason the seam is shaped this way: `apply_verdict` takes a
    # `Verdict` it did not compute, so a PASSING verdict over a proposal citing a key
    # that is not in the store still writes a fact. If P6 re-ran the check, P6 and P8
    # would each hold half a validator and they would drift.
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="ANYTHING",
                        citations=("sha256:" + "b" * 64,), unknown=False)   # well-formed, absent
    assert _apply(p6_conn, request, proposal, Verdict(passed=True)) is not None
    rows = [r for r in facts_for_file(p6_conn, request.file_id,
                                      request.content_hash)
            if r["field_key"] == "subject"]
    assert [r["canonical_value"] for r in rows] == ["ANYTHING"]


def test_the_closed_field_catalogue_is_the_one_floor_a_verdict_cannot_lift(
        subject_file, p6_conn):
    # §3.5: the LLM "is not allowed to invent a new fact schema, create an
    # unsupported field". That is not this module checking anything -- there is no row
    # to point at, so the write refuses.
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="vibe_score", value="9",
                        citations=(subject_file[2],), unknown=False)
    with pytest.raises(FieldNotInCatalogue):
        _apply(p6_conn, request, proposal, Verdict(passed=True))
    assert facts_for_file(p6_conn, request.file_id, request.content_hash) == []


# --- §3.4's five parts ---------------------------------------------------------

def test_the_llm_fact_lands_at_the_llm_tier_with_p8s_two_values(
        subject_file, p6_conn):
    # §3.4's five parts. P8's SPEC: "P8 computes and publishes the
    # `prompt_fingerprint` and `model_id` that P6's cache key requires; P6 owns
    # cache-key composition." Both are required keywords here.
    signature = inspect.signature(apply_verdict)
    for name in ("proposal_state", "model_identifier", "prompt_fingerprint"):
        parameter = signature.parameters[name]
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
        assert parameter.default is inspect.Parameter.empty
    file_id, content_hash, key = subject_file
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="BUSIB 4300",
                        citations=(key,), unknown=False)
    fact_id = _apply(p6_conn, request, proposal, Verdict(passed=True))
    row = [r for r in facts_for_file(p6_conn, file_id, content_hash)
           if r["fact_id"] == fact_id][0]

    versions = canonical_json([["pdf.text", "1.0.0"]])
    assert row["cache_key"] == fact_cache_key(
        content_hash=content_hash, extractor_version=versions,
        analysis_tier=ANALYSIS_TIERS[-1], model_identifier=MODEL,
        prompt_fingerprint=PROMPT)
    assert ANALYSIS_TIERS[-1] == "llm"
    # The deterministic fact over the SAME evidence is a different slot, which is why
    # re-resolution supersedes rather than overwrites (§8.2). Both halves matter: the
    # tier alone and the two model parts alone each move the key.
    assert row["cache_key"] != fact_cache_key(
        content_hash=content_hash, extractor_version=versions,
        analysis_tier="native", model_identifier=MODEL, prompt_fingerprint=PROMPT)
    assert row["cache_key"] != fact_cache_key(
        content_hash=content_hash, extractor_version=versions,
        analysis_tier=ANALYSIS_TIERS[-1], model_identifier=None,
        prompt_fingerprint=None)
    # §3.3: the two model parts are `None` on every deterministic fact and this is
    # the one exception, so the ROW carries P8's values and not only the digest.
    assert row["model_identifier"] == MODEL
    assert row["prompt_fingerprint"] == PROMPT


def test_an_abstention_and_a_fact_from_one_pass_share_one_cache_key(
        subject_file, p6_conn):
    # Preamble §3.2's deciding argument: "The fact and the abstention produced by one
    # pass share one key", so the same events invalidate both.
    file_id, content_hash, key = subject_file
    request = _request(p6_conn, subject_file)
    passing = Proposal(field_key="subject", value="BUSIB 4300",
                       citations=(key,), unknown=False)
    fact_id = _apply(p6_conn, request, passing, Verdict(passed=True))
    fact = [r for r in facts_for_file(p6_conn, file_id, content_hash)
            if r["fact_id"] == fact_id][0]
    failing = Proposal(field_key="school", value="Nowhere",
                       citations=(key,), unknown=False)
    assert _apply(p6_conn, request, failing,
                  Verdict(passed=False, failed_check=FOUR_CHECKS[2])) is None
    abstention = unresolved_for_file(p6_conn, file_id, content_hash)[0]
    assert abstention["cache_key"] == fact["cache_key"]


# --- the seam that must stay open ----------------------------------------------

def test_p6_publishes_neither_a_normalizer_nor_a_contradiction_oracle():
    """Round 4's C-5, pinned in code so the gap is visible from the repository.

    P8's SPEC names `normalize(field, raw_value) -> value | not_normalizable` and
    `contradicts(claim, existing_fact) -> bool` as things it receives FROM P6; P6's
    Task 17 says P6 owns none of the checking. Each part hands them to the other, so
    neither builds them. This task does not pick a side and does not invent them --
    it makes the day someone quietly adds one a failing test instead of a merge.
    """
    for owner in (llm_seam,):
        assert not hasattr(owner, "normalize")
        assert not hasattr(owner, "contradicts")
    for info in pkgutil.iter_modules(facts.__path__):
        module = importlib.import_module(f"facts.{info.name}")
        assert not hasattr(module, "normalize"), info.name
        assert not hasattr(module, "contradicts"), info.name


def test_the_whole_module_runs_with_p8_absent():
    # Done-means 17. No client, no model call, no configuration, no default
    # `propose`. Every verdict above was a hand-authored fixture.
    #
    # Asserted by introspection rather than by searching the source text: §3.6 is
    # quoted verbatim in the module docstring and contains the word "proposed", so a
    # raw `"propose" not in source` check would fail on the SPEC quotation while
    # saying nothing about the code. The preamble's own rule -- "a text search matches
    # comments and docstrings" -- settles which one this has to be.
    assert not hasattr(llm_seam, "propose")
    assert [name for name, value in vars(llm_seam).items()
            if callable(value) and "propose" in name] == []
    # No default is a callable, so no `propose` slipped in as a parameter default.
    for function in (build_request, apply_verdict, require_llm_state):
        for parameter in inspect.signature(function).parameters.values():
            if parameter.default is inspect.Parameter.empty:
                continue          # no default at all; `_empty` is itself callable
            assert not callable(parameter.default), parameter.name
    # Nothing outside the stdlib, P4's shape package and P6's own siblings is
    # imported -- a model client would have to arrive through one of these.
    tree = ast.parse(inspect.getsource(llm_seam))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported <= {"__future__", "sqlite3", "dataclasses", "typing",
                        "evidence_shape", "facts"}, sorted(imported)
    for banned in ("http", "openai", "anthropic", "urllib", "socket", "api_key"):
        assert [one for one in _code_strings(llm_seam)
                if banned in one.lower()] == [], banned


# --- the value that gets stored ---------------------------------------------------


@pytest.mark.xfail(strict=True, reason=(
    "The stored value is the model's spelling, not the normalized form. The fix "
    "is P8's, not P6's: `fact_validation` computes `normalize(field, raw)` for "
    "check 3 and DISCARDS it one line before calling `apply_verdict`. Passing it "
    "through changes a published signature between two parts, and "
    "`tests/integration/test_p8_p6_fact_seam.py:97` deliberately plants a "
    "throwing normalizer to assert P6 never calls `request.normalizers` itself -- "
    "so the obvious local fix is the one the design forbids. Owner-visible; "
    "recorded in `72` §15."))
def test_the_stored_value_is_the_normalized_one_not_the_models_spelling(
        subject_file, p6_conn):
    """§3.6 check 3 asks whether "the proposed value can be normalized safely".
    A pass therefore means a normal form EXISTS -- and the store recorded the
    model's spelling instead of it.

    `FactRequest.normalizers` was carried and never called. The consequence is the
    identity-splitting defect `65` §4.2 already cost this project four one-file
    groups from one course: `PHYS 1401` and `PHYS1401` become two `values` rows,
    two value ids, and two folders, because `ensure_value` derives the id from the
    string it is handed.

    The check and the write must agree about what the value IS. Validating one
    form and storing another is the same class of defect as measuring a model
    against one field list and judging it against a second.
    """
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="  PHYS1401  ",
                        citations=(subject_file[2],), unknown=False)

    fact_id = _apply(p6_conn, request, proposal, Verdict(passed=True))

    stored = p6_conn.execute(
        'SELECT v.canonical_value FROM file_facts f JOIN "values" v '
        "ON v.value_id = f.value_id WHERE f.fact_id = ?", (fact_id,)).fetchone()
    assert stored["canonical_value"] == "PHYS1401"


def test_a_field_with_no_normalizer_keeps_the_value_it_was_given(
        subject_file, p6_conn):
    """The twin, and the reason this is not P6 inventing a rule.

    `NORMALIZERS` is injected and P6 authors none of its contents -- per-field
    normalizers are a Deferred row, "one worked example, not a table". A field the
    deployment supplied no normalizer for is stored exactly as proposed, because
    the alternative is this module deciding what a normal form looks like for a
    field nobody has ruled on, which is what §3.5 forbids at the model's boundary.
    """
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="work_type", value="  Homework  ",
                        citations=(subject_file[2],), unknown=False)

    fact_id = _apply(p6_conn, request, proposal, Verdict(passed=True))

    stored = p6_conn.execute(
        'SELECT v.canonical_value FROM file_facts f JOIN "values" v '
        "ON v.value_id = f.value_id WHERE f.fact_id = ?", (fact_id,)).fetchone()
    assert stored["canonical_value"] == "  Homework  "
