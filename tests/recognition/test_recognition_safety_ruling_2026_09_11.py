# tests/recognition/test_recognition_safety_ruling_2026_09_11.py
"""Seven members, ratified by the owner on 11 Sep 2026, in session.

`104` §18.2 "PROTECTED EVIDENCE" predicted this gap before it was measured: "the
missing words (vaccination, immunisation, hkid) are precisely the ones these
documents contain." `vaccination` and `hkid` were `96` §19's gap; this ruling
closes the sibling gap `96` §19 left standing in `medical`: the vocabulary carried
`vaccination record` (a phrase) and `immunization`/`immunisation` (bare, but filed
as CONTEXT -- see below) while the bare word `vaccine` was authored nowhere at all,
and `patient`, `diagnosis` and `prescription` sat as context terms that, by
`_safety_readings_in_evidence`'s own rule, "protect nothing."

The ruling names seven: `vaccine`, `vaccination`, `immunisation` (and the spelling
`immunization`), `prescription`, `diagnosis`, `medical record`, `patient`. Of the
seven, `medical record` was already an authored WORK TYPE (`96` §19) and needed no
change. The other six were context-only or entirely absent, so this ruling moves
`immunisation`/`immunization` from `context_terms` into `work_type_terms`
(`test_recognition_safety_vocabulary.py::test_the_british_spelling_is_authored_too`
carries that half) and adds `vaccine`, `vaccination`, `prescription`, `diagnosis`
and `patient` as new work types.

**ALL SEVEN ARE WORK TYPES**, for the same reason `96` §19 put its seven there:
`detector._safety_readings_in_evidence` reads `work_type_terms` and nothing else.
A term filed as context helps recognition and protects nothing.

These two pins are asserted against the PACKAGED manifest
(`src/recognition/library/recognition.json`), not a hand-built rule set, because
the claim under test is about the shipped vocabulary itself, not about the
detector's general mechanism (which `test_recognition_precaution_report.py`
already covers with a synthetic schema).
"""
from __future__ import annotations

from pathlib import Path

from evidence_shape.store import RunWriter
from extractors.runs import coverage
from extractors.shape import location, observation, run
from extractors.sink import ExtractionResult
from recognition.detector import (
    Abstention, ENTITY_NAMESPACE, PERSON_ENTITY, Precaution, Recognition,
)
from recognition.rules import load_rules
from test_recognition_detector import CLOCK, a_file, db, detector  # noqa: F401

MANIFEST_PATH = (Path(__file__).resolve().parents[2] / "src" / "recognition"
                 / "library" / "recognition.json")

#: The seven, as ratified. Data, not assertions -- so the ruling's own words travel
#: with the term the way `96` §19's `ADDED` tuple carries its "why".
RATIFIED: tuple[str, ...] = (
    "vaccine", "vaccination", "immunisation", "immunization",
    "prescription", "diagnosis", "medical record", "patient",
)


def _rules():
    return load_rules(MANIFEST_PATH.read_text)


def _name_someone(db, file_id, content_hash):
    """Mint a bare person-entity reading -- the corroboration a body-prose work
    type now needs (the owner's ruling of 13 Sep 2026, `Detector._corroborated`):
    "a person the entity encoder named anywhere in the file". Both files below
    are a real note about a real patient, so this is the encoder finding what a
    real pass would find, not a fact invented for the test.
    """
    observations = (observation(
        file_id=file_id, content_hash=content_hash,
        extractor_name=ENTITY_NAMESPACE + PERSON_ENTITY, extractor_version="0.1.0",
        source_type="text_document", raw_value="Jane Roberts",
        location=location(zone="body"), observed_at=CLOCK,
        reliability="possible"),)
    RunWriter(db, author="P5").write(ExtractionResult(
        run=run(file_id=file_id, content_hash=content_hash,
                extractor_name=ENTITY_NAMESPACE + PERSON_ENTITY,
                extractor_version="0.1.0", source_type="text_document",
                analysis_tier="native", config={}, completeness="complete",
                coverage=coverage("files", 1, 1), observation_count=1,
                started_at=CLOCK, finished_at=CLOCK),
        observations=observations))


def _held(db, file_id, content_hash, rules):
    """The report and the record, from one detector, for one file.

    Mirrors `test_recognition_precaution_report.py`'s `_held`: both are asserted
    together because a report of a hold nobody took, or a hold with no report, are
    the two ways gap 24 was broken.
    """
    engine = detector(rules)
    outcome = engine.explain(db, file_id, content_hash)
    report = engine.precaution_report(db, outcome, file_id=file_id,
                                      content_hash=content_hash)
    return outcome, report, engine(db, file_id, content_hash)


def test_all_seven_ratified_members_are_authored_as_medical_work_types():
    """The ruling names members, not roles -- but only a work type protects.

    Owner, 11 Sep 2026, in session: `vaccine`, `vaccination`, `immunisation`,
    `immunization`, `prescription`, `diagnosis`, `medical record`, `patient` are
    the protected-term vocabulary's seven members (`immunisation`/`immunization`
    counted once, as the ruling states them).
    """
    medical = _rules().schemas["medical"]
    for term in RATIFIED:
        assert term in medical.work_type_terms, term


def test_hkid_was_not_added_by_this_ruling():
    """Seven members, as ruled -- not eight. `hkid` is `96` §19's `identity` term.

    Register `104-DIAGNOSIS-FINAL.md` §18.2 names `hkid` in the same breath as
    `vaccination` and `immunisation`, but the ruling this pin defends draws the
    line at seven `medical` members. Adding `hkid` here would be this pin
    inventing a member the owner did not ratify.
    """
    medical = _rules().schemas["medical"]
    assert "hkid" not in medical.work_type_terms
    assert "hkid" not in medical.context_terms


def test_a_flu_vaccine_record_is_held_as_medical_and_sensitive_personal(
        db, tmp_path):
    """`96` §19's own worked example, one word over: `vaccine` rather than
    `vaccination` or `immunization`.

    `Covid -19 vaccination record (1).pdf` was `96` §19's saved-by-luck file; this
    is its sibling -- a flu shot record whose body never says `vaccination` at
    all, only `vaccine`. Before this ruling `vaccine` was authored nowhere, so
    `explain` would have abstained `no_evidence` and `precaution_report` would
    have returned `None`.

    AND SINCE the owner's ruling of 13 Sep 2026, the bare word in body prose
    corroborates rather than holds alone, so the fixture also names the
    patient the record is about.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "flu_shot.pdf",
        body="flu vaccine record 2022-2023")
    _name_someone(db, file_id, content_hash)

    outcome, report, record = _held(db, file_id, content_hash, _rules())

    assert isinstance(outcome, (Abstention, Recognition)), outcome
    assert isinstance(report, Precaution), report
    assert report.schema_id == "medical"
    assert "vaccine" in report.terms
    assert record is not None
    assert record.basis == "safety_domain"
    assert record.handling_class == "sensitive_personal"
    assert record.protected is True


def test_the_patients_prescription_is_held_as_medical_and_sensitive_personal(
        db, tmp_path):
    """`prescription` and `patient`, together, in the shape a real note takes.

    Neither word names a document format on its own -- that is exactly why `96`
    §19 called a term filed as context one that "protects nothing" -- so before
    this ruling a note built entirely of the two carried no safety work type and
    was never held.

    AND SINCE the owner's ruling of 13 Sep 2026, a body-prose work type also
    needs corroboration -- so the fixture names the patient, as a real note
    like this one would.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "zzqy8823.pdf",
        body="the patient's prescription")
    _name_someone(db, file_id, content_hash)

    outcome, report, record = _held(db, file_id, content_hash, _rules())

    assert isinstance(outcome, (Abstention, Recognition)), outcome
    assert isinstance(report, Precaution), report
    assert report.schema_id == "medical"
    assert set(report.terms) & {"patient", "prescription"}
    assert record is not None
    assert record.basis == "safety_domain"
    assert record.handling_class == "sensitive_personal"
    assert record.protected is True


def test_a_document_with_none_of_the_seven_and_no_other_term_is_not_held(
        db, tmp_path):
    """The negative twin, without which a detector that always held would pass.

    No safety-domain term, no work type, no context term of any kind -- so
    `explain` finds no evidence at all and there is nothing for any precaution
    to hold. The filename is deliberately inert too: `notes.pdf` would itself
    carry `academic`'s authored term `notes`, which is not the property this
    test is pinning.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "zzqx7412.pdf",
        body="The weather in April was unusually mild this year.")

    outcome, report, record = _held(db, file_id, content_hash, _rules())

    assert isinstance(outcome, Abstention), outcome
    assert outcome.reason == "no_evidence"
    assert report is None
    assert record is None
