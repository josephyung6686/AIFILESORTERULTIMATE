# hr.onboarding-offboarding — lab notes (R1b)

Depth: J-DEPTH
Date: 2026-08-26
Roster row: `kind: template`, `schema_id: hr`, `launch: placeholder`, `parent_id: null`.
Output: [`hr.onboarding-offboarding.json`](hr.onboarding-offboarding.json).
Salvage: none — no prior draft of either file existed. Both files are written from scratch in this pass.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` — the standing brief, read in full. J-DEPTH, the six
  requirements, and the instruction that a refusal is a success.
- `planning/domains/dispatch/make_prompt.py hr.onboarding-offboarding` — the stamped assignment.
  Supplied the row metadata, `must_consider_neighbors` (`career`, `business_operations`, `finance`),
  `must_consider_residuals` (`Protected Records`, `Independent Records`), `inherited_field_keys: []`,
  the node test, and the done-when list this memo is audited against.
- `planning/domains/nodes/hr.json` — **the schema anchor, and the row this template is measured
  against.** Read in full because the node test is literally "how do you differ from the default
  template". Its four proposed keys, eleven work types, seven deterministic signals, ten never-alone
  rules and empty-by-PR-6 dimension order are the baseline every claim below argues against.
- `planning/00-database-agent-product-design.md` — authoritative, read by targeted `grep -n -o` only,
  per the token discipline in the dispatch. Three spans were extracted and re-matched verbatim
  (audit below). **The word "onboarding" does not occur in `00` at all** — verified by grep. That is
  not a defect in the row, it is the reason `provenance` is `inference` and `design_cite` is `null`.
- `planning/domains/roster.json` — confirmed the id, the twelve `hr.*` siblings, and every edge
  endpoint. All nine `collides_with` targets, all three `also_holds_with` targets and both
  `role_split` targets resolve to roster `domain_id`s; both residual names are §7.3 names.
- `planning/domains/nodes/finance.crypto-assets.research.md` — the depth calibration launch row named
  by the brief. Read one, as instructed.
- `planning/domains/nodes/business_operations.it-asset-inventory.{json,research.md}` and
  `business_operations.policy-handbook.{json,research.md}` — found by one grep for landed rows that
  already argue a boundary against this id. Read only the matched regions. **Both had already written
  their side of a boundary against this row and both explicitly flagged the reciprocal as owed.**
  This pass pays both.

## THE CHARGE — the strongest case that this row should not exist

I put this first because it is the part of the work that decides whether anything else is worth
writing. The case against is genuinely strong and has four independent legs.

**1. It is a lifecycle stage — the disqualifier by name.** "Onboarding" and "offboarding" are the
first and last stages of the employment lifecycle. A stage is a position in time, not a filing world.
The brief lists "a lifecycle stage" as a reason to refuse, and this row wears the stage in its id.

**2. It is already a value on its own schema, twice over.** The `hr` schema row's `work_types` list
contains, verbatim, "onboarding or offboarding plan, checklist, induction record, or acknowledgement".
Its `people_cycle` proposed key gives "2026 graduate intake" as an example value. So the schema has
already declared this row's entire content as (a) one value of a work-type enum and (b) one value of
a proposed field. ALIGNMENT says work types are values, never nodes. On this reading the row is a
duplicate of two enum members.

**3. Its detection signal is already the schema's own.** `hr.json`'s fourth deterministic signal is
"an onboarding or offboarding tracker whose columns combine joiner/leaver identity, effective date,
process task, owner, and completion state". The schema fires on my best fixture without me. If a
template's signals are identical to the schema default, CONNECTION's node test says refuse.

**4. The offboarding half is defined by an absence.** A leaver is a person who is no longer employed.
A row half of which is "the employee stopped being here" is a row defined by the absence of something
— another disqualifier the brief names. And gluing two opposites together (the legacy `hr.offboarding`
was absorbed into this id by the roster, not by research) is exactly how the 574 manufactured rows.

Leg 3 is the one that nearly killed the row, and I want to be explicit that I nearly refused on it.

### Why the row survives anyway

**Against leg 1 and leg 4.** A lifecycle stage that produces no distinctive artifacts is a label. This
one produces a distinctive artifact family whose *authors are mostly not HR*: an IT provisioning
ticket, a facilities badge request, a payroll setup form, a security access grant, a manager's
first-week plan. These bytes exist and get filed whether or not anyone calls the stage "onboarding".
And the leaver half is not an absence: it is the positive presence of a **revocation** task set, a
return-of-property receipt, a duties handover document, a final-pay instruction and an exit record.
"Absence of employment" produces no files; revocation produces a stack of them.

**Against leg 2.** A work type is a value when it names a *document shape*. "Checklist" is a value.
What this row names is not a document shape but a **cross-functional handoff structure**: a task
matrix whose owner column contains four or five different functions, converging on one date, for one
person whose employment status changes on that date. No enum member can carry a structure; enum
members carry names. The proof that this is structure and not a name is that the structure is what
discriminates, and the name is the single worst never-alone on the node (see the collision fixture).

**Against leg 3 — the node test, argued in full.** CONNECTION's test is that a template exists only
when its **detection signals**, its **recommended dimensions**, or its **privacy rules** differ from
its schema's default. Taking each on its own reasoning:

*Detection signals — DIFFER, and this is the load-bearing leg.* The `hr` schema's default requires
"a personnel process, workforce population, or employee case structure". Every other `hr` sibling
satisfies that through one of three shapes: a **population** (payroll register, workforce census,
establishment plan — one row per worker, employer-side totals), a **cycle instrument** (review
calibration, survey responses — one row per person carrying a measure), or a **case** (grievance,
incident — a reference plus allegation plus outcome). This row satisfies it through a fourth shape
that none of the others has: **rows that are TASKS, columns that are OWNING FUNCTIONS, a completion
state per cell, and exactly one effective date for the whole sheet.** A payroll register has workers
but no tasks. A calibration has people and measures but no owners-by-function. A grievance has a
process but no provisioning. Layered on top is a discriminator that exists nowhere else in the family:
**provisioning direction** — a grant vocabulary (account created, equipment issued, badge issued,
payroll set up, buddy assigned) versus a revoke vocabulary (account disabled, mailbox delegated,
equipment returned, badge surrendered, final pay raised). Direction is readable, deterministic and
unique to this row, because no other personnel situation grants or revokes anything. The schema's
fourth deterministic signal is a *summary* of this row; this row supplies the structure the summary
gestures at, plus two signals the schema does not have at all (the joint new-starter form, the joint
archive manifest). That is a real difference, not a restatement.

*Recommended dimensions — DIFFER in substance, unencodable in form, and I will not pretend otherwise.*
The `hr` schema row's prose default is "work type or named people programme first; then workforce unit
or cohort ...; then people cycle". This row recommends the **inverse**: people cycle first, work type
as leaf. The argument is evidential. One joiner process emits exactly one of each work type — one
checklist, one starter form, one acknowledgement, one receipt, one agenda — so a work-type-first order
scatters a single person's process across five folders and files each member next to a stranger's
member of the same type. That is the precise failure `00` describes when it says a homework item is
meaningless without its course, transposed: a handover receipt is meaningless without the departure it
served. **But PR-6 means the `hr` schema declares no canonical field rows, and a template may only
branch on a field its own schema declares, so `dimension_order` must be `[]` here exactly as it is on
the anchor.** The difference is therefore real, argued, and *recorded as prose for R1c* rather than
encoded. I am flagging this rather than smoothing it, because a reader comparing the two JSON files
will see two empty arrays and could conclude this leg is empty. It is not empty; it is deferred.
It is also NJ-ONB-4.

*Privacy rules — DIFFER in kind, and this is the leg I would defend the row on if the other two fell.*
The schema's default is "employee-identifying content must be protected before any cloud step". This
row's rule is not a stronger version of that; it is a different rule with a different object. A joiner
packet is the densest concentration of **identity-schema** material in the entire employer filing
world — a passport or right-to-work scan, a statutory identifier, a bank account for payroll setup, a
date of birth, a home address, a next of kin, often a background check — all assembled in one place, at
one moment, under one name, by a process whose *own purpose coherence makes absorbing them look
correct*. `00` names "passport scans ... visas, legal forms, or credentials" as Protected Records
material outright. No other `hr` sibling routinely holds a passport. So this row's distinctive privacy
rule is a **refusal**: purpose coherence must never launder an identity document into an ordinary
process folder; identity's protection runs first and the group forms *around* that member. That rule
appears nowhere on the schema anchor and could not, because it is specific to the one situation that
collects identity documents as a task.

Verdict: `refuse_node: false`, on signals and privacy independently, with the dimension leg argued and
deferred. Nothing was invented to save the id — `fields: []`, no key minted, and the one key the row
depends on is a *seconding* of the schema's existing proposal rather than a new one.

## The organizational situation, bottom up

Twelve file examples. The list is deliberately unbalanced toward the ugly cases:

| Fixture | Why it is on the list |
|---|---|
| `New joiner checklist - J Patel - start 2026-09-01.xlsx` | the labelled happy case; all four axes present |
| `New joiners - September intake tracker.xlsx` | the cohort case. **Deliberately the same bytes the `hr` anchor carries, named identically**, so schema and template agree on one fixture |
| `New starter form - completed.pdf` | the joint-slot signal; also the finance/identity false-split trap |
| `Right to work check - passport scan.jpg` | **the refusal fixture** — sits inside a joiner folder and must NOT activate this row |
| `Induction day 1 - welcome deck.pptx` | names nobody; the file that must still group |
| `Handbook acknowledgement - J Patel - signed.pdf` | the policy-handbook shared bytes |
| `Laptop handover form - signed.pdf` | the it-asset-inventory shared bytes; co-activation, not theft |
| `Leaver checklist - last day 2026-11-14.xlsx` | the revoke direction; proves the offboarding half is positive evidence |
| `Exit interview notes.docx` | unlabelled prose naming third parties; the `needs_llm` case |
| `Client onboarding checklist - Meridian Ltd.xlsx` | **the collision fixture** (below) |
| `onboarding-pack.zip` | the archive packet with mixed members `00` asks for |
| `Day 1.pdf` | the sparse file — the `HW 3.pdf` of this node |

Four fixtures carry `group_without_copying_facts: true`. `Day 1.pdf` is the important one: a page of
times and room names with no date, no employer and no person, sitting beside an induction deck and two
acknowledgements. The neighbourhood is the *only* thing suggesting a domain, so it may join an accepted
group and receives **nothing** — no cycle, no unit, no person. Activation is not grouping.

## The collision fixture

`Client onboarding checklist - Meridian Ltd.xlsx`. Task, owner, due and completed columns —
structurally identical to the joiner sheet. Tasks: KYC check, conflict check, engagement letter signed,
credit terms agreed, portal access granted, kickoff booked, welcome pack sent. One go-live date. The
word "onboarding" in the filename. Every surface signal this row has, it has.

**What discriminates it:** the *subject* of the tasks. Here it is a counterparty organisation with an
engagement, KYC, conflict, credit or contract anchor. In this row it is a natural person acquiring an
employment status — the giveaways being contract of employment, right to work, payroll setup, staff ID,
probation. Nothing else separates them, which is why "onboarding", "welcome pack", "access provisioned",
"first 30 days" and the checklist shape itself are all written into `never_alone`. Routes to
`business_operations.customer-account-management`. Tenant move-in packs, patient intake forms and
product user-onboarding specs are the same trap in three other worlds.

## Files considered and rejected

- **`Offer Letter - Summer Analyst.pdf`** — the `hr` anchor's own fixture and the most tempting file
  here, because it is the document that *causes* this row's process. Rejected: an offer exists whether
  or not it is accepted; the process exists only after acceptance. It is `career.employer-side-hiring`'s
  output and this row's trigger, never this row's evidence.
- **`Employee Handbook v4.2.pdf`** — `business_operations.policy-handbook` settled this from its side
  and this pass reciprocates rather than relitigates. The controlled document is theirs; only the
  person-anchored acknowledgement reaches here.
- **A standing device register / entitlement export** — `business_operations.it-asset-inventory`'s, and
  that row's own rule (a form anchored on one asset identifier with no employment content is theirs) is
  adopted verbatim as this row's limit.
- **A payroll register, an employer remittance, a benefits enrolment file** — `hr.payroll-benefits-administration`.
  Payroll recurs on a payroll calendar; this row happens once per person per date. The checklist task
  that *says* "payroll set up" is a task, not a payroll record.
- **An org chart, a seating plan, a benefits summary** — reused *by* induction, produced by
  `hr.org-design-headcount`, `business_operations.facilities-workplace` and `hr.compensation-planning`.
  Induction being their consumer confers no ownership.
- **A mandatory-training matrix and a course completion roster** — `hr.training-development`. The hard
  residue is `Induction completion roster - Sept 2026 intake.xlsx`, which is genuinely both; it is named
  in the collision edge rather than claimed.
- **An employment contract / a settlement agreement** — legal instruments. Co-activation, recorded in
  `also_holds_with: legal`; not file examples, because their correct home is not decided by this row.
- **A personal "my first week" diary or blog draft** — prose about starting a job is not an employer
  process record. Listed in `needs_llm` with abstention as the right answer, not as a fixture.
- **`Termination - J Patel - final pack.zip`** — deliberately kept OUT of `file_examples` and put only
  in the `hr.employee-relations` collision, because its correct outcome is a *split*, and a file example
  implies a single verdict this row should not be seen to render.

## Reciprocal boundaries

Nine `collides_with` edges, each stated in both directions with the same fixture bytes named on both
sides. The three that matter most:

| Neighbour | This row must not take | The neighbour must not take | Shared fixture bytes |
|---|---|---|---|
| `business_operations.policy-handbook` (landed) | the governing document, including one titled Induction Policy | an acknowledgement or induction checklist anchored on one named joiner | `Employee Handbook v4.2.pdf` / `Handbook acknowledgement - J Patel - signed.pdf` |
| `business_operations.it-asset-inventory` (landed) | a form anchored on one asset identifier with no employment content; a standing register | a checklist spanning accounts, payroll, induction and access | `Laptop handover form - signed.pdf` |
| `identity.core-documents` | the passport/visa/ID itself or any scan of it, **even inside a purpose-coherent packet** | the employer's dated, signed check RECORD, which is process evidence | `Right to work check - passport scan.jpg` |

The other six — `career.employer-side-hiring` (the acceptance line), `career.employment-records` (same
bytes, opposite custody), `business_operations.customer-account-management` (the collision fixture),
`hr.training-development` (the word "induction"), `hr.employee-relations` (every dismissal makes both),
`hr.payroll-benefits-administration` (setup and final pay) — are written the same way in the JSON.

Both landed `business_operations` rows recorded their edge as one-way with the reciprocal owed. **This
pass pays both, using their filenames and their discriminators unchanged**, so R1c should find the two
sides already agreeing rather than needing to arbitrate. That is a recommendation to R1c, not an edit:
I did not touch either neighbour file.

## Neighbours considered that did **not** get an edge

- **`finance`** — named in `must_consider_neighbors`, and rejected as a direct edge. The seam that looks
  like finance (the joiner's bank details, the leaver's final pay) is fully intercepted by
  `hr.payroll-benefits-administration`, which sits between them. Giving finance an edge as well would
  give one evidence item three claimants — the failure the crypto launch row names.
- **`business_operations.project-delivery`** — a task/owner/due matrix is also a project plan. No edge:
  a project plan has milestones, dependencies and a scope, and no employment-status change. The
  discriminator is already carried by the first `never_alone` on checklist shape.
- **`identity.immigration-visa`** — a visa sponsorship file is a real joiner artifact, but the
  discriminating bytes are the same ones `identity.core-documents` already covers, and adding a second
  identity edge would duplicate one refusal.
- **`business_operations.meeting-record`** — an induction session and an exit interview are meetings. No
  edge: the meeting-record shape is agenda/attendees/minutes/actions with no employment-status change,
  and the exit interview's real contested neighbour is `hr.employee-relations`, which has the edge.
- **`hr.performance-cycle`** — deliberately **no edge**, and this is the interesting omission. A
  probation review is genuinely contested between us, but I could not settle where onboarding ends, and
  writing a boundary I cannot state in both directions would be a guess dressed as a contract. It is
  NJ-ONB-3 instead.
- **`role_split`** — two entries only (`career.employment-records`, `business_operations.it-asset-inventory`).
  A third was tempting — the employer versus the *outsourced provider* who runs the process — but there
  is no canonical key for a service provider, and minting one to solve a single template's problem is
  the move that produced thousands of private field names in the overnight pass.

## `proposed_fields` — one entry, and it is a seconding

`people_cycle`, already proposed by the `hr` schema row. This row does not mint it; it asks R1c to
adjudicate it with this situation's evidence present, because this row is simultaneously the strongest
case *for* the key and the strongest case *against* the schema anchor's own prose ordering of it.

**One key was deliberately refused: a joiner/leaver direction key.** Provisioning direction is the
sharpest discriminator on the node, which is exactly why it is tempting to make it a field. It is a
**value** — of `work_type`, or of the cycle — and making it a key would immediately force the question
of whether it can be a folder level, where the answer is plainly no: a directory named "Leavers"
publishes departures. Recorded in `work_types` and `recognition` as a value, and in NJ-ONB-2 as an
argument about row shape, not field shape.

## Audits run before returning

- `python3 -m json.tool` — parses.
- 12/12 `file_examples.source_type` in the fourteen-member `SOURCE_TYPES` list, checked mechanically.
- 14/14 edge endpoints (9 `collides_with`, 3 `also_holds_with`, 2 `role_split`) resolve to roster
  `domain_id` values, checked mechanically against `roster.json`.
- 2/2 `falls_through_to` names are §7.3 residual names.
- All three `00` spans of 25+ characters extracted from the JSON and matched **verbatim** against
  `planning/00-database-agent-product-design.md`. No fabricated quotation. `design_cite` is `null` and
  `provenance` is `inference` because `00` never uses the word "onboarding" (grep-verified).
- No threshold, score, count or handling class anywhere in either file. `sensitivity` is
  `potentially_sensitive` only.
- `fields: []`; no canonical key minted; `proposed_fields` holds one seconding, marked `adjudicate: R1c`.
- At least one `never_alone` is true of a tempting false file: the word "onboarding" and the checklist
  shape are both never-alone, and both are true of `Client onboarding checklist - Meridian Ltd.xlsx`.
- Only the two assigned files were written. No neighbour node, roster, `canonical_fields.json`,
  `check.py`, `src/` or SPEC was touched.

## NEEDS-JOSEPH (this node only)

- **NJ-ONB-1 — may a purpose-coherent joiner packet absorb its identity-document member?** This row
  says no. `00` supports grouping by purpose despite topic diversity, and also names passport scans as
  Protected Records material; the two pull opposite ways on the same bytes. (a) Absorb under a
  strictest-side-wins rule — the group's exposure surface becomes as wide as its worst member.
  (b) Route the identity member to identity/Protected Records and let the group hold a reference — what
  this row recommends, and what the current contract does not obviously permit. (c) Refuse to group
  packets containing identity members at all — safe, and loses the process. **Not resolved here.**
- **NJ-ONB-2 — one row or two?** The roster glued legacy `hr.offboarding` into this id. For one row: an
  identical task/owner/effective-date structure, with direction as a value (which is why no direction
  key was minted). For two: materially different sensitivity profiles (joiner discloses identity
  documents; leaver discloses the departure itself) and a claimant on the leaver side
  (`hr.employee-relations`) that the joiner side does not have. Alternatives: keep one row; split into
  `hr.onboarding` and `hr.offboarding`; or keep one row and route disciplinary departures wholly to
  employee-relations.
- **NJ-ONB-3 — where does onboarding end?** Day one, first week, thirty/sixty/ninety days, or probation
  confirmation are all defensible, and the choice decides whether a probation review is this row's
  closing act or `hr.performance-cycle`'s opening one. This row lists probation records in `work_types`
  and writes **no** edge to `hr.performance-cycle` rather than guess a boundary it cannot state
  reciprocally.
- **NJ-ONB-4 — `people_cycle` leading, and destination-eligibility.** This row asks for the cycle to
  lead, contradicting the `hr` anchor's prose default of work type first, and asks for the key to be
  destination-eligible, which interacts with the anchor's NJ-HR-2. The sharp edge is the single leaver:
  a folder named for one departure discloses the departure, so if the key leads it must lead for
  cohorts and be suppressed for individuals — a conditional this row can recommend but cannot encode
  while PR-6 keeps `dimension_order` empty.

## Recommendations to R1c (not edits — no neighbour file was touched)

1. **Two owed reciprocals are now paid from this side.** `business_operations.it-asset-inventory` and
   `business_operations.policy-handbook` each recorded their edge to this id as one-way with the
   reciprocal outstanding. Both are now written here with their own fixture bytes and discriminators.
   R1c should be able to close them by inspection rather than arbitration.
2. **The `hr` anchor's prose dimension default and this row's recommendation disagree**, deliberately
   and with reasons on both sides. R1c should decide the ordering for the family, not per row.
3. **`people_cycle` should be adjudicated with this row in front of it**, since this situation supplies
   both the clearest need for the key and the clearest constraint on its destination-eligibility.
