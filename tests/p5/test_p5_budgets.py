# tests/p5/test_p5_budgets.py
"""§8.6 — the four ceilings, deferral, and the count line P4's `completeness` feeds."""
import pytest

import extractors.budgets as budgets_module
from database_agent.budget import BUDGET_DDL, CEILING_KEYS, set_ceiling
from database_agent.db import create_schema

from extractors.budgets import (
    DEFERRED_COMPLETENESS, P5_CEILING_KEYS, UNREADABLE_COMPLETENESS, deferred_result,
    extraction_counts, p5_ceilings,
)

from conftest import FIXED_CLOCK

FILE_ROW = {"file_id": "f-book", "content_hash": "338b639c2b1f4ae1ae5341132963e1a4ec8a5017775c92300270d14dbff12f4c",
            "filename": "scanned-book-400pp.pdf"}


def a_run(file_id, completeness, tier="native"):
    return {"file_id": file_id, "completeness": completeness, "analysis_tier": tier}


def test_p5s_four_ceilings_are_p1s_keys():
    # G4: P1 owns the §8.6 configuration object, namespaced. P5 defines no key.
    assert len(P5_CEILING_KEYS) == 4
    assert set(P5_CEILING_KEYS) <= set(CEILING_KEYS)
    assert P5_CEILING_KEYS == ("ocr.max_pages_per_file", "ocr.max_time_per_file",
                               "ocr.max_time_per_scan",
                               "image.max_analysis_ops_per_scan")


def test_p5_stores_no_ceiling_value():
    for name, value in vars(budgets_module).items():
        if name.startswith("__"):
            continue
        assert not isinstance(value, (int, float)) or isinstance(value, bool), name


def test_a_ceiling_is_read_through_p1_and_is_none_until_p1_holds_one(conn):
    create_schema(conn)
    conn.executescript(BUDGET_DDL)
    assert p5_ceilings(conn) == {key: None for key in P5_CEILING_KEYS}
    set_ceiling(conn, "ocr.max_pages_per_file", 50)
    assert p5_ceilings(conn)["ocr.max_pages_per_file"] == 50


def test_a_deferred_run_carries_no_evidence_at_all(sink):
    result = deferred_result(file_row=FILE_ROW, source_type="text_document",
                             extractor_name="ocr.apple-vision",
                             extractor_version="19.1", analysis_tier="ocr",
                             units="pages", total=400, now=FIXED_CLOCK)
    run_id = sink.write(result)
    assert sink.observations_for(run_id) == []
    assert sink.units_for(run_id) == []
    assert sink.run_for(run_id)["coverage"] == {"units": "pages", "processed": 0,
                                               "total": 400}
    sink.conforms()


def test_a_deferral_is_not_a_failure(sink):
    # §8.6's legibility rule: a file that was never processed must never look like a
    # file that was understood and found unimportant.
    run_id = sink.write(deferred_result(
        file_row=FILE_ROW, source_type="text_document",
        extractor_name="ocr.apple-vision", extractor_version="19.1",
        analysis_tier="ocr", units="pages", total=400, now=FIXED_CLOCK))
    row = sink.run_for(run_id)
    assert row["completeness"] == "deferred"
    assert row["failure_reason"] is None


def test_p5_publishes_no_cheaper_substitute():
    # §8.6: "Cost exhaustion must never turn into lower-quality automatic
    # classification." There is nothing here to downgrade to.
    names = [n for n in vars(budgets_module) if not n.startswith("__")]
    for token in ("fallback", "substitute", "guess", "downgrade", "cheaper"):
        assert not [n for n in names if token in n.lower()], token


def test_the_section_8_6_count_line():
    # "1,842 files indexed; 1,611 fully extracted; 89 … deferred after the OCR limit;
    # … 18 files remain unreadable."
    runs = [
        a_run("a", "complete", "filesystem"), a_run("a", "complete"),
        a_run("b", "complete", "filesystem"), a_run("b", "capped", "ocr"),
        a_run("c", "complete", "filesystem"), a_run("c", "deferred", "ocr"),
        a_run("d", "unreadable"),
        a_run("e", "failed"),
    ]
    counts = extraction_counts(runs, files_scanned=10)
    assert counts == {"files_scanned": 10, "indexed": 5, "fully_extracted": 1,
                      "deferred": 2, "unreadable": 2}


def test_capped_and_deferred_are_one_query_and_unreadable_and_failed_another():
    # B1: two different values, two different queries — never two readings of one
    # word.
    assert DEFERRED_COMPLETENESS == ("deferred", "capped")
    assert UNREADABLE_COMPLETENESS == ("unreadable", "failed")
    assert not set(DEFERRED_COMPLETENESS) & set(UNREADABLE_COMPLETENESS)


def test_a_complete_run_with_zero_observations_is_still_fully_extracted():
    # §2.4's `complete`-with-zero: the file genuinely contained nothing, and that is
    # a processed file.
    counts = extraction_counts([a_run("a", "complete")], files_scanned=1)
    assert counts["fully_extracted"] == 1


def test_an_unsupported_run_is_neither_extracted_nor_unreadable():
    # §2.4's four distinguishable states stay four.
    counts = extraction_counts([a_run("a", "unsupported")], files_scanned=1)
    assert counts["indexed"] == 1
    assert counts["fully_extracted"] == 0
    assert counts["deferred"] == 0
    assert counts["unreadable"] == 0


def test_metadata_only_is_indexed_and_not_fully_extracted():
    counts = extraction_counts([a_run("a", "metadata_only")], files_scanned=1)
    assert counts == {"files_scanned": 1, "indexed": 1, "fully_extracted": 0,
                      "deferred": 0, "unreadable": 0}


def test_files_requiring_model_review_are_p8s_count_and_not_here():
    counts = extraction_counts([a_run("a", "complete")], files_scanned=1)
    assert "model" not in " ".join(counts)
    assert "review" not in " ".join(counts)
