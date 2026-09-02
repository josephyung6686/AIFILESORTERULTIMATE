"""P7 gate is the only way a live Released reaches P8 transport."""
from __future__ import annotations

import hashlib
import tempfile
from dataclasses import replace
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import record_file
from extractors.schema import create_extraction_schema
from evidence_shape.canonical import canonical_json
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.locator import serialize_locator
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import (
    TextUnit, new_id, record_observation, record_run, record_text_unit,
)
from llm_harness.fingerprint import dossier_content_address, prompt_fingerprint
from llm_harness.dossier import build_dossier, field_glossary, canonical_dossier_bytes
from llm_harness.records import (
    DossierRequest, PromptDefinition, ValidationUnavailable, build_call_payload,
)
from llm_harness.schema import create_llm_schema
from llm_harness.transport import ModelClient, ModelResponse, issue
from llm_harness.vocabulary import A_FACT, REDUCTION_NONE, REMAINS_AMBIGUOUS
from privacy.binding import BindingMismatch, ReleaseAlreadySpent
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.defaults import MORE_REDACTING
from privacy.gate import Gate
from privacy.items import Excerpt
from privacy.policy import Policy, UNSET_POLICY_VERSION, set_policy
from privacy.release import Denied, ModelCallRequest, ModelTarget, Released, Target
from privacy.schema import create_privacy_schema

from p8.conftest import make_evidence_item
from p8.test_p8_transport import Recorder, _spent
from llm_harness.fixtures import FIXTURE_HANDLE_KEY


OBSERVED_AT = "2026-08-22T09:00:00Z"
PLAN_VERSION = "plan-v1"
TEXT = "Passport number A1234567 was issued in 2019 to the applicant."
SPAN = TextSpan(start=16, end=24)
LOCAL = ModelTarget(locality="local", model_id="llama-local", provider="on-device")
CLOUD = ModelTarget(locality="cloud", model_id="big-model", provider="a-provider")
COMPONENT = "0.1.0"


@pytest.fixture()
def egress_conn(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    create_privacy_schema(conn)
    create_llm_schema(conn)
    return conn


def _file(conn, name: str, content_hash: str) -> str:
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
        content_hash=content_hash,
    )


def _evidence(conn, file_id: str, content_hash: str) -> str:
    digest = hashlib.sha256(content_hash.encode()).hexdigest()
    run_id = new_id()
    page = (Segment(kind="page", index=1),)
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=digest,
        extractor_name="fixture.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=OBSERVED_AT, observation_count=1,
    ))
    record_text_unit(conn, TextUnit(run_id=run_id, container_path=page, text=TEXT))
    location = Location(zone="body", container_path=page, text_span=SPAN)
    record_observation(conn, Observation(
        file_id=file_id, content_hash=digest, extractor_name="fixture.text",
        extractor_version="1.0.0", source_type="text_document",
        raw_value=TEXT[SPAN.start:SPAN.end], location=location, occurrence_count=1,
        observed_at=OBSERVED_AT, reliability="direct", run_id=run_id,
        context_before=TEXT[:SPAN.start], context_after=TEXT[SPAN.end:],
        context_truncated=False,
    ))
    return observation_key(
        content_hash=digest, extractor_name="fixture.text",
        locator=serialize_locator(location), raw_value=TEXT[SPAN.start:SPAN.end],
    )


def _store_policy(conn, mode: str, *, grants=()) -> Policy:
    draft = Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode=mode,
        consent_grants=tuple(grants), redaction_settings=dict(MORE_REDACTING),
        automatic_move_permissions={}, plan_version=PLAN_VERSION, set_at=OBSERVED_AT,
    )
    version = set_policy(
        conn, draft, component_version=COMPONENT, user_id="joseph",
        reason="test fixture",
    )
    return replace(draft, policy_version=version)


def _classify(conn, file_id: str, content_hash: str, *, key: str) -> None:
    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="public_low", protected=False, basis="detector",
        evidence_refs=(key,), reliability_state="direct", observed_at=OBSERVED_AT,
    ))


def _classifier(value: str, *, context_before=None, context_after=None) -> str | None:
    return "fixture-identifier-class"


def _transform(value: str, *, identifier_class: str) -> str:
    return "[redacted]"


def _gate(conn, **overrides) -> Gate:
    keywords: dict[str, object] = {
        "store": ClassificationStore(conn),
        "plan_version": PLAN_VERSION,
        "classifier": _classifier,
        "transform": _transform,
        "unclassified_permits_local": False,
        "scope_for": lambda file_id: "area-1",
        "files_in_scope": lambda scope: (),
        "component_version": COMPONENT,
        "now": lambda: OBSERVED_AT,
        "user_id": "joseph",
    }
    keywords.update(overrides)
    return Gate(conn, **keywords)


def _prompt() -> PromptDefinition:
    return PromptDefinition(
        template_id="template.grouping",
        template_bytes=b"TEMPLATE",
        response_schema_bytes=b'{"type":"object"}',
        call_site=A_FACT,
        call_site_version="1",
        shaping_policy_bytes=b'{"policy":"authored"}',
    )


def _request(*, items, model_target, file_ids, fingerprint: str) -> ModelCallRequest:
    return ModelCallRequest(
        stage="grouping", target=Target(file_ids=tuple(file_ids)),
        model_target=model_target, requested_items=tuple(items),
        prompt_template_id="template.grouping",
        prompt_fingerprint=fingerprint,
        max_dossier_tokens=4000,
    )


def _payload_from(released: Released, prompt: PromptDefinition):
    dossier = b"\n".join(
        item.value.encode("utf-8") for item in released.materialised_items
    )
    return build_call_payload(
        prompt,
        dossier,
        model_target=released.model_target,
        policy_version=released.policy_version,
        release_id=released.release_id,
        dossier_id=dossier_content_address(
            dossier, allowed_vocabulary=(), allowed_schema_bytes=b"{}",
        ),
    )


def _seed_classified(conn, *, name: str, content_hash: str) -> tuple[str, str]:
    file_id = _file(conn, name, content_hash)
    key = _evidence(conn, file_id, content_hash)
    _classify(conn, file_id, content_hash, key=key)
    return file_id, key


def test_unclassified_gate_denies_and_transport_is_never_reached(egress_conn):
    recorder = Recorder()
    file_id = _file(egress_conn, "unknown.pdf", "hash-unknown")
    _store_policy(egress_conn, "hybrid")
    key = _evidence(egress_conn, file_id, "hash-unknown")
    prompt = _prompt()
    decision = _gate(egress_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        model_target=CLOUD, file_ids=(file_id,),
        fingerprint=prompt_fingerprint(prompt),
    ))
    assert isinstance(decision, Denied)
    assert decision.reason == "unclassified"
    assert recorder.calls == []
    issued = list(egress_conn.execute(
        "SELECT event_type FROM events WHERE event_type = 'model_call_issued'"
    ))
    assert issued == []


def test_gate_release_then_issue_invokes_the_client_exactly_once(egress_conn):
    recorder = Recorder()
    file_id, key = _seed_classified(egress_conn, name="notes.pdf", content_hash="hash-notes")
    policy = _store_policy(egress_conn, "hybrid")
    prompt = _prompt()
    digest = prompt_fingerprint(prompt)
    decision = _gate(egress_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        model_target=CLOUD, file_ids=(file_id,),
        fingerprint=digest,
    ))
    assert isinstance(decision, Released)
    assert decision.model_target == CLOUD
    assert decision.policy_version == policy.policy_version
    payload = _payload_from(decision, prompt)
    assert payload.prompt_fingerprint == digest
    result = issue(
        egress_conn, decision, payload,
        model_client=ModelClient(model_target=CLOUD, invoke=recorder),
    )
    assert isinstance(result, ModelResponse)
    assert recorder.calls == [payload.model_visible_bytes]
    assert _spent(egress_conn, decision.release_id) is not None
    issued = list(egress_conn.execute(
        "SELECT event_type FROM events WHERE event_type = 'model_call_issued'"
    ))
    assert len(issued) == 1


def test_second_issue_of_a_gate_release_is_already_spent(egress_conn):
    recorder = Recorder()
    file_id, key = _seed_classified(egress_conn, name="notes.pdf", content_hash="hash-notes")
    _store_policy(egress_conn, "hybrid")
    prompt = _prompt()
    decision = _gate(egress_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        model_target=CLOUD, file_ids=(file_id,),
        fingerprint=prompt_fingerprint(prompt),
    ))
    payload = _payload_from(decision, prompt)
    client = ModelClient(model_target=CLOUD, invoke=recorder)
    issue(egress_conn, decision, payload, model_client=client)
    with pytest.raises(ReleaseAlreadySpent):
        issue(egress_conn, decision, payload, model_client=client)
    assert len(recorder.calls) == 1


def test_cloud_client_cannot_spend_a_local_gate_release(egress_conn):
    recorder = Recorder()
    file_id, key = _seed_classified(egress_conn, name="notes.pdf", content_hash="hash-local")
    _store_policy(egress_conn, "hybrid")
    prompt = _prompt()
    decision = _gate(egress_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        model_target=LOCAL, file_ids=(file_id,),
        fingerprint=prompt_fingerprint(prompt),
    ))
    assert isinstance(decision, Released)
    assert decision.model_target == LOCAL
    payload = _payload_from(decision, prompt)
    with pytest.raises(BindingMismatch):
        issue(
            egress_conn, decision, payload,
            model_client=ModelClient(model_target=CLOUD, invoke=recorder),
        )
    assert recorder.calls == []
    assert _spent(egress_conn, decision.release_id) is None


def test_local_client_cannot_spend_a_cloud_gate_release(egress_conn):
    recorder = Recorder()
    file_id, key = _seed_classified(egress_conn, name="notes.pdf", content_hash="hash-cloud")
    _store_policy(egress_conn, "hybrid")
    prompt = _prompt()
    decision = _gate(egress_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        model_target=CLOUD, file_ids=(file_id,),
        fingerprint=prompt_fingerprint(prompt),
    ))
    assert isinstance(decision, Released)
    payload = _payload_from(decision, prompt)
    with pytest.raises(BindingMismatch):
        issue(
            egress_conn, decision, payload,
            model_client=ModelClient(model_target=LOCAL, invoke=recorder),
        )
    assert recorder.calls == []
    assert _spent(egress_conn, decision.release_id) is None


def _dossier_request(*, file_id: str, key: str, fingerprint: str) -> DossierRequest:
    """The builder's side of the seam, addressed at the same released item."""
    return DossierRequest(
        call_site=A_FACT,
        subject_ref=file_id,
        eligibility_reason=REMAINS_AMBIGUOUS,
        evidence_items=(make_evidence_item(evidence_ref=key),),
        conflicts=(),
        model_call_request=_request(
            items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
            model_target=CLOUD, file_ids=(file_id,), fingerprint=fingerprint,
        ),
        plan_version=None,
        evidence_snapshot_id="snap-1",
    )


def _released_and_body(conn) -> tuple[Released, str]:
    """One real gate release, carried through the real `build_dossier`."""
    file_id, key = _seed_classified(
        conn, name="passport.pdf", content_hash="hash-passport")
    _store_policy(conn, "hybrid")
    prompt = _prompt()
    digest = prompt_fingerprint(prompt)
    decision = _gate(conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        model_target=CLOUD, file_ids=(file_id,), fingerprint=digest,
    ))
    assert isinstance(decision, Released), decision
    dossier = build_dossier(
        _dossier_request(file_id=file_id, key=key, fingerprint=digest),
        decision,
        reduction_rung=REDUCTION_NONE,
        allowed_vocabulary=("school",),
        prompt=prompt, handle_key=FIXTURE_HANDLE_KEY,
    )
    assert not isinstance(dossier, ValidationUnavailable), dossier
    return decision, canonical_dossier_bytes(dossier, prompt, handle_key=FIXTURE_HANDLE_KEY).decode("utf-8")


def test_the_release_carries_no_text_outside_the_requested_span(egress_conn):
    """§8.4 puts "complete extracted text" in the always-local set
    (`planning/00-database-agent-product-design.md:186`) and P7 SPEC:248 says
    `materialised_items[] post-redaction values only`. The gate redacted the
    value and then handed `context_before` / `context_after` straight off the
    pre-redaction record into `Released`, and `dossier._released_body` wrote both
    into the canonical model-visible bytes -- so an 8-character requested span
    released every character of its unit, the redacted name masked and the
    passport number beside it not.

    The property, not the mechanism: no window of the source unit that reaches
    outside the requested span may appear in the bytes the model is shown.

    **Why the glossary is subtracted before the scan, and why that is not a
    loophole.** The dossier now also carries `field_glossary()`, whose prose is
    authored English -- and English collides with English. `school`\'s meaning
    ends "never the application target", this unit ends "to the applicant", and
    the scan below reported ` the appli` as released source text. It was not:
    those characters are in the bytes because a fixed sentence about a FIELD is,
    and they would be there for a file that said nothing of the kind.

    Subtracting it can only hide a leak if the glossary could ever carry
    something about the file, and four tests in
    `tests/p8/test_p8_field_glossary.py` say it cannot -- it varies between two
    files (it does not), it is handed anything but the vocabulary (it is not),
    always-local content reaches it (it does not), and every meaning is verbatim
    from a cited ratified source. So the subtraction removes a constant, and a
    constant cannot encode a secret.
    """
    released, body = _released_and_body(egress_conn)

    item = released.materialised_items[0]
    assert item.value == "[redacted]"          # the span itself was redacted
    assert "[redacted]" in body                # and the release is not empty

    # The file-independent constant, removed by VALUE rather than by position, so
    # this keeps working if the dossier ever moves where it puts the glossary.
    meanings = field_glossary(("school",))
    assert meanings, "the glossary went empty; this subtraction is now hiding a leak"
    scanned = body
    for meaning in meanings.values():
        scanned = scanned.replace(meaning, " ")

    window = SPAN.end - SPAN.start + 2         # wider than the requested span
    leaked = [
        TEXT[start:start + window]
        for start in range(len(TEXT) - window + 1)
        if TEXT[start:start + window] in scanned
    ]
    assert leaked == [], f"released text outside the requested span: {leaked}"


def test_the_manifest_still_carries_the_context_it_always_did(egress_conn):
    """M5 split the context out "precisely so §8.4 can redact a value without
    dropping its context" (`privacy/redaction.py`). That property is about the
    LOCAL audit entry, which travels inside the audit event's explanation. It is
    kept; this asserts it was not thrown away with the released copy."""
    released, _body_text = _released_and_body(egress_conn)

    entry = released.redaction_manifest.entries[0]
    assert entry.context_before == TEXT[:SPAN.start]
    assert entry.context_after == TEXT[SPAN.end:]
    assert entry.context_truncated is False


def test_no_released_record_has_a_place_to_put_raw_context():
    """The guard. Removal, not discipline: a released record with no context
    field cannot re-release context, and the model-visible payload builder must
    not name one either. `Materialised` and `RedactionEntry` keep theirs -- they
    are the pre-redaction resolution record and the local audit entry.
    """
    import dataclasses
    import inspect

    import llm_harness.dossier as dossier_module
    from llm_harness.records import ReleasedEvidence
    from privacy.release import ReleasedItem

    forbidden = {"context_before", "context_after", "context_truncated"}
    for record in (ReleasedItem, ReleasedEvidence):
        names = {field.name for field in dataclasses.fields(record)}
        assert not (names & forbidden), f"{record.__name__} carries {names & forbidden}"

    source = inspect.getsource(dossier_module)
    for name in sorted(forbidden):
        assert name not in source, f"dossier.py still names {name}"
