# tests/eval/test_counts.py
import json
from pathlib import Path

from eval_harness.bundle import (
    add_extraction_run, add_file_entry, open_bundle, seal_bundle,
)
from eval_harness.counts import (
    DEFERRED_COMPLETENESS, UNREADABLE_COMPLETENESS, bundle_counts,
)
from eval_harness.store import create_eval_schema

FIXTURES = Path(__file__).parent / "fixtures"


def _bundle_with_runs(conn, runs, *, entries):
    bundle_id = open_bundle(conn, corpus_form="snapshot",
                            source_scan_ref="scan-fixture",
                            pinned_plan_id="plan-fixture", pinned_plan_version="1",
                            policy_settings={})
    for file_id in entries:
        add_file_entry(conn, bundle_id, file_id=file_id,
                       content_hash=f"sha256:{file_id}", hash_algorithm="sha256",
                       handling_class=None, payload_ref=f"blobs/{file_id}")
    for row in runs:
        add_extraction_run(conn, bundle_id, row=row)
    seal_bundle(conn, bundle_id)
    return bundle_id


def test_the_two_completeness_sets_are_p5s(eval_conn):
    # P5: deferred = runs at `deferred` or `capped`; unreadable = `unreadable` or
    # `failed`. Adopted verbatim, not restated differently.
    assert DEFERRED_COMPLETENESS == frozenset({"deferred", "capped"})
    assert UNREADABLE_COMPLETENESS == frozenset({"unreadable", "failed"})


def test_the_count_line_is_reproducible_from_the_bundle_alone(eval_conn, tmp_path):
    # Done-means 13, with no live filesystem present.
    create_eval_schema(eval_conn)
    runs = json.loads((FIXTURES / "p4_runs.json").read_text(encoding="utf-8"))
    bundle_id = _bundle_with_runs(
        eval_conn, runs, entries=["file-book", "file-syllabus", "file-broken"])
    counts = bundle_counts(eval_conn, bundle_id)
    assert counts["files_indexed"] == 3
    assert counts["files_fully_extracted"] == 1          # only file-syllabus
    assert counts["runs_deferred"] == 1                  # the capped OCR run
    assert counts["runs_unreadable"] == 1                # the unreadable native run
    # Nothing but the database itself is on disk — no corpus, no extracted text,
    # no file the counts could have been read from. `eval_conn` opens
    # `tmp_path/agent.sqlite`, so the directory is never empty; the same targeted
    # form Task 5's `test_a_bundle_needs_no_live_filesystem` uses.
    assert {p.name for p in tmp_path.iterdir()} <= {
        "agent.sqlite", "agent.sqlite-wal", "agent.sqlite-shm"}


def test_files_requiring_model_review_is_unavailable_not_zero(eval_conn):
    # P5: "'Files require model review' is P8's count, not P5's." A 0 would assert
    # a fact P2 cannot know; None keeps unmeasured work visible as unmeasured.
    create_eval_schema(eval_conn)
    bundle_id = _bundle_with_runs(eval_conn, [], entries=["f1"])
    assert bundle_counts(eval_conn, bundle_id)["files_requiring_model_review"] is None


def test_indexed_is_reported_from_both_sources_because_they_disagree(eval_conn):
    # P2's Contract out §3 says the bundle_file_entry[] count; P5's mapping, which
    # the same paragraph says is adopted verbatim, says "files with any run".
    # This plan reports both and picks neither.
    create_eval_schema(eval_conn)
    runs = [json.loads((FIXTURES / "p4_runs.json").read_text(
        encoding="utf-8"))[1]]                     # only file-syllabus has a run
    bundle_id = _bundle_with_runs(eval_conn, runs,
                                  entries=["file-syllabus", "file-never-extracted"])
    counts = bundle_counts(eval_conn, bundle_id)
    assert counts["files_indexed"] == 2
    assert counts["files_with_any_run"] == 1
    assert counts["files_indexed"] != counts["files_with_any_run"]


def test_a_file_with_one_complete_and_one_capped_run_is_not_fully_extracted(eval_conn):
    # P5: "fully extracted = files whose EVERY run is `complete`." A PDF can have
    # a complete native run and a capped OCR run on the same content hash (I4).
    create_eval_schema(eval_conn)
    runs = [
        {"run_id": "r1", "file_id": "f1", "content_hash": "sha256:f1",
         "extractor_name": "pdf.native", "extractor_version": "1.0.0",
         "source_type": "text", "config_fingerprint": "sha256:c",
         "completeness": "complete",
         "coverage": {"units": "pages", "processed": 2, "total": 2},
         "observation_count": 3},
        {"run_id": "r2", "file_id": "f1", "content_hash": "sha256:f1",
         "extractor_name": "ocr.fixture", "extractor_version": "1.0.0",
         "source_type": "ocr", "config_fingerprint": "sha256:c",
         "completeness": "capped",
         "coverage": {"units": "pages", "processed": 1, "total": 2},
         "observation_count": 1},
    ]
    bundle_id = _bundle_with_runs(eval_conn, runs, entries=["f1"])
    counts = bundle_counts(eval_conn, bundle_id)
    assert counts["files_fully_extracted"] == 0
    assert counts["runs_deferred"] == 1


def test_the_counts_have_no_aggregate_and_no_ratio(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle_with_runs(eval_conn, [], entries=["f1"])
    counts = bundle_counts(eval_conn, bundle_id)
    for key in counts:
        for part in key.split("_"):
            assert part not in {"accuracy", "score", "aggregate", "overall", "rate",
                                "percent", "grade"}


def test_a_dataless_source_gets_its_own_count_and_is_not_called_unreadable(eval_conn):
    """C4, ratified 2026-08-20. A file whose bytes are in iCloud is not deferred (the
    budget did not run out), not unreadable (nothing is damaged), and not unsupported
    (an extractor exists). Before the ninth value it had no bucket at all, so §8.6's
    progress line either dropped these files or filed them under a word that lies."""
    from eval_harness.counts import DATALESS_COMPLETENESS
    assert DATALESS_COMPLETENESS == frozenset({"dataless"})
    create_eval_schema(eval_conn)
    runs = json.loads((FIXTURES / "p4_runs.json").read_text(encoding="utf-8"))
    cloud = {**runs[0], "run_id": "run-cloud", "file_id": "file-cloud",
             "content_hash": "sha256:file-cloud", "completeness": "dataless",
             "observation_count": 0}
    bundle_id = _bundle_with_runs(eval_conn, [cloud], entries=["file-cloud"])
    counts = bundle_counts(eval_conn, bundle_id)
    assert counts["runs_dataless"] == 1
    assert counts["runs_unreadable"] == 0
    assert counts["runs_deferred"] == 0
    assert counts["files_fully_extracted"] == 0
