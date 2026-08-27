# Research memo — `retail_hospitality.event-production`

Depth: J-DEPTH
Date: 2026-08-27
Output: `planning/domains/nodes/retail_hospitality.event-production.json`
Roster row: template on the fieldless `retail_hospitality` schema, `parent_id: null`, `launch: placeholder`
Pass: R1b, one row, one agent

## Result

**Accept**, and narrow. The row survives, but not as "the event one" — it survives as **the occasion with a clock**. Its four structures are a clock-and-responsible-party running order bracketed by load-in and strike, a many-suppliers-one-date call schedule, a temporary-occupation safety plan, and a two-sided reconciliation pairing budget-against-actual with expected-against-attended. None of the four appears in the schema's ten default detection structures, and none appears in the four structures `business_operations.project-delivery` names as its own.

It is narrowed in one respect the schema anchor asked for: it is the **host or venue's** side of delivery only. An agency producing an event for a paying client is an instructed commission and is not this row. That is this pass's answer to NJ-RH-2, which the schema anchor left open with exactly this alternative ("narrow the template to venue-side delivery, or refuse it").

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `also_holds_with: []`, `time_first: false`.

## The charge — the strongest case that this row should not exist

I ran the charge before writing anything. Seven forms of it, four of them serious.

### 1. It is a work_type value of its own schema — the serious one

The schema anchor's `work_types` list contains, verbatim: `"event delivery record - brief, plan, supplier schedule, run sheet, on-the-day log, post-event reconciliation"`. My `one_line_hint` is a near-restatement of that string. The schema's own `never_alone` then says: *"A DOCUMENT-TYPE WORD, standing alone - invoice, rota, log, price list, order, review. These are values of a function dimension, and a row resting on one is the schema's default template wearing a name."* On its face this row is a function value that was promoted to a node — the 574's exact failure.

**Defeated, by an inversion test that I think is the general form of this charge.** A work_type row holds **one function across many occasions** — every rota, every price list, every log. This row holds **many functions across one occasion**: a brief, a drawing, a supplier grid, a timeline, a photographed whiteboard, a prose debrief and a two-column reconciliation, sharing no content, no format and no source type. That is the design's own purpose-coherence pattern rather than a topic or function grouping: *"The documents are content-incoherent but purpose-coherent."* If this row were a work_type, its members would be interchangeable across occasions; instead a run sheet from a different wedding is useless in this pack, and a floor plan from the same one is essential. The test cuts the other way too, which is what makes it usable: `retail_hospitality.guest-feedback` and `retail_hospitality.stocktake` pass it as well (both are occasion- or cycle-anchored), while a hypothetical `retail_hospitality.rota` would fail it.

### 2. It is a lifecycle stage

"Brief → plan → delivery → reconciliation" is a lifecycle, and lifecycle stages are not nodes.

**Defeated.** The lifecycle is *inside* the row, not what the row is — the row is the whole bracket, and the bracket is precisely what it recommends as its second dimension. The falsification is on the roster: if this were a stage row there would be siblings for the other stages, and there is no `event-planning` and no `event-reconciliation` among the schema's fourteen children. There is one row for the whole arc.

### 3. It is a duplicate of `business_operations.project-delivery` — the second serious one

Project-delivery's own `one_line` describes "ONE BOUNDED PIECE OF WORK that has a start, an intended end and a named owner". An event is that. It even claims the anchor is "the PROJECT as a bounded effort with a closure", and an event closes hard.

**Defeated on structure, and the argument generalises.** Project-delivery names four structures as the things that activate it — "a scope-and-out-of-scope pair, a dependency-bearing schedule, a stage-gate-and-RAG reporting cadence, and an acceptance-paired-with-handover closure". I could not construct a realistic event pack containing any of the four, and could not construct a project pack containing any of mine. The deep reason is a property of the domain rather than of the paperwork: **an event cannot slip.** A project's date is an output of its schedule; an event's date is an input that everything else compresses against. That is why the event artefact is a *clock over one day with a responsible party* rather than a *dependency network over months with percent-complete*, and why the closing artefact is a **reconciliation** rather than an **acceptance** — nobody signs an event off. Fixture in the JSON: `Annual Conference 2026 - master plan.xlsx`, a workbook with a Gantt tab and a run-sheet tab, split tab-by-tab.

### 4. It is a duplicate of `retail_hospitality.catering-contract` — the third serious one, and only partly defeated

The schema anchor's NJ-RH-3 already doubts catering-contract ("may be a duplicate of `bookings-reservations` plus `event-production` plus `business_operations.contract-administration`"). The mirror doubt is fair: if catering-contract owns the function sheet, what is left here?

**Defeated on scope, contested on one document.** Strip the food and the paying client from catering-contract and nothing remains. Strip them from this row and the run sheet, the supplier call schedule, the site plan, the on-the-day log, the safety plan and the attendance reconciliation all survive — a free community festival, a ticketed gig, a shop's launch night and an internal conference are all this row and none is catering. The genuinely contested object is the **function sheet / Banqueting Event Order**, which carries a commercial instrument and a delivery timeline in adjacent sections of one file. I did not smooth that; it is **NJ-EP-1** with three alternatives.

### 5. It is a duplicate of `creative.theatre-production` or `creative.exhibition`

Both mount something at a venue over dates, both have an install/strike bracket, both produce dated forms.

**Defeated on the join.** Theatre-production's own `one_line` says its documents are joined "by CUE NUMBERS that join documents no other creative row joins" — a cue-number-to-script-page join that an event pack never has. Exhibition's unit is "a REGISTER OF OTHER PEOPLE'S OBJECTS" — a checklist with artists, media, dimensions, editions and lenders, plus loan agreements and paired condition reports — which an event pack never has either. Both rows and this one share the bracket, which is exactly why I did not make the bracket the discriminator against them.

### 6. It is defined only by an absence

"The trading occasion that isn't a booking, a count, a session or a premises."

**Defeated.** Four positive structures, each with named real artefacts. I only reach for absences as *discriminators* against neighbours, never as the definition.

### 7. Medium, length, file format, organisation name

Not applicable and stated for completeness. The row is not `.xlsx`, not "one-day", not a venue's name. Its `never_alone` list forbids the venue name, the occasion word, the date, the bare time-of-day column and the document-type word from firing alone — and the occasion word is listed first, because that is the token a lazy detector would use.

## The node test, all three legs

The schema's default template, quoted from the anchor's `template.why`, is: *the TRADING UNIT — site, venue or channel — ONLY where the corpus genuinely spans more than one, then the TRADING OCCASION, then the OPERATIONAL RECORD FUNCTION*, with trading period inside the occasion and `time_first: false`.

**Leg 1 — detection signals. PASS, and this is the strongest leg.** The schema lists ten deterministic structures: tender-and-drawer reconciliation, count-against-book, capacity-against-dated-demand, premises-keyed permission, daily-signed-check diary, ingredient-and-yield, order-cycle, guest-voice, catalogue-and-price, plus folder/email/archive context. **Not one has a time-of-day axis.** This row's primary signal is a clock, and its second is the *inversion* of the schema's order-cycle: one supplier across many dates is `supplier-order`; many suppliers across one date is this row. The nearest default structure, capacity-against-dated-demand, is genuinely close — an event has a headcount and a date — but a run sheet has no capacity column at all, and the discriminator against `bookings-reservations` is stated reciprocally in the JSON. Inference, marked as such: I am arguing from the shape of named real artefacts, not from a design-doc sentence about events.

**Leg 2 — recommended dimensions. PASS, held as prose because PR-6 forbids a serialized order.** Two deviations, both argued in `template.why`. (a) **The top inverts.** The occasion comes first and the site is presumptively *off*, not merely conditional, because an event's place is frequently a venue the operator hires and does not run. Rooting an event pack at a site produces either a one-child branch naming the operator's own venue or a per-hired-venue branch that splits one occasion's paperwork — both are what the validator sentence rejects: *"The engine validates that the proposed template does not repeat a parent dimension, create meaningless one-child levels, exceed practical depth limits, use an author or organization merely as a collector, expose protected information, or produce empty branches when tested against the accepted group."* (b) **The second level is a phase, not a function list** — before / on-the-day / after — because a flat function list scatters three run-sheet revisions, the pen-annotated scan and the debrief across unrelated siblings.

The time-first temptation is sharper here than anywhere on the schema, and I resisted it on the design's own terms: *"For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."* The exception is *"Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material."* The four hundred wedding JPEGs sitting beside my run sheet are what that exception is for, and their being time-first is the clearest demonstration that the run sheet is not.

**Leg 3 — privacy. PASS ON KIND, NOT ON VALUE, and I say so in the JSON.** The value is `potentially_sensitive`, identical to the schema. What differs is what the sensitive members *are*: the schema's argument is about bulk guest contact and purchase histories; this row's exposure is the **on-the-day log as an incident record** (injuries to named attendees, ejections naming attendee and steward), the **seating plan** (which records who was placed next to whom), the **delegate list** (a professional-affiliation dataset), and **crew mobile numbers**, which are personal rather than corporate contact details. This leg alone would not carry the row. It is recorded as the weakest of the three deliberately, because a row that claims three strong legs when it has two is padding.

## Files considered and rejected

Named because each is a tempting false positive I would otherwise have absorbed.

- `Ashcroft 06.06.26 - confirmation and deposit.pdf` → `bookings-reservations`. The reservation of the date is not the production of the day. Sequential on one occasion, which is why they will co-occur in one user folder and why the boundary is written in both directions.
- `Bar stock - 6 Jun function.xlsx` → `stocktake`. It is count-against-book. Being *for* one event does not make it *of* the event's delivery.
- `Z read - 6 Jun festival bar.pdf` → `pos-reporting`. Tender split against declared cash. A festival bar produces this and my reconciliation on the same night; both are correct on their own bytes.
- `Temporary Event Notice - 06.06.26.pdf` → `premises-licensing` on the grant test, **under protest**, as NJ-EP-2.
- `Wedding 6 Jun/` (400 JPEGs) → `photos` / `creative.shoot-day-media`. This row does not share the capture-time-first exception and must not annex the media because it holds the paperwork.
- `Annual Conference 2026 - workstream plan v6.xlsx` → `business_operations.project-delivery`. All four of its structures present; none of mine.
- `Q3 all-hands - agenda and timings.docx` → `business_operations.meeting-record`. Three decisive absences together: no supplier arrivals, no load-in/strike bracket, no attendance-against-expected reconciliation.
- `AV hire invoice 4471.pdf`, isolated → Receipts and Confirmations. One transaction is a residual's business.
- `Delegate list - Harbour Summit.csv`, alone → Protected Records. A register of people with no delivery apparatus around it is not an operating record, and treating it as one is how this row would become a consumer database with a folder name.
- `Event Management Plan - TEMPLATE (blank).docx` → not a record. The schema's real-versus-template determination applies with full force: a blank run sheet and a completed one are the same grid with the actions removed. *"Topic answers what a file is about, while purpose answers what the file was for."*
- `Wedding brochure - Ashcroft Hall 2026.pdf` → sales collateral, `business_operations` or `creative`. A venue's own marketing pack describes what it *could* deliver; this row holds what it *did*.

## The collision fixtures

**Primary: `Order of service - Ashcroft wedding.pdf`.** Times down the left, items across, one date — visually almost identical to a run sheet. It is not one. Two discriminators, both structural: **no responsible-party column**, and **no bracket** — it begins at the first guest moment and ends at the last, where a run sheet begins with a florist at 07:00 and ends with a marquee de-rig on Sunday morning. Typeset in a display face with print bleed marks and a printer's job number; it is `creative.print-production` output and, standing alone, Independent Records. This fixture is why the JSON's `never_alone` forbids a bare time-of-day column: an agenda, a timetable, a broadcast log and a departure board all have one.

**Secondary: `Running order - Spring Gala 2026 (client approval v4).docx`.** A *genuine* run sheet — clock, responsible parties, load-in and strike — carrying a cover sheet naming an agency and a client, a fee summary, a change-order reference, a tracked client-side approval block, and deliverables against milestones. The holder appears in the agency block. This row must not activate. It is the NJ-RH-2 case made concrete, and it is why the role split is authored.

## Reciprocal boundaries

Eleven, each written as a same-fixture-both-sides object per the edge shape. Summarised by which fixture each turns on:

| Neighbour | Same fixture both sides | Discriminator |
|---|---|---|
| `retail_hospitality.catering-contract` | `Function sheet - Ashcroft wedding 06.06.26.docx` | commercial instrument vs delivery timeline (contested — NJ-EP-1) |
| `retail_hospitality.bookings-reservations` | `Ashcroft 06.06.26 - confirmation and deposit.pdf` | capacity-against-demand vs clock-against-responsibility |
| `business_operations.project-delivery` | `Annual Conference 2026 - master plan.xlsx` | Gantt/RAG/acceptance vs clock/suppliers/reconciliation |
| `creative.theatre-production` | `Running order - 6 Jun.pdf` | cue numbers to script pages vs supplier arrivals and carriages |
| `creative.exhibition` | `Install schedule - Ashcroft Gallery, private view 6 Jun.xlsx` | register of others' objects vs dated occasion with attendees |
| `retail_hospitality.premises-licensing` | `Temporary Event Notice - 06.06.26.pdf` | grants something vs plans something |
| `retail_hospitality.pos-reporting` | `6 Jun - festival bar takings.xlsx` | counted-vs-believed vs planned-vs-spent and promised-vs-present |
| `logistics` | `POD - 20 trestle tables, 6 Jun, gate 2.pdf` | keyed to a consignment vs keyed to a position in the running order |
| `hr` | `6 Jun - crew call.xlsx` | occasion's clock vs employee's terms |
| `business_operations.meeting-record` | `Q3 all-hands - agenda and timings.docx` | convening vs producing |
| `photos` | `IMG_4471.jpg` (whiteboard) | the act of capture vs what the sheet says |

Three are **authored one-way** and R1c owes the reciprocal on the landed neighbour: `business_operations.project-delivery`, `logistics`, and `photos`. The `hr` edge is the event-shaped instance of the schema anchor's own NJ-RH-1 and must be answered the same way that is — a bare crew call is as undecidable as a bare rota.

## Fields and dimensions

`fields: []` by contract — the schema declares none, and a template may only reuse its schema's fields.

`proposed_fields: []` **deliberately**, and the rejections matter more than the empty list:

- `event` — a mint of exactly the kind the schema's `trading_occasion` was created to prevent. The schema's own argument covers this case: an event is "a bounded occurrence identified by a reference or a date, against which a counted or booked quantity is recorded". Reuse, don't mint.
- `venue` — would be a synonym of the schema's `site` and a near-synonym of `construction_property`'s `property`. The real strain (a *hired* venue is not the operator's trading unit) is recorded as a `role_split` entry and as **NJ-EP-3** rather than fixed by minting.
- `event_date` — the schema's `record_period` covers a dated occasion, and the schema's `trading_occasion` already carries the date as part of its identity. A third date key would guarantee the year-first tree the design forbids.
- `phase` / `event_phase` (pre / on-the-day / post) — this is a **function value**, and the schema's `never_alone` list rules that a row or level resting on a document-type word is "the schema's default template wearing a name". The phase is recommended as a *dimension shape* in prose; it is not a fact.
- `supplier` — never-alone as an organisation name, and as a level it would be an organisation-as-collector, which the validator sentence rejects outright.

The schema's `product` and `record_period` are not contested by this row. `record_period`'s sub-daily question (schema NJ-RH-5) matters here: if `record_period` cannot go sub-daily, this row's clock has no key — which is survivable, because the clock is *detection evidence*, never a fact this row writes.

## Open questions — NEEDS-JOSEPH

**NJ-EP-1 — the function sheet / BEO.** One file, two owners, adjacent sections. (a) `catering-contract` owns the file and this row reads its timeline as a group member without claiming the file — my preference, because it keeps whole-file ownership single-valued. (b) This row owns it whenever the timeline section exists — which hollows out catering-contract and lends weight to the schema's own NJ-RH-3 doubt that catering-contract survives at all. (c) Both activate on disjoint sections, which may not be supported at sub-file granularity. **Both rows must say the same thing**, and only one of them has been written.

**NJ-EP-2 — the Temporary Event Notice.** The one artefact where `premises-licensing`'s persistence test and this row's occasion test give opposite answers: it is permission-shaped and dead the morning after. Ruled to `premises-licensing` on the grant test. Alternative: occasion-scoped permissions come here and only persistent premises permissions stay there — which would be tidier conceptually and would split a coherent licensing file in practice.

**NJ-EP-3 — does `site` stretch to a hired venue?** If not, this row has no key for an event's place and must treat the venue as evidence only. If so, `site`, `property` (construction_property) and the hired venue must be adjudicated as a **triple**, not the pair the schema anchor asked for.

**NJ-EP-4 — recurring-edition series.** Harbour Food Festival 2025 and 2026: two occasions, one identity, every artefact titled with a year. I insist each edition is its own group and the series is a browse relationship — but this is the exact shape a user or a later dimension engine will re-propose as a year-first tree, and the design's rule against year-first is stated for record domains generally rather than for a series specifically. Decide whether a series identity is representable without minting the key I declined to mint.

**Carried forward from the schema anchor, unresolved and reciprocal here:** NJ-RH-1 (the bare rota — my `hr` edge is its event-shaped twin), NJ-RH-3 (catering-contract's survival — NJ-EP-1 is the hinge), NJ-RH-5 (sub-daily `record_period`), NJ-RH-6 (whether "events" is a third leg of the schema name — this pass agrees with the anchor that it is not; there is no schema-level event structure, only this template's).

## Recommendations for R1c — cross-row, not actioned here

1. `business_operations.project-delivery` should gain the reciprocal edge to this row, naming `Annual Conference 2026 - master plan.xlsx` and the four-structures-each-way test verbatim.
2. `logistics` and `photos` owe reciprocals on the fixtures named above.
3. `retail_hospitality.catering-contract` must be written against NJ-EP-1's chosen option, not independently.
4. The schema anchor's `work_types` string "event delivery record …" should be read as this row's *coverage statement*, not as evidence that the row is a work_type; the inversion test in the charge section is the general form and may be worth promoting into the contract.

## Self-verification

- `python3 -m json.tool` on the node: **passes**.
- Every quotation grep-verified verbatim against `planning/00-database-agent-product-design.md` (lines 42, 45, 95, 97, 120, 177 and the archive, ICS, university-name, consulting-facets and template-order sentences): **all return exactly one match**.
- Key set matches the landed template sibling `creative.exhibition.json` exactly, including `file_examples` sub-keys and `collides_with` object shape.
- Every `collides_with` entry is an object with `domain`, `signal` (SAME FIXTURE BOTH SIDES form) and `provenance`. No bare id strings.
- `also_holds_with: []` — this is a template row, and `also_holds_with` is schema↔schema only (CONNECTION §5). Co-activation intents are recorded above for R1c instead.
- Every neighbour id checked against `planning/domains/roster.json`.
- `falls_through_to` names five of `00`'s nine residual homes, including both residuals the assignment required (Receipts and Confirmations, Independent Records).
- No thresholds, no statistics, no file counts, no handling classes, no `public_low`, no regexes, no gazetteer contents.
- Files written: exactly the two assigned. No roster, contract, canonical-field, `src/`, or neighbour edits.
