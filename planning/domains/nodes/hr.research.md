# HR schema — J-DEPTH research memo

## Verdict

Retain `hr` as a **provisional schema anchor**, not as an employer-perspective alias. The node test passes only conditionally: the world has a candidate four-field structure (`workforce_member`, `workforce_unit`, `people_cycle`, `personnel_case`) and a materially stricter default for employee-identifying content. Because PR-6 defers the catalogue decision, `fields` remains empty and all four candidates stay proposals for R1c. If R1c decides those are merely generic person, organisation, purpose, and case aliases, this node should be refused rather than saved by the sentence “our firm is the employer.”

The default template is therefore also provisional. In prose it is programme/work type → genuine workforce unit or cohort → people cycle; a personnel case is local association only unless the user explicitly authorises a pseudonymous visible level. Employee name is never the default top dimension. The JSON correctly leaves `dimension_order` empty because proposed keys are not legal folder dimensions.

## Sources and method

The assignment was generated with `planning/domains/dispatch/make_prompt.py hr`; the standing source was `planning/domains/dispatch/RESEARCH-BRIEF.md`. For house structure and reciprocal seams I compared the landed schema anchors `career.json`, `business_operations.json`, `finance.json`, and `identity.json`; clinical privacy patterns in `clinical_practice.json` and its patient/case/safety children; the roster's eleven HR child templates; and already-authored neighbour edges that name those children. I used those files as schema idiom and collision evidence, not as authority for new canonical fields.

The design constraints carried through from the stamped prompt are: observations are not facts; extensions and source types never activate alone; placeholder schemas do not mint canonical fields; folder dimensions may use only destination-eligible declared fields; and protected content stays out of default cloud prompts. No detector regex, score, threshold, handling class, or roster edit is proposed.

## Node test, argued in full

### 1. Distinct schema structure

The strongest argument *against* HR is real. Career already holds “getting, holding and showing work,” including offer, agreement, performance review, separation letter, payslip-like evidence, and certificates. Business operations already holds how an organisation runs itself, including policies, budgets, projects, meetings, surveys, facilities, risks, compliance, and controlled records. Finance already holds account and transaction structure. A file does not become structurally new because the same company is now viewed as “our employer”; role perspective alone cannot license facts.

The residue that does not fit those schemas is a personnel-process relation. Its atoms are not company and role (career), or project/function and fiscal period (business operations), or institution/account/record type (finance). They are: the workforce subject, the internal population/unit, a recurring or bounded people cycle, and sometimes a personnel case. These are visible bottom-up in a payroll register, joiner tracker, calibration workbook, grievance pack, survey raw-data export, and incident file. Crucially, each candidate is role-qualified because the same bytes contain many other people, units, periods, and identifiers. A generic `person` or `case` would be worse than no key.

The field proposal is intentionally conservative:

- `workforce_member` is search/case association, not a default destination. A named employee is the subject, unlike the author, manager, witness, investigator, signatory, applicant, account holder, or client.
- `workforce_unit` is the population or establishment unit, not the legal entity whose operating record is in custody. It may become a dimension only in a genuinely multi-unit corpus.
- `people_cycle` is the named process instance that joins content-incoherent members. It is not a creation year or a generic fiscal period.
- `personnel_case` joins one grievance, disciplinary, capability, consultation, safety, or related case. It is proposed non-destination-eligible because even a case reference can disclose membership when placed beside a name.

This is the minimum coherent set. Adding salary, rating, demographic attribute, job title, manager, employment status, injury, allegation, or outcome would create a giant personnel form and multiply privacy risk. Those values may be observations, but the schema does not license them as facts.

### 2. Detection differs from neighbours

HR recognition requires one of three positive anchors: a structured personnel process; a workforce population/cohort; or an employee/personnel case. Employer letterhead, a person's name, a job title, and the word “employee” are expressly never-alone.

Career and HR compete on identical documents. `Offer Letter - Summer Analyst.pdf` belongs to career in the individual's own corpus when there is no roster, workflow, case, or employer-side process context. A folder containing the employer's offer templates, approval tracker, countersigned returns, and onboarding tasks may activate HR as a process; the one employee's copy does not. The same reciprocal boundary applies to performance reviews, separation letters, payslips, and training certificates.

Business operations and HR compete on shapes rather than extensions. `Project Phoenix resource plan.xlsx` has named people, allocations, start/end dates, and costs, but work-package and project-closure structure makes it delivery evidence. `FY27 establishment and headcount plan v5.pptx` has posts, grades, vacancies, reporting lines, and continuing capacity, so it is workforce design. `Employee Handbook v4.2.pdf` is the governing controlled policy; `Handbook acknowledgement - J Patel - signed.pdf` is person-side receipt. Neither row may swallow both merely because they arrived together.

Finance and HR meet in the payroll register. A general ledger export or bank statement remains finance. An employer-side register whose rows are workers and whose columns contain payroll components has a workforce-population structure. It can legally co-activate with finance because the same register supports ledger, cash, tax, and remittance evidence. One employee's payslip, however, is not the employer's population record.

Clinical privacy provides a further discriminator, not an excuse to duplicate facts. An occupational-health or injury packet can be both HR administration and clinical evidence. HR may recognize employee/process/case structure; it may not extract diagnosis or treatment as HR facts. Ambiguity protects and abstains.

### 3. Default template and privacy differ

Career's recorded prose is company → role or recruiting cycle → document type. Business operations is organised around project/function/body/contract/account and fiscal period. HR's candidate shape is programme/work type → population/unit → people cycle, with case association behind explicit policy. The parent dimension differs because “review form,” “acknowledgement,” or “response file” is meaningless without the process that produced it.

Privacy is not a decorative flag. Employee identity joined to pay, performance, allegation, health, absence, demographic cut, free text, or termination can be harmful. The row therefore prohibits employee name as an automatic destination and routes ambiguous person-side material to Protected Records. Aggregation does not automatically remove sensitivity: a small population cut or distinctive free-text response can re-identify a person. The schema invents no anonymity threshold.

This is materially different from the ordinary business-operations default, where many governing policies and published corporate records are not sensitive. The seam must remain member-level: a policy can be ordinary business material while its signed acknowledgements are protected HR evidence.

## Files considered bottom-up

### 1. `March 2026 payroll register - FINAL.xlsx`

Spreadsheet. Headers identify employee ID/name, department, gross pay, deductions, employer contributions, and net pay; rows are workers and the sheet carries employer control totals. Legal today: universal file, date, language, duplicate/version, and sensitivity facts only. Illegal: proposed HR fields, any folder path, or the claim that this is merely one employee's account statement. It co-activates finance. Without HR activation it falls to Protected Records.

### 2. `FY27 establishment and headcount plan v5.pptx`

Presentation. Current/proposed reporting lines, approved posts, vacancies, grades, sites, and headcount deltas. This is the positive collision against a project resource plan: continuing establishment supports HR; bounded work packages support business operations. Names on an org chart do not make every person a workforce-member fact. Without activation it is an Independent Record.

### 3. `New joiners - September intake tracker.xlsx`

Spreadsheet. One row per joiner; employee, start date, manager, department, induction, equipment, payroll, owner, and completion slots. It is purpose-coherent across HR, IT, payroll, and facilities. The IT handover task can carry business_operations too, but group membership must not copy the joiner's name onto every sparse receipt. Sensitive fallback: Protected Records.

### 4. `Annual review calibration - Customer Ops.xlsx`

Spreadsheet. Review period, business unit, employee, manager, proposed/calibrated rating, promotion recommendation, comments, and distribution formulas. It differs from corporate strategy or OKRs because the rows are employees and the outcome is a personnel decision. A goals workbook alone does not activate HR. Protected fallback.

### 5. `Grievance GRV-2026-014 investigation pack.zip`

Archive. Manifest lists form, acknowledgement email, interview notes, screenshots, findings, outcome, and appeal. The repeated case reference and process sequence support a purpose-defined group; the outer `.zip` does not. Statements retain their own speakers and allegations rather than inheriting all packet facts. Legal may also hold. Protected fallback and no default cloud dossier.

### 6. `Employee engagement survey raw responses.csv`

Spreadsheet. Survey items, response scale, business unit, site, tenure band, and free-text comment; rows are workforce responses. This is not generic market research merely because it is a survey. Removed names do not prove safety: unit cuts and comments can re-identify. Protected fallback.

### 7. `Incident 26-031 - warehouse fall report.pdf`

OCR. Labelled injured employee, site, date/time, witnesses, description, immediate action, investigation, and corrective actions. Absence of a text layer does not prove a scan; the recovered form structure does. The injury narrative cannot become a clinical diagnosis. Clinical may co-activate; Protected Records is the fallback.

### 8. `Handbook acknowledgement - J Patel - signed.pdf`

Text document. One employee, one policy version, signature, acknowledgement date. This is HR-side receipt; it is not the governing policy. Business operations can retain the policy-version relation without absorbing the employee record. Protected fallback.

### 9. `Offer Letter - Summer Analyst.pdf` — collision fixture rejected from HR

Text document. Employer letterhead, role, start date, compensation, and acceptance signature, but only one individual's copy and no employer-side workflow/population/case. This is career/employment evidence, not HR activation. It demonstrates why employer authorship is never-alone.

### 10. `Project Phoenix resource plan.xlsx` — collision fixture rejected from HR

Spreadsheet. Named people against work packages, allocation percentages, project roles, milestones, and a bounded closure. This is business_operations project delivery. Job titles, utilization percentages, and people columns do not convert a project plan into workforce administration.

## Other tempting files considered and rejected

- `Employee Handbook v4.2.pdf`: business_operations policy/handbook. It exists independently of any employee and carries owner, version, effective date, and review controls. HR may own acknowledgements or employee-specific application, not the governing bytes.
- `FY26 Operating Budget.xlsx`: salary/headcount lines are financial/operating evidence. HR needs row-level workforce population or compensation-process structure.
- `Customer satisfaction survey raw.csv`: generic research or business_operations/customer material. The word survey and a response scale are not HR.
- `Quarterly OKRs - Engineering.xlsx`: organisation/team strategy unless rows become individual performance decisions inside a review cycle.
- `Board minutes - restructure consultation.pdf`: business governance unless the same bytes carry the personnel consultation/case apparatus. It may co-activate, but the board shape does not surrender ownership.
- `ISO 45001 policy.pdf`: controlled compliance policy. HR workplace-safety administration begins with the employer's actual hazard, inspection, incident, training, or statutory process evidence.
- `Fit note - J Patel.pdf`: the individual's clinical/career evidence in isolation. Employer-side absence/adjustment workflow may co-activate, but HR cannot ingest diagnosis.
- `Salary benchmarking report.pdf` purchased from a consultancy: reference material unless the employer's own compensation planning cycle, decisions, or workforce population is evident.
- `Staff directory.vcf`: contacts data is protected and a contacts source type, not proof of a personnel process.
- `Screenshot 2026-03-14.png`: an opaque capture. Missing EXIF is not screenshot proof; OCR must reveal personnel-process structure before HR activates.

## Reciprocal boundaries and edge decisions

### Career

Career must not take employer-side rosters, multi-employee cycles, or formal personnel-case corpora simply because each row concerns a person's employment. HR must not take the individual's offer, agreement, review, payslip, certificate, or separation record merely because the issuer is the employer. Same bytes: `Offer Letter - Summer Analyst.pdf`, `Performance Review 2025 - J Patel.pdf`, and `Training Certificate - Forklift.pdf`. Employer process/population/case structure supports HR; personal employment evidence supports career. This is both a collision and a role split.

### Business operations

Business operations must not take establishment posts, calibration outcomes, joiner/leaver cycles, personnel cases, or signed acknowledgements. HR must not take governing policies, generic projects, budgets, surveys, risks, facilities records, meeting minutes, or retrospectives without workforce-process evidence. Same bytes: the two resource plans and the handbook/acknowledgement pair. Some packets lawfully co-activate, so both `collides_with` and `also_holds_with` are needed for different fixtures.

### Finance

Finance must not flatten the employer payroll register into generic account/transaction evidence; HR must not take the individual's payslip, bank statement, tax record, or benefits statement. Same bytes: the payroll register can carry both schemas. This is a collision at activation and an also-holds relation after both anchors are present.

### Clinical practice

No mutex edge is written at the schema root because an occupational-health or incident file can legally carry both worlds. HR owns workforce process/case structure; clinical owns diagnosis, treatment, fitness findings, and patient record semantics. The JSON records `also_holds_with` only.

### Legal

No mutex edge is written because agreements, investigations, consultation, grievance, and regulatory incident packets can simultaneously be personnel and legal records. Legal status is not a reason to strip workforce structure. `also_holds_with` is honest; template children may later add narrower collisions.

### Identity

No edge. A personnel file contains names, IDs, signatures, and sometimes passport copies, but identity-document protection is independently detectable and may co-exist at member level. The schema-level competition is weak: an employee number is expressly never-alone, and an actual passport activates identity on its own document structure. Adding a generic edge would overstate collision.

## Roster-child coverage

The schema anchor was authored before its eleven templates and supplies a common vocabulary/privacy boundary without pretending the templates are interchangeable. The children cover: employer payroll and benefits administration; organisation design/headcount; onboarding/offboarding; training/development; performance cycle; engagement survey; compensation planning; workforce analytics; DEI programme; employee relations; and workplace health/safety.

These are work types or organisational situations using one schema, not child schemas. Their detection differs enough to justify later template rows, but none may invent a second copy of fields. The schema's default is deliberately shallow. In particular, workplace safety and employee relations will likely have stronger case anchors; workforce analytics and engagement will have population-cut anchors; payroll has roster/run structure; and onboarding has checklist/process structure. Those differences belong in templates, not in additional schemas.

## Proposed-field adjudication

All four proposals are non-canonical and `fields` is empty.

`workforce_member` is the hardest privacy decision. A local fact can support search and association, but path exposure is dangerous. It is proposed destination-ineligible. If R1c prefers a universal subject-role model, it must still preserve the distinction between employee subject and author/manager/witness.

`workforce_unit` is not `organization`. The latter is already proposed by business_operations as custody/entity identity. A department, site population, cohort, establishment, or reporting unit is an internal grouping role. It is proposed destination-eligible only where the corpus genuinely spans several units.

`people_cycle` is a process-instance proposal, not a date synonym. If a universal `purpose` plus time model can represent “2026 graduate intake,” “March payroll run,” and “FY2026 annual review” without losing their labels, R1c may reject it; today no canonical key does so.

`personnel_case` is role-qualified to prevent collision with legal, clinical, support, and government cases. It is proposed destination-ineligible. If a universal case key is adopted later, the schema still needs a subject-role constraint and privacy rule.

## Privacy and residual behavior

Protected Records is the default when employee identity is joined to pay, performance, investigation, health/safety, absence, demographics, or free text and HR activation is missing or uncertain. Independent Records is appropriate for a durable standalone employment/admin file without a protected payload or employer-side process. A single sensitive file need not meet a normal group-size expectation before protection.

The schema does not claim that every HR-labelled document is sensitive. A public recruitment brochure, published DEI report, blank induction slide deck, or governing policy may be ordinary reference/business material. Sensitivity comes from the employee/population/process join and from content, not from the department name.

## NEEDS-JOSEPH

- **NJ-HR-1 — schema survival.** Approve the four-field role-qualified structure, or refuse HR. If refused, route programmes/policies/projects to business_operations, personal employment evidence to career, account material to finance, clinical facts to clinical_practice, and uncertain named-person material to Protected Records. Do not retain HR merely because the user's firm is employer.
- **NJ-HR-2 — visible case/person dimensions.** This row proposes both `workforce_member` and `personnel_case` as destination-ineligible. Alternative: permit a pseudonymous case reference only behind explicit policy. Cost: even a code beside surrounding names can disclose grievance, capability, injury, or health membership.
- **NJ-HR-3 — member-level dual-schema handling.** Decide whether one file can expose only policy/finance/operational facts to an ordinary group while HR/clinical/legal facts remain protected. Fixtures: payroll register, handbook acknowledgement, occupational-health packet, grievance archive.
- **NJ-HR-4 — aggregated data.** Confirm protection by default for survey, DEI, and workforce analytics unless a documented de-identification rule exists. Alternatives are unconditional protection, a future locally evaluated rule, or treating aggregates as ordinary business data. This row chooses unconditional default protection and invents no threshold.

## Consistency statement

JSON and memo agree: the node is retained conditionally; canonical `fields` is empty; exactly four proposed fields are recorded; no proposed field is used in `dimension_order`; ten concrete file examples include two explicit collision fixtures; career, business_operations, and finance receive reciprocal collision boundaries; clinical and legal receive co-activation boundaries; residuals are only Protected Records and Independent Records; privacy is `potentially_sensitive`; and NJ-HR-1 through NJ-HR-4 are repeated in the JSON ending.
