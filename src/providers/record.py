# src/providers/record.py
"""Which AI lane this folder uses, stored in the profile record. No secrets.

The order is the profile questions, then this step, then a scan. A missing
choice does not block a scan: the deterministic path still runs, and a
DeepSeek key in the environment remains the cloud default. The choice names
a lane and a provider. The key, when there is one, stays in the environment
or the keychain.
"""
from __future__ import annotations

import json
import sqlite3

from questions.profile import apply_profile
from questions.store import profile_wording

#: Profile questions, then the provider, then the scan. The provider command
#: is that middle step.
STEP_ORDER: tuple[str, ...] = ("profile", "ai_provider", "scan")

LANES: tuple[str, ...] = ("managed", "subscription", "byok", "none")
BYOK_PROVIDERS: frozenset[str] = frozenset({
    "deepseek", "openai", "anthropic", "openai-compatible",
})

#: A prefix, because `json.dumps(..., sort_keys=True)` does not start with `lane`
#: once a compatible provider also stores `base_url`.
MARKER: str = "filesorter-provider "


class ProviderChoiceRefused(ValueError):
    """The choice is not one this product can store."""


def explain_order() -> str:
    return (
        "AI provider is the step after the profile questions and before the "
        "first scan. Nothing in this step is sent off the device. A scan with "
        "no choice here still sorts from the files alone, and DeepSeek stays "
        "the cloud default when its key is set."
    )


def validate_choice(choice: dict) -> dict:
    if not isinstance(choice, dict):
        raise ProviderChoiceRefused("a provider choice is an object")
    lane = choice.get("lane")
    if lane not in LANES:
        raise ProviderChoiceRefused(
            f"lane {lane!r} is not one of {LANES}")
    if lane == "managed":
        raise ProviderChoiceRefused(
            "the included plan is coming later. There is no backend to select.")
    provider = choice.get("provider")
    if lane == "none":
        if provider not in (None, "none"):
            raise ProviderChoiceRefused(
                "lane none does not name a cloud provider")
        return {"lane": "none", "provider": "none", "credential": "none",
                "provenance": choice.get("provenance") or "answered"}
    if lane == "subscription":
        if provider == "anthropic":
            raise ProviderChoiceRefused(
                "not available — Anthropic policy. Use an API key or Claude Code.")
        if provider != "openai":
            raise ProviderChoiceRefused(
                "the only subscription lane implemented is OpenAI, and it stays "
                "off until FILESORTER_OPENAI_SIWC=1")
    if lane == "byok" and provider not in BYOK_PROVIDERS:
        raise ProviderChoiceRefused(
            f"{provider!r} is not a BYOK provider. The set is "
            f"{sorted(BYOK_PROVIDERS)}.")
    credential = choice.get("credential") or "env"
    if credential not in ("env", "keychain"):
        raise ProviderChoiceRefused(
            "credential is env or keychain. The secret itself is not stored here.")
    stored = {
        "lane": lane,
        "provider": provider,
        "credential": credential,
        "provenance": choice.get("provenance") or "answered",
    }
    if provider == "openai-compatible":
        base = choice.get("base_url")
        if not isinstance(base, str) or not base.startswith("https://"):
            raise ProviderChoiceRefused(
                "an OpenAI-compatible provider needs an https base_url")
        stored["base_url"] = base.rstrip("/")
    model = choice.get("model")
    if isinstance(model, str) and model.strip():
        stored["model"] = model.strip()
    return stored


def store_provider_choice(conn: sqlite3.Connection, choice: dict, *,
                          user_id: str, recorded_at: str) -> dict:
    stored = validate_choice(choice)
    apply_profile(
        conn, user_id=user_id, recorded_at=recorded_at,
        wording=(f"provider={MARKER}{json.dumps(stored, sort_keys=True)}",))
    return stored


def load_provider_choice(conn: sqlite3.Connection) -> dict | None:
    """The latest stored choice, or None when this database has none.

    A database that has not created the question tables yet is treated as no
    choice, which is the scan's ordinary state.
    """
    try:
        sentences = profile_wording(conn)
    except sqlite3.OperationalError:
        return None
    found: dict | None = None
    for sentence in sentences:
        if not isinstance(sentence, str) or not sentence.startswith(MARKER):
            continue
        try:
            parsed = json.loads(sentence[len(MARKER):])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict) and parsed.get("lane"):
            found = parsed
    return found
