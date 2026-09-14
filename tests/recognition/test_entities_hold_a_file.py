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

**AND, BY THE OWNER'S RULING OF 13 Sep 2026, THE PAIR ITSELF DOES NOT HOLD ALONE
EITHER.** Measured on the second corpus before the change: the pair held ten
essays and personal statements for every one that was a genuine record. So 7(b)'s
pair now travels the same road as 7(a)'s uncheckable shapes (`00` §18.60): it is
`Detector._corroborated`'s SECOND finding, standing beside a work type the rules
authored, never the first and never alone. The pins below that used to show the
pair holding by itself now show it corroborating a term instead, with the fixture
built to make that explicit; the pins about the PAIRING RULE itself -- which two
things, in which unit -- are unaffected and stand beside an authored term to say so.

The readings are written by the real `extractors.entities.record_entity_readings`
over a fixture reader, so the pins are against the contract that module publishes
rather than against rows this file invented. No identifier readings are minted
(`mint=False`), so a hold here can only have come from 7(b) and the authored
library beside it.
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
    ACADEMIC, CLOCK, FINANCE, MEDICAL, a_file, db, detector, rule_set,
    schema_entry)  # noqa: F401

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


def test_a_name_beside_a_diagnosis_corroborates_but_does_not_hold_alone(
        db, tmp_path):
    """7(b)'s own example, re-argued by the owner's ruling of 13 Sep 2026: the
    ordinary files the rules held "MUST NOT BE HELD", and ten of them were
    essays and personal statements held on a person beside a condition ALONE,
    for every one that was a genuine record. The pair is no longer a hold on
    its own -- `Detector._corroborated` reads it as the SECOND finding a hold
    needs, so with no authored medical term anywhere (the rule set below is
    still one ordinary schema, `00` amendment 7(b)'s own premise) the file
    stays unheld.

    SABOTAGE: drop the `_corroborated` gate from `precaution_report`'s
    abstention arm. The ALONE half below goes green on the pair by itself,
    which is exactly the 13 Sep over-protection `104` §18.60 measured.
    """
    file_id, content_hash = a_page(db, tmp_path, "scan101.pdf", HEALTH_FORM)
    read_entities(db, file_id, content_hash,
                  reader(("person", "Jane Roberts"),
                         ("medical condition", "type 2 diabetes")))

    # ALONE: the rules know nothing about medicine, so the pair holds nothing.
    outcome, report, record = held(db, file_id, content_hash)
    assert isinstance(outcome, Abstention), outcome
    assert report is None
    assert record is None or record.basis != "safety_domain"

    # CORROBORATING: the same pair, beside `medical`'s own authored term "care
    # plan", holds the file -- and the report cites the word AND both readings.
    care_id, care_hash = a_page(
        db, tmp_path, "scan101b.pdf", HEALTH_FORM + "Care plan reviewed.\n")
    read_entities(db, care_id, care_hash,
                  reader(("person", "Jane Roberts"),
                         ("medical condition", "type 2 diabetes")))
    engine = detector(rule_set(ACADEMIC, MEDICAL))
    outcome = engine.explain(db, care_id, care_hash)
    report = engine.precaution_report(db, outcome, file_id=care_id,
                                      content_hash=care_hash)
    record = engine(db, care_id, care_hash)

    assert isinstance(outcome, Abstention), outcome
    assert isinstance(report, Precaution), report
    assert report.schema_id == "medical"
    assert "care plan" in report.terms
    assert {"entities.person", "entities.medical_condition"} <= set(report.terms)
    assert record.basis == "safety_domain"
    assert record.protected is True
    assert record.handling_class == "sensitive_personal"


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


def test_a_name_beside_a_date_of_birth_corroborates_but_does_not_hold_alone(
        db, tmp_path):
    """The other half of the ruling's sentence, re-argued the same way: a date
    of birth is a shape without a check digit -- it is not one of
    `extractors.identifiers.CHECKSUMMED_KINDS` -- and 7(b)'s pair over it is on
    the same terms since the owner's ruling of 13 Sep 2026 (eight club sign-up
    sheets were held on exactly this pair alone, measured on the second
    corpus): it corroborates `identity`'s own term and holds nothing alone.
    """
    file_id, content_hash = a_page(
        db, tmp_path, "scan103.pdf",
        "Registration\nJane Roberts\nBorn 11 April 1990 in Kowloon\n")
    read_entities(db, file_id, content_hash,
                  reader(("person", "Jane Roberts"),
                         ("date of birth", "11 April 1990")))

    # ALONE: the rules author no `identity` schema at all, so the pair holds
    # nothing.
    _outcome, report, record = held(db, file_id, content_hash)
    assert report is None
    assert record is None or record.basis != "safety_domain"

    # CORROBORATING: the same pair, beside `identity`'s own authored term
    # "passport", holds -- and cites the word and both readings.
    identity = schema_entry("identity", context=("nationality",),
                            work_types=("passport",))
    reg_id, reg_hash = a_page(
        db, tmp_path, "scan103b.pdf",
        "Registration\nJane Roberts\nPassport application.\n"
        "Born 11 April 1990 in Kowloon\n")
    read_entities(db, reg_id, reg_hash,
                  reader(("person", "Jane Roberts"),
                         ("date of birth", "11 April 1990")))
    engine = detector(rule_set(ACADEMIC, identity))
    outcome = engine.explain(db, reg_id, reg_hash)
    report = engine.precaution_report(db, outcome, file_id=reg_id,
                                      content_hash=reg_hash)
    record = engine(db, reg_id, reg_hash)

    assert report is not None and report.schema_id == "identity"
    assert "passport" in report.terms
    assert {"entities.person", "entities.date_of_birth"} <= set(report.terms)
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


def test_an_account_number_and_a_medical_record_number_corroborate_but_do_not_hold_alone(
        db, tmp_path):
    """The second table, re-argued by the owner's ruling of 13 Sep 2026.

    `entities.account_number` and `entities.medical_record_number` are the
    ENTITY encoder's OWN readings -- a different table from `extractors.
    identifiers.CHECKSUMMED_KINDS`, which names IDENTIFIER kinds a check digit
    proves. Neither entity term is a member of that frozenset, so since the
    ruling they corroborate an authored term rather than holding a file on
    their own, on the same terms as 7(b)'s pair.
    """
    account, content_hash = a_page(db, tmp_path, "scan106.pdf",
                                   "Summary\nAccount 4021998855 closing balance\n")
    read_entities(db, account, content_hash,
                  reader(("account number", "4021998855")))
    _outcome, report, record = held(db, account, content_hash)
    assert report is None
    assert record is None or record.basis != "safety_domain"

    chart, chart_hash = a_page(db, tmp_path, "scan107.pdf",
                               "Ward list\nRecord 8842119 admitted overnight\n")
    read_entities(db, chart, chart_hash,
                  reader(("medical record number", "8842119")))
    _outcome, report, record = held(db, chart, chart_hash)
    assert report is None
    assert record is None or record.basis != "safety_domain"

    # CORROBORATING: beside `finance`'s own authored term, the account number
    # holds; beside `medical`'s, so does the record number.
    finance_engine = detector(rule_set(ACADEMIC, FINANCE))
    pay_id, pay_hash = a_page(
        db, tmp_path, "scan106b.pdf",
        "Payslip\nAccount 4021998855 closing balance\n")
    read_entities(db, pay_id, pay_hash,
                  reader(("account number", "4021998855")))
    outcome = finance_engine.explain(db, pay_id, pay_hash)
    report = finance_engine.precaution_report(db, outcome, file_id=pay_id,
                                              content_hash=pay_hash)
    record = finance_engine(db, pay_id, pay_hash)
    assert report is not None and report.schema_id == "finance"
    assert "payslip" in report.terms
    assert "entities.account_number" in report.terms
    assert record.protected is True

    medical_engine = detector(rule_set(ACADEMIC, MEDICAL))
    care_id, care_hash = a_page(
        db, tmp_path, "scan107b.pdf",
        "Ward list\nCare plan. Record 8842119 admitted overnight\n")
    read_entities(db, care_id, care_hash,
                  reader(("medical record number", "8842119")))
    outcome = medical_engine.explain(db, care_id, care_hash)
    report = medical_engine.precaution_report(db, outcome, file_id=care_id,
                                              content_hash=care_hash)
    record = medical_engine(db, care_id, care_hash)
    assert report is not None and report.schema_id == "medical"
    assert "care plan" in report.terms
    assert "entities.medical_record_number" in report.terms
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
    local model can weigh a pairing as a pairing.

    SINCE the owner's ruling of 13 Sep 2026 the pairing corroborates rather
    than holds alone, so the fixture also carries `medical`'s own authored
    term ("care plan") -- and the phrase now names BOTH: the word that raised
    the hold and the pairing that corroborated it.
    """
    from model_situation import _held_phrase

    file_id, content_hash = a_page(
        db, tmp_path, "scan109.pdf", HEALTH_FORM + "Care plan reviewed.\n")
    read_entities(db, file_id, content_hash,
                  reader(("person", "Jane Roberts"),
                         ("medical condition", "type 2 diabetes")))
    engine = detector(rule_set(ACADEMIC, MEDICAL))
    outcome = engine.explain(db, file_id, content_hash)
    report = engine.precaution_report(db, outcome, file_id=file_id,
                                      content_hash=content_hash)

    phrase = _held_phrase(report)
    assert "on the work type care plan" in phrase
    assert "on the entities person, medical_condition" in phrase
    assert "identifier" not in phrase


def test_a_unit_naming_many_conditions_beside_a_person_is_writing_about_them(
        db, tmp_path):
    """The owner's ruling of 13 Sep 2026: an author beside a disease term in a
    paper is not a patient record. Measured on the second corpus: a protected
    record's unit names ONE condition beside the person; a paper's names seven to
    thirteen. The deployment states the number (`cli.TOPIC_CONDITION_MENTIONS`).

    RE-ARGUED THE SAME DAY: the pair no longer holds by itself at all (a topic
    paper never did, and now nor does a genuine record's pair on its own), so
    the fixture also carries `medical`'s own authored term ("care plan") to
    give the corroboration gate something to test. `topic_condition_mentions`
    still separates the two, but what it now governs is what the REPORT
    CITES, not whether the file holds: the person named in either paper or
    record already corroborates the word under `Detector._corroborated` --
    "a person the entity encoder named anywhere in the file" -- so a topic
    paper that also carries the word is held on the word alone, and a record
    beside fewer conditions than the threshold is held on the word AND cites
    the pair beside it.
    """
    from recognition.detector import Detector
    from test_recognition_detector import CLOCK, POLICY

    conditions = ["asthma", "type 2 diabetes", "hypertension", "migraine",
                  "glaucoma"]
    paper = ("Review of " + ", ".join(conditions) + " by Jane Roberts. "
             "Care plan noted.\n")
    file_id, content_hash = a_page(db, tmp_path, "review.pdf", paper)
    read_entities(db, file_id, content_hash,
                  reader(("person", "Jane Roberts"),
                         *(("medical condition", c) for c in conditions)))
    engine = Detector(rule_set(ACADEMIC, MEDICAL), handling_for=POLICY,
                      now=lambda: CLOCK, topic_condition_mentions=5)
    outcome = engine.explain(db, file_id, content_hash)
    # AT the number: the pair is excluded, and the hold rests on the word alone.
    at_threshold = engine.precaution_report(db, outcome, file_id=file_id,
                                            content_hash=content_hash)
    assert isinstance(at_threshold, Precaution) and at_threshold.schema_id == "medical"
    assert at_threshold.terms == ("care plan",)

    # Below the number the pair is IN, and the report cites it beside the word.
    lenient = Detector(rule_set(ACADEMIC, MEDICAL), handling_for=POLICY,
                       now=lambda: CLOCK, topic_condition_mentions=6)
    below_threshold = lenient.precaution_report(db, outcome, file_id=file_id,
                                                content_hash=content_hash)
    assert isinstance(below_threshold, Precaution)
    assert below_threshold.schema_id == "medical"
    assert "care plan" in below_threshold.terms
    assert {"entities.person", "entities.medical_condition"} <= set(
        below_threshold.terms)
