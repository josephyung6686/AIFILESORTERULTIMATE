# Research memo — `government.public-health-administration`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.public-health-administration.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, placeholder launch
Absorbs legacy: `med.public-health-reporting`

## Result

**Accept.** `refuse_node: false`. The node survives on two of the three legs of the node test — detection signals and privacy rules — and I record honestly that it **fails the third**: its recommended dimension order is identical to the government schema's default (both empty under PR-6, and identical in prose). One leg failing is not fatal; the test is disjunctive. But a row that claimed all three would be padding, so I say which leg does not carry weight.

The distinct thing this row owns is not a health topic. It is a **workflow with an aggregation boundary inside it**: the same authority holds, in one bounded case, a clinician's notification naming a sick person, a pseudonymised line list derived from it, and a published aggregate derived from that. No other government sibling has three custody tiers of the same material inside one workflow, and the privacy consequences of that structure are not stated anywhere in the government default.

## THE CHARGE — the strongest case that this row should not exist

I state it before the defence, at full strength, because it very nearly wins.

**(a) It is a subject value, not a node.** "Public health" is a policy area. Strip the topic word from every candidate artifact and each one lands on a sibling that already exists: a premises inspection is `government.permit-licensing`, a nuisance investigation is `government.environmental-regulation`, named-person casework is `government.social-services-casework` or `government.constituent-casework`, an aggregate release is `government.statistical-programme`, an outbreak response is `government.emergency-management`, a health department's committee papers are `government.municipal-administration`, a health strategy is `government.policy-development`, and a health grant is `government.grant-programme-administration`. On that reading, "public health" is exactly what `housing` or `transport` would be — and `government.housing-authority` and `government.transport-authority` also exist on the roster, so the roster's own precedent does not rescue me. This is the charge's strongest form: **subject-area rows are the 574's characteristic error**, and I should assume I am one until proven otherwise.

**(b) It is an organisation name.** "The health department" is never-alone evidence by the government schema's own rule: *a government department, regulator, municipality... alone; the entity may be issuer, counterparty, subject, employer, cited authority, research venue, or service provider*. If the row's only anchor is the producing office's name, it can never activate.

**(c) It duplicates its own schema's default template.** The government schema's `work_types` already enumerate *inspection, enforcement record, reasons, decision*, *constituent, ombudsman, complaint, benefit, or service casework*, *census or survey instrument... statistical output, disclosure-control record*, and *public education... administration where the body sits inside the state*. The government default is already protected-by-default for named-person casework. If this row's contribution is "the above, about disease," it is a duplicate.

**(d) It is a document type / medium.** Line list, epi curve, case definition — a critic can call these three file shapes, and file shapes are values and `SOURCE_TYPES`, not nodes.

**(e) It is defined by absence.** A tempting formulation is "health work that is not clinical care" — a row defined by not-being-something. That formulation is disqualifying on its face.

## Defeating the charge

I defeat (a)–(d). I concede (e) entirely and refuse to use that formulation: this row is defined by what it positively holds, never as the residue of clinical care.

**Against (d), first, because it is easiest.** A case definition is not a file shape. It is a governing instrument: it states inclusion and exclusion criteria in person, place, and time, it is versioned, and every downstream classification in the outbreak is made *by reference to it*. Changing it retrospectively reclassifies cases already counted. No other government sibling produces a document whose function is to define membership of the very set the rest of the file is about. That is a workflow role, not a format.

**Against (b).** The row's deterministic signals never accept an office name. Every one of them requires the office block **plus** a workflow structure that only this world produces — a receiving-notification slot with a case classification, a coverage numerator against an eligible-population denominator, a contact-tier column, a cold-chain excursion window against lot numbers, a clearance-criteria section on an exclusion notice. Each of those is a labelled slot, not a topic word. The `never_alone` list is written specifically so that the strongest false friends trip it: a person's own vaccination card carries a programme name, dates, and lot numbers and still cannot fire.

**Against (c), the serious one.** The government default's *inspection, enforcement, decision* pattern is built on a **decision addressed to an application or an authorisation**. This row's core chain has no application and no applicant. A notification is unsolicited, arrives from a third party (a clinician or a laboratory) about a person who did not submit anything, and creates a case the subject may never know exists. That inverts the default's role model — the default assumes an applicant or regulated party facing a decision-maker. Second, the government default states no rule about the relationship between a published output and its own source: for a rulemaking, the published instrument and the received comments are simply different documents. Here the published bulletin **is** the source, transformed, and the transformation is the safeguard. Treating them as equivalently sensitive breaks the row in one direction and treating the bulletin's low risk as inherited by the line list breaks it catastrophically in the other. That is a genuinely new privacy rule.

**Against (a), the hardest.** The subject-area charge is right that health topics appear across many siblings. It is wrong that the artifacts are the same artifacts. Three families exist only here:

1. **The notifiable-disease surveillance chain.** A statutory duty on a clinician to notify an authority about a named person, producing a receipt register, a line list, contact tracing, and an aggregate. `government.statistical-programme` cannot hold this: it starts from an instrument the authority designed and administered to a sampled or enumerated population; this starts from a report the authority did not solicit about a person who did not consent to a statistical collection. `government.emergency-management` cannot hold it either — their own node already concedes this, discriminating on operating mode, and a weekly notification cycle in an ordinary week has no activation.
2. **Register-driven call-recall.** An eligible-population register, an invitation, a reminder, and a **non-responder list**. The non-responder list is the fixture that proves the family: it is a named-person list that exists because something *did not happen*, and it discloses health status by omission. No other government sibling produces one. (Note the distinction from charge (e): a *file* defined by absence is fine and is in fact the most sensitive artifact here; a *row* defined by absence would be disqualifying. This row is not.)
3. **The health-protection instrument against a person or a setting.** An exclusion notice barring a named food handler from work pending microbiological clearance runs against a person's capacity to transmit, not against a licence condition or a release to an environmental medium. `government.permit-licensing` and `government.environmental-regulation` each own the frames that this one is not.

Verdict: the row is a workflow, not a subject. Accepted.

## Node test, argued in three legs

The government schema's **default template** is: activation from an evidenced authority-side role plus a bounded proceeding reference; no fields and no dimensions under PR-6; `potentially_sensitive` with protection for citizen casework, submissions, unsuccessful bids, evaluator declarations, investigations, enforcement, restricted statistics, election operations, security material, and pre-decisional work.

**Leg 1 — detection signals: DIFFER.** The default fires on role plus a proceeding reference. This row requires an additional structural anchor drawn from a closed set of workflow furniture — receiving-notification slot with case classification, contact tier, coverage numerator against an eligible-population denominator, case-definition criteria tiers, cold-chain excursion window with lot disposition, clearance criteria on an exclusion notice, small-cell suppression footnote on a periodic output. Every one of those is true of the file list in the JSON and false of the government schema's own sixteen fixtures. The row also carries `never_alone` entries the default does not: a disease word, an epidemic curve, a case-classification word, a laboratory result, a provider's own infection-control audit, an employer's exposure register. Each of those is a real file that would otherwise be misrouted here.

**Leg 2 — recommended dimensions: DO NOT DIFFER.** Both are `[]` under PR-6. Even in prose, the order I would recommend — bounded workflow, then exact reference, then work type, with a named person never a folder level — is the government default's prose order verbatim in effect. I record one nuance in `template.why` (aggregation state is a stronger separator than period, because the tiers share every other value and differ only in access), but a nuance inside an empty order is not a differentiating leg and I do not claim it as one.

**Leg 3 — privacy rules: DIFFER, materially.** Three rules the government default does not state: the aggregation boundary inside one workflow; the sensitivity of absence-defined person lists; and suppression of cross-file semantic joining on onset date, locality, premises, and school or workplace because their *combination* re-identifies in a small population. The third parallels `government.defence-veterans`'s suppression of unit and posting values, and I name the parallel deliberately — but the mechanism is different (small-number epidemiological disclosure, not the aggregation of a career), so it is not a copy.

Two of three legs. Accept.

## Files considered and rejected

Naming what this row does **not** hold is the part that keeps it honest.

- **`Vaccination Record - Mira Patel - childhood schedule.pdf`** — the recipient's own immunisation card. Retained in the JSON *as the collision fixture* precisely because it is the most convincing false positive: programme name, dose dates, lot and batch numbers, clinician signatures — every token this row's programme evidence carries. Discriminator: no eligible-population denominator, no call-recall slot, no coverage frame, no authority-side office block in a producing role. It is `medical.personal-health-records`. Screening invitations, result letters, appointment letters, and exemption certificates all fail on the same test.
- **`Infection Control Audit - Ward 6 - August 2026.docx`** — a hospital's own infection-prevention audit. Case counts, isolation decisions, control measures. Rejected because a provider auditing itself is not a public authority and bed-days are not a resident population. `clinical_practice.practice-administration`.
- **`Public Health Grand Rounds - measles resurgence.pptx`** — teaching slides containing a real epidemic curve and a real case definition, lifted from an actual investigation. Rejected: the framing is an audience, not an operation; there is no operational case data and no office block. `clinical_practice.teaching-material`.
- **`Disease Outbreak News - measles - August 2026.pdf`** — a downloaded international outbreak notice. Rejected: publication by a health authority is not custody by one. Reading Inbox.
- **A pandemic-era folder of forty saved PDFs from one browser session** — rejected as an activation basis: *“A session should never be treated as proof of topic”*.
- **A clinical guideline or care pathway** — rejected. Guidance issued *by the authority to providers* is in `work_types`; a guideline held by the clinician who follows it is `clinical_practice.protocol-guideline`.
- **A health-charity campaign report with the same indicator tables** — rejected. Public-benefit purpose is not public authority; `nonprofit.advocacy-campaign` owns it. This is the `must_consider_neighbors: nonprofit` item, resolved as a non-edge (see below).
- **An epidemiological research dataset and its ethics approval** — rejected. Secondary analysis of surveillance data is `research.dataset-analysis` / `research.ethics-compliance`. The authority may also be the researcher, but the research frame carries its own protocol and approval furniture.
- **A public-health job description, payslip, or staff roster** — rejected. Government as employer is never this schema; the government default already excludes it.
- **A health-programme budget line inside a council's estimates** — rejected. It is a committee paper with a health subject; `government.municipal-administration` owns the governance cycle.
- **A live surveillance database or notification portal account** — rejected as a node: a source system is not a file. A bounded export with a readable manifest is represented (`Outbreak OB-2026-118 - full case file export.zip`); connector ingestion is a later security decision.
- **Contact exports and address books of clinicians, laboratories, and school contacts** — rejected. Names in a directory do not evidence a workflow. `contacts` is consequently absent from `file_kinds.source_types`.
- **A disease-name gazetteer or pathogen list** — deliberately not invented. R4 owns gazetteer contents; `proposed_context_terms` is empty rather than a smuggled term list.

## The collision fixture

`Vaccination Record - Mira Patel - childhood schedule.pdf`, above. It is the fixture that would silently break this row if the row activated on programme vocabulary. What discriminates it is structural and cheap to check: **is there a denominator?** Programme administration always counts against an eligible population; a personal record counts nothing. A secondary discriminator is the direction of the office block — issuing *to* a person versus producing *for* the authority's own operation.

A second, subtler one is retained: `Complaint 26-4471 - odour - Mill Lane - caller details.docx`, taken verbatim from `government.environmental-regulation`'s node so the same bytes are named on both sides.

## Reciprocal boundaries

Eight `collides_with` edges, each stated in both directions with a shared fixture named on both sides.

- **`government.emergency-management`** — reciprocal of the one-way edge they already authored. I adopt their discriminator unchanged (operating mode: reporting cycle vs. declared activation with operational periods) and their fixture pair (a mass-vaccination clinic plan as programme document vs. run under an incident-command activation). Their side is landed; this closes the pair.
- **`government.environmental-regulation`** — reciprocal of their authored edge, same fixture, same test (permit/receiving-medium frame vs. health-protection investigation of exposed persons).
- **`government.permit-licensing`** — authored one-way here. Shared fixture `Food Premises Inspection - The Harbour Cafe - FHRS visit 2026-08-11.docx`; the test is what the contraventions are written *against* (an authorisation condition, or transmission risk to persons). This is the weakest boundary in the set and it becomes NJ-2 below.
- **`government.statistical-programme`** — authored one-way. Shared fixture `Weekly Communicable Disease Bulletin - Week 34 2026.pdf`; the test is whether an official-statistics production frame exists (instrument, collection round, methodology, microdata-access regime) or the aggregate is a by-product of operational surveillance.
- **`clinical_practice.patient-chart`** — authored one-way. Shared fixture `Notifiable Disease Notification - NOTIF-26-0912 - measles.pdf`, which exists as identical bytes in two custodies; the test is which block is the receiving slot and whether a register reference was assigned. Neither side erases the other: a laboratory result inside an outbreak group remains clinical evidence.
- **`medical.personal-health-records`** — authored one-way. Shared fixture is the collision fixture above.
- **`hr.workplace-health-safety`** — authored one-way. A workplace outbreak generates an exposure register, a contact list, and return-to-work clearances on both sides; the test is the holder and to whom the duty runs (employer to workforce vs. authority to population).
- **`government.social-services-casework`** — authored one-way. Both are named-person casework in one public office, both full of health material; the test is the case frame (opened because of transmission/exposure/screening status, vs. opened because of care, safeguarding, welfare, or entitlement need).

`also_holds_with` and `role_split` are **empty**, matching the landed launch row's reasoning and the government schema's own file: a template cannot author schema-level coactivation, and a fieldless schema exposes no role key to split on. Coactivation is instead recorded per-fixture as `also_schema` (medical, legal, photos).

### Neighbours considered that did NOT get an edge

- **`legal`** (named in `must_consider_neighbors`) — the exclusion notice is a statutory instrument and the FOI-adjacent disclosure of an outbreak file is legal work, but the government **schema** already carries a `collides_with: legal` edge covering exactly this. Repeating it here would be a duplicate, not a boundary. Recorded as `also_schema: "legal"` on the exclusion-notice fixture instead.
- **`nonprofit`** (named) — health charities are a real false friend and the schema's `collides_with: nonprofit` edge already states the owner-role test. Non-edge for the same reason.
- **`business_operations`** (named) — a private laboratory's or a vaccine supplier's own records are business operations; again already covered at schema level. The genuinely *new* commercial-side confusion is the employer one, which is why `hr.workplace-health-safety` got the edge instead.
- **`government.policy-development`** — a health needs assessment shades into health strategy. Not authored: the discriminator (population-assessment frame vs. options-and-decision frame) is thin, and I would rather leave it for R1c than assert a boundary I cannot test on a named file.
- **`government.grant-programme-administration`** — health grants are grants; the grant furniture decides it cleanly with no shared ambiguity.
- **`government.municipal-administration`** — a health committee paper is governance. Their own numbered-paper-with-resolution test (already authored against emergency-management) resolves it without a new edge.
- **`construction_property.site-health-safety`** — site safety is a contractor's duty on a site, not population health. No shared fixture.
- **`government.education-institution-governance` / `government.school-district-administration`** — a school outbreak generates records on both sides, but a school's exclusion register is the school's and the authority's outbreak file is the authority's; the holder test is unambiguous and no fixture is genuinely shared.

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false`, `proposed_context_terms: []`. All intentional.

The government schema declares no fields under PR-6 and a template may not branch on undeclared fields. Candidates I considered and **did not** mint: an aggregation-state or access-tier key, an outbreak or notification reference, a case classification, a programme round, a setting or premises, an eligible population, a coverage denominator. Each is a real organizing concept in this world; none is canonical; minting any of them here would be exactly the unilateral schema growth D1 and PR-6 forbid. They are routed to NJ-1 instead.

`record_type` and `institution` exist as canonical keys but are scoped to Finance; `purpose` is scoped to College Applications. Reusing them here would be a synonym raid, not reuse.

## Grouping without copied facts

Groups are bounded by an exact outbreak, notification, programme-round, or premises-case reference. Membership never copies a classification, a diagnosis, an identity, or a date onto a member: `RE Cluster at Mill Lane School... .eml` may join OB-2026-118 without its lab attachment acquiring a case classification, and the incident-call `.ics` joins without acquiring a severity. Four fixtures carry `group_without_copying_facts: true` for this reason. A shared premises name, address, proprietor, locality, or school is explicitly **not** membership evidence — that is the same combination the sensitivity rule suppresses for semantic joining, and allowing it in through grouping would defeat the suppression.

The archive manifest is read without unpacking, and the packet stays shallow while its internal access boundaries are unknown.

## Residual routing

Protected Records is the principal fallback and takes the whole person-level chain. Independent Records takes standalone notices, provider-action notices, guidance, and the person-free logistics log. Reading Inbox takes published bulletins and reports held for reading. Review Later takes material whose holder role, aggregation state, or operating mode is unresolved — including the coverage report and the needs assessment, both of which are legible but role-ambiguous. Temporary Screenshots takes a positively evidenced dashboard capture with no reference. Unsupported or Encrypted takes the surveillance-system backup without letting the word "surveillance" manufacture a sensitivity result. Both residuals named in the assignment (`Independent Records`, `Protected Records`) are used, and all six quotes grep back verbatim out of `00` line 120.

## Tensions I am not smoothing over

- The premises-inspection boundary against `government.permit-licensing` is decidable only by reading the document's working frame, and one real municipal service issues one document that serves both purposes at once. I have stated a test; I do not claim it is reliable.
- The aggregation boundary is this row's best argument and it is currently inexpressible except as prose, because there are no fields. A prose-only privacy rule is a rule the system cannot enforce, only recommend.
- Public-health authority status is genuinely hybrid in many jurisdictions — arm's-length agencies, health boards, quasi-public institutes, contracted providers exercising delegated statutory functions. The government schema's own open question already flags this; this row inherits it and cannot resolve it.

## NEEDS-JOSEPH

**NJ-1 — Aggregation state as a concept.** If PR-6 is lifted, decide centrally whether an aggregation-state or access-tier concept may exist (identifiable source / working list / published output), whether it may ever be destination-eligible, and whether it belongs on the government schema or as a universal privacy attribute alongside `sensitivity_status`. Alternatives: (i) a government-schema field, which limits it to this world though the same three-tier structure appears in statistics and casework; (ii) a universal attribute, which is more correct but touches every schema; (iii) leave it prose-only, which is the status quo and means the row's strongest rule is unenforceable. This row mints nothing.

**NJ-2 — Premises inspection ownership.** Adjudicate `Food Premises Inspection - The Harbour Cafe - FHRS visit 2026-08-11.docx` against `government.permit-licensing`. Alternatives: (i) route all premises inspection to permit-licensing and leave this row the person-level chain only — clean, but loses hygiene and food-borne investigation, which is core public-health work; (ii) split by frame, hygiene and communicable-disease inspection here and authorisation inspection there — correct in principle, unreliable in practice; (iii) accept dual candidacy and force user review — safe, noisy.

**NJ-3 — The notification form's two custodies.** Decide whether the clinician-copy / authority-receipt split against `clinical_practice.patient-chart` may be represented as a `role_split` at all, given that neither schema declares a role field to split on. Today it is a `collides_with`, which is a mutex and therefore slightly wrong: both copies legitimately exist, in different hands.

**NJ-4 — Hybrid public-health bodies.** Whether arm's-length health agencies, health boards, national institutes, and delegated contracted providers count as public authorities for activation, and whether that comes from a deployment-specific gazetteer or user confirmation. Inherited from the government schema's own open question; flagged here because this world has an unusually high proportion of them.

## Self-verification

- JSON parses (`python3 -m json.tool`).
- Key set matches `government.json` and the landed `government.*` siblings exactly.
- All six `design_cite` residual quotes and all five inline `00` quotations grep back verbatim (`grep -c` returned 1 for each; residual quotes are from line 120).
- Every `file_examples.source_type` is in `SOURCE_TYPES`; `contacts` was deliberately dropped from `file_kinds`.
- Every edge id is on the roster (`government.emergency-management`, `government.environmental-regulation`, `government.permit-licensing`, `government.statistical-programme`, `clinical_practice.patient-chart`, `medical.personal-health-records`, `hr.workplace-health-safety`, `government.social-services-casework`); every `falls_through_to` name is one of `00`'s residual templates.
- No fields, no proposed fields, no context terms, no thresholds, no handling classes, no folder paths written as facts.
- Only the two assigned files were written.
