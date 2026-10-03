"""Deterministic BYOK provider routing (everyday-product Task 1)."""
from __future__ import annotations

import pytest

from assistant.provider import resolve_provider
from assistant.trust import trust_facts_for


@pytest.fixture(autouse=True)
def _no_dotenv(monkeypatch):
    monkeypatch.setattr("assistant.provider.load_dotenv", lambda *a, **k: None)


def _clear_provider_env(monkeypatch) -> None:
    for key in (
        "ASSISTANT_PROVIDER",
        "DEEPSEEK_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "DEEPSEEK_BASE_URL",
        "OPENAI_BASE_URL",
        "ANTHROPIC_BASE_URL",
        "DEEPSEEK_MODEL_FAST",
        "DEEPSEEK_MODEL_LOGIC",
        "OPENAI_MODEL",
        "ANTHROPIC_MODEL",
    ):
        monkeypatch.delenv(key, raising=False)


def test_deepseek_only(monkeypatch):
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-deepseek")
    cfg = resolve_provider()
    assert cfg.provider == "deepseek"
    assert "deepseek" in cfg.base_url.lower()
    assert cfg.model == "deepseek-chat"
    assert cfg.api_key == "sk-deepseek"
    assert trust_facts_for(cfg.provider).provider == "deepseek"


def test_openai_only(monkeypatch):
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    cfg = resolve_provider()
    assert cfg.provider == "openai"
    assert "openai.com" in cfg.base_url.lower()
    assert "deepseek" not in cfg.base_url.lower()
    assert cfg.model != "deepseek-chat"
    assert cfg.api_key == "sk-openai"
    assert trust_facts_for(cfg.provider).provider == "openai"


def test_anthropic_only(monkeypatch):
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-anthropic")
    cfg = resolve_provider()
    assert cfg.provider == "anthropic"
    assert "anthropic" in cfg.base_url.lower()
    assert cfg.api_key == "sk-anthropic"
    assert trust_facts_for(cfg.provider).provider == "anthropic"


def test_explicit_provider_missing_key(monkeypatch):
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("ASSISTANT_PROVIDER", "openai")
    with pytest.raises(RuntimeError, match="ASSISTANT_PROVIDER=openai"):
        resolve_provider()


def test_multiple_keys_with_explicit_provider(monkeypatch):
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-deepseek")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-anthropic")
    monkeypatch.setenv("ASSISTANT_PROVIDER", "openai")
    cfg = resolve_provider()
    assert cfg.provider == "openai"
    assert cfg.api_key == "sk-openai"
    assert "openai.com" in cfg.base_url.lower()


def test_no_keys(monkeypatch):
    _clear_provider_env(monkeypatch)
    with pytest.raises(RuntimeError, match="No API key|Nothing was sent"):
        resolve_provider()


def test_ambiguous_multiple_keys_refuse(monkeypatch):
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-deepseek")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    with pytest.raises(RuntimeError, match="ASSISTANT_PROVIDER"):
        resolve_provider()


def test_trust_refuses_unknown_provider():
    with pytest.raises(RuntimeError, match="Unknown provider"):
        trust_facts_for("not-a-real-provider")
