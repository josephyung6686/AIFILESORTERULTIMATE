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
    CommandResult as ClaudeResult,
    classify_argv,
    run_prompt,
)
from readers.model_keychain import (
    OPENAI_API_KEY,
    SIWC_ACCESS,
    SIWC_HOST,
    SIWC_REFRESH,
    SIWC_REGISTRATION,
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
    JWKS_URI,
    PLAN_SCOPE,
    REAUTH_MESSAGE,
    accept_token_response,
    authorize_request,
    begin_or_refuse,
    finish_sign_in,
    pkce_pair,
    prepare_sign_in,
    read_responses_stream,
    refresh_form,
    responses_body,
    rs256_signature_ok,
    session_action,
    token_exchange_form,
)
from readers.model_provider_cli import main as providers_main
from readers.model_provider_cli import (
    siwc_tokens_for_storage,
    understanding_from_choice,
)
from understanding.provider import CompletionRequest


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


#: Signed with a throwaway RSA key. The private key is not in this tree.
#: Payload: iss https://auth.openai.com, aud oaiapp_issued, nonce n,
#: exp 9999999999, sub user-1. kid test-key, alg RS256.
_SIGNED_ID_TOKEN = (
    "eyJhbGciOiJSUzI1NiIsImtpZCI6InRlc3Qta2V5IiwidHlwIjoiSldUIn0."
    "eyJpc3MiOiJodHRwczovL2F1dGgub3BlbmFpLmNvbSIsImF1ZCI6Im9haWFwcF9pc3N1ZWQi"
    "LCJub25jZSI6Im4iLCJleHAiOjk5OTk5OTk5OTksInN1YiI6InVzZXItMSJ9."
    "NVy4F-h71fx_E1mDgNJTNPkqClKvdFJ8_8yuHyneJlqhDmrncc6XDDEl3MVRjjw6gnPFZawEi"
    "j9kwfIkGX6GQHUol_dQK1QRWiO1gKQwmN4kC9qNCNC59oY44YABC5bGjvmon1LBKMbJJDeB9l"
    "20kJp9vKXlIjnLbdqqpbpxy5be1fnSH2K_nb0BzCv8ODlj03IX3-_07fc0-gi3JriV48mxpHN"
    "L61Lf-W5r1BJ-C_ry_4UfSg2KaGZQ8Daxnx_Wk7hPd0SSWs1wcBYBkXiCmdHr5KdRviNSE2UP"
    "o78QqtZKb-Am_3qSQtjRz0TfqU1YAVLb_NDD4R6jZxuFgVfbIg"
)
_JWKS = {"keys": [{
    "kty": "RSA",
    "kid": "test-key",
    "alg": "RS256",
    "n": (
        "vnhQdlwqVCxClit2tmHBAfx_rVfDJ8aSEEd_tFgNXwgdszAq-KWmW2BDQIO8i9qu9ZTAF"
        "MbjU4uBuLfRFWyAvJSK93NAIMEPLCMiudyDWptfPBX_7pa9w6U6I0wqWfA3lDJAUQV_2-"
        "kCFkyFrviMHNKye3I-QAxK1FY_oYlTiQCR5MjIti--aEtNh8qopjzJm924fzog6LtIgg9"
        "O4m-0-YPsln7Oc6kuxXnCP2bt040LUt5BemkEK8-nOqAyY-sOc24Rl8HCVKzR0SbGKaN3"
        "soKtbpMW5rZ6FWDj9AxhtRMVtcakJLVcHiDD_ScJRndfplawpGHrnE3XP7ERJjpsTQ"
    ),
    "e": "AQAB",
}]}
_ACCESS = "access-secret-siwc"


def _tampered(token: str) -> str:
    last = "A" if token[-1] != "A" else "B"
    return token[:-1] + last


def _token_response(id_token: str, *, access: str = _ACCESS) -> dict:
    return {
        "client_id": "oaiapp_issued",
        "id_token": id_token,
        "access_token": access,
        "refresh_token": "refresh-secret",
        "expires_in": 3600,
        "scope": f"openid profile email offline_access resource.invoke {PLAN_SCOPE}",
    }


def test_rs256_accepts_the_fixture_and_a_tampered_signature_is_not_stored():
    assert rs256_signature_ok(_SIGNED_ID_TOKEN, _JWKS) is True
    tampered = _tampered(_SIGNED_ID_TOKEN)
    assert rs256_signature_ok(tampered, _JWKS) is False
    attempt = prepare_sign_in(
        host_id="urn:uuid:host", port=1455, nonce="n", state="state-1")

    def post_form(_url, form):
        assert form["client_id"] == "oaiapp_issued"
        assert form["client_id"] != DYNAMIC_CLIENT
        return _token_response(tampered)

    with pytest.raises(Exception) as raised:
        finish_sign_in(
            attempt, {"code": "auth-code", "state": "state-1",
                      "client_id": "oaiapp_issued"},
            post_form=post_form, jwks=_JWKS, now=1_700_000_000)
    assert _ACCESS not in str(raised.value)
    assert "refresh-secret" not in str(raised.value)
    assert JWKS_URI in str(raised.value)
    assert "Tokens were not stored" in str(raised.value)
    session = finish_sign_in(
        attempt, {"code": "auth-code", "state": "state-1",
                  "client_id": "oaiapp_issued"},
        post_form=lambda _url, _form: _token_response(_SIGNED_ID_TOKEN),
        jwks=_JWKS, now=1_700_000_000)
    assert session.inference_ready is True
    assert session.id_token == _SIGNED_ID_TOKEN
    stored = siwc_tokens_for_storage(session, model="user-model")
    assert stored[SIWC_ACCESS] == _ACCESS
    registration = stored[SIWC_REGISTRATION]
    assert _ACCESS not in registration
    assert "user-model" in registration
    assert _SIGNED_ID_TOKEN in registration


def test_flag_off_sign_in_does_not_open_a_database(tmp_path, monkeypatch):
    monkeypatch.delenv("FILESORTER_OPENAI_SIWC", raising=False)
    monkeypatch.chdir(tmp_path)
    out = io.StringIO()
    assert providers_main(["sign-in-chatgpt"], out=out) == 2
    assert "FILESORTER_OPENAI_SIWC" in out.getvalue()
    assert list(tmp_path.iterdir()) == []


def test_flag_on_sign_in_stores_the_keychain_and_does_not_print_the_token(
        tmp_path, monkeypatch):
    monkeypatch.setenv("FILESORTER_OPENAI_SIWC", "1")
    database = tmp_path / "plan.sqlite"
    memory = MemoryKeychain()
    opened = []

    def wait(url):
        opened.append(url)
        return {"code": "auth-code", "state": "state-1", "client_id": "oaiapp_issued"}

    def post_form(_url, form):
        assert form["client_id"] == "oaiapp_issued"
        return _token_response(_SIGNED_ID_TOKEN)

    out = io.StringIO()
    code = providers_main(
        ["--database", str(database), "sign-in-chatgpt", "--model", "user-model"],
        out=out, keychain_run=memory, siwc_post=post_form, siwc_jwks=_JWKS,
        siwc_wait=wait, siwc_now=1_700_000_000, siwc_nonce="n",
        siwc_state="state-1")
    printed = out.getvalue()
    assert code == 0, printed
    assert _ACCESS not in printed
    assert "refresh-secret" not in printed
    assert memory.items[SIWC_ACCESS] == _ACCESS
    assert _ACCESS not in memory.items[SIWC_REGISTRATION]
    registration = json.loads(memory.items[SIWC_REGISTRATION])
    assert registration["issued_client_id"] == "oaiapp_issued"
    assert registration["model"] == "user-model"
    assert registration["id_token"] == _SIGNED_ID_TOKEN
    assert memory.items[SIWC_HOST].startswith("urn:uuid:")
    assert opened and "dynamic_agent_client" in opened[0]
    assert "127.0.0.1" in opened[0]
    from database_agent.db import open_database
    from providers.record import load_provider_choice
    conn = open_database(database, scan_roots=[])
    try:
        choice = load_provider_choice(conn)
    finally:
        conn.close()
    assert choice["lane"] == "subscription"
    assert choice["provider"] == "openai"
    assert choice["credential"] == "keychain"
    assert choice["model"] == "user-model"


def test_a_bad_signature_on_the_command_stores_nothing(tmp_path, monkeypatch):
    monkeypatch.setenv("FILESORTER_OPENAI_SIWC", "1")
    memory = MemoryKeychain()
    out = io.StringIO()
    code = providers_main(
        ["--database", str(tmp_path / "plan.sqlite"), "sign-in-chatgpt"],
        out=out, keychain_run=memory,
        siwc_post=lambda _url, _form: _token_response(_tampered(_SIGNED_ID_TOKEN)),
        siwc_jwks=_JWKS,
        siwc_wait=lambda _url: {
            "code": "auth-code", "state": "state-1", "client_id": "oaiapp_issued"},
        siwc_now=1_700_000_000, siwc_nonce="n", siwc_state="state-1")
    assert code == 2
    assert _ACCESS not in out.getvalue()
    assert SIWC_ACCESS not in memory.items
    assert JWKS_URI in out.getvalue()


def test_claude_code_is_stored_without_a_credential_and_the_binary_is_unmodified(
        tmp_path, monkeypatch):
    database = str(tmp_path / "plan.sqlite")
    out = io.StringIO()
    code = providers_main(
        ["--database", database, "use", "byok", "claude-code"],
        out=out, keychain_run=MemoryKeychain())
    printed = out.getvalue()
    assert code == 0, printed
    assert "Sign in inside Claude Code" in printed
    stored = json.loads(printed.strip().splitlines()[-1])
    assert stored["provider"] == "claude-code"
    assert stored["credential"] == "none"
    assert stored["lane"] == "byok"
    refused = io.StringIO()
    assert providers_main(
        ["--database", database, "use", "subscription", "claude-code"],
        out=refused, keychain_run=MemoryKeychain()) == 2
    assert "Anthropic policy" in refused.getvalue()
    calls = []

    def run(argv):
        calls.append(tuple(argv))
        return ClaudeResult(0, '{"ok":true}', "sk-token-in-stderr")

    monkeypatch.setenv("FILESORTER_CLAUDE_CODE", "1")
    decided = understanding_from_choice(
        {"lane": "byok", "provider": "claude-code", "credential": "none"},
        out=io.StringIO(),
        env_lookup=lambda _name: "deepseek-secret",
        which_claude=lambda name: "/usr/bin/claude" if name == "claude" else None,
        claude_run=run)
    adapter, model = decided
    assert model == "claude"
    assert adapter.locality() == "cloud"
    payload = adapter.complete(CompletionRequest(
        model_id="claude", prompt="classify this", max_tokens=16))
    assert calls == [("/usr/bin/claude", "-p", "classify this")]
    assert "sk-token-in-stderr" not in json.dumps(payload)
    monkeypatch.delenv("FILESORTER_CLAUDE_CODE", raising=False)
    blocked = io.StringIO()
    assert understanding_from_choice(
        {"lane": "byok", "provider": "claude-code", "credential": "none"},
        out=blocked, env_lookup=lambda _name: "deepseek-secret") == (None, "")
    assert "deepseek-secret" not in blocked.getvalue()
    assert "Sign in inside Claude Code" in blocked.getvalue()


def _session_keychain(*, access="old-access", expires_at=9_999_999_999,
                      inference_ready=True, model="user-model"):
    memory = MemoryKeychain()
    add_secret(SIWC_ACCESS, access, run=memory)
    add_secret(SIWC_REFRESH, "refresh-secret", run=memory)
    add_secret(SIWC_REGISTRATION, json.dumps({
        "issued_client_id": "oaiapp_issued",
        "host_id": "urn:uuid:host",
        "expires_at": expires_at,
        "scopes": ["openid", PLAN_SCOPE],
        "inference_ready": inference_ready,
        "subject": "user-1",
        "model": model,
    }), run=memory)
    return memory


def test_a_ready_chatgpt_session_uses_responses_and_not_deepseek(monkeypatch):
    import cli
    monkeypatch.setenv("FILESORTER_OPENAI_SIWC", "1")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-secret")
    memory = _session_keychain(access=_ACCESS)
    seen = {}

    def post(url, headers, body):
        seen["url"] = url
        seen["auth"] = headers["Authorization"]
        seen["body"] = body
        return {"events": [
            'data: {"type":"response.output_text.delta","delta":"ok"}',
            'data: {"type":"response.completed"}',
        ]}

    out = io.StringIO()
    routing = cli.model_route(
        out=out, discover=lambda _endpoint: (), keychain_run=memory,
        siwc_post=post, siwc_now=1_700_000_000,
        provider_choice={"lane": "subscription", "provider": "openai",
                         "credential": "keychain"})
    assert routing is not None
    assert "deepseek-secret" not in out.getvalue()
    site = next(iter(cli.TIER_OF_CALL_SITE))
    assert routing.client_for(site).invoke(b"hello") == b"ok"
    assert seen["url"].endswith("/responses")
    assert seen["body"]["store"] is False
    assert seen["body"]["stream"] is True
    assert seen["body"]["input"][0]["role"] == "user"
    assert seen["auth"] == "Bearer " + _ACCESS
    assert "deepseek" not in seen["url"]


def test_flagged_chatgpt_without_a_session_does_not_fall_through(monkeypatch):
    import cli
    monkeypatch.setenv("FILESORTER_OPENAI_SIWC", "1")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-secret")
    out = io.StringIO()
    routing = cli.model_route(
        out=out, discover=lambda _endpoint: (), keychain_run=MemoryKeychain(),
        provider_choice={"lane": "subscription", "provider": "openai"})
    assert routing is None
    text = out.getvalue()
    assert "deepseek-secret" not in text
    assert "sign-in-chatgpt" in text


def test_an_expired_chatgpt_token_is_refreshed_or_not_sent(monkeypatch):
    import cli
    monkeypatch.setenv("FILESORTER_OPENAI_SIWC", "1")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-secret")
    memory = _session_keychain(access="old-access", expires_at=10)
    sent = {}

    def post_form(_url, form):
        assert form["grant_type"] == "refresh_token"
        assert "scope" not in form
        assert form["refresh_token"] == "refresh-secret"
        return _token_response(_SIGNED_ID_TOKEN, access="new-access")

    def post(url, headers, body):
        sent["auth"] = headers["Authorization"]
        sent["body"] = body
        return {"events": [
            'data: {"type":"response.output_text.delta","delta":"ok"}',
            'data: {"type":"response.completed"}',
        ]}

    out = io.StringIO()
    routing = cli.model_route(
        out=out, discover=lambda _endpoint: (), keychain_run=memory,
        siwc_post=post, siwc_post_form=post_form, siwc_jwks=_JWKS,
        siwc_now=11,
        provider_choice={"lane": "subscription", "provider": "openai"})
    assert routing is not None, out.getvalue()
    site = next(iter(cli.TIER_OF_CALL_SITE))
    assert routing.client_for(site).invoke(b"hello") == b"ok"
    assert sent["auth"] == "Bearer new-access"
    assert "old-access" not in out.getvalue()
    assert memory.items[SIWC_ACCESS] == "new-access"

    refused = _session_keychain(access="old-access", expires_at=10)

    def fail(_url, _form):
        raise RuntimeError("old-access must not be printed")

    out = io.StringIO()
    called = []
    routing = cli.model_route(
        out=out, discover=lambda _endpoint: (), keychain_run=refused,
        siwc_post=lambda *args: called.append(args),
        siwc_post_form=fail, siwc_jwks=_JWKS, siwc_now=11,
        provider_choice={"lane": "subscription", "provider": "openai"})
    assert routing is None
    assert called == []
    assert "old-access" not in out.getvalue()
    assert "Reauthenticate" in out.getvalue()
    assert refused.items[SIWC_ACCESS] == "old-access"


def test_understanding_follows_the_stored_lane(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-secret")
    monkeypatch.setenv("FILESORTER_OPENAI_SIWC", "1")
    out = io.StringIO()
    assert understanding_from_choice(
        {"lane": "subscription", "provider": "openai", "credential": "keychain"},
        out=out, env_lookup=lambda name: "deepseek-secret" if "DEEPSEEK" in name else "",
        keychain_run=MemoryKeychain()) == (None, "")
    assert "deepseek-secret" not in out.getvalue()
    assert "sign-in-chatgpt" in out.getvalue()

    memory = _session_keychain(access=_ACCESS)
    seen = {}

    def siwc_post(url, headers, body):
        seen["siwc_url"] = url
        seen["store"] = body["store"]
        return {"events": [
            'data: {"type":"response.output_text.delta","delta":"{\\"kind\\":\\"note\\"}"}',
            'data: {"type":"response.completed"}',
        ]}

    adapter, model = understanding_from_choice(
        {"lane": "subscription", "provider": "openai", "credential": "keychain"},
        out=io.StringIO(), keychain_run=memory, siwc_post=siwc_post,
        siwc_now=1_700_000_000,
        env_lookup=lambda _name: "deepseek-secret")
    assert model == "user-model"
    assert adapter.provider_name() == "openai-siwc"
    payload = adapter.complete(CompletionRequest(
        model_id=model, prompt="Reply with json", max_tokens=32))
    assert seen["siwc_url"].endswith("/responses")
    assert seen["store"] is False
    assert "kind" in payload["choices"][0]["message"]["content"]

    def anthropic_post(url, headers, body):
        seen["anthropic_url"] = url
        seen["anthropic_key"] = headers["x-api-key"]
        seen["anthropic_body"] = body
        return {"stop_reason": "end_turn",
                "content": [{"type": "text", "text": "{\"ok\": true}"}]}

    adapter, model = understanding_from_choice(
        {"lane": "byok", "provider": "anthropic", "credential": "env",
         "model": "user-model"},
        out=io.StringIO(), http_post=anthropic_post,
        env_lookup=lambda name: "anthropic-key" if name == "ANTHROPIC_API_KEY" else "")
    assert model == "user-model"
    assert adapter.provider_name() == "anthropic"
    payload = adapter.complete(CompletionRequest(
        model_id=model, prompt="Reply with one JSON object.", max_tokens=16))
    assert seen["anthropic_url"].endswith("/messages")
    assert seen["anthropic_key"] == "anthropic-key"
    assert "response_format" not in seen["anthropic_body"]
    assert "anthropic-key" not in json.dumps(payload)

    def openai_post(url, headers, body):
        seen["openai_url"] = url
        seen["openai_auth"] = headers["Authorization"]
        seen["openai_body"] = body
        return {"choices": [{"finish_reason": "stop",
                             "message": {"content": "{\"ok\": true}"}}]}

    keychain = MemoryKeychain()
    add_secret(OPENAI_API_KEY, "openai-key", run=keychain)
    adapter, model = understanding_from_choice(
        {"lane": "byok", "provider": "openai", "credential": "keychain",
         "model": "user-model"},
        out=io.StringIO(), http_post=openai_post, keychain_run=keychain,
        env_lookup=lambda _name: "")
    payload = adapter.complete(CompletionRequest(
        model_id=model, prompt='Reply with one JSON object {"ok": true}',
        max_tokens=16))
    assert seen["openai_url"].endswith("/chat/completions")
    assert seen["openai_body"]["response_format"]["type"] == "json_object"
    assert seen["openai_auth"] == "Bearer openai-key"
    assert "openai-key" not in json.dumps(payload)
    assert adapter.provider_name() == "openai"
