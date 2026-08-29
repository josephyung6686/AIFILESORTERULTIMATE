# tests/p8/test_p8_dossier.py
"""P8 repair R2: the canonical post-release dossier.

The dossier is the *only* input to a model call (SPEC §1: "the dossier is the actual
input to the LLM"). Before this task `harness._canonical_bytes` newline-joined the
released values and threw away the P7 addresses, the zone, the context fields, the
builder's reference metadata and the conflicts, and `harness._dossier_for` used the
single-use `release_id` as the dossier identity. Both are repaired here.

`dossier_id` is a content address. `release_id` stays beside it as the spend
capability. The two are different things and must not be the same string.
"""
from __future__ import annotations

import json

import pytest

from evidence_shape.location import TextSpan
from llm_harness.dossier import (
    build_dossier,
    canonical_dossier_bytes,
    dossier_address,
)
from llm_harness.records import (
    Conflict,
    DossierRequest,
    EvidenceItem,
    PromptDefinition,
    ReleasedEvidence,
    ValidationUnavailable,
)
from llm_harness.vocabulary import (
    A_FACT,
    CONTEXT_SUPPORTED,
    DIRECT_ANCHOR,
    REDUCTION_NONE,
    REMAINS_AMBIGUOUS,
)
from privacy.items import Excerpt
from privacy.redaction import RedactionManifest
from privacy.release import (
    ModelCallRequest, ModelTarget, Released, ReleasedItem, Target,
)

CLOUD = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")
KEY = "obs-key-1"
OTHER_KEY = "obs-key-2"
VOCABULARY = ("school", "employer")


def _prompt(**overrides) -> PromptDefinition:
    values = dict(
        template_id="template.fact",
        template_bytes=b"TEMPLATE",
        response_schema_bytes=b'{"type":"object"}',
        call_site=A_FACT,
        call_site_version="1",
        shaping_policy_bytes=b'{"policy":"authored"}',
    )
    values.update(overrides)
    return PromptDefinition(**values)


def _model_call_request(*, keys: tuple[str, ...] = (KEY,)) -> ModelCallRequest:
    return ModelCallRequest(
        stage="fact_extraction",
        target=Target(file_ids=("file-1",)),
        model_target=CLOUD,
        requested_items=tuple(
            Excerpt(observation_key=key, span=TextSpan(0, 18), reason="names the school")
            for key in keys
        ),
        prompt_template_id="template.fact",
        prompt_fingerprint="fingerprint.fact",
        max_dossier_tokens=4000,
    )


def _evidence_item(**overrides) -> EvidenceItem:
    values = dict(
        evidence_ref=KEY,
        kind="excerpt",
        location="page-1",
        excerpt_span=(0, 18),
        reliability_state="direct",
        basis=DIRECT_ANCHOR,
    )
    values.update(overrides)
    return EvidenceItem(**values)


def _request(**overrides) -> DossierRequest:
    values = dict(
        call_site=A_FACT,
        subject_ref="file-1",
        eligibility_reason=REMAINS_AMBIGUOUS,
        evidence_items=(_evidence_item(),),
        conflicts=(),
        model_call_request=_model_call_request(),
        plan_version=None,
        evidence_snapshot_id="snap-1",
    )
    values.update(overrides)
    return DossierRequest(**values)


def _materialised(**overrides) -> ReleasedItem:
    values = dict(
        observation_key=KEY,
        span="0:18",
        value="Columbia University",
        zone="body",
        unit_length=64,
    )
    values.update(overrides)
    return ReleasedItem(**values)


def _released(**overrides) -> Released:
    values = dict(
        release_id="rel-1",
        audit_id=17,
        policy_version="policy-1",
        materialised_items=(_materialised(),),
        redaction_manifest=RedactionManifest(entries=()),
        model_target=CLOUD,
    )
    values.update(overrides)
    return Released(**values)


def _build(**overrides):
    values = dict(
        request=_request(),
        released=_released(),
        reduction_rung=REDUCTION_NONE,
        allowed_vocabulary=VOCABULARY,
        prompt=_prompt(),
    )
    values.update(overrides)
    request = values.pop("request")
    released = values.pop("released")
    return build_dossier(request, released, **values)


def _body(dossier=None, prompt=None) -> dict:
    dossier = dossier if dossier is not None else _build()
    prompt = prompt if prompt is not None else _prompt()
    return json.loads(canonical_dossier_bytes(dossier, prompt).decode("utf-8"))


# --- the common envelope --------------------------------------------------------


def test_canonical_bytes_carry_the_common_envelope():
    body = _body()
    assert body["call_site"] == A_FACT
    assert body["subject_ref"] == "file-1"
    assert body["eligibility_reason"] == REMAINS_AMBIGUOUS
    assert body["plan_version"] is None
    assert body["policy_version"] == "policy-1"
    assert body["max_dossier_tokens"] == 4000
    assert body["reduction_rung"] == REDUCTION_NONE


def test_canonical_bytes_carry_every_allowed_vocabulary_member():
    assert _body()["allowed_vocabulary"] == list(VOCABULARY)


def test_canonical_bytes_never_carry_the_release_capability():
    raw = canonical_dossier_bytes(_build(), _prompt())
    assert b"rel-1" not in raw
    body = json.loads(raw.decode("utf-8"))
    assert "release_id" not in body
    assert "audit_id" not in body
    assert "dossier_id" not in body


# --- what P7 actually released --------------------------------------------------


def test_canonical_bytes_carry_the_full_released_item_not_a_joined_value():
    item = _body()["released_evidence"][0]
    assert item["observation_key"] == KEY
    assert item["address"] == "0:18"
    assert item["value"] == "Columbia University"
    assert item["zone"] == "body"
    # And nothing else. The released item carried the raw text on either side of
    # the requested span; §8.4 keeps "complete extracted text" local.
    assert set(item) == {"observation_key", "address", "value", "zone"}


def test_the_materialised_dossier_retains_an_immutable_released_evidence_map():
    dossier = _build()
    assert dossier.released_evidence == (
        ReleasedEvidence(
            observation_key=KEY,
            address="0:18",
            value="Columbia University",
            zone="body",
        ),
    )
    with pytest.raises(AttributeError):
        dossier.released_evidence = ()


def test_redacted_released_values_travel_as_released_never_as_raw():
    released = _released(
        materialised_items=(_materialised(value="[REDACTED-NAME] University"),),
    )
    item = _body(_build(released=released))["released_evidence"][0]
    assert item["value"] == "[REDACTED-NAME] University"
    assert "Columbia" not in json.dumps(item)


# --- builder-owned reference metadata -------------------------------------------


def test_canonical_bytes_carry_builder_reference_metadata_verbatim():
    request = _request(
        evidence_items=(
            _evidence_item(
                kind="member",
                location="folder-3",
                excerpt_span=None,
                reliability_state="validated",
                basis=CONTEXT_SUPPORTED,
            ),
        ),
    )
    item = _body(_build(request=request))["evidence_items"][0]
    assert item["evidence_ref"] == KEY
    assert item["kind"] == "member"
    assert item["location"] == "folder-3"
    assert item["excerpt_span"] is None
    assert item["reliability_state"] == "validated"
    assert item["basis"] == CONTEXT_SUPPORTED


def test_p8_does_not_synthesise_basis_kind_or_reliability():
    """§1: `basis` is supplied by the dossier builder, never inferred by P8."""
    request = _request(
        evidence_items=(_evidence_item(basis=CONTEXT_SUPPORTED, kind="member"),),
    )
    dossier = _build(request=request)
    assert dossier.evidence_items == request.evidence_items


def test_canonical_bytes_carry_the_builders_conflicts():
    request = _request(conflicts=(Conflict(conflict_id="c-9", kind="target_institution"),))
    conflicts = _body(_build(request=request))["conflicts"]
    assert conflicts == [{"conflict_id": "c-9", "kind": "target_institution"}]


# --- the authored response schema and shaping policy ----------------------------


def test_canonical_bytes_carry_the_authored_schema_and_shaping_policy():
    body = _body()
    assert body["response_schema"] == '{"type":"object"}'
    assert body["shaping_policy"] == '{"policy":"authored"}'


# --- the address ----------------------------------------------------------------


def test_dossier_id_is_the_content_address_and_not_the_release_id():
    dossier = _build()
    assert dossier.release_id == "rel-1"
    assert dossier.dossier_id != dossier.release_id
    assert dossier.dossier_id == dossier_address(dossier, _prompt())
    assert len(dossier.dossier_id) == 64


def test_equivalent_released_content_under_two_release_ids_has_one_address():
    first = _build()
    second = _build(released=_released(release_id="rel-2", audit_id=99))
    assert first.release_id != second.release_id
    assert first.dossier_id == second.dossier_id
    assert canonical_dossier_bytes(first, _prompt()) == canonical_dossier_bytes(
        second, _prompt()
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        pytest.param(
            {"released": _released(materialised_items=(_materialised(value="Cornell"),))},
            id="released-value",
        ),
        pytest.param(
            {"released": _released(materialised_items=(_materialised(zone="footer"),))},
            id="released-zone",
        ),
        pytest.param({"allowed_vocabulary": ("school",)}, id="vocabulary"),
        pytest.param(
            {"prompt": _prompt(response_schema_bytes=b'{"type":"array"}')},
            id="response-schema",
        ),
        pytest.param(
            {"prompt": _prompt(shaping_policy_bytes=b'{"policy":"other"}')},
            id="shaping-policy",
        ),
        pytest.param(
            {"request": _request(evidence_items=(_evidence_item(kind="member"),))},
            id="builder-kind",
        ),
        pytest.param(
            {"request": _request(conflicts=(Conflict(conflict_id="c-9", kind="k"),))},
            id="builder-conflicts",
        ),
        pytest.param({"reduction_rung": "summarized_facts"}, id="reduction-rung"),
    ],
)
def test_any_model_visible_change_changes_the_address(kwargs):
    assert _build(**kwargs).dossier_id != _build().dossier_id


# --- the three-way key match ----------------------------------------------------


def test_a_released_key_with_no_builder_metadata_is_validation_unavailable():
    released = _released(
        materialised_items=(_materialised(), _materialised(observation_key=OTHER_KEY)),
    )
    result = _build(released=released, request=_request(
        model_call_request=_model_call_request(keys=(KEY, OTHER_KEY)),
    ))
    assert isinstance(result, ValidationUnavailable)
    assert "builder_evidence_metadata" in result.missing


def test_a_released_key_that_was_never_requested_is_validation_unavailable():
    released = _released(materialised_items=(_materialised(observation_key=OTHER_KEY),))
    request = _request(evidence_items=(_evidence_item(evidence_ref=OTHER_KEY),))
    result = _build(request=request, released=released)
    assert isinstance(result, ValidationUnavailable)
    assert "released_key_not_requested" in result.missing


def test_a_release_with_nothing_materialised_is_validation_unavailable():
    result = _build(released=_released(materialised_items=()))
    assert isinstance(result, ValidationUnavailable)
    assert "released_evidence" in result.missing


def test_structural_builder_items_may_exceed_the_released_keys():
    """A Site-B candidate member is a reference, not a released observation."""
    request = _request(
        evidence_items=(
            _evidence_item(),
            _evidence_item(evidence_ref="file-7", kind="member", excerpt_span=None),
        ),
    )
    dossier = _build(request=request)
    assert not isinstance(dossier, ValidationUnavailable)
    assert len(dossier.evidence_items) == 2
    assert len(dossier.released_evidence) == 1


# --- the guard ------------------------------------------------------------------


def test_only_the_dossier_module_and_the_fixtures_construct_a_dossier():
    """One writer. `harness._dossier_for` was the second, and it used `release_id`."""
    import ast
    from pathlib import Path

    root = Path(__file__).resolve().parents[2] / "src" / "llm_harness"
    offenders = []
    for path in sorted(root.glob("*.py")):
        if path.name in {"dossier.py", "fixtures.py"}:
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "Dossier"
            ):
                offenders.append(f"{path.name}:{node.lineno}")
    assert offenders == [], (
        "a second dossier writer can address a dossier differently from "
        f"build_dossier: {offenders}"
    )


def test_the_injected_authorities_reach_the_model_as_text_not_hex():
    """`_body` is the exact bytes the model is shown. `response_schema_bytes` and
    `shaping_policy_bytes` are the two injected authorities meant to constrain the
    model's answer, and hex renders both unreadable to it. Hex is right for the
    fingerprint, where `canonical_json` cannot encode raw bytes; it is wrong here.
    """
    prompt = _prompt(
        response_schema_bytes=b'{"type":"object","required":["claims"]}',
        shaping_policy_bytes=b'{"policy":"one claim per field"}',
    )
    raw = canonical_dossier_bytes(_build(prompt=prompt), prompt).decode("utf-8")
    body = json.loads(raw)
    assert body["response_schema"] == '{"type":"object","required":["claims"]}'
    assert body["shaping_policy"] == '{"policy":"one claim per field"}'
    assert prompt.response_schema_bytes.hex() not in raw
    assert prompt.shaping_policy_bytes.hex() not in raw


def test_an_authority_the_model_cannot_read_is_refused():
    """P8 authors neither, and shows the model whatever it is handed. Bytes that
    are not text are not something the model can be constrained by."""
    from llm_harness.records import MalformedRecord

    prompt = _prompt(response_schema_bytes=b"\xff\xfe not text")
    with pytest.raises(MalformedRecord):
        canonical_dossier_bytes(_build(prompt=prompt), prompt)
