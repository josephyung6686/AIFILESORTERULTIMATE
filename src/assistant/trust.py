"""Per-provider onboarding trust facts (Addendum A4).

Never claim OpenAI/Anthropic retention for DeepSeek.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderTrustFacts:
    provider: str
    data_location: str
    retention: str
    training_note: str
    policy_url: str
    zdr_available: bool


TRUST_BY_PROVIDER: dict[str, ProviderTrustFacts] = {
    "deepseek": ProviderTrustFacts(
        provider="deepseek",
        data_location="People's Republic of China (Hangzhou DeepSeek)",
        retention=(
            "As long as necessary for service/legal/business — "
            "no published fixed API day-count"
        ),
        training_note=(
            "Inputs may be used to improve models unless you opt out of "
            "training via DeepSeek account controls"
        ),
        policy_url=(
            "https://cdn.deepseek.com/policies/en-US/"
            "deepseek-privacy-policy.html"
        ),
        zdr_available=False,
    ),
    "openai": ProviderTrustFacts(
        provider="openai",
        data_location="Per OpenAI API data residency / account settings",
        retention="Abuse-monitoring logs retained up to ~30 days (API docs)",
        training_note="API inputs not used for training by default (API)",
        policy_url="https://openai.com/policies/api-data-usage-policies",
        zdr_available=False,  # typical BYOK student: no ZDR agreement
    ),
    "anthropic": ProviderTrustFacts(
        provider="anthropic",
        data_location="Per Anthropic API terms",
        retention=(
            "API inputs/outputs deleted within ~30 days; Covered Models "
            "may require 30-day retention even under ZDR"
        ),
        training_note="See Anthropic commercial terms for training use",
        policy_url="https://www.anthropic.com/legal/privacy",
        zdr_available=False,
    ),
    "local": ProviderTrustFacts(
        provider="local",
        data_location="This device only",
        retention="No cloud body egress for local-only sessions",
        training_note="N/A — on-device",
        policy_url="",
        zdr_available=True,
    ),
}


def trust_facts_for(provider: str) -> ProviderTrustFacts:
    key = (provider or "deepseek").strip().lower()
    if key not in TRUST_BY_PROVIDER:
        # Unknown provider: refuse to invent OpenAI-style 30-day copy.
        return ProviderTrustFacts(
            provider=key,
            data_location="Unknown — check your provider's policy",
            retention="Unknown — do not assume 30 days",
            training_note="Unknown — review provider terms before sending files",
            policy_url="",
            zdr_available=False,
        )
    return TRUST_BY_PROVIDER[key]


def onboarding_lines(provider: str) -> list[str]:
    f = trust_facts_for(provider)
    lines = [
        f"Provider: {f.provider}",
        f"Data location: {f.data_location}",
        f"Retention: {f.retention}",
        f"Training: {f.training_note}",
        f"ZDR for typical BYOK: {'yes' if f.zdr_available else 'not available'}",
    ]
    if f.policy_url:
        lines.append(f"Policy: {f.policy_url}")
    return lines
