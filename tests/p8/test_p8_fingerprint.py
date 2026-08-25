"""Deterministic prompt fingerprints and dossier content addresses."""
from __future__ import annotations

import dataclasses
import inspect
import re

import pytest

import llm_harness
from llm_harness.fingerprint import dossier_content_address, prompt_fingerprint
from llm_harness.records import (
    CallPayload,
    MalformedRecord,
    PromptDefinition,
    assemble,
    build_call_payload,
)
from llm_harness.vocabulary import A_FACT, B_GROUP
from privacy.release import RELEASED_FIELDS, ModelTarget


_HEX_DIGEST = re.compile(r"^[0-9a-f]{64}$")


def _model_target() -> ModelTarget:
    return ModelTarget(locality="local", model_id="fixture-model", provider="fixture")


def _prompt(**overrides: object) -> PromptDefinition:
    fields = dict(
        template_id="template.grouping",
        template_bytes=b"TEMPLATE",
        response_schema_bytes=b'{"type":"object"}',
        call_site=A_FACT,
        call_site_version="1",
        shaping_policy_bytes=b'{"policy":"authored"}',
    )
    fields.update(overrides)
    return PromptDefinition(**fields)


def _address(
    released_material: bytes = b"RELEASED-EXCERPT",
    *,
    allowed_vocabulary: tuple[str, ...] = ("school",),
    allowed_schema_bytes: bytes = b'{"type":"object"}',
    **kwargs: object,
) -> str:
    return dossier_content_address(
        released_material,
        allowed_vocabulary=allowed_vocabulary,
        allowed_schema_bytes=allowed_schema_bytes,
        **kwargs,
    )


def test_fingerprint_helpers_are_not_on_the_task_1_public_surface():
    assert llm_harness.__all__ == [
        "Dossier",
        "P8Verdict",
        "Refusal",
        "ValidationUnavailable",
        "NeedsConsent",
    ]
    assert "prompt_fingerprint" not in llm_harness.__all__
    assert "dossier_content_address" not in llm_harness.__all__
    assert not hasattr(llm_harness, "prompt_fingerprint")
    assert not hasattr(llm_harness, "dossier_content_address")


def test_prompt_fingerprint_is_a_digest_not_raw_prompt_or_evidence():
    definition = _prompt()
    digest = prompt_fingerprint(definition)
    assert _HEX_DIGEST.fullmatch(digest)
    assert digest != definition.template_bytes.decode("ascii")
    assert "TEMPLATE" not in digest
    assert '{"type":"object"}' not in digest
    assert '{"policy":"authored"}' not in digest
    assert "RELEASED-EXCERPT" not in digest
    assert definition.template_bytes.hex() not in digest


def test_prompt_fingerprint_changes_when_any_source_field_changes():
    base = prompt_fingerprint(_prompt())
    assert prompt_fingerprint(_prompt(template_bytes=b"TEMPLATE\x00")) != base
    assert prompt_fingerprint(_prompt(response_schema_bytes=b'{"type":"array"}')) != base
    assert prompt_fingerprint(_prompt(call_site=B_GROUP)) != base
    assert prompt_fingerprint(_prompt(call_site_version="2")) != base
    assert prompt_fingerprint(_prompt(shaping_policy_bytes=b'{"policy":"other"}')) != base
    assert prompt_fingerprint(_prompt(template_id="template.other")) != base


def test_prompt_fingerprint_is_stable_under_equivalent_canonical_source_fields():
    first = _prompt()
    rebuilt = PromptDefinition(
        template_id=str(first.template_id),
        template_bytes=bytes(first.template_bytes),
        response_schema_bytes=bytes(first.response_schema_bytes),
        call_site=str(first.call_site),
        call_site_version=str(first.call_site_version),
        shaping_policy_bytes=bytes(first.shaping_policy_bytes),
    )
    assert rebuilt is not first
    assert prompt_fingerprint(rebuilt) == prompt_fingerprint(first)
    assert prompt_fingerprint(_prompt()) == prompt_fingerprint(first)


def test_prompt_fingerprint_hex_encodes_non_utf8_template_bytes():
    binary = _prompt(template_bytes=b"\xff\xfeTEMPLATE")
    digest = prompt_fingerprint(binary)
    assert _HEX_DIGEST.fullmatch(digest)
    assert digest != prompt_fingerprint(_prompt())


def test_build_call_payload_retains_sources_and_assembles_model_visible_bytes():
    definition = _prompt()
    dossier_bytes = b"DOSSIER"
    target = _model_target()
    payload = build_call_payload(
        definition,
        dossier_bytes,
        model_target=target,
        policy_version="policy-1",
        release_id="rel-1",
    )
    assert payload.prompt_definition is definition
    assert payload.canonical_dossier_bytes == dossier_bytes
    assert payload.model_visible_bytes == assemble(definition, dossier_bytes)
    assert payload.model_visible_bytes == definition.template_bytes + dossier_bytes
    assert payload.prompt_fingerprint == prompt_fingerprint(definition)
    assert payload.model_target is target
    assert payload.policy_version == "policy-1"
    assert payload.release_id == "rel-1"
    for provenance in (
        payload.release_id,
        payload.policy_version,
        payload.prompt_fingerprint,
        payload.model_target.model_id,
    ):
        assert provenance.encode("utf-8") not in payload.model_visible_bytes


def test_build_call_payload_binds_released_model_target_and_policy_version():
    target = _model_target()
    policy_version = "policy-1"
    payload = build_call_payload(
        _prompt(),
        b"DOSSIER",
        model_target=target,
        policy_version=policy_version,
        release_id="rel-1",
    )
    assert payload.model_target == target
    assert payload.policy_version == policy_version
    assert "model_target" in RELEASED_FIELDS
    assert "policy_version" in RELEASED_FIELDS


def test_mutating_either_source_changes_the_recomputed_payload():
    definition = _prompt()
    dossier_bytes = b"DOSSIER"
    baseline = build_call_payload(
        definition,
        dossier_bytes,
        model_target=_model_target(),
        policy_version="policy-1",
        release_id="rel-1",
    )
    mutated_definition = dataclasses.replace(
        definition, template_bytes=definition.template_bytes + b"X",
    )
    after_template = build_call_payload(
        mutated_definition,
        dossier_bytes,
        model_target=_model_target(),
        policy_version="policy-1",
        release_id="rel-1",
    )
    after_dossier = build_call_payload(
        definition,
        dossier_bytes + b"Y",
        model_target=_model_target(),
        policy_version="policy-1",
        release_id="rel-1",
    )
    assert after_template.model_visible_bytes != baseline.model_visible_bytes
    assert after_template.prompt_fingerprint != baseline.prompt_fingerprint
    assert after_template.prompt_fingerprint == prompt_fingerprint(mutated_definition)
    assert after_dossier.model_visible_bytes != baseline.model_visible_bytes
    assert after_dossier.prompt_fingerprint == baseline.prompt_fingerprint


def test_factory_cannot_accept_inconsistent_preassembled_bytes():
    assert "model_visible_bytes" not in inspect.signature(build_call_payload).parameters
    definition = _prompt()
    with pytest.raises(MalformedRecord):
        CallPayload(
            prompt_definition=definition,
            canonical_dossier_bytes=b"DOSSIER",
            model_visible_bytes=b"OTHER",
            model_target=_model_target(),
            prompt_fingerprint=prompt_fingerprint(definition),
            policy_version="policy-1",
            release_id="rel-1",
        )


def test_factory_cannot_bind_a_fingerprint_that_does_not_match_the_definition():
    definition = _prompt()
    payload = build_call_payload(
        definition,
        b"DOSSIER",
        model_target=_model_target(),
        policy_version="policy-1",
        release_id="rel-1",
        prompt_fingerprint="not-the-digest",
    )
    assert payload.prompt_fingerprint == prompt_fingerprint(definition)
    assert payload.prompt_fingerprint != "not-the-digest"


def test_dossier_content_address_is_a_digest_of_model_visible_payload():
    address = _address()
    assert _HEX_DIGEST.fullmatch(address)
    assert "RELEASED-EXCERPT" not in address
    assert "school" not in address
    assert '{"type":"object"}' not in address
    assert "rel-1" not in address
    assert "snap-1" not in address


def test_dossier_content_address_is_byte_identical_for_equivalent_payloads():
    first = _address()
    rebuilt = dossier_content_address(
        bytes(b"RELEASED-EXCERPT"),
        allowed_vocabulary=["school"],
        allowed_schema_bytes=bytes(b'{"type":"object"}'),
    )
    assert rebuilt == first
    assert _address() == first


def test_dossier_content_address_changes_when_any_model_visible_byte_changes():
    baseline = _address()
    assert _address(b"RELEASED-EXCERPT\x00") != baseline
    assert _address(allowed_vocabulary=("school", "year")) != baseline
    assert _address(allowed_schema_bytes=b'{"type":"array"}') != baseline


def test_dossier_content_address_excludes_release_and_audit_capability_values():
    baseline = _address()
    assert _address(release_id="rel-1", audit_id=17) == baseline
    assert _address(release_id="rel-other", audit_id=99) == baseline
    parameters = inspect.signature(dossier_content_address).parameters
    assert parameters["release_id"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parameters["audit_id"].kind is inspect.Parameter.KEYWORD_ONLY


def test_evidence_snapshot_id_is_stored_separately_and_does_not_enter_the_address():
    parameters = inspect.signature(dossier_content_address).parameters
    assert "evidence_snapshot_id" in parameters
    assert parameters["evidence_snapshot_id"].kind is inspect.Parameter.KEYWORD_ONLY
    assert _address(evidence_snapshot_id="snap-1") == _address(evidence_snapshot_id="snap-2")
    assert _address(evidence_snapshot_id="snap-1") == _address()
