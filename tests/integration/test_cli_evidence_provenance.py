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
from extractors.long_tail import SENSITIVITY_DDL  # noqa: E402

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


# --- `104` R-148: the readings a file offers about itself ----------------------

#: The `files` row `reading_citations` reads the version off. `content_hash_of`
#: keys the reading set to a file VERSION, so a fixture without this row is a file
#: this run has never seen rather than a file with nothing to say.
def _indexed(conn, *, file_id: str = "file-1",
             content_hash: str = CONTENT_HASH) -> None:
    # P5's table, empty. `releasable_observations` asks it for the per-value
    # signal, and a fixture without it would be a corpus P5 never ran on rather
    # than one it found nothing in.
    conn.executescript(SENSITIVITY_DDL)
    conn.execute(
        "INSERT INTO files (file_id, current_path, filename, "
        "normalized_filename, extension, directory_position, volume_id, "
        "content_hash, hash_algorithm, observed_size, observed_timestamps, "
        "scan_state) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (file_id, "/holder/corpus/Problem Set 3.txt", "Problem Set 3.txt",
         "problem set 3.txt", ".txt", 0, "volume-1", content_hash, "sha256",
         len(BODY), "{}", "indexed"))


def test_a_file_with_body_text_and_no_fact_still_offers_its_own_readings(
        evidence):
    """`104` R-148, and it is the whole row. Site C's evidence was built out of
    `file_facts`, so a file P6 settled nothing about arrived at
    `_judge_with_model` with nothing to send and was recorded
    `NOT_ELIGIBLE_FOR_MODEL` before a dossier existed -- 103 of the owner's 199
    files on r12, and 52% of their coursework. No fact is written here; the
    readings come back anyway, because they are the file's own words."""
    _indexed(evidence)
    key = _observation(evidence, zone="body", span=TextSpan(10, 21),
                       value="problem set")

    offered = cli.reading_citations(evidence, "file-1", limit=12)

    assert [ref for ref, _location, _reliability in offered] == [key]
    # And there is no fact to be had: P6's table is not even on this connection,
    # so nothing here could be reading one by accident.
    assert not evidence.execute(
        "SELECT name FROM sqlite_master WHERE name = 'file_facts'").fetchall()


def test_a_reading_carries_its_own_zone_and_its_own_span(evidence):
    """The address is P4's. `104` R-11 records what inventing one cost at this
    same seam: `location="heading"` and `excerpt_span=(0, len(value))` printed
    over every citation there had ever been."""
    _indexed(evidence)
    _observation(evidence, zone="table", span=TextSpan(0, 9), value="PHYS 1401")

    (_ref, location, reliability), = cli.reading_citations(
        evidence, "file-1", limit=12)

    assert location.zone == "table"
    assert (location.text_span.start, location.text_span.end) == (0, 9)
    # P4's own word for the reading, not a constant typed at the seam.
    assert reliability == "direct"


def test_a_file_with_no_readings_offers_none(evidence):
    """The state that stays `NOT_ELIGIBLE_FOR_MODEL`, and it is then a true
    sentence: a file with nothing to send is not sent."""
    _indexed(evidence)

    assert cli.reading_citations(evidence, "file-1", limit=12) == ()


def test_an_always_local_reading_is_not_offered(evidence):
    """`releasable_observations`' first exclusion, reached through this seam
    rather than restated: §8.4's `path` and `filename` zones may never leave the
    device, and placement is the site where the folder a file already sits in
    looks like the most relevant evidence in the store."""
    _indexed(evidence)
    body = _observation(evidence, zone="body", span=TextSpan(10, 21),
                        value="problem set")
    _observation(evidence, zone="path", span=None, value="/holder/corpus",
                 container=(Segment(kind="field", label="directory"),))

    offered = cli.reading_citations(evidence, "file-1", limit=12)

    assert [ref for ref, _location, _reliability in offered] == [body]


def test_a_whole_document_reading_is_not_offered(evidence):
    """§8.4's "should not send full documents where a short heading or OCR
    excerpt is enough", applied a step before the door so the call is never built
    rather than built and denied.

    THE DOCUMENT GAINED ITS LINE BREAKS FOR `104` R-152, and it needed its own unit to
    hold them. It was the whole of `BODY`, one 49-character line, which is now RELEASED:
    a unit holding no line break is a line, and §8.4 names a short excerpt as what to
    send instead of a document. A control built from a single line was pinning the
    refusal that row measured as the loss -- 47 gate denials at r13, 36 of them a whole
    site-A call. `BODY` stays as it is because half this file addresses spans into it.
    """
    _indexed(evidence)
    short = _observation(evidence, zone="body", span=TextSpan(10, 21),
                         value="problem set")
    page_three = (Segment(kind="page", index=3),)
    document = (BODY + "\nHand it in at the box outside the office.\n"
                "Late work loses a letter grade.")
    record_text_unit(evidence, TextUnit(run_id="run-1",
                                        container_path=page_three, text=document))
    _observation(evidence, zone="body", span=TextSpan(0, len(document)),
                 value=document, container=page_three)

    offered = cli.reading_citations(evidence, "file-1", limit=12)

    assert [ref for ref, _location, _reliability in offered] == [short]


def test_the_cap_is_the_callers_and_this_function_states_no_number(evidence):
    """`FACT_CALL_MAX_RELEASED_OBSERVATIONS` is where this deployment chooses the
    count, for site A and now for site C. A default here would be a second
    choice, and the two would drift."""
    _indexed(evidence)
    for start in range(0, 6):
        _observation(evidence, zone="body", span=TextSpan(start, start + 4),
                     value=BODY[start:start + 4])

    assert len(cli.reading_citations(evidence, "file-1", limit=2)) == 2
    assert len(cli.reading_citations(evidence, "file-1", limit=6)) == 6


def test_a_file_this_run_has_no_version_for_offers_nothing(evidence):
    """`located_citations`' own rule, one address up: a file version nothing
    carries is not evidence, and a reading set keyed to no hash would be a
    different file's."""
    _observation(evidence, zone="body", span=TextSpan(10, 21),
                 value="problem set")

    assert cli.reading_citations(evidence, "file-1", limit=12) == ()
