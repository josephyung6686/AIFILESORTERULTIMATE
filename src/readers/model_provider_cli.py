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
    print("1. Managed / plan-included: coming later. No backend.", file=out)
    print("2. Subscription sign-in:", file=out)
    print("   Continue with ChatGPT — " + (
        "flag on (FILESORTER_OPENAI_SIWC=1)." if os.environ.get(SIWC_FLAG) == "1"
        else "shown, not live. Use an API key today."), file=out)
    print("   Claude subscription — " + POLICY, file=out)
    print("3. API key (BYOK): deepseek, openai, anthropic, openai-compatible.",
          file=out)
    print("   Claude Code — the unmodified binary, flag "
          f"{CLAUDE_FLAG}. " + (
              "Flag is on." if claude_flag() else "Flag is off."), file=out)


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
        print("Managed / plan-included is coming later. There is no backend.",
              file=out)
        return 2
    if lane == "subscription" and provider in ("anthropic", "claude"):
        print(POLICY, file=out)
        return 2
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
        described = {
            "provider": "deepseek",
            "endpoint": os.environ.get("DEEPSEEK_BASE_URL", ""),
            "model": model or "",
            "shape": "chat.completions",
            "sent": False,
        }
        body = None
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
    print("No file was read. No request was sent.", file=out)
    return 0


def command_sign_in(out) -> int:
    refusal = begin_or_refuse()
    if refusal is not None:
        print(refusal, file=out)
        return 2
    print("FILESORTER_OPENAI_SIWC=1 is set. This build will not store tokens:",
          file=out)
    print("ID token signature verification against OpenAI's JWKS is a TODO, "
          "so the safer path is still an API key. The authorize URL can be "
          "built by readers.model_siwc.authorize_request; this command does "
          "not open a browser until that check exists.", file=out)
    return 2


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
         claude_run=None, which_claude=None) -> int:
    out = out if out is not None else sys.stdout
    parser = argparse.ArgumentParser(prog="filesorter providers")
    parser.add_argument("--database", default=None)
    parser.add_argument("--user", default="local")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("list")
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
    sub.add_parser("sign-in-chatgpt")
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
    needs_db = command in ("list", "add", "remove", "use")
    conn = _open(_database(args.database)) if needs_db else None
    run = keychain_run or _keychain_run()

    if command == "list":
        return command_list(conn, out)
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
        return command_sign_in(out)
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


def siwc_tokens_for_storage(session) -> dict[str, str]:
    """What goes into the keychain, keyed by account. Not for the plan database."""
    return {
        SIWC_ACCESS: session.access_token,
        SIWC_REFRESH: session.refresh_token,
        SIWC_REGISTRATION: json.dumps({
            "issued_client_id": session.issued_client_id,
            "host_id": session.host_id,
            "expires_at": session.expires_at,
            "scopes": list(session.scopes),
            "inference_ready": session.inference_ready,
            "subject": session.subject,
        }, sort_keys=True),
    }
