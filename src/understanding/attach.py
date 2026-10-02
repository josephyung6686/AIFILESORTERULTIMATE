# src/understanding/attach.py
"""Run the understanding pass on files this scan did not place.

The provider is injected by the composition root. This module does not
open a socket and does not read a key.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from understanding.answer import interpret_answer
from understanding.dossier import (
    WORD_CAP, FileView, NotSendable, build_dossier, dossier_hash, excerpt,
    path_is_protected,
)
from understanding.run import Budget, run_understanding
from understanding.store import STATEMENT, cache_get, consent_recorded

# More characters than 400 words, so the word cap is what truncates, and
# fewer than a whole document. The SQL `substr` is the bound.
EXCERPT_CHARS: int = 8000


def stored_excerpt(conn, file_id: str) -> str:
    """The start of the latest extracted text for this file.

    The query asks SQLite for a prefix, so the rest of the unit stays in
    the database. When two runs share a timestamp, the longer text wins:
    a filename record is not the document. A folder with no extraction
    tables yields an empty excerpt. The word cap is applied by the dossier
    builder.
    """
    try:
        row = conn.execute(
            "SELECT substr(tu.text, 1, ?) FROM text_units AS tu "
            "JOIN extraction_runs AS er ON er.run_id = tu.run_id "
            "WHERE er.file_id = ? "
            "ORDER BY er.started_at DESC, length(tu.text) DESC LIMIT 1",
            (EXCERPT_CHARS, file_id),
        ).fetchone()
    except sqlite3.OperationalError:
        return ""
    if row is None or not row[0]:
        return ""
    return excerpt(str(row[0]), word_cap=WORD_CAP)


def indexed_views(conn, directory) -> list[FileView]:
    """Every ordinary file this scan indexed, when no plan was made.

    Nothing was placed, so each of these is unplaced. A protected path is
    marked and carries no excerpt.
    """
    root = directory.resolve()
    rows = conn.execute(
        "SELECT file_id, current_path, filename FROM files").fetchall()
    views = []
    for file_id, path, filename in rows:
        try:
            Path(path).resolve().relative_to(root)
        except ValueError:
            continue
        protected = path_is_protected(path)
        views.append(FileView(
            file_id=file_id, path=path, filename=filename,
            text="" if protected else stored_excerpt(conn, file_id),
            protected=protected))
    return views


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


@dataclass(frozen=True)
class ResidualSelection:
    """What a second pass may still send.

    ``pending`` has not been settled: no cached answer, or the rules never
    placed the file and the first pass did not reach it. ``settled`` already
    has a life area. ``already_review`` was asked and the answer was
    needs-review; it is not sent again. ``excluded`` is protected or private.
    """

    pending: tuple[FileView, ...]
    settled: int
    already_review: int
    excluded: int


def placed_file_ids(conn) -> set[str]:
    """File ids the latest plan placed. Empty when this database has no plan.

    A missing table is an unscanned database, not a placed file. The subject
    address is ``file:<file id>:<content hash>``; the hash is the last field.
    """
    from placement.vocabulary import FILE, PLACE
    try:
        row = conn.execute(
            "SELECT plan_version_id FROM plan_versions "
            "ORDER BY created_at DESC, rowid DESC LIMIT 1"
        ).fetchone()
    except sqlite3.OperationalError:
        return set()
    if row is None:
        return set()
    try:
        rows = conn.execute(
            "SELECT subject_ref, outcome FROM placement_decisions "
            "WHERE plan_version = ? AND superseded_by IS NULL",
            (row[0],),
        ).fetchall()
    except sqlite3.OperationalError:
        return set()
    placed: set[str] = set()
    prefix = f"{FILE}:"
    for subject_ref, outcome in rows:
        if outcome != PLACE:
            continue
        ref = "" if subject_ref is None else str(subject_ref)
        if not ref.startswith(prefix):
            continue
        file_id, sep, _digest = ref[len(prefix):].rpartition(":")
        if sep and file_id:
            placed.add(file_id)
    return placed


def residual_views(conn, directory, *, private_areas: set[str],
                   declared_areas: set[str], model_id: str,
                   profile_note: str = "") -> ResidualSelection:
    """Unplaced files that still need a call.

    A placed file is not asked again. A cached answer that names a life area
    is not asked again. A cached needs-review answer was already paid for
    and stays in the review pile. A file with no cache row — a budget stop,
    a rejected call, a file the first pass never reached — is pending.
    """
    placed = placed_file_ids(conn)
    pending: list[FileView] = []
    settled = 0
    already_review = 0
    excluded = 0
    for view in indexed_views(conn, directory):
        if view.file_id in placed:
            continue
        try:
            dossier = build_dossier(view, private_areas=private_areas)
        except NotSendable:
            excluded += 1
            continue
        cached = cache_get(
            conn, dossier_hash(
                dossier, model_id=model_id, profile_note=profile_note))
        if cached is None:
            pending.append(view)
            continue
        try:
            understood = interpret_answer(
                cached, file_id=view.file_id, declared_areas=declared_areas)
        except Exception:  # noqa: BLE001 -- an unreadable row is not a new call
            already_review += 1
            continue
        if understood.needs_review:
            already_review += 1
        else:
            settled += 1
    return ResidualSelection(
        pending=tuple(pending), settled=settled,
        already_review=already_review, excluded=excluded)


def _print_understanding_summary(report, budget: Budget, out) -> None:
    print(f"Understanding: {report.sent} sent, {report.cache_hits} from cache, "
          f"{report.excluded} excluded, {report.needs_review} need review, "
          f"{report.budget_stopped} stopped by the budget "
          f"({budget.calls} of {budget.max_calls} calls, "
          f"{budget.input_tokens} of {budget.max_input_tokens} "
          f"estimated input tokens).", file=out)
    if report.budget_stopped:
        print("Those files were not sent. Raise --understand-max-calls, "
              "or run the same folder again with --understand-residuals "
              "to ask only about what is still open.", file=out)
    print_after_understanding(report, out)


def understand_unplaced(conn, decisions, *, directory, private_areas: set[str],
                        declared_areas: set[str], offline: bool, out,
                        provider=None, model_id: str = "", now: str = "",
                        profile_note: str = "", budget: Budget | None = None) -> None:
    if offline:
        print("offline: the understanding pass sent nothing.", file=out)
        return
    root = str(directory)
    if not consent_recorded(conn, root):
        print(STATEMENT, file=out)
        print("Understanding did not run. This folder has no record that "
              "dossier text may be sorted with the model provider. "
              "Run `filesorter onboard` for this folder. Nothing was sent.",
              file=out)
        return
    if decisions is None:
        views = indexed_views(conn, directory)
    else:
        views = unplaced_views(conn, decisions, private_areas=private_areas)
    if not views:
        print("Understanding: no unplaced file to ask about.", file=out)
        return
    if provider is None or not model_id:
        print("Understanding did not run: no model is configured. "
              "Nothing was sent.", file=out)
        return
    budget = budget or Budget()
    report = run_understanding(
        conn=conn, views=views, declared_areas=declared_areas,
        private_areas=private_areas, provider=provider, model_id=model_id,
        offline=False, consent=True, budget=budget, now=now,
        profile_note=profile_note)
    _print_understanding_summary(report, budget, out)


def understand_residuals(conn, *, directory, private_areas: set[str],
                         declared_areas: set[str], offline: bool, out,
                         provider=None, model_id: str = "", now: str = "",
                         profile_note: str = "",
                         budget: Budget | None = None) -> None:
    """Ask only about files a previous pass left open. Does not scan.

    The caller has already opened the plan database. This reads the indexed
    files and the understanding cache. It does not walk the folder.
    """
    if offline:
        print("offline: the understanding pass sent nothing.", file=out)
        return
    root = str(directory)
    if not consent_recorded(conn, root):
        print(STATEMENT, file=out)
        print("Understanding did not run. This folder has no record that "
              "dossier text may be sorted with the model provider. "
              "Run `filesorter onboard` for this folder. Nothing was sent.",
              file=out)
        return
    if provider is None or not model_id:
        print("Understanding did not run: no model is configured. "
              "Nothing was sent.", file=out)
        return
    try:
        selection = residual_views(
            conn, directory, private_areas=private_areas,
            declared_areas=declared_areas, model_id=model_id,
            profile_note=profile_note)
    except sqlite3.OperationalError:
        print("Understanding residuals needs a scan of this folder first. "
              "Nothing was sent.", file=out)
        return
    print(f"Understanding residuals: {len(selection.pending)} still to ask, "
          f"{selection.settled} already settled, "
          f"{selection.already_review} still need review from an earlier "
          f"answer, {selection.excluded} excluded.", file=out)
    if not selection.pending:
        print("Understanding: no residual file to ask about.", file=out)
        return
    budget = budget or Budget()
    report = run_understanding(
        conn=conn, views=list(selection.pending), declared_areas=declared_areas,
        private_areas=private_areas, provider=provider, model_id=model_id,
        offline=False, consent=True, budget=budget, now=now,
        profile_note=profile_note)
    _print_understanding_summary(report, budget, out)


def print_after_understanding(report, out) -> None:
    """Life areas the pass named, including answers that came from the cache.

    ``What you have`` is the rules' reading and it is printed before this pass.
    A file the rules left unnamed stays in that earlier block. This block is
    the pass's own reading, so a successful run is not summarised only as unsorted.
    """
    areas: dict[str, int] = {}
    review = 0
    excluded = 0
    flagged = 0
    for result in report.results:
        if result.status == "excluded":
            excluded += 1
            continue
        understood = result.understanding
        area = getattr(understood, "life_area", None) if understood is not None else None
        if isinstance(area, str) and area.strip() and area != "needs_review":
            areas[area] = areas.get(area, 0) + 1
            if getattr(understood, "needs_review", False):
                flagged += 1
        else:
            review += 1
    total = len(report.results)
    noun = "file" if total == 1 else "files"
    print("", file=out)
    print(f"After understanding: {total} {noun}.", file=out)
    notice = getattr(report, "balance_notice", "") or ""
    if notice:
        print(f"    {notice}", file=out)
    for area, count in sorted(areas.items(), key=lambda item: (-item[1], item[0])):
        print(f"    {count} {area}", file=out)
    if review:
        print(f"    {review} need review", file=out)
    if excluded:
        print(f"    {excluded} excluded", file=out)
    if flagged:
        print(f"    {flagged} of the named files need review", file=out)
