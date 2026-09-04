# tests/p6/test_p6_subject_rule.py
"""`subject`, as the SHIPPED command fills it. A shape is a candidate, not a fact.

**The measurement this file exists to hold shut.** 199 of the owner's real files, run
`academic.coursework`, no model. `subject` was filled by one DIRECT slot over one
regex, `_STRUCTURED`, and scored against the hand-made labels it was **0 correct and
14 wrong** -- every single value it produced on a labelled file was false. The values
it produced most often were postal codes:

    NY11794   x8   Stony Brook, NY 11794 -- an author affiliation
    MD20852   x8   10900 Rockville Pike, MD 20852 -- a mailing address
    VHX7000   x4   a Keyence digital microscope
    UARF470911     a United Airlines booking reference
    U238           uranium-238, out of a physics exam
    BOEING777      an aircraft type, out of a flight itinerary
    USA107         part of `Proc. Natl. Acad. Sci. USA 107, 4335-4340`

`planning/99-SUBJECT-IDENTIFIER-VOCABULARY.md` measured the mechanism: 6,679
observations, 107 survive the pattern, 61 distinct values, and the two commonest
"subjects" on this person's disk are ZIP codes. A `direct` fact outranks anything a
model can propose (§3.6), so a ZIP code beat a right answer about the same file.

**Why the fix is not a better pattern.** `99` §4 measured that too. Tightening the
shape to `[A-Z]{2,4}[ -]?[0-9]{3,4}` takes 61 distinct values to 26 -- and of the 26
exactly one is a course. It removes two REAL courses (`E1006`, `I1403`, one-letter
prefixes) and keeps every flight number. **A shape can narrow this and cannot settle
it.** A department-prefix list was rejected twice by the owner and is not general: it
cannot answer for a university it has never been told about.

**Why the fix is not the sentence encoder either, which was measured here.** The
neighbourhood of every candidate in that run was embedded with the shipped MiniLM
weights and scored against course-language prototypes. It does not separate: the ZIP
code `MD20852` scores 0.296 and outranks BOTH real courses -- `I1403` at 0.266 and
`E1006` at 0.193. The reason is that these documents genuinely ARE academic; the
affiliation block that carries the ZIP code is full of universities and departments.
Topic similarity answers "is this an academic document", and the question here is
"is this token the course", which is a different question.

**So the fix is §3.5's, quoted, and it needed no new machinery.** *"Rules create
validated facts when a candidate passes strict context checks. For example, BUSIB
4300 becomes a course fact only when the engine finds a course-code pattern together
with academic context such as 'syllabus,' 'lecture,' 'credits,' 'instructor,' or
'semester.'"* `facts.rules.apply_rules` has been written and tested since P6 landed
and had no caller; `tests/p6/test_p6_rules_stage_wiring.py` proved the composition
and is titled NOT YET SHIPPED. This file is the shipped half.

Two things change together and neither works alone:

* the DIRECT slot goes. A regex over body text is a JUDGEMENT, and §3.5's direct slot
  "names a location and applies no test to the reading's reliability" -- so a slot is
  structurally the wrong home for it, whatever the pattern says;
* the rule arrives, and with it the `unresolved` row. A refusal is now RECORDED
  against the file rather than being a silence. Measured on the shipped run over the
  owner's 199 files: 158 rows over 51 files say "an identifier was read here and the
  engine declined to call it your subject" -- 89 of them `context_truncated` and 69
  `context_check_failed`. That MORE of them are truncations than considered refusals
  is itself a finding: `context_window` is now load-bearing for this field's recall,
  which it was not while a shape alone could fill it.

**Nothing here is a threshold and nothing here is a vocabulary this repo authored.**
The five context terms are `facts.rules.ACADEMIC_CONTEXT_TERMS`, which are §3.5's own
five words, quoted; the pattern is `cli._STRUCTURED`, already shipped; and the fix
introduces no number at all, so there is nothing for `src/cli.py` to tune.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import cli

from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts.file_facts import RULE, facts_for_file
from facts.states import DIRECT, VALIDATED
from facts.unresolved import unresolved_for_file
from facts.values import values_in_field

CLOCK = "2026-08-19T12:00:00+00:00"

#: The eleven values the owner was shown, with the neighbourhood each one actually
#: sits in, copied from the `evidence` rows of the measured run. The left half is
#: what the product called a COURSE; the right half is why nobody would.
#:
#: `context_before` is the 200 characters P4 kept before the reading and
#: `context_after` the 200 after, both truncated as the real rows are.
JUNK: tuple[tuple[str, str, str], ...] = (
    ("VHX7000",
     "the thickness and diameter of the grafts were measured using a Keyence ",
     " microscope."),
    ("UARF470911",
     "Issuing Airline: UNITED AIRLINES\nIATA Number: 13305040\nFrequent Flyer No: ",
     " FOID:\nCustomer Number:\nITINERARY:\nFLIGHT STOP/EQP"),
    ("MA01923",
     "please contact Copyright Clearance\nCenter, 222 Rosewood Drive, Danvers, ",
     ", or fax 978-750-4470.\nLIMIT OF LIABILITY/DISCLAIMER OF WARRANTY:"),
    ("NY11794",
     "Department of Materials Science and Chemical Engineering, "
     "Stony Brook University, Stony Brook, ",
     ", 7 Department of Neurological Surgery, Stony Brook University Medical Center"),
    ("MD20852",
     "1Corresponding Author: Yung Hau Hong Joseph, Georgetown Preparatory School, "
     "10900 Rockville Pike, North Bethesda, ",
     ", United States. josephyung33@gmail.com "),
    ("U238", "   U   (", ")                U (U-235)"),
    ("DSC250",
     "[Configuration]\r\nCompany Name\tStonybrook Univ\r\n"
     "Instrument Name\tDSC2-01778\r\nInstrument Type\t",
     "\r\nSerial Number\tDSC2-01778\r\nIP\t192.168.10.2\r\n"
     "Location of Instrument\tStonybrook Univ"),
    ("BOEING777",
     "WED 24AUG DEP TAIWAN TAOYUAN INTL 09:50 UA872 NON-STOP\n"
     "TERMINAL 2 PREMIUM ECONOMY/O ",
     "-300ER JET\nARR SAN FRANCISCO INTL 06:50 CONFIRMED"),
    ("USA107",
     "pluripotent stem cells follows developmental principles but with\n"
     "variable potency. Proc. Natl. Acad. Sci. ",
     ", 4335-4340.\nIoffe, S., and Szegedy, C. (2015). Batch normalization:"),
    ("SBDD153",
     "业务类型 2025 年度收入 "
     "2024 年度收入\nDEL 249,817,848.09 199,278,048.75 25.36\nFBDD/",
     ",767,822.21 120,220,383.75 27.90\nOBT 75,260,445.56 48,034,038.54 56.68"),
    ("V2022", "(17)\tMethods-Statement-", ".Pdf. "),
)

#: The right column of `99` §3: readings that ARE what their document is about,
#: printed the way people print them, beside the words a course is described with.
#:
#: The last is BYTE-EXACT from the owner's own files, and it is the reason the
#: context vocabulary is not §3.5's five words alone -- none of the five literal
#: terms appears anywhere near it; `ELTU3017` sits next to a URL containing
#: "courses".
#:
#: **TWO ROWS LEFT THIS TUPLE ON 2026-09-05 AND THE CLAIM THEY CARRIED WAS FALSE.**
#: `E1006` and `I 1403` were listed here as real courses the product "must keep",
#: on a measurement that silencing them costs four of five working placements. The
#: ground-truth labels were then scored against the values themselves: the rule
#: produced eleven `subject` facts over the 215-file corpus and ALL ELEVEN are
#: wrong, these two among them. They are fragments, not courses -- see
#: `TRUNCATIONS` below -- and the placements they were propping up were placements
#: into a folder named after half a token.
COURSES: tuple[tuple[str, str, str, str], ...] = (
    ("PHYS 1401", "Syllabus - ", " Introductory Physics", "PHYS1401"),
    ("BUSIB 4300", "Course ", " meets Tuesdays; the instructor is Dr. Ramirez.",
     "BUSIB4300"),
    ("COMS-4995", "Advanced topics, ",
     ", 3 credits. Prerequisite: COMS 3134.", "COMS4995"),
    ("E1006", "# ENGI ",
     ": Introduction to Computing\n## Lecture 1: Course Overview", "E1006"),
    ("ELTU3017", "The Chinese University of Hong Kong. ",
     ": Medicine in the Humanities. English\nLanguage Teaching Unit, "
     "eltu.cuhk.edu.hk/courses/eltu3017/.", "ELTU3017"),
)

#: THE THIRD REFUSAL: A SINGLE CAPITAL BEFORE THE NUMBER IS NOT A DEPARTMENT.
#: Both readings are byte-exact from the owner's disk, both were `COURSES` rows
#: until 2026-09-05, and both are FRAGMENTS of something longer that the shape cut
#: in half. Read the neighbourhood, which is the whole argument:
#:
#: * `E1006` is preceded by `ENGI ` -- the course is `ENGI E1006`, Columbia's own
#:   spelling, and the letter the shape kept is the SUFFIX of a prefix it dropped;
#: * `I 1403` is preceded by `General Chemistry ` -- the `I` is the roman numeral
#:   that ends "General Chemistry I", a word of the sentence and not a code at all.
#:
#: MEASURED, AND IT IS WHY THIS IS NOT A JUDGEMENT CALL. Over the owner's 215-file
#: ground-truth corpus the rule produced ELEVEN `subject` facts and the labels score
#: ALL ELEVEN wrong; eight of the eleven are these two values (`E1006` on 5 files,
#: `I1403` on 3). Neither truncation is recoverable either: the labels want
#: `PYTHON1006` and `PHYS1403`, and no document in the corpus prints either string,
#: so there is no better value to reach for. "Absent means refuse, never guess."
TRUNCATIONS: tuple[tuple[str, str, str], ...] = (
    ("I 1403", "General Chemistry ",
     " Dr. Beer\nSample Exam 2\nProvide the best possible answer to the question."),
    # The same defect wherever a title ends in a capital. Neither is on the owner's
    # disk; both are what the refusal is FOR, and a fix that only knew `Chemistry I`
    # would be a fix for one document.
    ("A 2150", "Music Theory ", " Prof. Vaughan\nMidterm exam, 3 credits."),
    ("B 4100", "Organic Chemistry ", "\nProblem set 2. Instructor: Dr. Lin."),
)


#: THE TWO EXCLUSIONS THE VOCABULARY MAKES, each with the real reading that made
#: the case. Neither may become a `subject`, and neither is refused by the shape.
#:
#: `MD20852` is the harder one and it is why "grade" is not a context term: it is
#: the owner's own high-school transcript, an unambiguously academic document, and
#: the ZIP code of the school's address is the ONLY identifier printed on it -- so
#: no margin, no position and no uniqueness test can help. Only the vocabulary can,
#: and only if it excludes a word whose commonest sense ("Grade Enrolled: 9", a
#: school YEAR) is not an act of teaching.
#:
#: `RATE2018` is why "quarter" is not one: a financial table column reading
#: "2022 Q3 12 months ending with quarter".
AMBIGUOUS_NEIGHBOURS: tuple[tuple[str, str, str], ...] = (
    ("MD20852",
     "Georgetown Preparatory School\n10900 Rockville Pike\nNorth Bethesda, ",
     "\n(301) 493-5000\nHau Hong Joseph Yung Birth Date: 03/30/2007\n"
     "Grade Enrolled: 9\nKa Ning Path, Tai Hang, Hong Kong Island"),
    ("RATE2018",
     "<th>2022 Q3 12 months ending with quarter</th>", "</th>\n<tbody>"),
)

#: AND THE ONE THAT DECIDES THE WHOLE DESIGN. Every postal code in `99` §3 lives
#: in an author-affiliation block, and an affiliation block is DENSE with the
#: words a naive "academic context" list would hold: university, school, faculty,
#: department, institute. So an INSTITUTION vocabulary admits every ZIP code in
#: the corpus, and the vocabulary has to be about TEACHING instead. This reading
#: is byte-exact from `Abstract- Characterizing Mechanical Properties...docx`.
INSTITUTION_NEIGHBOUR: tuple[str, str, str] = (
    "MA01003",
    ", 3University of Massachusetts Amherst, Amherst, ",
    ", 4 University of Oxford, Oxford, UK, 5 SUNY Geneseo, Geneseo, NY, "
    "6 Department of Materials Science and Chemical Engineering")


def _file(conn, tmp_path, *, name="notes.pdf", body=b"a document"):
    path = tmp_path / "Downloads" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _located(conn, *, file_id, content_hash, raw, before="", after="",
             truncated=False, zone="body", run_id="run-1", start=0,
             container_path=(Segment("page", index=1),)):
    """P4's structured-string observation: a substring the finder located on a page.

    The span is the reason the DIRECT slot could ever see it -- `cli.
    reads_a_structured_string` admits a `body`/`heading` locator carrying a `#` -- so
    every reading built here is one the old slot WOULD have claimed. That is the
    point: the tests below are asked of readings the shipped product really sees.
    """
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="0.1.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    record_observation(conn, Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="0.1.0", source_type="text_document", raw_value=raw,
        location=Location(zone, container_path,
                          text_span=TextSpan(start, start + len(raw))),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id=run_id, context_before=before, context_after=after,
        context_truncated=truncated))


def _subjects(conn, file_id, content_hash) -> set[tuple[str, str, str]]:
    """Every `subject` the SHIPPED deterministic pass reaches, with how it reached it.

    Both stages, in the order `FactResolver` runs them, so a value that arrives from
    either producer is visible and the reliability it arrived with is not assumed.
    """
    cli._direct_stage(conn, file_id=file_id, content_hash=content_hash)
    cli._rule_stage(conn, file_id=file_id, content_hash=content_hash)
    by_id = {row["value_id"]: row["canonical_value"]
             for row in values_in_field(conn, "subject")}
    return {(by_id[row["value_id"]], row["reliability_state"], row["origin"])
            for row in facts_for_file(conn, file_id, content_hash)
            if row["field_key"] == "subject"}


def _refusals(conn, file_id, content_hash) -> list[str]:
    return [row["reason"] for row in unresolved_for_file(conn, file_id, content_hash)
            if row["field_key"] == "subject"]


@pytest.mark.parametrize("raw,before,after", JUNK,
                         ids=[one[0] for one in JUNK])
def test_none_of_the_eleven_things_the_owner_was_shown_is_a_subject(
        p6_conn, tmp_path, raw, before, after):
    """THE DEFECT, one row at a time, with each value's real neighbourhood.

    A microscope, a booking reference, three postal codes, an isotope, an
    instrument, an aircraft, a journal citation, a Chinese financial report line and
    a version string. Not one of them is a course, and the evidence that says so is
    the words beside it -- never the shape, which is identical in all eleven.
    """
    file_id, content_hash = _file(p6_conn, tmp_path)
    _located(p6_conn, file_id=file_id, content_hash=content_hash,
             raw=raw, before=before, after=after)

    assert _subjects(p6_conn, file_id, content_hash) == set()


@pytest.mark.parametrize("raw,before,after,expected", COURSES,
                         ids=[one[0] for one in COURSES])
def test_a_code_beside_the_words_a_course_is_described_with_is_a_subject(
        p6_conn, tmp_path, raw, before, after, expected):
    """The other half, and the reason refusing everything is not the fix.

    §3.5's own worked example is `BUSIB 4300`, and the four here are one per
    context term the design states. The value is CANONICAL -- `PHYS 1401` and
    `PHYS1401` are one course (`65` §4.2: four files of one course became four
    one-file groups and the folder was proposed empty) -- and the reliability is
    `validated`, never `direct`, so a person or a model can still overrule it.
    """
    file_id, content_hash = _file(p6_conn, tmp_path)
    _located(p6_conn, file_id=file_id, content_hash=content_hash,
             raw=raw, before=before, after=after)

    assert _subjects(p6_conn, file_id, content_hash) == {
        (expected, VALIDATED, RULE)}

@pytest.mark.parametrize("raw,before,after", TRUNCATIONS,
                         ids=[one[0] for one in TRUNCATIONS])
def test_a_partial_identifier_is_refused_rather_than_stored(
        p6_conn, tmp_path, raw, before, after):
    """A rule that emits half a token is worse than one that declines.

    Both of these clear the context check outright -- `Lecture` sits beside one and
    `Sample Exam` beside the other -- so the vocabulary cannot refuse them and only
    the shape can. What it refuses is the SINGLE LEADING CAPITAL: a department
    abbreviation is two letters or more in every catalogue this product will meet,
    and a lone capital before a number is either a word of the surrounding sentence
    (`Chemistry I`) or the tail of a prefix the match dropped (`ENGI E1006`).

    THE COST OF NOT REFUSING IS NOT THE FIELD, IT IS THE FOLDERS. A wrong `subject`
    is conflicting evidence for every other file that shares its neighbourhood, and
    `planning/101` measured the mechanism on this same corpus: junk identifier
    values suppressed 258 destination nodes. A refusal costs one file its leaf; a
    confident fragment costs a whole branch.
    """
    file_id, content_hash = _file(p6_conn, tmp_path)
    _located(p6_conn, file_id=file_id, content_hash=content_hash,
             raw=raw, before=before, after=after)

    assert _subjects(p6_conn, file_id, content_hash) == set()

@pytest.mark.parametrize("raw,before,after", AMBIGUOUS_NEIGHBOURS,
                         ids=[one[0] for one in AMBIGUOUS_NEIGHBOURS])
def test_a_word_whose_commonest_sense_is_not_teaching_admits_nothing(
        p6_conn, tmp_path, raw, before, after):
    """THE COST OF EVERY WORD IN THE VOCABULARY, PAID BY THESE TWO.

    Widening §3.5's five terms is the only thing that recovers `ELTU3017`,
    and every word added is a way back in for something that is not a
    course. These two are what "grade" and "quarter" let through when the list was
    first drawn, and they are kept here as the boundary: a term earns its place by
    naming an act of TEACHING, not by appearing in academic documents.

    `MD20852` is the sharp one. It is the owner's own school transcript -- as
    academic a document as exists -- and the school's postal code is the ONLY
    identifier on the page. No margin, no uniqueness rule and no position rule can
    refuse it, because there is nothing to outrank and nowhere better in the
    document. The vocabulary is the only gate that sees it, so the vocabulary is
    where the discipline has to be.
    """
    file_id, content_hash = _file(p6_conn, tmp_path)
    _located(p6_conn, file_id=file_id, content_hash=content_hash,
             raw=raw, before=before, after=after)

    assert _subjects(p6_conn, file_id, content_hash) == set()


def test_an_institution_is_not_an_act_of_teaching(p6_conn, tmp_path):
    """THE RULING THAT SHAPES THE WHOLE LIST, and the measurement behind it.

    Every postal code in `99` §3 -- `NY11794`, `MD20852`, `MA01003`, `IN46256`,
    `NY10172`, `CA94588`, `MA01923` -- sits in an author-affiliation block, and an
    affiliation block is the densest academic prose in the corpus: universities,
    faculties, departments, institutes, medical centres. A context vocabulary built
    from the words that make a document ACADEMIC therefore admits every one of
    them, which is also why the sentence encoder failed here (see this file's
    header: `MD20852` scores 0.296 and outranks both real courses).

    So the list contains no institution word, and this test is what says so. The
    reading below carries `University` twice, `Department`, `SUNY` and a named
    faculty, and states a postal code that must never name a folder.
    """
    raw, before, after = INSTITUTION_NEIGHBOUR
    file_id, content_hash = _file(p6_conn, tmp_path)
    _located(p6_conn, file_id=file_id, content_hash=content_hash,
             raw=raw, before=before, after=after)

    assert _subjects(p6_conn, file_id, content_hash) == set()


def test_the_designs_own_five_words_are_all_still_context_terms(p6_conn, tmp_path):
    """The deployment WIDENED §3.5's list; it did not replace it.

    `facts.rules.ACADEMIC_CONTEXT_TERMS` is the design's five, quoted, and that
    module refuses a sixth on purpose -- "adding one is a design change, not an
    implementation detail". The sixth and the twenty-sixth are the DEPLOYMENT's,
    which is the same seam every pattern in `cli.py` arrives through, and the five
    remain a subset so no document that used to fill stops filling.
    """
    from facts.rules import ACADEMIC_CONTEXT_TERMS

    assert set(ACADEMIC_CONTEXT_TERMS) <= set(cli.SUBJECT_RULE.required_context_terms)
    for term in ACADEMIC_CONTEXT_TERMS:
        assert term in cli.SUBJECT_CONTEXT_TERMS


def test_no_shape_alone_reaches_direct_any_more(p6_conn, tmp_path):
    """§3.6 is why this is the load-bearing half.

    `direct` outranks every state a model can propose, so while the slot shipped, a
    ZIP code could not be corrected by asking a better question -- the right answer
    arrived and lost. After this, the deterministic path cannot state a `subject` at
    `direct` at all: no shipped slot claims the field.
    """
    file_id, content_hash = _file(p6_conn, tmp_path)
    _located(p6_conn, file_id=file_id, content_hash=content_hash,
             raw="NY11794", before="Stony Brook, ", after=", United States")

    cli._direct_stage(p6_conn, file_id=file_id, content_hash=content_hash)

    assert facts_for_file(p6_conn, file_id, content_hash) == []
    assert "subject" not in {slot.field_key for slot in cli.DIRECT_SLOTS.slots}
    assert DIRECT not in {state for _, state, _ in
                          _subjects(p6_conn, file_id, content_hash)}


def test_a_refusal_is_written_down_and_says_which_kind_it_was(p6_conn, tmp_path):
    """§8.2 and §8.6. Silence and refusal are different records, and both are kept.

    Deleting the slot alone would make the eleven values vanish without a trace,
    which is a worse product: nobody could see that the engine had read
    `NY 11794` and decided against it. `apply_rules` writes the row, and it
    distinguishes the two honest answers -- `context_check_failed` is "we looked and
    the words were not there", `context_truncated` is "P4 cut the context and we
    could not see far enough to look". Reporting the first when the second happened
    would claim a considered refusal that was never made.
    """
    file_id, content_hash = _file(p6_conn, tmp_path)
    _located(p6_conn, file_id=file_id, content_hash=content_hash,
             raw="NY11794", before="Stony Brook, ", after=", United States")
    cli._rule_stage(p6_conn, file_id=file_id, content_hash=content_hash)
    assert _refusals(p6_conn, file_id, content_hash) == ["context_check_failed"]

    cut_id, cut_hash = _file(p6_conn, tmp_path, name="long.pdf", body=b"a long one")
    _located(p6_conn, file_id=cut_id, content_hash=cut_hash, run_id="run-2",
             raw="VHX7000", before="measured using a Keyence ",
             after=" microscope.", truncated=True)
    cli._rule_stage(p6_conn, file_id=cut_id, content_hash=cut_hash)
    assert _refusals(p6_conn, cut_id, cut_hash) == ["context_truncated"]


def test_a_term_written_in_capitals_is_still_not_a_course(p6_conn, tmp_path):
    """THE RECORDED INCIDENT, re-armed against the producer that replaced the slot.

    `cli.py`'s own comment: `AY 2024-25` was worse than nothing -- `_STRUCTURED`
    claimed `AY 2024` and filed a person's essays under a course called AY2024. The
    slot kept its distance with `not _is_term(raw)`, a predicate over the reading.
    `facts.rules.Rule` has NO such predicate: it carries a pattern, a context list
    and a field. So the refusal has to live in the pattern, and a semester written in
    capitals next to the word `semester` is exactly the reading that would otherwise
    walk straight through the context check.
    """
    for run, raw in enumerate(("SPRING 2026", "SPRING2026", "AY 2024-25")):
        file_id, content_hash = _file(p6_conn, tmp_path, name=f"t{run}.pdf",
                                      body=f"term {run}".encode())
        _located(p6_conn, file_id=file_id, content_hash=content_hash,
                 run_id=f"run-t{run}", raw=raw,
                 before="Syllabus for the ", after=" semester, 3 credits.")

        assert _subjects(p6_conn, file_id, content_hash) == set(), raw


def test_a_whole_page_that_merely_contains_a_course_code_is_not_a_subject(
        p6_conn, tmp_path):
    """`apply_rules` SEARCHES the reading; the slot it replaces MATCHED the locator.

    That difference is a widening, and it has a measured precedent: admitting whole
    zones produced a proposed folder named "Fudan application checklist [x]
    transcript [x] personal statement [ ] recommendation [ ] HSK certificate". The
    old slot excluded whole pages by refusing a span-less locator; the rule has no
    locator to look at, so the pattern is anchored to the WHOLE reading instead. A
    located identifier is exactly its match -- `extract_pdf` slices it out as
    `raw = unit_text[start:end]` -- so anchoring costs nothing real and refuses every
    page, heading and paragraph that merely contains one.

    Simulated over the owner's 6,679 real observations before the change was made:
    bare `search` writes 214 `context_check_failed` rows against the anchored
    pattern's 93, and BOTH produce the same five facts. The 121 extra rows are
    pages, not identifiers. (The shipped run's own totals are in this file's
    header and are smaller again, because the anchors also keep the rule off the
    whole-zone readings the simulation counted.)

    **The context has to PASS for this test to be about the anchors.** Written first
    with an empty context, it went GREEN under a sabotaged pattern with the anchors
    removed -- the context check was refusing the page and the anchors were never
    asked, so the test proved nothing and said it did. The page below carries the
    words §3.5 demands, which leaves the anchor as the only thing between a whole
    paragraph and a folder named after it.
    """
    file_id, content_hash = _file(p6_conn, tmp_path)
    _located(p6_conn, file_id=file_id, content_hash=content_hash,
             raw="Week 3 covers PHYS 1401 and the reading for it.",
             before="Syllabus, page 2. ",
             after=" Lecture times, credits and the instructor are below.",
             start=0)

    assert _subjects(p6_conn, file_id, content_hash) == set()


def test_the_deployment_still_reads_every_identifier_it_ever_read(p6_conn,
                                                                  tmp_path):
    """What did NOT change, and the line between seeing and asserting.

    `65` §2.2 records widening extraction as a privacy trade-off and `cli.py` states
    the posture: what the product SEES and what the product ASSERTS are two knobs.
    Only the second one moved. `_STRUCTURED` is untouched, so P4 still stores the
    same readings, `recognition`'s `_identifier_observations` still gets the same
    identifiers, and a future producer with better evidence loses nothing.
    """
    assert cli._STRUCTURED.fullmatch("PHYS1401") is not None
    assert cli._STRUCTURED.fullmatch("NY11794") is not None
    text = "Homework for PHYS 1401 at Stony Brook, NY 11794"
    assert [text[one.start:one.end] for one in cli.find_structured_strings(text)] == [
        "PHYS 1401", "NY 11794"]
