# R1b lab notes — `resource_operations.oil-gas-operations`

Date: 2026-08-27
Assignment: `kind: template` · `schema_id: resource_operations` · `launch: placeholder`
Result: **keep, narrowly** (`refuse_node: false`), field-less and dimension-less pending R1c.

## Verdict and strongest charge

This row survives only as a **well/field operational-history template**, not as an oil-and-gas
industry label. Its anchor is a labelled relation among an operating authority, field/site, well or
facility, actual operational state or measured production, and reporting period. That relation is
visible in real well activity reports, end-of-operations/completion records, daily drilling logs,
well tests, production allocations and post-authorization monitoring returns.

The strongest charge is that this is merely a narrow value set inside the already broad
`resource_operations` schema default. That charge is serious: the parent schema already recognizes
authorized source/site → asset → measured output → period and proposes all six field keys this row
would use. The row survives because its recognition and recommended order differ materially:

- the schema default is source/output-led and conditionally recommends
  `site → operating_authority → output_stream → reporting_period → record_type`;
- this row is **well-history-led** and conditionally recommends
  `site/field → asset/well → reporting_period → record_type`, with authority optional above the
  well and production stream normally search/allocation evidence rather than a standing branch;
- the row's decisive file structures are actual well activity, actual completion state, well tests
  and production allocation, all of which distinguish planned design/permission from performed
  operation;
- precise wellbore, infrastructure and subsurface evidence creates a sharper privacy posture than
  the schema's generic operational default, even though the only legal catalogue value remains
  `potentially_sensitive`.

If R1c concludes that the schema default already captures those differences as values and an
asset-led optional branch, this row should be refused. That alternative is explicit in
NJ-OILGAS-1; keeping the legacy id is not itself evidence.

## Authority stack and method

Repository authorities read:

- `planning/domains/dispatch/RESEARCH-BRIEF.md` in full, including the ratified J-DEPTH override.
- The complete stamped output of
  `python3 planning/domains/dispatch/make_prompt.py resource_operations.oil-gas-operations`.
- `planning/00-database-agent-product-design.md`, authoritative for every product-design quote.
- `planning/01-product-design-structured.md`, used as a locator only; `00` wins.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`,
  `planning/domains/CONNECTION.md`, and all eight fixtures in
  `planning/domains/CONNECTION-EXAMPLES.md`.
- `planning/domains/canonical_fields.json`, `planning/domains/roster.json`, `ROSTER.md` §4 and
  Appendix A, and `src/evidence_shape/vocabulary.py`.
- `planning/overnight/council/DECISION-BRIEF.md`, including ratified D1–D6, J-IND and J-DEPTH.
- The landed `resource_operations` schema JSON and research memo, read in full. Its six proposed
  keys, node-test argument and operator/government boundary are inherited research, not silently
  reinvented.
- The landed launch-depth exemplar `identity.core-documents` JSON and research memo for structure,
  observation/fact discipline, false-positive analysis and open-question depth.
- Existing same-kind neighbour files and memos for `engineering.drawing-package`,
  `government.permit-licensing`, `government.environmental-regulation`,
  `business_operations.corporate-regulatory-filings`, and
  `business_operations.compliance-audit`. No neighbour was edited.

The stamped prompt's “gist” wording conflicts with the newer J-DEPTH ratification and standing
brief, so it was not followed. The CONNECTION §5 rule also overrides the stamped output example:
template rows do not author template-level `also_holds_with`.

## External evidence used

These sources establish **real document names and recurring slot structures**. They do not license
product fields, jurisdiction-specific detectors, identifier regexes, thresholds, legal conclusions,
authenticity judgments or handling classes.

- The [BSEE forms catalogue](https://www.bsee.gov/about-bsee/doing-business-with-bsee) names, among
  its drilling/operational forms, Application for Permit to Drill, Application for Permit to Modify,
  End of Operations Report, Well Activity Report, Open Hole Data Report, Facility/Equipment Damage
  Report and Rig Movement Notification Report. It separately names Well Potential Test Report and
  Semiannual Well Test Report under production. These names ground the file set; a form title never
  activates alone.
- BSEE's [eWell End of Operations Report query](https://www.data.bsee.gov/Well/eWellEOR/Default.aspx)
  exposes real EOR records keyed by lease/well/company/status data, supporting the recurring
  well-identity and final-state relation without implying that a downloaded record is current.
- BSEE's [OGOR-A production data](https://www.data.bsee.gov/main/ogor-a.aspx?op=Search) identifies
  Oil and Gas Operations Report Part A as well-production information and provides record-layout
  downloads. This supports the production-allocation fixture and its separation from an invoice or
  market table.
- The [BSEE production information page](https://www.data.bsee.gov/Main/Production.aspx) describes
  production files by lease, well/API number or operator and distinguishes well, lease and product
  sales/inventory reports. This supports separate measurement/allocation roles, not a detector term
  list.
- The [Bureau of Land Management forms catalogue](https://www.blm.gov/services/electronic-forms)
  names Application for Permit to Drill or Reenter, Well Completion or Re-completion Report and Log,
  and Sundry Notices and Reports on Wells. The same organizational relation therefore appears in a
  second official system; this row does not hard-code either system's form numbers.
- The NSTA's [onshore well-operations guidance](https://www.nstauthority.co.uk/regulatory-information/exploration-and-production/onshore/well-operations/)
  describes WONS applications/consents, activity/completion notifications, shut-in/reopening
  notifications, well tests and monthly oil/gas/water production reporting. It supports the
  planned-versus-actual and notification-versus-proof boundaries.
- The NSTA [UKCS Well Applications and Consents Guidance](https://www.nstauthority.co.uk/media/4hejqh5s/nsta-wons-guide-2026.pdf)
  explains that post-activity WONS notifications report actual information such as actual total
  depth and require a wellbore update with well results and acquired data. This is direct support
  for treating actual-state structure as distinct from a permit application.
- The NSTA/data.gov.uk [PPRS field production dataset](https://www.data.gov.uk/dataset/e2c7af85-8b52-4ecc-ab8d-c4f0639d5459/ukcs-hydrocarbon-field-production-reports-pprs-points-wgs84)
  identifies field/terminal production reporting and its reporting-unit structure. It supports a
  field/period/output relation and demonstrates why one jurisdiction's names are values, not new
  field keys.

No external source is quoted as product design. All JSON recognition and collision claims have
`inference` or `proposal` provenance.

## Bottom-up file set

The JSON contains fourteen concrete files. The first ten are positive or collision-bearing
operational fixtures; the last four exercise sparse, cross-schema and false-positive behavior.

1. **`BSEE-0133_WAR_OCS-G-12345_A-17_2026-W32.pdf`** (`text_document`). The title and labelled
   slots join lease, well/API, operator, rig, interval, well status, depths, operation summary and
   casing/log progress. The form title or API-shaped token alone does not fire. Legal now: universal
   fields only. It cannot establish approval, safety, correctness or a folder path.

2. **`BSEE-0125_EOR_OCS-G-12345_A-17.pdf`** (`text_document`). Actual start/end/final state and an
   attachment list for casing, cement, completion, logs and surveys distinguish it from a planned
   programme. Signature is evidence of a slot, not truth. Facts from one attachment are not copied
   to every member.

3. **`Daily-Drilling-Report_BR-17_2026-08-21.xlsx`** (`spreadsheet`). Repeated time rows join well,
   rig, actual operation, depth/progress, non-productive-time reason, fluid/pressure observations and
   current state. “Daily,” one date and a well-shaped token are never-alone evidence. An operation
   narrative is not independently verified merely because it occupies a table.

4. **`OGOR-A_Well-Production_OCS-G-12345_2026-06.csv`** (`spreadsheet`). Lease/well, production
   month, operator, oil/gas/water roles and status/disposition make this a production record. It is
   not an invoice, tax calculation, cargo ledger or market table. The same bytes become a collision
   with corporate regulatory filing when a submission wrapper is present.

5. **`BR-17_Production-Allocation_2026-06.xlsx`** (`spreadsheet`). Well test/meter values reconcile
   to facility and field totals with measured, allocated, fuel, flare, inventory and adjustment
   roles. A quantity column proves nothing alone; the linked roles are the evidence. Arithmetic
   equality does not prove physical accuracy.

6. **`BSEE-0123_APD_OCS-G-12345_A-17_Approved-with-Conditions.pdf`** (`text_document`). This is the
   hardest permit fixture. It has a proposed well, approval block and conditions, but no proof that
   drilling commenced. It remains Independent Records unless the same well reference is independently
   joined to actual activity/completion evidence. Government owns the authority-side case apparatus;
   letterhead and reference occur on both copies.

7. **`Well-Schematic_BR-17_As-Completed_Rev0.pdf`** (`design_creative`). An as-completed attachment
   shows casing, cement, perforation, tubing and barriers, while also carrying a controlled identifier
   and revision. It is oil/gas operational evidence only when bound to a completion/EOR relation;
   otherwise `engineering.drawing-package` owns the controlled sheet family. Neither “well,”
   “as-completed,” title block nor revision decides alone.

8. **`EPR-AB1234 - Quarterly Monitoring Return Q2 2026 - Outfall 001.xlsx`** (`spreadsheet`). The
   operator/field, permit condition, sampling point, method, result, unit and submission sheet define
   operator compliance evidence. A government copy with receipt/assessment/enforcement evidence is
   authority-side. The existing government neighbour assigns a generic operator copy to
   manufacturing; this row explicitly raises the oil/gas-specific conflict instead of contradicting
   it silently.

9. **`BR-17_Well-Data-Submission.zip`** (`archive`). The manifest names completion, directional
   survey, open-hole log, schematic and sample members for one well. It may support a packet group,
   but it cannot donate one record type, period or fact to every member, and it is never unpacked to
   strengthen recognition. Opaque LAS/DLIS members remain unsupported if no approved extractor exists.

10. **`Rig-Move-and-Spud-Notification_BR-17.ics`** (`calendar`). An exact well reference and
    operator/rig-team roles can support group retrieval after the well is independently anchored.
    The event records a plan, not proof that the rig moved or spud occurred. Calendar is a
    `SOURCE_TYPE`, never a schema and never activation by itself.

11. **`RE BR-17 NPT and revised programme.eml`** (`email`). Native sender/recipient/subject and
    attachments make it useful context. Employer domains and well/NPT words do not prove cause,
    duration or template activation. Attachments require independent extraction; their facts are not
    copied onto the message.

12. **`IMG_4821_Wellhead-Gauge.jpg`** (`image`). Real camera EXIF and an industrial-looking scene
    establish Photos evidence, not an oil/gas well. With no readable tag, unit, site or permit, it
    may join an accepted well group without receiving that group's facts and otherwise falls through
    to One-Off Images.

13. **`Crude-Oil-Market-Outlook-2026.pdf`** (`text_document`). It is the topic false positive:
    publication structure, cross-country tables and price/production discussion but no holder-side
    field, well, permit or operational state. It belongs in Reading Inbox. This is a real file that
    looks maximally topical and is not this row's evidence.

14. **`AFE_BR-17_Drilling-Budget.xlsx`** (`spreadsheet`). A proposed-well cost authorization with
    vendor, cost code, forecast and approval columns is business/project/finance evidence. A well
    reference plus drilling vocabulary does not prove performed operation or production. It belongs
    in Independent Records or a business group if that schema independently activates.

Together the set covers labelled forms, tables, scanned/visual material, archive manifests, email,
calendar, sparse group members, a same-byte drawing collision, a same-byte permit collision, a
same-byte regulator/operator return, a compelled-filing seam and clear topic/budget false positives.

## Node test — all three legs

### 1. Detection signals differ from the schema default

The schema default accepts many authorized-source and measured-output worlds: utilities, renewable
generation, mining, farming, fisheries and forestry. It therefore recognizes broad structures such
as permit/source/output/period and asset/meter series. This row needs a narrower **actual well
lifecycle grammar**:

- well identity joined to rig, status, depths, operation summary and casing/log progress;
- approved activity distinguished from actual spud/progress/completion state;
- completion/EOR state joined to actual casing, cement, perforation and wellbore attachments;
- well tests joined to production conditions and stream rates;
- lease/well/month production joined to oil/gas/water allocation and disposition roles;
- workover, intervention, shut-in, restart and abandonment as state changes on one enduring well.

A field name, well token, permit, volume or oil/gas topic cannot express that relation alone. This
is materially narrower than the parent detector and produces useful abstentions on a permit
application, design sheet, market report and budget workbook.

### 2. Recommended dimensions differ from the schema default

The parent schema's provisional default is:

`site → operating_authority → output_stream → reporting_period → record_type`

This row's researched recommendation is:

`site/field → asset/well → reporting_period → record_type`

`operating_authority` may sit above the well where a corpus spans several leases/consents;
`output_stream` is normally search/allocation evidence because a well's oil, gas and water records
belong to one well history rather than three permanent branches. The well is the intelligible
parent: a daily report, completion, test or intervention is ambiguous without it. Time is not first.
The exact product sentence used in JSON is: **“For document and record domains, project, function,
or subject usually comes before time because putting year first scatters related work across
calendar folders.”** The quote was copied verbatim from `00`.

No order is serialized because PR-6 leaves `resource_operations.fields` empty. Writing proposed
keys into `dimension_order` would silently make them legal. The prose is evidence for R1c, not a
path and not a frozen filesystem.

### 3. Privacy rules differ from the schema default

The parent schema already marks operational records potentially sensitive, but this situation
concentrates exact well and field coordinates, subsurface configuration, barrier design, production
and reserve performance, facility vulnerabilities, incident/NPT narratives and environmental
exceedances. Some regulator copies may be public; publication of one report does not lower the
unpublished drilling/completion packet. Coordinates, pressures, quantities, conditions and personal
contacts are not destination dimensions and should not appear in general summaries.

This difference supports a sharper template privacy rule but not a new handling class. P7 owns the
classification and model-access policy. NJ-OILGAS-5 asks whether stronger protection should be
product-wide for critical-infrastructure/subsurface evidence.

## Proposed fields — six secondings, zero inventions

`fields` remains empty. The JSON's six proposals deliberately repeat the schema anchor's exact keys
and arguments with oil/gas evidence; they do not mint variants.

- **`site`** — field, lease area, platform or facility as operating place. It is not Photos
  `location`; a field image may be captured elsewhere. Conditional first dimension only in a
  multi-site corpus.
- **`operating_authority`** — operator-held lease/permit/consent and conditions. Government owns
  the issuing case. Destination eligibility is useful but may expose concession/infrastructure
  identifiers, so the schema's policy caveat remains.
- **`asset`** — the enduring well/wellbore/facility thread. This row argues that `asset` should be
  broad enough; it refuses to mint `well_id` before R1c.
- **`output_stream`** — oil, gas, condensate, produced water and similar labelled allocation roles.
  Useful evidence, but not a standing folder level for most well histories.
- **`reporting_period`** — period the activity or production is about. Not `creation_date`,
  `tax_year`, `term` or `capture_year`; it is optional below the well and never first.
- **`record_type`** — reuse the canonical spelling if R1c makes it cross-domain. Well activity,
  completion, test and allocation are values, not child nodes.

Tempting rejected fields:

- `well_id` — rejected as a private synonym before `asset` is adjudicated;
- `field` or `lease` — rejected as a private synonym or premature split of `site`;
- `operator` — role ambiguous and often authorship/holder identity; no proposed global key exists;
- `rig` — valuable search/group evidence on drilling reports but a poor stable destination;
- `depth`, `pressure`, `volume`, `rate`, `reserve`, `coordinate` — high-cardinality, sensitive,
  revision-prone content, not destination facets;
- `well_status` — potentially useful search state, but it changes over time and would turn one
  well history into state folders competing with version/event records;
- `form_number` — an observation helping document-function validation, not an organizing fact.

## Reciprocal boundaries — exact fixture bytes on both sides

Every collision uses a roster-valid template id and an object shaped exactly
`{domain, signal, provenance}`. The `signal` states both directions and names one identical fixture.

### Engineering drawing package

**Same fixture bytes:** `Well-Schematic_BR-17_As-Completed_Rev0.pdf`.

- This row must not steal a free-standing controlled well schematic merely because it says well or
  as-completed. Without an EOR/completion attachment relation, the title-block identifier, revision
  history and issue/transmittal structure belong to `engineering.drawing-package`.
- Engineering must not steal the actual completion state when the sheet is explicitly attached to
  an EOR/workover record and the casing/cement/perforation/tubing/barrier positions record what was
  installed rather than what was designed.

The engineering neighbour's own memo makes title-block structure the anchor and says version-family
membership never transfers facts. This row adopts that rule. R1c owes the reciprocal edge because
the engineering file predates this row.

### Government permit and licensing

**Same fixture bytes:** `BSEE-0123_APD_OCS-G-12345_A-17_Approved-with-Conditions.pdf`.

- This row owns the holder-side instrument only when the same well reference is independently joined
  to actual activity/completion evidence. It expressly refuses activation from possession of an
  approved permit alone.
- `government.permit-licensing` owns the deciding authority's continuing-permission case: intake,
  assessment, representations, determination, register/renewal and adverse-power apparatus.

The government neighbour explicitly says possession of a permit by its holder never activates the
government row and that reference/letterhead occur on both copies. This row does not contradict it;
it takes only the operator's later operational grouping, and abstains if no actual operation exists.

### Government environmental regulation

**Same fixture bytes:**
`EPR-AB1234 - Quarterly Monitoring Return Q2 2026 - Outfall 001.xlsx`.

- This row owns the operator-prepared return when field/facility and permit-condition evidence joins
  measured results to the producing operation and there is no authority receipt/assessment step.
- `government.environmental-regulation` owns the authority-side received and assessed copy when a
  return-register receipt, officer review, surveillance, incident or enforcement relation exists.

The landed government node names the same bytes but assigns the generic operator copy to
`manufacturing.environmental-compliance`. That is the important contradiction risk. The JSON signal
and NJ-OILGAS-4 surface it explicitly: R1c must decide whether field-specific operator monitoring
belongs here or whether one cross-sector operator-compliance applicability definition is reused.
This row does not silently erase the prior claim.

### Business regulatory filings

**Same fixture bytes:** `OGOR-A_Well-Production_OCS-G-12345_2026-06.csv`.

- This row owns the well/lease/month production and allocation content, whether internal or later
  submitted.
- `business_operations.corporate-regulatory-filings` owns the external obligation and submission
  trail: deadline, filing reference, declaration, receipt, acknowledgement, reminder or penalty.

The business neighbour already states that sector regulated returns lean to the sector row when
site/asset/metered-quantity evidence is present, using utility metering as its current reciprocal.
This oil/gas edge extends that same discriminator to a roster-valid sector sibling. Custody alone
settles neither side.

## Same-byte collision fixture — the row's hardest test

The single strongest fixture is the approved APD:

`BSEE-0123_APD_OCS-G-12345_A-17_Approved-with-Conditions.pdf`

It looks exactly like this row's evidence: oil/gas well, operator, lease, drilling programme,
authority approval and conditions. It is nevertheless **not sufficient**. Planned activity is not
performed activity. The file can be:

- a government authority-case member when case apparatus establishes deciding custody;
- an operator Independent Record when held alone;
- a member of an oil/gas well history only after a WAR, spud notification, EOR/completion or other
  actual-state evidence independently anchors the same well.

The permit reference and letterhead are identical across copies. The discriminator is evidence
outside those shared bytes only when it is represented as the bounded dossier/custody relation; no
fact is copied from the dossier onto the permit. This is the row's deliberate refusal to equate
authorization with operation.

The market outlook is the pure topic fixture and the well schematic is the pure format/appearance
fixture. Together they prove that neither topical language nor engineering appearance can rescue an
otherwise missing operational relation.

## Files considered and rejected from activation

- **`Crude-Oil-Market-Outlook-2026.pdf`** — Reading Inbox; topic, price and production tables across
  many countries, no operator-side well/field relation.
- **`AFE_BR-17_Drilling-Budget.xlsx`** — a proposed-work cost authorization; business/project/finance
  evidence, not proof that drilling occurred.
- **`BSEE-0123_APD...Approved-with-Conditions.pdf` alone** — authorization, not operation;
  Independent Records or government case depending custody.
- **`North-Field-Reservoir-Simulation_Case-12.xlsx`** — engineering/research analysis if it tests a
  model or general proposition; projected rates are not measured production.
- **`PFD_Central-Processing-Facility_RevD.pdf`** — process-plant design; revision/baseline and
  tag-line topology, no actual well activity or production period.
- **`Pipeline-Shipment-Tickets_June.csv`** — logistics custody/movement; origin, destination,
  consignment and quantity do not form well production.
- **`Crude-Sales-Invoice_2026-06.pdf`** — finance/sales record; price, buyer and payment terms are
  not production allocation.
- **`Royalty-Statement_Lease-12345.pdf`** — finance/regulatory payment record unless the underlying
  production schedule independently carries the operational relation; payment does not prove
  quantity accuracy.
- **`Sustainability-Report_2025.pdf`** — business/publication evidence unless site-level operator
  monitoring and conditions are directly cited; aggregate ESG charts do not activate this row.
- **`Drilling-Contract_Master-Service-Agreement.pdf`** — legal/business contract; well vocabulary
  states scope, not performed work.
- **`Wellhead-Gauge.jpg`** — Photos/One-Off Images without readable well/site evidence; industrial
  appearance cannot activate.
- **an unreadable `.dlis`, `.las` or vendor database** — Unsupported or Encrypted unless an approved
  extractor exposes a usable structure; extension and filename remain routing clues only.

## Neighbours considered without another edge

- **`business_operations.compliance-audit`** — a well-control audit can quote activity reports and
  barrier evidence, but the assessment-occurrence/request/finding/corrective-action chain is clear
  once present. Corporate filings is the sharper same-byte boundary for the production return.
- **`engineering.process-plant-design`** — facility P&IDs, line lists and control narratives are
  tempting, but this row rejects them without actual operational state. The drawing-package edge is
  narrower and attaches to literal shared well-schematic bytes; a second broad engineering edge
  would add little.
- **`logistics.shipment`** — crude and gas movements share quantities and facilities, but
  consignment/custody/origin-destination is plainly different from well/lease production. The JSON
  false-positive list carries this boundary without an edge because no unresolved same-byte fixture
  remains after structure is extracted.
- **`finance.small-business-bookkeeping` / tax and royalty rows** — money, royalty and valuation
  records may quote production quantities, but financial institution/account/tax/record structures
  remain distinguishable. Finance is a safety schema and protective ordering wins if it activates.
- **`research.dataset-analysis`** — reservoir, seismic and production datasets can be research when
  their object is a generalizable proposition. A named well's recurring actual activity/production
  series is operational. The boundary is important but not represented by one unresolved fixture in
  this row.
- **`resource_operations.renewable-generation` and `mining-operations`** — sibling templates use the
  same schema proposals but have different asset/output vocabularies and operations. A generic
  “production report” is never-alone; extracted well/wellbore versus generator/mine structures
  discriminate without a new edge at this stage.

## Co-activation intent — memo only for R1c

`also_holds_with` is deliberately `[]` because CONNECTION §5 allows that edge only schema↔schema.
This template does **not** author template-level coactivation.

R1c should consider or reuse the `resource_operations` schema anchor's existing schema-level intent:

- an as-executed completion schematic can carry independent engineering evidence and oil/gas
  operational evidence;
- a permit or monitoring return can carry independent government issuer/assessment evidence and
  resource-operator evidence;
- the wellhead photograph can carry Photos facts independently while grouping with a well;
- a compelled production return can carry submission-purpose evidence, but whether that merits
  business_operations schema coactivation or one shared P10 applicability definition is
  NJ-OILGAS-2.

No `file_examples.also_schema` value is used to evade the rule except `photos` on the camera image,
where the file's own EXIF independently licenses Photos facts. Collision fixtures otherwise keep
`also_schema: null` so collision and coactivation are not asserted from the same ambiguous evidence.

## Residual behavior

- **Independent Records** — standalone readable permit, report, completion attachment or test with
  durable value but no accepted well/field group.
- **Review Later** — actual-versus-planned, operator-versus-authority or operational-versus-design
  status cannot be cited.
- **Unsupported or Encrypted** — native well-log/proprietary database/encrypted data-room material
  yields metadata only.
- **One-Off Images** — field photograph has camera evidence but no readable operational subject.
- **Reading Inbox** — market outlook, technical paper, regulator guidance or published reserve
  report is reference material.
- **Protected Records** — inactive precise well/subsurface/infrastructure or incident material needs
  a safe broad home. This is a residual recommendation, never a handling class.

All residual targets use the nine names from `00`. They are not roster ids and do not activate.

## NEEDS-JOSEPH / R1c adjudication

1. **NJ-OILGAS-1 — survive or fold.** Is well-history-led recognition plus
   `site → asset → period → record_type` enough to license a distinct template, or is the row only
   oil/gas values inside the resource_operations default? Keep if detection/order/privacy differ;
   refuse if the only difference is terms and form names.
2. **NJ-OILGAS-2 — operational return versus compelled filing.** Should operator-side production
   and environmental returns be owned by the sector template, by
   `business_operations.corporate-regulatory-filings`, or by two applicability records compiled to
   one shared P10 definition? The same bytes carry measured content and submission purpose.
3. **NJ-OILGAS-3 — well and field roles.** Is `asset` broad enough for well/wellbore and `site`
   broad enough for field/lease/platform? Alternatives: widen/reuse the two proposals; split one
   canonical role with an argued cross-template need; or refuse depth and keep the values only in
   groups. This row mints neither `well_id` nor `field`.
4. **NJ-OILGAS-4 — operator environmental owner.** The government environmental node currently
   assigns its operator copy to manufacturing environmental compliance. Confirm that a return tied
   to a producing oil/gas field belongs here, or compile both into a cross-sector operator-compliance
   definition. The existing neighbour cannot remain silently contradicted.
5. **NJ-OILGAS-5 — protection posture.** Should precise well/subsurface/critical-infrastructure
   records receive stronger P7 controls even when regulator copies may be public? Options: packet
   posture dominates; public-member evidence lowers only that member; or user policy declares the
   corpus role. The catalogue cannot choose a handling class.
6. **NJ-OILGAS-6 — authority in paths.** The schema proposes `operating_authority` as
   destination-eligible. For this template, lease/consent identifiers improve retrieval but expose
   concessions and infrastructure. Decide true, false or policy-dependent centrally; the JSON
   preserves the schema proposal and warns to flatten/protect.

None blocks research completion. All are explicit alternatives rather than smoothed assumptions.

## Self-audit

- The row is a template on roster-valid schema `resource_operations`; `parent_id` remains null.
- `fields` and `template.dimension_order` are empty under PR-6.
- All six `proposed_fields` second the exact schema-anchor proposals; no synonym or private field was
  minted.
- All fourteen `file_examples.source_type` values are in the closed `SOURCE_TYPES` vocabulary.
- File examples separate observations from facts and write no folder path as a fact.
- Sparse calendar, email, image and archive members use `group_without_copying_facts`; no well or
  site fact is propagated from a neighbourhood.
- Work types are values, not child nodes.
- Every `collides_with` endpoint exists in `roster.json`, is `kind: template`, and each edge is
  exactly `{domain, signal, provenance}`. Each signal states both directions and names the same
  fixture bytes.
- `also_holds_with` is empty; intended schema coactivation is recorded above for R1c.
- Every fallthrough is one of `00`'s nine residual names.
- No threshold, score, statistic, jurisdiction-specific regex, gazetteer content or handling class
  was invented.
- Direct design quotations in JSON and this memo were copied from `00`; external sources are
  paraphrased and do not become design authority.
- Only the two assigned output files were created; no neighbour, roster, schema, canonical field,
  source, test, planning or git-state file was touched.
