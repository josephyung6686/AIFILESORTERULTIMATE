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
    conn.execute(SETTINGS_DDL)
    row = conn.execute("SELECT value FROM session_settings WHERE key = ?",
                       (key,)).fetchone()
    return row[0] if row is not None else default


def put_setting(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(SETTINGS_DDL)
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
              sensitive: bool = False,
              on_no: dict | None = None) -> dict[str, Any]:
    proposal = {"kind": kind, "ref": ref, "summary": summary,
                "moves": [{"from": a, "to": b} for a, b in moves],
                "sensitive": bool(sensitive)}
    if on_no is not None:
        proposal["on_no"] = on_no
    return {"ok": True, "needs_confirmation": proposal}


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
               destination: str | None = None,
               kind: str | None = None) -> dict[str, Any]:
    """Propose a one-off sort of named files, or of a suggestion's whole set
    (`kind`: the same files the greeting counted), each kind's files going
    into a folder beside them."""
    from assistant.plans import PlanOp, create_draft_plan
    found, missing, protected = [], [], []
    if kind:
        from items.suggest import KINDS, files_for
        if kind not in KINDS:
            return {"ok": False, "error": "I can sort screenshots, copies or "
                                          "installers as a set."}
        rows = files_for(conn, kind)
        if not rows:
            return {"ok": False, "error": f"There are no loose {kind} to "
                                          "sort."}
        files = []
        for row in rows:
            if item_is_sensitive(conn, row["item_id"]):
                protected.append(row["display_label"])
            else:
                found.append(row)
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
    folder = destination or (
        {"copies": "Copies"}.get(kind or "")
        or _type_folder([r["display_label"] for r in found]))
    target = parent / folder
    in_tree, not_placed = ({}, []) if destination or kind else _tree_places(
        conn, found, parent)
    pairs = [(row, src, in_tree.get(row["item_id"],
                                    src.parent / folder if kind else target)
              / src.name)
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


def undo_last(conn: sqlite3.Connection,
              context: Any = None) -> dict[str, Any]:
    token = getattr(context, "last_undo_token", None)
    if token and token.startswith("branch:"):
        # A branch move writes no assistant plan; the Session remembers it.
        return undo_proposal(conn, token)
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
    return _plain_and_holes(text, options)[0]


def _plain_and_holes(text: str, options) -> tuple[str, bool]:
    """`_plain`, and whether a code was dropped with nothing in its place --
    which leaves a sentence with a hole in it ("Which of these is?")."""
    holes = False
    for token in wording_problems(text):
        label = next((o.label for o in options
                      if token in {getattr(o, f.name) for f in fields(o)
                                   if f.name != "label"}), None)
        holes = holes or not label
        text = text.replace(token, label) if label else text.replace(token, "")
    text = re.sub(r"\s{2,}", " ", re.sub(r"\s+([?.,!])", r"\1", text)).strip()
    return text, holes


def _whole_sentences(text: str, options) -> str:
    """Only the sentences that read whole once codes are taken out."""
    kept = []
    for sentence in re.split(r"(?<=[.!?])\s+", text or ""):
        plain, holes = _plain_and_holes(sentence, options)
        if plain and not holes:
            kept.append(plain)
    return " ".join(kept)


def _branch_rows(conn, base: str, branch: str) -> list:
    """The files the plan places under a proposed folder of that name."""
    try:
        from assistant.organize_tools import _sorter_tree
        tree = _sorter_tree(conn)
    except Exception:
        return []
    if tree is None or not branch:
        return []
    ids = [file_id for file_id, d in tree["by_file"].items()
           if d.outcome == "place" and d.destination is not None and (
               (path := tree["path"](d.destination.node_id)) == branch
               or path.startswith(branch + "/"))][:400]
    if not ids:
        return []
    return conn.execute(base + f"AND file_id IN ({','.join('?' * len(ids))})"
                        " ORDER BY display_label LIMIT 40", ids).fetchall()


def _question_files(conn, q, count: int | None = None) -> list[str]:
    """Up to three ordinary files a question is about, by name. Never a
    protected or held one. Read from the index by the question's scope:
    a folder's own files, a kind's files, or the files nothing judged."""
    if conn is None:
        return []
    from items.file_identity import path_is_protected
    kind, _, rest = q.scope.partition(":")
    base = ("SELECT item_id, display_label, open_target FROM items "
            "WHERE presence = 'live' AND superseded_by IS NULL "
            "AND open_target IS NOT NULL AND coalesce(typing_state, '') "
            "!= 'held' ")
    try:
        if kind == "folder":
            rel = rest.strip("/")
            if rel in ("", "."):
                import json
                roots = {s for (sources,) in conn.execute(
                    "SELECT sources FROM corpus_selections")
                    for s in json.loads(sources or "[]")}
                rows = [r for r in conn.execute(
                    base + "ORDER BY display_label")
                    if str(Path(r["open_target"]).parent) in roots]
            else:
                rows = [r for r in conn.execute(
                    base + "AND open_target LIKE ? ORDER BY display_label",
                    (f"%/{rel}/%",))
                    if Path(r["open_target"]).parent.as_posix().endswith(
                        "/" + rel)]
        elif kind == "branch" and rest.startswith("default:"):
            rows = conn.execute(
                base + "AND type_schema IS NULL ORDER BY display_label "
                "LIMIT 40").fetchall()
        elif kind == "branch" and (placed := _branch_rows(conn, base, rest)):
            rows = placed
        elif kind == "branch" and rest and "." not in rest:
            rows = conn.execute(
                base + "AND (type_schema = ? OR type_schema LIKE ?) "
                "ORDER BY display_label LIMIT 40",
                (rest, rest + ".%")).fetchall()
        else:
            rows = []
    except sqlite3.Error:
        return []
    ordinary = [r for r in rows if not path_is_protected(r["open_target"])
                and not item_is_sensitive(conn, r["item_id"])]
    # A folder question is about SOME of the folder's files (those nothing
    # could read); its examples are shown only when they are all of them.
    if kind == "folder" and count is not None and len(ordinary) != count:
        return []
    names: list[str] = []
    for r in ordinary:
        if r["display_label"] not in names and not wording_problems(
                r["display_label"]):
            names.append(r["display_label"])
        if len(names) == 3:
            break
    return names


#: Sentences the sorter writes about its own workings -- counts of levels,
#: warnings, what a library carries -- which a person cannot act on.
_ENGINE_SENTENCE = re.compile(
    r"warning|would create|records? no values|library carries|kind-of-file "
    r"word|no model has judged|file\(s\)|unresolved|own facts|own words "
    r"support|nobody has said|not because anything", re.I)

#: An ordering number in front of a folder name ("98 Review and Unsorted"):
#: two digits, so a date such as "4 AUG 2023" is left alone.
_ORDERING = re.compile(r"^\d{2}\s+(?=\S)")


def display_name(path: str) -> str:
    """A folder path as the person reads it, without ordering numbers."""
    return "/".join(_ORDERING.sub("", part) for part in str(path).split("/"))


def _person_sentences(text: str, options) -> str:
    """The whole sentences of `text` that speak to the person, not about
    the engine."""
    return " ".join(
        s for s in re.split(r"(?<=[.!?])\s+", _whole_sentences(text, options))
        if s and not _ENGINE_SENTENCE.search(s))


def _folders_inside(branch: str, paths: list[str]) -> str:
    """The folders a shape builds inside `branch`, named from inside it:
    its first level, or the level under a single first folder."""
    rel = [p[len(branch) + 1:] if p.startswith(branch + "/") else p
           for p in paths]
    first = list(dict.fromkeys(p.split("/")[0] for p in rel))
    prefix = ""
    if len(first) == 1:
        second = list(dict.fromkeys(p.split("/")[1] for p in rel
                                    if p.count("/") >= 1))
        if second:
            prefix, first = first[0] + ": ", second
    more = f" and {len(first) - 5} more" if len(first) > 5 else ""
    return prefix + ", ".join(first[:5]) + more


def _option_label(o, options, branch: str) -> str:
    """An option as a folder path, or a short plain sentence."""
    if getattr(o, "chooses_destination", None):
        return display_name(o.label)
    if getattr(o, "gates_template", None) is not None:
        built = re.search(r"builds (.*?)(?: -- |$)", o.label)
        if built:
            return _folders_inside(branch, [
                display_name(re.sub(r" \(\d+\)$", "", c))
                for c in built.group(1).split(", ")])
        said = _person_sentences(o.label, options)
        return said or ("No subfolders: all of them go straight into "
                        f"{display_name(branch)}")
    return _plain(o.label, options)


def question_event(q, index: int, of: int, conn=None):
    """A sorter question as one plain sentence naming its files (folder,
    two or three names, the count). The sorter's own sentences about its
    workings are left out, and options that read the same are shown once
    (the first one's id is the answer)."""
    from assistant.events import Option, Question
    m = re.match(r"\s*(\d[\d,]*) files?\b", q.evidence_context or "")
    stated = int(m.group(1).replace(",", "")) if m else None
    names = _question_files(conn, q, stated)
    count = stated if stated is not None else len(names)
    kind, _, where = q.scope.partition(":")
    where = display_name(where.strip("/")) if kind in ("folder", "branch") \
        and not where.startswith("default:") else ""
    e_g = (f" ({names[0]})" if count == 1 and names else
           f" (e.g. {', '.join(names)})" if names else "")
    files = ("this file" if count == 1 else f"the {count} files" if count
             else "these files")
    inside = f" in {where}" if where and where != "." else ""
    text, holes = _plain_and_holes(q.prompt, q.options)
    if any(getattr(o, "gates_template", None) is not None
           for o in q.options):
        text = f"How should {files}{inside}{e_g} be split into folders?"
    elif any(getattr(o, "chooses_destination", None) for o in q.options):
        text = f"Where should {files}{inside}{e_g} go?"
    elif holes or not text:
        they = "it" if count == 1 else "they"
        asks = (f"what {'is' if count == 1 else 'are'} {they}?"
                if any(getattr(o, "selects_situation", None)
                       for o in q.options)
                else f"where should {they} live?")
        these = ("This file" if count == 1 else
                 f"These {count} files" if count else "Some of your files")
        text = f"{these}{e_g} — {asks}"
    elif names and not any(n in text for n in names):
        text = (f"{text} ({_plural(count, 'file')}"
                f"{', e.g. ' + ', '.join(names) if count > 1 else ': ' + names[0]})")
    options: list = []
    for o in q.options:
        label = _option_label(o, q.options, where or "this folder")
        if label and label not in [x.label for x in options]:
            options.append(Option(id=o.option_id, label=label))
    return Question(
        question_id=q.question_id,
        text=text[:1].upper() + text[1:],
        why=_person_sentences(q.evidence_context, q.options),
        changes=_person_sentences(q.unlocks, q.options),
        options=tuple(options),
        allow_text=True, allow_skip=True,
        files_preview=tuple(names), count=count, index=index, of=of)


def askable_questions(conn: sqlite3.Connection) -> tuple[tuple, dict]:
    """The sorter's open questions a person can answer, and a count of the
    rest: those about files inside a set-aside coding project, and those
    naming no file anyone could recognise (files nothing could read)."""
    try:
        from questions.store import open_questions as store_open
        every = store_open(conn)
    except sqlite3.Error:
        return (), {"inside_projects": 0, "unnamed_files": 0}
    from assistant.organize_tools import _set_aside_folders, inside_set_aside
    aside = _set_aside_folders(conn)
    asked, projects, unnamed = [], 0, 0
    for q in every:
        kind, _, rest = q.scope.partition(":")
        if kind == "folder" and aside and inside_set_aside(
                conn, rest.strip("/"), aside):
            projects += 1
            continue
        event = question_event(q, 1, 1, conn)
        # A folder's files, or a subject that was an internal code, are
        # nameable only by the files themselves.
        if not event.files_preview and (
                kind == "folder" or _plain_and_holes(q.prompt, q.options)[1]):
            unnamed += event.count or 1
            continue
        asked.append(q)
    return tuple(asked), {"inside_projects": projects,
                          "unnamed_files": unnamed}


def open_questions(conn: sqlite3.Connection) -> tuple:
    return askable_questions(conn)[0]


def skipped_sentence(skipped: dict) -> str:
    """The questions left unasked, as a plain count."""
    parts = []
    if skipped.get("unnamed_files"):
        n = skipped["unnamed_files"]
        parts.append(f"{_plural(n, 'file')} I couldn't read — "
                     f"{'it' if n == 1 else 'they'}'ll stay where "
                     f"{'it is' if n == 1 else 'they are'}.")
    if skipped.get("inside_projects"):
        n = skipped["inside_projects"]
        parts.append(f"{_plural(n, 'question')} about files inside coding "
                     f"projects {'was' if n == 1 else 'were'} skipped.")
    return " ".join(parts)


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
    # An answer can change the plan, so a lock-in the last run could not
    # offer is worth trying again.
    conn.execute(SETTINGS_DDL)
    conn.execute("UPDATE session_settings SET value = '' "
                 "WHERE key LIKE 'lock_in_blocked:%'")
    now = datetime.now(timezone.utc).isoformat()
    option = next((o.option_id for o in q.options
                   if typed == o.option_id
                   or typed.casefold() == o.label.casefold()), None)
    if option is None:
        # The words or the number the person was shown.
        shown = question_event(q, 1, 1, conn).options
        number = re.fullmatch(r"(?:option\s*)?(\d+)", typed.casefold())
        option = next((o.id for i, o in enumerate(shown, 1)
                       if typed.casefold() == o.label.casefold()
                       or (number and int(number.group(1)) == i)), None)
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


def answer_question(conn: sqlite3.Connection, answer: str,
                    context: Any) -> dict[str, Any]:
    """The person's words for the sorter question on their screen, recorded
    as a typed answer is. The Session asks the next one after the turn."""
    asking = getattr(context, "asking", None)
    queue = getattr(context, "question_queue", None) or []
    question_id = (asking.question_id if asking is not None else
                   queue[0].question_id if queue else None)
    if question_id is None:
        return {"ok": False, "error": "There is no question on the screen "
                                      "to answer."}
    try:
        kind = record_person_answer(conn, question_id, answer)
    except Exception:
        return {"ok": False, "error": "I couldn't save that answer. Nothing "
                                      "changed."}
    return {"ok": True, "recorded": kind, "moved": False,
            "text": {"choice": "Saved your answer.",
                     "skipped": "Skipped that question.",
                     "free_text": "Saved your answer in your words."}[kind]}


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


def _chosen_by_name(conn: sqlite3.Connection, folder: str,
                    context: Any) -> Path | None:
    """The person's chosen folder this argument names: "Desktop", "my
    desktop", "~/Desktop" or the real `/Users/x/Desktop` all mean the folder
    called Desktop that they chose. None when nothing chosen is named, or
    when the argument is already inside a chosen folder."""
    import json
    chosen = {Path(p) for p in getattr(context, "chosen_folders", ())}
    try:
        for row in conn.execute("SELECT sources FROM corpus_selections"):
            chosen.update(Path(s) for s in json.loads(row[0] or "[]"))
    except sqlite3.Error:
        pass
    asked = Path(folder.strip()).expanduser()
    if any(c == asked or c in asked.parents for c in chosen):
        return None
    words = re.sub(r"\b(my|the|folder|directory)\b", " ",
                   asked.name.lower()).split()
    name = " ".join(words)
    matches = [c for c in chosen if c.name.lower() == name]
    return matches[0] if len(matches) == 1 else None


def check_folder(conn: sqlite3.Connection, folder: str, context: Any,
                 action: str) -> tuple[Path | None, dict | None]:
    """(path, None) when the folder may be read now; otherwise (None, payload)
    refusing it or asking the person first."""
    from items.file_identity import path_is_protected
    path = _chosen_by_name(conn, folder, context) or Path(folder).expanduser()
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
        # Kept for the code that reads it (the branch names a freeze
        # prints); never shown to the person or the model.
        self.lines.extend(line.strip() for line in str(text).splitlines()
                          if line.strip())
        return len(text)

    def flush(self) -> None:
        pass


def organise_folder(conn: sqlite3.Connection, folder: str,
                    context: Any) -> dict[str, Any]:
    path, refusal = check_folder(conn, folder, context, "organise")
    if refusal is not None:
        return refusal
    return run_organise(conn, path, context)


def _stage(context: Any, line: str) -> None:
    emit = getattr(context, "emit", None)
    if emit is not None:
        from assistant.events import Progress
        emit(Progress(stage="organise", line=line))


def _cloud_ready() -> bool:
    """Whether a cloud model key is configured where the sorter looks."""
    import cli
    if os.environ.get(cli.CREDENTIAL_NAME, "").strip():
        return True
    if os.environ.get("GRAPH_AGENT_NO_DOTENV"):
        return False
    return bool((cli._dotenv(cli.ENV_FILE).get(cli.CREDENTIAL_NAME) or ""
                 ).strip())


def _cloud_undecided(conn: sqlite3.Connection, path: Path) -> bool:
    from database_agent.cloud_consent import cloud_consent_for
    try:
        return cloud_consent_for(conn, str(path)) is None
    except Exception:
        return False


ROUGH = ("I organised without the AI, so the folders will be rough. Say "
         "“use the AI to organise” any time to redo it properly.")


def run_organise(conn: sqlite3.Connection, path: Path, context: Any,
                 cloud: bool | None = None) -> dict[str, Any]:
    """The sorter over one folder, proposing folders and moving nothing.
    The person sees a few plain lines; the model gets counts read back from
    the database, never the sorter's screen.

    Before the first organise of a folder with no cloud decision (and a key
    to use), the person is asked whether the AI may read short excerpts of
    ordinary files. Yes is the sorter's own `--enable-cloud`, which records
    the per-folder consent; no runs offline. Protected files are never sent
    either way: that is the sorter's gate, untouched here."""
    import cli
    if cloud is None and _cloud_ready() and _cloud_undecided(conn, path):
        return _proposal(
            "cloud", str(path),
            "Organising works much better if the AI reads short excerpts of "
            "your ordinary files (never protected ones). Allow for "
            f"{_home_words(path)}?",
            on_no={"kind": "organise_offline", "ref": str(path)})
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
    _stage(context, "Reading and grouping your files…")
    try:
        # The whole proposal, placements included: a tree with no file in
        # it is nothing a person can judge, and the sorter places files
        # only into the groups it has accepted. "Lock in" accepts the same
        # groups (`--accept-groups --freeze`), so what is shown here is what
        # locking in would approve. Without `--freeze` nothing is approved
        # for moving and nothing moves.
        code = cli.main([str(path), "--database", database_path(conn),
                         "--accept-groups",
                         *(["--enable-cloud"] if cloud else [])], out=stream)
    except (Cancelled, KeyboardInterrupt):
        if emit is not None:
            from assistant.events import Message
            emit(Message(text="Stopped. Nothing moved."))
        return {"ok": False, "cancelled": True,
                "error": "The person stopped organising. Nothing moved."}
    except SystemExit as exc:
        code = exc.code
    except Exception:
        return {"ok": False, "error": "Organising stopped with a problem. "
                                      "Nothing moved."}
    # The sorter refuses a plan by name; lock-in reruns the same design and
    # would refuse it again, so it is not offered until a run succeeds.
    refused = (_refusal_text(stream.lines)
               if code not in (0, None) else "")
    put_setting(conn, f"lock_in_blocked:{path}", refused)
    if refused:
        return {"ok": False, "moved": False, "error": refused}
    _stage(context, "Designing folders… done.")
    asked, skipped = askable_questions(conn)
    n = len(asked)
    if n and context is not None:
        context.ask_questions_after_turn = True
    try:
        from assistant.organize_tools import organise_summary
        summary = organise_summary(conn, path)
    except Exception:
        summary = None
    if summary is not None and not summary.get("files_to_move"):
        # Locking in would freeze nothing: say so now, not after a rerun.
        put_setting(conn, f"lock_in_blocked:{path}", (
            "There's nothing to lock in yet: the plan doesn't move any file "
            f"({_plural(summary.get('files_already_in_place') or 0, 'file')} "
            "it places are already where it puts them). "
            + ("Answering the questions may change that. " if n else "")
            + "Nothing moved."))
    text = ((ROUGH + " " if cloud is False else "")
            + "I've looked through the folder. Nothing moved. "
            + (f"I have {_plural(n, 'question')} first. " if n else "")
            + (skipped_sentence(skipped) + " " if any(skipped.values())
               else "")
            + "When the folders look right, say “lock in the plan” and you "
              "can then move them one folder at a time.")
    return {"ok": True, "open_questions": n, "summary": summary,
            "moved": False, "text": text.strip(),
            "next_step": ("freeze_plan proposes locking in this plan; "
                          "apply_branch needs it first.")}


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
    protected = c.protected  # held files are already inside it
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


def _citation(path: str, name: str | None = None, note: str = ""):
    from assistant.events import Citation
    from assistant.session import _folder_of
    return Citation(name=name or Path(path).name, folder=_folder_of(path),
                    open_target=path, note=note)


def _size_words(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f} MB"
    return f"{max(1, round(n / 1000))} KB" if n else "0 KB"


def what_was_sent(conn: sqlite3.Connection,
                  context: Any = None) -> dict[str, Any]:
    """Today's requests to the AI model, from the egress ledger: how many,
    how big, and the files whose names or text went. Shown to the person
    by code; protected files are never listed (they were never sent)."""
    import json
    from datetime import datetime, timezone
    from assistant.egress import ensure_egress_schema
    from assistant.events import Message
    ensure_egress_schema(conn)
    today = datetime.now(timezone.utc).date().isoformat()
    rows = conn.execute(
        "SELECT provider, bytes, question, item_ids_json FROM egress_ledger "
        "WHERE ts >= ? ORDER BY ts", (today,)).fetchall()
    names = {"deepseek": "DeepSeek", "openai": "OpenAI",
             "anthropic": "Anthropic"}
    providers = sorted({names.get(r[0], r[0]) for r in rows})
    total = sum(int(r[1]) for r in rows)
    item_ids = list(dict.fromkeys(
        i for r in rows for i in json.loads(r[3] or "[]")))
    files = []
    for item_id in item_ids:
        row = conn.execute("SELECT display_label, open_target FROM items "
                           "WHERE item_id = ?", (item_id,)).fetchone()
        if row is None or not row[1] or item_is_sensitive(conn, item_id):
            continue
        files.append(_citation(row[1], row[0]))
    to = " and ".join(providers) or "the AI model"
    text = (f"Today: {_plural(len(rows), 'request')} to {to}, about "
            f"{_size_words(total)} in all — your messages, my replies and "
            "what I looked up.")
    text += (f" These {_plural(len(files), 'file')} had their names (and "
             "for some, a short piece of text) included:" if files else
             " No file names or text were included.")
    if context is not None and hasattr(context, "show_locally"):
        context.show_locally(Message(text=text, citations=tuple(files)))
    return {"ok": True, "shown_to_person": True, "requests": len(rows),
            "bytes": total, "sent_to": providers or ["nobody"],
            "files": [c.name for c in files],
            "note": "These numbers and files are on the person's screen. "
                    "Reply in one short sentence at most; do not repeat "
                    "them or say what else was or wasn't sent."}


def _why_protected(conn: sqlite3.Connection, row) -> str:
    """One plain reason, from the classification record's basis."""
    from items.file_identity import path_is_protected
    if row["open_target"] and path_is_protected(row["open_target"]):
        return "a key or password file"
    basis = ""
    try:
        from privacy.classification_store import ClassificationStore
        record = ClassificationStore(conn).current(row["file_id"],
                                                   row["content_hash"])
        basis = getattr(record, "basis", "") or ""
    except Exception:
        pass
    if basis == "user":
        return "you protected it"
    if basis == "safety_domain":
        return "looks like an ID, health, money or legal document"
    if basis.startswith("detector"):
        return "its name or text looks personal"
    return "protected"


def show_protected(conn: sqlite3.Connection,
                   context: Any = None) -> dict[str, Any]:
    """The protected files and folders, listed on this Mac with a reason.
    The model is told only how many."""
    from assistant.events import Message
    from items.identity import excluded_areas
    shown = []
    for row in conn.execute(
            "SELECT item_id, display_label, open_target, file_id, "
            "content_hash FROM items WHERE presence = 'live' AND "
            "superseded_by IS NULL AND item_type = 'file' "
            "ORDER BY display_label").fetchall():
        if row["open_target"] and item_is_sensitive(conn, row["item_id"]):
            shown.append(_citation(row["open_target"], row["display_label"],
                                   _why_protected(conn, row)))
    try:
        areas = [a for a in excluded_areas(conn) if a["protected"]]
    except Exception:
        areas = []
    for area in areas:
        shown.append(_citation(area["folder"],
                               note="a protected folder; nothing inside is "
                                    "opened"))
    if context is not None and hasattr(context, "show_locally"):
        context.show_locally(Message(
            text=("Protected — shown only to you, never sent anywhere:"
                  if shown else "Nothing is protected."),
            citations=tuple(shown)))
    return {"ok": True, "shown_to_person": len(shown),
            "note": "The list is on the person's screen, from this Mac. You "
                    "are not told the names; never guess them."}


def show_copies(conn: sqlite3.Connection,
                context: Any = None) -> dict[str, Any]:
    """Files with exactly the same content (by content hash), each copy
    beside the file it duplicates. Shown to the person by code."""
    from assistant.events import Message
    from items.suggest import _live_files, files_for
    copies = files_for(conn, "copies")
    hashes = list(dict.fromkeys(c["content_hash"] for c in copies))
    groups = {h: [] for h in hashes}
    for row in _live_files(conn):
        if row["content_hash"] in groups:
            groups[row["content_hash"]].append(row)
    shown, hidden = [], 0
    for h in hashes:
        group = groups[h]
        if any(item_is_sensitive(conn, r["item_id"]) for r in group):
            hidden += 1
            continue
        for row in group:
            others = [r["display_label"] for r in group if r is not row]
            shown.append(_citation(row["open_target"], row["display_label"],
                                   "same content as " + ", ".join(others)))
    text = ("Files with exactly the same content (I compared the files "
            "themselves, not their names):" if shown else
            "I found no files with exactly the same content.")
    if hidden:
        text += f" {_plural(hidden, 'set')} involving protected files not shown."
    if context is not None and hasattr(context, "show_locally"):
        context.show_locally(Message(text=text, citations=tuple(shown)))
    return {"ok": True, "shown_to_person": len(shown),
            "files": [c.name for c in shown],
            "note": "The pairs are on the person's screen, found by content."}


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
            "protected": c.protected, "moved": False,
            "text": counts_sentence(c)}


def index_folder(conn: sqlite3.Connection, folder: str,
                 context: Any) -> dict[str, Any]:
    path, refusal = check_folder(conn, folder, context, "index")
    if refusal is not None:
        return refusal
    return run_index(conn, path, context)


def freeze_plan(conn: sqlite3.Connection, folder: str,
                context: Any) -> dict[str, Any]:
    """Propose accepting the proposed folders and locking in the plan, so
    branches can be moved. Moves nothing; always asks."""
    path, refusal = check_folder(conn, folder, context, "organise")
    if refusal is not None:
        return refusal
    # Never a yes/no the sorter can already be seen to refuse.
    blocked = get_setting(conn, f"lock_in_blocked:{path}", "")
    if blocked:
        return {"ok": False, "error": blocked}
    if _selection_root(conn, path) is None:
        return {"ok": False, "error": "I haven't looked through that folder "
                                      "yet. Organise it first."}
    return _proposal("freeze", str(path),
                     f"Accept the proposed folders for {_home_words(path)} "
                     "and lock in the plan, so you can move them one folder "
                     "at a time? Nothing moves yet.")


def _branches_printed(lines: list[str]) -> list[str]:
    """The branch names the freeze printed, exactly as the sorter's apply
    flag takes them."""
    import shlex
    flag = "--" + "apply"
    found = []
    for line in lines:
        if flag not in line:
            continue
        try:
            parts = shlex.split(line)
        except ValueError:
            continue
        if flag in parts and parts.index(flag) + 1 < len(parts):
            name = parts[parts.index(flag) + 1]
            if name not in found:
                found.append(name)
    return found


def _refusal_text(lines: list[str]) -> str:
    """Why the sorter made no plan, or froze nothing, in the person's words.
    A refused folder's name is theirs to read; the code around it is not."""
    empty = next((m.group(1) for m in (
        re.search(r"accepting 'branch:([^']+)' produced no node", line)
        for line in lines) if m), None)
    if empty:
        return (f"I can't lock in this plan: the proposed folder "
                f"“{display_name(empty)}” has no file the sorter can put in "
                "it, so it refuses the whole plan. Nothing changed and "
                "nothing moved.")
    if any(line.startswith("Nothing was frozen") for line in lines):
        return ("Nothing could be locked in: every file is still waiting on "
                "a question or held for review. Nothing moved.")
    if any(line.startswith("No plan was made") for line in lines):
        return ("The sorter couldn't make a plan for this folder, so there "
                "is nothing to lock in. Nothing moved.")
    return ("There was nothing ready to lock in, so nothing changed. "
            "Nothing moved.")


def _freeze(conn: sqlite3.Connection, folder: str,
            context: Any) -> dict[str, Any]:
    """The sorter's own `--accept-groups --freeze`. Never moves a file."""
    import cli
    conn.commit()
    stream = _ProgressStream(context)
    try:
        code = cli.main([folder, "--database", database_path(conn),
                         "--accept-groups", "--freeze"], out=stream)
    except (Cancelled, KeyboardInterrupt):
        return {"ok": False, "moved": False, "undo_token": None,
                "text": "Stopped. Nothing is locked in and nothing moved."}
    except SystemExit as exc:
        code = exc.code
    except Exception:
        code = 1
    try:
        from assistant.organize_tools import show_tree
        tree = show_tree(conn)
    except Exception:
        tree = {}
    frozen = int(tree.get("frozen_moves") or 0)
    branches = _branches_printed(stream.lines)
    if code not in (0, None) or not frozen or not branches:
        return {"ok": False, "moved": False, "undo_token": None,
                "text": _refusal_text(stream.lines)}
    shown = [display_name(b) for b in branches]
    waiting = [f["path"] for f in tree.get("folders") or ()
               if f["kind"] != "existing" and "/" not in f["path"]
               and not any(b == f["path"] or b.startswith(f["path"] + "/")
                           for b in shown)]
    listed = "\n".join(f"  {b}" for b in shown[:12])
    more = (f"\n  and {len(shown) - 12} more" if len(shown) > 12 else "")
    rest = (f" {_plural(len(waiting), 'proposed folder')} "
            f"({', '.join(waiting[:5])}) "
            f"{'has' if len(waiting) == 1 else 'have'} nothing ready to "
            "move yet — still waiting on questions or a closer look."
            if waiting else "")
    return {"ok": True, "moved": False, "undo_token": None,
            "text": f"Locked in {_plural(len(shown), 'folder')} "
                    f"({_plural(frozen, 'file')}).{rest} Nothing moved yet. "
                    "Tell me which folder to move:\n" + listed + more}


def _real_branch(conn: sqlite3.Connection, branch: str) -> str:
    """The plan's own folder path for a name the person was shown (which
    has its ordering numbers dropped)."""
    try:
        from assistant.organize_tools import _sorter_tree
        tree = _sorter_tree(conn)
    except Exception:
        tree = None
    if tree is not None:
        shown = display_name(branch).casefold()
        for node_id in tree["nodes"]:
            path = tree["path"](node_id)
            if display_name(path).casefold() == shown:
                return path
    return branch


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
        return {"ok": False, "error": "There is no locked-in plan to move "
                                      "yet. Organise the folder, then lock "
                                      "in the plan (freeze_plan)."}
    branch = _real_branch(conn, branch)
    return _proposal("branch", f"{path}|{branch}",
                     f"Move the files planned for {display_name(branch)} in "
                     f"{_home_words(path)}? Every move can be undone.")


def _in_place(conn: sqlite3.Connection) -> int:
    """Moves the sorter's journal says happened and are not yet taken back."""
    try:
        from apply_run.run import applied_entries
        return len(applied_entries(conn))
    except sqlite3.Error:
        return 0


def _attempts(conn: sqlite3.Connection) -> int:
    try:
        return conn.execute("SELECT count(*) FROM execution_records"
                            ).fetchone()[0]
    except sqlite3.Error:
        return 0


def _why_nothing_moved(conn: sqlite3.Connection, since: int,
                       lines: list[str]) -> str:
    """The sorter's own reason, read from what it recorded for this attempt."""
    from apply_run.run import sentence_for
    rows = conn.execute(
        "SELECT result FROM execution_records ORDER BY rowid LIMIT -1 "
        "OFFSET ?", (since,)).fetchall()
    for (result,) in rows:
        try:
            sentence = sentence_for(result, cross_volume="it would have to "
                                    "cross to another drive")
        except Exception:
            sentence = None
        if sentence:
            return sentence
    text = " ".join(lines)
    if "Already filed" in text:
        return "they are already where the plan puts them."
    if "Nothing was frozen" in text:
        return "nothing in the locked-in plan goes into that folder."
    return "the sorter found nothing it could move there."


def _branch(conn: sqlite3.Connection, ref: str, undo: bool) -> dict[str, Any]:
    """Run the sorter's own `--apply` / `--undo` for one branch and report
    what its journal says actually happened, never the exit code alone."""
    import cli
    folder, _, branch = ref.partition("|")
    conn.commit()
    before, tried = _in_place(conn), _attempts(conn)
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
    n = (before - _in_place(conn)) if undo else (_in_place(conn) - before)
    if n <= 0:
        why = (_why_nothing_moved(conn, tried, stream.lines) if not undo
               else "nothing from that folder had been moved.")
        return {"ok": False, "moved": False, "undo_token": None,
                "text": f"0 files {'put back' if undo else 'moved'} — {why}"}
    them = "it" if n == 1 else "them"
    shown = display_name(branch)
    return {"ok": True, "moved": True,
            "undo_token": None if undo else f"branch:{ref}",
            "text": (f"Put {_plural(n, 'file')} back from {shown}." if undo
                     else f"Moved {_plural(n, 'file')} into {shown}. Say "
                          f"undo to put {them} back.")}


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


def _protect_without_a_run(conn: sqlite3.Connection, file_id: str,
                           now: str) -> None:
    """One `user` classification row, `protected=True`: it shuts the cloud
    door and `item_is_sensitive` reads it at once. Narrows, never widens."""
    import getpass
    import cli
    from privacy.classification_store import ClassificationStore
    from privacy.learning_seam import reclassify
    from privacy.schema import create_privacy_schema
    create_privacy_schema(conn)
    content_hash = conn.execute("SELECT content_hash FROM files "
                                "WHERE file_id = ?", (file_id,)).fetchone()[0]
    reclassify(conn, file_id, "sensitive_personal",
               "the person asked to protect this file in the conversation",
               store=ClassificationStore(conn), content_hash=content_hash,
               protected=True, evidence_refs=(), user_id=getpass.getuser(),
               component_version=cli.COMPONENT_VERSION, observed_at=now)


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
            # The person's protected row alone. `apply_file_held` would also
            # grant automatic moves on an organised folder, and the chat
            # promises a protected file "won't be moved automatically".
            _protect_without_a_run(conn, row["file_id"], now)
        else:
            cli.apply_release(conn, [row["file_id"]],
                              user_id=getpass.getuser(), recorded_at=now)
        conn.commit()
    except Exception:
        conn.rollback()
        return {"ok": False, "moved": False, "undo_token": None,
                "text": ("Nothing changed — organise this folder first, then "
                         "I can treat it as an ordinary file."
                         if action != "hold" else
                         "I couldn't protect that file. Nothing changed.")}
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
    if kind == "freeze":
        return _freeze(conn, ref, context)
    if kind == "branch":
        return _branch(conn, ref, undo=False)
    if kind == "undo" and ref.startswith("branch:"):
        return _branch(conn, ref.partition(":")[2], undo=True)
    if kind in ("cloud", "organise_offline"):
        result = run_organise(conn, Path(ref), context,
                              cloud=(kind == "cloud"))
        return {"ok": bool(result.get("ok")), "moved": False,
                "undo_token": None,
                "text": result.get("error") or result.get("text") or
                        "Done. Nothing moved."}
    if kind == "folder":
        action, _, folder = ref.partition(":")
        if context is not None:
            context.chosen_folders.add(Path(folder))
        result = (run_organise(conn, Path(folder), context)
                  if action == "organise" else
                  run_index(conn, Path(folder), context))
        if "needs_confirmation" in result:
            # The AI question follows the folder question; the Session
            # proposes it in turn.
            return {**result, "moved": False, "undo_token": None,
                    "text": result["needs_confirmation"]["summary"]}
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
                          args.get("destination"), args.get("kind"))
    if name == "undo_last":
        return undo_last(conn, context)
    if name == "next_questions":
        return next_questions(conn, context)
    if name == "answer_question":
        return answer_question(conn, str(args.get("answer") or ""), context)
    if name == "index_folder":
        return index_folder(conn, str(args.get("folder") or ""), context)
    if name == "organise_folder":
        return organise_folder(conn, str(args.get("folder") or ""), context)
    if name == "set_level":
        return set_level(conn, int(args.get("level") or 0))
    if name == "what_was_sent":
        return what_was_sent(conn, context)
    if name == "show_protected":
        return show_protected(conn, context)
    if name == "show_copies":
        return show_copies(conn, context)
    if name == "status":
        from assistant.session import _counts
        c = _counts(conn)
        return {"ok": True, "text": counts_sentence(c) if c else
                "Nothing is indexed yet.",
                "level": get_level(conn),
                "open_questions": len(open_questions(conn))}
    if name == "freeze_plan":
        return freeze_plan(conn, str(args.get("folder") or ""), context)
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
