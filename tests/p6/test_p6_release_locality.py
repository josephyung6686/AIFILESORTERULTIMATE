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

Every test here was a PAIR or a walk over `LOCALITIES` where the rule divided,
because "this now depends on the target" is a claim about a difference and an
assertion about one half of it would not make that claim.

**SUPERSESSION, 9 Sep 2026, `104` §17.13 (the owner's ruling).** Asked §17.6's
question again with the code's answer in front of them -- a cloud call was shown zero
characters of body on the measured corpus -- the owner ruled item 14 the rest of the
way: *"honestly now let's just do cloud run"*, a cloud model shown a whole text unit,
the person's folder path and OCR text within the same ceiling. So the two arms R-159
divided divide by nothing now, and the two PAIRS below are WALKS with the same answer
on both localities. That is a weaker shape of assertion, so what keeps them
discriminating is spelled rather than assumed: the `filename` zone, the half of the
partition §17.13 did not move, is asserted refused in the same walk, and the P5 arm
below is asserted refused on both. `locality` itself stays required and validated,
because the gate's privacy-CLASS rule and the per-file route (R-170) still divide by
it -- which FILE may reach a cloud target is decided before any of this is asked.
"""
from __future__ import annotations

import json
from dataclasses import replace

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
    document_order, fill_reserving_top_reading, may_be_released,
    ordered_releasable_observations, releasable_observations,
    released_wire_cost, within_dossier_budget, zone_evidence_counts,
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
# may_be_released: the arms R-159 divided, and what is left of the division
# --------------------------------------------------------------------------

def test_a_path_zone_reading_is_released_to_every_target(conn, tmp_path):
    """THE WALK on the zone the ruling names first, and the zone it left behind.

    "The person's folder path" is the ruling's own phrase, and this is the reading
    it is about: `extractors/filesystem.py` writes one per indexed file, span-less,
    carrying the parent directory. On r15 that was where 20 of the 43 labelled
    coursework files kept their course code and nowhere else -- so the model was
    asked what course a file belonged to while the answer sat in a reading the
    builder refused to offer.

    **This was a PAIR until 9 Sep 2026.** R-159 released the path to a LOCAL target
    and held the cloud refusal, so the assertion was `False` for the cloud and `True`
    for the local. `104` §17.13 extends item 14 to the cloud -- the same folder path,
    within the same ceiling -- and R-82 is signed in the same build so the consent
    text names the folder labels before they cross. The zone arm therefore reads
    `ALWAYS_LOCAL_ZONES_FOR_EVERY_TARGET`, which `path` is not in, and the answer is
    the same on both localities.

    **The `filename` half is what keeps the walk discriminating.** An arm that had
    simply stopped asking about zones would pass the first assertion below and
    release the filename with it. `filename` is the one member of `ALWAYS_LOCAL_ZONES`
    §17.13 did not move, for a reason that was never about the destination: §7.7's
    name has its own door, `items.Filename` under `allow_unratified`, where §7.3's
    protected-records ban also applies, and a `filename`-zone excerpt would bypass
    both while releasing nothing the door does not already carry.

    The constructed reading is not recorded, and does not need to be: the zone arm
    answers off `observation.location` and returns before the store is read at all.

    SABOTAGE: widen the zone arm to `ALWAYS_LOCAL_ZONES` and the path assertions go
    red; delete the zone arm and the filename assertions do.
    """
    _file_id, _hash, folder, _heading, _page = _corpus(conn, tmp_path)
    named = replace(
        folder, raw_value="HW 3.pdf",
        location=Location("filename", (Segment("field", label="filename"),)))
    # A WALK MAKES THE RULING'S CLAIM ONLY IF THE CLOUD IS IN IT. The pair this
    # replaced said `cloud` out loud; a walk over a set that had lost its cloud
    # member would pass while asserting the opposite of what §17.13 decided.
    assert CLOUD_LOCALITY in LOCALITIES
    for locality in LOCALITIES:
        assert _released(conn, folder, locality) is True, locality
        assert _released(conn, named, locality) is False, locality


def test_a_whole_page_is_released_to_every_target(conn, tmp_path):
    """THE WALK on the whole-unit rule, in the span-less shape the corpus is in.

    §8.4's "should not send full documents where a short heading or OCR excerpt is
    enough" sat under `00`:186's *"when a cloud model is used"*, and R-159 read that
    sentence literally. Every text extractor emits one span-less observation over
    each page or paragraph, so this single arm refused the body of all 199 files --
    to a local model that never sends anything anywhere until 8 Sep, and to a cloud
    one until 9 Sep.

    **`104` §17.13 amends the sentence for this deployment**, which is the honest
    description of what the ruling did: a cloud model may be shown a whole text unit
    within the same ceiling, so `may_be_released` has no whole-unit arm left on
    either target and this assertion is the same on both.

    THE LENGTH RULE DID NOT GO AWAY; IT MOVED, and this test asserts none of it. What
    bounds a whole unit now is the ceiling alone, in two places: `within_dossier_
    budget` below skips a reading that does not fit, and `items.check_item` refuses a
    whole unit longer than P1's STORED ceiling at the door. Neither is a number this
    file could write, which is why what is asserted here is only that the
    zone-and-coverage refusal is gone.

    A `may_be_released` that had stopped answering at all would pass this. The two
    tests below are what stops that reading: the short reading must still be
    released, and the P5-signalled one must still be refused.
    """
    _file_id, _hash, _folder, _heading, page = _corpus(conn, tmp_path)
    assert CLOUD_LOCALITY in LOCALITIES
    for locality in LOCALITIES:
        assert _released(conn, page, locality) is True, locality


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

    **The reason moved on 9 Sep 2026 and got stronger.** Until `104` §17.13 two arms
    of this function tested `== CLOUD_LOCALITY`, so `"Cloud"` or `""` would take the
    LOCAL branch and release the folder -- the guard caught a value the arms would
    have misread. §17.13 removed both arms, so `_check_locality` is now called for
    its raise alone and its answer is discarded: NOTHING else in this function reads
    `locality`. That is exactly the shape a later reader deletes as dead code, and
    deleting it would let a mistyped locality through to the two places that still
    divide by one -- the gate's privacy-CLASS refusal and R-170's per-file route,
    both of which read an unrecognised value as local. So the guard is asserted here
    rather than assumed, and this test is now the only thing holding it.
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
        # `104` R-164 gave this function the cap the caller was already going to
        # spend, so that `opening_excerpt_bound` can derive an excerpt length from
        # it rather than invent one. It still caps nothing here; these four short
        # pages are longer than no bound and none of them is cut.
        conn, file_id=_file_id, content_hash=content_hash, locality=LOCAL, limit=12)

    assert [document_order(one)[0] for one in offered] == [1, 3, 7, 12]
    # And the old term would have answered differently, which is what makes this a
    # test of the change rather than of an accident.
    by_hash = sorted(made.values(), key=lambda one: one.observation_key)
    assert [document_order(one)[0] for one in by_hash] != [1, 3, 7, 12], (
        "this fixture's digests happen to sort into document order, so it cannot "
        "tell the two orderings apart; change a page's text")


def test_a_segment_with_no_index_contributes_zero_and_is_still_comparable(
        conn, tmp_path):
    """§2.3's sheet and §2.8's field are addressed by a LABEL and carry no index.

    `Segment.__post_init__` refuses an index on those kinds, so "missing index" is a
    real state of the vocabulary and not a defensive branch. Zero is the honest
    answer -- an address with no position is at the start -- and it is spelled rather
    than left to `None`, which would raise the moment the sort compared two of them.

    THE COMPARISON BELOW IS THE POINT AND THE ORDERING IS NOT. `zone_rank` runs
    first, so the sort never actually weighs a `metadata` field against a `body`
    page; what it does need is that every address yields a tuple of ints, which is
    what a label-only segment would break. The two zones here are named only because
    that is where the two segment kinds occur.
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
# The bound: the ceiling, for either target (`104` §17.13 retired the count)
# --------------------------------------------------------------------------

class _Reading:
    """What `within_dossier_budget` measures, and nothing else: since `104` R-174
    that is the reading's bytes on the wire, which `released_wire_cost` spells from
    the key, the location and the raw value. A fixture that built P4 rows would be
    asserting the store."""

    def __init__(self, name, length):
        self.name = name
        self.observation_key = name
        self.raw_value = "x" * length
        self.location = Location("body", (), text_span=TextSpan(0, length))

    def __repr__(self):
        return f"<{self.name}:{len(self.raw_value)}>"


def test_a_cloud_call_is_bound_by_the_ceiling_alone_like_a_local_one():
    """`104` §17.13 (9 Sep 2026): the cloud is shown what the local model is shown,
    within the same ceiling, so the count cap R-159 kept for a cloud call is gone
    with the locality it divided by. Twenty readings under a slack ceiling all come
    back; `cli.FACT_CALL_MAX_RELEASED_OBSERVATIONS` is spent on the excerpt bound
    and on nothing else.
    """
    readings = [_Reading(f"r{n}", 10) for n in range(20)]
    # `104` §18.2 gap 5: the fill answers a `DossierFill` -- what it took AND what
    # the ceiling cut -- so the claim this test always made is now the `.taken` half,
    # and the other half is asserted beside it because a slack ceiling cutting
    # anything would be the same defect stated the other way round.
    fill = within_dossier_budget(readings, ceiling=1_000_000)
    assert fill.taken == tuple(readings)
    assert fill.dropped == ()
    assert fill.dropped_bytes == 0


def test_a_local_call_ignores_the_count_and_stops_at_the_ceiling():
    """The half that changed. Twenty readings, no count cap, and the ceiling binds.

    Once a whole page is releasable a COUNT stops being an honest bound on how much
    of a document leaves: twelve spreadsheet cells are a few hundred characters and
    twelve PDF pages are twenty thousand.
    """
    readings = [_Reading(f"r{n}", 100) for n in range(20)]
    # `104` R-174: the ceiling is spent in wire bytes, so "room for five" is five
    # readings' cost and not five hundred characters. Derived from the readings
    # rather than typed, and short of a sixth by one byte.
    ceiling = sum(released_wire_cost(one) for one in readings[:6]) - 1
    fill = within_dossier_budget(readings, ceiling=ceiling)
    assert fill.taken == tuple(readings[:5])
    assert sum(released_wire_cost(one) for one in fill.taken) <= ceiling
    # `104` §18.2 gap 5: the fifteen that did not fit are the CUT, and they are
    # returned rather than dropped in silence. Every reading is in exactly one half,
    # which is what makes the two counts a complete account of the offer.
    assert fill.dropped == tuple(readings[5:])
    assert len(fill.taken) + len(fill.dropped) == len(readings)


def test_a_reading_that_does_not_fit_is_skipped_and_the_walk_continues():
    """`104` R-159's own sentence, and `104` R-164 is why it matters.

    A plain-text document is still one text unit (R-164, open), so a 39,000-character
    `.txt` reading fits no ceiling there has ever been. Stopping at the first
    over-long reading would cost that file every smaller reading behind it -- which
    is the state the ruling was made to end, not one to re-create with a `break`.

    SABOTAGE: turn the `continue` in `within_dossier_budget` into a `break` and this
    goes red while the test above it still passes.

    SABOTAGE (`104` §18.2 gap 5): drop the `dropped.append` before the `continue` and
    the last two assertions go red -- the walk still carries the right readings and
    the run can no longer say what it left behind, which is the silence the gap is
    about.
    """
    small_one = _Reading("small-1", 40)
    enormous = _Reading("enormous", 5_000)
    small_two = _Reading("small-2", 30)
    fill = within_dossier_budget(
        [small_one, enormous, small_two],
        ceiling=released_wire_cost(small_one) + released_wire_cost(small_two))
    assert fill.taken == (small_one, small_two)
    assert fill.dropped == (enormous,)
    assert fill.dropped_bytes == released_wire_cost(enormous)


def test_the_order_is_the_callers_and_the_fill_does_not_re_sort():
    """What fits is not "the ones that fit best".

    Re-ordering by length here would be this function choosing which part of a
    document a person reads first, which is exactly what `document_order` exists to
    stop `observation_key` doing.
    """
    readings = [_Reading("first", 60), _Reading("second", 20),
                _Reading("third", 20)]
    fill = within_dossier_budget(
        readings, ceiling=sum(released_wire_cost(one) for one in readings))
    assert [one.name for one in fill.taken] == ["first", "second", "third"]


def test_a_zero_remainder_takes_nothing_rather_than_taking_one_anyway():
    """The state `fact_call_stage` reaches when the anchor context has spent the
    whole ceiling. Taking a reading anyway would breach the ceiling the ladder is
    about to report as met, which is the disagreement `104` R-159 closed.

    `104` §18.2 gap 5: and the reading is in the CUT rather than nowhere. A zero
    remainder is the state where the whole of a file's own evidence is lost to the
    anchor context, which is precisely the state a person most needs told about.
    """
    readings = [_Reading("only", 1)]
    fill = within_dossier_budget(readings, ceiling=0)
    assert fill.taken == ()
    assert fill.dropped == tuple(readings)


def test_many_tiny_readings_are_bounded_by_their_bytes_on_the_wire():
    """`104` R-174, the r18 shape: a spreadsheet's 509 cells, ~30 characters each.

    Under a character count all of them fit a 4,000-character ceiling and their
    envelopes made a 241 KB payload; under the wire cost the same ceiling admits as
    many as their whole bodies fit, and the bytes the model is shown stay under it.

    SABOTAGE: make `within_dossier_budget` measure `len(raw_value)` again and the
    second assertion goes red -- every reading fits, and the sum of their wire
    costs is many times the ceiling.
    """
    readings = [_Reading(f"cell-{n}", 30) for n in range(509)]
    ceiling = 4_000
    fill = within_dossier_budget(readings, ceiling=ceiling)
    taken = fill.taken
    assert 0 < len(taken) < len(readings)
    assert sum(released_wire_cost(one) for one in taken) <= ceiling
    assert taken == tuple(readings[:len(taken)])
    # `104` §18.2 gap 5: this is the shape the cut was invented for. A spreadsheet
    # whose 509 cells become a handful of released readings is the file whose report
    # most needs to say how much was left out, and before the gap was closed the
    # screen said nothing at all.
    assert len(fill.dropped) == len(readings) - len(taken)
    assert fill.dropped_bytes > ceiling


def test_the_wire_cost_is_the_bytes_the_dossier_writes_for_the_reading():
    """The measure is taken off `dossier._released_body`, not re-spelled here: the
    address the gate would give the item, the handle at its wire length, the zone
    and the value. So the cost of a one-character reading is dominated by its
    envelope, and a reading's cost is never less than its value's characters."""
    one = _Reading("one", 1)
    long = _Reading("long", 300)
    assert released_wire_cost(one) > len(one.raw_value)
    # 299 characters more, and the address grows with the span's end as well.
    assert released_wire_cost(long) - released_wire_cost(one) >= 300 - 1


def test_the_composed_function_offers_the_document_in_order_under_the_ceiling(
        conn, tmp_path):
    """`releasable_observations` is the two halves composed, and its callers still
    ask it as one question. The pages are scrambled on the way in and the ceiling
    admits three of the four."""
    pages = [(7, "g" * 40), (1, "a" * 40), (12, "l" * 40), (3, "c" * 40)]
    file_id, content_hash, _made = _paged_corpus(conn, tmp_path, pages)

    # `104` R-174: room for three pages is three pages' bytes on the wire, read off
    # the unbounded offer rather than typed.
    in_order = ordered_releasable_observations(
        conn, file_id=file_id, content_hash=content_hash, locality=LOCAL,
        limit=12)
    room = sum(released_wire_cost(one) for one in in_order[:3])
    offered = releasable_observations(
        conn, file_id=file_id, content_hash=content_hash, limit=12,
        locality=LOCAL, ceiling=room)

    assert [document_order(one)[0] for one in offered] == [1, 3, 7]


# --------------------------------------------------------------------------
# `104` §18.2 gap 6: the order is measured, and no table decides it
# --------------------------------------------------------------------------

def _states_the_field(conn, *, file_id, content_hash, field, value, ref):
    """One fact of the store's own, citing one reading -- what the order is measured
    off. This is the shape `facts.rules` and `facts.direct` write, asked of the
    fixture directly so that a test about ORDER does not run a rule pass to get one.
    """
    from facts.cache import pass_cache_key
    from facts.file_facts import RULE, write_fact
    from facts.values import VALUE_ORIGINS, ensure_value

    value_id = ensure_value(conn, field_key=field, canonical_value=value,
                            first_evidence_ref=ref, origin=VALUE_ORIGINS[0])
    return write_fact(
        conn, file_id=file_id, content_hash=content_hash, field_key=field,
        value_id=value_id, reliability_state="validated", origin=RULE,
        evidence_refs=(ref,), active=True,
        cache_key=pass_cache_key(conn, file_id=file_id,
                                 content_hash=content_hash))


def _with_facts(conn):
    """P6's own tables, beside the fixture's P1 and P4 ones. `_corpus` does not
    create them because nothing it tested read a fact; the order does now."""
    from facts.fields import create_fields
    from facts.schema import create_facts_schema

    create_facts_schema(conn)
    create_fields(conn)


def _observe_extra(conn, file_id, content_hash, *, zone, raw, container):
    """One more reading of the same file version, in a zone `_corpus` does not
    produce. Written here rather than added to `_corpus` because every other test in
    this file asserts over the three readings that fixture holds.

    The unit is recorded beside it and is LONGER than the reading, because the
    whole-unit rule is asked of every candidate: a span covering the whole of its
    unit is refused and the reading would never reach the order this test is about.
    """
    record_text_unit(conn, TextUnit(
        run_id="run-hw", container_path=container,
        text=raw + " and the rest of the scanned page"))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location(zone, container, text_span=TextSpan(0, len(raw))),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id="run-hw")
    record_observation(conn, observation)
    return observation


def test_no_zone_table_stands_in_the_module_that_orders_the_dossier():
    """CONSTITUTION RULE ONE, pinned by introspection because prose cannot hold it.

    `104` §18.2 gap 6: `model_facts._ZONE_PREFERENCE` was six zone names typed in
    this product's own order -- title, heading, metadata, body, table, notes -- and
    `zone_rank` sent every zone outside the six, `ocr` and `path` among them, behind
    all six. That table decided which of a file's readings survived a capped dossier,
    which is hardcoded domain knowledge deciding what the model sees.

    The pin is over the SOURCE and not over any behaviour, because a second table
    would pass every behavioural test the day it was written and disagree with the
    measurement six months later -- which is exactly how this deployment came to hold
    two of them, `_ZONE_PREFERENCE` here and `cli.ZONE_WEIGHT` there, ranking the
    same fifteen zones differently. Any literal sequence or mapping in this module
    naming two or more of P4's zones is that table coming back, whatever it is
    called.

    SABOTAGE: put `_ZONE_PREFERENCE = ("title", "heading")` back into `model_facts`
    -- or any dict keyed on two zone names -- and this goes red while every other
    test in this file still passes.
    """
    import ast
    import inspect

    import model_facts
    from evidence_shape.vocabulary import ZONES

    def named_zones(node):
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            written = node.elts
        elif isinstance(node, ast.Dict):
            written = node.keys
        else:
            return set()
        return {one.value for one in written
                if isinstance(one, ast.Constant)
                and isinstance(one.value, str)} & set(ZONES)

    tables = [(node.lineno, sorted(named_zones(node)))
              for node in ast.walk(ast.parse(inspect.getsource(model_facts)))
              if len(named_zones(node)) >= 2]

    assert tables == [], (
        "a literal ordering of P4's zones is back in the module that decides what "
        "the model is shown; the order is measured, not typed")


def test_the_order_follows_the_zones_this_corpus_states_the_field_in(conn, tmp_path):
    """THE REPLACEMENT FOR THE TABLE: the corpus is asked, and it answers.

    `104` §18.2 gap 6. The offer is ordered for the fields the call is about to ask,
    and the first term is the count of readings this corpus's own recognisers have
    cited for those fields. Here one `subject` fact cites the file's HEADING, so
    `body` is where this corpus states a subject, and the body readings lead the
    offer -- ahead of the folder path, which the document's own order puts first (a
    label-only address stands at 0 and a page at 1, which is what the assertion
    before the fact says).

    Nothing about the readings changed between the two calls and no rule was added:
    the same three readings, the same file, the same call, one fact in the store.
    That is the whole claim -- what the model is shown first is a property of the
    corpus and not of a list in `model_facts`.

    SABOTAGE: make `ordered_releasable_observations` ignore its `fields` (or make
    `zone_evidence_counts` return `{}`) and the two orders become one, so the second
    assertion goes red while the first still passes.
    """
    _with_facts(conn)
    file_id, content_hash, folder, heading, page = _corpus(conn, tmp_path)

    def offer(fields):
        return [one.observation_key for one in ordered_releasable_observations(
            conn, file_id=file_id, content_hash=content_hash, locality=LOCAL,
            limit=12, fields=fields)]

    # NOTHING MEASURED: the document's own order, and the folder's address is first.
    assert offer(()) == [folder.observation_key, heading.observation_key,
                         page.observation_key]

    _states_the_field(conn, file_id=file_id, content_hash=content_hash,
                      field="subject", value="PHYS1401",
                      ref=heading.observation_key)

    # MEASURED: `body` is where this corpus states a subject, so the two body
    # readings come first and the path reading follows them.
    assert offer(("subject",)) == [heading.observation_key,
                                   page.observation_key, folder.observation_key]
    assert zone_evidence_counts(conn, fields=("subject",)) == {"body": 1}


def test_a_field_nobody_asked_about_orders_nothing(conn, tmp_path):
    """The measurement is per FIELD, so a fact about one field does not re-order the
    offer for a call asking another.

    `104` §18.2 gap 6's own sentence -- "a per-field zone preference" -- and the
    reason it has to be per field: `subject` is answered from folder paths and course
    codes, `work_type` from headings and filenames, and one order for both would be a
    smaller version of the table this replaced.

    SABOTAGE: drop the `field_key IN (...)` clause from `zone_evidence_counts` and
    the second assertion goes red, because the `subject` fact starts ordering a
    `work_type` call.
    """
    _with_facts(conn)
    file_id, content_hash, folder, heading, page = _corpus(conn, tmp_path)
    _states_the_field(conn, file_id=file_id, content_hash=content_hash,
                      field="subject", value="PHYS1401",
                      ref=heading.observation_key)

    def offer(fields):
        return [one.observation_key for one in ordered_releasable_observations(
            conn, file_id=file_id, content_hash=content_hash, locality=LOCAL,
            limit=12, fields=fields)]

    assert offer(("subject",))[0] == heading.observation_key
    assert offer(("work_type",)) == [folder.observation_key,
                                     heading.observation_key,
                                     page.observation_key]
    assert zone_evidence_counts(conn, fields=("work_type",)) == {}


def test_a_zone_no_fact_has_cited_is_not_sent_behind_every_other_one(conn, tmp_path):
    """`zone_rank`'s worst half, and the one `104` §17.13 had just made expensive.

    Every zone outside the six typed names scored `len(_ZONE_PREFERENCE)` -- WORSE
    than every named zone -- so `path` and `ocr`, opened to every target by §17.13
    days earlier, queued behind `notes` and `table`, zones no reader in this
    deployment produces. On the measured corpus the folder path was where 20 of 43
    labelled coursework files kept their course code and nowhere else, and a scanned
    page's only reading is `ocr`.

    An unmeasured zone now scores zero, which ties it with every other unmeasured
    zone and leaves the document's own order to decide between them. Both assertions
    are needed: the first says an unmeasured zone follows a measured one WITHOUT
    being sent behind every other unmeasured zone, and the second says that with
    nothing measured at all the offer is simply the document in its own order.

    SABOTAGE: give the sort key a fallback that scores an unmeasured zone behind a
    measured one -- `cited.get(zone, -1)` in `ordered_releasable_observations` --
    and the second assertion goes red.
    """
    _with_facts(conn)
    file_id, content_hash, folder, heading, page = _corpus(conn, tmp_path)
    scanned = _observe_extra(conn, file_id, content_hash, zone="ocr",
                             raw="PHYS 1401 scanned header",
                             container=(Segment("region", 1),))
    _states_the_field(conn, file_id=file_id, content_hash=content_hash,
                      field="subject", value="PHYS1401",
                      ref=heading.observation_key)

    offered = [one.observation_key for one in ordered_releasable_observations(
        conn, file_id=file_id, content_hash=content_hash, locality=LOCAL,
        limit=12, fields=("subject",))]

    # `body` is the measured zone, so it leads; the two UNMEASURED zones follow in
    # the document's own order -- the folder's label-only address at 0, the scanned
    # region at 1 -- and neither is behind the other because of what it is.
    assert offered == [heading.observation_key, page.observation_key,
                       folder.observation_key, scanned.observation_key]
    # And with nothing measured at all they are not last either. `path` -- the zone
    # `zone_rank` sent behind every named one -- LEADS the offer, and the whole offer
    # is non-decreasing in the document's own order, which is the only thing left
    # deciding it. Where the scanned region falls among the two readings that share
    # page 1's address is that order and then the content-addressed tie-break, never
    # the fact that it is `ocr`.
    unmeasured = ordered_releasable_observations(
        conn, file_id=file_id, content_hash=content_hash, locality=LOCAL, limit=12)
    assert unmeasured[0].location.zone == "path"
    assert ([document_order(one) for one in unmeasured]
            == sorted(document_order(one) for one in unmeasured))


# --------------------------------------------------------------------------
# `104` §18.2 gap 6: the file's own strongest reading is reserved
# --------------------------------------------------------------------------

def test_the_files_own_strongest_reading_travels_beside_a_large_context():
    """THE COVERAGE HALF OF gap 6, and the state it is about is not hypothetical.

    `104` R-135 gathers the anchor context from a NEIGHBOUR under a rule that knows
    nothing about how much room is left, and the fill then gave the file's own
    readings whatever the context had not spent. One long syllabus in the folder left
    a remainder of zero, and the file reached the model carrying not one word of its
    own -- so the model was asked what THIS file is and shown only what the file next
    door says. An answer built that way is a fact about the syllabus.

    The reserve admits the top reading first and lets the context fill what is left.
    Both halves are asserted, because "the file's reading travels" is only half the
    claim: the total still fits the ceiling, so nothing here buys coverage by
    breaching the bound the door is about to measure.

    SABOTAGE: delete the `if` in `fill_reserving_top_reading` and the file's own
    reading disappears from `taken` while the context keeps every line.
    """
    head = _Reading("the file's own page", 200)
    rest = [_Reading(f"own-{n}", 200) for n in range(3)]
    crowd = [_Reading(f"neighbour-{n}", 200) for n in range(9)]
    # ROOM FOR THREE READINGS, derived from the readings rather than typed -- and the
    # context alone wants nine of them, which is the state that used to leave zero.
    ceiling = sum(released_wire_cost(one) for one in crowd[:3])

    kept, fill = fill_reserving_top_reading([head, *rest], crowd, ceiling=ceiling)

    assert fill.taken[0] is head
    assert sum(released_wire_cost(one)
               for one in tuple(kept) + fill.taken) <= ceiling
    # The context yielded, and it yielded only what it had to: it still carries every
    # line the reserve left room for.
    assert list(kept) == crowd[:2]


def test_the_context_the_reserve_trimmed_is_in_the_cut_and_not_in_a_silence():
    """`104` §18.2 gap 5's promise, kept one object over.

    The reserve is a second place where the ceiling takes readings away, and a cut
    recorded for the file's own readings but not for the context would be the same
    silence gap 5 closed, moved rather than fixed. `GroundingReport.readings_dropped`
    reads one `DossierFill`, so both cuts come back in it.

    SABOTAGE: return `own` unchanged from `fill_reserving_top_reading` instead of
    folding `cut` into its `dropped`, and the trimmed context lines vanish from every
    record this run writes.
    """
    head = _Reading("own", 200)
    crowd = [_Reading(f"neighbour-{n}", 200) for n in range(9)]
    ceiling = sum(released_wire_cost(one) for one in crowd[:3])

    kept, fill = fill_reserving_top_reading([head], crowd, ceiling=ceiling)

    assert set(fill.dropped) == set(crowd) - set(kept)
    assert fill.dropped_bytes == sum(
        released_wire_cost(one) for one in fill.dropped)


def test_a_context_that_already_leaves_room_is_handed_back_as_itself():
    """THE ORDINARY PATH, asserted by IDENTITY because that is what the caller asks.

    `fact_call_stage` decides whether to pay for a second `build_request` by asking
    `shown is not context`, so a reserve that rebuilt an untouched tuple would cost
    every call in the run a second read of the store for nothing. And a fill that
    moved on a call it had no business moving is the change nobody would notice.

    SABOTAGE: make `fill_reserving_top_reading` always trim (drop the second half of
    its condition) and this goes red -- the context comes back equal and not the
    same.
    """
    head = _Reading("own", 100)
    crowd = [_Reading(f"neighbour-{n}", 100) for n in range(2)]
    roomy = sum(released_wire_cost(one) for one in (head, *crowd))

    kept, fill = fill_reserving_top_reading([head], crowd, ceiling=roomy)

    assert kept is crowd
    assert fill.taken == (head,)
    assert fill.dropped == ()


def test_a_top_reading_that_cannot_travel_alone_takes_nothing_from_the_context():
    """The other boundary, and the reason the condition has two halves.

    A reading longer than the whole ceiling does not fit however much is taken away
    from the neighbours, so trimming for it would cost the call its context and buy
    the file nothing. `ordered_releasable_observations` already withholds a reading
    longer than the STORED ceiling; this is the same answer asked of the call's own
    remainder, which is smaller.

    SABOTAGE: drop `head <= ceiling` from the condition and the context is stripped
    to make room for a reading that still does not fit.
    """
    enormous = _Reading("own", 5_000)
    crowd = [_Reading(f"neighbour-{n}", 100) for n in range(2)]
    ceiling = sum(released_wire_cost(one) for one in crowd)

    kept, fill = fill_reserving_top_reading([enormous], crowd, ceiling=ceiling)

    assert kept is crowd
    assert fill.taken == ()
    assert fill.dropped == (enormous,)
