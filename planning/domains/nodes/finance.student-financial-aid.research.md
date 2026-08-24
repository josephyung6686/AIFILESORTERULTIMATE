# finance.student-financial-aid — R1b lab notes

Date: 2026-08-22
Row: kind template, schema_id finance, launch placeholder, provenance inference.
Output: finance.student-financial-aid.json.

## Result

The node is retained. It is not a label for every file about paying for school. It is the
protected organizational situation formed by a financial-aid process and its education-loan
records: application or processed summary, school offer, verification, disbursement, and the
education-specific evidence on a loan document.

It passes the template node test for three independent reasons:

1. Its recognition is narrower than the Finance default. A school name, an amount, or the word
   award does not suffice; the record needs an aid-application, eligibility, offer,
   disbursement, or education-loan structure.
2. Its recommended order is shallower than the Finance default. institution then record_type
   keeps a mixed offer whole, while account_type is optional because one offer can contain
   grants, work-study, and loans at once.
3. Its privacy rule is materially different. A verification or aid packet can aggregate a
   student, parents or other contributors, tax records, identity evidence, income, assets,
   signatures, school choices, and loan balances. The combined packet must not become a cloud
   dossier.

The node does not claim launch-depth support. It remains a placeholder on a safety schema, with
useful detection and template guidance for later implementation.

## Sources used

### Binding repository sources

- planning/00-database-agent-product-design.md — read in full. It governs the observation/fact
  boundary, the four Finance keys, many-fact files, safety-before-model behavior, group
  non-propagation, template ordering, and residual homes.
- planning/01-product-design-structured.md — read only in the task-relevant rendering:
  Facts and facets, Grouping, template sections 5.3 through 5.9, residual sections 7.1 through
  7.9, and privacy section 8.4. The unnumbered 00 document wins.
- planning/prompts/ALIGNMENT.md — templates are situations rather than categories; work types
  are values; a template must differ from its schema default.
- planning/domains/_CONTRACT.md — entry shape, provenance, field-key, safety-domain, and closed
  edge rules.
- planning/domains/CONNECTION.md and CONNECTION-EXAMPLES.md — activation is not grouping;
  templates never copy schema fields; parent_id is browse-only; also_holds_with is schema-only;
  file kinds are never sufficient; residual names are closed.
- planning/domains/roster.json — confirmed the assignment and every edge target.
- planning/domains/canonical_fields.json — reused institution, account_type, tax_year, and
  record_type. No synonym was minted.
- src/evidence_shape/vocabulary.py — used only the closed SOURCE_TYPES.
- planning/overnight/council/DECISION-BRIEF.md — carried D6 snake_case and subject, D2's P7
  classification ownership, and J-IND's placeholder-depth discipline.
- Landed nodes inspected but not edited: finance.json, finance.loans-mortgage.json,
  finance.investment-brokerage.json, applications.scholarship-fellowship.json,
  applications.undergraduate-packet.json, applications.k12-admission.json,
  academic.study-abroad.json, and academic.transcripts-credentials.json.

### External primary sources

These sources were used to confirm current document names and concrete structures, not to add a
jurisdiction-specific schema:

- [Federal Student Aid — FAFSA Submission Summary](https://studentaid.gov/articles/fafsa-submission-summary/)
  confirms the current summary name and its eligibility, form-answer, school-information, and
  next-step sections. It also distinguishes the processed summary from a school's final aid
  offer.
- [Federal Student Aid — How financial aid works](https://studentaid.gov/sites/default/files/how-financial-aid-works.pdf)
  and [evaluating aid offers](https://studentaid.gov/articles/evaluating-financial-aid-offers/)
  support the offer fixture with grants, work-study, and loans as separate components.
- [Federal Student Aid — account records](https://studentaid.gov/articles/key-facts-accounts/)
  confirms that completed promissory notes and loan-counseling documents are account records that
  a user can view or download.
- [Federal Student Aid — preparing for loan payments](https://studentaid.gov/articles/6-ways-prepare-repayment-begin-again/)
  supports the servicer billing-statement fixture and the separation between provider, servicer,
  payment due information, and repayment account.
- [College Board — CSS Profile](https://cssprofile.collegeboard.org/about) confirms that CSS
  Profile is a common application for nonfederal institutional aid, which is why one record can
  list several institutions without any one of them becoming the issuer or a unique application
  target.

The U.S. names above are file fixtures for one jurisdiction. Other deployments will see bursary,
maintenance-grant, entitlement, sponsor, or ministry vocabulary. Those names are values and
recognition-catalogue content, never new fields or nodes.

No deferred catalogue was consumed. The node names rule families only: labelled structure,
word-boundary organization resolution, explicit role-labelled periods, and jurisdiction-injected
aid terminology. It authors no regex, gazetteer entry, detector rule, or score.

## Bottom-up file inventory

The JSON carries the full observation/fact split for seventeen concrete files. The set was chosen
to cover the process rather than only polished award letters:

- 2026-27 FAFSA Submission Summary.pdf — processed common-aid summary; several listed schools
  are references, not issuer or target facts.
- Financial Aid Offer - Harbour University - 2026-27.pdf — school offer with cost, grants,
  work-study, and loans; also carries academic school and term evidence.
- CSS Profile Acknowledgment 2026-27.pdf — common nonfederal aid application with multiple
  recipients; the admissions collision fixture.
- Verification Request - Missing Documents.eml — labelled mail fields plus a request for tax
  and identity evidence; the request does not copy facts from its attachments.
- Financial Aid Verification Packet.zip — archive manifest with mixed protected members,
  inspected without unpacking.
- Student Aid Disbursement Notice Fall 2026.pdf — scheduled and posted aid rows tied to a school
  account and enrolment period.
- Student Account Statement Fall 2026.pdf — bursar ledger where aid credits and tuition charges
  coexist.
- Direct Loan Master Promissory Note.pdf — education-loan origination record that also activates
  the Legal safety placeholder on its own execution evidence.
- Student Loan Statement Jun 2026.pdf — repayment record on the boundary with
  finance.loans-mortgage.
- Screenshot 2026-03-22 at 10.45.11.png — OCR-derived aid portal; capture evidence and aid
  evidence remain separate.
- Award Letter - Regional Scholarship 2026.pdf — looks like this node but belongs to the
  scholarship-application situation without account, eligibility, or disbursement structure.
- Erasmus Grant Award Letter.pdf — legitimately carries both aid and study-abroad evidence.
- 529 Plan Statement Fall 2026.pdf — one Finance schema, two template situations: investment
  holdings and education funding.
- Aid Offer Comparison.xlsx — user-authored multi-school comparison; no institution may be
  selected from the first or largest row.
- Aid Appeal - Special Circumstances.docx — unlabelled, highly sensitive prose requiring local
  or redacted interpretation.
- scan_0048.pdf — the sparse HW 3 analogue; it may join an aid group without receiving the
  group's fields.
- financial_aid_notice_protected.pdf — unreadable encrypted record; filename and session do not
  establish its domain.

The list covers labelled form structure, unlabelled prose, OCR, a mixed archive, email,
spreadsheet, an unreadable binary, a tempting false file, files that also carry another schema,
and a sparse context-supported member.

## Files considered and rejected

- FAFSA Student Aid Report 2026.pdf — not used as the current fixture. Student Aid Report is the
  older U.S. term; current official material uses FAFSA Submission Summary. A landed neighbor
  uses the older filename, so the reciprocal edge records the terminology tension without
  rewriting that node.
- Financial Aid Deadline.ics — a calendar reminder can retrieve the aid neighborhood, but it is
  not an aid record and calendar is a SOURCE_TYPE rather than a domain.
- Federal Student Aid Handbook.pdf — general reading material, not a person's aid record. Its
  honest residual is Reading Inbox if no research or course association exists.
- Scholarship Search Results.xlsx — research about possible awards, not an application, offer,
  account, or disbursement record.
- Tax Return 2025.pdf — may be submitted for verification, but it remains a tax record and may
  be a context-supported packet member without becoming student-aid material.
- Parent Contact.vcf — a contact record is privacy/search material, not a folder proposal and not
  an aid-domain signal.
- Loan Repayment Calculator.xlsx — a calculation with no issuer, borrower, account, or servicing
  structure is not a loan record.

## Facet decisions

fields is intentionally empty because this is a template. It references the Finance schema and
does not copy the schema's four rows.

The four inherited keys are used conservatively:

- institution is the financial or record issuer: aid administrator, school aid office,
  government provider, plan administrator, or loan servicer as the document itself establishes.
  A school merely listed as a recipient or comparison candidate is not institution.
- account_type holds the account or aid relationship, such as student aid, institutional aid,
  or education loan. It must not be forced to one value when a combined offer contains several
  aid forms.
- record_type holds the concrete document role from work_types.
- tax_year is legal only when the record explicitly labels the tax-information year. An aid year,
  award year, school year, statement month, or disbursement period is never tax_year.

The finance schema's pending account_holder proposal was not duplicated here. Student, parent,
contributor, beneficiary, borrower, and co-borrower distinctions are important privacy evidence,
but this template must not settle the shared field vocabulary or create person-name folder
dimensions.

## proposed_fields

One field is proposed for R1c:

aid_year, type string, destination-eligible.

Why it is not a synonym:

- tax_year identifies the tax source period and commonly differs from the period funded;
- application_cycle belongs to College Applications and stops describing the record after
  admission;
- term belongs to Academic and can be narrower than an annual award;
- creation_date and statement dates are universal evidence, not the funded period.

Why it is not used yet:

CONNECTION requires a template dimension to resolve through its schema. This template therefore
keeps aid-period text as raw evidence and a P9 grouping anchor and does not place aid_year in
dimension_order. R1c should cluster the proposal with period needs from insurance, benefits,
subscriptions, or grants before choosing aid_year versus a broader shared key.

## Dimension recommendation

Recommended: institution then record_type.

This is deliberately shallow. It keeps each actual issuer legible and lets combined aid offers
remain whole. account_type is optional when the corpus has distinct aid and education-loan
series; it is not a mandatory level because one offer can contain several account-like aid
forms. tax_year is excluded. aid_year would naturally sit between institution and record_type,
but cannot be used before canonical adjudication.

The recommendation is weakest for common application summaries and servicing transfers:

- a common summary names several schools but has one actual issuer, so the recipient list must
  not create school folders;
- an education loan can move between servicers, so institution-first can split one repayment
  lifecycle.

Those cases are why the JSON allows a packet or accepted group to remain flat and why the user may
reverse or remove dimensions.

## Connection audit

Seven landed nodes already pointed to this missing row. All seven are reciprocated:

- finance.loans-mortgage — aid and disbursement evidence versus repayment-account evidence;
- applications.scholarship-fellowship — applicant-side award process versus account,
  eligibility, offer, or disbursement structure;
- applications.undergraduate-packet — admissions addressee and cycle versus financial-aid
  process;
- applications.k12-admission — admission-role evidence versus household-finance and
  tuition-assistance evidence;
- academic.study-abroad — enrolment and credit evidence versus grant payment and account
  evidence;
- academic.transcripts-credentials — grades and registrar attestation versus aid amounts and
  disbursement;
- finance.investment-brokerage — holdings structure versus beneficiary-student and
  school-payment structure.

No also_holds_with edge is authored because that edge joins schemas only. Legitimate overlaps
are represented by schema activation already present on finance.json and by P9 group
multi-membership. role_split remains empty because field-role edges live in
canonical_fields.json; this template does not duplicate Finance's institution versus school and
target roles.

## Neighbors considered without a new edge

- finance.tax-filings — a tax return submitted for verification remains a tax record. Packet
  membership is not same-evidence confusion, so no collision was added.
- finance.payroll-received — a work-study pay statement is payroll after earnings occur. An
  offered work-study allocation is an aid-offer line. The structures are distinguishable and no
  mutex edge is needed.
- finance.personal-records — a student account statement can fit the Finance default, but the
  template distinction is a branch choice rather than an evidence-item collision.
- applications.purpose-packet — a verification archive can be purpose-coherent, but this
  template may not borrow the Applications-only purpose field. P9 can still form a packet from
  its anchors.
- academic.coursework — satisfactory-progress and enrolment references do not make an aid
  record coursework. No course-code-plus-context confusion was found.
- identity.core-documents — identity scans are common packet members, but the schema-level
  finance and identity safety relationship already owns the co-activation. The files are not
  confusable as document types.
- photos.screenshot-captures — the screenshot example carries capture and aid evidence; the
  schema-level Finance and Photos relation already owns that join.

## Privacy and D2

The node sets only sensitivity = potentially_sensitive. It assigns no handling class.
ClassificationRecord remains P7's authoritative gate under D2. Until policy permits otherwise,
paths, filenames, full text, OCR, raw financial values, identities, school lists, and group
memberships remain local.

The most important packet-level rule is non-composition: even if one redacted letter could be
eligible for bounded model review, the system must not concatenate a verification archive's tax,
identity, income, and household records into one model dossier. Local deterministic recognition
and abstention are successful outcomes.

## NEEDS-JOSEPH

- NJ-aid-1 — Time role. Accept aid_year as a canonical field, or fold it into a broader shared
  benefit or coverage period? Without a decision, the funded period remains evidence and a group
  label rather than a destination dimension.
- NJ-aid-2 — Student-loan servicing ownership. The roster hint includes servicing, while the
  landed finance.loans-mortgage node assigns principal, interest, payment, and servicer records to
  its repayment lifecycle. This node recommends overlapping P9 groups where education-purpose
  and repayment evidence are both present. Decide whether P10 routinely offers both branch
  templates or asks the user to choose one.

## Quote discipline

The JSON uses provenance inference, design_cite null, and no attributed quotation from 00.
Repository design statements are paraphrased here. Official terminology is linked to its primary
source. This keeps the verbatim-quote audit mechanically empty rather than relying on memory.
