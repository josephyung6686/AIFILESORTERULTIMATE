# manufacturing.tooling-fixture — R1b lab notes

**Depth: J-DEPTH**

Date: 2026-08-27
Roster row: `kind: template` · `schema_id: manufacturing` · `launch: placeholder`
Legacy coverage: `tooling.moulds-fixtures` (ROW)

## Verdict

**Keep provisionally; do not refuse.** The row is about an enduring mould, die, jig, fixture,
checking gauge or similar manufacturing aid and its own lifecycle: design/build identity, product
interface, acceptance or tryout, maintenance, verification, custody, life limit and retirement.
It is not a generic *tool* keyword, a CAD-file bucket, a purchase folder or an equipment register.

The strongest charge is that the `manufacturing` schema already covers production, inspection,
calibration, maintenance and asset records. That charge would win if this row only enumerated moulds,
dies and fixtures as work-type values. It survives narrowly because a tooling dossier keeps one
enduring tool asset together while crossing several manufacturing functions: a tool tryout, repair,
dimensional check and retirement decision can all concern the same tool even when no product lot is
being made. The schema default's product → batch/lot branch cannot make an enduring fixture's own
history intelligible, and its generic asset branch does not by itself distinguish a tool from the
machine that uses it. R1c should refuse if those relations are judged adequately covered by the
default or by `manufacturing.asset-register` plus maintenance/calibration templates.

No field is authored. D1/PR-6 leave the manufacturing schema's proposed `product`, `site`,
`batch_lot`, `asset`, `quality_event` and `record_type` undecided; this template does not copy or
mint them. No executable dimensions are written and no template-level `also_holds_with` edge is
authored. Intended coactivation is stated for R1c below.

## Authority stack and method

Repository material read:

- `planning/domains/dispatch/RESEARCH-BRIEF.md`, including the full J-DEPTH requirement.
- Complete stamped output of `python3 planning/domains/dispatch/make_prompt.py manufacturing.tooling-fixture`.
- `planning/prompts/ALIGNMENT.md` and authoritative `planning/00-database-agent-product-design.md`.
- `planning/domains/_CONTRACT.md`, `planning/domains/CONNECTION.md` and
  `planning/domains/CONNECTION-EXAMPLES.md` for node tests, evidence/fact separation, grouping,
  residuals and edge rules.
- `planning/domains/roster.json`, `planning/domains/ROSTER.md`,
  `planning/domains/canonical_fields.json`, and `src/evidence_shape/vocabulary.py`.
- `planning/overnight/council/DECISION-BRIEF.md` for D1–D6, J-IND and J-DEPTH.
- Manufacturing schema anchor `manufacturing.json` and its memo; it is the source of the broad
  product/batch/asset/quality grammar, not permission to add private fields here.
- Landed-depth exemplar `identity.core-documents.json` and `.research.md` for abstention, privacy,
  archive and observation/fact idiom.
- Existing same-kind boundaries: `engineering.cad-model`, `engineering.drawing-package`,
  `logistics.shipment`, `business_operations.procurement-sourcing`,
  `manufacturing.asset-register`, `manufacturing.maintenance-work-order`, and
  `manufacturing.calibration-record`. None was edited.

External sources validate recurring tooling and metrology artefacts only. They do not license
catalogue fields, form-number regexes, standards compliance, supplier identity or acceptance:

- [Autodesk, Tooling and Mold Design](https://images.autodesk.com/adsk/files/invtooling10_detail__bro_us.pdf)
  confirms mould/tool design as a distinct design activity involving material and process
  information. A design brochure is not evidence that a physical mould was built or accepted.
- [Autodesk, Current Mold Construction and Mold Tuning Process](https://static-au-uw2-stg.autodesk.com/MA4986-P_v1_ma4986-p_okonski.pdf)
  names milestones such as supplier award, tool-shop onboarding, steel cut, production-machine
  mould trial and tooling complete. This grounds build/tryout fixtures without importing a vendor's
  workflow as a product rule.
- [AIAG CQI-15 errata](https://www-clyde.aiag.org/docs/default-source/training-and-resources/errata-documents/cqi-15-2nd-errata-nov2022.pdf)
  names part-touching details, locating pins, fixture locators and tooling mating surfaces in a
  special-process context. It supports fixture/interface evidence, not a universal detector.
- [ISO 17662:2016](https://www.iso.org/cms/live/live/en/sites/isoorg/contents/data/standard/06/60/66052.html?browse=tc)
  describes calibration, verification and validation of equipment used to control process
  variables. It supports the boundary between a fixture/gauge calibration result and a generic
  product inspection, without asserting a jurisdiction or acceptance threshold.
- [ISO 10791-7:2020](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso%3A10791%3A-7%3Aed-3%3Av1%3Aen)
  identifies test conditions, tooling and recorded test information for machining centres. It is a
  useful false-positive source: machine test-piece tooling may be engineering/test evidence rather
  than a reusable production fixture lifecycle.

## J-DEPTH node test — all three legs

### Leg 1 — detection differs from the manufacturing default

The manufacturing schema default recognizes a repeatable transformation or control cycle tied to
a product, batch/lot, production site/line, controlled asset or quality event. It can therefore
recognize production travellers, inspection reports, maintenance work orders and calibration
certificates. A tooling row that only adds *mould* as a value is not a node.

This row requires the **tool as the measured or controlled subject** and a lifecycle relation. A
positive record identifies a tool asset and connects it to at least one of: a product interface and
build/tryout disposition; tool-specific wear/repair and return-to-use; tool geometry verification;
calibration of a checking gauge; custody/storage/life-limit state; or an implemented change and
release. The machine that houses the tool, the article measured by a fixture, and the supplier who
built it are distinct roles. A CAD model, purchase order, carrier manifest or generic machine work
order does not activate this row without that own-tool relation.

### Leg 2 — recommended dimensions differ from the default

The schema anchor's ordinary production branch is product → batch/lot → record type, while its
maintenance alternative uses site → asset → record type. Tooling history needs the enduring tool
asset as the parent: condition, tryout, repair, verification and retirement are unintelligible if
scattered under each product lot. Conditional on R1c promoting schema proposals, the useful order is
**site → tool asset → product interface (optional) → record type**. For a one-site or one-tool corpus,
site and product are flattened. A multi-row tool register has no single asset value and belongs to
the asset-register situation instead. Dates, cycle counts, cavity numbers, dimensions and supplier
names remain evidence/search values, not default folder levels.

`dimension_order` is therefore empty in JSON. This is a placeholder and does not create `tool_id`,
`mould_id`, `fixture_type` or `tool_status` proposals. It is not time-first: the exact applicable
design sentence is, “For document and record domains, project, function, or subject usually comes
before time because putting year first scatters related work across calendar folders.” A tool's
previous build, current repair and next inspection should remain discoverable together.

### Leg 3 — privacy and commercial exposure differ from the default

Manufacturing records already can expose product and production information. Tooling adds the
physical means of production: proprietary cavity or datum geometry, tool materials and inserts,
product interfaces, cycle/life counts, supplier terms, plant or storage location, maintenance
condition, release readiness and engineering-change details. A leaked tool dossier can reveal how a
product is made even when no finished-product lot is present. The node is consequently
`potentially_sensitive`; P7 owns handling classes and the local/cloud decision.

Custody is ambiguous in exactly the files most likely to be shared. The same byte-identical
`Tooling-Purchase-Order_PO-7714.pdf`, `Tooling-Shipping-Manifest_T-2048.pdf`, or
`Mold-M06_Build-and-Tryout-Report.pdf` may sit with a manufacturer, supplier, carrier or customer.
Grouping can retrieve a bounded packet but cannot copy the tool asset, product or acceptance fact
from one member to another.

### Node-test conclusion

Keep only as the narrow tool-asset lifecycle template. R1c should refuse if all positive files are
already ordinary asset-register, maintenance, calibration, inspection or engineering records and
there is no recurring need to retrieve a tool's cross-functional life history. The legacy row does
not justify retaining it by itself.

## Bottom-up file corpus

The JSON carries thirteen concrete fixtures, each splitting observations from legal facts. Since the
manufacturing schema is field-less, positive files list universal facts only; tool, product, site,
revision and lifecycle conclusions remain observations or R1c proposals.

1. **`Tool-Register_Press-07.xlsx`** (`spreadsheet`) — a multi-row tool-room population pairing
   identifiers with type, product interface, storage, custodian, due dates and lifecycle states.
   No single tool value may be copied from the register to every member.
2. **`Mold-M06_Build-and-Tryout-Report.pdf`** (`text_document`) — mould identity, product/cavity
   interface, build checklist, trial conditions and release disposition. A tool-maker signature is
   not proof of acceptance or future lot conformity.
3. **`Fixture-F12_Datum-Verification.csv`** (`spreadsheet`) — fixture identity, datum points,
   nominal/tolerance, measured result, instrument and disposition. It checks the tool interface,
   not the unrelated product's production release.
4. **`Tooling-Maintenance-Work-Order_T-2048.pdf`** (`text_document`) — tool condition/wear,
   replaced inserts, performed work, post-work inspection and return-to-use status. The production
   machine is a using asset, not automatically the maintained subject.
5. **`Checking-Gauge-G07_Calibration-Certificate.pdf`** (`text_document`) — gauge identity,
   reference standard, as-found/as-left results, traceability and due state. This can also activate
   the calibration sibling; calibration is not silently rewritten as product inspection.
6. **`Tool-Change-Notice_T-2048_Rev-C.pdf`** (`text_document`) — controlled tool revision,
   affected product interface, modification, post-change measurements, tryout and release. A
   revised CAD file alone does not prove implementation.
7. **`Toolroom-Photo_T-2048.jpg`** (`image`) — camera facts plus a tool cart and partial tag, with
   no own acceptance or product-use evidence. It can join a tool group without gaining a tool fact.
8. **`Tool-Tag-Scan_T-2048.png`** (`ocr`) — OCR of a cropped metal tag, but no product/site/life
   relation. A serial-like token is insufficient and absent EXIF is not screenshot proof.
9. **`Tooling-Handover_T-2048.eml`** (`email`) — native mail fields and body/manifest describing
   condition, receiving custodian, product use and acceptance checks. Transmission is not delivery
   or acceptance, and an attachment's facts remain separate until extracted.
10. **`Tooling-Life-History_T-2048.zip`** (`archive`) — manifest of tool card, CAD, build, tryout,
    maintenance, inspection and retirement members, plus supplier/carrier records. It is inspected
    without unpacking and cannot donate one member's facts to all others.
11. **`Tooling-Shipping-Manifest_T-2048.pdf`** (`text_document`) — crate, carrier, origin,
    destination, seal and tracking fields citing a tool. It is post-dispatch Logistics evidence
    unless the same bytes are joined to condition and receiving acceptance.
12. **`Tooling-Purchase-Order_PO-7714.pdf`** (`text_document`) — supplier, tool description,
    price, delivery and terms. It proves a procurement transaction, not physical existence,
    acceptance or tryout.
13. **`Press-07_Mold-Mounting-Drawing_Rev-B.dwg`** (`design_creative`) — controlled geometry,
    interface, datum and revision. It is the Engineering collision fixture until physical build,
    tryout or maintenance evidence joins it to this row.

The set covers labelled forms, structured tables, unlabelled/cropped OCR, screenshots and camera
images, email, calendar-like planning boundaries, archives, CAD, custody transfer, supplier
procurement, metrology and sparse group members. A calendar booking such as
`Mould-Trial_T-2048.ics` would remain a planned event unless a completed result is attached; this
is covered by the JSON recognition and rejection rules without adding a fourteenth duplicate fixture.

## Collisions and reciprocal boundaries

Each JSON collision has exactly `{domain, signal, provenance}`. Each signal names the same fixture
bytes and explains both directions; R1c must land reciprocal edges or remove the pair:

- **`engineering.cad-model` — SAME FIXTURE BYTES:** `Press-07_Mold-Mounting-Drawing_Rev-B.dwg`.
  Manufacturing wins when the drawing is evidence in an accepted physical tool lifecycle;
  Engineering wins when it is the controlled geometric definition under design revision. CAD alone
  does not prove a physical tool.
- **`engineering.drawing-package` — SAME FIXTURE BYTES:** `Tool-Change-Notice_T-2048_Rev-C.pdf`.
  Manufacturing wins for implemented modification, tryout and release; Engineering wins for an
  intended design-change package without execution or custody evidence.
- **`logistics.shipment` — SAME FIXTURE BYTES:** `Tooling-Shipping-Manifest_T-2048.pdf`.
  Manufacturing wins for tool condition, receiving acceptance and life history; Logistics wins for
  crate, carrier, seal, destination and movement. Tracking is not acceptance.
- **`business_operations.procurement-sourcing` — SAME FIXTURE BYTES:**
  `Tooling-Purchase-Order_PO-7714.pdf`. Manufacturing wins only when the order is retained as
  evidence in an accepted tool lifecycle; Business Operations wins for sourcing, award and purchase
  transaction. A line item is not a physical tool.
- **`manufacturing.asset-register` — SAME FIXTURE BYTES:** `Tool-Register_Press-07.xlsx`.
  This row wins for one-tool lifecycle semantics; asset-register wins for a multi-asset population
  whose rows have no single document subject. A repeated tag does not decide ownership.
- **`manufacturing.maintenance-work-order` — SAME FIXTURE BYTES:**
  `Tooling-Maintenance-Work-Order_T-2048.pdf`. This row wins when the work is retained in a
  tool-specific lifecycle with wear, inserts, tryout or life-limit context; maintenance-work-order
  wins for the generic performed-maintenance transaction on any production asset.
- **`manufacturing.calibration-record` — SAME FIXTURE BYTES:**
  `Checking-Gauge-G07_Calibration-Certificate.pdf`. This row wins for the checking fixture's
  enduring use and lifecycle; calibration-record wins when the measured object and traceability
  chain are the instrument's calibration result.

## Neighbours considered but not edged

- **Engineering schema generally** — considered because tools have drawings, datum schemes and
  controlled revisions. The two specific Engineering templates capture CAD/design custody; a broad
  schema edge would incorrectly mutex every tool maintenance or tryout record.
- **Logistics schema generally** — considered because tool build, transfer and return involve crates
  and carriers. `logistics.shipment` is the sharper post-dispatch boundary; generic movement is not
  a tooling collision when a tool lifecycle relation is present.
- **Business Operations schema generally** — considered because tool procurement, supplier terms
  and approvals can be retained by a company. `business_operations.procurement-sourcing` is the
  specific purchase boundary; vendor management was not edged because no supplier-qualification
  fixture is needed to identify this row.
- **`manufacturing.inspection-record`** — considered because fixtures and gauges appear in product
  inspection. A product characteristic/result record is not a tool life record unless the document's
  measured object is the fixture itself; the checking-gauge collision is sharper.
- **`manufacturing.production-record`** — considered because mould trials produce samples. Trial
  disposition is tooling evidence only when it governs tool release; ordinary product production
  remains the production template.
- **`manufacturing.spare-parts`** — considered because inserts and wear parts occur in tool repair.
  A stock population or purchase line is not a tool asset; no direct shared fixture was needed.
- **`manufacturing.environmental-compliance`** — considered because mould materials and shop-floor
  chemicals can appear in records. No environmental fixture shares the same tool-life evidence.

## Files considered and rejected from activation

- **Standalone CAD, STEP or drawing file** — Engineering controlled definition; no physical build,
  acceptance or use is evidenced.
- **Purchase order, quote, invoice or supplier email** — procurement evidence until an accepted
  tool lifecycle and tool-specific disposition are independently visible.
- **Carrier manifest, delivery proof or customs packet** — Logistics movement/custody; tool identity
  does not make transport a manufacturing lifecycle event.
- **Machine maintenance work order** — maintenance of the press, CNC or production line is not
  maintenance of the mould, die or fixture it uses.
- **Product inspection report using a fixture** — Manufacturing inspection; the fixture is an
  instrument/equipment observation, not the report's controlled subject.
- **Calibration certificate for a general instrument** — Calibration sibling unless the certificate's
  object is a checking fixture and the file is retained in its tool lifecycle.
- **Toolroom inventory or multi-asset register** — `manufacturing.asset-register`; no single tool
  fact may be copied from one row to the document or to neighbouring files.
- **Calendar trial booking** — planned event only; it cannot establish a completed tool tryout.
- **Photograph of a mould, die or tool tag** — Photos or Review Later unless the image's own
  evidence includes a labelled lifecycle submission; camera metadata never proves acceptance.
- **Generic document named Tooling, Moulds or Fixtures** — filename is a clue only; unreadable or
  contradictory content falls through to Review Later or Unsupported/Encrypted.

## Intended coactivation for R1c (not authored in JSON)

The template deliberately leaves `also_holds_with` empty. A supplier-built tool packet may support
Engineering (controlled geometry), Business Operations (procurement), Logistics (shipment/custody),
and Manufacturing (accepted tool lifecycle) on the same bytes or on independently extracted
members. R1c should decide whether P9 grouping and per-file `also_schema` observations are enough, or
whether a future schema-level relationship is warranted. A shared tool number, supplier name or
product name is not sufficient; the second schema needs its own role-bearing evidence.

## NEEDS-JOSEPH

1. **NJ-MFG-TOOL-1 — field identity and dimensions.** Should this row reuse manufacturing's proposed
   `asset`, `product`, `site` and `record_type`, with tool identity as an asset value, or is a neutral
   tool/product-interface role required across schemas? The useful projection is site → tool asset →
   optional product interface → record type, but PR-6 prevents local field decisions.
2. **NJ-MFG-TOOL-2 — register versus lifecycle ownership.** When a multi-row tool register also
   includes maintenance due dates and status, should `manufacturing.asset-register` own it while a
   single-tool history belongs here? The selector must use row-population versus one-tool subject
   evidence and must not copy a selected row's facts to the register.
3. **NJ-MFG-TOOL-3 — mixed supplier packet.** When CAD, purchase, shipment, handover and tryout bytes
   are held by different parties, should P9 represent coactivation across Engineering, Business
   Operations, Logistics and Manufacturing, or should one custody owner be selected? This template
   authors no `also_holds_with` edge.
4. **NJ-MFG-TOOL-4 — calibration and inspection seam.** Should a checking fixture's calibration
   certificate activate both this row and `manufacturing.calibration-record`, or should the measured
   object determine one mutex template? The same fixture bytes and role-bearing evidence must be
   reviewed before automatic placement.
5. **NJ-MFG-TOOL-5 — validation catalogues.** R2/R4 must settle deployment-specific tool-tag,
   part-number, revision, cavity and supplier identifiers. No regex, supplier list, standard number,
   acceptance threshold or jurisdictional rule is asserted here.

## Self-verification

- Both assigned paths were absent before authoring and are the only paths added by this task.
- JSON parses with `python3 -m json.tool` after authoring.
- Every fixture source type is in the exact fourteen-member `SOURCE_TYPES` vocabulary.
- `fields`, `proposed_fields` and `template.dimension_order` are empty under PR-6; no local field is
  minted.
- Every collision is exactly `{domain, signal, provenance}`; every signal names `SAME FIXTURE BYTES`
  and explains both directions.
- `also_holds_with` has no entries; intended coactivation is recorded here for R1c only.
- Collision endpoints are roster-valid and residual destinations use the named residual library.
- The two quoted design sentences were checked byte-for-byte against `00`; no fabricated quote is
  used.
- Final scoped whitespace/diff and repository-status checks are required before handoff.
