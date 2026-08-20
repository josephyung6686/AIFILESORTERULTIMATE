# tests/wave2/test_wave2_orchestrator.py
"""The Wave-2 caller: P3 scan -> P5 route/extract -> P4 record -> P1 status -> P2 bundle.

18-wave2-orchestrator.md: P1, P2 and P3 are shipped, P4 and P5 are green, and
"nothing calls them in sequence". `scan()` returns a `scan_run_id` and stops. Every
test here is about the JOIN -- the thing 1,205 unit tests were comprehensive about
shape for and silent about.
"""
from pathlib import Path

import pytest

from database_agent.files_table import get_file
from orchestrator import Wave2, run_wave2
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.selection import record_selection

NEVER = lambda: False

# Fixtures live in this module, NOT in a tests/wave2/conftest.py.
#
# pytest's prepend import mode keys a rootless module on its BASENAME, so a second
# `conftest.py` claims `sys.modules["conftest"]` and whichever directory is imported
# first wins for the whole session. tests/p5/ does `from conftest import
# RecordingSink`; a tests/wave2/conftest.py made that import resolve HERE and broke
# three tests in a package this one does not touch -- and only in a full run, which is
# what makes it worth a comment. The same collision cost this project a whole-suite
# outage once already, in tests/eval/.
FIXED_CLOCK = "2026-08-21T12:00:00+00:00"


@pytest.fixture()
def db(conn):
    from database_agent.db import create_schema
    from eval_harness.store import create_eval_schema
    from evidence_shape.schema import create_evidence_schema
    from scan_agent.schema import create_scan_schema
    create_schema(conn)
    create_scan_schema(conn)
    create_evidence_schema(conn)
    create_eval_schema(conn)
    return conn


@pytest.fixture()
def corpus(tmp_path: Path) -> Path:
    """A real corpus on disk. Nothing here synthesizes a record: the point of these
    tests is the join, and every defect the 2026-08-21 stress test found passed its
    unit tests and was visible only end to end."""
    root = tmp_path / "Documents"
    root.mkdir()
    (root / "syllabus.pdf").write_bytes(b"%PDF-1.4 BUSIB 4300")
    (root / "notes.md").write_bytes(b"# BUSIB 4300\nlecture notes")
    return root


def mime_for(path: Path) -> str | None:
    return {".pdf": "application/pdf", ".md": "text/markdown"}.get(path.suffix)


def readers(**over):
    from extractors.dispatch import Readers
    from extractors.pdf import PdfDocument, PdfPage
    from extractors.docx import DocxDocument
    from extractors.reading import Region
    from extractors.archive import ArchiveManifest
    from extractors.image import ImageRecord
    from extractors.structured_text import TextDocument
    from extractors.long_tail import LongTailFile

    page = "BUSIB 4300 Course Information"
    base = dict(
        read_pdf=lambda p: PdfDocument(
            metadata={"Title": "BUSIB 4300 Syllabus"}, iso_dates={},
            pages=(PdfPage(number=1, text=page,
                           regions=(Region(zone="heading", start=0, end=29,
                                           ordinal=1, label="Course Information"),)),)),
        read_docx=lambda p: DocxDocument(core_properties={}),
        read_text_document=lambda p: TextDocument(text="BUSIB 4300 lecture notes"),
        read_long_tail=lambda p, transcribe=False: LongTailFile(),
        read_manifest=lambda p: ArchiveManifest(archive_type="zip"),
        read_image=lambda p: ImageRecord(image_format="PNG", dimensions="2880x1800",
                                         width=2880, height=1800),
        find_structured_strings=lambda text: (),
        recognize_markers=lambda names: (),
        dimension_signal=lambda w, h: None,
        filename_pattern=lambda name: None,
    )
    base.update(over)
    return Readers(**base)


def go(db, corpus, **over):
    from evidence_shape.store import RunWriter
    from extractors.safety import SafetyPolicy
    from scan_agent.exclusion import is_protected_container

    selection = record_selection(db, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    policy = over.pop("policy", SafetyPolicy(
        is_protected_container=is_protected_container,
        is_dataless=lambda path: False))
    return run_wave2(
        db, selection,
        source=FilesystemCorpusSource(), mime_type_for=mime_for,
        scan_state="scanned", budget_exhausted=NEVER,
        detect_format=lambda p: p.suffix.lstrip(".") or None,
        policy=policy, readers=readers(**over.pop("readers", {})),
        sink=RunWriter(db, author="P5"),
        now=lambda: FIXED_CLOCK, context_window=40,
        no_usable_facts=over.pop("no_usable_facts", lambda f, h: False),
        transcription_authorized=lambda: False,
        corpus_form="snapshot", policy_settings={},
        file_entry_body=lambda row: {"payload_ref": f"blobs/{row['content_hash']}"},
        **over)


# ------------------------------------------------------------- it runs at all
def test_a_scan_now_produces_extraction_runs(db, corpus):
    """The whole reason this exists: `scan()` stopped, and nothing called P5."""
    result = go(db, corpus)
    assert isinstance(result, Wave2)
    runs = db.execute("SELECT count(*) c FROM extraction_runs").fetchone()["c"]
    assert runs > 0


def test_every_scanned_file_reaches_the_filesystem_tier(db, corpus):
    go(db, corpus)
    tiers = {r["analysis_tier"] for r in
             db.execute("SELECT DISTINCT analysis_tier FROM extraction_runs")}
    assert "filesystem" in tiers and "native" in tiers


def test_the_status_column_is_no_longer_empty_after_a_real_extraction(db, corpus):
    """§8.2's file record names "extraction status by extractor tier", and until this
    caller existed the column read `{}` after every real extraction."""
    import json
    go(db, corpus)
    rows = db.execute("SELECT extraction_status_by_tier FROM files").fetchall()
    assert rows
    for row in rows:
        status = json.loads(row["extraction_status_by_tier"])
        assert status != {}
        assert "filesystem" in status


def test_it_reads_current_path_and_not_path(db, corpus):
    """The sketch used `file_row["path"]` and would KeyError on the first file. The
    live column is `current_path`."""
    go(db, corpus)
    file_id = db.execute("SELECT file_id FROM files LIMIT 1").fetchone()["file_id"]
    assert get_file(db, file_id)["current_path"].startswith(str(corpus))


# ---------------------------------------------------------- exactly one event
def test_each_run_appends_exactly_one_event(db, corpus):
    go(db, corpus)
    for row in db.execute("SELECT run_id FROM extraction_runs"):
        events = db.execute(
            "SELECT count(*) c FROM events WHERE explanation LIKE ?",
            (f'%"run_id":"{row["run_id"]}"%',)).fetchone()["c"]
        assert events == 1, row["run_id"]


def test_no_event_names_the_orchestrator_as_its_author(db, corpus):
    """M8 / §8.2: an author field naming the part that merely ARRANGED the work makes
    §8.2's reconstruction requirement unmeetable. The orchestrator never appears."""
    go(db, corpus)
    authors = {r["subsystem"] for r in db.execute("SELECT DISTINCT subsystem FROM events")}
    assert authors <= {"P3", "P5"}


# --------------------------------------------------- the exception contract
def test_a_protected_container_produces_nothing_at_all(db, tmp_path):
    """11 §4b, ratified 2026-08-20. No run row, no observation, no status write for
    anything inside -- and `continue` the OUTER loop, never `break`, because `break`
    falls through to the status write and that is a P1 write authored "P5" on a file
    the product is forbidden to have touched."""
    from extractors.safety import SafetyPolicy
    root = tmp_path / "Apps"
    inside = root / "Numbers.app" / "Contents"
    inside.mkdir(parents=True)
    (inside / "sheet.numbers").write_bytes(b"x")
    (root / "ordinary.md").write_bytes(b"# fine")

    go(db, root, policy=SafetyPolicy(
        is_protected_container=lambda p: ".app" in str(p),
        is_dataless=lambda p: False))

    paths = [r["current_path"] for r in db.execute("SELECT current_path FROM files")]
    assert not any(".app" in p for p in paths), paths
    for row in db.execute("SELECT run_id, file_id FROM extraction_runs"):
        assert ".app" not in get_file(db, row["file_id"])["current_path"]


def test_a_reader_that_raises_becomes_a_failed_run_and_the_scan_continues(db, corpus):
    """§2.4: never silently an empty document -- and never a crashed scan either."""
    def locked(path):
        raise ValueError("file has not been decrypted")

    go(db, corpus, readers={"read_pdf": locked})
    failed = db.execute(
        "SELECT completeness, failure_reason FROM extraction_runs "
        "WHERE completeness = 'failed'").fetchall()
    assert len(failed) == 1
    assert failed[0]["failure_reason"] == "ValueError: file has not been decrypted"
    # The other file still got through.
    assert db.execute("SELECT count(*) c FROM files").fetchone()["c"] == 2


# -------------------------------------------------------------- the stat cache
def test_a_second_scan_of_an_unchanged_corpus_re_extracts_nothing(db, corpus):
    """§1.2: on REUSE, P5 is not invoked and prior results stand."""
    go(db, corpus)
    after_first = db.execute("SELECT count(*) c FROM extraction_runs").fetchone()["c"]
    go(db, corpus)
    assert db.execute(
        "SELECT count(*) c FROM extraction_runs").fetchone()["c"] == after_first


# ------------------------------------------------------------------ the bundle
def test_the_bundle_carries_the_scan_run_as_its_source_ref(db, corpus):
    """The join P3 published, P1 adopted, and nothing made until now."""
    result = go(db, corpus)
    row = db.execute("SELECT source_scan_ref, sealed_at FROM bundle_manifest "
                     "WHERE bundle_id = ?", (result.bundle_id,)).fetchone()
    assert row["source_scan_ref"] == result.scan_run_id
    assert row["sealed_at"] is not None


def test_the_bundle_counts_read_the_runs_that_were_actually_written(db, corpus):
    from eval_harness.counts import bundle_counts
    result = go(db, corpus)
    counts = bundle_counts(db, result.bundle_id)
    assert counts["files_indexed"] == 2


# ------------------------------------------------------- what it does not own
def test_the_orchestrator_holds_no_vocabulary():
    """It "spells no `completeness`, `source_type`, `analysis_tier`, zone or event
    type; every such value reaches P1/P4 inside a record a part constructed"."""
    import ast
    import orchestrator as module
    tree = ast.parse(Path(module.__file__).read_text())
    docstrings = {id(n.body[0].value) for n in ast.walk(tree)
                  if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef))
                  and n.body and isinstance(n.body[0], ast.Expr)
                  and isinstance(n.body[0].value, ast.Constant)
                  and isinstance(n.body[0].value.value, str)}
    held = {n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
            and id(n) not in docstrings}
    for token in ("complete", "metadata_only", "unsupported", "dataless", "failed",
                  "text_document", "image", "filesystem", "native", "ocr",
                  "extraction", "OCR", "heading", "body", "P5"):
        assert token not in held, token
