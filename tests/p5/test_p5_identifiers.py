# tests/p5/test_p5_identifiers.py
"""`00` amendment 7(a)'s deterministic extractor: a checksum fires, a mask holds.

The ruling of 12 Sep 2026 16:05 is one sentence with three obligations in it --
identifier patterns with checksums are a deterministic extractor, their observations
hold a file, and "the recorded value is never the whole identifier" -- and this file
pins the first and the third. `tests/recognition/test_identifiers_hold_a_file.py`
pins the second.

**Every kind has its negative twin, and the twin is the point.** `104` §18.56's
measurement is of a product that both missed real identifiers and over-held ordinary
files, and a recogniser that fires on everything fails the second half while passing
every "it fires" test anyone writes. So each kind is asserted with a real identifier
AND with something the same shape that fails the scheme's own arithmetic: a product
code that fails Luhn, an IBAN whose mod-97 is off by one, a nine-digit number with no
label beside it.

**The leak test is over the DATABASE and not over the record.** A row has eight
columns that can hold text, and the one that made this whole design hard is
`context_before`/`context_after` -- §2.8's window around a routing number holds the
account number whole. So the assertion is: after a real write through P4's own
writer, the identifier does not appear in ANY column of ANY row, in any spelling the
document used.
"""
from __future__ import annotations

import pytest

from database_agent.db import create_schema
from database_agent.files_table import record_file
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import RunWriter, record_observation, text_units_for_run
from evidence_shape.text_units import TextUnit, check_span_anchor
from extractors.identifiers import (
    IDENTIFIERS_NAMESPACE, IDENTIFIER_SHAPES, KINDS, MASK, VERSION,
    aba_ok, card_ok, hkid_ok, iban_ok, identifier_observations,
    is_identifier_extractor, kind_of, luhn_ok, masked_tail, ssn_ok,
)
from extractors.runs import coverage
from extractors.schema import create_extraction_schema
from extractors.shape import location, observation, run
from extractors.sink import ExtractionResult

from conftest import FIXED_CLOCK

#: The one this deployment ships, imported from where the number lives rather than
#: retyped: `cli.IDENTIFIER_MASK_TAIL` is the only place it is chosen, and a test
#: holding its own 4 would keep passing after somebody changed the deployment's.
from cli import IDENTIFIER_MASK_TAIL

HASH = "c4b68614329771504e26f782d73842637dfa7ece1ad2bc377faae5c296806a0b"


#: ONE LINE PER KIND: the kind, a line that carries a real identifier of it, the
#: whole identifier as the document spells it, and a line of the SAME SHAPE that the
#: scheme's own test refuses. Every identifier here is a published test value or is
#: constructed to satisfy the scheme and belongs to nobody: `4242…4242` is Stripe's
#: documented test card, `GB82 WEST…` is the IBAN registry's own example, `078-05-1120`
#: is the Woolworth wallet number the SSA published as never-to-be-used, `021000021`
#: is JPMorgan Chase's public routing number.
CASES: tuple[tuple[str, str, str, str], ...] = (
    ("payment_card",
     "Charged to Visa 4242 4242 4242 4242 on the third.",
     "4242 4242 4242 4242",
     "Product code 1234567812345678 in the catalogue."),
    ("iban",
     "Please remit to IBAN GB82 WEST 1234 5698 7654 32 by Friday.",
     "GB82 WEST 1234 5698 7654 32",
     "Please remit to IBAN GB82 WEST 1234 5698 7654 33 by Friday."),
    ("hkid",
     "Holder HKID A123456(3) presented at the counter.",
     "A123456(3)",
     "Holder HKID A123456(4) presented at the counter."),
    ("bank_account",
     "Routing 021000021 Account 1234567890 for the transfer.",
     "1234567890",
     "Routing 021000022 Account 1234567890 for the transfer."),
    ("us_ssn",
     "SSN: 078-05-1120 on file.",
     "078-05-1120",
     "Reference: 078-05-1120 on file."),
    ("passport_number",
     "Passport No. X1234567 expires in 2031.",
     "X1234567",
     "Part number X1234567 expires in 2031."),
    ("medical_record_number",
     "MRN 4487211 admitted overnight.",
     "4487211",
     "Invoice 4487211 admitted overnight."),
    ("date_of_birth",
     "Jane Marie Roberts   1990-04-11   admitted",
     "1990-04-11",
     "Invoice raised 1990-04-11 and settled"),
)


def _unit(text: str, *, run_id: str = "run-1") -> TextUnit:
    return TextUnit(run_id=run_id, container_path=(), text=text)


def observe(text: str, *, mask_tail: int = IDENTIFIER_MASK_TAIL, zone: str = "body"):
    return identifier_observations(
        file_id="f-statement", content_hash=HASH, source_type="text_document",
        units=[_unit(text)], zone_for=lambda unit: zone, now=FIXED_CLOCK,
        mask_tail=mask_tail)


def _of_kind(rows, kind: str):
    return [row for row in rows
            if row.extractor_name == IDENTIFIERS_NAMESPACE + kind]


# --- the vocabulary is closed and it agrees with itself ---------------------------

def test_every_shape_has_a_kind_and_every_case_has_a_shape():
    """The table below IS the coverage claim. A kind added to the extractor with no
    case here would ship untested, so the roster is compared rather than trusted."""
    assert {case[0] for case in CASES} == set(KINDS)
    assert len(CASES) == len(IDENTIFIER_SHAPES)


def test_the_namespace_predicate_and_the_kind_are_exact_inverses():
    for kind in KINDS:
        assert is_identifier_extractor(IDENTIFIERS_NAMESPACE + kind)
        assert kind_of(IDENTIFIERS_NAMESPACE + kind) == kind
    assert not is_identifier_extractor("text.structured")
    assert not is_identifier_extractor("derived.anchor_statements.line")
    with pytest.raises(ValueError):
        kind_of("text.structured")


# --- each kind, and its near miss -------------------------------------------------

@pytest.mark.parametrize("kind, line, whole, near_miss",
                         CASES, ids=[case[0] for case in CASES])
def test_a_real_identifier_is_observed_masked_and_spanned(kind, line, whole,
                                                          near_miss):
    """The positive half: the kind fires, and what it records is the TAIL.

    SABOTAGE: return `match.span()` from `masked_tail`. Every assertion about the
    span's width goes red, which is the ruling's "never the whole identifier" stated
    as a failure.
    """
    rows = _of_kind(observe(line), kind)
    assert len(rows) == 1, [row.normalized_value for row in rows]
    row = rows[0]

    span = row.location.text_span
    assert span is not None
    # RAW-1 (P4 conformance rule 5): the value IS the substring the span addresses,
    # which is what makes the mask a property of the DATABASE and not of a printer.
    assert row.raw_value == line[span.start:span.end]
    assert len([c for c in row.raw_value if c.isalnum()]) == IDENTIFIER_MASK_TAIL
    assert span.end - span.start < len(whole)

    # The masked rendering a screen and a dossier print.
    assert row.normalized_value.startswith(f"{kind} {MASK}")
    assert row.normalized_value.endswith(
        "".join(c for c in row.raw_value if c.isalnum()))

    assert row.extractor_name == IDENTIFIERS_NAMESPACE + kind
    assert row.extractor_version == VERSION
    assert row.location.zone == "body"
    assert row.occurrence_count == 1
    # D11: a checksum says the digits are well formed, never that this person holds
    # them. `direct` is §3.13's word for a labelled slot the format itself names.
    assert row.reliability == "possible"


@pytest.mark.parametrize("kind, line, whole, near_miss",
                         CASES, ids=[case[0] for case in CASES])
def test_the_same_shape_that_fails_its_own_test_is_not_observed(kind, line, whole,
                                                                near_miss):
    """The negative twin. Same shape, failing arithmetic or missing label -- and the
    file gets nothing, because "a recogniser that fires on everything" is the
    over-protection collapse `recognition.detector._precaution` records the cost of.
    """
    assert _of_kind(observe(near_miss), kind) == []


def test_a_sixteen_digit_product_code_failing_luhn_is_not_a_card():
    """The ruling's own example of what a CHECKSUM buys, asserted on its own.

    Luhn alone admits one in ten digit strings, so this is the difference between an
    extractor and a regex: `1234567812345678` is sixteen digits with a Visa-shaped
    length and it is a catalogue number.
    """
    assert not luhn_ok("1234567812345678")
    assert observe("Product code 1234567812345678 in the catalogue.") == ()
    # And the working: the same sixteen digits with a correct check digit ARE one.
    assert luhn_ok("4242424242424242")
    assert len(observe("Card 4242424242424242 charged.")) == 1


def test_the_schemes_own_arithmetic_is_the_schemes_own():
    """Published test values, so a rewritten checksum cannot pass by agreeing with
    itself. Each is the number the scheme's own documentation prints."""
    assert card_ok(IDENTIFIER_SHAPES[0].pattern.search("4242424242424242"))
    assert iban_ok(IDENTIFIER_SHAPES[1].pattern.search("GB82WEST12345698765432"))
    assert not iban_ok(IDENTIFIER_SHAPES[1].pattern.search("GB82WEST12345698765433"))
    assert hkid_ok(IDENTIFIER_SHAPES[2].pattern.search("A123456(3)"))
    assert not hkid_ok(IDENTIFIER_SHAPES[2].pattern.search("A123456(4)"))
    assert ssn_ok(IDENTIFIER_SHAPES[4].pattern.search("078-05-1120"))
    # The SSA's never-issued ranges, which are the whole of that scheme's test.
    assert not ssn_ok(IDENTIFIER_SHAPES[4].pattern.search("000-05-1120"))
    assert not ssn_ok(IDENTIFIER_SHAPES[4].pattern.search("666-05-1120"))
    assert not ssn_ok(IDENTIFIER_SHAPES[4].pattern.search("078-00-1120"))
    assert not ssn_ok(IDENTIFIER_SHAPES[4].pattern.search("078-05-0000"))
    assert aba_ok("021000021") and not aba_ok("021000022")


def test_a_pair_is_a_pair_in_either_printed_order():
    """`bank_account` reads the checksum of BOTH halves, so a statement and an
    application form -- which print them the other way round -- are both held, and
    what is masked is the person's account and not the bank's public code."""
    first = _of_kind(observe("Routing 021000021 Account 1234567890"), "bank_account")
    second = _of_kind(observe("Account 1234567890 Routing 021000021"), "bank_account")
    assert len(first) == len(second) == 1
    assert first[0].normalized_value == second[0].normalized_value == (
        f"bank_account {MASK}7890")


def test_a_date_of_birth_fires_on_a_label_or_on_a_name_and_on_neither_alone():
    """The ruling names an OR -- "beside a person-name-like token or the words 'date
    of birth'/'DOB'" -- so both halves are asserted, and so is the absence of both."""
    assert len(_of_kind(observe("Date of birth: 11/04/1990"), "date_of_birth")) == 1
    assert len(_of_kind(observe("Jane Marie Roberts  11/04/1990"),
                        "date_of_birth")) == 1
    assert _of_kind(observe("Payment due 11/04/1990"), "date_of_birth") == []


def test_one_identifier_printed_five_times_is_one_reading_that_counts_to_five():
    """§2.8's `occurrence_count` (P4 conformance rule 7). A card number on every page
    of a statement is one identifier; five rows would be five citations of one fact
    on a screen that counts them."""
    line = "Card 4242 4242 4242 4242 charged.\n"
    rows = _of_kind(observe(line * 5), "payment_card")
    assert len(rows) == 1
    assert rows[0].occurrence_count == 5


def test_a_page_with_no_identifier_produces_nothing():
    assert observe(
        "The syllabus is posted. Office hours are Tuesdays, and problem set 3 is "
        "due in week 4. Bring your student card.") == ()


def test_the_mask_may_not_be_widened_past_the_identifier():
    """A mask as long as the identifier is no mask. `masked_tail` refuses rather than
    returning the whole span, so a shorter scheme added later fails CLOSED."""
    assert masked_tail("MRN 4487211", 4, 11, mask_tail=4) == (7, 11)
    assert masked_tail("MRN 4487211", 4, 11, mask_tail=7) is None
    with pytest.raises(ValueError):
        masked_tail("MRN 4487211", 4, 11, mask_tail=0)


# --- the leak test, over the stored rows ------------------------------------------

@pytest.fixture()
def db(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    return conn


def _a_file_with(db, tmp_path, text: str):
    """One real `files` row, one real run through P4's own writer, and the identifier
    readings recorded onto that run -- which is how the pass runs in production."""
    path = tmp_path / "statement.txt"
    path.write_text(text)
    file_id = record_file(
        db, path, filename="statement.txt", normalized_filename="statement.txt",
        extension=".txt", observed_size=path.stat().st_size,
        observed_timestamps="{}", parent_folder_context=str(tmp_path),
        mime_type=None, detected_format=None, scan_state="scanned",
        materialized=True)
    content_hash = db.execute(
        "SELECT content_hash FROM files WHERE file_id = ?", (file_id,)
    ).fetchone()["content_hash"]
    run_id = RunWriter(db, author="P5").write(ExtractionResult(
        run=run(file_id=file_id, content_hash=content_hash,
                extractor_name="text.structured", extractor_version="0.4.0",
                source_type="text_document", analysis_tier="native", config={},
                completeness="complete", coverage=coverage("files", 1, 1),
                observation_count=1, started_at=FIXED_CLOCK,
                finished_at=FIXED_CLOCK),
        observations=(observation(
            file_id=file_id, content_hash=content_hash,
            extractor_name="text.structured", extractor_version="0.4.0",
            source_type="text_document", raw_value=text,
            location=location(zone="body"), observed_at=FIXED_CLOCK,
            reliability="possible"),),
        text_units=({"container_path": (), "text": text, "length": len(text),
                     "truncated": False},)))
    units = text_units_for_run(db, run_id)
    minted = identifier_observations(
        file_id=file_id, content_hash=content_hash, source_type="text_document",
        units=units, zone_for=lambda unit: "body", now=FIXED_CLOCK,
        mask_tail=IDENTIFIER_MASK_TAIL)
    for record in minted:
        record_observation(db, record)
    return file_id, content_hash, run_id, units, minted


#: Every identifier of the table above, on one page, in the document's own spelling.
PAGE = "\n".join(line for _kind, line, _whole, _miss in CASES)
WHOLE_IDENTIFIERS = tuple(whole for _kind, _line, whole, _miss in CASES)


def test_every_minted_reading_anchors_in_the_stored_unit(db, tmp_path):
    """P4 conformance rule 10 and RAW-1, through P4's own checker.

    The readings ride on the HOST run, so the unit their span points into is on their
    run at their container path -- which is what makes a masked reading with a real
    span lawful at all. SABOTAGE: mint onto a run_id of this module's own; every case
    raises `SpanAnchorError`.
    """
    _file_id, _hash, _run_id, units, minted = _a_file_with(db, tmp_path, PAGE)
    assert len(minted) == len(CASES)
    unit = units[0]
    for record in minted:
        check_span_anchor(record, unit)


def test_the_whole_identifier_is_in_no_stored_column_of_any_evidence_row(db,
                                                                        tmp_path):
    """THE RULING'S THIRD OBLIGATION: "the recorded value is never the whole
    identifier", asserted over the database rather than over the record.

    Eight columns can hold text and the dangerous one is the context window: §2.8's
    surrounding characters of a routing number hold the account number whole, which
    would restore exactly what the mask removed. So the whole row is searched, for
    every kind, in the spelling the document used.

    The host run's own `text_units` row still holds the document verbatim, and that
    is correct and is not what this asserts: P4's text is the file's own text under
    §8.4's gate. What must not exist is a second, addressable, RELEASABLE copy of the
    number wearing an evidence row's clothes.
    """
    _file_id, _hash, _run_id, _units, minted = _a_file_with(db, tmp_path, PAGE)
    stored = [{name: row[name] for name in row.keys()}
              for row in db.execute(
                  "SELECT * FROM evidence WHERE extractor_name LIKE ?",
                  (IDENTIFIERS_NAMESPACE + "%",))]
    assert len(stored) == len(minted) == len(CASES)
    for row in stored:
        printed = " | ".join(str(value) for value in row.values())
        for whole in WHOLE_IDENTIFIERS:
            assert whole not in printed, (whole, row["extractor_name"])
            assert whole.replace(" ", "") not in printed
        # The context window is not merely free of the identifier: it is EMPTY, and
        # the module says why -- the characters around an identifier are the rest of
        # the identifier and its neighbours.
        assert row["context_before"] is None and row["context_after"] is None


def test_a_reading_is_addressed_by_its_kind_so_two_kinds_are_two_citations(db,
                                                                          tmp_path):
    """`observation_key` hashes the extractor name, so the kind is part of the handle
    every consumer cites (M14) -- a `payment_card` and an `iban` ending in the same
    four digits stay two findings."""
    _file_id, _hash, _run_id, _units, minted = _a_file_with(db, tmp_path, PAGE)
    keys = {record.observation_key for record in minted}
    assert len(keys) == len(minted)
    assert {record.extractor_name for record in minted} == {
        IDENTIFIERS_NAMESPACE + kind for kind in KINDS}
