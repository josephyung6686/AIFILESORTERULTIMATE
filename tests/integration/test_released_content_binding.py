# tests/integration/test_released_content_binding.py
"""CR-02: `transport.issue` must not send bytes the gate never released.

`00` §8.4 is sequencing before it is anything else -- "Privacy policy must be
enforced before content reaches any model or external connector" -- and P8's
Done-means 1 states the method: exactly one function constructs a model request, and
its only content parameter is a `Released`.

`issue` takes TWO content-shaped arguments: the `Released`, and a `CallPayload` whose
`canonical_dossier_bytes` are what the model is actually shown. Before this file
nothing compared them. `transport_guard`'s docstring named three checks that
supposedly proved the payload's bytes were the released dossier, and none of the
three ever sees the `Released`:

  * `records.build_call_payload` never receives it;
  * `CallPayload.__post_init__` checks `model_visible_bytes == assemble(prompt,
    canonical_dossier_bytes)` -- self-consistency;
  * `_require_sources` recomputes the fingerprint and reassembles the same two
    fields -- self-consistency again.

`_require_binding` compares `model_target`, `release_id`, `policy_version`, and
`consume_release` compares `BINDING_TERMS`. Those bind WHO receives the bytes and
UNDER WHAT POLICY. Nothing bound WHAT.

So the reviewer minted a real release whose one materialised item was `"[redacted]"`,
handed `issue` a payload whose dossier bytes were a dump of every `raw_value`, every
`context_before`/`context_after`, every `current_path` and every `content_hash`, and
got a `ModelResponse` back with all of it on the wire. That is `test_the_reviewers_
probe_reaches_the_client` below, and it is the whole finding.

The four probes after it are the ways round a check that only compared a digest of a
projection: a faithful evidence list with a poisoned sibling key, a faithful entry
with a smuggled extra field, a substituted value, and a `dataclasses.replace`d
`Released` that relabels what was released. Each must be refused before the ledger
spend -- which means, in every case: the client is never called, the release is
still unspent, and no `model_call_issued` event was written.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
from dataclasses import replace
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import record_file
from evidence_shape.canonical import canonical_json
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.locator import serialize_locator
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import (
    TextUnit, new_id, record_observation, record_run, record_text_unit,
)
from extractors.schema import create_extraction_schema
from llm_harness.dossier import canonical_dossier_bytes, build_dossier
from llm_harness.fingerprint import dossier_content_address, prompt_fingerprint
from llm_harness.fixtures import FIXTURE_HANDLE_KEY
from llm_harness.records import (
    DossierRequest, PromptDefinition, build_call_payload,
)
from llm_harness.released_content import DOSSIER_BODY_KEYS, released_content_digest
from llm_harness.schema import create_llm_schema
from llm_harness.transport import ModelClient, ModelResponse, issue
from llm_harness.vocabulary import A_FACT, REDUCTION_NONE, REMAINS_AMBIGUOUS
from privacy.binding import BindingMismatch, content_digest_of
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.defaults import MORE_REDACTING
from privacy.gate import Gate
from privacy.items import Excerpt
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from privacy.release import (
    CONTENT_BOUND_FIELDS, RELEASED_EVIDENCE_FIELDS,
    ModelCallRequest, ModelTarget, Released, Target,
)
from privacy.schema import create_privacy_schema

from p8.conftest import make_evidence_item

OBSERVED_AT = "2026-09-02T09:00:00Z"
PLAN_VERSION = "plan-cr02"
COMPONENT = "0.1.0"
CLOUD = ModelTarget(locality="cloud", model_id="big-model", provider="a-provider")
#: The caller's echo of P1's ceiling. A number only a test may choose.
MAX_DOSSIER_TOKENS = 4000

#: The sentence the corpus holds, and the span the call asks for. The redaction
#: transform below turns the span into `"[redacted]"`, so the pre-redaction words are
#: exactly what must never reach the client.
TEXT = "This syllabus covers the spring term for BUSIB 4300.\npage 1 of 1\n"
SPAN = TextSpan(start=40, end=50)
PRE_REDACTION = TEXT[SPAN.start:SPAN.end]
PRIVATE_PATH = "/Users/joseph/Documents/Legal/Divorce/Syllabus.pdf"


class Recorder:
    """Every byte string the client is handed. `calls == []` is the assertion."""

    def __init__(self) -> None:
        self.calls: list[bytes] = []

    def __call__(self, blob: bytes) -> bytes:
        self.calls.append(blob)
        return b'{"claims":[]}'


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
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=4096,
        observed_timestamps=canonical_json({"modified": OBSERVED_AT}),
        parent_folder_context="corpus", mime_type="application/pdf",
        detected_format="pdf", scan_state="scanned", materialized=True,
        content_hash=content_hash,
    )


def _evidence(conn, file_id: str, content_hash: str) -> str:
    digest = hashlib.sha256(content_hash.encode()).hexdigest()
    run_id = new_id()
    page = (Segment(kind="page", index=1), Segment(kind="heading", index=1))
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=digest,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=OBSERVED_AT, observation_count=1,
    ))
    record_text_unit(conn, TextUnit(run_id=run_id, container_path=page, text=TEXT))
    location = Location(zone="heading", container_path=page, text_span=SPAN)
    record_observation(conn, Observation(
        file_id=file_id, content_hash=digest, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document",
        raw_value=PRE_REDACTION, location=location, occurrence_count=1,
        observed_at=OBSERVED_AT, reliability="direct", run_id=run_id,
        context_before=TEXT[:SPAN.start], context_after=TEXT[SPAN.end:],
        context_truncated=False,
    ))
    return observation_key(
        content_hash=digest, extractor_name="pdf.text",
        locator=serialize_locator(location), raw_value=PRE_REDACTION,
    )


def _store_policy(conn) -> Policy:
    draft = Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode="cloud_assisted",
        consent_grants=(("area-1", "cloud_model"),),
        redaction_settings=dict(MORE_REDACTING),
        automatic_move_permissions={}, plan_version=PLAN_VERSION,
        set_at=OBSERVED_AT,
    )
    version = set_policy(conn, draft, component_version=COMPONENT,
                         user_id="joseph", reason="CR-02")
    return replace(draft, policy_version=version)


def _classify(conn, file_id: str, content_hash: str, *, key: str) -> None:
    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash, handling_class="public_low",
        protected=False, basis="detector", evidence_refs=(key,),
        reliability_state="direct", observed_at=OBSERVED_AT,
    ))


def _gate(conn) -> Gate:
    return Gate(
        conn, store=ClassificationStore(conn), plan_version=PLAN_VERSION,
        classifier=lambda value, *, context_before=None, context_after=None:
            "course-code",
        transform=lambda value, *, identifier_class: "[redacted]",
        unclassified_permits_local=False,
        scope_for=lambda file_id: "area-1",
        files_in_scope=lambda scope: (),
        component_version=COMPONENT, now=lambda: OBSERVED_AT, user_id="joseph",
    )


def _prompt() -> PromptDefinition:
    """Injected, and deliberately not prompt text. `76`: `template_bytes` is
    fingerprinted into every audit record, so the real one is the owner's to ratify
    and a test's placeholder must not read like a candidate."""
    return PromptDefinition(
        template_id="template.under-ratification",
        template_bytes=b"<no prompt has been ratified; this is a test placeholder>",
        response_schema_bytes=b'{"type":"object"}',
        call_site=A_FACT, call_site_version="1",
        shaping_policy_bytes=b'{"policy":"injected"}',
    )


ALLOWED = ("subject",)


def _released(conn) -> tuple[Released, PromptDefinition, DossierRequest]:
    """One real release through the real gate, on the ordinary cloud path."""
    content_hash = "hash-syllabus"
    file_id = _file(conn, "Syllabus.pdf", content_hash)
    key = _evidence(conn, file_id, content_hash)
    _classify(conn, file_id, content_hash, key=key)
    _store_policy(conn)
    prompt = _prompt()
    item = Excerpt(observation_key=key, span=SPAN, reason="heading")
    model_call = ModelCallRequest(
        stage="fact_resolution", target=Target(file_ids=(file_id,)),
        model_target=CLOUD, requested_items=(item,),
        prompt_template_id=prompt.template_id,
        prompt_fingerprint=prompt_fingerprint(prompt),
        max_dossier_tokens=MAX_DOSSIER_TOKENS,
    )
    decision = _gate(conn).release(model_call)
    assert isinstance(decision, Released), decision
    assert [i.value for i in decision.materialised_items] == ["[redacted]"], (
        "the release must carry the redacted value, or the probes below prove nothing")
    request = DossierRequest(
        call_site=A_FACT, subject_ref="group:subject:opaque:seed",
        eligibility_reason=REMAINS_AMBIGUOUS,
        evidence_items=(make_evidence_item(evidence_ref=key),),
        conflicts=(), model_call_request=model_call,
        plan_version=PLAN_VERSION, evidence_snapshot_id=None,
    )
    return decision, prompt, request


def _payload(released: Released, prompt: PromptDefinition, dossier: bytes):
    return build_call_payload(
        prompt, dossier,
        model_target=released.model_target,
        policy_version=released.policy_version,
        release_id=released.release_id,
        dossier_id=dossier_content_address(
            dossier, allowed_vocabulary=ALLOWED,
            allowed_schema_bytes=prompt.response_schema_bytes),
    )


def _honest_bytes(released, prompt, request) -> bytes:
    dossier = build_dossier(
        request, released, reduction_rung=REDUCTION_NONE,
        allowed_vocabulary=ALLOWED, prompt=prompt,
        handle_key=FIXTURE_HANDLE_KEY)
    return canonical_dossier_bytes(dossier, prompt, handle_key=FIXTURE_HANDLE_KEY)


def _spent(conn, release_id: str):
    row = conn.execute(
        "SELECT spent_at FROM release_ledger WHERE release_id = ?",
        (release_id,)).fetchone()
    return None if row is None else row["spent_at"]


def _issued(conn) -> list:
    return list(conn.execute(
        "SELECT event_type FROM events WHERE event_type = 'model_call_issued'"))


def _nothing_left(conn, released, recorder) -> None:
    """The four assertions every refusal owes. A check that raises after the spend,
    or after the socket, is not a check -- `00`:200: revocation cannot retract what
    has already left the device."""
    assert recorder.calls == [], "the client was handed bytes"
    assert _spent(conn, released.release_id) is None, (
        "a refused call spent the release; §6 binds BEFORE it spends so a mis-wired "
        "caller cannot burn an authorization the user granted")
    assert _issued(conn) == [], (
        "an event says a model call was issued and no model call was issued")


# ================================================================================
# The finding, run
# ================================================================================

def test_the_reviewers_probe_reaches_the_client(egress_conn):
    """CR-02 exactly as reported: a valid live release, and bytes from nowhere.

    SABOTAGE: remove `"content_digest"` from `privacy.binding.BINDING_TERMS` and
    this goes green again -- which is the run in which the complete extracted text,
    the absolute path and the content hash of every scanned file reach a provider
    under an audit record that says one `[redacted]` excerpt was released.
    """
    recorder = Recorder()
    released, prompt, _request = _released(egress_conn)
    poisoned = canonical_json({
        "complete_extracted_text": [
            {"raw_value": PRE_REDACTION,
             "context_before": TEXT[:SPAN.start],
             "context_after": TEXT[SPAN.end:]}],
        "paths": [{"current_path": PRIVATE_PATH}],
        "file_hashes": [{"content_hash": hashlib.sha256(b"x").hexdigest()}],
    }).encode("utf-8")
    payload = _payload(released, prompt, poisoned)

    with pytest.raises((BindingMismatch, ValueError)):
        issue(egress_conn, released, payload,
              model_client=ModelClient(model_target=CLOUD, invoke=recorder))
    _nothing_left(egress_conn, released, recorder)


def test_a_poisoned_sibling_key_beside_a_faithful_evidence_list(egress_conn):
    """The variant a digest over `released_evidence` alone would have let through.

    Every released entry is exactly what the gate released. The always-local material
    rides in a key beside it. A check that digests only the entries it recognises is
    a check that ignores everything it does not.
    """
    recorder = Recorder()
    released, prompt, request = _released(egress_conn)
    body = json.loads(_honest_bytes(released, prompt, request))
    body["paths"] = [{"current_path": PRIVATE_PATH}]
    payload = _payload(released, prompt, canonical_json(body).encode("utf-8"))

    with pytest.raises((BindingMismatch, ValueError)):
        issue(egress_conn, released, payload,
              model_client=ModelClient(model_target=CLOUD, invoke=recorder))
    _nothing_left(egress_conn, released, recorder)


def test_a_smuggled_field_inside_a_released_entry(egress_conn):
    """The second variant: the entry's four keys are all correct, and it carries a
    fifth. `_released_body`'s docstring says the context was removed because §8.4
    keeps complete extracted text local; it was removed from the RELEASE."""
    recorder = Recorder()
    released, prompt, request = _released(egress_conn)
    body = json.loads(_honest_bytes(released, prompt, request))
    body["released_evidence"][0]["context_before"] = TEXT[:SPAN.start]
    payload = _payload(released, prompt, canonical_json(body).encode("utf-8"))

    with pytest.raises((BindingMismatch, ValueError)):
        issue(egress_conn, released, payload,
              model_client=ModelClient(model_target=CLOUD, invoke=recorder))
    _nothing_left(egress_conn, released, recorder)


def test_the_pre_redaction_value_cannot_be_substituted_for_the_released_one(egress_conn):
    """The shape the whole part exists to stop: the redaction is undone in the bytes
    while the audit record still says `redaction_applied`."""
    recorder = Recorder()
    released, prompt, request = _released(egress_conn)
    body = json.loads(_honest_bytes(released, prompt, request))
    assert body["released_evidence"][0]["value"] == "[redacted]"
    body["released_evidence"][0]["value"] = PRE_REDACTION
    payload = _payload(released, prompt, canonical_json(body).encode("utf-8"))

    with pytest.raises((BindingMismatch, ValueError)):
        issue(egress_conn, released, payload,
              model_client=ModelClient(model_target=CLOUD, invoke=recorder))
    _nothing_left(egress_conn, released, recorder)


def test_a_relabelled_release_cannot_authorize_its_own_content(egress_conn):
    """`Released` is an ordinary frozen dataclass, so `dataclasses.replace` mints a
    copy with different `materialised_items` and the same, real, `release_id`.

    This is why the digest is a LEDGER term and not a field on `Released`: the ledger
    row was written by the gate and the caller cannot reach it. A check that compared
    the bytes against the object in the caller's hand would compare a forgery with
    itself.
    """
    recorder = Recorder()
    released, prompt, request = _released(egress_conn)
    body = json.loads(_honest_bytes(released, prompt, request))
    body["released_evidence"][0]["value"] = PRE_REDACTION
    relabelled = replace(released, materialised_items=tuple(
        replace(item, value=PRE_REDACTION) for item in released.materialised_items))
    payload = _payload(released, prompt, canonical_json(body).encode("utf-8"))

    with pytest.raises(BindingMismatch):
        issue(egress_conn, relabelled, payload,
              model_client=ModelClient(model_target=CLOUD, invoke=recorder))
    _nothing_left(egress_conn, released, recorder)


# ================================================================================
# The control. The honest call still goes through.
# ================================================================================

def test_the_dossier_the_builder_produced_is_accepted_and_sent_once(egress_conn):
    """The door closes on forged bytes and stays open for the real ones.

    Without this the four refusals above are also satisfied by a transport that
    refuses everything, which would be a privacy property no product could ship.
    """
    recorder = Recorder()
    released, prompt, request = _released(egress_conn)
    honest = _honest_bytes(released, prompt, request)
    payload = _payload(released, prompt, honest)

    result = issue(egress_conn, released, payload,
                   model_client=ModelClient(model_target=CLOUD, invoke=recorder))
    assert isinstance(result, ModelResponse)
    assert recorder.calls == [payload.model_visible_bytes]
    assert _spent(egress_conn, released.release_id) is not None
    assert len(_issued(egress_conn)) == 1
    assert PRE_REDACTION.encode() not in recorder.calls[0]
    assert PRIVATE_PATH.encode() not in recorder.calls[0]


# ================================================================================
# The residual: the slots that were bound in SHAPE and not in CONTENT
# ================================================================================
#
# The first pass bound `released_evidence` and stated, at
# `llm_harness/released_content.py`, that the builder-authored slots were bound in
# shape only. The re-verification took that statement and ran it: a body with exactly
# `DOSSIER_BODY_KEYS`, a faithful `released_evidence` list folding to the ledger's
# digest, and the corpus in the other slots -- and `issue` returned `ModelResponse`
# with `current_path` in the bytes handed to the client.
#
# Each test below is one of those slots. What is bound is bound against something the
# TRANSPORT legitimately holds -- the `PromptDefinition` in its own payload, the
# closed vocabularies P8 already publishes, the keying `_body` applies to every
# identifier it writes -- and never against a guess.


def _poison(released, prompt, request, mutate) -> bytes:
    body = json.loads(_honest_bytes(released, prompt, request))
    mutate(body)
    return canonical_json(body).encode("utf-8")


def _refused(conn, released, prompt, body: bytes, recorder) -> None:
    payload = _payload(released, prompt, body)
    with pytest.raises((BindingMismatch, ValueError)):
        issue(conn, released, payload,
              model_client=ModelClient(model_target=CLOUD, invoke=recorder))
    _nothing_left(conn, released, recorder)


def test_the_reverifications_well_shaped_forgery(egress_conn):
    """The re-verification's probe, whole: every key correct, the corpus in the
    slots that were bound in shape only. It returned `ModelResponse`."""
    recorder = Recorder()
    released, prompt, request = _released(egress_conn)

    def mutate(body):
        body["subject_ref"] = PRIVATE_PATH
        body["evidence_items"] = [{"anything": PRIVATE_PATH, "at_all": PRE_REDACTION}]
        body["conflicts"] = [{"conflict_id": PRIVATE_PATH, "kind": PRE_REDACTION}]
        body["field_glossary"] = {"x": PRIVATE_PATH}
        body["response_schema"] = PRIVATE_PATH
        body["shaping_policy"] = PRE_REDACTION

    _refused(egress_conn, released, prompt,
             _poison(released, prompt, request, mutate), recorder)


def test_an_evidence_item_entry_gets_the_same_key_set_check(egress_conn):
    """The omission the reviewer said to fix first: `released_evidence` entries were
    key-set checked and `evidence_items` entries, one function away, were not. Keys
    `anything` and `at_all` passed."""
    recorder = Recorder()
    released, prompt, request = _released(egress_conn)
    _refused(egress_conn, released, prompt, _poison(
        released, prompt, request,
        lambda b: b.__setitem__("evidence_items",
                                [{"anything": PRIVATE_PATH, "at_all": "x"}])),
        recorder)


def test_a_smuggled_field_beside_an_honest_evidence_item(egress_conn):
    recorder = Recorder()
    released, prompt, request = _released(egress_conn)

    def mutate(body):
        body["evidence_items"][0]["context_before"] = TEXT[:SPAN.start]

    _refused(egress_conn, released, prompt,
             _poison(released, prompt, request, mutate), recorder)


def test_the_two_authored_documents_must_be_the_ones_the_prompt_carries(egress_conn):
    """`response_schema` and `shaping_policy` are the injected authorities `_as_text`
    decodes out of the `PromptDefinition`. The transport holds that definition, so
    these are bound by EQUALITY and not by shape."""
    recorder = Recorder()
    released, prompt, request = _released(egress_conn)
    for slot in ("response_schema", "shaping_policy"):
        _refused(egress_conn, released, prompt, _poison(
            released, prompt, request,
            lambda b, s=slot: b.__setitem__(s, PRIVATE_PATH)), recorder)


def test_the_glossary_must_be_the_one_the_vocabulary_produces(egress_conn):
    """`field_glossary` is built from `allowed_vocabulary` and nothing else -- its own
    comment calls it "the one key here whose content is the same on every file in
    every corpus". So the door recomputes it rather than trusting it."""
    recorder = Recorder()
    released, prompt, request = _released(egress_conn)
    _refused(egress_conn, released, prompt, _poison(
        released, prompt, request,
        lambda b: b.__setitem__("field_glossary", {"subject": PRIVATE_PATH})),
        recorder)


def test_every_identifier_the_builder_keys_must_arrive_keyed(egress_conn):
    """`_body` runs `wire_handle` over `subject_ref` and every `conflict_id`, so an
    unkeyed string in either is a value that did not come through the builder."""
    recorder = Recorder()
    released, prompt, request = _released(egress_conn)
    _refused(egress_conn, released, prompt, _poison(
        released, prompt, request,
        lambda b: b.__setitem__("subject_ref", PRIVATE_PATH)), recorder)
    _refused(egress_conn, released, prompt, _poison(
        released, prompt, request,
        lambda b: b.__setitem__(
            "conflicts", [{"conflict_id": PRIVATE_PATH, "kind": "duplicate"}])),
        recorder)


def test_the_closed_vocabularies_are_checked_at_the_door_too(egress_conn):
    """`call_site`, `eligibility_reason`, `reduction_rung`, and an evidence item's
    `basis` and `reliability_state` are all closed vocabularies P8 already publishes.
    A door that let a free string sit in one of them would be trusting the builder to
    have validated what the builder is the thing being checked."""
    recorder = Recorder()
    released, prompt, request = _released(egress_conn)
    for slot in ("call_site", "eligibility_reason", "reduction_rung"):
        _refused(egress_conn, released, prompt, _poison(
            released, prompt, request,
            lambda b, s=slot: b.__setitem__(s, PRIVATE_PATH)), recorder)

    def basis(body):
        body["evidence_items"][0]["basis"] = PRIVATE_PATH

    _refused(egress_conn, released, prompt,
             _poison(released, prompt, request, basis), recorder)


def test_what_is_still_not_bound_is_named_and_nothing_else_is(egress_conn):
    """The residual, asserted rather than promised.

    These three slots reach the model as free caller-chosen text and this test says
    so out loud. `location` and both `kind`s are free strings with no vocabulary in
    `records.py` to check them against; `allowed_vocabulary` is the caller's declared
    answer vocabulary and is legitimately arbitrary -- P9's is group labels, P10's is
    node ids, P11's is residual actions, none of them field names.

    If a later change binds one, this test goes red and must be narrowed. That is the
    point: the residual is a list somebody maintains, not a sentence somebody wrote.
    """
    recorder = Recorder()
    released, prompt, request = _released(egress_conn)
    still_free = []
    for mutate, name in (
        (lambda b: b["evidence_items"][0].__setitem__("location", PRIVATE_PATH),
         "evidence_items[].location"),
        (lambda b: b["evidence_items"][0].__setitem__("kind", PRIVATE_PATH),
         "evidence_items[].kind"),
        (lambda b: b.__setitem__("allowed_vocabulary", [PRIVATE_PATH]),
         "allowed_vocabulary"),
    ):
        payload = _payload(released, prompt,
                           _poison(released, prompt, request, mutate))
        try:
            issue(egress_conn, released, payload,
                  model_client=ModelClient(model_target=CLOUD, invoke=recorder))
        except Exception:
            continue
        still_free.append(name)
        break   # the release is spent; one probe per release

    assert still_free == ["evidence_items[].location"], (
        f"the residual changed: {still_free}. Update this test AND the module "
        "docstring at `llm_harness/released_content.py` together, or one of them "
        "starts lying to the next reviewer")


# ================================================================================
# The drift guards. The door reads a shape two other modules write.
# ================================================================================

def test_the_door_knows_every_key_the_builder_writes(egress_conn):
    """`DOSSIER_BODY_KEYS` is a constant and `dossier._body` is its source.

    The door refuses a body carrying a key it does not recognise, so a key ADDED to
    `_body` without being added here would close the door on every honest call. That
    is the fail-closed direction and it is still a break; this is the test that says
    so at the line rather than 200 tests later.
    """
    released, prompt, request = _released(egress_conn)
    body = json.loads(_honest_bytes(released, prompt, request))
    assert set(body) == DOSSIER_BODY_KEYS


def test_the_door_folds_exactly_the_fields_the_release_binds(egress_conn):
    """`_released_body`'s four keys, and the three of them the gate folds.

    `observation_key` is the fourth and is deliberately not folded: `wire_handles`
    keys it before it is written, and the transport holds no key. The assertion is
    that it is on the wire AND outside the binding -- both halves, because either
    one alone reads as an oversight.
    """
    released, prompt, request = _released(egress_conn)
    body = json.loads(_honest_bytes(released, prompt, request))
    entry = body["released_evidence"][0]
    assert set(entry) == set(RELEASED_EVIDENCE_FIELDS)
    assert set(CONTENT_BOUND_FIELDS) == set(entry) - {"observation_key"}
    assert entry["observation_key"].startswith("handle:"), (
        "the identifier reaches the model keyed, which is why it is not folded")
    assert released_content_digest(
        _honest_bytes(released, prompt, request),
        prompt_definition=prompt,
        policy_version=released.policy_version,
    ) == content_digest_of(released.materialised_items), (
            "the gate's fold and the door's fold are the same value or the term "
            "binds nothing")
