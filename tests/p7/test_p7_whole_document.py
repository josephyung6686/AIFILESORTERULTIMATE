# tests/p7/test_p7_whole_document.py
"""CR-07: a whole document reached the wire as one span-less excerpt.

`extractors/structured_text.py` emits the whole text of a document as ONE span-less
`body` observation at the empty container path, beside the `text_units` row holding
the same characters. `resolve.materialise` resolved that address to `raw_value` --
the document -- and reported `unit_length=None`, and `items.is_whole_document` read
a missing length as "not a whole document". So §8.4's *"should not send full
documents where a short heading or OCR excerpt is enough to resolve the question"*
never fired, and `complete_extracted_text` -- member 2 of `ALWAYS_LOCAL` -- was
releasable as an excerpt.

Reproduced twice before it was fixed. At the unit level `check_item` PASSED on a
span-less whole-document excerpt; on the live path a 278-character `.txt` through
`run_production_p1_p7` came back `Released` with `materialised_items[0].value ==
<the file's text>`.

**The fix is not a blanket refusal of span-less items, and half of this file exists
to prove it is not.** Three legitimate span-less shapes are checked below and every
one of them is still released: §2.3's spreadsheet cell (a deep container path with
no unit anywhere in the run), §2.8's EXIF field (a `field=` path in a run that emits
no text units at all), and a bounded field that sits at a path a unit DOES occupy.
The last is the sharpest: it is the only one that can tell "the value covers the
unit" apart from "a unit exists somewhere near this observation".

The distinction lives where both halves of it are in hand. `resolve.materialise` is
the only module holding the resolved value AND permitted to ask P4 for the unit at
the observation's path, so it computes the fact; `items.is_whole_document` decides
what the fact means. That is the split `check_item`'s own docstring already assigned
to the two modules.
"""
from __future__ import annotations

import hashlib
import tempfile
from dataclasses import replace
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import record_file
from evidence_shape.canonical import canonical_json
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.locator import serialize_locator
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import (
    TextUnit, new_id, record_observation, record_run, record_text_unit,
)
from extractors.safety import SafetyPolicy
from extractors.schema import create_extraction_schema
from extractors.structured_text import TextDocument, extract_structured_text
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.defaults import MORE_REDACTING
from privacy.gate import Gate
from privacy.items import (
    Excerpt, RedactedIdentifier, WholeDocumentRequested, check_item,
    is_whole_document,
)
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from privacy.release import Denied, ModelCallRequest, ModelTarget, Released, Target
from privacy.resolve import materialise
from privacy.schema import create_privacy_schema
from privacy.vocabulary import ALWAYS_LOCAL

OBSERVED_AT = "2026-09-03T09:00:00Z"
PLAN_VERSION = "plan-whole-1"
COMPONENT = "0.1.0"
CLOUD = ModelTarget(locality="cloud", model_id="a-model", provider="Acme")
#: P7's own ceiling echo. A number only a test may choose.
MAX_DOSSIER_TOKENS = 4000

#: What `structured_text.py` reads out of a `.txt` and emits whole: the document,
#: as both the run's one text unit and the raw value of one span-less observation.
DOCUMENT = (
    "PHYS 1401 syllabus. Office hours are Tuesday afternoons in room 214. "
    "Grading is 40% exams, 30% labs, 30% homework. Late work is accepted for one "
    "week with a penalty, and the final exam is cumulative."
)
#: A bounded value at a path a unit occupies. Shorter than `DOCUMENT`, which is the
#: whole of what makes it bounded.
A_HEADING = "PHYS 1401 syllabus"
#: §2.8's shape: an EXIF field. A camera make is not a document at any length.
A_CAMERA = "Canon"
#: §2.3's shape: one spreadsheet cell.
A_CELL = "4,200.00"


# --- the substrate ------------------------------------------------------------

@pytest.fixture()
def whole_conn(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    create_privacy_schema(conn)
    return conn


def _file(conn, name: str, content_hash: str) -> str:
    corpus = Path(tempfile.mkdtemp()) / "corpus"
    corpus.mkdir()
    path = corpus / name
    path.write_text(DOCUMENT)
    return record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(DOCUMENT),
        observed_timestamps=canonical_json({"modified": OBSERVED_AT}),
        parent_folder_context="corpus", mime_type="text/plain",
        detected_format="text", scan_state="scanned", materialized=True,
        content_hash=content_hash,
    )


def _observation(conn, file_id: str, *, tag: str, zone: str, container_path,
                 raw_value: str, unit_text: str | None,
                 span: TextSpan | None = None,
                 extractor: str = "structured_text",
                 source_type: str = "text_document") -> str:
    """One observation, and optionally the text unit standing at its own path.

    `unit_text=None` is the case that has no unit ANYWHERE in the run -- §2.3's cell
    and §2.8's field. A unit at a path OTHER than the observation's is written by
    passing `unit_text` with a different `container_path` through a second call.
    """
    digest = hashlib.sha256(f"{tag}:{zone}".encode()).hexdigest()
    run_id = new_id()
    location = Location(zone=zone, container_path=container_path, text_span=span)
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=digest,
        extractor_name=extractor, extractor_version="1.0.0",
        source_type=source_type, analysis_tier="native", config={},
        completeness="complete", started_at=OBSERVED_AT, observation_count=1,
    ))
    if unit_text is not None:
        record_text_unit(conn, TextUnit(
            run_id=run_id, container_path=container_path, text=unit_text))
    record_observation(conn, Observation(
        file_id=file_id, content_hash=digest, extractor_name=extractor,
        extractor_version="1.0.0", source_type=source_type, raw_value=raw_value,
        location=location, occurrence_count=1, observed_at=OBSERVED_AT,
        reliability="possible", run_id=run_id,
        context_before=None, context_after=None, context_truncated=False,
    ))
    return observation_key(
        content_hash=digest, extractor_name=extractor,
        locator=serialize_locator(location), raw_value=raw_value)


def _store_policy(conn) -> Policy:
    draft = Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode="cloud_assisted",
        consent_grants=(("area-1", "cloud_model"),),
        redaction_settings=dict(MORE_REDACTING),
        automatic_move_permissions={}, plan_version=PLAN_VERSION,
        set_at=OBSERVED_AT,
    )
    version = set_policy(
        conn, draft, component_version=COMPONENT, user_id="joseph",
        reason="whole-document test",
    )
    return replace(draft, policy_version=version)


def _classify(conn, file_id: str, content_hash: str, *, key: str) -> None:
    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash, handling_class="public_low",
        protected=False, basis="detector", evidence_refs=(key,),
        reliability_state="direct", observed_at=OBSERVED_AT,
    ))


def _gate(conn) -> Gate:
    return Gate(
        conn,
        store=ClassificationStore(conn),
        plan_version=PLAN_VERSION,
        classifier=lambda value, *, context_before=None, context_after=None: None,
        transform=lambda value, *, identifier_class: "[redacted]",
        unclassified_permits_local=False,
        scope_for=lambda file_id: "area-1",
        files_in_scope=lambda scope: (),
        component_version=COMPONENT,
        now=lambda: OBSERVED_AT,
        user_id="joseph",
    )


def _request(*, items, file_id: str) -> ModelCallRequest:
    return ModelCallRequest(
        stage="fact_resolution", target=Target(file_ids=(file_id,)),
        model_target=CLOUD, requested_items=tuple(items),
        prompt_template_id="template.under-ratification",
        prompt_fingerprint="fingerprint-whole-1",
        max_dossier_tokens=MAX_DOSSIER_TOKENS,
    )


class Item:
    """Task 7's two text-bearing kinds, as `resolve` reads them: a key and a span."""

    def __init__(self, observation_key: str, span: TextSpan | None):
        self.observation_key = observation_key
        self.span = span


@pytest.fixture()
def a_document(whole_conn):
    """`structured_text.py`'s shape exactly: `units = [text_unit(text=document.text)]`
    at the empty container path, and `emit(zone="body", raw=document.text,
    container_path=(), span=None)` beside it."""
    file_id = _file(whole_conn, "Syllabus.txt", "hash-document")
    key = _observation(whole_conn, file_id, tag="document", zone="body",
                       container_path=(), raw_value=DOCUMENT, unit_text=DOCUMENT)
    _classify(whole_conn, file_id, "hash-document", key=key)
    _store_policy(whole_conn)
    return file_id, key


# ================================================================================
# The defect: the whole document, addressed without a span
# ================================================================================

def test_the_span_less_body_address_really_does_resolve_to_the_whole_file(
        whole_conn, a_document):
    """The premise, run rather than asserted about. If `structured_text` ever stops
    emitting the document whole, this test goes red first and the refusal below
    becomes unnecessary rather than silently vacuous."""
    _file_id, key = a_document
    found = materialise(whole_conn, Item(key, None))
    assert found.value == DOCUMENT
    assert len(found.value) == len(DOCUMENT)


def test_resolve_reports_the_unit_length_of_a_span_less_whole_document(
        whole_conn, a_document):
    """CR-07's first half. The fact the refusal is taken against is measured here,
    by the only module that may ask P4 for it.

    SABOTAGE: restore `value, unit_length = observation.raw_value, None` in
    `resolve.materialise`'s span-less branch and this goes red.
    """
    _file_id, key = a_document
    assert materialise(whole_conn, Item(key, None)).unit_length == len(DOCUMENT)


def test_a_span_less_whole_document_is_a_whole_document(whole_conn, a_document):
    """CR-07's second half, and the line the reproduction printed as `False`.

    SABOTAGE: restore `if span is None or unit_length is None: return False` in
    `items.is_whole_document` and this goes red.
    """
    _file_id, key = a_document
    item = Excerpt(observation_key=key, span=None, reason="the whole thing")
    assert is_whole_document(item, unit_length=len(DOCUMENT)) is True


def test_check_item_refuses_it_and_the_message_survives_the_missing_span(
        whole_conn, a_document):
    """The refusal must be a refusal, not an `AttributeError`.

    `check_item`'s message read `item.span.start`, which does not exist on the item
    this refusal now fires for; `_postcheck_items` catches `WholeDocumentRequested`
    only, so a crash there would leave `Gate.release` raising instead of denying.

    SABOTAGE: put `f"span {item.span.start}-{item.span.end} covers"` back
    unconditionally and this goes red with `AttributeError`.
    """
    _file_id, key = a_document
    item = Excerpt(observation_key=key, span=None, reason="the whole thing")
    with pytest.raises(WholeDocumentRequested) as caught:
        check_item(item, unit_length=len(DOCUMENT), zone="body", protected=False,
                   sensitive_keys=frozenset(), allow_unratified=True,
                   suspension_permits_self_description=False)
    assert str(len(DOCUMENT)) in str(caught.value)
    assert "full documents" in str(caught.value)


def test_the_gate_denies_a_span_less_whole_document_and_releases_nothing(
        whole_conn, a_document):
    """CR-07 closed on the ordinary release path, which is where it was reproduced.

    `complete_extracted_text` is member 2 of `ALWAYS_LOCAL`; the run that produced
    this finding ended with the file's own text as the `value` of a released item.

    SABOTAGE: either half of the fix -- `resolve`'s unit lookup or
    `is_whole_document`'s span-less arm -- and this goes red on `isinstance(decision,
    Denied)`.
    """
    file_id, key = a_document
    decision = _gate(whole_conn).release(_request(
        items=(Excerpt(observation_key=key, span=None, reason="the whole thing"),),
        file_id=file_id))
    assert isinstance(decision, Denied), (
        "the whole document was released as one excerpt; "
        f"{ALWAYS_LOCAL[1]!r} is the second of the nine")
    assert decision.reason == "whole_document_requested"
    assert not hasattr(decision, "materialised_items")


def test_a_redacted_identifier_over_the_whole_document_is_refused_too(
        whole_conn, a_document):
    """The rule is about the ADDRESS, not about the kind -- the same line
    `test_a_redacted_identifier_over_the_whole_unit_is_also_refused` draws for the
    span form. A redaction covering the document would send the document with one
    value starred out."""
    file_id, key = a_document
    decision = _gate(whole_conn).release(_request(
        items=(RedactedIdentifier(observation_key=key, span=None,
                                  identifier_class="course-code"),),
        file_id=file_id))
    assert isinstance(decision, Denied)
    assert decision.reason == "whole_document_requested"


# ================================================================================
# The controls. A span-less value is not automatically a whole document.
# ================================================================================

def test_a_spreadsheet_cell_is_still_released(whole_conn):
    """§2.3's cell: a `sheet/row/cell` path, and no text unit in the run.

    This is the case `is_whole_document`'s own docstring was written to protect, and
    the reason a blanket refusal of span-less items is the wrong fix. Reading the
    absent length as zero would make every cell a whole document.

    SABOTAGE: return True from `is_whole_document` whenever `item.span is None`, or
    have `resolve` report a length whenever the value is span-less, and this goes
    red.
    """
    file_id = _file(whole_conn, "Budget.numbers", "hash-cell")
    cell = (Segment(kind="sheet", index=1), Segment(kind="row", index=4),
            Segment(kind="cell", index=3))
    key = _observation(whole_conn, file_id, tag="cell", zone="table",
                       container_path=cell, raw_value=A_CELL, unit_text=None,
                       extractor="xlsx_tables", source_type="spreadsheet")
    _classify(whole_conn, file_id, "hash-cell", key=key)
    _store_policy(whole_conn)

    assert materialise(whole_conn, Item(key, None)).unit_length is None
    decision = _gate(whole_conn).release(_request(
        items=(Excerpt(observation_key=key, span=None, reason="the cell"),),
        file_id=file_id))
    assert isinstance(decision, Released), "a cell is a bounded value, not a document"
    assert decision.materialised_items[0].value == A_CELL
    assert decision.materialised_items[0].unit_length is None


def test_an_exif_field_in_a_run_with_no_units_at_all_is_still_released(whole_conn):
    """§2.8's field, in `extractors/image.py`'s exact shape: span-less, at a `field=`
    path, in a run that emits NO `text_units` rows whatever.

    Nearer to the defect than the cell is: `image.py` addresses a field with no
    label at the EMPTY container path -- the document observation's own path -- and
    the only thing separating the two there is whether a unit stands at it. A fix
    that refused anything span-less at `()`, rather than looking the unit up, would
    take this with it.

    SABOTAGE: refuse a span-less item whose container path is empty, instead of
    asking `unit_for_observation`, and this goes red once `container_path=()`.
    """
    file_id = _file(whole_conn, "IMG_4021.jpg", "hash-exif")
    key = _observation(
        whole_conn, file_id, tag="exif", zone="metadata",
        container_path=(Segment(kind="field", label="camera_make"),),
        raw_value=A_CAMERA, unit_text=None,
        extractor="image_metadata", source_type="image")
    _classify(whole_conn, file_id, "hash-exif", key=key)
    _store_policy(whole_conn)

    assert materialise(whole_conn, Item(key, None)).unit_length is None
    decision = _gate(whole_conn).release(_request(
        items=(Excerpt(observation_key=key, span=None, reason="the camera"),),
        file_id=file_id))
    assert isinstance(decision, Released)
    assert decision.materialised_items[0].value == A_CAMERA


def test_a_bounded_span_less_value_at_a_path_a_unit_occupies_is_still_released(
        whole_conn):
    """The sharpest control: the unit is RIGHT THERE, at the observation's own path,
    and the value is a fraction of it.

    Nothing in the product emits this today, and that is exactly why it is here: the
    refusal must key off the value covering its unit, not off a unit existing. A
    check written as "span-less and a unit is present" passes every other test in
    this file and fails this one.

    SABOTAGE: drop the `len(value) >= unit.length` comparison in `resolve` and
    report `unit.length` whenever a unit is found, and this goes red.
    """
    file_id = _file(whole_conn, "Notes.txt", "hash-bounded")
    key = _observation(whole_conn, file_id, tag="bounded", zone="heading",
                       container_path=(), raw_value=A_HEADING, unit_text=DOCUMENT)
    _classify(whole_conn, file_id, "hash-bounded", key=key)
    _store_policy(whole_conn)

    assert len(A_HEADING) < len(DOCUMENT)
    assert materialise(whole_conn, Item(key, None)).unit_length is None
    decision = _gate(whole_conn).release(_request(
        items=(Excerpt(observation_key=key, span=None, reason="the heading"),),
        file_id=file_id))
    assert isinstance(decision, Released), (
        "§8.4 asks for a short heading INSTEAD of the document; refusing the "
        "heading would refuse the thing the sentence recommends")
    assert decision.materialised_items[0].value == A_HEADING


def test_the_real_extractor_stands_its_document_observation_where_its_unit_stands():
    """The premise the whole fix rests on, taken from the real extractor.

    Everything above is hand-built evidence. The refusal only reaches a real document
    because `extractors/structured_text.py` writes its whole-file `text_units` row at
    the SAME container path its span-less `body` observation addresses -- the empty
    one. Move either and the lookup finds nothing, `unit_length` stays `None`, and
    CR-07 is open again with every test above still green.

    This is also the requirement `95` §5.5 inherits: a PDF `body` observation added
    later must emit its unit at the observation's own path, per page or per document,
    or it reopens this silently.

    SABOTAGE: give the `body` emit in `structured_text.py` a container path, or drop
    `units = [text_unit(text=document.text)]`, and this goes red.
    """
    result = extract_structured_text(
        file_row={"file_id": "f-premise", "content_hash": "c" * 64},
        path=Path(tempfile.mkdtemp()) / "Syllabus.txt",
        policy=SafetyPolicy(is_protected_container=lambda path: False,
                            is_dataless=lambda path: False),
        source_type="text_document",
        read_text_document=lambda path: TextDocument(text=DOCUMENT),
        find_structured_strings=lambda text: (),
        now=OBSERVED_AT, context_window=20)

    body = [observation for observation in result.observations
            if observation["raw_value"] == DOCUMENT
            and observation["location"]["text_span"] is None]
    assert len(body) == 1, "the document is emitted whole, span-less, exactly once"
    at = body[0]["location"]["container_path"]
    units = [unit for unit in result.text_units if unit["container_path"] == at]
    assert units and units[0]["text"] == DOCUMENT, (
        "the unit the refusal measures against must stand at the observation's own "
        f"container path; the observation is at {at!r} and the run's units are at "
        f"{[unit['container_path'] for unit in result.text_units]!r}")


def test_a_bounded_span_inside_the_document_is_still_released(whole_conn):
    """The ordinary excerpt, unchanged. The span form of this rule already worked;
    the fix must not have widened it into the substrings it was letting through."""
    file_id = _file(whole_conn, "Spans.txt", "hash-span")
    key = _observation(whole_conn, file_id, tag="span", zone="body",
                       container_path=(), raw_value=DOCUMENT[0:18],
                       unit_text=DOCUMENT, span=TextSpan(0, 18))
    _classify(whole_conn, file_id, "hash-span", key=key)
    _store_policy(whole_conn)

    decision = _gate(whole_conn).release(_request(
        items=(Excerpt(observation_key=key, span=TextSpan(0, 18),
                       reason="the course code"),),
        file_id=file_id))
    assert isinstance(decision, Released)
    assert decision.materialised_items[0].value == DOCUMENT[0:18]
    assert decision.materialised_items[0].unit_length == len(DOCUMENT)
