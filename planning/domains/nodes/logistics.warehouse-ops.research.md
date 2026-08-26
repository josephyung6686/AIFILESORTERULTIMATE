# logistics.warehouse-ops — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: logistics`, `launch: placeholder`, `parent_id: null`.
Output: [`logistics.warehouse-ops.json`](logistics.warehouse-ops.json). Salvage: none — both files new.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the stamped assignment
  (`make_prompt.py logistics.warehouse-ops`).
- `planning/domains/nodes/logistics.json` — **the schema anchor, and the decisive input.** Written
  at J-DEPTH, declares no field rows under PR-6, proposes five keys (`consignment`, `carrier`,
  `asset`, `site`, `record_type`), and states in capitals inside its own `template.why` that its
  prose order is *the default template the seven siblings must differ from*. This row is measured
  against that sentence and answers it explicitly.
- `planning/00-database-agent-product-design.md` — authoritative; reached by targeted `grep -n`
  for the six spans quoted, never streamed. All verified verbatim before writing (audit below).
- `planning/domains/nodes/finance.crypto-assets.research.md` — the one landed launch row read for
  calibration. Two of its arguments are reused honestly: dropping a schema-default dimension
  because *the facts cannot fill it* (it dropped `account_type`; this row suppresses the
  counterparty level), and refusing to mint a key for the string the material is saturated with
  (it refused wallet address and ticker; this row refuses bin code and SKU).
- `planning/domains/roster.json` — all eight `collides_with` ids, both `also_holds_with` schema
  ids and all three `role_split` neighbours resolved mechanically by grep.
- `planning/domains/nodes/clinical_practice.pharmacy-operations.{json,research.md}` — the only
  landed row that had already argued a boundary against this id.

## THE CHARGE — the case that this row should not exist

Stated at full strength before any defence.

1. **A lifecycle stage.** The schema's anchor is a custody handover. A warehouse is the interval
   *between* two handovers; `logistics.shipment` holds the consignment inbound and outbound, and
   this row claims the gap. A stage of another row's subject is not a node.
2. **A value of `site`.** The schema already proposes `site`, example `Depot B — Avonmouth`.
   "Warehouse" is a value that key takes.
3. **A bundle of `work_type` values.** Three of the anchor's twenty enumerated work types are
   verbatim this row's contents: *goods-in receipt, put-away, stock-location and cycle-movement
   record*; *pick list, pack note, dispatch note and load manifest*; *warehouse exception: damage,
   quarantine, shortage or hold record*. Work types are values, never nodes.
4. **A duplicate of its own schema's default template.** The default reads *counterparty (only
   where plural) → custody subject (the consignment or container; **or, in the fleet and dispatch
   branches, the vehicle, the depot or the working day**) → document function → time leaf.* The
   depot is already inside that custody-subject slot, so `site → record_type` looks like the
   default with one branch selected.
5. **Defined by an absence** — "logistics minus the road": no carrier, no movement between places,
   no consignee.
6. **A duplicate of neighbours.** A sheet of item codes, quantities and locations is
   `retail_hospitality.stocktake` with extra columns; a spares crib is `manufacturing.spare-parts`;
   an item-and-location register is `business_operations.it-asset-inventory`.

Charges 3 and 4 are serious. Charges 2 and 5 would be fatal if true.

## Defeating it

**Against 1 and 5 — the decisive fact: the consignment identity does not survive the building.** An
inbound pallet is broken at receipt into lines put away into bins where they mingle with stock from
other receipts, and they leave in many different outbound consignments; one bin holds goods from
several inbound references, one wave satisfies several outbound orders. There is therefore **no
consignment key that can retrieve a put-away task, a stock-on-hand row or a count variance** — not
because the key is missing but because it never existed for those records. That is not a stage of
the schema's retrieval spine; it is a different spine with its own keys (handling unit, bin, wave,
task, adjustment). Charge 5 falls with it: the row has a positive structure — stock identifier +
quantity + structured intra-facility location + a movement verb from a closed internal vocabulary +
an internal task or handling-unit reference. The missing counterparty is corroboration, not the
definition.

**Against 2 — the site-value charge, the one that could kill it.** The row is not "files whose
`site` is a warehouse." A walkaround check is signed at a depot; a customs pack is filed at a
depot; a run sheet is printed at a depot; a racking certificate is issued for a depot. All carry
`site = Depot B` and **none** is this row's. The building is the recommended *first dimension*,
which is not the same as being the definition. `never_alone` encodes it — *a site, depot or
building name alone* — and `Warehouse lease - Unit 4 Avonmouth.pdf` exists to trip it.

**Against 3.** Every sibling can be described as a subset of the anchor's twenty work types; the
anchor enumerated all twenty across the family deliberately, because work types are schema-level
values. The node test does not ask whether a row's work types are enumerated upstream — it asks
whether signals, dimensions or privacy rules differ. All three do. And the row is not the union of
three enum members: it is the evidence structure they share and no other sibling has.

**Against 4.** Answered by stating the diff, not claiming one — two levels differ, see leg 2.

**Against 6.** Each is written as a reciprocal collision with a byte-readable discriminator.

**Verdict: the node survives.** `refuse_node: false`, with `fields: []`, `proposed_fields: []`,
`dimension_order: []`. Nothing was invented to keep it, and NJ-WH-1 hands R1c the charge intact so
it can still be refused above this row.

## The node test, all three legs

### Leg 1 — detection signals differ structurally

The schema default fires on a **consignment structure**: two named parties in *different roles* +
a carrier undertaking + one described quantity + a place of taking over + a place of delivery + an
acknowledgement slot. The anchor calls that "the family's fingerprint."

A warehouse record has none of those six. No second party, no undertaking, no place of delivery,
and — sharpest — **no acknowledgement by a receiving counterparty**: only an operative signoff and
a system timestamp. `Put-away tasks 2026-04-14 AM - Depot B.csv` is the pure demonstration: dock
door → bin, item, quantity, timestamp, operative id, and not one party name in the file.

Two signals have no analogue in the default at all. The **two-quantity receiving reconciliation**
(advised against received, reason code, put-away destination) is exactly what separates a goods-in
record from the one-quantity signed delivery note the driver handed over. The **count-variance
structure** (system qty beside counted qty per location, recount pass, adjustment reason) is not a
consignment shape in any respect.

### Leg 2 — recommended dimensions differ on two levels

Default: *counterparty (where plural) → custody subject → document function → time leaf.*
This row: **`site` → `record_type`, time as a leaf only.**

- **The counterparty level is suppressed outright, not made conditional.** A put-away list, a count
  variance and a stock-on-hand report name no carrier and frequently no supplier either; a level
  most of the corpus cannot enter is worse than no level.
- **`site` is promoted to first**, not left as one option in the default's second slot, because a
  bin code is meaningful only relative to a building — `A-12-03-B` exists in every facility an
  operator runs. `00`: "a parent dimension should provide the context required to understand the
  child." A consignment's meaning survives independent of where it rests; a bin's does not.
- **What is deliberately not a level** matters as much: the custody subject here is the stock
  identifier at a location, and neither is made a dimension — the opposite of the default, which
  puts the custody subject at level two.

`time_first: false`, per `00`: "For document and record domains, project, function, or subject
usually comes before time because putting year first scatters related work across calendar
folders." A receipt, its put-away, its shortage note and the count that six weeks later found the
missing pallet must group.

### Leg 3 — privacy rules differ in kind, by inversion

The strongest leg. The schema binds all seven siblings to **THE CONSIGNEE IS A PARTY, NEVER A
FOLDER**, because the family's ordinary payload is a counterparty's personal data — home address,
signatory surname, signature image, delivery coordinate, doorstep photograph of a dwelling.

**This row's exposure is inverted.** A put-away task leaks a bin; a cycle count leaks a company's
holdings. What it leaks instead, and what the family principle says nothing about, is **the firm's
own workers**: a pick-accuracy and units-per-hour report is individual performance measurement; an
operative column on a movement log is a minute-by-minute record of one named worker's day inside a
building — structurally the tachograph's harm arriving through a *quantity* column rather than a
*location* one; a short-pick exception attributed to a named picker is a conduct record; a
stock-loss investigation names a suspected employee and attaches CCTV stills.

So the row states its own rule — **THE OPERATIVE IS A SIGNOFF, NEVER A FOLDER** — and a second the
family has no version of: **a bin code is not a folder either**, being a machine coordinate that
opens thousands of branches no human browses and a tree that publishes a facility's internal layout.
`00` supports the person half: "A folder should not become a collection point for everything
produced by the same person or organization." `Pick accuracy and units per hour - April 2026.xlsx`
is carried as a fixture so this leg has evidence rather than a claim.

## Fixtures, bottom up

Twelve, covering the ugly cases. `Goods in 2026-04 Depot B.xlsx` is the happy case and the shared
fixture with the anchor. `Put-away tasks 2026-04-14 AM - Depot B.csv` is the purest — **no party
appears anywhere in the file**, the row's whole argument in one artefact. `Pick wave 4417 - pick
list.pdf` is the hinge: it *does* carry outbound order references and still belongs here, because it
belongs to many of them. `Cycle count variance 2026-W16 - Zone C.xlsx` is the stocktake seam with
the discriminating column missing on purpose. `Depot B - goods in note scan 2026-04-12.pdf` is OCR
of a counterparty's document where a **handwritten annotation** is the only thing that moves it
across the boundary. `Quarantine hold notice - batch 24B117.pdf` is the manufacturing
co-activation: goods that neither transform nor move. `IMG_20260414_0917.jpg` is the sparse file.
`WMS_stock_adjustments_20260414.xml` is the structured export, inspected as structure not format.
`Loading manifest - trailer T4402 2026-04-14.pdf` is the changeover document, conceded to
`logistics.shipment` at the point a carrier undertaking appears. `Pick accuracy and units per hour -
April 2026.xlsx` carries leg 3. The last two are negatives, below.

The archive case is handled by `falls_through_to → Unsupported or Encrypted` rather than a fixture:
an operations archive's manifest rarely discloses a movement structure, so `00`'s
inspect-without-unpacking rule yields a facility name and nothing this row can act on.

## The collision fixture

`Stock valuation 2026-03-31.xlsx` satisfies a careless reading of the fingerprint almost exactly —
item code, quantity on hand, and a **bin-shaped location column**. Three things discriminate it, all
readable in the bytes: (1) a unit-cost and extended-value column, which the row encodes as an
inverted `never_alone` — a valuation column is not weak evidence for this row but evidence
*against* it; (2) an ownership premise in the heading ("stock owned at 31 March"), because a
stocktake counts what a business owns in order to value it while a warehouse frequently holds
somebody else's goods; (3) **no movement at all** — no from-location, no verb, no task or
handling-unit reference. A position is not a movement. It is `retail_hospitality.stocktake`'s and
is carried here with `facts_legal: []`.

The second negative, `Warehouse lease - Unit 4 Avonmouth.pdf`, exposes something structural:
**three roster rows are tempted by the word warehouse and only one is about goods** — this row
(movements), `business_operations.facilities-workplace` (the building as a workplace) and
`construction_property.commercial-lease` (the building as a demise). The lease is the third's, and
neither of the first two should have it.

## Reciprocal boundaries

Eight collisions are written, each in both directions with a shared fixture. The three that matter:

- **`logistics.shipment`** (same-schema mutex). *Outbound:* the moment a carrier undertaking, a
  trailer under that undertaking and a place of delivery appear, that row takes it — stated on
  `Loading manifest - trailer T4402`. *Inbound:* that row must not take a wave, a put-away or a
  count merely because a consignment reference appears on the page, because the wave serves many
  consignments and belongs to none. *Reverse, same fixture family:* `Depot B - goods in note scan
  2026-04-12.pdf` without its goods-in stamp and shortage annotation is that row's delivery
  evidence, not this row's.
- **`retail_hospitality.stocktake`.** The anchor stated this seam from above; this row **confirms
  it from below with independent reasoning and the same fixture pair** rather than inheriting it —
  `Cycle count variance 2026-W16 - Zone C.xlsx` here against `Stock valuation 2026-03-31.xlsx`
  there. The reciprocal the anchor did not state, added here for R1c: the return direction, that
  this row must not take a period-end valuation just because it carries a location column.
- **`manufacturing`.** The anchor's quantity-identity test (identity changes → transformation →
  manufacturing; holder changes → movement → logistics) does not decide a *hold*, where the goods
  do neither. Sharpened here for the static case: **fitness versus place.** A disposition against a
  specification (accept, reject, rework, concession) is manufacturing's; a disposition about
  placement (quarantine, block from pickable stock, release to the pick face, scrap out of the
  location) is this row's. `Quarantine hold notice - batch 24B117.pdf` usually records both and is
  also written under `also_holds_with`.

Also written: `manufacturing.spare-parts` (a spares store's demand documents point *inward* at
equipment — asset id, work order, failure code — and its issues are consumed; this row's point
*outward* at an order, a wave and a staging lane, and its stock leaves intact),
`business_operations.it-asset-inventory` (fungible stock versus identified assets in use — where an
assignee, build state or lifecycle date appears, that row keeps it),
`business_operations.facilities-workplace`, `retail_hospitality.ecommerce-ops` (keyed on the
customer order versus keyed on the facility's work), and `construction_property.materials-delivery`
(whose job-key test this row endorses, adding that a builders' merchant's *own* depot records are
this row's even though every outbound note the merchant produces is that row's).

**`clinical_practice.pharmacy-operations`** — the only landed row that had already argued against
this id, and it argued *for* it, routing ordinary inventory to "`retail_hospitality.stocktake` or
`logistics.warehouse-ops`" and giving a discriminator this row accepts unchanged: "A bin-location or
pallet movement anchored on storage and fulfilment supports warehouse-ops; a per-product accountable
register, named supply, controlled schedule, witnessed destruction, or dispensing-payer return
supports this row." No edge is written back, deliberately — the edge it needs is one this row would
only restate, and writing it would suggest a contest where there is agreement.

## Neighbours considered that did not get an edge

`business_operations.procurement-sourcing` — buying is not moving; a purchase order never reaches
the fingerprint (no location, no verb, no task), and the anchor holds the seam at family level.
`manufacturing.production-planning` — item codes and quantities without a location-keyed movement;
covered by a `needs_llm` line. `retail_hospitality.supplier-order` — the inbound demand document,
one step upstream of anything this row sees. `retail_hospitality.returns-warranty` — the anchor
already ruled that entitlement stays there and only the movement leg is logistics'; restating it
would duplicate an anchor ruling. `construction_property.plant-hire` and
`manufacturing.asset-register` — both move identified assets in and out of a store, but an asset is
not fungible stock, and `business_operations.it-asset-inventory` already carries that discriminator;
two more claimants would give one evidence item four homes. `finance` — the freight-invoice seam is
the anchor's, and this row's material has no price column at all.

`also_holds_with` is restricted to schema ids (`manufacturing`, `photos`) per the contract's
schema-only rule on that edge. The anchor uses a template id in one of its own entries; this row did
not copy that and flags the divergence rather than following it silently — see NJ-WH-5.

## Files considered and rejected from the kept corpus

- **A racking inspection certificate / forklift thorough-examination report** — unmistakably
  warehouse material, but its subject is equipment and a statutory duty, not stock. Taking it would
  make this row "everything that happens in a shed."
- **A depot shift rota and a forklift-operator training matrix** — same reason, and they would drag
  the row toward person-keyed material leg 3 has just refused.
- **A dangerous-goods storage-segregation plan** — a close call, since it names locations and goods.
  Rejected because it is a *rule about* storage, not a *record of* a movement; prescription is not
  evidence of an event.
- **A packing list** — the most warehouse-ish document in the schema's whole work-type list,
  produced at a pack bench, and given up anyway: its rows are packages under one consignment
  travelling to one place, so the internal-key test this row itself proposes hands it to
  `logistics.shipment`. Consistency required the loss.
- **A carrier's rate card for depot collections** — procurement's; no stock in it.
- **A stock-item photograph for a product catalogue** — merchandise is
  `retail_hospitality.product-catalogue`'s; only the *condition* photograph is this row's, and only
  through a group.
- **A `.ics` cycle-count reminder** — a `SOURCE_TYPE` and an event; nothing fires that the default
  would not.

## `proposed_fields` — empty, deliberately

`fields: []` because a template never copies its schema's list and the schema declares none under
PR-6. `proposed_fields: []` because `site` and `record_type` are already proposed on the `logistics`
schema row and are **reused, not re-proposed** — which is exactly what the anchor asked for in its
NJ-LOG-5.

The two strings this material is saturated with are deliberately not fields, and this is the row's
most consequential restraint. **A bin or location code**: no canonical key exists, and minting one
would immediately raise whether it may be a folder level, where the answer is no twice over —
thousands of unbrowsable branches, and a tree that publishes a facility's internal layout. **A stock
identifier (SKU / part / batch)**: the worst `never_alone` token on the node, since the same short
alphanumeric shape is a part number, a drawing reference, a policy clause, a room number and a
catalogue code. Evidence, and at most a value inside content — never a key.

`proposed_context_terms` is not written: `00` states the pattern-plus-context *shape* for course
codes only, and this row's vocabulary (put away, replenish, pick face, handling unit, cycle count)
is R6's to adjudicate.

## Sparse-file discipline

`IMG_20260414_0917.jpg` is the `HW 3.pdf` of this node — two other frames of the same pallet beside
it, an illegible bin label in frame, EXIF datetime and no GPS. Marked
`group_without_copying_facts: true` with `facts_legal: []` — **not even `site`**, because the
neighbourhood is the only thing suggesting a facility and the row refuses to manufacture one. Its
`must_not_conclude` covers both halves of `00`'s warning: absent GPS proves nothing, and a present
coordinate would be a capture location, not the facility the stock was held in.

## Audits run before returning

`python3 -m json.tool` parses. Every `00` span written inside quote marks was grep-matched verbatim
**before** being written — six spans, six matches: roles-separation and collection-point (line 44),
session/topic (line 45), more-than-one-domain (line 48), parent-dimension and project-before-time
(line 95); the protected-records sentence verified by `grep -c` returning 1. **No `00` quotation in
this node is fabricated or paraphrased inside quote marks.** All twelve `file_examples.source_type`
values are in the fourteen-member `SOURCE_TYPES` list; all eight `collides_with.domain` values, both
`also_holds_with` domains, both `also_schema` values and all three `role_split.neighbour` values are
roster ids; all six `falls_through_to` names are §7.3 residuals. `fields`, `proposed_fields` and
`dimension_order` are empty with stated reasons. Twelve `never_alone` rules, at least two true of a
tempting false file by construction. No threshold, score or evidence count anywhere; no handling
class; `sensitivity: potentially_sensitive` only. No file example writes a folder path as a fact —
every one carries "a folder path" in `must_not_conclude`. Only the two assigned files were written;
the roster, `canonical_fields.json`, `check.py`, `src/`, the SPECs and every neighbour node are
untouched.

## NEEDS-JOSEPH (this node only)

- **NJ-WH-1 — is the INTERNAL-KEY test the right seam against `logistics.shipment`, or should this
  coverage fold into that row as `work_type` values?** THE CHARGE, handed to R1c intact so the row
  remains refusable above this level. *For folding:* five of the anchor's own work types are this
  row's contents, and work types are values. *Against:* a consignment key cannot retrieve a put-away
  task or a count variance, because the consignment identity is destroyed at receipt and rebuilt at
  despatch. Alternatives: (a) keep the row on the internal-key test, as written; (b) fold into
  `logistics.shipment` and accept that inside-the-building records fall through to `Independent
  Records` whenever no consignment reference is present — which is most of them; (c) narrow to the
  exception subset (damage, shortage, quarantine, hold) only, which would make it a row defined by
  absence. Recommends (a); considers (c) the worst option.
- **NJ-WH-2 — does `site → record_type` survive a single-facility corpus?** Most corpora have one
  depot, in which case the first level collapses to a constant and the order becomes `record_type`
  alone — arguably indistinguishable from the default's third level, weakening leg 2 to a one-level
  claim. Alternatives: (a) emit `site` only where the corpus spans more than one facility, exactly
  as the default treats the carrier level; (b) always emit it, for stability as a corpus grows;
  (c) state the order as `record_type` with `site` as an optional parent. Recommends (a). Legs 1 and
  3 carry the node without leg 2, so this does not put the row itself at risk.
- **NJ-WH-3 — who owns worker-performance and shrinkage-investigation records?** Held here under the
  operative rule, but their subject is a person, not stock. Alternatives: (a) this row does not fire
  on them and they route to `Protected Records` or `business_operations.organisational-records`;
  (b) held here with the no-person-dimension rule as written, being facility-scoped operational
  records; (c) deferred to the anchor's NJ-LOG-4 on whether a record-SUBJECT person may ever be a
  destination dimension — the same question, answerable once globally.
- **NJ-WH-4 — `site` and `record_type` are reused, not re-proposed.** If R1c splits, renames or
  rejects either, this row's recommended order and eight `facts_legal` lines change with it. Flagged
  rather than silently depended on.
- **NJ-WH-5 (cross-row recommendation for R1c; this row edited nothing).** The `logistics` schema
  anchor writes a **template** id (`construction_property.materials-delivery`) under
  `also_holds_with`, which the contract restricts to schema ids. Reconcile the anchor entry or the
  rule.
