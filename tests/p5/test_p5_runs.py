# tests/p5/test_p5_runs.py
"""P4's `extraction_runs`, from P5's side: coverage, §3.4's cache key, and the four
analysis tiers I4 closed."""
import pytest

from extractors.runs import (
    ANALYSIS_TIER_BY_EXTRACTOR, TierConflict, cache_key, coverage,
    extraction_status_by_tier,
)


def a_run(**overrides):
    row = dict(extractor_name="pdf.text", analysis_tier="native",
               completeness="complete")
    row.update(overrides)
    return row


def test_coverage_is_p4s_three_keys_and_nothing_else():
    assert coverage("pages", 40, 312) == {"units": "pages", "processed": 40,
                                          "total": 312}


def test_coverage_refuses_to_claim_more_progress_than_there_is():
    with pytest.raises(ValueError):
        coverage("pages", 400, 312)
    with pytest.raises(ValueError):
        coverage("pages", -1, 312)


def test_the_tier_map_is_i4s_four_names_and_p5_writes_three_of_them():
    # SPEC: "filesystem observations re-emitted as `source_type: filesystem` are
    # `filesystem`; E1-E5 are `native`; E6 is `ocr`." P8 is the only writer of `llm`.
    assert ANALYSIS_TIER_BY_EXTRACTOR["filesystem.record"] == "filesystem"
    for native in ("pdf.text", "docx.structure", "text.structured",
                   "archive.manifest", "image.metadata"):
        assert ANALYSIS_TIER_BY_EXTRACTOR[native] == "native"
    assert set(ANALYSIS_TIER_BY_EXTRACTOR.values()) == {"filesystem", "native"}


def test_an_ocr_extractor_name_is_recognised_by_its_prefix():
    # §2.7's provider is named by the engine, not by P5 (S1 makes Apple Vision the
    # one engine v1 ships, and the engine reports its own name). The tier is keyed on
    # the family prefix so a new provider needs no edit here.
    from extractors.runs import analysis_tier_for
    assert analysis_tier_for("ocr.apple_vision") == "ocr"
    assert analysis_tier_for("pdf.text") == "native"
    assert analysis_tier_for("filesystem.record") == "filesystem"


def test_an_unknown_extractor_name_has_no_tier_and_is_not_guessed():
    from extractors.runs import analysis_tier_for
    with pytest.raises(KeyError):
        analysis_tier_for("something.new")


def test_a_rename_is_free_because_the_path_is_not_in_the_cache_key():
    # §3.4, quoted in the SPEC: "This is what makes a rename free and a content
    # rewrite expensive." There is no path parameter to pass.
    import inspect
    assert "path" not in inspect.signature(cache_key).parameters
    first = cache_key(content_hash="sha256:abc", extractor_name="pdf.text",
                      extractor_version="0.1.0", analysis_tier="native",
                      config_fingerprint="sha256:cfg")
    second = cache_key(content_hash="sha256:abc", extractor_name="pdf.text",
                       extractor_version="0.1.0", analysis_tier="native",
                       config_fingerprint="sha256:cfg")
    assert first == second


def test_a_content_rewrite_an_upgrade_and_a_config_change_each_change_the_key():
    base = dict(content_hash="sha256:abc", extractor_name="pdf.text",
                extractor_version="0.1.0", analysis_tier="native",
                config_fingerprint="sha256:cfg")
    original = cache_key(**base)
    assert cache_key(**{**base, "content_hash": "sha256:def"}) != original
    assert cache_key(**{**base, "extractor_version": "0.2.0"}) != original
    assert cache_key(**{**base, "analysis_tier": "ocr"}) != original
    assert cache_key(**{**base, "config_fingerprint": "sha256:other"}) != original
    # §2.7's provider is part of the key for OCR, and it is `extractor_name`: there
    # is no OCR-specific key shape (B1).
    assert cache_key(**{**base, "extractor_name": "ocr.apple_vision"}) != original


def test_the_status_map_names_only_the_tiers_that_were_attempted():
    # SPEC: "a missing key means that tier was not attempted."
    runs = [a_run(extractor_name="filesystem.record", analysis_tier="filesystem"),
            a_run(extractor_name="image.metadata", analysis_tier="native"),
            a_run(extractor_name="ocr.apple_vision", analysis_tier="ocr",
                  completeness="capped")]
    assert extraction_status_by_tier(runs) == {
        "filesystem": "complete", "native": "complete", "ocr": "capped"}


def test_an_image_that_ran_e5_and_e6_says_exif_succeeded_and_ocr_capped():
    # B1's own sentence: an opaque image "produces two rows and can say 'EXIF read
    # successfully, OCR capped.' A per-file status could not express that."
    runs = [a_run(extractor_name="image.metadata", analysis_tier="native",
                  completeness="complete"),
            a_run(extractor_name="ocr.apple_vision", analysis_tier="ocr",
                  completeness="capped")]
    status = extraction_status_by_tier(runs)
    assert status["native"] == "complete"
    assert status["ocr"] == "capped"


def test_two_runs_at_one_tier_that_disagree_are_not_collapsed_silently():
    # The design does not rule on this and P5 does not pick a winner.
    runs = [a_run(analysis_tier="native", completeness="complete"),
            a_run(analysis_tier="native", completeness="failed")]
    with pytest.raises(TierConflict):
        extraction_status_by_tier(runs)


def test_p5_never_puts_llm_in_the_status_map():
    runs = [a_run(analysis_tier="llm", completeness="complete")]
    with pytest.raises(ValueError):
        extraction_status_by_tier(runs)


def test_the_module_writes_nothing_to_the_files_table():
    # P1 publishes no setter for `files.extraction_status_by_tier`, and `files` is
    # P1's table. This module computes the map and a caller hands it over.
    from pathlib import Path

    import extractors.runs as module
    source = Path(module.__file__).read_text().upper()
    assert "UPDATE FILES" not in source
    assert "INSERT INTO FILES" not in source
