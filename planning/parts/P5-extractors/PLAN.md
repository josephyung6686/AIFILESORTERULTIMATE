# P5 — Extractors (×6) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn every file P3 hands over into **observations in the shape P4 froze** — §2.1's read-once-per-content-version evidence layer, §2.2–§2.7's six extractor families, §2.9's routing and long-tail coverage — with one outcome record per *(file version × extractor)* in P4's `extraction_runs`, bulk text in P4's `text_units`, and **no per-format branch left for any downstream consumer** (§2.8).

**Architecture:** P5 is a third package (`src/extractors/`) alongside P1's `database_agent` and P3's `scan_agent`, inside P1's single local SQLite database (§0). It owns **two** tables — a routing decision per file and a sensitivity signal per located value — and writes P4's three records through an injected **sink**, because `evidence`, `extraction_runs` and `text_units` are P4's tables and P5 never creates them. Every extractor has the same two-part shape: an **injected, caller-supplied format reader** that knows one library, and a **P5 half** that turns what the reader returns into P4's records. That split is what makes the six extractors independently buildable, and it is what makes Task 19's one-shape claim provable — the P5 half is nearly identical across all six because §2.8 says it must be.

**Tech Stack:** Python 3.12 · stdlib only (`sqlite3`, `hashlib`, `unicodedata`, `json`) · `pytest` · P1's `database_agent` package · **no third-party runtime dependency is added by this plan.** Real PDF/DOCX/HEIC/OCR reading cannot be done in the stdlib; every such reader is a parameter, and the libraries a real deployment needs are named in *Dependencies a real deployment must choose* below and in **NEEDS JOSEPH**.

---

## Read this before Task 1 — the three rules that decide whether this part is correct

### 1. P5 emits P4's shape. It invents none of its own.

`observation` / `extraction_runs` / `text_units` are **P4's** records, P4's field names, P4's closed
vocabularies. P5's `shape.py` is a *builder* for them, not a second definition of them. Concretely:

- P5 publishes **no status vocabulary** (B1). What happened once an extractor ran is
  `extraction_runs.completeness`, one row per *(file version × extractor)*. P5's obligation is to
  write the right value, not to name a parallel one. An opaque image runs E5 **and** E6 and produces
  **two** rows — "EXIF read successfully, OCR capped" — which a per-file status cannot express.
- P5 emits `context_before`, `context_after` and `context_truncated` as **three** fields (M5).
  §2.8's single "Surrounding context" line is published as three so §8.4 can redact a value without
  dropping its context. An extractor emitting one context field fails P4's conformance rule 1.
- `Location` is P4's **structured record** — `zone`, an ordered `container_path[]` of typed segments,
  `text_span` / `time_span` / `region` — never a per-format string. **P5 OQ1 is CLOSED**
  (04-resolutions.md, *The four remaining cross-spec questions*). Do not re-open it.
- OCR provider, config, languages, confidence and the complete-or-capped flag live on
  **`extraction_runs`**, not on the observation. **P5 OQ2 is CLOSED** (same document). Do not put
  them on an observation.
- `observation_key`, `observation_id`, `run_id` and the canonical `locator` string are **P4-assigned**.
  P5 supplies the structured `location`; P4 serializes it. P5 contains no percent-encoding and no
  locator parser — two implementations of one serialization is the drift this project has paid for
  three times already.

**Until P4 lands, the import does not exist.** Every module below builds plain mappings whose keys
are P4's field names, and hands them to an injected `EvidenceSink`. `tests/p5/p4_stub.py` reconstructs
P4's vocabularies, its locator serialization and its twelve conformance rules **from P4's SPEC**, and
every extractor test validates its output through that stub. When P4 ships, `p4_stub.py` is deleted
and the same tests import `from evidence.records import ...` and `from evidence.conformance import
validate_observation` instead — the production modules under `src/extractors/` do not change, because
they never imported the stub.

### 2. Two safety rules bind every extractor, and neither has an override path

**Applications and system items are never read, never moved, never opened.**
[`../../11-ops-runtime.md`](../../11-ops-runtime.md) §4b and P3's SPEC: an application bundle, a macOS
package, and anything under a system location is a **protected container**. *"P3 does not descend into
one, does not stat its contents, does not hash a byte of it, and does not create a `files` row for
anything inside it… no policy, approval, or user gesture makes it movable — this is not a default that
review can override."* The label is **`untouched_protected`**. P5's consequence: **no extractor is
reachable for a path inside a protected container**, and Task 3 is the test that proves it.

**A dataless (cloud-placeholder) file is never materialized, hashed, or extracted.**
`11-ops-runtime.md` §5: *"Do not materialize, hash, or extract."* P1's `hash_file` takes a required
`materialized` keyword and raises `DatalessFileRefused`. P5 **detects before reading** and never forces
a download. P4 Open question 6 — which `completeness` such a file carries — stays open: P5 writes **no
run row** for one, exactly as P3 writes no run row.

Both rules are enforced in **one** module, `safety.py`, at the single entry point every extractor
passes through. There is no second path in.

### 3. Every open question stays open

Nine questions are open in P5's SPEC (one of them settled: OQ3). Not one of them is answered in code
here. Each is held by a guard in Task 20 that names it and fails the moment someone answers it in an
implementation instead of in a SPEC. Where the design leaves a value open — a threshold, a ceiling, a
resolution list, an aspect ratio, a language, a regex, a producer-string list — this plan holds a
**caller-supplied strategy or a required keyword**, never a number and never a list.

---

## Global Constraints

Every task's requirements implicitly include these.

- **P5 decides nothing about meaning** (§2.8). No folder path, no domain, no fact field, no merge
  across files, no model output as proof. `subject = BUSIB 4300` is a fact and belongs to P6 (§3.2);
  the filename, the PDF title and the page-one heading are observations and belong here.
- **P5 contains no model call of any kind.** Every LLM call is P8's (§3.3). OCR is a local recognition
  engine (§2.7), not a model escalation, and `analysis_tier = "llm"` is a value P5 never writes.
- **No negative observation, no conflict observation** (§2.6, P4 *What an observation may not do*).
  "No EXIF", "no text layer" and "metadata stripped" are recorded by the **run** — a `complete` run
  that emitted no `metadata` rows *is* the record — or nowhere. Conflicting signals are two
  observations with two `signal_tier` values; resolving them is P6's §3.7 margin rule.
- **Raw is never touched.** `raw_value` is exactly the source substring: no case folding, no Unicode
  normalization, no whitespace collapse, no trimming (P4 RAW-1/RAW-2). Normalization is mechanical
  only (P4 D8) and `normalized_value = null` is always legal (RAW-3).
- **Bulk text has exactly one home** (G1). Page text, whole-file text and recognized text are
  `text_units` rows keyed by `(run_id, container_path)`. No extractor stores text anywhere else, and
  every non-null `text_span` resolves against a unit on the same `run_id`.
- **P5 never overwrites anything.** Not an observation, not a run, not a text unit. A better extractor
  **supersedes** (§8.2); both records and both runs' text units remain readable.
- **P5 authors its events; P1 writes them** (M8). Two of §8.2's nineteen: `extraction` and **`OCR`** —
  spelled `OCR`, not `ocr` (MINOR 2, [`../../05-minor-resolutions.md`](../../05-minor-resolutions.md)),
  because P1's writer validates the type against §8.2's vocabulary and the lowercase spelling is
  rejected at run time. P5 registers nothing: both are reserved §8.2 names already in P1's frozen table.
- **P5 recomputes none of P3's ten fields** (O5). The §1.2 basic filesystem record is P3's; P5
  surfaces it as `source_type: filesystem` observations referencing P3's row. P5 hashes nothing —
  `hashlib` does not appear in `src/extractors/` — and determines no MIME type of its own.
- **"Parent-folder context", never "directory position"** (MINOR 11). §2.9's name is the published
  one. P1's `files` column is still spelled `directory_position`; P5 reads that column and publishes
  the value under §2.9's name.
- **No invented values.** No threshold, no ceiling, no gazetteer, no screen-resolution list, no aspect
  ratio, no language list, no regex, no producer-string list. Task 20 enforces this by **runtime
  introspection** of every module's namespace, not by searching source text — a source-text guard
  matches comments and docstrings and has broken three tasks on this project already.
- **Fixture readers, never the user's disk.** Every extractor test drives an in-test reader over
  in-test data; the two tests that touch disk (`submission.zip`, the skeleton) build under `tmp_path`.
- **Python 3.12**, stdlib only. `extractors` adds no third-party dependency.
- **P5 creates and modifies no P1 file and no P3 file.** `pyproject.toml`, `tests/conftest.py` and
  everything under `src/database_agent/` and `src/scan_agent/` belong to other parts. P1's
  `[tool.setuptools.packages.find] where = ["src"]` already discovers `extractors`, and P1's
  `pythonpath = ["src"]` already makes it importable under pytest, so nothing needs to change. P5's
  tests live in `tests/p5/` with their own `conftest.py` and inherit P1's root `conn` fixture.

---

## What P5 consumes from P1

Written against `src/database_agent/` **as implemented on 2026-08-20** — verified by importing the
package and reading `inspect.signature`, not from P1's PLAN, which is a superseded construction record
and says so in its own header.

```text
database_agent.db          open_database(path, *, scan_roots=()) -> sqlite3.Connection
                           create_schema(conn) -> None
                           transaction(conn)                         contextmanager
database_agent.identity    hash_file(path, *, materialized: bool) -> str
                           HASH_ALGORITHM: str
                           DatalessFileRefused                       (raised by hash_file)
database_agent.files_table get_file(conn, file_id) -> sqlite3.Row
                           FILES_COLUMNS: tuple[str, ...]            (sixteen)
database_agent.events      append_event(conn, **fields) -> int
                           RESERVED_EVENT_TYPES: frozenset[str]      (§8.2's nineteen)
                           EVENT_FIELDS: tuple[str, ...]             (eleven, forever — MINOR 1)
                           MalformedEvent, UnregisteredEventType
```

Four facts about that surface, each of which changes how a task below is written:

- **`events` has exactly eleven fields** and `event_type`, `subsystem`, `component_version`,
  `observed_at` and `explanation` are each required and non-empty at the writer. P5's `extraction` and
  `OCR` events must therefore carry a non-empty structured `explanation`; Task 16 supplies §8.2's
  *"structured explanation or evidence reference"* as canonical JSON naming the `run_id`.
- **P1 appends no event on its own initiative** (M8). When P5 acts, `subsystem = "P5"`. There is one
  place in `extractors` where that value is written, and Task 20 asserts there is no second.
- **P1 publishes no writer for `files.extraction_status_by_tier`.** The column exists
  (`db.py` `FILES_DDL`) and `invalidate_extraction_state` resets it to `'{}'`, but there is no setter,
  and P5 does not `UPDATE files` — that table is P1's. Task 5 therefore **computes** the map as a pure
  function and hands it to an injected writer. *This is a real gap in P1's published surface and is
  reported rather than patched here; see the final report.*
- **`files.directory_position`** is the column that holds §2.9's parent-folder context (MINOR 11
  renamed the term, not the column). P5 reads it and never writes it.

## What P5 consumes from P4 — and how, before P4 exists

P4's SPEC is frozen; P4's code is not written. Every field name, vocabulary member, invariant and
conformance rule below is quoted from `../P4-evidence-shape/SPEC.md`.

```text
evidence          observation_id · observation_key                    P4-assigned
                  file_id · content_hash · extractor_name · extractor_version ·
                  source_type · raw_value · normalized_value · location ·
                  context_before · context_after · context_truncated ·
                  occurrence_count · observed_at · reliability          P5-supplied
                  run_id · confidence · signal_tier                     run_id P4, rest P5
                  supersedes · superseded_by · supersede_reason         P4-assigned
location          zone · container_path[] · text_span · time_span · region   P5-supplied
                  locator                                              P4-derived
extraction_runs   run_id                                               P4-assigned
                  file_id · content_hash · extractor_name · extractor_version ·
                  source_type · analysis_tier · config · config_fingerprint ·
                  completeness · coverage · observation_count ·
                  started_at · finished_at · failure_reason             P5-supplied
text_units        run_id                                               P4-assigned
                  container_path · unit_locator · text · length · truncated
                                                                       unit_locator P4-derived
```

**Closed vocabularies P5 uses and does not re-publish:** `zone` (fifteen), segment `kind` (fifteen),
`source_type` (fourteen), `reliability` (six, of which an extractor may write **two** — D11), and
`completeness` (eight). P5 restates only the two restrictions that are P5's own half of the contract:
`EXTRACTOR_RELIABILITY = ("direct", "possible")` (D11) and `ANALYSIS_TIERS` with `llm` refused (I4,
where the SPEC says *"P5 owns the vocabulary and writes the first three"*).

## What P5 consumes from P3, P6, P7 and configuration

| From | What | § |
|---|---|---|
| P3 | one `files` row per file, already exclusion-filtered; P5 never recomputes it | §1.1, §1.2, O5 |
| P3 | protected-container verdicts — a path inside one never reaches P5 | 11 §4b |
| P6 | `no_usable_facts(file_id, content_hash) -> bool`, the **only** thing that may trigger targeted OCR on a broken-text-layer PDF | §2.2, M11 |
| P7 | the explicit privacy-and-compute policy that is the only thing that may authorize speech-to-text (§2.9); and reclassification of a file as private (§8.4, §8.7) | §8.4, §2.9 |
| config | four §8.6 ceilings: max pages OCRed per file, max OCR time per file, max OCR time per scan, max image-analysis operations per scan — **values are P1's namespaced configuration object (G4)**, never literals here | §8.6, §2.7 |

`no_usable_facts` and the transcription authorization are **injected predicates** with no default:
P6 and P7 do not exist yet, and a default would be P5 answering another part's question.

## Dependencies a real deployment must choose

Named, not chosen. Every one is a **NEEDS JOSEPH** item; nothing here is installed by this plan, and
every reader below is a constructor parameter with a deterministic fixture implementation in tests.

| Reader | Needed for | Stdlib? | What a real deployment needs |
|---|---|---|---|
| `detect_format` | §2.9 signature-over-extension routing | no | libmagic (`python-magic`) or macOS `UTType`/`CoreServices` |
| `read_pdf` | E1 §2.2 text, metadata, page structure | no | `pypdf` / `pdfminer.six` / PDFKit via PyObjC |
| `read_docx` | E2 §2.3 paragraphs, headings, tables, headers/footers, relationships | no | `python-docx` (note: it is also the §2.2 producer string P6 discounts) |
| `read_text_document` | E3 §2.4 text, headings, language, structural markers | partly | stdlib for TXT/MD/JSON/CSV/YAML-as-text; `markdown-it-py`, `tomllib` (stdlib 3.11+) |
| `read_long_tail` | E3 §2.9 email / calendar / contacts / spreadsheet / presentation / audio-video | partly | stdlib `email`, `csv`; `icalendar`, `vobject`, `openpyxl`, `python-pptx`, `mutagen`/`ffprobe` |
| `read_manifest` | E4 §2.5 archive manifests | partly | stdlib `zipfile`/`tarfile` for ZIP and TAR; `py7zr`, `rarfile` beyond them |
| `read_image` | E5 §2.6 dimensions, EXIF, perceptual hash, **HEIC** | no | `Pillow` + `pillow-heif`, or macOS `ImageIO`/`Vision` via PyObjC |
| `perceptual_hash` | §2.6 near-duplicate identification (G5 consumes it) | no | `imagehash`, or an ImageIO-based implementation |
| `ocr_engine` | E6 §2.7 recognition, regions, confidence | no | **Apple Vision** — the one engine §2.7 names, and the whole of v1's OCR scope (S1) |
| `speech_to_text` | §2.9 transcripts, **only** under P7's explicit policy | no | deferred with the policy; see NEEDS JOSEPH |

---

## File Structure

```text
src/extractors/__init__.py           package marker
src/extractors/authorship.py         P5 authors `extraction` and `OCR` (M8, MINOR 2)
src/extractors/shape.py              P4's records, built — no vocabulary of P5's own
src/extractors/sink.py               the P4 write seam: EvidenceSink, one batch per run
src/extractors/safety.py             11 §4b protected containers · 11 §5 dataless — the one entry point
src/extractors/reading.py            the shapes P5's injected format readers return
src/extractors/schema.py             P5's two tables, inside P1's database
src/extractors/router.py             R — §2.9 routing, signature over extension
src/extractors/runs.py               P4 `extraction_runs`: coverage, cache key, analysis tiers
src/extractors/filesystem.py         O5 — P3's record re-emitted as `source_type: filesystem`
src/extractors/pdf.py                E1 — §2.2
src/extractors/ocr_policy.py         §2.2's three text-layer states and §2.7's OCR trigger
src/extractors/docx.py               E2 — §2.3
src/extractors/structured_text.py    E3 — §2.4
src/extractors/long_tail.py          E3's §2.9 families and the sensitivity signal
src/extractors/archive.py            E4 — §2.5
src/extractors/image.py              E5 — §2.6
src/extractors/ocr.py                E6 — §2.7
src/extractors/budgets.py            §8.6 — the four ceilings, deferral, the count line
src/extractors/events.py             §8.2 — `extraction` and `OCR`, authored by P5
src/extractors/stage_output.py       §8.5 / B7 — P2's envelope, produced not stored

tests/p5/conftest.py                 the recording sink, fixture readers, a fixed clock
tests/p5/p4_stub.py                  P4's SPEC, stubbed: vocabularies, locator, twelve rules
tests/p5/test_p5_authorship.py       M8, MINOR 2
tests/p5/test_p5_shape.py            P4 conformance rules 1, 2, 3, 6, 7, 11
tests/p5/test_p5_safety.py           11 §4b, 11 §5 — the two rules with no override
tests/p5/test_p5_router.py           Done-means 10, §2.9's family table
tests/p5/test_p5_runs.py             Done-means 1, the §3.4 cache key, the four analysis tiers
tests/p5/test_p5_filesystem.py       O5, P4 fixture 11
tests/p5/test_p5_pdf.py              Done-means 4, §2.2
tests/p5/test_p5_ocr_policy.py       Done-means 5, §2.2/§2.7
tests/p5/test_p5_docx.py             Done-means 6, §2.3
tests/p5/test_p5_structured_text.py  §2.4
tests/p5/test_p5_long_tail.py        §2.9's families, OQ5 and OQ7 held open
tests/p5/test_p5_archive.py          Done-means 7, §2.5
tests/p5/test_p5_image.py            Done-means 8, §2.6's three traps
tests/p5/test_p5_ocr.py              Done-means 9, §2.7's nine fields
tests/p5/test_p5_budgets.py          §8.6, Done-means 1's counting rules
tests/p5/test_p5_events.py           §8.2, MINOR 2
tests/p5/test_p5_stage_output.py     §8.5, B7
tests/p5/test_p5_reextraction.py     Done-means 12, §8.2 supersession
tests/p5/test_p5_one_shape.py        Done-means 2, 3, 11 — §2.8's whole claim
tests/p5/test_p5_no_invention.py     every open question held open
tests/p5/test_p5_skeleton_step.py    02-segmentation-map.md's P4/P5 step
```

Files split by published record and by extractor family, not by technical layer: each of E1–E6 is one
module and one test file, with no import between siblings, so the six can be built in parallel and one
can be rejected in review without touching its neighbours.

---

### Task 1: Package skeleton and P5's authorship constants

**Files:**
- Create: `src/extractors/__init__.py`
- Create: `src/extractors/authorship.py`
- Test: `tests/p5/test_p5_authorship.py`

**Interfaces:**
- Consumes: `database_agent.events.RESERVED_EVENT_TYPES`.
- Produces: `SUBSYSTEM: str`, `COMPONENT_VERSION: str`, `AUTHORED_EVENT_TYPES: tuple[str, str]`, `event_defaults(**fields) -> dict`.

**Why this is Task 1.** Sixteen later modules append or hand over events, and the one thing that must
never be got wrong is whose name lands in `subsystem` and how the OCR type is spelled. **MINOR 2**:
§8.2 spells it **`OCR`**, and P1's writer validates the type against §8.2's frozen vocabulary — the
lowercase `ocr` P4's and P5's drafts both used raises `UnregisteredEventType` at run time, not at
review. Putting the constant first means no later task has a plausible reason to type either value by
hand, and Task 20's guard has exactly one place to look.

**P5 authors two of §8.2's nineteen and registers nothing.** `extraction` (once per file per extractor
family per content version) and `OCR` (once per OCR run) are both reserved §8.2 names already in P1's
frozen table, so `extractors` contains no registration call (B5's rule 4: registration is a spec-level
act). P5 appends `hashing` and `stat observation` **never** — those are P1's and P3's.

**`event_defaults` is a helper, not a writer.** It fills §8.2's authorship fields and returns a plain
`dict` for the caller to hand to P1's `append_event`. It opens no connection and writes nothing, so
there is no code path where P5 appends an event without a caller having decided to.

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_authorship.py
import pytest

from database_agent.events import RESERVED_EVENT_TYPES

from extractors.authorship import (
    AUTHORED_EVENT_TYPES, COMPONENT_VERSION, SUBSYSTEM, event_defaults,
)


def test_p5_names_itself_as_the_author():
    # M8: the acting part authors; P1 writes. One value, no default.
    assert SUBSYSTEM == "P5"


def test_p5_authors_exactly_extraction_and_ocr():
    # SPEC Cross-cutting answers -> Provenance: "two of §8.2's enumerated event
    # types: `extraction` ... and `OCR`". No third.
    assert AUTHORED_EVENT_TYPES == ("extraction", "OCR")


def test_the_ocr_event_type_is_spelled_the_way_8_2_spells_it():
    # MINOR 2, 05-minor-resolutions.md: "§8.2 spells it `OCR`. P4 and P5 change.
    # The writer validates against the vocabulary, so this would have failed at
    # runtime." Not a style preference — a rejected INSERT.
    assert "OCR" in AUTHORED_EVENT_TYPES
    assert "ocr" not in AUTHORED_EVENT_TYPES


def test_every_type_p5_authors_is_one_of_8_2s_reserved_nineteen():
    # B5: registration is a spec-level act. Both names are reserved, so P5 declares
    # nothing and registers nothing.
    assert set(AUTHORED_EVENT_TYPES) <= set(RESERVED_EVENT_TYPES)


def test_p5_publishes_no_registration_call():
    import extractors.authorship as module
    assert not [name for name, value in vars(module).items()
                if callable(value) and name.lower().startswith("register")]


def test_event_defaults_fill_in_8_2s_authorship_fields():
    fields = event_defaults(event_type="extraction", file_id="f1",
                            content_hash="sha256:abc", explanation="{}")
    assert fields["subsystem"] == "P5"
    assert fields["component_version"] == COMPONENT_VERSION
    assert fields["observed_at"]
    assert fields["event_type"] == "extraction"
    assert fields["file_id"] == "f1"


def test_event_defaults_refuse_a_type_p5_does_not_author():
    # P3 authors `discovery`, `stat observation` and `hashing`; P12 authors the
    # move events. P5 puts its name on neither.
    for foreign in ("discovery", "stat observation", "hashing", "executed move"):
        with pytest.raises(ValueError):
            event_defaults(event_type=foreign, file_id="f1", explanation="{}")


def test_event_defaults_reject_the_lowercase_ocr_spelling():
    with pytest.raises(ValueError):
        event_defaults(event_type="ocr", file_id="f1", explanation="{}")


def test_event_defaults_cannot_be_told_to_name_another_subsystem():
    with pytest.raises(ValueError):
        event_defaults(event_type="extraction", file_id="f1", explanation="{}",
                       subsystem="P1")


def test_event_defaults_require_the_structured_explanation_8_2_asks_for():
    # P1's writer refuses an empty `explanation`; §8.2 requires "a structured
    # explanation or evidence reference". Failing here beats failing at the INSERT.
    with pytest.raises(ValueError):
        event_defaults(event_type="extraction", file_id="f1", explanation="")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_authorship.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'extractors'`

- [ ] **Step 3: Write the implementation**

```python
# src/extractors/__init__.py
"""P5 — the six extractors. Every one of them emits P4's shape and nothing else."""
```

```python
# src/extractors/authorship.py
"""P5 is the author of its own events; P1 writes them (M8).

§8.2: "the responsible subsystem". P1 appends no event on its own initiative, so
the value that lands in `subsystem` is set HERE and in no other module.

P5 authors two of §8.2's nineteen reserved types and registers nothing:

    `extraction`  once per file per extractor family per content version
    `OCR`         once per OCR run

`OCR` is spelled the way §8.2 spells it (MINOR 2). P1's writer validates the type
against §8.2's frozen vocabulary, so the lowercase spelling earlier drafts used is
not a style issue: it raises UnregisteredEventType at the INSERT.
"""
from __future__ import annotations

from datetime import datetime, timezone

#: M8. There is one value and no default anywhere in `extractors`.
SUBSYSTEM = "P5"

#: §8.2's "extractor version" on the event row. Per-extractor versions live on the
#: extractor modules; this is the version of P5's own event authorship.
COMPONENT_VERSION = "0.1.0"

#: §8.2's own names, spelled as §8.2 spells them (MINOR 2). Both are reserved, so
#: P5 registers nothing (B5, rule 4: registration is a spec-level act).
AUTHORED_EVENT_TYPES: tuple[str, str] = ("extraction", "OCR")


def event_defaults(**fields) -> dict:
    """Fill §8.2's authorship fields and return a plain dict for P1's append_event.

    Writes nothing and opens nothing: there is no code path where P5 appends an
    event without a caller having decided to.
    """
    event_type = fields.get("event_type")
    if event_type not in AUTHORED_EVENT_TYPES:
        raise ValueError(
            f"P5 does not author {event_type!r}; it authors {AUTHORED_EVENT_TYPES}. "
            "`discovery`, `stat observation` and `hashing` are P3's, and the move "
            "events are P12's (M8)."
        )
    if "subsystem" in fields and fields["subsystem"] != SUBSYSTEM:
        raise ValueError(
            f"P5 cannot author an event as {fields['subsystem']!r}: the acting part "
            "authors and P1 writes (M8)"
        )
    if not fields.get("explanation"):
        raise ValueError(
            "§8.2 requires a structured explanation or evidence reference on every "
            "event; P1's writer refuses an empty one"
        )
    return {
        **fields,
        "subsystem": SUBSYSTEM,
        "component_version": fields.get("component_version") or COMPONENT_VERSION,
        "observed_at": fields.get("observed_at") or datetime.now(timezone.utc).isoformat(),
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p5/test_p5_authorship.py -v`
Expected: PASS — 9 passed

- [ ] **Step 5: Commit**

```bash
git add src/extractors/__init__.py src/extractors/authorship.py \
        tests/p5/test_p5_authorship.py
git commit -m "feat(P5): package skeleton, P5 authors extraction and OCR (MINOR 2's spelling)"
```

---

### Task 2: P4's shape, built — and the stub that stands in until P4 lands

**Files:**
- Create: `src/extractors/shape.py`
- Create: `src/extractors/sink.py`
- Create: `tests/p5/p4_stub.py`
- Create: `tests/p5/conftest.py` — `RecordingSink`, the `sink` fixture, `FIXED_CLOCK`
- Test: `tests/p5/test_p5_shape.py`

**Interfaces:**
- Consumes: nothing. This module is the bottom of P5.
- Produces: `OBSERVATION_FIELDS`, `LOCATION_FIELDS`, `RUN_FIELDS`, `TEXT_UNIT_FIELDS`, `EXTRACTOR_RELIABILITY`, `ANALYSIS_TIERS`, `P5_ANALYSIS_TIERS`, `segment()`, `location()`, `observation()`, `text_unit()`, `run()`, `normalize_mechanical()`, `context_for()`, `canonical_json()`, `fingerprint()`, `ForbiddenReliability`, `ForbiddenAnalysisTier`; and `sink.ExtractionResult`, `sink.EvidenceSink`.

**This module is a builder for P4's records, not a second definition of them.** It publishes field
*orders* so a test can assert every extractor emits the same keys, and it publishes exactly two
restrictions that are **P5's own half** of the contract:

- `EXTRACTOR_RELIABILITY = ("direct", "possible")` — P4 D11: *"Extractors may write only two of
  §3.13's six reliability states."* `validated`, `llm_supported`, `user_confirmed` and `rejected` are
  fact-layer outcomes; §2.8 forbids extraction treating model output as proof.
- `ANALYSIS_TIERS = ("filesystem", "native", "ocr", "llm")` — **I4, ratified 2026-08-19**, closed.
  P5's SPEC: *"P5 owns the vocabulary and writes the first three."* `run()` refuses `llm` outright,
  which is the only enforcement point P5 needs against §3.3's boundary.

Everything else — `zone`, segment `kind`, `source_type`, `completeness`, the six reliability states —
is **P4's** and is not restated here. `shape.py` accepts the string it is given; P4's validator is the
gate. Restating a closed vocabulary in the consumer is how two names for one concept get created, and
that is the most expensive recurring defect on this project.

**What P5 does not compute.** `observation_id`, `observation_key`, `run_id`, the canonical `locator`
string, `unit_locator`, and the three supersede columns are **P4-assigned**. P5 emits the structured
`location`; P4 serializes it. There is no percent-encoding and no locator parser in `src/extractors/`,
and Task 20 asserts it — two implementations of one serialization is exactly the drift §2.8 exists to
prevent.

**The one hash P5 computes is not a content hash.** `fingerprint()` hashes the canonical JSON of a
run's `config` to produce P4's `config_fingerprint`, which §3.4's cache key and §8.5's diff both need.
P5 hashes **no file bytes**: the content hash is P1's and P5 never recomputes it (O5). `hashlib`
appears in `shape.py` and nowhere else in the package, and `shape.py` opens no file — Task 20 asserts
both.

**`normalize_mechanical` implements P4 D8 and nothing more:** Unicode NFC, whitespace collapse,
soft-hyphen and line-break repair. It resolves no entity, expands no abbreviation, and parses no date
out of free text (§3.10 forbids fuzzy date parsing). §2.8's own example is the test: a document saying
`U Chicago` keeps `U Chicago`. Turning it into `University of Chicago` is a **resolver's** job and the
resolver runs after extraction (§3.2).

**`context_for` takes a required `window`.** §8.6 makes the context budget configurable and P4 owns
the ceiling; the *value* is configuration (P4 Deferred). There is no default number here, so no caller
can accidentally inherit an invented one, and `context_truncated` is set whenever the window cut
anything — §8.6: a prompt *"should not truncate silently in a way that removes the decisive
evidence."*

**The sink is the P4 seam.** An extractor returns one `ExtractionResult` — the run plus every
observation and text unit it produced — and a sink writes it. That shape is deliberate: it is atomic
(no half-written run), it makes P4's conformance rule 9 checkable at the boundary, and it makes Task
19's determinism comparison a comparison of two whole batches. `RecordingSink` in `conftest.py` is the
test implementation; **P4 ships the real one**, and when it does the only change is which object the
caller constructs.

**`tests/p5/p4_stub.py` is a test-harness file, not a production module.** It reconstructs, from
`../P4-evidence-shape/SPEC.md`, the five closed vocabularies, the locator serialization with its
escaping rules, and the twelve conformance rules. Every extractor test below validates through it.
**When P4 lands, delete this file** and change the imports in `tests/p5/` to
`from evidence.records import ...` / `from evidence.conformance import validate_observation`. Nothing
under `src/extractors/` imports it, so nothing under `src/extractors/` changes.

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_shape.py
"""P4's shape, built by P5. Conformance rules 1, 2, 3, 4, 6, 7, 10, 11."""
import pytest

from extractors.shape import (
    ANALYSIS_TIERS, EXTRACTOR_RELIABILITY, LOCATION_FIELDS, OBSERVATION_FIELDS,
    P5_ANALYSIS_TIERS, RUN_FIELDS, TEXT_UNIT_FIELDS, ForbiddenAnalysisTier,
    ForbiddenReliability, canonical_json, context_for, fingerprint,
    location, normalize_mechanical, observation, run, segment, text_unit,
)
from extractors.sink import ExtractionResult

from p4_stub import locator_for, parse_locator, validate_observation

NOW = "2026-08-19T12:00:00+00:00"


def an_observation(**overrides):
    fields = dict(
        file_id="f1", content_hash="sha256:abc", extractor_name="pdf.text",
        extractor_version="0.1.0", source_type="text_document",
        raw_value="BUSIB 4300",
        location=location(zone="heading",
                          container_path=(segment("page", index=1),
                                          segment("heading", index=2,
                                                  label="Course Information")),
                          text_span={"start": 0, "end": 10}),
        observed_at=NOW, reliability="possible",
    )
    fields.update(overrides)
    return observation(**fields)


def test_the_observation_carries_every_2_8_field_and_no_extractor_private_one():
    # P4 conformance rule 1. The field list is P4's, in P4's order.
    obs = an_observation()
    assert tuple(obs) == OBSERVATION_FIELDS
    assert OBSERVATION_FIELDS == (
        "file_id", "content_hash", "extractor_name", "extractor_version",
        "source_type", "raw_value", "normalized_value", "location",
        "context_before", "context_after", "context_truncated",
        "occurrence_count", "observed_at", "reliability",
        "confidence", "signal_tier",
    )


def test_surrounding_context_is_three_fields_and_never_one():
    # M5: "P5, P6, P8, P9 and P11 correct their reproduced field lists to name P4's
    # three fields instead of §2.8's single 'surrounding context' line." §8.4 must be
    # able to redact a value without dropping its context.
    obs = an_observation()
    assert "context_before" in obs and "context_after" in obs
    assert "context_truncated" in obs
    assert "surrounding_context" not in obs
    assert "context" not in obs


def test_location_is_the_structured_record_and_never_a_string():
    # P5 OQ1 is CLOSED (04-resolutions.md): "Yes — P4's structured record plus the
    # canonical locator." §2.8's per-source-type examples cannot be a string.
    obs = an_observation()
    assert isinstance(obs["location"], dict)
    assert tuple(obs["location"]) == LOCATION_FIELDS == (
        "zone", "container_path", "text_span", "time_span", "region")


def test_p5_supplies_the_structured_fields_and_p4_derives_the_locator():
    # The locator is redundant with the structured fields by construction, so P5
    # emits no `locator` key: one serialization, one implementation (P4's).
    obs = an_observation()
    assert "locator" not in obs["location"]
    assert locator_for(obs["location"]) == "heading:page=1/heading=2#0-10"
    assert parse_locator("heading:page=1/heading=2#0-10")["zone"] == "heading"


def test_an_extractor_may_write_only_direct_and_possible():
    # P4 D11, conformance rule 3. The other four are fact-layer outcomes (§3.5).
    assert EXTRACTOR_RELIABILITY == ("direct", "possible")
    for forbidden in ("validated", "llm_supported", "user_confirmed", "rejected"):
        with pytest.raises(ForbiddenReliability):
            an_observation(reliability=forbidden)


def test_occurrence_count_is_at_least_one():
    # P4 conformance rule 7.
    assert an_observation()["occurrence_count"] == 1
    with pytest.raises(ValueError):
        an_observation(occurrence_count=0)


def test_signal_tier_is_null_by_default_and_only_ever_one_two_or_three():
    # P4: "null on every observation outside §2.6's image hierarchy"; rule 11.
    assert an_observation()["signal_tier"] is None
    for tier in (1, 2, 3):
        assert an_observation(signal_tier=tier)["signal_tier"] == tier
    for bad in (0, 4, "1"):
        with pytest.raises(ValueError):
            an_observation(signal_tier=bad)


def test_the_observation_carries_no_destination_domain_group_or_plan_reference():
    # P4 conformance rule 6; §2.8's prohibitions.
    obs = an_observation()
    for forbidden in ("path_proposal", "destination", "destination_node", "domain",
                      "category", "field_name", "group_id", "node_id", "template_id",
                      "plan_version", "handling_class", "sensitivity_state",
                      "preferred"):
        assert forbidden not in obs


def test_container_path_indices_are_one_based_and_a_label_kind_has_no_index():
    # P4 D3 and segment-kind rule 2.
    assert segment("page", index=1) == {"kind": "page", "index": 1, "label": None}
    assert segment("field", label="Producer") == {"kind": "field", "index": None,
                                                  "label": "Producer"}
    with pytest.raises(ValueError):
        segment("page", index=0)
    with pytest.raises(ValueError):
        segment("page")
    with pytest.raises(ValueError):
        segment("field", index=1)


def test_normalization_is_mechanical_and_resolves_no_entity():
    # P4 D8 and §2.8's own example: "If a document says `U Chicago`, the raw
    # observation remains exactly that wording, while A RESOLVER may normalize it."
    # The resolver is P6's and runs after extraction (§3.2).
    assert normalize_mechanical("U Chicago") == "U Chicago"
    assert normalize_mechanical("  BUSIB   4300 ") == "BUSIB 4300"
    assert normalize_mechanical("Uni­versity") == "University"
    assert normalize_mechanical("Colum-\nbia") == "Columbia"


def test_raw_value_is_never_normalized_in_place():
    # P4 RAW-1 / RAW-2: raw_value is exactly the source substring.
    obs = an_observation(raw_value="U Chicago",
                         normalized_value=normalize_mechanical("U Chicago"))
    assert obs["raw_value"] == "U Chicago"


def test_a_null_normalized_value_is_always_legal():
    # P4 RAW-3: "An extractor that cannot normalize safely leaves it null."
    assert an_observation()["normalized_value"] is None


def test_context_is_cut_by_a_caller_supplied_window_and_says_so_when_it_was():
    # §8.6: never truncate silently. There is no default window: the value is
    # configuration (P4 Deferred, "the context_before/context_after budget").
    text = "Syllabus — BUSIB 4300 — Spring 2026"
    before, after, truncated = context_for(text, 11, 21, window=11)
    assert before == "Syllabus — " and after == " — Spring 2"
    assert truncated is True
    before, after, truncated = context_for(text, 11, 21, window=40)
    assert before == "Syllabus — " and after == " — Spring 2026"
    assert truncated is False
    with pytest.raises(TypeError):
        context_for(text, 11, 21)


def test_text_offsets_are_counted_in_code_points():
    # P4 D4: Unicode scalar values, not bytes and not UTF-16 code units. §2.7
    # requires CJK, so the unit must be language-stable.
    text = "課程 BUSIB 4300"
    before, after, truncated = context_for(text, 3, 13, window=8)
    assert before == "課程 "
    unit = text_unit(text=text)
    assert unit["length"] == 13


def test_the_run_record_carries_every_p4_field_and_a_config_fingerprint():
    row = run(file_id="f1", content_hash="sha256:abc", extractor_name="pdf.text",
              extractor_version="0.1.0", source_type="text_document",
              analysis_tier="native", config={"reader": "fixture"},
              completeness="complete",
              coverage={"units": "pages", "processed": 2, "total": 2},
              observation_count=1, started_at=NOW, finished_at=NOW)
    assert tuple(row) == RUN_FIELDS
    assert row["config_fingerprint"] == fingerprint({"reader": "fixture"})
    assert row["failure_reason"] is None


def test_p5_never_writes_the_llm_analysis_tier():
    # I4: "P5 owns the vocabulary and writes the first three; P8 is the only writer
    # of `llm`." §3.3's boundary, enforced at the one place P5 could cross it.
    assert ANALYSIS_TIERS == ("filesystem", "native", "ocr", "llm")
    assert P5_ANALYSIS_TIERS == ("filesystem", "native", "ocr")
    with pytest.raises(ForbiddenAnalysisTier):
        run(file_id="f1", content_hash="sha256:abc", extractor_name="x",
            extractor_version="0.1.0", source_type="text_document",
            analysis_tier="llm", config={}, completeness="complete",
            coverage={"units": "files", "processed": 1, "total": 1},
            observation_count=0, started_at=NOW, finished_at=NOW)


def test_a_text_unit_is_keyed_by_container_path_and_records_its_own_length():
    # P4 D12/G1. `container_path: ()` is the whole file (§2.4).
    unit = text_unit(text="page one text", container_path=(segment("page", index=1),))
    assert tuple(unit) == TEXT_UNIT_FIELDS == ("container_path", "text", "length",
                                               "truncated")
    assert unit["length"] == len("page one text")
    assert unit["truncated"] is False
    assert text_unit(text="whole file")["container_path"] == ()


def test_canonical_json_is_stable_across_key_order():
    assert canonical_json({"b": 1, "a": 2}) == canonical_json({"a": 2, "b": 1})
    assert fingerprint({"b": 1, "a": 2}) == fingerprint({"a": 2, "b": 1})
    assert fingerprint({}).startswith("sha256:")


def test_an_extraction_result_is_one_run_and_its_whole_batch(sink):
    result = ExtractionResult(
        run=run(file_id="f1", content_hash="sha256:abc", extractor_name="pdf.text",
                extractor_version="0.1.0", source_type="text_document",
                analysis_tier="native", config={}, completeness="complete",
                coverage={"units": "pages", "processed": 1, "total": 1},
                observation_count=1, started_at=NOW, finished_at=NOW),
        observations=(an_observation(),),
        text_units=(text_unit(text="BUSIB 4300",
                              container_path=(segment("page", index=1),
                                              segment("heading", index=2,
                                                      label="Course Information"))),),
    )
    run_id = sink.write(result)
    assert sink.runs[0]["run_id"] == run_id
    assert sink.observations[0]["run_id"] == run_id
    assert sink.text_units[0]["run_id"] == run_id
    sink.conforms()


def test_the_p4_stub_rejects_a_span_with_no_text_unit():
    # P4 conformance rule 10: "rule 10 fails an observation whose span has no unit".
    with pytest.raises(AssertionError):
        validate_observation(an_observation(), text_units=[])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_shape.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'extractors.shape'`

- [ ] **Step 3: Write the implementation**

```python
# src/extractors/shape.py
"""P4's records, built by P5.

This module is a BUILDER for `../P4-evidence-shape/SPEC.md`'s three records, not a
second definition of them. It restates exactly two things, both of which are P5's own
half of the contract:

    EXTRACTOR_RELIABILITY   P4 D11 - an extractor may write two of section 3.13's six
    ANALYSIS_TIERS          I4 (closed) - P5 owns the vocabulary, writes the first three

`zone`, segment `kind`, `source_type` and `completeness` are P4's closed vocabularies
and are NOT restated: this module accepts the string it is handed and P4's validator
is the gate. Restating a closed vocabulary in the consumer is how one concept ends up
with two names, which is the defect this project has paid for most often.

Not computed here, because they are P4-assigned: `observation_id`, `observation_key`,
`run_id`, the canonical `locator`, `unit_locator`, and the three supersede columns.
P5 emits the structured location; P4 serializes it.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from typing import Any, Mapping, Sequence

#: Section 2.8's field list, in section 2.8's order, plus the additions P4 marks with
#: a cross. The three context fields are P4's published shape of section 2.8's single
#: "Surrounding context" line (M5): section 8.4 must be able to redact a value
#: without dropping its context.
OBSERVATION_FIELDS: tuple[str, ...] = (
    "file_id", "content_hash", "extractor_name", "extractor_version",
    "source_type", "raw_value", "normalized_value", "location",
    "context_before", "context_after", "context_truncated",
    "occurrence_count", "observed_at", "reliability",
    "confidence", "signal_tier",
)

#: P4 D1. One shape for every source type; never a per-format string.
LOCATION_FIELDS: tuple[str, ...] = ("zone", "container_path", "text_span",
                                    "time_span", "region")

#: P4 D5 `extraction_runs`, minus `run_id`, which P4 assigns.
RUN_FIELDS: tuple[str, ...] = (
    "file_id", "content_hash", "extractor_name", "extractor_version", "source_type",
    "analysis_tier", "config", "config_fingerprint", "completeness", "coverage",
    "observation_count", "started_at", "finished_at", "failure_reason",
)

#: P4 D12 / G1 `text_units`, minus `run_id` and `unit_locator`, which P4 assigns.
TEXT_UNIT_FIELDS: tuple[str, ...] = ("container_path", "text", "length", "truncated")

#: P4 D11: "Extractors may write only two of section 3.13's six reliability states."
#: `validated`, `llm_supported`, `user_confirmed` and `rejected` are fact-layer
#: outcomes (section 3.5); section 2.8 forbids extraction treating model output as
#: proof.
EXTRACTOR_RELIABILITY: tuple[str, str] = ("direct", "possible")

#: I4, ratified 2026-08-19 - closed. P5 owns the vocabulary.
ANALYSIS_TIERS: tuple[str, ...] = ("filesystem", "native", "ocr", "llm")

#: "P5 writes the first three; P8 is the only writer of `llm`."
P5_ANALYSIS_TIERS: tuple[str, ...] = ("filesystem", "native", "ocr")

#: P4 segment-kind rule 2: a label-addressed kind has no index.
LABEL_ADDRESSED_KINDS: tuple[str, ...] = ("field", "entry", "key")

_SOFT_HYPHEN = "­"
_LINE_BREAK_HYPHEN = re.compile(r"-\n\s*")


class ForbiddenReliability(Exception):
    """P4 D11 - a fact-layer state reached an extractor."""


class ForbiddenAnalysisTier(Exception):
    """I4 - P5 attempted to write `llm`, which only P8 writes."""


def canonical_json(value: Any) -> str:
    """Deterministic serialization. Section 8.5's replay diff and section 3.4's cache
    key both need one."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def fingerprint(config: Mapping[str, Any]) -> str:
    """P4's `config_fingerprint` - "so section 3.4's key and section 8.5's diff can
    tell configs apart".

    This is the ONLY hash P5 computes, and it is a hash of configuration, never of
    file bytes: the content hash is P1's and P5 never recomputes it (O5).
    """
    digest = hashlib.sha256(canonical_json(dict(config)).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def segment(kind: str, *, index: int | None = None, label: str | None = None) -> dict:
    """One typed segment of P4's `container_path`.

    P4 D3: indices are 1-based, because section 2.8's own examples are ("page 1,
    heading 2") and they appear in user-visible section 8.2 explanations.
    P4 segment-kind rule 2: an indexed kind is addressed by its index and its label
    is descriptive only; a label-addressed kind (`field`, `entry`, `key`) has no
    index.
    """
    if index is None and label is None:
        raise ValueError(f"segment {kind!r} needs an index or a label")
    if index is not None and index < 1:
        raise ValueError(f"container-path indices are 1-based (P4 D3); got {index!r}")
    if kind in LABEL_ADDRESSED_KINDS and index is not None:
        raise ValueError(f"{kind!r} is label-addressed and takes no index (P4 rule 2)")
    return {"kind": kind, "index": index, "label": label}


def location(*, zone: str, container_path: Sequence[Mapping[str, Any]] = (),
             text_span: Mapping[str, int] | None = None,
             time_span: Mapping[str, int] | None = None,
             region: Mapping[str, Any] | None = None) -> dict:
    """P4 D1's addressing scheme. Outermost -> innermost.

    No `locator` key: the canonical string is P4's serialization and P5 owns no
    second implementation of it.
    """
    if text_span is not None and time_span is not None:
        raise ValueError("a location carries a text_span or a time_span, not both")
    return {
        "zone": zone,
        "container_path": tuple(container_path),
        "text_span": dict(text_span) if text_span is not None else None,
        "time_span": dict(time_span) if time_span is not None else None,
        "region": dict(region) if region is not None else None,
    }


def observation(*, file_id: str, content_hash: str, extractor_name: str,
                extractor_version: str, source_type: str, raw_value: str,
                location: Mapping[str, Any], observed_at: str, reliability: str,
                normalized_value: str | None = None,
                context_before: str = "", context_after: str = "",
                context_truncated: bool = False, occurrence_count: int = 1,
                confidence: float | None = None,
                signal_tier: int | None = None) -> dict:
    """One row of P4's `evidence`, in P4's field order.

    `raw_value` is exactly the source substring (RAW-1): no case folding, no Unicode
    normalization, no whitespace collapse and no trimming happens here or anywhere
    else in P5.
    """
    if reliability not in EXTRACTOR_RELIABILITY:
        raise ForbiddenReliability(
            f"{reliability!r} is a fact-layer state; an extractor may write "
            f"{EXTRACTOR_RELIABILITY} only (P4 D11, conformance rule 3)"
        )
    if occurrence_count < 1:
        raise ValueError("occurrence_count >= 1 (P4 conformance rule 7)")
    if signal_tier is not None and signal_tier not in (1, 2, 3):
        raise ValueError(
            "signal_tier is section 2.6's three-level image hierarchy: 1, 2, 3 or "
            "null (P4 conformance rule 11)"
        )
    return {
        "file_id": file_id,
        "content_hash": content_hash,
        "extractor_name": extractor_name,
        "extractor_version": extractor_version,
        "source_type": source_type,
        "raw_value": raw_value,
        "normalized_value": normalized_value,
        "location": dict(location),
        "context_before": context_before,
        "context_after": context_after,
        "context_truncated": context_truncated,
        "occurrence_count": occurrence_count,
        "observed_at": observed_at,
        "reliability": reliability,
        "confidence": confidence,
        "signal_tier": signal_tier,
    }


def text_unit(*, text: str, container_path: Sequence[Mapping[str, Any]] = (),
              truncated: bool = False) -> dict:
    """One row of P4's `text_units` (D12, G1) - the ONE home for bulk extracted text.

    `container_path: ()` is the whole file (section 2.4). `length` is counted in
    Unicode scalar values (D4), which is what makes RAW-1 checkable for CJK and emoji
    alike.
    """
    return {
        "container_path": tuple(container_path),
        "text": text,
        "length": len(text),
        "truncated": truncated,
    }


def run(*, file_id: str, content_hash: str, extractor_name: str,
        extractor_version: str, source_type: str, analysis_tier: str,
        config: Mapping[str, Any], completeness: str, coverage: Mapping[str, Any],
        observation_count: int, started_at: str, finished_at: str,
        failure_reason: str | None = None) -> dict:
    """One row of P4's `extraction_runs` - THE extraction-outcome record (B1).

    One row per (file version x extractor). P5 publishes no parallel status
    vocabulary of its own: an opaque image runs the image extractor AND OCR, which is
    two rows, and a per-file status cannot say "EXIF read successfully, OCR capped."
    """
    if analysis_tier not in P5_ANALYSIS_TIERS:
        raise ForbiddenAnalysisTier(
            f"P5 writes {P5_ANALYSIS_TIERS}; {analysis_tier!r} is refused. "
            "P8 is the only writer of `llm` (I4)."
        )
    return {
        "file_id": file_id,
        "content_hash": content_hash,
        "extractor_name": extractor_name,
        "extractor_version": extractor_version,
        "source_type": source_type,
        "analysis_tier": analysis_tier,
        "config": dict(config),
        "config_fingerprint": fingerprint(config),
        "completeness": completeness,
        "coverage": dict(coverage),
        "observation_count": observation_count,
        "started_at": started_at,
        "finished_at": finished_at,
        "failure_reason": failure_reason,
    }


def normalize_mechanical(raw: str) -> str:
    """P4 D8 - the four mechanical transforms, and nothing else.

    "Unicode NFC, whitespace collapse, soft-hyphen/line-break repair, and an ISO-8601
    rendering of a timestamp the source stored as a structured date. It may not
    resolve entities, expand abbreviations, or parse a date out of free text."

    Section 2.8's own example is the test: `U Chicago` stays `U Chicago`. Turning it
    into `University of Chicago` is a resolver's job and the resolver is P6's (3.2).
    """
    repaired = raw.replace(_SOFT_HYPHEN, "")
    repaired = _LINE_BREAK_HYPHEN.sub("", repaired)
    return unicodedata.normalize("NFC", " ".join(repaired.split()))


def context_for(text: str, start: int, end: int, *,
                window: int) -> tuple[str, str, bool]:
    """Section 2.8's surrounding context, as P4's three fields (M5).

    `window` is required and has no default: section 8.6 makes the context budget
    configurable and P4 owns the ceiling, so the number is configuration and naming
    one here would be an invented value. Returns
    (context_before, context_after, context_truncated); the flag is set whenever the
    window cut anything, because section 8.6 forbids truncating silently.
    """
    before_available, after_available = text[:start], text[end:]
    before = before_available[-window:] if window else ""
    after = after_available[:window] if window else ""
    truncated = (len(before) < len(before_available)
                 or len(after) < len(after_available))
    return before, after, truncated
```

```python
# src/extractors/sink.py
"""The P4 write seam.

`evidence`, `extraction_runs` and `text_units` are P4's tables. P5 creates none of
them and writes none of them directly: an extractor returns ONE `ExtractionResult` -
the run plus every observation and text unit it produced - and a sink writes it.

Why one batch rather than open/append/close: it is atomic, so there is no
half-written run; P4's conformance rule 9 ("unsupported, deferred and failed runs
carry zero observations") is checkable at the boundary; and section 8.5's determinism
comparison becomes a comparison of two whole batches rather than of two row streams.

The real sink is P4's. `RecordingSink` in tests/p5/conftest.py is the test one; when
P4 lands, the only change is which object the caller constructs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


@dataclass(frozen=True)
class ExtractionResult:
    """One run and everything it produced. The unit P5 hands to P4."""
    run: Mapping[str, Any]
    observations: tuple[Mapping[str, Any], ...] = ()
    text_units: tuple[Mapping[str, Any], ...] = ()


class EvidenceSink(Protocol):
    """P4's writer, as P5 sees it.

    `supersede_reason` is section 8.2's "the reason it was superseded": a later,
    improved extractor over the same content supersedes an earlier run, and BOTH
    remain available. P5 supplies the reason; P4 owns the supersede columns.
    """

    def write(self, result: ExtractionResult, *,
              supersede_reason: str | None = None) -> str:
        """Write the batch and return P4's `run_id`."""
        ...
```

```python
# tests/p5/p4_stub.py
"""P4's SPEC, stubbed - a TEST-HARNESS file, not a production module.

Reconstructed from ../../P4-evidence-shape/SPEC.md: the five closed vocabularies, the
locator serialization with its escaping rules, and the twelve conformance rules.
Every extractor test in tests/p5/ validates its output through this file, so a P5
extractor cannot ship a record P4 would reject.

WHEN P4 LANDS: delete this file and change the imports in tests/p5/ to
    from evidence.records import locator_for, parse_locator, ZONES, SOURCE_TYPES
    from evidence.conformance import validate_observation, validate_run
Nothing under src/extractors/ imports this file, so nothing under src/extractors/
changes.

Two rules are checked structurally rather than semantically, and this file says so
rather than pretending otherwise: rule 8 (determinism) is a property of two runs and
is asserted in tests/p5/test_p5_one_shape.py; rule 12 (no absence, no conflict) is
checked here as "no absence or conflict field, and a non-empty raw_value", with the
substantive check living in tests/p5/test_p5_image.py where section 2.6's three traps
are.
"""
from __future__ import annotations

import hashlib
from typing import Any, Iterable, Mapping

#: P4 "Zone vocabulary (closed)". Fifteen rows.
ZONES: tuple[str, ...] = (
    "filename", "path", "metadata", "title", "heading", "body", "table",
    "header_footer", "notes", "link", "annotation", "reference_list", "manifest",
    "ocr", "transcript",
)

#: P4 "Segment kinds (closed)". Fifteen rows.
SEGMENT_KINDS: tuple[str, ...] = (
    "page", "slide", "sheet", "heading", "paragraph", "table", "row", "column",
    "cell", "region", "layer", "artboard", "field", "entry", "key",
)

#: P4 segment-kind rule 2 - addressed by label, never by index.
LABEL_ADDRESSED: tuple[str, ...] = ("field", "entry", "key")

#: P4 "`source_type` vocabulary (section 2.9's families, closed)". Fourteen.
SOURCE_TYPES: tuple[str, ...] = (
    "filesystem", "text_document", "spreadsheet", "presentation", "image", "ocr",
    "email", "calendar", "contacts", "code_structured", "audio_video",
    "design_creative", "archive", "opaque_binary",
)

#: Section 3.13's six. An extractor may write the first two only (P4 D11).
RELIABILITY_STATES: tuple[str, ...] = (
    "direct", "possible", "validated", "llm_supported", "user_confirmed", "rejected",
)
EXTRACTOR_RELIABILITY: tuple[str, ...] = ("direct", "possible")

#: P4 `completeness` (closed), after B1 added `metadata_only`.
COMPLETENESS: tuple[str, ...] = (
    "complete", "capped", "partial", "metadata_only", "deferred", "unsupported",
    "unreadable", "failed",
)

#: P4 conformance rule 9, as M3 relaxed it: `unreadable` and `partial` runs MAY and
#: normally DO carry observations (section 2.9's "indexed-but-unreadable").
ZERO_OBSERVATION_COMPLETENESS: tuple[str, ...] = ("unsupported", "deferred", "failed")

#: I4, closed.
ANALYSIS_TIERS: tuple[str, ...] = ("filesystem", "native", "ocr", "llm")

OBSERVATION_FIELDS: tuple[str, ...] = (
    "file_id", "content_hash", "extractor_name", "extractor_version",
    "source_type", "raw_value", "normalized_value", "location",
    "context_before", "context_after", "context_truncated",
    "occurrence_count", "observed_at", "reliability",
    "confidence", "signal_tier",
)
NULLABLE_OBSERVATION_FIELDS: tuple[str, ...] = ("normalized_value", "confidence",
                                                "signal_tier")

#: P4's prohibitions, as schema-level rejections (conformance rule 6).
FORBIDDEN_OBSERVATION_FIELDS: tuple[str, ...] = (
    "locator", "path_proposal", "destination", "destination_node", "domain",
    "category", "field_name", "fact", "group_id", "node_id", "template_id",
    "plan_id", "plan_version", "handling_class", "sensitivity_state", "preferred",
    "absent", "conflict", "resolution", "screenshot", "media_type",
)

_ESCAPE = set("%/=#@:")


def _escape(label: str) -> str:
    """P4: percent-encode % / = # @ : and control characters, uppercase hex, UTF-8."""
    out = []
    for ch in label:
        if ch in _ESCAPE or ord(ch) < 0x20 or ord(ch) == 0x7F:
            out.extend(f"%{byte:02X}" for byte in ch.encode("utf-8"))
        else:
            out.append(ch)
    return "".join(out)


def _unescape(text: str) -> str:
    raw = bytearray()
    i = 0
    while i < len(text):
        if text[i] == "%":
            raw.append(int(text[i + 1:i + 3], 16))
            i += 3
        else:
            raw.extend(text[i].encode("utf-8"))
            i += 1
    return raw.decode("utf-8")


def unit_locator_for(container_path: Iterable[Mapping[str, Any]]) -> str:
    parts = []
    for seg in container_path:
        kind = seg["kind"]
        addr = _escape(seg["label"]) if kind in LABEL_ADDRESSED else str(seg["index"])
        parts.append(f"{kind}={addr}")
    return "/".join(parts)


def locator_for(location: Mapping[str, Any]) -> str:
    """P4's canonical serialization.

    locator := zone [":" segments] ["#" text_span | "@" time_span]
    """
    text = location["zone"]
    segments = unit_locator_for(location["container_path"])
    if segments:
        text += ":" + segments
    span, time_span = location.get("text_span"), location.get("time_span")
    if span is not None:
        text += f"#{span['start']}-{span['end']}"
    elif time_span is not None:
        text += f"@{time_span['start_ms']}-{time_span['end_ms']}"
    return text


def parse_locator(text: str) -> dict:
    """Inverse of locator_for. Labels escape # and @, so the first raw one delimits."""
    head, mark, tail = text, None, ""
    for i, ch in enumerate(text):
        if ch in "#@":
            head, mark, tail = text[:i], ch, text[i + 1:]
            break
    zone, _, segment_text = head.partition(":")
    container_path = []
    if segment_text:
        for chunk in segment_text.split("/"):
            kind, _, addr = chunk.partition("=")
            if kind in LABEL_ADDRESSED:
                container_path.append({"kind": kind, "index": None,
                                       "label": _unescape(addr)})
            else:
                container_path.append({"kind": kind, "index": int(addr),
                                       "label": None})
    span = time_span = None
    if mark == "#":
        start, _, end = tail.partition("-")
        span = {"start": int(start), "end": int(end)}
    elif mark == "@":
        start, _, end = tail.partition("-")
        time_span = {"start_ms": int(start), "end_ms": int(end)}
    return {"zone": zone, "container_path": tuple(container_path),
            "text_span": span, "time_span": time_span, "region": None}


def observation_key(observation: Mapping[str, Any]) -> str:
    """P4: sha256(content_hash + extractor_name + locator + raw_value), DELIBERATELY
    excluding extractor_version so section 8.5's replay can diff versions (MINOR 8).
    P4 assigns it; this stub computes it so tests can assert its stability."""
    material = "\x1f".join((observation["content_hash"], observation["extractor_name"],
                            locator_for(observation["location"]),
                            observation["raw_value"]))
    return "sha256:" + hashlib.sha256(material.encode("utf-8")).hexdigest()


def validate_observation(observation: Mapping[str, Any], *,
                         text_units: Iterable[Mapping[str, Any]] = ()) -> None:
    """P4's conformance validator, rules 1-7 and 9-12. Fails; never coerces."""
    # Rule 1 - every section 2.8 field present, three context fields, not one.
    assert tuple(observation) == OBSERVATION_FIELDS, tuple(observation)
    for name in OBSERVATION_FIELDS:
        if name not in NULLABLE_OBSERVATION_FIELDS:
            assert observation[name] is not None, name
    # Rule 6 - no destination, domain, field name, group, node, template or plan.
    for name in FORBIDDEN_OBSERVATION_FIELDS:
        assert name not in observation, name
    assert isinstance(observation["file_id"], str)

    location = observation["location"]
    # Rule 2 - closed vocabularies.
    assert location["zone"] in ZONES, location["zone"]
    assert observation["source_type"] in SOURCE_TYPES, observation["source_type"]
    for seg in location["container_path"]:
        assert seg["kind"] in SEGMENT_KINDS, seg
        if seg["kind"] in LABEL_ADDRESSED:
            assert seg["index"] is None and seg["label"] is not None, seg
        else:
            assert isinstance(seg["index"], int) and seg["index"] >= 1, seg
    # Rule 3 - an extractor writes `direct` or `possible`.
    assert observation["reliability"] in EXTRACTOR_RELIABILITY, observation["reliability"]
    # Rule 4 - the locator round-trips.
    text = locator_for(location)
    back = parse_locator(text)
    assert back["zone"] == location["zone"], text
    assert len(back["container_path"]) == len(location["container_path"]), text
    for parsed, built in zip(back["container_path"], location["container_path"]):
        assert parsed["kind"] == built["kind"], text
        if built["kind"] in LABEL_ADDRESSED:
            assert parsed["label"] == built["label"], text
        else:
            assert parsed["index"] == built["index"], text
    assert back["text_span"] == location["text_span"], text
    assert back["time_span"] == location["time_span"], text
    # Rule 7 - occurrence_count >= 1.
    assert observation["occurrence_count"] >= 1
    # Rule 11 - signal_tier is section 2.6-scoped.
    if observation["signal_tier"] is not None:
        assert observation["signal_tier"] in (1, 2, 3)
        assert observation["source_type"] == "image", (
            "signal_tier is section 2.6's image hierarchy")
    # Rule 12 - an observation is a reading, never an absence or a comparison.
    assert observation["raw_value"] != "", "an absence has no value to record (2.6)"
    # Rules 5 and 10 - RAW-1 against the unit the container path names.
    span = location["text_span"]
    if span is not None:
        units = [u for u in text_units
                 if tuple(u["container_path"]) == tuple(location["container_path"])]
        assert units, f"no text_units row for {text} (rule 10)"
        stored = units[0]["text"]
        assert stored[span["start"]:span["end"]] == observation["raw_value"], (
            f"RAW-1 fails at {text}")


def validate_run(run: Mapping[str, Any], observation_count: int) -> None:
    """P4 conformance rule 9 plus the run-level vocabularies."""
    assert run["completeness"] in COMPLETENESS, run["completeness"]
    assert run["analysis_tier"] in ANALYSIS_TIERS, run["analysis_tier"]
    assert run["analysis_tier"] != "llm", "P8 is the only writer of `llm` (I4)"
    assert run["source_type"] in SOURCE_TYPES, run["source_type"]
    assert set(run["coverage"]) == {"units", "processed", "total"}, run["coverage"]
    assert run["observation_count"] == observation_count
    if run["completeness"] in ZERO_OBSERVATION_COMPLETENESS:
        assert observation_count == 0, (
            f"an {run['completeness']} run carries zero observations (rule 9)")
    if run["completeness"] in ("unreadable", "failed"):
        assert run["failure_reason"], "failure_reason is required here"
```

```python
# tests/p5/conftest.py
"""P5's test fixtures: the recording sink that stands in for P4's writer, a fixed
clock so section 8.5's determinism assertion is a real assertion, and the fixture
readers the six extractors are driven by (added by the tasks that need them)."""
from __future__ import annotations

import pytest

from extractors.sink import ExtractionResult

from p4_stub import validate_observation, validate_run

#: Section 8.5 and P4 conformance rule 8 require two runs at the same content hash,
#: extractor version and config fingerprint to produce a byte-identical observation
#: set. The record carries `observed_at`, so the clock must be injectable for that to
#: be literally true. Every extractor below takes `now` as a required keyword.
FIXED_CLOCK = "2026-08-19T12:00:00+00:00"


class RecordingSink:
    """P4's writer, recorded. Appends only: nothing here updates or deletes, because
    P5 never overwrites an observation, a run or a text unit (section 8.2)."""

    def __init__(self) -> None:
        self.runs: list[dict] = []
        self.observations: list[dict] = []
        self.text_units: list[dict] = []
        self.supersessions: list[tuple[str, str]] = []

    def write(self, result: ExtractionResult, *,
              supersede_reason: str | None = None) -> str:
        run_id = f"run-{len(self.runs) + 1}"
        self.runs.append({"run_id": run_id, **result.run})
        for observation in result.observations:
            self.observations.append({"run_id": run_id, **observation})
        for unit in result.text_units:
            self.text_units.append({"run_id": run_id, **unit})
        if supersede_reason is not None:
            self.supersessions.append((run_id, supersede_reason))
        return run_id

    # --- read helpers, so tests never reach into the lists directly ---

    def units_for(self, run_id: str) -> list[dict]:
        return [u for u in self.text_units if u["run_id"] == run_id]

    def observations_for(self, run_id: str) -> list[dict]:
        return [o for o in self.observations if o["run_id"] == run_id]

    def run_for(self, run_id: str) -> dict:
        return next(r for r in self.runs if r["run_id"] == run_id)

    def conforms(self) -> None:
        """Every observation and every run, through P4's validator."""
        for run in self.runs:
            validate_run(run, len(self.observations_for(run["run_id"])))
        for observation in self.observations:
            validate_observation(
                {k: v for k, v in observation.items() if k != "run_id"},
                text_units=[{k: v for k, v in u.items() if k != "run_id"}
                            for u in self.units_for(observation["run_id"])],
            )


@pytest.fixture()
def sink() -> RecordingSink:
    return RecordingSink()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p5/test_p5_shape.py -v`
Expected: PASS — 19 passed

- [ ] **Step 5: Commit**

```bash
git add src/extractors/shape.py src/extractors/sink.py \
        tests/p5/p4_stub.py tests/p5/conftest.py tests/p5/test_p5_shape.py
git commit -m "feat(P5): P4's shape built, the sink seam, and P4's validator stubbed from its SPEC"
```

---

### Task 3: The safety gate — two rules with no override path

**Files:**
- Create: `src/extractors/safety.py`
- Test: `tests/p5/test_p5_safety.py`

**Interfaces:**
- Consumes: nothing. It calls two caller-supplied predicates and nothing else.
- Produces: `SafetyPolicy`, `admit()`, `ProtectedContainerRefused`, `DatalessRefused`, `UNTOUCHED_PROTECTED`.

**These are the two rules Joseph ratified, and neither has an override.**

[`../../11-ops-runtime.md`](../../11-ops-runtime.md) §4b, ratified 2026-08-20: *"An application
bundle, a macOS package, and anything under a system location is a **protected container**… P12 never
moves one, and no policy, approval, or user gesture makes it movable — this is not a default that
review can override, which is what separates it from every other refusal in this design."* P3's SPEC
carries the rule and its label, **`untouched_protected`**. *"What is recorded is the container, not
its contents."*

`11-ops-runtime.md` §5: *"Do not materialize, hash, or extract."* A dataless iCloud item's bytes are
not on this machine and **opening it downloads it**. P1's `hash_file` takes a required `materialized`
keyword and raises `DatalessFileRefused`; P5's obligation is the same one a step earlier — detect
before reading.

**Why both predicates are injected rather than implemented here.** Both detections are **P3's**:
11 §4b puts the protected set in P3's SPEC (*"Membership of the protected set is authored, not
inferred… P3 guesses no new ones at run time"*) and 11 §5 puts dataless detection in P3
(*"P3 detects a dataless / not-downloaded ubiquitous item before hashing"*). O5's reasoning applies
verbatim: *"A second derivation of any of them… is a contract violation, not an optimization, because
the two would drift."* So P5 consumes the verdict. `src/extractors/` contains no `SF_DATALESS`
constant, no `st_flags` read, no `.app` literal and no system-path literal — Task 20 asserts it.

**Why `admit` is called by every extractor and not only by a dispatcher.** "No extractor is reachable
for a path inside a protected container" has to be true of the extractor, not of one caller of it.
Every `extract_*` below takes a `SafetyPolicy` and calls `admit` as its **first statement**, before it
touches its reader. Task 19 parametrizes the refusal across all six and asserts that in every case the
reader was never called and no run was written — which is the only form of the claim that cannot be
bypassed by adding a second caller later.

**`admit` opens nothing and stats nothing.** It calls the two predicates and returns or raises. A
refusal writes no `extraction_runs` row: for a protected container the record is P3's exclusion
verdict, and for a dataless file *"P3 records the detection and writes no run row (P5 writes runs, not
P3)"* — which `completeness` such a file would carry is **P4 Open question 6** and stays open here.

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_safety.py
"""11-ops-runtime.md §4b and §5 — the two ratified rules, and the fact that P5 has
no path around either of them."""
from pathlib import Path

import pytest

from extractors.safety import (
    UNTOUCHED_PROTECTED, DatalessRefused, ProtectedContainerRefused, SafetyPolicy,
    admit,
)

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)


def test_an_ordinary_path_is_admitted():
    assert admit(Path("/corpus/Syllabus.pdf"), policy=OPEN_POLICY) is None


def test_a_path_inside_a_protected_container_is_refused():
    # 11 §4b: "P3 does not descend into one... P12 never moves one, and no policy,
    # approval, or user gesture makes it movable."
    policy = SafetyPolicy(
        is_protected_container=lambda path: "Preview.app" in str(path),
        is_dataless=lambda path: False,
    )
    with pytest.raises(ProtectedContainerRefused):
        admit(Path("/Applications/Preview.app/Contents/Resources/help.pdf"),
              policy=policy)


def test_the_label_is_p3s_word_and_p5_coins_no_second_one():
    # P3's SPEC: "The label is `untouched_protected`, and it is a statement about the
    # product's restraint, not about the file."
    assert UNTOUCHED_PROTECTED == "untouched_protected"


def test_there_is_no_override_argument_anywhere_in_the_signature():
    # 11 §4b: "no policy, approval, or user gesture makes it movable - this is not a
    # default that review can override." A keyword that could turn the rule off would
    # be that override, so there is none to pass.
    import inspect
    parameters = set(inspect.signature(admit).parameters)
    assert parameters == {"path", "policy"}
    for forbidden in ("force", "override", "allow_protected", "approved", "consent"):
        assert forbidden not in parameters
    policy_fields = set(SafetyPolicy.__dataclass_fields__)
    assert policy_fields == {"is_protected_container", "is_dataless"}


def test_a_dataless_file_is_refused_before_anything_reads_it():
    # 11 §5: "Do not materialize, hash, or extract."
    policy = SafetyPolicy(is_protected_container=lambda path: False,
                          is_dataless=lambda path: True)
    with pytest.raises(DatalessRefused):
        admit(Path("/corpus/Thesis.pdf"), policy=policy)


def test_the_protected_check_runs_before_the_dataless_check():
    # Inside a protected container P5 must not even ask a question about the file:
    # asking is a stat of its contents, which 11 §4b forbids.
    asked = []

    def is_dataless(path):
        asked.append(path)
        return False

    policy = SafetyPolicy(is_protected_container=lambda path: True,
                          is_dataless=is_dataless)
    with pytest.raises(ProtectedContainerRefused):
        admit(Path("/Applications/Thing.app/x.pdf"), policy=policy)
    assert asked == []


def test_the_gate_opens_nothing_and_stats_nothing():
    # Detection is a filesystem observation made by P3 (11 §5); P5 consumes the
    # verdict. A second derivation would drift (O5), so there is nothing here to
    # drift from: this module reads no bytes and no stat result.
    import extractors.safety as module
    source = Path(module.__file__).read_text()
    for forbidden in ("open(", "read_bytes", "os.stat", "st_flags", "hash_file",
                      "SF_DATALESS"):
        assert forbidden not in source, forbidden


def test_a_refusal_writes_no_extraction_run(sink):
    policy = SafetyPolicy(is_protected_container=lambda path: False,
                          is_dataless=lambda path: True)
    with pytest.raises(DatalessRefused):
        admit(Path("/corpus/Thesis.pdf"), policy=policy)
    # P4 Open question 6 stays open: none of P4's eight completeness values means
    # "the bytes are not on this machine", and P5 chooses none and adds no ninth.
    assert sink.runs == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_safety.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'extractors.safety'`

- [ ] **Step 3: Write the implementation**

```python
# src/extractors/safety.py
"""The one gate every extractor passes through. Two rules, no override path.

11-ops-runtime.md section 4b (ratified 2026-08-20): "An application bundle, a macOS
package, and anything under a system location is a protected container... P12 never
moves one, and no policy, approval, or user gesture makes it movable - this is not a
default that review can override, which is what separates it from every other refusal
in this design." What is recorded is the container, not its contents.

11-ops-runtime.md section 5: "Do not materialize, hash, or extract." A dataless
iCloud item's bytes are not on this machine and OPENING it downloads it.

Both detections belong to P3 (its SPEC authors the protected set; 11 section 5 assigns
dataless detection to P3 "before hashing"), so both arrive here as caller-supplied
predicates. O5's reasoning applies verbatim: a second derivation of a value another
part computes is a contract violation, not an optimization, because the two would
drift. This module therefore reads no bytes, no stat result and no platform constant.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

#: P3's word, quoted rather than coined. A statement about the product's restraint,
#: not about the file.
UNTOUCHED_PROTECTED = "untouched_protected"


class ProtectedContainerRefused(Exception):
    """11 section 4b. There is no argument that turns this off."""


class DatalessRefused(Exception):
    """11 section 5. The bytes are not on this machine; reading would download them."""


@dataclass(frozen=True)
class SafetyPolicy:
    """P3's two verdicts, as P5 consumes them.

    Two fields, and deliberately no third: a `force`, `override` or `approved` field
    would be the override 11 section 4b says does not exist.
    """
    is_protected_container: Callable[[Path], bool]
    is_dataless: Callable[[Path], bool]


def admit(path: Path, *, policy: SafetyPolicy) -> None:
    """Raise if this path may not be read at all. Otherwise return None.

    Called as the FIRST statement of every extractor, before its reader is touched,
    so that "no extractor is reachable for a path inside a protected container" is a
    property of the extractor rather than of one of its callers.

    The protected check runs first: inside a protected container P5 must not even ask
    a question about the file, because asking is a stat of its contents.
    """
    if policy.is_protected_container(path):
        raise ProtectedContainerRefused(
            f"{path} is inside a protected container and is recorded as "
            f"{UNTOUCHED_PROTECTED}; its contents are never entered "
            "(11-ops-runtime.md section 4b). There is no override."
        )
    if policy.is_dataless(path):
        raise DatalessRefused(
            f"{path} is a dataless (not-downloaded) item; reading it would download "
            "it (11-ops-runtime.md section 5). P5 writes no run row for it, and "
            "which completeness such a file carries is P4 Open question 6."
        )
    return None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p5/test_p5_safety.py -v`
Expected: PASS — 8 passed

- [ ] **Step 5: Commit**

```bash
git add src/extractors/safety.py tests/p5/test_p5_safety.py
git commit -m "feat(P5): the safety gate - protected containers and dataless files, no override"
```

---

### Task 4: R — the router (§2.9), signature over extension

**Files:**
- Create: `src/extractors/router.py`
- Create: `src/extractors/schema.py`
- Test: `tests/p5/test_p5_router.py`

**Interfaces:**
- Consumes: `database_agent.db.create_schema`; a caller-supplied `detect_format(path) -> str | None`.
- Produces: `router.SOURCE_TYPE_BY_FORMAT`, `router.HANDLER_BY_FORMAT`, `router.HANDLER_BY_SOURCE_TYPE`, `router.UNROUTED_COMPLETENESS`, `router.RoutingDecision`, `router.route()`, `router.record_routing_decision()`, `router.routing_decisions()`, `router.ROUTING_DDL`, `schema.create_extraction_schema()`.

**§2.9's rule, and the fixture that proves it.** *"The engine should treat the file extension as a
routing signal rather than an assumption about meaning, inspect the real MIME type or file signature
where possible, and dispatch each file to a type-specific extractor."* P5's fixture: **`report.txt`
that is a ZIP by signature routes to E4.** The detected format wins; the disagreement is recorded, not
discarded.

**`detect_format` is injected, and returns one of §2.9's format tokens.** A real deployment maps
libmagic's MIME type or macOS's `UTType` onto that token space; **that mapping belongs to the reader**,
because the MIME and UTType vocabularies are external, versioned and enormous, and copying a slice of
one into `src/extractors/` would be an invented table with no § behind it. What P5 owns is the table
P4 explicitly defers to it — *"MIME/signature → extractor routing table | §2.9 | P5."*

**Every key in `SOURCE_TYPE_BY_FORMAT` is a format §2.9 or §2.6 names**, and no key is anything else.
The value is a **tuple**, because §2.9 lists two formats twice and specifies different field lists for
each with no tiebreak — that is **SPEC Open question 2** and it is not answered here:

- `pdf` is under *Text documents* and under *Presentations* ("PDF slide decks");
- `csv` is under *Spreadsheets* and under *Code, notebooks, config, structured data*.

Both candidates are recorded on the decision. The operative `source_type` is the **first** candidate,
which is §2.9's own document order and not a preference of P5's — there is no preference constant to
find, and Task 20's guard says so and names OQ2.

**Three families are enumerated by the design and one is not.** §2.9 names formats for text documents,
spreadsheets, presentations, email, calendar, contacts, code/structured and design/creative; §2.6 names
HEIC and PNG for images and P5's own fixture set names `.jpg`. §2.9's **audio and video** bullet names
**no format at all**, so the table contains no audio/video key: routing to that family has nothing to
key on. The handler exists and is tested (Task 11) — only the routing entry is missing, and it is a
**NEEDS JOSEPH** item, not an invention to make here.

**What a file with no handler gets.** §2.4 is explicit: *"The system should never silently treat an
unsupported format as an empty document, because an empty extraction result is different from an
extractor that does not yet exist."* So the router says which of P4's values applies:

| case | `unrouted_completeness` | § |
|---|---|---|
| format known, family has no handler yet (`psd`, `ai`) | `unreadable` — and the run still carries metadata-level rows (M3) | §2.9 design/creative |
| `opaque_binary` (`dmg`, `bin`) | `metadata_only` — §2.9's deliberate safe stop | §2.9 |
| format not in the table at all | `unsupported` — no extractor exists | §2.4, §2.9 |

**One P5-owned table, and only one.** `extraction_routing` records the decision per
(file × content hash × router version). P5 creates **no** P4 table: `evidence`, `extraction_runs` and
`text_units` are P4's, and Task 20 asserts `create_extraction_schema` creates neither.

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_router.py
"""R - §2.9's routing. Done-means 10: "Routing follows signature over extension on
the disagreeing fixture, and each §2.9 family either has its handler or an explicit
`unsupported` status.\""""
from pathlib import Path

import pytest

from database_agent.db import create_schema

from extractors.router import (
    HANDLER_BY_FORMAT, HANDLER_BY_SOURCE_TYPE, SOURCE_TYPE_BY_FORMAT,
    record_routing_decision, route, routing_decisions,
)
from extractors.schema import create_extraction_schema


def detector(mapping):
    return lambda path: mapping.get(path.name)


def test_a_txt_that_is_a_zip_by_signature_routes_to_the_archive_extractor():
    # SPEC fixture: "`report.txt` that is a ZIP by signature | §2.9 | routes by
    # signature, not extension."
    decision = route(file_id="f1", content_hash="sha256:abc",
                     path=Path("/corpus/report.txt"), extension=".txt",
                     detect_format=detector({"report.txt": "zip"}))
    assert decision.detected_format == "zip"
    assert decision.declared_extension == ".txt"
    assert decision.disagree is True
    assert decision.source_type == "archive"
    assert decision.extractor_name == "archive.manifest"


def test_agreement_is_recorded_as_agreement():
    decision = route(file_id="f1", content_hash="sha256:abc",
                     path=Path("/corpus/Syllabus.pdf"), extension=".pdf",
                     detect_format=detector({"Syllabus.pdf": "pdf"}))
    assert decision.disagree is False
    assert decision.extractor_name == "pdf.text"


def test_the_extension_is_used_when_the_detector_cannot_identify_the_file():
    # §2.9: "inspect the real MIME type or file signature WHERE POSSIBLE".
    decision = route(file_id="f1", content_hash="sha256:abc",
                     path=Path("/corpus/notes.md"), extension=".md",
                     detect_format=lambda path: None)
    assert decision.detected_format is None
    assert decision.disagree is False
    assert decision.source_type == "text_document"
    assert decision.extractor_name == "text.structured"


def test_pdf_and_csv_carry_both_of_the_families_2_9_lists_them_under():
    # SPEC Open question 2: "Routing precedence for formats §2.9 lists twice. CSV
    # appears under both Spreadsheets and Code/structured data; PDF appears under
    # both Text documents and Presentations. The design specifies different field
    # lists for each and no tiebreak." Not answered here.
    assert SOURCE_TYPE_BY_FORMAT["pdf"] == ("text_document", "presentation")
    assert SOURCE_TYPE_BY_FORMAT["csv"] == ("spreadsheet", "code_structured")
    decision = route(file_id="f1", content_hash="sha256:abc",
                     path=Path("/corpus/grades.csv"), extension=".csv",
                     detect_format=detector({"grades.csv": "csv"}))
    assert decision.source_type_candidates == ("spreadsheet", "code_structured")
    assert decision.source_type == "spreadsheet"      # §2.9's document order, not a preference


def test_every_format_in_the_table_is_one_2_9_or_2_6_names():
    # No invented membership: each key is a format the design spells.
    named_by_2_9 = {
        "pdf", "docx", "rtf", "txt", "md", "html", "epub", "odt",          # text documents
        "xlsx", "xls", "csv", "tsv", "ods", "numbers",                     # spreadsheets
        "pptx", "ppt", "odp",                                              # presentations
        "eml", "mbox", "msg",                                              # email
        "ics", "vcf",                                                      # calendar, contacts
        "py", "js", "sql", "ipynb", "json", "yaml", "yml", "toml", "xml",  # code/structured
        "psd", "ai", "svg",                                                # design/creative
        "zip",                                                             # archives
        "dmg", "bin",                                                      # opaque binary
    }
    named_by_2_6_or_the_spec_fixtures = {"heic", "png", "jpg", "jpeg"}
    assert set(SOURCE_TYPE_BY_FORMAT) == named_by_2_9 | named_by_2_6_or_the_spec_fixtures


def test_no_audio_or_video_format_is_enumerated():
    # §2.9's audio-and-video bullet names a family and NO format. There is nothing to
    # key routing on, so the table has no entry and P5 invents none. The handler is
    # built and tested (Task 11); the routing entry is a NEEDS JOSEPH item.
    assert not [fmt for fmt, families in SOURCE_TYPE_BY_FORMAT.items()
                if "audio_video" in families]


def test_an_unknown_format_is_unsupported_and_never_an_empty_document():
    # §2.4: "an empty extraction result is different from an extractor that does not
    # yet exist."
    decision = route(file_id="f1", content_hash="sha256:abc",
                     path=Path("/corpus/thing.qqq"), extension=".qqq",
                     detect_format=lambda path: None)
    assert decision.extractor_name is None
    assert decision.unrouted_completeness == "unsupported"


def test_a_disk_image_and_an_executable_stop_at_metadata_only():
    # SPEC fixture: "`archive.dmg`, `tool.bin` | §2.9 | `metadata_only`."
    for name, extension, fmt in (("archive.dmg", ".dmg", "dmg"),
                                 ("tool.bin", ".bin", "bin")):
        decision = route(file_id="f1", content_hash="sha256:abc",
                         path=Path("/corpus") / name, extension=extension,
                         detect_format=detector({name: fmt}))
        assert decision.source_type == "opaque_binary"
        assert decision.extractor_name is None
        assert decision.unrouted_completeness == "metadata_only"


def test_a_proprietary_design_format_is_unreadable_not_unsupported():
    # SPEC fixture: "`design.psd` | §2.9 | `unreadable` carrying metadata-level
    # observations (M3) - indexed-but-unreadable, never zero rows."
    decision = route(file_id="f1", content_hash="sha256:abc",
                     path=Path("/corpus/design.psd"), extension=".psd",
                     detect_format=detector({"design.psd": "psd"}))
    assert decision.source_type == "design_creative"
    assert decision.extractor_name is None
    assert decision.unrouted_completeness == "unreadable"


def test_svg_routes_to_the_image_extractor():
    # SPEC routing table: design and creative -> "E5 (raster/SVG), else `unreadable`".
    decision = route(file_id="f1", content_hash="sha256:abc",
                     path=Path("/corpus/logo.svg"), extension=".svg",
                     detect_format=detector({"logo.svg": "svg"}))
    assert decision.extractor_name == "image.metadata"


def test_the_four_core_families_reach_their_named_handlers():
    assert HANDLER_BY_FORMAT["pdf"] == "pdf.text"
    assert HANDLER_BY_FORMAT["docx"] == "docx.structure"
    assert HANDLER_BY_SOURCE_TYPE["archive"] == "archive.manifest"
    assert HANDLER_BY_SOURCE_TYPE["image"] == "image.metadata"
    for family in ("text_document", "spreadsheet", "presentation", "email",
                   "calendar", "contacts", "code_structured", "audio_video"):
        assert HANDLER_BY_SOURCE_TYPE[family] == "text.structured"


def test_pdf_slide_decks_route_to_e1_and_the_question_stays_open():
    # SPEC routing table: "Presentations | ... PDF slide decks | ... | E3 (PDF decks:
    # E1)". There is no deck detection anywhere: distinguishing a slide deck from a
    # document is OQ2's other half and is not answered in code.
    decision = route(file_id="f1", content_hash="sha256:abc",
                     path=Path("/corpus/deck.pdf"), extension=".pdf",
                     detect_format=detector({"deck.pdf": "pdf"}))
    assert decision.extractor_name == "pdf.text"
    assert "presentation" in decision.source_type_candidates


def test_the_decision_is_recorded_and_readable(conn):
    create_schema(conn)
    create_extraction_schema(conn)
    decision = route(file_id="f1", content_hash="sha256:abc",
                     path=Path("/corpus/report.txt"), extension=".txt",
                     detect_format=detector({"report.txt": "zip"}))
    record_routing_decision(conn, decision)
    rows = routing_decisions(conn, "f1", "sha256:abc")
    assert len(rows) == 1
    assert rows[0]["detected_format"] == "zip"
    assert rows[0]["declared_extension"] == ".txt"
    assert rows[0]["disagree"] == 1
    assert rows[0]["source_type"] == "archive"
    assert rows[0]["extractor_name"] == "archive.manifest"


def test_p5_creates_no_p4_table(conn):
    # `evidence`, `extraction_runs` and `text_units` are P4's. P5 writes them through
    # the sink and creates none of them.
    create_schema(conn)
    create_extraction_schema(conn)
    tables = {r["name"] for r in
              conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "extraction_routing" in tables
    for p4_table in ("evidence", "extraction_runs", "text_units"):
        assert p4_table not in tables


def test_the_schema_is_idempotent(conn):
    create_schema(conn)
    create_extraction_schema(conn)
    create_extraction_schema(conn)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_router.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'extractors.router'`

- [ ] **Step 3: Write the implementation**

```python
# src/extractors/router.py
"""R - the router (section 2.9).

"The engine should treat the file extension as a ROUTING SIGNAL rather than an
assumption about meaning, inspect the real MIME type or file signature where
possible, and dispatch each file to a type-specific extractor."

`detect_format` is injected and returns one of the format tokens below. A real
deployment maps libmagic's MIME type or macOS's UTType onto that token space, and
THAT mapping belongs to the reader: the MIME and UTType vocabularies are external,
versioned and enormous, and copying a slice of one in here would be an invented table
with no section behind it. What P5 owns is the table P4 explicitly defers to it -
"MIME/signature -> extractor routing table | section 2.9 | P5".

Every key below is a format section 2.9 or section 2.6 names. Nothing else is a key.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

#: The router's own version, part of the routing decision's identity.
VERSION = "0.1.0"

#: Section 2.9's eleven bullets and section 2.6's images, as (format token ->
#: source_type candidates). The value is a TUPLE because section 2.9 lists two
#: formats twice and gives each a different field list with no tiebreak - SPEC Open
#: question 2. The operative choice is the FIRST candidate, which is section 2.9's
#: own document order and not a preference of P5's.
SOURCE_TYPE_BY_FORMAT: dict[str, tuple[str, ...]] = {
    # Text documents - "PDF, DOCX, RTF, TXT, Markdown, HTML, EPUB, OpenDocument"
    "pdf": ("text_document", "presentation"),   # also "PDF slide decks" - OQ2
    "docx": ("text_document",),
    "rtf": ("text_document",),
    "txt": ("text_document",),
    "md": ("text_document",),
    "html": ("text_document",),
    "epub": ("text_document",),
    "odt": ("text_document",),
    # Spreadsheets - "XLSX, XLS, CSV, TSV, ODS, Numbers exports"
    "xlsx": ("spreadsheet",),
    "xls": ("spreadsheet",),
    "csv": ("spreadsheet", "code_structured"),  # listed under both - OQ2
    "tsv": ("spreadsheet",),
    "ods": ("spreadsheet",),
    "numbers": ("spreadsheet",),
    # Presentations - "PPTX, PPT, ODP, PDF slide decks"
    "pptx": ("presentation",),
    "ppt": ("presentation",),
    "odp": ("presentation",),
    # Email - "EML, MBOX, MSG, exported mail archives"
    "eml": ("email",),
    "mbox": ("email",),
    "msg": ("email",),
    # Calendar - "ICS"; Contacts - "VCF"
    "ics": ("calendar",),
    "vcf": ("contacts",),
    # Code, notebooks, config, structured data - "Python, JavaScript, SQL, Jupyter
    # notebooks, JSON, YAML, TOML, XML, CSV"
    "py": ("code_structured",),
    "js": ("code_structured",),
    "sql": ("code_structured",),
    "ipynb": ("code_structured",),
    "json": ("code_structured",),
    "yaml": ("code_structured",),
    "yml": ("code_structured",),
    "toml": ("code_structured",),
    "xml": ("code_structured",),
    # Design and creative - "PSD, AI, SVG, Figma exports, CAD files, 3D files".
    # Figma exports, CAD and 3D name no single format token, so none is invented.
    "psd": ("design_creative",),
    "ai": ("design_creative",),
    "svg": ("design_creative",),
    # Images - section 2.6 names HEIC and PNG; the SPEC's fixture set names .jpg.
    "heic": ("image",),
    "png": ("image",),
    "jpg": ("image",),
    "jpeg": ("image",),
    # Compressed archives - "Yield their manifests without extraction."
    "zip": ("archive",),
    # Disk images, executables, databases, encrypted containers, damaged files,
    # unknown binary. Section 2.9 names no format; the SPEC's fixtures name two.
    "dmg": ("opaque_binary",),
    "bin": ("opaque_binary",),
    # Audio and video: section 2.9 names a family and NO format, so there is nothing
    # to key routing on and no entry is invented here. See NEEDS JOSEPH.
}

#: Two formats have a dedicated extractor of their own (sections 2.2 and 2.3).
HANDLER_BY_FORMAT: dict[str, str] = {
    "pdf": "pdf.text",
    "docx": "docx.structure",
}

#: Everything else routes by family. `None` means "no extractor exists for this
#: family", which is a statement about the product, not about the file.
HANDLER_BY_SOURCE_TYPE: dict[str, str | None] = {
    "text_document": "text.structured",
    "spreadsheet": "text.structured",
    "presentation": "text.structured",
    "email": "text.structured",
    "calendar": "text.structured",
    "contacts": "text.structured",
    "code_structured": "text.structured",
    "audio_video": "text.structured",
    "archive": "archive.manifest",
    "image": "image.metadata",
    "design_creative": None,          # raster and SVG are re-routed below
    "opaque_binary": None,
}

#: Section 2.9's design-and-creative bullet: "at minimum yield filename, format,
#: dimensions ... unsupported proprietary formats should be recorded as
#: indexed-but-unreadable rather than silently treated as empty." The SPEC's routing
#: table reads "E5 (raster/SVG), else `unreadable`".
IMAGE_CAPABLE_DESIGN_FORMATS: tuple[str, ...] = ("svg",)

#: Which of P4's values a file with no handler carries. Section 2.4: an unsupported
#: format is never silently an empty document.
UNROUTED_COMPLETENESS: dict[str, str] = {
    "design_creative": "unreadable",     # M3 - and it still carries metadata rows
    "opaque_binary": "metadata_only",    # section 2.9's deliberate safe stop
}


@dataclass(frozen=True)
class RoutingDecision:
    """Contract out R - "Every file leaves the router with exactly one routing
    decision"."""
    file_id: str
    content_hash: str
    detected_format: str | None
    declared_extension: str
    disagree: bool
    source_type: str | None
    source_type_candidates: tuple[str, ...]
    extractor_name: str | None
    router_version: str
    unrouted_completeness: str | None


def route(*, file_id: str, content_hash: str, path: Path, extension: str,
          detect_format: Callable[[Path], str | None]) -> RoutingDecision:
    """Decide which extractor family handles this file. Reads nothing itself.

    Section 2.9: the detected format wins over the declared extension, and the
    disagreement is recorded rather than discarded.
    """
    detected = detect_format(path)
    declared = extension.lower().lstrip(".")
    operative = detected if detected is not None else declared
    disagree = detected is not None and detected != declared

    candidates = SOURCE_TYPE_BY_FORMAT.get(operative, ())
    source_type = candidates[0] if candidates else None

    handler = HANDLER_BY_FORMAT.get(operative)
    if handler is None and source_type is not None:
        handler = HANDLER_BY_SOURCE_TYPE.get(source_type)
        if (handler is None and source_type == "design_creative"
                and operative in IMAGE_CAPABLE_DESIGN_FORMATS):
            handler = HANDLER_BY_SOURCE_TYPE["image"]

    unrouted = None
    if handler is None:
        unrouted = UNROUTED_COMPLETENESS.get(source_type, "unsupported")

    return RoutingDecision(
        file_id=file_id,
        content_hash=content_hash,
        detected_format=detected,
        declared_extension=extension,
        disagree=disagree,
        source_type=source_type,
        source_type_candidates=candidates,
        extractor_name=handler,
        router_version=VERSION,
        unrouted_completeness=unrouted,
    )


ROUTING_DDL = """
CREATE TABLE IF NOT EXISTS extraction_routing (
    routing_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id                TEXT NOT NULL,
    content_hash           TEXT NOT NULL,
    detected_format        TEXT,
    declared_extension     TEXT NOT NULL,
    disagree               INTEGER NOT NULL,
    source_type            TEXT,
    source_type_candidates TEXT NOT NULL,
    extractor_name         TEXT,
    router_version         TEXT NOT NULL,
    unrouted_completeness  TEXT,
    observed_at            TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS extraction_routing_file
    ON extraction_routing (file_id, content_hash);
"""


def record_routing_decision(conn: sqlite3.Connection,
                            decision: RoutingDecision) -> int:
    """Persist the decision. This is P5's own record, not one of P4's three."""
    cursor = conn.execute(
        "INSERT INTO extraction_routing (file_id, content_hash, detected_format, "
        "declared_extension, disagree, source_type, source_type_candidates, "
        "extractor_name, router_version, unrouted_completeness, observed_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (decision.file_id, decision.content_hash, decision.detected_format,
         decision.declared_extension, int(decision.disagree), decision.source_type,
         ",".join(decision.source_type_candidates), decision.extractor_name,
         decision.router_version, decision.unrouted_completeness,
         datetime.now(timezone.utc).isoformat()),
    )
    return cursor.lastrowid


def routing_decisions(conn: sqlite3.Connection, file_id: str,
                      content_hash: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM extraction_routing WHERE file_id = ? AND content_hash = ? "
        "ORDER BY routing_id", (file_id, content_hash),
    ).fetchall()
```

```python
# src/extractors/schema.py
"""P5's own tables. They live inside P1's single local SQLite database (section 0);
P1 owns the handle, the transaction boundary, `files` and `events`.

P5 creates NO P4 table: `evidence`, `extraction_runs` and `text_units` are P4's, and
P5 writes them through the sink (src/extractors/sink.py).
"""
from __future__ import annotations

import sqlite3

from extractors.router import ROUTING_DDL


def create_extraction_schema(conn: sqlite3.Connection) -> None:
    """Create every P5-owned table. Idempotent. P1's `create_schema` runs first."""
    conn.executescript(ROUTING_DDL)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p5/test_p5_router.py -v`
Expected: PASS — 15 passed

- [ ] **Step 5: Commit**

```bash
git add src/extractors/router.py src/extractors/schema.py tests/p5/test_p5_router.py
git commit -m "feat(P5): the router - signature over extension, §2.9's family table, OQ2 held open"
```

---

### Task 5: `extraction_runs` — coverage, the §3.4 cache key, and the four analysis tiers

**Files:**
- Create: `src/extractors/runs.py`
- Test: `tests/p5/test_p5_runs.py`

**Interfaces:**
- Consumes: `extractors.shape.canonical_json`, `extractors.shape.P5_ANALYSIS_TIERS`.
- Produces: `ANALYSIS_TIER_BY_EXTRACTOR`, `coverage()`, `cache_key()`, `extraction_status_by_tier()`, `TierConflict`.

**P5 writes P4's outcome record and no second one (B1).** *"P5 keeps its router table (format →
extractor); P4 explicitly defers that to P5. P5 deletes its status enum and restates its §8.6 counting
rules against P4's values."* This module holds the three derived things P5 owes about a run and
nothing that names an outcome.

**The tier map is P5's, because I4 gave P5 the vocabulary.** P5's SPEC: *"`analysis_tier` is closed
(I4): `filesystem | native | ocr | llm`. P5 writes the first three and never writes `llm`. Mapping:
filesystem observations re-emitted as `source_type: filesystem` are `filesystem`; E1–E5 are `native`;
E6 is `ocr`."* That is the whole table, keyed by extractor name, and `run()` in Task 2 already refuses
`llm` structurally.

**The cache key is §3.4's, quoted.** P5's SPEC: *"Content hash + extractor version + `analysis_tier`,
plus provider/version/configuration for OCR. This is what makes a rename free and a content rewrite
expensive, and what makes an extractor upgrade auditable."* Provider is `extractor_name` and
configuration is `config_fingerprint` (Task 2), so one function covers both the OCR and non-OCR cases
without an OCR-specific shape (B1). The **path is not in the key** — that is what "a rename is free"
means, and the test asserts it by never being given one.

**`extraction_status_by_tier` is computed, not written.** §8.2's file record carries *"extraction
status by extractor tier"* and P1 stores it opaquely on `files.extraction_status_by_tier` — but **P1
publishes no setter for it**, and `files` is P1's table, so P5 does not `UPDATE` it. This module
produces the map; a caller hands it to P1. *That missing P1 function is reported, not patched here.*

**Two runs at one tier are not collapsed silently.** In the normal case each tier has at most one run
per file — the router selects one native extractor, the filesystem record is its own run, and OCR is
its own tier — so the map is well defined. If two runs ever land on one tier with different
`completeness`, that is a modelling problem the design does not rule on, and this module raises
`TierConflict` rather than picking a winner. Held open in Task 20.

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_runs.py
"""P4's `extraction_runs`, from P5's side: coverage, §3.4's cache key, and the four
analysis tiers I4 closed."""
import pytest

from extractors.runs import (
    ANALYSIS_TIER_BY_EXTRACTOR, TierConflict, cache_key, coverage,
    extraction_status_by_tier,
)


def a_run(**overrides):
    row = dict(extractor_name="pdf.text", analysis_tier="native",
               completeness="complete")
    row.update(overrides)
    return row


def test_coverage_is_p4s_three_keys_and_nothing_else():
    assert coverage("pages", 40, 312) == {"units": "pages", "processed": 40,
                                          "total": 312}


def test_coverage_refuses_to_claim_more_progress_than_there_is():
    with pytest.raises(ValueError):
        coverage("pages", 400, 312)
    with pytest.raises(ValueError):
        coverage("pages", -1, 312)


def test_the_tier_map_is_i4s_four_names_and_p5_writes_three_of_them():
    # SPEC: "filesystem observations re-emitted as `source_type: filesystem` are
    # `filesystem`; E1-E5 are `native`; E6 is `ocr`." P8 is the only writer of `llm`.
    assert ANALYSIS_TIER_BY_EXTRACTOR["filesystem.record"] == "filesystem"
    for native in ("pdf.text", "docx.structure", "text.structured",
                   "archive.manifest", "image.metadata"):
        assert ANALYSIS_TIER_BY_EXTRACTOR[native] == "native"
    assert set(ANALYSIS_TIER_BY_EXTRACTOR.values()) == {"filesystem", "native"}


def test_an_ocr_extractor_name_is_recognised_by_its_prefix():
    # §2.7's provider is named by the engine, not by P5 (S1 makes Apple Vision the
    # one engine v1 ships, and the engine reports its own name). The tier is keyed on
    # the family prefix so a new provider needs no edit here.
    from extractors.runs import analysis_tier_for
    assert analysis_tier_for("ocr.apple_vision") == "ocr"
    assert analysis_tier_for("pdf.text") == "native"
    assert analysis_tier_for("filesystem.record") == "filesystem"


def test_an_unknown_extractor_name_has_no_tier_and_is_not_guessed():
    from extractors.runs import analysis_tier_for
    with pytest.raises(KeyError):
        analysis_tier_for("something.new")


def test_a_rename_is_free_because_the_path_is_not_in_the_cache_key():
    # §3.4, quoted in the SPEC: "This is what makes a rename free and a content
    # rewrite expensive." There is no path parameter to pass.
    import inspect
    assert "path" not in inspect.signature(cache_key).parameters
    first = cache_key(content_hash="sha256:abc", extractor_name="pdf.text",
                      extractor_version="0.1.0", analysis_tier="native",
                      config_fingerprint="sha256:cfg")
    second = cache_key(content_hash="sha256:abc", extractor_name="pdf.text",
                       extractor_version="0.1.0", analysis_tier="native",
                       config_fingerprint="sha256:cfg")
    assert first == second


def test_a_content_rewrite_an_upgrade_and_a_config_change_each_change_the_key():
    base = dict(content_hash="sha256:abc", extractor_name="pdf.text",
                extractor_version="0.1.0", analysis_tier="native",
                config_fingerprint="sha256:cfg")
    original = cache_key(**base)
    assert cache_key(**{**base, "content_hash": "sha256:def"}) != original
    assert cache_key(**{**base, "extractor_version": "0.2.0"}) != original
    assert cache_key(**{**base, "analysis_tier": "ocr"}) != original
    assert cache_key(**{**base, "config_fingerprint": "sha256:other"}) != original
    # §2.7's provider is part of the key for OCR, and it is `extractor_name`: there
    # is no OCR-specific key shape (B1).
    assert cache_key(**{**base, "extractor_name": "ocr.apple_vision"}) != original


def test_the_status_map_names_only_the_tiers_that_were_attempted():
    # SPEC: "a missing key means that tier was not attempted."
    runs = [a_run(extractor_name="filesystem.record", analysis_tier="filesystem"),
            a_run(extractor_name="image.metadata", analysis_tier="native"),
            a_run(extractor_name="ocr.apple_vision", analysis_tier="ocr",
                  completeness="capped")]
    assert extraction_status_by_tier(runs) == {
        "filesystem": "complete", "native": "complete", "ocr": "capped"}


def test_an_image_that_ran_e5_and_e6_says_exif_succeeded_and_ocr_capped():
    # B1's own sentence: an opaque image "produces two rows and can say 'EXIF read
    # successfully, OCR capped.' A per-file status could not express that."
    runs = [a_run(extractor_name="image.metadata", analysis_tier="native",
                  completeness="complete"),
            a_run(extractor_name="ocr.apple_vision", analysis_tier="ocr",
                  completeness="capped")]
    status = extraction_status_by_tier(runs)
    assert status["native"] == "complete"
    assert status["ocr"] == "capped"


def test_two_runs_at_one_tier_that_disagree_are_not_collapsed_silently():
    # The design does not rule on this and P5 does not pick a winner.
    runs = [a_run(analysis_tier="native", completeness="complete"),
            a_run(analysis_tier="native", completeness="failed")]
    with pytest.raises(TierConflict):
        extraction_status_by_tier(runs)


def test_p5_never_puts_llm_in_the_status_map():
    runs = [a_run(analysis_tier="llm", completeness="complete")]
    with pytest.raises(ValueError):
        extraction_status_by_tier(runs)


def test_the_module_writes_nothing_to_the_files_table():
    # P1 publishes no setter for `files.extraction_status_by_tier`, and `files` is
    # P1's table. This module computes the map and a caller hands it over.
    from pathlib import Path

    import extractors.runs as module
    source = Path(module.__file__).read_text().upper()
    assert "UPDATE FILES" not in source
    assert "INSERT INTO FILES" not in source
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_runs.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'extractors.runs'`

- [ ] **Step 3: Write the implementation**

```python
# src/extractors/runs.py
"""What P5 owes about a run, derived - and nothing that names an outcome.

B1: "P4's `extraction_runs` is THE record. P5's parallel status vocabulary is
deleted." The eight `completeness` values are P4's and are not restated here; what is
here is the coverage helper, section 3.4's cache key, and the analysis-tier map I4
gave P5.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from extractors.shape import ANALYSIS_TIERS, canonical_json

#: I4, closed. SPEC: "filesystem observations re-emitted as `source_type: filesystem`
#: are `filesystem`; E1-E5 are `native`; E6 is `ocr`."
ANALYSIS_TIER_BY_EXTRACTOR: dict[str, str] = {
    "filesystem.record": "filesystem",
    "pdf.text": "native",
    "docx.structure": "native",
    "text.structured": "native",
    "archive.manifest": "native",
    "image.metadata": "native",
}

#: Section 2.7's OCR provider is named by the ENGINE, not by P5 - S1 makes Apple
#: Vision the one engine v1 ships and the engine reports its own name and version
#: (section 2.7, "OCR provider and version"). Keying the tier on the family prefix
#: means a second provider needs no edit here and P5 spells no provider name.
OCR_EXTRACTOR_PREFIX = "ocr."


class TierConflict(Exception):
    """Two runs landed on one analysis tier with different outcomes.

    In the normal case each tier has at most one run per file: the router selects one
    native extractor, the filesystem record is its own run, and OCR is its own tier.
    The design does not rule on the collision, so P5 refuses rather than picking a
    winner and losing the other outcome.
    """


def analysis_tier_for(extractor_name: str) -> str:
    """The tier this extractor writes. Never guessed for an unknown name."""
    if extractor_name.startswith(OCR_EXTRACTOR_PREFIX):
        return "ocr"
    return ANALYSIS_TIER_BY_EXTRACTOR[extractor_name]


def coverage(units: str, processed: int, total: int) -> Mapping[str, Any]:
    """P4's `coverage {units, processed, total}` - "says how far it got".

    Section 8.6 needs it to make "89 scanned PDFs deferred after the OCR limit"
    computable rather than estimated, so a run may not claim more progress than the
    work it was given.
    """
    if processed < 0 or total < 0:
        raise ValueError(f"coverage cannot be negative: {processed}/{total}")
    if processed > total:
        raise ValueError(
            f"coverage claims {processed} of {total} {units}; a run cannot process "
            "more units than it had"
        )
    return {"units": units, "processed": processed, "total": total}


def cache_key(*, content_hash: str, extractor_name: str, extractor_version: str,
              analysis_tier: str, config_fingerprint: str) -> str:
    """Section 3.4's key, as the SPEC quotes it: "Content hash + extractor version +
    `analysis_tier`, plus provider/version/configuration for OCR."

    Provider is `extractor_name` and configuration is `config_fingerprint`, so there
    is one key shape and no OCR-specific one (B1). There is no `path` parameter: that
    absence is what "a rename is free and a content rewrite is expensive" means.
    """
    return canonical_json([content_hash, extractor_name, extractor_version,
                           analysis_tier, config_fingerprint])


def extraction_status_by_tier(runs: Iterable[Mapping[str, Any]]) -> dict[str, str]:
    """Section 8.2's "extraction status by extractor tier", as a map.

    A missing key means that tier was not attempted. P1 stores the map opaquely on
    `files.extraction_status_by_tier`; P1 publishes no setter for it and `files` is
    P1's table, so this function computes the map and a caller hands it over.
    """
    status: dict[str, str] = {}
    for run in runs:
        tier = run["analysis_tier"]
        if tier not in ANALYSIS_TIERS:
            raise ValueError(f"{tier!r} is not one of I4's four tiers")
        if tier == "llm":
            raise ValueError("P8 is the only writer of `llm` (I4); P5 writes none")
        existing = status.get(tier)
        if existing is not None and existing != run["completeness"]:
            raise TierConflict(
                f"two runs at tier {tier!r} disagree: {existing!r} and "
                f"{run['completeness']!r}. The design does not rule on this and P5 "
                "does not pick a winner."
            )
        status[tier] = run["completeness"]
    return status
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p5/test_p5_runs.py -v`
Expected: PASS — 12 passed

- [ ] **Step 5: Commit**

```bash
git add src/extractors/runs.py tests/p5/test_p5_runs.py
git commit -m "feat(P5): extraction_runs helpers - coverage, §3.4 cache key, I4's analysis tiers"
```

---

### Task 6: O5 — P3's record, re-emitted as `source_type: filesystem`

**Files:**
- Create: `src/extractors/filesystem.py`
- Test: `tests/p5/test_p5_filesystem.py`

**Interfaces:**
- Consumes: `extractors.shape`, `extractors.safety.admit`, `extractors.runs.coverage`; a P3 `files` row.
- Produces: `VERSION`, `EXTRACTOR_NAME`, `METADATA_SLOTS`, `extract_filesystem()`, `unrouted_result()`.

**O5 in one sentence.** *"P3 computes the §1.2 basic filesystem record; P5 emits `source_type:
filesystem` observations referencing it, **never recomputing it**."* P5's SPEC: *"The §1.2 basic
filesystem record is P3's and P5 never recomputes it; P5 surfaces it as `source_type: filesystem`
observations referencing P3's row, which is how a filename or parent-folder value becomes citable
evidence (§2.2, §2.9, O5)."*

Concretely: this module takes a `files` row and reads values **out of it**. It stats nothing, opens
nothing, hashes nothing, normalizes no filename and determines no MIME type. O5's stated reason is
drift — *"the two would drift and §3.4's cache key is built on the hash."*

**Which of §2.9's basic-extraction fields become observations, and why the rest do not.** §2.9's list
is *"path, filename, normalized filename, extension, MIME type, size, timestamps, content hash,
duplicate and version-family signals, and parent-folder context"* — but that is the list of what P3
**records**, and this module's job is to make citable the ones that are evidence about what a file
*is*:

| §2.9 field | emitted | why |
|---|---|---|
| filename | ✔ zone `filename`, `possible` | §2.2: "a course code or university name found in a **filename**…"; P4 fixture 11 |
| parent-folder context | ✔ zone `path`, `possible` | §2.9's own name for it (MINOR 11); §3.1's "user-approved folder" |
| normalized filename, extension, MIME type | ✔ zone `metadata`, `direct` | named slots on P3's row; `direct` describes the slot |
| size, timestamps | ✘ | G6 assigns the download-session fact to **P6**, *"computed from P3 timestamps"* — P6 reads them from `files`, so a second copy here would be two homes for one value |
| content hash | ✘ | G5 assigns duplicate and version-family signals to **P6**, *"from P1's content hashes and P5's perceptual hashes"* — same reason |
| duplicate and version-family signals | ✘ | G5: P6 computes them. P5 emits the perceptual hash (Task 13) and nothing derived from it |

**One text unit, at `container_path: []`, holding the filename.** P4's fixture 11 is
`filename#0-6` — a *span* into the filename — so a unit must exist for the span to index into
(conformance rule 10), and `text_units` is keyed by `(run_id, container_path)`, which means a run may
hold exactly one unit at `[]`. The filename gets it; the parent-folder observation therefore carries
**no** span and degrades to the coarser address, which is P4's segment-kind rule 4 exactly.

**`unrouted_result` is where §2.4's three-way distinction becomes rows.** A file the router could not
hand to an extractor still gets a run, and which of P4's values it carries decides what a query can
later tell apart:

- `unsupported` — no extractor exists. Zero observations (P4 conformance rule 9).
- `metadata_only` — §2.9's deliberate safe stop. Zero observations from *this* run; **the file is
  still indexed**, through the `filesystem` run above (P4 fixture 19).
- `unreadable` — §2.9's *"recorded as indexed-but-unreadable rather than silently treated as empty"*.
  **Carries metadata-level rows** (M3, P4 fixture 18): filename and format, both taken from P3's row,
  because reading a proprietary format is exactly what there is no library for.

> **P4 SPEC inconsistency, reported not resolved.** P4's fixture 19 says a `metadata_only` run carries
> *"no observations from this extractor"* and that the file *"is still indexed through its `filesystem`
> observations (fixture 11)"*, while P4's conformance-rule-9 note says *"`metadata_only` runs likewise
> carry the metadata-level rows §2.9's basic filesystem extraction produces."* This plan follows
> fixture 19 — the `filesystem` run carries them, the `metadata_only` run carries none — because that
> reading keeps §2.4's `complete`-with-zero / `unsupported` / `metadata_only` distinction intact and
> puts each value in exactly one place. Flagged for P4.

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_filesystem.py
"""O5 - P3's §1.2 record, re-emitted as citable evidence. P4 fixtures 11, 18, 19."""
from pathlib import Path

import pytest

from extractors.filesystem import EXTRACTOR_NAME, extract_filesystem, unrouted_result
from extractors.router import route
from extractors.safety import SafetyPolicy

from conftest import FIXED_CLOCK
from p4_stub import locator_for

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)

FILE_ROW = {
    "file_id": "f1",
    "content_hash": "sha256:abc",
    "filename": "Wash U.docx",
    "normalized_filename": "wash u.docx",
    "extension": ".docx",
    "directory_position": "/Users/jy/Downloads",
    "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "observed_size": 18240,
    "observed_timestamps": "2026-07-17T14:03:22+00:00",
}


def run_it(row=None, **kwargs):
    return extract_filesystem(file_row=row or FILE_ROW,
                              path=Path("/Users/jy/Downloads/Wash U.docx"),
                              policy=OPEN_POLICY, now=FIXED_CLOCK,
                              context_window=40, **kwargs)


def test_the_filename_is_citable_evidence_with_a_span_into_its_own_unit(sink):
    # P4 fixture 11: `filesystem` | `filename#0-6` | `Wash U` | `possible`.
    result = run_it()
    sink.write(result)
    sink.conforms()
    filename = [o for o in sink.observations if o["location"]["zone"] == "filename"]
    assert len(filename) == 1
    assert filename[0]["raw_value"] == "Wash U.docx"
    assert filename[0]["reliability"] == "possible"
    assert locator_for(filename[0]["location"]) == "filename#0-11"
    unit = sink.units_for(filename[0]["run_id"])[0]
    assert unit["container_path"] == ()
    assert unit["text"] == "Wash U.docx"


def test_the_parent_folder_context_is_emitted_under_2_9s_name(sink):
    # MINOR 11: "P5 calls it 'parent-folder context'; P3 calls it 'directory
    # position'. §2.9 says 'parent-folder context'. Ground truth wins."
    result = run_it()
    sink.write(result)
    path_rows = [o for o in sink.observations if o["location"]["zone"] == "path"]
    assert len(path_rows) == 1
    assert path_rows[0]["raw_value"] == "/Users/jy/Downloads"
    assert path_rows[0]["location"]["text_span"] is None    # P4 segment rule 4
    assert locator_for(path_rows[0]["location"]) == "path"


def test_the_named_slots_are_direct_and_the_free_positions_are_possible(sink):
    # P4: "`direct` ... an explicit, labeled, machine-structured slot"; "`possible`
    # ... a filename, or any unlabeled position."
    sink.write(run_it())
    by_locator = {locator_for(o["location"]): o for o in sink.observations}
    assert by_locator["metadata:field=extension"]["reliability"] == "direct"
    assert by_locator["metadata:field=mime_type"]["reliability"] == "direct"
    assert by_locator["metadata:field=normalized_filename"]["reliability"] == "direct"
    assert by_locator["filename#0-11"]["reliability"] == "possible"
    assert by_locator["path"]["reliability"] == "possible"


def test_size_timestamps_and_content_hash_are_not_re_emitted(sink):
    # G5 gives duplicate and version-family signals to P6 "from P1's content hashes";
    # G6 gives the bounded download session to P6 "computed from P3 timestamps". P6
    # reads them from `files`, so a second copy here would be two homes for one value.
    sink.write(run_it())
    emitted = {locator_for(o["location"]) for o in sink.observations}
    for absent in ("metadata:field=observed_size", "metadata:field=observed_timestamps",
                   "metadata:field=content_hash", "metadata:field=version_family",
                   "metadata:field=duplicate_family"):
        assert absent not in emitted


def test_a_null_mime_type_produces_no_row_rather_than_an_empty_one(sink):
    # An observation records presence, never absence (§2.6, P4). A file P3 could not
    # type has no mime_type row, and the `complete` run IS the record of that.
    sink.write(run_it({**FILE_ROW, "mime_type": None}))
    emitted = {locator_for(o["location"]) for o in sink.observations}
    assert "metadata:field=mime_type" not in emitted
    assert sink.runs[0]["completeness"] == "complete"
    sink.conforms()


def test_the_run_is_the_filesystem_tier(sink):
    sink.write(run_it())
    row = sink.runs[0]
    assert row["extractor_name"] == EXTRACTOR_NAME == "filesystem.record"
    assert row["source_type"] == "filesystem"
    assert row["analysis_tier"] == "filesystem"
    assert row["completeness"] == "complete"
    assert row["coverage"] == {"units": "files", "processed": 1, "total": 1}


def test_this_module_recomputes_none_of_p3s_ten_fields():
    # O5: "A second derivation of any of them - including a second MIME-type
    # determination or a second hash - is a contract violation, not an optimization."
    import extractors.filesystem as module
    source = Path(module.__file__).read_text()
    for forbidden in ("hashlib", "mimetypes", "os.stat", "unicodedata", "casefold",
                      "read_bytes", "open("):
        assert forbidden not in source, forbidden


def test_an_unsupported_format_carries_zero_observations(sink):
    # §2.4: "an empty extraction result is different from an extractor that does not
    # yet exist." P4 conformance rule 9.
    decision = route(file_id="f1", content_hash="sha256:abc",
                     path=Path("/corpus/thing.qqq"), extension=".qqq",
                     detect_format=lambda path: None)
    sink.write(unrouted_result(file_row={**FILE_ROW, "filename": "thing.qqq"},
                               decision=decision, now=FIXED_CLOCK))
    assert sink.runs[0]["completeness"] == "unsupported"
    assert sink.observations == []
    sink.conforms()


def test_a_disk_image_stops_at_metadata_only_and_is_still_indexed(sink):
    # P4 fixture 19: "run: `completeness: metadata_only` ... The file is still
    # indexed through its `filesystem` observations (fixture 11)."
    decision = route(file_id="f1", content_hash="sha256:abc",
                     path=Path("/corpus/archive.dmg"), extension=".dmg",
                     detect_format=lambda path: "dmg")
    row = {**FILE_ROW, "filename": "archive.dmg", "extension": ".dmg",
           "mime_type": None}
    sink.write(extract_filesystem(file_row=row, path=Path("/corpus/archive.dmg"),
                                  policy=OPEN_POLICY, now=FIXED_CLOCK,
                                  context_window=40))
    sink.write(unrouted_result(file_row=row, decision=decision, now=FIXED_CLOCK))
    opaque = [r for r in sink.runs if r["source_type"] == "opaque_binary"][0]
    assert opaque["completeness"] == "metadata_only"
    assert sink.observations_for(opaque["run_id"]) == []
    indexed = [r for r in sink.runs if r["source_type"] == "filesystem"][0]
    assert sink.observations_for(indexed["run_id"])
    sink.conforms()


def test_a_psd_is_indexed_but_unreadable_and_never_zero_rows(sink):
    # SPEC fixture: "`design.psd` | §2.9 | `unreadable` carrying metadata-level
    # observations (M3) - indexed-but-unreadable, never zero rows."
    decision = route(file_id="f1", content_hash="sha256:abc",
                     path=Path("/corpus/design.psd"), extension=".psd",
                     detect_format=lambda path: "psd")
    row = {**FILE_ROW, "filename": "design.psd", "extension": ".psd",
           "mime_type": "image/vnd.adobe.photoshop"}
    sink.write(unrouted_result(file_row=row, decision=decision, now=FIXED_CLOCK))
    assert sink.runs[0]["completeness"] == "unreadable"
    assert sink.runs[0]["source_type"] == "design_creative"
    assert sink.runs[0]["failure_reason"]
    emitted = {locator_for(o["location"]): o["raw_value"] for o in sink.observations}
    assert emitted["filename"] == "design.psd"
    assert emitted["metadata:field=format"] == "psd"
    sink.conforms()


def test_the_extractor_refuses_a_protected_path_before_reading_the_row():
    from extractors.safety import ProtectedContainerRefused
    policy = SafetyPolicy(is_protected_container=lambda path: True,
                          is_dataless=lambda path: False)
    with pytest.raises(ProtectedContainerRefused):
        extract_filesystem(file_row=FILE_ROW,
                           path=Path("/Applications/Thing.app/Wash U.docx"),
                           policy=policy, now=FIXED_CLOCK, context_window=40)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_filesystem.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'extractors.filesystem'`

- [ ] **Step 3: Write the implementation**

```python
# src/extractors/filesystem.py
"""O5 - P3's section 1.2 record, re-emitted as `source_type: filesystem` observations.

"P3 computes the section 1.2 basic filesystem record; P5 emits `source_type:
filesystem` observations referencing it, NEVER recomputing it." This module reads
values out of a `files` row. It stats nothing, opens nothing, hashes nothing,
normalizes no filename and determines no MIME type - O5's stated reason is drift:
"the two would drift and section 3.4's cache key is built on the hash."

Also here, because they are made of the same material: the run a file gets when the
router found no extractor for it. Section 2.4 forbids the three cases being one:

    unsupported     no extractor exists           zero observations
    metadata_only   section 2.9's safe stop       zero observations; the FILESYSTEM
                                                  run above is how the file is still
                                                  indexed (P4 fixture 19)
    unreadable      indexed-but-unreadable        carries metadata-level rows (M3)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from extractors.runs import coverage
from extractors.safety import SafetyPolicy, admit
from extractors.shape import context_for, location, observation, run, segment, text_unit
from extractors.sink import ExtractionResult

VERSION = "0.1.0"
EXTRACTOR_NAME = "filesystem.record"
SOURCE_TYPE = "filesystem"
ANALYSIS_TIER = "filesystem"

#: Named slots on P3's row that become `direct` observations at zone `metadata`.
#: Section 2.9's remaining basic-extraction fields are deliberately absent: G5 gives
#: duplicate and version-family signals to P6 "from P1's content hashes", and G6
#: gives the bounded download session to P6 "computed from P3 timestamps". P6 reads
#: those from `files`; a second copy here would be two homes for one value.
METADATA_SLOTS: tuple[str, ...] = ("normalized_filename", "extension", "mime_type")


def extract_filesystem(*, file_row: Mapping[str, Any], path: Path,
                       policy: SafetyPolicy, now: str,
                       context_window: int) -> ExtractionResult:
    """One run whose observations are P3's record, made citable.

    The filename gets the run's single `container_path: ()` text unit, so P4's
    fixture 11 (`filename#0-6`, a SPAN into the filename) has a unit to index into.
    `text_units` is keyed by (run_id, container_path), so a run holds exactly one
    unit at `()`; the parent-folder observation therefore carries no span and
    degrades to the coarser address, which is P4's segment-kind rule 4.
    """
    admit(path, policy=policy)

    filename = file_row["filename"]
    observations = []
    before, after, truncated = context_for(filename, 0, len(filename),
                                           window=context_window)
    observations.append(observation(
        file_id=file_row["file_id"], content_hash=file_row["content_hash"],
        extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
        source_type=SOURCE_TYPE, raw_value=filename,
        location=location(zone="filename", text_span={"start": 0,
                                                      "end": len(filename)}),
        context_before=before, context_after=after, context_truncated=truncated,
        observed_at=now, reliability="possible",
    ))

    parent = file_row.get("directory_position")
    if parent:
        # MINOR 11: section 2.9's name for this value is "parent-folder context";
        # `directory_position` is only the column P1 stores it in.
        observations.append(observation(
            file_id=file_row["file_id"], content_hash=file_row["content_hash"],
            extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
            source_type=SOURCE_TYPE, raw_value=parent,
            location=location(zone="path"),
            observed_at=now, reliability="possible",
        ))

    for slot in METADATA_SLOTS:
        value = file_row.get(slot)
        if not value:
            continue        # an observation records presence, never absence
        observations.append(observation(
            file_id=file_row["file_id"], content_hash=file_row["content_hash"],
            extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
            source_type=SOURCE_TYPE, raw_value=str(value),
            location=location(zone="metadata",
                              container_path=(segment("field", label=slot),)),
            observed_at=now, reliability="direct",
        ))

    return ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
                source_type=SOURCE_TYPE, analysis_tier=ANALYSIS_TIER, config={},
                completeness="complete", coverage=coverage("files", 1, 1),
                observation_count=len(observations), started_at=now, finished_at=now),
        observations=tuple(observations),
        text_units=(text_unit(text=filename),),
    )


def unrouted_result(*, file_row: Mapping[str, Any], decision,
                    now: str) -> ExtractionResult:
    """The run a file gets when the router found no extractor for it.

    Section 2.4: "The system should never silently treat an unsupported format as an
    empty document, because an empty extraction result is different from an extractor
    that does not yet exist." Which of P4's three values applies is the router's
    decision; what it means in rows is here.
    """
    completeness = decision.unrouted_completeness
    source_type = decision.source_type or "opaque_binary"
    observations: list[Mapping[str, Any]] = []
    failure_reason = None

    if completeness == "unreadable":
        # M3 and section 2.9: "unsupported proprietary formats should be recorded as
        # indexed-but-unreadable rather than silently treated as empty", and its
        # metadata-level rows - "at minimum filename, format" - are what "indexed"
        # means. Both come from P3's row: reading the format is exactly what there is
        # no library for.
        failure_reason = (
            f"no extractor exists for {decision.detected_format or 'this format'}; "
            "recorded as indexed-but-unreadable (section 2.9, M3)"
        )
        observations.append(observation(
            file_id=file_row["file_id"], content_hash=file_row["content_hash"],
            extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
            source_type=source_type, raw_value=file_row["filename"],
            location=location(zone="filename"),
            observed_at=now, reliability="possible",
        ))
        detected = decision.detected_format
        if detected:
            observations.append(observation(
                file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
                source_type=source_type, raw_value=detected,
                location=location(zone="metadata",
                                  container_path=(segment("field", label="format"),)),
                observed_at=now, reliability="direct",
            ))

    return ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
                source_type=source_type, analysis_tier=ANALYSIS_TIER, config={},
                completeness=completeness,
                coverage=coverage("files", 0, 1),
                observation_count=len(observations), started_at=now, finished_at=now,
                failure_reason=failure_reason),
        observations=tuple(observations),
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p5/test_p5_filesystem.py -v`
Expected: PASS — 11 passed

- [ ] **Step 5: Commit**

```bash
git add src/extractors/filesystem.py tests/p5/test_p5_filesystem.py
git commit -m "feat(P5): O5 - P3's record as source_type filesystem, and the three unrouted outcomes"
```

---

### Task 7: E1 — PDF (§2.2), the complete document with its locations

**Files:**
- Create: `src/extractors/reading.py`
- Create: `src/extractors/pdf.py`
- Test: `tests/p5/test_p5_pdf.py`

**Interfaces:**
- Consumes: `extractors.shape`, `extractors.safety.admit`, `extractors.runs.coverage`; caller-supplied `read_pdf(path) -> PdfDocument` and `find_structured_strings(text) -> tuple[StructuredString, ...]`.
- Produces: `reading.StructuredString`, `reading.Region`, `reading.ZONE_BY_STRUCTURED_KIND`, `pdf.VERSION`, `pdf.EXTRACTOR_NAME`, `pdf.TITLE_SLOTS`, `pdf.PdfPage`, `pdf.PdfDocument`, `pdf.extract_pdf()`.

**§2.2, in full, is this task.** *"For PDFs with usable text layers, the engine should extract the
complete document rather than only a first-page preview. It should preserve the title, author,
subject, creator and producer metadata, creation and modification dates, page count, complete text by
page, headings, URLs, email addresses, DOI values, citations, identifiers, and other structured
strings… Crucially, it must preserve **where** each important piece of evidence appears."*

**The three homes, and why each field is where it is.**

| §2.2 requires | where it lands | why |
|---|---|---|
| title | observation, zone `title`, `direct` | P4's zone table: `title` is *"the document title"*, named at §2.2 and §3.2 ("the PDF title") |
| author, subject, creator, producer, dates | observations, zone `metadata`, `field=<slot verbatim>`, `direct` | P4 D7: the `field` segment carries *"the source format's own slot name, verbatim"* |
| page count | `run.coverage {units: "pages", processed, total}` | P4 already requires coverage for a capped run; a second home for the same number is the drift this project keeps paying for. See the report. |
| complete text, by page | `text_units`, one row per page, `[{page, N}]` | G1: *"a page of text is not a located value"* |
| headings | observation zone `heading` **and** a `text_units` row at `[{page,N},{heading,K}]` | P4's fixture 1 is `heading:page=1/heading=2#0-10` — a span — and conformance rule 10 requires a unit at exactly that path |
| URLs, emails, DOIs | observation zone `link` | P4's zone table: *"`link` — a URL, email address, DOI or hyperlink"* |
| citations | observation zone `reference_list` | P4's zone table cites §2.2's *"a reference list on page eighteen"* |
| identifiers, other structured strings | observation at the zone of the region they were found in | §2.2 names the class; the zone is where it sits |

**Two units per heading is deliberate, not an oversight.** §2.2 requires the complete text *by page*,
and P4's own fixture 1 addresses a value at `heading:page=1/heading=2#0-10`, which conformance rule 10
says must have a `text_units` row whose `container_path` is exactly `[page=1, heading=2]`. Those are
two different requirements about the same characters, and P4 D12 rule 2 forbids the cheaper way out
(*"An extractor that cannot address text finely emits a coarser unit… It never invents a finer unit to
justify a span"* — here the fine unit is real, not invented). Heading strings are short; the page text
is the bulk, and it is stored once.

**Only `heading` regions get a container segment.** P4's segment kinds include `heading` but include no
`body` and no `reference_list` — those are **zones**, not addresses. So a body or reference-list region
contributes the `zone` and the observation stays at `[{page, N}]` with a span into the page unit. That
is the division P4 D2 states: *"The zone answers what kind of place; the container path answers which
one."*

**Metadata is supporting evidence, and there is no marker on the record (M4).** §2.2: *"Author and
creator fields may be stale, generic, or generated by a tool rather than a person, so a value such as
`python-docx`, `Mozilla/5.0`, or a browser-generated producer string should not be mistaken for
meaningful content."* P5 emits the value **verbatim** at `zone = metadata` with `reliability: direct`
— *"`direct` describes the **slot**, not the value's usefulness"* — and sets **no flag of any kind**.
M4: *"P6 gains an explicit producer/creator discount rule keyed on P4's `zone = metadata` plus the
deferred tool-string list."* The list is **Deferred** and is not in `src/extractors/`; Task 20 asserts
that by introspection rather than by searching source text, because this very paragraph quotes the
strings.

**`normalized_value` is mechanical or null.** Date slots use the ISO-8601 rendering the reader supplies
— a PDF date string like `D:20260717140322Z` is a format detail and parsing it belongs with the library
— and every other value gets `normalize_mechanical` (P4 D8). Nothing here resolves an entity or parses a
date out of free text (§3.10).

**Occurrence collapsing is P4 D10, applied exactly.** *"One observation per (run, exact raw value,
zone); `occurrence_count` counts within that zone; `location` addresses the first occurrence in
document order."* Document order here is: metadata slots (sorted by slot name, because metadata has no
document order and a stable order is what §3.4's caching and §8.5's replay require), then pages in page
order, then within a page the regions in the reader's order and the found strings by offset.

**The SPEC's own fixture is the headline test.** *"`syllabus-busib4300.pdf` — course code in title and
in a page-18 reference list | §2.2, §3.2 | two observations, distinct locations, distinct occurrence
counts."* Distinct **zones** are what make them two rows under D10, and that is precisely §2.2's point:
*"A course code or university name found in a filename, title, or page-one heading is more meaningful
than the same text appearing once in a reference list on page eighteen."*

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_pdf.py
"""E1 - §2.2. Done-means 4: "PDF is complete, not previewed, and location survives:
the page-1 and page-18 occurrences of one string are two distinguishable
observations.\""""
from pathlib import Path

import pytest

from extractors.pdf import EXTRACTOR_NAME, PdfDocument, PdfPage, extract_pdf
from extractors.reading import Region, StructuredString
from extractors.safety import ProtectedContainerRefused, SafetyPolicy

from conftest import FIXED_CLOCK
from p4_stub import locator_for

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)

FILE_ROW = {"file_id": "f1", "content_hash": "sha256:abc",
            "filename": "syllabus-busib4300.pdf"}

PAGE_1 = ("BUSIB 4300 Course Information\n"
          "Syllabus — Spring 2026. Contact prof@wustl.edu.")
PAGE_18 = ("References\n"
           "Ng, A. (2024). BUSIB 4300 readings. doi:10.1000/xyz. "
           "See also BUSIB 4300 supplement.")


def a_syllabus() -> PdfDocument:
    """The SPEC's `syllabus-busib4300.pdf`: the course code in the title and in a
    page-18 reference list."""
    return PdfDocument(
        metadata={"Title": "BUSIB 4300 Syllabus", "Author": "J. Yung",
                  "Producer": "python-docx", "CreationDate": "D:20260717140322Z"},
        iso_dates={"CreationDate": "2026-07-17T14:03:22+00:00"},
        pages=(
            PdfPage(number=1, text=PAGE_1,
                    regions=(Region(zone="heading", start=0, end=29, ordinal=1,
                                    label="Course Information"),
                             Region(zone="body", start=30, end=len(PAGE_1)))),
            PdfPage(number=18, text=PAGE_18,
                    regions=(Region(zone="heading", start=0, end=10, ordinal=1,
                                    label="References"),
                             Region(zone="reference_list", start=11,
                                    end=len(PAGE_18)))),
        ),
    )


def find_the_course_code(text: str):
    """The fixture finder. §2.2's pattern sets are DEFERRED (SPEC Deferred: "Citation
    and identifier pattern sets ... The patterns"), so no pattern lives in
    src/extractors/ and the test supplies this one."""
    found = []
    start = text.find("BUSIB 4300")
    while start != -1:
        found.append(StructuredString(kind="identifier", start=start,
                                      end=start + len("BUSIB 4300")))
        start = text.find("BUSIB 4300", start + 1)
    for token, kind in (("prof@wustl.edu", "email"), ("doi:10.1000/xyz", "doi")):
        at = text.find(token)
        if at != -1:
            found.append(StructuredString(kind=kind, start=at, end=at + len(token)))
    return tuple(sorted(found, key=lambda s: s.start))


def run_it(document=None, finder=find_the_course_code, **kwargs):
    return extract_pdf(file_row=FILE_ROW, path=Path("/corpus/syllabus.pdf"),
                       policy=OPEN_POLICY, read_pdf=lambda path: document or a_syllabus(),
                       find_structured_strings=finder, now=FIXED_CLOCK,
                       context_window=40, **kwargs)


def test_every_observation_conforms_to_p4s_shape(sink):
    sink.write(run_it())
    sink.conforms()


def test_the_complete_text_is_stored_by_page(sink):
    # §2.2: "extract the complete document rather than only a first-page preview";
    # G1: page text is a text_units row, not an observation.
    run_id = sink.write(run_it())
    pages = {u["container_path"][0]["index"]: u["text"]
             for u in sink.units_for(run_id) if len(u["container_path"]) == 1}
    assert pages == {1: PAGE_1, 18: PAGE_18}
    assert not [o for o in sink.observations if o["raw_value"] == PAGE_1]


def test_the_page_count_is_the_runs_coverage(sink):
    run_id = sink.write(run_it())
    assert sink.run_for(run_id)["coverage"] == {"units": "pages", "processed": 2,
                                                "total": 2}


def test_the_course_code_in_the_title_and_in_the_reference_list_are_two_rows(sink):
    # SPEC fixture: "two observations, distinct locations, distinct occurrence counts."
    # §2.2: a code in a title "is more meaningful than the same text appearing once in
    # a reference list on page eighteen."
    sink.write(run_it())
    rows = {o["location"]["zone"]: o for o in sink.observations
            if o["raw_value"] == "BUSIB 4300"}
    assert set(rows) == {"heading", "reference_list"}
    assert locator_for(rows["heading"]["location"]) == "heading:page=1/heading=1#0-10"
    assert rows["heading"]["occurrence_count"] == 1
    assert rows["reference_list"]["location"]["container_path"][0]["index"] == 18
    assert rows["reference_list"]["occurrence_count"] == 2


def test_the_title_slot_is_its_own_zone_and_is_direct(sink):
    # P4's zone table: `title` is "the document title", named at §2.2 and §3.2.
    sink.write(run_it())
    titles = [o for o in sink.observations if o["location"]["zone"] == "title"]
    assert len(titles) == 1
    assert titles[0]["raw_value"] == "BUSIB 4300 Syllabus"
    assert titles[0]["reliability"] == "direct"
    assert locator_for(titles[0]["location"]) == "title:field=Title"


def test_the_producer_is_emitted_verbatim_with_no_marker_of_any_kind(sink):
    # SPEC fixture: "`python-docx-producer.pdf` | §2.2, §8.5 | producer emitted
    # verbatim at `zone = metadata`, `reliability: direct`, NO MARKER OF ANY KIND on
    # the observation; P6 discounts it (M4)."
    from extractors.shape import OBSERVATION_FIELDS
    sink.write(run_it())
    producer = [o for o in sink.observations
                if locator_for(o["location"]) == "metadata:field=Producer"][0]
    assert producer["raw_value"] == "python-docx"
    assert producer["reliability"] == "direct"
    assert tuple(k for k in producer if k != "run_id") == OBSERVATION_FIELDS
    for marker in ("tool_generated", "suppressed", "discount", "trustworthy",
                   "generic", "stale"):
        assert marker not in producer


def test_a_structured_date_slot_is_normalized_to_iso_8601_by_the_reader(sink):
    # P4 D8's fourth transform. The PDF date syntax is a format detail, so the reader
    # renders it and P5 carries it; §3.10 forbids parsing a date out of free text.
    sink.write(run_it())
    created = [o for o in sink.observations
               if locator_for(o["location"]) == "metadata:field=CreationDate"][0]
    assert created["raw_value"] == "D:20260717140322Z"
    assert created["normalized_value"] == "2026-07-17T14:03:22+00:00"


def test_headings_are_observations_and_have_their_own_addressable_unit(sink):
    # §2.2 requires headings; P4's fixture 1 addresses a value INSIDE one, which
    # conformance rule 10 says needs a unit at exactly that container path.
    run_id = sink.write(run_it())
    heading = [o for o in sink.observations
               if o["location"]["zone"] == "heading"
               and o["raw_value"].startswith("BUSIB 4300 Course")][0]
    path = heading["location"]["container_path"]
    assert [s["kind"] for s in path] == ["page", "heading"]
    assert path[1]["label"] == "Course Information"
    unit = [u for u in sink.units_for(run_id) if u["container_path"] == path][0]
    assert unit["text"] == "BUSIB 4300 Course Information"


def test_a_url_email_or_doi_lands_in_the_link_zone(sink):
    # P4's zone table: "`link` - a URL, email address, DOI or hyperlink".
    sink.write(run_it())
    links = {o["raw_value"] for o in sink.observations
             if o["location"]["zone"] == "link"}
    assert links == {"prof@wustl.edu", "doi:10.1000/xyz"}


def test_surrounding_context_is_carried_as_p4s_three_fields(sink):
    # §2.2 requires surrounding context; M5 makes it three fields.
    sink.write(run_it())
    code = [o for o in sink.observations
            if o["raw_value"] == "BUSIB 4300"
            and o["location"]["zone"] == "reference_list"][0]
    assert "BUSIB 4300 readings" not in code["context_before"]
    assert code["context_after"].startswith(" readings")
    assert code["context_truncated"] in (True, False)


def test_raw_survives_exactly_and_normalization_is_mechanical(sink):
    # Done-means 3: "A document saying `U Chicago` keeps that exact wording as the raw
    # value regardless of what any resolver later does with it."
    document = PdfDocument(
        metadata={}, pages=(PdfPage(number=1, text="Applying to U  Chicago this fall.",
                                    regions=(Region(zone="body", start=0, end=33),)),))

    def finder(text):
        at = text.find("U  Chicago")
        return (StructuredString(kind="identifier", start=at, end=at + 10),)

    sink.write(run_it(document, finder))
    row = [o for o in sink.observations if o["raw_value"] == "U  Chicago"][0]
    assert row["raw_value"] == "U  Chicago"
    assert row["normalized_value"] == "U Chicago"     # whitespace collapse only


def test_a_pdf_with_no_structured_strings_is_complete_with_zero_of_them(sink):
    # §2.4's rule, applied here: an empty result is `complete`, never `unsupported`.
    document = PdfDocument(metadata={},
                           pages=(PdfPage(number=1, text="   ",
                                          regions=()),))
    run_id = sink.write(run_it(document, lambda text: ()))
    assert sink.run_for(run_id)["completeness"] == "complete"
    assert sink.observations_for(run_id) == []
    sink.conforms()


def test_the_run_is_native_and_names_the_pdf_extractor(sink):
    run_id = sink.write(run_it())
    row = sink.run_for(run_id)
    assert row["extractor_name"] == EXTRACTOR_NAME == "pdf.text"
    assert row["source_type"] == "text_document"
    assert row["analysis_tier"] == "native"


def test_e1_refuses_a_protected_path_before_it_calls_its_reader():
    calls = []
    policy = SafetyPolicy(is_protected_container=lambda path: True,
                          is_dataless=lambda path: False)
    with pytest.raises(ProtectedContainerRefused):
        extract_pdf(file_row=FILE_ROW,
                    path=Path("/Applications/Thing.app/Resources/help.pdf"),
                    policy=policy,
                    read_pdf=lambda path: calls.append(path) or a_syllabus(),
                    find_structured_strings=find_the_course_code, now=FIXED_CLOCK,
                    context_window=40)
    assert calls == []


def test_there_is_no_language_quality_check_anywhere_in_e1():
    # §2.2: "The system should not use unreliable global language-quality checks that
    # incorrectly punish multilingual or mathematics-heavy documents." Done-means 5.
    import inspect

    import extractors.pdf as module
    names = {name.lower() for name in vars(module)}
    for forbidden in ("language_quality", "gibberish", "readability", "is_garbled",
                      "text_quality", "looks_like_text", "detect_language"):
        assert forbidden not in names
    assert "language" not in inspect.signature(extract_pdf).parameters
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_pdf.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'extractors.pdf'`

- [ ] **Step 3: Write the implementation**

```python
# src/extractors/reading.py
"""The shapes P5's injected format readers return.

P5 adds no third-party runtime dependency: real PDF, DOCX, HEIC, archive and OCR
reading cannot be done in the standard library, so every format-specific reader is a
caller-supplied callable and these are the shapes it hands back. A deterministic
fixture reader in tests/p5/ implements each one; a real library implements the same
shape without changing an observation, a run or a text unit.

These are P5's own input types. They are NOT P4 records and never reach the sink.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Region:
    """A labelled stretch of a unit's text.

    `zone` is one of P4's fifteen: the reader says WHAT KIND OF PLACE this is,
    because that is library knowledge (a heading style, a table cell, a footer). Only
    `heading` also carries an address - P4's segment kinds include `heading` and
    include no `body` and no `reference_list`, because those are zones, not addresses
    (P4 D2: "The zone answers what kind of place; the container path answers which
    one").
    """
    zone: str
    start: int
    end: int
    ordinal: int | None = None
    label: str | None = None


@dataclass(frozen=True)
class StructuredString:
    """One of section 2.2's "URLs, email addresses, DOI values, citations,
    identifiers, and other structured strings".

    `kind` uses section 2.2's own words. The PATTERNS are Deferred - the SPEC's
    Deferred table says DOI is named and citations and identifiers are named as
    classes, but "The patterns" are not settled - so no pattern lives in
    src/extractors/ and the finder is supplied by the caller.
    """
    kind: str
    start: int
    end: int


#: Which of P4's zones a found string belongs to when its kind implies one.
#: P4's zone table: "`link` - a URL, email address, DOI or hyperlink";
#: "`reference_list` - a citation / reference list", citing section 2.2's "a
#: reference list on page eighteen". A kind not listed here takes the zone of the
#: region it was found in, because section 2.2 names the class and the region says
#: where it sits.
ZONE_BY_STRUCTURED_KIND: dict[str, str] = {
    "url": "link",
    "email": "link",
    "doi": "link",
    "citation": "reference_list",
}
```

```python
# src/extractors/pdf.py
"""E1 - PDF extraction (section 2.2).

"For PDFs with usable text layers, the engine should extract the complete document
rather than only a first-page preview... Crucially, it must preserve WHERE each
important piece of evidence appears."

Three homes, one per kind of thing:
    metadata slots      -> observations, zone `title` for the title and `metadata`
                           for the rest, `field=<the format's own slot name>` (D7)
    complete text       -> text_units, one row per page (G1)
    structured strings  -> observations, spans into the unit their container names

Section 2.2's metadata rule is carried by emitting the value VERBATIM and marking
nothing: "a value such as python-docx, Mozilla/5.0, or a browser-generated producer
string should not be mistaken for meaningful content" is a DISCOUNT RULE, and M4 puts
it in P6, keyed on `zone = metadata` plus a list that is Deferred and is not here.

There is no global language-quality check in this module or anywhere else in P5:
section 2.2 forbids one because it "incorrectly punishes multilingual or
mathematics-heavy documents".
"""
from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from typing import Any, Callable, Mapping

from extractors.reading import ZONE_BY_STRUCTURED_KIND, Region, StructuredString
from extractors.runs import coverage
from extractors.safety import SafetyPolicy, admit
from extractors.shape import (
    context_for, location, normalize_mechanical, observation, run, segment, text_unit,
)
from extractors.sink import ExtractionResult

VERSION = "0.1.0"
EXTRACTOR_NAME = "pdf.text"
SOURCE_TYPE = "text_document"
ANALYSIS_TIER = "native"

#: The one metadata slot that is its own zone. P4's zone table gives `title` as "the
#: document title", named at section 2.2 and section 3.2 ("the PDF title"). Every
#: other slot is `metadata`.
TITLE_SLOTS: tuple[str, ...] = ("Title",)


@dataclass(frozen=True)
class PdfPage:
    number: int                                  # 1-based (P4 D3)
    text: str
    regions: tuple[Region, ...] = ()


@dataclass(frozen=True)
class PdfDocument:
    """What an injected `read_pdf` returns.

    `metadata` maps the format's own slot names to their values, verbatim (P4 D7).
    `iso_dates` carries the ISO-8601 rendering of any slot the reader recognised as a
    structured date - P4 D8's fourth mechanical transform. The PDF date syntax is a
    format detail, so the library that knows it does the rendering, and P5 never
    parses a date out of free text (section 3.10).
    """
    metadata: Mapping[str, str]
    pages: tuple[PdfPage, ...]
    iso_dates: Mapping[str, str] = dataclass_field(default_factory=dict)


@dataclass(frozen=True)
class _Candidate:
    zone: str
    raw: str
    container_path: tuple
    span: dict | None
    unit_text: str | None
    reliability: str
    normalized: str | None


def _region_at(page: PdfPage, offset: int) -> Region | None:
    """The innermost region containing this offset, preferring an addressable one."""
    containing = [r for r in page.regions if r.start <= offset < r.end]
    if not containing:
        return None
    headings = [r for r in containing if r.zone == "heading"]
    return headings[0] if headings else containing[0]


def extract_pdf(*, file_row: Mapping[str, Any], path: Path, policy: SafetyPolicy,
                read_pdf: Callable[[Path], PdfDocument],
                find_structured_strings: Callable[[str], tuple[StructuredString, ...]],
                now: str, context_window: int) -> ExtractionResult:
    """Section 2.2's complete document, as P4 records.

    Document order, which P4 D10 says `location` addresses the first occurrence in:
    metadata slots sorted by slot name (metadata has no document order, and section
    3.4's caching and section 8.5's replay both require a STABLE one), then pages in
    page order, then within a page the reader's regions and the found strings by
    offset.
    """
    admit(path, policy=policy)
    document = read_pdf(path)

    candidates: list[_Candidate] = []
    units: list[Mapping[str, Any]] = []

    for slot in sorted(document.metadata):
        value = document.metadata[slot]
        if not value:
            continue                      # presence only; an absence is never a row
        candidates.append(_Candidate(
            zone="title" if slot in TITLE_SLOTS else "metadata",
            raw=value,
            container_path=(segment("field", label=slot),),
            span=None, unit_text=None, reliability="direct",
            normalized=document.iso_dates.get(slot) or normalize_mechanical(value),
        ))

    for page in document.pages:
        page_path = (segment("page", index=page.number),)
        units.append(text_unit(text=page.text, container_path=page_path))

        heading_paths: dict[int, tuple] = {}
        for region in page.regions:
            if region.zone != "heading":
                continue                  # `body` and `reference_list` are zones, not
                                          # addresses: P4 publishes no such segment kind
            heading_path = page_path + (segment("heading", index=region.ordinal,
                                                label=region.label),)
            heading_paths[region.start] = heading_path
            heading_text = page.text[region.start:region.end]
            units.append(text_unit(text=heading_text, container_path=heading_path))
            candidates.append(_Candidate(
                zone="heading", raw=heading_text, container_path=heading_path,
                span={"start": 0, "end": len(heading_text)}, unit_text=heading_text,
                reliability="possible", normalized=normalize_mechanical(heading_text),
            ))

        for found in find_structured_strings(page.text):
            region = _region_at(page, found.start)
            zone = ZONE_BY_STRUCTURED_KIND.get(
                found.kind, region.zone if region is not None else "body")
            if region is not None and region.zone == "heading":
                container = heading_paths[region.start]
                unit_text = page.text[region.start:region.end]
                start, end = found.start - region.start, found.end - region.start
            else:
                container = page_path
                unit_text = page.text
                start, end = found.start, found.end
            raw = unit_text[start:end]
            candidates.append(_Candidate(
                zone=zone, raw=raw, container_path=container,
                span={"start": start, "end": end}, unit_text=unit_text,
                reliability="possible", normalized=normalize_mechanical(raw),
            ))

    observations = _collapse(candidates, file_row=file_row, now=now,
                             context_window=context_window)
    pages = len(document.pages)
    return ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
                source_type=SOURCE_TYPE, analysis_tier=ANALYSIS_TIER,
                config={"reader": "injected"},
                completeness="complete", coverage=coverage("pages", pages, pages),
                observation_count=len(observations), started_at=now, finished_at=now),
        observations=observations,
        text_units=tuple(units),
    )


def _collapse(candidates, *, file_row: Mapping[str, Any], now: str,
              context_window: int) -> tuple[Mapping[str, Any], ...]:
    """P4 D10: one observation per (run, exact raw value, zone).

    "`occurrence_count` counts within that zone; `location` addresses the FIRST
    occurrence in document order." Collapsing is on EXACT raw match, because P4 makes
    no normalization judgement: `Columbia` and `columbia` are two observations, and
    cross-form aggregation is P6's (section 3.7).
    """
    first: dict[tuple[str, str], _Candidate] = {}
    counts: dict[tuple[str, str], int] = {}
    order: list[tuple[str, str]] = []
    for candidate in candidates:
        key = (candidate.zone, candidate.raw)
        if key not in first:
            first[key] = candidate
            counts[key] = 0
            order.append(key)
        counts[key] += 1

    observations = []
    for key in order:
        candidate = first[key]
        before = after = ""
        truncated = False
        if candidate.span is not None and candidate.unit_text is not None:
            before, after, truncated = context_for(
                candidate.unit_text, candidate.span["start"], candidate.span["end"],
                window=context_window)
        observations.append(observation(
            file_id=file_row["file_id"], content_hash=file_row["content_hash"],
            extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
            source_type=SOURCE_TYPE, raw_value=candidate.raw,
            normalized_value=candidate.normalized,
            location=location(zone=candidate.zone,
                              container_path=candidate.container_path,
                              text_span=candidate.span),
            context_before=before, context_after=after, context_truncated=truncated,
            occurrence_count=counts[key], observed_at=now,
            reliability=candidate.reliability,
        ))
    return tuple(observations)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p5/test_p5_pdf.py -v`
Expected: PASS — 15 passed

- [ ] **Step 5: Commit**

```bash
git add src/extractors/reading.py src/extractors/pdf.py tests/p5/test_p5_pdf.py
git commit -m "feat(P5): E1 PDF - complete text by page, located structured strings, no marker on metadata"
```

---

### Task 8: §2.2's three text-layer states and §2.7's OCR trigger

**Files:**
- Create: `src/extractors/ocr_policy.py`
- Test: `tests/p5/test_p5_ocr_policy.py`

**Interfaces:**
- Consumes: an `ExtractionResult` from E1 or E5; a caller-supplied `no_usable_facts(file_id, content_hash) -> bool` (P6's read surface, M11).
- Produces: `TEXT_LAYER_STATES`, `OcrDecision`, `text_layer_state()`, `document_ocr_decision()`, `image_ocr_decision()`.

**Done-means 5:** *"The two text-layer states behave differently, and no global language-quality check
exists anywhere in the codebase (§2.2, §2.7)."*

**§2.2's distinction, and why it is a behaviour rather than a stored value.**

| state | definition | action |
|---|---|---|
| `text_layer_usable` | text extracted and usable | no OCR |
| `text_layer_absent` | **no** text layer | route **directly** to E6 |
| `text_layer_broken` | technically produces text, but the stored evidence yields no usable facts | **targeted** OCR only, and only after P6 reports no usable facts |

The state is **not** an observation and **not** a column. "No text layer" is an *absence*, and P4 is
explicit: *"An extractor may not write an 'EXIF absent', 'no text layer' or 'metadata stripped'
observation; the run record already says it, and an absence written as evidence is a value P6 can
rank."* It is not on the run either, because `completeness` is P4's vocabulary and B1 forbids a
parallel one. §2.2's requirement that the system *distinguish* the two is met by the two paths
behaving differently, which is what the tests assert.

**`no_usable_facts` is P6's, injected, and has no default.** M11: *"P6 publishes
`no_usable_facts(file_id, content_hash) -> bool` on its read surface. §2.2 requires targeted OCR only
when stored evidence yields no usable facts; P5 depends on it… The threshold is a deferred
configuration value (P5 OQ1)."* P6 does not exist yet and a default would be P5 answering P6's
question, so the parameter is required. **SPEC Open question 1 — the threshold — is not answered
here:** this module holds no number, no `min_facts`, no ratio, and Task 20 asserts that by
introspection.

**The direct route never asks P6.** §2.2: *"A file with no text should route directly to OCR."* A
document with no text layer has no evidence for P6 to have failed to make facts from, so calling
`no_usable_facts` would be asking a question whose answer cannot mean what the broken case means. The
test asserts the predicate is never called on that path.

**The prohibited trigger.** §2.2: *"The system should not use unreliable global language-quality checks
that incorrectly punish multilingual or mathematics-heavy documents."* §2.7: a broken-text-layer PDF
must not reach OCR *"because a broad quality heuristic says the text looks unusual"*. So this module
takes exactly one signal about a non-empty text layer — P6's verdict — and there is no parameter,
constant or helper here that looks at the text at all.

**§2.7's image trigger is the same rule with different inputs.** *"OCR should therefore run when a file
yields no usable text **and** no usable metadata, including scanned PDFs, confirmed screenshots, and
opaque images without EXIF."* For an image run that means: the run produced no text unit with text in
it, and it produced no `metadata`-zone observation. Reading the absence to make a routing decision is
allowed; **writing** it as an observation is not (M2), and Task 13 asserts the second half.

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_ocr_policy.py
"""Done-means 5 - §2.2's two states behave differently, and no global
language-quality check exists anywhere."""
from pathlib import Path

import pytest

from extractors.ocr_policy import (
    TEXT_LAYER_STATES, document_ocr_decision, image_ocr_decision, text_layer_state,
)
from extractors.pdf import PdfDocument, PdfPage, extract_pdf
from extractors.reading import Region
from extractors.safety import SafetyPolicy

from conftest import FIXED_CLOCK

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
FILE_ROW = {"file_id": "f1", "content_hash": "sha256:abc", "filename": "Hw 5.pdf"}


def a_pdf(text: str) -> PdfDocument:
    regions = (Region(zone="body", start=0, end=len(text)),) if text else ()
    return PdfDocument(metadata={}, pages=(PdfPage(number=1, text=text,
                                                   regions=regions),))


def extracted(text: str):
    return extract_pdf(file_row=FILE_ROW, path=Path("/corpus/Hw 5.pdf"),
                       policy=OPEN_POLICY, read_pdf=lambda path: a_pdf(text),
                       find_structured_strings=lambda t: (), now=FIXED_CLOCK,
                       context_window=40)


def test_the_three_states_are_2_2s_own_three():
    assert TEXT_LAYER_STATES == ("text_layer_usable", "text_layer_absent",
                                 "text_layer_broken")


def test_a_photographed_page_has_no_text_layer_and_routes_directly(sink):
    # SPEC fixture: "`hw5-photographed.pdf` - no text layer | §2.1, §2.2 |
    # `text_layer_absent` -> direct OCR route, no language check."
    asked = []
    decision = document_ocr_decision(
        result=extracted(""), file_id="f1", content_hash="sha256:abc",
        no_usable_facts=lambda file_id, content_hash: asked.append(file_id) or True)
    assert decision.state == "text_layer_absent"
    assert decision.run_ocr is True
    assert decision.targeted is False
    # §2.2: "A file with no text should route DIRECTLY to OCR." A document with no
    # evidence has nothing P6 could have failed to make facts from, so P6 is not asked.
    assert asked == []


def test_a_usable_text_layer_does_not_reach_ocr():
    decision = document_ocr_decision(
        result=extracted("Homework 5. Solve for x."), file_id="f1",
        content_hash="sha256:abc",
        no_usable_facts=lambda file_id, content_hash: False)
    assert decision.state == "text_layer_usable"
    assert decision.run_ocr is False


def test_a_broken_text_layer_waits_for_p6_and_is_then_targeted():
    # SPEC fixture: "`corrupt-text-layer.pdf` | §2.2, §8.5 | `text_layer_broken`; NO
    # OCR until P6 returns no-usable-facts."
    result = extracted("�� garbled � text that is not empty")
    still_useful = document_ocr_decision(
        result=result, file_id="f1", content_hash="sha256:abc",
        no_usable_facts=lambda file_id, content_hash: False)
    assert still_useful.state == "text_layer_usable"
    assert still_useful.run_ocr is False

    no_facts = document_ocr_decision(
        result=result, file_id="f1", content_hash="sha256:abc",
        no_usable_facts=lambda file_id, content_hash: True)
    assert no_facts.state == "text_layer_broken"
    assert no_facts.run_ocr is True
    assert no_facts.targeted is True


def test_the_broken_state_is_never_an_observation_and_never_a_run_field(sink):
    # P4: "An extractor may not write an 'EXIF absent', 'NO TEXT LAYER' or 'metadata
    # stripped' observation." The state is a behaviour, not a stored value.
    sink.write(extracted(""))
    sink.conforms()
    assert sink.observations == []
    for state in TEXT_LAYER_STATES:
        assert state not in str(sink.runs[0])
    assert sink.runs[0]["completeness"] == "complete"


def test_p6s_verdict_is_required_and_has_no_default():
    # M11. P6 does not exist yet, and a default here would be P5 answering P6's
    # question.
    import inspect
    parameter = inspect.signature(document_ocr_decision).parameters["no_usable_facts"]
    assert parameter.default is inspect.Parameter.empty


def test_there_is_no_language_quality_check_and_nothing_looks_at_the_text():
    # §2.2: "The system should not use unreliable global language-quality checks that
    # incorrectly punish multilingual or mathematics-heavy documents."
    # §2.7: not "because a broad quality heuristic says the text looks unusual".
    import inspect

    import extractors.ocr_policy as module
    names = {name.lower() for name in vars(module)}
    for forbidden in ("language_quality", "gibberish", "readability", "is_garbled",
                      "text_quality", "looks_like_text", "detect_language",
                      "confidence_of_text", "printable_ratio"):
        assert forbidden not in names
    parameters = set(inspect.signature(document_ocr_decision).parameters)
    assert parameters == {"result", "file_id", "content_hash", "no_usable_facts"}


def test_the_module_holds_no_threshold_because_oq1_is_open():
    # SPEC Open question 1: "What is the 'no usable facts' threshold? ... the design
    # never says how few facts is 'no usable facts'. It is a deferred configuration
    # value." Nothing numeric is bound to a name in this module.
    import extractors.ocr_policy as module
    numeric = {name: value for name, value in vars(module).items()
               if isinstance(value, (int, float)) and not isinstance(value, bool)
               and not name.startswith("__")}
    assert numeric == {}


def test_an_image_with_no_text_and_no_metadata_reaches_ocr(sink):
    # §2.7: "OCR should therefore run when a file yields no usable text AND no usable
    # metadata, including scanned PDFs, confirmed screenshots, and opaque images
    # without EXIF."
    from extractors.shape import run
    from extractors.sink import ExtractionResult
    opaque = ExtractionResult(
        run=run(file_id="f1", content_hash="sha256:abc",
                extractor_name="image.metadata", extractor_version="0.1.0",
                source_type="image", analysis_tier="native", config={},
                completeness="complete",
                coverage={"units": "images", "processed": 1, "total": 1},
                observation_count=0, started_at=FIXED_CLOCK,
                finished_at=FIXED_CLOCK))
    decision = image_ocr_decision(result=opaque)
    assert decision.run_ocr is True
    assert decision.state is None       # §2.2's states are about documents


def test_an_image_with_usable_metadata_does_not_reach_ocr():
    from extractors.shape import location, observation, run, segment
    from extractors.sink import ExtractionResult
    with_exif = ExtractionResult(
        run=run(file_id="f1", content_hash="sha256:abc",
                extractor_name="image.metadata", extractor_version="0.1.0",
                source_type="image", analysis_tier="native", config={},
                completeness="complete",
                coverage={"units": "images", "processed": 1, "total": 1},
                observation_count=1, started_at=FIXED_CLOCK, finished_at=FIXED_CLOCK),
        observations=(observation(
            file_id="f1", content_hash="sha256:abc",
            extractor_name="image.metadata", extractor_version="0.1.0",
            source_type="image", raw_value="Canon",
            location=location(zone="metadata",
                              container_path=(segment("field", label="Make"),)),
            observed_at=FIXED_CLOCK, reliability="direct", signal_tier=1),))
    assert image_ocr_decision(result=with_exif).run_ocr is False


def test_ocr_text_density_is_not_an_input_anywhere_in_the_policy():
    # §2.6: "OCR text density is also not a reliable screenshot detector." Nothing
    # here counts characters, and Task 13 asserts the emission half.
    import inspect

    import extractors.ocr_policy as module
    source = inspect.getsource(module.image_ocr_decision)
    for forbidden in ("len(", "density", "count("):
        assert forbidden not in source, forbidden


def test_text_layer_state_is_available_on_its_own():
    assert text_layer_state(result=extracted(""), file_id="f1",
                            content_hash="sha256:abc",
                            no_usable_facts=lambda f, c: False) == "text_layer_absent"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_ocr_policy.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'extractors.ocr_policy'`

- [ ] **Step 3: Write the implementation**

```python
# src/extractors/ocr_policy.py
"""When OCR may run (sections 2.2 and 2.7). One signal, and no quality heuristic.

Section 2.2 requires the system to distinguish a PDF with NO text layer from one with
a BROKEN text layer:

    text_layer_absent   no text at all      route DIRECTLY to OCR
    text_layer_broken   text, but the stored evidence yields no usable facts
                                            TARGETED OCR, and only after P6 says so
    text_layer_usable   text and facts      no OCR

The state is not an observation and not a run field. "No text layer" is an ABSENCE,
and P4 is explicit that an extractor "may not write an 'EXIF absent', 'no text layer'
or 'metadata stripped' observation; the run record already says it, and an absence
written as evidence is a value P6 can rank." Section 2.2's requirement that the two be
DISTINGUISHED is met by the two paths behaving differently.

Section 2.2 forbids the alternative trigger outright: "The system should not use
unreliable global language-quality checks that incorrectly punish multilingual or
mathematics-heavy documents", and section 2.7 repeats it - not "because a broad
quality heuristic says the text looks unusual". So the only input about a non-empty
text layer is P6's `no_usable_facts` verdict (M11), injected with no default, and the
threshold behind that verdict is SPEC Open question 1 and is not answered here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from extractors.sink import ExtractionResult

#: Section 2.2's own three.
TEXT_LAYER_STATES: tuple[str, str, str] = (
    "text_layer_usable", "text_layer_absent", "text_layer_broken",
)


@dataclass(frozen=True)
class OcrDecision:
    """Whether E6 may run, and on what footing.

    `state` is section 2.2's text-layer state for a document and is None for an
    image, which has no text layer to have a state about.
    """
    state: str | None
    run_ocr: bool
    targeted: bool
    reason: str


def _has_text(result: ExtractionResult) -> bool:
    """Did this run store any text at all? Reads the run's own units, nothing else."""
    return any(unit["text"].strip() for unit in result.text_units)


def _has_metadata_observation(result: ExtractionResult) -> bool:
    return any(o["location"]["zone"] == "metadata" for o in result.observations)


def text_layer_state(*, result: ExtractionResult, file_id: str, content_hash: str,
                     no_usable_facts: Callable[[str, str], bool]) -> str:
    """Section 2.2's state for a document run.

    P6 is asked ONLY about a non-empty text layer: a document with no text has no
    stored evidence P6 could have failed to make facts from, so its verdict there
    could not mean what it means in the broken case.
    """
    if not _has_text(result):
        return "text_layer_absent"
    if no_usable_facts(file_id, content_hash):
        return "text_layer_broken"
    return "text_layer_usable"


def document_ocr_decision(*, result: ExtractionResult, file_id: str,
                          content_hash: str,
                          no_usable_facts: Callable[[str, str], bool]) -> OcrDecision:
    """Section 2.2's OCR route for a document."""
    state = text_layer_state(result=result, file_id=file_id,
                             content_hash=content_hash,
                             no_usable_facts=no_usable_facts)
    if state == "text_layer_absent":
        return OcrDecision(state=state, run_ocr=True, targeted=False,
                           reason="no text layer; section 2.2 routes directly to OCR")
    if state == "text_layer_broken":
        return OcrDecision(
            state=state, run_ocr=True, targeted=True,
            reason=("P6 reported no usable facts from the stored evidence; "
                    "section 2.2 allows targeted OCR only on that verdict"))
    return OcrDecision(state=state, run_ocr=False, targeted=False,
                       reason="the text layer produced usable facts")


def image_ocr_decision(*, result: ExtractionResult) -> OcrDecision:
    """Section 2.7's trigger for an image: "when a file yields no usable text AND no
    usable metadata, including scanned PDFs, confirmed screenshots, and opaque images
    without EXIF."

    Reading an absence to make a routing decision is allowed; WRITING one as an
    observation is not (M2), and nothing here writes anything.
    """
    if _has_text(result) or _has_metadata_observation(result):
        return OcrDecision(state=None, run_ocr=False, targeted=False,
                           reason="the file yielded usable text or usable metadata")
    return OcrDecision(
        state=None, run_ocr=True, targeted=False,
        reason=("no usable text and no usable metadata (section 2.7); an opaque "
                "image is how a screenshot becomes understandable at all"))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p5/test_p5_ocr_policy.py -v`
Expected: PASS — 12 passed

- [ ] **Step 5: Commit**

```bash
git add src/extractors/ocr_policy.py tests/p5/test_p5_ocr_policy.py
git commit -m "feat(P5): §2.2's three text-layer states and §2.7's OCR trigger, no quality heuristic"
```

---

### Task 9: E2 — DOCX (§2.3), full semantic structure with its zones intact

**Files:**
- Create: `src/extractors/docx.py`
- Test: `tests/p5/test_p5_docx.py`

**Interfaces:**
- Consumes: `extractors.shape`, `extractors.reading`, `extractors.safety.admit`, `extractors.runs.coverage`; caller-supplied `read_docx(path) -> DocxDocument` and `find_structured_strings`.
- Produces: `VERSION`, `EXTRACTOR_NAME`, `TITLE_PROPERTIES`, `DocxParagraph`, `DocxCell`, `DocxLink`, `DocxAnnotation`, `DocxDocument`, `extract_docx()`.

**§2.3, in full, is this task.** *"DOCX extraction should preserve the full semantic structure of a
document rather than reading only its first few paragraphs. The engine should extract core properties,
all paragraphs in order, heading levels, tables and table-cell text, headers and footers where
feasible, hyperlinks, document relationships, and available revision or comment metadata."*

**Tables are mandatory, not optional.** §2.3: *"Resumes, forms, applications, invoices, and
administrative documents often place their most useful information in cells rather than body
paragraphs."* A cell locates as `table:table=T/row=R/column=C` — P4's fixture 4, and §2.8's own DOCX
example.

**Zone fidelity is the load-bearing requirement.** §2.3: *"The extractor must preserve the difference
between a heading, a table label, a filename, and ordinary body text, because those locations carry
different evidentiary weight."* And the case that makes it concrete: *"`Wash U.docx` may have an
unhelpful filename but a heading stating, 'Please tell us what you are interested in studying at
college and why.' That heading is strong evidence for the College Applications domain, even though the
filename itself does not reveal the file's purpose."* If the zone is flattened here, no later part can
recover it.

**Heading *levels* are the container path's depth, not a new field.** §2.3 requires heading levels;
P4's zone vocabulary has one `heading` zone (*"a heading at any level"*) and no level field. P4's
segment table resolves it: `heading` is addressed by *"index (ordinal within parent)"*, and *"every
prefix of a valid path is itself a valid coarser address"* — so an H2 under an H1 is
`heading=1/heading=2` and the level is the chain's depth. The reader reports each paragraph's heading
ancestry; nothing new is invented and nothing is lost.

**One text unit per paragraph and per cell, and no whole-document unit.** Every heading, footer and
cell observation carries a span, and P4's conformance rule 10 requires a unit at exactly that container
path. §2.9's *"full text"* for a text document is the concatenation of those units in container order —
storing it a second time as a whole-file unit would put the same characters in two places, which is the
duplication G1 exists to end.

**Body paragraphs are units, not observations** — for the same reason a page of text is not an
observation (G1: *"a page of text is not a located value"*). Values inside body text arrive through the
same injected `find_structured_strings` E1 uses, so the two extractors differ in their reader and in
nothing else that reaches P4.

**Author metadata is supporting information only, and carries no marker.** §2.3: *"DOCX author metadata
should remain supporting information only, because it may identify a prior editor, a document template,
or a script rather than the meaningful subject or purpose of the file."* Exactly as in E1: emitted
verbatim at `zone = metadata` with `reliability: direct`, and **no flag** — M4 puts the discount rule
in P6.

**Filename and extension are not emitted here.** §2.3 does not ask for them, and O5 assigns them to the
`filesystem` run (Task 6). Emitting them twice would be two homes for one value.

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_docx.py
"""E2 - §2.3. Done-means 6: "DOCX table cells and heading zones are present and
distinguishable from body text.\""""
from pathlib import Path

import pytest

from extractors.docx import (
    DocxAnnotation, DocxCell, DocxDocument, DocxLink, DocxParagraph, EXTRACTOR_NAME,
    extract_docx,
)
from extractors.reading import StructuredString
from extractors.safety import ProtectedContainerRefused, SafetyPolicy

from conftest import FIXED_CLOCK
from p4_stub import locator_for

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
FILE_ROW = {"file_id": "f1", "content_hash": "sha256:abc", "filename": "Wash U.docx"}

PROMPT = "Please tell us what you are interested in studying at college and why."


def a_wash_u_docx() -> DocxDocument:
    """The SPEC's `wash-u.docx`: an unhelpful filename, a decisive heading, and the
    data in table cells."""
    return DocxDocument(
        core_properties={"title": "", "creator": "python-docx",
                         "lastModifiedBy": "J. Yung",
                         "created": "2026-07-17T14:03:22Z"},
        iso_dates={"created": "2026-07-17T14:03:22+00:00"},
        paragraphs=(
            DocxParagraph(index=1, text="Application Essay", zone="heading",
                          heading_path=((1, "Application Essay"),)),
            DocxParagraph(index=2, text=PROMPT, zone="heading",
                          heading_path=((1, "Application Essay"), (1, PROMPT))),
            DocxParagraph(index=3, text="I want to study economics at Wash U.",
                          zone="body",
                          heading_path=((1, "Application Essay"), (1, PROMPT))),
            DocxParagraph(index=4, text="Page 1 of 2", zone="header_footer"),
        ),
        cells=(DocxCell(table=3, row=1, column=1, text="Institution",
                        column_header="Field"),
               DocxCell(table=3, row=2, column=1, text="Wash U",
                        column_header="Field")),
        links=(DocxLink(target="https://admissions.wustl.edu", paragraph=3),),
        relationships=("word/document.xml", "word/footer1.xml"),
        annotations=(DocxAnnotation(name="comment", text="tighten this",
                                    paragraph=3),),
    )


def find_wash_u(text: str):
    at = text.find("Wash U")
    return (StructuredString(kind="identifier", start=at, end=at + 6),) if at != -1 else ()


def run_it(document=None, finder=find_wash_u):
    return extract_docx(file_row=FILE_ROW, path=Path("/corpus/Wash U.docx"),
                        policy=OPEN_POLICY,
                        read_docx=lambda path: document or a_wash_u_docx(),
                        find_structured_strings=finder, now=FIXED_CLOCK,
                        context_window=40)


def test_every_observation_conforms_to_p4s_shape(sink):
    sink.write(run_it())
    sink.conforms()


def test_a_heading_a_table_cell_and_body_text_are_three_distinguishable_zones(sink):
    # §2.3: "The extractor must preserve the difference between a heading, a table
    # label, a filename, and ordinary body text, because those locations carry
    # different evidentiary weight."
    sink.write(run_it())
    zones = {o["location"]["zone"] for o in sink.observations}
    assert {"heading", "table", "header_footer"} <= zones
    heading = [o for o in sink.observations if o["raw_value"] == PROMPT][0]
    assert heading["location"]["zone"] == "heading"
    cell = [o for o in sink.observations
            if o["raw_value"] == "Wash U" and o["location"]["zone"] == "table"][0]
    assert locator_for(cell["location"]) == "table:table=3/row=2/column=1#0-6"


def test_the_decisive_heading_survives_the_unhelpful_filename(sink):
    # §2.3's own worked case. The filename says nothing; the heading says everything,
    # and the heading's zone is what makes that difference visible to P6.
    sink.write(run_it())
    prompts = [o for o in sink.observations if o["raw_value"] == PROMPT]
    assert len(prompts) == 1
    assert prompts[0]["location"]["zone"] == "heading"
    assert prompts[0]["reliability"] == "possible"


def test_heading_level_is_the_container_paths_depth(sink):
    # §2.3 requires heading levels; P4 has one `heading` zone and no level field, and
    # its segment table addresses `heading` by "ordinal within parent". Depth is the
    # level.
    sink.write(run_it())
    top = [o for o in sink.observations
           if o["raw_value"] == "Application Essay"][0]
    nested = [o for o in sink.observations if o["raw_value"] == PROMPT][0]
    assert len(top["location"]["container_path"]) == 1
    assert len(nested["location"]["container_path"]) == 2
    assert locator_for(nested["location"]) == f"heading:heading=1/heading=1#0-{len(PROMPT)}"


def test_every_cell_and_paragraph_has_its_own_addressable_unit(sink):
    # P4 conformance rule 10.
    run_id = sink.write(run_it())
    paths = {locator_for({"zone": "x", "container_path": u["container_path"],
                          "text_span": None, "time_span": None})
             for u in sink.units_for(run_id)}
    assert "x:table=3/row=2/column=1" in paths
    assert "x:heading=1/heading=1/paragraph=3" in paths
    assert not [u for u in sink.units_for(run_id) if u["container_path"] == ()]


def test_a_body_paragraph_is_a_unit_and_not_an_observation(sink):
    # G1's reasoning, applied to §2.3: a paragraph of body text is not a located value.
    run_id = sink.write(run_it())
    body_text = "I want to study economics at Wash U."
    assert any(u["text"] == body_text for u in sink.units_for(run_id))
    assert not [o for o in sink.observations if o["raw_value"] == body_text]


def test_a_value_inside_body_text_arrives_through_the_injected_finder(sink):
    sink.write(run_it())
    found = [o for o in sink.observations
             if o["raw_value"] == "Wash U" and o["location"]["zone"] == "body"]
    assert len(found) == 1
    assert found[0]["location"]["container_path"][-1]["kind"] == "paragraph"


def test_the_column_header_is_carried_on_the_column_segment(sink):
    # P4's segment table: "`column` | index | column header text".
    sink.write(run_it())
    cell = [o for o in sink.observations
            if o["raw_value"] == "Wash U" and o["location"]["zone"] == "table"][0]
    assert cell["location"]["container_path"][-1]["label"] == "Field"


def test_hyperlinks_relationships_and_comments_are_all_emitted(sink):
    # §2.3: "hyperlinks, document relationships, and available revision or comment
    # metadata."
    sink.write(run_it())
    by_zone = {}
    for o in sink.observations:
        by_zone.setdefault(o["location"]["zone"], []).append(o["raw_value"])
    assert "https://admissions.wustl.edu" in by_zone["link"]
    assert "word/footer1.xml" in by_zone["metadata"]
    assert "tighten this" in by_zone["annotation"]


def test_the_hyperlink_target_keeps_its_position_and_carries_no_span(sink):
    # The target is a machine slot, not a substring of the paragraph, so there is
    # nothing for a span to index - P4 rule 4's coarser address.
    sink.write(run_it())
    link = [o for o in sink.observations
            if o["raw_value"] == "https://admissions.wustl.edu"][0]
    assert link["location"]["text_span"] is None
    assert link["reliability"] == "direct"
    assert link["location"]["container_path"][-1]["kind"] == "paragraph"


def test_the_author_metadata_is_supporting_information_with_no_marker(sink):
    # §2.3: "DOCX author metadata should remain supporting information only." M4: the
    # discount rule is P6's and there is no marker on the record.
    from extractors.shape import OBSERVATION_FIELDS
    sink.write(run_it())
    creator = [o for o in sink.observations
               if locator_for(o["location"]) == "metadata:field=creator"][0]
    assert creator["raw_value"] == "python-docx"
    assert creator["reliability"] == "direct"
    assert tuple(k for k in creator if k != "run_id") == OBSERVATION_FIELDS


def test_an_empty_core_property_produces_no_row(sink):
    # An observation records presence, never absence.
    sink.write(run_it())
    assert not [o for o in sink.observations
                if locator_for(o["location"]) == "title:field=title"]


def test_neither_the_filename_nor_the_extension_is_re_emitted_here(sink):
    # O5: they are the `filesystem` run's, and two homes for one value is the defect.
    sink.write(run_it())
    assert not [o for o in sink.observations
                if o["location"]["zone"] in ("filename", "path")]


def test_the_run_is_native_and_names_the_docx_extractor(sink):
    run_id = sink.write(run_it())
    row = sink.run_for(run_id)
    assert row["extractor_name"] == EXTRACTOR_NAME == "docx.structure"
    assert row["source_type"] == "text_document"
    assert row["analysis_tier"] == "native"
    assert row["completeness"] == "complete"
    assert row["coverage"]["units"] == "paragraphs"


def test_e2_refuses_a_protected_path_before_it_calls_its_reader():
    calls = []
    policy = SafetyPolicy(is_protected_container=lambda path: True,
                          is_dataless=lambda path: False)
    with pytest.raises(ProtectedContainerRefused):
        extract_docx(file_row=FILE_ROW, path=Path("/Applications/T.app/x.docx"),
                     policy=policy,
                     read_docx=lambda path: calls.append(path) or a_wash_u_docx(),
                     find_structured_strings=find_wash_u, now=FIXED_CLOCK,
                     context_window=40)
    assert calls == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_docx.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'extractors.docx'`

- [ ] **Step 3: Write the implementation**

```python
# src/extractors/docx.py
"""E2 - DOCX extraction (section 2.3).

"DOCX extraction should preserve the FULL SEMANTIC STRUCTURE of a document rather than
reading only its first few paragraphs... core properties, all paragraphs in order,
heading levels, tables and table-cell text, headers and footers where feasible,
hyperlinks, document relationships, and available revision or comment metadata."

Two requirements are load-bearing and shape everything here:

  Tables are mandatory. "Resumes, forms, applications, invoices, and administrative
  documents often place their most useful information in cells rather than body
  paragraphs." A cell locates as table=T/row=R/column=C (section 2.8's own example).

  Zones must stay distinct. "The extractor must preserve the difference between a
  heading, a table label, a filename, and ordinary body text, because those locations
  carry different evidentiary weight." Section 2.3's own case is `Wash U.docx`: an
  unhelpful filename and a decisive heading. Flatten the zone here and no later part
  can recover it.

Heading LEVEL is the container path's depth, not a new field: P4 has one `heading`
zone ("a heading at any level") and addresses `heading` by "ordinal within parent", so
an H2 under an H1 is heading=1/heading=2.
"""
from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from typing import Any, Callable, Mapping

from extractors.reading import ZONE_BY_STRUCTURED_KIND, StructuredString
from extractors.runs import coverage
from extractors.safety import SafetyPolicy, admit
from extractors.shape import (
    context_for, location, normalize_mechanical, observation, run, segment, text_unit,
)
from extractors.sink import ExtractionResult

VERSION = "0.1.0"
EXTRACTOR_NAME = "docx.structure"
SOURCE_TYPE = "text_document"
ANALYSIS_TIER = "native"

#: The core property that is its own zone (P4: `title` is "the document title").
TITLE_PROPERTIES: tuple[str, ...] = ("title",)


@dataclass(frozen=True)
class DocxParagraph:
    """One paragraph, in order.

    `zone` is one of P4's: `heading`, `body` or `header_footer`. `heading_path` is the
    paragraph's heading ancestry as (ordinal, label) pairs, outermost first; for a
    heading paragraph its LAST element is that heading.
    """
    index: int
    text: str
    zone: str
    heading_path: tuple[tuple[int, str], ...] = ()


@dataclass(frozen=True)
class DocxCell:
    table: int
    row: int
    column: int
    text: str
    column_header: str | None = None


@dataclass(frozen=True)
class DocxLink:
    target: str
    paragraph: int | None = None


@dataclass(frozen=True)
class DocxAnnotation:
    """Section 2.3's "available revision or comment metadata"."""
    name: str
    text: str
    paragraph: int | None = None


@dataclass(frozen=True)
class DocxDocument:
    """What an injected `read_docx` returns."""
    core_properties: Mapping[str, str]
    paragraphs: tuple[DocxParagraph, ...] = ()
    cells: tuple[DocxCell, ...] = ()
    links: tuple[DocxLink, ...] = ()
    relationships: tuple[str, ...] = ()
    annotations: tuple[DocxAnnotation, ...] = ()
    iso_dates: Mapping[str, str] = dataclass_field(default_factory=dict)


def _heading_segments(paragraph: DocxParagraph) -> tuple:
    return tuple(segment("heading", index=ordinal, label=label)
                 for ordinal, label in paragraph.heading_path)


def _paragraph_path(paragraph: DocxParagraph) -> tuple:
    """A heading paragraph IS its innermost heading segment; anything else hangs off
    the heading ancestry as a `paragraph` segment (P4 names the kind at section 2.3)."""
    if paragraph.zone == "heading":
        return _heading_segments(paragraph)
    return _heading_segments(paragraph) + (segment("paragraph", index=paragraph.index),)


def extract_docx(*, file_row: Mapping[str, Any], path: Path, policy: SafetyPolicy,
                 read_docx: Callable[[Path], DocxDocument],
                 find_structured_strings: Callable[[str], tuple[StructuredString, ...]],
                 now: str, context_window: int) -> ExtractionResult:
    """Section 2.3's full semantic structure, as P4 records."""
    admit(path, policy=policy)
    document = read_docx(path)

    observations: list[Mapping[str, Any]] = []
    units: list[Mapping[str, Any]] = []

    def emit(*, zone, raw, container_path, span, unit_text, reliability,
             normalized=None):
        before = after = ""
        truncated = False
        if span is not None and unit_text is not None:
            before, after, truncated = context_for(unit_text, span["start"],
                                                   span["end"], window=context_window)
        observations.append(observation(
            file_id=file_row["file_id"], content_hash=file_row["content_hash"],
            extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
            source_type=SOURCE_TYPE, raw_value=raw,
            normalized_value=normalized if normalized is not None
            else normalize_mechanical(raw),
            location=location(zone=zone, container_path=container_path,
                              text_span=span),
            context_before=before, context_after=after, context_truncated=truncated,
            observed_at=now, reliability=reliability,
        ))

    for name in sorted(document.core_properties):
        value = document.core_properties[name]
        if not value:
            continue                     # presence only; an absence is never a row
        emit(zone="title" if name in TITLE_PROPERTIES else "metadata",
             raw=value, container_path=(segment("field", label=name),), span=None,
             unit_text=None, reliability="direct",
             normalized=document.iso_dates.get(name))

    for paragraph in document.paragraphs:
        if not paragraph.text:
            continue
        container = _paragraph_path(paragraph)
        units.append(text_unit(text=paragraph.text, container_path=container))
        whole = {"start": 0, "end": len(paragraph.text)}
        if paragraph.zone in ("heading", "header_footer"):
            # A heading and a running footer are short, labelled positions and are
            # values in their own right (section 2.3; section 3.7 weights "a footer").
            emit(zone=paragraph.zone, raw=paragraph.text, container_path=container,
                 span=whole, unit_text=paragraph.text, reliability="possible")
        for found in find_structured_strings(paragraph.text):
            raw = paragraph.text[found.start:found.end]
            emit(zone=ZONE_BY_STRUCTURED_KIND.get(found.kind, paragraph.zone),
                 raw=raw, container_path=container,
                 span={"start": found.start, "end": found.end},
                 unit_text=paragraph.text, reliability="possible")

    for cell in document.cells:
        if not cell.text:
            continue
        container = (segment("table", index=cell.table),
                     segment("row", index=cell.row),
                     segment("column", index=cell.column, label=cell.column_header))
        units.append(text_unit(text=cell.text, container_path=container))
        emit(zone="table", raw=cell.text, container_path=container,
             span={"start": 0, "end": len(cell.text)}, unit_text=cell.text,
             reliability="possible")

    for link in document.links:
        container = ((segment("paragraph", index=link.paragraph),)
                     if link.paragraph is not None else ())
        emit(zone="link", raw=link.target, container_path=container, span=None,
             unit_text=None, reliability="direct")

    for target in document.relationships:
        emit(zone="metadata", raw=target,
             container_path=(segment("field", label="relationship"),), span=None,
             unit_text=None, reliability="direct")

    for annotation in document.annotations:
        container = ((segment("paragraph", index=annotation.paragraph),)
                     if annotation.paragraph is not None
                     else (segment("field", label=annotation.name),))
        emit(zone="annotation", raw=annotation.text, container_path=container,
             span=None, unit_text=None, reliability="direct")

    paragraphs = len(document.paragraphs)
    return ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
                source_type=SOURCE_TYPE, analysis_tier=ANALYSIS_TIER,
                config={"reader": "injected"}, completeness="complete",
                coverage=coverage("paragraphs", paragraphs, paragraphs),
                observation_count=len(observations), started_at=now, finished_at=now),
        observations=tuple(observations),
        text_units=tuple(units),
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p5/test_p5_docx.py -v`
Expected: PASS — 15 passed

- [ ] **Step 5: Commit**

```bash
git add src/extractors/docx.py tests/p5/test_p5_docx.py
git commit -m "feat(P5): E2 DOCX - tables mandatory, zones distinct, heading level as path depth"
```

---
