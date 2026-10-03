"""Draw a Session's events in a terminal, and the JSON-lines app contract.

Nothing here decides anything: the Session does. This file turns events into
lines a person reads, and their typing into Session calls. No internal id ever
reaches the screen; the Session keeps what is waiting for an answer.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from assistant import events as ev
from assistant.session import Session

MOVES_SHOWN = 10
QUIT = {"quit", "exit", "bye", "q"}


def _home(path: str) -> str:
    try:
        return "~/" + str(Path(path).relative_to(Path.home()))
    except ValueError:
        return path


class TerminalRenderer:
    def __init__(self, stdout) -> None:
        self.out = stdout
        self.tty = bool(getattr(stdout, "isatty", lambda: False)())
        self.progress_open = False
        self.citations: tuple[ev.Citation, ...] = ()

    def _line(self, text: str = "") -> None:
        if self.progress_open:
            self.out.write("\n")
            self.progress_open = False
        self.out.write(text + "\n")
        self.out.flush()

    def _dim(self, text: str) -> str:
        return f"\x1b[2m{text}\x1b[0m" if self.tty else text

    def __call__(self, event: Any) -> None:
        if isinstance(event, ev.Progress):
            line = event.line or f"{event.stage} {event.done}/{event.total}"
            self.out.write(("\r\x1b[K" if self.tty else "") + "  " + line[:76]
                           + ("" if self.tty else "\n"))
            self.out.flush()
            self.progress_open = self.tty
        elif isinstance(event, ev.Message):
            self._line(event.text)
            if event.citations:
                self.citations = event.citations
                width = max(len(c.name) for c in event.citations)
                for i, c in enumerate(event.citations, start=1):
                    self._line(f"  {i}) {c.name.ljust(width)}   {c.folder}"
                               + ("   (matched by name)"
                                  if c.matched_by == "name" else ""))
        elif isinstance(event, ev.Question):
            head = f"Question {event.index} of {event.of}: " if event.of > 1 \
                else ""
            self._line(head + event.text)
            if event.why:
                self._line(self._dim("  " + event.why))
            for i, option in enumerate(event.options, start=1):
                self._line(f"  {i}) {option.label}")
            self._line("  or type your own · s) skip")
        elif isinstance(event, ev.Confirm):
            self._line(event.summary)
            for move in event.moves[:MOVES_SHOWN]:
                self._line(f"  {Path(move.src).name}  →  "
                           f"{_home(str(Path(move.dst).parent))}/")
            if len(event.moves) > MOVES_SHOWN:
                self._line(f"  and {len(event.moves) - MOVES_SHOWN} more")
            if event.sensitive:
                self._line(self._dim("  This touches protected files."))
            self._line("Go ahead? 1) Yes  2) No")
        elif isinstance(event, ev.Counts):
            parts = [f"Indexed {event.indexed}"]
            if event.set_aside:
                parts.append(f"Set aside {event.set_aside}")
            if event.protected + event.held:
                parts.append(f"Protected {event.protected + event.held}")
            if event.open_questions:
                parts.append(f"Questions {event.open_questions}")
            self._line("· " + " · ".join(parts))
        elif isinstance(event, ev.Suggestions):
            for item in event.items:
                self._line(f"  - {item.get('text', '')}")
        elif isinstance(event, ev.Error):
            self._line(event.text)
        # Done carries the undo token for the app; the Message after it is
        # what the person reads.


def _handle(session: Session, renderer: TerminalRenderer, text: str) -> None:
    # The Session maps a reply to whatever is on the screen (yes / no / a
    # number / skip / cancel); the renderer only draws.
    if text.strip().lower() == "cancel":
        session.cancel()
        return
    session.say(text.strip())


def run_terminal(conn, *, folder: Path | None = None, stdin=None, stdout=None,
                 provider_turn=None) -> int:
    stdin = stdin if stdin is not None else sys.stdin
    stdout = stdout if stdout is not None else sys.stdout
    renderer = TerminalRenderer(stdout)
    session = Session(conn, provider_turn=provider_turn, emit=renderer)
    try:
        if folder is not None:
            session.choose_folder(str(folder))
        else:
            session.open()
        return _loop(session, renderer, stdin, stdout)
    except (KeyboardInterrupt, EOFError):
        stdout.write("\n")
        return 0


def _loop(session: Session, renderer: TerminalRenderer, stdin, stdout) -> int:
    while True:
        interactive = getattr(stdin, "isatty", lambda: False)()
        if session.awaiting_key and interactive:
            # A pasted key is never echoed to the screen.
            import getpass
            try:
                line = getpass.getpass("key › ") + "\n"
            except EOFError:
                return 0
        else:
            if getattr(stdout, "isatty", lambda: False)():
                stdout.write("› ")
                stdout.flush()
            line = stdin.readline()
        if not line:
            return 0
        if line.strip().lower() in QUIT:
            return 0
        if not line.strip() and not session.awaiting_key:
            continue
        try:
            _handle(session, renderer, line)
        except KeyboardInterrupt:
            return 0
        except Exception:
            renderer(ev.Error(text="Something went wrong on my side. "
                                   "Nothing changed.", changed=False))


def run_once(conn, text: str, *, stdout=None, provider_turn=None) -> int:
    """`database-agent "where is my CV"`: one answer, then exit."""
    renderer = TerminalRenderer(stdout if stdout is not None else sys.stdout)
    Session(conn, provider_turn=provider_turn, emit=renderer).say(text)
    return 0


def run_events(conn, *, stdin=None, stdout=None, provider_turn=None) -> int:
    """`database-agent --events`: one JSON event per line out, one JSON
    action per line in (design §9)."""
    stdin = stdin if stdin is not None else sys.stdin
    stdout = stdout if stdout is not None else sys.stdout

    def emit(event: Any) -> None:
        stdout.write(ev.to_json(event) + "\n")
        stdout.flush()

    session = Session(conn, provider_turn=provider_turn, emit=emit)
    # The app gets the greeting and the counts without asking for them.
    session.open()
    for line in stdin:
        if not line.strip():
            continue
        try:
            action = json.loads(line)
            kind = action["action"]
            if kind == "say":
                session.say(str(action["text"]))
            elif kind == "open":
                session.open()
            elif kind == "answer":
                value = ("skip" if action.get("skip") else
                         action.get("option_id") or action.get("text") or "")
                session.answer(str(action["question_id"]), str(value))
            elif kind == "confirm":
                yes = action.get("yes", action.get("answer"))
                session.confirm(str(action["confirm_id"]),
                                yes is True or str(yes).lower() == "yes")
            elif kind == "set_level":
                session.set_level(int(action["level"]))
            elif kind == "undo":
                session.undo(str(action["undo_token"]))
            elif kind == "cancel":
                session.cancel()
            else:
                raise ValueError(kind)
        except Exception:
            emit(ev.Error(text="I didn't understand that request. Nothing "
                               "changed.", changed=False))
    return 0
