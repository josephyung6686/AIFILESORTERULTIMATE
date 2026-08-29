# construction_property.materials-delivery — lab notes (template row)

**Depth: J-DEPTH** (deepened from GIST, 2026-08-25). The gist verdict — the row stands — is
**upheld, but on narrower grounds than the gist claimed.** One of its three legs is withdrawn. The
"what changed in this pass" section at the end is the audit trail.

---

## Sources

`planning/00-database-agent-product-design.md` (every quotation below machine-verified with `grep -F`
against that file before writing), `ALIGNMENT.md`, `_CONTRACT.md`, `CONNECTION.md` §2,
`roster.json`, `canonical_fields.json`, `DECISION-BRIEF.md` (J-IND, J-DEPTH, D1, PR-6),
`ROSTER.md` §4 → `13-trades-property-logistics.json` (line 916), `src/evidence_shape/vocabulary.py`
for `SOURCE_TYPES`.

**Neighbour files read in full before writing, and not contradicted:**
`construction_property.research.md` (the deepened schema anchor — the default template, the
professional/householder seam, and the `logistics` / `manufacturing` seams all come from there),
`construction_property.construction-project.research.md` (the spine),
`construction_property.plant-hire.research.md`, `construction_property.quote-estimate.research.md`,
`business_operations.procurement-sourcing.research.md` (deepened; NJ-BO-7 is the live question this
row sits inside), and `business_operations.policy-handbook.research.md` +
`construction_property.building-control.research.md` as the two precedents for writing a seam with a
schema that does not exist yet.

---

## What it is for, and what it holds

**Physical arrival.** Delivery and advice notes, signed proofs of delivery, goods-received sheets,
shortage and damage annotations, site call-offs and purchase orders carrying a site delivery
address, materials take-offs that deliveries are booked against, batch and conformity certificates
that travelled with a load, weighbridge tickets, fuel delivery notes for site plant, waste transfer
notes running the other way, and phone photographs of all of the above.

The situation is not "buying materials" and not "moving materials." It is the **three-way
comparison**: what was ordered, what the paperwork says arrived, and what the person signing said
actually came off the lorry. A delivery note with no discrepancy is filed out of habit; a delivery
note with `2 pallets short` written across it is filed because a job depends on it later.

---

## The node test, argued leg by leg

CONNECTION.md §2 is the binding form of the test: *"A **template** row exists only if its detection
signals, recommended dimensions, or privacy rules differ from its schema's default template."* The
schema anchor states that default so a sibling's refusal is checkable:

> **`property` or site → `instruction` (the job, the letting, the scheme, the block) → document
> function**, with a period level only where the situation *genuinely cycles* (a service-charge year,
> a rent-review cycle). **Not time-first.**

And it names the standard this row must clear:

> *`variation`, `snagging`, `dilapidations`, `retention`, `preliminaries`, `certificate`, `drawing`,
> `schedule`, `survey`, `valuation` and `report` are **values of `work_type`**, not rows.*

### Leg 1 — detection signals. **Differs. This is the leg the row stands on.**

The signal is not the word "delivery note." It is a **slot pair**: a **DELIVER-TO** address in a
labelled slot that is *different from* the **INVOICE-TO** address printed beside it, on the same
page, in the same document. Nothing else in this family has it. A valuation, a variation
instruction, a snagging schedule, a drawing sheet, a survey report, a certificate and a lease
schedule each carry *one* address; the delivery note is the only document in the construction world
whose structure encodes the fact that **the buyer and the destination are different parties**. That
is why it exists.

`00` licenses reading exactly this kind of structure as strong evidence: *"Deterministic extractors
create direct facts when the information comes from a reliable, explicit source, such as a content
hash, EXIF timestamp, a document title, or a labeled form field."* Two labelled address slots whose
values disagree is a *structural* observation, not a lexical one — which matters enormously, because
the family's own constitution is that it *is not detected by its nouns*.

Two further signals, each independent of the first:

- **Ordered-against-delivered columns.** A table with two quantity columns whose values differ on
  some rows. `00` is explicit that this is where the meaning of such documents lives: *"Tables matter
  because resumes, forms, applications, invoices, and administrative documents often place their most
  useful information in cells rather than body paragraphs."* An invoice has one quantity column; an
  order has one; a take-off has a required and a delivered column and no signature. Only the note has
  two quantity columns *plus* a receipt block.
- **A correction made at the moment of handover.** A struck-through quantity, `received unchecked`
  scrawled across a signature, `2 pallets short`. This is the strangest and most useful signal on the
  row, because it is **contemporaneous annotation on a printed form** — a document that disagrees
  with itself at the point of signing. No other row in this family produces one. A snagging schedule
  is *composed* of defects; a delivery note is a clean form that someone spoiled on purpose, and the
  spoiling is the record.

**Why this is not the `compliance-certificate` refusal repeating itself** — the charge the dispatch
put first, and the one that deserves the most care. That row was refused because *"its one candidate
detection signal reduces, when stripped, to **a document-type word plus an address** — and both
halves are constitutionally never-alone on this schema."* Strip this row the same way and something
survives: not the word `delivery note` (which is *also* never-alone here, and is now written into
`never_alone` in those terms), and not the address (likewise), but the **relationship between two
addresses** and the **disagreement between two quantity columns**. A relationship between two slots
is not a token; it cannot be produced by a merchant's letterhead, a filename, or a folder full of
building paperwork. The `compliance-certificate` refusal is not undermined by this row — it is
confirmed by it, because the row is refusing the same evidence class (`delivery note` + an address)
that the certificate row died on, and standing on something else.

### Leg 2 — recommended dimensions. **Withdrawn. The gist row over-claimed here.**

The gist memo asserted, verbatim (its text is in git at the previous commit): *"**Dimensions differ:** site → order → delivery date, with supplier deliberately *below* site."* Two problems, and both are conceded rather than argued around.

1. **The leg is structurally unavailable to every row in this family, equally.** `template.dimension_order`
   is empty by binding contract because the schema declares no fields, which the schema anchor
   records as a live question: *"If D1's deferral holds, the dimensions leg of the node test is
   unavailable to all 27 equally, and each must justify itself on detection signals and privacy rules
   alone."* A row that leans on this leg is leaning on nothing.
2. **Even as prose, the difference is thin.** Site → order → delivery date maps onto property →
   instruction → document function almost exactly, if a purchase order counts as an instruction. The
   one genuine departure is the *leaf*: the family puts **document function** last, and this row puts
   the **delivery event** last, because the terminal question about a delivery record is *when did it
   arrive*, not *what genre is it*. That is a real difference and a small one. Recorded in
   `template.why` and explicitly **not** relied on.

The anchor also warns that the reversal itself earns nothing: *"**Reversing is not a difference that
earns a node**; it is one of the things a template is *for*, and a sibling claiming a node on the
reversal alone has claimed nothing."* The supplier-below-site recommendation the gist row was proud
of is exactly such a reversal. It stays in `template.why` as a recommendation. It is no longer
offered as evidence.

### Leg 3 — privacy rules. **Differs, modestly but genuinely.**

The family's default privacy concern is **occupier and third-party personal data at an address** —
tenant references, leaseholder arrears, a householder's own home. This row's concern is different in
kind: it is **the signer**, and it is **geolocation**.

- Every delivery note in the corpus carries a **printed name and a signature image of an individual**
  whose only relationship to the file is that they were standing at a gate. That person is not a
  client, not a party, and not an author; they are custody. Authorship and custody are never
  destinations, and the row says so in every fixture's `must_not_conclude`.
- Carrier PODs and phone photographs of notes carry **precise coordinates**. `00` names the corpus
  this product handles — it *"can include identity documents, account statements, tax records, medical
  information, legal records, credentials, private correspondence, GPS metadata, employment materials,
  and educational records."* — and GPS metadata is on that list by name. The operative limit is `00`'s:
  *"Protected material should not be included in cloud-model prompts by default, should not display raw
  content in general group summaries, and should not be moved automatically without a user policy that
  explicitly permits it."*

This is not a *stricter* posture than the family's — `site-health-safety` holds that title — but it
is a **different one**, aimed at a different person on the page. The row assigns only the catalogue
value `potentially_sensitive` and does not assign, alias, rank or infer a P7 handling class.

### Verdict

**Stands, on legs 1 and 3.** One structural fingerprint no sibling has, one privacy concern aimed at
a different party than the family default. Leg 2 is withdrawn. This is a **narrower** basis than the
gist row claimed and it is stated that way deliberately: if R1c decides that a slot-pair fingerprint
plus a signer-privacy posture is not enough to buy a row on a field-less schema, the honest
consequence is that this row folds into `construction_property.construction-project` as a
`work_type`, and the memo below already names where the coverage would go. That outcome is written
out rather than defended against.

---

## The three charges, answered

### (a) "A delivery note is a **document type** — the charge that refused `compliance-certificate` in your own family." *(dispatch)*

Answered in leg 1. The short form: the charge is **correct about the word and wrong about the
structure.** `delivery note` as a lexical token is now explicitly listed in the row's `never_alone`
block, in the same terms the refusal used, so that the row cannot be activated by the noun that got
its sibling refused. What it activates on is a two-slot disagreement and a two-column disagreement.

There is a second, sharper form of the charge that the gist row never faced: **a delivery note is a
document type in the way that `certificate` and `drawing` are** — i.e. it appears in the anchor's
list of things that are *values of `work_type`*. It does not appear in that list, and the difference
is not luck. `certificate`, `drawing`, `valuation`, `report` and `schedule` are genres that *any* of
this family's situations can emit. A delivery note is emitted by exactly one situation and describes
that situation entirely. It is closer to `snagging schedule` — which also names a whole situation
and *also* got a row — than it is to `certificate`.

### (b) "It is plausibly `logistics`' material, and if the only discriminator is that the destination is a building site, that is a location value, not a structure." *(dispatch)*

**This is the strongest charge and the schema anchor has already ruled on it**, one-way, because
`logistics` is unwritten. The anchor's reciprocal table:

| Neighbour | This schema must not take | The neighbour must not take | Shared fixture |
|---|---|---|---|
| `logistics` *(not yet written)* | the carrier, route, fleet and warehouse — everything before the site gate | a delivery note keyed to a plot and a job reference and signed by a site manager | a delivery note |

The dispatch is right that "the destination is a building site" would be a location value and not a
structure. **That is not the discriminator this row uses.** The discriminator is **the key**:

- A **consignment or waybill reference** keys the record to a *transport movement*. The document is
  one row in a carrier's network; it is retrieved by consignment, it has a depot, a leg and a service
  level, and it exists identically whether the destination is a site, a shop or a house. → `logistics`.
- A **job, plot or site reference** keys the record to a *works instruction*. It is retrieved by job,
  it is compared against an order and a take-off placed for that job, and it is meaningless outside
  it. → this row.

The fixture bytes are named on both sides in the JSON, which is the thing the anchor asked for and
the gist row did not do: **`POD_export_2026-03.csv`** (consignment-keyed, coordinates, no job — goes
to logistics, and is now written into this row as an outbound negative fixture) against
**`DN-448120 - Marsh Lane.pdf`** (job-keyed, received-by signature, a shortage — this row's). And
the genuinely hard case is written out rather than resolved: **a single carrier POD for a merchant
delivery to a named site is on the gate itself**, and both families should retrieve it.

**What the logistics author is owed, said plainly so it can be disagreed with.** The line proposed
here is *the key, not the destination*. The alternative line is **custody** — whoever holds the file
owns the reading, so the haulier's copy is logistics' and the site's copy is construction's. Custody
matches how the two people actually experience the document and splits one POD into two families;
the key test is checkable from the bytes and does not. This row prefers the key test **and records
the alternative as an open question** (NJ-CP-MD-3), because a seam drawn against an absent neighbour
should be a stated position, not an assumed one. This follows the precedent set by
`business_operations.policy-handbook` with `hr` and by `construction_property.building-control` with
`government`.

**Where `manufacturing` stops, likewise.** The anchor: this schema holds *"the article's
**installation and approval at a named site**, not its making."* A works order, a production batch
record and a factory quality regime with no site on the page are `manufacturing`'s. The same batch
or heat number on a **declaration of performance that travelled with a load to a named site** is
genuinely shared, and this row keeps `DoP - steel batch 8841.pdf` as the fixture that proves it. A
new `manufacturing` collision entry says so; the id is written bare because no row id exists to
assert.

### (c) "It may be a `work_type` of `construction-project` — receiving goods is a step in building." *(dispatch)*

**The neighbour answers this from its own side, and its answer is the deciding evidence.** The
deepened `construction-project` memo lists, in its rejected-files table, *Plant hire and materials
delivery notes* → `plant-hire` (asset + hire period) and `materials-delivery` (the delivery event),
adding that *"They appear here only as residual examples."* The spine of this family has read its
own catalogue and declined these documents. A row cannot be a `work_type` of a parent that does not
want it.

Two supporting arguments, neither sufficient alone:

- **Most deliveries have no project.** A one-van trade job, a merchant collection, a fuel drop for
  plant standing on a site between two jobs — the delivery event routinely exists where no
  `construction-project` file exists at all. This is the same argument `quote-estimate` used and won
  on (*"At the moment a quote is written there is no job"*), applied to the other end of the
  lifecycle, and it is honestly weaker here than there: most *materials* deliveries do land on a job.
- **The `progress-photos` argument is NOT available to this row, and the gist memo came close to
  borrowing it.** That row earned its node because *"a `work_type` value cannot carry a different
  detection method; only a template can"* — it is recognised by capture metadata rather than by
  document structure. This row is recognised by document structure like everything else in the
  family. It gets no help from that reasoning and does not claim any.

---

## Files considered and rejected

The dispatch's own test: a row that only lists what it holds has not been researched.

| File | Why it is **not** this row's evidence |
|---|---|
| `Jewson statement - March.pdf` *(kept in the JSON — the inbound collision fixture)* | A merchant's monthly account statement quoting a column of delivery-note numbers. Every lexical signal fires. It is an accounting document; `finance.small-business-bookkeeping` owns it. See below. |
| `POD_export_2026-03.csv` *(added this pass — the outbound collision fixture)* | A carrier's own consignment-keyed network export. Delivery evidence in every ordinary sense of the word, and on the far side of the site gate. |
| `Meridian invoice 33012.pdf` | `business_operations.procurement-sourcing` already keeps this fixture, and its reading — *"A demand for payment is a bookkeeping transaction **even when it quotes a PO number**"* — is adopted here unchanged. Not re-fixtured; naming it twice would imply a disagreement that does not exist. |
| A builders' merchant price list or catalogue PDF | No arrival, no receipt, no order. `quote-estimate` already rejected the same file for the mirror reason (a catalogue is not an offer for specific works). Consistent on both sides. |
| A merchant credit-account application form | The commercial relationship, not a delivery. Bookkeeping / `business_operations`. |
| A skip-hire booking confirmation | A booking. `Receipts and Confirmations` handles it with no fixture needed — and note that the *waste transfer note* the skip later generates **is** this row's, which is the cleanest small demonstration that this row is keyed on the movement event and not on the supplier relationship. |
| A signed dayworks sheet listing materials used | Routed by the family's own `timesheet` refusal to `variation-claim`. Materials consumed is not materials received. Not collected here. |
| A stock-take or site materials count | Inventory, not arrival — and `construction_property.inventory-inspection` and `retail_hospitality` are the neighbourhoods for it. A count has no counterparty and no signature. |
| A supplier's CE/UKCA technical library downloaded from a website | Reading Inbox — *"papers, articles, reports, and saved PDFs that appear to be reading material but have no active research, course, or project association."* Identical vocabulary to a genuine DoP, zero event evidence. The discriminator is that the real one arrived **with a load**. |
| A driver's CPC card or a delivery driver's insurance certificate | An individual's credential. Identity/protected material, and never a delivery record. Named because a folder of scanned site paperwork routinely contains them. |
| A materials price-increase notification letter | Commercial correspondence; it changes what a future order costs and evidences no arrival. |
| An operative's expense claim for materials bought at a trade counter | `finance.receipts-expenses`. The till receipt is a purchase record held by a person, not a receipt of goods by a site. |

---

## The collision fixture, both directions

**Inbound (would wrongly fire this row): `Jewson statement - March.pdf`.** It carries a merchant
name, an account number, a period, and — decisively — **a column of delivery-note numbers**. It sits
in a folder full of delivery notes. Every lexical signal this row could be built on fires on it.

**What discriminates it:** the slot pair is absent. There is no deliver-to address distinct from an
invoice-to address, no quantity columns, no receipt signature; there is a balance and payment
instructions. And the note numbers it quotes are the trap in its purest form — `00`'s
*"The graph does not automatically copy those missing facts onto sparse files."* The statement is the
single most likely place in this row's world for a delivery fact to leak onto a document that is not
a delivery. `finance.small-business-bookkeeping` owns it.

**Outbound (must not be lost *to* this row): `POD_export_2026-03.csv`.** A carrier's proof-of-delivery
export: waybills, depot codes, delivered-at timestamps, coordinates, signatory surnames. It is
*literally* proof of delivery and this row is *literally* about proof of delivery. It belongs to
`logistics`, because it is keyed on consignments and knows nothing about a job. If this row swallows
it, the unwritten `logistics` schema is born already robbed of its paradigm document — which is
precisely the failure the two earlier unwritten-neighbour seams were written to prevent.

**And the file both sides should keep: `DoP - steel batch 8841.pdf`.** Retained from the gist row
because its reading was right and remains right: it is an *honest shared file*, not a mistake.
`construction_property.compliance-certificate` **refused** as a row, so its coverage routes to
Independent Records and to the situations that actually produce certificates — and this is one of
them. The gist JSON's fixture text still points at `compliance-certificate` as a live neighbour;
that is now a stale reference in prose, flagged here for R1c rather than edited into a contradiction
with a refused sibling I am not permitted to rewrite.

---

## Reciprocal boundaries, both directions

| Neighbour | This row must not take | The neighbour must not take | Shared fixture |
|---|---|---|---|
| `finance.small-business-bookkeeping` | an invoice, a statement, a payment demand or a posting reference, however many note numbers it quotes | a signed note with quantity columns, merely because the merchant is a payable | `Jewson statement - March.pdf` |
| `business_operations.procurement-sourcing` **(deepened)** | a bounded competition — solicitation, responses, evaluation, award | a routine site call-off against a materials schedule, and never the arrival evidence | `RE_ Marsh Lane - blockwork call-off wk16.eml`; a PO |
| `business_operations.contract-administration` | a release whose reference points **backwards** at an executed supply agreement | a delivery note, which is downstream of every one of those readings | `PO-2026-0331.pdf` (that row's fixture, named here, not duplicated) |
| `construction_property.construction-project` | a head-contract reference, a works measurement, a valuation cycle | the delivery event, which it has already declined in its own rejected-files table | a delivery note in a job folder |
| `construction_property.plant-hire` | an asset identity with an on-hire/off-hire period | a fuel delivery note for site plant — that row routes it **here** and this row accepts | `Fuel delivery - red diesel - 950L.pdf` |
| `construction_property.variation-claim` | an assertion of entitlement with a narrative and a cost consequence | the contemporaneous record that substantiates it | a shortage annotation |
| `construction_property.progress-photos` | an image of the state of the works | a photographed **document** whose accepted group is a delivery event | `IMG_1148.HEIC` |
| `construction_property.site-diary` | a dated narrative of a day | a per-consignment document with quantities and a receipt signature | a diary line reading "4 loads blockwork" |
| `logistics` *(not yet written)* | the carrier, route, fleet, depot and waybill — everything before the site gate | a job-keyed note signed at a site | `POD_export_2026-03.csv` vs `DN-448120 - Marsh Lane.pdf` |
| `manufacturing` *(not yet written)* | the works order, the production batch record, the factory quality regime | a certificate that travelled with a load to a named site | `DoP - steel batch 8841.pdf` |

The last two are authored **one-way**, as the anchor's are, and **R1c owes the reciprocals.** The
`business_operations` rows do not currently name this row from their side either; the fixture bytes
are named here so the reciprocal can be *checked* rather than asserted.

---

## Legacy id absorbed (ROSTER.md §4)

`cons.materials-delivery` (ROW), 1:1. No other legacy id folds in here; in particular the legacy
haulage and warehouse rows do **not**, and that is the site-gate seam expressed in roster terms.

---

## proposed_fields

**None.** PR-6 forbids field rows on this schema and D1's deferral stands. Candidate dimensions
(site/job, order, delivery event) remain prose in `template.why` for R1c.

**Seconding an existing proposal rather than minting one:** if R1c ever licenses fields on
`construction_property`, this row's need is met by whichever of NJ-CP-2's two options wins —
*reuse `project`* or *mint `instruction`* — and this row takes no position between them beyond
noting that a delivery note attaches to a job far more naturally than to a property, which is a
point in `instruction`'s favour and is recorded as such. The row mints nothing and proposes no
variant of its own. It explicitly does **not** propose a `supplier` or `delivery_date` key: supplier
is the row's most dangerous never-alone, and a delivery date is a `creation_date`-adjacent universal
that the shared fact set already covers.

---

## Neighbours considered that did NOT get an edge

- **`retail_hospitality.supplier-order`** — kept from the gist pass, still correct: trade-counter
  replenishment against a catalogue and a stockroom is that row's; delivery to a named site for a
  specific job is this one's. Not re-argued, because nothing changed.
- **`construction_property.snagging-defects`** — damaged goods on arrival and a defect at handover
  are both "something is wrong with the material," and they are separated cleanly by *practical
  completion*, which is the boundary that row already draws with the project spine. No new edge;
  duplicating it would risk contradicting a reciprocal that row has already authored.
- **`construction_property.final-account`** — materials cost flows into it, but the account is a
  payment settlement and this row holds no money reading at all.
- **`government`** — a waste transfer note is a statutory duty-of-care record and the `government`
  schema is unwritten. No edge drawn, deliberately: `construction_property.building-control` has
  authored this family's seam with `government` at length, and a second, thinner version of it from
  this row would be exactly the "contradicting a reciprocal that does not exist yet" risk the
  construction-project memo warns about. Flagged for R1c instead.
- **`identity`** — driver credentials and signatory names appear in this material constantly. The
  relationship is **protection, not a shared reading**, and it is handled through `sensitivity` and
  the Protected Records fallthrough, as the schema anchor does.

---

## Open questions

- **NJ-CP-MD-1 · Who owns the purchase order?** *(carried forward from the gist row, sharpened, and
  now four-way rather than three-way.)* `business_operations.procurement-sourcing` (a competitively
  sourced PO), `business_operations.contract-administration` (a release against an executed
  agreement), `finance.small-business-bookkeeping` (the commitment behind the invoice), and this row
  (a site call-off against a materials schedule). **This is not an independent question**: it is
  NJ-BO-7, already stated at length by the deepened `procurement-sourcing` memo, whose recommendation
  is *split at competitive-versus-routine, as a user-facing setting rather than a roster decision.*
  **This row agrees with that recommendation** and adds one fact from its own side: the construction
  case is the clearest instance of the routine half, because a call-off against a materials schedule
  has *no competition anywhere in its lifecycle*. Recorded for R1c: `procurement-sourcing`'s NJ-BO-7
  names `finance.small-business-bookkeeping` and `retail_hospitality.supplier-order` as the rows that
  would inherit the routine half, and **does not name this row.** That is an omission, not a
  disagreement — but it must be corrected on that side, not silently assumed here, and this row will
  not edit a neighbour to fix it.
- **NJ-CP-MD-2 · The photographed document.** Whether a phone photo of a delivery note is handled as
  a document (this row), as a capture (`photos`), or as both. *(Carried forward unchanged from the
  gist row; it remains `00`'s one-file-many-facts question in its most literal form.)* The fixture
  `IMG_1148.HEIC` records both readings rather than choosing, with `One-Off Images` as its
  fallthrough. Costs: treating it as a capture files a business record under a capture year, which
  the family default forbids; treating it as a document requires OCR to have run, which for
  handwriting is the least reliable path in the pipeline.
- **NJ-CP-MD-3 · Key or custody — where does `logistics` begin?** *(New this pass.)* **(a) The key**
  (a consignment/waybill reference is logistics', a job/plot reference is this row's) — checkable
  from the bytes, and this row's recommendation; cost is that one carrier POD for a merchant delivery
  to a site satisfies neither cleanly and must be shared. **(b) Custody** (whoever holds the file owns
  the reading) — matches how a haulier and a site manager each experience the document; cost is that
  it is not readable from the file at all, so it becomes a user-policy question, and it splits a
  single POD into two families. Stated so the `logistics` author can adopt or reject a written line.
- **NJ-CP-MD-4 · Does this row survive R1c on a field-less schema?** The schema anchor names this row
  by name among those that *"may then be `work_type` values on a sibling rather than rows of their own."* With leg 2 withdrawn above, this row stands on one structural fingerprint and one privacy
  posture. **If that is judged insufficient**, the coverage routes as follows and the routing is
  written now so the decision is cheap: the arrival documents become a `work_type` on
  `construction_property.construction-project`; the ordering half joins NJ-BO-7's routine split; the
  isolated note with no job goes to `Receipts and Confirmations`; the certificates go to Independent
  Records, exactly as the `compliance-certificate` refusal already routes them. This row does not
  believe that is the right answer, and it names the price of being wrong.

---

## What changed in this pass

**Preserved unchanged** (the gist row's work was sound and is not rewritten for its own sake): the
`one_line`'s core reading of the situation; the deliver-to/invoice-to fingerprint; all nine original
`file_examples` and their `must_not_conclude` lists; the bookkeeping, procurement, retail, plant-hire,
variation-claim, progress-photos and compliance-certificate collisions; all five `falls_through_to`
residuals with their quotes; the `sensitivity_why`; and the purchase-order open question.

**Added to the JSON:**
- Two `deterministic` signals — the purpose-coherent delivery **pack**, and the **call-off/schedule
  release** shape that separates routine ordering from a procurement event.
- Three `never_alone` entries, one of which is the answer to charge (a): the **delivery-note number**
  as a four-way bridge (with `00`'s high-frequency-bridge stop rule), the **job reference** as
  family-selecting but never row-selecting, and the **document-type word** itself, disclaimed in the
  same terms that refused `compliance-certificate`.
- One `needs_llm` entry covering the four-way PO ambiguity, ending in abstention.
- Three new `file_examples`: `POD_export_2026-03.csv` (the outbound logistics fixture, which the row
  previously lacked), `Fuel delivery - red diesel - 950L.pdf` (accepting `plant-hire`'s explicit
  routing), and `RE_ Marsh Lane - blockwork call-off wk16.eml` (an ordering document with no
  competition, which is the fixture NJ-BO-7 is actually about).
- Four new `collides_with` entries: `construction_property.construction-project` (the edge this row
  most owed — charge (c), answered with the neighbour's own words), `business_operations.contract-administration`,
  `manufacturing`, and `construction_property.site-diary`.
- The `logistics.shipment` collision **rewritten** to adopt the schema anchor's site-gate ruling
  verbatim, name the fixture bytes on both sides, and state the key-versus-destination discriminator
  explicitly for an author who does not exist yet.
- A second `open_question` (key vs custody), and grouping/context/work-type additions.

**Reversed or withdrawn — stated plainly, as the addendum requires:**
- **Leg 2 of the node test is withdrawn.** The gist memo claimed *"**Dimensions differ:** site → order → delivery date, with supplier deliberately *below* site"* as one of three supporting legs. That claim is wrong twice over: the leg is unavailable to all 27 siblings equally
  on a field-less schema, and the specific difference (supplier below site) is a *reversal*, which
  the schema anchor says earns nothing. The row now stands on two legs and says so.
- **The overall verdict is NOT reversed.** The row stands. It stands on a narrower and better-argued
  basis, with the price of being wrong written out in NJ-CP-MD-4.
- **NJ numbering changed.** The gist row used `NJ-CP-5` and `NJ-CP-6`, which **collide** with the
  schema anchor's `NJ-CP-5` (the logistics/manufacturing seams) and with `plant-hire`'s `NJ-CP-7`/`NJ-CP-8`.
  Renumbered to the row-scoped `NJ-CP-MD-*`, matching the `NJ-BO-PS-2` convention. Flagged for R1c
  because the collision exists across other gist rows too and this pass may not edit them.

**Not done, and why:** no neighbour file was edited. Three corrections belong to other rows and are
recommendations to R1c, not changes: (i) `procurement-sourcing`'s NJ-BO-7 should name this row among
the inheritors of the routine PO half; (ii) this row's `DoP - steel batch 8841.pdf` fixture text calls
`construction_property.compliance-certificate` "a live neighbour" when that row has refused — a stale
prose reference that R1c should retire family-wide rather than this row silently rewording; (iii) the
`logistics` and `manufacturing` reciprocals are owed from schemas that do not exist yet.

---

## Audits run before returning

- `python3 -m json.tool` on the node → **parses**.
- Key set compared programmatically against `construction_property.plant-hire.json`,
  `construction_property.variation-claim.json` and `construction_property.building-control.json`
  (landed J-DEPTH) → **identical, in order**.
- Every `“…”` quotation in the JSON extracted by script and `grep -F`'d against
  `planning/00-database-agent-product-design.md` → **25 quotes, 0 missing.**
- Every quotation in this memo attributed to `00` or to a neighbour file `grep -F`'d against its
  source (whitespace-normalised, to survive line wrapping) → **all present verbatim.** Four remaining
  quoted strings are quotations of the **dispatch message** (the three charges) and are labelled
  *(dispatch)*; one is a quotation of **this row's own superseded gist memo**, checked against
  `git show HEAD:` before use and attributed as such; one is an ordinary scare quote.
- Files written: exactly the two assigned. `git status` confirms no other path touched.
