"""The conversation engine: history, permission level, confirmations, events.

A `Session` never prints. It hands events (`assistant.events`) to `emit`, and a
renderer draws them. The model decides what to do through tools; this code
delivers: confirmations, permission checks and question rendering are built
here from database rows, never from model text.
"""
from __future__ import annotations

import sqlite3
import uuid
from pathlib import Path
from typing import Any, Callable

from assistant import events as ev

#: History is trimmed to this many characters before each model call. The
#: oldest tool payloads go first; the person's words and the replies stay.
HISTORY_BUDGET = 60_000
DROPPED = "[earlier result dropped]"

FOLDER_QUESTION = "Which folder should I look after?"


def _counts(conn: sqlite3.Connection):
    """The index totals, or None when nothing could be read.

    One indirection so the Session does not care whether the index module is
    present yet; a missing table means nothing is indexed.
    """
    try:
        from items.indexing import counts
        return counts(conn)
    except Exception:
        return None


def _short_reason(exc: BaseException) -> str:
    text = str(exc).lower()
    if "402" in text or "balance" in text or "credit" in text:
        return "the account is out of credit"
    if "no api key" in text or "unset" in text or "api key" in text:
        return "no key is set up"
    if "timeout" in text or "timed out" in text:
        return "it timed out"
    if "connect" in text or "network" in text or "resolve" in text:
        return "no connection"
    return "it returned an error"


def _folder_of(path: str | None) -> str:
    if not path:
        return ""
    parent = Path(path).parent
    try:
        return "~/" + str(parent.relative_to(Path.home()))
    except ValueError:
        return str(parent)


class Session:
    def __init__(self, conn: sqlite3.Connection, *,
                 provider_turn: Callable[..., dict] | None = None,
                 emit: Callable[[object], None],
                 session_id: str | None = None) -> None:
        self.conn = conn
        self.provider_turn = provider_turn
        self.emit = emit
        self.session_id = session_id or str(uuid.uuid4())
        self.history: list[dict[str, Any]] = []
        self.no_model = False

    # -- opening ---------------------------------------------------------
    def open(self) -> None:
        c = _counts(self.conn)
        if c is not None:
            self.emit(ev.Counts(indexed=c.indexed, set_aside=c.set_aside,
                                protected=c.protected, held=c.held,
                                open_questions=c.open_questions))
        if c is None or c.indexed == 0:
            self.emit(ev.Message(text=FOLDER_QUESTION))
            return
        self.emit(ev.Message(text=f"I'm looking after {c.indexed} files. "
                                  "What would you like to find or tidy?"))

    # -- a turn ----------------------------------------------------------
    def say(self, text: str) -> None:
        self.history.append({"role": "user", "content": text})
        if self.no_model:
            self.emit(ev.Message(text="No AI model is answering right now, "
                                      "so I can find files, show what I've "
                                      "got and undo."))
            return
        try:
            answer = self._converse(text)
        except Exception as exc:  # the person never sees a traceback
            self.no_model = True
            self.emit(ev.Error(
                text=(f"The AI model didn't respond ({_short_reason(exc)}). "
                      "Nothing changed. I can still find files and undo."),
                changed=False))
            return
        self.history.append({"role": "assistant", "content": answer.text})
        self.emit(ev.Message(text=_strip_citation_line(answer.text),
                             citations=self._citations(answer.citations)))

    def _converse(self, text: str):
        from assistant.chat import (
            _provider_name, build_system_prompt, converse)
        from assistant.egress import PersistentEgress
        from assistant.tools import ToolRuntime

        cfg = None
        provider, model = "deepseek", "deepseek-chat"
        if self.provider_turn is None:
            from assistant.provider import resolve_provider
            cfg = resolve_provider()
            provider, model = _provider_name(cfg), cfg.model
        try:
            from items.refresh import refresh_index
            refresh_index(self.conn, prefer_fsevents=False)
        except Exception:
            pass
        self._trim()
        runtime = ToolRuntime(self.conn, session_key=self.session_id,
                              egress_class="cloud")
        messages = [{"role": "system",
                     "content": build_system_prompt(self.conn, text)},
                    *self.history]
        # `converse` appends the model turns and tool replies; the history
        # keeps the tool messages (between the last user line and the answer)
        # so a later turn can refer back to them.
        messages, answer = converse(
            self.conn, messages, runtime=runtime,
            provider_turn=self.provider_turn, config=cfg,
            provider=provider, model=model,
            ledger=PersistentEgress(self.conn, session_id=self.session_id),
            question=text)
        new = messages[1 + len(self.history):]
        # The final assistant message is re-added by `say` as plain text.
        if new and new[-1].get("role") == "assistant" and not new[-1].get(
                "tool_calls"):
            new = new[:-1]
        self.history.extend(new)
        return answer

    def _trim(self) -> None:
        def total() -> int:
            return sum(len(str(m.get("content") or "")) for m in self.history)
        for m in self.history:
            if total() < HISTORY_BUDGET:
                return
            if m["role"] == "tool" and m.get("content") != DROPPED:
                m["content"] = DROPPED

    def _citations(self, item_ids) -> tuple[ev.Citation, ...]:
        out = []
        for item_id in item_ids:
            row = self.conn.execute(
                "SELECT display_label, open_target FROM items "
                "WHERE item_id = ?", (item_id,)).fetchone()
            if row is None:
                continue
            out.append(ev.Citation(name=row["display_label"],
                                   folder=_folder_of(row["open_target"]),
                                   open_target=row["open_target"]))
        return tuple(out)


def _strip_citation_line(text: str) -> str:
    """The model's `Citations:` line carries internal ids; the person gets
    the citations as names instead."""
    return "\n".join(line for line in text.splitlines()
                     if not line.lower().startswith("citations:")).strip()
