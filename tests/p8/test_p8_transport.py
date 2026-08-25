"""P8's single release-consuming model egress."""
from __future__ import annotations

import ast
import dataclasses
import inspect
import json
import pathlib
from collections.abc import Callable
from dataclasses import FrozenInstanceError

import pytest

from database_agent.db import create_schema, transaction
from evidence_shape.schema import create_evidence_schema
from llm_harness.authorship import SUBSYSTEM
from llm_harness.fingerprint import prompt_fingerprint
from llm_harness.records import (
    CallFailed,
    CallPayload,
    MalformedRecord,
    PromptDefinition,
    assemble,
    build_call_payload,
)
from llm_harness.schema import create_llm_schema
from llm_harness.transport import (
    ModelClient,
    ModelResponse,
    TransportTransactionOpen,
    issue,
)
from llm_harness.vocabulary import A_FACT
from privacy.binding import (
    BindingMismatch,
    ReleaseAlreadySpent,
    ReleaseNotIssued,
    mint_release,
)
from privacy.policy import Policy
from privacy.redaction import RedactionManifest
from privacy.release import RELEASED_FIELDS, ModelTarget, Released
from privacy.schema import create_privacy_schema

from p8.conftest import FIXED_CLOCK


HARNESS_ROOT = pathlib.Path(__file__).resolve().parents[2] / "src" / "llm_harness"
SDK_ROOTS = frozenset({
    "openai", "anthropic", "litellm", "groq", "together", "vertexai",
    "google.generativeai", "boto3",
})
LOCAL = ModelTarget(locality="local", model_id="local-small", provider="local")
CLOUD = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")
POLICY_VERSION = "policy-1"


class Recorder:
    """Deterministic injected client. Records every byte string it is given."""

    def __init__(self, reply: bytes | object = b'{"claims":[]}', *,
                 error: BaseException | None = None) -> None:
        self.calls: list[bytes] = []
        self.reply = reply
        self.error = error

    def __call__(self, blob: bytes) -> bytes:
        self.calls.append(blob)
        if self.error is not None:
            raise self.error
        if not isinstance(self.reply, (bytes, bytearray, memoryview)):
            return self.reply  # type: ignore[return-value]
        return bytes(self.reply)


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


def _policy(**over) -> Policy:
    base = dict(
        policy_version=POLICY_VERSION, operation_mode="cloud_assisted",
        consent_grants=(("Academics", "cloud_model"),),
        redaction_settings={
            "names": "redacted", "previews": "redacted", "thumbnails": "redacted",
            "ocr_text": "redacted", "location_data": "redacted",
        },
        automatic_move_permissions={}, plan_version="plan-1",
        set_at=FIXED_CLOCK,
    )
    base.update(over)
    return Policy(**base)


def _forged(**over) -> Released:
    values = {
        "release_id": "release-never-minted",
        "audit_id": 1,
        "policy_version": POLICY_VERSION,
        "materialised_items": (),
        "redaction_manifest": RedactionManifest(entries=()),
        "model_target": CLOUD,
    }
    missing = [name for name in RELEASED_FIELDS if name not in values]
    assert not missing
    values.update(over)
    return Released(**values)


def _payload(released: Released, *, dossier: bytes = b"DOSSIER",
             prompt: PromptDefinition | None = None,
             model_target: ModelTarget | None = None) -> CallPayload:
    definition = prompt or _prompt()
    return build_call_payload(
        definition,
        dossier,
        model_target=model_target or released.model_target,
        policy_version=released.policy_version,
        release_id=released.release_id,
    )


def _client(target: ModelTarget, recorder: Recorder) -> ModelClient:
    return ModelClient(model_target=target, invoke=recorder)


def _mint(conn, *, model_target=CLOUD, prompt: PromptDefinition | None = None,
          audit_id: int = 1) -> Released:
    definition = prompt or _prompt()
    digest = prompt_fingerprint(definition)
    release_id = mint_release(
        conn, policy=_policy(), model_target=model_target,
        prompt_fingerprint=digest, audit_id=audit_id, minted_at=FIXED_CLOCK,
    )
    return _forged(
        release_id=release_id, audit_id=audit_id, model_target=model_target,
        policy_version=POLICY_VERSION,
    )


def _spent(conn, release_id: str) -> str | None:
    row = conn.execute(
        "SELECT spent_at FROM release_ledger WHERE release_id = ?",
        (release_id,),
    ).fetchone()
    return None if row is None else row["spent_at"]


def _events(conn, event_type: str) -> list:
    return list(conn.execute(
        "SELECT event_type, subsystem, component_version, prompt_fingerprint, "
        "explanation FROM events WHERE event_type = ? ORDER BY event_id",
        (event_type,),
    ))


@pytest.fixture()
def transport_conn(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_privacy_schema(conn)
    create_llm_schema(conn)
    return conn


def test_model_client_is_frozen_and_target_bound():
    recorder = Recorder()
    client = _client(CLOUD, recorder)
    assert client.model_target == CLOUD
    assert isinstance(client.invoke, Callable)
    with pytest.raises(FrozenInstanceError):
        client.model_target = LOCAL  # type: ignore[misc]
    with pytest.raises((FrozenInstanceError, AttributeError)):
        client.invoke = recorder  # type: ignore[misc]


def test_issue_signature_is_the_authority_bearing_shape():
    signature = inspect.signature(issue, eval_str=True)
    assert list(signature.parameters) == ["conn", "released", "payload", "model_client"]
    assert signature.parameters["model_client"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["released"].annotation is Released
    assert signature.parameters["payload"].annotation is CallPayload
    assert signature.parameters["model_client"].annotation is ModelClient


def test_forged_released_raises_before_any_client_call(transport_conn):
    recorder = Recorder()
    released = _forged()
    payload = _payload(released)
    with pytest.raises(ReleaseNotIssued):
        issue(transport_conn, released, payload, model_client=_client(CLOUD, recorder))
    assert recorder.calls == []
    assert _events(transport_conn, "model_call_issued") == []


def test_cloud_client_with_local_payload_is_binding_mismatch(transport_conn):
    recorder = Recorder()
    prompt = _prompt()
    released = _mint(transport_conn, model_target=LOCAL, prompt=prompt)
    payload = _payload(released, prompt=prompt)
    with pytest.raises(BindingMismatch):
        issue(
            transport_conn, released, payload,
            model_client=_client(CLOUD, recorder),
        )
    assert recorder.calls == []
    assert _spent(transport_conn, released.release_id) is None
    assert _events(transport_conn, "model_call_issued") == []


def test_local_client_with_cloud_payload_is_binding_mismatch(transport_conn):
    recorder = Recorder()
    prompt = _prompt()
    released = _mint(transport_conn, model_target=CLOUD, prompt=prompt)
    payload = _payload(released, prompt=prompt)
    with pytest.raises(BindingMismatch):
        issue(
            transport_conn, released, payload,
            model_client=_client(LOCAL, recorder),
        )
    assert recorder.calls == []
    assert _spent(transport_conn, released.release_id) is None
    assert _events(transport_conn, "model_call_issued") == []


def test_second_use_raises_already_spent_and_does_not_invoke_again(transport_conn):
    recorder = Recorder()
    prompt = _prompt()
    released = _mint(transport_conn, prompt=prompt)
    payload = _payload(released, prompt=prompt)
    client = _client(CLOUD, recorder)
    first = issue(transport_conn, released, payload, model_client=client)
    assert isinstance(first, ModelResponse)
    assert len(recorder.calls) == 1
    with pytest.raises(ReleaseAlreadySpent):
        issue(transport_conn, released, payload, model_client=client)
    assert len(recorder.calls) == 1
    assert _spent(transport_conn, released.release_id) is not None


def test_consume_happens_before_the_client_is_invoked(transport_conn):
    prompt = _prompt()
    released = _mint(transport_conn, prompt=prompt)
    payload = _payload(released, prompt=prompt)
    seen: list[str | None] = []

    def invoke(blob: bytes) -> bytes:
        seen.append(_spent(transport_conn, released.release_id))
        return b'{"claims":[]}'

    result = issue(
        transport_conn, released, payload,
        model_client=ModelClient(model_target=CLOUD, invoke=invoke),
    )
    assert isinstance(result, ModelResponse)
    assert seen == [_spent(transport_conn, released.release_id)]
    assert seen[0] is not None


def test_client_receives_only_model_visible_bytes(transport_conn):
    recorder = Recorder()
    prompt = _prompt()
    released = _mint(transport_conn, prompt=prompt, audit_id=17)
    payload = _payload(released, prompt=prompt, dossier=b"VISIBLE-DOSSIER")
    issue(transport_conn, released, payload, model_client=_client(CLOUD, recorder))
    assert recorder.calls == [payload.model_visible_bytes]
    assert recorder.calls[0] == assemble(prompt, b"VISIBLE-DOSSIER")
    sent = recorder.calls[0]
    assert payload.release_id.encode() not in sent
    assert payload.policy_version.encode() not in sent
    assert payload.prompt_fingerprint.encode() not in sent
    assert b"17" not in sent
    assert CLOUD.model_id.encode() not in sent


def test_issued_and_received_events_carry_audit_id_and_fingerprint(transport_conn):
    recorder = Recorder(b'{"claims":[{"claim_ref":"c1"}]}')
    prompt = _prompt()
    released = _mint(transport_conn, prompt=prompt, audit_id=17)
    payload = _payload(released, prompt=prompt)
    result = issue(
        transport_conn, released, payload, model_client=_client(CLOUD, recorder),
    )
    assert isinstance(result, ModelResponse)
    assert result.response_bytes == b'{"claims":[{"claim_ref":"c1"}]}'
    assert result.prompt_fingerprint == payload.prompt_fingerprint
    assert result.release_audit_id == 17
    issued = _events(transport_conn, "model_call_issued")
    received = _events(transport_conn, "model_response_received")
    assert len(issued) == 1
    assert len(received) == 1
    assert issued[0]["subsystem"] == SUBSYSTEM
    assert issued[0]["prompt_fingerprint"] == payload.prompt_fingerprint
    assert received[0]["prompt_fingerprint"] == payload.prompt_fingerprint
    issued_body = json.loads(issued[0]["explanation"])
    received_body = json.loads(received[0]["explanation"])
    assert issued_body["audit_id"] == 17
    assert received_body["audit_id"] == 17
    assert issued_body["prompt_fingerprint"] == payload.prompt_fingerprint
    refused = _events(transport_conn, "call_refused")
    assert refused == []
    failures = list(transport_conn.execute("SELECT * FROM llm_call_failure"))
    assert failures == []


def test_lying_payload_fingerprint_is_refused_before_spend_or_invoke(transport_conn):
    recorder = Recorder()
    prompt = _prompt()
    released = _mint(transport_conn, prompt=prompt)
    honest = _payload(released, prompt=prompt)
    lying = CallPayload(
        prompt_definition=honest.prompt_definition,
        canonical_dossier_bytes=honest.canonical_dossier_bytes,
        model_visible_bytes=honest.model_visible_bytes,
        model_target=honest.model_target,
        prompt_fingerprint="0" * 64,
        policy_version=honest.policy_version,
        release_id=honest.release_id,
    )
    with pytest.raises(MalformedRecord):
        issue(transport_conn, released, lying, model_client=_client(CLOUD, recorder))
    assert recorder.calls == []
    assert _spent(transport_conn, released.release_id) is None
    assert _events(transport_conn, "model_call_issued") == []


def test_issue_rejects_an_already_open_transaction(transport_conn):
    recorder = Recorder()
    prompt = _prompt()
    released = _mint(transport_conn, prompt=prompt)
    payload = _payload(released, prompt=prompt)
    client = _client(CLOUD, recorder)
    with pytest.raises(TransportTransactionOpen):
        with transaction(transport_conn):
            issue(transport_conn, released, payload, model_client=client)
    assert recorder.calls == []
    assert _spent(transport_conn, released.release_id) is None
    assert _events(transport_conn, "model_call_issued") == []
    result = issue(transport_conn, released, payload, model_client=client)
    assert isinstance(result, ModelResponse)
    assert len(recorder.calls) == 1


def test_empty_client_exception_returns_call_failed(transport_conn):
    recorder = Recorder(error=RuntimeError())
    prompt = _prompt()
    released = _mint(transport_conn, prompt=prompt, audit_id=17)
    payload = _payload(released, prompt=prompt)
    result = issue(
        transport_conn, released, payload, model_client=_client(CLOUD, recorder),
    )
    assert isinstance(result, CallFailed)
    assert result.explanation
    assert "RuntimeError" in result.explanation
    assert result.release_id == released.release_id
    assert result.audit_id == 17
    assert _spent(transport_conn, released.release_id) is not None
    assert len(_events(transport_conn, "model_call_issued")) == 1
    assert _events(transport_conn, "model_response_received") == []
    assert _events(transport_conn, "call_refused") == []
    rows = list(transport_conn.execute("SELECT * FROM llm_call_failure"))
    assert len(rows) == 1
    assert rows[0]["failure_class"] == "client_raised"
    assert rows[0]["explanation"]


def test_client_raise_records_failure_and_returns_call_failed(transport_conn):
    recorder = Recorder(error=RuntimeError("provider down"))
    prompt = _prompt()
    released = _mint(transport_conn, prompt=prompt, audit_id=17)
    payload = _payload(released, prompt=prompt)
    result = issue(
        transport_conn, released, payload, model_client=_client(CLOUD, recorder),
    )
    assert isinstance(result, CallFailed)
    assert result.release_id == released.release_id
    assert result.audit_id == 17
    assert result.request_identity
    assert "provider down" in result.explanation
    assert _spent(transport_conn, released.release_id) is not None
    assert len(_events(transport_conn, "model_call_issued")) == 1
    assert _events(transport_conn, "model_response_received") == []
    assert _events(transport_conn, "call_refused") == []
    rows = list(transport_conn.execute("SELECT * FROM llm_call_failure"))
    assert len(rows) == 1
    assert rows[0]["failure_class"] == "client_raised"


def test_malformed_client_bytes_record_failure_not_a_response(transport_conn):
    recorder = Recorder(reply="not-bytes")
    prompt = _prompt()
    released = _mint(transport_conn, prompt=prompt, audit_id=4)
    payload = _payload(released, prompt=prompt)
    result = issue(
        transport_conn, released, payload, model_client=_client(CLOUD, recorder),
    )
    assert isinstance(result, CallFailed)
    assert result.audit_id == 4
    assert _events(transport_conn, "model_response_received") == []
    assert _events(transport_conn, "call_refused") == []
    rows = list(transport_conn.execute("SELECT * FROM llm_call_failure"))
    assert len(rows) == 1
    assert rows[0]["failure_class"] == "malformed_bytes"


def _enclosing_function(tree: ast.AST, node: ast.AST) -> str | None:
    function_nodes = [
        item for item in ast.walk(tree)
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    enclosing = [
        item for item in function_nodes
        if getattr(item, "end_lineno", item.lineno) is not None
        and item.lineno <= node.lineno <= (item.end_lineno or item.lineno)
    ]
    if not enclosing:
        return None
    return max(enclosing, key=lambda item: item.lineno).name


def _is_model_client_invoke(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    return (
        isinstance(func, ast.Attribute)
        and func.attr == "invoke"
        and isinstance(func.value, ast.Name)
        and func.value.id == "model_client"
    )


def test_sole_invoke_site_is_transport_issue():
    sites: list[tuple[str, str | None]] = []
    sdk_imports: list[str] = []
    aliases: list[str] = []
    for path in sorted(HARNESS_ROOT.rglob("*.py")):
        source = path.read_text()
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if _is_model_client_invoke(node):
                sites.append((path.name, _enclosing_function(tree, node)))
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".", 1)[0]
                    if root in SDK_ROOTS or alias.name in SDK_ROOTS:
                        sdk_imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".", 1)[0]
                if root in SDK_ROOTS or node.module in SDK_ROOTS:
                    sdk_imports.append(node.module)
            elif isinstance(node, ast.Assign):
                if isinstance(node.value, ast.Attribute) and node.value.attr == "invoke":
                    aliases.append(f"{path.name}: aliased invoke")
            elif isinstance(node, ast.Lambda):
                for child in ast.walk(node):
                    if _is_model_client_invoke(child) or (
                        isinstance(child, ast.Attribute) and child.attr == "invoke"
                    ):
                        aliases.append(f"{path.name}: lambda invoke")
    assert sites == [("transport.py", "issue")], sites
    assert sdk_imports == []
    assert aliases == []


def test_transport_imports_neither_evidence_readers_nor_later_parts():
    source = (HARNESS_ROOT / "transport.py").read_text()
    tree = ast.parse(source)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    for forbidden in (
        "facts", "facts.llm_seam", "eval_harness", "orchestrator", "production",
        "evidence_shape.store", "grouping",
    ):
        assert forbidden not in imported
    assert "privacy.binding" in imported
    assert "llm_harness.store" in imported
    assert "def normalize(" not in source
    assert "def contradicts(" not in source
    assert dataclasses.is_dataclass(ModelClient)
