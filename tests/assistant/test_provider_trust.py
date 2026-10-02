"""Addendum A4 — per-provider trust copy, no fake 30-day for DeepSeek."""
from __future__ import annotations

from assistant.trust import onboarding_lines, trust_facts_for


def test_deepseek_not_openai_thirty_days():
    f = trust_facts_for("deepseek")
    assert "China" in f.data_location or "PRC" in f.data_location
    assert "30" not in f.retention or "no published" in f.retention.lower()
    assert f.zdr_available is False
    text = "\n".join(onboarding_lines("deepseek"))
    assert "OpenAI" not in text
    assert "Anthropic" not in text


def test_openai_has_thirty_day_note_when_selected():
    f = trust_facts_for("openai")
    assert "30" in f.retention


def test_local_mode():
    f = trust_facts_for("local")
    assert f.zdr_available is True
    assert "device" in f.data_location.lower()
