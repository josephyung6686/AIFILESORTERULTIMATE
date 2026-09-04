# tests/p7/test_p7_no_safety_evidence.py
"""A class is not evidence of having looked, and §8.4's precondition wanted the latter.

`96` §19 measured what raising classification cost. Of 78 files stored
`personal_non_sensitive, protected=0`, **41 matched no safety work type at all** --
including `2025209423_Joseph_Yung_HKID.pdf`, a Hong Kong identity card read to 21
observations. Before that night those 41 carried no classification row, and §8.4 makes
a handling class a precondition of any model call, so the silence was holding the door
shut. Raising classification opened it for all 41 and gained no evidence to justify
any of them.

`96` §20 states the fix as a property rather than a mechanism: *"the precondition
would then be satisfied by evidence of having LOOKED, not merely by a class
existing."* Two halves, and the second is the one this file is for:

  KNOWS IT   `detector._safety_readings_in_evidence` already returns exactly the
             empty set for those 41 files, and is already computed on the classify
             path.
  CANNOT SAY IT  the only field carrying that meaning is
             `ClassificationRecord.basis`, whose vocabulary is
             `privacy.vocabulary.CLASSIFICATION_BASES` -- closed at three.

So a fourth member, and the gate reading it. The weaker claim gets the weaker word:
`detector_no_safety_evidence` is `detector` minus the one thing that would make a
negative worth acting on.

**This is not the over-protection collapse and does not go near it.** Nothing here
marks a file protected, changes a handling class, or removes a file from placement.
The 41 stay `personal_non_sensitive, protected=0` and stay locally placeable. What
changes is that a CLOUD model call on one is refused, because the product has not
established the thing that call would depend on.
"""
from __future__ import annotations

import dataclasses
import hashlib
import sqlite3
import tempfile
from pathlib import Path

import pytest

from database_agent.files_table import record_file
from evidence_shape.canonical import canonical_json
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.locator import serialize_locator
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import (
    TextUnit, new_id, record_observation, record_run, record_text_unit,
)

from privacy.authorship import COMPONENT_VERSION
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.defaults import MORE_REDACTING
from privacy.denial import (
    DECIDABLE_FROM_REQUEST, DENIAL_ORDER, no_safety_evidence_denies,
)
from privacy.gate import Gate
from privacy.items import Excerpt
from privacy.policy import Policy, UNSET_POLICY_VERSION, set_policy
from privacy.release import Denied, ModelCallRequest, ModelTarget, Released, Target
from privacy.schema import create_privacy_schema
from privacy.vocabulary import (
    CLASSIFICATION_BASES, DETECTOR, DETECTOR_NO_SAFETY_EVIDENCE, OutOfVocabulary,
    check_denial_reason,
)

OBSERVED_AT = "2026-08-22T09:00:00Z"
PLAN_VERSION = "plan-v1"
TEXT = "Homework 3 is due on Friday. Show your working for every part."
SPAN = TextSpan(start=0, end=10)
LOCAL = ModelTarget(locality="local", model_id="llama-local", provider="on-device")
CLOUD = ModelTarget(locality="cloud", model_id="big-model", provider="a-provider")


# --------------------------------------------------------------------------
# seeding
# --------------------------------------------------------------------------

def _file(conn: sqlite3.Connection, name: str, content_hash: str) -> str:
    corpus = Path(tempfile.mkdtemp()) / "corpus"
    corpus.mkdir()
    path = corpus / name
    path.write_bytes(b"%PDF-1.4 fixture bytes")
    return record_file(
        conn, path, filename=name,
        normalized_filename=name.lower(), extension=Path(name).suffix,
        observed_size=4096,
        observed_timestamps=canonical_json({"modified": OBSERVED_AT}),
        parent_folder_context="corpus", mime_type="application/pdf",
        detected_format="pdf", scan_state="scanned", materialized=True,
        content_hash=content_hash)


def _evidence(conn: sqlite3.Connection, file_id: str, content_hash: str) -> str:
    # P4's runs are keyed on P1's real digest (R1), so the evidence side hashes the
    # fixture's label rather than storing it -- the same shape `test_p7_release`
    # uses, and the reason its `_evidence` and `_classify` disagree about the hash.
    digest = hashlib.sha256(content_hash.encode()).hexdigest()
    run_id = new_id()
    page = (Segment(kind="page", index=1),)
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=digest,
        extractor_name="fixture.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=OBSERVED_AT, observation_count=1))
    # The unit the span is a substring OF. Without it every RELEASE here would fail
    # on `UnresolvableSpan`, which would make the two control tests pass for a
    # reason that has nothing to do with the basis under test.
    record_text_unit(conn, TextUnit(run_id=run_id, container_path=page, text=TEXT))
    location = Location(zone="body", container_path=page, text_span=SPAN)
    record_observation(conn, Observation(
        file_id=file_id, content_hash=digest, extractor_name="fixture.text",
        extractor_version="1.0.0", source_type="text_document",
        raw_value=TEXT[SPAN.start:SPAN.end], location=location, occurrence_count=1,
        observed_at=OBSERVED_AT, reliability="direct", run_id=run_id,
        context_before=TEXT[:SPAN.start], context_after=TEXT[SPAN.end:],
        context_truncated=False))
    return observation_key(
        content_hash=digest, extractor_name="fixture.text",
        locator=serialize_locator(location), raw_value=TEXT[SPAN.start:SPAN.end])


def _policy(conn: sqlite3.Connection, mode: str, *, grants=()) -> Policy:
    draft = Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode=mode,
        consent_grants=tuple(grants), redaction_settings=dict(MORE_REDACTING),
        automatic_move_permissions={}, plan_version=PLAN_VERSION, set_at=OBSERVED_AT)
    version = set_policy(conn, draft, component_version=COMPONENT_VERSION,
                         user_id="joseph", reason="test fixture")
    return dataclasses.replace(draft, policy_version=version)


def _classify(conn: sqlite3.Connection, file_id: str, content_hash: str, *,
              basis: str, handling_class: str = "personal_non_sensitive",
              protected: bool = False) -> None:
    """The ordinary detector outcome, with the basis under test."""
    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash, handling_class=handling_class,
        protected=protected, basis=basis,
        evidence_refs=(observation_key(
            content_hash="a" * 64, extractor_name="fixture.text",
            locator="body:page=1#0-10", raw_value="Homework 3"),),
        reliability_state="possible", observed_at=OBSERVED_AT))


def _gate(conn: sqlite3.Connection, **overrides) -> Gate:
    keywords: dict[str, object] = {
        "store": ClassificationStore(conn),
        "plan_version": PLAN_VERSION,
        "classifier": lambda value, *, context_before=None, context_after=None:
            "fixture-identifier-class",
        "transform": lambda value, *, identifier_class: "[redacted]",
        "unclassified_permits_local": False,
        "scope_for": lambda file_id: "area-1",
        "files_in_scope": lambda scope: (),
        "component_version": COMPONENT_VERSION,
        "now": lambda: OBSERVED_AT,
        "user_id": "joseph",
    }
    keywords.update(overrides)
    return Gate(conn, **keywords)


def _request(*, items, model_target=CLOUD, file_ids=("f1",)) -> ModelCallRequest:
    return ModelCallRequest(
        stage="grouping", target=Target(file_ids=tuple(file_ids)),
        model_target=model_target, requested_items=tuple(items),
        prompt_template_id="template.grouping",
        prompt_fingerprint="fingerprint.grouping", max_dossier_tokens=4000)


@pytest.fixture()
def gate_conn(p7_conn):
    create_privacy_schema(p7_conn)
    return p7_conn


def _ordinary_file(conn, name="homework.pdf", digest="hash-homework"):
    file_id = _file(conn, name, digest)
    return file_id, digest, _evidence(conn, file_id, digest)


# --------------------------------------------------------------------------
# the vocabulary: a fourth member, and what it does NOT do
# --------------------------------------------------------------------------

def test_the_basis_vocabulary_gains_a_fourth_member_and_stays_closed():
    """`96` §20: "a fourth member is needed to express it".

    Asserted as an equality rather than a membership, because a closed vocabulary
    that only ever grows by assertion is not closed. A fifth member is a red test
    and a decision, which is exactly what SPEC §2's three were.
    """
    assert CLASSIFICATION_BASES == (
        "detector", "detector_no_safety_evidence", "safety_domain", "user")
    assert DETECTOR_NO_SAFETY_EVIDENCE == "detector_no_safety_evidence"
    assert DETECTOR_NO_SAFETY_EVIDENCE in CLASSIFICATION_BASES


def test_the_weak_basis_is_a_different_word_from_the_strong_one():
    """`detector` must keep meaning what it meant.

    The whole value of the new member is that the two are TOLD APART. A rename that
    made them equal, or an alias, would leave the 41 files saying exactly what they
    said before.
    """
    assert DETECTOR_NO_SAFETY_EVIDENCE != DETECTOR


def test_the_weak_basis_is_still_an_evidence_backed_classification():
    """§8.4: the classification "is itself evidence-backed".

    The weakness is about SAFETY evidence, not about evidence. A record on this
    basis still cites the observations the ordinary schema was recognised from, and
    a record citing nothing is still refused.
    """
    with pytest.raises(Exception):
        ClassificationRecord(
            file_id="f1", content_hash="h1",
            handling_class="personal_non_sensitive", protected=False,
            basis=DETECTOR_NO_SAFETY_EVIDENCE, evidence_refs=(),
            reliability_state="possible", observed_at=OBSERVED_AT)


def test_a_basis_outside_the_four_is_still_refused():
    with pytest.raises(OutOfVocabulary):
        ClassificationRecord(
            file_id="f1", content_hash="h1",
            handling_class="personal_non_sensitive", protected=False,
            basis="detector_probably", evidence_refs=("k",),
            reliability_state="possible", observed_at=OBSERVED_AT)


# --------------------------------------------------------------------------
# the denial: a ninth reason, because the eighth would have to lie
# --------------------------------------------------------------------------

def test_the_denial_reason_is_its_own_and_not_borrowed_from_unclassified():
    """`deny_unclassified` says "no classification record exists". This file HAS one.

    Reusing that reason would put the same untruth `96` §19 objected to into a
    different column: a person reading the audit log would be told the product never
    looked, when what happened is that it looked and found no safety word.
    """
    assert "no_safety_evidence" in DENIAL_ORDER
    assert check_denial_reason("no_safety_evidence") == "no_safety_evidence"
    assert DENIAL_ORDER.index("no_safety_evidence") == \
        DENIAL_ORDER.index("unclassified") + 1


def test_the_new_reason_is_decidable_from_the_request():
    """It needs a row lookup and no text, so it must precede every content denial.

    `DECIDABLE_FROM_REQUEST` is not a label: `test_p7_release` asserts that every
    member of it precedes every non-member, so a reason left out of this set would
    be allowed to be decided after an excerpt had already been materialised.
    """
    assert "no_safety_evidence" in DECIDABLE_FROM_REQUEST
    late = {r for r in DENIAL_ORDER if r not in DECIDABLE_FROM_REQUEST}
    assert max(DENIAL_ORDER.index(r) for r in DECIDABLE_FROM_REQUEST) < \
        min(DENIAL_ORDER.index(r) for r in late)


def test_the_predicate_refuses_a_cloud_target_and_permits_a_local_one():
    """The rule, stated once, with no knob.

    CLOUD is refused because the product has not established the thing that call
    would depend on. LOCAL is permitted because §8.4's whole distinction is that a
    local model call moves nothing off the device -- `hybrid` is "Sensitive files
    remain LOCAL", not "sensitive files are never read". Denying local calls as
    well would withhold from the on-device model exactly the files it exists to
    look at, and would be a second, larger `unclassified_permits_local` invented
    here rather than asked of the owner.
    """
    assert no_safety_evidence_denies(locality="cloud") is True
    assert no_safety_evidence_denies(locality="local") is False


# --------------------------------------------------------------------------
# the gate: the property `96` §20 asks for
# --------------------------------------------------------------------------

def test_a_class_reached_without_safety_evidence_does_not_clear_a_cloud_call(
        gate_conn):
    """THE HOLE, closed. This is the HKID's own shape.

    `personal_non_sensitive, protected=0` -- a positive statement that the file is
    not sensitive -- reached without a single safety term having matched. The gate
    refuses to treat it as a cleared file.
    """
    file_id, digest, key = _ordinary_file(gate_conn)
    _policy(gate_conn, "hybrid")
    _classify(gate_conn, file_id, digest, basis=DETECTOR_NO_SAFETY_EVIDENCE)

    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="body"),),
        file_ids=(file_id,)))

    assert isinstance(decision, Denied), decision
    assert decision.reason == "no_safety_evidence"


def test_the_same_file_on_the_strong_basis_is_released(gate_conn):
    """THE CONTROL, and the reason this is a gate change rather than a class change.

    Identical file, identical class, identical protected flag. The ONLY difference
    is the basis. If this test and the one above ever agree, the new member is
    either doing nothing or refusing everything.
    """
    file_id, digest, key = _ordinary_file(gate_conn, "syllabus.pdf", "hash-syllabus")
    _policy(gate_conn, "hybrid")
    _classify(gate_conn, file_id, digest, basis=DETECTOR)

    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="body"),),
        file_ids=(file_id,)))

    assert isinstance(decision, Released), decision


def test_a_local_model_may_still_look_at_it(gate_conn):
    """What must NOT be broken: the on-device model.

    §8.4 `local_model`: "Local extraction plus a user-installed local LLM for
    eligible dossiers." A file nobody has established anything about is exactly the
    case §2.7 and §7.8 want a local model for. Refusing it here would trade a cloud
    hole for a local blackout and would show up as a coverage regression wearing a
    safety fix's name.
    """
    file_id, digest, key = _ordinary_file(gate_conn, "notes.pdf", "hash-notes")
    _policy(gate_conn, "local_model")
    _classify(gate_conn, file_id, digest, basis=DETECTOR_NO_SAFETY_EVIDENCE)

    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="body"),),
        model_target=LOCAL, file_ids=(file_id,)))

    assert isinstance(decision, Released), decision


def test_the_denial_says_what_was_and_was_not_established(gate_conn):
    """SPEC §6: the explanation is user-facing. §8.6: it shows what was deferred and why.

    The sentence has to survive being read by the owner, so it says the true thing:
    a class exists, no safety evidence was found, and finding none is not the same
    as establishing that there is none.
    """
    file_id, digest, key = _ordinary_file(gate_conn, "scan.pdf", "hash-scan")
    _policy(gate_conn, "hybrid")
    _classify(gate_conn, file_id, digest, basis=DETECTOR_NO_SAFETY_EVIDENCE)

    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="body"),),
        file_ids=(file_id,)))

    assert "personal_non_sensitive" in decision.explanation
    assert "safety" in decision.explanation
    assert decision.remedy_options, "a denial with no remedy is a dead end (§8.6)"


def test_mode_and_policy_denials_still_outrank_it(gate_conn):
    """`DENIAL_ORDER` is Task 13's, and the gate delegates rather than re-sorting.

    Under `offline` a cloud target is refused before anything about the file is
    read; a new reason inserted mid-list must not have changed that.
    """
    file_id, digest, key = _ordinary_file(gate_conn, "essay.pdf", "hash-essay")
    _policy(gate_conn, "offline")
    _classify(gate_conn, file_id, digest, basis=DETECTOR_NO_SAFETY_EVIDENCE)

    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="body"),),
        file_ids=(file_id,)))

    assert decision.reason == "mode_forbids_target"


def test_an_unclassified_file_still_answers_unclassified(gate_conn):
    """The ordinary path, unchanged. `unclassified` precedes the new reason.

    A file with no record at all has a different problem from one whose record is
    weak, and the audit log must keep telling them apart.
    """
    file_id, digest, key = _ordinary_file(gate_conn, "unknown.pdf", "hash-unknown")
    _policy(gate_conn, "hybrid")

    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="body"),),
        file_ids=(file_id,)))

    assert decision.reason == "unclassified"
