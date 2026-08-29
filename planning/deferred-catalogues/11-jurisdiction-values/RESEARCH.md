**No jurisdiction is packed: D4 ratified the shape (one jurisdiction, values only, injected) but
not the member; Joseph's corpus jurisdiction is stated nowhere I could find; so per the dispatch
prompt this deliverable is the file shape, a two-row `00`-example seed, and NEEDS-JOSEPH "which
one" with two seed packs sketched — picking silently is the forbidden move.**

# Catalogue 11 — research record

Authored 2026-08-22 by R5. Nothing is committed by the authoring agent — Joseph reviews and
commits. A prior R5 run was killed by a session limit **before writing anything**: at salvage
time (2026-08-22) `planning/deferred-catalogues/11-jurisdiction-values/` did not exist, so there
was no draft to audit and everything here is first-authored this pass, with every mechanical
claim verified fresh (section 9).

**Second salvage pass, same day:** the run that authored these files was itself interrupted by a
session limit. A successor R5 pass re-audited the whole directory as an untrusted draft: every
quoted span in the markdown files re-verified against its named source (the JSON quotes were
already gated by `check.py`), every count in section 3 and `field-hygiene.md` re-derived by an
independent scan, every catalogue-08 hook and slot re-resolved, and `check.py` re-run clean. One
error was found and fixed: the country tally had copied the ships seat's "UK 8" instead of this
scan's own word-boundary count (7 at 574; the correction is noted inline in section 3). All
other claims reproduced exactly.

---

## 1. The decision state, exactly

- **Ratified** (DECISION-BRIEF RATIFIED table, 2026-08-21; applied at `_CONTRACT.md` rule 9):
  "`jurisdiction` is a **value, never a field name and never a destination dimension**. One
  jurisdiction's gazetteers in v1, injected."
- **Open**: which jurisdiction. The brief's own D4 section: "v1 ships one jurisdiction's
  gazetteers, injected per deployment; the list is decided when P10 is planned" — and its
  recorded fork: risk seat says US-shaped (from the design's worked examples), ships seat's
  catalogue tally says UK-shaped. Both are quoted in section 3 with corrections.
- The dispatch prompt describes D4 as "recommendation, not ratified" — it predates the
  ratification. The recorded state is followed: the *shape* questions the prompt leaves
  conditional are closed (value not field; one pack; never a dimension), and the *member*
  question is exactly as open as the prompt assumes.

## 2. Sources read

| source | what it contributed |
|---|---|
| `planning/00-database-agent-product-design.md` | the zero-result scans (jurisdiction / country / locale / GDPR / HIPAA / United States / W-2: zero occurrences each — this is absence, not under-specification); §3.12's value-auto-creation sentence, the field/value language; §3.10's `Michaelmas Term 2024`; §3.15's safety-domain sentence; §4.9's protected-records sentence; §7.3's Protected Records contents; §8.6's false-impression sentence; the US-shaped worked entities (UChicago, Columbia, Duke, Cornell, Georgetown Prep, BUSIB 4300, PHYS1401) |
| `planning/01-product-design-structured.md` | § locators only (per CONNECTION.md's convention); §3.11's six-domain table, §7.3's nine residual names, §5.4's template sentence |
| `planning/overnight/council/DECISION-BRIEF.md` | D4's ratified row and open half; the seat disagreement |
| `planning/overnight/council/seat-what-goes-wrong.md` | the failure analysis (recognition fails by not firing; detectors fail safe); the two cheap asks this catalogue implements (structured jurisdiction key → the row tag; the residual honesty string → `unsupported-region.md`); the "29 field rows" count |
| `planning/overnight/council/seat-design-reading.md` | the altitude rule ("the design says `record type`, the catalogue wants to know whether that record is a W-2 or a P60"); "It has not decided anything." |
| `planning/overnight/NEEDS-JOSEPH.md` B4 | the original three-catalogue question this catalogue answers the answerable half of |
| `planning/domains/_CONTRACT.md` | rules 3 (no numbers), 9 (D4 applied), 10 (D1: no career/identity/medical/legal field rows — why `field_pending_R1` exists) |
| `planning/domains/CONNECTION.md` | values are never roster nodes (section 2); never-alone (section 4 step 2); one canonical field list (section 6); PR-2 (safety schemas: protection plus small schema), PR-8 (insurance as templates over Finance vocabulary) |
| `planning/domains/canonical_fields.json` | the 37 keys; `record_type` / `tax_year` / `account_type` / `institution` resolve; no court / permit / identity / medical key exists (D1) — the `field_pending_R1` boundary is drawn from this file |
| `planning/domains/05-…,06-…,07-…,12-…,13-….json` | the value mining (section 3) and the field-hygiene scan (`field-hygiene.md`) |
| `planning/parts/P7-privacy-consent-gate/SPEC.md` | "Absence of a classification resolves to `unreadable_unclassified`, never to `public_low`." — the safety-independence anchor |
| `../08-sensitivity-detector/` | the consumer contract: four injected slots owned by R5 (section 5); the detector hook ids value rows point at; `02-identifier-classes.json`'s `jurisdiction_dependent: true` classes |
| `../10-gazetteers/` | the boundary (institutions are R4's; this catalogue's brief quoted there verbatim); the schema conventions this directory copies (word-boundary matcher, rule N, quote checking, injected null slots) |
| `../12-academic-capture-patterns/` | R6 landed with twelve term-pattern families including Michaelmas — category 6 is closed as "R6's, nothing to add" |

**No external source was consulted.** Every string in the JSONs is design- or overnight-derived
and cited; the registers a real pack would draw on (IRS forms index, gov.uk form lists, court
directories) are named in the sketches as candidate universes for a decision, not sources
opened. Same discipline as R4's RESEARCH.md, stated the same way.

## 3. The split, recounted at 574

**Prose jurisdiction-dependence** (entries whose JSON mentions `jurisdiction` anywhere,
case-insensitive): **124 of 574** — government 34, law 28, trades-property-logistics 24,
finance-legal-admin 21, career 7, engineering 4, healthcare 3, business 2, research 1. The risk
seat's "124 of 560" reproduces exactly at 574.

**Country and agency mentions** (word-boundary scan over the 14 JSON slices; the `.md` files
mirror the JSONs and are excluded to avoid double counting): England 8 · Wales 8 · UK 7 ·
United Kingdom 7 · Canada 3 · Ireland 2 · Scotland 1 · European Union 1 · Companies House 1 ·
NHS 1 · United States 1 · British 1 (that last is `British Airways`, not a jurisdiction
signal). Method differences against the ships seat's tally (it counted bare `EU` tokens; this
scan counted `European Union` and `EU ` forms; its "UK 8" over 560 is 7 under this scan's
word-boundary rule at 574) do not move the conclusion: **the catalogue's prose is UK-shaped.**

**The design is US-shaped — with one correction that matters.** The design's worked entities
are UChicago, Columbia, Duke, Cornell, Georgetown Prep, `BUSIB 4300`, `PHYS1401`, plus exactly
one British token, `Michaelmas Term 2024`. But **`W-2` is not in `00`** — zero occurrences,
verified mechanically — despite two seat documents attributing it to "the design's worked
examples" (`seat-what-goes-wrong.md`: "the worked examples throughout the design (`BUSIB
4300`, `W-2`, `UChicago`)"; DECISION-BRIEF D4 repeats the trio). W-2 entered the record through
the seats' own prose, which is why the seed rows carry `provenance: proposal` and
`source_kind: overnight_prose`, never `design`. The US-shaped conclusion survives the
correction (the institutions carry it); the citation does not.

**A nuance the council did not record: the split runs *within* the catalogue.** The
finance/legal/government slices are UK-flavoured (`VAT`, `grant of probate`, `lasting power of
attorney`, `council tax banding`, `Companies House`, `building regulations approval`), while
the healthcare slice is US-flavoured (`explanation of benefits`, `superbill` — and
`med.insurance-claim-eob` is an entry id). Whichever pack Joseph picks, some catalogue prose is
pointed the wrong way; it is examples and recognition strings, which is the cheap direction to
re-point (the brief says the same).

## 4. The six value categories — what a pack must hold, and what already exists

1. **Tax record types** → values of `record_type` (canonical, resolves;
   `00`: "Finance files may use institution, account type, tax year, and record type").
   The 574 deliberately wrote `return_type` "described functionally, never by a jurisdiction's
   form name" — the form names were left for exactly this catalogue. Consumers: P6 facts +
   catalogue 08's `tax_form_identifier_gazetteer` (hook `det-tax-form-completed`, whose
   completed-vs-blank discrimination is its populated-values conjunct, not ours). Seeded with
   the W-2/P60 pair; the rest is pack-sketch material.
2. **Identity document types** → no canonical field and none may be minted (D1: identity is a
   field-less placeholder; PR-2/PR-6). A chosen pack ships them as a `field_pending_R1` value
   file (fact-side dormant until Joseph authors the schema) whose **gate projections are live
   immediately** — hooks `det-passport-mrz`, `det-id-drivers-licence`, `det-id-travel-visa`,
   `det-id-national-id-labeled`, `det-id-civil-certificate`; plus `gate_label` rows for
   national-identifier label wordings (the identifier *values* are redaction input, never
   facts — catalogue 08's `government_id_number` class). Protection does not wait on the pack
   either way (section 6 of `README.md`).
3. **Court and matter types that appear on real PDFs a person keeps** — court names, form/claim
   labels, caption wordings — not the civil procedure code. Court *names* are this catalogue's
   (institutions in R4 are schools/orgs/financial; the R4 README records the courts boundary on
   its side). No canonical field (D1 legal deferral) → `field_pending_R1` file plus
   `legal_caption_gazetteer` extensions (catalogue 08 holds the generic openers — "IN THE
   UNITED STATES DISTRICT COURT", "IN THE HIGH COURT OF" — as its own data; one jurisdiction's
   long tail is pack content). The 574's `legal.court-records` shows the functional altitude
   (`forum`, `case_number`, `document_type`) whose value space the pack fills.
4. **Permit and licence names a household or small business actually files.** Same shape:
   functional fields exist in the 574 (`licence_type`, `consent_type`), the names are pack
   values, no canonical field yet (`field_pending_R1`). The 574's own examples are first
   sketch members (`building regulations approval`, `premises licence` shapes in slice 13).
5. **Healthcare record types that appear on exports.** Detecting them is R2's
   (`det-medical-eob`, `det-medical-clinical-document`); *naming* them as values is this
   catalogue's. The 574 already carries `explanation of benefits`, `superbill`, `discharge
   summary` as work-type prose. Medical is a D1 placeholder → `field_pending_R1`; note
   `discharge summary` is jurisdiction-light (both sketches carry it) while `EOB`/`superbill`
   are US-specific and `FIT note`/`FP10` are UK-specific.
6. **Academic calendar tokens** — **closed: R6's.** The dispatch prompt's "beyond R6's three"
   predates R6's landing; R6 shipped twelve term-pattern families (US season-year, AY ranges,
   UK named terms, quarters, semester ordinals, German, CJK 年度, bare ranges), including
   `Michaelmas Term 2024`, which is `design` (`00` §3.10) and survives any pack choice, US
   included. This catalogue adds no calendar tokens; `check.py` guards Michaelmas's survival
   in `00` and in R6's file, and forbids any non-design Michaelmas row here, so the ownership
   cannot silently respell.

## 5. The catalogue-08 consumer contract (verified against its JSON)

Catalogue 08's `injected_slots` declares exactly four slots with `owner: "R5 (jurisdiction
values)"` — `check.py` cross-checks the set on every run and fails if it drifts:

| slot | 08's meaning (paraphrase) | this catalogue's carrier |
|---|---|---|
| `tax_form_identifier_gazetteer` | jurisdiction tax-form identifiers as values; 08 holds the type, R5 the names | `record_type.json` rows via `gate_slots` |
| `national_id_label_gazetteer` | label wordings per jurisdiction, plus per-label value shapes | `gate_label` rows (chosen pack) |
| `account_locator_patterns` | jurisdiction account-locator value shapes (IBAN-style, routing/sort-code-style) | `gate_label` rows with `value_shape` (chosen pack) |
| `legal_caption_gazetteer` | court-caption and instrument wordings extending 08's generic English markers | `gate_label` rows (chosen pack) |

Also 08's `02-identifier-classes.json`: classes marked `jurisdiction_dependent: true` (phone
shapes, address formats, `government_id_number`) name R5 as owner of shapes/labels per
jurisdiction — same carrier, `gate_label` rows. And 08's open item `unc-localized-labels`
(English-only label lists; "fold into R5?") lands with pack authoring — recorded in
NEEDS-JOSEPH below, not closed.

## 6. Seams recorded (not defects, not mine to fix)

- `canonical_fields.json`'s `record_type` row carries `gazetteer: null`; wiring this pack into
  R1a's per-field gazetteer tags (as `schools`/`orgs` are wired for R4) is R1a/P6's edit when a
  pack lands.
- P11's residual surface has no field for the honesty string yet (the risk seat's §7.5
  observation) — `unsupported-region.md` defines the slot; the SPEC edit is P11's.
- The risk seat's safety reassurance rests on P7 Task 3's absence rule, which is contract but
  unbuilt; `README.md` carries the caveat beside the claim.
- R4 and this catalogue share the D4 fork: Joseph's one answer picks R4's institution register
  and this catalogue's pack together.

## 7. The two seed packs, sketched for the decision

**Sketches, not rows.** Everything below is `proposal`, illustrative, and deliberately not
authored as JSON — authoring either one is the ratification protocol in `PACKS.md`, and
shipping both was refused (D4 option 2). First-wave members are chosen for what actually
appears in a personal/small-business corpus; completeness is what the named registers are for.

### `us/` — if Joseph's corpus is US-shaped (the design's institutions suggest it)

| category | first-wave values | notes |
|---|---|---|
| `record_type` (resolves) | W-2 · W-4 · 1099-NEC · 1099-MISC · 1099-INT · 1099-K · 1040 · 1098 · 1098-T · 1095-A/B/C · Schedule K-1 · property tax statement | hooks: `det-tax-form-completed`; candidate universe: the IRS forms index |
| identity documents (`field_pending_R1`) | passport · passport card · driver's license · REAL ID · Social Security card · permanent resident card · employment authorization document · visa classes as values (F-1, J-1, H-1B, B-1/B-2) | hooks: `det-passport-mrz`, `det-id-drivers-licence`, `det-id-travel-visa`, `det-id-civil-certificate` |
| gate labels | "Social Security number" / "SSN" · "ITIN" · "EIN" · routing-number and account-number shapes | `national_id_label_gazetteer`, `account_locator_patterns`; value shapes authored with the pack |
| courts / matter types (`field_pending_R1`) | United States District Court · Court of Appeals · state Superior/Circuit Court · small claims · summons · complaint · subpoena · judgment | caption extensions over 08's generic openers |
| permits / licences (`field_pending_R1`) | business license · building permit · certificate of occupancy · seller's permit · vehicle registration and title | |
| healthcare record types (`field_pending_R1`) | EOB · superbill · CMS-1500 · UB-04 · discharge summary · after-visit summary · immunization record | hooks: `det-medical-eob`, `det-medical-clinical-document`; the 574's healthcare prose already leans this way |
| academic calendar | — | R6's; US season-year patterns already exist there |

### `uk/` — if Joseph's corpus is UK-shaped (the catalogue prose suggests it)

| category | first-wave values | notes |
|---|---|---|
| `record_type` (resolves) | P60 · P45 · P11D · SA100 Self Assessment return · SA302 · VAT return · council tax bill · PAYE coding notice · CT600 | hooks: `det-tax-form-completed`; candidate universe: gov.uk / HMRC form lists |
| identity documents (`field_pending_R1`) | passport · driving licence · biometric residence permit · National Insurance number letter · visa vignette | hooks as US row |
| gate labels | "National Insurance number" / "NI number" / "NINO" · "UTR" · sort-code and account-number shapes | as US row |
| courts / matter types (`field_pending_R1`) | County Court · High Court · Crown Court · Magistrates' Court · Employment Tribunal · claim form · particulars of claim · judgment · decree absolute | the 574's own examples (Employment Tribunal, `England and Wales`) came from here |
| permits / licences (`field_pending_R1`) | planning permission · building regulations approval · premises licence · MOT certificate · V5C · TV licence | `building regulations approval` is already a 574 example value |
| healthcare record types (`field_pending_R1`) | discharge summary · GP referral letter · FIT note · FP10 prescription · NHS appointment letter | |
| academic calendar | — | R6's; `Michaelmas Term 2024` is design and ships regardless |

## 8. NEEDS-JOSEPH

Open questions only; none is closed here, and D4's ratified shape is not re-opened.

- **NJ-R5-1 · Which jurisdiction is the v1 pack?** The one real fork. The evidence points both
  ways by construction (section 3): the design's institutions are US, the catalogue prose is
  UK, and the healthcare slice is US again. Sketches for both are in section 7; the
  ratification protocol (five edits, one commit) is in `PACKS.md`; R4's institution-register
  choice rides on the same answer. Until answered: no deployable pack, `check.py` fails any
  `v1` manifest, and safety is unaffected (README, "Safety does not depend on the pack").
- **NJ-R5-2 · The immigration two-jurisdiction case.** `admin.immigration` (legacy 574) argues
  a per-file jurisdiction pair (`destination_jurisdiction`, `nationality_jurisdiction`) is
  load-bearing for that domain, and D4's letter forbids jurisdiction field names. Both facts
  are recorded in `field-hygiene.md`. The collision only becomes live when Joseph authors the
  D1-deferred legal/identity schemas; flagged so it is decided then, not rediscovered.
- **NJ-R5-3 · Ratify the `unsupported_region_copy` wording** ("This domain is not modelled for
  your region.") — `proposal` until then, held so by `check.py`; and the P11 §7.5 surface seam
  (the risk seat's observation) needs a SPEC owner when P11 is next edited.
- **NJ-R5-4 · Localized (non-English) label lists** — catalogue 08's `unc-localized-labels`
  points at R5: the OCR ratification says which languages produce text; whose labels ship is a
  corpus question, and it lands with pack authoring (a pack may need non-English aliases —
  the per-alias `script` key already represents them without schema change). Kept open here
  and there.

## 9. Audit record — mechanical verifications, this pass

| claim | method | result |
|---|---|---|
| prior-run salvage | listed `planning/deferred-catalogues/` at session start | `11-jurisdiction-values/` absent; nothing to salvage; all files first-authored 2026-08-22 |
| second-pass audit (authoring run also interrupted) | successor pass treated the directory as an untrusted draft: markdown quotes re-verified against sources, all counts re-derived independently, hooks/slots re-resolved, `check.py` re-run | one fix — country tally "UK 8" corrected to 7 (the 8 was the ships seat's 560-count, not this scan's); everything else reproduced exactly |
| `00` says nothing about jurisdiction | word searches: jurisdiction, country, locale, GDPR, HIPAA, United States | zero occurrences each |
| `W-2` not in `00` | word search | zero; found only in the two seat files and the DECISION-BRIEF (locations recorded in section 3) |
| `Michaelmas Term 2024` in `00` | exact-string search | present (§3.10 sentence); also present in R6's `03-academic-term-patterns.json` (`atp-uk-named-term`); both asserted by `check.py` on every run |
| `w2_tax_year`-class field names | underscore-tokenized scan, 574 entries: 3,706 schema-field rows + 1,648 dimension members | **0** — D4's claim re-confirmed at 574 |
| jurisdiction-named fields | same scan | **29** literal + **4** `*_jurisdiction` + **2** `governing_law` = 35 rows / 34 entries; **4** of the 35 field rows also inside a `dimension_order` — full table in `field-hygiene.md` |
| jurisdiction-named dimension members | same predicate applied directly to all 1,648 `dimension_order` members (not via schema-field cross-reference) | **6** — the 4 mirroring field rows, plus 2 dimension-only compounds (`issuing_board_or_jurisdiction`, `jurisdiction_or_route`) with no matching schema field name; both missed by this file's first pass, caught by adversarial audit — table in `field-hygiene.md` |
| prose dependence | per-entry substring scan | 124 of 574, per-slice counts in section 3 (risk seat's number reproduced) |
| canonical list clean | key scan of `canonical_fields.json` (37 keys) | no jurisdiction-named key; `record_type`/`tax_year`/`account_type`/`institution` resolve; no court/permit/identity/medical key (D1) |
| catalogue-08 contract | parsed `01-detector-rules.json` | exactly four R5-owned injected slots (names in section 5); all `detector_hook` values in the seed resolve to 08 entry ids; both asserted by `check.py` |
| every quote in this directory's JSONs | `check.py` whitespace-normalized span check against the named source file | passing (run `python3 check.py`) |
| seed matcher behaviour | `check.py` reference word-boundary matcher | `W-2` matches nowhere in `SW-2000`/`W-2000`/lowercase prose; `P60` nowhere in `P600`/`UP60`; each `example_true` matches its own row; each `example_false` matches no row in its file |
