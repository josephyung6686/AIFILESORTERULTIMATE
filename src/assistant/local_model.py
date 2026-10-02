"""Optional on-device model adapter (P2 option).

When unavailable, callers keep using BYOK cloud. Never silently falls back
to cloud with held bodies.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LocalModelStatus:
    available: bool
    reason: str
    supports_tools: bool = False


def probe_apple_foundation_models() -> LocalModelStatus:
    """Detect Apple Foundation Models without importing private APIs hard."""
    try:
        import platform
        if platform.system() != "Darwin":
            return LocalModelStatus(
                available=False, reason="not macOS")
    except Exception:
        return LocalModelStatus(available=False, reason="platform probe failed")
    # Framework availability varies by OS version; refuse to claim ready
    # until a real adapter is wired and tested.
    return LocalModelStatus(
        available=False,
        reason=(
            "Apple Foundation Models adapter not wired yet — "
            "use BYOK or wait for P2 local-model ship"
        ),
        supports_tools=False,
    )


def require_local_or_refuse(*, local_only: bool) -> LocalModelStatus:
    status = probe_apple_foundation_models()
    if local_only and not status.available:
        return LocalModelStatus(
            available=False,
            reason=f"local-only session refused: {status.reason}",
            supports_tools=False,
        )
    return status
