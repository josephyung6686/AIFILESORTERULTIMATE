"""Single assistant policy boundary for every tool call.

Validate → privacy/trust → dispatch. Callers must not bypass ``gate_tool_call``.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence
from urllib.parse import urlparse

from assistant.registry import (
    ALWAYS_TOOLS,
    DEFERRED_GROUPS,
    WRITE_SHAPED,
    is_write_shaped,
    schema_for_tool,
)
from items.mailbox import path_is_protected

# Keys that must never appear as free-form write destinations in tool args.
_DESTINATION_KEYS = frozenset({
    "dst", "dest", "destination", "target_path", "to_path", "move_to",
    "src", "source_path", "from_path", "path", "open_target",
})

# Payload keys that may carry filesystem paths and must be stripped when
# the item is held/protected (or always scrubbed for protected path values).
_PATH_PAYLOAD_KEYS = frozenset({
    "open_target", "path", "src", "dst", "dest", "destination",
    "source_path", "target_path", "from_path", "to_path", "root",
})

# File-derived / attacker-controlled fields — always untrusted.
UNTRUSTED_FIELD_KEYS = frozenset({
    "display_label", "title", "subject", "basename", "label",
    "untrusted_snippet", "snippet", "peer_label", "explanation",
    "raw_value", "filename", "name",
})

_LOOPBACK_HOSTS = frozenset({
    "localhost", "127.0.0.1", "::1", "0.0.0.0",
})

# Test / audit hook — every gate records here.
_GATE_LOG: list[dict[str, Any]] = []


@dataclass(frozen=True)
class PolicyResult:
    allowed: bool
    reason: str
    protected: bool = False
    untrusted: bool = True
    bytes_in: int = 0
    bytes_out: int = 0
    citations: tuple[str, ...] = ()
    egress_class: str = "none"  # none | local | cloud | provider
    arguments: dict[str, Any] = field(default_factory=dict)
    sanitized_payload: dict[str, Any] | None = None


def clear_gate_log() -> None:
    _GATE_LOG.clear()


def gate_log() -> list[dict[str, Any]]:
    return list(_GATE_LOG)


def envelope_bytes(obj: Any) -> int:
    """Byte size of a JSON-serialized request/response envelope."""
    return len(json.dumps(obj, ensure_ascii=False, default=str).encode("utf-8"))


def is_loopback_url(url: str) -> bool:
    if not url or not str(url).strip():
        return False
    raw = str(url).strip()
    if "://" not in raw:
        raw = "http://" + raw
    try:
        host = (urlparse(raw).hostname or "").lower()
    except Exception:
        return False
    return host in _LOOPBACK_HOSTS


def explicit_local_base_url() -> str | None:
    """Local transport only when ASSISTANT_LOCAL_BASE_URL is set explicitly."""
    base = (os.environ.get("ASSISTANT_LOCAL_BASE_URL") or "").strip()
    return base or None


def classify_egress(
        *,
        local_only: bool = False,
        provider: str | None = None,
        base_url: str | None = None,
) -> str:
    """Label egress class for a generation request.

    Loopback explicit local transport → ``local``.
    Remote / provider endpoints (including remote 'local-compatible') → ``cloud``.
    Index-only / no generation → ``none``.
    """
    if provider and provider.lower() in ("deepseek", "openai", "anthropic"):
        return "cloud"
    url = base_url or explicit_local_base_url() or ""
    if url:
        return "local" if is_loopback_url(url) else "cloud"
    if local_only:
        return "none"
    if provider and provider.lower() == "local":
        return "local"
    return "provider" if provider else "none"


def local_held_body_allowed() -> bool:
    """Held bodies only when an explicit loopback local transport is configured."""
    base = explicit_local_base_url()
    return bool(base and is_loopback_url(base))


def item_is_held_or_protected(
        conn: sqlite3.Connection, item_id: str,
) -> tuple[bool, bool, str | None]:
    """Return (held_or_protected, is_protected_path, open_target)."""
    row = conn.execute(
        "SELECT typing_state, open_target FROM items "
        "WHERE item_id = ? AND presence = 'live' AND superseded_by IS NULL",
        (item_id,),
    ).fetchone()
    if row is None:
        return False, False, None
    path = row["open_target"]
    protected = bool(path and path_is_protected(path))
    held = row["typing_state"] == "held" or protected
    return held, protected, path


def strip_protected_paths(
        payload: Any,
        *,
        force_strip_all_paths: bool = False,
        protected_values: Sequence[str] | None = None,
) -> Any:
    """Recursively remove protected/held filesystem paths from payloads."""
    blocked = {p for p in (protected_values or ()) if p}
    if isinstance(payload, dict):
        out: dict[str, Any] = {}
        for key, value in payload.items():
            if key in _PATH_PAYLOAD_KEYS:
                if force_strip_all_paths:
                    out[key] = None
                    continue
                if isinstance(value, str) and (
                        path_is_protected(value) or value in blocked):
                    out[key] = None
                    continue
            out[key] = strip_protected_paths(
                value,
                force_strip_all_paths=force_strip_all_paths,
                protected_values=protected_values,
            )
        return out
    if isinstance(payload, list):
        return [
            strip_protected_paths(
                v,
                force_strip_all_paths=force_strip_all_paths,
                protected_values=protected_values,
            )
            for v in payload
        ]
    if isinstance(payload, str) and (
            path_is_protected(payload) or payload in blocked):
        return None
    return payload


def mark_untrusted_fields(payload: dict[str, Any]) -> dict[str, Any]:
    """Ensure file-derived fields are tagged untrusted when present."""
    # Structural tagging only — do not mutate nested values into wrappers.
    if any(k in payload for k in UNTRUSTED_FIELD_KEYS):
        if "trust" not in payload:
            payload = {**payload, "trust": "UNTRUSTED_LABEL"}
    return payload


def validate_tool_arguments(
        name: str, arguments: dict[str, Any],
) -> tuple[bool, str, dict[str, Any]]:
    """Validate args against the tool schema before dispatch.

    Rejects unknown fields, non-integer limits, and free-form path destinations
    (except ``scan_refresh.root`` which is an explicit root scan argument).
    """
    schema = schema_for_tool(name)
    if schema is None:
        # Unknown tool — still reject free-form destinations.
        for key in arguments:
            if key in _DESTINATION_KEYS:
                return False, f"free-form destination field refused: {key}", {}
        return True, "", dict(arguments)

    params = (schema.get("function") or schema).get("parameters") or {}
    props = params.get("properties") or {}
    required = set(params.get("required") or [])
    allowed_keys = set(props.keys())

    cleaned: dict[str, Any] = {}
    for key, value in arguments.items():
        if key not in allowed_keys:
            return False, f"unknown field: {key}", {}
        # Free-form destinations never accepted except scan_refresh.root.
        if key in _DESTINATION_KEYS and not (
                name == "scan_refresh" and key == "root"):
            return False, f"free-form destination field refused: {key}", {}
        if key == "path" and name != "scan_refresh":
            return False, "path strings refused in tool arguments", {}
        prop = props.get(key) or {}
        expected = prop.get("type")
        if expected == "integer":
            if type(value) is not int or isinstance(value, bool):
                return False, f"{key} must be an integer", {}
        elif expected == "string":
            if not isinstance(value, str):
                return False, f"{key} must be a string", {}
        elif expected == "boolean":
            if not isinstance(value, bool):
                return False, f"{key} must be a boolean", {}
        elif expected == "array":
            if not isinstance(value, list):
                return False, f"{key} must be an array", {}
        if expected == "string" and "enum" in prop:
            if value not in prop["enum"]:
                return False, f"{key} must be one of {prop['enum']}", {}
        cleaned[key] = value

    missing = required - set(cleaned.keys())
    if missing:
        return False, f"missing required: {sorted(missing)}", {}
    return True, "", cleaned


def validate_citations(
        claimed: Iterable[str] | Iterable[Any],
        *,
        returned_item_ids: Sequence[str],
        returned_source_ids: Sequence[str] = (),
) -> tuple[tuple[str, ...], tuple[str, ...], str | None]:
    """Keep only citations that match returned item/source ids.

    Returns (valid_item_ids, valid_source_ids, refuse_reason_or_None).
    Invented citations are dropped; if *all* claimed were invented, reason set.
    """
    allowed_items = set(returned_item_ids)
    allowed_sources = set(returned_source_ids)
    valid_items: list[str] = []
    valid_sources: list[str] = []
    invented = False
    claimed_list = list(claimed)
    if not claimed_list:
        return (), (), None
    for c in claimed_list:
        if isinstance(c, dict):
            iid = str(c.get("item_id") or "")
            sids = c.get("source_ids") or ()
            if iid and iid in allowed_items:
                if iid not in valid_items:
                    valid_items.append(iid)
                for s in sids:
                    s = str(s)
                    if s in allowed_sources and s not in valid_sources:
                        valid_sources.append(s)
                    elif s and s not in allowed_sources:
                        invented = True
            elif iid:
                invented = True
        else:
            iid = str(c)
            if iid in allowed_items:
                if iid not in valid_items:
                    valid_items.append(iid)
            elif iid:
                invented = True
    if invented and not valid_items:
        return (), (), "invented citations refused"
    return tuple(valid_items), tuple(valid_sources), (
        "invented citations stripped" if invented else None
    )


def parse_answer_citations(text: str) -> list[str]:
    """Extract item_id-like tokens from a Citations: line."""
    if not text:
        return []
    m = re.search(r"(?im)^citations:\s*(.+)$", text)
    if not m:
        return []
    body = m.group(1).strip()
    if body.lower() in ("(none)", "none", "-"):
        return []
    out: list[str] = []
    for part in re.split(r"[,;\s]+", body):
        token = part.strip().strip("[]()")
        if not token:
            continue
        # Drop src= annotations: item[src=a,b]
        token = token.split("[", 1)[0].strip()
        if token and token not in out:
            out.append(token)
    return out


def group_for_tool(name: str) -> str | None:
    for group, tools in DEFERRED_GROUPS.items():
        if name in tools:
            return group
    return None


def gate_tool_call(
        *,
        name: str,
        arguments: dict[str, Any] | str | Any,
        conn: sqlite3.Connection | None = None,
        loaded_groups: set[str] | None = None,
        allow_held_body: bool = False,
        writes_unlocked: bool = False,
        bytes_spent: int = 0,
        byte_budget: int = 24_000,
        egress_class: str = "cloud",
) -> PolicyResult:
    """One policy gate for every base and deferred tool.

    Order: parse → schema → unlock/privacy → budget.
    """
    loaded = loaded_groups or set()
    bytes_in = 0

    # Parse arguments
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments or "{}")
        except json.JSONDecodeError:
            result = PolicyResult(
                allowed=False,
                reason="arguments must be JSON object",
                egress_class=egress_class,
            )
            _record(name, result)
            return result
    if not isinstance(arguments, dict):
        result = PolicyResult(
            allowed=False,
            reason="arguments must be object",
            egress_class=egress_class,
        )
        _record(name, result)
        return result

    bytes_in = envelope_bytes(arguments)

    # Byte budget before any further work
    if bytes_spent >= byte_budget:
        result = PolicyResult(
            allowed=False,
            reason="turn byte budget exceeded; refuse further body",
            bytes_in=bytes_in,
            egress_class=egress_class,
        )
        _record(name, result)
        return result

    group = group_for_tool(name)

    # Unlock refusals BEFORE schema — injection fixtures smuggle free-form
    # destinations; those must still fail as "not enabled"/"locked".
    if name in ("apply_moves", "undo_moves") and not writes_unlocked:
        result = PolicyResult(
            allowed=False,
            reason=(
                "apply/undo locked — set ASSISTANT_ENABLE_APPLY=1 "
                "and request_tools(organize_apply)"
            ),
            bytes_in=bytes_in,
            egress_class=egress_class,
        )
        _record(name, result)
        return result

    if group is not None and name != "place_preview" and group not in loaded:
        if is_write_shaped(name) or name in WRITE_SHAPED:
            msg = (
                "write tools are not enabled until "
                "request_tools(<group>); apply still locked without "
                "ASSISTANT_ENABLE_APPLY=1"
            )
        else:
            msg = f"request_tools({group!r}) required first"
        result = PolicyResult(
            allowed=False,
            reason=msg,
            bytes_in=bytes_in,
            egress_class=egress_class,
        )
        _record(name, result)
        return result

    if (
            name not in ALWAYS_TOOLS
            and group is None
            and name != "place_preview"
            and (is_write_shaped(name) or name in WRITE_SHAPED)
    ):
        result = PolicyResult(
            allowed=False,
            reason=(
                "write tools are not enabled until "
                "request_tools(<group>); apply still locked without "
                "ASSISTANT_ENABLE_APPLY=1"
            ),
            bytes_in=bytes_in,
            egress_class=egress_class,
        )
        _record(name, result)
        return result

    # Schema validation (for tools that are unlocked / always-on)
    ok, reason, cleaned = validate_tool_arguments(name, arguments)
    if not ok:
        result = PolicyResult(
            allowed=False,
            reason=reason,
            bytes_in=bytes_in,
            egress_class=egress_class,
        )
        _record(name, result)
        return result

    # place_preview is dry-run — executable without group; schema still deferred.
    if name == "place_preview":
        result = PolicyResult(
            allowed=True,
            reason="ok",
            untrusted=False,
            bytes_in=bytes_in,
            egress_class=egress_class,
            arguments=cleaned,
        )
        _record(name, result)
        return result

    # Always-on tools
    if name in ALWAYS_TOOLS:
        if name == "read_item" and conn is not None:
            item_id = str(cleaned.get("item_id") or "")
            held, protected, _path = item_is_held_or_protected(conn, item_id)
            if held and not allow_held_body:
                result = PolicyResult(
                    allowed=False,
                    reason=(
                        "held or protected — body withheld from cloud path; "
                        "metadata only. Use local-only + ASSISTANT_LOCAL_BASE_URL "
                        "for on-device body read."
                    ),
                    protected=protected or held,
                    untrusted=True,
                    bytes_in=bytes_in,
                    citations=(item_id,) if item_id else (),
                    egress_class=egress_class,
                    arguments=cleaned,
                )
                _record(name, result)
                return result
        result = PolicyResult(
            allowed=True,
            reason="ok",
            untrusted=True,
            bytes_in=bytes_in,
            egress_class=egress_class,
            arguments=cleaned,
        )
        _record(name, result)
        return result

    # apply/undo unlocked path
    if name in ("apply_moves", "undo_moves"):
        result = PolicyResult(
            allowed=True,
            reason="ok",
            untrusted=False,
            bytes_in=bytes_in,
            egress_class=egress_class,
            arguments=cleaned,
        )
        _record(name, result)
        return result

    if group is not None:
        # extract_one: refuse held/protected entirely
        if name == "extract_one" and conn is not None:
            item_id = str(cleaned.get("item_id") or "")
            held, protected, _path = item_is_held_or_protected(conn, item_id)
            if held:
                result = PolicyResult(
                    allowed=False,
                    reason=(
                        "extract_one refused for held/protected item — "
                        "metadata path withheld"
                    ),
                    protected=True,
                    untrusted=True,
                    bytes_in=bytes_in,
                    citations=(item_id,) if item_id else (),
                    egress_class=egress_class,
                    arguments=cleaned,
                )
                _record(name, result)
                return result

        result = PolicyResult(
            allowed=True,
            reason="ok",
            untrusted=True,
            bytes_in=bytes_in,
            egress_class=egress_class,
            arguments=cleaned,
        )
        _record(name, result)
        return result

    result = PolicyResult(
        allowed=False,
        reason=f"unknown or deferred tool: {name}",
        bytes_in=bytes_in,
        egress_class=egress_class,
        arguments=cleaned,
    )
    _record(name, result)
    return result


def finalize_payload(
        name: str,
        payload: dict[str, Any],
        *,
        conn: sqlite3.Connection | None = None,
        allow_held_body: bool = False,
        citations: Sequence[str] = (),
        source_ids: Sequence[str] = (),
        egress_class: str = "cloud",
) -> PolicyResult:
    """Post-execute: strip protected paths, tag untrusted, measure bytes_out."""
    blocked_paths: list[str] = []
    force = False
    if conn is not None and not allow_held_body:
        # Collect held/protected open_targets to scrub from nested payloads.
        try:
            for row in conn.execute(
                "SELECT open_target, typing_state FROM items "
                "WHERE presence='live' AND superseded_by IS NULL "
                "AND open_target IS NOT NULL"
            ):
                path = row["open_target"]
                if not path:
                    continue
                if row["typing_state"] == "held" or path_is_protected(path):
                    blocked_paths.append(path)
        except sqlite3.Error:
            pass

    sanitized = strip_protected_paths(
        payload,
        force_strip_all_paths=force,
        protected_values=blocked_paths,
    )
    if isinstance(sanitized, dict):
        sanitized = mark_untrusted_fields(sanitized)
    else:
        sanitized = {"value": sanitized}

    valid_cites, _valid_src, _ = validate_citations(
        citations,
        returned_item_ids=list(citations),
        returned_source_ids=list(source_ids),
    )
    # Citations from tools are authoritative returned ids — keep them.
    cite_tuple = tuple(citations) if citations else valid_cites
    blob = envelope_bytes(sanitized)
    protected = bool(blocked_paths) or bool(sanitized.get("refused"))
    return PolicyResult(
        allowed=True,
        reason="ok",
        protected=protected,
        untrusted=True,
        bytes_out=blob,
        citations=cite_tuple,
        egress_class=egress_class,
        sanitized_payload=sanitized,
    )


def schemas_for_session(loaded_groups: set[str]) -> list[dict[str, Any]]:
    """Always schemas + exact deferred schemas for requested groups only."""
    from assistant.registry import always_schemas, deferred_schemas_for

    out = always_schemas()
    for group in sorted(loaded_groups):
        out.extend(deferred_schemas_for(group))
    return out


def _record(name: str, result: PolicyResult) -> None:
    _GATE_LOG.append({
        "name": name,
        "allowed": result.allowed,
        "reason": result.reason,
        "protected": result.protected,
        "egress_class": result.egress_class,
        "bytes_in": result.bytes_in,
    })
