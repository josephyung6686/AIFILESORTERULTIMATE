# P5 — Extractors

Owns: §2.1–2.7, §2.9
Status: contract draft

---

## Purpose

Convert every file the scan hands over into **observations in the shape P4 froze** (§2.8), reading
each file **once per content version** and storing the result so that no later stage reopens it
(§2.1). A PDF is not reopened for the Academic, Applications, Research and Career templates, and the
same raw document is not sent repeatedly to a model (§2.1).

P5 decides **nothing about meaning**. It does not create a folder path, invent a domain, merge files
that share one string, or treat model output as proof (§2.8). It does not create facts — the filename
`Syllabus BUSIB 4300 Spring 2026.pdf`, the PDF title, and a page-one heading are observations;
`subject = BUSIB 4300` is a fact and belongs to P6 (§3.2).

Six extractor families are mutually independent and share one shape. Each is specified below as a
separate sub-contract with its own output field list, its own failure states, and its own fixtures.

---

## Design slice owned

| § | Slice | Sub-contract |
|---|---|---|
| §2.1 | Why the evidence layer exists — read once per content version, reuse everywhere | all |
| §2.2 | PDF extraction | **E1** |
| §2.3 | DOCX extraction | **E2** |
| §2.4 | Text-bearing and structured files | **E3** |
| §2.5 | Archives | **E4** |
| §2.6 | Images | **E5** |
| §2.7 | OCR | **E6** |
| §2.9 | Format coverage beyond the core four — routing and the long-tail families | **R** (router) + E1–E6 |

**Explicitly not owned.** §2.8 the observation shape itself → P4. §1.1 exclusions and §1.2 basic
filesystem extraction → P3; P5 consumes that record and never recomputes it. §3.x facts, resolvers,
gazetteers, positional weighting, date regexes → P6. §8.4 handling-class assignment → P7. Every LLM
call → P8; **P5 contains no model call of any kind.** OCR is a local recognition engine (§2.7), not a
model escalation.

---

## Contract in

**From P3 (§1.1, §1.2)** — one file record per file, already filtered by the exclusion rules, so P5
is never handed a path under `node_modules`, `.git`, `venv`, `build`, `dist`, `target`, `vendor`,
`Pods`, `site-packages`, `Library`, `__pycache__`, or a descendant of a software project root (§1.1):

```text
Internal file ID
Path, filename, normalized filename, extension
MIME type
Size, timestamps, directory position
Content hash
Scan state
Parent-folder context
```

**Stat-cache semantics (§1.2).** If size and modification time are unchanged, P5 is not invoked and
prior extraction results stand. If either changes, P5 re-runs; it must not assume time only moves
forward. If the content hash changes, the file is a **new version** and all extractors re-run (§8.2).

**From P1 (§0, §8.2)** — the durable file identity (content hash + algorithm), the SQLite evidence
store P5 writes into (§2.1), and the append-only event log P5 appends to. Supersede-never-overwrite
is P1's guarantee and P5 relies on it: a second OCR pass must be able to land beside the first
(§8.2).

**From P4 (§2.8)** — the frozen records. P5 emits nothing outside them. §2.8's "Surrounding context"
is published as **three** fields, not one, so that §8.4 can redact a value without dropping its context
(M5); an extractor that emits a single context field fails P4's conformance rule 1:

```text
observation_key · File identifier · Content hash · Extractor name and version · Source type ·
Raw value · Normalized candidate value · Location · context_before · context_after ·
context_truncated · Occurrence count · Observation time · Reliability state ·
run_id · confidence · signal_tier · supersedes · superseded_by · supersede_reason
```

`observation_key` — not `observation_id` — is the handle every consumer cites (M14). `signal_tier` is
P4's home for §2.6's three-level image hierarchy (M2); it is null on everything else. `Location` is
P4's **structured record** — `zone`, an ordered `container_path[]` of typed segments, `text_span` /
`time_span` / `region`, and the canonical `locator` string — never a per-format string: §2.8's
per-source-type examples (page/heading, table/row/column, an EXIF field, an OCR region, a manifest
path) cannot be expressed by a plain string, and all of them are paths in that one shape, which is
what keeps §3.7's positional weighting computable and §2.3's zone distinction alive across the seam.

**From P4 (`extraction_runs`)** — the single extraction-outcome record, one row per
(file version × extractor). P5 writes one per run and publishes **no parallel status vocabulary of its
own** (B1). It carries `completeness`, `coverage {units, processed, total}`, `config` and
`config_fingerprint`, which is where §2.7's languages, configuration and complete-or-capped flag live.

**From P4 (`text_units`)** — the home for bulk text, keyed by `(run_id, container_path)` (G1). §2.2's
"complete text by page", §2.4's full text, and §2.7's "raw recognized text" are written here, not as
observations; an observation's `text_span` is an offset into the unit its `container_path` names.

**From P7 (§8.4, §2.9)** — the operation mode, and the explicit privacy-and-compute policy that is
the *only* thing that may authorize speech-to-text transcription of audio and video (§2.9). Absent
that policy, audio/video extraction stops at container metadata. P5 also needs to know when a user
has reclassified a file as private (§8.4, §8.7).

**From configuration (§8.6)** — the four ceilings P5 consumes: maximum pages OCRed per file, maximum
OCR time per file, maximum OCR time per scan, maximum image-analysis operations per scan.

**From P6 (§2.2, §2.7)** — a *return* signal, published on P6's read surface as
`no_usable_facts(file_id, content_hash) -> bool` (M11): for a PDF with a non-empty but unusable text
layer, the verdict that its stored evidence produced no usable facts. This is the only condition that
may trigger targeted OCR on such a file (see E1/E6). It is a genuine back-edge from wave 2's later
part into P5, not a hand-off. The threshold behind the verdict is a deferred configuration value —
Open questions #1.

---

## Contract out

P5 publishes three things: a **routing decision per file**, **observations, text units and
`extraction_runs` rows** in P4's shapes, and **events** (§8.2). Nothing else.

The §1.2 basic filesystem record is P3's and P5 never recomputes it; P5 surfaces it as
`source_type: filesystem` observations referencing P3's row, which is how a filename or parent-folder
value becomes citable evidence (§2.2, §2.9, O5).

P5 also emits P2's `stage_output` with `stage_id = extraction`, carrying `inputs[]`, an explicit
abstention value, a distinct budget-deferral value, and the version tuple (§8.5, B7).

### R — the router (§2.9)

Extension is a **routing signal, not an assumption about meaning** (§2.9). The router inspects the
real MIME type or file signature where possible and dispatches to the best available extractor for
the *actual* format. A `.txt` that is a ZIP by signature routes to E4.

Every file leaves the router with exactly one **routing decision**:

```text
File identifier
Content hash
Detected format (signature/MIME) and declared extension
Whether they disagree
Selected extractor family and version, or none
```

**The outcome is P4's, not P5's (B1).** P5 publishes no status vocabulary of its own. What happened
once an extractor ran is recorded in P4's `extraction_runs`, **one row per (file version ×
extractor)** — so an opaque image, which runs E5 *and* E6, produces two rows and can say "EXIF read
successfully, OCR capped." A per-file status could not express that, and §2.7's provider, version,
languages, configuration and complete-or-capped flag have no home on one either.

P5's obligation is to write the right `completeness` value, and §2.4's rule is what the vocabulary
exists to protect: an unsupported format must never be silently treated as an empty document, because
an empty extraction result is different from an extractor that does not yet exist.

| P4 `completeness` | P5 writes it when | § |
|---|---|---|
| `complete` | the extractor ran to the end of the file — **including when it found nothing**, which is §2.4's "empty extraction result" and carries zero observations | §2.4, §2.7 |
| `capped` | a configured ceiling stopped it; `coverage` says how far it got (OCR page cap, run-time limit) | §2.7, §8.6 |
| `partial` | some parts were readable and some were not (nested or oversized archive, mixed-readability document) | §2.5 |
| `metadata_only` | deliberate safe stop — disk images, executables, databases, encrypted containers, damaged files, unknown binary | §2.9 |
| `deferred` | the budget was exhausted before the extractor started | §8.6 |
| `unsupported` | no extractor exists for this format yet | §2.4, §2.9 |
| `unreadable` | format known, content not recoverable (password-protected, malformed, damaged, encrypted). **Still carries the metadata-level observations §2.9 requires** — "indexed-but-unreadable", never zero rows | §2.5, §2.9 |
| `failed` | the extractor errored — an error is not an empty document | §2.4 |

The one substitution to make when reading an older draft of this spec: **`extracted_empty` is
`complete` with zero observations.** §2.4's distinction survives as `complete`-with-zero (the file
genuinely contained nothing) versus `unsupported` (no extractor exists) versus `metadata_only` (a
deliberate policy stop), which are three distinguishable states rather than one ambiguous one.

These values count directly into §8.6's user-facing sentence — *"1,842 files indexed; 1,611 fully
extracted; 89 scanned PDFs deferred after the OCR limit; 34 files require model review; 18 files
remain unreadable"* — as: **indexed** = files with any run (P3's scanned count is the denominator);
**fully extracted** = files whose every run is `complete`; **deferred** = runs at `deferred` or
`capped`; **unreadable** = runs at `unreadable` or `failed`. "Files require model review" is P8's
count, not P5's.

**Long-tail family routing table (§2.9).** Every family the design enumerates, with the fields §2.9
requires each to yield. These are enumerated here, not deferred.

| Family | Formats named by §2.9 | Fields §2.9 requires | Handler |
|---|---|---|---|
| Text documents | PDF, DOCX, RTF, TXT, Markdown, HTML, EPUB, OpenDocument | full text, headings, metadata, links, structural information | E1 (PDF), E2 (DOCX), E3 (rest) |
| Spreadsheets | XLSX, XLS, CSV, TSV, ODS, Numbers exports | workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, dates or identifiers from labeled cells | E3 |
| Presentations | PPTX, PPT, ODP, PDF slide decks | slide titles, text boxes, speaker notes where available, hyperlinks, embedded tables, slide-level page boundaries | E3 (PDF decks: E1) |
| Email | EML, MBOX, MSG, exported mail archives | sender, recipients, subject, sent date, thread identifiers, message body, attachment names, reply-chain context — **addresses and message content treated as potentially sensitive** | E3 |
| Calendar | ICS | event title, start and end time, location, organizer, attendees, recurrence metadata | E3 |
| Contacts | VCF | names, organizations, email addresses, phone numbers, address-book metadata — **normally privacy-protected rather than used to create folder proposals** | E3 |
| Code, notebooks, config, structured data | Python, JavaScript, SQL, Jupyter notebooks, JSON, YAML, TOML, XML, CSV | readable text plus language, imports, notebook cell types, package manifests, schema keys, repository markers, project-root signals | E3 |
| Audio and video | — | duration, container and codec metadata, creation time, embedded tags, subtitles or captions where present; speech-to-text transcripts **only under an explicit privacy and compute policy** | E3 |
| Design and creative | PSD, AI, SVG, Figma exports, CAD, 3D | at minimum filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, preview text; unsupported proprietary formats recorded as **indexed-but-unreadable, never silently empty** | E5 (raster/SVG), else `unreadable` |
| Compressed archives | — | manifests, **without extraction** | E4 |
| Disk images, executables, databases, encrypted containers, damaged files, unknown binary | — | `metadata_only` unless a dedicated extractor has been **explicitly approved** | R only |

### E1 — PDF (§2.2)

**Emits, for a PDF with a usable text layer — the complete document, not a first-page preview:**

```text
Document metadata:   title · author · subject · creator · producer ·
                     creation date · modification date · page count
Text:                complete text, by page
Structured strings:  headings · URLs · email addresses · DOI values ·
                     citations · identifiers · other structured strings that
                     may later support file facts
```

The **complete text, by page** is written to P4's `text_units`, one row per page, keyed by
`(run_id, [{page, N}])` (G1). It is not emitted as observations: a page of text is not a located
value. Structured strings are the observations, and their `text_span` offsets index into the page unit
their `container_path` names.

**Every observation carries** a document zone, page number, text offset, surrounding context
(`context_before`, `context_after`, `context_truncated` — P4's three fields, M5), and occurrence count
(§2.2). This is load-bearing: a course code or university name in a filename, title,
or page-one heading is more meaningful than the same text appearing once in a reference list on page
eighteen (§2.2). The same string in both places produces **two observations with different
locations**, never one merged observation.

**Metadata is supporting evidence, not truth (§2.2).** Author and creator fields may be stale,
generic, or generated by a tool rather than a person. `python-docx`, `Mozilla/5.0`, and
browser-generated producer strings must not be mistaken for meaningful content. They are emitted
verbatim (the raw value is never discarded, §2.8) at `zone = metadata` with `reliability: direct` —
`direct` describes the **slot**, not the value's usefulness.

**There is no marker on the observation** (M4). P5 sets no suppression flag and invents no field: the
producer/creator **discount rule is P6's**, keyed on P4's `zone = metadata` plus the tool-string list
below under *Deferred*. P5's obligation is to emit the value in a slot P6 can key on, not to decide
what it is worth. This closes what was Open question #13.

**Text-layer states — the distinction §2.2 requires:**

| State | Definition | Action |
|---|---|---|
| `text_layer_usable` | Text extracted and usable | No OCR |
| `text_layer_absent` | **No** text layer | Route **directly** to E6 (§2.2, §2.7) |
| `text_layer_broken` | Technically produces text, but the stored evidence yields no usable facts | **Targeted** OCR only, and only after P6 reports no usable facts (§2.2, §2.7) |

A PDF with no extractable text and evidence of being created from a photographed page routes directly
to OCR (§2.7).

**Prohibited.** No global language-quality check: those incorrectly punish multilingual and
mathematics-heavy documents (§2.2). A broken-text-layer PDF must not reach OCR "because a broad
quality heuristic says the text looks unusual" (§2.7). The trigger is the absence of usable facts,
not the appearance of the text.

### E2 — DOCX (§2.3)

**Emits — the full semantic structure, not the first few paragraphs:**

```text
Core properties
All paragraphs, in order
Heading levels
Tables and table-cell text
Headers and footers, where feasible
Hyperlinks
Document relationships
Revision or comment metadata, where available
```

**Tables are mandatory, not optional** (§2.3). Resumes, forms, applications, invoices and
administrative documents often place their most useful information in cells rather than body
paragraphs. A table-cell observation locates as table N, row R, column C (§2.8).

**Zone fidelity.** The extractor must preserve the difference between a **heading**, a **table
label**, a **filename**, and **ordinary body text**, because those locations carry different
evidentiary weight (§2.3). `Wash U.docx` has an unhelpful filename but a heading stating "Please tell
us what you are interested in studying at college and why." — strong evidence for the College
Applications domain even though the filename reveals nothing (§2.3). If the zone is flattened, that
distinction is destroyed at the source and no later part can recover it.

**Author metadata is supporting information only** (§2.3) — it may identify a prior editor, a
document template, or a script rather than the subject or purpose of the file.

### E3 — Structured text and code (§2.4, §2.9)

**Emits, for Markdown, plain text, JSON, CSV, source code, notebooks, configuration** — the full text
to P4's `text_units` as one whole-file unit, `container_path: []` (§2.4, G1), and the rest as
observations:

```text
Text                   → text_units, container_path: []
Filename · extension
Language, where relevant
Headings
Structural indicators: repository markers · package manifests ·
                       notebook metadata · README files
```

**Code relies on local structural evidence** — repository roots and package files — **rather than
forcing semantic analysis** to infer a project from arbitrary code text (§2.4). E3 emits the
structural markers it finds; it does not read code to guess a project.

**Spreadsheets and presentations (§2.4).** §2.4 permits exactly two outcomes and no third: dedicated
extraction support (sheet names, visible cell text, slide titles, notes, metadata — full field lists
in the routing table above), **or** `completeness: unsupported`. Which of the two the initial release
ships is Open question #5. Either way the outcome is explicit: a format with no extractor is
`unsupported`, never `complete` with zero observations.

**Email, calendar, contacts, audio/video, per §2.9** — field lists in the routing table. E3 marks
email addresses, message content, and all VCF output as potentially sensitive at emission (§2.9), for
P7 to act on. Audio/video stops at container metadata unless the explicit privacy and compute policy
authorizes transcription (§2.9).

### E4 — Archives (§2.5)

**Emits — read from the manifest, with nothing written to disk:**

```text
Archive type
Contained paths · filenames · folder names · extensions
File count
Uncompressed size, where available
Recognizable markers: source-code manifests · document names
```

Observations locate as a **manifest path** (§2.8). `submission.zip` containing a transcript, personal
statement, resume, certificate and form is meaningful evidence of a purpose-defined application
packet even when the outer archive name is vague (§2.5). A source-code archive revealing `README.md`,
`package.json`, a `src` directory, or a Python package layout can be recognized as a code project
(§2.5).

**Absolute prohibition.** The normal scan **never** extracts archive contents to the filesystem —
doing so creates security, storage and side-effect risks (§2.5). Password-protected, malformed,
nested, and oversized archives are marked `unreadable` or `partial` (P4's words for §2.5's
"unreadable or partially inspected"); they are never forced open and never allowed to become
**decompression-bomb** risks (§2.5). Uncompressed size is
read from the manifest where the format declares it, and is itself a bomb signal — it is never
established by decompressing.

### E5 — Images (§2.6)

**Emits, for every supported image:**

```text
Format · pixel dimensions · file size
Color information, where useful
Content hash · perceptual hash
EXIF: camera make · camera model · lens data · ISO · focal length ·
      capture time · GPS · orientation
Software metadata
Filename pattern
OCR output, where needed (→ E6)
```

Camera EXIF, GPS and capture time support deterministic photo-event proposals; exact and perceptual
hashes identify duplicates and near-duplicates (§2.6).

**HEIC support is mandatory and explicit** (§2.6). Failing to configure the image stack for HEIC
silently excludes a meaningful portion of an Apple-centric corpus — a silent exclusion, which is the
worst failure mode available to this part. A HEIC fixture is a required test, not an optional one.

**The signal hierarchy (§2.6).** E5 emits each signal as its own observation, carrying P4's
`signal_tier ∈ {1, 2, 3}` (M2). E5 emits **no photo/screenshot conclusion** — `media type` is a
Photos-domain fact (§3.11) and belongs to P6. E5's obligation is to expose the tier so P6 can weigh
it; P4 carries the field so §2.6's hierarchy is not re-derived, and drifted from, in a second place.

| `signal_tier` | Signals | §2.6's weight |
|---|---|---|
| 1 | Camera EXIF | **strong** photo evidence |
| 2 | Capture time, GPS, sensor-shaped dimensions | reinforce photo |
| 3 | Exact display resolutions, PNG format, software metadata | **may support** a screenshot hypothesis |

**Two explicit traps, both of which must be tested (§2.6, §8.5).**

1. **Absence of EXIF is not proof of a screenshot.** Messaging platforms and downloaded web images
   routinely strip metadata from real photographs. **Absence is never an observation** (M2): P4's
   record holds presence only, so "no EXIF" is recorded on `extraction_runs` — a `complete` image run
   that emitted no `metadata` observations *is* the record that the file carried no EXIF. E5 writes no
   "EXIF absent" row, because a row is a value P6 can rank and an absence must never become one.
2. **OCR text density is not a screenshot detector.** Receipts, document scans, whiteboards, and
   photographs of pages all contain dense text. E5 never derives a screenshot signal from text
   volume.

**Conflicting signals lead to abstention, not an invented classification** (§2.6). E5 emits the
conflicting signals as **two ordinary observations with two `signal_tier` values** — camera EXIF at
tier 1, the exact display resolution at tier 3 — and nothing else. It writes no "conflict" row and no
resolution. **Resolving the conflict is P6's** (M2): §3.7's rule that a facet is filled only when a
candidate clears both a minimum score and a minimum margin over the second-best is what produces
§2.6's abstention. A conflict is a comparison of readings; an observation is a reading.

### E6 — OCR (§2.7)

OCR is **not merely a rescue tool for scanned PDFs**. It is the main way screenshots and opaque loose
images become understandable to the engine (§2.7). A screenshot is always a screenshot *of something*
— a receipt, application portal, conversation, code problem, document, calendar, or research figure —
and without OCR the product sees only an image with a weak filename (§2.7).

**When it runs (§2.7):** when a file yields no usable text **and** no usable metadata. That covers
scanned PDFs, confirmed screenshots, and opaque images without EXIF. A PDF with no extractable text
and evidence of being created from a photographed page routes directly. A document with a non-empty
but unusable text layer receives OCR **only** when its extracted evidence fails to produce usable
facts — never because a broad quality heuristic says the text looks unusual.

**Scope: macOS-only for v1 (S1).** §2.7 says *"On macOS, Apple Vision should be configured
explicitly…"* and names no other OCR provider anywhere. v1 therefore ships OCR on macOS only; there is
no cross-platform OCR requirement in this contract, and no other provider is implied, deferred, or
stubbed. This closes the non-macOS half of what was Open question #9; the remaining half — which
library implements each non-OCR format — is still open.

**macOS configuration — the one engine the design names (§2.7):** Apple Vision, configured
**explicitly** with

```text
Accurate recognition (not fast)
Appropriate language support, including CJK where required
A practical rendering resolution such as 200 DPI
```

**Languages — ratified 2026-08-20: English, CJK (Chinese, Japanese, Korean), and Western European
(French, German, Spanish, Italian, Portuguese).** This settles *"where required"* for this corpus.

It is a **configuration value, not a P5 constant.** P5's `config` stays a required keyword with no
default and `extractors` holds no language tag anywhere — the no-invention guard that asserts this
must keep passing. The list above is the ratified default a deployment supplies, and it lands in
`extraction_runs.config` where §2.7 requires it, so it is fingerprinted and replayable per run: two
runs at different language sets are correctly distinguishable rather than silently merged by §3.4's
cache key.

**Limits (§2.7, §8.6):** page cap, total run-time limit, progress state, partial-read state. Long
scanned books otherwise create unexpectedly expensive workloads (§2.7). A capped run keeps the text
it recognized and is marked capped — it is never presented as complete.

**Persisted for every OCR run (§2.7):**

```text
OCR provider and version
Languages
Configuration
Page or image reference
Raw recognized text
Locations or bounding boxes, where available
Confidence information
Whether extraction was complete or capped
```

All nine have a home, and none needs an OCR-specific shape (B1). Provider and version are
`extraction_runs.extractor_name` / `.extractor_version`; **languages and configuration** are
`run.config` plus `run.config_fingerprint`; **complete-or-capped** is `run.completeness` with
`run.coverage {units, processed, total}`; page or image reference is
`location.container_path` (`page=N` / `region=M`); bounding boxes are `location.region`; confidence is
the observation's `confidence`; and **raw recognized text** is a `text_units` row per page or region
(G1), with the pointed observations' spans indexing into it. This closes what was Open question #2 —
the seam P5 and P4 were most likely to fail to meet.

### Fixtures published

P5 publishes these fixtures so P6, P2 and P4 can be built before P5 exists. Each is drawn from the
design's own examples or from §8.5's adversarial suite.

| Fixture | From | Asserts |
|---|---|---|
| `syllabus-busib4300.pdf` — course code in title and in a page-18 reference list | §2.2, §3.2 | two observations, distinct locations, distinct occurrence counts |
| `hw5-photographed.pdf` — no text layer | §2.1, §2.2 | `text_layer_absent` → direct OCR route, no language check |
| `corrupt-text-layer.pdf` | §2.2, §8.5 | `text_layer_broken`; **no** OCR until P6 returns no-usable-facts |
| `python-docx-producer.pdf` | §2.2, §8.5 | producer emitted verbatim at `zone = metadata`, `reliability: direct`, **no marker of any kind** on the observation; P6 discounts it (M4) |
| `wash-u.docx` — unhelpful filename, decisive heading, data in table cells | §2.3 | heading zone preserved; table N/row/column locations present |
| `submission.zip` — transcript, statement, resume, certificate, form | §2.5 | manifest read; **zero bytes written outside the process** |
| `protected.zip`, `bomb.zip`, `nested.zip` | §2.5 | `unreadable` / `capped`; never forced open |
| `photo.heic` | §2.6 | dimensions + EXIF extracted, EXIF rows at `signal_tier: 1`; HEIC never silently skipped |
| `whatsapp-stripped-exif.jpg` — a real photograph, EXIF removed | §2.6, §8.5 | **zero** observations written about the absence; the `complete` run with no `metadata` rows is the whole record. No screenshot signal exists anywhere (M2) |
| `page-photo-dense-text.jpg` | §2.6 | dense OCR text emits **no** screenshot signal, and no observation derived from text volume |
| `conflicting-signals.png` — camera EXIF **and** exact display resolution | §2.6 | **two** observations, `signal_tier: 1` and `signal_tier: 3`; no conflict row, no resolution, no classification. Abstention is P6's §3.7 margin outcome (M2) |
| `scanned-book-400pp.pdf` | §2.7, §8.6 | stops at page cap; `capped`, never `complete` |
| `report.txt` that is a ZIP by signature | §2.9 | routes by signature, not extension |
| `archive.dmg`, `tool.bin` | §2.9 | `metadata_only` |
| `design.psd` | §2.9 | `unreadable` carrying metadata-level observations (M3) — indexed-but-unreadable, never zero rows |

---

## Deferred — manual design required

Everything here is hand-authored content that P5 will need but must not invent.

| Deferred | Defined by | What is settled | What is not |
|---|---|---|---|
| Tool-generated producer/creator string list | §2.2 | Three examples: `python-docx`, `Mozilla/5.0`, "a browser-generated producer string" | The full list |
| Known screen resolutions / "exact display resolutions" | §2.6 | That they support a screenshot hypothesis | Which resolutions |
| "Sensor-shaped dimensions" | §2.6 | That they reinforce photo evidence | Which aspect ratios qualify |
| Camera-filename pattern library | §2.6 | That filename pattern is an emitted field; `IMG_4821.png` is the design's example | The pattern set |
| Repository markers and package manifests beyond §1.1's four | §2.4, §1.1, §2.5 | `package.json`, `requirements.txt`, `Cargo.toml`, `go.mod` (§1.1); `README.md`, `package.json`, `src`, Python package layout (§2.5) | Everything else; §1.1's list is P3's |
| Archive "recognizable markers" beyond the above | §2.5 | That manifests and document names are markers | The marker set |
| OCR language configuration | §2.7 | "appropriate language support including CJK where required" | The language list, and how "where required" is determined |
| Citation and identifier pattern sets | §2.2 | DOI is named; citations and identifiers are named as classes | The patterns. Date patterns are P6's (§3.10) and out of scope here |
| Numeric budget ceiling values | §8.6, §2.7 | 200 DPI named as "a practical rendering resolution such as"; the four ceilings are named as knobs; **P1 owns the configuration object**, namespaced (G4) | Their values |

**Not deferred by P5 because P5 never touches them.** The 200–300 template library (§5.7), the
domain fact-schema fields (§3.11), gazetteer contents (§3.7), and the residual library beyond §7.3's
nine names are all downstream of facts. P5 emits no domain-scoped output at all, so none of them
enters this contract in any form.

---

## Done means

1. **Every file has exactly one outcome record.** No file handed over by P3 leaves P5 without one,
   and its status is one of the eight enumerated values. `unsupported` is distinguishable from
   `complete`-with-zero-observations in a query (§2.4, §2.9).
2. **Every observation validates against P4's frozen shape**, with no extractor-private field on any
   record. A consumer written against P4's shape reads PDF, DOCX, image, archive and OCR observations
   through one code path with no per-format branch (§2.8).
3. **Raw is retained separately from normalized.** A document saying `U Chicago` keeps that exact
   wording as the raw value regardless of what any resolver later does with it (§2.8).
4. **PDF is complete, not previewed**, and location survives: the page-1 and page-18 occurrences of
   one string are two distinguishable observations (§2.2).
5. **The two text-layer states behave differently**, and no global language-quality check exists
   anywhere in the codebase (§2.2, §2.7).
6. **DOCX table cells and heading zones are present and distinguishable** from body text (§2.3).
7. **No archive fixture writes a byte outside the process**, and the bomb/protected/nested fixtures
   all terminate in a marked state (§2.5).
8. **HEIC extracts.** The three §2.6 traps — stripped EXIF, dense OCR text, conflicting signals —
   each produce abstention, and E5 emits no photo/screenshot conclusion at all (§2.6). No observation
   records an absence or a conflict, and every §2.6 hierarchy signal carries its `signal_tier` (M2).
9. **OCR persists all nine §2.7 fields** across `extraction_runs`, the observation and `text_units`,
   and the 400-page fixture is marked `capped` rather than `complete` (§2.7).
10. **Routing follows signature over extension** on the disagreeing fixture (§2.9), and each §2.9
    family either has its handler or an explicit `unsupported` status.
11. **Re-run determinism.** Same content hash + same extractor version → identical observation set,
    so a P2 replay bundle produces a comparable diff (§8.5).
12. **Re-extraction is additive.** Running an improved extractor over already-extracted content
    leaves both records readable, including both runs' `text_units` (§8.2).
13. **Bulk text has one home.** Every `text_span` an extractor emits resolves against a `text_units`
    row on the same `run_id`, and no extractor stores page text, full text or recognized text anywhere
    else (§2.2, §2.4, §2.7, G1).

---

## Cross-cutting answers

### Provenance (§8.2)

**Events P5 appends** — two of §8.2's enumerated event types: `extraction` (once per file per
extractor family per content version) and `OCR` (once per OCR run) — spelled as §8.2 spells them,
because P1's writer validates the event type against that vocabulary (MINOR 2,
05-minor-resolutions.md). Each carries event type, file ID, content hash, responsible subsystem,
extractor version, time of observation, and a structured explanation or evidence reference (§8.2).
For E6 the OCR provider, version, languages and configuration occupy the position §8.2 gives to
model version and prompt fingerprint. P5 appends `hashing` and `stat observation` events never —
those are P1's and P3's.

**What P5 never overwrites.** Nothing. Not an observation, not an outcome record, not an OCR result.
A newer result **supersedes** an earlier one while the earlier one and the reason for supersession
both remain (§8.2). §8.2's own example is P5's: a first OCR pass produces unreadable text, a later
improved engine recovers a university name, and **both extraction records remain available**. The
resolver may mark the newer value preferred, but a user inspecting a placement must still be able to
reach the origin of the conclusion (§8.2).

**Cache key (§3.4).** Content hash + extractor version + `analysis_tier`, plus provider/version/
configuration for OCR. This is what makes a rename free and a content rewrite expensive, and what
makes an extractor upgrade auditable. **`analysis_tier` is closed** (I4): `filesystem | native | ocr | llm`.
P5 writes the first three and never writes `llm`. Mapping: filesystem observations re-emitted as
`source_type: filesystem` are `filesystem`; E1–E5 are `native`; E6 is `ocr`. P5 also writes
`extraction_status_by_tier` as a map from those four keys to P4 `completeness`; a missing key means
that tier was not attempted.

### Budgets and degradation (§8.6)

**Ceilings P5 consumes** — four of §8.6's twelve; the rest belong to P8, P9 and P10:

```text
Maximum pages OCRed per file
Maximum OCR time per file
Maximum OCR time per scan
Maximum image-analysis operations per scan
```

plus §2.7's own page cap, total run-time limit, progress state and partial-read state.

**Position in the degradation order (§8.6).** Direct facts and high-precision rules run first because
they are cheap and reliable. **Full local extraction and OCR run second, within budget.** Graph
retrieval and LLM calls come after and are not P5's. So P5 sits in the cheap tier with one expensive
tail — OCR — and that tail is where every P5 budget lives.

**On exhaustion.** P5 retains the evidence already extracted, writes `completeness: deferred` on the
run that did not start (or `capped` with `coverage` on the one that stopped short), and leaves the
file in review. It does **not** substitute a cheaper extractor, guess from the filename, or
downgrade quality. §8.6 is explicit: *cost exhaustion must never turn into lower-quality automatic
classification.* A capped OCR run keeps its partial text and is flagged capped — partial evidence is
allowed, misrepresented evidence is not.

**Legibility.** P4's `completeness` values count directly into §8.6's user-facing summary, so that
"89 scanned PDFs deferred after the OCR limit" and "18 files remain unreadable" are two different
queries against two different values — `deferred`/`capped` and `unreadable`/`failed` — rather than
two readings of one word (B1). A file that was never processed must never look like a file that was
understood and found unimportant (§8.6), which is why `complete`-with-zero, `unsupported`,
`metadata_only` and `deferred` are four values and not one.

### Correction learning (§8.7)

**P5 records no corrections, and owns no correction scope.** Every user action §8.7 enumerates —
accepting or rejecting a group, excluding a member from a packet, renaming a branch, merging or
splitting, changing template order, creating a custom template, moving a residual file, choosing a
shallow fallback, keeping a file in place, disabling a suggestion type — acts on a *proposal*. P5
produces observations, not proposals (§3.2), so none of §8.7's six scopes (file / group / node /
template / domain / corpus) has anything to attach to at this layer.

**Two obligations P5 does carry.**

1. **Re-extraction on demand.** §8.7's improvements and §8.2's superseding both require that P5 can
   be re-run over already-extracted content at any time, additively.
2. **Reclassification as private.** A user marking a file private (§8.7, §8.4) must take effect on
   P5's already-stored output — email bodies, VCF contents, GPS, OCR text. §8.4 says the user should
   be able to review and **delete** local derived data; whether reclassification deletes or only
   gates P5's stored observations — and the `text_units` they point into — is Open question #6.

Negative feedback storage (§8.7) belongs to P6, P9 and P11.

### Plan versioning (§8.8)

**None of P5's state belongs to a plan version.** §8.8 settles this directly: *"The evidence database
remains shared across plan versions."* Observations are keyed by content hash and extractor version
(§3.4), never by plan. Renaming Applications to Admissions, reordering the Academic template, or
restoring an earlier draft changes nothing P5 wrote, and the same observation set serves every plan
version simultaneously. This is what makes §8.8's promise — that a new plan never silently
reclassifies old files — cheap to keep.

**One boundary.** §8.8's plan version captures "Privacy and model-consent policies", and §2.9 makes
one P5 output conditional on such a policy: the speech-to-text transcript. The transcript is evidence
and therefore shared; the authorization that produced it is plan-versioned. Whether a transcript
survives revocation of the policy that authorized it is Open question #6.

**Speech-to-text is OUT OF SCOPE for v1 — ratified 2026-08-20.** Audio and video stop at container
metadata: duration, container and codec metadata, creation time, embedded tags, and subtitles or
captions already present in the file. No transcript is produced, so v1 needs no speech model, no
consent flow for one, and no answer to whether a transcript survives revocation. §2.9 makes
transcription conditional precisely so it can be deferred this way. P5's `transcription_authorized`
predicate stays in the contract with no default and refuses any transcript that arrives without it —
so turning this on later is a policy decision plus a reader, and changes no record shape.

---

## Open questions

Each of these is unsettled by the design. None is answered here.

**Settled since the draft, and removed from this list.** *Is `Location` format-parameterized?* — no:
P4 publishes one structured scheme for every source type (`zone`, `container_path[]`, `text_span` |
`time_span`, `region`, plus a canonical `locator`), which was the single highest-risk item between P4
and P5 and is now closed. *Where do OCR's languages, configuration, confidence and complete-or-capped
flag live?* — settled by **B1**: on `extraction_runs` (`config`, `config_fingerprint`, `completeness`,
`coverage`) and, for confidence, on the observation; see E6. *Where does an image observation record
its §2.6 tier?* — settled by **M2**: P4's `signal_tier`. *Which reliability states may an extractor
stamp?* — `direct` and `possible` only, per P4's D11; P4 still carries the corresponding question
about P6's confirmation of the vocabulary. *How is "supporting evidence, not truth" expressed on the
record?* — settled by **M4**: it is not expressed on the record at all; there is no marker, and the
discount rule is P6's. *Who owns the §8.6 budget configuration object?* — settled by **G4**: P1,
namespaced. *Who computes version-family signals?* — settled by **G5**: P6, from P1's content hashes
and P5's perceptual hashes. *Non-macOS OCR* — settled by **S1**: there is none; v1 is macOS-only.

1. **What is the "no usable facts" threshold?** The owner and the surface are settled — P6 publishes
   `no_usable_facts(file_id, content_hash) -> bool` (M11) and P5 calls it before any targeted OCR on a
   broken-text-layer PDF. What remains open is the threshold behind the verdict: §2.2 and §2.7 define
   the trigger in terms of facts and the design never says how few facts is "no usable facts". It is a
   deferred configuration value.
2. **Routing precedence for formats §2.9 lists twice.** CSV appears under both Spreadsheets and Code/
   structured data; PDF appears under both Text documents and Presentations ("PDF slide decks"). The
   design specifies different field lists for each and no tiebreak.
3. ~~**What are the analysis tiers?**~~ **Settled — I4, ratified 2026-08-19.**
   `filesystem | native | ocr | llm`, closed. P5 owns the vocabulary and writes the first three;
   P8 is the only writer of `llm`. See Cache key above and
   [`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md).
4. **Library and engine choices for every format.** The design names Apple Vision for macOS OCR
   (§2.7) — the one engine it names, and the whole of v1's OCR scope under S1 — and names no library
   for PDF, DOCX, HEIC, archives, spreadsheets, presentations, email, calendar, contacts, audio/video,
   or design formats.
5. **Do spreadsheets and presentations ship at launch or ship as `unsupported`?** §2.4 explicitly
   permits either; §2.9 specifies full field lists for both. Which is a release-scope decision the
   design leaves open.
6. ~~**Does reclassifying a file as private delete P5's stored observations or only gate them?**~~
   **Settled — ratified 2026-08-20: GATE by default, with an explicit user-initiated delete.**
   Marking a file private hides its observations and `text_units` behind P7's handling class; the rows
   are retained so §8.2's *"a user inspecting a placement must still be able to reach the origin of the
   conclusion"* still holds. §8.4's *review and delete local derived data* is then a separate, explicit
   user action — never an automatic consequence of reclassification. **P5 publishes no deletion**; the
   gate is P7's and the delete surface is P13's, so both parts inherit this as a requirement rather
   than a choice. Transcription is out of scope for v1 (see the §8.8 boundary above), so the
   revocation half of this question does not arise in v1. The original wording follows. §8.4
   says the user should be able to review and delete local derived data; §8.7 lists marking a file
   private as a correction. The same question now applies to the `text_units` a run produced, which
   are the bulk of the derived text (G1), and to a speech-to-text transcript after the authorizing
   policy is revoked (§2.9, §8.4, §8.8).
7. **Does P5 assign a handling class or only supply the signal?** §2.9 requires email addresses,
   message content and VCF output be treated as potentially sensitive at extraction; §8.4 puts
   handling-class assignment in P7. The boundary between "P5 flags" and "P7 classifies" is unstated.
8. **May a nested archive's manifest be read one level down, in memory?** §2.5 lists nested archives
   among those marked unreadable or partially inspected, but reading an inner manifest without
   unpacking is not the same act as extraction, and the design does not distinguish them.
