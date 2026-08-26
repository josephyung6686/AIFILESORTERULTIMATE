# Research memo — `logistics.fleet-vehicle`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/logistics.fleet-vehicle.json`
Roster row: template on the field-less `logistics` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accept**, and rename. The roster hint calls this "one vehicle across its working life — acquisition,
licensing, insurance, servicing, defects, fuel and disposal." That hint is a *document list*, and as a
document list it is a near-verbatim duplicate of a row that has already landed on a different schema.
The researched node is narrower and is named for what actually activates it: **one identified vehicle
held under a continuing operator duty**. The evidence is not a van, a plate, a make and model or a
garage bill; it is a *duty artefact* keyed on one asset — an inspection at a stated interval, a
driver-reported defect closed by a named rectification signoff, a statutory test result with defect and
advisory items, or an operator authorisation naming a vehicle margin and an operating centre.

## The charge — the strongest case that this row should not exist

I built the case before writing anything, in five forms, strongest first.

**(a) It is a duplicate of a landed neighbour.** `finance.vehicle-records` landed with the one_line
"the records that follow one owned or operated vehicle across acquisition, title and registration,
financing, insurance, inspection, maintenance, recall work and disposal." Set that beside this row's
hint. They are the same sentence with two words swapped. Worse, that row's fixture list already
contains `Certificate of Title`, `Annual Safety Inspection Report`, `Vehicle Maintenance Log.xlsx`,
`Repair Order 004812 - 48000mi.pdf`, `Safety Recall Owner Letter` and — decisively —
`Commercial Auto Policy Fleet Schedule.pdf`. It has already reached into the fleet case. If a landed
row holds all my documents, I hold nothing.

**(b) It is a size, not a kind.** "Fleet" appears to mean only "more than one vehicle." A count is not
a filing world. If the difference between the two rows is the number of rows in a table, this row is a
`work_type` value at best and a threshold at worst, and thresholds are forbidden.

**(c) It is a bundle of document types.** Acquisition, licensing, insurance, servicing, defects, fuel,
disposal — seven nouns, each of which is a `work_type` value. A row whose identity is its list of
document types is a form taxonomy wearing a domain's clothes.

**(d) It is its own schema's default template.** The `logistics` schema row's default reads: the
carrier or trading counterparty only where the corpus spans more than one, then "the custody subject
(the consignment or container; **or, in the fleet and dispatch branches, the vehicle**, the depot or the
working day), then the document function, then time only as a leaf." The schema *already names the
vehicle as its own default's subject*. A template that files by the thing its schema's default already
files by is the default.

**(e) It is a lifecycle stage of something else.** "Working life" is a stage word. An asset's life is
acquisition → operation → disposal, which is a timeline, and timelines are not nodes.

## Defeating the charge

**Against (a) and (b) — the duty artefact, not the count.** `finance.vehicle-records` did not merely
fail to claim the fleet case; it *documented where it stops*. Its `template.why` says its order "is
intentionally scoped inside an accepted one-vehicle group" and that "a multi-vehicle corpus must remain
grouped or flat rather than misuse another field." Its fleet-schedule fixture carries the explicit
`must_not_conclude` "one-vehicle group when several vehicle values are listed." That is a landed row
naming its own boundary from the inside, without knowing this id existed.

But the boundary it names is a count, and a count would not save this row. The discriminator I argue
instead is the **duty**: an external obligation that makes an asset generate documents on a schedule
for as long as it is operated. A sole trader with one van under an operator authorisation, filing
six-weekly inspection sheets and daily walkaround checks, is this row's — one vehicle. A household with
three cars, three titles, three policies and a folder of repair orders is that row's — three vehicles.
The count runs the opposite way to the verdict in both examples, which is how I know the count is not
the test. This survives (b) directly, and it survives (a) because the duty artefact is a *structure*
the finance row's fixture set does not contain: not one of its twenty fixtures carries an inspection
interval, a defect-to-rectification loop, an authorised vehicle margin or an operating centre.

**Against (c) — the documents are values, and are filed as such.** The seven nouns in the hint are in
`work_types[]`, which is where the dispatch prompt says values live. None of them activates anything.
The activating structures in `recognition.deterministic` are compound and are named by shape, not by
document title: *an interval slot beside a numbered check list with dispositions and a fitness
declaration*; *two signatures at two dates against one asset*; *a table whose rows are assets*. The
best evidence that the row is not a document list is that its own collision fixture is a document with
the right title and the wrong structure — see below.

**Against (d) — the deletion is the argument.** This is the leg the node test actually measures, and it
turns on what the schema default *is*, not what it mentions. The default fires on a consignment
structure: two named parties in different roles, one described quantity of goods, a place of taking
over, a place of delivery, an acknowledgement. This row's activating structure contains **none of those
five elements** — no consignor, no consignee, no goods, no place pair, no handover. It has one party
(the filer), one asset, and a recurrence obligation. The two structures cannot be satisfied by the same
file by accident. On dimensions, this row does not shorten the default order, it *deletes its first
level and forbids it*: a fleet asset's file is authored by a licensing authority, a testing station, an
insurer, a lessor and several garages, none of whom is a counterparty to a movement, so a counterparty
level scatters one asset across five branches and answers no question the operator asks. That is
exactly the objection `finance.vehicle-records` raised in its own words about institution-first, reached
independently on a different schema, which I take as corroboration rather than borrowing. And the
default's subject is transient — a consignment dies on delivery — where this row's subject persists and
accumulates, which changes what a time leaf *is*: two inspection sheets on one asset are identical
except for the date, so here the leaf is load-bearing rather than incidental.

**Against (e) — the stages are levels, not the object.** "Acquisition" and "disposal" are two documents
in a file that is dominated by the repeating middle. The object is the asset; the stages are values of
function.

**Privacy is the third independent leg.** The schema's binding family principle is *the consignee is a
party, never a folder*, written to protect a delivery recipient's home address. This row has no
consignee, so it is neither served nor constrained by that rule and must state its own — and its own
runs the other way. Here the record's *subject* is a machine while its incidental content is repeatedly
a named third-party worker: the driver who signed the check, the technician who signed the
rectification, a fuel row that is a timestamped location, a telematics event with coordinates. So: the
asset **may** be a folder (unlike the consignee, an operated vehicle is the filer's own subject), and
the person named on the asset's record **must not** be — and no per-asset record may be aggregated into
a per-person profile. That is a different rule, not a stronger version of the same one.

Three legs, three independent reasons. Verdict: accept.

## Sources actually read

The stamped assignment; the standing brief; `legal.practice-matter-file.research.md` as the depth
calibration; the `logistics` schema anchor JSON in full (default template, family privacy principle,
work types, role splits, NJ-LOG-1..5); `finance.vehicle-records.json` (one_line, template, recognition,
never_alone, work types, four fixtures, open question); `construction_property.plant-hire.json` and
`business_operations.it-asset-inventory.json` (one_line and collision lists only); the two landed
`engineering` rows that had already written a boundary against this id; and `00` by targeted grep only.
Every `00` span in quote marks in the JSON and here was grep-verified verbatim before use. `00` contains
**no** occurrence of *vehicle*, *fleet*, *maintenance*, *registration*, *odometer* or *tachograph* — the
whole subject matter is unlicensed by the design docs, which is why this row's `provenance` is
`inference` and why every design quote used here is a general rule read across, never a domain claim.

## Landed rows that argued against me first

`engineering.aerospace-airworthiness` wrote this seam against this id before this row existed, calling
it "the sharpest same-shape neighbour, because an aircraft is a vehicle with a life record." It named
the fixture bytes in both directions: `N214FR_Hull-Insurance-Certificate-2026.pdf` is mine on both
sides, `AD-Compliance-Record_N214FR_2026.xlsx` is theirs on both sides "and fleet-vehicle must not claim
it merely because it is indexed by the same registration mark." **Confirmed**, with an independent
reason rather than deference: their artefacts prove continued conformity to an *approved type design*,
so the referent is a design authority's document and the registration is only an index into it; my
artefacts assert a *condition on a date*, and the referent is the asset. A directive-compliance record
survives a change of operator; an inspection sheet does not.

`engineering.automotive-program` **refused itself**, and in doing so handed me a fixture:
`Certificate-of-Conformity_WVWZZZ1JZ3W386752.pdf` — "finance.vehicle-records owns purchase,
registration, service and insurance records for a vehicle a person or business owns… logistics.
fleet-vehicle takes the same document when the filer runs a fleet." I accept the fixture and *sharpen
the condition*: not "when the filer runs a fleet" (a count, and unreadable from the bytes) but when a
duty artefact exists independently in the corpus.

## Files considered and rejected

- **`Service invoice 88213 - Marsh Motors - YJ19 KXR.pdf` — the collision fixture.** It has everything
  this row looks for: garage letterhead, a labelled vehicle block, an odometer reading, itemised work on
  the asset, a date. It is not this row's evidence. What discriminates it is the presence of a
  **priced line, a tax treatment, an amount due and a bill-to** — it is a purchase of work on the asset,
  not the record the asset's duty generates. The schema row reached the same ruling in its own
  recognition list, that a single garage invoice does not satisfy the vehicle-lifecycle structure, and
  I confirm it from this side. The absence of an interval, a disposition column and a fitness
  declaration is what completes the discrimination. Routes to Receipts and Confirmations, or coactivates
  `finance.small-business-bookkeeping`. Carried as a file example so the refusal is explicit.
- **`PCN 2026 - YJ19 KXR - Dartford.pdf`** — a keeper-addressed penalty. Registration, date, place,
  amount payable. Tempting because it arrives at the operator and names the asset, but it is a payable
  transactional notice about an event, not a record of the asset's condition, and it names a keeper
  rather than a driver. Receipts and Confirmations.
- **`IMG_2201.jpg`** — a damage photograph with no legible plate. Rejected because an asset identity
  cannot be read from a vehicle appearing in the frame. One-Off Images.
- **`2021 Corolla Owner Manual.pdf`** (a `finance.vehicle-records` fixture) — a manual is reference
  material about a *model*, not a record of an *asset*. Not carried; it is Reading Inbox material and
  belongs to nobody here.
- **A vehicle sales listing, an auction lot sheet and a parts catalogue** — all carry an identification
  string and a make and model. Rejected under `never_alone`; each is a different role for the same token.
- **A fleet-management SaaS account, a maintenance database and a mailbox** — source systems, not file
  nodes. Only a bounded export with a readable manifest is represented.
- **A driver's licence, medical certificate and CPC card** — rejected as `logistics.driver-compliance`'s
  subject, even when filed inside a folder named for a van.
- **A route sheet, a load plan and a delivery manifest** — rejected as `logistics.route-dispatch` and
  `logistics.shipment`. They name the same vehicle; their subject is a working day or a consignment.
- **A hired excavator's on-hire and off-hire pair** — rejected to `construction_property.plant-hire`,
  whose stated core is exactly that pair against a continuing charge.
- **A vehicle-line programme, a type approval and a Certificate of Conformity held by a manufacturer** —
  rejected to `engineering.product-certification` and its siblings, per the automotive row's refusal.

## Proposed fields

**`proposed_fields: []`, `fields: []`, `dimension_order: []`.** Deliberate on all three. `logistics`
declares no field rows under PR-6, so a dimension has nothing legal to branch on; the recommendation is
carried as prose in `template.why`, which is the schema row's own pattern.

I mint nothing, and the reason is a finding rather than a caution: **two competing proposals for this
exact object already exist** — the `logistics` schema row proposes `asset`, and the landed
`finance.vehicle-records` proposes `vehicle`. Adding a third would be the failure the brief names.
Rejected candidates and why: `record_type` is canonical but scoped to Finance and would, if reused here,
quietly re-import that row's whole reading; `asset_id`, `registration`, `vin`, `plate`, `fleet_number`,
`odometer`, `inspection_interval` and `operator` are all variants or slots, and every one of them is a
value on a record rather than a fact that could survive as a folder level; `location` is the Photos key
and an operating centre must never become a destination in any case; `institution` would file one asset
under five issuers, which is the exact error this row's dimension argument rejects.

## Neighbours considered that did not get an edge

- **`business_operations.it-asset-inventory`** (an assigned neighbour). Same *shape* — a maintained
  register of an estate with holders and entitlements — but no shared fixture bytes: its rows are
  laptops and licences, and no roadworthiness duty exists over them. The genuinely confusable table is
  the mixed asset register, and that competition is already carried against
  `manufacturing.asset-register`. A second edge would be shape-matching, not evidence.
- **`retail_hospitality`** (an assigned neighbour). A café's delivery scooter or a restaurant's van
  produces the same documents. But nothing in the retail rows competes for the *bytes*: the seam is the
  duty test again, and where no duty artefact exists the file is `finance.vehicle-records`'. Recorded
  here rather than as an edge.
- **`business_operations.procurement-sourcing` / `.vendor-management`.** The vehicle tender, the
  framework and the supplier relationship are theirs. Expressed as a `role_split` on organization
  instead of a collision, because the objects differ even though the names recur.
- **`logistics.shipment`, `.route-dispatch`, `.warehouse-ops`, `.last-mile-pod`.** Siblings that name the
  same vehicles. No collision: their subjects are a consignment, a working day, a depot and a delivery
  point. The vehicle is an attribute on their records and the subject of mine.
- **`finance.receipts-expenses`.** Absorbed by the Receipts and Confirmations fallthrough and by the
  `finance.small-business-bookkeeping` coactivation; a third finance edge would be noise.
- **`government.transport-authority`.** A real object, but the coactivation is written at schema level
  (`government`) because the authority's identity varies and this row must not encode one jurisdiction's
  regulator into an edge.

## Reciprocal boundaries — the same fixture named on both sides

Every collision in the JSON states both directions and names shared bytes. The three that decide whether
this row survives:

| Neighbour | Shared fixture | This row takes it when | The neighbour takes it when |
|---|---|---|---|
| `finance.vehicle-records` | `V5C - YJ19 KXR.pdf`; the fleet insurance schedule | a duty artefact exists independently in the corpus | no duty artefact does — which is also the conservative default |
| `logistics.driver-compliance` | a `.ddd` tachograph download | the header names the **vehicle unit** | the header names the **driver card** |
| `manufacturing.maintenance-work-order` | an inspection sheet vs a preventive work order | the artefact carries a signed fitness declaration | the artefact carries a work-order number, a planner and a labour booking |

The walkaround sheet is deliberately **not** resolved. It is honestly the vehicle's defect record and
the driver's discharge of a personal duty in the same bytes, so it is left in `also_holds_with` with
`logistics.driver-compliance`, following the schema row's own precedent for the shared delivery note and
`00`'s "One file may hold facts from more than one domain without losing information." That produces a
collision *and* a coactivation to one neighbour on different fixtures, which is flagged for R1c below.

## NEEDS-JOSEPH

1. **NJ-FV-1 — `asset` or `vehicle`?** Two proposed keys for one object now exist across landed rows.
   Not cosmetic: `asset` generalises to plant, containers and equipment and lets a mixed register share
   one key; `vehicle` is narrow and would split a forklift row from a van row inside one table. This row
   mints neither and proposes no third.
2. **NJ-FV-2 — is *duty* the right seam against `finance.vehicle-records`?** The falsifier, stated
   plainly: if R1c judges the duty artefact to be a `work_type` value rather than an activation
   condition, this row collapses into that one and its coverage routes there, plus Independent Records
   and Receipts and Confirmations. Nothing else here would save it.
3. **NJ-FV-3 — may an ASSET be a destination dimension, and must its label be an alias?** This row
   asserts yes-with-alias and flags that it is asserting rather than citing; `00` licenses no view. This
   is the schema's own NJ-LOG-4 approached from the opposite side, and this row's answer for *people* is
   a flat never.
4. **NJ-FV-4 — collision and coactivation to the same neighbour.** Legal under CONNECTION.md on
   different fixtures, or a contradiction? The schema row set the precedent; R1c should ratify it rather
   than let it stand by imitation.
5. **NJ-FV-5 — recommendation to R1c, not a change made here.** `finance.vehicle-records` landed without
   knowing this id existed and carries `Commercial Auto Policy Fleet Schedule.pdf` with no reciprocal
   edge. This row writes the boundary from its side only. R1c should add the return edge there; this
   memo records the request rather than touching a neighbour's file.

## Self-verification

`python3 -m json.tool` parses the node. Key set matches the landed siblings, plus the `node_test` and
`proposed_context_terms` keys the `logistics` anchor and the landed engineering rows already carry.
Every `source_type` in `file_examples` is in `SOURCE_TYPES`. Every edge id is on `roster.json`; every
`falls_through_to` name is one of `00`'s residual templates. Every quoted `00` span was grep-verified
verbatim before it was written. No threshold, count, statistic or handling class appears anywhere. No
file example writes a folder path as a fact. `fields` and `proposed_fields` are empty. Only the two
assigned files were written.
