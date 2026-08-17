"""Index destination folders and build content profiles.

A node's profile is the token Counter of files already in it — not the folder name.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

SKIP_DIR_NAMES = frozenset(
    {
        "node_modules",
        ".git",
        "venv",
        ".venv",
        "build",
        "dist",
        "target",
        "vendor",
        "Pods",
        "site-packages",
        "Library",
        "__pycache__",
        "DerivedData",
        "Auto-Save",
        "Previews",
    }
)
SKIP_MARKERS = frozenset({"package.json", "requirements.txt", "Cargo.toml", "go.mod"})
SKIP_SUFFIXES = frozenset({".egg-info", ".xcodeproj"})
TCC_NAMES = frozenset({"Desktop", "Documents", "Downloads"})
CLOUD_PATH_PARTS = frozenset({"OneDrive", "Mobile Documents", "com~apple~CloudDocs"})

_CAMEL = re.compile(r"(?<=[a-z])(?=[A-Z])")
_SPLIT = re.compile(r"[^A-Za-z0-9]+")
COMPOUND_RE = re.compile(r"[A-Za-z]+\d+[A-Za-z0-9]*")
CLASS_CODE_RE = re.compile(r"^[a-z]{2,}\d{3,}$")

WEAK_TOKENS = frozenset(
    {
        "hw",
        "homework",
        "lecture",
        "lectures",
        "notes",
        "note",
        "lab",
        "final",
        "exam",
        "quiz",
        "assignment",
        "syllabus",
        "copy",
        "readme",
        "untitled",
        "download",
        "downloads",
        "document",
        "documents",
        "file",
        "files",
        "img",
        "dsc",
        "image",
        "images",
        "photo",
        "photos",
        "screenshot",
        "screenshots",
        "new",
        "old",
        "draft",
        "edited",
        "summary",
        "todo",
        "the",
        "and",
        "for",
        "with",
        "from",
        "pdf",
        "docx",
        "txt",
        "md",
        "py",
        "jpg",
        "jpeg",
        "png",
        "xlsx",
        "csv",
        "zip",
    }
)


@dataclass(frozen=True)
class RootInfo:
    path: Path
    tcc_protected: bool
    cloud_synced: bool
    listing_unreliable: bool
    file_count: int
    warning: str | None


@dataclass
class NodeProfile:
    path: Path
    token_counts: Counter[str] = field(default_factory=Counter)
    file_count: int = 0
    extensions: Counter[str] = field(default_factory=Counter)


def is_dataless(path: Path) -> bool:
    name = path.name.lower()
    return name.endswith(".icloud") or path.suffix.lower() == ".icloud"


def tokenize(filename: str, *, identity_tokens: frozenset[str] = frozenset()) -> tuple[str, ...]:
    path = Path(filename)
    stem = _CAMEL.sub(" ", path.stem)
    ext = path.suffix.lower().lstrip(".")
    parts = [p.lower() for p in _SPLIT.split(stem) if p]
    tokens: list[str] = []
    seen: set[str] = set()

    def add(token: str) -> None:
        if token in seen or token in identity_tokens:
            return
        if token.isdigit() and len(token) < 4:
            return
        if len(token) < 2:
            return
        seen.add(token)
        tokens.append(token)

    for part in parts:
        for match in COMPOUND_RE.finditer(part):
            add(match.group(0).lower())
        for frag in re.findall(r"[a-z]+|\d+", part.lower()):
            add(frag)
    if ext:
        add(ext)
    return tuple(tokens)


def class_codes(tokens: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(t for t in tokens if CLASS_CODE_RE.match(t))


def is_skipped_destination(path: Path) -> bool:
    resolved = path.resolve()
    for current in (resolved, *resolved.parents):
        if current.name in SKIP_DIR_NAMES or current.suffix in SKIP_SUFFIXES:
            return True
        if current == current.parent:
            break
        try:
            if any((current / marker).is_file() for marker in SKIP_MARKERS):
                return True
        except OSError:
            continue
    return False


def iter_destination_folders(roots: list[Path]) -> list[Path]:
    found: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        if not root.exists():
            continue
        resolved_root = root.resolve()
        stack = [resolved_root]
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            try:
                if not current.is_dir():
                    continue
            except OSError:
                continue
            rel_parts = current.relative_to(resolved_root).parts if current != resolved_root else ()
            if any(part.startswith(".") for part in rel_parts):
                continue
            if is_skipped_destination(current):
                continue
            found.append(current)
            try:
                children = list(current.iterdir())
            except OSError:
                continue
            for child in children:
                if child.is_dir():
                    stack.append(child)
    found.sort()
    return found


def assign_file_to_node(path: Path, dest_folders: list[Path]) -> Path | None:
    resolved = path.resolve()
    dest_set = {p.resolve() for p in dest_folders}
    deepest: Path | None = None
    deepest_len = -1
    for folder in dest_set:
        try:
            resolved.relative_to(folder)
        except ValueError:
            continue
        if len(folder.parts) > deepest_len:
            deepest = folder
            deepest_len = len(folder.parts)
    return deepest


def build_profiles(
    dest_folders: list[Path],
    filed_files: list[Path],
    *,
    identity_tokens: frozenset[str] = frozenset(),
) -> dict[Path, NodeProfile]:
    profiles = {folder.resolve(): NodeProfile(path=folder.resolve()) for folder in dest_folders}
    resolved_dests = list(profiles)
    for file_path in filed_files:
        if is_dataless(file_path):
            continue
        node = assign_file_to_node(file_path, resolved_dests)
        if node is None:
            continue
        profile = profiles[node]
        profile.file_count += 1
        profile.token_counts.update(tokenize(file_path.name, identity_tokens=identity_tokens))
        ext = file_path.suffix.lower()
        if ext:
            profile.extensions[ext] += 1
    return profiles


def describe_root(path: Path) -> RootInfo:
    resolved = path.resolve()
    tcc_protected = resolved.name in TCC_NAMES
    cloud_synced = any(part in CLOUD_PATH_PARTS for part in resolved.parts)
    children: list[Path] = []
    if resolved.exists():
        try:
            children = list(resolved.iterdir())
        except OSError:
            children = []
        if not cloud_synced and any(is_dataless(child) for child in children):
            cloud_synced = True
    files = [child for child in children if child.is_file() and not is_dataless(child)]
    listing_unreliable = tcc_protected and len(children) == 0
    warnings: list[str] = []
    if cloud_synced:
        warnings.append("This folder is cloud-synced. Filing here uploads.")
    if listing_unreliable:
        warnings.append(
            "This folder looks empty, which often means the app does not have permission. "
            "Grant access in System Settings."
        )
    return RootInfo(
        path=resolved,
        tcc_protected=tcc_protected,
        cloud_synced=cloud_synced,
        listing_unreliable=listing_unreliable,
        file_count=len(files),
        warning=" ".join(warnings) or None,
    )
