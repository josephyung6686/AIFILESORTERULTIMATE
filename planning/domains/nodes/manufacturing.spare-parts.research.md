# Research memo — `manufacturing.spare-parts`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/manufacturing.spare-parts.json`
Roster row: template on the fieldless `manufacturing` schema, `parent_id: null`, placeholder launch

## Result

**Accept.** The row survives a serious charge and its identity turns out to be sharper than its name.
Its object is not a document called a spare parts list. Its object is **a standing balance** — a
per-item stock position, held against future equipment demand, carrying a reorder policy and a
used-on relation to a population of machines. Every other manufacturing template's object is an
**event**: a job, a batch, an inspection, a deviation, a calibration. This is the schema's only
row whose subject persists between events, and that difference is what makes it a node rather
than a value.

Four landed rows had already named it and drawn a boundary against it before this pass began. That
is strong external evidence the row is real: `retail_hospitality.stocktake`,
`manufacturing.maintenance-work-order`, `manufacturing.asset-register`, `logistics.warehouse-ops`
and `engineering.bill-of-materials` each reserved a seam for it, in each case with the same fixture
bytes named on both sides. This memo reciprocates all five in their own terms and adds three more.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the stamped R1b prompt for this id.
- `planning/domains/nodes/manufacturing.json` — the schema anchor. Read for its default template,
  `recognition`, `work_types`, `collides_with` and `proposed_fields`. Its default template prose and
  deterministic list are quoted below and are the measure of the node test.
- `planning/00-database-agent-product-design.md` — reached by targeted grep. Two spans used, both
  grep-verified verbatim before quoting (line 95 and line 45; see Quotes below).
- `planning/domains/canonical_fields.json` — full key list read; no key names a stocked item.
- Landed neighbours, read only where they named this row:
  `retail_hospitality.stocktake.json`, `manufacturing.asset-register.json`,
  `logistics.warehouse-ops.json` + memo, `manufacturing.maintenance-work-order.json` + memo,
  `engineering.bill-of-materials.json` + memo.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — depth calibration only.
- `planning/domains/roster.json` — every edge target grep-verified present.

## THE CHARGE — the strongest case that this row should not exist

I put six charges to the row. Two of them are genuinely dangerous and one is nearly fatal.

**1. It is a work_type value of its own schema. (Nearly fatal.)** The anchor's `work_types` list
contains, literally, `"asset register, spare-parts list or maintenance schedule"`. On the schema's
own account "spare-parts list" is an enumerated **value of a field**, which is exactly what the
dispatch forbids: *"Work types are values… Do not ask R1a for a child node per work type."* If a
row may exist because its documents are called spare parts lists, then `bin-card`,
`cycle-count-sheet` and `requisition` may exist too, and the manufacturing subtree becomes a
document-type taxonomy wearing node clothing. My sibling `manufacturing.maintenance-work-order`
put this identical charge on itself and named me inside it.

**2. It is a duplicate of `manufacturing.asset-register`. (Serious.)** Both are row sets of physical
things at a site, under headers Item, Description, Location, Status, Quantity. The landed
asset-register row admits the fixture is shared and admits *"item number and location alone
discriminate neither"*. If the discriminator is that thin, one row should hold both.

**3. It is a duplicate of `logistics.warehouse-ops`. (Serious.)** The warehouse-ops memo states the
charge against itself better than I can: *"A spares store is a warehouse by every physical
description: bins, item codes, quantities, issue notes, min-max levels, cycle counts. The bytes of
an issue note are near-identical."*

**4. It is a row defined by an ABSENCE.** A spare is conventionally defined negatively — not
installed yet, not for sale, not a raw material, not an identified asset. A row whose definition is
a list of what it is not can never activate, because absence is not evidence.

**5. It is a document type.** Bin card, count sheet, min-max report, requisition — these are names
of forms, and a row that is a bag of forms is a filing world invented to save an id.

**6. It is a duplicate of `retail_hospitality.stocktake`.** Counting inventory is counting
inventory; the industry of the counter is an organisation fact, and organisation names are
never-alone evidence.

### Defeating the charges

**Charge 1 falls to the event/position distinction.** A work type names *what a document is*. This
row's anchor is not a document — it is a quantity that persists across documents and that the
documents update. Spares master, cycle count, issue slip, min-max review and valuation extract are
five different work types, and they belong together because each reads or writes **the same balance
for the same item**. That is what makes a node: it produces a group no single work type could
produce, from evidence (`part` + on-hand + policy) rather than from a word. The failure case is the
contrast — a row called `cycle-count` would hold one work type and have nothing to group. The
anchor's `work_types` entry is a symptom of writing at schema altitude, not proof the subject is a
value.

**Charge 2 falls to cardinality.** An asset row has cardinality one and an **identity**: serial,
installed functional location, lifecycle obligation. A stock row has cardinality N and a
**quantity**: on hand, reserved, min, max, reorder point. You cannot count an asset or reorder an
identity. The landed asset-register row independently reached this same line from the other side.
The rotable case — a spare motor with both a serial and a bin — is not a counter-example but the
reason a `role_split` was authored instead of a merge.

**Charge 3 falls to what the store exists to serve, and it is readable.** A spares store's demand
documents point **inward** at equipment — asset identifier, work order, failure code — and its issues
are consumed on site; a warehouse's point **outward** at an order, wave and staging lane, and its
stock leaves intact. That is an observable column, not an industry label. Where the consuming
reference names neither, both rows agree neither fires and `Independent Records` holds the file.

**Charge 4 fails on inspection: the definition is positive.** The evidence is three co-occurring
positive structures — a balance-and-policy pair, a storage location, and a **used-on relation mapping
one item up to several machines**. That last is the strongest single discriminator here and its
direction is inverted from every neighbour: a bill of materials maps one product **down** to many
parts; a spares master maps one part **up** to many assets. No neighbour has a many-to-many
item→equipment relation.

**Charge 5 falls with charge 1.** The deterministic list requires column co-occurrence and explicitly
refuses the words spare, spares, stock, stores, bin and inventory as sole proof.

**Charge 6 falls to the population's purpose.** Goods held for sale, whose losses are spoilage and
shrink, against a population that exists to serve equipment. The tells are columns, not industries —
sell price, waste, usage on one side; used-on, reorder point, criticality on the other. A restaurant
stocking a spare compressor for its walk-in has both populations, and both rows fire on their own
evidence.

## The node test, all three legs

The manufacturing schema's **default template** is: `dimension_order: []` under PR-6, with prose
recommending *"product then batch/lot then record type for production and quality records; site then
asset then record type for maintenance and calibration; quality event then record type for NCR/CAPA
files."* Its default recognition is the twelve-item deterministic list quoted in the anchor. Measured
against that:

**Leg 1 — detection signals differ.** None of the anchor's twelve deterministic signals describes a
stock position. The closest is *"an asset register row set with stable asset identifiers, equipment
descriptions, site or line, service/calibration interval and status, where multiple rows prove a
controlled population rather than one purchase"* — and that signal belongs to
`manufacturing.asset-register`, whose subject is identity, not balance. The anchor's list contains
no on-hand slot, no reorder policy, no bin, no variance-against-system-quantity, and no used-on
relation. Every deterministic signal this row writes is new to the schema. The anchor also has a
`never_alone` entry that *cuts against* naive activation here — *"an invoice, purchase order,
packing list or delivery receipt alone; those are procurement/logistics evidence"* — and this row
extends it rather than contradicting it, adding that buying a part proves a transaction and not a
holding. **Passes.**

**Leg 2 — the recommended dimensions differ, and differ deliberately.** The anchor's maintenance
branch is *site then asset then record type*. This row recommends **site (as stocking location) then
part then record type, DELETING the asset level**. The deletion is the whole argument: a stocked item
serves many machines, so an asset parent would either duplicate one bearing under every machine that
takes it or force an arbitrary single parent, and either outcome destroys the only question a spares
corpus answers — do we hold this, and how many. The asset survives as a cross-reference, not a
parent. That is the inverse of every other maintenance-side row and cannot be obtained by reordering
the anchor. Record type stays at the leaf, because master row, count sheet, issue slip, valuation and
obsolescence notice all describe the **same** item; a record-type level would shred each item into
five folders. Governing rule: *"The recommendation should follow the practical rule that a parent
dimension should provide the context required to understand the child."* A variance of minus four is
unintelligible without the item, exactly as *"A work type such as Homework 3 is meaningful only after
the course is known."* `time_first` is false and unusually firmly so — the anchor's rows are dated
events, this row's subject is a **current** position, and a year level would file an item's live
balance under the year someone last counted it. **Passes; strongest leg.**

**Leg 3 — privacy differs, though less dramatically; I state that honestly.** The schema default
already covers commercial confidentiality and named workers. This row adds one disclosure no sibling
has: **a spares holding is an inference channel about fragility.** Which items are stocked deep,
flagged critical or held as insurance spares reveals what breaks and where a plant is weak, and a
used-on column enumerates the equipment population. One maintenance job leaks one failure; a spares
master leaks the shape of expected failure across the site. Valuation extracts add unit cost and
supplier pricing. A real difference in kind, but the weakest of the three legs — the row would pass
on legs 1 and 2 alone. No handling class is assigned; that is P7's.

**Verdict: accept.** Two strong legs and one moderate.

## Files considered and rejected

Tempting false positives, and why each is not this row's evidence:

- **`PO 45001982 - AX410 castings.pdf` and any parts purchase order or invoice.** Buying a part
  proves a transaction, not a held position. No balance, no policy, no bin. Procurement evidence;
  routes to `business_operations.procurement-sourcing` or the Receipts residual. The anchor's own
  `never_alone` already says so and this row inherits it.
- **`LOT-24-081_pick_list.csv`.** Part numbers, quantities and bins drawn from a store — but the
  Issued to column names a **product lot**. These items are consumed *into* an output, with genealogy
  back to the made article. `manufacturing.production-record` owns it. Kept as a file example
  precisely because it is the most seductive miss.
- **`Stocktake 2026-06-30 - Bar and cellar.xlsx`.** The collision fixture (below).
- **`Assembly parts list A-2201 rev C.pdf`.** Enumerates orderable parts with quantities, but carries
  a revision block and an approval slot for the item's definition. That is
  `engineering.bill-of-materials`, and the landed BOM row already named the seam.
- **`Maintenance manual - Model 40 Compressor.pdf`.** Describes how to service a machine and may
  contain a parts diagram. Evidences no owned asset, no holding and no performed work. The anchor
  puts this in `needs_llm` as an abstain case; it falls to Reading Inbox or Independent Records.
- **`Asset card CNC-07.pdf`.** One machine, one identity, a service history. `manufacturing.asset-register`.
- **A live stores or ERP database, or a stores mailbox.** A source system is not a file node. A
  bounded export with readable column headers is represented (`Stock export MB52_20260817.txt`);
  connector ingestion is a later security decision.
- **Supplier catalogues and price lists.** They enumerate purchasable parts but describe no holding
  of the holder's. Reference material, not stock records.
- **Warranty and returned-goods paperwork for a failed part.** `manufacturing.warranty-claim` on the
  roster; a core return that reconciles a balance is this row's, a claim against a supplier is not.

## The collision fixture

**`Stocktake 2026-06-30 - Bar and cellar.xlsx`.** It looks exactly like this row's evidence: a
per-item count sheet, quantities, a location, a variance implied between opening, purchases and
closing count. It is not this row's evidence.

**What discriminates it:** the columns Sell price, Waste and Usage, and the absence of any bin,
reorder point, used-on or equipment reference. The population exists to be **sold**, and its losses
are spoilage and shrink rather than consumption against a machine. `retail_hospitality.stocktake`
keeps it. Run the test in reverse and `Cycle count variance 2026-08 - Store 04.csv` — system qty,
counted qty, variance, bin, over stock codes with a used-on master behind them — comes to this row,
even though a naive column-shape match would put the two files in the same place.

A second, harder collision worth naming: **`Equipment and Spares Master.xlsx`**, one sheet holding
two populations under shared headers. Neither this row nor `manufacturing.asset-register` should
claim the file as a whole. It is marked `group_without_copying_facts: true` and routed to
`Review Later` if unresolved — the row's clearest statement that a single file may not have a single
anchor.

## Reciprocal boundaries

Eight `collides_with` entries, each an object carrying the same fixture bytes on both sides. Five
reciprocate an edge a landed row already authored; three are new.

| Neighbour | Shared fixture | Discriminator |
|---|---|---|
| `manufacturing.asset-register` | `Equipment and Spares Master.xlsx` | **Quantity or identity.** Balance + bin + reorder + used-on ⇒ mine; serial + installed functional location + lifecycle ⇒ theirs. Also a `role_split`, for rotables. |
| `manufacturing.maintenance-work-order` | `Parts issue slip WO-8814.csv` | Closes a stock balance ⇒ mine; charges a job via a Charged To column with no balance ⇒ theirs. Their wording, reciprocated. |
| `logistics.warehouse-ops` | an issue/pick note with codes, qty, bins | Demand points **inward** at an asset/work order/failure code and stock is consumed ⇒ mine; **outward** at an order/wave/lane and stock leaves intact ⇒ theirs. Names neither ⇒ Independent Records. |
| `retail_hospitality.stocktake` | a per-item count sheet with qty + location | Population serves **equipment** ⇒ mine; population is held for **sale to the public**, losses are spoilage/shrink ⇒ theirs. |
| `engineering.bill-of-materials` | `Spare Parts List - Model 40 Compressor.pdf` | Recommended-stock + order-code, addressed to a technician ⇒ mine; controlling revision block + approval slot ⇒ theirs. Relation direction also splits them: part **up** to many machines vs product **down** to many parts. |
| `business_operations.it-asset-inventory` | an IT stores extract with bins and quantities | Balance-and-policy ⇒ mine; assignee, build state or lifecycle date ⇒ theirs. A shelf of spare keyboards with a reorder point is genuinely arguable ⇒ Review Later. |
| `business_operations.procurement-sourcing` | `Obsolescence notice - drive controller DX-22.eml` | Settles a **transaction** ⇒ theirs; settles a **balance** (last-time-buy quantity computed against equipment population) ⇒ mine. |
| `manufacturing.production-record` | `LOT-24-081_pick_list.csv` | Consumption reference is a **product lot** ⇒ theirs; an **asset**, plus a reconciled balance ⇒ mine. |

**`role_split` — one, against `manufacturing.asset-register`.** A rotable unit (spare motor, pump,
gearbox) occupies two roles across its life on different handles: in stock it is a fungible line with
a quantity and a bin, keyed on the proposed `part`; installed it is an identified unit with a serial
and a functional location, keyed on the schema-proposed `asset`. The rotation is real and repeats, so
neither side may copy the other's handle onto its rows.

**`also_holds_with: []`.** CONNECTION §5 makes schema↔schema coactivation the only legal content and
this row is a template, so it authors none. **Recorded for R1c:** `Spares valuation 2026-06-30.xlsx`
is a genuine dual-schema file — stock-position slots and accounting slots in the same bytes — and the
`manufacturing` ↔ `finance` coactivation belongs on the schema anchor, not here. The fixture carries
`also_schema: "finance"` so the case is not lost.

## Neighbours considered that did NOT get an edge

- **`manufacturing.calibration-record`** — an instrument is an asset, not stock; no shared fixture.
  The asset-register collision already covers the identity seam.
- **`manufacturing.failure-analysis`** — consumption history is input to a failure argument, but a
  usage column is not a cause. Reasoning from a population ⇒ theirs; holding a balance ⇒ mine. No
  same-evidence file was found, so no edge was forced.
- **`manufacturing.supplier-qualification`** — an approved-supplier list is not a holding.
- **`engineering.change-order`** — a supersession changes what to stock, but the change document
  itself carries from/to revisions, not balances. Adjacent, not confusable.
- **`logistics.fleet-vehicle`** — vehicle parts stock is real but is a straightforward instance of
  this row's own structure, not a competing claim; if a landed fleet row later shows a genuine mutex,
  R1c can add it.
- **`finance`** — a coactivation, not a mutex. Handled above.

## Fields and dimensions

`fields: []` and `dimension_order: []` are correct and intentional under PR-6 and D1's standing
deferral. One `proposed_fields` entry:

- **`part`** — no canonical key names a fungible stocked item. The schema-proposed `product` is the
  article being **made**; a spare is consumed. The schema-proposed `asset` is one identified machine
  and cannot carry a quantity. `record_type` names the document. `artifact_type` and `project` are
  scoped to research and code. `reliability_ceiling: possible` — a stock code usually sits under a
  labelled header, but part-number-shaped tokens are indistinguishable from drawing, order and serial
  numbers outside a slot; confirmation needs a column-header-plus-quantity-context rule family, and
  this row writes no regex.

I deliberately reused neighbours' existing proposals rather than minting variants: `asset` and `site`
come from the schema anchor, `work_order` from `manufacturing.maintenance-work-order`. A bin is not
proposed as a field — it is too fine for a folder level and belongs in search.

## Quotes used (all grep-verified verbatim before quoting)

From `planning/00-database-agent-product-design.md`, line 95: *"The recommendation should follow the
practical rule that a parent dimension should provide the context required to understand the child."*
· *"A work type such as Homework 3 is meaningful only after the course is known"* · *"For document and
record domains, project, function, or subject usually comes before time because putting year first
scatters related work across calendar folders."* From line 45: *"A session should never be treated as
proof of topic"*. No `design_cite` is written on the node, because none of these spans is about this
domain specifically and a decorative cite is worse than none.

## NEEDS-JOSEPH

1. **NJ-SP-1 — who gets the word `part`.** Engineering may want it for the revision-controlled design
   item. Alternatives: (a) this row takes `stock_item` and engineering takes `part`; (b) one `part`
   key shared, with the stock/definition roles separated by a role split; (c) both defer and the
   concept stays search-only. This row proposes `part` and will yield to (a) rather than mint a
   variant of both.
2. **NJ-SP-2 — should the rotable role split be canonical?** The same stock-versus-identity rotation
   recurs in IT assets and fleet parts. Alternatives: keep it as a per-row `role_split` in three
   places, or ratify one pattern and have the rows reference it.
3. **NJ-SP-3 — stocking location versus `site`.** One plant may run several independent storerooms
   whose balances must not merge, so `site` may be too coarse to be the top dimension. Alternatives:
   overload `site`; propose `storeroom`; or leave it a search-only observation and let the top level
   be `part` for every holder.
4. **NJ-SP-4 — the mixed-population file.** `Equipment and Spares Master.xlsx` has two anchors in one
   sheet. P6/P8 need a rule for whether row-level activation is permitted at all, or whether such a
   file must abstain to `Review Later` as this row currently routes it. The asset-register row raised
   the same question from its side; it should be answered once, for both.

## Self-verification

`python3 -m json.tool` parses. All nine edge targets (`manufacturing.asset-register`,
`.maintenance-work-order`, `.production-record`, `logistics.warehouse-ops`,
`retail_hospitality.stocktake`, `engineering.bill-of-materials`,
`business_operations.it-asset-inventory`, `.procurement-sourcing`, plus the `finance` `also_schema`)
grep-verified present in `roster.json`. Every `collides_with` and `role_split` entry is an object with
`domain`, a both-sides signal naming the same fixture, and `provenance` — no bare id strings.
`also_holds_with` is empty, per CONNECTION §5 for a template. Every `falls_through_to` name is one of
`00`'s nine residual homes. Every `file_examples.source_type` is in `SOURCE_TYPES`. No file example
writes a folder path as a fact; three carry `group_without_copying_facts: true`. No threshold numbers,
no handling classes, no fabricated quotes. `fields: []`. Key set matches the landed manufacturing
siblings including `proposed_context_terms`. Only the two assigned files were written.
