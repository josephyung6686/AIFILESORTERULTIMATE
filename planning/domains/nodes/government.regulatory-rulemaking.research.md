# Research memo — `government.regulatory-rulemaking`

Depth: J-DEPTH
Date: 2026-08-26
Output: `planning/domains/nodes/government.regulatory-rulemaking.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, `launch: placeholder`

## Result

Accept the node, narrowly, on one difference the schema default cannot state: **docket reciprocity**. Everything else about this row — the vocabulary, the document types, the stages — is a work-type list and would not have earned a node.

## The charge, stated at its strongest

I am obliged to argue this row out of existence before arguing it in. The case against it is unusually strong, and it has four independent legs.

**1. It is a work_type enum, verbatim.** The government schema anchor's `work_types` already contains, as one string: `"proposed rule, supporting analysis, public comment, response to comments, final instrument, or guidance"`. My assignment's `one_line_hint` is: "the proposal, the supporting analysis, the comments received, the response to them and the final instrument." Those are the same list. The dispatch prompt is explicit that `work_types[]` is an enum of values and that a child node per work type is exactly what not to ask for. On its face this row is the schema's own enum promoted to an id.

**2. It is a lifecycle stage of a neighbour.** `government.policy-development` covers "policy options paper, impact assessment, briefing, consultation, response analysis, or decision record". Rulemaking is arguably policy development that happens to end in a binding text — a terminal stage, not a different world. Stages are not nodes.

**3. It is a duplicate of `government.public-consultation`.** Two of my five named components — comments received, response to comments — are that row's entire subject. `government.legislative-record` has already landed a boundary saying consultation "belongs to the body that will decide the proposal and keys its comments to a consultation identifier". The body that will decide a proposed rule *is* the rulemaking body. On that sentence, my comment stage is already owned.

**4. "Final instrument" is a document type, and "regulator" is an organisation name.** A statutory instrument, a Federal Register final rule, a made regulation — these are document types, and the schema anchor already excludes organisation names and document-type words as activation evidence.

If all four hold, this row is a label and should be refused.

## Why the charge does not carry — the one real difference

The defence is not that rulemaking has different documents. It does not; the documents are the enum. The defence is that rulemaking has a **different activation rule**, and it differs from the schema default in the one direction that matters for safety.

The government schema's stated default is role-structural: every accepted signal "must evidence the holder or producer in an authority-side role, not merely name a public body." That rule is correct for legislative records, permits, casework, procurement, statistics — in each, the authority produced the thing.

A rulemaking docket breaks it. The majority of a real docket by item count was **produced by parties the body does not control**: comment letters on company letterhead, campaign template letters, individual submissions, petitions for rulemaking. Applying the schema default to those files rejects them, because the producer block belongs to Acme Chemicals, not to the regulator. Applying it loosely — accepting anything with the regulator's name on it — activates on every regulated firm's downloads folder in the country.

So this row needs a signal the default does not have and cannot borrow: **the same proposal reference printed on an item the body ISSUED and an item the body RECEIVED, in one custody.** Reciprocity, not authorship. That is a genuinely different detection rule, it is true of my file list, and it is the discriminator on which the `Comment 0231` / `Consultation response - FINAL - approved by GC - v7.docx` pair turns. Under CONNECTION's node test, differing detection signals are sufficient on their own.

Two further differences reinforce it, neither load-bearing alone:

- **Grouping across changed identifiers.** In real rulemaking the identifier changes at the moment of making: a docket string becomes an instrument number, a consultation reference becomes an SI number. The schema default's grouping — "an exact reference" — assembles the proposal family and the instrument family as two separate groups and stops. This row needs the extra rule that a *printed cross-reference on the later document* ("further to the consultation published under...", "amends SI 2019/123") joins them. That is not the default.
- **A two-posture split inside one packet.** The schema default is protect-by-default. Rulemaking is deliberately public in part — the docket is published on purpose — and strictly embargoed in part: the pre-publication draft instrument and the draft response-to-comments are pre-decisional and sometimes market-moving, sitting in the same folder as items the body itself published. Neither the schema default nor a residual expresses that a published rule's presence must not lower the posture of the drafts beside it. Both remain `potentially_sensitive` because that is the whole vocabulary available in this phase; the difference is in the recognition and `never_alone` rules, not in the label.

**Rebuttals to legs 1, 2 and 4.** Leg 1 is defeated because the node is not the enum: the enum is retained as `work_types` values inside the node, exactly as the prompt requires, and the node itself is the reciprocity rule. Leg 2 is defeated by the terminus: policy development's chain ends in a decision or a published policy and has no received-and-logged third-party evidence at its centre; the impact assessment is the honest contested fixture and I have named it on both sides. Leg 4 is defeated because I do not activate on the instrument at all — `Federal Register - Final Rule - Hazardous Waste Generator Improvements.pdf`, the single most rulemaking-looking file in the world, routes to Reading Inbox in this node.

**Leg 3 is not fully defeated.** It survives as NJ-1 below. I have proposed a seam and I do not think it is obviously right.

## Node test, three legs

- **Detection signals.** Differ. The schema default requires authority-side producer evidence on the item; this row requires custody reciprocity across two items and explicitly admits items with third-party producer blocks. This is the leg the node passes on.
- **Recommended dimensions.** Empty on both sides, and cannot differ, because PR-6 leaves the government schema fieldless and a template cannot branch on undeclared fields. The prose recommendation does differ (docket reference and rule stage as *separate* levels, because one docket must be able to hold two identifiers across the making event, and because proposal/comments/response/instrument are families a user genuinely wants apart), but I count this leg as **not passed** — it is a note for R1c, not evidence.
- **Privacy rules.** Differ in kind rather than in label. Same `potentially_sensitive` value; different rule, because deliberate publication of part of the packet is normal here and must not be allowed to propagate to the rest. I count this as **partially passing** — it constrains recognition, not classification.

One leg cleanly, one partially, one not. The contract requires that signals, dimensions, *or* privacy differ. One clean leg is enough, and I would rather record the split honestly than claim three.

## Evidence base

Design docs, grepped rather than streamed: `planning/00-database-agent-product-design.md` (residual library definitions; the dimension-ordering rule; the protected-material rule), the standing brief, the stamped assignment, `government.json` (the schema anchor — default template, work_types, collisions, residuals, sensitivity), and `government.legislative-record.json` (the only landed row that already argues a boundary against this id). `legal.practice-matter-file.research.md` was read once for calibration.

Three verbatim `00` spans are used in the JSON and all grep back out of source: the residual definitions for Independent Records, Protected Records, Reading Inbox, Review Later, Unsupported or Encrypted and Temporary Screenshots; “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”; “The system recommends an order based on the domain template, but the user can reverse, remove, add, or flatten dimensions.”; and “Protected material should not be included in cloud-model prompts by default, should not display raw content in general group summaries, and should not be moved automatically without a user policy that explicitly permits it.”

Everything about rulemaking practice itself — comment periods, receipt logs, response-to-comments dispositions, explanatory memoranda, made-versus-in-force dates, general permits, mass-comment campaigns — is marked **inference** from named real document types. `00` says nothing about rulemaking and I do not pretend otherwise. `provenance: proposal` on the node reflects that.

## Files considered and rejected

Named false positives, with the discriminator on each:

- `Federal Register - Final Rule - Hazardous Waste Generator Improvements.pdf` — **the collision fixture.** Agency masthead, document number, full preamble including a response-to-comments discussion. It contains, inside one PDF, a facsimile of my entire chain. Discriminator: no receipt stamps, no comment index, no proposal-side sibling, no draft version family, a download-manager filename, and consultancy client alerts beside it. Publication origin is not custody. → Reading Inbox.
- `Consultation response - FINAL - approved by GC - v7.docx` — the reciprocity fixture from the other direction. Discriminator: an internal version family v1–v7, a legal-review markup, an approval thread, and the docket reference appearing only in the addressee line. Drafted-and-approved, not received-and-logged. → `business_operations.corporate-regulatory-filings`.
- The mass-campaign template letter — rejected as *this row's* evidence when found on the campaign's drive beside mobilisation assets and a response tracker; accepted when found inside the body's comment index, where its duplicate count is itself part of the record and must not be de-duplicated away.
- `Permit PPC-2026-0442 - Acme Chemicals Ltd - variation decision.pdf` — a named holder and a determination. Rule-application, not rule-making. → `government.permit-licensing`.
- `Enforcement Notice - Acme Chemicals Ltd - breach of condition 4.pdf` — same regulator masthead as my proposal, keyed to an operator and a condition. → `government.environmental-regulation`.
- `Fitness to Practise - Registrant 88213 - panel determination.pdf` — same regulator, casework about a named person. → `government.professional-regulator`.
- A law-firm client alert reproducing draft regulation text verbatim — legal-text shape without custody. → Reading Inbox or a practitioner matter file.
- A standalone options appraisal with the same subject and no draft instrument → `government.policy-development`.
- A scrutiny committee report and the division on an annulment motion → `government.legislative-record`, mirroring the boundary that row already wrote.
- `Rulemaking docket archive 2019-2024 - password protected.zip` — the filename asserts a docket, a range and a subject and establishes none of them. → Unsupported or Encrypted, unopened.
- Rejected as node content, not just as files: a taxonomy of regulatory regimes, sectors, instrument types, or jurisdictions; a procedural-stage tree; live docket-system ingestion. Each would turn a placeholder into the industry catalogue J-IND defers.

## Reciprocal boundaries

Nine collisions are authored, each naming the same fixture on both sides. The four that carry real risk:

1. **`government.public-consultation`** — engagement exercise vs instrument chain. Same packet, split: question set / response form / response-analysis summary go there; draft instrument text, the impact assessment bound to it by printed reference, the response-to-comments annexed to the instrument, and the made instrument come here. Received named submissions are protected on both sides regardless. This split is NJ-1.
2. **`government.legislative-record`** — reciprocal to the boundary they already landed, using their fixture unchanged. Made instrument + explanatory memorandum → here. Scrutiny report + annulment motion + division → there. I did not restate their sentence; I mirrored its allocation.
3. **`business_operations.corporate-regulatory-filings`** — custody direction on identical bytes, both directions stated: the firm's comment letter with its approval chain is theirs; the same text with a receipt stamp in the body's index is mine; a made instrument on the firm's drive is their compliance reference, not my docket member.
4. **`government.permit-licensing`** — `General Permit GP-14` is the fixture: permit vocabulary, no named holder, class eligibility, a comment recital. A rule wearing permit clothing comes here; a holder-named variation decision never does.

Also authored: `government.policy-development`, `government.professional-regulator`, `government.environmental-regulation`, `nonprofit.advocacy-campaign`, `legal.practice-matter-file`.

**Neighbours deliberately given no edge.** `government.public-records-foi` — a disclosure request *about* a rulemaking docket is an FOI case keyed to a request reference, not a docket member; the seam is clean enough not to need a mutex. `government.public-procurement` — shares received-submission mechanics but a bid is priced and awarded, not commented on. `research.reading-library` — the false-friend published rule is already routed by residual rather than by mutex, per the pattern the landed legal row used. `photos.screenshot-captures` is a coactivation case on the portal screenshot, recorded as `also_schema` on that fixture, not a collision.

`also_holds_with` is empty: this template cannot author schema-level coactivation, and the government schema exposes no role field to split. `role_split` carries one entry against `business_operations.corporate-regulatory-filings` recording the sender/receiver seam as a recognition rule, explicitly noting that no role key can be written while PR-6 stands.

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false`, `proposed_context_terms: []`. All intentional under PR-6 and D1.

Candidates considered and not minted: a docket or proposal reference, an instrument identifier, a rule stage, a making body, a comment receipt number, an effective date. Each is a real slot on my fixtures and each would be a new canonical key on a schema the design has deliberately left fieldless. I propose none; NJ-2 records them for central adjudication if PR-6 lifts. `record_type` and `institution` are Finance-scoped; `purpose` is Applications-scoped; none are reusable here.

Time is not first: a docket's dates — proposal, comment close, made, laid, coming-into-force, filesystem — all differ in meaning, and year-first would scatter one instrument's chain across five folders.

## Grouping without copied facts

Membership is bounded by docket reciprocity plus, for a received item, an exact receipt number appearing in a comment index. Membership creates nothing on the member: a comment letter joined to a docket gains no body, no date, no disposition, and no publication authority. Three fixtures carry `group_without_copying_facts: true` — the comment letter, the late-submission email, and the portal screenshot — because each can be retrieved into a candidate docket neighbourhood while the schema stays inactive on the file itself. An archive is read from its manifest and not unpacked to improve classification.

## What this node must never conclude

That a rule was made, is in force, unrevoked, or currently accurate. That a recited consultation duty was satisfied. That a comment was accepted, considered, or is legally late. That a preferred option in an impact assessment was adopted. That a pre-publication marking is a handling class or an embargo finding. That publication of the docket authorises publication or remote transmission of any member. That a count of index rows is a count of opinions.

## NEEDS-JOSEPH

- **NJ-1 — the consultation seam.** A consultation on a draft instrument is one real packet that this proposal divides between two rows. Alternatives: (a) rulemaking absorbs the comment stage wherever a draft instrument exists, leaving `government.public-consultation` only non-instrument engagement; (b) consultation absorbs the comment stage entirely, leaving this row proposal, analysis and instrument; (c) the proposed split stands and the packet is divided. R1c should decide this reciprocally with the public-consultation row rather than let each side assume it wins. This is also the thinnest point in the whole government cluster.
- **NJ-2 — fields, if PR-6 lifts.** Adjudicate centrally, not in children, whether a docket/proposal reference, an instrument identifier, and a rule stage may exist; whether any is destination-eligible; and whether a submitter identity may ever be a dimension. My position: a submitter must never be a dimension, because a person-named branch generated from received submissions publishes a fact the body may be obliged to withhold.
- **NJ-3 — delegated rulemaking bodies.** Standards bodies, self-regulatory organisations and quasi-public regulators make binding rules with the same apparatus and no clear public-body status. The schema anchor already asks whether public-authority status may be user-confirmed; this row is where the question bites hardest, because the rulemaking apparatus is identical and only the body's status differs. Same fixture, opposite answers: `Consultation - proposed changes to the Code of Conduct - CP26-3.pdf` from a statutory regulator versus from a trade association.
- **NJ-4 — pre-publication material.** P7 should own whether a pre-decisional draft instrument or draft response-to-comments warrants a stricter posture than the published items beside it. This phase has only `none` and `potentially_sensitive` and cannot express it.

## Self-verification

`python3 -m json.tool` parses the node. Key set matches `government.legislative-record.json` exactly, including `proposed_context_terms`. Every `source_type` is in `SOURCE_TYPES`. Every neighbour id is on the roster. Every `falls_through_to` name is one of the nine residual homes. All four `00` spans grep back verbatim. No thresholds, no handling classes, no invented quotations, no folder path written as a fact. Sixteen file examples, covering labelled form, unlabelled internal prose, spreadsheet index, email, OCR screenshot, audio-video, archive, encrypted binary, two collision fixtures and one permit-shaped rule. Only the two assigned files were written.
