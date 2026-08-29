# `clinical_practice.practice-administration` — lab notes (template row, deepened to J-DEPTH)

**Depth: J-DEPTH** (deepened 2026-08-25).

Verdict: **KEPT, but narrowed materially.** This is not *running a clinical practice as a business*.
It is the regulated clinical-operation seam that ordinary business administration does not model.
`fields: []`; `proposed_fields: []`; no clinical field keys are minted in this pass.

## What changed at the top level

The gist draft was right to disclaim contracts, vendors, facilities, payroll, and staff policies, but
its title and legacy hint still invited those files back in. This pass makes the boundary testable.
The row stands only where at least one of two structures is present:

1. **Administrative form, clinical population:** one operational document contains repeated
   third-party subjects or a clinical cohort—clinic lists, recall searches, appointment/DNA exports,
   row-level activity returns. These files look like schedules and spreadsheets but disclose
   healthcare relationships at scale.
2. **The practice as regulated provider:** the subject of registration, inspection, conditions, or an
   action plan is an organisation providing care, not one practitioner's entitlement to work. This is
   an organisation-versus-individual role distinction, not a healthcare-industry keyword.

Everything else falls away. A cleaning contract, facilities log, payroll summary, ordinary staff
rota, supplier review, generic policy, and ordinary management minute are business, HR, or facilities
material exactly as they would be for a bakery. `Clinic` in the holder name changes no structure.

The JSON was written first. It retains all 27 universal keys, keeps `fields: []`, and corrects a stale
edge to the now-refused `clinical_practice.licensure-credentialing`: individual professional licences
route to `career.credentials-licenses`; the practice's provider registration remains here.

## Sources actually used

### Binding local authority

- `planning/00-database-agent-product-design.md`, quoted verbatim only.
- `planning/prompts/ALIGNMENT.md`.
- `planning/domains/_CONTRACT.md`, `CONNECTION.md`, and `CONNECTION-EXAMPLES.md`.
- `planning/domains/canonical_fields.json`, `roster.json`, and the stamped assignment produced by
  `planning/domains/dispatch/make_prompt.py clinical_practice.practice-administration`.
- `planning/domains/dispatch/RESEARCH-BRIEF.md` and `DEEPEN-ADDENDUM.md`.

### Anchors and neighbours read, and not edited

- `clinical_practice.research.md`: family anchor, including its two-role, multi-subject, and
  protect-before-model arguments and empty default dimension order.
- `clinical_practice.patient-chart`: one-subject longitudinal accumulation.
- `clinical_practice.referral-correspondence`: directed clinical correspondence workflow.
- `clinical_practice.pharmacy-operations`: regulated medicine custody/supply accountability.
- `clinical_practice.licensure-credentialing`: J-DEPTH refusal proving regulator industry is only a
  value for an individual's credential.
- `business_operations.support-operations`: queue/case-register structure that survives despite
  generic operational vocabulary.
- `business_operations.facilities-workplace`: asset-plus-obligation, access, and space structures,
  irrespective of the occupier's industry.

Named document types below are bottom-up file-shape inferences. No claim that a document type exists
comes from invented product-design prose.

## The schema default this template must differ from

The clinical anchor's prose recommendation is professional situation, then document function; never
a patient or diagnosis level, and not time-first. Its JSON dimension order is empty because the
placeholder schema declares no fields and visible patient-shaped folder labels would reveal the
protected fact.

This row cannot distinguish itself by dimensions. Its `template.dimension_order` remains `[]`, and
`time_first` remains false. The natural prose order—regulated operational function, then period—cannot
become a folder template in this pass. The only possible node-test support is distinct detection or
privacy structure.

The general record-domain principle is quoted exactly in the JSON and applies here:

> “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

No person-shaped level is proposed. The design also says:

> “It should avoid using authorship or creator identity as a destination dimension.”

The third-party subject is stronger still: a patient name or condition in a folder path would publish
the fact the protected state is meant to contain.

## Node test, leg by leg

### Leg 1 — detection signals: passes, but only under the narrowed reading

The old broad formulation failed. `Practice`, `admin`, `rota`, `policy`, `meeting`, `supplier`, and a
clinic letterhead are never-alone signals. Combining several never-alone signals does not make an
activation. A clinic's facilities handbook is still a facilities handbook.

The narrowed row has four paired structures:

1. **Repeated subject rows plus a clinical-session header.** A named clinician, room, date, and
   session are crossed with repeated patient identity blocks and slot/reason fields. This is not a
   generic rota and not a one-person chart. The structure is a many-subject care operation.
2. **Search criteria plus a person-level result set.** A coded condition, review interval, or recall
   rule is crossed with repeated patient identifiers and last-action dates. The criteria themselves
   disclose why every person is listed. This is administration by purpose and clinical data by
   content.
3. **Payer/commissioner scheme plus measured clinical activity.** A reporting period and scheme
   reference are crossed with registered population, appointments, attendance, coded activity, or
   outcome counts. A generic KPI workbook lacks the care-delivery scheme and population structure.
4. **Registered-provider organisation plus regulatory operation.** An organisation/provider block is
   crossed with registered premises or services, assessment domains, conditions, findings, and an
   organisational action plan. A regulator name or certificate shape alone is insufficient.

The tabular parts are observable under the design's own extraction model:

> “Tables matter because resumes, forms, applications, invoices, and administrative documents often place their most useful information in cells rather than body paragraphs.”

An unlabelled prose report, a blurred screenshot, or a partially mapped export needs the LLM and must
still cite bounded evidence. The governing abstention is:

> “A model that cannot cite sufficient evidence must return unknown.”

**Verdict on leg 1: pass.** It passes on paired structure, not industry vocabulary. Remove the patient
population or regulated-provider role and the row no longer fires.

### Leg 2 — privacy rules: passes, and is the strongest leg

This row's dangerous files wear ordinary office clothes. A clinic list looks like a schedule. A
recall search looks like a CRM export. A row-level activity return looks like a KPI spreadsheet. The
false-negative direction therefore differs from generic business operations: content must be
protected before any ordinary administrative summary or cloud prompt sees it.

The product rule is exact:

> “A scanned passport, tax statement, medical document, authentication key, or account record should enter a protected state immediately.”

And the consequence is exact:

> “Protected material should not be included in cloud-model prompts by default, should not display raw content in general group summaries, and should not be moved automatically without a user policy that explicitly permits it.”

The distinction is not merely that healthcare is sensitive. It is structural:

- one file may expose many people who are not the user;
- a cohort criterion can disclose a condition for every listed person even when individual notes are
  absent;
- the administrative title may not reveal clinical content;
- a practice registration certificate may be non-personal, but ambiguous system exports require
  cautious treatment.

The JSON keeps `sensitivity: potentially_sensitive` for the row. It assigns no handling class and
does not re-derive P7.

**Verdict on leg 2: pass.** Generic support and facilities rows may contain personal or authentication
material, but neither assumes batched third-party clinical subjects as the characteristic hidden
content of its central operational files.

### Leg 3 — recommended dimensions: unavailable, and not claimed as a pass

The schema declares no fields. A dimension may not name a field that cannot be written. This row
therefore keeps an empty `dimension_order`, as do its clinical siblings. In prose, function before
period is intelligible; in JSON, no key is licensed.

**Verdict on leg 3: unavailable.** This is recorded rather than laundered into a pass.

### Overall

**Kept narrowly on legs 1 and 2.** The row would be refused under the legacy *all back-office files of
a clinic* reading. It survives as the seam between clinical delivery and operations: multi-subject
clinical administration and organisation-level regulated-provider operations.

## Why this is not generic business operations

The business anchor's never-alone principle is decisive. An organisation name plus a document-type
word does not activate a business node, and adding “medical” to the organisation name does not create
a clinical exception.

### Against `business_operations.support-operations`

Support stands on a queue/case register: requester, channel, status, assignment, resolution, service
level, and escalation. This row stands on care-session populations, clinical-cohort searches,
care-activity returns, and regulated-provider findings.

Same bytes in both directions: `Access request 4831 - patient record export.eml`.

- **This row must not take** a helpdesk case merely because the requester is a patient or the queue is
  operated by a clinic. Request/agent/status/resolution remains support.
- **Support must not take** a record-access fulfilment list or cohort export merely because it arrived
  through a queue. Repeated patient subjects and clinical search criteria invoke this row's privacy
  posture; the support ticket may remain support as a separate reading.

No JSON edge is added because the central files are separable and can also-hold at the
email/attachment boundary; an edge would overstate a mutex collision.

### Against `business_operations.facilities-workplace`

Facilities stands on asset-plus-next-obligation, access holder-plus-zone, or space-plus-allocation.
Its structures remain facilities structures inside a clinic.

Same bytes in both directions: `cleaning contract - renewal 2026.pdf` and the resulting cleaning
schedule.

- **This row must not take** the contract, PPM schedule, keys register, room inspection, maintenance
  log, or cleaning rota merely because the premises provides care.
- **Facilities must not take** a clinic/session list merely because rooms and capacity appear in it.
  Repeated patient slots and care-session framing discriminate the clinical operation.

The cleaning contract remains the JSON's primary inbound collision fixture. The instrument is
`business_operations.contract-administration`; the resulting site schedule is facilities. Neither
becomes practice administration.

### Against `business_operations.organisational-records`

That row's refusal is adopted. Generic policies, agendas, minutes, reports, forms, and organisation
names have no paired structure of their own. This row does not resurrect them under a clinical label.
A practice meeting remains generic unless named cases, clinical-population operations, or a provider
regulatory cycle are the organising business. One significant-event item does not move an otherwise
ordinary management meeting.

## The regulated-provider seam after licensure refusal

`clinical_practice.licensure-credentialing` correctly reversed its gist verdict. An individual
professional licence has the same credential structure across industries: holder, issuer, identifier,
scope, issue/expiry, renewal or continuing-competence evidence. The regulating body being medical is
a value, not a new node. That material routes to `career.credentials-licenses`.

This row keeps a different role:

- **individual is regulated** → `career.credentials-licenses`;
- **organisation/service/premises is registered and inspected as a care provider** → this row;
- **regulator's internal casework and decision file** → `government.professional-regulator`.

Same bytes in both directions: a regulator-issued certificate or inspection report.

- A personal registration number and scope of practice attached to one practitioner must not be
  taken here.
- A registered-provider block crossed with service/premises, inspection domains, organisational
  findings, and an action plan must not be taken as one employee's credential.
- Regulator letterhead and certificate layout decide nothing.

This is a true two-role distinction. The **registered subject** is different, not merely the industry.
The stale JSON edge to the refused row is therefore replaced by `career.credentials-licenses`.

## Boundaries inside clinical practice

### `clinical_practice.patient-chart`

Same bytes: `records request cover sheet - Jane Doe.pdf` or a clinic-list row later filed into one
person's chart.

- **Chart → administration:** a procedural request, chase, transfer, recall, or population operation
  about records, without a dated account of care for one person.
- **Administration → chart:** one-subject longitudinal accumulation containing encounters, results,
  diagnoses, plans, and filed correspondence.

A populated clinic list must not be split into invented chart facts. The design is explicit:

> “The graph does not automatically copy those missing facts onto sparse files.”

### `clinical_practice.referral-correspondence`

Same bytes: an onward-send cover letter carrying a patient banner and addressee.

- **Correspondence → administration:** no clinical reason/report body; the item requests, chases,
  acknowledges, invoices, or transfers a record procedurally.
- **Administration → correspondence:** a directed clinical item with reason for referral, findings,
  recommendation, or an acknowledgement/reply paired to that clinical dispatch.

Direction and body purpose matter. `Referral` alone does not.

### `clinical_practice.pharmacy-operations`

Same bytes: `responsible pharmacist rota September.xlsx` and a pharmacy inspection evidence pack.

- **Pharmacy → administration:** staff/session/cover structure with no medicine custody, receipt,
  supply, balance, witness, batch, expiry, or temperature accountability.
- **Administration → pharmacy:** a controlled-drug register, dispensing accountability export,
  stock custody record, recall action tied to batches/recipients, or temperature excursion record.

The pharmacy memo already routes the responsible-pharmacist rota here. Medicine vocabulary alone is
never enough; the regulated operational structure decides.

### `clinical_practice.case-conference`

Same bytes: `practice meeting minutes 2026-02-03.docx`.

- **Case conference → administration:** several named cases are the agenda and clinical outcomes are
  recorded.
- **Administration → case conference:** rotas, staffing, premises, returns, and practice actions are
  the agenda; one case-related item does not transform the meeting.

## Bottom-up file corpus

The JSON keeps nine concrete examples. Their purpose is to show what activates, what merely
supports, and what must be rejected.

1. **`Tuesday AM clinic list 2026-04-14.pdf`** — repeated subject rows plus session header; Protected
   Records if inactive.
2. **`overdue reviews search 2026-03.csv`** — cohort criteria plus repeated people. Strongest privacy
   fixture because the criteria disclose why every row exists.
3. **`rota_april_v3.xlsx`** — supports this row only when clinics, patient-facing sessions, or clinical
   cover appear. People/hours/leave alone is HR.
4. **`inspection report - final.pdf`** — registered-provider organisation, services/premises,
   assessment domains, findings, and action plan.
5. **`practice meeting minutes 2026-02-03.docx`** — ordinary management shape does not activate alone.
6. **`clinics.ics`** — calendar representation of named clinical sessions. `.ics` and recurrence are
   routing evidence only.
7. **`quarterly return Q4.zip`** — mixed archive holding a clinical activity return and supporting
   exports. The archive may be represented
   without extraction; member context does not propagate facts automatically.
8. **`Screenshot 2026-04-02 at 09.14.11.png`** — OCR may reveal a clinic grid or patient queue; until
    readable it is potentially sensitive observation, not asserted fact.
9. **`cleaning contract - renewal 2026.pdf`** — collision fixture. Practice as customer, supplier,
    term, scope, price; no clinical population or provider-regulatory structure. Reject.

Extensions are never sufficient. The product's exact rule is:

> “treat the file extension as a routing signal rather than an assumption about meaning”

And bulk download context never supplies topic:

> “A session should never be treated as proof of topic”

## Files considered and rejected

| Tempting file | Decision and discriminator |
|---|---|
| `cleaning contract - renewal 2026.pdf` | Reject. Contract/customer/supplier/term/price structure; clinic industry is only a value. |
| `PPM schedule - treatment centre.xlsx` | Reject. Asset crossed with next-due obligation is facilities-workplace. |
| `Staff rota April.xlsx` | Reject unless named clinical sessions or service cover are present. People/hours/leave is HR. |
| `Practice handbook.docx` | Reject. Generic policy vocabulary and organisation name are never-alone evidence. |
| `Practice meeting minutes.docx` | Reject unless clinical-population operations or provider regulation is the organising business. |
| `Dr Chen revalidation portfolio.zip` | Reject. Individual credential structure; `career.credentials-licenses`. |
| `Controlled Drugs Register 2026.pdf` | Reject. Medicine custody/supply accountability; pharmacy operations. |
| `Referral - Orthopaedics - Jane Doe.pdf` | Reject when directed clinical reason/report content is present; referral correspondence. |
| `SOAP note - Jane Doe.docx` | Reject. One-subject dated account of care; patient chart. |
| `Helpdesk queue - EHR access.csv` | Reject. Requester/agent/status/resolution remains support operations. |
| `Clinic capacity brochure.pdf` | Reject. Descriptive reading material, not an operational record; Reference Clips. |
| unreadable `dashboard.png` | Do not classify by appearance. Protect conservatively and await OCR/bounded evidence. |

## Collision fixture in both directions

### Over-firing: `cleaning contract - renewal 2026.pdf`

It has the practice name, a health-premises address, a service schedule, a vendor, and compliance
language. Under the legacy reading it would fire immediately. Under the narrowed reading it does not:
there are no repeated clinical subjects, clinical cohort criteria, care-activity scheme, or
registered-provider assessment structure. The practice is simply a customer. Contract administration
owns the instrument; facilities owns the resulting site schedule.

### Under-firing: `overdue reviews search 2026-03.csv`

It resembles an ordinary campaign or CRM list: criteria, people, last-action dates, next action. It
must not be lost to support or generic operations. The search criteria name a clinical condition or
care interval, and result rows identify the people to whom it applies. That paired structure is both
the activation and the sensitivity reason.

The safe fallback is not maximal movement:

> “Correct abstention is a successful outcome because the product’s goal is reliable organization, not maximum file movement.”

## Recognition discipline

### Deterministic only with paired structure

- session header **plus** repeated patient/slot rows;
- clinical cohort/search criteria **plus** repeated subject identifiers;
- commissioner/payer scheme reference **plus** care-delivery measures;
- registered-provider organisation block **plus** premises/service/inspection/action-plan structure;
- clinical-system report title **plus** labelled run/search block and output table.

### Needs the LLM

- whether a free-form meeting is about running the practice or discussing named cases;
- whether “session” means a care session, training, login, or meeting;
- whether a row-level return contains patient data beneath an aggregate cover;
- whether an organisation or an individual is the regulated subject in unlabelled prose;
- whether a screenshot is a patient queue, staff rota, or generic dashboard.

### Never alone

- clinic or practice name; regulator or commissioner name;
- `admin`, `rota`, `report`, `policy`, `meeting`, `inspection`, `registration`, `session`, or `recall`;
- any person name, staff list, address, four-digit number, extension, folder name, or export session;
- clinical vocabulary without operational structure;
- a supplier's healthcare-sector marketing material.

## Fields and grouping discipline

`fields: []`. `proposed_fields: []`. The task explicitly forbids keys, and the schema anchor declares
none. `session`, `clinic`, `registered_provider`, `commissioner`, and `reporting_period` are tempting
but are not minted. Universal facts such as file type, creation date, language, version-family,
duplicate-family, and sensitivity status may still be legal where supported; they are not clinical
schema fields.

Grouping does not propagate missing facts. Valid packet reasons are one inspection and response, one
reporting cycle, one rota version family, or one recurring clinic series. A shared folder named
`Practice Admin` is support, not proof. One stray clinic list may remain ungrouped and protected.

## Residuals

- **Protected Records** for populated clinic lists, recall searches, row-level returns, and readable
  screenshots containing patient information.
- **Independent Records** for an isolated practice registration certificate, non-personal inspection
  notice, procedure, or ordinary rota with durable purpose but no accepted group.
- **Review Later** where clinical-versus-generic operational meaning remains unresolved.
- **Temporary Screenshots** for an un-OCRed capture with no accepted relationship.
- **Unsupported or Encrypted** for proprietary or encrypted practice-system exports represented
  without unsafe extraction.

## NEEDS-JOSEPH

- **NJ-CP-12 — keep versus branch pattern.** KEEP: multi-subject clinical-operation and
  organisation-as-regulated-provider structures differ from generic business operations, and the
  false-negative privacy cost is high. FOLD: a practice manager experiences these beside contracts,
  premises, staffing, and finance; the clinical subset could be a sensitivity branch pattern on
  business/HR rather than a node. This pass recommends **keep narrowly**, but the roster ruling remains
  Joseph's.
- **NJ-CP-12A — provider regulation boundary.** Should organisation-level registration and inspection
  remain here, or live under a government/regulatory-casework node with a holder-side role? Keeping it
  here preserves the operational packet; moving it makes the same inspection legible from both
  custodial sides but risks filing the practice's action plan with the regulator.
- **NJ-CP-12B — row-level versus aggregate returns.** Should aggregate-only activity returns inherit
  row-wide `potentially_sensitive`, or may deterministic absence of person-level rows lower them? The
  catalogue has only a row-level value, so this pass stays cautious and mints no per-file downgrade.
- **NJ-CP-RECIP — stale reciprocal edges after licensure refusal.** R1c must remove remaining references
  elsewhere that say `clinical_practice.licensure-credentialing` owns individual licences and point
  them to `career.credentials-licenses`. This pass changes only its assigned JSON and memo.

## What changed in this pass

### JSON first

1. Rewrote `one_line` from the broad legacy frame to the two structures that earn the node; replaced
   the retired gist label with J-DEPTH.
2. Kept `refuse_node: false`, `fields: []`, `proposed_fields: []`, `role_split: []`, and empty
   `dimension_order`.
3. Replaced the collision edge to refused `clinical_practice.licensure-credentialing` with
   `career.credentials-licenses` and rewrote the organisation-versus-individual discriminator.
4. Corrected the rota edge and inspection fixture so they no longer claim the refused sibling owns
   individual revalidation.
5. Preserved nine concrete examples, strict residuals, and `potentially_sensitive`.

### Memo second

Replaced the 8.7KB gist memo with this J-DEPTH analysis: schema default; all three node-test legs;
support/facilities/licensure comparisons; reciprocal boundaries with chart, referral, pharmacy, and
case conference; rejected files; both-direction collision fixtures; recognition discipline;
fields/grouping/residuals; and explicit NEEDS-JOSEPH items.

## Self-verification

- JSON parses and has exactly 27 universal keys.
- Memo declares literal `J-DEPTH` within its first eight lines and ends on a complete section.
- `fields` and `proposed_fields` are empty; no clinical key was minted.
- All quoted `00` strings were checked as exact substrings after Markdown quote-prefix removal.
- No neighbour file was edited.
