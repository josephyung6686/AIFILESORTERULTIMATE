# tests/recognition/test_recognition_no_safety_evidence.py
"""The detector already knows it saw no safety word. This is it saying so.

`96` §20, on the 41 files stored `personal_non_sensitive, protected=0` having matched
no safety work type at all: *"It can KNOW it. It cannot currently SAY it. Both halves
matter."*

  KNOWS IT   `_safety_readings_in_evidence` returns exactly the empty tuple for them,
             and `__call__` already computes it on the way to
             `_safety_readings_naming_the_file`.
  SAYS IT    `privacy.vocabulary.CLASSIFICATION_BASES` gained
             `detector_no_safety_evidence`, so there is now a word for the weaker
             claim. `privacy.denial.no_safety_evidence_denies` is what acts on it.

**Recognition is untouched and must stay untouched.** The schema still wins, the
handling class is still the deployment's, the protected flag is still `False`. A test
here that changed any of those would be re-running the over-protection collapse
`cli.classifier` records -- the one that "made an unreadable scan and a passport
identical in P7's store" -- under a new name. What changes is one field, and the field
is the one SPEC §2 provides for saying where a conclusion came from.

WHY THE DISTINCTION IS NOT "did a safety schema lose". It is whether any safety
domain's OWN WORK TYPE -- a term that says what the file IS, not a word that
surrounds such a document -- appeared anywhere in the file's evidence. That is the
same question `_precaution` and the winning-schema guard already ask, asked once more
for the record rather than for a verdict.
"""
from __future__ import annotations

from privacy.vocabulary import DETECTOR, DETECTOR_NO_SAFETY_EVIDENCE

from recognition.detector import Handling
from test_recognition_detector import (  # the packaged harness
    ACADEMIC, a_file, db, detector, rule_set, schema_entry)  # noqa: F401

#: A safety domain spelled the way the real library spells one: a work type that says
#: what the file IS, and a context term that merely accompanies such a document.
#: `credit` is the real one -- out of "credit hours" it marked two university syllabi
#: `sensitive_personal` -- and it is here so the context/work-type line is under test
#: rather than assumed.
FINANCE = schema_entry(
    "finance", context=("credit", "account"),
    work_types=("bank statement", "payslip"))

#: The deployment's shape, in miniature: ordinary schemas carry `detector`, safety
#: schemas carry `safety_domain`. `cli.HANDLING_POLICY` is the real one and it is not
#: imported here, because these tests are about the BASIS the detector chooses and
#: not about which classes this deployment happens to hand out.
POLICY = {
    "academic": Handling(handling_class="personal_non_sensitive", protected=False,
                         basis=DETECTOR),
    "finance": Handling(handling_class="sensitive_personal", protected=True,
                        basis="safety_domain"),
}


def _classify(db, tmp_path, **kwargs):
    file_id, content_hash = a_file(db, tmp_path, **kwargs)
    return detector(rule_set(ACADEMIC, FINANCE), handling_for=POLICY)(
        db, file_id, content_hash)


# --------------------------------------------------------------------------
# the hole, and its shape
# --------------------------------------------------------------------------

def test_an_ordinary_class_reached_with_no_safety_term_says_so(db, tmp_path):
    """THE 41. A file the detector read fully, with no safety word anywhere in it.

    Two academic terms, a plausible file kind, a clean win -- and nothing about
    finance, identity, medical or legal was ever matched. The class is right. The
    confident negative that used to ride along with it is what this removes.
    """
    record = _classify(db, tmp_path, filename="Problem set 3.pdf",
                       body="Syllabus and office hours for the term.")

    assert record is not None, "an ordinary file must still be classified"
    assert record.basis == DETECTOR_NO_SAFETY_EVIDENCE


def test_the_class_and_the_flag_are_exactly_what_they_were(db, tmp_path):
    """WHAT MUST NOT MOVE. This is a basis change and nothing else.

    `96` §19's warning is that a wrong confident answer is worse than a question --
    and answering "possibly sensitive" here would be a second wrong confident answer
    pointing the other way. The file is coursework. It stays coursework, it stays
    unprotected, and it stays placeable.
    """
    record = _classify(db, tmp_path, filename="Problem set 3.pdf",
                       body="Syllabus and office hours for the term.")

    assert record.handling_class == "personal_non_sensitive"
    assert record.protected is False
    assert record.evidence_refs, "§8.4: the classification is itself evidence-backed"


def test_a_safety_work_type_in_the_evidence_keeps_the_strong_basis(db, tmp_path):
    """THE 37, and the half that proves this is not just "ordinary files are weak now".

    `96` §19 splits the 78 released files into 41 that matched no safety work type
    and 37 that matched one and were released anyway. Those 37 were EXAMINED: a
    safety term was found, weighed against where it sat, and let go. That is a
    judgement, and it keeps the strong word.

    Here the work type sits in the BODY, which `_safety_readings_naming_the_file`
    refuses as a naming zone -- the rule that stopped a chip datasheet being sealed
    on the word "will". So the file is still released, and still on `detector`.
    """
    record = _classify(
        db, tmp_path, filename="Problem set 3.pdf",
        body="Syllabus and office hours. Attach your bank statement if claiming.")

    assert record is not None and record.protected is False, (
        f"the body-prose rule stopped protecting: {record}")
    assert record.basis == DETECTOR


def test_a_context_term_alone_does_not_earn_the_strong_basis(db, tmp_path):
    """A word that SURROUNDS a financial document is not evidence about safety.

    `credit`, out of "credit hours", is the real measured case: it marked two
    university syllabi `sensitive_personal`. The work-type/context line that fixed
    that is the same line read here -- a file whose only finance word is `credit`
    was not examined for safety in any sense worth recording, so it gets the weak
    basis exactly like a file with no finance word at all.
    """
    record = _classify(
        db, tmp_path, filename="Problem set 3.pdf",
        body="Syllabus and office hours. Four credit hours this term.")

    assert record.basis == DETECTOR_NO_SAFETY_EVIDENCE


def test_a_safety_domain_that_wins_is_untouched(db, tmp_path):
    """`safety_domain` is a different claim about a different thing, and it stays.

    A file the detector reads AS a payslip is a payslip. Nothing in this change
    reaches the branch where one of `00`'s four domains wins on its own terms.
    """
    record = _classify(db, tmp_path, filename="Payslip March.pdf",
                       body="Bank statement and payslip for the period.")

    assert record is not None
    assert record.basis == "safety_domain"
    assert record.protected is True


def test_a_protection_raised_over_a_winner_is_untouched(db, tmp_path):
    """The winning-schema override still writes `safety_domain`, not the weak word.

    A file whose own FILENAME says it is a bank statement, where an ordinary schema
    happens to win on term count. `_safety_readings_naming_the_file` protects it,
    and a protection is the strongest thing this detector says -- it must never come
    back wearing the word for "nothing was found".
    """
    record = _classify(
        db, tmp_path, filename="bank statement.pdf",
        body="Syllabus, office hours, problem set and lecture notes.")

    assert record is not None and record.protected is True, (
        f"a file whose filename names a bank statement was released: {record}")
    assert record.basis == "safety_domain"


def test_a_file_with_no_terms_at_all_is_still_unclassified(db, tmp_path):
    """The locked door stays locked, and does NOT become a weak-basis release.

    `no_evidence` means nothing was recognised. Answering it with an ordinary class
    on a weak basis would be the "default to public so the pipeline can continue"
    path `privacy/classification.py` exists to refuse -- and it would put files back
    through the door this whole change closes.
    """
    record = _classify(db, tmp_path, filename="IMG_4471.pdf",
                       body="Rome, the balance of light.")

    assert record is None
