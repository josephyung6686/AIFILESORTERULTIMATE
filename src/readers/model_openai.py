# src/readers/model_openai.py
"""OpenAI API-key calls, and the same JSON shape for any OpenAI-compatible URL.

Chat Completions is the request the API-key lane sends. Sign in with ChatGPT
does not use this module: that lane is the Responses API in `model_siwc`.

The key arrives already resolved. This module does not read the environment
or the keychain, and it does not put the key in an exception.
"""
from __future__ import annotations

import json
from typing import Callable
from urllib.parse import urlparse

from privacy.release import ModelTarget

from llm_harness.transport import ModelClient
from readers.model_routing import FAST, LOGIC, REASONING, TIERS, TierRouting

PROVIDER: str = "openai"
COMPATIBLE: str = "openai-compatible"
CLOUD: str = "cloud"

#: Platform docs: https://platform.openai.com/docs/api-reference/chat/create
DEFAULT_BASE_URL: str = "https://api.openai.com/v1"
CHAT_PATH: str = "/chat/completions"

ENV_KEY: str = "OPENAI_API_KEY"
ENV_MODEL: str = "OPENAI_MODEL"
ENV_COMPATIBLE_KEY: str = "OPENAI_COMPATIBLE_API_KEY"
ENV_COMPATIBLE_BASE: str = "OPENAI_COMPATIBLE_BASE_URL"
ENV_COMPATIBLE_MODEL: str = "OPENAI_COMPATIBLE_MODEL"


class OpenAIRequestRefused(RuntimeError):
    """The request was not sent."""


def chat_url(base_url: str) -> str:
    if not isinstance(base_url, str) or not base_url.strip():
        raise OpenAIRequestRefused("an OpenAI-compatible call needs a base URL")
    base = base_url.strip().rstrip("/")
    parsed = urlparse(base)
    if parsed.scheme != "https":
        raise OpenAIRequestRefused(
            "the API-key endpoint must be https. A non-https URL would send "
            "the key in the clear, so the call was not made.")
    if not parsed.netloc:
        raise OpenAIRequestRefused("the base URL has no host")
    return base + CHAT_PATH


def chat_headers(api_key: str) -> dict[str, str]:
    if not isinstance(api_key, str) or not api_key.strip():
        raise OpenAIRequestRefused("no API key was injected")
    return {
        "Authorization": "Bearer " + api_key.strip(),
        "Content-Type": "application/json",
    }


def chat_body(*, model_id: str, max_tokens: int, prompt: str) -> dict:
    """One Chat Completions body. JSON mode, one answer, no stored log on our side.

    OpenAI's JSON mode requires the prompt to mention JSON. The same precondition
    DeepSeek states is checked here so an empty reply is not blamed on the model.
    """
    if not isinstance(model_id, str) or not model_id.strip():
        raise OpenAIRequestRefused(
            f"no model id. Set {ENV_MODEL} or pass one. This module does not "
            "pick a model.")
    if not isinstance(max_tokens, int) or max_tokens < 1:
        raise OpenAIRequestRefused("max_tokens must be a positive integer")
    if "json" not in prompt.lower():
        raise OpenAIRequestRefused(
            "JSON mode is set and the prompt never contains the word 'json'. "
            "The call was not sent.")
    return {
        "model": model_id.strip(),
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
        "n": 1,
    }


def chat_text(payload: dict) -> str:
    """The assistant message, or a refusal. Never a partial choice."""
    choices = payload.get("choices")
    if not isinstance(choices, list) or len(choices) != 1:
        raise OpenAIRequestRefused(
            "the response did not contain exactly one choice")
    choice = choices[0]
    if not isinstance(choice, dict):
        raise OpenAIRequestRefused("the choice was not an object")
    reason = choice.get("finish_reason")
    if reason == "length":
        raise OpenAIRequestRefused(
            "the answer was cut off at the token ceiling (finish_reason=length)")
    if reason == "content_filter":
        raise OpenAIRequestRefused(
            "the provider declined (finish_reason=content_filter)")
    if reason != "stop":
        raise OpenAIRequestRefused(
            f"finish_reason is {reason!r}; the only completed answer is 'stop'")
    message = choice.get("message") or {}
    text = message.get("content") if isinstance(message, dict) else None
    if not isinstance(text, str) or not text.strip():
        raise OpenAIRequestRefused("the response carried no message content")
    return text


def openai_invoke(*, api_key: str, base_url: str, model_target: ModelTarget,
                  max_response_tokens: int, provider: str,
                  post: Callable[..., dict]) -> Callable[[bytes], bytes]:
    """`ModelClient.invoke`. `post` is the only socket, and tests replace it."""
    if model_target.provider != provider:
        raise OpenAIRequestRefused(
            f"model_target.provider is {model_target.provider!r}; this call "
            f"is {provider!r}")
    if model_target.locality != CLOUD:
        raise OpenAIRequestRefused(
            f"model_target.locality is {model_target.locality!r}; an API call "
            f"is {CLOUD!r}")
    if model_target.model_id.strip() == "":
        raise OpenAIRequestRefused("model_target.model_id is empty")
    url = chat_url(base_url)
    headers = chat_headers(api_key)
    model_id = model_target.model_id

    def invoke(payload: bytes) -> bytes:
        try:
            prompt = payload.decode("utf-8")
        except UnicodeDecodeError as problem:
            raise OpenAIRequestRefused(
                "the released bytes are not UTF-8") from problem
        body = chat_body(model_id=model_id, max_tokens=max_response_tokens,
                         prompt=prompt)
        answer = post(url, headers, body)
        if not isinstance(answer, dict):
            raise OpenAIRequestRefused("the transport did not return an object")
        return chat_text(answer).encode("utf-8")

    return invoke


def one_model_routing(*, api_key: str, base_url: str, model_id: str,
                      provider: str, tier_of_call_site,
                      max_response_tokens: int,
                      post: Callable[..., dict]) -> TierRouting:
    """One named model for every tier. The screen says so; it is not a downgrade.

    The same rule `ollama_routing` uses when the machine has one model: the
    person named it, and every call site is told that name.
    """
    target = ModelTarget(locality=CLOUD, model_id=model_id, provider=provider)
    invoke = openai_invoke(
        api_key=api_key, base_url=base_url, model_target=target,
        max_response_tokens=max_response_tokens, provider=provider, post=post)
    client = ModelClient(model_target=target, invoke=invoke)
    return TierRouting(
        tier_of_call_site=tier_of_call_site,
        client_of_tier={tier: client for tier in TIERS})


def describe_request(*, provider: str, base_url: str, model_id: str) -> dict:
    """What a dry-run may print. No key, no prompt, no file bytes."""
    return {
        "provider": provider,
        "endpoint": chat_url(base_url) if base_url else "",
        "model": model_id,
        "shape": "chat.completions",
        "sent": False,
    }


def encode_body(body: dict) -> bytes:
    return json.dumps(body).encode("utf-8")


def post_json(url: str, headers: dict, body: dict, *, timeout: float = 90) -> dict:
    """One HTTPS POST. The error names the status, never the key or the body."""
    import urllib.request
    request = urllib.request.Request(
        url, data=encode_body(body), headers=dict(headers), method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            parsed = json.loads(response.read().decode("utf-8"))
    except Exception as problem:
        code = getattr(problem, "code", None)
        raise OpenAIRequestRefused(
            "the provider did not answer"
            + (f" (HTTP {code})" if code else "")) from None
    if not isinstance(parsed, dict):
        raise OpenAIRequestRefused("the provider's reply was not a JSON object")
    return parsed


# Re-exported so a reader of this module sees the tier names it fills.
__all__ = ["PROVIDER", "COMPATIBLE", "REASONING", "LOGIC", "FAST"]
