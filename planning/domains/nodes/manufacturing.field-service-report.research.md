# Research memo — `manufacturing.field-service-report`

Depth: J-DEPTH
Date: 2026-08-27
Output: `planning/domains/nodes/manufacturing.field-service-report.json`
Roster row: template on the fieldless `manufacturing` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accept**, on a narrower claim than the roster hint states, and with one leg of the node test
recorded as partially failing rather than smoothed.

The roster hint reads "What an engineer found and did at a customer's site." That sentence, taken
literally, is a document type plus an organisation name, and would not survive the charge below.
What survives is narrower and structural: **the servicing party's closure of one attendance at a
third party's serialised installed unit under an entitlement.** The holder made nothing, operates
nothing, and owns no site in these files. Every anchor the manufacturing schema recommends —
product, batch/lot, the holder's own plant and line, the holder's own calibrated instrument — is
absent by construction. That absence is not what licenses the row; the row is licensed by what
replaces those anchors, which is a customer, a unit that is somebody else's property, and a
coverage position.

## Sources used

The standing brief and the stamped assignment; `manufacturing.json` (the schema anchor and the
node-test comparator) in full; `legal.practice-matter-file.research.md` as the one depth
calibration; targeted greps of `00` for the six spans quoted in the JSON, each verified verbatim
(`00` was not streamed); the three landed neighbours that had already argued a boundary against
this id, read only at the matched spans — `manufacturing.maintenance-work-order.json`,
`manufacturing.warranty-claim.json`, `construction_property.trade-job.json`, plus one line of
`engineering.verification-validation.research.md`; `canonical_fields.json` at the `client` entry;
`roster.json` for this row and the edge ids; and `SOURCE_TYPES`, checked programmatically.

## THE CHARGE — the strongest case that this row should not exist

Stated before the defence, and stated at full strength. Six independent attacks, in descending
order of force.

**1. It is a work_type value of its own schema.** This is the strongest attack, and it is written
into the schema anchor's own text. `manufacturing.json` `work_types[]` contains, as one enum
value: *"maintenance request, work order, service report or breakdown log"*. The words "service
report" are literally a value in the schema's list of values. The brief is explicit that work types
are values and not nodes. On its face this row is a value that has been promoted to an id.

**2. It is a duplicate of `manufacturing.maintenance-work-order`, differing only in who holds the
file.** That row has landed and has already authored both a `collides_with` and a `role_split`
against this id, describing "the same entity type — one job performed on one machine — split by
holder role rather than by content, and keyed on the same proposed `asset` and `work_order`
handles." If the entity is the same and the handles are the same, holder role looks like a *field
value* — a role — and the catalogue already owns an edge type, `role_split`, whose whole purpose is
to express exactly that without minting a second node.

**3. It is a duplicate of `construction_property.trade-job` across a sector name.** That row states
of this one: "A field-service visit report is byte-for-byte this row's job sheet in a different
sector, produced by the same class of software." Byte-for-byte identity separated by an industry
label is the 574's recorded failure mode. Worse, that row's own `open_question` names the condition
under which it dissolves: if its work-performed structure is conceded to
`manufacturing.field-service-report`, it "IS a residual wearing a domain's clothes". Two rows
cannot both be the home of one structure; at least one of them is padding.

**4. It is a lifecycle stage.** In-service, post-delivery, post-commissioning. The same unit is
covered by engineering before it is built, by production while it is made, by verification when it
is accepted, by this row while it runs, and by warranty when it fails under cover. A stage on a
timeline is not an organizational situation.

**5. It is a document type plus an organisation name.** "Report" is a document type word. "At a
customer's site" is an organisation name and an address. Both are on the schema's own `never_alone`
list — "a product name, part number, SKU, organization name, supplier name, site name or postal
address alone". A row whose whole identity is a document word plus never-alone evidence can never
activate.

**6. It is defined by an absence.** No lot, no plant, no line, no internal cost centre. Everything
distinctive about this row on first inspection is a thing the schema default has and this row
lacks. A row defined by what is missing is not a row.

## The defence, and where it does not reach

**Against attack 1.** The enum value naming "service report" sits inside a single value whose other
members are "maintenance request, work order... breakdown log" — that value is *the internal
maintenance job*, and it is what `manufacturing.maintenance-work-order` was built on. This row is
not that value. What it recognises is not a document called a service report but a conjunction no
work_type expresses: a customer block **distinct from the letterhead**, a unit belonging to that
customer, an attendance period, a work/parts/labour triple, an entitlement position, and an
**acceptance signed by the party who owns the machine**. The row's own `never_alone` says so
directly: the words *field service, service report, call-out, engineer* never fire.

**Against attack 2 — the decisive one.** `role_split` in this catalogue splits *fields*, not
corpora, and what changes here is not one field value: it is which anchors exist at all. In an
operator's corpus the file hangs under the operator's own site and asset register, both of which
the operator possesses. In a servicing vendor's corpus neither exists — the vendor has no site in
the schema's sense ("the facility that performs production"), and the machine is in someone else's
register. What the vendor has instead is a **customer** and a **contract**, and the customer is the
level the corpus is actually organised by, because one vendor's corpus is many customers × many
units × many visits. Detection signals differ and the recommended first dimension differs in kind
rather than in order, both as consequences of the same fact. That is a template, not a role value.
The `role_split` is authored **as well**, reciprocally and in that row's own words, because both
statements are true: the entity is shared, the situations are not.

**Against attack 3.** Not fully defeated, and it is recorded as **NJ-FSR-3** rather than argued
away. The concession this memo makes is real and costs the row territory: single-appliance work at
a dwelling is **ceded to `construction_property.trade-job`**, because on that fixture the premises,
not the unit, is what the corpus is organised by. This row keeps the file only when the subject is
the unit and the unit survives the address — a leased forklift, a lift car, a CT scanner, a chiller
relocated between towers — under a named service contract, with a visit history that persists
across the move. Sector is explicitly *not* the discriminator; portability of the subject is. Where
neither unit history nor contract is evidenced, the property wins and this row abstains.

**Against attack 4.** The lifecycle observation is true and is not sufficient to refuse, because
this row is not claiming the stage — it is claiming a *transaction that recurs within* the stage.
The unit is in service for twenty years; the row's object is the individual attendance, of which
there are many, each with its own reference, times, parts and acceptance. Verification-validation
takes the unit once at acceptance; warranty takes it when a claim is raised; this row takes it
every time somebody attends. A stage happens once; this happens on a schedule.

**Against attack 5.** Correct, and it is why the deterministic list opens by naming the conjunction
and why the `never_alone` list is longer than the schema's. The most useful line there is the one
about the **captured signature image**, added because it is the most tempting false discriminator
in this exact neighbourhood: `construction_property.trade-job` explicitly *withdrew* the claim that
a signature-on-a-work-record is distinctive, and `construction_property.materials-delivery` carries
one for entirely different bytes. A signature proves that somebody accepted something.

**Against attack 6.** This is the attack the memo takes most seriously, and it changed the row. The
`one_line` and the `template.why` are deliberately written so that the row's claim is what is
*present* — customer, third-party unit, entitlement, acceptance — with the absences recorded only
as the reason the schema default's dimensions cannot be reused. If R1c strips the customer level
(NJ-FSR-1), the row loses its positive content and should be re-examined for refusal.

## The node test, all three legs

**The schema's default template**, quoted from `manufacturing.json`: `dimension_order: []` with a
prose recommendation that is "intentionally branch-shaped rather than one deep tree: product then
batch/lot then record type for production and quality records; site then asset then record type for
maintenance and calibration; quality event then record type for NCR/CAPA files." Its default
detection presumes a holder who transforms material or operates a controlled asset. Its default
privacy posture is the holder's own commercial confidentiality plus named workers.

**Leg 1 — detection signals differ. PASSES.** The schema's twelve deterministic signals all assume
the holder's own transformation or the holder's own asset: travellers, genealogy, in-process
inspection, calibration of the holder's instrument, the holder's line log, the holder's HSE. Not
one of them fires on a vendor's corpus, because the vendor makes nothing and owns none of the
machines. This row's fingerprint — the closure conjunction plus the **entitlement/chargeability
structure** — appears nowhere in the schema's list and nowhere in any landed sibling.
`maintenance-work-order` occupies that slot with a cost centre and an internal requestor.
`warranty-claim` has entitlement but *not* performed work: on that side the unit travels back and a
settlement is adjudicated. `asset-register` is a population, `calibration-record` is metrological.
The conjunction is genuinely unclaimed.

**Leg 2 — recommended dimensions differ. PASSES, and is the strongest leg.** The difference is not
an ordering preference; it is that neither of the schema's two branch recommendations is *available*
here. `product` and `batch_lot` do not exist because nothing was made. `site` is defined in the
schema anchor as "the facility that performs production" — the holder's plant — and the only site
in these files belongs to a third party, so using it would be a category error, not a reordering.
The recommendation is **client → asset → visit**, whose first level uses a canonical key
(`client`: "the counterparty organization an engagement serves", aliases including *customer*,
`destination_eligible: true`) that the manufacturing schema does not carry at all. A new first
level of a different kind is the clearest form leg 2 can take. It also satisfies 00's ordering rule
directly — "a parent dimension should provide the context required to understand the child" — since
a visit is unintelligible without the unit and a unit serial is unique only within a manufacturer's
series, so it needs the customer to disambiguate it in a many-customer corpus.

**Leg 3 — privacy rules differ. PASSES against the schema default; PARTIALLY FAILS against one
sibling. Recorded as failing rather than smoothed.** Against the default the difference is a real
inversion: the default protects the holder's own secrets, whereas here the holder is a custodian
and essentially the entire corpus is about other parties — their premises, equipment, fault
histories, access routes, alarm procedures and key holders. At volume that is an access map to
buildings the holder does not own, and the exposed parties cannot consent. Two consequences are
actually distinguishing: a `Protected Records` route for access/credential members of a visit pack,
and the treatment of the vendor's own engineers, whose attendance times and GPS-tagged site
photographs make the corpus a **movement record about named individuals** — an exposure the schema
default does not carry at all. **But** `manufacturing.maintenance-work-order`'s own
`sensitivity_why` already names third-party service data in one clause ("a field-service copy of
the same job names a customer's site, their equipment and their fault history"). Against that
sibling this leg reduces to *the third party is the entire subject rather than one clause*, which is
closer to scale than to kind, and `construction_property.trade-job` was right to refuse to let
volume count as evidence. The leg is recorded as passing on the comparator the node test actually
names (the schema default) and as weak against the sibling.

Two of three legs are strong and independent, and the row's claim does not rest on privacy. Accept.

## Files considered and REJECTED — the tempting false positives

- **`WO-8814 CNC-07 spindle alarm.xml`** — the schema anchor's own fixture, rejected despite a
  perfect work-performed structure: internal requestor, cost centre, returned-to-service approval
  signed by the holder's own supervisor. Operator side. Kept in `file_examples` precisely to show a
  work-performed triple is not this row's evidence.
- **`Installation and Commissioning Report - chiller CH-02 - Tower B.pdf`** — the collision fixture,
  below.
- **`Invoice INV-9912 - service call FS-20416.pdf`** — quotes the call reference as a line-item
  narrative but has no work-carried-out text, no attendance times, no acceptance. A quoted
  reference is not a closure → `Receipts and Confirmations`.
- **`Engineer schedule week 34.ics`** — calendar entries evidence intent to attend, never
  attendance. Groups without copying facts; a shared van, day or route must not propagate customer
  or unit facts between calls.
- **`Service manual PR-330 rev C.pdf`, spare-parts catalogues** — instructions describe how a
  machine is serviced and evidence no visit. The schema anchor already flags this shape ("a
  maintenance manual that describes how to service a machine but does not evidence any owned asset
  or performed work"); the vendor-side version is the same trap.
- **`PM schedule 2026 - all customers.xlsx`** — a plan of visits not yet performed is a planning
  artefact, closer to `manufacturing.production-planning` and `business_operations`.
- **`RMA-7741 returned unit AX410.pdf`** — the unit leaving site is the tell;
  `manufacturing.warranty-claim`.
- **`Customers.csv`** — a contacts corpus. Organisation names at volume are still never-alone.
- **`Site access - Meridian Tower plant room - alarm and key holder.pdf`** — rejected as a *service
  record* but retained as a fixture, because it will sit in visit folders and must route to
  `Protected Records` rather than be absorbed by proximity. Folder co-location is not evidence.

## THE COLLISION FIXTURE

**`Installation and Commissioning Report - chiller CH-02 - Tower B.pdf`.**

It matches this row on every surface feature: an engineer from the supplying company, at a
customer's site, working on a serialised unit, recording readings and parts, signed for by the
customer, produced by the same field software, filed in the same folder tree, often with the same
reference series.

It is not this row's evidence. What discriminates it is a **specification column and a taking-over
statement**. A commissioning report proves that a unit meets its stated specification at *first
acceptance* — setpoints against design values, a witness-test column, a handover into an
operation-and-maintenance pack, a one-time event with no prior visit and no fault. This row's
evidence records a **fault or a scheduled task on an already-accepted, already-in-service unit**,
and carries the two things commissioning cannot: an entitlement position (because there is nothing
to charge for at handover — the work is part of the supply) and a place in a visit sequence.
Reciprocally: this row must not claim a commissioning report because an engineer signed it at a
customer site, and `engineering.verification-validation` / the construction handover rows must not
claim a service report because it contains recorded readings.

Where the report is ambiguous — a first-year "commissioning-and-first-service" hybrid is common —
the file goes to `Review Later`. It is not assigned by guess.

## Reciprocal boundaries — stated in both directions, same fixture on both sides

All six are in `collides_with` as objects with the discriminator, not as bare ids. Summarised here
with the shared fixture named once:

| Neighbour | Shared fixture | This row keeps it when | The neighbour keeps it when |
|---|---|---|---|
| `manufacturing.maintenance-work-order` | `Service report SR-4471 - press at Acme Plant 2.pdf` | holder is the servicing vendor: customer block ≠ letterhead, entitlement reference, covered/chargeable split, **customer's** acceptance | holder operates the machine: internal requestor, cost centre, plant location, **holder's** returned-to-service approval |
| `manufacturing.warranty-claim` | `Service Visit SV-4881 - AX410 leak.pdf` | the document **closes a visit**: attendance times, work carried out, parts, outcome at the machine | the document **adjudicates a claim**: allegation, entitlement, returned-unit custody, settlement |
| `construction_property.trade-job` | `Boiler service - 14 Elm Road - ecoTEC serial 0020188.pdf` | the **unit** is the subject and survives a change of address, under a named service contract | the **premises** is the subject: property address, trade identity, no unit history — including, per the concession above, single-appliance work at a dwelling |
| `business_operations` | `Jobs 2026.xlsx` | the file is the **closure of one job**: work-carried-out narrative plus acceptance | the file is a **register of many jobs**: status, value, scheduling and pipeline columns |
| `logistics` | `Parts to site FS-20416.pdf` | the part is recorded as **fitted** during an attendance, charged to a call, no balance, no carrier | the part is recorded as **moved**: ship-to ≠ bill-to, carrier and tracking, received-by for the consignment |
| `engineering` | `Field change FCO-118 - PR-330 guard interlock.pdf` | the document records **performance at one installation**: which serial, date, engineer, parts, accepted by whom | the document **authorises a change across a population**: affected item, revision from/to, rationale, approvals, effectivity |

The three landed rows above (`maintenance-work-order`, `warranty-claim`, `trade-job`) had already
authored their halves. Their phrasing is adopted rather than re-authored, so the two sides read as
one sentence; the only place this memo departs from a landed neighbour is the narrowing recorded
against `trade-job`, which **cedes** territory rather than taking it, and which is surfaced as
NJ-FSR-3 because that row's continued existence partly depends on it.

## Neighbours considered that did NOT get an edge

- **`manufacturing.failure-analysis`** — a repeat-visit history could feed an analysis, but this row
  never argues a cause from assembled evidence, and `maintenance-work-order` already authored that
  seam in terms that apply unchanged. A third statement would be duplication.
- **`manufacturing.asset-register`** — a vendor's installed-base list resembles an asset register,
  but the units are not the holder's assets and the seam is already carried by NJ-FSR-2.
- **`manufacturing.inspection-record` / `calibration-record`** — an engineer may take measurements
  on site, but neither a spec-versus-result table nor an as-found/as-left pair is what closes a
  visit, and neither row would claim a closure report.
- **`photos`** — coactivation, recorded on the `IMG_3120.jpg` fixture. The trap made explicit there:
  Photos' `location` is a **capture** role and must never become the customer's site as a subject
  fact.
- **`finance`** — recorded on the invoice fixture as `also_schema`, not as a collision, because the
  invoice is not this row's evidence in the first place.

## `also_holds_with` — deliberately empty, with the intent recorded for R1c

Empty by contract. CONNECTION §5 makes `also_holds_with` **schema ↔ schema only**, and this row is
a template. The coactivation intents that would otherwise go there, recorded here for R1c to place
on the `manufacturing` schema row if it agrees:

1. **manufacturing ↔ photos** — on-site photographs carry genuine capture facts and genuine
   service-context facts on disjoint evidence.
2. **manufacturing ↔ finance** — a visit pack that contains both a closure report and the invoice
   raised from it holds both on disjoint slots; the schema anchor already carries the analogous
   `business_operations` and `logistics` intents.

## proposed_fields — deliberately empty, and why

`fields: []` and `proposed_fields: []`. The schema anchor owns the fields, and every key this row
needs already exists or has already been proposed elsewhere:

- **customer** → the canonical `client` already exists, `destination_eligible: true`, aliases
  include *customer*. Minting a manufacturing-local synonym would be exactly the variant-minting
  the brief forbids. The problem is not a missing key, it is that `manufacturing` does not
  reference `client` — a schema question, raised as **NJ-FSR-1**.
- **the unit** → reuse the schema's own proposed `asset`, in a different holder role. Raised as
  **NJ-FSR-2**; not re-minted as `installed_asset`.
- **the visit** → reuse `manufacturing.maintenance-work-order`'s proposed `work_order`. Reusing an
  existing proposal beats a `service_call` variant.
- **coverage / chargeability** → deliberately **not** proposed. It is a commercial *conclusion*,
  recorded in a slot the servicing party filled in its own interest, and the product should read it
  as detection structure and never assert it. Raised as **NJ-FSR-4**.

## NEEDS-JOSEPH

- **NJ-FSR-1 — the customer level has no home.** This row's recommended first dimension is
  canonical `client`, which `manufacturing` does not carry, and the schema's `site` is the holder's
  own plant. *Alternatives:* (a) R1c widens `client` onto `manufacturing` for servicing corpora;
  (b) R1c rules that a servicing corpus files by unit alone and drops the customer level — in which
  case leg 2 weakens materially and this row should be re-examined for refusal; (c) a new
  manufacturing-local key is minted, which this memo recommends against as variant-minting.
- **NJ-FSR-2 — `asset` carries two holder roles.** The schema's `asset` assumes equipment the
  holder maintains or calibrates; here it is a third party's property, and its serial is unique
  only within a manufacturer's series rather than within the holder's corpus. *Alternatives:* a
  canonical holder-role split on `asset`; or a per-row note with no canonical consequence.
- **NJ-FSR-3 — the boiler fixture, reciprocal with `construction_property.trade-job`.** That row's
  own `open_question` names this row as one of the conditions under which it falls. This memo
  declines the concession and cedes single-appliance work at a dwelling instead, but both rows
  cannot be right about the same bytes. *Alternatives:* (a) subject-portability governs, as
  proposed here — unit survives the address → this row, otherwise → trade-job; (b) the presence of
  a manufacturer service contract governs regardless of premises; (c) the structure belongs wholly
  to one row and the other refuses.
- **NJ-FSR-4 — may a coverage or chargeability position be extracted at all?** It is a commercial
  conclusion written by an interested party. This row currently treats it as detection structure
  only. *Alternatives:* leave it unextractable; or permit it at a `possible` ceiling from a labelled
  slot with an explicit "as asserted by the servicing party" marker.

## Verification performed

`python3 -m json.tool` parses. All six `00` spans grep-verified verbatim before use (six OK). All
13 `file_examples.source_type` values checked programmatically against
`src.evidence_shape.vocabulary.SOURCE_TYPES`; `file_kinds.source_types` is a subset. All six edge
ids confirmed on `roster.json`. All `falls_through_to` names are among 00's nine residual homes.
Every `collides_with` and `role_split` entry is an object carrying a discriminator with the same
fixture named on both sides; `also_holds_with` is empty per CONNECTION §5. No thresholds,
statistics, file counts or handling classes; sensitivity is `potentially_sensitive` only. Exactly
the two assigned files were written — no neighbour node, roster, canonical-field, `check.py`,
`src/` or SPEC file was touched.
