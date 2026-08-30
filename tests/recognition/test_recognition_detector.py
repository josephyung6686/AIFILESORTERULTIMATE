"""The detector, and every path on which it declines to classify.

Two rules shape this file.

**Abstention is a result, not a failure.** `00` requires abstention where two
readings are both supported. A detector that always returns a schema is worse than
one that returns `None`, because a confident wrong classification files a file
somewhere a person will never look for it. Every abstaining path is asserted on
directly, through `explain`, and then again through the `ClassificationProducer`.

**Every guard has its negative twin.** The positive half of a monotone property
cannot detect substitution: a detector that matched everything would pass every
"it fires on a matching file" test in this file. So each one is paired with a
near-miss that must NOT fire.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import record_file
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import RunWriter
from extractors.runs import coverage
from extractors.schema import create_extraction_schema
from extractors.shape import location, observation, run
from extractors.sink import ExtractionResult
from facts.domains import SCHEMA_IDS, UnknownSchema
from privacy.classification import ClassificationRecord, UnbackedClassification
from privacy.vocabulary import OutOfVocabulary
from recognition.detector import (  # noqa: F401
    SAFETY_DOMAIN_IDS, _tokens,
    Abstention, Detector, Handling, Recognition, SAFETY_DOMAIN_HANDLING,
)
from recognition.rules import load_rules
from recognition.vocabulary import ABSTENTION_REASONS, MANIFEST_VERSION

CLOCK = "2026-08-28T12:00:00+00:00"
MANIFEST_PATH = (Path(__file__).resolve().parents[2] / "src" / "recognition"
                 / "library" / "recognition.json")


# --- a small hand-built rule set ------------------------------------------------
# Deliberately not the packaged 8,907-term manifest: a unit test that moved every
# time a researcher edited a node row would stop being a test of the detector.

def schema_entry(schema_id, *, context=(), work_types=(),
                 source_types=("text_document",),
                 extensions=(".pdf",), readings=()):
    return {
        "schema_id": schema_id,
        "context_terms": sorted(context),
        "work_type_terms": sorted(work_types),
        "source_types": sorted(source_types),
        "extensions": sorted(extensions),
        "file_kind_never_alone": True,
        "rows": [f"{schema_id}.row"],
        "refused_rows": [],
        "needs_llm": ([{"row": f"{schema_id}.row", "readings": list(readings)}]
                      if readings else []),
        "never_alone_rows": [],
    }


def rule_set(*entries):
    payload = {"manifest_version": MANIFEST_VERSION, "compiled_rows": len(entries),
               "refused_rows": 0,
               "schemas": {entry["schema_id"]: entry for entry in entries}}
    return load_rules(lambda: json.dumps(payload))


ACADEMIC = schema_entry(
    "academic", context=("syllabus", "office hours"), work_types=("problem set",),
    readings=("an unlabelled essay whose only course signal is its register",))
MEDICAL = schema_entry(
    "medical", context=("discharge summary", "referral"), work_types=("care plan",))
FINANCE = schema_entry(
    "finance", context=("account statement", "referral"), work_types=("payslip",))


# --- the database this detector reads -------------------------------------------

@pytest.fixture()
def db(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    return conn


def a_file(db, tmp_path, filename: str, *, body: str | None = None,
           source_type: str = "text_document", extension: str = ".pdf",
           subdirectory: str = "", identifier: str | None = None):
    """One `files` row and its real P4 observations, through the real writers."""
    directory = tmp_path / subdirectory if subdirectory else tmp_path
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename
    path.write_bytes(filename.encode())
    file_id = record_file(
        db, path, filename=filename, normalized_filename=filename.casefold(),
        extension=extension, observed_size=path.stat().st_size,
        observed_timestamps="{}", parent_folder_context=str(directory),
        mime_type=None, detected_format=None, scan_state="scanned",
        materialized=True)
    content_hash = db.execute(
        "SELECT content_hash FROM files WHERE file_id = ?", (file_id,)
    ).fetchone()["content_hash"]

    observations = [observation(
        file_id=file_id, content_hash=content_hash,
        extractor_name="filesystem.record", extractor_version="0.1.0",
        source_type="filesystem", raw_value=filename,
        location=location(zone="filename"),
        observed_at=CLOCK, reliability="possible")]
    if body:
        observations.append(observation(
            file_id=file_id, content_hash=content_hash,
            extractor_name="pdf.text", extractor_version="0.1.0",
            source_type=source_type, raw_value=body,
            location=location(zone="body"),
            observed_at=CLOCK, reliability="possible"))
    if identifier:
        # A structured string is its OWN observation, spanned inside the body --
        # which is what `extractors/structured_text.py` emits on a real run, and
        # what lets a corroborating signal be told apart from the term matches
        # that named the schema.
        observations.append(observation(
            file_id=file_id, content_hash=content_hash,
            extractor_name="text.structured", extractor_version="0.1.0",
            source_type=source_type, raw_value=identifier,
            location=location(zone="body"),
            observed_at=CLOCK, reliability="possible"))
    RunWriter(db, author="P5").write(ExtractionResult(
        run=run(file_id=file_id, content_hash=content_hash,
                extractor_name="filesystem.record", extractor_version="0.1.0",
                source_type="filesystem", analysis_tier="filesystem", config={},
                completeness="complete", coverage=coverage("files", 1, 1),
                observation_count=len(observations), started_at=CLOCK,
                finished_at=CLOCK),
        observations=tuple(observations)))
    return file_id, content_hash


#: `00` states a protection for its four safety domains and for no other schema,
#: so `SAFETY_DOMAIN_HANDLING` alone would abstain on every ordinary schema. These
#: tests add one ordinary policy of their own -- which is exactly how a deployment
#: extends the shipped one -- so the recognition paths can be tested apart from the
#: policy paths.
POLICY = {**SAFETY_DOMAIN_HANDLING,
          "academic": Handling("personal_non_sensitive", False, "detector")}


def detector(rules, *, handling_for=None, is_protected=None,
             corroborating_observations=None, settled_by_user=None):
    return Detector(
        rules, handling_for=POLICY if handling_for is None else handling_for,
        now=lambda: CLOCK, is_protected=is_protected,
        corroborating_observations=corroborating_observations,
        settled_by_user=settled_by_user)


def _identifier_keys(db, value):
    """The deployment's answer to "which observations are structured identifiers".

    The DEPLOYMENT owns the pattern -- `cli.py` holds the only one that ships --
    so the detector is told which observations are identifiers rather than
    working it out. Here that is spelled by value, which is all these tests need.
    """

    def observations(conn, file_id, content_hash):
        return frozenset(
            row[0] for row in conn.execute(
                "SELECT observation_key FROM evidence WHERE file_id = ? "
                "AND content_hash = ? AND raw_value = ? "
                "AND superseded_by IS NULL", (file_id, content_hash, value)))

    return observations


# --- the standing security rule, checked before anything is read ------------------

def test_a_file_inside_a_protected_container_is_marked_counted_and_never_opened(
        db, tmp_path):
    """MARKED AND COUNTED, NEVER OPENED. A detector's natural instinct is to open a
    file to classify it; P3's rule is the one refusal nothing overrides."""
    file_id, content_hash = a_file(
        db, tmp_path, "Discharge summary care plan.pdf",
        subdirectory="Numbers.app/Contents")
    read: list[str] = []

    class Watched:
        """Every statement the detector issues, in order. `sqlite3.Connection` is
        a C type and takes no attribute assignment, so the seam is a proxy."""

        def execute(self, sql, *args):
            read.append(sql)
            return db.execute(sql, *args)

    outcome = detector(rule_set(MEDICAL)).explain(Watched(), file_id, content_hash)

    assert isinstance(outcome, Abstention)
    assert outcome.reason == "protected_container"
    # Present, named and explained -- never a silent skip and never an error.
    assert file_id in outcome.detail and "protected container" in outcome.detail
    # Never opened: the evidence table was not read, though the filename alone
    # carries two of this schema's terms and would otherwise have recognised it.
    assert not [sql for sql in read if "evidence" in sql.lower()], read


def test_the_same_file_outside_a_protected_container_is_recognised(db, tmp_path):
    """The negative twin. Without it, a detector that abstained on everything
    would pass the test above."""
    file_id, content_hash = a_file(
        db, tmp_path, "Discharge summary care plan.pdf", subdirectory="Records")
    outcome = detector(rule_set(MEDICAL)).explain(db, file_id, content_hash)
    assert isinstance(outcome, Recognition)
    assert outcome.schema_id == "medical"


def test_a_deployment_supplied_protected_predicate_can_only_add(db, tmp_path):
    file_id, content_hash = a_file(
        db, tmp_path, "Discharge summary care plan.pdf", subdirectory="Frameworks")
    marked = detector(rule_set(MEDICAL),
                      is_protected=lambda path: path.name == "Frameworks")
    assert marked.explain(db, file_id, content_hash).reason == "protected_container"


# --- the never-alone arity ------------------------------------------------------

def test_two_authored_terms_co_occurring_recognise_the_schema(db, tmp_path):
    file_id, content_hash = a_file(db, tmp_path, "Syllabus.pdf",
                                   body="Problem set 3 is due in office hours.")
    outcome = detector(rule_set(ACADEMIC)).explain(db, file_id, content_hash)
    assert isinstance(outcome, Recognition)
    assert outcome.schema_id == "academic"
    assert {match.term for match in outcome.matches} >= {"syllabus", "problem set"}
    assert outcome.evidence_refs


def test_one_authored_term_alone_never_recognises_anything(db, tmp_path):
    """`never_alone` read literally, and the negative twin of the test above.

    All 358 rows carry a `never_alone` array; the whole point of the word is that
    a single signal does not activate a schema. `00` states the same rule
    positively: a course code becomes a course fact "only when the engine finds a
    course-code pattern TOGETHER WITH academic context"."""
    file_id, content_hash = a_file(db, tmp_path, "Syllabus.pdf",
                                   body="Nothing else this schema authored.")
    outcome = detector(rule_set(ACADEMIC)).explain(db, file_id, content_hash)
    assert isinstance(outcome, Abstention)
    assert outcome.reason == "no_corroboration"
    assert outcome.schema_id == "academic"


def test_one_term_repeated_is_still_one_term(db, tmp_path):
    # The arity counts DISTINCT terms. Counting occurrences would let a single
    # word repeated in a filename and a heading activate a schema by itself.
    file_id, content_hash = a_file(db, tmp_path, "Syllabus syllabus.pdf",
                                   body="syllabus syllabus syllabus")
    outcome = detector(rule_set(ACADEMIC)).explain(db, file_id, content_hash)
    assert isinstance(outcome, Abstention)
    assert outcome.reason == "no_corroboration"


def test_a_file_matching_no_authored_term_abstains_with_no_evidence(db, tmp_path):
    file_id, content_hash = a_file(db, tmp_path, "IMG_5512.pdf", body="")
    outcome = detector(rule_set(ACADEMIC)).explain(db, file_id, content_hash)
    assert isinstance(outcome, Abstention)
    assert outcome.reason == "no_evidence"
    assert outcome.schema_id is None


# --- terms are tokens, not substrings --------------------------------------------

def test_a_term_matches_on_word_boundaries_and_not_inside_a_longer_word(db, tmp_path):
    # The compiled vocabulary holds two-letter terms -- `cc`, `re`, `qc`, `uv`.
    # Substring matching would fire `cc` on `soccer` and recognise a schema from a
    # word nobody authored.
    short = schema_entry("medical", context=("cc", "re"), work_types=())
    file_id, content_hash = a_file(db, tmp_path, "soccer.pdf",
                                   body="Recreation, according to nobody.")
    outcome = detector(rule_set(short)).explain(db, file_id, content_hash)
    assert isinstance(outcome, Abstention)
    assert outcome.reason == "no_evidence"


def test_the_same_two_terms_as_whole_words_do_match(db, tmp_path):
    short = schema_entry("medical", context=("cc", "re"), work_types=())
    file_id, content_hash = a_file(db, tmp_path, "cc.pdf", body="RE: the thing")
    outcome = detector(rule_set(short)).explain(db, file_id, content_hash)
    assert isinstance(outcome, Recognition)


def test_a_multi_word_term_matches_only_as_a_contiguous_phrase(db, tmp_path):
    file_id, content_hash = a_file(
        db, tmp_path, "Syllabus.pdf",
        body="The problem, and the set of hours in the office, are separate.")
    outcome = detector(rule_set(ACADEMIC)).explain(db, file_id, content_hash)
    assert isinstance(outcome, Abstention)
    assert outcome.reason == "no_corroboration"


# --- file kinds are corroboration, never a signal ---------------------------------

def test_a_plausible_file_kind_alone_recognises_nothing(db, tmp_path):
    # `file_kinds.never_alone` is `true` in all 358 rows.
    file_id, content_hash = a_file(db, tmp_path, "untitled.pdf", body="")
    outcome = detector(rule_set(ACADEMIC)).explain(db, file_id, content_hash)
    assert isinstance(outcome, Abstention)
    assert outcome.reason == "no_evidence"


def test_matched_terms_on_an_implausible_file_kind_do_not_recognise(db, tmp_path):
    file_id, content_hash = a_file(
        db, tmp_path, "Syllabus.dmg", extension=".dmg", source_type="opaque_binary",
        body="Problem set 3 is due in office hours.")
    outcome = detector(rule_set(ACADEMIC)).explain(db, file_id, content_hash)
    assert isinstance(outcome, Abstention)
    assert outcome.reason == "file_kind_implausible"
    assert outcome.schema_id == "academic"


# --- two readings both supported -> abstain, never pick --------------------------

def test_two_schemas_tied_on_the_same_evidence_abstain(db, tmp_path):
    """`00` requires abstention where two readings are both supported.

    `referral` is authored by both schemas here, exactly as 416 terms in the real
    manifest are authored by two or more. No threshold decides this: the two
    candidates score equally and a tie is an abstention."""
    both = rule_set(
        schema_entry("medical", context=("referral", "letter")),
        schema_entry("finance", context=("referral", "letter")))
    file_id, content_hash = a_file(db, tmp_path, "Referral letter.pdf")
    outcome = detector(both).explain(db, file_id, content_hash)
    assert isinstance(outcome, Abstention)
    assert outcome.reason == "ambiguous"
    assert set(outcome.tied_schema_ids) == {"medical", "finance"}


def test_the_schema_with_strictly_more_matched_terms_wins(db, tmp_path):
    """The negative twin: a tie abstains, a clear majority does not."""
    both = rule_set(
        schema_entry("medical", context=("referral", "letter", "care plan")),
        schema_entry("finance", context=("referral", "letter")))
    file_id, content_hash = a_file(db, tmp_path, "Referral letter.pdf",
                                   body="See the care plan.")
    outcome = detector(both).explain(db, file_id, content_hash)
    assert isinstance(outcome, Recognition)
    assert outcome.schema_id == "medical"


# --- the handling policy is the caller's -------------------------------------------

def test_a_recognised_schema_with_no_handling_policy_abstains_and_says_why(
        db, tmp_path):
    """The catalogue is FORBIDDEN from carrying a handling class.

    `planning/domains/_CONTRACT.md` rule 5: "`sensitivity` is §2.9's phrase and
    nothing more. Handling classes are P7's (§8.4). A catalogue that assigns one is
    inventing P7's vocabulary." So recognition and classification are two steps, and
    a schema `00` states no protection for is recognised and not classified."""
    file_id, content_hash = a_file(db, tmp_path, "Syllabus.pdf",
                                   body="Problem set 3 is due in office hours.")
    outcome = detector(rule_set(ACADEMIC),
                       handling_for=SAFETY_DOMAIN_HANDLING).explain(
                           db, file_id, content_hash)
    assert isinstance(outcome, Abstention)
    assert outcome.reason == "unassigned_handling"
    assert outcome.schema_id == "academic"
    # The needs_llm readings ride on the abstention so P8 can pick them up.
    assert outcome.deferred_readings == (
        "an unlabelled essay whose only course signal is its register",)


def test_a_caller_supplied_handling_policy_classifies_that_schema(db, tmp_path):
    file_id, content_hash = a_file(db, tmp_path, "Syllabus.pdf",
                                   body="Problem set 3 is due in office hours.")
    produce = detector(rule_set(ACADEMIC), handling_for={
        "academic": Handling(handling_class="personal_non_sensitive",
                             protected=False, basis="detector")})
    record = produce(db, file_id, content_hash)
    assert record.handling_class == "personal_non_sensitive"
    assert record.protected is False
    assert record.basis == "detector"


def test_a_handling_policy_naming_an_unrecognised_schema_is_a_load_error():
    with pytest.raises(UnknownSchema):
        Detector(rule_set(ACADEMIC), now=lambda: CLOCK, handling_for={
            "astrology": Handling("public_low", False, "detector")})


def test_a_handling_policy_outside_P7s_closed_vocabulary_is_a_load_error():
    with pytest.raises(OutOfVocabulary):
        Handling(handling_class="quite sensitive", protected=False, basis="detector")
    with pytest.raises(OutOfVocabulary):
        Handling(handling_class="public_low", protected=False, basis="a hunch")


def test_the_gate_outcome_can_never_be_offered_as_a_handling_policy():
    # D2: `unreadable_unclassified` is a gate OUTCOME, not a file fact. P7's store
    # refuses it; this refuses it a step earlier, where a policy is authored.
    with pytest.raises(UnbackedClassification):
        Handling(handling_class="unreadable_unclassified", protected=True,
                 basis="detector")


# --- `00`'s four safety domains ----------------------------------------------------

def test_the_shipped_policy_is_exactly_00s_four_safety_domains():
    """`00`:52: "Finance, identity, medical, and legal material should be
    implemented first as safety domains, meaning the system detects and protects
    them before any cloud or automated placement decision is allowed." """
    assert set(SAFETY_DOMAIN_HANDLING) == {"finance", "identity", "medical", "legal"}
    for handling in SAFETY_DOMAIN_HANDLING.values():
        # `00`:185: such material "should enter a protected state immediately".
        assert handling.protected is True
        assert handling.basis == "safety_domain"


def test_a_recognised_safety_domain_is_protected(db, tmp_path):
    file_id, content_hash = a_file(db, tmp_path, "Discharge summary.pdf",
                                   body="The care plan follows.")
    record = detector(rule_set(MEDICAL))(db, file_id, content_hash)
    assert isinstance(record, ClassificationRecord)
    assert record.protected is True
    assert record.basis == "safety_domain"
    assert record.file_id == file_id and record.content_hash == content_hash
    assert record.observed_at == CLOCK
    assert record.evidence_refs


def test_a_recognised_non_safety_domain_is_not_protected_by_this_policy(db, tmp_path):
    # The negative twin of the safety-domain test: `protected` is not something
    # every recognition sets, or the flag would carry no information.
    file_id, content_hash = a_file(db, tmp_path, "Syllabus.pdf",
                                   body="Problem set 3 is due in office hours.")
    record = detector(rule_set(ACADEMIC), handling_for={
        "academic": Handling("personal_non_sensitive", False, "detector")})(
            db, file_id, content_hash)
    assert record.protected is False


# --- the ClassificationProducer contract -------------------------------------------

def test_every_abstention_returns_None_through_the_producer_seam(db, tmp_path):
    produce = detector(rule_set(ACADEMIC))
    file_id, content_hash = a_file(db, tmp_path, "IMG_5512.pdf", body="")
    assert produce(db, file_id, content_hash) is None


def test_evidence_refs_are_P4_observation_keys_the_record_itself_validates(
        db, tmp_path):
    # `ClassificationRecord` refuses a reference that is not an `observation_key`
    # (M14). Constructing one at all is the proof that the detector cites keys.
    file_id, content_hash = a_file(db, tmp_path, "Discharge summary.pdf",
                                   body="The care plan follows.")
    record = detector(rule_set(MEDICAL))(db, file_id, content_hash)
    stored = {row["observation_key"] for row in db.execute(
        "SELECT observation_key FROM evidence WHERE file_id = ?", (file_id,))}
    assert set(record.evidence_refs) <= stored


def test_a_file_with_no_observations_at_all_abstains_rather_than_raising(db, tmp_path):
    path = tmp_path / "unread.pdf"
    path.write_bytes(b"x")
    file_id = record_file(
        db, path, filename="unread.pdf", normalized_filename="unread.pdf",
        extension=".pdf", observed_size=1, observed_timestamps="{}",
        parent_folder_context=str(tmp_path), mime_type=None, detected_format=None,
        scan_state="scanned", materialized=True)
    content_hash = db.execute(
        "SELECT content_hash FROM files WHERE file_id = ?", (file_id,)
    ).fetchone()["content_hash"]
    outcome = detector(rule_set(ACADEMIC)).explain(db, file_id, content_hash)
    assert isinstance(outcome, Abstention) and outcome.reason == "no_evidence"


def test_every_abstention_reason_this_package_names_is_reachable(db, tmp_path):
    # A named reason nothing can produce is a vocabulary entry pretending to be
    # behaviour. `needs_llm` is deliberately NOT in the tuple for that reason: this
    # detector never returns it, it only carries the readings.
    reached = {
        outcome.reason for outcome in (
            Abstention("protected_container", None, "x"),
            Abstention("no_evidence", None, "x"),
            Abstention("no_corroboration", "academic", "x"),
            Abstention("file_kind_implausible", "academic", "x"),
            Abstention("ambiguous", None, "x", tied_schema_ids=("a", "b")),
            Abstention("unassigned_handling", "academic", "x"),
        )}
    assert reached == set(ABSTENTION_REASONS)


# --- the packaged rule set on real evidence ------------------------------------------

def test_every_authored_safety_work_type_is_reachable_through_the_tokeniser():
    """The check that makes a spelling mismatch impossible to ship twice.

    A `TermMatch.term` is TOKENISED -- `_tokens` "separates on everything that is
    not a letter or digit" -- while `work_type_terms` holds the RAW authored
    strings. Comparing one to the other tests `'after visit summary'` for
    membership of a list containing `'after-visit summary'` and answers no.

    Shipped, that silently disarmed 159 of 470 safety work-type spellings, and a
    plaintext password-manager export (authored `'password-manager export'`)
    reached the end of a run with NO CLASSIFICATION ROW AT ALL. It is the worse
    direction: a person sees a syllabus wrongly marked sensitive, and does not see
    a password vault that was never marked.

    This asserts the property directly against the SHIPPED library rather than a
    hand-built rule set, because a hand-built one would be written in whatever
    spelling the test author happened to choose -- which is how the bug survived a
    green suite.
    """
    rules = load_rules(MANIFEST_PATH.read_text)
    det = detector(rules)

    unreachable = {
        schema_id: [term for term in rules.schemas[schema_id].work_type_terms
                    if " ".join(_tokens(term)) not in det._work_types[schema_id]]
        for schema_id in SAFETY_DOMAIN_IDS if schema_id in rules.schemas}
    named = {schema: terms for schema, terms in unreachable.items() if terms}

    assert not named, (
        "authored safety work-type terms that no evidence can ever match, because "
        f"the comparison uses a different spelling from the tokeniser: {named}")


def test_the_packaged_manifest_recognises_a_real_safety_domain_file(db, tmp_path):
    rules = load_rules(MANIFEST_PATH.read_text)
    file_id, content_hash = a_file(
        db, tmp_path, "Bank account statement 2026.pdf",
        body="Closing balance and direct debit for the statement period.")
    outcome = detector(rules).explain(db, file_id, content_hash)
    assert isinstance(outcome, Recognition), outcome
    assert outcome.schema_id == "finance"


def test_the_packaged_manifest_abstains_on_a_file_that_says_nothing(db, tmp_path):
    rules = load_rules(MANIFEST_PATH.read_text)
    file_id, content_hash = a_file(db, tmp_path, "IMG_5512.pdf", body="")
    assert isinstance(detector(rules).explain(db, file_id, content_hash), Abstention)


def test_the_packaged_rule_set_names_only_schemas_the_product_recognises():
    rules = load_rules(MANIFEST_PATH.read_text)
    assert set(rules.schemas) <= set(SCHEMA_IDS)


# --- the term arrays were also used as a notes field -------------------------------

NOTE = ("proposed for r6, not design: accession register, deaccession, object "
        "entry, transfer of title, credit line, condition report, previous "
        "intervention, treatment report, reversibility, preventive conservation, "
        "each proposed only as a candidate that must co-occur with a second signal")


def test_an_editorial_note_compiled_as_a_term_matches_nothing_and_changes_nothing(
        db, tmp_path):
    """1,616 of the 9,647 authored entries are six words or longer and 32 are
    twenty or longer, because several rows used `work_types` and
    `proposed_context_terms` as a notes field. They compile -- the compiler does
    not get to decide that a researcher's entry is not a term -- and they can never
    match a real file. The guard is that their presence is inert."""
    plain = detector(rule_set(ACADEMIC))
    noted = detector(rule_set(schema_entry(
        "academic", context=("syllabus", "office hours", NOTE),
        work_types=("problem set",))))
    file_id, content_hash = a_file(db, tmp_path, "Syllabus.pdf",
                                   body="Problem set 3 is due in office hours.")
    before = plain.explain(db, file_id, content_hash)
    after = noted.explain(db, file_id, content_hash)
    assert isinstance(before, Recognition) and isinstance(after, Recognition)
    assert {m.term for m in before.matches} == {m.term for m in after.matches}


def test_the_phrase_scan_stops_where_no_authored_term_continues(db, tmp_path):
    """A fixed window sized by the LONGEST TERM would widen every scan in the
    corpus by the length of the longest editorial aside -- eighty-one tokens, for
    a phrase that can never match. The scan is bounded by the authored prefixes
    instead, so a text nobody wrote a term for costs one lookup per word."""
    noted = detector(rule_set(schema_entry(
        "academic", context=("syllabus", NOTE), work_types=())))

    class Counting(dict):
        lookups = 0

        def get(self, key, default=None):
            type(self).lookups += 1
            return super().get(key, default)

    Counting.lookups = 0
    noted._index = Counting(noted._index)
    words = "alpha beta gamma delta epsilon zeta eta theta iota kappa".split()
    list(noted._terms_in(" ".join(words)))
    assert Counting.lookups == len(words), Counting.lookups


def test_a_no_corroboration_abstention_names_every_reading_it_could_not_choose(
        db, tmp_path):
    """One term each from two schemas is a TIE, and the record must say so.

    `leaders` is `sorted(...)`, so reporting `leaders[0]` picks ALPHABETICALLY and
    silently drops the rest. On a real file reading "Passport number X12345678.
    Client identity document." the readings are `creative` (from 'client') and
    `identity` (from 'passport'). `identity` is one of `00`'s four SAFETY
    DOMAINS, and it lost a coin toss to alphabetical order -- so the file's most
    alarming reading was present in the evidence and thrown away before anything
    downstream could see it.

    This changes no classification. The detector still abstains, for the same
    reason, with the same arity rule. It stops the abstention being a LOSSY
    record of what was found. `tied_schema_ids` already exists for exactly this
    and the `ambiguous` branch already populates it.
    """
    rules = rule_set(
        schema_entry("creative", context=("client",)),
        schema_entry("identity", work_types=("passport",)))
    file_id, content_hash = a_file(
        db, tmp_path, "Client Passport.pdf",
        body="Passport number X12345678. Client identity document.")

    outcome = detector(rules).explain(db, file_id, content_hash)

    assert isinstance(outcome, Abstention)
    assert outcome.reason == "no_corroboration"
    assert set(outcome.tied_schema_ids) == {"creative", "identity"}, (
        f"the tie was recorded as {outcome.tied_schema_ids!r} and the reading "
        f"reported was {outcome.schema_id!r}; a safety domain was dropped by "
        "alphabetical order")


def test_a_single_unambiguous_reading_still_records_no_tie(db, tmp_path):
    """The negative twin. Filling `tied_schema_ids` unconditionally would make
    every one-term abstention look contested -- a different false record, in the
    other direction, and one that would make the field useless for the safety
    reading it exists to preserve."""
    rules = rule_set(
        schema_entry("creative", context=("client",)),
        schema_entry("identity", work_types=("passport",)))
    file_id, content_hash = a_file(db, tmp_path, "Passport.pdf",
                                   body="Passport number X12345678.")

    outcome = detector(rules).explain(db, file_id, content_hash)

    assert isinstance(outcome, Abstention)
    assert outcome.reason == "no_corroboration"
    assert outcome.schema_id == "identity"
    assert outcome.tied_schema_ids == (), (
        "one reading is not a tie and must not be recorded as one")


def test_a_tie_that_includes_a_safety_domain_still_protects_the_file(db, tmp_path):
    """Corroboration governs what we CLAIM. Precaution governs what we EXPOSE.

    `never_alone` is a rule about ACTIVATING A SCHEMA, and the detector applied it
    to protection as well -- so "Passport number X12345678. Client identity
    document." matched `creative` ('client') and `identity` ('passport'), tied at
    one term each, abstained, and the file came back unclassified and UNPROTECTED.
    Its number then became a proposed folder name on the litigator's corpus.

    `00`:52 states the opposite requirement for exactly these four domains:
    finance, identity, medical and legal are "detected and protected BEFORE any
    cloud or automated placement decision is allowed", and `00`:185 says such
    material "should enter a protected state immediately". Neither sentence asks
    for corroboration first; both are about precaution.

    So the two questions are answered separately, and the answers differ:
    `explain` still ABSTAINS -- no schema is activated, the file is honestly
    unrecognised -- while the classification carries the safety domain's own
    handling, with `basis='safety_domain'` saying exactly why.
    """
    rules = rule_set(
        schema_entry("creative", context=("client",)),
        schema_entry("identity", work_types=("passport",)))
    file_id, content_hash = a_file(
        db, tmp_path, "Client Passport.pdf",
        body="Passport number X12345678. Client identity document.")
    det = detector(rules)

    # Recognition is unchanged: it still declines to say what the file IS.
    assert isinstance(det.explain(db, file_id, content_hash), Abstention)

    record = det(db, file_id, content_hash)
    assert record is not None, (
        "a file whose evidence names a safety domain came back unclassified and "
        "unprotected, so nothing downstream could keep its number off the disk")
    assert record.protected is True
    assert record.basis == "safety_domain"
    assert record.evidence_refs, "a protection with no evidence behind it"


def test_a_tie_with_no_safety_domain_in_it_is_still_simply_unclassified(
        db, tmp_path):
    """The negative twin, and the guard against the collapse this project already
    made once.

    `cli.py`'s `classifier` records what happened last time an abstention was
    answered with protection: it "made an unreadable scan and a passport
    identical in P7's store -- same class, same flag, same sentence to the user".
    The rule above must fire ONLY on a safety-domain reading, never on a tie in
    general, or that collapse comes straight back.
    """
    rules = rule_set(
        schema_entry("creative", context=("client",)),
        schema_entry("academic", context=("syllabus",)))
    file_id, content_hash = a_file(db, tmp_path, "Notes.pdf",
                                   body="client syllabus")
    det = detector(rules)

    assert isinstance(det.explain(db, file_id, content_hash), Abstention)
    assert det(db, file_id, content_hash) is None, (
        "an ordinary unrecognised file was marked protected; that is the "
        "over-protection collapse, not a precaution")


def test_a_safety_domain_is_protected_even_when_another_schema_wins_outright(
        db, tmp_path):
    """The same passport, one branch over -- and the branch precaution never reached.

    `_precaution` fixed this for the TIE. `__call__` consults it only when `explain`
    returns an `Abstention`, so a file whose evidence names a safety domain is
    protected when no schema wins and unprotected when one does. Winning is a fact
    about what we CLAIM; the docstring above says in terms that precaution governs
    what we EXPOSE, and gating it on the outcome of the claim is the confusion that
    sentence exists to forbid.

    Measured through the shipped CLI before this test existed: a file reading
    "Passport number A1234567 -- scanned copy for records." matched `photos` on
    'scan', won outright, and was stored `personal_non_sensitive, protected=0,
    review_policy='auto_eligible'` -- then the report offered to file it into a
    folder named `A1234567`. `00`:52 requires these four domains "detected and
    protected BEFORE any cloud or automated placement decision is allowed", and
    `00`:185 says such material "should enter a protected state immediately".
    Neither sentence has an exception for a file some other schema also describes.

    `explain` is deliberately unchanged: the file really is coursework, and saying
    so is honest. Only the classification moves.
    """
    # `passport` is a WORK TYPE, matching the shipped library, where `identity`
    # carries no context terms at all. Spelling it as a context term here would
    # assert the broader rule and reject the narrowing the next test requires.
    rules = rule_set(
        schema_entry("academic", context=("syllabus", "lecture")),
        schema_entry("identity", work_types=("passport",)))
    file_id, content_hash = a_file(
        db, tmp_path, "Passport Scan.pdf",
        body="Passport number X12345678. syllabus and lecture handout.")
    det = detector(rules)

    # The CLAIM is untouched: academic wins outright on two terms against one.
    outcome = det.explain(db, file_id, content_hash)
    assert isinstance(outcome, Recognition) and outcome.schema_id == "academic", outcome

    record = det(db, file_id, content_hash)
    assert record is not None
    assert record.protected is True, (
        "a passport was stored unprotected because another schema described the "
        "file better; its number is now free to become a folder name")
    assert record.basis == "safety_domain"
    assert record.evidence_refs, "a protection with no evidence behind it"


def test_a_winning_schema_with_no_safety_domain_present_is_left_alone(db, tmp_path):
    """The negative twin, guarding the collapse this project already made once.

    `cli.py`'s `classifier` records what happened when an abstention was answered
    with protection: it "made an unreadable scan and a passport identical in P7's
    store". The rule above must fire ONLY where a safety-domain term is actually in
    the file's own evidence -- never on every recognition -- or that collapse
    returns through the door the tie fix left open.

    **The safety schema must be IN the rule set for this to falsify anything.** A
    corpus where no safety domain exists cannot show one failing to fire, and an
    earlier version of this test built a rule set of `academic` alone -- so it
    passed under every possible implementation and guarded nothing. `finance` is
    here, with a context term the file genuinely contains, and must stay silent.
    """
    rules = rule_set(schema_entry("academic", context=("syllabus", "lecture")),
                     schema_entry("finance", context=("credit",)))
    file_id, content_hash = a_file(
        db, tmp_path, "Week 1.pdf",
        body="syllabus and lecture handout. Four credit hours.")
    det = detector(rules)

    record = det(db, file_id, content_hash)
    assert record is not None
    assert record.protected is False, (
        "an ordinary coursework file was marked protected; that is the "
        "over-protection collapse, not a precaution")
    assert record.basis == "detector"


def test_a_safety_term_in_the_directory_chain_protects_nothing_under_it(db, tmp_path):
    """The trap the guard above walks straight into, found by running the product.

    `_matches` reads every live observation, and P4's `path` locator holds the whole
    ancestor chain -- so a corpus under a folder called `Passport` names `identity`
    for every file inside it. Measured: a two-file corpus in a scratch directory
    named `passport/` came back with BOTH files "protected material (§8.4)",
    including a syllabus, and the same run under a neutrally-named directory
    protected only the passport.

    This is the defect `test_a_term_from_the_absolute_path_alone_cannot_be_
    corroborated` already fixed for corroboration, arriving on the protection path:
    "Every file on a disk sits under some words, and none of them are its own."
    Over-protection is the collapse this project made once already, and a rule that
    protects a whole folder because of its name would reach it by a new route.
    """
    rules = rule_set(
        schema_entry("academic", context=("syllabus", "lecture")),
        schema_entry("identity", work_types=("passport",)))
    file_id, content_hash = a_file(
        db, tmp_path, "Week 1.pdf", body="syllabus and lecture handout.")
    # `a_file` writes filename and body zones only; P4's `path` observation is what
    # carries the ancestor chain on a real run, and it is the whole point here. Its
    # locator serializes to bare "path", which is what `_path_keys` selects on.
    RunWriter(db, author="P5").write(ExtractionResult(
        run=run(file_id=file_id, content_hash=content_hash,
                extractor_name="filesystem.record", extractor_version="0.1.0",
                source_type="filesystem", analysis_tier="filesystem", config={},
                completeness="complete", coverage=coverage("files", 1, 1),
                observation_count=1, started_at=CLOCK, finished_at=CLOCK),
        observations=(observation(
            file_id=file_id, content_hash=content_hash,
            extractor_name="filesystem.record", extractor_version="0.1.0",
            source_type="filesystem",
            raw_value="/Users/jo/Documents/Passport Scans/Week 1.pdf",
            location=location(zone="path"), observed_at=CLOCK,
            reliability="possible"),)))

    record = detector(rules)(db, file_id, content_hash)

    assert record is not None
    assert record.protected is False, (
        "a word in a parent directory protected a file that carries no safety "
        "term of its own; every file under a folder called Passport would be held")


def test_a_file_carrying_no_term_at_all_is_never_protected(db, tmp_path):
    """The other twin. Precaution keys on EVIDENCE PRESENT, never on absence --
    "we deliberately did not look" and "we could not tell" are different answers
    and must not become the same one."""
    rules = rule_set(schema_entry("identity", work_types=("passport",)))
    file_id, content_hash = a_file(db, tmp_path, "Notes.pdf",
                                   body="nothing any schema authored")
    det = detector(rules)

    assert det(db, file_id, content_hash) is None


def test_a_structured_identifier_corroborates_the_one_term_that_named_a_schema(
        db, tmp_path):
    """`00`'s own worked example, which could not execute until now.

    `00` states the rule as: "BUSIB 4300 becomes a course fact only when the
    engine finds a course-code PATTERN TOGETHER WITH academic context such as
    'syllabus,' 'lecture,' 'credits,' 'instructor,' or 'semester.'" That is ONE
    PATTERN and ONE TERM.

    The implementation required TWO TERMS, and `SchemaRules` has no pattern field
    at all, so a course code contributed exactly zero to recognition. The
    sentence `00` uses to define the whole mechanism described something the
    product could not do.

    `never_alone` is unchanged and still literal: one SIGNAL never activates a
    schema. What changes is that a signal stops being assumed to be a term.

    **A pattern corroborates and never nominates.** The deployment's identifier
    pattern is schema-AGNOSTIC -- `PHYS1401` and `X12345678` are the same shape to
    it -- so it cannot say WHICH schema a file belongs to and is never allowed to
    try. It can only second a schema that a term already named, which is why this
    adds no false positive: a file whose terms name two schemas still abstains.
    """
    rules = rule_set(schema_entry("academic", context=("syllabus",)))
    file_id, content_hash = a_file(db, tmp_path, "Syllabus.pdf",
                                   body="Syllabus for BUSIB 4300.",
                                   identifier="BUSIB 4300")
    identifiers = _identifier_keys(db, "BUSIB 4300")

    outcome = detector(rules, corroborating_observations=identifiers).explain(
        db, file_id, content_hash)

    assert isinstance(outcome, Recognition), (
        f"`00`'s own example still does not recognise: {outcome}")
    assert outcome.schema_id == "academic"


def test_a_structured_identifier_cannot_break_a_tie_between_two_schemas(
        db, tmp_path):
    """The negative twin that matters most, and the reason this is not the
    declared-situation shortcut.

    An identifier says "this file carries a structured code". It does not say
    WHICH schema authored that code -- the shipped pattern matches a course code,
    a claim number and a passport number identically. So it may second a schema a
    term already named and may never choose between two. A deposition transcript
    whose only term is authored by seven schemas must still abstain.
    """
    rules = rule_set(
        schema_entry("law_practice", context=("transcript",)),
        schema_entry("academic", context=("transcript",)))
    file_id, content_hash = a_file(db, tmp_path, "Deposition.pdf",
                                   body="Transcript in re CV20261234.",
                                   identifier="CV20261234")
    identifiers = _identifier_keys(db, "CV20261234")

    outcome = detector(rules, corroborating_observations=identifiers).explain(
        db, file_id, content_hash)

    assert isinstance(outcome, Abstention), (
        f"a schema-agnostic pattern chose between two readings: {outcome}")
    assert outcome.reason == "no_corroboration"


def test_a_file_with_an_identifier_and_no_term_still_recognises_nothing(
        db, tmp_path):
    """The other twin. A pattern alone is one signal, and `never_alone` holds:
    a corroborating signal with nothing to corroborate activates nothing."""
    rules = rule_set(schema_entry("academic", context=("syllabus",)))
    file_id, content_hash = a_file(db, tmp_path, "Notes.pdf",
                                   body="PHYS1401 and nothing else.",
                                   identifier="PHYS1401")
    identifiers = _identifier_keys(db, "PHYS1401")

    outcome = detector(rules, corroborating_observations=identifiers).explain(
        db, file_id, content_hash)

    assert isinstance(outcome, Abstention)
    assert outcome.reason == "no_evidence"


def test_a_deployment_that_supplies_no_identifier_reader_is_unchanged(
        db, tmp_path):
    """The authority is injected and absent means "this deployment finds none",
    which must behave exactly as before rather than as "none present"."""
    rules = rule_set(schema_entry("academic", context=("syllabus",)))
    file_id, content_hash = a_file(db, tmp_path, "Syllabus.pdf",
                                   body="Syllabus for BUSIB 4300.")

    outcome = detector(rules).explain(db, file_id, content_hash)

    assert isinstance(outcome, Abstention)
    assert outcome.reason == "no_corroboration"


def test_a_term_from_the_absolute_path_alone_cannot_be_corroborated(db, tmp_path):
    """Every file on a disk sits under some words, and none of them are its own.

    Found by running the product, not by reading it. A corpus in a directory
    called `.../test_a_placement_the_person_mu0/` matched the authored term
    'placement' out of the PATH observation -- P4's `path` locator holds the whole
    ancestor chain -- and a structured identifier in the body then confirmed it,
    so four files containing nothing but a meaningless code classified as
    `creative`.

    §2.2 ranks "a filename, title, or page-one heading" as meaningful evidence and
    says nothing about the machine's directory chain. So corroboration requires a
    nominating term from the file ITSELF. The two-term rule is deliberately
    untouched: whether a path may supply both terms is a different question from
    this one, and answering it here would be widening the change under cover of a
    fix.
    """
    rules = rule_set(schema_entry("academic", context=("syllabus",)))
    file_id, content_hash = a_file(
        db, tmp_path, "a.txt", subdirectory="syllabus_backups",
        body="QQQ1111 and nothing else.", identifier="QQQ1111")
    identifiers = _identifier_keys(db, "QQQ1111")

    outcome = detector(rules, corroborating_observations=identifiers).explain(
        db, file_id, content_hash)

    assert isinstance(outcome, Abstention), (
        f"a word in a parent directory named this file's schema: {outcome}")


def test_a_term_in_the_files_own_name_is_still_the_files_own(db, tmp_path):
    """The negative twin. §2.2 names the FILENAME as meaningful evidence, so
    narrowing this to body text only would throw away the case `00` calls out."""
    rules = rule_set(schema_entry("academic", context=("syllabus",)))
    file_id, content_hash = a_file(
        db, tmp_path, "Syllabus.pdf", body="QQQ1111 and nothing else.",
        identifier="QQQ1111")
    identifiers = _identifier_keys(db, "QQQ1111")

    outcome = detector(rules, corroborating_observations=identifiers).explain(
        db, file_id, content_hash)

    assert isinstance(outcome, Recognition), (
        f"the file's own name stopped counting as evidence about it: {outcome}")


# --- what a person's own answer resolves (P15) ------------------------------------


def test_a_confirmed_answer_resolves_a_tie_the_evidence_cannot(db, tmp_path):
    """`00` requires abstention where two readings are both supported BY EVIDENCE.
    A person's answer is not evidence about the file -- it is authority about the
    person -- so it settles a tie without breaking that rule.

    `66` §13 puts this in the structural column in as many words: a structural
    answer "resolves a user relationship or policy fact that FILE EVIDENCE CANNOT
    SAFELY DETERMINE", and may "resolve role ambiguity". The tie is exactly such a
    fact: the file is one thing, the words support two readings, and the person
    knows which.

    What the person settled is the SCHEMA, not the handling class. The
    classification's `basis` keeps saying where the HANDLING came from -- the
    deployment's policy, so `detector` -- because overloading it with "a person
    was involved in the recognition" would blur two different claims about the
    file. Where the answer came from is P15's own record, which is where §13 says
    a person goes to inspect it.
    """
    rules = rule_set(
        schema_entry("academic", context=("transcript",)),
        schema_entry("law_practice", context=("transcript",)))
    file_id, content_hash = a_file(db, tmp_path, "Notes.pdf",
                                   body="transcript and more transcript detail")
    tied = detector(rules).explain(db, file_id, content_hash)
    assert isinstance(tied, Abstention), tied

    settled = detector(rules, settled_by_user=lambda: frozenset({"academic"}))
    outcome = settled.explain(db, file_id, content_hash)

    assert isinstance(outcome, Recognition), (
        f"the person said which reading is right and it changed nothing: {outcome}")
    assert outcome.schema_id == "academic"
    assert settled(db, file_id, content_hash).handling_class == (
        POLICY["academic"].handling_class)


def test_an_answer_naming_neither_tied_reading_settles_nothing(db, tmp_path):
    """The negative twin. An answer about a different corpus, or one the person
    gave before these files existed, must not reach in and decide this tie."""
    rules = rule_set(
        schema_entry("academic", context=("transcript",)),
        schema_entry("law_practice", context=("transcript",)))
    file_id, content_hash = a_file(db, tmp_path, "Notes.pdf",
                                   body="transcript and more transcript detail")

    outcome = detector(
        rules, settled_by_user=lambda: frozenset({"finance"})
    ).explain(db, file_id, content_hash)

    assert isinstance(outcome, Abstention)


def test_an_answer_naming_both_tied_readings_settles_nothing(db, tmp_path):
    """The other twin, and the one that keeps `00`'s rule intact. If the person
    has confirmed BOTH readings somewhere, the tie is still a tie -- and choosing
    between them would be the invented tie-breaker this package exists without."""
    # Two DISTINCT terms each, so the tie is the `ambiguous` one rather than the
    # arity one -- the reading both branches share is that nothing breaks it.
    rules = rule_set(
        schema_entry("academic", context=("transcript", "witness")),
        schema_entry("law_practice", context=("transcript", "witness")))
    file_id, content_hash = a_file(db, tmp_path, "Notes.pdf",
                                   body="transcript of the witness")

    outcome = detector(
        rules, settled_by_user=lambda: frozenset({"academic", "law_practice"})
    ).explain(db, file_id, content_hash)

    assert isinstance(outcome, Abstention)
    assert outcome.reason == "ambiguous"


def test_an_answer_cannot_activate_a_schema_the_evidence_never_supported(db, tmp_path):
    """The most important twin. A confirmed answer RESOLVES an ambiguity the file
    raised; it does not put a reading into a file that never suggested one.

    Otherwise a person who once said "Columbia is where I study" would have every
    unrelated file on their disk read as coursework, which is `66` §13's
    prohibition on an answer being "reused outside its stated scope" arriving as a
    recognition bug.
    """
    rules = rule_set(schema_entry("academic", context=("syllabus",)))
    file_id, content_hash = a_file(db, tmp_path, "Notes.pdf",
                                   body="nothing any schema authored")

    outcome = detector(
        rules, settled_by_user=lambda: frozenset({"academic"})
    ).explain(db, file_id, content_hash)

    assert isinstance(outcome, Abstention)
    assert outcome.reason == "no_evidence"
