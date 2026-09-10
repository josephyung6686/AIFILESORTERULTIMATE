"""`104` §18.2 gap 22 -- §8.6's two per-scan ceilings have an enforcement point.

The design sentences.

`00`:243-248 declares the ceilings, among them *"Maximum OCR time per scan"* and
*"Maximum image-analysis operations per scan"*.

`00`:257: *"A model prompt that exceeds its token budget should not truncate
silently in a way that removes the decisive evidence."*

`00`:258: *"If the budget is exhausted, the product should retain extracted
evidence, mark the deferred stage, and leave the file or group in review rather
than guessing. Cost exhaustion must never turn into lower-quality automatic
classification."*

`00`:259: *"The user interface should show the difference between completed work
and deferred work ... This makes the product's limitations legible and avoids the
false impression that an unprocessed file was understood and found unimportant."*

What was measured before this patch. `cli.py`'s `_bootstrap` said it in a comment
beside the two ceilings it DOES set: the other two *"have no enforcement point
anywhere in `src/`: nothing accumulates a per-scan OCR clock and nothing counts
image operations."* `extractors/budgets.py` -- `p5_ceilings`, `deferred_result`,
`extraction_counts` -- had no callers at all, and `cli.py`'s deferred-cause branch
said *"This build records no deferral."* So the rung §8.6 exists to provide could
not fire, and a scan that ran out of budget had no way to say so.

These tests drive a real `run_p1_p7` over a real corpus with a real ceiling
stored, and read the answer out of the database.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from database_agent.budget import set_ceiling
from database_agent.db import create_schema
from eval_harness.store import create_eval_schema
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import RunWriter
from extraction_pool import ExtractionContext, InlinePool
from extractors.archive import ArchiveManifest
from extractors.budgets import extraction_counts, p5_ceilings
from extractors.dispatch import Readers
from extractors.docx import DocxDocument
from extractors.image import ImageRecord
from extractors.long_tail import LongTailFile
from extractors.pdf import PdfDocument, PdfPage
from extractors.reading import Region
from extractors.safety import SafetyPolicy
from extractors.schema import create_extraction_schema
from extractors.stage_output import extraction_stage_output
from extractors.structured_text import TextDocument
from facts.schema import create_facts_schema
from orchestrator import run_p1_p7
from privacy.classification_store import ClassificationStore
from privacy.schema import create_privacy_schema
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection


@pytest.fixture()
def database(conn):
    create_schema(conn)
    create_scan_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    create_facts_schema(conn)
    create_privacy_schema(conn)
    create_eval_schema(conn)
    return conn


def _policy() -> SafetyPolicy:
    return SafetyPolicy(is_protected_container=lambda path: False,
                        is_dataless=lambda path: False)


def _readers() -> Readers:
    """A reader for every family, so the router's choice is what decides.

    `read_image` returns a record §2.6 can read a signal out of, which is what
    makes a NON-deferred image run distinguishable from a deferred one: the first
    carries observations and the second, by P4's
    `ZERO_OBSERVATION_COMPLETENESS`, carries none.
    """
    return Readers(
        read_pdf=lambda path: PdfDocument(
            metadata={},
            pages=(PdfPage(number=1, text="body",
                           regions=(Region(zone="body", start=0, end=4),)),)),
        read_docx=lambda path: DocxDocument(core_properties={}),
        read_text_document=lambda path: TextDocument(text="text"),
        read_long_tail=lambda path, transcribe=False: LongTailFile(),
        read_manifest=lambda path: ArchiveManifest(archive_type="zip"),
        read_image=lambda path: ImageRecord(image_format="PNG",
                                            dimensions="4032x3024",
                                            width=4032, height=3024),
        find_structured_strings=lambda text: (),
        recognize_markers=lambda names: (),
        dimension_signal=lambda width, height: "sensor-shaped dimensions",
        filename_pattern=lambda name: None,
        ocr_engine=None,
    )


def _run(conn, root: Path, *, mime="image/png", detected="png"):
    readers = _readers()
    context = ExtractionContext(policy=_policy(), readers=readers,
                                transcription_authorized=lambda: False)
    selection = record_selection(conn, sources=[root], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return run_p1_p7(
        conn, selection, source=FilesystemCorpusSource(),
        mime_type_for=lambda path: mime, scan_state="scanned",
        budget_exhausted=lambda: False, detect_format=lambda path: detected,
        policy=_policy(), readers=readers, sink=RunWriter(conn, author="P5"),
        now=lambda: datetime.now(timezone.utc).isoformat(), context_window=40,
        transcription_authorized=lambda: False, corpus_form="snapshot",
        policy_settings={}, file_entry_body=lambda row: {"payload_ref": "blob"},
        resolve_native=lambda db, file_id, content_hash: None,
        targeted_ocr_needed=lambda file_id, content_hash: False,
        resolve_with_ocr=lambda db, file_id, content_hash: None,
        classify=lambda db, file_id, content_hash: None,
        classification_store=ClassificationStore(conn),
        p7_component_version="0.1.0", pool=InlinePool(context))


def _images(tmp_path: Path, count: int) -> Path:
    root = tmp_path / "corpus"
    root.mkdir()
    for index in range(count):
        (root / f"photo-{index}.png").write_bytes(
            b"\x89PNG\r\n\x1a\n" + str(index).encode() * 8)
    return root


def _runs(conn, *, tier=None):
    sql = ("SELECT file_id, extractor_name, source_type, analysis_tier, "
           "completeness, coverage, observation_count FROM extraction_runs")
    if tier is not None:
        sql += f" WHERE analysis_tier = '{tier}'"
    return [dict(row) for row in conn.execute(sql + " ORDER BY rowid")]


# --------------------------------------------------------------------------- #
# The ceiling has an enforcement point at all
# --------------------------------------------------------------------------- #

def test_a_scan_with_no_ceiling_stored_reads_every_image(database, tmp_path):
    """The baseline, pinned FIRST so the test below cannot pass vacuously.

    `00`:243 calls these "configurable ceilings" and `_bootstrap` deliberately
    stores no value for either per-scan one, so an ordinary run of this product
    is unbounded and every image is analysed. `get_ceiling` answering `None`
    means no ceiling -- not a ceiling of zero.
    """
    assert p5_ceilings(database)["image.max_analysis_ops_per_scan"] is None

    _run(database, _images(tmp_path, 3))

    native = _runs(database, tier="native")
    assert len(native) == 3
    assert {run["completeness"] for run in native} == {"complete"}


def test_a_file_past_the_image_ceiling_is_deferred_and_not_truncated(
        database, tmp_path):
    """The item itself, measured on a real scan.

    `00`:248's "Maximum image-analysis operations per scan" is stored as 2 and
    three images are scanned. Measured: the first two are analysed and the third
    carries `completeness = deferred` -- P4's own word for a run a budget stopped
    before it started -- with `0 of 1 images` of coverage and zero observations.

    It is DEFERRED and not `capped`: `capped` means an extractor read something
    and stopped, and this one never ran. It is not `unreadable` either, which
    would say the product tried and failed. `00`:259's whole point is that a
    person can tell those apart.
    """
    set_ceiling(database, "image.max_analysis_ops_per_scan", 2)

    _run(database, _images(tmp_path, 3))

    native = _runs(database, tier="native")
    assert [run["completeness"] for run in native] == [
        "complete", "complete", "deferred"]

    deferred = native[-1]
    assert deferred["observation_count"] == 0
    assert json.loads(deferred["coverage"]) == {
        "units": "images", "processed": 0, "total": 1}
    assert deferred["source_type"] == "image"


def test_nothing_read_below_the_ceiling_is_deleted(database, tmp_path):
    """`00`:258: "the product should retain extracted evidence".

    Two things are measured. The two images that WERE analysed keep every
    observation they produced -- a ceiling is not a reason to throw away work
    already done. And the deferred file keeps its own filesystem record, so it
    is still indexed, still named, and still citable: a file past a ceiling
    disappears from no list.
    """
    set_ceiling(database, "image.max_analysis_ops_per_scan", 2)

    _run(database, _images(tmp_path, 3))

    analysed = [run for run in _runs(database, tier="native")
                if run["completeness"] == "complete"]
    assert len(analysed) == 2
    assert all(run["observation_count"] > 0 for run in analysed), (
        "a ceiling reached on a later file removed evidence from an earlier one")

    deferred_file = [run for run in _runs(database, tier="native")
                     if run["completeness"] == "deferred"][0]["file_id"]
    filesystem = [run for run in _runs(database, tier="filesystem")
                  if run["file_id"] == deferred_file]
    assert len(filesystem) == 1 and filesystem[0]["observation_count"] > 0, (
        "the deferred file lost its filesystem record, so it is indexed nowhere")


# --------------------------------------------------------------------------- #
# The deferral rung
# --------------------------------------------------------------------------- #

def test_the_deferred_file_carries_section_8_6_s_rung(database, tmp_path):
    """`104` §18.2 gap 22 asks for "the deferral rung written (the design's rung)".

    The design's rung is P2's: §8.5's `extraction` stage output, whose `outcome`
    is `deferred` and whose `budget_state` is `ceiling_reached`.
    `eval_harness.stage_output.record_stage_output` enforces the pairing itself
    -- *"a ceiling-reached stage is 'deferred', never 'abstained': §8.6 forbids
    cost exhaustion becoming a judgement about evidence"* -- and P5's
    `extraction_stage_output` is the producer.

    Measured: the run this scan wrote for the file past the ceiling produces
    exactly that envelope, and its dimension value measures NOTHING, which is
    P2's row for "the stage ran and measured nothing" rather than an absent row
    that would read as `not_run`.
    """
    set_ceiling(database, "image.max_analysis_ops_per_scan", 2)

    _run(database, _images(tmp_path, 3))

    deferred = [run for run in _runs(database, tier="native")
                if run["completeness"] == "deferred"][0]
    envelope = extraction_stage_output(run={**deferred,
                                            "coverage": json.loads(deferred["coverage"]),
                                            "extractor_version": "0.1.0",
                                            "content_hash": "c" * 64})

    assert envelope["stage_id"] == "extraction"
    assert envelope["outcome"] == "deferred"
    assert envelope["budget_state"] == "ceiling_reached"
    assert envelope["values"][0].outcome == "deferred"
    assert envelope["values"][0].value is None


# --------------------------------------------------------------------------- #
# The coverage sentences count it
# --------------------------------------------------------------------------- #

def test_the_coverage_sentence_counts_the_deferred_file(database, tmp_path):
    """`00`:259's own line: "89 scanned PDFs deferred after the OCR limit".

    `extractors.budgets.extraction_counts` is §8.6's sentence as four queries and
    had no caller before this patch because there was no deferral to count.
    Measured over the records this scan actually wrote: three files indexed, two
    fully extracted, one deferred, none unreadable.

    "Fully extracted" is the number that has to move. A deferred file counted
    among the fully extracted would be exactly `00`:259's "false impression that
    an unprocessed file was understood and found unimportant".
    """
    set_ceiling(database, "image.max_analysis_ops_per_scan", 2)

    _run(database, _images(tmp_path, 3))

    counts = extraction_counts(_runs(database), files_scanned=3)
    assert counts["indexed"] == 3
    assert counts["fully_extracted"] == 2
    assert counts["deferred"] == 1
    assert counts["unreadable"] == 0


def test_a_deferred_file_is_not_reported_as_unreadable(database, tmp_path):
    """`00`:259's two buckets are different sentences and must stay different.

    *"89 scanned PDFs deferred after the OCR limit ... 18 files remain
    unreadable."* One says a budget ran out; the other says the product tried and
    could not. A file past a per-scan ceiling has NO observations of its own --
    P4 lists `deferred` in `ZERO_OBSERVATION_COMPLETENESS` -- so the roster
    reconciliation's "was anything read out of it" test finds nothing for it and
    would have called it unreadable.

    That is a false sentence in front of a person, and the one `00`:259 names:
    it invites them to conclude their photo is corrupt when it was never opened.
    Measured through `cli._budget_deferred`, which is the predicate the
    reconciliation asks before it reaches for `unreadable`.
    """
    from cli import _budget_deferred

    set_ceiling(database, "image.max_analysis_ops_per_scan", 2)
    _run(database, _images(tmp_path, 3))

    native = _runs(database, tier="native")
    deferred_file = [run for run in native
                     if run["completeness"] == "deferred"][0]["file_id"]
    analysed_file = [run for run in native
                     if run["completeness"] == "complete"][0]["file_id"]

    hashes = {row["file_id"]: row["content_hash"] for row in database.execute(
        "SELECT file_id, content_hash FROM files")}

    assert _budget_deferred(database, deferred_file, hashes[deferred_file])
    assert not _budget_deferred(database, analysed_file, hashes[analysed_file])


def test_a_ceiling_costs_a_file_this_scan_and_not_the_next_one(
        database, tmp_path):
    """A deferral is not a permanent verdict, and this is the trap it avoids.

    `orchestrator._already_extracted` asks whether this content already has the
    run the router says it is owed, and a file that has one is `reused` -- never
    read again. A `deferred` run counted as that run would make a single scan's
    budget permanent: the file would be skipped on every later scan, including
    the one with the ceiling raised, and nobody would ever be told why their
    images were never read.

    Measured: the same corpus, scanned again with the ceiling lifted, reads the
    file the first scan deferred.
    """
    set_ceiling(database, "image.max_analysis_ops_per_scan", 2)
    root = _images(tmp_path, 3)
    _run(database, root)

    deferred_file = [run for run in _runs(database, tier="native")
                     if run["completeness"] == "deferred"][0]["file_id"]

    set_ceiling(database, "image.max_analysis_ops_per_scan", 99)
    _run(database, root)

    later = [run for run in _runs(database, tier="native")
             if run["file_id"] == deferred_file
             and run["completeness"] == "complete"]
    assert later, (
        "the file the first scan deferred was never re-read; a budget became a "
        "permanent verdict about a file nobody ever looked at")

    # AND THE OLD DEFERRAL MUST STOP SPEAKING FOR THE FILE. P4 supersedes runs and
    # never deletes them, so the first scan's `deferred` row is still in
    # `runs_for_content` -- and `WORST_FIRST` ranks `deferred` above `complete`,
    # so the coverage line would go on calling a fully-read file deferred for the
    # rest of the database's life. That is the same false sentence in the other
    # direction: `00`:259's buckets have to describe what is true NOW.
    from cli import _budget_deferred

    content_hash = database.execute(
        "SELECT content_hash FROM files WHERE file_id = ?",
        (deferred_file,)).fetchone()["content_hash"]
    assert not _budget_deferred(database, deferred_file, content_hash), (
        "a deferral the next scan answered still reports the file as deferred")
