# tests/p6/test_p6_work_type.py
"""`artifact_kind`'s producer: the library's own work-type terms, ranked as §3.7 asks.

`def.subject-work-record` binds four levels and marks TWO of them REQUIRED --
`subject_anchor` -> `subject`, and `artifact_kind` -> `work_type`. Nothing in `src/`
filled `work_type`, so the second required level could never be built and every file
in the situation went unplaced: measured 0.0% exact over the ground-truth corpus,
with 85.4% "not placed".

**The vocabulary is the library's and this producer authors none of it.**
`recognition.json` ships `work_type_terms` per schema -- 124 for `academic` -- and
twelve of the thirteen distinct leaf values the ground-truth labels use for
`academic.coursework` are members of that list, verbatim (`essay`, `exercise`,
`lecture slides`, `practice test`, `lecture`, `problem set`, `exam`, `homework`,
`course handout`, `reading`, `quiz`, `assignment brief`). The labels were authored
from the shipped vocabulary, so matching against it is reading the design rather
than inventing a parallel list.

**A MENTION IS NOT A CLAIM, and that is the whole of the precision story.**
`work_type` answers what the file IS, and `recognition.detector.NAMING_ZONES` is
already the design's own answer to that question -- its comment says `body`, `table`,
`ocr`, `notes`, `annotation` and `reference_list` "are where a document mentions
OTHER documents, and the whole of this constant's job is to keep a mention from
becoming a claim." Measured over the ground-truth corpus, reading every zone fills
10 correctly and 12 WRONGLY -- `Joseph Yung - Final Draft.pdf` becomes an
`acceptance letter` because its prose says so somewhere. Reading only the naming
zones keeps all 10 and drops the wrong ones to 5. The constant is injected, not
re-spelled here: this module reaches `recognition/` never.
"""
import json
import re
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts.file_facts import facts_for_file
from facts.unresolved import unresolved_for_file
from facts.kind import (
    EmptyVocabulary, compile_vocabulary, kind_facts, terms_in,
)

CLOCK = "2026-08-22T00:00:00Z"

#: The shipped `academic` terms this suite exercises, quoted from
#: `src/recognition/library/recognition.json`. A test that invented a term would be
#: testing a vocabulary the product does not have; `test_every_term_here_is_shipped`
#: reads the library and fails if any of these has stopped being one of its own.
SHIPPED = ("homework", "essay", "exam", "lecture", "lecture slides",
           "practice test", "problem set", "syllabus", "quiz", "transcript",
           "unofficial transcript")

#: P4's fifteen zones. Every one carries a weight, because `rank` raises rather than
#: defaulting and a corpus reaches zones a test did not think of.
ZONE_WEIGHT = {"filename": 3.0, "title": 3.0, "heading": 2.0, "body": 1.0,
               "header_footer": 0.25, "metadata": 1.0, "path": 1.0, "table": 1.0,
               "notes": 1.0, "link": 1.0, "annotation": 1.0, "reference_list": 0.5,
               "manifest": 1.0, "ocr": 1.0, "transcript": 1.0}
TIER_WEIGHT = {1: 4.0, 2: 2.0, 3: 1.0}
MINIMUM_SCORE = 1.0
MINIMUM_MARGIN = 0.5

#: SPEC 2.2's ranking, and the composition root's to supply. Spelled here as the
#: caller's value exactly as `test_p6_date_facts.py` spells the date catalogue: the
#: rule these express is proved by a test rather than asserted at the one call site.
NAMING_ZONES = frozenset({"filename", "title", "heading", "header_footer"})
FIRST_PAGE = 1

VOCABULARY = compile_vocabulary(SHIPPED)


def _record(conn, tmp_path, *, name, body):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Courses", mime_type="text/plain",
        detected_format="txt", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, zone="filename",
             page=1):
    if conn.execute("SELECT 1 FROM extraction_runs WHERE run_id = ?",
                    (run_id,)).fetchone() is None:
        record_run(conn, ExtractionRun(
            run_id=run_id, file_id=file_id, content_hash=content_hash,
            extractor_name="pdf.text", extractor_version="1.0.0",
            source_type="text_document", analysis_tier="native", config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    segments = () if page is None else (Segment("page", page),)
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location(zone, segments), occurrence_count=1,
        observed_at=CLOCK, reliability="possible", run_id=run_id)
    record_observation(conn, observation)
    return observation


def _run(conn, tmp_path, *, name, readings, vocabulary=VOCABULARY):
    """One file, one observation per (text, zone, page), then the producer."""
    file_id, content_hash = _record(conn, tmp_path, name=name, body=b"corpus")
    for index, reading in enumerate(readings):
        text, zone, page = reading
        _observe(conn, run_id=f"run-{index}", file_id=file_id,
                 content_hash=content_hash, raw=text, zone=zone, page=page)
    written = kind_facts(
        conn, file_id=file_id, content_hash=content_hash, field_key="work_type",
        vocabulary=vocabulary, naming_zones=NAMING_ZONES, first_page=FIRST_PAGE,
        zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT,
        minimum_score=MINIMUM_SCORE, minimum_margin=MINIMUM_MARGIN)
    return file_id, content_hash, written


def _values(conn, file_id, content_hash):
    return [row["canonical_value"]
            for row in facts_for_file(conn, file_id, content_hash)
            if row["field_key"] == "work_type" and row["active"]]


def _refusal(conn, file_id, content_hash):
    return [row["reason"] for row in unresolved_for_file(
        conn, file_id, content_hash, field_key="work_type")]


# --- the vocabulary is the library's ----------------------------------------

def test_every_term_here_is_shipped_by_the_library():
    # The point of the producer is that it reads the library's own `artifact_kind`
    # vocabulary. If this suite drifted onto terms the library does not author, it
    # would be proving a matcher against a list the product never sees.
    library = json.loads(
        (Path(__file__).resolve().parents[2] / "src" / "recognition" / "library"
         / "recognition.json").read_text())
    academic = set(library["schemas"]["academic"]["work_type_terms"])
    assert set(SHIPPED) <= academic


def test_an_empty_vocabulary_is_refused_rather_than_matching_nothing():
    # F8's rule: absent means refuse, never a default that quietly answers a
    # question. A producer built on an empty vocabulary abstains on every file in
    # the corpus and looks exactly like one that is working and finding nothing.
    with pytest.raises(EmptyVocabulary):
        compile_vocabulary(())


# --- filling -----------------------------------------------------------------

def test_a_work_type_in_the_filename_fills_the_field(p6_conn, tmp_path):
    file_id, content_hash, written = _run(
        p6_conn, tmp_path, name="Homework_3.pdf",
        readings=[("Homework_3.pdf", "filename", None)])
    assert len(written) == 1
    assert _values(p6_conn, file_id, content_hash) == ["homework"]
    assert _refusal(p6_conn, file_id, content_hash) == []


def test_the_stored_value_is_the_librarys_spelling_not_the_documents(
        p6_conn, tmp_path):
    # The value becomes a FOLDER NAME, and the library authored `lecture slides`.
    # Storing the document's own casing would make `LECTURE SLIDES week 1.pdf` and
    # `Lecture Slides Week 2.pdf` two folders for one kind of work -- `65` §4.2's
    # recorded failure, "one identity arriving as several spellings".
    file_id, content_hash, _ = _run(
        p6_conn, tmp_path, name="LECTURE SLIDES week 1.pdf",
        readings=[("LECTURE SLIDES week 1.pdf", "filename", None)])
    assert _values(p6_conn, file_id, content_hash) == ["lecture slides"]


def test_a_work_type_fact_is_validated_and_never_direct(p6_conn, tmp_path):
    # §3.13: `validated` is "found by a deterministic rule and passed contextual
    # checks", and clearing a minimum score and a minimum margin over ranked
    # candidates is exactly that check.
    file_id, content_hash, _ = _run(
        p6_conn, tmp_path, name="Essay 2.docx",
        readings=[("Essay 2.docx", "filename", None)])
    rows = [row for row in facts_for_file(p6_conn, file_id, content_hash)
            if row["field_key"] == "work_type"]
    assert [row["reliability_state"] for row in rows] == ["validated"]
    assert [row["origin"] for row in rows] == ["rule"]


# --- the longest authored term claims the span -------------------------------

def test_a_longer_authored_term_beats_the_shorter_one_inside_it(
        p6_conn, tmp_path):
    # `lecture` and `lecture slides` are BOTH authored. They are not two rival
    # readings of this filename -- the shorter is a fragment of the longer -- so
    # counting both would put them level at 3.0 each and the margin would refuse a
    # file whose name says exactly what it is. Nine ground-truth files want
    # `lecture slides`.
    file_id, content_hash, written = _run(
        p6_conn, tmp_path, name="Lecture Slides Week 3.pdf",
        readings=[("Lecture Slides Week 3.pdf", "filename", None)])
    assert len(written) == 1
    assert _values(p6_conn, file_id, content_hash) == ["lecture slides"]


def test_the_same_rule_holds_for_unofficial_transcript(p6_conn, tmp_path):
    # The nesting is not special to `lecture slides`: `transcript` and
    # `unofficial transcript` are a second shipped pair, and an unofficial
    # transcript filed as a transcript is a different folder.
    file_id, content_hash, _ = _run(
        p6_conn, tmp_path, name="unofficial transcript.pdf",
        readings=[("unofficial transcript.pdf", "filename", None)])
    assert _values(p6_conn, file_id, content_hash) == ["unofficial transcript"]


# --- a mention is not a claim ------------------------------------------------

def test_a_term_in_the_body_does_not_fill_the_field(p6_conn, tmp_path):
    # `NAMING_ZONES`' own comment: body, table, ocr, notes, annotation and
    # reference_list "are where a document mentions OTHER documents". An essay
    # whose prose discusses the homework it accompanies is not a homework.
    file_id, content_hash, written = _run(
        p6_conn, tmp_path, name="Untitled.pdf",
        readings=[("see the homework for details", "body", 1)])
    assert written == ()
    assert _refusal(p6_conn, file_id, content_hash) == ["no_candidate_evidence"]


def test_the_filename_decides_and_the_body_cannot_outvote_it(p6_conn, tmp_path):
    # The measured failure this prevents: a file named `Homework_3.pdf` whose body
    # mentions the syllabus three times. Body readings are not weighed against the
    # filename -- they are not read at all -- so no amount of prose can move it.
    file_id, content_hash, _ = _run(
        p6_conn, tmp_path, name="Homework_3.pdf",
        readings=[("Homework_3.pdf", "filename", None),
                  ("syllabus", "body", 1),
                  ("syllabus", "body", 1),
                  ("syllabus", "body", 1)])
    assert _values(p6_conn, file_id, content_hash) == ["homework"]


def test_a_heading_after_page_one_is_not_the_document_naming_itself(
        p6_conn, tmp_path):
    # `pdf.text` "calls a line a heading when its type is larger than the page's
    # body size, which is a typographic guess and not a semantic one" -- the
    # detector measured a 642-page datasheet locked on a page-2 "heading". SPEC
    # 2.2's phrase is "page-ONE heading".
    file_id, content_hash, written = _run(
        p6_conn, tmp_path, name="Untitled.pdf",
        readings=[("Homework", "heading", 2)])
    assert written == ()
    assert _refusal(p6_conn, file_id, content_hash) == ["no_candidate_evidence"]


def test_an_unpaginated_heading_still_names_the_file(p6_conn, tmp_path):
    # "A page of `None` passes. That is not a missing page, it is a format that
    # does not paginate -- a `.docx` heading and a filename both have no page."
    file_id, content_hash, _ = _run(
        p6_conn, tmp_path, name="Untitled.docx",
        readings=[("Problem Set 4", "heading", None)])
    assert _values(p6_conn, file_id, content_hash) == ["problem set"]


# --- word boundaries ---------------------------------------------------------

def test_a_term_inside_a_longer_word_is_not_a_match(p6_conn, tmp_path):
    # §3.7's own rule: "names such as MIT can be found inside 'submit'". `exam`
    # inside `examination` is the same failure, and `Final examination` is a
    # phrase a real syllabus uses about a course rather than about the file.
    file_id, content_hash, written = _run(
        p6_conn, tmp_path, name="examinations.pdf",
        readings=[("examinations.pdf", "filename", None)])
    assert written == ()
    assert _refusal(p6_conn, file_id, content_hash) == ["no_candidate_evidence"]


def test_a_term_split_by_punctuation_still_matches(p6_conn, tmp_path):
    # The counterpart to the rule above, and the detector's measured reason for
    # holding it: comparing a tokenised term against raw authored strings meant
    # "159 of 470 safety work-type spellings could never match". A person writes
    # `Problem-Set-4` and `Problem Set 4` interchangeably.
    file_id, content_hash, _ = _run(
        p6_conn, tmp_path, name="Problem-Set-4.pdf",
        readings=[("Problem-Set-4.pdf", "filename", None)])
    assert _values(p6_conn, file_id, content_hash) == ["problem set"]


# --- abstention is a result --------------------------------------------------

def test_two_different_work_types_in_one_name_refuse_rather_than_guess(
        p6_conn, tmp_path):
    # §3.7's margin, doing the job it exists for. A file called
    # `Quiz and Homework.pdf` is genuinely two readings and `00` requires
    # abstention where two readings are both supported. One unplaced file is the
    # cost; a wrong folder the owner has to find and undo is the alternative.
    file_id, content_hash, written = _run(
        p6_conn, tmp_path, name="Quiz and Homework.pdf",
        readings=[("Quiz and Homework.pdf", "filename", None)])
    assert written == ()
    assert _refusal(p6_conn, file_id, content_hash) == ["below_margin"]


def test_a_file_carrying_no_authored_term_refuses_with_no_candidate_evidence(
        p6_conn, tmp_path):
    file_id, content_hash, written = _run(
        p6_conn, tmp_path, name="IMG_4471.jpg",
        readings=[("IMG_4471.jpg", "filename", None)])
    assert written == ()
    assert _refusal(p6_conn, file_id, content_hash) == ["no_candidate_evidence"]


def test_a_term_only_in_the_header_footer_is_under_the_score_floor(
        p6_conn, tmp_path):
    # `header_footer` is a naming zone and weighs 0.25, so one reading there scores
    # under §3.7's floor on its own. The refusal names WHICH bar was missed:
    # §8.5 asks "Did it abstain when evidence was absent?" and this is the case
    # where it was present and too weak, which is a different answer.
    file_id, content_hash, written = _run(
        p6_conn, tmp_path, name="Untitled.pdf",
        readings=[("homework", "header_footer", 1)])
    assert written == ()
    assert _refusal(p6_conn, file_id, content_hash) == ["below_score_threshold"]


def test_the_absolute_path_is_not_one_of_the_files_own_words(p6_conn, tmp_path):
    # The detector's measured rule, and this producer inherits it by construction:
    # `path` is not a naming zone. "every file on a disk sits under some words, and
    # none of them are the file's own" -- a photograph in a folder called
    # `Homework` is not a homework.
    file_id, content_hash, written = _run(
        p6_conn, tmp_path, name="IMG_4471.jpg",
        readings=[("/Users/jy/Courses/Homework/IMG_4471.jpg", "path", None)])
    assert written == ()
    assert _refusal(p6_conn, file_id, content_hash) == ["no_candidate_evidence"]


# --- nothing is defaulted ----------------------------------------------------

@pytest.mark.parametrize("missing", [
    "vocabulary", "naming_zones", "first_page", "zone_weight", "tier_weight",
    "minimum_score", "minimum_margin", "field_key",
])
def test_every_policy_is_required_and_none_is_defaulted(missing, p6_conn,
                                                        tmp_path):
    # `src/cli.py` is the sole composition root: no part package picks a number or
    # a policy. A default here would answer a question the SPEC left open, in the
    # one place nobody looks (F8).
    file_id, content_hash = _record(p6_conn, tmp_path, name="Homework.pdf",
                                    body=b"x")
    keywords = dict(
        field_key="work_type", vocabulary=VOCABULARY, naming_zones=NAMING_ZONES,
        first_page=FIRST_PAGE, zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT,
        minimum_score=MINIMUM_SCORE, minimum_margin=MINIMUM_MARGIN)
    del keywords[missing]
    with pytest.raises(TypeError):
        kind_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                        **keywords)


def test_the_module_spells_no_field_key_and_no_term():
    # `dates.py` never spells `term`; this never spells `work_type`. A part package
    # that named the field would be a second home for `facts.fields`, and one that
    # named a term would be a second home for the shipped library.
    # A module named for the field may of course name its own functions after it.
    # What it may not do is BIND one: the test is for a string literal, which is
    # the only form that could reach `fields` or `values` as a key.
    source = (Path(__file__).resolve().parents[2] / "src" / "facts"
              / "kind.py").read_text()
    body = "\n".join(line for line in source.splitlines()
                     if not line.lstrip().startswith("#"))
    code = body.split('"""')[-1]
    for literal in ('"work_type"', "'work_type'", '"homework"', "'homework'",
                    '"essay"', "'essay'", '"artifact_kind"', "'artifact_kind'"):
        assert literal not in code, literal


def test_the_tokeniser_agrees_with_the_detectors(p6_conn):
    # This module cannot import `recognition/` -- `facts/` reaches it never -- so
    # the phrase tokeniser is spelled twice in the product. Two spellings of one
    # rule drift silently, so the agreement is a test rather than a comment.
    #
    # They now differ in ONE place and only one, and it is deliberate: a digit run
    # adjacent to a letter run separates HERE and not there. Every string below is
    # free of that boundary, so agreement is still the rule; the exception is pinned
    # by `test_the_producer_and_the_detector_differ_only_at_the_digit_boundary`,
    # which also says why the detector's must not follow.
    from recognition.detector import _tokens as detector_tokens
    from facts.kind import tokens as producer_tokens
    for text in ("Lecture Slides Week 3.pdf", "Problem-Set-4", "after-visit summary",
                 "1403.Sample.Exam.1.No.1.w.key_revised.docx", "C++ / notes",
                 "  MIXED   Case_and.punctuation  "):
        assert producer_tokens(text) == detector_tokens(text), text


# --- what the composition root binds -----------------------------------------

def test_the_composition_root_reads_the_shipped_library_and_invents_no_term():
    # The whole design decision, asserted where it can fail: the vocabulary is the
    # library's, joined to the four schemas that DECLARE the field (`60` H6.2), and
    # `cli` adds nothing of its own to it.
    import cli
    from facts.fields import DOMAIN_FIELDS
    library = json.loads(cli._RECOGNITION_MANIFEST.read_text())["schemas"]
    declaring = [s for s, fields in DOMAIN_FIELDS.items()
                 if cli.WORK_TYPE_FIELD in fields]
    shipped = {term for s in declaring
               for term in library.get(s, {}).get("work_type_terms", ())}
    assert declaring, "no schema declares the field; the join has broken"
    assert set(cli.WORK_TYPE_VOCABULARY.terms.values()) <= shipped
    # And the schemas that do NOT declare it contribute nothing: `medical`'s
    # `discharge summary` becoming a work_type is the re-route H6.2 forbids.
    withheld = {term for s in library if s not in declaring
                for term in library[s].get("work_type_terms", ())}
    assert not (withheld - shipped) & set(cli.WORK_TYPE_VOCABULARY.terms.values())


def test_the_composition_root_withholds_the_heading_zone():
    # Measured over the ground-truth corpus: of the 36 files the producer filled,
    # every fill whose only evidence was a heading was WRONG (three of three) and
    # not one correct fill depended on a heading. A heading names a section; a
    # filename and a title name the document, and `work_type` is a claim about the
    # whole file. P7 keeps `heading` because it is deciding protection, where the
    # same misreading errs toward sealing a file rather than toward naming a folder.
    import cli
    from recognition.detector import NAMING_ZONES as P7_NAMING_ZONES
    assert "heading" in P7_NAMING_ZONES
    assert "heading" not in cli.WORK_TYPE_NAMING_ZONES
    assert {"filename", "title"} <= cli.WORK_TYPE_NAMING_ZONES
    assert cli.WORK_TYPE_NAMING_ZONES < P7_NAMING_ZONES


# --- one mechanism, more than one type key -----------------------------------

def test_the_same_function_fills_a_second_type_key_with_no_new_logic(
        p6_conn, tmp_path):
    """`60` H6.1 asks one question -- what KIND of thing is this -- under three keys.

    `work_type` is the work product of a bounded engagement, `artifact_type` is the
    output of a making process, `record_type` is what remains. All three are
    `value_kind = "enum"`, all three are closed, and the compiled recognition
    release ships ONE vocabulary that feeds all of them: `work_type_terms`, per
    schema, routed to whichever type key that schema declares.

    So binding a second key is a CALL, not a change. Nothing in `facts.kind` moves
    between this test and the one above it -- the field key and the vocabulary are
    both parameters, and `research`'s own shipped terms are the vocabulary here.

    THIS IS A TEST AND NOT A PRODUCTION WIRING, deliberately. H6.2 requires the
    active schema to choose the key, and the schema is not known when the producer
    runs, so `cli.py` wires `work_type` alone. See `facts.kind`'s docstring.
    """
    library = json.loads(
        (Path(__file__).resolve().parents[2] / "src" / "recognition" / "library"
         / "recognition.json").read_text())
    research = library["schemas"]["research"]["work_type_terms"]
    # The library's own example chain for a research file is
    # `('Chen Lab', 'PVA-RDP', 'protocol')`, and `protocol` is one of its terms.
    assert "protocol" in research
    file_id, content_hash = _record(p6_conn, tmp_path,
                                    name="PVA-RDP protocol.pdf", body=b"x")
    _observe(p6_conn, run_id="r-artifact", file_id=file_id,
             content_hash=content_hash, raw="PVA-RDP protocol.pdf",
             zone="filename", page=None)
    written = kind_facts(
        p6_conn, file_id=file_id, content_hash=content_hash,
        field_key="artifact_type", vocabulary=compile_vocabulary(research),
        naming_zones=NAMING_ZONES, first_page=FIRST_PAGE,
        zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT,
        minimum_score=MINIMUM_SCORE, minimum_margin=MINIMUM_MARGIN)
    assert len(written) == 1
    stored = [row["canonical_value"]
              for row in facts_for_file(p6_conn, file_id, content_hash)
              if row["field_key"] == "artifact_type" and row["active"]]
    assert stored == ["protocol"]
    # And nothing landed under the other key: the caller chose one.
    assert _values(p6_conn, file_id, content_hash) == []


def test_the_vocabularies_of_the_three_type_keys_are_nearly_disjoint():
    """Why routing is a real requirement and not bookkeeping.

    Measured over the shipped library: `work_type` (4 schemas, 942 terms) and
    `record_type` (7 schemas, 1,269 terms) share 98 terms, because `career`
    declares BOTH keys. On the 199-file corpus that overlap is what puts `resume`
    under two keys on 15 files and `cover letter` under three on 2 -- H6.3's
    cross-domain collision, which is why `cli.py` wires one key and not three.
    """
    library = json.loads(
        (Path(__file__).resolve().parents[2] / "src" / "recognition" / "library"
         / "recognition.json").read_text())["schemas"]
    from facts.fields import DOMAIN_FIELDS
    from facts.kind import tokens as tok
    vocab = {}
    for field in ("work_type", "artifact_type", "record_type"):
        declaring = [s for s, f in DOMAIN_FIELDS.items() if field in f]
        assert declaring, field
        vocab[field] = {tok(t) for s in declaring
                        for t in library.get(s, {}).get("work_type_terms", ())
                        if tok(t)}
    # Each key has a substantial vocabulary of its own, and no two are the same
    # list under two names -- if they were, routing would not matter.
    for field, terms in vocab.items():
        assert len(terms) > 100, (field, len(terms))
    assert vocab["work_type"] != vocab["artifact_type"] != vocab["record_type"]
    # The overlap is small but real, and small enough that most files reach one
    # key only: `work_type` and `artifact_type` share far less than either holds.
    assert len(vocab["work_type"] & vocab["artifact_type"]) < 20
    # ...and `career` declaring two keys is what makes the biggest overlap real.
    assert vocab["work_type"] & vocab["record_type"]
    assert "career" in DOMAIN_FIELDS
    assert {"work_type", "record_type"} <= set(DOMAIN_FIELDS["career"])


# --- the digit boundary: a gap that was recorded, then closed -----------------

def test_a_term_run_together_with_digits_reaches_the_vocabulary_word(
        p6_conn, tmp_path):
    """`lecture08` is `lecture`, and this test used to assert the opposite.

    It was pinned as an accepted gap on the argument that "relaxing the boundary is
    §3.7's forbidden substring match -- the rule that keeps `MIT` out of `submit`",
    and that "splitting alpha from digit runs is P4's call at the observation, not a
    matcher's." The first half does not hold and the second was a routing preference,
    not a rule. A substring match FINDS a shorter term inside a longer token, which is
    why `submit` must not yield `mit`; `submit` carries no digit and is still ONE
    token here. This re-SEGMENTS a run at a change of character class, and then
    matches whole tokens exactly as before -- so the discipline `word_boundary_match`
    shares with every other facet is untouched, and
    `test_a_shorter_term_inside_a_longer_word_is_not_a_match` still passes.

    What it cost to leave open: all five of the owner's Python lectures are named
    this way, and `def.subject-work-record` marks the level `work_type` fills
    REQUIRED, so a folder that cannot be named cannot be built and the file is not
    placed at all.
    """
    file_id, content_hash, written = _run(
        p6_conn, tmp_path, name="lecture08_recursion.ipynb",
        readings=[("lecture08_recursion.ipynb", "filename", None)])
    assert len(written) == 1
    assert _values(p6_conn, file_id, content_hash) == ["lecture"]


def test_the_boundary_is_the_digit_and_never_the_case():
    """An ALL-CAPS RUN IS ONE TOKEN, and that is the whole safety of this rule.

    The hazard a camel-case boundary carries and this one does not: `HKID` is the
    owner's own identity card, and a rule that split a letter run on case would
    reduce it to `h` + `kid` and stop the identity term matching the document that
    names it. Case is never read here -- only whether a character is a digit -- so
    every acronym in the corpus survives whole.
    """
    from facts.kind import tokens
    assert tokens("HKID") == ("hkid",)
    assert tokens("PDF") == ("pdf",)
    assert tokens("OrderReceipt") == ("orderreceipt",)


def test_the_boundary_splits_a_digit_run_from_a_letter_run_either_way():
    from facts.kind import tokens
    assert tokens("lecture01_introduction") == ("lecture", "01", "introduction")
    assert tokens("week3") == ("week", "3")
    assert tokens("chapter12") == ("chapter", "12")
    assert tokens("2024report") == ("2024", "report")
    # ...and a run with no digit in it is untouched, which is every English word.
    assert tokens("submit") == ("submit",)
    assert tokens("examination") == ("examination",)


def test_the_boundary_re_keys_no_shipped_work_type_term_and_loses_no_reading():
    """Why the rule cannot invent or lose a reading. Measured, not asserted by hope.

    `compile_vocabulary` tokenises the AUTHORED terms with this same function, so a
    boundary that re-segmented a term would re-key the vocabulary. Two facts, both
    measured over the shipped library:

    Of the 944 terms of the four schemas declaring `work_type` -- the one key
    `cli.py` wires -- NOT ONE contains a digit beside a letter, so the compiled key
    set is identical to the one the previous rule produced and the boundary fires on
    the evidence side alone. That is the whole of production.

    Five terms of the two keys nothing wires do re-key: `3d brief` and three more
    `3d ...` under `artifact_type`, and `409a or other common-stock valuation report`
    under `record_type`. They still match, because the SAME function tokenises the
    evidence -- `3D-Brief.docx` and `3d brief` reach the same key from either side --
    and the term's own spelling is what the vocabulary returns. Re-keying is not
    re-reading, and the assertion below is the one that would catch it if it were.
    """
    library = json.loads(
        (Path(__file__).resolve().parents[2] / "src" / "recognition" / "library"
         / "recognition.json").read_text())["schemas"]
    from facts.fields import DOMAIN_FIELDS
    from facts.kind import tokens

    def previous_rule(text):
        out, current = [], []
        for character in text:
            if character.isalnum():
                current.append(character)
            elif current:
                out.append("".join(current).casefold())
                current = []
        if current:
            out.append("".join(current).casefold())
        return tuple(out)

    def authored_for(field_key):
        return [term
                for schema_id, fields in DOMAIN_FIELDS.items()
                if field_key in fields
                for term in library.get(schema_id, {}).get("work_type_terms", ())]

    # Production's key: unchanged, so nothing the product ships is re-keyed at all.
    work_type = authored_for("work_type")
    assert len(work_type) > 900, len(work_type)
    assert [t for t in work_type if tokens(t) != previous_rule(t)] == []

    # The other two: re-keyed, and every one still reaches itself through the
    # compiled vocabulary. A term that stopped matching its own spelling would fail
    # here, which is the failure re-keying could actually cause.
    for field_key in ("artifact_type", "record_type"):
        terms = authored_for(field_key)
        moved = [t for t in terms if tokens(t) != previous_rule(t)]
        assert moved, field_key
        vocabulary = compile_vocabulary(terms)
        for term in moved:
            assert term in terms_in(term, vocabulary=vocabulary), term

    # ...and no two distinct terms were merged onto one key by the new segmentation.
    for field_key in ("work_type", "artifact_type", "record_type"):
        terms = authored_for(field_key)
        def collisions(rule):
            keyed = {}
            for term in terms:
                key = rule(term)
                if key:
                    keyed.setdefault(key, set()).add(term.casefold())
            return {k for k, v in keyed.items() if len(v) > 1}
        assert collisions(tokens) == collisions(previous_rule), field_key


def test_the_producer_and_the_detector_differ_only_at_the_digit_boundary():
    """The drift guard, and the one deliberate exception to it.

    `test_the_tokeniser_agrees_with_the_detectors` still holds everywhere else. The
    detector's tokeniser is NOT changed to match, and the divergence is the point:
    its evidence side carries the structured identifiers that corroborate a schema --
    `PHYS1401`, `E1006`, an HKID's own digits -- and it compares an observation's
    tokens WHOLE against a term (`observation_tokens == tuple(term.split(" "))`).
    Splitting a course code into two tokens there would change the `whole` flag, the
    corroboration gate and the prefix index, all of which decide PROTECTION. Here the
    same split only names a folder. Different consequence, different rule.
    """
    from recognition.detector import _tokens as detector_tokens
    from facts.kind import tokens as producer_tokens
    assert producer_tokens("lecture08_recursion.ipynb") == (
        "lecture", "08", "recursion", "ipynb")
    assert detector_tokens("lecture08_recursion.ipynb") == (
        "lecture08", "recursion", "ipynb")
    # The identifier the detector must keep whole, and does.
    assert detector_tokens("PHYS1401") == ("phys1401",)
    assert producer_tokens("PHYS1401") == ("phys", "1401")


def test_a_model_work_type_outside_the_librarys_vocabulary_is_not_normalizable():
    """CONSTITUTION 3, applied to VALUES: `work_type` is a closed vocabulary field.

    **Measured, cloud run with retrieval on, 2026-09-05.** The rule producer wrote
    `lecture`, `homework`, `exam`, `essay`, `resume` -- every one a member of the
    942-term vocabulary the library ships. The MODEL wrote `.pdf`, `Proposed Scope`,
    `GRC Proposed Scope V2.1` and `Abstract`, none of them members, and one of them
    became a folder: four files were placed into
    `Coursework/Daniel Lacker/IEOR3658/.pdf`.

    `normalize_for_model` is §3.6 check 3 and its promise is already exactly this --
    "the model's value is canonicalised by the SAME rule the deterministic slot uses
    for that field", and a value the field's own rule rejects "is NOT normalizable".
    `work_type`'s rule is a closed vocabulary; it simply had no branch here. Nothing
    is authored: the vocabulary is the library's, the same object `kind_facts` reads.

    The library's own spelling comes back rather than the model's, for the reason
    `KindVocabulary` gives: that spelling becomes a folder name and the document's
    casing must not.
    """
    import cli

    assert cli.normalize_for_model("work_type", ".pdf") is None
    assert cli.normalize_for_model("work_type", "GRC Proposed Scope V2.1") is None
    assert cli.normalize_for_model("work_type", "Lecture") == "lecture"
    assert cli.normalize_for_model("work_type", "  HOMEWORK  ") == "homework"
