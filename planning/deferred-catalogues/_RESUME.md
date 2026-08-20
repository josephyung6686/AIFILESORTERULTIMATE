# Resume state — deferred evidence catalogues

Working state for an interrupted session. Delete this file when all seven catalogues are done.
Paused 2026-08-20 at Joseph's request (laptop closing). Nothing is half-written: every file listed
as done is complete, rendered, and passing its checks.

## Done — 3 of 7

| File | entries | verified by |
|---|---|---|
| `01-tool-producer-strings` | 115 entries, 6 refused, 6 uncertain | `checks/check01.py` — PASS |
| `02-screen-resolutions` | 70 entries, 4 uncertain | `checks/check23.py` — PASS |
| `03-sensor-aspect-ratios` | 5 ratios, 12 sensor-size anchors, 3 refused, 5 uncertain | `checks/check23.py` — PASS |

## Remaining — 4 of 7, plus README

- `04-camera-filename-patterns` — **in progress, nothing written yet.** Research is done; the
  design decisions below are settled and should not be re-litigated.
- `05-repository-markers` — two arrays, `p3_exclusion_roots` and `p5_evidence_markers`.
- `06-citation-identifier-patterns` — DOI, ISBN, ISSN, arXiv, ORCID, PMID. **No §3.10 date regexes.**
- `07-archive-recognizable-markers` — feeds P5 E4's `recognize_markers`; `MARKER_KINDS` is exactly
  `("source-code manifest", "document name")` and a third class raises `UnknownMarkerKind`.
- `README.md` — owner, consumer, and the injection rule (never a module-level constant in `extractors/`).

## How to resume

```bash
cd "planning/deferred-catalogues"
python3 render.py            # JSON -> MD; JSON is the source of truth, never hand-edit an .md
python3 render.py --check    # no-drift guard, exits non-zero if any .md is stale
python3 checks/check01.py    # list 01 matcher + acceptance cases
python3 checks/check23.py    # list 02/03 arbitration + overlap flags
```

`checks/build02.py` regenerates `02-screen-resolutions.json` from its row table — edit that script,
not the JSON, when adding resolutions.

## Settled decisions — carry these forward, do not redesign

1. **`prefix` is not "starts-with".** It fires on whole-value equality, or on prefix + boundary
   character + a remainder containing a digit. A test caught `Microsoft Word` matching
   `Microsoft Word skills certificate` under naive starts-with. Two rows opt out with
   `tail_required: "any"` and carry their own false-positive analysis.
2. **Arbitration between 02 and 03.** `dimension_signal` returns at most one name. Catalogue 02
   (exact) is consulted first, then catalogue 03 (ratio, 0.5 % tolerance), else `None`. Reasoning is
   written out in both files.
3. **Catalogue 02 stores the landscape form** (`1920x1080`) with `also_written` for portrait; the
   matcher compares the unordered pair.
4. **`4032x3024` is a catalogue-03 anchor, never a catalogue-02 row.** `checks/check23.py` asserts
   no anchor is also a resolution.

## Settled decisions for file 04 — research already done, write these

- **The design's own words matter here.** §1.2: "`IMG_4821.png` may be a screenshot of a receipt,
  application portal, conversation, code error, or research figure." So `IMG_####` is catalogued as
  the **Apple/DCF camera-roll naming convention** — a fact about the string's form — and *not* as a
  media-type verdict. The iOS ambiguity (screenshots saved to Photos get the same name) is recorded
  on the row. This is why P5 emits the filename pattern at `reliability: possible` with **no
  `signal_tier`**: filenames are absent from §2.6's tier table, so this catalogue cannot smuggle a
  screenshot signal into the hierarchy.
- **Pattern labels name the naming convention, never the media type** — "Apple/DCF camera-roll
  sequence", "macOS screen-capture default filename" — because P5 SPEC E5 forbids E5 emitting any
  photo/screenshot conclusion.
- **Match against the filename stem**, extension removed. P5 passes `file_row["filename"]`, which
  includes the extension.
- **Patterns are ordered; first match wins.** `IMG_20240115_103045` must not fall into `^IMG_\d{4}$`
  — anchoring handles it, but the order and a test should both assert it.
- **No date parsing.** Android/iOS filenames embed timestamps; the pattern recognises the *shape*
  and must never parse, normalise, or emit a date. §3.10 is P6's.
- **Open contract question for the report:** does `filename_pattern(filename) -> str | None` return
  the matched substring or the pattern name? P5 PLAN Task 15 does `emit(zone="filename", raw=matched,
  label=None, reliability="possible")`, so the return value becomes `raw_value`. Give each entry both
  a `capture` group and a `pattern_label` so either reading works, and put the question in
  `uncertain`.
- **Include a `messaging` class** (`IMG-20240115-WA0001`). It is the positive evidence that *explains*
  stripped EXIF, which is what §2.6's trap 1 wants instead of inferring from absence.
- **Sources already retrieved 2026-08-20** (re-cite, no need to re-search):
  - JEITA CP-3461 / DCF — <https://en.wikipedia.org/wiki/Design_rule_for_Camera_File_system> —
    "The first four characters consist only of the upper-case alphanumeric characters (A - Z),
    (0 - 9) and the underscore `_` character, followed by a number between `0001` and `9999`…
    Common four-character prefixes include `DSC_`, `DSC0`, `DSCF`, `IMG_`/`MOV_`, or `P000`."
    Directory form is `100APPLE` / `101MSDCF`. Generic pattern: `^[A-Z0-9_]{4}[0-9]{4}$`.
  - JEITA standard page — <https://www.jeita.or.jp/cgi-bin/standard_e/pdf.cgi?jk_n=51&jk_pdf_file=CP>
  - Canon KB on DCF file naming — <https://support.usa.canon.com/kb/s/article/ART156893>
  - Android/vendor conventions (weaker sourcing, mark accordingly) —
    <https://forum.fairphone.com/t/default-camera-app-of-android-schema-of-file-names/23056>

## Constraints still in force

- Create files **only** under `planning/deferred-catalogues/`. Read anything.
- Do not edit `src/` — especially not `src/extractors/` — `tests/`, or any existing planning doc,
  beyond at most a one-line pointer in `planning/parts/P5-extractors/PLAN.md` and
  `planning/parts/P6-facts-facets/SPEC.md` if genuinely needed. No pointer has been added yet.
- Nothing has been committed. Joseph reviews and commits.
- **Default: add nothing to `p3_exclusion_roots`**; anything added there must be marked
  `"status": "proposed"`. Extra language ecosystems go in `p5_evidence_markers` first.
