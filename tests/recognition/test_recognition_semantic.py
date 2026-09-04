"""Recognition by MEANING, and the four rules that keep it from releasing a file.

The detector matches authored terms literally. Measured over the owner's own 199
files it classified 37 of them, and the reason is not that the library is thin:
8,429 authored terms, of which 38.9% are prose an authoring note left behind --
"proposal note: none of these terms appears in 00...". No file can ever carry
those as a string, and they are the richest description in the library. The
matching method throws away exactly the part that says the most.

So this path embeds the file's own evidence and the library's own terms and takes
a nearest neighbour. Everything that decides -- the floors, the margin, the model,
the zones, the budget -- is INJECTED, because a similarity threshold is a policy
and this package authors none.

Four rules, each with its negative twin, because a similarity path can release a
file that the term path was holding shut:

**PROTECTION IS A UNION, NEVER A REPLACEMENT.** The term detector runs first and
its answer is returned untouched. This path is reached only where that one said
nothing, so no protection it raises can be lowered by a vector.

**A SAFETY DOMAIN IS NEVER CLAIMED, IN EITHER DIRECTION.** A protect floor was
written here first and then measured away. Over the 199-file ground-truth corpus
the eight hand-labelled protected files score 0.084 to 0.151 against the safety
centroids and sit at the 43rd to 90th percentiles of the corpus -- two below the
median -- while the highest safety score of all 199 belongs to a Red Cross
first-aid certificate and a `LICENSE` file outranks the owner's real HKID. So the
vector neither protects nor releases one of `00`'s four domains: it abstains and
leaves the file exactly as the term detector left it.

**A VECTOR OVER A FILENAME IS ONE SIGNAL.** `never_alone`, in the form a vector
can state it. The only two protected files this path ever claimed as ordinary
carry 22 and 84 characters of their own text, and mean pooling makes a vector over
22 characters look exactly as confident as a vector over four pages.

**A PROTECTED CONTAINER IS MARKED AND COUNTED, NEVER OPENED.** Checked before any
evidence is read and before the encoder is reached, on P3's own predicate.

**THE ABSOLUTE PATH IS NOT ONE OF THE FILE'S OWN WORDS.** `_matches` learned this
by running the product: `IMG_4471.jpg`, an ordinary photograph, in a folder called
`Passport and Visa Documents`, came back `sensitive_personal`. A vector over the
same string would do the same thing more quietly, so the same refusal is applied
here, to the same evidence rows, by the same test.
"""
from __future__ import annotations

import json

import pytest

from database_agent.files_table import get_file
from facts.domains import UnknownSchema
from privacy.classification import ClassificationRecord
from recognition.detector import Handling, SAFETY_DOMAIN_HANDLING
from recognition.semantic import (
    FLOAT32_LE, SEMANTIC_ABSTENTION_REASONS, SemanticAbstention, SemanticFloors,
    SemanticProposal, SemanticRecogniser, SimilarityReading, VetoUnreachable,
    build_schema_anchors, embedding_text_for, evidence_text, schema_similarity_from,
    scope_for,
)
from recognition.vocabulary import ABSTENTION_REASONS, UnknownAbstentionReason
from test_recognition_detector import (  # noqa: F401  the packaged harness
    ACADEMIC, CLOCK, a_file, db, rule_set,
)

#: The zones a deployment would read, in SPEC 2.2's own ranking: where a document
#: names itself first, so a truncation keeps the identifying half. Spelled here
#: because a TEST may hold a policy -- `cli.py` holds the shipped one.
ZONES = ("filename", "title", "heading", "header_footer", "body", "table", "ocr")
BUDGET = 4_000

POLICY = {**SAFETY_DOMAIN_HANDLING,
          "academic": Handling("personal_non_sensitive", False, "detector")}

MIN_CHARS = 100


def floors_default(caution=0.30, release=0.45, margin=0.05):
    """The floors, built INSIDE a call and never at module scope.

    A module-scope `SemanticFloors(...)` turns a signature change into a
    COLLECTION error, and pytest then aborts the whole run before executing a
    single test -- so one stale keyword in this file takes down every other
    agent's ability to verify anything. That happened: `protect=` outlived its
    rename to `caution=` by a few minutes and `tests/` would not collect.

    Behind a function, the identical mistake fails the tests that call it and
    leaves the suite runnable. The cost of the rule is one pair of parentheses.
    """
    return SemanticFloors(caution=caution, release=release, margin=margin)

#: A P4 observation key's real shape. `privacy.classification` refuses any
#: other, on M14: "the key, not the id, is what makes that durable".
OBSERVATION_KEY = "sha256:" + "a1" * 32


def silent(conn, file_id, content_hash):
    """A term detector that found nothing. The door this path exists behind."""
    return None


def scores(_chars=1000, **by_schema):
    """A similarity function that returns what the test says, and cites one row."""

    def similarity(conn, file_id, content_hash):
        return SimilarityReading(scores=dict(by_schema),
                                 evidence_refs=(OBSERVATION_KEY,),
                                 scope=scope_for(ZONES, BUDGET), chars=_chars)

    return similarity


def recogniser(similarity, *, lexical=silent, floors=None, handling_for=None,
               is_protected=None, min_chars=MIN_CHARS):
    return SemanticRecogniser(
        lexical=lexical, schema_similarity=similarity,
        floors=floors if floors is not None else floors_default(),
        handling_for=POLICY if handling_for is None else handling_for,
        is_protected=is_protected, now=lambda: CLOCK, min_chars=min_chars)


# --- the standing security rule, checked before anything is read ----------------

def test_a_protected_container_is_never_opened_and_never_encoded(db, tmp_path):
    """P3's refusal, and the encoder must not even be reached.

    The detector checks this first "because a detector's natural instinct is to
    open a file to classify it". A similarity path's instinct is worse: it wants
    the whole document, not a term, so the cost of getting this wrong is the whole
    document rather than a word of it.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "keychain.db", body="Passport number X12345678",
        subdirectory="Numbers.app/Contents")
    reached = []

    def similarity(conn, a, b):
        reached.append(a)
        raise AssertionError("a protected container was handed to the encoder")

    subject = recogniser(similarity)
    outcome = subject.explain(db, file_id, content_hash)
    assert isinstance(outcome, SemanticAbstention)
    assert outcome.reason == "protected_container"
    assert subject(db, file_id, content_hash) is None
    assert reached == []


def test_the_deployments_own_protected_predicate_is_consulted(db, tmp_path):
    """`is_protected` is P3's injected extra, and this path honours it too."""
    file_id, content_hash = a_file(db, tmp_path, "notes.pdf", body="anything")
    subject = recogniser(scores(academic=0.99), is_protected=lambda path: True)
    outcome = subject.explain(db, file_id, content_hash)
    assert isinstance(outcome, SemanticAbstention)
    assert outcome.reason == "protected_container"


def test_the_absolute_path_is_not_one_of_the_files_own_words(db, tmp_path):
    """A folder called `Passport and Visa Documents` describes no file inside it.

    `_matches` refuses P4's `path` locator for exactly this, after an ordinary
    photograph in such a folder came back `sensitive_personal, protected=True`. A
    vector over the same string would reach the same answer without leaving a term
    behind to explain it.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "IMG_4471.jpg", body="Rome, the balance of light",
        abspath="/Users/someone/Passport and Visa Documents/IMG_4471.jpg")
    text, refs = evidence_text(db, file_id, content_hash,
                               zones=ZONES, char_budget=BUDGET)
    assert "Passport" not in text
    assert "Rome, the balance of light" in text
    assert refs


def test_the_refusal_is_on_the_locator_and_not_only_on_the_zone(db, tmp_path):
    """Two doors, and this is the inner one.

    The zone list closes the outer door: `scope_for` refuses `path` outright, so a
    caller cannot ask for it. That is the door the test above walks into, and on
    the shipped writer it is the only one -- P4 gives a path observation the `path`
    zone AND the `path` locator, so either check alone excludes it.

    They are not the same check, and this asserts the one `detector._matches`
    actually makes. Written by moving a readable row onto the path locator, which
    the shipped writer never does, because a guard that cannot be reached through
    the writer is still the guard the next writer will be measured against. Its
    first version was satisfied by the zone filter alone and stayed green when the
    locator branch was deleted.
    """
    file_id, content_hash = a_file(db, tmp_path, "notes.pdf",
                                   body="the ordinary body prose")
    template = db.execute(
        "SELECT * FROM evidence WHERE file_id = ? AND raw_value = ?",
        (file_id, "the ordinary body prose")).fetchone()
    moved = {**json.loads(template["location"]), "locator": "path"}
    assert moved["zone"] == "body"          # still a zone the caller asked for
    columns = [name for name in template.keys() if name != "record_id"]
    values = [template[name] for name in columns]
    values[columns.index("observation_id")] = "moved-onto-the-path-locator"
    values[columns.index("observation_key")] = "sha256:" + "b2" * 32
    values[columns.index("raw_value")] = "Passport and Visa Documents"
    values[columns.index("location")] = json.dumps(moved)
    # INSERTED rather than updated: `evidence_never_overwritten` refuses an update
    # outright -- "a better extractor emits a new observation and a new run (§8.2)"
    # -- which is P4's own append-only rule and not something to work around.
    db.execute(f"INSERT INTO evidence ({', '.join(columns)}) VALUES "
               f"({', '.join('?' * len(columns))})", values)

    text, refs = evidence_text(db, file_id, content_hash, zones=ZONES,
                               char_budget=BUDGET)
    assert "the ordinary body prose" in text
    assert "Passport" not in text
    assert "sha256:" + "b2" * 32 not in refs


def test_a_zone_list_may_not_name_the_path(db):
    """The refusal is stated where the policy is stated, as well as where it runs."""
    with pytest.raises(ValueError, match="path"):
        scope_for(("filename", "path"), BUDGET)


# --- the floors, which are the over-release guard --------------------------------

def test_a_caution_veto_that_can_never_fire_is_refused():
    """A veto at the maximum cosine is an over-release wearing a number.

    The guard is on the PAIR: neither a caution of 1.0 nor a release floor is
    wrong alone, and together they are a recogniser that claims files with the
    safety check switched off.
    """
    with pytest.raises(VetoUnreachable):
        SemanticFloors(caution=1.0, release=0.40, margin=0.05)


def test_a_floor_outside_the_similarity_range_is_refused():
    with pytest.raises(ValueError):
        SemanticFloors(caution=-0.1, release=0.4, margin=0.05)
    with pytest.raises(ValueError):
        SemanticFloors(caution=0.3, release=1.4, margin=0.05)
    with pytest.raises(ValueError):
        SemanticFloors(caution=0.3, release=0.4, margin=-0.01)


def test_a_safety_domain_that_leads_is_neither_protected_nor_released(
        db, tmp_path):
    """The measured rule. A Red Cross certificate outscores an HKID here.

    Neither direction is available to this path: it does not protect the file,
    because the floor that catches the corpus's eight protected files protects
    half the disk; and it does not file it as ordinary, because that would hand a
    payslip to the placement stage. It abstains, and the file keeps whatever the
    term detector gave it.
    """
    file_id, content_hash = a_file(db, tmp_path, "doc.pdf", body="anything")
    subject = recogniser(scores(finance=0.80, academic=0.35))
    outcome = subject.explain(db, file_id, content_hash)
    assert isinstance(outcome, SemanticAbstention)
    assert outcome.reason == "safety_domain_uncertain"
    assert outcome.schema_id == "finance"
    assert subject(db, file_id, content_hash) is None


def test_a_safety_domain_LEADING_below_the_caution_line_still_silences_the_path(
        db, tmp_path):
    """The two doors separate, and this is the one that needed its own case.

    The shipped floors put the caution line ABOVE the release floor -- measured,
    0.137 against 0.10 -- so a safety domain can lead a file, clear the release
    floor, and still sit under the caution line. Deleting the leader half of the
    veto then releases it as `sensitive_personal, protected=False`, and the first
    version of this file could not tell: both of its safety cases scored high
    enough for the near-miss door to catch them, so the leader door was never the
    thing being tested.
    """
    file_id, content_hash = a_file(db, tmp_path, "doc.pdf", body="anything")
    tight = floors_default(caution=0.137, release=0.10, margin=0.01)
    subject = recogniser(scores(finance=0.12, academic=0.02), floors=tight)
    outcome = subject.explain(db, file_id, content_hash)
    assert outcome.safety_similarity if isinstance(outcome, SemanticProposal) else True
    assert isinstance(outcome, SemanticAbstention)
    assert outcome.reason == "safety_domain_uncertain"
    assert outcome.schema_id == "finance"
    assert subject(db, file_id, content_hash) is None
    # and the twin: an ORDINARY leader at the same similarity is claimed.
    ordinary = recogniser(scores(academic=0.12, creative=0.02), floors=tight)
    assert ordinary(db, file_id, content_hash) is not None


def test_a_safety_domain_merely_NEAR_the_caution_line_also_silences_the_path(
        db, tmp_path):
    """The second door. `academic` leads outright and still nothing is claimed."""
    file_id, content_hash = a_file(db, tmp_path, "doc.pdf", body="anything")
    subject = recogniser(scores(academic=0.80, finance=0.31))
    outcome = subject.explain(db, file_id, content_hash)
    assert isinstance(outcome, SemanticAbstention)
    assert outcome.reason == "safety_domain_uncertain"
    assert subject(db, file_id, content_hash) is None


def test_a_safety_domain_below_the_caution_line_does_not_silence_it(db, tmp_path):
    """The negative twin. Otherwise the guard above is satisfied by everything."""
    file_id, content_hash = a_file(db, tmp_path, "doc.pdf", body="anything")
    subject = recogniser(scores(academic=0.80, finance=0.29))
    outcome = subject.explain(db, file_id, content_hash)
    assert isinstance(outcome, SemanticProposal)
    assert outcome.schema_id == "academic"
    assert outcome.safety_similarity == 0.29
    assert subject(db, file_id, content_hash).protected is False


def test_a_file_with_too_little_text_of_its_own_is_never_claimed(db, tmp_path):
    """`never_alone` in the form a vector can state it.

    Mean pooling hides how much was pooled: a vector over 22 characters has the
    same shape and the same magnitude as a vector over four pages. The two
    protected files this path ever released carry 22 and 84 characters.
    """
    file_id, content_hash = a_file(db, tmp_path, "doc.pdf", body="anything")
    subject = recogniser(scores(_chars=99, academic=0.99, creative=0.01))
    outcome = subject.explain(db, file_id, content_hash)
    assert isinstance(outcome, SemanticAbstention)
    assert outcome.reason == "too_little_text"
    assert subject(db, file_id, content_hash) is None
    enough = recogniser(scores(_chars=100, academic=0.99, creative=0.01))
    assert enough(db, file_id, content_hash) is not None


def test_an_ordinary_schema_below_the_release_floor_claims_nothing(db, tmp_path):
    file_id, content_hash = a_file(db, tmp_path, "doc.pdf", body="anything")
    subject = recogniser(scores(academic=0.44, creative=0.10))
    outcome = subject.explain(db, file_id, content_hash)
    assert isinstance(outcome, SemanticAbstention)
    assert outcome.reason == "below_similarity_floor"
    assert outcome.schema_id == "academic"
    assert subject(db, file_id, content_hash) is None


def test_an_ordinary_schema_inside_the_margin_claims_nothing(db, tmp_path):
    """`00` requires abstention where two readings are both supported.

    The detector breaks a tie with nothing at all. A vector never ties exactly, so
    the same rule has to be stated as a distance -- and the distance is the
    caller's, never this module's.
    """
    file_id, content_hash = a_file(db, tmp_path, "doc.pdf", body="anything")
    subject = recogniser(scores(academic=0.60, creative=0.57))
    outcome = subject.explain(db, file_id, content_hash)
    assert isinstance(outcome, SemanticAbstention)
    assert outcome.reason == "inside_margin"
    assert outcome.tied_schema_ids == ("academic", "creative")
    assert subject(db, file_id, content_hash) is None


def test_an_ordinary_schema_clear_of_both_is_proposed(db, tmp_path):
    file_id, content_hash = a_file(db, tmp_path, "doc.pdf", body="anything")
    subject = recogniser(scores(academic=0.62, creative=0.40))
    record = subject(db, file_id, content_hash)
    assert isinstance(record, ClassificationRecord)
    assert record.handling_class == "personal_non_sensitive"
    assert record.protected is False
    assert record.reliability_state == "possible"
    assert record.evidence_refs == (OBSERVATION_KEY,)


# --- protection is a union, never a replacement ---------------------------------

def test_a_term_detectors_answer_is_returned_untouched(db, tmp_path):
    """The whole of the over-release guard, in one line of composition.

    If the term detector spoke, this path never runs -- so a similarity can add a
    classification where there was none and can never change one that exists.
    """
    file_id, content_hash = a_file(db, tmp_path, "doc.pdf", body="anything")
    locked = ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="sensitive_personal", protected=True,
        basis="safety_domain", evidence_refs=(OBSERVATION_KEY,),
        reliability_state="possible", observed_at=CLOCK)
    reached = []

    def similarity(conn, a, b):
        reached.append(a)
        raise AssertionError("the similarity path ran after the detector spoke")

    subject = recogniser(similarity, lexical=lambda *a: locked)
    assert subject(db, file_id, content_hash) is locked
    assert reached == []


def test_an_ordinary_term_classification_is_also_left_alone(db, tmp_path):
    """Not only the protected ones: this path never SECOND-GUESSES the detector."""
    file_id, content_hash = a_file(db, tmp_path, "doc.pdf", body="anything")
    ordinary = ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="personal_non_sensitive", protected=False,
        basis="detector", evidence_refs=(OBSERVATION_KEY,),
        reliability_state="possible", observed_at=CLOCK)
    subject = recogniser(scores(creative=0.99), lexical=lambda *a: ordinary)
    assert subject(db, file_id, content_hash) is ordinary


# --- recognition is not classification ------------------------------------------

def test_a_schema_the_policy_states_no_class_for_is_recognised_and_not_classified(
        db, tmp_path):
    """`_CONTRACT.md` rule 5, unchanged by the method that reached the schema."""
    file_id, content_hash = a_file(db, tmp_path, "doc.pdf", body="anything")
    subject = recogniser(scores(creative=0.90, academic=0.10),
                         handling_for={"academic": POLICY["academic"]})
    outcome = subject.explain(db, file_id, content_hash)
    assert isinstance(outcome, SemanticProposal)
    assert outcome.schema_id == "creative"
    assert subject(db, file_id, content_hash) is None


def test_a_score_for_a_schema_the_product_does_not_recognise_is_refused(
        db, tmp_path):
    """The encoder is injected, so its labels are checked rather than trusted."""
    file_id, content_hash = a_file(db, tmp_path, "doc.pdf", body="anything")
    subject = recogniser(scores(**{"not_a_schema": 0.9}))
    with pytest.raises(UnknownSchema):
        subject.explain(db, file_id, content_hash)


def test_a_file_whose_evidence_carries_no_text_is_not_classified(db, tmp_path):
    file_id, content_hash = a_file(db, tmp_path, "doc.pdf", body="anything")
    subject = recogniser(lambda conn, a, b: None)
    outcome = subject.explain(db, file_id, content_hash)
    assert isinstance(outcome, SemanticAbstention)
    assert outcome.reason == "no_evidence"
    assert subject(db, file_id, content_hash) is None


# --- nothing is defaulted -------------------------------------------------------

def test_every_authority_is_required(db):
    with pytest.raises(TypeError):
        SemanticRecogniser(lexical=silent, schema_similarity=scores(academic=1.0),
                           floors=floors_default(), handling_for=POLICY, now="not a clock",
                           min_chars=MIN_CHARS)
    with pytest.raises(TypeError):
        SemanticRecogniser(lexical=silent, schema_similarity="not callable",
                           floors=floors_default(), handling_for=POLICY, now=lambda: CLOCK,
                           min_chars=MIN_CHARS)
    with pytest.raises(TypeError):
        SemanticRecogniser(lexical=silent, schema_similarity=scores(academic=1.0),
                           floors=(0.3, 0.4, 0.05), handling_for=POLICY,
                           now=lambda: CLOCK, min_chars=MIN_CHARS)
    with pytest.raises(TypeError):
        SemanticRecogniser(lexical=silent, schema_similarity=scores(academic=1.0),
                           floors=floors_default(), handling_for=POLICY, now=lambda: CLOCK)
    with pytest.raises(ValueError):
        SemanticRecogniser(lexical=silent, schema_similarity=scores(academic=1.0),
                           floors=floors_default(), handling_for=POLICY, now=lambda: CLOCK,
                           min_chars=0)


def test_the_abstention_reasons_extend_the_packages_own_and_never_restate_them():
    """One vocabulary, widened. Two vocabularies holding one meaning is the
    defect this project names most often, so the reasons the detector already
    publishes are IMPORTED, and only the two a similarity can reach are added."""
    assert set(ABSTENTION_REASONS) < set(SEMANTIC_ABSTENTION_REASONS)
    assert set(SEMANTIC_ABSTENTION_REASONS) - set(ABSTENTION_REASONS) == {
        "below_similarity_floor", "inside_margin", "too_little_text",
        "safety_domain_uncertain"}
    with pytest.raises(UnknownAbstentionReason):
        SemanticAbstention("no_such_reason", None, "")


# --- the scope, which is part of what a vector MEANS ----------------------------

def test_the_scope_names_the_zones_and_the_budget_it_was_read_under():
    """P9: "a silent default would make two vectors incomparable while looking
    identical". The zones and the budget ARE the scope, so they cannot drift
    apart from the name a vector is filed under."""
    assert scope_for(ZONES, BUDGET) != scope_for(ZONES[:2], BUDGET)
    assert scope_for(ZONES, BUDGET) != scope_for(ZONES, BUDGET * 2)
    assert scope_for(ZONES, BUDGET) == scope_for(ZONES, BUDGET)


def test_the_p9_text_seam_refuses_a_scope_it_did_not_compute(db, tmp_path):
    file_id, content_hash = a_file(db, tmp_path, "doc.pdf", body="anything")
    reader = embedding_text_for(ZONES, BUDGET)
    assert reader(db, file_id, content_hash, scope_for(ZONES, BUDGET))
    with pytest.raises(ValueError, match="scope"):
        reader(db, file_id, content_hash, "some.other.scope")


def test_the_naming_zones_are_read_before_the_body(db, tmp_path):
    """A truncation must keep the half that says what the file IS.

    SPEC 2.2 ranks "a filename, title, or page-one heading" and the budget is
    finite, so the order the zones are given in is the order they are spent in.
    """
    file_id, content_hash = a_file(
        db, tmp_path, "syllabus.pdf", body="x" * 5_000, heading="Course outline")
    text, _ = evidence_text(db, file_id, content_hash, zones=ZONES,
                            char_budget=200)
    assert "syllabus.pdf" in text
    assert "Course outline" in text
    assert len(text) <= 200


def test_a_zone_the_policy_did_not_name_is_not_read(db, tmp_path):
    file_id, content_hash = a_file(
        db, tmp_path, "doc.pdf", body="the body prose",
        metadata_field=("Producer", "Quartz PDFContext"))
    text, _ = evidence_text(db, file_id, content_hash, zones=("filename", "body"),
                            char_budget=BUDGET)
    assert "Quartz" not in text
    assert "the body prose" in text


# --- the anchors are the library's, not this module's ---------------------------

def test_the_anchors_are_the_authored_terms_and_this_module_writes_none():
    """The 8,429 terms are the owner's research. This turns them into anchors and
    invents not one of them -- which is the whole claim of the approach: the
    library was never wrong, the matching was."""
    rules = rule_set(ACADEMIC)
    anchors = build_schema_anchors(rules, max_words=None)
    assert set(anchors) == {"academic"}
    assert set(anchors["academic"]) == {"syllabus", "office hours", "problem set"}


def test_the_word_cap_drops_the_authoring_prose_and_keeps_the_terms():
    """13.5% of the compiled terms are notes ABOUT the research, not about a
    document -- one is a 77-word aside beginning "proposed for r6, not design".
    They were expected to be the richest anchors and measured as the worst:
    dropping them moves top-1 schema accuracy from 29.1% to 32.2%."""
    rules = rule_set({**ACADEMIC, "context_terms": [
        "syllabus", "proposal note: none of these terms appears in 00 and each "
        "is offered as a candidate for a later round"]})
    assert build_schema_anchors(rules, max_words=6)["academic"] == (
        "syllabus", "problem set")
    assert len(build_schema_anchors(rules, max_words=None)["academic"]) == 3


def test_a_schema_that_authored_no_term_gets_no_anchor():
    """An empty anchor set would be a point at the origin that everything is
    equally near, which is a schema that matches every file."""
    rules = rule_set(ACADEMIC, {**ACADEMIC, "schema_id": "creative",
                                "context_terms": [], "work_type_terms": []})
    anchors = build_schema_anchors(rules, max_words=None)
    assert "creative" not in anchors


# --- the P9 seam, which was built and connected to nothing ----------------------

def test_the_vector_is_stored_as_a_p1_record_and_reused_rather_than_recomputed(
        db, tmp_path):
    """`grouping/embeddings.py` was written, tested and called by nobody.

    This is the assignment it was waiting for. The document vector goes through
    `ensure_file_embedding`, so it is a versioned record keyed on the FILE VERSION
    -- P9's rule that "a vector belongs to a file version" -- rather than a number
    computed twice and stored nowhere. Measured on a real run: `vector_embeddings`
    holds 0 rows before and 109 after.

    The second half is what stops the encoder running twice per file: an identity
    that already has a vector is READ BACK, which is the only path
    `decode_vector` is ever on.
    """
    from grouping.embeddings import EmbeddingConfig
    from database_agent.vector_versions import current_embedding

    file_id, content_hash = a_file(db, tmp_path, "notes.pdf",
                                   body="a page of ordinary prose about a course")
    scope = scope_for(ZONES, BUDGET)
    config = EmbeddingConfig(model_id="test/encoder", model_version="v1@256tok",
                             scope=scope, encoding=FLOAT32_LE, dimension=3)
    encoded = []

    def encode(text):
        encoded.append(text)
        return (0.5, 0.5, 0.5)

    seen = []
    similarity = schema_similarity_from(
        anchor_scores=lambda vector: seen.append(tuple(vector)) or {"academic": 0.9},
        config=config, encode=encode, zones=ZONES, char_budget=BUDGET,
        now=lambda: CLOCK)

    reading = similarity(db, file_id, content_hash)
    assert reading.scores == {"academic": 0.9}
    assert reading.scope == scope
    assert reading.chars > 0 and reading.evidence_refs
    stored = current_embedding(db, file_id=file_id, content_hash=content_hash,
                               scope=scope, embedding_model_id="test/encoder",
                               embedding_version="v1@256tok")
    assert stored is not None
    assert stored.dimension == 3 and stored.encoding == FLOAT32_LE
    assert len(stored.array_bytes) == 12          # three float32

    # Called again on the same file version: P1 already holds the vector, so the
    # encoder is not run and the stored bytes are decoded instead.
    again = similarity(db, file_id, content_hash)
    assert len(encoded) == 1
    assert seen[1] == pytest.approx(seen[0])
    assert again.scores == reading.scores


def test_a_config_whose_scope_is_not_the_one_assembled_is_refused(db):
    """P9 files a vector under the scope it is handed, so the two must agree."""
    from grouping.embeddings import EmbeddingConfig

    with pytest.raises(ValueError, match="scope"):
        schema_similarity_from(
            anchor_scores=lambda v: {}, encode=lambda t: (0.0,),
            config=EmbeddingConfig(model_id="m", model_version="v",
                                   scope="something.else", encoding=FLOAT32_LE,
                                   dimension=1),
            zones=ZONES, char_budget=BUDGET, now=lambda: CLOCK)


def test_a_codec_this_reader_does_not_implement_is_refused_never_sniffed(db):
    """P1 stores opaque bytes and publishes no codec. Something has to read one
    back, and the honest form of that is to name the one codec implemented and
    refuse the rest -- guessing from a byte length is how a 5-dimension vector
    gets filed under a 3-dimension identity and noticed months later."""
    from recognition.semantic import decode_vector

    assert decode_vector(b"\x00\x00\x80\x3f", FLOAT32_LE, 1) == (1.0,)
    with pytest.raises(ValueError, match="float32-le"):
        decode_vector(b"\x00" * 8, "float64-le", 1)
    with pytest.raises(ValueError, match="floats"):
        decode_vector(b"\x00\x00\x80\x3f", FLOAT32_LE, 3)
