# tests/p6/test_p6_release_locality.py
"""`104` R-159 -- whose target the release rules were ever about, at site A's builder.

`00`:186 puts paths, complete extracted text and OCR output under "should remain
local", and says that *"when a cloud model is used"* the engine sends "selected
excerpts" rather than full documents. That is one sentence about a CLOUD destination.
Until 8 Sep 2026 `model_facts.may_be_released` applied it to every destination, and
the gate's OTHER always-local rule -- `105` §13.3's privacy CLASS, cloud-only since
`104` R-89 -- disagreed with it inside the same door.

Measured on r15, 199 files, a local model: 54 files had body readings and NOT ONE was
releasable; the median file was shown 109 characters of its own text under a
4,000-character ceiling; 20 of the 43 labelled coursework files carried their course
code only in the person's own folder path; 29 OCR runs were shown to nobody. The
owner ruled §15.4 item 14 the first way: a local model may be shown a whole text
unit, the folder path and OCR text, within the dossier ceiling.

The DOOR's half of the ruling is `tests/p7/test_p7_always_local_zone.py` and
`tests/p7/test_p7_whole_document.py`, which drive `Gate.release` directly. This file
is the BUILDER's half -- the same refusals asked a step early so a call is never
built rather than built and denied -- plus the ordering and the fill that spend what
the ruling opened.

Every test here is a PAIR or a walk over `LOCALITIES` where the rule divides, because
"this now depends on the target" is a claim about a difference and an assertion about
one half of it would not make that claim.
"""
from __future__ import annotations

import json

from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_observation, record_run, record_text_unit
from evidence_shape.text_units import TextUnit

from extractors.long_tail import SENSITIVITY_DDL

from model_facts import (
    document_order, may_be_released, ordered_releasable_observations,
    releasable_observations, within_dossier_budget,
)
from privacy.vocabulary import CLOUD_LOCALITY, LOCALITIES

CLOCK = "2026-09-08T00:00:00Z"
LOCAL = "local"

#: The shape `extractors/filesystem.py` writes for every indexed file: the parent
#: directory, span-less, in the `path` zone. It is the reading 20 of r15's 43
#: labelled coursework files carried their course code in and nothing else did.
A_FOLDER = "/Users/joseph/Documents/Courses/PHYS 1401"

#: A page, and the whole of one text unit. Every text extractor emits this shape --
#: one span-less body observation over each page or paragraph -- which is why the
#: whole-unit rule refused the entire body of every document in the corpus.
A_PAGE = ("Homework 3 for PHYS 1401, Spring 2026.\n"
          "Answer all five questions and show your working.")

#: A short reading of the same document that is not the whole of anything.
A_HEADING = "Homework 3"


def _corpus(conn, tmp_path):
    """One coursework file: a folder-path reading, a heading, and a whole page."""
    create_schema(conn)
    create_evidence_schema(conn)
    # P5's per-value signal table, created EMPTY and created visibly: the release
    # path reads it for every candidate, so "this fixture signals nothing" is
    # written here rather than being an absence that happens to pass. `104` R-161
    # is the row that says nothing would signal a text document even if it were
    # populated.
    conn.executescript(SENSITIVITY_DDL)
    body = A_PAGE.encode()
    path = tmp_path / "HW 3.pdf"
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename="HW 3.pdf", normalized_filename="hw 3.pdf",
        extension=".pdf", observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Courses", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    run_id = "run-hw"
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))

    page_at = (Segment("page", 1),)
    record_text_unit(conn, TextUnit(
        run_id=run_id, container_path=page_at, text=A_PAGE))

    def observe(raw, container, span, *, zone="body"):
        observation = Observation(
            file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
            extractor_version="1.0.0", source_type="text_document", raw_value=raw,
            location=Location(zone, container, text_span=span),
            occurrence_count=1, observed_at=CLOCK, reliability="possible",
            run_id=run_id)
        record_observation(conn, observation)
        return observation

    # Span-less and with no unit at its own path, which is the filesystem
    # extractor's own shape: there is nothing for it to be the whole OF, so only
    # the zone rule ever refused it.
    folder = observe(A_FOLDER, (Segment("field", label="path"),), None, zone="path")
    heading = observe(A_HEADING, page_at, TextSpan(0, len(A_HEADING)))
    # Span-less over a unit it covers entirely: `items.is_whole_document`'s second
    # shape, and the one every page of every PDF in the corpus arrives in.
    page = observe(A_PAGE, page_at, None)
    return file_id, content_hash, folder, heading, page


def _released(conn, observation, locality):
    return may_be_released(conn, observation, sensitive=frozenset(),
                           locality=locality)


# --------------------------------------------------------------------------
# may_be_released: the two arms the ruling divides, and the two it does not
# --------------------------------------------------------------------------

def test_a_path_zone_reading_is_released_to_a_local_target_only(conn, tmp_path):
    """THE PAIR on the zone the ruling names first.

    "The person's folder path" is the ruling's own phrase, and this is the reading
    it is about: `extractors/filesystem.py` writes one per indexed file, span-less,
    carrying the parent directory. On r15 that was where 20 of the 43 labelled
    coursework files kept their course code and nowhere else -- so the model was
    asked what course a file belonged to while the answer sat in a reading the
    builder refused to offer.

    SABOTAGE: drop the `RELEASED_TO_A_LOCAL_TARGET` half of the zone condition in
    `may_be_released` and the local half goes red; drop the `cloud or` half and the
    cloud half does.
    """
    _file_id, _hash, folder, _heading, _page = _corpus(conn, tmp_path)
    assert _released(conn, folder, CLOUD_LOCALITY) is False
    assert _released(conn, folder, LOCAL) is True


def test_a_whole_page_is_released_to_a_local_target_only(conn, tmp_path):
    """THE PAIR on the whole-unit rule, in the span-less shape the corpus is in.

    §8.4's "should not send full documents where a short heading or OCR excerpt is
    enough" sits under `00`:186's *"when a cloud model is used"*. Every text
    extractor emits one span-less observation over each page or paragraph, so this
    single arm refused the body of all 199 files to a local model that never sends
    anything anywhere.

    What bounds the local branch instead is the ceiling, and that is
    `within_dossier_budget`'s tests below rather than a length written here.
    """
    _file_id, _hash, _folder, _heading, page = _corpus(conn, tmp_path)
    assert _released(conn, page, CLOUD_LOCALITY) is False
    assert _released(conn, page, LOCAL) is True


def test_a_short_reading_is_released_to_either_target(conn, tmp_path):
    """The control that makes the two pairs above discriminating.

    A rule that had simply stopped checking would pass both of them. This is the
    reading that was ALWAYS releasable -- a heading, §8.4's own example of what to
    send instead of a document -- and it must go on being released to both.
    """
    _file_id, _hash, _folder, heading, _page = _corpus(conn, tmp_path)
    for locality in LOCALITIES:
        assert _released(conn, heading, locality) is True, locality


def test_a_p5_signalled_reading_is_refused_to_every_target(conn, tmp_path):
    """The arm the ruling did NOT divide, walked over both localities.

    P5's per-value signal says a human identifier was recognised in that value,
    which is not a fact about where the value is going. `104` R-159 divided the zone
    and the whole-unit arms and left this one, the protected arm, the unratified
    arm and the suspension arm alone.
    """
    _file_id, _hash, _folder, heading, _page = _corpus(conn, tmp_path)
    for locality in LOCALITIES:
        assert may_be_released(
            conn, heading, sensitive=frozenset({heading.observation_key}),
            locality=locality) is False, locality


def test_a_locality_outside_the_closed_set_is_refused_not_read_as_local(
        conn, tmp_path):
    """SPEC §1: a value outside a closed set is a load error, not a fallback.

    Both arms test `== CLOUD_LOCALITY`, so `"Cloud"` or `""` would take the LOCAL
    branch and release the folder. The guard is what makes the fail direction closed
    instead of open, and it is asserted rather than assumed.
    """
    import pytest

    _file_id, _hash, folder, _heading, _page = _corpus(conn, tmp_path)
    for outside in ("Cloud", "CLOUD", "remote", ""):
        with pytest.raises(ValueError):
            _released(conn, folder, outside)


# --------------------------------------------------------------------------
# The order: the document's own, in place of the hash
# --------------------------------------------------------------------------

def _paged_corpus(conn, tmp_path, pages):
    """One file with a body reading on each of `pages`, recorded out of order."""
    create_schema(conn)
    create_evidence_schema(conn)
    conn.executescript(SENSITIVITY_DDL)
    path = tmp_path / "Lecture notes.pdf"
    path.write_bytes(b"%PDF-1.4 fixture")
    file_id = record_file(
        conn, path, filename="Lecture notes.pdf",
        normalized_filename="lecture notes.pdf", extension=".pdf",
        observed_size=16, observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context="Courses", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    run_id = "run-notes"
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    made = {}
    for page, text in pages:
        at = (Segment("page", page),)
        record_text_unit(conn, TextUnit(run_id=run_id, container_path=at,
                                        text=text + " (the rest of the page)"))
        observation = Observation(
            file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
            extractor_version="1.0.0", source_type="text_document", raw_value=text,
            location=Location("body", at, text_span=TextSpan(0, len(text))),
            occurrence_count=1, observed_at=CLOCK, reliability="possible",
            run_id=run_id)
        record_observation(conn, observation)
        made[page] = observation
    return file_id, content_hash, made


def test_the_readings_come_back_in_the_documents_own_order(conn, tmp_path):
    """`104` R-159: page 1 before page 7, whatever the digests say.

    An `observation_key` is `sha256(content_hash | extractor | locator | raw_value)`,
    and it used to be the ONLY tie-break inside a zone. So which twelve of a PDF's
    forty body pages reached a dossier was decided by which digests happened to sort
    lowest -- a reading of a hash rather than of the document.

    The pages are recorded here in a deliberately scrambled order, so a function that
    simply preserved insertion order would fail this too.

    SABOTAGE: remove `document_order` from the sort key and this goes red for the
    seeds below; the hash order for this fixture is asserted to differ, so the test
    cannot pass by coincidence.
    """
    pages = [(7, "Chapter four"), (1, "Chapter one"), (12, "Chapter six"),
             (3, "Chapter two")]
    _file_id, content_hash, made = _paged_corpus(conn, tmp_path, pages)

    offered = ordered_releasable_observations(
        conn, file_id=_file_id, content_hash=content_hash, locality=LOCAL)

    assert [document_order(one)[0] for one in offered] == [1, 3, 7, 12]
    # And the old term would have answered differently, which is what makes this a
    # test of the change rather than of an accident.
    by_hash = sorted(made.values(), key=lambda one: one.observation_key)
    assert [document_order(one)[0] for one in by_hash] != [1, 3, 7, 12], (
        "this fixture's digests happen to sort into document order, so it cannot "
        "tell the two orderings apart; change a page's text")


def test_a_segment_with_no_index_contributes_zero_and_orders_before_page_one(
        conn, tmp_path):
    """§2.3's sheet and §2.8's field are addressed by a LABEL and carry no index.

    `Segment.__post_init__` refuses an index on those kinds, so "missing index" is a
    real state of the vocabulary and not a defensive branch. Zero is the honest
    answer -- an address with no position is at the start -- and it is spelled rather
    than left to `None`, which would raise on comparison.
    """
    labelled = Location("metadata", (Segment(kind="field", label="Author"),))
    numbered = Location("body", (Segment(kind="page", index=1),))

    class _At:
        def __init__(self, location):
            self.location = location

    assert document_order(_At(labelled)) == (0,)
    assert document_order(_At(numbered)) == (1,)
    assert document_order(_At(labelled)) < document_order(_At(numbered))


# --------------------------------------------------------------------------
# The bound: a count for a cloud call, the ceiling for a local one
# --------------------------------------------------------------------------

class _Reading:
    """Just the `raw_value` `within_dossier_budget` measures. The function reads
    nothing else, and a fixture that built P4 rows would be asserting the store."""

    def __init__(self, name, length):
        self.name = name
        self.raw_value = "x" * length

    def __repr__(self):
        return f"<{self.name}:{len(self.raw_value)}>"


def test_a_cloud_call_keeps_the_count_cap_and_the_ceiling_is_slack():
    """The half of the ruling that changed nothing.

    §8.4 asks for "a compact dossier ... selected excerpts" and states no number;
    `cli.FACT_CALL_MAX_RELEASED_OBSERVATIONS` is where this deployment chooses one,
    and R-159 does not touch it. Twelve readings come back however much room the
    ceiling has left.
    """
    readings = [_Reading(f"r{n}", 10) for n in range(20)]
    taken = within_dossier_budget(readings, limit=12, locality=CLOUD_LOCALITY,
                                  ceiling=1_000_000)
    assert taken == tuple(readings[:12])


def test_a_local_call_ignores_the_count_and_stops_at_the_ceiling():
    """The half that changed. Twenty readings, no count cap, and the ceiling binds.

    Once a whole page is releasable a COUNT stops being an honest bound on how much
    of a document leaves: twelve spreadsheet cells are a few hundred characters and
    twelve PDF pages are twenty thousand.
    """
    readings = [_Reading(f"r{n}", 100) for n in range(20)]
    taken = within_dossier_budget(readings, limit=12, locality=LOCAL, ceiling=550)
    assert taken == tuple(readings[:5])
    assert sum(len(one.raw_value) for one in taken) <= 550


def test_a_reading_that_does_not_fit_is_skipped_and_the_walk_continues():
    """`104` R-159's own sentence, and `104` R-164 is why it matters.

    A plain-text document is still one text unit (R-164, open), so a 39,000-character
    `.txt` reading fits no ceiling there has ever been. Stopping at the first
    over-long reading would cost that file every smaller reading behind it -- which
    is the state the ruling was made to end, not one to re-create with a `break`.

    SABOTAGE: turn the `continue` in `within_dossier_budget` into a `break` and this
    goes red while the test above it still passes.
    """
    small_one = _Reading("small-1", 40)
    enormous = _Reading("enormous", 5_000)
    small_two = _Reading("small-2", 30)
    taken = within_dossier_budget(
        [small_one, enormous, small_two], limit=12, locality=LOCAL, ceiling=100)
    assert taken == (small_one, small_two)


def test_the_order_is_the_callers_and_the_fill_does_not_re_sort():
    """What fits is not "the ones that fit best".

    Re-ordering by length here would be this function choosing which part of a
    document a person reads first, which is exactly what `document_order` exists to
    stop `observation_key` doing.
    """
    readings = [_Reading("first", 60), _Reading("second", 20),
                _Reading("third", 20)]
    taken = within_dossier_budget(readings, limit=12, locality=LOCAL, ceiling=100)
    assert [one.name for one in taken] == ["first", "second", "third"]


def test_a_zero_remainder_takes_nothing_rather_than_taking_one_anyway():
    """The state `fact_call_stage` reaches when the anchor context has spent the
    whole ceiling. Taking a reading anyway would breach the ceiling the ladder is
    about to report as met, which is the disagreement `104` R-159 closed."""
    readings = [_Reading("only", 1)]
    assert within_dossier_budget(
        readings, limit=12, locality=LOCAL, ceiling=0) == ()


def test_the_composed_function_offers_the_document_in_order_under_the_ceiling(
        conn, tmp_path):
    """`releasable_observations` is the two halves composed, and its callers still
    ask it as one question. The pages are scrambled on the way in and the ceiling
    admits three of the four."""
    pages = [(7, "g" * 40), (1, "a" * 40), (12, "l" * 40), (3, "c" * 40)]
    file_id, content_hash, _made = _paged_corpus(conn, tmp_path, pages)

    offered = releasable_observations(
        conn, file_id=file_id, content_hash=content_hash, limit=12,
        locality=LOCAL, ceiling=120)

    assert [document_order(one)[0] for one in offered] == [1, 3, 7]
