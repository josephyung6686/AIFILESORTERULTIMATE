# tests/recognition/test_recognition_protection_zone.py
"""Protection reads what a file CALLS ITSELF, not every word inside it.

`_safety_readings_in_evidence` already refuses a term that merely SURROUNDS a
document: only a `work_type_term` may protect, never a `context_term`. That fixed
`credit`, out of "credit hours", protecting a syllabus.

It did not fix the other half. `will`, `statement`, `receipt`, `invoice` and
`passport` are authored as work types AND are ordinary English, so one of them
anywhere in a document's prose protected it. Measured over a real 639-file corpus,
33 files were locked `sensitive_personal, protected=1` -- withheld from placement
entirely -- by:

    will 19 . statement 14 . receipt 5 . invoice 3 . passport 1

Among them `Arduino/libraries/SD/LICENSE.txt` (on "receipt", "statement", "will"),
`rp2040-datasheet.pdf` -- a chip datasheet -- on the word "will", and the owner's
own design notes for THIS PRODUCT on the phrase "discharge summary".

ARITY DOES NOT SEPARATE THESE, and was tried first. Requiring two distinct work
types keeps `LICENSE.txt` protected -- it has three generic words -- and releases
`Statement.pdf`, a real brokerage statement. Wrong in both directions.

WHERE the term sits separates them exactly. Of those 33 files, ONE carries its work
type in a naming zone -- `Statement.pdf`, whose filename is the word -- and it is
the one file judged genuine. The other 32 are body prose.

This is not a new rule. `_matches`'s own docstring cites it: *"SPEC 2.2 ranks 'a
filename, title, or page-one heading' as meaningful evidence"*. The protection path
now reads the ranking the design already states.

SCOPE, deliberately narrow: this governs the path where ANOTHER schema won and a
safety domain is raised over it, plus the tied-abstention path. A safety domain that
WINS outright is protected by its own handling and never reaches here -- a file the
detector reads AS a payslip is a payslip wherever its terms sit.
"""
from __future__ import annotations

from recognition.detector import NAMING_ZONES
from test_recognition_detector import (  # the packaged harness
    ACADEMIC, CLOCK, a_file, db, detector, rule_set, schema_entry)  # noqa: F401

#: A safety domain whose work types are the two shapes that matter: one ordinary
#: English word, and one specific phrase. Both are how the real library spells them.
FINANCE_GENERIC = schema_entry(
    "finance", context=("account", "total"), work_types=("statement", "receipt"))


def test_the_naming_zones_are_the_ones_spec_2_2_ranks():
    """filename, title, heading -- and the two that are a heading by another name.

    `header_footer` is a running head: a page-one heading, on page two. `metadata`
    is the format's own title slot -- a document naming itself in its own words.

    `body`, `table`, `ocr`, `notes` and `annotation` are NOT here, and that is the
    whole point: they are where a document mentions OTHER documents.
    """
    assert NAMING_ZONES == frozenset(
        {"filename", "title", "heading", "header_footer", "metadata"})


def test_body_and_table_and_ocr_are_not_naming_zones():
    """The negative twin of the zone list -- pinning the three that carried the 32."""
    assert not (NAMING_ZONES & {"body", "table", "ocr"})


def test_a_work_type_in_the_filename_still_protects(db, tmp_path):
    """`Statement.pdf`. This is the capability, and it has to keep working."""
    file_id, content_hash = a_file(
        db, tmp_path, "Statement.pdf",
        body="Syllabus and office hours for the term.")
    record = detector(rule_set(ACADEMIC, FINANCE_GENERIC))(db, file_id, content_hash)
    assert record is not None
    assert record.protected is True
    assert record.basis == "safety_domain"


def test_the_same_word_in_body_prose_does_not_protect(db, tmp_path):
    """`LICENSE.txt`: "...no receipt or statement shall be implied...".

    Same word, same schema, same rule set as the test above. Only the zone differs,
    which is the whole claim.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "LICENSE.txt", extension=".txt",
        # ONE finance work type, so `academic` wins on two terms and the file
        # reaches the winning-schema override -- which is the path 34 of the real
        # corpus's 35 locks came through. Two would tie, and a tie is
        # `_precaution`'s path, which is governed by arity instead.
        body="Syllabus and office hours for the term. No statement shall be "
             "implied by this licence.")
    record = detector(rule_set(ACADEMIC, FINANCE_GENERIC))(db, file_id, content_hash)
    assert record is None or record.protected is False


def test_a_datasheet_is_not_sensitive_for_saying_will(db, tmp_path):
    """`rp2040-datasheet.pdf`, locked on the commonest modal verb in English."""
    legal = schema_entry("legal", context=("clause",), work_types=("will",))
    file_id, content_hash = a_file(
        db, tmp_path, "rp2040-datasheet.pdf",
        body="Syllabus and office hours. The processor will assert the interrupt.")
    record = detector(rule_set(ACADEMIC, legal))(db, file_id, content_hash)
    assert record is None or record.protected is False


def test_notes_naming_a_document_kind_do_not_become_that_kind(db, tmp_path):
    """The owner's own product notes, locked on the phrase "discharge summary".

    The case arity could not reach: a SPECIFIC multi-word work type, in prose. Two
    distinct terms would have kept this protected; the zone rule releases it.
    """
    medical = schema_entry("medical", context=("referral",),
                           work_types=("discharge summary", "care plan"))
    file_id, content_hash = a_file(
        db, tmp_path, "frontend_impl_guide.md", extension=".md",
        body="Syllabus and office hours. Worked example: classifying a discharge "
             "summary from a scanner.")
    record = detector(rule_set(ACADEMIC, medical))(db, file_id, content_hash)
    assert record is None or record.protected is False


def test_a_safety_domain_that_wins_outright_is_still_protected(db, tmp_path):
    """The scope boundary, and the guard against over-correcting.

    Nothing above may weaken the ordinary case. A file the detector reads AS
    finance -- its own schema winning on its own terms -- is protected wherever
    those terms sit, because it never reaches the override path at all.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "scan.pdf",
        body="Statement of account. Total and receipt enclosed.")
    record = detector(rule_set(FINANCE_GENERIC))(db, file_id, content_hash)
    assert record is not None
    assert record.protected is True
    assert record.basis == "safety_domain"


# --------------------------------------------------------------------------
# SPEC 2.2 says "page-one heading", and the page is in the record.
# --------------------------------------------------------------------------

def test_a_heading_deep_in_a_document_is_not_where_it_names_itself(db, tmp_path):
    """`rp2040-datasheet.pdf` again -- it survived the zone rule on a HEADING.

    `pdf.text` calls a line a heading when its type is larger than the page's body
    size. That is a typographic guess, not a semantic one, so a large-set sentence
    fragment deep in a 642-page datasheet -- "The next attempt to claim the l..."
    -- arrives zoned `heading`. Measured: a World History textbook was locked the
    same way on "dispensation. Are you ready to receive it? Will you".

    SPEC 2.2's words are "a filename, title, or page-one HEADING", and the page is
    recorded in `container_path`. Reading the whole phrase separates these from
    `Statement.pdf`, whose heading -- "Statement of assets as of 09.01.2025" -- is
    on page one.
    """
    legal = schema_entry("legal", context=("clause",), work_types=("will",))
    file_id, content_hash = a_file(
        db, tmp_path, "datasheet.pdf",
        body="Syllabus and office hours.",
        heading="The processor will assert the interrupt", heading_page=7)
    record = detector(rule_set(ACADEMIC, legal))(db, file_id, content_hash)
    assert record is None or record.protected is False


def test_a_page_one_heading_still_protects(db, tmp_path):
    """`Statement.pdf`'s own heading. The capability, on the other side of the cut."""
    file_id, content_hash = a_file(
        db, tmp_path, "scan001.pdf",
        body="Syllabus and office hours.",
        heading="Statement of assets as of 09.01.2025", heading_page=1)
    record = detector(rule_set(ACADEMIC, FINANCE_GENERIC))(db, file_id, content_hash)
    assert record is not None
    assert record.protected is True


def test_a_heading_in_a_document_with_no_pages_still_protects(db, tmp_path):
    """A `.docx` has headings and no pagination, so there is no page one to be on.

    Absent must not mean "fails the test" here, or the rule would silently stop
    protecting every unpaginated format.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "letter.docx", extension=".docx",
        body="Syllabus and office hours.",
        heading="Statement of assets", heading_page=None)
    record = detector(rule_set(ACADEMIC, FINANCE_GENERIC))(db, file_id, content_hash)
    assert record is not None
    assert record.protected is True
