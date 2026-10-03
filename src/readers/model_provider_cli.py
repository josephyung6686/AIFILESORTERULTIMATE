# src/readers/model_provider_cli.py
"""`database-agent providers` and `filesorter providers`.

Three lanes, in the order a person reads them:

1. Managed. Coming later. Selecting it refuses. There is no backend.
2. Subscription. OpenAI's Sign in with ChatGPT, off until the flag is set.
   Claude subscription is shown and refused: Anthropic's policy.
3. API key. DeepSeek, OpenAI, Anthropic, and an OpenAI-compatible URL.

DeepSeek stays the cloud default when `DEEPSEEK_API_KEY` is set and no other
choice is stored. Secrets go to the keychain helper or stay in the
environment. This command never prints a key.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from getpass import getpass
from pathlib import Path

from providers.record import (
    explain_order, load_provider_choice, store_provider_choice,
)
from readers.model_anthropic import (
    ENV_MODEL as ANTHROPIC_MODEL,
    MESSAGES_URL,
    messages_body,
    messages_headers,
)
from readers.model_claude_code import (
    FLAG as CLAUDE_FLAG,
    MISSING,
    POLICY,
    find_binary,
    flag_enabled as claude_flag,
    run_prompt,
)
from readers.model_keychain import (
    ANTHROPIC_API_KEY,
    COMPATIBLE_API_KEY,
    DEEPSEEK_API_KEY,
    OPENAI_API_KEY,
    SIWC_ACCESS,
    SIWC_HOST,
    SIWC_REFRESH,
    SIWC_REGISTRATION,
    KeychainError,
    add_secret,
    delete_secret,
    find_secret,
)
from readers.model_openai import (
    COMPATIBLE,
    DEFAULT_BASE_URL,
    ENV_COMPATIBLE_BASE,
    ENV_COMPATIBLE_MODEL,
    ENV_KEY as OPENAI_ENV_KEY,
    ENV_MODEL as OPENAI_MODEL,
    PROVIDER as OPENAI_PROVIDER,
    chat_body,
    chat_headers,
    describe_request,
)
from readers.model_siwc import (
    FLAG as SIWC_FLAG,
    REAUTH_MESSAGE,
    begin_or_refuse,
    session_action,
)

ACCOUNT_OF = {
    "deepseek": DEEPSEEK_API_KEY,
    "openai": OPENAI_API_KEY,
    "anthropic": ANTHROPIC_API_KEY,
    "openai-compatible": COMPATIBLE_API_KEY,
}

ENV_OF = {
    "deepseek": "DEEPSEEK_API_KEY",
    "openai": OPENAI_ENV_KEY,
    "anthropic": "ANTHROPIC_API_KEY",
    "openai-compatible": "OPENAI_COMPATIBLE_API_KEY",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _database(path: str | None) -> Path:
    return Path(path) if path else Path.cwd() / "database-agent-plan.sqlite"


def _open(path: Path):
    from database_agent.db import open_database
    from questions.schema import create_questions_schema
    conn = open_database(path, scan_roots=[])
    create_questions_schema(conn)
    return conn


def _keychain_run():
    import subprocess

    def run(argv):
        from readers.model_keychain import CommandResult
        completed = subprocess.run(
            list(argv), check=False, capture_output=True, text=True)
        return CommandResult(completed.returncode, completed.stdout,
                             completed.stderr)

    return run


def _print_lanes(out) -> None:
    print(explain_order(), file=out)
    print("", file=out)
    print("1. Managed — coming later. No backend.", file=out)
    print("2. Subscription:", file=out)
    if os.environ.get(SIWC_FLAG) == "1":
        print("   Continue with ChatGPT — live. "
              "Commercial use still waits on OpenAI's partner access.", file=out)
    else:
        print("   Continue with ChatGPT — shown, not live. "
              f"Set {SIWC_FLAG}=1 to sign in on this machine. "
              "An API key works today.", file=out)
    print("   Claude subscription — use Claude Code or an API key — "
          "Anthropic policy. Sign in inside Claude Code.", file=out)
    print("3. API key — deepseek, openai, anthropic, openai-compatible.",
          file=out)
    present = find_binary(shutil.which)
    print("   Claude Code — the unmodified `claude` binary. "
          + ("claude is on PATH. " if present else "claude is not on PATH. ")
          + "Sign in inside Claude Code. This app never reads that login. "
          + (f"{CLAUDE_FLAG}=1." if claude_flag() else f"{CLAUDE_FLAG} is off."),
          file=out)


def _active_line(conn) -> str:
    choice = load_provider_choice(conn)
    if choice is None:
        if os.environ.get("DEEPSEEK_API_KEY", "").strip():
            return ("Active: deepseek via DEEPSEEK_API_KEY "
                    "(the default when that key is set and no other provider "
                    "is stored).")
        return "Active: none stored. A scan uses no cloud model unless DeepSeek's key is set."
    return "Active: " + json.dumps(
        {key: choice[key] for key in choice if key != "base_url" or True},
        sort_keys=True)


def command_list(conn, out) -> int:
    _print_lanes(out)
    print("", file=out)
    print(_active_line(conn), file=out)
    return 0


def _key_state(provider: str, keychain_run) -> str:
    """present or absent. The secret itself is never returned."""
    env_name = ENV_OF.get(provider, "")
    if env_name and os.environ.get(env_name, "").strip():
        return "present"
    account = ACCOUNT_OF.get(provider)
    if account is None or keychain_run is None:
        return "absent"
    try:
        found = find_secret(account, run=keychain_run)
    except Exception:
        return "absent"
    return "present" if found else "absent"


def command_status(conn, out, *, keychain_run) -> int:
    """Where this folder stands. Sends nothing and prints no secret."""
    print(_active_line(conn), file=out)
    for provider in ("deepseek", "openai", "anthropic", "openai-compatible"):
        print(f"{provider} key: {_key_state(provider, keychain_run)}", file=out)
    print(f"{SIWC_FLAG}: "
          + ("on" if os.environ.get(SIWC_FLAG) == "1" else "off"), file=out)
    print(f"{CLAUDE_FLAG}: " + ("on" if claude_flag() else "off"), file=out)
    print("claude binary: "
          + ("on PATH" if find_binary(shutil.which) else "not on PATH"),
          file=out)
    print("Managed — coming later. Selecting it refuses.", file=out)
    print("Nothing was sent.", file=out)
    return 0


def command_add(conn, provider: str, *, key: str, base_url: str | None,
                model: str | None, user: str, keychain_run) -> dict:
    if provider not in ACCOUNT_OF:
        raise KeychainError(
            f"{provider!r} is not a BYOK provider this command can store")
    if provider == "openai-compatible" and not (base_url or "").startswith("https://"):
        raise KeychainError(
            f"set {ENV_COMPATIBLE_BASE} to an https URL before adding that provider")
    add_secret(ACCOUNT_OF[provider], key, run=keychain_run)
    choice = {
        "lane": "byok",
        "provider": provider,
        "credential": "keychain",
        "provenance": "answered",
    }
    if provider == "openai-compatible":
        choice["base_url"] = base_url
    if model:
        choice["model"] = model
    return store_provider_choice(
        conn, choice, user_id=user, recorded_at=_now())


def command_remove(conn, provider: str, *, user: str, keychain_run, out) -> int:
    if provider not in ACCOUNT_OF:
        print(f"{provider!r} is not a stored API-key provider.", file=out)
        return 2
    delete_secret(ACCOUNT_OF[provider], run=keychain_run)
    current = load_provider_choice(conn)
    if current and current.get("provider") == provider:
        store_provider_choice(
            conn, {"lane": "none", "provider": "none", "provenance": "answered"},
            user_id=user, recorded_at=_now())
    print(f"Removed the keychain item for {provider}. "
          "Add it again to rotate.", file=out)
    return 0


def command_use(conn, lane: str, provider: str, *, user: str, model: str | None,
                base_url: str | None, keychain_run, out) -> int:
    if lane == "managed":
        print("Managed — coming later. There is no backend.", file=out)
        return 2
    if lane == "subscription" and provider in ("anthropic", "claude", "claude-code"):
        print(POLICY, file=out)
        print("Sign in inside Claude Code, or use an API key.", file=out)
        return 2
    if lane == "subscription" and provider == "openai":
        choice = {
            "lane": "subscription", "provider": "openai", "credential": "keychain",
            "provenance": "answered",
        }
        if model:
            choice["model"] = model
        try:
            stored = store_provider_choice(
                conn, choice, user_id=user, recorded_at=_now())
        except ValueError as refusal:
            print(str(refusal), file=out)
            return 2
        print("Stored Continue with ChatGPT. Sign in with "
              "`filesorter providers sign-in-chatgpt` when "
              f"{SIWC_FLAG}=1. The plan database has the lane, not the tokens.",
              file=out)
        print(json.dumps(stored, sort_keys=True), file=out)
        return 0
    if provider == "claude-code":
        choice = {"lane": "byok", "provider": "claude-code", "credential": "none",
                  "provenance": "answered"}
        if model:
            choice["model"] = model
        try:
            stored = store_provider_choice(
                conn, choice, user_id=user, recorded_at=_now())
        except ValueError as refusal:
            print(str(refusal), file=out)
            return 2
        print("Stored Claude Code. Sign in inside Claude Code. "
              "This app does not read that login.", file=out)
        print(json.dumps(stored, sort_keys=True), file=out)
        return 0
    choice = {"lane": lane, "provider": provider, "credential": "env",
              "provenance": "answered"}
    if model:
        choice["model"] = model
    if base_url:
        choice["base_url"] = base_url
    if lane == "byok" and provider in ACCOUNT_OF:
        # Prefer a keychain item when one exists; otherwise the environment.
        if find_secret(ACCOUNT_OF[provider], run=keychain_run):
            choice["credential"] = "keychain"
    try:
        stored = store_provider_choice(
            conn, choice, user_id=user, recorded_at=_now())
    except ValueError as refusal:
        print(str(refusal), file=out)
        return 2
    print("Stored provider choice (no secret is in the plan database):", file=out)
    print(json.dumps(stored, sort_keys=True), file=out)
    return 0


def command_dry_run(provider: str, *, model: str | None, base_url: str | None,
                    key_present: bool, out) -> int:
    """Print the request shape. Sends nothing and never prints a key."""
    if provider == OPENAI_PROVIDER:
        described = describe_request(
            provider=provider,
            base_url=base_url or DEFAULT_BASE_URL,
            model_id=model or os.environ.get(OPENAI_MODEL, ""),
        )
        body = None
        if described["model"]:
            body = chat_body(model_id=described["model"], max_tokens=16,
                             prompt='Reply with one JSON object {"ok": true}')
        headers = "Authorization: Bearer <redacted>" if key_present else "no key"
    elif provider == "anthropic":
        described = {
            "provider": "anthropic",
            "endpoint": MESSAGES_URL,
            "model": model or os.environ.get(ANTHROPIC_MODEL, ""),
            "shape": "messages",
            "sent": False,
        }
        body = (messages_body(model_id=described["model"], max_tokens=16,
                              prompt="Reply with one JSON object.")
                if described["model"] else None)
        headers = ("x-api-key: <redacted>, anthropic-version: "
                   + messages_headers("present")["anthropic-version"]
                   if key_present else "no key")
    elif provider == COMPATIBLE:
        described = describe_request(
            provider=provider,
            base_url=base_url or os.environ.get(ENV_COMPATIBLE_BASE, ""),
            model_id=model or os.environ.get(ENV_COMPATIBLE_MODEL, ""),
        )
        body = None
        headers = "Authorization: Bearer <redacted>" if key_present else "no key"
    elif provider == "deepseek":
        model_id = model or os.environ.get("DEEPSEEK_MODEL_FAST", "")
        base = (os.environ.get("DEEPSEEK_BASE_URL", "").strip()
                or "https://api.deepseek.com")
        described = {
            "provider": "deepseek",
            "endpoint": base.rstrip("/") + "/chat/completions",
            "model": model_id,
            "shape": "chat.completions",
            "sent": False,
        }
        body = None
        if model_id:
            from readers.model_deepseek import request_body
            body = request_body(
                model_id=model_id, max_tokens=16,
                prompt='Reply with one JSON object {"ok": true}')
        headers = "Authorization: Bearer <redacted>" if key_present else "no key"
    else:
        print(f"{provider!r} is not a dry-run provider.", file=out)
        return 2
    print(json.dumps({
        "lane": "byok",
        "provider": described["provider"],
        "endpoint": described.get("endpoint", ""),
        "model": described.get("model", ""),
        "shape": described.get("shape", ""),
        "key": headers,
        "sent": False,
        "body_without_secrets": body,
    }, indent=2, sort_keys=True), file=out)
    print("No file was read. No request was sent. No network call was made.",
          file=out)
    return 0


def command_sign_in(out, *, conn=None, user: str = "local", keychain_run=None,
                    post_form=None, jwks=None, wait=None, open_url=None,
                    model: str | None = None, now: int | None = None,
                    nonce: str | None = None, state: str | None = None) -> int:
    """Loopback Sign in with ChatGPT. Flag off refuses before any browser."""
    refusal = begin_or_refuse()
    if refusal is not None:
        print(refusal, file=out)
        return 2
    if conn is None or keychain_run is None:
        print("Sign in needs a plan database and a keychain. Nothing was stored.",
              file=out)
        return 2
    from readers.model_siwc import (
        JWKS_URI,
        SiwcRefused,
        bind_loopback,
        fetch_jwks,
        finish_sign_in,
        post_token_form,
        prepare_sign_in,
    )
    host = find_secret(SIWC_HOST, run=keychain_run)
    if not host:
        import uuid
        host = "urn:uuid:" + uuid.uuid4().hex
        add_secret(SIWC_HOST, host, run=keychain_run)
    issued = None
    raw = find_secret(SIWC_REGISTRATION, run=keychain_run)
    if raw:
        try:
            issued = json.loads(raw).get("issued_client_id")
        except json.JSONDecodeError:
            issued = None
    server = None
    if wait is None:
        server = bind_loopback()
        port = server.server_address[1]
    else:
        port = 1455
    attempt = prepare_sign_in(
        host_id=host, port=port, issued_client_id=issued,
        state=state, nonce=nonce)
    print("Continue with ChatGPT. Open this URL if the browser does not:", file=out)
    print(attempt.url, file=out)
    print("Commercial use of ChatGPT plan tokens waits on OpenAI's partner "
          "access. This command is the local sign-in.", file=out)
    if open_url is not None:
        open_url(attempt.url)
    elif wait is None:
        import webbrowser
        webbrowser.open(attempt.url)
    if wait is None:
        server.timeout = 300
        server.handle_request()
        query = server.query
        if not query:
            print("The browser did not return to the loopback callback. "
                  "No token was stored.", file=out)
            return 2
    else:
        query = wait(attempt.url)
    try:
        document = jwks if jwks is not None else fetch_jwks()
        session = finish_sign_in(
            attempt, query, post_form=post_form or post_token_form,
            jwks=document, now=now if now is not None else int(
                datetime.now(timezone.utc).timestamp()))
    except SiwcRefused as refusal:
        print(str(refusal), file=out)
        return 2
    except Exception:
        print("Sign in did not finish. Tokens were not stored.", file=out)
        return 2
    stored_tokens = siwc_tokens_for_storage(session, model=model)
    for account, secret in stored_tokens.items():
        add_secret(account, secret, run=keychain_run)
    choice = {
        "lane": "subscription", "provider": "openai", "credential": "keychain",
        "provenance": "answered",
    }
    if model:
        choice["model"] = model
    stored = store_provider_choice(
        conn, choice, user_id=user, recorded_at=_now())
    print("ChatGPT sign-in is stored in the keychain. "
          "The plan database has the lane, not the tokens.", file=out)
    if not session.inference_ready:
        print("chatgpt.tokens.use.direct was not granted, so plan usage "
              "will not be called.", file=out)
    print("JWKS: " + JWKS_URI, file=out)
    print(json.dumps(
        {key: stored[key] for key in stored if key != "subject"},
        sort_keys=True), file=out)
    return 0


def command_claude(prompt: str, *, run, which, out) -> int:
    if not claude_flag():
        print(POLICY, file=out)
        print(f"Set {CLAUDE_FLAG}=1 to run the local binary.", file=out)
        return 2
    binary = find_binary(which)
    if binary is None:
        print(MISSING, file=out)
        return 2
    try:
        answer = run_prompt(binary, prompt, run=run, flag_on=True)
    except RuntimeError as refusal:
        print(str(refusal), file=out)
        return 2
    print(answer, file=out)
    return 0


def command_reauth_status(*, expires_at: int, now: int,
                          refresh_failed: bool, out) -> int:
    action = session_action(
        expires_at=expires_at, now=now, refresh_failed=refresh_failed)
    if action == "reauthenticate":
        print(REAUTH_MESSAGE, file=out)
        return 2
    print(action, file=out)
    return 0


def main(argv: list[str], *, out=None, key_reader=None, keychain_run=None,
         claude_run=None, which_claude=None, siwc_post=None, siwc_jwks=None,
         siwc_wait=None, siwc_open=None, siwc_now=None, siwc_nonce=None,
         siwc_state=None) -> int:
    out = out if out is not None else sys.stdout
    parser = argparse.ArgumentParser(prog="filesorter providers")
    parser.add_argument("--database", default=None)
    parser.add_argument("--user", default="local")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("list")
    sub.add_parser("status")
    add = sub.add_parser("add")
    add.add_argument("provider")
    add.add_argument("--base-url", default=None)
    add.add_argument("--model", default=None)
    remove = sub.add_parser("remove")
    remove.add_argument("provider")
    use = sub.add_parser("use")
    use.add_argument("lane")
    use.add_argument("provider")
    use.add_argument("--model", default=None)
    use.add_argument("--base-url", default=None)
    dry = sub.add_parser("dry-run")
    dry.add_argument("provider")
    dry.add_argument("--model", default=None)
    dry.add_argument("--base-url", default=None)
    sign_in = sub.add_parser("sign-in-chatgpt")
    sign_in.add_argument("--model", default=None)
    claude = sub.add_parser("claude-code")
    claude.add_argument("--prompt", default='Reply with one JSON object {"ok": true}')
    status = sub.add_parser("session")
    status.add_argument("--expires-at", type=int, required=True)
    status.add_argument("--now", type=int, required=True)
    status.add_argument("--refresh-failed", action="store_true")

    if not argv:
        argv = ["list"]
    args = parser.parse_args(argv)
    command = args.command or "list"
    needs_db = command in ("list", "add", "remove", "use", "status")
    conn = _open(_database(args.database)) if needs_db else None
    run = keychain_run or _keychain_run()

    if command == "list":
        return command_list(conn, out)
    if command == "status":
        return command_status(conn, out, keychain_run=run)
    if command == "add":
        secret = key_reader() if key_reader else getpass(
            "Paste the API key. It is not shown and it is not written to the "
            "plan database: ")
        try:
            stored = command_add(
                conn, args.provider, key=secret, base_url=args.base_url,
                model=args.model, user=args.user, keychain_run=run)
        except (KeychainError, ValueError) as refusal:
            print(str(refusal), file=out)
            return 2
        print("Stored the key in the keychain and recorded the provider. "
              "The key is not in this sentence.", file=out)
        print(json.dumps(stored, sort_keys=True), file=out)
        return 0
    if command == "remove":
        return command_remove(
            conn, args.provider, user=args.user, keychain_run=run, out=out)
    if command == "use":
        return command_use(
            conn, args.lane, args.provider, user=args.user, model=args.model,
            base_url=args.base_url, keychain_run=run, out=out)
    if command == "dry-run":
        present = False
        account = ACCOUNT_OF.get(args.provider)
        env_name = ENV_OF.get(args.provider)
        if env_name and os.environ.get(env_name, "").strip():
            present = True
        elif account is not None and find_secret(account, run=run):
            present = True
        return command_dry_run(
            args.provider, model=args.model, base_url=args.base_url,
            key_present=present, out=out)
    if command == "sign-in-chatgpt":
        from readers.model_siwc import flag_enabled
        if not flag_enabled():
            return command_sign_in(out)
        return command_sign_in(
            out, conn=_open(_database(args.database)), user=args.user,
            keychain_run=run, post_form=siwc_post, jwks=siwc_jwks,
            wait=siwc_wait, open_url=siwc_open, model=args.model,
            now=siwc_now, nonce=siwc_nonce, state=siwc_state)
    if command == "claude-code":
        return command_claude(
            args.prompt, run=claude_run or run,
            which=which_claude or (lambda _name: None), out=out)
    if command == "session":
        return command_reauth_status(
            expires_at=args.expires_at, now=args.now,
            refresh_failed=args.refresh_failed, out=out)
    parser.error(f"unknown providers command {command!r}")
    return 2


def route_byok(choice: dict, *, tier_of_call_site, max_response_tokens: int,
               timeout_seconds: float, out, keychain_run=None):
    """A TierRouting for a stored OpenAI, Anthropic, or compatible choice.

    DeepSeek stays on the existing route. This returns None, after a sentence,
    when the model id or the key is missing. It does not print the key.
    """
    from readers.model_anthropic import (
        ENV_MODEL as ANTHROPIC_ENV_MODEL,
        MESSAGES_URL,
        anthropic_http_invoke,
        post_json as anthropic_post,
    )
    from readers.model_openai import (
        COMPATIBLE,
        DEFAULT_BASE_URL,
        ENV_COMPATIBLE_BASE,
        ENV_COMPATIBLE_MODEL,
        ENV_MODEL,
        one_model_routing,
        post_json as openai_post,
    )
    from privacy.release import ModelTarget
    from llm_harness.transport import ModelClient
    from readers.model_routing import TIERS, TierRouting

    provider = choice.get("provider")
    key = resolve_api_key(
        provider, credential=choice.get("credential") or "env",
        keychain_run=keychain_run)
    if provider == "openai":
        model = choice.get("model") or os.environ.get(ENV_MODEL, "")
        base = DEFAULT_BASE_URL
        if not key or not model.strip():
            print("No OpenAI model was consulted. Set OPENAI_MODEL and provide "
                  "OPENAI_API_KEY, or store the key in the keychain.", file=out)
            return None
        return one_model_routing(
            api_key=key, base_url=base, model_id=model.strip(),
            provider="openai", tier_of_call_site=tier_of_call_site,
            max_response_tokens=max_response_tokens, post=openai_post)
    if provider == COMPATIBLE or provider == "openai-compatible":
        model = choice.get("model") or os.environ.get(ENV_COMPATIBLE_MODEL, "")
        base = choice.get("base_url") or os.environ.get(ENV_COMPATIBLE_BASE, "")
        if not key or not model.strip() or not str(base).startswith("https://"):
            print("No OpenAI-compatible model was consulted. It needs an https "
                  "base URL, a model id, and a key.", file=out)
            return None
        return one_model_routing(
            api_key=key, base_url=base, model_id=model.strip(),
            provider="openai-compatible", tier_of_call_site=tier_of_call_site,
            max_response_tokens=max_response_tokens, post=openai_post)
    if provider == "anthropic":
        model = choice.get("model") or os.environ.get(ANTHROPIC_ENV_MODEL, "")
        if not key or not model.strip():
            print("No Anthropic model was consulted. Set ANTHROPIC_MODEL and "
                  "provide ANTHROPIC_API_KEY, or store the key in the keychain.",
                  file=out)
            return None
        target = ModelTarget(locality="cloud", model_id=model.strip(),
                             provider="anthropic")
        invoke = anthropic_http_invoke(
            api_key=key, model_target=target,
            max_response_tokens=max_response_tokens, post=anthropic_post,
            url=MESSAGES_URL)
        client = ModelClient(model_target=target, invoke=invoke)
        return TierRouting(
            tier_of_call_site=tier_of_call_site,
            client_of_tier={tier: client for tier in TIERS})
    print(f"No cloud model was consulted: {provider!r} is not routed.", file=out)
    return None


def resolve_api_key(provider: str, *, credential: str, environ=None,
                    keychain_run=None) -> str:
    """Environment, then .env is the caller's job, then keychain. Never logs."""
    source = os.environ if environ is None else environ
    env_name = ENV_OF.get(provider, "")
    from_env = (source.get(env_name) or "").strip() if env_name else ""
    if from_env:
        return from_env
    if credential != "keychain":
        return ""
    account = ACCOUNT_OF.get(provider)
    if account is None or keychain_run is None:
        return ""
    found = find_secret(account, run=keychain_run)
    return found or ""


def siwc_tokens_for_storage(session, *, model: str | None = None) -> dict[str, str]:
    """What goes into the keychain, keyed by account. Not for the plan database."""
    from readers.model_siwc import registration_document
    return {
        SIWC_ACCESS: session.access_token,
        SIWC_REFRESH: session.refresh_token,
        SIWC_REGISTRATION: json.dumps(
            registration_document(session, model=model), sort_keys=True),
    }


def _env_value(name: str, env_lookup) -> str:
    if not name:
        return ""
    if env_lookup is None:
        return (os.environ.get(name) or "").strip()
    return (env_lookup(name) or "").strip()


def _byok_key(provider: str, choice: dict, env_lookup, keychain_run) -> str:
    found = _env_value(ENV_OF.get(provider, ""), env_lookup)
    if found:
        return found
    if choice.get("credential") != "keychain" or keychain_run is None:
        return ""
    account = ACCOUNT_OF.get(provider)
    if account is None:
        return ""
    return find_secret(account, run=keychain_run) or ""


def understanding_from_choice(choice, *, out, role: str = "fast", env_lookup=None,
                              keychain_run=None, http_post=None, siwc_post=None,
                              siwc_post_form=None, siwc_jwks=None, siwc_now=None,
                              claude_run=None, which_claude=None):
    """The understanding adapter for a stored choice.

    None means the caller keeps the DeepSeek environment path, including its
    `/models` check. A tuple means this choice already decided, and `(None, "")`
    means nothing is sent. A ChatGPT or Claude Code choice does not fall
    through to DeepSeek.
    """
    if not choice:
        return None
    lane = choice.get("lane")
    provider = choice.get("provider")
    if lane == "none":
        print("No cloud model was consulted: the stored provider choice is none.",
              file=out)
        return (None, "")
    if lane == "managed":
        print("Managed — coming later. There is no backend.", file=out)
        return (None, "")
    if provider == "deepseek" and choice.get("credential") != "keychain":
        return None
    if provider == "claude-code":
        if not claude_flag():
            print(POLICY, file=out)
            print(f"Set {CLAUDE_FLAG}=1 to run the local binary.", file=out)
            return (None, "")
        binary = find_binary(which_claude or shutil.which)
        if binary is None:
            print(MISSING, file=out)
            return (None, "")
        from readers.model_claude_code import ClaudeCodeUnderstanding, default_runner
        model = (choice.get("model") or "claude").strip()
        return (ClaudeCodeUnderstanding(binary, claude_run or default_runner()), model)
    if lane == "subscription":
        if provider != "openai":
            print(POLICY, file=out)
            print("Sign in inside Claude Code, or use an API key.", file=out)
            return (None, "")
        from readers.model_siwc import SiwcUnderstanding, load_ready_access, post_responses
        ready = load_ready_access(
            out=out, keychain_run=keychain_run, post_form=siwc_post_form,
            jwks=siwc_jwks, now=siwc_now)
        if ready is None:
            return (None, "")
        access, model = ready
        return (SiwcUnderstanding(
            access_token=access, post=siwc_post or post_responses, model_id=model),
            model)
    if provider == "deepseek":
        key = _byok_key("deepseek", choice, env_lookup, keychain_run)
        role_env = {
            "fast": "DEEPSEEK_MODEL_FAST",
            "logic": "DEEPSEEK_MODEL_LOGIC",
            "reasoning": "DEEPSEEK_MODEL_REASONING",
        }.get(role, "")
        model = (choice.get("model") or _env_value(role_env, env_lookup)).strip()
        base = _env_value("DEEPSEEK_BASE_URL", env_lookup) or "https://api.deepseek.com"
        if not key or not model:
            print("No DeepSeek model was consulted. Store the key and set the "
                  "model id. No dossier was sent.", file=out)
            return (None, "")
        from readers.model_understanding_http import DeepSeekUnderstanding, post_json
        return (DeepSeekUnderstanding(
            api_key=key, base_url=base, post=http_post or post_json), model)
    if provider == "openai":
        key = _byok_key("openai", choice, env_lookup, keychain_run)
        model = (choice.get("model") or _env_value(OPENAI_MODEL, env_lookup)).strip()
        if not key or not model:
            print("No OpenAI model was consulted. Set OPENAI_MODEL and provide "
                  "OPENAI_API_KEY, or store the key in the keychain.", file=out)
            return (None, "")
        from readers.model_understanding_http import (
            OpenAICompatibleUnderstanding, post_json,
        )
        return (OpenAICompatibleUnderstanding(
            api_key=key, base_url=DEFAULT_BASE_URL, post=http_post or post_json,
            name="openai"), model)
    if provider in (COMPATIBLE, "openai-compatible"):
        key = _byok_key("openai-compatible", choice, env_lookup, keychain_run)
        model = (choice.get("model") or _env_value(ENV_COMPATIBLE_MODEL, env_lookup)).strip()
        base = choice.get("base_url") or _env_value(ENV_COMPATIBLE_BASE, env_lookup)
        if not key or not model or not str(base).startswith("https://"):
            print("No OpenAI-compatible model was consulted. It needs an https "
                  "base URL, a model id, and a key.", file=out)
            return (None, "")
        from readers.model_understanding_http import (
            OpenAICompatibleUnderstanding, post_json,
        )
        return (OpenAICompatibleUnderstanding(
            api_key=key, base_url=str(base), post=http_post or post_json), model)
    if provider == "anthropic":
        key = _byok_key("anthropic", choice, env_lookup, keychain_run)
        model = (choice.get("model") or _env_value(ANTHROPIC_MODEL, env_lookup)).strip()
        if not key or not model:
            print("No Anthropic model was consulted. Set ANTHROPIC_MODEL and "
                  "provide ANTHROPIC_API_KEY, or store the key in the keychain.",
                  file=out)
            return (None, "")
        from readers.model_anthropic import AnthropicUnderstanding, post_json
        return (AnthropicUnderstanding(
            api_key=key, post=http_post or post_json, model_id=model), model)
    print(f"No cloud model was consulted: {provider!r} is not routed.", file=out)
    return (None, "")
