# Research memo — `government.education-accreditation`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.education-accreditation.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, `launch: placeholder`

## Result

Accept the node, narrowly, as the **assessor-side review-cycle** template — and refer its schema placement to R1c as an open question rather than smoothing it over.

The row survives because one apparatus is real, recurrent, and found nowhere else in the government schema: a **peer-review team of volunteers recruited from other institutions**, with signed conflict-of-interest and recusal records, writing **findings keyed to a published, numbered standards edition**, in a **draft state under embargo** that becomes a **public decision** after the reviewed institution's response window. That combination — external volunteer assessors, criterion numbering, and a draft/final embargo seam inside one packet — is not produced by permit casework, professional licensure, inspection by a line manager, or an audit engaged by the audited party. It changes activation (received-versus-authored apparatus on a document the holder did not write), grouping (a cycle that spans years, with a draft/final version family), and the privacy rule (identical text confidential as draft, public as final).

## The charge — the strongest case that this row should not exist

I state the case against first, at full strength, because three of its four legs are genuinely strong.

**1. It is a work_type value of its own schema.** This is the strongest leg and it is verbatim. `government.json`'s `work_types` already contains the value: *"public education, accreditation, cultural-service, museum, library, archive, or records-management administration where the body sits inside the state."* The schema anchor has already enumerated accreditation as a value of the government work-type enum. Under the brief's own rule — *"work types are values"* — a row whose only content is one entry of its parent's enum is a category error, and this project's recorded failure mode is exactly minting nodes to save legacy ids (here, `acad.accreditation-institutional`).

**2. It is an organisation kind, which is never-alone evidence.** "Accrediting body" names a type of organisation, and `00` forbids an institution name as sole proof. WSCUC, ABET, AACSB, Ofsted, QAA appear on letterheads, in footers, in PDF producer strings, on certificates, on marketing pages, and in the reviewed institution's own folder names. If the row's activation reduces to recognising those names, it can never activate legally.

**3. It is a duplicate of neighbours.** Four candidates compete for the same bytes. `government.professional-regulator` also publishes standards, inspects, and sanctions. `government.permit-licensing` also receives an application, evaluates it, and issues a decision with conditions. `business_operations.compliance-audit` also produces evidence requests, criterion-numbered findings, a management response, and a final report. `nonprofit.standards-body` also writes numbered standards and certifies against them — and, decisively, **most real education accreditors are private membership associations, not public bodies at all**, which makes the government schema look like the wrong home before the row is even argued.

**4. It is defined by the absence of something.** "Assessor side" is a negation: not the institution's side. A row whose entire content is *the other end of a relationship a neighbour already holds* is a `role_split` edge on that neighbour, not a node of its own.

### Defeating the charge

**Against leg 1 (work_type value).** The enum entry names a *function label*; this row is the **proceeding shape** underneath it. The government default's recognition asks whether a public body is exercising a public function — a test that cannot separate the accreditor's file from the licensing office's, and that gets the decisive fixture backwards: a received self-study is not the holder exercising a function, it is a document authored by someone else, and the holder's authority-side evidence is the *wrapper*, not the content. This row's deterministic signals are written about the wrapper, the reviewer apparatus, and the draft/final seam. None appears in the anchor's deterministic list, which is organised around legislature, rulemaking, procurement, permits, FOI, statistics, elections, and casework shapes. The difference is in signals, not in a value.

**Against leg 2 (organisation kind).** Conceded, and encoded rather than argued away. Twelve `never_alone` clauses are written; the first four are body name, accreditation vocabulary, standards PDF, and institution name. The row activates from none of them, singly or combined. What activates is apparatus: submission identifier + received stamp + reviewer assignment; or criterion numbering + team severity labels + addressee institution; or a decision letter over a commission signature with a next-review date.

**Against leg 3 (duplicate).** Each competitor gets a named fixture and a stated discriminator in `collides_with`. `professional-regulator` — the judged subject is an institution or programme here, a named individual practitioner there. `compliance-audit` — who engaged whom: own cycle against own published standards, versus engaged by the audited party. `school-district-administration` — whether the reviewer sits inside the reviewed body's management line. `nonprofit.standards-body` — the education review cycle with volunteer peers and a reaffirmation term; this is the weakest of the four and is escalated as NJ-1 rather than asserted. `permit-licensing` is deliberately given no edge; see non-edges.

**Against leg 4 (defined by absence).** Half-conceded, and answered with a `role_split` to `government.education-institution-governance`. But the assessor end holds artefacts the institution end never has: a reviewer roster with recusals, reviewer training material, a cross-institution annual data collection on the body's own instrument, complaint intake against institutions, and the commission's deliberation record. A row with exclusive artefacts is not a negation.

**Verdict: accept, with NJ-1 open.**

## The node test, argued in three legs

`CONNECTION.md` §2 admits a template only when its **detection signals**, **recommended dimensions**, or **privacy rules** differ from its schema's default template. The government anchor's default is quoted from its own file:

> *"an evidenced public body acts as legislature, regulator, decision-maker, programme administrator, records holder, statistical authority, election administrator, or citizen-casework office; submissions and named-person case material are protected by default"*

with `template.dimension_order: []`, `time_first: false`, and prose order *"authority-side function or bounded proceeding/case/programme first, then an exact reference or cycle, then work type."*

**Leg 1 — detection signals: DIFFER.** The default asks a role question about the holder. This row asks a custody-and-apparatus question about a document the holder did not author. Three signals here have no counterpart in the anchor's deterministic list: (a) the received-wrapper test that separates a submitted self-study from an authored one; (b) the volunteer peer-reviewer apparatus — a roster naming evaluators by *home institution*, with recusals — which is structurally impossible in staff-run casework; (c) the draft/response/final triple keyed to identical criterion numbering, which is a version family the anchor never describes. Conversely, the anchor's decisive signals (bill identifiers, proposed rules and comment dockets, tender and bid packets, ballot accounting, FOI disclosure schedules) do not fire here at all.

**Leg 2 — recommended dimensions: DIFFER in prose, empty in serialization.** Both are `[]` under PR-6, so this leg cannot carry the node alone; I say so plainly rather than counting it. The prose differs in a way that matters if fields are ever ratified: the anchor recommends **function first**, but here function is *invariant* — the holder does one thing, so a function level would create a single branch holding everything. The organizing anchor is instead the reviewed institution or programme plus its cycle. The row also carries two prohibitions the anchor does not state: the reviewing body's own name must never be a dimension (invariant across the whole corpus), and a reviewer's name must never be a dimension (named people are never-alone, and a reviewer-named branch discloses assignment). `time_first: false` is inherited and re-argued: one cycle runs from self-study to commission action across calendar years, and `00` says *"For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."* Any order stays editable: *"The system recommends an order based on the domain template, but the user can reverse, remove, add, or flatten dimensions."*

**Leg 3 — privacy rules: DIFFER.** The anchor already protects submissions and named-person casework, so "confidential submissions" alone would be inherited, not distinct. The distinct rule is the **embargo seam**: the same finding text is confidential as a draft team report and public as a final commission action, and both live in one packet under near-identical filenames. Publication state, not content, decides sensitivity — so a content-similarity or filename heuristic will get it backwards. Two further rules are specific to this row: an institution's name is not safe in a branch label while a show-cause or probation case is open (the status may not yet be published), and a peer reviewer's identity plus assignment is sensitive even though the reviewer is not the subject of the review. `00` governs the posture: *"Privacy policy must be enforced before content reaches any model or external connector."*

Two legs differ substantively and the third differs in prose only. The node stands.

## Evidence base — named real document types

No design document describes accreditation, so this row's world-evidence is **named real artefact types**, marked as such, not quotations. Design quotations are used only for residual definitions, dimension policy, extension policy, session policy, and privacy — each grep-verified verbatim from `planning/00-database-agent-product-design.md` before being written.

Named standards editions whose numbering appears verbatim in findings: WSCUC **Standards of Accreditation** with its **Criteria for Review**; ABET **Criteria for Accrediting Engineering Programs** (Criterion 1–8) and its **Self-Study Questionnaire**; Middle States **Standards for Accreditation and Requirements of Affiliation**; the AACSB business standards; the **UK Quality Code** (QAA); Ofsted's **Education Inspection Framework**.

Named artefact types across one cycle: eligibility/candidacy application; **self-study** or institutional self-evaluation report with exhibit index; **evaluation team report** / **draft statement**; the institution's **response to the draft statement** (the due-process step); **final statement**; **commission action letter** (initial accreditation, reaffirmation, continued with interim report, deferral, **probation**, **show cause**, withdrawal); interim report and mid-cycle review; annual institutional data submissions; **substantive change** prospectus; third-party comment and complaint intake; peer-reviewer rosters, training, and conflict-of-interest disclosures.

**Inference (marked):** that the received-wrapper, the volunteer-peer roster, and the draft/final embargo are the three discriminating shapes is my inference from those artefact types, not a design statement. It is falsifiable — an accreditor using only salaried inspectors and publishing its drafts would defeat the second and third.

## Files considered and rejected

A row that only lists what it holds has not been researched. These are the tempting false positives, each with the reason it is not this row's evidence.

- **`WSCUC Standards of Accreditation 2023.pdf`** — the most tempting file of all: accreditor's name, imprint, and the exact criterion numbering the real findings use. It is *published*. Publication by the body is not custody by the body, and the reviewed institution keeps byte-identical copies while preparing. → Reading Inbox.
- **`Self-Study - Riverbend State University - draft 7 tracked.docx`** — the collision fixture proper; see below. → Review Later.
- **`Accreditation Readiness Assessment - prepared by Meridian Advisory.pptx`** — a consultancy's gap analysis keyed to the same criteria as a genuine team report. Prepared-for / prepared-by blocks plus scope, fee, and milestone slides mark an engaged service, not an assessor's finding. Criterion numbering is not evidence of custody. → Review Later.
- **An accreditation certificate, badge, or seal image held by an institution or graduate** — the recipient of an outcome is not the assessor. → Independent Records.
- **A programme accreditation confirmation in a learner's credential folder** — the individual's record; `academic.transcripts-credentials` owns it, recorded as `role_split` rather than collision.
- **`Reviewer Training Webinar - 2026 cohort.mp4`** — assessor-side but institution-free; body operations, not any cycle, and must not be grouped into one. → Reference Clips.
- **A staff employment contract, payslip, or calendar naming the accrediting body** — government-as-employer, excluded by the schema's own never-alone list.
- **The accreditor's own petition for recognition to a recogniser or ministry** — the holder is here the *regulated party*, not the assessor. Kept as a work-type value, but it must not activate from assessor-side apparatus, because none is present.
- **A student essay, thesis chapter, or news article about accreditation** — dense in the vocabulary, zero apparatus. Academic or Reading Inbox.
- **A live accreditation management system, portal account, or reviewer database** — a source system, not a file node. Only a bounded export with a readable manifest is represented.
- **Individual exhibit members inside `Riverbend Exhibits 2026 - evidence room.zip`** — audited financials, board minutes, de-identified student work. Each keeps its own schema evidence; membership copies no institution or cycle label onto them, and the archive is not unpacked to raise confidence.

## The collision fixture

**`Self-Study Report - Riverbend State University`** — the same prose, in two custodies.

On the assessor's side it arrives wrapped: a portal submission identifier, a received date stamp applied by a system other than the author's, a transmittal sheet naming a staff liaison and a team chair, and an accreditor-side institution reference. On the institution's side it exists as `Self-Study - Riverbend State University - draft 7 tracked.docx`: tracked changes and comment threads from the institution's own named staff, internal committee headings, gap lists and to-do markers where evidence is still missing, and **no** submission identifier, received stamp, or reviewer assignment.

**What discriminates:** the wrapper, not the body text. Document properties are unreliable here — the received copy's author metadata still names the institution, because the institution wrote it. Standards numbering is present in both. The accreditor's name is present in both. Folder names are identical on both sides ("Accreditation", "Self-Study", "2026 Review"). Only the received-side apparatus separates them, and when it is absent the file must go to Review Later rather than be guessed.

A second collision fixture guards the audit seam: **`Riverbend Exhibits 2026 - evidence room.zip`** looks exactly like an external audit's evidence request response. What discriminates is whether the requesting instrument is the body's own published education standards edition on a review cycle, or an engagement letter from the audited organisation.

## Reciprocal boundaries

Every boundary is stated in both directions and names the same fixture on both sides. These are **recommendations to R1c** for the neighbour's side; I have edited no neighbour file, and no landed node currently mentions this id (`grep -rl "education-accreditation" planning/domains/nodes/` returns nothing).

1. **`government.education-institution-governance`** — fixture: the self-study. *This row:* the received copy, with submission wrapper and reviewer assignment. *That row:* the authored copy, with the institution's own tracked drafts and committee apparatus, plus the decision letter as something **received**. Also a `role_split`: assessor versus reviewed party, same review, two custodians. Recommend R1c mirror both edges.
2. **`nonprofit.standards-body`** — fixture: a numbered standards edition plus a criterion-keyed finding plus a decision letter. *This row:* an education review cycle — reviewed institution or programme, volunteer peer team, reaffirmation term, institution-facing outcome. *That row:* standards writing, product or management-system certification, company accreditation, or any standards work without an institutional education review cycle. Recommend R1c mirror, **and** resolve NJ-1 at the same time, because the private-association case makes this the load-bearing edge.
3. **`government.professional-regulator`** — fixture: a criterion-keyed inspection report with a sanction letter. *This row:* the judged subject is an institution or programme; assessors are external volunteers. *That row:* the judged subject is a named individual practitioner — registration, fitness to practise, discipline — with staff investigators and person-keyed case files. Recommend R1c mirror.
4. **`business_operations.compliance-audit`** — fixture: the evidence-room archive and the criterion-numbered finding with a management response. *This row:* the reviewer applies its own published education standards on its own cycle and decides an accreditation status. *That row:* the audit is engaged by, or internal to, the audited organisation — the consultancy readiness deck falls here. Recommend R1c mirror.
5. **`government.school-district-administration`** — fixture: a school evaluation report with numbered judgements. *This row:* the reviewer sits outside the reviewed body's management line. *That row:* a district or system evaluating schools it operates. Recommend R1c mirror.

## Neighbours considered that did not get an edge

- **`government.permit-licensing`** — the strongest omission, and deliberate. Both receive an application, evaluate it, and issue a conditioned decision. But permit casework has no volunteer peer team, no applicant-authored self-study against a numbered standards edition, and no draft/response/final embargo. A fifth mutex would blur the discriminator the other four carry; R1c can add it if a landed sibling shows a true same-bytes contest.
- **`legal`** — the schema anchor already collides with legal on enforcement and decision bytes. Withdrawal appeals and litigation are the legal row's evidence, not a same-bytes contest here.
- **`academic.transcripts-credentials`** — a `role_split`, not a collision: the learner's copy of an accreditation confirmation is a credential record.
- **`research.ethics-compliance`** — IRB review also has submissions, external reviewers, and decisions, but its subject is a study protocol, not an institution's degree-granting quality. No contest for the listed fixtures.
- **`career.credentials-licenses`** — an individual's licence tied to an accredited programme. Person-side; excluded by the same never-alone rules.
- **`nonprofit.member-association`** — accreditors are often membership bodies, so dues notices and member directories co-occur. Association operations, not review records; no fixture contest.
- **`photos`** — the portal screenshot is a per-fixture coactivation (`also_schema: "photos"`), not a mutex.

`also_holds_with` is empty at node level: the government schema exposes no field, so this template cannot author schema-level coactivation. Coactivation is recorded per-fixture instead, matching the landed launch rows.

## Fields and proposed_fields

`fields: []`, `proposed_fields: []`, `template.dimension_order: []`. This is required, not a shortfall: PR-6 leaves the government schema fieldless and D1's deferral stands, so a template on it can declare nothing.

Candidates considered and rejected against `canonical_fields.json`:

- **`institution`** — exists but is Finance-scoped. Reusing it would silently extend one schema's key into another, and it is ambiguous here: reviewed institution, reviewer's home institution, and reviewing body would all compete for it.
- **`school`** / **`term`** — Academic keys. `school` is tempting for the reviewed institution, but Academic's `school` means the learner's or teacher's institution; borrowing it would let a review packet contaminate coursework grouping. `term` is an academic term, not a review cycle.
- **`record_type`** — Finance-scoped enum. **`work_type`** — Academic-scoped; this row's work types are written as values in the government anchor's own `work_types[]`.
- **`purpose`** — scoped to College Applications. Purpose is genuinely live here (a cycle packet is purpose-coherent and content-incoherent, exactly as `00` describes for an application packet), but the key is not available to this schema.
- **New keys** for reviewed institution, cycle, standards edition, criterion, review stage, or decision outcome are **not minted** — that would build the deep industry taxonomy J-IND defers and pre-empt R1c. Listed here as concepts for adjudication only.

## Grouping, and residual routing

A candidate group is bounded by an exact, repeated cycle or case reference — never by institution name, accreditor name, standards edition, date proximity, or semantic similarity. Sparse members (a bare enrolment table, a calendar event, an unlabelled exhibit) join through that exact reference while `group_without_copying_facts` stays true: membership creates no institution, cycle, or decision fact on the member. This is the row's `HW 3.pdf` case — activation and grouping are separate decisions. The draft/final pair is one version family sharing criterion numbering across a response window, but the two are **not** interchangeable for privacy: a group summary must not surface draft text because the final is public.

Protected Records is the principal fallback — received self-studies, exhibit sets, embargoed drafts, reviewer disclosures, named complaints, institution-level data. Independent Records takes a standalone published decision or certificate; Reading Inbox takes standards editions and sector reports held for reading; Review Later takes criterion-keyed documents whose custody side is unresolved; Unsupported or Encrypted takes unreadable archives and portal binaries; Temporary Screenshots takes an evidenced screen capture whose OCR yields no cycle; Reference Clips takes reviewer training media with no institution. No residual is a schema fact or a permanent destination mandate.

`CONNECTION.md` and the stamped prompt did not disagree anywhere this row touches. `ALIGNMENT.md`'s prohibition on inventing a schema tree is respected: no child node was proposed for any work type.

## NEEDS-JOSEPH

**NJ-1 — schema placement (blocking for R1c).** Most United States education accreditors, and many quality-assurance agencies elsewhere, are **private membership associations**, not public bodies. The government schema's own never-alone list excludes "a charity, campaign, union, faith body, standards body, accreditor, or membership association" unless public-body status is independently evidenced — so the schema anchor arguably excludes the typical occupant of this row. Alternatives: **(a)** keep the row on `government` and treat the accreditor's quasi-public function as sufficient, accepting that recognition must then evidence public-body status it usually cannot find; **(b)** move the row to the `nonprofit` schema beside `nonprofit.standards-body`, and leave state approval boards and national inspectorates to `government.professional-regulator` and `government.school-district-administration`; **(c)** split by the reviewer's own status — public inspectorate under government, private accreditor under nonprofit — at the cost of two rows for one apparatus. My recommendation is (b) or (c); I have written (a) because the roster assigns it, and flagged it in `open_question` on the node.

**NJ-2 — the embargo seam and P7.** Draft findings and the final decision are the same text in two publication states. This row records only `potentially_sensitive` and cannot express "confidential until superseded". P7 must decide whether publication state is representable at all, or whether the whole cycle packet simply stays protected.

**NJ-3 — institution names in branch labels.** An institution name in a visible branch discloses that an accreditation case exists, which for an open probation or show-cause matter may not yet be public. Decide whether assessor-side packets require redacted display labels with local-only aliases, as `legal.practice-matter-file` asks for client and matter names.

**NJ-4 — reviewer identity.** Peer reviewers are named people who are neither the holder nor the subject. Decide whether reviewer names may ever appear in group summaries, and confirm the prohibition on reviewer-named dimensions is a policy rather than only this row's recommendation.

**NJ-5 — cross-institution collections.** The annual data submission spreadsheet holds many institutions in one file. Decide whether such a file may join a per-institution cycle group at all, or must stay with its collection instrument; I have written the latter.

## Self-verification

- JSON parses; top-level key set matches `government.json` exactly, including `proposed_context_terms`.
- Every `file_examples.source_type` is in `SOURCE_TYPES`; every `falls_through_if_inactive` and `falls_through_to.residual_template` is one of `00`'s nine residual names.
- Every neighbour id in `collides_with` and `role_split` was confirmed present in `planning/domains/roster.json`.
- Every quoted span was grep-verified verbatim against `planning/00-database-agent-product-design.md` before use. No quotation is attributed to `00` that was not matched.
- `fields`, `proposed_fields`, and `dimension_order` are empty; no canonical key is reused or minted. No thresholds, no counts, no handling classes.
- Only the two assigned files were written.
