"""What `evidence_for` tells P11 about a file is what the database actually holds.

`104` R-11's second half. Before this, `cli.run.evidence_for` built one
`EvidenceItem` per fact out of three values it made up:

    location="heading"                  for a value read out of a table, a
                                        filename, OCR or anywhere at all
    excerpt_span=(0, len(value))        coordinates into the FACT VALUE, which is
                                        not the document the span addresses
    basis="direct-anchor"               printed over an `llm_supported` guess

and it took `evidence_refs[0]`, so on the owner's corpus 97 facts carrying 525
citations between them offered 97 and called the other 428 absent. `00`:58 asks the
dossier to "explicitly distinguish direct evidence from inferred context", and
`00`:62 has the validator check "that every cited text span or metadata field exists
in SQLite". Neither was true of what this seam produced.

The helpers are module-level in `cli` so that this file can put a real evidence row
in front of them and read the answer, rather than asserting the shape of a closure
through a whole run.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402
from evidence_shape.location import Location, Segment, TextSpan  # noqa: E402
from evidence_shape.locator import serialize_locator  # noqa: E402
from evidence_shape.observation import Observation, observation_key  # noqa: E402
from evidence_shape.runs import ExtractionRun  # noqa: E402
from evidence_shape.schema import create_evidence_schema  # noqa: E402
from evidence_shape.store import (  # noqa: E402
    TextUnit, record_observation, record_run, record_text_unit,
)

CONTENT_HASH = "b" * 64
AT = "2026-09-06T00:00:00+00:00"
PAGE = (Segment(kind="page", index=2),)
BODY = "PHYS 1401 problem set 3. Due Thursday October 17."


@pytest.fixture()
def evidence(conn):
    """P1's root connection with P4's tables and one file version's text on it."""
    create_evidence_schema(conn)
    record_run(conn, ExtractionRun(
        run_id="run-1", file_id="file-1", content_hash=CONTENT_HASH,
        extractor_name="fixture.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=AT, observation_count=2))
    record_text_unit(conn, TextUnit(run_id="run-1", container_path=PAGE,
                                    text=BODY))
    return conn


def _observation(conn, *, zone: str, span: TextSpan | None, value: str,
                 container=PAGE) -> str:
    location = Location(zone=zone, container_path=container, text_span=span)
    record_observation(conn, Observation(
        file_id="file-1", content_hash=CONTENT_HASH,
        extractor_name="fixture.text", extractor_version="1.0.0",
        source_type="text_document", raw_value=value, location=location,
        occurrence_count=1, observed_at=AT, reliability="direct", run_id="run-1",
        context_before=None, context_after=None, context_truncated=False))
    return observation_key(content_hash=CONTENT_HASH,
                           extractor_name="fixture.text",
                           locator=serialize_locator(location), raw_value=value)


def test_a_citation_resolves_to_its_real_zone_and_its_real_span(evidence):
    """The address is P4's, not a shape invented at the seam. `heading` was printed
    for every citation there has ever been; here the observation is in `table`."""
    key = _observation(evidence, zone="table", span=TextSpan(0, 9),
                       value="PHYS 1401")

    located = cli.located_citations(evidence, "file-1", [key])

    assert len(located) == 1
    ref, location = located[0]
    assert ref == key
    assert location.zone == "table"
    assert (location.text_span.start, location.text_span.end) == (0, 9)


def test_every_citation_is_returned_and_not_only_the_first(evidence):
    """`104` R-11. One fact, three citations: the seam offered one of them."""
    keys = [
        _observation(evidence, zone="title", span=TextSpan(0, 9),
                     value="PHYS 1401"),
        _observation(evidence, zone="body", span=TextSpan(10, 21),
                     value="problem set"),
        _observation(evidence, zone="metadata", span=None, value="coursework",
                     container=(Segment(kind="field", label="category"),)),
    ]

    located = cli.located_citations(evidence, "file-1", keys)

    assert [ref for ref, _location in located] == keys
    assert {location.zone for _ref, location in located} == {
        "title", "body", "metadata"}


def test_a_span_less_citation_keeps_no_span_rather_than_a_made_up_one(evidence):
    """§2.3's cell and §2.8's field address a container and no span. `(0, len(value))`
    said otherwise for both, and for every one of them at once."""
    key = _observation(evidence, zone="metadata", span=None, value="coursework",
                       container=(Segment(kind="field", label="category"),))

    (_ref, location), = cli.located_citations(evidence, "file-1", [key])

    assert location.text_span is None


def test_a_citation_that_does_not_resolve_is_dropped_and_not_carried(evidence):
    """`00`:62: the validator checks "that every cited text span or metadata field
    exists in SQLite". An address nothing carries is not evidence, and passing it on
    would put a citation the validator must reject in front of the model."""
    real = _observation(evidence, zone="body", span=TextSpan(0, 9),
                        value="PHYS 1401")

    located = cli.located_citations(
        evidence, "file-1", [real, "sha256:" + "0" * 64])

    assert [ref for ref, _location in located] == [real]


def test_a_citation_belonging_to_another_file_is_not_this_files_evidence(evidence):
    """`within_file_ids` is the scope, and the membership check is what makes the
    answer this file's. A key that resolves elsewhere is somebody else's citation."""
    key = _observation(evidence, zone="body", span=TextSpan(0, 9),
                       value="PHYS 1401")

    assert cli.located_citations(evidence, "file-2", [key]) == ()


def test_one_citation_named_twice_is_one_citation(evidence):
    """An address repeated in `evidence_refs` is the same address."""
    key = _observation(evidence, zone="body", span=TextSpan(0, 9),
                       value="PHYS 1401")

    assert len(cli.located_citations(evidence, "file-1", [key, key, key])) == 1
