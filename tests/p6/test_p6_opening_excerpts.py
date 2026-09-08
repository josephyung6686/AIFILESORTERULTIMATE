# tests/p6/test_p6_opening_excerpts.py
"""`104` R-164 -- the excerpt `00`:186 asks for, minted so a page stops being a document.

`104` §16 traced one run stage by stage and found the evidence dying at RELEASE, not
at extraction: 199 files produced 18,489 text units and 3.3M characters, and the
model's median dossier body was 212 characters. For 23 labelled files the course code
was in the file's full extracted text and NOT in the dossier the model saw, and none
of the 23 was answered right; the two files that had it in the dossier both were.

The refusal doing that is correct and must not be weakened. SF-1 / `104` R-07: a
whole DOCX body once travelled span-less at 45,843 bytes, and `may_be_released`
refuses "a span-less observation whose value is at least as long as the unit standing
at its own path" for a cloud target ever since. The defect is that a PDF PAGE arrives
in that same shape -- one span-less ~1,500-character unit -- so a rule written to stop
a whole document refuses every page of every document.

`00`:186 says what to send instead, and it is not the page:

    "the engine should send only a compact dossier relevant to the current question:
    selected excerpts, redacted identifiers, candidate labels, non-sensitive metadata,
    and evidence references. It should not send full documents where a short heading
    or OCR excerpt is enough to resolve the question."

So this mints the excerpt: a reading over the OPENING of the unit, with a span of its
own inside it, on `104` R-135's minted-line pattern. The whole-unit refusal keeps
refusing the whole unit; the model gets sentences.

MEASURED BEFORE THIS WAS WRITTEN, offline through the real release path over the
lead's own 199-file run at `gt-w1bn` (commit d1a135e), own-file readings only:
a CLOUD target's median released body was 0 characters, and of the 129 files with
body readings 76 had none releasable. The same corpus and the same code at a LOCAL
target: median 106, and 12 of 129. R-159's ruling unstarved the local target; what
is left is entirely the cloud one.
"""
from __future__ import annotations

import json

from database_agent.budget import set_ceiling
from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import (
    is_derived, record_observation, record_run, record_text_unit,
)
from evidence_shape.text_units import TextUnit

from extractors.long_tail import POTENTIALLY_SENSITIVE, SENSITIVITY_DDL

from model_facts import (
    DOSSIER_CEILING_KEY, may_be_released, opening_excerpt_bound,
    ordered_releasable_observations, within_dossier_budget,
)
from privacy.vocabulary import CLOUD_LOCALITY

CLOCK = "2026-09-08T00:00:00Z"
LOCAL = "local"

#: This deployment's cap, `cli.FACT_CALL_MAX_RELEASED_OBSERVATIONS`. Spelled as a
#: number in the fixture and never imported: importing `cli` into a P6 test to read
#: twelve would import the composition root to assert arithmetic.
CAP = 12

#: A page in the shape every text extractor writes one: several lines, no blank line
#: between them, and one span-less `body` observation over the whole of it.
PAGE = ("PHYS 1401 Homework 3, Spring 2026\n"
        "Answer all five questions and show your working. Credit is given for the\n"
        "method as well as the answer, so set out each step.\n"
        "Question 1. A block of mass m slides down a frictionless incline of angle t.\n"
        "Question 2. Two carts collide elastically on a level air track.\n"
        "Question 3. A pendulum of length L swings through a small angle.\n")

A_FOLDER = "/Users/joseph/Documents/Courses/PHYS 1401"


def _corpus(conn, tmp_path, *, ceiling=4_000, text=PAGE):
    """One coursework file: a folder-path reading and a whole page, as r15 saw them."""
    create_schema(conn)
    create_evidence_schema(conn)
    conn.executescript(SENSITIVITY_DDL)
    if ceiling is not None:
        set_ceiling(conn, DOSSIER_CEILING_KEY, ceiling)
    body = text.encode()
    path = tmp_path / "HW 3.pdf"
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename="HW 3.pdf", normalized_filename="hw 3.pdf",
        extension=".pdf", observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Courses", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    record_run(conn, ExtractionRun(
        run_id="run-hw", file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    page_at = (Segment("page", 1),)
    record_text_unit(conn, TextUnit(
        run_id="run-hw", container_path=page_at, text=text))

    def observe(raw, container, span, *, zone="body"):
        observation = Observation(
            file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
            extractor_version="1.0.0", source_type="text_document", raw_value=raw,
            location=Location(zone, container, text_span=span),
            occurrence_count=1, observed_at=CLOCK, reliability="possible",
            run_id="run-hw")
        record_observation(conn, observation)
        return observation

    folder = observe(A_FOLDER, (Segment("field", label="path"),), None, zone="path")
    page = observe(text, page_at, None)
    return file_id, content_hash, folder, page


def _offer(conn, file_id, content_hash, locality, limit=CAP):
    return ordered_releasable_observations(
        conn, file_id=file_id, content_hash=content_hash, locality=locality,
        limit=limit)


# --------------------------------------------------------------------------
# The bound, and where every character of it came from
# --------------------------------------------------------------------------

def test_the_bound_is_the_stored_ceiling_divided_by_the_call_s_own_cap(conn,
                                                                      tmp_path):
    """NOT A NUMBER CHOSEN HERE. `104` R-159 is an owner ruling that nothing be built
    on an invented length, so both operands are already stored: the ceiling is P1's
    `model.max_dossier_tokens_per_call`, read from `budget_ceilings`, and the cap is
    the `limit` the caller was already going to spend
    (`cli.FACT_CALL_MAX_RELEASED_OBSERVATIONS`). The quotient is the share of one
    call one reading may take if the call is to carry its full complement of them --
    which is the same sentence as "twelve of these fit under the ceiling".
    """
    _corpus(conn, tmp_path, ceiling=4_000)

    assert opening_excerpt_bound(conn, limit=CAP) == 4_000 // CAP


def test_a_deployment_that_stores_no_ceiling_mints_nothing(conn, tmp_path):
    """No stored bound, no excerpt -- never a bound invented to stand in for one."""
    file_id, content_hash, _folder, _page = _corpus(conn, tmp_path, ceiling=None)

    assert opening_excerpt_bound(conn, limit=CAP) is None
    assert [one.location.text_span
            for one in _offer(conn, file_id, content_hash, CLOUD_LOCALITY)] == []


# --------------------------------------------------------------------------
# The excerpt itself
# --------------------------------------------------------------------------

def test_a_page_refused_as_a_whole_unit_is_offered_to_the_cloud_as_an_opening(
        conn, tmp_path):
    """The measurement in this module's docstring, as one file.

    Before: a cloud call over this corpus offered nothing from the body at all -- the
    page is refused as a whole unit and the folder path is refused as an always-local
    zone, so the model was shown the file's extension and its MIME type. After: it is
    offered the opening of the page, with a span, and the page itself is still
    refused.
    """
    file_id, content_hash, _folder, page = _corpus(conn, tmp_path)

    offered = _offer(conn, file_id, content_hash, CLOUD_LOCALITY)

    assert [one.raw_value for one in offered] != []
    excerpt, = offered
    assert excerpt.observation_key != page.observation_key
    assert excerpt.location.text_span.start == 0
    assert 0 < excerpt.location.text_span.end < len(PAGE)
    assert excerpt.raw_value == PAGE[:excerpt.location.text_span.end]
    # And the sentences are actually there, which is the whole reason this exists.
    assert "PHYS 1401" in excerpt.raw_value


def test_the_excerpt_fits_the_share_of_the_call_the_bound_gave_it(conn, tmp_path):
    """A full complement of these has to fit the ceiling the gate is about to
    measure, or the fix trades a starved dossier for a `dossier_over_budget`
    denial."""
    file_id, content_hash, _folder, _page = _corpus(conn, tmp_path)

    excerpt, = _offer(conn, file_id, content_hash, CLOUD_LOCALITY)

    assert len(excerpt.raw_value) <= opening_excerpt_bound(conn, limit=CAP)
    assert len(excerpt.raw_value) * CAP <= 4_000


def test_the_excerpt_is_releasable_and_the_whole_page_is_still_not(conn, tmp_path):
    """SF-1 / `104` R-07 is not weakened by a character. The rule that refuses a
    span-less reading covering the whole of its unit answers exactly as it did; what
    changed is that there is now something else to offer."""
    file_id, content_hash, _folder, page = _corpus(conn, tmp_path)
    excerpt, = _offer(conn, file_id, content_hash, CLOUD_LOCALITY)

    assert may_be_released(conn, excerpt, sensitive=frozenset(),
                           locality=CLOUD_LOCALITY)
    assert not may_be_released(conn, page, sensitive=frozenset(),
                               locality=CLOUD_LOCALITY)


def test_a_local_target_still_gets_the_whole_unit_and_no_second_copy(conn,
                                                                    tmp_path):
    """`104` R-159's ruling is untouched and is not paid for twice. A local model may
    be shown the whole page within the ceiling, so an excerpt beside it would be the
    same characters spending the ceiling a second time."""
    file_id, content_hash, _folder, page = _corpus(conn, tmp_path)

    offered = _offer(conn, file_id, content_hash, LOCAL)

    assert [one.observation_key for one in offered
            if one.location.zone == "body"] == [page.observation_key]


def test_an_excerpt_already_stored_yields_to_the_unit_it_was_cut_from(conn,
                                                                     tmp_path):
    """A minted excerpt is RECORDED, so it outlives the call that minted it.

    The corpus this measures was read for a cloud target and is then read again for a
    local one -- the state a deployment reaches by changing where its model runs, and
    the state the measurement script for this row reached within one process. A local
    target may be shown the whole unit (`104` R-159), so offering the page AND its own
    opening would be the same characters twice, the second copy spending a ceiling the
    ruling meant for the first.
    """
    file_id, content_hash, _folder, page = _corpus(conn, tmp_path)
    excerpt, = _offer(conn, file_id, content_hash, CLOUD_LOCALITY)
    assert conn.execute(
        "SELECT count(*) c FROM evidence WHERE observation_key = ?",
        (excerpt.observation_key,)).fetchone()["c"] == 1

    body = [one for one in _offer(conn, file_id, content_hash, LOCAL)
            if one.location.zone == "body"]

    assert [one.observation_key for one in body] == [page.observation_key]
    # And the cloud target still gets the excerpt and not the page.
    assert [one.observation_key
            for one in _offer(conn, file_id, content_hash, CLOUD_LOCALITY)] == [
        excerpt.observation_key]


def test_nothing_is_minted_over_an_always_local_zone(conn, tmp_path):
    """`104` R-159 released `path` and `ocr` to a LOCAL target and not to a cloud one,
    and `filename` to neither as an excerpt. An excerpt cut from one of those zones
    would be that ruling walked around by a producer, which is why the zone is asked
    before anything is cut and not after."""
    file_id, content_hash, folder, _page = _corpus(conn, tmp_path)

    offered = _offer(conn, file_id, content_hash, CLOUD_LOCALITY)

    assert all(one.location.zone != "path" for one in offered)
    assert A_FOLDER not in "".join(one.raw_value for one in offered)
    assert folder.observation_key not in {one.observation_key for one in offered}


def test_nothing_is_minted_over_a_reading_p5_signalled(conn, tmp_path):
    """The per-value signal refuses the WHOLE request, and a recognised human
    identifier is not a fact about where the value is going. Cutting the opening off
    a signalled reading would release the part of it P5 objected to."""
    file_id, content_hash, _folder, page = _corpus(conn, tmp_path)
    conn.execute(
        "INSERT INTO extraction_sensitivity_signal "
        "(run_id, observation_key, signal, basis, observed_at) "
        "VALUES (?, ?, ?, 'test', ?)",
        ("run-hw", page.observation_key, POTENTIALLY_SENSITIVE, CLOCK))

    assert _offer(conn, file_id, content_hash, CLOUD_LOCALITY) == ()


def test_the_excerpt_is_derived_and_is_not_evidence_about_the_file(conn, tmp_path):
    """`104` R-135's ruling, and this reading is the same kind of thing its minted
    line is: an addressable copy of text an earlier pass already stored, so that it
    can be cited. It says nothing new about what the file IS, and a rule pass or a
    recogniser that counted it would count the file's own words twice."""
    file_id, content_hash, _folder, _page = _corpus(conn, tmp_path)

    excerpt, = _offer(conn, file_id, content_hash, CLOUD_LOCALITY)

    assert is_derived(excerpt)


def test_minting_the_same_excerpt_twice_writes_one_row(conn, tmp_path):
    """The handle is content-addressed, so asking the same question twice finds the
    row the first ask wrote. A release path that grew the evidence table on every
    call would make `104` §8.5's replay disagree with itself."""
    file_id, content_hash, _folder, _page = _corpus(conn, tmp_path)
    first = _offer(conn, file_id, content_hash, CLOUD_LOCALITY)
    rows = conn.execute("SELECT count(*) c FROM evidence").fetchone()["c"]

    second = _offer(conn, file_id, content_hash, CLOUD_LOCALITY)

    assert [one.observation_key for one in second] == [
        one.observation_key for one in first]
    assert conn.execute("SELECT count(*) c FROM evidence").fetchone()["c"] == rows


def test_a_unit_no_longer_than_the_bound_gets_no_excerpt_and_keeps_its_answer(
        conn, tmp_path):
    """There is nothing shorter than the unit to cut, so the whole-unit rule keeps the
    answer it already had and this producer adds nothing to it.

    AND THAT LEAVES A RESIDUAL, recorded here rather than in a comment. `104` R-152
    exempted a whole LINE unit and a whole HEADING unit from the document rule, but in
    the SPAN-BEARING arm: `released_whole_excerpt_unit` is asked of a reading that has
    a span. A short page whose reading is SPAN-LESS -- one line of extracted text with
    no span over it -- is still refused to a cloud target, and an excerpt cannot help
    it because any excerpt of it would be shorter than the words it already has.
    Closing that is a change to SF-1's own wording and is not R-164's to make.
    """
    file_id, content_hash, _folder, page = _corpus(
        conn, tmp_path, text="Homework 3 for PHYS 1401")

    assert _offer(conn, file_id, content_hash, CLOUD_LOCALITY) == ()
    assert not may_be_released(conn, page, sensitive=frozenset(),
                               locality=CLOUD_LOCALITY)
    # And a local target, which R-159 ruled may see the unit, still does.
    assert [one.observation_key
            for one in _offer(conn, file_id, content_hash, LOCAL)
            if one.location.zone == "body"] == [page.observation_key]


# --------------------------------------------------------------------------
# The bound the excerpts are spent under
# --------------------------------------------------------------------------

def test_a_cloud_call_is_bounded_by_the_ceiling_as_well_as_by_the_count(conn,
                                                                       tmp_path):
    """The half of `104` R-159's fill that has to move now, and only now.

    R-159 left a cloud call bound by the count alone, and said so in its own words:
    the ceiling was slack because no page could be released, so twelve readings were
    always small. Once each of the twelve may be an excerpt, a count stops being an
    honest bound on characters -- which is R-159's OWN argument, made about a local
    target because that is where the ruling made pages releasable first.

    The gate already refuses an over-ceiling dossier (`dossier_over_budget`, 2 files
    on the corpus at `gt-w1bn`). Applying the same ceiling before the door turns a
    refused CALL into a shorter one, which is `104` R-07's rule that one question has
    one answer.
    """
    readings = [_Reading(f"r{n}", 100) for n in range(20)]

    taken = within_dossier_budget(readings, limit=CAP, locality=CLOUD_LOCALITY,
                                  ceiling=550)

    assert taken == tuple(readings[:5])


def test_the_count_still_binds_a_cloud_call_when_the_ceiling_is_slack(conn,
                                                                     tmp_path):
    """And the cap is NOT replaced. §8.4's "data-minimizing" is a count as well as a
    length, and `104` R-159 ruled the cloud restrictions stand for a cloud target."""
    readings = [_Reading(f"r{n}", 10) for n in range(20)]

    taken = within_dossier_budget(readings, limit=CAP, locality=CLOUD_LOCALITY,
                                  ceiling=1_000_000)

    assert taken == tuple(readings[:CAP])


class _Reading:
    """Just the `raw_value` `within_dossier_budget` measures, as `104` R-159's own
    budget tests build it."""

    def __init__(self, name, length):
        self.name = name
        self.raw_value = "x" * length

    def __repr__(self):
        return f"<{self.name}:{len(self.raw_value)}>"
