# Research memo — `retail_hospitality.store-operations`

Depth: J-DEPTH
Date: 2026-08-27
Kind: template on the fieldless `retail_hospitality` schema · `parent_id: null` · `launch: placeholder`
Output: `planning/domains/nodes/retail_hospitality.store-operations.json`

## Result

**Accept, narrowly, and only after refusing the roster hint's widest reading.** The hint bundles
rotas, opening and closing checks, standards audits, maintenance and "the compliance paperwork the
site must hold." Taken literally that is five homes wearing one name, and I would have refused it.
What survives is one occasion the parent schema's default does not enumerate: **the site operating
day** — labour capacity planned against forecast trade, the open/close diary of the selling space,
the shift handover of trading-floor state, and a brand or mystery-shopper walk of that space. Durable
licence packs, food-temperature diaries, till closes, facilities maintenance calendars and company
handbooks are neighbours' evidence, not this row's definition.

## Sources actually read

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (in full).
- The stamped assignment from `make_prompt.py retail_hospitality.store-operations`.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — one landed launch row, for depth
  calibration only.
- `planning/domains/nodes/retail_hospitality.json` — schema anchor only (per dispatch economy). This is
  the document the node test is measured against.
- Targeted `grep -c` verification of every `00` span quoted below against
  `planning/00-database-agent-product-design.md`. Every quoted span returned exactly one match.
- Neighbour edges that already name this id, read only at those entries:
  `business_operations.facilities-workplace.json` (collision toward this id),
  `retail_hospitality.pos-reporting.json` (site-pack collision authored one-way toward this id).
- `planning/domains/roster.json` — every neighbour id in my edges confirmed present as a `domain_id`.

## THE CHARGE — the strongest case that this row should not exist

Six charges. Five are serious.

**1. It is the schema's default template wearing a name.** The schema's one-liner is the operator's
trading record from a site. "Running a shop day to day" is that sentence restated. CONNECTION §2 and
ALIGNMENT both refuse a template that only repeats its schema's default.

**2. It is a work_type value of the schema's own list.** The anchor's `work_types[]` already names
`"site operating record - rota against forecast trade, opening and closing checks, standards audit,
reactive maintenance call, the compliance pack the site must hold"` almost word for word with the
roster hint. The schema's never-alone rule says a document-type word is *"a value of a function
dimension, and a row resting on one is the schema's default template wearing a name."*

**3. It is a bag of leftovers defined by absence.** After catalogue, stocktake, supplier-order,
pos-reporting, ecommerce, returns, menu, food-safety, premises-licensing, events, bookings, catering
and guest-feedback take their structures, this row would be "everything else about the shop." That is
the `business_operations.organisational-records` refusal pattern.

**4. Every artefact already has a home.** Rotas → `hr`. Opening/closing and cleaning →
`retail_hospitality.food-safety` or `business_operations.facilities-workplace`. Standards audits →
`business_operations.compliance-audit`. Maintenance → facilities. Compliance paperwork →
`retail_hospitality.premises-licensing`. If each neighbour takes its half, is there a remainder?

**5. It is five rows wearing one name** — labour plan, open/close diary, brand visit, reactive call,
durable compliance pack — with three different time shapes (day, visit, multi-year).

**6.** (Weak.) It is a medium or format. It is not: fixtures span spreadsheet, text, email, image,
ocr, archive and audio_video.

## Defeating the charge

### Against charges 1 and 2 — the occasion, not the function

The schema default, held as prose because PR-6 leaves it fieldless, is: TRADING UNIT where the corpus
spans more than one, then TRADING OCCASION — *"the session, count, order cycle, booking, function or
licensed premises the material belongs to"* — then OPERATIONAL RECORD FUNCTION.

That sentence enumerates five occasion shapes. **A site operating day is none of them**, and it
differs from all five:

- A **session** is a till close — `retail_hospitality.pos-reporting` already landed on that and forbade
  this row from taking loose Z-reads.
- A **count** is a stocktake.
- An **order cycle** is supplier replenishment.
- A **booking** or **function** is capacity sold to a guest.
- A **licensed premises** is the permission file — `retail_hospitality.premises-licensing`.

The site operating day is bounded by **open and close of the selling space**, centres on **labour
capacity planned against forecast trade**, and assembles the operative diary of the floor. That is an
occasion-level difference, not a function-level one. Charges 1 and 2 fail once the row is narrowed to
that occasion. They would succeed if I kept the hint's "compliance paperwork the site must hold" as a
defining structure — which is why NJ-SO-2 refuses that widening.

### Against charge 3 — defined by a presence

The row is not "files no sibling wanted." It is the presence of labour-against-forecast, trading-floor
open/close vocabulary, shift-handover of trading state, and brand-standards visit structure. A day
that produces all four and none of a Z-read, a temp log or a licence grant is still squarely this row.
Charge 3 fails for the narrowed reading.

### Against charge 4 — neighbours already drew the remainder

Two landed neighbours argued my side before I wrote:

- `business_operations.facilities-workplace` already collides toward
  `retail_hospitality.store-operations` and states that a trading premises' opening checks support the
  **sector row** when a trading or guest-facing anchor is present. If I refused, that seam would dump
  trading-floor diaries into facilities against the neighbour's own words.
- `retail_hospitality.pos-reporting` already authored a SAME FIXTURE collision on
  `Camden - March site pack.pdf`: it owns the closes; **this row owns the pack as an assembly**. I
  match that wording rather than invent a second seam.

The food-safety / premises-licensing / compliance-audit / hr remainders are argued in `collides_with`
with named fixtures. Four independent lines around the same remainder is evidence the remainder is a
real object.

### Against charge 5 — one structure, tested; one limb refused

Labour plan, open/close diary, handover and brand visit all instantiate **one dated site day at one
selling space**. The reactive same-day call is a member of that day, not a second row. The durable
compliance pack is **refused as a defining limb** (NJ-SO-2): it is premises-licensing / food-safety /
Independent Records material that may sit *inside* a site pack as a contained neighbour, exactly as
Z-reads sit inside the pack without becoming store-operations. Charge 5 fails for the narrowed set
and is recorded honestly for the limb I cut.

## The three legs of the node test

CONNECTION §2 — a template exists only where detection signals, recommended dimensions, or privacy
rules differ from its schema's default.

**Leg 1 — detection signals: PASS.** The schema lists ten deterministic structures. None is
labour-against-forecast. The nearest relatives are daily-signed-check (food-safety diary vocabulary)
and capacity-against-dated-demand (guest bookings). Labour-against-forecast pairs staff hours with a
**trade forecast column**; trading-floor open/close pairs initials with **float/till/alarm/visual-merch
acts**; brand visit pairs a store with a **mystery-shopper or regional scorecard without a PBC chain**.
Those three signals are false of the schema default and false of every landed sibling.

**Leg 2 — recommended dimensions: PASS, at the occasion level.** `dimension_order` is `[]` by
contract. The prose difference inserts SITE OPERATING DAY where the parent lists session / count /
order / booking / function / licence. Not time-first: *"For document and record domains, project,
function, or subject usually comes before time because putting year first scatters related work across
calendar folders."* The trading date identifies the day; it does not root the tree.

**Leg 3 — privacy rules: PASS, with a named delta.** The parent's posture rests on volume of guest
data. This row's ordinary output is **staff-facing first** — named labour plans, duty-manager
handovers, allegation-adjacent till-exception mentions — and only secondarily guest-affecting. That
is closer to `pos-reporting`'s inversion than to `guest-feedback`, and it is why the sensitivity
statement cannot simply copy the parent. CCTV remains unsettled (NJ-SO-4) and the file example routes
a lone CCTV export to Protected Records rather than claiming it.

Three legs pass. The row stands — narrowly.

## Files considered and rejected

1. **`Week 12 rota.xlsx` (bare)** — the parent's NJ-RH-1 fixture. Names, days, hours; no forecast
   column and no hr columns. Undecidable. In `file_examples` as "THIS ROW DOES NOT ACTIVATE" and
   falls to Review Later. This is the collision fixture against `hr`.
2. **`Fridge temps March.jpg`** — the parent's own daily-signed-check example. Probe vocabulary.
   `retail_hospitality.food-safety`'s. Must not be stolen because both sheets are titled "checks."
3. **`EOD 2026-03-14 Till 2 - Camden.pdf`** — a Z-read. `retail_hospitality.pos-reporting`'s. The
   site-pack seam forbids taking loose closes because packs sometimes contain them.
4. **`Premises licence 12345 - conditions.pdf`** — permission-to-trade. The hint's "compliance
   paperwork" temptation. `retail_hospitality.premises-licensing`'s.
5. **`Employee Handbook v4.2.pdf`** — company governance. The parent's existential seam against
   `business_operations`. Not a site day.
6. **`Franchise ops manual - opening procedure.pdf`** — specimen / training blank. Purpose is
   instruction, not contemporaneous evidence. *"Topic answers what a file is about, while purpose
   answers what the file was for."*
7. **`Unit 4 - opening checks March.pdf`** — property-interest adjacency. Without trading-floor
   vocabulary it is construction_property / facilities, not this row.
8. **`Store 214 CCTV export - 14 Mar evening.mp4`** — highest-risk bytes, no accompanying site-day
   structure. Filename must not manufacture activation (NJ-SO-4). Protected Records.
9. **A year-long fridge maintenance contract** — facilities' planned calendar for the same appliance
   this row may call about mid-service.
10. **A hygiene cleaning schedule with probe rows** — food-safety, even when signed at opening time.

## The collision fixture

**`Week 12 rota.xlsx`.** On filename and first page it is indistinguishable from this row's strongest
positive example (`Week 12 rota - Camden - forecast covers.xlsx`). Both have names, days and hours.

**What discriminates it:** the forecast-trade column is absent. Without sales-per-labour-hour,
labour-percentage or forecast covers, the sheet is not a trading capacity plan; without contracted
hours, absence codes or pay rates, it is not clearly hr's either. The honest outcome is abstention
and Review Later — not a quiet win for either row. This is exactly the undecidable the parent schema
recorded as NJ-RH-1, and this template inherits it as NJ-SO-1 rather than pretending to settle it.

Secondary collision fixtures: `Fridge temps March.jpg` (food-safety), `EOD 2026-03-14 Till 2 -
Camden.pdf` (pos-reporting), `Premises licence 12345 - conditions.pdf` (premises-licensing),
`Franchise ops manual - opening procedure.pdf` (specimen).

## Reciprocal boundaries

Eight `collides_with` entries, every one an object with `domain` + `signal` + `provenance`, every
signal using the SAME FIXTURE BOTH SIDES construction and a named discriminator.

**Already agreed (match neighbour wording):**

- `retail_hospitality.pos-reporting` — fixture `Camden - March site pack.pdf`; discriminator close
  versus pack-as-assembly.
- `business_operations.facilities-workplace` — fixtures open/close checklist and same-day fridge-failure
  email; discriminator trading-floor diary / same-day call versus multi-month premises administration.

**Authored one-way here; R1c owes reciprocals:**

- `hr` — fixture `Week 12 rota.xlsx`; discriminator forecast-trade column (NJ-SO-1).
- `business_operations.compliance-audit` — fixture mystery-shopper scorecard; discriminator PBC /
  control-framework chain versus brand-ops score.
- `retail_hospitality.food-safety` — fixture fridge-temps sheet; discriminator check vocabulary
  (neighbour not yet landed).
- `retail_hospitality.premises-licensing` — fixture premises licence conditions; discriminator grant
  versus site-day diary (neighbour not yet landed).
- `construction_property` — fixture `Unit 4 - opening checks March.pdf`; discriminator trading-floor
  vocabulary versus property-interest apparatus.
- `business_operations` — fixture employee handbook; discriminator site-day structure versus company
  governance.

`also_holds_with` is **empty**. Per handoff / CONNECTION it is schema↔schema only and this row is a
template. Intent for R1c: the parent schema already authors `retail_hospitality` ↔ `hr` and ↔
`business_operations` co-holds on disjoint evidence inside a site pack; I found the same joins from
below and do not re-author them on a template.

`role_split` is empty. The schema already carries operator/guest; staff-versus-operating-business on
a rota is expressed as the `hr` collision and NJ-SO-1, not as a decorative split with no keys.

## Fields

`fields: []` and **`proposed_fields: []`**. Deliberate. The schema owns field proposals (`site`,
`trading_occasion`, `record_period`, `product`). This row asks R1c to **widen** `trading_occasion` to
admit SITE OPERATING DAY as a sixth shape (NJ-SO-5), not to mint `operating_day`, `shift`, `rota_week`
or `store_day`.

Rejected as values, not keys: check-type (open/close/standards), visit-score, labour-percentage.
Branching a tree on those would be a function-level split under an occasion that already exists.

## Open questions — NEEDS-JOSEPH

All five are in the node's `open_question` in full:

- **NJ-SO-1** — bare rota undecidable with `hr` (inherits NJ-RH-1). *Alternatives:* forecast-trade
  column discriminator (this pass); or hr takes every rota.
- **NJ-SO-2** — does "compliance paperwork the site must hold" survive inside this row? *Alternatives:*
  refuse as defining structure (this pass); or admit durable packs as members.
- **NJ-SO-3** — mystery shopper versus compliance-audit. *Alternatives:* keep brand/regulatory split
  (this pass); fold into compliance-audit and narrow further.
- **NJ-SO-4** — CCTV / door-access (inherits NJ-RH-4). *Alternatives:* admit when paired with a
  site-day pack; Protected Records only (file-example posture); or a future security world.
- **NJ-SO-5** — widen `trading_occasion` for site operating day, or leave prose-only until fields
  exist?

## Recommendations for R1c (not applied — edited only my two files)

1. Add reciprocals on `hr`, `business_operations.compliance-audit`, `retail_hospitality.food-safety`,
   `retail_hospitality.premises-licensing`, `construction_property` and `business_operations` using the
   fixtures named above.
2. Confirm NJ-SO-2 before any later pass re-expands this row into a compliance-pack residual.
3. When ruling `trading_occasion`, rule on site operating day together with the shapes returns-warranty
   and the anchor already worried about — one adjudication, not three.

## Self-verification

- `python3 -m json.tool` on the node: **parses** (run at return).
- Every `00` span in either file grep-verified: single match each; no paraphrases inside quote marks.
- Every `collides_with` / neighbour id confirmed in `roster.json`.
- Every `falls_through_to` name is one of 00's nine residual homes.
- Every `file_examples.source_type` is in `SOURCE_TYPES`.
- Every edge is an object with SAME FIXTURE BOTH SIDES construction; no bare strings.
- `also_holds_with: []` — schema↔schema only.
- `fields: []`, `proposed_fields: []`.
- No threshold numbers, no handling classes, no invented catalogue contents, no regexes.
- Files written: exactly `planning/domains/nodes/retail_hospitality.store-operations.json` and this
  memo. Nothing else touched. No commit.
