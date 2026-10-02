"""Load a profile package. No branch on the profile name inside the detector."""
from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any


class ProfileRefused(ValueError):
    """The package shape is wrong. Nothing was applied."""


@dataclass(frozen=True)
class ProfilePackage:
    profile_id: str
    profile_version: str
    item_types: frozenset[str]
    relationship_types: frozenset[str]
    schema_to_item_type: dict[str, str]
    graph_cap: int
    timeline_days: int
    raw: dict[str, Any]


REQUIRED = (
    "profile_id", "profile_version", "item_types", "relationship_types",
)


def load_profile(source: str | Path | dict) -> ProfilePackage:
    """Load from a dict, a path, or a packaged name like `student` / `files_only`."""
    if isinstance(source, dict):
        data = source
    elif isinstance(source, Path) or (
            isinstance(source, str) and (source.endswith(".json") or "/" in source)):
        path = Path(source)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as problem:
            raise ProfileRefused(str(problem)) from problem
    else:
        data = _packaged(str(source))
    return _parse(data)


def _packaged(name: str) -> dict:
    try:
        root = resources.files("items.profiles")
        text = (root / f"{name}.json").read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError, OSError) as problem:
        raise ProfileRefused(f"unknown profile package {name!r}") from problem
    try:
        return json.loads(text)
    except json.JSONDecodeError as problem:
        raise ProfileRefused(str(problem)) from problem


def _parse(data: dict) -> ProfilePackage:
    if not isinstance(data, dict):
        raise ProfileRefused("profile must be a JSON object")
    missing = [key for key in REQUIRED if key not in data]
    if missing:
        raise ProfileRefused(f"profile missing {missing}")
    # A package may not clear holds. Ignore any hold-related keys.
    for banned in ("clear_holds", "release_safety", "unprotect"):
        data.pop(banned, None)
    item_types = frozenset(data["item_types"])
    relationship_types = frozenset(data["relationship_types"])
    if not item_types:
        raise ProfileRefused("item_types must be non-empty")
    mapping = data.get("schema_to_item_type") or {}
    if not isinstance(mapping, dict):
        raise ProfileRefused("schema_to_item_type must be an object")
    graph_cap = int(data.get("graph_cap", 40))
    timeline_days = int(data.get("timeline_days", 90))
    if graph_cap <= 0:
        raise ProfileRefused("graph_cap must be positive")
    return ProfilePackage(
        profile_id=str(data["profile_id"]),
        profile_version=str(data["profile_version"]),
        item_types=item_types,
        relationship_types=relationship_types,
        schema_to_item_type={str(k): str(v) for k, v in mapping.items()},
        graph_cap=graph_cap,
        timeline_days=timeline_days,
        raw=dict(data),
    )


def allows_relationship(profile: ProfilePackage | None, rel_type: str) -> bool:
    if profile is None:
        # No package: only hash duplicates, which do not need a life.
        return rel_type == "duplicate-of"
    return rel_type in profile.relationship_types
