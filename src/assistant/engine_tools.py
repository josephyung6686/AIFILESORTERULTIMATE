"""The conversation's own tools, each a thin wrapper over an existing seam.

A tool that would move a file, change protection or change a setting returns
`{"ok": True, "needs_confirmation": {kind, ref, summary, moves, sensitive}}`
and changes nothing. The Session turns that into a `Confirm` (or, when the
person's permission level allows, runs it) and only then calls
`execute_confirmed`. Every sentence here is written for the person: no ids,
hashes or internal codes.
"""
from __future__ import annotations

import hashlib
import os
from dataclasses import fields
import re
import sqlite3
from pathlib import Path
from typing import Any

from items.file_identity import item_is_sensitive

LEVELS = (1, 2, 3)
SMALL_SORT = 20

SETTINGS_DDL = """
CREATE TABLE IF NOT EXISTS session_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


# -- settings ---------------------------------------------------------------

def get_setting(conn: sqlite3.Connection, key: str, default: str) -> str:
    conn.executescript(SETTINGS_DDL)
    row = conn.execute("SELECT value FROM session_settings WHERE key = ?",
                       (key,)).fetchone()
    return row[0] if row is not None else default


def put_setting(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.executescript(SETTINGS_DDL)
    conn.execute("INSERT INTO session_settings (key, value) VALUES (?, ?) "
                 "ON CONFLICT (key) DO UPDATE SET value = excluded.value",
                 (key, value))
    conn.commit()


def get_level(conn: sqlite3.Connection) -> int:
    try:
        level = int(get_setting(conn, "permission_level", "1"))
    except ValueError:
        return 1
    return level if level in LEVELS else 1


def level_allows(level: int, kind: str, n_moves: int, sensitive: bool) -> bool:
    """Whether a proposal runs without asking. Only small ordinary sorts the
    person asked for ever do; branch applies, undo of a branch, protection,
    rules and settings always ask."""
    if kind != "plan" or sensitive:
        return False
    if level == 2:
        return n_moves <= SMALL_SORT
    return level == 3


# -- helpers ----------------------------------------------------------------

def _sha256(path: Path) -> str | None:
    if path.is_symlink() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _proposal(kind: str, ref: str, summary: str, moves=(), *,
              sensitive: bool = False) -> dict[str, Any]:
    return {"ok": True, "needs_confirmation": {
        "kind": kind, "ref": ref, "summary": summary,
        "moves": [{"from": a, "to": b} for a, b in moves],
        "sensitive": bool(sensitive)}}


def _plural(n: int, word: str) -> str:
    return f"{n} {word}" + ("" if n == 1 else "s")


_TYPE_FOLDERS = (
    ({".png", ".jpg", ".jpeg", ".heic", ".gif", ".webp", ".tiff"}, "Images"),
    ({".pdf"}, "PDFs"),
    ({".doc", ".docx", ".txt", ".md", ".rtf", ".pages", ".odt"}, "Documents"),
    ({".xls", ".xlsx", ".csv", ".numbers"}, "Spreadsheets"),
    ({".ppt", ".pptx", ".key"}, "Presentations"),
    ({".zip", ".tar", ".gz", ".rar", ".7z"}, "Archives"),
    ({".dmg", ".pkg"}, "Installers"),
    ({".mp3", ".wav", ".m4a", ".aac", ".flac"}, "Audio"),
    ({".mp4", ".mov", ".avi", ".mkv"}, "Video"),
)


def _type_folder(names: list[str]) -> str:
    if names and all(n.lower().startswith(("screenshot", "screen shot"))
                     for n in names):
        return "Screenshots"
    labels = set()
    for name in names:
        ext = Path(name).suffix.lower()
        labels.add(next((label for exts, label in _TYPE_FOLDERS
                         if ext in exts), "Other"))
    return labels.pop() if len(labels) == 1 else "Sorted"


def _resolve(conn: sqlite3.Connection, name: str):
    """The live item the person named: an exact file name first, then the
    best search hit whose name contains what they typed."""
    rows = conn.execute(
        "SELECT item_id, display_label, open_target, file_id FROM items "
        "WHERE presence = 'live' AND superseded_by IS NULL "
        "AND lower(display_label) = lower(?) AND open_target IS NOT NULL",
        (name,)).fetchall()
    if rows:
        return rows[0]
    from items.hot_index import find_files
    for hit in find_files(conn, name, limit=5).hits:
        if name.lower() in (hit.display_label or "").lower():
            return conn.execute(
                "SELECT item_id, display_label, open_target, file_id "
                "FROM items WHERE item_id = ?", (hit.item_id,)).fetchone()
    return None


# -- tools ------------------------------------------------------------------

def quick_sort(conn: sqlite3.Connection, files: list[str],
               destination: str | None = None) -> dict[str, Any]:
    from assistant.plans import PlanOp, create_draft_plan
    found, missing, protected = [], [], []
    for name in files:
        row = _resolve(conn, str(name))
        if row is None:
            missing.append(str(name))
        elif item_is_sensitive(conn, row["item_id"]):
            protected.append(row["display_label"])
        elif row not in found:
            found.append(row)
    if not found:
        text = "I couldn't find " + ", ".join(missing) if missing else ""
        if protected:
            text = (text + ". " if text else "") + (
                ", ".join(protected) + " is protected and stays where it is")
        return {"ok": False, "error": text or "No files named.",
                "not_found": missing}
    paths = [Path(r["open_target"]) for r in found]
    parent = Path(os.path.commonpath([str(p.parent) for p in paths]))
    folder = destination or _type_folder([r["display_label"] for r in found])
    target = parent / folder
    in_tree, not_placed = ({}, []) if destination else _tree_places(
        conn, found, parent)
    pairs = [(row, src, in_tree.get(row["item_id"], target) / src.name)
             for row, src in zip(found, paths)]
    pairs = [p for p in pairs if p[1].parent != p[2].parent]
    scope = os.path.commonpath([str(parent)] + [str(d.parent)
                                                for _, _, d in pairs])
    ops, moves = [], []
    for row, src, dst in pairs:
        ops.append(PlanOp(item_id=row["item_id"], src=str(src), dst=str(dst),
                          file_id=row["file_id"], content_hash=_sha256(src),
                          root_scope=scope))
        moves.append((str(src), str(dst)))
    if not ops:
        return {"ok": False, "error": f"Those files are already in {folder}."}
    plan = create_draft_plan(conn, ops=ops)
    conn.commit()
    folders = sorted({_home_words(Path(b).parent) if Path(b).parent != target
                      else folder for _, b in moves})
    summary = (f"Move {_plural(len(ops), 'file')} into "
               + (folders[0] if len(folders) == 1 else "the folders below"))
    if not_placed:
        summary += ". " + "; ".join(not_placed)
    if protected:
        summary += (". " + ", ".join(protected)
                    + " is protected and stays where it is")
    if missing:
        summary += ". I couldn't find " + ", ".join(missing)
    return {**_proposal("plan", plan.plan_id, summary + ".", moves,
                        sensitive=bool(protected)),
            "not_found": missing}


def _selection_root(conn: sqlite3.Connection, folder: Path) -> Path | None:
    """The deepest recorded selection source containing `folder`."""
    import json
    try:
        rows = conn.execute("SELECT sources FROM corpus_selections").fetchall()
    except sqlite3.Error:
        return None
    best = None
    for row in rows:
        for source in json.loads(row[0] or "[]"):
            s = Path(source)
            if (s == folder or s in folder.parents) and (
                    best is None or len(s.parts) > len(best.parts)):
                best = s
    return best


def _tree_places(conn: sqlite3.Connection, found: list,
                 parent: Path) -> tuple[dict[str, Path], list[str]]:
    """Where the sorter's tree puts each file, as folders beside them, and a
    plain line for each file it has not placed (its `why`, never the bare
    abstention code)."""
    try:
        from assistant.organize_tools import propose_tree
        result = propose_tree(conn, [r["item_id"] for r in found])
    except Exception:
        return {}, []
    if result.get("source") != "sorter_tree":
        return {}, []
    # The tree's paths are relative to the folder the sorter organised: the
    # recorded selection that holds these files.
    root = _selection_root(conn, parent)
    if root is None:
        return {}, []
    places, notes = {}, []
    for entry in result.get("files") or []:
        dest = entry.get("destination")
        if dest:
            places[entry["item_id"]] = root / dest
        elif entry.get("display_label"):
            why = entry.get("question") or entry.get("why") or (
                "the sorter has not placed it yet")
            notes.append(f"{entry['display_label']} goes by type: {why}")
    return places, notes


def undo_proposal(conn: sqlite3.Connection, token: str) -> dict[str, Any]:
    """The confirmation for putting one batch back."""
    kind, _, ref = token.partition(":")
    if kind == "branch":
        branch = ref.partition("|")[2]
        return _proposal("undo", token, f"Put the files from {branch} back "
                                        "where they were?")
    if kind != "plan":
        return {"ok": False, "error": "I can't find that batch of moves."}
    rows = conn.execute(
        "SELECT src, dst FROM assistant_plan_ops WHERE plan_id = ?",
        (ref,)).fetchall()
    if not rows:
        return {"ok": False, "error": "I can't find that batch of moves."}
    return _proposal("undo", token,
                     f"Put {_plural(len(rows), 'file')} back where "
                     f"{'it was' if len(rows) == 1 else 'they were'}.",
                     [(r["dst"], r["src"]) for r in rows])


def recent_batches(conn: sqlite3.Connection, limit: int = 5) -> list[dict]:
    """The last moved batches that can still be put back, in plain words:
    `{token, text}` each."""
    from assistant.plans import ensure_plans_schema
    ensure_plans_schema(conn)
    out = []
    for row in conn.execute(
            "SELECT plan_id, created_ts FROM assistant_plans "
            "WHERE state = 'applied' ORDER BY created_ts DESC LIMIT ?",
            (limit,)).fetchall():
        dsts = [Path(r[0]) for r in conn.execute(
            "SELECT dst FROM assistant_plan_ops WHERE plan_id = ?",
            (row["plan_id"],))]
        folders = sorted({d.parent.name for d in dsts})
        when = row["created_ts"][:16].replace("T", " ")
        out.append({"token": f"plan:{row['plan_id']}",
                    "text": f"{_plural(len(dsts), 'file')} into "
                            f"{', '.join(folders)} ({when} UTC)"})
    return out


def undo_last(conn: sqlite3.Connection) -> dict[str, Any]:
    from assistant.plans import ensure_plans_schema
    ensure_plans_schema(conn)
    row = conn.execute(
        "SELECT plan_id FROM assistant_plans WHERE state = 'applied' "
        "ORDER BY created_ts DESC LIMIT 1").fetchone()
    if row is None:
        return {"ok": False, "error": "There's nothing I moved to put back."}
    return undo_proposal(conn, f"plan:{row['plan_id']}")


# -- questions --------------------------------------------------------------

_CODE_PATTERNS = (
    # academic.coursework -- but not a file name such as notes.txt
    re.compile(r"(?<![\w.])[a-z]+\.[a-z][a-z_-]{4,}\b"),
    re.compile(r"\b[a-z0-9]+_[a-z0-9_]+\b"),        # snake_case ids
    # hex ids: letters and digits both, so a date or a number is left alone
    re.compile(r"\b(?=[0-9a-f]*[a-f])(?=[0-9a-f]*[0-9])[0-9a-f]{8,}\b"),
)


def wording_problems(text: str) -> list[str]:
    """Internal codes a person should never read: schema ids, situation
    codes, snake_case names, long hex ids."""
    found: list[str] = []
    for pattern in _CODE_PATTERNS:
        for token in pattern.findall(text or ""):
            if token not in found:
                found.append(token)
    return found


def _plain(text: str, options) -> str:
    """The text with any code replaced by the label of the option it names,
    or dropped when no option does."""
    for token in wording_problems(text):
        label = next((o.label for o in options
                      if token in {getattr(o, f.name) for f in fields(o)
                                   if f.name != "label"}), None)
        text = text.replace(token, label) if label else text.replace(token, "")
    return re.sub(r"\s{2,}", " ", re.sub(r"\s+([?.,!])", r"\1", text)).strip()


def question_event(q, index: int, of: int):
    from assistant.events import Option, Question
    return Question(
        question_id=q.question_id,
        text=_plain(q.prompt, q.options),
        why=_plain(q.evidence_context, q.options),
        changes=_plain(q.unlocks, q.options),
        options=tuple(Option(id=o.option_id, label=_plain(o.label, q.options))
                      for o in q.options),
        allow_text=True, allow_skip=True, index=index, of=of)


def open_questions(conn: sqlite3.Connection) -> tuple:
    try:
        from questions.store import open_questions as store_open
        return store_open(conn)
    except sqlite3.Error:
        return ()


SKIP_WORDS = {"skip", "s", "skip it", "not now", "later"}


def record_person_answer(conn: sqlite3.Connection, question_id: str,
                         value: str) -> str:
    """Store what the person said: an option (by id or its label), a skip,
    or their own words as free text that selects nothing. Returns the kind
    recorded: "choice", "skipped" or "free_text"."""
    import getpass
    from datetime import datetime, timezone
    from questions.records import StructuralAnswer
    from questions.store import _question_of, live_answer_id, record_answer
    from questions.vocabulary import CONFIRMED, FREE_TEXT

    row = conn.execute("SELECT * FROM structural_questions "
                       "WHERE question_id = ?", (question_id,)).fetchone()
    if row is None:
        raise LookupError("no such question")
    q = _question_of(row)
    typed = (value or "").strip()
    user = getpass.getuser()
    now = datetime.now(timezone.utc).isoformat()
    option = next((o.option_id for o in q.options
                   if typed == o.option_id
                   or typed.casefold() == o.label.casefold()), None)
    if option is not None or typed.casefold() in SKIP_WORDS:
        # The sorter's own `--answer` path, so the answer is also remembered
        # as an event exactly as the sorter remembers it.
        from cli import apply_answers
        apply_answers(conn, [f"{question_id}={option or 'skip'}"],
                      user_id=user, recorded_at=now)
        conn.commit()
        return "choice" if option else "skipped"
    previous = live_answer_id(conn, question_id=question_id, scope=q.scope)
    record_answer(conn, StructuralAnswer(
        question_id=question_id, option_id=None, state=CONFIRMED,
        scope=q.scope, user_id=user, recorded_at=now,
        answer_type=FREE_TEXT, raw_wording=typed, supersedes=previous,
        supersede_reason=("the user answered this again"
                          if previous else None)))
    conn.commit()
    return "free_text"


def next_questions(conn: sqlite3.Connection, context: Any) -> dict[str, Any]:
    qs = open_questions(conn)
    if context is not None and qs:
        context.ask_questions_after_turn = True
    return {"ok": True, "open_questions": len(qs),
            "note": ("The questions are shown to the person one at a time "
                     "by the app, with their options. Do not repeat or "
                     "answer them yourself.") if qs else
                    "There are no open questions."}


# -- folders and the sorter -------------------------------------------------

def _home_words(path: Path) -> str:
    try:
        return "~/" + str(path.relative_to(Path.home()))
    except ValueError:
        return str(path)


def database_path(conn: sqlite3.Connection) -> str:
    for row in conn.execute("PRAGMA database_list").fetchall():
        if row[1] == "main":
            return row[2]
    return ""


def _chosen_by_person(conn: sqlite3.Connection, folder: Path,
                      context: Any) -> bool:
    """A folder the person picked: in this conversation, or recorded as
    their selection by an earlier run."""
    if context is not None and folder in getattr(context, "chosen_folders",
                                                 set()):
        return True
    try:
        rows = conn.execute(
            "SELECT sources FROM corpus_selections "
            "WHERE selected_by IS NOT NULL").fetchall()
    except sqlite3.Error:
        return False
    import json
    return any(str(folder) in json.loads(r[0] or "[]") for r in rows)


def check_folder(conn: sqlite3.Connection, folder: str, context: Any,
                 action: str) -> tuple[Path | None, dict | None]:
    """(path, None) when the folder may be read now; otherwise (None, payload)
    refusing it or asking the person first."""
    from items.file_identity import path_is_protected
    path = Path(folder).expanduser()
    try:
        path = path.resolve()
    except OSError:
        return None, {"ok": False, "error": "I can't find that folder."}
    if path_is_protected(str(path)) or any(
            path_is_protected(str(p)) for p in path.parents):
        return None, {"ok": False, "error": "That folder is protected. I never "
                                            "open it."}
    if not path.is_dir():
        return None, {"ok": False, "error": "I can't find that folder."}
    if not _chosen_by_person(conn, path, context):
        return None, _proposal(
            "folder", f"{action}:{path}",
            f"Read {_home_words(path)} to build the private index? "
            "Nothing moves.")
    return path, None


class Cancelled(Exception):
    """The person said cancel while the sorter was running."""


class _ProgressStream:
    def __init__(self, context: Any) -> None:
        self.context = context
        self.lines: list[str] = []

    def write(self, text: str) -> int:
        if getattr(self.context, "cancel_requested", False):
            raise Cancelled()
        from assistant.events import Progress
        for line in str(text).splitlines():
            if line.strip():
                self.lines.append(line.strip())
                emit = getattr(self.context, "emit", None)
                if emit is not None:
                    emit(Progress(stage="organise", line=line.strip()))
        return len(text)

    def flush(self) -> None:
        pass


def organise_folder(conn: sqlite3.Connection, folder: str,
                    context: Any) -> dict[str, Any]:
    path, refusal = check_folder(conn, folder, context, "organise")
    if refusal is not None:
        return refusal
    return run_organise(conn, path, context)


def run_organise(conn: sqlite3.Connection, path: Path,
                 context: Any) -> dict[str, Any]:
    import cli
    conn.commit()
    stream = _ProgressStream(context)
    emit = getattr(context, "emit", None)
    if context is not None:
        context.cancel_requested = False
    if emit is not None:
        from assistant.events import Message
        emit(Message(text="Organising reads every file, so this can take "
                          "several minutes. Type cancel (or press Ctrl-C) "
                          "to stop — nothing moves either way."))
    try:
        cli.main([str(path), "--database", database_path(conn),
                  "--stop-after", "tree"], out=stream)
    except (Cancelled, KeyboardInterrupt):
        if emit is not None:
            from assistant.events import Message
            emit(Message(text="Stopped. Nothing moved."))
        return {"ok": False, "cancelled": True,
                "error": "The person stopped organising. Nothing moved."}
    except SystemExit:
        pass
    except Exception:
        return {"ok": False, "error": "Organising stopped with a problem. "
                                      "Nothing moved."}
    n = len(open_questions(conn))
    if n and context is not None:
        context.ask_questions_after_turn = True
    try:
        from assistant.organize_tools import show_tree
        tree = show_tree(conn)
    except Exception:
        tree = None
    text = ("I've looked through the folder. Nothing moved. "
            + (f"I have {_plural(n, 'question')} first." if n else ""))
    return {"ok": True, "open_questions": n, "tree": tree,
            "moved": False, "text": text.strip(),
            "last_lines": stream.lines[-12:]}


def counts_sentence(c) -> str:
    """The totals in the person's words, one protection word."""
    parts = [f"I've indexed {_plural(c.indexed, 'file')}."]
    if c.set_aside:
        folders = getattr(c, "set_aside_folders", 0) or 1
        parts.append(
            f"{_plural(c.set_aside, 'file')} "
            f"{'are' if c.set_aside != 1 else 'is'} inside "
            f"{folders} coding project{'s' if folders != 1 else ''} — each "
            "is kept as one item and nothing inside is moved.")
    protected = c.protected + c.held
    if protected:
        parts.append(f"{_plural(protected, 'file')} "
                     f"{'look' if protected != 1 else 'looks'} personal "
                     "(ID, health) and "
                     f"{'are' if protected != 1 else 'is'} protected — I'll "
                     "show them only to you.")
    return " ".join(parts)


def set_level(conn: sqlite3.Connection, level: int) -> dict[str, Any]:
    if level not in LEVELS:
        return {"ok": False, "error": "The levels are 1, 2 and 3."}
    words = {1: "ask before every move",
             2: "move up to 20 ordinary files without asking",
             3: "move ordinary files without asking"}[level]
    return _proposal("settings", f"level:{level}",
                     f"Change to level {level}: {words}? Protected files and "
                     "whole-folder changes always ask.")


def what_was_sent(conn: sqlite3.Connection) -> dict[str, Any]:
    """Today's requests to the AI model, in plain words. No ids."""
    from datetime import datetime, timezone
    from assistant.egress import ensure_egress_schema
    ensure_egress_schema(conn)
    today = datetime.now(timezone.utc).date().isoformat()
    rows = conn.execute(
        "SELECT provider, bytes, question FROM egress_ledger "
        "WHERE ts >= ? ORDER BY ts", (today,)).fetchall()
    names = {"deepseek": "DeepSeek", "openai": "OpenAI",
             "anthropic": "Anthropic"}
    providers = sorted({names.get(r[0], r[0]) for r in rows})
    total = sum(int(r[1]) for r in rows)
    return {"ok": True, "today": {
        "requests": len(rows), "bytes": total,
        "sent_to": providers or ["nobody"],
        "your_questions": [r[2] for r in rows if r[2]][-10:],
        "never_sent": "protected files' names, folders and text"}}


def run_index(conn: sqlite3.Connection, path: Path,
              context: Any) -> dict[str, Any]:
    from assistant.events import Progress
    emit = getattr(context, "emit", None)

    def progress(stage: str, done: int, total: int) -> None:
        if emit is not None:
            emit(Progress(stage=stage, done=done, total=total,
                          line=("Indexed." if stage == "done" else
                                f"Indexing {done} of {total}" if total else
                                f"Indexing… {done} files so far")))
    try:
        from items.indexing import index_folder as index
        c = index(conn, path, on_progress=progress)
        conn.commit()
    except Exception:
        return {"ok": False, "error": "I couldn't index that folder. "
                                      "Nothing changed."}
    if context is not None:
        context.after_index(c)
    return {"ok": True, "indexed": c.indexed, "set_aside": c.set_aside,
            "protected": c.protected + c.held, "moved": False,
            "text": counts_sentence(c)}


def index_folder(conn: sqlite3.Connection, folder: str,
                 context: Any) -> dict[str, Any]:
    path, refusal = check_folder(conn, folder, context, "index")
    if refusal is not None:
        return refusal
    return run_index(conn, path, context)


def apply_branch(conn: sqlite3.Connection, branch: str, folder: str,
                 context: Any) -> dict[str, Any]:
    """Propose moving the files the sorter froze for one branch. Always
    asks, at every level."""
    path, refusal = check_folder(conn, folder, context, "organise")
    if refusal is not None:
        return refusal
    branch = (branch or "").strip()
    if not branch or branch.startswith("-"):
        return {"ok": False, "error": "Which folder of the plan should I "
                                      "move?"}
    try:
        from assistant.organize_tools import show_tree
        frozen = int(show_tree(conn).get("frozen_moves") or 0)
    except Exception:
        frozen = 0
    if not frozen:
        return {"ok": False, "error": "There is no approved plan to move "
                                      "yet. Organise the folder first."}
    return _proposal("branch", f"{path}|{branch}",
                     f"Move the files planned for {branch} in "
                     f"{_home_words(path)}? Every move can be undone.")


def _branch(conn: sqlite3.Connection, ref: str, undo: bool) -> dict[str, Any]:
    import cli
    folder, _, branch = ref.partition("|")
    conn.commit()
    stream = _ProgressStream(None)
    try:
        code = cli.main([folder, "--database", database_path(conn),
                         "--undo" if undo else "--apply", branch], out=stream)
    except SystemExit as exc:
        code = exc.code
    except Exception:
        code = 1
    if code not in (0, None):
        return {"ok": False, "moved": False, "undo_token": None,
                "text": "The sorter refused that, so nothing moved."}
    return {"ok": True, "moved": True,
            "undo_token": None if undo else f"branch:{ref}",
            "text": (f"Put the files from {branch} back." if undo else
                     f"Moved the files for {branch}. Say undo to put them "
                     "back.")}


def _named_item(conn: sqlite3.Connection, file: str):
    return conn.execute(
        "SELECT item_id, display_label, open_target, file_id FROM items "
        "WHERE presence = 'live' AND superseded_by IS NULL "
        "AND lower(display_label) = lower(?)", (file,)).fetchone()


def mark_sensitive(conn: sqlite3.Connection, file: str) -> dict[str, Any]:
    row = _named_item(conn, file)
    if row is None:
        return {"ok": False, "error": f"I couldn't find {file}."}
    if item_is_sensitive(conn, row["item_id"]):
        # Never `--file-held` here: on a file already held it would grant
        # permission to move it, which is not what the person asked.
        return {"ok": False, "error": "That file is already protected."}
    return _proposal(
        "protection", f"hold:{row['item_id']}",
        f"Protect {row['display_label']}? It will never be sent to the AI "
        "model and won't be moved automatically.")


def release(conn: sqlite3.Connection, file: str) -> dict[str, Any]:
    row = _named_item(conn, file)
    if row is None:
        return {"ok": False, "error": f"I couldn't find {file}."}
    if not item_is_sensitive(conn, row["item_id"]):
        return {"ok": False, "error": f"{row['display_label']} isn't "
                                      "protected."}
    return _proposal(
        "protection", f"release:{row['item_id']}",
        f"Treat {row['display_label']} as an ordinary file? It stops being "
        "protected: it can be sorted, and its text may be sent to the AI "
        "model from now on.", sensitive=True)


# -- rules and memory -------------------------------------------------------

def remember_rule(conn: sqlite3.Connection, text: str) -> dict[str, Any]:
    text = (text or "").strip()
    if not text:
        return {"ok": False, "error": "What should I remember?"}
    return _proposal("rule", f"add:{text}", f"Remember this rule: “{text}”?")


def list_rules(conn: sqlite3.Connection) -> dict[str, Any]:
    from assistant.memory_v1 import list_rules as rules
    return {"ok": True, "rules": [
        {"number": i, "text": r["rule_text"]}
        for i, r in enumerate(rules(conn), start=1)]}


def forget_rule(conn: sqlite3.Connection, number: int) -> dict[str, Any]:
    from assistant.memory_v1 import list_rules as rules
    current = rules(conn)
    if not 1 <= number <= len(current):
        return {"ok": False, "error": "I don't have a rule with that number."}
    rule = current[number - 1]
    return _proposal("rule", f"forget:{rule['rule_id']}",
                     f"Forget the rule “{rule['rule_text']}”?")


def forget_conversations(conn: sqlite3.Connection) -> dict[str, Any]:
    return _proposal("rule", "forget-conversations:",
                     "Forget our past conversations? Your files, answers "
                     "and rules stay.")


def _rule(conn: sqlite3.Connection, ref: str) -> dict[str, Any]:
    action, _, value = ref.partition(":")
    if action == "add":
        from assistant.memory_v1 import add_rule
        add_rule(conn, rule_text=value)
        text = "Got it — I'll remember that."
    elif action == "forget":
        conn.execute("UPDATE memory_rules SET active = 0 WHERE rule_id = ?",
                     (value,))
        text = "Forgotten."
    else:
        from assistant.conversation_store import forget
        forget(conn)
        text = "I've forgotten our past conversations."
    conn.commit()
    return {"ok": True, "moved": False, "undo_token": None, "text": text}


# -- execution after a yes --------------------------------------------------

def _label(conn: sqlite3.Connection, item_id: str, fallback: str) -> str:
    row = conn.execute("SELECT display_label FROM items WHERE item_id = ?",
                       (item_id,)).fetchone()
    return row[0] if row is not None else Path(fallback).name


def _precheck(conn: sqlite3.Connection, plan_id: str) -> str | None:
    """Every op checked before anything moves, so a refusal moves nothing."""
    from assistant.apply import _validate_op
    for r in conn.execute(
            "SELECT item_id, file_id, content_hash, src, dst, root_scope, "
            "protected_snapshot FROM assistant_plan_ops WHERE plan_id = ?",
            (plan_id,)).fetchall():
        name = _label(conn, r["item_id"], r["src"])
        err = _validate_op(
            conn, item_id=r["item_id"], src=Path(r["src"]),
            dst=Path(r["dst"]), content_hash=r["content_hash"],
            file_id=r["file_id"], root_scope=r["root_scope"],
            protected_snapshot=r["protected_snapshot"])
        if err is None and Path(r["dst"]).exists():
            err = "dest exists"
        if err is None:
            continue
        if "mismatch" in err:
            return (f"{name} has changed since I suggested this, so I didn't "
                    "move anything. Ask me again for a fresh plan.")
        if "held" in err or "protected" in err:
            return f"{name} is protected, so I didn't move anything."
        if "missing src" in err:
            return (f"{name} isn't where it was any more, so I didn't move "
                    "anything.")
        if "dest exists" in err:
            return (f"There's already a file called {Path(r['dst']).name} "
                    "there, so I didn't move anything.")
        return "I couldn't move those files, so nothing moved."
    return None


def _protection(conn: sqlite3.Connection, ref: str) -> dict[str, Any]:
    import cli
    action, _, item_id = ref.partition(":")
    row = conn.execute("SELECT display_label, open_target, file_id FROM items "
                       "WHERE item_id = ?", (item_id,)).fetchone()
    if row is None or not row["open_target"]:
        return {"ok": False, "moved": False, "undo_token": None,
                "text": "I can't find that file any more. Nothing changed."}
    import getpass
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    # The sorter's own `--file-held` / `--release` gestures, on this database.
    try:
        if action == "hold":
            cli.apply_file_held(conn, [row["file_id"]],
                                plan_version=cli.PLAN_VERSION,
                                user_id=getpass.getuser(), recorded_at=now)
        else:
            cli.apply_release(conn, [row["file_id"]],
                              user_id=getpass.getuser(), recorded_at=now)
        conn.commit()
    except Exception:
        conn.rollback()
        return {"ok": False, "moved": False, "undo_token": None,
                "text": ("I can't change protection until this folder has "
                         "been organised once. Nothing changed.")}
    if item_is_sensitive(conn, item_id) != (action == "hold"):
        return {"ok": False, "moved": False, "undo_token": None,
                "text": "I couldn't change that file's protection. Nothing "
                        "changed."}
    name = row["display_label"]
    return {"ok": True, "moved": False, "undo_token": None,
            "text": (f"{name} is protected now." if action == "hold" else
                     f"{name} is an ordinary file now.")}


def execute_confirmed(conn: sqlite3.Connection, kind: str,
                      ref: str, context: Any = None) -> dict[str, Any]:
    """Run a proposal the person said yes to (or their level allowed).

    Returns `{ok, moved, undo_token, text}`; `text` is a sentence for them.
    """
    from assistant.apply import SWITCHED_OFF, apply_enabled
    if kind in ("plan", "undo", "branch") and not apply_enabled(
            confirmed_by_person=True):
        return {"ok": False, "moved": False, "undo_token": None,
                "text": SWITCHED_OFF}
    if kind == "protection":
        return _protection(conn, ref)
    if kind == "rule":
        return _rule(conn, ref)
    if kind == "settings":
        level = int(ref.partition(":")[2])
        put_setting(conn, "permission_level", str(level))
        return {"ok": True, "moved": False, "undo_token": None,
                "text": f"Level {level} is on."}
    if kind == "branch":
        return _branch(conn, ref, undo=False)
    if kind == "undo" and ref.startswith("branch:"):
        return _branch(conn, ref.partition(":")[2], undo=True)
    if kind == "folder":
        action, _, folder = ref.partition(":")
        if context is not None:
            context.chosen_folders.add(Path(folder))
        result = (run_organise(conn, Path(folder), context)
                  if action == "organise" else
                  run_index(conn, Path(folder), context))
        return {"ok": bool(result.get("ok")), "moved": False,
                "undo_token": None,
                "text": result.get("error") or result.get("text") or
                        "Done. Nothing moved."}
    if kind == "plan":
        from assistant.apply import apply_plan
        from assistant.plans import approve_plan
        problem = _precheck(conn, ref)
        if problem:
            return {"ok": False, "moved": False, "undo_token": None,
                    "text": problem}
        approved = approve_plan(conn, ref, actor="user",
                                full_list_viewed=True)
        result = apply_plan(conn, ref, full_list_viewed=True,
                            confirmed_by_person=True) if approved.ok else None
        conn.commit()
        if result is None or not result.ok:
            moved = bool(result and result.moved)
            return {"ok": False, "moved": moved,
                    "undo_token": f"plan:{ref}" if moved else None,
                    "text": ("Some files moved before something got in the "
                             "way; say undo to put them back." if moved else
                             "I couldn't move those files, so nothing moved.")}
        n = len(result.applied)
        return {"ok": True, "moved": True, "undo_token": f"plan:{ref}",
                "text": f"Moved {_plural(n, 'file')}. Say undo to put "
                        f"{'it' if n == 1 else 'them'} back."}
    if kind == "undo":
        from assistant.undo import undo_plan
        _, _, plan_id = ref.partition(":")
        result = undo_plan(conn, plan_id, confirmed_by_person=True)
        conn.commit()
        if not result.ok:
            return {"ok": False, "moved": bool(result.moved),
                    "undo_token": None,
                    "text": ("A file was changed or moved since, so I "
                             "stopped and left it where it is.")}
        n = len(result.undone)
        return {"ok": True, "moved": True, "undo_token": None,
                "text": f"Put {_plural(n, 'file')} back."}
    return {"ok": False, "moved": False, "undo_token": None,
            "text": "I can't do that one. Nothing changed."}


# -- dispatch ---------------------------------------------------------------

def run(conn: sqlite3.Connection, name: str, args: dict,
        *, context: Any = None) -> dict[str, Any]:
    if name == "quick_sort":
        return quick_sort(conn, list(args.get("files") or []),
                          args.get("destination"))
    if name == "undo_last":
        return undo_last(conn)
    if name == "next_questions":
        return next_questions(conn, context)
    if name == "index_folder":
        return index_folder(conn, str(args.get("folder") or ""), context)
    if name == "organise_folder":
        return organise_folder(conn, str(args.get("folder") or ""), context)
    if name == "set_level":
        return set_level(conn, int(args.get("level") or 0))
    if name == "what_was_sent":
        return what_was_sent(conn)
    if name == "status":
        from assistant.session import _counts
        c = _counts(conn)
        return {"ok": True, "text": counts_sentence(c) if c else
                "Nothing is indexed yet.",
                "level": get_level(conn),
                "open_questions": len(open_questions(conn))}
    if name == "apply_branch":
        return apply_branch(conn, str(args.get("branch") or ""),
                            str(args.get("folder") or ""), context)
    if name == "mark_sensitive":
        return mark_sensitive(conn, str(args.get("file") or ""))
    if name == "release":
        return release(conn, str(args.get("file") or ""))
    if name == "remember_rule":
        return remember_rule(conn, str(args.get("text") or ""))
    if name == "list_rules":
        return list_rules(conn)
    if name == "forget_rule":
        return forget_rule(conn, int(args.get("number") or 0))
    if name == "forget_conversations":
        return forget_conversations(conn)
    return {"ok": False, "error": "That isn't something I can do."}
