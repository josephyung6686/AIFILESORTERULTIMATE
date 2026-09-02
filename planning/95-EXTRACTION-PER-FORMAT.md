# 95 — What extraction actually does, per format

**Measured 2026-09-03.** The owner's question was *"I don't know how good the extraction
system is"*, and nobody on this project did. This is the answer, per format, with the
method attached so it can be re-run rather than believed.

Everything below is a measurement unless it is marked **reasoned**, which means it was
read off the code path because no real file of that kind could be produced on this
machine. There are three such rows and they say so.

---

## 1. Method

**Corpus.** 17 real files, and *real* is the whole point — a corpus of stub bytes measures
the stub. `textutil` wrote the `.rtf`, the `.docx` and a genuine Word 97 `.doc`;
`cupsfilter` wrote a multi-page PDF with a real text layer; Quartz rendered that PDF to a
bitmap and re-wrapped it as an image-only PDF (the scanned case) and wrote a JPEG carrying
real EXIF including a GPS tag; `openpyxl` wrote the `.xlsx` **at fixture time only**, never
as a runtime dependency; the `.pptx` and the ODF files are OOXML and ODF written by hand,
which is also what pins the format contract. Generator: `make_corpus.py` in the extraction
scratchpad.

**Harness.** `measure.py`. It drives the **shipped** router (`extractors.router.route` with
`cli._detect_format`) and the **shipped** readers (`readers.deployment.macos_readers`). Only
two things are substituted: P3's two safety predicates, because nothing in the corpus is
protected or dataless, and `find_structured_strings`, which the CLI supplies too.

**Columns.** `completeness / coverage / observations / characters of stored text`.
"BEFORE" is the state on 2026-09-02, before `8dca892`, `4a9682e` and `7b25e27`.

**A second corpus, in the proportions of the owner's own disk** (25,770 files counted;
1:100 scale — 11 PDFs, 8 PNG, 2 JPG, 6 txt, 5 md, 5 csv, 5 docx, 2 html, 11 extensionless,
8 wav) is §4.

---

## 2. The table

| file | routed to | what a person would reasonably expect | BEFORE | AFTER |
|---|---|---|---|---|
| `PHYS 1401 syllabus.txt` | `text.structured` | the words | complete 1/1 · 2 obs · 704 ch | unchanged |
| `lab notes.md` | `text.structured` | the words **and the headings** | complete 1/1 · 1 obs · 473 ch | complete 1/1 · **6 obs** · 541 ch |
| `registration.html` | `text.structured` | the page a person sees | complete 1/1 · 5 obs · 646 ch **of page source** | complete 1/1 · **8 obs** · 325 ch **of the page** |
| `recommendation.rtf` | `text.structured` | the letter | complete 1/1 · 3 obs · 3,257 ch **of control words** | complete 1/1 · 3 obs · **302 ch of the letter** |
| `recommendation.docx` | `docx.structure` | headings, paragraphs, tables | complete 11/11 · 2 obs · 293 ch | unchanged |
| `measurements.pdf` | `pdf.text` | text by page, headings, metadata, dates | complete 2/2 · 3 obs · 8,424 ch | unchanged |
| `scanned receipt.pdf` | `pdf.text` + `ocr.apple_vision` | OCR of the scan | complete · 3 obs · **1,521 ch of OCR** | unchanged |
| `whiteboard.png` | `image.metadata` + `ocr.apple_vision` | dimensions, format, **the words in the picture** | complete · 3 obs · **1,521 ch of OCR** | unchanged |
| `receipt photo.jpg` | `image.metadata` + `ocr.apple_vision` | the same, plus EXIF | complete · 3 obs · 1,521 ch · **no EXIF** | unchanged |
| `settings.json` | `text.structured` | text, language, structure markers | complete 1/1 · 2 obs · 79 ch | complete 1/1 · **3 obs** · 79 ch |
| `grades.csv` | `text.structured` | the cells | **`unsupported` 0/1 · 0 obs · 0 ch** | complete 1/1 · **18 obs** · 142 ch |
| `readings.tsv` | `text.structured` | the cells | **`unsupported` 0/1 · 0 obs · 0 ch** | complete 1/1 · **11 obs** · 60 ch |
| `budget.xlsx` | `text.structured` | sheet names, headers, cells, dates | **`unsupported` 0/1 · 0 obs · 0 ch** | complete 2/2 · **15 obs** · 150 ch |
| `thesis defence.pptx` | `text.structured` | titles, text boxes, notes, links | **`unsupported` 0/1 · 0 obs · 0 ch** | complete 3/3 · **4 obs** · 292 ch |
| `midterm results.eml` | `text.structured` | sender, recipients, subject, date, thread, body, attachments | **`unsupported` 0/1 · 0 obs · 0 ch** | complete 1/1 · **6 obs** · 163 ch |
| `advising.ics` | `text.structured` | title, times, location, organizer, attendees, recurrence | **`unsupported` 0/1 · 0 obs · 0 ch** | complete 1/1 · **7 obs** · 51 ch |
| `adviser.vcf` | `text.structured` | names, orgs, emails, phones, addresses | **`unsupported` 0/1 · 0 obs · 0 ch** | complete 1/1 · **7 obs** · 0 ch |

`unsupported` is §2.4's phrase for *"no reader exists and the bytes were never looked at"*.
Seven of seventeen files carried it, and nothing on any screen said so.

### 2.1 Two rows where the BEFORE column is worse than empty

`recommendation.rtf` stored 3,257 characters beginning `{\rtf1\ansi\ansicpg1252\cocoartf2822`
and `registration.html` stored its `<style>` block and the body of a `<script>` element.
Both runs were recorded `complete`. That is not missing information, it is **false**
information about a file the product claims to have read, and the recogniser — which reads
observations — read it as prose the author had written. `.epub` and `.odt` are ZIP
containers and were decoded as UTF-8 the same way, producing mojibake stored as `complete`;
both are read properly now.

### 2.2 Formats not in the corpus, now read

`.odt` and `.epub` complete §2.9's eight text formats. `.mbox` joins `.eml`. `.mp4`,
`.m4a`, `.mov` and `.wav` yield container metadata — duration, timescale, codec, creation
time — which is exactly where **B6 (2026-08-20)** stops audio and video for v1, with
NEEDS JOSEPH 7 the same day putting speech-to-text out of scope.

---

## 3. The boundary — what still yields nothing, and what it costs

Read this as the honest edge of the product, not as a to-do list. Each row says what a
person loses.

| format | what happens | measured? | what it costs |
|---|---|---|---|
| `.ods` | routes to `spreadsheet`, reader returns `None`, **`unsupported` 0/1** | measured, real ODF | every cell of a LibreOffice/OpenOffice spreadsheet. **Cheapest gap in this table to close: ZIP + XML, the same machinery `.odt` already uses, no dependency.** |
| `.odp` | routes to `presentation`, **`unsupported` 0/1** | measured, real ODF | every slide of an ODF deck. Same machinery. |
| `.doc` | **no `source_type`, no extractor at all** | measured, genuine Word 97 binary from `textutil` | *Every legacy Word document a person owns.* `doc` is not a key in `router.SOURCE_TYPE_BY_FORMAT` — the table has `docx` and stops. This is a routing-table gap, not a reader gap, and it is the one row here that surprised me. |
| `.xls`, `.ppt`, `.msg` | routed, reader returns `None`, `unsupported` | **reasoned** — no tool on this machine writes one | legacy spreadsheets, decks and Outlook mail. All three are OLE compound files; `olefile` plus format work, or `extract-msg` for `.msg` alone. |
| `.numbers`, `.pages`, `.key` | `.numbers` routes to `spreadsheet` and is `unsupported`; `.pages` and `.key` are not routing-table keys at all | **reasoned** | Apple iWork documents. On a Mac corpus this is not a long tail. |
| `.mp3` | routes to `audio_video`, `unsupported` | **reasoned** | duration and tags only — low value for a product that files documents. `mutagen` closes it. |
| PDF tables | the PDF is read; a table arrives as **lines of text in reading order** | measured | pdfminer gives text with per-character position and no table model. `pdfplumber` builds on the dependency already declared. |
| images: EXIF | dimensions and format only; §2.6's tier-1 band is unavailable | measured | **RULED: not to be built** — `94` F21, `40c6816`. §2.7's OCR trigger runs OCR only when a file yields no usable text *and no usable metadata*, so an EXIF reader would **stop OCR running on exactly the photographs whose words matter** — the photographed whiteboard, the picture of a receipt. And `image_exif` and `gps` are both in `ALWAYS_LOCAL`, so EXIF can never inform a model by construction, while facts derived from OCR text are releasable normally. The trigger changes first, or the words disappear and nobody sees it happen. |
| HTML link targets | an `<a href>` whose URL is not in the visible text is lost | measured | §2.9 asks a text document for "links". `extractors.structured_text.TextDocument` has slots for text, language, headings and markers and none for links — a P5 shape change, not a reader change. |
| an extensionless `.csv` | reads as `txt`: prose, not addressed cells (8 observations where a named `.csv` gives 18) | measured | a delimiter-consistency test would catch it and is exactly the kind of guess that misfires on prose containing commas, so it is not made |
| non-UTF-8 text with no declared encoding | replacement characters | measured | guessing cp1252 puts a plausible **wrong** letter inside a word, unmarked. Where a format declares its encoding — HTML's `<meta charset>`, RTF's `\ansicpg` — the declaration is read and honoured. `chardet` would close the undeclared case. |

---

## 4. Against the owner's own disk

25,770 files across Desktop, Downloads and Documents. The headline "13% routed" counts
9,000+ source files from code projects and is misleading: **this product files documents.**
The document picture is ~2,684 routed (`.pdf` 1122, `.txt` 560, `.md` 512, `.docx` 490)
plus `.png` 767, `.csv` 496, `.jpg` 209, `.html` 223, and **1,057 files with no extension
at all**.

A corpus in those proportions, 63 files, through the shipped path:

```
format    outcome                          files   obs     chars
(none)    pdf / image+ocr / docx / text       11    35    40,127
pdf       pdf.text complete                   11    33    92,664
png       image.metadata + ocr complete        8    24    12,168
jpg       image.metadata + ocr complete        2     6     3,042
txt       text.structured complete             6    12     4,224
md        text.structured complete             5    30     2,705
csv       text.structured complete             5    90       710
docx      docx.structure complete              5    10     1,465
html      text.structured complete             2    16       650
wav       text.structured complete             8    32         0

288 observations, 157,755 characters. Zero unsupported. Zero unrouted.
```

Every line held a `0 obs / 0 chars` entry for at least one of its formats on 2026-09-02.

### 4.1 What a real run will cost

Apple Vision, timed three times at 200 DPI on full-page images: **1.87s, 1.33s, 1.34s**.
The 63-file corpus took 19.8s end to end and thirteen OCR passes account for essentially
all of it. On the owner's disk that is **976 images × ~1.5s ≈ 24 minutes of OCR alone**,
plus 1,122 PDFs through pdfminer, whose own module docstring names speed on large documents
as its known cost.

§8.6's four OCR ceilings exist for this and P1 holds their values — but **nothing in this
build records which ceiling fired**. `database_agent.budget` publishes seventeen keys and
stores no record of one being hit, so `review_run.progress`'s `cause_for` answers `None`
for every state and a stopped run shows the person a deferred count beside the sentence
*"no ceiling is recorded as the cause"*. At 24 minutes of OCR that stops being hypothetical.

---

## 5. Findings that are not per-format

### 5.1 `python-docx` is an undeclared runtime dependency

`src/readers/docx_python_docx.py:33` does `import docx` at module scope. `pyproject.toml`'s
`readers` extra lists `pdfminer.six` and the two pyobjc packages and **not** `python-docx`.
It works on this machine because the package happens to be installed. On a machine where it
is not, importing `readers.deployment` raises and the whole command dies — not a `.docx`
recorded `unsupported`, which is the graceful outcome the module's own docstring describes.

### 5.2 OCR works, and it is Apple Vision

A `grep` for `pytesseract` finds nothing and the conclusion "no OCR anywhere" does not
follow. `readers/deployment.py:102` wires `vision_ocr()`, the engine §2.7 names by name.
Measured: ten of ten images in the proportioned corpus produced an `ocr.apple_vision
complete` run, and so did three extensionless files that are really PNGs. `extractors/ocr.py`
and `readers/ocr_vision.py` are live code.

### 5.3 `_detect_format` was never the reason a `.csv` extracted nothing

`route()` reads `operative = detected if detected is not None else declared`, so a `.csv`
whose detector declined still routed on its declared extension and still reached
`text.structured`. The zero-extraction cause was `deployment.py`'s `read_long_tail =
_no_reader`. The five-entry table cost nothing for a file that *has* an extension and
everything for the 1,057 that do not — see `7b25e27`.

### 5.4 CLOSED 2026-09-03 (`acb75cd`, CR-07). A whole document WAS releasable as one excerpt

**Closed.** `resolve.materialise` now reports the unit length at the observation's own container
path when the value covers it, and `is_whole_document` refuses it. §2.3's cell and §2.8's field are
untouched. `92` CR-07 carries the verification and the four things it does not cover — the first of
which, an observation standing where no unit stands, **§5.5's PDF body work inherits as a hard
requirement.**

The original finding follows, unedited, because a closed defect read without its cause teaches
nothing.

### 5.4 (as found) A whole document is releasable to a model as one excerpt

**Open, and the reason `5.5` is not built.** `extractors/structured_text.py` emits the whole
document as one span-less `body` observation. That is deliberate and its folder-naming half
holds — `cli.reads_a_structured_string` requires a span, so the document cannot become a
folder name. But `privacy/resolve.py:197` resolves a span-less observation to its
`raw_value`, which *is* the whole document, with `unit_length=None`; and
`privacy/items.py:is_whole_document` returns `False` when `unit_length is None`. So §8.4's
*"should not send full documents where a short heading or OCR excerpt is enough"* never
fires on it. Reproduced on the live path: a 339-character `.txt` through `run_wave2`, then
`Excerpt(observation_key=<the prose key>, span=None)` → `materialise` returns 339 chars,
`check_item` **passes**. `complete_extracted_text` is member 2 of `ALWAYS_LOCAL`.

`span=None` is legitimate elsewhere — §2.3's cell and §2.8's EXIF field have no unit to take
a substring of — so a blanket refusal breaks those. The shape of a fix is *"refuse a
span-less excerpt whose `raw_value` is the whole of a text unit at its own container path"*,
and that is a `src/privacy/` decision.

### 5.5 A PDF's body text is invisible to the recogniser

`recognition/detector.py` reads observations only, on purpose. Exactly one extractor emits
document prose as an observation — `structured_text.py`, for `text_document` only.
`pdf.py`, `docx.py` and `ocr.py` put their text in `text_units` and emit observations only
for metadata, headings and structured strings:

```
PHYS 1401 syllabus.txt    704 chars ->  2 observations, prose INCLUDED
measurements.pdf        8,424 chars ->  3 observations, prose EXCLUDED
recommendation.docx       293 chars ->  2 observations, prose EXCLUDED
scanned receipt.pdf     1,521 OCR   ->  1 observation,  prose EXCLUDED
```

The same syllabus is read by the recogniser as a `.txt` and not read as a `.pdf`. On the
owner's disk that is 1,122 PDFs — the largest document format there. The fix mirrors
`structured_text.py`: one span-less `body` observation per page or per document.
**Not built**, because extending that pattern to every PDF page multiplies the exposure in
§5.4 before it is closed, and because it changes which folders get named on every corpus in
a tree many agents are testing against. Close §5.4 first.

---

## 6. Re-running this

Scratchpad `.../scratchpad/extraction/`:

```
make_corpus.py     builds the 17 real files
measure.py         drives the shipped router and readers -> JSON + table
before.json        2026-09-02 state
after.json         after 8dca892 / 4a9682e
census.json        the 63-file proportioned corpus
boundary.json      the still-unsupported formats in §3
CLI-PATCH.txt      two hunks for src/cli.py, with patch.py + check-anchors.py
FINDINGS.txt       the long form of this document
```

`python3 measure.py <corpus dir> <out.json>` reproduces any row above.

---

## 7. What changed, and how it was proved

| commit | what |
|---|---|
| `8dca892` | `readers/long_tail_stdlib.py` and `readers/text_documents.py`, and the two lines in `deployment.py` that wire them. 63 tests. |
| `4a9682e` | five tests on the live Wave-2 path, including the contacts privacy chain end to end. |
| `7b25e27` | `readers/signatures.py` — §2.9's file-signature clause. 54 tests. |

All three are **standard library only**. `pyproject.toml`'s `dependencies = []` stays empty
and the `readers` extra does not grow.

**Mutation testing, stated precisely.** 57 mutations across the three modules; 51 caught on
the first pass. All six survivors were real test weaknesses, and every one is now covered:
an attachment filter that only ever met an `application/pdf` part; an RTF fixture declaring
the code page the reader falls back to; an HTML line-break rule only ever fired from an end
tag, so `<br>` was untested; a "binary" fixture that also failed UTF-8 decoding, so the
control-character test was never what caught it; a configuration file whose keys were not
the header names the mail test looks for; and a JSON fixture short enough that parsing the
window and parsing the file agreed. **57 of 57** after.

**Privacy, proven rather than asserted.** Reading `.vcf` is new, so the chain was tested end
to end on bytes a real contact card wrote: `extract_long_tail` marks every contacts value
and every address header `potentially sensitive`, `orchestrator` records the signal against
P4's own observation key, and `privacy.items.check_item` raises `AlwaysLocalRequested` when
anything asks to release one. No new `ALWAYS_LOCAL` kind is created — the new observations
sit in zones the product already released from, and no reader added here returns OCR output,
EXIF, a GPS tag, a path or a file hash.

Full suite at the time of writing: **7,398 passed, 19 skipped, 23 xfailed, 0 failed**,
7,440 collected.
