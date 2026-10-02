"""Optional on-device model adapter (P2 option) + local-only capability probe.

When Apple FM is unavailable, local-only sessions still answer find/list
questions from the hybrid index (no cloud). Never silently falls back to
cloud with held bodies.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LocalModelStatus:
    available: bool
    reason: str
    supports_tools: bool = False
    index_find: bool = True  # hybrid FTS/vector find always local


def probe_apple_foundation_models() -> LocalModelStatus:
    """Detect Apple Foundation Models without importing private APIs hard."""
    try:
        import platform
        if platform.system() != "Darwin":
            return LocalModelStatus(
                available=False,
                reason="not macOS",
                index_find=True,
            )
    except Exception:
        return LocalModelStatus(
            available=False, reason="platform probe failed", index_find=True)
    # Framework availability varies by OS version; refuse to claim ready
    # until a real adapter is wired and tested.
    return LocalModelStatus(
        available=False,
        reason=(
            "Apple Foundation Models adapter not wired yet — "
            "local-only uses hybrid index find (no cloud)"
        ),
        supports_tools=False,
        index_find=True,
    )


def require_local_or_refuse(*, local_only: bool) -> LocalModelStatus:
    status = probe_apple_foundation_models()
    if not local_only:
        return status
    if status.available:
        return status
    # Index-find is the supported local-only path today.
    if status.index_find:
        return LocalModelStatus(
            available=False,
            reason=(
                "local-only: Apple FM not wired — "
                "using index-only find (no cloud)"
            ),
            supports_tools=False,
            index_find=True,
        )
    return LocalModelStatus(
        available=False,
        reason=f"local-only session refused: {status.reason}",
        supports_tools=False,
        index_find=False,
    )


def capability_lines() -> list[str]:
    """Human-readable probe for CLI --show-local-capability."""
    st = probe_apple_foundation_models()
    return [
        f"apple_foundation_models: {'yes' if st.available else 'no'}",
        f"index_find_local: {'yes' if st.index_find else 'no'}",
        f"reason: {st.reason}",
    ]
