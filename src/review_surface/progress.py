"""§8.6's progress line. Completed and deferred are never one number.

    "The user interface should show the difference between completed work and
    deferred work."
    "This makes the product's limitations legible and avoids the false impression
    that an unprocessed file was understood and found unimportant."

That last sentence is the reason this record exists, and it is why
`FileAbsentFromEveryEntry` is raised rather than logged: a file that reaches no
entry has been silently dropped from the user's picture of their own corpus, and a
progress line that omits it looks complete.

FOUR THINGS ARE INJECTED WITH NO DEFAULT, because the SPEC's own Open questions
decide them and P13 must not answer any of them in arithmetic:

* `precedence` -- how a file with runs in several completeness states is bucketed
  (Open question 4). P4's record is per (file version x extractor) and §8.6's line
  is per file, and nothing in the design arbitrates between them.
* `awaiting_model_review` and `flagged_by_model_review` -- §8.6's "34 files require
  model review" admits two readings over two different populations (Open question
  3), so BOTH are entries and neither is called "34".
* `cause_for` -- which ceiling produced a deferral. §8.6 requires the cause NAMED,
  not implied, and the ceiling values are P1's configuration (G4). P13 displays
  the ceiling that fired and never a value of its own.

`dataless` is live in P4 and absent from the P13 SPEC's eight-state Contract-in.
It gets its own labelled entry rather than being folded into `unreadable` or
`complete`: whether it belongs under either is the owner's, and an entry keeps the
choice visible instead of burying it.

**P4 publishes `COMPLETENESS` as a tuple and no named constant per member**, so
the state names below are spelled here and immediately checked against the live
tuple. That check is the whole safety: if P4 renames or adds a state, this module
fails to import rather than silently bucketing it nowhere.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence

from evidence_shape.runs import ExtractionRun
from evidence_shape.store import runs_for_content
from evidence_shape.vocabulary import COMPLETENESS

from review_surface.records import INDEXED, ProgressEntry, ProgressLine
from review_surface.vocabulary import (
    SOURCE_P3_R5,
    SOURCE_P4_RUNS,
    SOURCE_P8,
    STATE_BLOCKED,
    STATE_COMPLETED,
    STATE_DEFERRED,
)

#: The one state that means the whole file is done, per the SPEC's own rule that
#: a file counts as fully extracted only when EVERY run over its current content
#: hash reports it.
COMPLETE: str = "complete"

#: P5's published mapping, restated as the pair it is: an `unreadable` run and a
#: `failed` run both mean the product could not obtain usable content. Taking the
#: pair rather than `unreadable` alone is what stops a `failed` run appearing in
#: no entry at all, which the §8.6 rule forbids.
UNREADABLE_STATES: tuple[str, ...] = ("unreadable", "failed")

#: Which of §8.6's three states each P4 bucket reports as. A deferral is deferred;
#: a file the product cannot read or has no extractor for is blocked; everything
#: partial is deferred, because it is work that has not finished rather than work
#: that failed.
BUCKET_STATE: Mapping[str, str] = {
    "complete": STATE_COMPLETED,
    "capped": STATE_DEFERRED,
    "partial": STATE_DEFERRED,
    "metadata_only": STATE_DEFERRED,
    "deferred": STATE_DEFERRED,
    "dataless": STATE_DEFERRED,
    "unsupported": STATE_BLOCKED,
    "unreadable": STATE_BLOCKED,
    "failed": STATE_BLOCKED,
}
assert set(BUCKET_STATE) == set(COMPLETENESS), (
    "P4 changed its completeness vocabulary; a state with no bucket would land "
    "in no entry, which §8.6 forbids")
assert COMPLETE in COMPLETENESS
assert set(UNREADABLE_STATES) <= set(COMPLETENESS)

#: A file with no run at all. NOT one of P4's states, because P4 has no record for
#: it -- which is precisely the case §8.6's sentence is about.
NOT_YET_PROCESSED: str = "not yet processed"

#: The labels §8.6's own example uses, spelled once each.
FULLY_EXTRACTED: str = "fully extracted"
UNREADABLE: str = "unreadable"
AWAITING_MODEL_REVIEW: str = "awaiting model review"
FLAGGED_BY_MODEL_REVIEW: str = "flagged by model review"


class FileAbsentFromEveryEntry(RuntimeError):
    """An indexed file reached no entry. §8.6 forbids exactly this."""


class CompletenessPrecedenceRequired(ValueError):
    """A precedence that does not cover every live completeness state."""


def _require_precedence(precedence: Sequence[str]) -> None:
    if set(precedence) != set(COMPLETENESS):
        raise CompletenessPrecedenceRequired(
            f"the precedence must cover every one of P4's {len(COMPLETENESS)} "
            f"completeness states. Missing: "
            f"{sorted(set(COMPLETENESS) - set(precedence))}; unknown: "
            f"{sorted(set(precedence) - set(COMPLETENESS))}. SPEC Open question "
            "4 is open, so the arbitration is the caller's stated choice and "
            "P13 supplies none")


def bucket_for(runs: Sequence[ExtractionRun], *,
               precedence: Sequence[str]) -> str:
    """The one bucket a file falls in, by the caller's stated precedence.

    Worst-first: the caller lists the states in the order that decides ties, and
    the first one present wins. A file with no runs is `NOT_YET_PROCESSED`, which
    is a real answer and not a missing one.
    """
    _require_precedence(precedence)
    if not runs:
        return NOT_YET_PROCESSED
    present = {run.completeness for run in runs}
    for state in precedence:
        if state in present:
            return state
    return NOT_YET_PROCESSED


def assert_every_file_accounted(indexed_files: Mapping[str, str],
                                entries: Sequence[ProgressEntry]) -> None:
    """§8.6's rule, as a function so it can be pointed at any entry list.

    `indexed` is skipped because it is the POPULATION rather than a bucket:
    counting it would make every line account for everything and the rule could
    never fail. The refusal names the files, not just how many, because a count
    tells the reader something is missing and not which thing.
    """
    accounted = {file_id for entry in entries if entry.label != INDEXED
                 for file_id in entry.file_ids}
    missing = sorted(set(indexed_files) - accounted)
    if missing:
        raise FileAbsentFromEveryEntry(
            f"{len(missing)} indexed file(s) reach no entry: {missing}. §8.6 "
            "requires that no indexed file is absent from every entry, because "
            "a progress line that omits a file creates the false impression "
            "that an unprocessed file was understood and found unimportant")


def progress_line(conn: sqlite3.Connection, *, scan_ref: str,
                  plan_version: str, rendered_at: str,
                  indexed_files: Mapping[str, str],
                  precedence: Sequence[str],
                  awaiting_model_review: Callable[[], Sequence[str]],
                  flagged_by_model_review: Callable[[], Sequence[str]],
                  cause_for: Callable[[str], str | None]) -> ProgressLine:
    """Assemble §8.6's line from real records. Every indexed file lands somewhere.

    `indexed_files` maps `file_id -> current content_hash`, which is P3's R5
    population joined to P1's current version. It is passed rather than queried,
    so the caller decides what "in this scan" means and P13 counts what it is
    given rather than inventing a population.
    """
    _require_precedence(precedence)

    fully_extracted: list[str] = []
    by_bucket: dict[str, list[str]] = {}
    for file_id, content_hash in indexed_files.items():
        mine = [run for run in runs_for_content(conn, content_hash)
                if run.file_id == file_id]
        if mine and all(run.completeness == COMPLETE for run in mine):
            fully_extracted.append(file_id)
            continue
        by_bucket.setdefault(bucket_for(mine, precedence=precedence),
                             []).append(file_id)

    entries: list[ProgressEntry] = [
        ProgressEntry(label=INDEXED, count=len(indexed_files),
                      state=STATE_COMPLETED, source=SOURCE_P3_R5, cause=None,
                      file_ids=tuple(sorted(indexed_files))),
        ProgressEntry(label=FULLY_EXTRACTED, count=len(fully_extracted),
                      state=STATE_COMPLETED, source=SOURCE_P4_RUNS, cause=None,
                      file_ids=tuple(sorted(fully_extracted))),
    ]

    # §8.6's "unreadable" is P5's mapping: `unreadable` OR `failed`, one entry.
    unreadable = sorted(file_id for state in UNREADABLE_STATES
                        for file_id in by_bucket.get(state, ()))
    if unreadable:
        entries.append(ProgressEntry(
            label=UNREADABLE, count=len(unreadable), state=STATE_BLOCKED,
            source=SOURCE_P4_RUNS, cause=cause_for(UNREADABLE),
            file_ids=tuple(unreadable)))

    # Every remaining bucket keeps its own label, so nothing is folded together.
    # `complete` is skipped because a file whose runs were not all complete is
    # already in another bucket by construction.
    for state in COMPLETENESS:
        if state in UNREADABLE_STATES or state == COMPLETE:
            continue
        members = sorted(by_bucket.get(state, ()))
        if not members:
            continue
        entries.append(ProgressEntry(
            label=state, count=len(members), state=BUCKET_STATE[state],
            source=SOURCE_P4_RUNS, cause=cause_for(state),
            file_ids=tuple(members)))

    untouched = sorted(by_bucket.get(NOT_YET_PROCESSED, ()))
    if untouched:
        entries.append(ProgressEntry(
            label=NOT_YET_PROCESSED, count=len(untouched),
            state=STATE_DEFERRED, source=SOURCE_P4_RUNS,
            cause=cause_for(NOT_YET_PROCESSED), file_ids=tuple(untouched)))

    awaiting = tuple(sorted(awaiting_model_review()))
    flagged = tuple(sorted(flagged_by_model_review()))
    if awaiting:
        entries.append(ProgressEntry(
            label=AWAITING_MODEL_REVIEW, count=len(awaiting),
            state=STATE_DEFERRED, source=SOURCE_P8,
            cause=cause_for(AWAITING_MODEL_REVIEW), file_ids=awaiting))
    if flagged:
        entries.append(ProgressEntry(
            label=FLAGGED_BY_MODEL_REVIEW, count=len(flagged),
            state=STATE_DEFERRED, source=SOURCE_P8, cause=None,
            file_ids=flagged))

    assert_every_file_accounted(indexed_files, entries)
    return ProgressLine(scan_ref=scan_ref, entries=tuple(entries),
                        rendered_at=rendered_at, plan_version=plan_version)
