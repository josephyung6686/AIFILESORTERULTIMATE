"""What a Session says, as plain data. Renderers draw these; nothing here prints.

The shapes are the desktop-app contract (design §9): `to_json` writes one
object per line with a `type` field.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class Citation:
    name: str
    folder: str
    open_target: str | None
    #: "name" while the file's text has not been read yet: it was found by
    #: its name alone.
    matched_by: str = ""
    #: A short plain reason shown beside the file ("you protected it").
    note: str = ""


@dataclass(frozen=True)
class Message:
    text: str
    citations: tuple[Citation, ...] = ()


@dataclass(frozen=True)
class Progress:
    stage: str
    done: int = 0
    total: int = 0
    line: str = ""


@dataclass(frozen=True)
class Option:
    id: str
    label: str


@dataclass(frozen=True)
class Question:
    question_id: str
    text: str
    why: str
    changes: str
    options: tuple[Option, ...]
    allow_text: bool = True
    allow_skip: bool = True
    files_preview: tuple[str, ...] = ()
    count: int = 0
    index: int = 1
    of: int = 1


@dataclass(frozen=True)
class Move:
    src: str
    dst: str


@dataclass(frozen=True)
class Confirm:
    confirm_id: str
    summary: str
    moves: tuple[Move, ...]
    sensitive: bool
    undo_available: bool


@dataclass(frozen=True)
class Counts:
    indexed: int
    set_aside: int
    protected: int
    held: int
    open_questions: int


@dataclass(frozen=True)
class Suggestions:
    items: tuple[dict, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Done:
    moved: bool
    undo_token: str | None


@dataclass(frozen=True)
class Error:
    text: str
    changed: bool = False


_TYPES = {
    Message: "message", Progress: "progress", Question: "question",
    Confirm: "confirm", Counts: "counts", Suggestions: "suggestions",
    Done: "done", Error: "error",
}


def to_json(event) -> str:
    data = asdict(event)
    if isinstance(event, Confirm):
        # The contract names a move's ends `from` and `to`.
        data["moves"] = [{"from": m.src, "to": m.dst} for m in event.moves]
    return json.dumps({"type": _TYPES[type(event)], **data}, ensure_ascii=False)
