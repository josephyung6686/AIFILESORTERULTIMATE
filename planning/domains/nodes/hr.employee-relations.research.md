# Research memo — `hr.employee-relations`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/hr.employee-relations.json`
Roster row: template on the fieldless `hr` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accept the node.** `refuse_node: false`. It survives the charge on a positive structure that nothing else in the corpus has: the **served procedural apparatus** of a formal employment process. Not the words, not the subject matter, not the badness of the situation — the apparatus.

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `role_split: []`. All four are consequences of PR-6 and are argued below rather than assumed.

## The charge — the strongest case that this row should not exist

I put six charges to the row before writing anything. Two of them are serious and one of them nearly killed it.

**(a) It is a `work_type` VALUE of the `hr` schema, not a node.** This is the strongest charge and it is not hypothetical: `hr.json`'s own `work_types[]` array contains the literal string `"grievance, disciplinary, capability, investigation, consultation, or appeal record"`. My row's name is one enumerated value of a field the schema already declares. The dispatch prompt is explicit that work types are values and that asking for a child node per work type is the failure. On its face this row is exactly that.

*Answered.* A work_type value describes what a document IS. This row is not defined by a document kind; it is defined by a **multi-role procedure with a decision that has a lifespan**. Three structural facts do the work, and none of them is expressible as a work_type value:

1. **The role triad.** A grievance or disciplinary process requires an investigating officer, a decision-maker, and an appeal hearer who are *different people*, and the separation is the point of the procedure rather than an accident of staffing. `Grievance GRV-2026-014 - terms of reference.docx` names the first two in labelled slots; `Appeal outcome - GRV-2026-014.pdf` names the third and states he is not the original decision-maker. No other `hr` row, and no `business_operations` row, has three role-holders whose distinctness is load-bearing. A performance review has a reviewer. A payroll run has an approver. A project has an owner.
2. **The served instrument.** `Invitation to disciplinary hearing - J Patel - 2026-08-14.pdf` carries five things in one document: a named person, a dated and located hearing, the allegations, the right to be accompanied by a colleague or trade union representative, and the possible outcome. This is a *legal-effect-adjacent artifact addressed to one person*, and it exists in no other people process. An induction invitation, a survey invitation, and a calibration invitation are all invitations; none of them tells the recipient what could be done to them.
3. **The decision with a lifespan and an exit.** `First written warning - outcome letter - J Patel.pdf` carries a sanction, a period for which it stays live, and an appeal route with a deadline and a named hearer. A performance rating does not expire. A training completion does not expire into nothing. A case closes when appeals are exhausted, not on a date — which is why, in the JSON, `people_cycle` is argued to be inapplicable here.

A work_type value cannot carry a role triad, a service event, and an expiring decision. The value in `hr.json` is the *label* for this world; the world itself has structure the label does not.

**(b) It is a document type — an "investigation report".** *Answered.* An investigation report is precisely the file this row **cannot** activate on alone, and I have made that an explicit `never_alone`: the timeline-cause-findings-actions shape is identical to `business_operations.retrospective-postmortem`, which names the same fixture from its side. The row activates on the *packet's* apparatus, not on the report.

**(c) It is a lifecycle stage — the bad part of employment, between onboarding and offboarding.** *Answered, but this is the second serious charge.* A stage is not a node. The defence is that the row is not positioned in a lifecycle at all: a grievance can be raised in week two, a collective consultation touches people who are performing well, and a whistleblowing report may concern someone other than the reporter. What unifies the row is not a moment in a relationship but the fact that a **written procedure has been invoked and is now controlling the sequence of documents**. That is a state of the *process*, not a stage of the *person*.

**(d) It is defined by the ABSENCE of something — the absence of ordinary, harmonious management.** *Answered.* If that were true, the row's recognition would be a list of exclusions. It is not: every `deterministic` entry in the JSON is a positive conjunction of labelled slots, and I removed every candidate signal that read as "a management document that has gone wrong."

**(e) It duplicates its own schema's default template.** *Answered at length in the node test below.* This charge failed on all three legs.

**(f) It duplicates a neighbour.** *Answered.* Five neighbours already named this row before it landed, from their own sides, each with a different fixture and a different discriminator — `business_operations.meeting-record`, `.support-operations`, `.retrospective-postmortem`, `clinical_practice.case-conference`, `clinical_practice.malpractice-incident`. A row that four independent authors reached for and could not absorb is not a duplicate of any one of them. `clinical_practice.case-conference` says in terms: *"One-way edge; the neighbour has not landed and owes the reciprocal."* That reciprocal is now written.

**What I would have refused.** Had the row been "HR investigations" or "disciplinary documents", I would have refused it as a document type folded into `hr` plus `business_operations.retrospective-postmortem`. The row survives because the roster hint scopes it to the *process*, not the *paperwork*.

## The node test, argued in full

CONNECTION.md's test: a template exists only when its **detection signals**, its **recommended dimensions**, or its **privacy rules** differ from its schema's default. All three legs pass, which is more than the test requires.

**The `hr` schema's default template, stated exactly.** From `hr.json`: `dimension_order: []`, `time_first: false`, and a prose default held for R1c — *work type or named people programme first; then workforce unit or cohort when the corpus genuinely spans several; then people cycle; and only under explicit user policy a pseudonymous personnel case. Never lead with the employee's name.* Its recognition is seven deterministic bullets built around a workforce **population** or a **process instance**. Its privacy rule is that employee-identifying **content** must be protected before any cloud step.

**Leg 1 — detection signals differ.** The schema has one bullet covering this territory: an employee-relations *or workplace-safety* case form carrying a case reference plus subject, event or allegation, investigator/manager, and outcome or corrective-action slots. That bullet is a superset of two different worlds and it is under-specified in both. This row replaces it with eight signals the schema does not have, four of which are new in kind: the five-part served instrument; the investigator-separate-from-commissioner terms of reference; the sanction-with-a-live-period-and-a-named-appeal-hearer outcome; and the collective consultation apparatus (representative election, stated consultation period, selection pool and criteria). It also adds a discrimination the schema lacks — a case log's `case ref + status + handler` columns are *not* sufficient, because that is a service desk; the process-name and subject-employee columns are what discriminate. And it **splits** the schema's conflated bullet: allegation-and-conduct here, incident-and-hazard to `hr.workplace-health-safety`. That split is recorded as NJ-ER-2 for R1c.

**Leg 2 — recommended dimensions differ, and differ by contradiction.** The schema's first two prose levels are both actively wrong here, which is a stronger difference than merely adding one.

- *Work type must not lead.* One case migrates across work types while it is live: a grievance that produces a counter-disciplinary; a capability process that becomes an ill-health case; a disciplinary that ends in a settlement. A work-type first level would split one case's bytes across two branches mid-process — the one thing a case anchor exists to prevent.
- *Workforce unit must not lead.* `Customer Operations` plus a formal-process branch name re-identifies the subject in a small department without any name appearing.
- *People cycle does not apply.* A case has no wave, round, run, or annual instance. It has a notice date, a hearing date, a decision, an appeal window, and a sanction expiry — five dates with five different meanings, which is also why `time_first` is false.

The recommendation is therefore a **single pseudonymous case anchor with nothing above it**, function below it, and, absent explicit user policy, **no visible depth at all** — represent in place and let search carry the case. The schema recommends three levels then a case; this row recommends a case then nothing, or nothing at all.

**Leg 3 — privacy rules differ, and differ in kind.** The schema protects employee-identifying *content*. This row's claim is that the **existence** of the record is the disclosure: a directory listing that pairs a person with a formal-process word discloses that they are under allegation, to anyone who can see the listing, without opening a file. Two further rules are unique to this row and appear nowhere in the schema. First, **role asymmetry inside one case**: a witness's identity may need protection from the subject, a complainant's from the respondent, a whistleblower's from everyone — so one case-level protection is insufficient. Second, **non-migration**: a witness statement joins the *case*, never the witness's own personnel file, and case material must not flow outward into the subject's ordinary employment record. Neither rule is derivable from "protect employee-identifying content."

## Files considered and rejected

Naming what this row holds would not be research. These are the tempting false positives and the reason each one is not my evidence.

- **`Employee Handbook v4.2 - Disciplinary Procedure extract.pdf`** — the collision fixture, treated at length below. Rejected: a published clause, not a served instrument.
- **`Performance improvement plan - K Ruiz - Q3.docx`** — rejected when it carries the annual review-round header and no procedure citation. It is a `hr.performance-cycle` output. The row takes it only when a procedure is cited, a review period is fixed, and a consequence of failure is stated.
- **`Exit interview - K Ruiz.docx`** — rejected outright. A leaver's opinions are `hr.onboarding-offboarding`, even when they are complaints, unless a grievance was actually raised and a procedure invoked.
- **`Serious incident investigation - warehouse fall 26-031.pdf`** — rejected. Same investigation shape, same case-number shape, but the subject under review is an event and a place. `hr.workplace-health-safety`.
- **`Attrition and grievance rate by department FY26.xlsx`** — rejected. Aggregate counts of cases are `hr.workforce-analytics`; the aggregate is *about* cases and is not a member of any one of them. Small-cell re-identification is a real hazard here but it is that row's hazard, not mine.
- **`Anti-harassment training completion roster.xlsx`** — rejected. Training on the subject matter of this row is `hr.training-development`. The vocabulary overlap is total and the structure shares nothing.
- **`Code of Conduct - acknowledgement - J Patel - signed.pdf`** — rejected. It names a person and cites conduct, but nothing has been alleged. It is an onboarding or policy artifact.
- **`Union recognition agreement - Northgate Ltd and USW.pdf`** — *not* rejected, but flagged. It is a standing agreement rather than a process instance, and it sits at the edge of NJ-ER-1.
- **A live case-management system, an HR mailbox, an HRIS export** — rejected as source systems rather than files. A bounded export with a readable manifest is representable; live ingestion is a later connector and security decision.
- **`Contacts export - HR business partners.vcf`** — rejected. Investigator, companion, and representative names in a contacts file establish no case.
- **`Team offsite retro - what went wrong.docx`** — rejected. Named individuals plus a list of grievances in the ordinary-English sense, with no procedure and no subject-under-review. `business_operations.retrospective-postmortem`.

## The collision fixture

**`Employee Handbook v4.2 - Disciplinary Procedure extract.pdf`.**

This file contains every single word this row's vocabulary is built from — grievance, disciplinary, capability, investigation, suspension, hearing, appeal, gross misconduct — and it contains them at higher density than any real case file does. It contains the right-to-be-accompanied sentence verbatim. It contains the full sanction ladder including the live periods. It contains the appeal route. A recogniser built on words, on phrases, or even on the *presence of the procedural clauses* fires on it with maximum confidence, and would then file the company's staff handbook inside somebody's disciplinary record.

**What discriminates it:** it is addressed to nobody, it alleges nothing, and it carries a document version and an effective date instead of a case reference and a hearing date. The general form of the discriminator is **served versus published**. This is why `never_alone` contains "a right-to-be-accompanied *sentence*, a procedure citation, or a sanction ladder appearing as generic text" as a distinct entry from the vocabulary entry — the vocabulary entry alone would not have caught this file, because this file is not a bag of words, it is the real clauses.

Its correct home is `business_operations.policy-handbook`. The one exception, written into that edge: when the same extract is enclosed with a hearing invitation as an addressed enclosure, it becomes a case member — served, not published.

A second, weaker collision fixture is **`ER case log 2026.xlsx`**, whose layout is indistinguishable from a service-desk ticket export. It is discriminated by two columns rather than by shape: a process-name column drawn from the formal-procedure vocabulary, and a subject-employee column. `business_operations.support-operations` states the same discriminator from its side.

## Reciprocal boundaries

Eleven `collides_with` edges are written, each naming the same fixture on both sides. Five of them are reciprocals of edges a landed neighbour already wrote against this row; six are new from this side. Every id is on the roster.

| Neighbour | Shared fixture | Discriminator |
|---|---|---|
| `career.employment-records` | the warning letter; the settlement draft | possession of the apparatus only the employer holds — terms of reference, witness statements, panel papers |
| `business_operations.policy-handbook` | handbook procedure extract | served and addressed vs published and versioned |
| `business_operations.retrospective-postmortem` | the investigation report | what is under review: a person vs an effort, system, or event |
| `business_operations.meeting-record` | the hearing notes | procedural roles in the attendee list vs ordinary work discussion |
| `business_operations.support-operations` | the case log; the portal screenshot | employee-as-subject and process name vs fault and agent resolution |
| `hr.performance-cycle` | the PIP | procedure citation and stated consequence vs annual-round output |
| `hr.workplace-health-safety` | the OH report; any incident investigation | allegation/conduct/capability/attendance vs incident/hazard/place |
| `hr.onboarding-offboarding` | the settlement draft beside a leaver checklist | the negotiated instrument vs the exit administration |
| `legal.practice-matter-file` | the ET3 response | employer-as-party vs practitioner-representing-a-client |
| `clinical_practice.malpractice-incident` | a case against a clinician-employee | allegation about clinical care of a patient vs about employment conduct |
| `clinical_practice.case-conference` | a staff case conference / return-to-work | patient receiving care vs employee under employment apparatus |

Two of these deserve a note. `hr.workplace-health-safety` is the boundary the schema itself blurs, and the split is offered to R1c as NJ-ER-2 rather than imposed. `hr.onboarding-offboarding` is the hardest live case in the set — a resignation submitted with a grievance attached is genuinely both, and the JSON resolves it as a **reviewable candidate link, never a merge**, because merging would put a complainant's material inside a leaver's routine file.

## Neighbours considered that got no edge

- **`finance`** — named in `must_consider_neighbors` and deliberately **not** edged. A settlement payment, a back-pay award, or a tribunal award is financial evidence, but nothing in this row's apparatus is confusable with an account, a statement, or a transaction. The genuinely confusable payroll evidence is already owned by the `hr` ↔ `finance` collision authored at schema level on `hr.json` (`March 2026 payroll register - FINAL.xlsx`), and duplicating it here would add noise, not a boundary. If R1c disagrees, the fixture would be a remittance advice for a settlement payment, and the discriminator would be that finance holds the payment while this row holds the instrument that caused it.
- **`business_operations.risk-register`** — a people-risk line ("ER caseload rising") is a possibility, not a realised case. That row's own tense discriminator already settles it.
- **`hr.org-design-headcount`** — no edge for the *individual* half. For the *collective* half it is a real question and it is NJ-ER-1, not a silent edge.
- **`identity`, `medical`** — an identity document or a medical certificate inside a case packet is co-activation of its own schema, not a mutex. Membership never converts identity or clinical data into an hr fact.
- **`business_operations.compliance-audit`** — a whistleblowing report is handled under procedure here; a compliance investigation into the *organisation* is that row. No shared fixture that both sides would fight over, so no edge yet.

## Fields, proposed fields, and dimensions

`fields: []` is required: PR-6 leaves `hr` with no canonical field rows, and a template may reuse only what its schema declares.

`proposed_fields: []` is a deliberate choice rather than an omission. `hr.json` already proposes `workforce_member`, `workforce_unit`, `people_cycle`, and `personnel_case`; the brief says to reuse an existing proposal rather than mint a variant. This row **endorses `personnel_case`** as its primary anchor and endorses its proposed `destination_eligible: false`, for the sharper reason given in `sensitivity_why` — that the existence, not just the content, is the disclosure.

Three candidates were considered and rejected rather than minted:

- **`case_role`** (subject / complainant / witness / investigator / decision-maker / companion / appeal hearer) is the most tempting, because role asymmetry is the row's distinctive privacy rule. Rejected: a role is a property of a *person's appearance inside* a file, not a property of the file. One witness statement has a witness and a subject in it. A field cannot hold that, and a per-mention role belongs to P9's group representation, not to a schema key. This is folded into NJ-ER-4 instead.
- **`case_stage`** — rejected as a lifecycle value, exactly the thing the node test warns against.
- **`procedure_cited`** — rejected. It is genuinely diagnostic evidence and it is written into the recognition signals, but as a fact it would be a document reference rather than a filing dimension.

## Grouping without copied facts

The case reference is the join. `Hearing recording - 2026-08-21 - GRV-2026-014.m4a` and a sparse `notes.docx` carry `group_without_copying_facts: true`: they may join an accepted case group by membership without the subject, the case reference, the procedure, or the outcome being written onto them as facts. `Witness statement - A Okafor - GRV-2026-014 - signed.pdf` carries the same flag for the opposite reason — the danger there is not sparseness but leakage, and membership must not propagate the witness's identity outward.

Cross-case semantic similarity is suppressed. Allegations, manager names, procedure text, and companion names recur across unrelated cases without authorising any link between them.

## Open questions

- **NJ-ER-1 — does collective consultation belong on this row at all?** The roster hint puts it here ("an individual or their representatives") and the procedural spine genuinely matches: governing procedure, served notice, representation, numbered meetings, outcome. But the collective half has **no individual subject**, so its privacy calculus is materially weaker, and `Collective consultation - meeting 3 - minutes.docx` would be filed under a protection posture designed for allegations. Alternatives: (i) keep both halves here, separated by a work_type value — what the JSON currently does; (ii) split a collective row; (iii) move the collective half to `hr.org-design-headcount` and leave this row purely individual. I did not smooth this: it is the one place where the row's unity is argued rather than observed.
- **NJ-ER-2 — should the `hr` schema's single bullet conflating employee-relations cases with workplace health and safety be split?** This row argues yes and states the discriminator (allegation-and-conduct vs incident-and-hazard). Only R1c can change the schema.
- **NJ-ER-3 — if PR-6 is lifted, may `personnel_case` ever be destination-eligible for this row?** This row recommends a pseudonymous case level *only* behind explicit user policy, and no visible depth at all by default. The alternative is search-only representation in place, which is safer and less usable.
- **NJ-ER-4 — how does P9 record the grievance-and-counter-disciplinary candidate link, and witness-statement membership, without letting a witness's or complainant's identity propagate into the subject's group?** This is where the rejected `case_role` concept actually lives.

## Self-verification

- JSON parses (`python3 -m json.tool`).
- Key set matches the landed siblings and the `_CONTRACT` shape; no extra keys, none omitted.
- Every `file_examples.source_type` is in `SOURCE_TYPES`: `text_document`, `spreadsheet`, `ocr`, `archive`, `audio_video`.
- Every edge id checked against `planning/domains/roster.json`: all 11 collision ids, the 3 `also_holds_with` schema ids, and the 5 residual names all exist. The five residual names are `00`'s: Protected Records, Independent Records, Review Later, Unsupported or Encrypted, Temporary Screenshots.
- **No text is presented as a quotation from `00`.** The one quoted string in this memo is from `clinical_practice.case-conference.json`, attributed to it. No thresholds, no counts, no handling classes, no scores.
- No file example writes a folder path as a fact; every one carries an explicit `must_not_conclude: a folder path`.
- `never_alone` entries that trip real tempting files: the handbook extract is tripped by the vocabulary entry *and* by the generic-clause entry; the ER case log is tripped by the case-reference-shape entry; the investigation report is tripped by the timeline-cause-findings-actions entry; the portal screenshot is tripped by the missing-EXIF entry.
- Files written: `planning/domains/nodes/hr.employee-relations.json` and this memo. Nothing else. `planning/29-DOMAIN-OWNERSHIP.md`, the roster, `canonical_fields.json`, `check.py`, `src/`, and every neighbour node were read-only or untouched.
