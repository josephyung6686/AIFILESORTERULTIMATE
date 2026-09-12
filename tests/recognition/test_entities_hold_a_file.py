# tests/recognition/test_entities_hold_a_file.py
"""`00` amendment 7(b): a person BESIDE something holds the file, and alone does not.

    "a small local entity encoder ... names people, diagnoses, dates of birth and
    identity numbers as observations, and a person beside a diagnosis or an identity
    number holds the file without a model call."

The rule reaches the same three methods 7(a)'s identifiers reach --
`_safety_evidence`, `precaution_report`, `_protect_as` -- so a file held on a pair is
held with the same class, the same flag and the same `basis='safety_domain'` as one
held on an authored term. What is new is the PAIRING, and every pin below is about
that: the same two entities in one unit hold the file, in two units do not, and
either one alone does not.

The readings are written by the real `extractors.entities.record_entity_readings`
over a fixture reader, so the pins are against the contract that module publishes
rather than against rows this file invented. No identifier readings are minted
(`mint=False`), so a hold here can only have come from 7(b).
"""
from __future__ import annotations

from dataclasses import dataclass

from evidence_shape.store import RunWriter
from extractors.entities import record_entity_readings
from extractors.runs import coverage
from extractors.shape import location, observation, run, segment
from extractors.sink import ExtractionResult
from recognition.detector import Abstention, Precaution
from test_recognition_detector import (  # the packaged harness
    ACADEMIC, CLOCK, a_file, db, detector, rule_set)  # noqa: F401

#: The deployment's own, from the one place each is chosen.
from cli import ENTITY_MASKED_LABELS, ENTITY_TAIL_KEPT


@dataclass(frozen=True)
class Found:
    """What `extractors.entities` requires of a reader's finding, and no more."""
    label: str
    start: int
    end: int
    score: float
    text: str


def reader(*labelled: tuple[str, str]):
    """A fixture encoder: each `(label, exact text)` is found wherever it stands.

    Deliberately literal. A pin that ran the real GLiNER weights would be measuring
    the model, and what is under test is the RULE that reads its output.
    """
    def entities(text: str):
        for label, phrase in labelled:
            at = text.find(phrase)
            if at != -1:
                yield Found(label, at, at + len(phrase), 0.9, phrase)
    return entities


def a_page(db, tmp_path, filename: str, *paragraphs: str):
    """One file whose body is these paragraphs, each its OWN text unit.

    Which is what `extractors/structured_text.py` emits for a document with blank
    lines in it: one span-less `body` reading standing over each paragraph, at
    `body:paragraph=N`, with the unit at exactly that path. Two paragraphs are two
    units, and that is the whole of what "beside" is about.
    """
    file_id, content_hash = a_file(db, tmp_path, filename)
    observations, units = [], []
    for index, text in enumerate(paragraphs, start=1):
        container = (segment("paragraph", index=index),)
        observations.append(observation(
            file_id=file_id, content_hash=content_hash,
            extractor_name="text.structured", extractor_version="0.4.0",
            source_type="text_document", raw_value=text,
            location=location(zone="body", container_path=container),
            observed_at=CLOCK, reliability="possible"))
        units.append({"container_path": container, "text": text,
                      "length": len(text), "truncated": False})
    RunWriter(db, author="P5").write(ExtractionResult(
        run=run(file_id=file_id, content_hash=content_hash,
                extractor_name="text.structured", extractor_version="0.4.0",
                source_type="text_document", analysis_tier="native", config={},
                completeness="complete", coverage=coverage("files", 1, 1),
                observation_count=len(observations), started_at=CLOCK,
                finished_at=CLOCK),
        observations=tuple(observations), text_units=tuple(units)))
    return file_id, content_hash


def read_entities(db, file_id, content_hash, entities):
    record_entity_readings(
        db, file_versions=((file_id, content_hash),), entities=entities,
        zones=("body",), char_budget=10_000,
        masked_labels=ENTITY_MASKED_LABELS, tail_kept=ENTITY_TAIL_KEPT,
        now=CLOCK)


def held(db, file_id, content_hash):
    """The report and the record, from one detector, for one file.

    Both, always: a report of a hold nobody took would be a screen inventing a lock,
    and a hold with no report is `104` §18 gap 24's own defect.
    """
    engine = detector(rule_set(ACADEMIC))
    outcome = engine.explain(db, file_id, content_hash)
    report = engine.precaution_report(db, outcome, file_id=file_id,
                                      content_hash=content_hash)
    return outcome, report, engine(db, file_id, content_hash)


HEALTH_FORM = ("Patient intake\n"
               "Name   Jane Roberts\n"
               "Presenting complaint   type 2 diabetes\n")

DISEASE_PAPER = ("A review of type 2 diabetes in adolescent populations, with "
                 "reference to the 2019 cohort and its published outcomes.\n")


def test_a_name_beside_a_diagnosis_holds_the_file_as_medical(db, tmp_path):
    """7(b)'s own example. The rules know nothing about medicine here -- the rule set
    is one ordinary schema -- so the hold can only be the pair.

    SABOTAGE: drop the `people and` test from `_entity_readings`. This still passes
    and the next test goes red, which is why the two are written together.
    """
    file_id, content_hash = a_page(db, tmp_path, "scan101.pdf", HEALTH_FORM)
    read_entities(db, file_id, content_hash,
                  reader(("person", "Jane Roberts"),
                         ("medical condition", "type 2 diabetes")))

    outcome, report, record = held(db, file_id, content_hash)

    assert isinstance(outcome, Abstention), outcome
    assert isinstance(report, Precaution), report
    assert report.schema_id == "medical"
    assert set(report.terms) == {"entities.person", "entities.medical_condition"}
    assert record.basis == "safety_domain"
    assert record.protected is True
    assert record.handling_class == "sensitive_personal"
    # §8.4: a record cites what raised it, and what raised this is BOTH readings.
    assert len(record.evidence_refs) == 2


def test_a_paper_about_a_disease_with_no_person_is_not_held(db, tmp_path):
    """The negative twin, and the reason the rule is a pair rather than a keyword.

    A diagnosis is the subject of an enormous amount of ordinary writing. Holding
    every file that names one is the over-protection collapse `_precaution` records
    -- and it is the same failure as the authored library locking the owner's own
    design notes on the phrase "discharge summary".
    """
    file_id, content_hash = a_page(db, tmp_path, "scan102.pdf", DISEASE_PAPER)
    read_entities(db, file_id, content_hash,
                  reader(("medical condition", "type 2 diabetes")))

    _outcome, report, record = held(db, file_id, content_hash)

    assert report is None
    assert record is None or record.basis != "safety_domain"


def test_a_name_beside_a_date_of_birth_holds_the_file_as_identity(db, tmp_path):
    """The other half of the ruling's sentence, and `identity` is 7(a)'s own reading
    of where a birth date belongs."""
    file_id, content_hash = a_page(
        db, tmp_path, "scan103.pdf",
        "Registration\nJane Roberts\nBorn 11 April 1990 in Kowloon\n")
    read_entities(db, file_id, content_hash,
                  reader(("person", "Jane Roberts"),
                         ("date of birth", "11 April 1990")))

    _outcome, report, record = held(db, file_id, content_hash)

    assert report is not None and report.schema_id == "identity"
    assert set(report.terms) == {"entities.person", "entities.date_of_birth"}
    assert record.basis == "safety_domain" and record.protected is True


def test_a_name_alone_holds_nothing(db, tmp_path):
    """The rule that keeps the corpus usable at all.

    Every document a person owns names somebody. If a name were a lock there would
    be no unlocked file on the disk, and "we deliberately did not look" and "we could
    not tell" would collapse into one answer for the whole corpus.
    """
    file_id, content_hash = a_page(
        db, tmp_path, "scan104.pdf",
        "Minutes\nJane Roberts chaired and the Acme Society approved the budget.\n")
    read_entities(db, file_id, content_hash,
                  reader(("person", "Jane Roberts"),
                         ("organization", "Acme Society")))

    _outcome, report, record = held(db, file_id, content_hash)

    assert report is None
    assert record is None or record.basis != "safety_domain"


def test_beside_means_the_same_unit_and_not_the_same_file(db, tmp_path):
    """WHAT MAKES "BESIDE" A RULE. The same two entities, in two paragraphs.

    Without this the pairing is just co-occurrence anywhere in a document, and a
    lecture handout that names its lecturer on page one and a disease on page nine
    is somebody's health record. The unit is the document's own division --
    `extractors/structured_text.py` cuts paragraphs on the document's blank lines --
    so this asks nothing about distance and holds no number.
    """
    file_id, content_hash = a_page(
        db, tmp_path, "scan105.pdf",
        "Lecture notes by Jane Roberts, spring term.\n",
        "Week nine covers type 2 diabetes and its complications.\n")
    read_entities(db, file_id, content_hash,
                  reader(("person", "Jane Roberts"),
                         ("medical condition", "type 2 diabetes")))

    _outcome, report, record = held(db, file_id, content_hash)

    assert report is None
    assert record is None or record.basis != "safety_domain"


def test_an_account_number_and_a_medical_record_number_need_nobody_beside_them(
        db, tmp_path):
    """The second table. These are issued to a holder and printed on that holder's
    own paper, so the number is already about a person -- and they are the two kinds
    7(a)'s pattern layer holds a file on alone, which the two layers must agree on."""
    account, content_hash = a_page(db, tmp_path, "scan106.pdf",
                                   "Summary\nAccount 4021998855 closing balance\n")
    read_entities(db, account, content_hash,
                  reader(("account number", "4021998855")))
    _outcome, report, record = held(db, account, content_hash)
    assert report is not None and report.schema_id == "finance"
    assert report.terms == ("entities.account_number",)
    assert record.protected is True

    chart, chart_hash = a_page(db, tmp_path, "scan107.pdf",
                               "Ward list\nRecord 8842119 admitted overnight\n")
    read_entities(db, chart, chart_hash,
                  reader(("medical record number", "8842119")))
    _outcome, report, record = held(db, chart, chart_hash)
    assert report is not None and report.schema_id == "medical"
    assert record.protected is True


def test_an_entity_reading_is_not_counted_a_second_time_as_a_word(db, tmp_path):
    """`_matches` refuses these rows, for `104` R-135's reason.

    An entity reading of a named thing IS the document's own characters -- that is
    its contract -- but it is a SECOND ADDRESS for text the host reading already
    carries. Counting both counts one word twice, and `never_alone`'s arity is a
    count: this file's single occurrence of `syllabus` would reach two on its own.
    """
    file_id, content_hash = a_page(
        db, tmp_path, "scan108.pdf",
        "The syllabus is posted by Jane Roberts.\n")
    read_entities(db, file_id, content_hash, reader(("person", "syllabus")))

    engine = detector(rule_set(ACADEMIC))
    matches, _ = engine._matches(db, file_id, content_hash)

    # One: the host body reading. Never the entity copy standing over the same word.
    assert len([match for match in matches if match.term == "syllabus"]) == 1


def test_the_dossier_calls_an_entity_an_entity(db, tmp_path):
    """What site G is TOLD. A pairing the encoder found is neither a word the author
    wrote nor a checksum, and `_held_phrase` says which of the three it is so the
    local model can weigh a pairing as a pairing."""
    from model_situation import _held_phrase

    file_id, content_hash = a_page(db, tmp_path, "scan109.pdf", HEALTH_FORM)
    read_entities(db, file_id, content_hash,
                  reader(("person", "Jane Roberts"),
                         ("medical condition", "type 2 diabetes")))
    _outcome, report, _record = held(db, file_id, content_hash)

    phrase = _held_phrase(report)
    assert "on the entities person, medical_condition" in phrase
    assert "work type" not in phrase and "identifier" not in phrase
