# tests/wave2/test_wave2_full_tree.py
"""The joins `test_wave2_orchestrator.py` does not see.

23-full-tree-stress.md executed the live tree and found six breaks that all passed
1,244 tests. Five of them are here; each one is a statement the eval bundle or the
status projection makes about a corpus that is not true of that corpus.

The sixth (two in-flight scans on one selection) is 11 §7 and is P3's, not the
caller's, so it is not tested here.

Fixtures are imported from the sibling module rather than re-declared -- and NOT
lifted into a `tests/wave2/conftest.py`, for the reason that module's own comment
gives.
"""
from pathlib import Path

import pytest

from eval_harness.counts import bundle_counts
from orchestrator import TARGETED_OCR_UNAVAILABLE, run_wave2
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.selection import record_selection

from test_wave2_orchestrator import (  # noqa: F401 -- pytest resolves fixtures by name
    FIXED_CLOCK, NEVER, corpus, db, go, mime_for, readers,
)


def _pdf_without_a_text_layer():
    """§2.2's `text_layer_absent`: the route that goes straight to OCR."""
    from extractors.pdf import PdfDocument
    return lambda p: PdfDocument(metadata={"Title": "Scanned"}, iso_dates={}, pages=())


# ----------------------------------------------------- 1. the bundle is the corpus
def test_a_rescan_bundle_still_carries_the_extractions(db, corpus):
    """§8.5's envelope must describe THIS selection's corpus, not this pass's writes.

    Second scan of an unchanged corpus is all REUSE, so nothing is re-extracted --
    which is right. The bundle then reported a directory listing with no extractions
    at all, and an eval harness reading it would measure a corpus where extraction
    never happened.
    """
    go(db, corpus)
    second = go(db, corpus)

    assert second.run_ids == ()          # nothing re-extracted: the cache worked
    counts = bundle_counts(db, second.bundle_id)
    assert counts["files_indexed"] == 2
    assert counts["files_with_any_run"] == 2, (
        "the second bundle describes a corpus nothing was ever extracted from")


def test_one_selections_bundle_does_not_swallow_anothers_files(db, tmp_path):
    """File membership was `SELECT * FROM files` -- every file in the database."""
    a = tmp_path / "A"
    a.mkdir()
    (a / "a.md").write_bytes(b"# alpha")
    b = tmp_path / "B"
    b.mkdir()
    (b / "b.md").write_bytes(b"# beta")

    go(db, a)
    second = go(db, b)

    paths = {row["file_id"] for row in db.execute(
        "SELECT file_id FROM bundle_file_entry WHERE bundle_id = ?",
        (second.bundle_id,))}
    names = {db.execute("SELECT current_path FROM files WHERE file_id = ?",
                        (fid,)).fetchone()["current_path"] for fid in paths}
    assert all(name.endswith("b.md") for name in names), (
        f"bundle B carries files from selection A: {names}")


def test_the_bundle_carries_the_observation_payloads(db, corpus):
    """`add_extraction_output` is P2's writer and the caller never called it.

    P2 implements it, `bundle_extraction_output` exists, and a replay bundle with
    zero payloads cannot replay anything: conformance rule 8's key is exactly what
    this table holds.
    """
    result = go(db, corpus)
    payloads = db.execute(
        "SELECT count(*) AS n FROM bundle_extraction_output WHERE bundle_id = ?",
        (result.bundle_id,)).fetchone()["n"]
    observations = db.execute(
        "SELECT count(*) AS n FROM evidence").fetchone()["n"]
    assert observations > 0, "the fixture produced no observations to carry"
    assert payloads == observations


# ------------------------------------------- 2. an OCR failure is not the PDF's loss
def test_an_ocr_failure_keeps_the_finished_pdf_run(db, corpus):
    """`extract()` built the PDF result, called OCR, and OCR raised -- so the PDF
    result was never returned. A finished native extraction was discarded because a
    SECOND, optional pass failed."""
    def engine_that_raises(path, config):
        raise RuntimeError("vision unavailable")

    go(db, corpus,
       readers={"read_pdf": _pdf_without_a_text_layer(),
                "ocr_engine": engine_that_raises},
       no_usable_facts=lambda file_id, content_hash: True)

    rows = db.execute(
        "SELECT extractor_name, completeness FROM extraction_runs "
        "WHERE extractor_name = 'pdf.text'").fetchall()
    assert rows, "the PDF produced no run at all"
    assert any(row["completeness"] != "failed" for row in rows), (
        "the finished native PDF run was discarded because OCR raised")


def test_a_failed_run_is_stamped_with_the_extractors_version(db, corpus):
    """The `failed` run carried `decision.router_version` -- the ROUTER's number --
    while claiming to be `pdf.text`. Two computations for one value: the run says
    `pdf.text` ran at a version `pdf.text` has never been at."""
    from extractors import pdf

    def reader_that_raises(path):
        raise RuntimeError("corrupt")

    go(db, corpus, readers={"read_pdf": reader_that_raises})

    row = db.execute(
        "SELECT extractor_name, extractor_version FROM extraction_runs "
        "WHERE completeness = 'failed'").fetchone()
    assert row is not None, "no failed run was recorded"
    assert row["extractor_name"] == pdf.EXTRACTOR_NAME
    assert row["extractor_version"] == pdf.VERSION, (
        f"the failed run claims {row['extractor_name']} at "
        f"{row['extractor_version']}; that extractor is at {pdf.VERSION}")


def test_a_router_handler_drift_propagates_rather_than_blaming_the_file(db, corpus):
    """`UnknownFamily` says the two routing tables disagree. That is a statement
    about the CALL, so it inherits `ContractViolation` -- recording it as this
    file's `failed` run would file a defect in P5 under the corpus's name, which is
    the exact swallow `ContractViolation` was introduced to stop."""
    from extractors.dispatch import UnknownFamily
    from extractors.failure import ContractViolation

    assert issubclass(UnknownFamily, ContractViolation)

    import extractors.dispatch as dispatch

    def drifted(**kwargs):
        raise UnknownFamily("the router named a handler nothing implements")

    original = dispatch.extract_pdf
    dispatch.extract_pdf = drifted
    try:
        with pytest.raises(UnknownFamily):
            go(db, corpus)
    finally:
        dispatch.extract_pdf = original

    failed = db.execute(
        "SELECT count(*) AS n FROM extraction_runs WHERE completeness = 'failed'"
    ).fetchone()["n"]
    assert failed == 0, "a P5 routing defect was recorded as the file's failure"


# ------------------------------------------ 3. eviction composes, never overwrites
class _EvictingSource:
    """A corpus source reporting one path as a dataless iCloud item.

    Staged at the SOURCE because it cannot be staged on the file: `SF_DATALESS` is
    outside macOS's `SF_SETTABLE` mask, as `scan_agent.dataless` says where it names
    the constant, so no test can set the real flag. `Entry.dataless` is the seam P3
    actually reads and the one `SnapshotCorpusSource` fills from a bundle.
    """

    has_bytes = True

    def __init__(self, evicted: Path):
        self._inner = FilesystemCorpusSource()
        self._evicted = str(evicted)

    def entries(self, directory):
        from dataclasses import replace
        return [replace(entry, dataless=True) if entry.path == self._evicted
                else entry
                for entry in self._inner.entries(directory)]


def _evicted(db, corpus):
    """Hashed on a first scan, then moved to iCloud: same size, same mtime, so P3's
    stat cache says REUSE and only the 2b loop sees it."""
    go(db, corpus)                                    # scan 1: everything local
    return corpus / "syllabus.pdf"


def test_eviction_composes_the_status_and_does_not_erase_the_native_run(db, corpus):
    """P5's own `test_p5_dataless_result.py` states the map is
    `{filesystem: complete, native: dataless}` when both runs are passed. The
    caller passed only the dataless one, so a full extraction's status was replaced
    by the single word `dataless` -- §8.6's line then reports a file as un-extracted
    that was extracted five seconds earlier."""
    import json

    from database_agent.files_table import get_file
    from extractors.safety import SafetyPolicy
    from scan_agent.exclusion import is_protected_container

    evicted = _evicted(db, corpus)
    file_id = db.execute("SELECT file_id FROM files WHERE current_path = ?",
                         (str(evicted),)).fetchone()["file_id"]
    before = json.loads(get_file(db, file_id)["extraction_status_by_tier"])
    assert before.get("filesystem") == "complete"

    go(db, corpus, source=_EvictingSource(evicted), policy=SafetyPolicy(
        is_protected_container=is_protected_container,
        is_dataless=lambda path: Path(path) == evicted))

    after = json.loads(get_file(db, file_id)["extraction_status_by_tier"])
    assert after.get("native") == "dataless"
    assert after.get("filesystem") == "complete", (
        f"the earlier filesystem run was erased by the eviction pass: {after}")


def test_the_dataless_predicate_is_one_gate_not_two(db, corpus):
    """P3 observes datalessness during the scan; P5's `SafetyPolicy.is_dataless`
    refuses the read. The caller is the only place that sees both, and it wired
    neither to the other -- so a policy that says "local" and a P3 detection that
    says "evicted" both ran, and the native extractor opened a file iCloud would
    have had to download."""
    from extractors.safety import SafetyPolicy
    from scan_agent.exclusion import is_protected_container

    evicted = _evicted(db, corpus)
    evicted.write_bytes(b"%PDF-1.4 BUSIB 4300 and one more line")   # size changed

    # The policy default every caller uses: "nothing is dataless".
    second = go(db, corpus, source=_EvictingSource(evicted), policy=SafetyPolicy(
        is_protected_container=is_protected_container,
        is_dataless=lambda path: False))

    file_id = db.execute("SELECT file_id FROM files WHERE current_path = ?",
                         (str(evicted),)).fetchone()["file_id"]
    this_pass = [dict(row) for row in db.execute(
        "SELECT analysis_tier, completeness FROM extraction_runs "
        f"WHERE file_id = ? AND run_id IN ({','.join('?' * len(second.run_ids))})",
        (file_id, *second.run_ids))] if second.run_ids else []

    assert any(row["completeness"] == "dataless" for row in this_pass), (
        "P3 detected the eviction and no dataless run was written for it")
    opened = [row for row in this_pass
              if row["analysis_tier"] == "native"
              and row["completeness"] == "complete"]
    assert not opened, (
        "the native extractor ran against an evicted file in the same pass that "
        "recorded it dataless -- on a real machine iCloud downloads it, which is "
        "the one thing 11 §5 exists to prevent")
