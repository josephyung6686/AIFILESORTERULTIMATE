"""Local-only mode + capability probe."""
from __future__ import annotations

from assistant.local_model import (
    capability_lines,
    probe_apple_foundation_models,
    probe_local_generation,
    require_local_or_refuse,
)


def test_local_probe_does_not_claim_ready_without_backend():
    status = probe_apple_foundation_models()
    # May be available on some Macs; if not, must not crash.
    assert status.index_find is True


def test_local_only_session_index_fallback():
    status = require_local_or_refuse(local_only=True)
    if status.available:
        assert status.supports_tools or status.backend == "apple_fm"
    else:
        assert status.index_find is True
        assert "index-only" in status.reason or "local-only" in status.reason


def test_capability_lines_shape():
    lines = capability_lines()
    assert any(l.startswith("apple_foundation_models:") for l in lines)
    assert any(l.startswith("local_generation:") for l in lines)
    assert any(l.startswith("index_find_local:") for l in lines)


def test_probe_local_generation_never_raises():
    st = probe_local_generation()
    assert st.backend in ("apple_fm", "ollama_compat", "none")
