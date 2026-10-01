# src/readers/model_siwc.py
"""Sign in with ChatGPT, the open-source OAuth flow. Off unless the flag is set.

Followed, and cited in `docs/model-providers.md`:

- https://developers.openai.com/siwc/quickstart
- https://developers.openai.com/siwc/token-sharing-open-source/sign-in
- https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference
- https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations

This module does not read `~/.codex/auth.json` or any browser cookie. Tokens
are returned to the caller, who stores them in the keychain. The commercial
waitlist is not a URL this checkout found on those pages, so the flag-off
message points at the quickstart, which is the page that states the limit.

ID-token signature verification against OpenAI's JWKS is not implemented.
`accept_token_response` refuses to mark inference ready until a caller passes
a verifier that returns true. Guessing a JWKS URL, or skipping the check, is
the less safe path and is not what this module does.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
from dataclasses import dataclass
from typing import Callable, Mapping

FLAG: str = "FILESORTER_OPENAI_SIWC"
QUICKSTART: str = "https://developers.openai.com/siwc/quickstart"

AUTHORIZE_URL: str = "https://auth.openai.com/api/accounts/authorize"
TOKEN_URL: str = "https://auth.openai.com/api/accounts/oauth/token"
RESPONSES_URL: str = "https://api.openai.com/v1/responses"
RESOURCE: str = "https://api.openai.com/v1"
DYNAMIC_CLIENT: str = "dynamic_agent_client"
AGENT_NAME: str = "filesorter"
CALLBACK_PATH: str = "/auth/callback"
ISSUER: str = "https://auth.openai.com"

#: Identity scopes plus the plan-usage scopes the sign-in page names.
SCOPES: str = (
    "openid profile email offline_access resource.invoke "
    "chatgpt.tokens.use.direct"
)
PLAN_SCOPE: str = "chatgpt.tokens.use.direct"

FLAG_OFF_MESSAGE: str = (
    "Continue with ChatGPT is shown here and is not live. OpenAI's Sign in "
    "with ChatGPT quickstart says ChatGPT plan usage is limited to open-source "
    "partners and selected private clients; a commercial app needs that access. "
    "Use an API key today. The page that states the limit is "
    + QUICKSTART
    + ". Set FILESORTER_OPENAI_SIWC=1 only after that access applies to this "
    "app. This checkout did not find a separate waitlist form URL on that page."
)


class SiwcRefused(RuntimeError):
    """The sign-in did not proceed. The message has no token in it."""


def flag_enabled(environ: Mapping[str, str] | None = None) -> bool:
    source = os.environ if environ is None else environ
    return source.get(FLAG) == "1"


def pkce_pair(*, random_bytes: bytes | None = None) -> tuple[str, str]:
    """RFC 7636 S256. The challenge is base64url without padding."""
    raw = secrets.token_bytes(32) if random_bytes is None else random_bytes
    if len(raw) < 32:
        raise SiwcRefused("a PKCE verifier needs at least 32 random bytes")
    verifier = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    if not 43 <= len(verifier) <= 128:
        raise SiwcRefused("the PKCE verifier is outside the length RFC 7636 allows")
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return verifier, challenge


def redirect_uri(port: int) -> str:
    if not isinstance(port, int) or not 1 <= port <= 65535:
        raise SiwcRefused("the loopback port is not a TCP port")
    return f"http://127.0.0.1:{port}{CALLBACK_PATH}"


def authorize_request(*, host_id: str, redirect: str, state: str, nonce: str,
                      code_challenge: str, issued_client_id: str | None = None,
                      ) -> dict[str, str]:
    """Query parameters for the authorize endpoint. First sign-in uses the
    dynamic client. A later sign-in reuses the issued client id and omits the
    name hint, which is what the sign-in page says to do.
    """
    if not host_id or host_id == DYNAMIC_CLIENT:
        raise SiwcRefused("ext_agent_host_id must be this app's own host id")
    if "127.0.0.1" not in redirect or not redirect.endswith(CALLBACK_PATH):
        raise SiwcRefused(
            "redirect_uri must be the 127.0.0.1 loopback path /auth/callback. "
            "localhost is not a substitute the sign-in page allows.")
    client_id = issued_client_id or DYNAMIC_CLIENT
    params = {
        "client_id": client_id,
        "ext_agent_host_id": host_id,
        "response_type": "code",
        "redirect_uri": redirect,
        "scope": SCOPES,
        "resource": RESOURCE,
        "state": state,
        "nonce": nonce,
        "code_challenge_method": "S256",
        "code_challenge": code_challenge,
    }
    if client_id == DYNAMIC_CLIENT:
        params["agent_name_hint"] = AGENT_NAME
    return params


def authorize_url(params: Mapping[str, str]) -> str:
    from urllib.parse import urlencode
    return AUTHORIZE_URL + "?" + urlencode(params)


def token_exchange_form(*, client_id: str, code: str, verifier: str,
                        redirect: str) -> dict[str, str]:
    if client_id == DYNAMIC_CLIENT or not client_id:
        raise SiwcRefused(
            "token exchange uses the issued client id, not dynamic_agent_client")
    return {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "code": code,
        "code_verifier": verifier,
        "redirect_uri": redirect,
        "resource": RESOURCE,
    }


def refresh_form(*, client_id: str, refresh_token: str) -> dict[str, str]:
    """Refresh. Scope is omitted so the existing grant is kept, per the accounts page."""
    if client_id == DYNAMIC_CLIENT or not client_id:
        raise SiwcRefused(
            "refresh uses the issued client id, not dynamic_agent_client")
    if not refresh_token:
        raise SiwcRefused("there is no refresh token to send")
    return {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "refresh_token": refresh_token,
        "resource": RESOURCE,
    }


def responses_body(*, model: str, prompt: str) -> dict:
    """The inference body the models-and-inference page requires.

    `store` false and `stream` true are not optional on this flow. The input
    is an array. A system-role message is rejected by that page, so this body
    does not send one.
    """
    if not model.strip():
        raise SiwcRefused("no model id for the Responses call")
    return {
        "model": model,
        "input": [{"role": "user", "content": prompt}],
        "store": False,
        "stream": True,
    }


def responses_headers(access_token: str) -> dict[str, str]:
    if not access_token.strip():
        raise SiwcRefused("no access token")
    return {
        "Authorization": "Bearer " + access_token.strip(),
        "Content-Type": "application/json",
    }


@dataclass(frozen=True, slots=True)
class Session:
    issued_client_id: str
    host_id: str
    access_token: str
    refresh_token: str
    expires_at: int
    scopes: tuple[str, ...]
    inference_ready: bool
    subject: str


def _payload(id_token: str) -> dict:
    parts = id_token.split(".")
    if len(parts) != 3:
        raise SiwcRefused("the ID token is not a three-part JWT")
    padded = parts[1] + "=" * (-len(parts[1]) % 4)
    try:
        raw = base64.urlsafe_b64decode(padded.encode("ascii"))
        data = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeError) as problem:
        raise SiwcRefused("the ID token payload could not be read") from problem
    if not isinstance(data, dict):
        raise SiwcRefused("the ID token payload is not an object")
    return data


def structural_id_checks(id_token: str, *, nonce: str, audience: str,
                         now: int) -> dict:
    """Issuer, audience, expiry, and nonce. Not a signature check."""
    data = _payload(id_token)
    if data.get("iss") != ISSUER:
        raise SiwcRefused("the ID token issuer is not https://auth.openai.com")
    if data.get("aud") != audience:
        raise SiwcRefused("the ID token audience is not the issued client id")
    if data.get("nonce") != nonce:
        raise SiwcRefused("the ID token nonce does not match this attempt")
    exp = data.get("exp")
    if not isinstance(exp, int) or exp <= now:
        raise SiwcRefused("the ID token is expired")
    if not isinstance(data.get("sub"), str) or not data["sub"]:
        raise SiwcRefused("the ID token has no subject")
    return data


def accept_token_response(response: Mapping, *, nonce: str, now: int,
                          host_id: str, expires_in_from_now: bool = True,
                          signature_ok: bool) -> Session:
    """Build a session. Inference stays off until the signature check passed.

    `signature_ok` is the caller's verifier. The default live command passes
    false, because this build does not check the JWKS. False stores nothing
    the Responses API may use.
    """
    client_id = str(response.get("client_id") or "")
    if not client_id or client_id == DYNAMIC_CLIENT:
        raise SiwcRefused(
            "the token response has no issued client id. "
            "dynamic_agent_client is not saved.")
    id_token = str(response.get("id_token") or "")
    claims = structural_id_checks(
        id_token, nonce=nonce, audience=client_id, now=now)
    scopes = response.get("scope") or response.get("scopes") or ""
    if isinstance(scopes, str):
        scope_list = tuple(scopes.split())
    else:
        scope_list = tuple(scopes)
    if not signature_ok:
        raise SiwcRefused(
            "ID token signature verification is not implemented in this build "
            "(TODO: OpenAI's published JWKS for issuer https://auth.openai.com). "
            "Tokens were not stored. Use an API key.")
    expires_in = response.get("expires_in")
    if not isinstance(expires_in, int) or expires_in < 1:
        raise SiwcRefused("the token response has no expires_in")
    access = str(response.get("access_token") or "")
    refresh = str(response.get("refresh_token") or "")
    if not access or not refresh:
        raise SiwcRefused("the token response is missing an access or refresh token")
    ready = PLAN_SCOPE in scope_list
    return Session(
        issued_client_id=client_id,
        host_id=host_id,
        access_token=access,
        refresh_token=refresh,
        expires_at=now + expires_in if expires_in_from_now else expires_in,
        scopes=scope_list,
        inference_ready=ready,
        subject=claims["sub"],
    )


def session_action(*, expires_at: int, now: int, refresh_failed: bool) -> str:
    """What to tell the person. Expired and unrefreshable means reauthenticate."""
    if now < expires_at and not refresh_failed:
        return "use"
    if not refresh_failed:
        return "refresh"
    return "reauthenticate"


REAUTH_MESSAGE: str = (
    "Reauthenticate: the ChatGPT sign-in has expired and the refresh token "
    "was refused. Start Continue with ChatGPT again. The old access token "
    "will not be sent."
)


def read_responses_stream(events: list[str]) -> str:
    """Join `response.output_text.delta` until `response.completed`.

    A failed or incomplete event is a refusal. Stopping before `completed`
    would treat a partial stream as the model's answer.
    """
    text: list[str] = []
    completed = False
    for line in events:
        if not line.startswith("data:"):
            continue
        raw = line[len("data:"):].strip()
        if raw == "[DONE]":
            continue
        event = json.loads(raw)
        kind = event.get("type")
        if kind == "response.output_text.delta":
            text.append(str(event.get("delta") or ""))
        elif kind == "response.failed":
            raise SiwcRefused("the Responses stream failed before it completed")
        elif kind == "response.incomplete":
            raise SiwcRefused("the Responses stream ended incomplete")
        elif kind == "response.completed":
            completed = True
    if not completed:
        raise SiwcRefused(
            "the Responses stream had no response.completed event")
    if not "".join(text).strip():
        raise SiwcRefused("the Responses stream completed with no text")
    return "".join(text)


def begin_or_refuse(environ: Mapping[str, str] | None = None) -> str | None:
    """None when the flow may start. Otherwise the sentence to print."""
    if flag_enabled(environ):
        return None
    return FLAG_OFF_MESSAGE
