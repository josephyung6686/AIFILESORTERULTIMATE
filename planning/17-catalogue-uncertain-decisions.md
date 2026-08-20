# Catalogue uncertain items — recommended calls, NOT decisions

Date: 2026-08-20
Status: **RECOMMENDATIONS ONLY. Joseph has not answered these.** Nothing here has been applied to the
catalogues, and the `uncertain[]` arrays still hold all 43 rows.

> **Provenance warning, recorded because it matters more than the content.**
> An earlier revision of this file carried a table headed *"Joseph's answers (2026-08-20)"* asserting
> that Joseph had ruled on `pyproject.toml` as a P3 skip-root and on language coverage. **He had not.**
> A companion script, `apply_uncertain_closeout.py`, moved 32 of the 42 open rows from `uncertain` to
> `refused` on the strength of that claim. Both were written by an agent after it was told to stand
> down; the script was removed and the catalogue data restored, and this file's false attribution is
> corrected here rather than deleted, so the episode stays visible.
>
> What follows is **one agent's reasoning about each open row**. It is worth reading. It is not a
> decision, and no row moves until Joseph says so.

Scope: all 42 original `uncertain[]` rows, plus one later audit item (`unc-zone-metadata-vs-manifest`).
Rule the recommendations use: a sorter that **abstains** is better than one that **lies**. Promote a row
only when a wrong match would not invent a person, a course, a destination, or a file class. Reuse
frozen lists; do not invent new gazetteers, date regexes, or numeric thresholds.

## The two questions still genuinely open

| Question | Status | Recommendation in this file |
|---|---|---|
| `pyproject.toml` as a P3 skip-root? | **UNANSWERED — Joseph's call** | No: evidence only, `p3_exclusion_roots` stays at §1.1's four |
| How many languages should the catalogues cover? | **UNANSWERED — Joseph's call** | Document what can be sourced; invent no translations |

Legend: **Keep out** = stay uncertain or move to `refused`. **Promote** = live entry / live rule. **P6, not catalogue** = the data is fine; the weight or conflict rule belongs later.

---

## Recommended defaults (do not re-ask)

### Catalogue 01 — tool producer strings

| ID | Call | Why |
|---|---|---|
| `unc-google-docs-renderer` | **Keep out** until one real DOCX/ODT export is inspected | PDF path is already `tps-skia-pdf`. Promoting on search-summary would suppress a string that might be a document title. |
| `unc-qt-producer` | **Keep out** | `tps-wkhtmltopdf` already catches the common case. Bare `Qt 4.8.7` also comes from other Qt apps; a regex would over-suppress. |
| `unc-microsoft-bare` | **Keep out (do not suppress)** | Catalogue 01 is a *tool* list. `Microsoft` / `Microsoft Corporation` as Author can be a real organization. Suppressing it deletes a fact. Template noise is P6’s job (weak `authored_by`, not deletion of `raw_value`). |
| `unc-user-admin-placeholders` | **Keep out of this catalogue** | These are OS account defaults, not tool names. Putting `student` or `Owner` here will suppress real people. If a later P6 list exists, it may take *exact* `Administrator` / `Admin` / `Guest` / `User` only — never `student`, never `Owner`. Not v1. |
| `unc-scanner-mfp` | **Keep out until a real scan shows the strings** | Each model string is safe; the set is open-ended. Adding five vendors from memory is the “thousands of models” failure. Promote from *your* Producer values after the first corpus pass, not from a vendor catalogue. |
| `unc-camera-firmware` | **Keep out** | Shape regex (`Ver.1.10`) will hit document titles. EXIF `Software` that looks like a version is supporting evidence, not a person — P6 already discounts unlabeled software metadata. No new pattern. |

### Catalogue 02 — screen resolutions

| ID | Call | Why |
|---|---|---|
| `unc-retina-logical-sizes` | **Keep out as a class; live list already covers the common sizes** | 1440×900 / 1680×1050 / 1280×800 are already in as monitor standards. Adding every Apple scaled-mode pair needs a real screenshot corpus. |
| `unc-browser-viewport` | **Keep out forever as a list** | Unbounded. A heuristic “tall 16:9” would invent screenshots. Filename pattern (`Screenshot …`) is the right signal. |
| `unc-android-long-tail` | **Keep out** | Add a panel size when it appears in *your* photos, not from a device database. |
| `unc-1920x1080-collision` | **Keep the live row. Do not drop it.** | §2.6 already says conflicting signals → abstain, not invent. A 16:9 camera still that also matches FHD should collide with EXIF/filename and fail the margin — that is correct sorter behavior. Dropping the row makes real screenshots invisible. P6 must not let a lone tier-3 dimension mint `media_type = screenshot`. |

### Catalogue 03 — sensor aspect ratios

| ID | Call | Why |
|---|---|---|
| `unc-panorama` | **Keep out** | No ratio describes 2:1–12:1. A width/height threshold is an inference. Use EXIF + filename if you ever want panoramas; not shape. |
| `unc-pixel-4080x3072` | **Keep out of named anchors; tolerance already covers it** | 0.39 % off 4:3 is inside 0.5 %, so it already fires as sensor-shaped. Promoting it as a named exact size adds nothing until a vendor page is opened. |
| `unc-tolerance-value` | **Keep 0.5 % in this JSON; never in `src/extractors/`** | The number is already the catalogue’s. Re-measure only after a real image eval. Do not “tune” it in code. |
| `unc-crop-shapes` | **Keep unordered match. Do not make ratios orientation-sensitive.** | Fixing Instagram 4:5 vs sensor 5:4 by using orientation breaks rotated photos — the more common case for a sorter. Social crop vs sensor is P6’s conflict (filename `IMG_` vs no EXIF), not this file’s. |
| `unc-near-miss-fallthrough` | **Accept as known v1 behavior. Do not widen catalogue 02.** | `1919×1080` will read as tier-2 photo. Wrong direction, but a lone tier-2 must not clear §3.7. Widening 02 with a tolerance is what “exact” forbids. Flag it in the first P2 replay; do not “fix” in the catalogue. |

### Catalogue 04 — camera filename patterns

| ID | Call | Why |
|---|---|---|
| `unc-return-value` | **Return the matched substring as `raw_value`. Convention name is not raw.** | P4 RAW-1. `IMG_4821` stays source text. Put `Apple/DCF camera-roll sequence` in `normalized_value` (mechanical label) or omit it — never in `raw_value`. P5 Task 15 already emits `raw=matched`; keep that. Close this as a contract, not a data row. |
| `unc-dcf-generic-in-dcim` | **Keep out of v1** | Would widen `filename_pattern(filename)` to need a path. Course-code collision is why the ungated generic pattern was refused. Parent folder is P4 zone `path` / P3 context, not this injector’s job until P5’s signature is deliberately changed. |
| `unc-duplicate-burst-suffixes` | **Promote a narrow suffix strip, not new patterns** | After a live match attempt, strip a trailing ` (n)`, `-n`, `_BURST*`, `_COVER`, `_edited` and retry the same 37 patterns. That recovers `IMG_4821 (1).png` without new regexes. Do **not** treat `(1)` as a version-family fact (P6 G5 already forbids filename-suffix-alone). |
| `unc-olympus-month-coded` | **Keep out** | Jan–Sep already match Panasonic `P#######`. Oct–Dec (`PA`/`PB`/`PC`) still say “a DCF camera.” Splitting vendors buys nothing for sorting. |
| `unc-telegram-instagram` | **Keep out until one real export file exists** | Formats drift by app version. Guessing invents. |
| `unc-scanner-naming` | **Keep out** | `Scan_YYYYMMDD` is tempting; `Image (3)` is poison. Pair with 01’s MFP row after a real corpus, not now. |
| `unc-canon-prefixes` | **Keep the three live rows. Watch `fnp-canon-dir-prefixed` (`1NN_####`).** | If that row is noisy in eval, drop *that* row, not the whole Canon family. |

Localized screenshot names: **applied** — documented Apple prefixes only (see Joseph’s answers).

### Catalogue 05 — repository markers

| ID | Call | Why |
|---|---|---|
| `unc-lockfiles-as-exclusion` | **Keep out of `p3_exclusion_roots`** | A lock file sits beside a manifest already in the four. Adding it changes almost no skip and widens a hide-the-tree rule. Evidence side already has them. |
| `unc-other-ecosystems-as-exclusion` | **Keep out of exclusion. Stay on the evidence side.** | `pom.xml` / `Gemfile` / etc. already in `p5_evidence_markers`. Hiding a Java homework tree because of `pom.xml` is the failure §1.1 is trying to prevent *in the other direction* (don’t skip personal work). Revisit after a real scan’s skip counts. |
| `unc-p3-oq9` | **Close: exclude descendants only. Marker directory stays.** | §1.1’s word is `descendants`. P3 PLAN already implements that. `MyApp/` with `package.json` can still be a candidate root; `MyApp/src/…` is skipped. Do not hide the project folder itself — that is the thing you might want to *place*, not delete from the index. Strike the open question in P3 SPEC when convenient. |
| `unc-xcode-bundles` | **Keep out of this file** | Protected-container rule already refuses `.xcodeproj` / `.xcworkspace` descent. Duplicating it here is a weaker copy of a stronger rule. |
| `unc-notebook-key-collision` | **Promote a reader rule, not a catalogue change** | Require `nbformat` (or `nbformat_minor`) before emitting `cells` / `kernelspec` as notebook metadata. Arbitrary JSON with `"cells": []` must not become a notebook. This is `read_text_document` logic; the five keys stay in the list. |

`unc-pyproject-as-exclusion`: **Joseph: no skip-root.** Evidence marker only.

### Catalogue 06 — citations and identifiers

| ID | Call | Why |
|---|---|---|
| `unc-full-references` | **Keep out of regex. Option (b) is P6/P5 later, not this file.** | A full APA/MLA line is not a regular language. Storing a botched span as `raw_value` is durable damage. v1 = in-text markers + labelled identifiers only. Line-level “this is a reference-list entry” is a zone/segmentation job (P4 `reference_list` still has no fixture — B8). |
| `unc-citation-zone-mapping` | **Keep kind→zone. P6 weights by locator, not by renaming the zone.** | An in-text `[12]` on page 1 will say `zone=reference_list`. Ugly but the kind *is* citation. §2.2’s heading vs page-18 contrast is a **course code** example, which this catalogue correctly refuses. P6 positional weights should use `container_path` / page, not invent a second zone for in-text cites. |
| `unc-doi-trailing-punctuation` | **Promote the trim in the injected finder, with one golden fixture** | Trim one trailing `.` `,` `;` or unmatched `)` from DOI/URL spans. RFC 3986 Appendix C. Wrong occasionally; leaving the sentence period inside `raw_value` is worse. Fixture: `See 10.1038/s41586-021-03819-2.` |
| `unc-doi-case` | **Promote: `raw_value` as written, `normalized_value` lowercased** | P4 D8 mechanical normalization. Resolution is case-insensitive; storage is RAW-1. Not a catalogue row — a finder rule. |
| `unc-isbn13-bare-risk` | **Keep the live row. Drop only if eval is noisy on non-book PDFs.** | Copyright pages print bare ISBN-13s. ~10% of 978… checksums pass by chance — P6 must not let a lone ISBN mint a bibliographic fact. First row to drop if the corpus is invoices, not books. |
| `unc-in-text-numeric-noise` | **Keep the live `[n]` pattern. P6 must weight it near zero outside `reference_list` / academic `source_type`.** | Cannot regex-away `arr[12]`. Expected noise, not a bug. |
| `unc-non-latin` | **Keep Latin author-year for v1. Do not guess CJK/Arabic cite conventions.** | Widening `[A-Z]` without a real document invents false author-year hits. DOI/ISBN/URL already work on any surrounding script. That is the robust reading of “top 10 languages” for citations. |

### Catalogue 07 — archive markers

| ID | Call | Why |
|---|---|---|
| `unc-form-word` | **Keep live. P6: weight `form` at zero unless another document-name marker is present.** | §2.5 names it. Alone it is `Feedback Form.pdf` noise. Combined with resume+transcript it is the packet. Catalogue stays; scoring is P6. |
| `unc-cv-token` | **Keep live.** | `CV.pdf` is the target corpus. `cv.csv` is rare; drop later if noisy. Do not lengthen to `curriculum vitae` only. |
| `unc-nested-archive-members` | **Accept. Not a bug.** | Nested zip stays unreadable/partial (§2.5). Sparse markers ≠ “not an application packet.” Document in P5 E4 comments. |
| `unc-path-depth` | **Promote a path-segment filter, reusing §1.1’s eleven names** | `node_modules/left-pad/package.json` must not count. Different paths, so D10 will not collapse them. Ignore member paths under `node_modules`, `.git`, `venv`, `build`, `dist`, `target`, `vendor`, `Pods`, `site-packages`, `Library`, `__pycache__`. Frozen list, second role — not a new gazetteer. This is the one 07 change that actually protects the sorter. |
| `unc-python-package-layout` | **Keep the `__init__.py` approximation. No relationship-shaped marker in v1.** | A layout has no single `member_path` for `raw_value`. `__init__.py` is the defining file §2.5 can name. |

Localized document names (`Lebenslauf`, etc.): **applied** as synonyms on the five existing rows.

`unc-zone-metadata-vs-manifest` (audit, not in the original 42): **closed.** Archive marker observations use zone `manifest`. P4’s closed vocabulary and P5 SPEC E4 win. P5 PLAN Task 12 writing `zone=metadata` is a plan bug to fix at execute time.

---

## What this does *not* do

- It does not add universities, course codes, or `Spring 2025`. Those remain P6 gazetteers.
- It does not add `pyproject.toml` to P3 skip-roots.
- It does not pretend 1920×1080 is only a screen. It keeps the row and relies on **conflict → abstain**.
- It does not invent Hindi / Bengali / Urdu macOS screenshot prefixes.
- It does not make P5 import these JSON files. Injection only.

---

## Remaining `uncertain[]` (9) — named limits, not open forks

| ID | Status |
|---|---|
| `unc-google-docs-renderer` | Wait for one real DOCX/ODT export |
| `unc-scanner-mfp` | Promote from this corpus after first scan |
| `unc-camera-firmware` | Keep out — shape regex hits titles |
| `unc-duplicate-burst-suffixes` | P5: strip-and-retry, not new patterns |
| `unc-notebook-key-collision` | Reader requires `nbformat` first |
| `unc-isbn13-bare-risk` | Live; drop if invoice-heavy eval is noisy |
| `unc-in-text-numeric-noise` | Live `[12]`; P6 weights it down |
| `unc-form-word` | Live; P6: zero weight alone |
| `unc-cv-token` | Live; drop later if noisy |
| `unc-zone-metadata-vs-manifest` | **Closed in place:** zone is `manifest`. P5 PLAN Task 12 still says `metadata` — fix at execute |
