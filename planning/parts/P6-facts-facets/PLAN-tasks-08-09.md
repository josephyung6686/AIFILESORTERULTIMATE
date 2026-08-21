### Task 8: Direct facts — §3.5's four explicit slots

**Files:**
- Create: `src/facts/direct.py`
- Test: `tests/p6/test_p6_direct.py`

**Interfaces:**
- Consumes: `facts.evidence`, `facts.file_facts.write_fact`, `facts.values.ensure_value`,
  `database_agent.files_table.get_file`.
- Produces: `direct_facts(conn, *, file_id, content_hash, slots: DirectSlots) -> tuple[str, ...]`,
  `DirectSlots` — an injected frozen dataclass of slot-name predicates, no defaults.
- Also imports, because the skeleton's `Consumes:` line predates Task 4's signature and
  `write_fact` requires a `cache_key`: `facts.cache.fact_cache_key`, `facts.states.STATES`,
  `facts.file_facts.FACT_ORIGINS`, `facts.values.VALUE_ORIGINS`,
  `evidence_shape.canonical.canonical_json`, `evidence_shape.vocabulary.ANALYSIS_TIERS`. It reads
  none of them for anything but the cache key and the two enumerations it addresses by index.
- Also produces, beyond the skeleton's list and for the same reason Task 7 publishes `UnknownRun`:
  `DirectSlot` (the member of `DirectSlots.slots`), `DIRECT_STATE`, `DIRECT_ORIGIN`, `UnknownFile`.
  Nothing in the skeleton's list is renamed.

**Done-means:** 5, and part of 4.

**What "part of 4" is, stated exactly, because the whole of it is not this task's.** Done-means 4 is
the §3.2 fixture producing `subject`, term and work type. **None of those three is a direct fact** —
they come from a filename, a PDF title and a page-one heading, and §3.5 gives text to the *rule*
producer (Task 10), which is why Task 10's Done-means line reads *"8, and the `validated` half of
4"*. What Task 8 owns of item 4 is its last clause: *"each observation's `raw value` unchanged
afterwards (§3.2, §2.8)"*. This task proves it for the one fixture where the temptation to rewrite is
real — the EXIF reading, whose stored form (`2026:07:17 14:03:22`) is not the fact's form
(`2026-07-17`).

**The one rule this module exists to hold: the slot decides, and nothing else does.**

§3.5, verbatim: *"Deterministic extractors create direct facts when the information comes from a
reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled
form field."* §3.13 says the same in the reliability vocabulary: *"A direct fact was read from a
reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled
form field."*

Both sentences describe a **location**, never a value and never a confidence. That is not a reading
imposed here; it is P4's own fixture 6, whose design case is written on the fixture:

> `6 · §2.2 — direct describes the slot, not the value's usefulness` — `raw_value = "python-docx"`,
> zone `metadata`, locator `metadata:field=Producer`, `reliability = "direct"`.

So this module applies **no** test to the observation's own `reliability`. Two consequences, and both
are tests below:

- **A slot match on a `possible` observation still produces a `direct` fact.** P4's fixture 12 is
  §3.5's fourth slot — *"dates or identifiers from labeled cells"*, locator
  `table:sheet=2/row=7/column=3` — and P4 marks it `reliability = "possible"`. A gate on the
  observation's reliability would make one of the four slots §3.5 names unreachable against P4's own
  fixture for it. P4's two-member `EXTRACTOR_RELIABILITY_STATES` is what an extractor may claim about
  an *observation*; the fact's six-state vocabulary is P6's, and Task 1 asserts that boundary from
  both sides. Confusing the two is the same error in the other direction.
- **A `Producer` slot would therefore turn `python-docx` into a `direct` fact.** It is stopped by
  Task 9's suppression tier firing first, not by anything here. Task 8 declares no metadata-property
  slot and imports nothing from `facts.discount` — the ordering obligation is the sequencer's
  (Task 24) and is named in *Contract ambiguities* rather than assumed.

**Why the slot name is injected and not written down (F8).** P5's `image.py` carries the EXIF tag
only as a reader-supplied `container_path` segment label and spells no tag name anywhere, on purpose
(P4 D7: *"the source format's own slot name, verbatim"*). P4's fixture 7 happens to use
`DateTimeOriginal`, but a fixture is data, not a vocabulary. A literal `"DateTimeOriginal"` in
`src/facts/` would be P6 minting a vocabulary member P5 deliberately refused to publish, and it would
be wrong for the first camera whose reader spells it differently. So `DirectSlots` arrives at the
call, with **no default**, and `facts.direct` contains not one slot name. The catalogue behind that
injection **does not exist**; it is the same shape as catalogue 01 and belongs beside it (F8).

**The predicate reads P4's `locator`, which is the slot's published name.** `Observation.locator` is
a P4 property (verified: `metadata:field=DateTimeOriginal`, `title:page=1`,
`table:sheet=2/row=7/column=3`, `metadata:field=Producer`). Reading it means this module needs no
rule for *which* `container_path` segment names a slot — a rule that would differ per format and
would be exactly the branching §2.8 exists to prevent. Task 9 reads the `field`-kind segment's label
instead, because **catalogue 01 specifies that** in its `match_field` clause; the two reads are
different because their sources ask for different things, and neither is a helper the other could
share across a module boundary it does not own.

**How far §3.5's four slots actually reach today.** This is checked, not assumed, and two of the four
do not land in a fact:

| §3.5 slot | Publisher in the built system | Field it can fill | Status |
|---|---|---|---|
| EXIF timestamp | `image.exif` / P5's `image.py`, tag name as a segment label | `capture_date` | **produces a fact** (Done-means 5) |
| labeled form field | `xlsx.cells` and its siblings, fixture 12's shape | `application_cycle` | **produces a fact** |
| document title | `pdf.text`, zone `title`, fixture 2 | *none in the catalogue* | **raises `FieldNotInCatalogue`** — §3.12 forbids creating one at run time, so the refusal is the correct outcome and is the test |
| content hash | P1's `files.content_hash` — **not an observation** | — | **cannot be written here.** M14 makes every citation an `observation_key` and Task 4 raises `EvidenceRequired` on anything else, so a fact whose only evidence is a P1 column has no lawful form. Its design consumer is §8.3's duplicate family, which is Task 14's |

Verified against the shipped extractor, because this is where a plan invents a publisher that is not
there: `extractors.filesystem` emits `METADATA_SLOTS = ("normalized_filename", "extension",
"mime_type")` at `reliability = "direct"`, zone `metadata`, `extractor_name = "filesystem.record"`,
`analysis_tier = "filesystem"`. **`mime_type` is a real, shipped §3.5 slot** and fills `file_type`.
**No timestamp is among them**, so §3.13's "filesystem timestamp" — `creation_date` — has the slot
and no publisher. The test drives its shape and the gap is reported; the injection makes it a
one-line change on the day P5 adds the slot, which is the point of injecting it.

**Why `get_file` is consumed.** P1 owns identity (§1.2) and P6 re-observes no filesystem. A `direct`
fact is the strongest state a deterministic producer writes, and writing one against a `file_id` the
system of record does not hold would put an unanchored fact in the strongest tier. `direct_facts`
reads the row and raises `UnknownFile` when P1 has none. It reads **no value** out of it: the row's
`content_hash` and `observed_timestamps` are the two columns a careless implementation would mine for
§3.5's first and second slots, and neither is citable evidence.

**This producer never abstains.** `facts.unresolved` is absent from its `Consumes:` and that is
deliberate rather than an omission. A slot that matched nothing is not a refusal — §8.6's order runs
direct, then rule-validated, then the model, and a field that no direct slot filled is a field the
next producer has not tried yet. Writing an `unresolved` row here would report *"P6 abstained"* for
every field on every file before the work had been done, which is the exact opposite of B7's purpose:
the row exists so §8.5's *"Did it abstain when evidence was absent?"* has a truthful answer. The
abstention is written once, by the sequencer, after every producer has had its turn.

**Ordering.** `observations_for_version` already returns Task 7's total order, keyed on
`observation_key`. This module sorts once more, by `(field_key, canonical_value)`, before it writes,
so the returned tuple is identical whether the caller lists its slots in one order or another and
whether P4's rows went in forwards or backwards. Same reason as Task 7's: a corpus extracted twice
must produce one answer, or §8.5's replay compares a run with itself and reports a regression.

- [ ] **Step 1: Write the failing test**

```python
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
from facts.fields import FieldNotInCatalogue
from facts.file_facts import facts_for_file
from facts.unresolved import unresolved_for_file
from facts.values import values_in_field

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
                           slots=DirectSlots(slots=(EXIF_SLOT,)))
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
                 slots=DirectSlots(slots=(EXIF_SLOT,)))

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
                 slots=DirectSlots(slots=(CREATION_SLOT,)))
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
                 slots=DirectSlots(slots=(EXIF_SLOT,)))
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
                        slots=DirectSlots(slots=(EXIF_SLOT, CREATION_SLOT))) == ()
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
                 slots=DirectSlots(slots=(CELL_SLOT,)))
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
                 slots=DirectSlots(slots=(FILE_TYPE_SLOT,)))
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert [(row["field_key"], row["reliability_state"]) for row in rows] == [
        ("file_type", DIRECT_STATE)]


# --- §3.12: a producer may not create a field ------------------------------------

def test_a_slot_naming_a_field_outside_the_catalogue_raises_and_creates_nothing(
        p6_conn, tmp_path):
    # §3.5's "document title" slot has no catalogue field, and §3.12 is the reason
    # the answer is a raise rather than a new row: "the system may create new values
    # ... but it should not invent new fields automatically". Done-means 3's negative
    # half, reached from a producer instead of from Task 2's own test.
    file_id, content_hash = _file(p6_conn, tmp_path, name="syllabus.pdf",
                                  body=b"%PDF-4")
    _observe(p6_conn, run_id="run-title", file_id=file_id,
             content_hash=content_hash, raw="BUSIB 4300 Syllabus", zone="title",
             container_path=(Segment("page", index=1),))

    with pytest.raises(FieldNotInCatalogue):
        direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                     slots=DirectSlots(slots=(TITLE_SLOT,)))
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
                        slots=DirectSlots(slots=(EXIF_SLOT,))) == ()
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
                           slots=DirectSlots(slots=(EXIF_SLOT,)))
    assert len(written) == 1
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert json.loads(rows[0]["evidence_refs"]) == sorted(
        {first.observation_key, second.observation_key})


def test_every_evidence_ref_is_an_observation_key(p6_conn, photo):
    # M14. Task 4 raises `EvidenceRequired` on anything else; this asserts the shape
    # this producer actually stores rather than trusting the writer's guard.
    file_id, content_hash, _ = photo
    direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                 slots=DirectSlots(slots=(EXIF_SLOT,)))
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
                 slots=DirectSlots(slots=(EXIF_SLOT,)))
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
                     slots=DirectSlots(slots=slots))
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
                     slots=DirectSlots(slots=(EXIF_SLOT,)))


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
    assert {literal for literal in _code_strings(direct_module)
            if any(character.isdigit() for character in literal)} == set()
```

- [ ] **Step 2: Run the test and read the failure**

Run: `pytest tests/p6/test_p6_direct.py -v`

Expected: FAIL — collection error, `ModuleNotFoundError: No module named 'facts.direct'`. Tasks 1–6
are green and Task 7 has landed, so `facts.evidence`, `facts.fields`, `facts.values`,
`facts.file_facts`, `facts.unresolved` and `facts.cache` all import; `facts.direct` is the only
missing name. **17 tests fail to collect, 0 pass.**

- [ ] **Step 3: Write the implementation**

```python
# src/facts/direct.py
"""§3.5's direct facts. The slot decides, and the slot is injected.

§3.5: "Deterministic extractors create direct facts when the information comes from a
reliable, explicit source, such as a content hash, EXIF timestamp, a document title,
or a labeled form field." §3.13 repeats it in the reliability vocabulary. Both
sentences name a LOCATION, never a value and never a confidence -- which is P4's own
fixture 6, whose design case reads "direct describes the slot, not the value's
usefulness" over a `raw_value` of `python-docx`.

Three consequences, and each is a test rather than a comment:

* **No test is applied to the observation's own `reliability`.** P4's fixture 12 is
  §3.5's labeled form field and P4 marks it `possible`; a gate here would make one of
  the four named slots unreachable against P4's own fixture for it. An extractor's
  two admissible states are a claim about an OBSERVATION (P4 D11); the fact's six are
  P6's, and Task 1 asserts that boundary from both sides.

* **A `Producer` slot would therefore make `python-docx` a direct fact.** It is
  stopped by §2.2's suppression tier firing first (`facts.discount`), never by
  anything here. This module declares no slot and imports nothing from that one; the
  ordering is the sequencer's.

* **No slot name appears in this file.** P5 spells no EXIF tag name anywhere, on
  purpose (P4 D7: "the source format's own slot name, verbatim"), so a literal here
  would be P6 minting a vocabulary member P5 refused to publish. `DirectSlots`
  arrives at the call with no default. The catalogue behind it does not exist (F8).

The predicate reads P4's `locator` -- `metadata:field=DateTimeOriginal`,
`title:page=1`, `table:sheet=2/row=7/column=3` -- because that is the slot's
published name and reading it needs no rule for which `container_path` segment names
a slot. Such a rule would differ per format, which is what §2.8 exists to prevent.

This producer never abstains. §8.6's order is direct, then rule-validated, then the
model; a field no direct slot filled is a field the next producer has not tried. An
`unresolved` row here would answer §8.5's "Did it abstain when evidence was absent?"
with a claim that had not happened yet. The sequencer writes that row once, at the
end.

`get_file` is read for exactly one thing: P1 owns §1.2's identity, and a `direct`
fact -- the strongest state a deterministic producer writes -- must not be anchored
to a `file_id` the system of record does not hold. No VALUE is taken from the row:
`files.content_hash` and `files.observed_timestamps` are the two columns a careless
implementation would mine for §3.5's first and second slots, and neither is citable
evidence (M14 makes every citation an `observation_key`).
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Callable, Iterable

from database_agent.files_table import get_file as _get_file
from evidence_shape.canonical import canonical_json as _canonical_json
from evidence_shape.observation import Observation
from evidence_shape.vocabulary import ANALYSIS_TIERS as _ANALYSIS_TIERS

from facts.cache import fact_cache_key as _fact_cache_key
from facts.evidence import analysis_tier_for_observation as _tier_of
from facts.evidence import cite as _cite
from facts.evidence import observations_for_version as _observations_for_version
from facts.file_facts import FACT_ORIGINS as _FACT_ORIGINS
from facts.file_facts import write_fact as _write_fact
from facts.states import STATES as _STATES
from facts.values import VALUE_ORIGINS as _VALUE_ORIGINS
from facts.values import ensure_value as _ensure_value

#: §3.13's second state. Spelled by index rather than as a literal so `facts.states`
#: stays the one place a state name is written (Task 1).
DIRECT_STATE: str = _STATES[1]

#: §3.1's first of five origins -- the deterministic extractor. Also by index; Task 4
#: owns the spelling.
DIRECT_ORIGIN: str = _FACT_ORIGINS[0]


class UnknownFile(Exception):
    """P1 holds no `files` row for the `file_id` a direct fact was asked for."""


@dataclass(frozen=True)
class DirectSlot:
    """One of §3.5's explicit slots, named and canonicalised by the caller.

    `names` is a predicate over the slot's published name -- P4's
    `Observation.locator`. `canonical` turns the raw reading into the fact's value;
    §3.2's own example is `2026:07:17 14:03:22` becoming `2026-07-17`, and P6 owns
    neither end of that map (round 4's C-5: `normalize(field, raw_value)` is claimed
    by P8's Contract-in and disowned by P6's Task 17, so no part builds it). A
    canonicaliser that raises propagates: a broken injection must not arrive as a
    silent absence of facts (§8.6).
    """

    slot_id: str
    field_key: str
    names: Callable[[str], bool]
    canonical: Callable[[str], str]


@dataclass(frozen=True)
class DirectSlots:
    """The injected slot set. No default, so no call can omit it (F8)."""

    slots: tuple[DirectSlot, ...]


def direct_facts(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                 slots: DirectSlots) -> tuple[str, ...]:
    """§3.5's direct facts for one version of one file. Returns the fact ids.

    Every reading a slot claims becomes a `direct` fact citing the observation it was
    read from. Readings that agree on a value are ONE fact with several citations
    (§3.1: "Every fact preserves where it came from" -- plural); that is not an answer
    to OQ6, which asks how many values a field may hold.
    """
    if _get_file(conn, file_id) is None:
        raise UnknownFile(
            f"P1 holds no files row for {file_id!r}; P6 re-observes no filesystem "
            f"and will not anchor a {DIRECT_STATE!r} fact to a file the system of "
            f"record has never seen"
        )

    grouped: dict[tuple[str, str], list[Observation]] = {}
    for slot in slots.slots:
        for one in _observations_for_version(conn, file_id, content_hash):
            if slot.names(one.locator):
                key = (slot.field_key, slot.canonical(one.raw_value))
                grouped.setdefault(key, []).append(one)

    written: list[str] = []
    for (field_key, canonical_value) in sorted(grouped):
        cited = grouped[(field_key, canonical_value)]
        refs = tuple(sorted({_cite(one) for one in cited}))
        value_id = _ensure_value(conn, field_key=field_key,
                                 canonical_value=canonical_value,
                                 first_evidence_ref=refs[0],
                                 origin=_VALUE_ORIGINS[0])
        written.append(_write_fact(
            conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
            value_id=value_id, reliability_state=DIRECT_STATE,
            origin=DIRECT_ORIGIN, evidence_refs=refs,
            cache_key=_cache_key(conn, content_hash=content_hash,
                                 observations=cited),
            active=True))
    return tuple(written)


def _cache_key(conn: sqlite3.Connection, *, content_hash: str,
               observations: Iterable[Observation]) -> str:
    """§3.4's five parts for a fact built from several observations.

    §3.4 states one extractor version and one analysis tier; a fact citing several
    observations has several of each, and no task owns the reconciliation, so the
    rule is written out here rather than shared -- `facts.cache` is another task's
    module. The versions are the canonical JSON of the sorted distinct
    (name, version) pairs; the tier is the LAST one present in `ANALYSIS_TIERS`
    order -- filesystem < native < ocr < llm -- so a fact that cited an OCR reading
    lands outside the slot the native pass computed under, which is what makes
    preamble rule 5's pass 4 supersede rather than overwrite. Identical wording in
    `facts.families`, `facts.session` and `facts.discount`; see Contract ambiguities.
    """
    observations = tuple(observations)
    pairs = sorted({(one.extractor_name, one.extractor_version)
                    for one in observations})
    tiers = {_tier_of(conn, one) for one in observations}
    tier = max(tiers, key=_ANALYSIS_TIERS.index) if tiers else _ANALYSIS_TIERS[0]
    return _fact_cache_key(
        content_hash=content_hash,
        extractor_version=_canonical_json([list(pair) for pair in pairs]),
        analysis_tier=tier, model_identifier=None, prompt_fingerprint=None)
```

- [ ] **Step 4: Run the test and confirm it passes**

Run: `pytest tests/p6/test_p6_direct.py -v`

Expected: PASS — **17 passed**. The two that would have been silently wrong are
`test_the_slot_decides_and_not_the_observations_own_reliability`, which passes only because no gate
on `Observation.reliability` was written, and `test_facts_direct_holds_no_date_knowledge`, which
passes only because every import is bound to a private name and the module holds no digit-bearing
literal.

- [ ] **Step 5: Run the whole P6 suite, because Task 7's guards police this module**

Run: `pytest tests/p6 -q`

Expected: PASS. `tests/p6/test_p6_evidence.py` walks `pkgutil.iter_modules(facts.__path__)` and
fails if any module holds a `source_type`-keyed dict or a code string equal to a member of
`SOURCE_TYPES` or to one of P4's nineteen fixture extractor names. `facts.direct` has neither: the
only literals it contains are the two f-string message fragments in `UnknownFile`, and `"filesystem"`
— which is both a source type and an analysis tier — is reached as `_ANALYSIS_TIERS[0]` rather than
written down.

- [ ] **Step 6: Commit**

```bash
git add src/facts/direct.py tests/p6/test_p6_direct.py
git commit -m "feat(P6): §3.5 direct facts — the slot decides, and the slot is injected"
```

---
