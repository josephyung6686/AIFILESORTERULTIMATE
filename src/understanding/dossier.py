# src/understanding/dossier.py
"""The bounded dossier a cloud model may see. Never the whole file.

Fields that leave the device, and nothing else: the filename, path hints
(directory names, not the file bytes), a kind if one is already known, the
first N words of text or OCR, and a few metadata keys the caller already
extracted. A protected file, a held file, or a path inside an area the person
marked private is not a dossier.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

PROMPT_VERSION: str = "understanding-1"
WORD_CAP: int = 400

FIELDS_THAT_LEAVE: tuple[str, ...] = (
    "filename",
    "path_hints",
    "kind",
    "text_excerpt",
    "metadata",
)

#: Path parts that are private even when nobody typed them. A name-only walk
#: can see these without opening the file.
PROTECTED_PARTS: frozenset[str] = frozenset({
    ".ssh", ".gnupg", "keychains", "cookies", "passwords",
})
PROTECTED_EXTENSIONS: frozenset[str] = frozenset({
    ".pem", ".key", ".p12", ".kdbx", ".keystore",
})


class NotSendable(ValueError):
    """This file does not become a dossier."""


@dataclass(frozen=True, slots=True)
class FileView:
    """What the pass knows about one file before it asks."""

    file_id: str
    path: str
    filename: str
    kind: str = ""
    text: str = ""
    metadata: dict | None = None
    protected: bool = False
    held: bool = False


def path_is_protected(path: str) -> bool:
    parts = {part.casefold() for part in path.replace("\\", "/").split("/")}
    if parts & PROTECTED_PARTS:
        return True
    lower = path.casefold()
    return any(lower.endswith(ext) for ext in PROTECTED_EXTENSIONS)


def in_private_area(path: str, private_areas: set[str]) -> bool:
    """A private area matches a path segment or the kind name, case-insensitively."""
    if not private_areas:
        return False
    banned = {area.casefold() for area in private_areas if area.strip()}
    parts = [part.casefold() for part in path.replace("\\", "/").split("/") if part]
    return any(part in banned for part in parts)


def excerpt(text: str, *, word_cap: int = WORD_CAP) -> str:
    words = (text or "").split()
    if len(words) <= word_cap:
        return " ".join(words)
    return " ".join(words[:word_cap])


def path_hints(path: str) -> list[str]:
    parts = [part for part in path.replace("\\", "/").split("/") if part]
    # The filename is its own field. The hints are the directories above it.
    return parts[:-1]


def build_dossier(view: FileView, *, private_areas: set[str]) -> dict:
    if view.protected or view.held or path_is_protected(view.path):
        raise NotSendable(f"{view.file_id} is protected or held and is not sent")
    if in_private_area(view.path, private_areas) or (
            view.kind and view.kind.casefold() in {a.casefold() for a in private_areas}):
        raise NotSendable(
            f"{view.file_id} is in an area marked private and is not sent")
    metadata = {}
    for key, value in (view.metadata or {}).items():
        if key.casefold() in {"filename", "path", "text", "body", "content"}:
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            metadata[str(key)] = value
    return {
        "file_id": view.file_id,
        "filename": view.filename,
        "path_hints": path_hints(view.path),
        "kind": view.kind,
        "text_excerpt": excerpt(view.text),
        "metadata": metadata,
    }


def dossier_hash(dossier: dict, *, model_id: str) -> str:
    payload = json.dumps(
        {"dossier": dossier, "model": model_id, "prompt": PROMPT_VERSION},
        sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def estimate_input_tokens(dossier: dict) -> int:
    """Upper bound used by the dry-run. `chars / 4` for the JSON, nothing else.

    This is a formula, not a measured tokenizer and not a price.
    """
    raw = json.dumps(dossier, sort_keys=True)
    return max(1, len(raw) // 4)
