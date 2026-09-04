# tests/p8/test_p8_folder_levels.py
"""The template's own structure, carried to the model inside the dossier.

**What was broken.** `allowed_vocabulary` is a FLAT list -- `active_field_allowlist`
is "the universal fields plus every active schema's field SET, deduplicated" -- and
nothing in it says which of those fields the person's chosen situation actually
builds folders out of, which of those are required, or in what order. Measured on a
real cloud run over 199 files: 59 `file_type`, 34 `authored_by`, 19 `creation_date`
and ONE `work_type`, the required level that decides where the file goes.

The model was answering the question it was asked. This is the missing half of the
question: the shipped template library already holds, per situation, an ordered list
of `(field, label, requirement)` -- "Course" required, "Kind of work" required, "My
school" optional -- and none of it reached the dossier.

**The one-computation rule.** `model_facts.pending_fields_for` warns that "a model
measured against one list and validated against another can be rejected for obeying
its instructions". `folder_levels` is therefore a PROJECTION of
`allowed_vocabulary`, never a second vocabulary: every field it names is a member of
the list the validator holds, and `released_content_digest` recomputes that
relationship rather than trusting it -- the same posture it already takes for
`field_glossary`.

**Privacy.** A level carries a field key, a library label and a library word. All
three are the same on every file in every corpus, which is what these tests pin: two
dossiers built from two different files carry byte-identical `folder_levels`. Nothing
in §8.4's always-local set has a route in, because nothing about the file reaches
this key at all.
"""
from __future__ import annotations

import json

import pytest

from evidence_shape.location import TextSpan
from llm_harness.dossier import build_dossier, canonical_dossier_bytes
from llm_harness.records import (
    DossierRequest,
    EvidenceItem,
    FolderLevel,
    MalformedRecord,
    PromptDefinition,
)
from llm_harness.released_content import DOSSIER_BODY_KEYS, released_content_digest
from llm_harness.vocabulary import (
    A_FACT,
    B_GROUP,
    COHERENCE_JUDGEMENT,
    DIRECT_ANCHOR,
    REDUCTION_NONE,
    REMAINS_AMBIGUOUS,
)
from llm_harness.fixtures import FIXTURE_HANDLE_KEY
from privacy.items import Excerpt
from privacy.redaction import RedactionManifest
from privacy.release import (
    ModelCallRequest, ModelTarget, Released, ReleasedItem, Target,
)


CLOUD = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")
KEY = "obs-key-1"
VOCABULARY = ("file_type", "authored_by", "school", "term", "subject", "work_type")

#: `academic.coursework` as the shipped library declares it: the definition's
#: `default_order` joined to the applicability row's `role_bindings`.
COURSEWORK = (
    FolderLevel(field="school", label="My school", requirement="optional"),
    FolderLevel(field="term", label="Semester", requirement="optional"),
    FolderLevel(field="subject", label="Course", requirement="required"),
    FolderLevel(field="work_type", label="Kind of work", requirement="required"),
)


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


def _request(*, subject_ref: str = "file-1", call_site: str = A_FACT,
             eligibility_reason: str = REMAINS_AMBIGUOUS) -> DossierRequest:
    return DossierRequest(
        call_site=call_site,
        subject_ref=subject_ref,
        eligibility_reason=eligibility_reason,
        evidence_items=(EvidenceItem(
            evidence_ref=KEY, kind="excerpt", location="page-1",
            excerpt_span=(0, 18), reliability_state="direct", basis=DIRECT_ANCHOR),),
        conflicts=(),
        model_call_request=ModelCallRequest(
            stage="fact_interpretation",
            target=Target(file_ids=(subject_ref,)),
            model_target=CLOUD,
            requested_items=(Excerpt(
                observation_key=KEY, span=TextSpan(0, 18), reason="names the course"),),
            prompt_template_id="template.fact",
            prompt_fingerprint="fingerprint.fact",
            max_dossier_tokens=4000),
        plan_version=None,
        evidence_snapshot_id="snap-1",
    )


def _released(value: str = "Columbia University") -> Released:
    return Released(
        release_id="rel-1", audit_id=17, policy_version="policy-1",
        materialised_items=(ReleasedItem(
            observation_key=KEY, span="0:18", value=value, zone="body",
            unit_length=64),),
        redaction_manifest=RedactionManifest(entries=()),
        model_target=CLOUD,
    )


def _build(*, folder_levels=COURSEWORK, subject_ref="file-1", value="Columbia University",
           allowed_vocabulary=VOCABULARY, call_site=A_FACT,
           eligibility_reason=REMAINS_AMBIGUOUS):
    return build_dossier(
        _request(subject_ref=subject_ref, call_site=call_site,
                 eligibility_reason=eligibility_reason),
        _released(value),
        reduction_rung=REDUCTION_NONE,
        allowed_vocabulary=allowed_vocabulary,
        folder_levels=folder_levels,
        prompt=_prompt(),
        handle_key=FIXTURE_HANDLE_KEY,
    )


def _body(**kwargs) -> dict:
    dossier = _build(**kwargs)
    assert not isinstance(dossier, Exception), dossier
    return json.loads(canonical_dossier_bytes(
        dossier, _prompt(), handle_key=FIXTURE_HANDLE_KEY).decode("utf-8"))


# --- the key reaches the model --------------------------------------------------


def test_the_body_carries_the_situations_levels_in_the_librarys_order():
    """Order is position, requirement is the library's word, label is its label.

    This is the whole repair: before it, the bytes the model saw said nothing about
    `work_type` beyond its presence in a flat list of nineteen keys.
    """
    assert _body()["folder_levels"] == [
        {"field": "school", "label": "My school", "requirement": "optional"},
        {"field": "term", "label": "Semester", "requirement": "optional"},
        {"field": "subject", "label": "Course", "requirement": "required"},
        {"field": "work_type", "label": "Kind of work", "requirement": "required"},
    ]


def test_the_door_recognises_the_key():
    """`released_content_digest` reads `set(body) != DOSSIER_BODY_KEYS` by EQUALITY,
    so a key the builder writes and the door does not list refuses every call."""
    assert "folder_levels" in DOSSIER_BODY_KEYS


def test_a_call_site_with_no_template_carries_an_empty_list_not_a_missing_key():
    """B, C and D design no folder tree. The truthful answer is `[]`, and it is
    PRESENT: the door's key check is equality, and an absent key is a refusal."""
    assert _body(folder_levels=(), call_site=B_GROUP,
                 eligibility_reason=COHERENCE_JUDGEMENT)["folder_levels"] == []


# --- the projection invariant ---------------------------------------------------


def test_a_level_naming_a_field_outside_the_vocabulary_is_refused_at_the_builder():
    """The failure this prevents is the one `pending_fields_for` names: a model told
    to fill a field the validator will reject for not being in the active schema."""
    with pytest.raises(MalformedRecord):
        _build(folder_levels=(
            FolderLevel(field="instructor", label="Teacher", requirement="required"),))


def test_the_door_recomputes_the_projection_rather_than_trusting_it():
    """A body whose `folder_levels` names a field its own `allowed_vocabulary` does
    not carry is refused BEFORE the spend, the way `field_glossary` already is."""
    dossier = _build()
    prompt = _prompt()
    raw = canonical_dossier_bytes(dossier, prompt, handle_key=FIXTURE_HANDLE_KEY)
    # Clean bytes pass.
    released_content_digest(raw, prompt_definition=prompt, policy_version="policy-1")
    body = json.loads(raw.decode("utf-8"))
    body["folder_levels"] = [
        {"field": "instructor", "label": "Teacher", "requirement": "required"}]
    tampered = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    with pytest.raises(MalformedRecord):
        released_content_digest(
            tampered, prompt_definition=prompt, policy_version="policy-1")


def test_the_door_refuses_a_level_entry_of_the_wrong_shape():
    dossier = _build()
    prompt = _prompt()
    body = json.loads(canonical_dossier_bytes(
        dossier, prompt, handle_key=FIXTURE_HANDLE_KEY).decode("utf-8"))
    body["folder_levels"] = [
        {"field": "subject", "label": "Course", "requirement": "required",
         "hint": "look in the header"}]
    tampered = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    with pytest.raises(MalformedRecord):
        released_content_digest(
            tampered, prompt_definition=prompt, policy_version="policy-1")


# --- §8.4: the key is corpus-independent ----------------------------------------


def test_two_files_in_one_run_carry_byte_identical_levels():
    """A template label is safe; an example drawn from the person's corpus is not.
    Nothing about the file, the subject or the evidence reaches this key, and the
    only way to say so is to build two dossiers that differ in all three."""
    first = _body(subject_ref="file-1", value="Columbia University")
    second = _body(subject_ref="file-2", value="Hong Kong Baptist University")
    assert first["subject_ref"] != second["subject_ref"]
    assert first["released_evidence"] != second["released_evidence"]
    assert first["folder_levels"] == second["folder_levels"]


def test_no_released_value_or_subject_text_appears_in_the_levels():
    body = _body(subject_ref="Desktop/Python 1006/homework0.py",
                 value="Columbia University")
    printed = json.dumps(body["folder_levels"])
    assert "Columbia" not in printed
    assert "homework0" not in printed
    assert "Python 1006" not in printed
