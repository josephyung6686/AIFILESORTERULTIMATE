"""Local-only mode refuses cleanly when adapter missing."""
from __future__ import annotations

from assistant.local_model import probe_apple_foundation_models, require_local_or_refuse


def test_local_probe_does_not_claim_ready():
    status = probe_apple_foundation_models()
    # Until wired, must not claim available=True
    assert status.available is False


def test_local_only_session_refuses():
    status = require_local_or_refuse(local_only=True)
    assert status.available is False
    assert "refused" in status.reason or "not wired" in status.reason
