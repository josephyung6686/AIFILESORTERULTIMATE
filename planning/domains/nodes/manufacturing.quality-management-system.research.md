# Quality management system documentation — R1b research memo

**Depth: J-DEPTH**

## Scope and authority

This memo owns only `manufacturing.quality-management-system`. The stamped assignment makes it a
`kind: template` on `schema_id: manufacturing`, with no parent. The manufacturing anchor is a
placeholder schema under PR-6: its `fields` array is empty and its proposed product/site/lot/asset/
quality-event/record-type vocabulary awaits R1c. This template therefore writes no fields, does not
copy the anchor's proposed fields, and leaves `template.dimension_order` empty in JSON. The possible
QMS order is explained in prose for R1c.

Sources read before writing:

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the stamped output of
  `python3 planning/domains/dispatch/make_prompt.py manufacturing.quality-management-system`;
- `planning/prompts/ALIGNMENT.md`, `planning/00-database-agent-product-design.md`,
  `planning/01-product-design-structured.md`, `planning/domains/_CONTRACT.md`, and
  `planning/domains/CONNECTION.md`;
- `planning/domains/roster.json`, `planning/domains/canonical_fields.json`, and
  `src/evidence_shape/vocabulary.py`;
- `planning/domains/nodes/manufacturing.json` as the schema anchor and the landed
  `identity.core-documents` exemplar for depth, safety and edge discipline;
- landed manufacturing inspection, calibration, nonconformance/CAPA, safety-case and related
  siblings for the established JSON shape and boundary idiom.

The design does not name a Quality Management System as a separate schema or template. This row is
therefore a proposal extending the named Manufacturing situation. The following quotations are
from `planning/00-database-agent-product-design.md` and were checked there verbatim:

- “Every file will be treated as a record with many facts, rather than forcing it into one
  permanent category.”
- “The engine should treat the file extension as a routing signal rather than an assumption about
  meaning,”
- “Archives should be inspected without being unpacked to disk.”
- “A session should never be treated as proof of topic, and it should not carry the same
  confidence as a hash match or a directly extracted document fact.”
- “For document and record domains, project, function, or subject usually comes before time
  because putting year first scatters related work across calendar folders.”
- “Independent Records may live under Personal/Independent Records and hold standalone
  certificates, notices, confirmations, forms, and PDFs that have a durable purpose but no broader
  group.”
- “Review Later may hold files whose meaning is partly understood but whose final location requires
  a future decision.”
- “Protected Records may represent sensitive isolated material such as passport scans, medical
  documents, account statements, visas, legal forms, or credentials; it should normally remain
  local-only and must not cause filenames or content to be exposed in model prompts.”

The QMS-specific file structures and boundary claims below are inferences from the manufacturing
anchor and ordinary quality-system records, not quotations from the product design.

## Node test

The row is retained provisionally because its three distinguishing legs are real and not merely
file extensions or work-type labels.

**Signals.** The manufacturing schema anchor is activated by a repeatable transformation or control
cycle tied to a product, batch/lot, site/line, controlled asset or quality event. A QMS template
needs a wider system relation: a manual or process map defines controls that span products or
processes; controlled procedures and document registers govern the system; an audit programme or
report evaluates several processes against criteria; and a management review joins objectives,
complaints, supplier performance, resources and actions. A single inspection result, work
instruction, calibration certificate, NCR or CAPA case can cite the QMS but does not establish the
system-level situation.

**Dimensions.** The anchor's production default is product -> batch_lot -> record_type; its
maintenance alternative is site -> asset -> record_type; its nonconformance alternative is
quality_event -> record_type. QMS material is function/system-led: if R1c licenses a neutral scope
field, the useful recommendation is site or organization scope -> quality-system process/area ->
record_type, with reporting period only for recurring audits, KPI packs and management reviews.
Product and batch_lot remain optional references when a procedure or audit is product-specific; they
should not become the parent of a manual that governs several products. Because no fields are
licensed at launch, the JSON stores no dimensions.

**Privacy.** QMS material often contains audit findings, complaint and supplier trends, process
weaknesses, named auditors or owners, training status, management decisions and quality objectives.
These details can expose operational vulnerabilities, personal performance information and
commercial position. The template is consequently `potentially_sensitive`; it assigns no handling
class and does not make personnel, findings, scores, revision identifiers or action details folder
dimensions.

The strongest objection is that quality manual, procedure, audit, review, training and corrective
action are simply `record_type` values under Manufacturing. The row survives only where those files
form the governed system itself: controlled documents establish scope and responsibility, audits
test the system across processes, management review evaluates trends and resources, and action
records close the loop. If a corpus contains isolated procedures or single audit checklists with no
cross-process governance, the row should be refused; the narrower Manufacturing sibling or residual
templates cover the evidence.

## Bottom-up file set

The JSON records fourteen concrete files. `observations` are raw extractor observations, while
`facts_legal` is deliberately limited to universal facts because the manufacturing schema's domain
fields remain deferred. Proposed QMS scope and record fields are not silently asserted. A sparse
calendar, email, image or checklist may join an accepted QMS group, but grouping does not copy the
system scope, site, product or review period onto it.

### Manual, procedures and audit records

* `Quality-Manual_Rev12.pdf` (`text_document`, `.pdf`) has a title, revision, scope across multiple
  manufacturing processes/sites, management responsibilities, quality objectives, document control
  and audit-review sections. It is the strongest native-text system anchor. The filename does not
  itself establish scope, currentness or membership in every procedure in the corpus.

* `Document-Control-Procedure_QP-001.docx` (`text_document`, `.docx`) contains labelled procedure
  identifier, owner, approval/effective date, revision history and controlled-document issuance,
  distribution and acknowledgement rules. These fields distinguish system governance from an
  executable machine setup instruction. A procedure number or owner name alone is not QMS proof.

* `Internal-Audit-Programme_2026.xlsx` (`spreadsheet`, `.xlsx`) schedules audits across production,
  quality, purchasing and maintenance processes. Its headers label criteria, scope, auditor,
  planned date and follow-up and reference a QMS process map. It is a programme, not proof that the
  scheduled audits happened, and its year is not automatically a validated period fact.

* `Internal-Audit-Report_Plant-2_Process-Controls.pdf` (`text_document`, `.pdf`) labels audit scope,
  criteria, process owners, findings, evidence and follow-up. Findings cover document control,
  training and production controls rather than one lot. This can activate the QMS template when its
  cross-process/system scope is explicit; a regulator inspection or an enterprise compliance audit
  has a different custody and control relation.

* `Management-Review-Minutes_Q2-2026.docx` (`text_document`, `.docx`) contains a management-review
  agenda and minutes, audit results, complaints, supplier performance, objectives, resource
  decisions and owned actions. It is system-level evidence. A calendar invitation, draft agenda or
  project status meeting does not establish completed review decisions.

### Metrics, competence and supplier quality

* `QMS-KPI-and-Complaint-Trends_Q2-2026.pptx` (`presentation`, `.pptx`) charts complaints,
  nonconformities, audit closure and on-time actions against quality objectives, then records
  systemic actions and management decisions. A chart alone could be a line dashboard or customer
  service report; the management-review and quality-objective context is the discriminator.

* `Quality-Training-and-Competence-Matrix.xlsx` (`spreadsheet`, `.xlsx`) maps controlled procedures
  and process roles to training status, revision taught, effectiveness checks and retraining needs
  across production, inspection and document-control roles. It supports QMS only with the controlled
  process/effectiveness relation. Names alone do not become a personnel or competence destination.

* `Supplier-Quality-Audit-and-System-Review_SUP-17.pdf` (`text_document`, `.pdf`) separates
  supplier-process findings from the organization's supplier-monitoring review, with QMS criteria,
  systemic actions and management escalation alongside supplier approval and scorecard sections.
  This is an intentional multi-perspective fixture: system-level trends may activate QMS while the
  supplier's capability and approval evidence activates `manufacturing.supplier-qualification`.

* `Quality-Procedure-Change-Approval.eml` (`email`, `.eml`) has a labelled subject identifying a
  controlled procedure revision, approver roles, effective-date coordination and redlined procedure
  and approval-form attachments. A request for approval is not an approval, and email source type
  does not establish QMS scope. Addresses and message content remain potentially sensitive.

### Calendar, archive, image and OCR paths

* `QMS-Management-Review.ics` (`calendar`, `.ics`) proposes a management-review meeting and includes
  organizer, attendees, location and recurrence metadata. It has no minutes, KPI pack or decisions.
  Calendar structure and an event title are never-alone evidence; this file may join a review group
  only after the minutes or system packet are accepted.

* `QMS-Release-2026-04.zip` (`archive`, `.zip`) has a manifest listing manual, controlled procedures,
  audit programme, review minutes, KPI deck and action register, including current and obsolete
  revisions. The archive is not unpacked. No one revision or review period is copied to the whole
  archive; each member retains its own evidence.

* `Signed-Audit-Checklist_Plant-2.jpg` (`image`, `.jpg`) shows a signed checklist with partial quality
  and process-control headings; camera EXIF exists, but plant and audit identifiers are not fully
  legible. A signature or image scene cannot establish system scope. It may be a Photos item and a
  sparse QMS group member, but absent EXIF would not prove screenshot origin.

* `Scanned-Quality-Manual_Rev9.pdf` (`ocr`, `.pdf`) yields OCR headings for quality policy and process
  map; signature and revision fields are partly legible, while scope and effective-date lines are
  unreadable. OCR provides possible evidence, not direct facts for unreadable values. If the system
  cannot establish current scope, Review Later is safer.

* `Plant-2-Control-Plan-and-Inspection-Results.xlsx` (`spreadsheet`, `.xlsx`) is a collision fixture:
  it has product, lot, characteristic, specification, measurement and disposition columns for one
  lot, but no system audit, document-control or management-review structure. Quality vocabulary does
  not make it QMS; it belongs to `manufacturing.inspection-record`.

The set covers labelled forms, unlabelled/ambiguous prose pathways, native text, spreadsheet and
presentation extractors, email, calendar, archive manifest, image, OCR and a concrete collision.
There is no meaningful contact-export role here. A `.vcf` is privacy-protected contact material, not
QMS evidence. Audio/video training or a code-structured portal export could join an accepted group,
but neither source type alone can activate the template.

## Recognition and abstention

Deterministic recognition uses structural clusters. A manual needs scope, responsibilities and
controlled-system sections; an audit needs scope/criteria/process/findings/follow-up; a management
review needs objectives, inputs, decisions and owners; a document register needs revision,
approval/effective and obsolete status. A QMS archive is identified from a manifest containing
several complementary members, not from a filename. A file can be system-level and cross-product
without exposing a folder path or asserting a field that R1c has not licensed.

The `needs_llm` entries are bounded interpretation cases: unlabeled quality culture prose, unclear
procedure roles, ambiguous audit custody, KPI semantics, draft versus completed review, OCR-poor
forms and mixed archives. The model receives only the compact evidence packet after deterministic
signals and must cite evidence or return unknown. It cannot infer QMS from a parent folder or copy a
manual's scope to every procedure.

The `never_alone` entries block the common false positives: “quality”, “audit”, “ISO”, “procedure”,
“CAPA”, a part or lot number, a signature, a source type, a calendar event, a portal session or an
invoice. A government inspection, supplier audit, engineering requirement review, warehouse
exception log and business compliance engagement can all carry identical vocabulary. The relation
and custody roles decide; a token never does.

## Conditional dimensions and field restraint

`proposed_fields` is intentionally empty. No QMS-specific key such as `process_area`,
`quality_system`, `audit_cycle`, `review_period` or `procedure_owner` is minted. Those concepts are
either observations, values, or unresolved candidates for the global vocabulary. The anchor's
proposed `record_type`, `site` and `product` may be reused only after R1c adjudication.

If R1c licenses an appropriate scope key, the useful order is:

`site or organization scope -> quality-system process/area -> record_type`,

with a period dimension only for recurring audits, KPI packs and management reviews. Product or
batch_lot can be an optional branch for a product-specific quality plan, but a QMS manual should not
be forced under one product. Quality objectives, revision, approver, finding, score and personnel
values remain search/review evidence. The order is a recommendation rather than a filesystem path,
and the user can flatten or reverse it after seeing accepted groups.

## Reciprocal boundaries and collision fixtures

The JSON authors eight same-kind `collides_with` edges. Each is exactly `{domain, signal,
provenance}`; no bare string, `domain_id`, `id`, `target` or `why` key appears in a collision object.
Every signal explains both directions and names `SAME FIXTURE BYTES:` followed by a concrete file.
All are `provenance: inference`, since `00` does not name these QMS neighbours. R1c must reconcile
reciprocity; the target rows may not yet name this not-yet-landed node.

1. **Inspection record — `Plant-2-Control-Plan-and-Inspection-Results.xlsx`.** QMS owns any
   cross-process control-plan governance, audit and systemic review appendix; inspection owns the
   lot-specific characteristic/specification/measurement/disposition sheets. A limit or pass/fail
   cell alone supports neither.

2. **Nonconformance/CAPA — `NCR-2026-041-Systemic-Review-and-CAPA.pdf`.** QMS owns recurring finding
   trends, management escalation and system-level effectiveness; nonconformance-CAPA owns the one
   event's affected product/lot, containment, root cause, action and closure. An NCR number or
   corrective-action word alone supports neither.

3. **Work instruction — `QP-001-Document-Control-and-Line-Setup-Instruction.docx`.** QMS owns
   document-control and cross-process governance sections; work-instruction owns executable sequence,
   parameters, setup and operator checks for one line or operation. A revision or SOP label alone
   supports neither.

4. **Supplier qualification — `Supplier-Quality-Audit-and-System-Review_SUP-17.pdf`.** QMS owns
   cross-supplier trends, audit governance and management escalation; supplier qualification owns the
   individual supplier's capability, approval scope and status. A supplier name, score or certificate
   alone supports neither.

5. **Business compliance audit — `Integrated-Quality-and-Compliance-Audit-Report_Plant-2.pdf`.**
   QMS owns manufacturing process conformity, quality objectives and follow-up; business compliance
   owns enterprise scope, risk/control testing, remediation and assurance conclusions. “Audit” and a
   finding alone support neither.

6. **Business policy handbook — `Corporate-Quality-Policy-and-QMS-Manual_Rev12.pdf`.** QMS owns
   manufacturing process governance, objectives, audits and review; policy handbook owns enterprise
   policy hierarchy, broad employee obligations and approvals. “Policy” or a signature alone
   supports neither.

7. **Engineering requirements — `Product-Quality-Requirements-and-QMS-Control-Plan.pdf`.** QMS owns
   controlled process, auditability and records requirements; engineering owns technical product
   requirements, interfaces, acceptance criteria and verification traceability. A requirement id or
   acceptance criterion alone supports neither.

8. **Logistics warehouse operations — `Warehouse-Quality-Control-Procedure-and-Stock-Exception-Log.xlsx`.
   ** QMS owns system procedure governance, audit findings and systemic action; warehouse operations
   owns live stock, receipt, pick, bin, quarantine and movement rows. A warehouse name, quarantine
   word or quantity alone supports neither.

The collision edges are mutexes for the same evidence item, not a statement that a file cannot carry
two legitimate perspectives. A shared report can have QMS sections and business compliance sections
on disjoint evidence. `also_holds_with` remains empty because CONNECTION restricts that edge to
schema-to-schema relations, not templates.

## Intended coactivation for R1c (not authored as an edge)

R1c should consider coactivation where one file carries independently supported roles:

- `Supplier-Quality-Audit-and-System-Review_SUP-17.pdf` can carry QMS system trends and supplier-
  qualification approval/capability evidence.
- `Management-Review-Minutes_Q2-2026.docx` can carry QMS review decisions and business governance
  or meeting-record facts without copying QMS scope to attendees.
- `NCR-2026-041-Systemic-Review-and-CAPA.pdf` can carry the individual CAPA case and QMS systemic
  effectiveness review.
- `Plant-2-Control-Plan-and-Inspection-Results.xlsx` can carry inspection facts and, only if a
  separate appendix genuinely supports it, a QMS control-governance view.
- `QMS-KPI-and-Complaint-Trends_Q2-2026.pptx` can carry QMS metrics and business compliance or
  customer-account review facts when those sections are independently evidenced.
- `Signed-Audit-Checklist_Plant-2.jpg` can carry Photos capture facts while joining the QMS group as
  a checklist member; capture metadata does not create a QMS scope fact.

This is memo guidance for R1c, not an authored template `also_holds_with` edge. Group membership
never copies the manual's site, process, revision or period facts onto a sparse file.

## Neighbours considered but not edged

`business_operations.project-delivery` was considered for quality plans attached to a capital or
implementation project. Its project scope, milestones and deliverables are not the QMS system
relation; the engineering-requirements and work-instruction fixtures are sharper. It can coactivate
on a project quality plan without a general collision.

`business_operations.organizational-records` was considered for management minutes and registers,
but the sharper policy-handbook and compliance-audit boundaries cover the same evidence. A board or
corporate register does not become QMS without manufacturing quality controls.

`manufacturing.production-record` was considered for batch records that cite a procedure. A batch,
lot, operation and release structure is production; QMS owns the procedure governance or systemic
review only when those sections are independently present. The collision is better handled by
inspection and work-instruction edges.

`manufacturing.calibration-record` and `manufacturing.asset-register` were considered for calibration
and equipment-control procedures. A certificate or asset row is not a QMS system; QMS may govern the
procedure while calibration or asset-register facts remain separate. Their evidence is narrower and
does not need a broad collision edge here.

`manufacturing.safety-case` and `manufacturing.hse-incident` were considered for integrated QMS/HSE
manuals. A safety case or incident requires hazard, barrier, event and corrective-action structure;
QMS requires system governance. A shared integrated management review may coactivate, but this row
does not claim every HSE policy is QMS.

`engineering.stage-gate-review` was considered because review packs include approvals and actions.
Engineering stage gates control a technical/project lifecycle; QMS management review controls system
objectives, audits and quality performance. The engineering requirements fixture is the more direct
same-evidence boundary.

`logistics.shipment` and `logistics.customs-export` were considered because supplier, receipt and
traceability records may be quality inputs. Shipment custody, origin/destination and customs
declarations are logistics; QMS owns the controlled-system audit or systemic review that uses them.
The warehouse fixture is a more precise collision than generic shipment material.

`government.permit-licensing` and `government.environmental-regulation` were considered for
certification/surveillance audits. Government owns issuer-side licensing, regulatory inspection and
enforcement; this template owns the manufacturer's internal system evidence. Those are real role
boundaries, but the assigned neighbour set emphasizes engineering, logistics and business
operations; R1c can add a government edge if a reciprocal fixture is found.

## Residual routing and safety

The JSON routes six residual cases. A standalone manual, procedure, certificate, notice or audit
acknowledgement with durable purpose goes to Independent Records. An isolated certification
confirmation or quality-service receipt goes to Receipts and Confirmations. An ambiguous checklist,
KPI workbook, draft agenda, OCR scan or mixed packet goes to Review Later. An unreadable portal export
or protected archive goes to Unsupported or Encrypted. Audit findings, training matrices, supplier
weaknesses, complaint trends and management decisions may go to Protected Records when no safe
accepted QMS group exists. A lone signed checklist or plant image goes to One-Off Images. These are
residual homes, not hidden QMS categories.

## Proposed fields, refusal and NEEDS-JOSEPH

`proposed_fields` is `[]`; no canonical field is added or respelled. The row is not refused, but the
decision remains conditional. R1c should refuse it if real corpora show only isolated procedures,
one-off audits, generic quality invoices or product inspection records without system-wide scope,
cross-process governance or management review. The manufacturing anchor, narrower siblings and
residuals cover that evidence honestly.

NEEDS-JOSEPH items for this node:

- **NJ-QMS-1:** Should R1c license a neutral `record_type` plus `site`/`product` scope for QMS, or
  keep system scope metadata-only because one manual can govern several sites and products? A
  private `quality_system` or `process_area` key is not minted here.
- **NJ-QMS-2:** Should audit findings and management-review actions coactivate QMS with
  manufacturing.nonconformance-capa and business_operations.compliance-audit on disjoint evidence,
  or should user policy choose one accepted group when a report combines all roles?
- **NJ-QMS-3:** When one controlled procedure is both a QMS governance document and an executable
  work instruction, should P10 expose two independently evidenced views while preserving one
  version family, or require a single user-selected destination?

## Self-verification

Both target paths were absent before writing and remain the only paths edited for this assignment;
no commit was made. The JSON parses with `python3 -m json.tool`. It contains fourteen file examples,
all example and file-kind source types are members of the exact vocabulary in
`src/evidence_shape/vocabulary.py`, all eight collision domains resolve to roster endpoints, every
collision object has exactly `domain`, `signal`, `provenance`, and every signal contains both
directions plus `SAME FIXTURE BYTES`. `fields`, `proposed_fields`, `template.dimension_order` and
`also_holds_with` are empty as required for this placeholder template. Residuals use only the nine
named homes. The eight quoted design spans were checked verbatim after whitespace normalization. No
thresholds, handling classes, bare collision strings, fabricated design quotations, private field
keys or paths-as-facts were added.
