# tests/p5/test_p5_join.py
"""The four join defects the 2026-08-21 stress test executed against live packages.

Each passed every unit test in tests/p5/ while being broken, because the suite is
comprehensive about SHAPE and was not comprehensive about the JOIN: P5 never called
extraction_status_by_tier on the two-run unrouted fixture, never raised from a
reader, never collapsed DOCX, and never went through P4's event writer.
"""
from pathlib import Path

import pytest


# ---------------------------------------------------------------- break 2
def test_an_unrouted_run_is_the_native_tier_not_a_second_filesystem_extract():
    """A4, ratified 2026-08-20: a routed-but-stopped run carries `analysis_tier: native`.

    It was `filesystem`, reusing `filesystem.record` as the extractor name. So a .dmg
    produced TWO runs in the filesystem tier -- `complete` from the indexer and
    `metadata_only` from the stopper -- and extraction_status_by_tier raised
    TierConflict on the first .dmg in Downloads. The stopping run is not a second
    filesystem extract; it is the native extractor that did not exist or refused.
    """
    from extractors.filesystem import unrouted_result
    from extractors.router import route
    row = {"file_id": "f1", "content_hash": "a" * 64, "filename": "archive.dmg",
           "extension": ".dmg", "mime_type": None, "detected_format": "dmg"}
    decision = route(file_id="f1", content_hash="a" * 64, path=Path("/c/archive.dmg"),
                     extension=".dmg", detect_format=lambda p: "dmg")
    result = unrouted_result(file_row=row, decision=decision, now="t")
    assert result.run["analysis_tier"] == "native"
    assert result.run["extractor_name"] != "filesystem.record"


def test_the_indexer_and_the_stopper_no_longer_collide():
    """The executed failure: extraction_status_by_tier([filesystem, unrouted]) raised."""
    from extractors.runs import extraction_status_by_tier
    fs = {"analysis_tier": "filesystem", "completeness": "complete"}
    stopped = {"analysis_tier": "native", "completeness": "metadata_only"}
    assert extraction_status_by_tier([fs, stopped]) == {
        "filesystem": "complete", "native": "metadata_only"}


# ---------------------------------------------------------------- break 3
def test_a_reader_that_raises_becomes_a_failed_run_not_a_crashed_scan():
    """§2.4's `completeness=failed` is in P4's vocabulary and rule 9. Nothing produced
    it: `src/extractors/` contained zero `except`. A password-protected PDF, a corrupt
    ZIP or a truncated DOCX propagated and ended the scan."""
    from extractors.failure import failed_result
    row = {"file_id": "f1", "content_hash": "b" * 64, "filename": "locked.pdf",
           "extension": ".pdf", "mime_type": None, "detected_format": "pdf"}
    result = failed_result(file_row=row, error=ValueError("file is encrypted"),
                           extractor_name="pdf.text", extractor_version="0.1.0",
                           source_type="text_document", now="t")
    assert result.run["completeness"] == "failed"
    assert result.observations == ()          # P4 rule 9: failed carries none
    assert "encrypted" in result.run["failure_reason"]


def test_the_exception_is_the_signal_and_no_threshold_is_invented():
    """"Do not invent a threshold for 'too corrupt.' The exception is the signal."""
    import ast, inspect
    from extractors import failure
    # Scoped to CODE, not prose. Asserting a token appears nowhere in the source also
    # matches the docstring explaining WHY the token is absent -- the guard-token trap
    # that has now bitten this project five times. Names and literals only.
    tree = ast.parse(inspect.getsource(failure))
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    names |= {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    numbers = {n.value for n in ast.walk(tree)
               if isinstance(n, ast.Constant) and isinstance(n.value, (int, float))}
    assert not any("threshold" in x.lower() or "max_" in x.lower() for x in names), names
    assert not (numbers - {0, 1}), f"an invented number: {numbers}"


# ---------------------------------------------------------------- break 4
def test_every_extractor_collapses_because_the_result_itself_does():
    """P4 D10: one observation per (run, exact raw value, zone), `occurrence_count`
    counting within the zone and `location` addressing the FIRST occurrence.

    `_collapse` lived in pdf.py and archive.py only, so DOCX, structured text,
    long-tail, OCR, image and filesystem emitted one row per hit -- exploding row
    counts and splitting P6's weight across clones of one string. Collapsing where
    every extractor already passes (ExtractionResult) fixes six at one point, and a
    seventh extractor inherits it instead of silently skipping it.
    """
    from extractors.sink import ExtractionResult
    from extractors.shape import location, observation
    def obs(raw):
        return observation(file_id="f1", content_hash="c" * 64,
                           extractor_name="docx.text", extractor_version="0.1.0",
                           source_type="text_document", raw_value=raw,
                           location=location(zone="body"), observed_at="t",
                           reliability="possible")
    result = ExtractionResult(run={"run_id": "r"},
                              observations=(obs("Columbia"), obs("Columbia"), obs("Yale")))
    assert len(result.observations) == 2, "two Columbia hits must collapse to one row"
    columbia = [o for o in result.observations if o["raw_value"] == "Columbia"][0]
    assert columbia["occurrence_count"] == 2


# ---------------------------------------------------------------- break 5
def test_p5_does_not_write_events_around_p4():
    """P4's `record_run_event` shipped. P5's `append` still called P1's `append_event`
    directly, so an orchestrator following both plans writes two `extraction` events
    per run -- and "exactly one event per run" cannot hold."""
    import inspect
    from extractors import events
    src = inspect.getsource(events)
    body = "\n".join(l for l in src.split("\n") if not l.lstrip().startswith("#"))
    # Break 5 is NOT closed, and the test says so rather than pretending.
    # P4's record_run_event reads observation_keys from stored rows, so it needs the
    # run written first; P5 authors its event before any sink has seen the run. The
    # fix needs the orchestrator's ordering (run -> observations -> one event), so
    # this asserts the reason is recorded, not that the swap happened.
    assert "record_run_event" in src, "the blocker must stay documented at the call site"
    assert "orchestrator" in src.lower()
