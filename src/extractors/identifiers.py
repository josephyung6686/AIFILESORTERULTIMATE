# src/extractors/identifiers.py
"""Amendment 7(a) -- identifier patterns with checksums, as a deterministic extractor.

`00`, Amendments of 2026-09-11, item 7(a), the owner's ruling of 12 Sep 2026 16:05:

    **identifier patterns with checksums** are a deterministic extractor -- card
    numbers, account and IBAN shapes, national-identity and passport shapes,
    medical record numbers, a date of birth beside a name -- whose observations
    hold a file exactly as an authored safety term does, and whose recorded value
    is never the whole identifier.

**What it is for, measured.** `104` §18.56 graded the second corpus against its
answer key: the rules alone RELEASED two health forms to the cloud (basis
`detector`, `protected = 0`, cloud-eligible on the rules' word), and of the key's
29 protected files twelve were left ordinary. Those files are not unlabelled in any
interesting sense -- they print a Hong Kong identity number, a card number, a
medical record number. What was missing was not another authored word; §18.56's own
sentence is that "the fix is not more authored words". It is a reader that fires on
the IDENTIFIER rather than on a guess about the document, which is the industry's
own first layer -- Purview and Presidio call these "sensitive information types":
a shape, a checksum, and where the shape alone is weak, a context word on the same
line.

**The recorded value is never the whole identifier, and P4 is what makes that a
fact rather than a promise.** Conformance rules 5 and 10 say that an observation
carrying a `text_span` must have a `text_units` row at exactly its container path
on its own run, and that `raw_value` must be the substring at that span (RAW-1,
`evidence_shape.text_units.check_span_anchor`). Both are enforced at write
(`store.RunWriter`) and again at release (`privacy.resolve`, which materialises a
span by reading the stored unit). So a span and a synthetic `raw_value` cannot both
be had, and the resolution is the stronger of the two:

    THE SPAN NAMES THE TAIL AND NOTHING ELSE. `location.text_span` covers the last
    `mask_tail` alphanumeric characters of the identifier, and `raw_value` is that
    substring. The whole identifier is therefore absent from the row AND unreachable
    through it -- `privacy.resolve` materialising this span returns four characters,
    because four characters is all the span addresses. A masked string beside a span
    over the whole number would have stored the mask and left the number one
    `raw_value_at` away.

    THE KIND PLUS THE MASKED TAIL IS `normalized_value` -- `payment_card …4242` --
    which is §2.8's "Normalized candidate value" and is the form a screen, a dossier
    and a report print. It is the one field P4 permits to differ from the source,
    which is exactly why the masked rendering lives there.

`context_before` and `context_after` are NULL on every row this emits, and that is
the point rather than an omission: the characters surrounding an identifier are the
rest of the identifier and its neighbours -- §2.8's window around a routing number
holds the account number whole -- so filling them would restore precisely what the
mask removed. `evidence_shape.store.line_reading_for` clears the same three fields
for the same reason.

**Nothing here opens a file.** It reads the text units P4 already stored for a file
version and mints readings onto the run those units belong to, which is
`facts/anchor_statements.py`'s shape and for the same reason: rule 10's unit has to
sit on the reading's own run, and `text_units` is D12/G1's ONE home for bulk text,
so a pass that wrote its own copy of the document to hang a span on would be a
second materialisation locus. `104` R-135's derived-reading mint is the precedent;
the namespace predicate below is modelled on `evidence_shape.store.DERIVED_NAMESPACE`
for the same reason it exists there -- a consumer opts in by asking, never by
keeping a roster.

**It holds no number.** `mask_tail` arrives from the caller and `cli.py` holds the
one this deployment ships, with its rationale. Checksums are arithmetic and not
thresholds -- Luhn's doubling, ISO 7064's mod-97, the ABA 3-7-1 weights and the Hong
Kong identity card's mod-11 are the numbering scheme's own definition, not a tuning
knob -- so they are here.
"""
from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from evidence_shape.location import Location, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.text_units import TextUnit

#: The namespace every reading this module mints sits in, spelled once. A CONVENTION
#: and not a list, exactly as `evidence_shape.store.DERIVED_NAMESPACE` is one: a
#: consumer asks the predicate below and keeps no roster of kinds of its own.
IDENTIFIERS_NAMESPACE: str = "identifiers."

#: This extractor's version, and it moves whenever the SHAPES move. `00`:44's rule --
#: "an upgraded reader invalidates the answers that rested on its output" -- read
#: through `104` §17.11's trap: `model_facts.call_identity_dimensions` treats
#: `extractor_versions` as a set of `(name, version)` pairs, WHICH readers ran and
#: never what they produced, so the version string is the only signal a changed
#: output has. A widened pattern or a corrected checksum changes the output for every
#: file in the corpus and must move this.
VERSION: str = "0.1.0"

#: What stands in for the characters the mask removed, wherever the masked rendering
#: is printed. ONE marker and never a count of them: a run of four asterisks would be
#: a number, and this module holds none.
MASK: str = "…"


def is_identifier_extractor(extractor_name: str) -> bool:
    """Whether readings from this extractor are masked identifier readings.

    The row-level spelling, published because two consumers must agree about it and
    a second copy of a vocabulary is this project's costliest defect.
    `recognition.detector._matches` SKIPS these rows: their `normalized_value` prints
    the kind, so a tokeniser reading `medical_record_number …8842` finds the word
    `record`, which several schemas author as a term -- the file would then be held
    by the wrong rule, citing the wrong evidence, and a `payment_card` reading would
    corroborate `finance` as though the document had said the word. The same rows are
    read as SAFETY READINGS in their own right by `detector._identifier_readings`.
    """
    return extractor_name.startswith(IDENTIFIERS_NAMESPACE)


def kind_of(extractor_name: str) -> str:
    """The kind an identifier reading's extractor name names."""
    if not is_identifier_extractor(extractor_name):
        raise ValueError(
            f"{extractor_name!r} is not in {IDENTIFIERS_NAMESPACE!r}; only a reading "
            "this module minted carries a kind")
    return extractor_name[len(IDENTIFIERS_NAMESPACE):]


# --- the closed vocabulary ---------------------------------------------------------
#
# THESE ARE SHAPES OF IDENTIFIERS, AND CONTEXT WORDS FOR THEM, GENERIC ACROSS EVERY
# DOMAIN. Not one of them is a corpus word and none of them may become one.
#
# `00` §3 is explicit that fixed patterns cannot capture "unlabeled forms", and `104`
# §18.56 records the cost of authored words used as a substitute for judgement -- so
# what is authored here has to be of a different kind, and it is. Nothing below
# describes a DOCUMENT. Every pattern describes a NUMBERING SCHEME published by a
# standards body or a government: ISO/IEC 7812 for a card's issuer identification
# number and its Luhn digit, ISO 13616 and ISO 7064 for an IBAN, the Social Security
# Administration's own never-issued ranges, the ABA routing transit number's 3-7-1
# weights, the Hong Kong identity card's mod-11 check character. Every context word
# is the LABEL a form prints beside such a number -- `SSN`, `passport`, `MRN`,
# `account`, `DOB` -- in any country, in any industry, on any document type.
#
# The distinction is checkable, and it is what makes this vocabulary the extractor's
# own rather than something the owner must ratify: `discharge summary` says what a
# DOCUMENT is and belongs to the recogniser's authored library; `SSN` says what the
# NINE DIGITS BESIDE IT are, and says the same thing on a tax form, a bank
# application and a hospital intake sheet. Widening this table means adding a
# numbering scheme, never adding an opinion about a corpus.

#: Separators a printed identifier is broken up with, in the three spellings forms
#: use. Removed only to compute a checksum; never to rewrite what was found.
_SEPARATORS = re.compile(r"[ \-–.]")

#: The context labels each weak-shaped kind requires ON ITS OWN LINE, matched
#: case-insensitively. A LINE, and not a window of N characters, because a line is
#: the unit a form's label and its value share -- "Patient ID: 4487211" is one line
#: on every intake sheet ever printed -- and a window would be a number.
CONTEXT_WORDS: Mapping[str, tuple[str, ...]] = MappingProxyType({
    "us_ssn": ("ssn", "s.s.n", "social security", "socialsecurity"),
    "passport_number": ("passport", "travel document"),
    "medical_record_number": ("mrn", "m.r.n", "medical record", "patient id",
                              "patient identifier", "patient no", "patient number",
                              "chart no", "chart number", "health record number"),
    "date_of_birth": ("date of birth", "dob", "d.o.b", "birth date", "birthdate",
                      "born on"),
    "bank_account": ("account", "acct", "routing", "aba", "sort code"),
})

#: A DATE BESIDE A NAME IS AMENDMENT 7(b)'s, AND THIS IS THE RECORD OF WHY.
#:
#: 7(a)'s list ends "a date of birth beside a name", and the obvious deterministic
#: reading of "a name" -- two or more adjacent capitalised words -- was written,
#: measured, and removed the same hour. Over lines of the kind a student's disk is
#: full of:
#:
#:     "Final Exam: May 15, 2024"        -> held, identity
#:     "Office Hours   10/12/2024"       -> held, identity
#:     "Adobe Acrobat 11/04/1990"        -> held, identity
#:
#: Adjacency does not rescue it: `Final Exam` and `Office Hours` sit against their
#: dates with a colon or a space between. Every syllabus, every assignment sheet and
#: every reading list in the owner's corpus would have come back
#: `sensitive_personal, protected=1` -- which is precisely the collapse
#: `recognition.detector._precaution` records the cost of ("made an unreadable scan
#: and a passport identical in P7's store") and precisely the over-protection half of
#: what `104` §18.56 measured.
#:
#: TITLE CASE IS NOT A NAME, and that is the whole finding. A capital letter is
#: typography; a person is an ENTITY, and naming one is what amendment 7(b) puts in a
#: local entity encoder -- "a small local entity encoder (GLiNER-class, ONNX ...)
#: names people, diagnoses, dates of birth and identity numbers as observations, and
#: a person beside a diagnosis or an identity number holds the file without a model
#: call". That is the same sentence as this arm, in the layer that can actually
#: execute it. So `date_of_birth` here fires on its LABEL, which is a shape of a form
#: and not a guess about a document, and the other half waits for 7(b) rather than
#: being approximated by a regex over capital letters.


class UnknownKind(ValueError):
    """A kind this module does not define. Raised rather than defaulted."""


@dataclass(frozen=True, slots=True)
class IdentifierShape:
    """One numbering scheme: its name, its written shape, and its own test.

    `check` is the scheme's OWN arithmetic or structural rule over the found text --
    Luhn, mod-97, mod-11, the ABA weights, a date's month and day, the SSA's refused
    ranges. It is what separates an identifier from sixteen digits, and it is the
    whole of why this extractor is deterministic rather than a guess: a product code
    that happens to be sixteen digits fails Luhn and is never observed.

    `needs_context` says the shape alone is too weak to fire on -- nine digits are
    nine digits until a form calls them an SSN -- and the words are `CONTEXT_WORDS`'
    entry for the kind, required on the identifier's own line.

    `value_span` says WHICH characters of a match are the person's identifier, for
    the one kind whose match holds more than that. It defaults to the whole match.
    """

    kind: str
    pattern: re.Pattern[str]
    check: Callable[[re.Match[str]], bool]
    needs_context: bool = False
    value_span: Callable[[re.Match[str]], tuple[int, int]] | None = None


# --- the schemes' own arithmetic ---------------------------------------------------

def _compact(text: str) -> str:
    """The text with its printed separators removed. Computed with, never stored."""
    return _SEPARATORS.sub("", text)


def luhn_ok(number: str) -> bool:
    """ISO/IEC 7812-1 Annex B's check digit, over a string of digits."""
    total = 0
    for position, character in enumerate(reversed(number)):
        digit = ord(character) - 48
        if position % 2:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


#: ISO/IEC 7812's ISSUER IDENTIFICATION NUMBERS, as the schemes publish them, each
#: with the lengths that issuer issues.
#:
#: LUHN ALONE IS NOT THE TEST, and the arithmetic says why: one in ten random digit
#: strings of any length passes it, so on a real disk Luhn alone observes every order
#: number, every invoice number and every serial number as a payment card. The issuer
#: prefix and the length are what make the shape a CARD. This is `104` §18.56's own
#: lesson applied before the measurement rather than after it -- a recogniser that
#: fires on everything is the over-protection collapse
#: `recognition.detector._precaution` already records the cost of, where "an
#: unreadable scan and a passport" became identical in P7's store.
_CARD_SCHEMES: tuple[tuple[tuple[str, ...], tuple[int, ...]], ...] = (
    (("4",), (13, 16, 19)),                                     # Visa
    (("34", "37"), (15,)),                                      # American Express
    (("51", "52", "53", "54", "55"), (16,)),                    # Mastercard
    (("2221", "2222", "2223", "2224", "2225", "2226", "2227",   # Mastercard 2-series
      "2228", "2229", "223", "224", "225", "226", "227", "228", "229",
      "23", "24", "25", "26", "270", "271", "2720"), (16,)),
    (("6011", "644", "645", "646", "647", "648", "649", "65"),  # Discover
     (16, 19)),
    (("3528", "3529", "353", "354", "355", "356", "357", "358"),  # JCB
     (16, 19)),
    (("300", "301", "302", "303", "304", "305", "3095", "36", "38", "39"),  # Diners
     (14, 16, 19)),
)


def card_ok(match: re.Match[str]) -> bool:
    """An issuer identification number, a length that issuer issues, and Luhn."""
    number = _compact(match.group(0))
    if not number.isdigit():
        return False
    if not any(number.startswith(prefixes) and len(number) in lengths
               for prefixes, lengths in _CARD_SCHEMES):
        return False
    return luhn_ok(number)


def iban_ok(match: re.Match[str]) -> bool:
    """ISO 13616's shape and ISO 7064's mod-97-10: rearrange, letter -> number, == 1."""
    account = _compact(match.group(0)).upper()
    if not 15 <= len(account) <= 34 or not account.isalnum():
        return False
    if not (account[:2].isalpha() and account[2:4].isdigit()):
        return False
    expanded = "".join(
        str(ord(character) - 55) if character.isalpha() else character
        for character in account[4:] + account[:4])
    if not expanded.isdigit():
        return False
    return int(expanded) % 97 == 1


def ssn_ok(match: re.Match[str]) -> bool:
    """The Social Security Administration's own never-issued ranges.

    Area `000`, `666` and `900`-`999`; group `00`; serial `0000`. A STRUCTURAL test
    and not a checksum, because the scheme publishes none -- which is exactly why
    this kind also requires its label on the line.
    """
    number = _compact(match.group(0))
    if len(number) != 9 or not number.isdigit():
        return False
    area, group, serial = number[:3], number[3:5], number[5:]
    if area in ("000", "666") or area[0] == "9":
        return False
    return group != "00" and serial != "0000"


def hkid_ok(match: re.Match[str]) -> bool:
    """The Hong Kong identity card's mod-11 check character.

    One or two leading letters, six digits, a check character. Weights run 9 down to
    2 over the eight leading positions; a one-letter card is computed as though a
    space (value 36) stood in the first position, which is the scheme's own rule. A
    remainder of 10 is written `A`.
    """
    body = match.group("body").upper()
    letters = body[:-6]
    values = ([36] if len(letters) == 1 else []) + [
        ord(letter) - 55 for letter in letters]
    values += [ord(digit) - 48 for digit in body[-6:]]
    total = sum(value * weight for value, weight in zip(values, range(9, 1, -1)))
    remainder = (11 - total % 11) % 11
    expected = "A" if remainder == 10 else str(remainder)
    return match.group("check").upper() == expected


def aba_ok(routing: str) -> bool:
    """The ABA routing transit number's 3-7-1 weighted checksum, mod 10."""
    if len(routing) != 9 or not routing.isdigit():
        return False
    return sum(int(digit) * weight for digit, weight
               in zip(routing, (3, 7, 1, 3, 7, 1, 3, 7, 1))) % 10 == 0


def _routing_half(match: re.Match[str]) -> str | None:
    """WHICH of the two numbers on this line is the routing number, or neither.

    THE PAIR IS THE IDENTIFIER -- the ruling's own words, "bank account/routing pairs
    with context" -- so the test is asked of both halves and the order they were
    printed in decides nothing. A statement writes "Routing 021000021 Account
    1234567890" and an application form writes them the other way round; a rule that
    read only the first would hold one document and release the other.

    BOTH passing is refused rather than resolved. Two nine-digit numbers that both
    checksum are two routing numbers or a coincidence, and there is no account number
    to mask -- recording either one would be this module guessing which of a person's
    numbers is the private one.
    """
    first, second = match.group("first"), match.group("second")
    passes = [half for half in (first, second) if aba_ok(half)]
    return passes[0] if len(passes) == 1 else None


def bank_account_ok(match: re.Match[str]) -> bool:
    """Exactly one of the two numbers is a routing number that checksums."""
    return _routing_half(match) is not None


def bank_account_value(match: re.Match[str]) -> tuple[int, int]:
    """The half that is NOT the routing number: the person's account number.

    A routing number is the BANK's and is printed on every cheque that bank ever
    issued; masking it would protect a public number and leave the private one in the
    row. So the reading spans the other half, and the routing number is what made the
    pair an identifier rather than two numbers.
    """
    routing = _routing_half(match)
    name = "second" if match.group("first") == routing else "first"
    return match.start(name), match.end(name)


#: The months a written date may name. Not a vocabulary about any domain: it is how a
#: date is written.
_MONTH_PREFIXES: tuple[str, ...] = (
    "jan", "feb", "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "oct", "nov", "dec")


def date_ok(match: re.Match[str]) -> bool:
    """A real calendar day: a month of 1-12 and a day of 1-31, however it is written.

    No year range and no "is this plausible as a birth" test. A ceiling on how old a
    person may be is a number and this module holds none; what makes a date a DATE OF
    BIRTH is the label or the name beside it, which is the ruling's own rule.

    A slashed or dotted date is written day-first in most of the world and month-first
    in the United States. BOTH READINGS ARE ADMITTED, because choosing one would be
    this module deciding a locale it was never told: the pair passes when some reading
    of it is a real day.
    """
    named = match.groupdict()
    if named.get("iso_m"):
        return 1 <= int(named["iso_m"]) <= 12 and 1 <= int(named["iso_d"]) <= 31
    if named.get("month_name"):
        return 1 <= int(named["name_d"]) <= 31
    if named.get("dm_month"):
        return 1 <= int(named["dm_d"]) <= 31
    first, second = int(named["num_a"]), int(named["num_b"])
    return ((1 <= first <= 12 and 1 <= second <= 31)
            or (1 <= second <= 12 and 1 <= first <= 31))


# --- the shapes, in the order they are tried ---------------------------------------
#
# ORDER IS A REFUSAL, not a preference. One stretch of characters is one identifier:
# a sixteen-digit card is also nine digits followed by seven, and an ABA routing
# number is also a nine-digit SSN shape. So a later kind never claims characters an
# earlier one already did, and the strongest-tested kinds run first -- the ones whose
# scheme publishes a checksum before the ones that lean on a label, because a
# checksum is a property of the number and a label is a property of the page.
IDENTIFIER_SHAPES: tuple[IdentifierShape, ...] = (
    IdentifierShape(
        kind="payment_card",
        pattern=re.compile(r"(?<![\w-])(?:\d[ \-]?){11,18}\d(?![\w-])"),
        check=card_ok),
    IdentifierShape(
        kind="iban",
        pattern=re.compile(r"(?<![\w-])[A-Z]{2}\d{2}[ ]?(?:[A-Z0-9][ ]?){11,30}"
                           r"(?<![ ])(?![\w-])"),
        check=iban_ok),
    IdentifierShape(
        kind="hkid",
        pattern=re.compile(r"(?<![\w-])(?P<body>[A-Za-z]{1,2}\d{6})"
                           r"\(?(?P<check>[0-9Aa])\)?(?![\w-])"),
        check=hkid_ok),
    IdentifierShape(
        kind="bank_account",
        # `[^\d\r\n]` and not `\D`, and the newline is the whole of the difference.
        # A pair is a pair BECAUSE the two numbers are printed together, and `\D`
        # crosses line breaks: measured on a synthetic statement, a medical record
        # number on one line paired with a routing number on the next, claimed the
        # characters of both, and the real pair below it never fired -- one wrong
        # reading that also silenced two right ones. UNBOUNDED between them, because
        # the line already bounds it: a "within N characters" window would be a
        # number, and this module holds none.
        pattern=re.compile(r"(?<![\w-])(?P<first>\d{6,17})[^\d\r\n]+?"
                           r"(?P<second>\d{6,17})(?![\w-])"),
        check=bank_account_ok, needs_context=True,
        value_span=bank_account_value),
    IdentifierShape(
        kind="us_ssn",
        pattern=re.compile(r"(?<![\w-])\d{3}[- ]?\d{2}[- ]?\d{4}(?![\w-])"),
        check=ssn_ok, needs_context=True),
    IdentifierShape(
        kind="passport_number",
        pattern=re.compile(r"(?<![\w-])(?:[A-Z]{1,2}\d{6,7}|[A-Z]\d{8}|\d{9})"
                           r"(?![\w-])"),
        # The scheme publishes no check digit in the number itself -- ICAO's is in the
        # machine-readable zone, which a text extraction of a passport page does not
        # carry -- so the SHAPE is the whole structural test and the word `passport`
        # on the line is what the ruling requires beside it.
        check=lambda match: True, needs_context=True),
    IdentifierShape(
        kind="medical_record_number",
        pattern=re.compile(r"(?<![\w-])[A-Z]{0,3}[- ]?\d{6,10}(?![\w-])"),
        # A hospital's numbering is the hospital's; no scheme publishes a shared check
        # digit for it, so the label -- `MRN`, `patient ID` -- is what the ruling asks
        # for and what this requires.
        check=lambda match: True, needs_context=True),
    IdentifierShape(
        kind="date_of_birth",
        pattern=re.compile(
            r"(?<![\w-])(?:"
            r"(?P<iso_y>\d{4})-(?P<iso_m>\d{1,2})-(?P<iso_d>\d{1,2})"
            r"|(?P<num_a>\d{1,2})[/.](?P<num_b>\d{1,2})[/.]\d{2,4}"
            rf"|(?P<month_name>{'|'.join(_MONTH_PREFIXES)})[a-z]*\.?\s+"
            r"(?P<name_d>\d{1,2})(?:st|nd|rd|th)?,?\s+\d{4}"
            # DAY FIRST, which is how the rest of the world writes a written date and
            # how the machine-readable half of a passport page prints one: `11 Apr
            # 1990`. Left out of the first draft and caught by a synthetic passport
            # page whose birth date then went unread, which is the same silence
            # `104` §18.56 measured with a different cause.
            rf"|(?P<dm_d>\d{{1,2}})\s+(?P<dm_month>{'|'.join(_MONTH_PREFIXES)})"
            r"[a-z]*\.?,?\s+\d{4}"
            r")(?![\w-])", re.IGNORECASE),
        check=date_ok, needs_context=True),
)

#: The kinds, in the order above. THE CLOSED VOCABULARY, published so a consumer --
#: `recognition.detector.IDENTIFIER_SAFETY_DOMAIN` is the first -- can be checked
#: against it at import instead of keeping a second copy that quietly stops matching.
KINDS: tuple[str, ...] = tuple(shape.kind for shape in IDENTIFIER_SHAPES)

#: THE KINDS WHOSE SHAPE CARRIES ITS OWN PROOF: a check digit or a modulus the
#: number has to satisfy (Luhn, mod-97, the HKID check character, the SSN's
#: published exclusions, the routing-number pair). The other shapes above --
#: a passport-shaped string, a hospital's record number, a date beside a
#: birth-date label -- match a pattern and nothing more, and the detector treats
#: them as corroboration rather than as a hold on their own (`recognition.
#: detector.precaution_report`, the ruling of 13 Sep 2026). Named here beside
#: `KINDS` so the split lives with the shapes that define it.
CHECKSUMMED_KINDS: frozenset[str] = frozenset(
    {"payment_card", "iban", "bank_account", "us_ssn", "hkid"})

if len(set(KINDS)) != len(KINDS):                                    # pragma: no cover
    raise UnknownKind(f"two shapes claim one kind: {KINDS}")
for _kind in CONTEXT_WORDS:                                          # pragma: no cover
    if _kind not in KINDS:
        raise UnknownKind(
            f"{_kind!r} has context words and no shape; a label with nothing to "
            "label is a rule that can never fire")
for _shape in IDENTIFIER_SHAPES:                                     # pragma: no cover
    if _shape.needs_context and _shape.kind not in CONTEXT_WORDS:
        raise UnknownKind(
            f"{_shape.kind!r} says its shape is too weak to fire alone and names no "
            "context words; the two halves of that rule live together")


# --- reading the stored units ------------------------------------------------------

def line_around(text: str, start: int, end: int) -> str:
    """The line the found characters sit on: previous newline to next newline."""
    opening = text.rfind("\n", 0, start) + 1
    closing = text.find("\n", end)
    return text[opening:len(text) if closing == -1 else closing]


#: Each label as a WHOLE-WORD pattern, built once at import.
#:
#: A substring test was written first and is wrong in the permissive direction, which
#: is the direction that costs: `dob` is inside `Adobe`, `aba` inside `database`,
#: `mrn` inside nothing English but inside plenty of file names, and `acct` inside
#: `acctg`. Measured: "Adobe Acrobat 11/04/1990" was read as a date of birth. A label
#: is a WORD a form prints, so the test is for the word.
_CONTEXT_PATTERNS: Mapping[str, tuple[re.Pattern[str], ...]] = MappingProxyType({
    kind: tuple(re.compile(rf"\b{re.escape(word)}\b") for word in words)
    for kind, words in CONTEXT_WORDS.items()})


def _has_context(kind: str, line: str) -> bool:
    """One of the kind's own labels, as a whole word, on this line, case-folded."""
    folded = line.casefold()
    return any(pattern.search(folded) for pattern in _CONTEXT_PATTERNS[kind])


def _is_a_fraction(match: re.Match[str]) -> bool:
    """Are these digits part of a longer DECIMAL NUMBER rather than an identifier?

    MEASURED, and it is the largest false-positive class there is. Over the
    synthetic corpus's six spreadsheets, 29 readings fired and every one of them was
    the fractional part of a random float:

        31,0.5503786251865023,meeting   ->  `5503786251865023`, a Mastercard prefix
        53,0.4124219052004032,essay     ->  `4124219052004032`, a Visa prefix

    Sixteen digits after a decimal point pass Luhn one time in ten and carry an
    issuer prefix about one time in four, so a table of floats holds a payment card
    every dozen rows -- and every dataset a person owns would be
    `sensitive_personal, protected=1`. That is the over-protection collapse, reached
    by arithmetic rather than by a word.

    A DECIMAL POINT AND NOT A COMMA, and the choice is the consequential one. `,` is
    a decimal separator in much of the world AND the field separator in every CSV
    ever written, so refusing on it would refuse a column of real card numbers --
    `31,4124219052004032,x` -- which is the file this whole layer exists to catch. A
    European-formatted float is therefore still admitted, and it is the rarer error
    in the safer direction.
    """
    text, start, end = match.string, match.start(), match.end()
    if start >= 2 and text[start - 1] == "." and text[start - 2].isdigit():
        return True
    return (end + 1 < len(text) and text[end] == "."
            and text[end + 1].isdigit())


def _fires(shape: IdentifierShape, match: re.Match[str], line: str) -> bool:
    """The scheme's own test, and its label where the shape alone is too weak.

    ONE RULE FOR EVERY KIND, and `date_of_birth`'s second half is deliberately not
    here: see the block above `IdentifierShape` for why "a date of birth beside a
    name" is amendment 7(b)'s and not a regex over capital letters.
    """
    if _is_a_fraction(match):
        return False
    return shape.check(match) and (
        not shape.needs_context or _has_context(shape.kind, line))


def masked_tail(text: str, start: int, end: int, *,
                mask_tail: int) -> tuple[int, int] | None:
    """The span of the LAST `mask_tail` alphanumeric characters of `text[start:end]`.

    Walked back over the printed separators rather than counted off the end, so a
    card written `4242 4242 4242 4242` and one written `4242424242424242` record the
    same four digits. A separator falling inside the tail is INCLUDED in the span,
    because the span has to address real stored characters -- RAW-1 compares
    `raw_value` to the substring and a span that skipped a space would not be one.
    The masked RENDERING drops it again; see `_masked`.

    `None` when the identifier is not longer than the mask, and the refusal is the
    safe direction: a reading whose span covered every character of the identifier
    would be the whole identifier stored under a name that says it is not. Nothing
    reaches it today -- every shape above is at least six characters and every
    deployment's mask is smaller -- and it is here so that a shorter scheme added
    later fails closed rather than quietly leaking.
    """
    if mask_tail < 1:
        raise ValueError(
            f"mask_tail is how many characters of an identifier may be recorded and "
            f"is at least one; got {mask_tail!r}. Zero is not safer -- it is an "
            "empty raw_value, which P4's `check_non_empty` refuses.")
    seen = 0
    position = end
    while position > start:
        position -= 1
        if text[position].isalnum():
            seen += 1
            if seen == mask_tail:
                return (position, end) if position > start else None
    return None


def _masked(kind: str, tail: str) -> str:
    """§2.8's "Normalized candidate value" for a masked reading: the kind, the mask,
    then the tail's own alphanumeric characters.

    The separators are dropped HERE and not from `raw_value`, which stays the source
    substring RAW-1 compares against: `iban …5432` is what a person reads, while the
    row still stores exactly the characters its span addresses.
    """
    kept = "".join(character for character in tail if character.isalnum())
    return f"{kind} {MASK}{unicodedata.normalize('NFC', kept)}"


def identifier_observations(
        *, file_id: str, content_hash: str, source_type: str,
        units: Iterable[TextUnit], zone_for: Callable[[TextUnit], str],
        now: str, mask_tail: int) -> tuple[Observation, ...]:
    """Every identifier this file version's stored units carry, masked.

    ONE READING PER DISTINCT IDENTIFIER PER UNIT, spanned at the first occurrence and
    carrying `occurrence_count` for the rest. §2.8's count is what that field is for
    (P4 conformance rule 7), and a card number printed on every page of a statement
    is one identifier: five rows would be five citations of one fact and would let a
    repeated number look like five findings on a screen that counts them.

    `zone_for` is INJECTED because P4 stores no zone on a text unit -- a unit is an
    address (`TextUnit.unit_locator`: "no zone: a unit is an address, not a located
    value") and the zone lives on the observation the unit was emitted beside. The
    caller holds those observations; this module opens nothing and asks nobody.

    The readings ride on the unit's OWN run (`TextUnit.run_id`), which is what makes
    conformance rule 10 true by construction: the unit a span points into is on the
    reading's run at exactly the reading's container path.
    `facts/anchor_statements.py` mints onto the host run for the same reason and
    `104` R-135 records it.

    Returned and never written. Whether these rows may exist is the caller's -- P4
    does not decide what a caller is allowed to have, which is
    `evidence_shape.store.line_reading_for`'s own rule -- and `record_observation` is
    what writes one.
    """
    minted: list[Observation] = []
    for unit in units:
        text = unit.text
        if not text:
            continue
        zone = zone_for(unit)
        claimed: list[tuple[int, int]] = []
        #: (kind, masked value) -> [tail start, tail end, occurrences]. Keyed on the
        #: MASKED value because that is the identity the row will carry: two cards
        #: ending in the same four digits are one reading of one masked value, and
        #: counting them separately would report a number this row cannot show.
        found: dict[tuple[str, str], list[int]] = {}
        for shape in IDENTIFIER_SHAPES:
            for match in shape.pattern.finditer(text):
                if any(match.start() < taken_end and taken_start < match.end()
                       for taken_start, taken_end in claimed):
                    continue
                if not _fires(shape, match, line_around(text, *match.span())):
                    continue
                start, end = (match.span() if shape.value_span is None
                              else shape.value_span(match))
                tail = masked_tail(text, start, end, mask_tail=mask_tail)
                if tail is None:
                    continue
                claimed.append(match.span())
                value = _masked(shape.kind, text[tail[0]:tail[1]])
                entry = found.get((shape.kind, value))
                if entry is None:
                    found[(shape.kind, value)] = [tail[0], tail[1], 1]
                else:
                    entry[2] += 1
        for (kind, value), (tail_start, tail_end, count) in found.items():
            minted.append(Observation(
                file_id=file_id, content_hash=content_hash,
                extractor_name=IDENTIFIERS_NAMESPACE + kind,
                extractor_version=VERSION, source_type=source_type,
                # RAW-1: the substring the span addresses, and nothing wider. The
                # whole identifier is not in this row and is not reachable from it.
                raw_value=text[tail_start:tail_end],
                normalized_value=value,
                location=Location(zone=zone, container_path=unit.container_path,
                                  text_span=TextSpan(tail_start, tail_end)),
                occurrence_count=count,
                observed_at=now,
                # D11's weaker state, and the honest one: a checksum says the digits
                # are a well-formed card number, never that this person is its
                # holder. §3.13's `direct` is for a labelled slot the format itself
                # names, and a number found in running text is not one.
                reliability="possible",
                run_id=unit.run_id,
                # NULL, and this is the mask's other half -- see the module docstring.
                context_before=None, context_after=None, context_truncated=False,
            ))
    return tuple(minted)
