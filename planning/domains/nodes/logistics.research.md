# logistics — lab notes (schema anchor)

Row kind: **schema**. Launch: **placeholder** (`fields: []`). Depth: **J-DEPTH**. Verdict: **kept, not
refused** — argued below against two charges taken at full strength, with the falsifier for each stated.

This is the schema row for an **eight-row family** — this row plus **seven templates**
(`shipment`, `customs-export`, `fleet-vehicle`, `driver-compliance`, `route-dispatch`,
`warehouse-ops`, `last-mile-pod`). Those seven measure their node test against the default template
stated here, so this memo is written on the assumption that **a sibling author reads this file before
writing theirs**: the anchor, the default template, the family never-alone bar, the privacy principle
and the seams are stated explicitly rather than left to be inferred from the JSON.

Nothing was salvaged: neither file existed. Every claim below traces to a quotation, a named neighbour
file, or an inference marked as one.

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — authoritative. **Every `“…”` in both files was
  machine-checked with `grep -F` against its source before writing**; the verification loop is in
  *Audits* below, and four quotations were shortened after it failed them.
- `planning/prompts/ALIGNMENT.md`; `planning/domains/_CONTRACT.md`; `CONNECTION.md` §2 (the node
  test), §4 (activation, never-alone), and `CONNECTION-EXAMPLES.md`.
- `planning/domains/roster.json` — confirmed `logistics` is `kind: schema`, `launch: placeholder`,
  and carries exactly seven templates; every edge id below was checked to exist there.
- `planning/domains/canonical_fields.json` — all 37 keys read. **No key minted.** Three of the five
  `proposed_fields` are explicit REUSE.
- `planning/overnight/council/DECISION-BRIEF.md` — D1, PR-6, J-IND and J-DEPTH taken as ratified.
- `ROSTER.md` §4 (the triage table, including the 18 `format / SOURCE_TYPE` drops that are the charge
  against this family), §4 Appendix A line 899 `13-trades-property-logistics.json`, and NJ-J-IND-1.
- `src/evidence_shape/vocabulary.py` for `SOURCE_TYPES`.

### Neighbour files read in full before writing, and not edited

- **`construction_property.materials-delivery.research.md` + `.json`** — the row that wrote this seam
  nineteen times before this schema existed. Read in full, as instructed. Answered in §1.
- `construction_property.research.md` — for NJ-CP-5, which drew the `logistics` seam one-way and
  says “Whoever writes those schemas may reasonably draw them”
- `manufacturing.json` — authored two commits ago. Its `collides_with.logistics` entry and its
  `asset` / `site` / `record_type` proposals are both answered and reused. §2.
- `business_operations.procurement-sourcing.research.md` — including the passage where it **declined**
  an edge with this family. §3.
- `business_operations.research.md` — read as the model for what a schema anchor owes its siblings
  (the default-template paragraph and the family never-alone bar are built on its pattern).
- `business_operations.support-operations.research.md` and `.meeting-record` — read for how the
  format charge was survived twice. §4 borrows its method and refuses to borrow its conclusion.
- `finance.vehicle-records.json`, `retail_hospitality` roster rows (`stocktake`, `supplier-order`,
  `returns-warranty`), `creative.research.md` (anchor idiom).

### Legacy ids absorbed (ROSTER.md §4, Appendix A, `13-trades-property-logistics.json`)

Seven, all 1:1 ROWs, none folded: `log.shipment`, `log.customs-export`, `fleet.vehicle`,
`fleet.driver-compliance`, `log.route-dispatch`, `log.warehouse-ops`, `log.last-mile-pod`. This
family therefore absorbed **no** consolidation surplus, which matters for §4: it cannot defend itself
by pointing at situations it swallowed from elsewhere.

---

## What this family covers, and what it deliberately does not

**The anchor, stated once so every leg can be tested against it: the custody handover.** A record
belongs to this family when it says *what quantity of what goods passed from whose control to whose
control, at what place, at what time, and who acknowledged it* — or when it evidences the **licence
and fitness of the party performing that custody** (the vehicle, the driver, the depot, the
authority's permission to cross a border).

Two things follow immediately, and they are the whole shape of the family:

1. **It is not about ownership, price or obligation.** A consignment note characteristically carries
   *no price at all*. That absence is not an accident of form; it is the point. The goods on it may
   belong to none of the three parties named on it.
2. **It is not about transformation.** The quantity on a movement record keeps its identity and
   changes place. The quantity on a production record changes identity.

**What it deliberately does not cover**, stated as flatly as the inclusions:

- **Buying the transport.** A freight tender, a rate card, a haulage contract award — `business_operations.procurement-sourcing`, which claimed them, and this row agrees. §3.
- **Paying for the transport.** A freight invoice is `finance`'s. §3.
- **Owning the goods.** Stock valuation, retail inventory, catalogue — `retail_hospitality`. §5.
- **A private person's parcels.** Tracking emails, courier cards, "your order has shipped" — the
  `Receipts and Confirmations` residual, and this is the family's largest fallthrough by volume in an
  ordinary corpus. Getting this wrong would manufacture a freight domain out of somebody's online
  shopping, and it is written into `never_alone` and carried as a negative file example.
- **The dispute.** Once a cargo claim becomes a pleaded matter it is `legal`'s.
- **Travel.** A person moving is not goods moving; ROSTER §5.6 refused travel as a schema and this
  row does not reopen it.

---

## The default template, stated for the seven siblings

`template.dimension_order` is **empty by contract** — a dimension may only branch on a field the same
schema declares, and this placeholder declares none. The recommendation is held as prose, and **this
is the paragraph every sibling must differ from**:

> the **carrier or trading counterparty** *only where the corpus genuinely spans more than one* → the
> **custody subject** — the consignment or container; or, in the fleet and dispatch branches, the
> vehicle, the depot, or the working day → the **document function** → **time only as a leaf.**
> Not time-first. **No level may be built from a consignee name or a delivery address.**

Why each level, and why in that order:

- **The carrier level is conditional and nearly always absent.** In a single-carrier corpus it is a
  one-child folder. It is also one step from being a collection point for an organization, which `00`
  warns against directly, so it is proposed with that warning attached rather than confidently.
- **The custody subject is the load-bearing level**, and it is deliberately branch-shaped rather than
  one key. A consignment makes a packing list, a declaration, a receipt and a damage photograph
  intelligible together; a vehicle makes a test certificate and a defect report intelligible; a
  working day makes a run sheet and its debrief intelligible. Forcing all three onto one key would be
  the giant-form failure the node test warns about.
- **Not time-first, despite this being a family of dated events**, and the reasoning is specific
  rather than a default: `00` says *“For document and record domains, project, function, or subject
  usually comes before time because putting year first scatters related work across calendar
  folders,”* and a consignment is the sharpest possible case — its booking, declaration, transport
  document, delivery receipt and claim routinely straddle a month or a year boundary, so a
  time-first order scatters exactly the files a claim needs together. The one sibling with a genuine
  claim on time-first is `route-dispatch`, whose subject *is* a working day. **It must argue that,
  not assume it**, and a reversal of the default earns nothing on its own.

---

## The family never-alone bar (binding on all seven siblings)

Modelled on the bar `business_operations` set for its 24, and made specific to this family's danger:

> **No sibling may rest its activation on a document-type word, a carrier or courier brand name, an
> address, or an identifier-shaped token.** Every detection signal must pair a **custody structure** —
> two named parties in *different roles* over one described quantity of goods, with a place and an
> acknowledgement — with a **labelled slot**. A row that can only name a form's title is not a node;
> it is the default template, or a `work_type` value on a sibling.

The **address** clause is this family's own contribution and is not borrowed. An address is the most
tempting false signal this schema has because it appears in at least four distinct roles on a single
page — place of receipt, place of delivery, depot of custody, capture location — and a sibling that
fires on "there is an address here" will fire on every invoice, letterhead and contact card in the
corpus. This is why the JSON's `site` proposal is defined as *the facility holding the goods*, never
as *any address printed on the document*.

---

## §1 — The seam with `construction_property.materials-delivery`, answered from this side

That row wrote this boundary in advance, one-way, so that it could be argued against. Taking it
seriously means saying which half I confirm, which half I sharpen, and which of its two alternatives
I reject — with reasons that are mine and not a restatement of its own.

**I confirm its ruling.** It reserves to this schema *“the carrier, route, fleet, depot and waybill —
everything before the site gate”* and to itself *“a job-keyed note signed at a site”*. That line is
right, and the dispatch's charge against it — that a delivery note is my material distinguished only
by the destination being a building site, which is a location value, not a structure — **fails**, but
not for the reason a defender would reach for first. It fails because *the destination is not the
discriminator on either side.*

**I confirm its discriminator, the KEY, and I restate it in my own terms because a two-sided
agreement is only worth something if the second side derived it.** The question is **which retrieval
spine the document is a row in**:

- A **consignment or waybill reference** indexes into *a carrier's network of movements*. The
  document's siblings are other consignments. It has a depot, a leg and a service level, and it exists
  in identical form whether the goods stop at a site, a shop or a house. → this schema.
- A **job or plot reference** indexes into *one works instruction*. Its siblings are the order and
  the take-off placed for that job, and it is meaningless outside it. → that row.

The test is checkable from the bytes, which is the property that makes it a discriminator rather than
a preference. **Fixture bytes named identically on both sides**, and now carried as file examples on
both sides: **`POD_export_2026-03.csv`** (consignment-keyed, depot codes, coordinates, no job — mine)
against **`DN-448120 - Marsh Lane.pdf`** (job-keyed, received-by signature, a hand-annotated shortage
— theirs). That row wrote the first into itself as an outbound negative fixture before I existed; I
have now written the second into myself as an inbound negative fixture. Neither file can now be lost
silently.

**I reject its stated alternative, and this is the one place I contest rather than confirm.** Its
NJ-CP-MD-3 offers **custody of the file** — *“whoever holds the file”* owns the reading, so the
haulier's copy is mine and the site's copy is theirs. That row already names the honest cost (it is
not readable from the file at all, and it splits one POD into two families). I add a second cost it
did not name, and it is the decisive one **from my side**: custody would hand this schema a job-keyed
note *that this schema has no key to retrieve it by*. My retrieval spine is the consignment; a note
carrying only `Job 4412 / Plot 17` is, in my hands, an orphan filed under a carrier folder it does not
name. Custody is therefore not merely unreadable — it is **unusable** for the family it would give the
file to. The key test survives independent confirmation; custody does not.

**I accept the shared case rather than resolving it.** That row calls a single carrier POD for a
merchant delivery to a named site *“on the gate itself”* and says both families should retrieve it. I
agree and make no attempt at a discriminator, because there is no honest one in the bytes: the file
genuinely carries a consignment key *and* a job key. It is written as `also_holds_with`, licensed by
`00`: *“One file may hold facts from more than one domain without losing information.”*

**Net effect on the charge.** The charge assumed the discriminator was the destination. It is not, on
either side, and the boundary is now argued from both. NJ-CP-MD-3 should close in favour of **(a) the
key**; R1c is ratifying a two-sided position, not adjudicating a dispute.

---

## §2 — The seam with `manufacturing`: goods in and goods out

`manufacturing` landed two commits ago and wrote the seam from its side: it owns *transformation,
inspection and release of the lot*; this schema owns *custody movement, shipment, carrier and
receipt*. **Confirmed, and sharpened with a test it did not state.**

**Read the quantity columns.** If quantity **changes identity** — consumed, output, yield, scrap,
rework — the record is a transformation and is `manufacturing`'s. If quantity **keeps its identity and
changes place or holder** — shipped, received, short, damaged in transit — it is a movement and is
this schema's. This is stronger than "who owns the lot number", because both families legitimately
carry the same lot token, and it is checkable per-column.

**Same fixture bytes on both sides**, as that row asked: `Lot genealogy L240817-03.xlsx` (its
example, `also_schema: logistics`) beside `Packing list SO-9912.xlsx` (mine, `also_schema:
manufacturing`, written with a lot column present on some rows precisely so the shared case is
visible). Consume/output-operation columns support it; carton, weight, marks and ship-to columns
support me.

**The genuinely hard file is the goods-received note at a factory door**, and I do not resolve it. It
is a custody receipt against a consignment *and* a lot acceptance against incoming quality. It sits in
this row's `needs_llm` and in `also_holds_with`, on disjoint evidence: the inbound reference and
receipt acknowledgement on my side, the lot-acceptance and inspection disposition on theirs. That is
the same treatment `manufacturing` gave the supplier certificate, so the two rows are consistent.

**Reciprocal recommendation for R1c (not an edit):** `manufacturing`'s `collides_with.logistics`
entry names a packing list generically; it could now name `Packing list SO-9912.xlsx` and adopt the
quantity-column test. I did not touch that file.

---

## §3 — Buying versus moving: `procurement-sourcing`, `vendor-management`, `finance`

**`business_operations.procurement-sourcing` explicitly declined an edge with this family**, on the
ground that *“freight tendering is this row in a sector. A sector is not a node.”* **I agree and do
not contest it.** A freight tender, a carrier rate card and a haulage contract award are procurement's
situation with freight as the category, and a category is a value. This schema does not want them.

But the declination is one-directional, and **the return direction is owed and is not stated on that
side**. Offered for R1c:

> Procurement must not take the movement's own record. A **purchase order is a two-party commercial
> instrument** — buyer, seller, price, authorisation. A **consignment note is a three-party physical
> one** — consignor, consignee, carrier, quantity, place, acknowledgement, and no price.

Same bytes both sides: a carrier's rate card (theirs) against `CMR_2026-04-11_DE-HK.pdf` (mine).
`business_operations.vendor-management` keeps the standing carrier relationship for the same reason,
which is also why the JSON's `role_split` points the `carrier` key at that row rather than at
procurement.

**`finance`: an invoice for freight is still an invoice.** This is the single most tempting false
positive the schema has, and it is carried as a negative file example rather than argued away:
`Freight invoice 88214 - Kuehne.pdf` names consignments, a carrier and a movement, and is not mine.
The discriminator is **what the document does** — money and obligation versus possession and location.
The invoice has an amount due, a tax treatment, payment terms and a remit-to block, and *no receipt
acknowledgement and no consignee role slot*. The consignment note has the acknowledgement and no
price. Both tests are positive-and-negative, which is what makes the pair decidable.

**`finance.vehicle-records` is the harder finance edge, and I concede the default to it.** That landed
row follows *“one owned or operated vehicle”* across acquisition, tests, servicing and disposal —
structurally identical to this schema's fleet branch, holding the same document types.
`Vehicle_MOT_YK71ABC_2026.pdf` **cannot be discriminated from its own bytes**, and I say so rather
than inventing a signal. What discriminates is a **controlled population under an operator's duty**:
an operator licence, a periodic safety-inspection interval, walkaround defect reporting, several
vehicles. **Where none of that is evidenced, the finance row keeps the file.** A `role_split` entry
records this, because the two rows hold the same entity type in different roles.

---

## §4 — The charge: "these are formats, not domains"

The charge, written at full strength before any answer, because a reader who does not accept this
section should not accept the rest:

> *ROSTER §4 dropped **18** legacy ids as “format / SOURCE_TYPE” material — calendar, mail, chat,
> call, contact and log — because a container is not a domain. Now look at this family's paradigm
> documents. A **waybill** is a form. A **manifest** is a form. A **delivery note** is a form. A
> **tracking export** is a log. `log.shipment`, `log.warehouse-ops` and `log.last-mile-pod` even carry
> the log in the id. Strip the forms out and what remains is `procurement`'s buying, `finance`'s
> paying and `construction_property`'s receiving. This family is a stationery cupboard.*

Three concessions are owed before the answer.

**Concession 1 — some of this family's material really is container material, and the schema does not
get it.** A tracking notification email, a courier's SMS export and a telematics log dump are
`SOURCE_TYPES` and extractor output. `00` settles their status: the engine must *“dispatch each file
to a type-specific extractor”* — a container is a dispatch decision. This is hardened into an explicit
`never_alone` entry, and `Shipping confirmation - order 10093.eml` is carried as a file example whose
whole job is to be a file the domain plausibly produces and must **not** fire it.

**Concession 2 — three of the seven ids name a form or a log.** `log.shipment`, `log.warehouse-ops`,
`log.last-mile-pod`. That is a fair reason to have been suspicious.

**Concession 3 — `meeting-record`'s answer is unavailable here**, and I am not claiming it. That row
survives on a cross-file *series* regularity: N files, one varying date token, one invariant heading
skeleton. This family's monthly carrier exports superficially resemble that, but the resemblance is
worthless — a monthly re-export is an overlapping row set, which is a duplicate-family problem, and
the JSON's `grouping_reasons` treats it as one. I do not claim the series signal.

### The answer, in three legs

**Leg 1 — the evidence is a role structure, and no `SOURCE_TYPE` definition contains a role.** This
is `support-operations`' method and it transfers exactly. That row survived by showing its signal was
*“roles inside the table”* rather than the transport. Mine is: **two named parties in *different*
roles — consignor and consignee — plus a carrier undertaking, over one described quantity of goods,
with a place of taking over, a place of delivery, and an acknowledgement.** Test it: `.pdf` is the
container; `email` is a container; *consignor × consignee × carrier × quantity × place × acknowledgement*
is **the vocabulary of a situation** — one party gives up possession, a second takes it on
undertaking, a third receives it, and the handover is acknowledged. No `SOURCE_TYPE` definition
contains any of those words, and no extractor dispatches on them. That is the precise difference
between this family and the 18 dropped ids: **those ids named the transport (`mail`, `chat`, `call`,
`calendar`, `logs`); this schema names the roles inside the document.** `00` puts reading such a
structure in the rules layer, not the model layer: *“Tables matter because resumes, forms,
applications, invoices, and administrative documents often place their most useful information in
cells rather than body paragraphs.”*

**Leg 2 — the paradigm document is an instrument, which is a thing no format is.** This is the leg
`support-operations` could not reach for, and it is the strongest one this family has. A **bill of
lading is a document of title**: it has a stated number of originals, an endorsement space, and a
condition-on-receipt clause, and possession of the paper controls delivery of the goods. A **customs
declaration** creates a liability to a public authority. A **CMR consignment note** allocates
liability for loss in transit. A container does none of these things; an `.eml` allocates no
liability. A charge that this material is form-shaped has to explain why the forms have **legal
effects** that survive the format they are rendered in — the same bill of lading is a bill of lading
as paper, PDF or an EDI segment set.

**Leg 3 — four of the seven siblings are not form-shaped at all**, and the charge has to explain them
away. `fleet-vehicle` and `driver-compliance` are **entity dossiers** — one vehicle's working life,
one person's licensing and fitness — anchored on an asset and a person, not on a movement or a form.
`route-dispatch` is anchored on **a working day × a vehicle** with an *ordered* drop sequence, and the
ordering is the signal, because it is exactly what distinguishes a run from a list of addresses.
`warehouse-ops` is anchored on **goods at rest in a place under a bailment**, which is neither a
movement nor a transaction. None of the four is a dump of anything and no container produces them.

### The falsifier, stated

If R1c judges that *consignor / consignee / carrier / quantity / place / acknowledgement* is in fact
**the generic despatch-form skeleton** — a shape every logistics tool emits and therefore a document
shape alone, forbidden by this row's own never-alone bar — then leg 1 fails on the family principle
and leg 3 becomes the schema's main support. In that world the honest outcome is a **smaller family,
not none**: `fleet-vehicle` and `driver-compliance` stand on an asset anchor and a privacy posture,
`warehouse-ops` and `route-dispatch` stand on their own structures, and `shipment`, `customs-export`
and `last-mile-pod` become `work_type` values with their coverage routed to `Receipts and
Confirmations`, `government` and `One-Off Images` respectively. I do not think that judgement is
right, because the discriminating slots are *two parties in different roles* and *an acknowledgement
of receipt*, which a purchase order, an invoice and a work order all lack — but the price of being
wrong is written out so the decision is cheap. This is NJ-LOG-2.

### The second charge: "a shipment is only a transaction, so `finance` and `procurement` own it"

Answered in §3 and shorter. **It proves too much.** If a shipment were only a transaction between two
parties, the consignment note would name two parties and carry a price. It names **three** and carries
**no price**. The third party — the carrier, who owns none of the goods and is party to neither side
of the sale — is the thing neither `finance` nor `procurement` has a place for, and is precisely the
party whose custody the whole family is about. Where a document *does* reduce to two parties and a
price, this row hands it over: that is the freight invoice, and it is a file example routed to
`Receipts and Confirmations`.

---

## §5 — Reciprocal boundaries, both directions, with the fixture named on both sides

| Neighbour | This schema must not take | The neighbour must not take | Shared fixture |
|---|---|---|---|
| `construction_property.materials-delivery` *(landed; wrote its side first)* | a job- or plot-keyed note signed at a site | the carrier-keyed POD export that knows nothing about a job | `POD_export_2026-03.csv` vs `DN-448120 - Marsh Lane.pdf` |
| `manufacturing` *(landed)* | consume/output genealogy, inspection, release, disposition | the shipped/received movement of the same lot | `Lot genealogy L240817-03.xlsx` vs `Packing list SO-9912.xlsx` |
| `finance` | an amount due, tax treatment, payment terms, remit-to | the receipt acknowledgement with no price | `Freight invoice 88214 - Kuehne.pdf` |
| `finance.vehicle-records` *(landed)* | one household vehicle with no operator-duty evidence | a vehicle inside a controlled fleet under an operator licence | `Vehicle_MOT_YK71ABC_2026.pdf` |
| `business_operations.procurement-sourcing` *(landed; declined the edge)* | the freight tender, rate card and award | the three-party movement record itself | rate card vs `CMR_2026-04-11_DE-HK.pdf` |
| `business_operations.vendor-management` | the standing carrier relationship, reviews, scorecards | the individual consignment under it | a carrier SLA vs a waybill |
| `retail_hospitality.stocktake` | a count with a valuation or unit-cost column, on owned stock | a custody log with bin locations and book-outs, on others' goods | `Goods in 2026-04 Depot B.xlsx` |
| `government` | a tariff ruling, authorisation or registration with no consignment | the declaration as a consignment's travelling document | `Export declaration MRN 26GB1234567890.pdf` |
| `legal` | the pleaded cargo dispute; the instrument as instrument | the transport record of the consignment | `BL_MAEU5512884.pdf` |
| `photos` | the capture as a capture, GPS as `location` | the doorstep image's role as an arrival record | `IMG_20260411_1432.jpg` |
| `medical` | a clinician's fitness opinion as health information | the licence-entitlement structure around it | `Driver medical certificate - D Okonkwo 2026.pdf` |

The `construction_property` and `manufacturing` rows are the only two that had already authored their
side; **both are confirmed rather than contradicted**, and both now have the same fixture named on
both sides, which is what makes the reciprocal *checkable* rather than asserted. The remaining nine
are authored one-way from here, and **R1c owes the reciprocals**.

### Neighbours considered that did NOT get an edge, and why

- **`hr`** — a driver is an employee, and licence, training and medical records look like HR files.
  **No edge, deliberately.** The discriminator is not the person but the *duty*: driver entitlement
  and hours records exist because an operator's licence requires them for anyone holding custody of a
  vehicle, not because someone is employed. A driver who is a subcontractor has the same file. HR
  owns the employment relationship; this family owns the fitness-to-hold-custody evidence. If R1c
  disagrees, `logistics.driver-compliance` is the row that moves, not the schema.
- **`code`** — an EDI or carrier-API payload is `code_structured`. Rejected: a structured export is a
  `SOURCE_TYPE`, and treating it as a code project would be the format error in reverse.
- **`resource_operations`** — bulk haulage of fuel, aggregates or crops. Rejected for the same reason
  procurement rejected freight tendering: *what* is being moved is a value, not a node.
- **`business_operations.facilities-workplace`** — a warehouse is a building. Rejected: that row owns
  the premises as premises (lease, services, fit-out); this one owns the goods inside them.
- **`construction_property.plant-hire`** — plant is delivered on a low-loader. Rejected: that row
  already routes a fuel delivery note to `materials-delivery`, and the on-hire/off-hire asset period
  is its own anchor, not a custody handover.
- **`identity`** — a driving licence. Rejected: a person's own licence as an identity document is
  `identity`'s; this family sees it only inside an entitlement structure with categories and expiries
  held by an operator.

---

## §6 — The collision fixture, and files considered and rejected

**The required collision fixture — a file that looks exactly like this schema's evidence and is not:
`Freight invoice 88214 - Kuehne.pdf`.** It carries consignment references as line items, a carrier's
name in the letterhead, and describes movements that genuinely happened. It is `finance`'s.
**Discriminator:** an amount due, a fuel surcharge, a VAT treatment, payment terms and a remit-to
block — and, negatively, *no acknowledgement of receipt of goods and no consignee role slot*. If this
schema swallows it, it has become a folder for anything with a courier's name on it, which is exactly
the never-alone failure its own bar forbids.

**Rejected — `Shipping confirmation - order 10093.eml`.** A retailer's templated mail with a tracking
number and a courier brand. This is the highest-volume tempting false positive in a *personal* corpus,
and it must land in `Receipts and Confirmations`. One recipient, one purchase, a price, no role
structure, no acknowledgement of arrival. A schema that fires on this converts a private person's
shopping into a freight domain.

**Rejected — `DN-448120 - Marsh Lane.pdf`.** `construction_property.materials-delivery`'s, by the key
test of §1. Carried here as a file example so the seam is falsifiable from this side.

**Rejected — a quarterly stock count with a valuation column.** `retail_hospitality.stocktake`'s. My
`Goods in 2026-04 Depot B.xlsx` is written with valuation columns deliberately absent, so the pair is
decidable rather than a matter of emphasis.

**Rejected — `ECN`-style change notes, works orders, calibration certificates.** `manufacturing`'s and
`engineering`'s; no custody handover appears on any of them.

**Rejected — a courier's marketing email, a fuel-station receipt, a road-toll statement.** Receipts,
not custody records. The toll statement is the interesting one: it is a per-vehicle dated log and
looks like fleet material, but it evidences a payment, not a duty or a defect.

---

## §7 — Privacy posture (the point the anchor was explicitly asked to state)

**Consignment records carry addresses, and addresses are personal data.** This is not a caution
attached to the family; it is the constraint that shapes its default template.

The ordinary payload of this family's paradigm documents includes: a consignee's **name and home
address**, a **signatory's surname**, a **signature image**, a **delivery-point coordinate**, a
**photograph of a private dwelling**, and a delivery-instruction note that can disclose absence,
disability or occupancy patterns. The fleet and driver branches are worse: a **tachograph download is
a minute-by-minute activity and location history of one named worker**, and a **driver medical
certificate is health information**. `driver-compliance` is, on this reading, the most privacy-exposed
row on this schema and possibly among the most exposed outside the four named safety domains.

**FAMILY PRINCIPLE, binding on all seven siblings:**

> **The consignee is a party, never a folder.** No sibling may propose a destination dimension built
> from a consignee or consignor name, a delivery address, a driver's or signatory's name, or a
> coordinate. Those are **search-and-privacy facts only.**

`00` supports this in two places rather than one. For the address-book case directly: contact formats
*“should normally be privacy-protected rather than used to create folder proposals”*. For the entity
case generally: *“A folder should not become a collection point for everything produced by the same
person or organization.”* And the design already anticipates the material: *“Rare but sensitive files
such as passports, visas, and legal documents may be surfaced as protected records even when they do
not meet a normal group-size threshold”* — the driver dossier is that shape.

**This principle is the reason the `consignment` key exists and is destination-eligible while the
consignee is not.** A consignment reference identifies *goods*; it is the one key in this family that
is safe to fold a folder on. The asymmetry in `proposed_fields` — a `carrier` key offered but no
consignor/consignee key — is deliberate and is the schema's answer to its own privacy problem, not an
oversight for R1c to complete.

The schema is `potentially_sensitive`, not a safety domain, and **assigns no handling class** — those
are P7's. It records the same structural gap `construction_property` (NJ-CP-4) and
`business_operations` recorded: the substitute mechanism that forces the privacy path ahead of a model
or connector path for **third-party** personal material has no home, and this family is a strong
argument for one. Flagged, not solved, and it should be answered with those two rows rather than
separately.

---

## §8 — `proposed_fields`: what is proposed and, more importantly, what is reused

Five keys. **Two proposed new, three explicit REUSE.** The reuse is the more considered half.

- **`consignment`** *(new)* — the custody-chain key, and the only genuinely novel concept this family
  needs. No canonical key holds it: `project` is bounded work and would turn every parcel into a
  project; `record_type` describes the document rather than what it is about; `event` is Photos'
  capture-occasion key and carries a time-primary reading this family must not inherit.
  `reliability_ceiling: validated`, because an identifier-shaped token must be confirmed by a
  reference-pattern rule co-occurring with a carrier-role or place slot — R6's rule family; **no regex,
  no threshold and no score is written here.** `00` names the underlying hazard exactly: *“file names
  and documents frequently contain numbers that look like years but are course identifiers, version
  numbers, build numbers, ZIP codes, or other unrelated values.”*
- **`carrier`** *(new)* — the role key, licensed by `00`: *“The system must separate roles that happen
  to contain the same entity type.”* One page names three organizations in three roles, and
  `institution`, `client`, `our_firm` and the `organization` proposal each collapse at least two.
  Destination-eligibility is proposed TRUE only conditionally, with the collection-point warning
  attached; R1c may reasonably seed it ineligible.
- **`asset`** *(REUSE of `manufacturing`'s proposal)* — for the fleet vehicle. That row proposes
  `asset` for *“the maintained, calibrated or inspected equipment item”*, and a fleet vehicle is that
  thing exactly. **This row deliberately does NOT mint `vehicle`, `registration` or `fleet_number`.**
  A vehicle is a value of `asset`, and minting a domain-shaped synonym for a key another schema
  already proposed is the 574's mistake in miniature. If R1c splits `asset`, this row wants the split
  argued **once, globally**, not twice locally.
- **`site`** *(REUSE of `manufacturing`'s proposal)* — for the depot, warehouse, terminal or
  cross-dock. One warning added for R1c that `manufacturing` did not need: in this family a place
  value appears in four roles on one page, so `site` must be defined as *the facility holding the
  goods*, never as *any address printed on the document*.
- **`record_type`** *(REUSE of the canonical key)* — and this row **raises no new question about it**.
  `manufacturing`'s NJ-MFG-1 already asks whether the canonical Finance-role key is global enough for
  operational records; opening a second thread on one decision would cost R1c time and gain nothing.
  This row records only that it needs the same answer.

**Deliberately not proposed:** no consignor/consignee key (§7); no `vehicle` (reuse); no
`trade_lane`, `service_level`, `incoterm` or `mode` — those are **values** of a `work_type` or of
`record_type`, and the node test is explicit that a value dressed as a key is the failure mode.

---

## NEEDS-JOSEPH (this node only)

- **NJ-LOG-1 · Key or custody — where does `logistics` begin?** *(Answers
  `construction_property.materials-delivery`'s NJ-CP-MD-3 from the other side.)* **(a) The key** — a
  consignment/waybill reference is this schema's, a job/plot reference is that row's. **This row's
  recommendation**, confirmed with independent reasoning in §1, not merely accepted. **(b) Custody** —
  whoever holds the file owns the reading. **Rejected here**, for that row's own stated cost (not
  readable from the bytes) plus one it did not name: custody would hand this schema a job-keyed note
  it has no key to retrieve by. Both sides now say (a); R1c is ratifying, not adjudicating.
- **NJ-LOG-2 · Does the schema survive the format charge?** Argued in §4 with the falsifier stated. If
  R1c judges the role structure to be a generic despatch-form skeleton, the honest outcome is a
  **smaller family** — `fleet-vehicle`, `driver-compliance`, `warehouse-ops`, `route-dispatch` stand;
  `shipment`, `customs-export`, `last-mile-pod` become `work_type` values routed to `Receipts and
  Confirmations`, `government` and `One-Off Images`. Alternatives spelled out so the trim is cheap.
- **NJ-LOG-3 · Which of the seven templates survive on a field-less schema?** The dimensions leg of
  the node test is unavailable to all seven equally under D1's deferral, so each must stand on
  detection signals or privacy rules. **`logistics.last-mile-pod` is at real risk** — a POD is
  arguably a `work_type` value on `logistics.shipment` — and what would save it is a **privacy-rule**
  difference (doorstep photographs of dwellings, signature images, delivery coordinates), which is a
  legitimate leg. `driver-compliance` has the strongest privacy leg in the family and should survive
  on it alone. `shipment` and `warehouse-ops` stand on structure. This row does not pre-judge the
  seven; it tells each sibling which leg it will have to argue.
- **NJ-LOG-4 · Is a record-SUBJECT person ever a destination dimension?** A driver's own dossier is
  keyed on a named person the way a patient chart is. `00` forbids *authorship* as a destination, but
  a driver is a subject, not an author. Alternatives: **(a)** never — the dossier groups but never
  folders, this row's default and the reason it proposes no person key; **(b)** a protected-area
  exception mirroring whatever `medical` was granted; **(c)** a canonical record-subject key
  adjudicated globally across `medical`, `hr`, `legal` and this family. Not settled here.
- **NJ-LOG-5 · Reuse, not variants.** `record_type`, `asset` and `site` are taken from the canonical
  row and from `manufacturing`'s proposals rather than re-proposed. If R1c splits any of them, this
  row asks that the split be argued once globally. It also inherits `manufacturing`'s NJ-MFG-3 (is
  `site` distinct from Photos' `location` as subject-versus-capture?) rather than restating it.
- **NJ-LOG-6 · Third-party personal data has no forcing mechanism.** Same gap `construction_property`
  recorded as NJ-CP-4 and `business_operations` recorded independently. This family is a stronger case
  than either, because consignee home addresses and tachograph location histories are its *routine*
  payload, not an edge case. Should be answered with those two rows, not separately.

---

## Recommendations to R1c (never edits — no neighbour file was touched)

1. **`construction_property.materials-delivery`'s NJ-CP-MD-3 can close** in favour of (a) the key.
   Both sides now argue it independently and reject custody for compatible reasons.
2. **`business_operations.procurement-sourcing` should carry the return direction** of the buying/moving
   seam (§3). It declined an edge with this family, correctly, but a declination is not a boundary.
3. **`manufacturing`'s `collides_with.logistics` entry could name `Packing list SO-9912.xlsx`** and
   adopt the quantity-column test, so the fixture is named on both sides as it now is for
   `construction_property`.
4. **`finance.vehicle-records` should carry the mirror sentence** of the operator-duty split, since the
   `role_split` here concedes the default to it.
5. **NJ numbering**: this row uses row-scoped `NJ-LOG-*`, matching the `NJ-CP-MD-*` / `NJ-BO-PS-*`
   convention, to avoid the collision that pass reported.

---

## Audits run before returning

- `python3 -m json.tool` on `logistics.json` → **parses**.
- Key set compared programmatically against `manufacturing.json`, `construction_property.json`,
  `business_operations.json` and `creative.json` (landed J-DEPTH schema anchors) → **identical, in
  order**, all 27 keys.
- **Every `“…”` quotation in the JSON extracted by script and `grep -F`'d against its source.** The
  first run produced **four failures** and all four were fixed by shortening rather than by
  re-wording: a trailing period inside the session quote; a trailing comma inside the
  procurement quote; a two-line wrap in `materials-delivery` that made *“whoever holds the file owns
  the reading”* ungreppable as one string, shortened to *“whoever holds the file”*; and two
  punctuation variants of the collection-point quote. Final run: **0 misses.**
- Every `collides_with`, `also_holds_with`, `role_split` and `also_schema` id checked to exist in
  `roster.json` → **all present**. Every `falls_through_to` name checked against `00` §7.3's nine
  residual templates → **all present**.
- Every `file_examples.source_type` and every `file_kinds.source_types` member checked against
  `src/evidence_shape/vocabulary.py` → **all in `SOURCE_TYPES`**.
- `fields: []`, `dimension_order: []`, `launch: "placeholder"` → **PR-6 shape held**. No canonical key
  minted; three of five proposals are reuse.
- No folder path appears as a fact in any `file_examples` entry; every entry separates `observations`
  from `facts_legal`; two entries carry `group_without_copying_facts: true` for the sparse cases.
- No threshold, statistic, score, file count or regex anywhere in either file.
- `git status` checked: **only the two assigned files were written.**
