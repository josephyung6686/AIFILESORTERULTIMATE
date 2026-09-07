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
"""
from __future__ import annotations

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
from facts.file_facts import DETERMINISTIC_EXTRACTOR, facts_for_file, write_fact
from facts.llm_seam import build_request
from facts.read_surface import PROPOSAL_ELIGIBLE_STATES
from facts.states import LLM_SUPPORTED, POSSIBLE, VALIDATED
from facts.values import VALUE_ORIGINS, ensure_value, values_in_field
from llm_harness.fact_validation import FactValidationDependencies
from llm_harness.fixtures import FIXTURE_HANDLE_KEY
from llm_harness.records import Dossier, EvidenceItem, ReleasedEvidence
from llm_harness.schema import create_llm_schema
from llm_harness.sites import FactSiteDependencies, SiteDependencies, dispatch
from llm_harness.vocabulary import (
    A_FACT,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
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


@pytest.mark.parametrize("field_key", ["work_type", "term", "instructor", "school"])
def test_only_subject_has_a_review_normaliser_today(field_key):
    """R-98 is the `subject` half of G15 and this test is the scope line.

    `work_type` was refused on seven of eight coursework files in the same run, for
    the same reason in a different vocabulary (the library's 942 terms). That is the
    other half of §13.7 and it is not this change: `work_type`'s members are the
    ratified library's, and a value the library has not seen becomes a folder NAME
    from a closed list, which is a different question from a course's own title.
    """
    assert normalize_for_review(field_key, "Some Words Here") is None


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
           stronger: tuple[str, str] | None = None) -> World:
    path = tmp_path / "Essay 2 Final Draft.pdf"
    path.write_bytes(b"a university writing essay")
    file_id = record_file(
        conn, path, filename="Essay 2 Final Draft.pdf",
        normalized_filename="essay 2 final draft.pdf", extension=".pdf",
        observed_size=26, observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    record_run(conn, ExtractionRun(
        run_id="r-1", file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=released,
        location=Location("heading", (Segment("field", label="heading"),)),
        occurrence_count=1, observed_at=CLOCK, reliability="possible", run_id="r-1")
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
        dossier_id="dossier-review", call_site=A_FACT, subject_ref=file_id,
        eligibility_reason=REMAINS_AMBIGUOUS, plan_version=None,
        policy_version=POLICY, allowed_vocabulary=tuple(request.allowlist),
        evidence_items=(EvidenceItem(
            evidence_ref=released_key, kind="excerpt", location="body",
            excerpt_span=(0, len(released)), reliability_state="direct",
            basis=DIRECT_ANCHOR),),
        conflicts=(),
        released_evidence=(ReleasedEvidence(
            observation_key=released_key, address=ADDRESS, value=released,
            zone="body"),),
        max_dossier_tokens=4000, reduction_rung=REDUCTION_NONE, release_id="rel-1")
    fact_dependencies = (
        FactValidationDependencies(
            normalize=normalize_for_model, contradicts=contradicts_stronger,
            normalize_for_review=normalize_for_review)
        if review else
        FactValidationDependencies(
            normalize=normalize_for_model, contradicts=contradicts_stronger,
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


def _subject_rows(world: World):
    by_id = {row["value_id"]: row["canonical_value"]
             for row in values_in_field(world.conn, "subject")}
    return [(row["reliability_state"], by_id[row["value_id"]])
            for row in facts_for_file(world.conn, world.file_id, world.content_hash)
            if row["field_key"] == "subject"]


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
    """
    world = _world(
        site_a_conn, tmp_path, released="University Writing - Essay 2")
    verdict = _verdicts(
        world, _response("subject", "University Writing", key=world.released_key,
                         span="University Writing"), apply=True)

    assert (verdict.outcome, verdict.reasons) == (ACCEPT_CONTEXT_SUPPORTED, ())
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
    """
    world = _world(site_a_conn, tmp_path,
                   released="PHYS 1401 University Writing",
                   stronger=("subject", "PHYS1401"))
    verdict = _verdicts(
        world, _response("subject", "University Writing", key=world.released_key,
                         span="University Writing"), apply=True)

    assert (verdict.outcome, verdict.reasons) == (ACCEPT_CONTEXT_SUPPORTED, ())
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
