# tests/p8/test_p8_subject_title_to_review.py
"""R-98: a course that names itself with words, not a code, reaches the person.

**The measurement.** On the owner's pinned corpus, cloud, site A was asked 83 times.
Of the 23 files that are genuinely coursework the model answered `subject` ten times
and ALL TEN were refused `VALUE_NOT_NORMALIZABLE`: every one was a course TITLE of one
to six words and `cli.SUBJECT_RULE.pattern` requires a code-shaped identifier. `105`
§1.5 records the same thing from the bench side as gap G15 -- *"no title-named course
can be filed and the glossary's `(code or title)` cannot be measured through
acceptance"* -- and `104` §11.2 step 1 says `subject` means *"the course as the course
names itself (code or title)"*.

**The ruling this file implements.** `104` §13.5 (Q-A): a rule may reject only a
STRUCTURALLY INVALID answer. §13.7 (Q-C): the model names and the user confirms -- *"a
value the library has not seen is proposed once; the user confirms or renames it"*. A
title is not structurally invalid; it is unverifiable, and `00`:42 says what happens to
an unverifiable model answer: it *"may remain a possible clue for review; it must not
quietly become a folder proposal or an asserted file property"*.

**So there are two normalisers and they answer two different questions.**
`cli.normalize_for_model` is unchanged and still answers "is this the identifier the
deterministic rule reads", which is what `accept_direct` rests on;
`cli.normalize_for_review` answers "is this a title a person could confirm", and its
answer reaches P6 as `possible` -- below `facts.read_surface.PROPOSAL_ELIGIBLE_STATES`,
so it is a candidate and never a folder until somebody says yes. The deterministic
`subject` rule is untouched, which is why every value
`tests/p6/test_p6_subject_slot.py` measured off a real disk is still refused here.

**`work_type` AND `term` JOINED `subject` HERE ON 2026-09-09 (`104` §18.2 gap 3).**
The scope line this file used to draw -- "only `subject` has a review normaliser
today" -- was the other half of G15 left standing, and `104` measured what it cost:
`VALUE_NOT_NORMALIZABLE` was r15's LARGEST rejection class and those two fields were
most of it. `00`:298 covers all three by name. The closed sets in code did not go
away; they became the seed the review path starts from, which is what `00`:298 means
by "the ratified library is the vocabulary the model is shown first".
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

import pytest

from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_observation, record_run
from facts.domains import ActivationSignal, ActivationSignals
from facts.fields import create_fields
from facts.file_facts import (
    DETERMINISTIC_EXTRACTOR, USER_CORRECTION, facts_for_file, write_fact,
)
from facts.llm_seam import build_request
from facts.read_surface import PROPOSAL_ELIGIBLE_STATES
from facts.states import LLM_SUPPORTED, POSSIBLE, USER_CONFIRMED, VALIDATED
from facts.values import (
    VALUE_ORIGINS, ensure_value, merge_values, values_in_field,
)
from llm_harness.fact_validation import FactValidationDependencies
from llm_harness.fixtures import FIXTURE_HANDLE_KEY
from llm_harness.records import Dossier, EvidenceItem, ReleasedEvidence
from llm_harness.schema import create_llm_schema
from llm_harness.sites import FactSiteDependencies, SiteDependencies, dispatch
from llm_harness.vocabulary import (
    ABSTAIN,
    A_FACT,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    CONTEXT_SUPPORTED,
    CONTRADICTED_BY_STRONGER,
    DIRECT_ANCHOR,
    LLM_SUPPORTED_REVIEW,
    REDUCTION_NONE,
    REJECT,
    REMAINS_AMBIGUOUS,
    VALUE_NOT_IN_CITED_TEXT,
    VALUE_NOT_NORMALIZABLE,
)

import cli
from cli import contradicts_stronger, normalize_for_model, normalize_for_review

CLOCK = "2026-09-07T12:00:00+00:00"
MODEL = "review-model"
PROMPT_FP = "sha256:review-fingerprint"
POLICY = "policy-1"
ADDRESS = "heading:course"


#: The ten refusals, as their values. `105` §1.3 and §1.4 record the course names the
#: model actually produced on the bench, and `104` §11.1 the `University Writing`
#: essays; these are those words. Not one of them carries a code, and every one was
#: `VALUE_NOT_NORMALIZABLE` on the run.
TITLES: tuple[str, ...] = (
    "University Writing",
    "AP World History",
    "Introduction to Organic Chemistry",
    "Machine Learning",
    "Thermodynamics",
    "Rotational Dynamics",
    "Calculus 2",
)

#: What must stay refused, and where each one comes from. The first four are this
#: task's own list; the rest are values another test file already measured off a real
#: disk (`tests/p6/test_p6_subject_slot.py`) or that a ratified stress case pins
#: (`tests/p8/test_p8_prompt_stress_cases.py` S1 and S6's control). A review path that
#: admitted any of them would be the laundering the deterministic rule was tightened to
#: stop, arriving by the other door.
STAYS_REFUSED: tuple[str, ...] = (
    "Spring 2026",           # a term, not a course (S7)
    "!",                     # punctuation off a PDF heading region
    "report.pdf",            # a filename with an extension
    "",                      # nothing at all
    "   ",                   # nothing at all, spelled with spaces
    "PHYS",                  # S6's control: a fragment of a code, not a title
    "PHYS1401 Problem Set 4",  # S1: a line that CONTAINS a code is not a title
    "a" * 300,               # longer than any title
    "&", "-", "(i)", "* DIEI ==outcomes in E", "#corre 1 . 4 - 1 : 4 . 10 - 4",
    "AUDIENCES IN GA4", "ADVERTISING REPORTS", "Addition principle-",
    "Analytics with google analytics 4 (ga4)",
    # `104` R-146 widened refusal 1 and these three are what that means on this
    # path. `normalize_for_review` refuses "a code, or a line containing one" by
    # asking `cli._STRUCTURED.search`, and until 2026-09-08 that shape saw only
    # UPPERCASE letters -- so S1's rule caught `PHYS1401 Problem Set 4` above and
    # let the same sentence through whenever the department was a word. All three
    # below were ACCEPTED as `possible` titles before R-146 and are refused now,
    # which is S1's own rule reaching the readings it always meant: A_fact rule 4
    # takes "the smallest run of characters that identifies the thing, not the
    # phrase that contains it". The third carries a term rather than a code and is
    # refused for `Spring 2026`'s reason, one line up in the same function.
    "Physics 1401 Introductory Mechanics",
    "Linear Algebra Section 001",
    "Modern Physics Spring 2026",
)


# --- the normaliser, asked directly ----------------------------------------------


@pytest.mark.parametrize("raw,expected", [("PHYS 1401", "PHYS1401"),
                                          ("PHYS1401", "PHYS1401"),
                                          ("UA872", "UA872")])
def test_a_code_shaped_subject_still_normalises_to_the_canonical_code(raw, expected):
    """The deterministic path is untouched, which is the precondition for the rest.

    `normalize_for_model` still answers the identifier question and still answers it
    the same way, so `65` §4.2's failure -- one course arriving as several spellings
    and becoming several folders -- cannot come back through this change. The review
    normaliser declines the same values, because a code is the direct path's and a
    value cannot be both.
    """
    assert normalize_for_model("subject", raw) == expected
    assert normalize_for_review("subject", raw) is None


#: `104` R-146 widened the identifier shape and `normalize_for_model` is the other
#: door it widened. Each row is (value, what the model path now makes of it); every
#: one of them was `None` -- refused outright -- until 2026-09-08.
WORD_SHAPED_ON_THE_MODEL_PATH: tuple[tuple[str, str | None], ...] = (
    # What the widening is FOR: a model answering with the course its document
    # prints, in the spelling the document prints it.
    ("Physics 1401", "Physics 1401"),
    ("COMS W3134", "COMS W3134"),
    # And what comes with it, because no shape separates these from the two above.
    ("Chapter 101", "Chapter 101"),
    ("Section 001", "Section 001"),
    # A title-case word plus a calendar year is a date, on both paths. `March 2026`
    # used to pass because nothing separated it from `Physics 1401`; the year does.
    ("March 2026", None),
    ("Due 2026", None),
    # A department written in capitals plus a year is still a course. The
    # canonicaliser drops the space in front of the digits, as it does for
    # `PHYS 1401`.
    ("CS 2026", "CS2026"),
    # Still refused, and by the lookahead R-146 made load-bearing rather than by
    # luck: a term is not a course on either path.
    ("Spring 2026", None),
    # Still refused by the single-capital rule, which R-146 did not touch.
    ("I 1403", None),
    ("A 2150", None),
)


@pytest.mark.parametrize("raw,expected", WORD_SHAPED_ON_THE_MODEL_PATH,
                         ids=[one[0] for one in WORD_SHAPED_ON_THE_MODEL_PATH])
def test_the_model_path_takes_a_word_and_a_number_now(raw, expected):
    """The second door `104` R-146 widened, stated rather than discovered later.

    `normalize_for_model` asks `cli.SUBJECT_RULE.pattern`, so widening the shape so
    that `Physics 1401` is a course at all necessarily lets a model's answer of
    `Chapter 101` through the same check. That is the constitution's trade taken
    deliberately: code delivers a shape, the model and then the person decide, and
    a model value arrives as `llm_supported` -- weaker than the deterministic rule
    and overrulable by the person, which is not true of what a shape asserts alone.

    The refusals matter as much as the admissions. `Spring 2026` is held off by
    the term lookahead, which stopped being decoration when the widening made a
    season match the identifier shape. `March 2026` and `Due 2026` are held off
    by the calendar-year lookahead: a title-case word plus a year is a date, and
    `CS 2026` stays because the department is written in capitals. `I 1403` and
    `A 2150` are held off by the single-capital rule that `TRUNCATIONS` in
    `tests/p6/test_p6_subject_rule.py` records, and R-146 did not touch it.
    """
    assert normalize_for_model("subject", raw) == expected


@pytest.mark.parametrize("raw", TITLES)
def test_a_title_normalises_only_into_the_review_path(raw):
    """The ten refusals, reversed -- into review, and no further."""
    assert normalize_for_model("subject", raw) is None
    assert normalize_for_review("subject", raw) == raw


@pytest.mark.parametrize("raw", STAYS_REFUSED)
def test_a_value_that_is_not_a_title_stays_refused_on_both_paths(raw):
    assert normalize_for_model("subject", raw) is None
    assert normalize_for_review("subject", raw) is None


def test_the_canonical_form_of_a_title_is_whitespace_collapsed_and_case_preserved():
    """Collapsed because `PHYS  1401` off a two-column page is one value, not two;
    case preserved because the title becomes a label a person reads, and
    `KindVocabulary`'s reason for respelling a `work_type` -- a closed library
    spelling -- does not exist for a name nobody has seen before.
    """
    assert normalize_for_review(
        "subject", "  Introduction   to\tOrganic  Chemistry \n") == (
            "Introduction to Organic Chemistry")
    assert normalize_for_review("subject", "aP wORLD hISTORY") == "aP wORLD hISTORY"


@pytest.mark.parametrize("field_key", ["instructor", "school"])
def test_a_field_nobody_opened_still_has_no_review_normaliser(field_key):
    """THE SCOPE LINE, MOVED BY `104` §18.2 GAP 3 AND STILL A LINE.

    **SABOTAGE:** widen `normalize_for_review`'s branch to every field, or drop the
    `return None` at the foot of it, so a model's answer about a PERSON or an
    INSTITUTION becomes a proposal on the person's screen. Nothing rules that: `00`:298
    names *"`work_type`, `subject`, `term` and user labels"* and gap 3 names two of the
    three; `instructor` and `school` were refused on the same run for the same reason
    and neither the owner nor the design has opened them. A file opening a field on its
    own authority is the file deciding, which is the constitution's first rule read
    backwards.

    This test used to read `test_only_subject_has_a_review_normaliser_today` and used
    to hold `work_type` and `term` too. Its old docstring argued that a value the
    library has not seen "becomes a folder NAME from a closed list, which is a
    different question from a course's own title" -- and `104` §18.2 gap 3 rules that
    reasoning wrong: the closed list was code deciding, `VALUE_NOT_NORMALIZABLE` was
    r15's largest rejection class, and `term` and `work_type` were most of it. The two
    fields moved to `test_a_value_the_library_has_not_seen_is_proposed_not_rejected`
    below; the scope line itself did not move, it narrowed.
    """
    assert normalize_for_review(field_key, "Some Words Here") is None


@pytest.mark.parametrize("field_key, unseen, refused", [
    # The library ships 942 `work_type` terms and has never seen either of these.
    # Both are values a real cloud run produced (`tests/p6/test_p6_kind.py` records
    # the measurement); `.pdf`, from the same run, is the one that became the folder
    # `Coursework/Daniel Lacker/IEOR3658/.pdf` and must still not come back.
    ("work_type", "Proposed Scope", ".pdf"),
    ("work_type", "Abstract", "GRC Proposed Scope V2.1"),
    # `105` §14.2 ruled in five term forms and ruled OUT three shapes by hand. A
    # sixth form nobody has met is a proposal; a shape the owner refused stays
    # refused, because that is an answer already given and not a value unseen.
    ("term", "Trimester 2 2025", "2023-2024"),
    ("term", "2023-24 Term 1", "S2026"),
])
def test_a_value_the_library_has_not_seen_is_proposed_not_rejected(
        field_key, unseen, refused):
    """`104` §18.2 gap 3, and `00`:298 in one assertion each way.

    **SABOTAGE:** restore the closed-vocabulary gate -- put `work_type` and `term`
    back behind `WORK_TYPE_VOCABULARY.terms` and `DATE_PATTERNS` alone, so a value
    neither knows dies at `VALUE_NOT_NORMALIZABLE` instead of reaching a person.
    `00`:298: *"A value the shipped library has not seen is proposed once; the user
    confirms or renames it."* On r15 that gate was the largest rejection class there
    was, `term` and `work_type` most of it, and the model was never told the fields
    were closed -- so it answered honestly and was refused for it.

    The second half of each row is what makes this a change of one thing rather than
    an opening of everything: a value the SHAPE refuses, or a shape the OWNER refused,
    is still `None`. Deleting either refusal is the other half of the sabotage.
    """
    assert normalize_for_review(field_key, unseen) == unseen
    assert normalize_for_review(field_key, refused) is None


def test_the_library_still_answers_first_and_in_its_own_spelling():
    """The seed did not move, and `104` §18.2 gap 3 says it must not.

    **SABOTAGE:** route a value the library DOES know through the review path -- have
    `normalize_for_model` return `None` for `Lecture` so it arrives as a proposal, or
    return the model's casing instead of the library's. `00`:298's own last clause is
    *"the ratified library is the vocabulary the model is shown first"*, and
    `facts.kind.KindVocabulary` gives the casing reason: that spelling becomes a
    folder name and the document's casing must not. A known term reaching the person
    as a question would ask them to ratify what the library already ratified, and
    `LECTURE SLIDES week 1.pdf` and `Lecture Slides Week 2.pdf` would become two
    folders -- `65` §4.2's recorded failure.
    """
    assert normalize_for_model("work_type", "Lecture") == "lecture"
    assert normalize_for_model("work_type", "  HOMEWORK  ") == "homework"
    assert normalize_for_model("term", "Spring-2026") == "Spring2026"
    # AND THE REVIEW HALF IS NEVER REACHED FOR THEM, which is
    # `fact_validation._check_three`'s order and not this function's: the
    # deployment's normaliser is asked first and its answer ends check 3. Asserted
    # here as the pair it is, so a reader can see that "the seed answers first"
    # means the person is not asked about `Lecture`.
    assert normalize_for_model("work_type", "Lecture") is not None
    assert normalize_for_model("term", "Fall 2023") is not None


def test_the_review_normaliser_refuses_a_non_string():
    assert normalize_for_review("subject", 4) is None
    assert normalize_for_review("subject", None) is None


# --- a real Site A world ---------------------------------------------------------


@dataclass(frozen=True)
class World:
    conn: object
    file_id: str
    content_hash: str
    dossier: Dossier
    dependencies: SiteDependencies
    resolver: object
    released_key: str


@pytest.fixture()
def site_a_conn(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    create_llm_schema(conn)
    return conn


def _world(conn, tmp_path, *, released: str, review: bool = True,
           stronger: tuple[str, str] | None = None,
           normalize=None, basis: str = DIRECT_ANCHOR, contradicts=None) -> World:
    """`basis` and `contradicts` arrived with `104` §18.2 gap 3b.

    `basis` is R-135's: an `EvidenceItem` the file did not say itself is
    `context-supported`, and `acceptance_outcome` turns a DIRECT acceptance of it
    into `accept_context_supported` -- the second producer of the outcome gap 3b's
    flag exists to tell apart. `contradicts` is the deployment's check-4 oracle, and
    it is a parameter because `cli.contradicts_stronger` answers `False` for a value
    its normaliser declined, which is right for this deployment and makes the
    two-flag case unreachable through it.
    """
    # ONE NAME PER WORLD, so a test may build TWO of them in one database. `104`
    # §18.2 gap 3b needs a comparison -- a proposal beside a neighbour-grounded
    # answer -- and a second `_world` with the same `run_id` and the same filename
    # collided on `extraction_runs.run_id` rather than telling the caller anything.
    # `name` is derived from `released` so it is stable per world and unique
    # between two worlds that differ at all.
    # A DIGEST AND NOT `hash()`: Python randomises string hashing per process, and a
    # filename that moves between runs is exactly what `tests/p8/determinism_probe.py`
    # exists to catch.
    stamp = hashlib.sha256(released.encode("utf-8")).hexdigest()[:8]
    name = f"Essay 2 Final Draft {stamp}.pdf"
    path = tmp_path / name
    path.write_bytes(b"a university writing essay")
    file_id = record_file(
        conn, path, filename=name,
        normalized_filename=name.lower(), extension=".pdf",
        observed_size=26, observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    run_id = f"r-{file_id}"
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=released,
        location=Location("heading", (Segment("field", label="heading"),)),
        occurrence_count=1, observed_at=CLOCK, reliability="possible", run_id=run_id)
    record_observation(conn, observation)
    released_key = observation.observation_key

    if stronger is not None:
        field_key, canonical = stronger
        value_id = ensure_value(
            conn, field_key=field_key, canonical_value=canonical,
            first_evidence_ref=released_key, origin=VALUE_ORIGINS[0])
        write_fact(
            conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
            value_id=value_id, reliability_state=VALIDATED,
            origin=DETERMINISTIC_EXTRACTOR, evidence_refs=(released_key,),
            cache_key="cache-stronger", active=True)

    request = build_request(
        conn, file_id=file_id, content_hash=content_hash,
        activation_signals=ActivationSignals(signals=(
            ActivationSignal(schema_id="academic", activates=lambda rows: True),)),
        normalizers={})
    dossier = Dossier(
        dossier_id=f"dossier-review-{stamp}", call_site=A_FACT, subject_ref=file_id,
        eligibility_reason=REMAINS_AMBIGUOUS, plan_version=None,
        policy_version=POLICY, allowed_vocabulary=tuple(request.allowlist),
        evidence_items=(EvidenceItem(
            evidence_ref=released_key, kind="excerpt", location="body",
            excerpt_span=(0, len(released)), reliability_state="direct",
            basis=basis),),
        conflicts=(),
        released_evidence=(ReleasedEvidence(
            observation_key=released_key, address=ADDRESS, value=released,
            zone="body"),),
        max_dossier_tokens=4000, reduction_rung=REDUCTION_NONE, release_id="rel-1")
    # THE DEPLOYMENT'S NORMALISER, WHICH IS THE COMPOSITION ROOT'S TO CHOOSE.
    # `src/cli.py` binds `normalize_with_the_persons_own_values(conn)` at the live
    # seam; the default here is the pure function, so every test written before
    # `104` §18.2 gap 3 asks exactly what it asked, and a test about the person's
    # own vocabulary passes the closure the run would.
    chosen = normalize_for_model if normalize is None else normalize
    oracle = contradicts_stronger if contradicts is None else contradicts
    fact_dependencies = (
        FactValidationDependencies(
            normalize=chosen, contradicts=oracle,
            normalize_for_review=normalize_for_review)
        if review else
        FactValidationDependencies(
            normalize=chosen, contradicts=oracle,
            normalize_for_review=None))
    return World(
        conn=conn, file_id=file_id, content_hash=content_hash, dossier=dossier,
        dependencies=SiteDependencies(
            fact=FactSiteDependencies(
                fact_request=request, fact_dependencies=fact_dependencies),
            placement=None, residual=None, template=None),
        resolver=lambda key: released if key == released_key else None,
        released_key=released_key)


def _response(field: str, value: str, *, key: str, span: str) -> bytes:
    return json.dumps({"claims": [{
        "payload": {"field": field, "value": value},
        "citations": [{"evidence_ref": key, "cited_span": span,
                       "why_it_supports": "the heading names it"}],
    }]}, separators=(",", ":")).encode("utf-8")


def _verdicts(world: World, response_bytes: bytes, *, apply: bool = False):
    result = dispatch(
        world.conn, world.dossier, response_bytes,
        site_dependencies=world.dependencies, evidence_resolver=world.resolver,
        contradicts=contradicts_stronger, model_id=MODEL,
        prompt_fingerprint=PROMPT_FP, dossier_builder="review-suite",
        release_audit_id=None, policy_version=POLICY, apply_consequence=apply,
        handle_key=FIXTURE_HANDLE_KEY)
    assert isinstance(result, tuple), result
    verdicts, _report = result
    assert len(verdicts) == 1, verdicts
    return verdicts[0]


def _rows_in(world: World, field_key: str):
    by_id = {row["value_id"]: row["canonical_value"]
             for row in values_in_field(world.conn, field_key)}
    return [(row["reliability_state"], by_id[row["value_id"]])
            for row in facts_for_file(world.conn, world.file_id, world.content_hash)
            if row["field_key"] == field_key]


def _subject_rows(world: World):
    return _rows_in(world, "subject")


# --- the seam ---------------------------------------------------------------------


def test_a_code_shaped_subject_is_still_accepted_direct_and_written_llm_supported(
        site_a_conn, tmp_path):
    """The control. If this moved, the change would have cost the corpus its codes."""
    world = _world(site_a_conn, tmp_path, released="PHYS 1401 syllabus")
    verdict = _verdicts(
        world, _response("subject", "PHYS 1401", key=world.released_key,
                         span="PHYS 1401"), apply=True)

    assert (verdict.outcome, verdict.reasons) == (ACCEPT_DIRECT, ())
    assert verdict.requires_review is False
    assert _subject_rows(world) == [(LLM_SUPPORTED, "PHYS1401")]


def test_a_title_is_recorded_as_a_candidate_the_person_confirms(
        site_a_conn, tmp_path):
    """The ten refusals, at the seam that refused them.

    `accept_context_supported` is the outcome the harness already publishes for an
    acceptance that a person has to look at, and its disposition is spelled
    `llm_supported_review`. `may_propose` is true because the value IS proposed --
    once, as §13.7 says -- and `requires_review` is true because nothing may act on
    it until somebody answers.

    **RE-ARGUED FOR `104` §18.2 GAP 3b: `reasons` WAS `()` AND IS NOW THE FLAG.**
    The old line asserted that an accepted title carried no reason code, and the
    argument for it was that a reason belongs to a refusal. That argument cost the
    record the one thing it needed: `accept_context_supported` has a second
    producer -- R-135's neighbour-grounded acceptance -- and with an empty `reasons`
    the two were the same row, so nothing could count how many values a run had put
    to the person. `VALUE_NOT_NORMALIZABLE` is the honest word for what happened
    (the canonicaliser DID decline) and it is now a reason to ask rather than a
    reason to discard, exactly as `CONTRADICTED_BY_STRONGER` became under gap 1.
    """
    world = _world(
        site_a_conn, tmp_path, released="University Writing - Essay 2")
    verdict = _verdicts(
        world, _response("subject", "University Writing", key=world.released_key,
                         span="University Writing"), apply=True)

    assert (verdict.outcome, verdict.reasons) == (
        ACCEPT_CONTEXT_SUPPORTED, (VALUE_NOT_NORMALIZABLE,))
    assert verdict.disposition == LLM_SUPPORTED_REVIEW
    assert verdict.requires_review is True
    assert verdict.may_propose is True
    assert _subject_rows(world) == [(POSSIBLE, "University Writing")]


def test_a_reviewed_title_is_not_a_folder_level_until_it_is_confirmed(
        site_a_conn, tmp_path):
    """`00`:42's own sentence, as the state the row carries.

    P6 publishes the floor a folder proposal rests on and P10 reads it; `possible` is
    the one ranked state below it, so a title cannot become a level by being repeated
    on five files -- which is exactly how `Georgetown Preparatory School` became one
    (`tree_design.materialise._unanchored_single_values`, whose own note records that
    a value seven files carry survives that guard). Confirming the value is what
    raises it, and confirming is the person's.
    """
    assert POSSIBLE not in PROPOSAL_ELIGIBLE_STATES

    world = _world(site_a_conn, tmp_path, released="AP World History Study Guide")
    _verdicts(world, _response("subject", "AP World History",
                               key=world.released_key, span="AP World History"),
              apply=True)

    states = [state for state, _value in _subject_rows(world)]
    assert states == [POSSIBLE]
    assert not set(states) & set(PROPOSAL_ELIGIBLE_STATES)


def test_a_title_the_cited_text_does_not_carry_is_still_refused(
        site_a_conn, tmp_path):
    """Grounding stays hard on the review path (`104` §13.6: grounding hard, the rest
    shown). A title a person could confirm is still only offered when the file said
    it."""
    world = _world(site_a_conn, tmp_path, released="Essay 2, final draft")
    verdict = _verdicts(
        world, _response("subject", "University Writing", key=world.released_key,
                         span="Essay 2"))

    assert (verdict.outcome, verdict.reasons) == (REJECT, (VALUE_NOT_IN_CITED_TEXT,))


def test_an_unseen_term_reaches_the_person_instead_of_the_rejection_pile(
        site_a_conn, tmp_path):
    """`104` §18.2 gap 3, at the seam, for `term`.

    **SABOTAGE:** put `DATE_PATTERNS` back in front of the review path -- let
    `normalize_for_model`'s `None` end check 3 for this field -- and this claim is
    `reject VALUE_NOT_NORMALIZABLE` again, which is where r15's largest rejection
    class came from. `105` §14.2 ruled in five term forms and a person's university
    writes a sixth; under the closed catalogue they got no term folder at all and no
    sentence saying why.

    `2023-2024 Term 1` is a form the owner DID rule in, so the shape used here is one
    nobody has ruled on at all: `Trimester 2 2025`. It comes back
    `accept_context_supported` and is written `possible`, which is the same seam
    `subject`'s titles pass through six tests above -- not a copy of it, the same
    `_check_three`.

    **RE-ARGUED FOR `104` §18.2 GAP 3b:** the verdict now NAMES check 3 while
    accepting. `104` §18.22 is why -- on r19 the local model answered `term` 109
    times and the run could not say which of its `value_not_normalizable` claims
    had become proposals -- and this field is the one that measurement was about.
    """
    world = _world(
        site_a_conn, tmp_path, released="Trimester 2 2025 reading list")
    verdict = _verdicts(
        world, _response("term", "Trimester 2 2025", key=world.released_key,
                         span="Trimester 2 2025"), apply=True)

    assert (verdict.outcome, verdict.reasons) == (
        ACCEPT_CONTEXT_SUPPORTED, (VALUE_NOT_NORMALIZABLE,))
    assert verdict.disposition == LLM_SUPPORTED_REVIEW
    assert verdict.requires_review is True
    assert _rows_in(world, "term") == [(POSSIBLE, "Trimester 2 2025")]
    # AND IT IS STILL NOT A FOLDER. `possible` is the one ranked state below the
    # floor a proposal rests on, so opening the field cost the tree nothing.
    assert POSSIBLE not in PROPOSAL_ELIGIBLE_STATES


def test_an_unseen_work_type_reaches_the_person_instead_of_the_rejection_pile(
        site_a_conn, tmp_path):
    """`104` §18.2 gap 3, at the seam, for `work_type`.

    **SABOTAGE:** restore the 942-term vocabulary as a gate. `Proposed Scope` is a
    value a real cloud run produced and the library has never seen; under the gate it
    was `VALUE_NOT_NORMALIZABLE`, and `work_type` was refused on seven of eight
    coursework files in that run. `00`:298: the value is proposed once and the user
    confirms or renames it.

    The pair that must NOT move is asserted one test down: `.pdf`, from the same run,
    is still refused, and it is the value that became the folder
    `Coursework/Daniel Lacker/IEOR3658/.pdf`.

    **RE-ARGUED FOR `104` §18.2 GAP 3b:** the accepted verdict carries check 3's
    word. The rejection two tests down carries the SAME word under `reject`, and
    that is the point rather than a collision -- one code, two consequences, and the
    outcome is what says which.
    """
    world = _world(
        site_a_conn, tmp_path, released="Proposed Scope of the module")
    verdict = _verdicts(
        world, _response("work_type", "Proposed Scope", key=world.released_key,
                         span="Proposed Scope"), apply=True)

    assert (verdict.outcome, verdict.reasons) == (
        ACCEPT_CONTEXT_SUPPORTED, (VALUE_NOT_NORMALIZABLE,))
    assert verdict.requires_review is True
    assert _rows_in(world, "work_type") == [(POSSIBLE, "Proposed Scope")]


def test_a_renamed_proposal_is_accepted_direct_on_the_next_run_at_the_seam(
        site_a_conn, tmp_path):
    """The rename, proved through `dispatch` and not only through the closure.

    **SABOTAGE:** believe that a rename that maps in `normalize` maps in the product.
    Check 3 is not the last check: `value_is_grounded` runs after it, and the person's
    word for the thing -- `scope note` -- appears NOWHERE in the file. If grounding
    tested only the canonical form, every renamed value would map at check 3 and die
    at `VALUE_NOT_IN_CITED_TEXT`, and "the user renames it" would be true of a
    function and false of the product. It survives because `value_is_grounded` tries
    BOTH spellings and its own docstring says why -- "the canonical form need not
    resemble the text". This test is what stops that permissiveness being narrowed
    without anyone noticing it was load-bearing for renames.

    The two runs are the point. Run one is the closure with an empty database: the
    library has never seen `Proposed Scope`, so it arrives `possible` and waits. The
    person answers between them, the way the missing gesture would. Run two is the
    same claim, the same evidence, the same model -- and now `accept_direct`, written
    `llm_supported` under the word THEY chose.
    """
    conn = site_a_conn
    world = _world(
        conn, tmp_path, released="Proposed Scope of the module",
        normalize=cli.normalize_with_the_persons_own_values(conn))
    answer = _response("work_type", "Proposed Scope", key=world.released_key,
                       span="Proposed Scope")

    first = _verdicts(world, answer, apply=True)
    assert first.outcome == ACCEPT_CONTEXT_SUPPORTED
    assert _rows_in(world, "work_type") == [(POSSIBLE, "Proposed Scope")]

    # The person renames it. `merge_values` records the alias and deletes nothing.
    proposed = next(row["value_id"] for row in values_in_field(conn, "work_type")
                    if row["canonical_value"] == "Proposed Scope")
    kept = ensure_value(conn, field_key="work_type", canonical_value="scope note",
                        first_evidence_ref=None, origin=VALUE_ORIGINS[1])
    write_fact(
        conn, file_id=world.file_id, content_hash=world.content_hash,
        field_key="work_type", value_id=kept, reliability_state=USER_CONFIRMED,
        origin=USER_CORRECTION, evidence_refs=(),
        cache_key="sha256:the-person-renamed-it", active=True)
    merge_values(conn, keep=kept, merged=proposed, reason="the person renamed it")

    second = _verdicts(world, answer, apply=True)
    assert (second.outcome, second.reasons) == (ACCEPT_DIRECT, ())
    assert second.requires_review is False
    assert (LLM_SUPPORTED, "scope note") in _rows_in(world, "work_type")


@pytest.mark.parametrize("field_key, value", [
    ("work_type", ".pdf"),
    ("work_type", "GRC Proposed Scope V2.1"),
    ("term", "2023-2024"),
])
def test_the_measured_bad_values_are_still_refused_at_the_seam(
        site_a_conn, tmp_path, field_key, value):
    """The teeth of the two tests above.

    **SABOTAGE:** open the fields by deleting the refusals as well as the closed sets
    -- drop `_TITLE_SHAPE` from the shared preamble, or stop asking `term_refusal`.
    Then `.pdf` is a proposal on the person's screen and `2023-2024` is offered as a
    semester, which `105` §14.2 ruled it is not. Opening a field is not the same as
    admitting everything, and §13.5 draws the line where this test does: a rule may
    reject only a STRUCTURALLY INVALID answer, and these three are that.
    """
    world = _world(site_a_conn, tmp_path, released=f"heading: {value} here")
    verdict = _verdicts(
        world, _response(field_key, value, key=world.released_key, span=value),
        apply=True)

    assert (verdict.outcome, verdict.reasons) == (REJECT, (VALUE_NOT_NORMALIZABLE,))
    assert _rows_in(world, field_key) == []


@pytest.mark.parametrize("value", ["Spring 2026", "PHYS", "report.pdf"])
def test_a_value_that_is_not_a_title_is_still_rejected_at_the_seam(
        site_a_conn, tmp_path, value):
    """S7 and S6's control, unmoved. The review path widens what is offered to a
    person; it does not widen what the validator accepts."""
    world = _world(site_a_conn, tmp_path, released=f"heading: {value} here")
    verdict = _verdicts(
        world, _response("subject", value, key=world.released_key, span=value),
        apply=True)

    assert (verdict.outcome, verdict.reasons) == (REJECT, (VALUE_NOT_NORMALIZABLE,))
    assert _subject_rows(world) == []


def test_without_a_review_normaliser_the_seam_is_exactly_what_it_was(
        site_a_conn, tmp_path):
    """The third callback is the DEPLOYMENT's, like the other two (C-5).

    A deployment that authors no review normaliser has no review path, and that is
    the honest answer rather than a default: P8 must not invent one, and a title is
    then the refusal it was this morning.
    """
    world = _world(
        site_a_conn, tmp_path, released="University Writing - Essay 2", review=False)
    verdict = _verdicts(
        world, _response("subject", "University Writing", key=world.released_key,
                         span="University Writing"), apply=True)

    assert (verdict.outcome, verdict.reasons) == (REJECT, (VALUE_NOT_NORMALIZABLE,))
    assert _subject_rows(world) == []


def test_a_title_beside_a_stronger_code_is_a_candidate_and_not_a_contradiction(
        site_a_conn, tmp_path):
    """CHECK 4 DOES NOT RUN ON A TITLE, AND THIS IS THE PIN FOR IT.

    `cli.contradicts_stronger` normalises before it compares and answers `False`
    when the normaliser declines, on a reason its own docstring gives: *"check 3
    runs first and has already rejected it"*. That sentence is no longer true of a
    title, so a file carrying a `validated` `subject = PHYS1401` and a model saying
    `subject = "University Writing"` gets both, and no `CONTRADICTED_BY_STRONGER`.

    That is `104` §13.6's direction and not an accident -- *"a hard veto only when a
    model fact is not grounded ... every other check, including rule-fact precedence
    over model facts, is shown to the model as a flag"* -- and it costs nothing here
    because the second row is `possible`: it cannot outrank the code and cannot
    become a folder. It is recorded rather than left to be discovered, because the
    day the review path writes anything stronger, this test is where it breaks.

    **RE-ARGUED FOR `104` §18.2 GAP 3b, AND THE ASSERTION IS SHARPER THAN IT WAS.**
    `reasons` is no longer empty, so "no `CONTRADICTED_BY_STRONGER`" is now a claim
    about WHICH word is on the record rather than about there being none: check 3's
    flag is present and check 4's is absent, which is exactly the sentence this
    test's title makes. Under the old empty tuple, a check-4 flag appearing here
    would have been caught -- and so would check 3's, which is the finding gap 3b
    exists to record.
    """
    world = _world(site_a_conn, tmp_path,
                   released="PHYS 1401 University Writing",
                   stronger=("subject", "PHYS1401"))
    verdict = _verdicts(
        world, _response("subject", "University Writing", key=world.released_key,
                         span="University Writing"), apply=True)

    assert (verdict.outcome, verdict.reasons) == (
        ACCEPT_CONTEXT_SUPPORTED, (VALUE_NOT_NORMALIZABLE,))
    assert CONTRADICTED_BY_STRONGER not in verdict.reasons
    assert sorted(_subject_rows(world)) == [
        (POSSIBLE, "University Writing"), (VALIDATED, "PHYS1401")]


def test_the_deterministic_pass_still_refuses_every_title_it_ever_refused(
        site_a_conn, tmp_path):
    """The other producer, unmoved, asked about the same words.

    `104` §11.2 step 1 changes what the MODEL is asked, not what the rule reads. A
    heading saying `University Writing` beside the word `syllabus` still fills no
    `subject` fact: the rule wants an identifier, and this change did not touch it.
    """
    assert cli.SUBJECT_RULE.pattern.search("University Writing") is None
    assert cli.normalize_for_model("subject", "University Writing") is None


# --- `104` §18.2 gap 3b: the record says WHICH half of check 3 answered ------------


def test_a_proposal_and_a_neighbours_answer_no_longer_arrive_as_the_same_row(
        site_a_conn, tmp_path):
    """`104` §18.2 gap 3b's whole reason for existing, in one comparison.

    **SABOTAGE:** take `VALUE_NOT_NORMALIZABLE` back off the review acceptance in
    `fact_validation._run_checks` -- return `reasons=()` for it, as gap 3 did. Then
    the two verdicts below are indistinguishable: same `accept_context_supported`,
    same `llm_supported_review`, same `requires_review`, same empty reasons, same
    `possible` fact. One of them is *"nobody has ever seen this value, please
    confirm it"* and the other is *"this was read off the syllabus next door"*, and
    no reader of `llm_verdict` can tell which is which. `104` §18.22 is that
    blindness measured on a real run: the local model answered `term` 109 times, 125
    claims carried check 3's word, and the run could not say how many had become
    proposals.

    The two producers are genuinely different questions. R-135's is about WHERE the
    answer was grounded and is settled by `acceptance_outcome` reading the cited
    item's `basis`; gap 3's is about whether this deployment's canonicaliser has ever
    seen the value, and is settled by the review-shape predicate. Only the second is
    a question for a person.
    """
    proposed = _world(site_a_conn, tmp_path, released="University Writing - Essay 2")
    proposal_verdict = _verdicts(
        proposed, _response("subject", "University Writing",
                            key=proposed.released_key, span="University Writing"))

    neighbour = _world(site_a_conn, tmp_path, released="PHYS 1401 syllabus",
                       basis=CONTEXT_SUPPORTED)
    neighbour_verdict = _verdicts(
        neighbour, _response("subject", "PHYS 1401", key=neighbour.released_key,
                             span="PHYS 1401"))

    # THE HALF THEY SHARE, which is why the reason had to carry the difference.
    assert proposal_verdict.outcome == neighbour_verdict.outcome
    assert proposal_verdict.disposition == neighbour_verdict.disposition
    assert proposal_verdict.requires_review is True
    assert neighbour_verdict.requires_review is True
    # AND THE HALF THAT NOW SEPARATES THEM.
    assert proposal_verdict.reasons == (VALUE_NOT_NORMALIZABLE,)
    assert neighbour_verdict.reasons == ()


def test_check_three_and_check_four_both_land_on_one_verdict(
        site_a_conn, tmp_path):
    """Two flags, two questions, one claim -- and neither erases the other.

    **SABOTAGE:** put the two-armed assignment back --
    `reasons = (CONTRADICTED_BY_STRONGER,) if flagged else ()` -- and check 4's
    finding overwrites check 3's. The person is then told a stronger fact disagrees
    and never told the value is one the product has never seen, so the screen asks
    them to settle a conflict between two values it claims to know, one of which it
    has never heard of. `placement_validation._flagged` composes for the same reason
    at site C: several flags tell the person one thing each.

    **`contradicts` IS THIS DEPLOYMENT'S AND IT IS INJECTED HERE ON PURPOSE.**
    `cli.contradicts_stronger` answers `False` when its normaliser declines the value
    -- so under `src/cli.py` a title beside a stronger code is a candidate and not a
    contradiction, which the test above this block pins. That is the DEPLOYMENT's
    answer (C-5), not P8's, and the validator must compose the two flags whatever a
    deployment's oracle says, or the order the checks happen to run in would quietly
    decide what the record keeps.
    """
    world = _world(site_a_conn, tmp_path,
                   released="PHYS 1401 University Writing",
                   stronger=("subject", "PHYS1401"),
                   contradicts=lambda proposal, row: True)
    verdict = _verdicts(
        world, _response("subject", "University Writing", key=world.released_key,
                         span="University Writing"), apply=True)

    assert verdict.outcome == ACCEPT_CONTEXT_SUPPORTED
    assert verdict.reasons == (VALUE_NOT_NORMALIZABLE, CONTRADICTED_BY_STRONGER)
    assert verdict.requires_review is True
    # STILL AN ACCEPTANCE, AND STILL BELOW THE FLOOR. Two flags do not add up to a
    # rejection: the claim is written `possible` beside the rule's `validated` row,
    # which is `104` §18.2 gap 1's ruling and gap 3b does not touch it.
    assert sorted(_subject_rows(world)) == [
        (POSSIBLE, "University Writing"), (VALIDATED, "PHYS1401")]


@pytest.mark.parametrize("field_key,value,released", [
    ("term", "Trimester 2 2025", "Trimester 2 2025 reading list"),
    ("work_type", "Proposed Scope", "Proposed Scope of the module"),
    ("subject", "University Writing", "University Writing - Essay 2"),
])
def test_one_word_two_outcomes_and_the_outcome_is_what_says_which(
        site_a_conn, tmp_path, field_key, value, released):
    """`VALUE_NOT_NORMALIZABLE` is now a refusal AND a question, and that is fine.

    **SABOTAGE:** mint a second reason code for the flag -- `value_proposed`, say --
    instead of reusing check 3's own word. Then `_REASON_TO_CHECK` needs a row for
    it, `p6_verdict_from_p8` needs to know it can never be a rejection, the closed
    vocabulary grows a code meaning the same thing as one it already has, and every
    stored verdict written before the new code is one nobody can compare with a
    verdict written after. Gap 1 made the same choice one check later and for the
    same reason: `CONTRADICTED_BY_STRONGER` is the flag word AND the rejection word
    it used to be.

    What tells the two apart is the OUTCOME, which is the field a reader already has
    to look at to know whether a claim became a fact. `p6_verdict_from_p8` branches
    on it too, so the flagged half never reaches `_REASON_TO_CHECK` at all.
    """
    accepted = _world(site_a_conn, tmp_path, released=released)
    proposal = _verdicts(
        accepted, _response(field_key, value, key=accepted.released_key, span=value))

    refused_value = "GRC Proposed Scope V2.1"
    rejected_world = _world(site_a_conn, tmp_path,
                            released=f"heading: {refused_value} here")
    rejection = _verdicts(
        rejected_world, _response(field_key, refused_value,
                                  key=rejected_world.released_key,
                                  span=refused_value))

    assert proposal.reasons == (VALUE_NOT_NORMALIZABLE,)
    assert rejection.reasons == (VALUE_NOT_NORMALIZABLE,)
    assert (proposal.outcome, proposal.may_propose) == (
        ACCEPT_CONTEXT_SUPPORTED, True)
    assert (rejection.outcome, rejection.may_propose) == (REJECT, False)


@pytest.mark.parametrize("raw", ["", "   ", '""'])
def test_an_empty_answer_is_still_an_abstention_and_carries_no_flag(
        site_a_conn, tmp_path, raw):
    """R-119 is upstream of gap 3b and stays there.

    **SABOTAGE:** move `_declined_the_field` below `_check_three`, or let the review
    predicate answer for an empty string. Either way a decline becomes a PROPOSAL:
    the person is shown `term: ''` on the confirm screen, `model_facts` stops reusing
    the abstention (`store.abstained_fields` reads abstentions, not acceptances), and
    the same model is asked the same question it already declined. R-119 measured 19
    of these on the owner's corpus.

    An empty value is the third of the three outcomes this change is about --
    propose, reject, abstain -- and it is the one gap 3b must not touch.
    """
    world = _world(site_a_conn, tmp_path, released="Trimester 2 2025 reading list")
    verdict = _verdicts(
        world, _response("term", raw, key=world.released_key,
                         span="Trimester 2 2025"), apply=True)

    assert (verdict.outcome, verdict.reasons) == (ABSTAIN, ())
    assert verdict.requires_review is False
    assert _rows_in(world, "term") == []
