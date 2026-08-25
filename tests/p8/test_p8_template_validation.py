"""Site E template validation against P8-owned recorded pairs."""
from __future__ import annotations

import ast
import json
from pathlib import Path

from llm_harness.fixtures import SITE_E_OUTCOME_PAIRS
from llm_harness.records import ValidationUnavailable
from llm_harness.template_validation import (
    TemplateDependencies,
    validate_template_response,
)
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    E_TEMPLATE,
    REJECT,
    SCOPE_TEMPLATE,
    WEAK,
)

RELEASED = "span-1"


def _resolver(observation_key: str) -> str | None:
    if observation_key.startswith("obs-"):
        return RELEASED
    return None


def _never_contradicts(*_a, **_k) -> bool:
    return False


def _deps(pair) -> TemplateDependencies:
    def schema_validator(payload: object) -> bool:
        del payload
        return pair.schema_ok

    return TemplateDependencies(schema_validator=schema_validator)


def _validate(pair, *, dependencies=None, contradicts=_never_contradicts):
    deps = _deps(pair) if dependencies is None else dependencies
    return validate_template_response(
        pair.dossier,
        pair.response_bytes,
        evidence_resolver=_resolver,
        contradicts=contradicts,
        dependencies=deps,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        dossier_builder="p8-fixture",
        release_audit_id=17,
    )


def test_site_e_outcome_pairs_cover_direct_context_weak_reject_unknown():
    by_name = {pair.name: pair for pair in SITE_E_OUTCOME_PAIRS}
    assert tuple(by_name) == (
        "direct_accept", "context_accept", "weak", "reject", "unknown",
    )
    for pair in SITE_E_OUTCOME_PAIRS:
        assert pair.dossier.call_site == E_TEMPLATE
        assert pair.dossier.plan_version

    direct = _validate(by_name["direct_accept"])[0][0]
    assert direct.outcome == ACCEPT_DIRECT
    assert direct.reasons == ()
    assert direct.scope == SCOPE_TEMPLATE
    assert direct.may_propose is True
    assert direct.plan_version == by_name["direct_accept"].dossier.plan_version

    context = _validate(by_name["context_accept"])[0][0]
    assert context.outcome == ACCEPT_CONTEXT_SUPPORTED
    assert context.requires_review is True

    weak = _validate(by_name["weak"])[0][0]
    assert weak.outcome == WEAK
    assert weak.may_propose is False

    reject = _validate(by_name["reject"])[0][0]
    assert reject.outcome == REJECT
    assert reject.may_propose is False

    unknown = _validate(by_name["unknown"])[0][0]
    assert unknown.outcome == ABSTAIN


def test_site_e_citation_required_per_proposed_dimension():
    pair = next(p for p in SITE_E_OUTCOME_PAIRS if p.name == "direct_accept")
    verdict = _validate(pair)[0][0]
    payload_claim = json.loads(pair.response_bytes)["claims"][0]
    dimensions = payload_claim["payload"]["dimensions"]
    cited = {item["evidence_ref"] for item in payload_claim["citations"]}
    for dimension in dimensions:
        assert dimension["evidence_ref"] in cited
    assert verdict.outcome == ACCEPT_DIRECT


def test_site_e_allowed_vocabulary_closure_rejects():
    pair = next(p for p in SITE_E_OUTCOME_PAIRS if p.name == "reject")
    assert pair.schema_ok is True
    verdict = _validate(pair)[0][0]
    assert verdict.outcome == REJECT
    dimension_names = [
        item["name"]
        for item in json.loads(pair.response_bytes)["claims"][0]["payload"]["dimensions"]
    ]
    assert any(name not in pair.dossier.allowed_vocabulary for name in dimension_names)


def test_omitted_schema_validator_is_unavailable():
    pair = SITE_E_OUTCOME_PAIRS[0]
    result = validate_template_response(
        pair.dossier,
        pair.response_bytes,
        evidence_resolver=_resolver,
        contradicts=_never_contradicts,
        dependencies=None,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        dossier_builder="p8-fixture",
        release_audit_id=17,
    )
    assert isinstance(result, ValidationUnavailable)
    assert result.missing == ("schema_validator",)


def test_injected_schema_failure_is_schema_invalid():
    pair = next(p for p in SITE_E_OUTCOME_PAIRS if p.name == "direct_accept")
    failing = TemplateDependencies(schema_validator=lambda _payload: False)
    verdicts, report = _validate(pair, dependencies=failing)
    assert verdicts[0].outcome == REJECT
    assert "SCHEMA_INVALID" in verdicts[0].reasons
    assert report.reasons_histogram["SCHEMA_INVALID"] == 1


def test_template_validation_does_not_score_a_hierarchy():
    source = (
        Path(__file__).resolve().parents[2]
        / "src" / "llm_harness" / "template_validation.py"
    ).read_text()
    names = {
        node.name
        for node in ast.walk(ast.parse(source))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert not {"score_hierarchy", "invent_hierarchy", "rank_template"} & names
