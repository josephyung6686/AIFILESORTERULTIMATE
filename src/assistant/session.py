"""The conversation engine: history, permission level, confirmations, events.

A `Session` never prints. It hands events (`assistant.events`) to `emit`, and a
renderer draws them. The model decides what to do through tools; this code
delivers: confirmations, permission checks and question rendering are built
here from database rows, never from model text.
"""
from __future__ import annotations

import re
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

YES_WORDS = {"y", "yes", "yeah", "yep", "sure", "ok", "okay", "go ahead",
             "1", "yes please", "sure thing", "go"}

LEVEL_WORDS = {
    1: "OK — I'll ask before moving anything.",
    2: "OK — I'll move up to 20 ordinary files at once without asking, "
       "always with undo. Protected files and bigger changes still ask.",
    3: "OK — I'll move ordinary files you ask for without asking, always "
       "with undo. Protected files and whole-folder changes still ask.",
}


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
        from assistant.conversation_store import recent
        try:
            self.history: list[dict[str, Any]] = recent(conn)
        except sqlite3.Error:
            self.history = []
        self.no_model = False
        self.offering_questions = False
        self.awaiting_folder = False
        self.ask_questions_after_turn = False
        #: Folders the person picked in this conversation; tools may read
        #: these without asking again.
        self.chosen_folders: set[Path] = set()
        #: Set by `cancel()`; the sorter's progress stream checks it.
        self.cancel_requested = False
        self.question_queue: list = []
        self.question_total = 0
        #: confirm_id -> proposal awaiting the person's yes or no.
        self.pending: dict[str, dict] = {}
        self._proposals: list[dict] = []

    # -- opening ---------------------------------------------------------
    def open(self) -> None:
        c = _counts(self.conn)
        if c is not None:
            self.emit(ev.Counts(indexed=c.indexed, set_aside=c.set_aside,
                                protected=c.protected, held=c.held,
                                open_questions=c.open_questions))
        if c is None or c.indexed == 0:
            self.awaiting_folder = True
            self.emit(ev.Message(text=FOLDER_QUESTION))
            return
        self.emit(ev.Message(text=f"I'm looking after {c.indexed} files. "
                                  "What would you like to find or tidy?"))
        from assistant.engine_tools import open_questions
        n = len(open_questions(self.conn))
        if n:
            self.offering_questions = True
            self.emit(ev.Message(
                text=f"While you were away I have {n} "
                     f"question{'s' if n != 1 else ''} — want to go "
                     f"through {'them' if n != 1 else 'it'}?"))

    def choose_folder(self, text: str) -> None:
        """The person's answer to the folder question: index it now."""
        from assistant.engine_tools import check_folder, run_index
        path = Path(text.strip().strip("'\"")).expanduser()
        try:
            self.chosen_folders.add(path.resolve())
        except OSError:
            pass
        folder, refusal = check_folder(self.conn, str(path), self, "index")
        if refusal is not None:
            self.emit(ev.Message(text=refusal.get("error") or
                                 "I can't use that folder."))
            return
        self.awaiting_folder = False
        result = run_index(self.conn, folder, self)
        if not result.get("ok"):
            self.awaiting_folder = True
            self.emit(ev.Error(text=result["error"], changed=False))
            return
        self.emit(ev.Message(text=result["text"] + " What would you like "
                                                   "to find or tidy?"))

    def after_index(self, c) -> None:
        self.emit(ev.Counts(indexed=c.indexed, set_aside=c.set_aside,
                            protected=c.protected, held=c.held,
                            open_questions=c.open_questions))

    def cancel(self) -> None:
        self.cancel_requested = True

    # -- the sorter's questions ------------------------------------------
    def start_questions(self) -> None:
        from assistant.engine_tools import open_questions
        self.offering_questions = False
        self.question_queue = list(open_questions(self.conn))
        self.question_total = len(self.question_queue)
        self._ask_next()

    def _ask_next(self) -> None:
        from assistant.engine_tools import question_event
        if not self.question_queue:
            self.emit(ev.Message(text="That's all the questions for now. "
                                      "Thanks — I'll use your answers when "
                                      "I organise."))
            return
        q = self.question_queue[0]
        index = self.question_total - len(self.question_queue) + 1
        self.emit(question_event(q, index, self.question_total))

    def answer(self, question_id: str, value: str) -> None:
        from assistant.engine_tools import record_person_answer
        try:
            kind = record_person_answer(self.conn, question_id, value)
        except Exception:
            self.emit(ev.Error(text="I couldn't save that answer. Nothing "
                                    "changed.", changed=False))
            return
        self.history.append({"role": "assistant", "content": (
            "The person skipped a question." if kind == "skipped" else
            "The person answered one of the sorter's questions.")})
        self.question_queue = [q for q in self.question_queue
                               if q.question_id != question_id]
        self._ask_next()

    # -- memory and the no-model mode -------------------------------------
    def _remember(self, role: str, text: str) -> None:
        from assistant.conversation_store import save_turn
        try:
            save_turn(self.conn, self.session_id, role, text)
        except sqlite3.Error:
            pass

    def _without_model(self, text: str) -> None:
        from assistant.engine_tools import undo_last
        words = text.strip().lower()
        if words in ("questions", "question") or words.startswith(
                ("questions", "go through the questions")):
            self.start_questions()
            return
        if words.startswith("undo"):
            proposal = undo_last(self.conn)
            if proposal.get("ok"):
                self._propose(proposal["needs_confirmation"])
            else:
                self.emit(ev.Message(text=proposal["error"]))
            return
        for event in route_without_model(self.conn, text):
            self.emit(event)

    # -- a turn ----------------------------------------------------------
    def say(self, text: str) -> None:
        if self.awaiting_folder:
            self.choose_folder(text)
            return
        if self.offering_questions:
            self.offering_questions = False
            if text.strip().lower().rstrip("!.") in YES_WORDS:
                self.history.append({"role": "user", "content": text})
                self.start_questions()
                return
        self.history.append({"role": "user", "content": text})
        self._remember("user", text)
        self._proposals = []
        if self.no_model:
            self._without_model(text)
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
        reply = _strip_citation_line(answer.text)
        self.history.append({"role": "assistant", "content": answer.text})
        self._remember("assistant", reply)
        self.emit(ev.Message(text=reply,
                             citations=self._citations(answer.citations)))
        for proposal in self._proposals:
            self._propose(proposal)
        if self.ask_questions_after_turn:
            self.ask_questions_after_turn = False
            self.start_questions()

    # -- decisions the person makes ---------------------------------------
    def _propose(self, proposal: dict) -> None:
        from assistant.engine_tools import get_level, level_allows
        moves = proposal.get("moves") or []
        if level_allows(get_level(self.conn), proposal["kind"], len(moves),
                        bool(proposal.get("sensitive"))):
            self._execute(proposal)
            return
        confirm_id = uuid.uuid4().hex
        self.pending[confirm_id] = proposal
        self.emit(ev.Confirm(
            confirm_id=confirm_id, summary=proposal["summary"],
            moves=tuple(ev.Move(src=m["from"], dst=m["to"]) for m in moves),
            sensitive=bool(proposal.get("sensitive")),
            undo_available=proposal["kind"] in ("plan", "branch")))

    def _execute(self, proposal: dict) -> None:
        from assistant.engine_tools import execute_confirmed
        try:
            result = execute_confirmed(self.conn, proposal["kind"],
                                       proposal["ref"], context=self)
        except Exception:
            result = {"ok": False, "moved": False, "undo_token": None,
                      "text": "Something went wrong, so I stopped. "
                              "Nothing changed."}
        self.history.append({"role": "assistant", "content": result["text"]})
        if result["ok"]:
            self.emit(ev.Done(moved=bool(result["moved"]),
                              undo_token=result.get("undo_token")))
            self.emit(ev.Message(text=result["text"]))
        else:
            self.emit(ev.Error(text=result["text"],
                               changed=bool(result["moved"])))

    def confirm(self, confirm_id: str, yes: bool) -> None:
        proposal = self.pending.pop(confirm_id, None)
        if proposal is None:
            self.emit(ev.Message(text="That question has already been "
                                      "answered. Nothing changed."))
            return
        if not yes:
            self._capture_no(proposal)
            self.history.append({"role": "assistant",
                                 "content": "Cancelled. Nothing moved."})
            self.emit(ev.Message(text="Cancelled. Nothing moved."))
            return
        self._execute(proposal)

    def _capture_no(self, proposal: dict) -> None:
        """A declined sort is a correction the product learns from (dark
        until its release gate passes)."""
        if proposal["kind"] != "plan":
            return
        try:
            from assistant.memory_l0 import capture_reject
            items = [r[0] for r in self.conn.execute(
                "SELECT item_id FROM assistant_plan_ops WHERE plan_id = ?",
                (proposal["ref"],))]
            capture_reject(self.conn, ai_proposal={
                "action": "quick_sort", "plan_id": proposal["ref"],
                "moves": proposal.get("moves") or []},
                item_ids=items, reason="person said no")
            self.conn.commit()
        except Exception:
            pass

    def undo(self, undo_token: str) -> None:
        from assistant.engine_tools import undo_proposal
        proposal = undo_proposal(self.conn, undo_token)
        if not proposal.get("ok"):
            self.emit(ev.Message(text=proposal["error"]))
            return
        self._propose(proposal["needs_confirmation"])

    def set_level(self, n: int) -> None:
        from assistant.engine_tools import LEVELS, put_setting
        if n not in LEVELS:
            self.emit(ev.Message(text="The levels are 1, 2 and 3."))
            return
        put_setting(self.conn, "permission_level", str(n))
        self.emit(ev.Message(text=LEVEL_WORDS[n]))

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
                              egress_class="cloud", engine=True,
                              engine_context=self)
        self._proposals = runtime.pending_confirmations
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


NO_MODEL_HELP = ("Without the AI model I can: find <name>, where is <name>, "
                 "status, show skipped, show protected, questions, undo, help.")

_FIND = re.compile(r"^(find|where('s| is)|search( for)?)\b\s*(my\s+)?",
                   re.IGNORECASE)


def route_without_model(conn: sqlite3.Connection, text: str) -> list:
    """The deterministic answers that need no model. Everything shown here
    is rendered on this Mac; nothing is sent anywhere."""
    from assistant.engine_tools import counts_sentence
    words = text.strip()
    lower = words.lower().rstrip("?!.")
    match = _FIND.match(words)
    if match:
        return [_find_locally(conn, words[match.end():].strip(" ?!."))]
    if lower in ("status", "what have you got", "what have you got?"):
        c = _counts(conn)
        return [ev.Message(text=counts_sentence(c) if c is not None else
                           "Nothing is indexed yet. " + FOLDER_QUESTION)]
    if lower in ("show skipped", "show protected"):
        return [_excluded_list(conn, protected=lower.endswith("protected"))]
    return [ev.Message(text=NO_MODEL_HELP)]


def _find_locally(conn: sqlite3.Connection, query: str):
    from items.file_identity import item_is_sensitive
    from items.hot_index import find_files
    if not query:
        return ev.Message(text="What should I look for?")
    try:
        hits = find_files(conn, query, limit=8).hits
    except Exception:
        hits = ()
    if not hits:
        return ev.Message(text=f"I couldn't find anything matching {query}.")
    citations, protected = [], 0
    for hit in hits:
        row = conn.execute("SELECT open_target FROM items WHERE item_id = ?",
                           (hit.item_id,)).fetchone()
        target = row[0] if row is not None else None
        if hit.protected or item_is_sensitive(conn, hit.item_id):
            protected += 1
        citations.append(ev.Citation(name=hit.display_label,
                                     folder=_folder_of(target),
                                     open_target=target))
    line = f"Found {len(citations)}:"
    if protected:
        line += (f" ({protected} protected — shown only to you, never "
                 "sent anywhere)")
    return ev.Message(text=line, citations=tuple(citations))


def _excluded_list(conn: sqlite3.Connection, *, protected: bool):
    try:
        from items.identity import excluded_areas
        areas = [a for a in excluded_areas(conn)
                 if bool(a["protected"]) == protected]
    except Exception:
        areas = []
    if not areas:
        return ev.Message(text="Nothing is protected." if protected else
                          "Nothing is set aside.")
    head = ("Protected — never opened:" if protected else
            "Set aside — kept as one item each, nothing inside is moved:")
    return ev.Message(text=head, citations=tuple(
        ev.Citation(name=Path(a["folder"]).name, folder=_folder_of(
            a["folder"]), open_target=a["folder"]) for a in areas))


def _strip_citation_line(text: str) -> str:
    """The model's `Citations:` line carries internal ids; the person gets
    the citations as names instead."""
    return "\n".join(line for line in text.splitlines()
                     if not line.lower().startswith("citations:")).strip()
