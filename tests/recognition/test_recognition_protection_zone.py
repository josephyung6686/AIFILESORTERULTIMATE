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

import cli  # the DEPLOYMENT's handling policy, which is the one that ships

from recognition.detector import NAMING_ZONES
from recognition.rules import load_rules
from test_recognition_detector import (  # the packaged harness
    ACADEMIC, CLOCK, MANIFEST_PATH, a_file, db, detector, rule_set,
    schema_entry)  # noqa: F401

#: A safety domain whose work types are the two shapes that matter: one ordinary
#: English word, and one specific phrase. Both are how the real library spells them.
FINANCE_GENERIC = schema_entry(
    "finance", context=("account", "total"), work_types=("statement", "receipt"))


def test_the_naming_zones_are_the_ones_spec_2_2_ranks():
    """filename, title, heading -- and the one that is a heading by another name.

    `header_footer` is a running head: a page-one heading, on page two.

    `metadata` IS NOT HERE, and used to be, on the claim that it is "the format's
    own title slot, a document naming itself in its own words". P4 already gives
    that its own zone: `extractors/pdf.py:135` routes a slot to `zone="title"` if
    it is a title slot and to `metadata` otherwise, so `metadata` is by
    construction everything that is NOT the document naming itself. Measured over
    the owner's real corpora, what actually lands there is
    `extension`, `mime_type`, `language`, `Producer`, `CreationDate`, `ModDate`,
    `Creator`, `format`, `pixel dimensions` and `Trapped` -- the format talking
    about itself and about the toolchain that wrote it.

    It cost accuracy, not just tidiness: `HW 9.pdf`'s only authored term is
    `retail_hospitality:build`, out of
    `Producer = 'iOS Version 18.5 (Build 22F76) Quartz PDFContext'`, sitting in a
    zone that says the physics homework named itself that.

    `body`, `table`, `ocr`, `notes` and `annotation` are NOT here either, and that
    is the same point: they are where a document mentions OTHER documents.
    """
    assert NAMING_ZONES == frozenset(
        {"filename", "title", "heading", "header_footer"})


def test_a_toolchain_string_in_metadata_does_not_name_the_file(db, tmp_path):
    """The `Producer` field is the writing software, not the document.

    A safety work type landing in one must not be able to say the file IS that
    kind of document -- a PDF written by "Statement Printer 3.0" is not a
    financial statement.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "notes.pdf", body="Syllabus and office hours.",
        metadata_field=("Producer", "Statement Printer 3.0"))

    record = detector(rule_set(ACADEMIC, FINANCE_GENERIC))(db, file_id, content_hash)

    assert record is None or record.protected is False, (
        f"a toolchain string sealed an ordinary file: {record}")


def test_the_documents_own_title_slot_still_names_it(db, tmp_path):
    """The half that must NOT be lost: P4's `title` zone is the real one.

    `extractors/pdf.py:135` routes a title slot to `zone="title"`, so narrowing
    `metadata` takes nothing away from a document that names itself in its own
    metadata -- it just stops the toolchain fields pretending to.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "scan001.pdf", body="Syllabus and office hours.",
        title="Statement of assets")

    record = detector(rule_set(ACADEMIC, FINANCE_GENERIC))(db, file_id, content_hash)

    assert record is not None and record.protected is True, (
        f"a document whose own title slot names a financial statement was "
        f"released: {record}")


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


# --- the same word in two places, and which one gets recorded --------------------

def test_body_prose_repeating_the_heading_does_not_unprotect_the_file(db, tmp_path):
    """A file that names itself names itself however many other times it says so.

    `_matches` keeps ONE match per (schema, term) and kept whichever observation
    `rowid` reached first. P4 writes a body before a heading, so a brokerage
    statement whose page-one heading reads "Statement of assets" AND whose prose
    also says "statement" had its one `finance` match filed at the BODY -- and
    `_safety_readings_naming_the_file` then found nothing in a naming zone and let
    the file go.

    That is an over-release produced by ADDING ordinary prose: the identical file
    without the second sentence is protected (`test_a_page_one_heading_still_
    protects`). Protection must not depend on the order P4 happened to write its
    rows in, and arity is untouched -- the same term twice is still one term.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "letter.pdf", extension=".pdf",
        body="Syllabus and office hours. A statement of the facts follows.",
        heading="Statement of assets", heading_page=1)

    record = detector(rule_set(ACADEMIC, FINANCE_GENERIC))(db, file_id, content_hash)

    assert record is not None and record.protected is True, (
        "a page-one heading naming a financial statement stopped protecting the "
        f"file because its body also says the word: {record}")
    assert record.basis == "safety_domain"


# --- a work type spelled inside a longer work type -------------------------------
#
# `Chinese University Personal Statement.pdf` -- a real file on the owner's disk --
# is sealed `sensitive_personal, protected=1` because `finance` authors bare
# `statement` and it is in the FILENAME, where the zone cut cannot reach it. That
# over-protection is REAL and is NOT fixed here: refusing a term covered by a longer
# one releases `last will and testament` and `living will` (both context terms
# covering `legal:will`), `financial statement`, `pay statement` and `statement
# period` (covering `finance:statement`), and `government`'s rows covering every
# `identity` work type -- 210 such pairs over the shipped library. An over-release is
# worse than an over-protection. See `_terms_in`'s docstring and `planning/96`.
#
# What IS held below is the direction that must never regress.

def test_the_bare_word_still_protects_where_it_stands_on_its_own(db, tmp_path):
    """The floor under the comment above, against the SHIPPED library.

    `Statement.pdf` is a real brokerage statement on the owner's disk whose
    filename is `finance`'s work type standing on its own tokens, and it is a
    measured `protected=1` on the `~/Documents` run. Any future attempt to cure
    the `personal statement` over-protection has to keep this green, and the
    reverted one did -- it was the 210 OTHER pairs that sank it.

    The real deployment's policy, not the harness's: with the harness `POLICY`
    this file abstains `unassigned_handling` before it ever reaches the branch
    that protects, so the assertion would pass without testing anything.
    """
    rules = load_rules(MANIFEST_PATH.read_text)
    file_id, content_hash = a_file(
        db, tmp_path, "Statement.pdf",
        body="Table of contents. Client holdings as of 09.01.2025.")

    record = detector(rules, handling_for=cli.HANDLING_POLICY)(
        db, file_id, content_hash)

    assert record is not None and record.protected is True, (
        f"a brokerage statement was released: {record}")
