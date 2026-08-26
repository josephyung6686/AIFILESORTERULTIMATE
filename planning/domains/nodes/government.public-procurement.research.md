# Research memo — `government.public-procurement`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.public-procurement.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, `launch: placeholder`
Absorbs legacy: `gov.contract-award-record`

## Result

**Accept.** The node survives the charge, but only on one leg of the node test, and the argument that nearly killed it is recorded below rather than smoothed away. Its increment over the `government` default is not "procurement done by government" — that phrase is a sector label and would have been fatal. It is two things that are evidence rather than vocabulary: the **fan-in of sealed submissions authored by external competitors the holder does not control**, and the **publication-and-remedy artifact family that only a regulated competition produces** (a structured contract notice with a named procedure, answers issued to all tenderers, a standstill/debrief letter, a published award notice). Neither exists in the schema default, and neither exists in private sourcing.

## The charge — the strongest case that this row should not exist

I ran the charge before writing anything, and three of the six failure shapes landed hard.

**(1) Duplicate of its own schema's default template.** This is the near-fatal one. The `government` anchor has already pre-empted procurement in all three of the places a template would claim. Its `recognition.deterministic` carries, verbatim, "a public procurement record whose issuer block is a public contracting authority and whose structured notice, requirement, bid-receipt register, evaluation, approval, or award slots show buyer-side custody; a bidder's copy or a supplier's tender response alone is business_operations". Its `work_types` carry "procurement notice, specification, received bid, evaluation, approval, award, or contract-management record on the buyer side" — which is the roster's `one_line_hint` for this row restated almost word for word. And its `file_examples` already contain `Tender Evaluation Panel - IT Service 2026.xlsx`, with buyer-side block, procurement reference, received-bids, declared-interests, evaluation, approval and award-recommendation sheets. That is my central fixture, already landed on the anchor.

This is exactly the argument that killed the sibling `government.municipal-administration`, which is refused on the roster with the reasoning that "The `government` anchor's deterministic list already carries the governance-cycle recognizer verbatim ... Every signal this row could write is that signal plus the token municipal / council / local". If my increment were "that signal plus the token *public*", I would owe a refusal on identical grounds.

**(2) Duplicate of a neighbour — an organisation-type adjective on `business_operations.procurement-sourcing`.** A competition with a reference, a deadline, weighted criteria, an evaluation and an award is not a public-sector invention. `business_operations.procurement-sourcing` has already landed against me and says so: "Public-sector procurement is this situation under a statutory regime". If "under a statutory regime" is the whole difference, then the difference is a fact about the buyer's constitution — and a public body's name is precisely the never-alone evidence the anchor forbids ("a government department, regulator, municipality, legislature, court, public school, archive, museum, or official-looking seal alone").

**(3) A lifecycle stage of `business_operations.contract-administration`.** The `one_line_hint` reads as a sequence — "the notice, the tender documents, the bids received, evaluation and the decision to award". A lifecycle is not a node. Contract administration already landed the seam: "An authority's contract management and a supplier's copy of the same agreement are identical documents."

Two further shapes I checked and dismissed quickly: this is not a document type (no single document defines it — the row is only ever a bounded population), and it is not defined by an absence.

## Defeating the charge

**Against (1), the schema-duplication charge.** The municipal refusal turned on the added evidence being a *name* — a tier of government, which is never-alone by construction. My added evidence is not a name and not an adjective; it is a set of document types with no counterpart anywhere else in the roster, which exist only because an unsuccessful competitor has a remedy:

- A **standstill / debrief letter** exists solely to give a losing bidder a window and enough information to challenge. It discloses the winner's name and score alongside the recipient's own scores and per-criterion narrative. No private buyer writes this document, because no private loser has that right.
- A **clarification log with an issued-to-all-tenderers column** exists because every competitor must receive the same information simultaneously. A private buyer answers whoever asks.
- A **contract award notice** in the same structured form as the opening notice exists because of a transparency duty. A private buyer publishes nothing.
- A **published contract notice with a named regulated procedure** (open, restricted, competitive dialogue, negotiated, light-touch) plus a classification-code block and a fixed, non-extendable deadline. A private RFP has a deadline it can move.

The anchor's single procurement bullet does none of this. It discriminates *buyer-side versus supplier-side custody* and stops. It answers "is this an authority's procurement thing?"; the template answers "which competition, and where in it?", and adds a recognizer the anchor does not have — **two or more complete submissions from different external organisations under one issued reference**, which is the only signal in this world strong enough to establish direction of custody without relying on a name. Provenance: inference throughout this paragraph; the design docs do not discuss procurement, and I claim no statutory rule, only the observable existence of these document shapes.

**Against (2), the sector-label charge.** The discriminator I wrote into `collides_with` is not "the buyer is public". It is "the artifacts of publication and remedy are present". A state-owned utility that runs a regulated competition produces them; a government department that buys a laptop on a purchase order does not. The boundary therefore cuts across the public/private line rather than along it — which is what proves it is not the line. (It also generates NJ-2 below, honestly: for a body of ambiguous constitution the artifacts are identical and only the constitution differs, and I cannot settle that here.)

**Against (3), the lifecycle charge.** The row is not the sequence; it is the *bounded competition* as one object, and it stops at award. Everything after signature — the register, the notice calendar, variations, obligations — is `business_operations.contract-administration`, and I wrote that boundary reciprocally on the shared fixture (the executed order form). A row that ended at "and then we manage the contract" would indeed be a lifecycle and would deserve refusal.

## The node test, argued in full

CONNECTION §2: a template exists when its **detection signals**, **recommended dimensions**, or **privacy rules** differ from the schema's default. Three legs, each argued separately.

**Leg 1 — detection signals: DIFFER.** Argued above. The schema default has one procurement bullet turning on issuer-block custody. This template adds four signal families the default does not contain: the structured-notice-plus-named-procedure form; the issued-to-all clarification duty artifact; the multi-competitor fan-in under one reference; and the outbound decision correspondence (standstill, debrief, award notice) that only a remedy regime produces. It also adds never_alone entries the schema cannot state because they are procurement-specific — most importantly that a **competition reference token is never-alone**, since the identical token is printed on the authority's pack, on every bidder's response, on the published notice and in press coverage.

**Leg 2 — recommended dimensions: IDENTICAL, and I concede it.** The `government` schema declares no field rows under PR-6 (D1's deferral stands), so its default `dimension_order` is `[]` and `time_first` is `false`. A template cannot branch on undeclared fields. My recommendation is therefore the schema's recommendation character for character. This leg fails, exactly as it failed for `legal.practice-matter-file`, and I record it as a failure rather than dressing an empty array as a decision. The prose order (competition → issued/received/decided → work type) is written into `template.why` as prose only, and it is the substance of NJ-1.

**Leg 3 — privacy rules: DIFFER, and this is the second surviving leg.** The government default is a flat authority-side protective posture. This row's posture is **mixed inside a single group**, which the default cannot express. One competition reference simultaneously binds: material under a publication duty (notice, specification, award notice); third-party commercial property the holder did not author and holds in trust (received tenders, priced schedules, insurances, named CVs) including, before the deadline, the bare fact of *who bid*, which the receipt register discloses in one column; and named-person material (evaluator declarations of interest naming relationships to bidders, moderator narratives about named organisations). The standstill letters are the sharpest case — they are **bilateral by construction**, each naming the winner and one recipient's own scores, so no two are interchangeable and none may be shown to another bidder. A flat inherited posture is wrong in both directions here: it over-protects the notice and under-protects the receipt register. Publication of the award does not retro-publish the file.

Verdict: two of three legs differ. One suffices under §2. Accept.

## Files considered and rejected

Naming what is *not* my evidence was the most useful part of this pass.

- **A purchase order, supplier invoice, delivery note or payment record naming a public body.** Tempting because it is procurement-shaped and government-named. Rejected: it is the transactional record of a supply relationship, not the competition that created it. It is Finance/bookkeeping evidence or `business_operations.contract-administration`, and it activates neither this row nor the government schema.
- **A downloaded contract notice, framework agreement or published specification.** The single most common false positive, because it is the *most published* thing in this world and therefore the thing most likely to be on a stranger's disk. Rejected on the anchor's own principle — publication by an authority is not custody by an authority. It routes to Reading Inbox.
- **A supplier's contracts-register entry or bid-tracking spreadsheet.** Same columns as a procurement pipeline. Rejected: direction. The forward-plan register is in the JSON as a member-of-none fixture precisely because even the authority's own register belongs to no single competition and must not donate a competition fact to any file it names.
- **A framework agreement's schedules, held post-signature.** Rejected to `business_operations.contract-administration`; the competition is over.
- **A procurement portal's notification emails.** Rejected as a class: the same portal sends the bidder a submission confirmation and the buyer a receipt register, from the same domain, with the same branding. The portal name is a never_alone entry for this reason.
- **A live e-procurement system, a contracts database, or a procurement team's mailbox.** A source system, not a file node. A bounded export with a readable manifest is represented; live ingestion is a connector and security decision, not this row's.
- **Contact exports naming buyers, bidders, evaluators or category managers.** Rejected. Relationship roles need evidence in a competition workflow; an address book is not one.
- **Procurement policy, standing orders, thresholds guidance, training decks.** Rejected as reference material about procurement rather than a competition. They fall to Reading Inbox or the `government` default, and importing them here would make the row a topic.
- **A committee agenda pack containing a contract-award report.** Rejected to the `government` default, which already owns it (`Council Housing Committee - Agenda Pack - 18 August 2026.pdf`). A governance cycle that happens to approve an award is a governance cycle.
- **Named CVs, insurance certificates and identity documents inside a received bid.** Not rejected from the packet, but rejected as *converted* evidence: packet membership must not erase or overwrite their own identity/finance evidence, and this row's fixture marks the archive `group_without_copying_facts: true`.

## The collision fixture

**`ITT-2026-0412 - our tender response - FINAL.docx`** — the supplier's own bid, held by the supplier.

It carries the identical competition reference, quotes the authority's specification back verbatim, cites the same deadline, names the same contracting authority throughout, and may well be marked commercial-in-confidence. Every token-level signal matches. **What discriminates it is the surrounding population, not the document:** exactly one response is present; there is no receipt register; there are no other bidders; there is no evaluation, no declarations sheet and no approval block; and the version history and internal bid/no-bid note show the holder as author rather than recipient. It routes to `business_operations.procurement-sourcing`'s neighbourhood, and standalone to Independent Records.

A second collision is carried in the JSON because the reciprocal was already written against me: **`Grant Call GC-2026-08 - Assessment Panel Scoresheet.xlsx`**, which is structurally indistinguishable from my consensus scoresheet. It is discriminated by the *instrument*, never by the process.

A third, weaker collision worth naming: **a private company's `Request for Proposals - Website Redesign.pdf`** with a timetable, weighted criteria and a clarification window — the furniture copied without the regime. Absent a notice, a procedure name, an issued-to-all log or a standstill, it is `business_operations.procurement-sourcing`.

## Reciprocal boundaries

Each collision names the same fixture on both sides.

1. **`business_operations.procurement-sourcing`** — shared fixture: the issued tender pack (`ITT-2026-0412 Volume 1`) versus a private RFP with the same furniture. Mine requires publication/remedy artifacts; theirs requires a private buyer free to negotiate, change criteria or cancel silently. **Reverse direction, same fixture set:** the single tender response is theirs, never mine. Their landed row already states the seam from their side ("a published contract notice, a regulated procedure name, a transparency publication or a statutory standstill supports the government row"); I have written the mirror without editing their file.
2. **`business_operations.contract-administration`** — shared fixture: the executed agreement / order form (`Framework Schedule 4 - Order Form`). Mine is everything before signature; theirs is everything after, and theirs holds one agreement among many with no competition attached. Their landed row states it as a holder-side question; I state it as a lifecycle-phase question, which is the sharper cut, and record the difference as a recommendation to R1c rather than an edit.
3. **`government.grant-programme-administration`** — shared fixture: the evaluation/assessment scoresheet, named identically on both sides. Their landed text: "this row requires an instrument that gives money for the recipient's own purposes under conditions of funding with recovery on breach; procurement requires the authority buying goods or services for itself, with a specification, deliverables, and acceptance. Where only the scoresheet survives and no instrument is present, neither row activates." I have adopted that discriminator verbatim in substance so the two sides cannot drift.
4. **`construction_property.subcontract`** — shared fixture: a package bid analysis spreadsheet. Mine needs notice/procedure/publication; theirs needs a named site, a works package and a main-contract reference. Both directions matter because an authority procuring construction works genuinely produces both shapes.

## Neighbours considered that got no edge

- **`government.policy-development`, `government.public-consultation`** — a consultation and a tender both issue a document and receive responses, but consultation responses are opinions invited from anyone and are usually published, whereas bids are sealed, priced, competitive and confidential. The privacy posture is opposite, so the two are unlikely to be confused by a classifier and a mutex would be noise.
- **`government.public-records-foi`** — procurement files are a common disclosure subject, but a disclosure bundle is the FOI workflow's output; the underlying competition file is mine. Not the same evidence.
- **`business_operations.vendor-management`** — supplier performance, scorecards and relationship reviews are post-award and already covered by the contract-administration boundary. Adding a third edge on the same seam would over-specify.
- **`nonprofit.grant-reporting`** — recipient-side reporting. Already handled by the grant-programme boundary from the other direction.
- **`manufacturing.supplier-qualification`** — supplier audits and first-article approvals are qualification, not competition. `business_operations.procurement-sourcing` already carries that seam.
- **`legal`** is `also_holds_with`, not a collision: an award recommendation, a standstill letter or a challenge response is legitimately both.

## Fields, dimensions, `role_split`

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `role_split: []` — all intentional, all forced by PR-6. `role_split` in particular requires two field keys to split a role between; the `government` schema exposes none, so the buyer/bidder role distinction — which is this row's whole discriminator — cannot be serialized as an edge and lives in `recognition` and `collides_with` instead. That is a genuine expressive gap and is the reason NJ-1 exists.

Candidate keys rejected without minting: `institution` and `record_type` are Finance-scoped; `project` and `artifact_type` are Research/Code-scoped; `purpose` remains College-Applications-scoped under the current canonical record. `procurement_reference`, `contracting_authority`, `bidder`, `lot`, `procedure_type` and `award_status` are not canonical and this row does not mint them. **Bidder identity in particular must never become a field or a dimension** — a folder per losing organisation publishes in the filesystem the exact fact the debrief regime keeps bilateral.

## Contract compliance and self-verification

- JSON parses; key list is identical to the landed sibling `government.grant-programme-administration.json`.
- All 16 `file_examples[].source_type` values are in `SOURCE_TYPES`; so are all `file_kinds.source_types`.
- Every `collides_with` / `also_holds_with` id exists on `planning/domains/roster.json` (`business_operations.procurement-sourcing`, `business_operations.contract-administration`, `government.grant-programme-administration`, `construction_property.subcontract`, `legal`).
- All five `falls_through_to` names are §7.3 residuals; every `design_cite` and every quoted span in this memo and in the JSON was grep-verified verbatim against `planning/00-database-agent-product-design.md` before use (lines 32, 35, 42, 45, 95, 120).
- No thresholds, no confidence scores, no handling classes, no folder paths as facts.
- `never_alone` entries are true of tempting false files by construction — the reference token, the authority name, the portal name and the confidence legend are each present on the collision fixture `ITT-2026-0412 - our tender response - FINAL.docx`.
- Files written: only the two assigned. No roster, canonical-fields, neighbour-node, `src/`, or SPEC edits.

## NEEDS-JOSEPH

**NJ-1 — a bounded-competition key on the `government` schema.** Without one, this row recommends no dimension at all despite an obvious competition → function → work-type structure. `government.grant-programme-administration` has already raised the same question from the funding side. Alternatives: (a) leave PR-6 as is and accept that all government templates recommend `[]`; (b) declare one generic bounded-proceeding key reused across the whole `government` family (competition, case, consultation, programme, request) and let each template constrain it in prose; (c) declare per-template keys, which reopens the field explosion D1 deferred. Decide once, not twice.

**NJ-2 — bodies of ambiguous constitution.** A state-owned operator, a utility, a university, an arm's-length delivery company or a charity buying under a funder's flow-down conditions can all issue a notice-shaped pack with a named procedure and a standstill. The artifacts are identical; only the body's constitution differs, and constitution is exactly the never-alone evidence this schema forbids. Alternatives: (a) activate on the artifacts regardless of body, accepting that `business_operations.procurement-sourcing` loses some regulated private buyers; (b) require an evidenced public body, accepting that regulated utility procurement falls to the private row despite producing standstill letters; (c) abstain to Review Later whenever constitution is unevidenced. I have written (c) into `needs_llm` as the safe default but it is not a decision.

**NJ-3 — the bidder's side has no home that fits.** `business_operations.procurement-sourcing` is framed on the roster as a private *buyer's* sourcing, yet the collision fixture — a supplier responding to notices, meeting exclusion grounds, and receiving standstill letters — is a seller's bid desk. This row cannot hold it (it would destroy the direction discriminator) and should not be widened to try. Alternatives: (a) widen `business_operations.procurement-sourcing` to both sides of a purchase; (b) route the bid desk to `business_operations.contract-administration` pre-award, which fits badly; (c) accept Independent Records / Review Later as the honest residual for bid-desk material until a roster row exists. This is R1c's call and it touches a file I may not edit.
