"""The conversation engine: history, permission level, confirmations, events.

A `Session` never prints. It hands events (`assistant.events`) to `emit`, and a
renderer draws them. The model decides what to do through tools; this code
delivers: confirmations, permission checks and question rendering are built
here from database rows, never from model text.
"""
from __future__ import annotations

import re
import threading
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Callable

from assistant import events as ev

#: History is trimmed to this many characters before each model call. The
#: oldest tool payloads go first; the person's words and the replies stay.
HISTORY_BUDGET = 60_000
DROPPED = "[earlier result dropped]"

FOLDER_QUESTION = (
    "I'll read file names and text here to build a private index on this "
    "Mac. Nothing moves unless you say yes. macOS may ask to allow access — "
    "choose Allow.\n"
    "Which folder should I look after?\n"
    "  1) Desktop\n  2) Documents\n  3) Downloads\n  or type a path")
FOLDER_CHOICES = {"1": "~/Desktop", "2": "~/Documents", "3": "~/Downloads",
                  "desktop": "~/Desktop", "documents": "~/Documents",
                  "downloads": "~/Downloads"}

KEY_PROMPT = ("Paste a DeepSeek key to chat, or press Enter to keep going "
              "without one — I can still find files and undo.")
NO_MODEL_LINE = ("No AI model is set up, so I can find files, show what "
                 "I've got and undo — paste a DeepSeek key any time to chat.")
PROVIDER_NAMES = {"deepseek": "DeepSeek", "openai": "OpenAI",
                  "anthropic": "Anthropic"}

YES_WORDS = {"y", "yes", "yeah", "yep", "sure", "ok", "okay", "go ahead",
             "1", "yes please", "sure thing", "go"}
NO_WORDS = {"n", "no", "nope", "nah", "2", "no thanks", "don't", "dont"}
#: Commands, never answers: they cancel what is on the screen.
CANCEL_WORDS = {"cancel", "stop", "never mind", "nevermind", "forget it"}
SKIP_WORDS = {"s", "skip", "skip it", "not now", "later"}
#: A bare undo: code asks about the last batch, the model never words it.
UNDO_WORDS = {"undo", "undo something", "undo that", "undo it", "undo this",
              "put it back", "put them back", "put those back"}
_YES_FIRST = {"y", "yes", "yeah", "yep", "yup", "sure", "ok", "okay", "go"}
_NO_FIRST = {"n", "no", "nope", "nah"}
#: A reply with any of these is more than a yes or a no: the model reads it.
_MORE_THAN_YES_NO = re.compile(
    r"\?|\b(but|only|except|instead|which|what|why|how|where|wait)\b")


def yes_or_no(text: str) -> bool | None:
    """True / False when the whole reply is a plain yes or no, else None."""
    words = text.strip().lower().rstrip("!.")
    if words in YES_WORDS:
        return True
    if words in NO_WORDS:
        return False
    tokens = re.findall(r"[a-z']+|\d+", words)
    if not tokens or len(tokens) > 6 or _MORE_THAN_YES_NO.search(words):
        return None
    if tokens[0] in _NO_FIRST:
        return False
    if tokens[0] in _YES_FIRST or "yes" in tokens:
        return True
    return None


#: A sentence telling the person something waits on their screen. Removed
#: from a reply whenever nothing does: code knows, the model guesses.
_PROMPT_CLAIM = re.compile(
    r"\b(on|in front of) (your |the )?screen\b|\bwaiting (on|for) (you|your)\b"
    r"|\bstill waiting\b|\b(tap|press|click) (yes|no|the button|it)\b"
    r"|\bup for (your )?(confirmation|a yes)|\b(asked|ask) you to confirm\b"
    r"|\bsay \W*yes\W* (and|to|if)\b|\bwaiting for a yes\b",
    re.IGNORECASE)


def drop_prompt_claims(text: str) -> str:
    out = []
    for line in text.splitlines():
        parts = re.split(r"(?<=[.!?])\s+", line)
        kept = [p for p in parts if not _PROMPT_CLAIM.search(p)]
        if line.strip() and not kept:
            continue
        out.append(" ".join(kept))
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()

#: "I don't see those names myself" — false once the list is on screen.
_DISOWNS_LIST = re.compile(
    r"\bI (don'?t|do not|can'?t|cannot) see (those|these|the|their|any)"
    r" (file )?names\b", re.IGNORECASE)


#: "I can't point to a location" -- false when the Session shows it next.
_CANT_LOCATE = re.compile(
    r"\b(can'?t|cannot|unable to) (point to|tell you|say|give|share|show)"
    r" (you )?(a |the |its |exact |where)\w*", re.IGNORECASE)
PROTECTED_HITS_LINE = ("I can't read it or send it to the AI — here it is "
                       "for you:")


def _drop_sentences(text: str, pattern: re.Pattern) -> str:
    out = []
    for line in text.splitlines():
        parts = re.split(r"(?<=[.!?])\s+", line)
        kept = [p for p in parts if not pattern.search(p)]
        if line.strip() and not kept:
            continue
        out.append(" ".join(kept))
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()


#: A sentence saying a search found nothing.
_NOT_FOUND = re.compile(
    r"\b(didn'?t|did not|couldn'?t|could not|can'?t|cannot|don'?t|do not)"
    r" (find|see|have)\b|\bnot found\b|\bno (\w+ ){0,3}(exists?|found)\b"
    r"|\bcame up empty\b|\bnothing (matched|came up)\b", re.IGNORECASE)


def not_found_corrected(text: str, protected: int) -> str:
    """When protected files matched this turn, a "not found" is false: the
    sentence goes and the true one, from code state, leads the reply."""
    kept = []
    dropped = False
    for line in text.splitlines():
        parts = re.split(r"(?<=[.!?])\s+", line)
        keep = [p for p in parts if not _NOT_FOUND.search(p)]
        dropped = dropped or len(keep) != len(parts)
        if line.strip() and not keep:
            continue
        kept.append(" ".join(keep))
    if not dropped:
        return text
    files = ("1 protected file" if protected == 1 else
             f"{protected} protected files")
    open_n = "open 1" if protected == 1 else f"open 1 to open {protected}"
    lead = (f"{files} matched — listed below, shown only to you. Say "
            f"{open_n} to see {'it' if protected == 1 else 'them'}.")
    rest = re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip()
    return lead + ("\n" + rest if rest else "")


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


_NUM = r"\d[\d,]*(?:\s*[–-]\s*\d[\d,]*)?"
_PROTECTED_BEFORE = re.compile(
    rf"\b{_NUM}(?=\s+(?:\w+\s+){{0,2}}(?:protected|held)\b)", re.IGNORECASE)
_PROTECTED_AFTER = re.compile(
    rf"(\bprotected(?: files)?\s*(?:\(|:\s*)){_NUM}", re.IGNORECASE)


def agree_protected_count(text: str, c) -> str:
    """The model's protected number, made the index's number. The Session's
    counts line is the one authority for what the person reads."""
    if c is None:
        return text
    now = str(c.protected)  # held files are already inside it

    def agree(sentence: str) -> str:
        if _A_SEARCH.search(sentence):
            # How many matched a search is not the index's total.
            return sentence
        sentence = _PROTECTED_BEFORE.sub(now, sentence)
        return _PROTECTED_AFTER.sub(lambda m: m.group(1) + now, sentence)
    return "\n".join(
        " ".join(agree(p) for p in re.split(r"(?<=[.!?])\s+", line))
        for line in text.split("\n"))


_A_SEARCH = re.compile(r"\bmatch(ed|es|ing)?\b|\bsearch\b|\bcame up\b",
                       re.IGNORECASE)


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


def _key_file() -> Path:
    return Path.home() / ".graph-agent" / ".env"


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
        self._emit = emit
        #: The last files shown, for `open N` / `show N`.
        self.last_citations: tuple[ev.Citation, ...] = ()
        self.session_id = session_id or str(uuid.uuid4())
        from assistant.conversation_store import recent
        try:
            self.history: list[dict[str, Any]] = recent(conn)
        except sqlite3.Error:
            self.history = []
        self.no_model = False
        self.awaiting_key = False
        #: Undo choices offered by a bare `undo`: number -> token.
        self.undo_choices: dict[str, str] = {}
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
        #: The one yes/no prompt on the person's screen, and the one sorter
        #: question being asked: what the chat may say is waiting.
        self.on_screen: str | None = None
        self.asking: ev.Question | None = None
        self._proposals: list[dict] = []
        self._protected_hits: tuple[str, ...] = ()
        #: Lists a tool built for the person's eyes only, shown after the
        #: reply and never part of a model request.
        self._shown_locally: list = []
        self._opened = False
        #: Document text is read once per session, after the first index.
        self._reading_started = False
        self.reader = None
        #: The last moved batch's undo token, for `undo_last` and `undo`.
        self.last_undo_token: str | None = None
        #: Held while the Session answers; the background reader's events
        #: wait for it, so they never land inside a reply.
        self._turn_lock = threading.RLock()

    def emit(self, event) -> None:
        with self._turn_lock:
            self._emit_now(event)

    def _emit_now(self, event) -> None:
        if isinstance(event, ev.Progress) and event.line:
            line = scrub_developer_text(event.line) or "Working…"
            event = ev.Progress(stage=event.stage, done=event.done,
                                total=event.total, line=line)
        if isinstance(event, ev.Message) and event.citations:
            self.last_citations = event.citations
        self._emit(event)

    def show_locally(self, event) -> None:
        self._shown_locally.append(event)

    def _provider_name(self) -> str | None:
        """Who answers, or None when no model is set up."""
        if self.provider_turn is not None:
            return "DeepSeek"
        try:
            from assistant.provider import load_dotenv, resolve_provider
            load_dotenv(_key_file())
            cfg = resolve_provider()
        except Exception:
            return None
        return PROVIDER_NAMES.get(cfg.provider, cfg.provider)

    # -- opening ---------------------------------------------------------
    def open(self) -> None:
        """The greeting, once: a second call (the app's `open` action after
        `--events` already opened) changes nothing."""
        with self._turn_lock:
            self._open()

    def _open(self) -> None:
        if self._opened:
            return
        self._opened = True
        if self._provider_name() is None:
            self.awaiting_key = True
            self.emit(ev.Message(text=KEY_PROMPT))
            return
        self._open_rest()

    def _take_key(self, text: str) -> None:
        """A pasted key goes to ~/.graph-agent/.env (0600), never into the
        database, the history or any event."""
        import os
        self.awaiting_key = False
        key = text.strip()
        if not key:
            self.no_model = True
            self.emit(ev.Message(text=NO_MODEL_LINE))
            self._open_rest()
            return
        if " " in key or len(key) < 20:
            self.awaiting_key = True
            self.emit(ev.Message(text="That doesn't look like a key. " +
                                      KEY_PROMPT))
            return
        path = _key_file()
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        lines = []
        if path.exists():
            lines = [line for line in path.read_text().splitlines()
                     if not line.startswith("DEEPSEEK_API_KEY=")]
        lines.append(f"DEEPSEEK_API_KEY={key}")
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as fh:
            fh.write("\n".join(lines) + "\n")
        os.chmod(path, 0o600)
        os.environ["DEEPSEEK_API_KEY"] = key
        self.no_model = False
        self.emit(ev.Message(text="Key saved on this Mac only."))
        self._open_rest()

    def _open_rest(self) -> None:
        c = _counts(self.conn)
        if c is not None:
            self.emit(self._counts_event(c))
        if c is None or c.indexed == 0:
            self.awaiting_folder = True
            self.emit(ev.Message(text=FOLDER_QUESTION))
            return
        self._greet(c)
        if getattr(c, "unread_documents", 0) and not self._reading_started:
            # Reading resumes in every session until every file is read.
            self._reading_started = True
            self.reader = start_reading(self.conn, self.emit)
        from assistant.engine_tools import open_questions
        n = len(open_questions(self.conn))
        if n:
            self.offering_questions = True
            self.emit(ev.Message(
                text=f"While you were away I have {n} "
                     f"question{'s' if n != 1 else ''} — want to go "
                     f"through {'them' if n != 1 else 'it'}?"))

    def _greet(self, c) -> None:
        from assistant.engine_tools import counts_sentence
        lines = [counts_sentence(c)]
        name = None if self.no_model else self._provider_name()
        if name:
            lines.append(f"Questions and file snippets go to {name} to answer "
                         f"you. Protected files ({c.protected}) "
                         "never leave this Mac.")
        lines.append("What would you like to find or tidy?")
        self.emit(ev.Message(text="\n".join(lines)))
        try:
            from items.suggest import suggestions
            items = suggestions(self.conn)
        except Exception:
            items = []
        if items:
            self.emit(ev.Suggestions(items=tuple(items)))

    def choose_folder(self, text: str) -> None:
        """The person's answer to the folder question: index it now."""
        with self._turn_lock:
            self._choose_folder(text)

    def _choose_folder(self, text: str) -> None:
        from assistant.engine_tools import check_folder, run_index
        typed = text.strip().strip("'\"")
        typed = FOLDER_CHOICES.get(typed.lower(), typed)
        path = Path(typed).expanduser()
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
        c = _counts(self.conn)
        if c is not None:
            self._greet(c)
        else:
            self.emit(ev.Message(text=result["text"]))

    def _counts_event(self, c) -> ev.Counts:
        """The totals line. Its question count is the one the chat says
        ("I have N questions"): the questions a person can answer."""
        from assistant.engine_tools import open_questions
        try:
            asked = len(open_questions(self.conn))
        except Exception:
            asked = c.open_questions
        return ev.Counts(indexed=c.indexed, set_aside=c.set_aside,
                         protected=c.protected, held=c.held,
                         open_questions=asked)

    def after_index(self, c) -> None:
        self.emit(self._counts_event(c))
        if not self._reading_started:
            self._reading_started = True
            self.reader = start_reading(self.conn, self.emit)

    def cancel(self) -> None:
        """`cancel`: No to the prompt on screen, or stop the questions, or
        stop organising."""
        if self.on_screen in self.pending:
            self.confirm(self.on_screen, False)
        elif self.asking is not None:
            self._stop_questions()
        else:
            self.cancel_requested = True

    def _stop_questions(self) -> None:
        self.asking = None
        self.question_queue = []
        line = "Stopped the questions. Nothing was recorded for that one."
        self._note(line)
        self.emit(ev.Message(text=line))

    def _note(self, text: str) -> None:
        """A code-written line in the conversation's record, so the model
        (now and in later sessions) knows what really happened."""
        self.history.append({"role": "assistant", "content": text})
        self._remember("assistant", text)

    # -- the sorter's questions ------------------------------------------
    def start_questions(self) -> None:
        from assistant.engine_tools import open_questions
        self.offering_questions = False
        self.question_queue = list(open_questions(self.conn))
        self.question_total = len(self.question_queue)
        self._ask_next()

    def _ask_next(self) -> None:
        from assistant.engine_tools import question_event
        self.asking = None
        if not self.question_queue:
            self.emit(ev.Message(text="That's all the questions for now. "
                                      "Thanks — I'll use your answers when "
                                      "I organise."))
            return
        q = self.question_queue[0]
        index = self.question_total - len(self.question_queue) + 1
        self.asking = question_event(q, index, self.question_total,
                                     self.conn)
        self.emit(self.asking)

    def answer(self, question_id: str, value: str) -> None:
        from assistant.engine_tools import record_person_answer
        try:
            kind = record_person_answer(self.conn, question_id, value)
        except Exception:
            self.emit(ev.Error(text="I couldn't save that answer. Nothing "
                                    "changed.", changed=False))
            return
        if self.asking is not None and self.asking.question_id == question_id:
            self.asking = None
        self._note("The person skipped a question." if kind == "skipped" else
                   "The person answered one of the sorter's questions.")
        self.question_queue = [q for q in self.question_queue
                               if q.question_id != question_id]
        self._ask_next()

    # -- deterministic commands -------------------------------------------
    def _local_command(self, text: str) -> bool:
        """`open N`, `show N` and the undo history: code, never the model."""
        words = text.strip().lower()
        match = re.fullmatch(r"(open|show)\s+(\d+)", words)
        if match and self.last_citations:
            n = int(match.group(2))
            if not 1 <= n <= len(self.last_citations):
                self.emit(ev.Message(text=f"Pick a number from 1 to "
                                          f"{len(self.last_citations)}."))
                return True
            target = self.last_citations[n - 1].open_target
            if not target:
                self.emit(ev.Message(text="I can't open that one."))
                return True
            if not open_in_finder(target, reveal=match.group(1) == "show"):
                self.emit(ev.Message(
                    text="I can't open files on this Mac from here — the "
                         f"file is at {_folder_of(target)}/"
                         f"{Path(target).name}"))
            return True
        if words in self.undo_choices:
            token = self.undo_choices[words]
            self.undo_choices = {}
            self.undo(token)
            return True
        self.undo_choices = {}
        if words.rstrip("!.") in UNDO_WORDS:
            from assistant.engine_tools import recent_batches
            batches = recent_batches(self.conn)
            token = self.last_undo_token or ""
            if token.startswith("branch:"):
                # A folder of the plan moved by the sorter: not in the
                # assistant's own batches, so offered first from here.
                batches.insert(0, {"token": token, "text": "the files moved "
                                   "into " + token.rpartition("|")[2]})
            if not batches:
                self.emit(ev.Message(text="There's nothing I moved to put "
                                          "back."))
                return True
            if len(batches) == 1:
                # One batch: nothing to pick, so ask once about it.
                self.undo(batches[0]["token"])
                return True
            self.undo_choices = {str(i): b["token"]
                                 for i, b in enumerate(batches, start=1)}
            listing = "\n".join(f"  {i}) {b['text']}"
                                for i, b in enumerate(batches, start=1))
            self.emit(ev.Message(text="Which batch should I put back?\n"
                                      + listing))
            return True
        return False

    # -- memory and the no-model mode -------------------------------------
    def _remember(self, role: str, text: str) -> None:
        from assistant.conversation_store import save_turn
        try:
            save_turn(self.conn, self.session_id, role, text)
        except sqlite3.Error:
            pass

    @staticmethod
    def _routes_without_model(text: str) -> bool:
        words = text.strip().lower().rstrip("?!.")
        return bool(_FIND.match(text.strip())) or words.startswith(
            ("undo", "questions", "go through the questions")) or words in (
            "question", "status", "what have you got", "show protected",
            "show skipped")

    def _without_model(self, text: str) -> None:
        from assistant.engine_tools import undo_last
        words = text.strip().lower()
        if words in ("questions", "question") or words.startswith(
                ("questions", "go through the questions")):
            self.start_questions()
            return
        if words.startswith("undo"):
            proposal = undo_last(self.conn, self)
            if proposal.get("ok"):
                self._propose(proposal["needs_confirmation"])
            else:
                self.emit(ev.Message(text=proposal["error"]))
            return
        for event in route_without_model(self.conn, text):
            self.emit(event)

    # -- a turn ----------------------------------------------------------
    def say(self, text: str) -> None:
        with self._turn_lock:
            self._say(text)

    def _say(self, text: str) -> None:
        if self.awaiting_key:
            self._take_key(text)
            return
        if self._reply_to_screen(text):
            return
        if self._local_command(text):
            return
        if self.awaiting_folder:
            self.choose_folder(text)
            return
        if self.offering_questions:
            self.offering_questions = False
            if text.strip().lower().rstrip("!.") in YES_WORDS:
                self.history.append({"role": "user", "content": text})
                self.start_questions()
                return
        self._drop_stale_prompt()
        self.history.append({"role": "user", "content": text})
        self._remember("user", text)
        self._proposals = []
        self._protected_hits = ()
        self._shown_locally = []
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
            # A find, status or undo is answered now too, as every later
            # message is: by code. Anything else waits for the next one.
            if self._routes_without_model(text):
                self._without_model(text)
            return
        # The model's own question is a plain question, not a choice prompt:
        # nothing waits on the screen for it.
        said = re.sub(r"^Need your answer:\s*", "", answer.text)
        reply = agree_protected_count(plain_reply(
            self.conn, scrub_developer_text(strip_id_fragments(
                self.conn, _strip_citation_line(said)))),
            _counts(self.conn)) or "OK."
        if self._shown_locally:
            # The Session put the list on screen; the reply never disowns it.
            reply = _drop_sentences(reply, _DISOWNS_LIST) or "OK."
        if not self._prompt_will_show():
            reply = drop_prompt_claims(reply) or "OK."
        if self._protected_hits:
            reply = not_found_corrected(
                _drop_sentences(reply, _CANT_LOCATE) or "OK.",
                len(self._protected_hits))
        self.history.append({"role": "assistant", "content": reply})
        self._remember("assistant", reply)
        if reply != "OK." or not (self._shown_locally or
                                  self._protected_hits):
            # A reply emptied by the checks above, with a list of its own
            # on screen: the list is the answer, not a bare "OK.".
            self.emit(ev.Message(text=reply, citations=self._citations(
                self._shown_citations(answer, reply))))
        if self._protected_hits:
            # Protected matches are shown here, from the database, and never
            # through the model's reply.
            self.emit(ev.Message(text=PROTECTED_HITS_LINE,
                                 citations=self._citations(
                                     self._protected_hits)))
        for event in self._shown_locally:
            self.emit(event)
        shown_before = self.on_screen
        for proposal in self._proposals:
            self._propose(proposal)
        if self.ask_questions_after_turn:
            self.ask_questions_after_turn = False
            self.start_questions()
            return
        if self.on_screen in self.pending and self.on_screen == shown_before:
            proposal = self.pending[self.on_screen]
            proposal["reminded"] = True
            self.emit(ev.Message(text=f"Still waiting for your yes or no: "
                                      f"{proposal['summary']}  1) Yes  "
                                      "2) No"))
        elif self.asking is not None and self.on_screen not in self.pending:
            # One prompt at a time: a yes/no on screen hides the question
            # until it is answered.
            self._ask_again()

    def _drop_stale_prompt(self) -> None:
        """Every yes/no is reminded once; a second reply that does not
        answer it drops it, so it never trails the conversation."""
        proposal = self.pending.get(self.on_screen or "")
        if proposal is None or not proposal.get("reminded"):
            return
        self.pending.pop(self.on_screen)
        self.on_screen = None
        line = (f"Not done: {proposal['summary'].rstrip('?.')}. "
                f"{_nothing(proposal)} Ask again if you still want it.")
        self._note(line)
        self.emit(ev.Message(text=line))

    def _prompt_will_show(self) -> bool:
        """Whether, after this turn, something waits on the person's screen."""
        from assistant.engine_tools import get_level, level_allows
        if self.on_screen in self.pending or self.asking is not None:
            return True
        if self.ask_questions_after_turn:
            return True
        level = get_level(self.conn)
        return any(not level_allows(level, p["kind"],
                                    len(p.get("moves") or ()),
                                    bool(p.get("sensitive")))
                   for p in self._proposals)

    def _ask_again(self) -> None:
        """The question stays on screen unless the model recorded an answer
        to it this turn; then the next one is asked."""
        from assistant.engine_tools import open_questions
        asked = self.asking
        if asked.question_id in {q.question_id
                                 for q in open_questions(self.conn)}:
            self.emit(asked)
            return
        self.question_queue = [q for q in self.question_queue
                               if q.question_id != asked.question_id]
        self._ask_next()

    def _reply_to_screen(self, text: str) -> bool:
        """A reply to the prompt or question on screen, mapped by code.
        False for anything else: the model then reads it, told what is on
        the screen, and the prompt stays."""
        words = text.strip().lower().rstrip("!.")
        if self._maps_to_screen(words, text):
            # The person's own reply goes in the record, then what happened.
            self.history.append({"role": "user", "content": text.strip()})
            self._remember("user", text.strip())
        if self.on_screen in self.pending:
            if words in CANCEL_WORDS:
                self.confirm(self.on_screen, False)
                return True
            answer = yes_or_no(text)
            if answer is None:
                return False
            self.confirm(self.on_screen, answer)
            return True
        if self.asking is not None:
            q = self.asking
            if words in CANCEL_WORDS:
                self._stop_questions()
                return True
            if words in SKIP_WORDS:
                self.answer(q.question_id, "skip")
                return True
            if words.isdigit() and 1 <= int(words) <= len(q.options):
                self.answer(q.question_id, q.options[int(words) - 1].id)
                return True
            match = next((o for o in q.options
                          if o.label.casefold() == words.casefold()), None)
            if match is not None:
                self.answer(q.question_id, match.id)
                return True
        return False

    def _maps_to_screen(self, words: str, text: str) -> bool:
        if self.on_screen in self.pending:
            return words in CANCEL_WORDS or yes_or_no(text) is not None
        if self.asking is not None:
            q = self.asking
            return (words in CANCEL_WORDS or words in SKIP_WORDS
                    or (words.isdigit() and 1 <= int(words) <= len(q.options))
                    or any(o.label.casefold() == words.casefold()
                           for o in q.options))
        return False

    def screen_state(self) -> str:
        """What is on the person's screen, for the model, from code state."""
        if self.on_screen in self.pending:
            summary = self.pending[self.on_screen]["summary"]
            return ("On the person's screen right now: a yes/no prompt — "
                    f"“{summary}”. Their newest message did not answer it, "
                    "so it stays; they answer it by saying yes or no.")
        if self.asking is not None:
            from assistant.registry import ENGINE_TOOLS
            record = ("call answer_question with their words"
                      if "answer_question" in ENGINE_TOOLS else
                      "tell them to pick a number or type s to skip")
            printed = "\n".join(ev.question_lines(self.asking))
            return ("On the person's screen right now is this question, "
                    "exactly as printed (nothing else about it is shown; "
                    "a file not named here is not on the screen):\n"
                    f"{printed}\nIf their newest message answers it, "
                    f"{record}; if they ask about it, explain and leave it "
                    "open.")
        return ("Nothing is waiting on the person's screen right now: no "
                "yes/no prompt and no question. Never say something is "
                "waiting for them. A prompt earlier in the conversation that "
                "has no answer after it was dropped and did not happen; if "
                "the person wants it now, call the tool again.")

    # -- decisions the person makes ---------------------------------------
    def _propose(self, proposal: dict) -> None:
        from assistant.engine_tools import get_level, level_allows
        if proposal["kind"] == "cloud":
            proposal = {**proposal, "summary": self._cloud_summary(
                proposal["ref"])}
        moves = proposal.get("moves") or []
        if level_allows(get_level(self.conn), proposal["kind"], len(moves),
                        bool(proposal.get("sensitive"))):
            self._execute(proposal)
            return
        if self.on_screen in self.pending:
            old = self.pending.pop(self.on_screen)
            line = (f"Cancelled: {old['summary'].rstrip('?.')}. "
                    f"{_nothing(old)}")
            self._note(line)
            self.emit(ev.Message(text=line))
        confirm_id = uuid.uuid4().hex
        self.pending[confirm_id] = proposal
        self.on_screen = confirm_id
        self.emit(ev.Confirm(
            confirm_id=confirm_id, summary=proposal["summary"],
            moves=tuple(ev.Move(src=m["from"], dst=m["to"]) for m in moves),
            sensitive=bool(proposal.get("sensitive")),
            undo_available=proposal["kind"] in ("plan", "branch")))

    def _cloud_summary(self, folder: str) -> str:
        """The AI-permission question, built here: who reads the excerpts
        and what a no does."""
        from assistant.engine_tools import _home_words
        name = self._provider_name() or "the AI"
        return (f"Organising works much better if the AI ({name}) reads "
                "short excerpts of your ordinary files — never protected "
                f"ones. Allow for {_home_words(Path(folder))}? No: I'll "
                "organise without the AI; the result will be rougher.")

    def _execute(self, proposal: dict) -> None:
        from assistant.engine_tools import execute_confirmed
        before = _before_moving(self.conn, proposal)
        try:
            result = execute_confirmed(self.conn, proposal["kind"],
                                       proposal["ref"], context=self)
        except Exception:
            result = {"ok": False, "moved": False, "undo_token": None,
                      "text": "Something went wrong, so I stopped. "
                              "Nothing changed."}
        if result.get("ok") and proposal["kind"] in ("plan", "undo",
                                                     "branch"):
            result = _as_moved(self.conn, proposal, before, result)
        if result.get("needs_confirmation"):
            # The step needs one more yes (organise asking about the cloud).
            self._propose(result["needs_confirmation"])
            return
        if _forgets_conversations(proposal) and result["ok"]:
            # Forgotten means forgotten now, not from the next session; the
            # model still learns that it happened (this session only).
            self.history = [{"role": "assistant", "content": result["text"]}]
        elif not _forgets_conversations(proposal):
            self._note(result["text"])
        if result["ok"] and result.get("undo_token"):
            self.last_undo_token = result["undo_token"]
        elif result["ok"] and proposal["kind"] == "undo" and (
                proposal["ref"] == self.last_undo_token):
            self.last_undo_token = None
        if result["ok"]:
            self.emit(ev.Done(moved=bool(result["moved"]),
                              undo_token=result.get("undo_token")))
            self.emit(ev.Message(text=result["text"]))
        else:
            self.emit(ev.Error(text=result["text"],
                               changed=bool(result["moved"])))
        if self.ask_questions_after_turn and self.on_screen not in (
                self.pending):
            # "I have N questions" is followed by question 1, now.
            self.ask_questions_after_turn = False
            self.start_questions()

    def confirm(self, confirm_id: str, yes: bool) -> None:
        with self._turn_lock:
            self._confirm_shown(confirm_id, yes)

    def _confirm_shown(self, confirm_id: str, yes: bool) -> None:
        hidden = self.asking
        self._confirm(confirm_id, yes)
        if hidden is not None and self.asking is hidden and (
                self.on_screen not in self.pending):
            # The question the yes/no had hidden comes back (a question
            # asked during the step was already shown).
            self.emit(self.asking)

    def _confirm(self, confirm_id: str, yes: bool) -> None:
        proposal = self.pending.pop(confirm_id, None)
        if confirm_id == self.on_screen:
            self.on_screen = None
        if proposal is None:
            self.emit(ev.Message(text="That question has already been "
                                      "answered. Nothing changed."))
            return
        if not yes and proposal.get("on_no"):
            # A no that has its own next step (organise without the cloud).
            self._capture_no(proposal)
            self._execute(proposal["on_no"])
            return
        if not yes:
            self._capture_no(proposal)
            line = f"Cancelled. {_nothing(proposal)}"
            self._note(line)
            self.emit(ev.Message(text=line))
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
            from assistant.provider import load_dotenv, resolve_provider
            load_dotenv(_key_file())
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
        from assistant.conversation_store import forgot_line
        forgot = forgot_line(self.conn)
        messages = [{"role": "system",
                     "content": build_system_prompt(self.conn, text)
                     + "\n" + PLAIN_WORDS + "\n"
                     + (forgot + "\n" if forgot else "")
                     + self.screen_state()},
                    *self.history]
        # `converse` appends the model turns and tool replies to the history;
        # `_trim` drops those tool replies before the next turn.
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
        self._protected_hits = tuple(runtime.protected_hits)
        return answer

    def _trim(self) -> None:
        """Before each turn: earlier turns' tool results are dropped (the
        replies built from them stay), then the oldest words if still over
        budget. Each request then carries one turn's results, not all."""
        for m in self.history:
            if m["role"] == "tool":
                m["content"] = DROPPED

        def total() -> int:
            return sum(len(str(m.get("content") or "")) for m in self.history)
        for m in self.history:
            if total() < HISTORY_BUDGET:
                return
            if m["role"] == "tool" and m.get("content") != DROPPED:
                m["content"] = DROPPED

    def _shown_citations(self, answer, reply: str) -> list[str]:
        """The files listed under a reply: the ones the model cited, then
        the ones it named -- nothing else, so a list never pads a reply
        that names no file. A reply saying nothing was found lists only
        files it names."""
        from assistant.policy import parse_answer_citations
        # A citation line the model garbled leaves no valid ids; the
        # search's own matches are still the pool to choose from.
        ids = list(answer.citations) or list(dict.fromkeys(
            o.item_id for o in answer.citation_objs))
        claimed = [] if _NOT_FOUND.search(reply) else [
            i for i in parse_answer_citations(answer.text) if i in ids]
        said = reply.casefold()
        rows = {}
        for item_id in ids:
            row = self.conn.execute(
                "SELECT display_label, open_target FROM items "
                "WHERE item_id = ?", (item_id,)).fetchone()
            if row is not None:
                rows[item_id] = row
        named = [i for i in ids if i in rows and rows[i][0]
                 and rows[i][0].casefold() in said]
        return list(dict.fromkeys(claimed + named))

    def _citations(self, item_ids) -> tuple[ev.Citation, ...]:
        out = []
        for item_id in item_ids:
            row = self.conn.execute(
                "SELECT display_label, open_target, content_hash FROM items "
                "WHERE item_id = ?", (item_id,)).fetchone()
            if row is None:
                continue
            out.append(ev.Citation(name=row["display_label"],
                                   folder=_folder_of(row["open_target"]),
                                   open_target=row["open_target"],
                                   matched_by=_matched_by(
                                       self.conn, row["content_hash"])))
        return tuple(out)


# -- what really moved ---------------------------------------------------------

CREATED_DDL = """
CREATE TABLE IF NOT EXISTS assistant_created_folders (
    plan_id TEXT NOT NULL,
    folder TEXT NOT NULL,
    PRIMARY KEY (plan_id, folder)
);
"""


def _journal_mark(conn: sqlite3.Connection) -> int:
    try:
        return conn.execute("SELECT COALESCE(MAX(rowid), 0) "
                            "FROM move_journal").fetchone()[0]
    except sqlite3.Error:
        return 0


def _before_moving(conn: sqlite3.Connection, proposal: dict) -> dict:
    """What to compare against after a move: the folders a sort will create,
    and where the sorter's journal ends."""
    created: list[Path] = []
    if proposal.get("kind") == "plan":
        for move in proposal.get("moves") or ():
            folder = Path(move["to"]).parent
            while not folder.exists() and folder not in created and (
                    folder != folder.parent):
                created.append(folder)
                folder = folder.parent
    return {"created": created, "journal": _journal_mark(conn)}


def _plural(n: int, word: str) -> str:
    return f"{n} {word}" + ("" if n == 1 else "s")


def _as_moved(conn: sqlite3.Connection, proposal: dict, before: dict,
              result: dict) -> dict:
    """The result's words rebuilt from the disk and the journals: a count of
    files that really moved, or "Nothing moved" with the reason."""
    kind, ref = proposal["kind"], str(proposal["ref"])
    is_plan = kind == "plan" or ref.startswith("plan:")
    undoing = kind == "undo"
    if is_plan:
        plan_id = ref.partition(":")[2] if undoing else ref
        try:
            rows = conn.execute("SELECT src, dst FROM assistant_plan_ops "
                                "WHERE plan_id = ?", (plan_id,)).fetchall()
        except sqlite3.Error:
            rows = []
        here, gone = (0, 1) if undoing else (1, 0)
        n = sum(1 for r in rows
                if Path(r[here]).exists() and not Path(r[gone]).exists())
        where = ", ".join(sorted({Path(r[1]).parent.name for r in rows}))
    else:
        where = ref.rpartition("|")[2]
        try:
            rows = conn.execute(
                "SELECT destination_path FROM move_journal WHERE rowid > ?",
                (before["journal"],)).fetchall()
        except sqlite3.Error:
            rows = []
        n = sum(1 for r in rows if Path(r[0]).exists())
    if n == 0:
        why = ("the files weren't where I left them, so nothing was put "
               "back" if undoing else
               "the files weren't where I expected, so I left everything "
               "as it was" if is_plan else
               f"the plan had no files ready to move into {where}")
        return {"ok": True, "moved": False, "undo_token": None,
                "text": f"Nothing moved — {why}."}
    them = "it" if n == 1 else "them"
    if undoing:
        # Said as what is now true, so it never reads as the question again.
        text = (f"{_plural(n, 'file')} "
                f"{'is' if n == 1 else 'are'} back where "
                f"{'it was' if n == 1 else 'they were'}." if is_plan else
                f"{_plural(n, 'file')} from {where} "
                f"{'is' if n == 1 else 'are'} back.")
    else:
        text = (f"Moved {_plural(n, 'file')} into {where}. Say undo to put "
                f"{them} back.")
    if is_plan:
        _created_folders(conn, plan_id, before["created"], undoing)
    return {**result, "moved": True, "text": text}


def _created_folders(conn: sqlite3.Connection, plan_id: str,
                     created: list[Path], undoing: bool) -> None:
    """Remember the folders a sort created; after its undo, remove each one
    that is empty. A folder that existed before, or holds anything, stays."""
    conn.execute(CREATED_DDL)
    if not undoing:
        conn.executemany(
            "INSERT OR IGNORE INTO assistant_created_folders VALUES (?, ?)",
            [(plan_id, str(f)) for f in created if f.is_dir()])
        conn.commit()
        return
    folders = [Path(r[0]) for r in conn.execute(
        "SELECT folder FROM assistant_created_folders WHERE plan_id = ?",
        (plan_id,))]
    for folder in sorted(folders, key=lambda f: len(f.parts), reverse=True):
        try:
            folder.rmdir()  # only ever succeeds on an empty folder
        except OSError:
            pass
    conn.execute("DELETE FROM assistant_created_folders WHERE plan_id = ?",
                 (plan_id,))
    conn.commit()


def _forgets_conversations(proposal: dict) -> bool:
    return (proposal.get("kind") == "rule"
            and str(proposal.get("ref", "")).startswith("forget-conversations"))


def _nothing(proposal: dict) -> str:
    return ("Nothing moved." if proposal.get("kind") in ("plan", "undo",
                                                         "branch")
            else "Nothing changed.")


def open_in_finder(path: str, *, reveal: bool) -> bool:
    """Open a file, or show it in Finder, through macOS itself (no child
    process). False when this Mac's workspace API is not available."""
    try:
        from AppKit import NSWorkspace
        from Foundation import NSURL
    except ImportError:
        return False
    url = NSURL.fileURLWithPath_(path)
    workspace = NSWorkspace.sharedWorkspace()
    if reveal:
        workspace.activateFileViewerSelectingURLs_([url])
        return True
    return bool(workspace.openURL_(url))


def _hash_of(conn: sqlite3.Connection, item_id: str) -> str | None:
    row = conn.execute("SELECT content_hash FROM items WHERE item_id = ?",
                       (item_id,)).fetchone()
    return row[0] if row is not None else None


def _matched_by(conn: sqlite3.Connection, content_hash: str | None) -> str:
    """"name" while a file's text has not been read yet, else ""."""
    try:
        from items.hot_index import _text_was_read
        return "" if _text_was_read(conn, content_hash) else "name"
    except Exception:
        return ""


# -- reading document text in the background ---------------------------------

#: One reader per database at a time, across every Session in this process.
_READERS: dict[str, threading.Lock] = {}
_READERS_GUARD = threading.Lock()


def _reader_lock(path: str):
    with _READERS_GUARD:
        return _READERS.setdefault(path, threading.Lock())


def start_reading(conn: sqlite3.Connection, emit):
    """Read the text of the files indexed by name, once, on a background
    thread with its own connection. Returns the thread, or None when there
    is nothing to start (no reader in this build, or one already running on
    this database). Each file has the extraction pool's own time ceiling, so
    one file cannot stall the rest; a file it gives up on stays found by
    name and is counted in what is said at the end."""
    try:
        from items.indexing import read_document_text  # noqa: F401
    except ImportError:
        return None
    from assistant.engine_tools import database_path
    path = database_path(conn)
    if not path:
        return None
    lock = _reader_lock(path)
    if not lock.acquire(blocking=False):
        return None
    thread = threading.Thread(target=_read_all, args=(path, emit, lock),
                              name="read-document-text", daemon=True)
    thread.start()
    return thread


def _read_all(path: str, emit, lock) -> None:
    from database_agent.db import open_database
    from items import indexing
    own = None
    try:
        # `open_database` takes DATABASE_AGENT_KEY_FILE itself, as the
        # Session's own connection did.
        own = open_database(Path(path), scan_roots=[])

        def progress(stage: str, done: int, total: int) -> None:
            if total:
                emit(ev.Progress(stage="read", done=done, total=total,
                                 line=f"Reading document text… "
                                      f"{total - done} left"))
        read = indexing.read_document_text(own, on_progress=progress,
                                           limit=None)
        left = getattr(read, "unreadable", 0)
        # Named on the person's own screen only: this line is never part of
        # the conversation record or a model request.
        rows = (own.execute("SELECT display_label FROM items "
                            "WHERE item_id = ?", (i,)).fetchone()
                for i in getattr(read, "protected_items", ()))
        names = [r[0] for r in rows if r is not None]
        found = len(names)
        text = (f"Finished reading document text ({read} "
                f"file{'s' if read != 1 else ''}).")
        if found:
            text += (f" {found} more file{'s' if found != 1 else ''} "
                     f"look{'' if found != 1 else 's'} personal now that "
                     "I've read them, so I protected "
                     f"{'them' if found != 1 else 'it'}: "
                     f"{', '.join(names)}.")
        if left:
            text += (f" {left} file{'s' if left != 1 else ''} couldn't be "
                     "read and "
                     f"{'are' if left != 1 else 'is'} found by name only.")
        emit(ev.Message(text=text))
    except Exception:
        emit(ev.Message(text="I stopped reading document text. Files not "
                             "read yet are still found by their names."))
    finally:
        if own is not None:
            own.close()
        lock.release()


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
    if lower == "show protected":
        from types import SimpleNamespace
        from assistant.engine_tools import show_protected
        shown: list = []
        show_protected(conn, SimpleNamespace(show_locally=shown.append))
        return shown
    if lower == "show skipped":
        return [_excluded_list(conn, protected=False)]
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
        citations.append(ev.Citation(
            name=hit.display_label, folder=_folder_of(target),
            open_target=target,
            matched_by="" if getattr(hit, "matched_by", "") == "content"
            else _matched_by(conn, getattr(hit, "content_hash", None)
                             or _hash_of(conn, hit.item_id))))
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
                     if not _CITATIONS_LINE.match(line)).strip()


_CITATIONS_LINE = re.compile(
    r"^\W*(citations?|cite[sd]?|sources?|refs?|references?)\b\W*(:|$)",
    re.IGNORECASE)
#: A piece of an internal id ("-56b1-4793-9f82-"): hex groups joined by
#: dashes. Kept only when it is part of one of the person's file names.
#: At least one letter a-f, so a year range such as 2024-2025 stays.
_ID_FRAGMENT = re.compile(r"-?\b(?=[0-9a-f-]*[a-f])[0-9a-f]{4,}"
                          r"(?:-[0-9a-f]{4,})+\b-?",
                          re.IGNORECASE)


def strip_id_fragments(conn: sqlite3.Connection, text: str) -> str:
    """The text without id pieces; a line left with nothing but a label
    ("Cite:") goes with them."""
    def keep(m: re.Match) -> str:
        token = m.group(0).strip("-")
        try:
            named = conn.execute(
                "SELECT 1 FROM items WHERE instr(lower(display_label), ?) "
                "LIMIT 1", (token.lower(),)).fetchone()
        except sqlite3.Error:
            named = None
        return m.group(0) if named else ""
    out = []
    for line in text.splitlines():
        cleaned = _ID_FRAGMENT.sub(keep, line)
        if cleaned != line and not re.search(
                r"\w{2,}", re.sub(r"^\W*\w+\s*:", "", cleaned)):
            continue
        out.append(cleaned.rstrip())
    return "\n".join(out).strip()

#: Sentences no person should read: database files, command-line flags,
#: model ids, sums the model worked out loud, internal snake_case codes.
_DEVELOPER = (
    re.compile(r"\S*\.sqlite\w*\b"),
    re.compile(r"(?<![\w-])--[a-z][\w-]*"),
    re.compile(r"\bno citations?\b|\bcitations? (needed|line)\b"
               r"|\bnothing to cite\b", re.IGNORECASE),
    re.compile(r"\b(deepseek-(chat|reasoner|v[\w.]+)|gpt-[\w.-]+|"
               r"claude-[\w.-]+|o[134]-mini)\b", re.IGNORECASE),
    re.compile(r"\bitem[ _-]?ids?\b|\btool (calls?|names?|results?)\b"
               r"|\b(this|the|a) (lookup|payload|schema)\b"
               r"|\bpayloads?\b|\bschemas?\b", re.IGNORECASE),
    # Two or more of + × * = between numbers; never - or /, so dates stay.
    re.compile(r"\b\d[\d,.]*(?:\s*[+×*=]\s*\d[\d,.]*){2,}"),
)
def scrub_developer_text(text: str) -> str:
    """The text without any sentence carrying developer text. (Internal
    codes inside a sentence are replaced by `plain_reply`.)"""
    def developer(sentence: str) -> bool:
        return any(p.search(sentence) for p in _DEVELOPER)
    out = []
    for line in text.splitlines():
        parts = re.split(r"(?<=[.!?])\s+", line)
        kept = [p for p in parts if not developer(p)]
        if line.strip() and not kept:
            continue
        out.append(" ".join(kept))
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()


PLAIN_WORDS = (
    "Speak in plain words a student or a job-seeker uses. Never say internal "
    "state names or codes: not unplaced, typed, held, schema ids, situation "
    "codes, branch ids or item ids. Say \"not sorted yet\", not "
    "\"unplaced\"; say \"protected\", not \"held\"; name a folder the way "
    "the plan shows it.\n"
    "\"Put / move my screenshots (or installers, copies) into a folder\" is "
    "a one-off: call quick_sort with kind, which takes every loose one. "
    "Only \"always / whenever / from now on …\" is a standing rule: call "
    "remember_rule. Never both for one request.\n"
    "Keep replies to a few short sentences. Never mention file paths of "
    "databases, model names, command-line flags or internal codes, and "
    "don't show arithmetic.")

#: State words a person should never read, and what to say instead. "typed"
#: is ordinary English after you/I, so only the state use is replaced.
_STATE_WORDS = (
    (re.compile(r"\bunplaced\b"), "not sorted yet"),
    (re.compile(r"\bUnplaced\b"), "Not sorted yet"),
    (re.compile(r"\b(?:held|typing_state)\b(?! (?:off|on|up|back)\b)"),
     "protected"),
    (re.compile(r"\bHeld\b(?! (?:off|on|up|back)\b)"), "Protected"),
    (re.compile(r"(?<!\byou )(?<!\bI )(?<!\bwe )\buntyped\b"),
     "not recognised yet"),
    (re.compile(r"(?<!\byou )(?<!\bI )(?<!\bwe )(?<!\bYou )\btyped\b"),
     "recognised"),
)


def plain_reply(conn: sqlite3.Connection, text: str) -> str:
    """The model's reply with internal words replaced, whatever it emitted.

    Codes (`wording_problems`) are dropped unless they are part of a file
    name in the reply or of a name this database holds -- a person's file
    called `my_cv.pdf` keeps its name."""
    from assistant.engine_tools import wording_problems
    for pattern, words in _STATE_WORDS:
        text = pattern.sub(words, text)
    dropped = False
    for token in wording_problems(text):
        if re.search(re.escape(token) + r"[\w-]*\.[A-Za-z0-9]{1,5}\b", text):
            continue
        try:
            named = conn.execute(
                "SELECT 1 FROM items WHERE instr(lower(display_label), ?) "
                "LIMIT 1", (token,)).fetchone()
        except sqlite3.Error:
            named = None
        if named is None:
            text = text.replace(token, "")
            dropped = True
    # "inside ****" lost its name: the word goes with it, and only there.
    text, inside = re.subn(r"\s*\binside\s+(\*\*\s*\*\*|__\s*__)(\s*,)?", "",
                           text)
    text, emptied = _EMPTY_EMPHASIS.subn("", text)
    emptied += inside
    if not dropped and not emptied:
        return text.strip()
    return re.sub(r"(?<=\S)[ \t]{2,}", " ",
                  re.sub(r"[ \t]+([?.,!:;])", r"\1", text)).strip()


#: Bold or italics around nothing ("****", "** **", "__"): the model's name
#: for something it was not told.
_EMPTY_EMPHASIS = re.compile(r"(\*\*|__)\s*\1|(?<![*\w])\*\s*\*(?![*\w])")
