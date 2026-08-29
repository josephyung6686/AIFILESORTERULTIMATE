# creative.printmaking-editions — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: creative`, `launch: placeholder`, `parent_id: null`.
Output: [`creative.printmaking-editions.json`](creative.printmaking-editions.json).
Salvage: none — both files are new. No prior draft existed.

**Verdict: the node SURVIVES, narrowed.** It survives as the *impression register* — one matrix and
the closed enumerated set of objects pulled from it. It does **not** survive as "physical craft."
The narrowing is the main finding of this pass and is recorded as open_question 1, a rename
recommendation for R1c, not a roster edit.

## Sources actually used

- `RESEARCH-BRIEF.md` + `make_prompt.py creative.printmaking-editions` — brief and stamped assignment.
- `planning/00-database-agent-product-design.md` — **grepped, not streamed**, per the token rule.
  Every span I quote was matched against it verbatim by script before it entered the JSON
  (fourteen spans, fourteen matches, under whitespace/curly-quote normalisation).
- `planning/domains/nodes/creative.json` — the schema anchor, and the file this row is *measured
  against*: its `template.why` holds the creative DEFAULT TEMPLATE as prose, its `recognition` the
  ten default signals, its `sensitivity_why` the four default privacy reasons. All three legs of my
  node test are argued against those.
- `planning/domains/nodes/creative.exhibition.json` + `.research.md` — the one landed row that had
  already argued a boundary against me (found by `grep -rl "printmaking" planning/domains/nodes/`).
- `planning/domains/nodes/finance.crypto-assets.research.md` — read once, as depth calibration.
- `planning/domains/roster.json` (358 ids, every edge endpoint checked),
  `canonical_fields.json` (no key minted; every `facts_legal` entry script-checked),
  `src/evidence_shape/vocabulary.py` `SOURCE_TYPES`.

**External reality checks.** Printmaking's editioning vocabulary is a real, standardised trade
practice, not something I invented for the row: a numbered impression written as a fraction in the
lower margin; the proof classes that stand *outside* the numbered run (**bon à tirer**, *artist's
proof* / AP, *printer's proof* / PP, *hors commerce* / HC, *épreuve d'artiste* / EV); successive
**states** of a plate; the **chop mark** or blindstamp of the workshop; and **plate cancellation**,
where the matrix is scored or defaced and a cancellation proof is pulled from it to prove the run is
closed. These establish that the documents I list exist and what is inside them. They create no
canonical field, no gazetteer content, no regex and no threshold.

## THE CHARGE — the strongest case that this row should not exist

I wrote this before writing anything else. Six ways to kill it, in descending strength.

**(1) It is a MEDIUM.** "Printmaking, ceramics, textiles, bindings" is a list of materials and
techniques. The brief names a medium as a disqualifier, and the creative anchor already agrees:
`work_types` are values, and technique words are values of a technique. *Etching*, *screenprint*,
*stoneware*, *indigo* would be exactly the kind of enum the 574 mistook for a filing world.

**(2) It is defined by an ABSENCE.** The roster's own hint says it: "the files are only ever
documentation of it." That is a row whose distinguishing evidence is *the missing digital original*.
A detector built on that fires on every scan, every download and every photograph in the corpus. The
brief names "a row defined only by the ABSENCE of something" as a disqualifier, and this hint is the
purest instance of it I have seen in the family.

**(3) It duplicates its own schema's default template.** `creative.json`'s `work_types` already
contains **"documentation of a physical work"**, **"specimen"**, **"proof"** and **"master"**. If
those are the row's contribution, the row *is* four enum values.

**(4) It duplicates neighbours.** A finished print photographed is `career.portfolio-work-samples`.
A print in a show is `creative.exhibition`. A print pulled at a press is
`creative.print-production`. A flat shot with EXIF is `photos`. A folder of `_v1.._v3` files is
`creative.revision-round`. What is left?

**(5) It is a lifecycle stage.** "Editioning" is the stage after the work is made and before it is
sold — a phase of `creative.self-initiated-work`, addressable as a `stage` value.

**(6) The dimensions leg is unavailable to it.** The creative schema declares no fields, so
`dimension_order` is empty by contract for all 41 siblings. One of the three legs of the node test
cannot be used. A row that then also fails on signals or privacy has nothing left.

**(2), (3) and (5) are correct about part of the row, and I concede them rather than argue them
away.** The kiln log, the dye lot sheet and the one-off bound book are killed by (2) and are routed
out of the node in the JSON — `Kiln log 2026-02 - cone 6 oxidation - mug batch.csv` is carried as a
file example precisely so the narrowing is enforceable rather than asserted, and
`the ABSENCE OF A WORKING FILE IS NOT EVIDENCE OF A PHYSICAL PRACTICE` is written as a
`never_alone` rule so the row cannot later drift back.

**What defeats (1), (3), (4) and (6) is one structure the default template does not have and gets
actively wrong: the CLOSED ENUMERATED SET.**

## The node test, argued in full

### Leg 1 — detection signals differ from the creative default. PASSES, and this is decisive.

The creative anchor's default deterministic signals are, in its own words, a LINKED-ASSET
structure, a LAYER or ARTBOARD structure, a REVISION-ROUND structure, a BRIEF structure, a DELIVERY
or HANDOFF structure, PRODUCTION-PAPERWORK, a SCRIPT structure, a TIMELINE-and-MEDIA structure, an
INDEXED-BUT-UNREADABLE state, and a RELEASE or RIGHTS structure.

The default's third signal is the one that matters. The anchor defines it as "a version-shaped token
in the filename occurring across a run of same-stem files … together with a same-stem export," and
grounds it in `00`'s universal `duplicate and version-family signals`.

An edition presents the *same surface evidence* — a run of same-stem siblings each carrying a
numeric token — and means the **opposite thing**:

| | version family | enumerated edition |
|---|---|---|
| relation between members | ordered, **superseding** — v3 replaces v2 | **coequal** — 12/30 does not replace 11/30 |
| how many exist at the end | one that matters | thirty, in thirty different rooms |
| numeric token | monotonic, open-ended | fraction with a **constant denominator** over a **closed** numerator set |
| members outside the sequence | none | BAT, AP 1/6…6/6, PP, HC — designated, not numbered |
| terminal document | none | **cancellation** of the matrix |

Inheriting the default here does not merely under-serve the material; it produces a **wrong answer
about physical objects** — it collapses thirty separately-owned things into one family and offers to
surface the latest. That is the strongest form a template row's justification can take, and it is
why the row survives (1), (3) and (4): technique words are indeed values, but *enumeration is not a
value, it is a structure*, and no other creative sibling has it.

Three further signals are new rather than merely differing, each named in the JSON:

- **DISPOSITION-PER-COPY** — a table whose *row unit is one physical object* (number, date pulled,
  paper, condition, where it is now, who holds it), under a heading naming **one** work. Every other
  creative row's unit is the work, the round or the delivery set. Marked inference: `00` requires
  structured extraction from spreadsheets but does not name this table shape.
- **MATRIX-STATE** — state designations across scans of the same image beside a matrix noun. States
  are a history of the *tool*; the earlier state is a separately collectible object, not a draft.
- **CANCELLATION** — the only document in the whole creative schema whose meaning is that the work
  *can never be produced again*.

### Leg 2 — recommended dimensions. UNAVAILABLE, and I say so rather than fake a pass.

`creative.json` declares no fields, so `dimension_order` must be `[]` for this row and for all 41
siblings — the anchor's own open_question 4 says exactly this: the dimensions leg "is unavailable to
all of them equally." **This row does not claim this leg.** It records a prose recommendation for
R1c instead, with one arguable difference from the default: **drop `stage`**. The default order is
`client` (only where genuinely multi-client) → `project` → `stage` → `artifact_type`. `stage`
describes a work moving through revisions toward delivery. An edition does not pass through stages;
it passes through **one-way terminal events** — matrix worked, one proof approved, run pulled,
matrix cancelled — after which nothing further can exist. A `stage` level opens branches that are
empty during the work and permanently empty after it. Dropping `client` is *not* claimed as a
difference: the default already drops it where there is no multi-client corpus.

The parent-context test still fixes the order: `00` — "a parent dimension should provide the context
required to understand the child" — and `12/30` is meaningless without the work, exactly as Homework
3 is meaningless without the course. `time_first: false`; this material is not capture-based and may
not claim the photos exception the anchor grants by name to `creative.shoot-day-media` and
`creative.raw-photo-catalogue`.

### Leg 3 — privacy rules differ in KIND. PASSES.

The creative default's first protection reason is **unpublished work**: "A campaign before launch, a
manuscript before submission, an identity before reveal and a cut before release are confidential by
default." That protection is **temporal — it expires on release.**

An impression register inverts it. The edition is published, hung, sold — and the register becomes
**more** sensitive afterwards, not less, because it is the document that says *who owns each object
and where each one physically is*. A template that inherited the default unchanged would relax
exactly at the moment the material most needs holding. Second, and separately: edition size, proof
count and the cancellation record are the **authenticity instrument**. Corrupting or exposing them
damages every impression already sold and every person holding one — third parties who never touched
this corpus. `00`'s operative boundary applies to both: "Paths, complete extracted text, OCR output,
file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain
local," against "Privacy policy must be enforced before content reaches any model or external
connector."

`sensitivity: potentially_sensitive`. No `is_safety_domain`, no handling class (P7's vocabulary).

**Two legs of three, with the third honestly forfeited.** CONNECTION's test requires *a* difference,
not all three, and the difference on leg 1 is not a nuance — it is the default producing an
incorrect grouping.

## Files considered and REJECTED

Naming what is *not* mine was the more useful half of this pass.

- **`Kiln log 2026-02 - cone 6 oxidation - mug batch.csv`** — kept in the JSON as a file example
  with `group_without_copying_facts: true` and a fallthrough to Independent Records, *specifically
  so the narrowing is enforced by a fixture rather than by prose*. Twenty-four mugs are a batch of
  interchangeable objects. No enumeration, no designations, no cancellation, no per-copy
  disposition. This is the roster hint's "physical craft," and it does not activate.
- **A one-off hand-bound book, a single thrown pot, a woven length.** Same reason, no fixture
  needed: their only distinguishing evidence is the absence of a digital original.
- **A studio supplies invoice (paper, copper, ink, clay).** A purchase. Receipts and Confirmations,
  or `finance.small-business-bookkeeping`. Naming a matrix material is not evidence of an edition.
- **A technique tutorial PDF or a saved auction listing for someone else's print.** Reference Clips
  — `00`'s "does not belong to a current project" is the exact test.
- **An artist's CV whose exhibitions and editions lines are prose.** `career`. It is the strongest
  false positive this row will ever see and is written into the `career` collision as a refusal.
- **A gallery price list for a group show.** `creative.exhibition` — many works, one venue.
- **An NFT / numbered digital issuance.** Borrowed vocabulary, no physical object, no matrix, no
  cancellation. Carried as a `needs_llm` line rather than a fixture; `finance.crypto-assets` already
  owns that material and adding it here would give one evidence item a third home.
- **A `.psd` scan-retouch working file for a documentation shot.** The creative default's
  linked-asset and layer signals already explain it; nothing here is added by claiming it.

## The collision fixture

**`Print Run Order Confirmation - 500 A2 posters - Ashgrove Press.pdf`.** It has a print workshop's
letterhead, paper stock, a colour spec, the word **proof**, the word **run**, and a token reading
**3/4**. Every lexical cue this row cares about is present.

It is not my evidence, and four things discriminate it:

1. **500 is a quantity beside a unit price**, not a denominator repeated down a column of
   individually addressable rows. Fungible copies, not an enumerated set.
2. **`3/4` is a date fragment** — the proof-approval date — not an impression number. This is why
   `A FRACTION-SHAPED TOKEN ALONE` is a `never_alone` rule and why the rule demands a *constant
   denominator across a run*.
3. **"Proof" here is a prepress approval**, not a bon à tirer standing outside a numbered run.
4. **There is no cancellation and no signature block.** The run is open; more can always be printed.

It falls through to Receipts and Confirmations, and its domain home, if any, is
`creative.print-production`.

A second, subtler one is carried too: **`Riso zine - ink layers - v3 FINAL.ai`**, which names a
physical printing technique in its layer names and is nonetheless the *creative default's* file —
linked assets, layers, a version family, no register.

## Reciprocal boundaries, both directions, same fixture on both sides

- **`creative.print-production`** — fixture: the poster order above. *Print-production owns runs of
  interchangeable copies specified by quantity, stock and colour spec, approved by a prepress proof,
  closed by a delivery. This row owns closed enumerated sets, approved by a bon à tirer, closed by a
  cancellation.* Reciprocal: this row must not claim a job merely because a physical technique is
  named; print-production must not claim an edition merely because a press pulled it.
- **`creative.exhibition`** — fixture, *named identically on both sides*: a checklist row reading
  `Untitled, 2025, screenprint, edition 12/40`. Exhibition's landed file already states it —
  "editions must not claim a checklist merely because a row carries an edition fraction, and this
  row must not claim an edition register merely because one impression was hung." My side
  reciprocates in the same terms. The tell is the **row unit**: many works and one venue is
  exhibition; one work and many objects is this.
- **`creative.revision-round`** — fixture: a run of same-stem siblings carrying numeric tokens.
  *Revision-round must not read an impression list as a version family and propose a latest; this
  row must not read `_v1.._v3` as an edition of three.* The discriminator is the constant
  denominator plus designations standing outside the sequence.
- **`career.portfolio-work-samples`** — fixture, same bytes both sides:
  `Tidal Flat - documentation - flat shot - colour checker.tif`. *Career must not claim a
  documentation set because its images are impressive; this row must never claim a CV or a portfolio
  PDF.* Where a lone flat shot has neither register nor curation, `00`: "Correct abstention is a
  successful outcome…"
- **`photos.camera-events`** — fixture, same bytes both sides: the four flat shots and `IMG_2287.jpg`.
  The captures carry the same EXIF a family photograph carries, and that alone would propose a
  capture-year home for an object *whose own date is not the photograph's* — the print was pulled in
  March and shot in June. *Photos must not lose a studio snapshot because sheets are depicted; this
  row must not claim a capture event.* `IMG_2287.jpg` is where the correct outcome is that **neither**
  fires.
- **`code.software-project`** — fixture: a plotter/generative edition whose repository generates the
  images. *Code must not claim the edition register because a script produced the images; this row
  must not propose re-filing anything inside a preserved repository root.* The register normally
  sits outside it.
- **`finance.small-business-bookkeeping`** — fixture: the edition record's `Held by` and `Price`
  columns. *Bookkeeping must not claim the register because it carries prices; this row must not
  claim an invoice or a period summary because it lists works.* The **row unit** decides — object vs
  transaction — and where one spreadsheet genuinely does both, the honest answer is two groups over
  one file.

## Neighbours considered that did NOT get an edge

- **`creative.licensing-rights`** — a reproduction licence for an editioned image is real, but it is
  a *grant*, and the anchor's open_question 2 already records that no canonical key holds a usage
  grant. Adding an edge would relitigate the schema's hole from a template row.
- **`creative.self-initiated-work`** — the tempting parent. Refused as an edge because the
  relationship is browse-only, not evidential: no fixture is contested. The unenumerated-craft
  coverage I route out lands *there* or in a residual, and I say so in open_question 1 rather than
  drawing a collision I cannot ground in shared bytes.
- **`legal.leases-agreements` / `legal`** — the consignment agreement is genuinely double-reading,
  but `also_holds_with` is a **schema-only** edge (`_CONTRACT` rule 14) and the creative schema
  already declares `legal`. So `also_holds_with` is `[]` here, matching the landed
  `creative.exhibition`, and the double reading is expressed where a template may express it:
  `also_schema: "legal"` on `Consignment - Harlow Editions - Spring 2026 - signed.pdf`, and
  `also_schema: "photos"` on the flat shot. Both values are on the schema's declared list.
- **`photos.scanned-documents`** — a margin scan is a scan, but scanned-documents is about
  *documents*; a print is not a document and the discriminating evidence never collides.
- **`business_operations.*`** — an atelier's own operations are real, but the register is not an
  operational record and no fixture is contested that `finance.small-business-bookkeeping` does not
  already cover.

## `proposed_fields` — empty, deliberately

`fields: []` because `_CONTRACT` rule 12 forbids a template copying its schema's list, and because
the creative schema declares none at all. `proposed_fields: []` is the harder choice and the correct
one: **the impression number is not proposed as a key.** It is the most distinctive string this
world has and the row's entire detection signal, which is exactly what makes minting it the 574's
mistake at the point of maximum temptation. Even if minted it must never be a folder level — a
directory per impression scatters one edition across thirty branches, which is the opposite of what
the register is for. The same refusal covers **edition size**, **price**, **paper** and
**technique**; the last is a value, per the anchor.

`proposed_context_terms` (seventeen) are candidates for R6, marked PROPOSED. `00` states the
pattern-plus-context *shape* for course codes only; it does not list these.

## `never_alone` — each rule trips a real fixture in my own list

Eleven rules, written so that every one is falsifiable against the file examples: a
fraction-shaped token alone (trips the poster order's `3/4`), the word *edition* alone (trips the
Instagram screenshot), the proof abbreviations alone (AP is Accounts Payable and Advanced
Placement; BAT is an animal), a technique word alone (trips the riso zine), a photograph of a
physical object alone (trips the flat shot), **the absence of a working file** (kills the roster
hint's own framing), an organisation name alone, a bare four-digit number, an extension alone, a
signature in an image, and a quantity beside a unit price.

## Sparse-file discipline

`IMG_2287.jpg` is the `HW 3.pdf` of this node: a phone photo of a drying rack, sitting in the folder
with the register and the documentation set, with nothing legible in frame.
`group_without_copying_facts: true`, `facts_legal` is universals only, and its `must_not_conclude`
covers both halves — the graph does not copy the register's impression number onto it, and missing
EXIF is not proof of a screenshot. `Kiln log …csv` carries the same flag for a different reason: it
belongs to the studio neighbourhood without belonging to an edition.

## Audits run before returning

- `python3 -m json.tool` — parses.
- All fourteen quoted spans of 25+ characters extracted from the JSON and matched against `00` under
  whitespace/curly-quote normalisation: **14/14 verbatim.** No fabricated quote.
- Every `source_type` is in the fourteen-member `SOURCE_TYPES` list (13/13 fixtures, 9/9 file_kinds).
- Every `facts_legal` entry is a `canonical_fields.json` key. **One correction made:** the flat shot
  and `IMG_2287.jpg` initially carried `capture_date`, which does not exist; the canonical key is
  `capture_year`, and both were changed.
- Every `collides_with.domain_id` (7/7) and the one `role_split.other_domain` resolve to roster ids.
  Every residual name (7/7 + 13/13) is one of §7.3's nine.
- `also_holds_with: []` by contract; both `also_schema` values are on the schema row's declared list.
- No threshold, score, confidence or evidence count. No handling class; `sensitivity` is
  `potentially_sensitive` only.
- Only the two assigned files were written; `29-DOMAIN-OWNERSHIP.md`, the roster,
  `canonical_fields.json`, `check.py`, `src/` and every neighbour node untouched.

## NEEDS-JOSEPH (this node only)

- **NJ-PRINT-1 — the roster name is wider than the defensible row.** The roster calls it
  "Printmaking, editions and physical craft" and hints at "prints, ceramics, textiles, bindings."
  Research finds one node inside that: the closed enumerated set and its register. The rest has no
  enumeration, no per-copy disposition, no proofs and no cancellation, and its only distinguishing
  evidence is the **absence** of a digital original — never-alone evidence that cannot activate
  anything. Alternatives: **(a)** rename to *editions and impression registers*, routing
  unenumerated craft to `creative.self-initiated-work` and Independent Records — recommended, and
  already enforced by this row's fixtures and `never_alone` rules; **(b)** keep the wide name and
  accept that half the coverage never activates, which is the 574's failure written into a launch
  row; **(c)** split into an editions row and a studio-practice row, which needs a real filesystem
  to justify and would produce a second row defined by absence. **Not acted on — the roster is not
  this agent's to edit.** Recommendation to R1c.
- **NJ-PRINT-2 — no canonical key holds an impression number, and none is proposed.** The row is
  detected by a string it may not record. Alternatives: leave it unmodelled (current — the string
  stays evidence and never a fact); mint an impression key and fence it as
  destination-**ineligible**; or mint it destination-eligible, which scatters one edition across
  thirty branches and is rejected here. The same question covers edition size, price and paper. This
  parallels the creative schema's own rights-and-licence hole (anchor open_question 2) and is
  recorded for R1c as this row's one genuinely field-shaped hole.
- **NJ-PRINT-3 — no canonical key holds a collector or owner role.** The register's `Held by` column
  names private individuals who are neither clients, nor authors, nor the corpus owner, so the
  `role_split` in this node covers the maker side (`client` / `our_firm`) only. Alternatives: leave
  it unmodelled (current — the names stay in `must_not_conclude` and drive the sensitivity posture);
  overload `client` with a purchaser meaning it was not defined to carry; or mint an owner key on
  the shared vocabulary, a decision about the product's field table that one template row must not
  make. This is also the reason `Protected Records` appears in `falls_through_to`.
- **NJ-PRINT-4 — the edition register vs the sales ledger is one file with two row units.** Real
  studios keep a single spreadsheet that is simultaneously the impression register and the sales
  record. This node's answer is two groups over one file, decided by row unit. If R1c prefers one
  home, it must choose between `finance.small-business-bookkeeping` and this row, and the choice
  changes which columns are protected. Stated reciprocally in `collides_with`, not silently guessed.
