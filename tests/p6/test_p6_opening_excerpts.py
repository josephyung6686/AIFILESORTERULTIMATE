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

**SUPERSESSION, 9 Sep 2026, `104` §17.13 (the owner's ruling).** The cloud is now
shown what the local model is shown, within the same ceiling, so the refusal this
producer was built to answer is gone: a page is no longer refused for covering its
unit, on either target. What is left of "cannot travel as itself" is LENGTH -- a
reading refused outright, or one longer than P1's STORED ceiling, which no call on
any target can carry and which `items.check_item` now calls a whole document. So
every test below that asked "is the page refused to the cloud" is re-argued to ask
"is the unit longer than the ceiling", and the fixture's ceiling is derived from the
page rather than chosen (`OVER_CEILING`). Two consequences are recorded rather than
smoothed over: the local target now mints where it never minted before, and
`test_the_offer_carries_the_opening_of_a_unit_no_call_can_carry` is a STRICT XFAIL
because the excerpt this producer mints no longer reaches an offer at all.
"""
from __future__ import annotations

import json

from database_agent.budget import set_ceiling
from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file

from dataclasses import replace

from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import (
    is_derived, record_observation, record_run, record_text_unit,
)
from evidence_shape.text_units import TextUnit

from extractors.long_tail import POTENTIALLY_SENSITIVE, SENSITIVITY_DDL

import pytest

from model_facts import (
    DOSSIER_CEILING_KEY, OPENING_EXCERPT_EXTRACTOR, may_be_released,
    mint_opening_excerpts, opening_excerpt_bound,
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

#: The ceiling at which this page becomes a whole document under `104` §17.13, and it
#: is DERIVED FROM THE PAGE rather than chosen: half the unit's own length. §17.13
#: made the stored ceiling the condition for minting, so a fixture that wants an
#: excerpt has to hold a unit longer than the ceiling, and the honest way to write
#: "longer than" is to read the unit. `OVER_CEILING // CAP` is still positive, which
#: is what `opening_excerpt_bound` needs in order to return a bound at all.
OVER_CEILING = len(PAGE) // 2


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


def _mint(conn, readings, locality, *, ceiling):
    """`mint_opening_excerpts` asked DIRECTLY, with the bound the offer would give it.

    `104` §17.13 separated the two questions this module used to ask as one. Whether a
    row is MINTED and whether it is OFFERED were the same answer while the page it was
    cut from was refused; they are not any more, because the page is now released and
    `_without_superseded_excerpts` yields the excerpt to it. So a test about minting
    asks the producer and a test about the offer asks the offer.
    """
    return mint_opening_excerpts(
        conn, readings, sensitive=frozenset(), locality=locality,
        bound=opening_excerpt_bound(conn, limit=CAP), ceiling=ceiling)


def _minted(conn):
    """Every opening excerpt standing in the evidence table, by its raw value."""
    return [row["raw_value"] for row in conn.execute(
        "SELECT raw_value FROM evidence WHERE extractor_name = ? "
        "ORDER BY raw_value", (OPENING_EXCERPT_EXTRACTOR,)).fetchall()]


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
    """No stored bound, no excerpt -- never a bound invented to stand in for one.

    **`104` §17.13 gave this a SECOND reason and took away its old assertion.**
    `mint_opening_excerpts` now refuses on a `None` ceiling as well as on a `None`
    bound, because the ruling made the stored ceiling the condition for minting at
    all: a deployment that stores no ceiling holds no length at which a unit becomes
    a whole document, so there is no refusal for an excerpt to answer and P7 will not
    invent one to create the occasion.

    What this used to assert -- that the offer was EMPTY -- is now false for a reason
    that has nothing to do with minting: with no whole-unit refusal and no `path`
    refusal, both stored readings travel. Inferring "nothing was minted" from an
    empty offer was only ever safe while everything else was refused, so the claim is
    read off the evidence table instead, which is where a minted row actually goes.
    """
    file_id, content_hash, folder, page = _corpus(conn, tmp_path, ceiling=None)

    assert opening_excerpt_bound(conn, limit=CAP) is None
    offered = _offer(conn, file_id, content_hash, CLOUD_LOCALITY)

    assert _minted(conn) == []
    assert [one.observation_key for one in offered] == [
        page.observation_key, folder.observation_key]


# --------------------------------------------------------------------------
# The excerpt itself
# --------------------------------------------------------------------------

def test_a_page_that_fits_the_ceiling_is_offered_whole_and_nothing_is_minted(
        conn, tmp_path):
    """THE RULING ITSELF, and the replacement for what this file measured first.

    Until 9 Sep 2026 this test read: a cloud call over this corpus offered nothing
    from the body at all -- the page was refused as a whole unit and the folder path
    as an always-local zone, so the model was shown the file's extension and its MIME
    type -- and the fix was to offer the OPENING of the page instead. `104` §17.13
    answers the same starvation a shorter way: the cloud is shown what the local
    model is shown, so the page itself travels, and both readings this fixture holds
    are on the offer for either target.

    So the excerpt is not minted, and that is asserted rather than left implied. An
    excerpt beside a page that already fits would be the same characters spending the
    ceiling twice, which is the trade §17.13 removed the need for.

    The two targets are WALKED rather than asserted once, because "the cloud is shown
    what the local model is shown" is a claim about their agreeing and an assertion
    about one of them would not make it.
    """
    file_id, content_hash, folder, page = _corpus(conn, tmp_path)

    for locality in (CLOUD_LOCALITY, LOCAL):
        offered = _offer(conn, file_id, content_hash, locality)

        assert [one.observation_key for one in offered] == [
            page.observation_key, folder.observation_key], locality
        assert offered[0].raw_value == PAGE, locality
        # And the sentences are actually there, which is the whole reason this file
        # exists -- they simply arrive in the page now instead of in a copy of it.
        assert "PHYS 1401" in offered[0].raw_value, locality
    assert _minted(conn) == []


def test_the_excerpt_fits_the_share_of_the_call_the_bound_gave_it(conn, tmp_path):
    """A full complement of these has to fit the ceiling the gate is about to
    measure, or the fix trades a starved dossier for a `dossier_over_budget`
    denial.

    THE CLAIM IS UNCHANGED AND THE OCCASION MOVED. Under `104` §17.13 an excerpt is
    minted only for a unit longer than the STORED ceiling, so the fixture holds a
    ceiling the page does not fit under -- derived from the page, `OVER_CEILING` --
    and the producer is asked directly. Asking the offer would answer a different
    question now, because the offer no longer carries what this mints.
    """
    _file_id, _hash, folder, page = _corpus(conn, tmp_path, ceiling=OVER_CEILING)

    excerpt, = _mint(conn, [folder, page], CLOUD_LOCALITY, ceiling=OVER_CEILING)

    assert len(excerpt.raw_value) <= opening_excerpt_bound(conn, limit=CAP)
    assert len(excerpt.raw_value) * CAP <= OVER_CEILING


def test_a_unit_longer_than_the_ceiling_is_minted_an_opening_on_either_target(
        conn, tmp_path):
    """THE OTHER HALF OF THE RULING, and the half that is easy to miss.

    This test read, until 9 Sep 2026: the excerpt is releasable and the whole page is
    still not. Its premise was SF-1 / `104` R-07 -- a span-less reading covering the
    whole of its unit is refused to a cloud target -- and `104` §17.13 retired that
    refusal, so the second assertion cannot be made about anything any more.

    What replaces it is the condition §17.13 put in its place: LENGTH. A unit longer
    than P1's stored ceiling is what `items.check_item` now calls a whole document,
    it is what no call on any target can carry, and it is the one case this producer
    still serves. THE LOCAL TARGET IS THE SURPRISE HERE: R-159 gave a local model the
    whole unit and this producer minted nothing for it, so a local call over a
    39,000-character `.txt` unit saw the body as nothing at all. It mints for both
    now, which is why the localities are walked and the two answers compared.

    The excerpt is asserted releasable and the page is asserted releasable too. That
    is not a weakened claim, it is the ruling: what separates them is no longer
    `may_be_released` but the ceiling, and the ceiling is spent in
    `within_dossier_budget` and refused at the door in `check_item`.
    """
    _file_id, _hash, folder, page = _corpus(conn, tmp_path, ceiling=OVER_CEILING)

    for locality in (CLOUD_LOCALITY, LOCAL):
        excerpt, = _mint(conn, [folder, page], locality, ceiling=OVER_CEILING)

        assert excerpt.observation_key != page.observation_key, locality
        assert excerpt.location.text_span.start == 0, locality
        assert 0 < excerpt.location.text_span.end < len(PAGE), locality
        assert excerpt.raw_value == PAGE[:excerpt.location.text_span.end], locality
        # And the sentences are actually there, which is the whole reason this exists.
        assert "PHYS 1401" in excerpt.raw_value, locality
        assert may_be_released(conn, excerpt, sensitive=frozenset(),
                               locality=locality), locality
    # The page is releasable too, on both, and that is the ruling rather than a leak:
    # what stops an over-ceiling unit is the ceiling, asked in the fill and at the
    # door, and never this predicate.
    for locality in (CLOUD_LOCALITY, LOCAL):
        assert may_be_released(conn, page, sensitive=frozenset(),
                               locality=locality), locality


def test_every_target_gets_the_whole_unit_and_no_second_copy(conn, tmp_path):
    """`104` R-159's ruling is not paid for twice, and since §17.13 neither is the
    cloud's.

    A model may be shown the whole page within the ceiling, so an excerpt beside it
    would be the same characters spending the ceiling a second time. R-159 made that
    true of a local target and `104` §17.13 makes it true of both, so the test that
    named one target now walks them.

    THE FIXTURE IS THE OVER-CEILING ONE, which is what makes this discriminating.
    Under a slack ceiling nothing is minted at all and "no second copy" would hold
    for want of anything to copy. Here a copy genuinely exists -- `_minted` asserts
    it -- and the offer still carries the unit alone.
    """
    file_id, content_hash, _folder, page = _corpus(conn, tmp_path,
                                                   ceiling=OVER_CEILING)

    for locality in (CLOUD_LOCALITY, LOCAL):
        offered = _offer(conn, file_id, content_hash, locality)

        assert [one.observation_key for one in offered
                if one.location.zone == "body"] == [page.observation_key], locality
    assert _minted(conn) != []


def test_an_excerpt_already_stored_yields_to_the_unit_it_was_cut_from(conn,
                                                                     tmp_path):
    """A minted excerpt is RECORDED, so it outlives the call that minted it -- and
    since `104` §17.13 it yields to that unit on EVERY call, which is a residual this
    test records rather than hides.

    The rule is `_without_superseded_excerpts`: an excerpt is offered instead of the
    reading it was cut from, never beside it. It was written for one case, a corpus
    read for a cloud target and then read again for a local one, where the local read
    would otherwise find the stored excerpt standing beside a page R-159 had just made
    releasable -- the same characters twice, the second copy spending a ceiling the
    ruling meant for the first.

    **§17.13 turned that one case into every case, and this is the consequence.** The
    reading an excerpt is cut from is now ALWAYS releasable, on both targets, whatever
    its length, so the excerpt always yields. This fixture is the case the producer
    exists for -- a unit longer than the ceiling, which no call can carry -- and the
    row is minted, is one row, and is on no offer. What the call then carries is the
    page, which the fill drops for length, so the body reaches the model as nothing.

    That is R-164's own starvation returning by another door, it is reported to the
    lead as a code defect at `4896628`, and the test that states the intended
    behaviour is the strict xfail below. This one asserts what the code does today,
    because a test that asserted the intention would be red for a reason that has
    nothing to do with excerpts yielding.
    """
    file_id, content_hash, _folder, page = _corpus(conn, tmp_path,
                                                   ceiling=OVER_CEILING)
    excerpt, = _mint(conn, [page], CLOUD_LOCALITY, ceiling=OVER_CEILING)
    assert conn.execute(
        "SELECT count(*) c FROM evidence WHERE observation_key = ?",
        (excerpt.observation_key,)).fetchone()["c"] == 1

    for locality in (CLOUD_LOCALITY, LOCAL):
        body = [one for one in _offer(conn, file_id, content_hash, locality)
                if one.location.zone == "body"]

        assert [one.observation_key for one in body] == [
            page.observation_key], locality
    # And the row is still there, unoffered, which is the residual in one line.
    assert _minted(conn) == [excerpt.raw_value]


@pytest.mark.xfail(strict=True, reason=(
    "`104` §17.13's own promise, unmet at 4896628 and reported to the lead. "
    "`mint_opening_excerpts` says a 39,000-character `.txt` unit 'reaches the model "
    "as its opening rather than as nothing', but the ruling made the page it was cut "
    "from releasable, so `_without_superseded_excerpts` yields the excerpt to a "
    "reading `within_dossier_budget` then drops for length. The producer mints a row "
    "no offer can carry and the body reaches the model as nothing, which is the "
    "R-164 starvation `104` §17.16 warned would return. STRICT: the day the offer is "
    "fixed this XPASSes and the suite goes red until the two tests around it are "
    "re-argued to the fix."))
def test_the_offer_carries_the_opening_of_a_unit_no_call_can_carry(conn, tmp_path):
    """What §17.13 has to mean if `mint_opening_excerpts` is to serve any purpose.

    A unit longer than the stored ceiling cannot travel as itself on any target. The
    producer cuts its opening for exactly that case. So the call this fixture builds
    should carry the opening in the body's place, and it carries nothing.
    """
    file_id, content_hash, _folder, _page = _corpus(conn, tmp_path,
                                                    ceiling=OVER_CEILING)

    offered = _offer(conn, file_id, content_hash, CLOUD_LOCALITY)
    carried = within_dossier_budget(offered, ceiling=OVER_CEILING)
    body = [one for one in carried if one.location.zone == "body"]

    assert body != [], (
        "an over-ceiling unit reaches the call as nothing: the page is offered, the "
        "minted opening is superseded by it, and the fill then drops the page")
    assert [one.extractor_name for one in body] == [OPENING_EXCERPT_EXTRACTOR]


def test_nothing_is_minted_over_an_always_local_zone(conn, tmp_path):
    """The producer still cuts nothing from `path`, `ocr` or `filename`, and since
    `104` §17.13 the reason has changed for two of the three.

    R-159 released `path` and `ocr` to a LOCAL target and not to a cloud one, and
    `filename` to neither as an excerpt; an excerpt cut from one of those zones would
    be that ruling walked around by a producer. §17.13 released `path` and `ocr` to
    every target, so an excerpt of either would no longer walk around a refusal -- it
    would simply be a shorter second copy of a reading that already travels whole,
    spending the ceiling twice. `filename` keeps the original reason exactly: its door
    is `items.Filename` under `allow_unratified`, where §7.3's protected-records ban
    also applies, and an excerpt would bypass both.

    So the assertion inverts for `path`. It used to be that the folder was ABSENT from
    the offer; it is now present, as itself, and what must be absent is any excerpt
    cut from it.

    All three zones are walked, in the shape the producer would meet them, because
    `mint_opening_excerpts` still guards on the whole of `ALWAYS_LOCAL_ZONES` rather
    than on the half §17.13 kept. THE `ocr` READING IS WHAT MAKES THAT
    LOAD-BEARING, and it is built with care: it is longer than the ceiling and it has
    a real stored unit to cut from, so the zone guard is the only thing standing
    between it and an excerpt. Given a reading with no unit, `opening_reading_for`
    would decline to cut anyway and this test would pass for a reason that is not
    the zone.

    The fixture is the over-ceiling one, so the producer is minting: a slack ceiling
    would satisfy "nothing was cut from `path`" by cutting nothing at all.

    SABOTAGE: narrow the guard to `ALWAYS_LOCAL_ZONES_FOR_EVERY_TARGET` and a second
    row is minted, over the OCR unit, and the two assertions on `minted` go red.
    """
    file_id, content_hash, folder, page = _corpus(conn, tmp_path,
                                                  ceiling=OVER_CEILING)
    named = replace(
        folder, raw_value="HW 3.pdf",
        location=Location("filename", (Segment("field", label="filename"),)))
    scanned_at = (Segment("page", 2),)
    record_text_unit(conn, TextUnit(run_id="run-hw", container_path=scanned_at,
                                    text=PAGE))
    scanned = replace(page, raw_value=PAGE,
                      location=Location("ocr", scanned_at))
    record_observation(conn, scanned)

    minted = _mint(conn, [folder, named, scanned, page], CLOUD_LOCALITY,
                   ceiling=OVER_CEILING)
    offered = _offer(conn, file_id, content_hash, CLOUD_LOCALITY)

    # One row, and it is the page's -- nothing was cut from any always-local zone.
    assert [one.location.zone for one in minted] == ["body"]
    assert [one.location.container_path for one in minted] == [
        page.location.container_path]
    assert A_FOLDER not in "".join(_minted(conn))
    assert "HW 3.pdf" not in "".join(_minted(conn))
    # And the folder now travels as itself, which is the half of the ruling that
    # makes this test's old assertion false.
    assert folder.observation_key in {one.observation_key for one in offered}


def test_nothing_is_minted_over_a_reading_p5_signalled(conn, tmp_path):
    """The per-value signal refuses the WHOLE request, and a recognised human
    identifier is not a fact about where the value is going. Cutting the opening off
    a signalled reading would release the part of it P5 objected to.

    THE ARM IS UNTOUCHED BY `104` §17.13, which divided the zone arm and the
    whole-unit arm and left the sensitive-key arm, the protected arm, the unratified
    arm and the suspension arm alone. Two things about the test moved.

    The fixture takes the OVER-CEILING ceiling, because with a slack one the producer
    mints nothing for any reason and the test would pass without the signal doing any
    work. And the old assertion -- the offer is EMPTY -- is now false: the folder path
    carries no signal and travels. What is asserted is the signalled reading's own
    absence, and that no row was cut from it.
    """
    file_id, content_hash, folder, page = _corpus(conn, tmp_path,
                                                  ceiling=OVER_CEILING)
    conn.execute(
        "INSERT INTO extraction_sensitivity_signal "
        "(run_id, observation_key, signal, basis, observed_at) "
        "VALUES (?, ?, ?, 'test', ?)",
        ("run-hw", page.observation_key, POTENTIALLY_SENSITIVE, CLOCK))

    offered = _offer(conn, file_id, content_hash, CLOUD_LOCALITY)

    assert [one.observation_key for one in offered] == [folder.observation_key]
    assert _minted(conn) == []


def test_the_excerpt_is_derived_and_is_not_evidence_about_the_file(conn, tmp_path):
    """`104` R-135's ruling, and this reading is the same kind of thing its minted
    line is: an addressable copy of text an earlier pass already stored, so that it
    can be cited. It says nothing new about what the file IS, and a rule pass or a
    recogniser that counted it would count the file's own words twice.

    `104` §17.13 moved only where the excerpt is read from. The offer no longer
    carries it, so the producer is asked directly and the fixture holds a ceiling the
    page does not fit under.
    """
    _file_id, _hash, folder, page = _corpus(conn, tmp_path, ceiling=OVER_CEILING)

    excerpt, = _mint(conn, [folder, page], CLOUD_LOCALITY, ceiling=OVER_CEILING)

    assert is_derived(excerpt)


def test_minting_the_same_excerpt_twice_writes_one_row(conn, tmp_path):
    """The handle is content-addressed, so asking the same question twice finds the
    row the first ask wrote. A release path that grew the evidence table on every
    call would make `104` §8.5's replay disagree with itself.

    THE FIXTURE HAD TO MOVE OR THIS TEST WOULD PASS FOR NOTHING. Under a slack ceiling
    `104` §17.13 mints no row at all, so "the table did not grow" would hold because
    nothing was ever written. The over-ceiling fixture makes the producer write, and
    the assertion that exactly one excerpt stands afterwards is what says the second
    call found the first call's row instead of adding to it.

    The two calls are on DIFFERENT targets, which is the second thing §17.13 changed
    here: both mint now, so a handle that hashed the destination would write two rows.
    """
    file_id, content_hash, _folder, _page = _corpus(conn, tmp_path,
                                                    ceiling=OVER_CEILING)
    first = _offer(conn, file_id, content_hash, CLOUD_LOCALITY)
    rows = conn.execute("SELECT count(*) c FROM evidence").fetchone()["c"]
    assert len(_minted(conn)) == 1

    second = _offer(conn, file_id, content_hash, LOCAL)

    assert [one.observation_key for one in second] == [
        one.observation_key for one in first]
    assert conn.execute("SELECT count(*) c FROM evidence").fetchone()["c"] == rows
    assert len(_minted(conn)) == 1


def test_a_unit_no_longer_than_the_bound_gets_no_excerpt_and_keeps_its_answer(
        conn, tmp_path):
    """There is nothing shorter than the unit to cut, so the whole-unit rule keeps the
    answer it already had and this producer adds nothing to it.

    **THE RESIDUAL THIS TEST RECORDED IS CLOSED, and `104` §17.13 closed it.** It read:
    R-152 exempted a whole LINE unit and a whole HEADING unit from the document rule,
    but in the SPAN-BEARING arm, so a short page whose reading is SPAN-LESS -- one line
    of extracted text with no span over it -- was still refused to a cloud target, and
    no excerpt could help it because any excerpt of it would be shorter than the words
    it already has. Closing that was a change to SF-1's own wording and was not
    R-164's to make. The owner made it: a whole unit is released to every target
    within the ceiling, so this short page travels, span-less, as itself.

    `opening_reading_for` still declines to cut a unit no longer than the bound, for
    the reason it always gave -- the opening would BE the unit -- and that reason
    outlived the refusal it was written beside. The assertion is now that the page is
    offered and no row was minted, on both targets.
    """
    file_id, content_hash, folder, page = _corpus(
        conn, tmp_path, text="Homework 3 for PHYS 1401")

    for locality in (CLOUD_LOCALITY, LOCAL):
        offered = _offer(conn, file_id, content_hash, locality)

        assert [one.observation_key for one in offered] == [
            page.observation_key, folder.observation_key], locality
        assert may_be_released(conn, page, sensitive=frozenset(),
                               locality=locality), locality
    assert _minted(conn) == []


# --------------------------------------------------------------------------
# The bound the excerpts are spent under: the ceiling, and only the ceiling
# --------------------------------------------------------------------------

def test_the_ceiling_is_the_one_bound_for_a_cloud_call_and_the_cap_only_cuts(conn,
                                                                            tmp_path):
    """THE REPLACEMENT FOR TWO TESTS WHOSE SUBJECT NO LONGER EXISTS.

    They were `test_a_cloud_call_is_bounded_by_the_ceiling_as_well_as_by_the_count`
    and `test_the_count_still_binds_a_cloud_call_when_the_ceiling_is_slack`, and both
    were about `within_dossier_budget`'s count cap for a CLOUD call. R-159 kept that
    cap because §8.4's "data-minimizing" reads as a count as well as a length, and
    R-164 added the ceiling beside it. `104` §17.13 removed the locality the cap
    divided by -- the cloud is shown what the local model is shown, within the same
    ceiling -- and the cap went with it: `within_dossier_budget` now takes neither
    `limit` nor `locality`, and one bound answers for either target.

    So the two claims collapse into one, asserted in both directions. A slack ceiling
    admits more readings than the cap would ever have allowed, which is the assertion
    the second test made backwards. A tight ceiling still binds, which is the first.

    **`CAP` IS NOT GONE, IT IS SPENT ELSEWHERE, and that is why this test still names
    it.** `cli.FACT_CALL_MAX_RELEASED_OBSERVATIONS` now buys exactly one thing, the
    share of the ceiling one minted excerpt may take
    (`test_the_bound_is_the_stored_ceiling_divided_by_the_call_s_own_cap` above), and
    a reader who found the constant with no test naming it would delete it and take
    the excerpt bound with it.
    """
    _corpus(conn, tmp_path, ceiling=4_000)
    assert opening_excerpt_bound(conn, limit=CAP) is not None

    slack = [_Reading(f"r{n}", 10) for n in range(CAP * 2)]
    assert within_dossier_budget(slack, ceiling=1_000_000) == tuple(slack)

    # And the ceiling, the one bound left, still binds: five of these fit under 550
    # and the sixth does not.
    hundreds = [_Reading(f"r{n}", 100) for n in range(20)]
    assert within_dossier_budget(hundreds, ceiling=550) == tuple(hundreds[:5])


class _Reading:
    """Just the `raw_value` `within_dossier_budget` measures, as `104` R-159's own
    budget tests build it."""

    def __init__(self, name, length):
        self.name = name
        self.raw_value = "x" * length

    def __repr__(self):
        return f"<{self.name}:{len(self.raw_value)}>"
