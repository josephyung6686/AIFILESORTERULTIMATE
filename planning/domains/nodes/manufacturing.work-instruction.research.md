# manufacturing.work-instruction — research memo (R1b, J-DEPTH)

Date: 2026-08-27
Roster row: `kind: template` · `schema_id: manufacturing` · `launch: placeholder`
Legacy coverage: `mfg.work-instruction` (ROW)

## Verdict

**Keep provisionally; do not refuse.** A controlled work instruction is a genuine organizational
situation: it tells an operator how to perform one repeatable operation at a type-level scope, under
a controlled revision, effective date and approval. The load-bearing relation is controlled
manufacturing scope → ordered steps → tooling/materials → specified parameters → checks and safety
controls. “Work instruction” and “SOP” are labels only; this structure is the evidence.

The row is narrower than the manufacturing schema's broad execution grammar. A production record
carries actual values for one order or lot; an engineering specification states normative
requirements across many jobs; a warehouse procedure governs internal custody; a business policy
binds a population or administrative process. The work instruction is reusable across those worlds
only when its own station, machine, product or process scope and controlled operator steps are shown.

This survival is conditional. The manufacturing schema remains a PR-6 fieldless placeholder, so this
template writes no fields and no executable dimensions. If R1c decides that the type-level document
is merely the schema's `work instruction` work-type value, or cannot preserve the type-versus-instance
boundary, refusal is required. The row is not retained just to rescue the legacy id.

## Authority stack and method

Read and applied:

- `planning/domains/dispatch/RESEARCH-BRIEF.md`, including the J-DEPTH override.
- Complete stamped output of `python3 planning/domains/dispatch/make_prompt.py manufacturing.work-instruction`.
- `planning/prompts/ALIGNMENT.md` and authoritative `planning/00-database-agent-product-design.md`;
  `planning/01-product-design-structured.md` was used only as a locator and `00` wins.
- `planning/domains/CONNECTION.md`, `CONNECTION-EXAMPLES.md` and `_CONTRACT.md`, especially node
  testing, activation versus grouping, the closed edge vocabulary and template-only
  `also_holds_with` prohibition.
- `planning/domains/canonical_fields.json`, `planning/domains/roster.json`, `ROSTER.md` section 4
  and Appendix A, and `src/evidence_shape/vocabulary.py`.
- Ratified `planning/overnight/council/DECISION-BRIEF.md` (D1–D6, J-IND and J-DEPTH).
- Landed `manufacturing` schema and memo; `manufacturing.production-record`,
  `business_operations.policy-handbook`, `engineering.material-specification`,
  `logistics.warehouse-ops`; and `identity.core-documents` for launch-depth calibration.
- Existing neighbour material was inspected without editing it, including commissioning,
  requirements, compliance, training, driver-compliance, maintenance and calibration rows.

No jurisdiction-specific standard, quality-system certification, safety law, process parameter,
worker-performance rule, document-control software rule, detector regex, threshold, confidence score
or handling class is asserted. The files below are concrete fixtures and recurring structures;
domain-specific conclusions are inference/proposal, not legal authority.

## Design evidence and quote discipline

The direct product-design anchors are:

- `00` says, **“Every file will be treated as a record with many facts, rather than forcing it into
  one permanent category.”** An instruction can therefore also be a version-family member, a group
  member and potentially sensitive without becoming one permanent category.
- `00` says, **“A session should never be treated as proof of topic, and it should not carry the same
  confidence as a hash match or a directly extracted document fact.”** Release email, training event
  and portal-download context are grouping/review clues, not proof of instruction content or status.
- `00` says, **“For document and record domains, project, function, or subject usually comes before
  time because putting year first scatters related work across calendar folders.”** The prose order
  below is product/process or station first, not year first.
- `00` says, **“The system recommends an order based on the domain template, but the user can reverse,
  remove, add, or flatten dimensions.”** The recommendation is not a frozen path.
- For image evidence, `00` says, **“However, the system must not mistake the absence of EXIF for proof
  that an image is a screenshot.”** A photographed page needs controlled-document structure, not only
  image metadata.

These quotations are reproduced exactly in the JSON or here. Manufacturing-specific distinctions and
field recommendations are inference/proposal and do not use fabricated design citations.

## J-DEPTH node test — all three legs

### Detection signals differ from the schema default

The manufacturing schema anchor is deliberately broad: it joins recurring transformation or control
cycles to a product, batch/lot, site/line, controlled asset or quality event. Its default includes
executed travellers, lot genealogy, inspections, nonconformance/CAPA, calibration, maintenance,
asset registers, line logs and HSE records. Its work_types already include “work instruction,
standard operating procedure or setup sheet,” so a row named only after that phrase would fail.

This template's signal is a type-level controlled document plus its manufacturing scope and ordered
operator execution. A setup sheet identifies a station or machine, fixture/tools, sequence and
specified ranges, often with first-piece or in-process checks. A visual work aid carries annotated
operation images plus control metadata. A cleaning, sanitation, line-clearance or lockout procedure
sets preconditions, actions, verification and release. Such a file can exist before a lot is made and
can be reused across many lots.

The negative signal is essential. A traveller with the same procedure text but actual quantities,
timestamps, operator signoffs and release disposition is a production record. A special-process
document with normative requirements, qualification and sampling is engineering material
specification. A pick/pack standard-work document has internal custody, bin and outbound-wave
structure rather than transformation or in-process control. A company-wide policy has population
scope, obligations and administrative responsibilities rather than one shop-floor operation.

The strongest same-schema collision is `manufacturing.production-record`. The exact procedure and
parameter table can appear in both `Setup sheet OP30 AX-410 rev C.pdf` and
`BPR_AX410_L240817-03.pdf`. The discriminator is what the table is bound to: type-level scope and
specified ranges versus one order/lot and actual execution. This template resolves the reusable
instruction side without taking the production instance.

### Recommended dimensions differ from the schema default

The manufacturing anchor holds several branch patterns in prose: product → batch/lot → record
function for production and quality; site → asset → record function for maintenance and calibration;
quality event → record function for NCR/CAPA. Those are appropriate for records of what happened.

This situation is reusable across orders, so its provisional recommendation is product or process →
site/station or machine → record type. Site is optional in a single-plant corpus. Batch/lot is
omitted because the instruction is not one execution instance. Revision remains universal
`version_family` evidence rather than a branch level: separating Rev A/B/C into folders can split one
controlled family and falsely turn a path into a fact.

The machine order stays `[]` because manufacturing declares no legal fields. R1c may reuse the
anchor's proposed `product`, `site`, `asset` and global `record_type`; operation/station, document
number, revision, parameter and effective state remain evidence until canonical adjudication. The
row does not mint `operation`, `station`, `instruction_id`, `revision` or `effective_date`.

This is not time-first. Effective, review, training and execution dates refer to different events.
Product/station-first organization keeps an instruction with the process it governs while dates stay
searchable and version-family evidence.

### Privacy differs from the schema default

The manufacturing schema is already potentially sensitive because production recipes, supplier
genealogy, plant layouts, failures, corrective actions and worker records can expose a business.
This template concentrates the exposure in a reusable recipe: settings, parameter ranges, tooling,
fixtures, material sequence, quality gates, safety interlocks and distribution controls. It can teach
the process without any lot record, and release/training packets may add named operators or access
restrictions.

The row therefore keeps `potentially_sensitive`, prefers bounded local excerpts and excludes product
names, machine tags, worker names, parameter values, document identifiers and effective state from
destinations until R1c. This is not a P7 handling class.

### Node-test conclusion

The row clears the test in the narrow form: controlled type-level operator instructions have a
document-control plus ordered-step/parameter grammar not equivalent to executed records or normative
specifications; they need a product/process or station-first recommendation rather than lot-first;
and they concentrate reusable process IP and safety/access detail. If R1c sees these only as a
work-type value, refusal is correct.

## Bottom-up file set

The JSON carries nineteen concrete fixtures:

1. **`Setup sheet OP30 AX-410 rev C.pdf`** (`text_document`): controlled number, revision,
   effective date, approver, operation/station scope, steps, tooling and specified ranges, with no
   lot actuals.
2. **`BPR_AX410_L240817-03.pdf`** (`text_document`): the same OP30 table and procedure text inside
   a batch record, but actual values, timestamps, signoffs and release disposition bind it to one
   instance.
3. **`CNC-07 Setup Parameters.xlsx`** (`spreadsheet`): machine, fixture, tool list, setup sequence,
   ranges and first-piece checks plus control metadata; ranges do not prove achievement.
4. **`PS-217 Rev 3 - Solution Heat Treat and Age.docx`** (`text_document`): normative special-process
   scope, allowable ranges, qualification and test provisions; engineering specification, not an
   operator instruction.
5. **`SOP-014 Goods receipt.docx`** (`text_document`): numbered responsibility steps and revision
   history for administrative/warehouse receipt work; SOP vocabulary alone cannot choose a side.
6. **`Pick-Pack Standard Work - Bay 3.pdf`** (`text_document`): photographs, steps, bins, item
   codes and outbound references describe warehouse custody, not transformation.
7. **`Line-4 Changeover Checklist.jpg`** (`image`): photographed/scanned line, tooling, cleaning
   and verification checklist with unreadable completion marks; reusable versus completed is unresolved.
8. **`MES Work Instruction Export.json`** (`code_structured`): structured document revision,
   operation, station, steps, parameters and approval versus execution acknowledgements.
9. **`WI_scan_OP30_page-2.jpg`** (`ocr`): partial OCR of station heading, steps, tools and ranges;
   cut-off approval prevents a validated current revision.
10. **`Operator Training - OP30.pptx`** (`presentation`): selected steps and photographs in a
    training deck, without the full controlled instruction or effective release.
11. **`WI release and withdrawal notice.eml`** (`email`): native fields cite a revision, attachment
    and withdrawn copy, but contain no instruction body.
12. **`Annual SOP review - Plant 2.ics`** (`calendar`): review appointment with plant and procedure
    terms but no revision content or outcome.
13. **`Work Instruction Archive - Plant 2.zip`** (`archive`): manifest of current/withdrawn PDFs,
    setup sheets, visual aids, notices and training references; it is inspected without unpacking.
14. **`Portable torque tool calibration.jpg`** (`image`): tool and calibration markings but no
    numbered operator sequence or controlled scope.
15. **`Process map - Operator Steps.svg`** (`design_creative`): flowchart labels and arrows but
    draft designer/project metadata without released control.
16. **`Home appliance assembly instructions.pdf`** (`text_document`): consumer assembly/safety
    steps and model name, with no local shop-floor scope or controlled copy.
17. **`Router setup.pdf`** (`text_document`): ambiguous filename spanning network, woodworking and
    manufacturing meanings; body is unreadable.
18. **`Safety Data Sheet - Acetone.pdf`** (`text_document`): hazard, handling and property sections
    but no local operation, approved range or operator scope.
19. **`Instruction packet - OP30.zip`** (`archive`): released WI, blank acknowledgement, training
    deck and batch traveller share a reference but have different document functions.

The set covers labelled and unlabelled prose, spreadsheets, native/OCR images, presentation, email,
calendar, structured JSON, design graphics, archives and ambiguous/unreadable bytes. It includes
same-byte type/instance, normative/execution, custody/process and administrative/shop-floor
collisions, plus sparse members that must not inherit facts.

## Reciprocal boundaries and same-byte collision fixtures

### Manufacturing production records

**Same fixture bytes:** `Setup sheet OP30 AX-410 rev C.pdf` and the same parameter table embedded in
`BPR_AX410_L240817-03.pdf`.

- This row owns the type-level controlled instruction: scope, revision/effective control, ordered
  steps, tooling and specified ranges without one-lot actuals.
- `manufacturing.production-record` owns instance execution: order/lot, actual values/timestamps,
  operator signoffs, issued/good/scrap reconciliation and release disposition.

Procedure text, product name, range or signoff alone allocates neither. This row must not take actual
traveller values; production-record must not take a reusable setup sheet merely because it names a
product and operation.

### Engineering material specification

**Same fixture bytes:** `PS-217 Rev 3 - Solution Heat Treat and Age.docx`.

- This row owns operator-facing ordered execution with station/tooling, specified ranges, checks and
  controlled release.
- `engineering.material-specification` owns normative requirements, qualification, standards,
  sampling and acceptance across many jobs.

Temperature, time, process name, revision or approval alone decides neither. `Furnace 2 - Load and
Unload Steps Rev B.docx` is the instruction-side negative where station, fixture and per-load sequence
are explicit.

### Logistics warehouse operations

**Same fixture bytes:** `Pick-Pack Standard Work - Bay 3.pdf`.

- This row owns a process/assembly/test/control instruction at a manufacturing station with
  parameters, tooling/material inputs and in-process checks.
- `logistics.warehouse-ops` owns internal custody: pick, pack, scan, bin, handling unit and outbound
  wave, with no transformation or manufacturing release.

Numbered steps, item code, bay, revision or operator audience allocates neither. Manufacturing must
not claim warehouse standard work; warehouse-ops must not claim a manufacturing setup merely because
goods pass through a station.

### Business policy and procedures

**Same fixture bytes:** `SOP-014 Goods receipt.docx`.

- This row owns a shop-floor instruction tied to product/process and station/machine control.
- `business_operations.policy-handbook` owns an organization-wide governing procedure with scope,
  responsibilities, obligations, review and document governance.

Numbered steps, responsibility columns, revision history and “SOP” alone allocate neither. The
manufacturing row must not take an administrative procedure; policy-handbook must not take a shop-floor
execution instruction merely because both are controlled.

### Engineering commissioning and handover

**Same fixture bytes:** `Irrigation-Pump-Commissioning-Pack_Field-12.zip` and the visual-aid form
`Process map - Operator Steps.svg`.

- This row owns a reusable station/process procedure with steps, ranges, tooling and checks.
- `engineering.commissioning-handover` owns installed-instance acceptance: as-built identity,
  test results, settings, punch-list closure, witnessed acceptance and transfer.

A step diagram, machine tag, parameter, handover word or approval alone allocates neither. Operators
receiving an acceptance pack does not make it a work instruction; a type-level procedure used during
startup does not become handover evidence.

## Files considered and rejected

- **Blank traveller or blank setup form:** a grid without controlled scope/effective approval or
  execution values is unresolved template material, not a current instruction by filename.
- **Completed traveller/batch record:** actual values, timestamps, lot and release disposition make
  `manufacturing.production-record`, even when the instruction is embedded.
- **Special-process specification:** normative requirements and qualification are engineering;
  ranges do not become operator instructions by themselves.
- **Engineering drawing, CAD or commissioning pack:** controlled design and installed acceptance are
  engineering evidence, not a shop-floor procedure.
- **Warehouse pick/pack or goods-in SOP:** bins, handling units and outbound waves are logistics;
  no transformation or manufacturing release appears.
- **Corporate policy or administrative procedure:** population scope and obligations are business
  operations; “procedure” is not a manufacturing signal.
- **Maintenance manual or calibration certificate:** general service instructions and as-found/as-left
  results are reference or maintenance/calibration evidence unless a reusable operator scope is shown.
- **Training deck or acknowledgement:** can join an instruction-release group but cannot prove body or
  effective status.
- **Supplier manual, SDS or public standard:** external reference/specification until local control
  and manufacturing scope are evidenced.
- **Consumer assembly booklet:** numbered steps and a model name do not establish local shop-floor
  control.
- **Draft process map or visual aid:** controlled scope, revision/effective metadata and checks are
  required; designer title block alone is insufficient.
- **Machine/product photograph:** image metadata and visible tooling are not instruction evidence;
  grouping may attach the image without copying facts.
- **Portal screenshot, release email or review calendar:** session/context clue only; no steps,
  approval or current revision may be inferred.
- **Ambiguous `Router setup.pdf`:** filename cannot choose network, woodworking or manufacturing
  meaning; unreadable bytes fall through safely.
- **Encrypted MES export:** metadata-only indexing cannot rescue a work-instruction-shaped filename.

## Neighbours considered without an additional edge

- **`engineering.requirements-specification`:** considered for process requirements and acceptance;
  material-specification is the sharper, fixture-backed normative/execution seam.
- **`business_operations.compliance-audit`:** an audit may inspect an instruction, but programme,
  finding, evidence request and closure are not instruction content; a group can connect them.
- **`business_operations.training-development`:** training and competence records reference an
  instruction but are not its controlled body; training is group context here.
- **`logistics.driver-compliance`:** driver licences, hours, routes and competence are transport
  records; generic safety words are never-alone.
- **`business_operations.procurement-sourcing`:** buyer/supplier evaluation is procurement; local
  approved operation/setup begins the manufacturing instruction.
- **`manufacturing.maintenance-work-order` and `manufacturing.calibration-record`:** performed
  asset-specific work and as-found/as-left evidence are their situations; reusable operator procedure
  needs type-level process scope.
- **`manufacturing.tooling-fixture`:** rostered but not landed; tooling identity alone activates
  neither row, and the fixture row would own an enduring tool record if preserved.

## Proposed fields — deliberately empty

Full list: `[]`. Manufacturing declares no field rows under PR-6. This template cannot copy or mint a
second schema field list, and `template.dimension_order` remains empty until a canonical key is
licensed.

The anchor's proposals are the only candidates worth carrying forward: `product`, `site`, `asset`
and global `record_type`. This research suggests a process/operation or station role, but no canonical
key licenses it and this row will not mint `operation`, `station`, `instruction_id`, `revision` or
`effective_date`. Revision is universal version-family evidence; control metadata is evidence rather
than an automatic folder level. Parameters, tools, worker names and customer references are
high-cardinality or privacy-loaded.

## Template coactivation for R1c — memo only

The contract restricts `also_holds_with` to schema rows, so this template authors an empty array.
R1c should adjudicate intended independent activation:

- manufacturing ↔ engineering for the special-process specification plus operator-instruction packet;
- manufacturing ↔ business_operations for a document carrying both organization-wide obligations and
  station steps;
- manufacturing ↔ logistics for a receiving/internal-custody procedure that also carries a genuine
  manufacturing transformation or control relation;
- manufacturing ↔ photos for a photographed checklist with both camera evidence and an independent
  instruction/checklist structure.

These are recommendations, not authored coactivation edges. Empty `also_holds_with` is required for a
template and does not claim files cannot carry multiple schemas.

## NEEDS-JOSEPH

- **NJ-WI-1 — type versus instance:** Is the reusable controlled instruction distinct from
  `manufacturing.production-record`, or should both be one work-type family under the manufacturing
  default? Keep only if type-level control and instance actuals remain independently actionable.
- **NJ-WI-2 — canonical subject:** Should R1c reuse `product`, `site`, `asset` and global
  `record_type`, with operation/station as values/search facets, or license one neutral process role?
  This row proposes no private key.
- **NJ-WI-3 — normative versus executional:** When a specification and instruction repeat ranges,
  should manufacturing and engineering coactivate on disjoint evidence, or should one side own the
  shared document while the other is only a group member?
- **NJ-WI-4 — policy versus shop floor:** Should a mixed SOP packet lift manufacturing↔business schema
  coactivation, or remain independently scoped at member/section level?
- **NJ-WI-5 — logistics boundary:** For goods receipt, internal handling and line-side material
  procedures, does custody plus one manufacturing setup justify both schemas, or should dominant
  purpose own the bytes? The same decision affects `SOP-014 Goods receipt.docx`.
- **NJ-WI-6 — sensitive depth:** Should process parameters, machine identifiers, worker references
  and controlled revision state remain search-only, or may a user-confirmed private tree expose values?
- **NJ-WI-7 — sparse release members:** Is accepted-group context sufficient for a release email,
  review event, screenshot or training deck to join while its own instruction facts remain unknown?
- **NJ-WI-8 — control validity:** Which rule family confirms that effective date, approver and
  withdrawal state are authoritative rather than copied text? Until resolved, preserve as possible.

## Refusal condition and audit claim

Refusal status: **not refused, with an explicit collapse condition**. Refuse if the only distinction
is “work instruction,” an extension, numbered steps, or a product/machine name; or if controlled
type-level steps cannot be separated from production actuals and engineering normative requirements.
Keep only if the reusable instruction relation, product/station-first recommendation and process-IP
privacy posture remain implementable.

The row claims no current revision, operator competence, process safety, parameter correctness,
product conformity, legal compliance or destination path. It claims only that manufacturing corpora
contain controlled operator instructions with scope, ordered execution, tooling, specified parameters,
checks, safety controls and revision/effective metadata, distinguishable from production, engineering,
logistics, business, reference and residual files.
