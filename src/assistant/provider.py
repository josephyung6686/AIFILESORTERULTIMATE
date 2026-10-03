"""Thin BYOK chat clients (OpenAI-compatible + Anthropic).

Loads credentials from the environment only — never hardcodes keys.
Provider selection is deterministic: explicit ASSISTANT_PROVIDER wins;
a single key selects that provider; multiple keys without an explicit
provider refuse.
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
    provider: str = "deepseek"  # deepseek | openai | anthropic


_CLOUD_PROVIDERS = frozenset({"deepseek", "openai", "anthropic"})


def load_dotenv(path: Path | None = None) -> None:
    """Load KEY=VALUE lines into os.environ if unset. Never prints values."""
    env_path = path or Path.cwd() / ".env"
    if not env_path.is_file():
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


def _env(name: str) -> str:
    return (os.environ.get(name) or "").strip()


def _keys_present() -> dict[str, str]:
    found: dict[str, str] = {}
    deepseek = _env("DEEPSEEK_API_KEY")
    openai = _env("OPENAI_API_KEY")
    anthropic = _env("ANTHROPIC_API_KEY")
    if deepseek:
        found["deepseek"] = deepseek
    if openai:
        found["openai"] = openai
    if anthropic:
        found["anthropic"] = anthropic
    return found


def _config_for(provider: str, api_key: str) -> ProviderConfig:
    if provider == "anthropic":
        return ProviderConfig(
            api_key=api_key,
            base_url=_env("ANTHROPIC_BASE_URL") or "https://api.anthropic.com",
            model=_env("ANTHROPIC_MODEL") or "claude-sonnet-4-20250514",
            provider="anthropic",
        )
    if provider == "openai":
        return ProviderConfig(
            api_key=api_key,
            base_url=(
                _env("OPENAI_BASE_URL") or "https://api.openai.com/v1"
            ).rstrip("/"),
            model=_env("OPENAI_MODEL") or "gpt-4o-mini",
            provider="openai",
        )
    # deepseek
    return ProviderConfig(
        api_key=api_key,
        base_url=(
            _env("DEEPSEEK_BASE_URL") or "https://api.deepseek.com"
        ).rstrip("/"),
        model=(
            _env("DEEPSEEK_MODEL_FAST")
            or _env("DEEPSEEK_MODEL_LOGIC")
            or "deepseek-chat"
        ),
        provider="deepseek",
    )


def resolve_provider() -> ProviderConfig:
    load_dotenv()
    forced = _env("ASSISTANT_PROVIDER").lower()
    keys = _keys_present()

    if forced:
        if forced not in _CLOUD_PROVIDERS:
            known = ", ".join(sorted(_CLOUD_PROVIDERS))
            raise RuntimeError(
                f"Unknown ASSISTANT_PROVIDER={forced!r}. "
                f"Use one of: {known}. Nothing was sent."
            )
        key = keys.get(forced)
        if not key:
            env_name = {
                "deepseek": "DEEPSEEK_API_KEY",
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
            }[forced]
            raise RuntimeError(
                f"ASSISTANT_PROVIDER={forced} but {env_name} unset. "
                "Nothing was sent."
            )
        return _config_for(forced, key)

    if not keys:
        raise RuntimeError(
            "No API key in environment. Set DEEPSEEK_API_KEY, "
            "OPENAI_API_KEY, or ANTHROPIC_API_KEY "
            "(or set ASSISTANT_PROVIDER with the matching key). "
            "Nothing was sent."
        )
    if len(keys) > 1:
        present = ", ".join(sorted(keys))
        raise RuntimeError(
            f"Multiple API keys set ({present}) without ASSISTANT_PROVIDER. "
            f"Set ASSISTANT_PROVIDER to one of: {present}. "
            "Nothing was sent."
        )
    provider = next(iter(keys))
    return _config_for(provider, keys[provider])


def _openai_tools_to_anthropic(tools: list[dict[str, Any]]) -> list[dict]:
    out = []
    for t in tools:
        fn = t.get("function") or t
        out.append({
            "name": fn["name"],
            "description": fn.get("description") or "",
            "input_schema": fn.get("parameters") or {"type": "object"},
        })
    return out


def _messages_to_anthropic(
        messages: list[dict[str, Any]],
) -> tuple[str, list[dict[str, Any]]]:
    system = ""
    converted: list[dict[str, Any]] = []
    for msg in messages:
        role = msg.get("role")
        if role == "system":
            system = (msg.get("content") or "") + (
                ("\n" + system) if system else "")
            continue
        if role == "tool":
            converted.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": msg.get("tool_call_id") or "unknown",
                    "content": msg.get("content") or "",
                }],
            })
            continue
        if role == "assistant" and msg.get("tool_calls"):
            blocks: list[dict[str, Any]] = []
            if msg.get("content"):
                blocks.append({"type": "text", "text": msg["content"]})
            for tc in msg["tool_calls"]:
                args = tc["function"].get("arguments") or "{}"
                if isinstance(args, str):
                    try:
                        args_obj = json.loads(args)
                    except json.JSONDecodeError:
                        args_obj = {}
                else:
                    args_obj = args
                blocks.append({
                    "type": "tool_use",
                    "id": tc["id"],
                    "name": tc["function"]["name"],
                    "input": args_obj,
                })
            converted.append({"role": "assistant", "content": blocks})
            continue
        converted.append({
            "role": "user" if role == "user" else "assistant",
            "content": msg.get("content") or "",
        })
    return system.strip(), converted


def chat_turn_anthropic(
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        config: ProviderConfig,
        temperature: float = 0.2,
) -> dict[str, Any]:
    """Anthropic Messages API → OpenAI-shaped assistant message."""
    import anthropic

    system, converted = _messages_to_anthropic(messages)
    client = anthropic.Anthropic(
        api_key=config.api_key,
        base_url=config.base_url or None,
    )
    kwargs: dict[str, Any] = {
        "model": config.model,
        "max_tokens": 2048,
        "messages": converted,
        "temperature": temperature,
        "tools": _openai_tools_to_anthropic(tools),
    }
    if system:
        kwargs["system"] = system
    response = client.messages.create(**kwargs)
    text_parts = []
    tool_calls = []
    for block in response.content:
        btype = getattr(block, "type", None)
        if btype == "text":
            text_parts.append(block.text)
        elif btype == "tool_use":
            tool_calls.append({
                "id": block.id,
                "type": "function",
                "function": {
                    "name": block.name,
                    "arguments": json.dumps(block.input or {}),
                },
            })
    out: dict[str, Any] = {
        "role": "assistant",
        "content": "\n".join(text_parts) if text_parts else None,
    }
    if tool_calls:
        out["tool_calls"] = tool_calls
    return out


def chat_turn(
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        config: ProviderConfig | None = None,
        temperature: float = 0.2,
) -> dict[str, Any]:
    """One chat turn. Returns OpenAI-shaped assistant message dict."""
    cfg = config or resolve_provider()
    if cfg.provider == "anthropic":
        return chat_turn_anthropic(
            messages=messages, tools=tools, config=cfg,
            temperature=temperature)

    from openai import OpenAI

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
    return msg


def dump_safe(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)
