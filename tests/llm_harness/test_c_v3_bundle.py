"""The Site C revision bundle of `104` R-126 / R-133, under `105` §14.1 and §14.6.

Three things are pinned here, with the deployment validator and the bench's own
cases and nothing scripted around them:

* the validator: a context-only placement with verified accepted-group support
  is accepted for review; an unverified one is refused; the two counts are
  recorded and never compared; the two-condition codes fire on what the
  validator can observe and on nothing else;
* the draft schema v2 (`tools/promptbench/drafts/`): the context-only shape is
  valid, an empty citations list with a direct level is not, every object is
  closed, and the decline shape is the 2026-09-06 one byte for byte;
* the ratified and unratified library files: eliminate-v2 and its schema are
  untouched -- the drafts live beside the library, not in it.

The draft text itself is checked the way `test_d2_draft_templates.py` will
check it once a manifest row names it: terminator, key line, no fence, no
provider names, no catalogue key in a worked example, and shapes that parse and
validate against schema v2 after instantiation on a bench case.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import jsonschema
import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from llm_harness.vocabulary import (  # noqa: E402
    ABSTAIN, ACCEPT_CONTEXT_SUPPORTED, ACCEPT_DIRECT, BELOW_SUPPORT_THRESHOLD,
    C_PLACEMENT, INSUFFICIENT_MARGIN, REJECT, SCHEMA_INVALID,
    SLOT_FILLED_WITHOUT_EVIDENCE, UNCITED_CLAIM, WEAK,
)
from llm_harness.wire_handles import wire_handle  # noqa: E402

from tools.promptbench.candidates import LIBRARY, MANIFEST  # noqa: E402
from tools.promptbench.dossiers import BENCH_HANDLE_KEY, dossier_of  # noqa: E402
from tools.promptbench.judge import (  # noqa: E402
    APPROPRIATE_ABSTENTION, CORRECT_PLACEMENT, INCORRECT_PLACEMENT, INVALID_OUTPUT,
    UNNECESSARY_ABSTENTION, expected_class, judge, outcome_class,
    site_dependencies_for,
)
from tools.promptbench.suites import cases_for  # noqa: E402
from tools.promptbench.suites.suite_c import ACTIVATION  # noqa: E402

DRAFTS = REPO / "tools" / "promptbench" / "drafts"
TEXT_V3 = DRAFTS / "c_placement_template.eliminate-v3.txt"
SCHEMA_V2 = DRAFTS / "c_placement_response_schema.v2.json"
SCHEMA_V1 = LIBRARY / "c_placement_response_schema.json"

CASES = {case.case_id: case for case in cases_for(C_PLACEMENT)}


def _schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _cite(case, index: int, span: str) -> dict:
    item = case.evidence[index]
    assert span in item.value, (span, item.value)
    return {"evidence_ref": wire_handle(item.key, key=BENCH_HANDLE_KEY),
            "cited_span": span, "why_it_supports": "the released text carries it"}


def _place(destination, levels, citations, *, alternatives=(), support=None,
           next_support=None, conflicts=()) -> bytes:
    payload = {"destination": destination, "per_dimension_support": list(levels),
               "alternatives": list(alternatives),
               "conflicts_considered": list(conflicts),
               "support": len(citations) if support is None else support,
               "next_support": 0 if next_support is None else next_support,
               "refinement": "not_applicable"}
    return json.dumps({"claims": [{"payload": payload,
                                   "citations": list(citations)}]}).encode()


def _decline(alternatives=()) -> bytes:
    return json.dumps({"claims": [{
        "payload": {"destination": "none", "alternatives": list(alternatives),
                    "conflicts_considered": []},
        "unknown": {"insufficiency_statement": "two candidates stood"}}]}).encode()


def _judge(case_id: str, response: bytes):
    case = CASES[case_id]
    return judge(case, dossier_of(case), response, schema=_schema(SCHEMA_V2),
                 site_dependencies=site_dependencies_for(case))


def _reasons(judgement) -> list[str]:
    return [r for v in judgement.verdicts for r in v["reasons"]]


def _context(dimension: str, value: str, group: str) -> dict:
    return {"dimension": dimension, "value": value, "support": "context",
            "context_group": group}


def _direct(dimension: str, value: str) -> dict:
    return {"dimension": dimension, "value": value, "support": "direct"}


# --- the validator: context-only placement, verified and unverified -------------


def test_a_context_only_placement_with_verified_group_support_is_accepted_for_review():
    """C17: no file text names the course or the kind of work; the accepted
    group carries both. Empty citations, every level context, the group named
    on every level -- accepted, and review is required (`00`:111)."""
    response = _place("n-03", [
        _context("course", "PHYS 1401", "group-phys1401-hw"),
        _context("kind of work", "homework", "group-phys1401-hw")], [])
    result = _judge("C17", response)
    assert result.json_schema_valid, result.json_schema_errors
    assert result.worst_outcome == ACCEPT_CONTEXT_SUPPORTED
    assert result.accepted and result.correct
    assert result.citations_total == 0
    assert result.outcome_class == CORRECT_PLACEMENT == result.expected_class
    assert result.detail["context_only"] is True


def test_a_context_level_naming_no_group_is_refused():
    response = _place("n-03", [
        {"dimension": "course", "value": "PHYS 1401", "support": "context"},
        {"dimension": "kind of work", "value": "homework", "support": "context"}], [])
    result = _judge("C17", response)
    assert result.json_schema_valid is False           # schema v2 refuses it too
    assert result.worst_outcome == REJECT
    assert _reasons(result) == [SLOT_FILLED_WITHOUT_EVIDENCE]
    assert result.outcome_class == INVALID_OUTPUT


def test_a_context_level_naming_a_group_the_dossier_does_not_carry_is_refused():
    response = _place("n-03", [
        _context("course", "PHYS 1401", "group-elsewhere"),
        _context("kind of work", "homework", "group-elsewhere")], [])
    result = _judge("C17", response)
    assert result.json_schema_valid
    assert result.worst_outcome == REJECT
    assert _reasons(result) == [SLOT_FILLED_WITHOUT_EVIDENCE]


def test_a_merely_retrieved_group_is_not_support():
    """C06 carries the Columbia packet as a group the file was RETRIEVED for
    (`possible`), not accepted into. A context level leaning on it is refused:
    `105` §14.1, "a merely-retrieved group is not support"."""
    response = _place("n-12", [
        _context("target university", "Columbia", "group-columbia"),
        _context("application document type", "essay", "group-columbia")], [],
        conflicts=["conflict-target-duke"])
    result = _judge("C06", response)
    assert result.worst_outcome == REJECT
    assert _reasons(result) == [SLOT_FILLED_WITHOUT_EVIDENCE]


def test_a_context_only_placement_on_a_dossier_with_no_group_at_all_is_refused():
    """C09: the generic hub. Nothing accepted, so no context level can stand."""
    response = _place("n-12", [
        _context("target university", "Columbia", "group-columbia")], [])
    result = _judge("C09", response)
    assert result.worst_outcome == REJECT
    assert _reasons(result) == [SLOT_FILLED_WITHOUT_EVIDENCE]
    assert result.outcome_class == INVALID_OUTPUT


def test_an_uncited_placement_with_a_direct_level_is_still_uncited():
    """The universal rule survives: only an all-context placement may cite
    nothing. A direct level with no citation is UNCITED_CLAIM, as before."""
    response = _place("n-03", [_direct("course", "PHYS 1401")], [])
    result = _judge("C18", response)
    assert result.json_schema_valid is False
    assert result.worst_outcome == REJECT
    assert _reasons(result) == [UNCITED_CLAIM]


# --- shared branch, parent/child, multiple institution ----------------------------


def test_the_shared_branch_stands_alone_on_its_two_groups_and_is_no_longer_weak():
    """C05: the transcript's text supports no packet; the branch that serves
    both accepted groups is the destination, context on every level, and the
    counts the model writes -- 1 and 1 the last three times -- decide nothing."""
    response = _place("n-11", [
        _context("branch", "Shared Application Materials", "group-columbia")], [],
        support=1, next_support=1)
    result = _judge("C05", response)
    assert result.worst_outcome == ACCEPT_CONTEXT_SUPPORTED
    assert result.correct and result.accepted
    assert INSUFFICIENT_MARGIN not in _reasons(result)
    assert result.outcome_class == CORRECT_PLACEMENT


def test_a_placement_that_reports_a_standing_alternative_is_unresolved():
    """The one thing INSUFFICIENT_MARGIN means now: the model placed the file
    and listed another fully supported candidate still standing. The text says
    that is a `none`; the validator records it unresolved, not as a move."""
    response = _place("n-11", [
        _context("branch", "Shared Application Materials", "group-columbia")], [],
        alternatives=["n-09", "n-10"])
    result = _judge("C05", response)
    assert result.worst_outcome == WEAK
    assert _reasons(result) == [INSUFFICIENT_MARGIN]
    assert result.accepted is False
    assert result.outcome_class == UNNECESSARY_ABSTENTION


def test_parent_and_child_supported_by_one_passage_the_child_stands_on_context():
    """C18: the heading supports the course folder and its homework child
    alike; the accepted group establishes the kind of work. Direct on the
    course, context on the kind, one citation -- accepted, and a tie in the
    counts changes nothing."""
    case = CASES["C18"]
    response = _place("n-03", [
        _direct("course", "PHYS 1401"),
        _context("kind of work", "homework", "group-phys1401-hw")],
        [_cite(case, 0, "PHYS 1401")], support=1, next_support=1)
    result = _judge("C18", response)
    assert result.worst_outcome == ACCEPT_DIRECT
    assert result.correct and result.accepted
    assert result.outcome_class == CORRECT_PLACEMENT


def test_the_essay_naming_a_former_school_and_a_target_university_is_placed():
    """C14: the former school is a mention, not a contradiction (`105` §14.1's
    contradiction rule); the target university's essays node is not struck."""
    case = CASES["C14"]
    response = _place("n-21", [
        _direct("target university", "UChicago"),
        _direct("application document type", "Why UChicago?")],
        [_cite(case, 0, "UChicago"), _cite(case, 2, "The University of Chicago")])
    result = _judge("C14", response)
    assert result.worst_outcome == ACCEPT_DIRECT
    assert result.correct and result.accepted


# --- the two counts and the two codes ---------------------------------------------


@pytest.mark.parametrize("support,next_support", [(0, 0), (1, 1), (0, 5), (3, 1)])
def test_the_two_counts_are_recorded_and_never_a_veto(support, next_support):
    case = CASES["C18"]
    response = _place("n-03", [_direct("course", "PHYS 1401")],
                      [_cite(case, 0, "PHYS 1401")],
                      support=support, next_support=next_support)
    result = _judge("C18", response)
    assert result.worst_outcome == ACCEPT_DIRECT, (support, next_support)
    assert not {BELOW_SUPPORT_THRESHOLD, INSUFFICIENT_MARGIN} & set(_reasons(result))


def test_a_missing_or_non_numeric_count_is_a_shape_violation():
    case = CASES["C18"]
    good = json.loads(_place("n-03", [_direct("course", "PHYS 1401")],
                             [_cite(case, 0, "PHYS 1401")]))
    for mutate in (lambda p: p.pop("support"), lambda p: p.pop("next_support"),
                   lambda p: p.update(support="high")):
        doc = json.loads(json.dumps(good))
        mutate(doc["claims"][0]["payload"])
        result = _judge("C18", json.dumps(doc).encode())
        assert result.worst_outcome == REJECT
        assert _reasons(result) == [SCHEMA_INVALID]


def test_below_support_threshold_means_no_supported_level_was_listed():
    case = CASES["C18"]
    response = _place("n-03", [], [_cite(case, 0, "PHYS 1401")], support=1)
    result = _judge("C18", response)
    assert result.json_schema_valid is False           # v2 wants one level
    assert result.worst_outcome == WEAK
    assert _reasons(result) == [BELOW_SUPPORT_THRESHOLD]


# --- abstention -------------------------------------------------------------------


def test_the_decline_shape_may_now_list_what_stood_and_abstains():
    """C04: two homes and no shared branch. The `none` answer names the two
    that stood so the person sees them; the validator records an abstention."""
    result = _judge("C04", _decline(["n-09", "n-10"]))
    assert result.json_schema_valid, result.json_schema_errors
    assert result.worst_outcome == ABSTAIN
    assert result.abstained and result.abstain_correct
    assert result.outcome_class == APPROPRIATE_ABSTENTION == result.expected_class


def test_an_abstention_on_an_answerable_case_is_an_unnecessary_abstention():
    result = _judge("C17", _decline())
    assert result.worst_outcome == ABSTAIN
    assert result.outcome_class == UNNECESSARY_ABSTENTION
    assert result.expected_class == CORRECT_PLACEMENT


def test_a_placement_on_a_should_abstain_case_is_an_incorrect_placement():
    """C15: OCR noise, answered anyway with a grounded span -- the S1 failure the
    local arm produced. Accepted by the validator; classed as what it is."""
    case = CASES["C15"]
    response = _place("n-18", [_direct("application cycle", "2O26")],
                      [_cite(case, 0, "2O26")])
    result = _judge("C15", response)
    assert result.accepted
    assert result.outcome_class == INCORRECT_PLACEMENT


def test_outcome_class_covers_the_five_and_nothing_else():
    common = dict(parsed=True, json_schema_valid=True, verdicts=[{"reasons": []}])
    assert outcome_class(**common, worst_outcome=ACCEPT_DIRECT,
                         should_abstain=False, correct=True) == CORRECT_PLACEMENT
    assert outcome_class(**common, worst_outcome=ACCEPT_DIRECT,
                         should_abstain=False, correct=False) == INCORRECT_PLACEMENT
    assert outcome_class(**common, worst_outcome=ABSTAIN,
                         should_abstain=True, correct=None) == APPROPRIATE_ABSTENTION
    assert outcome_class(**common, worst_outcome=WEAK,
                         should_abstain=False, correct=True) == UNNECESSARY_ABSTENTION
    assert outcome_class(**common, worst_outcome=REJECT,
                         should_abstain=False, correct=True) == INVALID_OUTPUT
    assert outcome_class(parsed=False, json_schema_valid=False, verdicts=[],
                         worst_outcome=None, should_abstain=False,
                         correct=None) == INVALID_OUTPUT


# --- schema v2 --------------------------------------------------------------------


def _v2():
    schema = _schema(SCHEMA_V2)
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema)


def test_schema_v2_accepts_the_context_only_shape_and_v1_rejects_it():
    doc = json.loads(_place("n-03", [_context("course", "PHYS 1401", "g")], []))
    assert _v2().is_valid(doc)
    assert not jsonschema.Draft202012Validator(_schema(SCHEMA_V1)).is_valid(doc)


def test_schema_v2_rejects_an_empty_citations_list_when_any_level_is_direct():
    doc = json.loads(_place("n-03", [
        _context("course", "PHYS 1401", "g"), _direct("kind of work", "Problem")], []))
    assert not _v2().is_valid(doc)
    doc["claims"][0]["citations"] = [{"evidence_ref": "k", "cited_span": "Problem",
                                      "why_it_supports": "states it"}]
    assert _v2().is_valid(doc)


def test_schema_v2_ties_context_group_to_context_and_keeps_every_object_closed():
    validator = _v2()
    direct_with_group = json.loads(_place("n-03", [
        dict(_direct("course", "PHYS 1401"), context_group="g")],
        [{"evidence_ref": "k", "cited_span": "PHYS", "why_it_supports": "x"}]))
    assert not validator.is_valid(direct_with_group)
    no_levels = json.loads(_place("n-03", [], []))
    assert not validator.is_valid(no_levels)
    stray = json.loads(_place("n-03", [_context("course", "PHYS 1401", "g")], []))
    stray["claims"][0]["payload"]["extra"] = 1
    assert not validator.is_valid(stray)
    schema = _schema(SCHEMA_V2)
    closed = [schema, schema["$defs"]["claim"], schema["$defs"]["payload"],
              schema["$defs"]["payload"]["properties"]["per_dimension_support"]["items"],
              schema["$defs"]["citation"], schema["$defs"]["unknown"]]
    assert all(obj.get("additionalProperties") is False for obj in closed)


def test_schema_v2_keeps_the_decline_shape_of_v1():
    v1, v2 = _schema(SCHEMA_V1), _schema(SCHEMA_V2)
    assert v1["$defs"]["claim"]["oneOf"][1] == v2["$defs"]["claim"]["oneOf"][1]
    assert v1["$defs"]["unknown"] == v2["$defs"]["unknown"]
    assert _v2().is_valid(json.loads(_decline(["n-09"])))
    assert _v2().is_valid(json.loads(_decline()))


# --- nothing in the library moved -------------------------------------------------


def test_eliminate_v2_and_its_schema_are_byte_identical_to_the_manifest():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for name in ("c_placement_template.eliminate-v2.txt",
                 "c_placement_response_schema.json",
                 "c_placement_shaping_policy.json"):
        digest = hashlib.sha256((LIBRARY / name).read_bytes()).hexdigest()
        assert digest == manifest["digests"][name], name
    assert TEXT_V3.read_bytes() != (LIBRARY / "c_placement_template.eliminate-v2.txt").read_bytes()
    assert not (LIBRARY / "c_placement_template.eliminate-v3.txt").exists()
    assert not (LIBRARY / "c_placement_response_schema.v2.json").exists()


# --- the v3 text, checked as the manifest tests will check it ---------------------


DOSSIER_KEYS = sorted([
    "allowed_vocabulary", "call_site", "conflicts", "eligibility_reason",
    "evidence_items", "field_glossary", "folder_levels", "max_dossier_tokens",
    "plan_version", "policy_version", "reduction_rung", "released_evidence",
    "response_schema", "shaping_policy", "subject_ref"])
FORBIDDEN_WORDS = ("deepseek", "qwen", "ollama", "anthropic", "claude", "openai",
                   "gpt", "reasoning tier", "logic tier", "fast tier")
FIELD_KEYS = ("work_type", "subject", "school", "term", "instructor",
              "target_university", "application_cycle", "capture_year")


def _shapes(text: str) -> list[dict]:
    return [json.loads(line) for line in text.splitlines()
            if line.startswith("{") and line.endswith("}")]


def test_the_v3_text_holds_the_template_constraints():
    text = TEXT_V3.read_text(encoding="utf-8")
    assert text.endswith("The dossier follows.\n") and not text.endswith("\n\n")
    assert "`" not in text
    for word in FORBIDDEN_WORDS:
        assert word not in text.lower(), word
    line = next(l for l in text.splitlines()
                if l.startswith("The dossier has these keys and no others:"))
    assert [k.strip().rstrip(".") for k in line.split(":", 1)[1].split(",")] == DOSSIER_KEYS
    for key in FIELD_KEYS:
        assert f'"{key}"' not in text, key
    assert "2026-09" not in text and "2025" not in text


def test_the_v3_text_states_the_ruling_verbatim():
    text = TEXT_V3.read_text(encoding="utf-8")
    assert ("Strike a candidate only when the released evidence establishes an "
            "incompatible value for the same dimension, semantic role, and scope; "
            "mentioning another institution, term, project, or course is not itself "
            "a contradiction.") in text
    assert '"context_group"' in text
    assert 'When every level is "context", "citations" is an empty list' in text
    assert "They are recorded and they decide nothing" in text
    assert "it does not bring back a candidate you struck" in text


def test_the_v3_shapes_parse_and_validate_against_schema_v2_on_bench_cases():
    shapes = _shapes(TEXT_V3.read_text(encoding="utf-8"))
    answering = [s for s in shapes if "citations" in s["claims"][0]]
    declining = [s for s in shapes if "unknown" in s["claims"][0]]
    assert len(answering) == 2 and len(declining) == 1
    context_only = next(s for s in answering if s["claims"][0]["citations"] == [])
    claim = json.loads(json.dumps(context_only["claims"][0]))
    claim["payload"]["destination"] = "n-03"
    claim["payload"]["per_dimension_support"] = [
        _context("course", "PHYS 1401", "group-phys1401-hw")]
    claim["payload"]["conflicts_considered"] = []
    response = json.dumps({"claims": [claim]}).encode()
    _v2().validate(json.loads(response))
    assert _judge("C17", response).worst_outcome == ACCEPT_CONTEXT_SUPPORTED
    decline = json.loads(json.dumps(declining[0]))
    decline["claims"][0]["payload"]["conflicts_considered"] = []
    _v2().validate(decline)
    assert _judge("C04", json.dumps(decline).encode()).worst_outcome == ABSTAIN


# --- the activation set -----------------------------------------------------------


def test_the_activation_set_names_one_case_per_ruled_behaviour_and_every_abstainer():
    assert set(ACTIVATION) <= set(CASES)
    abstainers = {c for c, case in CASES.items() if case.should_abstain}
    assert abstainers <= set(ACTIVATION)
    for case_id in ("C17", "C05", "C14", "C18"):
        assert case_id in ACTIVATION and not CASES[case_id].should_abstain
    assert CASES["C17"].title.startswith("context-only")
    assert CASES["C18"].title.startswith("parent/child")
    assert expected_class(CASES["C17"]) == CORRECT_PLACEMENT
    assert expected_class(CASES["C04"]) == APPROPRIATE_ABSTENTION
    # the first answerable and the first should-abstain case did not move
    assert next(c for c in cases_for(C_PLACEMENT) if not c.should_abstain).case_id == "C01"
    assert next(c for c in cases_for(C_PLACEMENT) if c.should_abstain).case_id == "C04"
