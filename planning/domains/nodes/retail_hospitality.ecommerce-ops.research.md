# Research memo — `retail_hospitality.ecommerce-ops`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/retail_hospitality.ecommerce-ops.json`
Roster row: template on the fieldless `retail_hospitality` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accept**, and accept it on a narrower and more structural basis than the roster hint describes. The
hint reads as a list of channel artefacts ("channel listings, order and customer exports, fulfilment
records, platform settings and the marketing data behind them") and a list of artefacts is exactly
what a refusal is made of. The row survives because underneath that list sits one structure no
sibling and no neighbour holds: **a REMOTE STATE MACHINE in a platform's identifier namespace** —
published/unpublished on the listing side, paid/refunded and unfulfilled/partial/fulfilled on the
order side — and, on the order side, a **delivery address on every row**. Physical retail has no
publication state (a shelf is either stocked or not), no fulfilment state (the goods left with the
buyer), and no address (the buyer carried them home).

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `also_holds_with: []`. What this row
actually contributes is recognition, a recommended prose order that differs from its schema's
default in two arguable ways, and a privacy rule that contradicts its schema's default and is better
than it.

## The charge — the strongest case that this row should not exist

I ran the charge in six forms before writing anything. Five are real and four of them nearly landed.

**1. It is a MEDIUM, and a medium is not a filing world.** This is the strongest form. "E-commerce"
names the *channel through which* trading happens, not a different thing traded. The schema anchor's
own defining never-alone says trading in a sector is a field value — and worse than that, the schema
anchor literally names this row's subject as a *value of one of its proposed keys*: `site` is
proposed with the example "the online channel `Shopify - UK store`". A row whose entire identity is
one value of one field is the 574's original mistake in its purest form.

*Defeated, but only partly, and the partial defeat is the honest answer.* A value of `site` would
produce the same records as the other sites with a different label on them. That is not what
happens. Three of this row's structures have no counterpart at any physical site: a publication state
(a listing can exist and be invisible; a shelf cannot), a fulfilment state machine (a physical sale
has no interval between payment and delivery in which a record must track where the goods are), and
a promisable-stock column set (available/committed/incoming, where *committed* means reserved against
orders that have not shipped). Conversely the physical siblings hold structures this row cannot
produce at all: there is no drawer to reconcile, no over/short, no session, no covers, no licensable
activity, no fridge. Two worlds that each hold structures the other cannot produce are not one world
with a field value distinguishing them. **What survives of the charge, and I record it rather than
bury it:** the *catalogue* half of this row genuinely is the physical catalogue plus a state column,
which is why `retail_hospitality.product-catalogue` gets the sharpest reciprocal edge in the file
and why the boundary is drawn on that single column rather than on the file.

**2. It is a duplicate of four siblings, assembled by channel.** Listings = `product-catalogue`
online; order exports = `pos-reporting` online; fulfilment = `supplier-order`/`warehouse-ops` online;
returns = `returns-warranty` online. A union of four neighbours differing only in the platform the
export came off is a duplicate, not a node.

*Defeated by asymmetry, in both directions, on named fixtures.* `pos-reporting` is keyed to a TILL
and a SESSION; this row has neither, and the reason is structural rather than incidental — the
storefront never closes, so the schema's whole "trading occasion" level has no e-commerce member.
`stocktake` is built on a counted-versus-system pair with a count date; a promisable-stock export has
no counted column and no count date, because nobody counted anything. `returns-warranty` is built on
a return-authorisation identity separate from the order identity; a refunded row in an order export
has no such identity. `product-catalogue` is built on cost, margin, supplier and range; a listing
export has none of those and has publication state, variant matrices and SEO slots instead. Each of
those is a column-level test I can state in both directions, which is the form a real boundary takes
and a duplicate cannot.

**3. It is a file format and a vendor name.** `.csv` and `.json` off a named SaaS platform. If the
row rests on "Shopify emits these files", it rests on `SOURCE_TYPES` plus an organisation name, both
never-alone.

*Defeated by construction, and the JSON encodes the defeat.* Both the platform brand and the
export-shaped filename are written into `never_alone`, and both are true of the row's collision
fixture — a buyer's own `Your Orders - amazon.com - 2026.csv` carries a marketplace brand in its
filename and is not this row's. Nothing in `deterministic` names a vendor. Every entry is a column
set or a schema-key set.

**4. It is defined by the ABSENCE of a premises.** No till, no covers, no licence — "retail_
hospitality minus everything physical". A row defined by absence cannot activate.

*Defeated, but this one deserved the scrutiny.* The row is written on positives only: state
machines, committed quantities, zone-and-rate tables, per-page addressee blocks. The absences appear
only as *discriminators against named neighbours*, which is where absences legitimately belong.

**5. It is a lifecycle stage.** "Order lifecycle" sounds like exactly the stage-shaped refusal the
brief warns about. *Defeated:* the lifecycle is not the row's scope, it is the row's evidence — the
row does not hold "the fulfilment stage of trading", it holds the record in which a state slot is
carried, whatever state that slot happens to read. A row scoped to a stage would exclude the
unfulfilled rows; this one includes them because the slot is the signal.

**6. It is a duplicate of its own schema's default template.** Handled in full below; it is the leg
this row passes least comfortably and the one I would most want R1c to re-test.

## The node test, all three legs

The schema's default template is held as prose because PR-6 leaves `retail_hospitality` fieldless.
Verbatim from the anchor: *the TRADING UNIT — site, venue or channel — ONLY where the corpus
genuinely spans more than one, then the TRADING OCCASION — the session, count, order cycle, booking,
function or licensed premises the material belongs to, then the OPERATIONAL RECORD FUNCTION. Trading
period sits INSIDE the occasion level, never above the site. NOT TIME-FIRST.*

**Leg 1 — detection signals differ.** The schema lists ten deterministic structures. None of them is
a listing-publication state, an order state machine, a promisable-stock column set, a
storefront-configuration key set, or a per-page-addressee dispatch batch. The nearest is the
schema's ORDER-CYCLE structure — but that is *inbound*, keyed to the operator's own purchase order
against a supplier, and closes with a goods-received note and a credit note. This row is *outbound*,
keyed to a platform-issued order identifier against a consumer, and closes with a tracking number.
They share the word "order" and no columns. Five new structures, argued individually in the JSON.

**Leg 2 — dimension order differs, in two ways.** (a) The channel level is **unconditional** where
the schema makes the trading unit conditional. The schema's reason for conditionality is that a
single-shop operator gains a one-child branch naming their own shop; that reasoning does not
transfer, because multi-channel is the ordinary case, the order-identifier **namespaces collide**
across channels (the same `#1042` exists on two systems and means two different buyers), and the
same catalogue carries different prices, titles and category codes per channel. I state the honest
limit in the JSON: where a merchant truly has one channel the level collapses and the
recommendation degrades to the schema default. (b) The occasion level has **no member here**. There
is no session, no count, no booking, no function. What replaces it is an **export window** — an
arbitrary date range chosen by whoever pulled the report. That is a different kind of second level,
not a relabelling of the same one.

**Leg 3 — the privacy rule differs, and contradicts the schema's.** The schema's posture rests on
the claim that the family *"CANNOT BE SEPARATED into a safe half and a sensitive half at recognition
time"*. That is false for this row and usefully so: the corpus separates from the header row alone.
Products, inventory, settings, shipping rates and ads exports contain **no person at all**; orders,
customers, subscriber lists and packing-slip batches contain a **full delivery address on every
row**, by construction. That is a stronger and more actionable rule than the schema's, and it cuts
both ways — this row must not be blanket-protected either, or a shipping-rate table gets locked for
nothing. The value stays `potentially_sensitive` (the only non-`none` value the dispatch allows); it
is the rule that differs, which is what leg 3 asks for.

The row passes all three. Leg 2(a) is the weakest: it depends on R1c ruling that a channel is
keyable at all (NJ-EC-1). If R1c rules it is not, this row still passes on legs 1 and 3, and I say so
rather than pretending the leg is safe.

## Files considered and rejected

Named false positives, each with why it is not this row's evidence.

- **`Your Orders - amazon.com - 2026.csv`** — the collision fixture; see below.
- **`Settlement report 2026-03 - marketplace.txt`** — a real, tempting, order-keyed file whose lines
  join exactly to this row's order export. It is `finance.small-business-bookkeeping`'s. The schema
  anchor had already fenced this row on it ("RETAIL_HOSPITALITY MUST NOT TAKE ... a merchant
  settlement statement"), and this template accepts the fence instead of arguing it back. It stays in
  `file_examples` precisely as a rejection.
- **A theme export / `.liquid` templates / `package.json`** — `code.software-project`. Repository
  markers decide. A store archive containing *both* a settings file and a theme directory does not
  become code because one member is code.
- **A Squarespace or Wix site backup for a brochure site that sells nothing** — no listing state, no
  orders, no rates. Not a trading record at all; Review Later or code.
- **A supplier's specimen product feed and a scraped competitor catalogue** — byte-identical to a
  live feed. `business_operations.market-research` for the competitor pull; a specimen is a template,
  and the schema's own `needs_llm` already names "a supplier's sample" as the live/specimen problem.
- **A demo-store seed export** — a real artefact of every store build, and undetectable from
  structure. Routed to the same live/template determination; abstention where unresolved.
- **A dropshipping course PDF or a "build your first store" guide** — Reading Inbox. It talks about
  every structure this row detects and contains none of them.
- **A carrier's tracking export or proof-of-delivery file** — `logistics.shipment` /
  `logistics.last-mile-pod`. A tracking number is this row's evidence only as a *column inside* an
  order-keyed record; a file keyed on consignments is theirs.
- **A `customers.vcf` address-book export** — contacts source type, and 00 is explicit that contact
  formats "should normally be privacy-protected rather than used to create folder proposals". Not a
  trading record.
- **A bank or PSP statement for the store's account** — finance, on account identity.

## The collision fixture

`Your Orders - amazon.com - 2026.csv` — a buyer's own order-history download.

It is an order export CSV. It has order identifiers, dates, item titles, quantities, prices, a
shipping address, and a marketplace brand in its filename. On filename, extension, source type and
half its columns it is indistinguishable from this row's primary fixture.

**What discriminates it, stated positively:** the **cardinality of the recipient**. The buyer's
export carries ONE recipient (the holder) across MANY selling merchants; the merchant's export
carries MANY recipients across ONE store. Secondarily, the buyer's file has **no operating
apparatus** — no fulfilment-status column, no payment-gateway column, no fee, no payout, no discount
code, because the buyer was never responsible for any of those. This is the schema's operator/guest
role split applied to a counter where the two sides never meet, and it is sharper here than anywhere
else in the family, because the **same platform generates both sides' files with the same default
filenames**. Where the evidence does not settle the side, this row must not activate, and the file
routes to Receipts and Confirmations, which names "purchase receipts" by design.

## Reciprocal boundaries

Nine `collides_with` entries, every one an object carrying a SAME-FIXTURE-BOTH-SIDES signal naming
one real file and the discriminating evidence item. Summarised by fixture:

| Fixture both sides claim | This row owns | Neighbour owns | Discriminator |
|---|---|---|---|
| `products_export.csv` | listing as channel state | `product-catalogue`: product as thing sold | publication-state column |
| `Sales by day March 2026.xlsx` | channel read (sessions, orders, AOV) | `pos-reporting`: session read (tender, over/short) | drawer reconciliation |
| despatch report with order nos. + picker col. | keyed on customer order | `logistics.warehouse-ops`: keyed on facility work | order-order vs location-order |
| `Settlement report ... .txt` | order-level operating read | `finance.small-business-bookkeeping`: fee/payout/ledger | account identity + fee structure |
| `store-export-2026-03.zip` | storefront configuration | `code.software-project`: theme as software | repository markers |
| `inventory_by_location_...csv` | promisable stock | `retail_hospitality.stocktake`: counted stock | counted-vs-system pair |
| refund line in orders export | refund as order state | `returns-warranty`: return as its own case | separate RMA identity |
| `customers_export.csv` | channel customer population | `business_operations.customer-account-management`: named B2B account | relationship apparatus per row |
| `Ads - campaign performance ... .csv` | spend against store revenue | `creative.ad-campaign`: campaign as commissioned work | creative + approval apparatus |

**One reciprocal already existed and I accepted it unchanged.** `logistics.warehouse-ops` is the only
landed row that had argued a boundary against this id, and it argued *for* it, writing: "The
discriminator is whether the record is keyed on the CUSTOMER ORDER or on the FACILITY'S WORK." I
endorse that verbatim rather than restating it in my own words, and add only the case it did not
cover — a packing-slip batch with no bin, wave or picker column anywhere is wholly this row's. A
neighbour independently needing this row to exist in order to draw its own boundary is the single
best piece of evidence against the refusal case, and it is external to my own reasoning.

**Neighbours considered that got no edge.** `business_operations.market-research` (segment and
competitor studies — real seam, but the row keys differ so completely that no single fixture is
contested); `manufacturing` (`product` and `site` are shared *proposals*, not shared evidence — the
schema anchor already holds that seam and a template restating it would suggest a contest where
there is agreement); `photos.screenshot-captures` and `photos` generally (coactivation, not mutex —
recorded on the screenshot fixture as `also_schema`); `logistics.shipment` (a carrier's consignment
record never overlaps an order export's *bytes*, only its subject matter); `identity` and `hr` (this
row's people are consumers, never staff or the holder).

## `also_holds_with` — deliberately empty

CONNECTION §5 makes `also_holds_with` schema↔schema only, and this row is a template. The
coactivations I found are recorded as `also_schema` on individual fixtures instead — `finance` on the
order export and the settlement report, `photos` on the admin screenshot — and the schema-level
intent is recorded **here, for R1c**: `retail_hospitality ↔ finance` on a store export carrying both
an order population and a payout reconciliation (the schema anchor already authored this one-way);
`retail_hospitality ↔ code` on a store archive carrying both a settings file and a theme directory,
which the schema anchor did **not** author and which R1c should consider adding.

## Fields and dimensions

`fields: []` by contract — the schema owns fields and declares none.

`proposed_fields: []`, **deliberately**, and this is the memo's main recommendation to R1c. The
tempting mint is `channel`. I declined it. The schema anchor already proposed `site` with an online
channel as an example value and explicitly deferred the ruling — *"NOT YET SETTLED: whether an
e-commerce channel is a `site` at all, since it has no physical location; this row's reading is that
a channel is a trading unit in the same sense and should be admitted, but R1c owes the ruling and
`retail_hospitality.ecommerce-ops` depends on it."* My job as the named dependant is to supply the
evidence for that ruling, not to pre-empt it with a variant key that would seed exactly the synonym
family (`store`, `outlet`, `channel`, `storefront`) the canonical list exists to prevent. The
evidence and the three alternatives are in `open_question` as NJ-EC-1. `role_split` carries
`site`/`channel` as a pair so R1c adjudicates two roles rather than one word.

`dimension_order: []` follows from `fields: []`. The recommendation lives in `template.why` as prose,
stated against the schema default so the difference is auditable rather than asserted.

## NEEDS-JOSEPH

- **NJ-EC-1 — is an e-commerce channel a `site`?** The ruling the schema anchor deferred and named
  this row as dependant on. Evidence: a channel behaves like a site in every structural respect that
  matters to a template (records keyed to it, unique identifier namespaces, per-channel prices and
  titles, corpora spanning several) and unlike one in exactly one respect (no location).
  Alternatives: (a) widen `site` to "the trading unit or selling surface" — **preferred**, costs one
  word; (b) mint `channel` — declined here, seeds a synonym family and forces bricks-and-clicks
  merchants to carry two keys for one top level; (c) rule a channel unkeyable — survivable, but this
  row's recommended first dimension is then unavailable and it degrades to the schema default plus
  its privacy rule.
- **NJ-EC-2 — the export window.** The schema's NJ-RH-5 asks whether `record_period` may be
  *sub*-daily (a lunch service). This row needs the **opposite** stretch: an arbitrary user-chosen
  date range with no operational meaning, because whoever pulled the report chose the dates. If
  `record_period` must be a natural period, this row's second dimension has no key and the
  recommendation collapses to channel-then-function. R1c should answer both stretches together —
  they are the same key being pulled in two directions by two children of one schema.
- **NJ-EC-3 — the marketing seam.** Drawn here on a discriminator I can state but not prove: a
  performance export keyed on this store's own product handles is this row's; a brief and its assets
  are `creative.ad-campaign`; a segment study is `business_operations.market-research`. A blended
  agency report containing a ROAS table *and* creative thumbnails satisfies no test cleanly.
  Alternatives: cede marketing entirely and drop the work_type, or keep the seam and accept that
  blended reports route to Review Later.
- **NJ-EC-4 — subscriber and consent data.** A marketing list export carrying consent state is
  arguably a compliance record rather than a trading one, and no landed row claims it. Alternatives:
  this row; `business_operations.customer-account-management`; or a privacy-only route straight to
  Protected Records with no domain claim.
- **NJ-EC-5 (inherited, restated with a fixture).** The schema's NJ-RH-4 asks whether the mechanism
  forcing P7 ahead of a model path reaches third-party personal data in a row that does not carry
  `is_safety_domain`. This row supplies the concrete case the schema could only gesture at: a single
  `orders_export.csv` is a structured consumer address database with a name, email, telephone, full
  postal address and gateway token per row, in a template that is not a safety domain.

## Self-verification

- `python3 -m json.tool` parses the node file; key set matches the landed siblings.
- Every `00` quotation grep-verified verbatim before use (10 distinct spans, each `grep -c` = 1).
- Every `file_examples.source_type` is in `SOURCE_TYPES`; every edge id confirmed present in
  `planning/domains/roster.json`; every `falls_through_to` name is one of 00's nine residuals.
- No thresholds, no statistics, no handling classes, no `public_low`, no fabricated quotes.
- `also_holds_with` empty per CONNECTION §5 (template row); every `collides_with` entry is an object
  with a same-fixture-both-sides signal.
- Two files written, both mine. No neighbour node, roster, canonical field, `check.py`, `src/` or
  SPEC touched.
