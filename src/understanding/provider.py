# src/understanding/provider.py
"""The provider interface the understanding pass calls.

DeepSeek, any OpenAI-compatible API key, Anthropic's Messages API, a
verified ChatGPT plan token, the unmodified Claude Code binary, and a
local Ollama on loopback. The composition root picks the adapter. This
pass does not scrape a login, and it does not read Claude.ai or Codex
tokens. Those limits are in `docs/model-providers.md`.

The key is not a field of the request, so a log of the request cannot
contain it. Adapters that speak HTTP live under `readers/model_` because
that is where a socket is allowed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class CompletionRequest:
    model_id: str
    prompt: str
    max_tokens: int
    thinking: str = "disabled"


class ModelProvider(Protocol):
    def provider_name(self) -> str: ...

    def locality(self) -> str: ...

    def complete(self, request: CompletionRequest) -> dict: ...


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    """Names and a base URL. The key is looked up by the caller, not stored."""

    provider: str
    model_fast: str
    model_logic: str
    model_reasoning: str
    base_url: str
    locality: str


def config_from_env(environ: dict[str, str]) -> ProviderConfig:
    """DeepSeek when its key name is set, otherwise local Ollama if named.

    An OpenAI-compatible endpoint is selected when OPENAI_COMPATIBLE_BASE_URL
    is set. The key itself is not copied into this object.
    """
    if (environ.get("OPENAI_COMPATIBLE_BASE_URL") or "").startswith("https://"):
        return ProviderConfig(
            provider="openai-compatible",
            model_fast=environ.get("OPENAI_COMPATIBLE_MODEL", ""),
            model_logic=environ.get("OPENAI_COMPATIBLE_MODEL", ""),
            model_reasoning=environ.get("OPENAI_COMPATIBLE_MODEL", ""),
            base_url=environ["OPENAI_COMPATIBLE_BASE_URL"].rstrip("/"),
            locality="cloud",
        )
    if (environ.get("DEEPSEEK_API_KEY") or "").strip() or environ.get("DEEPSEEK_MODEL_FAST"):
        return ProviderConfig(
            provider="deepseek",
            model_fast=environ.get("DEEPSEEK_MODEL_FAST", ""),
            model_logic=environ.get("DEEPSEEK_MODEL_LOGIC", ""),
            model_reasoning=environ.get("DEEPSEEK_MODEL_REASONING", ""),
            base_url=(environ.get("DEEPSEEK_BASE_URL") or "https://api.deepseek.com").rstrip("/"),
            locality="cloud",
        )
    return ProviderConfig(
        provider="ollama",
        model_fast=environ.get("GRAPH_AGENT_LOCAL_MODEL", ""),
        model_logic=environ.get("GRAPH_AGENT_LOCAL_MODEL", ""),
        model_reasoning=environ.get("GRAPH_AGENT_LOCAL_MODEL", ""),
        base_url=(environ.get("OLLAMA_BASE_URL") or "http://127.0.0.1:11434").rstrip("/"),
        locality="local",
    )


def model_for_role(config: ProviderConfig, role: str) -> str:
    if role == "fast":
        return config.model_fast
    if role == "logic":
        return config.model_logic
    if role == "reasoning":
        return config.model_reasoning
    raise ValueError(
        f"{role!r} is not a role. Classification uses fast, grouping uses "
        "logic, and onboarding questions use reasoning.")
