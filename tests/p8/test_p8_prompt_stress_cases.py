# tests/p8/test_p8_prompt_stress_cases.py
"""`76-PROMPT-RESEARCH.md` §7's fifteen stress cases, run against the real validator.

`76` §10.3 records that these fifteen are *"recorded response bytes plus an expected
`(outcome, reasons)` pair"* and *"can be written against `fixtures._bytes` and run
without a model, which means the prompt can be stress-tested before it is ever
fingerprinted."* This file is that suite.

**No `PromptDefinition` is constructed here and no model is called.** Every test
below feeds recorded bytes to `llm_harness.sites.dispatch` at `A_FACT` over a real
P1 file, a real P4 observation, P6's own `build_request`, and this deployment's own
oracles -- `cli.normalize_for_model` and `cli.contradicts_stronger`. What is measured
is the MACHINE: for each of the fifteen, does the validator catch the wrong answer,
or is the prompt the only defence?

Each test carries its own control: the near-identical response that produces the
other outcome. A stress case whose bytes are accepted and whose control is also
accepted has not been exercised, and the control is what says so.
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
from facts.states import DIRECT
from facts.unresolved import unresolved_for_file
from facts.values import VALUE_ORIGINS, ensure_value
from llm_harness.fact_validation import FactValidationDependencies
from llm_harness.records import Dossier, EvidenceItem, ReleasedEvidence
from llm_harness.schema import create_llm_schema
from llm_harness.sites import FactSiteDependencies, SiteDependencies, dispatch
from llm_harness.vocabulary import (
    A_FACT,
    ABSTAIN,
    ACCEPT_DIRECT,
    CITATION_NOT_FOUND,
    CITATION_NOT_IN_DOSSIER,
    CITATION_SPAN_MISMATCH,
    CONTRADICTED_BY_STRONGER,
    DIRECT_ANCHOR,
    FIELD_NOT_IN_ACTIVE_SCHEMA,
    REDUCTION_NONE,
    REJECT,
    REMAINS_AMBIGUOUS,
    SCHEMA_INVALID,
    VALUE_NOT_NORMALIZABLE,
)

# The deployment's own answers to §3.6 checks 3 and 4. Imported, never re-authored:
# `src/cli.py` is the sole composition root and the only module in `src/` that owns
# them (`cli.py:558`, `cli.py:600`). A second normaliser written here would be a
# second deployment, and the whole point of the suite is to measure this one.
from cli import contradicts_stronger, normalize_for_model  # noqa: E402
from llm_harness.fixtures import FIXTURE_HANDLE_KEY

CLOCK = "2026-08-31T12:00:00+00:00"
MODEL = "stress-model"
PROMPT_FP = "sha256:stress-fingerprint"
POLICY = "policy-1"
ADDRESS = "heading:course"
OTHER_ADDRESS = "heading:not-this-one"


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
    second_key: str | None


@pytest.fixture()
def site_a_conn(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    create_llm_schema(conn)
    return conn


def _record_file(conn, tmp_path, body: bytes) -> tuple[str, str]:
    path = tmp_path / "Syllabus.pdf"
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename="Syllabus.pdf", normalized_filename="syllabus.pdf",
        extension=".pdf", observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, file_id, content_hash, raw, label, run_id) -> str:
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location("heading", (Segment("field", label=label),)),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id=run_id)
    record_observation(conn, observation)
    return observation.observation_key


def _world(
    conn,
    tmp_path,
    *,
    released: str = "PHYS1401 Problem Set 4",
    stored: str | None = None,
    address: str = ADDRESS,
    second_reading: str | None = None,
    release_the_second: bool = False,
    stronger: tuple[str, str] | None = None,
) -> World:
    """One file, one released observation, and the real P6/P8 authorities over it.

    `released` is what P7 put in front of the model. `stored` is what the evidence
    resolver returns for it -- they differ under redaction, which is the whole of S4
    and the reason `_check_citation` never span-matches against the store.
    """
    file_id, content_hash = _record_file(conn, tmp_path, b"BUSIB 4300, Spring 2026")
    released_key = _observe(
        conn, file_id=file_id, content_hash=content_hash, raw=released,
        label="heading", run_id="r-1")
    second_key = None
    if second_reading is not None:
        second_key = _observe(
            conn, file_id=file_id, content_hash=content_hash,
            raw=second_reading, label="footer", run_id="r-2")

    if stronger is not None:
        field_key, canonical = stronger
        value_id = ensure_value(
            conn, field_key=field_key, canonical_value=canonical,
            first_evidence_ref=released_key, origin=VALUE_ORIGINS[0])
        write_fact(
            conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
            value_id=value_id, reliability_state=DIRECT,
            origin=DETERMINISTIC_EXTRACTOR, evidence_refs=(released_key,),
            cache_key="cache-stronger", active=True)

    request = build_request(
        conn, file_id=file_id, content_hash=content_hash,
        activation_signals=ActivationSignals(signals=(
            ActivationSignal(schema_id="academic", activates=lambda rows: True),
        )),
        normalizers={},
    )
    items = [EvidenceItem(
        evidence_ref=released_key, kind="excerpt", location="body",
        excerpt_span=(0, len(released)), reliability_state="direct",
        basis=DIRECT_ANCHOR)]
    released_items = [ReleasedEvidence(
        observation_key=released_key, address=address, value=released, zone="body")]
    if second_key is not None:
        items.append(EvidenceItem(
            evidence_ref=second_key, kind="excerpt", location="body",
            excerpt_span=None, reliability_state="direct", basis=DIRECT_ANCHOR))
        if release_the_second:
            released_items.append(ReleasedEvidence(
                observation_key=second_key, address=OTHER_ADDRESS,
                value=second_reading, zone="body"))
    dossier = Dossier(
        dossier_id="dossier-stress",
        call_site=A_FACT,
        subject_ref=file_id,
        eligibility_reason=REMAINS_AMBIGUOUS,
        plan_version=None,
        policy_version=POLICY,
        # §9.3: nothing asserts this equals `FactRequest.allowlist`. Here it does,
        # deliberately -- a suite measuring the prompt must not also be measuring a
        # dossier builder that shows the model a different list from the one it is
        # judged against.
        allowed_vocabulary=tuple(request.allowlist),
        evidence_items=tuple(items),
        conflicts=(),
        released_evidence=tuple(released_items),
        max_dossier_tokens=4000,
        reduction_rung=REDUCTION_NONE,
        release_id="rel-1",
    )
    resolvable = {released_key: stored if stored is not None else released}
    if second_key is not None:
        resolvable[second_key] = second_reading
    dependencies = SiteDependencies(
        fact=FactSiteDependencies(
            fact_request=request,
            fact_dependencies=FactValidationDependencies(
                normalize=normalize_for_model,
                contradicts=contradicts_stronger,
            ),
        ),
        placement=None, residual=None, template=None,
    )
    return World(
        conn=conn, file_id=file_id, content_hash=content_hash, dossier=dossier,
        dependencies=dependencies, resolver=lambda key: resolvable.get(key),
        released_key=released_key, second_key=second_key,
    )


def _judge(world: World, response_bytes: bytes, *,
           apply: bool = False) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Every verdict the real dispatcher returns, as `(outcome, reasons)` pairs.

    `apply` is `apply_consequence`. It is False unless a test is about the
    consequence, because `write_unresolved` is always an INSERT and a suite that
    applied every control response would leave P6's tables full of refusals nobody
    made.
    """
    result = dispatch(
        world.conn, world.dossier, response_bytes,
        site_dependencies=world.dependencies,
        evidence_resolver=world.resolver,
        contradicts=contradicts_stronger,
        model_id=MODEL,
        prompt_fingerprint=PROMPT_FP,
        dossier_builder="stress-suite",
        release_audit_id=None,
        policy_version=POLICY,
        apply_consequence=apply, handle_key=FIXTURE_HANDLE_KEY,
    )
    assert isinstance(result, tuple), result
    verdicts, _report = result
    return tuple((verdict.outcome, verdict.reasons) for verdict in verdicts)


def _one(world: World, response_bytes: bytes, *,
         apply: bool = False) -> tuple[str, tuple[str, ...]]:
    judged = _judge(world, response_bytes, apply=apply)
    assert len(judged) == 1, judged
    return judged[0]


# --- response builders -----------------------------------------------------------


def _claim(field: str, value: object, *, key: str, span: str | None = None,
           metadata: str | None = None, why: str = "the heading names it",
           claim_ref: str = "c1", extra: dict | None = None) -> dict:
    citation: dict[str, object] = {"evidence_ref": key, "why_it_supports": why}
    if span is not None:
        citation["cited_span"] = span
    if metadata is not None:
        citation["metadata_field_name"] = metadata
    claim: dict[str, object] = {
        "claim_ref": claim_ref,
        "payload": {"field": field, "value": value},
        "citations": [citation],
    }
    if extra:
        claim.update(extra)
    return claim


def _decline(field: str, statement: str, claim_ref: str = "c1") -> dict:
    return {
        "claim_ref": claim_ref,
        "payload": {"field": field},
        "unknown": {"insufficiency_statement": statement},
    }


def _response(*claims: dict) -> bytes:
    return json.dumps({"claims": list(claims)}, separators=(",", ":")).encode("utf-8")


#: Expectations are the WHOLE response's verdicts, in order. Site A can answer one
#: response with several verdicts or destroy all of them with one, so a per-claim
#: expectation would hide exactly the failure `76` R16 is about.
ONE_ACCEPT = ((ACCEPT_DIRECT, ()),)
ONE_ABSTAIN = ((ABSTAIN, ()),)
WHOLE_RESPONSE_DEAD = ((REJECT, (SCHEMA_INVALID,)),)


def _one_reject(reason: str) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return ((REJECT, (reason,)),)


# --- the fifteen -----------------------------------------------------------------


@dataclass(frozen=True)
class Case:
    """One §7 stress case as data: a world, wrong bytes, right bytes, two verdicts.

    `control` is not decoration. A stress case whose wrong answer is accepted proves
    nothing unless the right answer is known to be accepted too, and a stress case
    whose wrong answer is rejected proves nothing unless the near-identical right
    answer is known to pass -- otherwise the rejection could be the world's fault.
    """

    case_id: str
    what: str
    world: dict
    stress: object
    stress_expected: tuple
    control: object
    control_expected: tuple
    #: One of `MACHINE`, `PROMPT_ONLY`, `NEITHER`. The whole point of the suite.
    defence: str


#: The validator rejects the wrong answer on its own. The prompt's wording about
#: this case is belt-and-braces: if the model gets it wrong, nothing is stored.
MACHINE = "machine"

#: The wrong answer passes every check and becomes an `llm_supported` fact. The
#: prompt's wording is the entire defence, and a word changed here changes what
#: ends up on someone's file.
PROMPT_ONLY = "prompt-only"

#: The model's answer is CORRECT and accepted, and the damage happens after the
#: verdict. Neither wording nor a check can reach it; only code can.
NEITHER = "neither"


DEFAULT_RELEASED = "PHYS1401 Problem Set 4"


def _good(world: World, field: str = "subject", value: str = "PHYS1401") -> bytes:
    return _response(_claim(field, value, key=world.released_key, span=value))


CASES: tuple[Case, ...] = (
    Case(
        "S1", "the whole released line proposed as the value",
        {"released": DEFAULT_RELEASED},
        lambda w: _response(_claim(
            "subject", DEFAULT_RELEASED, key=w.released_key, span=DEFAULT_RELEASED)),
        ONE_ACCEPT,
        lambda w: _good(w),
        ONE_ACCEPT,
        PROMPT_ONLY,
    ),
    Case(
        "S2", "a plausible value invented over prose that supports nothing",
        {"released": "Prepared for the committee in the autumn, with notes."},
        lambda w: _response(_claim(
            "instructor", "the committee", key=w.released_key,
            span="the committee")),
        ONE_ACCEPT,
        lambda w: _response(_decline(
            "instructor", "no released value names a person")),
        ONE_ABSTAIN,
        PROMPT_ONLY,
    ),
    Case(
        "S3", "two claims about one field",
        {"released": DEFAULT_RELEASED, "second_reading": "ASTR1002 Lab Notes",
         "release_the_second": True},
        lambda w: _response(
            _claim("subject", "PHYS1401", key=w.released_key, span="PHYS1401"),
            _claim("subject", "ASTR1002", key=w.second_key, span="ASTR1002",
                   claim_ref="c2"),
        ),
        WHOLE_RESPONSE_DEAD,
        lambda w: _response(
            _claim("subject", "PHYS1401", key=w.released_key, span="PHYS1401"),
            _claim("instructor", "Lab Notes", key=w.second_key, span="Lab Notes",
                   claim_ref="c2"),
        ),
        ((ACCEPT_DIRECT, ()), (ACCEPT_DIRECT, ())),
        MACHINE,
    ),
    Case(
        "S4", "a quotation from the store that P7 did not release",
        {"released": "PHYS1401", "stored": "PHYS1401 taught by Dr Smith"},
        lambda w: _response(_claim(
            "instructor", "Dr Smith", key=w.released_key, span="Dr Smith")),
        _one_reject(CITATION_SPAN_MISMATCH),
        lambda w: _good(w),
        ONE_ACCEPT,
        MACHINE,
    ),
    Case(
        "S5", "a field key outside allowed_vocabulary",
        {"released": DEFAULT_RELEASED},
        lambda w: _response(_claim(
            "course_code", "PHYS1401", key=w.released_key, span="PHYS1401")),
        _one_reject(FIELD_NOT_IN_ACTIVE_SCHEMA),
        lambda w: _good(w),
        ONE_ACCEPT,
        MACHINE,
    ),
    Case(
        "S6", "a second spelling of a value a stronger fact already carries",
        {"released": "PHYS 1401", "stronger": ("subject", "PHYS1401")},
        lambda w: _response(_claim(
            "subject", "PHYS 1401", key=w.released_key, span="PHYS 1401")),
        ONE_ACCEPT,
        lambda w: _response(_claim(
            "subject", "PHYS", key=w.released_key, span="PHYS")),
        _one_reject(CONTRADICTED_BY_STRONGER),
        # Check 4 catches a real disagreement -- that is what the control shows.
        # What nothing catches is the case itself: the correct answer, accepted,
        # then stored under a second spelling. `test_s6_...` below measures that.
        NEITHER,
    ),
    Case(
        "S7", "a term proposed as a subject",
        {"released": "PHYS1401 Spring 2026"},
        lambda w: _response(_claim(
            "subject", "Spring 2026", key=w.released_key, span="Spring 2026")),
        _one_reject(VALUE_NOT_NORMALIZABLE),
        lambda w: _response(_claim(
            "term", "Spring 2026", key=w.released_key, span="Spring 2026")),
        ONE_ACCEPT,
        MACHINE,
    ),
    Case(
        "S8", "a fluent quotation that is in no released value",
        {"released": DEFAULT_RELEASED},
        lambda w: _response(_claim(
            "subject", "PHYS1401", key=w.released_key,
            span="the course is taught in the autumn term")),
        _one_reject(CITATION_SPAN_MISMATCH),
        lambda w: _good(w),
        ONE_ACCEPT,
        MACHINE,
    ),
    Case(
        "S9", "an evidence_ref in evidence_items with nothing released for it",
        {"released": DEFAULT_RELEASED,
         "second_reading": "a footer P7 released nothing for"},
        lambda w: _response(_claim(
            "instructor", "a footer", key=w.second_key, span="a footer")),
        _one_reject(CITATION_NOT_IN_DOSSIER),
        lambda w: _good(w),
        ONE_ACCEPT,
        MACHINE,
    ),
    Case(
        "S10", "both cited_span and metadata_field_name filled",
        {"released": DEFAULT_RELEASED},
        lambda w: _response(_claim(
            "subject", "PHYS1401", key=w.released_key, span="PHYS1401",
            metadata=ADDRESS)),
        WHOLE_RESPONSE_DEAD,
        lambda w: _response(_claim(
            "subject", "PHYS1401", key=w.released_key, metadata=ADDRESS)),
        ONE_ACCEPT,
        MACHINE,
    ),
    Case(
        "S11", "an empty claims list instead of an abstention",
        {"released": DEFAULT_RELEASED},
        lambda w: b'{"claims":[]}',
        WHOLE_RESPONSE_DEAD,
        lambda w: _response(_decline("subject", "no released value names a course")),
        ONE_ABSTAIN,
        MACHINE,
    ),
    Case(
        "S12", "a preamble and a code fence around the JSON",
        {"released": DEFAULT_RELEASED},
        lambda w: b"Here is my answer:\n```json\n" + _good(w) + b"\n```",
        WHOLE_RESPONSE_DEAD,
        lambda w: _good(w),
        ONE_ACCEPT,
        MACHINE,
    ),
    Case(
        "S13", '"unknown": false alongside a real claim',
        {"released": DEFAULT_RELEASED},
        lambda w: _response(_claim(
            "subject", "PHYS1401", key=w.released_key, span="PHYS1401",
            extra={"unknown": False})),
        WHOLE_RESPONSE_DEAD,
        lambda w: _good(w),
        ONE_ACCEPT,
        MACHINE,
    ),
    Case(
        "S14", "a metadata citation whose field name is retyped, not copied",
        {"released": DEFAULT_RELEASED},
        lambda w: _response(_claim(
            "subject", "PHYS1401", key=w.released_key, metadata="heading")),
        _one_reject(CITATION_SPAN_MISMATCH),
        lambda w: _response(_claim(
            "subject", "PHYS1401", key=w.released_key, metadata=ADDRESS)),
        ONE_ACCEPT,
        MACHINE,
    ),
    Case(
        "S15", "a value emitted as a number rather than a JSON string",
        {"released": DEFAULT_RELEASED},
        lambda w: _response(_claim(
            "creation_date", 2026, key=w.released_key, span="PHYS1401")),
        _one_reject(VALUE_NOT_NORMALIZABLE),
        lambda w: _response(_claim(
            "creation_date", "2026", key=w.released_key, span="PHYS1401")),
        ONE_ACCEPT,
        MACHINE,
    ),
)


@pytest.mark.parametrize("case", CASES, ids=[case.case_id for case in CASES])
def test_the_recorded_stress_case_and_its_control(case, site_a_conn, tmp_path):
    """`76` §7, one row at a time, against the validator that actually runs."""
    world = _world(site_a_conn, tmp_path, **case.world)
    assert _judge(world, case.stress(world)) == case.stress_expected, case.what
    assert _judge(world, case.control(world)) == case.control_expected, case.what
    rejected = case.stress_expected[0][0] == REJECT
    assert (case.defence == MACHINE) is rejected, (
        "a case defended by the machine is one whose wrong answer is REJECTED, and "
        "a case defended by wording is one whose wrong answer is not")


def test_the_split_between_machine_defended_and_prompt_defended_cases():
    """The deliverable, as an assertion.

    Twelve of the fifteen the validator rejects on its own. Two -- S1 and S2 -- it
    accepts, writing an `llm_supported` fact; there the prompt's wording is the only
    thing standing between a model and someone's file. One, S6, is answered
    correctly and stored wrongly, which no wording and no check can reach.

    If the prompt-only set ever grows, a wording rule has quietly become load
    bearing. If it shrinks, a check was added and `82` §3 can stop calling that
    requirement unenforced.
    """
    by_defence: dict[str, set[str]] = {}
    for case in CASES:
        by_defence.setdefault(case.defence, set()).add(case.case_id)
    assert by_defence[PROMPT_ONLY] == {"S1", "S2"}
    assert by_defence[NEITHER] == {"S6"}
    assert len(by_defence[MACHINE]) == 12
    assert sum(len(ids) for ids in by_defence.values()) == 15


# --- what the two prompt-only cases actually cost --------------------------------


def test_s1_the_over_quoted_value_becomes_a_real_llm_supported_fact(
        site_a_conn, tmp_path):
    """S1's consequence, not just its verdict.

    `76` §9.1: *"The prompt is the only thing standing between a 3B model and a
    folder named `PHYS1401 Problem Set 4`."* The verdict alone does not show that --
    an accepted verdict that wrote nothing would be harmless. This runs the
    consequence and reads P6's own table back.
    """
    world = _world(site_a_conn, tmp_path, released=DEFAULT_RELEASED)
    over_quoted = _response(_claim(
        "subject", DEFAULT_RELEASED, key=world.released_key, span=DEFAULT_RELEASED))

    assert _judge(world, over_quoted, apply=True) == ONE_ACCEPT

    rows = [row for row in facts_for_file(
        site_a_conn, world.file_id, world.content_hash)
        if row["field_key"] == "subject"]
    assert [row["canonical_value"] for row in rows] == [DEFAULT_RELEASED]
    assert rows[0]["reliability_state"] == "llm_supported"
    assert rows[0]["active"] == 1


def test_s1_check_three_does_not_bound_the_value_at_all(site_a_conn, tmp_path):
    """`82` §3 calls R11 *"stated, never enforced"*. Verified against the live oracle.

    Not through the validator this time but directly against `cli.normalize_for_model`,
    because the claim under test is about the check itself: for `subject` it collapses
    whitespace, strips the identifier's separator, and returns whatever is left, at
    any length.
    """
    assert normalize_for_model("subject", DEFAULT_RELEASED) == DEFAULT_RELEASED
    assert normalize_for_model("subject", "a" * 300) == "a" * 300
    # `instructor` has no slot at all, so the check rejects only the empty string
    # and the non-string.
    assert normalize_for_model("instructor", "a whole paragraph of prose") == (
        "a whole paragraph of prose")
    assert normalize_for_model("instructor", "") is None
    assert normalize_for_model("instructor", 4) is None


def test_s2_the_value_is_never_compared_to_the_evidence_it_cites(
        site_a_conn, tmp_path):
    """The widest hole the fifteen imply, stated on its own.

    §3.6's check 2 asks whether the CITATION holds. Check 3 asks whether the VALUE
    normalizes. Nothing asks whether the value has anything to do with the citation,
    so a real span from the released text will carry any value at all -- including a
    string that appears nowhere in the dossier. S2 is this failure with a plausible
    value; here it is with an impossible one, so the absence of the check cannot be
    mistaken for the check being lenient.
    """
    world = _world(
        site_a_conn, tmp_path,
        released="Prepared for the committee in the autumn, with notes.")
    unrelated = _response(_claim(
        "instructor", "Dr Nobody", key=world.released_key, span="the committee",
        why="the committee named the instructor"))

    assert _judge(world, unrelated) == ONE_ACCEPT


def test_s6_one_course_becomes_two_value_rows(site_a_conn, tmp_path):
    """`76` §9.2, measured: check 4 canonicalises and the writer does not.

    The model answers correctly -- it copied the evidence's spelling, which is
    exactly what R12 and the draft's rule 5 ask for -- and check 4 correctly does
    not fire, because `contradicts_stronger` canonicalises both sides. Then
    `apply_verdict` stores `proposal.value` raw. Two rows, one course.
    """
    world = _world(
        site_a_conn, tmp_path, released="PHYS 1401",
        stronger=("subject", "PHYS1401"))
    faithful = _response(_claim(
        "subject", "PHYS 1401", key=world.released_key, span="PHYS 1401"))

    assert _judge(world, faithful, apply=True) == ONE_ACCEPT

    stored = [row["canonical_value"] for row in site_a_conn.execute(
        'SELECT canonical_value FROM "values" WHERE field_key = ? '
        "ORDER BY canonical_value", ("subject",))]
    assert stored == ["PHYS 1401", "PHYS1401"]


# --- two orderings the fifteen do not settle -------------------------------------


def test_a_fabricated_evidence_ref_is_not_found_rather_than_not_in_dossier(
        site_a_conn, tmp_path):
    """S9's neighbour, and the one place `76` §7 leaves the reason ambiguous.

    S9's row names `CITATION_NOT_IN_DOSSIER`, which is what a key that IS one of
    P6's observations but was not released produces. A key P6 never observed fails
    the COARSE check first (`fact_validation.py:217`) and comes back as
    `CITATION_NOT_FOUND`. Both reach P6 as one word -- `citation_absent_from_evidence`
    -- so the difference is only visible in the P8 record, and it is worth pinning
    because the two say different things about where the model went wrong.
    """
    world = _world(site_a_conn, tmp_path)
    invented = _response(_claim(
        "subject", "PHYS1401", key="obs:never-observed", span="PHYS1401"))

    assert _judge(world, invented) == _one_reject(CITATION_NOT_FOUND)


def test_declining_costs_exactly_one_unresolved_row(site_a_conn, tmp_path):
    """R19's claim, priced. Abstention is `ABSTAIN`, and it writes one visible row.

    `76` §5: *"The cost of declining is one `unresolved` row that a person can see.
    The cost of guessing is an `llm_supported` fact that becomes a folder name."*
    Both halves are now measured -- this one and `test_s1_...` above.
    """
    world = _world(site_a_conn, tmp_path)
    declined = _response(_decline("subject", "no released value names a course"))

    assert _judge(world, declined, apply=True) == ONE_ABSTAIN

    rows = unresolved_for_file(site_a_conn, world.file_id, world.content_hash)
    assert [(row["field_key"], row["reason"]) for row in rows] == [
        ("subject", "model_returned_unknown")]
    assert facts_for_file(site_a_conn, world.file_id, world.content_hash) == []
