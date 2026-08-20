# tests/p5/test_p5_dataless_result.py
"""OQ4 -- the run for a file whose bytes are in iCloud.

C4, ratified 2026-08-20: P4 gets an explicit NINTH `completeness` value, `dataless`,
so §8.6's progress line can say "31 files are in iCloud" instead of filing them under
a word that lies about why they are missing. P4 has the value and P2 has the bucket
(`eval_harness/counts.py`), and until now nothing could construct the run that fills
either -- so the bucket could only ever read zero.

The gate keeps one job. `admit()` still raises `DatalessRefused` and writes nothing;
this is the CATCHER C4 names, and it is only constructible for a file recorded while
local and evicted since (OQ3) -- a file dataless at first sight has no `files` row,
because minting one requires a hash and hashing downloads the bytes (11 §5).
"""
import pytest

from extractors.filesystem import VERSION, dataless_result
from extractors.runs import TierConflict, extraction_status_by_tier
from extractors.safety import DatalessRefused

from conftest import FIXED_CLOCK

HASH = "5f7b1a1c9d4e6f2a3b8c0d1e2f3a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c"
FILE_ROW = {"file_id": "f1", "content_hash": HASH, "filename": "Thesis.pdf",
            "extension": ".pdf", "mime_type": "application/pdf",
            "detected_format": "pdf"}


def a_result(**over):
    return dataless_result(file_row={**FILE_ROW, **over.pop("file_row", {})},
                           error=DatalessRefused("bytes are not on this machine"),
                           source_type="text_document", now=FIXED_CLOCK, **over)


def test_the_run_carries_c4s_ninth_completeness_value():
    assert a_result().run["completeness"] == "dataless"


def test_it_carries_zero_observations_and_no_text():
    """P4 rule 9: `dataless` is in ZERO_OBSERVATION_COMPLETENESS -- nothing was
    opened, so nothing was seen."""
    result = a_result()
    assert result.observations == ()
    assert result.text_units == ()


def test_the_identity_is_the_one_recorded_while_the_file_was_local():
    """Nothing is re-hashed. The hash on the run is the hash P1 already stored."""
    result = a_result()
    assert result.run["content_hash"] == HASH
    assert result.run["file_id"] == "f1"


def test_the_run_is_the_native_tier_not_the_filesystem_tier():
    """18-wave2-orchestrator.md's OQ4 direction says `analysis_tier=filesystem`.
    Executed, that reproduces break 2: the file was scanned while local, so a
    `complete` filesystem run already exists for it, and a second filesystem-tier run
    at `dataless` makes extraction_status_by_tier raise TierConflict on exactly the
    files this value was added to make visible.

    A4's precedent settles it. A routed-but-stopped run is the NATIVE extractor that
    could not read -- and a dataless file is the same shape: the bytes were not there
    to read. The filesystem tier keeps saying what stat knows, which is still true.
    """
    assert a_result().run["analysis_tier"] == "native"

    indexer = {"analysis_tier": "filesystem", "completeness": "complete"}
    assert extraction_status_by_tier([indexer, a_result().run]) == {
        "filesystem": "complete", "native": "dataless"}


def test_the_filesystem_tier_direction_would_have_collided():
    """The executed counter-example, kept so the choice above cannot be quietly
    reverted to the page's direction."""
    indexer = {"analysis_tier": "filesystem", "completeness": "complete"}
    as_filesystem = {"analysis_tier": "filesystem", "completeness": "dataless"}
    with pytest.raises(TierConflict):
        extraction_status_by_tier([indexer, as_filesystem])


def test_it_carries_no_failure_reason_because_nothing_failed():
    """P4 conformance rule 9: `failure_reason` belongs to `failed` and `unreadable`.

    This test asserted the opposite first and P4 rejected the run -- correctly, and
    for C4's own reason. A file in iCloud has not failed and is not damaged, so a
    reason phrased as one is the lie the ninth value was added to stop.
    `completeness = dataless` is the whole explanation.
    """
    assert a_result().run["failure_reason"] is None


def test_it_refuses_to_build_a_run_for_a_file_that_has_no_identity():
    """OQ3's caveat, enforced rather than documented: a file dataless at FIRST SIGHT
    has no `files` row and no hash, and inventing either violates 11 §5."""
    with pytest.raises(ValueError):
        a_result(file_row={"content_hash": None})
    with pytest.raises(ValueError):
        a_result(file_row={"file_id": None})


def test_the_run_conforms_to_p4(sink):
    from p4_stub import validate_run
    result = a_result()
    run_id = sink.write(result)
    validate_run(sink.run_for(run_id), 0)


def test_the_version_is_the_modules_own():
    assert a_result().run["extractor_version"] == VERSION
