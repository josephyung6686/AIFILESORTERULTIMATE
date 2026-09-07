# tests/p8/test_p8_a_fact_schema_failures.py
"""R-99, second half: which rule a parsed-but-invalid A_fact response actually breaks.

**The measurement.** Sixteen responses on a cloud run over the owner's corpus were
`SCHEMA_INVALID` at site A. Seven did not decode (`test_p8_json_decode_at_the_tail`);
nine decoded, carried a `claims` list whose entries had `payload.field`,
`payload.value` or `unknown`, and `citations`, and were destroyed anyway. Which rule
each broke could not be read off the record: every one was one verdict, `claim_ref =
"schema"`, reason `SCHEMA_INVALID`.

**So this file is the matrix.** Every response below mirrors the ratified A_fact
template's own SHAPE section -- and mirrors it literally, with no `claim_ref`, because
the template does not print one -- then deviates in exactly one way, and is run through
the real `sites.dispatch` over a real P6 world. What each deviation costs is recorded
beside it: some destroy the whole response (template rule 11, *"One malformed claim
destroys every claim in the answer"*), some reject one claim, and some are accepted.
The `claim_ref` now names the rule, so the NEXT run answers the question this one
could not.

**Nothing is widened here.** Where the ratified `a_fact_response_schema.json` and the
code disagree, the disagreement is pinned and reported: as a fact where the schema
demands something the template never asked the model for, and as a strict xfail where
the code accepts something both the schema and the template forbid.
"""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path

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
from facts.llm_seam import build_request
from llm_harness.fact_validation import FactValidationDependencies
from llm_harness.fixtures import FIXTURE_HANDLE_KEY
from llm_harness.records import Dossier, EvidenceItem, ReleasedEvidence
from llm_harness.schema import create_llm_schema
from llm_harness.sites import FactSiteDependencies, SiteDependencies, dispatch
from llm_harness.wire_handles import wire_ref
from llm_harness.vocabulary import (
    A_FACT,
    ABSTAIN,
    ACCEPT_DIRECT,
    CITATION_NOT_FOUND,
    DIRECT_ANCHOR,
    REDUCTION_NONE,
    REJECT,
    REMAINS_AMBIGUOUS,
    SCHEMA_INVALID,
    VALUE_NOT_NORMALIZABLE,
)

from cli import contradicts_stronger, normalize_for_model, normalize_for_review

CLOCK = "2026-09-07T12:00:00+00:00"
RELEASED = "PHYS 1401 syllabus, Spring 2026"
ADDRESS = "heading:course"
POLICY = "policy-1"

LIBRARY = Path(__file__).resolve().parents[2] / "src" / "llm_harness" / "library"
RESPONSE_SCHEMA = json.loads(
    (LIBRARY / "a_fact_response_schema.json").read_text(encoding="utf-8"))
TEMPLATE_TEXT = (
    LIBRARY / "a_fact_template_folder_levels.txt").read_text(encoding="utf-8")


# --- a real Site A world ----------------------------------------------------------


@dataclass(frozen=True)
class World:
    conn: object
    dossier: Dossier
    dependencies: SiteDependencies
    resolver: object
    handle: str


@pytest.fixture()
def site_a_conn(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    create_llm_schema(conn)
    return conn


@pytest.fixture()
def world(site_a_conn, tmp_path) -> World:
    path = tmp_path / "Syllabus.pdf"
    path.write_bytes(b"PHYS 1401 syllabus")
    file_id = record_file(
        site_a_conn, path, filename="Syllabus.pdf",
        normalized_filename="syllabus.pdf", extension=".pdf", observed_size=18,
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(site_a_conn, file_id)["content_hash"]
    record_run(site_a_conn, ExtractionRun(
        run_id="r-1", file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=RELEASED,
        location=Location("heading", (Segment("field", label="heading"),)),
        occurrence_count=1, observed_at=CLOCK, reliability="possible", run_id="r-1")
    record_observation(site_a_conn, observation)
    key = observation.observation_key
    request = build_request(
        site_a_conn, file_id=file_id, content_hash=content_hash,
        activation_signals=ActivationSignals(signals=(
            ActivationSignal(schema_id="academic", activates=lambda rows: True),)),
        normalizers={})
    dossier = Dossier(
        dossier_id="dossier-schema", call_site=A_FACT, subject_ref=file_id,
        eligibility_reason=REMAINS_AMBIGUOUS, plan_version=None,
        policy_version=POLICY, allowed_vocabulary=tuple(request.allowlist),
        evidence_items=(EvidenceItem(
            evidence_ref=key, kind="excerpt", location="body",
            excerpt_span=(0, len(RELEASED)), reliability_state="direct",
            basis=DIRECT_ANCHOR),),
        conflicts=(),
        released_evidence=(ReleasedEvidence(
            observation_key=key, address=ADDRESS, value=RELEASED, zone="body"),),
        max_dossier_tokens=4000, reduction_rung=REDUCTION_NONE, release_id="rel-1")
    return World(
        conn=site_a_conn, dossier=dossier,
        dependencies=SiteDependencies(
            fact=FactSiteDependencies(
                fact_request=request,
                fact_dependencies=FactValidationDependencies(
                    normalize=normalize_for_model,
                    contradicts=contradicts_stronger,
                    normalize_for_review=normalize_for_review)),
            placement=None, residual=None, template=None),
        resolver=lambda asked: RELEASED if asked == key else None,
        handle=wire_ref(key, key=FIXTURE_HANDLE_KEY))


def _judge(world: World, body) -> tuple[tuple[str, tuple[str, ...], str], ...]:
    """Every verdict the real dispatcher returns, with the address it recorded."""
    if not isinstance(body, (bytes, bytearray)):
        body = json.dumps(body, separators=(",", ":")).encode("utf-8")
    result = dispatch(
        world.conn, world.dossier, body, site_dependencies=world.dependencies,
        evidence_resolver=world.resolver, contradicts=contradicts_stronger,
        model_id="schema-model", prompt_fingerprint="sha256:schema",
        dossier_builder="schema-suite", release_audit_id=None,
        policy_version=POLICY, apply_consequence=False,
        handle_key=FIXTURE_HANDLE_KEY)
    assert isinstance(result, tuple), result
    verdicts, _report = result
    return tuple((v.outcome, v.reasons, v.claim_ref) for v in verdicts)


# --- the shapes the template prints -----------------------------------------------


def _cite(world: World) -> dict:
    return {"evidence_ref": world.handle, "cited_span": "PHYS 1401",
            "why_it_supports": "the heading names it"}


def _support(world: World) -> dict:
    return {"payload": {"field": "subject", "value": "PHYS 1401"},
            "citations": [_cite(world)]}


def _decline() -> dict:
    return {"payload": {"field": "school"},
            "unknown": {"insufficiency_statement": "no released value names one"}}


def test_the_two_shapes_this_file_deviates_from_are_the_template_s_own(world):
    """The baseline is the prompt's text, not a shape this file invented.

    The template prints both moves literally, and neither printed line carries a
    `claim_ref`. Every case below starts from these bytes.
    """
    assert '{"claims":[{"payload":{"field":"a key copied from allowed_vocabulary",' \
        '"value":"the value, as a JSON string"},"citations":[' in TEMPLATE_TEXT
    assert '"unknown":{"insufficiency_statement":' in TEMPLATE_TEXT
    assert '"claim_ref"' not in TEMPLATE_TEXT

    assert _judge(world, {"claims": [_support(world)]}) == (
        (ACCEPT_DIRECT, (), "subject"),)
    assert _judge(world, {"claims": [_decline()]}) == ((ABSTAIN, (), "school"),)


# --- the matrix -------------------------------------------------------------------


def _cases(world: World):
    """One deviation each, with what it costs and the rule it breaks.

    `(case, claim builder, expected verdicts)`. A `claim_ref` of the form
    `claim-N:<rule>` means the whole response died on claim N for that rule; a field
    key means one claim was judged and the rest of the response survived.
    """
    cite = _cite(world)
    support = _support(world)
    return (
        # --- rule 3 and the payload's own required keys: the response dies ---------
        ("value omitted", {"payload": {"field": "subject"}, "citations": [cite]},
         ((REJECT, (SCHEMA_INVALID,), "claim-0:payload_value_missing"),)),
        ("value null",
         {"payload": {"field": "subject", "value": None}, "citations": [cite]},
         ((REJECT, (SCHEMA_INVALID,), "claim-0:payload_value_missing"),)),
        ("field omitted",
         {"payload": {"value": "PHYS 1401"}, "citations": [cite]},
         ((REJECT, (SCHEMA_INVALID,), "claim-0:payload_field_missing"),)),
        ("payload omitted", {"citations": [cite]},
         ((REJECT, (SCHEMA_INVALID,), "claim-0:payload_field_missing"),)),
        ("payload sent as a list",
         {"payload": [{"field": "subject", "value": "PHYS 1401"}],
          "citations": [cite]},
         ((REJECT, (SCHEMA_INVALID,), "claim-0:payload_field_missing"),)),
        # --- rule 10, the `unknown` key -------------------------------------------
        ("unknown as a sentence",
         {"payload": {"field": "school"}, "unknown": "no school is named"},
         ((REJECT, (SCHEMA_INVALID,), "claim-0:unknown_not_an_object"),)),
        ("unknown false", dict(support, unknown=False),
         ((REJECT, (SCHEMA_INVALID,), "claim-0:unknown_not_an_object"),)),
        # --- rule 6, the citation --------------------------------------------------
        ("citations as one object",
         {"payload": {"field": "subject", "value": "PHYS 1401"}, "citations": cite},
         ((REJECT, (SCHEMA_INVALID,), "claim-0:citations_not_a_list"),)),
        ("a citation that is a bare reference",
         {"payload": {"field": "subject", "value": "PHYS 1401"},
          "citations": [world.handle]},
         ((REJECT, (SCHEMA_INVALID,), "claim-0:citation_malformed"),)),
        ("a citation with neither span nor metadata field",
         {"payload": {"field": "subject", "value": "PHYS 1401"},
          "citations": [{"evidence_ref": world.handle, "why_it_supports": "w"}]},
         ((REJECT, (SCHEMA_INVALID,), "claim-0:citation_malformed"),)),
        ("a citation with both",
         {"payload": {"field": "subject", "value": "PHYS 1401"},
          "citations": [{"evidence_ref": world.handle, "cited_span": "PHYS 1401",
                         "metadata_field_name": ADDRESS, "why_it_supports": "w"}]},
         ((REJECT, (SCHEMA_INVALID,), "claim-0:citation_malformed"),)),
        ("a citation with an empty evidence_ref",
         {"payload": {"field": "subject", "value": "PHYS 1401"},
          "citations": [{"evidence_ref": "", "cited_span": "PHYS 1401",
                         "why_it_supports": "w"}]},
         ((REJECT, (SCHEMA_INVALID,), "claim-0:citation_malformed"),)),
        ("a citation with no why_it_supports",
         {"payload": {"field": "subject", "value": "PHYS 1401"},
          "citations": [{"evidence_ref": world.handle, "cited_span": "PHYS 1401"}]},
         ((REJECT, (SCHEMA_INVALID,), "claim-0:citation_malformed"),)),
        # --- one claim rejected, the response alive -------------------------------
        ("an empty value",
         {"payload": {"field": "subject", "value": ""}, "citations": [cite]},
         ((REJECT, (VALUE_NOT_NORMALIZABLE,), "subject"),)),
        ("a value emitted as a number",
         {"payload": {"field": "subject", "value": 1401}, "citations": [cite]},
         ((REJECT, (VALUE_NOT_NORMALIZABLE,), "subject"),)),
        ("an empty citations list",
         {"payload": {"field": "subject", "value": "PHYS 1401"}, "citations": []},
         ((REJECT, (CITATION_NOT_FOUND,), "subject"),)),
    )


def test_the_matrix_of_one_deviation_at_a_time(world):
    """Every row, run against the validator that actually runs.

    Read the `claim_ref` column: it is what the record could not say before. Eleven
    of these sixteen shapes destroy the whole response and five do not, and until
    now every one of the eleven arrived as the same four words.
    """
    for case, claim, expected in _cases(world):
        assert _judge(world, {"claims": [claim]}) == expected, case


def test_a_malformed_claim_names_which_claim_it_was(world):
    """Rule 11's cost, addressed. A good claim beside a bad one still loses, and the
    record now says the loss was claim 1 and not claim 0."""
    good = _support(world)
    bad = {"payload": {"field": "school"}, "citations": [_cite(world)]}

    assert _judge(world, {"claims": [good, bad]}) == (
        (REJECT, (SCHEMA_INVALID,), "claim-1:payload_value_missing"),)


def test_two_claims_about_one_field_name_the_field(world):
    """Template rule 8, and the address says which field was answered twice."""
    support = _support(world)
    assert _judge(world, {"claims": [support, copy.deepcopy(support)]}) == (
        (REJECT, (SCHEMA_INVALID,), "claims:duplicate_field:subject"),)


@pytest.mark.parametrize("body,expected_ref", [
    ({"claims": []}, "schema:claims_empty"),
    ({"claims": {"payload": {"field": "subject"}}}, "schema:claims_not_a_list"),
    ([{"payload": {"field": "subject"}}], "schema:not_an_object"),
    ({"claims": ["subject"]}, "claim-0:not_an_object"),
])
def test_a_response_whose_envelope_is_wrong_names_the_envelope(
        world, body, expected_ref):
    assert _judge(world, body) == ((REJECT, (SCHEMA_INVALID,), expected_ref),)


# --- what the ratified schema says, and where the code differs from it ------------


def test_the_ratified_schema_cannot_express_template_rule_8(world):
    """CONTRACT GAP. `claims` has no uniqueness constraint anywhere in the schema.

    *"Never send two claims about the same field: that destroys your whole answer"*
    is template rule 8 and nothing else. So the validator destroys a response the
    ratified `a_fact_response_schema.json` would accept, and the schema's own header
    -- *"where the two could differ, the template is what the model was told and this
    is what the validator enforces, and they are meant to say the same thing"* --
    is not true of this rule. Recorded, not changed: the code follows the template,
    which is the document the model was actually given.
    """
    claims = RESPONSE_SCHEMA["properties"]["claims"]
    assert "uniqueItems" not in claims
    assert "field" not in json.dumps(claims.get("items", {}))
    assert "Never send two claims about the same field" in TEMPLATE_TEXT

    support = _support(world)
    assert _judge(world, {"claims": [support, copy.deepcopy(support)]})[0][1] == (
        SCHEMA_INVALID,)


#: The four places the ratified schema closes the object and the template never
#: mentions a limit. `additionalProperties: false` says "no other keys"; the template
#: prints a shape and says nothing about extra ones, and the paragraph that DOES close
#: a key set closes the DOSSIER's ("has these keys and no others"), not the response's.
CLOSED_IN_THE_SCHEMA: tuple[tuple[str, ...], ...] = (
    (),
    ("$defs", "claim"),
    ("$defs", "payload"),
    ("$defs", "citation"),
    ("$defs", "unknown"),
)


@pytest.mark.parametrize("path", CLOSED_IN_THE_SCHEMA, ids=lambda p: "/".join(p) or "root")
def test_the_schema_closes_four_objects_the_template_never_closes(path):
    """CONTRACT GAP, and it is the one the task names: the schema demands something
    the template does not ask the model for."""
    node = RESPONSE_SCHEMA
    for step in path:
        node = node[step]
    assert node["additionalProperties"] is False
    assert "no other keys" not in TEMPLATE_TEXT
    assert "additional" not in TEMPLATE_TEXT.lower()


@pytest.mark.parametrize("case,claim_extra,payload_extra", [
    ("claim_ref", {"claim_ref": "c1"}, {}),
    ("a confidence the model was told not to send", {}, {"confidence": 0.9}),
])
def test_an_extra_key_is_accepted_by_the_code_and_refused_by_the_schema(
        world, case, claim_extra, payload_extra):
    """The same gap, measured from the code's side. Nothing is widened or narrowed."""
    claim = _support(world)
    claim.update(claim_extra)
    claim["payload"].update(payload_extra)

    assert _judge(world, {"claims": [claim]}) == ((ACCEPT_DIRECT, (), "subject"),)


def test_a_top_level_key_beside_claims_is_accepted_by_the_code(world):
    assert _judge(world, {"claims": [_support(world)], "reasoning": "I read it"}) == (
        (ACCEPT_DIRECT, (), "subject"),)


def test_claim_ref_is_forbidden_by_the_ratified_schema_and_read_by_the_validator():
    """CONTRACT GAP, and the sharpest one: two documents in this repo disagree.

    `a_fact_response_schema.json` closes the claim object, so `claim_ref` is not a
    legal key. `llm_harness.validation`'s module docstring publishes the recorded
    response shape with `claim_ref` in it as optional, `_validate_claim` reads it, and
    this repo's own stress-case fixtures send it. The A_fact template mentions it
    nowhere. Whichever way the owner rules, one of the three has to move.
    """
    assert "claim_ref" not in RESPONSE_SCHEMA["$defs"]["claim"]["properties"]
    assert RESPONSE_SCHEMA["$defs"]["claim"]["additionalProperties"] is False

    from llm_harness import validation

    assert '"claim_ref": str,' in validation.__doc__
    assert "claim_ref" not in TEMPLATE_TEXT


# --- the declining branch: three shapes the code accepts and both documents forbid -

#: `sites._proposal` returns as soon as it sees a `unknown` object, before it looks at
#: anything else on the claim. So a claim that DECLINES and ASSERTS at the same time is
#: read as a decline and everything else it carried is dropped -- the same shape of
#: defect as `104` R-16 at site B, where the model's four answers were validated and
#: three of them thrown away.
#:
#: All three are refused by the ratified schema's `claim.oneOf` and by template rule
#: 10 (*"A claim carries either citations or unknown, never both and never neither. A
#: declining claim carries no value and no citations"*), and all three are ABSTAIN
#: today. They are xfails and not a fix because the fix has a measured cost and is the
#: owner's to weigh: rule 11 makes the honest refusal destroy the WHOLE response, and
#: `105` §1.5 measured that at one response in fourteen. Constitution rule 2 is that
#: coverage is sacred, so trading three abstentions for a destroyed answer is a ruling,
#: not a tidy-up.
DECLINE_AND_ASSERT: tuple[tuple[str, dict], ...] = (
    ("a decline that also cites",
     {"payload": {"field": "school"},
      "unknown": {"insufficiency_statement": "none"},
      "citations": [{"evidence_ref": "handle", "cited_span": "PHYS 1401",
                     "why_it_supports": "w"}]}),
    ("a decline that also carries a value",
     {"payload": {"field": "school", "value": "Columbia"},
      "unknown": {"insufficiency_statement": "none"}}),
    ("a decline whose statement is empty",
     {"payload": {"field": "school"}, "unknown": {"insufficiency_statement": ""}}),
)


@pytest.mark.parametrize("case,claim", DECLINE_AND_ASSERT,
                         ids=[case for case, _claim in DECLINE_AND_ASSERT])
@pytest.mark.xfail(strict=True, reason=(
    "104 R-99: `sites._proposal` reads the `unknown` branch and returns before it "
    "looks at `citations` or `payload.value`, so a claim that declines and asserts "
    "at once is recorded as an abstention and the assertion is dropped. The ratified "
    "response schema's `claim.oneOf` and template rule 10 both forbid the shape. "
    "Whether the honest refusal is worth rule 11's cost -- one malformed claim "
    "destroys the whole response, measured at 1 in 14 -- is the owner's ruling."))
def test_a_claim_that_declines_and_asserts_at_once_should_not_be_an_abstention(
        world, case, claim):
    claim = copy.deepcopy(claim)
    for citation in claim.get("citations", ()):
        citation["evidence_ref"] = world.handle

    assert _judge(world, {"claims": [claim]})[0][:2] == (REJECT, (SCHEMA_INVALID,))


def test_the_three_shapes_above_are_abstentions_today(world):
    """The xfails' twin, green, so the current behaviour is on the record too."""
    for case, claim in DECLINE_AND_ASSERT:
        claim = copy.deepcopy(claim)
        for citation in claim.get("citations", ()):
            citation["evidence_ref"] = world.handle
        assert _judge(world, {"claims": [claim]}) == ((ABSTAIN, (), "school"),), case


def test_the_schema_and_the_template_agree_that_those_three_are_illegal():
    """Both documents, read as data, so the xfails above rest on the contract and not
    on this file's opinion."""
    decline = next(branch for branch in RESPONSE_SCHEMA["$defs"]["claim"]["oneOf"]
                   if branch["title"] == "decline")
    assert decline["not"] == {"required": ["citations"]}
    assert decline["properties"]["payload"]["not"] == {"required": ["value"]}
    assert RESPONSE_SCHEMA["$defs"]["unknown"]["properties"][
        "insufficiency_statement"]["minLength"] == 1
    assert ("A claim carries either \"citations\" or \"unknown\", never both and "
            "never neither.") in TEMPLATE_TEXT
    assert "A declining claim carries no value and no citations." in TEMPLATE_TEXT
