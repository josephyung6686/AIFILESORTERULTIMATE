# Research memo — `retail_hospitality.stocktake`

Depth: J-DEPTH
Date: 2026-08-27
Output: `planning/domains/nodes/retail_hospitality.stocktake.json`
Roster row: template on the fieldless `retail_hospitality` schema, `parent_id: null`, `launch: placeholder`

## Result

Accept the node. It survives the charge on all three legs of the CONNECTION §2 test, but only narrowly on one of them, and the leg it nearly failed is recorded as NJ-RH-STOCK-1 rather than smoothed over.

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `also_holds_with: []`, `role_split: []`, `time_first: false`. Eight `collides_with` entries, all written as objects naming a fixture on both sides.

## The charge — the strongest case that this row should not exist

I put five prosecutions to the row before writing anything. Two of them are serious.

**1. It is a work_type value.** This is the strongest charge and it is made by the schema itself. `retail_hospitality.json` lists, in `work_types[]`, verbatim: `"stock record - count sheet, variance report, wastage log, allocation, transfer"`. Every artefact I would claim is enumerated there as a *value* of a function dimension. The schema also wrote its own never-alone rule against exactly this move: *"A DOCUMENT-TYPE WORD, standing alone - invoice, rota, log, price list, order, review. These are values of a function dimension, and a row resting on one is the schema's default template wearing a name."* If `stocktake` is the word "count sheet" promoted to a node, the row is the 574's original mistake reproduced inside a family that already warned against it.

**Defeat.** The charge conflates the *documents* with the *situation*. A work_type value files a count sheet as one document of one type. What this row recognises is a **count event**: a dated, bounded, repeatable act of enumeration over a defined population at a defined location, whose output is structurally never one document. The minimum readable unit is a **pair** — the instrument (a ruled sheet, blank or completed, sometimes a photograph of a clipboard) and the result (a variance report or valuation) — plus a continuous loss log that belongs to the interval between two counts and to neither exclusively. No other sibling in this family requires two structurally dissimilar artefacts to be intelligible: an end-of-day read is complete on its own, a booking confirmation is complete on its own, a licence grant is complete on its own. The schema's own `grouping_reasons` concedes the point in its own words — *"ONE COUNT: the count sheets, the variance report and the wastage log for one location on one count date"* — which is a grouping situation, not a document type. A `work_type` field value cannot express that a blank form and a signed PDF are one thing.

**2. It is a lifecycle stage of `retail_hospitality.supplier-order`.** Goods are ordered in, held, counted, sold. On this reading the count is just the "held" phase of the ordering cycle and belongs on the order row.

**Defeat.** The two are distinguished by *scope and counterparty*, and the distinction is visible in the header block of every fixture. An ordering record is bounded by one consignment, one named supplier and one order reference; a count is bounded by a population, a location and a date, and names no counterparty at all. The stage reading also gets the direction wrong: a count is not a stage the goods pass through, it is an act performed *on the whole population at once*, mixing goods from many order cycles and many suppliers, and its variance cannot be attributed to any one of them. This is nevertheless the row's sharpest same-family seam and it is recorded reciprocally (NJ-RH-STOCK-3) because `supplier-order` has not landed.

**3. It is a duplicate of `logistics.warehouse-ops`.** Both count things in rooms.

**Defeat, and the neighbour landed it first.** `logistics.warehouse-ops.json` already authored the seam against me from its side, and I adopt its wording rather than inventing a competing one. Its `collides_with` entry reads: *"a valuation, unit-cost or retail-price column and an ownership premise mark a stocktake, while a bin-location, put-away, pick and book-out sequence marks a custody log"*, and it names the fixture pair — it carries `Stock valuation 2026-03-31.xlsx` as its *negative* fixture, handing it to me, and keeps `Cycle count variance 2026-W16 - Zone C.xlsx` with *"the valuation columns deliberately absent"*. Its deepest reason is a premise difference and I accept it verbatim as the boundary: a stocktake counts what a business **owns** in order to value it; a warehouse record moves goods that are frequently somebody else's.

**4. It is a duplicate of the schema's default template.** The schema's `recognition.deterministic` already contains a COUNT-AGAINST-BOOK signal, and the schema's exemplar fixture is literally `Stock count W12 2026 - counted vs system.xlsx`. If the family already detects counts, what does the template add?

**Defeat — this is the leg the row passes least comfortably, and the argument is dimensional and privacy-based, not detection-based.** The schema's detection list is a family-level OR of six structures; owning one branch of an OR is not by itself a template. The real differences are the other two legs, argued in full below. I record honestly that if NJ-RH-STOCK-1 resolves against the count-location level, the dimensional leg fails and the row would rest on pair-grouping and privacy alone. It would still stand, but by a thinner margin than this memo would like.

**5. It is a row defined by absence** (stock that is *missing*). Rejected quickly: a count with zero variance is still a count, and the row's strongest signal is the presence of *two* quantities, not the absence of any.

## The node test, all three legs

CONNECTION §2: a template exists only where its **detection signals**, **recommended dimensions**, or **privacy rules** differ from its schema's default.

**The schema's default template, stated so the difference is measurable.** `retail_hospitality.json` holds it as prose because PR-6 leaves the family fieldless: *"the TRADING UNIT - site, venue or channel - ONLY where the corpus genuinely spans more than one, then the TRADING OCCASION - the session, count, order cycle, booking, function or licensed premises the material belongs to, then the OPERATIONAL RECORD FUNCTION. Trading period sits INSIDE the occasion level, never above the site. NOT TIME-FIRST."*

**Leg 1 — detection. Differs, but by narrowing plus one addition.** The family signal is COUNT-AGAINST-BOOK. This row sharpens it to an arithmetic relationship between three columns — a counting word, a believing word, and their difference — which is deliberately not a keyword rule, because the row's constitutional never-alone is the word "stock" itself. It adds two signals the schema does not name: the **instrument shape** (a ruled sheet with an *empty* quantity column and initial slots, which fires as a count member carrying no data at all) and the **loss-reason enumeration** (spoilage, ullage, breakage, staff meal, comp, shrink), which is the surest discriminator in the row and appears nowhere in the `business_operations` family. I count this leg as passed but not decisive on its own.

**Leg 2 — dimensions. Differs by one inserted level.** Recommendation: trading unit (conditional, on the schema's terms) → **count event** → **count location** → function. The count-location level is the entire difference and it is defensible for a reason unique to this row: a count is executed as several *simultaneous enumerations of disjoint populations* — cellar, bar, kitchen, dry store — each with its own sheets, counter and variance. No other occasion in this family subdivides by room; a session belongs to a till, a booking to a date, a licence to a premises. Flattening puts four unrelated ruled sheets in one pile at the moment the user is asking which room was short. The level is conditional for the same reason the site level is, and for the reason `00` gives: *"The engine validates that the proposed template does not repeat a parent dimension, create meaningless one-child levels, exceed practical depth limits, use an author or organization merely as a collector, expose protected information, or produce empty branches when tested against the accepted group."*

Two levels are forbidden outright, both tempting here specifically: **product/SKU** (a branch per line over thousands of lines) and the **counter's or approver's name** (a staff-facing loss branch published into the directory tree).

`time_first: false`, and this row is the family's hardest test of that rule. A count is *named* by its date, and its date is a fiscal date that budget, payroll and accounts material shares. The date identifies the event; it does not root the tree — *"For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."* A count-cycle comparison series is a content period, not a capture date, and the exception belongs to media. The order stays advisory: *"The system recommends an order based on the domain template, but the user can reverse, remove, add, or flatten dimensions."*

**Leg 3 — privacy. Differs by inversion, and this is the row's cleanest pass.** The family's posture exists because its highest-volume output is personal data about members of the public — reservation exports, dietary and allergen notes, check-in identity scans. A stocktake corpus contains essentially none of that; the family's guest rule still applies and protects nothing here. What this row carries instead is (a) commercial confidentiality of a kind the family otherwise meets only in costing — unit cost, margin, supplier buying terms, a closing valuation feeding the accounts — and (b) **staff-facing allegation-adjacent data**: a variance is a statement that something is missing, recorded beside the names of whoever counted, checked, authorised the write-off, and whichever department was short. Unlike guest data, these are people in a continuing relationship with the holder. Operative consequences are serialised in `sensitivity_why`. Sensitivity is `potentially_sensitive`; no handling class is assigned — that is P7's vocabulary.

Verdict: three legs, two of them decisive, one honest-but-narrow. Accept.

## Sources used

`planning/domains/dispatch/RESEARCH-BRIEF.md`; the stamped assignment via `make_prompt.py`; `planning/domains/nodes/legal.practice-matter-file.research.md` as the depth calibration; `planning/domains/nodes/retail_hospitality.json` (the schema anchor — `template`, `recognition`, `work_types`, `grouping_reasons`, `never_alone`, `sensitivity_why`, `falls_through_to`, `proposed_fields`); `planning/domains/roster.json` (sibling ids and neighbour-id verification); the two landed rows that had already argued a boundary against this id, found with a single `grep -rl` — `logistics.warehouse-ops.json` and `clinical_practice.pharmacy-operations.json`; and `planning/00-database-agent-product-design.md` reached only by targeted grep. Every `00` quotation in the JSON and this memo was `grep`-verified verbatim before use, from lines 29, 35, 95 and 120. No design cite is attached to the node itself: `design_cite` is `null` because no span of `00` names this situation, and a decorative cite is worse than none.

The `.research.md` of the schema anchor was **not** opened. The JSON settled the node test without it.

## Files considered and rejected

Named false positives, each with the reason it is not this row's evidence.

- **`Asset register - IT equipment 2026.xlsx`** — one row per unique serialised asset, lifecycle dates, quantity always one, no count-versus-book pair, no loss-reason vocabulary. `business_operations.it-asset-inventory`. This row's populations are fungible, perishable and recounted.
- **`Delivery note 2026-03-28 - Brakes - 2 lines short.pdf`** — the most seductive rejection in the set, because it *is* a counted-against-expected quantity variance. It is `retail_hospitality.supplier-order`'s: one consignment, one named supplier, one order reference.
- **`Controlled drugs register - CD cabinet - March 2026.pdf`** — a signed running balance, a witness slot on every entry, batch-and-expiry columns, a schedule reference. `clinical_practice.pharmacy-operations` authored this seam from its side and this row adopts it.
- **`stock_export_20260331.csv`** — a book-only export. It is the *recorded belief* half with no counting beside it. On its own bytes it favours `retail_hospitality.product-catalogue`; it is promoted here only when an as-at timestamp matches a count date **and** a sheet or variance record exists for the same population. Never promoted from a filename.
- **`Screenshot 2026-03-31 at 22.14.03.png`** — an EPOS stock-on-hand screen. Single quantity column, no count location, no variance. Temporary Screenshots. Screen origin is established by positive evidence only; missing EXIF proves nothing.
- **`Stocktake archive 2019-2024 - password protected.zip`** — carries the row's never-alone word in its filename and nothing else. Unsupported or Encrypted. It must not be opened to classify it.
- **A freezer inventory or home pantry list** — item and quantity columns, no second quantity, no trading unit, no ownership-for-sale premise. No row should fire; Independent Records.
- **A live EPOS or inventory database** — a source system, not a file node. Only a bounded export with a readable manifest is represented; live ingestion is a later connector and security decision.
- **A count-policy or SOP document** ("How to run a period-end count") — instructions *about* counts with no count event, no date, no population. It is procedure, and the row does not fire on it.

## `proposed_fields` justification

There are none, deliberately. The schema owns the fields and declares none under PR-6 as D1 narrowed it; a template may only reuse what its schema declares, and this one declares nothing. Minting a `count_event`, `count_location`, `variance_kind` or `stock_location` key here would create exactly the second copy of the schema the contract forbids. The intent is recorded for R1c in NJ-RH-STOCK-5 instead: if PR-6 is lifted, this row would want the schema's already-proposed `site` plus a count-event and a count-location concept — proposed as concepts, not as keys.

## Neighbours considered that did not get an edge

- **`retail_hospitality.pos-reporting`** — both reconcile a counted reality against a recorded belief, and on the family's framing they are siblings in structure. But the populations do not overlap: one counts *money in a drawer against a till*, the other counts *goods on a shelf against a book*. No single file plausibly reads as both, so there is no same-evidence mutex and no edge. If a cash-and-stock combined period-end pack turns up in a real corpus, R1c can revisit.
- **`retail_hospitality.food-safety`** — shares the kitchen, the fridge and a habit of photographing paper sheets, and its temperature log is also a ruled recurring sheet with initial slots. The discriminator is total: a food-safety row records a *reading against a tolerance*, this row records a *quantity against a book*. Structurally adjacent, evidentially disjoint. No edge.
- **`retail_hospitality.store-operations`** — the site compliance pack may physically contain count sheets. That is containment, not confusion; the pack's manifest is the operations row's evidence and the sheets remain this row's.
- **`business_operations.budget-forecast`** — the schema already drew this boundary from above (forecast-against-actual over line items and fiscal periods, versus counted-against-believed keyed to a till or a population). Adding it here would duplicate a seam the anchor owns.
- **`hr`** — a variance report naming a member of staff does *not* make it an HR record. It is a trading record with a staff-facing sensitivity, which is what `sensitivity_why` says and why Protected Records is the routing rather than a neighbour edge. Recording an HR edge would invite exactly the inference the row must not make.

## The collision fixture

`Cycle count variance 2026-W16 - Zone C.xlsx`. It carries a counted-against-expected pair per bin with a variance quantity — this row's headline signal, present in full. It is not this row's file. `logistics.warehouse-ops` authored it with the valuation, unit-cost and retail-price columns *deliberately absent*, and it carries bin-location, handling-unit and task-reference columns. What discriminates: value computed over a counted quantity under an ownership premise is this row's; a counted pair inside a custody chain over goods that may be somebody else's is not. The reciprocal is stated in both directions and both rows now name the same fixture pair.

A second, harder one is inside the family: `Delivery note 2026-03-28 - Brakes - 2 lines short.pdf`. It is a genuine quantity variance with the same vocabulary, and only the order reference and the named counterparty in the header separate it from a count.

## Recommendations for R1c (not applied — no neighbour file was touched)

1. `retail_hospitality.supplier-order`, when it lands, must state the short-delivery seam in the same words this row does: order reference plus named counterparty decides for it, population plus location plus date decides for this row.
2. `retail_hospitality.product-catalogue`, when it lands, should carry `stock_export_20260331.csv` as its *positive* fixture and name the promotion condition to this row, mirroring what `logistics.warehouse-ops` did for the valuation file.
3. The `retail_hospitality` ↔ `finance` coactivation intent (a closing valuation is legitimately both a trading record and finance evidence) belongs on the schema pair, not here. `also_holds_with` is schema-to-schema only under CONNECTION §5 and this row is a template, so it is left empty and the intent is logged in NJ-RH-STOCK-4.

## NEEDS-JOSEPH

- **NJ-RH-STOCK-1** — the count-location level is this row's entire dimensional difference and is also the level most likely to be a one-child branch. *A:* recommend it conditionally, exactly as the schema conditions the site level, firing only where a count event shows two or more disjoint locations. *B:* drop it; the count event holds every sheet flat. This row proposes A. If B is chosen the dimensional leg fails and the row rests on pair-grouping and privacy.
- **NJ-RH-STOCK-2** — the wastage log spans the interval *between* two counts and belongs exclusively to neither. *A:* a continuous series beside the counts at the count-location level. *B:* attached to the count it reconciles into. The design docs settle neither and the choice changes P9 group membership.
- **NJ-RH-STOCK-3** — reciprocity with `retail_hospitality.supplier-order` on the short delivery. Both rows read a counted-against-expected table. That row has not landed and must say the same thing.
- **NJ-RH-STOCK-4** — schema-level coactivation intent with `finance` cannot be recorded on a template. For R1c to place on the `retail_hospitality` schema if it agrees.
- **NJ-RH-STOCK-5** — if D1 or PR-6 is lifted, decide which fields the family may declare. This row proposes no key.

## Self-verification

`python3 -m json.tool` parses the node. Key set matches the landed siblings exactly (checked against `retail_hospitality.json`'s key list). Every `file_examples.source_type` is drawn from `SOURCE_TYPES`. Every `collides_with` entry is an object with `domain`, `signal` and `provenance`, and every `domain` was confirmed present in `roster.json`. Every `falls_through_to.residual_template` is one of `00`'s nine residual names. Every quotation was grep-verified verbatim in `00` before it was written. No thresholds, no handling classes, no confidence scores. `fields`, `proposed_fields`, `dimension_order`, `also_holds_with` and `role_split` are all empty by contract. Only the two assigned files were written.
