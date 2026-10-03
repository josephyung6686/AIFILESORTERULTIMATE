"""On-device / local-only model adapter.

Order of preference for ``local_only`` generation:
1. Apple Foundation Models (Swift probe) when available
2. OpenAI-compatible local endpoint (Ollama / MLX) via ASSISTANT_LOCAL_BASE_URL
3. Hybrid index find only (no cloud) — always available

Never silently falls back to cloud BYOK when local_only=True.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LocalModelStatus:
    available: bool
    reason: str
    supports_tools: bool = False
    index_find: bool = True
    backend: str = "none"  # apple_fm | ollama_compat | none


def _swift_probe() -> LocalModelStatus | None:
    """Run tools/apple_fm_probe.swift when swiftc/swift is present."""
    root = Path(__file__).resolve().parents[2]
    script = root / "tools" / "apple_fm_probe.swift"
    if not script.is_file():
        return None
    swift = shutil.which("swift")
    if not swift:
        return None
    try:
        proc = subprocess.run(
            [swift, str(script)],
            capture_output=True, text=True, timeout=8,
        )
        line = (proc.stdout or "").strip().splitlines()
        out = line[-1] if line else ""
        if out == "available":
            return LocalModelStatus(
                available=True,
                reason="Apple Foundation Models framework present",
                supports_tools=False,  # tool loop not wired through FM yet
                index_find=True,
                backend="apple_fm",
            )
        return LocalModelStatus(
            available=False,
            reason=f"Apple FM probe: {out or proc.stderr.strip() or 'unavailable'}",
            index_find=True,
            backend="none",
        )
    except Exception as exc:
        return LocalModelStatus(
            available=False,
            reason=f"Apple FM probe failed: {exc}",
            index_find=True,
            backend="none",
        )


def _ollama_compat_probe() -> LocalModelStatus | None:
    """OpenAI-compatible local server (Ollama default: :11434/v1)."""
    base = (
        os.environ.get("ASSISTANT_LOCAL_BASE_URL")
        or os.environ.get("OLLAMA_HOST")
        or ""
    ).strip()
    if not base:
        # Conventional Ollama OpenAI bridge
        base = "http://127.0.0.1:11434/v1"
    if base.endswith("/"):
        base = base[:-1]
    # Health: /models or bare tags
    urls = [f"{base}/models"]
    if "11434" in base:
        urls.append("http://127.0.0.1:11434/api/tags")
    for url in urls:
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if 200 <= resp.status < 300:
                    model = (
                        os.environ.get("ASSISTANT_LOCAL_MODEL")
                        or os.environ.get("OLLAMA_MODEL")
                        or "llama3.2"
                    )
                    return LocalModelStatus(
                        available=True,
                        reason=f"local OpenAI-compat at {base} model={model}",
                        supports_tools=True,
                        index_find=True,
                        backend="ollama_compat",
                    )
        except Exception:
            continue
    return None


def probe_apple_foundation_models() -> LocalModelStatus:
    try:
        import platform
        if platform.system() != "Darwin":
            return LocalModelStatus(
                available=False, reason="not macOS", index_find=True)
    except Exception:
        return LocalModelStatus(
            available=False, reason="platform probe failed", index_find=True)
    probed = _swift_probe()
    if probed is not None:
        return probed
    return LocalModelStatus(
        available=False,
        reason=(
            "Apple Foundation Models not available on this Mac — "
            "local-only uses index find and/or ASSISTANT_LOCAL_BASE_URL"
        ),
        supports_tools=False,
        index_find=True,
        backend="none",
    )


def probe_local_generation() -> LocalModelStatus:
    """Best available on-device/local generation backend."""
    apple = probe_apple_foundation_models()
    if apple.available and apple.backend == "apple_fm":
        # FM present but no tool-loop adapter yet — prefer ollama if up.
        local = _ollama_compat_probe()
        if local is not None:
            return local
        return apple
    local = _ollama_compat_probe()
    if local is not None:
        return local
    return LocalModelStatus(
        available=False,
        reason=apple.reason,
        supports_tools=False,
        index_find=True,
        backend="none",
    )


def require_local_or_refuse(*, local_only: bool) -> LocalModelStatus:
    status = probe_local_generation()
    if not local_only:
        return status
    if status.available:
        return status
    if status.index_find:
        return LocalModelStatus(
            available=False,
            reason=(
                "local-only: no on-device generator — "
                "using index-only find (no cloud)"
            ),
            supports_tools=False,
            index_find=True,
            backend="none",
        )
    return LocalModelStatus(
        available=False,
        reason=f"local-only session refused: {status.reason}",
        supports_tools=False,
        index_find=False,
        backend="none",
    )


def capability_lines() -> list[str]:
    apple = probe_apple_foundation_models()
    gen = probe_local_generation()
    return [
        f"apple_foundation_models: {'yes' if apple.backend == 'apple_fm' and apple.available else 'no'}",
        f"local_generation: {'yes' if gen.available else 'no'} ({gen.backend})",
        f"index_find_local: yes",
        f"reason: {gen.reason}",
    ]


def local_chat_turn(
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """One chat completion against ASSISTANT_LOCAL_BASE_URL (OpenAI shape).

    Raises RuntimeError if local server unavailable.
    """
    status = probe_local_generation()
    if not status.available or status.backend != "ollama_compat":
        raise RuntimeError(
            f"local generation unavailable ({status.reason}). "
            "Start Ollama or set ASSISTANT_LOCAL_BASE_URL."
        )
    base = (
        os.environ.get("ASSISTANT_LOCAL_BASE_URL")
        or "http://127.0.0.1:11434/v1"
    ).rstrip("/")
    model = (
        os.environ.get("ASSISTANT_LOCAL_MODEL")
        or os.environ.get("OLLAMA_MODEL")
        or "llama3.2"
    )
    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    if tools:
        body["tools"] = tools
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"local chat failed: {exc}") from exc
    choices = payload.get("choices") or []
    if not choices:
        raise RuntimeError("local chat returned no choices")
    msg = choices[0].get("message") or {}
    return {
        "role": msg.get("role") or "assistant",
        "content": msg.get("content"),
        "tool_calls": msg.get("tool_calls"),
    }
