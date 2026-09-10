# tests/recognition/test_recognition_hold_on_a_recognition.py
"""A file the rules RECOGNISED can be held too, and the hold says why.

`104` §18.26 gap 24b. `basis='safety_domain'` has THREE writers and gap 24 gave a
report to one of them -- `_precaution`, which holds a file the detector abstained
on. The other two run on a `Recognition`:

* **the winning-schema branch.** Another schema won outright and a safety domain
  still NAMED the file -- its own work type, in one of SPEC 2.2's naming zones --
  so `_protect_as` writes the safety domain's handling over the winner's.
* **a safety domain winning outright.** The recognition IS the hold: the record
  `__call__` returns carries `SAFETY_DOMAIN_HANDLING`'s own basis.

Measured on r19 against the owner's hand labels, EIGHT of the eleven ordinary
files wrongly marked protected were of these two kinds, and none of them was ever
put to the local model: `cli.ask_the_situation` counted a recognised file
`settled` and `00`:110 sanctioned that -- "the LLM should not be called for
direct, unique matches". The owner's ruling of 10 Sep 13:10 is that `00`:110
yields to a protected hold, because a hold is not a direct unique match: it is a
word-list guess about what the file IS, taken on a term that may be the modal verb
"will" in the body of a datasheet, and the local model reads the whole text.

**THIS FILE IS ABOUT THE REPORT AND NOT ABOUT THE HOLD.** Not one rule about when
a hold is taken moved: no vocabulary, no floor, no zone test. `tests/recognition/`
passes unchanged, which is the measurement -- the 184 pins that say WHICH files
are held are exactly the pins that must not move while the detector learns to say
WHY.
"""
from __future__ import annotations

from recognition.detector import Precaution, Recognition
from test_recognition_detector import (  # the packaged harness
    ACADEMIC, FINANCE, a_file, db, detector, rule_set, schema_entry)  # noqa: F401

#: The same hand-authored safety domain `test_recognition_precaution_report` uses:
#: one work type that is also ordinary English, one that is a phrase, and context
#: terms that ACCOMPANY such a document without being it.
LEGAL = schema_entry("legal", context=("counsel", "matter"),
                     work_types=("will", "deposition transcript"))

#: Enough of `academic`'s own words to reach `never_alone`'s arity and WIN, which
#: is the whole precondition of this file: a tie would take the abstention arm and
#: measure gap 24 over again.
WINS = "The syllabus lists office hours and a problem set."


def _held(db, file_id, content_hash, rules):
    """The report and the record, from one detector, for one RECOGNISED file.

    Both, always, for `test_recognition_precaution_report`'s reason: the property
    is that they agree. The `isinstance` is an assertion and not a convenience --
    a file that quietly abstained would send every test below down the arm gap 24
    already pinned, and they would all pass while measuring nothing.
    """
    engine = detector(rules)
    outcome = engine.explain(db, file_id, content_hash)
    assert isinstance(outcome, Recognition), outcome
    report = engine.precaution_report(db, outcome, file_id=file_id,
                                      content_hash=content_hash)
    return report, engine(db, file_id, content_hash)


def test_the_winning_schema_branchs_hold_is_reported_in_its_own_terms(
        db, tmp_path):
    """WRITER TWO, given the words it held the file on.

    `academic` wins on four of its own terms. `legal`'s work type `will` is in the
    FILENAME -- one of SPEC 2.2's naming zones -- so the winning-schema branch
    protects the file anyway, and until now the record said `sensitive_personal,
    protected=1` and nothing about which domain, which word, or where.

    THE TERMS ARE THE NARROWED SET AND NOT THE WIDER ONE. This writer's rule is
    `_safety_readings_naming_the_file`; reporting what `_precaution` would have
    read on an abstention would describe a hold this branch never took.

    SABOTAGE: return `None` from `_recognised_hold`'s second arm. The record is
    unchanged -- the file is still protected -- and site G is never told why, which
    is the r19 state stated as a failure.
    """
    file_id, content_hash = a_file(db, tmp_path, "will syllabus.pdf", body=WINS)

    report, record = _held(db, file_id, content_hash, rule_set(ACADEMIC, LEGAL))

    assert isinstance(report, Precaution), report
    assert report.schema_id == "legal"
    assert report.terms == ("will",)
    assert report.zones == ("filename",)
    assert record is not None and record.protected is True
    assert record.basis == "safety_domain"


def test_a_safety_domain_that_won_outright_reports_the_recognition_itself(
        db, tmp_path):
    """WRITER THREE. The recognition IS the hold, so the report is the winner.

    `legal` wins on two of its own WORK TYPES and `__call__` returns
    `SAFETY_DOMAIN_HANDLING`'s record for it -- `basis='safety_domain'`, the same
    word the precaution writes. A file held this way is as askable as any other
    under the owner's ruling, and what it owes the model is the same three fields.

    SABOTAGE: drop the `outcome.schema_id in SAFETY_DOMAIN_IDS` arm. The file is
    still protected and site G is told nothing, and the equivalence pinned at the
    end of this file goes red as well.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "notes.pdf",
        body="The will and the deposition transcript are enclosed.")

    report, record = _held(db, file_id, content_hash, rule_set(ACADEMIC, LEGAL))

    assert isinstance(report, Precaution), report
    assert report.schema_id == "legal"
    assert set(report.terms) == {"will", "deposition transcript"}
    assert report.zones == ("body",)
    assert record is not None and record.protected is True
    assert record.basis == "safety_domain"


def test_a_domain_that_won_on_context_terms_alone_names_no_work_type(
        db, tmp_path):
    """AND IT IS STILL A HOLD, which is the half that must not be tidied away.

    `finance` wins on `account statement` and `referral`, both of them CONTEXT
    terms -- words that accompany a financial document without being one -- and
    the record is `protected=1, basis='safety_domain'` all the same, because the
    domain won the recognition on its own words. `Precaution.terms` is "the work
    types of that domain the file's evidence carries" and there are none, so the
    report names the domain and nothing else rather than calling a context term a
    work type.

    EMPTY AND NOT `None`. A `None` here would be a live `safety_domain` row that
    `cli.ask_the_situation` counts as no hold at all -- the file would go back to
    `settled`, unasked and protected, which is exactly the r19 defect this gap is
    closing.

    SABOTAGE: return `None` when the work types come back empty. This goes red and
    so does the equivalence at the end of the file.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "notes.pdf",
        body="The account statement and the referral are enclosed.")

    report, record = _held(db, file_id, content_hash, rule_set(ACADEMIC, FINANCE))

    assert isinstance(report, Precaution), report
    assert report.schema_id == "finance"
    assert report.terms == ()
    assert report.zones == ()
    assert record is not None and record.protected is True
    assert record.basis == "safety_domain"


def test_a_work_type_in_body_prose_holds_nothing_where_a_schema_won(
        db, tmp_path):
    """THE ZONE RULE DID NOT MOVE, pinned from the other side.

    `will` in BODY prose is what locked an Arduino `LICENSE.txt` and a 642-page
    datasheet on the owner's real corpus, and `_safety_readings_naming_the_file`
    is the measured answer to it: on the path where a schema WON, the work type
    must sit where a document names itself. That rule is this branch's and gap 24b
    reads it rather than rewriting it -- the report is silent because the hold was
    never taken, and the file stays ordinary.

    SABOTAGE: report the lenient reading -- any safety work type anywhere -- and
    this file is held on the word "will" in a sentence about a deadline.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "notes.pdf",
        body=WINS + " The will is attached for the estate matter.")

    report, record = _held(db, file_id, content_hash, rule_set(ACADEMIC, LEGAL))

    assert report is None
    assert record is not None and record.protected is False
    assert record.basis != "safety_domain"


def test_the_report_and_the_record_answer_together_on_a_recognition_too(
        db, tmp_path):
    """ONE RULE, TWO READERS -- `test_recognition_precaution_report`'s last test,
    asked of the arm gap 24b added.

    `cli.ask_the_situation` reads the LIVE row's basis and then asks
    `precaution_report`; a file whose row says `safety_domain` and whose report is
    silent is a hold no screen counts and no model is asked about, and a report
    with no row behind it is a screen inventing a lock. `__call__` writes the
    record THROUGH this report on the winning-schema arm, so the agreement is by
    construction on that one -- this is what says it holds on all of them.

    Four files across both answers, so neither a report that always answers nor
    one that never does can pass.

    SABOTAGE: give `_recognised_hold` its own copy of the naming-zone test, then
    change one of them.
    """
    rules = rule_set(ACADEMIC, LEGAL)
    corpus = {
        "will syllabus.pdf": WINS,
        "estate.pdf": "The will and the deposition transcript are enclosed.",
        "notes.pdf": WINS + " The will is attached for the estate matter.",
        "plain syllabus.pdf": WINS,
    }
    for name, body in corpus.items():
        file_id, content_hash = a_file(db, tmp_path / name.replace(".", "_"),
                                       name, body=body)
        report, record = _held(db, file_id, content_hash, rules)
        held_by_the_record = record is not None and record.basis == "safety_domain"
        assert (report is not None) == held_by_the_record, (name, report, record)
        # And the record's own flag agrees with its basis, which is what makes
        # the row a HOLD rather than a class that happens to share a word.
        assert held_by_the_record == bool(record is not None and record.protected)
