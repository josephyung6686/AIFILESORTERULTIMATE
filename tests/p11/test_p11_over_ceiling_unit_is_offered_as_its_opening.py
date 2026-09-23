# tests/p11/test_p11_over_ceiling_unit_is_offered_as_its_opening.py
"""A unit LONGER than the stored ceiling reaches site C as its opening, not as nothing.

**Measured on the owner's own corpus, 22 Sep 2026.** A cloud run over 199 files left
113 of the 182 it should have filed unfiled, and the largest single cause was the
door: 15 `whole_document_requested` refusals and 9 `dossier_over_budget`, 24 files
between them, every one at `pre-call:C_placement`. On the 34-file corpus the same
refusal accounted for 2 of the 4 misses. The units were 4,753 and 7,442 characters
against a stored 4,000.

**The refusal is right and the request is what is wrong.** `items.check_item`
withholds any reading longer than the stored ceiling, which is §8.4's "should not
send full documents where a short heading or OCR excerpt is enough to resolve the
question" doing its job. What §8.4 asks for instead already exists and is already
ratified: `model_facts.mint_opening_excerpts` cuts a bounded opening off a reading
no call can carry, under four refusals asked before anything is cut, and site A has
used it since `104` R-164.

**Site C never called it.** `model_placement.py` imported exactly one name from
`model_facts` -- `may_be_released` -- so the same question got two answers at two
sites, which is the thing `104` R-159 exists to refuse in its own words: *"The five
refusals are one question -- may this reading leave the device -- and one question
does not get two answers because two sites ask it."*

**The bound is derived and not chosen here.** `opening_excerpt_bound` is
`ceiling // limit`, and site A's limit is `FACT_CALL_MAX_RELEASED_OBSERVATIONS`
(twelve, "because a fact call asks about a dozen fields"), the gate's is
`GATE_MAX_RELEASED_OBSERVATIONS` (five). Site C has no such count, and inventing an
eighteenth published number is exactly what R-159 forbids. So the limit is the one
the call already states: the number of readings this call carries. The bound
function's own sentence is that rule -- *"A call may carry `limit` readings under
`ceiling` characters, so `ceiling // limit` is the largest excerpt at which a call
carrying its full complement of them still fits"* -- and for this site the full
complement is what was asked for.

SABOTAGE: give `releasable_excerpts` back its old import list and the first test
goes red with the whole unit offered alone, which is the state the corpus measured.
"""
from __future__ import annotations

import json

from database_agent.budget import BUDGET_DDL, set_ceiling
from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_observation, record_run, record_text_unit
from evidence_shape.text_units import TextUnit

from extractors.long_tail import SENSITIVITY_DDL

from model_facts import DOSSIER_CEILING_KEY
from model_placement import releasable_excerpts
from privacy.vocabulary import CLOUD_LOCALITY

CLOCK = "2026-09-22T00:00:00Z"

#: The stored ceiling for these tests. The same 4,000 the owner's deployment holds,
#: so the arithmetic under test is the deployment's own and not a fixture's.
A_CEILING = 4000

#: Longer than the ceiling, and multi-line so no line-unit exemption can carry it.
#: 5,000 characters: `104` §17.13's whole-unit arm releases a unit UNDER the ceiling
#: to either target, so a unit that is merely long proves nothing. This one is over.
A_LONG_PAGE = "\n".join(f"line {n:04d} of a long scanned page" for n in range(160))
assert len(A_LONG_PAGE) > A_CEILING, "the fixture must exceed the ceiling to bind"


def _corpus(conn, tmp_path):
    """One document whose single text unit is longer than the stored ceiling."""
    create_schema(conn)
    create_evidence_schema(conn)
    conn.executescript(SENSITIVITY_DDL)
    conn.executescript(BUDGET_DDL)
    set_ceiling(conn, DOSSIER_CEILING_KEY, A_CEILING)

    body = A_LONG_PAGE.encode()
    path = tmp_path / "scan.pdf"
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename="scan.pdf", normalized_filename="scan.pdf",
        extension=".pdf", observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Scans", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    run_id = "run-scan"
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))

    page_at = (Segment("page", 1),)
    record_text_unit(conn, TextUnit(
        run_id=run_id, container_path=page_at, text=A_LONG_PAGE))
    page = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document",
        raw_value=A_LONG_PAGE,
        location=Location("body", page_at, text_span=TextSpan(0, len(A_LONG_PAGE))),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id=run_id)
    record_observation(conn, page)
    return file_id, content_hash, page


def test_site_c_offers_a_bounded_opening_of_an_over_ceiling_unit(conn, tmp_path):
    """The whole point: something the door can carry is offered for this file.

    Before this, the only excerpt offered was the whole 5,000-character unit, which
    `items.check_item` withholds for being longer than the stored ceiling -- so the
    call carried nothing about the file's text and the placement abstained.
    """
    _fid, _ch, page = _corpus(conn, tmp_path)

    offered = releasable_excerpts(
        conn, evidence_refs=[page.observation_key], locality=CLOUD_LOCALITY)

    carried = [one for one in offered
               if one.span is not None
               and (one.span.end - one.span.start) <= A_CEILING]
    assert carried, (
        "every excerpt offered for this file is longer than the ceiling the door "
        "enforces, so the call would carry no text at all")


def test_the_opening_is_bounded_by_the_deployment_arithmetic_not_by_a_typed_number(
        conn, tmp_path):
    """`ceiling // limit`, with the limit the call's own count of readings.

    One reading is asked for here, so the bound is the whole ceiling and the opening
    is 4,000 characters of a 5,000-character page. The assertion is the arithmetic
    rather than the number: change the stored ceiling and the excerpt follows it,
    which is what `104` R-159 means by "only number".
    """
    _fid, _ch, page = _corpus(conn, tmp_path)

    offered = releasable_excerpts(
        conn, evidence_refs=[page.observation_key], locality=CLOUD_LOCALITY)

    openings = [one for one in offered
                if one.span is not None
                and (one.span.end - one.span.start) <= A_CEILING]
    assert openings, "no bounded opening was offered"
    longest = max(one.span.end - one.span.start for one in openings)
    assert longest <= A_CEILING // 1, "the opening exceeded one reading's share"
    assert longest > A_CEILING // 2, (
        "the opening is far under its share, so the bound was taken from something "
        "other than the ceiling over this call's own count of readings")


def test_a_unit_under_the_ceiling_still_travels_whole_and_mints_nothing(
        conn, tmp_path):
    """The control, and it is `104` §17.13's ruling rather than an edge case.

    A whole unit UNDER the ceiling goes to either target as itself. Minting an
    opening for it would spend the ceiling twice on one reading and would quietly
    narrow what the owner ruled may travel, so the producer's first refusal is that
    a reading the call can already carry needs no second copy of itself.
    """
    create_schema(conn)
    create_evidence_schema(conn)
    conn.executescript(SENSITIVITY_DDL)
    conn.executescript(BUDGET_DDL)
    set_ceiling(conn, DOSSIER_CEILING_KEY, A_CEILING)

    short = "Invoice total 42.00\nDue on receipt"
    body = short.encode()
    path = tmp_path / "short.pdf"
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename="short.pdf", normalized_filename="short.pdf",
        extension=".pdf", observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Bills", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    run_id = "run-short"
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    at = (Segment("page", 1),)
    record_text_unit(conn, TextUnit(run_id=run_id, container_path=at, text=short))
    page = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=short,
        location=Location("body", at, text_span=TextSpan(0, len(short))),
        occurrence_count=1, observed_at=CLOCK, reliability="possible", run_id=run_id)
    record_observation(conn, page)

    offered = releasable_excerpts(
        conn, evidence_refs=[page.observation_key], locality=CLOUD_LOCALITY)

    assert [one.observation_key for one in offered] == [page.observation_key], (
        "a unit under the ceiling must travel as itself, once")
