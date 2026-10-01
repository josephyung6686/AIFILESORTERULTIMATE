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

ID-token signatures are checked against the JWKS URI OpenAI publishes for
issuer https://auth.openai.com:
https://auth.openai.com/.well-known/jwks.json
(`developers.openai.com/siwc/website`). A bad signature is not stored.
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
#: Published on the Sign in with ChatGPT website page. Not a guessed host.
JWKS_URI: str = "https://auth.openai.com/.well-known/jwks.json"
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
    id_token: str = ""


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

    `signature_ok` is the caller's verifier. False stores nothing the
    Responses API may use. The live sign-in sets it only after
    `rs256_signature_ok` against the published JWKS.
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
            "the ID token signature did not verify against "
            + JWKS_URI
            + ". Tokens were not stored.")
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
        id_token=id_token,
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


_SHA256_DIGESTINFO: bytes = bytes.fromhex(
    "3031300d060960864801650304020105000420")


def _b64url_decode(segment: str) -> bytes:
    padded = segment + "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def _b64url_int(segment: str) -> int:
    raw = _b64url_decode(segment)
    return int.from_bytes(raw, "big")


def _jwt_parts(id_token: str) -> tuple[dict, str]:
    parts = id_token.split(".")
    if len(parts) != 3 or not all(parts):
        raise SiwcRefused("the ID token is not a three-part JWT")
    try:
        header = json.loads(_b64url_decode(parts[0]).decode("utf-8"))
    except (ValueError, UnicodeError) as problem:
        raise SiwcRefused("the ID token header could not be read") from problem
    if not isinstance(header, dict):
        raise SiwcRefused("the ID token header is not an object")
    return header, parts[0] + "." + parts[1]


def rs256_signature_ok(id_token: str, jwks: Mapping) -> bool:
    """True when one published RSA key signs this token as RS256.

    `alg` none, or any algorithm other than RS256, is a failure. The key is
    chosen by `kid`. The message is the header and payload as they arrived,
    not a re-encoded copy.
    """
    try:
        header, signing_input = _jwt_parts(id_token)
    except SiwcRefused:
        return False
    if header.get("alg") != "RS256":
        return False
    kid = header.get("kid")
    keys = jwks.get("keys") if isinstance(jwks, Mapping) else None
    if not isinstance(keys, list):
        return False
    signature = _b64url_decode(id_token.split(".")[2])
    digest = hashlib.sha256(signing_input.encode("ascii")).digest()
    digestinfo = _SHA256_DIGESTINFO + digest
    for key in keys:
        if not isinstance(key, dict):
            continue
        if key.get("kty") != "RSA":
            continue
        if kid and key.get("kid") != kid:
            continue
        if key.get("alg") not in (None, "RS256"):
            continue
        n = key.get("n")
        e = key.get("e")
        if not isinstance(n, str) or not isinstance(e, str):
            continue
        if _pkcs1_sha256_ok(signature, digestinfo, _b64url_int(n), _b64url_int(e)):
            return True
    return False


def _pkcs1_sha256_ok(signature: bytes, digestinfo: bytes, n: int, e: int) -> bool:
    k = (n.bit_length() + 7) // 8
    if e < 3 or k < 64 or len(signature) != k:
        return False
    s = int.from_bytes(signature, "big")
    if s <= 0 or s >= n:
        return False
    em = pow(s, e, n).to_bytes(k, "big")
    if len(em) < len(digestinfo) + 11 or not em.startswith(b"\x00\x01"):
        return False
    rest = em[2:]
    separator = rest.find(b"\x00")
    if separator < 8:
        return False
    if rest[:separator] != b"\xff" * separator:
        return False
    return rest[separator + 1:] == digestinfo


@dataclass(frozen=True, slots=True)
class SignInAttempt:
    url: str
    verifier: str
    nonce: str
    state: str
    redirect: str
    host_id: str
    issued_client_id: str | None


def prepare_sign_in(*, host_id: str, port: int,
                    issued_client_id: str | None = None,
                    state: str | None = None, nonce: str | None = None,
                    ) -> SignInAttempt:
    """The authorize URL and the secrets that stay on this machine until callback."""
    verifier, challenge = pkce_pair()
    state = state or secrets.token_urlsafe(24)
    nonce = nonce or secrets.token_urlsafe(24)
    redirect = redirect_uri(port)
    params = authorize_request(
        host_id=host_id, redirect=redirect, state=state, nonce=nonce,
        code_challenge=challenge, issued_client_id=issued_client_id)
    return SignInAttempt(
        url=authorize_url(params), verifier=verifier, nonce=nonce, state=state,
        redirect=redirect, host_id=host_id, issued_client_id=issued_client_id)


def finish_sign_in(attempt: SignInAttempt, query: Mapping, *,
                   post_form: Callable, jwks: Mapping, now: int) -> Session:
    """Exchange the callback and verify the ID token. No token is returned on failure."""
    if query.get("state") != attempt.state:
        raise SiwcRefused("the callback state does not match this attempt")
    if query.get("error"):
        raise SiwcRefused("OpenAI refused the sign-in. No token was stored.")
    code = query.get("code")
    if not isinstance(code, str) or not code:
        raise SiwcRefused("the callback did not include an authorization code")
    client_id = query.get("client_id") or attempt.issued_client_id
    if not isinstance(client_id, str) or not client_id or client_id == DYNAMIC_CLIENT:
        raise SiwcRefused(
            "the callback did not include an issued client id. "
            "Registration was not stored.")
    if attempt.issued_client_id and client_id != attempt.issued_client_id:
        raise SiwcRefused(
            "the callback client id does not match the saved registration")
    response = post_form(TOKEN_URL, token_exchange_form(
        client_id=client_id, code=code, verifier=attempt.verifier,
        redirect=attempt.redirect))
    if not isinstance(response, Mapping):
        raise SiwcRefused("the token endpoint did not return an object")
    if "client_id" not in response:
        response = dict(response)
        response["client_id"] = client_id
    id_token = str(response.get("id_token") or "")
    if not rs256_signature_ok(id_token, jwks):
        raise SiwcRefused(
            "the ID token signature did not verify against "
            + JWKS_URI + ". Tokens were not stored.")
    return accept_token_response(
        response, nonce=attempt.nonce, now=now, host_id=attempt.host_id,
        signature_ok=True)


def bind_loopback():
    """A 127.0.0.1 listener on an ephemeral port. The query is one GET."""
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import parse_qs, urlparse

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 - stdlib name
            parsed = urlparse(self.path)
            if parsed.path != CALLBACK_PATH:
                self.send_response(404)
                self.end_headers()
                return
            query = {key: values[0] for key, values in parse_qs(parsed.query).items()}
            self.server.query = query  # type: ignore[attr-defined]
            body = b"You can close this window and return to filesorter."
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, _format, *_args):
            return

    server = HTTPServer(("127.0.0.1", 0), _Handler)
    server.query = None  # type: ignore[attr-defined]
    return server


def post_token_form(url: str, form: Mapping[str, str]) -> dict:
    """POST the token endpoint. Errors name the failure, not the body."""
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen
    data = urlencode(dict(form)).encode("ascii")
    request = Request(
        url, data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        raise SiwcRefused("the token endpoint did not answer") from None
    if not isinstance(payload, dict):
        raise SiwcRefused("the token endpoint did not return an object")
    return payload


def fetch_jwks(get=None) -> dict:
    """The published JWKS document. `get` returns parsed JSON for tests."""
    if get is None:
        from urllib.request import urlopen
        try:
            with urlopen(JWKS_URI, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception:
            raise SiwcRefused("OpenAI's JWKS document could not be read") from None
    else:
        payload = get(JWKS_URI)
    if not isinstance(payload, dict) or not isinstance(payload.get("keys"), list):
        raise SiwcRefused("OpenAI's JWKS document had no keys")
    return payload


ENV_MODEL: str = "OPENAI_SIWC_MODEL"


def registration_document(session: Session, *, model: str | None = None) -> dict:
    """Keychain JSON for one verified session. The access token is a separate item."""
    document = {
        "issued_client_id": session.issued_client_id,
        "host_id": session.host_id,
        "expires_at": session.expires_at,
        "scopes": list(session.scopes),
        "inference_ready": session.inference_ready,
        "subject": session.subject,
    }
    if session.id_token:
        document["id_token"] = session.id_token
    if model:
        document["model"] = model
    return document


def responses_text(answer) -> str:
    """Text from a Responses result. Tests return `{"events": [sse lines]}`."""
    try:
        if isinstance(answer, dict) and isinstance(answer.get("events"), list):
            return read_responses_stream([str(line) for line in answer["events"]])
        if isinstance(answer, str):
            return read_responses_stream(answer.splitlines())
    except SiwcRefused:
        raise
    except Exception:
        raise SiwcRefused("the Responses stream could not be read") from None
    raise SiwcRefused("the Responses transport did not return a stream")


def post_responses(url: str, headers: Mapping[str, str], body: Mapping, *,
                   timeout: float = 90) -> dict:
    """POST the Responses API and return the SSE lines. The error has no token."""
    import urllib.request
    if not str(url).startswith("https://"):
        raise SiwcRefused("the Responses call is https only")
    request = urllib.request.Request(
        url, data=json.dumps(dict(body)).encode("utf-8"),
        headers=dict(headers), method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except Exception as problem:
        code = getattr(problem, "code", None)
        raise SiwcRefused(
            "the Responses call did not answer"
            + (f" (HTTP {code})" if code else "")) from None
    return {"events": raw.splitlines()}


def responses_invoke(*, access_token: str, model_id: str, post,
                     url: str = RESPONSES_URL) -> Callable[[bytes], bytes]:
    """`ModelClient.invoke` for the Responses API. `post` is the only socket."""
    headers = responses_headers(access_token)

    def invoke(payload: bytes) -> bytes:
        try:
            prompt = payload.decode("utf-8")
        except UnicodeDecodeError:
            raise SiwcRefused("the released bytes are not UTF-8") from None
        body = responses_body(model=model_id, prompt=prompt)
        answer = post(url, headers, body)
        return responses_text(answer).encode("utf-8")

    return invoke


class SiwcUnderstanding:
    """Classification through a verified ChatGPT plan token. Locality is cloud."""

    def __init__(self, *, access_token: str, post, model_id: str):
        if not str(access_token).strip():
            raise SiwcRefused("no access token")
        if not str(model_id).strip():
            raise SiwcRefused("no model id for the Responses call")
        self._token = access_token.strip()
        self._post = post
        self._model = model_id.strip()

    def provider_name(self) -> str:
        return "openai-siwc"

    def locality(self) -> str:
        return "cloud"

    def complete(self, request) -> dict:
        from understanding.backoff import RateLimited
        model = (getattr(request, "model_id", "") or self._model).strip()
        body = responses_body(model=model or self._model, prompt=request.prompt)
        try:
            answer = self._post(
                RESPONSES_URL, responses_headers(self._token), body)
        except (RateLimited, SiwcRefused):
            raise
        except Exception:
            raise SiwcRefused("the Responses call did not answer") from None
        text = responses_text(answer)
        return {"choices": [{"finish_reason": "stop",
                             "message": {"content": text}}]}


def refresh_session(*, client_id: str, refresh_token: str, host_id: str,
                    post_form: Callable, jwks: Mapping | None, now: int,
                    previous_scopes: tuple[str, ...] = ()) -> Session:
    """Refresh. A new ID token is verified when the response includes one.

    The old access token is not returned when this raises.
    """
    response = post_form(TOKEN_URL, refresh_form(
        client_id=client_id, refresh_token=refresh_token))
    if not isinstance(response, Mapping):
        raise SiwcRefused("the token endpoint did not return an object")
    response = dict(response)
    response.setdefault("client_id", client_id)
    if str(response.get("client_id") or "") != client_id:
        raise SiwcRefused("the refresh response named a different client id")
    if not response.get("refresh_token"):
        response["refresh_token"] = refresh_token
    if not (response.get("scope") or response.get("scopes")) and previous_scopes:
        response["scope"] = " ".join(previous_scopes)
    id_token = str(response.get("id_token") or "")
    if id_token:
        document = jwks if jwks is not None else fetch_jwks()
        if not rs256_signature_ok(id_token, document):
            raise SiwcRefused(
                "the refreshed ID token signature did not verify against "
                + JWKS_URI + ". Tokens were not stored.")
        claims = _payload(id_token)
        nonce = claims.get("nonce")
        if not isinstance(nonce, str) or not nonce:
            raise SiwcRefused("the refreshed ID token has no nonce")
        return accept_token_response(
            response, nonce=nonce, now=now, host_id=host_id, signature_ok=True)
    access = str(response.get("access_token") or "")
    refresh = str(response.get("refresh_token") or "")
    expires_in = response.get("expires_in")
    if not access or not refresh or not isinstance(expires_in, int) or expires_in < 1:
        raise SiwcRefused("the refresh response has no access token")
    return Session(
        issued_client_id=client_id,
        host_id=host_id,
        access_token=access,
        refresh_token=refresh,
        expires_at=now + expires_in,
        scopes=previous_scopes,
        inference_ready=PLAN_SCOPE in previous_scopes,
        subject="",
        id_token="",
    )


def _write_session(session: Session, *, keychain_run, model: str | None) -> None:
    from readers.model_keychain import (
        SIWC_ACCESS, SIWC_REFRESH, SIWC_REGISTRATION, add_secret,
    )
    document = registration_document(session, model=model)
    add_secret(SIWC_ACCESS, session.access_token, run=keychain_run)
    add_secret(SIWC_REFRESH, session.refresh_token, run=keychain_run)
    add_secret(SIWC_REGISTRATION, json.dumps(document, sort_keys=True), run=keychain_run)


def _model_id(registration: Mapping, environ: Mapping[str, str] | None) -> str:
    named = registration.get("model")
    if isinstance(named, str) and named.strip():
        return named.strip()
    source = os.environ if environ is None else environ
    return (source.get(ENV_MODEL) or "").strip()


def load_ready_access(*, out, keychain_run=None, post_form=None, jwks=None,
                      now: int | None = None,
                      environ: Mapping[str, str] | None = None,
                      ) -> tuple[str, str] | None:
    """A verified, unexpired, inference-ready access token and model id.

    Prints the reason and returns None otherwise. Does not send the old
    access token after a failed refresh, and does not fall through to another
    provider.
    """
    refusal = begin_or_refuse(environ)
    if refusal is not None:
        print(refusal, file=out)
        return None
    if keychain_run is None:
        print("Sign in needs a keychain. Nothing was sent.", file=out)
        return None
    from readers.model_keychain import SIWC_ACCESS, SIWC_REFRESH, SIWC_REGISTRATION, find_secret
    raw = find_secret(SIWC_REGISTRATION, run=keychain_run)
    access = find_secret(SIWC_ACCESS, run=keychain_run)
    refresh = find_secret(SIWC_REFRESH, run=keychain_run)
    if not raw or not access:
        print("Continue with ChatGPT is flagged on and no verified session is "
              "stored. Run: filesorter providers sign-in-chatgpt. An API key "
              "works today. No dossier was sent.", file=out)
        return None
    try:
        registration = json.loads(raw)
    except json.JSONDecodeError:
        print("The stored ChatGPT sign-in could not be read. Sign in again. "
              "No dossier was sent.", file=out)
        return None
    if not isinstance(registration, dict):
        print("The stored ChatGPT sign-in could not be read. Sign in again. "
              "No dossier was sent.", file=out)
        return None
    if not registration.get("inference_ready"):
        print("chatgpt.tokens.use.direct was not granted, so plan usage will "
              "not be called. Use an API key.", file=out)
        return None
    model = _model_id(registration, environ)
    if not model:
        print("No ChatGPT model was consulted. Pass --model to "
              "sign-in-chatgpt or set OPENAI_SIWC_MODEL. An API key works today.",
              file=out)
        return None
    import time
    current = int(time.time()) if now is None else int(now)
    try:
        expires_at = int(registration.get("expires_at") or 0)
    except (TypeError, ValueError):
        expires_at = 0
    if current >= expires_at:
        client_id = str(registration.get("issued_client_id") or "")
        host_id = str(registration.get("host_id") or "")
        scopes = registration.get("scopes") or []
        previous = tuple(scopes) if isinstance(scopes, list) else tuple(str(scopes).split())
        if not refresh or not client_id:
            print(REAUTH_MESSAGE, file=out)
            return None
        try:
            session = refresh_session(
                client_id=client_id, refresh_token=refresh, host_id=host_id,
                post_form=post_form or post_token_form, jwks=jwks, now=current,
                previous_scopes=previous)
        except SiwcRefused as problem:
            text = str(problem)
            if access and access in text:
                text = REAUTH_MESSAGE
            print(text, file=out)
            return None
        except Exception:
            print(REAUTH_MESSAGE, file=out)
            return None
        if not session.inference_ready:
            print("chatgpt.tokens.use.direct was not granted, so plan usage "
                  "will not be called. Use an API key.", file=out)
            return None
        _write_session(session, keychain_run=keychain_run, model=model)
        access = session.access_token
    return access, model


def siwc_cloud_routing(*, out, tier_of_call_site, max_response_tokens: int,
                       keychain_run=None, post=None, post_form=None, jwks=None,
                       now: int | None = None,
                       environ: Mapping[str, str] | None = None):
    """A TierRouting for a verified ChatGPT session, or None after a sentence.

    `max_response_tokens` is accepted so the call site matches the other
    routes. The Responses body this flow sends is the one the
    models-and-inference page requires, and that body has no token ceiling.
    """
    del max_response_tokens
    ready = load_ready_access(
        out=out, keychain_run=keychain_run, post_form=post_form, jwks=jwks,
        now=now, environ=environ)
    if ready is None:
        return None
    access, model = ready
    from privacy.release import ModelTarget
    from llm_harness.transport import ModelClient
    from readers.model_routing import TIERS, TierRouting
    target = ModelTarget(locality="cloud", model_id=model, provider="openai")
    invoke = responses_invoke(
        access_token=access, model_id=model, post=post or post_responses)
    client = ModelClient(model_target=target, invoke=invoke)
    return TierRouting(
        tier_of_call_site=tier_of_call_site,
        client_of_tier={tier: client for tier in TIERS})
