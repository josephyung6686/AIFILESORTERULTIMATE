# src/understanding/catalog.py
"""Resolve a configured model id against a `/models` catalog.

The catalog is handed in. This module does not open a socket. A name the
catalog does not list is an error that names that id and the ids that were
listed. It is not a silent swap onto another tier.

`deepseek-v4-flash` and `deepseek-flash` are one pair. A live catalog listed
`deepseek-flash`. The template and one machine's environment have used
`deepseek-v4-flash`. When the configured id is one of the pair and only the
other is listed, the listed one is used and the resolution says so. When
neither is listed, the error names the configured id.
"""
from __future__ import annotations

FLASH_IDS: frozenset[str] = frozenset({"deepseek-v4-flash", "deepseek-flash"})


class ModelIdNotListed(ValueError):
    """The configured id is not in the catalog. The message names it."""


def resolve_model_id(configured: str, listed: set[str] | frozenset[str]) -> str:
    if not isinstance(configured, str) or not configured.strip():
        raise ModelIdNotListed(
            "no model id was configured. Set DEEPSEEK_MODEL_FAST, "
            "DEEPSEEK_MODEL_LOGIC, or DEEPSEEK_MODEL_REASONING. "
            "This does not pick one.")
    name = configured.strip()
    known = {item.strip() for item in listed if isinstance(item, str) and item.strip()}
    if name in known:
        return name
    if name in FLASH_IDS:
        for candidate in ("deepseek-flash", "deepseek-v4-flash"):
            if candidate in known:
                return candidate
    shown = ", ".join(sorted(known)) or "(the catalog was empty)"
    raise ModelIdNotListed(
        f"{name!r} is not in the provider's /models list. "
        f"The ids it lists are: {shown}.")
