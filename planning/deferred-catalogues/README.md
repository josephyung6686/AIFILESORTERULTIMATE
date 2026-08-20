# Deferred evidence catalogues

Hand-authored content that P3, P5 and P6 need and **must not invent**. Each catalogue fills one row
of a *Deferred — manual design required* table in a part SPEC. Nothing here is a plan, a schema, or
an implementation; each file is data plus the reasoning and sourcing behind it.

Authored 2026-08-20. Nothing is committed by the authoring agent — Joseph reviews and commits.

---

## The seven catalogues

| # | File | Owner | Consumed by | Rows |
|---|---|---|---|---|
| 01 | `01-tool-producer-strings` | **P6** | the §2.2/§2.3 discount rule, tier 1 — **suppression** | 115 entries · 6 refused · 6 uncertain |
| 02 | `02-screen-resolutions` | P5 (injected) | `dimension_signal` → `"exact display resolution"`, tier 3 | 70 entries · 4 uncertain |
| 03 | `03-sensor-aspect-ratios` | P5 (injected) | `dimension_signal` → `"sensor-shaped dimensions"`, tier 2 | 5 ratios · 12 cited anchors · 3 refused · 5 uncertain |
| 04 | `04-camera-filename-patterns` | P5 (injected) | `filename_pattern` → one `possible`, tier-less observation | 37 entries · 5 refused · 8 uncertain |
| 05 | `05-repository-markers` | **P3 and P5** | two arrays, two jobs — see below | 4 + 118 entries · 4 refused · 6 uncertain |
| 06 | `06-citation-identifier-patterns` | P5 (injected) | `find_structured_strings` for E1, E2, E3 | 22 entries · 7 refused · 7 uncertain |
| 07 | `07-archive-recognizable-markers` | P5 (injected) | E4's `recognize_markers` | 80 entries · 4 refused · 6 uncertain |

Every catalogue is a pair: `NN-name.json` is the source of truth, `NN-name.md` is generated from it.

---

## How P5 and P6 must consume these — never as module-level constants

**The rule.** P5 PLAN's *Global Constraints* forbid any module-level gazetteer, regex, screen
resolution, producer string, aspect ratio or language tag inside `src/extractors/`, and **Task 20
enforces it by runtime introspection of every module's namespace** — not by searching source text,
because a source-text guard matches comments and docstrings and has broken three tasks on this
project already. Exactly one module-level regex is permitted in the whole package:
`shape._LINE_BREAK_HYPHEN`, P4 D8's soft-hyphen repair.

So none of these files may be `import`ed by anything under `src/extractors/`. They are **data the
caller loads and injects**, and the injection points already exist in P5's signatures as *required
keywords with no default* — a default would be a place for an invented value to hide.

### The injection points

| Catalogue | Injected as | Into |
|---|---|---|
| 02 + 03 | `dimension_signal(width, height) -> str \| None` | `extract_image` (E5) |
| 04 | `filename_pattern(filename) -> str \| None` | `extract_image` (E5) |
| 06 | `find_structured_strings(text) -> tuple[StructuredString, ...]` | `extract_pdf` (E1), `extract_docx` (E2), `extract_structured_text` (E3), long-tail |
| 05 (`p5_evidence_markers`) | the `markers` field of what `read_text_document(path) -> TextDocument` returns | E3 |
| 07 | `recognize_markers(member_paths) -> tuple[ArchiveMarker, ...]` | `extract_archive` (E4) |
| 05 (`p3_exclusion_roots`) | scan configuration, beside §1.1's eleven literal directory names | P3 |
| 01 | fact-resolver construction, or the P1-namespaced configuration object (G4) | **P6 only** — never P5 |

Sketch, for the image extractor:

```python
# In the CALLER. Not in src/extractors/ — Task 20 fails if any of this lands there.
resolutions = load("planning/deferred-catalogues/02-screen-resolutions.json")
ratios      = load("planning/deferred-catalogues/03-sensor-aspect-ratios.json")
patterns    = load("planning/deferred-catalogues/04-camera-filename-patterns.json")

result = extract_image(
    file_row,
    read_image=reader,
    dimension_signal=make_dimension_signal(resolutions, ratios),  # required kwarg, no default
    filename_pattern=make_filename_pattern(patterns),             # required kwarg, no default
)
```

### Three constraints the injected functions must respect

1. **`dimension_signal` returns at most one name.** `DIMENSION_SIGNALS` is exactly
   `("sensor-shaped dimensions", "exact display resolution")` and a third name raises
   `UnknownSignal`. Catalogue 02 is consulted first, then 03, else `None` — the reasoning is written
   out in both files under *Arbitration*.
2. **E4's `recognize_markers` returns only two kinds.** `MARKER_KINDS` is exactly
   `("source-code manifest", "document name")`; a third raises `UnknownMarkerKind`.
3. **E3's structural markers use four kinds.** `("repository marker", "package manifest",
   "notebook metadata", "README file")`; a fifth raises `UnknownMarkerKind`.

---

## Catalogue 01 is different: P5 never sees it

P5 emits producer, creator and author values **verbatim** at `zone = metadata` with
`reliability: direct` — `direct` describes the *slot*, not the value's usefulness — and sets **no
flag of any kind** (M4). Catalogue 01 is P6's, and it drives one rule with two tiers:

- **Suppression** — a match produces **no fact in any field** and one `unresolved` row with
  `reason = discounted_tool_metadata`. Not demoted to `possible`: a tool name is not a weak clue
  about the document, it is a fact about the software.
- **Demotion** — any *other* producer/creator/author value may populate `authored_by` and nothing
  else. Never topic, purpose, project, course, institution or target.

That containment is why the list can afford to be broad: a false positive costs one `authored_by`,
a field §3.8 already makes `destination_eligible = FALSE`.

## Catalogue 05 is different: two arrays, two jobs

- `p3_exclusion_roots` — P3 skips **descendants** of a directory holding one of these. Destructive:
  a wrong entry makes real user files invisible to the whole product, with no observation, no fact
  and no review surface.
- `p5_evidence_markers` — an admitted file *looks like part of a project*. One weak observation P6
  can outweigh.

`package.json` is in both, with its two roles documented on both rows. `CMakeLists.txt` is in
`p5_evidence_markers` only — putting it in the exclusion side would hide hand-written C++ trees,
which is the opposite of §1.1's stated purpose.

---

## Working on these files

```bash
cd planning/deferred-catalogues
python3 render.py          # regenerate every .md from its .json
python3 render.py --check   # no-drift guard; non-zero if any .md is stale
./checks/run_all.sh         # every catalogue check plus the drift guard
```

**Edit the JSON, never the markdown.** The tables are generated; a hand-edit is overwritten on the
next render and `--check` will flag it. Catalogues 02, 05 and 07 are themselves generated from
builder scripts in `checks/` — edit the builder, not the JSON. Catalogue 07's source-code-manifest
array is derived from catalogue 05, so the two cannot disagree about what a project marker is.

### What the checks actually assert

Not that the files parse — that every entry behaves. For each catalogue: every `example_true`
matches its own row, and every `example_false` matches **no row anywhere in the file**. On top of
that, the acceptance cases: `python-docx` suppresses while `Jane Chen` does not match anything;
`IMG_4821` reads as a camera convention while `MATH2010` matches nothing; `1920x1080` is flagged as
overlapping 16:9; `4032x3024` is a catalogue-03 anchor and never a catalogue-02 row;
`p3_exclusion_roots` is exactly §1.1's four; no §3.10 date, no entity, and no privacy pattern leaks
into catalogue 06; `submission.zip` yields five document-name markers. Catalogue 06's ISBN, ISSN and
MOD 11-2 checksum validators are implemented in the checker and self-verified against known-good and
known-bad values, so the "checksum required" claims are exercised rather than asserted.

Four checks found real defects during authoring, all now fixed and recorded: naive `prefix` matching
made `Microsoft Word` match `Microsoft Word skills certificate` (68 rows); catalogue 06's author-year
citation pattern required a name *after* `et al.`; catalogue 07's `__init__.py` row referenced an id
catalogue 05 never generated; and catalogue 06's PMID row capped at 8 digits, which silently missed
every PubMed ID issued since NLM moved to 9-digit UIs in 2002.

## Sourcing — read the `verification` tag before trusting a citation

Every source carries a `verification` value, and it is not decoration:

| tag | means |
|---|---|
| `read` | the page was opened and read; quoted text is verbatim |
| `read (teammate)` | opened and read by the catalogues-finish agent, who supplied verbatim quotes |
| `SEARCH SUMMARY — not opened` | the fact came from a web-search result summary; the page was **not** retrieved |
| `UNREACHABLE` | the URL failed when tried; the citation must be replaced before it is relied on |

Of 44 citations, **8 were actually opened** — five by the authoring agent, three by the
catalogues-finish agent. The rest are search summaries, and they say `consulted` rather than
`retrieved`, because recording a retrieval date for a page nobody opened is precisely the unearned
confidence these catalogues exist to keep out of the product. A search summary is not worthless — it
is how most of the vendor-prefix and manifest-name knowledge here was gathered — but it must not be
quoted as if read, and any row that would be harmful if wrong should be upgraded before launch.

Two citations are `UNREACHABLE` and both are in catalogue 06: ORCID's support pages return HTTP 403
and ISBN International's return HTTP 404. Neither row depends on the citation, because
`checks/check06.py` implements and exercises the ORCID MOD 11-2 and ISBN check-digit algorithms
directly — running code is stronger evidence than a link.

---

## Entry shape

Every row carries `id`, `match` or `pattern`, `match_kind` (`exact` | `prefix` | `regex`),
`case_sensitive`, `rationale`, `design_cite` (section plus a quote), `false_positive_risk`,
`example_true`, and `example_false` — a string that must **not** match. Rows add fields where the
domain needs them: `checksum`, `kind`, `applies_to`, `capture`, `pattern_label`, `tolerance`,
`aspect_ratio`, `overlaps_sensor_ratio`, `tail_required`, `status`.

Three arrays appear beyond `entries`:

- **`refused`** — things deliberately *not* matched, with the false-positive analysis that decided
  it. These are as load-bearing as the entries: `ref-dcf-generic` in catalogue 04 is what keeps
  course codes from being read as camera filenames.
- **`uncertain`** — things needing Joseph. Recall-safe: when in doubt, a row goes here rather than
  into `entries`.
- **`cross_match_expected`** — on a `refused` or `uncertain` row, states an *intended* interaction
  with a live entry so the checker reports it as expected rather than as a failure. Three exist, and
  each documents a real design point.

---

## What these files deliberately do not contain

Adjacent deferred rows owned elsewhere, listed so nothing seeds them by accident:

- **Date and academic-term patterns** (§3.10) — P6's, deferred separately. Catalogue 06 refuses them
  explicitly and a check asserts `Spring 2025`, `AY 2024-25`, `Michaelmas Term 2024`, `2024-05-11`
  and `2025` match nothing.
- **Gazetteers** (§3.7) — universities, course-code formats, institutions, companies, labs, venues.
  P6's. `BUSIB 4300` matches nothing in any catalogue here.
- **The 200–300 template library** (§5.7) and the residual library beyond §7.3's nine names — P10's.
  Catalogue 07 stops its document-name vocabulary at §2.5's literal five for this reason.
- **Fact-schema fields**, **minimum score and margin values**, **positional weights per zone**,
  **signal-tier weights**, **OCR language configuration**, **budget ceilings** — each is its own
  deferred row with its own owner.
- **Personal-data patterns** — government IDs, payment cards, phone numbers. §8.4 privacy surface,
  P7's, and refused on principle in catalogue 06: a finder that located them would write them into
  `raw_value` and into context windows, manufacturing the exposure the privacy gate then has to
  contain.

---

## NEEDS JOSEPH

Written here, on disk, deliberately: three agent final reports have already been lost on this
project, and a decision list that exists only in a chat message is a decision list that dies.

**42 uncertain items across the seven catalogues**, each with its argument on both sides in the
`uncertain[]` array of its own JSON file. None blocks the build — every catalogue runs and every
check passes with all of them unresolved. Each one left unresolved is a class of evidence the
product cannot see, or a judgement call made by default rather than on purpose.

The one worth deciding first is **`unc-pyproject-as-exclusion`** (catalogue 05): whether
`pyproject.toml` joins §1.1's four `p3_exclusion_roots`. It is the strongest candidate and the
consequences are asymmetric — adding it makes P3 skip every descendant of any Python project
directory, permanently and invisibly. `.git` was considered and **refused**: it would be
catastrophic, and the reasoning is recorded rather than assumed.

### Every open item, by catalogue

**01 — tool producer strings** (6 open, 6 refused)

- **`unc-google-docs-renderer`** — Widely reported as the generator string on Google Docs exports, but no vendor or standards source confirming it was found on 2026-08-20. The Google Docs **PDF** export path is already covered with a cited source via `tps-skia-pdf` (`Skia/PDF m…`), so omitti…
- **`unc-qt-producer`** — wkhtmltopdf's Qt backend reportedly writes `Qt 4.8.7` into Producer. Only blog-tier sourcing found. A whole-value regex `^Qt \d+\.\d+(\.\d+)?$` would be safe, but the string also appears from other Qt applications, and `tps-wkhtmltopdf` already catches the …
- **`unc-microsoft-bare`** — Should a bare `Microsoft` / `Microsoft Corporation` in an Author slot be suppressed, or demoted to `authored_by = Microsoft`? Suppression loses a true organizational authorship fact; demotion admits a value that is usually a template artefact. Currently ref…
- **`unc-user-admin-placeholders`** — OS account defaults that land in `lastModifiedBy` and `Author`. They are not tool *names*, so they sit outside §2.2's literal wording, but they are exactly as uninformative and §2.3's "a prior editor" reasoning covers them. Suppressing them is defensible; i…
- **`unc-scanner-mfp`** — Office multifunction scanners write model-specific Producer strings. Each is individually safe but the set is open-ended and vendor-specific; matching them well needs a real corpus. High value if Joseph's corpus contains scanned paperwork, because these fil…
- **`unc-camera-firmware`** — Non-dotted firmware forms (`Ver.1.10`, `1.0.0 (Android)`, `V2.30`) that `tps-bare-version` does not catch. Enumerating them per model is exactly the "thousands of obscure phone models" the brief rules out; a shape-based regex is possible but needs FP analys…

**02 — screen resolutions** (4 open, 0 refused)

- **`unc-retina-logical-sizes`** — A macOS screenshot taken with a scaled resolution setting can land on the logical size rather than the native one. Several such sizes (1440×900, 1680×1050, 1280×800) are already in the list as standalone monitor standards, so the common cases are covered by…
- **`unc-browser-viewport`** — A full-page browser screenshot is viewport-width by page-height — an unbounded set. Not enumerable, and any attempt would be a heuristic. Recorded so the gap is visible rather than discovered later.
- **`unc-android-long-tail`** — The Android panel set is open-ended. v1 covers the dominant 18:9/19:9/19.5:9/20:9 FHD+ and QHD+ families. Adding more should be driven by what Joseph's corpus actually contains, not by a device database.
- **`unc-1920x1080-collision`** — The single most overloaded pair in this file: it is FHD portrait, the iPhone 6-8 Plus native panel, **and** exactly 16:9 — which is also a video-still and 16:9-camera-mode shape. It is one row with `false_positive_risk: high`. If Joseph's corpus contains ma…

**03 — sensor aspect ratios** (5 open, 3 refused)

- **`unc-panorama`** — An iPhone or Android panorama is an arbitrary stitched width — anywhere from roughly 2:1 to 12:1 — so no ratio describes the class and no honest entry can be written. A width-to-height threshold (say, longer/shorter > 2.5) would be a heuristic, and §2.6's d…
- **`unc-pixel-4080x3072`** — The Pixel-class 12.5 MP binned output. Its ratio is 1.3281, which is 0.39 % off nominal 4:3 — inside the 0.5 % tolerance, and the concrete case that motivates the tolerance existing at all. Community-reported rather than vendor-documented, so it is recorded…
- **`unc-tolerance-value`** — 0.005 is chosen to clear the widest real sensor deviation found (0.39 %) with margin, while staying far inside the 6.7 % gap between 4:3 and 5:4. It has not been measured against a real corpus. It is a number, so it must not live inside `src/extractors/` ei…
- **`unc-crop-shapes`** — `4:5` is the Instagram portrait crop and `9:16` the story crop. Both are the unordered form of 5:4 and 16:9 respectively, so they already match — which is arguably wrong, since a social-media crop is not a sensor readout. Whether to distinguish them needs t…
- **`unc-near-miss-fallthrough`** — A consequence of the arbitration order that is worth naming because it is not obvious. `1919x1080` — a screenshot cropped by one pixel — misses catalogue 02 exactly (as §2.6's word "exact" requires) and then lands inside the 0.5 % band around 16:9, so it is…

**04 — camera filename patterns** (8 open, 5 refused)

- **`unc-return-value`** — **A contract question for the P5 owner, not a data question — and raised independently by both versions of this file, which is the strongest signal available that it genuinely needs answering.** P5 PLAN Task 15 does `emit(zone="filename", raw=matched, label…
- **`unc-dcf-generic-in-dcim`** — The safe form of the refused generic pattern: apply it only when an ancestor directory is `DCIM` or matches `^\d{3}[A-Z0-9]{5}$` (`100APPLE`, `101MSDCF`), both defined by the DCF standard. A course code will not sit under `DCIM`. Not adopted in v1 because `…
- **`unc-duplicate-burst-suffixes`** — Copies and burst frames append suffixes that break the anchored patterns: `IMG_4821 (1).png`, `IMG_4821-2.jpg`, `IMG_20240115_103045_BURST001_COVER.jpg`. The Android rows already absorb a `_N` tail and the Pixel row absorbs a mode suffix, but the general ca…
- **`unc-localized-screenshots`** — macOS and Android localize the screenshot filename prefix. v1 covers English only. Worth adding if Joseph's corpus is not English-locale — a single question that would settle it. Guessing the exact localized date formats without a real file to check would b…
- **`unc-olympus-month-coded`** — Olympus encodes the month as a single character (1-9 then A, B, C for October to December) and the day as two digits. The shape collides with the plain `P#######` Panasonic row for months 1-9, so `fnp-panasonic-p` already catches most of them; only October-…
- **`unc-telegram-instagram`** — Telegram (`photo_1234@15-01-2024_10-30-45`) and Instagram saved-post naming would extend the messaging class, which is the class that explains stripped EXIF under §2.6's trap 1. Both are community-reported with format variation across versions and platforms…
- **`unc-scanner-naming`** — Flatbed and multifunction scanners write their own conventions (`Scan_20240115`, `Scanned Document`, `Image (3)`). A scanner class would pair with catalogue 01's `unc-scanner-mfp` row. Left out of v1 because the naming is per-vendor and per-driver, and `Ima…
- **`unc-canon-prefixes`** — Canon has used at least four naming schemes across its EOS, PowerShot and legacy lines. Three are live entries here; the other version of this list left the whole family in `uncertain` (its `unc-canon-prefixes`), which is a defensible alternative reading. T…

**05 — repository markers** (6 open, 4 refused)

- **`unc-pyproject-as-exclusion`** — The strongest candidate for extending §1.1's four, and still not added. §1.1's list is explicitly open ("files such as"), it names `requirements.txt`, and `pyproject.toml` has since replaced it as the Python project root marker — so the *intent* of §1.1 arg…
- **`unc-lockfiles-as-exclusion`** — A lock file is a *stronger* dependency-tree signal than a manifest: it is machine-generated and never hand-authored, so a directory holding one is far more likely to be a real dependency tree than a personal folder. That makes lock files the safest possible…
- **`unc-other-ecosystems-as-exclusion`** — The obvious per-ecosystem extension of §1.1's four. All are in `p5_evidence_markers` already, which is where the task says extra language ecosystems go first. Adding any of them to the exclusion side hides whole trees, and none of them is a case where Josep…
- **`unc-p3-oq9`** — P3 SPEC Open Question 9: "Does the project-root rule exclude the root directory itself, or only its descendants? §1.1 says 'descendants of software project roots.' Whether the marker-bearing directory can still be a candidate root is unsettled." This catalo…
- **`unc-xcode-bundles`** — These are directory bundles, and P3's ratified protected-container rule already refuses to descend into macOS packages — "P3 does not descend into one, does not stat its contents, does not hash a byte of it". Adding them here would duplicate a stronger rule…
- **`unc-notebook-key-collision`** — These five keys are matched against **top-level JSON object keys**, not filenames — a different match target from every other row in this file, which is why each carries `applies_to: notebook_json_key`. An arbitrary JSON document could contain a top-level `…

**06 — citation & identifier patterns** (7 open, 7 refused)

- **`unc-full-references`** — §2.2 names "citations" and this file matches only the in-text markers. A full reference — authors, title, venue, volume, pages — is not a regular language, and the four major styles disagree on ordering, punctuation and abbreviation. A regex attempt would p…
- **`unc-citation-zone-mapping`** — A consequence of P4's `ZONE_BY_STRUCTURED_KIND` worth surfacing before P6 sets its positional weights. §2.2's motivating sentence contrasts a course code in a page-one heading with the same string "in a reference list on page eighteen" — but an in-text cita…
- **`unc-doi-trailing-punctuation`** — Both the DOI and URL rows need a trailing-punctuation trim, because `.` and `)` are legal inside a DOI suffix and a URL path but usually belong to the sentence. The trim rule proposed here — remove a single trailing `.`, `,`, `;` or unmatched `)` and shorte…
- **`unc-doi-case`** — DOI names are case-insensitive for *resolution* but must be stored as written. P4 RAW-1 already forces that — `raw_value` is the source substring — so the only question is whether `normalized_value` should carry a lowercased form. P4 D8 permits mechanical n…
- **`unc-isbn13-bare-risk`** — The only unlabelled row in the file. Roughly one in ten random 13-digit strings starting `978` passes a mod-10 check by chance, so a document full of long numeric codes could produce spurious ISBNs. Kept in v1 because copyright pages and reference lists gen…
- **`unc-in-text-numeric-noise`** — `[12]` is an IEEE citation in a paper and an array index in a code listing, a footnote marker in a contract, and a placeholder in a template. Marked `false_positive_risk: high` for that reason. The mitigation is not a better regex — it is P6's positional we…
- **`unc-non-latin`** — The author-year citation row requires `[A-Z]` for the surname's first letter, so it will not fire on CJK, Cyrillic or Arabic author names. §2.7 requires "appropriate language support including CJK where required", and P4 RAW-1 is verified on a CJK fixture —…

**07 — archive markers** (6 open, 4 refused)

- **`unc-form-word`** — §2.5 names `form` literally, so it is in — but it is the weakest string in either array. Whole-word matching keeps it out of `format`, `formula`, `information` and `transformation`, and the check asserts that. It will still fire on `Feedback Form.pdf`, `For…
- **`unc-cv-token`** — Two characters, matched as a whole word. Safe against `cvs`, `cvx` and `opencv` because of the word boundaries, but a member literally named `cv.csv` in a data folder would match. Kept because `CV.pdf` is overwhelmingly the more common real case in the corp…
- **`unc-nested-archive-members`** — An archive containing `project.zip` cannot have its inner members inspected without opening it, and §2.5 marks nested archives as a case to leave `unreadable` or `partial` rather than force open. So a nested archive's markers are simply not available, and t…
- **`unc-path-depth`** — `package.json` at `project/package.json` is a project root marker. The same name at `project/node_modules/left-pad/package.json` is a dependency's manifest and means almost nothing — and a real Node archive contains thousands of them. P4 D10 already collaps…
- **`unc-python-package-layout`** — §2.5 names "Python package layout" alongside three concrete files, and a layout is a *relationship* between paths — a directory containing `__init__.py` plus sibling modules — not a single member. This file approximates it with the `__init__.py` row, which …
- **`unc-localized-document-names`** — `Lebenslauf`, `curriculum`, `expediente`, `relevé de notes` — the same five documents in other languages. Same position as catalogue 04's localized screenshot row: easy to add, impossible to choose correctly without knowing which languages the corpus contai…

