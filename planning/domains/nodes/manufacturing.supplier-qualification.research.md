# Research memo — `manufacturing.supplier-qualification`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/manufacturing.supplier-qualification.json`
Roster row: template on the fieldless `manufacturing` schema, `parent_id: null`, `launch: placeholder`
Status: **SALVAGE.** A killed agent left the JSON with no memo. This memo carries the argument, and the JSON was verified line by line and repaired before it was accepted. What changed is recorded at the end.

## Result

Accept the node. It is a two-party approval file and its anchor is neither a supplier's name nor the word audit: it is a **counterparty held in the supplier role, paired with an approval scope, carrying a standing status inside an assessment or disposition structure.** It passes all three legs of the node test against the manufacturing schema's default template, and the first leg it passes on a discriminator the default does not possess at all.

Recommended prose order (no dimensions serialized, `fields: []` under PR-6): **supplier → approval scope → record type.** Not time-first. Not status-first.

## The charge, stated at full strength before it is answered

The brief asks for the strongest case that this row should not exist. There are four, and the first is genuinely dangerous.

**Charge 1 — it is an organisation-name row, i.e. never-alone evidence, and can never activate.** Its parent dimension is a company. The brief says outright that "a row whose only evidence is never-alone (an organisation name, a person's name, a document-type word) can never activate," and the manufacturing schema's own `never_alone` list independently bans "a product name, part number, SKU, organization name, supplier name, site name or postal address alone." If this row's job is to file by supplier, it is filing by exactly the token the schema refuses to fire on.

**Charge 2 — it duplicates `business_operations.vendor-management`.** That row also organises by the same counterparty, at the same folder level, in the same corpus, and a supplier and a vendor are the same organisation seen twice.

**Charge 3 — it is a bundle of document types.** Audit report, certificate, questionnaire, warrant, declaration, register. Six document-type words wearing a trench coat. ALIGNMENT is explicit that work types are values of a field and never nodes.

**Charge 4 — it is defined by an absence.** Read the JSON's own fixtures and the recurring discriminator is that these files have **no batch or lot of the holder's own making.** A row defined by what is missing is on the brief's own list of things a row must not be.

### Answering charge 1 — the anchor is a structure, not a name

The row does not activate on a supplier name and its `never_alone` list refuses one four separate ways: the name, the supplier code, the sender's email domain, and a folder called Suppliers. What activates it is a structure that only exists because a **second party is being granted or refused permission**, and those structures have no other reason to exist:

- a **customer-disposition block** — a slot carrying approved / interim approval / rejected, addressed at a party who is not the author. A document does not disposition itself.
- an **auditee slot occupied by an external organisation**. An audit report has an auditee; whose name sits in it is the whole question.
- a **submitting-organisation slot and an accepting-organisation slot holding different companies on one page** (the first-article report shape).
- an **approved-supplier register**, where many rows each pair a counterparty with a scope of supply, a status and a requalification date. Multiple rows prove a controlled population rather than one relationship, which is the same discipline the manufacturing schema already uses for its asset register.

None of these is a name. Each is a slot relationship, and each is exactly the "labelled-role context" that `00`'s evidence discipline requires before an organisation name may become a fact. The `supplier` key is proposed with `reliability_ceiling: validated` for this reason: the name alone is `possible` at best, and only a supplier-master or approved-list cross-check inside an assessment structure lifts it. R4/R6 own that rule family; this row writes no pattern and no threshold.

**The schema itself concedes the gap.** `manufacturing.json`'s own `needs_llm` list contains, verbatim: *"a supplier certificate that may be procurement evidence, incoming-quality evidence, or both depending on whether the holder accepted it against a received lot."* The default template can name the supplier case but cannot resolve it, and hands it to an LLM. That is a schema declaring a hole. This row fills it with a deterministic two-party structure rather than a judgement call. Charge 1 fails.

### Answering charge 2 — the vendor-management mutex is real but not fatal, and it is escalated

This is the sharpest edge on the roster and it is **not** fully settled here. The boundary that holds is *commercial relationship* versus *technical permission*:

- vendor-management owns onboarding admin, banking and tax details, contacts, spend, delivery and price performance, escalation, renewal.
- this row owns whether a named scope of supply **may be used**, and the assessment evidence that it still may.

`Vendor-Scorecard_Vertex_2026-Q2.xlsx` is the fixture that decides it. On-time-delivery, spend and responsiveness columns → vendor-management. Open-audit-findings, approval-status and requalification-due columns → this row. A scorecard carrying both is held by both on disjoint columns rather than fought over. `Vendor-Onboarding-Pack_Vertex.zip` is vendor-management's even though it contains a certificate copy, because the pack's purpose is admission to the payables system.

That boundary is workable but it is a **judgement about purpose applied to one spreadsheet**, and I do not think one agent should settle it alone. It is escalated as **NJ-SQ-3**. Charge 2 is answered but flagged, not dismissed.

### Answering charge 3 — the document types file identically, which a document-type node could not do

A warrant, a supplier audit report and a management-system certificate are three different `record_type` values. They file in the **same folder** under one supplier and one approval scope, because a person asking "may we still buy this part from Vertex?" needs all three at once. A node built on any one of those words would split that answer across three trees. The row therefore refuses to split on document type and holds it as a leaf. That is the opposite of a document-type node. Charge 3 fails.

### Answering charge 4 — the absence is a consequence, not the definition

"No lot" is a symptom of the real property, which is a positive one: **these files exist before and above any particular production run.** A part-submission warrant is written so that production may begin; an approved-supplier register governs orders that have not been placed; a management-system certificate expires on a date unrelated to any run. The lot's absence follows from a positive temporal and logical position, and the row activates on the two-party structure, never on the missing lot. Charge 4 fails, though it is the charge that most nearly succeeded and it is why the `must_not_conclude` block on the warrant fixture forbids manufacturing a `batch_lot` fact.

## Node test — three legs, against the schema's default template

The manufacturing schema's default is stated in `manufacturing.json`: `dimension_order: []` with a branch-shaped prose recommendation — *product then batch/lot then record type* for production and quality records; *site then asset then record type* for maintenance and calibration; *quality event then record type* for NCR/CAPA files.

**Leg 1 — detection signals: DIFFERENT, on an axis the default lacks.** All twelve of the schema's deterministic signals are single-party: they evidence the holder's own transformation or control cycle on the holder's own product, lot, asset or site. This row's four discriminators are two-party (disposition addressed outward, external auditee, differing submitting/accepting organisations, counterparty register). The schema's needs_llm concession quoted above proves the default cannot make this call. This leg is not a close call.

**Leg 2 — dimension order: DIFFERENT, with a key the schema does not propose.** `supplier` is not among the schema's six proposals (product, site, batch_lot, asset, quality_event, record_type), so the recommended parent level is unreachable from the default. The evidential reason is that a lot-led branch would strand a standing certificate, a register and a questionnaire in a level none of them can fill. The parent is the supplier because `00` states the rule directly: *"a parent dimension should provide the context required to understand the child."* A finding, a warrant and a corrective-action request are unintelligible without knowing whose approval they concern.

Not time-first, on `00`'s own rule: *"For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."* Both quotations grep back verbatim out of `planning/00-database-agent-product-design.md` (line 95 of the paragraph containing both).

Not status-first either, and that refusal is deliberate. Status is the most salient thing on every file here and the worst possible dimension: it changes without the file changing, so a status-led branch moves files nobody edited, and a stale extracted status is worse than none. That is **NJ-SQ-2**.

**Leg 3 — privacy: DIFFERENT IN KIND.** The schema's default sensitivity is the holder's own commercial exposure plus workers named in incident records. Every file here is a **judgement about a second organisation, held under an obligation owed to that organisation**: audit findings, capability results, capacity and financial-health answers, disqualification records. The exposure is asymmetric and contractual in a way no batch record is — a leak damages a third party who never chose this holder's filing system. Social-compliance and site-audit material additionally names workers at another company. Marked inference: `00` binds privacy to run before any model or connector receives content; it does not name supplier audit files.

Three legs, three differences. Accept.

## Files considered and rejected — the tempting false positives

Five files look like this row's evidence and are not. Each is in the JSON as a fixture with `facts_legal: []`.

1. **`Internal-Audit-Report_Plant-2_QMS_2026-04.pdf`** — the collision fixture, below.
2. **`RFQ-2026-114_Award-Recommendation.pdf`** — names several suppliers, scores them, has an approval chain of signatories. It is procurement's: nobody is granted a technical scope, and the scores are commercial weightings. The word *evaluation* does not activate this row.
3. **`Vertex-Precision_Delivery-Note_DN-88214.pdf`** — supplier name, part number, quantity, a received-by signature. Supplier name plus part number is precisely the never-alone pair. A signature is not an approval. → Receipts and Confirmations.
4. **`Screenshot 2026-06-02 at 09.14.11 - SQ Portal approval status.png`** — OCR shows a supplier row and a status label in a portal table. Refused: an approval-status fact from OCR alone is exactly the fact NJ-SQ-2 says is most dangerous. Positive screen-origin evidence activates Photos; missing EXIF would have proved nothing. → Temporary Screenshots.
5. **`Supplier-Qualification-Archive_Vertex_password-protected.zip`** — the filename contains a supplier name *and the word qualification*, and yields nothing. No supplier, scope or status fact from a filename; the archive is not forced open to improve classification. → Unsupported or Encrypted.

Also rejected as *not this row's evidence at all*: a maintenance manual from a machine vendor (equipment documentation, no assessment); a supplier's marketing capability deck (no question set of the holder's, no disposition); an NDA with a supplier (contract administration); a supplier's own internal procedure received as an audit attachment (it is evidence *cited by* an audit, not the audit).

## The collision fixture

**`Internal-Audit-Report_Plant-2_QMS_2026-04.pdf` beside `Supplier-Audit-Report_Vertex-Precision_2026-05-14.pdf`.**

These two files are **structurally identical**: scored clause or checklist rows with conformity ratings, findings carrying a severity and an objective-evidence note, an auditor identity and team list, corrective-action owners and due dates, the same standard cited, often the same template and the same auditor. Clause numbers decide nothing. Severities decide nothing. The word *audit* decides nothing. The auditor's employer decides nothing — a supplier audit is frequently performed by a contracted third party, and an internal audit is frequently performed by a consultant.

**What discriminates: the occupant of the auditee slot.** External organisation → this row. The holder's own plant and department → `manufacturing.quality-management-system`. When the cover page names two organisations and does not say which was audited, the file abstains to Review Later rather than guessing; that case is in `needs_llm` deliberately.

This is the misfire I most expect in production, and it is the reason `audit scope`, `objective evidence` and `finding severity` are marked in `proposed_context_terms_note` as confirming terms only, never firing terms.

## Reciprocal boundaries — both directions, same fixture on both sides

Ten collisions are authored. Six of them **reciprocate an edge a landed row already wrote against this one**, and I checked each against the neighbour's own signal text rather than asserting it:

| Neighbour | Shared fixture | This row owns | They own |
|---|---|---|---|
| `business_operations.vendor-management` | `Vendor-Scorecard_Vertex_2026-Q2.xlsx` | audit-finding, approval-status, requalification columns | delivery, spend, responsiveness columns |
| `business_operations.procurement-sourcing` | `SAQ_Vertex-Precision_2026.xlsx` / `RFQ-2026-114` | the standing approval that outlives the order | the competition and the award |
| `manufacturing.quality-management-system` | the two audit reports above | external auditee | the holder's own site as auditee |
| `manufacturing.inspection-record` | supplier-issued material test report / CoA | issuer identity + approval scope | composition and property tables, against one received quantity |
| `manufacturing.nonconformance-capa` | `SCAR-2026-018_Vertex_late-plating-adhesion.pdf` | the request issued **outward** | the internal action it triggers |
| `engineering.product-certification` | `ISO9001-Certificate_Vertex-Precision.pdf` | certified object is an **organisation** | certified object is an **article** against a regulation |
| `engineering.automotive-program` | `PPAP_BPA-210_Level-3_Submission.zip` | the packet's purpose | the design records inside, in their own files |
| `engineering.industrial-design` | appearance approval | the supplier's submission **to** a standard | the master sample that **establishes** the standard |
| `engineering.change-order` | `PCN-2026-0331_Supplier-Bushing-EOL.pdf` | the inbound supplier notification | the internal ECN raised in response |
| `engineering.material-specification` | `RoHS and REACH SVHC Declaration - connector 5747299-1.pdf` | declaring-organisation block = standing relationship evidence | substance table = material-content statement |

Two of these deserve their own sentence because they encode `00`'s archive discipline in opposite directions. **PPAP:** a container does not transfer its members' facts, and members do not transfer the container's purpose — `engineering.automotive-program` wrote that first and this row agrees on the same bytes. **Appearance approval:** the direction of authority separates them, and the two files even reference each other (`PPAP_Appearance-Approval_Supplier-Vertex_PSW-2201.pdf` cites `Appearance-Approval_BPA-210_Graphite_Master-Sample-MS-014.pdf`); citation is not membership.

### Deliberate non-edge

**`government.public-procurement` is NOT a collision, and the draft was wrong to make it one.** That row landed first and explicitly declined the edge, in its own memo: *"`manufacturing.supplier-qualification` — supplier audits and first-article approvals are qualification, not competition. `business_operations.procurement-sourcing` already carries that seam."* Adding a one-directional edge against a neighbour who argued the seam away would create exactly the non-reciprocal edge CONNECTION forbids. Removed from the JSON; recorded here. If a public-tender pre-qualification questionnaire filed as the holder's own standing evidence later proves to be a genuine same-evidence mutex, R1c can add it from both sides at once.

### Coactivation intent for R1c

`also_holds_with` is schema ↔ schema only, so the three entries there are `engineering`, `business_operations` and `logistics`. Two **template-level** coactivations are real and cannot be written here: with `business_operations.vendor-management` on a mixed scorecard, and with `engineering.material-specification` on a supplier-issued declaration. Both neighbours have already said in their own files that the shared fixture is held on disjoint evidence rather than fought over. R1c should decide whether template-level coactivation gets a slot; today the intent lives in this paragraph.

## Salvage record — what was verified and what was repaired

The inherited JSON was substantial and largely sound. It was **not** trusted unverified. Checks run and repairs made:

- **Neighbour ids:** all ten collision domains and all three coactivation schemas verified present in `planning/domains/roster.json`. **No dangling id** — the defect found on a sibling salvage row this session is not present here.
- **Quotations:** both `00` quotations grep back verbatim (`design_cite`, and the parent-dimension rule used in leg 2). The `"A session should never be treated as proof of topic"` line in `never_alone` also verifies verbatim. No fabricated quote.
- **Removed** the `government.public-procurement` collision — the neighbour declined it with an argued reason (above).
- **Added** the `engineering.material-specification` collision — that row had landed a collision against this one and the draft left it unreciprocated, holding the seam only at schema level in `also_holds_with`, which does not answer a template-level edge.
- **Extended** the `manufacturing.inspection-record` signal to name the material test report / certificate of analysis, which is the fixture that neighbour actually named; the draft had answered on a different fixture.
- **Added eight missing house keys** the draft lacked entirely against the landed template key set: `node_test` (the charge and all three legs — the most important omission), `fields_note`, `proposed_fields_note`, `proposed_context_terms`, `proposed_context_terms_note`, `work_types_note`, `also_holds_with_note`, `role_split_note`. Key set now matches `engineering.change-order.json` exactly, in both directions.
- **Confirmed and kept:** `fields: []`, `dimension_order: []`, `refuse_node: false`, `sensitivity: potentially_sensitive` with no handling class, one proposed field only, closed edge vocabulary, five residual homes all drawn from `00`'s nine, no thresholds and no regexes anywhere.

## NEEDS-JOSEPH

**NJ-SQ-1 — is `supplier` the right key, or should R1c mint a canonical counterparty?**
*Alternative A:* keep `supplier`, industry-scoped. Simple, reads correctly, but every schema with a two-party file will mint its own (`subcontractor`, `vendor`, `licensee`) and the roster ends up with one key per industry for one relationship.
*Alternative B:* mint a canonical `counterparty` with a role qualifier, reused across supplier qualification, subcontracting and vendor management.
*Alternative C:* widen the existing canonical `client` / `our_firm` engagement pair to be direction-neutral. Rejected here because reusing `client` for a seller inverts the relationship on every file, but R1c may see it differently. This is also why `role_split` is empty: the issuing/receiving split is real and sits in labelled slots, but no canonical key carries either side.

**NJ-SQ-2 — may a status-like fact exist at all?**
Approval status is the most useful fact on every file here and the most dangerous, because it changes without the file changing.
*Alternative A:* extract it as a **search-only, non-destination** fact, never a folder level. Preferred here.
*Alternative B:* do not extract it at all — a stale status is worse than no status.
*Alternative C:* extract it as a literal observation of what the document records ("the disposition box shows approved") rather than as a status assertion about the world. The warrant fixture's `must_not_conclude` is written for C, but C needs ratifying rather than assuming.

**NJ-SQ-3 — two templates with a mutex, or one template with a function dimension?**
This row and `business_operations.vendor-management` organise the same counterparty on the same folder level in the same corpus. Either they stay two templates and the mutex on `Vendor-Scorecard_Vertex_2026-Q2.xlsx` must hold in production, or they merge into one supplier template with a function dimension separating commercial from technical. Decide **before either row grows fields**, because fields minted on both sides make the merge unaffordable.

**NJ-MFG-1 (inherited, not re-argued)** — whether `record_type` widens from its canonical Finance role into a global document-function key. This row's leaf level depends on the answer and does not pre-empt it.

## Final recommendation

Keep `manufacturing.supplier-qualification` as a placeholder template with `fields: []`, `dimension_order: []`, one proposed field, and no time-first or status-first hierarchy. Activate on the two-party assessment or disposition structure and never on a supplier name, a supplier code, a certificate word or an expiry date. Hold the auditee slot as the discriminator against the holder's own internal audit. Route unresolved audits and supplier email to Review Later rather than manufacturing a supplier fact. Settle NJ-SQ-3 before this row or `vendor-management` grows a single field.
