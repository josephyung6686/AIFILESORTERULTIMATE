# tests/recognition/test_identifiers_hold_a_file.py
"""`00` amendment 7(a)'s second obligation: the observations HOLD the file.

The ruling of 12 Sep 2026 16:05 says identifier patterns with checksums are a
deterministic extractor "whose observations hold a file exactly as an authored safety
term does". "Exactly as" is the assertion: the same handling class, the same
`protected` flag, the same `basis='safety_domain'`, the same `Precaution` shape --
produced by the same three methods, not by a fifth arm that happens to reach a
similar answer.

**Why it matters, in numbers.** `104` §18.56 graded the second corpus against its
answer key: of the key's 29 protected files the product caught 17 and missed 12, and
four of those misses carried basis `detector` with `protected = 0`, which is
CLOUD-ELIGIBLE ON THE RULES' WORD. Two were health forms. Every file below is that
shape -- a page whose words tell the rules nothing and whose numbers are conclusive.

**The rules are given NOTHING about these domains, deliberately.** The hand-built
rule set here knows one ordinary schema and no safety domain at all, so a hold can
only come from the identifier. A test that also authored `identity` terms could not
tell which half held the file.

**Every hold has its negative twin**, which is this package's own discipline: a page
with no identifier, and a page whose sixteen digits fail Luhn, must come back
unheld -- otherwise these tests would pass under a detector that protected
everything, which is the over-protection collapse `_precaution` records the cost of.
"""
from __future__ import annotations

import pytest

from evidence_shape.store import RunWriter, record_observation, text_units_for_run
from extractors.identifiers import IDENTIFIERS_NAMESPACE, identifier_observations
from extractors.runs import coverage
from extractors.shape import location, observation, run
from extractors.sink import ExtractionResult
from recognition.detector import (
    Abstention, IDENTIFIER_SAFETY_DOMAIN, Precaution, Recognition,
)
from test_recognition_detector import (  # the packaged harness
    ACADEMIC, CLOCK, a_file, db, detector, rule_set, schema_entry)  # noqa: F401

#: The deployment's own number, from the one place it is chosen.
from cli import IDENTIFIER_MASK_TAIL

#: A PASSPORT PAGE whose words name no safety domain. `passport` appears exactly
#: once, as the label the extractor's own vocabulary requires beside the number --
#: and the recogniser never sees it, because `_matches` refuses the identifier rows
#: and this page's body carries no authored term of any schema in the rule set.
PASSPORT_PAGE = """REPUBLIC OF EXAMPLE
Passport No. X1234567
Surname   ROBERTS
Given names   JANE MARIE
Nationality   EXAMPLIAN
Date of birth   11 Apr 1990
Place of issue   CAPITAL CITY
"""

#: A CARD STATEMENT of the kind `104` §18.56 measured going out on the rules' word:
#: a table of numbers whose prose ties nothing.
CARD_STATEMENT = """Monthly summary
Prepared for J M Roberts
Visa 4242 4242 4242 4242
Opening balance 0.00
Purchases 412.35
Closing balance 412.35
"""

#: THE NEGATIVE. A page of ordinary coursework prose with no identifier of any kind.
SYLLABUS_PAGE = """Course outline
The syllabus is posted online and office hours are on Tuesdays.
Problem set 3 is due in week 4. Bring your student card to the first lecture.
"""

#: THE OTHER NEGATIVE, and it is the one a regex would fail. Sixteen digits, a
#: Visa-shaped length, and a check digit that is wrong: a catalogue number.
PRODUCT_PAGE = """Parts list
Product code 1234567812345678 in the catalogue.
Order raised 11/04/1990 and settled.
"""


def a_page(db, tmp_path, filename: str, text: str):
    """One file whose body is `text`, read the way production reads it.

    `a_file` gives the `files` row and the filesystem observation; this adds the
    `text.structured` run that a real extraction writes -- the whole-unit body
    reading and the `text_units` row it stands over -- and then mints the identifier
    readings onto THAT run, which is where they ride (conformance rule 10: the unit a
    span points into is on the reading's own run).

    THE FILENAME IS DELIBERATELY BLAND. `scan001.pdf` carries no authored term, so a
    hold below cannot have come from the file's name sitting in a naming zone --
    which is the evidence `_safety_readings_naming_the_file` reads and is not what
    these tests are about.
    """
    file_id, content_hash = a_file(db, tmp_path, filename)
    run_id = RunWriter(db, author="P5").write(ExtractionResult(
        run=run(file_id=file_id, content_hash=content_hash,
                extractor_name="text.structured", extractor_version="0.4.0",
                source_type="text_document", analysis_tier="native", config={},
                completeness="complete", coverage=coverage("files", 1, 1),
                observation_count=1, started_at=CLOCK, finished_at=CLOCK),
        observations=(observation(
            file_id=file_id, content_hash=content_hash,
            extractor_name="text.structured", extractor_version="0.4.0",
            source_type="text_document", raw_value=text,
            location=location(zone="body"), observed_at=CLOCK,
            reliability="possible"),),
        text_units=({"container_path": (), "text": text, "length": len(text),
                     "truncated": False},)))
    for record in identifier_observations(
            file_id=file_id, content_hash=content_hash,
            source_type="text_document", units=text_units_for_run(db, run_id),
            zone_for=lambda unit: "body", now=CLOCK,
            mask_tail=IDENTIFIER_MASK_TAIL):
        record_observation(db, record)
    return file_id, content_hash


def _held(db, file_id, content_hash, rules=None):
    """The report and the record, from one detector, for one file.

    Both, always: a report of a hold nobody took would be a screen inventing a lock,
    and a hold with no report is `104` §18 gap 24's own defect. The two are computed
    from one set of matches so they cannot disagree, and asserting them together is
    what makes that checkable.
    """
    engine = detector(rules or rule_set(ACADEMIC))
    outcome = engine.explain(db, file_id, content_hash)
    report = engine.precaution_report(db, outcome, file_id=file_id,
                                      content_hash=content_hash)
    return outcome, report, engine(db, file_id, content_hash)


def _identifier_keys(db, file_id, content_hash) -> set[str]:
    return {row[0] for row in db.execute(
        "SELECT observation_key FROM evidence WHERE file_id = ? AND content_hash = ? "
        "AND extractor_name LIKE ? AND superseded_by IS NULL",
        (file_id, content_hash, IDENTIFIERS_NAMESPACE + "%"))}


# --- the two files the ruling was written for -------------------------------------

def test_a_passport_page_is_held_as_identity_on_its_number(db, tmp_path):
    """`00`:52 and `00`:185 for a file whose words say nothing the rules know.

    The page's prose is a passport's prose and the hand-built rule set has no
    `identity` schema at all, so the recognition ABSTAINS -- and the file is still
    held, which is `_precaution`'s own distinction: corroboration governs what we
    CLAIM, precaution governs what we EXPOSE.

    SABOTAGE: drop the identifier arm from `precaution_report`. The record comes back
    unprotected, which is `104` §18.56's measured miss reproduced as a green test.
    """
    file_id, content_hash = a_page(db, tmp_path, "scan001.pdf", PASSPORT_PAGE)

    outcome, report, record = _held(db, file_id, content_hash)

    assert isinstance(outcome, Abstention), outcome
    assert isinstance(report, Precaution), report
    assert report.schema_id == "identity"
    # The terms ARE the kinds, because that is what the reading says: not that the
    # document used the word `passport`, but that the characters on its page are a
    # passport number and a date of birth.
    assert set(report.terms) == {"passport_number", "date_of_birth"}
    assert report.zones == ("body",)

    assert record is not None
    assert record.basis == "safety_domain"
    assert record.protected is True
    assert record.handling_class == "sensitive_personal"
    # §8.4: a record cites what raised IT. What raised this is the identifiers.
    assert set(record.evidence_refs) <= _identifier_keys(db, file_id, content_hash)
    assert set(record.evidence_refs) == set(report.evidence_refs)


def test_a_card_statement_is_held_as_finance_on_a_luhn_valid_number(db, tmp_path):
    """The file `104` §18.56 measured going to the cloud on the rules' word.

    Nothing in this page's prose is an authored finance term in the rule set below,
    and the sixteen digits are conclusive. That asymmetry is the whole of 7(a).
    """
    file_id, content_hash = a_page(db, tmp_path, "scan002.pdf", CARD_STATEMENT)

    outcome, report, record = _held(db, file_id, content_hash)

    assert isinstance(outcome, Abstention), outcome
    assert isinstance(report, Precaution), report
    assert report.schema_id == "finance"
    assert report.terms == ("payment_card",)
    assert record.basis == "safety_domain"
    assert record.protected is True
    assert set(record.evidence_refs) <= _identifier_keys(db, file_id, content_hash)


# --- the negatives ----------------------------------------------------------------

def test_a_page_with_no_identifier_is_not_held(db, tmp_path):
    """"We deliberately did not look" and "we could not tell" stay different answers,
    and so do "this file carries a number" and "this file mentions a card".

    A page of coursework prose. The recogniser may or may not activate `academic` on
    it -- that is not what this asserts -- but nothing may reach `safety_domain`.
    """
    file_id, content_hash = a_page(db, tmp_path, "scan003.pdf", SYLLABUS_PAGE)

    _outcome, report, record = _held(db, file_id, content_hash)

    assert report is None
    assert _identifier_keys(db, file_id, content_hash) == set()
    assert record is None or (record.basis != "safety_domain"
                              and record.protected is False)


def test_sixteen_digits_that_fail_luhn_hold_nothing(db, tmp_path):
    """The negative twin of the card statement, and the one that separates an
    extractor from a regex. Same shape, same length, wrong check digit -- and the
    date beside it is labelled `Order raised`, not a birth."""
    file_id, content_hash = a_page(db, tmp_path, "scan004.pdf", PRODUCT_PAGE)

    _outcome, report, record = _held(db, file_id, content_hash)

    assert _identifier_keys(db, file_id, content_hash) == set()
    assert report is None
    assert record is None or record.basis != "safety_domain"


# --- the seam the hold travels on -------------------------------------------------

def test_an_identifier_reading_is_not_read_as_a_word_the_document_said(db, tmp_path):
    """`_matches` refuses these rows, and the refusal is load-bearing.

    A masked reading's `normalized_value` prints the KIND --
    `medical_record_number …7211` -- so a tokeniser that saw it would find `record`,
    an authored term of a safety domain, and the file would be held by the wrong rule
    citing the wrong evidence. Asserted by naming the kind's own words as terms of an
    ORDINARY schema: if the identifier row reached `_matches`, this file would be
    recognised as that schema, and it is not.
    """
    file_id, content_hash = a_page(db, tmp_path, "scan005.pdf", CARD_STATEMENT)
    #: An ordinary schema whose terms are exactly the words a masked card reading
    #: prints. Nothing on this page says either word.
    decoy = schema_entry("creative", context=("payment", "card"),
                         work_types=("payment card",))

    engine = detector(rule_set(ACADEMIC, decoy))
    outcome = engine.explain(db, file_id, content_hash)

    assert not (isinstance(outcome, Recognition) and outcome.schema_id == "creative")
    matches, _ = engine._matches(db, file_id, content_hash)
    assert all(match.term not in ("payment", "card", "payment card")
               for match in matches), [m.term for m in matches]


def test_a_recognised_file_is_still_held_by_its_identifier(db, tmp_path):
    """The winning-schema arm (`104` §18.26 gap 24b), reached by a checksum.

    A page the rules recognise as coursework that also prints a card number. "Another
    schema described this better" is not one of the exceptions `00`:52 and `00`:185
    allow, and a number is not a mention -- an essay about credit cards contains no
    valid card number -- so the naming-zone rule that guards the authored half is
    deliberately not applied to this one.
    """
    text = SYLLABUS_PAGE + "Course fee charged to Visa 4242 4242 4242 4242.\n"
    file_id, content_hash = a_page(db, tmp_path, "scan006.pdf", text)

    outcome, report, record = _held(db, file_id, content_hash)

    assert isinstance(outcome, Recognition), outcome
    assert outcome.schema_id == "academic"
    assert isinstance(report, Precaution), report
    assert report.schema_id == "finance"
    assert record.basis == "safety_domain"
    assert record.protected is True


def test_every_kind_the_extractor_produces_reaches_one_of_the_four(db, tmp_path):
    """The mapping is closed at import; this asserts it is also LIVE.

    A kind with a domain in the table and no path to a hold would be `104` §18.56's
    miss wearing a table entry, so each kind is put through the whole seam once.
    """
    lines = {
        "payment_card": "Visa 4242 4242 4242 4242 charged.",
        "iban": "Remit to IBAN GB82 WEST 1234 5698 7654 32.",
        "bank_account": "Routing 021000021 Account 1234567890.",
        "us_ssn": "SSN: 078-05-1120 on file.",
        "passport_number": "Passport No. X1234567 expires 2031.",
        "hkid": "Holder HKID A123456(3) at the counter.",
        "date_of_birth": "Jane Marie Roberts 11/04/1990 attended.",
        "medical_record_number": "MRN 4487211 admitted overnight.",
    }
    assert set(lines) == set(IDENTIFIER_SAFETY_DOMAIN)
    for index, (kind, line) in enumerate(sorted(lines.items())):
        file_id, content_hash = a_page(
            db, tmp_path, f"page{index}.pdf", f"Notes\n{line}\n")
        _outcome, report, record = _held(db, file_id, content_hash)
        assert report is not None, kind
        assert report.schema_id == IDENTIFIER_SAFETY_DOMAIN[kind], kind
        assert kind in report.terms, (kind, report.terms)
        assert record.basis == "safety_domain" and record.protected is True, kind
