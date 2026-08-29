# 12/05 — Capture composition rules: P5 signals → P6 facts

Authored 2026-08-22 (salvage-completed; drafted under the R6 dispatch). Status: **rules catalogue** —
this file states composition rules and named slots; it contains no thresholds and no code.
Owner: **P6** (the fact resolver — media type, capture date, photo events). P5's own catalogues
(02–04 at the top level of `deferred-catalogues/`) are already injected into P5 and are **not**
restated here; this file is the P6-side answer to *when do those observations support facts, and
when must P6 abstain*.

Every quotation below attributed to `00` appears verbatim in
`planning/00-database-agent-product-design.md` and was matched mechanically (check.py re-verifies).
Statements sourced to the P6 SPEC are paraphrases with locators, not quotations.

Provenance marks: `design` (00 states it), `inference` (follows from stated rules),
`proposal` (authored here for Joseph to keep or drop).

---

## 1. What arrives from P5 — and is not re-derived here

P5 classifies dimension and filename signals using the already-injected catalogues:

| Input | Produced by | Catalogue | What it carries |
|---|---|---|---|
| `dimension_signal` = exact display resolution | P5 E5 | `02-screen-resolutions.json` | tier-3 screenshot-hypothesis signal |
| `dimension_signal` = sensor-shaped dimensions | P5 E5 | `03-sensor-aspect-ratios.json` | tier-2 reinforcing signal |
| `filename_pattern` (naming-convention label) | P5 E5 | `04-camera-filename-patterns.json` | a tier-less `possible` observation — labels name **naming conventions, never media types** (catalogue 04's own rule 5) |
| camera EXIF (make, model, lens, capture time, GPS) | P5 E5 | — | tier-1 / tier-2 observations in the `metadata` zone |
| `signal_tier ∈ {1,2,3}` | P4 shape (M2) | — | §2.6's hierarchy, assigned upstream |

**Rule 1.1 (design).** P6 consumes `signal_tier` as given and never re-derives it from
`extractor_name` or a field label — the P6 SPEC (M2, conflicting image signals) forbids encoding
§2.6 in a second place. This file therefore assigns no tiers; it only composes them.

**Rule 1.2 (design).** Absence is not an observation. P5 records absence of EXIF on
`extraction_runs`, so no observation exists for a missing signal and nothing in this file can
consume one. This is the mechanical form of `00`'s absolute:

> "the system must not mistake the absence of EXIF for proof that an image is a screenshot"

and its reason:

> "Messaging platforms and downloaded web images often strip metadata from real photographs."

---

## 2. `media_type` — the composition rule

`media_type` is a §3.11 Photos field ("Photos may use capture year, event, location, people,
camera information, and media type."). Its allowed value set is a **deferred enum** (P6 SPEC,
Deferred table) — this file composes evidence for the two hypothesis values `00` itself discusses
(photograph, screenshot) without authoring the enum.

**Rule 2.1 (design).** Resolution is the ordinary §3.7 procedure — P6 SPEC states it for exactly
this case: each tiered observation is a weighted vote for one candidate, candidates are ranked, and
the winner must clear **both** the injected minimum score and the injected margin. There is no
bespoke screenshot classifier.

The tier bands, as `00` sets them:

> "camera EXIF is strong photo evidence; capture time, GPS, and sensor-shaped dimensions reinforce
> it; exact display resolutions, PNG format, and software metadata may support a screenshot
> hypothesis; conflicting signals should lead to abstention rather than an invented classification"

**Rule 2.2 — the two absolutes (design).** Carried over from §2.6 as P6 Done-means assertions:

1. **A missing EXIF signal is never evidence for anything.** No observation exists for an absence
   (Rule 1.2), so "no EXIF ⇒ screenshot" is unbuildable by construction — and stays that way.
2. **OCR text density is never a screenshot signal.**

   > "OCR text density is also not a reliable screenshot detector because receipts, document scans,
   > whiteboards, and photographs of pages can all contain dense text."

**Rule 2.3 (inference).** A catalogue-04 `filename_pattern` observation is a `possible`-grade clue
about a *naming convention*. It may sit in the evidence packet; it is never a vote strong enough to
fill `media_type` on its own — catalogue 04 refuses media-type conclusions on the P5 side, and the
never-alone reading is the same rule on this side.

**Rule 2.4 (design).** Below-margin conflict fills nothing and emits one `unresolved` row with
reason `below_margin` (P6 SPEC's reason vocabulary) — which is §2.6's abstention requirement stated
in P6's terms. Abstention is a successful outcome, not a failure.

**Named slots (injected, no values here):** `signal_tier_weights` (what each of the three tiers is
worth in the §3.7 vote — deferred with the other §3.7 weights, P6 SPEC M2), `min_score`,
`min_margin`, `positional_weight_by_zone`.

### Decision table (rules above, in one view)

| Evidence present | May support | May never do |
|---|---|---|
| tier 1: camera EXIF (make/model/lens) | photograph, strongly | — |
| tier 2: capture time, GPS, sensor-shaped dimensions | photograph, reinforcing | establish photograph alone against conflicting tier-1-less screenshot evidence without clearing margin |
| tier 3: exact display resolution, PNG format, software metadata | screenshot hypothesis | conclude screenshot below the injected score/margin |
| catalogue-04 filename pattern | a `possible` clue about naming | fill `media_type`; contribute to a photo event |
| absence of EXIF | nothing | support screenshot ("no EXIF ⇒ screenshot" is refused) |
| OCR text density | nothing (for media type) | act as a screenshot detector |
| conflicting tiers, margin not cleared | nothing | an invented classification — `unresolved(below_margin)` instead |

---

## 3. `capture_date` and `capture_year`

**Rule 3.1 (design).** `capture_date` has exactly one authored source: the EXIF `DateTimeOriginal`
slot family (`04-narrow-date-families.json`, `fam-exif-datetimeoriginal`), producing a `direct`
fact — `00` §3.2's own worked pair, asserted by P6 SPEC Done-means 5.

**Rule 3.2 (inference).** `capture_year` (the §3.11 Photos field) derives from the year component
of a `capture_date` fact. It is never read from a printed year in text or a filename — a bare year
is a refused date shape (12/04, `ref-bare-year`).

**Rule 3.3 (inference).** A date parsed from a *filename* (12/04's compact family matching
`IMG_20240517_123456.jpg`) is a `creation_date` candidate on the §3.10 path, `validated` at best.
It never fills `capture_date`: filenames are not the EXIF slot, and messaging apps rewrite
filenames as freely as they strip metadata.

---

## 4. Photo events — G7, named slots only

The Photos-domain `event` fact is P6's (P6 SPEC G7): a deterministic clustering over EXIF
observations, seeding P9's photo groups. `00`:

> "Camera EXIF, GPS, and capture time can support deterministic photo-event proposals."

**Rule 4.1 (design).** Inputs are P5's camera, capture-time and GPS EXIF observations **only**.
Tier-3 screenshot signals never contribute to an event. Absence of EXIF produces no event.

**Rule 4.2 (design).** Reliability is `validated` — a deterministic rule passing a contextual
check — and never `direct` (no slot states the event) and never `possible` (P9 requires seed facts
at Direct or Validated strength). `event` values auto-create (§3.12 names "event" in the
auto-create list).

**Rule 4.3 (design, G7).** The clustering parameters are **named slots with no values in this
repo** — the design names the inputs and states no thresholds, and this file follows it exactly:

| Slot | What it will hold (when Joseph sets it) | This file's contribution |
|---|---|---|
| `event_time_window` | how close two capture times must be to sit in one event | the name |
| `event_gps_radius` | how close two GPS fixes must be to sit in one event | the name |
| `camera_identity_test` | what counts as "the same camera" (make/model equality, body serial when present, or a policy mixing them) | the name |

No number, distance, duration or count appears in these slots anywhere in catalogue 12, and
check.py asserts the slot definitions above carry no digits.

**Rule 4.4 (inference).** A file with a capture time but no GPS may still join an event only under
whatever `camera_identity_test` + `event_time_window` policy Joseph sets — this file does not
decide it; the slot owner does. What this file does decide: a cluster built **only** from
tier-3 signals or filename patterns is not an event, ever.

---

## 5. Abstention map — what P6 writes when composition fails

| Situation | P6 outcome (P6 SPEC vocabulary) |
|---|---|
| conflicting media-type signals, margin not cleared | no fact; `unresolved(below_margin)` |
| no candidate evidence at all (e.g. stripped EXIF, no dimension signal) | no fact; `unresolved(no_candidate_evidence)` |
| EXIF slot present but value fails its layout | no fact; `unresolved(normalization_failed)` |
| screenshot hypothesis supported only by a filename pattern | no fact (never-alone, Rule 2.3); `unresolved(below_score_threshold)` once ranked |
| event clustering inputs absent | no `event` fact, no row invented — there was nothing to attempt |

---

## 6. Acceptance constraints

- **A07** (`tests/eval/fixtures/adversarial/A07.json`, "stripped EXIF on messaging-app
  photographs"): zero observations; the expected outcome is `abstained` and the forbidden value is
  `screenshot`. Rules 1.2 and 2.2 are the defense; any composition that reads absence as evidence
  fails A07.
- **A08** (`A08.json`, "screenshots with unreadable OCR"): the residual side of Rule 2.2's second
  absolute — unreadable OCR must not push a file into placement (`leave_in_place`, never
  `return_to_placement`). This file's contribution is upstream: OCR density never made it a
  screenshot in the first place.
- **P6 SPEC Done-means 5** — the EXIF capture-date row (Rule 3.1).
- **A01/A02** are not capture cases but bind every pattern in catalogue 12: word-boundary, never
  substring.

## 7. Open forks touched by this file (recorded in README.md NEEDS-JOSEPH, never closed here)

- The `media_type` enum's allowed values (P6 deferred) — this file composes evidence for the two
  `00`-named hypotheses only.
- The three G7 slots' values, and Rule 4.4's mixed-evidence policy.
- Whether sibling EXIF date slots route to `capture_date` (12/04 `unc-exif-sibling-slots`).
