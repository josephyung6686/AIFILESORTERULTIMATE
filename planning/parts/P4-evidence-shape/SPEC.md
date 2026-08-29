# P4 — Evidence shape

Owns: §2.8
Status: contract draft

## Purpose

§2.8 exists for one reason, stated in its first sentence: *"Every extractor should emit evidence in a
common format so later domain templates, validation rules, and LLM prompts do not need separate logic
for PDFs, DOCX files, images, archives, or OCR."* P4 publishes that format and nothing else.

This is the most depended-on contract in the system. Six extractors (P5, §2.1–§2.7) write to it, every
long-tail format extractor writes to it (§2.9, final paragraph), the whole fact layer reads it (P6,
§3.2), the validator resolves LLM citations against it (§3.6, §4.8, §6.10, §7.9), the privacy gate
redacts at its granularity (§8.4), and the replay harness diffs extractor versions by comparing sets of
it (§8.5). The segmentation map makes the ordering explicit: *"the shape precedes the extractors"* —
written afterwards, six extractors invent six shapes and every consumer grows per-format branches,
which is exactly what §2.8 forbids.

P4 requires no extractor to exist. It is schema, vocabulary, serialization, invariants and fixtures. It
can be frozen before P5 begins, and P6 can be built entirely against its fixtures.

## Design slice owned

§2.8 in full: the observation record's field list, the raw/normalized separation, the prohibitions, and
the location examples. §2.9's final paragraph, which binds every long-tail extractor to the same shape.
§2.2's five location requirements (document zone, page number, text offset, surrounding context,
occurrence count), which are the only place the design states what a location must contain.

### Design decisions made here, and alternatives rejected

§2.8 gives location *examples*, not a scheme. Designing one uniform scheme is explicitly in P4's scope.
Everything below is a decision made by P4, not something the design states. Each is constrained to
vocabulary the design already names.

**D1 — Location is a structured record, not a per-format string.**
`location = { zone, container_path[], text_span | time_span, region }` plus a canonical string
serialization (the *locator*). One shape for all source types.
*Rejected:* a free-form human string per format (`"page 1, heading 2"`). It forces every consumer to
parse per-format text — the exact per-format branching §2.8 exists to prevent — and §3.7's positional
weighting cannot compare a parsed string against another format's parsed string.
*Rejected:* a tagged union with one variant per source type (`PdfLocation | DocxLocation | ...`). Every
consumer then carries a switch over source types. §2.8 forbids that; it also means adding an EPUB
extractor (§2.9) edits P6, P7 and P8.

**D2 — `zone` is a closed, format-independent vocabulary; `container_path` is an ordered list of typed
segments.** The zone answers *what kind of place* (which §3.7 weights); the container path answers
*which one* (which §8.2 explanations cite). Both vocabularies are closed and owned by P4; an extractor
may not add a value. Adding one is a P4 contract revision and a shape-version bump.
*Rejected:* an open zone string. Six extractors then produce `heading`, `Heading`, `hdg`, `h1` and
§3.7's weighting table has no stable key.

**D3 — Container-path indices are 1-based; text offsets are 0-based half-open.**
§2.8's own examples are 1-based (`page 1, heading 2`; `table 3, row 2, column 1`) and appear in
user-visible explanations (§8.2). Offsets are machine-only, and 0-based half-open makes
`raw_value == text[start:end]` hold in every mainstream language.

**D4 — Text offsets are counted in Unicode scalar values (code points), not bytes and not UTF-16 code
units.** §2.2 says "text offset" without a unit. §2.7 requires CJK language support, so the unit must
be language-stable, and D9's raw-value invariant must hold for CJK and emoji alike.

**D5 — Two records for outcomes, not one: `evidence` (the observation) and `extraction_runs` (the run
that produced a batch of them).** A third record, `text_units`, holds bulk text — see D12.
§2.4 forbids conflating "unsupported format" with "empty document"; §2.5 requires
"partially inspected"; §2.7 requires provider, version, languages, configuration and "whether
extraction was complete or capped" be preserved; §2.9 requires "indexed-but-unreadable"; §8.6 requires
the deferred stage be marked. None of those can live on an observation, because the cases that need
them produce **zero** observations.
*Rejected:* replicating provider/version/config/completeness on every observation — redundant on a
1,000-observation PDF and structurally impossible at zero observations.
*Rejected:* keeping run state private to P5 — then P6 cannot tell "no course code found" from "the
extractor does not exist yet" (§2.4), and §8.6's user-facing count *"18 files remain unreadable"* has
no source.
`extraction_runs` is **the** extraction-outcome record for the whole system: P5 writes one row per
(file version × extractor) and publishes no parallel status vocabulary of its own. An opaque image
runs the image extractor and OCR, which is two rows — one may be `complete` while the other is
`capped`. A per-file record cannot express that, which is why this one is per-run.

**D6 — `source_type` uses §2.9's own format families; `zone` says where inside the source.** §2.8 lists
both fields separately, and its examples ("a PDF match", "an image observation", "an archive
observation") are format families. Taking §2.9's bullet list verbatim avoids inventing a taxonomy.

**D7 — The `field` segment carries the source format's own slot name, verbatim, never a product field
name.** This is how a value that arrives in a named slot (EXIF `DateTimeOriginal`, `dc:title`, email
`Subject`, ICS `DTSTART`, an archive's file count) says which slot it came from, with no separate
field. Product fields are P6's `fields` table and §3.12 forbids creating them automatically.

**D8 — Extractor-time normalization is mechanical only.** §2.8 assigns entity normalization
("U Chicago" → "University of Chicago") to *"a resolver"*, and §3.2 puts the resolver after extraction.
So `normalized_value` at P4 may only carry format-mechanical transforms: Unicode NFC, whitespace
collapse, soft-hyphen/line-break repair, and an ISO-8601 rendering of a timestamp the source stored as
a structured date. It may not resolve entities, expand abbreviations, or parse a date out of free text
(§3.10 forbids fuzzy date parsing).

**D9 — `raw_value` is exactly the span; context is stored beside it, never around it.**
`context_before` and `context_after` are separate fields, so `raw_value` stays character-exact (§2.8)
and §8.4 can redact a value without dropping its context, or the reverse.

**D10 — One observation per (run, exact raw value, zone); `occurrence_count` counts within that zone;
`location` addresses the first occurrence in document order.**
*Rejected:* one observation per occurrence — a 300-page document mentioning "Columbia" 400 times
produces 400 rows, against §8.6's ceilings.
*Rejected:* one observation per value per file — destroys §2.2's entire point, that a page-one heading
outweighs a page-eighteen reference list.
Collapsing is on **exact** raw match, because P4 makes no normalization judgement (§2.8). `Columbia`
and `columbia` are two observations. Cross-form aggregation is P6's (§3.7 word-boundary matching and
ranking).

**D11 — Extractors may write only two of §3.13's six reliability states.** See *Reliability state*
below. Confirmation needed from P6 — recorded in Open questions.

**D12 — Bulk extracted text is a third record, `text_units`, keyed by `(run_id, container_path)`.**
§2.2 requires "complete text by page", §2.4 requires text-bearing files' full text, §2.7 requires
"raw recognized text". None of those is a *located value*, so none is an observation — yet D1's
`text_span` is defined as an offset into a stored, addressable text unit, so the unit must exist and
must be addressed by the same `container_path` vocabulary the observation uses. P4 owns the span
semantics, so P4 owns the unit.
*Rejected:* one observation per page of text. A page is not a value; §2.8's `raw_value` would then
mean two different things, and D10's collapsing rule and §8.6's ceilings both break.
*Rejected:* leaving it to P5 per extractor. Six extractors then store text six ways, and §8.4's
redaction unit, §4.4's "short evidence excerpts" and §8.5's "did the expected text appear?" each
grow a per-format branch — the outcome §2.8 exists to prevent.
*Rejected:* P1's file record. Text is per (content version × extractor × configuration), not per
file: a text-layer pass and an OCR pass over the same PDF produce two different texts, and §8.2
requires both remain available.

### Not owned here

Which strings an extractor should look for (§2.2's "other structured strings", §2.3 tables, §2.6 EXIF
hierarchy, §2.7 OCR triggering) — P5. Fields, values, facts, positional weights, gazetteers, word-
boundary rules (§3.1–§3.14) — P6. Handling classes (§8.4) — P7. Dossier construction and citation
checking (§3.6, §4.8) — P8. File identity, path history and the event log (§8.2) — P1. Filesystem
attributes and the stat cache (§1.2, §2.9's "basic filesystem extraction") — P3; P4 references them by
`file_id`, it does not restate them.

## Contract in

P4 consumes contracts; it consumes no runtime output, which is why it can be frozen first.

| From | What P4 requires | §  |
|---|---|---|
| P1 | `file_id` (internal file ID) and `content_hash` + hash algorithm as the durable identity of a file version | §8.2 |
| P1 | An append-only event log accepting an `extraction` and an `OCR` event with an evidence reference | §8.2 |
| P1 | Supersede-never-overwrite semantics: a newer result retains the older one plus the reason it was superseded | §8.2 |
| P3 | `files` rows populated with path, filename, normalized filename, extension, MIME type, size, timestamps, parent-folder context | §1.2, §2.9 |
| P3 | Stat-cache semantics: unchanged size+mtime reuses results; either changed forces recompute | §1.2 |
| P2 | Replay bundles carry observation sets and diff them across extractor versions, which requires deterministic serialization and an identity stable across versions | §8.5 |
| P6 | The reliability-state vocabulary (six states) | §3.13 |
| P6 | The `evidence` table name and its stated columns: source, location, surrounding text, extractor version, content hash | §3.12 |
| P7 | Redaction operates on individually addressable excerpts, not whole documents | §8.4 |

## Contract out

### Record 1 — `evidence` (the observation)

The table name is the design's (§3.12: *"**evidence** — stores raw observations from extractors,
including the source, location, surrounding text, extractor version, and content hash"*). The field
list is §2.8's, in §2.8's order, plus additions the design separately requires (marked ✚).

```jsonc
{
  "observation_id":   "uuid",            // unique per row; P4-assigned
  "observation_key":  "sha256:…",        // ✚ D-stable identity, see below

  // ── §2.8 field list ───────────────────────────────────────────────
  "file_id":          "uuid",            // File identifier      §2.8, §8.2
  "content_hash":     "sha256:…",        // Content hash         §2.8, §8.2
  "extractor_name":   "pdf.text",        // Extractor name       §2.8, §2.7
  "extractor_version":"3.1.0",           // …and version         §2.8, §3.4
  "source_type":      "text_document",   // Source type          §2.8, §2.9
  "raw_value":        "BUSIB 4300",      // Raw value            §2.8
  "normalized_value": "BUSIB 4300",      // Normalized candidate §2.8  (nullable)
  "location":         { … },             // Location             §2.8, §2.2
  "context_before":   "Syllabus — ",     // Surrounding context  §2.8, §2.2
  "context_after":    " — Spring 2026",  //   "                  §2.8, §2.2
  "context_truncated": false,            // ✚ §8.6 (never truncate silently)
  "occurrence_count": 3,                 // Occurrence count     §2.8, §2.2
  "observed_at":      "2026-08-19T…Z",   // Observation time     §2.8
  "reliability":      "possible",        // Reliability state    §2.8, §3.13

  // ── required elsewhere in the design ──────────────────────────────
  "run_id":           "uuid",            // ✚ FK → extraction_runs      D5
  "confidence":       0.92,              // ✚ §2.7 "confidence information" (nullable)
  "signal_tier":      null,              // ✚ §2.6 signal hierarchy (nullable)  M2
  "supersedes":       null,              // ✚ §8.2 supersession pointer, inverse
  "superseded_by":    null,              // ✚ §8.2 supersession pointer
  "supersede_reason": null               // ✚ §8.2 "the reason it was superseded"
}
```

§2.8 says *"At minimum, every observation should contain…"*, which is what licenses the ✚ additions;
each traces to a section that requires the information be preserved.

**The three context fields are the published shape of §2.8's single "Surrounding context" line** (D9).
A consumer or extractor author reproducing §2.8's eleven-field list must name `context_before`,
`context_after` and `context_truncated`, not one "surrounding context" field; a single-field emission
fails conformance rule 1.

**The three supersede columns are P1's published set** — `supersedes`, `superseded_by`,
`supersede_reason` — adopted here verbatim. The fourth column P1 publishes, `preferred`, is **not** an
observation field: §8.2 says *"the resolver may mark the newer value as preferred"* and §3.2 places
the resolver after extraction, so preference lives on P6's `file_facts`. See *Provenance* below.

`observation_key = sha256(content_hash ‖ extractor_name ‖ locator ‖ raw_value)`, deliberately **excluding
`extractor_version`**. §8.5 requires the replay harness to compare a new extractor version against a
prior result for the same content; identity that includes the version makes every row a false diff.
Version differences are visible in the rows, not in the key. This is a **deliberate divergence from
P2**, whose replay bundle keys its extraction output by content hash *plus* extractor version: the
bundle names *which run* is being compared while the key names *the same observation across runs*, so
carrying the version in both would leave nothing to diff against — the exclusion is intentional and is
not a bug to be fixed (MINOR 8, 05-minor-resolutions.md).

**`observation_key` is the citation handle.** Every consumer that cites evidence — P6's `evidence_refs[]`
(§3.6), P8's dossier citations (§4.4, §4.8), P9's group support (§4.5), P11's placement explanations
(§6.10, §7.9) — cites the **key**, never `observation_id`. `observation_id` is a per-row primary key
that dies on extractor upgrade; §8.7 requires a negative example recorded today to still resolve after
that upgrade, and only the content-addressed key satisfies it.

`observed_at` is wall-clock time at extraction. It is not the document's date, not the file's
timestamp, and must never be used as evidence about the file's content (§3.2's `DateTimeOriginal` →
`capture date` example; §3.10's narrow date rule).

**`signal_tier ∈ {1, 2, 3}`, nullable, §2.6-scoped.** §2.6 states a three-level hierarchy for image
signals and P4 carries it as a field rather than making P6 re-derive it: tier 1 is camera EXIF
(*"strong photo evidence"*), tier 2 is capture time, GPS and sensor-shaped dimensions (*"reinforce
it"*), tier 3 is exact display resolutions, PNG format and software metadata (*"may support a
screenshot hypothesis"*). Re-deriving the hierarchy downstream from `extractor_name` plus the `field`
label would encode §2.6 in a second place and drift from it. The field is **null on every observation
outside §2.6's image hierarchy** and is not a general-purpose strength score; `reliability` states the
kind of slot the value came from, `confidence` is the extractor's own number, and neither is
comparable to a tier. The tier is an input to P6's weighting and ranking (§3.7), never a conclusion:
§2.6's *"conflicting signals should lead to abstention rather than an invented classification"* is
resolved by P6's minimum-score-and-margin rule (§3.7), not by any field on the observation.

### The location addressing scheme

One shape for every source type (D1).

```jsonc
"location": {
  "zone": "heading",                       // closed vocabulary, below   §2.2 "document zone"
  "container_path": [                      // ordered, outermost → innermost
    { "kind": "page",    "index": 1 },     //                            §2.2 "page number"
    { "kind": "heading", "index": 2, "label": "Course Information" }
  ],
  "text_span": { "start": 0, "end": 10 },  // nullable                   §2.2 "text offset"
  "time_span": null,                       // nullable, ms               §2.9 audio/video
  "region":    null,                       // nullable                   §2.7 bounding boxes
  "locator":   "heading:page=1/heading=2#0-10"
}
```

- `text_span` — 0-based, half-open, Unicode scalar values (D3, D4), offsets into the **text unit named
  by the innermost container segment** (that page, that cell, that OCR region, that transcript).
- `time_span` — `{ start_ms, end_ms }`, integer milliseconds from media start. §2.9's audio/video row
  requires captions, subtitles and transcripts to emit this same shape; those have no page and no
  document-text offset.
- `region` — `{ x, y, w, h, unit }` where `unit ∈ {px, norm}`. §2.7: *"locations or bounding boxes where
  available"*. Null when the OCR provider does not report one.
- `locator` — canonical string, below. Redundant with the structured fields by construction; it exists
  because §8.2 provenance events, §4.4 dossiers and §3.6/§4.8/§6.10/§7.9 citation checks all need one
  short stable handle.

### Zone vocabulary (closed)

Every zone is a place the design names as carrying evidence. Nothing here is invented; the citation is
where the design names that place.

| zone | means | named at |
|---|---|---|
| `filename` | the file's own name | §2.2, §2.9, §3.1 |
| `path` | parent-folder context — §1.2's "directory position" and §2.9's "parent-folder context" are one field, published under §2.9's name (MINOR 11) | §2.9 "parent-folder context", §1.2 "directory position", §3.1 "user-approved folder" |
| `metadata` | a named property slot: document core properties, EXIF, ID3, email headers, ICS fields, workbook properties | §2.2, §2.3, §2.6, §2.9, §3.1 |
| `title` | the document title | §2.2, §3.2, §3.13 (a Direct source) |
| `heading` | a heading at any level | §2.2, §2.3, §2.8 ("heading 2") |
| `body` | ordinary body text / paragraphs | §2.2 "complete text by page", §2.3, §3.7 |
| `table` | a table cell or table label | §2.3, §2.8 ("table 3, row 2, column 1"), §3.1 |
| `header_footer` | running headers and footers | §2.3, §3.7 "a footer" |
| `notes` | speaker notes | §2.9 presentations |
| `link` | a URL, email address, DOI or hyperlink | §2.2, §2.3 |
| `annotation` | comments and revision metadata | §2.3 |
| `reference_list` | a citation / reference list | §2.2 ("a reference list on page eighteen"), §2.2 "citations" |
| `manifest` | an archive manifest entry or property | §2.5, §2.8 ("a manifest path") |
| `ocr` | recognized text from OCR | §2.7, §2.8 ("an OCR region"), §3.1 |
| `transcript` | subtitles, captions, speech-to-text | §2.9 audio/video |

P4 publishes the vocabulary. P6 owns what each zone is *worth* (§3.7 positional weighting) — a page-one
`heading` outweighing a `reference_list` on page eighteen is §2.2's example and §3.7's rule, not P4's.

### Segment kinds (closed)

| kind | addressed by | label carries | named at |
|---|---|---|---|
| `page` | index | — | §2.2, §2.7 |
| `slide` | index | slide title | §2.9 presentations |
| `sheet` | index | sheet name | §2.9 spreadsheets |
| `heading` | index (ordinal within parent) | heading text | §2.8, §2.3 |
| `paragraph` | index | — | §2.3 |
| `table` | index | — | §2.8 |
| `row` | index | — | §2.8 |
| `column` | index | column header text | §2.8, §2.9 "column headers" |
| `cell` | index | notebook cell type | §2.9 notebooks |
| `region` | index (ordinal of recognized region) | — | §2.7, §2.8 |
| `layer` | index | layer name | §2.9 design/creative |
| `artboard` | index | artboard name | §2.9 design/creative |
| `field` | **label** | the source format's own slot name, verbatim (D7) | §2.8 (`DateTimeOriginal`), §2.9 |
| `entry` | **label** | member path inside an archive | §2.5, §2.8 |
| `key` | **label** | structured-data key path | §2.9 "schema keys" |

Rules:
1. Outermost → innermost order. Every prefix of a valid path is itself a valid coarser address.
2. A kind with an index is addressed by its index; its label is descriptive only and never appears in
   the locator. A label-addressed kind (`field`, `entry`, `key`) has no index.
3. Native addresses go in the label: a spreadsheet cell is `sheet=2/row=7/column=3` with
   `label: "C7"` on the column segment, not a separate `cell` kind.
4. **Unknown structure degrades to a coarser path; it never invents a kind.** An extractor that can
   locate a value on a page but not within it emits `container_path: [{page, 4}]`.
5. Adding a zone or a kind is a P4 contract revision plus a shape-version bump. An extractor that needs
   one and ships it locally has broken the contract for every consumer.

### Locator serialization

```text
locator   := zone [ ":" segments ] [ "#" text_span | "@" time_span ]
segments  := segment ( "/" segment )*
segment   := kind "=" addr
addr      := <1-based decimal integer>     ; indexed kinds
           | <escaped label>               ; field | entry | key
text_span := start "-" end                 ; 0-based code points, half-open
time_span := start_ms "-" end_ms           ; integer milliseconds
```

Escaping, in labels only: percent-encode `%` `/` `=` `#` `@` `:` and any control character as `%XX`,
uppercase hex, over UTF-8 bytes. Archive member paths contain `/` and this is not optional.

Serialization is canonical and deterministic: the same location always produces the same string, and
parsing a locator reproduces the structured record exactly.

```text
filename                                    the filename itself
filename#0-6                                first six code points of the filename
title:page=1                                the document title
heading:page=1/heading=2                    §2.8's "page 1, heading 2"
table:page=4/table=3/row=2/column=1         §2.8's "table 3, row 2, column 1"
metadata:field=DateTimeOriginal             §2.8's EXIF example
metadata:field=dc%3Atitle                   colon escaped
manifest:entry=docs%2Ftranscript.pdf        §2.8's "a manifest path"
ocr:page=4/region=2#0-24                    §2.8's "an OCR region"
body:page=18#12043-12051                    §2.2's page-eighteen reference
table:sheet=2/row=7/column=3                a spreadsheet cell
notes:slide=6#0-42                          speaker notes
transcript@252500-255200                    a caption at 04:12.5–04:15.2
```

### Raw vs normalized vs display (§2.8)

§2.8: *"If a document says `U Chicago`, the raw observation remains exactly that wording, while a
resolver may normalize it to `University of Chicago` and the user may later choose to display it as
`UChicago`."* Three forms; P4 stores **two**.

| form | field | owner | rule |
|---|---|---|---|
| raw — `U Chicago` | `raw_value` | P4 / P5 | Exactly the source substring. No case folding, no Unicode normalization, no whitespace collapse, no trimming. |
| normalized candidate — `University of Chicago` | `normalized_value` | P4 carries it; P6's resolver fills the semantic form (§2.8, §3.2) | A **candidate**. Nullable. Never authoritative, never replaces raw. Extractor-time normalization is mechanical only (D8). |
| display — `UChicago` | *not a P4 field* | P6 / P10 | An alias (§0 "taxonomy aliases", §3.12 values, §8.7 user vocabulary). It is a user preference, not evidence. |

Invariants:

- **RAW-1.** For any observation with a `text_span`, `raw_value` is byte-for-byte the substring of the
  stored text unit at that span. This is machine-checkable and is the anchor for every citation check
  in §3.6, §4.8, §6.10 and §7.9.
- **RAW-2.** `raw_value` is never updated, ever. A better extractor emits a **new** observation and a
  new run; the old row survives with `superseded_by` set and `supersede_reason` recorded (§8.2's own
  example: a first OCR pass producing unreadable text and a later engine recovering a university name
  must *both* remain available).
- **RAW-3.** `normalized_value = null` is always legal. An extractor that cannot normalize safely
  leaves it null rather than guessing (§3.10).
- **RAW-4.** Normalization is always redoable, because raw is always present.

### Occurrence count (D10)

`occurrence_count` is the number of times this exact raw value occurred **within this zone** in this
run. `location` addresses the **first** occurrence in document order, where document order is the
extractor's traversal order and must be stable across runs for the same content hash (required by §3.4
caching and §8.5 replay). The same value in two zones is two observations with two counts — which is
what lets §2.2's rule work at all.

### Reliability state (§2.8 field, §3.13 vocabulary)

The field uses §3.13's six-state vocabulary — the only reliability vocabulary the design defines.
Extractors may write **only two of them** (D11):

| state | an extractor may write it when | §3.13's own definition |
|---|---|---|
| `direct` | the value came from an explicit, labeled, machine-structured slot: a metadata/EXIF field, the document title, a labeled form field, a manifest entry, a content hash | *"Read from a reliable and explicit source"* |
| `possible` | the value was recovered from free text, OCR, a filename, or any unlabeled position | *"A useful but insufficient clue"* |

`validated`, `llm_supported`, `user_confirmed` and `rejected` are **fact-layer outcomes** and P4 rejects
an observation carrying them. §3.5 assigns them: rules produce validated facts, the LLM produces
LLM-supported facts, the user produces user-confirmed facts. §2.8 forbids extraction from treating model
output as proof. Note the mapping is about the *source slot*, not the *value*: a course code in
page-eighteen body text is `possible`; the same string in `metadata:field=Subject` is `direct`.

`confidence` is extractor-reported (§2.7 requires it be preserved for OCR) and is **not comparable
across extractors**. §3.13: *"The product may calculate internal numeric scores… but the stored record
must preserve the kind and quality of evidence behind the conclusion."*

### Record 2 — `extraction_runs` (D5)

One row per (file version × extractor), and **the** extraction-outcome record for the system — there is
no second, per-file status vocabulary anywhere (B1). Which extractor a file is routed to is P5's
(§2.9's routing table); what happened once it ran is this row. It scopes a batch of observations and
carries everything that is true of the *attempt* rather than of any one value — including when there
are zero observations.

```jsonc
{
  "run_id":            "uuid",
  "file_id":           "uuid",                //                        §8.2
  "content_hash":      "sha256:…",            // extraction is per content version §2.1, §8.2
  "extractor_name":    "ocr.apple_vision",    //                        §2.7 "provider"
  "extractor_version": "2.4.1",               //                        §2.7, §3.4
  "source_type":       "ocr",                 //                        §2.9
  "analysis_tier":     "ocr",                 // §3.4 cache key; closed: filesystem | native | ocr | llm (I4)
  "config":            { "dpi": 200, "languages": ["en","zh-Hans"],
                         "recognition": "accurate" },  // §2.7 "languages, configuration"
  "config_fingerprint":"sha256:…",            // so §3.4's key and §8.5's diff can tell configs apart
  "completeness":      "capped",              // closed vocabulary, below
  "coverage":          { "units": "pages", "processed": 40, "total": 312 },
  "observation_count": 118,
  "started_at":        "2026-08-19T…Z",
  "finished_at":       "2026-08-19T…Z",
  "failure_reason":    null                   // free text, only when completeness ∈ {unreadable, failed}
}
```

`completeness` (closed):

| value | means | required by |
|---|---|---|
| `complete` | the extractor ran to the end of the file | §2.7 "complete or capped" |
| `capped` | stopped at a configured ceiling; `coverage` says how far it got | §2.7, §8.6 ("89 scanned PDFs deferred after the OCR limit") |
| `partial` | some parts were readable and some were not | §2.5 "partially inspected" |
| `metadata_only` | deliberate safe stop: the format is indexed at metadata level and no content extractor was run | §2.9 (disk images, executables, databases, encrypted containers, damaged files, unknown binary) |
| `deferred` | not attempted; the budget was exhausted before it started | §8.6 "mark the deferred stage" |
| `unsupported` | no extractor exists for this format | §2.4, §2.9 |
| `unreadable` | encrypted, password-protected, malformed, damaged | §2.5, §2.9 "indexed-but-unreadable" |
| `failed` | the extractor errored | §2.4 (an error is not an empty document) |

**A `complete` run with zero observations means the file genuinely contained nothing extractable. An
`unsupported` run with zero observations means no extractor exists.** §2.4 requires these be
distinguishable: *"an empty extraction result is different from an extractor that does not yet exist."*
This distinction is why D5 exists.

`metadata_only` is the third member of that family and is not the same as either: it is a **deliberate
policy stop**, not a gap in the product and not an empty file. §2.9 makes it the default for disk
images, executables, databases, encrypted containers, damaged files and unknown binary formats
*"unless a dedicated extractor has been explicitly approved"*. Such a file is still indexed — §2.9's
opening requires every file to receive basic filesystem extraction — so it carries the
`source_type: filesystem` observations that record surfaces (fixture 11), while the format-specific
extractor emits none.

**Absence is recorded here or nowhere.** A `complete` run that emitted no `metadata` observations *is*
the record that the file carried no such metadata; §2.6's "no EXIF" is exactly this case. No field is
added for it, and no observation is written for it — see *What an observation may not do* below.

### Record 3 — `text_units` (D12, G1)

The home for the bulk text §2.2, §2.4 and §2.7 require extractors to produce. One row per addressable
text unit an extraction run emitted, keyed by `(run_id, container_path)` — the same container-path
vocabulary the observation uses, so a unit and the observations that point into it are addressed
identically.

```jsonc
{
  "run_id":         "uuid",                       // FK → extraction_runs        D5
  "container_path": [ { "kind": "page", "index": 4 } ],  // the unit's address; [] = whole file
  "unit_locator":   "page=4",                     // canonical serialization of container_path
  "text":           "…",                          // the unit's text, exactly as extracted
  "length":         1274,                         // Unicode scalar values       D4
  "truncated":      false                         // §8.6 — never truncate silently
}
```

What each design requirement maps to:

| design requires | rows emitted |
|---|---|
| §2.2 "complete text by page" | one row per page: `container_path: [{page, N}]` |
| §2.4 full text of a text-bearing file | one row with `container_path: []` (the whole file) |
| §2.7 "raw recognized text" | one row per OCR page or region: `[{page, N}]` or `[{page, N}, {region, M}]` |
| §2.9 transcripts, captions, subtitles | one row per transcript: `container_path: []` on the transcript run, with observations addressed by `time_span` |

Rules:

1. **A unit exists for every span.** An observation whose `text_span` is non-null must have a
   `text_units` row on the same `run_id` whose `container_path` equals the observation's
   `location.container_path`. This is what makes RAW-1 machine-checkable: `raw_value ==
   text[start:end]` on that row, in code points (D4).
2. **An extractor that cannot address text finely emits a coarser unit**, and its observations degrade
   to the same coarser path (segment-kind rule 4). It never invents a finer unit to justify a span.
3. **Context may cross the unit boundary.** `context_before` / `context_after` are drawn from the
   surrounding document text and are not required to lie inside the unit — which is why D9 stores them
   beside `raw_value` rather than as offsets.
4. **Text is per run, not per file.** A text-layer pass and an OCR pass over the same PDF produce two
   different texts under two `run_id`s, and §8.2 requires both remain available. Superseding a run
   never rewrites or deletes the earlier run's units (RAW-2's rule, applied to text).
5. **Never silently truncated** (§8.6). If a storage ceiling cuts a unit, `truncated: true` and
   `length` is the stored length. A truncated unit invalidates no observation whose span lies inside
   the stored prefix; an observation whose span lies beyond it is not written.
6. **Always local** (§8.4). *"Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS…
   should remain local."* `text_units` is that store. §4.4's "short evidence excerpts" and §8.4's
   *"selected excerpts, redacted identifiers"* are **cut from** these rows by P8 under P7's gate; the
   rows themselves never leave the machine and are never sent to a model.
7. **No plan-version state, no deletion.** Same as the observation record: keyed by run, never by plan
   (§8.8); superseded, never removed (§8.2).

This settles what P4's own largest open question asked and what §8.4, §4.4 and §8.5 each depended on:
P7's redaction unit is the observation plus the unit it points into, P8 cuts excerpts from the unit,
and §8.5's *"Did the expected text appear?"* is a query against `text_units`.

### §2.7's required OCR fields, mapped

§2.7 enumerates exactly what the database must preserve for OCR. Every item lands somewhere in the two
records, with no OCR-specific shape:

| §2.7 requires | lives at |
|---|---|
| OCR provider and version | `run.extractor_name`, `run.extractor_version` |
| languages, configuration | `run.config`, `run.config_fingerprint` |
| page or image reference | `location.container_path` → `page=N` / `region=N` |
| raw recognized text | `text_units.text` (per page or region); `raw_value` on the pointed observations |
| locations or bounding boxes where available | `location.region` |
| confidence information | `confidence` |
| whether extraction was complete or capped | `run.completeness`, `run.coverage` |

### `source_type` vocabulary (§2.9's families, closed)

`filesystem` (§2.9 "basic filesystem extraction"), `text_document`, `spreadsheet`, `presentation`,
`image` (§2.6), `ocr` (§2.7), `email`, `calendar`, `contacts`, `code_structured`, `audio_video`,
`design_creative`, `archive`, `opaque_binary` (§2.9's disk images / executables / databases / encrypted
containers / damaged / unknown row).

OCR output is `source_type: "ocr"`, never the underlying format — including OCR over a scanned PDF.
§2.2 requires "no text layer" and "broken text layer" be distinguishable, and §8.5 requires evaluation
decomposed by stage; both fail if OCR observations are indistinguishable from text-layer observations.

### What an observation may not do (§2.8, verbatim prohibitions)

§2.8: *"Extraction does not create a final folder path, invent domains, merge all files that share one
string, or treat model output as proof."* Enforced as schema-level rejections:

| Prohibition | Enforcement |
|---|---|
| **No folder path.** | The record has no destination, path-proposal or node field. A `path` zone addresses where the file *is* (§2.9 parent-folder context), never where it should go. |
| **No domains.** | No domain, category, field-name or fact field. §3.12: fields are never created automatically; §3.11 activates domain schemas at the fact layer, not here. |
| **No merging across files.** | An observation references exactly one `file_id` and one `content_hash`. There is no multi-file observation, and two files sharing a raw value share nothing structurally — that link, if any, is P6's or P9's. |
| **No model output as proof.** | An extractor may not write `llm_supported` (or `validated` / `user_confirmed` / `rejected`). Model-derived conclusions are facts (§3.5) and pass P8's validator (§3.6) before they exist. |

Three more, derived from sections outside §2.8 and stated here because six extractors need them:

- **No negative observations.** An observation records presence, never absence. §2.6 forbids treating
  the absence of EXIF as proof of anything. Absence lives on the run record (`completeness`,
  `coverage`, and the fact that a `complete` run emitted no such row) or nowhere. An extractor may not
  write an "EXIF absent", "no text layer" or "metadata stripped" observation; the run record already
  says it, and an absence written as evidence is a value P6 can rank.
- **No conflict observations, and no resolution of one.** §2.6's conflicting signals — camera EXIF and
  an exact display resolution on the same image — are emitted as **two observations with two
  `signal_tier` values**, never as a third "conflict" row and never as a classification. §2.6's
  *"abstention rather than an invented classification"* is produced by P6's minimum-score-and-margin
  rule (§3.7) reading those two rows. An observation is a reading, not a comparison of readings.
- **No plan-version state.** No group id, node id, template id, or plan id. §3.14 keeps facts separate
  from the destination tree; §8.8 keeps the evidence database shared across plan versions.
- **No deletion.** Observations are superseded, never removed (§8.2). §8.7 requires that rejected
  proposals *"must be stored with the evidence that produced them"*; deleting evidence decays every
  negative example that depends on it.

### Worked examples, one per source type

Abbreviated to the discriminating fields. These are the fixture set (see *Done means*).

| # | source_type | locator | raw_value | reliability | design case |
|---|---|---|---|---|---|
| 1 | `text_document` | `heading:page=1/heading=2` | `BUSIB 4300` | `possible` | §2.8 "page 1, heading 2"; §3.2's syllabus. `context_before: "Syllabus — "`, `context_after: " — Spring 2026"` |
| 2 | `text_document` | `title:page=1` | `BUSIB 4300 Syllabus` | `direct` | §3.2 "the PDF title" |
| 3 | `text_document` | `body:page=18#12043-12051` | `Columbia` | `possible` | §2.2's page-eighteen reference list |
| 4 | `text_document` | `table:table=3/row=2/column=1` | `Wash U` | `possible` | §2.8's DOCX example; §2.3 tables |
| 5 | `text_document` | `heading:page=1/heading=1` | `Please tell us what you are interested in studying at college and why.` | `possible` | §2.3's `Wash U.docx` heading |
| 6 | `text_document` | `metadata:field=Producer` | `python-docx` | `direct` | §2.2 — `direct` describes the *slot*, not the value's usefulness; P6 discounts it (§2.2, §2.3) |
| 7 | `image` | `metadata:field=DateTimeOriginal` | `2026:07:17 14:03:22` | `direct` | §2.8's EXIF example; §3.2's capture-date derivation |
| 8 | `ocr` | `ocr:page=4/region=2#0-24` | `Your Columbia University` | `possible` | §2.8's "OCR region"; §7.8's admissions screenshot |
| 9 | `archive` | `manifest:entry=docs%2Ftranscript.pdf` | `docs/transcript.pdf` | `direct` | §2.8's "manifest path"; §2.5's `submission.zip` |
| 10 | `archive` | `manifest:field=file_count` | `37` | `direct` | §2.5 "file count" — D7's `field` segment |
| 11 | `filesystem` | `filename#0-6` | `Wash U` | `possible` | §2.2, §2.9 filename as evidence |
| 12 | `spreadsheet` | `table:sheet=2/row=7/column=3` | `2025` | `possible` | §2.9 "dates or identifiers from labeled cells" |
| 13 | `presentation` | `notes:slide=6#0-42` | *(speaker note text)* | `possible` | §2.9 presentations |
| 14 | `email` | `metadata:field=Subject` | `Columbia Application — Next Steps` | `direct` | §2.9 email |
| 15 | `calendar` | `metadata:field=DTSTART` | `20260717T140000Z` | `direct` | §2.9 calendar |
| 16 | `code_structured` | `metadata:field=name` (in `key=dependencies`) | `react` | `direct` | §2.4, §2.9 package manifests |
| 17 | `audio_video` | `transcript@252500-255200` | *(caption text)* | `possible` | §2.9 audio/video |
| 18 | `design_creative` | `metadata:layer=3` | *(layer name)* | `direct` | §2.9 design/creative. On an unsupported proprietary format the run is `unreadable` and **still carries these metadata-level rows** — §2.9's "indexed-but-unreadable" (M3) |
| 19 | `opaque_binary` | — | *(no observations from this extractor)* | — | run: `completeness: metadata_only` — §2.9's safe default for disk images, executables, databases, encrypted containers, damaged files, unknown binary. The file is still indexed through its `filesystem` observations (fixture 11) |

**Walking-skeleton fixture.** The segmentation map's skeleton is *"extract page-one text; emit ONE
observation in the frozen shape"* → example 1 above, with a `complete` run and the one `text_units`
row its span indexes into. Its context is `context_before: "Syllabus — "`, which carries one of §3.5's
five required academic context terms — *"syllabus," "lecture," "credits," "instructor," or
"semester"* — so P6 can resolve it rather than being obliged to refuse it (B8a). That also makes the
fixture §3.2's own worked case. P6 resolves it to one validated fact (`course = BUSIB 4300`) with its
evidence link; P2 replays and asserts it. This fixture is the integration test every later part keeps
green.

### Conformance

A validator, shipped with P4, rejects a non-conforming observation. Six extractor authors run it as
their gate; P6, P7 and P8 may assume it passed.

1. Every §2.8 field present — with `context_before`, `context_after` and `context_truncated` as three
   fields, not one (M5); nullable only where stated.
2. `zone`, all `kind`s, `source_type`, `reliability`, `completeness` drawn from the closed vocabularies.
3. `reliability ∈ {direct, possible}` on any row written by an extractor.
4. `locator` round-trips: serialize → parse → structurally equal.
5. RAW-1 holds wherever `text_span` is non-null.
6. Exactly one `file_id`; no destination, domain, field-name, group, node, template or plan reference.
7. `occurrence_count ≥ 1`.
8. Same content hash + same extractor version + same config fingerprint ⇒ byte-identical observation
   set (§3.4 caching, §8.5 replay).
9. `run.completeness` present; **`unsupported`, `deferred` and `failed` runs carry zero observations.**
   `unreadable` and `partial` runs **may and normally do** carry observations: §2.9 requires an
   unsupported proprietary format be *"recorded as indexed-but-unreadable rather than silently treated
   as empty"*, and its metadata-level rows — *"at minimum filename, format, dimensions or canvas
   properties, embedded metadata"* — are what "indexed" means. A rule forbidding them would make an
   indexed PSD indistinguishable from a file nobody opened, which is the conflation §2.4 forbids.
   **`metadata_only` carries ZERO observations from the stopping extractor** — settled 2026-08-20,
   because this sentence and the SPEC's own worked example 19 said opposite things and six extractors
   would have run the gate. Example 19 is the frozen reading: the run records the deliberate stop and
   emits nothing, while the file stays indexed through its `filesystem` observations (example 11),
   which P3 already produced and P5 re-emits under O5. Keeping the metadata rows on the *stopping*
   run instead would put §2.9's basic filesystem record in two homes and make `complete`-with-zero,
   `unsupported` and `metadata_only` indistinguishable — the three states §2.4 and §2.9 require be
   told apart.
10. Every observation with a non-null `text_span` has a `text_units` row on the same `run_id` whose
    `container_path` equals the observation's, and RAW-1 holds against that row's `text` (D12).
11. `signal_tier` is null unless the observation is one of §2.6's image-hierarchy signals; where
    present it is `1`, `2` or `3`.
12. No observation carries an absence, a conflict, or a resolution of a conflict (§2.6).

## Deferred — manual design required

None of the following is P4's to author, and P4 invents no part of it. Listed with the § that defines
each, so no other part assumes P4 supplied it.

| Deferred | Defined by | Note |
|---|---|---|
| The 200–300 domain template library | §5.7 | P10. §5.7 itself says the product "does not need to fully implement every template at launch". |
| Domain fact-schema fields beyond §3.11's literal six-row table | §3.11 | P6. §3.11 anticipates "many specialized fields" but authors none. |
| Gazetteer contents (institution, course, company, venue name lists) | §3.7 "validated gazetteers" | P6. P4 stores raw values; it matches nothing against any list. |
| Residual library contents beyond §7.3's nine named templates | §7.2–§7.4 | **P10** — M10 moved the residual-library definitions (the nine names, their attribute slots, and the enable/rename/relocate model) from P11 to P10; P11 keeps the §7.5–§7.11 workflow. |
| Which structured strings each extractor should recognize | §2.2 "other structured strings", §2.3–§2.7, §2.9 | P5, per format. P4 fixes the shape, not the catalogue. |
| MIME/signature → extractor routing table | §2.9 | P5. |
| Date-candidate regular expressions and academic-term patterns | §3.10 | P6. Directly bounds `normalized_value`: without them, D8 holds and extractors leave dates from free text unnormalized. |
| Numeric values for every §8.6 ceiling, including the `context_before`/`context_after` budget | §8.6 ("configurable ceilings") | P4 fixes the fields and the truncation flag; the numbers are configuration. |
| Positional weights per zone | §3.7 | P6. P4 publishes the vocabulary these weights key on. |

## Done means

1. `evidence` and `extraction_runs` schemas exist, with every §2.8 field and every closed vocabulary.
2. The conformance validator exists and enforces all twelve rules above; it fails a non-conforming
   observation rather than coercing it.
3. Locator serialize/parse round-trips, with a passing escaping test on an archive path containing
   `/`, `=`, `#` and a non-ASCII segment.
4. RAW-1 verified on a CJK fixture and an emoji fixture (D4's code-point unit).
5. All 19 fixtures above exist as golden files with golden locators, covering all 14 zones and all 14
   source types, including fixture 19's `metadata_only` run with no extractor-emitted observations, and
   fixture 18's `unreadable` run that still carries its metadata-level rows (§2.9, M3).
6. Negative tests pass: an extractor cannot write `validated` / `llm_supported` / `user_confirmed` /
   `rejected`; an observation cannot reference two files; an observation cannot carry a path, domain,
   field name, group, node or plan reference; an observation cannot record an absence or a conflict
   (§2.6); a `complete` zero-observation run, an `unsupported` zero-observation run and a
   `metadata_only` run are three distinguishable states (§2.4, §2.9).
7. Supersession test: a second run's observation on the same content leaves the first row's
   `raw_value`, `location`, `occurrence_count`, `observed_at` and `extractor_version` untouched and sets
   `superseded_by` + `supersede_reason` on the old row and `supersedes` on the new one (§8.2), leaving
   both runs' `text_units` rows readable.
8. Determinism test: two runs at the same content hash, extractor version and config fingerprint
   produce byte-identical observation sets.
9. **The independence test the segmentation map requires:** P6 resolves `course = BUSIB 4300` from
   fixture 1 with no extractor present — which it can, because fixture 1's context carries §3.5's
   "syllabus" term (B8a) — and a P5 author can write a conforming extractor from this document plus the
   fixtures without asking P4 a question.
10. `text_units` exists and is exercised: a per-page unit (§2.2), a whole-file unit (§2.4) and a
    per-region OCR unit (§2.7); rule 10 fails an observation whose span has no unit; a truncated unit
    sets `truncated: true`; and two runs over one PDF — text layer and OCR — leave two independent unit
    sets readable (§8.2).

## Cross-cutting answers

### Provenance (§8.2)

**Events appended.** Every `extraction_runs` row appends one §8.2 event — `extraction`, or `OCR` when
the extractor is OCR; both names are §8.2's own, spelled exactly as §8.2 spells them (MINOR 2,
05-minor-resolutions.md). The event carries §8.2's required payload: event type, file ID, content
hash, responsible subsystem, extractor version, time of observation, and *"a structured explanation
or evidence reference"* — which is where P4 contributes: the reference is `run_id` plus the
`observation_key`s (or a `locator` for a single cited value). It is the **key**, never
`observation_id` (M14). Old and new paths do not apply; `prompt fingerprint` does not apply (P4 is
model-free); `user identity` does not apply (see Correction learning).

**Never overwritten.** `raw_value`, `location`, `occurrence_count`, `observed_at`, `extractor_name`,
`extractor_version`, `run_id`. Improvement is **insert + supersede**, never update — §8.2: *"if a first
OCR pass produces unreadable text and a later improved OCR engine recovers a university name, both
extraction records should remain available."*

**Not P4's to write.** §8.2 continues: *"The resolver may mark the newer value as preferred."* Preference
is therefore a resolver concern; there is no `preferred` field in the observation, and it is the one
column of P1's published four that the evidence layer does not adopt (M1). P4 records what was read and
what superseded it — `supersedes`, `superseded_by`, `supersede_reason` — and P6's `file_facts` decides
which one wins.

### Budgets and degradation (§8.6)

**Ceilings P4 owns.** The `context_before`/`context_after` length budget (configurable per §8.6), and
D10's collapsing rule, which is itself a ceiling: a value occurring 400 times in one zone is one row
with `occurrence_count: 400`, not 400 rows.

**Ceilings P4 does not own but must express.** §8.6's "maximum pages OCRed per file", "maximum OCR time
per file", "maximum OCR time per scan", "maximum image-analysis operations per scan" are P5's to
enforce. P4's obligation is that their effect is *recorded*: `run.completeness ∈ {capped, partial,
deferred}` with `run.coverage` (`processed` / `total`), which is what makes §8.6's user-facing statement
— *"1,842 files indexed; 1,611 fully extracted; 89 scanned PDFs deferred after the OCR limit… 18 files
remain unreadable"* — computable rather than estimated.

**Never silent.** §8.6: a prompt *"should not truncate silently in a way that removes the decisive
evidence."* At P4's layer: `context_truncated` is mandatory whenever context was cut, a stored text
unit that was cut is marked `truncated`, and a capped run must be marked capped. An observation whose
context was truncated is still a complete observation — `raw_value` is never truncated.

**Degradation must not become lower quality.** §8.6: *"Cost exhaustion must never turn into
lower-quality automatic classification."* Concretely, a capped or deferred run:
- emits **no** observations for units it did not read — it never interpolates or extrapolates;
- does **not** lower `reliability` to compensate, and does not raise it to make a thin result usable;
- leaves the shortfall visible as `completeness` + `coverage` so P6 abstains (§3.6) rather than
  concluding from partial evidence.

### Correction learning (§8.7)

**User actions P4 records: none.** Every action §8.7 enumerates — accepting or rejecting a group,
excluding a packet member, renaming a branch, merging or splitting, changing template order, creating a
custom template, moving a residual file, choosing a shallow fallback, keeping a file in place, marking a
file private, disabling a suggestion type — belongs to P6, P7, P9, P10 or P11. None of them changes what
a document says.

**Why none, structurally.** A user correcting a value corrects the **fact**, never the observation.
§3.13's `user_confirmed` is a fact state; §2.8 forbids overwriting raw. If an extractor misread the
document, the design's mechanism is supersession by a better extractor (§8.2), not editing the record of
what was read. Whether a user may author or correct an observation *directly* is unsettled — Open
questions.

**What P4 must guarantee so §8.7 works.** §8.7 requires that *"Rejected groups, rejected destination
matches, rejected labels, and rejected residual recommendations must be stored with the evidence that
produced them. Otherwise the system will repeatedly resurface the same attractive but incorrect
grouping."* That imposes two obligations on P4:
1. `observation_key` is stable and permanently resolvable, so a negative example recorded today still
   resolves after an extractor upgrade.
2. Observations are never deleted, only superseded — otherwise every stored negative example decays
   into a dangling reference and the rejected proposal returns.

**Scope.** P4 records no correction at any scope (file / group / node / template / domain / corpus). It
supplies the stable evidence handles that corrections at every scope point back to.

### Plan versioning (§8.8)

**None of P4's state belongs to a plan version.** §8.8 settles this directly: *"The evidence database
remains shared across plan versions, but the destination tree and user policy define which projections
are valid in each version."* Observations and extraction runs are keyed by content hash and extractor
version (§3.4), not by plan.

Consequences, all binding on P5:
- Creating, editing, restoring or adopting a plan version never re-runs, invalidates, re-scopes or
  rewrites an observation. §8.8: *"A new plan should never silently reclassify or move old files."*
- The observation record carries no plan-version-scoped identifier — no node id, group id, template id
  or plan id (also required by §2.8's prohibitions and §3.14).
- A plan-version diff (§8.8) never shows evidence changes, because evidence is not part of a plan
  version. It shows renames, moves, template changes and files needing renewed review.
- The reverse also holds: a new extractor version adds observations to the shared database without
  invalidating any plan version. Plans see the improvement through P6's resolver, at review, not through
  a silent rewrite.

## Open questions

Each is unsettled by the design, and each blocks or endangers a named neighbouring part.

**Settled since the draft, and removed from this list.** *Where does bulk extracted text live, and who
owns it?* — settled by **G1**: it is P4's, as the `text_units` record above (D12). It was the largest
open question in P4's area and it blocked the walking skeleton. *Which identifier do consumers cite?* —
settled by **M14**: `observation_key`. *Does the observation carry §2.6's signal tier?* — settled by
**M2**: yes, `signal_tier`, and P5 records it among its own settled-since-the-draft entries. *May an `unreadable` run carry observations?* — settled by
**M3**: yes, at metadata level. *What is the supersede column set?* — settled by **M1**.

1. ~~**The extractor-tier vocabulary is never enumerated.**~~ **Settled — I4** ([`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md)).
   `analysis_tier ∈ filesystem | native | ocr | llm`. P5 owns the vocabulary and writes the first three;
   P8 writes `llm`. A value outside the four is rejected. `source_type` remains a different field.

2. ~~**Is an observation owned by the content hash or by the file record?**~~ **Settled — ratified
   2026-08-20: the CONTENT HASH owns the observation.** Two file records with the same content hash
   share one observation set, and a fact derived on one applies to the other. The file identifier stays
   on the observation as §2.8 requires, but it is a way in, not the owner — which is why P4's contract
   was buildable either way. This follows §2.1's *"read each file once per content version"* and §8.2's
   same-content-new-path rule, and it means a duplicate is never re-extracted. Consequences to carry:
   P5 re-extracts per content version, not per path; P6 attaches facts to the hash; P11's §6.9
   multi-home file has one evidence set with several homes.

   *The original, now-superseded wording is kept below for provenance. It describes the question as
   unsettled; it is settled. Nothing in the paragraph that follows is in force.* — §2.8's field list contains
   both. §2.1 says the engine should *"read each file once per content version"*; §8.2 says *"If the
   same content appears at a new path, the system recognizes it as the same file version."* Together
   those imply one observation set per content hash, shared by every duplicate file — but §2.8 still
   requires a file identifier on each observation. Unsettled: whether two file records with the same
   content hash share one observation set, and whether a fact derived on one applies to the other.
   *Threatens P1 and P3 (identity), P5 (re-extraction), P6 (does a fact attach to a hash or a file?),
   P11 (§6.9 multi-home files).* P4's contract carries both fields, so it is buildable either way — but
   only one answer is correct.

3. ~~**Do observations and facts share one reliability vocabulary?**~~ **Settled — ratified 2026-08-20. See *Ratified decisions* at the end of this file; that table is what is in force. The original wording follows.** **One vocabulary: §3.13's six, with extractors stamping only `direct` | `possible`.** §2.8 puts a "reliability state" on
   the observation; §3.13 defines six reliability states for *file facts*. The design never says they
   are the same vocabulary. P4 reuses §3.13 and restricts extractors to `direct` and `possible` (D11)
   because the field is mandatory and must have a domain — but this needs P6's confirmation, and if P6
   defines a separate observation-level vocabulary, D11 and conformance rule 3 change.
   *Threatens P6 and P5.*

4. **Is the §8.4 handling class stored per observation or only per file?** §8.4 says the system should
   *"classify data into handling classes"* without naming the granularity; §8.2's file record carries a
   single "Sensitivity state". But §8.4 also requires that only *"selected excerpts, redacted
   identifiers"* reach a cloud model, which is observation-granular. P4 adds no privacy field (P7 owns
   handling classes) and instead guarantees that observations are individually addressable by locator
   and joinable by `file_id`, and that the text they point into is addressable by
   `(run_id, container_path)`, so either answer is implementable. *Threatens P7 (where the class is
   stored) and P8 (what unit it redacts).*

5. ~~**May a user author or correct an observation directly?**~~ **Settled — ratified 2026-08-20. See *Ratified decisions* at the end of this file; that table is what is in force. The original wording follows.** **No — a user corrects the FACT at P6, never `raw_value`; a better pass supersedes.** §8.7 enumerates user actions and none is
   "correct an extracted value"; §3.13's `user_confirmed` is a fact state; §2.8 forbids overwriting raw.
   Unsettled: whether a user who sees an OCR misread can write a corrected observation (with what
   `extractor_name` and what reliability state), or whether the only route is a user-confirmed fact at
   P6. *Threatens P6 (§3.13 semantics) and P7 (§8.4's "reclassify a file as private").*

6. ~~**What `completeness` does a source that is not on this machine carry?**~~ **Settled — ratified 2026-08-20. See *Ratified decisions* at the end of this file; that table is what is in force. The original wording follows.** **A ninth value, `dataless`, carrying zero observations.** macOS "Optimize Mac
   Storage" leaves a Finder entry whose bytes are not local; hashing or opening it triggers a
   download, which [`../../11-ops-runtime.md`](../../11-ops-runtime.md) §5 forbids. None of the eight
   values fits: `deferred` is budget exhaustion (§8.6), `unreadable` is encrypted-or-damaged (§2.5,
   §2.9), `metadata_only` is a format decision (§2.9). The design does not contemplate a
   not-downloaded source, so P4 does not invent a ninth value here. Until this closes, P3 records the
   detection and no `extraction_runs` row is written for such a file. *Threatens P3 (detection),
   P5 (the writer of runs), and §8.6's progress line, which cannot name the category without it.*

---

## Ratified decisions — 2026-08-20 (second session)

Joseph's answers to this plan's NEEDS JOSEPH list. Each is binding; the PLAN was made to
follow, and its guards were updated rather than left asserting a superseded reading.

| ID | Decision | Consequence in the contract |
|---|---|---|
| **A1** | Conformance **rule 8 keys on four fields**, not three: `content_hash`, `extractor_name`, `extractor_version`, `config_fingerprint`. | Rule 8's three-field sentence is unsatisfiable as written — `observation_key` includes `extractor_name`, so two extractors could never produce one identical set. `REPLAY_KEY_FIELDS` carries the four §3.4 names. **Rule 8's text should gain the fourth name.** |
| **A2** | A span into a **filename** does require a `text_units` row. | Keeps exactly one way to resolve a citation. Cost is one small row. |
| **A3** | A run with **zero observations may still keep its text units**. | Otherwise §8.5's *"did the expected text appear?"* has nothing to query. `check_run` constrains units by run and address, never by count. |
| **A4** | A routed-but-stopped run carries `analysis_tier: native`. | Which extractor was routed is the fact §2.4 wants preserved: *"an empty extraction result is different from an extractor that does not yet exist."* |
| **B4** | The §8.6 context budget gets **P1's sixteenth ceiling key**, `evidence.context_window`, **and** goes in the run's `config` so it is fingerprinted. | A ceiling outside the fingerprint makes two runs at different context widths look identical to §3.4's cache key and §8.5's replay — a silent wrong answer. P4 still holds no number: the value arrives as data. |
| **B8** | **Done-means 5 is amended.** The nineteen worked examples cover the zones and source types the table reaches, not "all 14". | The five missing zones (`path`, `header_footer`, `link`, `annotation`, `reference_list`) and `contacts` are authored **when P5 actually extracts those formats**, from real output. P4 stays the owner of the shape; P5 supplies the first honest instance. Inventing them now would have six extractor authors building against a fabrication. |
| **C1 (OQ3)** | **One reliability vocabulary.** §3.13's six, and extractors may stamp only `direct` \| `possible`. | Confirms what D11 and conformance rule 3 already implement. **P6's SPEC must state it** so nobody grows a seventh enum. A PDF heading must not be born `validated`. |
| **C2 (OQ4)** | **Not yet ratified — P7 decides.** Direction of travel: **file class as default, observation-level override.** | §8.4's excerpt redaction needs per-observation granularity; a file-only class cannot send page 1 to a model while holding back page 3. P4 added no privacy field, so both remain addressable. Must be settled **before P7's schema.** |
| **C3 (OQ5)** | **No — a user corrects a fact, never an observation.** | §8.7 lists no "correct an extracted value"; §3.13's `user_confirmed` is a fact state; §2.8 forbids overwriting `raw_value`. A better OCR pass **supersedes** (new row, old readable) per §8.2. A second way to mint evidence would fight RAW-2. |
| **C4 (OQ6)** | **Settled — a ninth `completeness` value: `dataless`.** | None of the eight meant "the bytes are not on this machine": `deferred` is budget, `unreadable` is damage, `unsupported` is a missing extractor. The word is `dataless` because P1 (`DatalessFileRefused`), P3 (`scan_agent.dataless`) and `11-ops-runtime.md` §5 already use it — coining `not_local` beside them would be two vocabularies for one concept. It carries **zero observations** and P2's count line gained `runs_dataless`. |

**Also settled here:** `metadata_only` carries **zero** observations from the stopping extractor
(rule 9's note and worked example 19 disagreed; example 19 is the frozen reading), and the file
stays indexed through its `filesystem` observations.
