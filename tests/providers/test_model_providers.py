# tests/providers/test_model_providers.py
"""The three provider lanes: keychain, request shapes, and the flags that stay off."""
from __future__ import annotations

import hashlib
import base64
import io
import json

import pytest

from privacy.release import ModelTarget
from readers.model_anthropic import (
    ANTHROPIC_VERSION,
    messages_body,
    messages_headers,
    messages_text,
    anthropic_http_invoke,
)
from readers.model_claude_code import (
    POLICY,
    classify_argv,
    run_prompt,
)
from readers.model_keychain import (
    OPENAI_API_KEY,
    SIWC_ACCESS,
    CommandResult,
    KeychainError,
    add_secret,
    delete_secret,
    find_secret,
)
from readers.model_openai import (
    chat_body,
    chat_headers,
    chat_text,
    chat_url,
    openai_invoke,
)
from readers.model_siwc import (
    DYNAMIC_CLIENT,
    FLAG_OFF_MESSAGE,
    PLAN_SCOPE,
    REAUTH_MESSAGE,
    accept_token_response,
    authorize_request,
    begin_or_refuse,
    pkce_pair,
    read_responses_stream,
    refresh_form,
    responses_body,
    session_action,
    token_exchange_form,
)
from readers.model_provider_cli import main as providers_main
from readers.model_provider_cli import siwc_tokens_for_storage


SECRET = "sk-test-do-not-print"


class MemoryKeychain:
    def __init__(self):
        self.items: dict[str, str] = {}

    def __call__(self, argv):
        argv = list(argv)
        account = argv[argv.index("-a") + 1]
        if argv[1] == "add-generic-password":
            self.items[account] = argv[argv.index("-w") + 1]
            return CommandResult(0)
        if argv[1] == "find-generic-password":
            if account not in self.items:
                return CommandResult(44, "", "not found")
            return CommandResult(0, self.items[account] + "\n")
        if argv[1] == "delete-generic-password":
            self.items.pop(account, None)
            return CommandResult(0 if account or True else 44)
        return CommandResult(1, "", "unexpected")


def test_keychain_round_trip_never_names_the_secret_in_an_error():
    memory = MemoryKeychain()
    add_secret(OPENAI_API_KEY, SECRET, run=memory)
    assert find_secret(OPENAI_API_KEY, run=memory) == SECRET
    assert delete_secret(OPENAI_API_KEY, run=memory) is True
    assert find_secret(OPENAI_API_KEY, run=memory) is None
    add_secret(OPENAI_API_KEY, SECRET, run=memory)
    memory.items.clear()

    def boom(_argv):
        return CommandResult(1, "", SECRET)

    with pytest.raises(KeychainError) as raised:
        add_secret(OPENAI_API_KEY, SECRET, run=boom)
    assert SECRET not in str(raised.value)


def test_pkce_is_s256_without_padding():
    verifier, challenge = pkce_pair(random_bytes=b"k" * 32)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    expect = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    assert challenge == expect
    assert "=" not in challenge
    assert 43 <= len(verifier) <= 128


def test_refresh_uses_the_issued_client_and_omits_scope():
    form = refresh_form(client_id="oaiapp_issued", refresh_token="refresh-1")
    assert form["grant_type"] == "refresh_token"
    assert form["client_id"] == "oaiapp_issued"
    assert "scope" not in form
    assert form["resource"] == "https://api.openai.com/v1"
    with pytest.raises(Exception):
        refresh_form(client_id=DYNAMIC_CLIENT, refresh_token="refresh-1")


def test_flag_off_refuses_and_points_at_the_quickstart():
    assert begin_or_refuse({}) == FLAG_OFF_MESSAGE
    assert "FILESORTER_OPENAI_SIWC=1" in FLAG_OFF_MESSAGE
    assert "https://developers.openai.com/siwc/quickstart" in FLAG_OFF_MESSAGE
    assert begin_or_refuse({"FILESORTER_OPENAI_SIWC": "1"}) is None


def test_expired_refresh_failure_asks_to_reauthenticate():
    assert session_action(expires_at=10, now=11, refresh_failed=True) == "reauthenticate"
    assert session_action(expires_at=10, now=11, refresh_failed=False) == "refresh"
    assert "Reauthenticate" in REAUTH_MESSAGE


def test_unverified_id_token_is_not_stored_and_the_token_is_not_in_the_error():
    response = {
        "client_id": "oaiapp_issued",
        "id_token": _token({"iss": "https://auth.openai.com", "aud": "oaiapp_issued",
                            "nonce": "n", "exp": 9_999_999_999, "sub": "user-1"}),
        "access_token": "access-secret",
        "refresh_token": "refresh-secret",
        "expires_in": 3600,
        "scope": f"openid {PLAN_SCOPE}",
    }
    with pytest.raises(Exception) as raised:
        accept_token_response(
            response, nonce="n", now=1_700_000_000, host_id="urn:uuid:host",
            signature_ok=False)
    assert "access-secret" not in str(raised.value)
    assert "refresh-secret" not in str(raised.value)
    session = accept_token_response(
        response, nonce="n", now=1_700_000_000, host_id="urn:uuid:host",
        signature_ok=True)
    assert session.inference_ready is True
    stored = siwc_tokens_for_storage(session)
    assert stored[SIWC_ACCESS] == "access-secret"
    assert "access-secret" not in stored["openai-siwc-registration"]


def test_authorize_request_uses_the_dynamic_client_only_for_the_first_sign_in():
    verifier, challenge = pkce_pair(random_bytes=b"k" * 32)
    first = authorize_request(
        host_id="urn:uuid:host", redirect="http://127.0.0.1:1455/auth/callback",
        state="state", nonce="nonce", code_challenge=challenge)
    assert first["client_id"] == DYNAMIC_CLIENT
    assert first["agent_name_hint"] == "filesorter"
    assert "localhost" not in first["redirect_uri"]
    again = authorize_request(
        host_id="urn:uuid:host", redirect="http://127.0.0.1:1455/auth/callback",
        state="state", nonce="nonce", code_challenge=challenge,
        issued_client_id="oaiapp_issued")
    assert "agent_name_hint" not in again
    exchange = token_exchange_form(
        client_id="oaiapp_issued", code="code", verifier=verifier,
        redirect=first["redirect_uri"])
    assert exchange["client_id"] == "oaiapp_issued"
    assert exchange["code_verifier"] == verifier


def test_responses_body_stores_nothing_and_streams():
    body = responses_body(model="a-model-the-user-named", prompt="hello")
    assert body["store"] is False
    assert body["stream"] is True
    assert body["input"][0]["role"] == "user"
    text = read_responses_stream([
        'data: {"type":"response.output_text.delta","delta":"{\\"ok\\":true}"}',
        'data: {"type":"response.completed"}',
    ])
    assert "ok" in text
    with pytest.raises(Exception):
        read_responses_stream([
            'data: {"type":"response.output_text.delta","delta":"partial"}',
        ])


def test_openai_and_anthropic_request_shapes_differ():
    openai_headers = chat_headers("openai-key")
    anthropic = messages_headers("anthropic-key")
    assert openai_headers["Authorization"] == "Bearer openai-key"
    assert "x-api-key" not in openai_headers
    assert anthropic["x-api-key"] == "anthropic-key"
    assert anthropic["anthropic-version"] == ANTHROPIC_VERSION
    assert "Authorization" not in anthropic
    chat = chat_body(model_id="user-model", max_tokens=16,
                     prompt='Reply with one JSON object {"ok": true}')
    assert chat["response_format"]["type"] == "json_object"
    messages = messages_body(model_id="user-model", max_tokens=16,
                             prompt="Reply with one JSON object.")
    assert "messages" in messages
    assert "response_format" not in messages
    with pytest.raises(Exception):
        chat_url("http://example.invalid/v1")


def test_fake_transports_return_the_answer_and_drop_the_key_from_errors():
    seen = {}

    def post(url, headers, body):
        seen["url"] = url
        seen["headers"] = headers
        seen["body"] = body
        return {"choices": [{"finish_reason": "stop",
                             "message": {"content": "{\"ok\": true}"}}]}

    target = ModelTarget(locality="cloud", model_id="user-model", provider="openai")
    invoke = openai_invoke(
        api_key="openai-key", base_url="https://api.openai.com/v1",
        model_target=target, max_response_tokens=16, provider="openai", post=post)
    assert invoke(b'Reply with one JSON object {"ok": true}') == b'{"ok": true}'
    assert seen["url"].endswith("/chat/completions")
    assert seen["headers"]["Authorization"] == "Bearer openai-key"

    def anthropic_post(url, headers, body):
        seen["anthropic_url"] = url
        seen["anthropic_headers"] = headers
        return {"stop_reason": "end_turn",
                "content": [{"type": "text", "text": "{\"ok\": true}"}]}

    anthropic_target = ModelTarget(
        locality="cloud", model_id="user-model", provider="anthropic")
    anthropic_invoke = anthropic_http_invoke(
        api_key="anthropic-key", model_target=anthropic_target,
        max_response_tokens=16, post=anthropic_post)
    assert anthropic_invoke(b"Reply with one JSON object.") == b'{"ok": true}'
    assert seen["anthropic_headers"]["x-api-key"] == "anthropic-key"
    with pytest.raises(Exception) as raised:
        messages_text({"stop_reason": "max_tokens", "content": [
            {"type": "text", "text": "half"}]})
    assert "anthropic-key" not in str(raised.value)
    assert chat_text({"choices": [{"finish_reason": "stop",
                                   "message": {"content": "{\"ok\": true}"}}]}) == '{"ok": true}'


def test_claude_subscription_is_the_policy_sentence_and_the_binary_is_gated():
    assert "not available" in POLICY
    assert "Anthropic policy" in POLICY
    calls = []

    def run(argv):
        calls.append(argv)
        return type("R", (), {"returncode": 0, "stdout": "ok", "stderr": ""})()

    with pytest.raises(Exception) as raised:
        run_prompt("/usr/bin/claude", "prompt", run=run, flag_on=False)
    assert calls == []
    assert "Anthropic" in str(raised.value)
    with pytest.raises(Exception):
        classify_argv("/usr/bin/not-claude", "prompt")
    answer = run_prompt("/usr/bin/claude", "prompt", run=run, flag_on=True)
    assert answer == "ok"
    assert calls[0][1] == "-p"


def test_providers_command_lists_lanes_and_does_not_print_a_key(tmp_path):
    out = io.StringIO()
    database = str(tmp_path / "plan.sqlite")
    code = providers_main(["--database", database, "list"], out=out)
    text = out.getvalue()
    assert code == 0
    assert "coming later" in text
    assert "Anthropic policy" in text
    assert "after the profile questions" in text
    memory = MemoryKeychain()
    out = io.StringIO()
    code = providers_main(
        ["--database", database, "add", "openai", "--model", "user-model"],
        out=out, key_reader=lambda: SECRET, keychain_run=memory)
    printed = out.getvalue()
    assert code == 0
    assert SECRET not in printed
    assert memory.items[OPENAI_API_KEY] == SECRET
    out = io.StringIO()
    code = providers_main(
        ["--database", database, "dry-run", "openai", "--model", "user-model"],
        out=out, keychain_run=memory)
    dry = out.getvalue()
    assert code == 0
    assert SECRET not in dry
    assert "sent" in dry
    assert "No file was read" in dry
    assert "chat.completions" in dry
    out = io.StringIO()
    code = providers_main(
        ["--database", database, "dry-run", "anthropic", "--model", "user-model"],
        out=out, keychain_run=MemoryKeychain())
    anthropic = out.getvalue()
    assert "messages" in anthropic
    assert "No file was read" in anthropic
    assert code == 0
    out = io.StringIO()
    assert providers_main(["sign-in-chatgpt"], out=out) == 2
    assert "FILESORTER_OPENAI_SIWC" in out.getvalue()
    out = io.StringIO()
    assert providers_main(
        ["--database", database, "use", "managed", "plan"], out=out,
        keychain_run=memory) == 2
    assert "coming later" in out.getvalue()
    out = io.StringIO()
    assert providers_main(
        ["--database", database, "use", "subscription", "anthropic"], out=out,
        keychain_run=memory) == 2
    assert "Anthropic policy" in out.getvalue()
    out = io.StringIO()
    assert providers_main(
        ["session", "--expires-at", "10", "--now", "11", "--refresh-failed"],
        out=out) == 2
    assert "Reauthenticate" in out.getvalue()
    removed = io.StringIO()
    assert providers_main(
        ["--database", database, "remove", "openai"], out=removed,
        keychain_run=memory) == 0
    assert OPENAI_API_KEY not in memory.items
    assert SECRET not in removed.getvalue()


def test_a_chatgpt_choice_does_not_fall_through_to_deepseek(monkeypatch):
    import cli
    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-secret")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    monkeypatch.setenv("DEEPSEEK_MODEL_REASONING", "a-model")
    monkeypatch.setenv("DEEPSEEK_MODEL_LOGIC", "a-model")
    monkeypatch.setenv("DEEPSEEK_MODEL_FAST", "a-model")
    out = io.StringIO()
    routing = cli.model_route(
        out=out, discover=lambda _endpoint: (),
        provider_choice={"lane": "subscription", "provider": "openai"})
    assert routing is None
    text = out.getvalue()
    assert "deepseek-secret" not in text
    assert "API key" in text


def test_a_stored_openai_key_routes_without_printing_it(monkeypatch):
    import cli
    from readers.model_provider_cli import route_byok
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    memory = MemoryKeychain()
    add_secret(OPENAI_API_KEY, SECRET, run=memory)
    out = io.StringIO()
    routing = route_byok(
        {"lane": "byok", "provider": "openai", "credential": "keychain",
         "model": "user-model"},
        tier_of_call_site=cli.TIER_OF_CALL_SITE,
        max_response_tokens=16, timeout_seconds=1, out=out,
        keychain_run=memory)
    assert routing is not None
    site = next(iter(cli.TIER_OF_CALL_SITE))
    assert routing.client_for(site).model_target.provider == "openai"
    assert routing.client_for(site).model_target.model_id == "user-model"
    assert SECRET not in out.getvalue()


def test_cli_providers_is_not_a_scan(tmp_path, monkeypatch):
    import cli
    out = io.StringIO()
    monkeypatch.chdir(tmp_path)
    code = cli.main(["providers", "list"], out=out)
    assert code == 0
    assert "Managed" in out.getvalue()
    assert "Plan database" not in out.getvalue()
    assert (tmp_path / "database-agent-plan.sqlite").exists()


def _token(payload: dict) -> str:
    raw = json.dumps(payload).encode("utf-8")
    body = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    return f"aaa.{body}.sig"
