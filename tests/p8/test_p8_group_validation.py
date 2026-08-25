"""Site B group validation against P8-owned recorded pairs."""
from __future__ import annotations

import dataclasses
import json
from collections import Counter
from pathlib import Path

from llm_harness.fixtures import SITE_B_OUTCOME_PAIRS, SITE_B_REASON_PAIRS
from llm_harness.group_validation import validate_group_response
from llm_harness.records import P8Verdict, ValidationUnavailable
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    B_GROUP,
    CONTEXT_ONLY_SUPPORT,
    CONTEXT_SUPPORTED_MEMBERSHIP,
    DIRECT_MEMBERSHIP,
    FOLDER_HIERARCHY_PROPOSED,
    GENERIC_SIMILARITY_ONLY,
    INVENTED_DATE,
    INVENTED_MEMBERSHIP,
    INVENTED_PROJECT,
    INVENTED_PURPOSE,
    LABEL_WITHOUT_COHERENCE,
    REJECT,
    REJECTED,
    SCOPE_GROUP,
    SITE_B_REASON_CODES,
    UNRESOLVED,
    WEAK,
)

RELEASED = "span-1"


def _resolver(observation_key: str) -> str | None:
    if observation_key.startswith("obs-"):
        return RELEASED
    return None


def _never_contradicts(*_a, **_k) -> bool:
    return False


def _validate(pair, *, contradicts=_never_contradicts, evidence_resolver=_resolver):
    return validate_group_response(
        pair.dossier,
        pair.response_bytes,
        evidence_resolver=evidence_resolver,
        contradicts=contradicts,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        dossier_builder="p8-fixture",
        release_audit_id=17,
    )


def _with_payload_fields(pair, *, drop=(), **fields):
    parsed = json.loads(pair.response_bytes)
    payload = parsed["claims"][0]["payload"]
    for key in drop:
        payload.pop(key, None)
    payload.update(fields)
    return dataclasses.replace(pair, response_bytes=json.dumps(parsed).encode())


def test_site_b_reason_registry_exercises_each_code_exactly_once():
    seen: list[str] = []
    for pair in SITE_B_REASON_PAIRS:
        assert pair.dossier.call_site == B_GROUP
        result = _validate(pair)
        assert not isinstance(result, ValidationUnavailable)
        verdicts, report = result
        assert len(verdicts) == 1
        verdict = verdicts[0]
        assert isinstance(verdict, P8Verdict)
        assert verdict.reasons == pair.expected_reasons
        assert len(verdict.reasons) == 1
        assert verdict.outcome == pair.expected_outcome
        assert verdict.disposition == pair.expected_disposition
        assert verdict.scope == SCOPE_GROUP
        seen.append(verdict.reasons[0])
        assert report.reasons_histogram[verdict.reasons[0]] == 1
    assert tuple(seen) == SITE_B_REASON_CODES
    assert Counter(seen) == Counter(SITE_B_REASON_CODES)


def test_site_b_outcome_pairs_cover_direct_context_weak_reject_unknown():
    by_name = {pair.name: pair for pair in SITE_B_OUTCOME_PAIRS}
    direct = _validate(by_name["direct_accept"])[0][0]
    assert direct.outcome == ACCEPT_DIRECT
    assert direct.disposition == DIRECT_MEMBERSHIP
    assert direct.reasons == ()
    assert direct.may_propose is True
    assert direct.requires_review is False

    context = _validate(by_name["context_accept"])[0][0]
    assert context.outcome == ACCEPT_CONTEXT_SUPPORTED
    assert context.disposition == CONTEXT_SUPPORTED_MEMBERSHIP
    assert context.requires_review is True
    assert CONTEXT_ONLY_SUPPORT not in context.reasons

    weak = _validate(by_name["weak"])[0][0]
    assert weak.outcome == WEAK
    assert weak.disposition == UNRESOLVED
    assert weak.may_propose is False

    reject = _validate(by_name["reject"])[0][0]
    assert reject.outcome == REJECT
    assert reject.disposition in {REJECTED, UNRESOLVED}
    assert not set(reject.reasons) & set(SITE_B_REASON_CODES)

    unknown = _validate(by_name["unknown"])[0][0]
    assert unknown.outcome == ABSTAIN
    assert unknown.disposition == UNRESOLVED
    assert unknown.reasons == ()


def test_invented_membership_is_a_file_outside_the_dossier():
    pair = next(p for p in SITE_B_REASON_PAIRS if p.expected_reasons == (INVENTED_MEMBERSHIP,))
    members = {item.evidence_ref for item in pair.dossier.evidence_items if item.kind == "member"}
    assert "file-invented" not in members
    verdict = _validate(pair)[0][0]
    assert verdict.reasons == (INVENTED_MEMBERSHIP,)
    assert verdict.outcome == REJECT


def test_string_list_members_are_checked_against_dossier():
    pair = next(p for p in SITE_B_OUTCOME_PAIRS if p.name == "direct_accept")
    members = {item.evidence_ref for item in pair.dossier.evidence_items if item.kind == "member"}
    assert "file-invented" not in members
    invented = _validate(_with_payload_fields(pair, members=["file-invented"]))[0][0]
    assert invented.outcome == REJECT
    assert invented.reasons == (INVENTED_MEMBERSHIP,)
    assert invented.may_propose is False
    accepted = _validate(_with_payload_fields(pair, members=["file-a", "file-b"]))[0][0]
    assert accepted.outcome == ACCEPT_DIRECT
    assert accepted.reasons == ()


def test_label_without_coherence_rejects():
    pair = next(
        p for p in SITE_B_REASON_PAIRS if p.expected_reasons == (LABEL_WITHOUT_COHERENCE,)
    )
    verdict = _validate(pair)[0][0]
    assert verdict.reasons == (LABEL_WITHOUT_COHERENCE,)
    assert verdict.outcome == REJECT
    assert verdict.may_propose is False


def test_folder_hierarchy_is_rejected():
    pair = next(
        p for p in SITE_B_REASON_PAIRS if p.expected_reasons == (FOLDER_HIERARCHY_PROPOSED,)
    )
    verdict = _validate(pair)[0][0]
    assert verdict.reasons == (FOLDER_HIERARCHY_PROPOSED,)
    assert verdict.outcome == REJECT


def test_generic_similarity_is_rejected():
    pair = next(
        p for p in SITE_B_REASON_PAIRS if p.expected_reasons == (GENERIC_SIMILARITY_ONLY,)
    )
    verdict = _validate(pair)[0][0]
    assert verdict.reasons == (GENERIC_SIMILARITY_ONLY,)
    assert verdict.outcome == REJECT
    assert verdict.disposition == UNRESOLVED


def test_invented_date_project_purpose_are_isolated():
    for code in (INVENTED_DATE, INVENTED_PROJECT, INVENTED_PURPOSE):
        pair = next(p for p in SITE_B_REASON_PAIRS if p.expected_reasons == (code,))
        verdict = _validate(pair)[0][0]
        assert verdict.reasons == (code,)
        assert verdict.outcome == REJECT


def test_context_only_support_reason_pair_is_distinct_from_outcome_context():
    pair = next(p for p in SITE_B_REASON_PAIRS if p.expected_reasons == (CONTEXT_ONLY_SUPPORT,))
    verdict = _validate(pair)[0][0]
    assert verdict.outcome == ACCEPT_CONTEXT_SUPPORTED
    assert verdict.reasons == (CONTEXT_ONLY_SUPPORT,)
    assert verdict.requires_review is True
    assert verdict.disposition == CONTEXT_SUPPORTED_MEMBERSHIP


def test_omitted_contradicts_is_unavailable_not_an_accept():
    pair = SITE_B_OUTCOME_PAIRS[0]
    result = _validate(pair, contradicts=None)
    assert isinstance(result, ValidationUnavailable)
    assert "contradicts" in result.missing


def test_group_validation_does_not_create_or_retrieve_groups():
    import ast

    source = (
        Path(__file__).resolve().parents[2]
        / "src" / "llm_harness" / "group_validation.py"
    ).read_text()
    names = {
        node.name
        for node in ast.walk(ast.parse(source))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert not {"retrieve_neighbours", "create_group", "accept_membership"} & names
