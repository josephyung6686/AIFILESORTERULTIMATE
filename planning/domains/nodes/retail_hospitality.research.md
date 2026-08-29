# `retail_hospitality` — lab notes (schema anchor, J-DEPTH)

**Row:** `retail_hospitality`, `kind: schema`, `launch: placeholder`, `fields: []`, `refuse_node: false`.
**Written from nothing:** neither file existed. There was no draft to salvage.
**Charge answered:** *this may be `business_operations` with a shopfront.* It is not, and the argument
is below in full, before anything else. **The row would have been refused if it were.**

This is a **schema anchor carrying fourteen templates**. Every one of them measures its node test
against the default template stated here. Modelled on the landed J-DEPTH anchors, and closest of all
on `business_operations.research.md` (46KB), whose never-alone principle this memo inherits, extends,
and does not restate where it already holds.

---

## The charge, answered first

> A shop and a restaurant have suppliers, staff, premises, accounts, marketing and compliance exactly
> as any company does — and if that is all this family holds, most of its templates are duplicates and
> the honest outcome is a narrow schema or a refusal. **Trading in a sector is a field value, not a
> structure.**

**Accepted without qualification.** The premise is correct, and this row adopts it as its first
family-wide principle rather than arguing with it. A hospitality operator's board minutes are
`business_operations.meeting-record`. Its budget is `budget-forecast`. Its staff handbook is
`policy-handbook`. Its EPOS terminals are `it-asset-inventory`. Its supplier agreement is
`contract-administration`. Its ISO pack is `compliance-audit`. Its confirmation statement is
`corporate-regulatory-filings`. **None of that is this family's, and this row's `collides_with` entry
for `business_operations` says so in those words.**

`business_operations.organisational-records` was read in full, including the four-answer two-role
closure in its JSON. Its refusal turned on a row *defined by subtraction* — "carries an organisation
and a document type but no more specific operational sub-domain" — and it observed that **a negative
definition cannot own a positive structure.** The test this row therefore had to pass is the exact
inverse: **name positive structures, each pairing a structure with a labelled slot, that the
twenty-five landed `business_operations` rows do not hold.**

Five were found. Each is stated as a structure, not a topic, and each survives the deletion test the
refusal proposed: *delete every entity name, every trade name, and every document-type word, and see
whether anything is left.*

### 1. Counted money against recorded money — the till reconciliation

A Z-read or end-of-day: for **one trading date and one identified till**, a takings figure **broken
out by tender** (cash, card, voucher, account), a **declared or banked cash** figure against an
**expected** figure, an **over/short** line, and void / no-sale / refund / discount counts.

`business_operations.budget-forecast` also has a variance. It is not the same variance and the
difference is structural, not topical: that row compares **forecast against actual over line items
and fiscal periods**; this compares **money physically counted in a drawer against money the system
believed**, keyed to a till and a session. Delete every name and word — the paired tender columns and
the over/short line remain, and they are meaningless anywhere else in the roster.

### 2. Counted stock against book stock

One row per stock line, **Counted qty** paired against **System qty**, with variance quantity *and
variance value*, scoped to a location and a count date; usually with wastage, shrinkage or spoilage
columns.

`business_operations.it-asset-inventory` is the tempting relative and it is a genuinely different
shape: one row per **unique serialised asset** with lifecycle dates, **no count-versus-book pair**,
and nothing perishable. The count-against-book pair for **fungible, recounted, perishable** goods
appears nowhere in that family, and wastage appears nowhere in the roster at all.

### 3. Finite capacity against dated demand

A party size, cover count, pax, room-nights, seat or table allocation, or ticket count, bound to a
**date and a time window**, with a status slot (confirmed / provisional / cancelled / no-show) and a
requirements slot.

The false friend is a calendar entry. `00` says of ICS that it "should yield event title, start and
end time, location, organizer, attendees, and recurrence metadata" — attendees, but **no counted
quantity against a capacity**. `business_operations.meeting-record` has bodies and dates; it has no
covers. This is the hospitality invariant and it is why bookings, events, catering and store
operations are one family rather than four strays.

### 4. A permission keyed to a *place*, not an *entity*

A premises licence: a **premises address** as the key, a schedule of **licensable activities each with
its own permitted hours**, a conditions annex, and a named responsible individual in a labelled role
slot (premises supervisor, food business operator).

`business_operations.corporate-regulatory-filings` is keyed to an **entity identifier and a period**
and is made by the entity **about itself**. A premises licence is granted to **whoever operates that
place**, transfers with the operation, and — decisively — **can be objected to, reviewed and varied by
third parties**, which no confirmation statement can be. That asymmetry is structural.

### 5. The operative's own contemporaneous signed diary

A recurring schedule of checks with, per row, a date, a reading or tick, a **target or tolerance**, a
**corrective-action slot**, and an **initial or signature**, repeated per day, frequently as a
photograph of a paper clipboard sheet.

`business_operations.compliance-audit` is built on an **assessment occurrence** and its
request→evidence→finding→sign-off chain, performed by "a party structurally distinct from the party
assessed". The daily log is **self-recorded** and is the material an audit later **pulls from**. Both
directions are stated in the JSON: this row must not take the audit report or the corrective-action
register; that row must not take the diary.

### What this does *not* prove, said plainly

It does not prove that all fourteen templates survive. It proves the **schema** survives. Three
templates are flagged in `open_question` as at genuine risk — `catering-contract` (NJ-RH-3) most of
all, `event-production` (NJ-RH-2) next — and this memo recommends R1c test them against these five
structures rather than against the sector word. A template that cannot name one of the five, or a
sixth of equal standing, is `business_operations` with a shopfront and should be refused.

---

## Sources actually used

**Binding.** `planning/00-database-agent-product-design.md` (all quotations; every one machine-checked
with `grep -F`/exact substring match before writing — see Audits). `planning/domains/_CONTRACT.md`,
`CONNECTION.md`, `planning/prompts/ALIGNMENT.md`, `planning/domains/canonical_fields.json`,
`planning/domains/roster.json`, `src/evidence_shape/vocabulary.py` (SOURCE_TYPES),
`planning/domains/dispatch/RESEARCH-BRIEF.md`, the stamped assignment.

**Landed neighbours read and not touched.** `business_operations.json` + `.research.md` (anchor, and
the source of the never-alone principle and the not-time-first prohibition);
`business_operations.organisational-records.json` (the refusal, in full, including its two-role
closure); `customer-account-management`, `procurement-sourcing`, `facilities-workplace`,
`compliance-audit`, `it-asset-inventory`, `budget-forecast`, `corporate-regulatory-filings`;
`government.json` (authored 2765f94); `hr.json` (authored 873d553);
`construction_property.commercial-lease.json`, and `construction_property.json`'s `organization`
reuse note; `manufacturing.json` (for `site`, `product`, `batch_lot`);
`finance.payroll-received.json` and `finance.subscriptions-utilities.json` (for `record_period`);
`clinical_practice.patient-chart` (via the refusal's account of it).

**Not read, and the gap is declared.** The `logistics` schema row had not landed. Its seam is
therefore **authored one-way here** and marked `provenance: inference`; R1c owes the reciprocal. The
same is true of the `finance` seam — the landed finance rows do not name this schema — and of
`photos`.

**Evidence discipline.** Every structural claim above is either a quotation, a named real document
type in general trade use (Z-read, goods-received note, function sheet, premises licence, temperature
log, allergen matrix), or an inference explicitly marked as one. No thresholds, statistics or file
counts were invented. No gazetteer contents and no detector regexes were written — `rule_family`
names the *family* of rule, as P4 requires.

---

## Provenance: why this row is `proposal` and its `design_cite` is `null`

`00` does not name retail or hospitality. Its initial-release domain list is explicit — "The initial
release should fully support only the domains required to validate the product on real heterogeneous
corpora: academic coursework, college applications, research and lab work, career and recruiting,
photos and captures, and code projects." This family is not there, and it does not claim to be. It is
licensed instead by the template-library sentence — "The product should eventually maintain a library
of roughly 200–300 domain-specific templates, covering common organizational situations such as
academic programs, university applications, recruiting processes, client engagements, research
workflows, financial records, travel, legal matters, creative projects, software repositories,
personal administration, and photo collections." — which names *organizational situations* as the
unit. That is what the five structures are. `provenance: "proposal"`, `design_cite: null`, and
`launch: "placeholder"` are the honest triple.

---

## The node test, all three legs, each argued

### Leg 1 — a distinct field set

The row proposes **four keys and mints exactly one**, which is itself part of the argument: a family
that had to mint four would be describing a world with no relatives, and a family that could mint none
would be `business_operations`.

- **`site` — REUSE from `manufacturing`.** Same referent shape (one physical operating location inside
  one entity, against which records are keyed); different world. Minting `store` / `venue` / `outlet`
  / `branch` would produce the synonym family the canonical list exists to prevent. **Deliberately not
  `organization`:** that key answers *whose record this is* and is seeded ineligible as a destination
  because in a single-entity corpus it names the holder's own business above everything, which is two
  validator failures at once. A trading corpus genuinely spans several sites and channels under one
  entity — **that is why `site` is eligible where `organization` is not**, and it is a real
  field-level difference from the parent family, not a rename.
- **`trading_occasion` — the one mint,** and the level without which this schema has no non-time top
  and collapses into a calendar. `project` is an internally initiated undertaking of open duration; a
  booking is not a project and a till session is not a project. `fiscal_period` and `record_period`
  are *periods*, and a period cannot hold a party size or a counted quantity. `batch_lot` is the
  nearest structural relative — bounded, dated, countable — but a lot **travels with goods**, while an
  occasion is **consumed at a place and time and vanishes**. `instruction` is a commission from a
  client, which the guest-facing world does not have.
- **`record_period` — REUSE from `finance`.** A trading day or week is exactly the bounded window
  those two rows describe. **`fiscal_period` is explicitly refused**: nine rows want an *accounting*
  period, and conflating it with a *trading* day is how a till reconciliation becomes a management
  account.
- **`product` — REUSE from `manufacturing`,** with the strain declared: a room type and a ticket class
  are sold *capacity*, not an object, and if R1c judges the key cannot stretch, the correct outcome is
  to **narrow this row's claim, not mint a variant**. Proposed as a fact and marked
  destination-hostile — ten thousand SKUs would be ten thousand one-child branches.

Leg 1 passes on the reuse pattern as much as on the mint: this family's fields are **a trading-shaped
selection over the existing proposal pool plus one genuinely unheld concept**, which is what a real
sibling schema looks like.

### Leg 2 — detection signals of its own

The five structures above are the leg, and each is written into `recognition.deterministic` as a
**structure paired with a labelled slot**, per the parent family's requirement. None of the five
appears in the twenty-five landed `business_operations` rows; each was checked against the specific
row most likely to hold it, and the discriminator was written in **both directions** in each case.

The leg is reinforced by what the row **refuses** to treat as a signal. `recognition.never_alone` is
longer here than in any neighbour read, and deliberately so — see the next section.

### Leg 3 — privacy rules of its own

**This is the leg the row passes most clearly, and it is not shared with any neighbour.**

`business_operations` holds material that is mostly **commercially confidential about an
organisation**. `hr` holds **employee** data about a known workforce under contract. This family's
ordinary, everyday, highest-volume output is **personal data about members of the public who have no
relationship with the holder beyond one visit, and who never chose to be filed**:

- a reservation or order export is names, phone numbers, addresses, card tokens and stay histories;
- a function sheet carries **dietary and allergen requirements and accessibility needs** — health-
  derived data about named private individuals;
- an accommodation register may carry **identity-document numbers** taken at check-in;
- a guest complaint names a guest *and* frequently makes an **allegation against a named staff member**;
- a returns or chargeback file joins a named consumer to a payment dispute;
- **till exception and cash-variance reports are, in substance, suspicion records about named staff**;
- a food-safety incident log names the person who missed the check;
- **CCTV and door-access media** are images of customers and staff alike.

**Volume is itself the risk.** One booking is a receipt; a year of bookings is a consumer database;
and the second is produced by this family as a matter of routine. Binding on all fourteen templates:
"Privacy policy must be enforced before content reaches any model or external connector." and
"Protected material should not be included in cloud-model prompts by default, should not display raw
content in general group summaries, and should not be moved automatically without a user policy that
explicitly permits it."

Two honesty notes, so the value is not read as more than it is. **It invents no handling class** —
those are P7's, and the dispatch allows only `none` or `potentially_sensitive`. **It does not claim
every file here is sensitive** — a price list, a range plan, a printed menu and a stock count carry no
person and stay ordinary. The posture exists because the family **cannot be split into a safe half and
a sensitive half at recognition time**: the sensitive members arrive inside the *same exports and the
same folders* as the safe ones. The row does **not** carry `is_safety_domain` and does not ask for it;
it asks that whatever mechanism forces P7 ahead of a model path for third-party personal data reaches
it (NJ-RH-4).

**Verdict: three legs, three passes. `refuse_node: false`.**

---

## The default template, stated for the fourteen siblings

`template.dimension_order` is **empty by contract** — PR-6 leaves this placeholder with no field rows,
and a dimension may only branch on a field its own schema declares. The recommendation is held as
prose, and **this is the paragraph every one of the fourteen must differ from**:

> the **trading unit** — site, venue or channel — *only where the corpus genuinely spans more than
> one* → the **trading occasion**: the session, count, order cycle, booking, function or licensed
> premises the material belongs to → the **operational record function**. Trading period sits *inside*
> the occasion level, never above the site. **Not time-first.**

- **The site level is conditional, but not seeded ineligible** — and this is a deliberate, argued
  divergence from `business_operations`, which seeds `organization` ineligible. A single-site
  operator's tree would gain a one-child branch naming their own shop, so the template-time check
  against the accepted group still applies; but a **multi-site or multi-channel corpus under one
  entity is the normal case in this world**, and the site is then the most useful top level available.
- **The occasion level is the real top,** and it is what stops the tree becoming a calendar.
- **Not time-first, and this family will be more tempted than any other to break the rule,** because
  almost every artefact it holds is *identified* by a trading date. The answer: **the date identifies
  the occasion, it does not root the tree.** "For document and record domains, project, function, or
  subject usually comes before time because putting year first scatters related work across calendar
  folders." The exception belongs to capture-based media alone: "Photos and capture-based media are
  the major exception: time often belongs first because capture date is a defining aspect of the
  material." A trading day, a licence year and a season are **content periods, not capture dates**. A
  child template claiming `time_first: true` is claiming the photos exception without the photos
  evidence, and R1c should reject it on sight — the same ruling `business_operations` made for its 24.
- **Two dimensions are forbidden outright.** `product` would branch per SKU; a **guest name** would
  publish a member of the public's name into the user's directory tree. Both are refused by "The
  engine validates that the proposed template does not repeat a parent dimension, create meaningless
  one-child levels, exceed practical depth limits, use an author or organization merely as a
  collector, expose protected information, or produce empty branches when tested against the accepted
  group."
- Any later order remains editable: "The system recommends an order based on the domain template, but
  the user can reverse, remove, add, or flatten dimensions."

---

## Family-wide principles the fourteen templates must apply

**P1 — Trading in a sector is a field value, not a structure.** The parent family's never-alone rule
is inherited whole and extended. Here, **three tokens are each constitutionally never-alone**: a
**trade name**, a **sector vocabulary word** (menu, store, guest, hotel, table, cover, till, stock),
and a **document-type word**. The reasoning reads across from "A university name alone should not
create a group because Columbia can appear as an authoring school, course provider, target
institution, employer, research venue, or merely a cited organization." — a sentence about **role
ambiguity**, and a hospitality word is *worse* than a university name: `Menu.pdf` may be a live menu,
a designer's portfolio piece, a caterer's proposal, a diner's souvenir, a training example, or a
navigation specification in a software project.

**P2 — The operator side only.** Every artefact here names two parties and the identical bytes exist
twice: the operator's booking sheet and the guest's confirmation; the retailer's dispatch note and the
buyer's delivery email. **The customer's copy is never this family.** The operator's copy carries a
**population or a cycle**; the customer's carries exactly one transaction and no operational
apparatus. Where evidence does not settle which side the holder is on, **the schema must not
activate** — "A model that cannot cite sufficient evidence must return unknown."

**P3 — The paired-reality rule.** Three of the five structures are **pairs**: counted against
recorded. A template claiming one must show the *pair*. A single number is `finance` or
`business_operations`.

**P4 — Capacity is the hospitality invariant.** A template about "an event" with no capacity or
attendance structure is `business_operations.project-delivery` or `creative`, not this family.

**P5 — Never time-first**, per the default template above.

**P6 — The lone-transaction rule.** A single supplier invoice or customer receipt is **not** this
family. `00` names the destination by hand: "Receipts and Confirmations may hold isolated invoices,
delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and
similar transactional documents." — booking records, purchase receipts and event tickets, *by name*.
This family owns the **cycle**, not the document.

**P7 — Guest-data default.** Any template whose evidence can include a guest list, a review, a
complaint, a dietary note or CCTV carries `potentially_sensitive` and **may not weaken it because the
file "looks like a spreadsheet"**.

**P8 — Refusal is a success.** A template that cannot name one of the five structures (or a sixth of
equal standing) should refuse and route through `falls_through_to`. Keeping a row to preserve a legacy
id is the 574's mistake.

---

## Files considered and rejected

The tempting false positives, and why each is not this family's evidence:

| File | Why not here |
|---|---|
| `Employee Handbook v4.2.pdf`, staff training certificate | `business_operations.policy-handbook` / `hr`. A governing document does not become a trading record because the staff serve food. |
| `FY26 budget v7 FINAL.xlsx`, `March 2026 board pack.pdf` | `business_operations`. Period-and-line-item variance, not counted-against-recorded. |
| VAT return, annual accounts, merchant settlement statement | `finance`. Account identity plus posting structure. |
| `Supplier agreement - Harlow Foods.pdf` | `business_operations.contract-administration` (register/notice machinery) or `legal` (the instrument). This row owns the **orders placed under it**, not the agreement. |
| Public liability / stock insurance schedule | `finance.insurance-corporate`. |
| `Tender pack - catering concession.pdf` | `business_operations.procurement-sourcing`, or `government.public-procurement` on the authority side. A sourcing *event* is not replenishment, even when the goods are food. |
| `Unit 4 - service charge 2026.pdf`, rent review, dilapidations | `construction_property.commercial-lease`. A lease record survives a change of trade; a trading record does not survive a change of premises. |
| EPOS software licence and support contract | `business_operations.it-asset-inventory` / `contract-administration`. The row owns what the terminal **recorded**, not the terminal. |
| `Menu_Spring2026_v7.indd`, `SKU40182_hero_final.psd` | `creative`. Production apparatus, not commercial apparatus. |
| Campaign calendar, social assets | `creative` / `business_operations.go-to-market`. |
| A plated-food photograph with camera EXIF | `photos`. A picture of food is not a food-safety record. |
| `Booking confirmation - Le Petit Jardin 14 Mar.pdf` (the diner's copy) | **Receipts and Confirmations.** P2. This is the rejection most likely to be got wrong, because it is the most hospitality-*looking* file a personal corpus contains. |
| Blank temperature log, wholesaler's specimen price list, franchise operations manual | Template / sample / instructional material. "Topic answers what a file is about, while purpose answers what the file was for." |

---

## The collision fixture, named

**`Invoice 88231.pdf`** — a food wholesaler's letterhead, VAT number, line items with quantities, a
total, payment terms. It looks exactly like `retail_hospitality.supplier-order` evidence. **It is
not.**

What discriminates it: **the absence of the cycle.** No purchase-order reference, no goods-received
annotation, no shortage or rejection column, no credit note beside it, nothing else in the folder
sharing a reference with it. `supplier-order` requires a **recurring reference across an order,
a delivery note carrying ordered-against-received, and a settlement**, or a trade price list /
allocation structure. One invoice is a transaction, and `00` has already named its home: "Receipts and
Confirmations may hold isolated invoices, delivery confirmations, booking records, boarding passes,
purchase receipts, event tickets, and similar transactional documents."

**Second fixture, in the other direction:** `Appointments_2026-03.csv` — named individuals, dates,
time slots, durations, phone numbers, a notes column. Capacity-against-dated-demand on its face, and
it is `clinical_practice`. Discriminator: the slot is with a **named practitioner** for a **subject of
care**, with a clinical or procedure code or a chart reference; this family requires the slot to
consume a **finite physical capacity** — a table, a room, a seat — counted in covers, pax or
room-nights. Neither may take the other on the shape alone, and where evidence does not settle it,
neither should activate.

**Third fixture, the one that decides the family's privacy posture:** `Week 12 rota.xlsx`. See NJ-RH-1.

---

## Reciprocal boundaries — the seams, both directions

Nine are written into `collides_with`, each stating what **this row must not take** and what the
**neighbour must not take**, and each naming the same fixture bytes on both sides. Summarised:

| Neighbour | Same bytes | Discriminator |
|---|---|---|
| `business_operations` (**existential**) | `Kitchen deep clean schedule signed.pdf`, `Employee Handbook v4.2.pdf`, `Supplier agreement.pdf` | The five structures. Sub-seams written for `procurement-sourcing` (sourcing event vs replenishment), `customer-account-management` (named B2B relationship vs one-visit consumer), `facilities-workplace` (the fridge's **maintenance contract** vs the fridge's **temperature log**), `compliance-audit` (assessment occurrence vs the diary it pulls from), `it-asset-inventory` (the terminal vs what it recorded). |
| `finance` | `Sales summary March 2026.xlsx` | **Account identity + posting structure → finance. Till / session / department / tender structure with no account identity → here.** Where both present, finance's protective ordering runs first. One-way; R1c owes the reciprocal. |
| `government` | `Premises licence 12345 - conditions.pdf`, `Food hygiene inspection report.pdf` | **Custody, not content** — precisely the rule `government`'s own anchor states, and consistent with the side `construction_property.building-control` already wrote. Authority-side administration → `government`; the operator's own copy of its own permission → here. Receipt of an authority-issued document does not activate `government`. |
| `hr` | `Week 12 rota.xlsx` | Labour hours against **forecast covers/sales** (with a sales-per-labour-hour column) → here; contracted hours, absence, pay → `hr`. **Unresolved on the bare fixture — NJ-RH-1.** |
| `construction_property` | `Unit 4 - …` | A lease record survives a change of trade; a trading record does not survive a change of premises. Three-way noted: fit-out → `construction-project`, maintenance → `facilities-workplace`, selling → here. |
| `logistics` | a delivery note | Keyed to a **consignment** → logistics; keyed to the buyer's **purchase order** → here. One-way; reciprocal owed. |
| `creative` | `Menu_…v7.indd` | Production apparatus vs commercial apparatus. |
| `manufacturing` | an ingredient list with yields and unit costs | A batch code the operator **receives** is traceability here; a batch code the operator **issues** is manufacturing's. |
| `clinical_practice` | `Appointments_2026-03.csv` | Practitioner-and-subject-of-care vs finite physical capacity. Dietary/allergen data raises privacy here and creates **no** medical claim either way. |

`also_holds_with` records five genuine disjoint-evidence joins (`finance`, `business_operations`,
`hr`, `government`, `photos`) — the case that keeps the existential seam from becoming a fight over
whole folders.

---

## Recommendations to R1c (this row edited no neighbour)

1. **`business_operations`** — its `customer-account-management`, `procurement-sourcing`,
   `facilities-workplace` and `compliance-audit` rows already name `retail_hospitality.*` templates in
   their `collides_with`. Those edges should be checked against the sub-seam wording written here;
   this row believes they agree, but it did not touch them.
2. **`finance`** and **`logistics`** — reciprocals owed; both seams were authored one-way and marked
   `inference`.
3. **`site` vs `property`** — adjudicate as a **pair** (see `role_split`), so neither absorbs the
   other, exactly as `construction_property` asked for `organization`.
4. **`manufacturing`** — asked to **widen** `site` and `product` rather than have a second key minted
   here.

---

## Sparse-file discipline

Nothing in this world licenses a fact copy. A group formed on one trading occasion does **not** put a
trading date on an undated photograph that happens to sit in the folder; a supplier-order cycle does
**not** put an order reference on an unrelated PDF. Every `file_examples` entry sets
`facts_legal` to the universal facts only and lists a folder path under `must_not_conclude`, because
the schema declares no fields and **a path is never a fact**.

---

## Audits run before returning

- `python3 -m json.tool planning/domains/nodes/retail_hospitality.json` — **parses.**
- Key set compared programmatically against `business_operations.json` — **symmetric difference is
  empty** (27 keys, same order).
- `refuse_node: false`, `launch: "placeholder"`, `fields: []`, `kind: "schema"`, `provenance:
  "proposal"`, `design_cite: null` — **as the assignment requires.**
- Every `“…”` quotation in the JSON extracted by regex and tested for exact substring membership in
  `planning/00-database-agent-product-design.md` — **23 quotations, 0 failures.** One near-quotation
  that came from the dispatch prompt rather than `00` was **de-quoted** rather than left to imply a
  `00` citation.
- `file_kinds.source_types` checked against `src/evidence_shape/vocabulary.py` `SOURCE_TYPES` — all
  twelve values are members.
- No canonical field key minted; four `proposed_fields`, of which **three are explicit reuses** of
  existing proposals and one is a mint with its argument.
- Files written: **exactly two**, both under `planning/domains/nodes/`. No neighbour, roster,
  canonical-fields, `src/` or `check.py` edit.

---

## NEEDS-JOSEPH

- **NJ-RH-1 — the bare rota.** `Week 12 rota.xlsx` (names, days, hours) is undecidable between
  `retail_hospitality.store-operations` and `hr`. **Alternatives:** (a) a sales-per-labour-hour or
  labour-percentage column decides for this family, contracted-hours/absence/pay decides for `hr` —
  this row's proposal; (b) `hr` takes every rota and this family takes only the trade forecast it is
  built from. **Both rows must say the same thing**, and `hr` landed first.
- **NJ-RH-2 — `event-production`.** A venue delivering a function has capacity structure and is
  clearly this family; an **agency producing an event for a client** is an instructed commission and
  may not be. **Alternatives:** narrow the template to venue-side delivery, or refuse it and route to
  `business_operations.project-delivery` plus this schema's default.
- **NJ-RH-3 — `catering-contract` may be a duplicate** of `bookings-reservations` +
  `event-production` + `business_operations.contract-administration`. It survives **only** if the
  function-sheet → allergen-sheet → final-account chain is shown to be a structure none of the three
  holds. R1c should test it hard rather than assume it.
- **NJ-RH-4 — trading-floor CCTV and door-access media.** No landed row claims them; they are the
  family's highest-risk bytes and they are `audio_video`, not documents. **Alternatives:**
  `store-operations`; a privacy-only route straight to Protected Records with no domain claim; or a
  security world that does not exist yet. **Related and more general:** whether the mechanism that
  forces P7 ahead of a model path reaches **third-party** personal data in a row that does not carry
  `is_safety_domain`. `business_operations` recorded the same gap; it is sharper here because the data
  subjects are members of the public.
- **NJ-RH-5 — may `record_period` be sub-daily?** Both `finance` proposals of that key are multi-day
  ranges. If it may not stretch to a lunch service or a morning till session, this family has **no key
  for a service session** and five templates lose a level.
- **NJ-RH-6 — the name.** The roster says "Retail, hospitality and events", but this pass found no
  schema-level structure for *events* beyond the capacity invariant the whole family shares, so events
  is carried **inside** rather than as a third leg. If R1c disagrees, **the name should change rather
  than the shape.**
- **NJ-RH-7 — is an e-commerce channel a `site`?** It has no physical location.
  `retail_hospitality.ecommerce-ops` depends on the answer. This row's reading is that a channel is a
  trading unit in the same sense and should be admitted; the alternative is that `ecommerce-ops` has
  no top level and folds toward `product-catalogue` plus `business_operations.support-operations`.
