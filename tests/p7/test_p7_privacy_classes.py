# tests/p7/test_p7_privacy_classes.py
"""`105` §14.3: two named lists, a precedence between them, and a fourth class.

R-89 is the defect. On the owner's own corpus a receipt, an order confirmation, a
boarding pass and a screenshot were all being called "protected material (§8.4)" on a
corpus whose `00`:120 names Receipts and Confirmations as their DESTINATION. Two
different rules were being read as one list, so a file that should have been filed by
a rule was held back as though it were a passport, and the person got neither the
filing nor the protection.

R-130 is what the owner ruled about it on 7 September 2026:

    "Keep both lists, apply the most restrictive matching rule to the content and its
     derivatives regardless of file format, and classify unresolved cases as pending
     rather than ordinary."

Five clauses, each with its own tests below:

  1. two lists -- always-local kinds shown to no CLOUD model and filed by rules and
     local models; protected kinds shown to NO model and filed one at a time;
  2. precedence, explicit and applied to the CONTENT whatever the file format:
     protected, then always-local, then ordinary;
  3. a file the detector did not assess is `pending`, distinct from an assessed
     ordinary file, and treated like unclassified for every gate;
  4. OCR text, excerpts and summaries carry the source's restriction;
  5. classification precedes the model call it governs.

**WHAT IS PROVED HERE AND WHAT IS OWED.** Clauses 1, 2, 3 and 4 are proved end to
end. Clause 1's always-local consequence and half of clause 4 are proved as the
resolution they are and NOT at the gate, because SPEC §2's classification record has
eight fields and none of them carries a document kind: the gate has no way to learn
that a file is a receipt. That gap is named at `classification.privacy_class_of` and
in `test_the_gate_cannot_yet_read_a_kind_and_this_file_says_so_rather_than_implying_it`
below, which is a test whose whole content is the admission -- so a later reader finds
the hole by running the suite rather than by trusting a docstring.
"""
from __future__ import annotations

import hashlib
import tempfile
from dataclasses import replace
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import record_file
from evidence_shape.canonical import canonical_json
from evidence_shape.location import Location, Segment
from evidence_shape.locator import serialize_locator
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import new_id, record_observation, record_run
from extractors.schema import create_extraction_schema

from privacy.classification import (
    CLASSIFICATION_FIELDS, ClassificationRecord, UNREADABLE_UNCLASSIFIED,
    derivative_privacy_class, privacy_class_for, privacy_class_of, resolve_class,
)
from privacy.classification_store import ClassificationStore
from privacy.defaults import MORE_REDACTING
from privacy.denial import deny_unclassified
from privacy.gate import Gate
from privacy.items import Excerpt
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from privacy.release import Denied, ModelCallRequest, ModelTarget, Released, Target
from privacy.schema import create_privacy_schema
from privacy.vocabulary import (
    ALWAYS_LOCAL_KINDS, ALWAYS_LOCAL_ZONES, OutOfVocabulary,
    PRIVACY_CLASS_ALWAYS_LOCAL, PRIVACY_CLASS_ORDINARY, PRIVACY_CLASS_PENDING,
    PRIVACY_CLASS_PROTECTED, PRIVACY_CLASSES, PROTECTED_KINDS,
    RESTRICTED_KIND_LABELS, RESTRICTED_KINDS, check_restricted_kind,
)

OBSERVED_AT = "2026-09-07T09:00:00Z"
PLAN_VERSION = "plan-privacy-classes"
COMPONENT = "0.1.0"
CLOUD = ModelTarget(locality="cloud", model_id="a-model", provider="Acme")
LOCAL = ModelTarget(locality="local", model_id="a-local-model", provider="on-device")
#: P7's own ceiling echo. A number only a test may choose.
MAX_DOSSIER_TOKENS = 4000
#: A bounded metadata value, the shape the always-local zone file uses for its
#: controls: releasable, so a refusal below is about the FILE and never about the item.
A_TITLE = "Spring Term Syllabus"

#: A P4 observation key, so a `ClassificationRecord` on a detector basis is
#: evidence-backed. Minted from a real locator rather than written as a literal:
#: `ClassificationRecord.__post_init__` asks `evidence_shape.observation` whether a
#: reference is a key, and M14 is explicit that the KEY is what makes it durable.
_A_KEY = observation_key(
    content_hash="a" * 64, extractor_name="filesystem",
    locator=serialize_locator(Location(
        zone="metadata", container_path=(Segment(kind="field", label="title"),),
        text_span=None)),
    raw_value=A_TITLE,
)


# ================================================================================
# Clause 1: two lists, two names, ten members
# ================================================================================

@pytest.mark.parametrize("kind", ALWAYS_LOCAL_KINDS)
def test_every_always_local_kind_classifies_always_local(kind: str):
    """§13.3's first list: "receipts, order confirmations, boarding passes and
    tickets, screenshots that show a person's own account or messages, bank or card
    notifications", shown to no cloud model and filed by rules and local models.

    Every member is asserted, not a sample. A list whose fourth member silently
    resolved to `ordinary` is exactly R-89 in the other direction.
    """
    assert privacy_class_for([kind]) == PRIVACY_CLASS_ALWAYS_LOCAL


@pytest.mark.parametrize("kind", PROTECTED_KINDS)
def test_every_protected_kind_classifies_protected(kind: str):
    """§13.3's second list: "identity documents (passport, licence, national id),
    medical records, financial statements and tax returns, credentials and password
    vaults, legal documents naming the person", shown to no model at all.
    """
    assert privacy_class_for([kind]) == PRIVACY_CLASS_PROTECTED


def test_the_two_lists_are_five_and_five_and_share_no_member():
    """The lists are the owner's and a kind belongs to one of them.

    The precedence below is a rule about a FILE matching two kinds. It is not a rule
    about a kind belonging to two lists, and if one ever did, the precedence would be
    deciding a question the lists had already answered inconsistently.
    """
    assert len(ALWAYS_LOCAL_KINDS) == 5
    assert len(PROTECTED_KINDS) == 5
    assert not set(ALWAYS_LOCAL_KINDS) & set(PROTECTED_KINDS)
    assert len(set(RESTRICTED_KINDS)) == 10


def test_each_of_the_ten_carries_the_owners_own_words():
    """The prose is pinned beside the identifier, as `HANDLING_CLASS_LABELS` pins
    §8.4's five lines. A paraphrase is a failing test, and the reason is R-89's own:
    "screenshots that show a person's own account or messages" is a narrower promise
    than "screenshots", and the narrower one is what was ruled.
    """
    assert set(RESTRICTED_KIND_LABELS) == set(RESTRICTED_KINDS)
    assert RESTRICTED_KIND_LABELS["own_account_or_message_screenshot"] == (
        "screenshots that show a person's own account or messages")
    assert RESTRICTED_KIND_LABELS["identity_document"] == (
        "identity documents (passport, licence, national id)")


def test_a_kind_on_neither_list_is_ordinary_and_is_not_an_error():
    """§13.3: "A kind on neither list is ordinary."

    The universe of document kinds is open -- a syllabus, an essay, a photograph --
    and P7 publishes no list of it. Only the two RESTRICTED lists are closed, so an
    unrecognised name here is an ordinary document rather than a mistake.
    """
    assert privacy_class_for(["syllabus"]) == PRIVACY_CLASS_ORDINARY
    assert privacy_class_for(["syllabus", "essay"]) == PRIVACY_CLASS_ORDINARY


def test_the_guard_against_a_misspelling_is_at_the_writer_and_not_here():
    """Because an unknown kind is ordinary, `"reciept"` would be a silent downgrade
    if nothing else caught it -- the failure §8.6 names by name.

    What catches it is the WRITER's side: a detector names a restricted kind through
    `check_restricted_kind` or through one of the ten constants beside the lists, so
    the typo is refused there rather than resolving quietly three modules away. The
    refusal names the closed set and never a neighbour, on `_check`'s own argument
    that a suggestion in this vocabulary IS the silent downgrade.
    """
    assert check_restricted_kind("receipt") == "receipt"
    with pytest.raises(OutOfVocabulary) as raised:
        check_restricted_kind("reciept")
    assert "receipt" not in str(raised.value), (
        "the refusal put the nearest member in front of the author of the mistake")
    assert "10" in str(raised.value)


# ================================================================================
# Clause 2: precedence, applied to the content and not to the format
# ================================================================================

def test_a_screenshot_of_a_bank_statement_is_protected(): 
    """The owner's own first example, verbatim from §14.3: "A screenshot of a bank
    statement is protected although account screenshots are always-local."

    The FORMAT says screenshot and the CONTENT says financial statement, and the
    ruling is that the content decides. This is the case R-89's single list could not
    express at all: one list has no way to say that a member of it is sometimes
    something stronger.
    """
    assert privacy_class_for([
        "own_account_or_message_screenshot",
        "financial_statement_or_tax_return",
    ]) == PRIVACY_CLASS_PROTECTED


def test_a_receipt_containing_credentials_is_protected():
    """The owner's second example: "a receipt containing credentials is protected."

    Order-independent, because a precedence that depended on which kind the detector
    happened to list first would be a rule about the detector rather than about the
    file.
    """
    assert privacy_class_for([
        "receipt", "credentials_or_password_vault",
    ]) == PRIVACY_CLASS_PROTECTED
    assert privacy_class_for([
        "credentials_or_password_vault", "receipt",
    ]) == PRIVACY_CLASS_PROTECTED


def test_the_precedence_is_the_published_tuples_order():
    """§14.3: "Precedence, explicit: protected, then always-local, then ordinary."

    Asserted as a SEQUENCE and not as a membership, because `privacy_class_for` walks
    this tuple and returns the first class that matches: a reorder changes what the
    product does, and a test that only checked the members would stay green through
    one.
    """
    assert PRIVACY_CLASSES[:3] == (
        PRIVACY_CLASS_PROTECTED, PRIVACY_CLASS_ALWAYS_LOCAL, PRIVACY_CLASS_ORDINARY)
    assert PRIVACY_CLASSES[3] == PRIVACY_CLASS_PENDING, (
        "`pending` is outside the precedence, the way `rejected` is outside §3.13's "
        "ranking: it says nothing was looked at rather than what was found")


# ================================================================================
# Clause 3: pending is not ordinary
# ================================================================================

def test_an_unassessed_file_is_pending_and_an_assessed_one_is_ordinary():
    """§14.3: "'On neither list' distinguishes an assessed ordinary document from one
    the detector failed to recognise, which is pending."

    The empty sequence against `None` is the whole of the distinction, and it is why
    the argument is an optional sequence rather than a set. Collapsing them would
    turn every file nothing had looked at into a confident "ordinary" -- `96` §19's
    finding one column along, and the failure §8.6 forbids by name.
    """
    assert privacy_class_for(None) == PRIVACY_CLASS_PENDING
    assert privacy_class_for(()) == PRIVACY_CLASS_ORDINARY
    assert privacy_class_for([]) == PRIVACY_CLASS_ORDINARY


def test_a_bare_string_is_refused_rather_than_read_as_one_character_kinds():
    """`privacy_class_for("receipt")` would iterate seven characters, match nothing,
    and answer `ordinary` -- a downgrade produced by a caller's plausible mistake.

    The same shape `ClassificationRecord` already refuses for `evidence_refs`, and
    for the same reason: a string is a sequence and the type system will not say so.
    """
    with pytest.raises(TypeError) as raised:
        privacy_class_for("receipt")
    assert "ordinary" in str(raised.value)


def test_pending_and_ordinary_are_distinguished_on_the_record(p7_conn):
    """On the RECORD: the absence of a classification is `pending`, and a stored
    classification of an unprotected file is `ordinary`.

    The two answers agree with `resolve_class` by construction -- a file that is
    pending here is exactly a file that resolves to `unreadable_unclassified` there
    -- which is what lets §14.3's "treated like unclassified for every gate" hold
    with no second rule anywhere.
    """
    assert privacy_class_of(None) == PRIVACY_CLASS_PENDING
    assert resolve_class(None) == UNREADABLE_UNCLASSIFIED

    record = ClassificationRecord(
        file_id="f1", content_hash="h1", handling_class="personal_non_sensitive",
        protected=False, basis="detector", evidence_refs=(_A_KEY,),
        reliability_state="direct", observed_at=OBSERVED_AT)
    assert privacy_class_of(record) == PRIVACY_CLASS_ORDINARY
    assert resolve_class(record) != UNREADABLE_UNCLASSIFIED


def test_the_class_is_read_off_the_flag_and_never_off_the_handling_class():
    """SPEC §2: "Neighbouring parts should consume the `protected` flag, not infer it
    from the class", and Open question 1 -- whether `protected` is exactly the top two
    handling classes -- is unsettled and is NOT settled by §14.3.

    Two records with the same handling class and different flags must land in
    different privacy classes, which is only true if the flag is what is read.
    """
    fields = dict(
        file_id="f1", content_hash="h1",
        handling_class="highly_sensitive_credential_bearing", basis="detector",
        evidence_refs=(_A_KEY,), reliability_state="direct",
        observed_at=OBSERVED_AT)
    assert privacy_class_of(ClassificationRecord(protected=True, **fields)) == (
        PRIVACY_CLASS_PROTECTED)
    assert privacy_class_of(ClassificationRecord(protected=False, **fields)) == (
        PRIVACY_CLASS_ORDINARY)


def test_the_screen_sentence_says_pending_rather_than_ordinary():
    """On the SCREEN: the sentence a person reads must say which of the two happened.

    "Nothing has assessed these bytes" and "this was assessed and is on neither list"
    want different things done about them -- the first is answered by running the
    detector and the second is answered by nothing -- and the denial used to say
    neither.
    """
    denied = deny_unclassified(file_ids=("f1",), locality="cloud", completeness=None)
    assert denied.reason == "unclassified", (
        "§14.3 treats pending like unclassified for every gate, so a tenth denial "
        "reason would be a second name for one refusal")
    assert PRIVACY_CLASS_PENDING in denied.explanation
    assert PRIVACY_CLASS_ORDINARY in denied.explanation, (
        "the sentence must name the other reading to hold the two apart")
    assert denied.remedy_options, "§8.6: a denial is never a dead end"


# ================================================================================
# Clause 4: a derivative carries its source's restriction
# ================================================================================

@pytest.mark.parametrize("source", PRIVACY_CLASSES)
def test_a_derivative_carries_its_sources_restriction(source: str):
    """§14.3: "OCR text, excerpts and summaries retain the source's restriction."

    Every class, including `pending`: a summary of a file nothing has assessed is
    itself unassessed, and the one direction this must never travel is toward
    ordinary.
    """
    assert derivative_privacy_class(source) == source


def test_an_excerpt_of_a_protected_file_has_no_releasable_form():
    """"A released excerpt of a protected file is impossible" -- the ruling's own
    words. The excerpt inherits `protected`, and `protected` is shown to no model, so
    there is no target for which the derivative resolves to something releasable.
    """
    assert derivative_privacy_class(PRIVACY_CLASS_PROTECTED) == (
        PRIVACY_CLASS_PROTECTED)
    assert PRIVACY_CLASSES.index(PRIVACY_CLASS_PROTECTED) == 0, (
        "protected is the most restrictive class, so nothing it is inherited by can "
        "be less restricted than it")


def test_an_excerpt_of_an_always_local_file_is_local_only():
    """"...of an always-local file, local only." The derivative is not demoted to
    ordinary by being an excerpt, which is the move that would put a receipt's text
    in a cloud prompt while the receipt itself stayed home.
    """
    assert derivative_privacy_class(PRIVACY_CLASS_ALWAYS_LOCAL) == (
        PRIVACY_CLASS_ALWAYS_LOCAL)


def test_a_derivative_cannot_be_given_a_class_outside_the_four():
    """The inheritance is validated rather than passed through. A caller handing this
    an invented class would otherwise be minting a restriction level.
    """
    with pytest.raises(OutOfVocabulary):
        derivative_privacy_class("public_low")


def test_the_format_never_weakens_the_restriction_and_ocr_is_the_proof():
    """"regardless of file format" is in the ruling's own sentence.

    OCR is where it bites and where this product already paid for it: a scanned HKID
    and a vaccination record were both OCR'd on the owner's disk, and a card number
    recognised in either was an `Excerpt` the gate would have released, because the
    `ocr` zone had no check. `ocr` is in `ALWAYS_LOCAL_ZONES` for that reason, so the
    structural half of clause 4 is already enforced for the one derivative that
    reaches the gate as its own zone.
    """
    assert "ocr" in ALWAYS_LOCAL_ZONES
    assert derivative_privacy_class(PRIVACY_CLASS_PROTECTED) == (
        PRIVACY_CLASS_PROTECTED)


def test_the_gate_cannot_yet_read_a_kind_and_this_file_says_so_rather_than_implying_it():
    """WHAT IS OWED, asserted so it is found by running the suite.

    SPEC §2's classification record has eight fields and none of them carries a
    document KIND, so a file whose recognised kind is `receipt` is indistinguishable
    at the gate from an ordinary one. `privacy_class_for` decides that case correctly
    from the kinds; `privacy_class_of` cannot reach them and answers `ordinary`.

    So clause 1's always-local consequence is enforced by the caller that holds the
    kinds and by NOTHING at the gate. The seam is one field on this record and one
    column in `privacy.schema`. This test passes today and must be deleted -- not
    edited -- on the day the class is recorded, because on that day its claim is
    false.
    """
    assert "privacy_class" not in CLASSIFICATION_FIELDS
    a_receipt = ClassificationRecord(
        file_id="f1", content_hash="h1", handling_class="personal_non_sensitive",
        protected=False, basis="detector", evidence_refs=(_A_KEY,),
        reliability_state="direct", observed_at=OBSERVED_AT)
    assert privacy_class_of(a_receipt) == PRIVACY_CLASS_ORDINARY
    assert privacy_class_for(["receipt"]) == PRIVACY_CLASS_ALWAYS_LOCAL


# ================================================================================
# Clause 5: classification precedes the model call it governs
# ================================================================================

@pytest.fixture()
def gate_conn(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    create_privacy_schema(conn)
    return conn


def _file(conn, name: str, content_hash: str) -> str:
    corpus = Path(tempfile.mkdtemp()) / "corpus"
    corpus.mkdir()
    path = corpus / name
    path.write_bytes(b"%PDF-1.4 fixture bytes")
    return record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=4096,
        observed_timestamps=canonical_json({"modified": OBSERVED_AT}),
        parent_folder_context="corpus", mime_type="application/pdf",
        detected_format="pdf", scan_state="scanned", materialized=True,
        content_hash=content_hash,
    )


def _observation(conn, file_id: str, content_hash: str, *, raw_value: str) -> str:
    """One bounded `metadata`-zone value: releasable, so a refusal is about the FILE.

    The same span-less shape `tests/p7/test_p7_always_local_zone.py` uses for its
    controls, and for that file's reason -- §2.8's EXIF-style field is a bounded
    value rather than a document, so `is_whole_document` does not fire on it and no
    zone rule refuses it. Every denial below is therefore the file's own.
    """
    digest = hashlib.sha256(f"{content_hash}:metadata".encode()).hexdigest()
    run_id = new_id()
    location = Location(zone="metadata",
                        container_path=(Segment(kind="field", label="title"),),
                        text_span=None)
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=digest,
        extractor_name="filesystem", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=OBSERVED_AT, observation_count=1,
    ))
    record_observation(conn, Observation(
        file_id=file_id, content_hash=digest, extractor_name="filesystem",
        extractor_version="1.0.0", source_type="text_document",
        raw_value=raw_value, location=location, occurrence_count=1,
        observed_at=OBSERVED_AT, reliability="direct", run_id=run_id,
        context_before=None, context_after=None, context_truncated=False,
    ))
    return observation_key(
        content_hash=digest, extractor_name="filesystem",
        locator=serialize_locator(location), raw_value=raw_value,
    )


def _store_policy(conn, *, grants: tuple) -> Policy:
    draft = Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode="cloud_assisted",
        consent_grants=grants, redaction_settings=dict(MORE_REDACTING),
        automatic_move_permissions={}, plan_version=PLAN_VERSION,
        set_at=OBSERVED_AT,
    )
    version = set_policy(conn, draft, component_version=COMPONENT,
                         user_id="joseph", reason="privacy classes test")
    return replace(draft, policy_version=version)


def _gate(conn, *, permits_local: bool) -> Gate:
    return Gate(
        conn,
        store=ClassificationStore(conn),
        plan_version=PLAN_VERSION,
        classifier=lambda value, *, context_before=None, context_after=None: None,
        transform=lambda value, *, identifier_class: "[redacted]",
        unclassified_permits_local=permits_local,
        scope_for=lambda file_id: "area-1",
        files_in_scope=lambda scope: (),
        component_version=COMPONENT,
        now=lambda: OBSERVED_AT,
        user_id="joseph",
    )


def _request(*, key: str, file_id: str, target: ModelTarget) -> ModelCallRequest:
    return ModelCallRequest(
        stage="fact_resolution", target=Target(file_ids=(file_id,)),
        model_target=target,
        requested_items=(Excerpt(observation_key=key, span=None, reason="title"),),
        prompt_template_id="template.under-ratification",
        prompt_fingerprint="fingerprint-privacy-classes",
        max_dossier_tokens=MAX_DOSSIER_TOKENS,
    )


def _pending_file(conn, *, grants: tuple = ()) -> tuple[str, str]:
    """A file with an observation and NO classification record: nothing assessed it."""
    content_hash = "hash-pending"
    file_id = _file(conn, "pending-fixture.pdf", content_hash)
    key = _observation(conn, file_id, content_hash, raw_value=A_TITLE)
    _store_policy(conn, grants=grants)
    return file_id, key


def test_the_gate_refuses_a_pending_file_for_a_cloud_target(gate_conn):
    """§14.3's clause 5 at the door: a file nothing has assessed does not reach a
    cloud model, whatever the caller's answer to Open question 5.

    `unclassified_permits_local=True` here on purpose -- the permissive setting -- so
    what refuses is the CLOUD target and not the strict configuration.
    """
    file_id, key = _pending_file(gate_conn)
    decision = _gate(gate_conn, permits_local=True).release(
        _request(key=key, file_id=file_id, target=CLOUD))

    assert isinstance(decision, Denied), (
        f"a pending file was {type(decision).__name__} for a cloud model")
    assert decision.reason == "unclassified"
    assert PRIVACY_CLASS_PENDING in decision.explanation


def test_the_gate_admits_a_pending_file_for_a_local_target_under_the_rule(gate_conn):
    """The other half, and it is the half that makes the refusal above a rule rather
    than a blanket.

    Open question 5 -- "Does `unreadable_unclassified` permit a LOCAL model call?" --
    is unanswered, so the caller answers it and P7 names no winner. §14.3's clause 5
    is written to that: a pending file reaches a dossier only where the
    local-unclassified rule admits it, and here it does.
    """
    file_id, key = _pending_file(gate_conn)
    decision = _gate(gate_conn, permits_local=True).release(
        _request(key=key, file_id=file_id, target=LOCAL))

    assert isinstance(decision, Released), (
        f"a pending file was {type(decision).__name__} for a local model although "
        f"the caller permits local calls on unclassified files")
    assert decision.materialised_items, "released nothing while calling it a release"


def test_a_pending_file_is_refused_locally_when_the_rule_does_not_admit_it(gate_conn):
    """The same file and the same target, with the strict answer to Open question 5.

    Run because "admits it for local only under the unclassified rule" is a claim
    about the RULE, and a test that only ever passed `True` would be green with the
    parameter ignored.
    """
    file_id, key = _pending_file(gate_conn)
    decision = _gate(gate_conn, permits_local=False).release(
        _request(key=key, file_id=file_id, target=LOCAL))

    assert isinstance(decision, Denied)
    assert decision.reason == "unclassified"


def test_a_protected_files_excerpt_is_not_released_to_a_cloud_model(gate_conn):
    """"A released excerpt of a protected file is impossible", at the door.

    The excerpt is a bounded `metadata` value that this same fixture releases when
    its file is ordinary -- `test_the_gate_admits_a_pending_file...` above releases
    the identical item -- so what refuses it here is the file's protected flag and
    nothing about the item.

    NARROWER THAN THE RULING, and the remaining half is named rather than assumed.
    §8.4 offers "allow a local model" as one of its four consent options, so a
    protected file with a granted scope and a LOCAL target is `Released` today. §14.3
    says protected kinds are shown to no model at all. Whether that closes §8.4's own
    consent path for every `protected=True` file, or only for files whose recognised
    KIND is on §13.3's protected list, is the question this test does not answer and
    must not decide by pinning one reading.
    """
    content_hash = "hash-protected"
    file_id = _file(gate_conn, "passport.pdf", content_hash)
    key = _observation(gate_conn, file_id, content_hash, raw_value=A_TITLE)
    ClassificationStore(gate_conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="highly_sensitive_credential_bearing", protected=True,
        basis="detector", evidence_refs=(key,), reliability_state="direct",
        observed_at=OBSERVED_AT))
    _store_policy(gate_conn, grants=())

    decision = _gate(gate_conn, permits_local=True).release(
        _request(key=key, file_id=file_id, target=CLOUD))

    assert not isinstance(decision, Released), (
        "an excerpt of a protected file reached a cloud model")
    assert isinstance(decision, Denied)
    assert decision.reason == "protected_cloud_target"
