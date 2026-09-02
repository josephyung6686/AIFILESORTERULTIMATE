"""§8.6's progress line, rendered. "18 files remain unreadable" had no printer.

    "The user interface should show the difference between completed work and
    deferred work." ... "This makes the product's limitations legible and avoids
    the false impression that an unprocessed file was understood and found
    unimportant."

`review_surface.progress` assembles that line from P4's own runs and refuses to
sum two states together. It was reachable from nothing: `src/cli.py` prints
folders, placements and holds, and says NOTHING about a file it could not read.
A person running this over a real disk was told about the files it understood and
told nothing about the ones it did not open.

These tests drive the RENDERER, which is the half that decides what the person
actually reads. Two properties are load-bearing and both are asserted against a
sabotage:

* **A deferral with no named cause says so.** §8.6 requires the cause NAMED, not
  implied. Nothing in `src/` records which ceiling fired -- `database_agent.budget`
  publishes seventeen keys and stores no record of one being hit -- so `cause_for`
  answers `None`, and a renderer that printed the count alone would leave the
  person reading "12 deferred" with no way to learn why. The gap is printed as a
  gap.
* **No two entries are summed.** A renderer is exactly where the single number
  §8.6 forbids would reappear, because the entries are right there in a list.
"""
from __future__ import annotations

import hashlib

from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_run
from evidence_shape.vocabulary import COMPLETENESS

from review_run.progress import progress_lines

RENDERED_AT = "2026-09-02T00:00:00Z"
VERSION = "plan-1"
SCAN = "scan-1"

#: Worst first, so a file with several runs is reported by its worst one. Spelled
#: in the TEST because it is the caller's stated choice under Open question 4,
#: exactly as it will be spelled in `src/cli.py`; the seam supplies none.
WORST_FIRST = ("failed", "unreadable", "unsupported", "dataless",
               "metadata_only", "deferred", "capped", "partial", "complete")
assert set(WORST_FIRST) == set(COMPLETENESS)


def _run(conn, file_id: str, content_hash: str, completeness: str) -> None:
    """One of P4's own runs, through P4's own writer. A raw INSERT would test the
    table rather than the read, and would drift the moment P4 adds a column."""
    record_run(conn, ExtractionRun(
        run_id=f"run-{file_id}", file_id=file_id, content_hash=content_hash,
        extractor_name="text", extractor_version="1",
        source_type="text_document", analysis_tier="native", config={},
        completeness=completeness, started_at=RENDERED_AT,
        observation_count=0, coverage=None, finished_at=RENDERED_AT,
        failure_reason=None))


def _hash(seed: str) -> str:
    """A 64-character hex digest. P4 refuses anything that is not one."""
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def _lines(conn, indexed, *, cause_for=lambda label: None):
    return progress_lines(
        conn, scan_ref=SCAN, plan_version=VERSION, rendered_at=RENDERED_AT,
        indexed_files=indexed, precedence=WORST_FIRST,
        awaiting_model_review=tuple, flagged_by_model_review=tuple,
        cause_for=cause_for)


HASH = _hash("a")
HASH2 = _hash("b")


def test_completed_work_and_blocked_work_are_two_lines_and_never_one_number(
        p13_conn):
    """§8.6's whole point, as the shape of the output rather than as a comment.

    Three files: one read, one unreadable, one the product never reached. The
    assertion is the whole tuple of lines, because asserting that "unreadable"
    appears somewhere would hold just as well for a renderer that also printed a
    single blended total beside it -- and the blended total is the thing §8.6
    names as the failure.
    """
    _run(p13_conn, "f-1", HASH, "complete")
    _run(p13_conn, "f-2", HASH2, "unreadable")
    indexed = {"f-1": HASH, "f-2": HASH2, "f-3": _hash("c")}

    assert _lines(p13_conn, indexed) == (
        "",
        "What this run could read: 3 files indexed.",
        "  1 fully extracted  (completed)",
        "  1 unreadable  (blocked) -- no ceiling is recorded as the cause, so "
        "this build cannot say which limit stopped it",
        "  1 not yet processed  (deferred) -- no ceiling is recorded as the "
        "cause, so this build cannot say which limit stopped it",
        "  A file counted here was not necessarily understood. Nothing above "
        "is added together: deferred work and completed work are different "
        "answers.",
    )


def test_a_named_cause_replaces_the_missing_cause_sentence(p13_conn):
    """When something CAN say why, the gap sentence goes away and the cause prints.

    The twin of the line above. A renderer that always printed the gap sentence
    would pass every assertion in the previous test and would tell a person with
    a real ceiling record that the product cannot say why -- which would be a
    lie the moment anything starts recording one.
    """
    _run(p13_conn, "f-2", HASH2, "deferred")
    lines = _lines(p13_conn, {"f-2": HASH2},
                   cause_for=lambda label: "ocr.max_time_per_file")
    assert lines == (
        "",
        "What this run could read: 1 file indexed.",
        "  0 fully extracted  (completed)",
        "  1 deferred  (deferred) -- ocr.max_time_per_file",
        "  A file counted here was not necessarily understood. Nothing above "
        "is added together: deferred work and completed work are different "
        "answers.",
    )


def test_a_renderer_that_sums_the_entries_prints_a_number_the_design_forbids(
        p13_conn):
    """The sabotage: one blended "processed" figure over the same entries.

    §8.6's sentence is five counts, and the reason it is five is that a single
    figure "avoids the false impression that an unprocessed file was understood
    and found unimportant". The sabotage is one line of arithmetic over the exact
    list the real renderer walks -- which is what makes it the honest sabotage
    rather than an invented one -- and the assertion is that no line the real
    renderer produced carries its answer.
    """
    _run(p13_conn, "f-1", HASH, "complete")
    _run(p13_conn, "f-2", HASH2, "unreadable")
    indexed = {"f-1": HASH, "f-2": HASH2}
    lines = _lines(p13_conn, indexed)

    blended = f"{len(indexed)} files processed"
    assert blended == "2 files processed"
    assert not any(blended in line for line in lines)


def test_an_indexed_file_that_reaches_no_entry_is_a_failure_and_not_a_short_line(
        p13_conn):
    """P13's own refusal survives the seam rather than being caught and smoothed.

    A renderer that swallowed `FileAbsentFromEveryEntry` would print a shorter,
    perfectly readable line for a run that had lost somebody's file. The
    sabotage here is a precedence missing one of P4's states, which is the
    likeliest way a caller produces the condition; `progress_line` refuses it and
    the seam does not intercept.
    """
    import pytest

    from review_surface.progress import CompletenessPrecedenceRequired

    _run(p13_conn, "f-1", HASH, "complete")
    with pytest.raises(CompletenessPrecedenceRequired):
        progress_lines(
            p13_conn, scan_ref=SCAN, plan_version=VERSION,
            rendered_at=RENDERED_AT, indexed_files={"f-1": HASH},
            precedence=("complete",), awaiting_model_review=tuple,
            flagged_by_model_review=tuple, cause_for=lambda label: None)
