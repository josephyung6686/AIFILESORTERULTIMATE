# Research memo — `retail_hospitality.product-catalogue`

Depth: J-DEPTH
Date: 2026-08-27
Output: `planning/domains/nodes/retail_hospitality.product-catalogue.json`
Roster row: template on the fieldless `retail_hospitality` schema, `parent_id: null`, placeholder launch

## Result

**Accept the node.** It survives the charge on all three legs, and it survives it in an unusual way: this is
the one row in its family that is not a record *of an event*. Every sibling records a trading occasion and
measures a counted reality against a recorded belief. This row **is the recorded belief** — the standing
range, the standing price — that the others measure against. That is not an absence, it is a different
anchor, and it produces different detection signals, an inverted dimension shape, and a privacy rule that
runs opposite to its schema's.

Three landed siblings had already argued a boundary against this row before it was written, and all three
positively assign it material: `ecommerce-ops` cedes "the PRODUCT AS A THING SOLD", `menu-recipe-costing`
cedes "the ATOMIC PRICED SELLING LINE", `stocktake` cedes the file "when it is read as a range and price
file". `logistics.warehouse-ops` goes further and names the row in its rejected list: "**A stock-item
photograph for a product catalogue** — merchandise is `retail_hospitality.product-catalogue`'s". A row that
four independently-written neighbours have already handed work to is not a label.

## Sources used

The standing brief and the stamped assignment; `00` reached by targeted grep only, with every span
grep-verified (`grep -c -F`) before use; the `retail_hospitality` schema anchor for its default template,
recognition structures, `work_types`, sensitivity and residuals; `legal.practice-matter-file.research.md`
for depth calibration; `roster.json` for edge ids; and the landed siblings `ecommerce-ops.json`,
`menu-recipe-costing.json`, `stocktake.json` and `logistics.warehouse-ops.research.md`, read only at the
spans naming this row.

## The charge — the strongest case that this row should not exist

Stated at full strength before the defence, because it is genuinely strong and two of its five limbs land.

**1. It is a work-type value, and the schema itself files it as one.** `retail_hospitality.work_types[0]`
reads: "product, range and price record - catalogue line, price list, range plan, listing, product copy and
imagery brief". The schema has already declared this row's entire subject matter to be a *value of a
function dimension*. CONNECTION's node test and the brief both say work types are values, not rows.

**2. It is a document type.** "Catalogue", "price list", "menu", "line sheet", "brochure" are document-type
words. The schema anticipates precisely this row in its own `never_alone` list: "A DOCUMENT-TYPE WORD,
standing alone - invoice, rota, log, price list, order, review. These are values of a function dimension,
and a row resting on one is the schema's default template wearing a name." *Price list* is named. No other
row in the family is indicted by its own schema this directly.

**3. It is a medium and a length.** "Product photography" is an image. "Product copy" is short-form text.
A row that bundles an image medium and a text medium under a subject noun is a folder, not a node.

**4. It is defined by an absence.** The family's grammar is the trading occasion. This row's distinguishing
feature is that it *has* no occasion. A row whose definition is "the one without the thing" is the failure
mode the brief names explicitly.

**5. It duplicates its neighbours.** `ecommerce-ops` holds product listings. `menu-recipe-costing` holds
priced menus with allergen footnotes. `stocktake` holds SKU-and-price exports. `supplier-order` holds trade
price lists. Between them, is anything left?

## Defeating it

**Limbs 3 and 5 are conceded in part, and the concession narrows the row.** The row does *not* own product
photography as a medium — an image alone is `never_alone` here, by the schema's own rule ("A FOOD, DRINK OR
PRODUCT IMAGE, standing alone"), and the *making* of the images goes to `creative.commissioned-shoot` on a
reciprocal edge. It owns only the delivered asset **named by an item key that recurs in an accepted range or
price file**. Likewise it does not own listings (`ecommerce-ops`), cost models (`menu-recipe-costing`),
counts (`stocktake`) or inbound trade lists (`supplier-order`). Seven `collides_with` edges are the price of
admission, and each one removes material. What remains is smaller than the row's name suggests, which is the
correct outcome of a charge that partly lands.

**Limb 4 fails on inspection.** The row is not defined by the absent occasion; it is defined by a *present*
anchor the family has nowhere else — the **range or season**, versioned by an **effective-from date**. The
schema's own summary makes the point available: the family's anchor "is a TRADING UNIT running a TRADING
OCCASION … and producing a record that pairs a COUNTED REALITY against a RECORDED BELIEF, or a FINITE
CAPACITY against a DATED DEMAND". A pairing needs two halves. The recorded belief and the finite capacity
are *authored somewhere* before an occasion tests them, and this row is where. `stocktake`'s own edge proves
it: it takes `stock_export_20260331.csv` as "the RECORDED BELIEF half of a count" and concedes that "on its
own bytes the file favours the catalogue row". A row that other rows must *borrow from* to complete their
own structure is a referent, not a gap.

**Limbs 1 and 2 fail on the node test proper**, which is the only test that decides this, and which follows.

## The node test, all three legs

CONNECTION §2: a template row exists only where its **detection signals**, **recommended dimensions**, or
**privacy rules** differ from its schema's default. This row differs on all three, with independent
reasoning for each.

### Leg 1 — detection signals

The schema's default template holds nine deterministic structures; one of them, "A CATALOGUE-AND-PRICE
structure", is this row's raw material: "A record with one row per selling line carrying a code, a
description, a price, and at least two of a cost, a margin, a range or season slot, a barcode-shaped token,
and a stock-status slot". If that were all this row had, limb 2 of the charge would win — the row would be
the default template wearing the word *catalogue*.

It is not all. The row's signal adds two requirements the schema-level structure does not state:

- **an effective-from, valid-from or version slot**, which makes two files with *identical rows* two
  different records rather than duplicates; and
- **an item key that recurs across artefacts of different function** — the same code naming an image file,
  a paragraph of copy, a label-print row and a price-change line.

A table of items and prices with neither is explicitly routed *back to the default*, in the node's own
recognition text. That is a signal that discriminates in both directions rather than a re-labelling.

Two further structures fire here that appear nowhere in the schema's nine and nowhere in
`business_operations`:

- **the PRICE-CHANGE structure** — a was/now pair with an effective-from, a scope and a reason. Its
  discriminator against `pos-reporting` is temporal direction: a Z-read records what price *was charged*
  across a completed session; this records what price *will apply* from a future instant, and carries no
  takings, no tender split, no till identity. Nothing else in the roster produces this shape.
- **the RANGE-PLAN structure** — a forward commitment in *physical sellable options* (colourway, size ratio,
  pack, intake units, launch and exit dates), which is what separates it from
  `business_operations.budget-forecast`, whose rows are money line items over fiscal periods. Money appears
  in both; only one of them can be worn.

So the answer to limb 1 of the charge is exact: the schema's work-type value *"product, range and price
record"* names the **function**; this row is not that function, it is the **structure of a versioned
population under a range**, and it declines the parts of the work-type string that belong to neighbours
(the word *listing* in that same string is `ecommerce-ops`'s, not this row's).

### Leg 2 — recommended dimensions

The schema's default, held as prose because PR-6 leaves it fieldless, is: the **trading unit** (conditional
on the corpus spanning more than one), then the **trading occasion**, then the **operational record
function**, not time-first.

This row cannot use the middle level *at all* — there is no occasion in a range plan. Its middle level is
the **effective version**. And the top level does not merely reorder, it **drops out**: a range is normally
common to the whole estate, so branching on site would split one range across every shop and produce the
exact fault the engine rejects — "The engine validates that the proposed template does not repeat a parent
dimension, create meaningless one-child levels, exceed practical depth limits, use an author or organization
merely as a collector, expose protected information, or produce empty branches when tested against the
accepted group." Site returns only where prices or assortments genuinely differ by store group, and then it
sits **below** the range, as a scope on a price version. Recommended shape: **RANGE/SEASON → EFFECTIVE
VERSION → FUNCTION.** Two of the default's three levels are replaced.

`time_first` is false, and this row must hold that line harder than its siblings because nearly every
artefact it holds is stamped with an effective date. The date **versions** the record; it does not root the
tree — "For document and record domains, project, function, or subject usually comes before time because
putting year first scatters related work across calendar folders." The exception is capture-based media —
"Photos and capture-based media are the major exception: time often belongs first because capture date is a
defining aspect of the material." — and product photography *is* capture-based media, which is the trap.
The resolution is that a delivered catalogue image is filed by **item**, not by capture; the shoot day,
where capture date really is defining, is `creative.commissioned-shoot`'s, on the reciprocal edge.

`dimension_order` is nonetheless serialised as `[]`. A dimension may only branch on a field the schema
declares, and it declares none. The recommendation lives in `template.why` as prose, exactly as the schema
anchor holds its own default. This is honest rather than convenient: the difference is real and unstorable,
and it is NJ-PC-1.

### Leg 3 — privacy rules

This is where the row **inverts** its schema rather than differing by degree, and it is the leg that would
justify the row on its own.

The family's declared posture is that its "ordinary, everyday, highest-volume output is PERSONAL DATA ABOUT
MEMBERS OF THE PUBLIC WHO HAVE NO RELATIONSHIP WITH THE HOLDER BEYOND ONE VISIT". This row holds almost none
of that. A range plan, a price list and a shelf-label run have **no data subject at all**. The fixture
`AW26 costs and margins - CONFIDENTIAL - do not circulate.xlsx` is marked confidential and contains not one
named individual.

The exposure is **commercial**: landed cost, supplier terms, margin, and above all an **unlaunched range**,
whose leak is a competitive harm rather than a privacy harm, frequently under a supplier confidentiality
obligation or a dated embargo. Two consequences follow that no sibling shares.

First, the discrimination is **intra-file and column-level**. One spreadsheet's description, image and
retail columns are *meant to be published* — this row's output is literally the operator's public face —
while the cost, margin, supplier and intake columns beside them must never leave the machine. A model step
for this row should therefore be offered column headers and a description sample only. "Privacy policy must
be enforced before content reaches any model or external connector."

Second, the row retains two small personal-data pockets that the general commercial posture must not be
allowed to hide: product photography containing an identifiable model or staff member where a usage release
may not exist, and copy or specification documents whose tracked changes name their authors.

`potentially_sensitive` is the only available value and it is correct, but the **reason** differs from the
schema's, and the reason is what governs handling. Handling classes remain P7's; the confidentiality legend
on the fixture is a literal observation, never a class.

**Verdict: three legs, three independent differences. The row stands, narrowed.**

## The collision fixture

`Trade price list 2026 - Bidfood.pdf`. It is the same document shape as this row's own
`Price list - trade + RRP - effective 2026-04-01.pdf`, the same extension, and it is frequently in the same
folder. Both are titled *price list*. Both are one row per line with codes, descriptions and money.

**What discriminates it: direction.** The supplier's list is *inbound* — the holder's **account number** in
a labelled slot, a minimum order value, a delivery-day schedule, case sizes, unit cost only, and **no
retail, RRP or margin column anywhere**. The holder's own list is *outbound* — the holder is the issuer, a
selling price exists. The determination is read from the letterhead, the account slot and the presence of a
selling price; it is never read from the words *price list*, because both documents carry them. That fixture
is what makes the schema's own `never_alone` rule about document-type words operative in this row rather
than merely quoted by it.

Second collision, restated from the schema: `Invoice 88231.pdf`. Priced line items, an issuer, a total.
No population, no version, no recurring key → Receipts and Confirmations.

## Files considered and rejected

- **`Screenshot 2026-04-02 at 09.14.11.png`, a phone photograph of a competitor's shelf.** OCR yields
  product names and prices — the row's two most tempting tokens — but no item key belonging to the holder.
  Rejected to **Reference Clips**, whose `00` definition names this material in the row's own vocabulary:
  "saved visual inspiration, **product references**, quotes, recipes, short article captures".
- **A downloaded consumer catalogue** (the holder shopping, not selling). Same shape, wrong side of the
  counter; the schema's operator-versus-customer determination governs, and it goes to Reading Inbox or
  Reference Clips. This row never activates from a catalogue the holder did not author.
- **A blank range-plan workbook, a wholesaler's specimen price list, a franchise manual extract.** Every
  header, every formula, no values — or values that are somebody else's. Live-versus-specimen is a
  `needs_llm` determination, and unresolved it goes to Review Later.
- **A planogram.** Tempting (products, prices, a printed face) and refused: it is a *rule about* shelf
  space, an instruction to a store, not a record of the range. It belongs to `retail_hospitality.store-operations`.
- **A promotion's artwork and point-of-sale design source.** `.indd` and `.psd` say the file is a design
  source and say nothing about whether the holder sells the thing depicted; that extension is in
  `never_alone` for exactly this reason. `creative`'s.
- **A supplier's product data sheet / spec sent to the holder.** Looks like this row's specification
  fixture; it is an input to qualification and ordering, not the holder's own selling record.
- **A `.ics` reminder for a range review meeting.** A `SOURCE_TYPE` and an event; nothing fires that the
  default would not.
- **A single dish photograph with no code.** One-Off Images. Merchandise is this row's subject, but a
  picture of merchandise is not this row's evidence.

## Reciprocal boundaries

All seven are written as objects carrying the same fixture on both sides, per the repaired edge shape.
Three restate a landed neighbour's own wording so the pair reads identically from either end.

| Neighbour | Same fixture | This row owns | Neighbour owns | Discriminator |
|---|---|---|---|---|
| `retail_hospitality.ecommerce-ops` | `products_export.csv` | the product as a thing sold | the listing as channel state | a publication-state column |
| `retail_hospitality.menu-recipe-costing` | `Spring menu 2026 - print final.pdf` | the atomic priced selling line | the cost model | the component explosion |
| `retail_hospitality.stocktake` | `stock_export_20260331.csv` | range and price reading | the recorded-belief half of a count | a sibling count artefact |
| `retail_hospitality.supplier-order` | `Trade price list 2026 - Bidfood.pdf` | the outbound price list | the inbound trade list | direction: issuer + selling price |
| `business_operations.product-requirements` | `Product spec v3.docx` | a thing with a code and a price | a behaviour with acceptance criteria | what is being specified |
| `logistics.warehouse-ops` | `item_master.csv` | selling attributes | handling attributes | price to a customer vs where it lives |
| `creative.commissioned-shoot` | `AW26_product_shoot/` | the delivered item-keyed asset | the shoot as a commission | item-key naming vs production apparatus |

Note on `menu-recipe-costing`: that row states honestly that being occasion-free separates neither row from
the other, since both are standing records. This memo agrees and does not use occasion-freeness against it —
occasion-freeness is this row's difference from **the schema default**, not from that neighbour.

Note on `warehouse-ops`: its research already ceded merchandise photography here and kept the *condition*
photograph of damaged stock. The edge is written to match, so no R1c repair is needed on that side.

## Neighbours considered that got no edge

- **`finance.small-business-bookkeeping`** and the wider `finance` family. Considered because
  `must_consider_neighbors` names finance and because this row is full of money. Refused: the schema's own
  `never_alone` already settles it — "A CURRENCY-DENOMINATED TABLE, standing alone. Money in cells is
  finance … before it is this." A price list has no account identity, no posting reference and no
  transaction; the genuinely confusable artefact is the lone invoice, and `00` sends that to a residual, not
  to a neighbour. An edge here would record a confusion that does not exist.
- **`business_operations.go-to-market`** and **`.market-research`**. A pricing-strategy deck or a
  competitor price study is *analysis about* a range, not the range record. Recognisable by argument
  structure and the absence of an item-key population. Left as a non-edge; if R1c finds a real
  same-fixture mutex it can add one without this row growing a marketing arm.
- **`retail_hospitality.pos-reporting`**. Argued inside the price-change signal rather than as an edge,
  because the two shapes never actually collide on one file: a Z-read has takings, a tender split and a
  till; a price-change file has none of the three.
- **`manufacturing.production-record`** / **`.spare-parts`**. Both hold part numbers and specifications,
  but neither prices an item to a member of the public. Different world, no shared fixture.
- **`photos.*`**. Coactivation-shaped, not mutex: a merchandise image without an item key is simply
  `photos`' or a residual's, and the `never_alone` rule already routes it there.

## Fields and proposed fields

`fields: []` and `proposed_fields: []`, both intentional. The `retail_hospitality` schema declares no field
rows (D1 as narrowed, `_CONTRACT` rules 10 and 15, PR-6), a template may reuse only its schema's fields, and
this row does not mint. Candidates were examined and all refused:

- a **range/season** key and an **effective-from** key are the two this row genuinely needs, and it proposes
  neither, because minting them here would put a schema-level field on a template. They are raised as
  NJ-PC-1 for R1c.
- `record_type` and `institution` are scoped to Finance; `project` and `artifact_type` to Research and Code;
  `purpose` to College Applications. None means *the season a selling line belongs to*.
- `site`, which the schema anchor itself proposes, is the schema's to ratify, not this row's to consume —
  and this row's argument is that site belongs *below* the range anyway.

`proposed_context_terms` are offered as **proposal** provenance and are recognition vocabulary only; they
mint nothing and `00` is not claimed to have listed them.

## Grouping without copied facts

Groups here are joined by the **item key**, never by the product's *name*, which repeats across ranges,
suppliers and seasons. Five grouping reasons are recorded; the one that matters most operationally is the
last: a repeatedly re-exported product file is a **version family, not a duplicate family**. Identical rows
under different effective dates are different records. This is the only row in the roster where getting that
wrong deletes the currently-effective price file.

Membership copies nothing. An image named `4821_front_white.jpg` joins a range group through key recurrence
and still carries no range, season or price fact — the schema declares none, so only the universal facts are
ever legal.

## NEEDS-JOSEPH

- **NJ-PC-1 — the unstorable anchor.** With no field rows, neither the range/season nor the effective-from
  date can be stored, so the leg-2 dimension recommendation is advisory only. Alternatives: (a) leave both
  detection-only and accept an unenforceable recommendation; (b) R1c proposes a range/season key and an
  effective-date key on the schema, which would make this the first row in the family able to serialise a
  dimension order; (c) borrow a canonical key — declined here, because none carries the meaning.
- **NJ-PC-2 — version family versus duplicate family.** Sharper here than anywhere else in the roster. A
  deduplicator that cannot see the effective date will delete the wrong price file. Alternatives: treat
  effective-dated files as an explicit version family, or exclude this row's material from duplicate
  collapse entirely.
- **NJ-PC-3 — the intra-file public/confidential split.** This is the one row whose material is *partly
  meant to be published*, and the product has no way to say "these columns are public, those are not". A
  whole-file conservative posture is chosen here; the alternative is a P7 column-level policy this row would
  then depend on.
- **NJ-PC-4 — the coactivation this row cannot author.** A printed catalogue or menu is simultaneously a
  trading record and a design deliverable, but `also_holds_with` is schema-to-schema only under CONNECTION
  §5 and this row is a template. Recorded for R1c as a candidate `retail_hospitality` ↔ `creative`
  schema-level edge. The `creative.commissioned-shoot` collision is the narrower, correct template-level
  statement available today.

## Recommendations for R1c (not made here)

Add the reciprocal halves on `supplier-order`, `business_operations.product-requirements` and
`creative.commissioned-shoot`, which have not yet argued against this row; the other four pairs are already
symmetrical. Rule NJ-PC-1. And consider whether the schema's `work_types[0]` string should shed the word
*listing*, which this row declines and `ecommerce-ops` holds — not edited here, it is not this row's file.

## Self-verification

- `python3 -m json.tool` parses the node; key set is **identical** to `retail_hospitality.json`'s.
- All **15** `“…”` spans in the JSON grep back out of `00` verbatim (`grep -c -F`, zero unverified).
- All **7** `collides_with` ids exist in `planning/domains/roster.json`; every entry is an object with
  `domain`, `signal` and `provenance`, and every signal names one fixture on both sides.
- Every `file_examples.source_type` is in `SOURCE_TYPES` (spreadsheet, text_document, image, ocr, archive).
- All seven `falls_through_to` names are `00` residual homes, each with a verbatim definition span.
- `fields`, `proposed_fields`, `also_holds_with`, `role_split` and `template.dimension_order` are empty by
  contract; `design_cite` is `null` (no span was verified as *licensing* the row, only as constraining it).
- No thresholds, no counts, no handling classes, no invented `00` clause.
- Files written: exactly the two assigned. No neighbour, roster, canonical-field, `src/` or shared file was
  opened for writing.
