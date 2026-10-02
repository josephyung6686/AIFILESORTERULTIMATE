"""Thin BYOK chat client (OpenAI-compatible tool calling).

Loads credentials from the environment only — never hardcodes keys.
DeepSeek is the default provider shape used by this repo.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProviderConfig:
    api_key: str
    base_url: str
    model: str


def load_dotenv(path: Path | None = None) -> None:
    """Load KEY=VALUE lines into os.environ if unset. Never prints values."""
    env_path = path or Path.cwd() / ".env"
    if not env_path.is_file():
        # also try repo root relative to this file
        alt = Path(__file__).resolve().parents[2] / ".env"
        env_path = alt if alt.is_file() else env_path
    if not env_path.is_file():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def resolve_provider() -> ProviderConfig:
    load_dotenv()
    key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "No API key in environment. Set DEEPSEEK_API_KEY (BYOK). "
            "Nothing was sent."
        )
    base = (
        os.environ.get("DEEPSEEK_BASE_URL")
        or os.environ.get("OPENAI_BASE_URL")
        or "https://api.deepseek.com"
    )
    model = (
        os.environ.get("DEEPSEEK_MODEL_FAST")
        or os.environ.get("DEEPSEEK_MODEL_LOGIC")
        or os.environ.get("OPENAI_MODEL")
        or "deepseek-chat"
    )
    return ProviderConfig(api_key=key, base_url=base.rstrip("/"), model=model)


def chat_turn(
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        config: ProviderConfig | None = None,
        temperature: float = 0.2,
) -> dict[str, Any]:
    """One chat.completions turn. Returns the assistant message dict."""
    from openai import OpenAI

    cfg = config or resolve_provider()
    client = OpenAI(api_key=cfg.api_key, base_url=cfg.base_url)
    response = client.chat.completions.create(
        model=cfg.model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=temperature,
    )
    choice = response.choices[0].message
    out: dict[str, Any] = {
        "role": "assistant",
        "content": choice.content,
    }
    if choice.tool_calls:
        out["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments or "{}",
                },
            }
            for tc in choice.tool_calls
        ]
    return out


def message_to_openai(msg: dict[str, Any]) -> dict[str, Any]:
    """Pass-through helper; keeps tool message shape stable."""
    return msg


def dump_safe(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)
