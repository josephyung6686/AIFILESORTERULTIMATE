# 2. Reading a file — extraction and evidence

## 2.0 The split: who reads bytes and who fixes the shape

Two parts do the work this section describes, and the division between them is
strict.

**P5 (`src/extractors/`)** knows about formats. It has one module per format family
— `pdf.py`, `docx.py`, `image.py`, `archive.py`, `structured_text.py`,
`long_tail.py`, `ocr.py`, `filesystem.py` — and a router that decides which one a
file goes to. It opens nothing itself; every actual file read arrives as an injected
callable (§2.7 below).

**P4 (`src/evidence_shape/`)** knows nothing about formats. It fixes the *shape* of
what an extractor may say: three record types, six closed vocabularies, a canonical
address string, a twelve-rule validator, and the SQLite tables all three land in. It
has no `if pdf` anywhere; `src/evidence_shape/` imports nothing from
`src/extractors/`, and the dependency runs one way only (`src/evidence_shape/store.py:376-378`
states this deliberately: "P5 depends on P4; the reverse would make the evidence layer
unbuildable without a sorter").

The consequence a reader should hold onto: **an extractor cannot invent a field, a
zone name, or an outcome word.** Every closed vocabulary lives in
`src/evidence_shape/vocabulary.py`, and `check()` (`vocabulary.py:109-117`) raises
`NotInVocabulary` on anything outside it — "No case folding, no stripping, no nearest
match." P5's own builder module says so explicitly: `src/extractors/shape.py:11-14`
declares that `zone`, segment `kind`, `source_type` and `completeness` are *not*
restated in P5 and that P4's validator is the gate.

Three records exist, and nothing else:

| Record | Module | Grain |
|---|---|---|
| `evidence` (the observation) | `evidence_shape/observation.py` | one located value |
| `extraction_runs` | `evidence_shape/runs.py` | one (file version × extractor) attempt |
| `text_units` | `evidence_shape/text_units.py` | one addressable stretch of bulk text |

---

## 2.1 The observation — one located reading of one value

`Observation` is a frozen dataclass with eighteen emitted fields
(`observation.py:126-146`). The stored row adds four more: `observation_id` and P1's
three supersede columns (`observation.py:71-73`).

### Raw and normalized are separate fields, on purpose

`raw_value` is the source substring, byte for byte. `normalized_value` is a
*candidate*, nullable, and produced only by `normalize_mechanical`
(`shape.py:275-287`), which does exactly four things: strip soft hyphens, repair
line-break hyphenation, collapse whitespace, and Unicode NFC. The docstring names the
test case: `U Chicago` stays `U Chicago`. Expanding it to `University of Chicago`
would be resolution, and resolution is P6's.

`raw_value` is never rewritten. Two mechanisms enforce it. First, the DDL
(`evidence_shape/schema.py:108-111`) installs a `BEFORE UPDATE` trigger over
`raw_value, location, occurrence_count, observed_at, extractor_name,
extractor_version, run_id` that aborts with "RAW-2: never updated; a better extractor
emits a new observation and a new run". Second, `evidence_no_delete`
(`schema.py:101-105`) aborts any DELETE at all. The only legal write to an existing
row is the three supersede columns.

An empty `raw_value` is refused at two points, both calling the *same* function:
`check_non_empty` in `observation.py:99-107`, called by the record's `__post_init__`
and by P5's builder (`shape.py:220-221`). The comment at `observation.py:81-89`
records why the second call site exists — the builder used to accept an empty raw
value and the refusal arrived at database-write time, deep in a scan.

### `occurrence_count ≥ 1`: presence only, never absence

Enforced in three places (`observation.py:165-168`, `shape.py:195-196`,
`conformance.py:174-178`). The reasoning is the same everywhere: a count of zero
would be an absence, and an absence written as evidence is a value P6 could rank. The
run record is the only home for absence.

### The locator, and why an observation with no span cannot be released

`Location` (`location.py:154-185`) is a structured record, never a per-format string:

- `zone` — one of fifteen (`vocabulary.py:22-26`): `filename`, `path`, `metadata`,
  `title`, `heading`, `body`, `table`, `header_footer`, `notes`, `link`,
  `annotation`, `reference_list`, `manifest`, `ocr`, `transcript`. It answers *what
  kind of place*.
- `container_path` — an ordered tuple of `Segment`s, outermost first. It answers
  *which one*. Twelve indexed kinds (`page`, `slide`, `sheet`, `heading`,
  `paragraph`, `table`, `row`, `column`, `cell`, `region`, `layer`, `artboard`) and
  three label-addressed kinds (`field`, `entry`, `key`) — `vocabulary.py:31-41`.
  Indices are 1-based, checked at `location.py:55-59`.
- `text_span` — 0-based, half-open, in Unicode scalar values (`location.py:62-76`).
- `time_span` — integer milliseconds (`location.py:79-93`). A location may carry one
  span or the other, never both (`location.py:181-185`).
- `region` — a bounding box, `{x, y, w, h, unit}` with `unit ∈ {px, norm}`
  (`location.py:96-111`).

The **locator** is the canonical string serialization of that record. Its grammar is
stated at `locator.py:4-9`:

```
locator := zone [ ":" segments ] [ "#" text_span | "@" time_span ]
```

Labels are percent-encoded over `% / = # @ :` and control characters
(`locator.py:51-59`) — archive member paths contain `/`, so this is not optional.
The bounding box has no term in the grammar and is deliberately absent
(`locator.py:21-22`).

The locator is redundant with the structured fields *by construction*, and both
directions are checked: `location_from_mapping` refuses a stored mapping whose stated
`locator` does not re-serialize from its own fields (`locator.py:223-228`), and
conformance rule 4 checks `parse(serialize(x)) == addressing(x)`
(`conformance.py:192-206`). `addressing` (`locator.py:116-131`) strips descriptive
labels off indexed segments and drops the region, because those are the two things
the grammar deliberately cannot carry.

The locator is one of the four inputs to `observation_key`:

```
observation_key = sha256(content_hash ‖ extractor_name ‖ locator ‖ raw_value)
```

(`observation.py:108-118`). `extractor_version` is deliberately excluded so that an
upgraded extractor's row and the row it improves on share one handle — which is what
`store._supersede` (`store.py:421-463`) pairs on, and what `observations_by_key`
(`store.py:206-212`) returns a *list* from. `sha256_of` length-prefixes each part
(`canonical.py:51-59`) because plain concatenation is not injective.

**Why a spanned observation with no unit is unreleasable.** Conformance rule 10:
every observation with a non-null `text_span` must have a `text_units` row on the
*same* `run_id` whose `container_path` equals the observation's, and RAW-1 must hold
against that row's text — `raw_value == unit.text[start:end]`
(`text_units.py:134-163`, reported through `conformance.check_run:285-298`). Without
that anchor, a citation resolves to nothing: the span is an offset into a text that
does not exist, and P8's excerpts, P13's review surface and §8.2's explanations all
cite spans. `check_span_anchor` compares on the *address*, not the record
(`text_units.py:145-153`), because a labelled `slide=6` and a bare `slide=6` are one
address and `(run_id, unit_locator)` is the primary key (`schema.py:123`).

Extractors that emit a value with no span degrade to the coarser address rather than
faking one — e.g. `image.py:193-198` emits the filename-pattern match at
`zone=filename` with no span, because the filename's text unit belongs to the
*filesystem* run and rule 10 keys units on the same run.

### Reliability: an extractor may write two of six

`RELIABILITY_STATES` has six (`vocabulary.py:53-55`); `EXTRACTOR_RELIABILITY_STATES`
has two, `direct` and `possible` (`vocabulary.py:61`). `validated`, `llm_supported`,
`user_confirmed` and `rejected` are fact-layer outcomes. Refused at
`shape.py:190-194` (`ForbiddenReliability`) and again at `conformance.py:165-171`.

In practice `direct` means an explicit labelled machine slot — a PDF metadata key
(`pdf.py:122-128`), a DOCX core property (`docx.py:154-157`), an EXIF tag
(`image.py:180-181`) — and `possible` means free text, OCR, a filename or an
unlabelled position.

### `signal_tier` and `confidence`

`signal_tier ∈ {1,2,3}` carries §2.6's image hierarchy on the record so it is never
re-derived (`vocabulary.py:82`, catalogue in `image.py:46-54`). Rule 11 checks the
structural half only: a non-null tier implies `source_type = "image"`
(`conformance.py:180-190`). P4 authors no EXIF-name-to-tier list; that is P5's
catalogue.

`confidence` is stored with **no asserted range** (`observation.py:169-175`): §3.13
says confidence is not comparable across extractors, so P4 refuses to pretend it is.
Only OCR sets it (`ocr.py:180`).

### D10 — collapsing repeats

One observation per `(run, exact raw value, zone)`; `occurrence_count` counts within
that zone and `location` addresses the first occurrence in document order.
`collapse_key` publishes the tuple (`observation.py:253-260`) but P4 enforces no
uniqueness on it. The collapse itself happens once, for every extractor, in
`ExtractionResult.__post_init__` (`sink.py:33-66`), and its docstring records that
six extractors promised D10 and two delivered it before this moved to the result
object. The collapse also renumbers, so it publishes `collapsed_index` — the map from
submitted position to surviving position — because `long_tail`'s sensitivity signals
carry batch positions (`sink.py:69-94`, consumed at `long_tail.py:346-354`).

Note that `pdf.py:185-226` and `archive.py:195-227` still run their *own* collapse
before handing the batch over. `sink._collapse` is idempotent (it sums
`occurrence_count`), so this is duplication rather than a bug — but it is two
implementations of one rule.

---

## 2.2 The extraction run — why outcomes need their own record

`ExtractionRun` (`runs.py:76-125`) is one row per (file version × extractor).
`runs.py:3-9` states the reason plainly: §2.4 forbids conflating "unsupported format"
with "empty document", §2.5 requires "partially inspected", §2.7 requires
provider/version/languages/configuration/complete-or-capped be preserved, §2.9
requires "indexed-but-unreadable", §8.6 requires the deferred stage be marked — and
**none of those can live on an observation, because the cases that need them produce
zero observations.**

Fields: `run_id`, `file_id`, `content_hash`, `extractor_name`, `extractor_version`,
`source_type`, `analysis_tier`, `config`, `config_fingerprint`, `completeness`,
`coverage`, `observation_count`, `started_at`, `finished_at`, `failure_reason`
(`runs.py:32-36`).

`coverage` is `{units, processed, total}` with `processed ≤ total` enforced
(`runs.py:62-70`, and again at `extractors/runs.py:50-64`). `config` is an opaque
mapping P4 defines no schema for; `config_fingerprint` is
`sha256_of(canonical_json(config))` (`runs.py:46-48`), and P5 *calls* that function
rather than recomputing it — `shape.py:101-124` records the incident where P5's own
`hashlib.sha256` over the same canonical bytes produced a different digest (P4
length-prefixes) and P4 therefore rejected every run P5 emitted.

### The nine `completeness` values

`vocabulary.py:63-68`:

| value | means | who writes it in `src/` |
|---|---|---|
| `complete` | ran to the end | every native extractor's success path |
| `capped` | stopped at a configured ceiling | `ocr.py:188` when the engine reports `capped` |
| `partial` | some parts readable, some not | `archive.py:177-178` only |
| `metadata_only` | deliberate safe stop, no content extractor run | `router.py:185` → `filesystem.unrouted_result` |
| `deferred` | not attempted; budget exhausted first | `budgets.py:75` — **no caller in `src/`** |
| `unsupported` | no extractor exists for this format | `failure.unsupported_result:50-81` |
| `unreadable` | encrypted, malformed, damaged; indexed-but-unreadable | `archive.py:172`, `router.py:184` |
| `failed` | a reader ran and raised | `failure.failed_result:84-104` |
| `dataless` | the bytes are not on this machine | `filesystem.dataless_result:175-231` |

`failure_reason` is free text and is *only* legal on `unreadable` and `failed`
(`runs.py:39`, enforced `runs.py:117-125`). A `capped` run did not fail;
`metadata_only` is a policy stop; `dataless` is not damage. `filesystem.py:208-216`
records that the first version of `dataless_result` wrote a `failure_reason` and P4
rejected it — correctly, because a file in iCloud has not failed.

### The load-bearing principle: a `complete` run with zero observations

`runs.py:16-18`: "A `complete` run that emitted no `metadata` observations IS the
record that the file carried no such metadata; §2.6's 'no EXIF' is exactly this case.
No field is added for it and no observation is written for it."

So three zero-observation states are distinguishable in one query:

- `complete` + 0 observations → the file genuinely contained nothing extractable.
- `unsupported` + 0 observations → **no reader exists in this deployment**; the bytes
  were never looked at (`failure.py:58-62`).
- `metadata_only` + 0 observations → a deliberate stop; the file is still indexed
  through its separate `filesystem` run (`filesystem.py:11-17`).

And `unreadable` is a fourth thing: it carries rows. `ZERO_OBSERVATION_COMPLETENESS`
(`vocabulary.py:75-76`) is `unsupported, deferred, failed, metadata_only, dataless` —
`unreadable` and `partial` are deliberately absent, so an indexed-but-unreadable PSD
keeps its filename and format rows (`filesystem.py:130-156`, fixture 18). Rule 9
checks this at `conformance.py:252-255`.

### Analysis tier

`filesystem | native | ocr | llm` (`vocabulary.py:79`). P5 writes the first three and
`shape.run` raises `ForbiddenAnalysisTier` on `llm` (`shape.py:252-256`).
`extraction_status_by_tier` (`extractors/runs.py:80-101`) folds a file's runs into
the map P1 stores opaquely, and raises `TierConflict` if two runs at one tier
disagree rather than picking a winner. This is why an unrouted or dataless run is
stamped `format.unrouted` at tier `native` rather than reusing `filesystem.record`
(`filesystem.py:32-40` records that the earlier spelling raised `TierConflict` on the
first `.dmg`).

---

## 2.3 Dispatch — how a file reaches an extractor

Two modules, deliberately separate.

**`router.py`** decides. `route()` (`router.py:205-242`) takes an injected
`detect_format`, computes `operative = detected or declared_extension`, records
`disagree` when they differ, looks up `SOURCE_TYPE_BY_FORMAT` (a 50-entry table,
`router.py:40-149`), then `HANDLER_BY_FORMAT` (only `pdf` and `docx` have dedicated
handlers) and finally `HANDLER_BY_SOURCE_TYPE` (`router.py:159-173`). A file with no
handler leaves with `unrouted_completeness` from `UNROUTED_COMPLETENESS`
(`router.py:183-186`): `design_creative → unreadable`, `opaque_binary →
metadata_only`, everything else → `unsupported`. The decision is persisted to P5's
own `extraction_routing` table (`router.py:245-279`), which is not one of P4's three.

The table is honest about its provenance: `router.py:89-115` marks the WebP/GIF/TIFF/
BMP/AVIF/HEIF keys as **inference**, not design text, and `router.py:122-148` does
the same for the five audio/video extensions.

**`dispatch.py`** executes. `extract_initial` (`dispatch.py:153-230`) switches on
`decision.extractor_name`. The interesting case is `text.structured`, which serves
*eight* source types through two halves: `structured_text.py` claims
`text_document, code_structured` and `long_tail.py` claims the other six. Since both
halves answer to one extractor name, the **source type** picks the half
(`dispatch.py:206-225`). `dispatch.py:16-21` records that without this a real corpus
raised `WrongFamily` on its first `.xlsx` while every unit test still passed.

A format nothing supports never reaches this switch — the router already returned
`extractor_name = None`, and `extract_initial:163-165` produces `unrouted_result`
instead. A router that names a handler nothing implements raises `UnknownFamily`
(`dispatch.py:296-307`), which is a `ContractViolation` — a statement about the call,
not the file — and therefore propagates past the orchestrator's catch-all
(`orchestrator.py:312-321`) rather than being recorded as that file's `failed` run.

### Route by extension, not by sniffing

`detect_format` is injected, and the shipped one is:

```python
return {".pdf": "pdf", ".txt": "txt", ".md": "md"}.get(path.suffix.lower())
```

(`cli.py:341-348`). Its docstring states the reason: "sniffing means opening the
file, and the one class of file this command must never open is decided by PATH
(`is_protected_container`) before any format question is asked."

That gate is `safety.admit` (`safety.py:49-70`), called as the **first statement of
every extractor** (`pdf.py:103`, `docx.py:116`, `image.py:133`, `archive.py:121`,
`structured_text.py:109`, `long_tail.py:223`, `ocr.py:152`, `filesystem.py:63`). It
raises `ProtectedContainerRefused` — "There is no override" — before the reader is
touched, and the protected check runs before the dataless check because inside a
protected container P5 must not even stat the contents. `SafetyPolicy`
(`safety.py:38-47`) has exactly two fields "and deliberately no third: a `force`,
`override` or `approved` field would be the override 11 section 4b says does not
exist."

The two refusals are asymmetric, and the orchestrator owns the asymmetry
(`orchestrator.py:594-600`): a protected container produces **nothing at all** — no
run row, no status write — while a dataless file produces one `dataless` run,
because its identity is already known and §8.6 requires unfinished work to stay
visible.

---

## 2.4 The readers layer — every format library is injected

`src/extractors/` imports no third-party library. `reading.py:3-8` states the rule
and `readers/__init__.py:4-12` restates the direction: `readers/` depends on
`extractors/` for the shapes it fills, never the reverse.

`Readers` (`dispatch.py:56-77`) is the injection point — twelve callables:
`read_pdf`, `read_docx`, `read_text_document`, `read_long_tail`, `read_manifest`,
`read_image`, `find_structured_strings`, `recognize_markers`, `dimension_signal`,
`filename_pattern`, and optionally `ocr_engine` + `ocr_config`. `ocr_engine` may be
`None`, which is a *deployment* state: §2.2's and §2.7's OCR routes simply stop, and
no run is written (`dispatch.py:131-132`).

Each reader has a declared return shape as a frozen dataclass: `PdfDocument`
(`pdf.py:56-68`), `DocxDocument` (`docx.py:86-95`), `ImageRecord`
(`image.py:91-106`), `ArchiveManifest` (`archive.py:60-75`), `TextDocument`
(`structured_text.py:87-94`), `LongTailFile` (`long_tail.py:118-125`), `OcrOutput`
(`ocr.py:100-112`). A reader that returns `None` means "this deployment ships no
library for this format" and becomes an `unsupported` run.

### What macOS actually supplies

`readers/deployment.py:59-86` wires exactly three real readers:

- **`read_pdf`** → `pdfminer_reader()` (`readers/pdf_pdfminer.py`). Chosen because
  `Region`'s contract needs per-character font size and position to produce honest
  heading zones (`pdf_pdfminer.py:4-12`). It also renders PDF date syntax into
  `iso_dates` (`pdf_pdfminer.py:63-79`), which is D8's fourth mechanical transform.
- **`read_text_document`** → `read_text_file`, which does one thing: decode UTF-8
  with `errors="replace"`. No heading detection, on purpose (`deployment.py:48-56`).
- **`ocr_engine`** → `vision_ocr()` (`readers/ocr_vision.py`), Apple Vision via
  PyObjC/Quartz. It rasterises PDF pages at the configured DPI
  (`ocr_vision.py:72-86`), numbers regions *within* their page, and flips Vision's
  bottom-left origin to top-left because P4's `Region` carries no origin key
  (`ocr_vision.py:119-141`).

Everything else — `read_docx`, `read_long_tail`, `read_manifest`, `read_image` — is
`_no_reader`, returning `None` (`deployment.py:43-45, 72-76`). `recognize_markers`,
`dimension_signal` and `filename_pattern` are stubs returning `()` / `None`
(`deployment.py:77-82`).

**So on the shipped macOS deployment, only PDF, TXT and Markdown are actually read.**
DOCX, spreadsheets, presentations, email, calendar, contacts, archives and images all
route to a real extractor whose reader returns `None`, and therefore record
`unsupported`.

`VISION_CONFIG` (`deployment.py:36-40`) is `{languages: ["en-US"], dpi: 200,
recognition_level: "accurate"}`. It is a `config` mapping, not constructor arguments,
precisely so it lands in `extraction_runs.config` and is fingerprinted into §3.4's
cache key.

---

## 2.5 Structured strings — the seam P5 ships empty

`StructuredString` (`reading.py:35-47`) is `{kind, start, end}`. Its docstring is
explicit: "no pattern lives in `src/extractors/` and the finder is supplied by the
caller." `find_structured_strings: Callable[[str], tuple]` is a required field of
`Readers` with no default, and `deployment.py:14-19` explains why a default returning
`()` would be *worse* than none: "it silently claims a file contains no URLs, no
emails and no identifiers, and every downstream count would agree with it."

Every text-bearing extractor calls it and places what it returns: `pdf.py:150-167`,
`docx.py:170-175`, `structured_text.py:162-177`, `long_tail.py:307-318`,
`ocr.py:164-181`. Placement is by `ZONE_BY_STRUCTURED_KIND` (`reading.py:56-61`):
`url`, `email`, `doi` → `link`; `citation` → `reference_list`; anything else takes
the zone of the region it was found in.

### What the shipped deployment supplies: one regular expression

`cli.py:188`:

```python
_STRUCTURED = re.compile(r"\b[A-Z][A-Z0-9]*[ -]?[0-9]{3,}\b")
```

`find_structured_strings` (`cli.py:304-307`) emits every match as
`kind="identifier"`. That is the whole of it. No URL pattern, no email pattern, no
DOI pattern, no citation pattern ships — so `ZONE_BY_STRUCTURED_KIND` never fires in
production, and the `link` and `reference_list` zones are unreachable on a live scan.

The comment block (`cli.py:170-187`) records both the posture and one change: the
`[ -]?` separator was added on **2026-08-29** so that `PHYS 1401` and `PHYS-1401`
read as identifiers. The recorded cause is that the first run on a real folder
returned `NothingToDesign` because the files said `PHYS 1401` and the pattern wanted
`PHYS1401`.

Verified behaviour of the current pattern:

| input | matches |
|---|---|
| `PHYS 1401 syllabus` | `PHYS 1401` |
| `Invoice INV20261` | `INV20261` |
| `ABC-4471 x` | `ABC-4471` |
| `see 2026 budget` | *(none)* |
| `Chapter 12` | *(none)* |

A bare year, a page number, a sum of money and ordinary prose are all invisible to
it. So is `phys 1401`, and so is a course code written `Phys 1401`.

---

## 2.6 OCR — policy, the deferred stage, and the two text-layer paths

### The policy module holds no heuristic

`ocr_policy.py` names §2.2's three states (`ocr_policy.py:33-35`):

- `text_layer_absent` — no text at all → route directly to OCR.
- `text_layer_broken` — text exists, but the stored evidence yields no usable facts →
  **targeted** OCR, and only after P6 says so.
- `text_layer_usable` — no OCR.

The state is neither an observation nor a run field. `ocr_policy.py:11-16` is
explicit: an extractor may not write a "no text layer" observation, because an
absence written as evidence is a value P6 can rank. The requirement that the two be
*distinguished* is met by the two paths behaving differently.

There is no language-quality check anywhere in P5, and `ocr_policy.py:18-23` says so
outright — the only permitted input about a non-empty text layer is P6's injected
`no_usable_facts(file_id, content_hash)` verdict, with no default. The threshold
behind that verdict is P5 SPEC Open question 1 and is not answered in code.

### The two passes

`extract_initial` runs the native PDF pass, then calls
`direct_document_ocr_needed(result=...)` (`ocr_policy.py:56-63`) — which is just "did
this run store any non-blank text?" — and OCRs immediately if not
(`dispatch.py:171-181`).

`extract_targeted_ocr` (`dispatch.py:233-272`) is the second, post-P6 pass, PDF-only.
It verifies that the supplied prior result really is *this* file version's native
`pdf.text` run (`dispatch.py:249-260`) and raises `ContractViolation` on any
mismatch, then asks `document_ocr_decision`, which asks `no_usable_facts`.

For **images**, `image_ocr_decision` (`ocr_policy.py:135-149`) fires when the run
yielded no usable text *and* no usable metadata. "Usable metadata" is narrowed to
`signal_tier ∈ {1,2}` (`ocr_policy.py:72, 96-98`) — the docstring at
`ocr_policy.py:75-98` records that counting *any* `zone=metadata` row made §2.7's
main path dead, because `image.py` emits `format` and `pixel dimensions` for every
image and an opaque PNG screenshot therefore always looked like it had metadata.

### The OCR run itself

`extract_ocr` (`ocr.py:140-195`) writes one `text_units` row per recognised page or
region, and observations only for the structured strings found inside them. The
extractor name is built from what the engine reports —
`extractor_name_for("Apple Vision") → "ocr.apple_vision"`
(`ocr.py:120-137`), folding case and word breaks so one engine has one identity
across machines. `extractor_version` is the *provider's*, which is why
`current_versions()` deliberately omits OCR (`dispatch.py:324-328`): P5 cannot state
a version it would have to ask an uninstalled engine for.

`FIELD_HOMES` (`ocr.py:71-81`) maps §2.7's nine required fields onto records P4
already publishes — no OCR-specific record and nothing OCR-specific on an
observation.

An engine that *raises* becomes a `failed` OCR run rather than propagating
(`dispatch.py:115-150`); the docstring records the incident where a raising engine
discarded a native result that had already succeeded.

### The deferred stage and budget exhaustion — the honest answer

`budgets.py` names four §8.6 ceilings in P1's spelling
(`budgets.py:29-34`): `ocr.max_pages_per_file`, `ocr.max_time_per_file`,
`ocr.max_time_per_scan`, `image.max_analysis_ops_per_scan`. A membership check at
import turns a P1 rename into an `ImportError` (`budgets.py:36-41`).

`deferred_result` (`budgets.py:60-76`) is the run for an extractor the budget stopped
*before it started*: zero observations, `coverage 0/total`, and **no
`failure_reason`** — "a deferral carrying a failure reason reads as a failure."
Nothing here downgrades: `budgets.py:12-14` says there is no fallback extractor, no
filename guess, and nothing to downgrade to.

A budget exhausted *mid-read* is a different value: the engine reports `capped` and
the run keeps what it recognised, with `coverage` saying how far it got
(`ocr.py:188-190`). `ocr_vision.py:184-209` is the only place in `src/` that can set
it — it breaks the page loop on `page_cap` or `time_limit_seconds` and sets
`capped=stopped_early`, distinguishing "a limit stopped this" from "the document
ended".

**But:** `VISION_CONFIG` supplies neither `page_cap` nor `time_limit_seconds`
(`deployment.py:36-40`), and `settings.get(...)` therefore returns `None` for both
(`ocr_vision.py:156-157`). And nothing in `src/` imports `extractors.budgets` at all.
So on the shipped deployment, `capped` never occurs and `deferred` is never written.
The SPEC ratification B3 says the four ceilings "stay unset until a real OCR engine
is wired, then chosen empirically" — the engine is wired and the ceilings are still
unset.

---

## 2.7 Golden fixtures — building downstream parts with no extractor present

`evidence_shape/fixtures.py` publishes the SPEC's nineteen worked examples as
constructed records, not files (`fixtures.py:9-12`: a JSON file would need a loader
that reconstructs exactly what this module already constructs). P4's Done-means 9
requires that "P6 resolves `course = BUSIB 4300` from fixture 1 with no extractor
present", and `privacy/fixtures.py:67` shows a downstream part consuming them for
real.

Each `Fixture` (`fixtures.py:56-64`) is a number, the design case it comes from, one
`ExtractionRun`, its observations and its text units. Fixture 1 is the walking
skeleton (a syllabus heading at `page=1/heading=2`); fixture 8 is an OCR region with
a `norm` bounding box and confidence 0.92; fixture 11 is a span into a *filename*;
fixture 17 is a caption addressed by `time_span`; fixture 18 is an `unreadable` run
that still carries a metadata row; fixture 19 is a `metadata_only` run with no
observations at all.

The coverage shortfall is **computed and published rather than filled**
(`fixtures.py:14-17`, `fixtures.py:247-260`). Verified by running it: the fixtures
cover 10 of the 15 zones — `path`, `header_footer`, `link`, `annotation` and
`reference_list` have no worked example — and 13 of the 14 source types (`contacts`
is missing). No fixture carries a `signal_tier`, because §2.6 makes
`DateTimeOriginal` both camera EXIF and a capture time and the design does not settle
which tier wins (`fixtures.py:19-22`).

---

## 2.8 The write seam

An extractor returns one `ExtractionResult` — run + observations + text units, none
carrying a `run_id` (`sink.py:22-31`). `RunWriter` (`store.py:360-419`) is the sink:
it mints the `run_id`, refuses a batch that carries one (`store.py:387-395`),
validates the whole batch through `validate_run` *before* the run row exists, then
writes run → text units → observations → the one §8.2 event, in one transaction.

The event is last because its evidence reference is the observation keys, which do
not exist until the rows do (`store.py:9-13`, `record_run_event:95-117`). P4 authors
no event: `author` is required at construction and `P1` is refused
(`evidence_shape/authorship.py`), because M8 says the acting part authors and P1
writes.

`record_observation` (`store.py:120-145`) recomputes the run's `observation_count`
from the rows on every insert — a stored count that disagrees with the rows is a fact
nobody downstream can use.

`observation_keys_for_run` (`store.py:174-198`) orders by `rowid`, and its docstring
records the bug that made this necessary: it once ordered by `observation_id`, a
uuid4, so `long_tail`'s sensitivity signals attached to the wrong values.

Conformance is twelve rules (`conformance.py:43-71`). `check_observation` reports
*every* violation before raising (`conformance.py:8-9`), because a gate that stops at
the first problem makes an extractor author fix one thing per run. Rule 8
(determinism) needs two runs and lives in `determinism.py`; its comparison excludes
`run_id`, `observed_at` and `file_id` (`determinism.py:53`) and keys on four fields
rather than rule 8's stated three — `determinism.py:17-23` reports that SPEC/design
discrepancy rather than resolving it.

---

## 2.9 Inert surface — concepts with no live reader

Verified by grepping `src/` for callers:

- **`extractors/budgets.py` entirely.** Nothing imports it. `deferred_result`,
  `p5_ceilings` and `extraction_counts` have no caller, so the `deferred`
  completeness value is unreachable on any live scan and the four §8.6 ceilings are
  never read from P1.
- **`extractors/stage_output.py` entirely.** `extraction_stage_output` and
  `extractor_versions` have no caller in `src/`; §8.5's extraction envelope is never
  produced live. `facts/stage_output.py:10` cites it as the pattern it follows.
- **`extractors/runs.py:analysis_tier_for`** — no caller. It would also `KeyError` on
  `format.unrouted`, which is a name `current_versions()` publishes
  (`dispatch.py:339`).
- **`extractors/runs.py:cache_key`** — no caller. §3.4's cache key is never computed.
- **`evidence_shape/determinism.py`** — `observation_set_digest` and
  `assert_identical_observation_sets` have no caller in `src/`. Rule 8 is never
  checked outside tests.
- **`evidence_shape/conformance.py:validate_observation`** — no caller; only
  `validate_run` is used (via `RunWriter`).
- **`extractors/events.py`** — says so itself at `events.py:24-25`: "NOTHING IN
  `src/` CALLS EITHER ONE."
- **`ocr.PERSISTED_FIELDS` / `ocr.FIELD_HOMES`** — documentation tables with no
  reader in `src/`.
- **`observation.SECTION_2_8_LINES`**, **`observation.collapse_key`**,
  **`router.routing_decisions`**, **`safety.UNTOUCHED_PROTECTED`** — no `src/`
  caller.
- **`ZONE_BY_STRUCTURED_KIND`'s four keys** — live code, but unreachable in
  production, because the only shipped pattern emits `kind="identifier"`.
- **Vocabulary members nothing writes:** `deferred`; the `heading`-only subset of
  `LABEL_SEGMENT_KINDS` is used, but `cell`, `layer` and `artboard` segment kinds are
  written by no extractor in `src/`; the `header_footer` zone is written only by
  `docx.py` (whose reader is unwired), and `annotation`, `link` and `reference_list`
  likewise.

---

## What looks wrong here

1. **`vocabulary.py:63` says "B1's eight" above a tuple of nine values.** The P5 SPEC
   Done-means 1 also says "one of the eight enumerated values" and the P4 SPEC's
   `completeness` table lists eight rows — `dataless` (ratified C4, 2026-08-20) was
   added to the code and not to either table. `stage_output.py:56` and
   `stage_output.py:91` say nine. Two documents and one comment disagree with the
   code.

2. **The whole budget layer is inert, and `capped` is unreachable on the shipped
   deployment.** `VISION_CONFIG` (`deployment.py:36-40`) passes no `page_cap` and no
   `time_limit_seconds`, and nothing imports `extractors.budgets`. P5 SPEC Done-means
   9 requires "the 400-page fixture is marked `capped` rather than `complete`"; live,
   a 400-page scanned PDF is OCRed to the end with no ceiling. §8.6's
   "89 scanned PDFs deferred after the OCR limit" line cannot be produced.

3. **A scanned PDF in a deployment with no OCR records `complete`.**
   `extract_pdf` hardcodes `completeness="complete"`
   (`pdf.py:178`) regardless of whether any text came out, and if `ocr_engine` is
   `None` the OCR run simply does not happen (`dispatch.py:131-132`). P4's own
   semantics say `complete` + zero observations means "the file genuinely contained
   nothing extractable" (`runs.py:16-18`) — which is precisely the false statement
   §2.4 exists to prevent. The same applies to `docx.py:213`,
   `structured_text.py:185`, `image.py:206` and `long_tail.py:328`: five of the six
   native extractors can only ever write `complete`.

4. **Images reach OCR because a reader is missing, not because the image is
   opaque.** `read_image` is `_no_reader` (`deployment.py:75`), so `extract_image`
   returns `unsupported_result` with zero observations and zero text units
   (`image.py:137-142`); `image_ocr_decision` then sees no text and no
   tier-1/2 metadata and returns `run_ocr=True` (`ocr_policy.py:143-149`). Every
   routed image on the live deployment therefore produces
   `image.metadata · unsupported` plus a full Apple Vision run. §2.7's trigger is
   being satisfied by a deployment gap rather than by a fact about the image.

5. **`_detect_format` recognises three extensions**, so `disagree` is always `False`
   and `detected_format` is `NULL` for everything except `.pdf`, `.txt`, `.md`
   (`cli.py:341-348`). P5 SPEC Done-means 10 ("routing follows signature over
   extension on the disagreeing fixture") cannot be exercised live, and
   `router.route`'s detected-wins branch (`router.py:214-215`) is dead in production.
   The `unreadable` path in `unrouted_result` also emits its `format` observation
   only `if detected` (`filesystem.py:147-156`), so an indexed-but-unreadable file
   gets a filename row and no format row.

6. **Targeted OCR is switched off by a lambda.** `usable_threshold=lambda facts,
   unresolved: True` (`cli.py:392`) with the comment "targeted OCR is never
   triggered". So §2.2's `text_layer_broken` path — the whole reason
   `no_usable_facts`, `extract_targeted_ocr`, `authoritative_result` and the
   two-phase orchestrator exist — never fires. A large amount of machinery
   (`dispatch.py:233-272`, `store.py:272-302`, `orchestrator.py:660-706`) is live
   code reachable only by changing that lambda.

7. **One shipped regular expression is the entire structured-string catalogue.**
   `\b[A-Z][A-Z0-9]*[ -]?[0-9]{3,}\b` (`cli.py:188`) means the product's *only*
   in-document evidence beyond metadata and headings is an uppercase-then-digits
   token. It misses `Phys 1401`, every URL, every email address, every DOI and every
   citation — and `deployment.py:14-19` argues at length that a finder returning `()`
   would be a lie, which is close to what a finder this narrow does for most content.
   It will also match `A 1234` in ordinary prose.

8. **D10 is implemented twice.** `sink._collapse` (`sink.py:69-94`) collapses every
   batch, and `pdf._collapse` (`pdf.py:185-226`) and `archive._collapse`
   (`archive.py:195-227`) collapse again beforehand with a slightly different
   mechanism (candidate objects vs. dicts). The result is idempotent today, but this
   is exactly the "one concept, two homes" defect the codebase's comments repeatedly
   name as its costliest.

9. **D10 collapses across container paths, and rule 10 is checked only on the
   survivor.** The key is `(zone, raw_value)` (`sink.py:83-84`) with no container
   path. Two identical strings in two different table cells become one observation
   whose `location` addresses the first — which is D10 as specified, but it means
   `occurrence_count` silently spans places the record no longer names, and P6's
   §3.7 zone weighting sees one row where the document had two positions.

10. **`ExtractionResult.__post_init__` mutates a frozen dataclass** via
    `object.__setattr__` on every construction (`sink.py:61-66`), including
    overwriting the `observation_count` the extractor computed. The count on the run
    is therefore never the extractor's own number, which contradicts
    `stage_output.py:117-140`'s claim that it is ("Both are P4's own numbers, counted
    by the extractor").

11. **`extraction_counts` exists twice under two owners.** `budgets.py:79-103` (P5,
    uncalled) and `eval_harness/counts.py:31-73` (P2, called) compute §8.6's line
    with different bucket sets — P2's version added a `dataless` bucket that P5's
    lacks, and P2's own docstring admits its `files_indexed` disagrees with P5's
    mapping and reports both.

12. **The fixtures do not meet P4's Done-means 5.** It asks for "all 14 zones and all
    14 source types"; there are 15 zones (`vocabulary.py:22-26`) and the fixtures
    cover 10 of them and 13 of 14 source types. The shortfall is honestly published
    (`fixtures.py:255-260`) rather than hidden — but a downstream part built only
    against fixtures has no worked example for `link`, `annotation`,
    `reference_list`, `header_footer`, `path` or `contacts`.

13. **`analysis_tier_for` would crash on a name the same package publishes.**
    `ANALYSIS_TIER_BY_EXTRACTOR` (`extractors/runs.py:17-24`) has no entry for
    `format.unrouted`, which `current_versions()` returns (`dispatch.py:339`) and
    which every unrouted and dataless run carries. The function has no caller today,
    so this is latent rather than live.

14. **`observation_count` is corrected by the sink but `coverage` is not.** An
    `unsupported` run reports `coverage {files, 0, 1}` (`failure.py:78`) while a
    `complete` PDF reports `{pages, n, n}` (`pdf.py:178`) — the `units` string is
    caller-supplied with no vocabulary (`runs.py:56`), so `files`, `pages`,
    `entries`, `images` and `paragraphs` all appear. Any consumer aggregating
    coverage across runs is adding incommensurable numbers.

15. **`UNREPORTED_PROVIDER_NAME = "ocr"`** (`ocr.py:56`) is stamped as the
    `extractor_name` when an engine crashes before reporting itself, and the module
    flags its own spelling as unsettled ("Whether this is the right spelling is a
    vocabulary question -- see NEEDS-JOSEPH"). It is also the one `extractor_name`
    that does not match `OCR_EXTRACTOR_PREFIX = "ocr."`, so
    `analysis_tier_for("ocr")` would fall through to the dict and `KeyError`.
