# tests/p8/test_p8_json_decode_at_the_tail.py
"""R-99, first half: a response that did not decode says WHERE, and is repaired once.

**The measurement.** A cloud run over the owner's corpus produced sixteen
`SCHEMA_INVALID` verdicts at site A. Seven of them were JSON that did not decode --
the output breaking in the last few bytes on a bracket -- and nine were JSON that
decoded and did not fit the shape. The record could not tell them apart: every one was
one verdict, `claim_ref="schema"`, reason `SCHEMA_INVALID`. Separating them took the
stored bytes and a person.

**What changes and what does not.** The reason code is unchanged. `vocabulary.py`
records the last reason-code addition in full -- *"THE FOURTH SITE-A CODE, ADDED
2026-09-02 WITH THE OWNER'S APPROVAL"* -- so the codes are the owner's to add and
`SCHEMA_INVALID` already says "this did not fit the shape". What was missing is the
address, and `claim_ref` is the address: for a decode failure there is no claim to
name, so it names the byte instead.

**The one repair, and why it is a proof and not a guess.** `104` §13.5: a rule may
reject only a structurally invalid answer. A complete JSON document followed by one
stray closing bracket is not structurally invalid -- a closing bracket cannot open,
name or extend anything, so nothing inside the document depends on it. `raw_decode`
is what proves the document complete. Everything else is refused, including both
shapes `105` measured (§5.3's `...]]}],"citations":[` and §4.7's `"merge_terms":[]}],`),
because those are mis-closes in the MIDDLE with content still to come, and mending one
means choosing which of several documents the model meant. `105` §4.7's own fix was to
reorder the payload so its last key is a scalar, not to mend the bytes.
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
from facts.llm_seam import build_request
from llm_harness.fact_validation import FactValidationDependencies
from llm_harness.fixtures import FIXTURE_HANDLE_KEY
from llm_harness.records import Dossier, EvidenceItem, ReleasedEvidence
from llm_harness.schema import create_llm_schema
from llm_harness.sites import FactSiteDependencies, SiteDependencies, dispatch
from llm_harness.validation import decode_response
from llm_harness.vocabulary import (
    A_FACT,
    ACCEPT_DIRECT,
    DIRECT_ANCHOR,
    REDUCTION_NONE,
    REJECT,
    REMAINS_AMBIGUOUS,
    SCHEMA_INVALID,
)

from cli import contradicts_stronger, normalize_for_model, normalize_for_review

CLOCK = "2026-09-07T12:00:00+00:00"
MODEL = "decode-model"
PROMPT_FP = "sha256:decode-fingerprint"
POLICY = "policy-1"
RELEASED = "PHYS 1401 syllabus"

#: The support shape the ratified A_fact template prints, byte for byte, with the
#: worlds' own key filled in below. No `claim_ref`: the template's SHAPE section does
#: not show one, so a response that mirrors the prompt does not send one.
SUPPORT = ('{"claims":[{"payload":{"field":"subject","value":"PHYS 1401"},'
           '"citations":[{"evidence_ref":"%s","cited_span":"PHYS 1401",'
           '"why_it_supports":"the heading names it"}]}]}')


# --- the decoder, asked directly ---------------------------------------------------


def test_a_complete_document_decodes_with_no_address():
    value, ref = decode_response(b'{"claims":[]}')
    assert value == {"claims": []}
    assert ref is None


@pytest.mark.parametrize("surplus", ["]", "}", "]\n", "  }  "])
def test_one_stray_closing_bracket_after_a_complete_document_is_inert(surplus):
    """The repair, and its proof: the prefix already parsed as a whole document."""
    document = '{"claims":[{"payload":{"field":"subject"}}]}'
    value, ref = decode_response((document + surplus).encode("utf-8"))

    assert ref is None
    assert value == json.loads(document)


@pytest.mark.parametrize("tail", ["]]", "}}", "]}", "],", '],"x"', "] junk"])
def test_more_than_one_stray_character_is_refused_and_not_mended(tail):
    """Two brackets is a guess about which document was meant; one is not."""
    document = '{"claims":[{"payload":{"field":"subject"}}]}'
    value, ref = decode_response((document + tail).encode("utf-8"))

    assert value is None
    assert ref is not None and ref.startswith("schema:json_decode@byte-")


#: The two shapes `105` measured, and neither is a trailing surplus. The first is
#: §5.3's E defect -- the payload's last key is a populated array and the model closes
#: it one bracket too many, with `"citations"` still to come. The second is §4.7's B
#: defect, one bracket short in the same position. Both break in the MIDDLE.
MEASURED_MISCLOSES: tuple[str, ...] = (
    '{"claims":[{"payload":{"field":"subject","value":"x",'
    '"example_label_chains":[["a","b"]]]}],'
    '"citations":[{"evidence_ref":"k","cited_span":"x","why_it_supports":"w"}]}]}',
    '{"claims":[{"payload":{"field":"subject","value":"x","merge_terms":[]}],'
    '"citations":[{"evidence_ref":"k","cited_span":"x","why_it_supports":"w"}]}]}',
)


@pytest.mark.parametrize("body", MEASURED_MISCLOSES)
def test_the_two_measured_misclose_shapes_are_recorded_and_refused(body):
    """`105` §5.3 and §4.7's own bytes. There is no unambiguous repair for either."""
    with pytest.raises(ValueError):
        json.loads(body)

    value, ref = decode_response(body.encode("utf-8"))

    assert value is None
    assert ref is not None and ref.startswith("schema:json_decode@byte-")


def test_a_document_missing_its_last_bracket_is_refused_with_the_offset():
    """A MISSING bracket is not repaired, and this is the sentence that says so.

    Appending one means choosing between `]` and `}`, and between one and several.
    The refusal is recorded with the byte the decoder ran out on, which for a
    truncation is the end of the bytes.
    """
    body = '{"claims":[{"payload":{"field":"subject","value":"PHYS 1401"}}]'
    value, ref = decode_response(body.encode("utf-8"))

    assert value is None
    assert ref == f"schema:json_decode@byte-{len(body)}"


def test_the_offset_is_counted_in_bytes_and_not_in_characters():
    """`JSONDecodeError.pos` counts characters; the record names the byte somebody
    would open, which is a different number the moment the response is not ASCII."""
    body = '{"claims":[{"payload":{"field":"subject","value":"Économie"}}] ]]'
    with pytest.raises(json.JSONDecodeError) as raised:
        json.loads(body)
    characters = raised.value.pos
    in_bytes = len(body[:characters].encode("utf-8"))

    value, ref = decode_response(body.encode("utf-8"))

    assert value is None
    assert in_bytes != characters
    assert ref == f"schema:json_decode@byte-{in_bytes}"


def test_bytes_that_are_not_utf8_are_refused_at_the_byte_that_is_not():
    value, ref = decode_response(b'{"claims":[{"payload":{"field":"\xff"}}]}')

    assert value is None
    assert ref == "schema:json_decode@byte-32"


def test_a_preamble_and_a_code_fence_are_still_refused_outright():
    """Stress case S12, unmoved: a fence is not whitespace and is not a bracket."""
    value, ref = decode_response(b'Here is my answer:\n```json\n{"claims":[]}\n```')

    assert value is None
    assert ref == "schema:json_decode@byte-0"


# --- and at the site, over a real world --------------------------------------------


@dataclass(frozen=True)
class World:
    conn: object
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
        dossier_id="dossier-decode", call_site=A_FACT, subject_ref=file_id,
        eligibility_reason=REMAINS_AMBIGUOUS, plan_version=None,
        policy_version=POLICY, allowed_vocabulary=tuple(request.allowlist),
        evidence_items=(EvidenceItem(
            evidence_ref=key, kind="excerpt", location="body",
            excerpt_span=(0, len(RELEASED)), reliability_state="direct",
            basis=DIRECT_ANCHOR),),
        conflicts=(),
        released_evidence=(ReleasedEvidence(
            observation_key=key, address="heading:course", value=RELEASED,
            zone="body"),),
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
        released_key=key)


def _verdicts(world: World, response_bytes: bytes):
    result = dispatch(
        world.conn, world.dossier, response_bytes,
        site_dependencies=world.dependencies, evidence_resolver=world.resolver,
        contradicts=contradicts_stronger, model_id=MODEL,
        prompt_fingerprint=PROMPT_FP, dossier_builder="decode-suite",
        release_audit_id=None, policy_version=POLICY, apply_consequence=False,
        handle_key=FIXTURE_HANDLE_KEY)
    assert isinstance(result, tuple), result
    verdicts, _report = result
    return verdicts


def _handled(world: World) -> str:
    """What the model was shown for this observation: the keyed handle, never the P4
    key. `wire_handles` says why -- an un-keyed digest on the wire was reversed."""
    from llm_harness.wire_handles import wire_ref

    return wire_ref(world.released_key, key=FIXTURE_HANDLE_KEY)


def test_a_response_with_one_surplus_bracket_is_judged_and_not_destroyed(world):
    """The seven, at the site that refused them. The claims inside were answerable."""
    body = (SUPPORT % _handled(world)).encode("utf-8")

    assert [(v.outcome, v.reasons) for v in _verdicts(world, body + b"]")] == [
        (ACCEPT_DIRECT, ())]


def test_a_truncated_response_is_one_refusal_that_names_the_byte(world):
    body = (SUPPORT % _handled(world))[:-2].encode("utf-8")
    verdicts = _verdicts(world, body)

    assert len(verdicts) == 1
    assert (verdicts[0].outcome, verdicts[0].reasons) == (REJECT, (SCHEMA_INVALID,))
    assert verdicts[0].claim_ref == f"schema:json_decode@byte-{len(body)}"


def test_the_verdict_id_still_addresses_this_response(world):
    """`_addressed_to_the_response` appends the digest, so two decode failures over
    one dossier are two rows and not a primary-key collision."""
    first = _verdicts(world, b'{"claims":[{"payload":{"field":"subject"}}]')
    second = _verdicts(world, b'{"claims":[{"payload":{"field":"school"}}]')

    assert first[0].verdict_id != second[0].verdict_id
    assert first[0].dossier_id == second[0].dossier_id
