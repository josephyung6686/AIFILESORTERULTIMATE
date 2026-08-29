# Research memo — `manufacturing.production-record`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/manufacturing.production-record.json`
Roster row: template on the fieldless `manufacturing` schema, `parent_id: null`, `launch: placeholder`
Status: **SALVAGE.** A killed agent left the JSON with no memo. This memo verifies, repairs and owns it.

## Result

**Accept the node**, but only after the charge against it was taken at full strength, because it is
the single weakest-looking row in the manufacturing set. It survives on one structural fact —
**this row's anchor is the executed instance, not the artefact and not the product** — and on three
signals the schema anchor provably cannot resolve. It writes `fields: []`, `dimension_order: []`,
one `proposed_field`, and four NEEDS-JOSEPH items.

## What the salvage draft got right, and what I repaired

The draft was unusually strong: twelve fixtures, six reciprocal collisions, an argued three-leg node
test. I verified it line by line rather than trusting it.

**Verified clean.** Every neighbour id resolves against `planning/domains/roster.json` —
`manufacturing.production-planning`, `manufacturing.work-instruction`,
`manufacturing.inspection-record`, `manufacturing.nonconformance-capa`, `engineering.prototype-build`,
`creative.print-production`, `construction_property.site-diary`, `logistics`, `engineering`. **No
dangling id**, unlike the sibling salvage row flagged this session. All three quotations attributed
to landed neighbours grep back verbatim from their JSON. The `00` quotation in `template.why` greps
back verbatim from line 95 of `00`.

**Three defects repaired.**

1. **A fabricated design citation.** The draft's first `never_alone` entry asserted "00 forbids a
   bare 4-digit number as proof." That phrase does not exist in `00` — I grepped for `four-digit`,
   `4-digit`, `a bare number` and got nothing. The claim is *true in substance* but was sourced to
   the wrong authority. Repaired to cite the actual authority, the schema anchor's own never-alone
   line: `a serial number, asset tag, work-order number, deviation number or other identifier-shaped
   token outside a labelled role slot`, and marked INFERENCE. A false attribution to `00` is worse
   than no citation, because a downstream reader cannot tell it from a real one.
2. **Wrong edge shape on `also_holds_with`.** The draft placed two SCHEMAS (`logistics`,
   `engineering`) in a TEMPLATE row's `also_holds_with`. CONNECTION §5 records that edge as
   `schema ↔ schema only`. Both were removed and their arguments preserved verbatim as NJ-PROD-0 for
   R1c to author on the `manufacturing` anchor — where, checked against the anchor JSON, both pairs
   **already exist**, so no coverage is lost. The remaining template↔template entry
   (`manufacturing.nonconformance-capa`) follows the landed `manufacturing.inspection-record`
   precedent and was rewritten into the SAME FIXTURE BOTH SIDES form.
3. **A one-sided boundary against a row that had already authored it.** The draft's
   `manufacturing.inspection-record` signal argued the seam from scratch without noticing that the
   landed neighbour had already written it — and had already assigned the shared fixtures. Replaced
   with the neighbour's verbatim assignment so the two rows now agree in the same words.

**One addition.** `proposed_context_terms` was absent; every landed manufacturing sibling carries
it. Seventeen execution-instance terms were added — deliberately terms the schema anchor does *not*
already list (`route card`, `job packet`, `operation number`, `work centre`, `quantity issued`,
`quantity good`, `quantity scrapped`, `kitting slip`, `device history record`, `as run`,
`signed off`, `reprocess`, …). The anchor's list is type-level vocabulary; this row's is
instance-level, which is the same distinction the node test rests on.

## THE CHARGE — the strongest case that this row should not exist

Stated at full strength before any defence. Six independent grounds, any one of which would
ordinarily kill a row.

1. **It is a document-type word.** *Traveller*, *route card*, *router*, *batch record* are names of a
   FORM. Naming a row after a form is a recorded failure mode of the 574.
2. **It is a work_type VALUE.** The `manufacturing` schema's `work_types[]` opens with
   `production order, traveller, router or batch production record`. This row is verbatim value #1
   of its own schema's enum. That is the original mistake in its purest form.
3. **It duplicates the schema's default template.** The anchor's *first* deterministic signal reads
   `a batch-production or traveller structure with a labelled product/part slot, batch or lot slot,
   planned-versus-actual quantities, sequential operation rows, operator/date signoffs, and release
   status`. That is this row's signal, already written on the schema.
4. **It is a lifecycle stage.** Sitting between `manufacturing.production-planning` and
   `manufacturing.inspection-record`, this is simply the *executed* stage of one shop order.
5. **Its evidence is never-alone.** A lot token, a job number and a part number are each explicitly
   forbidden as sole proof by the anchor.
6. **It is defined by absence.** "The production record that is not an inspection, calibration, NCR,
   maintenance or HSE record" is a residual carved out of eighteen siblings, not a filing world.

Grounds 1, 2, 5 and 6 are answered by what the row is *anchored on*, not what it is *called*: the
row's `one_line` and every deterministic signal anchor on the **executed order or batch**, never on
the form name and never on a bare token. Ground 4 is answered by the fact that planning and
execution do not merely differ in *when* — they differ in *cardinality*: a planning artefact holds
many orders, an execution artefact holds one. Ground 3 is the serious one, and is only partly
answered; see below.

## Node test, argued in three legs

### The schema's default template — and why there isn't one

**This is the load-bearing structural fact.** The `manufacturing` anchor's `template.dimension_order`
is `[]` and its `why` holds a **three-way branch in prose**, verbatim: `product then batch/lot then
record type for production and quality records; site then asset then record type for maintenance and
calibration; quality event then record type for NCR/CAPA files.`

A branch-shaped default is not a default template. It cannot be resolved to one ordered list, which
means **the anchor has no single default template for this row to duplicate.** Templates on this
schema exist precisely to resolve the branch. That is what makes nineteen templates legitimate here
where they would not be on a schema with one settled order.

### Leg 1 — signals differ (defeated the charge; ground 3 conceded in part)

I concede the general form of ground 3 openly. A fieldless anchor schema is written as the **union**
of its children's structures, so *every* manufacturing template will find some ancestor of its signal
on the schema row. If that alone refused a row, this schema could carry no templates at all. The
real test is whether this row's signal SET discriminates a situation the union cannot resolve.
Three signals do, and none is derivable from the anchor:

- **The partial-execution frontier.** A sequential operation table in which a contiguous PREFIX of
  rows carries operator/date/quantity values while the structurally identical remaining rows are
  empty. No other manufacturing record has a mid-state: an inspection report, a calibration
  certificate, a maintenance work order are each complete or absent. This shape is what makes a live
  traveller recognisable, and it is why the blank rows must not be read as missing data. The anchor
  names none of this.
- **The reconciliation triple.** Issued quantity, good quantity and scrap/rework quantity closing
  against each other under one signature, with the arithmetic present in the bytes. The anchor names
  `planned-versus-actual quantities` — a *pair*. The closing triple under a signoff is specific to a
  closed order and is what separates a batch record from a schedule that also shows planned and
  actual columns.
- **The instance-versus-type split.** The same operation text, the same parameter table and the same
  product appear in `manufacturing.work-instruction` under a document revision and effective date,
  and here under an order identifier with actual values written into those same cells. The
  discriminator is not the text but whether the cells are **populated and bound to an instance**.
  The union cannot make that call because it holds both structures.

### Leg 2 — dimensions differ (defeated on the branch)

This row resolves the anchor's production branch and then **differs from the branch it resolves by
dropping its terminal level.** `record_type` is near-constant inside this row — every member is the
production record — so a record-type level would generate a single-child folder under every order.
The researched recommendation, held as prose because no key involved is canonical:

> **product → executed order or batch**, with `site` optional above `product` only in a genuinely
> multi-site corpus, and a serial level below the order only where the corpus is serialised.

Not time-first. `00` (verified verbatim, line 95): *"For document and record domains, project,
function, or subject usually comes before time because putting year first scatters related work
across calendar folders."* A traveller carries a start date, a per-operation date, a release date and
a scan date; ordering on any of them would scatter one order across calendar folders — the exact harm
`00` names. `dimension_order` serialises as `[]` because the placeholder contract forbids serialising
non-canonical keys.

### Leg 3 — privacy differs (weakly; the row does not rest on it)

Stated plainly rather than inflated into a third leg. Sensitivity remains `potentially_sensitive`,
identical to the schema, and no handling class is assigned — that is P7's. The one genuine
difference is a **concentration, not a category**: the traveller is the only manufacturing record
carrying a named worker or clock number on nearly *every* row, and it carries the executed process
recipe — times, temperatures, feeds, tooling, actual yields and scrap rates — in the same bytes. It
is the intersection of worker-identifying data and the trade secret. Two consequences are written
into the JSON: an operator or shift name stays a search and privacy observation and is never promoted
to a destination dimension; and where an excerpt must leave the machine, the header plus one
operation row is preferred over the whole document.

**Verdict: accept.** Legs 1 and 2 each independently defeat the charge. Leg 3 supports but does not
carry it.

## Files considered and REJECTED — the tempting false positives

A row that only lists what it holds has not been researched. Five of the twelve fixtures in the JSON
exist to be rejected.

- **`Setup sheet OP30 AX-410 rev C.pdf` — the most convincing false positive in this domain.** Same
  product, same operation number, same parameter table as the traveller. Rejected because every
  parameter cell holds a *specified range* and none holds an actual value, and because there is no
  order, batch or serial identifier anywhere in the document. It carries a document number,
  revision C, an effective date and an approver block — type-level furniture. It is
  `manufacturing.work-instruction`.
- **`Production schedule week 34 Plant 2.xlsx`.** Order numbers, product, quantity, dates, work
  centre. Rejected on **cardinality and actuals**: many orders in one file, and no operator, no
  signoff, no actual quantity, no scrap column. A column of order numbers does not make an order
  fact for this row.
- **`Prototype build log DVT unit 003.docx`.** A sequential dated build narrative with a unit
  number and bench measurements — it looks exactly like a traveller of quantity one. Rejected
  because the design revision it builds to is **unreleased** and there is no production order,
  routing or release. It is `engineering.prototype-build`.
- **`Line 2 shift log 2026-08-17.xlsx`.** Output, scrap, downtime, changeover, shift. Rejected
  because the constant is the **line**, not an order: order numbers appear only as passing
  references, several per shift, and there is no routed operation sequence. A line-primary record is
  not an order-primary record. This row deliberately does not annex it — see NJ-PROD-2.
- **`PO 45001982 - AX410 castings.pdf`** (the anchor's fixture, re-tested here). A part name and a
  quantity are not execution evidence. Procurement until a lot-acceptance structure appears.

Also rejected as *sources rather than files*: an MES or ERP database is a source system, not a node;
a bounded export with a readable manifest is represented (`MES_ops_export_2026-08.json`), live
ingestion is a later connector decision. And deliberately not enumerated: industry sectors, process
types, discrete-versus-process taxonomies, or an operation vocabulary. Enumerating those would turn a
placeholder into the industry-depth catalogue J-IND forbids.

## The collision fixture

**`Setup sheet OP30 AX-410 rev C.pdf`**, whose parameter table is byte-for-byte the table embedded
inside `BPR_AX410_L240817-03.pdf`. Two files containing identical bytes, one mine and one not.

**What discriminates it:** not the text, not the product, not the operation number — all shared.
Only two things. (a) **Are the parameter cells populated with actual values?** (b) **Is the document
bound to an instance identifier?** The setup sheet answers no to both and carries revision-control
furniture instead. This is the cleanest statement of the instance-versus-type split, and it is why
this row's recognition can never rest on subject matter.

A second collision worth naming: the token `Router`. It is a route card, a network device and a
woodworking tool. `Router setup.pdf` is a plausible false positive from three unrelated worlds — which
is precisely why the row is not named after its form.

## Reciprocal boundaries — both directions, same fixture on both sides

Six are authored in `collides_with`, each in the object shape with an explicit SAME FIXTURE line.

| Neighbour | Shared fixture | Mine | Theirs |
|---|---|---|---|
| `manufacturing.production-planning` | `Production schedule week 34 Plant 2.xlsx` ↔ the traveller header block | one order, once actuals and signoffs are written on it | many orders, planned dates/quantities, capacity — no actuals |
| `manufacturing.work-instruction` | `Setup sheet OP30 AX-410 rev C.pdf` | the instance where the cells carry actual values under an order id | the type: document number, revision, effective date, approver, specified ranges only |
| `manufacturing.inspection-record` | `BPR_AX410_L240817-03.pdf` / `Final inspection AX410 lot L240817-03.csv` | the batch record incl. embedded check rows (a check *happened*) | the separately identified datasheet (what was *measured*) |
| `engineering.prototype-build` | `Prototype build log DVT unit 003.docx` | execution against a **released** definition, with an order and a release | sequential dated build against an **unreleased** revision, no order |
| `creative.print-production` | `Press run record Job 88214 - 4c cover.pdf` | route card with operation rows and a reconciliation triple, even if the product is printed | make-ready, plate, ink-sequence, proof-approval slots tied to a print job |
| `construction_property.site-diary` | `Site diary 2026-08-17 Riverside.pdf` ↔ `Line 2 shift log 2026-08-17.xlsx` | order/batch/line reference | site address, weather, trades |

Three of these six were **authored first by the landed neighbour**, and this row adopts their words
rather than inventing a competing formulation: `engineering.prototype-build` already assigns
`EXECUTION OF A RELEASED DEFINITION at batch or lot scale` to this row; `creative.print-production`
already states that `generic shop-floor production records belong to manufacturing`;
`construction_property.site-diary` already names the discriminator as `a batch, line, or work-order
reference supports the manufacturing row`. All three verified verbatim.

Two of the six — `production-planning` and `work-instruction` — are **forward declarations against
rows that have not landed yet** (no JSON exists for either). They are written so those agents can
adopt or contest them; if they contest, R1c adjudicates.

The reciprocal caution added from this side on the site-diary seam: a plant address and a headcount
column are not enough *here* either. Without an order, batch or line anchor, a serial dated
operational record does not activate this row.

## Fields

`fields: []` — the schema anchor owns the fields and declares none under PR-6.

One `proposed_field`: **`work_order`** (string, e.g. `WO-2026-4471`, `destination_eligible: true`,
`reliability_ceiling: validated`).

Why no existing key works: the anchor proposes `batch_lot` for the **material output** of a
transformation. That cannot carry this row's anchor in the discrete case — a make-to-order machine
shop routes a JOB that produces serial numbers and no lot at all, and a process plant can split one
lot across several orders or merge several orders into one lot. The **executed order** is the level
at which the traveller exists, is signed and is closed. The validation rule family is an
identifier pattern **plus manufacturing execution context** — an order-shaped token confirmed only by
co-occurring routed-operation or signoff structure, never by the token alone. No regex, no threshold;
R6 owns the pattern.

Rejected alternatives: `project` (would turn every order into a project), `record_type` (describes
the document, not the controlled unit), `batch_lot` unwidened (see NJ-PROD-1), and any operator,
shift or work-centre key (person and organisation names are never destination dimensions).

## NEEDS-JOSEPH

- **NJ-PROD-0 — edge shape.** Two schema-level coactivations (manufacturing ↔ logistics,
  manufacturing ↔ engineering) were removed from this template's `also_holds_with` per CONNECTION §5
  and are recorded for R1c. Both already exist on the `manufacturing` anchor, so no coverage is lost.
  Alternative if R1c disagrees: permit template→schema `also_holds_with` and restore them here.
- **NJ-PROD-1 — the execution anchor.** Is it a new `work_order` key, or should the anchor's
  `batch_lot` be widened from "material lot" to "execution instance" so discrete jobs and process
  batches share one key? Third option: R1c mints a general `case`-shaped key and manufacturing,
  quality and maintenance all bind to it — which would also settle the anchor's own NJ-MFG-2. This
  row states the gap and does not assume the answer.
- **NJ-PROD-2 — the missing line-log row.** The roster has no line-log or shift-log template (checked:
  twenty `manufacturing.*` ids, none of them). `Line 2 shift log 2026-08-17.xlsx` therefore has no
  template home. Alternatives: (a) it falls to the schema default; (b) Independent Records;
  (c) R1c widens this row to cover line-primary execution records. This row **excludes it** rather
  than annexing coverage it did not argue.
- **NJ-PROD-3 — serials.** Should serial numbers under an order be a dimension level below the
  order, or facts on members only? Untestable until `work_order` is adjudicated.
- **NJ-PROD-4 — answering the landed neighbour.** `manufacturing.inspection-record` NJ-INSP-2 asks
  whether an SPC chart or capability study belongs to inspection, to this row "as line evidence", or
  to `manufacturing.quality-management-system`. **This row declines it.** An SPC chart's subject is
  one characteristic over time across many orders: no instance identifier, no routed operation
  sequence, no reconciliation triple — it fails all three of this row's deterministic signals. This
  row agrees with the neighbour that it falls to Review Later until R1c places it.

## Residual routing

Independent Records (a standalone route card with no confirmed anchor); Receipts and Confirmations
(a job-complete notification with no routed structure); Review Later (an OCR-poor route card whose
instance identifier cannot be read — abstain rather than manufacture an order fact from a recovered
token); One-Off Images (a shop-floor photograph yielding no readable identifier); Unsupported or
Encrypted (a proprietary MES binary or password-protected order archive).

## Self-verification

`python3 -m json.tool` parses. Key set matches the landed sibling `manufacturing.inspection-record`
exactly. All ten neighbour ids resolve on `roster.json`. The `00` quotation and all three
landed-neighbour quotations grep back verbatim. `fields: []`, `dimension_order: []`, sensitivity
`potentially_sensitive`, no handling class, no threshold number, no regex. Every `collides_with` and
`also_holds_with` entry is an object with `domain`, `signal`, `provenance`. `design_cite` left `null`
throughout — the one verified `00` span is carried in `template.why` as prose rather than as a
decorative cite. Only the two assigned files were written.
