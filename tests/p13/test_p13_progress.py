"""§8.6's progress line. `74` §6 B10.

    "1,842 files indexed; 1,611 fully extracted; 89 scanned PDFs deferred after
    the OCR limit; 34 files require model review; 18 files remain unreadable."
    "This makes the product's limitations legible and avoids the false impression
    that an unprocessed file was understood and found unimportant."

B10's named test is `test_completed_and_deferred_are_never_summed_into_one_number`
and its negative twin is `test_an_indexed_file_absent_from_every_entry_fails`. The
twin is a twin in the house sense: it goes red against an assembler that quietly
drops a file, which is the failure this whole record exists to prevent and the one
that is invisible in a passing suite -- the line still renders, the numbers still
add up among themselves, and a file has vanished from the user's picture of their
own corpus.

Three of the SPEC's Open questions are left open here, and each is left open by
being INJECTED rather than decided: OQ4 (how a file with runs in several states is
bucketed), OQ3 (which of two populations "34 files require model review" counts --
both are entries, neither is called 34), and G4's ceiling values (P13 names the
ceiling that fired and never a value of its own).
"""
from __future__ import annotations

import dataclasses
import hashlib

import pytest

from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_run
from evidence_shape.vocabulary import COMPLETENESS

from review_surface.progress import (
    NOT_YET_PROCESSED,
    assert_every_file_accounted,
    CompletenessPrecedenceRequired,
    FileAbsentFromEveryEntry,
    bucket_for,
    progress_line,
)
from review_surface.vocabulary import (
    SOURCE_P3_R5,
    SOURCE_P4_RUNS,
    SOURCE_P8,
    STATE_BLOCKED,
    STATE_COMPLETED,
    STATE_DEFERRED,
)

T0 = "2026-08-29T00:00:00Z"

#: A stated precedence over P4's NINE live completeness states, worst-first.
#: Injected, never a constant inside `review_surface` -- SPEC Open question 4 is
#: open and this arbitration is the caller's declared choice, not P13's.
PRECEDENCE = ("failed", "unreadable", "unsupported", "deferred", "capped",
              "dataless", "metadata_only", "partial", "complete")


def _hash(seed: str) -> str:
    """A 64-character hex digest. P4 refuses anything that is not one."""
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def _run(conn, file_id, content_hash, extractor, completeness) -> None:
    record_run(conn, ExtractionRun(
        run_id=f"run-{file_id}-{extractor}", file_id=file_id,
        content_hash=content_hash, extractor_name=extractor,
        extractor_version="1", source_type="text_document",
        analysis_tier="native", config={}, completeness=completeness,
        started_at=T0, observation_count=0, coverage=None, finished_at=T0,
        failure_reason=None))


def _line(conn, indexed, **overrides):
    values = dict(
        scan_ref="scan-1", plan_version="plan-1", rendered_at=T0,
        indexed_files=indexed, precedence=PRECEDENCE,
        awaiting_model_review=lambda: (),
        flagged_by_model_review=lambda: (),
        cause_for=lambda state: None)
    values.update(overrides)
    return progress_line(conn, **values)


def test_completed_and_deferred_are_never_summed_into_one_number(p13_conn):
    """`74` §6 B10's named test, and the sentence the record exists for.

    A complete file and a deferred one reach two entries in two states. Nothing
    in the line adds them together, and every entry declares which of §8.6's
    three states it is in -- so a reader can always tell finished work from work
    that has not happened.
    """
    _run(p13_conn, "f-1", _hash("a"), "pdf", "complete")
    _run(p13_conn, "f-2", _hash("b"), "ocr", "deferred")
    line = _line(p13_conn, {"f-1": _hash("a"), "f-2": _hash("b")})
    body = [entry for entry in line.entries if entry.label != "indexed"]
    states = {entry.state for entry in body}
    assert STATE_COMPLETED in states and STATE_DEFERRED in states
    for entry in line.entries:
        assert entry.state in (STATE_COMPLETED, STATE_DEFERRED, STATE_BLOCKED)
    # The two populations never share an entry, in either direction.
    for entry in body:
        assert not (set(entry.file_ids) >= {"f-1", "f-2"}), (
            f"{entry.label!r} merges a completed file with a deferred one")


def test_an_indexed_file_absent_from_every_entry_fails(p13_conn):
    """`74` §6 B10's negative twin, run against a deliberately lying population.

    An indexed file the assembler cannot place must stop the line rather than be
    dropped: §8.6's whole point is that omitting a file creates the false
    impression that an unprocessed file was understood and found unimportant.

    The twin is exercised by handing the assembler a file whose entries are then
    stripped, which is what a bug of this shape looks like from the outside, and
    by checking that the guard names the file rather than only the count.
    """
    for index, state in enumerate(COMPLETENESS):
        _run(p13_conn, f"f-{index}", _hash(str(index)), "pdf", state)
    indexed = {f"f-{index}": _hash(str(index))
               for index in range(len(COMPLETENESS))}
    # The honest assembly accounts for every one of the nine states.
    line = _line(p13_conn, indexed)
    accounted = {file_id for entry in line.entries if entry.label != "indexed"
                 for file_id in entry.file_ids}
    assert accounted == set(indexed), f"unaccounted: {set(indexed) - accounted}"
    # And a file with no run at all -- the case §8.6's sentence is really about
    # -- reaches an entry rather than vanishing.
    line = _line(p13_conn, indexed | {"f-nothing": _hash("z")})
    entry = next(e for e in line.entries
                 if e.label != "indexed" and "f-nothing" in e.file_ids)
    assert entry.label == NOT_YET_PROCESSED
    assert entry.state == STATE_DEFERRED


def test_the_guard_fires_when_an_entry_list_loses_a_file(p13_conn):
    """The other half of the twin: the guard must be able to RAISE.

    A guard proven only by "it found nothing on a good input" is worthless, so
    the check is a function that can be pointed at an entry list P13 did not
    build. It passes on a list that accounts for every file, refuses one that
    drops a single file, and names the file rather than only the count -- because
    a count tells the reader a file is missing and not which one.
    """
    entries = _line(p13_conn, {"f-1": _hash("a"), "f-2": _hash("b")}).entries
    assert_every_file_accounted({"f-1": _hash("a"), "f-2": _hash("b")}, entries)
    short = tuple(
        dataclasses.replace(
            entry,
            file_ids=tuple(f for f in entry.file_ids if f != "f-2"),
            count=len([f for f in entry.file_ids if f != "f-2"]))
        for entry in entries)
    with pytest.raises(FileAbsentFromEveryEntry) as caught:
        assert_every_file_accounted({"f-1": _hash("a"), "f-2": _hash("b")},
                                    short)
    assert "f-2" in str(caught.value)
    # `indexed` does not count as accounting for a file: it is the population,
    # not a bucket, so a line consisting of `indexed` alone accounts for nothing.
    only_indexed = tuple(e for e in entries if e.label == "indexed")
    with pytest.raises(FileAbsentFromEveryEntry):
        assert_every_file_accounted({"f-1": _hash("a")}, only_indexed)


def test_the_precedence_must_cover_every_live_completeness_state(p13_conn):
    """P4 publishes NINE states; the P13 SPEC's Contract-in lists eight and omits
    `dataless`. The live tuple governs, and a short precedence is refused."""
    assert set(PRECEDENCE) == set(COMPLETENESS)
    assert len(COMPLETENESS) == 9
    with pytest.raises(CompletenessPrecedenceRequired):
        _line(p13_conn, {"f-1": _hash("a")}, precedence=("complete", "failed"))


def test_bucket_for_takes_the_worst_state_by_the_stated_precedence():
    """SPEC Open question 4's own case: EXIF complete, OCR capped."""
    runs = [
        ExtractionRun(run_id="a", file_id="f", content_hash=_hash("a"),
                      extractor_name="exif", extractor_version="1",
                      source_type="image", analysis_tier="native", config={},
                      completeness="complete", started_at=T0,
                      observation_count=1, coverage=None, finished_at=T0,
                      failure_reason=None),
        ExtractionRun(run_id="b", file_id="f", content_hash=_hash("a"),
                      extractor_name="ocr", extractor_version="1",
                      source_type="image", analysis_tier="ocr", config={},
                      completeness="capped", started_at=T0,
                      observation_count=0, coverage=None, finished_at=T0,
                      failure_reason=None),
    ]
    assert bucket_for(runs, precedence=PRECEDENCE) == "capped"
    assert bucket_for((), precedence=PRECEDENCE) == NOT_YET_PROCESSED


def test_fully_extracted_requires_every_run_to_report_complete(p13_conn):
    """P13 SPEC:337-340 states this outright: any other run keeps the file out."""
    _run(p13_conn, "f-1", _hash("a"), "pdf", "complete")
    _run(p13_conn, "f-1", _hash("a"), "ocr", "complete")
    _run(p13_conn, "f-2", _hash("b"), "pdf", "complete")
    _run(p13_conn, "f-2", _hash("b"), "ocr", "capped")
    line = _line(p13_conn, {"f-1": _hash("a"), "f-2": _hash("b")})
    entries = {entry.label: entry for entry in line.entries}
    assert entries["fully extracted"].count == 1
    assert entries["fully extracted"].file_ids == ("f-1",)
    assert entries["fully extracted"].state == STATE_COMPLETED
    assert entries["fully extracted"].source == SOURCE_P4_RUNS


def test_indexed_comes_from_p3(p13_conn):
    line = _line(p13_conn, {"f-1": _hash("a"), "f-2": _hash("b")})
    indexed = next(e for e in line.entries if e.label == "indexed")
    assert indexed.count == 2
    assert indexed.source == SOURCE_P3_R5


def test_a_deferred_entry_names_the_ceiling_that_fired(p13_conn):
    """§8.6 requires the user to see what is running, what has been deferred, and
    WHY -- named, not implied. The ceiling values are P1's (G4)."""
    _run(p13_conn, "f-1", _hash("a"), "ocr", "deferred")
    line = _line(p13_conn, {"f-1": _hash("a")},
                 cause_for=lambda state: ("ocr.max_pages_per_file"
                                          if state == "deferred" else None))
    deferred = next(e for e in line.entries if e.label == "deferred")
    assert deferred.state == STATE_DEFERRED
    assert deferred.cause == "ocr.max_pages_per_file"


def test_unreadable_takes_p5_s_mapping_of_unreadable_or_failed(p13_conn):
    """P13 SPEC:341-345: taking P5's mapping rather than `unreadable` alone is
    what stops a `failed` run from appearing in no entry at all."""
    _run(p13_conn, "f-1", _hash("a"), "pdf", "unreadable")
    _run(p13_conn, "f-2", _hash("b"), "pdf", "failed")
    line = _line(p13_conn, {"f-1": _hash("a"), "f-2": _hash("b")})
    unreadable = next(e for e in line.entries if e.label == "unreadable")
    assert unreadable.count == 2
    assert set(unreadable.file_ids) == {"f-1", "f-2"}
    assert unreadable.state == STATE_BLOCKED


def test_a_dataless_file_gets_its_own_entry_and_is_not_folded_in(p13_conn):
    """The CONFLICT the PLAN records: `dataless` is live in P4 and absent from
    the SPEC's eight. Whether it belongs under `unreadable`, under `complete` or
    on its own line is the owner's, so it gets its own labelled entry and the
    choice stays visible rather than folded in."""
    _run(p13_conn, "f-1", _hash("a"), "pdf", "dataless")
    line = _line(p13_conn, {"f-1": _hash("a")})
    entry = next(e for e in line.entries if e.label == "dataless")
    assert entry.count == 1


def test_model_review_is_two_entries_and_not_one_number(p13_conn):
    """SPEC Open question 3 is OPEN: §8.6's phrase admits two readings and they
    are different populations. Neither is called "34"."""
    _run(p13_conn, "f-1", _hash("a"), "pdf", "complete")
    _run(p13_conn, "f-2", _hash("b"), "pdf", "complete")
    line = _line(p13_conn, {"f-1": _hash("a"), "f-2": _hash("b")},
                 awaiting_model_review=lambda: ("f-1",),
                 flagged_by_model_review=lambda: ("f-2",))
    labels = {e.label: e for e in line.entries}
    assert labels["awaiting model review"].count == 1
    assert labels["flagged by model review"].count == 1
    assert labels["awaiting model review"].source == SOURCE_P8
    assert labels["flagged by model review"].source == SOURCE_P8


def test_the_line_reproduces_section_8_6_s_shape_from_real_records(p13_conn):
    """Done-means 18, assembled end to end from records rather than from counts."""
    for n in range(6):
        _run(p13_conn, f"c-{n}", _hash(f"c{n}"), "pdf", "complete")
    for n in range(2):
        _run(p13_conn, f"d-{n}", _hash(f"d{n}"), "ocr", "deferred")
    _run(p13_conn, "u-0", _hash("u0"), "pdf", "unreadable")
    indexed = ({f"c-{n}": _hash(f"c{n}") for n in range(6)}
               | {f"d-{n}": _hash(f"d{n}") for n in range(2)}
               | {"u-0": _hash("u0")})
    line = _line(
        p13_conn, indexed, awaiting_model_review=lambda: ("c-0",),
        cause_for=lambda s: ("ocr.max_pages_per_file" if s == "deferred"
                             else None))
    labels = {e.label: e.count for e in line.entries}
    assert labels["indexed"] == 9
    assert labels["fully extracted"] == 6
    assert labels["deferred"] == 2
    assert labels["unreadable"] == 1
    assert labels["awaiting model review"] == 1
    assert line.total_accounted() == 9
