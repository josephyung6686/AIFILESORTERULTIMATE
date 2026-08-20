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
and the same tests import from **`evidence_shape`** — the package P4 actually publishes. The swap is
written out verbatim in Task 2 so it is a delete-and-import, not a search-and-replace against a module
path that does not exist. (An earlier draft of this plan named `evidence.records` / `evidence.conformance`;
no such package exists in P4's plan, and shipping both would have left two locator implementations —
the drift §2.8 exists to prevent.) The production modules under `src/extractors/` do not change at
all, because they never imported the stub — they talk to the injected `EvidenceSink` and nothing else.

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
  surfaces it as `source_type: filesystem` observations referencing P3's row. **P5 hashes no file
  bytes**: `hashlib` is bound in exactly one module, `shape.py`, where `fingerprint()` hashes a
  *configuration mapping* to produce P4's `config_fingerprint` — never a path and never a byte of a
  file. P5 also determines no MIME type of its own. Task 20 asserts both by introspection.
  *(Corrected 2026-08-20: this clause previously read "`hashlib` does not appear in
  `src/extractors/`", which Task 2's own `shape.fingerprint` contradicts. The rule was always about
  file bytes; the wording is now what the rule is. See Self-Review.)*
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
`completeness` (nine, after C4 added `dataless`). P5 restates only the two restrictions that are P5's own half of the contract:
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

## Catalogue wiring — the production caller loads these, the tests do not

`planning/deferred-catalogues/` holds seven hand-authored catalogues (B9, authored 2026-08-20).
They are the content behind five of this plan's caller-supplied strategies, and **nothing in this
plan loads them** — which is correct, and also the way they rot.

| strategy parameter | catalogue | task |
|---|---|---|
| `find_structured_strings` | 06 citation & identifier patterns | E1 |
| `recognize_markers` | 05 `p5_evidence_markers`, 07 archive markers | E3, E4 |
| `filename_pattern` | 04 camera filename patterns | E5 |
| `dimension_signal` | 02 screen resolutions, then 03 sensor ratios (in that order) | E5 |
| — (P6's, not P5's) | 01 tool producer strings | P6's discount rule |

**The production caller loads these seven JSON files and injects them. `src/extractors/` imports
none of them** — Task 20's no-invention guard fails if a gazetteer, regex table, resolution or
producer string appears in the package, and copying the JSON into `src/extractors/catalogues.py`
would satisfy the letter of that guard while destroying its point.

**Tests inject fixtures, not the live JSON.** A test that loads the real catalogue couples this
plan's green-ness to hand-authored data that changes for reasons unrelated to P5, and a catalogue
edit would then fail an extractor test. If an integration test over the real files is wanted, it is
a *named* test that says so.

Two consequences worth stating plainly: an executor can take every task in this plan green with
`dimension_signal=lambda *_: None` and never discover the catalogues exist; and a v1 deployment that
forgets to wire them sees no citations, no camera filenames, no screen dimensions and no project
markers — with nothing failing, because absence is indistinguishable from a corpus that contains
none of those things.

---

## Dependencies a real deployment must choose

Named, not chosen. Every one is a **NEEDS JOSEPH** item; nothing here is installed by this plan, and
every reader below is a constructor parameter with a deterministic fixture implementation in tests.
The full per-format table — including which of them the standard library *does* cover — is
*Dependencies a real deployment needs*, at the end of this plan; this table is the reader-by-reader
summary.

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
the real P4 package:

```python
from evidence_shape.locator import parse_locator, serialize_locator
from evidence_shape.vocabulary import SOURCE_TYPES, ZONES
from evidence_shape.conformance import validate_observation
from evidence_shape.store import observation_keys_for_run, record_run_event
```

`locator_for` in this stub is P4's `serialize_locator`; `ZONES` / `SOURCE_TYPES` live in
`evidence_shape.vocabulary`, not beside the records. Nothing
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

    **It delegates to P4 and computes nothing itself.** P5 previously called
    `hashlib.sha256` on the same canonical JSON, while P4's `sha256_of`
    length-prefixes the part before hashing. The canonical bytes were identical and
    the digests never were, so P4 rejected EVERY run record P5 emitted -- and because
    `config_fingerprint` is in §3.4's cache key and rule 8's four-field replay key,
    two runs of one process would never have matched and replay would have reported
    divergence that did not happen. P4 owns the field, so P4 computes it; a second
    computation of one value is the same defect as a second name for one concept.
    """
    return sha256_of(canonical_json(dict(config)))


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
    # When P4 ships, this stub is deleted and these are the real imports:
    #   from evidence_shape.locator import parse_locator, serialize_locator
    #   from evidence_shape.vocabulary import SOURCE_TYPES, ZONES
    #   from evidence_shape.conformance import validate_observation
    # P4 publishes `serialize_locator`, not `locator_for`, and keeps the vocabularies
    # in their own module. There is no `evidence` package -- it is `evidence_shape`.
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

#: P4 `completeness` (closed), after B1 added `metadata_only` and C4 added `dataless`.
COMPLETENESS: tuple[str, ...] = (
    "complete", "capped", "partial", "metadata_only", "deferred", "unsupported",
    "unreadable", "failed", "dataless",
)

#: P4 conformance rule 9, as M3 relaxed it: `unreadable` and `partial` runs MAY and
#: normally DO carry observations (section 2.9's "indexed-but-unreadable").
#: P4 conformance rule 9. MUST equal P4's tuple: `metadata_only` joined it when
#: fixture 19 was frozen (the stopping extractor emits nothing; the file stays
#: indexed through its `filesystem` run), and `dataless` joined it with C4 (nothing
#: was opened, so nothing was seen). This is not documentation -- the rule-9 check
#: below reads it, so a three-value copy here would let P5 emit observations on a
#: `metadata_only` run that P4 forbids: one rule, two parts, opposite behaviour.
ZERO_OBSERVATION_COMPLETENESS: tuple[str, ...] = (
    "unsupported", "deferred", "failed", "metadata_only", "dataless")

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
    # The GATE writes nothing, and that is still right: it raises, and a gate that
    # also wrote would be doing two jobs. P4 OQ6 closed on 2026-08-20 with a ninth
    # `completeness` value, `dataless`, so the refusal is now NAMEABLE -- but the row
    # is written by whoever CATCHES DatalessRefused (the router, Task 4), not here.
    # Until that caller exists, a dataless file is still absent from §8.6's count
    # line; what changed is that the vocabulary can now say why, instead of the file
    # being filed under a word that lies about it.
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
deleted." The nine `completeness` values are P4's and are not restated here; what is
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

> **Settled 2026-08-20 — fixture 19 is the frozen reading.** P4's fixture 19 says a `metadata_only` run carries
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

### Task 10: E3 — structured text and code (§2.4), and §2.4's two outcomes with no third

**Files:**
- Create: `src/extractors/structured_text.py`
- Test: `tests/p5/test_p5_structured_text.py`

**Interfaces:**
- Consumes: `extractors.shape`, `extractors.reading`, `extractors.safety.admit`, `extractors.runs.coverage`; caller-supplied `read_text_document(path) -> TextDocument | None` and `find_structured_strings`.
- Produces: `VERSION`, `EXTRACTOR_NAME`, `STRUCTURED_TEXT_SOURCE_TYPES`, `STRUCTURAL_MARKER_KINDS`, `WrongFamily`, `UnknownMarkerKind`, `StructuralMarker`, `TextDocument`, `extract_structured_text()`, `unsupported_result()`.

**§2.4, in full, is this task and Task 11.** *"Text-bearing files such as Markdown, plain text, JSON,
CSV, source code, notebooks, and configuration files should be handled through a lighter
structured-text extractor. The engine should store their text, filename, extension, language where
relevant, headings, and structural indicators such as repository markers, package manifests, notebook
metadata, and README files."* The §2.9 long-tail families that also route to E3 — spreadsheets,
presentations, email, calendar, contacts, audio/video — are Task 11; this task is E3's §2.4 half and
the `unsupported` path both halves share.

**Where each §2.4 field lands.**

| §2.4 requires | where it lands | why |
|---|---|---|
| text | `text_units`, one whole-file row at `container_path: []` | G1 and the SPEC's E3 line: *"the full text to P4's `text_units` as one whole-file unit, `container_path: []`"* |
| filename · extension | **the `filesystem` run** (Task 6), not here | O5. The SPEC's Contract out: *"P5 surfaces it as `source_type: filesystem` observations referencing P3's row, which is how a filename … becomes citable evidence."* Emitting it a second time here would be two homes for one value. See *SPEC vs design*. |
| language, where relevant | observation, zone `metadata`, `field=language`, `direct` | reader-supplied. P5 detects no language and holds no language list — §2.7's *"appropriate language support"* is Deferred and Task 20 guards it |
| headings | observation zone `heading` **and** a `text_units` row at `[{heading, K}]` | exactly E1's rule: P4 conformance rule 10 requires a unit at the container path an observation's span indexes into |
| structural indicators | observations, zone `metadata`, `field=<§2.4's own class name>`, `direct` | §2.4 names four classes; **which files are members is Deferred** and the reader supplies them |

**The extractor is `text.structured` — one family, two modules.** The router sends eight
`source_type`s to `text.structured`; §2.4's two (`text_document`, `code_structured`) are handled here
and §2.9's six in Task 11. They publish **one** `EXTRACTOR_NAME`, because E3 is one extractor family in
the SPEC and `runs.ANALYSIS_TIER_BY_EXTRACTOR` keys the tier on the family name. A `source_type` from
the other half raises `WrongFamily` rather than being extracted in the wrong shape; Task 11 asserts the
two halves partition the router's set exactly, with no gap and no overlap.

**Code relies on local structural evidence, and E3 reads no code.** §2.4: *"Code-related files should
rely heavily on local structural evidence, including repository roots and package files, rather than
forcing semantic analysis to infer a project from arbitrary code text."* So E3 emits the markers the
reader found and the strings the injected finder found, and nothing else: there is no import parser, no
symbol table and no project inference in `src/extractors/`. §2.9's *"language, imports, notebook cell
types, package manifests, schema keys, repository markers, project-root signals"* all arrive as reader
output — a marker, a `field=` slot or a found string — and never as a P5-side analysis.

**§2.4's two outcomes, and the third one it forbids.** *"Spreadsheet and presentation formats should
either receive dedicated extraction support … or be marked clearly as unsupported in the initial
release. The system should never silently treat an unsupported format as an empty document, because an
empty extraction result is different from an extractor that does not yet exist."* The reader returning
`None` means **this deployment ships no reader for this format** and produces `completeness:
unsupported` with zero observations; a reader returning `TextDocument(text="")` means **the file was
empty** and produces `completeness: complete` with zero observations. Two runs, two values, one query
apart — SPEC Done-means 1. **SPEC Open question 5 is CLOSED (B6, ratified 2026-08-20): spreadsheets and
presentations SHIP AT LAUNCH.** That does not change this task's shape — the reader is still injected and
P5 still names no library, so Task 20's guard keeps passing — but it changes what `unsupported` MEANS.
It now marks a format with genuinely no extractor, never one deferred by choice, and a v1 deployment
that ships without `openpyxl` / `python-pptx` wired is not conforming.

**No `partial` and no `failed` are written here.** A text file is read whole or not at all; a reader
that raises is the caller's error to record, and inventing a `failed` path around an injected callable
would be P5 deciding what a library failure means. Task 12's archives are where `partial` is real.

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_structured_text.py
"""E3's §2.4 half. SPEC Done-means 1: "`unsupported` is distinguishable from
`complete`-with-zero-observations in a query."
"""
from pathlib import Path

import pytest

from extractors.reading import Region, StructuredString
from extractors.safety import DatalessRefused, ProtectedContainerRefused, SafetyPolicy
from extractors.structured_text import (
    EXTRACTOR_NAME, STRUCTURAL_MARKER_KINDS, StructuralMarker, TextDocument,
    UnknownMarkerKind, WrongFamily, extract_structured_text,
)

from conftest import FIXED_CLOCK
from p4_stub import locator_for

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
FILE_ROW = {"file_id": "f-readme", "content_hash": "sha256:readme",
            "filename": "README.md"}

BODY = "This project belongs to U Chicago and ships from src.\n"
HEADING = "Setup"


def a_readme() -> TextDocument:
    text = HEADING + "\n" + BODY
    return TextDocument(
        text=text,
        language="Markdown",
        headings=(Region(zone="heading", start=0, end=len(HEADING), ordinal=1,
                         label=HEADING),),
        markers=(StructuralMarker(kind="README file", value="README.md"),
                 StructuralMarker(kind="package manifest", value="package.json")),
    )


def find_u_chicago(text: str):
    at = text.find("U Chicago")
    return (StructuredString(kind="identifier", start=at, end=at + 9),) if at != -1 else ()


def run_it(document="default", source_type="text_document", finder=find_u_chicago):
    body = a_readme() if document == "default" else document
    return extract_structured_text(
        file_row=FILE_ROW, path=Path("/corpus/README.md"), policy=OPEN_POLICY,
        source_type=source_type, read_text_document=lambda path: body,
        find_structured_strings=finder, now=FIXED_CLOCK, context_window=20)


def test_every_observation_conforms_to_p4s_shape(sink):
    sink.write(run_it())
    sink.conforms()


def test_the_full_text_is_one_whole_file_unit(sink):
    # §2.4 + G1: "the full text to P4's `text_units` as one whole-file unit,
    # `container_path: []`".
    run_id = sink.write(run_it())
    whole = [u for u in sink.units_for(run_id) if u["container_path"] == ()]
    assert len(whole) == 1
    assert whole[0]["text"] == HEADING + "\n" + BODY
    assert whole[0]["length"] == len(HEADING + "\n" + BODY)


def test_a_heading_is_both_a_zone_and_an_address(sink):
    run_id = sink.write(run_it())
    heading = [o for o in sink.observations if o["raw_value"] == HEADING][0]
    assert locator_for(heading["location"]) == "heading:heading=1#0-5"
    # P4 conformance rule 10: the span indexes into a unit at exactly that path.
    paths = [u["container_path"] for u in sink.units_for(run_id)]
    assert heading["location"]["container_path"] in paths


def test_language_is_the_readers_value_and_p5_detected_nothing(sink):
    sink.write(run_it())
    language = [o for o in sink.observations
                if o["location"]["container_path"]
                and o["location"]["container_path"][0]["label"] == "language"][0]
    assert language["raw_value"] == "Markdown"
    assert language["location"]["zone"] == "metadata"
    assert language["reliability"] == "direct"


def test_structural_indicators_land_under_section_2_4s_own_class_names(sink):
    sink.write(run_it())
    markers = {o["location"]["container_path"][0]["label"]: o["raw_value"]
               for o in sink.observations
               if o["location"]["container_path"]
               and o["location"]["container_path"][0]["label"] in STRUCTURAL_MARKER_KINDS}
    assert markers == {"README file": "README.md",
                       "package manifest": "package.json"}


def test_a_marker_kind_section_2_4_does_not_name_is_refused():
    # The four CLASSES are §2.4's words; their MEMBERS are Deferred. A reader that
    # coins a fifth class would be authoring vocabulary P5 does not own.
    document = TextDocument(text="x", markers=(StructuralMarker(kind="project vibe",
                                                               value="good"),))
    with pytest.raises(UnknownMarkerKind):
        run_it(document=document)


def test_e3_reads_no_code_and_infers_no_project(sink):
    # §2.4: structural evidence, "rather than forcing semantic analysis to infer a
    # project from arbitrary code text". With no finder and no markers, source code
    # produces its text unit and nothing else.
    source = TextDocument(text="import os\n\n\ndef main():\n    return os.getcwd()\n")
    run_id = sink.write(run_it(document=source, source_type="code_structured",
                               finder=lambda text: ()))
    assert sink.observations_for(run_id) == []
    assert sink.units_for(run_id)[0]["text"] == source.text
    assert sink.run_for(run_id)["completeness"] == "complete"


def test_an_unsupported_format_is_not_an_empty_document(sink):
    # §2.4's whole point, and Done-means 1. Two runs, two values, one query apart.
    empty = sink.write(run_it(document=TextDocument(text="")))
    absent = sink.write(run_it(document=None))

    assert sink.run_for(empty)["completeness"] == "complete"
    assert sink.run_for(absent)["completeness"] == "unsupported"
    assert sink.observations_for(empty) == sink.observations_for(absent) == []
    assert sink.run_for(absent)["extractor_name"] == EXTRACTOR_NAME
    sink.conforms()


def test_an_unsupported_run_stores_no_text_unit(sink):
    run_id = sink.write(run_it(document=None))
    assert sink.units_for(run_id) == []


def test_raw_is_the_source_substring_untouched(sink):
    # SPEC Done-means 3: "A document saying `U Chicago` keeps that exact wording."
    sink.write(run_it())
    found = [o for o in sink.observations if o["raw_value"] == "U Chicago"]
    assert len(found) == 1
    assert found[0]["normalized_value"] == "U Chicago"


def test_the_same_content_produces_the_same_observations(sink):
    # P4 conformance rule 8 / §8.5's replay diff.
    first, second = sink.write(run_it()), sink.write(run_it())
    strip = lambda rows: [{k: v for k, v in r.items() if k != "run_id"} for r in rows]
    assert strip(sink.observations_for(first)) == strip(sink.observations_for(second))


def test_a_source_type_from_the_other_half_of_e3_is_refused():
    with pytest.raises(WrongFamily):
        run_it(source_type="email")


def test_no_extractor_is_reachable_inside_a_protected_container():
    policy = SafetyPolicy(is_protected_container=lambda path: True,
                          is_dataless=lambda path: False)
    with pytest.raises(ProtectedContainerRefused):
        extract_structured_text(
            file_row=FILE_ROW, path=Path("/Applications/Thing.app/Contents/README.md"),
            policy=policy, source_type="text_document",
            read_text_document=lambda path: pytest.fail("the reader was reached"),
            find_structured_strings=lambda text: (), now=FIXED_CLOCK,
            context_window=20)


def test_a_dataless_file_is_never_read():
    policy = SafetyPolicy(is_protected_container=lambda path: False,
                          is_dataless=lambda path: True)
    with pytest.raises(DatalessRefused):
        extract_structured_text(
            file_row=FILE_ROW, path=Path("/corpus/README.md"), policy=policy,
            source_type="text_document",
            read_text_document=lambda path: pytest.fail("the reader was reached"),
            find_structured_strings=lambda text: (), now=FIXED_CLOCK,
            context_window=20)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_structured_text.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'extractors.structured_text'`

- [ ] **Step 3: Write the implementation**

```python
# src/extractors/structured_text.py
"""E3 - structured text and code (section 2.4).

"Text-bearing files such as Markdown, plain text, JSON, CSV, source code, notebooks,
and configuration files should be handled through a lighter structured-text
extractor. The engine should store their text, filename, extension, language where
relevant, headings, and structural indicators such as repository markers, package
manifests, notebook metadata, and README files."

Filename and extension are NOT emitted here. They are P3's section 1.2 record and O5
gives them to the `filesystem` run, which is what makes a filename citable evidence;
a second emission would be two homes for one value.

Section 2.4's two outcomes, and the third it forbids:

    reader returns a document      -> `complete`, even with zero observations
    reader returns None            -> `unsupported`; no extractor exists for this
                                      format in this deployment

"The system should never silently treat an unsupported format as an empty document,
because an empty extraction result is different from an extractor that does not yet
exist."

E3 reads no code. Section 2.4 requires code files to "rely heavily on local
structural evidence ... rather than forcing semantic analysis to infer a project from
arbitrary code text", so there is no import parser and no project inference here: the
reader reports markers, the injected finder reports strings, and P5 places them.
"""
from __future__ import annotations

from dataclasses import dataclass
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

#: One family name for both halves of E3: the router dispatches eight `source_type`s
#: here and `runs.ANALYSIS_TIER_BY_EXTRACTOR` keys the tier on the family.
EXTRACTOR_NAME = "text.structured"
ANALYSIS_TIER = "native"

#: Section 2.4's own families, in P4's `source_type` vocabulary. The remaining six the
#: router sends to `text.structured` are section 2.9's and live in long_tail.py.
STRUCTURED_TEXT_SOURCE_TYPES: tuple[str, ...] = ("text_document", "code_structured")

#: Section 2.4's four classes of "structural indicators", in section 2.4's words.
#: WHICH FILES ARE MEMBERS of each class is Deferred - the SPEC's Deferred table says
#: section 1.1's four are P3's and "Everything else" is unsettled - so no member name
#: appears in this module and the reader supplies them.
STRUCTURAL_MARKER_KINDS: tuple[str, ...] = (
    "repository marker", "package manifest", "notebook metadata", "README file",
)

#: The slot section 2.4's "language where relevant" occupies. The VALUE is the
#: reader's; P5 detects no language and holds no language list.
LANGUAGE_FIELD = "language"


class WrongFamily(Exception):
    """A `source_type` this half of E3 does not handle."""


class UnknownMarkerKind(Exception):
    """A structural-indicator class section 2.4 does not name."""


@dataclass(frozen=True)
class StructuralMarker:
    """One of section 2.4's structural indicators, as the reader found it.

    `kind` is one of section 2.4's four classes; `value` is the marker itself - a
    file name, a manifest name, a notebook metadata key - verbatim.
    """
    kind: str
    value: str


@dataclass(frozen=True)
class TextDocument:
    """What an injected `read_text_document` returns, or None when this deployment
    ships no reader for the format (section 2.4's `unsupported` outcome)."""
    text: str
    language: str | None = None
    headings: tuple[Region, ...] = ()
    markers: tuple[StructuralMarker, ...] = ()


def unsupported_result(*, file_row: Mapping[str, Any], source_type: str,
                       now: str) -> ExtractionResult:
    """Section 2.4's second outcome: no extractor exists for this format yet.

    Zero observations and zero text units, and a `completeness` a query can tell
    apart from a `complete` run that found nothing (SPEC Done-means 1).
    """
    return ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
                source_type=source_type, analysis_tier=ANALYSIS_TIER, config={},
                completeness="unsupported", coverage=coverage("files", 0, 1),
                observation_count=0, started_at=now, finished_at=now))


def extract_structured_text(
        *, file_row: Mapping[str, Any], path: Path, policy: SafetyPolicy,
        source_type: str,
        read_text_document: Callable[[Path], TextDocument | None],
        find_structured_strings: Callable[[str], tuple[StructuredString, ...]],
        now: str, context_window: int) -> ExtractionResult:
    """Section 2.4's lighter structured-text extractor, as P4 records."""
    if source_type not in STRUCTURED_TEXT_SOURCE_TYPES:
        raise WrongFamily(
            f"{source_type!r} is one of section 2.9's long-tail families; E3 handles "
            f"it in long_tail.py. This half handles {STRUCTURED_TEXT_SOURCE_TYPES}."
        )
    admit(path, policy=policy)
    document = read_text_document(path)
    if document is None:
        return unsupported_result(file_row=file_row, source_type=source_type, now=now)

    observations: list[Mapping[str, Any]] = []
    units: list[Mapping[str, Any]] = [text_unit(text=document.text)]

    def emit(*, zone, raw, container_path, span, unit_text, reliability):
        before = after = ""
        truncated = False
        if span is not None and unit_text is not None:
            before, after, truncated = context_for(unit_text, span["start"],
                                                   span["end"], window=context_window)
        observations.append(observation(
            file_id=file_row["file_id"], content_hash=file_row["content_hash"],
            extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
            source_type=source_type, raw_value=raw,
            normalized_value=normalize_mechanical(raw),
            location=location(zone=zone, container_path=container_path,
                              text_span=span),
            context_before=before, context_after=after, context_truncated=truncated,
            observed_at=now, reliability=reliability,
        ))

    if document.language:
        emit(zone="metadata", raw=document.language,
             container_path=(segment("field", label=LANGUAGE_FIELD),), span=None,
             unit_text=None, reliability="direct")

    for marker in document.markers:
        if marker.kind not in STRUCTURAL_MARKER_KINDS:
            raise UnknownMarkerKind(
                f"{marker.kind!r} is not one of section 2.4's four structural-"
                f"indicator classes {STRUCTURAL_MARKER_KINDS}"
            )
        emit(zone="metadata", raw=marker.value,
             container_path=(segment("field", label=marker.kind),), span=None,
             unit_text=None, reliability="direct")

    heading_paths: dict[int, tuple] = {}
    for region in document.headings:
        heading_path = (segment("heading", index=region.ordinal, label=region.label),)
        heading_paths[region.start] = heading_path
        heading_text = document.text[region.start:region.end]
        units.append(text_unit(text=heading_text, container_path=heading_path))
        emit(zone="heading", raw=heading_text, container_path=heading_path,
             span={"start": 0, "end": len(heading_text)}, unit_text=heading_text,
             reliability="possible")

    for found in find_structured_strings(document.text):
        inside = next((r for r in document.headings
                       if r.start <= found.start < r.end), None)
        if inside is not None:
            container = heading_paths[inside.start]
            unit_text = document.text[inside.start:inside.end]
            start, end = found.start - inside.start, found.end - inside.start
            zone = ZONE_BY_STRUCTURED_KIND.get(found.kind, "heading")
        else:
            container = ()
            unit_text = document.text
            start, end = found.start, found.end
            zone = ZONE_BY_STRUCTURED_KIND.get(found.kind, "body")
        emit(zone=zone, raw=unit_text[start:end], container_path=container,
             span={"start": start, "end": end}, unit_text=unit_text,
             reliability="possible")

    return ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
                source_type=source_type, analysis_tier=ANALYSIS_TIER,
                config={"reader": "injected"}, completeness="complete",
                coverage=coverage("files", 1, 1),
                observation_count=len(observations), started_at=now, finished_at=now),
        observations=tuple(observations),
        text_units=tuple(units),
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p5/test_p5_structured_text.py -v`
Expected: PASS — 14 passed

- [ ] **Step 5: Commit**

```bash
git add src/extractors/structured_text.py tests/p5/test_p5_structured_text.py
git commit -m "feat(P5): E3 structured text - one whole-file unit, unsupported never an empty document"
```

---

### Task 11: E3's §2.9 long-tail families, and the sensitivity signal P5 supplies but does not classify

**Files:**
- Create: `src/extractors/long_tail.py`
- Modify: `src/extractors/schema.py`
- Test: `tests/p5/test_p5_long_tail.py`

**Interfaces:**
- Consumes: `extractors.shape`, `extractors.reading`, `extractors.safety.admit`, `extractors.runs.coverage`, `extractors.structured_text.unsupported_result`; caller-supplied `read_long_tail(path, *, transcribe) -> LongTailFile | None`, `find_structured_strings`, `transcription_authorized()`.
- Produces: `LONG_TAIL_SOURCE_TYPES`, `POTENTIALLY_SENSITIVE`, `SENSITIVE_EMAIL_ZONES`, `SENSITIVE_EMAIL_VALUE_KINDS`, `LongTailEntry`, `LongTailValue`, `LongTailText`, `LongTailFile`, `SensitivitySignal`, `LongTailResult`, `UnauthorizedTranscription`, `DuplicateUnit`, `extract_long_tail()`, `SENSITIVITY_DDL`, `record_sensitivity_signals()`, `sensitivity_signals_for()`.

**The six families §2.9 routes to E3, and where each field lands.** §2.9's field lists are the
requirement; P4's records are the homes. Nothing below is a new field.

| §2.9 family | §2.9's fields | home |
|---|---|---|
| Spreadsheets | workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, dates or identifiers from labeled cells | metadata → `field=` observations; sheet names → `sheet=N` segments **and** their labels; cell values → `table` zone at `sheet=N/row=R/column=C`, the column header carried as the `column` segment's descriptive label |
| Presentations | slide titles, text boxes, speaker notes where available, hyperlinks, embedded tables, slide-level page boundaries | `slide=N` is the page boundary; title → zone `heading`; text box → zone `body`; notes → zone `notes`; hyperlinks → zone `link`; embedded tables → zone `table` |
| Email | sender, recipients, subject, sent date, thread identifiers, message body, attachment names, reply-chain context | every named slot → `field=<slot>` at zone `metadata`; body → zone `body`; **addresses and message content carry the sensitivity signal** |
| Calendar | event title, start and end time, location, organizer, attendees, recurrence metadata | `entry=<uid>` per event, each field a `field=` slot |
| Contacts | names, organizations, email addresses, phone numbers, address-book metadata | `entry=<uid>` per card; **all VCF output carries the sensitivity signal** |
| Audio and video | duration, container and codec metadata, creation time, embedded tags, subtitles or captions where present; speech-to-text transcripts **only under an explicit privacy and compute policy** | metadata → `field=` slots; captions and transcripts → zone `transcript` with a `time_span` |

**One extractor family, two modules.** `EXTRACTOR_NAME` here is `text.structured`, the same value
Task 10 publishes, because the SPEC has one E3 and `runs.ANALYSIS_TIER_BY_EXTRACTOR` keys the tier on
the family. The test below asserts the two halves **partition** the router's `text.structured` set
exactly: no `source_type` reaches both and none reaches neither.

**Transcription is authorized by P7 or it does not happen.** §2.9: speech-to-text transcripts *"only
under an explicit privacy and compute policy"*, and the SPEC: *"Absent that policy, audio/video
extraction stops at container metadata."* So `transcription_authorized` is an **injected predicate with
no default** — P7 does not exist yet and a default would be P5 answering P7's question — and its answer
is passed to the reader as `transcribe=`, so that **no speech recognition is performed at all** when
the policy is absent. A reader that returns a speech-derived text anyway raises
`UnauthorizedTranscription`: a library may not smuggle a transcript past a policy P5 was told to
enforce. Embedded subtitles and captions are *not* speech-to-text — §2.9 lists them in the
unconditional half — and are extracted either way.

**The sensitivity signal is a signal, and P5 classifies nothing.** §2.9 requires email addresses,
message content and VCF output be *treated as potentially sensitive*; §8.4 puts **handling-class
assignment in P7**, and the boundary between the two is **SPEC Open question 7**. P5's side of that
line: one value, `POTENTIALLY_SENSITIVE`, and no vocabulary — no class, no level, no policy, no
redaction. `handling_class` and `sensitivity_state` are names P4's conformance rule 6 already forbids
on an observation and Task 20 asserts appear nowhere in `src/extractors/`.

**Why the signal is a P5 table and not a field.** P4's rule 6 forbids an extractor-private field on an
observation, so the signal cannot ride on the record; and it is *per located value*, so it cannot ride
on the run. It is therefore P5's second table — the one the architecture line names — keyed by
`(run_id, observation_key)` — **P4's handle, since 2026-08-20.** The batch position is still how a
signal is *carried* (it is the only handle at emit time; P4 assigns keys at write time), but it is not
how one is *stored*: `record_sensitivity_signals` takes P4's assigned keys and requires them with no
default. A position would not survive a re-run and P7 could not redact against it. The seam gap that
forced position-keying is closed by P4 publishing `observation_keys_for_run(conn, run_id)` — P5 still
grows no locator implementation of its own.

**Text units must be uniquely addressed, and the reader is what makes them so.** `text_units` is keyed
by `(run_id, container_path)` (G1), and a slide holds a title, text boxes and speaker notes at one
`slide=N`. The reader supplies a `region` ordinal for anything that is not a spreadsheet cell, and
`DuplicateUnit` fires if two texts still collide — G1's key is enforced at the boundary rather than
assumed.

**`unsupported` is shared with Task 10.** A reader returning `None` for a spreadsheet or presentation
still produces §2.4's *"marked clearly as unsupported"* run — the mechanism is unchanged and P5 still
names no library. But **SPEC Open question 5 is CLOSED (B6, 2026-08-20): both ship at launch**, so a
`None` reader in a v1 deployment is now a wiring defect rather than an exercised option.

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_long_tail.py
"""E3's §2.9 half: six families, one shape, and SPEC Open questions 5 and 7 held
open."""
from pathlib import Path

import pytest

from database_agent.db import create_schema

from extractors.long_tail import (
    LONG_TAIL_SOURCE_TYPES, LongTailEntry, LongTailFile, LongTailText, LongTailValue,
    POTENTIALLY_SENSITIVE, UnauthorizedTranscription, DuplicateUnit,
    extract_long_tail, record_sensitivity_signals, sensitivity_signals_for,
)
from extractors.reading import StructuredString
from extractors.router import HANDLER_BY_SOURCE_TYPE
from extractors.safety import ProtectedContainerRefused, SafetyPolicy
from extractors.schema import create_extraction_schema
from extractors.structured_text import STRUCTURED_TEXT_SOURCE_TYPES

from conftest import FIXED_CLOCK
from p4_stub import locator_for, unit_locator_for

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
FILE_ROW = {"file_id": "f-lt", "content_hash": "sha256:lt", "filename": "thing"}

NEVER = lambda: False
ALWAYS = lambda: True


def run_it(document, source_type, *, authorized=NEVER, finder=lambda text: ()):
    seen = {}

    def reader(path, *, transcribe):
        seen["transcribe"] = transcribe
        return document

    result = extract_long_tail(
        file_row=FILE_ROW, path=Path("/corpus/thing"), policy=OPEN_POLICY,
        source_type=source_type, read_long_tail=reader,
        find_structured_strings=finder, transcription_authorized=authorized,
        now=FIXED_CLOCK, context_window=20)
    return result, seen


def a_workbook() -> LongTailFile:
    return LongTailFile(
        entries=(LongTailEntry(kind="sheet", index=1, label="Applications"),),
        values=(LongTailValue(name="creator", value="Numbers"),),
        texts=(LongTailText(zone="table", text="Wash U", entry_ordinal=1, row=2,
                            column=1, column_header="Institution"),),
    )


def a_deck() -> LongTailFile:
    return LongTailFile(
        entries=(LongTailEntry(kind="slide", index=3, label=None),),
        texts=(LongTailText(zone="heading", text="Results", entry_ordinal=1, region=1),
               LongTailText(zone="body", text="Two cohorts.", entry_ordinal=1,
                            region=2),
               LongTailText(zone="notes", text="Mention the funding.",
                            entry_ordinal=1, region=3)),
    )


def an_email() -> LongTailFile:
    return LongTailFile(
        entries=(LongTailEntry(kind="entry", label="<msg-1@example.edu>"),),
        values=(LongTailValue(name="From", value="dean@wustl.edu",
                              entry_ordinal=1, kind="address"),
                LongTailValue(name="Subject", value="Your application",
                              entry_ordinal=1)),
        texts=(LongTailText(zone="body", text="Please send your transcript.",
                            entry_ordinal=1, region=1),),
    )


def a_video(*, with_speech: bool) -> LongTailFile:
    texts = [LongTailText(zone="transcript", text="[music]", region=1,
                          time_span={"start_ms": 0, "end_ms": 2000})]
    if with_speech:
        texts.append(LongTailText(zone="transcript", text="Welcome to the lecture.",
                                  region=2, from_speech=True,
                                  time_span={"start_ms": 2000, "end_ms": 6000}))
    return LongTailFile(values=(LongTailValue(name="duration", value="00:41:12"),),
                        texts=tuple(texts))


def find_lecture(text: str):
    at = text.find("lecture")
    return (StructuredString(kind="identifier", start=at, end=at + 7),) if at != -1 else ()


def test_the_two_halves_of_e3_partition_the_routers_set():
    routed = {name for name, handler in HANDLER_BY_SOURCE_TYPE.items()
              if handler == "text.structured"}
    assert set(STRUCTURED_TEXT_SOURCE_TYPES) | set(LONG_TAIL_SOURCE_TYPES) == routed
    assert not set(STRUCTURED_TEXT_SOURCE_TYPES) & set(LONG_TAIL_SOURCE_TYPES)


def test_every_family_conforms_to_p4s_shape(sink):
    for document, source_type in ((a_workbook(), "spreadsheet"),
                                  (a_deck(), "presentation"),
                                  (an_email(), "email"),
                                  (a_video(with_speech=False), "audio_video")):
        result, _ = run_it(document, source_type)
        sink.write(result.extraction)
    sink.conforms()


def test_a_spreadsheet_cell_locates_by_sheet_row_and_column(sink):
    result, _ = run_it(a_workbook(), "spreadsheet")
    run_id = sink.write(result.extraction)
    cell = [o for o in sink.observations_for(run_id) if o["raw_value"] == "Wash U"][0]
    assert locator_for(cell["location"]) == "table:sheet=1/row=2/column=1#0-6"
    header = cell["location"]["container_path"][-1]["label"]
    assert header == "Institution"


def test_a_slide_keeps_its_title_body_and_notes_as_three_zones(sink):
    result, _ = run_it(a_deck(), "presentation")
    run_id = sink.write(result.extraction)
    zones = {o["raw_value"]: o["location"]["zone"]
             for o in sink.observations_for(run_id)}
    assert zones["Results"] == "heading"
    assert zones["Mention the funding."] == "notes"
    # §2.9's "slide-level page boundaries" are the slide segment itself.
    assert all(o["location"]["container_path"][0] == {"kind": "slide", "index": 3,
                                                      "label": None}
               for o in sink.observations_for(run_id))


def test_a_slides_three_texts_are_three_units(sink):
    result, _ = run_it(a_deck(), "presentation")
    run_id = sink.write(result.extraction)
    paths = [unit_locator_for(u["container_path"]) for u in sink.units_for(run_id)]
    assert len(paths) == len(set(paths)) == 3
    assert set(paths) == {"slide=3/region=1", "slide=3/region=2", "slide=3/region=3"}


def test_two_texts_at_one_container_path_are_refused():
    # G1's key is (run_id, container_path); a collision would silently lose a unit.
    collide = LongTailFile(
        entries=(LongTailEntry(kind="slide", index=1),),
        texts=(LongTailText(zone="body", text="a", entry_ordinal=1),
               LongTailText(zone="notes", text="b", entry_ordinal=1)))
    with pytest.raises(DuplicateUnit):
        run_it(collide, "presentation")


def test_a_message_body_is_a_unit_and_not_an_observation(sink):
    # G1: "a page of text is not a located value". The same is true of a body.
    result, _ = run_it(an_email(), "email")
    run_id = sink.write(result.extraction)
    body = [u for u in sink.units_for(run_id)
            if u["text"] == "Please send your transcript."]
    assert len(body) == 1
    assert not [o for o in sink.observations_for(run_id)
                if o["raw_value"] == "Please send your transcript."]


def test_email_addresses_and_message_content_carry_the_sensitivity_signal(sink):
    result, _ = run_it(an_email(), "email",
                       finder=lambda text: ())
    run_id = sink.write(result.extraction)
    flagged = {result.extraction.observations[s.observation_index]["raw_value"]
               for s in result.sensitivity}
    assert flagged == {"dean@wustl.edu"}
    assert {s.signal for s in result.sensitivity} == {POTENTIALLY_SENSITIVE}
    # The subject is neither an address nor message content, so it carries nothing.
    assert "Your application" not in flagged


def test_every_vcf_value_carries_the_signal():
    card = LongTailFile(
        entries=(LongTailEntry(kind="entry", label="uid-1"),),
        values=(LongTailValue(name="FN", value="A. Dean", entry_ordinal=1),
                LongTailValue(name="TEL", value="+1-314-555-0100", entry_ordinal=1)))
    result, _ = run_it(card, "contacts")
    assert len(result.sensitivity) == len(result.extraction.observations) == 2


def test_p5_supplies_the_signal_and_assigns_no_class():
    # SPEC Open question 7 stays open: §8.4 puts handling-class assignment in P7.
    result, _ = run_it(an_email(), "email")
    assert all(s.signal == POTENTIALLY_SENSITIVE for s in result.sensitivity)
    assert all(not hasattr(s, "handling_class") for s in result.sensitivity)


def test_the_signal_is_stored_and_read_back(conn):
    create_schema(conn)
    create_extraction_schema(conn)
    result, _ = run_it(an_email(), "email")
    keys = [f"k{i}" for i in range(len(result.extraction.observations))]
    record_sensitivity_signals(conn, run_id="run-1", signals=result.sensitivity,
                               observation_keys=keys, now=FIXED_CLOCK)
    rows = sensitivity_signals_for(conn, "run-1")
    assert [r["signal"] for r in rows] == [POTENTIALLY_SENSITIVE]
    assert rows[0]["basis"]
    # keyed on P4's handle, which is what P7 redacts against and what survives a re-run
    assert rows[0]["observation_key"] in keys


def test_audio_stops_at_container_metadata_without_the_policy(sink):
    result, seen = run_it(a_video(with_speech=False), "audio_video",
                          authorized=NEVER)
    run_id = sink.write(result.extraction)
    assert seen["transcribe"] is False          # no recognition was even attempted
    assert [o["raw_value"] for o in sink.observations_for(run_id)] == ["00:41:12"]
    # Embedded captions are §2.9's unconditional half and are still extracted.
    assert [u["text"] for u in sink.units_for(run_id)] == ["[music]"]


def test_a_transcript_smuggled_past_the_policy_is_refused():
    with pytest.raises(UnauthorizedTranscription):
        run_it(a_video(with_speech=True), "audio_video", authorized=NEVER)


def test_an_authorized_transcript_locates_by_time_span(sink):
    result, seen = run_it(a_video(with_speech=True), "audio_video", authorized=ALWAYS,
                          finder=find_lecture)
    run_id = sink.write(result.extraction)
    assert seen["transcribe"] is True
    spoken = [o for o in sink.observations_for(run_id) if o["raw_value"] == "lecture"]
    assert spoken[0]["location"]["zone"] == "transcript"
    assert spoken[0]["location"]["time_span"] == {"start_ms": 2000, "end_ms": 6000}
    assert spoken[0]["location"]["text_span"] is None
    assert spoken[0]["context_before"]        # the offset still produced the context
    sink.conforms()


def test_a_spreadsheet_with_no_reader_is_unsupported(sink):
    # SPEC Open question 5: ship dedicated support, or ship `unsupported`. The
    # caller decides by supplying a reader or not; P5 decides nothing.
    result, _ = run_it(None, "spreadsheet")
    run_id = sink.write(result.extraction)
    assert sink.run_for(run_id)["completeness"] == "unsupported"
    assert sink.observations_for(run_id) == []
    assert result.sensitivity == ()


def test_no_extractor_is_reachable_inside_a_protected_container():
    policy = SafetyPolicy(is_protected_container=lambda path: True,
                          is_dataless=lambda path: False)
    with pytest.raises(ProtectedContainerRefused):
        extract_long_tail(
            file_row=FILE_ROW, path=Path("/Applications/Mail.app/Contents/a.eml"),
            policy=policy, source_type="email",
            read_long_tail=lambda path, *, transcribe: pytest.fail("reader reached"),
            find_structured_strings=lambda text: (),
            transcription_authorized=NEVER, now=FIXED_CLOCK, context_window=20)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_long_tail.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'extractors.long_tail'`

- [ ] **Step 3: Write the implementation**

```python
# src/extractors/long_tail.py
"""E3's section 2.9 half - the six long-tail families, and the sensitivity signal.

Section 2.9 gives spreadsheets, presentations, email, calendar, contacts and
audio/video a field list each and no record of their own; P4's three records are the
homes and this module is the placement. `EXTRACTOR_NAME` is `text.structured`, the
same family Task 10 publishes, because the SPEC has one E3.

Two things here are policy, not format:

  Speech-to-text runs only under P7's explicit privacy and compute policy (section
  2.9). The authorization is an injected predicate with no default and is passed to
  the reader, so absent the policy no recognition is performed at all. Embedded
  subtitles and captions are section 2.9's unconditional half and are not
  speech-to-text.

  Email addresses, message content and every VCF value are marked POTENTIALLY
  SENSITIVE at emission, for P7 to act on. P5 assigns no handling class: section 8.4
  gives classification to P7 and SPEC Open question 7 is exactly where the line
  falls. There is one signal value here and no vocabulary.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from extractors.reading import ZONE_BY_STRUCTURED_KIND, StructuredString
from extractors.runs import coverage
from extractors.safety import SafetyPolicy, admit
from extractors.shape import (
    context_for, location, normalize_mechanical, observation, run, segment, text_unit,
)
from extractors.sink import ExtractionResult
from extractors.structured_text import (
    ANALYSIS_TIER, EXTRACTOR_NAME, VERSION, unsupported_result,
)

#: Section 2.9's six long-tail families, in P4's `source_type` vocabulary. Together
#: with structured_text.STRUCTURED_TEXT_SOURCE_TYPES they partition the eight the
#: router sends to `text.structured`.
LONG_TAIL_SOURCE_TYPES: tuple[str, ...] = (
    "spreadsheet", "presentation", "email", "calendar", "contacts", "audio_video",
)

#: Section 2.9's own phrase, and the WHOLE of P5's sensitivity vocabulary. A class, a
#: level or a policy would be P7's (section 8.4); SPEC Open question 7 is the line.
POTENTIALLY_SENSITIVE = "potentially sensitive"

#: Section 2.9, Email: "while treating addresses and message content as potentially
#: sensitive". Message content is the body; a found address in it is zone `link`.
SENSITIVE_EMAIL_ZONES: tuple[str, ...] = ("body", "link")

#: The value classes section 2.9 names as sensitive in an email header. WHICH SLOTS
#: hold an address is format knowledge (RFC 5322 address fields), so the reader says
#: so and P5 does not pattern-match a header name.
SENSITIVE_EMAIL_VALUE_KINDS: tuple[str, ...] = ("address",)

#: Section 2.9, Contacts: "normally privacy-protected rather than used to create
#: folder proposals" - every value of a VCF, with no exception to enumerate.
FULLY_SENSITIVE_SOURCE_TYPES: tuple[str, ...] = ("contacts",)


class UnauthorizedTranscription(Exception):
    """A speech-derived text arrived without P7's explicit policy (section 2.9)."""


class DuplicateUnit(Exception):
    """Two texts claimed one `(run_id, container_path)` key (G1)."""


@dataclass(frozen=True)
class LongTailEntry:
    """One addressable place: a sheet, a slide, a message, an event, a card.

    `kind` is a P4 segment kind. `sheet` and `slide` are indexed; `entry` is
    label-addressed (P4 segment-kind rule 2) and carries the format's own identifier.
    """
    kind: str
    index: int | None = None
    label: str | None = None


@dataclass(frozen=True)
class LongTailValue:
    """One named value from a family's section 2.9 field list.

    `name` is the format's own slot name, verbatim (P4 D7). `kind` is set only where
    section 2.9 names a class P5 must act on - `address` for an email header.
    """
    name: str
    value: str
    entry_ordinal: int | None = None
    kind: str | None = None


@dataclass(frozen=True)
class LongTailText:
    """One stretch of text: a cell, a text box, a body, a note, a caption.

    `region` makes the container path unique where an entry holds several texts; a
    cell uses `row`/`column` instead. `from_speech` marks section 2.9's speech-to-text
    transcript, which no reader may return unless P7 authorized it.
    """
    zone: str
    text: str
    entry_ordinal: int | None = None
    row: int | None = None
    column: int | None = None
    column_header: str | None = None
    region: int | None = None
    time_span: Mapping[str, int] | None = None
    from_speech: bool = False


@dataclass(frozen=True)
class LongTailFile:
    """What an injected `read_long_tail` returns, or None when this deployment ships
    no reader for the format (section 2.4's `unsupported`)."""
    entries: tuple[LongTailEntry, ...] = ()
    values: tuple[LongTailValue, ...] = ()
    texts: tuple[LongTailText, ...] = ()
    iso_dates: Mapping[str, str] = dataclass_field(default_factory=dict)


@dataclass(frozen=True)
class SensitivitySignal:
    """One located value section 2.9 says to treat as potentially sensitive.

    `observation_index` is the observation's position in the batch, which is the only
    handle that exists at EMIT time -- P4 assigns `observation_key` at write time. The
    index is therefore how a signal is carried, not how it is stored: at write time
    `record_sensitivity_signals` takes P4's assigned keys and the row is keyed on
    `observation_key`, which is what survives a re-run and what P7 can redact against.
    The seam gap that forced position-keying is closed: P4 publishes
    `observation_keys_for_run(conn, run_id)`.
    """
    observation_index: int
    signal: str
    basis: str


@dataclass(frozen=True)
class LongTailResult:
    """The P4 batch, and the signals raised while building it.

    Two values rather than one because P4 conformance rule 6 forbids an
    extractor-private field on an observation, and the signal is per located value so
    it cannot ride on the run either.
    """
    extraction: ExtractionResult
    sensitivity: tuple[SensitivitySignal, ...] = ()


def _entry_segment(entry: LongTailEntry) -> dict:
    return segment(entry.kind, index=entry.index, label=entry.label)


def _entry_path(document: LongTailFile, ordinal: int | None) -> tuple:
    if ordinal is None:
        return ()
    return (_entry_segment(document.entries[ordinal - 1]),)


def _path_key(container_path: tuple) -> tuple:
    """A hashable form of a container path. Segments are P4 mappings, so the key is
    built rather than assumed - G1's uniqueness check needs one and P5 owns no
    locator serialization to borrow."""
    return tuple((s["kind"], s["index"], s["label"]) for s in container_path)


def _text_path(document: LongTailFile, text: LongTailText) -> tuple:
    path = _entry_path(document, text.entry_ordinal)
    if text.row is not None:
        path = path + (segment("row", index=text.row),
                       segment("column", index=text.column,
                               label=text.column_header))
    if text.region is not None:
        path = path + (segment("region", index=text.region),)
    return path


#: Zones whose whole text is itself a located value. A heading, a note and a cell are
#: short labelled positions (sections 2.3 and 2.9); a body and a transcript are bulk
#: text and G1 gives bulk text to `text_units`.
WHOLE_TEXT_ZONES: tuple[str, ...] = ("heading", "notes", "table")


def extract_long_tail(
        *, file_row: Mapping[str, Any], path: Path, policy: SafetyPolicy,
        source_type: str,
        read_long_tail: Callable[..., LongTailFile | None],
        find_structured_strings: Callable[[str], tuple[StructuredString, ...]],
        transcription_authorized: Callable[[], bool],
        now: str, context_window: int) -> LongTailResult:
    """Section 2.9's long-tail families, as P4 records."""
    if source_type not in LONG_TAIL_SOURCE_TYPES:
        raise ValueError(
            f"{source_type!r} is not one of section 2.9's long-tail families "
            f"{LONG_TAIL_SOURCE_TYPES}"
        )
    admit(path, policy=policy)
    transcribe = bool(transcription_authorized())
    document = read_long_tail(path, transcribe=transcribe)
    if document is None:
        return LongTailResult(
            extraction=unsupported_result(file_row=file_row,
                                          source_type=source_type, now=now))

    iso_dates = document.iso_dates
    observations: list[Mapping[str, Any]] = []
    units: list[Mapping[str, Any]] = []
    signals: list[SensitivitySignal] = []

    def emit(*, zone, raw, container_path, span, unit_text, reliability,
             normalized=None, sensitive_basis=None, time_span=None):
        before = after = ""
        truncated = False
        if span is not None and unit_text is not None:
            before, after, truncated = context_for(unit_text, span["start"],
                                                   span["end"], window=context_window)
        # A time-addressed medium locates by time: P4's `location` publishes
        # `text_span` and `time_span` as alternatives, and section 2.8's own
        # audio/video example is a time. The offset still produced the context.
        observations.append(observation(
            file_id=file_row["file_id"], content_hash=file_row["content_hash"],
            extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
            source_type=source_type, raw_value=raw,
            normalized_value=normalized if normalized is not None
            else normalize_mechanical(raw),
            location=location(zone=zone, container_path=container_path,
                              text_span=None if time_span is not None else span,
                              time_span=time_span),
            context_before=before, context_after=after, context_truncated=truncated,
            observed_at=now, reliability=reliability,
        ))
        basis = sensitive_basis
        if basis is None and source_type in FULLY_SENSITIVE_SOURCE_TYPES:
            basis = ("section 2.9, Contacts: address-book output is normally "
                     "privacy-protected")
        if basis is not None:
            signals.append(SensitivitySignal(observation_index=len(observations) - 1,
                                             signal=POTENTIALLY_SENSITIVE,
                                             basis=basis))

    for value in document.values:
        if not value.value:
            continue                     # presence only; an absence is never a row
        basis = None
        if (source_type == "email"
                and value.kind in SENSITIVE_EMAIL_VALUE_KINDS):
            basis = "section 2.9, Email: addresses are potentially sensitive"
        emit(zone="metadata", raw=value.value,
             container_path=_entry_path(document, value.entry_ordinal)
             + (segment("field", label=value.name),),
             span=None, unit_text=None, reliability="direct",
             normalized=iso_dates.get(value.name), sensitive_basis=basis)

    seen_paths: set[tuple] = set()
    for text in document.texts:
        if text.from_speech and not transcribe:
            raise UnauthorizedTranscription(
                "a speech-to-text transcript arrived without P7's explicit privacy "
                "and compute policy; section 2.9 authorizes one only under it"
            )
        if not text.text:
            continue
        container = _text_path(document, text)
        if _path_key(container) in seen_paths:
            raise DuplicateUnit(
                f"two texts claim the container path {container!r}; `text_units` is "
                "keyed by (run_id, container_path) (G1) and the second would be lost"
            )
        seen_paths.add(_path_key(container))
        units.append(text_unit(text=text.text, container_path=container))
        body_basis = (
            "section 2.9, Email: message content is potentially sensitive"
            if source_type == "email" and text.zone in SENSITIVE_EMAIL_ZONES
            else None)
        if text.zone in WHOLE_TEXT_ZONES:
            emit(zone=text.zone, raw=text.text, container_path=container,
                 span={"start": 0, "end": len(text.text)}, unit_text=text.text,
                 reliability="possible", sensitive_basis=body_basis)
        for found in find_structured_strings(text.text):
            zone = ZONE_BY_STRUCTURED_KIND.get(found.kind, text.zone)
            found_basis = body_basis
            if (found_basis is None and source_type == "email"
                    and zone in SENSITIVE_EMAIL_ZONES):
                found_basis = ("section 2.9, Email: addresses are potentially "
                               "sensitive")
            emit(zone=zone, raw=text.text[found.start:found.end],
                 container_path=container,
                 span={"start": found.start, "end": found.end},
                 unit_text=text.text, reliability="possible",
                 sensitive_basis=found_basis, time_span=text.time_span)

    entries = len(document.entries) or 1
    return LongTailResult(
        extraction=ExtractionResult(
            run=run(file_id=file_row["file_id"],
                    content_hash=file_row["content_hash"],
                    extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
                    source_type=source_type, analysis_tier=ANALYSIS_TIER,
                    config={"reader": "injected", "transcribe": transcribe},
                    completeness="complete",
                    coverage=coverage("entries", entries, entries),
                    observation_count=len(observations), started_at=now,
                    finished_at=now),
            observations=tuple(observations),
            text_units=tuple(units)),
        sensitivity=tuple(signals),
    )


SENSITIVITY_DDL = """
CREATE TABLE IF NOT EXISTS extraction_sensitivity_signal (
    signal_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT NOT NULL,
    observation_key TEXT NOT NULL,   -- P4's handle, not a batch position
    signal          TEXT NOT NULL,
    basis           TEXT NOT NULL,
    observed_at     TEXT NOT NULL,
    UNIQUE (run_id, observation_key)
);
"""


def record_sensitivity_signals(conn: sqlite3.Connection, *, run_id: str,
                               signals: Sequence[SensitivitySignal],
                               observation_keys: Sequence[str],
                               now: str) -> int:
    """Persist the signals for one written batch. Returns how many were stored.

    `observation_keys` is P4's assignment for this batch, in emit order --
    `evidence_shape.store.observation_keys_for_run(conn, run_id)`. It is required with
    no default: a default would let a caller store a batch position in a column named
    `observation_key`, which is the two-vocabularies defect wearing the right name.
    """
    for signal in signals:
        if signal.observation_index >= len(observation_keys):
            raise IndexError(
                f"signal at batch position {signal.observation_index} has no key: "
                f"P4 assigned {len(observation_keys)} for run {run_id}")
        conn.execute(
            "INSERT INTO extraction_sensitivity_signal (run_id, observation_key, "
            "signal, basis, observed_at) VALUES (?, ?, ?, ?, ?)",
            (run_id, observation_keys[signal.observation_index],
             signal.signal, signal.basis, now),
        )
    return len(signals)


def sensitivity_signals_for(conn: sqlite3.Connection,
                            run_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM extraction_sensitivity_signal WHERE run_id = ? "
        # signal_id is insertion order, which is emit order: `observation_index`
        # is no longer a column, the row is keyed on P4's `observation_key`.
        "ORDER BY signal_id", (run_id,)).fetchall()
```

**Modify: `src/extractors/schema.py`** — P5's second table joins the first. The architecture line names
two P5-owned tables and this is the second; `create_extraction_schema` stays the one place either is
created, and P4's three tables are still created by nothing in `extractors`.

```python
# src/extractors/schema.py
from extractors.long_tail import SENSITIVITY_DDL
from extractors.router import ROUTING_DDL


def create_extraction_schema(conn: sqlite3.Connection) -> None:
    """Create every P5-owned table. Idempotent. P1's `create_schema` runs first.

    Two tables, both P5's own: the routing decision per file (section 2.9) and the
    sensitivity signal per located value (section 2.9, section 8.4). P4's `evidence`,
    `extraction_runs` and `text_units` are created here never.
    """
    conn.executescript(ROUTING_DDL)
    conn.executescript(SENSITIVITY_DDL)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p5/test_p5_long_tail.py -v`
Expected: PASS — 16 passed

- [ ] **Step 5: Commit**

```bash
git add src/extractors/long_tail.py src/extractors/schema.py tests/p5/test_p5_long_tail.py
git commit -m "feat(P5): E3 long-tail families, transcription only under P7 policy, sensitivity signalled not classified"
```

---

### Task 12: E4 — archives (§2.5), the manifest read with nothing written to disk

**Files:**
- Create: `src/extractors/archive.py`
- Test: `tests/p5/test_p5_archive.py`

**Interfaces:**
- Consumes: `extractors.shape`, `extractors.safety.admit`, `extractors.runs.coverage`; caller-supplied `read_manifest(path) -> ArchiveManifest` and `recognize_markers(member_paths) -> tuple[ArchiveMarker, ...]`.
- Produces: `VERSION`, `EXTRACTOR_NAME`, `ARCHIVE_TYPE_FIELD`, `UNCOMPRESSED_SIZE_FIELD`, `MARKER_KINDS`, `UnknownMarkerKind`, `ArchiveMember`, `ArchiveManifest`, `ArchiveMarker`, `extract_archive()`.

**§2.5, in full, is this task.** *"Archives should be inspected without being unpacked to disk. The
engine should read and store the archive type, contained paths, filenames, folder names, extensions,
file count, uncompressed size where available, and recognizable markers such as source-code manifests or
document names."*

| §2.5 requires | where it lands |
|---|---|
| archive type | observation, zone `metadata`, `field=archive type`, `direct` |
| contained paths · filenames · folder names · extensions | observations at zone `manifest`, container `entry=<member path>`, each a **span of the member path** |
| file count | `run.coverage {units: "entries", processed, total}` — the same rule E1 applies to page count; a second home for one number is the drift this project keeps paying for |
| uncompressed size, where available | observation, zone `metadata`, `field=uncompressed size`, `direct` |
| recognizable markers | observations, zone `metadata`, `field=<§2.5's own class>`, `direct`, value = the member path that carries the marker |

**Four values, one unit, four spans.** §2.5 asks for the path, the filename, the folder names and the
extension, which are one string and four readings of it. Each member's path is stored once as a
`text_units` row at `manifest`/`entry=<path>` and each of the four is an observation with a span into
it, so P4 conformance rules 5 and 10 hold and no character is stored twice. §2.8's *"a path inside an
archive manifest"* is the location, exactly as P4's fixture 6 gives it.

**§2.5's own example is the headline test.** *"A ZIP file named `submission.zip` may contain a
transcript, personal statement, resume, certificate, and form, which is meaningful evidence of a
purpose-defined application packet even when the outer archive name is vague."* Five member names become
five located values; **P5 concludes nothing** from them — "application packet" is a fact and belongs to
P6 (§3.2).

**The absolute prohibition, and how it is tested.** §2.5: *"the normal scan should never extract archive
contents to the filesystem, because doing so creates security, storage, and side-effect risks."* The
test builds a real ZIP under `tmp_path` with the standard library, snapshots the whole tree, runs E4,
and asserts the tree is byte-for-byte unchanged. `src/extractors/archive.py` imports no archive library
at all — the manifest reader is injected — so there is no code path that could unpack one; Task 20
asserts that by introspection.

**A decompression bomb is refused by never decompressing.** §2.5: password-protected, malformed, nested
and oversized archives are *"marked as unreadable or partially inspected rather than forced open or
allowed to become decompression-bomb risks."* In P4's words that is `unreadable` and `partial`.
Uncompressed size is **read from the manifest where the format declares it** and is itself the bomb
signal; it is never established by decompressing, and **P5 holds no size ceiling** — the ceiling is
§8.6 configuration the reader was given (G4), and the reader reports that it stopped.

**`unreadable` still carries rows.** §2.9's *"indexed-but-unreadable rather than silently treated as
empty"* (M3): a password-protected archive still yields its type, and P4's conformance rule 9 lists
`unsupported`, `deferred` and `failed` as the zero-observation states — not `unreadable`.

**SPEC Open question 8 stays open.** *"May a nested archive's manifest be read one level down, in
memory?"* `ArchiveManifest` has no nested-manifest field and `extract_archive` calls `read_manifest`
**exactly once**; an inner archive is one ordinary manifest entry whose path ends in an archive
extension, and nothing recurses. The test asserts the single call.

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_archive.py
"""E4 - §2.5. Done-means 7: "No archive fixture writes a byte outside the process,
and the bomb/protected/nested fixtures all terminate in a marked state."
"""
import zipfile
from pathlib import Path

import pytest

from extractors.archive import (
    ARCHIVE_TYPE_FIELD, ArchiveManifest, ArchiveMarker, ArchiveMember,
    EXTRACTOR_NAME, MARKER_KINDS, UNCOMPRESSED_SIZE_FIELD, UnknownMarkerKind,
    extract_archive,
)
from extractors.safety import DatalessRefused, ProtectedContainerRefused, SafetyPolicy

from conftest import FIXED_CLOCK
from p4_stub import locator_for

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
FILE_ROW = {"file_id": "f-zip", "content_hash": "sha256:zip",
            "filename": "submission.zip"}

PACKET = ("transcript.pdf", "personal-statement.docx", "resume.pdf",
          "certificate.pdf", "form.pdf")


def a_submission_zip() -> ArchiveManifest:
    members = tuple(ArchiveMember(path=name, uncompressed_size=100)
                    for name in PACKET)
    return ArchiveManifest(archive_type="ZIP", members=members,
                           uncompressed_size=500, inspected=len(members),
                           total=len(members))


def no_markers(member_paths):
    return ()


def run_it(manifest=None, markers=no_markers, path=Path("/corpus/submission.zip")):
    calls = []

    def reader(target):
        calls.append(target)
        return manifest if manifest is not None else a_submission_zip()

    result = extract_archive(file_row=FILE_ROW, path=path, policy=OPEN_POLICY,
                             read_manifest=reader, recognize_markers=markers,
                             now=FIXED_CLOCK, context_window=20)
    return result, calls


def test_every_observation_conforms_to_p4s_shape(sink):
    result, _ = run_it()
    sink.write(result)
    sink.conforms()


def test_the_five_member_names_are_five_located_values(sink):
    # §2.5's own example: transcript, personal statement, resume, certificate, form.
    result, _ = run_it()
    run_id = sink.write(result)
    located = {o["raw_value"]: locator_for(o["location"])
               for o in sink.observations_for(run_id)
               if o["location"]["zone"] == "manifest"}
    for name in PACKET:
        assert located[name] == f"manifest:entry={name}#0-{len(name)}"


def test_p5_concludes_nothing_about_the_packet(sink):
    # "Application packet" is a fact (§3.2) and belongs to P6.
    result, _ = run_it()
    run_id = sink.write(result)
    values = " ".join(o["raw_value"] for o in sink.observations_for(run_id))
    assert "packet" not in values and "application" not in values.lower()


def test_the_archive_type_and_uncompressed_size_are_metadata(sink):
    result, _ = run_it()
    run_id = sink.write(result)
    slots = {o["location"]["container_path"][0]["label"]: o["raw_value"]
             for o in sink.observations_for(run_id)
             if o["location"]["zone"] == "metadata"}
    assert slots[ARCHIVE_TYPE_FIELD] == "ZIP"
    assert slots[UNCOMPRESSED_SIZE_FIELD] == "500"


def test_the_file_count_lives_on_coverage_and_nowhere_else(sink):
    result, _ = run_it()
    run_id = sink.write(result)
    assert sink.run_for(run_id)["coverage"] == {"units": "entries", "processed": 5,
                                                "total": 5}
    assert not [o for o in sink.observations_for(run_id)
                if o["raw_value"] == "5"]


def test_folder_names_and_extensions_are_spans_of_the_member_path(sink):
    manifest = ArchiveManifest(
        archive_type="ZIP",
        members=(ArchiveMember(path="project/src/main.py"),
                 ArchiveMember(path="project/src/util.py"),
                 ArchiveMember(path="project/", is_directory=True)),
        inspected=3, total=3)
    result, _ = run_it(manifest=manifest)
    run_id = sink.write(result)
    manifest_rows = {o["raw_value"]: o for o in sink.observations_for(run_id)
                     if o["location"]["zone"] == "manifest"}
    assert set(manifest_rows) == {"project/src/main.py", "project/src/util.py",
                                  "project/", "main.py", "util.py", ".py",
                                  "project", "src"}
    # D10: one row per (zone, raw); `src` appears in two members and counts twice.
    assert manifest_rows["src"]["occurrence_count"] == 2
    assert manifest_rows[".py"]["occurrence_count"] == 2
    # And the span really indexes the member path it names (P4 rule 5).
    sink.conforms()


def test_recognizable_markers_come_from_the_caller_not_from_p5(sink):
    seen = {}

    def recognizer(member_paths):
        seen["paths"] = tuple(member_paths)
        return (ArchiveMarker(member_path="project/package.json",
                              kind="source-code manifest"),)

    manifest = ArchiveManifest(
        archive_type="ZIP",
        members=(ArchiveMember(path="project/package.json"),),
        inspected=1, total=1)
    result, _ = run_it(manifest=manifest, markers=recognizer)
    run_id = sink.write(result)
    assert seen["paths"] == ("project/package.json",)
    marker = [o for o in sink.observations_for(run_id)
              if o["location"]["container_path"]
              and o["location"]["container_path"][0]["label"] in MARKER_KINDS][0]
    assert marker["raw_value"] == "project/package.json"
    assert marker["reliability"] == "direct"


def test_a_marker_class_section_2_5_does_not_name_is_refused():
    manifest = ArchiveManifest(archive_type="ZIP",
                               members=(ArchiveMember(path="a"),),
                               inspected=1, total=1)
    with pytest.raises(UnknownMarkerKind):
        run_it(manifest=manifest,
               markers=lambda paths: (ArchiveMarker(member_path="a",
                                                    kind="vibe"),))


def test_a_real_zip_is_read_and_not_one_byte_is_written(tmp_path, sink):
    # Done-means 7, and §2.5's absolute prohibition. The one test in this file that
    # touches a disk, and it builds its own tree under tmp_path.
    archive_path = tmp_path / "submission.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        for name in PACKET:
            archive.writestr(name, b"fixture bytes")

    def real_reader(target: Path) -> ArchiveManifest:
        with zipfile.ZipFile(target) as opened:
            infos = opened.infolist()
        return ArchiveManifest(
            archive_type="ZIP",
            members=tuple(ArchiveMember(path=i.filename, is_directory=i.is_dir(),
                                        uncompressed_size=i.file_size)
                          for i in infos),
            uncompressed_size=sum(i.file_size for i in infos),
            inspected=len(infos), total=len(infos))

    before = {p: p.stat().st_size for p in sorted(tmp_path.rglob("*"))}
    result = extract_archive(file_row=FILE_ROW, path=archive_path,
                             policy=OPEN_POLICY, read_manifest=real_reader,
                             recognize_markers=no_markers, now=FIXED_CLOCK,
                             context_window=20)
    after = {p: p.stat().st_size for p in sorted(tmp_path.rglob("*"))}

    assert after == before, "E4 wrote to the filesystem"
    run_id = sink.write(result)
    names = {o["raw_value"] for o in sink.observations_for(run_id)}
    assert set(PACKET) <= names
    assert sink.run_for(run_id)["completeness"] == "complete"


def test_a_password_protected_archive_is_unreadable_and_still_indexed(sink):
    # §2.5 + M3: "indexed-but-unreadable, never zero rows".
    manifest = ArchiveManifest(archive_type="ZIP", members=(), inspected=0, total=0,
                               unreadable_reason="password-protected")
    result, _ = run_it(manifest=manifest)
    run_id = sink.write(result)
    row = sink.run_for(run_id)
    assert row["completeness"] == "unreadable"
    assert "password-protected" in row["failure_reason"]
    assert [o["raw_value"] for o in sink.observations_for(run_id)] == ["ZIP"]
    sink.conforms()


def test_a_malformed_archive_is_unreadable_with_its_reason(sink):
    manifest = ArchiveManifest(archive_type="ZIP", members=(), inspected=0, total=0,
                               unreadable_reason="malformed central directory")
    result, _ = run_it(manifest=manifest)
    row = sink.run_for(sink.write(result))
    assert row["completeness"] == "unreadable"


def test_an_oversized_archive_is_partial_and_declares_its_size(sink):
    # The bomb signal is the DECLARED uncompressed size, read from the manifest.
    # P5 holds no ceiling: the reader was given §8.6's and reports that it stopped.
    manifest = ArchiveManifest(
        archive_type="ZIP",
        members=(ArchiveMember(path="huge.bin", uncompressed_size=10 ** 12),),
        uncompressed_size=10 ** 12, inspected=1, total=90000,
        partial_reason="stopped at the configured entry ceiling")
    result, _ = run_it(manifest=manifest)
    run_id = sink.write(result)
    row = sink.run_for(run_id)
    assert row["completeness"] == "partial"
    assert row["coverage"] == {"units": "entries", "processed": 1, "total": 90000}
    sizes = [o["raw_value"] for o in sink.observations_for(run_id)
             if o["location"]["container_path"]
             and o["location"]["container_path"][0]["label"] == UNCOMPRESSED_SIZE_FIELD]
    assert sizes == [str(10 ** 12)]
    sink.conforms()


def test_a_nested_archive_is_one_entry_and_the_manifest_is_read_once(sink):
    # SPEC Open question 8 is OPEN: whether an inner manifest may be read one level
    # down, in memory, is unsettled. E4 reads one manifest and recurses never.
    manifest = ArchiveManifest(
        archive_type="ZIP",
        members=(ArchiveMember(path="inner.zip", uncompressed_size=42),),
        inspected=1, total=2, partial_reason="contains a nested archive")
    result, calls = run_it(manifest=manifest)
    run_id = sink.write(result)
    assert len(calls) == 1
    assert sink.run_for(run_id)["completeness"] == "partial"
    inner = [o for o in sink.observations_for(run_id)
             if o["raw_value"] == "inner.zip"]
    assert inner[0]["location"]["zone"] == "manifest"


def test_the_same_manifest_produces_the_same_observations(sink):
    first = sink.write(run_it()[0])
    second = sink.write(run_it()[0])
    strip = lambda rows: [{k: v for k, v in r.items() if k != "run_id"} for r in rows]
    assert strip(sink.observations_for(first)) == strip(sink.observations_for(second))


def test_no_extractor_is_reachable_inside_a_protected_container():
    policy = SafetyPolicy(is_protected_container=lambda path: True,
                          is_dataless=lambda path: False)
    with pytest.raises(ProtectedContainerRefused):
        extract_archive(file_row=FILE_ROW,
                        path=Path("/Applications/Thing.app/Contents/a.zip"),
                        policy=policy,
                        read_manifest=lambda target: pytest.fail("reader reached"),
                        recognize_markers=no_markers, now=FIXED_CLOCK,
                        context_window=20)


def test_a_dataless_archive_is_never_materialized():
    policy = SafetyPolicy(is_protected_container=lambda path: False,
                          is_dataless=lambda path: True)
    with pytest.raises(DatalessRefused):
        extract_archive(file_row=FILE_ROW, path=Path("/corpus/submission.zip"),
                        policy=policy,
                        read_manifest=lambda target: pytest.fail("reader reached"),
                        recognize_markers=no_markers, now=FIXED_CLOCK,
                        context_window=20)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_archive.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'extractors.archive'`

- [ ] **Step 3: Write the implementation**

```python
# src/extractors/archive.py
"""E4 - archives (section 2.5).

"Archives should be inspected without being unpacked to disk. The engine should read
and store the archive type, contained paths, filenames, folder names, extensions,
file count, uncompressed size where available, and recognizable markers such as
source-code manifests or document names."

This module imports no archive library, opens no file and writes nothing: the
manifest reader is injected, so there is no code path here that could unpack an
archive. That is how "the normal scan should never extract archive contents to the
filesystem" is kept - by absence, not by a flag.

Uncompressed size is read from the manifest where the format declares it, and IS the
decompression-bomb signal. P5 holds no size ceiling: section 8.6's ceilings are
configuration the reader was given (G4), and the reader reports that it stopped.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from extractors.runs import coverage
from extractors.safety import SafetyPolicy, admit
from extractors.shape import (
    context_for, location, normalize_mechanical, observation, run, segment, text_unit,
)
from extractors.sink import ExtractionResult

VERSION = "0.1.0"
EXTRACTOR_NAME = "archive.manifest"
SOURCE_TYPE = "archive"
ANALYSIS_TIER = "native"

#: Section 2.5's own names for the two values that describe the archive itself.
ARCHIVE_TYPE_FIELD = "archive type"
UNCOMPRESSED_SIZE_FIELD = "uncompressed size"

#: Section 2.5's "recognizable markers such as source-code manifests or document
#: names" - the two classes section 2.5 names. WHICH files are markers is Deferred
#: ("Archive recognizable markers beyond the above | The marker set"), so no member
#: name appears here and the recognizer is caller-supplied.
MARKER_KINDS: tuple[str, ...] = ("source-code manifest", "document name")


class UnknownMarkerKind(Exception):
    """A marker class section 2.5 does not name."""


@dataclass(frozen=True)
class ArchiveMember:
    """One manifest entry. `uncompressed_size` is what the manifest DECLARES."""
    path: str
    is_directory: bool = False
    uncompressed_size: int | None = None


@dataclass(frozen=True)
class ArchiveManifest:
    """What an injected `read_manifest` returns.

    `unreadable_reason` is section 2.5's password-protected and malformed cases;
    `partial_reason` is its nested and oversized ones. The reader names the reason
    because the reason is format knowledge; P5 places it.
    """
    archive_type: str
    members: tuple[ArchiveMember, ...] = ()
    uncompressed_size: int | None = None
    inspected: int = 0
    total: int = 0
    unreadable_reason: str | None = None
    partial_reason: str | None = None


@dataclass(frozen=True)
class ArchiveMarker:
    """One of section 2.5's recognizable markers, as the caller recognized it."""
    member_path: str
    kind: str


def _name_spans(path_text: str, *, is_directory: bool) -> list[tuple[int, int]]:
    """Section 2.5's "contained paths, filenames, folder names, extensions" as spans
    of one member path - four readings of one string, so each is a located value and
    no character is stored twice."""
    spans = [(0, len(path_text))]
    parts = path_text.rstrip("/").split("/")
    offset = 0
    for position, part in enumerate(parts):
        start, end = offset, offset + len(part)
        offset = end + 1
        if not part:
            continue
        spans.append((start, end))
        if position == len(parts) - 1 and not is_directory:
            dot = part.rfind(".")
            if dot > 0:
                spans.append((start + dot, end))
    seen, unique = set(), []
    for span in spans:
        if span not in seen:
            seen.add(span)
            unique.append(span)
    return unique


def extract_archive(*, file_row: Mapping[str, Any], path: Path,
                    policy: SafetyPolicy,
                    read_manifest: Callable[[Path], ArchiveManifest],
                    recognize_markers: Callable[[Sequence[str]],
                                                Sequence[ArchiveMarker]],
                    now: str, context_window: int) -> ExtractionResult:
    """Section 2.5's manifest, as P4 records. Reads one manifest and recurses never.

    SPEC Open question 8 - whether a nested archive's manifest may be read one level
    down, in memory - is left open by that: an inner archive is one ordinary entry
    whose path ends in an archive extension, and nothing here looks inside it.
    """
    admit(path, policy=policy)
    manifest = read_manifest(path)

    candidates: list[tuple[str, str, tuple, dict | None, str | None, str]] = []
    units: list[Mapping[str, Any]] = []

    candidates.append(("metadata", manifest.archive_type,
                       (segment("field", label=ARCHIVE_TYPE_FIELD),), None, None,
                       "direct"))
    if manifest.uncompressed_size is not None:
        candidates.append(("metadata", str(manifest.uncompressed_size),
                           (segment("field", label=UNCOMPRESSED_SIZE_FIELD),), None,
                           None, "direct"))

    for member in manifest.members:
        container = (segment("entry", label=member.path),)
        units.append(text_unit(text=member.path, container_path=container))
        for start, end in _name_spans(member.path,
                                      is_directory=member.is_directory):
            candidates.append(("manifest", member.path[start:end], container,
                               {"start": start, "end": end}, member.path,
                               "possible"))

    for marker in recognize_markers([m.path for m in manifest.members]):
        if marker.kind not in MARKER_KINDS:
            raise UnknownMarkerKind(
                f"{marker.kind!r} is not one of section 2.5's marker classes "
                f"{MARKER_KINDS}"
            )
        candidates.append(("metadata", marker.member_path,
                           (segment("field", label=marker.kind),), None, None,
                           "direct"))

    observations = _collapse(candidates, file_row=file_row, now=now,
                             context_window=context_window)

    completeness = "complete"
    failure_reason = None
    if manifest.unreadable_reason:
        # Section 2.9 / M3: indexed-but-unreadable, never zero rows. The archive type
        # is still evidence and P4's rule 9 does not list `unreadable` as a
        # zero-observation state.
        completeness = "unreadable"
        failure_reason = (
            f"{manifest.unreadable_reason}; section 2.5 marks it rather than forcing "
            "it open"
        )
    elif manifest.partial_reason:
        completeness = "partial"

    return ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
                source_type=SOURCE_TYPE, analysis_tier=ANALYSIS_TIER,
                config={"reader": "injected"}, completeness=completeness,
                coverage=coverage("entries", manifest.inspected, manifest.total),
                observation_count=len(observations), started_at=now, finished_at=now,
                failure_reason=failure_reason),
        observations=observations,
        text_units=tuple(units),
    )


def _collapse(candidates, *, file_row: Mapping[str, Any], now: str,
              context_window: int) -> tuple[Mapping[str, Any], ...]:
    """P4 D10: one observation per (run, exact raw value, zone); `location` addresses
    the first occurrence in manifest order. `src` in two member paths is one row with
    an occurrence count of two."""
    first: dict[tuple[str, str], tuple] = {}
    counts: dict[tuple[str, str], int] = {}
    order: list[tuple[str, str]] = []
    for candidate in candidates:
        key = (candidate[0], candidate[1])
        if key not in first:
            first[key] = candidate
            counts[key] = 0
            order.append(key)
        counts[key] += 1

    observations = []
    for key in order:
        zone, raw, container, span, unit_text, reliability = first[key]
        before = after = ""
        truncated = False
        if span is not None and unit_text is not None:
            before, after, truncated = context_for(unit_text, span["start"],
                                                   span["end"], window=context_window)
        observations.append(observation(
            file_id=file_row["file_id"], content_hash=file_row["content_hash"],
            extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
            source_type=SOURCE_TYPE, raw_value=raw,
            normalized_value=normalize_mechanical(raw),
            location=location(zone=zone, container_path=container, text_span=span),
            context_before=before, context_after=after, context_truncated=truncated,
            occurrence_count=counts[key], observed_at=now, reliability=reliability,
        ))
    return tuple(observations)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p5/test_p5_archive.py -v`
Expected: PASS — 16 passed

- [ ] **Step 5: Commit**

```bash
git add src/extractors/archive.py tests/p5/test_p5_archive.py
git commit -m "feat(P5): E4 archives - manifest only, nothing unpacked, bomb signal read never decompressed"
```

---

### Task 13: E5 — images (§2.6), the signal hierarchy exposed and no conclusion drawn

**Files:**
- Create: `src/extractors/image.py`
- Test: `tests/p5/test_p5_image.py`

**Interfaces:**
- Consumes: `extractors.shape`, `extractors.safety.admit`, `extractors.runs.coverage`; caller-supplied `read_image(path) -> ImageRecord`, `dimension_signal(width, height) -> str | None`, `filename_pattern(filename) -> str | None`.
- Produces: `VERSION`, `EXTRACTOR_NAME`, `SIGNAL_TIER`, `DIMENSION_SIGNALS`, `PNG_FORMAT`, `FORMAT_FIELD`, `DIMENSIONS_FIELD`, `PERCEPTUAL_HASH_FIELD`, `FILENAME_PATTERN_FIELD`, `UnknownSignal`, `ExifValue`, `ImageRecord`, `extract_image()`.

**§2.6, in full, is this task.** *"For every supported image, the engine should store its format, pixel
dimensions, file size, color information where useful, content hash, perceptual hash, EXIF camera make
and model, lens data, ISO, focal length, capture time, GPS, orientation, software metadata, filename
pattern, and OCR output where needed."*

| §2.6 requires | where it lands |
|---|---|
| format | observation, zone `metadata`, `field=format`, `direct`; `signal_tier: 3` when it is PNG, because §2.6 names *"PNG format"* as a tier-3 signal |
| pixel dimensions | observation, `field=pixel dimensions`, `direct`; tier from the caller's `dimension_signal` |
| **file size · content hash** | **the `filesystem` run** and P1's `files` row — **not here** (O5) |
| color information, where useful | observations at the reader's own slot names, `direct`, no tier |
| perceptual hash | observation, `field=perceptual hash`, `direct` — the P5 half of **G5**, which gives duplicate and version families to P6 *"from P1's content hashes and P5's perceptual hashes"* |
| EXIF: camera make · model · lens · ISO · focal length · capture time · GPS · orientation | one observation per tag at the **format's own tag name** (P4 D7), `direct`, tier from the reader's classification |
| software metadata | observations at the reader's own slot names, `direct`, `signal_tier: 3` |
| filename pattern | observation, zone `filename`, no span, `possible` — the pattern set is **Deferred** and the matcher is the caller's |
| OCR output, where needed | **E6, as its own run** (Task 14). An opaque image produces two `extraction_runs` rows, which is exactly what B1 says a per-file status could not express |

**The hierarchy is exposed, and never resolved.** §2.6: *"camera EXIF is strong photo evidence; capture
time, GPS, and sensor-shaped dimensions reinforce it; exact display resolutions, PNG format, and
software metadata may support a screenshot hypothesis; conflicting signals should lead to abstention
rather than an invented classification."* `SIGNAL_TIER` is that sentence as a table, and P4's
`signal_tier` is where it lands (M2). **E5 emits no photo/screenshot conclusion at all** — `media type`
is a Photos-domain fact (§3.11) and belongs to P6 — and it writes no conflict row and no resolution:
§3.7's minimum-score-and-margin rule is what produces §2.6's abstention, and that is P6's.

**Three Deferred values, three caller-supplied strategies, no list in `src/extractors/`.** §2.6's
Deferred rows are *"which resolutions"*, *"which aspect ratios qualify"*, and *"the pattern set"*. So
`dimension_signal` and `filename_pattern` are **required keywords with no default**; `dimension_signal`
returns at most one of §2.6's two dimension readings and a third name is refused. No resolution, no
ratio and no filename regex appears anywhere in P5, and Task 20 asserts it by introspection.

**Trap 1 — absence of EXIF is not proof of a screenshot.** §2.6: *"Messaging platforms and downloaded
web images often strip metadata from real photographs."* P4 forbids writing an absence, so E5 writes
**nothing at all** about it: a JPEG with stripped EXIF produces a `complete` run whose observations
carry **no `signal_tier` of any kind**, and that run *is* the record. The checkable form of the SPEC's
sentence is "no EXIF-addressed observation and no `signal_tier`", because §2.6 also requires format and
dimensions at zone `metadata` — see *SPEC vs design*.

**Trap 2 — OCR text density is not a screenshot detector.** §2.6: *"receipts, document scans,
whiteboards, and photographs of pages can all contain dense text."* E5 is given **no text at all**:
`extract_image` takes no OCR parameter and no text parameter, so there is no value in scope from which a
text-volume signal could be derived. The test asserts that on the signature, which is stronger than
asserting the absence of an expression.

**Trap 3 — conflicting signals.** The SPEC's `conflicting-signals.png` carries camera EXIF **and** an
exact display resolution. Those are two different raw values, so P4 D10 makes them two observations —
one at `signal_tier: 1`, one at `signal_tier: 3` — and E5 stops there. **HEIC is mandatory** (§2.6:
failing to configure for it *"can silently exclude a meaningful portion of an Apple-centric corpus"*),
so a HEIC fixture is a required test, not an optional one.

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_image.py
"""E5 - §2.6. Done-means 8: "HEIC extracts. The three §2.6 traps — stripped EXIF,
dense OCR text, conflicting signals — each produce abstention, and E5 emits no
photo/screenshot conclusion at all."
"""
import inspect
from pathlib import Path

import pytest

from extractors.image import (
    DIMENSIONS_FIELD, DIMENSION_SIGNALS, EXTRACTOR_NAME, ExifValue,
    FILENAME_PATTERN_FIELD, FORMAT_FIELD, ImageRecord, PERCEPTUAL_HASH_FIELD,
    SIGNAL_TIER, UnknownSignal, extract_image,
)
from extractors.safety import DatalessRefused, ProtectedContainerRefused, SafetyPolicy

from conftest import FIXED_CLOCK

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
FILE_ROW = {"file_id": "f-img", "content_hash": "sha256:img",
            "filename": "IMG_4821.heic"}

NO_DIMENSION_SIGNAL = lambda width, height: None
NO_PATTERN = lambda filename: None


def a_photo_heic() -> ImageRecord:
    """The SPEC's `photo.heic`."""
    return ImageRecord(
        image_format="HEIC", dimensions="4032x3024", width=4032, height=3024,
        perceptual_hash="phash:8f3a",
        exif=(ExifValue(name="Make", value="Apple", kind="camera EXIF"),
              ExifValue(name="Model", value="iPhone 15 Pro", kind="camera EXIF"),
              ExifValue(name="DateTimeOriginal", value="2026:07:17 14:03:22",
                        kind="capture time"),
              ExifValue(name="GPSLatitude", value="38.6488N", kind="GPS")),
        color={"ColorSpace": "sRGB"},
        software={"Software": "iOS 19.1"})


def run_it(record=None, *, dimension_signal=NO_DIMENSION_SIGNAL,
           filename_pattern=NO_PATTERN, file_row=None):
    return extract_image(
        file_row=file_row or FILE_ROW, path=Path("/corpus/IMG_4821.heic"),
        policy=OPEN_POLICY,
        read_image=lambda target: record if record is not None else a_photo_heic(),
        dimension_signal=dimension_signal, filename_pattern=filename_pattern,
        now=FIXED_CLOCK, context_window=20)


def slots(rows):
    return {r["location"]["container_path"][0]["label"]: r
            for r in rows if r["location"]["container_path"]}


def test_every_observation_conforms_to_p4s_shape(sink):
    sink.write(run_it())
    sink.conforms()


def test_heic_extracts_and_its_camera_exif_is_tier_one(sink):
    # §2.6: "HEIC support must be included explicitly." A required test.
    run_id = sink.write(run_it())
    rows = slots(sink.observations_for(run_id))
    assert rows[FORMAT_FIELD]["raw_value"] == "HEIC"
    assert rows[DIMENSIONS_FIELD]["raw_value"] == "4032x3024"
    assert rows["Make"]["signal_tier"] == 1
    assert rows["Model"]["signal_tier"] == 1


def test_every_section_2_6_signal_carries_its_own_tier(sink):
    run_id = sink.write(run_it())
    rows = slots(sink.observations_for(run_id))
    assert rows["DateTimeOriginal"]["signal_tier"] == SIGNAL_TIER["capture time"] == 2
    assert rows["GPSLatitude"]["signal_tier"] == 2
    assert rows["Software"]["signal_tier"] == SIGNAL_TIER["software metadata"] == 3
    assert rows["ColorSpace"]["signal_tier"] is None


def test_the_perceptual_hash_is_emitted_and_the_content_hash_is_not(sink):
    # G5 gives duplicate and version families to P6, "from P1's content hashes and
    # P5's perceptual hashes". P5 supplies the second and recomputes the first never.
    run_id = sink.write(run_it())
    rows = slots(sink.observations_for(run_id))
    assert rows[PERCEPTUAL_HASH_FIELD]["raw_value"] == "phash:8f3a"
    assert not [o for o in sink.observations_for(run_id)
                if o["raw_value"] == FILE_ROW["content_hash"]]


def test_file_size_and_filename_are_not_re_emitted(sink):
    # O5: they are P3's §1.2 record, surfaced by the `filesystem` run (Task 6).
    run_id = sink.write(run_it())
    labels = set(slots(sink.observations_for(run_id)))
    assert "file size" not in labels
    assert not [o for o in sink.observations_for(run_id)
                if o["raw_value"] == FILE_ROW["filename"]]


def test_png_format_is_section_2_6s_tier_three_signal(sink):
    record = ImageRecord(image_format="PNG", dimensions="2880x1800", width=2880,
                         height=1800)
    run_id = sink.write(run_it(record=record))
    assert slots(sink.observations_for(run_id))[FORMAT_FIELD]["signal_tier"] == 3


def test_stripped_exif_writes_nothing_at_all_about_the_absence(sink):
    # The SPEC's `whatsapp-stripped-exif.jpg`: a real photograph, EXIF removed.
    record = ImageRecord(image_format="JPEG", dimensions="1080x1440", width=1080,
                         height=1440)
    run_id = sink.write(run_it(record=record))
    rows = sink.observations_for(run_id)
    assert sink.run_for(run_id)["completeness"] == "complete"
    assert all(o["signal_tier"] is None for o in rows), "a screenshot signal exists"
    joined = " ".join(o["raw_value"] for o in rows).lower()
    for word in ("absent", "missing", "stripped", "none", "no exif"):
        assert word not in joined
    sink.conforms()


def test_e5_is_given_no_text_so_text_density_cannot_become_a_signal():
    # §2.6: "OCR text density is also not a reliable screenshot detector." The
    # strongest available statement of that is that no text is in scope at all.
    parameters = set(inspect.signature(extract_image).parameters)
    assert not {"text", "ocr", "ocr_text", "recognized_text"} & parameters
    fields = set(inspect.signature(ImageRecord).parameters)
    assert not {"text", "ocr", "ocr_text", "text_density"} & fields


def test_conflicting_signals_are_two_observations_and_no_resolution(sink):
    # The SPEC's `conflicting-signals.png`: camera EXIF AND an exact display
    # resolution. Two raw values, so P4 D10 makes them two rows.
    record = ImageRecord(
        image_format="PNG", dimensions="1170x2532", width=1170, height=2532,
        exif=(ExifValue(name="Make", value="Canon", kind="camera EXIF"),))
    run_id = sink.write(run_it(
        record=record,
        dimension_signal=lambda width, height: "exact display resolution"))
    rows = slots(sink.observations_for(run_id))
    assert rows["Make"]["signal_tier"] == 1
    assert rows[DIMENSIONS_FIELD]["signal_tier"] == 3
    # No conflict row, no resolution, no classification.
    joined = " ".join(o["raw_value"] for o in sink.observations_for(run_id)).lower()
    for word in ("conflict", "screenshot", "photo", "resolved", "abstain"):
        assert word not in joined
    sink.conforms()


def test_e5_emits_no_photo_or_screenshot_conclusion(sink):
    # §3.11's `media type` is a Photos-domain FACT and belongs to P6.
    run_id = sink.write(run_it())
    for o in sink.observations_for(run_id):
        assert "media_type" not in o and "screenshot" not in o
        assert o["location"]["zone"] in ("metadata", "filename")


def test_the_resolution_list_and_the_aspect_ratios_are_the_callers():
    # §2.6 Deferred: "which resolutions" and "which aspect ratios qualify".
    for name in ("dimension_signal", "filename_pattern", "read_image"):
        parameter = inspect.signature(extract_image).parameters[name]
        assert parameter.default is inspect.Parameter.empty, name


def test_a_dimension_signal_section_2_6_does_not_name_is_refused():
    assert DIMENSION_SIGNALS == ("sensor-shaped dimensions",
                                 "exact display resolution")
    with pytest.raises(UnknownSignal):
        run_it(dimension_signal=lambda width, height: "retina-ish")


def test_an_exif_kind_section_2_6_does_not_name_is_refused():
    record = ImageRecord(image_format="JPEG", dimensions="1x1", width=1, height=1,
                         exif=(ExifValue(name="X", value="y", kind="vibes"),))
    with pytest.raises(UnknownSignal):
        run_it(record=record)


def test_the_filename_pattern_is_the_callers_match(sink):
    # §2.6's own example is `IMG_4821.png`; the pattern SET is Deferred.
    run_id = sink.write(run_it(filename_pattern=lambda name: "IMG_4821"))
    pattern = [o for o in sink.observations_for(run_id)
               if o["location"]["zone"] == "filename"][0]
    assert pattern["raw_value"] == "IMG_4821"
    assert pattern["signal_tier"] is None
    assert pattern["location"]["text_span"] is None


def test_the_same_image_produces_the_same_observations(sink):
    first, second = sink.write(run_it()), sink.write(run_it())
    strip = lambda rows: [{k: v for k, v in r.items() if k != "run_id"} for r in rows]
    assert strip(sink.observations_for(first)) == strip(sink.observations_for(second))


def test_no_extractor_is_reachable_inside_a_protected_container():
    policy = SafetyPolicy(is_protected_container=lambda path: True,
                          is_dataless=lambda path: False)
    with pytest.raises(ProtectedContainerRefused):
        extract_image(file_row=FILE_ROW,
                      path=Path("/Applications/Photos.app/Contents/a.heic"),
                      policy=policy,
                      read_image=lambda target: pytest.fail("reader reached"),
                      dimension_signal=NO_DIMENSION_SIGNAL,
                      filename_pattern=NO_PATTERN, now=FIXED_CLOCK,
                      context_window=20)


def test_a_dataless_image_is_never_materialized():
    policy = SafetyPolicy(is_protected_container=lambda path: False,
                          is_dataless=lambda path: True)
    with pytest.raises(DatalessRefused):
        extract_image(file_row=FILE_ROW, path=Path("/corpus/IMG_4821.heic"),
                      policy=policy,
                      read_image=lambda target: pytest.fail("reader reached"),
                      dimension_signal=NO_DIMENSION_SIGNAL,
                      filename_pattern=NO_PATTERN, now=FIXED_CLOCK,
                      context_window=20)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_image.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'extractors.image'`

- [ ] **Step 3: Write the implementation**

```python
# src/extractors/image.py
"""E5 - images (section 2.6).

"Images require their own extraction pipeline because filenames often carry little
semantic meaning."

E5 exposes section 2.6's hierarchy of signals and resolves nothing. It emits no
photo/screenshot conclusion - `media type` is a Photos-domain fact (section 3.11) and
belongs to P6 - it writes no row about an absence, and it writes no conflict row:
"conflicting signals should lead to abstention rather than an invented
classification", and the abstention is section 3.7's margin rule, which is P6's.

Three of section 2.6's inputs are Deferred - which display resolutions are "exact",
which aspect ratios are "sensor-shaped", and the camera-filename pattern set - so
`dimension_signal` and `filename_pattern` are required keywords with no default and
no list of any of the three exists in this package.

File size and content hash are section 1.2's and P1's. O5 gives them to the
`filesystem` run and P5 recomputes neither, so neither appears here even though
section 2.6 lists both.
"""
from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from typing import Any, Callable, Mapping

from extractors.runs import coverage
from extractors.safety import SafetyPolicy, admit
from extractors.shape import (
    location, normalize_mechanical, observation, run, segment,
)
from extractors.sink import ExtractionResult

VERSION = "0.1.0"
EXTRACTOR_NAME = "image.metadata"
SOURCE_TYPE = "image"
ANALYSIS_TIER = "native"

#: Section 2.6's hierarchy, as section 2.6 states it: "camera EXIF is strong photo
#: evidence; capture time, GPS, and sensor-shaped dimensions reinforce it; exact
#: display resolutions, PNG format, and software metadata may support a screenshot
#: hypothesis". P4's `signal_tier` is where each lands (M2), so the hierarchy is
#: carried on the record and never re-derived downstream.
SIGNAL_TIER: dict[str, int] = {
    "camera EXIF": 1,
    "capture time": 2,
    "GPS": 2,
    "sensor-shaped dimensions": 2,
    "exact display resolution": 3,
    "PNG format": 3,
    "software metadata": 3,
}

#: The two section 2.6 signals that are readings of the pixel dimensions. A caller
#: returns at most one: the design gives no tiebreak for dimensions that are both,
#: and P5 invents none. See NEEDS JOSEPH.
DIMENSION_SIGNALS: tuple[str, str] = ("sensor-shaped dimensions",
                                      "exact display resolution")

#: Section 2.6 names "PNG format" as a tier-3 signal, so this token is the design's
#: and not a format list of P5's. The comparison folds case on one word.
PNG_FORMAT = "PNG"

#: Section 2.6's own names for the slots that are not EXIF tags.
FORMAT_FIELD = "format"
DIMENSIONS_FIELD = "pixel dimensions"
PERCEPTUAL_HASH_FIELD = "perceptual hash"
FILENAME_PATTERN_FIELD = "filename pattern"


class UnknownSignal(Exception):
    """A signal name section 2.6's hierarchy does not contain."""


@dataclass(frozen=True)
class ExifValue:
    """One EXIF tag, at the format's own tag name (P4 D7).

    `kind` is which of section 2.6's signals this tag is. WHICH TAG IS WHICH is
    library knowledge - EXIF tag names are an external, versioned vocabulary - so the
    reader classifies and P5 places. An `orientation` tag that section 2.6 lists but
    does not rank carries `kind=None` and no tier.
    """
    name: str
    value: str
    kind: str | None = None


@dataclass(frozen=True)
class ImageRecord:
    """What an injected `read_image` returns.

    `dimensions` is the format's own rendering of the pair, verbatim, because a raw
    value is never constructed by P5 (RAW-1); `width` and `height` are ints supplied
    for the caller's dimension signal and are emitted nowhere.
    """
    image_format: str
    dimensions: str
    width: int
    height: int
    perceptual_hash: str | None = None
    exif: tuple[ExifValue, ...] = ()
    color: Mapping[str, str] = dataclass_field(default_factory=dict)
    software: Mapping[str, str] = dataclass_field(default_factory=dict)


def _tier(signal: str | None) -> int | None:
    if signal is None:
        return None
    if signal not in SIGNAL_TIER:
        raise UnknownSignal(
            f"{signal!r} is not one of section 2.6's signals {tuple(SIGNAL_TIER)}"
        )
    return SIGNAL_TIER[signal]


def extract_image(*, file_row: Mapping[str, Any], path: Path, policy: SafetyPolicy,
                  read_image: Callable[[Path], ImageRecord],
                  dimension_signal: Callable[[int, int], str | None],
                  filename_pattern: Callable[[str], str | None],
                  now: str, context_window: int) -> ExtractionResult:
    """Section 2.6's fields, as P4 records, with the hierarchy on the record.

    `context_window` is accepted and unused: every value here is a whole metadata
    slot with no surrounding text, so P4's three context fields are empty. The
    parameter stays so the six extractors have one calling shape.
    """
    admit(path, policy=policy)
    record = read_image(path)

    observations: list[Mapping[str, Any]] = []

    def emit(*, zone, raw, label, reliability, signal=None):
        observations.append(observation(
            file_id=file_row["file_id"], content_hash=file_row["content_hash"],
            extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
            source_type=SOURCE_TYPE, raw_value=raw,
            normalized_value=normalize_mechanical(raw),
            location=location(zone=zone,
                              container_path=(segment("field", label=label),)
                              if label is not None else ()),
            observed_at=now, reliability=reliability, signal_tier=_tier(signal),
        ))

    emit(zone="metadata", raw=record.image_format, label=FORMAT_FIELD,
         reliability="direct",
         signal="PNG format"
         if record.image_format.strip().upper() == PNG_FORMAT else None)

    chosen = dimension_signal(record.width, record.height)
    if chosen is not None and chosen not in DIMENSION_SIGNALS:
        raise UnknownSignal(
            f"{chosen!r} is not one of section 2.6's two readings of the pixel "
            f"dimensions {DIMENSION_SIGNALS}"
        )
    emit(zone="metadata", raw=record.dimensions, label=DIMENSIONS_FIELD,
         reliability="direct", signal=chosen)

    if record.perceptual_hash:
        emit(zone="metadata", raw=record.perceptual_hash,
             label=PERCEPTUAL_HASH_FIELD, reliability="direct")

    for tag in record.exif:
        if not tag.value:
            continue                    # presence only; an absence is never a row
        emit(zone="metadata", raw=tag.value, label=tag.name, reliability="direct",
             signal=tag.kind)

    for slot in sorted(record.color):
        if record.color[slot]:
            emit(zone="metadata", raw=record.color[slot], label=slot,
                 reliability="direct")

    for slot in sorted(record.software):
        if record.software[slot]:
            emit(zone="metadata", raw=record.software[slot], label=slot,
                 reliability="direct", signal="software metadata")

    matched = filename_pattern(file_row["filename"])
    if matched:
        # Zone `filename`, and no span: the filename's text unit belongs to the
        # `filesystem` run and P4 conformance rule 10 keys units on the SAME run, so
        # this degrades to the coarser address (P4 segment-kind rule 4).
        emit(zone="filename", raw=matched, label=None, reliability="possible")

    return ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
                source_type=SOURCE_TYPE, analysis_tier=ANALYSIS_TIER,
                config={"reader": "injected"}, completeness="complete",
                coverage=coverage("images", 1, 1),
                observation_count=len(observations), started_at=now, finished_at=now),
        observations=tuple(observations),
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p5/test_p5_image.py -v`
Expected: PASS — 17 passed

- [ ] **Step 5: Commit**

```bash
git add src/extractors/image.py tests/p5/test_p5_image.py
git commit -m "feat(P5): E5 images - HEIC, the signal hierarchy on the record, no conclusion and no absence"
```

---

### Task 14: E6 — OCR (§2.7), all nine persisted fields and no OCR-specific shape

**Files:**
- Create: `src/extractors/ocr.py`
- Test: `tests/p5/test_p5_ocr.py`

**Interfaces:**
- Consumes: `extractors.shape`, `extractors.safety.admit`, `extractors.runs.coverage`; caller-supplied `ocr_engine(path, *, config) -> OcrOutput`, `find_structured_strings`, and a caller-supplied `config` mapping.
- Produces: `VERSION`, `EXTRACTOR_NAME_PREFIX`, `SOURCE_TYPE`, `ANALYSIS_TIER`, `PERSISTED_FIELDS`, `FIELD_HOMES`, `OcrRegion`, `OcrOutput`, `extractor_name_for()`, `extract_ocr()`.

**§2.7 is this task and Task 8.** Task 8 decided *when* OCR may run — §2.2's three text-layer states and
§2.7's *"no usable text and no usable metadata"* trigger. This task is the run itself.

**All nine §2.7 fields, and the home each has (B1).** *"The database should preserve the OCR provider
and version, languages, configuration, page or image reference, raw recognized text, locations or
bounding boxes where available, confidence information, and whether extraction was complete or
capped."* This is the seam the SPEC calls *"the one P5 and P4 were most likely to fail to meet"*, and it
is what closed **P5 Open question 2**. `FIELD_HOMES` is that mapping in code, and the headline test walks
it.

| §2.7 field | home |
|---|---|
| OCR provider | `extraction_runs.extractor_name` (`ocr.<provider>`) |
| version | `extraction_runs.extractor_version` |
| languages | `extraction_runs.config` |
| configuration | `extraction_runs.config` + `config_fingerprint` |
| page or image reference | `location.container_path` — `page=N` / `region=K` |
| raw recognized text | `text_units`, one row per page or region (G1) |
| locations or bounding boxes | `location.region` |
| confidence information | the observation's `confidence` |
| complete or capped | `extraction_runs.completeness` + `coverage` |

**Nothing on this list needs a field P4 does not already publish**, and P5 adds none. OCR provider,
config, languages, confidence and the capped flag are **not** on the observation — that is P5 OQ2,
closed, and re-opening it is the specific mistake this task exists to prevent.

**P5 spells no provider name.** §2.7 names Apple Vision, and **S1** makes it the whole of v1's OCR scope
— *"v1 therefore ships OCR on macOS only; there is no cross-platform OCR requirement in this contract,
and no other provider is implied, deferred, or stubbed."* But the provider **reports its own name and
version** (§2.7's first persisted field), so `extractor_name` is built from what the engine returns and
`ocr.py` contains no provider string. That is also why `runs.analysis_tier_for` keys the `ocr` tier on
the `ocr.` prefix rather than on a name.

**Configuration is the caller's, with no default.** §2.7: *"accurate recognition (not fast), appropriate
language support including CJK where required, and a practical rendering resolution such as 200 DPI."*
The language list is **Deferred**, and 200 DPI is *"such as"* — an example, not a value. So `config` is a
required keyword P5 never fills in, the values arrive from P1's namespaced configuration object (G4),
and `src/extractors/ocr.py` holds **no number at all**. Which languages, which DPI and what confidence
policy are **NEEDS JOSEPH** items.

**Capped is never complete.** §2.7 and §8.6: *"OCR also needs a page cap, total run-time limit, progress
state, and partial-read state, because long scanned books can otherwise create unexpectedly expensive
workloads,"* and *"A capped run keeps the text it recognized and is marked capped — it is never
presented as complete."* The SPEC's `scanned-book-400pp.pdf` is the test: `completeness: capped`,
`coverage {pages, 50, 400}`, and the fifty pages of recognized text retained. **P5 holds no cap**: the
engine was given §8.6's ceilings and reports that it stopped.

**Recognized text is text, and text is a unit.** The observations E6 emits are the structured strings
found *in* the recognized text, at zone `ocr`, with spans into the region unit their container names. An
OCR run over a screenshot with no such strings is `complete` with **zero observations** and a full text
unit — §2.4's `complete`-with-zero, and the honest outcome: OCR's product is text.

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_ocr.py
"""E6 - §2.7. Done-means 9: "OCR persists all nine §2.7 fields across
`extraction_runs`, the observation and `text_units`, and the 400-page fixture is
marked `capped` rather than `complete`."
"""
import inspect
from pathlib import Path

import pytest

import extractors.ocr as ocr_module
from extractors.ocr import (
    ANALYSIS_TIER, EXTRACTOR_NAME_PREFIX, FIELD_HOMES, OcrOutput, OcrRegion,
    PERSISTED_FIELDS, extract_ocr, extractor_name_for,
)
from extractors.reading import StructuredString
from extractors.runs import analysis_tier_for, cache_key
from extractors.safety import DatalessRefused, ProtectedContainerRefused, SafetyPolicy
from extractors.shape import fingerprint

from conftest import FIXED_CLOCK

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
FILE_ROW = {"file_id": "f-scan", "content_hash": "sha256:scan",
            "filename": "hw5-photographed.pdf"}

#: Every value here is the CALLER's. §2.7's language list is Deferred and its DPI is
#: named as "such as", so no number and no language code lives in `extractors`.
FIXTURE_CONFIG = {"recognition": "accurate", "languages": ["en-US"], "dpi": 200}

RECOGNIZED = "Homework 5 for BUSIB 4300, due 2026-07-17."


def a_page(number=1, text=RECOGNIZED, confidence=0.94):
    return OcrRegion(page=number, region=1, text=text,
                     box={"x": 0.1, "y": 0.2, "width": 0.8, "height": 0.05},
                     confidence=confidence)


def an_output(**overrides) -> OcrOutput:
    base = dict(provider="apple-vision", provider_version="19.1",
                regions=(a_page(),), pages_processed=1, pages_total=1, capped=False)
    base.update(overrides)
    return OcrOutput(**base)


def find_course_code(text: str):
    at = text.find("BUSIB 4300")
    return (StructuredString(kind="identifier", start=at, end=at + 10),) if at != -1 else ()


def run_it(output=None, *, config=None, finder=find_course_code):
    seen = {}

    def engine(target, *, config):
        seen["config"] = config
        return output if output is not None else an_output()

    result = extract_ocr(
        file_row=FILE_ROW, path=Path("/corpus/hw5-photographed.pdf"),
        policy=OPEN_POLICY, ocr_engine=engine,
        config=FIXTURE_CONFIG if config is None else config,
        find_structured_strings=finder, now=FIXED_CLOCK, context_window=20)
    return result, seen


def test_every_observation_conforms_to_p4s_shape(sink):
    result, _ = run_it()
    sink.write(result)
    sink.conforms()


def test_all_nine_section_2_7_fields_have_a_home_and_are_populated(sink):
    # Done-means 9, and the closing of P5 Open question 2.
    assert len(PERSISTED_FIELDS) == 9
    assert set(FIELD_HOMES) == set(PERSISTED_FIELDS)

    result, _ = run_it()
    run_id = sink.write(result)
    row = sink.run_for(run_id)
    unit = sink.units_for(run_id)[0]
    found = sink.observations_for(run_id)[0]

    assert row["extractor_name"] == "ocr.apple-vision"          # provider
    assert row["extractor_version"] == "19.1"                   # version
    assert row["config"]["languages"] == ["en-US"]              # languages
    assert row["config_fingerprint"] == fingerprint(FIXTURE_CONFIG)  # configuration
    assert unit["container_path"][0] == {"kind": "page", "index": 1,
                                         "label": None}         # page reference
    assert unit["text"] == RECOGNIZED                            # raw recognized text
    assert found["location"]["region"] == {"x": 0.1, "y": 0.2, "width": 0.8,
                                           "height": 0.05}       # bounding box
    assert found["confidence"] == 0.94                           # confidence
    assert row["completeness"] == "complete"                     # complete or capped
    assert row["coverage"] == {"units": "pages", "processed": 1, "total": 1}


def test_the_ocr_specific_fields_are_never_on_the_observation():
    # P5 Open question 2 is CLOSED. Re-opening it is the mistake this test prevents.
    result, _ = run_it()
    for observation in result.observations:
        for name in ("provider", "languages", "config", "capped", "dpi",
                     "ocr_provider", "recognition"):
            assert name not in observation, name


def test_raw_recognized_text_is_a_unit_and_lives_nowhere_else(sink):
    # G1: one home for bulk text.
    result, _ = run_it()
    run_id = sink.write(result)
    assert [u["text"] for u in sink.units_for(run_id)] == [RECOGNIZED]
    assert all(o["raw_value"] != RECOGNIZED for o in sink.observations_for(run_id))


def test_the_span_indexes_into_the_unit_its_container_names(sink):
    result, _ = run_it()
    run_id = sink.write(result)
    found = sink.observations_for(run_id)[0]
    assert found["raw_value"] == "BUSIB 4300"
    assert found["location"]["zone"] == "ocr"
    unit = sink.units_for(run_id)[0]
    span = found["location"]["text_span"]
    assert unit["text"][span["start"]:span["end"]] == "BUSIB 4300"


def test_an_image_region_addresses_by_region_when_there_is_no_page(sink):
    output = an_output(regions=(OcrRegion(page=None, region=2, text="Receipt",
                                          confidence=0.7),),
                       pages_processed=1, pages_total=1)
    result, _ = run_it(output=output, finder=lambda text: ())
    run_id = sink.write(result)
    assert sink.units_for(run_id)[0]["container_path"] == (
        {"kind": "region", "index": 2, "label": None},)


def test_a_screenshot_with_no_structured_strings_is_complete_with_zero_rows(sink):
    result, _ = run_it(finder=lambda text: ())
    run_id = sink.write(result)
    assert sink.observations_for(run_id) == []
    assert sink.run_for(run_id)["completeness"] == "complete"
    assert sink.units_for(run_id)[0]["text"] == RECOGNIZED
    sink.conforms()


def test_the_provider_is_the_engines_and_p5_spells_none():
    # S1: Apple Vision is the one engine §2.7 names and the whole of v1's scope, and
    # §2.7's first persisted field is that the PROVIDER reports its own name.
    assert extractor_name_for("apple-vision") == "ocr.apple-vision"
    assert analysis_tier_for("ocr.apple-vision") == ANALYSIS_TIER == "ocr"
    # Scoped to real module-level constants, NOT to `__doc__`: the docstring quotes
    # §2.7 and names the engine, and a guard that matched prose would fail on the
    # very sentence it exists to enforce.
    values = [value for name, value in vars(ocr_module).items()
              if not name.startswith("__") and isinstance(value, str)]
    for value in values:
        assert "vision" not in value.lower(), value
        assert "tesseract" not in value.lower(), value


def test_p5_holds_no_dpi_no_language_and_no_confidence_threshold():
    # §2.7 Deferred: the language list, and "a practical rendering resolution such
    # as 200 DPI" is an example. Every value is the caller's.
    for name, value in vars(ocr_module).items():
        if name.startswith("__"):
            continue
        assert not isinstance(value, (int, float)) or isinstance(value, bool), name
    parameter = inspect.signature(extract_ocr).parameters["config"]
    assert parameter.default is inspect.Parameter.empty


def test_the_configuration_reaches_the_engine_and_changes_the_cache_key():
    # §3.4: "Content hash + extractor version + `analysis_tier`, plus provider,
    # version and configuration for OCR."
    _, seen = run_it()
    assert seen["config"] == FIXTURE_CONFIG

    other = dict(FIXTURE_CONFIG, languages=["ja-JP"])
    keys = set()
    for config in (FIXTURE_CONFIG, other):
        result, _ = run_it(config=config)
        keys.add(cache_key(content_hash=result.run["content_hash"],
                           extractor_name=result.run["extractor_name"],
                           extractor_version=result.run["extractor_version"],
                           analysis_tier=result.run["analysis_tier"],
                           config_fingerprint=result.run["config_fingerprint"]))
    assert len(keys) == 2


def test_the_four_hundred_page_book_is_capped_and_keeps_its_text(sink):
    # The SPEC's `scanned-book-400pp.pdf`. §8.6: "A capped OCR run keeps its partial
    # text and is flagged capped — partial evidence is allowed, misrepresented
    # evidence is not."
    regions = tuple(a_page(number=n, text=f"page {n} text") for n in range(1, 51))
    output = an_output(regions=regions, pages_processed=50, pages_total=400,
                       capped=True)
    result, _ = run_it(output=output, finder=lambda text: ())
    run_id = sink.write(result)
    row = sink.run_for(run_id)
    assert row["completeness"] == "capped"
    assert row["completeness"] != "complete"
    assert row["coverage"] == {"units": "pages", "processed": 50, "total": 400}
    assert len(sink.units_for(run_id)) == 50
    sink.conforms()


def test_p5_holds_no_page_cap_of_its_own():
    # §8.6's ceilings are configuration (G4); the engine was given them and reports
    # that it stopped. Nothing in E6 decides to stop.
    source_names = [name for name in vars(ocr_module) if not name.startswith("__")]
    for token in ("MAX_", "_LIMIT", "CEILING", "THRESHOLD", "PAGE_CAP"):
        assert not [n for n in source_names if token in n], token


def test_the_same_content_and_config_produce_the_same_observations(sink):
    first = sink.write(run_it()[0])
    second = sink.write(run_it()[0])
    strip = lambda rows: [{k: v for k, v in r.items() if k != "run_id"} for r in rows]
    assert strip(sink.observations_for(first)) == strip(sink.observations_for(second))


def test_no_extractor_is_reachable_inside_a_protected_container():
    policy = SafetyPolicy(is_protected_container=lambda path: True,
                          is_dataless=lambda path: False)
    with pytest.raises(ProtectedContainerRefused):
        extract_ocr(file_row=FILE_ROW,
                    path=Path("/System/Library/Thing/scan.pdf"), policy=policy,
                    ocr_engine=lambda target, *, config: pytest.fail("engine ran"),
                    config=FIXTURE_CONFIG, find_structured_strings=lambda text: (),
                    now=FIXED_CLOCK, context_window=20)


def test_a_dataless_file_is_never_ocred():
    policy = SafetyPolicy(is_protected_container=lambda path: False,
                          is_dataless=lambda path: True)
    with pytest.raises(DatalessRefused):
        extract_ocr(file_row=FILE_ROW, path=Path("/corpus/hw5-photographed.pdf"),
                    policy=policy,
                    ocr_engine=lambda target, *, config: pytest.fail("engine ran"),
                    config=FIXTURE_CONFIG, find_structured_strings=lambda text: (),
                    now=FIXED_CLOCK, context_window=20)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_ocr.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'extractors.ocr'`

- [ ] **Step 3: Write the implementation**

```python
# src/extractors/ocr.py
"""E6 - OCR (section 2.7).

"OCR is not merely a rescue tool for scanned PDFs. It is the main way screenshots and
opaque loose images become understandable to the pre-sorting engine."

WHEN it runs is ocr_policy.py's (section 2.2's three text-layer states and section
2.7's no-usable-text-and-no-usable-metadata trigger). This module is the run.

Section 2.7's nine persisted fields all land on records P4 already publishes, which
is what closed P5 Open question 2. FIELD_HOMES is that mapping; there is no
OCR-specific record and nothing OCR-specific on an observation.

P5 spells no provider name. Section 2.7 names Apple Vision and S1 makes it the whole
of v1's scope, but section 2.7's first persisted field is that the provider reports
its own name and version, so `extractor_name` is built from what the engine returns.

P5 holds no number. Section 2.7's language list is Deferred and its "practical
rendering resolution such as 200 DPI" is an example; section 8.6's page cap and
run-time limits are configuration P1 owns (G4). The engine is given them and reports
that it stopped; nothing here decides to stop.
"""
from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from typing import Any, Callable, Mapping

from extractors.reading import StructuredString
from extractors.runs import coverage
from extractors.safety import SafetyPolicy, admit
from extractors.shape import (
    context_for, location, normalize_mechanical, observation, run, segment, text_unit,
)
from extractors.sink import ExtractionResult

VERSION = "0.1.0"

#: `runs.analysis_tier_for` keys the `ocr` tier on this prefix rather than on a name,
#: so a second provider needs no edit there and P5 spells no provider.
EXTRACTOR_NAME_PREFIX = "ocr."
SOURCE_TYPE = "ocr"
ANALYSIS_TIER = "ocr"

#: Section 2.7's own list: "the OCR provider and version, languages, configuration,
#: page or image reference, raw recognized text, locations or bounding boxes where
#: available, confidence information, and whether extraction was complete or capped."
PERSISTED_FIELDS: tuple[str, ...] = (
    "OCR provider", "version", "languages", "configuration",
    "page or image reference", "raw recognized text",
    "locations or bounding boxes", "confidence information",
    "complete or capped",
)

#: Where each of the nine lives (B1). Every one of them is a field P4 already
#: publishes: this is the mapping that closed P5 Open question 2, and it is here so a
#: test can walk it rather than a reviewer having to trust prose.
FIELD_HOMES: dict[str, str] = {
    "OCR provider": "extraction_runs.extractor_name",
    "version": "extraction_runs.extractor_version",
    "languages": "extraction_runs.config",
    "configuration": "extraction_runs.config_fingerprint",
    "page or image reference": "location.container_path",
    "raw recognized text": "text_units.text",
    "locations or bounding boxes": "location.region",
    "confidence information": "evidence.confidence",
    "complete or capped": "extraction_runs.completeness",
}


@dataclass(frozen=True)
class OcrRegion:
    """One recognized page or image region.

    `page` is section 2.7's "page or image reference" for a paged document and is
    None for a loose image, which has a region and no page. `box` is section 2.7's
    "locations or bounding boxes, where available" and lands on P4's
    `location.region`.
    """
    page: int | None
    region: int
    text: str
    box: Mapping[str, float] | None = None
    confidence: float | None = None


@dataclass(frozen=True)
class OcrOutput:
    """What an injected `ocr_engine` returns.

    `capped` is section 2.7's partial-read state: the engine was given section 8.6's
    page cap and run-time limits and reports that it reached one.
    """
    provider: str
    provider_version: str
    regions: tuple[OcrRegion, ...] = ()
    pages_processed: int = 0
    pages_total: int = 0
    capped: bool = False


def extractor_name_for(provider: str) -> str:
    """Section 2.7's first persisted field, as P4's `extractor_name`."""
    return f"{EXTRACTOR_NAME_PREFIX}{provider}"


def extract_ocr(*, file_row: Mapping[str, Any], path: Path, policy: SafetyPolicy,
                ocr_engine: Callable[..., OcrOutput],
                config: Mapping[str, Any],
                find_structured_strings: Callable[[str],
                                                  tuple[StructuredString, ...]],
                now: str, context_window: int) -> ExtractionResult:
    """Section 2.7's run, as P4 records.

    The recognized text is a `text_units` row per page or region (G1); the
    observations are the structured strings found in it, with spans that index into
    the unit their container path names.
    """
    admit(path, policy=policy)
    output = ocr_engine(path, config=config)
    name = extractor_name_for(output.provider)

    observations: list[Mapping[str, Any]] = []
    units: list[Mapping[str, Any]] = []

    for recognized in output.regions:
        container = ((segment("page", index=recognized.page),)
                     if recognized.page is not None
                     else (segment("region", index=recognized.region),))
        units.append(text_unit(text=recognized.text, container_path=container))
        for found in find_structured_strings(recognized.text):
            raw = recognized.text[found.start:found.end]
            before, after, truncated = context_for(recognized.text, found.start,
                                                   found.end, window=context_window)
            observations.append(observation(
                file_id=file_row["file_id"],
                content_hash=file_row["content_hash"],
                extractor_name=name, extractor_version=output.provider_version,
                source_type=SOURCE_TYPE, raw_value=raw,
                normalized_value=normalize_mechanical(raw),
                location=location(zone="ocr", container_path=container,
                                  text_span={"start": found.start,
                                             "end": found.end},
                                  region=recognized.box),
                context_before=before, context_after=after,
                context_truncated=truncated, observed_at=now,
                reliability="possible", confidence=recognized.confidence,
            ))

    return ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=name, extractor_version=output.provider_version,
                source_type=SOURCE_TYPE, analysis_tier=ANALYSIS_TIER,
                config=config,
                completeness="capped" if output.capped else "complete",
                coverage=coverage("pages", output.pages_processed,
                                  output.pages_total),
                observation_count=len(observations), started_at=now,
                finished_at=now),
        observations=tuple(observations),
        text_units=tuple(units),
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p5/test_p5_ocr.py -v`
Expected: PASS — 15 passed

- [ ] **Step 5: Commit**

```bash
git add src/extractors/ocr.py tests/p5/test_p5_ocr.py
git commit -m "feat(P5): E6 OCR - nine persisted fields on P4's records, capped is never complete"
```

---

### Task 15: §8.6 — the four ceilings P5 consumes, deferral, and the user-facing count line

**Files:**
- Create: `src/extractors/budgets.py`
- Test: `tests/p5/test_p5_budgets.py`

**Interfaces:**
- Consumes: `database_agent.budget.CEILING_KEYS` and `get_ceiling` (G4 — P1 owns the configuration object), `extractors.shape.run`, `extractors.runs.coverage`.
- Produces: `P5_CEILING_KEYS`, `DEFERRED_COMPLETENESS`, `UNREADABLE_COMPLETENESS`, `p5_ceilings()`, `deferred_result()`, `extraction_counts()`.

**Four of §8.6's twelve, and P5 defines none of them.** §8.6's configurable ceilings that P5 consumes are
*maximum pages OCRed per file, maximum OCR time per file, maximum OCR time per scan, maximum
image-analysis operations per scan.* **G4 gives the configuration object to P1, namespaced**, and P1
publishes it *as implemented on 2026-08-20* as `database_agent.budget.CEILING_KEYS` — fifteen keys, of
which P5's four are `ocr.max_pages_per_file`, `ocr.max_time_per_file`, `ocr.max_time_per_scan` and
`image.max_analysis_ops_per_scan`. `budgets.py` names those four **and checks at import that every one
is a member of P1's tuple**, so a rename in P1 is an import error here rather than a silent drift. P5
stores no value: Task 20 asserts no module-level number exists anywhere in `extractors`.

**A deferral is not a failure, and P5 keeps the two apart.** §8.6: *"If the budget is exhausted, the
product should retain extracted evidence, mark the deferred stage, and leave the file or group in review
rather than guessing."* P4's `completeness: deferred` **is** the mark, so `deferred_result` writes no
`failure_reason` — a deferral with a failure reason reads as a failure, and §8.6's whole legibility
argument is that *"a file that was never processed must never look like a file that was understood and
found unimportant."* The reason a run was deferred is §8.2's *"structured explanation"* on the
`extraction` event (Task 16), which is where a reason belongs.

**Cost exhaustion never becomes a cheaper answer.** §8.6, emphasized in the design itself: ***"Cost
exhaustion must never turn into lower-quality automatic classification."*** So `deferred_result`
produces **zero observations and zero text units**, and `budgets.py` publishes no fallback, no
substitute extractor and no filename guess. There is nothing here to downgrade *to*, which is the only
durable form of that rule.

**§8.6's count line is four queries, not four readings of one word (B1).** The SPEC fixes the mapping:
**indexed** = files with any run, against P3's scanned count as the denominator; **fully extracted** =
files whose *every* run is `complete`; **deferred** = runs at `deferred` **or** `capped`; **unreadable**
= runs at `unreadable` **or** `failed`. The asymmetry — two file counts and two run counts — is the
SPEC's own and is preserved rather than smoothed: a capped OCR run on a file whose EXIF read fine is a
deferred *run*, and the file is not fully extracted. **"34 files require model review" is P8's count**
and `extraction_counts` does not produce it; a guard asserts P5 counts no model anything.

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_budgets.py
"""§8.6 — the four ceilings, deferral, and the count line P4's `completeness` feeds."""
import pytest

import extractors.budgets as budgets_module
from database_agent.budget import BUDGET_DDL, CEILING_KEYS, set_ceiling
from database_agent.db import create_schema

from extractors.budgets import (
    DEFERRED_COMPLETENESS, P5_CEILING_KEYS, UNREADABLE_COMPLETENESS, deferred_result,
    extraction_counts, p5_ceilings,
)

from conftest import FIXED_CLOCK

FILE_ROW = {"file_id": "f-book", "content_hash": "sha256:book",
            "filename": "scanned-book-400pp.pdf"}


def a_run(file_id, completeness, tier="native"):
    return {"file_id": file_id, "completeness": completeness, "analysis_tier": tier}


def test_p5s_four_ceilings_are_p1s_keys():
    # G4: P1 owns the §8.6 configuration object, namespaced. P5 defines no key.
    assert len(P5_CEILING_KEYS) == 4
    assert set(P5_CEILING_KEYS) <= set(CEILING_KEYS)
    assert P5_CEILING_KEYS == ("ocr.max_pages_per_file", "ocr.max_time_per_file",
                               "ocr.max_time_per_scan",
                               "image.max_analysis_ops_per_scan")


def test_p5_stores_no_ceiling_value():
    for name, value in vars(budgets_module).items():
        if name.startswith("__"):
            continue
        assert not isinstance(value, (int, float)) or isinstance(value, bool), name


def test_a_ceiling_is_read_through_p1_and_is_none_until_p1_holds_one(conn):
    create_schema(conn)
    conn.executescript(BUDGET_DDL)
    assert p5_ceilings(conn) == {key: None for key in P5_CEILING_KEYS}
    set_ceiling(conn, "ocr.max_pages_per_file", 50)
    assert p5_ceilings(conn)["ocr.max_pages_per_file"] == 50


def test_a_deferred_run_carries_no_evidence_at_all(sink):
    result = deferred_result(file_row=FILE_ROW, source_type="text_document",
                             extractor_name="ocr.apple-vision",
                             extractor_version="19.1", analysis_tier="ocr",
                             units="pages", total=400, now=FIXED_CLOCK)
    run_id = sink.write(result)
    assert sink.observations_for(run_id) == []
    assert sink.units_for(run_id) == []
    assert sink.run_for(run_id)["coverage"] == {"units": "pages", "processed": 0,
                                               "total": 400}
    sink.conforms()


def test_a_deferral_is_not_a_failure(sink):
    # §8.6's legibility rule: a file that was never processed must never look like a
    # file that was understood and found unimportant.
    run_id = sink.write(deferred_result(
        file_row=FILE_ROW, source_type="text_document",
        extractor_name="ocr.apple-vision", extractor_version="19.1",
        analysis_tier="ocr", units="pages", total=400, now=FIXED_CLOCK))
    row = sink.run_for(run_id)
    assert row["completeness"] == "deferred"
    assert row["failure_reason"] is None


def test_p5_publishes_no_cheaper_substitute():
    # §8.6: "Cost exhaustion must never turn into lower-quality automatic
    # classification." There is nothing here to downgrade to.
    names = [n for n in vars(budgets_module) if not n.startswith("__")]
    for token in ("fallback", "substitute", "guess", "downgrade", "cheaper"):
        assert not [n for n in names if token in n.lower()], token


def test_the_section_8_6_count_line():
    # "1,842 files indexed; 1,611 fully extracted; 89 … deferred after the OCR limit;
    # … 18 files remain unreadable."
    runs = [
        a_run("a", "complete", "filesystem"), a_run("a", "complete"),
        a_run("b", "complete", "filesystem"), a_run("b", "capped", "ocr"),
        a_run("c", "complete", "filesystem"), a_run("c", "deferred", "ocr"),
        a_run("d", "unreadable"),
        a_run("e", "failed"),
    ]
    counts = extraction_counts(runs, files_scanned=10)
    assert counts == {"files_scanned": 10, "indexed": 5, "fully_extracted": 1,
                      "deferred": 2, "unreadable": 2}


def test_capped_and_deferred_are_one_query_and_unreadable_and_failed_another():
    # B1: two different values, two different queries — never two readings of one
    # word.
    assert DEFERRED_COMPLETENESS == ("deferred", "capped")
    assert UNREADABLE_COMPLETENESS == ("unreadable", "failed")
    assert not set(DEFERRED_COMPLETENESS) & set(UNREADABLE_COMPLETENESS)


def test_a_complete_run_with_zero_observations_is_still_fully_extracted():
    # §2.4's `complete`-with-zero: the file genuinely contained nothing, and that is
    # a processed file.
    counts = extraction_counts([a_run("a", "complete")], files_scanned=1)
    assert counts["fully_extracted"] == 1


def test_an_unsupported_run_is_neither_extracted_nor_unreadable():
    # §2.4's four distinguishable states stay four.
    counts = extraction_counts([a_run("a", "unsupported")], files_scanned=1)
    assert counts["indexed"] == 1
    assert counts["fully_extracted"] == 0
    assert counts["deferred"] == 0
    assert counts["unreadable"] == 0


def test_metadata_only_is_indexed_and_not_fully_extracted():
    counts = extraction_counts([a_run("a", "metadata_only")], files_scanned=1)
    assert counts == {"files_scanned": 1, "indexed": 1, "fully_extracted": 0,
                      "deferred": 0, "unreadable": 0}


def test_files_requiring_model_review_are_p8s_count_and_not_here():
    counts = extraction_counts([a_run("a", "complete")], files_scanned=1)
    assert "model" not in " ".join(counts)
    assert "review" not in " ".join(counts)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_budgets.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'extractors.budgets'`

- [ ] **Step 3: Write the implementation**

```python
# src/extractors/budgets.py
"""Section 8.6 - the four ceilings P5 consumes, deferral, and the count line.

G4 gives the section 8.6 configuration object to P1, namespaced. P5 names four of
P1's fifteen keys and stores no value; the membership check below runs at import, so
a rename in P1 is an ImportError here rather than a silent drift.

Section 8.6's degradation order puts P5 in the cheap tier with one expensive tail:
"Direct facts and high-precision rules run first ... Full local extraction and OCR run
within the configured budget." Every P5 budget lives on that tail.

"Cost exhaustion must never turn into lower-quality automatic classification." So a
deferred run carries no evidence, and this module publishes no fallback extractor, no
filename guess and no downgraded mode. There is nothing to downgrade to.
"""
from __future__ import annotations

import sqlite3
from typing import Any, Iterable, Mapping

from database_agent.budget import CEILING_KEYS, get_ceiling

from extractors.runs import coverage
from extractors.shape import run
from extractors.sink import ExtractionResult

#: Section 8.6's "Maximum pages OCRed per file / Maximum OCR time per file / Maximum
#: OCR time per scan / Maximum image-analysis operations per scan", in P1's spelling.
P5_CEILING_KEYS: tuple[str, ...] = (
    "ocr.max_pages_per_file",
    "ocr.max_time_per_file",
    "ocr.max_time_per_scan",
    "image.max_analysis_ops_per_scan",
)

_unknown = set(P5_CEILING_KEYS) - set(CEILING_KEYS)
if _unknown:
    raise ImportError(
        f"P5 names ceiling keys P1 does not publish: {sorted(_unknown)}. P1 owns the "
        "section 8.6 configuration object (G4) and P5 defines no key of its own."
    )

#: Section 8.6's "89 scanned PDFs deferred after the OCR limit" - one query.
DEFERRED_COMPLETENESS: tuple[str, ...] = ("deferred", "capped")

#: Section 8.6's "18 files remain unreadable" - a different query against different
#: values (B1). The two sets are disjoint and stay that way.
UNREADABLE_COMPLETENESS: tuple[str, ...] = ("unreadable", "failed")


def p5_ceilings(conn: sqlite3.Connection) -> dict[str, int | None]:
    """The four values P1 holds for P5. `None` means P1 holds none yet.

    Reading a ceiling is not enforcing it, and P5 enforces none here: the OCR engine
    and the image reader are given their ceilings and report that they stopped.
    """
    return {key: get_ceiling(conn, key) for key in P5_CEILING_KEYS}


def deferred_result(*, file_row: Mapping[str, Any], source_type: str,
                    extractor_name: str, extractor_version: str,
                    analysis_tier: str, units: str, total: int,
                    now: str) -> ExtractionResult:
    """The run for an extractor the budget stopped before it started.

    No `failure_reason`: P4's `completeness: deferred` IS section 8.6's mark, and a
    deferral carrying a failure reason reads as a failure - which is exactly the
    confusion section 8.6 exists to prevent. The reason lives in section 8.2's
    structured explanation on the `extraction` event.
    """
    return ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=extractor_name, extractor_version=extractor_version,
                source_type=source_type, analysis_tier=analysis_tier, config={},
                completeness="deferred", coverage=coverage(units, 0, total),
                observation_count=0, started_at=now, finished_at=now))


def extraction_counts(runs: Iterable[Mapping[str, Any]], *,
                      files_scanned: int) -> dict[str, int]:
    """Section 8.6's user-facing sentence, as four queries over P4's `completeness`.

    Two file counts and two run counts, which is the SPEC's own asymmetry: a capped
    OCR run on a file whose EXIF read fine is a deferred RUN, and the file is not
    fully extracted. "Files require model review" is P8's count and is absent.
    """
    by_file: dict[str, list[str]] = {}
    deferred = unreadable = 0
    for record in runs:
        by_file.setdefault(record["file_id"], []).append(record["completeness"])
        if record["completeness"] in DEFERRED_COMPLETENESS:
            deferred += 1
        if record["completeness"] in UNREADABLE_COMPLETENESS:
            unreadable += 1
    fully = sum(1 for states in by_file.values()
                if all(state == "complete" for state in states))
    return {
        "files_scanned": files_scanned,
        "indexed": len(by_file),
        "fully_extracted": fully,
        "deferred": deferred,
        "unreadable": unreadable,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p5/test_p5_budgets.py -v`
Expected: PASS — 12 passed

- [ ] **Step 5: Commit**

```bash
git add src/extractors/budgets.py tests/p5/test_p5_budgets.py
git commit -m "feat(P5): §8.6 budgets - P1's ceiling keys, deferral is not failure, the count line"
```

---

### Task 16: §8.2 — the two events P5 authors, and the structured explanation each carries

**Files:**
- Create: `src/extractors/events.py`
- Test: `tests/p5/test_p5_events.py`

**Interfaces:**
- Consumes: `extractors.authorship.event_defaults`, `extractors.shape.canonical_json` and `fingerprint`; P1's `database_agent.events.append_event`.
- Produces: `EXTRACTION`, `OCR`, `extraction_event()`, `ocr_event()`, `append()`.

**Two of §8.2's nineteen, and P5 registers neither.** Task 1 established the authorship constants; this
task is the events themselves. §8.2 requires each to carry *"the event type, file ID, content hash,
responsible subsystem, extractor version, time of observation, and a structured explanation or evidence
reference"*, and P1's writer requires `event_type`, `subsystem`, `component_version`, `observed_at` and
`explanation` to be present and non-empty.

**§8.2's "extractor version" is P1's `component_version`.** P1's `events` table has **eleven fields,
forever** (MINOR 1) and no `extractor_version` column, so §8.2's extractor version occupies
`component_version` on an `extraction` event. `authorship.COMPONENT_VERSION` remains the version of P5's
own event authorship and is the value only where no extractor version applies.

**For an OCR event, §8.2's model positions are the OCR positions.** The SPEC: *"For E6 the OCR provider,
version, languages and configuration occupy the position §8.2 gives to model version and prompt
fingerprint."* Read against P1's eleven fields that is exact: the provider **version** is
`component_version`, and the **configuration** — which is where §2.7's languages live — is
`prompt_fingerprint`, as the same `fingerprint()` P4's `config_fingerprint` uses, so one configuration
has one identity in both places. The provider name is in the structured explanation and in the run's
`extractor_name`.

**MINOR 2 is a run-time fact, not a style note.** §8.2 spells it **`OCR`**, and P1's writer validates the
type against §8.2's frozen vocabulary — `database_agent.events.RESERVED_EVENT_TYPES` — so the lowercase
spelling earlier drafts used raises `UnregisteredEventType` at the INSERT. The test asserts both halves:
`OCR` is accepted, `ocr` is refused by P1.

**The explanation is canonical JSON naming the `run_id`.** §8.2 asks for *"a structured explanation or
evidence reference"*, and the `run_id` **is** the evidence reference: it is the handle for the run's
observations, its text units and its outcome. Canonical JSON so that §8.5's replay diff compares two
explanations rather than two renderings of one.

**P5 appends nothing on P1's behalf and nothing of P3's.** `discovery`, `stat observation` and `hashing`
are P3's; the move events are P12's (M8). `event_defaults` already refuses them, and Task 20 asserts
`subsystem` is set in exactly one module.

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_events.py
"""§8.2 — the two events P5 authors, written by P1. MINOR 2: `OCR`, not `ocr`."""
import json

import pytest

from database_agent.db import create_schema
from database_agent.events import (
    RESERVED_EVENT_TYPES, UnregisteredEventType, append_event,
)

from extractors.authorship import AUTHORED_EVENT_TYPES, SUBSYSTEM
from extractors.events import EXTRACTION, OCR, append, extraction_event, ocr_event
from extractors.shape import fingerprint

from conftest import FIXED_CLOCK

CONFIG = {"recognition": "accurate", "languages": ["en-US"], "dpi": 200}


def an_extraction_event():
    return extraction_event(run_id="run-7", file_id="f-1",
                            content_hash="sha256:abc", extractor_name="pdf.text",
                            extractor_version="0.1.0", completeness="complete",
                            observed_at=FIXED_CLOCK)


def an_ocr_event():
    return ocr_event(run_id="run-8", file_id="f-1", content_hash="sha256:abc",
                     provider="apple-vision", provider_version="19.1",
                     config=CONFIG, completeness="capped",
                     observed_at=FIXED_CLOCK)


def test_both_types_are_reserved_section_8_2_names_and_p5_registers_nothing():
    assert EXTRACTION in RESERVED_EVENT_TYPES
    assert OCR in RESERVED_EVENT_TYPES
    assert AUTHORED_EVENT_TYPES == (EXTRACTION, OCR)


def test_minor_2_p1_accepts_OCR_and_rejects_ocr(conn):
    create_schema(conn)
    assert OCR == "OCR"
    append_event(conn, event_type=OCR, subsystem=SUBSYSTEM,
                 component_version="19.1", observed_at=FIXED_CLOCK,
                 explanation="{}")
    with pytest.raises(UnregisteredEventType):
        append_event(conn, event_type="ocr", subsystem=SUBSYSTEM,
                     component_version="19.1", observed_at=FIXED_CLOCK,
                     explanation="{}")


def test_an_extraction_event_round_trips_through_p1(conn):
    create_schema(conn)
    append(conn, an_extraction_event())
    row = conn.execute("SELECT * FROM events").fetchone()
    assert row["event_type"] == "extraction"
    assert row["subsystem"] == "P5"
    assert row["file_id"] == "f-1"
    assert row["content_hash"] == "sha256:abc"
    assert row["observed_at"] == FIXED_CLOCK


def test_section_8_2s_extractor_version_is_p1s_component_version(conn):
    create_schema(conn)
    append(conn, an_extraction_event())
    row = conn.execute("SELECT * FROM events").fetchone()
    assert row["component_version"] == "0.1.0"


def test_the_explanation_is_structured_and_names_the_run(conn):
    create_schema(conn)
    append(conn, an_extraction_event())
    row = conn.execute("SELECT * FROM events").fetchone()
    explanation = json.loads(row["explanation"])
    assert explanation["run_id"] == "run-7"
    assert explanation["extractor_name"] == "pdf.text"
    assert explanation["completeness"] == "complete"


def test_an_ocr_event_puts_version_and_configuration_in_section_8_2s_model_slots(conn):
    create_schema(conn)
    append(conn, an_ocr_event())
    row = conn.execute("SELECT * FROM events WHERE event_type = ?", (OCR,)).fetchone()
    assert row["component_version"] == "19.1"
    assert row["prompt_fingerprint"] == fingerprint(CONFIG)
    explanation = json.loads(row["explanation"])
    assert explanation["provider"] == "apple-vision"
    assert explanation["run_id"] == "run-8"
    assert explanation["completeness"] == "capped"


def test_one_configuration_has_one_identity_in_both_places():
    # The event's `prompt_fingerprint` and P4's `config_fingerprint` are the same
    # function of the same mapping, so an audit can join them.
    assert an_ocr_event()["prompt_fingerprint"] == fingerprint(CONFIG)


def test_every_event_names_p5(conn):
    create_schema(conn)
    append(conn, an_extraction_event())
    append(conn, an_ocr_event())
    authors = conn.execute("SELECT DISTINCT subsystem FROM events").fetchall()
    assert [r["subsystem"] for r in authors] == ["P5"]


def test_p5_authors_none_of_p3s_events():
    # M8: `discovery`, `stat observation` and `hashing` are P3's.
    for event_type in ("discovery", "stat observation", "hashing", "planned move"):
        with pytest.raises(ValueError):
            extraction_event(run_id="r", file_id="f", content_hash="h",
                             extractor_name="pdf.text", extractor_version="0.1.0",
                             completeness="complete", observed_at=FIXED_CLOCK,
                             event_type=event_type)


def test_a_second_run_appends_a_second_event_and_the_first_remains(conn):
    # §8.2: P5 overwrites nothing. Supersession leaves both records readable.
    create_schema(conn)
    append(conn, an_extraction_event())
    append(conn, extraction_event(
        run_id="run-9", file_id="f-1", content_hash="sha256:abc",
        extractor_name="pdf.text", extractor_version="0.2.0",
        completeness="complete", observed_at=FIXED_CLOCK))
    rows = conn.execute("SELECT * FROM events ORDER BY event_id").fetchall()
    assert [json.loads(r["explanation"])["run_id"] for r in rows] == ["run-7", "run-9"]
    assert [r["component_version"] for r in rows] == ["0.1.0", "0.2.0"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_events.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'extractors.events'`

- [ ] **Step 3: Write the implementation**

```python
# src/extractors/events.py
# WHEN P4 LANDS, `append` BECOMES A CALL INTO P4 AND STOPS WRITING DIRECTLY.
#
# P4 Task 10 publishes `record_run_event(conn, run_id, *, author)`, which appends the
# one §8.2 event for a run AFTER its observations exist, reading the `observation_key`s
# out of the rows so the event and the database cannot disagree. P5 is the AUTHOR
# (`author="P5"`); P4 is the writer. That is M8.
#
# This module exists because P4 has not landed, and it must not survive as a second
# writer: two helpers appending one run's event means either a duplicated event or a
# dead API, and M8 cannot survive two. The day `evidence_shape` is importable:
#
#     from evidence_shape.store import record_run_event
#
#     def append(conn, event) -> int:
#         return record_run_event(conn, event.run_id, author=SUBSYSTEM)
#
# `extraction_event()` / `ocr_event()` stay: they are the payload builders and the
# guard that P5 authors none of P3's event types. What goes is the direct
# `append_event` call below -- P4 builds the same dict from the stored rows.
"""Section 8.2 - the two events P5 authors. P1 writes them (M8).

Each carries "the event type, file ID, content hash, responsible subsystem, extractor
version, time of observation, and a structured explanation or evidence reference".
P1's `events` has eleven fields forever (MINOR 1), so section 8.2's extractor version
occupies `component_version`, and the run_id - the handle for a run's observations,
text units and outcome - is section 8.2's evidence reference.

For the OCR event, section 8.2's model positions are the OCR positions: the provider
VERSION is `component_version` and the CONFIGURATION, which is where section 2.7's
languages live, is `prompt_fingerprint`, computed by the same `fingerprint()` that
produces P4's `config_fingerprint` so one configuration has one identity in both.
"""
from __future__ import annotations

import sqlite3
from typing import Any, Mapping

from database_agent.events import append_event

from extractors.authorship import event_defaults
from extractors.shape import canonical_json, fingerprint

#: Section 8.2's own spellings. `OCR`, not `ocr` (MINOR 2): P1's writer validates the
#: type against section 8.2's frozen vocabulary and the lowercase form is rejected at
#: the INSERT.
EXTRACTION = "extraction"
OCR = "OCR"


def extraction_event(*, run_id: str, file_id: str, content_hash: str,
                     extractor_name: str, extractor_version: str,
                     completeness: str, observed_at: str,
                     event_type: str = EXTRACTION, **extra: Any) -> dict:
    """One `extraction` event - once per file per extractor family per content
    version."""
    return event_defaults(
        event_type=event_type, file_id=file_id, content_hash=content_hash,
        component_version=extractor_version, observed_at=observed_at,
        explanation=canonical_json({
            "run_id": run_id,
            "extractor_name": extractor_name,
            "extractor_version": extractor_version,
            "completeness": completeness,
            **extra,
        }),
    )


def ocr_event(*, run_id: str, file_id: str, content_hash: str, provider: str,
              provider_version: str, config: Mapping[str, Any],
              completeness: str, observed_at: str, **extra: Any) -> dict:
    """One `OCR` event - once per OCR run."""
    return event_defaults(
        event_type=OCR, file_id=file_id, content_hash=content_hash,
        component_version=provider_version,
        prompt_fingerprint=fingerprint(config), observed_at=observed_at,
        explanation=canonical_json({
            "run_id": run_id,
            "provider": provider,
            "provider_version": provider_version,
            "completeness": completeness,
            **extra,
        }),
    )


def append(conn: sqlite3.Connection, event: Mapping[str, Any]) -> int:
    """Hand one authored event to P1's writer. P5 stores no event of its own."""
    return append_event(conn, **event)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p5/test_p5_events.py -v`
Expected: PASS — 10 passed

- [ ] **Step 5: Commit**

```bash
git add src/extractors/events.py tests/p5/test_p5_events.py
git commit -m "feat(P5): §8.2 events - extraction and OCR, extractor version and config in §8.2's slots"
```

---

### Task 17: §8.5 / B7 — P2's envelope, produced by P5 and stored by P2

**Files:**
- Create: `src/extractors/stage_output.py`
- Test: `tests/p5/test_p5_stage_output.py`

**Interfaces:**
- Consumes: `extractors.shape.canonical_json`. **Imports nothing from `eval_harness`** — P5 produces the envelope; P2 stores it.
- Produces: `STAGE_ID`, `ENVELOPE_FIELDS`, `OUTCOME_BY_COMPLETENESS`, `CEILING_REACHED_COMPLETENESS`, `extraction_stage_output()`, `extractor_versions()`.

**B7, verbatim:** *"P5, P6, P8, P9, P10 and P11 each add to Contract out: 'Emits P2 `stage_output` with
`stage_id = <id>`, carrying `inputs[]`, an explicit abstention value, a distinct budget-deferral value,
and the version tuple.'"* P2 is **built** (`src/eval_harness/`), so this task is written against its live
surface and the test drives P5's envelope through P2's real writer rather than a stub.

**Produced, not stored.** `eval_harness.replay.StageResult` is the shape a stage adapter returns —
`subject_ref`, `outcome`, `payload`, `inputs`, `budget_state` — and `record_stage_output` adds `run_id`,
`stage_id` and `version_tuple_ref` from the run it is replaying. So P5 builds exactly those five fields
plus `stage_id`, and imports no P2 module: P5 depends on P1 and on nothing else at run time, and Task 20
asserts it.

**The mapping from P4's nine `completeness` values to P2's five outcomes, and why each row is what it
is.** This mapping is P5's to author — it is the join between two closed vocabularies neither part owns
alone — so every row states its reason. The two rows the design did not settle were answered by Joseph
on 2026-08-20 (A5, both `abstained`); `dataless` follows them for the same reason, since P5 never opened
the file. `runs_dataless` is a P2 **count**, not a fifth outcome — visible as unfinished, not as damaged.

| P4 `completeness` | P2 `outcome` | `budget_state` | why |
|---|---|---|---|
| `complete` | `produced` | `within_ceiling` | the extractor ran to the end |
| `partial` | `produced` | `within_ceiling` | some parts were readable; evidence exists |
| `capped` | `produced` | **`ceiling_reached`** | a capped run **keeps the text it recognized** (§2.7); it produced, under a ceiling that was reached. P2 permits `produced` + `ceiling_reached` and forbids `abstained` + `ceiling_reached` |
| `deferred` | **`deferred`** | **`ceiling_reached`** | §8.6's budget deferral. P2's writer *requires* this exact pairing |
| `unsupported` | `abstained` | `within_ceiling` | no extractor exists; P5 asserted nothing |
| `metadata_only` | `abstained` | `within_ceiling` | §2.9's deliberate safe stop — **ANSWERED 2026-08-20 (A5): `abstained`.** P5 declined to assert; it did not fail |
| `unreadable` | `abstained` | `within_ceiling` | format known, content not recoverable; the metadata rows are real but the extraction dimension's question was not answered — **ANSWERED 2026-08-20 (A5): `abstained`.** Calling it `produced` would let a corpus of unreadable files read as a successful run |
| `failed` | `error` | `within_ceiling` | §2.4: *"an error is not an empty document"* |

**`inputs[]` is the content hash, and that is the point.** §3.4: the cache key holds the content hash and
no path, *"which is what makes a rename free and a content rewrite expensive."* An extraction run's input
is the **file version**, so `inputs = (content_hash,)`; `subject_ref` is the `file_id`, which is what P2's
`bundle_file_entry` keys a file by.

**P5's half of the version tuple is one axis.** `eval_harness.run.VERSION_AXES[0]` is
`extractor_versions` — *"{} — one version per extractor (§3.4)"* — so `extractor_versions()` folds a set
of runs into that map and P2 assembles the tuple and stores its reference. P5 does not build a version
tuple: five of its six axes belong to parts P5 knows nothing about.

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_stage_output.py
"""§8.5 / B7 — P5's envelope, through P2's live writer."""
import json

import pytest

import extractors.stage_output as stage_output_module
from eval_harness.replay import StageResult
from eval_harness.run import VERSION_AXES, record_version_tuple, start_run
from eval_harness.stage_output import record_stage_output, stage_outputs
from eval_harness.store import create_eval_schema
from eval_harness.vocabulary import BUDGET_STATES, OUTCOMES, STAGE_IDS

from extractors.stage_output import (
    CEILING_REACHED_COMPLETENESS, ENVELOPE_FIELDS, OUTCOME_BY_COMPLETENESS, STAGE_ID,
    extraction_stage_output, extractor_versions,
)

from conftest import FIXED_CLOCK

P4_COMPLETENESS = ("complete", "capped", "partial", "metadata_only", "deferred",
                   "unsupported", "unreadable", "failed", "dataless")


def a_run(completeness="complete", extractor_name="pdf.text", version="0.1.0"):
    return {"file_id": "f-1", "content_hash": "sha256:abc",
            "extractor_name": extractor_name, "extractor_version": version,
            "source_type": "text_document", "analysis_tier": "native",
            "completeness": completeness, "observation_count": 3,
            "coverage": {"units": "pages", "processed": 18, "total": 18}}


@pytest.fixture()
def p2_run(conn):
    create_eval_schema(conn)
    ref = record_version_tuple(
        conn, extractor_versions={"pdf.text": "0.1.0"}, graph_algorithm_version=None,
        prompt_fingerprint=None, model_identifier=None,
        template_library_version=None, placement_scorer_version=None,
        analysis_tiers_enabled=["filesystem", "native"])
    run_id = start_run(conn, bundle_id="b-p5", run_kind="replay",
                       version_tuple_ref=ref, budget_ceilings={},
                       run_settings={"model_enabled": False,
                                     "embeddings_enabled": False},
                       pinned_plan_id=None, pinned_plan_version=None)
    return run_id, ref


def test_the_stage_id_is_one_of_section_8_5s_ten():
    assert STAGE_ID == "extraction"
    assert STAGE_ID in STAGE_IDS


def test_the_envelope_is_exactly_p2s_stage_result_shape():
    envelope = extraction_stage_output(run=a_run())
    assert set(ENVELOPE_FIELDS) == set(envelope) - {"stage_id"}
    StageResult(**{k: v for k, v in envelope.items() if k != "stage_id"})


def test_every_completeness_maps_to_one_of_p2s_five_outcomes():
    assert set(OUTCOME_BY_COMPLETENESS) == set(P4_COMPLETENESS)
    assert set(OUTCOME_BY_COMPLETENESS.values()) <= set(OUTCOMES)


def test_abstention_and_budget_deferral_are_different_values():
    # B7: "an explicit abstention value, a distinct budget-deferral value".
    assert OUTCOME_BY_COMPLETENESS["unsupported"] == "abstained"
    assert OUTCOME_BY_COMPLETENESS["deferred"] == "deferred"
    assert OUTCOME_BY_COMPLETENESS["unsupported"] != OUTCOME_BY_COMPLETENESS["deferred"]


def test_inputs_is_the_content_hash_so_a_rename_is_free():
    envelope = extraction_stage_output(run=a_run())
    assert envelope["inputs"] == ("sha256:abc",)
    assert envelope["subject_ref"] == "f-1"


def test_the_payload_is_p5s_own_and_p2_never_parses_it():
    envelope = extraction_stage_output(run=a_run())
    payload = json.loads(envelope["payload"])
    assert payload["extractor_name"] == "pdf.text"
    assert payload["completeness"] == "complete"
    assert payload["coverage"] == {"units": "pages", "processed": 18, "total": 18}


def test_a_capped_run_produced_under_a_reached_ceiling(conn, p2_run):
    # §2.7: a capped run keeps the text it recognized. It produced.
    run_id, ref = p2_run
    envelope = extraction_stage_output(run=a_run(completeness="capped"))
    assert envelope["outcome"] == "produced"
    assert envelope["budget_state"] == "ceiling_reached"
    record_stage_output(conn, run_id=run_id, version_tuple_ref=ref,
                        **{k: v for k, v in envelope.items()
                           if k != "stage_id"}, stage_id=STAGE_ID)
    assert stage_outputs(conn, run_id)[0]["budget_state"] == "ceiling_reached"


def test_a_deferred_run_is_the_pairing_p2s_writer_requires(conn, p2_run):
    run_id, ref = p2_run
    envelope = extraction_stage_output(run=a_run(completeness="deferred"))
    assert (envelope["outcome"], envelope["budget_state"]) == ("deferred",
                                                               "ceiling_reached")
    record_stage_output(conn, run_id=run_id, version_tuple_ref=ref,
                        **{k: v for k, v in envelope.items()
                           if k != "stage_id"}, stage_id=STAGE_ID)
    assert stage_outputs(conn, run_id)[0]["outcome"] == "deferred"


def test_p5_never_produces_the_pairing_p2_refuses():
    # §8.6: a ceiling-reached stage is `deferred`, never `abstained`.
    assert set(CEILING_REACHED_COMPLETENESS) == {"deferred", "capped"}
    for completeness in CEILING_REACHED_COMPLETENESS:
        envelope = extraction_stage_output(run=a_run(completeness=completeness))
        assert envelope["outcome"] != "abstained"


def test_every_envelope_is_accepted_by_p2s_writer(conn, p2_run):
    run_id, ref = p2_run
    for completeness in P4_COMPLETENESS:
        envelope = extraction_stage_output(run=a_run(completeness=completeness))
        assert envelope["budget_state"] in BUDGET_STATES
        record_stage_output(conn, run_id=run_id, version_tuple_ref=ref,
                            **{k: v for k, v in envelope.items()
                               if k != "stage_id"}, stage_id=STAGE_ID)
    assert len(stage_outputs(conn, run_id)) == len(P4_COMPLETENESS)


def test_p5_supplies_one_axis_of_the_version_tuple(conn, p2_run):
    assert VERSION_AXES[0] == "extractor_versions"
    versions = extractor_versions([a_run(), a_run(extractor_name="ocr.apple-vision",
                                                  version="19.1")])
    assert versions == {"pdf.text": "0.1.0", "ocr.apple-vision": "19.1"}


def test_two_versions_of_one_extractor_are_refused():
    # §3.4's cache key is per (extractor, version); one map cannot hold two.
    with pytest.raises(ValueError):
        extractor_versions([a_run(version="0.1.0"), a_run(version="0.2.0")])


def test_p5_imports_no_part_of_p2():
    # P5 produces the envelope; P2 stores it. P5's only run-time dependency is P1.
    imported = {name for name, value in vars(stage_output_module).items()
                if getattr(value, "__module__", "").startswith("eval_harness")}
    assert imported == set()
    assert "eval_harness" not in [getattr(v, "__name__", "")
                                  for v in vars(stage_output_module).values()]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_stage_output.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'extractors.stage_output'`

- [ ] **Step 3: Write the implementation**

```python
# src/extractors/stage_output.py
"""Section 8.5 / B7 - P2's envelope, produced by P5 and stored by P2.

"Emits P2 `stage_output` with `stage_id = extraction`, carrying `inputs[]`, an
explicit abstention value, a distinct budget-deferral value, and the version tuple."

Produced, not stored: `eval_harness.replay.StageResult` is the shape a stage adapter
returns and P2 adds `run_id`, `stage_id` and `version_tuple_ref` from the run it is
replaying. This module imports no part of P2 - P5's only run-time dependency is P1.

The mapping below is the join between two closed vocabularies neither part owns
alone, so every row carries its reason. Two rows are genuinely unsettled by the
design and are NEEDS JOSEPH items rather than quiet choices: `metadata_only` and
`unreadable`, both of which produce real metadata rows while leaving section 8.5's
extraction question ("did the expected text, metadata, table values, OCR text, or
image facts appear?") unanswered.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from extractors.shape import canonical_json

#: One of section 8.5's ten attribution stages. P5 is the first.
STAGE_ID = "extraction"

#: `eval_harness.replay.StageResult`'s fields, as P5 fills them.
ENVELOPE_FIELDS: tuple[str, ...] = ("subject_ref", "outcome", "payload", "inputs",
                                    "budget_state")

#: P4's nine `completeness` values to P2's five outcomes.
OUTCOME_BY_COMPLETENESS: dict[str, str] = {
    "complete": "produced",       # ran to the end, section 2.4
    "partial": "produced",        # some parts readable, section 2.5
    "capped": "produced",         # kept the text it recognized, section 2.7
    "deferred": "deferred",       # section 8.6's budget deferral
    "unsupported": "abstained",   # no extractor exists, section 2.4
    "metadata_only": "abstained",  # section 2.9's deliberate safe stop
    "unreadable": "abstained",    # indexed-but-unreadable, section 2.9 / M3
    "failed": "error",            # "an error is not an empty document", section 2.4
    "dataless": "abstained",      # C4: the bytes are not on this machine, 11 section 5
}

#: Section 8.6: a run that met a ceiling says so, and is never `abstained` - P2's
#: writer refuses that pairing outright, because a budget event must not become a
#: judgement about evidence.
CEILING_REACHED_COMPLETENESS: tuple[str, ...] = ("deferred", "capped")


def extraction_stage_output(*, run: Mapping[str, Any]) -> dict:
    """One envelope for one `extraction_runs` row.

    `subject_ref` is the file id, which is what P2's `bundle_file_entry` keys a file
    by; `inputs` is the CONTENT HASH, because an extraction run's input is the file
    VERSION - section 3.4's "a rename is free and a content rewrite is expensive".
    """
    completeness = run["completeness"]
    if completeness not in OUTCOME_BY_COMPLETENESS:
        raise ValueError(
            f"{completeness!r} is not one of P4's nine `completeness` values"
        )
    return {
        "stage_id": STAGE_ID,
        "subject_ref": run["file_id"],
        "outcome": OUTCOME_BY_COMPLETENESS[completeness],
        "payload": canonical_json({
            "extractor_name": run["extractor_name"],
            "extractor_version": run["extractor_version"],
            "source_type": run["source_type"],
            "analysis_tier": run["analysis_tier"],
            "completeness": completeness,
            "coverage": dict(run["coverage"]),
            "observation_count": run["observation_count"],
        }),
        "inputs": (run["content_hash"],),
        "budget_state": ("ceiling_reached"
                         if completeness in CEILING_REACHED_COMPLETENESS
                         else "within_ceiling"),
    }


def extractor_versions(runs: Iterable[Mapping[str, Any]]) -> dict[str, str]:
    """P5's half of section 8.5's version tuple: its first axis, "one version per
    extractor".

    Two versions of one extractor in one tuple is refused rather than resolved:
    section 3.4's cache key is per (extractor, version) and a map cannot hold both,
    so a caller comparing two extractor versions is comparing two runs.
    """
    versions: dict[str, str] = {}
    for record in runs:
        name, version = record["extractor_name"], record["extractor_version"]
        if versions.get(name, version) != version:
            raise ValueError(
                f"{name!r} appears at two versions, {versions[name]!r} and "
                f"{version!r}; section 8.5's tuple holds one version per extractor"
            )
        versions[name] = version
    return versions
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p5/test_p5_stage_output.py -v`
Expected: PASS — 13 passed

- [ ] **Step 5: Commit**

```bash
git add src/extractors/stage_output.py tests/p5/test_p5_stage_output.py
git commit -m "feat(P5): §8.5 envelope - abstention and budget deferral distinct, inputs is the content hash"
```

---

### Task 18: Re-extraction is additive — §8.2's supersession, §8.7's re-run, §8.8's plan independence

**Files:**
- Test: `tests/p5/test_p5_reextraction.py`

**Interfaces:**
- Consumes: every extractor above, `extractors.runs.cache_key`.
- Produces: the standing guarantee that a better extractor never destroys a worse one's record.

**Done-means 12, verbatim.** *"Re-extraction is additive. Running an improved extractor over
already-extracted content leaves both records readable, including both runs' `text_units`."*

**§8.2's own example is P5's.** *"A first OCR pass produces unreadable text, a later improved engine
recovers a university name, and both extraction records remain available. The resolver may mark the
newer value preferred, but a user inspecting a placement must still be able to reach the origin of the
conclusion."* That is the test below, run through E6 twice.

**P5 overwrites nothing — and owns no supersede column.** `supersedes`, `superseded_by` and
`supersede_reason` are **P4-assigned**; P5 supplies the *reason* through the sink's
`supersede_reason=` keyword and nothing else. P1's guarantee is what makes it work: *"Supersede-never-
overwrite is P1's guarantee and P5 relies on it: a second OCR pass must be able to land beside the
first."*

**§3.4's cache key is what makes the re-run warranted or free.** *"Content hash + extractor version +
`analysis_tier`, plus provider/version/configuration for OCR. This is what makes a rename free and a
content rewrite expensive, and what makes an extractor upgrade auditable."* There is **no path
parameter**, and that absence is the test: renaming a file changes no key, so nothing re-runs.

**§8.8 needs nothing from P5, and that is the point.** *"The evidence database remains shared across plan
versions."* No P5 record carries a plan id, a plan version or a template, so renaming Applications to
Admissions or restoring an earlier draft changes nothing P5 wrote. The guard is structural: no P5
function takes a plan argument and no P5 record has a plan field.

**§8.7's second obligation stays open.** *"Whether reclassification deletes or only gates P5's stored
observations — and the `text_units` they point into — is Open question 6."* P5 therefore publishes **no
deletion of any kind**: not a delete, not a purge, not a redaction. Answering OQ6 in code would be P5
settling a privacy question §8.4 gives to P7.

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_reextraction.py
"""Done-means 12 — §8.2 supersession, §8.7's re-run on demand, §8.8's plan
independence, and SPEC Open question 6 held open."""
import importlib
import inspect
from pathlib import Path

import pytest

import extractors
from extractors.ocr import OcrOutput, OcrRegion, extract_ocr
from extractors.reading import StructuredString
from extractors.runs import cache_key
from extractors.safety import SafetyPolicy
from extractors.shape import fingerprint

from conftest import FIXED_CLOCK

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
FILE_ROW = {"file_id": "f-scan", "content_hash": "sha256:scan",
            "filename": "transcript-scan.pdf"}
CONFIG = {"recognition": "accurate", "languages": ["en-US"]}

GARBLED = "Ui1iversity 0f Cl1icago"
RECOVERED = "University of Chicago"

SOURCE_DIR = Path(extractors.__file__).parent


def p5_modules():
    return [importlib.import_module(f"extractors.{path.stem}")
            for path in sorted(SOURCE_DIR.glob("*.py")) if path.stem != "__init__"]


def find_university(text: str):
    at = text.find("University of Chicago")
    return (StructuredString(kind="identifier", start=at, end=at + 21),) if at != -1 else ()


def an_ocr_pass(*, text, provider_version, path="/corpus/transcript-scan.pdf"):
    output = OcrOutput(provider="apple-vision", provider_version=provider_version,
                       regions=(OcrRegion(page=1, region=1, text=text,
                                          confidence=0.5),),
                       pages_processed=1, pages_total=1)
    return extract_ocr(file_row=FILE_ROW, path=Path(path), policy=OPEN_POLICY,
                       ocr_engine=lambda target, *, config: output, config=CONFIG,
                       find_structured_strings=find_university, now=FIXED_CLOCK,
                       context_window=20)


def test_section_8_2s_own_example_both_records_remain_available(sink):
    first = sink.write(an_ocr_pass(text=GARBLED, provider_version="18.0"))
    second = sink.write(an_ocr_pass(text=RECOVERED, provider_version="19.1"),
                        supersede_reason="a later engine recovered readable text")

    assert first != second
    assert [r["run_id"] for r in sink.runs] == [first, second]
    assert sink.run_for(first)["extractor_version"] == "18.0"
    assert sink.run_for(second)["extractor_version"] == "19.1"
    # The first pass's unreadable text is still reachable.
    assert sink.units_for(first)[0]["text"] == GARBLED
    assert sink.units_for(second)[0]["text"] == RECOVERED
    # And the recovered university name exists only on the second.
    assert [o["raw_value"] for o in sink.observations_for(first)] == []
    assert [o["raw_value"] for o in sink.observations_for(second)] == [RECOVERED]
    sink.conforms()


def test_both_runs_text_units_survive(sink):
    # Done-means 12, in G1's terms: bulk text has one home PER RUN, not one home
    # per file that a re-run overwrites.
    first = sink.write(an_ocr_pass(text=GARBLED, provider_version="18.0"))
    second = sink.write(an_ocr_pass(text=RECOVERED, provider_version="19.1"))
    assert len(sink.text_units) == 2
    assert {u["run_id"] for u in sink.text_units} == {first, second}


def test_p5_supplies_the_reason_and_sets_no_supersede_column(sink):
    reason = "a later engine recovered readable text"
    run_id = sink.write(an_ocr_pass(text=RECOVERED, provider_version="19.1"),
                        supersede_reason=reason)
    assert sink.supersessions == [(run_id, reason)]
    for observation in sink.observations:
        for column in ("supersedes", "superseded_by", "supersede_reason",
                       "preferred"):
            assert column not in observation, column


def test_an_extractor_upgrade_changes_the_cache_key():
    keys = {cache_key(content_hash="sha256:scan", extractor_name="ocr.apple-vision",
                      extractor_version=version, analysis_tier="ocr",
                      config_fingerprint=fingerprint(CONFIG))
            for version in ("18.0", "19.1")}
    assert len(keys) == 2


def test_a_rename_is_free():
    # §3.4: there is no path in the key, and that absence IS the guarantee.
    assert "path" not in inspect.signature(cache_key).parameters
    moved = an_ocr_pass(text=RECOVERED, provider_version="19.1",
                        path="/corpus/renamed/somewhere-else.pdf")
    stayed = an_ocr_pass(text=RECOVERED, provider_version="19.1")
    key = lambda result: cache_key(
        content_hash=result.run["content_hash"],
        extractor_name=result.run["extractor_name"],
        extractor_version=result.run["extractor_version"],
        analysis_tier=result.run["analysis_tier"],
        config_fingerprint=result.run["config_fingerprint"])
    assert key(moved) == key(stayed)


def test_a_configuration_change_makes_the_re_run_auditable():
    keys = set()
    for languages in (["en-US"], ["en-US", "ja-JP"]):
        config = dict(CONFIG, languages=languages)
        keys.add(cache_key(content_hash="sha256:scan",
                           extractor_name="ocr.apple-vision",
                           extractor_version="19.1", analysis_tier="ocr",
                           config_fingerprint=fingerprint(config)))
    assert len(keys) == 2


def test_no_p5_record_and_no_p5_function_knows_about_a_plan():
    # §8.8: "The evidence database remains shared across plan versions."
    for module in p5_modules():
        for name, value in vars(module).items():
            if name.startswith("__"):
                continue
            assert "plan" not in name.lower(), f"{module.__name__}.{name}"
            if inspect.isfunction(value) and value.__module__ == module.__name__:
                parameters = inspect.signature(value).parameters
                assert not [p for p in parameters if "plan" in p.lower()], name


def test_p5_publishes_no_deletion_of_any_kind():
    # SPEC Open question 6 is OPEN: whether reclassifying a file as private deletes
    # P5's stored observations and their text units, or only gates them, is §8.4's
    # to settle and P7's to own. P5 answers it nowhere.
    for module in p5_modules():
        for name, value in vars(module).items():
            if name.startswith("__") or not callable(value):
                continue
            for token in ("delete", "purge", "redact", "erase", "overwrite",
                          "scrub"):
                assert token not in name.lower(), f"{module.__name__}.{name}"


def test_re_extraction_needs_nothing_but_the_call():
    # §8.7's first obligation: P5 can be re-run over already-extracted content at any
    # time. Every extractor is a pure function of its arguments — no run registry, no
    # "already extracted" check, nothing to reset.
    parameters = inspect.signature(extract_ocr).parameters
    assert not {"force", "overwrite", "reextract", "if_changed"} & set(parameters)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_reextraction.py -v`
Expected: FAIL if any prior task is incomplete; otherwise PASS. This task adds no module — it is the standing guarantee the earlier tasks must keep true.

- [ ] **Step 3: Fix whatever the guard catches**

No new module. If a guard fires, the fix is in the module that tripped it. The one legitimate change to the guard is narrowing a token that proves to be a false positive against a design quotation — never deleting the test.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p5/test_p5_reextraction.py -v`
Expected: PASS — 9 passed

- [ ] **Step 5: Commit**

```bash
git add tests/p5/test_p5_reextraction.py
git commit -m "test(P5): re-extraction is additive, both records readable, no deletion anywhere"
```

---

### Task 19: The one-shape guard — no consumer can tell which extractor produced an observation

**Files:**
- Test: `tests/p5/test_p5_one_shape.py`

**Interfaces:**
- Consumes: all eight producers — O5's `filesystem`, E1–E6.
- Produces: §2.8's whole claim, as a test that fails the moment any extractor grows a field of its own.

**§2.8 is one sentence and this task is its proof.** *"Every extractor must emit the same evidence shape
— file identity, content hash, extractor and version, source type, raw value, normalized candidate,
location, context, occurrence count, and reliability state — so downstream logic can work consistently
across formats."* SPEC Done-means 2 turns it into something checkable: *"A consumer written against P4's
shape reads PDF, DOCX, image, archive and OCR observations through one code path with no per-format
branch."*

**The claim this task proves, exactly.** Blind an observation's `extractor_name`, `extractor_version` and
`source_type`, and **nothing left in the record identifies which extractor produced it**. That is
stronger than "the fields match": it forbids a private field, a zone only one extractor uses as a
marker, and a nullable field one extractor quietly repurposes as a flag.

**Two fields are legitimately scoped, and both are scoped by the *declared source type*.** P4's
conformance rule 11 scopes `signal_tier` to §2.6's images, and §2.7 puts OCR confidence on the
observation. A consumer reading either is reading **by source type**, which §2.8 publishes for exactly
that purpose — not by extractor. The test states that as a closed exemption list of two and fails if a
third appears.

**Done-means 3 and 11 ride along.** *"Raw is retained separately from normalized. A document saying `U
Chicago` keeps that exact wording as the raw value regardless of what any resolver later does with
it."* And *"Same content hash + same extractor version → identical observation set, so a P2 replay
bundle produces a comparable diff."* P4's conformance rule 8 is a property of **two runs**, which is why
it lives here and not in `p4_stub.py`.

**Why this test is the one that would catch the defect this part is most likely to ship.** Each of the
six extractors was written on its own and reviewed on its own. The failure mode is not a bad extractor
— it is six good extractors that agree on nine fields and disagree on the tenth, discovered by P6 six
weeks later. Every producer runs here, in one file, against one assertion.

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_one_shape.py
"""§2.8's whole claim. Done-means 2, 3 and 11.

"Every extractor must emit the same evidence shape ... so downstream logic can work
consistently across formats."
"""
from pathlib import Path

import pytest

from extractors.archive import ArchiveManifest, ArchiveMember, extract_archive
from extractors.docx import DocxCell, DocxDocument, DocxParagraph, extract_docx
from extractors.filesystem import extract_filesystem
from extractors.image import ExifValue, ImageRecord, extract_image
from extractors.long_tail import (
    LongTailEntry, LongTailFile, LongTailText, LongTailValue, extract_long_tail,
)
from extractors.ocr import OcrOutput, OcrRegion, extract_ocr
from extractors.pdf import PdfDocument, PdfPage, extract_pdf
from extractors.reading import Region, StructuredString
from extractors.safety import SafetyPolicy
from extractors.shape import LOCATION_FIELDS, OBSERVATION_FIELDS
from extractors.structured_text import TextDocument, extract_structured_text

from conftest import FIXED_CLOCK
from p4_stub import locator_for, observation_key

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
FILE_ROW = {"file_id": "f-1", "content_hash": "sha256:one",
            "filename": "U Chicago admission.pdf",
            "normalized_filename": "u chicago admission.pdf", "extension": ".pdf",
            "mime_type": "application/pdf", "directory_position": "/corpus/apps"}
PATH = Path("/corpus/apps/U Chicago admission.pdf")

#: §2.8's own example of a value that must survive verbatim.
RAW = "U Chicago"

#: P4 scopes exactly two observation fields to a source type: conformance rule 11
#: scopes `signal_tier` to §2.6's images, and §2.7 puts OCR confidence on the
#: observation. Both are read through the DECLARED source type, which is what §2.8
#: publishes it for. A third entry here would be a new per-format branch.
SOURCE_TYPE_SCOPED = {"signal_tier": {"image"}, "confidence": {"ocr"}}

NULLABLE = ("normalized_value", "confidence", "signal_tier")


def find_raw(text: str):
    at = text.find(RAW)
    return (StructuredString(kind="identifier", start=at, end=at + len(RAW)),) if at != -1 else ()


def producers():
    """One call per producer, each over a fixture containing the same raw value."""
    common = dict(file_row=FILE_ROW, path=PATH, policy=OPEN_POLICY,
                  now=FIXED_CLOCK, context_window=16)

    yield "filesystem", lambda: extract_filesystem(**common)

    yield "pdf", lambda: extract_pdf(
        read_pdf=lambda target: PdfDocument(
            metadata={"Title": f"{RAW} supplement"},
            pages=(PdfPage(number=1, text=f"Applying to {RAW} this year.",
                           regions=(Region(zone="heading", start=0, end=11,
                                           ordinal=1, label="Applying to"),)),)),
        find_structured_strings=find_raw, **common)

    yield "docx", lambda: extract_docx(
        read_docx=lambda target: DocxDocument(
            core_properties={"creator": "python-docx"},
            paragraphs=(DocxParagraph(index=1, text=f"Why {RAW}?", zone="heading",
                                      heading_path=((1, "Why"),)),),
            cells=(DocxCell(table=1, row=1, column=1, text=RAW),)),
        find_structured_strings=find_raw, **common)

    yield "structured_text", lambda: extract_structured_text(
        source_type="text_document",
        read_text_document=lambda target: TextDocument(
            text=f"Notes on {RAW}.", language="Markdown"),
        find_structured_strings=find_raw, **common)

    yield "long_tail", lambda: extract_long_tail(
        source_type="email",
        read_long_tail=lambda target, *, transcribe: LongTailFile(
            entries=(LongTailEntry(kind="entry", label="<m-1@x>"),),
            values=(LongTailValue(name="Subject", value=RAW, entry_ordinal=1),),
            texts=(LongTailText(zone="body", text=f"About {RAW}.", entry_ordinal=1,
                                region=1),)),
        find_structured_strings=find_raw, transcription_authorized=lambda: False,
        **common).extraction

    yield "archive", lambda: extract_archive(
        read_manifest=lambda target: ArchiveManifest(
            archive_type="ZIP", members=(ArchiveMember(path=f"{RAW}/essay.docx"),),
            inspected=1, total=1),
        recognize_markers=lambda paths: (), **common)

    yield "image", lambda: extract_image(
        read_image=lambda target: ImageRecord(
            image_format="HEIC", dimensions="4032x3024", width=4032, height=3024,
            perceptual_hash="phash:1",
            exif=(ExifValue(name="Make", value="Apple", kind="camera EXIF"),)),
        dimension_signal=lambda width, height: None,
        filename_pattern=lambda name: None, **common)

    yield "ocr", lambda: extract_ocr(
        ocr_engine=lambda target, *, config: OcrOutput(
            provider="apple-vision", provider_version="19.1",
            regions=(OcrRegion(page=1, region=1, text=f"Admitted to {RAW}.",
                               confidence=0.9),),
            pages_processed=1, pages_total=1),
        config={"recognition": "accurate"}, find_structured_strings=find_raw,
        **common)


def every_observation():
    for name, call in producers():
        for observation in call().observations:
            yield name, observation


def test_every_producer_emits_at_least_one_observation():
    produced = {name for name, _ in every_observation()}
    assert produced == {"filesystem", "pdf", "docx", "structured_text", "long_tail",
                        "archive", "image", "ocr"}


def test_there_is_exactly_one_observation_shape():
    shapes = {tuple(observation) for _, observation in every_observation()}
    assert shapes == {OBSERVATION_FIELDS}


def test_no_extractor_has_a_field_of_its_own():
    keys = set()
    for _, observation in every_observation():
        keys |= set(observation)
    assert keys == set(OBSERVATION_FIELDS)


def test_there_is_exactly_one_location_shape():
    shapes = {tuple(observation["location"])
              for _, observation in every_observation()}
    assert shapes == {LOCATION_FIELDS}


def test_one_consumer_reads_every_observation_with_no_per_format_branch():
    # Done-means 2. This function is the consumer: it names no extractor, no format
    # and no source type, and it works on all eight.
    def cite(observation):
        return (f"{observation['raw_value']} at "
                f"{locator_for(observation['location'])} "
                f"({observation['reliability']}, x{observation['occurrence_count']})")

    citations = [cite(observation) for _, observation in every_observation()]
    assert len(citations) == len(list(every_observation()))
    assert all(citation.strip() for citation in citations)
    assert len(set(citations)) > 20      # they are distinct, not a constant


def test_blinding_the_three_declared_fields_hides_the_producer():
    # The claim: with `extractor_name`, `extractor_version` and `source_type`
    # removed, no remaining field identifies which extractor wrote the row.
    by_field: dict[str, set[str]] = {}
    for name, observation in every_observation():
        for field in NULLABLE:
            if observation[field] is not None:
                by_field.setdefault(field, set()).add(name)

    for field, producers_setting in by_field.items():
        if len(producers_setting) > 1:
            continue
        assert field in SOURCE_TYPE_SCOPED, (
            f"{field} is set by {producers_setting} alone and P4 does not scope it "
            "to a source type — that is a per-format branch"
        )


def test_the_two_scoped_fields_are_read_through_the_declared_source_type():
    for _, observation in every_observation():
        for field, allowed in SOURCE_TYPE_SCOPED.items():
            if observation[field] is not None:
                assert observation["source_type"] in allowed, field


def test_raw_survives_verbatim_in_every_producer_that_saw_it():
    # Done-means 3: "`U Chicago` keeps that exact wording as the raw value".
    carriers = {name for name, observation in every_observation()
                if observation["raw_value"] == RAW}
    assert {"pdf", "docx", "structured_text", "long_tail", "ocr"} <= carriers
    for name, observation in every_observation():
        if observation["raw_value"] == RAW:
            assert observation["normalized_value"] in (None, RAW), name


def test_every_producer_is_deterministic():
    # Done-means 11 / P4 conformance rule 8: a property of TWO runs, which is why it
    # is here and not in the per-observation validator.
    for name, call in producers():
        first, second = call(), call()
        assert first.observations == second.observations, name
        assert first.text_units == second.text_units, name
        assert first.run == second.run, name


def test_the_observation_key_is_stable_across_runs():
    for name, call in producers():
        keys = [tuple(observation_key(o) for o in call().observations)
                for _ in range(2)]
        assert keys[0] == keys[1], name


def test_every_producer_conforms_to_p4s_shape(sink):
    for _, call in producers():
        sink.write(call())
    sink.conforms()


def test_the_shared_fields_carry_the_per_format_difference():
    # The other half of §2.8: one shape does not mean one kind of content. The
    # difference lives in `zone` and `container_path`, which every consumer reads.
    zones = {observation["location"]["zone"]
             for _, observation in every_observation()}
    assert {"filename", "path", "metadata", "title", "heading", "table", "body",
            "manifest", "ocr"} <= zones
    kinds = {segment["kind"] for _, observation in every_observation()
             for segment in observation["location"]["container_path"]}
    assert {"field", "page", "heading", "table", "row", "column", "entry"} <= kinds
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_one_shape.py -v`
Expected: FAIL if any extractor emits a field of its own, a second location shape, or a non-deterministic value. If Tasks 1–18 were written as specified, it passes on the first run — and that is what it is for.

- [ ] **Step 3: Fix whatever the guard catches**

No new module. A failure here is fixed in the extractor that broke the shape, never by widening
`SOURCE_TYPE_SCOPED`: that dictionary has exactly two entries because P4 scopes exactly two fields, and
adding a third is the per-format branch §2.8 forbids.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p5/test_p5_one_shape.py -v`
Expected: PASS — 12 passed

- [ ] **Step 5: Commit**

```bash
git add tests/p5/test_p5_one_shape.py
git commit -m "test(P5): one shape - blinding name, version and source type hides the producer"
```

---

### Task 20: The no-invention guard — every open question held open, by introspection

**Files:**
- Test: `tests/p5/test_p5_no_invention.py`

**Interfaces:**
- Consumes: every module in `src/extractors/`.
- Produces: the standing guard the rest of the build must keep green.

**Two obligations, both negative.**

**Where the design leaves a value open, P5 holds a key or a caller-supplied strategy — never a number
and never a list.** The SPEC's *Deferred* table names nine such values: the tool-generated
producer/creator string list, the known screen resolutions, the sensor-shaped aspect ratios, the
camera-filename pattern library, repository markers and package manifests beyond §1.1's four, the
archive marker set, the OCR language configuration, the citation and identifier pattern sets, and every
numeric budget ceiling. **Not one of them exists in `src/extractors/`.**

**Every open question stays open.** Eight remain open in P5's SPEC (OQ3 closed as I4). Each gets a guard
below that names it and fails the moment someone answers it in an implementation instead of in a SPEC.

**Every guard here is runtime introspection of a module's namespace, never a search of source text.**
A source-text guard matches its own comments and the design quotations in its docstrings — `assert
"python-docx" not in source` fails against the very paragraph of §2.2 that E1's docstring quotes — and
that trap has broken four tasks on this project already. So these guards walk `vars(module)`, skip
dunder names (which is where `__doc__` lives), and inspect signatures.

**The strongest single guard is that P5 holds no number.** A threshold, a ceiling, a DPI, an aspect
ratio, a confidence cutoff and a page cap are all numbers, and there is no module-level number anywhere
in `extractors`. One assertion covers six Deferred rows and cannot be satisfied by a rename.

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_no_invention.py
"""The standing record that P5 answers no open question in code.

Every guard is RUNTIME INTROSPECTION. A source-text guard matches its own docstrings
— this file's own prose names `python-docx`, Apple Vision and 200 DPI, all of which
are design quotations — so nothing here reads a `.py` file.
"""
import importlib
import inspect
import re
import sqlite3
from pathlib import Path

import pytest

import extractors
from database_agent.db import create_schema
from database_agent.events import RESERVED_EVENT_TYPES

from extractors.archive import ArchiveManifest, extract_archive
from extractors.authorship import AUTHORED_EVENT_TYPES, SUBSYSTEM
from extractors.image import extract_image
from extractors.long_tail import POTENTIALLY_SENSITIVE, extract_long_tail
from extractors.ocr import extract_ocr
from extractors.ocr_policy import document_ocr_decision, text_layer_state
from extractors.pdf import extract_pdf
from extractors.router import SOURCE_TYPE_BY_FORMAT, route
from extractors.schema import create_extraction_schema
from extractors.shape import (
    ANALYSIS_TIERS, ForbiddenAnalysisTier, P5_ANALYSIS_TIERS, run,
)
from extractors.structured_text import extract_structured_text

SOURCE_DIR = Path(extractors.__file__).parent

#: The one module-level pattern P5 owns: P4 D8's "soft-hyphen/line-break repair",
#: which the design names as one of exactly four mechanical transforms.
MECHANICAL_REPAIR = ("extractors.shape", "_LINE_BREAK_HYPHEN")

RESOLUTION = re.compile(r"^\d+\s*[x×]\s*\d+$")
LANGUAGE_TAG = re.compile(r"^[a-z]{2}-[A-Z]{2}$")


def p5_modules():
    return [importlib.import_module(f"extractors.{path.stem}")
            for path in sorted(SOURCE_DIR.glob("*.py")) if path.stem != "__init__"]


def constants(module):
    """Module-level names and values, minus dunders — which is where `__doc__` is."""
    return {name: value for name, value in vars(module).items()
            if not name.startswith("__")}


def strings(value):
    """Every string reachable inside a module-level constant."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, (tuple, list, set, frozenset)):
        for item in value:
            yield from strings(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from strings(key)
            yield from strings(item)


def module_strings():
    for module in p5_modules():
        for name, value in constants(module).items():
            if (inspect.isclass(value) or inspect.isfunction(value)
                    or inspect.ismodule(value)):
                continue
            for text in strings(value):
                yield module.__name__, name, text


# --- the value guards -------------------------------------------------------

def test_p5_holds_no_number_anywhere():
    # One assertion for six Deferred rows: threshold, ceiling, DPI, aspect ratio,
    # confidence cutoff and page cap are all numbers, and P5 holds none.
    for module in p5_modules():
        for name, value in constants(module).items():
            assert not isinstance(value, (int, float)) or isinstance(value, bool), (
                f"{module.__name__}.{name} = {value!r}")


def test_the_only_pattern_p5_owns_is_p4_d8s_mechanical_repair():
    found = [(module.__name__, name) for module in p5_modules()
             for name, value in constants(module).items()
             if isinstance(value, re.Pattern)]
    assert found == [MECHANICAL_REPAIR]


def test_no_screen_resolution_no_language_tag_and_no_producer_string():
    # SPEC Deferred: "Known screen resolutions", "OCR language configuration", and
    # the "Tool-generated producer/creator string list".
    for module_name, name, text in module_strings():
        assert not RESOLUTION.match(text), f"{module_name}.{name} = {text!r}"
        assert not LANGUAGE_TAG.match(text), f"{module_name}.{name} = {text!r}"
        assert "python-docx" not in text, f"{module_name}.{name}"
        assert "Mozilla" not in text, f"{module_name}.{name}"


def test_the_marker_classes_hold_no_members():
    # SPEC Deferred: §1.1's four repository markers are P3's and "Everything else"
    # is unsettled; the archive marker set likewise. P5 holds the CLASS names §2.4
    # and §2.5 spell, and no file name.
    from extractors.archive import MARKER_KINDS
    from extractors.structured_text import STRUCTURAL_MARKER_KINDS
    for value in (*MARKER_KINDS, *STRUCTURAL_MARKER_KINDS):
        assert "." not in value, value
        assert "/" not in value, value


def test_p5_hashes_no_file_bytes():
    # O5. `hashlib` is bound in exactly one module and hashes a CONFIGURATION
    # mapping to produce P4's `config_fingerprint` — never a path, never a byte.
    binding = [module.__name__ for module in p5_modules()
               if getattr(constants(module).get("hashlib"), "__name__", "")
               == "hashlib"]
    assert binding == ["extractors.shape"]
    from extractors.shape import fingerprint
    parameters = inspect.signature(fingerprint).parameters
    assert list(parameters) == ["config"]
    with pytest.raises((TypeError, AttributeError)):
        fingerprint(Path("/corpus/anything.pdf"))


def test_p5_determines_no_mime_type():
    # SPEC OQ4 and §2.9: the real MIME type or signature comes from an injected
    # reader; P5 owns the routing TABLE and not the detection.
    for module in p5_modules():
        for name, value in constants(module).items():
            assert getattr(value, "__name__", "") not in ("mimetypes", "magic"), name
    assert (inspect.signature(route).parameters["detect_format"].default
            is inspect.Parameter.empty)


def test_there_is_no_global_language_quality_check():
    # §2.2: "The system should not use unreliable global language-quality checks that
    # incorrectly punish multilingual or mathematics-heavy documents." §2.7 repeats
    # it. The only input about a non-empty text layer is P6's verdict.
    for module in p5_modules():
        for name, value in constants(module).items():
            if not callable(value):
                continue
            for token in ("quality", "legible", "gibberish", "garbled",
                          "language_check", "readable_text"):
                assert token not in name.lower(), f"{module.__name__}.{name}"
    parameters = set(inspect.signature(text_layer_state).parameters)
    assert parameters == {"result", "file_id", "content_hash", "no_usable_facts"}


def test_p5_makes_no_model_call_and_writes_no_llm_tier():
    # I4 and §3.3. "P5 contains no model call of any kind."
    assert ANALYSIS_TIERS == ("filesystem", "native", "ocr", "llm")
    assert P5_ANALYSIS_TIERS == ("filesystem", "native", "ocr")
    with pytest.raises(ForbiddenAnalysisTier):
        run(file_id="f", content_hash="h", extractor_name="x", extractor_version="1",
            source_type="image", analysis_tier="llm", config={},
            completeness="complete", coverage={"units": "files", "processed": 1,
                                               "total": 1},
            observation_count=0, started_at="t", finished_at="t")
    for module in p5_modules():
        for name, value in constants(module).items():
            if not callable(value):
                continue
            for token in ("llm", "model_", "_model", "embedding", "dossier"):
                assert token not in name.lower(), f"{module.__name__}.{name}"


def test_subsystem_is_set_in_exactly_one_module():
    # M8: the acting part authors and P1 writes. There is one place that value lives.
    holders = [module.__name__ for module in p5_modules()
               if constants(module).get("SUBSYSTEM") == SUBSYSTEM]
    assert holders == ["extractors.authorship"]


def test_p5_registers_no_event_type():
    # B5 rule 4: registration is a spec-level act, and both P5 types are already
    # reserved §8.2 names in P1's frozen table.
    assert set(AUTHORED_EVENT_TYPES) <= RESERVED_EVENT_TYPES


def test_p5_creates_none_of_p4s_three_tables(conn):
    create_schema(conn)
    create_extraction_schema(conn)
    tables = {row["name"] for row in
              conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert {"extraction_routing", "extraction_sensitivity_signal"} <= tables
    assert not {"evidence", "extraction_runs", "text_units"} & tables


# --- one guard per open question --------------------------------------------

def test_oq1_the_no_usable_facts_threshold_is_not_answered_here():
    # OQ1: "§2.2 and §2.7 define the trigger in terms of facts and the design never
    # says how few facts is 'no usable facts'. It is a deferred configuration value."
    parameter = inspect.signature(document_ocr_decision).parameters["no_usable_facts"]
    assert parameter.default is inspect.Parameter.empty
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    import extractors.ocr_policy as policy
    assert not [n for n, v in constants(policy).items()
                if isinstance(v, (int, float)) and not isinstance(v, bool)]


def test_oq2_the_formats_section_2_9_lists_twice_still_have_two_candidates():
    # OQ2: "CSV appears under both Spreadsheets and Code/structured data; PDF appears
    # under both Text documents and Presentations. The design specifies different
    # field lists for each and no tiebreak."
    assert len(SOURCE_TYPE_BY_FORMAT["csv"]) == 2
    assert len(SOURCE_TYPE_BY_FORMAT["pdf"]) == 2
    decision = route(file_id="f", content_hash="h", path=Path("/corpus/a.csv"),
                     extension=".csv", detect_format=lambda target: "csv")
    # The candidates are recorded rather than discarded, and the operative one is
    # §2.9's own document order — not a preference of P5's.
    assert decision.source_type_candidates == SOURCE_TYPE_BY_FORMAT["csv"]
    assert decision.source_type == SOURCE_TYPE_BY_FORMAT["csv"][0]


def test_oq3_is_closed_and_stays_closed():
    # I4, ratified 2026-08-19: the four tiers are closed and P5 writes the first
    # three. This guard exists so a later edit cannot quietly re-open it.
    assert ANALYSIS_TIERS == ("filesystem", "native", "ocr", "llm")
    assert "llm" not in P5_ANALYSIS_TIERS


def test_oq4_every_library_and_engine_choice_is_a_required_keyword():
    # OQ4: "The design names Apple Vision for macOS OCR and names no library for PDF,
    # DOCX, HEIC, archives, spreadsheets, presentations, email, calendar, contacts,
    # audio/video, or design formats."
    required = {
        extract_pdf: ("read_pdf", "find_structured_strings"),
        extract_structured_text: ("read_text_document", "find_structured_strings"),
        extract_long_tail: ("read_long_tail", "find_structured_strings",
                            "transcription_authorized"),
        extract_archive: ("read_manifest", "recognize_markers"),
        extract_image: ("read_image", "dimension_signal", "filename_pattern"),
        extract_ocr: ("ocr_engine", "config", "find_structured_strings"),
    }
    for function, names in required.items():
        parameters = inspect.signature(function).parameters
        for name in names:
            assert parameters[name].default is inspect.Parameter.empty, name
            assert parameters[name].kind is inspect.Parameter.KEYWORD_ONLY, name


def test_oq5_spreadsheets_and_presentations_are_the_callers_release_decision(sink):
    # OQ5: "§2.4 explicitly permits either; §2.9 specifies full field lists for both.
    # Which is a release-scope decision the design leaves open."
    result = extract_long_tail(
        file_row={"file_id": "f", "content_hash": "h", "filename": "x.xlsx"},
        path=Path("/corpus/x.xlsx"),
        policy=__import__("extractors.safety", fromlist=["SafetyPolicy"]).SafetyPolicy(
            is_protected_container=lambda p: False, is_dataless=lambda p: False),
        source_type="spreadsheet", read_long_tail=lambda p, *, transcribe: None,
        find_structured_strings=lambda text: (),
        transcription_authorized=lambda: False, now="t", context_window=1)
    assert result.extraction.run["completeness"] == "unsupported"
    for module_name, name, text in module_strings():
        assert "launch" not in text.lower(), f"{module_name}.{name}"


def test_oq6_ratified_p5_holds_no_privacy_or_gating_vocabulary():
    # OQ6 CLOSED, ratified 2026-08-20: GATE by default, with an explicit
    # user-initiated delete. Both halves belong elsewhere — the gate is P7's handling
    # class, the delete surface is P13's — and "P5 publishes no deletion" is now a
    # ratified requirement rather than a question being held open. Same assertions,
    # stronger standing: P5 neither deletes (guarded in test_p5_reextraction.py)
    # nor gates.
    for module in p5_modules():
        for name in constants(module):
            for token in ("private", "gated", "gate_", "quarantine", "consent"):
                assert token not in name.lower(), f"{module.__name__}.{name}"


def test_oq7_there_is_one_sensitivity_value_and_no_handling_class():
    # OQ7: "§2.9 requires email addresses, message content and VCF output be treated
    # as potentially sensitive; §8.4 puts handling-class assignment in P7. The
    # boundary between 'P5 flags' and 'P7 classifies' is unstated."
    assert isinstance(POTENTIALLY_SENSITIVE, str)
    for module in p5_modules():
        for name in constants(module):
            for token in ("handling_class", "sensitivity_state", "classify",
                          "HANDLING"):
                assert token not in name, f"{module.__name__}.{name}"


def test_oq8_no_nested_manifest_is_read():
    # OQ8: "May a nested archive's manifest be read one level down, in memory? §2.5
    # lists nested archives among those marked unreadable or partially inspected, but
    # reading an inner manifest without unpacking is not the same act as extraction,
    # and the design does not distinguish them."
    fields = set(inspect.signature(ArchiveManifest).parameters)
    assert not {"nested", "inner", "nested_manifests", "children"} & fields
    readers = [name for name in inspect.signature(extract_archive).parameters
               if name.startswith("read_")]
    assert readers == ["read_manifest"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_no_invention.py -v`
Expected: FAIL — collection succeeds and any guard whose forbidden value is present fails. If every prior task was written as specified, the only expected failures are ones this task exists to surface.

- [ ] **Step 3: Fix whatever the guard catches**

No new module. If a guard fires, the fix is in the module that tripped it, never in the guard: the guard is the SPEC's negative half. The one legitimate change is **narrowing** a token that proves to be a false positive against a design-named value — for instance `budgets.P5_CEILING_KEYS` legitimately *names* §8.6's ceilings, which is why the ceiling guard here is about **values** (`test_p5_holds_no_number_anywhere`) and never about names. Narrow; do not delete.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p5/test_p5_no_invention.py -v`
Expected: PASS — 19 passed

- [ ] **Step 5: Commit**

```bash
git add tests/p5/test_p5_no_invention.py
git commit -m "test(P5): no-invention guard, every open question held open by introspection"
```

---

### Task 21: The walking-skeleton P5 step

**Files:**
- Test: `tests/p5/test_p5_skeleton_step.py`

**Interfaces:**
- Consumes: everything above, plus P1's real `files` row, real event log and real database handle.
- Produces: the integration test every later part must keep green.

**[`../../02-segmentation-map.md`](../../02-segmentation-map.md)'s P5 slice, verbatim:** *"P4/P5 —
extract page-one text; emit ONE observation in the frozen shape."*

The same document states the order this test sits in: *"Wave 2 understanding — P4 → P5 → P6
(deterministic only, no model)"*, and *"P4 before P5. §2.8, as above."* So this test is deterministic by
construction: no model, no cloud, no embeddings, no network. It is P5's counterpart to P1's
`test_skeleton_p1_step` and P3's `test_p3_skeleton_step`.

**It runs against P1 as built.** A real fixture file under `tmp_path`, a real `files` row through P1's
`record_file` — which takes **`parent_folder_context`** as its keyword and stores it in the
`directory_position` column, MINOR 11 exactly as the Global Constraints describe it — a real
`extraction` event through P1's writer, and P5's routing decision in P1's database. The only stand-in is
the sink, because `evidence`, `extraction_runs` and `text_units` are P4's tables and P4 has not landed;
when it does, `RecordingSink` becomes P4's writer and this test does not change.

**ONE observation is the assertion, and the fixture is built to make it exact.** A one-page PDF with no
metadata slots, one heading region and no structured strings produces exactly one observation — the
heading — plus two text units (the page, and the heading the span indexes into) and one run. If a later
change makes E1 emit a second row for that fixture, this test says so.

- [ ] **Step 1: Write the failing test**

```python
# tests/p5/test_p5_skeleton_step.py
"""The walking skeleton's P5 step (02-segmentation-map.md):
P4/P5 extract page-one text; emit ONE observation in the frozen shape.

This test stays in the repository as the integration test every later part must keep
green. It is deterministic: no model, no cloud, no embeddings, no network.
"""
import json
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file

from extractors.events import EXTRACTION, append, extraction_event
from extractors.pdf import EXTRACTOR_NAME, PdfDocument, PdfPage, extract_pdf
from extractors.reading import Region
from extractors.router import record_routing_decision, route, routing_decisions
from extractors.safety import SafetyPolicy
from extractors.schema import create_extraction_schema
from extractors.shape import EXTRACTOR_RELIABILITY
from extractors.stage_output import STAGE_ID, extraction_stage_output

from conftest import FIXED_CLOCK
from p4_stub import locator_for, validate_observation, validate_run

PAGE_ONE = "BUSIB 4300 Syllabus\nSpring 2026. Meetings on Tuesdays."
HEADING = "BUSIB 4300 Syllabus"

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)


def a_one_page_pdf(path: Path) -> PdfDocument:
    """No metadata slots and no structured strings, so the page yields exactly one
    located value: its heading."""
    return PdfDocument(
        metadata={},
        pages=(PdfPage(number=1, text=PAGE_ONE,
                       regions=(Region(zone="heading", start=0, end=len(HEADING),
                                       ordinal=1, label=HEADING),)),))


def test_skeleton_p5_step(conn, tmp_path: Path, sink):
    create_schema(conn)
    create_extraction_schema(conn)

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    document = corpus / "Syllabus BUSIB 4300 Spring 2026.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")

    # P1's real row, as P3 would have handed it over. `parent_folder_context` is
    # §2.9's name for the value P1 stores in `directory_position` (MINOR 11).
    file_id = record_file(
        conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(corpus), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=True)
    file_row = dict(get_file(conn, file_id))
    assert file_row["directory_position"] == str(corpus)

    # R — §2.9 routes by signature, and the decision is recorded.
    decision = route(file_id=file_id, content_hash=file_row["content_hash"],
                     path=document, extension=".pdf",
                     detect_format=lambda target: "pdf")
    assert decision.extractor_name == EXTRACTOR_NAME
    assert decision.disagree is False
    record_routing_decision(conn, decision)
    assert len(routing_decisions(conn, file_id, file_row["content_hash"])) == 1

    # E1 — page-one text, and ONE observation in the frozen shape.
    result = extract_pdf(file_row=file_row, path=document, policy=OPEN_POLICY,
                         read_pdf=a_one_page_pdf,
                         find_structured_strings=lambda text: (), now=FIXED_CLOCK,
                         context_window=24)
    run_id = sink.write(result)

    observations = sink.observations_for(run_id)
    assert len(observations) == 1
    only = observations[0]
    assert only["raw_value"] == HEADING
    assert locator_for(only["location"]) == "heading:page=1/heading=1#0-19"
    assert only["reliability"] in EXTRACTOR_RELIABILITY
    assert only["file_id"] == file_id
    assert only["content_hash"] == file_row["content_hash"]

    # It validates against P4's frozen shape, through P4's own conformance rules.
    units = [{k: v for k, v in u.items() if k != "run_id"}
             for u in sink.units_for(run_id)]
    validate_observation({k: v for k, v in only.items() if k != "run_id"},
                         text_units=units)
    validate_run(sink.run_for(run_id), 1)

    # Page-one text is a `text_units` row, not an observation (G1).
    page = [u for u in units if u["container_path"]
            == ({"kind": "page", "index": 1, "label": None},)]
    assert page and page[0]["text"] == PAGE_ONE
    assert all(o["raw_value"] != PAGE_ONE for o in observations)

    # Deterministic: the native tier, no model, no network.
    row = sink.run_for(run_id)
    assert row["analysis_tier"] == "native"
    assert row["completeness"] == "complete"
    assert row["coverage"] == {"units": "pages", "processed": 1, "total": 1}

    # P5 authors the extraction event; P1 writes it (M8).
    append(conn, extraction_event(
        run_id=run_id, file_id=file_id, content_hash=file_row["content_hash"],
        extractor_name=row["extractor_name"],
        extractor_version=row["extractor_version"],
        completeness=row["completeness"], observed_at=FIXED_CLOCK))
    event = conn.execute("SELECT * FROM events WHERE event_type = ?",
                         (EXTRACTION,)).fetchone()
    assert event["subsystem"] == "P5"
    assert json.loads(event["explanation"])["run_id"] == run_id

    # And the run is measurable (§8.5, B7).
    envelope = extraction_stage_output(run=row)
    assert envelope["stage_id"] == STAGE_ID
    assert envelope["outcome"] == "produced"
    assert envelope["inputs"] == (file_row["content_hash"],)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p5/test_p5_skeleton_step.py -v`
Expected: FAIL if any prior task is incomplete; otherwise PASS.

- [ ] **Step 3: Run the full suite one final time**

Run: `pytest -v --tb=short`
Expected: PASS — every P5 test from Tasks 1–21 green, and every P1, P2 and P3 test still green (P5 modified no file belonging to another part).

- [ ] **Step 4: Commit**

```bash
git add tests/p5/test_p5_skeleton_step.py
git commit -m "test(P5): walking-skeleton P5 step, page-one text and ONE observation in the frozen shape"
```

---

## Self-Review

**Spec coverage.** Every Contract-out record has a task. The **routing decision per file** → Task 4.
**Observations, `text_units` and `extraction_runs`** → Tasks 2 and 5 for the shape and the outcome
record, Tasks 6–14 for the eight producers. **Events (§8.2)** → Tasks 1 and 16. **P2's `stage_output`
(§8.5, B7)** → Task 17. P5's two own tables → Tasks 4 (routing) and 11 (sensitivity signal), both created
by `schema.create_extraction_schema` and nowhere else.

The six extractor families the SPEC names map one-to-one onto modules and tasks: **E1 PDF (§2.2)** →
Task 7 · **E2 DOCX (§2.3)** → Task 9 · **E3 structured text and code (§2.4, §2.9)** → Tasks 10 and 11 ·
**E4 archives (§2.5)** → Task 12 · **E5 images (§2.6)** → Task 13 · **E6 OCR (§2.7)** → Task 14, with
Task 8 deciding when E6 may run. **R the router (§2.9)** → Task 4. **O5's filesystem re-emission** →
Task 6.

Done-means 1–13 map as: 1→T4/T5/T6/T10 · 2→T2/T19 · 3→T2/T19 · 4→T7 · 5→T8/T20 · 6→T9 · 7→T12 · 8→T13 ·
9→T14 · 10→T4/T10/T11 · 11→T19 · 12→T18 · 13→T2/T7/T10/T14/T19.

**Authorship.** P5 authors and P1 writes, everywhere. `authorship.event_defaults` (Task 1) is the single
place `subsystem` is set, it refuses any value but `"P5"`, and it refuses a type P5 does not author.
Task 20's `test_subsystem_is_set_in_exactly_one_module` fails if a second route appears. Both types —
`extraction` and **`OCR`** (MINOR 2) — are reserved §8.2 names already in P1's frozen table, so **P5
registers nothing** (B5 rule 4) and Task 16 asserts it against P1's live `RESERVED_EVENT_TYPES`.

**No invention.** There is **no module-level number anywhere in `extractors`** — Task 20 asserts it by
walking every module's namespace — which discharges six Deferred rows at once: the numeric budget
ceilings, the OCR DPI, the sensor-shaped aspect ratios, the no-usable-facts threshold, the archive size
ceiling and any confidence cutoff. There is exactly **one** module-level regex, `shape._LINE_BREAK_HYPHEN`,
which is P4 D8's named mechanical transform. No screen resolution, no language tag, no producer string
and no marker file name exists in any module-level container.

**Open questions this plan does not answer.** **OQ1** (no-usable-facts threshold) — `no_usable_facts` is
a keyword-only parameter with no default and `ocr_policy` holds no number. **OQ2** (CSV and PDF listed
twice) — both keep two `source_type` candidates, the decision records the candidates, and the operative
one is §2.9's own document order rather than a preference of P5's. **OQ3** — closed as **I4** and guarded
so it stays closed. **OQ4** (library and engine choices) — every reader is a keyword-only parameter with
no default, in all six extractors. **OQ5** (spreadsheets and presentations at launch) — a reader
returning `None` produces `unsupported`; nothing in P5 decides. **OQ6** (private reclassification
deletes or gates) — P5 publishes no deletion (Task 18) and no gating vocabulary (Task 20). **OQ7** (P5
flags vs P7 classifies) — one signal value, `POTENTIALLY_SENSITIVE`, and `handling_class` appears
nowhere. **OQ8** (nested archive manifest) — `ArchiveManifest` has no nested field and `extract_archive`
takes exactly one reader. **P5 OQ1 and OQ2 as this plan's header states them are CLOSED** and stay
closed: `Location` is P4's structured record, and OCR's provider, config, languages, confidence and
capped flag are on `extraction_runs`, asserted by Task 14.

**The guard-token trap, handled.** Every guard in Tasks 18, 19 and 20 is **runtime introspection** of a
module's namespace with dunder names skipped — which is where `__doc__` lives. This file's own prose
quotes `python-docx`, Apple Vision and 200 DPI, all of them design quotations; a source-text guard would
fail on the sentence it exists to enforce. It cost one real failure during construction
(`test_the_provider_is_the_engines_and_p5_spells_none` matched `ocr.__doc__`) and the fix was to scope
the guard, not to soften it.

**Test filenames.** Checked against `tests/`, `tests/eval/` and `tests/p3/` as they stand: **no
`test_p5_*.py` basename collides with any existing test file.** `tests/p5/conftest.py` shares a basename
with three other conftests, which pytest special-cases — `tests/p3/conftest.py` already coexists with
`tests/conftest.py` and `tests/eval/conftest.py` in a green suite. **`tests/p5/__init__.py` is therefore
not created, and must not be**: under prepend import mode pytest inserts a conftest's own directory on
`sys.path` only when that directory is not a package, and `tests/p5/conftest.py` and every test file
import `p4_stub` as a top-level module.

**Corrections made to earlier sections.** One, recorded rather than made silently: the Global Constraints
bullet on O5 read *"P5 hashes nothing — `hashlib` does not appear in `src/extractors/`"*, which Task 2's
own `shape.fingerprint` contradicts — it hashes a **configuration mapping** to produce P4's
`config_fingerprint`, and P4 requires that. The rule was always about **file bytes**; the clause now says
so, and Task 20's `test_p5_hashes_no_file_bytes` asserts the true form (`hashlib` bound in exactly one
module, `fingerprint` taking a mapping and refusing a `Path`). Tasks 1–9 are otherwise untouched.

**Placeholder scan.** No "TBD", no "add error handling", no "similar to Task N", no angle-bracket
placeholder standing in for a real name. Every code step carries complete runnable code; every test step
names the exact `pytest` command and the expected count.

**Type consistency.** All eight producers take the same five keywords with the same spellings —
`file_row`, `path`, `policy`, `now`, `context_window` — which is what makes Task 19's producer table a
uniform call and what makes the one-shape claim checkable rather than argued. `find_structured_strings`
is spelled identically in Tasks 7, 9, 10, 11 and 14; `source_type` is a required keyword in Tasks 10 and
11 only, because those are the two halves of one family. `EXTRACTOR_NAME` is `text.structured` in both
halves of E3 and is registered once in `runs.ANALYSIS_TIER_BY_EXTRACTOR`. `completeness` values are P4's
eight everywhere and P5 publishes no ninth.

**Verification.** The whole plan was assembled into a runnable tree and run: **272 passed, 0 failed**,
across 21 source modules and 21 test files, against P1's real `database_agent` and P2's real
`eval_harness`. Tasks 19, 20 and 21 — the three that could only pass if Tasks 1–18 were mutually
consistent — passed on their first run.

## Known gaps, carried deliberately

- **No real format reader exists.** Every one of the ten is an injected callable with a deterministic
  fixture implementation in tests. That is the plan's central design choice, not an omission: it is what
  makes the six extractors independently buildable and what makes Task 19's one-shape claim provable.
  The libraries a real deployment needs are named below and the *choice* is a NEEDS JOSEPH item.
- **`filesystem.extract_filesystem` reads P3's row with `.get`**, so a caller must hand it a **mapping**,
  not the raw `sqlite3.Row` that P1's `get_file` returns. Task 21 converts with `dict(row)`. Worth
  either widening Task 6 to accept a Row or stating the mapping requirement on P5's read surface.
- **`files.extraction_status_by_tier` still has no writer.** Task 5 computes the map as a pure function
  and hands it to an injected writer because P1 publishes no setter and `files` is P1's table. Unchanged
  from what Task 5's author reported; restated because it is still open.
- **The sensitivity signal is keyed by batch position, not by `observation_key`.** P4's sink returns a
  `run_id` and nothing else, so P5 has no P4-assigned handle for a *per located value* record and owns no
  locator serialization to derive one. See *SPEC vs design* item 3.
- **`text_units` uniqueness depends on the long-tail reader.** `DuplicateUnit` enforces G1's key at the
  boundary, but a reader that omits `region` ordinals will hit it rather than silently losing a unit.
  That is the intended failure direction and it is tested; it is still a contract the reader must meet.
- **A `partial` outcome exists only for archives.** E3 reads a text file whole or not at all, and a
  reader that raises is the caller's error to record: inventing a `failed` path around an injected
  callable would be P5 deciding what a library failure means.
- **No end-to-end orchestrator.** There is no `extract_file(path)` that routes, dispatches, writes the
  run, appends the event and emits the envelope in one call. Each piece is built and tested; the driver
  that sequences them is P13's or the caller's, and no contract assigns it to P5. Task 21 is the closest
  thing and it sequences them by hand, deliberately, so the seams stay visible.

## Dependencies a real deployment needs

Named, not chosen. **This plan installs none of them** and adds no third-party runtime dependency: every
reader below is a keyword-only constructor parameter with a deterministic fixture implementation in
`tests/p5/`, so a real library drops in without changing an observation, a run or a text unit. The
*choice* is a NEEDS JOSEPH item.

| Format / capability | Reader parameter | Candidate library | Why the standard library cannot |
|---|---|---|---|
| Signature / MIME detection (§2.9) | `detect_format` | `python-magic` (libmagic), or macOS `UTType` via PyObjC | `mimetypes` maps **extensions**, which is the opposite of §2.9's rule; the stdlib ships no signature database |
| PDF text, metadata, page structure (§2.2) | `read_pdf` | `pypdf`, `pdfminer.six`, or PDFKit via PyObjC | PDF is a compressed object graph with its own font and encoding model; nothing in the stdlib parses it |
| PDF date strings (§2.2, P4 D8) | `read_pdf` → `iso_dates` | same as above | `D:20260717140322Z` is a PDF-specific syntax; `datetime` does not parse it and §3.10 forbids P5 parsing dates out of text |
| DOCX paragraphs, headings, tables, headers/footers, relationships (§2.3) | `read_docx` | `python-docx` | DOCX is OOXML inside a ZIP; `zipfile` reaches the parts but the paragraph, style, table and relationship model is a large specification |
| Markdown / HTML structure (§2.4) | `read_text_document` | `markdown-it-py`, `beautifulsoup4` | the stdlib reads the **bytes** but derives no headings; `html.parser` is a tokenizer, not a document model |
| TOML / JSON / CSV (§2.4) | `read_text_document` | **stdlib** `tomllib`, `json`, `csv` | none needed — these three are genuinely stdlib |
| YAML (§2.9) | `read_text_document` | `PyYAML` or `ruamel.yaml` | no YAML parser in the stdlib |
| Jupyter notebooks (§2.4) | `read_text_document` | `nbformat` (or `json` plus the notebook schema) | the container is JSON; the **cell-type and metadata schema** is versioned and external |
| Spreadsheets — XLSX/XLS/ODS/Numbers (§2.9) | `read_long_tail` | `openpyxl`, `xlrd`, `odfpy` | binary and OOXML workbook formats with formulas, shared strings and styles |
| Presentations — PPTX/PPT/ODP (§2.9) | `read_long_tail` | `python-pptx`, `odfpy` | same; plus the speaker-notes and slide-layout model |
| Email — EML / MBOX (§2.9) | `read_long_tail` | **stdlib** `email`, `mailbox` | none needed |
| Email — MSG (§2.9) | `read_long_tail` | `extract-msg` | MSG is an OLE compound file, not RFC 5322 |
| Calendar — ICS (§2.9) | `read_long_tail` | `icalendar` | RFC 5545 recurrence rules are not in the stdlib |
| Contacts — VCF (§2.9) | `read_long_tail` | `vobject` | RFC 6350 vCard parsing is not in the stdlib |
| Audio / video container metadata (§2.9) | `read_long_tail` | `mutagen`, or `ffprobe` via subprocess | container and codec parsing; duration, tags and embedded captions |
| Speech-to-text transcripts (§2.9) | `read_long_tail` (`transcribe=True`) | deferred with the authorizing policy — see NEEDS JOSEPH | speech recognition is a model, not a parser |
| Archive manifests — ZIP / TAR (§2.5) | `read_manifest` | **stdlib** `zipfile`, `tarfile` | none needed — both expose an entry list *without extracting*, which is exactly §2.5's requirement |
| Archive manifests — 7z / RAR (§2.5) | `read_manifest` | `py7zr`, `rarfile` | no stdlib support |
| Image dimensions, EXIF, colour (§2.6) | `read_image` | `Pillow`, or macOS `ImageIO` via PyObjC | the stdlib decodes no image format |
| **HEIC** (§2.6, mandatory) | `read_image` | `pillow-heif`, or macOS `ImageIO` | HEIC is HEIF/HEVC; failing to configure it *"can silently exclude a meaningful portion of an Apple-centric corpus"* |
| Perceptual hash (§2.6, G5) | `perceptual_hash` → `ImageRecord.perceptual_hash` | `imagehash`, or an ImageIO-based implementation | requires decoding and resampling the image |
| OCR (§2.7, macOS-only for v1 per **S1**) | `ocr_engine` | **Apple Vision** via PyObjC — the one engine §2.7 names | text recognition is a model |
| Structured-string patterns — DOI, citations, identifiers (§2.2) | `find_structured_strings` | none; the pattern set is **Deferred** and hand-authored | not a library problem — the patterns are content the design has not written |
| Repository markers, camera-filename patterns, screen resolutions, sensor ratios | `recognize_markers`, `filename_pattern`, `dimension_signal` | none; all **Deferred** | same — these are lists the design has not written |

## SPEC vs design — conflicts found

Reported, not unilaterally resolved. Each says what this plan did in the meantime.

**1. §2.4 and §2.6 ask E3 and E5 to emit fields O5 gives to P3.** P5's SPEC lists *"Filename ·
extension"* in E3's emit block and §2.6 lists *"file size"* and *"content hash"* in E5's. But O5 and the
SPEC's own *Contract out* say the opposite — *"The §1.2 basic filesystem record is P3's and P5 never
recomputes it; P5 surfaces it as `source_type: filesystem` observations referencing P3's row, which is
how a filename or parent-folder value becomes citable evidence."* All four values are §1.2 fields, and
emitting them again would put one value in two homes and defeat §3.4's cache key.
**This plan discharges all four through the `filesystem` run (Task 6) and emits none of them in E3 or
E5**, with tests asserting their absence (Tasks 10 and 13). **The SPEC's two emit blocks should be
amended to point at the filesystem run.** The requirement is met either way; the wording is not.

**2. §2.6's stripped-EXIF formulation cannot be satisfied literally.** The SPEC says the record of a
stripped-EXIF image is *"a `complete` image run that emitted no `metadata` observations."* But §2.6 also
requires format, pixel dimensions and colour information, and P4's zone for all three is `metadata` — so
a conforming E5 **always** emits metadata rows and the sentence can never be true.
**This plan asserts the checkable form**: no EXIF-addressed observation, and **no `signal_tier` of any
kind** on any row (Task 13). That is the substantive claim — *"No screenshot signal exists anywhere"* —
and it is what the SPEC's own fixture line actually asks for. **The SPEC sentence should be restated as
"no EXIF observation and no `signal_tier`."**

**3. P4's sink gives P5 no handle for a per-located-value record.** `EvidenceSink.write` returns a
`run_id`; `observation_key` is P4-assigned and P5 owns no locator serialization to derive one. So §2.9's
sensitivity signal — which is *per located value*, and cannot ride on the observation (P4 rule 6 forbids
an extractor-private field) or on the run (wrong granularity) — has nothing to key on.
**This plan keys it on the observation's position in the batch the sink wrote atomically** (Task 11) and
says so in the module docstring. **P4 should return the assigned `observation_key`s alongside the
`run_id`**, at which point this table's key changes and nothing else does. This is a seam gap for P4,
not a P5 preference.

**4. §2.7's "nine persisted fields" is eight bullets.** §2.7's sentence lists *provider and version,
languages, configuration, page or image reference, raw recognized text, locations or bounding boxes,
confidence information, complete or capped* — eight items, nine only if *"provider and version"* counts
as two. The SPEC's *"All nine have a home"* is right on the second reading.
**This plan spells nine** (`PERSISTED_FIELDS`, Task 14) with provider and version separate, because they
land on two different P4 columns. Worth a one-word clarification in the SPEC.

**5. B7 asks P5's `stage_output` to carry "the version tuple"; P2 as built does not accept one.**
`eval_harness.replay.StageResult` has five fields and no version tuple; `record_stage_output` takes
`version_tuple_ref` from the **run** it is replaying, and `record_version_tuple` assembles six axes of
which P5 owns exactly one (`extractor_versions`).
**This plan publishes `extractor_versions()` — P5's axis — and leaves the tuple to P2** (Task 17), with a
test that P2's `record_version_tuple` accepts it. **B7's wording should say "its axis of the version
tuple."**

**6. §2.5 requires E4 to store a file count and gives it no home.** P4 has no count field on an
observation and a second observation carrying `"5"` would be a value P6 could rank.
**This plan puts it on `run.coverage {units: "entries", processed, total}`** (Task 12), which is exactly
the rule Task 7 already applied to §2.2's page count and which Task 7's own table flagged for report.
Two SPEC fields, one rule; worth writing the rule down once in the SPEC rather than twice in tasks.

**7. P1 publishes no writer for `files.extraction_status_by_tier`.** The column exists in `db.py`'s
`FILES_DDL` and `invalidate_extraction_state` resets it to `'{}'`, but there is no setter and `files` is
P1's table. Task 5 computes the map as a pure function and hands it to an injected writer. **Unchanged
since Task 5 reported it; still a real gap in P1's published surface.**

## NEEDS JOSEPH

Manual input required. Each item states the question, the § that raises it, what the design does and does
not say, the options, and a recommendation. **None of these is answered in code** — each is held by a
keyword with no default or a caller-supplied strategy, with a guard in Task 20 that fails if someone
answers it in an implementation instead of in a SPEC.

**1. Which OCR engine, and is macOS-only acceptable for v1?**
§2.7, **S1**. The design names **Apple Vision** and names no other provider anywhere; S1 reads that as
"v1 ships OCR on macOS only." The plan holds `ocr_engine` as an injected callable and spells no provider
name.
*Options:* (a) Apple Vision only, macOS-only v1, as S1 says. (b) Apple Vision plus a cross-platform
fallback (Tesseract / PaddleOCR) — but §2.7 names none and adding one is P5 authoring scope.
(c) A cloud OCR API — which would make OCR a network call and collide with §8.4's local-first posture.
**Recommendation: (a).** It is what the design says, and the plan's injected engine means (b) costs one
new reader and zero changes to any record if you later decide otherwise.

**2. ~~Which OCR languages?~~ ANSWERED 2026-08-20 — English, CJK (Chinese, Japanese, Korean), and Western European (French, German, Spanish, Italian, Portuguese).**
Ratified in [`SPEC.md`](SPEC.md) as the deployment's **configuration**, not as a P5 constant: `config` stays a required keyword with no default, `extractors` still holds no language tag, and `test_no_screen_resolution_no_language_tag_and_no_producer_string` still passes. The list lands in `extraction_runs.config` where §2.7 wants it, so it is fingerprinted and two runs at different language sets stay distinguishable to §3.4's cache key. The original question follows.
§2.7, SPEC *Deferred*. The design says *"appropriate language support including CJK where required"* and
settles neither the list nor how "required" is decided. The plan holds `config` as a required keyword
with no default and holds no language tag anywhere.
*Options:* (a) A fixed list you write once (e.g. English + the CJK set your corpus needs).
(b) Per-scan configuration the user sets. (c) Detect the language first — which needs a language
detector §2.2 arguably prohibits in spirit (*"no global language-quality checks"*).
**Recommendation: (a) as a P1 configuration default with (b) available**, and explicitly not (c).
**This needs your input: which languages are in your corpus.**

**3. What is the OCR rendering resolution?**
§2.7 says *"a practical rendering resolution such as 200 DPI"* — *"such as"* makes 200 an example, not a
value, so the plan holds no number. **A real deployment needs one.**
**Recommendation: start at 200 DPI** (the design's own example) and treat it as a P1 ceiling you can
raise; it interacts directly with item 4's page cap.

**4. What are the four §8.6 ceiling values?**
`ocr.max_pages_per_file`, `ocr.max_time_per_file`, `ocr.max_time_per_scan`,
`image.max_analysis_ops_per_scan`. P1 publishes the **keys** (G4) and holds no defaults; §8.6 names the
knobs and no numbers. The SPEC's own worked example implies a page cap exists (*"89 scanned PDFs deferred
after the OCR limit"*, and a 400-page book that stops).
**Recommendation:** pick them empirically against your real corpus once one real OCR engine is wired —
they are the only P5 numbers that change user-visible behaviour, and guessing them now would be the
invented value this plan spent twenty tasks avoiding.

**5. What does OCR confidence mean downstream?**
§2.7 requires confidence to be *persisted*; nothing in the design says what a low confidence does. The
plan stores the engine's value on the observation and acts on it nowhere.
*Options:* (a) P6 weighs it in §3.7's scoring. (b) A threshold below which an OCR observation is not
usable evidence. (c) Purely informational, for the review surface.
**Recommendation: (a)**, and explicitly not (b) — a threshold here would be a second no-usable-facts
rule, and OQ1 already owns that question.

**6. Does the initial release ship spreadsheet and presentation extraction, or mark them `unsupported`?**
**SPEC OQ5.** §2.4 explicitly permits either; §2.9 gives both full field lists. The plan holds it open:
supply a reader and the format extracts, supply none and the run is `unsupported` with zero observations.
*Options:* (a) Ship both at launch (`openpyxl` + `python-pptx`). (b) Ship `unsupported` and add them
later — legitimate under §2.4 and visible to the user in §8.6's count line. (c) Ship spreadsheets only.
**Recommendation: (b) for v1, then (a).** The plan makes the upgrade a reader injection with no schema
change, and §2.4 was written to permit exactly this.

**7. ~~Is speech-to-text in scope?~~ ANSWERED 2026-08-20 — OUT OF SCOPE for v1.**
Audio and video stop at container metadata. No transcript is produced, so v1 needs no speech model, no consent flow for one, and no answer to the revocation half. `transcription_authorized` stays in the contract with no default and refuses any transcript arriving without it, so enabling this later is a policy decision plus a reader — no record shape changes. The original question follows.
§2.9 and **SPEC OQ6**. §2.9 authorizes transcripts *only* under an explicit privacy and compute policy;
§8.8 makes the *authorization* plan-versioned while the *evidence* is shared; the design never says what
happens when the policy is revoked. The plan requires an injected `transcription_authorized` predicate
with no default and refuses a transcript that arrives without it.
*Options:* (a) Out of scope for v1 — audio/video stops at container metadata. (b) In scope, and a
transcript survives revocation as evidence. (c) In scope, and revocation deletes the transcript and its
text units.
**Recommendation: (a) for v1.** It needs a model, a consent flow and an answer to (b)/(c), and §2.9 makes
it conditional precisely so it can be deferred. **This needs your decision.**

**8. ~~Delete or gate on private reclassification?~~ ANSWERED 2026-08-20 — GATE by default, with an explicit user-initiated delete.**
Rows are retained and hidden behind P7's handling class, so §8.2's *"reach the origin of the conclusion"* still holds; §8.4's delete is a separate explicit action, never an automatic consequence. **P5 publishes no deletion** — now a ratified requirement, not an open question. The gate is P7's and the delete surface is P13's, and both inherit this. The original question follows.
**SPEC OQ6**, §8.4, §8.7. §8.4 says the user should be able to review and **delete** local derived data;
§8.7 lists marking a file private as a correction. The same question applies to the `text_units` a run
produced, which are the bulk of the derived text (G1). The plan publishes **no deletion of any kind** and
no gating vocabulary.
*Options:* (a) Gate — the rows stay, P7's handling class hides them. (b) Delete — irreversible, and
breaks §8.2's *"a user inspecting a placement must still be able to reach the origin of the conclusion."*
(c) Gate by default with an explicit user-initiated delete.
**Recommendation: (c).** But this is a privacy commitment, not an engineering call, and §8.4 gives it to
P7 — **it needs your ratification before P7 is planned.**

**9. Does P5 flag sensitivity, or assign a handling class?**
**SPEC OQ7.** §2.9 requires email addresses, message content and VCF output be *treated as* potentially
sensitive at extraction; §8.4 puts handling-class assignment in P7. The boundary is unstated. The plan
emits **one** signal value and assigns no class.
**Recommendation: P5 flags, P7 classifies** — which is what this plan implements and what §8.4's
allocation implies. Confirm it so OQ7 can close.

**10. Routing precedence for the two formats §2.9 lists twice.**
**SPEC OQ2.** CSV is under both *Spreadsheets* and *Code/structured data*; PDF is under both *Text
documents* and *Presentations ("PDF slide decks")*. Each pairing has a **different field list** and the
design gives no tiebreak. The plan records **both** candidates on the routing decision and operates on
§2.9's own document order (`spreadsheet` for CSV, `text_document` for PDF) rather than a preference.
*Options:* (a) Ratify document order as the rule. (b) Content-sniff — a PDF with slide-shaped pages
routes as a presentation. (c) Run both extractors and let the two `extraction_runs` rows coexist, which
B1's one-row-per-(file × extractor) design already permits.
**Recommendation: (a) for v1**, and note that (c) is available with no schema change if the field lists
turn out to matter.

**11. Which P2 outcome does an `unreadable` or `metadata_only` run report?**
§8.5 / B7, and Task 17's mapping table. **ANSWERED 2026-08-20 — `abstained`** for both, and
`dataless` (the ninth value, C4) joins them for the same reason: P5 declined to assert, because it never
opened the file. Measuring an indexed-but-unreadable PSD as `produced` would let a corpus of unreadable
files look like a successful extraction run, which is §8.6's exact failure mode. The original question
follows. Six of P4's eight `completeness` values map to a P2 outcome
unambiguously. Two do not: both produce **real metadata-level observations** while leaving §8.5's
extraction question — *"did the expected text, metadata, table values, OCR text, or image facts
appear?"* — unanswered.
*Options:* (a) `abstained` — P5 declined to assert, which is what this plan implements.
(b) `produced` — rows exist, so measure them.
**Recommendation: (a).** Measuring an indexed-but-unreadable PSD as *produced* would let a corpus of
unreadable files look like a successful extraction run, which is §8.6's exact failure mode.

**12. What is the "no usable facts" threshold?**
**SPEC OQ1.** The owner and surface are settled — P6 publishes `no_usable_facts(file_id, content_hash)`
(M11) and P5 calls it before any targeted OCR on a broken-text-layer PDF. The **threshold behind the
verdict** is a deferred configuration value the design never names. It is P6's to hold, but it gates a
P5 behaviour, so it needs an answer before targeted OCR is real.

**13. May a nested archive's manifest be read one level down, in memory?**
**SPEC OQ8.** §2.5 lists nested archives among those marked *unreadable or partially inspected*, but
reading an inner manifest **without unpacking** is not the same act as extraction, and the design does
not distinguish them. The plan reads one manifest and recurses never; a nested archive is `partial`.
*Options:* (a) Never — as implemented. (b) One level, in memory, never to disk. (c) N levels with a
configured depth ceiling — which would be a new §8.6 knob the design does not have.
**Recommendation: (a) for v1.** `submission.zip` containing a nested archive still yields its outer
manifest, which is the evidence §2.5's example is actually about.

**14. The hand-authored content P5 consumes but must not invent.**
Five Deferred lists, all of them content rather than code, all held as caller-supplied strategies:
the **tool-generated producer/creator strings** (§2.2 gives three examples), the **known screen
resolutions** and **sensor-shaped aspect ratios** (§2.6), the **camera-filename patterns** (§2.6's
example is `IMG_4821.png`), the **repository markers and package manifests beyond §1.1's four**, and the
**citation and identifier pattern sets** (§2.2 names DOI and names the rest as classes). None blocks the
build — every extractor runs with an empty strategy — and each one that stays empty is a class of
evidence the product does not see. **These are the "domain stuff" you asked to be told about.**
