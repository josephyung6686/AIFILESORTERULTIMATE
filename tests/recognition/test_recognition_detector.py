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
from recognition.detector import (
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
           subdirectory: str = ""):
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


def detector(rules, *, handling_for=None, is_protected=None):
    return Detector(
        rules, handling_for=POLICY if handling_for is None else handling_for,
        now=lambda: CLOCK, is_protected=is_protected)


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
