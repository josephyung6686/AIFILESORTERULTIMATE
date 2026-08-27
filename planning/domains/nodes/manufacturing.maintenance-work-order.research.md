# Research memo — `manufacturing.maintenance-work-order`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/manufacturing.maintenance-work-order.json`
Roster row: template on the fieldless `manufacturing` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accept**, for one reason worth stating before anything else: this is the only manufacturing
situation whose evidence is an **obligation** rather than a **result**. Every other branch of the
anchor — batch record, inspection table, calibration certificate, nonconformance, release — is
recognised from a finished measurement or a disposition. A maintenance work order must be recognised
in three successive shapes, of which only the last has a result: the **request** that raises an
obligation, the **instruction** that plans it, and the **completion record** that discharges it and
becomes the asset's history. The schema default can see only the third.

## Sources read

Deliberately narrow, per the dispatch's token discipline.

- `dispatch/RESEARCH-BRIEF.md` in full; the stamped assignment from `make_prompt.py`.
- `nodes/manufacturing.json` in full — the row I must differ from, so the one file that had to be
  read whole.
- `nodes/legal.practice-matter-file.research.md` — one landed launch row, depth calibration only.
  Nothing from it is cited as evidence about this world.
- `00-database-agent-product-design.md` — **not read in full**; reached by two targeted greps (one
  for `maintenance|equipment|repair`, one to verify the three spans quoted).
- One grep for landed rows arguing a boundary against me, returning five; I read only the lines
  naming me in `engineering.aerospace-airworthiness`, `logistics.fleet-vehicle`,
  `construction_property.snagging-defects`, `engineering.commissioning-handover`,
  `manufacturing.inspection-record`.
- `roster.json` by grep only, to confirm my id, siblings and every edge target.

**A finding that governs provenance.** A case-insensitive grep of `00` for `maintenance`,
`equipment` and `repair` returns exactly one line, about evaluation decomposition. **`00` contains
no maintenance world.** Every claim here about what this corpus holds is therefore `inference` or
`proposal`; the only `design` material available is `00`'s general machinery — the parent-context
rule, the time-first rule, the session rule. I use exactly those three and dress no inference in a
citation to make it look stronger. No `design_cite` is attached to any edge, because none has a
verbatim span behind it and a decorative cite is worse than none.

## THE CHARGE — the strongest case that this row should not exist

**1. It is a `work_type` value. (Strongest.)** The anchor's own `work_types[]` contains, verbatim,
`"maintenance request, work order, service report or breakdown log"`. My whole row is one string in
someone else's enum, and the anchor proposes `record_type` with the example `"batch production
record"` — so on the anchor's account "maintenance work order" is a **value of a field**, exactly
what the dispatch forbids: *"Work types are values… Do not ask R1a for a child node per work type."*
If I survive because my documents are called work orders, so do `calibration-record`, `spare-parts`
and `asset-register`, and the manufacturing subtree is a document-type taxonomy in node clothing.
My sibling `manufacturing.inspection-record` put this same charge on itself and named me inside it.

**2. It duplicates its own schema's default template. (Nearly as strong.)** The anchor's seventh
deterministic signal reads, verbatim: `"a maintenance work order with an asset identifier, failure
or task code, work performed, parts or labour used, downtime and returned-to-service approval; an
invoice for the same work does not satisfy this structure"`. That is my detection signal, written by
someone else, already firing. Worse, the anchor's `template.why` already recommends my dimensions —
`"site then asset then record type for maintenance and calibration"` — and its `grouping_reasons`
already contains `"one asset across purchase/commissioning evidence, calibration, preventive
maintenance, breakdown and retirement records"`. Signals, dimensions and grouping: on the face of
the anchor, all three are already written and all three are mine.

**3. It is a document type** — "work order" is a form name, a printed template with boxes.
**4. It is a lifecycle stage** — the in-service phase of an asset already held by `asset-register`,
as commissioning is the handover phase and disposal the last.
**5. Defined by an absence?** Tested and rejected: it is not "a manufacturing record without a lot".
It has positive structure (dispatch, isolation, consumption, closure), and the aerospace and fleet
fixtures prove it exists where no manufacturing lot could exist.
**6. Never-alone evidence?** No. Not an organisation name; and the anchor already forbids activating
on the word *maintenance*, on an asset tag alone, or on a work-order-shaped number outside a role
slot. My row inherits all of that and adds to it.

## The node test, three legs

### Leg 1 — detection signals differ

The answer to charge 2 is that the anchor's signal describes **a completed job only**: it requires
*work performed, parts or labour used, downtime and returned-to-service approval*. Those four slots
are precisely the ones a maintenance request does not have.

`WO-14872 Maintenance Request - Line 3 conveyor noise.pdf` is a real and very common artefact:
reported-by, date reported, priority, target asset, free-text symptom, and Work Performed / Labour /
Parts blocks **printed and empty**. Under the default it cannot activate manufacturing at all —
every required slot is blank — so it falls to Independent Records: an open obligation against a
machine, filed loose, unrelated to the machine or to the job that eventually discharges it. That is
the whole open-backlog half of a maintenance corpus.

So my first deterministic signal is written the other way round: *a request structure whose
work-performed block is EMPTY or absent*. **The emptiness is the evidence** — a signal shape that
appears nowhere in the anchor and could not, because every other branch there is result-shaped.

Two further signals are not derivable from the default either:

- **A trigger that is a meter reading.** `PM-CNC07-Q3 preventive maintenance checklist.pdf` is bound
  to running hours or cycles — not a date, not a lot. Nothing else in manufacturing is scheduled by a
  counter on a machine; the anchor has no meter concept.
- **A row-semantics test.** `Work order history CNC-07 2019-2026.xlsx` is discriminated from an asset
  register not by its columns but by **what one row IS** — an event against a machine versus a
  machine. The anchor's register signal (`"an asset register row set… where multiple rows prove a
  controlled population"`) is a population test; mine is an event test. Opposite readings of the same
  table shape, and the default carries only one.

### Leg 2 — dimensions differ, and this row disagrees with its anchor

The anchor recommends `"site then asset then record type"`. **This row recommends asset first, the
job as leaf, site flattened for most holders.** A real disagreement, escalated as NJ-MFG-WO-2 rather
than smoothed, because both prose recommendations currently stand.

- **Site is a property of the asset, not an axis.** A machine lives at one plant; for a single-site
  holder the level never branches and should be flattened, while the asset level always branches.
  Site-first is natural for a product-and-lot schema, not for a corpus organised around machines.
- **`record_type` must not be the level under the asset.** Decisive. The request, permit, parts slip,
  photographs and completion report of **one job** are five record types. A record-type level shreds
  every job into five folders and destroys the only grouping the corpus is kept for. The leaf must be
  the **job** — which is what the proposed `work_order` key is for, and which the anchor has no key
  for.
- **Parent context governs**, quoting `00` verbatim: *"The recommendation should follow the practical
  rule that a parent dimension should provide the context required to understand the child."* A bare
  job number is unintelligible without its machine, exactly as *"A work type such as Homework 3 is
  meaningful only after the course is known."*

`time_first` is **false**, and this is the closest call in the row. Asset history is read
chronologically more than any other manufacturing corpus — the question is *what has happened to
this machine*. It is refused because `00` is explicit: *"For document and record domains, project,
function, or subject usually comes before time because putting year first scatters related work
across calendar folders."* A year-first tree scatters one machine's twenty-year life across twenty
folders and defeats the question the corpus exists to answer. Time is recommended as an unusually
strong **second** dimension instead, below asset and above job.

### Leg 3 — privacy differs

The anchor's posture is commercial confidentiality: recipes, tolerances, yields, layouts. My files
carry three exposures a batch record does not — kinds, not degrees.

- **Employment data.** A completion report attributes *actual hours to named technicians* — a
  timesheet in substance. A permit names who applied each isolation and who accepted the risk: a
  safety-liability record about identified individuals, materially unlike an operator's initial in a
  signoff box.
- **Personal and premises data.** `Boiler service report - 14 Sandy Lane - 2026-03-02.pdf` has the
  same shape as a plant work order and carries a **residential address**, an appliance serial and
  often access or key-holder details. No lot record describes where the holder sleeps.
- **Third-party data.** The field-service copy of the identical job names a **customer's** site,
  equipment and fault history.

Consequences in the row: named technicians and signatories stay search-and-privacy observations and
never become dimensions (authorship is never a destination); credential- or access-bearing members of
a closeout pack route to Protected Records rather than being previewed. No handling class — P7 owns
classes.

**Verdict: `refuse_node: false`.** Note what actually saves the row: not the phrase "work order",
but the request, the meter trigger, the row-semantics test, the job-as-leaf inversion and the
named-labour exposure — five things true of the situation and false of the value.

## Files

Fourteen fixtures carry full observation/fact splits in the JSON. The load-bearing ones:
`WO-14872` (the leg-1 request, empty completion blocks — the default cannot see it); `PM-CNC07-Q3`
(meter-triggered instruction); `WO-8814 completion report` (the only shape the default covers, and
the source of the named-labour exposure); `Work order history CNC-07 2019-2026.xlsx` (row-semantics
fixture, marked *must not conclude a `work_order` fact for the sheet as a whole* — the identifiers
are row values, not the file's anchor); `Permit to work PTW-2026-0338` (OCR, HSE seam);
`Parts issue slip WO-8814.csv` (spare-parts seam); `IMG_2201 sheared coupling WO-8814.jpg` (job
token in the **filename only**, `group_without_copying_facts: true` — the row's clearest statement
that activation is not grouping); `WO-2026-0413_N214FR_Wheel-Change.pdf` (the aerospace shared
fixture, named there as mine in both directions, carried here in the same terms); `WO-8814 closeout
pack.zip` (manifest inspected, not unpacked); and `Boiler service report - 14 Sandy Lane` (the
privacy edge case, kept under an ownership-evidence condition and escalated as NJ-MFG-WO-3).

## The collision fixture

**`Invoice INV-77213 - emergency callout Line 3 conveyor.pdf`.** It names the conveyor, the fault,
the engineer's hours and the date of attendance. By content it is indistinguishable from my
completion report, and it concerns *the very same job*.

**Discriminator: payable structure versus closure structure.** The invoice has supplier letterhead,
invoice number, tax lines, payment terms, remit-to — and **no requestor, no task code, no isolation,
no returned-to-service approval**; nobody signed to say the machine was safe to run. The work order
has all four and no payee. My anchor already forbids the shortcut in its own `never_alone`: *an
invoice, purchase order, packing list or delivery receipt alone; those are procurement/logistics
evidence until a lot-acceptance or equipment-control structure independently supports
manufacturing.* I restate that in maintenance-specific form and add the positive test, so the
discriminator is actionable rather than merely prohibitive. The invoice is
`group_without_copying_facts: true`: it may sit in WO-8814's group for a human, and must acquire no
`work_order` or `asset` fact by doing so.

**Second collision fixture**, taken from the anchor's own `needs_llm`: `Fanuc spindle service
procedures - maintenance manual.pdf`. Every maintenance word in the language appears in it; it
describes a machine **type**, has no owned instance, no date performed, no signature, no job id.
→ Reading Inbox. This is why my `never_alone` names the manual explicitly — it is the false positive
a term-frequency detector would rank highest.

## Files considered and rejected

| Tempting file | Why it is not this row's evidence |
|---|---|
| `Invoice INV-77213 …pdf` | Payable structure, no closure structure. → business_operations / Receipts and Confirmations. |
| `Fanuc … maintenance manual.pdf` | Machine type, not owned instance; no performed work. → Reading Inbox. |
| `Asset card CNC-07.pdf` | States what the machine permanently IS; a `Next PM Due` field is a property of the asset, not a job. → `asset-register`. |
| `Calibration certificate CNC-07 2026.pdf` | Purpose is a conformity statement (as-found/as-left/traceability). → `calibration-record`. The work order that dispatched it stays mine. |
| `8D report - repeated spindle failures.pdf` | Argues a cause from an assembled population. → `failure-analysis`. A failure code on one job is a dispatch category, not a finding. |
| MOT / statutory vehicle inspection certificate | A signed declaration of fitness for the road. → `logistics.fleet-vehicle`. |
| `PO 45001982 - spare bearing.pdf` | A purchase. Never mine, per the anchor's own never-alone rule. |
| `Line 2 shift log 2026-08-17.xlsx` | Production intervals on a line, not jobs on an asset. → `production-record`. Downtime appears on both and discriminates neither. |
| `Snag item - Plot 42 kitchen door binding.pdf` | A workmanship obligation that expires. → `snagging-defects`. |
| `Punch List - Harbour Pump Station - rev 7.xlsx` | Conditions of acceptance before takeover. → `commissioning-handover`, as a **role_split**, not a collision. |
| A CMMS database or live work-order module | A source system, not a file node. A bounded export with a readable manifest is represented; live ingestion is a later connector and security decision. |
| Technician competence cards and training records | Named-person records common in maintenance folders. Not jobs. They must create no asset fact, and their names must never become dimensions. |

## Reciprocal boundaries

Ten `collides_with` entries, each an object with a same-fixture-both-sides signal per the edge-shape
defect repaired this week — no bare id strings.

| Neighbour | Shared fixture | Discriminator |
|---|---|---|
| `manufacturing.asset-register` | `Work order history CNC-07 …xlsx` / `Asset card CNC-07.pdf` | **What a row IS** — an asset, or an event against one. |
| `manufacturing.calibration-record` | `CNC-07 probe calibration 2026-04.pdf` | As-found/as-left + traceability = theirs; dispatch + closure = mine. |
| `manufacturing.spare-parts` | `Parts issue slip WO-8814.csv` | Closes a stock balance = theirs; charges a job = mine. |
| `manufacturing.field-service-report` | `Service report SR-4471 - press at Acme Plant 2.pdf` | **Whose signature accepts the work.** Also authored as a role_split. |
| `manufacturing.failure-analysis` | `CNC-07 spindle - repeated bearing failures.pdf` | Argues a cause from a population = theirs; one job with a code = mine. |
| `manufacturing.hse-incident` | `Permit to work PTW-2026-0338 …pdf` | Job cross-reference + validity window = mine; site permit register or incident file = theirs. |
| `logistics.fleet-vehicle` | inspection sheet vs PM work order | **The declaration.** A work order proves work was done; an inspection asserts a condition. |
| `engineering.aerospace-airworthiness` | `WO-2026-0413_N214FR_Wheel-Change.pdf` | Execution slots = mine; approval-and-conformity slot = theirs. |
| `construction_property.snagging-defects` | a fault on a building service | **Whether an obligation ends.** Defects period = theirs; upkeep regime = mine. |
| `business_operations` | `Invoice INV-77213 …pdf` | Payable structure vs closure structure. |

The last four **restate boundaries those rows already authored against me**, on their own fixtures.
I checked each before writing and changed none; where their wording was already precise I reused it
deliberately, so the pair reads identically from both sides instead of drifting. Two `role_split`
entries reciprocate `commissioning-handover`'s (defect rectification either side of the taking-over
date) and author the operator/vendor split with `field-service-report` on the same bytes.

**Deliberate non-edges.** `production-record` (a log's rows are production intervals, mine are jobs —
adjacent, not confusable). `work-instruction` (an SOP is a controlled procedure; a PM checklist is a
task list bound to one asset and one interval). `tooling-fixture`, `safety-case`, `energy-audit` (no
fixture of mine could be claimed by them; edges would be decoration). `photos` (a co-holding on the
defect photograph, not a mutex — recorded as `also_schema`). `engineering.prototype-build` already
rejected me from its own side; that stands, no reciprocal needed.

## `also_holds_with` is empty, deliberately

CONNECTION §5 restricts it to **schema ↔ schema** pairs; this is a template row, so the empty array
is correct rather than an omission. The genuine co-holdings observed are recorded on the fixtures as
`also_schema` and surfaced for R1c to lift onto the `manufacturing` schema row if it agrees:
manufacturing ↔ photos (defect photograph in a closeout pack); manufacturing ↔ business_operations
(a vendor document that is simultaneously a payable and a service report, the two structures
disjoint in the same bytes); manufacturing ↔ logistics (a job on a vehicle that is also a
custody-moving unit). Recorded as NJ-MFG-WO-5.

## `proposed_fields`

**One key: `work_order`** (full argument in the JSON). It is the grouping anchor, and without it the
row has a situation it cannot serialise. `asset` is the machine and cannot separate one machine's
hundreds of jobs. `quality_event` is a controlled deviation and would make a lubrication route read
as a quality escape. `project` is bounded discretionary work. `record_type` names what kind of
document a file is — the wrong axis exactly, since request, permit, parts slip and completion report
are different record types belonging to the *same job*.

Two disciplines observed. **Reuse before minting:** I recommend R1c fold this into the broader
canonical `case`/`event` key the anchor already asked for in NJ-MFG-2 rather than ratify a
manufacturing-only synonym, and state the risk of folding so the decision is informed.
**Leaf-only eligibility:** a filesystem whose first branch is a job number is unreadable, so the key
is proposed eligible beneath the asset and explicitly not above it. Nothing else is minted; `asset`
and `site` are reused from the anchor unchanged. PM-versus-corrective is a **value** in
`work_types[]`, not a key and not a node.

## NEEDS-JOSEPH

- **NJ-MFG-WO-1 — the job key.** `work_order` as proposed, or folded into a broader canonical
  `case`/`event`? Folding is recommended for economy; the cost is that a routine job and a
  nonconformance share one field and every planned job risks reading as a quality escape. The
  alternative is two keys plus a rule that a job never populates the deviation key.
- **NJ-MFG-WO-2 — the dimension disagreement, and the one that must be resolved.** This row
  contradicts its own anchor's `template.why`: anchor says site → asset → record_type; this row says
  asset → (time) → job, site flattened, record_type refused as a level. Both currently stand as
  prose. R1c must ratify one.
- **NJ-MFG-WO-3 — domestic and personal service reports.** A boiler, car or appliance service is
  structurally identical to a plant work order (a job on an owned asset) and belongs to a different
  privacy world (residential address, occupier, access details). Kept here under an
  ownership-evidence condition. Alternatives: (a) as here; (b) route to a household/property
  situation if the roster has one I did not find; (c) always route to Independent Records — safe,
  and loses a real and common corpus.
- **NJ-MFG-WO-4 — permits to work.** Argued mine when job-scoped and cross-referenced, theirs when a
  site register or incident file. Authored reciprocally from this side only;
  `manufacturing.hse-incident` has not landed and must confirm, or the pair drifts.
- **NJ-MFG-WO-5 — schema-level co-holdings.** The three pairs above cannot be authored by a template
  row; R1c should decide whether to lift them onto `manufacturing`.

## Self-verification

`python3 -m json.tool` parses. All eleven edge targets grepped present in `roster.json`
(`manufacturing.asset-register`, `.calibration-record`, `.spare-parts`, `.field-service-report`,
`.failure-analysis`, `.hse-incident`, `logistics.fleet-vehicle`,
`engineering.aerospace-airworthiness`, `engineering.commissioning-handover`,
`construction_property.snagging-defects`, `business_operations`). Every `falls_through_to` name is
one of `00`'s nine residual homes. Every `file_examples.source_type` is in `SOURCE_TYPES`
(`presentation` and `audio_video` deliberately absent from `file_kinds` — no fixture needs them).
All three `00` quotations grep-verified verbatim before use (lines 45 and 95); anchor text is quoted
as the anchor's, never attributed to `00`. No thresholds, no confidence scores, no handling classes;
`sensitivity` is `potentially_sensitive` only. `fields: []`, `template.dimension_order: []` and
`also_holds_with: []` are all intentional and argued above. Every `collides_with` entry is an object
with a same-fixture-both-sides signal. Files written: exactly the two assigned — no neighbour node,
roster, canonical field, `check.py`, `src/` or SPEC was touched.
