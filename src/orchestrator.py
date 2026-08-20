# src/orchestrator.py
"""Wave 2's caller: P3 scan -> P5 route/extract -> P4 record -> P1 status -> P2 bundle.

**Not a part.** It owns no design section, publishes no vocabulary, and adds no table.
`02-segmentation-map.md` says the walking skeleton "stays in the repository as the
integration test every later part must keep green"; this module makes the Wave-2 half
of it ONE path rather than four separate stories. P1, P2 and P3 shipped, P4 and P5
went green, and nothing called them in sequence: `scan()` returned a `scan_run_id`
and stopped.

What it owns:

1. **Order.** Once per scan run.
2. **The exception contract** -- which refusal produces a run row and which produces
   nothing.
3. **The two joins each part half-published** -- `source_scan_ref = scan_run_id` and
   `files.extraction_status_by_tier`.
4. **Passing `author` through.** M8, §8.2: the acting part authors, P1 stores.

What it does not own: no vocabulary (it spells no `completeness`, `source_type`,
`analysis_tier`, zone or event type -- every such value reaches P1/P4 inside a record
a part constructed), no derivation (`extraction_status_by_tier` is P5's,
`bundle_counts` P2's), no ceiling enforcement, no refusal of its own, and no
authorship: it never appears in an event's `subsystem`. §8.2's reconstruction
requirement is unmeetable from a log whose author field names the thing that merely
arranged the work.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from database_agent.files_table import get_file as _get_file_row, set_extraction_status

from eval_harness.bundle import (
    add_extraction_run, add_file_entry, add_text_unit, open_bundle, seal_bundle,
)

from evidence_shape.store import runs_for_content, text_units_for_run

from extractors.authorship import COMPONENT_VERSION, SUBSYSTEM
from extractors.dispatch import current_versions, extract
from extractors.failure import failed_result
from extractors.filesystem import dataless_result, extract_filesystem
from extractors.router import route
from extractors.runs import extraction_status_by_tier
from extractors.safety import DatalessRefused, ProtectedContainerRefused

from scan_agent.dataless import dataless_detections
from scan_agent.scan import scan
from scan_agent.stat_cache import VERDICT_RECOMPUTE, cache_verdicts


@dataclass(frozen=True)
class Wave2:
    """What one pass produced. Handles, not counts: the counts are P2's."""
    scan_run_id: str
    bundle_id: str
    run_ids: tuple[str, ...]


def get_file(conn: sqlite3.Connection, file_id: str) -> dict:
    """P1's row as a plain mapping.

    `sqlite3.Row` supports indexing and not `.get`, and P5's constructors ask a row
    for optional fields -- `dataless_result` checks `file_row.get("file_id")` before
    it will build a run at all. Converting once here beats every extractor learning
    which row type it was handed, and it is the same reason the readers are injected:
    P5 should not know where its `file_row` came from.
    """
    return dict(_get_file_row(conn, file_id))


def _extraction_is_stale(conn: sqlite3.Connection, content_hash: str,
                        versions: Mapping[str, str]) -> bool:
    """Has any extractor that already ran on this content been upgraded since?

    §3.4 puts the extractor version in the cache key so that "stale results" do not
    survive and "model or prompt changes" stay auditable. §1.2's stat-cache verdict
    keys on path, mtime and size and holds no version, so REUSE alone would mean a bug
    shipped in `pdf.text 0.1.0` stays in the database for the life of the corpus --
    two caches, and the outer one wins.

    An extractor with no published version -- OCR, whose version is the provider's --
    is never called stale here. Guessing would be worse than the gap.
    """
    for run in runs_for_content(conn, content_hash):
        current = versions.get(run.extractor_name)
        if current is not None and current != run.extractor_version:
            return True
    return False


def _write(sink, result, written: list[str]) -> str:
    run_id = sink.write(result)
    written.append(run_id)
    return run_id


def _extract_one(*, file_row, path, decision, policy, readers, now, context_window,
                 no_usable_facts, transcription_authorized):
    """Every run this file's routing decision calls for, or the run its failure is.

    A reader that raises becomes one `failed` run rather than the end of the scan.
    §2.4's rule is that an unreadable file must never be "silently treated as an empty
    document", and a crashed scan is a worse version of the same lie: the file is not
    empty, it is unexamined. The exception is the signal -- there is no threshold here
    for "too corrupt" and no retry count.

    The two refusals from `admit()` are NOT caught here. They are the caller's, and
    they are the one place the two differ: see `run_wave2`.
    """
    try:
        dispatched = extract(
            file_row=file_row, decision=decision, path=path, policy=policy,
            readers=readers, now=now, context_window=context_window,
            no_usable_facts=no_usable_facts,
            transcription_authorized=transcription_authorized)
        return dispatched.results
    except (ProtectedContainerRefused, DatalessRefused):
        raise
    except Exception as error:                       # noqa: BLE001 -- see docstring
        return (failed_result(
            file_row=file_row, error=error,
            extractor_name=decision.extractor_name,
            extractor_version=decision.router_version,
            source_type=decision.source_type, now=now),)


def run_wave2(conn: sqlite3.Connection, selection_id: str, *,
              source, mime_type_for: Callable[[Path], str | None],
              scan_state: str, budget_exhausted: Callable[[], bool],
              detect_format: Callable[[Path], str | None],
              policy, readers, sink, now: Callable[[], str],
              context_window: int,
              no_usable_facts: Callable[[str, str], bool],
              transcription_authorized: Callable[[], bool],
              corpus_form: str, policy_settings: Mapping[str, Any],
              file_entry_body: Callable[[Mapping[str, Any]],
                                        Mapping[str, str]]) -> Wave2:
    """One scan, extracted, recorded and bundled.

    Every value passed on came from the part that owns it. `sink`, `policy`,
    `readers`, `detect_format`, `now`, `corpus_form` and `policy_settings` are
    caller-supplied; `scan_state` is P3's (SPEC Q4 is open) and `mime_type_for`
    answers P3's Q6. None is a value this module names.

    `file_entry_body` returns the kwargs for one `bundle_file_entry` -- either
    `{"payload_ref": ...}` for a snapshot bundle or `{"metadata_only": ...}` for a
    metadata-safe one. It is injected because WHERE a bundle keeps its payloads is
    the caller's, and because §8.4 requires the privacy gate to decide what a bundle
    may carry before anything is written into one; P7 is unbuilt and this module is
    not the place to guess. P2 enforces the exactly-one rule and the corpus_form
    match, so an inconsistent caller is refused there rather than half-written here.
    """
    # 1 -- P3. Full Disk Access is checked INSIDE scan(), before the run row exists
    #      (11 §1), so a refused scan leaves no partial corpus and no run to mistake
    #      for one.
    scan_run_id = scan(conn, selection_id, source=source,
                       mime_type_for=mime_type_for, scan_state=scan_state,
                       budget_exhausted=budget_exhausted)
    written: list[str] = []

    # 2 -- the roster. §1.2's stat cache: on REUSE, P5 is not invoked and prior
    #      results stand. That is resumption's work done without being called that.
    versions = current_versions()
    for verdict in cache_verdicts(conn, scan_run_id):
        if verdict["file_id"] is None:
            continue
        if verdict["verdict"] != VERDICT_RECOMPUTE and not _extraction_is_stale(
                conn, get_file(conn, verdict["file_id"])["content_hash"], versions):
            continue
        file_row = get_file(conn, verdict["file_id"])
        # `current_path`, not `path`. The live column is `current_path` and the
        # sketch on 18-wave2-orchestrator.md would KeyError on the first file.
        path = Path(file_row["current_path"])
        decision = route(file_id=file_row["file_id"],
                         content_hash=file_row["content_hash"], path=path,
                         extension=file_row["extension"],
                         detect_format=detect_format)
        stamp = now()
        try:
            results = [extract_filesystem(file_row=file_row, path=path, policy=policy,
                                          now=stamp, context_window=context_window)]
            results.extend(_extract_one(
                file_row=file_row, path=path, decision=decision, policy=policy,
                readers=readers, now=stamp, context_window=context_window,
                no_usable_facts=no_usable_facts,
                transcription_authorized=transcription_authorized))
        except ProtectedContainerRefused:
            # 11 §4b, ratified 2026-08-20. NOTHING: no run row, no observation, no
            # status write for anything inside. `continue` the outer loop and never
            # `break` the inner one -- a `break` falls through to the status write
            # below, which is a P1 write authored "P5" against a file the product is
            # forbidden to have touched. P3's exclusion verdict on the CONTAINER,
            # reason `protected_container`, is the whole record, and P13 presents
            # those as their own inspectable list.
            continue
        except DatalessRefused as refusal:
            # 11 §5, and the asymmetry is not an inconsistency. Both refusals protect
            # a read; they differ in what the product is permitted to KNOW. Nothing
            # inside a protected container ever acquires a file_id or a content_hash,
            # so a run row there is unconstructible. A dataless file's identity is
            # already known, and §8.6 requires it to stay visible AS unfinished.
            results = [dataless_result(file_row=file_row, error=refusal,
                                       source_type=decision.source_type, now=stamp)]

        for result in results:
            _write(sink, result, written)

        # 3 -- P1. The map is P5's; P1 stores it opaquely and interprets no key.
        set_extraction_status(
            conn, file_row["file_id"],
            status_by_tier=extraction_status_by_tier([r.run for r in results]),
            author=SUBSYSTEM, component_version=COMPONENT_VERSION)

    # 2b -- the evicted files. A file scanned while local and since moved to iCloud
    #       usually keeps its size and mtime, so its verdict is REUSE and the loop
    #       above skips it -- which is right for its CONTENT and wrong for its state.
    #       C4's ninth `completeness` value exists so §8.6's line can say "31 files
    #       are in iCloud", and it is reachable only from here. A file dataless at
    #       first sight has no `files` row (OQ3) and `dataless_result` refuses it.
    for detection in dataless_detections(conn, scan_run_id):
        row = conn.execute(
            "SELECT file_id FROM files WHERE current_path = ?",
            (detection["path"],)).fetchone()
        if row is None:
            continue
        file_row = get_file(conn, row["file_id"])
        decision = route(file_id=file_row["file_id"],
                         content_hash=file_row["content_hash"],
                         path=Path(file_row["current_path"]),
                         extension=file_row["extension"],
                         detect_format=detect_format)
        result = dataless_result(
            file_row=file_row,
            error=DatalessRefused(f"{detection['path']} is a dataless item"),
            source_type=decision.source_type, now=now())
        _write(sink, result, written)
        set_extraction_status(
            conn, file_row["file_id"],
            status_by_tier=extraction_status_by_tier([result.run]),
            author=SUBSYSTEM, component_version=COMPONENT_VERSION)

    # 4 -- P2. The join P3 published, P1 adopted, and nothing made until now.
    bundle_id = open_bundle(conn, corpus_form=corpus_form,
                            source_scan_ref=scan_run_id,
                            pinned_plan_id=None, pinned_plan_version=None,
                            policy_settings=dict(policy_settings))
    for file_row in conn.execute("SELECT * FROM files"):
        add_file_entry(conn, bundle_id, file_id=file_row["file_id"],
                       content_hash=file_row["content_hash"],
                       hash_algorithm=file_row["hash_algorithm"],
                       # P7's, and P7 is unbuilt. P1's column is the only source and
                       # it is NULL until a gate writes it; passing it through keeps
                       # the unknown visible as unknown rather than as "public".
                       handling_class=file_row["sensitivity_state"],
                       **file_entry_body(dict(file_row)))
    for run_id in written:
        row = conn.execute("SELECT * FROM extraction_runs WHERE run_id = ?",
                           (run_id,)).fetchone()
        add_extraction_run(conn, bundle_id, row=dict(row))
        for unit in text_units_for_run(conn, run_id):
            add_text_unit(conn, bundle_id, row=unit.to_mapping())
    seal_bundle(conn, bundle_id)

    return Wave2(scan_run_id=scan_run_id, bundle_id=bundle_id,
                 run_ids=tuple(written))
