# src/readers/model_understanding_http.py
"""HTTP adapters for the understanding pass. Tests inject `post`.

DeepSeek chat completions with thinking disabled. OpenAI-compatible chat
completions. Ollama on loopback only. The error text never includes the key.
"""
from __future__ import annotations

import json
from urllib.parse import urlparse

from understanding.backoff import RateLimited
from understanding.provider import CompletionRequest, ModelProvider


class ProviderError(RuntimeError):
    """The provider did not answer. The message has no key in it."""


def _host_is_loopback(base_url: str) -> bool:
    parsed = urlparse(base_url)
    return parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost"}


class DeepSeekUnderstanding:
    """FAST classification goes through this. Thinking is off on every call."""

    def __init__(self, *, api_key: str, base_url: str, post):
        if not api_key.strip():
            raise ProviderError("no DeepSeek API key was injected")
        if not base_url.startswith("https://"):
            raise ProviderError("the DeepSeek endpoint must be https")
        self._key = api_key
        self._base = base_url.rstrip("/")
        self._post = post

    def provider_name(self) -> str:
        return "deepseek"

    def locality(self) -> str:
        return "cloud"

    def complete(self, request: CompletionRequest) -> dict:
        body = {
            "model": request.model_id,
            "messages": [{"role": "user", "content": request.prompt}],
            "max_tokens": request.max_tokens,
            # json_schema on chat completions returns HTTP 400 for these ids.
            "response_format": {"type": "json_object"},
            "thinking": {"type": "disabled"},
        }
        if "json" not in request.prompt.lower():
            raise ProviderError("the prompt does not ask for json")
        try:
            return self._post(
                self._base + "/chat/completions",
                {"Authorization": "Bearer " + self._key,
                 "Content-Type": "application/json"},
                body)
        except (ProviderError, RateLimited):
            raise
        except Exception:
            raise ProviderError("the provider did not answer") from None


class OpenAICompatibleUnderstanding:
    def __init__(self, *, api_key: str, base_url: str, post):
        if not api_key.strip():
            raise ProviderError("no API key was injected")
        if not str(base_url).startswith("https://"):
            raise ProviderError("an OpenAI-compatible endpoint must be https")
        self._key = api_key
        self._base = base_url.rstrip("/")
        self._post = post

    def provider_name(self) -> str:
        return "openai-compatible"

    def locality(self) -> str:
        return "cloud"

    def complete(self, request: CompletionRequest) -> dict:
        body = {
            "model": request.model_id,
            "messages": [{"role": "user", "content": request.prompt}],
            "max_tokens": request.max_tokens,
            "response_format": {"type": "json_object"},
        }
        try:
            return self._post(
                self._base + "/chat/completions",
                {"Authorization": "Bearer " + self._key,
                 "Content-Type": "application/json"},
                body)
        except (ProviderError, RateLimited):
            raise
        except Exception:
            raise ProviderError("the provider did not answer") from None


class OllamaUnderstanding:
    def __init__(self, *, base_url: str, post):
        if not _host_is_loopback(base_url):
            raise ProviderError(
                "a local model is loopback only. This URL is not 127.0.0.1 "
                "or localhost.")
        self._base = base_url.rstrip("/")
        self._post = post

    def provider_name(self) -> str:
        return "ollama"

    def locality(self) -> str:
        return "local"

    def complete(self, request: CompletionRequest) -> dict:
        # The understanding pass reads a chat-completion shape. The adapter
        # asks Ollama and returns that shape so the rest of the pass is one
        # reader. `think` false is the local equivalent of thinking off.
        try:
            raw = self._post(
                self._base + "/api/chat",
                {"Content-Type": "application/json"},
                {"model": request.model_id,
                 "messages": [{"role": "user", "content": request.prompt}],
                 "stream": False, "think": False})
        except (ProviderError, RateLimited):
            raise
        except Exception:
            raise ProviderError("the local model did not answer") from None
        message = raw.get("message") if isinstance(raw, dict) else None
        content = ""
        if isinstance(message, dict):
            content = message.get("content") or ""
        return {"choices": [{"finish_reason": "stop",
                             "message": {"content": content}}]}


def list_model_ids(base_url: str, api_key: str, *, get) -> set[str]:
    """GET {base}/models. `get` returns the parsed JSON. No key in the error."""
    if not base_url.startswith("https://"):
        raise ProviderError("the model list endpoint must be https")
    payload = get(
        base_url.rstrip("/") + "/models",
        {"Authorization": "Bearer " + api_key})
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, list):
        raise ProviderError("the /models response had no data list")
    ids = set()
    for item in data:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            ids.add(item["id"])
    return ids


def get_json(url: str, headers: dict, *, timeout: float = 30) -> dict:
    import urllib.request
    request = urllib.request.Request(url, headers=dict(headers))
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            parsed = json.loads(response.read().decode("utf-8"))
    except Exception:
        raise ProviderError("the model list could not be read") from None
    if not isinstance(parsed, dict):
        raise ProviderError("the model list was not a JSON object")
    return parsed


def status_error(code: int, retry_after: str | None = None) -> ProviderError:
    """An HTTP failure the caller can show. The message has no key and no body."""
    if code == 429:
        try:
            wait = float(retry_after) if retry_after else 1.0
        except (TypeError, ValueError):
            wait = 1.0
        if wait < 0:
            wait = 1.0
        return RateLimited(min(wait, 60.0))
    return ProviderError(f"the provider did not answer (HTTP {code})")


def post_json(url: str, headers: dict, body: dict, *, timeout: float = 90) -> dict:
    import urllib.error
    import urllib.request
    request = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"), headers=dict(headers),
        method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            parsed = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as problem:
        header = None
        if problem.headers is not None:
            header = problem.headers.get("Retry-After")
        raise status_error(int(problem.code), header) from None
    except Exception as problem:
        code = getattr(problem, "code", None)
        if code:
            raise status_error(int(code)) from None
        raise ProviderError("the provider did not answer") from None
    if not isinstance(parsed, dict):
        raise ProviderError("the provider's reply was not a JSON object")
    return parsed


def _as_provider(provider: ModelProvider) -> ModelProvider:
    return provider
