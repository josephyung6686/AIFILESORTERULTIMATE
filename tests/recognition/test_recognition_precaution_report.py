# tests/recognition/test_recognition_precaution_report.py
"""The precaution says WHY it holds a file, and the reason is the rules' own.

`104` §18 gap 24. `_precaution` marks a file `sensitive_personal, protected=True,
basis='safety_domain'` when a safety domain stands among an abstention's tied
leaders and one of its WORK TYPES is anywhere in the file's evidence. Measured on
r19 against the owner's hand labels: 16 marks, 5 on truly protected files and 11
on ordinary ones -- `will` (8 of the 11, the modal verb, authored as a legal work
type), `statement` (5), `receipt` (4), `consent form` (3), `medical record` (3),
`visa` (2), `credit card` (2), `endorsement` (2), all in BODY prose on pages 1-4
of long documents that DISCUSS such things without being them.

What reached the store was the class, the flag and a list of observation keys.
Not which of `00`'s four domains was read, not which of its work types was found,
and not where -- so neither the person reading the report nor the local model
being asked to judge the same file could see one word of the reason for the hold.

**THE RULE HAS ONE HOME.** `precaution_report` is where the arithmetic now lives
and `_precaution` reads the schema off it, so a hold and its report can never
disagree about the same file. Every test below asserts both halves together for
that reason.

**THE ZONE IS REPORTED AND NOT TESTED**, and that is measured rather than
preferred. Applying `_names_the_file` -- the naming-zone rule the winning-schema
branch uses -- to this path was measured on r19 as dropping 7 of the 11 false
marks AND 2 of the 5 true ones. It is not the fix, the detector's own docstring
records why, and the two tests at the end of this file are what stop it being
reintroduced as a tidy-looking improvement.
"""
from __future__ import annotations

from evidence_shape.store import RunWriter
from extractors.runs import coverage
from extractors.shape import location, observation, run
from extractors.sink import ExtractionResult
from recognition.detector import (
    Abstention, ENTITY_NAMESPACE, PERSON_ENTITY, Precaution,
)
from test_recognition_detector import (  # the packaged harness
    ACADEMIC, CLOCK, a_file, db, detector, rule_set, schema_entry)  # noqa: F401

#: A safety domain spelled the way the shipped library spells the ones that
#: misfire: one work type that is also ordinary English, one that is a phrase, and
#: context terms that ACCOMPANY such a document without being it.
LEGAL = schema_entry("legal", context=("counsel", "matter"),
                     work_types=("will", "deposition transcript"))


def _name_someone(db, file_id, content_hash):
    """Mint a bare person-entity reading: the corroboration a body-prose work
    type now needs (the owner's ruling of 13 Sep 2026, `Detector._corroborated`)
    -- "a person the entity encoder named anywhere in the file". Neither test
    below is about the PAIRING rule (`00` amendment 7(b), covered in
    `test_entities_hold_a_file.py`); this is the plainest corroborating finding
    that rule also accepts, standing in for a real encoder pass over a file
    that is, in fact, somebody's own.
    """
    observations = (observation(
        file_id=file_id, content_hash=content_hash,
        extractor_name=ENTITY_NAMESPACE + PERSON_ENTITY, extractor_version="0.1.0",
        source_type="text_document", raw_value="Jane Roberts",
        location=location(zone="body"), observed_at=CLOCK,
        reliability="possible"),)
    RunWriter(db, author="P5").write(ExtractionResult(
        run=run(file_id=file_id, content_hash=content_hash,
                extractor_name=ENTITY_NAMESPACE + PERSON_ENTITY,
                extractor_version="0.1.0", source_type="text_document",
                analysis_tier="native", config={}, completeness="complete",
                coverage=coverage("files", 1, 1), observation_count=1,
                started_at=CLOCK, finished_at=CLOCK),
        observations=observations))


def _held(db, file_id, content_hash, rules):
    """The report and the record, from one detector, for one file.

    Both, always, because the property these tests are about is that the two
    agree: a report of a hold nobody took would be a screen inventing a lock, and
    a hold with no report is the r19 defect itself.
    """
    engine = detector(rules)
    outcome = engine.explain(db, file_id, content_hash)
    assert isinstance(outcome, Abstention), outcome
    report = engine.precaution_report(db, outcome, file_id=file_id,
                                      content_hash=content_hash)
    return report, engine(db, file_id, content_hash)


def test_the_report_names_the_domain_the_terms_and_the_zones(db, tmp_path):
    """WHAT THE RULES THOUGHT, in three fields a dossier and a screen can carry.

    A tie at one term each: `legal` on its work type `will`, `academic` on its
    context term `syllabus`. Neither activates a schema -- `never_alone` -- so the
    detector abstains, and the precaution holds the file anyway because `00`:52
    asks for exactly that. What is new is that it can say so.

    SINCE the owner's ruling of 13 Sep 2026, a tied leader's work type in body
    prose corroborates rather than holds alone (measured on the second corpus:
    four files held on the bare word `will` before the change), so the fixture
    also names someone -- the plainest corroborating finding `Detector.
    _corroborated` accepts, short of a second reading of `legal` itself, which
    this rule set authors none of.

    SABOTAGE: return `Precaution(schema_id, (), ())` from `precaution_report`.
    The record is unchanged and every assertion about the reason goes red, which
    is the r19 state stated as a failure.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "notes.pdf",
        body="The syllabus says the deadline will be extended.")
    _name_someone(db, file_id, content_hash)

    report, record = _held(db, file_id, content_hash, rule_set(ACADEMIC, LEGAL))

    assert isinstance(report, Precaution), report
    assert report.schema_id == "legal"
    assert report.terms == ("will",)
    assert report.zones == ("body",)
    # The hold itself is untouched: this gap changes what is SAID about the mark,
    # never whether the mark is made.
    assert record is not None and record.protected is True
    assert record.basis == "safety_domain"


def test_a_file_the_precaution_does_not_hold_reports_nothing(db, tmp_path):
    """The negative twin, without which a report that always answered would pass.

    `syllabus` is `academic`'s context term and nothing here is a safety work
    type, so no hold is taken -- and the report must say so rather than naming a
    domain the rules never read.

    SABOTAGE: drop the `if not readings: return None` arm.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "notes.pdf", body="The syllabus is attached.")

    report, record = _held(db, file_id, content_hash, rule_set(ACADEMIC, LEGAL))

    assert report is None
    assert record is None or record.protected is False


def test_only_a_work_type_is_reported_and_a_context_term_holds_nothing(
        db, tmp_path):
    """A safety domain that is merely MENTIONED is not a safety domain, and the
    report inherits that rule rather than restating it.

    `counsel` is `legal`'s CONTEXT term -- a word that accompanies a legal
    document. `_safety_readings_in_evidence` already refuses it, this reads that
    same answer, and the measured cost of the alternative is in the detector: two
    university syllabi marked `sensitive_personal` by `finance`'s context term
    `credit`, out of "credit hours".

    SABOTAGE: drop the `match.term in self._work_types[...]` test from
    `_safety_work_type_matches`. This goes red and so does the whole of
    `test_recognition_no_safety_evidence`, which is the point: one rule, one home.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "notes.pdf",
        body="The syllabus was reviewed by counsel.")

    report, record = _held(db, file_id, content_hash, rule_set(ACADEMIC, LEGAL))

    assert report is None
    assert record is None or record.protected is False


def test_a_work_type_in_body_prose_still_holds_and_says_where_it_sat(
        db, tmp_path):
    """THE MEASUREMENT THAT FORBIDS THE OBVIOUS FIX, pinned so it stays forbidden.

    `_names_the_file` is the naming-zone rule the winning-schema branch uses, and
    applying it here was measured on r19 as dropping 7 of the 11 false marks and
    2 of the 5 TRUE ones. The precaution therefore holds a work type wherever it
    sits, and reports where it sat so the local model can weigh it -- which is the
    whole of gap 24's answer: say more, decide the same.

    THE ZONE STAYS UNTESTED, AND A SECOND FINDING IS ASKED FOR INSTEAD (the
    owner's ruling of 13 Sep 2026). A body-prose work type alone is exactly the
    shape ten essays and statements were held on before the change, so the
    fixture names someone -- corroboration, not a narrower zone -- and the hold
    stays taken and still says where it sat.

    SABOTAGE: add `and _names_the_file(match)` to `_safety_work_type_matches`, or
    filter `readings` by it in `precaution_report`. This goes red on a body-zone
    hold that r19 says must keep being taken.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "scan001.pdf",
        body="A deposition transcript is attached to the syllabus.")
    _name_someone(db, file_id, content_hash)

    report, record = _held(db, file_id, content_hash, rule_set(ACADEMIC, LEGAL))

    assert report is not None
    assert "body" in report.zones
    assert record is not None and record.protected is True


def test_the_report_and_the_record_answer_together_or_not_at_all(db, tmp_path):
    """ONE RULE, TWO READERS. `cli.ask_the_situation` uses
    `precaution_report(...) is not None` as the exact predicate for "the rules are
    holding this file", so a file the report is silent about and the record marks
    would be a hold no screen counts and no model is asked about -- the r19 defect
    reintroduced through the back door.

    Four files across the two answers, so neither a report that always answers nor
    one that never does can pass.

    SABOTAGE: give `precaution_report` its own copy of the leader test, then
    change one of them.
    """
    rules = rule_set(ACADEMIC, LEGAL)
    corpus = {
        "held.pdf": "The syllabus says the deadline will be extended.",
        "phrase.pdf": "A deposition transcript is attached to the syllabus.",
        "context.pdf": "The syllabus was reviewed by counsel.",
        "plain.pdf": "The syllabus is attached.",
    }
    for name, body in corpus.items():
        file_id, content_hash = a_file(db, tmp_path / name.replace(".", "_"),
                                       name, body=body)
        report, record = _held(db, file_id, content_hash, rules)
        held_by_the_record = record is not None and record.protected
        assert (report is not None) == bool(held_by_the_record), (
            name, report, record)
