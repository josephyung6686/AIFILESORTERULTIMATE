# retail_hospitality.supplier-order — research notes

Depth: J-DEPTH
Kind: template · Schema: `retail_hospitality` · Launch: placeholder · Verdict: **KEEP** (`refuse_node: false`)

---

## 1. Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (full) and the stamped assignment from `make_prompt.py`.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — one landed launch row, read for depth calibration only.
- `planning/domains/nodes/retail_hospitality.json` — the schema anchor. Read for its **default template prose**, its `recognition.deterministic` and `never_alone` lists, its `work_types` enum and its `sensitivity_why`. This row's node test is measured against that prose.
- `planning/00-database-agent-product-design.md` — reached by grep, never streamed. Four spans grep-verified verbatim at count 1 each (§7 below), plus the residual-library paragraph at line 120.
- Neighbour node JSONs that had already argued a boundary against this id, located with one grep: `business_operations.procurement-sourcing`, `business_operations.vendor-management`, `construction_property.materials-delivery`, `retail_hospitality.stocktake`, `retail_hospitality.menu-recipe-costing`, `retail_hospitality.event-production`, `clinical_practice.pharmacy-operations`, `logistics.warehouse-ops`. I read only their `collides_with` entries naming this id.
- `planning/domains/canonical_fields.json` (key list only) and a grep across landed nodes for existing supplier/counterparty proposals.

Six neighbours had **already authored a boundary against this row before it existed**. That is the single most important fact about this research: the row was not defined here, it was *triangulated*, and my job was mostly to check whether the space they left is a real node or a hole they were polite about.

---

## 2. THE CHARGE — the strongest case that this row should not exist

Stated at full strength before any defence.

**(a) It is a document type.** "Purchase order", "delivery note", "credit note", "price list" are document-type words. The schema's own `never_alone` says so in terms: *a document-type word standing alone is a value of a function dimension, and "a row resting on one is the schema's default template wearing a name."* This row is named after four of them.

**(b) It is a lifecycle.** PO → confirmation → delivery → credit note is the textbook lifecycle of a single commercial transaction. A row whose definition is "the stages of one process" is a lifecycle row, and lifecycle stages are values, not nodes.

**(c) It is a work_type value — verbatim.** This is the sharpest form. The schema anchor's `work_types` array contains, as its third element: `"supplier ordering record - purchase order, order confirmation, delivery or goods-received note with shortages, credit note, trade price list"`. That is this row's entire scope, already enumerated as an *enum value on a field*. R1a's own rule — "work types are values" — appears to kill the row on sight.

**(d) It is a duplicate of a neighbour.** `business_operations.procurement-sourcing` already holds buying. The only claimed difference is that the goods are stock for resale in a retail or hospitality setting — and the schema anchor's constitutive never-alone says *"TRADING IN A SECTOR IS A FIELD VALUE, NOT A STRUCTURE."* So this row is procurement plus a sector value, which is exactly the 574's original mistake.

**(e) It is a row defined by absence.** Its cleanest discriminator against procurement is that *no competition is evidenced*. A row whose signal is "the evaluation matrix is missing" is defined by what is not there.

That is a genuinely dangerous stack. (c) and (d) are the ones that had to be answered with evidence rather than argument.

---

## 3. Defeating the charge

**Against (c), the work_type charge — the load-bearing answer.** All fourteen `retail_hospitality` templates correspond one-to-one with the schema's fourteen `work_types` values. That is how this family was laid out: the enum *is* the function dimension, and the templates are the situations that produce those functions. If the enum-membership argument killed this row it would kill all fourteen, including `stocktake`, `pos-reporting` and `premises-licensing`, which have landed. So enum membership is not the test. CONNECTION §2's test is: do the **detection signals, recommended dimensions, or privacy rules** differ from the schema's default? Answered in §4 below, leg by leg. The work_type charge is real but it is a charge against the *family's layout*, not against this row, and it must not be answered by pretending the overlap is not there — hence the row's `work_types` array lists the artefacts as values under it, not as sub-rows.

**Against (a), the document-type charge.** The row's detection signal is not any of the four nouns. It is **one reference token recurring across documents authored by two different parties**. `Delivery note.pdf` alone fires nothing; the schema anchor already says a single invoice is not this structure, and I have written the consumer-confirmation case into `never_alone` explicitly as the tempting false file. The nouns are the *values*; the recurrence is the *node*.

**Against (b), the lifecycle charge — and it half lands.** A row holding only goods-in paperwork would be a lifecycle-stage row and should be refused. That is precisely why this row is **not** split into an ordering row and a goods-in row, and why I recommend R1c never split it: the artefacts are unintelligible apart. A delivery note with two lines short means nothing without the order that says what was expected; the credit note means nothing without the delivery note. The row is the *binding*, not a stage of it. The charge is defeated by keeping the row whole, and it would immediately succeed against any future proposal to split it.

**Against (d), the duplicate charge.** The neighbour conceded it first, in its own file: *"a repeating stock replenishment against a catalogue supports the retail row; an order arising from a bounded competitive event supports this row."* `business_operations.vendor-management` also states that "order structure is already excluded by procurement/finance." Two neighbours independently drew the same line. More decisively, the structural difference is not sectoral: a sourcing event is **one requirement, one competition, one award against stated criteria** and produces an evaluation matrix and scored bidders; replenishment is **the same reference recurring weekly against an already-agreed price list** and produces no evaluation, ever. Those are different shapes, not the same shape in different clothes.

**Against (e), the absence charge — and I accept the correction.** "No competition present" is a bad signal and I did not write it as one. The row's positive signals are the recurring cross-author reference, the ordered-against-received column pair, the trade **account identifier**, and the **pack-structure triple** (order code / unit of issue / case price). The last is the quiet winner: a consumer purchase record has a price and a quantity; a trade order has the *unit of issue* between them, because what is ordered is a case and what is counted is a unit. That is present, not absent.

---

## 4. The node test, all three legs

**The schema's default template, quoted from the anchor's `template.why`:** "the TRADING UNIT - site, venue or channel - ONLY where the corpus genuinely spans more than one, then the TRADING OCCASION - the session, count, order cycle, booking, function or licensed premises the material belongs to, then the OPERATIONAL RECORD FUNCTION. Trading period sits INSIDE the occasion level, never above the site. NOT TIME-FIRST."

Note the trap: the default's occasion list **already names "order cycle."** So the row cannot claim its occasion is novel. It must differ elsewhere.

**Leg 1 — detection signals: DIFFER.** The schema's `AN ORDER-CYCLE structure` signal is this row's, and a template that merely restated it would fail. This row adds four signals the schema does not state: (i) the reference recurring **across different authors**, which no other signal in the family requires and no sibling artefact has — stocktake sheets, Z-reads, rotas and temperature logs are all single-author; (ii) the **supplier account identifier** in a labelled header slot, the token that separates trade paperwork from consumer paperwork; (iii) the **pack-structure triple**; (iv) **inbound direction** read structurally as which slot the holder occupies, which is what separates the row from `ecommerce-ops` when both files are called `orders_export.csv`. Leg passes.

**Leg 2 — dimensions: DIFFER, and this is the row's real claim.** Recommended: site (conditional, meaning the *deliver-to* unit) → **SUPPLIER ACCOUNT** → order reference → function. The inserted counterparty level is a level the default **does not have and structurally cannot have**, because its three levels are a place, an occasion and a function and a counterparty is none of the three. It earns its place on 00's own intelligibility argument: an order reference names nothing standing alone, exactly as Homework 3 is meaningless without the course. And nothing else binds the four artefacts, because two different parties wrote them. Not time-first, despite heavy pressure — every artefact here is dated and the corpus arrives weekly — because *"For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."* A delivery week is a content period, not a capture date. Leg passes, with NJ-RH-SUPP-1 open against it.

**Leg 3 — privacy rules: DIFFER IN RULE, not in label.** Both this row and the family carry `potentially_sensitive`, but for opposite reasons, and the rule is what CONNECTION §2 asks about. The family's posture is built on personal data about members of the public — guests, dietary and allergen requirements, identity-document numbers, complaint allegations. **This row is the family's one genuinely B2B row and can contain none of that**: the moment a consumer's name appears, the artefact is outbound and belongs to `ecommerce-ops`. What it protects instead is **negotiated trade terms** — case prices, rebates, settlement discounts, volume tiers on a named account — usually under a contractual confidence obligation. Plus one thin strand of a third kind: **delivery drivers' and reps' names and signatures**, private individuals who are neither the holder's staff nor the holder's customers. Leg passes.

Three legs pass. `refuse_node: false`. Had leg 2 failed I would have refused, because leg 1 alone would have been the schema's own signal restated.

---

## 5. Files considered and REJECTED

- **`Invoice 99213 - Bidfood.pdf` — collision fixture #1.** Same counterparty, same account, same line vocabulary. Rejected: an invoice's anchor is a *payment obligation* (terms, tax treatment, due date) and it reconciles **money**, not goods. The schema anchor states directly that a single invoice is not this structure. Discriminator: no quantity-received column, no reconciliation. → `finance.small-business-bookkeeping`.
- **`statement 31-03-2026 Brakes.pdf`.** Rejected: anchored to an *account balance across many invoices*. Finance.
- **`Order confirmation - your order has shipped.pdf` — collision fixture #2, and the one I care most about.** A consumer retailer's confirmation to a private individual. It has an order reference, a line table, a quantity, a price and a delivery date — four of the things that look like this row's evidence. Rejected: no trade-account identifier, no pack-structure triple, and **no later document under the same reference**. It falls to Receipts and Confirmations, which *"may hold isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents."* The operative word in that verbatim span is **ISOLATED**, and it is this row's fall-through rule in one word. This is why the row's constitutive never-alone is written against a document-type word rather than against a trade name.
- **`Stocktake 2026-03-31 - period end - all locations.xlsx`.** Rejected: variance scoped to a population at a location on a date, no counterparty in the header. Stocktake's, by its own authored signal.
- **`Recipe spec - beef shin ragu - GP calc.xlsx`.** Rejected: keyed to a *sold item* decomposing into components. Menu-recipe-costing's.
- **`Brakes - supply agreement 2026.pdf`.** Rejected: governs the relationship rather than executing against it. Vendor-management's.
- **`Supplier schedule - 6 Jun - Harbour site.xlsx`.** Rejected: many suppliers, one date. Event-production's, by the inversion it authored.
- **`orders_export.csv` (outbound).** Rejected: consumer names, delivery addresses, payment references — the holder is the seller. Ecommerce-ops'. Same filename as an inbound export; only the columns decide, which is why this got a `role_split` and not only a collision.
- **`CD register - March.pdf`.** Rejected: a custody/register obligation, not trade replenishment. Pharmacy-operations'.
- **`Amazon Business order - printer toner.pdf`.** Rejected and worth naming: a *trade account* buying *non-stock consumables*. It has an account identifier but the goods are never resold and there is no replenishment cycle. This is genuine `business_operations` overhead purchasing, and it is the case where my account-identifier signal is weakest — noted honestly rather than smoothed.

---

## 6. Reciprocal boundaries — status

Ten `collides_with` entries, every one an object carrying a `SAME FIXTURE BOTH SIDES` signal and an explicit both-directions MUST NOT TAKE clause, per the edge-shape repair. Six were **authored against this row first** and I adopted their framing rather than inventing a competing one: stocktake, menu-recipe-costing, procurement-sourcing, materials-delivery, event-production, pharmacy-operations. Adopting the neighbour's own words is deliberate — a boundary stated in two different vocabularies is not a boundary.

**Four are authored one-way here and R1c owes the reciprocal:** `logistics.shipment` (order reference vs consignment identity — event-production already flagged this as an open three-way), `finance.small-business-bookkeeping`, `retail_hospitality.ecommerce-ops`, and the ecommerce role split.

**`also_holds_with` is empty, deliberately.** CONNECTION §5 makes it schema ↔ schema only and this row is a template. The intent I would otherwise have recorded, for R1c: a supplier **credit note** genuinely carries both `retail_hospitality` (it settles a goods-in discrepancy) and `finance` (it is a tax document altering a payables balance) — that is a legitimate both-schemas file, not a collision, and R1c should consider it at schema level.

**Neighbours considered and deliberately given no edge:** `logistics.warehouse-ops` — its memo names this row as "the inbound demand document" and treats it as upstream, not competing; a warehouse's putaway and pick records have no order reference from the operator's side. `business_operations.contract-administration` — reached only through vendor-management, so an edge would duplicate. `retail_hospitality.store-operations` — a goods-in *rota slot* is a staffing record, not an order record, and the seam is thin enough not to need an edge. `finance.receipts-expenses` — that is the consumer-receipt world and the Receipts and Confirmations residual already covers the fall-through.

---

## 7. Quote verification

All four `00` spans used in the JSON were grep-verified verbatim, count 1 each:

1. "Privacy policy must be enforced before content reaches any model or external connector."
2. "Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs."
3. "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."
4. "However, the normal scan should never extract archive contents to the filesystem, because doing so creates security, storage, and side-effect risks."

Plus the residual-library span at `00` line 120 (Receipts and Confirmations) and the template-validation and screenshot spans, which I took from the schema anchor's already-verified usage. `design_cite` is `null`: no single span in `00` names this row's subject, and a decorative cite is worse than none. Provenance is `inference` throughout.

## 8. proposed_fields

Three, all **reused rather than minted**, and all recorded for R1c only — the row writes no field rows (PR-6).

- **`supplier`** — reused from an existing proposal found by grep across landed nodes; I deliberately did not mint `supplier_account`, `vendor` or `counterparty`. It is the row's only dimensional difference. Not canonical: `client` is the opposite role (who the holder acts *for*), `institution` and `venue` are places.
- **`trading_occasion`** — reused from the schema anchor's own proposed set. This row needs the schema's occasion key to accept an *order reference* as its value; it does not need a new key. Recorded so R1c can see the fourteen templates want one occasion key with fourteen kinds of value, not fourteen keys.
- **`site`** — reused from the schema's set, inherited conditional, flagged because this row's site value is the **deliver-to** unit, which in a head-office corpus is not the unit that placed the order.

## 9. NEEDS-JOSEPH

- **NJ-RH-SUPP-1 (decides whether the row survives).** The supplier-account level is the entire dimensional difference. **A:** recommend it unconditionally between site and order reference (this row's proposal). **B:** make it conditional as the site level is, firing only on two or more counterparties. If B and the corpus is single-supplier, leg 2 collapses and the row rests on the cross-author grouping leg and the commercial-confidence privacy leg alone — survivable, but narrowly.
- **NJ-RH-SUPP-2.** Does the supplier **invoice** ever join this row's P9 group? The schema says a single invoice is not this structure and finance owns the obligation — but an invoice carrying the order reference is the fourth artefact in the chain in most real corpora, and excluding it splits a group a user expects to be whole. **A:** finance owns every invoice absolutely. **B:** an invoice bearing the order reference joins the group *without this row activating on it*. The docs settle neither.
- **NJ-RH-SUPP-3.** The non-food **allocation sheet** is pushed, not ordered, and a receiving unit may hold one with no purchase order anywhere in its corpus. **A:** stays here as inbound order-cycle. **B:** goes to `retail_hospitality.product-catalogue` with the range plan it implements. Evidence genuinely balanced; the receiving-unit corpus is the case that breaks A.
- **NJ-RH-SUPP-4 (closure, not a question).** `retail_hospitality.stocktake`'s NJ-RH-STOCK-3 was left open pending this row landing. This row adopts that row's discriminator verbatim — order reference plus supplier identity in the header block decides for this row absolutely. **R1c may now close NJ-RH-STOCK-3.**
- **NJ-RH-SUPP-5 (recommendation, cross-row, not actioned here).** Four reciprocals are owed on neighbours I must not edit: `logistics.shipment`, `finance.small-business-bookkeeping`, `retail_hospitality.ecommerce-ops`, and the ecommerce role split. The logistics one is a **three-way** with `retail_hospitality.event-production`, which flagged it independently — a single POD can be claimed by movement identity, by order reference and by call-sheet position, and R1c should settle all three at once rather than pairwise.
- **NJ-RH-SUPP-6 (do not split).** Should a future pass propose separating "ordering" from "goods-in", the lifecycle charge in §2(b) succeeds immediately and both halves must be refused. Recording it so the argument is not re-litigated from scratch.

## 10. Self-verification

- `python3 -m json.tool` parses the node JSON. Key set matches the landed siblings' key set exactly (checked against `retail_hospitality.json`'s key list).
- Every `file_examples.source_type` is in `SOURCE_TYPES`: `text_document`, `spreadsheet`, `image`, `email`, `archive`.
- Every edge id verified present in `planning/domains/roster.json`. Every `falls_through_to` name is a `00` §7.3 residual.
- `fields: []`. No canonical key minted. No threshold number, no confidence score, no handling class anywhere.
- `also_holds_with: []` per CONNECTION §5 (template row).
- Twelve file examples, two of them explicitly labelled collision fixtures; the sparse-file case (`IMG_4471.jpg`) and the population case (`order_export_2026-w13.csv`) carry `group_without_copying_facts: true`.
- Only the two assigned files written. No neighbour, roster, canonical-fields, `check.py`, `src/` or SPEC file touched.
