# tests/p8/test_p8_release_binding.py
"""P8 repair R4: a citation is grounded in what P7 released, not in the store.

SPEC: *"`CITATION_SPAN_MISMATCH` therefore compares the cited span against the
released dossier's excerpt — what the model actually saw — while
`CITATION_NOT_FOUND` resolves the reference against the store."*

Before this task both checks ran against the injected `evidence_resolver`, so
the span-matching source was whatever the caller returned. With redaction on,
that is the RAW stored text: a model quoting `Columbia University` would pass
even though the dossier showed it `[REDACTED-NAME] University`, and a model
quoting the redacted text it actually saw would fail. The two roles are now
split — the dossier's immutable released map matches the span, and P4 only
confirms the key still resolves.
"""
from __future__ import annotations

import dataclasses
import json

import pytest

from llm_harness.records import (
    Conflict,
    Dossier,
    EvidenceItem,
    ReleasedEvidence,
)
from llm_harness.validation import validate_response
from llm_harness.vocabulary import (
    A_FACT,
    ACCEPT_DIRECT,
    CITATION_NOT_FOUND,
    CITATION_NOT_IN_DOSSIER,
    CITATION_SPAN_MISMATCH,
    DIRECT_ANCHOR,
    REDUCTION_NONE,
    REJECT,
    REMAINS_AMBIGUOUS,
)
from llm_harness.fixtures import FIXTURE_HANDLE_KEY

KEY = "sha256:obs-1"
MEMBER = "file-7"
RAW = "Columbia University"
REDACTED = "[REDACTED-NAME] University"


def _evidence_item(**overrides) -> EvidenceItem:
    values = dict(
        evidence_ref=KEY,
        kind="excerpt",
        location="body",
        excerpt_span=(0, 19),
        reliability_state="direct",
        basis=DIRECT_ANCHOR,
    )
    values.update(overrides)
    return EvidenceItem(**values)


def _released(**overrides) -> ReleasedEvidence:
    values = dict(
        observation_key=KEY,
        address="0:19",
        value=REDACTED,
        zone="body",
    )
    values.update(overrides)
    return ReleasedEvidence(**values)


def _dossier(*, evidence_items=None, released_evidence=None) -> Dossier:
    return Dossier(
        dossier_id="dossier-1",
        call_site=A_FACT,
        subject_ref="file-1",
        eligibility_reason=REMAINS_AMBIGUOUS,
        plan_version=None,
        policy_version="policy-1",
        allowed_vocabulary=("school",),
        evidence_items=(
            (_evidence_item(),) if evidence_items is None else evidence_items
        ),
        conflicts=(Conflict(conflict_id="c1", kind="stronger_fact"),),
        released_evidence=(
            (_released(),) if released_evidence is None else released_evidence
        ),
        max_dossier_tokens=4000,
        reduction_rung=REDUCTION_NONE,
        release_id="rel-1",
    )


def _bytes(*, ref: str = KEY, span: str = REDACTED) -> bytes:
    return json.dumps({
        "claims": [{
            "claim_ref": "c1",
            "payload": {"field": "school", "value": "Columbia"},
            "citations": [{
                "evidence_ref": ref,
                "cited_span": span,
                "why_it_supports": "names the school",
            }],
        }],
    }, separators=(",", ":")).encode("utf-8")


def _validate(dossier, response_bytes, *, resolver=None, contradicts=None):
    return validate_response(
        dossier,
        response_bytes,
        evidence_resolver=resolver if resolver is not None else (lambda key: RAW),
        site_validator=lambda *_a, **_k: None,
        contradicts=contradicts if contradicts is not None else (lambda *_a, **_k: False),
        model_id="fixture-model",
        prompt_fingerprint="fp-1",
        dossier_builder="fixture",
        release_audit_id=17, handle_key=FIXTURE_HANDLE_KEY,
    )


def _one(result):
    verdicts, _report = result
    assert len(verdicts) == 1
    return verdicts[0]


# --- the two checks have different sources --------------------------------------


def test_a_redacted_released_value_passes_when_cited_exactly():
    """The model saw the redacted text; quoting it exactly is grounded."""
    verdict = _one(_validate(_dossier(), _bytes(span=REDACTED)))
    assert verdict.outcome == ACCEPT_DIRECT
    assert verdict.citations_checked[0].span_matched is True


def test_citing_the_raw_store_value_fails_even_though_p4_holds_it():
    """P4 contains `Columbia University`. The model was never shown it."""
    verdict = _one(_validate(_dossier(), _bytes(span=RAW), resolver=lambda key: RAW))
    assert verdict.outcome == REJECT
    assert verdict.reasons == (CITATION_SPAN_MISMATCH,)
    assert verdict.citations_checked[0].resolved is True
    assert verdict.citations_checked[0].span_matched is False


def test_the_resolver_value_is_never_the_span_matching_source():
    """A resolver returning text that contains the span cannot rescue a mismatch."""
    verdict = _one(_validate(
        _dossier(),
        _bytes(span="Cornell"),
        resolver=lambda key: "Cornell College of Everything",
    ))
    assert verdict.outcome == REJECT
    assert verdict.reasons == (CITATION_SPAN_MISMATCH,)


def test_a_key_p4_no_longer_resolves_is_citation_not_found():
    """`CITATION_NOT_FOUND` resolves the reference against the store (SPEC)."""
    verdict = _one(_validate(_dossier(), _bytes(), resolver=lambda key: None))
    assert verdict.outcome == REJECT
    assert verdict.reasons == (CITATION_NOT_FOUND,)
    assert verdict.citations_checked[0].resolved is False


# --- outside the release --------------------------------------------------------


def test_citing_a_structural_reference_with_no_released_text_rejects():
    """A Site-B candidate member is a reference. Nothing about it was released."""
    dossier = _dossier(
        evidence_items=(
            _evidence_item(),
            _evidence_item(evidence_ref=MEMBER, kind="member", excerpt_span=None),
        ),
    )
    verdict = _one(_validate(dossier, _bytes(ref=MEMBER, span="anything")))
    assert verdict.outcome == REJECT
    assert verdict.reasons == (CITATION_NOT_IN_DOSSIER,)


def test_a_citation_naming_no_dossier_item_at_all_rejects():
    verdict = _one(_validate(_dossier(), _bytes(ref="sha256:never-shown")))
    assert verdict.outcome == REJECT
    assert verdict.reasons == (CITATION_NOT_IN_DOSSIER,)


def test_a_metadata_citation_with_nothing_released_under_that_name_rejects():
    body = json.loads(_bytes())
    del body["claims"][0]["citations"][0]["cited_span"]
    body["claims"][0]["citations"][0]["metadata_field_name"] = "page_count"
    verdict = _one(_validate(
        _dossier(), json.dumps(body, separators=(",", ":")).encode("utf-8"),
    ))
    assert verdict.outcome == REJECT
    assert verdict.reasons == (CITATION_SPAN_MISMATCH,)


def test_a_metadata_citation_matching_a_released_address_passes():
    dossier = _dossier(
        evidence_items=(_evidence_item(kind="metadata", excerpt_span=None),),
        released_evidence=(_released(address="page_count", value="12"),),
    )
    body = json.loads(_bytes())
    del body["claims"][0]["citations"][0]["cited_span"]
    body["claims"][0]["citations"][0]["metadata_field_name"] = "page_count"
    verdict = _one(_validate(
        dossier, json.dumps(body, separators=(",", ":")).encode("utf-8"),
    ))
    assert verdict.outcome == ACCEPT_DIRECT


# --- the released map is what replay reads --------------------------------------


def test_two_dossiers_over_the_same_key_use_their_own_released_value():
    """The release is per-dossier; a later, differently-redacted release is a
    different dossier and must be judged against its own bytes."""
    first = _dossier()
    second = _dossier(released_evidence=(_released(value="[REDACTED] University"),))
    assert _one(_validate(first, _bytes(span=REDACTED))).outcome == ACCEPT_DIRECT
    assert _one(_validate(second, _bytes(span=REDACTED))).outcome == REJECT


@pytest.mark.parametrize("resolved", [True, 1, object(), {"text": RAW}, RAW])
def test_any_non_none_resolution_means_the_key_still_exists(resolved):
    """The store answers presence. Its shape is not a second span source."""
    verdict = _one(_validate(_dossier(), _bytes(), resolver=lambda key: resolved))
    assert verdict.outcome == ACCEPT_DIRECT


# --- R5: the response row joins to its dossier ----------------------------------


def test_a_stored_response_is_keyed_by_the_dossier_not_the_release():
    """`transport.issue` wrote `dossier_id=payload.release_id`.

    Once `dossier_id` became a content address (R2) that stopped joining to
    anything: every stored response was orphaned from the dossier it answers, and
    `replay_recorded_response`, which looks up by `dossier.dossier_id`, could
    never find one. A capability is not an identity.
    """
    import inspect

    from llm_harness.records import CallPayload, build_call_payload

    assert "dossier_id" in {f.name for f in dataclasses.fields(CallPayload)}
    parameters = inspect.signature(build_call_payload).parameters
    assert parameters["dossier_id"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parameters["dossier_id"].default is inspect.Parameter.empty


def test_transport_never_uses_a_release_id_as_a_dossier_id():
    import ast
    from pathlib import Path

    source = (
        Path(__file__).resolve().parents[2] / "src" / "llm_harness" / "transport.py"
    ).read_text()
    offenders = [
        node.value.lineno
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.keyword)
        and node.arg == "dossier_id"
        and isinstance(node.value, ast.Attribute)
        and node.value.attr == "release_id"
    ]
    assert offenders == [], offenders


# --- two falsey values that meant the opposite of what they said ----------------


def test_an_empty_cited_span_does_not_match_everything():
    """`"" in anything` is True. A model emitting `"cited_span": ""` bypassed span
    checking at every site, and took the metadata branch down with it: the
    `is not None` guard sent an empty string to the substring test rather than to
    the address comparison, so neither check ever ran."""
    from llm_harness.records import Citation
    from llm_harness.validation import _check_citation

    citation = Citation(
        evidence_ref=KEY,
        cited_span="",
        metadata_field_name="not_the_address",
        why_it_supports="why",
    )
    checked, reason = _check_citation(citation, _dossier(), lambda key: RAW)
    assert reason == CITATION_SPAN_MISMATCH
    assert checked.span_matched is False


def test_a_false_unknown_is_not_an_abstention():
    """`"unknown": false` is not the schema's unknown, and it is not an abstention.

    The `is not None` guard read every falsey value as an abstention and threw the
    payload and its citations away: a real claim was recorded as one the model had
    declined to make, with nothing left to check. `validation._validate_claim`
    already required the Mapping shape and called anything else schema-invalid;
    Site A now agrees with it, so the response is rejected rather than
    reinterpreted.
    """
    from llm_harness.sites import _proposal

    for falsey in (False, 0, "", []):
        assert _proposal(handles={}, claim={
            "payload": {"field": "school", "value": "Columbia"},
            "unknown": falsey,
            "citations": [{
                "evidence_ref": KEY,
                "cited_span": REDACTED,
                "why_it_supports": "names it",
            }],
        }) is None, falsey


def test_a_real_unknown_is_still_an_abstention():
    from llm_harness.sites import _proposal

    parsed = _proposal(handles={}, claim={
        "payload": {"field": "school"},
        "unknown": {"insufficiency_statement": "no labelled school"},
    })
    assert parsed is not None
    proposal, citations = parsed
    assert proposal.unknown is True
    assert proposal.citations == ()
    assert citations == ()


def test_a_claim_keeps_its_spans_on_the_way_to_site_a():
    """P6's `Proposal` carries bare keys. A key alone cannot say whether the model
    quoted the release or invented the quotation, so both shapes travel."""
    from llm_harness.sites import _proposal

    parsed = _proposal(handles={}, claim={
        "payload": {"field": "school", "value": "Columbia"},
        "citations": [{
            "evidence_ref": KEY, "cited_span": REDACTED,
            "why_it_supports": "names it",
        }],
    })
    assert parsed is not None
    proposal, citations = parsed
    assert proposal.citations == (KEY,)
    assert [item.cited_span for item in citations] == [REDACTED]


def test_the_citation_check_has_no_unreachable_unavailable_branch():
    """`_check_citation` declared `| ValidationUnavailable` and never returned one,
    so every caller carried a branch that could not run. A handling path with no
    reachable cause is a claim about behaviour that is not there, and a reader
    checking whether the check can fail closed would find a lie."""
    import inspect

    from llm_harness.validation import _check_citation, check_citations

    assert "ValidationUnavailable" not in str(
        inspect.signature(_check_citation).return_annotation)
    assert "ValidationUnavailable" not in inspect.getsource(_check_citation)
    # `check_citations` keeps the union: it is the shared entry point, and a
    # missing injected authority reaches it from the site validators.
    assert "ValidationUnavailable" in str(
        inspect.signature(check_citations).return_annotation)
