# tests/p6/test_p6_direct.py
"""Done-means 5, §3.5's four explicit slots, and the raw-value half of Done-means 4."""
from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from evidence_shape.fixtures import by_number
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import (
    observations_by_key, observations_for_file, record_observation, record_run,
)

from facts import direct as direct_module
from facts.direct import (
    DIRECT_ORIGIN, DIRECT_STATE, DirectSlot, DirectSlots, UnknownFile, direct_facts,
)
from facts.discount import MetadataScreen
from facts.fields import FieldNotInCatalogue
from facts.file_facts import facts_for_file
from facts.unresolved import unresolved_for_file
from facts.values import values_in_field

#: Task 6's §2.2/§2.3 screen, injected EMPTY and injected VISIBLY. These tests hold no
#: tool-producer catalogue and no metadata property list, so nothing here is suppressed
#: or demoted -- but the producer takes the screen with no default (F8), so "this test
#: injects an empty catalogue" is written at every call site instead of being a silence
#: that let `python-docx` through. `tests/p6/test_p6_discount.py` is where a POPULATED
#: screen is driven end to end.
NO_CATALOGUE = MetadataScreen()

CLOCK = "2026-08-19T12:00:00+00:00"

#: §3.2's own worked derivation: "an EXIF field called DateTimeOriginal is raw
#: metadata; capture date = 2026-07-17 is the file fact derived from it." Fixture 7
#: carries the left-hand side byte-exact.
EXIF_RAW = "2026:07:17 14:03:22"
CAPTURE_DATE = "2026-07-17"


def _iso_date(raw: str) -> str:
    """The caller's canonicaliser, not P6's.

    §3.2 names both forms and P6 owns neither: round 4's C-5 records that
    `normalize(field, raw_value)` is claimed by P8's Contract-in and disowned by P6's
    Task 17, so no part builds it. A per-slot canonicaliser supplied at the call is
    how this task produces §3.2's right-hand side without inventing the function
    neither part owns. `facts.direct` holds no date knowledge whatever; the guard
    below asserts that by introspection.
    """
    return raw[:10].replace(":", "-")


def _refuse(raw: str) -> str:
    raise ValueError(f"this slot cannot canonicalise {raw!r}")


def _file(conn, tmp_path, *, name, body, mtime=1_700_000_000.0, parent="Downloads"):
    """One P1 `files` row over real bytes, so the content hash is P1's own."""
    path = tmp_path / parent / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": mtime}),
        parent_folder_context=parent, mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, zone, container_path=(),
             extractor="pdf.text", version="1.0.0", source_type="text_document",
             analysis_tier="native", reliability="direct"):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version=version,
        source_type=source_type, analysis_tier=analysis_tier, config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version=version, source_type=source_type, raw_value=raw,
        location=Location(zone, tuple(container_path)), occurrence_count=1,
        observed_at=CLOCK, reliability=reliability, run_id=run_id)
    record_observation(conn, observation)
    return observation


def _code_strings(module) -> set[str]:
    """Every string literal in a module that is NOT a docstring.

    A source-text search matches comments and docstrings, and a guard that does that
    has broken three tasks on this project already (P5 PLAN, Task 20). This reads the
    code. Same helper as `tests/p6/test_p6_evidence.py`; each test file stands alone.
    """
    tree = ast.parse(inspect.getsource(module))
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and body:
            first = body[0]
            if (isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docstrings.add(id(first.value))
    return {node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and id(node) not in docstrings}


# --- the slots, declared by the caller and never by `facts` ---------------------

EXIF_SLOT = DirectSlot(
    slot_id="exif-capture-time", field_key="capture_date",
    names=lambda locator: locator.endswith("field=DateTimeOriginal"),
    canonical=_iso_date)

#: P5's `filesystem.record` publishes `mime_type` at zone `metadata`,
#: `reliability = "direct"` -- a §3.5 slot that exists in the shipped system today.
FILE_TYPE_SLOT = DirectSlot(
    slot_id="fs-mime-type", field_key="file_type",
    names=lambda locator: locator.endswith("field=mime_type"),
    canonical=lambda raw: raw)

#: §3.13's "filesystem timestamp". `extractors.filesystem.METADATA_SLOTS` is
#: ("normalized_filename", "extension", "mime_type") -- no timestamp -- so this slot
#: has no publisher today. The injection is what makes that a one-line change later.
CREATION_SLOT = DirectSlot(
    slot_id="fs-observed-timestamps", field_key="creation_date",
    names=lambda locator: locator.endswith("field=observed_timestamps"),
    canonical=lambda raw: raw)

#: §3.5's "labeled form field" -- P4's fixture 12, a labeled spreadsheet cell.
CELL_SLOT = DirectSlot(
    slot_id="labeled-cell-cycle", field_key="application_cycle",
    names=lambda locator: locator.startswith("table:sheet=2/row=7/column=3"),
    canonical=lambda raw: raw)

#: §3.5's "document title". The catalogue carries no field for a raw document title,
#: which is the point of the test that uses it.
TITLE_SLOT = DirectSlot(
    slot_id="pdf-title", field_key="document_title",
    names=lambda locator: locator.startswith("title:"),
    canonical=lambda raw: raw)


@pytest.fixture()
def photo(p6_conn, tmp_path):
    """Fixture 7's EXIF reading on a file P1 holds, plus a text date to contrast."""
    file_id, content_hash = _file(p6_conn, tmp_path, name="IMG_4821.heic",
                                  body=b"\x00photo-bytes")
    exif = _observe(p6_conn, run_id="run-exif", file_id=file_id,
                    content_hash=content_hash, raw=EXIF_RAW, zone="metadata",
                    container_path=(Segment("field", label="DateTimeOriginal"),),
                    extractor="image.exif", source_type="image")
    return file_id, content_hash, exif


# --- Done-means 5: the EXIF slot ------------------------------------------------

def test_an_exif_datetimeoriginal_observation_produces_a_direct_capture_date_fact(
        p6_conn, photo):
    # Done-means 5, and §3.2's worked derivation: the EXIF field is raw metadata,
    # `capture date = 2026-07-17` is the file fact derived from it.
    file_id, content_hash, exif = photo
    written = direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                           slots=DirectSlots(slots=(EXIF_SLOT,)), screen=NO_CATALOGUE)
    assert len(written) == 1

    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert [row["field_key"] for row in rows] == ["capture_date"]
    assert rows[0]["reliability_state"] == DIRECT_STATE == "direct"
    assert rows[0]["origin"] == DIRECT_ORIGIN
    assert json.loads(rows[0]["evidence_refs"]) == [exif.observation_key]

    values = values_in_field(p6_conn, "capture_date")
    assert [value["canonical_value"] for value in values] == [CAPTURE_DATE]


def test_the_exif_observation_is_readable_and_unchanged_after_resolution(
        p6_conn, photo):
    # Done-means 5's second clause and Done-means 4's last: "each observation's raw
    # value unchanged afterwards". §3.2: the product "must preserve both the original
    # evidence and the conclusion built from it". P4's `evidence_never_overwritten`
    # trigger makes this unfalsifiable; the assertion states the intent.
    file_id, content_hash, exif = photo
    direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                 slots=DirectSlots(slots=(EXIF_SLOT,)), screen=NO_CATALOGUE)

    still = observations_by_key(p6_conn, exif.observation_key)
    assert [one.raw_value for one in still] == [EXIF_RAW]
    assert still[0].raw_value != CAPTURE_DATE
    assert still[0].normalized_value is None


# --- §3.5's distinction: the slot, not the string --------------------------------

def test_a_filesystem_timestamp_is_direct(p6_conn, tmp_path):
    # §3.13 names the filesystem timestamp a Direct source. `creation_date` is
    # §3.11's universal field for it and is distinct from `capture_date` (§3.2
    # separates them by name) and from `capture_year` (§3.11's Photos dimension).
    file_id, content_hash = _file(p6_conn, tmp_path, name="notes.pdf", body=b"%PDF-1")
    _observe(p6_conn, run_id="run-fs", file_id=file_id, content_hash=content_hash,
             raw="1700000000.0", zone="metadata",
             container_path=(Segment("field", label="observed_timestamps"),),
             extractor="filesystem.record", version="0.1.0",
             source_type="filesystem", analysis_tier="filesystem")

    direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                 slots=DirectSlots(slots=(CREATION_SLOT,)), screen=NO_CATALOGUE)
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert [(row["field_key"], row["reliability_state"]) for row in rows] == [
        ("creation_date", DIRECT_STATE)]


def test_the_same_date_string_in_body_text_produces_no_direct_fact(p6_conn, photo):
    # The §3.5 distinction, asserted on ONE string in TWO slots: the EXIF reading is
    # direct, the identical characters on page three are not, and §3.10's explicit-
    # pattern path (Task 12) is where the second one goes. The slot decides.
    file_id, content_hash, exif = photo
    body = _observe(p6_conn, run_id="run-body", file_id=file_id,
                    content_hash=content_hash, raw=EXIF_RAW, zone="body",
                    reliability="possible")

    direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                 slots=DirectSlots(slots=(EXIF_SLOT,)), screen=NO_CATALOGUE)
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert len(rows) == 1
    assert json.loads(rows[0]["evidence_refs"]) == [exif.observation_key]
    assert body.observation_key not in json.loads(rows[0]["evidence_refs"])

    # And it is still there for Task 12 to rank -- this producer consumed nothing.
    keys = {one.observation_key for one in observations_for_file(p6_conn, file_id)}
    assert body.observation_key in keys


def test_a_filename_date_produces_no_direct_fact(p6_conn, tmp_path):
    # P4's fixture 11 is `fs.basic` at zone `filename`, reliability `possible`: a
    # filename is evidence (§2.2) and is not one of §3.5's explicit slots.
    file_id, content_hash = _file(p6_conn, tmp_path, name="2026-07-17 scan.pdf",
                                  body=b"%PDF-2")
    _observe(p6_conn, run_id="run-name", file_id=file_id, content_hash=content_hash,
             raw=EXIF_RAW, zone="filename", extractor="filesystem.record",
             version="0.1.0", source_type="filesystem", analysis_tier="filesystem",
             reliability="possible")

    assert direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                        slots=DirectSlots(slots=(EXIF_SLOT, CREATION_SLOT)),
                        screen=NO_CATALOGUE) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []


def test_the_slot_decides_and_not_the_observations_own_reliability(p6_conn, tmp_path):
    # P4's fixture 6 states it on the fixture: "direct describes the slot, not the
    # value's usefulness". Fixture 12 is §3.5's labeled form field and P4 marks it
    # `possible`; gating on that would make one of the four named slots unreachable
    # against P4's own fixture for it.
    fixture = by_number(12)
    assert fixture.observations[0].reliability == "possible"
    file_id, content_hash = _file(p6_conn, tmp_path, name="applications.xlsx",
                                  body=b"PK\x03\x04cells")
    _observe(p6_conn, run_id="run-cells", file_id=file_id,
             content_hash=content_hash, raw="2025", zone="table",
             container_path=(Segment("sheet", index=2, label="Applications"),
                             Segment("row", index=7),
                             Segment("column", index=3, label="C7")),
             extractor="xlsx.cells", source_type="spreadsheet",
             reliability="possible")

    direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                 slots=DirectSlots(slots=(CELL_SLOT,)), screen=NO_CATALOGUE)
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert [(row["field_key"], row["reliability_state"]) for row in rows] == [
        ("application_cycle", DIRECT_STATE)]


def test_a_shipped_filesystem_mime_type_slot_fills_file_type(p6_conn, tmp_path):
    # `extractors.filesystem.METADATA_SLOTS` publishes `mime_type` at zone
    # `metadata`, reliability `direct` -- a §3.5 slot that exists today, so at least
    # one slot in this task is proved against a real publisher and not only a shape.
    file_id, content_hash = _file(p6_conn, tmp_path, name="essay.pdf", body=b"%PDF-3")
    _observe(p6_conn, run_id="run-fsm", file_id=file_id, content_hash=content_hash,
             raw="application/pdf", zone="metadata",
             container_path=(Segment("field", label="mime_type"),),
             extractor="filesystem.record", version="0.1.0",
             source_type="filesystem", analysis_tier="filesystem")

    direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                 slots=DirectSlots(slots=(FILE_TYPE_SLOT,)), screen=NO_CATALOGUE)
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert [(row["field_key"], row["reliability_state"]) for row in rows] == [
        ("file_type", DIRECT_STATE)]


# --- §3.12: a producer may not create a field ------------------------------------

def test_a_slot_naming_a_field_outside_the_catalogue_raises_and_creates_nothing(
        p6_conn, tmp_path):
    # §3.5's "document title" slot has no catalogue field, and §3.12 is the reason
    # the answer is a raise rather than a new row: "The system may create new values
    # ... but it should not invent new fields automatically." Done-means 3's negative
    # half, reached from a producer instead of from Task 2's own test.
    file_id, content_hash = _file(p6_conn, tmp_path, name="syllabus.pdf",
                                  body=b"%PDF-4")
    _observe(p6_conn, run_id="run-title", file_id=file_id,
             content_hash=content_hash, raw="BUSIB 4300 Syllabus", zone="title",
             container_path=(Segment("page", index=1),))

    with pytest.raises(FieldNotInCatalogue):
        direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                     slots=DirectSlots(slots=(TITLE_SLOT,)), screen=NO_CATALOGUE)
    assert facts_for_file(p6_conn, file_id, content_hash) == []


# --- the abstention is NOT this producer's -----------------------------------

def test_a_slot_that_matches_nothing_writes_no_fact_and_no_unresolved_row(
        p6_conn, tmp_path):
    # B7's row answers §8.5's "Did it abstain when evidence was absent?". A field the
    # direct producer did not fill is a field the rule and model producers have not
    # tried yet (§8.6's order), so a row here would report an abstention that has not
    # happened. The sequencer writes it once, after every producer has had its turn.
    file_id, content_hash = _file(p6_conn, tmp_path, name="empty.pdf", body=b"%PDF-5")
    _observe(p6_conn, run_id="run-none", file_id=file_id, content_hash=content_hash,
             raw="Columbia", zone="body", reliability="possible")

    assert direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                        slots=DirectSlots(slots=(EXIF_SLOT,)),
                        screen=NO_CATALOGUE) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


# --- evidence, grouping and the per-version scope --------------------------------

def test_two_observations_of_one_value_make_one_fact_citing_both(p6_conn, tmp_path):
    # §3.1: "Every fact preserves where it came from" -- plural. Two readings of the
    # same capture time are one claim with two citations, not two identical facts.
    # This is not an answer to OQ6: multiplicity asks how many VALUES a field may
    # hold, and both readings carry one.
    file_id, content_hash = _file(p6_conn, tmp_path, name="IMG_9.heic",
                                  body=b"\x00two-readers")
    first = _observe(p6_conn, run_id="run-a", file_id=file_id,
                     content_hash=content_hash, raw=EXIF_RAW, zone="metadata",
                     container_path=(Segment("field", label="DateTimeOriginal"),),
                     extractor="image.exif", source_type="image")
    second = _observe(p6_conn, run_id="run-b", file_id=file_id,
                      content_hash=content_hash, raw=EXIF_RAW, zone="metadata",
                      container_path=(Segment("field", label="DateTimeOriginal"),),
                      extractor="image.metadata", source_type="image")

    written = direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                           slots=DirectSlots(slots=(EXIF_SLOT,)), screen=NO_CATALOGUE)
    assert len(written) == 1
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert json.loads(rows[0]["evidence_refs"]) == sorted(
        {first.observation_key, second.observation_key})


def test_every_evidence_ref_is_an_observation_key(p6_conn, photo):
    # M14. Task 4 raises `EvidenceRequired` on anything else; this asserts the shape
    # this producer actually stores rather than trusting the writer's guard.
    file_id, content_hash, _ = photo
    direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                 slots=DirectSlots(slots=(EXIF_SLOT,)), screen=NO_CATALOGUE)
    refs = json.loads(facts_for_file(p6_conn, file_id, content_hash)[0]["evidence_refs"])
    assert refs and all(ref.startswith("sha256:") for ref in refs)


def test_a_prior_versions_observation_is_not_cited(p6_conn, tmp_path):
    # §3.4's cache key and §8.2's records are per content hash. Task 7 owns the
    # filter; this asserts the producer uses it and does not reach for
    # `observations_for_file` itself.
    file_id, content_hash = _file(p6_conn, tmp_path, name="IMG_5.heic",
                                  body=b"\x00version-one")
    old = _observe(p6_conn, run_id="run-old", file_id=file_id,
                   content_hash=content_hash, raw=EXIF_RAW, zone="metadata",
                   container_path=(Segment("field", label="DateTimeOriginal"),),
                   extractor="image.exif", source_type="image")
    second_hash = "c" * 64
    _observe(p6_conn, run_id="run-new", file_id=file_id, content_hash=second_hash,
             raw="2026:08:01 09:00:00", zone="metadata",
             container_path=(Segment("field", label="DateTimeOriginal"),),
             extractor="image.exif", source_type="image")

    direct_facts(p6_conn, file_id=file_id, content_hash=second_hash,
                 slots=DirectSlots(slots=(EXIF_SLOT,)), screen=NO_CATALOGUE)
    rows = facts_for_file(p6_conn, file_id, second_hash)
    assert [row["field_key"] for row in rows] == ["capture_date"]
    assert old.observation_key not in json.loads(rows[0]["evidence_refs"])
    assert facts_for_file(p6_conn, file_id, content_hash) == []


def test_the_result_does_not_depend_on_the_order_the_slots_were_declared(
        p6_conn, tmp_path):
    # Same reason as Task 7's shuffle test: an outcome that depends on the caller's
    # list order is an outcome §8.5's replay reports as a regression when nothing
    # changed. The write order is (field_key, canonical_value), imposed here.
    def resolve(slots):
        file_id, content_hash = _file(p6_conn, tmp_path,
                                      name=f"{len(slots)}-{slots[0].slot_id}.heic",
                                      body=b"\x00order" + slots[0].slot_id.encode())
        _observe(p6_conn, run_id=f"r-x-{file_id}", file_id=file_id,
                 content_hash=content_hash, raw=EXIF_RAW, zone="metadata",
                 container_path=(Segment("field", label="DateTimeOriginal"),),
                 extractor="image.exif", source_type="image")
        _observe(p6_conn, run_id=f"r-y-{file_id}", file_id=file_id,
                 content_hash=content_hash, raw="application/pdf", zone="metadata",
                 container_path=(Segment("field", label="mime_type"),),
                 extractor="filesystem.record", version="0.1.0",
                 source_type="filesystem", analysis_tier="filesystem")
        direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                     slots=DirectSlots(slots=slots), screen=NO_CATALOGUE)
        return [row["field_key"]
                for row in facts_for_file(p6_conn, file_id, content_hash)]

    assert resolve((EXIF_SLOT, FILE_TYPE_SLOT)) == resolve(
        (FILE_TYPE_SLOT, EXIF_SLOT)) == ["capture_date", "file_type"]


# --- P1 owns identity ------------------------------------------------------------

def test_a_file_p1_does_not_hold_raises_rather_than_writing_a_direct_fact(p6_conn):
    # P1 owns §1.2's identity and P6 re-observes no filesystem. `direct` is the
    # strongest state a deterministic producer writes; writing one against a file the
    # system of record has never seen would put an unanchored fact in the top tier.
    with pytest.raises(UnknownFile):
        direct_facts(p6_conn, file_id="file-that-p1-never-recorded",
                     content_hash="d" * 64,
                     slots=DirectSlots(slots=(EXIF_SLOT,)), screen=NO_CATALOGUE)


# --- the injection (F8) ----------------------------------------------------------

def test_direct_slots_has_no_default(p6_conn):
    # "Every threshold is injected with no default." A default slot table would be
    # P6 minting the EXIF tag names P5 deliberately refused to publish (P4 D7).
    with pytest.raises(TypeError):
        DirectSlots()
    with pytest.raises(TypeError):
        DirectSlot(slot_id="incomplete", field_key="capture_date")


def test_facts_direct_names_no_slot_and_holds_no_catalogue():
    # Runtime introspection, not a source-text search: a text search matches comments
    # and docstrings and has produced a false result nine times on this project. The
    # module-level namespace must hold no container at all -- every imported symbol is
    # bound to a private name precisely so this guard has nothing to excuse.
    forbidden = {"DateTimeOriginal", "CreateDate", "ModifyDate", "Producer",
                 "Creator", "Author", "Title", "mime_type", "observed_timestamps",
                 "normalized_filename", "extension"}
    assert _code_strings(direct_module) & forbidden == set()

    containers = {name: value for name, value in vars(direct_module).items()
                  if not name.startswith("_")
                  and isinstance(value, (tuple, list, dict, set, frozenset))}
    assert containers == {}


def test_facts_direct_holds_no_date_knowledge():
    # §3.10: "no fuzzy date parsing, ever", and §3.2's `2026-07-17` is produced by
    # the injected canonicaliser above. If this module could turn `2026:07:17
    # 14:03:22` into a date on its own it would be Task 12's job done twice, in the
    # one place with no pattern id to name.
    assert "re" not in vars(direct_module)
    assert not [name for name in vars(direct_module) if "date" in name.lower()]
    # Two adjacent digits, not one: `UnknownFile`'s message names P1 and P6, and a
    # part number is not a date format. Any year, offset, or `%Y:%m:%d` fragment has
    # two in a row.
    assert not [literal for literal in _code_strings(direct_module)
                if any(left.isdigit() and right.isdigit()
                       for left, right in zip(literal, literal[1:]))]


# --- §3.5's slots are plural, and two of them may share a locator -----------------


def test_two_slots_can_read_one_locator_and_claim_different_readings(
        p6_conn, tmp_path):
    """`names` alone cannot tell a course code from a term, and that is why the
    shipped deployment could only ever declare ONE slot.

    §3.5 speaks of slots in the plural, and `00`:78's own recommended tree is
    `Academics/Columbia/2026-Spring/PHYS1401/Homework` -- four dimensions, so at
    least two of them have to be read out of the same document text. But `names`
    is a predicate over the LOCATOR, and a course code and a term sitting in the
    same body share every locator prefix there is. A deployment that declared both
    slots would have each claim the other's readings, and every file would carry a
    term called PHYS1401 and a subject called 2026-Spring.

    So `matches` is added beside it: a predicate over the RAW READING, defaulting
    to None, which claims everything exactly as before. It is the smallest thing
    that makes §3.5's plural true, and it invents no pattern -- the predicate is
    the caller's, like `names` and `canonical` either side of it.
    """
    file_id, content_hash = _file(p6_conn, tmp_path, name="Syllabus.pdf",
                                  body=b"syllabus")
    for raw in ("PHYS1401", "2026-Spring"):
        _observe(p6_conn, run_id=f"run-{raw}", file_id=file_id,
                 content_hash=content_hash, raw=raw, zone="body",
                 extractor="text.structured", source_type="text_document")

    subject = DirectSlot(
        slot_id="text.subject", field_key="subject",
        names=lambda locator: True,
        matches=lambda raw: raw[0].isalpha(),
        canonical=lambda raw: raw)
    term = DirectSlot(
        slot_id="text.term", field_key="term",
        names=lambda locator: True,
        matches=lambda raw: raw[0].isdigit(),
        canonical=lambda raw: raw)

    direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                 slots=DirectSlots(slots=(subject, term)), screen=NO_CATALOGUE)

    by_field = {}
    for fact in facts_for_file(p6_conn, file_id, content_hash):
        by_field.setdefault(fact["field_key"], set()).add(
            values_by_id(p6_conn)[fact["value_id"]])

    assert by_field.get("subject") == {"PHYS1401"}, by_field
    assert by_field.get("term") == {"2026-Spring"}, by_field


def test_a_slot_with_no_reading_predicate_still_claims_every_reading(
        p6_conn, tmp_path):
    """The negative twin, and the compatibility guarantee. `matches` defaults to
    None, and None must mean "claims everything" exactly as before -- not
    "claims nothing", which would silently empty every existing deployment."""
    file_id, content_hash = _file(p6_conn, tmp_path, name="Syllabus.pdf",
                                  body=b"syllabus")
    for raw in ("PHYS1401", "2026-Spring"):
        _observe(p6_conn, run_id=f"run2-{raw}", file_id=file_id,
                 content_hash=content_hash, raw=raw, zone="body",
                 extractor="text.structured", source_type="text_document")

    everything = DirectSlot(
        slot_id="text.subject", field_key="subject",
        names=lambda locator: True, canonical=lambda raw: raw)

    direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                 slots=DirectSlots(slots=(everything,)), screen=NO_CATALOGUE)

    values = {values_by_id(p6_conn)[fact["value_id"]]
              for fact in facts_for_file(p6_conn, file_id, content_hash)
              if fact["field_key"] == "subject"}
    assert values == {"PHYS1401", "2026-Spring"}


def values_by_id(conn):
    return {row["value_id"]: row["canonical_value"]
            for row in conn.execute('SELECT value_id, canonical_value FROM "values"')}
