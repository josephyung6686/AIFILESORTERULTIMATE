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

import dataclasses
import json

import pytest

from evidence_shape.location import TextSpan
from llm_harness.dossier import (
    build_dossier, canonical_dossier_bytes, dossier_from_stored_body,
)
from llm_harness.records import (
    DossierRequest,
    EvidenceItem,
    FolderLevel,
    MalformedRecord,
    NodeFolderLevel,
    PromptDefinition,
)
from llm_harness.released_content import DOSSIER_BODY_KEYS, released_content_digest
from llm_harness.vocabulary import (
    A_FACT,
    B_GROUP,
    C_PLACEMENT,
    COHERENCE_JUDGEMENT,
    DIRECT_ANCHOR,
    REDUCTION_NONE,
    REMAINS_AMBIGUOUS,
    SEVERAL_LEGAL_NODES_PLAUSIBLE,
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
             eligibility_reason: str = REMAINS_AMBIGUOUS,
             plan_version: str | None = None) -> DossierRequest:
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
        plan_version=plan_version,
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
           eligibility_reason=REMAINS_AMBIGUOUS, plan_version=None):
    return build_dossier(
        _request(subject_ref=subject_ref, call_site=call_site,
                 eligibility_reason=eligibility_reason,
                 plan_version=plan_version),
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


# --- `104` R-77: the C shape of the same key ------------------------------------
#
# §13.6's schema half. The amended C row (`c_placement.unratified.
# eliminate-v2r-group-levels.2026-09-11`, line 33, written on the owner's "Yes,
# change it" of 11 Sep 2026) says what the key carries at site C: *"folder_levels
# lists, for each candidate node, the levels of the tree that node sits under,
# each by its name and the value that names its folder; a level you assign a file
# to must be one of these, spelled as listed, and a level that is not listed for a
# node does not exist there."*
#
# The projection invariant above is unchanged and only its subject moves. At A the
# vocabulary is the domain's field keys and a level names one of them; at C the
# vocabulary is the shortlist's node ids and a level belongs to one of them. That
# is the second of G9's three blockers closed: the old check refused any level
# whose `field` was outside `allowed_vocabulary`, and at C every level field is
# outside it by construction.

C_NODES = ("node-hw", "node-course")

#: One candidate's chain as the frozen tree holds it: `Node.dimension` beside the
#: `ExpectedValue` P10 wrote at that level, accumulated root-to-leaf by
#: `materialise._project`. Synthetic, like everything else in this file.
NODE_LEVELS = (
    NodeFolderLevel(node="node-course", level="subject", value="PHYS 1401"),
    NodeFolderLevel(node="node-hw", level="subject", value="PHYS 1401"),
    NodeFolderLevel(node="node-hw", level="work_type", value="Homework"),
)


def _c_build(**kwargs):
    values = dict(folder_levels=NODE_LEVELS, allowed_vocabulary=C_NODES,
                  call_site=C_PLACEMENT,
                  eligibility_reason=SEVERAL_LEGAL_NODES_PLAUSIBLE,
                  plan_version="plan-1")
    values.update(kwargs)
    return _build(**values)


def _c_body(**kwargs) -> dict:
    dossier = _c_build(**kwargs)
    assert not isinstance(dossier, Exception), dossier
    return json.loads(canonical_dossier_bytes(
        dossier, _prompt(), handle_key=FIXTURE_HANDLE_KEY).decode("utf-8"))


def test_the_c_body_carries_each_candidates_levels_by_name_and_value():
    """The amended row's sentence, as bytes. One entry per `(node, level)`, in the
    shortlist's order and each node's own root-to-leaf order."""
    assert _c_body()["folder_levels"] == [
        {"level": "subject", "node": "node-course", "value": "PHYS 1401"},
        {"level": "subject", "node": "node-hw", "value": "PHYS 1401"},
        {"level": "work_type", "node": "node-hw", "value": "Homework"},
    ]


def test_under_a_row_that_lists_nothing_the_c_key_is_the_empty_list_it_always_was():
    """`104` R-77's compatibility half, and the reason site C can keep observing
    the ratified row while this is built. Every C row through
    `eliminate-v2r-group` says the key is EMPTY at this site; under one of those
    the builder is handed nothing and writes `[]`, which is the same byte string
    it wrote before this shape existed."""
    assert _c_body(folder_levels=())["folder_levels"] == []


def test_levels_attributed_to_a_node_off_the_shortlist_are_refused_at_the_builder():
    """The projection invariant, in C's terms: levels about a folder the model may
    not answer with are levels no answer of its own can ever spell."""
    with pytest.raises(MalformedRecord):
        _c_build(folder_levels=(
            NodeFolderLevel(node="node-elsewhere", level="subject",
                            value="PHYS 1401"),))


def test_the_door_recomputes_the_c_projection_rather_than_trusting_it():
    """A body whose `folder_levels` describes a node its own `allowed_vocabulary`
    does not carry is refused BEFORE the spend, exactly as the A shape is."""
    prompt = _prompt()
    dossier = _c_build()
    raw = canonical_dossier_bytes(dossier, prompt, handle_key=FIXTURE_HANDLE_KEY)
    released_content_digest(raw, prompt_definition=prompt, policy_version="policy-1")
    body = json.loads(raw.decode("utf-8"))
    body["folder_levels"] = [
        {"level": "subject", "node": "node-elsewhere", "value": "PHYS 1401"}]
    tampered = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    with pytest.raises(MalformedRecord):
        released_content_digest(
            tampered, prompt_definition=prompt, policy_version="policy-1")


def test_the_door_refuses_a_c_level_entry_carrying_a_fourth_key():
    """`FolderLevel`'s own sentence, over the C record: a fourth key is how an
    example drawn from the person's corpus would travel beside a tree constant."""
    prompt = _prompt()
    dossier = _c_build()
    body = json.loads(canonical_dossier_bytes(
        dossier, prompt, handle_key=FIXTURE_HANDLE_KEY).decode("utf-8"))
    body["folder_levels"] = [
        {"level": "subject", "node": "node-hw", "value": "PHYS 1401",
         "hint": "the heading says so"}]
    tampered = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    with pytest.raises(MalformedRecord):
        released_content_digest(
            tampered, prompt_definition=prompt, policy_version="policy-1")


def test_a_dossier_may_not_mix_the_two_level_shapes():
    """One sentence per site, and a list carrying both shapes is a dossier no
    sentence is true of."""
    with pytest.raises(MalformedRecord):
        _c_build(folder_levels=(COURSEWORK[2], NODE_LEVELS[0]),
                 allowed_vocabulary=C_NODES + VOCABULARY)


def test_two_files_offered_one_shortlist_carry_byte_identical_c_levels():
    """§8.4, over the C shape. Every value here is the frozen tree's and the
    shortlist's; nothing about the file has a route in."""
    first = _c_body(subject_ref="file-1", value="Columbia University")
    second = _c_body(subject_ref="file-2", value="Hong Kong Baptist University")
    assert first["subject_ref"] != second["subject_ref"]
    assert first["released_evidence"] != second["released_evidence"]
    assert first["folder_levels"] == second["folder_levels"]


def test_a_stored_c_dossier_rebuilds_with_its_levels_intact():
    """`store.load_dossier` compares the rebuilt record against the row key by key,
    so a rebuild that assumed the A shape would be `MalformedRecord` out of every
    reuse decision R-127 makes about a C response."""
    dossier = _c_build()
    rebuilt = dossier_from_stored_body(
        dataclasses.asdict(dossier), release_id=dossier.release_id)
    assert rebuilt.folder_levels == NODE_LEVELS
