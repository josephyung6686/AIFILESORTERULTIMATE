# src/understanding/attach.py
"""Run the understanding pass on files this scan did not place.

The provider is injected by the composition root. This module does not
open a socket and does not read a key.
"""
from __future__ import annotations

import sqlite3

from understanding.dossier import WORD_CAP, FileView, excerpt, path_is_protected
from understanding.run import Budget, run_understanding
from understanding.store import STATEMENT, consent_recorded

# More characters than 400 words, so the word cap is what truncates, and
# fewer than a whole document. The SQL `substr` is the bound.
EXCERPT_CHARS: int = 8000


def stored_excerpt(conn, file_id: str) -> str:
    """The start of the latest extracted text for this file.

    The query asks SQLite for a prefix, so the rest of the unit stays in
    the database. A folder with no extraction tables yields an empty
    excerpt. The word cap is applied by the dossier builder.
    """
    try:
        row = conn.execute(
            "SELECT substr(tu.text, 1, ?) FROM text_units AS tu "
            "JOIN extraction_runs AS er ON er.run_id = tu.run_id "
            "WHERE er.file_id = ? "
            "ORDER BY er.started_at DESC LIMIT 1",
            (EXCERPT_CHARS, file_id),
        ).fetchone()
    except sqlite3.OperationalError:
        return ""
    if row is None or not row[0]:
        return ""
    return excerpt(str(row[0]), word_cap=WORD_CAP)


def unplaced_views(conn, decisions, *, private_areas: set[str]) -> list[FileView]:
    from placement.vocabulary import PLACE
    wanted = []
    for decision in decisions:
        if decision.outcome == PLACE:
            continue
        file_id = getattr(decision.subject, "file_id", None)
        if not file_id:
            continue
        privacy = getattr(decision, "privacy", None)
        if privacy is not None and getattr(privacy, "protected", False):
            continue
        wanted.append(file_id)
    if not wanted:
        return []
    rows = conn.execute(
        "SELECT file_id, current_path, filename FROM files WHERE file_id IN "
        "(" + ",".join("?" for _ in wanted) + ")",
        tuple(wanted)).fetchall()
    by_id = {row[0]: row for row in rows}
    views = []
    for file_id in wanted:
        row = by_id.get(file_id)
        if row is None:
            continue
        path, filename = row[1], row[2]
        protected = path_is_protected(path)
        views.append(FileView(
            file_id=file_id, path=path, filename=filename,
            text="" if protected else stored_excerpt(conn, file_id),
            protected=protected))
    return views


def understand_unplaced(conn, decisions, *, directory, private_areas: set[str],
                        declared_areas: set[str], offline: bool, out,
                        provider=None, model_id: str = "", now: str = "") -> None:
    if offline:
        print("offline: the understanding pass sent nothing.", file=out)
        return
    root = str(directory)
    if not consent_recorded(conn, root):
        print(STATEMENT, file=out)
        print("Understanding did not run. Pass --accept-cloud-understanding "
              "once for this folder. Nothing was sent.", file=out)
        return
    views = unplaced_views(conn, decisions, private_areas=private_areas)
    if not views:
        print("Understanding: no unplaced file to ask about.", file=out)
        return
    if provider is None or not model_id:
        print("Understanding did not run: no model is configured. "
              "Nothing was sent.", file=out)
        return
    report = run_understanding(
        conn=conn, views=views, declared_areas=declared_areas,
        private_areas=private_areas, provider=provider, model_id=model_id,
        offline=False, consent=True, budget=Budget(), now=now)
    print(f"Understanding: {report.sent} sent, {report.cache_hits} from cache, "
          f"{report.excluded} excluded, {report.needs_review} need review, "
          f"{report.budget_stopped} stopped by the budget.", file=out)
