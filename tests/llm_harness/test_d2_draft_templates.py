"""Every D2 draft, checked the way `90` §4 checked the A_fact candidates.

The drafts manifest (`src/llm_harness/library/drafts_2026-09-06.json`) is the
list of texts the packet puts to the owner. For each row this file asserts the
things a scorer can assert without a model: the bytes match the manifest, the id
says `unratified` and carries the date, the text names exactly the dossier keys
`llm_harness.dossier._body` emits (the failure that made the ratified A_fact
text stale the day `folder_levels` was added), it contains no backtick, no
provider, model or tier name, and no catalogue field key in a worked example;
the response schema is a valid 2020-12 schema; and the two shapes the text shows
the model parse, validate against that schema, and produce the verdict the text
promises when instantiated against a bench case and run through the real
validator: the answering shape is accepted, the declining shape abstains.
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
    F_ROLE_SHORTLIST,
    A_FACT, ABSTAIN, ACCEPT_CONTEXT_SUPPORTED, ACCEPT_DIRECT, B_GROUP, C_PLACEMENT,
    D_RESIDUAL, E_TEMPLATE,
)
from llm_harness.wire_handles import wire_handle  # noqa: E402

from tools.promptbench.candidates import (  # noqa: E402
    LIBRARY, MANIFEST, all_candidates,
)
from tools.promptbench.dossiers import (  # noqa: E402
    BENCH_HANDLE_KEY, dossier_of, model_visible_bytes,
)
from tools.promptbench.judge import judge, site_dependencies_for  # noqa: E402
from tools.promptbench.suites import cases_for  # noqa: E402

CANDIDATES = [c for c in all_candidates() if c.site != A_FACT]
IDS = [f"{c.site}:{c.name}" for c in CANDIDATES]

#: `dossier._body`'s keys, read from the module rather than typed, and sorted as
#: `canonical_json` emits them.
DOSSIER_KEYS = sorted([
    "allowed_vocabulary", "call_site", "conflicts", "eligibility_reason",
    "evidence_items", "field_glossary", "folder_levels", "max_dossier_tokens",
    "plan_version", "policy_version", "reduction_rung", "released_evidence",
    "response_schema", "shaping_policy", "subject_ref"])

FORBIDDEN_WORDS = ("deepseek", "qwen", "ollama", "anthropic", "claude", "openai",
                   "gpt", "reasoning tier", "logic tier", "fast tier")
#: Catalogue field keys a shared template must not use in a worked example (`76`
#: R18); the keys the site legitimately names as vocabulary are excluded per site.
FIELD_KEYS = ("work_type", "subject", "school", "term", "instructor",
              "target_university", "application_cycle", "capture_year")


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_the_manifest_digests_are_the_bytes_on_disk():
    manifest = _manifest()
    assert manifest["status"] == "unratified"
    for name, digest in manifest["digests"].items():
        assert hashlib.sha256((LIBRARY / name).read_bytes()).hexdigest() == digest, name
    for row in manifest["drafts"]:
        assert "unratified" in row["template_id"], row["template_id"]
        assert re.search(r"\d{4}-\d{2}-\d{2}$", row["template_id"]), row["template_id"]


def test_the_ratified_files_are_untouched():
    from llm_harness.prompt_library import (
        a_fact_response_schema_bytes, a_fact_shaping_policy_bytes,
        a_fact_template_bytes, a_fact_template_folder_levels_bytes,
    )
    for loader in (a_fact_template_bytes, a_fact_template_folder_levels_bytes,
                   a_fact_response_schema_bytes, a_fact_shaping_policy_bytes):
        assert loader()   # each raises RatifiedTextChanged if edited


@pytest.mark.parametrize("candidate", CANDIDATES, ids=IDS)
def test_the_text_is_a_constant_that_names_the_dossier_exactly(candidate):
    text = candidate.prompt().template_bytes.decode("utf-8")
    assert text.endswith("The dossier follows.\n"), "R1: the template supplies its terminator"
    assert not text.endswith("\n\n")
    assert "`" not in text, "R15: no fence characters"
    lowered = text.lower()
    for word in FORBIDDEN_WORDS:
        assert word not in lowered, word
    line = next((l for l in text.splitlines() if l.startswith(
        "The dossier has these keys and no others:")), None)
    assert line is not None, "R2: one line names the key set"
    named = [k.strip().rstrip(".") for k in line.split(":", 1)[1].split(",")]
    expected = sorted(DOSSIER_KEYS + (["readings"] if candidate.readings_rows else []))
    assert named == expected, named
    for key in FIELD_KEYS:
        assert f'"{key}"' not in text, f"R18: {key!r} in a worked example"
    assert "2026-09" not in text and "2025" not in text, "R17: nothing that varies"


@pytest.mark.parametrize("candidate", CANDIDATES, ids=IDS)
def test_the_schema_is_a_valid_2020_12_schema_and_the_policy_is_json(candidate):
    schema = candidate.response_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    assert schema["properties"]["claims"]["items"]
    policy = json.loads(candidate.prompt().shaping_policy_bytes.decode("utf-8"))
    assert policy["call_site"] == candidate.site
    assert "unratified" in policy["policy_id"]


def _shapes(text: str) -> list[dict]:
    """Every line of the template that is a JSON object, parsed."""
    shapes = []
    for line in text.splitlines():
        if line.startswith("{") and line.endswith("}"):
            shapes.append(json.loads(line))
    return shapes


@pytest.mark.parametrize("candidate", CANDIDATES, ids=IDS)
def test_the_shown_shapes_parse_and_one_declines(candidate):
    text = candidate.prompt().template_bytes.decode("utf-8")
    shapes = _shapes(text)
    assert len(shapes) >= 2, "an answering shape and a declining shape"
    declining = [s for s in shapes if "unknown" in s["claims"][0]]
    answering = [s for s in shapes if "citations" in s["claims"][0]]
    assert declining and answering


# --- the shapes, instantiated against a bench case and run through the validator --


def _first_case(site: str, *, abstain: bool):
    return next(c for c in cases_for(site) if c.should_abstain is abstain)


def _cite(case):
    item = case.evidence[0]
    return [{"evidence_ref": wire_handle(item.key, key=BENCH_HANDLE_KEY),
             "cited_span": item.value[: max(1, len(item.value) // 2)],
             "why_it_supports": "the released text carries it"}]


def _instantiate(candidate, case, shape: dict) -> bytes:
    """Fill the template's shown shape with the case's real identifiers."""
    claim = json.loads(json.dumps(shape["claims"][0]))
    payload = claim["payload"]
    if "citations" in claim:
        claim["citations"] = _cite(case)
    if candidate.site == F_ROLE_SHORTLIST:
        payload["situation"] = case.expect.get("situation") or "none"
        payload["alternatives"] = []
    if candidate.site == C_PLACEMENT:
        payload["destination"] = case.expect.get("destination", "none")
        if "citations" in claim:
            payload["per_dimension_support"] = [
                {"dimension": "a level", "value": case.evidence[0].value[:8],
                 "support": "direct"}]
            payload["alternatives"] = []
            payload["support"], payload["next_support"] = 1, 0
            payload["refinement"] = "not_applicable"
        payload["conflicts_considered"] = []
    elif candidate.site == D_RESIDUAL:
        if "citations" in claim:
            payload["action"] = case.expect.get("action") or case.expect["action_in"][0]
            payload["target"] = case.expect["target"]
        else:
            payload["action"] = "abstain"
            payload["target"] = None
        payload["relationships_considered"] = []
        payload["stop_reason"] = "instantiated"
    elif candidate.site == B_GROUP:
        members = [i.evidence_ref for i in case.items if i.kind == "member"]
        if "citations" in claim:
            payload["coherent"] = "yes"
            payload["basis"] = "direct-anchor"
            payload["category"] = case.allowed_vocabulary[0]
            payload["label"] = "instantiated"
            payload["members"] = [{"file_id": m, "decision": "include",
                                   "why": "states the basis",
                                   "evidence_refs": [_cite(case)[0]["evidence_ref"]]}
                                  for m in members]
            payload["outliers"] = []
            payload["merge_terms"] = []
        else:
            payload["coherent"] = "insufficient"
            payload["basis"] = "generic-similarity"
            payload["members"] = []
            payload["outliers"] = []
    elif candidate.site == E_TEMPLATE:
        if "citations" in claim:
            name = case.allowed_vocabulary[0] if case.allowed_vocabulary else "campaign"
            scope = "schema-field" if case.allowed_vocabulary else "template-local"
            ref = _cite(case)[0]["evidence_ref"]
            payload["domain"] = "instantiated"
            payload["allowed_fields"] = [name]
            payload["fragment_refs"] = []
            payload["dimensions"] = [{"name": name, "scope": scope,
                                      "evidence_ref": ref, "requirement": "required",
                                      "metadata_only": False, "order_index": 0,
                                      "values": ["v"]}]
            payload["levels"] = [{"dimension": name,
                                  "retrieval_justification": "instantiated"}]
            payload["sensitivity_policy_ref"] = "policy.personal-default"
            payload["example_label_chains"] = [["a", "b"]]
    return json.dumps({"claims": [claim]}).encode("utf-8")


@pytest.mark.parametrize("candidate", CANDIDATES, ids=IDS)
def test_the_answering_shape_is_accepted_and_the_declining_shape_abstains(candidate):
    text = candidate.prompt().template_bytes.decode("utf-8")
    shapes = _shapes(text)
    answering = next(s for s in shapes if "citations" in s["claims"][0])
    declining = next(s for s in shapes if "unknown" in s["claims"][0])
    schema = candidate.response_schema()

    case = _first_case(candidate.site, abstain=False)
    response = _instantiate(candidate, case, answering)
    jsonschema.Draft202012Validator(schema).validate(json.loads(response))
    verdict = judge(case, dossier_of(case), response, schema=schema,
                    site_dependencies=site_dependencies_for(case))
    assert verdict.worst_outcome in (ACCEPT_DIRECT, ACCEPT_CONTEXT_SUPPORTED), (
        verdict.verdicts)

    case = _first_case(candidate.site, abstain=True)
    response = _instantiate(candidate, case, declining)
    jsonschema.Draft202012Validator(schema).validate(json.loads(response))
    verdict = judge(case, dossier_of(case), response, schema=schema,
                    site_dependencies=site_dependencies_for(case))
    assert verdict.worst_outcome == ABSTAIN, verdict.verdicts


@pytest.mark.parametrize("candidate", CANDIDATES, ids=IDS)
def test_the_model_visible_bytes_carry_the_template_then_the_dossier(candidate):
    case = cases_for(candidate.site)[0]
    payload = model_visible_bytes(dossier_of(case), candidate.prompt())
    template = candidate.prompt().template_bytes
    assert payload.startswith(template)
    body = json.loads(payload[len(template):].decode("utf-8"))
    assert sorted(body) == DOSSIER_KEYS
    # A candidate that carries readings names a sixteenth key, `readings`, which
    # the run adds to these bytes (105 §1.8, §12); the bare bytes never carry it.
    line = next(l for l in template.decode("utf-8").splitlines()
                if l.startswith("The dossier has these keys and no others:"))
    assert ("readings" in line) == bool(candidate.readings_rows)
