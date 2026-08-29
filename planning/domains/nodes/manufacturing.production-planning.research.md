# R1b lab notes — `manufacturing.production-planning`

**Depth: J-DEPTH**

Date: 2026-08-27  
Assignment: `kind: template` · `schema_id: manufacturing` · `launch: placeholder`  
Result: **keep narrowly** (`refuse_node: false`), field-less and dimension-less pending R1c.

## Verdict and strongest charge

This row survives as a **production-planning and scheduling situation**, not as a manufacturing
industry label or a row for the word “schedule”. Its anchor is a multi-order planning horizon joined
to products or materials, a plant/site or production line, demand or supply requirements, planned
dates, capacity/material constraints, and a release or freeze decision. It appears in demand plans,
master production schedules, MRP/APS runs, finite-capacity boards, shortage reviews, sequencing plans,
and S&OP packets that contain manufacturing supply and capacity decisions.

The strongest charge is that the parent manufacturing schema already covers production and line
records. Its proposed `product`, `site`, `batch_lot`, `asset`, `quality_event`, and `record_type`
keys are the same vocabulary this row would use, and its recognition includes production/traveller
and line/shift tables. The row survives only because planning has a distinct grammar and order:

- the parent production branch is product → batch/lot → record type for executed production and
  quality material;
- planning is many-order and horizon-led: site → planning period → product → line/resource → record
  type, with planned supply, demand, capacity and exception states but no actual operator signoffs or
  completed quantities;
- the planning-period and production-line proposals expose two unresolved facts that the field-less
  parent cannot currently express without minting; they are proposed for R1c, not silently legalized;
- the records can reveal demand, customer mix, bottlenecks, supplier dependencies and launch timing,
  so sensitivity is `potentially_sensitive` even though no handling class is assigned.

If R1c decides that the parent schema's product branch and a reusable horizon/capacity option already
cover this distinction, this row should be refused. That alternative is NJ-PLAN-1; retaining the
roster id is not evidence.

## Authority stack and method

Read before drafting:

- `planning/domains/dispatch/RESEARCH-BRIEF.md`, including the ratified J-DEPTH override.
- The complete stamped output of `python3 planning/domains/dispatch/make_prompt.py manufacturing.production-planning`.
- `planning/00-database-agent-product-design.md` (authoritative for design quotations) and
  `planning/01-product-design-structured.md` (locator only).
- `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`, `planning/domains/CONNECTION.md`,
  and `planning/domains/CONNECTION-EXAMPLES.md`.
- `planning/domains/canonical_fields.json`, `planning/domains/roster.json`, `planning/domains/ROSTER.md`,
  `src/evidence_shape/vocabulary.py`, and ratified `planning/overnight/council/DECISION-BRIEF.md`.
- The manufacturing schema anchor and landed `manufacturing.production-record` and
  `manufacturing.inspection-record` siblings, plus `identity.core-documents` for launch-depth
  observation/fact, privacy and false-positive discipline.
- Existing neighbour material for `engineering`, `logistics`, `business_operations`,
  `logistics.route-dispatch`, `construction_property.site-diary`, and manufacturing work-instruction.
  No neighbour was edited.

The stamped assignment still contains retired “gist” wording; J-DEPTH controls. CONNECTION also
controls edge semantics: template rows do not author `also_holds_with`; intended coactivation is
recorded here for R1c, and every collision object uses only `{domain, signal, provenance}`.

## External evidence used

These sources confirm recurring production-planning objects and their slot structures. They do not
license catalogue fields, identifier patterns, thresholds, authenticity judgments, or handling classes.

- [SAP Help — Production Planning Order](https://help.sap.com/docs/SAP_SUPPLY_CHAIN_MANAGEMENT/6166c217a51047bfa17361b36195a615/88a0237080f511da36bb000f20dac9ef.html)
  describes a planning order as intended material, quantity, availability date, component demand,
  capacity consumption, operations and lifecycle, and distinguishes it from the detailed production
  order used for actual production.
- [SAP Help — Planned Orders and Production Orders](https://help.sap.com/docs/PRODUCT_ID/ce74cb613bb44bc1925126c84b191ad9/b7bfe9550da47b43e10000000a4450e5.html?locale=en-US&state=PRODUCTION&version=1.0+SP28)
  confirms that a planned order is a procurement proposal created during planning and may convert to
  a production order or purchase requisition. Conversion is not inferred from a plan file.
- [SAP Help — Scheduling Production Orders](https://help.sap.com/docs/SAP_BUSINESS_BYDESIGN/2754875d2d2a403f95e58a41a9c7d6de/2ccb8df2722d1014ac18f7a1a5a5f0bd.html)
  describes whole-order and operation scheduling, planned start/end dates, rescheduling when quantity,
  duration or operations change, and bottleneck-resource scheduling.
- [SAP Help — Production Orders Quick Guide](https://help.sap.com/docs/SAP_BUSINESS_BYDESIGN/2754875d2d2a403f95e58a41a9c7d6de/2ddeddbe722d1014b9c7ce09018e9332.html)
  distinguishes order-header and operation views, planned data, release decisions, production-order
  execution and production lots. This supports the planning-versus-execution seam.
- [FDA Q7A GMP guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/q7a-good-manufacturing-practice-guidance-active-pharmaceutical-ingredients)
  provides a second sector's distinction between master production instructions and batch production
  records, where a batch record is prepared for each batch and records completion of significant steps.
  It is used as a concrete execution contrast, not as a universal production-planning rule.
- [FDA inspection guidance on batch records](https://www.fda.gov/about-fda/center-drug-evaluation-and-research-cder/field-compliance-programs-inspections-licensed-biological-therapeutic-drug-products-7356002m)
  confirms that batch records represent individual lots and document processes, tests, reworking and
  distribution. A planning schedule does not acquire those actuals merely by naming a product.

Product-design quotations below are verbatim from `00` and were checked against the source:

Exact quote check: “A file can simultaneously be a syllabus, part of a particular course, created for a particular semester, related to a university, included in an application package, a member of a version family, and potentially sensitive. These are separate facts about the same file.”

Exact quote check: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

Exact quote check: “The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically.”

Exact quote check: “A session should never be treated as proof of topic”.

## Bottom-up file set

The JSON records twelve concrete fixtures. They cover labelled planning workbooks, structured MRP
exports, presentations, image/OCR, email, archive manifests, mixed planned/execution sheets, and
false positives owned by engineering, logistics, business operations and execution records.

1. **`Plant-2_MPS_FY2026-Q3_RevB.xlsx`** (`spreadsheet`). Labelled planning plant, product/SKU,
   demand bucket, planned quantity, due/availability date, line/capacity bucket, status and freeze
   approval make this a master schedule. Filename product and quarter are observations, not facts by
   themselves; no operator signoffs or output actuals are present.
2. **`MRP-Run_2026-08-26.json`** (`code_structured`). Structured run metadata joins demand, projected
   supply, BOM/component requirements, shortage codes and planned-order proposals under a run horizon.
   JSON is only a source type; the planning object structure is the signal, and a planned proposal is
   not a converted production order.
3. **`Line-4_Finite-Capacity-Plan_Week-35.xlsx`** (`spreadsheet`). Planned operations join line/work
   centre, setup family, planned start/end, available capacity and overload/reschedule flags. Missing
   actual starts, operators and completed quantities make the planning/execution seam explicit.
4. **`Plant-2_Schedule-Freeze-and-Release-Review.pptx`** (`presentation`). Slides reconcile product
   demand, planned supply, line capacity and shortages for a labelled horizon, then record a freeze or
   release recommendation. It can also activate business governance from disjoint decision evidence;
   management approval does not prove execution.
5. **`AX410_Demand-and-Supply-Plan_2026-09.csv`** (`spreadsheet`). Product family, demand bucket,
   forecast, confirmed orders, projected supply, manufacturing site and shortage status are distinct
   columns. It is planning only when the supply/capacity frame is present, not merely because a
   product forecast exists.
6. **`Material-Availability-and-Shortage-Review_2026-08-27.eml`** (`email`). Native planner,
   procurement and scheduler roles, shortage discussion and MRP attachment names provide context.
   The message cannot donate attachment facts, establish a final reschedule, or prove supplier receipt.
7. **`MPS Board Screenshot - Plant 2.png`** (`image`). A screen-shaped board shows product rows,
   planned dates, line names and capacity colors; OCR recovers only partial labels. It may join an
   accepted planning group, but screen origin and partial OCR do not establish product, horizon or
   approval; absent EXIF is not screenshot proof.
8. **`Plant-2_Planning-Packet_Week-35.zip`** (`archive`). Manifest names demand forecast, MPS, MRP
   exceptions, capacity board, shortage review and release deck. Members retain separate functions,
   dates and evidence; the archive is inspected without extraction and cannot transfer one horizon or
   approval status to every member.
9. **`Production-Schedule-and-Work-Order-Release_2026-08.xlsx`** (`spreadsheet`). The shared collision
   fixture has planned multi-order rows and a released-order sheet. Blank actual columns on planned
   rows support planning; populated routed actuals, signoffs or yield on one order would support the
   production-record sibling. A release proposal is not completed production.
10. **`AX410_Routing-and-Setup-Instruction_RevC.pdf`** (`text_document`). Controlled revision,
    operation sequence, standard times and setup parameters define a reusable method. Without demand
    horizon, order list, planned quantities or capacity exceptions it is work-instruction/engineering
    evidence, even though schedules consume its routing values.
11. **`Inbound-Component-Availability-and-Delivery-Board.xlsx`** (`spreadsheet`). Component, purchase
    order, supplier, promised receipt, warehouse location and delivery status dominate; a few planned
    demand references are not a manufacturing schedule. It is the logistics collision fixture.
12. **`Plant-2_Line-4_Shift-Output-and-Downtime_2026-08-27.xlsx`** (`spreadsheet`). Actual output,
    scrap, downtime, changeover and operator signoffs by line/shift make it an execution/line log, not
    planning. Planned-order references are passing values only.

## Node test — all three legs

### 1. Detection signals differ from the parent default

The manufacturing schema union covers executed batch/traveller records, genealogy, inspections,
quality events, maintenance, assets, HSE and line/shift logs. It does not by itself distinguish the
planning situation's **many-order, future-facing grammar**:

- products/materials are rows in a demand or supply horizon rather than one produced lot;
- planned orders join component demand, source of supply, capacity and availability/due dates;
- finite scheduling assigns operations to lines/work centres and exposes overload, setup or sequence
  decisions without actual operator/completion evidence;
- freeze/release and shortage decisions are planning states, not QA release or production completion;
- MRP/APS artifacts reconcile independent demand with projected supply and planned proposals.

The same words—production, order, line, quantity, date, release—occur in the parent and its siblings.
The distinguishing evidence is the combination of multi-order horizon, planned-vs-actual absence,
resource/capacity exceptions and demand/supply structure. A schedule title, product number or due date
alone is never enough.

### 2. Recommended dimensions differ from the parent default

The parent manufacturing template is branch-shaped prose: product → batch/lot → record type for
production/quality, site → asset → record type for maintenance/calibration, and quality event → record
type for NCR/CAPA. Planning resolves a different branch: site → planning period → product → line or
resource (when line-primary) → record type, with a site/product aggregate for S&OP. A planned order is
not a batch/lot, and `record_type` is useful here because schedule, MRP, capacity and release files
are genuinely different functions.

`planning_period` and `production_line` remain proposals; no dimension is serialized while the schema
is field-less. The exact `00` quote is: “For document and record domains, project, function, or subject
usually comes before time because putting year first scatters related work across calendar folders.”
The planning subject (site/product/horizon) must contextualize time; file creation date is not the
horizon.

### 3. Privacy rules differ from the parent default

Sensitivity remains `potentially_sensitive`, but planning concentrates demand forecasts, customer mix,
product launches, capacity bottlenecks, shortages, supplier dependencies and production sequencing in
files that may be widely shared internally. This is a concentration and exposure difference, not a new
handling class. P7 owns protection and model-access policy; names of customers, workers, suppliers and
decision owners remain role observations and never become destination dimensions.

## Proposed fields — four exact-key secondings and two candidates

`fields` remains empty. `product`, `site` and `record_type` exactly second the manufacturing schema's
proposals. `planning_period` is a new candidate because no canonical field represents the horizon the
schedule is about. `production_line` is a candidate because a line/work centre is a capacity resource,
not necessarily one maintained asset. Both are sent to R1c rather than legalized here. No planned-order
identifier is minted: the existing `work_order` proposal belongs to execution/maintenance and reusing
it could collapse planned and executed states.

Rejected alternatives from the anchor and nearby rows: `batch_lot` is a produced material quantity,
not a planning horizon or planned order; `asset` may be a machine but cannot safely mean a line/cell
without role adjudication; `creation_date` is not a schedule horizon; `version_family` identifies bytes,
not a business baseline; `project` would turn every planning run into a project; customer or supplier
names are roles, not destination dimensions.

## Collision fixture and reciprocal boundaries

The strongest same-byte fixture is **`Production-Schedule-and-Work-Order-Release_2026-08.xlsx`**. Its
planned rows and released-order sheet share product/order tokens, dates and line assignments with an
execution packet. The discriminator is not the file name or order number: planning requires many
planned items, future-facing dates, capacity/material exceptions and blank actuals; production-record
requires one order/batch with populated routed operations, operator signoffs, actual quantities, yield
or scrap. Sheet-level evidence must remain separate.

The JSON authors eight reciprocal collision objects, each with exact `{domain, signal, provenance}`
shape and an explicit SAME FIXTURE BYTES line:

- `manufacturing.production-record`: planned many-order rows versus one order's populated actuals;
- `manufacturing.work-instruction`: schedule assignments versus a reusable controlled method;
- `engineering`: planning use of routing versus engineering definition/revision;
- `logistics`: manufacturing shortage/capacity decisions versus inbound custody and delivery;
- `business_operations`: manufacturing horizon and loads versus S&OP governance and commitments;
- `business_operations.corporate-regulatory-filings`: operational plan versus statutory wrapper;
- `logistics.route-dispatch`: pre-execution production assignment versus shipment route/custody;
- `construction_property.site-diary`: recurring manufacturing plan versus property/trade progress.

No template-level `also_holds_with` is authored. The S&OP deck, demand/supply plan and planning decision
log can carry independently evidenced Business Operations governance and manufacturing planning roles;
the same workbook can carry planning and production-record sheets. Those intended coactivations are
recorded for R1c, not represented as a forbidden template edge.

## Neighbours considered but not edged

- **`manufacturing.asset-register`** — a capacity board can list machines, but its subject is planned
  load/horizon, not the controlled population, status and service history of assets. The line/resource
  seam is already represented through the `production_line` proposal and NJ-PLAN-2.
- **`manufacturing.maintenance-work-order`** — maintenance may be scheduled in a planner board, but a
  maintenance job's subject is an asset and work performed; this row requires many planned production
  orders and capacity/material planning.
- **`manufacturing.inspection-record`** — inspection dates and quantities may be scheduled, but a plan
  does not record measured characteristics, instruments, pass/fail or disposition. The shared order
  token is not enough.
- **`manufacturing.nonconformance-capa`** — shortage or delay exceptions are not quality events unless
  an identified deviation/CAPA case with containment, disposition and closure exists.
- **`finance`** — forecasts and quantities can feed financial plans, but a manufacturing capacity and
  planned-order frame is not a budget or account record. Finance is a schema-level coactivation option,
  not an additional template edge here.
- **`research`** — a production simulation or optimization paper can use the same terms, but a model
  or publication has no live plant demand/supply/capacity decision unless independently evidenced.
- **`photos`** — a planning-board screenshot may activate Photos capture evidence as well as planning
  only when its own image evidence supports both; this template does not claim every screenshot.

## Files considered and rejected from activation

- A **production traveller, batch record or line shift log** with actual operator signoffs, completed
  quantities, scrap/yield and execution dates is production-record evidence, not planning; a planned
  column inside it does not reverse the subject.
- A **routing or setup instruction** with revision, standard times and process parameters but no
  demand, order, horizon or capacity table is work-instruction/engineering evidence.
- A **purchase order, supplier promise, warehouse board or delivery confirmation** is logistics or
  procurement evidence unless it is joined to a manufacturing MRP/shortage decision and planned supply
  frame.
- A **sales forecast or executive strategy deck** is business operations unless it contains a
  manufacturing site/product/capacity/supply decision; product and quantity words alone do not fire.
- A **machine or line maintenance schedule** is asset/maintenance evidence if work performed, service
  interval or asset condition is the subject; a line label alone does not make production planning.
- An **engineering simulation, test schedule or project plan** may have dates and resources, but no
  manufacturing demand/supply or planned-order structure; it remains engineering/research/project
  material.
- A **calendar invite, email, screenshot, scan batch or archive name** can join a planning group only
  after independent planning evidence; context never copies a horizon or product fact.
- An **opaque ERP/MES/APS export** remains indexed-but-unreadable until an approved local extractor
  confirms planning structure. Extension and system branding are not content evidence.

## Sensitivity and NEEDS-JOSEPH

This row is `potentially_sensitive` because production plans expose demand, customer mix, launch timing,
capacity bottlenecks, supplier dependencies, shortages and sequencing. No P7 handling class is assigned.

- **NJ-PLAN-1 — distinct row or parent option?** Once R1c adjudicates the manufacturing proposals,
  should this horizon/capacity grammar remain a template, or is it a reusable option on the parent
  manufacturing branch? Both readings are defensible; do not silently collapse it.
- **NJ-PLAN-2 — line versus asset.** Should `production_line` become a canonical resource key, or should
  manufacturing's `asset` carry line/work-centre roles with a role split? A line contains maintained
  machines and is not always itself an asset.
- **NJ-PLAN-3 — planning horizon.** Should `planning_period` become a global neutral period key, or
  remain search-only? A schedule snapshot date and a demand horizon are different values, and no current
  canonical field expresses the latter.
- **NJ-PLAN-4 — planned-order identity.** Should planned-order identifiers reuse `work_order`, receive a
  distinct key, or remain evidence only? Reuse risks making planned and executed states indistinguishable.
- **NJ-PLAN-5 — mixed workbook activation.** When a workbook carries planned sheets and actual execution
  sheets, should sheet-level evidence permit both planning and production-record activation, or require
  a primary user decision? The fixture makes the seam explicit.
- **NJ-PLAN-6 — coactivation.** An S&OP deck or demand/supply plan may carry Business Operations and
  manufacturing facts independently. R1c should author schema-level coactivation if appropriate while
  this template keeps `also_holds_with` empty.
- **NJ-PLAN-7 — extractor scope.** Which ERP/MRP/APS export formats receive approved local extractors?
  Until an extractor is approved, opaque exports remain metadata-only and fall through.

## Self-verification

`python3 -m json.tool` parses. All twelve examples use closed `SOURCE_TYPES`; every collision domain
resolves on the roster and every residual name is one of the nine contract residuals. `fields` and
`template.dimension_order` are empty; proposed keys are exact parent secondings plus two explicit R1c
candidates; template-level `also_holds_with` is empty. Each collision object has exactly `domain`,
`signal`, `provenance`, names SAME FIXTURE BYTES and states both directions. The four exact product-design
quotes grep back verbatim from `00`. No threshold, confidence score, handling class, invented path,
`related_to`, `why`, `domain_id`, `id` or `target` collision key is used. Only the two assigned files
were written; no commit was made.
