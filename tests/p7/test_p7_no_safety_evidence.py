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
The 41 stay `personal_non_sensitive, protected=0` and stay locally placeable.

---

**AMENDED 2026-09-07, on the owner's ruling of 2026-09-05 (`104` §13.2), and the
amendment is a NARROWING rather than a reversal.**

`96` §20's rule shipped inside `fd68cb6` with its own escape hatch written into the
docstring -- *"LOCAL IS PERMITTED"* -- and no local model existed. So a rule meant to
REDIRECT ordinary files to an on-device model was, in the product as built, a total
cloud block: 44 of the owner's 199 files could reach the only wired model site and
155 could not (`103` C1, `104` R-01). The commit's own measurement table is headed
"no model", so the cloud effect was never measured by the commit that caused it. Read
against the constitution's second rule -- a gate that excludes readable files from
the engine is a defect -- that is a coverage regression wearing a safety fix's name.

What `96` §19 actually objected to survives, and this file's tests are now written
around it. A silence became a confident negative because the file had a CLASS and
nothing else. So the refusal now needs BOTH halves: the weak basis, AND a request
that carries no releasable reading of the file itself. A file with an excerpt of its
own words is not a silence and may reach a cloud model; a file with nothing but a
label and a field name is, and may not.

The cloud lift was gated on SF-1 (`104` R-07) being closed first, and it was: the
instrument measured 20 of the owner's Word documents releasing their entire text
before that fix, and 0 after. Widening the door before closing that one would have
sent whole documents to a provider.

Protected material is untouched by all of this. `protected_cloud_denies` is a
separate rung with no carve-out outside `cloud_assisted` plus an explicit grant, and
two tests below assert the lift cannot reach it.
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
from privacy.items import CandidateLabel, Excerpt, MetadataField
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
    and a decision, which is exactly what SPEC §2's three were -- and on 2026-09-08
    it was exactly that: this test went red, the owner's ruling (`104` §17.1) is
    what turned it green again, and `local_model_situation` is recorded at the
    member in `privacy/vocabulary.py`. The equality still holds the line: a SIXTH
    member is a red test and a decision.
    """
    assert CLASSIFICATION_BASES == (
        "detector", "detector_no_safety_evidence", "safety_domain", "user",
        "local_model_situation")
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


def test_the_predicate_needs_both_halves_and_local_needs_neither():
    """The rule, stated once, with no knob. NARROWED on the owner's `104` §13.2
    ruling: the weak basis alone no longer refuses a cloud call.

    CLOUD with releasable evidence is PERMITTED. That is the lift, and it is what
    `96` §20's own escape hatch assumed would exist -- its docstring says "LOCAL IS
    PERMITTED", and no local model did exist, so a rule meant to redirect ordinary
    files to an on-device model became a total cloud block over 155 of the owner's
    199 files.

    CLOUD with nothing releasable is still REFUSED, and for the reason `96` §19
    measured: a file whose whole contribution is that it acquired a class is a
    silence, and sending it turns that silence into a confident negative.

    LOCAL is permitted either way, because §8.4's whole distinction is about what
    leaves the device -- `hybrid` is "Sensitive files remain LOCAL", not "sensitive
    files are never read".
    """
    assert no_safety_evidence_denies(
        locality="cloud", releasable_evidence=True) is False
    assert no_safety_evidence_denies(
        locality="cloud", releasable_evidence=False) is True
    assert no_safety_evidence_denies(
        locality="local", releasable_evidence=False) is False
    assert no_safety_evidence_denies(
        locality="local", releasable_evidence=True) is False


# --------------------------------------------------------------------------
# the gate: the property `96` §20 asks for
# --------------------------------------------------------------------------

def test_an_ordinary_file_with_a_releasable_reading_may_reach_a_cloud_model(
        gate_conn):
    """THE LIFT (`104` §13.2, owner, 2026-09-05), and it is the case that matters.

    `personal_non_sensitive, protected=0` on the weak basis -- the shape 41 of the
    owner's classified files and 155 of his 199 total were refused under -- with one
    bounded excerpt of the file's own words in the request. This is an ordinary piece
    of coursework, and the constitution's second rule is that a gate excluding
    readable files from the engine is a defect.

    Its twin below is the file with nothing releasable, which is still refused.
    """
    file_id, digest, key = _ordinary_file(gate_conn)
    _policy(gate_conn, "hybrid")
    _classify(gate_conn, file_id, digest, basis=DETECTOR_NO_SAFETY_EVIDENCE)

    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="body"),),
        file_ids=(file_id,)))

    assert isinstance(decision, Released), decision
    # The reading the model is shown is this file's own, at the span asked for. Its
    # VALUE reads `[redacted]` and not `Homework 3`, because `_gate`'s injected
    # classifier answers for every span -- which is this file's fixture and not the
    # deployment's -- and that is the redaction path working, not the lift failing.
    assert [item.observation_key for item in decision.materialised_items] == [key]


def test_the_same_file_with_nothing_of_itself_in_the_request_is_still_refused(
        gate_conn):
    """THE NEGATIVE TWIN, and it is what keeps `96` §19's finding alive.

    Identical file, identical class, identical basis. The only difference is that
    the request carries no reading OF THE FILE: a `CandidateLabel` is a destination
    name and a `MetadataField` is a field NAME, and §4 says an evidence reference is
    "an id only -- no content". A call built from those asks a model to confirm that
    a file is not sensitive while showing it nothing of the file, which is exactly
    the silence-into-confident-negative `96` §19 counted 41 times.

    If this test and the one above ever agree, the condition is doing nothing.
    """
    file_id, digest, _key = _ordinary_file(gate_conn, "empty.pdf", "hash-empty")
    _policy(gate_conn, "hybrid")
    _classify(gate_conn, file_id, digest, basis=DETECTOR_NO_SAFETY_EVIDENCE)

    decision = _gate(gate_conn).release(_request(
        items=(CandidateLabel(label="Coursework"),
               MetadataField(name="page_count")),
        file_ids=(file_id,)))

    assert isinstance(decision, Denied), decision
    assert decision.reason == "no_safety_evidence"


def test_an_evidence_key_that_does_not_resolve_is_not_evidence(gate_conn):
    """The safe direction on an unresolvable key.

    A request naming a key the evidence does not carry has not shown the model
    anything, and `materialise` would raise on it later anyway. Counting it as
    evidence would let a caller lift its own denial by naming keys that do not
    exist -- which is the one way this condition could be turned into a bypass.
    """
    file_id, digest, _key = _ordinary_file(gate_conn, "ghost.pdf", "hash-ghost")
    _policy(gate_conn, "hybrid")
    _classify(gate_conn, file_id, digest, basis=DETECTOR_NO_SAFETY_EVIDENCE)

    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key="no-such-observation-key", span=SPAN,
                       reason="body"),),
        file_ids=(file_id,)))

    assert isinstance(decision, Denied), decision
    assert decision.reason == "no_safety_evidence"


def test_a_protected_file_on_this_basis_still_never_reaches_the_cloud(gate_conn):
    """WHAT THE LIFT MUST NOT REACH, asserted rather than reasoned about.

    §8.4: protected material is "not included in cloud-model prompts by default",
    and the standing rule is stricter -- marked and counted, never opened.
    `protected_cloud_denies` is a separate rung of the same ladder with no carve-out
    outside `cloud_assisted` plus an explicit grant, and widening
    `no_safety_evidence_denies` must not have reached it. The file below carries the
    weak basis AND a perfectly good releasable excerpt, so it satisfies the lifted
    condition completely, and it is refused anyway.
    """
    file_id, digest, key = _ordinary_file(gate_conn, "hkid.pdf", "hash-hkid")
    _policy(gate_conn, "hybrid")
    _classify(gate_conn, file_id, digest, basis=DETECTOR_NO_SAFETY_EVIDENCE,
              handling_class="sensitive_personal", protected=True)

    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="body"),),
        file_ids=(file_id,)))

    assert isinstance(decision, Denied), decision
    assert decision.reason == "protected_cloud_target"


def test_a_protected_file_reaches_no_cloud_model_under_any_of_the_four_modes(
        gate_conn):
    """The same rule, over §8.4's whole mode vocabulary rather than over one mode.

    `cloud_assisted` is the one mode with a carve-out and it needs an explicit grant
    for the file's own area; this policy holds none, so all four refuse. The reason
    differs -- `offline` and `local_model` forbid a cloud target outright, before
    anything about the file is read -- and every one of them is a refusal.
    """
    for index, mode in enumerate(
            ("offline", "local_model", "hybrid", "cloud_assisted")):
        file_id, digest, key = _ordinary_file(
            gate_conn, f"protected{index}.pdf", f"hash-protected-{index}")
        _policy(gate_conn, mode)
        _classify(gate_conn, file_id, digest, basis=DETECTOR_NO_SAFETY_EVIDENCE,
                  handling_class="sensitive_personal", protected=True)

        decision = _gate(gate_conn).release(_request(
            items=(Excerpt(observation_key=key, span=SPAN, reason="body"),),
            file_ids=(file_id,)))

        assert isinstance(decision, Denied), (mode, decision)
        assert decision.reason in ("mode_forbids_target",
                                   "protected_cloud_target"), (mode, decision)


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
    a class exists, no safety evidence was found, finding none is not the same as
    establishing that there is none -- and, since `104` §13.2 narrowed the rule, that
    the basis alone is no longer what stopped this call. A sentence that still blamed
    the basis alone would name the half that is now insufficient on its own and leave
    out the half that decided.
    """
    file_id, digest, _key = _ordinary_file(gate_conn, "scan.pdf", "hash-scan")
    _policy(gate_conn, "hybrid")
    _classify(gate_conn, file_id, digest, basis=DETECTOR_NO_SAFETY_EVIDENCE)

    decision = _gate(gate_conn).release(_request(
        items=(CandidateLabel(label="Coursework"),), file_ids=(file_id,)))

    assert "personal_non_sensitive" in decision.explanation
    assert "safety" in decision.explanation
    assert "no releasable reading" in decision.explanation
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
