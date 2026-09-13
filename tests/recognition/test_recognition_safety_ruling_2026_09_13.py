# tests/recognition/test_recognition_safety_ruling_2026_09_13.py
"""Five identity work types, ratified by the owner on 13 Sep 2026, in session.

`104` §18.57 measured the gap on the second corpus: a two-factor code sheet and an
entry/admission record that no deterministic layer held, because the identity
domain's authored work types ("backup codes", "recovery codes", "two-factor
recovery-code sheet", "entry, admission, or arrival/departure record") never
appear word-for-word in such a file. Measured before the ruling, the five terms
newly held exactly three corpus files, all three key-protected, and no ordinary
file.

ALL FIVE ARE WORK TYPES, on the 11 Sep ruling's own reason: `detector.
_safety_readings_in_evidence` reads `work_type_terms` and nothing else.
"""
from __future__ import annotations

from pathlib import Path

from recognition.detector import Abstention, Precaution
from recognition.rules import load_rules
from test_recognition_detector import a_file, db, detector  # noqa: F401

MANIFEST_PATH = (Path(__file__).resolve().parents[2] / "src" / "recognition"
                 / "library" / "recognition.json")

RATIFIED: tuple[str, ...] = (
    "two-step verification", "two-step verification codes",
    "form i-94", "arrival/departure record", "class of admission",
)


def _rules():
    return load_rules(MANIFEST_PATH.read_text)


def test_all_five_ratified_members_are_authored_as_identity_work_types():
    rules = _rules()
    work_types = set(rules.schemas["identity"].work_type_terms)
    missing = [term for term in RATIFIED if term not in work_types]
    assert not missing, missing


def test_a_two_step_verification_code_sheet_is_held_as_identity(db, tmp_path):
    file_id, content_hash = a_file(
        db, tmp_path, "codes.txt", extension=".txt",
        heading="Two-step verification codes", body=
        "Two-step verification codes\n\nUse one of these codes to sign in if you "
        "lose your phone.\n1234 5678\n2345 6789\n3456 7890\n")
    engine = detector(_rules())
    outcome = engine.explain(db, file_id, content_hash)
    report = engine.precaution_report(db, outcome, file_id=file_id,
                                      content_hash=content_hash)
    assert isinstance(report, Precaution) and report.schema_id == "identity", (
        outcome, report)


def test_an_entry_record_is_held_as_identity(db, tmp_path):
    file_id, content_hash = a_file(
        db, tmp_path, "entry.txt", extension=".txt",
        heading="Form I-94 arrival/departure record", body=
        "Form I-94 arrival/departure record\nClass of admission: F1\n"
        "Admit until date: D/S\n")
    engine = detector(_rules())
    outcome = engine.explain(db, file_id, content_hash)
    report = engine.precaution_report(db, outcome, file_id=file_id,
                                      content_hash=content_hash)
    assert isinstance(report, Precaution) and report.schema_id == "identity", (
        outcome, report)
