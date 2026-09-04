"""`extract_initial` may run somewhere else, and the database may not notice.

`src/extraction_pool.py` moves one call off the calling thread. Everything that
makes that safe is a claim about ORDER and about a GATE, and this file is where both
are made to fail on purpose before they are believed.

**Order.** §3.4's caching and §8.5's replay both need a stable order, and
`evidence_shape/store.py`'s `_ordered` exists because "P4's `rowid` order is a
property of the database and reverses when the same three runs are written in the
opposite sequence (verified by execution)". A pool finishes work in whatever order
the operating system schedules it, so the loop takes results back in SUBMISSION
order. The pool below finishes every batch BACKWARDS -- the worst order there is --
and the two databases still have to match row for row.

**The gate.** Protected material is marked and counted, never opened. The rule is
kept by the CALL ORDER and not by a check: `extract_filesystem`, whose first
statement is `admit()`, runs on the calling thread, and a path that refuses there is
never submitted to anything. The pool below writes down every path it is handed, so
"never submitted" is an assertion about a list rather than a claim in a docstring.
"""
from pathlib import Path

import pytest

from database_agent.db import create_schema, open_database
from eval_harness.store import create_eval_schema
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import RunWriter
from extraction_pool import ExtractionContext, InlinePool, perform
from extractors.archive import ArchiveManifest
from extractors.dispatch import Readers
from extractors.docx import DocxDocument
from extractors.image import ImageRecord
from extractors.long_tail import LongTailFile
from extractors.pdf import PdfDocument, PdfPage
from extractors.reading import Region, StructuredString
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


CLOCK = "2026-09-04T00:00:00+00:00"

#: Enough files that a reversal is visible. Three would let a coincidence pass.
CORPUS = ("alpha.pdf", "bravo.pdf", "charlie.pdf", "delta.pdf",
          "echo.pdf", "foxtrot.pdf", "golf.pdf", "hotel.pdf")

#: The one this deployment's policy calls protected. It is an ORDINARY file on disk
#: and P3's own exclusion has no opinion about it, which is the point: the test is
#: about P5's gate and the pool, so P3 must not refuse it first and leave the gate
#: untested. `test_live_path.py` covers the P3 half with a real `Numbers.app`.
VAULT = "vault.pdf"


def _bootstrap(conn):
    create_schema(conn)
    create_scan_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    create_facts_schema(conn)
    create_privacy_schema(conn)
    create_eval_schema(conn)
    return conn


@pytest.fixture()
def first_db(conn):
    return _bootstrap(conn)


@pytest.fixture()
def second_db(tmp_path: Path):
    """A SECOND database, because the comparison is between two whole runs.

    Row-for-row means `rowid` order, and two runs sharing one database would
    interleave rather than be compared.
    """
    other = open_database(tmp_path / "second.sqlite")
    yield _bootstrap(other)
    other.close()


def _readers() -> Readers:
    """Deterministic, and DIFFERENT per file.

    Every page's text names its own file, so two runs that wrote the same rows in a
    different order produce different `raw_value` sequences and the comparison below
    can see it. A reader that returned the same text for every file would make the
    reversal invisible and the ordering test worthless.
    """
    def read_pdf(path: Path) -> PdfDocument:
        name = Path(path).stem
        text = f"{name} carries course PHYS1401 and nothing else"
        return PdfDocument(
            metadata={"Title": f"{name} title"},
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
        find_structured_strings=lambda text: (
            (StructuredString(kind="identifier", start=text.index("PHYS1401"),
                              end=text.index("PHYS1401") + 8),)
            if "PHYS1401" in text else ()),
        recognize_markers=lambda names: (),
        dimension_signal=lambda width, height: None,
        filename_pattern=lambda name: None,
        ocr_engine=None,
    )


class BackwardsPool:
    """A pool that finishes every batch in exactly the wrong order.

    It buffers submissions and computes the whole outstanding window in REVERSE the
    first time a result is asked for, then hands each one back when it is asked for.
    So the extractions genuinely happen last-file-first, and if `run_p1_p7` took
    results back in completion order rather than submission order, the rows would be
    written backwards and the comparison would fail.

    `lookahead` is the depth the caller reads ahead, and it is what makes the
    reversal reach further than one file: at eight, the whole corpus is in flight at
    once and the reversal is total.
    """

    def __init__(self, context: ExtractionContext, *, lookahead: int) -> None:
        self.lookahead = lookahead
        self._context = context
        self._queued: list = []
        self._done: dict = {}
        #: Every path this pool was handed, in the order it was handed them. The
        #: protected-container assertion is made against this list.
        self.submitted: list[str] = []
        self.closed = False

    def submit(self, request):
        handle = object()
        self.submitted.append(str(request.path))
        self._queued.append((handle, request))
        return handle

    def result(self, handle):
        if handle not in self._done:
            for queued, request in reversed(self._queued):
                self._done[queued] = perform(request, self._context)
            self._queued = []
        return self._done.pop(handle)

    def close(self) -> None:
        self.closed = True


def _run(conn, root: Path, *, pool, readers, policy):
    """One whole P1--P7 pass, with everything but the pool held fixed."""
    selection = record_selection(conn, sources=[root], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return run_p1_p7(
        conn, selection, source=FilesystemCorpusSource(),
        mime_type_for=lambda path: "application/pdf", scan_state="scanned",
        budget_exhausted=lambda: False, detect_format=lambda path: "pdf",
        policy=policy, readers=readers, sink=RunWriter(conn, author="P5"),
        now=lambda: CLOCK, context_window=40,
        transcription_authorized=lambda: False, corpus_form="snapshot",
        policy_settings={}, file_entry_body=lambda row: {"payload_ref": "blob"},
        resolve_native=lambda db, file_id, content_hash: None,
        targeted_ocr_needed=lambda file_id, content_hash: False,
        resolve_with_ocr=lambda db, file_id, content_hash: None,
        classify=lambda db, file_id, content_hash: None,
        classification_store=ClassificationStore(conn),
        p7_component_version="0.1.0", pool=pool)


def _corpus(tmp_path: Path, name: str, names=CORPUS) -> Path:
    root = tmp_path / name
    root.mkdir()
    for index, filename in enumerate(names):
        (root / filename).write_bytes(b"%PDF-1.4 " + str(index).encode() * 8)
    return root


def _fingerprint(conn) -> dict:
    """What the database says, IN ROWID ORDER, with nothing minted in it.

    `run_id`, `observation_id` and `file_id` are uuids and differ between any two
    runs, so comparing them would compare the random number generator. Everything
    below is content: `observation_key` is a digest of the observation, `location`
    carries the span, and `rowid` order is the thing under test -- it is not sorted
    away, because sorting it would delete the defect this file exists to catch.
    """
    return {
        "runs": [tuple(row) for row in conn.execute(
            "SELECT extractor_name, extractor_version, source_type, analysis_tier, "
            "config_fingerprint, completeness, coverage, observation_count, "
            "started_at, finished_at, failure_reason "
            "FROM extraction_runs ORDER BY rowid")],
        "evidence": [tuple(row) for row in conn.execute(
            "SELECT observation_key, extractor_name, raw_value, normalized_value, "
            "location, context_before, context_after, occurrence_count, "
            "observed_at, reliability FROM evidence ORDER BY rowid")],
        "text_units": [tuple(row) for row in conn.execute(
            "SELECT container_path, unit_locator, text, length, truncated "
            "FROM text_units ORDER BY rowid")],
        # `extraction_routing.observed_at` is deliberately absent, and it is the one
        # column in this comparison that is: `record_routing_decision` stamps it from
        # the WALL CLOCK rather than from the injected `now`, so two runs of the same
        # corpus differ there by however long the first one took. That is a real
        # determinism hole in the product and it predates any pool -- it is noted
        # here rather than sorted away, because a test that hid it would also hide
        # the day somebody fixed it.
        "routing": [tuple(row) for row in conn.execute(
            "SELECT detected_format, declared_extension, disagree, source_type, "
            "source_type_candidates, extractor_name, router_version, "
            "unrouted_completeness FROM extraction_routing ORDER BY rowid")],
    }


# --------------------------------------------------------------------------
# Order
# --------------------------------------------------------------------------

def test_a_pool_that_finishes_backwards_writes_the_same_rows_in_the_same_order(
        first_db, second_db, tmp_path):
    """The whole claim of the parallel path, stated as an equality.

    Two databases, one corpus, two pools: the serial one and one that computes every
    batch last-file-first. If the loop consumed results as they finished rather than
    as it submitted them, `evidence` would come back in a different `rowid` order and
    §3.4's cache and §8.5's replay would key off a run nobody could reproduce.
    """
    # ONE corpus, read twice into two databases. Two directories would differ by
    # their own absolute paths, which `filesystem.record` observes and hashes into
    # `observation_key` -- so the comparison would fail on the folder's name and
    # never reach the thing under test.
    root = _corpus(tmp_path, "corpus")

    _run(first_db, root, pool=InlinePool(ExtractionContext(
        policy=_open_policy(), readers=_readers(),
        transcription_authorized=lambda: False)),
        readers=_readers(), policy=_open_policy())

    backwards = BackwardsPool(
        ExtractionContext(policy=_open_policy(), readers=_readers(),
                          transcription_authorized=lambda: False),
        lookahead=len(CORPUS))
    _run(second_db, root, pool=backwards, readers=_readers(),
         policy=_open_policy())

    serial, parallel = _fingerprint(first_db), _fingerprint(second_db)
    assert serial["runs"], "the corpus produced no runs; the comparison is empty"
    for table in ("runs", "evidence", "text_units", "routing"):
        assert parallel[table] == serial[table], (
            f"{table} differs between the serial and the reversed run")


def test_the_reversal_really_happened(tmp_path, second_db):
    """The control for the test above, and it is not ceremony.

    A `BackwardsPool` that quietly computed forwards would make the equality above
    pass while proving nothing at all. This asserts the pool really did do the work
    last-file-first: the whole corpus was in flight before anything was computed.
    """
    root = _corpus(tmp_path, "reversed")
    backwards = BackwardsPool(
        ExtractionContext(policy=_open_policy(), readers=_readers(),
                          transcription_authorized=lambda: False),
        lookahead=len(CORPUS))
    order: list[str] = []
    real_perform = backwards.result

    def watched(handle):
        before = list(backwards._done)
        outcome = real_perform(handle)
        if not before:
            order.extend(backwards.submitted)
        return outcome

    backwards.result = watched
    _run(second_db, root, pool=backwards, readers=_readers(),
         policy=_open_policy())

    assert len(backwards.submitted) == len(CORPUS), (
        f"every file should have been submitted once: {backwards.submitted}")
    assert order == backwards.submitted, (
        "the whole window was not in flight when the first result was taken, so "
        "the reversal never reached past one file")


def test_the_pool_is_closed_even_though_the_run_succeeded(tmp_path, second_db):
    """`close()` cancels the window. It runs on every way out, not just the bad one:
    a pool left open holds worker processes after the run that needed them ended."""
    root = _corpus(tmp_path, "closed")
    backwards = BackwardsPool(
        ExtractionContext(policy=_open_policy(), readers=_readers(),
                          transcription_authorized=lambda: False),
        lookahead=len(CORPUS))
    _run(second_db, root, pool=backwards, readers=_readers(),
         policy=_open_policy())
    assert backwards.closed is True


# --------------------------------------------------------------------------
# The gate
# --------------------------------------------------------------------------

def _open_policy() -> SafetyPolicy:
    return SafetyPolicy(is_protected_container=lambda path: False,
                        is_dataless=lambda path: False)


def _vault_policy() -> SafetyPolicy:
    """This deployment's policy: `vault.pdf` is inside a protected container.

    The predicate and not the filename is what the product enforces --
    `scan_agent.exclusion.is_protected_container` answers the same shape for a real
    `.app` -- and using a plain file here is deliberate: P3's exclusion would refuse
    a real bundle before P5's gate ever saw it, and a gate that is never reached is a
    gate that is never tested.
    """
    return SafetyPolicy(is_protected_container=lambda path: Path(path).name == VAULT,
                        is_dataless=lambda path: False)


def test_a_protected_path_is_never_handed_to_the_pool(tmp_path, second_db):
    """THE standing rule, as a property of the call order.

    `extract_filesystem` runs `admit()` on the calling thread before anything is
    submitted, so a protected path cannot reach a worker -- not because a worker
    checks, but because no request for it is ever made. The pool writes down every
    path it is given; this asserts what is on that list and what is not.
    """
    root = _corpus(tmp_path, "vaulted", names=(*CORPUS, VAULT))
    pool = BackwardsPool(
        ExtractionContext(policy=_vault_policy(), readers=_readers(),
                          transcription_authorized=lambda: False),
        lookahead=len(CORPUS))
    _run(second_db, root, pool=pool, readers=_readers(), policy=_vault_policy())

    assert pool.submitted, "nothing was submitted at all; the test proves nothing"
    assert not [path for path in pool.submitted if Path(path).name == VAULT], (
        f"a protected path was submitted to a worker: {pool.submitted}")
    assert sorted(Path(p).name for p in pool.submitted) == sorted(CORPUS), (
        "every unprotected file should still have been read")


def test_the_protected_file_is_counted_and_not_silently_omitted(
        tmp_path, second_db):
    """Marked and counted, never opened -- and never quietly dropped either.

    The file keeps its P1 row and stays in the roster; what it does not get is an
    extraction run or one byte of content in the database.
    """
    root = _corpus(tmp_path, "counted", names=(*CORPUS, VAULT))
    pool = BackwardsPool(
        ExtractionContext(policy=_vault_policy(), readers=_readers(),
                          transcription_authorized=lambda: False),
        lookahead=len(CORPUS))
    _run(second_db, root, pool=pool, readers=_readers(), policy=_vault_policy())

    names = [row[0] for row in second_db.execute("SELECT filename FROM files")]
    assert VAULT in names, "the protected file was omitted from the corpus entirely"

    runs = [row[0] for row in second_db.execute(
        "SELECT DISTINCT f.filename FROM extraction_runs r "
        "JOIN files f ON f.file_id = r.file_id")]
    assert VAULT not in runs, "a protected file was extracted"

    values = [row[0] for row in second_db.execute(
        "SELECT raw_value FROM evidence")] + [
        row[0] for row in second_db.execute("SELECT text FROM text_units")]
    assert not [v for v in values if v and VAULT.removesuffix(".pdf") in v], (
        "content from inside the protected container reached the database")


def test_the_gate_holds_when_the_pool_is_the_serial_one_too(tmp_path, second_db):
    """The same assertion through `InlinePool`, because the rule is the loop's and
    not the pool's. If this ever passed while the test above failed, the protection
    would be an accident of one pool's implementation."""
    root = _corpus(tmp_path, "serial-vault", names=(*CORPUS, VAULT))
    seen: list[str] = []
    inline = InlinePool(ExtractionContext(
        policy=_vault_policy(), readers=_readers(),
        transcription_authorized=lambda: False))
    real_submit = inline.submit

    def watched(request):
        seen.append(str(request.path))
        return real_submit(request)

    inline.submit = watched
    _run(second_db, root, pool=inline, readers=_readers(),
         policy=_vault_policy())
    assert seen, "nothing was submitted at all; the test proves nothing"
    assert not [path for path in seen if Path(path).name == VAULT]


# --------------------------------------------------------------------------
# The same claim, through real worker processes rather than a double.
# --------------------------------------------------------------------------

def _real_context() -> ExtractionContext:
    """What a spawned worker builds for itself.

    A module-level function because `spawn` re-imports rather than inheriting: what
    crosses the boundary is this NAME. It is deliberately the same wiring
    `_readers()` gives the caller, because a worker wired differently from its caller
    would write rows the caller could never reproduce -- and reproducing them is what
    this section is about.
    """
    return ExtractionContext(policy=_open_policy(), readers=_readers(),
                             transcription_authorized=lambda: False)


def test_two_runs_through_real_workers_produce_the_same_database(
        first_db, second_db, tmp_path):
    """Determinism is a product promise, and the pool is where it was most at risk.

    §3.4's caching and §8.5's replay both key off what a run wrote. Real worker
    processes finish in whatever order the operating system schedules them, and that
    order is genuinely different between two runs -- so if any of it reached the
    database, two runs over one corpus would differ and neither could be replayed.

    Two runs, two databases, one corpus, a real `ProcessPool` each time. The rows
    have to match in `rowid` order, which is submission order, which is roster order.
    """
    from extraction_pool import ProcessPool

    root = _corpus(tmp_path, "corpus")
    for conn in (first_db, second_db):
        pool = ProcessPool(workers=2, context_factory=_real_context,
                           lookahead_per_worker=2, floor=0)
        try:
            _run(conn, root, pool=pool, readers=_readers(), policy=_open_policy())
        finally:
            pool.close()

    first, second = _fingerprint(first_db), _fingerprint(second_db)
    assert first["evidence"], "the corpus produced no evidence; this proves nothing"
    for table in ("runs", "evidence", "text_units", "routing"):
        assert second[table] == first[table], (
            f"{table} differs between two runs of the same corpus through real "
            "worker processes")


def test_the_real_pool_agrees_with_the_serial_one_row_for_row(
        first_db, second_db, tmp_path):
    """And the parallel database is the SERIAL database, not merely a stable one of
    its own. A pool that consistently wrote the same wrong order would pass the test
    above and change every §3.4 cache key in the product."""
    from extraction_pool import ProcessPool

    root = _corpus(tmp_path, "corpus")
    _run(first_db, root, pool=InlinePool(_real_context()),
         readers=_readers(), policy=_open_policy())

    pool = ProcessPool(workers=2, context_factory=_real_context,
                       lookahead_per_worker=2, floor=0)
    try:
        _run(second_db, root, pool=pool, readers=_readers(),
             policy=_open_policy())
    finally:
        pool.close()

    serial, parallel = _fingerprint(first_db), _fingerprint(second_db)
    for table in ("runs", "evidence", "text_units", "routing"):
        assert parallel[table] == serial[table], (
            f"{table} differs between the serial run and the real pool")


# --------------------------------------------------------------------------
# The floor: below it, no worker is started at all.
# --------------------------------------------------------------------------

def test_a_run_below_the_floor_never_starts_a_worker(second_db, tmp_path):
    """Seven interpreters to read eight files is the wrong trade, and this is the
    assertion that keeps it from being made.

    A spawned worker re-imports the composition root and Apple's Vision framework at
    about five seconds of CPU each, so seven of them cost thirty-five CPU-seconds
    before one file is read. Measured on the owner's real files: four files take 1.0s
    serial and 3.4s with seven workers; twelve take 2.7s and 8.2s. Small folders are
    his ORDINARY case, so below the floor the pool reads on the calling thread.

    `started` and not `_pool is None` is what the assertion reads, and the difference
    is the whole test: `run_p1_p7` closes the pool on its way out and `close()` sets
    `_pool` back to None, so after a run the two cases are indistinguishable. The
    first version of this test asked the wrong one and passed whether or not seven
    interpreters had been started.
    """
    from extraction_pool import ProcessPool

    root = _corpus(tmp_path, "small")
    pool = ProcessPool(workers=7, context_factory=_real_context,
                       lookahead_per_worker=2, floor=len(CORPUS))
    try:
        _run(second_db, root, pool=pool, readers=_readers(),
             policy=_open_policy())
        assert pool.started is False, (
            "a worker pool was started for a corpus smaller than the floor")
    finally:
        pool.close()

    runs = second_db.execute(
        "SELECT COUNT(*) FROM extraction_runs "
        "WHERE extractor_name = 'pdf.text'").fetchone()[0]
    assert runs == len(CORPUS), "the files were not read at all"


def test_a_run_above_the_floor_does_start_workers(second_db, tmp_path):
    """The negative twin. Without it the floor could be hard-wired to "never build a
    pool" and every test above would still pass while the product had no concurrency
    at all."""
    from extraction_pool import ProcessPool

    root = _corpus(tmp_path, "big-enough")
    pool = ProcessPool(workers=2, context_factory=_real_context,
                       lookahead_per_worker=2, floor=2)
    try:
        _run(second_db, root, pool=pool, readers=_readers(),
             policy=_open_policy())
        assert pool.started is True, (
            "no worker pool was started for a corpus well above the floor")
    finally:
        pool.close()


def test_the_floor_does_not_change_a_single_row(first_db, second_db, tmp_path):
    """Whichever side of the floor a file falls on, the database is the same one.

    This is the assertion that makes the floor an optimisation rather than a second
    code path: a pool whose floor splits the corpus in half runs some files here and
    some in a worker, and the rows must be indistinguishable from the serial run's --
    same order, same spans, same keys.
    """
    from extraction_pool import ProcessPool

    root = _corpus(tmp_path, "corpus")
    _run(first_db, root, pool=InlinePool(_real_context()),
         readers=_readers(), policy=_open_policy())

    split = ProcessPool(workers=2, context_factory=_real_context,
                        lookahead_per_worker=2, floor=len(CORPUS) // 2)
    try:
        _run(second_db, root, pool=split, readers=_readers(),
             policy=_open_policy())
        assert split.started is True, "the corpus did not cross the floor"
    finally:
        split.close()

    serial, straddling = _fingerprint(first_db), _fingerprint(second_db)
    for table in ("runs", "evidence", "text_units", "routing"):
        assert straddling[table] == serial[table], (
            f"{table} differs when half the corpus was read here and half in a worker")


def test_a_pool_refuses_a_floor_that_is_not_a_count():
    from extraction_pool import ProcessPool

    with pytest.raises(ValueError, match="count of submissions"):
        ProcessPool(workers=2, context_factory=_real_context,
                    lookahead_per_worker=2, floor=-1)
