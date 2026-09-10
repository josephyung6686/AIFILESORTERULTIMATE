# tests/recognition/test_recognition_situation_outcome.py
"""`104` §18.26's owed row: ONE answer shape, so site G can read both recognisers.

**THE DEFECT.** `cli.ask_the_situation` read the recogniser's answer by asking
`isinstance` whether it was a `Recognition` or an `Abstention` -- the term
detector's two record classes. Under `--semantic-model` the object the run
classifies with is `SemanticRecogniser`, whose `explain` returns a
`SemanticProposal` or a `SemanticAbstention`, and neither is either. So on every
run with the weights named, EVERY file failed both tests, every file was counted
`settled by rule`, and the site that decides which situation a file is asked under
-- and whether it may leave the device at all -- asked nothing whatsoever. The
comment at the call site said the opposite: that the composed recogniser "is what
raises a candidate for the 60 `no_evidence` files".

**THE SHAPE.** `SituationOutcome` is what both recognisers project into: where the
recogniser got to (a reason or a schema, exactly one), the candidates it raised,
the terms and observations behind them, and -- under `by_the_rules` -- the TERM
detector's own record, which is the only thing `Detector.precaution_report` may be
asked about. A third recogniser needs no line in the pass.

**AND THE FOUR SAFETY DOMAINS STAY THE TERM DETECTOR'S ALONE** (`104` §18.11, the
constitution). `SemanticFloors`' measurement is that this path can neither protect
nor release one of `00`'s four -- a Red Cross certificate outscores an HKID -- so
it proposes none of them and puts none of them on a shortlist even as a near miss.
The only thing that raises finance, identity, medical or legal at site G is the
term detector's own hold.
"""
from __future__ import annotations

import pytest

from facts.domains import SCHEMA_IDS, UnknownSchema
from recognition.detector import (
    Abstention, Recognition, SituationOutcome, situation_outcome_of,
)
from recognition.detector import Handling
from recognition.semantic import SimilarityReading
from test_recognition_detector import (  # noqa: F401  the packaged harness
    ACADEMIC, CLOCK, FINANCE, MEDICAL, a_file, db, detector, rule_set,
    schema_entry,
)
from test_recognition_semantic import (  # noqa: F401
    BUDGET, MIN_CHARS, POLICY, ZONES, floors_default, recogniser, scores,
)

#: The floors these tests measure against, spelled once. `caution` is what a
#: safety domain must stay under for the veto to hold its tongue, `release` what a
#: leader must clear to be proposed, and `margin` how far clear of the runner-up.
#: A test may hold a policy; `cli.py` holds the shipped one.
FLOORS = dict(caution=0.30, release=0.45, margin=0.05)

#: TWO ORDINARY SCHEMAS BESIDE THE HARNESS'S ONE, because most of what this file
#: measures is what happens AWAY from `00`'s four: a tie between two ordinary
#: readings, and a proposal that is not a safety domain. The packaged harness
#: ships `academic` plus `medical` and `finance`, and two of those three are
#: safety domains the veto silences before any of this is reached.
CAREER = schema_entry("career", context=("cover letter",), work_types=("resume",))
CREATIVE = schema_entry("creative", context=("mood board",),
                        work_types=("storyboard",))

#: The handling the two of them carry: ordinary, `basis='detector'` -- exactly
#: what `cli.HANDLING_POLICY` states for the nineteen that are not `00`'s four.
ORDINARY = {**POLICY,
            "career": Handling("personal_non_sensitive", False, "detector"),
            "creative": Handling("personal_non_sensitive", False, "detector")}


def _outcome(subject, db, file_id, content_hash):
    return subject.situation_outcome(db, file_id, content_hash)


# --- the term detector's own answer, in the shape ---------------------------------


def test_an_abstention_becomes_its_reason_and_the_readings_it_raised(db, tmp_path):
    """THE PROJECTION IS THE ABSTENTION'S OWN WORDS and adds nothing to them.

    A tie raises both leaders, the reason is the recogniser's own member of
    `ABSTENTION_REASONS`, and nothing is recognised. `by_the_rules` is the record
    itself, because `precaution_report` answers about that record and about no
    projection of it.

    SABOTAGE: raise only `outcome.schema_id` in `situation_outcome_of` and drop
    the tied readings. The shortlist loses the second leader and the model is
    asked a question with one option and a way out.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "notes.pdf",
        body="Syllabus and office hours. Discharge summary and referral.")
    subject = detector(rule_set(ACADEMIC, MEDICAL))

    outcome = _outcome(subject, db, file_id, content_hash)

    assert outcome.reason == "ambiguous"
    assert outcome.recognised is None
    assert set(outcome.candidates) == {"academic", "medical"}
    assert isinstance(outcome.by_the_rules, Abstention)
    assert outcome.by_the_rules.reason == "ambiguous"
    assert outcome.evidence_refs, "the observations the readings rest on"


def test_a_recognition_becomes_the_schema_it_named_and_raises_only_that(db,
                                                                       tmp_path):
    """`00`:110 IN THE SHAPE. A direct, unique match raises itself and nothing
    else: the question on such a file -- when a hold makes it a question at all --
    is whether the HOLD is right, not what else the file might be.

    It carries NO matched terms, which is what the pass has always passed on for a
    recognised file. This projection adds no information the recogniser did not
    publish.

    SABOTAGE: set `reason=outcome.reason` on the recognition arm. `SituationQuestion`
    refuses a question that states both, and every recognised-and-held file raises.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "syllabus.pdf",
        body="Syllabus, office hours, and the problem set for week one.")
    subject = detector(rule_set(ACADEMIC))

    outcome = _outcome(subject, db, file_id, content_hash)

    assert outcome.recognised == "academic"
    assert outcome.reason is None
    assert outcome.candidates == ("academic",)
    assert outcome.matched_terms == ()
    assert isinstance(outcome.by_the_rules, Recognition)


def test_exactly_one_of_the_reason_and_the_recognised_schema_is_stated():
    """A recogniser either named the file or said why it could not, and there is no
    third thing it can have done. `SituationQuestion` holds the same invariant one
    module along, and two records that could disagree about one file is how a
    report comes to print both."""
    rules = Abstention("no_evidence", None, "nothing matched")
    with pytest.raises(ValueError):
        SituationOutcome(by_the_rules=rules, reason="no_evidence",
                         recognised="academic")
    with pytest.raises(ValueError):
        SituationOutcome(by_the_rules=rules, reason=None, recognised=None)


def test_a_candidate_from_outside_the_library_cannot_be_raised_at_all():
    """`recognition/_CONTRACT.md` rule 5 forbids inventing a class to let the
    pipeline continue, and a candidate is where such an invention would enter."""
    rules = Abstention("no_evidence", None, "nothing matched")
    with pytest.raises(UnknownSchema):
        SituationOutcome(by_the_rules=rules, reason="no_evidence",
                         recognised=None, candidates=("not_a_schema",))


def test_by_the_rules_is_the_term_detectors_record_and_nothing_else():
    """WHY THIS IS A RECORD AND NOT A PROTOCOL. `precaution_report` answers about
    the record its own author wrote; a projection handed to it, or a semantic
    answer, would be a wrapper answering for a decision it is not allowed to
    make -- and a synthesised `Abstention` whose tied readings carried semantic
    candidates would let a vector's nearest neighbour raise one of `00`'s four."""
    with pytest.raises(TypeError):
        SituationOutcome(by_the_rules="an abstention, honestly",
                         reason="no_evidence", recognised=None)


# --- the composed recogniser: the rules first, the vector only after them ---------


def test_the_term_detector_speaks_first_and_the_vector_is_not_consulted(db,
                                                                        tmp_path):
    """THE COMPOSITION, measured where the question is shaped. Where the rules
    recognised the file, the encoder is not reached at all: a similarity may add a
    reading where there was none and may never change, lower or second-guess one
    that exists.

    SABOTAGE: ask `self.explain` before the lexical outcome. The similarity below
    raises and this goes red.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "syllabus.pdf",
        body="Syllabus, office hours, and the problem set for week one.")

    def never(conn, a, b):
        raise AssertionError("the vector was consulted about a recognised file")

    subject = recogniser(never, lexical=detector(rule_set(ACADEMIC)))

    outcome = _outcome(subject, db, file_id, content_hash)

    assert outcome.recognised == "academic"
    assert isinstance(outcome.by_the_rules, Recognition)


def test_the_biggest_bucket_gains_the_candidates_the_vector_raised(db, tmp_path):
    """**THE 60 FILES.** A file carrying no term any schema authored is
    `no_evidence`: the lexical side raises nothing, `shortlist_for` returns a list
    of one, and `SituationQuestion` refuses it -- so site G could put no question
    about 60 of the owner's 112 abstentions. The composed recogniser's own
    candidates are what make them askable.

    THE REASON STAYS THE RULES'. What stopped the file is that no authored term is
    in it; the vector did not stop it, it failed to settle it. And each candidate
    carries an EMPTY term tuple, which is how the model reads that a vector raised
    it rather than a word in the file.

    SABOTAGE: drop the abstention arm's merge and return `by_the_rules`. The
    candidates are empty and the file is `nothing_to_ask` exactly as before.
    """
    file_id, content_hash = a_file(db, tmp_path, "IMG_4021.pdf",
                                   body="A photograph of a bicycle in the rain.")
    lexical = detector(rule_set(ACADEMIC, CAREER), handling_for=ORDINARY)
    assert _outcome(lexical, db, file_id, content_hash).candidates == ()

    subject = recogniser(
        scores(academic=0.50, career=0.48, medical=0.10),
        lexical=lexical, handling_for=ORDINARY, floors=floors_default(**FLOORS))

    outcome = _outcome(subject, db, file_id, content_hash)

    assert outcome.reason == "no_evidence"
    assert outcome.recognised is None
    assert set(outcome.candidates) == {"academic", "career"}
    assert outcome.matched_terms == (("academic", ()), ("career", ()))
    assert outcome.evidence_refs, (
        "a candidate raised from nothing citable is a question whose answer "
        "`privacy.classification` would refuse to write down")


def test_a_proposal_is_a_recognition_the_pass_may_settle_on(db, tmp_path):
    """A leader clear of the floor and clear of its runner-up is a RECOGNITION
    here, which is `SemanticRecogniser.__call__`'s own reading of the same
    proposal one seam along: where the rules wrote no record, the vector's is the
    record this run recorded, so the situation pass settles on it exactly as it
    settles on a term match.

    SABOTAGE: return the proposal as an abstention with the leader as a candidate.
    The file is ASKED and the run spends a local call on a file it had classified.
    """
    file_id, content_hash = a_file(db, tmp_path, "IMG_4021.pdf",
                                   body="A photograph of a bicycle in the rain.")
    subject = recogniser(scores(academic=0.90, medical=0.10),
                         lexical=detector(rule_set(ACADEMIC, MEDICAL)),
                         floors=floors_default(**FLOORS))

    outcome = _outcome(subject, db, file_id, content_hash)

    assert outcome.recognised == "academic"
    assert outcome.reason is None
    assert outcome.matched_terms == (("academic", ()),), (
        "the file matched no authored word for it, and the empty tuple is where "
        "the model reads that a vector raised the candidate")


def test_a_proposal_adds_to_the_rules_candidates_and_never_replaces_them(db,
                                                                        tmp_path):
    """TURNING THE WEIGHTS ON MAY NEVER NARROW WHAT A MODEL IS OFFERED.

    The rules read this file two ways and could not choose. A proposal that
    replaced their readings would put the file to the model as the vector's third
    schema with the rules' own readings missing from the list -- and on a HELD
    file that is the reading the person's protection turns on.

    SABOTAGE: set `candidates=(proposed,)` on the proposal arm. `academic` and
    `career` vanish from the shortlist of a file whose own words named them.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "notes.pdf",
        body="Syllabus and office hours. A cover letter and a resume for the post.")
    subject = recogniser(scores(creative=0.90, academic=0.10),
                         lexical=detector(rule_set(ACADEMIC, CAREER, CREATIVE),
                                          handling_for=ORDINARY),
                         handling_for=ORDINARY, floors=floors_default(**FLOORS))

    outcome = _outcome(subject, db, file_id, content_hash)

    assert outcome.recognised == "creative"
    assert set(outcome.candidates) == {"academic", "career", "creative"}
    assert list(outcome.candidates) == [
        schema_id for schema_id in SCHEMA_IDS if schema_id in outcome.candidates], (
        "`SCHEMA_IDS` order, so the same file puts the same question however the "
        "candidates arrived")


# --- the four safety domains stay the term detector's alone -----------------------


def test_a_proposal_can_never_name_one_of_the_four(db, tmp_path):
    """`104` §18.11 AND THE CONSTITUTION. The similarity path neither protects nor
    releases one of `00`'s four, so it may not RECOGNISE one either -- the veto in
    `explain` refuses to propose a safety leader whatever it scores.

    Measured on the domain a real corpus got wrong: a vector that is sure the file
    is medical still recognises nothing, and the file stays exactly as the term
    detector left it.

    SABOTAGE: delete the `leader in self._safety` half of the veto. The proposal
    arrives, `situation_outcome` raises rather than passing it on, and this is red
    either way -- which is the point of stating the invariant twice.
    """
    file_id, content_hash = a_file(db, tmp_path, "IMG_4021.pdf",
                                   body="A photograph of a bicycle in the rain.")
    subject = recogniser(scores(medical=0.99, academic=0.10),
                         lexical=detector(rule_set(ACADEMIC, MEDICAL)),
                         floors=floors_default(**FLOORS))

    outcome = _outcome(subject, db, file_id, content_hash)

    assert outcome.recognised is None
    assert "medical" not in outcome.candidates


def test_a_safety_domain_inside_the_margin_is_not_offered_as_a_near_miss(db,
                                                                        tmp_path):
    """THE DOOR THE VETO DOES NOT CLOSE, closed here. A safety domain can sit
    inside the margin of an ordinary leader and UNDER the caution line -- the
    vector has no opinion about it at all -- and `inside_margin` then names it in
    `tied_schema_ids` precisely because it is refusing to judge it.

    Offering a model a domain the recogniser has just said it cannot judge would
    be the guess the whole veto exists to refuse, and it would put one of `00`'s
    four on a shortlist with nothing but a vector behind it. The only thing that
    raises a safety domain at site G is the term detector's own hold.

    SABOTAGE: drop the `not in self._safety` filter from the merge. `medical`
    joins the shortlist of a file no authored medical term appears in.
    """
    file_id, content_hash = a_file(db, tmp_path, "IMG_4021.pdf",
                                   body="A photograph of a bicycle in the rain.")
    subject = recogniser(scores(academic=0.28, medical=0.27, finance=0.10),
                         lexical=detector(rule_set(ACADEMIC, MEDICAL, FINANCE)),
                         floors=floors_default(**FLOORS))

    outcome = _outcome(subject, db, file_id, content_hash)

    assert outcome.recognised is None, "under the release floor, so nothing is named"
    assert "medical" not in outcome.candidates
    assert outcome.candidates == ("academic",), (
        "the ordinary near miss is offered and the safety domain beside it is not")


def test_a_protected_container_raises_no_candidate_and_is_never_opened(db,
                                                                      tmp_path):
    """THE STANDING SECURITY RULE, through the shape. A protected container is
    marked, counted and never opened: no text of it was read, no vector of it
    exists, and no observation key of it may travel. So it raises nothing, site G
    asks nothing about it, and it lands in `nothing_to_ask` rather than in a
    dossier.

    SABOTAGE: give the `protected_container` abstention the reading's refs. Keys
    from inside a container the product promised never to open reach a dossier.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "keychain.db", body="Syllabus and office hours",
        subdirectory="Numbers.app/Contents")

    def never(conn, a, b):
        raise AssertionError("a protected container was handed to the encoder")

    from scan_agent.exclusion import is_protected_container

    subject = recogniser(never, lexical=detector(rule_set(ACADEMIC),
                                                 is_protected=is_protected_container),
                         is_protected=is_protected_container,
                         floors=floors_default(**FLOORS))

    outcome = _outcome(subject, db, file_id, content_hash)

    assert outcome.reason == "protected_container"
    assert outcome.candidates == ()
    assert outcome.evidence_refs == ()


# --- the hold's own citations (`104` §18.27) --------------------------------------


def test_a_precaution_carries_the_observations_its_terms_were_found_in(db,
                                                                      tmp_path):
    """`104` §18.27's owed row, at the source. A `Precaution` said WHICH domain,
    WHICH work types and in WHICH zones, and never which observations -- so site
    G, confirming a hold, had nothing of the hold's to cite and cited the ordinary
    schema's evidence instead.

    Every `TermMatch` already knew its `observation_key`; this is the same
    projection as `terms`, one field along, and reads the file no more than that
    one does.

    SABOTAGE: return `evidence_refs=()` from `_reported`. G's confirmed row falls
    back to the recogniser's citations and files a protected document on the
    evidence for the wrong claim.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "care plan.pdf",
        body="Care plan and referral for the patient. Syllabus.")
    subject = detector(rule_set(ACADEMIC, MEDICAL))
    outcome = subject.explain(db, file_id, content_hash)

    report = subject.precaution_report(db, outcome, file_id=file_id,
                                       content_hash=content_hash)

    assert report is not None and report.schema_id == "medical"
    assert report.terms == ("care plan",)
    assert report.evidence_refs, "the hold cites what raised the hold"
    found = {row["observation_key"] for row in db.execute(
        "SELECT observation_key, raw_value FROM evidence WHERE file_id = ? "
        "AND superseded_by IS NULL", (file_id,))
        if "care plan" in (row["raw_value"] or "").casefold()}
    assert set(report.evidence_refs) <= found, (
        "a hold cites the observations its own work types were found in, and no "
        "observation that merely sits in the same file")


def test_the_reading_a_similarity_returns_is_what_a_semantic_abstention_cites(db,
                                                                             tmp_path):
    """`00`:42 requires the answer to cite, and `privacy.classification` refuses a
    `local_model_situation` record that carries none. A near miss raised from a
    vector with no observation behind it would be a question whose answer could
    not be written down -- so the reading's own keys ride on the abstention, as
    `Abstention.evidence_refs` already ride on the term detector's.

    SABOTAGE: drop `evidence_refs=reading.evidence_refs` from the `inside_margin`
    arm. The file is asked, the model answers, and `assign` raises
    `UnbackedClassification` mid-run.
    """
    file_id, content_hash = a_file(db, tmp_path, "IMG_4021.pdf",
                                   body="A photograph of a bicycle in the rain.")
    subject = recogniser(scores(academic=0.50, career=0.48),
                         lexical=detector(rule_set(ACADEMIC, CAREER),
                                          handling_for=ORDINARY),
                         handling_for=ORDINARY, floors=floors_default(**FLOORS))

    semantic = subject.explain(db, file_id, content_hash)

    assert semantic.reason == "inside_margin"
    assert semantic.evidence_refs
    assert _outcome(subject, db, file_id,
                    content_hash).evidence_refs == semantic.evidence_refs


def test_a_reading_that_was_never_taken_cites_nothing():
    """The two abstentions that must stay empty. `no_evidence` is a file with no
    text in the configured zones and `protected_container` is a file that was
    never opened; neither has a reading, so neither has a key."""
    from recognition.semantic import SemanticAbstention

    assert SemanticAbstention("no_evidence", None, "d").evidence_refs == ()
    assert SemanticAbstention("protected_container", None, "d").evidence_refs == ()
    assert SimilarityReading(scores={}, evidence_refs=(), scope="s",
                             chars=0).evidence_refs == ()
