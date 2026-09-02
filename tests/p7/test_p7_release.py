# tests/p7/test_p7_release.py
"""§8.4's one door: the request, the three branches, and no way around it.

The shape tests are the point, and they come first. A gate whose decision logic is
right and whose signature carries an `override=` keyword is not a gate, and the second
failure is the one review does not catch. Every shape assertion here is parsed from
`inspect.signature` and `dataclasses.fields` -- never from source text, which matches
comments and docstrings and has produced a false result eight times on this project.

`Denied(unclassified)` is the ordinary path. The detector is unwritten (D2), so on a
real corpus every file lands there; the denial tests need no evidence at all, and the
ONE `Released` test is the one that has to write a classification by hand.
"""
from __future__ import annotations

import dataclasses
import hashlib
import inspect
import json
import sqlite3
import tempfile
from pathlib import Path

import pytest

from database_agent.budget import set_ceiling
from database_agent.files_table import get_file, record_file
from evidence_shape.canonical import canonical_json
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.locator import serialize_locator
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import (
    TextUnit, new_id, record_observation, record_run, record_text_unit,
)

from privacy.authorship import COMPONENT_VERSION
from privacy.binding import consume_release, content_digest_of
from privacy.classification import ClassificationRecord, UNREADABLE_UNCLASSIFIED
from privacy.classification_store import ClassificationStore
from privacy.consent import NeedsConsent, pending_consent
from privacy.defaults import MORE_REDACTING
from privacy.denial import DECIDABLE_FROM_REQUEST, DENIAL_ORDER
from privacy.gate import TEXT_BEARING, Gate
from privacy.items import Excerpt, Filename, RedactedIdentifier
from privacy.policy import Policy, UNSET_POLICY_VERSION, set_policy
from privacy.redaction import RedactionManifest
from privacy.release import (
    DECISION_ORDER, DECISION_TYPES, DENIED_FIELDS, FORBIDDEN_PARAMETER_NAMES, LOCALITIES,
    NEEDS_CONSENT_FIELDS, RELEASED_FIELDS, RELEASE_PARAMETERS, REQUEST_FIELDS,
    Denied, ModelCallRequest, ModelTarget, NoPolicyInForce, Released, Target,
)
from privacy.resolve import UnresolvableSpan
from privacy.schema import create_privacy_schema

OBSERVED_AT = "2026-08-22T09:00:00Z"
PLAN_VERSION = "plan-v1"
TEXT = "Passport number A1234567 was issued in 2019 to the applicant."
SPAN = TextSpan(start=16, end=24)          # "A1234567"
LOCAL = ModelTarget(locality="local", model_id="llama-local", provider="on-device")
CLOUD = ModelTarget(locality="cloud", model_id="big-model", provider="a-provider")


# --------------------------------------------------------------------------
# seeding -- P1 and P4 writers only, all introspected live 2026-08-22
# --------------------------------------------------------------------------

def _file(conn: sqlite3.Connection, name: str, content_hash: str) -> str:
    """A `files` row. Live `record_file` stats the path, so the bytes must exist."""
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
    """One run, one text unit, one observation. Returns the `observation_key`."""
    # Live P4 requires R1's 64 lowercase hex; the plan's tags stay on the files row.
    digest = hashlib.sha256(content_hash.encode()).hexdigest()
    run_id = new_id()
    page = (Segment(kind="page", index=1),)
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=digest,
        extractor_name="fixture.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=OBSERVED_AT, observation_count=1))
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


def _container_evidence(conn: sqlite3.Connection, file_id: str,
                        content_hash: str) -> tuple[str, str]:
    """One container-addressed cell and its canonical locator."""
    digest = hashlib.sha256(content_hash.encode()).hexdigest()
    run_id = new_id()
    path = (Segment(kind="sheet", index=1), Segment(kind="row", index=4),
            Segment(kind="cell", index=3))
    location = Location(zone="table", container_path=path)
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=digest,
        extractor_name="fixture.table", extractor_version="1.0.0",
        source_type="spreadsheet", analysis_tier="native", config={},
        completeness="complete", started_at=OBSERVED_AT, observation_count=1))
    raw_value = "sensitive cell"
    record_observation(conn, Observation(
        file_id=file_id, content_hash=digest, extractor_name="fixture.table",
        extractor_version="1.0.0", source_type="spreadsheet", raw_value=raw_value,
        location=location, occurrence_count=1, observed_at=OBSERVED_AT,
        reliability="direct", run_id=run_id, context_before=None,
        context_after=None, context_truncated=False))
    key = observation_key(content_hash=digest, extractor_name="fixture.table",
                          locator=serialize_locator(location), raw_value=raw_value)
    return key, serialize_locator(location)


def _policy(conn: sqlite3.Connection, mode: str, *, grants=()) -> Policy:
    """Store a policy and read back the version the gate will stamp."""
    draft = Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode=mode,
        consent_grants=tuple(grants), redaction_settings=dict(MORE_REDACTING),
        automatic_move_permissions={}, plan_version=PLAN_VERSION, set_at=OBSERVED_AT)
    version = set_policy(conn, draft, component_version=COMPONENT_VERSION,
                         user_id="joseph", reason="test fixture")
    return dataclasses.replace(draft, policy_version=version)


def _classify(conn: sqlite3.Connection, file_id: str, content_hash: str, *,
              handling_class: str, protected: bool,
              refs=(observation_key(
                  content_hash="a" * 64, extractor_name="fixture.text",
                  locator="body:page=1#16-24", raw_value="A1234567"),)) -> None:
    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash, handling_class=handling_class,
        protected=protected, basis="detector", evidence_refs=tuple(refs),
        reliability_state="direct", observed_at=OBSERVED_AT))


def _classifier(value: str, *, context_before=None, context_after=None) -> str | None:
    """SPEC *Deferred* keeps identifier classes opaque; this enumerates nothing."""
    return "fixture-identifier-class"


def _transform(value: str, *, identifier_class: str) -> str:
    return "[redacted]"


def _gate(conn: sqlite3.Connection, **overrides) -> Gate:
    keywords: dict[str, object] = {
        "store": ClassificationStore(conn),
        "plan_version": PLAN_VERSION,
        "classifier": _classifier,
        "transform": _transform,
        "unclassified_permits_local": False,
        "scope_for": lambda file_id: "area-1",
        "files_in_scope": lambda scope: (),
        "component_version": COMPONENT_VERSION,
        "now": lambda: OBSERVED_AT,
        "user_id": "joseph",
    }
    keywords.update(overrides)
    return Gate(conn, **keywords)


def _request(*, items, model_target=CLOUD, file_ids=("f1",), stage="grouping",
             max_dossier_tokens=4000) -> ModelCallRequest:
    return ModelCallRequest(
        stage=stage, target=Target(file_ids=tuple(file_ids)),
        model_target=model_target, requested_items=tuple(items),
        prompt_template_id=f"template.{stage}",
        prompt_fingerprint=f"fingerprint.{stage}",
        max_dossier_tokens=max_dossier_tokens)


def _events(conn: sqlite3.Connection, event_type: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM events WHERE event_type = ? ORDER BY event_id",
        (event_type,)).fetchall()


@pytest.fixture()
def gate_conn(p7_conn):
    create_privacy_schema(p7_conn)
    return p7_conn


# --------------------------------------------------------------------------
# 1-12  shape: the signature, the fields, and the absence of an override
# --------------------------------------------------------------------------

def test_release_takes_the_request_and_nothing_else():
    """B2: P8 adopts SPEC §6's signature verbatim, so there is no second parameter.

    The WHITELIST half, and it is the stronger one: an equality proves no unpublished
    parameter exists AT ALL, where a blacklist only catches words someone thought of.
    """
    assert set(inspect.signature(Gate.release).parameters) == RELEASE_PARAMETERS
    assert RELEASE_PARAMETERS == {"self", "request"}


def test_no_signature_and_no_branch_field_names_an_override():
    """The BLACKLIST half, token-wise over every published name in the part."""
    names = set(inspect.signature(Gate.release).parameters)
    names |= set(inspect.signature(Gate.__init__).parameters)
    for kind in (ModelCallRequest, Target, ModelTarget, *DECISION_TYPES):
        names |= {f.name for f in dataclasses.fields(kind)}
    tokens = {token for name in names for token in name.split("_")}
    assert tokens.isdisjoint(FORBIDDEN_PARAMETER_NAMES), sorted(
        tokens & FORBIDDEN_PARAMETER_NAMES)


def test_the_blacklist_is_compared_token_wise_and_not_by_substring():
    """`unclassified_permits_local` is legitimate and must stay legitimate.

    A substring comparison would have to drop `permit` from the blacklist or rename a
    parameter to appease a test. Both are worse than splitting on underscores.
    """
    name = "unclassified_permits_local"
    assert name in inspect.signature(Gate.__init__).parameters
    # A substring rule would have to keep `permit` out of the blacklist to let this
    # name through. A token rule does not: "permits" is not "permit".
    assert set(name.split("_")).isdisjoint(FORBIDDEN_PARAMETER_NAMES)
    assert "permit" not in FORBIDDEN_PARAMETER_NAMES


def test_the_request_carries_references_only():
    """§8.4 puts complete extracted text, paths and OCR output in the always-local set.

    A request field that accepted one would have moved content before the gate had
    decided anything. Asserted over the annotations, not over a value.
    """
    annotations = {f.name: str(f.type) for f in dataclasses.fields(ModelCallRequest)}
    assert annotations["target"] == "Target"
    assert annotations["model_target"] == "ModelTarget"
    assert annotations["requested_items"] == "tuple[RequestedItem, ...]"
    for name, annotation in annotations.items():
        assert "Observation" not in annotation, name
        assert "Path" not in annotation, name
    assert [f.name for f in dataclasses.fields(ModelCallRequest)
            if str(f.type) == "str"] == [
        "stage", "prompt_template_id", "prompt_fingerprint"]


def test_request_fields_are_specs_seven_in_specs_order():
    assert REQUEST_FIELDS == (
        "stage", "target", "model_target", "requested_items", "prompt_template_id",
        "prompt_fingerprint", "max_dossier_tokens")
    assert "call_site" not in REQUEST_FIELDS   # B2 puts it inside the fingerprint


def test_released_fields_are_specs_six_in_specs_order():
    assert RELEASED_FIELDS == (
        "release_id", "audit_id", "policy_version", "materialised_items",
        "redaction_manifest", "model_target")


def test_denied_carries_evidence_refs_as_its_fourth_field():
    """SPEC §6: the explanation is "evidence-referenced". Task 13's `deny` takes them.

    The skeleton's Task 11 block lists three fields and omits this one; a constructor
    that accepts a value the dataclass cannot hold is not writable.
    """
    assert DENIED_FIELDS == ("reason", "explanation", "remedy_options",
                             "evidence_refs")
    denied = Denied(reason="unclassified", explanation="why", remedy_options=("ask",),
                    evidence_refs=("obs-key-1", "obs-key-2"))
    assert denied.evidence_refs == ("obs-key-1", "obs-key-2")
    assert Denied(reason="unclassified", explanation="why",
                  remedy_options=("ask",)).evidence_refs == ()


def test_needs_consent_has_no_reason_field():
    """"`Denied` is the gate's answer, `NeedsConsent` is a question only the user can
    answer." A caller cannot map it onto a denial reason even by accident."""
    assert "reason" not in NEEDS_CONSENT_FIELDS
    assert "consent_request_id" in NEEDS_CONSENT_FIELDS


def test_the_three_branches_share_no_field_name():
    """Structurally distinct, so no branch can be read as another.

    This also carries the assertion Task 14 makes over two of the three; it is made
    here over all three because this is the module that publishes the union.
    """
    named = [{f.name for f in dataclasses.fields(kind)} for kind in DECISION_TYPES]
    for left in range(len(named)):
        for right in range(left + 1, len(named)):
            assert named[left].isdisjoint(named[right])


def test_release_returns_one_of_exactly_three_types():
    """SPEC §6: `ReleaseDecision = Released | Denied | NeedsConsent`. No fourth.

    `NoPolicyInForce` is an exception rather than a member: it says the call cannot be
    EVALUATED, where all three of these say what the answer IS.
    """
    assert DECISION_TYPES == (Released, Denied, NeedsConsent)
    assert not issubclass(NoPolicyInForce, tuple(DECISION_TYPES))


def test_release_py_imports_no_privacy_module_but_consent_and_vocabulary():
    """The import direction Tasks 12-14 fixed, asserted by module introspection.

    `denial` imports `release.Denied` at run time and `binding` imports `Released`
    under TYPE_CHECKING, so anything `release` imported back from those two would
    close a cycle. `vocabulary` is a leaf and cannot.
    """
    import privacy.release as module

    bound = {value.__name__ for value in vars(module).values()
             if getattr(value, "__module__", "").startswith("privacy.")}
    imported = {getattr(value, "__module__", "")
                for value in vars(module).values()
                if getattr(value, "__module__", "").startswith("privacy.")}
    assert imported <= {"privacy.consent", "privacy.vocabulary", "privacy.release"}
    assert "NeedsConsent" in bound          # re-exported, not redefined
    assert NeedsConsent.__module__ == "privacy.consent"


def test_decision_order_puts_every_request_decidable_denial_before_materialisation():
    """No denial decidable from the request may be decided after one that reads text.

    A gate that materialised an excerpt and THEN discovered the mode forbade the call
    has read a sensitive file for a call that was never going to happen.
    """
    assert DECISION_ORDER == (
        "collect_request_denials", "needs_consent", "materialise",
        "collect_content_denials", "append_audit", "mint_release")
    assert DECISION_ORDER.index("collect_request_denials") < \
        DECISION_ORDER.index("materialise")
    assert DECISION_ORDER.index("append_audit") < DECISION_ORDER.index("mint_release")
    late = {r for r in DENIAL_ORDER if r not in DECIDABLE_FROM_REQUEST}
    assert max(DENIAL_ORDER.index(r) for r in DECIDABLE_FROM_REQUEST) < \
        min(DENIAL_ORDER.index(r) for r in late)


# --------------------------------------------------------------------------
# 13-20  the denial branch -- the ordinary path
# --------------------------------------------------------------------------

def test_an_unclassified_file_is_denied_and_that_is_the_ordinary_path(gate_conn):
    """No detector exists (D2), so this is what the gate answers on a Tuesday.

    No classification is written by this test, which is the point: the setup for the
    normal case is nothing at all.
    """
    file_id = _file(gate_conn, "unknown.pdf", "hash-unknown")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-unknown")
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert isinstance(decision, Denied)
    assert decision.reason == "unclassified"


def test_absence_never_resolves_to_a_lower_class(gate_conn):
    """SPEC §1: absence resolves to `unreadable_unclassified`, NEVER to `public_low`.

    §8.6: "Cost exhaustion must never turn into lower-quality automatic
    classification." Asserted on the audit record the gate wrote, not on an internal.
    """
    file_id = _file(gate_conn, "unknown.pdf", "hash-unknown")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-unknown")
    _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    row = _events(gate_conn, "model_release_denied")[0]
    explanation = json.loads(row["explanation"])
    assert explanation["file_sensitivity"] == UNREADABLE_UNCLASSIFIED
    assert "public_low" not in row["explanation"]


def test_offline_mode_denies_a_cloud_target_before_anything_is_read(gate_conn):
    """§8.4: under offline "No content leaves the device". Outermost in DENIAL_ORDER."""
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    _policy(gate_conn, "offline")
    key = _evidence(gate_conn, file_id, "hash-notes")
    _classify(gate_conn, file_id, "hash-notes",
              handling_class="public_low", protected=False)
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert isinstance(decision, Denied)
    assert decision.reason == "mode_forbids_target"


def test_overlapping_reasons_resolve_through_first_reason(gate_conn):
    """An unclassified protected file under `offline` with a cloud target triggers
    three reasons at once. The gate collects and DELEGATES; `DENIAL_ORDER` is Task
    13's and a gate that re-sorted them would be a second home for a total order."""
    file_id = _file(gate_conn, "passport.pdf", "hash-passport")
    _policy(gate_conn, "offline")
    key = _evidence(gate_conn, file_id, "hash-passport")
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert decision.reason == DENIAL_ORDER[0] == "mode_forbids_target"


def test_a_protected_file_with_a_cloud_target_is_denied(gate_conn):
    """SPEC §2's first protected consequence: not in cloud prompts BY DEFAULT."""
    file_id = _file(gate_conn, "passport.pdf", "hash-passport")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-passport")
    _classify(gate_conn, file_id, "hash-passport",
              handling_class="sensitive_personal", protected=True,
              refs=(key,))
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert isinstance(decision, Denied)
    assert decision.reason == "protected_cloud_target"
    assert decision.evidence_refs == (key,)


def test_a_denial_appends_exactly_one_model_release_denied(gate_conn):
    """§8.2: "Every significant event affecting a file." One event, not two."""
    file_id = _file(gate_conn, "unknown.pdf", "hash-unknown")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-unknown")
    _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert len(_events(gate_conn, "model_release_denied")) == 1
    assert _events(gate_conn, "model_release") == []


def test_the_gate_writes_no_classification_and_leaves_the_column_alone(gate_conn):
    """C4 and D2 in one assertion, which is why it is one test and not two.

    C4: "a gate that also wrote would be doing two jobs." D2: "`Unreadable or
    unclassified` is a GATE OUTCOME, not a file fact ... it lives on the release
    decision and never in that column."
    """
    file_id = _file(gate_conn, "unknown.pdf", "hash-unknown")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-unknown")
    before = get_file(gate_conn, file_id)["sensitivity_state"]
    _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    after = get_file(gate_conn, file_id)["sensitivity_state"]
    assert after == before
    assert after is None or UNREADABLE_UNCLASSIFIED not in str(after)
    assert ClassificationStore(gate_conn).current(file_id, "hash-unknown") is None


def test_a_filename_on_a_protected_records_file_is_denied(gate_conn):
    """§7.3: for Protected Records, "filenames and content must not be exposed in
    model prompts at all" -- and it binds a LOCAL target too, which is why it
    outranks the cloud rule in DENIAL_ORDER."""
    file_id = _file(gate_conn, "passport.pdf", "hash-passport")
    _policy(gate_conn, "cloud_assisted", grants=(("area-1", "cloud_model"),))
    _classify(gate_conn, file_id, "hash-passport",
              handling_class="highly_sensitive_credential_bearing", protected=True)
    decision = _gate(
        gate_conn,
        template_for=lambda _file_id: "Protected Records",
    ).release(_request(items=(Filename(file_id=file_id),),
                       model_target=LOCAL, file_ids=(file_id,), stage="residual"))
    assert isinstance(decision, Denied)
    assert decision.reason == "protected_records_template"


# --------------------------------------------------------------------------
# 21-23  the consent branch
# --------------------------------------------------------------------------

def test_a_protected_file_on_a_local_target_with_no_grant_needs_consent(gate_conn):
    """§8.4: "If a model needs text containing sensitive content, the user should see
    that requirement and choose." The cloud case is denied at DENIAL_ORDER 6; the
    local case is the one that reaches the user, and all four answers are open."""
    file_id = _file(gate_conn, "passport.pdf", "hash-passport")
    _policy(gate_conn, "local_model")
    key = _evidence(gate_conn, file_id, "hash-passport")
    _classify(gate_conn, file_id, "hash-passport",
              handling_class="sensitive_personal", protected=True)
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),
               RedactedIdentifier(observation_key=key, span=SPAN,
                                  identifier_class="fixture.identifier")),
        model_target=LOCAL, file_ids=(file_id,)))
    assert isinstance(decision, NeedsConsent)
    assert decision.consent_request_id
    assert decision.requirement.items == (
        (key, "body:page=1#16-24"),
        (key, "body:page=1#16-24"),
    )
    assert pending_consent(
        gate_conn, decision.consent_request_id
    ).requirement.items == decision.requirement.items
    assert len(_events(gate_conn, "consent_requested")) == 1
    assert _events(gate_conn, "model_release") == []


def test_a_container_address_round_trips_through_pending_consent(gate_conn):
    file_id = _file(gate_conn, "records.xlsx", "hash-cell")
    _policy(gate_conn, "local_model")
    key, locator = _container_evidence(gate_conn, file_id, "hash-cell")
    _classify(gate_conn, file_id, "hash-cell",
              handling_class="sensitive_personal", protected=True, refs=(key,))
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=None, reason="named cell"),),
        model_target=LOCAL, file_ids=(file_id,)))
    assert isinstance(decision, NeedsConsent)
    assert decision.requirement.items == ((key, locator),)
    assert pending_consent(
        gate_conn, decision.consent_request_id
    ).requirement.items == ((key, locator),)


def test_consent_refuses_a_span_that_disagrees_with_the_live_location(gate_conn):
    file_id = _file(gate_conn, "passport.pdf", "hash-mismatch")
    _policy(gate_conn, "local_model")
    key = _evidence(gate_conn, file_id, "hash-mismatch")
    _classify(gate_conn, file_id, "hash-mismatch",
              handling_class="sensitive_personal", protected=True, refs=(key,))
    with pytest.raises(UnresolvableSpan, match="disagrees with the live location"):
        _gate(gate_conn).release(_request(
            items=(Excerpt(observation_key=key, span=TextSpan(0, 4),
                           reason="wrong address"),),
            model_target=LOCAL, file_ids=(file_id,)))


def test_mixed_file_consent_lists_only_items_owned_by_unanswered_files(gate_conn):
    protected_id = _file(gate_conn, "protected.pdf", "hash-protected-mixed")
    public_id = _file(gate_conn, "public.pdf", "hash-public-mixed")
    _policy(gate_conn, "local_model")
    protected_key = _evidence(
        gate_conn, protected_id, "hash-protected-mixed",
    )
    public_key = _evidence(gate_conn, public_id, "hash-public-mixed")
    _classify(gate_conn, protected_id, "hash-protected-mixed",
              handling_class="sensitive_personal", protected=True,
              refs=(protected_key,))
    _classify(gate_conn, public_id, "hash-public-mixed",
              handling_class="public_low", protected=False, refs=(public_key,))

    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=protected_key, span=SPAN,
                       reason="protected heading"),
               Excerpt(observation_key=public_key, span=SPAN,
                       reason="public heading")),
        model_target=LOCAL, file_ids=(protected_id, public_id)))

    assert isinstance(decision, NeedsConsent)
    assert decision.requirement.file_ids == (protected_id,)
    assert decision.requirement.items == (
        (protected_key, "body:page=1#16-24"),
    )


def test_consent_refuses_an_observation_owned_by_a_non_target_file(gate_conn):
    target_id = _file(gate_conn, "target.pdf", "hash-target-owner")
    external_id = _file(gate_conn, "external.pdf", "hash-external-owner")
    _policy(gate_conn, "local_model")
    external_key = _evidence(gate_conn, external_id, "hash-external-owner")
    _classify(gate_conn, target_id, "hash-target-owner",
              handling_class="sensitive_personal", protected=True)

    with pytest.raises(UnresolvableSpan, match="outside request.target.file_ids"):
        _gate(gate_conn).release(_request(
            items=(Excerpt(observation_key=external_key, span=SPAN,
                           reason="external text"),),
            model_target=LOCAL, file_ids=(target_id,)))


def test_the_consent_branch_reads_the_protected_flag_and_not_a_class_list(gate_conn):
    """SPEC §2: "Neighbouring parts should consume the `protected` flag, not infer it
    from the class." Whether `protected` is co-extensive with the top two classes is
    NEEDS-JOSEPH C5 and this module answers it nowhere."""
    import privacy.release as release_module
    import privacy.gate as gate_module

    assert not hasattr(release_module, "SENSITIVE_CLASSES")
    assert not hasattr(gate_module, "SENSITIVE_CLASSES")
    file_id = _file(gate_conn, "odd.pdf", "hash-odd")
    _policy(gate_conn, "local_model")
    key = _evidence(gate_conn, file_id, "hash-odd")
    _classify(gate_conn, file_id, "hash-odd",
              handling_class="personal_non_sensitive", protected=True)
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        model_target=LOCAL, file_ids=(file_id,)))
    assert isinstance(decision, NeedsConsent)


def test_a_granted_scope_does_not_ask_again(gate_conn):
    """Consent already given is not a question. §8.4's grant is per corpus area, and
    what a corpus area IS stays Open question 3 -- `scope_for` is the caller's.

    It returns `str | None` because Open question 3 is open: a file that belongs to
    no area must be representable, and `None not in granted` is True, so such a file
    asks for consent rather than matching a grant by accident. Widened from
    `Callable[[str], str]` at assembly, when Task 20's fixtures -- which pass
    `lambda _file_id: None` -- were reconciled onto this name."""
    file_id = _file(gate_conn, "passport.pdf", "hash-passport")
    _policy(gate_conn, "local_model", grants=(("area-1", "local_model"),))
    key = _evidence(gate_conn, file_id, "hash-passport")
    _classify(gate_conn, file_id, "hash-passport",
              handling_class="sensitive_personal", protected=True)
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        model_target=LOCAL, file_ids=(file_id,)))
    assert isinstance(decision, Released)


# --------------------------------------------------------------------------
# 24-28  the release branch, the ordering guarantee, and what escapes
# --------------------------------------------------------------------------

def test_a_clean_call_returns_released_with_an_audit_id_already_in_the_log(gate_conn):
    """Done-means 4, and the ONE test that has to write a classification by hand.

    SPEC §6: "the audit record is appended ... BEFORE `Released` is returned. There is
    no interval in which content is releasable and unaudited." `append_audit` returns
    `cursor.lastrowid`, so the id exists only after the row does -- which makes the
    ordering a structural fact rather than a discipline.
    """
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    policy = _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-notes")
    _classify(gate_conn, file_id, "hash-notes",
              handling_class="public_low", protected=False, refs=(key,))
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert isinstance(decision, Released)
    assert decision.policy_version == policy.policy_version
    assert decision.model_target == CLOUD
    row = gate_conn.execute("SELECT * FROM events WHERE event_id = ?",
                            (decision.audit_id,)).fetchone()
    assert row is not None
    assert row["event_type"] == "model_release"
    assert row["subsystem"] == "P7"
    explanation = json.loads(row["explanation"])
    pairs = explanation["excerpts_included"]
    assert len(pairs) == 1 and pairs[0][0] == key
    # SPEC §7: the record stores (observation_key, span) pairs "not a second copy of
    # the text". The pair is enough to re-run `resolve.materialise`; the value is not
    # in the log.
    assert TEXT[SPAN.start:SPAN.end] not in row["explanation"]


def test_the_released_id_is_in_the_ledger_and_a_fabricated_one_is_not(gate_conn):
    """Task 12 proves single use; this proves the gate actually MINTED through it.

    A `Released` the gate returned consumes; one a caller builds does not, because the
    id it carries was never in the ledger.
    """
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    policy = _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-notes")
    _classify(gate_conn, file_id, "hash-notes",
              handling_class="public_low", protected=False)
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    # The gate folded the fourth binding term from what it resolved; the spender
    # folds it from the same items. `llm_harness.transport` folds it from the BYTES
    # instead, which is the point of the term -- see
    # `tests/integration/test_released_content_binding.py`.
    digest = content_digest_of(decision.materialised_items)
    consume_release(gate_conn, decision, model_target=CLOUD,
                    prompt_fingerprint="fingerprint.grouping",
                    policy_version=policy.policy_version, content_digest=digest)
    forged = dataclasses.replace(decision, release_id="0" * 32)
    with pytest.raises(Exception):
        consume_release(gate_conn, forged, model_target=CLOUD,
                        prompt_fingerprint="fingerprint.grouping",
                        policy_version=policy.policy_version, content_digest=digest)


def test_no_content_is_read_before_every_request_decidable_check_has_run(
        gate_conn, monkeypatch):
    """The ordering property, proven by making materialisation fail the test.

    "Nothing materialises until every check that could deny has run" is the reason
    `DECISION_ORDER` exists, and a comment is not a proof.
    """
    import privacy.gate as gate_module

    def _explode(conn, item):   # pragma: no cover - the assertion IS not calling it
        raise AssertionError("the gate read content before it had decided")

    monkeypatch.setattr(gate_module, "materialise", _explode)
    file_id = _file(gate_conn, "passport.pdf", "hash-passport")
    _policy(gate_conn, "offline")
    key = _evidence(gate_conn, file_id, "hash-passport")
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert isinstance(decision, Denied)


def test_materialised_items_hold_only_what_had_a_value_to_resolve(gate_conn):
    """SPEC §6: "materialised_items[] post-redaction values only."

    §4: an evidence reference is "an id only -- no content", and a filename, a
    candidate label and a metadata field carry no local content either. The gate does
    not echo back what it did not touch; the caller still holds the request it sent.
    """
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-notes")
    _classify(gate_conn, file_id, "hash-notes",
              handling_class="public_low", protected=False)
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),
               Filename(file_id=file_id)),
        file_ids=(file_id,)))
    assert isinstance(decision, Released)
    assert len(decision.materialised_items) == 1
    assert decision.materialised_items[0].observation_key == key
    assert decision.materialised_items[0].value == "[redacted]"
    assert isinstance(decision.redaction_manifest, RedactionManifest)
    assert decision.redaction_manifest.any_redacted is True
    assert TEXT_BEARING == (Excerpt, RedactedIdentifier)


def test_a_call_with_no_policy_in_force_raises_rather_than_defaulting(gate_conn):
    """W1's local-first floor is resolved in `defaults.effective_policy`, where
    Done-means 12 is proven. A second resolution here would be a second home for it,
    and it would need `install_mode`, which is Open question 11."""
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    key = _evidence(gate_conn, file_id, "hash-notes")
    with pytest.raises(NoPolicyInForce):
        _gate(gate_conn).release(_request(
            items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
            file_ids=(file_id,)))


def test_a_resolve_failure_propagates_and_is_not_a_denial(gate_conn):
    """A span the evidence does not carry is a contract violation by the CALLER.

    P4's `check_span_anchor` "raises; never returns a repair", and a gate that
    repaired would release text nobody addressed. `Denied` and `NeedsConsent` are
    values; these two are exceptions, and the difference is deliberate.
    """
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    _policy(gate_conn, "hybrid")
    _evidence(gate_conn, file_id, "hash-notes")
    _classify(gate_conn, file_id, "hash-notes",
              handling_class="public_low", protected=False)
    with pytest.raises(UnresolvableSpan):
        _gate(gate_conn).release(_request(
            items=(Excerpt(observation_key="no-such-key", span=SPAN,
                           reason="heading"),),
            file_ids=(file_id,)))


def test_an_unset_dossier_ceiling_and_no_measurement_cannot_deny(gate_conn):
    """M9's backstop, and the two reasons it stays unreachable by default.

    `get_ceiling` returns `None` when nothing set it, and P7 owns no tokenizer, so
    `measure_tokens` is injected. With a ceiling AND a measurement the backstop fires;
    a P8 test that reaches it through the normal path is a P8 failure, not a gate
    result. Do not delete the check.
    """
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-notes")
    _classify(gate_conn, file_id, "hash-notes",
              handling_class="public_low", protected=False)
    request = _request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,))
    assert isinstance(_gate(gate_conn).release(request), Released)

    set_ceiling(gate_conn, "model.max_dossier_tokens_per_call", 10)
    decision = _gate(
        gate_conn, measure_tokens=lambda request, items: 11).release(request)
    assert isinstance(decision, Denied)
    assert decision.reason == "dossier_over_budget"


# ==========================================================================
# The two Gate.release blockers -- gate.py:134-135 on the parent commit.
#
# Both are PLAN defects, not build defects: the executor transcribed the
# plan's Step 5 block byte-for-byte, and the plan carries both lines
# verbatim (P7 PLAN.md:9665). §8.4 calls the gate "the ONE door"; these
# tests are what makes it one.
# ==========================================================================

def _two_areas(conn):
    """One unprotected file in `area-1`, one protected file in `area-2`."""
    ordinary = _file(conn, "notes.pdf", "hash-notes")
    protected = _file(conn, "passport.pdf", "hash-passport")
    _classify(conn, ordinary, "hash-notes",
              handling_class="personal_non_sensitive", protected=False)
    _classify(conn, protected, "hash-passport",
              handling_class="sensitive_personal", protected=True)
    areas = {ordinary: "area-1", protected: "area-2"}
    return ordinary, protected, areas


def test_a_protected_file_is_not_released_because_another_file_was_listed_first(
        gate_conn):
    """BLOCKER 1 -- `scope = self._scope_for(file_ids[0])`.

    One file's corpus area decided revocation, cloud protection AND consent for
    every file in the request. A protected file in an UNGRANTED area, placed
    second, rode out on the first file's grant: released to a cloud model with a
    real minted release_id. Reversing the tuple denied it, which is the whole
    proof -- the decision depended on list order, and §8.4's door does not.
    """
    ordinary, protected, areas = _two_areas(gate_conn)
    key = _evidence(gate_conn, protected, "hash-passport")
    _policy(gate_conn, "cloud_assisted", grants=(("area-1", "cloud_model"),))
    gate = _gate(gate_conn, scope_for=lambda file_id: areas[file_id])

    decision = gate.release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        model_target=CLOUD, file_ids=(ordinary, protected)))

    assert not isinstance(decision, Released), (
        "a protected file in an ungranted area reached a cloud model because an "
        "unprotected file was listed ahead of it")


def test_the_ordering_that_already_denied_still_denies(gate_conn):
    """The control for the test above: same request, reversed. It denied before
    the fix and must still deny after it, or the fix traded one order for another."""
    ordinary, protected, areas = _two_areas(gate_conn)
    key = _evidence(gate_conn, protected, "hash-passport")
    _policy(gate_conn, "cloud_assisted", grants=(("area-1", "cloud_model"),))
    gate = _gate(gate_conn, scope_for=lambda file_id: areas[file_id])

    decision = gate.release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        model_target=CLOUD, file_ids=(protected, ordinary)))

    assert not isinstance(decision, Released)


def test_a_local_model_grant_does_not_authorize_a_cloud_release(gate_conn):
    """BLOCKER 2 -- `granted = tuple(name for name, _option in ...)`.

    §8.4 asks the user to "choose whether to allow a local model, a cloud model, a
    redacted prompt, or no model use". The gate dropped the choice and kept only
    the scope, so answering LOCAL MODEL to a local-model prompt authorised a CLOUD
    release of that same protected file -- one file, no ordering trick, straight
    through P7's own published consent flow.
    """
    file_id = _file(gate_conn, "passport.pdf", "hash-passport")
    key = _evidence(gate_conn, file_id, "hash-passport")
    _classify(gate_conn, file_id, "hash-passport",
              handling_class="sensitive_personal", protected=True)
    _policy(gate_conn, "cloud_assisted", grants=(("area-1", "local_model"),))

    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        model_target=CLOUD, file_ids=(file_id,)))

    assert not isinstance(decision, Released), (
        "a local_model grant authorised a cloud release")


def test_a_cloud_grant_still_authorizes_the_cloud_release_it_was_given_for(
        gate_conn):
    """The carve-out §8.4 does intend must survive: cloud_assisted plus an explicit
    cloud_model grant for that area releases."""
    file_id = _file(gate_conn, "passport.pdf", "hash-passport")
    key = _evidence(gate_conn, file_id, "hash-passport")
    _classify(gate_conn, file_id, "hash-passport",
              handling_class="sensitive_personal", protected=True)
    _policy(gate_conn, "cloud_assisted", grants=(("area-1", "cloud_model"),))

    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        model_target=CLOUD, file_ids=(file_id,)))

    assert isinstance(decision, Released)


def test_every_consent_option_says_which_localities_it_authorizes():
    """The table is total, and it is a table for the reason `CONSENT_AUTHORIZES` is:
    written as a negated `if`, it is one edit away from silently granting."""
    from privacy.consent import CONSENT_AUTHORIZES_LOCALITY, grant_authorizes
    from privacy.vocabulary import CONSENT_OPTIONS

    assert set(CONSENT_AUTHORIZES_LOCALITY) == set(CONSENT_OPTIONS)
    for option, localities in CONSENT_AUTHORIZES_LOCALITY.items():
        assert localities <= set(LOCALITIES), option

    # the blocker, as a table row: the answer binds to what was asked.
    assert grant_authorizes("local_model", "local") is True
    assert grant_authorizes("local_model", "cloud") is False
    assert grant_authorizes("cloud_model", "cloud") is True
    assert grant_authorizes("no_model_use", "local") is False


def test_an_option_outside_the_four_raises_rather_than_reading_as_a_denial():
    """SPEC §1: a value outside the vocabulary is "a load error, not a fallback". A
    `False` here would hide a corrupt policy row behind a correct-looking refusal."""
    from privacy.consent import grant_authorizes
    with pytest.raises(KeyError):
        grant_authorizes("cloud_model_but_only_tuesdays", "cloud")
