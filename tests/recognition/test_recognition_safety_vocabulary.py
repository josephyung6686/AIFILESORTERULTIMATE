# tests/recognition/test_recognition_safety_vocabulary.py
"""Seven words the owner's own documents contain and the shipped library did not.

`96` §19 measured four protected files after extraction started emitting body prose.
Two became protected; two did not, and their reason was not starvation:

    2025209423_Joseph_Yung_HKID.pdf        21 observations, ZERO safety terms
    Covid -19 vaccination record (1).pdf   23 observations, ZERO safety terms

The vaccination record that WAS saved was saved by luck: its text happens to use the
American `immunization`, which is authored. Its sibling says `vaccination`, which is
not. `eWelcome_Pack_TC_BOC_Credit_Card_TPA.zip` and `DisplayMedicalRecord.pdf` are the
same shape one domain along.

So: `vaccination record`, `medical record`, `identity card`, `hkid`, `credit card`,
`bank statement`, and `immunisation` -- the British spelling of a word the library
already has in American only.

**ALL SEVEN ARE WORK TYPES, and that is the whole of why they are worth adding.**
`detector._safety_readings_in_evidence` reads `work_type_terms` and NOTHING else --
the line that stopped `finance`'s context term `credit`, out of "credit hours", from
sealing two university syllabi. A term filed as context helps recognition and protects
nothing, so a term added there would leave every file in `96` §19 exactly where it is.

`immunisation` is the exception that proves it: `immunization` is authored BOTH ways
in the medical rows -- as a context term and inside the work type `immunization
record` -- so the British spelling is mirrored into both places rather than promoted
into one.

**The manifest is DERIVED.** These are asserted against
`src/recognition/library/recognition.json`, which
`test_the_packaged_manifest_is_exactly_what_the_live_node_rows_compile_to` pins to
`planning/domains/nodes/`. A term that appears here and not in a node row is a
hand-edited rule set with no research behind it, and that test is what catches it.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from recognition.rules import load_rules

MANIFEST = (Path(__file__).resolve().parents[2] / "src" / "recognition"
            / "library" / "recognition.json")

#: The seven, and the schema each belongs to. Written as data so the reason a term
#: exists travels with the term, and so a future reader can tell an addition made for
#: a measured document from one made because it sounded plausible.
ADDED: tuple[tuple[str, str, str], ...] = (
    ("medical", "vaccination record",
     "Covid -19 vaccination record (1).pdf -- 23 observations, no safety term"),
    ("medical", "medical record",
     "DisplayMedicalRecord.pdf, and the phrase every records request uses"),
    ("medical", "immunisation record",
     "the British spelling of an authored work type; the library had US only"),
    ("identity", "identity card",
     "the generic of `national identity card`, which the library already carries"),
    ("identity", "hkid",
     "2025209423_Joseph_Yung_HKID.pdf -- 21 observations, no safety term"),
    ("finance", "credit card",
     "eWelcome_Pack_TC_BOC_Credit_Card_TPA.zip -- 33 observations, no safety term"),
    ("finance", "bank statement",
     "`finance` carried the bare `statement` and no word for a bank (`96` §6)"),
)


@pytest.fixture(scope="module")
def rules():
    return load_rules(lambda: MANIFEST.read_text(encoding="utf-8"))


@pytest.mark.parametrize("schema_id,term,why",
                         ADDED, ids=[t for _s, t, _w in ADDED])
def test_the_term_is_authored_as_a_work_type_of_its_safety_schema(
        rules, schema_id, term, why):
    """A WORK TYPE, not a context term. The distinction is the whole mechanism.

    `_safety_readings_in_evidence`: "The term must say what the file IS, not merely
    surround it. The library separates `work_type_terms` (a passport, a discharge
    summary) from `context_terms` (words that accompany such a document)." Only the
    first can protect anything.
    """
    schema = rules.schemas[schema_id]
    assert term in schema.work_type_terms, (term, why)


def test_the_british_spelling_is_a_context_term_too(rules):
    """`immunization` is authored BOTH ways, so its sibling must be.

    The medical rows carry `immunization` as a context term AND `immunization record`
    as a work type. Mirroring only the work type would leave the British spelling
    half-present in a way no reader could predict from either half.
    """
    medical = rules.schemas["medical"]
    assert "immunization" in medical.context_terms, "the US spelling was the premise"
    assert "immunisation" in medical.context_terms


def test_no_added_term_is_owned_by_more_than_its_own_schema(rules):
    """A term two schemas authored discriminates between neither, and ties abstain.

    `RecognitionRules.schemas_owning`: "A term several schemas authored discriminates
    between none of them ... the candidates tie, and a tie is an abstention." Adding a
    word a second schema already claims would make the file it was added for LESS
    recognisable, which is the opposite of the point.
    """
    for schema_id, term, why in ADDED:
        owners = rules.schemas_owning(term)
        assert owners == (schema_id,), (term, owners, why)


def test_the_old_spellings_still_stand(rules):
    """An addition, never a replacement. `96` §19's two saved files were saved by these.

    `joseph Yung Vaccination Records.pdf` is protected today because its body says
    `immunization`, and `148268M000 FUND Trading OTC...pdf` because of `finance`'s
    generic words. A vocabulary change that widened one word by removing another
    would unprotect a file that is protected now, and the harness would report it as
    a wash rather than as a regression.
    """
    assert "immunization record" in rules.schemas["medical"].work_type_terms
    assert "immunization" in rules.schemas["medical"].context_terms
    assert "national identity card" in rules.schemas["identity"].work_type_terms
    assert "statement" in rules.schemas["finance"].work_type_terms


def test_every_added_term_can_actually_reach_a_file_of_its_own_kind(rules):
    """`file_kind_plausible` is a VETO, so a term on an implausible kind is dead rule.

    The four formats the added terms were measured against: a `.pdf` identity card, a
    `.pdf` vaccination record, a `.zip` credit-card welcome pack. A term whose schema
    does not admit that extension compiles, never matches, and would make this whole
    change look like it worked while changing nothing.
    """
    assert ".pdf" in rules.schemas["identity"].extensions
    assert ".pdf" in rules.schemas["medical"].extensions
    assert ".zip" in rules.schemas["finance"].extensions
