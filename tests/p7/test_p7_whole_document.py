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

**SUPERSESSION, 9 Sep 2026, `104` §17.13 (the owner's ruling, applied on the owner's
word "for now its ok let it through").** Everything above still stands and none of
it moved: coverage of a text unit is still what "whole" means, and the two halves
that compute it are still the two modules named above. What §17.13 added is a SECOND
condition on the same arm -- the unit must ALSO be longer than P1's stored
`model.max_dossier_tokens_per_call`, read through `Gate._stored_ceiling` and never
the request's echo of it (M9). A whole unit that fits under the stored ceiling is
shown to either model as itself, on the owner's ruling that a cloud model may be
shown a whole text unit "within the same ceiling"; a whole unit longer than it is
refused, for every target, by the same bound the stage already fills to
(`model_facts.within_dossier_budget`), so the gate never refuses what the stage
sends. `None` -- no ceiling stored -- refuses nothing, because P7 invents no number.

So every gate test in this file that is ABOUT the refusal now stores a ceiling
shorter than its unit, and each says so where it does it. The one test that was a
locality PAIR is now a ceiling pair, which is the honest replacement: what divides
release from refusal here stopped being the destination and became the number.
"""
from __future__ import annotations

import hashlib
import tempfile
from dataclasses import replace
from pathlib import Path

import pytest

from database_agent.budget import set_ceiling
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
from privacy.release import (
    CLOUD_LOCALITY, Denied, ModelCallRequest, ModelTarget, Released, Target,
)
from privacy.resolve import materialise
from privacy.schema import create_privacy_schema
from privacy.vocabulary import ALWAYS_LOCAL

OBSERVED_AT = "2026-09-03T09:00:00Z"
PLAN_VERSION = "plan-whole-1"
COMPONENT = "0.1.0"
CLOUD = ModelTarget(locality="cloud", model_id="a-model", provider="Acme")
#: `104` R-159's other destination. Under `104` §17.13 this door answers the same
#: for either target, so the pair at the bottom loops over both rather than
#: contrasting them; the tests between here and there send to `CLOUD` because that
#: is the target the ruling moved.
LOCAL = ModelTarget(locality="local", model_id="a-model", provider="ollama")
#: P7's own ceiling echo. A number only a test may choose.
MAX_DOSSIER_TOKENS = 4000
#: P1's stored ceiling, which is the one `Gate._stored_ceiling` reads and the only
#: one `check_item`'s whole-document arm may be asked about (`104` §17.13). M9 calls
#: `request.max_dossier_tokens` "the caller's echo of it", so a test that wants the
#: refusal writes the number HERE and never into the request.
CEILING_KEY = "model.max_dossier_tokens_per_call"

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


def _request(*, items, file_id: str,
             model_target: ModelTarget = CLOUD) -> ModelCallRequest:
    return ModelCallRequest(
        stage="fact_resolution", target=Target(file_ids=(file_id,)),
        model_target=model_target, requested_items=tuple(items),
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
        # `104` §17.13: a whole unit is the whole DOCUMENT when it is longer than
        # the stored ceiling, on any target; the ceiling here is one short of it.
        check_item(item, unit_length=len(DOCUMENT), zone="body", protected=False,
                   sensitive_keys=frozenset(), allow_unratified=True,
                   suspension_permits_self_description=False,
                   locality=CLOUD_LOCALITY, ceiling=len(DOCUMENT) - 1)
    assert str(len(DOCUMENT)) in str(caught.value)
    assert "full documents" in str(caught.value)


def test_the_gate_denies_a_span_less_whole_document_and_releases_nothing(
        whole_conn, a_document):
    """CR-07 closed on the ordinary release path, which is where it was reproduced.

    `complete_extracted_text` is member 2 of `ALWAYS_LOCAL`; the run that produced
    this finding ended with the file's own text as the `value` of a released item.

    A CEILING ONE SHORTER THAN THE UNIT SINCE `104` §17.13, stored where P1 stores
    it. Under §17.13 the arm fires for a whole unit LONGER than the stored ceiling,
    so a test about the refusal has to put the document over one; the number is
    `len(DOCUMENT) - 1` and nothing this test invented. The pair at the bottom of the
    file is the same fixture with the ceiling AT the unit's length, released.

    SABOTAGE: either half of the fix -- `resolve`'s unit lookup or
    `is_whole_document`'s span-less arm -- and this goes red on `isinstance(decision,
    Denied)`.
    """
    file_id, key = a_document
    set_ceiling(whole_conn, CEILING_KEY, len(DOCUMENT) - 1)
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
    value starred out.

    The stored ceiling is one shorter than the unit for `104` §17.13's reason and it
    is the SAME ceiling the excerpt above is refused under.

    **`104` §18 S4 (9 Sep 2026) puts a stronger refusal in front of this one.** The
    gate in this file is built with a classifier that names no class -- which is
    every deployment while `104` SF-2's classifier is unwritten -- so the value
    would leave UNREDACTED under a name that says it was redacted. That is
    `raw_sensitive_values`, member of §8.4's nine, and `release.DECISION_ORDER`
    publishes `always_local_item` before `whole_document_requested`. So the reason
    asserted here is the always-local one; the whole-document arm is exercised on
    the same address by the `Excerpt` test above, and would be this kind's reason
    too under a classifier that redacts."""
    file_id, key = a_document
    set_ceiling(whole_conn, CEILING_KEY, len(DOCUMENT) - 1)
    decision = _gate(whole_conn).release(_request(
        items=(RedactedIdentifier(observation_key=key, span=None,
                                  identifier_class="course-code"),),
        file_id=file_id))
    assert isinstance(decision, Denied)
    assert decision.reason == "always_local_item", decision.reason
    assert "no redaction applied" in decision.explanation


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


# ================================================================================
# SF-1 (`104` R-07): the same defect, one extractor later
# ================================================================================
#
# `extractors/docx.py` gained the whole-prose `body` observation in `fd68cb6` --
# `emit(zone="body", raw="\n".join(prose), container_path=(), span=None,
# unit_text=None)` -- and did NOT gain the `text_units` row at the same empty path
# that `structured_text.py` has carried since E3. The comment above it even cites
# this file's reasoning ("both halves are load-bearing"), and the half that makes
# the refusal reachable is the one that was left out.
#
# So `unit_for_observation` found nothing at `()`, `resolve.materialise` reported
# `unit_length=None`, `is_whole_document` read a missing length as "not a whole
# document", and every word of a Word document was releasable as an excerpt.
# `104` §5 SF-1 measured it live on the owner's files: 7 of 42 dossiers over 16,000
# bytes, largest 45,843.
#
# The canary below is a sentence that exists ONLY in the body. It is not a heading,
# not a cell, not a core property, and no `find_structured_strings` match covers
# it -- so if it appears in released bytes, it got there as the whole body.

#: Planted in the body of the synthetic Word document and nowhere else in it.
DOCX_CANARY = "My mother's diagnosis was confirmed on the fourteenth of March."

DOCX_BODY = (
    "I want to study economics at Wash U. " + DOCX_CANARY
    + " That is the reason this application matters to me."
)


def _a_word_document():
    from extractors.docx import DocxCell, DocxDocument, DocxParagraph

    return DocxDocument(
        core_properties={"creator": "python-docx"},
        paragraphs=(
            DocxParagraph(index=1, text="Application Essay", zone="heading",
                          heading_path=((1, "Application Essay"),)),
            DocxParagraph(index=2, text=DOCX_BODY, zone="body",
                          heading_path=((1, "Application Essay"),)),
        ),
        cells=(DocxCell(table=1, row=1, column=1, text="Institution",
                        column_header="Field"),),
    )


def _extract_the_word_document(file_id: str, content_hash: str):
    from extractors.docx import extract_docx

    return extract_docx(
        file_row={"file_id": file_id, "content_hash": content_hash},
        path=Path(tempfile.mkdtemp()) / "Wash U.docx",
        policy=SafetyPolicy(is_protected_container=lambda path: False,
                            is_dataless=lambda path: False),
        read_docx=lambda path: _a_word_document(),
        find_structured_strings=lambda text: (),
        now=OBSERVED_AT, context_window=20)


def test_the_docx_extractor_stands_its_body_observation_where_its_unit_stands():
    """E2's twin of the E3 premise above, and it is the whole of SF-1.

    Everything the gate does about a whole document rests on a unit standing at the
    observation's own container path. E3 writes one; E2 wrote none, and its own
    comment claims the property E3's code delivers.

    SABOTAGE: drop the whole-body `text_unit` from `extractors/docx.py` and this
    goes red, exactly as the E3 test above does for `structured_text.py`.
    """
    result = _extract_the_word_document("f-docx-premise", "d" * 64)

    body = [observation for observation in result.observations
            if observation["location"]["zone"] == "body"
            and observation["location"]["text_span"] is None]
    assert len(body) == 1, "the prose is emitted whole, span-less, exactly once"
    at = body[0]["location"]["container_path"]
    units = [unit for unit in result.text_units if unit["container_path"] == at]
    assert units and units[0]["text"] == body[0]["raw_value"], (
        "the unit the refusal measures against must stand at the observation's own "
        f"container path; the observation is at {at!r} and the run's units are at "
        f"{[unit['container_path'] for unit in result.text_units]!r}")


def _write_the_word_document(conn, name: str, tag: bytes):
    """The real extractor through the real writer, returning the body's key."""
    from evidence_shape.store import RunWriter

    file_id = _file(conn, name, f"hash-{tag.decode()}")
    digest = hashlib.sha256(tag).hexdigest()
    run_id = RunWriter(conn, author="P5").write(
        _extract_the_word_document(file_id, digest))
    key = conn.execute(
        "SELECT observation_key FROM evidence WHERE run_id = ? AND raw_value = ?",
        (run_id, DOCX_BODY)).fetchone()[0]
    return file_id, digest, key


def test_the_whole_body_of_a_word_document_is_denied_and_releases_nothing(
        whole_conn):
    """The live path, through the real extractor, the real writer and the real gate.

    `104` SF-1's own words: "keep dossier payloads local". The canary is the
    assertion that says so -- a sentence that exists only in the body, so its
    presence in released bytes has exactly one explanation.

    A CEILING ONE SHORTER THAN THE BODY SINCE `104` §17.13. The measurement SF-1 was
    found by is what makes this the right half of the ruling to pin: 7 of 42 dossiers
    over 16,000 bytes, largest 45,843. A body that size is over any ceiling this
    product would store, so the refusal SF-1 closed is the one §17.13 keeps; what
    §17.13 releases is the short unit that never had 45,843 characters in it.
    """
    file_id, _digest, key = _write_the_word_document(
        whole_conn, "Wash U.docx", b"docx")
    _classify(whole_conn, file_id, "hash-docx", key=key)
    _store_policy(whole_conn)
    set_ceiling(whole_conn, CEILING_KEY, len(DOCX_BODY) - 1)

    decision = _gate(whole_conn).release(_request(
        items=(Excerpt(observation_key=key, span=None, reason="the body"),),
        file_id=file_id))

    assert isinstance(decision, Denied), decision
    assert decision.reason == "whole_document_requested", decision.reason
    assert not getattr(decision, "materialised_items", ())


def test_the_word_documents_body_is_offered_only_when_it_fits_the_ceiling(whole_conn):
    """The other half: the call is not BUILT, so nothing pays to materialise a
    document in order to refuse it (`model_facts.releasable_observations`).

    The canary check runs over every value the builder WOULD offer, which is the
    shape the instrument (`104` §7 "Instruments") repeats over the owner's corpus.

    **THIS ASSERTED THE ABSENCE ALONE UNTIL 9 Sep 2026.** `may_be_released` refused a
    whole unit for a cloud target then, so the body was never offered whatever the
    ceiling was. `104` §17.13 dropped that arm: ONE bound now decides, the ceiling, in
    `within_dossier_budget`, and it decides the same way for either target. So the
    absence has to be asserted against its own presence or it no longer says anything
    -- a builder that had simply stopped offering body readings at all would satisfy
    the old single assertion, and would be the coverage loss §17.13 was ruled to end.

    Both halves are run over the same document and the same limit, and the two
    ceilings are the body's own length either side of the bound. Under the generous
    one the body IS offered, canary and all; under the short one it is SKIPPED and the
    walk continues, so the headings and the cell beside it are still offered -- which
    is `within_dossier_budget`'s own rule that an over-long reading costs its file
    only itself.
    """
    from model_facts import (
        ordered_releasable_observations, releasable_observations, released_wire_cost,
    )

    file_id, digest, _key = _write_the_word_document(
        whole_conn, "Wash U 2.docx", b"docx-2")

    def offer(ceiling):
        return [observation.raw_value for observation in releasable_observations(
            whole_conn, file_id=file_id, content_hash=digest, limit=12,
            locality=CLOUD_LOCALITY, ceiling=ceiling)]

    fits = offer(MAX_DOSSIER_TOKENS)
    assert [value for value in fits if DOCX_CANARY in value], (
        "the body is not offered under a ceiling 26 times its length, so this test "
        "cannot tell the ceiling from a builder that dropped body readings; `104` "
        f"§17.13 offers it -- got {[value[:30] for value in fits]}")

    # `104` R-174: the ceiling is spent in wire bytes, so the bound the body does
    # not fit is one byte short of its own wire cost, read off the offer.
    body = [observation for observation in ordered_releasable_observations(
        whole_conn, file_id=file_id, content_hash=digest,
        locality=CLOUD_LOCALITY, limit=12) if DOCX_CANARY in observation.raw_value]
    assert len(body) == 1, body
    over = offer(released_wire_cost(body[0]) - 1)
    assert over, "the headings and cells beside the body are still offered"
    assert not [value for value in over if DOCX_CANARY in value], over
    assert set(over) < set(fits), (
        "the short ceiling dropped something other than the body")


# ================================================================================
# `104` R-152: a unit that holds no line break is a LINE, and a line released whole
# is an excerpt. Plus the half of `104` R-135 that never reached this file.
# ================================================================================
#
# The two rulings met here and the gate was answering neither. R-135 exempted a whole
# HEADING unit in `privacy.release` and taught both release builders to admit one --
# and the gate, which asks the whole-document question a second time over the RESOLVED
# items, went on refusing it. So the builders offered the heading that states a course
# code and its name together, and the gate denied the call it arrived in. Measured on
# the owner's corpus at r13: 47 `whole_document_requested` denials, 36 of them the
# WHOLE of a site-A call, `PRIVACY_GATE_REFUSED` in the grounding report and every fact
# of the file left `missing`; the units were under 200 characters, 24 of them under 50,
# mostly pdf and docx -- which is what a heading and a running footer and a table cell
# measure.
#
# R-152's ruling is structural and is not a length: a unit with no line break in it is
# ONE LINE, because a line break is the document's own statement that it has a second
# line, and §8.4's sentence asks for "a short heading or OCR excerpt" INSTEAD of a full
# document. What it does not decide is size -- a very long single line is still one
# line, is released, and is counted (`GroundingReport.longest_line_unit_length`); that
# is `104` R-145's paragraph and §8.6's ceiling bounds it.

#: Twenty characters, one line, the shape r13 refused 36 times at site A.
A_LINE = "Invoice total 42.00"

#: The same words with the line breaks a page of prose has. Not longer for the sake of
#: it: the ONLY difference between this and the line above is the newlines, so a test
#: that passes for one and fails for the other has isolated the criterion.
A_PAGE = "Invoice total 42.00\nDue on receipt, net 30\nRemit to the address above"

#: §8.4's own alternative to a document, and R-135's exemption.
A_TITLE = "COMS W3134: Data Structures"


def _whole_unit(conn, *, name, tag, zone, container_path, text):
    """One file whose run holds `text` as the unit at `container_path`, and one
    observation addressing the whole of it. The shape `extractors/pdf.py` emits a
    heading in and `extractors/docx.py` a running footer and a table cell."""
    file_id = _file(conn, name, f"hash-{tag}")
    key = _observation(conn, file_id, tag=tag, zone=zone,
                       container_path=container_path, raw_value=text,
                       unit_text=text, span=TextSpan(0, len(text)),
                       extractor="pdf.text", source_type="text_document")
    _classify(conn, file_id, f"hash-{tag}", key=key)
    _store_policy(conn)
    return file_id, key


def _release_whole(conn, file_id, key, text):
    return _gate(conn).release(_request(
        items=(Excerpt(observation_key=key, span=TextSpan(0, len(text)),
                       reason="the whole of one unit"),),
        file_id=file_id))


def test_the_gate_releases_a_short_single_line_unit_whole(whole_conn):
    """`104` R-152 on the path where the loss was measured.

    Nineteen characters, no line break, and before the ruling this came back
    `Denied(whole_document_requested)` -- which at site A is the file's whole call, so
    the file's facts were recorded `missing` and the model was never asked. §8.4 wants
    a short excerpt sent INSTEAD of a document, and this IS the short excerpt.

    **A CEILING ONE SHORTER THAN THE LINE SINCE `104` §17.13, AND WITHOUT IT THIS
    TEST STOPS TESTING ANYTHING.** §17.13 gave the whole-document arm a second
    condition -- the unit must be longer than P1's stored ceiling -- so with no
    ceiling stored the arm never fires, the postcheck has no `WholeDocumentRequested`
    to catch, and R-152's exemption is never reached on the way to this `Released`.
    The ceiling below puts the unit over the bound so that the arm DOES fire and the
    exemption is what waives it, which is what this test was written to assert. The
    sabotage above only goes red because of it.

    SABOTAGE: make `unit_holds_a_line_break` return `True` for a unit with no newline
    and this goes red, which is the whole of the criterion.
    """
    file_id, key = _whole_unit(
        whole_conn, name="Invoice.pdf", tag="line", zone="body",
        container_path=(Segment("page", 1), Segment("paragraph", 1)), text=A_LINE)
    set_ceiling(whole_conn, CEILING_KEY, len(A_LINE) - 1)

    decision = _release_whole(whole_conn, file_id, key, A_LINE)

    assert isinstance(decision, Released), getattr(decision, "reason", decision)
    assert decision.materialised_items[0].value == A_LINE
    assert decision.materialised_items[0].whole_line_unit is True
    assert decision.materialised_items[0].whole_heading_unit is False


def test_the_gate_denies_the_same_words_once_they_hold_line_breaks(whole_conn):
    """The control, and it differs from the test above by newlines and nothing else.

    A unit that holds a line break has said it has more than one line, and the whole of
    it is what §8.4 calls a full document. The exemption is structural, so it cannot
    widen to a page by accident -- and a page is exactly what this is.

    A CEILING ONE SHORTER THAN THE PAGE SINCE `104` §17.13, because the arm the
    exemption is an exemption FROM now needs the unit to be over the ceiling before it
    fires at all. R-152's criterion is untouched and is still what this isolates: the
    test above it releases the same words with the same ceiling arithmetic and differs
    from this one by newlines and nothing else.
    """
    file_id, key = _whole_unit(
        whole_conn, name="Statement.pdf", tag="page", zone="body",
        container_path=(Segment("page", 1),), text=A_PAGE)
    set_ceiling(whole_conn, CEILING_KEY, len(A_PAGE) - 1)

    decision = _release_whole(whole_conn, file_id, key, A_PAGE)

    assert isinstance(decision, Denied), decision
    assert decision.reason == "whole_document_requested", decision.reason
    assert not getattr(decision, "materialised_items", ())


def test_a_bounded_span_inside_a_multi_line_unit_is_still_released(whole_conn):
    """The ordinary excerpt out of a document, untouched by either ruling. Without
    this, "a multi-line unit is refused" could be read as "a multi-line unit is
    unreachable", which would be a coverage loss of its own."""
    file_id, key = _whole_unit(
        whole_conn, name="Statement 2.pdf", tag="page-2", zone="body",
        container_path=(Segment("page", 1),), text=A_PAGE)
    inner = _observation(
        whole_conn, file_id, tag="page-2-inner", zone="body",
        container_path=(Segment("page", 1),), raw_value="42.00",
        unit_text=A_PAGE, span=TextSpan(14, 19),
        extractor="pdf.text", source_type="text_document")
    _classify(whole_conn, file_id, "hash-page-2-inner", key=inner)

    decision = _gate(whole_conn).release(_request(
        items=(Excerpt(observation_key=inner, span=TextSpan(14, 19),
                       reason="the amount"),),
        file_id=file_id))

    assert isinstance(decision, Released), getattr(decision, "reason", decision)
    assert decision.materialised_items[0].value == "42.00"
    assert decision.materialised_items[0].whole_line_unit is False
    assert key  # the whole-unit address exists beside it and was not requested


def test_the_gate_releases_a_whole_heading_unit_which_is_r135s_missing_half(
        whole_conn):
    """`104` R-135 reached `privacy.release` and both builders and stopped at the gate.

    Measured at `e5cce44`, before this test existed: the gate answered
    `Denied(whole_document_requested)` for a span covering a whole `heading` unit. So
    the ruling's own worked example -- the syllabus heading that states `COMS W3134`
    and `Data Structures` together, which site C's prompt asks the model to judge two
    spellings from -- was offered by `model_placement.releasable_excerpts` and then
    refused, taking the call with it. `tests/p11/test_p11_anchor_heading_release.py`
    measures the builders and could not see this, because a builder does not release.

    It is fixed here rather than in a row of its own because it is one exemption asked
    in three places, and the gate was the third.

    The stored ceiling is one shorter than the heading for `104` §17.13's reason, and
    it is load-bearing rather than decorative: with no ceiling stored the arm this
    exemption excepts would not fire, and the test would pass without ever reaching
    R-135's exemption -- green, and testing nothing.
    """
    file_id, key = _whole_unit(
        whole_conn, name="Syllabus.pdf", tag="title", zone="heading",
        container_path=(Segment("page", 1), Segment("heading", 1)), text=A_TITLE)
    set_ceiling(whole_conn, CEILING_KEY, len(A_TITLE) - 1)

    decision = _release_whole(whole_conn, file_id, key, A_TITLE)

    assert isinstance(decision, Released), getattr(decision, "reason", decision)
    assert decision.materialised_items[0].value == A_TITLE
    assert decision.materialised_items[0].whole_heading_unit is True


def test_a_unit_that_only_ENDS_in_a_line_break_is_one_line(whole_conn):
    """A terminator is not a second line, and `rtrim` is why the distinction holds.

    `evidence_shape.text_units` stores a unit's text "exactly as extracted", so a unit
    can carry the newline that ended it. Reading that as two lines would refuse a unit
    for its punctuation -- and `store.line_reading_for`, which is P4's own reading of
    what a line is, would disagree: it takes the previous newline to the next one, and
    there is no next one after the last character.

    The stored ceiling is one shorter than the unit for `104` §17.13's reason: the arm
    the exemption excepts fires only over the ceiling, so without it this test would
    be green without the terminator question ever being asked.
    """
    text = A_LINE + "\n"
    file_id, key = _whole_unit(
        whole_conn, name="Invoice 2.pdf", tag="terminated", zone="body",
        container_path=(Segment("page", 1), Segment("paragraph", 1)), text=text)
    set_ceiling(whole_conn, CEILING_KEY, len(text) - 1)

    decision = _release_whole(whole_conn, file_id, key, text)

    assert isinstance(decision, Released), getattr(decision, "reason", decision)
    assert decision.materialised_items[0].whole_line_unit is True


def test_an_always_local_zone_still_refuses_a_whole_single_line_unit(whole_conn):
    """The exemption excepts ONE refusal, and this is the assertion that says so.

    `Gate._precheck_items` asks `check_item` everything it can answer with no unit
    length -- the always-local names, the sensitive key, the always-local zone, the
    protected file -- and returns that refusal BEFORE anything is materialised, which
    is `DECISION_ORDER`'s rule that a gate must not hold a value in memory in order to
    decide it was not allowed to. The whole-document arm is the only refusal that
    needed the resolved length, so it is the only one the postcheck's exception can
    waive.

    There is no one-line sabotage of the postcheck that turns this red, and that is
    the property rather than a gap in the test: `release` puts the precheck's refusal
    into the early denial builders, so an always-local-zone item is answered before
    the postcheck runs and cannot be released by anything the postcheck does. What
    this catches is a FUTURE move -- an exemption hoisted above `_precheck_items`, or
    a release short-circuited on one.

    **RE-ADDRESSED from `path` to `filename` by `104` §17.13, 9 Sep 2026**, which
    released `path` and `ocr` to every target and left `filename` as the one member of
    `ALWAYS_LOCAL_ZONES` refused to every target. The claim is untouched by the move
    -- it was never about paths, it is that R-152's exemption waives the
    whole-document refusal and NOTHING ELSE -- and `filename` is where there is still
    a zone refusal for the exemption to fail to waive. The value on the wire in the
    failure mode is now a name a person gave a file rather than an absolute directory,
    which is §7.7's own reason for giving the filename one door.

    The stored ceiling is one shorter than the line so that the whole-document arm
    fires too: without it the item is over no bound, only one refusal is in play, and
    "the exemption waives one refusal and not the other" is not being asked.
    """
    file_id, key = _whole_unit(
        whole_conn, name="Where.pdf", tag="filename-line", zone="filename",
        container_path=(Segment("page", 1), Segment("paragraph", 1)), text=A_LINE)
    set_ceiling(whole_conn, CEILING_KEY, len(A_LINE) - 1)

    decision = _release_whole(whole_conn, file_id, key, A_LINE)

    assert isinstance(decision, Denied), decision
    assert decision.reason == "always_local_item", decision.reason


# ================================================================================
# `104` R-159, then `104` §17.13: the pair stopped being about the target and
# became about the ceiling
# ================================================================================

def test_a_whole_unit_is_released_to_every_target_when_it_fits_the_stored_ceiling(
        whole_conn, a_document):
    """THE PAIR, and the field that differs is now the CEILING and not the target.

    **This test asserted `Denied` for `CLOUD` and `Released` for `LOCAL` on 8 Sep
    2026, which was `104` R-159.** §8.4's sentence -- the engine "should not send full
    documents where a short heading or OCR excerpt is enough to resolve the question"
    -- sits under `00`:186's *"when a cloud model is used"*, and until 8 Sep the code
    applied it to every destination. The measurement that made R-159 is still why
    anything here releases at all: every extractor emits page- and paragraph-sized
    units with one span-less observation over each, so on r15 fifty-four of 199 files
    had body readings and NOT ONE was releasable, and the median file was shown 109
    characters of its own text under a 4,000-character ceiling.

    **`104` §17.13, 9 Sep 2026, extended item 14 to the cloud target**: "a cloud model
    may be shown a whole text unit, the person's folder path and OCR text within the
    same ceiling, for every file the cloud gate permits." R-159 had already named what
    bounds the release -- the dossier ceiling, which is the bound §8.4's own sentence
    hands to `max_dossier_tokens_per_call` -- and §17.13 made that bound the whole of
    the rule, for both targets. So the pair survives with the same shape and a
    different axis: same document, same span-less excerpt, one field different, and
    the field is P1's stored ceiling.

    The bound is strict `>`: a unit exactly AT the ceiling fits, which is why the
    releasing half stores `len(DOCUMENT)` rather than something above it, and the
    refusing half stores one less. Both halves loop over both targets, because "the
    answer no longer depends on the destination" is a claim worth running -- a build
    that put `locality` back into the whole-document arm goes red here.

    The ceiling is stored where P1 stores it and never echoed through the request:
    `Gate._stored_ceiling` reads `budget_ceilings`, M9 calls `max_dossier_tokens` "the
    caller's echo of it", and a caller must not be able to raise its own ceiling.
    """
    file_id, key = a_document
    item = Excerpt(observation_key=key, span=None, reason="the whole thing")

    set_ceiling(whole_conn, CEILING_KEY, len(DOCUMENT) - 1)
    for target in (CLOUD, LOCAL):
        denied = _gate(whole_conn).release(_request(
            items=(item,), file_id=file_id, model_target=target))
        assert isinstance(denied, Denied), (
            f"a whole unit longer than the stored ceiling, bound for a "
            f"{target.locality} model, was {type(denied).__name__}; "
            f"{ALWAYS_LOCAL[1]!r} is the second of the nine")
        assert denied.reason == "whole_document_requested"

    set_ceiling(whole_conn, CEILING_KEY, len(DOCUMENT))
    for target in (CLOUD, LOCAL):
        released = _gate(whole_conn).release(_request(
            items=(item,), file_id=file_id, model_target=target))
        assert isinstance(released, Released), (
            f"a whole unit that FITS the stored ceiling, bound for a "
            f"{target.locality} model, was {type(released).__name__}; `104` §17.13 "
            f"shows either model the unit")
        assert [one.value for one in released.materialised_items] == [DOCUMENT], (
            f"the {target.locality} model is shown the page it is being asked "
            f"about, which is the whole of what the ruling changes at this door")


def test_a_bounded_span_is_released_to_either_target_and_the_pair_proves_the_arm(
        whole_conn, a_document):
    """The control on the pair above: nothing about a SHORT excerpt changed.

    Written for `104` R-159, where a test that only showed the whole unit arriving
    locally could not tell "the whole-document arm is now cloud-only" from "the door
    stopped checking spans". **`104` §17.13 makes the control read the other way and
    keeps it just as necessary**: the pair above now turns on the ceiling, and a test
    that only showed a whole unit released under a generous ceiling could not tell
    "the arm is ceiling-bound" from "the door stopped checking spans" either. The
    excerpt here is twelve characters of a 199-character unit and is released whatever
    the ceiling, because coverage is still the qualifier.
    """
    file_id = _file(whole_conn, "Syllabus.txt", "hash-bounded")
    span = TextSpan(0, 12)
    key = _observation(
        whole_conn, file_id, tag="bounded", zone="body", container_path=(),
        raw_value=DOCUMENT[:12], unit_text=DOCUMENT, span=span)
    _classify(whole_conn, file_id, "hash-bounded", key=key)
    _store_policy(whole_conn)
    short = Excerpt(observation_key=key, span=span, reason="the opening")
    for target in (CLOUD, LOCAL):
        decision = _gate(whole_conn).release(_request(
            items=(short,), file_id=file_id, model_target=target))
        assert isinstance(decision, Released), (
            f"a bounded excerpt bound for a {target.locality} model was "
            f"{type(decision).__name__}")
        assert [one.value for one in decision.materialised_items] == [DOCUMENT[:12]]
