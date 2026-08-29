# Research memo — `manufacturing.nonconformance-capa`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/manufacturing.nonconformance-capa.json`
Roster row: placeholder template on the fieldless `manufacturing` schema

## Result

Accept the node on two legs of the template node test. The schema anchor already contains NCR and
CAPA vocabulary, so the row cannot survive merely because those are document types. It survives
because one controlled quality event creates a bounded lifecycle across otherwise heterogeneous
files, and because that event must be the parent context: initial report, containment, disposition,
investigation, action and effectiveness evidence become unintelligible when scattered under product,
supplier, asset or calendar branches.

The row writes `fields: []`, `proposed_fields: []`, `dimension_order: []`, and
`also_holds_with: []`. The last point is deliberate: for this template row,
`also_holds_with` would incorrectly express schema-to-schema record-template intent. Files can carry
manufacturing plus engineering, operations, logistics or photos facts, but the template memo records
those possibilities through file fixtures and collisions rather than writing an applicability edge.

## Authority and sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md`, read completely.
- The stamped output of `make_prompt.py manufacturing.nonconformance-capa`.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/CONNECTION.md`,
  `CONNECTION-EXAMPLES.md`, and `_CONTRACT.md`.
- `planning/00-database-agent-product-design.md`, with quotations avoided except where mechanically
  verified. The JSON relies on argued inference rather than paraphrase presented as quotation.
- `planning/01-product-design-structured.md` as a locator only; `00` remains authoritative.
- `planning/domains/canonical_fields.json`, `planning/domains/roster.json`, and
  `src/evidence_shape/vocabulary.py` for legal keys, ids and source types.
- `planning/domains/nodes/manufacturing.json`, the actual schema default against which the node test
  is argued.
- `manufacturing.inspection-record`, `manufacturing.calibration-record`,
  `manufacturing.maintenance-work-order`, `manufacturing.supplier-qualification`, and relevant
  engineering research memos for already-landed reciprocal boundaries.
- `identity.core-documents` solely as the required three-key edge-shape exemplar.

## The refusal charge, argued before acceptance

The strongest case for refusal is that the manufacturing anchor already does almost everything this
row claims. Its recognition list explicitly describes a nonconformance form and a corrective-action
form. Its `work_types` already include nonconformance, deviation, complaint investigation, corrective
action and preventive action. Its prose template already names a quality-event branch. On a shallow
reading, this row is just a `record_type` value, and retaining it would recreate the old catalogue's
document-type taxonomy.

The charge is defeated narrowly, not rhetorically.

First, the anchor's signals recognize individual forms. This row's subject is the **continuity of one
controlled case**: a requirement-versus-observed departure leads to containment or disposition,
investigation and accountable action, then later effectiveness evidence. The controlled identifier
and role changes across the lifecycle distinguish it from a folder of unrelated NCR forms and from a
generic action tracker. A reject measurement proves only that a characteristic failed. It does not
prove that anyone opened a controlled case, quarantined material, assigned root cause, changed a
system or verified recurrence.

Second, the anchor has several competing defaults: product/lot for production evidence, site/asset
for maintenance, and quality event for NCR/CAPA. This row makes the last one binding as its
recommendation. One event may implicate a supplied part, a produced lot, an instrument and a work
instruction. Putting any of those first splits the case precisely where retrieval needs it together.
The event is not merely a leaf document type; it is the context without which `effectiveness
review.docx` has no intelligible referent.

Privacy does not differ materially. Product weaknesses, customer complaints, supplier performance
and named personnel are potentially sensitive, but the manufacturing anchor already says so. The row
does not use privacy to rescue itself.

## Bottom-up file census

Ten concrete fixtures were researched, including false positives and sparse evidence.

1. `NCR-2026-041 cracked housing.pdf` is the canonical positive. Labelled event, affected article,
   requirement, observed condition, containment and disposition appear together. The title cannot
   supply root cause, and an unread checkbox cannot supply approval.
2. `CAPA-2026-012 effectiveness review.docx` is a late-lifecycle positive. Its exact CAPA reference,
   implementation evidence, recurrence review and closure authority matter; the filename does not
   prove closure.
3. `SCAR-2026-018_Vertex_late-plating-adhesion.pdf` is outward-facing supplier evidence. It remains
   this row when it is a controlled request/response/acceptance case, but the supplier name does not
   become qualification status and the return movement does not become the event.
4. `NCR-2026-041 containment photos.zip` is a bounded packet. The manifest can connect candidate
   members, but unread photographs inherit no product, lot or quality-event fact.
5. `IMG_9042.jpg` is the collision fixture for sparse images: it visibly shows a crack and has real
   EXIF, yet contains no requirement, article identity or case link. It falls to One-Off Images and
   may later join a case without copied facts.
6. `LOT-24-081_Final-Inspection.xlsx` is inspection, not CAPA. Its measured values, stated limits and
   REJECT verdicts make an inspection record. Absence of a controlled event lifecycle is not itself
   proof, but no positive CAPA evidence exists.
7. `WO-8814 CNC-07 spindle alarm.xml` is maintenance. Asset, work performed, parts and returned-to-
   service evidence describe repair. A separately labelled systemic corrective-action case would be
   additional evidence; repair completion alone is not one.
8. `ECR-2026-077 permanently widen coating tolerance.pdf` is engineering change. It alters the
   released definition. The cited NCR remains the occurrence under the former definition, and its
   identifier is not copied onto the ECR as a manufacturing fact.
9. `Actions.xlsx` is the hardest generic false positive. Owner, due date and status columns are
   common operational structure. With no controlled event, departure, containment, disposition or
   effectiveness role, it routes to Review Later rather than activating CAPA.
10. `Out-of-tolerance impact assessment - LC-1142.pdf` belongs to calibration unless a separately
    opened controlled quality event appears. Instrument recall and product-impact review can link
    records without converting the assessment into an NCR.

The list covers labelled forms, prose, spreadsheet, image, archive, structured export and the email
case in recognition. A calendar reminder may join a case as a sparse candidate but can never activate
it from title and date. Opaque QMS exports are plausible file kinds only; without an inspectable
manifest they fall to Unsupported or Encrypted rather than being trusted by extension.

## Reciprocal boundaries and edge discipline

Every authored `collides_with` item is exactly `{domain, signal, provenance}`. Each signal explicitly
names **SAME FIXTURE BOTH SIDES** because P6 activation step 3 and P8's validator must be able to read
the discriminator and assign an evidence item to the correct side.

- Inspection versus CAPA uses `LOT-24-081_Final-Inspection.xlsx` and
  `NCR-2026-041 cracked housing.pdf`. Limit/actual/verdict is inspection evidence; controlled event,
  containment, investigation and closure is CAPA evidence. A REJECT row is not silently promoted.
- Calibration versus CAPA uses `Out-of-tolerance impact assessment - LC-1142.pdf`. Instrument,
  as-found/as-left, interval and recall chain count toward calibration. A distinct event plus
  containment/action/effectiveness counts toward CAPA.
- Maintenance versus CAPA uses `WO-8814 CNC-07 spindle alarm.xml`. Repairing the asset and restoring
  service is maintenance; changing the system to prevent recurrence under a controlled event is CAPA.
- Engineering change versus CAPA uses the ECR fixture. Changing the released definition belongs to
  engineering; controlling the occurrence before that definition changes belongs here.
- Business operations versus CAPA uses `Actions.xlsx` and the effectiveness review. Generic task
  governance is operations; the controlled quality lifecycle is this row.
- Logistics versus CAPA uses the supplier corrective-action fixture. Shipment/receipt/return custody
  counts toward logistics; defect, containment, response and accepted action count here.

These are mutex boundaries over evidence roles, not claims that two schemas can never both activate.
The same file may have distinct evidence for both schemas, but each observation must still be counted
on the side its role supports.

## Fields and dimension recommendation

No fields are proposed. The manufacturing anchor already proposes `quality_event`, `product`,
`batch_lot`, `asset`, `site`, and reuse of `record_type`; duplicating them here would violate the
template contract. The only unresolved field question is whether `quality_event` is too private a
name for semantics shared by complaints, incidents and investigations. That belongs to R1c.

`dimension_order` stays empty because the schema is placeholder and licenses no canonical field.
The prose recommendation is event first, then record function or lifecycle stage. Product, lot,
asset, supplier and time are retrieval facets. Time-first is specifically harmful: an initial report
in one quarter and effectiveness review in another are still one case.

## Files considered and rejected

- A blank `QF-044 Nonconformance Report Rev 6.docx` is a controlled QMS template, not an occurrence;
  it belongs to `manufacturing.quality-management-system` because there is no event value or executed
  evidence.
- `Root Cause Analysis Training.pptx` teaches five-whys and fishbone methods. Method vocabulary alone
  is never a case and the deck belongs with training or Independent Records.
- `Customer return RMA-66192.pdf` records authorization and custody. Without requirement departure,
  investigation or controlled action it is logistics/transactional evidence.
- `Vendor-Scorecard_Vertex_2026-Q2.xlsx` aggregates standing performance. One defect count or late-
  delivery rate is not a SCAR; supplier qualification/vendor management owns the relationship view.
- `PFMEA_AX410_RevC.xlsx` anticipates failure modes and controls before an occurrence. A row with a
  risk score is engineering risk analysis, not evidence that the failure happened.
- `8D template blank.docx` is a form definition. An executed 8D tied to an exact event can be this
  row; the empty template is QMS evidence.
- `Invoice - rework lot L240817-03.pdf` proves a transaction. The lot token and word rework do not
  establish who authorized disposition or whether a case existed.

## Neighbours considered without an additional edge

- `manufacturing.supplier-qualification`: one SCAR can influence standing approval, but the
  already-landed supplier row records the outward-request versus internal-action seam. A second edge
  here would add another claimant to the same bytes; the file fixture and business/logistics edges
  already preserve the distinction.
- `manufacturing.failure-analysis`: a deep technical analysis can support root cause, but failure
  analysis is an evidentiary member, while this row is the controlled case. The distinction is
  membership rather than a mutex unless the catalogue later proves the same file is actively claimed
  as both templates.
- `manufacturing.quality-management-system`: blank procedures and forms versus executed events is a
  clear boundary, encoded in rejected fixtures and `never_alone`. No edge is added because the
  neighbouring row was not yet available to verify a reciprocal same-fixture claim.
- `engineering.risk-analysis-fmea`: prospective failure-mode analysis versus realized occurrence.
  An NCR may cite an FMEA action, but citation does not transfer the document.
- `photos`: a defect photograph genuinely carries photo facts and may also join the case. That is not
  a template collision, and `also_holds_with` is intentionally unavailable for this template row.

## NEEDS-JOSEPH

1. **NJ-NC-1 — event key scope.** Should `quality_event` remain manufacturing-specific, or should
   R1c canonicalize a broader case identifier shared by complaints, safety incidents and regulated
   investigations? Recommend the broader key if role splits prevent collisions; this row mints none.
2. **NJ-NC-2 — one CAPA, several NCRs.** Alternatives: merge source NCRs into one event, or retain
   immutable event groups linked to a parent CAPA action group. Recommend linked groups; merging loses
   provenance and makes closure ambiguous.
3. **NJ-NC-3 — calibration impact assessment.** Does impact review after an out-of-tolerance result
   activate CAPA without a separately opened case? Recommend no: calibration owns it until positive
   controlled-event evidence appears, with P9 linkage allowed meanwhile.

## Self-verification

- JSON parsed with `python3 -m json.tool`.
- Both output paths match the stamped assignment; no other file was edited.
- `fields` and `proposed_fields` are empty; the template does not duplicate schema proposals.
- All file-example source types are in the closed `SOURCE_TYPES` vocabulary.
- Every example separates observations from legal facts and forbids a folder path.
- Every collision edge has exactly `domain`, `signal`, and `provenance`; every signal names SAME
  FIXTURE BOTH SIDES and gives the evidence discriminator.
- `also_holds_with` is empty as required for this template row.
- Residuals use only named residual templates. No threshold, confidence score, handling class or
  fabricated quotation was introduced.
