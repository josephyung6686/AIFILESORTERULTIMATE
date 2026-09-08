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
from privacy.vocabulary import CLOUD_LOCALITY  # noqa: E402

#: `104` R-159's two new keywords, spelled once for this file. `CLOUD_LOCALITY`
#: because every test here predates the ruling and is about the cloud half of it,
#: which is the half that did not change; the ceiling because a cloud call is bound
#: by the COUNT and never reads the ceiling, so any value states the same thing and
#: this one is the product's own stored number.
A_CEILING = 4000

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

    offered = cli.reading_citations(evidence, "file-1", limit=12,
                                  locality=CLOUD_LOCALITY, ceiling=A_CEILING)

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
        evidence, "file-1", limit=12, locality=CLOUD_LOCALITY,
        ceiling=A_CEILING)

    assert location.zone == "table"
    assert (location.text_span.start, location.text_span.end) == (0, 9)
    # P4's own word for the reading, not a constant typed at the seam.
    assert reliability == "direct"


def test_a_file_with_no_readings_offers_none(evidence):
    """The state that stays `NOT_ELIGIBLE_FOR_MODEL`, and it is then a true
    sentence: a file with nothing to send is not sent."""
    _indexed(evidence)

    assert cli.reading_citations(evidence, "file-1", limit=12,
                                  locality=CLOUD_LOCALITY, ceiling=A_CEILING) == ()


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

    offered = cli.reading_citations(evidence, "file-1", limit=12,
                                  locality=CLOUD_LOCALITY, ceiling=A_CEILING)

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

    offered = cli.reading_citations(evidence, "file-1", limit=12,
                                  locality=CLOUD_LOCALITY, ceiling=A_CEILING)

    assert [ref for ref, _location, _reliability in offered] == [short]


def test_the_cap_is_the_callers_and_this_function_states_no_number(evidence):
    """`FACT_CALL_MAX_RELEASED_OBSERVATIONS` is where this deployment chooses the
    count, for site A and now for site C. A default here would be a second
    choice, and the two would drift."""
    _indexed(evidence)
    for start in range(0, 6):
        _observation(evidence, zone="body", span=TextSpan(start, start + 4),
                     value=BODY[start:start + 4])

    assert len(cli.reading_citations(evidence, "file-1", limit=2,
                                     locality=CLOUD_LOCALITY, ceiling=A_CEILING)) == 2
    assert len(cli.reading_citations(evidence, "file-1", limit=6,
                                     locality=CLOUD_LOCALITY, ceiling=A_CEILING)) == 6


def test_a_file_this_run_has_no_version_for_offers_nothing(evidence):
    """`located_citations`' own rule, one address up: a file version nothing
    carries is not evidence, and a reading set keyed to no hash would be a
    different file's."""
    _observation(evidence, zone="body", span=TextSpan(10, 21),
                 value="problem set")

    assert cli.reading_citations(evidence, "file-1", limit=12,
                                  locality=CLOUD_LOCALITY, ceiling=A_CEILING) == ()


# --- `104` R-156: the item set is the set the door releases --------------------

#: R-154 asked the first of `releasable_excerpts`' five refusals a step early, in
#: `evidence_for`'s fact loop. The other four need the observation row and the
#: length of the unit a span points into, which `located_citations` does not
#: carry -- so `releasable_items` asks the door's own predicate over the candidate
#: refs instead of retyping them here. These tests drive that function with real
#: P4 rows, which is the same shape the rest of this file uses: the helpers are
#: module-level in `cli` so a test can put an evidence row in front of them.


def _item(ref: str, *, zone: str = "body", span=(10, 21)):
    from llm_harness.records import EvidenceItem
    from llm_harness.vocabulary import DIRECT_ANCHOR

    return EvidenceItem(evidence_ref=ref, kind="fact", location=zone,
                        excerpt_span=span, reliability_state="direct",
                        basis=DIRECT_ANCHOR)


def _offered(conn, *refs) -> list:
    return [item.evidence_ref
            for item in cli.releasable_items(conn, [_item(ref) for ref in refs],
                                     locality=CLOUD_LOCALITY)]


def test_a_fact_cited_from_a_body_span_is_offered(evidence):
    """The positive control, and the half that makes the four refusals below
    discriminating. A rule that dropped every item would pass all of them."""
    _indexed(evidence)
    body = _observation(evidence, zone="body", span=TextSpan(10, 21),
                        value="problem set")

    assert _offered(evidence, body) == [body]


def test_a_fact_cited_from_a_p5_signalled_reading_is_offered_no_item(evidence):
    """The refusal neither of the others can see, which is why the count is five.

    P5's per-value signal is the only one in the product -- P7 owns no detector --
    and a flagged card number sits in an ordinary `body` zone and is a fraction of
    its unit, so the zone test and the whole-unit test both pass it through. The
    gate answers `ProtectedItemRequested`; before this the seam offered the item,
    the model cited it, and `CITATION_NOT_IN_DOSSIER` took the whole answer.
    """
    from extractors.long_tail import (
        POTENTIALLY_SENSITIVE, SensitivitySignal, record_sensitivity_signals,
    )

    _indexed(evidence)
    card = "4111 1111 1111 1111"
    unit = (Segment(kind="page", index=4),)
    record_text_unit(evidence, TextUnit(run_id="run-1", container_path=unit,
                                        text=f"Card: {card}, expires soon"))
    flagged = _observation(evidence, zone="body", span=TextSpan(6, 6 + len(card)),
                           value=card, container=unit)
    ordinary = _observation(evidence, zone="body", span=TextSpan(10, 21),
                            value="problem set")
    keys = [row["observation_key"] for row in evidence.execute(
        "SELECT observation_key FROM evidence ORDER BY rowid")]
    record_sensitivity_signals(
        evidence, run_id="run-1",
        signals=(SensitivitySignal(observation_index=keys.index(flagged),
                                   signal=POTENTIALLY_SENSITIVE,
                                   basis="fixture: a card number"),),
        observation_keys=keys, now=AT)

    assert _offered(evidence, flagged, ordinary) == [ordinary]


def test_a_fact_cited_from_a_whole_multi_line_unit_is_offered_no_item(evidence):
    """§8.4's "should not send full documents where a short heading or OCR excerpt
    is enough", read at the seam rather than at the door.

    THE UNIT HOLDS LINE BREAKS ON PURPOSE (`104` R-152): a unit with none is a
    LINE and a line released whole is an excerpt, so a single-line control would
    pin a refusal that no longer exists. A fact whose citation covers the whole of
    a real document is the case that survives.
    """
    _indexed(evidence)
    short = _observation(evidence, zone="body", span=TextSpan(10, 21),
                         value="problem set")
    unit = (Segment(kind="page", index=5),)
    document = (BODY + "\nHand it in at the box outside the office.\n"
                "Late work loses a letter grade.")
    record_text_unit(evidence, TextUnit(run_id="run-1", container_path=unit,
                                        text=document))
    whole = _observation(evidence, zone="body", span=TextSpan(0, len(document)),
                         value=document, container=unit)

    assert _offered(evidence, whole, short) == [short]


def test_an_always_local_citation_is_offered_no_item_through_the_one_predicate(
        evidence):
    """`104` R-154's ruling, now answered by the same call as the other four.

    This is what makes the separate zone test in `evidence_for`'s fact loop safe
    to remove: the zone is part of an observation key's own address -- the key is
    minted over `serialize_locator(location)` -- so any live row for a ref carries
    the zone the loop read off it, and the door's first refusal and the loop's
    could not have disagreed.

    `anchor_line_citations` keeps its own check (`104` R-150). It is a separate
    function with its own contract and its own callers, and the reading it refuses
    it also refuses to NAME -- an address the caller never receives cannot be
    filtered by anything the caller does afterwards.
    """
    _indexed(evidence)
    body = _observation(evidence, zone="body", span=TextSpan(10, 21),
                        value="problem set")
    named = _observation(evidence, zone="filename", span=None,
                         value="Problem Set 3.txt",
                         container=(Segment(kind="field", label="name"),))

    assert _offered(evidence, named, body) == [body]


def test_an_empty_reading_cannot_exist_for_this_seam_to_offer(evidence):
    """The fifth refusal's state, and the honest answer about it.

    `releasable_excerpts` refuses an observation with no raw value, and this
    database cannot hold one: `Observation` refuses the empty string at
    construction, `record_observation` is the only INSERT into `evidence`, and
    `evidence_never_overwritten` forbids an UPDATE of `raw_value`. So the refusal
    guards a shape the record type does not admit rather than a row a corpus can
    produce, and a fixture that faked one would be testing a database that cannot
    exist. Pinned here so the guard is not later "fixed" by inventing a path to
    it.
    """
    from evidence_shape.observation import MalformedObservation

    with pytest.raises(MalformedObservation, match="raw_value"):
        _observation(evidence, zone="body", span=TextSpan(0, 0), value="")


# --- `104` R-159: site C has no ladder, so the remainder is computed --------

def test_the_ceiling_is_a_remainder_and_a_reading_over_it_is_skipped(evidence):
    """`104` R-159. Site A defers a call whose dossier will not fit; site C cannot.

    `placement.pipeline._judge_with_model` builds its request and the gate answers,
    so an over-ceiling site-C dossier is `Denied(over_dossier_ceiling)` and the file
    loses the one stage `00` §5 built for ambiguity. `evidence_for` therefore hands
    this function what `max_dossier_tokens` has LEFT after the facts' citations and
    R-135's anchor lines, and the fill spends that rather than the whole ceiling.

    A reading too long for the remainder is SKIPPED and the walk continues, so one
    oversized unit does not cost the file the smaller readings behind it.
    """
    _indexed(evidence)
    small = _observation(evidence, zone="body", span=TextSpan(0, 9),
                         value=BODY[:9])
    _observation(evidence, zone="body", span=TextSpan(0, len(BODY) - 1),
                 value=BODY[:len(BODY) - 1])
    later = _observation(evidence, zone="body", span=TextSpan(10, 21),
                         value=BODY[10:21])

    offered = cli.reading_citations(
        evidence, "file-1", limit=12, locality="local", ceiling=20)

    assert [ref for ref, _location, _reliability in offered] == [small, later]


def test_a_cloud_placement_call_is_bound_by_the_count_and_not_the_remainder(
        evidence):
    """The other half, and it is what says this is a locality rule rather than a
    new bound on everyone. §8.4's "selected excerpts" states no number and
    `FACT_CALL_MAX_RELEASED_OBSERVATIONS` is where this deployment chooses one; a
    cloud call spends that and never reads the ceiling."""
    _indexed(evidence)
    for start in range(0, 6):
        _observation(evidence, zone="body", span=TextSpan(start, start + 4),
                     value=BODY[start:start + 4])

    # A remainder that would admit at most one reading, and the count is what binds.
    offered = cli.reading_citations(
        evidence, "file-1", limit=6, locality=CLOUD_LOCALITY, ceiling=1)

    assert len(offered) == 6
