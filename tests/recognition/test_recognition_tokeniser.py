# tests/recognition/test_recognition_tokeniser.py
"""One boundary inside an alphanumeric run, and the half that must NOT be crossed.

`DisplayMedicalRecord.pdf` is one of the eight protected files in the ground truth.
It is a 672-byte macOS Finder alias -- `file(1)` says "MacOS Alias file", the first
eight bytes read `book....mark....` -- so there is no document inside it and no
extractor will ever recover a word from it. Its filename is the whole of its
evidence, and under the old rule that filename was the single token
`displaymedicalrecord`, which matches nothing. The product therefore had no way to
say anything about the owner's medical record other than "ordinary".

The boundary added here is lower-or-digit followed by an uppercase letter, and it
makes that filename `display medical record` -- which matches `medical record`, a
`medical` work type, in a naming zone.

**THE ALL-CAPS RUN IS NOT SPLIT, and that is the half that has to hold.** `HKID`
must stay one token or the `identity` term added for the owner's own Hong Kong
identity card stops matching and a national identity document goes back to being
called ordinary. That makes this only the CONSERVATIVE half of camel-case splitting:
`PDFReader` stays whole too, because separating an acronym from the word after it
needs a second and more aggressive rule that is deliberately not here.

MEASURED BEFORE LANDING, on the whole 215-file corpus, against the same HEAD:
protected not-marked 3 -> 2, CLASSIFY 91 -> 93, SORTING unchanged, and the
over-marked set byte-identical -- diffed file by file rather than compared by count,
because an equal count is not an equal set.

`tests/p6/test_p6_kind.py` is the other side of this: P6 keeps its own private
tokeniser in `facts/kind.py` and pins it against this one. Run that file too.
"""
from __future__ import annotations

import pytest

from recognition.detector import _tokens


def test_a_camel_case_filename_reads_as_the_words_a_person_reads():
    """THE CASE THIS EXISTS FOR. Three words a person reads as three words."""
    assert _tokens("DisplayMedicalRecord.pdf") == (
        "display", "medical", "record", "pdf")


def test_the_medical_record_work_type_is_reachable_in_that_filename():
    """Not just split -- split into the PHRASE the vocabulary carries.

    `medical record` is an authored `medical` work type. Splitting the filename
    into three tokens is only useful if two adjacent ones spell the term, so this
    asserts the phrase rather than the token count.
    """
    tokens = _tokens("DisplayMedicalRecord.pdf")
    assert ("medical", "record") == tokens[1:3]


def test_an_all_caps_run_is_never_split():
    """THE GUARD. `HKID` is one token or the owner's identity card goes unprotected.

    This is the assertion that stops the conservative half becoming the aggressive
    half by a later edit. `identity`'s `hkid` work type is matched out of the
    filename `2025209423_Joseph_Yung_HKID.pdf`, and that file is a Hong Kong
    identity card the product called `personal_non_sensitive, protected=0` until
    2026-09-04.
    """
    assert _tokens("HKID") == ("hkid",)
    assert _tokens("2025209423_Joseph_Yung_HKID.pdf") == (
        "2025209423", "joseph", "yung", "hkid", "pdf")


def test_an_acronym_followed_by_a_word_stays_whole():
    """The negative twin, and it is deliberate rather than an oversight.

    Splitting `PDFReader` into `pdf` + `reader` needs a rule about where an
    uppercase RUN ends, which is a different and more aggressive rule. Pinned so
    that adding it later is a visible decision and not a silent widening.
    """
    assert _tokens("PDFReader") == ("pdfreader",)


@pytest.mark.parametrize("text,expected", [
    # A digit followed by an uppercase letter is the same boundary.
    ("AY2024Spring", ("ay2024", "spring")),
    # Ordinary prose is untouched: no run boundary exists inside a lowercase word.
    ("problem set", ("problem", "set")),
    ("Problem  Set,", ("problem", "set")),
    # The academic patterns `cli.py` depends on keep their shape.
    ("BUSIB 4300 Spring 2026", ("busib", "4300", "spring", "2026")),
    ("PHYS1401", ("phys1401",)),
    ("lecture08_recursion.ipynb", ("lecture08", "recursion", "ipynb")),
])
def test_the_rest_of_the_tokeniser_is_unchanged(text, expected):
    """The blast radius, pinned. `_tokens` feeds every term match in the product.

    `PHYS1401` and `lecture08_recursion.ipynb` are here because
    `tests/p6/test_p6_kind.py` asserts these exact detector-side values against
    P6's own copy of this rule in `facts/kind.py`. If either moves, that file
    fails too, and the two tokenisers have silently diverged.
    """
    assert _tokens(text) == expected


def test_a_lowercase_prefix_before_a_capital_splits_and_that_has_a_cost():
    """THE EXPOSURE, written where the next person will read it.

    `eWelcome_Pack_...` becomes `e welcome pack ...`, and `CB_OrderReceipt.pdf`
    becomes `cb order receipt` -- putting `receipt`, a `finance` work type that is
    also ordinary English, into a naming zone. On the measured corpus that cost
    nothing (`CB_OrderReceipt.pdf` was already over-marked by other terms, and the
    over-marked SET did not change), but the mechanism is real: more tokens mean
    more phrase candidates, and `never_alone` turns a second match into an
    activated schema.

    Asserted rather than described, so that a future corpus where it DOES cost
    something has a test to point at.
    """
    assert _tokens("CB_OrderReceipt.pdf") == ("cb", "order", "receipt", "pdf")
    assert _tokens("eWelcome_Pack_TC.zip")[:2] == ("e", "welcome")
