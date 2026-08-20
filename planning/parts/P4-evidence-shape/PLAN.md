# P4 — Evidence Shape — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish §2.8's common evidence shape as running code — the three records ([`SPEC.md`](SPEC.md) *Contract out*: `evidence`, `extraction_runs`, `text_units`), the six closed vocabularies, the structured location scheme with its canonical locator, the content-addressed `observation_key`, and a conformance validator that enforces all twelve rules and **fails** a non-conforming observation rather than coercing it — so that P5's six extractors are written against a frozen contract and P6, P7, P8 and P2 can be built on its fixtures with no extractor in existence.

**Architecture:** P4 is a third package (`src/evidence_shape/`) inside P1's single local SQLite database (§0: *"Each part owns its own tables within it"*). It owns three tables, created by its own `create_evidence_schema` — **P1's `db.py` is not modified**. Twelve modules, one per published surface, split by record and by concern so a reviewer can reject one without touching its neighbours. P4 runs no extractor, opens no file, and reads no bytes off disk: every test below builds its records in memory or from a fixture string. That is what makes the whole part testable before P5 exists.

**Tech Stack:** Python 3.12 · stdlib only (`sqlite3`, `json`, `hashlib`, `uuid`, `dataclasses`, `unicodedata`, `ast`) · `pytest` · P1's `database_agent` package as the substrate · no third-party runtime dependencies.

---

## The authorship rule — read this before Task 1

**P4 authors no event. The acting part authors; P1 writes; P4 supplies the writer.** This is the single rule most likely to be got wrong here, because P4 ships the function that appends the `extraction` / `OCR` event and does not perform the extraction it records.

The design settles it three times over:

- **M8** ([`../../04-resolutions.md`](../../04-resolutions.md)): *"The acting part authors; P1 writes. P1 appends no event on its own initiative."*
- **P5's SPEC**, *Provenance*: *"**Events P5 appends** — two of §8.2's enumerated event types: `extraction` … and `OCR` … spelled as §8.2 spells them."* P5 is the acting part for the five native extractors and for OCR; P8 is the acting part for an `analysis_tier = llm` run (I4).
- **§8.2** itself requires *"the responsible subsystem"* on every event. A log whose `subsystem` names the schema library rather than the extractor cannot reconstruct what happened, which is the whole point of the log.

Concretely, in this plan:

- `evidence_shape` contains **no** `SUBSYSTEM` constant and **no** default author. Every writer that touches `events` takes required `author` and `component_version` keywords, exactly as P1's own `observe_path(conn, path, *, author, component_version, …)` does, and passes `author` straight into `events.subsystem`.
- P4 **refuses `author="P1"`** (M8: P1 originates nothing). It refuses nothing else, because it does not know who its callers will be.
- P4 **registers no event type** (P1's *Contract out §3*, rule 4: registration is a spec-level act). `extraction` and `OCR` are both among §8.2's nineteen reserved names, already in P1's frozen table.
- `OCR` is spelled `OCR` — capitals — because §8.2 spells it that way and P1's writer validates against that vocabulary (**MINOR 2**, [`../../05-minor-resolutions.md`](../../05-minor-resolutions.md)). The lowercase `ocr` in this plan is a **different thing**: `source_type = "ocr"` and `analysis_tier = "ocr"` are P4 vocabulary values, not event names. Task 1 asserts the distinction so nobody "normalizes" one into the other.

---

## Global Constraints

Every task's requirements implicitly include these. Values are copied verbatim from [`SPEC.md`](SPEC.md) and from [`../../01-product-design-structured.md`](../../01-product-design-structured.md).

- **P4 runs no extractor.** §2.8 is a shape, not a reader. `src/evidence_shape/` opens no file for content, imports no format library, and contains no MIME sniffing, no routing table, and no catalogue of strings to look for — all of that is P5's ([`SPEC.md`](SPEC.md) *Not owned here*). Task 18 asserts it.
- **P4 interprets nothing.** No field name, value, fact, domain, template, gazetteer, positional weight, destination, group or plan appears anywhere in `evidence_shape`. §2.8: *"Extraction does not create a final folder path, invent domains, merge all files that share one string, or treat model output as proof."*
- **No invented values.** No numeric threshold, no ceiling, no gazetteer, no category membership, no vocabulary the design does not spell. Where the design leaves a value open this plan holds a **key or a caller-supplied argument** — never a number and never a made-up enum. The one place this bites hardest is the §8.6 context budget: see *The context budget is caller-supplied* below.
- **Six closed vocabularies, and no seventh.** `zone` (15), segment `kind` (15), `source_type` (14), `reliability` (§3.13's six), `completeness` (nine, after C4), `analysis_tier` (four). Each is exactly the SPEC's list, in the SPEC's order. Adding a member is a P4 contract revision, not an implementation decision (segment-kind rule 5).
- **`raw_value` is never updated, ever** (RAW-2). Improvement is insert + supersede through P1's published three columns — `supersedes`, `superseded_by`, `supersede_reason` (**M1**; **MINOR 3** confirms the spelling is `supersede_reason`, never `supersession_reason`). P1's `preferred` is **not** adopted: §8.2 gives preference to the resolver and §3.2 places the resolver after extraction, so it lives on P6's `file_facts`.
- **`observation_key` excludes `extractor_version`, deliberately.** §8.5 requires the replay harness to compare a new extractor version against a prior result for the same content; identity that included the version would make every row a false diff and leave nothing to diff against. **This is not a bug to be fixed** (**MINOR 8**). Task 5 states the reason in the module docstring and asserts it.
- **`observation_key` is the citation handle**, never `observation_id` (**M14**). Every consumer that cites evidence — P6's `evidence_refs[]`, P8's dossier citations, P9's group support, P11's placement explanations — cites the key.
- **Absence is never an observation.** §2.6 forbids treating the absence of EXIF as proof of anything. Absence lives on `extraction_runs` (`completeness`, `coverage`, and the fact that a `complete` run emitted no such row) or nowhere.
- **`events` is INSERT-only.** P1 enforces it by SQL trigger. P4 issues no `UPDATE` and no `DELETE` against `events`, ever. Observations are superseded, never deleted (§8.2, §8.7).
- **P4 creates and modifies no P1 file.** `pyproject.toml`, `tests/conftest.py` and everything under `src/database_agent/` belong to P1. P1's `[tool.setuptools.packages.find] where = ["src"]` already discovers `evidence_shape`, and its `pythonpath = ["src"]` already makes it importable under pytest. P4's tests live in `tests/p4/` with their own `conftest.py` and inherit P1's root `conn` fixture without editing it.
- **`tests/p4/conftest.py` must not shadow P1's.** Under pytest's default prepend import mode, with no `__init__.py` under `tests/`, every `conftest.py` is imported as the top-level module `conftest` and the last one wins. P4's own fixtures may live in `tests/p4/conftest.py`; nothing imported across parts by name may.
- **Python 3.12**, stdlib only. `evidence_shape` adds no third-party dependency and no `pyproject.toml` change.
- **P1 must be green before Task 1 starts.** Run `pytest tests/ -q` and confirm P1's 152 tests pass; P4's first import failure otherwise reads as a P4 defect when it is a missing substrate.

### The context budget is caller-supplied

§8.6 lists **twelve** configurable ceilings and **none of them is a context length**. P1's `budget.CEILING_KEYS` holds fifteen keys (§8.6's twelve, with three namespaced across two owners per O10) and none of them is a context length either — and `set_ceiling` raises `KeyError` on a sixteenth.

So P4 does the only thing that invents nothing: `context_before` / `context_after` are **stored as the caller supplies them**, `context_truncated` records that the caller cut them, and `evidence_shape` contains no length, no default, and no truncation function. Whether the budget should become a sixteenth P1 ceiling key is a question for Joseph, recorded in the report accompanying this plan; until it is answered, holding no number is the only position that cannot be wrong. Task 18 asserts the package publishes no numeric constant outside its one allowlist.

### Two things called `region` — they are not the same thing

The SPEC publishes `region` twice and both spellings come straight out of §2.7/§2.8:

- **`Segment(kind="region", index=N)`** — the ordinal of a recognized OCR region, an addressing step inside `container_path`. This is §2.8's *"an OCR region"*. It appears in the locator: `ocr:page=4/region=2#0-24`.
- **`Location.region = Region(x, y, w, h, unit)`** — §2.7's *"locations or bounding boxes where available"*. It never appears in the locator; the grammar has no term for it.

Neither name is P4's to change — renaming one would be rewriting a published contract from inside an implementation. Task 3 asserts they are structurally distinct and Task 4 asserts the bounding box never reaches the locator, so the collision cannot silently become a defect.

---

## What P4 consumes from P1

Written against `src/database_agent/` **as implemented**, introspected on 2026-08-20 — not against P1's PLAN.md, whose header says it is a superseded construction record.

```text
database_agent.db          open_database(path, *, scan_roots=()) -> sqlite3.Connection
                           create_schema(conn) -> None
                           transaction(conn)                        contextmanager
database_agent.events      append_event(conn, **fields) -> int
                           EVENT_FIELDS: tuple[str, ...]            (eleven, MINOR 1)
                           RESERVED_EVENT_TYPES: frozenset[str]     (§8.2's nineteen)
                           MalformedEvent, UnregisteredEventType
database_agent.supersede   SUPERSEDE_COLUMNS: tuple[str, str, str]  (M1's three)
                           supersede_ddl(table) -> str
                           mark_superseded(conn, table, *, old_id, new_id, reason) -> None
                           chain(conn, table, record_id) -> list[sqlite3.Row]
database_agent.files_table observe_path(conn, path, *, author, component_version, …) -> str
                           get_file(conn, file_id) -> sqlite3.Row
```

`files_table` is consumed in **Task 19 only** — the walking-skeleton step, where a P3-shaped fixture creates the one `files` row the skeleton observation hangs off. No other task in this plan touches it, because P4's records are testable without a file row: the FK story is deliberately one-way (see Task 9).

**`mark_superseded` keys on a column literally named `record_id`.** P1's function is `UPDATE {table} … WHERE record_id = ?`, and P4's published primary key is `observation_id` (SPEC *Contract out*, Record 1). Renaming either would break a published contract, and writing a second supersede implementation would put one concept under two names — the most expensive recurring defect on this project. Task 9 resolves it with a SQLite **generated column**:

```sql
record_id TEXT GENERATED ALWAYS AS (observation_id) VIRTUAL
```

`observation_id` stays the published name, P1's tested `mark_superseded` and `chain` are reused verbatim, and no second implementation exists. Verified against SQLite 3.45.3 (the interpreter's bundled build) before this plan was written.

**`append_event` requires `subsystem`, `component_version`, `observed_at` and `explanation` non-empty**, and rejects any field outside its writable set. P4's event helper produces exactly the eleven §8.2 fields it fills and no twelfth; **P4 adds no event field** — §8.2 lists eleven and that is the count (MINOR 1).

**`open_database` already runs `create_schema`.** It stays public and idempotent, so every test here calls it explicitly and would still pass if that changed. P4's `create_evidence_schema` is a separate call and is never invoked for you.

---

## What P4 publishes, and who consumes it

| Surface | Consumed by | For |
|---|---|---|
| `Observation`, `OBSERVATION_FIELDS`, `OBSERVATION_ROW_FIELDS` | P5 (writes), P6/P7/P8/P9/P11 (read) | §2.8's shape |
| `observation_key(...)` | P6 `evidence_refs[]`, P8 citations, P9 support, P11 explanations, P2 diffs | M14's citation handle |
| `Location`, `Segment`, `TextSpan`, `TimeSpan`, `Region` | P5 (emits), P6 §3.7 (weights on `zone`), P8 (cites) | D1's one scheme |
| `serialize_locator` / `parse_locator` | everyone that cites one short handle | §8.2, §4.4, §3.6, §4.8, §6.10, §7.9 |
| `ExtractionRun`, `COMPLETENESS`, `Coverage` | P5 (writes), P2 (bundles, MINOR 9), P13 (§8.6's progress line, G14) | B1's single outcome record |
| `TextUnit`, `unit_locator` | P5 (writes), P7 (§8.4 redaction unit), P8 (§4.4 excerpts), P2 (§8.5 "did the text appear?") | G1/D12 |
| `conformance.validate_observation` / `validate_run` | six extractor authors, as their gate | SPEC *Conformance* |
| `determinism.observation_set_digest` / `assert_identical_observation_sets` / `replay_key` | P2 (§8.5 replay), §3.4's cache | conformance rule 8 |
| `ZONES`, `SEGMENT_KINDS`, `SOURCE_TYPES`, `RELIABILITY_STATES`, `ANALYSIS_TIERS` | P5, P6 | the closed vocabularies |
| `fixtures.FIXTURES` | P5 (write extractors against them), P6 (resolve with no extractor), P2 (bundle them) | SPEC *Done means* 5, 9 |

---

## File Structure

```text
src/evidence_shape/__init__.py        package marker; exports the three records
src/evidence_shape/authorship.py      the two §8.2 event names; the caller names itself (M8)
src/evidence_shape/vocabulary.py      the six closed vocabularies, and OPEN_QUESTIONS
src/evidence_shape/location.py        D1 — the structured location record and its parts
src/evidence_shape/locator.py         the canonical serialization and its parser
src/evidence_shape/canonical.py       byte-identical JSON, and the digest every key is built from
src/evidence_shape/observation.py     Record 1 — the observation, and observation_key (M14)
src/evidence_shape/runs.py            Record 2 — extraction_runs (D5, B1)
src/evidence_shape/text_units.py      Record 3 — text_units, and RAW-1 (D12, G1)
src/evidence_shape/schema.py          create_evidence_schema — three tables in P1's database
src/evidence_shape/store.py           the writers and readers, and the one §8.2 event per run
src/evidence_shape/conformance.py     the validator — the twelve rules, fail not coerce
src/evidence_shape/determinism.py     rule 8 — the compared observation set
src/evidence_shape/fixtures.py        the nineteen worked examples, as golden records

tests/p4/conftest.py                  p4_conn, record builders
tests/p4/test_p4_authorship.py        the authorship rule; MINOR 2's OCR spelling
tests/p4/test_p4_vocabulary.py        the six closed vocabularies
tests/p4/test_p4_location.py          D1, D2, D3; segment-kind rules 1-5
tests/p4/test_p4_locator.py           Done-means 3 — round-trip and escaping
tests/p4/test_p4_canonical.py         canonical JSON, and an injective digest
tests/p4/test_p4_observation.py       M5's three context fields; MINOR 8's key
tests/p4/test_p4_runs.py              D5, B1, M3 — the outcome record
tests/p4/test_p4_text_units.py        G1/D12 — the unit record
tests/p4/test_p4_schema.py            three tables, inside P1's database, P1 untouched
tests/p4/test_p4_store.py             the writers; the one §8.2 event per run
tests/p4/test_p4_raw1.py              Done-means 4 — RAW-1 on CJK and emoji
tests/p4/test_p4_conformance.py       the observation rules — 1, 2, 3, 4, 6, 7, 11, 12
tests/p4/test_p4_conformance_runs.py  the cross-record rules — 5, 9, 10
tests/p4/test_p4_supersession.py      Done-means 7
tests/p4/test_p4_determinism.py       Done-means 8
tests/p4/test_p4_fixtures.py          Done-means 5, and the coverage shortfall, named
tests/p4/test_p4_prohibitions.py      Done-means 6 — §2.8's four, plus the three derived
tests/p4/test_p4_no_invention.py      the guard, and every open question held open
tests/p4/test_p4_skeleton_step.py     Done-means 9 and the walking-skeleton fixture
```

---

### Task 1: Package skeleton, and the two §8.2 event names P4 supplies a writer for

**Files:**
- Create: `src/evidence_shape/__init__.py`
- Create: `src/evidence_shape/authorship.py`
- Create: `tests/p4/conftest.py`
- Test: `tests/p4/test_p4_authorship.py`

**Interfaces:**
- Consumes: `database_agent.events.RESERVED_EVENT_TYPES`, `database_agent.events.EVENT_FIELDS`, `database_agent.events.append_event`.
- Produces: `EXTRACTION_EVENT: str`, `OCR_EVENT: str`, `RUN_EVENT_TYPES: tuple[str, str]`, `OCR_ANALYSIS_TIER: str`, `UnauthoredEvent`, `run_event_type(analysis_tier) -> str`, `check_author(author) -> str`, `event_defaults(*, author, component_version, event_type, **fields) -> dict`.

**Why this is Task 1.** Every later task that writes a run appends one event, and the one thing that must never be got wrong is whose name lands in `subsystem`. Putting the check first means no later task has a plausible reason to type an author by hand, and Task 18's guard has exactly one place to look.

**`event_defaults` is a helper, not a writer.** It fills §8.2's authorship fields and returns a plain `dict` for the caller to hand to P1's `append_event`. It opens no connection and writes nothing, so there is no code path where P4 appends an event without a caller having decided to.

**Two vocabularies, one word.** `OCR_EVENT == "OCR"` is §8.2's event name (MINOR 2). `OCR_ANALYSIS_TIER == "ocr"` is I4's tier value, and `source_type = "ocr"` is §2.9's family. They are the same word in three vocabularies and P4 keeps all three spellings exactly as their owners spell them. The test below pins all three so a later "normalization" pass cannot quietly collapse them.

- [ ] **Step 1: Write the failing test**

```python
# tests/p4/test_p4_authorship.py
import pytest

from database_agent.events import EVENT_FIELDS, RESERVED_EVENT_TYPES, append_event

from evidence_shape.authorship import (
    EXTRACTION_EVENT, OCR_ANALYSIS_TIER, OCR_EVENT, RUN_EVENT_TYPES, UnauthoredEvent,
    check_author, event_defaults, run_event_type,
)


def test_the_two_run_events_are_8_2s_own_names():
    # MINOR 2 (05-minor-resolutions.md): "§8.2 spells it `OCR`." P1's writer
    # validates against that vocabulary, so a lowercase name fails at runtime.
    assert RUN_EVENT_TYPES == ("extraction", "OCR")
    assert EXTRACTION_EVENT == "extraction"
    assert OCR_EVENT == "OCR"


def test_both_run_events_are_reserved_8_2_names_so_p4_registers_nothing():
    # P1 Contract out §3, rule 4: registration is a spec-level act. Both names are
    # already in P1's frozen table; P4 declares neither.
    assert set(RUN_EVENT_TYPES) <= set(RESERVED_EVENT_TYPES)


def test_p4_publishes_no_registration_call_and_no_subsystem_of_its_own():
    # M8: the acting part authors; P1 writes; P4 supplies the writer and names nobody.
    import evidence_shape.authorship as module
    assert not [n for n, v in vars(module).items()
                if callable(v) and n.lower().startswith("register")]
    assert not [n for n in vars(module) if n == "SUBSYSTEM"]


def test_the_ocr_event_name_and_the_ocr_vocabulary_value_are_different_strings():
    # Same word, three vocabularies: §8.2's event name, I4's analysis tier, §2.9's
    # source-type family. P4 keeps each spelling as its owner spells it.
    assert OCR_EVENT == "OCR"
    assert OCR_ANALYSIS_TIER == "ocr"
    assert OCR_EVENT != OCR_ANALYSIS_TIER
    assert OCR_EVENT.lower() == OCR_ANALYSIS_TIER


def test_an_ocr_tier_run_appends_the_OCR_event_and_every_other_tier_appends_extraction():
    # SPEC, Cross-cutting answers -> Provenance: "`extraction`, or `OCR` when the
    # extractor is OCR". I4 makes "the extractor is OCR" the value `ocr`.
    assert run_event_type("ocr") == "OCR"
    assert run_event_type("native") == "extraction"
    assert run_event_type("filesystem") == "extraction"
    assert run_event_type("llm") == "extraction"


def test_the_caller_must_name_itself():
    assert check_author("P5") == "P5"
    with pytest.raises(UnauthoredEvent):
        check_author("")
    with pytest.raises(UnauthoredEvent):
        check_author(None)


def test_p1_may_never_be_named_as_the_author_of_an_extraction():
    # M8: "P1 appends no event on its own initiative." A log whose subsystem names
    # the storage substrate cannot reconstruct who read the document (§8.2).
    with pytest.raises(UnauthoredEvent):
        check_author("P1")


def test_event_defaults_fill_in_8_2s_authorship_fields():
    fields = event_defaults(author="P5", component_version="pdf.text/3.1.0",
                            event_type="extraction", file_id="f1",
                            content_hash="sha256:abc", explanation="{}")
    assert fields["subsystem"] == "P5"
    assert fields["component_version"] == "pdf.text/3.1.0"
    assert fields["event_type"] == "extraction"
    assert fields["file_id"] == "f1"
    assert fields["observed_at"]


def test_event_defaults_refuse_an_event_type_p4_supplies_no_writer_for():
    # P3 authors `hashing` and `stat observation`; P12 authors the move events.
    # P4 supplies a writer for exactly two.
    with pytest.raises(UnauthoredEvent):
        event_defaults(author="P5", component_version="v", event_type="hashing")


def test_event_defaults_refuse_a_field_outside_8_2s_eleven():
    # MINOR 1: §8.2 lists eleven event fields. P4 adds none.
    with pytest.raises(UnauthoredEvent):
        event_defaults(author="P5", component_version="v", event_type="extraction",
                       observation_key="sha256:deadbeef")
    assert len(EVENT_FIELDS) == 11


def test_what_event_defaults_produces_is_accepted_by_p1s_writer(conn):
    # The contract is only real if P1 takes it. `events.file_id` carries no foreign
    # key, so this needs no `files` row and no extractor.
    event_id = append_event(conn, **event_defaults(
        author="P5", component_version="ocr.apple_vision/2.4.1", event_type="OCR",
        file_id="f1", content_hash="sha256:abc", explanation='{"run_id": "r1"}'))
    row = conn.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
    assert row["event_type"] == "OCR"
    assert row["subsystem"] == "P5"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p4/test_p4_authorship.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'evidence_shape'`

- [ ] **Step 3: Write the implementation**

```python
# src/evidence_shape/__init__.py
"""P4 — the evidence shape (§2.8).

Three records, six closed vocabularies, one location scheme, one conformance
validator. No extractor, no file reading, no interpretation.
"""
```

```python
# src/evidence_shape/authorship.py
"""P4 authors no event: the acting part authors, P1 writes, P4 supplies the writer.

M8 (04-resolutions.md): "The acting part authors; P1 writes. P1 appends no event on
its own initiative." P5's SPEC claims the `extraction` and `OCR` events for itself,
and P8 is the acting part for an `analysis_tier = llm` run (I4). This module
therefore publishes no subsystem name and no default author; every caller names
itself, exactly as P1's own `observe_path(conn, path, *, author, ...)` requires.

`OCR` is spelled with capitals because §8.2 spells it that way and P1's writer
validates the event type against that vocabulary (MINOR 2, 05-minor-resolutions.md).
The lowercase word in `analysis_tier` and `source_type` belongs to two other
vocabularies and is not this name.
"""
from __future__ import annotations

from datetime import datetime, timezone

from database_agent.events import EVENT_FIELDS, RESERVED_EVENT_TYPES

#: §8.2's own two names for what an extraction run is. Both reserved; P4 registers
#: neither, because registration is a spec-level act (P1 Contract out §3, rule 4).
EXTRACTION_EVENT = "extraction"
OCR_EVENT = "OCR"
RUN_EVENT_TYPES: tuple[str, str] = (EXTRACTION_EVENT, OCR_EVENT)

#: I4's tier whose run is an OCR event rather than an extraction event. SPEC,
#: Cross-cutting answers -> Provenance: "`extraction`, or `OCR` when the extractor
#: is OCR"; I4 makes "the extractor is OCR" the closed value `ocr`.
OCR_ANALYSIS_TIER = "ocr"

#: M8: a caller naming P1 as the author of an extraction is recording that the
#: storage substrate read the document.
_STORAGE_SUBSYSTEM = "P1"


class UnauthoredEvent(Exception):
    """A run event with no responsible subsystem (§8.2), or with P1 named as one."""


def run_event_type(analysis_tier: str) -> str:
    """Which of §8.2's two names this run's event carries."""
    return OCR_EVENT if analysis_tier == OCR_ANALYSIS_TIER else EXTRACTION_EVENT


def check_author(author: str | None) -> str:
    """§8.2 requires "the responsible subsystem". P4 supplies no default for it."""
    if not author:
        raise UnauthoredEvent(
            "§8.2 requires the responsible subsystem on every event; P4 authors no "
            "event and supplies no default author"
        )
    if author == _STORAGE_SUBSYSTEM:
        raise UnauthoredEvent(
            "P1 stores; it originates no event (M8). Name the acting part: P5 for a "
            "filesystem, native or OCR run, P8 for an llm-tier run."
        )
    return author


def event_defaults(*, author: str, component_version: str, event_type: str,
                   **fields) -> dict[str, object]:
    """§8.2's authorship fields, ready for P1's `append_event`. Writes nothing.

    A caller-supplied `observed_at` wins, so a replay can pin the time (§8.5).
    """
    check_author(author)
    if event_type not in RUN_EVENT_TYPES:
        raise UnauthoredEvent(
            f"{event_type!r} is not one of the two events an extraction run appends "
            f"{RUN_EVENT_TYPES}; P4 supplies a writer for no other event type"
        )
    unknown = sorted(set(fields) - set(EVENT_FIELDS))
    if unknown:
        raise UnauthoredEvent(
            f"{unknown} are not among §8.2's eleven event fields (MINOR 1); P4 adds none"
        )
    return {
        "event_type": event_type,
        "subsystem": author,
        "component_version": component_version,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        **fields,
    }
```

```python
# tests/p4/conftest.py
"""P4's fixtures. P1's `tests/conftest.py` supplies `conn` and is not modified.

Nothing here may be imported across parts by name: under pytest's default prepend
import mode every `conftest.py` becomes the top-level module `conftest`, and the
last one imported wins.
"""
from __future__ import annotations

import pytest

#: A pinned observation time, so a test that compares two records is comparing what
#: the extractor produced and not two readings of the wall clock (§8.5 replay).
FIXED_OBSERVED_AT = "2026-08-19T14:03:22+00:00"


@pytest.fixture()
def observed_at() -> str:
    return FIXED_OBSERVED_AT
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p4/test_p4_authorship.py -v`
Expected: PASS — 11 passed

- [ ] **Step 5: Commit**

```bash
git add src/evidence_shape/__init__.py src/evidence_shape/authorship.py tests/p4/conftest.py tests/p4/test_p4_authorship.py
git commit -m "feat(P4): the two §8.2 run events; the caller names itself, P4 authors none"
```

---

### Task 2: The six closed vocabularies, and the five questions P4 holds open

**Files:**
- Create: `src/evidence_shape/vocabulary.py`
- Test: `tests/p4/test_p4_vocabulary.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `SHAPE_VERSION: int`, `ZONES`, `INDEXED_SEGMENT_KINDS`, `LABEL_SEGMENT_KINDS`, `SEGMENT_KINDS`, `SOURCE_TYPES`, `RELIABILITY_STATES`, `EXTRACTOR_RELIABILITY_STATES`, `COMPLETENESS`, `ZERO_OBSERVATION_COMPLETENESS`, `ANALYSIS_TIERS`, `SIGNAL_TIERS`, `REGION_UNITS`, `OPEN_QUESTIONS`, `NotInVocabulary`, `check(value, vocabulary, *, name)`.

**Every value here is the SPEC's, in the SPEC's order, and there is no seventh vocabulary.** Each zone and each source type carries a design citation in the SPEC's own tables; this task copies them and adds nothing. Segment-kind rule 5: *"Adding a zone or a kind is a P4 contract revision plus a shape-version bump. An extractor that needs one and ships it locally has broken the contract for every consumer."*

**One `check`, not nine near-identical checkers.** A closed vocabulary is one concept; giving it nine functions is how the second spelling of a value gets in. `check` rejects and never coerces — no case folding, no stripping, no nearest-match. §2.8's whole premise is that six extractors emit one shape, and a checker that quietly accepted `Heading` would let six spellings of one zone through.

**`analysis_tier` is not `source_type`, even where they share a word.** I4 ([`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md)): *"P4's observation `source_type` says where a value was read… `analysis_tier` says which process produced the *run*. An OCR run is `tier = ocr`; its observations may still have `source_type = ocr`. A native PDF run is `tier = native` even when a heading observation looks similar to an OCR heading."* Two tuples, two fields, and the test below pins the overlap so nobody merges them.

**`EXTRACTOR_RELIABILITY_STATES` is a strict subset, not a second vocabulary** (D11). §3.13's six are the only reliability vocabulary the design defines; extractors may write two of them. `validated`, `llm_supported`, `user_confirmed` and `rejected` are fact-layer outcomes (§3.5). Whether observations and facts *should* share one vocabulary is **Open question 3** and is held open here, not answered: P4 reuses §3.13 rather than minting a parallel set, and if P6 defines a separate observation-level vocabulary, D11 and conformance rule 3 change.

**`ZERO_OBSERVATION_COMPLETENESS` is three values, not five** (**M3**). `unreadable` and `partial` runs may and normally do carry observations: §2.9 requires an unsupported proprietary format be *"recorded as indexed-but-unreadable rather than silently treated as empty"*, and its metadata-level rows are what "indexed" means. A rule forbidding them would make an indexed PSD indistinguishable from a file nobody opened.

**`OPEN_QUESTIONS` is data, and the tests read it.** Four of P4's six SPEC open questions are still open. Two are closed: the extractor-tier vocabulary closed as I4 (its four values are `ANALYSIS_TIERS`), and OQ2 closed on 2026-08-20 — **the content hash owns the observation**, so two file records sharing a hash share one observation set. Publishing the open ones as a mapping means Task 18's guards can name the question they protect, and a later agent that answers one in code has to delete an entry — a visible act — rather than let an assumption drift in.

- [ ] **Step 1: Write the failing test**

```python
# tests/p4/test_p4_vocabulary.py
import pytest

from evidence_shape.vocabulary import (
    ANALYSIS_TIERS, COMPLETENESS, EXTRACTOR_RELIABILITY_STATES, INDEXED_SEGMENT_KINDS,
    LABEL_SEGMENT_KINDS, OPEN_QUESTIONS, REGION_UNITS, RELIABILITY_STATES,
    SEGMENT_KINDS, SHAPE_VERSION, SIGNAL_TIERS, SOURCE_TYPES,
    ZERO_OBSERVATION_COMPLETENESS, ZONES, NotInVocabulary, check,
)


def test_the_fifteen_zones_are_the_specs_fifteen_in_order():
    # Every zone is a place the design names as carrying evidence; the SPEC's table
    # carries the § for each. Nothing here is invented and nothing is missing.
    assert ZONES == (
        "filename", "path", "metadata", "title", "heading", "body", "table",
        "header_footer", "notes", "link", "annotation", "reference_list",
        "manifest", "ocr", "transcript",
    )


def test_the_fifteen_segment_kinds_split_into_twelve_indexed_and_three_label():
    # Segment-kind rule 2: an indexed kind is addressed by its index; a
    # label-addressed kind (field | entry | key) has no index.
    assert INDEXED_SEGMENT_KINDS == (
        "page", "slide", "sheet", "heading", "paragraph", "table", "row", "column",
        "cell", "region", "layer", "artboard",
    )
    assert LABEL_SEGMENT_KINDS == ("field", "entry", "key")
    assert SEGMENT_KINDS == INDEXED_SEGMENT_KINDS + LABEL_SEGMENT_KINDS
    assert not set(INDEXED_SEGMENT_KINDS) & set(LABEL_SEGMENT_KINDS)


def test_the_fourteen_source_types_are_2_9s_format_families():
    # D6: taking §2.9's bullet list verbatim avoids inventing a taxonomy.
    assert SOURCE_TYPES == (
        "filesystem", "text_document", "spreadsheet", "presentation", "image", "ocr",
        "email", "calendar", "contacts", "code_structured", "audio_video",
        "design_creative", "archive", "opaque_binary",
    )


def test_reliability_is_3_13s_six_and_extractors_may_write_two_of_them():
    # D11. §3.13 defines six states for file facts; P4 reuses them rather than
    # minting a parallel set (Open question 3), and restricts what an extractor
    # may write to the two that describe a source slot.
    assert RELIABILITY_STATES == (
        "user_confirmed", "direct", "validated", "llm_supported", "possible", "rejected",
    )
    assert EXTRACTOR_RELIABILITY_STATES == ("direct", "possible")
    assert set(EXTRACTOR_RELIABILITY_STATES) < set(RELIABILITY_STATES)


def test_completeness_is_the_nine_values():
    # B1 settled eight; C4 added the ninth on 2026-08-20. None of the eight meant
    # "the bytes are not on this machine": `deferred` is a budget, `unreadable` is
    # damage, `unsupported` is a missing extractor. A dataless file is none of those,
    # so §8.6's progress line could not name the bucket at all.
    assert COMPLETENESS == (
        "complete", "capped", "partial", "metadata_only", "deferred", "unsupported",
        "unreadable", "failed", "dataless",
    )


def test_five_completeness_values_forbid_observations():
    # M3: `unreadable` and `partial` runs DO carry the metadata-level rows §2.9
    # requires -- "recorded as indexed-but-unreadable rather than silently treated
    # as empty". `metadata_only` does NOT: settled 2026-08-20, because rule 9's note
    # and this SPEC's own worked example 19 said opposite things and six extractors
    # would have run the gate. Example 19 is the frozen reading -- the stopping
    # extractor emits nothing and the file stays indexed through its `filesystem`
    # observations. `dataless` joins it (C4): nothing was opened, so nothing was seen.
    assert ZERO_OBSERVATION_COMPLETENESS == (
        "unsupported", "deferred", "failed", "metadata_only", "dataless")
    assert set(ZERO_OBSERVATION_COMPLETENESS) < set(COMPLETENESS)
    for still_allowed in ("unreadable", "partial", "complete", "capped"):
        assert still_allowed not in ZERO_OBSERVATION_COMPLETENESS


def test_the_four_analysis_tiers_are_i4s_four():
    assert ANALYSIS_TIERS == ("filesystem", "native", "ocr", "llm")


def test_analysis_tier_and_source_type_overlap_in_words_and_are_not_one_field():
    # I4: "`source_type` is not the tier." They share two words and mean different
    # things; merging them would lose the distinction between a native PDF run's
    # heading and an OCR run's heading.
    assert set(ANALYSIS_TIERS) & set(SOURCE_TYPES) == {"filesystem", "ocr"}
    assert ANALYSIS_TIERS != SOURCE_TYPES
    assert "native" not in SOURCE_TYPES
    assert "text_document" not in ANALYSIS_TIERS


def test_signal_tier_is_2_6s_three_levels_and_region_units_are_the_specs_two():
    assert SIGNAL_TIERS == (1, 2, 3)
    assert REGION_UNITS == ("px", "norm")


def test_check_rejects_and_never_coerces():
    assert check("heading", ZONES, name="zone") == "heading"
    with pytest.raises(NotInVocabulary):
        check("Heading", ZONES, name="zone")          # no case folding
    with pytest.raises(NotInVocabulary):
        check(" heading", ZONES, name="zone")         # no stripping
    with pytest.raises(NotInVocabulary):
        check("h1", ZONES, name="zone")               # no nearest match
    with pytest.raises(NotInVocabulary):
        check("epub_chapter", ZONES, name="zone")     # D2: an extractor may not add one


def test_every_vocabulary_is_an_immutable_tuple():
    for vocabulary in (ZONES, SEGMENT_KINDS, INDEXED_SEGMENT_KINDS, LABEL_SEGMENT_KINDS,
                       SOURCE_TYPES, RELIABILITY_STATES, EXTRACTOR_RELIABILITY_STATES,
                       COMPLETENESS, ZERO_OBSERVATION_COMPLETENESS, ANALYSIS_TIERS,
                       SIGNAL_TIERS, REGION_UNITS):
        assert isinstance(vocabulary, tuple)


def test_a_shape_version_exists_because_the_contract_says_adding_a_kind_bumps_one():
    # Segment-kind rule 5 and D2 both say a vocabulary addition is "a shape-version
    # bump". A bump needs something to bump.
    assert isinstance(SHAPE_VERSION, int)


def test_the_four_open_questions_are_published_and_the_settled_ones_are_gone():
    # OQ1 (the extractor-tier vocabulary) closed as I4; its four values are
    # ANALYSIS_TIERS. The other five are unsettled by the design and stay open.
    assert set(OPEN_QUESTIONS) == {"OQ3", "OQ4", "OQ5", "OQ6"}
    assert "OQ1" not in OPEN_QUESTIONS   # closed as I4
    assert "OQ2" not in OPEN_QUESTIONS   # closed 2026-08-20: the content hash owns
    for question in OPEN_QUESTIONS.values():
        assert question.strip().endswith("?")


def test_open_questions_cannot_be_edited_at_runtime():
    with pytest.raises(TypeError):
        OPEN_QUESTIONS["OQ6"] = "answered"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p4/test_p4_vocabulary.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'evidence_shape.vocabulary'`

- [ ] **Step 3: Write the implementation**

```python
# src/evidence_shape/vocabulary.py
"""The six closed vocabularies of §2.8's shape, and the questions P4 holds open.

Closed means an extractor may not add a value. D2: "Six extractors then produce
`heading`, `Heading`, `hdg`, `h1` and §3.7's weighting table has no stable key."
Adding a zone or a kind is a P4 contract revision plus a shape-version bump
(segment-kind rule 5), never a local decision inside an extractor.

Every member below is the SPEC's, in the SPEC's order, and each carries a design
citation in the SPEC's own tables. Nothing here is invented.
"""
from __future__ import annotations

from collections.abc import Collection, Mapping
from types import MappingProxyType

#: Bumped when a vocabulary gains a member or the shape gains a field (D2, rule 5).
SHAPE_VERSION = 1

#: §2.2's "document zone". Fifteen places the design names as carrying evidence.
#: P4 publishes the vocabulary; P6 owns what each zone is *worth* (§3.7).
ZONES: tuple[str, ...] = (
    "filename", "path", "metadata", "title", "heading", "body", "table",
    "header_footer", "notes", "link", "annotation", "reference_list",
    "manifest", "ocr", "transcript",
)

#: Addressed by a 1-based index (D3). A label may accompany one and is descriptive
#: only: rule 2 keeps it out of the locator, and rule 3 puts a format's own native
#: address there (a spreadsheet cell is `sheet=2/row=7/column=3`, label "C7").
INDEXED_SEGMENT_KINDS: tuple[str, ...] = (
    "page", "slide", "sheet", "heading", "paragraph", "table", "row", "column",
    "cell", "region", "layer", "artboard",
)

#: Addressed by a label and carrying no index. `field` holds the source format's own
#: slot name verbatim (D7) -- never a product field name, which is P6's `fields`
#: table and which §3.12 forbids creating automatically.
LABEL_SEGMENT_KINDS: tuple[str, ...] = ("field", "entry", "key")

SEGMENT_KINDS: tuple[str, ...] = INDEXED_SEGMENT_KINDS + LABEL_SEGMENT_KINDS

#: §2.9's format families, verbatim (D6). OCR output is `ocr`, never the underlying
#: format -- §2.2 requires "no text layer" and "broken text layer" be
#: distinguishable, and §8.5 requires evaluation decomposed by stage.
SOURCE_TYPES: tuple[str, ...] = (
    "filesystem", "text_document", "spreadsheet", "presentation", "image", "ocr",
    "email", "calendar", "contacts", "code_structured", "audio_video",
    "design_creative", "archive", "opaque_binary",
)

#: §3.13's six, in §3.13's order. The only reliability vocabulary the design defines.
RELIABILITY_STATES: tuple[str, ...] = (
    "user_confirmed", "direct", "validated", "llm_supported", "possible", "rejected",
)

#: D11. An extractor may write two of the six: `direct` for an explicit, labeled,
#: machine-structured slot, `possible` for free text, OCR, a filename or any
#: unlabeled position. The other four are fact-layer outcomes (§3.5) and §2.8
#: forbids extraction from treating model output as proof.
EXTRACTOR_RELIABILITY_STATES: tuple[str, ...] = ("direct", "possible")

#: B1's eight. The single extraction-outcome record's vocabulary; there is no second,
#: per-file status vocabulary anywhere in the system.
COMPLETENESS: tuple[str, ...] = (
    "complete", "capped", "partial", "metadata_only", "deferred", "unsupported",
    "unreadable", "failed", "dataless",
)

#: Conformance rule 9, as M3 relaxed it. `unreadable` and `partial` runs carry the
#: metadata-level rows §2.9's "indexed-but-unreadable" requires. `metadata_only` does
#: not (settled 2026-08-20, matching worked example 19: the stopping extractor emits
#: nothing and the file stays indexed through its `filesystem` observations), and
#: neither does `dataless` (C4) -- nothing was opened, so nothing was seen.
ZERO_OBSERVATION_COMPLETENESS: tuple[str, ...] = (
    "unsupported", "deferred", "failed", "metadata_only", "dataless")

#: I4. P5 writes the first three; P8 is the only writer of `llm`. A fifth is rejected.
ANALYSIS_TIERS: tuple[str, ...] = ("filesystem", "native", "ocr", "llm")

#: §2.6's three-level hierarchy for image signals (M2). Null everywhere else.
SIGNAL_TIERS: tuple[int, ...] = (1, 2, 3)

#: §2.7's "locations or bounding boxes where available".
REGION_UNITS: tuple[str, ...] = ("px", "norm")

#: The questions the design leaves unsettled in P4's area. Each blocks or endangers a
#: named neighbouring part, and each is guarded by a test that fails if it is answered
#: in code instead of in a SPEC. OQ1 closed as I4 and is deliberately absent.
#: OQ1 closed as I4; OQ2 closed 2026-08-20 (the content hash owns the observation).
#: A closed question is DELETED from this mapping, never left with an answer beside
#: it — an entry here means "still unanswered", and that is what Task 18 reads.
OPEN_QUESTIONS: Mapping[str, str] = MappingProxyType({
    "OQ3": (
        "Do observations and facts share one reliability vocabulary? §2.8 puts a "
        "reliability state on the observation and §3.13 defines six states for file "
        "facts; the design never says they are the same vocabulary. Does P6 confirm "
        "the reuse, or define a separate observation-level vocabulary?"
    ),
    "OQ4": (
        "Is the §8.4 handling class stored per observation or only per file? §8.4 "
        "names no granularity; §8.2's file record carries one sensitivity state, yet "
        "only selected excerpts may reach a cloud model. Which unit does P7 classify?"
    ),
    "OQ5": (
        "May a user author or correct an observation directly? §8.7 enumerates user "
        "actions and none is 'correct an extracted value'; §3.13's user_confirmed is "
        "a fact state; §2.8 forbids overwriting raw. Is the only route a "
        "user-confirmed fact at P6?"
    ),
    "OQ6": (
        "What completeness does a source that is not on this machine carry? An "
        "iCloud dataless file cannot be hashed or opened (11-ops-runtime.md §5) and "
        "none of the eight values fits: deferred is budget exhaustion, unreadable is "
        "encrypted-or-damaged, metadata_only is a format decision. Is there a ninth?"
    ),
})


class NotInVocabulary(ValueError):
    """A value outside a closed vocabulary. P4 rejects; it never coerces."""


def check(value, vocabulary: Collection, *, name: str):
    """Membership, or a rejection. No case folding, no stripping, no nearest match."""
    if value not in vocabulary:
        raise NotInVocabulary(
            f"{name}={value!r} is not one of {tuple(vocabulary)}; adding a member is "
            "a P4 contract revision and a shape-version bump, not a local decision "
            "inside an extractor (segment-kind rule 5)"
        )
    return value
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p4/test_p4_vocabulary.py -v`
Expected: PASS — 14 passed

- [ ] **Step 5: Commit**

```bash
git add src/evidence_shape/vocabulary.py tests/p4/test_p4_vocabulary.py
git commit -m "feat(P4): the six closed vocabularies, and the five questions held open"
```

---

### Task 3: `Location` — one structured record for every source type (D1, D2, D3)

**Files:**
- Create: `src/evidence_shape/location.py`
- Test: `tests/p4/test_p4_location.py`

**Interfaces:**
- Consumes: `evidence_shape.vocabulary` — `ZONES`, `SEGMENT_KINDS`, `LABEL_SEGMENT_KINDS`, `REGION_UNITS`, `check`.
- Produces: `MalformedLocation`, `Segment`, `TextSpan`, `TimeSpan`, `Region`, `Location`.

**This is the decision the whole part turns on.** **P5 OQ1 is closed** ([`../../05-minor-resolutions.md`](../../05-minor-resolutions.md)): *"Is `Location` structured? **Yes — P4's structured record plus the canonical locator.** P5 called this 'the single highest-risk item between P4 and P5'; P4 had settled it. §2.8's per-source-type examples (page/heading, table/row/column, EXIF field, OCR region, manifest path) cannot be expressed by a string."* A free-form per-format string forces every consumer to parse per-format text — the exact per-format branching §2.8 exists to prevent — and §3.7's positional weighting cannot compare a parsed string against another format's parsed string.

**Indices are 1-based; text offsets are 0-based half-open** (D3). §2.8's own examples are 1-based (*"page 1, heading 2"*; *"table 3, row 2, column 1"*) and appear in user-visible explanations (§8.2). Offsets are machine-only, and 0-based half-open makes `raw_value == text[start:end]` hold in every mainstream language.

**Offsets count Unicode scalar values** (D4). §2.2 says "text offset" without a unit; §2.7 requires CJK, so the unit must be language-stable. Python strings are already sequences of code points, so `text[start:end]` *is* the D4 unit and no conversion exists anywhere in this package — which is the point of choosing it. Task 8 proves it on CJK and on an astral-plane emoji, where a UTF-16 unit count would differ.

**A label is optional on an indexed kind and required on a label-addressed one.** The SPEC's table says what each label typically carries, and rule 3 then puts a format's own native address there (`sheet=2/row=7/column=3` with `label: "C7"` on the column segment). So the label is not restricted per kind — restricting it would be inventing a rule the contract does not state. What *is* enforced is rule 2: an indexed kind has an index, a label-addressed kind has a label and no index.

**Rule 4, the one that keeps the vocabulary closed under pressure:** *"Unknown structure degrades to a coarser path; it never invents a kind."* An extractor that can locate a value on a page but not within it emits `container_path: [{page, 4}]`. There is no escape hatch, no `other` kind, and no free-text segment, because the first extractor that needs one would take it.

**One span or the other, never both.** The locator grammar is `[ "#" text_span | "@" time_span ]`. A caption has a time span and no document-text offset; a page has the reverse. A record carrying both would serialize to a string that cannot round-trip, so it is rejected at construction rather than at serialization.

**`Segment(kind="region")` and `Location.region` are different things** — see *Two things called `region`* in the Global Constraints. The test below pins the distinction structurally.

- [ ] **Step 1: Write the failing test**

```python
# tests/p4/test_p4_location.py
import pytest

from evidence_shape.location import (
    Location, MalformedLocation, Region, Segment, TextSpan, TimeSpan,
)
from evidence_shape.vocabulary import NotInVocabulary


def test_2_8s_own_pdf_example_is_expressible():
    # §2.8: "A PDF match may be located at page 1, heading 2".
    location = Location(
        zone="heading",
        container_path=(Segment("page", 1),
                        Segment("heading", 2, label="Course Information")),
        text_span=TextSpan(0, 10),
    )
    assert location.zone == "heading"
    assert location.container_path[0].index == 1
    assert location.container_path[1].label == "Course Information"


def test_2_8s_own_docx_exif_and_manifest_examples_are_expressible():
    # "table 3, row 2, column 1"; "EXIF DateTimeOriginal"; "a manifest path".
    assert Location("table", (Segment("table", 3), Segment("row", 2),
                              Segment("column", 1))).container_path[2].index == 1
    assert Location("metadata", (Segment("field", label="DateTimeOriginal"),))
    assert Location("manifest", (Segment("entry", label="docs/transcript.pdf"),))


def test_a_caption_carries_a_time_span_and_no_page():
    # §2.9 audio/video: captions and transcripts have no page and no document offset.
    location = Location("transcript", time_span=TimeSpan(252_500, 255_200))
    assert location.container_path == ()
    assert location.text_span is None


def test_container_path_accepts_any_sequence_and_stores_a_tuple():
    assert Location("body", [Segment("page", 4)]) == Location("body", (Segment("page", 4),))
    assert isinstance(Location("body", [Segment("page", 4)]).container_path, tuple)


def test_a_location_is_frozen_and_hashable():
    # RAW-2 in miniature: nothing about a recorded observation is edited in place.
    location = Location("body", (Segment("page", 18),), text_span=TextSpan(12043, 12051))
    with pytest.raises(Exception):
        location.zone = "title"
    assert {location, Location("body", (Segment("page", 18),),
                               text_span=TextSpan(12043, 12051))} == {location}


def test_the_zone_and_the_kind_come_from_the_closed_vocabularies():
    with pytest.raises(NotInVocabulary):
        Location("h1")
    with pytest.raises(NotInVocabulary):
        Location("body", (Segment("chapter", 2),))


def test_indices_are_1_based():
    # D3: §2.8's examples are 1-based and appear in user-visible explanations (§8.2).
    assert Segment("page", 1).index == 1
    with pytest.raises(MalformedLocation):
        Segment("page", 0)
    with pytest.raises(MalformedLocation):
        Segment("page", -1)


def test_an_indexed_kind_needs_an_index_and_a_label_kind_needs_a_label():
    # Segment-kind rule 2.
    with pytest.raises(MalformedLocation):
        Segment("page")                                  # indexed, no index
    with pytest.raises(MalformedLocation):
        Segment("field")                                 # label kind, no label
    with pytest.raises(MalformedLocation):
        Segment("field", 3, label="DateTimeOriginal")    # label kind with an index
    with pytest.raises(MalformedLocation):
        Segment("entry", 1)


def test_a_label_is_allowed_on_an_indexed_kind_because_rule_3_puts_one_there():
    # Rule 3: "a spreadsheet cell is `sheet=2/row=7/column=3` with `label: "C7"` on
    # the column segment, not a separate `cell` kind."
    assert Segment("column", 3, label="C7").label == "C7"
    assert Segment("slide", 6, label="Timeline").label == "Timeline"
    assert Segment("page", 4).label is None


def test_a_boolean_is_not_an_index():
    with pytest.raises(MalformedLocation):
        Segment("page", True)


def test_text_spans_are_0_based_and_half_open():
    assert TextSpan(0, 10).start == 0
    assert TextSpan(7, 7).end == 7                       # empty span is well-formed
    with pytest.raises(MalformedLocation):
        TextSpan(-1, 4)
    with pytest.raises(MalformedLocation):
        TextSpan(10, 4)                                  # end before start


def test_time_spans_are_integer_milliseconds_from_media_start():
    assert TimeSpan(252_500, 255_200).end_ms == 255_200
    with pytest.raises(MalformedLocation):
        TimeSpan(-1, 10)
    with pytest.raises(MalformedLocation):
        TimeSpan(255_200, 252_500)
    with pytest.raises(MalformedLocation):
        TimeSpan(1.5, 2.5)                               # milliseconds, not seconds


def test_a_location_carries_one_span_or_the_other_never_both():
    # The locator grammar is `[ "#" text_span | "@" time_span ]`; a record carrying
    # both would serialize to a string that cannot round-trip.
    with pytest.raises(MalformedLocation):
        Location("transcript", text_span=TextSpan(0, 4), time_span=TimeSpan(0, 10))


def test_a_bounding_box_carries_one_of_2_7s_two_units():
    assert Region(0, 0, 100, 40, "px").unit == "px"
    assert Region(0.1, 0.2, 0.3, 0.4, "norm").w == 0.3
    with pytest.raises(NotInVocabulary):
        Region(0, 0, 1, 1, "percent")


def test_the_region_segment_kind_and_the_region_bounding_box_are_not_one_thing():
    # §2.8's "an OCR region" is an addressing step; §2.7's "bounding boxes where
    # available" is a rectangle. Both are published as `region` and they are
    # structurally distinct: one is a Segment, one is a Region.
    location = Location("ocr", (Segment("page", 4), Segment("region", 2)),
                        text_span=TextSpan(0, 24),
                        region=Region(12, 40, 300, 22, "px"))
    assert isinstance(location.container_path[1], Segment)
    assert isinstance(location.region, Region)
    assert location.container_path[1].index == 2
    assert location.region.w == 300


def test_unknown_structure_degrades_to_a_coarser_path_and_invents_no_kind():
    # Segment-kind rule 4. An extractor that can locate a value on a page but not
    # within it emits `[{page, 4}]` -- there is no `other` kind and no free-text
    # segment, because the first extractor that needed one would take it.
    coarse = Location("body", (Segment("page", 4),))
    assert coarse.container_path == (Segment("page", 4),)
    with pytest.raises(NotInVocabulary):
        Segment("other", 1)
    with pytest.raises(NotInVocabulary):
        Segment("unknown", label="somewhere on page 4")


def test_every_prefix_of_a_valid_path_is_itself_a_valid_coarser_address():
    # Segment-kind rule 1.
    full = (Segment("page", 4), Segment("table", 3), Segment("row", 2),
            Segment("column", 1))
    for length in range(len(full) + 1):
        assert Location("table", full[:length]).container_path == full[:length]


def test_a_container_path_holds_segments_and_not_raw_tuples():
    with pytest.raises(MalformedLocation):
        Location("body", (("page", 4),))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p4/test_p4_location.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'evidence_shape.location'`

- [ ] **Step 3: Write the implementation**

```python
# src/evidence_shape/location.py
"""D1 -- one structured location record for every source type.

P5 OQ1, closed in 05-minor-resolutions.md: "Is `Location` structured? Yes -- P4's
structured record plus the canonical locator. §2.8's per-source-type examples
(page/heading, table/row/column, EXIF field, OCR region, manifest path) cannot be
expressed by a string."

`zone` answers what kind of place (which §3.7 weights); `container_path` answers
which one (which §8.2 explanations cite). Container indices are 1-based (D3, matching
§2.8's own "page 1, heading 2"); text offsets are 0-based half-open in Unicode scalar
values (D3, D4), which is what makes `raw_value == text[start:end]` hold.

Two published names spell `region` and they are different things: `Segment(kind=
"region")` is §2.8's "an OCR region", an addressing step that appears in the locator;
`Location.region` is §2.7's "locations or bounding boxes where available", which the
locator grammar has no term for. Neither name is P4's to change.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from evidence_shape.vocabulary import (
    LABEL_SEGMENT_KINDS, REGION_UNITS, SEGMENT_KINDS, ZONES, check,
)


class MalformedLocation(ValueError):
    """A structurally invalid location. P4 rejects it; it never repairs one."""


@dataclass(frozen=True, slots=True)
class Segment:
    """One addressing step, outermost to innermost (segment-kind rule 1)."""

    kind: str
    index: int | None = None
    label: str | None = None

    def __post_init__(self) -> None:
        check(self.kind, SEGMENT_KINDS, name="kind")
        if self.kind in LABEL_SEGMENT_KINDS:
            if self.index is not None:
                raise MalformedLocation(
                    f"{self.kind!r} is addressed by its label and carries no index "
                    "(segment-kind rule 2)"
                )
            if not self.label:
                raise MalformedLocation(
                    f"{self.kind!r} is addressed by its label, which is required "
                    "(segment-kind rule 2)"
                )
            return
        if type(self.index) is not int or self.index < 1:
            raise MalformedLocation(
                f"{self.kind!r} is addressed by a 1-based index, not {self.index!r} "
                "(D3: §2.8's own examples are 1-based and reach §8.2 explanations)"
            )


@dataclass(frozen=True, slots=True)
class TextSpan:
    """0-based, half-open, in Unicode scalar values (D3, D4)."""

    start: int
    end: int

    def __post_init__(self) -> None:
        for name, value in (("start", self.start), ("end", self.end)):
            if type(value) is not int or value < 0:
                raise MalformedLocation(
                    f"text_span.{name} is a 0-based code-point offset, not {value!r}"
                )
        if self.end < self.start:
            raise MalformedLocation("text_span is half-open: start <= end (D3)")


@dataclass(frozen=True, slots=True)
class TimeSpan:
    """Integer milliseconds from media start. §2.9 audio/video."""

    start_ms: int
    end_ms: int

    def __post_init__(self) -> None:
        for name, value in (("start_ms", self.start_ms), ("end_ms", self.end_ms)):
            if type(value) is not int or value < 0:
                raise MalformedLocation(
                    f"time_span.{name} is integer milliseconds, not {value!r}"
                )
        if self.end_ms < self.start_ms:
            raise MalformedLocation("time_span: start_ms <= end_ms")


@dataclass(frozen=True, slots=True)
class Region:
    """§2.7's "locations or bounding boxes where available". Null when unreported."""

    x: float
    y: float
    w: float
    h: float
    unit: str

    def __post_init__(self) -> None:
        for name in ("x", "y", "w", "h"):
            value = getattr(self, name)
            if type(value) not in (int, float):
                raise MalformedLocation(f"region.{name} is a number, not {value!r}")
        check(self.unit, REGION_UNITS, name="region.unit")


@dataclass(frozen=True, slots=True)
class Location:
    """§2.8's "Location", as one shape for every source type."""

    zone: str
    container_path: tuple[Segment, ...] = ()
    text_span: TextSpan | None = None
    time_span: TimeSpan | None = None
    region: Region | None = None

    def __post_init__(self) -> None:
        check(self.zone, ZONES, name="zone")
        if not isinstance(self.container_path, tuple):
            if isinstance(self.container_path, (str, bytes)) or not isinstance(
                    self.container_path, Iterable):
                raise MalformedLocation("container_path is an ordered sequence of Segments")
            object.__setattr__(self, "container_path", tuple(self.container_path))
        for segment in self.container_path:
            if not isinstance(segment, Segment):
                raise MalformedLocation(
                    f"container_path holds Segments, not {segment!r}"
                )
        for name, expected in (("text_span", TextSpan), ("time_span", TimeSpan),
                               ("region", Region)):
            value = getattr(self, name)
            if value is not None and not isinstance(value, expected):
                raise MalformedLocation(f"{name} is a {expected.__name__} or None")
        if self.text_span is not None and self.time_span is not None:
            raise MalformedLocation(
                "a location carries one span or the other, never both: the locator "
                'grammar is `[ "#" text_span | "@" time_span ]`'
            )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p4/test_p4_location.py -v`
Expected: PASS — 18 passed

- [ ] **Step 5: Commit**

```bash
git add src/evidence_shape/location.py tests/p4/test_p4_location.py
git commit -m "feat(P4): D1 — one structured location record for every source type"
```

---

### Task 4: The canonical locator — serialize, parse, escape (Done-means 3)

**Files:**
- Create: `src/evidence_shape/locator.py`
- Test: `tests/p4/test_p4_locator.py`

**Interfaces:**
- Consumes: `evidence_shape.location` — `Location`, `Segment`, `TextSpan`, `TimeSpan`, `Region`, `MalformedLocation`; `evidence_shape.vocabulary` — `LABEL_SEGMENT_KINDS`, `SEGMENT_KINDS`, `ZONES`, `check`.
- Produces: `MalformedLocator`, `escape_label`, `unescape_label`, `addressing`, `serialize_container_path`, `parse_container_path`, `serialize_locator`, `parse_locator`, `location_to_mapping`, `location_from_mapping`.

**Why a string at all, when the record is structured.** The locator is *"redundant with the structured fields by construction; it exists because §8.2 provenance events, §4.4 dossiers and §3.6/§4.8/§6.10/§7.9 citation checks all need one short stable handle."* It is also one of the four inputs to `observation_key` (Task 5), so a serialization that was not canonical would make the citation handle unstable — which is the one thing §8.7 requires it not be.

**The grammar, from the SPEC, verbatim:**

```text
locator   := zone [ ":" segments ] [ "#" text_span | "@" time_span ]
segments  := segment ( "/" segment )*
segment   := kind "=" addr
addr      := <1-based decimal integer>     ; indexed kinds
           | <escaped label>               ; field | entry | key
text_span := start "-" end                 ; 0-based code points, half-open
time_span := start_ms "-" end_ms           ; integer milliseconds
```

**Escaping, in labels only:** percent-encode `%` `/` `=` `#` `@` `:` and any control character as `%XX`, uppercase hex, over UTF-8 bytes. *"Archive member paths contain `/` and this is not optional."* "Control character" is read as Unicode general category `Cc`, which is the definition rather than a hand-picked range. **Non-ASCII is not escaped** — it round-trips as itself, and Done-means 3 requires a passing escaping test on a path containing `/`, `=`, `#` **and a non-ASCII segment**, which only means something if the non-ASCII survives.

**The bounding box never reaches the locator.** The grammar has no term for `region: {x, y, w, h, unit}`, and `serialize_locator` emits none — so two OCR observations that differ only in their bounding box produce the same locator and therefore the same `observation_key`. That is correct and deliberate: D10 collapses on `(run, exact raw value, zone)`, and a second bounding box for the same raw value in the same region path is the same observation, not a second one.

**Parsing rejects; it never repairs.** An unknown zone, an unknown kind, a segment with no `=`, a non-numeric index, a zero index, an odd `%`-escape, or both span markers at once all raise. §2.8's whole premise fails the moment a consumer's parser guesses.

- [ ] **Step 1: Write the failing test**

```python
# tests/p4/test_p4_locator.py
import pytest

from evidence_shape.location import (
    Location, MalformedLocation, Region, Segment, TextSpan, TimeSpan,
)
from evidence_shape.locator import (
    MalformedLocator, addressing, escape_label, location_from_mapping,
    location_to_mapping, parse_container_path, parse_locator,
    serialize_container_path, serialize_locator, unescape_label,
)
from evidence_shape.vocabulary import NotInVocabulary

#: The SPEC's own worked locators, plus the four zones its nineteen fixtures do not
#: reach. Every one of these round-trips; none of them is invented syntax.
GOLDEN_LOCATORS = (
    "filename",                                 # the filename itself
    "filename#0-6",                             # first six code points of the filename
    "path",                                     # §2.9 parent-folder context
    "title:page=1",                             # the document title
    "heading:page=1/heading=2",                 # §2.8's "page 1, heading 2"
    "heading:page=1/heading=1",                 # §2.3's Wash U.docx heading
    "table:page=4/table=3/row=2/column=1",      # §2.8's "table 3, row 2, column 1"
    "table:sheet=2/row=7/column=3",             # a spreadsheet cell
    "metadata:field=DateTimeOriginal",          # §2.8's EXIF example
    "metadata:field=dc%3Atitle",                # colon escaped
    "metadata:field=Producer",                  # §2.2's tool-generated producer
    "metadata:field=Subject",                   # §2.9 email
    "metadata:field=DTSTART",                   # §2.9 calendar
    "metadata:key=dependencies/field=name",     # §2.9 package manifests
    "metadata:layer=3",                         # §2.9 design/creative
    "manifest:entry=docs%2Ftranscript.pdf",     # §2.8's "a manifest path"
    "manifest:field=file_count",                # §2.5's "file count"
    "ocr:page=4/region=2#0-24",                 # §2.8's "an OCR region"
    "body:page=18#12043-12051",                 # §2.2's page-eighteen reference
    "notes:slide=6#0-42",                       # §2.9 presentations
    "transcript@252500-255200",                 # a caption at 04:12.5-04:15.2
    "link:page=1#40-72",                        # §2.2, §2.3 URLs and email addresses
    "annotation:page=2#0-18",                   # §2.3 comments and revision metadata
    "header_footer:page=1#0-24",                # §2.3, §3.7 "a footer"
    "reference_list:page=18#12000-12100",       # §2.2's reference list
)


@pytest.mark.parametrize("locator", GOLDEN_LOCATORS)
def test_every_golden_locator_round_trips(locator):
    # Conformance rule 4: "`locator` round-trips: serialize -> parse -> structurally
    # equal." Asserted here in the other direction too, which is the one that
    # catches a serializer that silently reorders or drops a segment.
    assert serialize_locator(parse_locator(locator)) == locator


@pytest.mark.parametrize("locator", GOLDEN_LOCATORS)
def test_every_golden_locator_survives_the_mapping_form(locator):
    location = parse_locator(locator)
    assert location_from_mapping(location_to_mapping(location)) == location
    assert location_to_mapping(location)["locator"] == locator


def test_2_8s_pdf_example_serializes_to_2_8s_own_words():
    location = Location("heading",
                        (Segment("page", 1), Segment("heading", 2, label="Course Information")))
    assert serialize_locator(location) == "heading:page=1/heading=2"


def test_addressing_is_what_a_round_trip_reproduces():
    # Conformance rule 4 is written against this projection, because rule 2 keeps a
    # descriptive label out of the string and the grammar has no term for a bounding
    # box. Round-tripping the full record would fail on both, correctly.
    full = Location("heading",
                    (Segment("page", 1), Segment("heading", 2, label="Course Information")),
                    text_span=TextSpan(0, 10), region=Region(1, 2, 3, 4, "px"))
    projected = addressing(full)
    assert projected == Location("heading", (Segment("page", 1), Segment("heading", 2)),
                                 text_span=TextSpan(0, 10))
    assert parse_locator(serialize_locator(full)) == projected
    assert addressing(projected) == projected


def test_addressing_keeps_the_label_on_a_label_addressed_kind():
    # `field`, `entry` and `key` ARE addressed by their label, so it is not
    # descriptive and it does appear in the locator.
    labelled = Location("metadata", (Segment("field", label="DateTimeOriginal"),))
    assert addressing(labelled) == labelled
    assert parse_locator(serialize_locator(labelled)) == labelled


def test_a_descriptive_label_never_appears_in_the_locator():
    # Segment-kind rule 2: "A kind with an index is addressed by its index; its label
    # is descriptive only and never appears in the locator."
    with_label = Location("table", (Segment("sheet", 2), Segment("row", 7),
                                    Segment("column", 3, label="C7")))
    without = Location("table", (Segment("sheet", 2), Segment("row", 7),
                                 Segment("column", 3)))
    assert serialize_locator(with_label) == serialize_locator(without)
    assert "C7" not in serialize_locator(with_label)


def test_the_bounding_box_never_appears_in_the_locator():
    # The grammar has no term for `region: {x, y, w, h, unit}`. Two OCR readings of
    # one raw value in one region path are one observation (D10), not two.
    boxed = Location("ocr", (Segment("page", 4), Segment("region", 2)),
                     text_span=TextSpan(0, 24), region=Region(12, 40, 300, 22, "px"))
    unboxed = Location("ocr", (Segment("page", 4), Segment("region", 2)),
                       text_span=TextSpan(0, 24))
    assert serialize_locator(boxed) == serialize_locator(unboxed) == "ocr:page=4/region=2#0-24"
    assert location_from_mapping(location_to_mapping(boxed)) == boxed


def test_an_archive_member_path_escapes_its_slashes_and_keeps_its_non_ascii():
    # Done-means 3: "a passing escaping test on an archive path containing `/`, `=`,
    # `#` and a non-ASCII segment". The escaping exists because §2.8's own example is
    # a manifest path, and paths contain `/`.
    member = "docs/2026=final#draft/提出書類.pdf"
    location = Location("manifest", (Segment("entry", label=member),))
    serialized = serialize_locator(location)

    assert serialized.split(":", 1)[1].count("/") == 0     # no segment boundary forged
    assert "#" not in serialized                           # no span marker forged
    assert "=" in serialized.split(":", 1)[1][:6]          # only the one addr marker
    assert "提" in serialized                          # non-ASCII stays literal
    assert parse_locator(serialized) == location
    assert parse_locator(serialized).container_path[0].label == member


def test_escaping_covers_every_reserved_character_and_control_characters():
    for reserved in ("%", "/", "=", "#", "@", ":"):
        assert unescape_label(escape_label(reserved)) == reserved
    for reserved in ("/", "=", "#", "@", ":"):
        # `%` is excluded from this half on purpose: its own escape is `%25`, which
        # necessarily contains it. That is the escape marker, not an unescaped char.
        assert reserved not in escape_label(reserved)
    tab = chr(9)
    assert tab not in escape_label(f"a{tab}b")
    assert unescape_label(escape_label(f"a{tab}b")) == f"a{tab}b"


def test_escapes_are_uppercase_hex_over_utf_8_bytes():
    assert escape_label(":") == "%3A"
    assert escape_label("/") == "%2F"
    assert escape_label("%") == "%25"
    assert escape_label("é") == "é"              # not reserved; not escaped


def test_an_emoji_label_round_trips_unescaped():
    location = Location("metadata", (Segment("field", label="Title \U0001F600"),))
    assert parse_locator(serialize_locator(location)) == location


def test_a_container_path_serializes_without_a_zone_prefix():
    # This is the form `text_units.unit_locator` carries (Task 7): the unit's address
    # is a container path, not a located value, so it has no zone.
    path = (Segment("page", 4), Segment("region", 2))
    assert serialize_container_path(path) == "page=4/region=2"
    assert parse_container_path("page=4/region=2") == path
    assert serialize_container_path(()) == ""
    assert parse_container_path("") == ()


def test_parsing_rejects_and_never_repairs():
    for malformed in ("", "heading:", "heading:page", "heading:page=x",
                      "heading:page=1#a-b", "heading:page=1#5",
                      "heading:page=1#0-10@0-10", "metadata:field=%zz",
                      "metadata:field=%2"):
        with pytest.raises((MalformedLocator, MalformedLocation)):
            parse_locator(malformed)


def test_parsing_rejects_a_zone_or_kind_outside_the_closed_vocabulary():
    with pytest.raises(NotInVocabulary):
        parse_locator("h1:page=1")
    with pytest.raises(NotInVocabulary):
        parse_locator("body:chapter=1")


def test_parsing_rejects_a_zero_index_because_indices_are_1_based():
    with pytest.raises(MalformedLocation):
        parse_locator("heading:page=0")


def test_a_locator_carries_one_span_or_the_other_never_both():
    with pytest.raises(MalformedLocator):
        parse_locator("transcript:page=1#0-4@0-10")


def test_the_mapping_form_rejects_a_locator_that_does_not_match_its_fields():
    # The string is redundant with the structured fields by construction. A stored
    # record whose two halves disagree is unusable for a citation check (§3.6, §4.8).
    with pytest.raises(MalformedLocation):
        location_from_mapping({"zone": "body", "container_path": [], "locator": "title"})


def test_the_mapping_form_rejects_an_unknown_field():
    with pytest.raises(MalformedLocation):
        location_from_mapping({"zone": "body", "page_number": 4})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p4/test_p4_locator.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'evidence_shape.locator'`

- [ ] **Step 3: Write the implementation**

```python
# src/evidence_shape/locator.py
"""The canonical serialization of a Location, and its parser.

    locator   := zone [ ":" segments ] [ "#" text_span | "@" time_span ]
    segments  := segment ( "/" segment )*
    segment   := kind "=" addr
    addr      := <1-based decimal integer>     ; indexed kinds
               | <escaped label>               ; field | entry | key
    text_span := start "-" end                 ; 0-based code points, half-open
    time_span := start_ms "-" end_ms           ; integer milliseconds

Redundant with the structured fields by construction. It exists because §8.2
provenance events, §4.4 dossiers and §3.6/§4.8/§6.10/§7.9 citation checks all need
one short stable handle -- and because it is one of the four inputs to
`observation_key`, which §8.7 requires to stay resolvable across extractor upgrades.

Escaping, in labels only: percent-encode `%` `/` `=` `#` `@` `:` and any control
character (Unicode category Cc) as %XX, uppercase hex, over UTF-8 bytes. Archive
member paths contain `/` and this is not optional. Non-ASCII is not escaped.

The bounding box (`Location.region`) has no term in the grammar and never appears
here; `Segment(kind="region")` does, and they are different things.
"""
from __future__ import annotations

import unicodedata
from collections.abc import Mapping, Sequence

from evidence_shape.location import (
    Location, MalformedLocation, Region, Segment, TextSpan, TimeSpan,
)
from evidence_shape.vocabulary import LABEL_SEGMENT_KINDS, SEGMENT_KINDS, ZONES, check

_RESERVED = ("%", "/", "=", "#", "@", ":")
_ZONE_MARK = ":"
_SEGMENT_MARK = "/"
_ADDR_MARK = "="
_SPAN_MARK = "#"
_TIME_MARK = "@"
_RANGE_MARK = "-"
_HEX = "0123456789ABCDEF"

_LOCATION_KEYS = frozenset(
    {"zone", "container_path", "text_span", "time_span", "region", "locator"})


class MalformedLocator(ValueError):
    """A locator that does not parse. P4 rejects it; no consumer guesses."""


def escape_label(label: str) -> str:
    """Percent-encode the reserved set and control characters, and nothing else."""
    out: list[str] = []
    for character in label:
        if character in _RESERVED or unicodedata.category(character) == "Cc":
            out.extend(f"%{byte:02X}" for byte in character.encode("utf-8"))
        else:
            out.append(character)
    return "".join(out)


def unescape_label(text: str) -> str:
    """The inverse. A malformed escape is a rejection, never a passed-through `%`."""
    raw = bytearray()
    index = 0
    while index < len(text):
        character = text[index]
        if character == "%":
            token = text[index + 1:index + 3]
            if len(token) != 2 or any(digit not in _HEX for digit in token):
                raise MalformedLocator(
                    f"%-escape must be two uppercase hex digits, got {text[index:index + 3]!r}"
                )
            raw.append(int(token, 16))
            index += 3
            continue
        if character in _RESERVED:
            raise MalformedLocator(f"unescaped {character!r} inside a label")
        raw.extend(character.encode("utf-8"))
        index += 1
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise MalformedLocator(f"%-escapes do not decode as UTF-8: {text!r}") from exc


def serialize_container_path(segments: Sequence[Segment]) -> str:
    """The address alone, with no zone. This is `text_units.unit_locator` (D12)."""
    return _SEGMENT_MARK.join(
        f"{segment.kind}{_ADDR_MARK}{segment.index}" if segment.index is not None
        else f"{segment.kind}{_ADDR_MARK}{escape_label(segment.label)}"
        for segment in segments
    )


def parse_container_path(text: str) -> tuple[Segment, ...]:
    if not text:
        return ()
    segments: list[Segment] = []
    for chunk in text.split(_SEGMENT_MARK):
        kind, mark, addr = chunk.partition(_ADDR_MARK)
        if not mark:
            raise MalformedLocator(f"segment {chunk!r} has no {_ADDR_MARK!r}")
        check(kind, SEGMENT_KINDS, name="kind")
        if kind in LABEL_SEGMENT_KINDS:
            segments.append(Segment(kind, label=unescape_label(addr)))
            continue
        if not addr.isdigit():
            raise MalformedLocator(
                f"{kind!r} is addressed by a 1-based decimal integer, got {addr!r}"
            )
        segments.append(Segment(kind, int(addr)))
    return tuple(segments)


def addressing(location: Location) -> Location:
    """The part of a location the locator carries.

    Segment-kind rule 2: "A kind with an index is addressed by its index; its label
    is descriptive only and never appears in the locator." So a round-trip through
    the string reproduces this projection, not the original record -- and conformance
    rule 4 is written against it. The bounding box is dropped for the same reason:
    the grammar has no term for it.
    """
    return Location(
        location.zone,
        tuple(Segment(segment.kind, segment.index) if segment.index is not None
              else segment for segment in location.container_path),
        text_span=location.text_span,
        time_span=location.time_span,
    )


def serialize_locator(location: Location) -> str:
    """Canonical and deterministic: the same location always produces this string."""
    out = location.zone
    if location.container_path:
        out += _ZONE_MARK + serialize_container_path(location.container_path)
    if location.text_span is not None:
        out += (f"{_SPAN_MARK}{location.text_span.start}"
                f"{_RANGE_MARK}{location.text_span.end}")
    elif location.time_span is not None:
        out += (f"{_TIME_MARK}{location.time_span.start_ms}"
                f"{_RANGE_MARK}{location.time_span.end_ms}")
    return out


def _split_span(text: str) -> tuple[str, TextSpan | None, TimeSpan | None]:
    marks = [(text.index(mark), mark) for mark in (_SPAN_MARK, _TIME_MARK) if mark in text]
    if not marks:
        return text, None, None
    if len(marks) == 2:
        raise MalformedLocator(
            "a locator carries one span or the other, never both: the grammar is "
            '`[ "#" text_span | "@" time_span ]`'
        )
    at, mark = marks[0]
    head, tail = text[:at], text[at + 1:]
    start, separator, end = tail.partition(_RANGE_MARK)
    if not separator or not start.isdigit() or not end.isdigit():
        raise MalformedLocator(
            f"span {tail!r} is start{_RANGE_MARK}end in non-negative decimals"
        )
    if mark == _SPAN_MARK:
        return head, TextSpan(int(start), int(end)), None
    return head, None, TimeSpan(int(start), int(end))


def parse_locator(text: str, *, region: Region | None = None) -> Location:
    """Parse, or reject. The bounding box is not in the string, so it is a keyword."""
    if not isinstance(text, str) or not text:
        raise MalformedLocator("a locator is a non-empty string")
    head, text_span, time_span = _split_span(text)
    zone, mark, segments = head.partition(_ZONE_MARK)
    check(zone, ZONES, name="zone")
    if mark and not segments:
        raise MalformedLocator(f"{text!r} carries a {_ZONE_MARK!r} and no segments")
    return Location(zone, parse_container_path(segments), text_span=text_span,
                    time_span=time_span, region=region)


def location_to_mapping(location: Location) -> dict[str, object]:
    """The SPEC's JSON shape, including the redundant-by-construction `locator`."""
    return {
        "zone": location.zone,
        "container_path": [
            {"kind": segment.kind,
             **({"index": segment.index} if segment.index is not None else {}),
             **({"label": segment.label} if segment.label is not None else {})}
            for segment in location.container_path
        ],
        "text_span": None if location.text_span is None
        else {"start": location.text_span.start, "end": location.text_span.end},
        "time_span": None if location.time_span is None
        else {"start_ms": location.time_span.start_ms,
              "end_ms": location.time_span.end_ms},
        "region": None if location.region is None
        else {"x": location.region.x, "y": location.region.y, "w": location.region.w,
              "h": location.region.h, "unit": location.region.unit},
        "locator": serialize_locator(location),
    }


def location_from_mapping(mapping: Mapping[str, object]) -> Location:
    """The inverse, with the two halves checked against each other."""
    unknown = sorted(set(mapping) - _LOCATION_KEYS)
    if unknown:
        raise MalformedLocation(f"unknown location fields: {unknown}")
    text_span = mapping.get("text_span")
    time_span = mapping.get("time_span")
    region = mapping.get("region")
    location = Location(
        mapping["zone"],
        tuple(Segment(segment["kind"], segment.get("index"), segment.get("label"))
              for segment in mapping.get("container_path", ())),
        text_span=None if text_span is None
        else TextSpan(text_span["start"], text_span["end"]),
        time_span=None if time_span is None
        else TimeSpan(time_span["start_ms"], time_span["end_ms"]),
        region=None if region is None
        else Region(region["x"], region["y"], region["w"], region["h"], region["unit"]),
    )
    stated = mapping.get("locator")
    if stated is not None and stated != serialize_locator(location):
        raise MalformedLocation(
            f"locator {stated!r} does not serialize from the structured fields; the "
            "two halves of a location must agree or no citation check can use it"
        )
    return location
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p4/test_p4_locator.py -v`
Expected: PASS — 66 passed (25 + 25 parametrized, plus 16 others)

- [ ] **Step 5: Commit**

```bash
git add src/evidence_shape/locator.py tests/p4/test_p4_locator.py
git commit -m "feat(P4): the canonical locator — one short stable handle, round-tripped"
```

---

### Task 5: Canonical bytes — deterministic JSON and an injective digest

**Files:**
- Create: `src/evidence_shape/canonical.py`
- Test: `tests/p4/test_p4_canonical.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `canonical_json(value) -> str`, `sha256_of(*parts: str) -> str`.

**Why this is its own module.** Three published values are digests or byte-comparisons of the same kind: `observation_key` (Task 6), `config_fingerprint` (Task 7) and the determinism digest (Task 15). Conformance rule 8 requires *"byte-identical observation set"*, §3.4 requires a cache key, and §8.5 requires a diff — all three fail if two equal records can serialize two ways. One module, two functions, three consumers; a second implementation of "canonical" is exactly how a replay diff starts reporting phantom changes.

**Why the digest is length-prefixed.** The SPEC writes `observation_key = sha256(content_hash ‖ extractor_name ‖ locator ‖ raw_value)`. Plain concatenation is not injective — `("ab", "c")` and `("a", "bc")` produce the same bytes — so two different observations could collide on the one handle §8.7 requires to stay permanently resolvable. Prefixing each part with its UTF-8 byte length makes the concatenation injective while keeping the SPEC's four inputs and their order exactly.

**Why `ensure_ascii=False`.** §2.7 requires CJK support and D4 counts code points. Escaping non-ASCII to `\uXXXX` would make the byte length of a canonical record depend on the script it is written in, for no gain; UTF-8 is the encoding everywhere else in this package.

- [ ] **Step 1: Write the failing test**

```python
# tests/p4/test_p4_canonical.py
from evidence_shape.canonical import canonical_json, sha256_of


def test_canonical_json_is_key_ordered_and_unpadded():
    assert canonical_json({"b": 1, "a": [2, 3]}) == '{"a":[2,3],"b":1}'
    assert canonical_json({"a": 1, "b": 2}) == canonical_json({"b": 2, "a": 1})


def test_canonical_json_keeps_non_ascii_as_itself():
    # §2.7 requires CJK; D4 counts code points. Escaping would make the byte length
    # of a record depend on the script it is written in, for no gain.
    assert canonical_json({"t": "提出書類"}) == '{"t":"提出書類"}'


def test_canonical_json_is_stable_across_equal_but_differently_built_values():
    first = {"languages": ["en", "zh-Hans"], "dpi": 200}
    second = {}
    second["dpi"] = 200
    second["languages"] = ["en", "zh-Hans"]
    assert canonical_json(first) == canonical_json(second)


def test_the_digest_carries_its_algorithm_the_way_content_hash_does():
    assert sha256_of("a").startswith("sha256:")


def test_the_digest_is_injective_over_its_parts():
    # Plain concatenation is not: ("ab", "c") and ("a", "bc") would collide, and the
    # collision would be on the one handle §8.7 requires to stay resolvable.
    assert sha256_of("ab", "c") != sha256_of("a", "bc")
    assert sha256_of("", "abc") != sha256_of("abc", "")
    assert sha256_of("a", "b", "c") != sha256_of("a", "bc")


def test_the_digest_is_deterministic():
    assert sha256_of("sha256:abc", "pdf.text", "heading:page=1/heading=2", "BUSIB 4300") == \
           sha256_of("sha256:abc", "pdf.text", "heading:page=1/heading=2", "BUSIB 4300")


def test_the_digest_is_computed_over_utf_8_bytes():
    assert sha256_of("提出") != sha256_of("提")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p4/test_p4_canonical.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'evidence_shape.canonical'`

- [ ] **Step 3: Write the implementation**

```python
# src/evidence_shape/canonical.py
"""Byte-identical serialization, and the digest every published key is built from.

Conformance rule 8 requires "byte-identical observation set" for the same content
hash, extractor version and config fingerprint; §3.4 keys a cache on it and §8.5
diffs on it. All three fail if two equal records can serialize two ways, so there is
exactly one canonical form and one place that produces it.

`sha256_of` length-prefixes each part before concatenating. The SPEC writes the key
as `sha256(a ‖ b ‖ c ‖ d)`, and plain concatenation is not injective -- ("ab", "c")
and ("a", "bc") produce the same bytes. §8.7 requires a negative example recorded
today to still resolve after an extractor upgrade, which a colliding handle cannot do.
"""
from __future__ import annotations

import hashlib
import json


def canonical_json(value) -> str:
    """One form per value: key-ordered, unpadded, UTF-8, never ASCII-escaped."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _length_prefixed(part: str) -> bytes:
    encoded = part.encode("utf-8")
    return str(len(encoded)).encode("ascii") + b":" + encoded


def sha256_of(*parts: str) -> str:
    """An injective digest over an ordered tuple of strings, algorithm-prefixed."""
    digest = hashlib.sha256(b"".join(_length_prefixed(part) for part in parts))
    return "sha256:" + digest.hexdigest()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p4/test_p4_canonical.py -v`
Expected: PASS — 7 passed

- [ ] **Step 5: Commit**

```bash
git add src/evidence_shape/canonical.py tests/p4/test_p4_canonical.py
git commit -m "feat(P4): canonical JSON and an injective digest, defined once"
```

---

### Task 6: Record 1 — the observation, and `observation_key` (M5, M14, MINOR 8)

**Files:**
- Create: `src/evidence_shape/observation.py`
- Test: `tests/p4/test_p4_observation.py`

**Interfaces:**
- Consumes: `evidence_shape.canonical` — `sha256_of`; `evidence_shape.location` — `Location`; `evidence_shape.locator` — `serialize_locator`, `location_to_mapping`, `location_from_mapping`; `evidence_shape.vocabulary` — `EXTRACTOR_RELIABILITY_STATES`, `SIGNAL_TIERS`, `SOURCE_TYPES`, `check`; `database_agent.supersede.SUPERSEDE_COLUMNS`.
- Produces: `MalformedObservation`, `SECTION_2_8_LINES`, `SECTION_2_8_FIELDS`, `ADDED_FIELDS`, `OBSERVATION_FIELDS`, `OBSERVATION_ROW_FIELDS`, `NULLABLE_FIELDS`, `observation_key(*, content_hash, extractor_name, locator, raw_value) -> str`, `Observation`, `observation_from_mapping(mapping) -> Observation`, `collapse_key(observation) -> tuple[str, str, str]`.

**Two field sets, because a value and a row are different things.** `Observation` is what an extractor *emits*: eighteen fields. The stored row adds four the store owns — `observation_id` (a per-row primary key, minted at write time) and P1's three supersede columns, which are set by a later run, not by the extractor that wrote the row. `OBSERVATION_ROW_FIELDS` is the full twenty-two and is what Task 9's DDL and Task 13's rule 6 are written against, so nobody can read the split as P4 having dropped a published field.

**§2.8's eleven lines become fourteen field names**, and `SECTION_2_8_LINES` keeps the eleven so the counting discipline MINOR 1 imposed on P1 is available here too. *"Extractor name and version"* is one line and two fields; *"Surrounding context"* is one line and — **M5** — three fields:

> P4's three-field split (`context_before`, `context_after`, `context_truncated`) is kept — §8.4 must redact a value without dropping its context. **P5, P6, P8, P9 and P11 correct their reproduced field lists** to name P4's three fields instead of §2.8's single "surrounding context" line.

`context_truncated` is an addition rather than one of §2.8's own, because it comes from §8.6 (*never truncate silently*); the SPEC marks it ✚ and this task keeps that marking in `ADDED_FIELDS`. A mapping carrying a single `surrounding_context` field is rejected: conformance rule 1 makes a single-field emission a conformance failure, and the test below is that rule's first appearance.

**`observation_key` excludes `extractor_version` and that is the point** (MINOR 8). §8.5 requires the replay harness to compare a new extractor version against a prior result for the same content; a key including the version makes every row a false diff and leaves nothing to diff against. **This is a deliberate divergence from P2**, whose replay bundle keys its extraction output by content hash *plus* extractor version: the bundle names *which run* is being compared while the key names *the same observation across runs*. It is intentional and is not a bug to be fixed.

**`observation_key` is the citation handle, never `observation_id`** (M14). `observation_id` is per-row and dies on extractor upgrade; §8.7 requires a negative example recorded today to still resolve afterwards, and only the content-addressed key satisfies it.

**`reliability` is restricted to two at construction, not only at the validator.** The SPEC is explicit: *"`validated`, `llm_supported`, `user_confirmed` and `rejected` are fact-layer outcomes and P4 rejects an observation carrying them."* Whether a *user* may author an observation at all is a different axis and is **Open question 5**, held open in Task 19: P4 neither supplies a user-authored writer nor forbids one, and adds no user field to the record.

**`confidence` has no range.** §2.7 requires *"confidence information"* be preserved and names no scale; §3.13 adds that it is *"not comparable across extractors"*. So P4 stores a number or null and asserts nothing about `0..1`, percentages, or ordering. Inventing a range here would silently rescale one provider's numbers into another's.

**`normalized_value = null` is always legal** (RAW-3). An extractor that cannot normalize safely leaves it null rather than guessing (§3.10). D8 bounds what may go in it at all: Unicode NFC, whitespace collapse, soft-hyphen/line-break repair, and an ISO-8601 rendering of a timestamp the source stored as a structured date — never entity resolution, never abbreviation expansion, never a date parsed out of free text. P4 carries the field and performs none of those transforms; the extractor does.

**`collapse_key` is D10's three, published so six extractors collapse the same way.** *"One observation per (run, exact raw value, zone); `occurrence_count` counts within that zone; `location` addresses the first occurrence in document order."* Collapsing is on **exact** raw match, because P4 makes no normalization judgement: `Columbia` and `columbia` are two observations. **P4 publishes the key and enforces no uniqueness on it** — the SPEC's twelve conformance rules do not include one, and adding a thirteenth would be P4 legislating P5's traversal.

- [ ] **Step 1: Write the failing test**

```python
# tests/p4/test_p4_observation.py
import pytest

from database_agent.supersede import SUPERSEDE_COLUMNS

from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import (
    ADDED_FIELDS, MalformedObservation, NULLABLE_FIELDS, OBSERVATION_FIELDS,
    OBSERVATION_ROW_FIELDS, Observation, SECTION_2_8_FIELDS, SECTION_2_8_LINES,
    collapse_key, observation_from_mapping, observation_key,
)
from evidence_shape.vocabulary import NotInVocabulary

#: SPEC fixture 1: §2.8's "page 1, heading 2", which is also §3.2's worked syllabus
#: and the walking skeleton's one observation.
FIXTURE_1 = dict(
    file_id="f1", content_hash="sha256:abc", extractor_name="pdf.text",
    extractor_version="3.1.0", source_type="text_document", raw_value="BUSIB 4300",
    location=Location("heading", (Segment("page", 1),
                                  Segment("heading", 2, label="Course Information"))),
    occurrence_count=3, observed_at="2026-08-19T14:03:22+00:00", reliability="possible",
    run_id="r1", normalized_value="BUSIB 4300", context_before="Syllabus — ",
    context_after=" — Spring 2026", context_truncated=False,
)


def test_2_8s_eleven_lines_become_fourteen_field_names():
    # MINOR 1's counting discipline: §2.8 prints eleven lines. "Extractor name and
    # version" is one line and two fields; "Surrounding context" is one line and,
    # under M5, three fields -- of which two are §2.8's and `context_truncated` is
    # §8.6's addition.
    assert len(SECTION_2_8_LINES) == 11
    assert len(SECTION_2_8_FIELDS) == 13
    assert "context_before" in SECTION_2_8_FIELDS
    assert "context_after" in SECTION_2_8_FIELDS
    assert "context_truncated" in ADDED_FIELDS
    assert "surrounding_context" not in OBSERVATION_ROW_FIELDS


def test_the_emitted_field_set_and_the_row_field_set_partition_cleanly():
    assert set(SECTION_2_8_FIELDS) | set(ADDED_FIELDS) == set(OBSERVATION_ROW_FIELDS)
    assert not set(SECTION_2_8_FIELDS) & set(ADDED_FIELDS)
    assert len(OBSERVATION_FIELDS) == 18
    assert len(OBSERVATION_ROW_FIELDS) == 22


def test_the_row_adds_exactly_the_id_and_p1s_three_supersede_columns():
    # M1: P1 publishes the set; P4 adopts three of the four. `preferred` is the one
    # P4 does not take -- §8.2 gives preference to the resolver and §3.2 places the
    # resolver after extraction, so it lives on P6's `file_facts`.
    assert set(OBSERVATION_ROW_FIELDS) - set(OBSERVATION_FIELDS) == \
        {"observation_id", *SUPERSEDE_COLUMNS}
    assert SUPERSEDE_COLUMNS == ("supersedes", "superseded_by", "supersede_reason")
    assert "preferred" not in OBSERVATION_ROW_FIELDS


def test_minor_3s_spelling_is_the_one_that_survived():
    assert "supersede_reason" in OBSERVATION_ROW_FIELDS
    assert "supersession_reason" not in OBSERVATION_ROW_FIELDS


def test_only_five_fields_are_nullable():
    assert NULLABLE_FIELDS == frozenset(
        {"normalized_value", "context_before", "context_after", "confidence",
         "signal_tier"})
    assert "raw_value" not in NULLABLE_FIELDS
    assert "location" not in NULLABLE_FIELDS


def test_fixture_1_builds_and_carries_its_locator():
    observation = Observation(**FIXTURE_1)
    assert observation.locator == "heading:page=1/heading=2"
    assert observation.zone == "heading"
    assert observation.observation_key.startswith("sha256:")


def test_the_key_is_stable_across_extractor_versions():
    # MINOR 8, stated in one sentence so nobody "fixes" it into a bug: P4 excludes
    # `extractor_version` from `observation_key` SO THAT §8.5's replay diff across
    # extractor versions has something to diff against.
    first = Observation(**FIXTURE_1)
    upgraded = Observation(**{**FIXTURE_1, "extractor_version": "4.0.0"})
    assert first.observation_key == upgraded.observation_key
    assert first.extractor_version != upgraded.extractor_version


def test_the_key_moves_when_any_of_its_four_inputs_moves():
    first = Observation(**FIXTURE_1)
    for changed in ({"raw_value": "BUSIB 4301"},
                    {"content_hash": "sha256:def"},
                    {"extractor_name": "ocr.apple_vision"},
                    {"location": Location("body", (Segment("page", 1),))}):
        assert Observation(**{**FIXTURE_1, **changed}).observation_key != \
            first.observation_key


def test_the_key_function_takes_the_four_inputs_the_spec_names():
    observation = Observation(**FIXTURE_1)
    assert observation_key(content_hash="sha256:abc", extractor_name="pdf.text",
                           locator="heading:page=1/heading=2",
                           raw_value="BUSIB 4300") == observation.observation_key


def test_the_key_is_not_the_row_id():
    # M14: `observation_id` is per-row and dies on extractor upgrade; §8.7 requires a
    # negative example recorded today to still resolve after that upgrade.
    assert "observation_id" not in OBSERVATION_FIELDS
    assert "observation_key" in OBSERVATION_FIELDS


def test_the_mapping_form_round_trips_in_the_specs_field_order():
    observation = Observation(**FIXTURE_1)
    mapping = observation.to_mapping()
    assert list(mapping) == list(OBSERVATION_FIELDS)
    assert observation_from_mapping(mapping) == observation


def test_a_single_surrounding_context_field_fails_conformance_rule_1():
    # M5: a consumer or extractor author reproducing §2.8's list must name P4's three
    # fields, not one. §8.4 must be able to redact a value without dropping its
    # context, or the reverse.
    mapping = Observation(**FIXTURE_1).to_mapping()
    collapsed = {name: value for name, value in mapping.items()
                 if name not in ("context_before", "context_after", "context_truncated")}
    collapsed["surrounding_context"] = "Syllabus — BUSIB 4300 — Spring 2026"
    with pytest.raises(MalformedObservation):
        observation_from_mapping(collapsed)


def test_an_extractor_may_write_two_reliability_states_and_no_other():
    # D11. The other four are fact-layer outcomes (§3.5); §2.8 forbids extraction
    # from treating model output as proof.
    assert Observation(**{**FIXTURE_1, "reliability": "direct"}).reliability == "direct"
    for fact_state in ("validated", "llm_supported", "user_confirmed", "rejected"):
        with pytest.raises(NotInVocabulary):
            Observation(**{**FIXTURE_1, "reliability": fact_state})


def test_the_location_is_the_structured_record_and_never_a_string():
    # P5 OQ1, closed: §2.8's per-source-type examples cannot be expressed by a string.
    with pytest.raises(MalformedObservation):
        Observation(**{**FIXTURE_1, "location": "page 1, heading 2"})


def test_occurrence_count_is_at_least_one():
    # Conformance rule 7. An observation records presence; a count of zero is an
    # absence, and absence lives on the run record or nowhere (§2.6).
    assert Observation(**{**FIXTURE_1, "occurrence_count": 1}).occurrence_count == 1
    for absent in (0, -1):
        with pytest.raises(MalformedObservation):
            Observation(**{**FIXTURE_1, "occurrence_count": absent})


def test_raw_value_is_never_empty():
    with pytest.raises(MalformedObservation):
        Observation(**{**FIXTURE_1, "raw_value": ""})


def test_normalized_value_may_always_be_null():
    # RAW-3: an extractor that cannot normalize safely leaves it null rather than
    # guessing (§3.10 forbids fuzzy date parsing).
    assert Observation(**{**FIXTURE_1, "normalized_value": None}).normalized_value is None


def test_signal_tier_is_2_6s_three_levels_or_null():
    for tier in (1, 2, 3, None):
        assert Observation(**{**FIXTURE_1, "signal_tier": tier}).signal_tier == tier
    with pytest.raises(NotInVocabulary):
        Observation(**{**FIXTURE_1, "signal_tier": 4})


def test_confidence_carries_no_range_because_2_7_names_no_scale():
    # §3.13: the number is "not comparable across extractors". A range invented here
    # would silently rescale one provider's numbers into another's.
    for value in (0.92, 0, 1, 87, None):
        assert Observation(**{**FIXTURE_1, "confidence": value}).confidence == value


def test_the_record_refuses_a_field_it_does_not_publish():
    # Conformance rule 6's structural half: no destination, domain, field name,
    # group, node, template or plan reference can be attached, because the record is
    # a closed field set and an unknown key is a rejection.
    mapping = Observation(**FIXTURE_1).to_mapping()
    for forbidden in ("proposed_path", "domain", "field_name", "group_id", "node_id",
                      "template_id", "plan_version_id", "handling_class"):
        with pytest.raises(MalformedObservation):
            observation_from_mapping({**mapping, forbidden: "x"})


def test_a_stored_key_that_does_not_match_its_observation_is_rejected():
    mapping = Observation(**FIXTURE_1).to_mapping()
    with pytest.raises(MalformedObservation):
        observation_from_mapping({**mapping, "observation_key": "sha256:0"})


def test_an_observation_is_frozen():
    # RAW-2: `raw_value` is never updated, ever. Improvement is insert + supersede.
    observation = Observation(**FIXTURE_1)
    with pytest.raises(Exception):
        observation.raw_value = "BUSIB 4301"


def test_the_same_value_in_two_zones_is_two_observations_with_two_counts():
    # D10, and the reason §2.2's rule works at all: a page-one heading outweighs a
    # page-eighteen reference list, which is only expressible if they are two rows.
    heading = Observation(**{**FIXTURE_1, "raw_value": "Columbia"})
    body = Observation(**{**FIXTURE_1, "raw_value": "Columbia",
                          "location": Location("body", (Segment("page", 18),),
                                               text_span=TextSpan(12043, 12051))})
    assert collapse_key(heading) == ("r1", "Columbia", "heading")
    assert collapse_key(body) == ("r1", "Columbia", "body")
    assert collapse_key(heading) != collapse_key(body)


def test_collapsing_is_on_exact_raw_match_because_p4_judges_no_normalization():
    # `Columbia` and `columbia` are two observations. Cross-form aggregation is P6's
    # (§3.7 word-boundary matching and ranking).
    upper = Observation(**{**FIXTURE_1, "raw_value": "Columbia"})
    lower = Observation(**{**FIXTURE_1, "raw_value": "columbia"})
    assert collapse_key(upper) != collapse_key(lower)
    assert upper.observation_key != lower.observation_key
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p4/test_p4_observation.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'evidence_shape.observation'`

- [ ] **Step 3: Write the implementation**

```python
# src/evidence_shape/observation.py
"""Record 1 -- the observation. §2.8's field list, in §2.8's order.

The table name is the design's (§3.12: "**evidence** -- stores raw observations from
extractors, including the source, location, surrounding text, extractor version, and
content hash"). §2.8 says "At minimum, every observation should contain...", which is
what licenses the additions; each traces to a section that requires the information
be preserved.

Two field sets, because a value and a row are different things. `Observation` is what
an extractor emits (eighteen fields). The stored row adds `observation_id` and P1's
three supersede columns, which a later run sets and the emitting extractor does not.

`observation_key` deliberately EXCLUDES `extractor_version`: §8.5 requires the replay
harness to compare a new extractor version against a prior result for the same
content, and identity that included the version would make every row a false diff
(MINOR 8). It is the citation handle every consumer cites -- never `observation_id`,
which is per-row and dies on extractor upgrade while §8.7 requires a negative example
recorded today to still resolve afterwards (M14).
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from database_agent.supersede import SUPERSEDE_COLUMNS

from evidence_shape.canonical import sha256_of
from evidence_shape.location import Location
from evidence_shape.locator import (
    location_from_mapping, location_to_mapping, serialize_locator,
)
from evidence_shape.vocabulary import (
    EXTRACTOR_RELIABILITY_STATES, SIGNAL_TIERS, SOURCE_TYPES, check,
)

#: §2.8's own eleven lines, verbatim, kept so the counting stays checkable (MINOR 1).
SECTION_2_8_LINES: tuple[str, ...] = (
    "File identifier", "Content hash", "Extractor name and version", "Source type",
    "Raw value", "Normalized candidate value", "Location", "Surrounding context",
    "Occurrence count", "Observation time", "Reliability state",
)

#: Those eleven lines as field names. "Extractor name and version" is two;
#: "Surrounding context" is `context_before` + `context_after` (M5).
SECTION_2_8_FIELDS: tuple[str, ...] = (
    "file_id", "content_hash", "extractor_name", "extractor_version", "source_type",
    "raw_value", "normalized_value", "location", "context_before", "context_after",
    "occurrence_count", "observed_at", "reliability",
)

#: Required elsewhere in the design, and marked ✚ in the SPEC. `context_truncated` is
#: §8.6's (never truncate silently); `run_id` is D5's; `confidence` is §2.7's;
#: `signal_tier` is §2.6's (M2); the three supersede columns are §8.2's (M1).
ADDED_FIELDS: tuple[str, ...] = (
    "observation_id", "observation_key", "context_truncated", "run_id", "confidence",
    "signal_tier", *SUPERSEDE_COLUMNS,
)

#: What an extractor emits, in the SPEC's display order.
OBSERVATION_FIELDS: tuple[str, ...] = (
    "observation_key",
    "file_id", "content_hash", "extractor_name", "extractor_version", "source_type",
    "raw_value", "normalized_value", "location", "context_before", "context_after",
    "context_truncated", "occurrence_count", "observed_at", "reliability",
    "run_id", "confidence", "signal_tier",
)

#: What the table holds. The store owns the four that are not emitted.
OBSERVATION_ROW_FIELDS: tuple[str, ...] = (
    ("observation_id",) + OBSERVATION_FIELDS + SUPERSEDE_COLUMNS
)

#: Nullable only where the SPEC states it (conformance rule 1).
NULLABLE_FIELDS = frozenset(
    {"normalized_value", "context_before", "context_after", "confidence", "signal_tier"})


class MalformedObservation(ValueError):
    """A non-conforming observation. P4 fails it rather than coercing it."""


def observation_key(*, content_hash: str, extractor_name: str, locator: str,
                    raw_value: str) -> str:
    """`sha256(content_hash ‖ extractor_name ‖ locator ‖ raw_value)`, injectively.

    `extractor_version` is absent on purpose: §8.5's replay diff compares a new
    extractor version against a prior result for the same content, and a key that
    carried the version would leave nothing to diff against (MINOR 8). Version
    differences are visible in the rows, not in the key.
    """
    return sha256_of(content_hash, extractor_name, locator, raw_value)


#: The property below needs the function while the class body shadows the name.
_key = observation_key


@dataclass(frozen=True, slots=True)
class Observation:
    """One located reading of one value in one file version."""

    file_id: str
    content_hash: str
    extractor_name: str
    extractor_version: str
    source_type: str
    raw_value: str
    location: Location
    occurrence_count: int
    observed_at: str
    reliability: str
    run_id: str
    normalized_value: str | None = None
    context_before: str | None = None
    context_after: str | None = None
    context_truncated: bool = False
    confidence: float | None = None
    signal_tier: int | None = None

    def __post_init__(self) -> None:
        for name in ("file_id", "content_hash", "extractor_name", "extractor_version",
                     "raw_value", "observed_at", "run_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise MalformedObservation(
                    f"{name} is a non-empty string, not {value!r}")
        check(self.source_type, SOURCE_TYPES, name="source_type")
        # D11: an extractor writes two of §3.13's six. The other four are fact-layer
        # outcomes (§3.5) and §2.8 forbids treating model output as proof.
        check(self.reliability, EXTRACTOR_RELIABILITY_STATES, name="reliability")
        if not isinstance(self.location, Location):
            raise MalformedObservation(
                "location is the structured record (D1), never a per-format string")
        for name in ("normalized_value", "context_before", "context_after"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, str):
                raise MalformedObservation(f"{name} is a string or None")
        if type(self.context_truncated) is not bool:
            raise MalformedObservation(
                "context_truncated is a bool and is never absent (§8.6)")
        if type(self.occurrence_count) is not int or self.occurrence_count < 1:
            raise MalformedObservation(
                "occurrence_count >= 1 (rule 7): an observation records presence, and "
                "absence lives on the run record or nowhere (§2.6)")
        if self.confidence is not None and type(self.confidence) not in (int, float):
            raise MalformedObservation(
                "confidence is the extractor's own number, or None. §2.7 names no "
                "scale and §3.13 says it is not comparable across extractors, so P4 "
                "stores it and asserts no range")
        if self.signal_tier is not None:
            check(self.signal_tier, SIGNAL_TIERS, name="signal_tier")

    @property
    def locator(self) -> str:
        """The canonical string form of `location`, and one input to the key."""
        return serialize_locator(self.location)

    @property
    def observation_key(self) -> str:
        """M14's citation handle."""
        return _key(content_hash=self.content_hash, extractor_name=self.extractor_name,
                    locator=self.locator, raw_value=self.raw_value)

    @property
    def zone(self) -> str:
        """§2.2's "document zone", which §3.7 weights and D10 collapses on."""
        return self.location.zone

    def to_mapping(self) -> dict[str, object]:
        mapping = {name: getattr(self, name) for name in OBSERVATION_FIELDS
                   if name not in ("location", "observation_key")}
        mapping["location"] = location_to_mapping(self.location)
        mapping["observation_key"] = self.observation_key
        return {name: mapping[name] for name in OBSERVATION_FIELDS}


def observation_from_mapping(mapping: Mapping[str, object]) -> Observation:
    """Build from a stored row or a fixture. Rejects; never fills a gap in."""
    missing = [name for name in OBSERVATION_FIELDS
               if name != "observation_key" and name not in mapping]
    if missing:
        raise MalformedObservation(
            f"missing fields: {missing}. §2.8's "
            '"Surrounding context" is three fields here -- context_before, '
            "context_after and context_truncated -- not one (M5)")
    unknown = sorted(set(mapping) - set(OBSERVATION_ROW_FIELDS))
    if unknown:
        raise MalformedObservation(
            f"{unknown} are not fields of the observation record. §2.8: extraction "
            "does not create a final folder path, invent domains, merge all files "
            "that share one string, or treat model output as proof")
    location = mapping["location"]
    observation = Observation(
        file_id=mapping["file_id"],
        content_hash=mapping["content_hash"],
        extractor_name=mapping["extractor_name"],
        extractor_version=mapping["extractor_version"],
        source_type=mapping["source_type"],
        raw_value=mapping["raw_value"],
        location=location if isinstance(location, Location)
        else location_from_mapping(location),
        occurrence_count=mapping["occurrence_count"],
        observed_at=mapping["observed_at"],
        reliability=mapping["reliability"],
        run_id=mapping["run_id"],
        normalized_value=mapping["normalized_value"],
        context_before=mapping["context_before"],
        context_after=mapping["context_after"],
        context_truncated=mapping["context_truncated"],
        confidence=mapping["confidence"],
        signal_tier=mapping["signal_tier"],
    )
    stated = mapping.get("observation_key")
    if stated is not None and stated != observation.observation_key:
        raise MalformedObservation(
            f"observation_key {stated!r} is not the key of this observation; the "
            "handle §8.7 depends on must be derivable from the row it names")
    return observation


def collapse_key(observation: Observation) -> tuple[str, str, str]:
    """D10's three: (run, exact raw value, zone).

    Published so six extractors collapse the same way. P4 enforces no uniqueness on
    it -- the SPEC's twelve conformance rules do not include one, and adding a
    thirteenth would be P4 legislating P5's traversal.
    """
    return (observation.run_id, observation.raw_value, observation.location.zone)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p4/test_p4_observation.py -v`
Expected: PASS — 24 passed

- [ ] **Step 5: Commit**

```bash
git add src/evidence_shape/observation.py tests/p4/test_p4_observation.py
git commit -m "feat(P4): Record 1 — the observation, and the version-free citation key"
```

---

### Task 7: Record 2 — `extraction_runs`, the one extraction-outcome record (D5, B1, I4)

**Files:**
- Create: `src/evidence_shape/runs.py`
- Test: `tests/p4/test_p4_runs.py`

**Interfaces:**
- Consumes: `evidence_shape.canonical` — `canonical_json`, `sha256_of`; `evidence_shape.vocabulary` — `ANALYSIS_TIERS`, `COMPLETENESS`, `SOURCE_TYPES`, `check`.
- Produces: `MalformedRun`, `RUN_FIELDS`, `Coverage`, `ExtractionRun`, `run_from_mapping(mapping) -> ExtractionRun`, `config_fingerprint(config) -> str`.

**This is the record §2.4's distinction lives in.** *"An empty extraction result is different from an extractor that does not yet exist."* A `complete` run with zero observations means the file genuinely contained nothing extractable; an `unsupported` run with zero observations means no extractor exists. Neither can be expressed on an observation, because both cases produce **zero** observations — which is why D5 exists at all.

**B1 settled that there is exactly one such record**, and it is this one:

> **P4's `extraction_runs` is the record. P5's parallel status vocabulary is deleted.** P4 is per-*(file version × extractor)*; P5 is per-file. An opaque image runs both the image extractor and OCR — two P4 rows, one P5 row — so P5 structurally cannot express "EXIF read successfully, OCR capped."

**`analysis_tier` is I4's closed four and is not `source_type`.** *"`analysis_tier ∈ filesystem | native | ocr | llm`. P5 owns the vocabulary and writes the first three; P8 writes `llm`. A value outside the four is rejected. `source_type` remains a different field."*

**Where §2.7's OCR requirements land** — **P5 OQ2 is closed** ([`../../05-minor-resolutions.md`](../../05-minor-resolutions.md)): *"Where do OCR provider / config / languages / confidence / capped-flag live? **P4's `extraction_runs`.** §2.7 requires all of them stored, and P4's record is per-(file × extractor), which is the only granularity that can hold them."* Concretely: provider and version are `extractor_name` / `extractor_version`; languages and configuration are `config` (fingerprinted so §3.4's cache key and §8.5's diff can tell two configurations apart); complete-or-capped is `completeness` with `coverage`.

**`config` is opaque and `coverage.units` is caller-supplied.** §2.7 names *"languages, configuration"* and no schema for either; §8.6's `coverage` example says `"units": "pages"` and names no vocabulary of units. So P4 stores whatever mapping it is handed, fingerprints it canonically, and defines **no** config schema and **no** closed set of unit names. An extractor that measures in regions or in bytes says so; P4 does not adjudicate.

**P4 enforces no `coverage` requirement.** §8.6 needs `coverage` to make its progress line computable rather than estimated, and the SPEC says a capped run carries one — but the twelve conformance rules do not make it a rule, and P4 does not add a thirteenth. `coverage` is nullable and a capped run without one is stored as given, so the shortfall is visible rather than silently repaired.

**`failure_reason` is free text and belongs to two values only.** *"only when completeness ∈ {unreadable, failed}"*. A `capped` run did not fail; a `metadata_only` run is a deliberate policy stop, not a gap in the product.

**Runs carry no supersede columns.** The SPEC's Record 2 field list has none. A later extractor produces a **new run**; the earlier run and its `text_units` stay readable (§8.2), and it is the *observations* that carry `supersedes` / `superseded_by` / `supersede_reason`. Adding them to the run record would be adding a field the contract does not publish.

- [ ] **Step 1: Write the failing test**

```python
# tests/p4/test_p4_runs.py
import pytest

from evidence_shape.canonical import canonical_json
from evidence_shape.runs import (
    Coverage, ExtractionRun, MalformedRun, RUN_FIELDS, config_fingerprint,
    run_from_mapping,
)
from evidence_shape.vocabulary import NotInVocabulary

#: The SPEC's own worked run: an OCR pass that stopped at a ceiling.
OCR_RUN = dict(
    run_id="r1", file_id="f1", content_hash="sha256:abc",
    extractor_name="ocr.apple_vision", extractor_version="2.4.1", source_type="ocr",
    analysis_tier="ocr",
    config={"dpi": 200, "languages": ["en", "zh-Hans"], "recognition": "accurate"},
    completeness="capped",
    coverage=Coverage(units="pages", processed=40, total=312),
    observation_count=118, started_at="2026-08-19T14:00:00+00:00",
    finished_at="2026-08-19T14:03:22+00:00",
)


def test_the_record_carries_the_specs_fifteen_fields_in_order():
    assert RUN_FIELDS == (
        "run_id", "file_id", "content_hash", "extractor_name", "extractor_version",
        "source_type", "analysis_tier", "config", "config_fingerprint",
        "completeness", "coverage", "observation_count", "started_at", "finished_at",
        "failure_reason",
    )


def test_runs_carry_no_supersede_columns():
    # A later extractor produces a NEW run; the earlier run and its text units stay
    # readable (§8.2). Supersession is on the observation.
    for column in ("supersedes", "superseded_by", "supersede_reason", "preferred"):
        assert column not in RUN_FIELDS


def test_the_ocr_run_builds_and_fingerprints_its_configuration():
    run = ExtractionRun(**OCR_RUN)
    assert run.completeness == "capped"
    assert run.coverage.processed == 40
    assert run.config_fingerprint.startswith("sha256:")
    assert run.config_fingerprint == config_fingerprint(OCR_RUN["config"])


def test_the_fingerprint_depends_on_the_configuration_and_not_on_key_order():
    # §3.4's cache key and §8.5's diff must be able to tell two configurations apart,
    # and must not report a change when nothing changed.
    reordered = {"recognition": "accurate", "languages": ["en", "zh-Hans"], "dpi": 200}
    assert config_fingerprint(reordered) == config_fingerprint(OCR_RUN["config"])
    changed = {**OCR_RUN["config"], "dpi": 300}
    assert config_fingerprint(changed) != config_fingerprint(OCR_RUN["config"])
    dropped = {"dpi": 200, "recognition": "accurate"}
    assert config_fingerprint(dropped) != config_fingerprint(OCR_RUN["config"])


def test_an_empty_configuration_still_fingerprints():
    assert config_fingerprint({}).startswith("sha256:")
    assert ExtractionRun(**{**OCR_RUN, "config": {}}).config_fingerprint == \
        config_fingerprint({})


def test_all_eight_completeness_values_are_constructible():
    # B1's eight. There is no ninth here and none is invented for an iCloud dataless
    # file -- that is Open question 6 and Task 19 keeps it open.
    for value in ("complete", "capped", "partial", "metadata_only", "deferred",
                  "unsupported", "unreadable", "failed"):
        payload = {**OCR_RUN, "completeness": value, "observation_count": 0}
        if value in ("unreadable", "failed"):
            payload["failure_reason"] = "password-protected"
        assert ExtractionRun(**payload).completeness == value


def test_2_4s_distinction_is_expressible_on_this_record_and_nowhere_else():
    # "an empty extraction result is different from an extractor that does not yet
    # exist." Both produce zero observations; only the run record separates them.
    empty = ExtractionRun(**{**OCR_RUN, "completeness": "complete",
                             "observation_count": 0, "coverage": None})
    missing = ExtractionRun(**{**OCR_RUN, "completeness": "unsupported",
                               "observation_count": 0, "coverage": None})
    policy = ExtractionRun(**{**OCR_RUN, "completeness": "metadata_only",
                              "observation_count": 0, "coverage": None})
    assert len({empty.completeness, missing.completeness, policy.completeness}) == 3


def test_completeness_source_type_and_analysis_tier_are_closed():
    with pytest.raises(NotInVocabulary):
        ExtractionRun(**{**OCR_RUN, "completeness": "extracted_empty"})
    with pytest.raises(NotInVocabulary):
        ExtractionRun(**{**OCR_RUN, "source_type": "pdf"})
    with pytest.raises(NotInVocabulary):
        ExtractionRun(**{**OCR_RUN, "analysis_tier": "vision"})


def test_i4s_four_tiers_are_all_accepted_including_the_one_only_p8_writes():
    # I4: "P8 is the only writer of `llm` runs -- P4 accepts the value; P5 never
    # emits it." P4 does not police who calls it; it polices the vocabulary.
    for tier in ("filesystem", "native", "ocr", "llm"):
        assert ExtractionRun(**{**OCR_RUN, "analysis_tier": tier}).analysis_tier == tier


def test_coverage_units_are_caller_supplied_because_8_6_names_no_vocabulary():
    for units in ("pages", "regions", "bytes", "entries"):
        assert Coverage(units=units, processed=1, total=2).units == units


def test_coverage_counts_are_non_negative_and_processed_never_exceeds_total():
    assert Coverage("pages", 0, 0).processed == 0
    with pytest.raises(MalformedRun):
        Coverage("pages", -1, 10)
    with pytest.raises(MalformedRun):
        Coverage("pages", 11, 10)


def test_coverage_is_optional_because_no_conformance_rule_requires_it():
    # §8.6 wants it on a capped run and the twelve rules do not make it a rule. P4
    # stores what it is handed rather than repairing a shortfall out of sight.
    assert ExtractionRun(**{**OCR_RUN, "coverage": None}).coverage is None


def test_a_failure_reason_belongs_to_unreadable_and_failed_and_to_nothing_else():
    assert ExtractionRun(**{**OCR_RUN, "completeness": "failed",
                            "failure_reason": "extractor raised"}).failure_reason
    assert ExtractionRun(**{**OCR_RUN, "completeness": "unreadable",
                            "failure_reason": "password-protected"}).failure_reason
    for wrong in ("complete", "capped", "partial", "metadata_only", "deferred",
                  "unsupported"):
        with pytest.raises(MalformedRun):
            ExtractionRun(**{**OCR_RUN, "completeness": wrong,
                             "failure_reason": "something went wrong"})


def test_observation_count_is_never_negative():
    with pytest.raises(MalformedRun):
        ExtractionRun(**{**OCR_RUN, "observation_count": -1})


def test_the_mapping_form_round_trips():
    run = ExtractionRun(**OCR_RUN)
    mapping = run.to_mapping()
    assert list(mapping) == list(RUN_FIELDS)
    assert mapping["config"] == OCR_RUN["config"]
    assert mapping["coverage"] == {"units": "pages", "processed": 40, "total": 312}
    assert run_from_mapping(mapping) == run


def test_the_mapping_form_rejects_a_field_the_record_does_not_publish():
    mapping = ExtractionRun(**OCR_RUN).to_mapping()
    for forbidden in ("plan_version_id", "handling_class", "domain", "node_id"):
        with pytest.raises(MalformedRun):
            run_from_mapping({**mapping, forbidden: "x"})


def test_a_stored_fingerprint_that_does_not_match_its_config_is_rejected():
    mapping = ExtractionRun(**OCR_RUN).to_mapping()
    with pytest.raises(MalformedRun):
        run_from_mapping({**mapping, "config_fingerprint": "sha256:0"})


def test_the_config_is_stored_as_handed_and_p4_defines_no_schema_for_it():
    # §2.7 names "languages, configuration" and no schema for either.
    exotic = {"engine": {"model": "x", "beams": 4}, "languages": [], "strict": True}
    run = ExtractionRun(**{**OCR_RUN, "config": exotic})
    assert run.config == exotic
    assert canonical_json(run.to_mapping()["config"]) == canonical_json(exotic)


def test_a_run_is_frozen():
    run = ExtractionRun(**OCR_RUN)
    with pytest.raises(Exception):
        run.completeness = "complete"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p4/test_p4_runs.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'evidence_shape.runs'`

- [ ] **Step 3: Write the implementation**

```python
# src/evidence_shape/runs.py
"""Record 2 -- `extraction_runs`, one row per (file version × extractor).

D5: two records for outcomes, not one. §2.4 forbids conflating "unsupported format"
with "empty document"; §2.5 requires "partially inspected"; §2.7 requires provider,
version, languages, configuration and whether extraction was complete or capped be
preserved; §2.9 requires "indexed-but-unreadable"; §8.6 requires the deferred stage
be marked. None of those can live on an observation, because the cases that need them
produce ZERO observations.

B1 makes this THE extraction-outcome record for the whole system: P5 writes one row
per (file version × extractor) and publishes no parallel status vocabulary of its own.
An opaque image runs the image extractor and OCR, which is two rows -- one may be
`complete` while the other is `capped`.

Absence is recorded here or nowhere. A `complete` run that emitted no `metadata`
observations IS the record that the file carried no such metadata; §2.6's "no EXIF"
is exactly this case. No field is added for it and no observation is written for it.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.vocabulary import (
    ANALYSIS_TIERS, COMPLETENESS, SOURCE_TYPES, check,
)

#: The SPEC's Record 2, in the SPEC's order.
RUN_FIELDS: tuple[str, ...] = (
    "run_id", "file_id", "content_hash", "extractor_name", "extractor_version",
    "source_type", "analysis_tier", "config", "config_fingerprint", "completeness",
    "coverage", "observation_count", "started_at", "finished_at", "failure_reason",
)

#: §2.4, §2.9. Free text, and only for a run that did not complete on its own terms.
_FAILURE_COMPLETENESS = frozenset({"unreadable", "failed"})


class MalformedRun(ValueError):
    """A non-conforming run record. P4 fails it rather than coercing it."""


def config_fingerprint(config: Mapping) -> str:
    """So §3.4's cache key and §8.5's diff can tell two configurations apart."""
    return sha256_of(canonical_json(config))


_fingerprint = config_fingerprint


@dataclass(frozen=True, slots=True)
class Coverage:
    """§8.6's "how far it got". `units` is caller-supplied: §8.6 names none."""

    units: str
    processed: int
    total: int

    def __post_init__(self) -> None:
        if not isinstance(self.units, str) or not self.units:
            raise MalformedRun("coverage.units is a non-empty string")
        for name in ("processed", "total"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise MalformedRun(f"coverage.{name} is a non-negative integer")
        if self.processed > self.total:
            raise MalformedRun("coverage.processed <= coverage.total")

    def to_mapping(self) -> dict[str, object]:
        return {"units": self.units, "processed": self.processed, "total": self.total}


@dataclass(frozen=True, slots=True)
class ExtractionRun:
    """What happened when one extractor ran over one content version."""

    run_id: str
    file_id: str
    content_hash: str
    extractor_name: str
    extractor_version: str
    source_type: str
    analysis_tier: str
    config: Mapping
    completeness: str
    started_at: str
    observation_count: int = 0
    coverage: Coverage | None = None
    finished_at: str | None = None
    failure_reason: str | None = None

    def __post_init__(self) -> None:
        for name in ("run_id", "file_id", "content_hash", "extractor_name",
                     "extractor_version", "started_at"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise MalformedRun(f"{name} is a non-empty string, not {value!r}")
        check(self.source_type, SOURCE_TYPES, name="source_type")
        # I4: "A value outside the four is rejected."
        check(self.analysis_tier, ANALYSIS_TIERS, name="analysis_tier")
        check(self.completeness, COMPLETENESS, name="completeness")
        if not isinstance(self.config, Mapping):
            raise MalformedRun("config is a mapping; P4 defines no schema for it")
        if self.coverage is not None and not isinstance(self.coverage, Coverage):
            raise MalformedRun("coverage is a Coverage or None")
        if type(self.observation_count) is not int or self.observation_count < 0:
            raise MalformedRun("observation_count is a non-negative integer")
        if self.failure_reason is not None:
            if not isinstance(self.failure_reason, str):
                raise MalformedRun("failure_reason is free text or None")
            if self.completeness not in _FAILURE_COMPLETENESS:
                raise MalformedRun(
                    f"failure_reason belongs to completeness in "
                    f"{sorted(_FAILURE_COMPLETENESS)}, not {self.completeness!r}: a "
                    "capped run did not fail, and metadata_only is a deliberate "
                    "policy stop (§2.9), not a gap in the product")

    @property
    def config_fingerprint(self) -> str:
        return _fingerprint(self.config)

    def to_mapping(self) -> dict[str, object]:
        mapping = {
            "run_id": self.run_id, "file_id": self.file_id,
            "content_hash": self.content_hash, "extractor_name": self.extractor_name,
            "extractor_version": self.extractor_version,
            "source_type": self.source_type, "analysis_tier": self.analysis_tier,
            "config": dict(self.config), "config_fingerprint": self.config_fingerprint,
            "completeness": self.completeness,
            "coverage": None if self.coverage is None else self.coverage.to_mapping(),
            "observation_count": self.observation_count,
            "started_at": self.started_at, "finished_at": self.finished_at,
            "failure_reason": self.failure_reason,
        }
        return {name: mapping[name] for name in RUN_FIELDS}


def run_from_mapping(mapping: Mapping[str, object]) -> ExtractionRun:
    missing = [name for name in RUN_FIELDS
               if name != "config_fingerprint" and name not in mapping]
    if missing:
        raise MalformedRun(f"missing run fields: {missing}")
    unknown = sorted(set(mapping) - set(RUN_FIELDS))
    if unknown:
        raise MalformedRun(f"{unknown} are not fields of the run record")
    coverage = mapping["coverage"]
    run = ExtractionRun(
        run_id=mapping["run_id"], file_id=mapping["file_id"],
        content_hash=mapping["content_hash"],
        extractor_name=mapping["extractor_name"],
        extractor_version=mapping["extractor_version"],
        source_type=mapping["source_type"], analysis_tier=mapping["analysis_tier"],
        config=mapping["config"], completeness=mapping["completeness"],
        started_at=mapping["started_at"],
        observation_count=mapping["observation_count"],
        coverage=coverage if coverage is None or isinstance(coverage, Coverage)
        else Coverage(coverage["units"], coverage["processed"], coverage["total"]),
        finished_at=mapping["finished_at"], failure_reason=mapping["failure_reason"],
    )
    stated = mapping.get("config_fingerprint")
    if stated is not None and stated != run.config_fingerprint:
        raise MalformedRun(
            f"config_fingerprint {stated!r} is not the fingerprint of this config; "
            "§3.4's cache key would then name a configuration that never ran")
    return run
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p4/test_p4_runs.py -v`
Expected: PASS — 19 passed

- [ ] **Step 5: Commit**

```bash
git add src/evidence_shape/runs.py tests/p4/test_p4_runs.py
git commit -m "feat(P4): Record 2 — extraction_runs, the one extraction-outcome record"
```

---

### Task 8: Record 3 — `text_units`, and RAW-1 (G1, D12, Done-means 4 and 10)

**Files:**
- Create: `src/evidence_shape/text_units.py`
- Test: `tests/p4/test_p4_text_units.py`

**Interfaces:**
- Consumes: `evidence_shape.location` — `Segment`, `TextSpan`; `evidence_shape.locator` — `serialize_container_path`; `evidence_shape.observation` — `Observation`.
- Produces: `MalformedTextUnit`, `SpanAnchorError`, `TEXT_UNIT_FIELDS`, `TextUnit`, `text_unit_from_mapping(mapping) -> TextUnit`, `check_span_anchor(observation, unit) -> None`, `raw_value_at(unit, text_span) -> str`.

**G1 called this a blocker, and it was.** [`../../04-resolutions.md`](../../04-resolutions.md): *"**P4** adds a `text_units` record keyed by `(run_id, container_path)`. P4's `text_span` already presupposes an addressable text unit and declined to own it; P5 emits bulk text with no home. **Blocks the skeleton** — resolve first."*

**Why a third record rather than more observations.** §2.2 requires *"complete text by page"*, §2.4 the full text of a text-bearing file, §2.7 *"raw recognized text"*. None of those is a *located value*, so none is an observation — yet a `text_span` is defined as an offset into a stored, addressable text unit, so the unit must exist and must be addressed by the same `container_path` vocabulary the observation uses. One observation per page of text would make `raw_value` mean two different things, and would break D10's collapsing rule and §8.6's ceilings at once.

**Not P1's file record, either.** Text is per (content version × extractor × configuration), not per file: a text-layer pass and an OCR pass over the same PDF produce two different texts, and §8.2 requires both remain available.

**RAW-1 is the anchor for every citation check in the system** (§3.6, §4.8, §6.10, §7.9): *"For any observation with a `text_span`, `raw_value` is byte-for-byte the substring of the stored text unit at that span."* It is machine-checkable, and this module is where it is checked.

**Rule 10 compares the address, not the record.** Segment-kind rule 2: *"A kind with an index is addressed by its index; its label is descriptive only and never appears in the locator."* So a unit at `slide=6` satisfies an observation whose innermost segment is `Segment("slide", 6, label="Deadlines")` — the two are one address, and `(run_id, unit_locator)` is the key `text_units` is stored under and the key `store.text_unit_at` looks up. Comparing the `Segment` records instead would reject every conforming observation that carries a heading's text, a sheet's name or a slide's title, which is most of them. *(Caught by Task 16's fixture 13, which is exactly that case.)*

**Why the check needs no unit conversion.** D4 counts Unicode scalar values, and a Python `str` is already a sequence of code points — so `text[start:end]` *is* the D4 unit and there is no conversion anywhere in this package. That is exactly why D4 chose code points: the same offsets hold for CJK (§2.7's requirement) and for an astral-plane emoji, where a UTF-16 count would differ by one per character and a byte count by two or three.

**Rule 3 is the reason context is stored beside the value, not around it** (D9): *"`context_before` / `context_after` are drawn from the surrounding document text and are not required to lie inside the unit."* A heading at the top of page 4 has context that came from page 3. Storing context as offsets would have made that unrepresentable, and §8.4 could not then redact a value while keeping its context.

**Truncation is never silent** (§8.6, rule 5). A cut unit sets `truncated: true` and `length` is the *stored* length. An observation whose span lies inside the stored prefix stays valid; one whose span lies beyond it *is not written* — and if one is, `check_span_anchor` says so rather than returning a short string.

**These rows never leave the machine** (rule 6, §8.4): *"Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS… should remain local."* §4.4's *"short evidence excerpts"* are **cut from** these rows by P8 under P7's gate; the rows themselves are never sent to a model. P4 enforces this by owning no egress: `evidence_shape` opens no socket and has no serializer aimed at a model. Task 19 asserts the package imports nothing that could.

- [ ] **Step 1: Write the failing test**

```python
# tests/p4/test_p4_text_units.py
import pytest

from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.text_units import (
    MalformedTextUnit, SpanAnchorError, TEXT_UNIT_FIELDS, TextUnit, check_span_anchor,
    raw_value_at, text_unit_from_mapping,
)

PAGE_ONE = "Syllabus — BUSIB 4300 — Spring 2026"


def _observation(**overrides):
    payload = dict(
        file_id="f1", content_hash="sha256:abc", extractor_name="pdf.text",
        extractor_version="3.1.0", source_type="text_document",
        raw_value="BUSIB 4300",
        location=Location("heading", (Segment("page", 1),),
                          text_span=TextSpan(11, 21)),
        occurrence_count=1, observed_at="2026-08-19T14:03:22+00:00",
        reliability="possible", run_id="r1",
    )
    payload.update(overrides)
    return Observation(**payload)


def test_the_record_carries_the_specs_six_fields_in_order():
    assert TEXT_UNIT_FIELDS == (
        "run_id", "container_path", "unit_locator", "text", "length", "truncated")


def test_a_per_page_unit_addresses_itself_with_the_same_vocabulary_the_observation_uses():
    # §2.2 "complete text by page": one row per page.
    unit = TextUnit(run_id="r1", container_path=(Segment("page", 4),), text="…")
    assert unit.unit_locator == "page=4"
    assert unit.container_path == (Segment("page", 4),)


def test_a_whole_file_unit_has_an_empty_path_and_an_empty_locator():
    # §2.4: the full text of a text-bearing file is one row, container_path: [].
    unit = TextUnit(run_id="r1", container_path=(), text="hello")
    assert unit.container_path == ()
    assert unit.unit_locator == ""


def test_a_per_region_ocr_unit_nests_page_and_region():
    # §2.7 "raw recognized text": one row per OCR page or region.
    unit = TextUnit(run_id="r1",
                    container_path=(Segment("page", 4), Segment("region", 2)),
                    text="Your Columbia University")
    assert unit.unit_locator == "page=4/region=2"


def test_length_is_the_stored_length_in_code_points():
    # D4, and rule 5: "`length` is the stored length".
    unit = TextUnit(run_id="r1", container_path=(), text=PAGE_ONE)
    assert unit.length == len(PAGE_ONE)


def test_raw_1_holds_on_the_walking_skeletons_own_fixture():
    # RAW-1: raw_value is byte-for-byte the substring of the stored text unit at that
    # span. This is the anchor for every citation check in §3.6, §4.8, §6.10, §7.9.
    unit = TextUnit(run_id="r1", container_path=(Segment("page", 1),), text=PAGE_ONE)
    observation = _observation()
    assert raw_value_at(unit, observation.location.text_span) == "BUSIB 4300"
    check_span_anchor(observation, unit)


def test_raw_1_holds_on_cjk_where_a_byte_offset_would_not():
    # Done-means 4, and §2.7's CJK requirement. Code points, not bytes.
    text = "課程 BUSIB 4300 春季"
    start, end = 3, 13
    assert text[start:end] == "BUSIB 4300"
    assert len(text.encode("utf-8")) != len(text)      # bytes would disagree
    unit = TextUnit(run_id="r1", container_path=(Segment("page", 1),), text=text)
    check_span_anchor(_observation(location=Location(
        "heading", (Segment("page", 1),), text_span=TextSpan(start, end))), unit)


def test_raw_1_holds_on_an_astral_emoji_where_a_utf_16_offset_would_not():
    # Done-means 4. An astral-plane emoji is ONE code point and TWO UTF-16 units, so
    # a UTF-16 offset would land one short from here on.
    text = "\U0001F600 BUSIB 4300"
    assert len(text) == 12 and len(text.encode("utf-16-le")) // 2 == 13
    unit = TextUnit(run_id="r1", container_path=(Segment("page", 1),), text=text)
    check_span_anchor(_observation(location=Location(
        "heading", (Segment("page", 1),), text_span=TextSpan(2, 12))), unit)


def test_the_anchor_fails_when_the_span_names_different_text():
    unit = TextUnit(run_id="r1", container_path=(Segment("page", 1),), text=PAGE_ONE)
    with pytest.raises(SpanAnchorError):
        check_span_anchor(_observation(raw_value="BUSIB 4301"), unit)


def test_the_anchor_fails_when_the_unit_belongs_to_another_run():
    # Rule 4: text is per run, not per file. A text-layer pass and an OCR pass over
    # the same PDF produce two different texts under two run_ids (§8.2).
    other = TextUnit(run_id="r2", container_path=(Segment("page", 1),), text=PAGE_ONE)
    with pytest.raises(SpanAnchorError):
        check_span_anchor(_observation(), other)


def test_the_anchor_fails_when_the_units_path_is_not_the_observations_path():
    # Rule 10: the unit's container_path must EQUAL the observation's.
    coarser = TextUnit(run_id="r1", container_path=(), text=PAGE_ONE)
    with pytest.raises(SpanAnchorError):
        check_span_anchor(_observation(), coarser)


def test_the_anchor_refuses_an_observation_with_no_span():
    # Rule 10 is scoped to a non-null text_span; a metadata observation has none and
    # is not a rule-10 case at all.
    metadata = _observation(
        location=Location("metadata", (Segment("field", label="Producer"),)),
        raw_value="python-docx", reliability="direct")
    unit = TextUnit(run_id="r1", container_path=(Segment("page", 1),), text=PAGE_ONE)
    with pytest.raises(SpanAnchorError):
        check_span_anchor(metadata, unit)


def test_a_span_beyond_a_truncated_prefix_fails_rather_than_returning_short_text():
    # Rule 5: "an observation whose span lies beyond it is not written." If one is,
    # the anchor says so -- §8.6 forbids a silent truncation that removes evidence.
    cut = TextUnit(run_id="r1", container_path=(Segment("page", 1),),
                   text=PAGE_ONE[:15], truncated=True)
    assert cut.truncated is True
    assert cut.length == 15
    with pytest.raises(SpanAnchorError):
        check_span_anchor(_observation(), cut)


def test_a_span_inside_a_truncated_prefix_is_still_valid():
    # Rule 5: "A truncated unit invalidates no observation whose span lies inside the
    # stored prefix."
    cut = TextUnit(run_id="r1", container_path=(Segment("page", 1),),
                   text=PAGE_ONE[:21], truncated=True)
    check_span_anchor(_observation(), cut)


def test_context_may_cross_the_unit_boundary():
    # Rule 3, and D9's reason for storing context beside raw_value rather than as
    # offsets: a heading at the top of page 4 has context that came from page 3.
    unit = TextUnit(run_id="r1", container_path=(Segment("page", 4),),
                    text="BUSIB 4300 Syllabus")
    observation = _observation(
        location=Location("heading", (Segment("page", 4),), text_span=TextSpan(0, 10)),
        context_before="…continued from page 3. ", context_after=" — Spring 2026")
    check_span_anchor(observation, unit)
    assert observation.context_before not in unit.text
    assert observation.context_after not in unit.text


def test_truncated_defaults_to_false_and_is_always_a_bool():
    assert TextUnit(run_id="r1", container_path=(), text="x").truncated is False
    with pytest.raises(MalformedTextUnit):
        TextUnit(run_id="r1", container_path=(), text="x", truncated=None)


def test_an_empty_unit_is_well_formed_because_a_page_may_carry_no_text():
    # §2.2 requires complete text by page; a blank page is a page.
    unit = TextUnit(run_id="r1", container_path=(Segment("page", 9),), text="")
    assert unit.length == 0


def test_the_mapping_form_round_trips():
    unit = TextUnit(run_id="r1", container_path=(Segment("page", 4), Segment("region", 2)),
                    text="Your Columbia University", truncated=False)
    mapping = unit.to_mapping()
    assert list(mapping) == list(TEXT_UNIT_FIELDS)
    assert mapping["unit_locator"] == "page=4/region=2"
    assert mapping["container_path"] == [{"kind": "page", "index": 4},
                                         {"kind": "region", "index": 2}]
    assert text_unit_from_mapping(mapping) == unit


def test_the_mapping_form_rejects_a_field_the_record_does_not_publish():
    mapping = TextUnit(run_id="r1", container_path=(), text="x").to_mapping()
    for forbidden in ("file_id", "handling_class", "plan_version_id", "sent_to_model"):
        with pytest.raises(MalformedTextUnit):
            text_unit_from_mapping({**mapping, forbidden: "x"})


def test_a_stored_unit_locator_that_does_not_match_its_path_is_rejected():
    mapping = TextUnit(run_id="r1", container_path=(Segment("page", 4),),
                       text="x").to_mapping()
    with pytest.raises(MalformedTextUnit):
        text_unit_from_mapping({**mapping, "unit_locator": "page=9"})


def test_a_text_unit_is_frozen():
    unit = TextUnit(run_id="r1", container_path=(), text="x")
    with pytest.raises(Exception):
        unit.text = "y"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p4/test_p4_text_units.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'evidence_shape.text_units'`

- [ ] **Step 3: Write the implementation**

```python
# src/evidence_shape/text_units.py
"""Record 3 -- `text_units`, the home for the bulk text (D12, G1).

§2.2 requires "complete text by page", §2.4 the full text of a text-bearing file,
§2.7 "raw recognized text". None of those is a LOCATED VALUE, so none is an
observation -- yet a `text_span` is defined as an offset into a stored, addressable
text unit, so the unit must exist and must be addressed by the same `container_path`
vocabulary the observation uses. P4 owns the span semantics, so P4 owns the unit.

Text is per RUN, not per file: a text-layer pass and an OCR pass over the same PDF
produce two different texts under two run_ids, and §8.2 requires both remain
available. Superseding a run never rewrites or deletes the earlier run's units.

RAW-1, checked here, is the anchor for every citation check in §3.6, §4.8, §6.10 and
§7.9: `raw_value` is byte-for-byte the substring of the stored text at that span.
Offsets are Unicode scalar values (D4) and a Python `str` is already a sequence of
code points, so there is no conversion in this module -- which is the property D4
was chosen for, and which holds for CJK (§2.7) and astral-plane characters alike.

These rows are always local (§8.4). §4.4's "short evidence excerpts" are cut FROM
them by P8 under P7's gate; the rows themselves never leave the machine.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from evidence_shape.location import Segment, TextSpan
from evidence_shape.locator import serialize_container_path
from evidence_shape.observation import Observation

#: The SPEC's Record 3, in the SPEC's order.
TEXT_UNIT_FIELDS: tuple[str, ...] = (
    "run_id", "container_path", "unit_locator", "text", "length", "truncated",
)


class MalformedTextUnit(ValueError):
    """A non-conforming text unit. P4 fails it rather than coercing it."""


class SpanAnchorError(ValueError):
    """RAW-1 or rule 10 does not hold between an observation and a unit."""


@dataclass(frozen=True, slots=True)
class TextUnit:
    """One addressable text unit an extraction run emitted."""

    run_id: str
    container_path: tuple[Segment, ...]
    text: str
    truncated: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.run_id, str) or not self.run_id:
            raise MalformedTextUnit("run_id is a non-empty string")
        if not isinstance(self.container_path, tuple):
            if isinstance(self.container_path, (str, bytes)) or not isinstance(
                    self.container_path, Iterable):
                raise MalformedTextUnit("container_path is a sequence of Segments")
            object.__setattr__(self, "container_path", tuple(self.container_path))
        for segment in self.container_path:
            if not isinstance(segment, Segment):
                raise MalformedTextUnit(
                    f"container_path holds Segments, not {segment!r}")
        if not isinstance(self.text, str):
            raise MalformedTextUnit("text is a string, exactly as extracted")
        if type(self.truncated) is not bool:
            raise MalformedTextUnit(
                "truncated is a bool and is never absent (§8.6: never silently)")

    @property
    def unit_locator(self) -> str:
        """The canonical serialization of `container_path`. No zone: a unit is an
        address, not a located value."""
        return serialize_container_path(self.container_path)

    @property
    def length(self) -> int:
        """The STORED length, in Unicode scalar values (D4, rule 5)."""
        return len(self.text)

    def to_mapping(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "container_path": [
                {"kind": segment.kind,
                 **({"index": segment.index} if segment.index is not None else {}),
                 **({"label": segment.label} if segment.label is not None else {})}
                for segment in self.container_path],
            "unit_locator": self.unit_locator,
            "text": self.text,
            "length": self.length,
            "truncated": self.truncated,
        }


def text_unit_from_mapping(mapping: Mapping[str, object]) -> TextUnit:
    missing = [name for name in TEXT_UNIT_FIELDS
               if name not in ("unit_locator", "length") and name not in mapping]
    if missing:
        raise MalformedTextUnit(f"missing text-unit fields: {missing}")
    unknown = sorted(set(mapping) - set(TEXT_UNIT_FIELDS))
    if unknown:
        raise MalformedTextUnit(f"{unknown} are not fields of the text-unit record")
    path = mapping["container_path"]
    unit = TextUnit(
        run_id=mapping["run_id"],
        container_path=path if isinstance(path, tuple) else tuple(
            Segment(segment["kind"], segment.get("index"), segment.get("label"))
            for segment in path),
        text=mapping["text"],
        truncated=mapping["truncated"],
    )
    stated_locator = mapping.get("unit_locator")
    if stated_locator is not None and stated_locator != unit.unit_locator:
        raise MalformedTextUnit(
            f"unit_locator {stated_locator!r} does not serialize from this "
            "container_path; the unit and the observations that point into it are "
            "addressed identically or not at all")
    stated_length = mapping.get("length")
    if stated_length is not None and stated_length != unit.length:
        raise MalformedTextUnit(
            f"length {stated_length!r} is not the stored length {unit.length}")
    return unit


def raw_value_at(unit: TextUnit, text_span: TextSpan) -> str:
    """The substring RAW-1 compares against, in code points (D4)."""
    return unit.text[text_span.start:text_span.end]


def check_span_anchor(observation: Observation, unit: TextUnit) -> None:
    """Conformance rule 10 and RAW-1, together. Raises; never returns a repair."""
    text_span = observation.location.text_span
    if text_span is None:
        raise SpanAnchorError(
            "rule 10 applies to an observation with a non-null text_span; this one "
            "has none and needs no unit")
    if unit.run_id != observation.run_id:
        raise SpanAnchorError(
            f"the unit belongs to run {unit.run_id!r} and the observation to "
            f"{observation.run_id!r}; text is per run, not per file (rule 4)")
    address = serialize_container_path(observation.location.container_path)
    if unit.unit_locator != address:
        raise SpanAnchorError(
            f"the unit is addressed {unit.unit_locator!r} and the observation's span "
            f"is into {address!r}; rule 10 requires they be equal. The comparison is "
            "on the ADDRESS and not on the record: segment-kind rule 2 makes a label "
            "descriptive only, so a labelled `slide=6` and a bare `slide=6` are one "
            "address -- and `(run_id, unit_locator)` is the key `text_units` is "
            "stored under")
    if text_span.end > unit.length:
        raise SpanAnchorError(
            f"the span ends at {text_span.end} and the stored unit is "
            f"{unit.length} long"
            + (" -- the unit is truncated, and an observation whose span lies beyond "
               "the stored prefix is not written (rule 5)" if unit.truncated else ""))
    found = raw_value_at(unit, text_span)
    if found != observation.raw_value:
        raise SpanAnchorError(
            f"RAW-1: raw_value {observation.raw_value!r} is not the substring at "
            f"{text_span.start}-{text_span.end}, which is {found!r}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p4/test_p4_text_units.py -v`
Expected: PASS — 21 passed

- [ ] **Step 5: Commit**

```bash
git add src/evidence_shape/text_units.py tests/p4/test_p4_text_units.py
git commit -m "feat(P4): Record 3 — text_units, and RAW-1 in code points"
```

---

### Task 9: The three tables, inside P1's database, with P1's file untouched

**Files:**
- Create: `src/evidence_shape/schema.py`
- Modify: `tests/p4/conftest.py` — add the `p4_conn` fixture
- Test: `tests/p4/test_p4_schema.py`

**Interfaces:**
- Consumes: `database_agent.db.create_schema`; `evidence_shape.observation.OBSERVATION_ROW_FIELDS`; `evidence_shape.runs.RUN_FIELDS`; `evidence_shape.text_units.TEXT_UNIT_FIELDS`.
- Produces: `EXTRACTION_RUNS_DDL: str`, `EVIDENCE_DDL: str`, `TEXT_UNITS_DDL: str`, `SUPERSEDE_ADAPTER_COLUMN: str`, `create_evidence_schema(conn) -> None`.

**§0: one local SQLite database, and each part owns its own tables within it.** P4 creates three and touches none of P1's. `src/database_agent/db.py` is not modified, `pyproject.toml` is not modified, and `tests/conftest.py` is not modified.

**The one column that is not a published field.** P1's `mark_superseded` and `chain` are `… WHERE record_id = ?`; P4's published primary key is `observation_id`. Renaming either breaks a published contract, and writing a second supersede implementation would put one concept under two names — the defect this project has paid for most often. The resolution is a SQLite **virtual generated column**:

```sql
record_id TEXT GENERATED ALWAYS AS (observation_id) VIRTUAL
```

It stores nothing, cannot diverge from `observation_id`, and does not appear in `PRAGMA table_info` — so the test below can assert that `table_info(evidence)` is **exactly** `OBSERVATION_ROW_FIELDS`, in order, while `table_xinfo` shows the adapter as the single hidden column with its reason. P1's tested supersede functions are then reused verbatim.

**Three enforcements in SQL, each one a quoted requirement, and no fourth.**

1. **No deletion.** §8.2 supersedes rather than overwrites; §8.7 requires that *"Rejected groups, rejected destination matches, rejected labels, and rejected residual recommendations must be stored with the evidence that produced them. Otherwise the system will repeatedly resurface the same attractive but incorrect grouping."* A deleted observation decays every negative example that points at it.
2. **RAW-2, as a trigger over exactly the SPEC's seven never-overwritten fields** — `raw_value`, `location`, `occurrence_count`, `observed_at`, `extractor_name`, `extractor_version`, `run_id`. The three supersede columns are deliberately outside the trigger, because supersession is the one legal write to an existing row. Seven is the SPEC's list; an eighth would be P4 widening its own contract.
3. **A text unit is never rewritten or deleted** (rule 4: *"Superseding a run never rewrites or deletes the earlier run's units"*; rule 7: *"superseded, never removed"*). The whole row is covered, because nothing about a stored unit is ever edited.

**The foreign keys run one way only.** `evidence.run_id` and `text_units.run_id` reference `extraction_runs`; nothing references P1's `files`. Two reasons, both load-bearing: **Open question 2** is unsettled — whether an observation is owned by the content hash or by the file record — and a foreign key to `files` would answer it in DDL; and P4 must be buildable and testable with no `files` row in existence, which is what lets P6 be built entirely against P4's fixtures with no extractor and no scan. `file_id` and `content_hash` are both `NOT NULL` on both records, which is what §2.8 requires and is deliberately as far as P4 goes.

**The cache-key index is §3.4's tuple.** `(content_hash, extractor_name, extractor_version, config_fingerprint)` — *"Each extraction result is tied to the content hash and the exact process that produced it."* It is an index, not a unique constraint: a re-run at the same key is legal and produces a second row that supersedes the first (§8.2), and a unique constraint would make that impossible.

**No index on `observation_key` is unique**, for the same reason MINOR 8 gives: two extractor versions produce two rows carrying one key, and that is the whole mechanism §8.5's diff runs on.

- [ ] **Step 1: Write the failing test**

```python
# tests/p4/test_p4_schema.py
import pytest

from database_agent.db import create_schema
from database_agent.supersede import chain, mark_superseded

from evidence_shape.observation import OBSERVATION_ROW_FIELDS
from evidence_shape.runs import RUN_FIELDS
from evidence_shape.schema import SUPERSEDE_ADAPTER_COLUMN, create_evidence_schema
from evidence_shape.text_units import TEXT_UNIT_FIELDS

P1_TABLES = {"files", "events", "learning_resets", "budget_ceilings", "vector_arrays",
             "scan_resource_usage"}


def _columns(conn, table):
    return [row["name"] for row in conn.execute(f"PRAGMA table_info({table})")]


def _insert_run(conn, run_id="r1", **overrides):
    values = dict(run_id=run_id, file_id="f1", content_hash="sha256:abc",
                  extractor_name="pdf.text", extractor_version="3.1.0",
                  source_type="text_document", analysis_tier="native", config="{}",
                  config_fingerprint="sha256:cfg", completeness="complete",
                  coverage=None, observation_count=0, started_at="t0",
                  finished_at="t1", failure_reason=None)
    values.update(overrides)
    conn.execute(
        f"INSERT INTO extraction_runs ({','.join(values)}) "
        f"VALUES ({','.join('?' * len(values))})", list(values.values()))


def _insert_observation(conn, observation_id, run_id="r1", **overrides):
    values = dict(observation_id=observation_id, observation_key="sha256:k",
                  file_id="f1", content_hash="sha256:abc", extractor_name="pdf.text",
                  extractor_version="3.1.0", source_type="text_document",
                  raw_value="BUSIB 4300", normalized_value=None,
                  location='{"zone":"heading"}', context_before=None,
                  context_after=None, context_truncated=0, occurrence_count=3,
                  observed_at="t0", reliability="possible", run_id=run_id,
                  confidence=None, signal_tier=None, supersedes=None,
                  superseded_by=None, supersede_reason=None)
    values.update(overrides)
    conn.execute(
        f"INSERT INTO evidence ({','.join(values)}) "
        f"VALUES ({','.join('?' * len(values))})", list(values.values()))


def test_the_three_tables_exist_and_p1s_are_untouched(p4_conn):
    tables = {row["name"] for row in p4_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert {"evidence", "extraction_runs", "text_units"} <= tables
    assert P1_TABLES <= tables


def test_creating_the_schema_twice_is_idempotent(p4_conn):
    create_evidence_schema(p4_conn)
    create_evidence_schema(p4_conn)
    assert len(_columns(p4_conn, "evidence")) == len(OBSERVATION_ROW_FIELDS)


def test_p1s_schema_function_still_runs_beside_it(p4_conn):
    create_schema(p4_conn)
    assert _columns(p4_conn, "files")


def test_the_evidence_columns_are_exactly_the_published_row_fields_in_order(p4_conn):
    assert _columns(p4_conn, "evidence") == list(OBSERVATION_ROW_FIELDS)


def test_the_run_and_unit_columns_are_exactly_their_published_fields_in_order(p4_conn):
    assert _columns(p4_conn, "extraction_runs") == list(RUN_FIELDS)
    assert _columns(p4_conn, "text_units") == list(TEXT_UNIT_FIELDS)


def test_the_one_adapter_column_is_hidden_generated_and_named(p4_conn):
    # It exists so P1's mark_superseded/chain, which key on `record_id`, work against
    # a table whose published primary key is `observation_id`. It stores nothing.
    assert SUPERSEDE_ADAPTER_COLUMN == "record_id"
    assert SUPERSEDE_ADAPTER_COLUMN not in _columns(p4_conn, "evidence")
    extended = {row["name"]: row["hidden"]
                for row in p4_conn.execute("PRAGMA table_xinfo(evidence)")}
    assert extended[SUPERSEDE_ADAPTER_COLUMN] == 2          # virtual generated
    assert set(extended) - set(OBSERVATION_ROW_FIELDS) == {SUPERSEDE_ADAPTER_COLUMN}


def test_p1s_supersede_functions_work_unchanged_against_the_evidence_table(p4_conn):
    _insert_run(p4_conn)
    _insert_observation(p4_conn, "o1")
    _insert_observation(p4_conn, "o2", extractor_version="4.0.0")
    mark_superseded(p4_conn, "evidence", old_id="o1", new_id="o2",
                    reason="a later improved OCR engine recovered the name")

    links = chain(p4_conn, "evidence", "o1")
    assert [row["observation_id"] for row in links] == ["o1", "o2"]
    assert links[0]["superseded_by"] == "o2"
    assert links[0]["supersede_reason"].startswith("a later improved")
    assert links[1]["supersedes"] == "o1"
    assert links[0]["raw_value"] == "BUSIB 4300"           # RAW-2: untouched


def test_an_observation_can_never_be_deleted(p4_conn):
    # §8.7: rejected proposals "must be stored with the evidence that produced them".
    _insert_run(p4_conn)
    _insert_observation(p4_conn, "o1")
    with pytest.raises(Exception):
        p4_conn.execute("DELETE FROM evidence WHERE observation_id = 'o1'")
    assert p4_conn.execute("SELECT count(*) c FROM evidence").fetchone()["c"] == 1


def test_the_seven_never_overwritten_fields_cannot_be_updated(p4_conn):
    # SPEC, Cross-cutting answers -> Provenance, "Never overwritten": raw_value,
    # location, occurrence_count, observed_at, extractor_name, extractor_version,
    # run_id. Improvement is insert + supersede, never update.
    _insert_run(p4_conn)
    _insert_observation(p4_conn, "o1")
    for column, value in (("raw_value", "BUSIB 4301"), ("location", "{}"),
                          ("occurrence_count", 9), ("observed_at", "t9"),
                          ("extractor_name", "ocr.apple_vision"),
                          ("extractor_version", "4.0.0"), ("run_id", "r2")):
        with pytest.raises(Exception):
            p4_conn.execute(
                f"UPDATE evidence SET {column} = ? WHERE observation_id = 'o1'",
                (value,))


def test_the_supersede_columns_are_outside_that_trigger_on_purpose(p4_conn):
    # Supersession is the one legal write to an existing row (§8.2).
    _insert_run(p4_conn)
    _insert_observation(p4_conn, "o1")
    p4_conn.execute("UPDATE evidence SET superseded_by = 'o2', supersede_reason = 'x' "
                    "WHERE observation_id = 'o1'")
    assert p4_conn.execute(
        "SELECT superseded_by s FROM evidence").fetchone()["s"] == "o2"


def test_a_text_unit_is_never_rewritten_or_deleted(p4_conn):
    # Rule 4: "Superseding a run never rewrites or deletes the earlier run's units."
    _insert_run(p4_conn)
    p4_conn.execute("INSERT INTO text_units (run_id, container_path, unit_locator, "
                    "text, length, truncated) VALUES ('r1', '[]', '', 'hello', 5, 0)")
    with pytest.raises(Exception):
        p4_conn.execute("UPDATE text_units SET text = 'goodbye'")
    with pytest.raises(Exception):
        p4_conn.execute("DELETE FROM text_units")


def test_a_run_is_never_deleted(p4_conn):
    _insert_run(p4_conn)
    with pytest.raises(Exception):
        p4_conn.execute("DELETE FROM extraction_runs WHERE run_id = 'r1'")


def test_an_observation_cannot_reference_a_run_that_does_not_exist(p4_conn):
    _insert_run(p4_conn)
    with pytest.raises(Exception):
        _insert_observation(p4_conn, "o9", run_id="missing")


def test_no_foreign_key_points_at_p1s_files_table(p4_conn):
    # Open question 2 -- whether an observation is owned by the content hash or by
    # the file record -- is unsettled, and a foreign key would answer it in DDL. P4
    # also has to be buildable with no `files` row, which is what lets P6 be built
    # entirely against P4's fixtures.
    for table in ("evidence", "extraction_runs", "text_units"):
        targets = {row["table"] for row in
                   p4_conn.execute(f"PRAGMA foreign_key_list({table})")}
        assert "files" not in targets
    _insert_run(p4_conn)
    _insert_observation(p4_conn, "o1", file_id="a-file-that-was-never-scanned")


def test_both_file_id_and_content_hash_are_required_on_both_records(p4_conn):
    # §2.8's field list contains both, and P4 carries both, which is what makes the
    # contract buildable either way once Open question 2 closes.
    for table in ("evidence", "extraction_runs"):
        required = {row["name"] for row in p4_conn.execute(f"PRAGMA table_info({table})")
                    if row["notnull"]}
        assert {"file_id", "content_hash"} <= required


def test_the_cache_key_index_is_3_4s_tuple_and_is_not_unique(p4_conn):
    # §3.4: content hash + the exact process that produced it. Not unique, because a
    # re-run at the same key is legal and supersedes rather than replaces (§8.2).
    indexes = {row["name"]: row["unique"]
               for row in p4_conn.execute("PRAGMA index_list(extraction_runs)")}
    cache = [name for name in indexes if "cache_key" in name]
    assert cache, indexes
    assert indexes[cache[0]] == 0
    columns = [row["name"] for row in
               p4_conn.execute(f"PRAGMA index_info({cache[0]})")]
    assert columns == ["content_hash", "extractor_name", "extractor_version",
                       "config_fingerprint"]


def test_two_extractor_versions_may_share_one_observation_key(p4_conn):
    # MINOR 8's mechanism, at the storage layer: a unique index on observation_key
    # would make §8.5's cross-version diff impossible.
    _insert_run(p4_conn)
    _insert_observation(p4_conn, "o1", observation_key="sha256:same")
    _insert_observation(p4_conn, "o2", observation_key="sha256:same",
                        extractor_version="4.0.0")
    assert p4_conn.execute(
        "SELECT count(*) c FROM evidence WHERE observation_key = 'sha256:same'"
    ).fetchone()["c"] == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p4/test_p4_schema.py -v`
Expected: FAIL with `fixture 'p4_conn' not found` / `ModuleNotFoundError: No module named 'evidence_shape.schema'`

- [ ] **Step 3: Write `schema.py`**

```python
# src/evidence_shape/schema.py
"""P4's three tables. They live inside P1's single local SQLite database (§0: "Each
part owns its own tables within it"); P1 owns the handle, the transaction boundary,
`files` and `events`, and P4 creates none of them and modifies no P1 file.

One column is not a published field. P1's `mark_superseded` and `chain` are
`... WHERE record_id = ?`, and P4's published primary key is `observation_id`.
`record_id` is a VIRTUAL generated projection of it: it stores nothing, cannot
diverge, does not appear in `PRAGMA table_info`, and lets P1's tested supersede
functions be reused verbatim instead of written a second time under a second name.

The foreign keys run one way. Nothing references P1's `files`: Open question 2 --
whether an observation is owned by the content hash or by the file record -- is
unsettled, and a foreign key would answer it in DDL. P4 must also be buildable and
testable with no `files` row in existence, which is what lets P6 be built entirely
against P4's fixtures with no extractor and no scan.
"""
from __future__ import annotations

import sqlite3

#: The one column that is not a published observation field. See the module docstring.
SUPERSEDE_ADAPTER_COLUMN = "record_id"

EXTRACTION_RUNS_DDL = """
CREATE TABLE IF NOT EXISTS extraction_runs (
    run_id             TEXT PRIMARY KEY,
    file_id            TEXT NOT NULL,
    content_hash       TEXT NOT NULL,
    extractor_name     TEXT NOT NULL,
    extractor_version  TEXT NOT NULL,
    source_type        TEXT NOT NULL,
    analysis_tier      TEXT NOT NULL,
    config             TEXT NOT NULL,
    config_fingerprint TEXT NOT NULL,
    completeness       TEXT NOT NULL,
    coverage           TEXT,
    observation_count  INTEGER NOT NULL DEFAULT 0,
    started_at         TEXT NOT NULL,
    finished_at        TEXT,
    failure_reason     TEXT
);
-- §3.4: "the content hash and the exact process that produced it". Not unique: a
-- re-run at the same key is legal and supersedes rather than replaces (§8.2).
CREATE INDEX IF NOT EXISTS extraction_runs_cache_key
    ON extraction_runs (content_hash, extractor_name, extractor_version,
                        config_fingerprint);
CREATE INDEX IF NOT EXISTS extraction_runs_file ON extraction_runs (file_id);
CREATE TRIGGER IF NOT EXISTS extraction_runs_no_delete
BEFORE DELETE ON extraction_runs
BEGIN SELECT RAISE(ABORT, 'a run is superseded by a later run, never removed (§8.2)'); END;
"""

EVIDENCE_DDL = """
CREATE TABLE IF NOT EXISTS evidence (
    observation_id     TEXT PRIMARY KEY,
    record_id          TEXT GENERATED ALWAYS AS (observation_id) VIRTUAL,
    observation_key    TEXT NOT NULL,
    file_id            TEXT NOT NULL,
    content_hash       TEXT NOT NULL,
    extractor_name     TEXT NOT NULL,
    extractor_version  TEXT NOT NULL,
    source_type        TEXT NOT NULL,
    raw_value          TEXT NOT NULL,
    normalized_value   TEXT,
    location           TEXT NOT NULL,
    context_before     TEXT,
    context_after      TEXT,
    context_truncated  INTEGER NOT NULL,
    occurrence_count   INTEGER NOT NULL,
    observed_at        TEXT NOT NULL,
    reliability        TEXT NOT NULL,
    run_id             TEXT NOT NULL REFERENCES extraction_runs (run_id),
    confidence         REAL,
    signal_tier        INTEGER,
    supersedes         TEXT,
    superseded_by      TEXT,
    supersede_reason   TEXT
);
-- Deliberately NOT unique (MINOR 8): two extractor versions carry one key, which is
-- the mechanism §8.5's cross-version diff runs on.
CREATE INDEX IF NOT EXISTS evidence_key ON evidence (observation_key);
CREATE INDEX IF NOT EXISTS evidence_run ON evidence (run_id);
CREATE INDEX IF NOT EXISTS evidence_file ON evidence (file_id);
CREATE INDEX IF NOT EXISTS evidence_content ON evidence (content_hash);
CREATE TRIGGER IF NOT EXISTS evidence_no_delete
BEFORE DELETE ON evidence
-- RAISE takes one string literal, so the reason is short here and long above:
-- §8.7 requires a rejected proposal to keep the evidence that produced it.
BEGIN SELECT RAISE(ABORT, 'observations are superseded, never removed (§8.2, §8.7)'); END;
-- RAW-2, over exactly the SPEC's seven never-overwritten fields. The three supersede
-- columns are outside it: supersession is the one legal write to an existing row.
CREATE TRIGGER IF NOT EXISTS evidence_never_overwritten
BEFORE UPDATE OF raw_value, location, occurrence_count, observed_at, extractor_name,
                 extractor_version, run_id ON evidence
BEGIN SELECT RAISE(ABORT, 'RAW-2: never updated; a better extractor emits a new observation and a new run (§8.2)'); END;
"""

TEXT_UNITS_DDL = """
CREATE TABLE IF NOT EXISTS text_units (
    run_id         TEXT NOT NULL REFERENCES extraction_runs (run_id),
    container_path TEXT NOT NULL,
    unit_locator   TEXT NOT NULL,
    text           TEXT NOT NULL,
    length         INTEGER NOT NULL,
    truncated      INTEGER NOT NULL,
    -- Keyed by (run_id, container_path), in the canonical string form of that path.
    PRIMARY KEY (run_id, unit_locator)
);
CREATE TRIGGER IF NOT EXISTS text_units_no_delete
BEFORE DELETE ON text_units
BEGIN SELECT RAISE(ABORT, 'a text unit is superseded by a later run, never removed (rule 7, §8.2)'); END;
CREATE TRIGGER IF NOT EXISTS text_units_no_rewrite
BEFORE UPDATE ON text_units
BEGIN SELECT RAISE(ABORT, 'superseding a run never rewrites an earlier run''s units (rule 4, §8.2)'); END;
"""


def create_evidence_schema(conn: sqlite3.Connection) -> None:
    """Create every P4-owned table. Idempotent. P1's `create_schema` runs first."""
    conn.executescript(EXTRACTION_RUNS_DDL)
    conn.executescript(EVIDENCE_DDL)
    conn.executescript(TEXT_UNITS_DDL)
```

- [ ] **Step 4: Add the `p4_conn` fixture to `tests/p4/conftest.py`**

Append to the file created in Task 1, keeping what is already there:

```python
# tests/p4/conftest.py
import pytest

from database_agent.db import create_schema

from evidence_shape.schema import create_evidence_schema


@pytest.fixture()
def p4_conn(conn):
    """P1's database with P4's three tables added. `conn` is P1's root fixture and
    `tests/conftest.py` is not modified."""
    create_schema(conn)
    create_evidence_schema(conn)
    return conn
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/p4/test_p4_schema.py -v`
Expected: PASS — 17 passed

- [ ] **Step 6: Commit**

```bash
git add src/evidence_shape/schema.py tests/p4/conftest.py tests/p4/test_p4_schema.py
git commit -m "feat(P4): three tables in P1's database, superseded and never deleted"
```

---

### Task 10: The run writer, and the one §8.2 event a run appends

**Files:**
- Create: `src/evidence_shape/store.py`
- Test: `tests/p4/test_p4_store.py`

**Interfaces:**
- Consumes: `database_agent.events.append_event`; `evidence_shape.authorship` — `event_defaults`, `run_event_type`; `evidence_shape.canonical.canonical_json`; `evidence_shape.runs` — `RUN_FIELDS`, `ExtractionRun`, `run_from_mapping`.
- Produces: `new_id() -> str`, `record_run(conn, run) -> str`, `get_run(conn, run_id) -> ExtractionRun`, `runs_for_file(conn, file_id) -> list[ExtractionRun]`, `runs_for_content(conn, content_hash) -> list[ExtractionRun]`, `record_run_event(conn, run_id, *, author) -> int`.

**The order P5 writes in, and why it is two calls and not one.**

```text
run_id = record_run(conn, run)          # the row; no event
         record_text_unit(conn, unit)   # Task 11
         record_observation(conn, obs)  # Task 11
         record_run_event(conn, run_id, author="P5")
```

The SPEC's Provenance section says the event's *"structured explanation or evidence reference"* is *"`run_id` plus the `observation_key`s (or a `locator` for a single cited value)"* — and at the moment the run row is inserted there are no observations yet. So the event is appended last, when the keys exist, and `record_run_event` reads them from the rows rather than being handed them, which means the event and the database cannot disagree.

**P4 does not enforce "exactly one event per run."** Doing so would need state P4 does not publish — a column, or a fragile scan of `events.explanation`. The order above is documented and tested; it is not policed by inventing a field. Note also that P8, writing an `analysis_tier = llm` run, appends its own registered events (`model_call_issued`, `model_response_received`, …) in addition; P4 says nothing about those and forbids none of them.

**`component_version` on the event is the extractor's version.** §8.2's event record lists *"extractor or model version"* and P1's column is `component_version`; for a run, the run's own `extractor_version` is that value, so it is derived rather than passed in. `observed_at` is the run's `finished_at`, falling back to `started_at` for a run that never finished — §8.2's *"time of observation"* for an extraction is when the extraction happened, not when the row was written.

**`prompt_fingerprint`, `old_path`, `new_path` and `user_id` are absent, each for a stated reason.** The SPEC's Provenance section: *"Old and new paths do not apply; `prompt fingerprint` does not apply (P4 is model-free); `user identity` does not apply."* `user_id` is populated *"only on explicit user action"* (MINOR 10) and a run is not one.

**`config` and `coverage` are stored as canonical JSON.** One form per value, so §3.4's cache key and §8.5's diff compare bytes rather than dictionary iteration order.

- [ ] **Step 1: Write the failing test**

```python
# tests/p4/test_p4_store.py
import json

import pytest

from database_agent.events import RESERVED_EVENT_TYPES

from evidence_shape.authorship import UnauthoredEvent
from evidence_shape.runs import Coverage, ExtractionRun
from evidence_shape.store import (
    get_run, new_id, record_run, record_run_event, runs_for_content, runs_for_file,
)


def _run(**overrides):
    payload = dict(
        run_id="r1", file_id="f1", content_hash="sha256:abc",
        extractor_name="pdf.text", extractor_version="3.1.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at="2026-08-19T14:00:00+00:00",
        finished_at="2026-08-19T14:03:22+00:00",
    )
    payload.update(overrides)
    return ExtractionRun(**payload)


def _ocr_run(**overrides):
    return _run(run_id="r2", extractor_name="ocr.apple_vision",
                extractor_version="2.4.1", source_type="ocr", analysis_tier="ocr",
                config={"dpi": 200, "languages": ["en", "zh-Hans"],
                        "recognition": "accurate"},
                completeness="capped",
                coverage=Coverage("pages", 40, 312), **overrides)


def test_ids_are_unique(p4_conn):
    assert new_id() != new_id()


def test_a_run_round_trips_through_the_database(p4_conn):
    record_run(p4_conn, _ocr_run())
    stored = get_run(p4_conn, "r2")
    assert stored == _ocr_run()
    assert stored.config["languages"] == ["en", "zh-Hans"]
    assert stored.coverage == Coverage("pages", 40, 312)
    assert stored.config_fingerprint == _ocr_run().config_fingerprint


def test_the_config_is_stored_as_canonical_json(p4_conn):
    record_run(p4_conn, _ocr_run())
    raw = p4_conn.execute(
        "SELECT config FROM extraction_runs WHERE run_id = 'r2'").fetchone()["config"]
    assert raw == '{"dpi":200,"languages":["en","zh-Hans"],"recognition":"accurate"}'


def test_a_run_with_no_coverage_stores_null(p4_conn):
    record_run(p4_conn, _run())
    assert p4_conn.execute(
        "SELECT coverage FROM extraction_runs WHERE run_id = 'r1'"
    ).fetchone()["coverage"] is None
    assert get_run(p4_conn, "r1").coverage is None


def test_two_runs_over_one_file_are_two_rows(p4_conn):
    # B1: "An opaque image runs the image extractor and OCR, which is two rows -- one
    # may be `complete` while the other is `capped`."
    record_run(p4_conn, _run())
    record_run(p4_conn, _ocr_run())
    rows = runs_for_file(p4_conn, "f1")
    assert [row.run_id for row in rows] == ["r1", "r2"]
    assert {row.completeness for row in rows} == {"complete", "capped"}


def test_runs_are_findable_by_content_hash(p4_conn):
    # §2.1: "read each file once per content version"; §3.4 keys on the content hash.
    record_run(p4_conn, _run())
    record_run(p4_conn, _ocr_run())
    assert len(runs_for_content(p4_conn, "sha256:abc")) == 2
    assert runs_for_content(p4_conn, "sha256:other") == []


def test_an_unknown_run_is_a_key_error(p4_conn):
    with pytest.raises(KeyError):
        get_run(p4_conn, "nope")


def test_a_native_run_appends_8_2s_extraction_event(p4_conn):
    record_run(p4_conn, _run())
    event_id = record_run_event(p4_conn, "r1", author="P5")

    row = p4_conn.execute("SELECT * FROM events WHERE event_id = ?",
                          (event_id,)).fetchone()
    assert row["event_type"] == "extraction"
    assert row["event_type"] in RESERVED_EVENT_TYPES
    assert row["subsystem"] == "P5"
    assert row["component_version"] == "3.1.0"
    assert row["file_id"] == "f1"
    assert row["content_hash"] == "sha256:abc"
    assert row["observed_at"] == "2026-08-19T14:03:22+00:00"


def test_an_ocr_run_appends_8_2s_OCR_event_spelled_the_way_8_2_spells_it(p4_conn):
    # MINOR 2: "§8.2 spells it `OCR`." P1's writer validates against that
    # vocabulary, so a lowercase name would fail at runtime.
    record_run(p4_conn, _ocr_run())
    event_id = record_run_event(p4_conn, "r2", author="P5")
    assert p4_conn.execute("SELECT event_type FROM events WHERE event_id = ?",
                           (event_id,)).fetchone()["event_type"] == "OCR"


def test_an_llm_tier_run_appends_an_extraction_event_and_p4_forbids_p8_nothing_else(
        p4_conn):
    # I4: "P8 is the only writer of `llm` runs." P4 accepts the value and appends the
    # one event a run appends; P8's own five registered events are its business.
    record_run(p4_conn, _run(run_id="r3", analysis_tier="llm"))
    event_id = record_run_event(p4_conn, "r3", author="P8")
    row = p4_conn.execute("SELECT * FROM events WHERE event_id = ?",
                          (event_id,)).fetchone()
    assert row["event_type"] == "extraction"
    assert row["subsystem"] == "P8"


def test_the_event_carries_the_run_id_and_the_keys_of_that_runs_observations(p4_conn):
    # SPEC, Provenance: the reference is "`run_id` plus the `observation_key`s".
    record_run(p4_conn, _run())
    event_id = record_run_event(p4_conn, "r1", author="P5")
    explanation = json.loads(p4_conn.execute(
        "SELECT explanation FROM events WHERE event_id = ?",
        (event_id,)).fetchone()["explanation"])
    assert explanation["run_id"] == "r1"
    assert explanation["observation_keys"] == []      # none written yet


def test_the_caller_names_itself_and_p1_may_never_be_named(p4_conn):
    # M8: the acting part authors; P1 writes. P4 supplies no default author.
    record_run(p4_conn, _run())
    with pytest.raises(UnauthoredEvent):
        record_run_event(p4_conn, "r1", author="P1")
    with pytest.raises(UnauthoredEvent):
        record_run_event(p4_conn, "r1", author="")
    with pytest.raises(TypeError):
        record_run_event(p4_conn, "r1")


def test_the_event_carries_no_prompt_fingerprint_no_paths_and_no_user(p4_conn):
    # SPEC, Provenance: "Old and new paths do not apply; `prompt fingerprint` does
    # not apply (P4 is model-free); `user identity` does not apply." MINOR 10 keeps
    # user_id for explicit user actions, and a run is not one.
    record_run(p4_conn, _run())
    row = p4_conn.execute("SELECT * FROM events WHERE event_id = ?",
                          (record_run_event(p4_conn, "r1", author="P5"),)).fetchone()
    for absent in ("prompt_fingerprint", "old_path", "new_path", "user_id",
                   "correction_scope", "polarity"):
        assert row[absent] is None


def test_recording_a_run_appends_nothing_by_itself(p4_conn):
    # The event is the second call, because the keys it references do not exist yet.
    before = p4_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    record_run(p4_conn, _run())
    assert p4_conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == before
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p4/test_p4_store.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'evidence_shape.store'`

- [ ] **Step 3: Write the implementation**

```python
# src/evidence_shape/store.py
"""The writers and readers over P4's three tables.

P4 AUTHORS NO EVENT. `record_run_event` takes a required `author`, passes it into
`events.subsystem`, and refuses `P1` -- M8: "The acting part authors; P1 writes. P1
appends no event on its own initiative." P5 is the acting part for filesystem, native
and OCR runs; P8 for an `analysis_tier = llm` run.

The write order is: run row, then text units and observations, then the one §8.2
event. The event's evidence reference is "`run_id` plus the `observation_key`s", and
those keys do not exist until the observations are written -- so `record_run_event`
reads them from the rows rather than being handed them, and the event and the
database cannot disagree.
"""
from __future__ import annotations

import json
import sqlite3
import uuid

from database_agent.events import append_event

from evidence_shape.authorship import event_defaults, run_event_type
from evidence_shape.canonical import canonical_json
from evidence_shape.runs import RUN_FIELDS, ExtractionRun, run_from_mapping


def new_id() -> str:
    """A row identifier. Not the citation handle -- that is `observation_key` (M14)."""
    return str(uuid.uuid4())


def record_run(conn: sqlite3.Connection, run: ExtractionRun) -> str:
    """Insert one `extraction_runs` row. Appends no event; see `record_run_event`."""
    mapping = run.to_mapping()
    mapping["config"] = canonical_json(mapping["config"])
    mapping["coverage"] = (None if mapping["coverage"] is None
                           else canonical_json(mapping["coverage"]))
    conn.execute(
        f"INSERT INTO extraction_runs ({','.join(RUN_FIELDS)}) "
        f"VALUES ({','.join('?' * len(RUN_FIELDS))})",
        [mapping[name] for name in RUN_FIELDS],
    )
    return run.run_id


def _run_from_row(row: sqlite3.Row) -> ExtractionRun:
    mapping = {name: row[name] for name in RUN_FIELDS}
    mapping["config"] = json.loads(mapping["config"])
    mapping["coverage"] = (None if mapping["coverage"] is None
                           else json.loads(mapping["coverage"]))
    return run_from_mapping(mapping)


def get_run(conn: sqlite3.Connection, run_id: str) -> ExtractionRun:
    row = conn.execute("SELECT * FROM extraction_runs WHERE run_id = ?",
                       (run_id,)).fetchone()
    if row is None:
        raise KeyError(f"unknown run {run_id!r}")
    return _run_from_row(row)


def runs_for_file(conn: sqlite3.Connection, file_id: str) -> list[ExtractionRun]:
    return [_run_from_row(row) for row in conn.execute(
        "SELECT * FROM extraction_runs WHERE file_id = ? ORDER BY started_at, run_id",
        (file_id,))]


def runs_for_content(conn: sqlite3.Connection,
                     content_hash: str) -> list[ExtractionRun]:
    """§2.1: the engine reads each file once per content version; §3.4 keys on it."""
    return [_run_from_row(row) for row in conn.execute(
        "SELECT * FROM extraction_runs WHERE content_hash = ? "
        "ORDER BY started_at, run_id", (content_hash,))]


def record_run_event(conn: sqlite3.Connection, run_id: str, *, author: str) -> int:
    """The one §8.2 event a run appends: `extraction`, or `OCR` for an OCR run.

    `author` is the acting part and P4 supplies no default (M8). `component_version`
    is the run's own extractor version -- §8.2's "extractor or model version".
    """
    run = get_run(conn, run_id)
    keys = [row["observation_key"] for row in conn.execute(
        "SELECT observation_key FROM evidence WHERE run_id = ? ORDER BY observation_id",
        (run_id,))]
    return append_event(conn, **event_defaults(
        author=author,
        component_version=run.extractor_version,
        event_type=run_event_type(run.analysis_tier),
        file_id=run.file_id,
        content_hash=run.content_hash,
        observed_at=run.finished_at or run.started_at,
        explanation=canonical_json({"run_id": run_id, "observation_keys": keys}),
    ))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p4/test_p4_store.py -v`
Expected: PASS — 14 passed

- [ ] **Step 5: Commit**

```bash
git add src/evidence_shape/store.py tests/p4/test_p4_store.py
git commit -m "feat(P4): the run writer, and the §8.2 event its caller authors"
```

---

### Task 11: The observation and text-unit writers, and the read surface

**Files:**
- Modify: `src/evidence_shape/store.py` — add the observation and text-unit writers and readers
- Test: `tests/p4/test_p4_store.py` — extend

**Interfaces:**
- Consumes: `evidence_shape.location.Segment`; `evidence_shape.locator.serialize_container_path`; `evidence_shape.observation` — `OBSERVATION_FIELDS`, `OBSERVATION_ROW_FIELDS`, `Observation`, `observation_from_mapping`; `evidence_shape.text_units` — `TEXT_UNIT_FIELDS`, `TextUnit`, `text_unit_from_mapping`.
- Produces (`store.py`): `record_observation(conn, observation) -> str`, `get_observation(conn, observation_id) -> Observation`, `observation_row(conn, observation_id) -> sqlite3.Row`, `observations_for_run(conn, run_id) -> list[Observation]`, `observations_for_file(conn, file_id) -> list[Observation]`, `observations_by_key(conn, observation_key) -> list[Observation]`, `observation_keys_for_run(conn, run_id) -> list[str]`, `record_text_unit(conn, unit) -> None`, `text_units_for_run(conn, run_id) -> list[TextUnit]`, `text_unit_at(conn, run_id, container_path) -> TextUnit | None`, `unit_for_observation(conn, observation) -> TextUnit | None`.

**`observations_by_key` is the citation resolver, and §8.7 is why it exists.** *"`observation_key` is stable and permanently resolvable, so a negative example recorded today still resolves after an extractor upgrade."* It returns a **list**, not one row: two extractor versions produce two rows carrying one key, which is exactly what MINOR 8 arranged and what §8.5's cross-version diff reads.

**`observation_count` is maintained by the store.** It is a derived count, like `observation_key`, `config_fingerprint` and `TextUnit.length` — and a stored count that disagrees with the rows is a fact nobody downstream can use, least of all §8.6's progress line (G14). `record_observation` recomputes it from `count(*)` on that run. A caller that declared a count up front sees it become the truth as rows land; a run row inserted alone keeps the count it was handed, so a bundle carrying a wrong one stays visibly wrong rather than being repaired out of sight.

**`unit_for_observation` is conformance rule 10's lookup**, published here because P5 needs the same lookup its gate uses. It resolves `(run_id, container_path)` — the key D12 names — through `unit_locator`, which is that path's canonical serialization, so the unit and the observations that point into it are addressed identically.

**Booleans cross the SQLite boundary as integers**, and come back as booleans. `context_truncated` and `truncated` are `bool` on the record and `INTEGER` in the column; the readers convert, so no consumer ever compares `truncated == 1`.

- [ ] **Step 1: Write the failing test**

Append to `tests/p4/test_p4_store.py`:

```python
# tests/p4/test_p4_store.py
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.store import (
    get_observation, observation_row, observations_by_key, observations_for_file,
    observations_for_run, record_observation, record_text_unit, text_unit_at,
    text_units_for_run, unit_for_observation,
)
from evidence_shape.text_units import TextUnit

PAGE_ONE = "Syllabus — BUSIB 4300 — Spring 2026"


def _observation(**overrides):
    payload = dict(
        file_id="f1", content_hash="sha256:abc", extractor_name="pdf.text",
        extractor_version="3.1.0", source_type="text_document",
        raw_value="BUSIB 4300",
        location=Location("heading", (Segment("page", 1),), text_span=TextSpan(11, 21)),
        occurrence_count=3, observed_at="2026-08-19T14:03:22+00:00",
        reliability="possible", run_id="r1", normalized_value="BUSIB 4300",
        context_before="Syllabus — ", context_after=" — Spring 2026",
        context_truncated=False,
    )
    payload.update(overrides)
    return Observation(**payload)


def test_an_observation_round_trips_through_the_database(p4_conn):
    record_run(p4_conn, _run())
    observation_id = record_observation(p4_conn, _observation())
    assert get_observation(p4_conn, observation_id) == _observation()


def test_the_stored_row_carries_the_key_and_a_separate_row_id(p4_conn):
    record_run(p4_conn, _run())
    observation_id = record_observation(p4_conn, _observation())
    row = observation_row(p4_conn, observation_id)
    assert row["observation_id"] == observation_id
    assert row["observation_key"] == _observation().observation_key
    assert row["observation_id"] != row["observation_key"]


def test_context_truncated_comes_back_as_a_bool_not_an_integer(p4_conn):
    record_run(p4_conn, _run())
    observation_id = record_observation(p4_conn,
                                        _observation(context_truncated=True))
    assert get_observation(p4_conn, observation_id).context_truncated is True


def test_a_null_normalized_value_survives_the_round_trip(p4_conn):
    record_run(p4_conn, _run())
    observation_id = record_observation(p4_conn, _observation(normalized_value=None))
    assert get_observation(p4_conn, observation_id).normalized_value is None


def test_the_run_observation_count_becomes_the_truth_as_rows_land(p4_conn):
    record_run(p4_conn, _run())
    assert get_run(p4_conn, "r1").observation_count == 0
    record_observation(p4_conn, _observation())
    record_observation(p4_conn, _observation(raw_value="Spring 2026"))
    assert get_run(p4_conn, "r1").observation_count == 2
    assert len(observations_for_run(p4_conn, "r1")) == 2


def test_one_key_resolves_to_every_row_that_carries_it(p4_conn):
    # §8.7: "a negative example recorded today still resolves after an extractor
    # upgrade." MINOR 8 makes the key survive the upgrade; this makes both rows
    # reachable through it.
    record_run(p4_conn, _run())
    record_run(p4_conn, _run(run_id="r9", extractor_version="4.0.0"))
    record_observation(p4_conn, _observation())
    record_observation(p4_conn, _observation(run_id="r9", extractor_version="4.0.0"))

    key = _observation().observation_key
    found = observations_by_key(p4_conn, key)
    assert len(found) == 2
    assert {row.extractor_version for row in found} == {"3.1.0", "4.0.0"}
    assert {row.observation_key for row in found} == {key}


def test_an_unknown_key_resolves_to_nothing_rather_than_raising(p4_conn):
    assert observations_by_key(p4_conn, "sha256:never-written") == []


def test_observations_are_findable_by_file(p4_conn):
    record_run(p4_conn, _run())
    record_observation(p4_conn, _observation())
    assert len(observations_for_file(p4_conn, "f1")) == 1
    assert observations_for_file(p4_conn, "f-other") == []


def test_a_text_unit_round_trips_and_is_addressed_by_its_container_path(p4_conn):
    record_run(p4_conn, _run())
    unit = TextUnit(run_id="r1", container_path=(Segment("page", 1),), text=PAGE_ONE)
    record_text_unit(p4_conn, unit)

    assert text_units_for_run(p4_conn, "r1") == [unit]
    assert text_unit_at(p4_conn, "r1", (Segment("page", 1),)) == unit
    assert text_unit_at(p4_conn, "r1", (Segment("page", 9),)) is None
    assert text_unit_at(p4_conn, "r-other", (Segment("page", 1),)) is None


def test_a_whole_file_unit_is_addressed_by_the_empty_path(p4_conn):
    # §2.4: the full text of a text-bearing file is one row, container_path: [].
    record_run(p4_conn, _run())
    unit = TextUnit(run_id="r1", container_path=(), text=PAGE_ONE)
    record_text_unit(p4_conn, unit)
    assert text_unit_at(p4_conn, "r1", ()) == unit


def test_truncated_comes_back_as_a_bool(p4_conn):
    record_run(p4_conn, _run())
    record_text_unit(p4_conn, TextUnit(run_id="r1", container_path=(),
                                       text=PAGE_ONE[:12], truncated=True))
    assert text_unit_at(p4_conn, "r1", ()).truncated is True


def test_rule_10s_lookup_finds_the_unit_an_observations_span_points_into(p4_conn):
    record_run(p4_conn, _run())
    record_text_unit(p4_conn, TextUnit(run_id="r1",
                                       container_path=(Segment("page", 1),),
                                       text=PAGE_ONE))
    observation = _observation()
    unit = unit_for_observation(p4_conn, observation)
    assert unit is not None
    assert unit.text[observation.location.text_span.start:
                     observation.location.text_span.end] == observation.raw_value


def test_rule_10s_lookup_returns_nothing_when_no_unit_was_written(p4_conn):
    record_run(p4_conn, _run())
    assert unit_for_observation(p4_conn, _observation()) is None


def test_two_runs_over_one_pdf_leave_two_independent_unit_sets(p4_conn):
    # Rule 4, and §8.2: "if a first OCR pass produces unreadable text and a later
    # improved OCR engine recovers a university name, both extraction records should
    # remain available."
    record_run(p4_conn, _run())
    record_run(p4_conn, _ocr_run())
    record_text_unit(p4_conn, TextUnit(run_id="r1",
                                       container_path=(Segment("page", 1),),
                                       text=PAGE_ONE))
    record_text_unit(p4_conn, TextUnit(run_id="r2",
                                       container_path=(Segment("page", 1),),
                                       text="SyIIabus BUS1B 43OO"))
    assert text_unit_at(p4_conn, "r1", (Segment("page", 1),)).text == PAGE_ONE
    assert text_unit_at(p4_conn, "r2", (Segment("page", 1),)).text != PAGE_ONE
    assert len(text_units_for_run(p4_conn, "r1")) == 1
    assert len(text_units_for_run(p4_conn, "r2")) == 1


def test_the_event_carries_the_keys_once_the_observations_exist(p4_conn):
    record_run(p4_conn, _run())
    record_observation(p4_conn, _observation())
    record_observation(p4_conn, _observation(raw_value="Spring 2026"))
    explanation = json.loads(p4_conn.execute(
        "SELECT explanation FROM events WHERE event_id = ?",
        (record_run_event(p4_conn, "r1", author="P5"),)).fetchone()["explanation"])
    assert explanation["run_id"] == "r1"
    assert len(explanation["observation_keys"]) == 2
    assert all(key.startswith("sha256:") for key in explanation["observation_keys"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p4/test_p4_store.py -v`
Expected: FAIL with `ImportError: cannot import name 'record_observation' from 'evidence_shape.store'`

- [ ] **Step 3: Add the writers and readers to `store.py`**

The five import lines merge into `store.py`'s existing import block; everything below them appends after `record_run_event`. Nothing already in the file changes.

```python
# src/evidence_shape/store.py
from evidence_shape.location import Segment
from evidence_shape.locator import serialize_container_path
from evidence_shape.observation import (
    OBSERVATION_FIELDS, OBSERVATION_ROW_FIELDS, Observation, observation_from_mapping,
)
from evidence_shape.text_units import (
    TEXT_UNIT_FIELDS, TextUnit, text_unit_from_mapping,
)


def record_observation(conn: sqlite3.Connection, observation: Observation) -> str:
    """Insert one `evidence` row and mint its `observation_id`.

    The run's `observation_count` becomes the count of rows on that run: it is a
    derived number, and a stored count that disagrees with the rows is a fact nobody
    downstream can use -- §8.6's progress line least of all.
    """
    mapping = observation.to_mapping()
    row = dict(mapping)
    row["observation_id"] = new_id()
    row["location"] = canonical_json(mapping["location"])
    row["context_truncated"] = int(observation.context_truncated)
    row["supersedes"] = None
    row["superseded_by"] = None
    row["supersede_reason"] = None
    conn.execute(
        f"INSERT INTO evidence ({','.join(OBSERVATION_ROW_FIELDS)}) "
        f"VALUES ({','.join('?' * len(OBSERVATION_ROW_FIELDS))})",
        [row[name] for name in OBSERVATION_ROW_FIELDS],
    )
    conn.execute(
        "UPDATE extraction_runs SET observation_count = "
        "(SELECT count(*) FROM evidence WHERE run_id = ?) WHERE run_id = ?",
        (observation.run_id, observation.run_id),
    )
    return row["observation_id"]


def _observation_from_row(row: sqlite3.Row) -> Observation:
    mapping = {name: row[name] for name in OBSERVATION_FIELDS}
    mapping["location"] = json.loads(mapping["location"])
    mapping["context_truncated"] = bool(mapping["context_truncated"])
    return observation_from_mapping(mapping)


def observation_row(conn: sqlite3.Connection, observation_id: str) -> sqlite3.Row:
    """The stored row, including the supersede state the emitted record has no
    field for."""
    row = conn.execute("SELECT * FROM evidence WHERE observation_id = ?",
                       (observation_id,)).fetchone()
    if row is None:
        raise KeyError(f"unknown observation {observation_id!r}")
    return row


def get_observation(conn: sqlite3.Connection, observation_id: str) -> Observation:
    return _observation_from_row(observation_row(conn, observation_id))


def observations_for_run(conn: sqlite3.Connection, run_id: str) -> list[Observation]:
    return [_observation_from_row(row) for row in conn.execute(
        "SELECT * FROM evidence WHERE run_id = ? ORDER BY observation_id", (run_id,))]


def observation_keys_for_run(conn: sqlite3.Connection, run_id: str) -> list[str]:
    """The keys P4 assigned to one batch, in the order the batch was written.

    Published because a caller that emits a per-located-value record alongside a batch
    has no handle otherwise: `record_observation` returns an `observation_id`, and a
    caller that derived its own key would need a second locator implementation --
    the drift §2.8 exists to prevent. P5's §2.9 sensitivity signal is the first such
    caller, and keyed on batch position until this existed.

    Ordered by `observation_id`, which is insertion order, so position N in the emitted
    batch is position N here.
    """
    return [row["observation_key"] for row in conn.execute(
        "SELECT observation_key FROM evidence WHERE run_id = ? ORDER BY observation_id",
        (run_id,))]


def observations_for_file(conn: sqlite3.Connection, file_id: str) -> list[Observation]:
    return [_observation_from_row(row) for row in conn.execute(
        "SELECT * FROM evidence WHERE file_id = ? ORDER BY observation_id", (file_id,))]


def observations_by_key(conn: sqlite3.Connection,
                        observation_key: str) -> list[Observation]:
    """M14's citation resolver. A LIST: two extractor versions carry one key, which
    is what MINOR 8 arranged and what §8.5's cross-version diff reads."""
    return [_observation_from_row(row) for row in conn.execute(
        "SELECT * FROM evidence WHERE observation_key = ? ORDER BY observation_id",
        (observation_key,))]


def record_text_unit(conn: sqlite3.Connection, unit: TextUnit) -> None:
    mapping = unit.to_mapping()
    conn.execute(
        f"INSERT INTO text_units ({','.join(TEXT_UNIT_FIELDS)}) "
        f"VALUES ({','.join('?' * len(TEXT_UNIT_FIELDS))})",
        [mapping["run_id"], canonical_json(mapping["container_path"]),
         mapping["unit_locator"], mapping["text"], mapping["length"],
         int(mapping["truncated"])],
    )


def _text_unit_from_row(row: sqlite3.Row) -> TextUnit:
    return text_unit_from_mapping({
        "run_id": row["run_id"],
        "container_path": json.loads(row["container_path"]),
        "unit_locator": row["unit_locator"],
        "text": row["text"],
        "length": row["length"],
        "truncated": bool(row["truncated"]),
    })


def text_units_for_run(conn: sqlite3.Connection, run_id: str) -> list[TextUnit]:
    return [_text_unit_from_row(row) for row in conn.execute(
        "SELECT * FROM text_units WHERE run_id = ? ORDER BY unit_locator", (run_id,))]


def text_unit_at(conn: sqlite3.Connection, run_id: str,
                 container_path: tuple[Segment, ...]) -> TextUnit | None:
    """D12's key, `(run_id, container_path)`, through that path's canonical form."""
    row = conn.execute(
        "SELECT * FROM text_units WHERE run_id = ? AND unit_locator = ?",
        (run_id, serialize_container_path(container_path)),
    ).fetchone()
    return None if row is None else _text_unit_from_row(row)


def unit_for_observation(conn: sqlite3.Connection,
                         observation: Observation) -> TextUnit | None:
    """Conformance rule 10's lookup: the unit an observation's span points into."""
    return text_unit_at(conn, observation.run_id,
                        observation.location.container_path)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p4/test_p4_store.py -v`
Expected: PASS — 29 passed

- [ ] **Step 5: Commit**

```bash
git add src/evidence_shape/store.py tests/p4/test_p4_store.py
git commit -m "feat(P4): observation and text-unit writers, and the citation resolver"
```

---

### Task 12: Supersede, never overwrite (Done-means 7)

**Files:**
- Modify: `src/evidence_shape/store.py` — add `supersede_observation` and `supersede_chain`
- Test: `tests/p4/test_p4_supersession.py`

**Interfaces:**
- Consumes: `database_agent.supersede` — `mark_superseded`, `chain`.
- Produces (`store.py`): `supersede_observation(conn, *, old_observation_id, new_observation_id, reason) -> None`, `supersede_chain(conn, observation_id) -> list[sqlite3.Row]`.

**§8.2, quoted, because the test is the sentence:**

> The product must never overwrite the evidence record merely because a later extractor or model produces a different answer. A newer result should **supersede** an earlier result while retaining the old observation and the reason it was superseded. For example, if a first OCR pass produces unreadable text and a later improved OCR engine recovers a university name, both extraction records should remain available.

**These are two lines, not two implementations.** P1 owns `mark_superseded` and `chain`, both tested there; P4 supplies the table name and nothing else. Writing a second cycle check, a second first-reason-sticks rule and a second chain walk under a second set of names is precisely the duplication that has cost this project most.

**The old row is untouched in a way the database itself enforces.** Task 9's `evidence_never_overwritten` trigger covers the SPEC's seven never-overwritten fields, so a caller that tries to "fix" a superseded row instead of superseding it gets an abort rather than a silent rewrite. The three supersede columns are outside that trigger, which is what lets `mark_superseded` do its one legal write.

**Both runs' `text_units` stay readable** (rule 4, and Done-means 7's last clause). Superseding an observation says nothing about text: the first OCR pass's garbled page and the second pass's recovered page are two rows under two `run_id`s, and §8.2 requires both remain available so a user reviewing a placement can inspect the origin of the conclusion.

**`preferred` is still not here** (M1). §8.2 continues: *"The resolver may mark the newer value as preferred."* Preference is a resolver concern and §3.2 places the resolver after extraction, so it lives on P6's `file_facts`. P4 records what was read and what superseded it; P6 decides which one wins.

- [ ] **Step 1: Write the failing test**

```python
# tests/p4/test_p4_supersession.py
import pytest

from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import (
    get_observation, observation_row, observations_by_key, record_observation,
    record_run, record_text_unit, supersede_chain, supersede_observation,
    text_unit_at,
)
from evidence_shape.text_units import TextUnit

GARBLED = "Y0ur C0Iumb1a Un1vers1ty"
RECOVERED = "Your Columbia University"


def _ocr_run(run_id, version):
    return ExtractionRun(
        run_id=run_id, file_id="f1", content_hash="sha256:abc",
        extractor_name="ocr.apple_vision", extractor_version=version,
        source_type="ocr", analysis_tier="ocr", config={"dpi": 200},
        completeness="complete", started_at="2026-08-19T14:00:00+00:00",
        finished_at="2026-08-19T14:03:22+00:00")


def _ocr_observation(run_id, version, raw_value):
    return Observation(
        file_id="f1", content_hash="sha256:abc", extractor_name="ocr.apple_vision",
        extractor_version=version, source_type="ocr", raw_value=raw_value,
        location=Location("ocr", (Segment("page", 4), Segment("region", 2)),
                          text_span=TextSpan(0, len(raw_value))),
        occurrence_count=1, observed_at="2026-08-19T14:03:22+00:00",
        reliability="possible", run_id=run_id, confidence=0.41)


@pytest.fixture()
def two_passes(p4_conn):
    """§8.2's own example: a first OCR pass produces unreadable text and a later
    improved engine recovers a university name."""
    record_run(p4_conn, _ocr_run("r1", "2.4.1"))
    record_text_unit(p4_conn, TextUnit(
        run_id="r1", container_path=(Segment("page", 4), Segment("region", 2)),
        text=GARBLED))
    first = record_observation(p4_conn, _ocr_observation("r1", "2.4.1", GARBLED))

    record_run(p4_conn, _ocr_run("r2", "3.0.0"))
    record_text_unit(p4_conn, TextUnit(
        run_id="r2", container_path=(Segment("page", 4), Segment("region", 2)),
        text=RECOVERED))
    second = record_observation(p4_conn, _ocr_observation("r2", "3.0.0", RECOVERED))
    return first, second


def test_the_old_row_keeps_every_never_overwritten_field(two_passes, p4_conn):
    # Done-means 7: raw_value, location, occurrence_count, observed_at and
    # extractor_version are untouched.
    first, second = two_passes
    before = get_observation(p4_conn, first)
    supersede_observation(p4_conn, old_observation_id=first,
                          new_observation_id=second,
                          reason="a later improved OCR engine recovered the name")
    after = get_observation(p4_conn, first)

    assert after.raw_value == before.raw_value == GARBLED
    assert after.location == before.location
    assert after.occurrence_count == before.occurrence_count
    assert after.observed_at == before.observed_at
    assert after.extractor_version == before.extractor_version == "2.4.1"


def test_the_supersede_pointers_are_set_on_both_rows(two_passes, p4_conn):
    first, second = two_passes
    supersede_observation(p4_conn, old_observation_id=first,
                          new_observation_id=second,
                          reason="a later improved OCR engine recovered the name")
    old_row = observation_row(p4_conn, first)
    new_row = observation_row(p4_conn, second)

    assert old_row["superseded_by"] == second
    assert old_row["supersede_reason"] == \
        "a later improved OCR engine recovered the name"
    assert new_row["supersedes"] == first
    assert new_row["superseded_by"] is None


def test_both_extraction_records_remain_available(two_passes, p4_conn):
    # §8.2's own words: "both extraction records should remain available."
    first, second = two_passes
    supersede_observation(p4_conn, old_observation_id=first,
                          new_observation_id=second, reason="improved engine")
    links = supersede_chain(p4_conn, first)
    assert [row["observation_id"] for row in links] == [first, second]
    assert [row["raw_value"] for row in links] == [GARBLED, RECOVERED]


def test_both_runs_text_units_stay_readable(two_passes, p4_conn):
    # Rule 4: superseding never rewrites or deletes the earlier run's units.
    first, second = two_passes
    supersede_observation(p4_conn, old_observation_id=first,
                          new_observation_id=second, reason="improved engine")
    path = (Segment("page", 4), Segment("region", 2))
    assert text_unit_at(p4_conn, "r1", path).text == GARBLED
    assert text_unit_at(p4_conn, "r2", path).text == RECOVERED


def test_a_reason_is_required(two_passes, p4_conn):
    # §8.2: "retaining the old observation AND THE REASON it was superseded."
    first, second = two_passes
    with pytest.raises(ValueError):
        supersede_observation(p4_conn, old_observation_id=first,
                              new_observation_id=second, reason="")


def test_the_first_reason_is_never_overwritten(two_passes, p4_conn):
    first, second = two_passes
    supersede_observation(p4_conn, old_observation_id=first,
                          new_observation_id=second, reason="improved engine")
    with pytest.raises(ValueError):
        supersede_observation(p4_conn, old_observation_id=first,
                              new_observation_id=second, reason="a different story")
    assert observation_row(p4_conn, first)["supersede_reason"] == "improved engine"


def test_a_record_cannot_supersede_itself(two_passes, p4_conn):
    first, _ = two_passes
    with pytest.raises(ValueError):
        supersede_observation(p4_conn, old_observation_id=first,
                              new_observation_id=first, reason="x")


def test_superseding_does_not_change_the_citation_handles(two_passes, p4_conn):
    # The two readings are different raw values, so they are different observations
    # with different keys -- and §8.7's negative examples still resolve to both.
    first, second = two_passes
    supersede_observation(p4_conn, old_observation_id=first,
                          new_observation_id=second, reason="improved engine")
    old_key = get_observation(p4_conn, first).observation_key
    new_key = get_observation(p4_conn, second).observation_key
    assert old_key != new_key
    assert len(observations_by_key(p4_conn, old_key)) == 1
    assert observations_by_key(p4_conn, old_key)[0].raw_value == GARBLED


def test_no_preferred_column_exists_anywhere(two_passes, p4_conn):
    # M1: §8.2 says "the resolver may mark the newer value as preferred", and §3.2
    # places the resolver after extraction. Preference is P6's `file_facts`.
    columns = {row["name"] for row in p4_conn.execute("PRAGMA table_xinfo(evidence)")}
    assert "preferred" not in columns
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p4/test_p4_supersession.py -v`
Expected: FAIL with `ImportError: cannot import name 'supersede_observation' from 'evidence_shape.store'`

- [ ] **Step 3: Add the two functions to `store.py`**

The import line merges into `store.py`'s existing import block; the two functions append after `unit_for_observation`. Nothing already in the file changes.

```python
# src/evidence_shape/store.py
from database_agent.supersede import chain, mark_superseded


def supersede_observation(conn: sqlite3.Connection, *, old_observation_id: str,
                          new_observation_id: str, reason: str) -> None:
    """§8.2: a newer result supersedes an earlier one, retaining the old observation
    and the reason it was superseded.

    P1 owns the mechanism -- the cycle check, the first-reason-sticks rule and the
    chain walk are all tested there. P4 supplies the table name and nothing else; a
    second implementation would put one concept under two names.
    """
    mark_superseded(conn, "evidence", old_id=old_observation_id,
                    new_id=new_observation_id, reason=reason)


def supersede_chain(conn: sqlite3.Connection,
                    observation_id: str) -> list[sqlite3.Row]:
    """Every link, oldest first. §8.2: both extraction records remain available."""
    return chain(conn, "evidence", observation_id)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p4/test_p4_supersession.py -v`
Expected: PASS — 9 passed

- [ ] **Step 5: Commit**

```bash
git add src/evidence_shape/store.py tests/p4/test_p4_supersession.py
git commit -m "feat(P4): supersede, never overwrite — both extraction records remain"
```

---

### Task 13: The conformance validator — the observation rules (1, 2, 3, 4, 6, 7, 11, 12)

**Files:**
- Create: `src/evidence_shape/conformance.py`
- Test: `tests/p4/test_p4_conformance.py`

**Interfaces:**
- Consumes: `evidence_shape.location` — `Location`, `MalformedLocation`; `evidence_shape.locator` — `MalformedLocator`, `addressing`, `location_from_mapping`, `parse_locator`, `serialize_locator`; `evidence_shape.observation` — `MalformedObservation`, `NULLABLE_FIELDS`, `OBSERVATION_FIELDS`, `OBSERVATION_ROW_FIELDS`, `Observation`, `observation_from_mapping`; `evidence_shape.vocabulary` — `EXTRACTOR_RELIABILITY_STATES`, `SEGMENT_KINDS`, `SIGNAL_TIERS`, `SOURCE_TYPES`, `ZONES`.
- Produces: `CONFORMANCE_RULES: Mapping[int, str]`, `Violation`, `NonConforming`, `check_observation(candidate) -> tuple[Violation, ...]`, `validate_observation(candidate) -> Observation`.

**Who runs this.** The SPEC: *"A validator, shipped with P4, rejects a non-conforming observation. Six extractor authors run it as their gate; P6, P7 and P8 may assume it passed."* Done-means 2: *"it fails a non-conforming observation rather than coercing it."*

**It reports every violation, then raises.** A gate that stops at the first problem makes an extractor author fix one thing per run. `check_observation` returns a tuple of `Violation(rule, message)`; `validate_observation` raises `NonConforming` carrying all of them, or returns the constructed `Observation`.

**Rule 11 is checked in the half that is structural, and P4 names no EXIF field.** The rule is *"`signal_tier` is null unless the observation is one of §2.6's image-hierarchy signals; where present it is `1`, `2` or `3`."* §2.6's hierarchy is entirely about images — *"camera EXIF is strong photo evidence; capture time, GPS, and sensor-shaped dimensions reinforce it; exact display resolutions, PNG format, and software metadata may support a screenshot hypothesis"* — so `signal_tier` non-null implies `source_type == "image"`, and that is checkable here. **Which field inside an image belongs to which tier is P5's catalogue** (the SPEC's *Deferred* table: *"Which structured strings each extractor should recognize… P5, per format. P4 fixes the shape, not the catalogue"*), and P4 authors no list of EXIF names. Enumerating one here would be inventing the gazetteer the hard rules forbid.

**Rule 12 is checked as "a reading, not a report or a comparison".** The rule is *"No observation carries an absence, a conflict, or a resolution of a conflict (§2.6)."* Three of its four teeth are structural and are checked: the record is a closed field set with no absence, conflict or comparison field (rule 6); `raw_value` is one value, not a list of competing readings; `occurrence_count ≥ 1`, because a count of zero *is* an absence (rule 7). §2.6's conflicting signals — camera EXIF and an exact display resolution on the same image — are **two observations with two `signal_tier` values**, never a third row, and *"abstention rather than an invented classification"* is produced by P6's minimum-score-and-margin rule (§3.7) reading those two rows.

The fourth tooth is **not** P4's and this plan says so rather than faking it: an absence expressed *inside* `raw_value` as a string — `"EXIF absent"`, `"no text layer"` — is undetectable without a list of forbidden strings, and authoring one would be inventing a vocabulary. That obligation sits with P5, whose SPEC already moves *"no EXIF"* onto `extraction_runs` under **M2**. `CONFORMANCE_RULES[12]` states the split so no consumer reads rule 12 as a guarantee it is not.

**Rule 4 is checked against the addressing, not the whole record.** Segment-kind rule 2 keeps a descriptive label out of the locator and the grammar has no term for a bounding box, so a round-trip reproduces `addressing(location)` — Task 4's published projection — and not the original. Checking against the original would fail every observation that carries a heading's text or an OCR region's box, which is most of them.

**The test helper derives the key it hands over.** `_mapping` builds through `Observation`, so a mapping that overrides `raw_value` comes back carrying *that row's* `observation_key` and not the fixture's. Rule 1 requires the handle be derivable from the row it names — §8.7's negative examples resolve through it years later — so a helper that left a stale key behind would report rule 1 on every override and hide the rule actually under test. Where an override is one the record rejects, the helper drops the key rather than inventing one: an emitted observation carries no key either, and rule 1 exempts an absent one.

**Rule 5 (RAW-1) and rules 9 and 10 need a second record and are Task 14. Rule 8 needs a second run and is Task 15.** Their entries exist in `CONFORMANCE_RULES` from this task, so the numbering is stable and no rule can be quietly dropped.

- [ ] **Step 1: Write the failing test**

```python
# tests/p4/test_p4_conformance.py
import pytest

from evidence_shape.conformance import (
    CONFORMANCE_RULES, NonConforming, Violation, check_observation,
    validate_observation,
)
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import MalformedObservation, Observation
from evidence_shape.vocabulary import NotInVocabulary

FIXTURE_1 = dict(
    file_id="f1", content_hash="sha256:abc", extractor_name="pdf.text",
    extractor_version="3.1.0", source_type="text_document", raw_value="BUSIB 4300",
    location=Location("heading", (Segment("page", 1),
                                  Segment("heading", 2, label="Course Information"))),
    occurrence_count=3, observed_at="2026-08-19T14:03:22+00:00", reliability="possible",
    run_id="r1", normalized_value="BUSIB 4300", context_before="Syllabus — ",
    context_after=" — Spring 2026", context_truncated=False,
)


def _mapping(**overrides):
    """Overrides go through the record, so `observation_key` is the key of the row
    that comes back. Rule 1 requires the handle be derivable from the row it names,
    and a helper that changed `raw_value` and left the fixture's key behind would be
    testing itself rather than the rule under test.

    Overrides the record rejects are the deliberately malformed ones. Those are
    applied to the mapping afterwards and the stale key is dropped with them: a
    malformed row has no derivable key, an emitted observation carries none either,
    and rule 1 exempts an absent one.
    """
    try:
        return Observation(**{**FIXTURE_1, **overrides}).to_mapping()
    except (TypeError, MalformedObservation, NotInVocabulary):
        mapping = Observation(**FIXTURE_1).to_mapping()
        mapping.update(overrides)
        mapping.pop("observation_key", None)
        return mapping


def _rules(violations):
    return sorted({violation.rule for violation in violations})


def test_all_twelve_rules_are_published_and_numbered():
    assert sorted(CONFORMANCE_RULES) == list(range(1, 13))
    for text in CONFORMANCE_RULES.values():
        assert text.strip()


def test_a_conforming_observation_passes_and_comes_back_constructed():
    observation = Observation(**FIXTURE_1)
    assert check_observation(observation) == ()
    assert validate_observation(observation) is observation
    assert validate_observation(observation.to_mapping()) == observation


def test_rule_1_a_missing_field_is_reported():
    mapping = _mapping()
    del mapping["occurrence_count"]
    assert 1 in _rules(check_observation(mapping))


def test_rule_1_a_single_surrounding_context_field_fails():
    # M5: three fields, not one, so §8.4 can redact a value without dropping its
    # context or the reverse.
    mapping = _mapping()
    for name in ("context_before", "context_after", "context_truncated"):
        del mapping[name]
    mapping["surrounding_context"] = "Syllabus — BUSIB 4300 — Spring 2026"
    violations = check_observation(mapping)
    assert 1 in _rules(violations)
    assert 6 in _rules(violations)


def test_rule_1_a_null_in_a_non_nullable_field_is_reported():
    assert 1 in _rules(check_observation(_mapping(raw_value=None)))
    assert 1 in _rules(check_observation(_mapping(observed_at=None)))
    # ...and the five nullable ones are fine.
    assert check_observation(_mapping(normalized_value=None, context_before=None,
                                      context_after=None, confidence=None,
                                      signal_tier=None)) == ()


def test_rule_2_a_zone_outside_the_closed_vocabulary_is_reported():
    mapping = _mapping()
    mapping["location"] = {**mapping["location"], "zone": "h1", "locator": "h1"}
    assert 2 in _rules(check_observation(mapping))


def test_rule_2_a_segment_kind_outside_the_closed_vocabulary_is_reported():
    mapping = _mapping()
    mapping["location"] = {"zone": "body",
                           "container_path": [{"kind": "chapter", "index": 2}],
                           "text_span": None, "time_span": None, "region": None}
    assert 2 in _rules(check_observation(mapping))


def test_rule_2_a_source_type_outside_2_9s_families_is_reported():
    assert 2 in _rules(check_observation(_mapping(source_type="pdf")))


def test_rule_3_an_extractor_may_not_write_a_fact_layer_state():
    # D11, and §2.8's "does not treat model output as proof".
    for fact_state in ("validated", "llm_supported", "user_confirmed", "rejected"):
        assert 3 in _rules(check_observation(_mapping(reliability=fact_state)))


def test_rule_3_direct_and_possible_both_pass():
    for allowed in ("direct", "possible"):
        assert check_observation(_mapping(reliability=allowed)) == ()


def test_rule_4_a_locator_that_does_not_round_trip_is_reported():
    mapping = _mapping()
    mapping["location"] = {**mapping["location"], "locator": "title:page=1"}
    assert 4 in _rules(check_observation(mapping))


def test_rule_4_holds_for_a_label_that_needed_escaping():
    member = "docs/2026=final#draft/提出書類.pdf"
    observation = Observation(**{**FIXTURE_1, "source_type": "archive",
                                 "reliability": "direct", "raw_value": member,
                                 "location": Location(
                                     "manifest", (Segment("entry", label=member),))})
    assert check_observation(observation) == ()
    assert observation.locator.startswith("manifest:entry=")


def test_rule_6_a_destination_domain_group_node_or_plan_reference_is_reported():
    # §2.8: "Extraction does not create a final folder path, invent domains, merge
    # all files that share one string, or treat model output as proof."
    for forbidden in ("proposed_path", "destination_node", "domain", "field_name",
                      "group_id", "node_id", "template_id", "plan_version_id"):
        assert 6 in _rules(check_observation(_mapping(**{forbidden: "x"})))


def test_rule_6_an_observation_references_exactly_one_file():
    # "There is no multi-file observation, and two files sharing a raw value share
    # nothing structurally -- that link, if any, is P6's or P9's."
    assert 6 in _rules(check_observation(_mapping(file_id=["f1", "f2"])))


def test_rule_7_an_occurrence_count_below_one_is_reported():
    for absent in (0, -1):
        assert 7 in _rules(check_observation(_mapping(occurrence_count=absent)))


def test_rule_11_a_signal_tier_outside_2_6s_three_levels_is_reported():
    image = _mapping(source_type="image", reliability="direct",
                     raw_value="2026:07:17 14:03:22")
    assert 11 in _rules(check_observation({**image, "signal_tier": 4}))
    assert 11 in _rules(check_observation({**image, "signal_tier": 0}))


def test_rule_11_a_signal_tier_outside_2_6s_image_hierarchy_is_reported():
    # §2.6's hierarchy is entirely about images. The field is "null on every
    # observation outside §2.6's image hierarchy".
    assert 11 in _rules(check_observation(_mapping(signal_tier=1)))
    assert 11 in _rules(check_observation(
        _mapping(source_type="ocr", signal_tier=2)))


def test_rule_11_all_three_tiers_pass_on_an_image_observation():
    for tier in (1, 2, 3):
        assert check_observation(_mapping(
            source_type="image", reliability="direct",
            raw_value="2026:07:17 14:03:22", signal_tier=tier)) == ()


def test_rule_12_a_conflict_pair_in_one_row_is_reported():
    # §2.6's conflicting signals are TWO observations with two signal_tier values,
    # never a third "conflict" row. An observation is a reading, not a comparison of
    # readings.
    assert 12 in _rules(check_observation(
        _mapping(raw_value=["Canon EOS R6", "1920x1080"])))


def test_rule_12_two_locations_in_one_row_are_reported():
    mapping = _mapping()
    mapping["location"] = [mapping["location"], mapping["location"]]
    assert 12 in _rules(check_observation(mapping))


def test_rule_12_states_the_half_p4_cannot_check():
    # An absence written INSIDE raw_value as a string is undetectable without a list
    # of forbidden strings, and authoring one would be inventing a vocabulary. P5
    # carries that obligation; M2 already moved "no EXIF" onto extraction_runs.
    assert "P5" in CONFORMANCE_RULES[12]


def test_the_validator_reports_every_violation_before_raising():
    mapping = _mapping(reliability="validated", occurrence_count=0,
                       source_type="pdf")
    violations = check_observation(mapping)
    assert {2, 3, 7} <= set(_rules(violations))
    with pytest.raises(NonConforming) as raised:
        validate_observation(mapping)
    assert len(raised.value.violations) == len(violations)


def test_the_validator_fails_rather_than_coercing():
    # Done-means 2. Nothing comes back repaired.
    with pytest.raises(NonConforming):
        validate_observation(_mapping(reliability="VALIDATED"))
    with pytest.raises(NonConforming):
        validate_observation(_mapping(source_type="Text_Document"))


def test_a_violation_names_its_rule_and_says_something_useful():
    violation = check_observation(_mapping(reliability="llm_supported"))[0]
    assert isinstance(violation, Violation)
    assert violation.rule == 3
    assert "llm_supported" in violation.message
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p4/test_p4_conformance.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'evidence_shape.conformance'`

- [ ] **Step 3: Write the implementation**

```python
# src/evidence_shape/conformance.py
"""The conformance validator. Twelve rules; it FAILS, it does not coerce.

SPEC, Conformance: "A validator, shipped with P4, rejects a non-conforming
observation. Six extractor authors run it as their gate; P6, P7 and P8 may assume it
passed."

It reports every violation before raising, because a gate that stops at the first
problem makes an extractor author fix one thing per run.

Rule 11 is checked in the half that is structural. §2.6's hierarchy is entirely about
images, so a non-null `signal_tier` implies `source_type = "image"` and that is
checkable here. WHICH field inside an image belongs to which tier is P5's catalogue
(SPEC, Deferred: "P4 fixes the shape, not the catalogue"), and P4 authors no list of
EXIF names -- enumerating one would be inventing a gazetteer.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from evidence_shape.location import Location, MalformedLocation
from evidence_shape.locator import (
    MalformedLocator, addressing, location_from_mapping, parse_locator,
    serialize_locator,
)
from evidence_shape.observation import (
    MalformedObservation, NULLABLE_FIELDS, OBSERVATION_FIELDS, OBSERVATION_ROW_FIELDS,
    Observation, observation_from_mapping,
)
from evidence_shape.vocabulary import (
    EXTRACTOR_RELIABILITY_STATES, SEGMENT_KINDS, SIGNAL_TIERS, SOURCE_TYPES, ZONES,
)

#: The SPEC's twelve, numbered as the SPEC numbers them. Rules 5, 9 and 10 are
#: cross-record and are checked by `conformance.check_run`; rule 8 needs two runs and
#: is checked by `determinism.assert_identical_observation_sets`.
CONFORMANCE_RULES: Mapping[int, str] = MappingProxyType({
    1: "Every §2.8 field present -- with context_before, context_after and "
       "context_truncated as three fields, not one (M5); nullable only where stated.",
    2: "zone, all kinds, source_type, reliability, completeness drawn from the "
       "closed vocabularies.",
    3: "reliability in {direct, possible} on any row written by an extractor.",
    4: "locator round-trips: serialize -> parse -> structurally equal.",
    5: "RAW-1 holds wherever text_span is non-null. Checked by check_run.",
    6: "Exactly one file_id; no destination, domain, field-name, group, node, "
       "template or plan reference.",
    7: "occurrence_count >= 1.",
    8: "Same content hash + same extractor version + same config fingerprint => "
       "byte-identical observation set. Checked by evidence_shape.determinism.",
    9: "run.completeness present; unsupported, deferred and failed runs carry zero "
       "observations. Checked by check_run.",
    10: "Every observation with a non-null text_span has a text_units row on the "
        "same run_id whose container_path equals the observation's, and RAW-1 holds "
        "against that row's text. Checked by check_run.",
    11: "signal_tier is null unless the observation is one of §2.6's image-hierarchy "
        "signals; where present it is 1, 2 or 3. P4 checks the structural half -- a "
        "tier implies source_type = image -- and names no EXIF field: which field "
        "belongs to which tier is P5's catalogue.",
    12: "No observation carries an absence, a conflict, or a resolution of a "
        "conflict (§2.6). P4 checks the structural half: the field set is closed, "
        "raw_value is one value and not a list of competing readings, and "
        "occurrence_count >= 1 because a count of zero is an absence. An absence "
        "written INSIDE raw_value as a string is P5's obligation -- detecting it "
        "would need a list of forbidden strings, and P4 authors no such list.",
})

#: §2.6's hierarchy is an image hierarchy. See rule 11 above and the module docstring.
_SIGNAL_TIER_SOURCE_TYPE = "image"


@dataclass(frozen=True, slots=True)
class Violation:
    rule: int
    message: str


class NonConforming(Exception):
    """Raised by `validate_observation` / `validate_run`, carrying every violation."""

    def __init__(self, violations: tuple[Violation, ...]) -> None:
        self.violations = tuple(violations)
        super().__init__("; ".join(
            f"rule {violation.rule}: {violation.message}" for violation in self.violations))


def _one_value(value) -> bool:
    return not isinstance(value, (list, tuple, set, frozenset))


def check_observation(candidate) -> tuple[Violation, ...]:
    """Every violation of the rules an observation can break on its own."""
    violations: list[Violation] = []
    if isinstance(candidate, Observation):
        mapping = candidate.to_mapping()
    elif isinstance(candidate, Mapping):
        mapping = dict(candidate)
    else:
        return (Violation(1, f"an observation is a record or a mapping, not "
                             f"{type(candidate).__name__}"),)

    # Rule 1 -- presence and nullability.
    missing = [name for name in OBSERVATION_FIELDS
               if name != "observation_key" and name not in mapping]
    if missing:
        violations.append(Violation(1, (
            f"missing fields {missing}. §2.8's \"Surrounding context\" is three "
            "fields here -- context_before, context_after, context_truncated -- and "
            "a single-field emission fails this rule (M5)")))
    for name in OBSERVATION_FIELDS:
        if name in mapping and mapping[name] is None and name not in NULLABLE_FIELDS:
            violations.append(Violation(1, f"{name} is not nullable"))

    # Rule 6 -- a closed field set, and exactly one file.
    unknown = sorted(set(mapping) - set(OBSERVATION_ROW_FIELDS))
    if unknown:
        violations.append(Violation(6, (
            f"{unknown} are not fields of the observation record. §2.8: extraction "
            "does not create a final folder path, invent domains, merge all files "
            "that share one string, or treat model output as proof")))
    if "file_id" in mapping and not _one_value(mapping["file_id"]):
        violations.append(Violation(6, (
            "an observation references exactly one file_id; two files sharing a raw "
            "value share nothing structurally, and that link is P6's or P9's")))

    # Rule 12 -- a reading, not a report or a comparison.
    for name in ("raw_value", "location", "normalized_value"):
        if name in mapping and not _one_value(mapping[name]):
            violations.append(Violation(12, (
                f"{name} is one value. §2.6's conflicting signals are two "
                "observations with two signal_tier values, never a third row: an "
                "observation is a reading, not a comparison of readings")))

    # Rule 2 -- the closed vocabularies, checked where they live.
    source_type = mapping.get("source_type")
    if source_type is not None and source_type not in SOURCE_TYPES:
        violations.append(Violation(2, f"source_type={source_type!r} is not one of "
                                       f"§2.9's families {SOURCE_TYPES}"))
    location = mapping.get("location")
    if isinstance(location, Location):
        location_mapping = {"zone": location.zone, "container_path": [
            {"kind": segment.kind} for segment in location.container_path]}
    elif isinstance(location, Mapping):
        location_mapping = location
    else:
        location_mapping = None
        if location is not None and _one_value(location):
            violations.append(Violation(1, "location is the structured record (D1)"))
    if location_mapping is not None:
        zone = location_mapping.get("zone")
        if zone not in ZONES:
            violations.append(Violation(2, f"zone={zone!r} is not one of {ZONES}"))
        for segment in location_mapping.get("container_path") or ():
            kind = segment.get("kind") if isinstance(segment, Mapping) else None
            if kind not in SEGMENT_KINDS:
                violations.append(
                    Violation(2, f"kind={kind!r} is not one of {SEGMENT_KINDS}"))

    # Rule 3 -- what an extractor may write.
    reliability = mapping.get("reliability")
    if reliability is not None and reliability not in EXTRACTOR_RELIABILITY_STATES:
        violations.append(Violation(3, (
            f"reliability={reliability!r}: an extractor may write "
            f"{EXTRACTOR_RELIABILITY_STATES}. validated, llm_supported, "
            "user_confirmed and rejected are fact-layer outcomes (§3.5), and §2.8 "
            "forbids extraction from treating model output as proof")))

    # Rule 7 -- presence, never absence.
    count = mapping.get("occurrence_count")
    if type(count) is not int or count < 1:
        violations.append(Violation(7, (
            f"occurrence_count={count!r}: an observation records presence, and a "
            "count of zero is an absence, which lives on the run record (§2.6)")))

    # Rule 11 -- §2.6's tier, in the half that is structural.
    tier = mapping.get("signal_tier")
    if tier is not None:
        if tier not in SIGNAL_TIERS:
            violations.append(
                Violation(11, f"signal_tier={tier!r} is not one of {SIGNAL_TIERS}"))
        if source_type != _SIGNAL_TIER_SOURCE_TYPE:
            violations.append(Violation(11, (
                f"signal_tier is set on a source_type={source_type!r} observation. "
                "§2.6's hierarchy is an image hierarchy, and the field is null on "
                "every observation outside it")))

    # Rule 4 -- the locator round-trips. Needs a constructed location.
    if location_mapping is not None and not violations:
        try:
            built = (location if isinstance(location, Location)
                     else location_from_mapping(location_mapping))
            serialized = serialize_locator(built)
            # Against `addressing`, not `built`: rule 2 keeps a descriptive label out
            # of the string and the grammar has no term for a bounding box, so those
            # two are deliberately not part of what a round-trip reproduces.
            if parse_locator(serialized) != addressing(built):
                violations.append(Violation(4, (
                    f"locator {serialized!r} does not parse back to the addressing it "
                    "serialized from")))
        except (MalformedLocation, MalformedLocator) as exc:
            violations.append(Violation(4, str(exc)))

    # Anything the record types catch that the rules above did not name.
    if not violations:
        try:
            observation_from_mapping(mapping) if not isinstance(
                candidate, Observation) else None
        except (MalformedObservation, MalformedLocation, MalformedLocator) as exc:
            violations.append(Violation(1, str(exc)))
    return tuple(violations)


def validate_observation(candidate) -> Observation:
    """The extractor's gate. Returns the constructed record, or raises with every
    violation. It never returns a repaired record (Done-means 2)."""
    violations = check_observation(candidate)
    if violations:
        raise NonConforming(violations)
    if isinstance(candidate, Observation):
        return candidate
    return observation_from_mapping(candidate)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p4/test_p4_conformance.py -v`
Expected: PASS — 24 passed

- [ ] **Step 5: Commit**

```bash
git add src/evidence_shape/conformance.py tests/p4/test_p4_conformance.py
git commit -m "feat(P4): the conformance validator — the observation rules, fail not coerce"
```

---
### Task 14: The conformance validator — the cross-record rules (5, 9, 10)

**Files:**
- Modify: `src/evidence_shape/conformance.py` — add `check_run` and `validate_run`
- Test: `tests/p4/test_p4_conformance_runs.py`
- Test: `tests/p4/test_p4_raw1.py`

**Interfaces:**
- Consumes: `evidence_shape.locator` — `serialize_container_path`; `evidence_shape.observation` — `Observation`, `observation_from_mapping`; `evidence_shape.runs` — `ExtractionRun`, `MalformedRun`, `run_from_mapping`; `evidence_shape.text_units` — `SpanAnchorError`, `TextUnit`, `check_span_anchor`; `evidence_shape.vocabulary` — `NotInVocabulary`, `ZERO_OBSERVATION_COMPLETENESS`.
- Produces (`conformance.py`): `check_run(run, observations=(), text_units=()) -> tuple[Violation, ...]`, `validate_run(run, observations=(), text_units=()) -> ExtractionRun`.

**Three rules need a second record, which is why they are here and not in Task 13.** Rule 9 is a statement about a run and its observation *set*; rules 10 and 5 are statements about an observation and the text unit its span points into. None of the three can be decided from an observation alone, and a validator that pretended otherwise would pass an extractor that emitted a span into a unit it never wrote.

**Rule 9, with M3's relaxation intact.** The SPEC: *"`run.completeness` present; **`unsupported`, `deferred` and `failed` runs carry zero observations.**"* Those three, and no others — `vocabulary.ZERO_OBSERVATION_COMPLETENESS` is that exact tuple and this task adds no second list. `unreadable`, `partial` and `metadata_only` runs **may and normally do** carry observations: §2.9 requires an unsupported proprietary format be *"recorded as indexed-but-unreadable rather than silently treated as empty"*, and its metadata-level rows are what "indexed" means. A rule forbidding them would make an indexed PSD indistinguishable from a file nobody opened.

**Rule 10 is the existence-and-address half; RAW-1 is checked once, and reported as rule 5.** Rule 10's own text ends *"and RAW-1 holds against that row's text"*, so the two rules overlap on one condition. This task checks that condition once and reports it under **rule 5**, the rule that names it — reporting one defect under two numbers would make an extractor author fix it twice and is the same one-concept-two-names defect the vocabularies exist to prevent. Rule 10 keeps the half that is its own: *a unit exists, on this run, at this address*.

**And it is Task 8's check, not a second one.** `text_units.check_span_anchor` already holds RAW-1, the run match, the address match and the truncated-prefix rule, and it is tested there. `check_run` looks the unit up and calls it. The difference between the two surfaces is what they do with a failure, not how they decide it: `check_span_anchor` raises on the first problem because it is a writer's assertion, `check_run` collects because it is an author's gate.

**No thirteenth rule about `observation_count`.** A run row whose count disagrees with its rows is a real defect, but the SPEC lists twelve rules and none of them is this one, and P4 does not legislate a thirteenth into a published contract. `store.record_observation` derives the count from the rows on every insert (Task 11), so the disagreement cannot arise through P4's own writer; a caller that inserts by hand is outside the shape P4 publishes.

**One call is the whole gate.** `check_run` runs Task 13's per-observation rules over each member of the set as well, tagged by position, so an extractor author who calls `validate_run` at the end of a run cannot get a false pass on a set whose members are individually non-conforming.

- [ ] **Step 1: Write the failing test**

```python
# tests/p4/test_p4_conformance_runs.py
import pytest

from evidence_shape.conformance import (
    NonConforming, check_run, validate_run,
)
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.text_units import TextUnit

PAGE_TEXT = "Syllabus — BUSIB 4300 — Spring 2026"
SPAN = TextSpan(PAGE_TEXT.index("BUSIB"), PAGE_TEXT.index("BUSIB") + len("BUSIB 4300"))


def _run(completeness="complete", run_id="r1", **overrides):
    fields = dict(
        run_id=run_id, file_id="f1", content_hash="sha256:abc",
        extractor_name="pdf.text", extractor_version="3.1.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness=completeness, started_at="2026-08-19T14:00:00+00:00",
        finished_at="2026-08-19T14:03:22+00:00")
    fields.update(overrides)
    return ExtractionRun(**fields)


def _observation(run_id="r1", *, text_span=None, container_path=(Segment("page", 1),),
                 raw_value="BUSIB 4300", **overrides):
    fields = dict(
        file_id="f1", content_hash="sha256:abc", extractor_name="pdf.text",
        extractor_version="3.1.0", source_type="text_document", raw_value=raw_value,
        location=Location("body", container_path, text_span=text_span),
        occurrence_count=1, observed_at="2026-08-19T14:03:22+00:00",
        reliability="possible", run_id=run_id)
    fields.update(overrides)
    return Observation(**fields)


def _unit(run_id="r1", *, text=PAGE_TEXT, container_path=(Segment("page", 1),),
          truncated=False):
    return TextUnit(run_id=run_id, container_path=container_path, text=text,
                    truncated=truncated)


def _rules(violations):
    return sorted({violation.rule for violation in violations})


def test_a_run_with_no_observations_and_no_units_passes():
    assert check_run(_run()) == ()


def test_a_run_whose_observations_carry_no_span_needs_no_units():
    # Rule 10 applies to a span. A metadata observation has none.
    observation = _observation(
        location=Location("metadata", (Segment("field", label="Producer"),)),
        raw_value="python-docx", reliability="direct")
    assert check_run(_run(), [observation]) == ()


def test_rule_9_the_three_zero_observation_states_reject_an_observation():
    # The SPEC's three, and only these three.
    for completeness in ("unsupported", "deferred", "failed"):
        violations = check_run(_run(completeness), [_observation()])
        assert 9 in _rules(violations), completeness
        assert completeness in violations[0].message


def test_rule_9_the_three_zero_observation_states_pass_with_zero_observations():
    for completeness in ("unsupported", "deferred", "failed"):
        assert check_run(_run(completeness)) == (), completeness


def test_rule_9_an_unreadable_run_still_carries_its_metadata_rows():
    # M3, and §2.9's "indexed-but-unreadable rather than silently treated as empty".
    # A rule forbidding these rows would make an indexed PSD indistinguishable from a
    # file nobody opened.
    layer = _observation(
        source_type="design_creative", reliability="direct", raw_value="Background",
        location=Location("metadata", (Segment("layer", 3),)))
    assert check_run(_run("unreadable"), [layer]) == ()


def test_rule_9_partial_and_capped_runs_may_carry_observations():
    for completeness in ("partial", "capped"):
        assert check_run(_run(completeness), [_observation()]) == (), completeness


def test_rule_9_a_metadata_only_run_carries_none(): 
    # Settled 2026-08-20 against worked example 19: the stopping extractor emits
    # nothing; the file stays indexed through its `filesystem` observations. Rule 9's
    # note used to say the opposite, and six extractors would have run that gate.
    assert 9 in _rules(check_run(_run("metadata_only"), [_observation()]))
    assert check_run(_run("metadata_only"), []) == ()


def test_rule_9_a_dataless_run_carries_none():
    # C4: nothing was opened, so nothing was seen.
    assert 9 in _rules(check_run(_run("dataless"), [_observation()]))
    assert check_run(_run("dataless"), []) == ()


def test_rule_9_a_run_with_no_completeness_is_reported():
    mapping = _run().to_mapping()
    del mapping["completeness"]
    assert 9 in _rules(check_run(mapping))


def test_rule_9_a_completeness_outside_the_closed_vocabulary_is_reported():
    mapping = _run().to_mapping()
    mapping["completeness"] = "empty"
    assert 9 in _rules(check_run(mapping))


def test_rule_9_an_observation_from_another_run_is_reported():
    # Rules 9 and 10 are both statements about THIS run's set.
    assert 9 in _rules(check_run(_run(), [_observation(run_id="r2")]))


def test_rule_10_a_span_with_no_unit_is_reported():
    violations = check_run(_run(), [_observation(text_span=SPAN)])
    assert _rules(violations) == [10]
    assert "page=1" in violations[0].message


def test_rule_10_a_unit_at_another_address_does_not_satisfy_the_span():
    violations = check_run(_run(), [_observation(text_span=SPAN)],
                           [_unit(container_path=(Segment("page", 2),))])
    assert _rules(violations) == [10]


def test_rule_10_a_unit_on_another_run_does_not_satisfy_the_span():
    # Text is per run, not per file: a text-layer pass and an OCR pass over one PDF
    # produce two texts under two run_ids (§8.2).
    violations = check_run(_run(), [_observation(text_span=SPAN)], [_unit(run_id="r2")])
    assert 10 in _rules(violations)


def test_rule_10_and_rule_5_are_satisfied_by_the_unit_the_span_points_into():
    assert check_run(_run(), [_observation(text_span=SPAN)], [_unit()]) == ()


def test_rule_10_matches_on_the_address_and_not_on_the_descriptive_label():
    # Segment-kind rule 2: a label is descriptive only and never appears in the
    # locator, and `(run_id, unit_locator)` is what text_units is keyed on. A unit at
    # `page=1` satisfies an observation whose segment carries a heading's text.
    labelled = _observation(text_span=SPAN,
                            container_path=(Segment("page", 1, label="Course Information"),))
    assert check_run(_run(), [labelled], [_unit()]) == ()


def test_rule_5_a_raw_value_that_is_not_the_substring_is_reported():
    # RAW-1 is checked ONCE and reported under rule 5, the rule that names it.
    violations = check_run(_run(), [_observation(text_span=SPAN, raw_value="Columbia")],
                           [_unit()])
    assert _rules(violations) == [5]
    assert "RAW-1" in violations[0].message


def test_rule_5_a_span_beyond_a_truncated_unit_is_reported():
    # §8.6: never truncate silently. An observation whose span lies beyond the stored
    # prefix is not written.
    violations = check_run(
        _run(), [_observation(text_span=TextSpan(0, 40))],
        [_unit(text=PAGE_TEXT[:20], truncated=True)])
    assert _rules(violations) == [5]
    assert "truncated" in violations[0].message


def test_the_per_observation_rules_are_checked_through_the_run_gate_too():
    # One call is the whole gate: a set whose members are individually non-conforming
    # does not pass because the run-level rules happen to hold.
    mapping = _observation().to_mapping()
    mapping["occurrence_count"] = 0
    violations = check_run(_run(), [mapping])
    assert 7 in _rules(violations)


def test_a_violation_from_the_set_names_which_member_it_came_from():
    mapping = _observation().to_mapping()
    mapping["occurrence_count"] = 0
    violations = check_run(_run(), [_observation(), mapping])
    assert violations[0].message.startswith("observation 1: ")


def test_validate_run_returns_the_constructed_run():
    run = _run()
    assert validate_run(run) is run
    assert validate_run(run.to_mapping()) == run


def test_validate_run_reports_every_violation_before_raising():
    with pytest.raises(NonConforming) as raised:
        validate_run(_run("failed"), [_observation(text_span=SPAN)])
    assert _rules(raised.value.violations) == [9, 10]


def test_validate_run_fails_rather_than_coercing():
    # Done-means 2. Nothing comes back repaired, and no observation is dropped to
    # make a `failed` run conform.
    with pytest.raises(NonConforming):
        validate_run(_run("unsupported"), [_observation()])
```

```python
# tests/p4/test_p4_raw1.py
"""Done-means 4, at the layer that ships: RAW-1 through the validator six extractor
authors run as their gate, on a CJK fixture and an emoji fixture (D4's code-point
unit).

Task 8 proves the same property on `check_span_anchor`, the primitive. This file
proves that `check_run` — the call an extractor author actually makes — enforces it as
rule 5, on the two scripts D4 was chosen for.
"""
from evidence_shape.conformance import check_run
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.text_units import TextUnit

#: §2.7 requires CJK. Every character here is one code point and three UTF-8 bytes.
CJK_PAGE = "提出書類は慶應義塾大学の入学課に送付してください。締切は二〇二六年三月三十一日です。"
CJK_VALUE = "慶應義塾大学"

#: One astral-plane emoji is ONE code point and TWO UTF-16 units, so an offset
#: counted in UTF-16 lands in the middle of the character and RAW-1 fails.
EMOJI_PAGE = "Submitted 🎓 to Columbia University"
EMOJI_VALUE = "Columbia"


def _run(run_id="r1"):
    return ExtractionRun(
        run_id=run_id, file_id="f1", content_hash="sha256:abc",
        extractor_name="ocr.apple_vision", extractor_version="2.4.1",
        source_type="ocr", analysis_tier="ocr",
        config={"languages": ["ja", "en"]}, completeness="complete",
        started_at="2026-08-19T14:00:00+00:00")


def _pair(page, value, *, start=None, end=None):
    start = page.index(value) if start is None else start
    end = start + len(value) if end is None else end
    observation = Observation(
        file_id="f1", content_hash="sha256:abc", extractor_name="ocr.apple_vision",
        extractor_version="2.4.1", source_type="ocr", raw_value=value,
        location=Location("ocr", (Segment("page", 1),),
                          text_span=TextSpan(start, end)),
        occurrence_count=1, observed_at="2026-08-19T14:03:22+00:00",
        reliability="possible", run_id="r1")
    return [observation], [TextUnit(run_id="r1", container_path=(Segment("page", 1),),
                                    text=page)]


def test_raw_1_holds_through_the_gate_on_a_cjk_fixture():
    observations, units = _pair(CJK_PAGE, CJK_VALUE)
    assert check_run(_run(), observations, units) == ()


def test_a_byte_offset_into_the_cjk_fixture_fails_the_gate():
    # The same value addressed in UTF-8 bytes, which is what a naive extractor would
    # emit. D4 counts code points precisely so this is a failure and not a silent
    # mis-citation.
    byte_start = len(CJK_PAGE[:CJK_PAGE.index(CJK_VALUE)].encode("utf-8"))
    observations, units = _pair(CJK_PAGE, CJK_VALUE, start=byte_start,
                                end=byte_start + len(CJK_VALUE.encode("utf-8")))
    violations = check_run(_run(), observations, units)
    assert [violation.rule for violation in violations] == [5]
    assert "RAW-1" in violations[0].message


def test_raw_1_holds_through_the_gate_across_an_astral_emoji():
    observations, units = _pair(EMOJI_PAGE, EMOJI_VALUE)
    assert check_run(_run(), observations, units) == ()


def test_a_utf_16_offset_across_an_astral_emoji_fails_the_gate():
    # In UTF-16 the emoji occupies two units, so every offset after it is one too
    # large. Nothing in this package converts, which is why the failure is visible.
    utf_16_start = EMOJI_PAGE.index(EMOJI_VALUE) + 1
    observations, units = _pair(EMOJI_PAGE, EMOJI_VALUE, start=utf_16_start,
                                end=utf_16_start + len(EMOJI_VALUE))
    violations = check_run(_run(), observations, units)
    assert [violation.rule for violation in violations] == [5]
    assert "RAW-1" in violations[0].message


def test_the_stored_length_is_counted_in_code_points_not_bytes():
    _, units = _pair(CJK_PAGE, CJK_VALUE)
    assert units[0].length == len(CJK_PAGE)
    assert units[0].length != len(CJK_PAGE.encode("utf-8"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p4/test_p4_conformance_runs.py tests/p4/test_p4_raw1.py -v`
Expected: FAIL with `ImportError: cannot import name 'check_run' from 'evidence_shape.conformance'`

- [ ] **Step 3: Write the implementation**

```python
# src/evidence_shape/conformance.py
from evidence_shape.locator import serialize_container_path
from evidence_shape.runs import ExtractionRun, MalformedRun, run_from_mapping
from evidence_shape.text_units import SpanAnchorError, TextUnit, check_span_anchor
from evidence_shape.vocabulary import (
    NotInVocabulary, ZERO_OBSERVATION_COMPLETENESS,
)


def check_run(run, observations=(), text_units=()) -> tuple[Violation, ...]:
    """Rules 9, 10 and 5 -- the three that need a second record -- plus Task 13's
    per-observation rules over every member of the set.

    RAW-1 is decided by `text_units.check_span_anchor` and reported under rule 5, the
    rule that names it. Rule 10 keeps the half that is its own: a unit exists, on this
    run, at this address. One defect is reported once.
    """
    violations: list[Violation] = []
    if isinstance(run, ExtractionRun):
        record = run
    elif isinstance(run, Mapping):
        try:
            record = run_from_mapping(run)
        except (MalformedRun, NotInVocabulary) as exc:
            return (Violation(9, str(exc)),)
    else:
        return (Violation(9, f"a run is a record or a mapping, not "
                             f"{type(run).__name__}"),)

    members = tuple(observations)
    # Rule 9. The SPEC's three, and no others: M3 keeps `unreadable`, `partial` and
    # `metadata_only` carrying the metadata-level rows §2.9's "indexed" means.
    if record.completeness in ZERO_OBSERVATION_COMPLETENESS and members:
        violations.append(Violation(9, (
            f"a {record.completeness!r} run carries zero observations and this one "
            f"carries {len(members)}; what such a run knows is on the run record")))

    index: dict[str, TextUnit] = {}
    for unit in text_units:
        if not isinstance(unit, TextUnit):
            violations.append(Violation(10, f"a text unit is a TextUnit record, not "
                                            f"{type(unit).__name__}"))
            continue
        if unit.run_id != record.run_id:
            violations.append(Violation(10, (
                f"unit {unit.unit_locator!r} belongs to run {unit.run_id!r}, not to "
                f"{record.run_id!r}; text is per run, not per file (§8.2)")))
            continue
        index[unit.unit_locator] = unit

    for position, candidate in enumerate(members):
        own = check_observation(candidate)
        if own:
            violations.extend(
                Violation(violation.rule, f"observation {position}: {violation.message}")
                for violation in own)
            continue
        observation = (candidate if isinstance(candidate, Observation)
                       else observation_from_mapping(candidate))
        if observation.run_id != record.run_id:
            violations.append(Violation(9, (
                f"observation {position} belongs to run {observation.run_id!r}, not "
                f"to {record.run_id!r}; rules 9 and 10 are statements about this "
                "run's own set")))
            continue
        if observation.location.text_span is None:
            continue
        address = serialize_container_path(observation.location.container_path)
        unit = index.get(address)
        if unit is None:
            violations.append(Violation(10, (
                f"observation {position} has a text_span and no text_units row at "
                f"{address!r} on run {record.run_id!r}; a span is an offset into a "
                "stored unit, and without one no citation check can resolve it")))
            continue
        try:
            check_span_anchor(observation, unit)
        except SpanAnchorError as exc:
            violations.append(Violation(5, f"observation {position}: {exc}"))
    return tuple(violations)


def validate_run(run, observations=(), text_units=()) -> ExtractionRun:
    """The extractor's gate for a whole run. Returns the constructed record, or
    raises with every violation. It never drops an observation to make a run
    conform (Done-means 2)."""
    violations = check_run(run, observations, text_units)
    if violations:
        raise NonConforming(violations)
    if isinstance(run, ExtractionRun):
        return run
    return run_from_mapping(run)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p4/test_p4_conformance_runs.py tests/p4/test_p4_raw1.py -v`
Expected: PASS — 26 passed

- [ ] **Step 5: Commit**

```bash
git add src/evidence_shape/conformance.py tests/p4/test_p4_conformance_runs.py tests/p4/test_p4_raw1.py
git commit -m "feat(P4): the conformance validator — the cross-record rules, RAW-1 reported once"
```

---
### Task 15: Determinism — conformance rule 8 and the compared observation set (Done-means 8)

**Files:**
- Create: `src/evidence_shape/determinism.py`
- Test: `tests/p4/test_p4_determinism.py`

**Interfaces:**
- Consumes: `evidence_shape.canonical` — `canonical_json`, `sha256_of`; `evidence_shape.observation` — `OBSERVATION_FIELDS`, `Observation`; `evidence_shape.runs` — `ExtractionRun`.
- Produces: `REPLAY_KEY_FIELDS`, `EXCLUDED_FROM_COMPARISON`, `COMPARED_FIELDS`, `NotDeterministic`, `replay_key(run) -> tuple[str, ...]`, `compared_form(observation) -> dict`, `observation_set_bytes(observations) -> str`, `observation_set_digest(observations) -> str`, `assert_identical_observation_sets(first_run, first_observations, second_run, second_observations) -> None`.

**Rule 8, verbatim:** *"Same content hash + same extractor version + same config fingerprint ⇒ byte-identical observation set (§3.4 caching, §8.5 replay)."* Done-means 8: *"two runs at the same content hash, extractor version and config fingerprint produce byte-identical observation sets."*

**Two fields are outside the comparison, and rule 8's own premise is what puts them there.** The premise is *two runs*. A `run_id` is minted per run and an `observed_at` is the wall-clock instant a reading was taken, so a comparison that included either would report every row as changed on every re-run and rule 8 would be unsatisfiable by construction — including for the cache §3.4 wants and the diff §8.5 wants. `EXCLUDED_FROM_COMPARISON` is exactly those two, each carrying its reason in the source, and it is the only exclusion list in this package.

**`file_id` is excluded, because OQ2 closed.** Ratified 2026-08-20: the content hash owns the observation, so two `files` rows holding the same bytes share one observation set. If `file_id` were compared, a duplicate would read as a *different* set and rule 8 could never hold across one — the exact case the ratification exists to make work. The field stays **on** the observation, as §2.8 requires: it records which copy was opened, not who owns the reading. (While OQ2 was open this plan kept `file_id` in, deliberately, so as not to answer a contract question from inside an implementation. The contract answered it.)

**The compared set is a multiset, sorted.** A set has no order, so the digest sorts; but D10's collapse key is `(run_id, raw_value, zone)` and Task 6 deliberately enforces no uniqueness on it, so two identical readings may legitimately both exist. Collapsing them here would make a validator quietly disagree with the table it validates.

**`REPLAY_KEY_FIELDS` carries four names where rule 8 lists three, and this is a SPEC-vs-design conflict this plan reports rather than hides.** Rule 8 names `content_hash`, `extractor_version` and `config_fingerprint`. §3.4 asks for a cache key on *"the content hash and the exact process that produced it"*, and Task 9's `extraction_runs_cache_key` index — already written — carries `extractor_name` as a fourth. Read literally, rule 8's three would require `pdf.text 3.1.0` and `ocr.apple_vision 3.1.0` over one file to produce one identical observation set; `observation_key` includes `extractor_name` (Task 6), so those two sets can never be equal and the literal rule can never hold. P4 therefore keys on the four §3.4 names, states the discrepancy in the module docstring, and records it under *SPEC vs design — conflicts found* at the end of this plan. **P4 does not rewrite rule 8's text** — that is a contract revision, and it is Joseph's.

**This module is not a diff.** §8.5's cross-version comparison is a different question — *what did the new extractor version change?* — and it is answered on `observation_key`, which excludes `extractor_version` precisely so the two versions' rows line up (MINOR 8, Task 6). Rule 8 asks the narrower question: *did the same process, twice, produce the same thing?* Building a diff here would be P4 writing P2's replay harness a second time.

- [ ] **Step 1: Write the failing test**

```python
# tests/p4/test_p4_determinism.py
"""Done-means 8, and conformance rule 8's compared observation set."""
import pytest

from evidence_shape.determinism import (
    COMPARED_FIELDS, EXCLUDED_FROM_COMPARISON, NotDeterministic, REPLAY_KEY_FIELDS,
    assert_identical_observation_sets, compared_form, observation_set_digest,
    replay_key,
)
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import OBSERVATION_FIELDS, Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import observations_for_run, record_observation, record_run

CONFIG = {"languages": ["en", "zh-Hans"], "recognition": "accurate"}


def _run(run_id, *, version="3.1.0", config=CONFIG, name="pdf.text"):
    return ExtractionRun(
        run_id=run_id, file_id="f1", content_hash="sha256:abc", extractor_name=name,
        extractor_version=version, source_type="text_document",
        analysis_tier="native", config=config, completeness="complete",
        started_at="2026-08-19T14:00:00+00:00")


def _observation(run_id, *, version="3.1.0", name="pdf.text",
                 raw_value="BUSIB 4300", heading=2, observed_at="2026-08-19T14:03:22+00:00"):
    return Observation(
        file_id="f1", content_hash="sha256:abc", extractor_name=name,
        extractor_version=version, source_type="text_document", raw_value=raw_value,
        location=Location("heading", (Segment("page", 1), Segment("heading", heading))),
        occurrence_count=3, observed_at=observed_at, reliability="possible",
        run_id=run_id, normalized_value=raw_value, context_before="Syllabus — ",
        context_after=" — Spring 2026", context_truncated=False)


def test_the_compared_set_is_every_emitted_field_but_three():
    # `file_id` joined the exclusions when OQ2 closed: the content hash owns the
    # observation, so two copies of one file must compare equal.
    assert EXCLUDED_FROM_COMPARISON == ("run_id", "observed_at", "file_id")
    assert COMPARED_FIELDS == tuple(
        name for name in OBSERVATION_FIELDS if name not in EXCLUDED_FROM_COMPARISON)


def test_two_runs_of_the_same_process_produce_one_digest(p4_conn):
    # Done-means 8, through the store, which is where a real extractor would land.
    first, second = _run("r1"), _run("r2")
    record_run(p4_conn, first)
    record_run(p4_conn, second)
    record_observation(p4_conn, _observation("r1"))
    record_observation(p4_conn, _observation("r2", observed_at="2026-08-20T09:15:00+00:00"))

    assert (observation_set_digest(observations_for_run(p4_conn, "r1"))
            == observation_set_digest(observations_for_run(p4_conn, "r2")))
    assert_identical_observation_sets(
        first, observations_for_run(p4_conn, "r1"),
        second, observations_for_run(p4_conn, "r2"))


def test_the_run_id_and_the_observation_time_are_the_two_fields_outside_it():
    # Rule 8's premise is TWO RUNS. A comparison that carried either of these would
    # report every row as changed on every re-run.
    base = _observation("r1")
    assert (observation_set_digest([base])
            == observation_set_digest([_observation("r9", observed_at="2027-01-01T00:00:00+00:00")]))


def test_a_different_reading_changes_the_digest():
    assert (observation_set_digest([_observation("r1")])
            != observation_set_digest([_observation("r1", raw_value="BUSIB 4301")]))


def test_a_different_location_changes_the_digest():
    assert (observation_set_digest([_observation("r1")])
            != observation_set_digest([_observation("r1", heading=3)]))


def test_the_digest_does_not_depend_on_emission_order():
    one, two = _observation("r1"), _observation("r1", heading=3)
    assert observation_set_digest([one, two]) == observation_set_digest([two, one])


def test_two_identical_readings_are_not_collapsed():
    # D10's collapse key is (run_id, raw_value, zone) and Task 6 enforces no
    # uniqueness on it. A digest that collapsed them would disagree with the table.
    one = _observation("r1")
    assert observation_set_digest([one]) != observation_set_digest([one, one])


def test_a_missing_observation_is_reported_with_the_row_that_went_missing():
    first, second = _run("r1"), _run("r2")
    with pytest.raises(NotDeterministic) as raised:
        assert_identical_observation_sets(
            first, [_observation("r1"), _observation("r1", heading=3)],
            second, [_observation("r2")])
    assert "heading=3" in str(raised.value)


def test_two_configurations_are_not_one_replay_key():
    with pytest.raises(NotDeterministic) as raised:
        assert_identical_observation_sets(
            _run("r1"), [], _run("r2", config={"recognition": "fast"}), [])
    assert "replay key" in str(raised.value)


def test_two_extractor_versions_are_not_one_replay_key_but_share_one_citation_handle():
    # MINOR 8: `observation_key` excludes `extractor_version` so §8.5's cross-version
    # diff has something to diff against. Rule 8 asks the narrower question.
    old = _observation("r1", version="3.1.0")
    new = _observation("r2", version="4.0.0")
    assert old.observation_key == new.observation_key
    with pytest.raises(NotDeterministic):
        assert_identical_observation_sets(
            _run("r1", version="3.1.0"), [old], _run("r2", version="4.0.0"), [new])


def test_the_replay_key_carries_the_extractor_name_rule_8_omits():
    # SPEC vs design, reported not hidden: rule 8 lists three fields; §3.4 asks for
    # "the content hash and the exact process that produced it" and Task 9's cache
    # index carries four. Two different extractors at one version can never produce
    # one set, because `observation_key` includes `extractor_name`.
    assert REPLAY_KEY_FIELDS == ("content_hash", "extractor_name", "extractor_version",
                                 "config_fingerprint")
    assert (replay_key(_run("r1", name="pdf.text"))
            != replay_key(_run("r2", name="ocr.apple_vision")))


def test_the_compared_form_accepts_a_stored_row_and_a_record_alike():
    observation = _observation("r1")
    assert compared_form(observation) == compared_form(observation.to_mapping())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p4/test_p4_determinism.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'evidence_shape.determinism'`

- [ ] **Step 3: Write the implementation**

```python
# src/evidence_shape/determinism.py
"""Conformance rule 8 -- the compared observation set.

Rule 8: "Same content hash + same extractor version + same config fingerprint =>
byte-identical observation set (§3.4 caching, §8.5 replay)."

Two fields are outside the comparison and rule 8's own premise is what puts them
there. The premise is TWO RUNS: a `run_id` is minted per run and `observed_at` is the
instant a reading was taken, so a comparison carrying either would report every row as
changed on every re-run and the rule could never hold. `file_id` is excluded for a
different reason: OQ2 closed on 2026-08-20 and the CONTENT HASH owns the observation,
so two `files` rows over one set of bytes share one observation set. Comparing
`file_id` would make a duplicate look like a different set and rule 8 could never hold
across one. The field stays ON the observation (§2.8 requires it) -- it says which
copy was opened, not who owns the reading.

SPEC vs design, reported and not resolved here: rule 8 lists THREE key fields and
§3.4 asks for a cache key on "the content hash and the exact process that produced
it", which the `extraction_runs_cache_key` index spells with FOUR -- `extractor_name`
included. Read literally, rule 8's three would require two different extractors at one
version over one file to produce one identical set, and `observation_key` includes
`extractor_name`, so those sets can never be equal. This module keys on the four §3.4
names. Rewriting rule 8's text is a contract revision and is not P4's to make.

This is not a diff. §8.5's cross-version comparison is a different question, answered
on `observation_key`, which excludes `extractor_version` precisely so the two versions'
rows line up (MINOR 8). Rule 8 asks only whether the same process, run twice, produced
the same thing.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Mapping

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.observation import OBSERVATION_FIELDS, Observation
from evidence_shape.runs import ExtractionRun

#: §3.4's "the content hash and the exact process that produced it". See the docstring
#: for why this is four names where rule 8's sentence lists three.
REPLAY_KEY_FIELDS: tuple[str, ...] = (
    "content_hash", "extractor_name", "extractor_version", "config_fingerprint",
)

#: The only exclusion list in this package, and each member is forced -- not chosen.
#: `run_id`: minted per run, and rule 8 compares two runs. `observed_at`: the wall
#: clock at the reading, which no re-run reproduces. `file_id`: OQ2 closed on
#: 2026-08-20 -- the CONTENT HASH owns the observation, so two `files` rows holding
#: the same bytes share one observation set. Comparing `file_id` would report the
#: second copy as a different set and rule 8 could never hold across a duplicate,
#: which is precisely the outcome the ratification forbids. `file_id` remains ON the
#: observation as §2.8 requires -- it records which copy was opened, not who owns it.
EXCLUDED_FROM_COMPARISON: tuple[str, str, str] = ("run_id", "observed_at", "file_id")

#: What "byte-identical observation set" is computed over.
COMPARED_FIELDS: tuple[str, ...] = tuple(
    name for name in OBSERVATION_FIELDS if name not in EXCLUDED_FROM_COMPARISON)


class NotDeterministic(ValueError):
    """Rule 8 does not hold between two runs, or the two are not one replay key."""


def replay_key(run: ExtractionRun) -> tuple[str, ...]:
    """The identity rule 8's premise fixes. `config_fingerprint` is derived (Task 7)."""
    return tuple(str(getattr(run, name)) for name in REPLAY_KEY_FIELDS)


def compared_form(observation) -> dict[str, object]:
    """One observation, reduced to what rule 8 compares. Record or stored row."""
    mapping = (observation.to_mapping() if isinstance(observation, Observation)
               else observation)
    if not isinstance(mapping, Mapping):
        raise NotDeterministic(
            f"an observation is a record or a mapping, not {type(observation).__name__}")
    return {name: mapping[name] for name in COMPARED_FIELDS if name in mapping}


def _lines(observations) -> list[str]:
    """The canonical line per observation, sorted: a set has no order.

    Sorted and NOT deduplicated. D10's collapse key is `(run_id, raw_value, zone)` and
    P4 enforces no uniqueness on it, so two identical readings may both exist and a
    digest that collapsed them would disagree with the table it validates.
    """
    return sorted(canonical_json(compared_form(one)) for one in observations)


def observation_set_bytes(observations) -> str:
    """The bytes rule 8 calls identical. One form per set, from `canonical_json`."""
    return canonical_json(_lines(observations))


def observation_set_digest(observations) -> str:
    """`observation_set_bytes`, addressed. What §3.4's cache compares cheaply."""
    return sha256_of(observation_set_bytes(observations))


def assert_identical_observation_sets(first_run, first_observations,
                                      second_run, second_observations) -> None:
    """Rule 8. Returns None when the two sets are identical; raises otherwise.

    A replay-key mismatch is raised as its own message: rule 8 says nothing at all
    about two different processes, and asserting it between them would be inventing a
    rule the SPEC does not state.
    """
    first_key, second_key = replay_key(first_run), replay_key(second_run)
    if first_key != second_key:
        raise NotDeterministic(
            f"these two runs are not one replay key -- {first_key} and {second_key}. "
            "Rule 8 compares the same process run twice; a comparison across "
            "processes is §8.5's diff, and it is made on observation_key")
    first_lines = Counter(_lines(first_observations))
    second_lines = Counter(_lines(second_observations))
    if first_lines == second_lines:
        return
    only_first = sorted((first_lines - second_lines).elements())
    only_second = sorted((second_lines - first_lines).elements())
    raise NotDeterministic(
        f"rule 8: two runs at replay key {first_key} produced different observation "
        f"sets.\nonly in the first run ({len(only_first)}):\n"
        + "\n".join(only_first)
        + f"\nonly in the second run ({len(only_second)}):\n"
        + "\n".join(only_second))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p4/test_p4_determinism.py -v`
Expected: PASS — 12 passed

- [ ] **Step 5: Commit**

```bash
git add src/evidence_shape/determinism.py tests/p4/test_p4_determinism.py
git commit -m "feat(P4): conformance rule 8 — the compared observation set, and the replay key"
```

---
### Task 16: The nineteen worked examples, and the coverage shortfall named (Done-means 5)

**Files:**
- Create: `src/evidence_shape/fixtures.py`
- Test: `tests/p4/test_p4_fixtures.py`

**Interfaces:**
- Consumes: every record module above, plus `evidence_shape.canonical` — `sha256_of`.
- Produces: `Fixture`, `FIXTURES: tuple[Fixture, ...]` (nineteen), `FIXTURE_OBSERVED_AT`, `by_number(number) -> Fixture`, `ZONES_WITH_A_WORKED_EXAMPLE`, `ZONES_WITHOUT_A_WORKED_EXAMPLE`, `SOURCE_TYPES_WITHOUT_A_WORKED_EXAMPLE`.

**Why this task exists at all.** *Done means* 9: *"a P5 author can write a conforming extractor from this document plus the fixtures without asking P4 a question"*, and *"P6 resolves `course = BUSIB 4300` from fixture 1 with no extractor present"*. P6, P7, P8 and P2 are all scheduled to be built before any extractor exists; what they build against is this module. It is the deliverable that makes *"the shape precedes the extractors"* mean something operational rather than aspirational.

**Golden records, not golden files.** Done-means 5 says *"golden files"*. This plan publishes them as a module of records instead, for one reason: every consumer named above imports them, and a JSON file would need a loader that reconstructs exactly the records this package already constructs — a second construction path for the same data, which is the duplication this project has paid for most. `canonical_json(observation.to_mapping())` produces the golden bytes from a record whenever a file is wanted. Recorded as a deviation in *SPEC vs design — conflicts found*.

**The coverage shortfall is named, not filled.** Done-means 5 asks for coverage of *"all 14 zones and all 14 source types"*. The SPEC's own worked-example table has nineteen rows and they reach **10 of the 15 zones** (the SPEC's zone table lists fifteen, not fourteen) and **13 of the 14 source types**. Missing zones: `path`, `header_footer`, `link`, `annotation`, `reference_list`. Missing source type: `contacts`. Authoring five more examples to close the gap would be P4 inventing worked examples the design does not give — and a fabricated `link` or `annotation` example is precisely the kind of thing six extractor authors would then implement against. So the module **computes** the shortfall from `FIXTURES` and publishes it, the test pins the exact list so it changes only when the SPEC gains examples, and the question goes to Joseph under *NEEDS JOSEPH*.

Note the shape of the gap: fixture 3's design case is *"§2.2's page-eighteen reference list"* and its golden zone is `body`, not `reference_list` — the SPEC's own reference-list example is filed under a different zone than the one it names. That is a fact about the table, reported here, not something this plan repairs.

**Two fixtures force a `text_units` row that is not bulk text.** Rule 10 requires a unit for *every* non-null `text_span`, and fixture 11's golden locator is `filename#0-6` — a span into a filename. The unit that satisfies it holds the filename as its text. §2.2, §2.4 and §2.7 describe `text_units` as the home for *bulk* text, so this is a real edge the contract does not discuss. The plan does what rule 10 says and reports the tension rather than narrowing rule 10, which would be a contract revision.

**No fixture carries a `signal_tier`, including the EXIF one.** §2.6's tier 1 is *"camera EXIF"* and tier 2 is *"capture time … reinforce it"*; `DateTimeOriginal` is camera EXIF **and** a capture time, so the design does not settle which tier it is. Task 13 already fixed P4's position: **which field belongs to which tier is P5's catalogue**, and P4 names no EXIF field. Assigning a tier here would author one entry of that catalogue inside a fixture, which is the quietest way possible to break the rule. Rule 11's three tiers already have their worked example in Task 13's test.

**Extractor names are illustrative.** `extractor_name` is free text, not a vocabulary; the SPEC supplies two (`pdf.text`, `ocr.apple_vision`) and a fixture must carry something. P5 owns the routing table and the real names (SPEC *Deferred*). Task 18's string-catalogue guards therefore exclude this module by name and say why: fixtures are data, and a guard that read them as code would have to forbid the SPEC's own examples.

- [ ] **Step 1: Write the failing test**

```python
# tests/p4/test_p4_fixtures.py
"""Done-means 5, and the coverage shortfall the SPEC's own examples leave."""
import pytest

from evidence_shape.canonical import canonical_json
from evidence_shape.conformance import validate_run
from evidence_shape.determinism import observation_set_digest
from evidence_shape.fixtures import (
    FIXTURES, SOURCE_TYPES_WITHOUT_A_WORKED_EXAMPLE, ZONES_WITHOUT_A_WORKED_EXAMPLE,
    ZONES_WITH_A_WORKED_EXAMPLE, by_number,
)
from evidence_shape.store import (
    observations_for_run, record_observation, record_run, record_text_unit,
    text_units_for_run,
)
from evidence_shape.vocabulary import SOURCE_TYPES, ZONES

#: The SPEC's worked-example table, column "locator", verbatim. Fixture 16's
#: locator is written there as `metadata:field=name` with "(in `key=dependencies`)"
#: beside it; the two segments serialize outermost-first.
GOLDEN_LOCATORS = {
    1: "heading:page=1/heading=2",
    2: "title:page=1",
    3: "body:page=18#12043-12051",
    4: "table:table=3/row=2/column=1",
    5: "heading:page=1/heading=1",
    6: "metadata:field=Producer",
    7: "metadata:field=DateTimeOriginal",
    8: "ocr:page=4/region=2#0-24",
    9: "manifest:entry=docs%2Ftranscript.pdf",
    10: "manifest:field=file_count",
    11: "filename#0-6",
    12: "table:sheet=2/row=7/column=3",
    13: "notes:slide=6#0-42",
    14: "metadata:field=Subject",
    15: "metadata:field=DTSTART",
    16: "metadata:key=dependencies/field=name",
    17: "transcript@252500-255200",
    18: "metadata:layer=3",
}


def test_there_are_nineteen_fixtures_numbered_as_the_spec_numbers_them():
    assert [fixture.number for fixture in FIXTURES] == list(range(1, 20))


def test_every_fixture_carries_its_golden_locator():
    for number, locator in GOLDEN_LOCATORS.items():
        observation, = by_number(number).observations
        assert observation.locator == locator, number


def test_fixture_19_emits_no_observation_and_says_so_on_the_run():
    # §2.9's safe default. The file is still indexed through its filesystem
    # observations (fixture 11's pattern), which this extractor does not write.
    nineteen = by_number(19)
    assert nineteen.observations == ()
    assert nineteen.run.completeness == "metadata_only"


def test_fixture_18_is_unreadable_and_still_carries_its_metadata_row(       ):
    # M3, and §2.9's "indexed-but-unreadable rather than silently treated as empty".
    eighteen = by_number(18)
    assert eighteen.run.completeness == "unreadable"
    assert len(eighteen.observations) == 1


def test_every_fixture_passes_the_conformance_gate():
    # The strongest form of Done-means 5: the golden records are not merely present,
    # they satisfy all twelve rules through the call an extractor author makes.
    for fixture in FIXTURES:
        assert validate_run(fixture.run, fixture.observations,
                            fixture.text_units) is fixture.run


def test_the_worked_examples_reach_ten_of_the_fifteen_zones():
    # Done-means 5 asks for all of them. The SPEC's own table does not supply them,
    # and P4 does not invent the missing five: a fabricated `link` or `annotation`
    # example is what six extractor authors would then implement against.
    assert ZONES_WITHOUT_A_WORKED_EXAMPLE == (
        "path", "header_footer", "link", "annotation", "reference_list")
    assert len(ZONES_WITH_A_WORKED_EXAMPLE) == 10
    assert set(ZONES_WITH_A_WORKED_EXAMPLE) | set(ZONES_WITHOUT_A_WORKED_EXAMPLE) == set(ZONES)


def test_the_worked_examples_reach_thirteen_of_the_fourteen_source_types():
    assert SOURCE_TYPES_WITHOUT_A_WORKED_EXAMPLE == ("contacts",)
    covered = {fixture.run.source_type for fixture in FIXTURES}
    assert covered == set(SOURCE_TYPES) - {"contacts"}


def test_the_page_eighteen_reference_list_is_filed_under_body():
    # Reported, not repaired: the SPEC's own reference-list example carries the
    # `body` zone, so `reference_list` has no worked example at all.
    observation, = by_number(3).observations
    assert observation.zone == "body"
    assert "reference list" in by_number(3).design_case


def test_the_filename_span_is_anchored_in_a_text_unit_holding_the_filename():
    # Rule 10 requires a unit for EVERY non-null text_span, and fixture 11's golden
    # locator is a span into a filename. §2.2/§2.4/§2.7 describe text_units as the
    # home for bulk text; this is the edge the contract does not discuss.
    fixture = by_number(11)
    unit, = fixture.text_units
    observation, = fixture.observations
    assert unit.container_path == ()
    assert unit.text.startswith(observation.raw_value)


def test_no_fixture_carries_a_signal_tier():
    # P4 names no EXIF field and authors no field-to-tier mapping; that catalogue is
    # P5's (SPEC Deferred). Rule 11's three tiers are exercised in Task 13.
    assert all(observation.signal_tier is None
               for fixture in FIXTURES for observation in fixture.observations)


def test_fixture_1_carries_the_context_the_walking_skeleton_depends_on():
    # B8a: the context term is what lets P6 resolve the skeleton fixture rather than
    # refuse it. P4 asserts the SPEC's literal string and holds no term list of its
    # own -- §3.5's five terms are P6's.
    observation, = by_number(1).observations
    assert observation.context_before == "Syllabus — "
    assert observation.context_after == " — Spring 2026"
    assert observation.raw_value == "BUSIB 4300"


def test_every_fixture_round_trips_through_canonical_bytes():
    for fixture in FIXTURES:
        for observation in fixture.observations:
            assert canonical_json(observation.to_mapping())


def test_the_fixtures_store_and_read_back_unchanged(p4_conn):
    # What P6, P7, P8 and P2 do with this module: load it into P1's database and
    # build against it with no extractor in existence.
    for fixture in FIXTURES:
        record_run(p4_conn, fixture.run)
        for unit in fixture.text_units:
            record_text_unit(p4_conn, unit)
        for observation in fixture.observations:
            record_observation(p4_conn, observation)

    for fixture in FIXTURES:
        stored = observations_for_run(p4_conn, fixture.run.run_id)
        assert (observation_set_digest(stored)
                == observation_set_digest(fixture.observations)), fixture.number
        assert len(text_units_for_run(p4_conn, fixture.run.run_id)) == len(fixture.text_units)


def test_by_number_rejects_a_number_the_spec_does_not_have():
    with pytest.raises(KeyError):
        by_number(20)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p4/test_p4_fixtures.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'evidence_shape.fixtures'`

- [ ] **Step 3: Write the implementation**

```python
# src/evidence_shape/fixtures.py
"""The SPEC's nineteen worked examples, as golden records.

Done-means 9: "a P5 author can write a conforming extractor from this document plus
the fixtures without asking P4 a question", and "P6 resolves `course = BUSIB 4300`
from fixture 1 with no extractor present". P6, P7, P8 and P2 are all built before any
extractor exists; this module is what they build against.

Records, not files. Every consumer imports them, and a JSON file would need a loader
that reconstructs exactly the records this package already constructs -- a second
construction path for one set of data. `canonical_json(observation.to_mapping())`
produces the golden bytes whenever a file is wanted.

The coverage shortfall is computed here and published, not filled: the SPEC's own
table reaches 10 of the 15 zones and 13 of the 14 source types, and inventing the
missing examples would author the very thing six extractor authors would implement
against.

No fixture carries a `signal_tier`. §2.6 makes `DateTimeOriginal` both "camera EXIF"
(tier 1) and a "capture time" (tier 2), so the design does not settle it, and which
field belongs to which tier is P5's catalogue (SPEC, Deferred). Extractor names here
are illustrative for the same reason: P5 owns the routing table and the real names.
"""
from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field

from evidence_shape.canonical import sha256_of
from evidence_shape.location import Location, Region, Segment, TextSpan, TimeSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.text_units import TextUnit
from evidence_shape.vocabulary import SOURCE_TYPES, ZONES

#: Pinned, so two readings of a fixture are never two readings of the wall clock.
FIXTURE_OBSERVED_AT = "2026-08-19T14:03:22+00:00"
FIXTURE_STARTED_AT = "2026-08-19T14:00:00+00:00"

#: Fixture 3's page: a reference list, elided down to the offsets the SPEC's golden
#: locator names. `body:page=18#12043-12051` is §2.2's page-eighteen reference.
_PAGE_18 = "…" * 12043 + "Columbia" + " University Press, 2019."

#: Fixture 8's OCR region. §7.8's admissions screenshot; the span is 0-24.
_OCR_REGION_4_2 = "Your Columbia University application status"

#: Fixture 11's unit. Rule 10 requires a unit for every span, and this span is into a
#: filename -- see the module tests for the tension that records.
_FILENAME = "Wash U.docx"

#: Fixture 13's speaker note. The golden span is 0-42, so the note is at least that
#: long; the words themselves are fixture text and carry no meaning to any rule.
_SLIDE_6_NOTES = "Application deadlines close on 1 December; mention the fee waiver."


@dataclass(frozen=True, slots=True)
class Fixture:
    """One row of the SPEC's worked-example table, as records."""

    number: int
    design_case: str
    run: ExtractionRun
    observations: tuple[Observation, ...] = ()
    text_units: tuple[TextUnit, ...] = ()


def _content_hash(number: int) -> str:
    return sha256_of(f"fixture-{number}")


def _run(number: int, *, source_type: str, extractor_name: str, analysis_tier: str,
         completeness: str = "complete", config: dict | None = None) -> ExtractionRun:
    return ExtractionRun(
        run_id=f"run-{number:02d}", file_id=f"file-{number:02d}",
        content_hash=_content_hash(number), extractor_name=extractor_name,
        extractor_version="1.0.0", source_type=source_type,
        analysis_tier=analysis_tier, config=config or {},
        completeness=completeness, started_at=FIXTURE_STARTED_AT,
        finished_at=FIXTURE_OBSERVED_AT)


def _observation(number: int, run: ExtractionRun, *, location: Location,
                 raw_value: str, reliability: str, **rest) -> Observation:
    return Observation(
        file_id=run.file_id, content_hash=run.content_hash,
        extractor_name=run.extractor_name, extractor_version=run.extractor_version,
        source_type=run.source_type, raw_value=raw_value, location=location,
        occurrence_count=rest.pop("occurrence_count", 1),
        observed_at=FIXTURE_OBSERVED_AT, reliability=reliability,
        run_id=run.run_id, **rest)


def _one(number: int, design_case: str, *, source_type: str, extractor_name: str,
         analysis_tier: str = "native", completeness: str = "complete",
         config: dict | None = None, units: tuple[TextUnit, ...] = (),
         **observation) -> Fixture:
    run = _run(number, source_type=source_type, extractor_name=extractor_name,
               analysis_tier=analysis_tier, completeness=completeness, config=config)
    return Fixture(number, design_case, run,
                   (_observation(number, run, **observation),),
                   tuple(TextUnit(run_id=run.run_id, container_path=path, text=text)
                         for path, text in units))


FIXTURES: tuple[Fixture, ...] = (
    # 1 -- §2.8 "page 1, heading 2"; §3.2's syllabus. The walking-skeleton fixture:
    # its context carries §3.5's "syllabus" term, which is what lets P6 resolve it
    # rather than refuse it (B8a).
    _one(1, '§2.8 "page 1, heading 2"; §3.2\'s syllabus',
         source_type="text_document", extractor_name="pdf.text",
         location=Location("heading", (Segment("page", 1),
                                       Segment("heading", 2,
                                               label="Course Information"))),
         raw_value="BUSIB 4300", normalized_value="BUSIB 4300",
         reliability="possible", occurrence_count=3,
         context_before="Syllabus — ", context_after=" — Spring 2026"),
    # 2 -- §3.2 "the PDF title".
    _one(2, '§3.2 "the PDF title"', source_type="text_document",
         extractor_name="pdf.text",
         location=Location("title", (Segment("page", 1),)),
         raw_value="BUSIB 4300 Syllabus", reliability="direct"),
    # 3 -- §2.2's page-eighteen reference list. Its zone is `body`: the SPEC's own
    # reference-list example is not filed under `reference_list`.
    _one(3, "§2.2's page-eighteen reference list", source_type="text_document",
         extractor_name="pdf.text",
         location=Location("body", (Segment("page", 18),),
                           text_span=TextSpan(12043, 12051)),
         raw_value="Columbia", reliability="possible",
         units=((( Segment("page", 18),), _PAGE_18),)),
    # 4 -- §2.8's DOCX example; §2.3 tables.
    _one(4, "§2.8's DOCX example; §2.3 tables", source_type="text_document",
         extractor_name="docx.text",
         location=Location("table", (Segment("table", 3), Segment("row", 2),
                                     Segment("column", 1))),
         raw_value="Wash U", reliability="possible"),
    # 5 -- §2.3's `Wash U.docx` heading.
    _one(5, "§2.3's Wash U heading", source_type="text_document",
         extractor_name="docx.text",
         location=Location("heading", (Segment("page", 1), Segment("heading", 1))),
         raw_value="Please tell us what you are interested in studying at college "
                   "and why.",
         reliability="possible"),
    # 6 -- §2.2: `direct` describes the SLOT, not the value's usefulness. P6
    # discounts it (§2.2, §2.3); P4 does not pre-discount it.
    _one(6, "§2.2 — direct describes the slot, not the value's usefulness",
         source_type="text_document", extractor_name="docx.metadata",
         location=Location("metadata", (Segment("field", label="Producer"),)),
         raw_value="python-docx", reliability="direct"),
    # 7 -- §2.8's EXIF example; §3.2's capture-date derivation. `signal_tier` is
    # null: §2.6 makes this both camera EXIF and a capture time, and the
    # field-to-tier catalogue is P5's.
    _one(7, "§2.8's EXIF example; §3.2's capture-date derivation",
         source_type="image", extractor_name="image.exif",
         location=Location("metadata",
                           (Segment("field", label="DateTimeOriginal"),)),
         raw_value="2026:07:17 14:03:22", reliability="direct"),
    # 8 -- §2.8's "OCR region"; §7.8's admissions screenshot. §2.7's bounding box
    # and confidence both have their worked example here; the geometry is fixture
    # geometry and the confidence is the SPEC's own 0.92.
    _one(8, '§2.8\'s "OCR region"; §7.8\'s admissions screenshot',
         source_type="ocr", extractor_name="ocr.apple_vision", analysis_tier="ocr",
         config={"dpi": 200, "languages": ["en"], "recognition": "accurate"},
         location=Location("ocr", (Segment("page", 4), Segment("region", 2)),
                           text_span=TextSpan(0, 24),
                           region=Region(0.08, 0.21, 0.55, 0.06, "norm")),
         raw_value="Your Columbia University", reliability="possible",
         confidence=0.92,
         units=(((Segment("page", 4), Segment("region", 2)), _OCR_REGION_4_2),)),
    # 9 -- §2.8's "manifest path"; §2.5's submission.zip. The label needs escaping.
    _one(9, "§2.8's manifest path; §2.5's submission.zip", source_type="archive",
         extractor_name="zip.manifest",
         location=Location("manifest",
                           (Segment("entry", label="docs/transcript.pdf"),)),
         raw_value="docs/transcript.pdf", reliability="direct"),
    # 10 -- §2.5 "file count" — D7's `field` segment on an archive property.
    _one(10, '§2.5 "file count"', source_type="archive",
         extractor_name="zip.manifest",
         location=Location("manifest", (Segment("field", label="file_count"),)),
         raw_value="37", reliability="direct"),
    # 11 -- §2.2, §2.9 filename as evidence. Rule 10 requires a unit for this span,
    # and the unit that satisfies it holds the filename.
    _one(11, "§2.2, §2.9 filename as evidence", source_type="filesystem",
         extractor_name="fs.basic", analysis_tier="filesystem",
         location=Location("filename", (), text_span=TextSpan(0, 6)),
         raw_value="Wash U", reliability="possible",
         units=(((), _FILENAME),)),
    # 12 -- §2.9 "dates or identifiers from labeled cells". Segment-kind rule 3: the
    # native address `C7` is the column segment's label, not a separate kind.
    _one(12, '§2.9 "dates or identifiers from labeled cells"',
         source_type="spreadsheet", extractor_name="xlsx.cells",
         location=Location("table", (Segment("sheet", 2, label="Applications"),
                                     Segment("row", 7),
                                     Segment("column", 3, label="C7"))),
         raw_value="2025", reliability="possible"),
    # 13 -- §2.9 presentations.
    _one(13, "§2.9 presentations", source_type="presentation",
         extractor_name="pptx.notes",
         location=Location("notes", (Segment("slide", 6, label="Deadlines"),),
                           text_span=TextSpan(0, 42)),
         raw_value=_SLIDE_6_NOTES[:42], reliability="possible",
         units=(((Segment("slide", 6),), _SLIDE_6_NOTES),)),
    # 14 -- §2.9 email.
    _one(14, "§2.9 email", source_type="email", extractor_name="email.headers",
         location=Location("metadata", (Segment("field", label="Subject"),)),
         raw_value="Columbia Application — Next Steps", reliability="direct"),
    # 15 -- §2.9 calendar.
    _one(15, "§2.9 calendar", source_type="calendar", extractor_name="ics.fields",
         location=Location("metadata", (Segment("field", label="DTSTART"),)),
         raw_value="20260717T140000Z", reliability="direct"),
    # 16 -- §2.4, §2.9 package manifests. D7: `key` carries the structured-data key
    # path and `field` the format's own slot name, outermost first.
    _one(16, "§2.4, §2.9 package manifests", source_type="code_structured",
         extractor_name="pkg.manifest",
         location=Location("metadata", (Segment("key", label="dependencies"),
                                        Segment("field", label="name"))),
         raw_value="react", reliability="direct"),
    # 17 -- §2.9 audio/video. A caption at 04:12.5-04:15.2: no page and no
    # document-text offset, which is what `time_span` exists for.
    _one(17, "§2.9 audio/video", source_type="audio_video",
         extractor_name="av.transcript",
         location=Location("transcript", (), time_span=TimeSpan(252500, 255200)),
         raw_value="and the Columbia application is due in December",
         reliability="possible"),
    # 18 -- §2.9 design/creative. The run is `unreadable` and STILL carries this
    # metadata-level row: §2.9's "indexed-but-unreadable" (M3).
    _one(18, "§2.9 design/creative, indexed-but-unreadable (M3)",
         source_type="design_creative", extractor_name="psd.metadata",
         completeness="unreadable",
         location=Location("metadata", (Segment("layer", 3),)),
         raw_value="Background", reliability="direct"),
    # 19 -- §2.9's safe default for disk images, executables, databases, encrypted
    # containers, damaged files and unknown binary. No observation from THIS
    # extractor; the file is still indexed through fixture 11's pattern.
    Fixture(19, "§2.9's metadata_only safe default",
            _run(19, source_type="opaque_binary", extractor_name="binary.none",
                 analysis_tier="native", completeness="metadata_only")),
)

_BY_NUMBER = {fixture.number: fixture for fixture in FIXTURES}

#: Computed, never hand-listed, so the shortfall cannot drift from the fixtures.
_COVERED_ZONES = {observation.zone for fixture in FIXTURES
                  for observation in fixture.observations}

ZONES_WITH_A_WORKED_EXAMPLE: tuple[str, ...] = tuple(
    zone for zone in ZONES if zone in _COVERED_ZONES)

#: Done-means 5 asks for all of them; the SPEC's table supplies these none.
ZONES_WITHOUT_A_WORKED_EXAMPLE: tuple[str, ...] = tuple(
    zone for zone in ZONES if zone not in _COVERED_ZONES)

SOURCE_TYPES_WITHOUT_A_WORKED_EXAMPLE: tuple[str, ...] = tuple(
    source_type for source_type in SOURCE_TYPES
    if source_type not in {fixture.run.source_type for fixture in FIXTURES})


def by_number(number: int) -> Fixture:
    """The SPEC's own numbering, so a reviewer can check one row against one table."""
    return _BY_NUMBER[number]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p4/test_p4_fixtures.py -v`
Expected: PASS — 14 passed

- [ ] **Step 5: Commit**

```bash
git add src/evidence_shape/fixtures.py tests/p4/test_p4_fixtures.py
git commit -m "feat(P4): the nineteen worked examples as golden records, and the named coverage shortfall"
```

---
### Task 17: §2.8's four prohibitions and the three derived ones (Done-means 6)

**Files:**
- Test: `tests/p4/test_p4_prohibitions.py`

**Interfaces:**
- Consumes: every module above. No new source.
- Produces: the negative half of the contract, as standing tests.

**Done-means 6, in full:** *"Negative tests pass: an extractor cannot write `validated` / `llm_supported` / `user_confirmed` / `rejected`; an observation cannot reference two files; an observation cannot carry a path, domain, field name, group, node or plan reference; an observation cannot record an absence or a conflict (§2.6); a `complete` zero-observation run, an `unsupported` zero-observation run and a `metadata_only` run are three distinguishable states (§2.4, §2.9)."*

**This is not Task 13 again.** Task 13 tests that the **validator** reports a violation. This task tests that the **shape itself** makes the thing impossible — the record constructor refuses it, the table has no column for it, the trigger aborts it. The difference matters because a validator is a call an author can forget and a schema is not: §2.8's prohibitions have to survive an extractor that never runs the gate.

**§2.8's four, verbatim:** *"Extraction does not create a final folder path, invent domains, merge all files that share one string, or treat model output as proof."* And the three the SPEC derives from outside §2.8 because six extractors need them: **no negative observations** (§2.6 — absence lives on the run record or nowhere), **no conflict observations and no resolution of one** (§2.6 — two rows with two `signal_tier` values, and §3.7's margin rule is P6's), **no plan-version state** (§3.14, §8.8), **no deletion** (§8.2, §8.7 — a rejected proposal must keep the evidence that produced it).

**`zone = "path"` is not a folder path.** It addresses §2.9's parent-folder context — where the file *is* — and the prohibition is on a destination. The two are one word and two concepts, so the test states the distinction rather than leaving a reviewer to infer it.

- [ ] **Step 1: Write the failing test**

```python
# tests/p4/test_p4_prohibitions.py
"""Done-means 6. §2.8's four prohibitions and the three the SPEC derives.

Task 13 tests that the validator REPORTS a violation. This file tests that the shape
makes the thing impossible: the constructor refuses it, the table has no column for
it, the trigger aborts it. A validator is a call an author can forget; a schema is not.
"""
import pytest

from evidence_shape.location import Location, Segment
from evidence_shape.observation import (
    MalformedObservation, OBSERVATION_ROW_FIELDS, Observation,
)
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import (
    observations_for_run, record_observation, record_run, record_text_unit,
    runs_for_file,
)
from evidence_shape.text_units import TextUnit
from evidence_shape.vocabulary import NotInVocabulary, ZONES

#: Every name a destination, a domain, a product field, a grouping or a plan would
#: have to be stored under. §2.8, §3.11, §3.12, §3.14, §8.8.
FORBIDDEN_COLUMNS = (
    "proposed_path", "destination", "destination_node", "target_path", "folder",
    "domain", "domain_id", "category", "field_name", "fact", "facet",
    "group_id", "node_id", "template_id", "plan_id", "plan_version_id",
    "handling_class", "preferred", "conflict", "resolution", "absent",
)

P4_TABLES = ("evidence", "extraction_runs", "text_units")


def _run(run_id="r1", file_id="f1", *, completeness="complete", number=1):
    return ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=f"sha256:abc{number}",
        extractor_name="pdf.text", extractor_version="3.1.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness=completeness, started_at="2026-08-19T14:00:00+00:00")


def _observation(run, **overrides):
    fields = dict(
        file_id=run.file_id, content_hash=run.content_hash,
        extractor_name=run.extractor_name, extractor_version=run.extractor_version,
        source_type=run.source_type, raw_value="Columbia",
        location=Location("body", (Segment("page", 1),)), occurrence_count=1,
        observed_at="2026-08-19T14:03:22+00:00", reliability="possible",
        run_id=run.run_id)
    fields.update(overrides)
    return Observation(**fields)


def _columns(conn, table):
    return [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]


# ── §2.8: "does not treat model output as proof" ──────────────────────────────

def test_an_extractor_cannot_write_a_fact_layer_reliability_state():
    # D11, and §3.5: rules produce validated facts, the LLM produces LLM-supported
    # facts, the user produces user-confirmed facts. None of them is an extractor.
    run = _run()
    for fact_state in ("validated", "llm_supported", "user_confirmed", "rejected"):
        with pytest.raises(NotInVocabulary):
            _observation(run, reliability=fact_state)


def test_the_refusal_is_in_the_record_not_only_in_the_validator():
    # An extractor that never calls validate_observation still cannot write one.
    with pytest.raises(NotInVocabulary):
        Observation(
            file_id="f1", content_hash="sha256:abc", extractor_name="llm.dossier",
            extractor_version="1.0.0", source_type="text_document",
            raw_value="Columbia", location=Location("body", (Segment("page", 1),)),
            occurrence_count=1, observed_at="2026-08-19T14:03:22+00:00",
            reliability="llm_supported", run_id="r1")


# ── §2.8: "does not create a final folder path" / "invent domains" ────────────

def test_no_p4_table_has_a_destination_domain_group_node_or_plan_column(p4_conn):
    for table in P4_TABLES:
        columns = set(_columns(p4_conn, table))
        for forbidden in FORBIDDEN_COLUMNS:
            assert forbidden not in columns, f"{table}.{forbidden}"


def test_the_observation_record_is_a_closed_field_set():
    # There is nowhere to put one even as an extra key: rule 6 rejects an unknown
    # field, and the row field list is the whole surface.
    assert "domain" not in OBSERVATION_ROW_FIELDS
    assert "proposed_path" not in OBSERVATION_ROW_FIELDS
    with pytest.raises(TypeError):
        _observation(_run(), domain="education")


def test_the_path_zone_addresses_where_the_file_is_not_where_it_should_go():
    # One word, two concepts. §2.9's parent-folder context is evidence; a
    # destination is P11's and does not exist here.
    assert "path" in ZONES
    observation = _observation(
        _run(), location=Location("path", (Segment("field", label="parent"),)),
        raw_value="Columbia Applications")
    assert observation.zone == "path"
    assert not hasattr(observation, "proposed_path")


# ── §2.8: "does not merge all files that share one string" ────────────────────

def test_an_observation_references_exactly_one_file():
    with pytest.raises(MalformedObservation):
        _observation(_run(), file_id=["f1", "f2"])


def test_two_files_sharing_a_raw_value_share_nothing_structurally(p4_conn):
    first, second = _run("r1", "f1", number=1), _run("r2", "f2", number=2)
    record_run(p4_conn, first)
    record_run(p4_conn, second)
    record_observation(p4_conn, _observation(first))
    record_observation(p4_conn, _observation(second))

    one, = observations_for_run(p4_conn, "r1")
    two, = observations_for_run(p4_conn, "r2")
    assert one.raw_value == two.raw_value == "Columbia"
    assert one.file_id != two.file_id
    # Not even the citation handle merges them: the key is content-addressed, and
    # two files are two contents. Any link between them is P6's or P9's.
    assert one.observation_key != two.observation_key


def test_p4_owns_three_tables_and_no_table_that_links_two_files(p4_conn):
    names = {row[0] for row in p4_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert set(P4_TABLES) <= names
    for suspicious in ("evidence_links", "value_matches", "duplicates", "groups"):
        assert suspicious not in names


# ── §2.6, derived: no absence, no conflict, no resolution of one ──────────────

def test_an_observation_cannot_record_an_absence():
    # A count of zero IS an absence, and absence lives on the run record or nowhere.
    with pytest.raises(MalformedObservation):
        _observation(_run(), occurrence_count=0)


def test_a_complete_run_that_emitted_nothing_is_how_absence_is_recorded(p4_conn):
    # §2.6's "no EXIF" is exactly this case: no field is added for it and no
    # observation is written for it.
    record_run(p4_conn, _run(completeness="complete"))
    assert observations_for_run(p4_conn, "r1") == []
    stored, = runs_for_file(p4_conn, "f1")
    assert stored.completeness == "complete"
    assert stored.observation_count == 0


def test_an_observation_cannot_carry_a_conflict_or_its_resolution():
    # §2.6's conflicting signals are TWO observations with two signal_tier values.
    # There is one raw_value slot, one location slot, and no third "conflict" row.
    with pytest.raises(MalformedObservation):
        _observation(_run(), raw_value=["Canon EOS R6", "1920x1080"])
    with pytest.raises(TypeError):
        _observation(_run(), conflicts_with="obs-2")


# ── §8.2 / §8.7, derived: superseded, never deleted ───────────────────────────

def test_an_observation_is_superseded_never_deleted(p4_conn):
    # §8.7 requires a rejected proposal to be stored WITH the evidence that produced
    # it; deleting evidence decays every negative example that depends on it.
    record_run(p4_conn, _run())
    record_observation(p4_conn, _observation(_run()))
    with pytest.raises(Exception):
        p4_conn.execute("DELETE FROM evidence")


def test_a_run_and_a_text_unit_are_never_deleted_either(p4_conn):
    record_run(p4_conn, _run())
    record_text_unit(p4_conn, TextUnit(run_id="r1",
                                       container_path=(Segment("page", 1),),
                                       text="Syllabus — BUSIB 4300"))
    with pytest.raises(Exception):
        p4_conn.execute("DELETE FROM text_units")
    with pytest.raises(Exception):
        p4_conn.execute("DELETE FROM extraction_runs")


# ── §2.4 / §2.9: three states that must stay distinguishable ──────────────────

def test_the_three_zero_observation_states_are_distinguishable(p4_conn):
    # §2.4: "an empty extraction result is different from an extractor that does not
    # yet exist." §2.9 adds the third: metadata_only is a deliberate policy stop.
    for index, (run_id, completeness) in enumerate((
            ("r-complete", "complete"),
            ("r-unsupported", "unsupported"),
            ("r-metadata-only", "metadata_only"))):
        record_run(p4_conn, _run(run_id, "f1", completeness=completeness,
                                 number=index))

    stored = {run.run_id: run for run in runs_for_file(p4_conn, "f1")}
    assert len(stored) == 3
    assert {run.completeness for run in stored.values()} == {
        "complete", "unsupported", "metadata_only"}
    for run in stored.values():
        assert run.observation_count == 0
        assert observations_for_run(p4_conn, run.run_id) == []
    # The three differ in exactly one field, and it is the field §2.4 requires.
    assert (stored["r-complete"].completeness
            != stored["r-unsupported"].completeness
            != stored["r-metadata-only"].completeness)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p4/test_p4_prohibitions.py -v`
Expected: FAIL if any prohibition is unenforced; otherwise PASS. If every prior task was written as specified, the only expected failures are ones this task exists to surface.

- [ ] **Step 3: Fix whatever the tests catch**

No new module. If one fires, the fix is in the module that let it through — a missing constructor check, a column that should not exist, a trigger that was not created. Never in the test: these seven sentences are the SPEC's negative half.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p4/test_p4_prohibitions.py -v`
Expected: PASS — 14 passed

- [ ] **Step 5: Commit**

```bash
git add tests/p4/test_p4_prohibitions.py
git commit -m "test(P4): §2.8's four prohibitions and the three derived, enforced by the shape"
```

---
### Task 18: The no-invention guard, and every open question held open

**Files:**
- Test: `tests/p4/test_p4_no_invention.py`

**Interfaces:**
- Consumes: every module above, plus `database_agent.budget` — `CEILING_KEYS`; `database_agent.events` — `RESERVED_EVENT_TYPES`; `database_agent.supersede` — `SUPERSEDE_COLUMNS`.
- Produces: the standing guard the rest of the build must keep green.

**Two obligations, both negative.** First: every open question in P4's SPEC gets a test that names it and fails the moment someone answers it in code instead of in a SPEC. Second: P4 invents no threshold, no ceiling, no gazetteer, no positional weight, no routing table, no catalogue of strings and no vocabulary member the design does not spell.

**The guard-token trap, and how this file avoids it.** `assert "gazetteer" not in source` matches a **docstring that says P4 authors no gazetteer** — which is the opposite of a violation. Four tasks on this project have been broken by exactly that, and P4's modules are unusually prose-heavy because they quote the design at every decision. So every token guard below runs against `code_only(path)`: the module re-emitted through `ast.unparse` with its docstrings removed. `ast.unparse` drops comments for free; the walk drops docstrings; what is left is code.

That still leaves string literals that *are* code — `CONFORMANCE_RULES`' published rule text, and every `Violation` message. Those legitimately contain `domain`, `destination`, `template`, `node`, `group` and `EXIF`, because §2.8's prohibitions are quoted where they are enforced. **`plan` is a substring of `explanation`.** The token lists below were checked against the real package before being written, and every one of them is empirically absent from real code; the concepts those unusable words name are guarded structurally instead — by Task 17's column guard, and by the import and constant guards here.

And a published *question* is text too. `OPEN_QUESTIONS["OQ6"]` contains the words *iCloud dataless* because that is the question P4 is **holding open** — a token guard reading it fires on the very thing it exists to protect. That obligation is therefore guarded on `identifiers()`: every name the package binds or reads, and no string literal at all. A question is text; an answer would be a name.

**Where a guard cannot be written, this task says so instead of faking one.** An absence written *inside* `raw_value` as a string is undetectable without a list of forbidden strings, and authoring one would be the invention. Task 13 records that split in `CONFORMANCE_RULES[12]`; nothing here pretends otherwise.

- [ ] **Step 1: Write the failing test**

```python
# tests/p4/test_p4_no_invention.py
"""The standing record that P4 answers no open question in code, and invents nothing.

Every token guard runs against `code_only`: the module with its docstrings and
comments removed. `assert "gazetteer" not in source` otherwise matches the docstring
that says P4 authors no gazetteer, which is the opposite of a violation.
"""
import ast
import inspect
from pathlib import Path

import pytest

import evidence_shape
from database_agent.budget import CEILING_KEYS
from database_agent.events import RESERVED_EVENT_TYPES
from database_agent.supersede import SUPERSEDE_COLUMNS

from evidence_shape.authorship import (
    EXTRACTION_EVENT, OCR_EVENT, RUN_EVENT_TYPES, UnauthoredEvent, check_author,
    event_defaults,
)
from evidence_shape.observation import (
    OBSERVATION_FIELDS, OBSERVATION_ROW_FIELDS, observation_key,
)
from evidence_shape.text_units import TEXT_UNIT_FIELDS
from evidence_shape.vocabulary import (
    ANALYSIS_TIERS, COMPLETENESS, EXTRACTOR_RELIABILITY_STATES, OPEN_QUESTIONS,
    RELIABILITY_STATES, SIGNAL_TIERS, SOURCE_TYPES,
)

SOURCE_DIR = Path(evidence_shape.__file__).parent

#: Data, not code. The nineteen worked examples are the SPEC's own table, and a
#: format-catalogue guard that read them as code would have to forbid the SPEC's own
#: examples. Every structural guard below still covers this module.
FIXTURE_DATA = "fixtures.py"


def modules():
    return sorted(path for path in SOURCE_DIR.glob("*.py")
                  if path.name != "__init__.py")


def code_only(path: Path) -> str:
    """The module's source with docstrings and comments removed."""
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if (isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                              ast.AsyncFunctionDef))
                and body and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)):
            node.body = body[1:] or [ast.Pass()]
    return ast.unparse(tree)


def all_code(*, skip=()) -> str:
    return "\n".join(code_only(path) for path in modules()
                     if path.name not in skip)


def identifiers(*, skip=()) -> set[str]:
    """Every name the package binds or reads -- and no string literal.

    Some obligations cannot be guarded on text at all, because the published contract
    quotes the very words a violation would use: `OPEN_QUESTIONS["OQ6"]` contains
    "iCloud dataless" because that is the question being HELD OPEN. A question is
    text; an answer would be a name.
    """
    names: set[str] = set()
    for path in modules():
        if path.name in skip:
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(node.name)
            elif isinstance(node, ast.Name):
                names.add(node.id)
            elif isinstance(node, ast.Attribute):
                names.add(node.attr)
            elif isinstance(node, ast.arg):
                names.add(node.arg)
            elif isinstance(node, ast.keyword) and node.arg:
                names.add(node.arg)
    return names


def module_constants(path: Path):
    """Top-level `NAME = <literal>` bindings, as (name, value-node) pairs."""
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
        elif isinstance(node, ast.AnnAssign):
            target = node.target
        else:
            continue
        if isinstance(target, ast.Name) and node.value is not None:
            yield target.id, node.value


# ── P4 runs no extractor, opens no file, and reaches no network ───────────────

def test_p4_imports_nothing_outside_the_stdlib_and_p1():
    # "P4 runs no extractor. §2.8 is a shape, not a reader." The import graph is the
    # exact form of that claim: no format library can be reached from here.
    allowed = {"__future__", "collections", "dataclasses", "datetime", "hashlib",
               "json", "sqlite3", "types", "unicodedata", "uuid",
               "database_agent", "evidence_shape"}
    for path in modules():
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for name in names:
                assert name.split(".")[0] in allowed, f"{path.name}: {name}"


def test_p4_opens_no_file():
    # Every test in this part builds its records in memory or from a fixture string.
    # That is what makes the whole part testable before P5 exists.
    source = all_code()
    for token in ("pathlib", "Path(", "open(", "os.", "io."):
        assert token not in source, token


def test_p4_sniffs_no_format_and_holds_no_routing_table():
    # SPEC Deferred: the MIME/signature -> extractor routing table is P5's, and
    # "which structured strings each extractor should recognize" is P5's per format.
    source = all_code(skip=(FIXTURE_DATA,))
    for token in ("mimetypes", "magic", "%PDF", "zipfile", "tarfile", "openpyxl",
                  "PyPDF", "PIL", "pytesseract", "csv", "docx", "pdf", "exif"):
        assert token not in source, token


def test_p4_reaches_no_network_and_prompts_no_model():
    # §2.8: extraction "does not treat model output as proof". P8 owns the model.
    source = all_code()
    for token in ("urllib", "requests", "socket", "prompt", "openai", "anthropic"):
        assert token not in source, token


# ── P4 invents no value ──────────────────────────────────────────────────────

def test_the_package_publishes_no_numeric_constant_outside_its_one_allowlist():
    # SHAPE_VERSION is D2's (a vocabulary change is a contract revision plus a bump);
    # SIGNAL_TIERS is §2.6's three levels. There is no third, and in particular no
    # §8.6 ceiling: those numbers are configuration and P1 owns the keys.
    allowed = {"SHAPE_VERSION", "SIGNAL_TIERS"}
    found = set()
    for path in modules():
        for name, value in module_constants(path):
            numbers = ([value] if isinstance(value, ast.Constant)
                       else list(value.elts) if isinstance(value, ast.Tuple) else [])
            if numbers and all(isinstance(node, ast.Constant)
                               and isinstance(node.value, (int, float))
                               and not isinstance(node.value, bool)
                               for node in numbers):
                found.add(name)
    assert found == allowed


def test_p4_authors_no_threshold_weight_gazetteer_or_template_library():
    # SPEC Deferred, every row of it: gazetteer contents (§3.7), positional weights
    # per zone (§3.7), the 200-300 domain template library (§5.7), the residual
    # library (§7.2-§7.4), date-candidate patterns (§3.10).
    source = all_code()
    for token in ("GAZETTEER", "gazetteer", "THRESHOLD", "threshold", "CEILING",
                  "MAX_", "_LIMIT", "WEIGHT", "weight", "TEMPLATE_LIBRARY",
                  "RESIDUAL", "re.compile", "import re"):
        assert token not in source, token


def test_the_context_budget_is_caller_supplied_and_p4_holds_no_length():
    # B4, ratified 2026-08-20: the ceiling now HAS a home -- P1's sixteenth key
    # `evidence.context_window` -- and it belongs in the run's `config` so it is
    # fingerprinted (two runs at different context widths must not look identical to
    # §3.4's cache key). What has not changed is that P4 holds no NUMBER: the value is
    # read from P1 by the caller and arrives as data. That is the claim this guards.
    assert "context_truncated" in OBSERVATION_FIELDS
    assert "evidence.context_window" in CEILING_KEYS      # P1 owns the ceiling
    assert "evidence.context_window" not in all_code()    # P4 does not read it itself
    source = all_code()
    for token in ("truncate(", "MAX_CONTEXT", "CONTEXT_LENGTH", "context_length"):
        assert token not in source, token


def test_p4_normalizes_nothing():
    # RAW-1 and §2.8: raw_value is "exactly that wording" -- no case folding, no
    # Unicode normalization, no whitespace collapse, no trimming. `unicodedata` is
    # imported for one call, `category(...) == "Cc"`, which is control-character
    # detection inside locator escaping and rewrites nothing.
    source = all_code()
    for token in ("unicodedata.normalize", "NFC", "NFD", "casefold", ".lower()",
                  ".upper()"):
        assert token not in source, token


def test_there_is_no_seventh_vocabulary():
    # Six closed vocabularies, published as ten names because three are derived
    # subsets. A seventh appearing here is a contract revision, not an edit.
    published = set()
    for name, value in module_constants(SOURCE_DIR / "vocabulary.py"):
        if (isinstance(value, ast.Tuple) and value.elts
                and all(isinstance(node, ast.Constant) and isinstance(node.value, str)
                        for node in value.elts)):
            published.add(name)
    assert published == {
        "ZONES", "INDEXED_SEGMENT_KINDS", "LABEL_SEGMENT_KINDS", "SOURCE_TYPES",
        "RELIABILITY_STATES", "EXTRACTOR_RELIABILITY_STATES", "COMPLETENESS",
        "ZERO_OBSERVATION_COMPLETENESS", "ANALYSIS_TIERS", "REGION_UNITS"}


# ── P4 authors no event ──────────────────────────────────────────────────────

def test_p4_supplies_no_default_author_and_refuses_p1():
    # M8: "The acting part authors; P1 writes. P1 appends no event on its own
    # initiative." §8.2 requires the responsible subsystem on every event.
    with pytest.raises(UnauthoredEvent):
        check_author("")
    with pytest.raises(UnauthoredEvent):
        check_author("P1")
    with pytest.raises(TypeError):
        event_defaults(component_version="1.0.0", event_type=EXTRACTION_EVENT)


def test_the_subsystem_field_is_set_in_exactly_one_module():
    for path in modules():
        if path.name == "authorship.py":
            continue
        assert "subsystem" not in code_only(path), path.name


def test_p4_registers_no_event_type_and_adds_no_event_field():
    # P1 Contract out §3, rule 4: registration is a spec-level act. Both names are
    # already among §8.2's nineteen. MINOR 1: §8.2 lists eleven fields and P4 adds none.
    assert "register" not in all_code()
    assert set(RUN_EVENT_TYPES) <= set(RESERVED_EVENT_TYPES)


def test_minor_2_the_ocr_event_and_the_ocr_vocabulary_member_are_two_things():
    # §8.2 spells the event `OCR`; `source_type` and `analysis_tier` spell their own
    # member `ocr`. Neither is a case variant of the other and nothing folds one into
    # the other -- P1's writer validates against §8.2's spelling and would reject it.
    assert OCR_EVENT == "OCR"
    assert OCR_EVENT not in SOURCE_TYPES
    assert OCR_EVENT not in ANALYSIS_TIERS
    assert "ocr" in SOURCE_TYPES and "ocr" in ANALYSIS_TIERS
    assert "ocr" not in RESERVED_EVENT_TYPES


def test_minor_3_the_third_supersede_column_is_supersede_reason():
    assert SUPERSEDE_COLUMNS == ("supersedes", "superseded_by", "supersede_reason")
    assert set(SUPERSEDE_COLUMNS) <= set(OBSERVATION_ROW_FIELDS)
    assert "supersession_reason" not in all_code()
    # M1: `preferred` is P1's fourth column and is NOT adopted. §8.2 gives preference
    # to the resolver and §3.2 places the resolver after extraction.
    assert "preferred" not in OBSERVATION_ROW_FIELDS


def test_minor_8_the_citation_handle_excludes_the_extractor_version_on_purpose():
    # NOT a bug to be fixed. §8.5's replay diff compares a new extractor version
    # against a prior result for the same content; a key carrying the version would
    # make every row a false diff and leave nothing to diff against.
    parameters = inspect.signature(observation_key).parameters
    assert set(parameters) == {"content_hash", "extractor_name", "locator", "raw_value"}
    assert "extractor_version" not in parameters


# ── Every open question, held open ───────────────────────────────────────────

def test_the_four_open_questions_are_published_and_none_is_answered():
    # OQ1 closed as I4 (analysis_tier's four values); OQ2 closed 2026-08-20.
    # Both are deliberately absent.
    assert sorted(OPEN_QUESTIONS) == ["OQ3", "OQ4", "OQ5", "OQ6"]
    assert "OQ1" not in OPEN_QUESTIONS   # closed as I4
    assert "OQ2" not in OPEN_QUESTIONS   # closed 2026-08-20
    for key, text in OPEN_QUESTIONS.items():
        assert text.strip().endswith("?"), key


def test_oq2_ratified_the_content_hash_owns_the_observation(p4_conn):
    # OQ2 CLOSED, ratified 2026-08-20: the content hash owns the observation, and two
    # file records sharing a hash share one observation set. §2.8 still requires a file
    # identifier, so both fields stay — but `file_id` is a way in, not the owner.
    # These are the same assertions this test made while the question was open, and
    # they are now REQUIRED rather than merely permitted: a foreign key to `files`
    # would make the file record the owner in DDL, which is the answer we did not take.
    assert "file_id" in OBSERVATION_FIELDS
    assert "content_hash" in OBSERVATION_FIELDS
    referenced = {row[2] for row in p4_conn.execute(
        "PRAGMA foreign_key_list(evidence)")}
    assert referenced == {"extraction_runs"}


def test_oq3_stays_open_p4_defines_no_second_reliability_vocabulary():
    # "Do observations and facts share one reliability vocabulary?" P4 reuses §3.13's
    # six and restricts extractors to two of them (D11). If P6 defines a separate
    # observation-level vocabulary, D11 and conformance rule 3 change -- and this
    # test is what makes that a visible contract revision.
    assert len(RELIABILITY_STATES) == 6
    assert set(EXTRACTOR_RELIABILITY_STATES) < set(RELIABILITY_STATES)


def test_oq4_stays_open_p4_stores_no_handling_class(p4_conn):
    # "Is the §8.4 handling class stored per observation or only per file?" P4 adds no
    # privacy field (P7 owns handling classes) and instead guarantees BOTH
    # granularities are addressable, so either answer stays implementable.
    for table in ("evidence", "extraction_runs", "text_units"):
        columns = {row[1] for row in p4_conn.execute(f"PRAGMA table_info({table})")}
        assert not columns & {"handling_class", "sensitivity", "sensitivity_state",
                              "privacy_class", "redaction"}
    assert "observation_key" in OBSERVATION_FIELDS      # addressable per observation
    assert "file_id" in OBSERVATION_FIELDS              # joinable per file
    assert TEXT_UNIT_FIELDS[:2] == ("run_id", "container_path")   # D12's key


def test_oq5_stays_open_p4_publishes_no_user_authored_route():
    # "May a user author or correct an observation directly?" §8.7 enumerates user
    # actions and none is "correct an extracted value". P4 supplies no writer for one
    # and no reliability state an extractor could reach that would mean it.
    import evidence_shape.store as store
    writers = sorted(name for name in dir(store)
                     if name.startswith(("record_", "supersede_", "correct_",
                                         "amend_", "edit_")))
    assert writers == ["record_observation", "record_run", "record_run_event",
                       "record_text_unit", "supersede_chain", "supersede_observation"]
    assert "user_confirmed" not in EXTRACTOR_RELIABILITY_STATES


def test_oq6_closed_the_ninth_completeness_is_dataless():
    # "What completeness does a source that is not on this machine carry?" None of the
    # eight fit: deferred is budget exhaustion, unreadable is encrypted-or-damaged,
    # metadata_only is a format decision. Ratified 2026-08-20: a ninth, and it is
    # `dataless` -- the word P1 (`DatalessFileRefused`), P3 (`scan_agent.dataless`)
    # and 11-ops-runtime §5 already use. Coining `not_local` beside them would have
    # been two vocabularies for one concept, this project's most expensive defect.
    assert len(COMPLETENESS) == 9
    assert COMPLETENESS[-1] == "dataless"
    # that it forbids observations is pinned in test_p4_vocabulary.py, which owns
    # ZERO_OBSERVATION_COMPLETENESS -- not restated here across files.
    for not_coined in ("not_downloaded", "offline", "remote", "evicted", "unavailable",
                       "not_local", "cloud_only"):
        assert not_coined not in COMPLETENESS
    # Guarded on NAMES, not on text: OPEN_QUESTIONS["OQ6"] quotes "iCloud dataless"
    # because that is the question being held open. A detection would be a name.
    lowered = {name.lower() for name in identifiers()}
    for token in ("dataless", "icloud", "downloaded", "evicted"):
        assert not any(token in name for name in lowered), token


def test_the_signal_tier_hierarchy_is_carried_but_not_catalogued():
    # M2 puts §2.6's three levels on the record. WHICH field belongs to which tier is
    # P5's catalogue (SPEC Deferred), and P4 names no EXIF field: enumerating one
    # would be the gazetteer the hard rules forbid. Task 16's fixture 7 is the case
    # that proves it -- DateTimeOriginal is both "camera EXIF" and a "capture time".
    assert SIGNAL_TIERS == (1, 2, 3)
    source = all_code(skip=(FIXTURE_DATA,))
    for field_name in ("DateTimeOriginal", "GPSLatitude", "Make", "Model",
                       "PixelXDimension", "Software"):
        assert field_name not in source, field_name
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p4/test_p4_no_invention.py -v`
Expected: FAIL — collection succeeds and any guard whose forbidden token is present fails. If every prior task was written as specified, the only expected failures are ones this task exists to surface.

- [ ] **Step 3: Fix whatever the guard catches**

No new module. If a guard fires, the fix is in the module that tripped it, never in the guard: the guard is the SPEC's negative half. The one legitimate change is to a **token**, when it turns out to be a false positive against real code — `plan` inside `explanation` is the worked example. In that case narrow the token or move the obligation to a structural guard; never delete the test.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p4/test_p4_no_invention.py -v`
Expected: PASS — 22 passed

- [ ] **Step 5: Commit**

```bash
git add tests/p4/test_p4_no_invention.py
git commit -m "test(P4): no-invention guard, and every open question held open"
```

---
### Task 19: The walking-skeleton P4 step

**Files:**
- Test: `tests/p4/test_p4_skeleton_step.py`

**Interfaces:**
- Consumes: everything above, plus `database_agent.files_table` — `get_file`, `observe_path` (its only use in this plan).
- Produces: the integration test every later part must keep green.

**[`../../02-segmentation-map.md`](../../02-segmentation-map.md)'s slice, verbatim:** *"P4/P5 extract page-one text; emit ONE observation in the frozen shape."* P5 does the extracting; **P4's half is the frozen shape** — that the one observation, the run that scoped it, and the page-one text it was read out of all exist, conform, store, and read back as what was emitted. This test proves P4's half with no extractor in existence, which is the whole claim P4 is making.

**The SPEC names the fixture:** *"the segmentation map's skeleton … → example 1 above, with a `complete` run and the one `text_units` row its span indexes into."* Fixture 1 is Task 16's, and this test rebuilds it against a real `file_id` and the content hash P1 computed — not against the fixture's own — so the seam with P1 is exercised rather than asserted.

**Fixture 1's golden locator carries no span, so nothing indexes into the unit.** `heading:page=1/heading=2` has no `#start-end`, so conformance rule 10 is vacuous for this observation and the `text_units` row exists because §2.2 requires *"complete text by page"* and the skeleton's own words are *"extract page-one text"* — not because a span forced it. The SPEC's phrase *"the one `text_units` row its span indexes into"* does not fit its own fixture 1; that is recorded under *SPEC vs design — conflicts found* rather than repaired by giving fixture 1 a span the golden table does not have.

**The seam this test defends is authorship.** P3 authors the file row's events; **P5** authors the `extraction` event, because P5 is the acting part for a native run (I4, M8); **P1 authors nothing**; and **P4 authors nothing either** — it ships the writer and names no subsystem. A log whose `subsystem` said `P4` would record that the schema library read the document.

**P6's half is P6's.** Done-means 9 asks that P6 resolve `course = BUSIB 4300` from this fixture with no extractor present. That test belongs to P6. What P4 owes it is the fixture with its context intact — `context_before: "Syllabus — "`, which carries one of §3.5's five academic terms (B8a) — and P4 holds no list of those five terms, because that list is P6's.

Deterministic: no model, no cloud, no embeddings, no network.

- [ ] **Step 1: Write the failing test**

```python
# tests/p4/test_p4_skeleton_step.py
"""The walking skeleton's P4 step (02-segmentation-map.md):
"P4/P5 extract page-one text; emit ONE observation in the frozen shape."

P5 does the extracting. P4's half is the frozen shape: one observation, the run that
scoped it, and the page-one text it was read out of, all conforming, stored, and read
back as what was emitted -- with no extractor in existence.

This test stays in the repository as the integration test every later part must keep
green. It is deterministic: no model, no cloud, no embeddings, no network.
"""
import json
from dataclasses import replace
from pathlib import Path

import pytest

from database_agent.files_table import get_file, observe_path

from evidence_shape.authorship import UnauthoredEvent
from evidence_shape.canonical import canonical_json
from evidence_shape.conformance import validate_run
from evidence_shape.determinism import observation_set_digest
from evidence_shape.fixtures import by_number
from evidence_shape.location import Segment
from evidence_shape.store import (
    get_run, observations_by_key, observations_for_run, record_observation,
    record_run, record_run_event, record_text_unit, text_unit_at,
)
from evidence_shape.text_units import TextUnit

#: The page the skeleton extracts. It carries the value three times, which is what
#: fixture 1's occurrence_count says, and the context §3.5's term lives in.
PAGE_ONE = (
    "BUSIB 4300 Syllabus\n"
    "Course Information\n"
    "Syllabus — BUSIB 4300 — Spring 2026\n"
    "Instructor office hours are by appointment.\n"
    "Questions about BUSIB 4300 go to the teaching assistant.\n"
)

SKELETON_RUN = "skeleton-run"
PAGE_ONE_PATH = (Segment("page", 1),)


def _file_row(conn, tmp_path: Path) -> tuple[str, str]:
    """P3's half of the seam, as a fixture: one `files` row, authored by P3.

    P4 touches `observe_path` here and nowhere else in this plan -- its records are
    testable without a file row, which is what lets P6 be built against the fixtures.
    """
    document = tmp_path / "corpus" / "syllabus-fixture.pdf"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text(PAGE_ONE, encoding="utf-8")
    stat = document.stat()
    file_id = observe_path(
        conn, document, author="P3", component_version="p3-skeleton-fixture",
        filename=document.name, normalized_filename=document.name,
        extension=document.suffix, observed_size=stat.st_size,
        observed_timestamps=json.dumps({"modified": stat.st_mtime}),
        parent_folder_context=str(document.parent), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def test_skeleton_p4_step(p4_conn, tmp_path: Path):
    file_id, content_hash = _file_row(p4_conn, tmp_path)

    # ── the frozen shape, rebuilt on the real identity P1 resolved ────────────
    template = by_number(1)
    run = replace(template.run, run_id=SKELETON_RUN, file_id=file_id,
                  content_hash=content_hash)
    observation = replace(template.observations[0], file_id=file_id,
                          content_hash=content_hash, run_id=SKELETON_RUN)
    unit = TextUnit(run_id=SKELETON_RUN, container_path=PAGE_ONE_PATH, text=PAGE_ONE)

    # ── the gate six extractor authors run, before anything is written ────────
    assert validate_run(run, [observation], [unit]) is run

    record_run(p4_conn, run)
    record_text_unit(p4_conn, unit)
    record_observation(p4_conn, observation)
    record_run_event(p4_conn, SKELETON_RUN, author="P5")

    # ── ONE observation, in the frozen shape ──────────────────────────────────
    assert p4_conn.execute("SELECT count(*) FROM evidence").fetchone()[0] == 1
    stored, = observations_for_run(p4_conn, SKELETON_RUN)
    assert stored == observation
    assert stored.locator == "heading:page=1/heading=2"
    assert stored.zone == "heading"
    assert stored.raw_value == "BUSIB 4300"
    assert stored.source_type == "text_document"
    assert stored.reliability == "possible"
    assert stored.occurrence_count == PAGE_ONE.count("BUSIB 4300") == 3
    assert stored.context_before == "Syllabus — "
    assert stored.context_after == " — Spring 2026"
    assert stored.context_truncated is False
    assert stored.signal_tier is None

    # Fixture 1's golden locator carries no span, so rule 10 is vacuous here: the
    # page-one unit exists because §2.2 requires complete text by page, not because a
    # span forced it.
    assert stored.location.text_span is None

    # ── the citation handle resolves, and it is the KEY, never the row id ─────
    assert observations_by_key(p4_conn, stored.observation_key) == [stored]
    assert stored.observation_key.startswith("sha256:")

    # ── the page-one text is stored and readable, and the value is in it ──────
    page = text_unit_at(p4_conn, SKELETON_RUN, PAGE_ONE_PATH)
    assert page.text == PAGE_ONE
    assert page.length == len(PAGE_ONE)
    assert page.truncated is False
    assert stored.raw_value in page.text

    # ── the run says what happened, including the count ───────────────────────
    recorded = get_run(p4_conn, SKELETON_RUN)
    assert recorded.completeness == "complete"
    assert recorded.analysis_tier == "native"
    assert recorded.observation_count == 1
    assert recorded.config_fingerprint == run.config_fingerprint

    # ── rule 8: what was stored is byte-identical to what was emitted ─────────
    assert (observation_set_digest([stored])
            == observation_set_digest([observation]))

    # ── the one §8.2 event, authored by the acting part (M8) ──────────────────
    events = p4_conn.execute(
        "SELECT * FROM events WHERE event_type = 'extraction'").fetchall()
    assert len(events) == 1
    event = events[0]
    assert event["subsystem"] == "P5"
    assert event["component_version"] == run.extractor_version
    assert event["file_id"] == file_id
    assert event["content_hash"] == content_hash
    # §8.2's "structured explanation or evidence reference": run_id plus the KEYS.
    assert event["explanation"] == canonical_json(
        {"run_id": SKELETON_RUN, "observation_keys": [stored.observation_key]})
    assert "observation_id" not in event["explanation"]

    # ── nobody named P4, and nobody named P1 ──────────────────────────────────
    authors = {row["subsystem"] for row in p4_conn.execute(
        "SELECT DISTINCT subsystem FROM events")}
    assert authors == {"P3", "P5"}
    assert "P4" not in authors
    assert "P1" not in authors


def test_the_skeleton_run_event_refuses_p1_as_its_author(p4_conn, tmp_path: Path):
    # M8: "P1 appends no event on its own initiative." A log whose subsystem names
    # the storage substrate cannot reconstruct what happened, which is §8.2's point.
    file_id, content_hash = _file_row(p4_conn, tmp_path)
    template = by_number(1)
    record_run(p4_conn, replace(template.run, run_id=SKELETON_RUN, file_id=file_id,
                                content_hash=content_hash))
    with pytest.raises(UnauthoredEvent):
        record_run_event(p4_conn, SKELETON_RUN, author="P1")
    with pytest.raises(UnauthoredEvent):
        record_run_event(p4_conn, SKELETON_RUN, author="")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p4/test_p4_skeleton_step.py -v`
Expected: FAIL if any prior task is incomplete; otherwise PASS.

- [ ] **Step 3: Run the full suite one final time**

Run: `pytest -q`
Expected: PASS — every P4 test from Tasks 1–19 green, and every P1, P2 and P3 test still green (P4 modified no file belonging to any of them).

- [ ] **Step 4: Commit**

```bash
git add tests/p4/test_p4_skeleton_step.py
git commit -m "test(P4): walking-skeleton P4 step, ONE observation in the frozen shape"
```

---
## Self-Review

**Executed, not merely written.** Every task in this plan was assembled into a runnable tree and run. **349 tests pass** across nineteen test files, against the real `src/database_agent/` — P1 as shipped, not as its PLAN.md describes it. Assembled alongside the live repository (P1's 152, P2's and P3's, 462 in total), the combined suite is **811 passed, 0 failed, no collection errors**.

**Test filenames do not collide.** The repository has already paid for this once: two test files with the same basename in different directories break collection for the entire suite under pytest's prepend import mode, which is why `tests/eval/__init__.py` exists. Every file here is `test_p4_*.py`, and no such basename exists in `tests/`, `tests/eval/` or `tests/p3/`. The only duplicated basenames in the combined tree are `conftest.py` — which pytest imports under a path-derived name and which already coexists across four directories — and the pre-existing `test_adversarial.py` pair that `tests/eval/__init__.py` already resolves. **`tests/p4/__init__.py` is not needed and is not created**; verified by running the combined tree.

**Spec coverage.** Every *Contract out* surface has a task. Record 1 → Tasks 6, 9, 11. Record 2 → Tasks 7, 9, 10. Record 3 → Tasks 8, 9, 11. The location addressing scheme → Task 3; the locator grammar and its escaping → Task 4; the six closed vocabularies → Task 2; canonical bytes and the injective digest → Task 5; §2.7's OCR field mapping → Tasks 7, 8, 16 (fixture 8 carries the bounding box and the confidence); the prohibitions → Task 17; the worked examples → Task 16; conformance → Tasks 13, 14, 15.

The twelve conformance rules map as: **1, 2, 3, 4, 6, 7, 11, 12 → Task 13**; **5, 9, 10 → Task 14**; **8 → Task 15**. All twelve are published in `CONFORMANCE_RULES` from Task 13 onward, so none can be quietly dropped, and Task 13 asserts the numbering is `range(1, 13)`.

*Done means* 1–10 map as: 1 → T2/T6/T7/T9 · 2 → T13/T14/T15 · 3 → T4 · 4 → T8 (the primitive) and T14 (`tests/p4/test_p4_raw1.py`, the same property through the gate an extractor author calls) · 5 → T16, with the shortfall named rather than filled · 6 → T17, with T13 covering the validator's half · 7 → T12 · 8 → T15 · 9 → T16 and T19 for P4's half; **P6's half is P6's to run**, and what P4 owes it is fixture 1 with its context intact · 10 → T8/T11/T14/T16.

**Every open question held open.** OQ1 is closed (I4) and is deliberately absent from `OPEN_QUESTIONS`. The five that remain each have a named guard in Task 18. **OQ2** (content hash or file record) — the observation carries both identifiers, `evidence` has no foreign key to `files`, and Task 15's compared set keeps `file_id` in precisely so the digest takes no position. **OQ3** (one reliability vocabulary or two) — §3.13's six are reused verbatim and extractors are restricted to two of them (D11); P4 defines no observation-level vocabulary, and Task 18's "no seventh vocabulary" guard fails if one appears. **OQ4** (handling-class granularity) — P4 adds no privacy field and guarantees both granularities are addressable, so P7 can answer either way. **OQ5** (may a user author an observation) — P4 publishes no writer for one; the store's six write/read names are pinned. **OQ6** (a source that is not on this machine) — `COMPLETENESS` is the SPEC's eight and there is no ninth; the guard runs on identifiers rather than on text, because the published question itself contains the words a violation would use.

**The SPEC's *Deferred* table is untouched.** No domain template library, no fact-schema field, no gazetteer, no residual library, no structured-string catalogue, no MIME routing table, no date pattern, no §8.6 numeric ceiling and no positional weight appears anywhere in `evidence_shape`. Task 18 guards each by token or by structure, and the import allowlist is the exact form of *"P4 runs no extractor"*: nothing outside the standard library and `database_agent` can be reached from this package.

**Placeholder scan.** No "TBD", no "TODO", no "similar to Task N", no bare `...` standing in for code, no angle-bracket placeholder. Every implementation step carries complete runnable code; every test step names the exact `pytest` command and the exact expected count, and **all eighteen stated counts were verified against a real run** — six of them were wrong when this plan was resumed (Tasks 4, 7, 9, 10, 11, 13) and are now corrected.

**Type consistency.** `observation_key`, `observation_id`, `supersede_reason`, `context_before` / `context_after` / `context_truncated`, `analysis_tier`, `config_fingerprint`, `container_path`, `unit_locator`, `text_span`, `time_span`, `signal_tier`, `create_evidence_schema`, `record_run` / `record_run_event` / `record_observation` / `record_text_unit`, `check_observation` / `validate_observation`, `check_run` / `validate_run`, `observation_set_digest` and `replay_key` are spelled identically in every task that names them. The three near-miss spellings that appear at all — `supersession_reason`, `surrounding_context`, and a second reliability vocabulary — appear **only** as values asserted absent, which is the point of them being there.

**One defect was found and fixed while writing Task 16.** `text_units.check_span_anchor` compared `container_path` as a tuple of `Segment` records, so a segment carrying a descriptive label (`Segment("slide", 6, label="Deadlines")`) failed rule 10 against a unit stored at the same address. Segment-kind rule 2 makes a label descriptive only, and `(run_id, unit_locator)` is the key `text_units` is actually stored under, so the comparison belongs on the address. Fixed in Task 8, with a named regression test in Task 14. It would have rejected most conforming observations — every one carrying a heading's text, a sheet's name or a slide's title.

**Four stale cross-references were corrected** in prose written before the task numbering settled: the generated-column and one-way-FK notes pointed at Task 8 rather than Task 9, the CJK/emoji note pointed at Task 11 rather than Task 8, and the determinism-digest note pointed at Task 16 rather than Task 15.

### Known gaps, carried deliberately

- **Five zones and one source type have no worked example** — `path`, `header_footer`, `link`, `annotation`, `reference_list`, and `contacts`. The SPEC's own nineteen-row table does not supply them and P4 does not invent them. Named in `ZONES_WITHOUT_A_WORKED_EXAMPLE` and `SOURCE_TYPES_WITHOUT_A_WORKED_EXAMPLE`, pinned by a test, and raised under *NEEDS JOSEPH*.
- **Conformance rule 12's fourth tooth is not checkable here.** An absence written *inside* `raw_value` as a string — `"EXIF absent"`, `"no text layer"` — cannot be detected without a list of forbidden strings, and authoring one would be the invention. `CONFORMANCE_RULES[12]` states the split, and P5's SPEC already carries the obligation.
- **No thirteenth conformance rule about `observation_count`.** A stored count that disagrees with the rows is a real defect, but the SPEC lists twelve and P4 does not legislate a thirteenth into a published contract. `store.record_observation` derives the count from the rows on every insert, so it cannot drift through P4's own writer.
- **The `analysis_tier` of a `metadata_only` run is a judgement, not a design statement.** Fixture 19 carries `native` — the tier of the extractor that was routed and stopped. I4 names four tiers and says nothing about a run that deliberately produced nothing. Raised under *NEEDS JOSEPH*.
- **`create_evidence_schema` is not called by `open_database`.** P1's handle creates P1's tables on open and knows nothing about P4's, so a caller that forgets it gets a database with `files` and `events` and none of P4's three. Deliberate: P4 modifies no P1 file.
- **Schema migration.** P4 adds three tables to P1's database and stamps no version of its own beyond `SHAPE_VERSION`, which versions the *shape*, not the tables. The first change to a P4 table needs a migration; the first creation does not.

---

## SPEC vs design — conflicts found

Reported, not unilaterally rewritten. Each is a place [`SPEC.md`](SPEC.md) disagrees with §-text, with its own other half, or with what the code can actually do. Where the plan had to act, what it did is stated; the contract itself is Joseph's to change.

| # | Where | The conflict | What this plan did |
|---|---|---|---|
| 1 | *Conformance* rule 8 vs §3.4 | Rule 8's key is *"content hash + extractor version + config fingerprint"* — three fields. §3.4 asks for a cache key on *"the content hash and the exact process that produced it"*, and Task 9's `extraction_runs_cache_key` index spells it with four, `extractor_name` included. Read literally, rule 8 would require `pdf.text 3.1.0` and `ocr.apple_vision 3.1.0` over one file to produce **one identical observation set** — impossible, because `observation_key` includes `extractor_name`. | `REPLAY_KEY_FIELDS` carries the four §3.4 names. Stated in `determinism.py`'s docstring and pinned by a test that names the conflict. |
| 2 | *Done means* 5 vs the *Zone vocabulary* table | Done-means 5 says *"all 14 zones"*. The zone table has **fifteen** rows. | Used fifteen everywhere. The plan's Global Constraints already said `zone` (15). |
| 3 | *Done means* 5 vs *Worked examples* | Done-means 5 asks the nineteen fixtures to cover *"all 14 zones and all 14 source types"*. They reach **10 of 15 zones** and **13 of 14 source types**. Missing zones: `path`, `header_footer`, `link`, `annotation`, `reference_list`. Missing source type: `contacts`. | Computed the shortfall from `FIXTURES`, published it, pinned it by test. Invented no example. *NEEDS JOSEPH #2.* |
| 4 | *Worked examples* row 3 vs the *Zone vocabulary* | Fixture 3's design case is *"§2.2's page-eighteen reference list"* and its golden zone is `body`. So the `reference_list` zone — which exists because §2.2 names it — has no worked example, and the SPEC's own reference-list example is filed elsewhere. | Kept the golden zone as the table gives it; asserted the fact in a test so it is visible rather than surprising. |
| 5 | *Done means* 5, wording | *"golden files"*. Every named consumer (P5, P6, P2) imports them, so a file would need a loader that reconstructs exactly the records this package already constructs. | Shipped `fixtures.py` as golden **records**; `canonical_json(observation.to_mapping())` produces the golden bytes on demand. Recorded as a deviation. |
| 6 | *Worked examples*, walking-skeleton note vs fixture 1 | The note says the skeleton is *"example 1 above, with a `complete` run and the one `text_units` row **its span** indexes into"*. Fixture 1's golden locator is `heading:page=1/heading=2` — **there is no span**, so conformance rule 10 is vacuous and nothing indexes into the unit. | Kept fixture 1's golden locator. The skeleton stores the page-one unit because §2.2 requires complete text by page and the skeleton's own words are *"extract page-one text"* — not because a span forced it. Asserted `text_span is None` explicitly. |
| 7 | *Conformance* rule 10 vs *Record 3* | Rule 10 requires a `text_units` row for **every** non-null `text_span`, and fixture 11's golden locator is `filename#0-6` — a span into a filename. Record 3 describes `text_units` as the home for the **bulk text** §2.2, §2.4 and §2.7 require. The unit that satisfies rule 10 here holds a filename. | Did what rule 10 says: fixture 11 carries a whole-file unit whose text is the filename. Narrowing rule 10 would be a contract revision. *NEEDS JOSEPH #4.* |
| 8 | *Conformance* rule 10 vs rule 5 | Rule 10 ends *"and RAW-1 holds against that row's text"*, which is rule 5's whole sentence. One defect, two numbers. | Checked once and reported under **rule 5**, the rule that names it. Rule 10 keeps the half that is its own: a unit exists, on this run, at this address. Stated in `check_run`'s docstring. |
| 9 | *Locator serialization* examples vs *Worked examples* row 4 | The grammar's example list writes §2.8's table case as `table:page=4/table=3/row=2/column=1`; the worked-example table writes the same case as `table:table=3/row=2/column=1`. | Followed the worked-example table, since that table is the fixture contract. Both parse and both round-trip. |
| 10 | *Worked examples* row 16 | Written as `metadata:field=name` with *"(in `key=dependencies`)"* beside it, which is not a serializable locator. | Serialized outermost-first as `metadata:key=dependencies/field=name`, which is what the grammar produces from the two segments the row describes. |
| 11 | *Conformance* rule 12 | Its fourth clause — an absence written *inside* `raw_value` as a string — is not checkable without a list of forbidden strings, which P4 may not author. | `CONFORMANCE_RULES[12]` states the split and names P5 as the carrier. Not faked. |
| 12 | *Cross-cutting answers* → *Budgets* vs §8.6 | The `context_before`/`context_after` budget is listed in *Deferred* as *"configuration"*, but §8.6's twelve ceilings do not include it and P1's fifteen `CEILING_KEYS` do not either — so there is no configuration surface for it to live on. | Stored as the caller supplies; `context_truncated` records that the caller cut it; `evidence_shape` holds no length. *NEEDS JOSEPH #1.* |

---

## NEEDS JOSEPH

Each item below needs a human decision. None is invented past in the tasks: every one is held open there by a guard test, and the plan is buildable and green under the position stated in the "what this plan does meanwhile" line. Part A is what building P4 surfaced. Part B is the SPEC's own open-questions list, restated in one place so the decisions Joseph has to make are one list.

### A. Decisions this plan surfaced

**A1 — Where does the §8.6 context budget live?**
*§-reference:* §8.6 (*"configurable ceilings"*); [`SPEC.md`](SPEC.md) *Deferred* row 8; P1 Contract out §6 (`budget.CEILING_KEYS`).
*What the design says:* §8.6 enumerates **twelve** configurable ceilings; P1 implements **fifteen** keys (§8.6's twelve, with three namespaced across two owners per O10) and `set_ceiling` raises `KeyError` on a sixteenth. *What it does not say:* none of the twelve or the fifteen is a context length, yet §2.8 requires surrounding context be stored and §8.6 requires nothing be truncated silently. The SPEC files the budget under "configuration" while no configuration surface accepts it.
*Options:* **(a)** add a sixteenth P1 ceiling key, e.g. `evidence.context_window`, and have P5 read it. **(b)** leave it caller-supplied forever — P5 decides per extractor and P4 stores what arrives. **(c)** make it a `config` entry on `extraction_runs`, so it is fingerprinted and replayable per run.
*Recommendation:* **(a)**, with **(c)** as a consequence rather than an alternative — a ceiling that is not in the fingerprint makes two runs at different context widths look identical to §3.4's cache and §8.5's replay. **(b)** is the only position that invents nothing, which is why it is what the plan does meanwhile.
*What this plan does meanwhile:* stores `context_before` / `context_after` exactly as supplied, records `context_truncated`, and holds no number. Guarded by `test_the_context_budget_is_caller_supplied_and_p4_holds_no_length`.

**A2 — Five zones and one source type have no worked example. Who writes them?**
*§-reference:* [`SPEC.md`](SPEC.md) *Worked examples*, *Done means* 5; zones from §2.2/§2.3/§2.9.
*What the design says:* Done-means 5 asks the fixtures to cover *"all 14 zones and all 14 source types"*. *What it does not say:* anything about `path`, `header_footer`, `link`, `annotation`, `reference_list` or `contacts` as worked examples — the nineteen-row table simply does not contain one. And its own reference-list case is filed under `body`.
*Options:* **(a)** author six more worked examples now, at design level, so the fixture set is complete before P5 starts. **(b)** amend Done-means 5 to *"every zone and source type the worked-example table reaches"* and let P5 contribute the rest as its extractors land. **(c)** have P4 invent them — **rejected**: six extractor authors would implement against a fabricated example, which is exactly the failure §2.8 exists to prevent.
*Recommendation:* **(b)** now, **(a)** when P5's format work begins and the real shapes are known. The five missing zones are all inside formats P5 has not designed yet, so an example written today would be a guess dressed as a contract.
*What this plan does meanwhile:* publishes the shortfall as data and pins it by test, so closing it is a visible change rather than a silent one.

**A3 — Does conformance rule 8's key include the extractor name?**
*§-reference:* [`SPEC.md`](SPEC.md) *Conformance* rule 8; §3.4; §8.5.
*What the design says:* rule 8 lists three fields; §3.4 says *"the content hash and the exact process that produced it"*. *What it does not say:* whether "the exact process" includes which extractor. It plainly must — `observation_key` includes `extractor_name`, so two extractors can never produce one identical set, and the literal three-field rule is unsatisfiable.
*Options:* **(a)** amend rule 8 to name four fields, matching §3.4 and the `extraction_runs_cache_key` index. **(b)** keep three and read them as shorthand. **(c)** drop `extractor_name` from `observation_key` — **rejected**: it would merge two extractors' readings of one value under one citation handle.
*Recommendation:* **(a)**. It is a one-word edit to the SPEC and it makes the rule true.
*What this plan does meanwhile:* keys on the four, states the discrepancy in `determinism.py`, and pins it with `test_the_replay_key_carries_the_extractor_name_rule_8_omits`.

**A4 — Does rule 10 apply to a span into a filename?**
*§-reference:* [`SPEC.md`](SPEC.md) *Conformance* rule 10, *Record 3*, *Locator serialization* (`filename#0-6`), worked example 11.
*What the design says:* rule 10 requires a `text_units` row for every non-null `text_span`; Record 3 describes `text_units` as the home for the bulk text §2.2/§2.4/§2.7 require; the grammar's own example list includes `filename#0-6`. *What it does not say:* whether a filename is a "text unit".
*Options:* **(a)** yes — a `filename` observation with a span carries a whole-file unit whose text is the filename. Rule 10 stays universal and RAW-1 is checkable everywhere. **(b)** narrow rule 10 to text-bearing zones, and let `filename` / `path` spans anchor against the `files` row instead — which reintroduces a second place a citation can resolve. **(c)** forbid spans on `filename` and `path`, dropping `filename#0-6` from the grammar.
*Recommendation:* **(a)**. It is the only option that leaves exactly one way to check a citation, and the cost is a very small row.
*What this plan does meanwhile:* **(a)**, asserted by `test_the_filename_span_is_anchored_in_a_text_unit_holding_the_filename`.

**A5 — What `analysis_tier` does a `metadata_only` run carry?**
*§-reference:* I4 ([`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md)); §2.9; [`SPEC.md`](SPEC.md) Record 2.
*What the design says:* `analysis_tier ∈ filesystem | native | ocr | llm`, and *"a value outside the four is rejected"*. `metadata_only` is §2.9's deliberate policy stop. *What it does not say:* which tier a run carries when the format-specific extractor was routed and deliberately produced nothing.
*Options:* **(a)** `native` — the tier of the extractor that was routed. **(b)** `filesystem` — the only work that actually happened. **(c)** make it P5's per-format decision and say so in P5's SPEC.
*Recommendation:* **(c)**, defaulting to **(a)**: which extractor was routed is the fact §2.4 wants preserved (*"an empty extraction result is different from an extractor that does not yet exist"*), and `filesystem` would make a routed-and-stopped PSD indistinguishable from a file only the basic pass ever touched.
*What this plan does meanwhile:* fixture 19 carries `native`, with the reason in a comment. Nothing in the code branches on it.

**A6 — Should a `text_units` row exist for a run that emitted no observation?**
*§-reference:* §2.2 (*"complete text by page"*), §2.4, *Record 3* rule 4, *Conformance* rule 9.
*What the design says:* §2.2 requires the page text be produced; rule 9 forbids observations on `unsupported`, `deferred` and `failed` runs. *What it does not say:* whether those runs may still carry text units. A `complete` run that read a whole PDF and found nothing worth observing plainly should keep its text — §8.5's *"Did the expected text appear?"* is a query against `text_units` and would otherwise have nothing to query.
*Options:* **(a)** units are independent of observations; any run that produced text stores it. **(b)** extend rule 9 to forbid units on the three zero-observation states as well.
*Recommendation:* **(a)**, and it is what the plan implements — but it is worth an explicit sentence in the SPEC, because rule 9 currently says nothing either way and a reader could take the silence as a prohibition.
*What this plan does meanwhile:* **(a)**. `check_run` constrains units only by run and address, never by count.

### B. The SPEC's open questions, restated  ·  **OQ2 ANSWERED 2026-08-20**

Each is already in [`SPEC.md`](SPEC.md) *Open questions* and each is held open by a named guard in Task 18. Listed here so Joseph's decisions are one list. P4 is buildable under either answer to all five; that is why they did not block this plan.

| # | Question | Blocks | My reading |
|---|---|---|---|
| ~~OQ2~~ | ~~Is an observation owned by the content hash or by the file record?~~ **ANSWERED 2026-08-20: the CONTENT HASH owns it.** | — | Two file records sharing a hash share one observation set; a fact derived on one applies to the other. `file_id` stays on the observation (§2.8 requires it) as a way in, not the owner — which is why P4 needed no structural change. **Carry into P5** (re-extract per content version, never per path), **P6** (facts attach to the hash), **P11** (a §6.9 multi-home file has one evidence set with several homes). Closed in [`SPEC.md`](SPEC.md) and dropped from `OPEN_QUESTIONS`. |
| OQ3 | Do observations and facts share one reliability vocabulary? | P5, P6 | Reusing §3.13's six and restricting extractors to two (D11) is the smaller contract and the one that needs no new vocabulary. Needs P6's confirmation; if P6 disagrees, D11 and conformance rule 3 change together. |
| OQ4 | Is the §8.4 handling class per observation or per file? | P7 (where the class is stored), P8 (what unit it redacts) | §8.4's own *"selected excerpts, redacted identifiers"* is observation-granular, which suggests per observation with a file-level roll-up. P4 needs no answer: both granularities are addressable today. |
| OQ5 | May a user author or correct an observation directly? | P6 (§3.13 semantics), P7 | §8.7 enumerates user actions and none is *"correct an extracted value"*; a user-confirmed **fact** at P6 looks like the intended route, and it keeps RAW-2 intact. If the answer is yes, P4 needs a new `extractor_name` convention and possibly a seventh reliability state — a real contract revision. |
| OQ6 | What `completeness` does a source that is not on this machine carry? | P3 (detection), P5 (the writer of runs), §8.6's progress line | None of the eight fits and a ninth value is the honest answer, but it is a vocabulary change and therefore Joseph's. Until then P3 records the detection and no `extraction_runs` row is written — which means §8.6's progress line cannot name the category. |

**Not needed from Joseph for P4.** The SPEC's *Deferred* table — the 200–300 domain template library (§5.7), domain fact-schema fields (§3.11), gazetteer contents (§3.7), the residual library (§7.2–§7.4), per-format structured-string catalogues, the MIME routing table (§2.9), date and academic-term patterns (§3.10), the §8.6 ceiling numbers, and positional weights per zone (§3.7) — is owned by P5, P6 and P10. P4 needs none of it to be complete, uses none of it, and Task 18's guards fail if any of it appears in `evidence_shape`.
