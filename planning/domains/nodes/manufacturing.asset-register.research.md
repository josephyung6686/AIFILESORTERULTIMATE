# Research memo — `manufacturing.asset-register`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/manufacturing.asset-register.json`
Roster row: template on the fieldless `manufacturing` schema, `parent_id: null`, `launch: placeholder`
Status: **SALVAGE ROW.** A killed agent left JSON with no memo. This memo owns the repaired result.

## Result

Accept the node. The row survives a serious refusal charge, but only on one argument, and it is worth
stating the argument narrowly rather than broadly: **the schema's default template cannot place this
row's central file at all.** Every other difference I could find is decoration on top of that.

The manufacturing default is branch-shaped. Its maintenance branch, quoted from the anchor's own
`template.why`, is "site then asset then record type for maintenance and calibration". That branch
requires a single `asset` value to pick a folder. A plant equipment register has no single asset
value — it has three hundred, and none of them is the file's subject. The default template is not
merely a poor fit for a register; applied to one, it is undefined. That is the node test's
`dimensions_differ` leg passing on inapplicability rather than on preference, which is the only
version of that leg I trust.

## What I changed in the salvaged draft

The draft was substantially right and cost real tokens; I kept its spine, its file set and most of
its recognition list. Six repairs:

1. **Added three missing collisions.** The draft had three edges. Five landed neighbours had already
   authored boundaries *against* this row and the draft answered only one of them properly. Added
   `manufacturing.calibration-record`, `logistics.fleet-vehicle` and `engineering.commissioning-handover`.
2. **Repaired the maintenance-work-order edge to name the same fixture as the neighbour.** The draft
   named `PM Work Order CNC-07 2026-08.pdf`; the landed neighbour names `Asset card CNC-07.pdf` /
   `Work order history CNC-07 2019-2026.xlsx` and discriminates on "what a row IS". Two rows naming
   two different fixtures is not a reciprocal boundary. Adopted the neighbour's fixtures and its
   wording, and put both files in `file_examples` so P8 can see the pair.
3. **Deleted the invented `asset_class` dimension level.** The draft recommended "site or line, then
   asset class, then asset" while itself admitting "asset_class has not been licensed". No such key
   exists anywhere on the roster. Inventing a level in prose to make a dimension order look richer is
   exactly the padding the brief forbids. The order is now site, then asset — with a restriction.
4. **Rewrote the dimension argument on inapplicability** rather than on "record_type would be a
   constant single-child level", which was a weak reason (the same is true of half the roster).
5. **Removed `facts_legal: ["asset", ...]` from every multi-asset fixture.** The draft let a register
   export yield an `asset` fact. It cannot: the file carries many asset values and asserting one
   would be the product manufacturing a fact. This is the sharpest correctness bug in the draft.
6. **Dropped the `node_test` object from the JSON.** No landed sibling carries that key; key parity
   against `manufacturing.maintenance-work-order.json` is now exact. The three legs are argued below,
   at more length than a JSON field could carry.

I checked the sibling-salvage warning: **no dangling neighbour id.** All six edge targets — including
`manufacturing.spare-parts`, which has not yet landed a node file — are present in `roster.json`.

## THE CHARGE — the strongest case that this row should not exist

I can build four independent arguments for refusing it, and one of them nearly succeeds.

**Charge 1 — it is a work_type value of its own schema.** The manufacturing anchor's `work_types`
list contains, verbatim: `"asset register, spare-parts list or maintenance schedule"`. The brief names
this failure mode explicitly. A row whose name is lifted from its own schema's value list is the
574's original mistake wearing a node's clothes.

**Charge 2 — the schema's deterministic union already fires on it.** This is the serious one. The
anchor's `recognition.deterministic` already contains: *"an asset register row set with stable asset
identifiers, equipment descriptions, site or line, service/calibration interval and status, where
multiple rows prove a controlled population rather than one purchase."* If the schema already detects
the register, a template adding the same signal adds nothing to activation. Under CONNECTION §2 a
template earns existence when its detection signals, dimensions or privacy rules differ from the
schema's default — and here the detection signal is not merely similar, it is the same sentence.

**Charge 3 — it is a document type.** "Register" is a shape of document: a table listing things. The
roster refuses rows defined by a medium, a length or a format, and "the file that is a list" is
uncomfortably close to that family.

**Charge 4 — it is a row defined by absence.** Its whole boundary set is negative: not a work order
(no performed job), not a calibration record (no outcome column), not spare parts (not consumed), not
a fixed-asset register (no depreciation), not IT (no hostname). A row that is only the residue after
its neighbours take their files is not a node; it is a gap.

### Defeating the charge

**Against Charge 2, which must be answered first.** The node test does not measure a template against
its schema's *recognition union*. It measures it against the schema's *default template*. Those are
different objects with different owners — CONNECTION §7 gives the schema to P6 ("which fact fields are
legal") and the template to P10 ("which of those fields may become folder levels, and in what
recommended order; detection signals; privacy rules"). The anchor's deterministic entry says the
manufacturing *schema* activates on a register. It does not say where the register goes, and the
default template's answer to that question is undefined, as argued above. So Charge 2 proves this row
is not needed for *activation* — which I concede — and says nothing about placement, which is what a
template is for. I have written the row's recognition list accordingly: it does not restate the
schema signal, it adds the *discriminations* the schema never has to make, because the schema is
choosing whether manufacturing is plausible while this row is choosing between five siblings that are
all manufacturing.

**Against Charge 1.** The value in the anchor's `work_types` is the phrase "asset register". This row
is not that phrase; it is a shape — *the rows are assets* — which happens to be what people call an
asset register. The test is whether the row would still exist if the phrase vanished, and it would:
`Equipment Master Export 2026-08-01.xml` is never called a register by anyone, carries no such word
anywhere in its bytes, and is squarely this row's file. Conversely, `Fixed Asset Register FY26.xlsx`
carries the phrase in its filename and is *not* this row's file. The name and the row cross.

**Against Charge 3.** A document type would admit any list. This row rejects `Equipment and Spares
Master.xlsx`'s parts rows, rejects a supplier's product catalogue, rejects a stock count sheet and
rejects a fleet's road-going rows — all of which are tables listing equipment-shaped things. The
admission criterion is not tabularity, it is the conjunction of *stable identity + installed position
+ standing obligation*. Two of three is not enough: a stock sheet has identity and position (bin) but
no standing obligation; a delivery note has identity and an obligation (warranty) but no installed
position.

**Against Charge 4.** The boundaries read negative because five siblings landed first and each took a
verb — performing, calibrating, consuming, delivering, depreciating. What is left is not a residue but
the only *noun* in the family: the thing the verbs are done to. Every neighbour's edge, written by
that neighbour before I arrived, presupposes this row's existence to state its own boundary —
`manufacturing.maintenance-work-order`'s `one_line` says outright that it is "not what the asset IS
(manufacturing.asset-register)". A row that four landed neighbours independently needed in order to
define themselves is load-bearing, not residual. That is corroboration I did not author.

**Verdict: accept**, on the placement argument, with the activation contribution honestly reduced to
"discriminates among manufacturing siblings" rather than "detects manufacturing".

## The node test, all three legs

**Leg 1 — dimensions differ.** Argued above and the strongest leg. The default's maintenance branch
is site → asset → record_type. For a multi-asset register that is undefined at the asset level. This
row's order is site (or line), then asset *only where the file carries one asset value* — an asset
card, a history index. Record type is dropped: the register **is** the record type, so the level
would have one child in every branch. No time-first level, on 00's own rule, grep-verified verbatim:
*"For document and record domains, project, function, or subject usually comes before time because
putting year first scatters related work across calendar folders."* Annual register exports are
versions of one enduring document, and a year-first order would shred that version family across
calendar folders — precisely the harm the sentence names.

This leg surfaced NJ-MFG-ASSET-4, which I could not settle: `asset` is destination-eligible for some
of this row's files and not others. Per-file destination eligibility may not be a thing the contract
allows. I have surfaced it rather than smoothed it.

**Leg 2 — signals differ.** The default template's maintenance-branch signals are per-record
structures: work performed, parts used, as-found and as-left values, failure codes, return-to-service
approval. This row's signal is the inverse and includes a *negative*: a stable header over two or more
asset identities, each joined to an installed position and at least one standing obligation, **and no
per-row outcome column.** That negative is the entire boundary with `manufacturing.calibration-record`
and it is not expressible in the default template, which never has to distinguish a roster from a
result. The row also carries a discrimination the schema does not need: a next-due date is a
*scheduling attribute of a population*, not evidence that anything happened — which is why
`Calibration due list 2026-Q4.xlsx` sits here and a due-list with an as-found column does not.

**Leg 3 — privacy differs.** Weaker than the other two, and I will not overclaim it: the catalogue
value is `potentially_sensitive` on both sides, and the anchor's `sensitivity_why` already names
"plant layouts, asset condition". The genuine difference is **aggregation**. A work order exposes one
machine on one day. A register exposes the complete productive capability of a plant — every machine,
its exact installed position, its criticality ranking, its condition, its service vulnerabilities —
in one file, and a disposal register additionally exposes forward plans. The operational consequence
I have written into the row is concrete rather than rhetorical: a compact evidence packet for this row
should carry **column roles and row counts, not register contents**, because excerpting a register
means excerpting the plant. That is a review rule the default template does not need. Marked as
inference; 00 does not discuss operational exploitability of a plant inventory and I have invented no
quotation for it. No handling class is assigned; P7 owns that vocabulary.

## Files considered and rejected

Naming what is *not* this row's evidence did more work here than naming what is.

- **`Packing list - CNC spindle unit SN883104.pdf`** — a serial number, an equipment description and a
  ship-to address. Rejected: a delivery proves a transaction, not standing control. The ship-to
  address is not an installed position, and nothing in the file says the unit was ever commissioned.
  Falls to Receipts and Confirmations.
- **`PO 45001982`-shaped purchase records** — rejected for the same reason, and the anchor already
  routes them: its `never_alone` list ends with "an invoice, purchase order, packing list or delivery
  receipt alone; those are procurement/logistics evidence until a lot-acceptance or equipment-control
  structure independently supports manufacturing."
- **A maintenance manual for a machine model** — the tempting one, because it names equipment in
  detail. Rejected: a manual describes a *model*, not an owned instance. No identity, no position, no
  obligation. The anchor lists it under `needs_llm` for the same reason.
- **A spare-parts stock sheet** — item, description, location, quantity, reorder level. Rejected: the
  "location" is a bin, and the thing is held and consumed rather than installed and maintained.
- **A supplier equipment catalogue** — equipment names, models, specifications, photographs. Rejected:
  goods for sale by someone else. No ownership evidence of any kind.
- **A CMMS database file or a live maintenance system** — a source system, not a file node. A bounded
  export with a readable manifest is represented; connector ingestion is a later security decision.
- **A single equipment nameplate photograph** — rejected unless it joins an accepted asset
  neighbourhood; alone it is One-Off Images, and it must not acquire an asset fact by proximity.
- **A machine-condition sensor log or vibration trace** — rejected: condition *monitoring* is a time
  series of measurements, not a population document. It would need its own row or the schema's line-log
  branch; it is not this one and I have not invented an edge for it.

## The collision fixture

The required fixture is **`Fixed Asset Register FY26.xlsx`**, and it is the best one because it fails
in the most tempting way: it contains the words "Asset Register", it contains real machine identities,
real lines and real service statuses, and a sheet-one excerpt would be indistinguishable from this
row's evidence. It is nonetheless not this row's file as a whole. Sheet two carries Acquisition Cost,
Depreciation Method, Accumulated Depreciation and Net Book Value against the same tags. **What
discriminates it:** the workbook's purpose is a finance control — the register exists to support a
depreciation schedule, and the machine columns are there to identify what is being depreciated. The
custody columns are ancillary. A repeated serial across two sheets does not let evidence from one
count for the other, and the filename phrase decides nothing. In practice both schemas may activate on
disjoint evidence, which is why the fixture carries `also_schema: finance` and drives NJ-MFG-ASSET-1.

Two secondary collision fixtures earn their place: `Packing list - CNC spindle unit SN883104.pdf`
(above) and **`Work order history CNC-07 2019-2026.xlsx`**, which is the same machine, the same
system and the same columns as an asset card, and is discriminated only by what a row IS.

## Reciprocal boundaries

Six, each naming the same fixture bytes on both sides. Four were authored by the neighbour first and I
have aligned to their wording rather than coining my own.

- **`business_operations.it-asset-inventory`** — fixture `CNC network and maintenance inventory.csv`.
  Machine number, line, criticality, next PM here; hostname, OS, licence entitlement, network address
  there; the shared asset tag counts for neither. The neighbour states the identical discriminator
  from its side, though without naming a fixture — a recommendation for R1c below.
- **`manufacturing.maintenance-work-order`** — fixtures `Asset card CNC-07.pdf` and `Work order
  history CNC-07 2019-2026.xlsx`. Rows-are-assets here, rows-are-events there. A register with a Next
  PM Due column is still mine; a history with an equipment column is still theirs.
- **`manufacturing.calibration-record`** — fixture `Calibration due list 2026-Q4.xlsx`. Population
  attributes only here; a per-instrument outcome or as-found status there. A next-due date does not
  move the file, because a due date is scheduling, not evidence of an event.
- **`logistics.fleet-vehicle`** — fixture `Fleet list - inspection due 2026.xlsx`. Fixed or site-bound
  equipment with cost-centre columns here; registration-shaped identifiers, plated weights and
  statutory test dates there, because those columns exist only because of an external roadworthiness
  duty. A forklift row here, a van row there, a mixed table groups without either side copying facts.
- **`manufacturing.spare-parts`** — fixture `Equipment and Spares Master.xlsx`. Installed and
  maintained here; held and consumed there. Item number and location discriminate neither. (That row
  has not landed a node file yet; the boundary is written to be adoptable verbatim from its side.)
- **`engineering.commissioning-handover`** — fixture `Asset Handover Schedule - Line 3.xlsx`. The unit
  as a delivered deliverable there — as-built definition, acceptance evidence, punch items, warranty
  start; the same unit as an operated asset here — register row, criticality, maintenance regime,
  in-service history. The handover schedule is the seed of the register.

## Recommendations for R1c (this row edited no neighbour)

1. **`engineering.commissioning-handover` mis-types its edge to this row.** It authors a `role_split`
   whose value is a domain id. CONNECTION §5 types `role_split` as "field ↔ field (lives in the
   canonical field list, section 6)" and §6 gives its only examples as `authored_by ↔ target_school`,
   `our_firm ↔ client`, `school ↔ target_university`. A domain-valued `role_split` is outside the
   vocabulary and the gate should catch it. I recorded my side as a `collides_with` and left
   `role_split: []`. R1c should either re-type the neighbour's entry or extend the vocabulary — see
   NJ-MFG-ASSET-2. I did not touch the file.
2. **`business_operations.it-asset-inventory`'s signal names no fixture.** It states the right
   discriminator but records no file both rows would claim, which is the shape P6 step 3 and P8 can
   act on. Suggest it adopt `CNC network and maintenance inventory.csv`, as my side does.
3. **`asset` should be adjudicated once, on the schema.** Three rows now second it — this one, the
   calibration row and the commissioning row — and none should be counted as a competing proposal.
4. **`also_holds_with` is empty and should stay empty.** CONNECTION §5 makes it schema ↔ schema only
   and this row is a template. The genuine coactivations are recorded per-fixture instead
   (`also_schema: finance` on the fixed-asset workbook, `engineering` on the handover schedule,
   `photos` on the register photograph) for R1c to lift to the schema level if it agrees.

## Fields, and what was rejected

`fields: []` — the manufacturing schema declares none under PR-6 and D1's deferral stands.
`proposed_fields` seconds exactly two of the anchor's existing proposals, `asset` and `site`, both
flagged SECONDING and both routed to a single R1c adjudication. Nothing is minted.

Rejected candidates: `asset_class` (deleted from the draft — unlicensed anywhere and invented purely
to lengthen a dimension order); `criticality`, `functional_location`, `in_service_status` (attributes
of a row, not organizing parents — no one browses a plant by criticality); `record_type` (a
single-child level for every branch of this row, and its canonical role is Finance-scoped and already
under NJ-MFG-1); `location` (Photos capture-place, wrong role); `organization` (custodian, never-alone
evidence in its own right).

## Residual routing

All four route through 00's named residual homes, quoted verbatim in the JSON:

- **Independent Records** — "standalone certificates, notices, confirmations, forms, and PDFs that
  have a durable purpose but no broader group": a lone manual, warranty card or asset card.
- **Receipts and Confirmations** — "isolated invoices, delivery confirmations, booking records,
  boarding passes, purchase receipts, event tickets, and similar transactional documents": the packing
  list and every purchase or disposal acknowledgement.
- **One-Off Images** — "images with no event, project, reference collection, or photo-family
  association": the unreadable equipment photograph, which must not acquire an asset fact.
- **Review Later** — files "whose meaning is partly understood but whose final location requires a
  future decision": the OCR-poor list, the mixed plant-and-vehicle table, the handover schedule whose
  side of the transfer is unresolved.

## NEEDS-JOSEPH

1. **NJ-MFG-ASSET-1** — a workbook with a custody sheet and a depreciation sheet for the same
   machines. *Alternatives:* (a) present one multi-schema file with sheet-level evidence spans and let
   both schemas hold it; (b) require the user to pick a primary placement once both activate; (c) treat
   sheet boundaries as file boundaries for placement. The catalogue can state the boundary; it cannot
   choose the review interaction.
2. **NJ-MFG-ASSET-2** — the domain-valued `role_split` on `engineering.commissioning-handover`.
   *Alternatives:* (a) re-type it as `collides_with`, matching what I wrote; (b) add a domain-to-domain
   lifecycle-handover relation to the closed vocabulary; (c) express it as an `engineering` ↔
   `manufacturing` `also_holds_with` at the schema level, where it may genuinely belong.
3. **NJ-MFG-ASSET-3** — one `asset` key is being asked to carry a producing machine, a measuring
   instrument (calibration's NJ-CAL-1) and a delivered installed instance. *Alternatives:* (a) one key
   plus a role distinction; (b) a canonical role split; (c) separate keys, which risks three synonyms.
4. **NJ-MFG-ASSET-4** — `asset` is destination-eligible for a single-asset card and undefined for a
   multi-asset register. *Alternatives:* (a) allow per-file destination eligibility, which may break
   P10's freeze model; (b) declare the register a site-level document that simply never uses the asset
   level, which is what the JSON currently recommends; (c) split this row in two, which I resisted
   because the asset card and the register are the same document at two cardinalities.

## Final recommendation

Keep `manufacturing.asset-register` as a placeholder template with no fields, no serialized
dimensions, no schema coactivation edge and no time-first hierarchy. Its discriminator is
**rows-are-assets plus installed position plus a standing obligation, and no per-row outcome column.**
Its claim to exist is that the schema default cannot place a population document. Route everything
that fails the conjunction to a residual rather than letting a serial number, a due date or the phrase
"asset register" manufacture an asset fact.
