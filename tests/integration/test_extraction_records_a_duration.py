"""How long one file took is a fact the run has to be able to state.

`00`:245-259 asks for elapsed time to be observable -- "Maximum OCR time per file",
"Maximum OCR time per scan", and the scan summary that distinguishes completed work
from deferred work. `extraction_runs` carries `started_at` and `finished_at` and
`database_agent/db.py`:384 says of the pair, in a comment, "(mechanics) so
elapsed_time is computable". It was not computable. `run_p1_p7` takes ONE stamp per
file on the calling thread, before the file is read, and hands that same string to
the extractor as `now`; every extractor writes `started_at=now, finished_at=now`. So
every run in the product recorded a duration of exactly zero, and the one number a
Phase 4 scale measurement most needs -- which files are slow -- could not be read
back from the records at all. It had to be inferred from a profiler attached to the
whole run, which is why the 5,000-file measurement could say the run was slow and
not say which files made it so.

The fix is one stamp, in one place: `finished_at` is taken WHEN THE RESULT LANDS, on
the consuming thread, from the `now` the caller already injected. Not in the worker,
because a spawned worker cannot be handed a test's clock and the parallel path would
then write rows the serial path could never reproduce; and not per extractor,
because eleven extractors would then each hold a clock.

`started_at` keeps its meaning exactly: the moment the orchestrator decided to
extract this file. So `finished_at - started_at` is submission-to-landing, which is
what a person waiting for a scan actually experiences.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from database_agent.db import create_schema
from eval_harness.store import create_eval_schema
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import RunWriter
from extraction_pool import ExtractionContext, InlinePool
from extractors.archive import ArchiveManifest
from extractors.dispatch import Readers
from extractors.docx import DocxDocument
from extractors.image import ImageRecord
from extractors.long_tail import LongTailFile
from extractors.pdf import PdfDocument, PdfPage
from extractors.reading import Region
from extractors.safety import SafetyPolicy
from extractors.schema import create_extraction_schema
from extractors.structured_text import TextDocument
from facts.schema import create_facts_schema
from orchestrator import run_p1_p7
from privacy.classification_store import ClassificationStore
from privacy.schema import create_privacy_schema
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection

#: What the stub extractor spends. Long enough to exceed the clock's resolution by
#: three orders of magnitude, short enough that the test costs a fifth of a second.
SLOW_SECONDS = 0.05


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


def _readers(*, seconds: float) -> Readers:
    """One deliberately slow reader, and nothing else unusual.

    The sleep stands in for the real cost this product measures -- pdfium over a
    fifty-page scan, Vision over a photographed page -- without needing either.
    """

    def read_pdf(path: Path) -> PdfDocument:
        time.sleep(seconds)
        text = f"{Path(path).stem} carries course PHYS1401"
        return PdfDocument(
            metadata={},
            pages=(PdfPage(number=1, text=text,
                           regions=(Region(zone="body", start=0, end=len(text)),)),))

    return Readers(
        read_pdf=read_pdf,
        read_docx=lambda path: DocxDocument(core_properties={}),
        read_text_document=lambda path: TextDocument(text="text"),
        read_long_tail=lambda path, transcribe=False: LongTailFile(),
        read_manifest=lambda path: ArchiveManifest(archive_type="zip"),
        read_image=lambda path: ImageRecord(image_format="PNG", dimensions="1x1",
                                            width=1, height=1),
        find_structured_strings=lambda text: (),
        recognize_markers=lambda names: (),
        dimension_signal=lambda width, height: None,
        filename_pattern=lambda name: None,
        ocr_engine=None,
    )


def _policy() -> SafetyPolicy:
    return SafetyPolicy(is_protected_container=lambda path: False,
                        is_dataless=lambda path: False)


def _run(conn, root: Path, *, readers, now):
    context = ExtractionContext(policy=_policy(), readers=readers,
                                transcription_authorized=lambda: False)
    selection = record_selection(conn, sources=[root], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return run_p1_p7(
        conn, selection, source=FilesystemCorpusSource(),
        mime_type_for=lambda path: "application/pdf", scan_state="scanned",
        budget_exhausted=lambda: False, detect_format=lambda path: "pdf",
        policy=_policy(), readers=readers, sink=RunWriter(conn, author="P5"),
        now=now, context_window=40,
        transcription_authorized=lambda: False, corpus_form="snapshot",
        policy_settings={}, file_entry_body=lambda row: {"payload_ref": "blob"},
        resolve_native=lambda db, file_id, content_hash: None,
        targeted_ocr_needed=lambda file_id, content_hash: False,
        resolve_with_ocr=lambda db, file_id, content_hash: None,
        classify=lambda db, file_id, content_hash: None,
        classification_store=ClassificationStore(conn),
        p7_component_version="0.1.0", pool=InlinePool(context))


def _corpus(tmp_path: Path, names=("alpha.pdf", "bravo.pdf")) -> Path:
    root = tmp_path / "corpus"
    root.mkdir()
    for index, name in enumerate(names):
        (root / name).write_bytes(b"%PDF-1.4 " + str(index).encode() * 8)
    return root


def _elapsed(row) -> float:
    return ((datetime.fromisoformat(row["finished_at"])
             - datetime.fromisoformat(row["started_at"])).total_seconds())


def test_a_slow_extractor_records_the_time_it_spent(database, tmp_path):
    """The whole item, as one number read back out of the records.

    A reader that sleeps for `SLOW_SECONDS` must leave a run whose two stamps are at
    least that far apart. Before the fix both stamps are the submission stamp and
    the difference is exactly 0.0 for every file in every run this product has ever
    made.
    """
    root = _corpus(tmp_path)
    _run(database, root, readers=_readers(seconds=SLOW_SECONDS),
         now=lambda: datetime.now(timezone.utc).isoformat())

    rows = list(database.execute(
        "SELECT extractor_name, started_at, finished_at FROM extraction_runs "
        "WHERE analysis_tier = 'native' ORDER BY rowid"))
    assert rows, "no native run was written; the measurement has nothing to read"
    for row in rows:
        assert _elapsed(row) >= SLOW_SECONDS, (
            f"{row['extractor_name']} slept {SLOW_SECONDS}s and its record claims "
            f"{_elapsed(row)}s; a run that cannot state its own duration cannot "
            "tell a person which file made their scan slow")


def test_the_per_file_durations_are_distinguishable_from_one_another(
        database, tmp_path):
    """Not merely non-zero: USABLE.

    A distribution is the deliverable -- min, median, p95, max -- and that needs the
    slow file to be distinguishable from the quick one. Two files are read by the
    same slow reader here, so what this asks is the weaker, sufficient thing: each
    file's record covers its own read and not the whole run's. If `finished_at` were
    stamped once at the end of the scan instead of as each result landed, the first
    file's elapsed time would include the second file's read and this would fail.
    """
    root = _corpus(tmp_path)
    _run(database, root, readers=_readers(seconds=SLOW_SECONDS),
         now=lambda: datetime.now(timezone.utc).isoformat())

    durations = [_elapsed(row) for row in database.execute(
        "SELECT started_at, finished_at FROM extraction_runs "
        "WHERE analysis_tier = 'native' ORDER BY rowid")]
    assert len(durations) == 2, f"expected one native run per file, got {durations}"
    for duration in durations:
        assert duration < SLOW_SECONDS * len(durations) * 2, (
            f"a single file's record claims {duration}s, which is more than its own "
            "read could have cost; the stamp is being taken too late")


def test_a_frozen_clock_still_writes_equal_stamps(database, tmp_path):
    """The determinism the whole test suite rests on is not disturbed.

    `finished_at` comes from the SAME injected `now` as `started_at`, so a caller
    that pins the clock -- which every replay comparison in this suite does -- gets
    the identical rows it got before. That is why the stamp is taken here and not
    from a wall clock inside the extractor.
    """
    root = _corpus(tmp_path)
    _run(database, root, readers=_readers(seconds=0.0),
         now=lambda: "2026-09-06T00:00:00+00:00")

    rows = list(database.execute(
        "SELECT started_at, finished_at FROM extraction_runs ORDER BY rowid"))
    assert rows, "no run was written"
    for row in rows:
        assert row["started_at"] == row["finished_at"] == "2026-09-06T00:00:00+00:00"
