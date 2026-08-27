# Research memo — `hr.training-development`

Depth: J-DEPTH
Date: 2026-08-27
Output: `planning/domains/nodes/hr.training-development.json`
Roster row: `kind: template` on the fieldless `hr` schema, `parent_id: null`, `launch: placeholder`
Absorbs: legacy `soft.training-material` (see the audience caveat, which I do not smooth)

## Result

**Accept the node**, and accept it on one argument rather than on a list of artefacts: this is the
only `hr` situation whose strongest evidence can contain **no employee at all**, and the only one
whose corpus splits into two halves with different privacy postures. Everything else in the row
follows from those two facts.

## Salvage disclosure — what I inherited and what I changed

A killed agent left `hr.training-development.json` with no memo. Per `28-AUTOPILOT.md` §4 it was an
untrusted draft. I verified it line by line and found it substantively strong: its signature
recognition signal, its dimension argument, and its privacy split are all sound and I have adopted
them as my own reasoning rather than rewriting them. Five things were wrong or missing:

1. **`also_holds_with` carried four template ids.** `CONNECTION.md` line 242 restricts that edge to
   `schema ↔ schema only`. A template row may therefore author none. I emptied the array and moved
   all four co-holds into this memo (see *Co-holds removed*) plus a new NJ-TD-3. The entries also
   lacked the required `provenance` key.
2. **`collides_with` signals buried the fixture** behind varied prose openings and repeated
   `Provenance: inference.` as free text beside the key that already carries it. I normalised every
   signal to open its fixture clause with `SAME FIXTURE BOTH SIDES:` and confirmed all nine entries
   are `{domain, signal, provenance}` objects.
3. **A missing neighbour.** `academic.continuing-education` landed without naming this row, and it
   is the sharpest remaining seam after `career.credentials-licenses`. I authored the missing half.
4. **Two `.csv` fixtures had different `source_type`s** for no stated reason (`code_structured` vs
   `spreadsheet`). The LMS export is now `spreadsheet`.
5. **No dangling neighbour id.** A sibling salvage row this session carried one; this one does not.
   All twelve original ids plus the one I added resolve against `roster.json` `domain_id` values —
   verification output below.

## THE CHARGE — the strongest case that this row should not exist

I put five attacks, hardest first. The first one nearly succeeds.

**Attack 1 — it is a `work_type` value, and its own schema already says so.** The `hr` schema row's
`work_types[]` contains, verbatim, `"learning curriculum, session record, completion roster, or
development plan"`. The brief's own failure mode is a row that is a value dressed as a node. The
schema has already enumerated this world as one item in an enum. There is nothing left to be.

**Attack 2 — it is a document-type row.** Certificates, decks, rosters, sign-in sheets. Strip the
artefact names and nothing remains but file kinds, which are `SOURCE_TYPES`, not nodes.

**Attack 3 — it is defined by an absence.** "A personnel record that is not a case, not a pay run,
not a review." A row whose definition is a subtraction from its schema is the schema's default
template with a filter on it.

**Attack 4 — it duplicates two neighbours.** `hr.onboarding-offboarding` already owns induction;
`academic.continuing-education` already owns a person's course-plus-certificate. Between them the
evidence is spoken for.

**Attack 5 — the absorbed legacy coverage is an audience distinction, and audience is a role
perspective.** `soft.training-material` is a product course. Whether it belongs here or to
`business_operations.go-to-market` turns *only* on whether the audience is staff or customers. `00`
forbids a role perspective as sole proof; the schema row's own `never_alone` starts with exactly
that reasoning for the employer role.

### Defeating the charge

**Attack 1 falls on a structural observation, not on rhetoric.** Every `hr` template maps to some
`work_types[]` entry — `hr.performance-cycle` maps to `"performance objective, review, calibration,
rating, or improvement-plan record"` and nobody argues it away. Enumerability decides nothing. What
decides it is this: the four artefacts that entry names **do not share a subject**. A curriculum's
subject is a body of instruction and it names no person. A completion roster's subject is a set of
named people and it contains no instruction. If this were one value, one dimension order and one
privacy posture would serve it. It needs two of each — which is precisely the test
`CONNECTION.md` sets. A value cannot fail to be one thing in the way this world fails to be one
thing.

**Attack 2 fails because the row's join is not a document.** The thing that groups
`Data Protection Essentials - Module 3 - facilitator guide.docx`, `LMS export - completions
2026-Q2.csv` and next year's refresher is a **programme identity that outlives every document in
it**. The same named course recurs across cohorts, across years, across departments, across
providers, and across a version-family of decks. No document type produces that join, and no other
`hr` row has an entity that survives its own cycle — a pay run, a review round, a survey wave and a
grievance all end.

**Attack 3 fails on a positive signature.** The row's first deterministic signal is stated
positively and is not a subtraction: labelled learning objectives, a module number within a stated
sequence, activity instructions, a knowledge check with answers or a pass mark, and a facilitator
script. That combination activates with no employee, no workforce population and no case anywhere
in the bytes. That is not "hr minus something" — it is evidence the `hr` schema default explicitly
cannot reach, because every one of its seven deterministic signals requires an employee or cohort
**and** a personnel process.

**Attack 4 fails on fixtures, argued reciprocally below.** Induction is start-date-scoped and dies
with the joiner process; a programme is deliberately re-run and its roster spans tenured staff.
`academic.continuing-education` needs a credit-unit statement this row has no equivalent of.

**Attack 5 I concede in part, and I am not smoothing it.** For the absorbed
`soft.training-material` coverage the discriminator genuinely *is* audience, and audience is
frequently stated only in a speaker note or an invitation. I therefore do **not** claim that
coverage activates deterministically. It sits in `needs_llm`, the row's `never_alone` list bars the
provider/academy name that most often tempts it, and `business_operations.go-to-market` holds the
reciprocal. A partly weak absorbed legacy row does not defeat a node whose core is strong; pretending
it were strong would be the failure the brief names.

**Verdict: the node stands.** Its weakest half is disclosed rather than dressed up.

## Node test — three legs, against the `hr` schema's default template

The `hr` schema is a fieldless placeholder (PR-6, D1). Its default template is prose in
`hr.json`: *work type or named people programme first; then workforce unit or cohort when the corpus
genuinely spans several; then people cycle; and only under explicit user policy a pseudonymous
personnel case.* I differ on all three legs.

**Leg 1 — detection signals differ.** The schema default's deterministic list is uniformly
person-anchored: the first entry requires labelled slots that *"jointly identify an employee or
workforce cohort AND a personnel process"*, and every subsequent entry repeats that shape (payroll
register, review packet, joiner tracker, case form, analytics export, personnel calendar item).
This row's signature signal negates that precondition — curriculum structure with no person present.
It also contributes two shapes the schema default has no vocabulary for: a table **whose rows are
courses** (catalogue), and a **two-dimensional learner-by-course grid** whose cells are completion
states. Every other `hr` spreadsheet is one-dimensional in people. The 2-D shape is the single
cheapest discriminator in the row.

**Leg 2 — recommended dimensions differ, and differ deliberately.** The schema default leads with
work type or workforce unit. This row leads with `learning_programme`, puts `people_cycle` (cohort
or renewal year) second, `work_type` third, demotes `workforce_unit` below all of them, and makes
`workforce_member` never a level. Two reasons, both traceable. First, `00`'s intelligibility rule
for `Homework 3`: a module guide, an attendance sheet and an evaluation form are meaningless
without their course, and a cohort is meaningless without its course, while a course is fully
meaningful without either — so the schema default's order inverts the dependency here. Second,
leading with `workforce_unit` would **shatter one curriculum into departmental copies**, because a
course is re-used across departments by design. `time_first: false`, and for a specific reason: a
session date, an enrolment date, a completion date, a certificate issue date and a renewal due date
are five different roles inside one programme, and no generic date rule separates them.

*Contract note:* `dimension_order` is `[]` because PR-6 forbids serialising a non-canonical key.
The recommendation is prose for R1c. This is the same posture `legal.practice-matter-file` took.

**Leg 3 — privacy rules differ, and not merely in degree.** The schema default applies one blanket
posture to employee-identifying content. This row's corpus **bifurcates**. The content half —
modules, facilitator guides, catalogues, general-course recordings — contains no personal data at
all, and treating it as protected would over-protect and hide material the user legitimately wants
to browse and re-use. The completion half is sharper than the `hr` default in a way the default does
not anticipate: **the course title itself is the leak.** A branch or filename pairing a learner with
*Substance Misuse Awareness*, *Safeguarding*, *Harassment Prevention*, *Return to Work* or
*Reasonable Adjustments* discloses more than the file's contents do. An `Exempt` or `Deferred`
marker in a matrix can encode a health, disability, pregnancy or religious circumstance without ever
naming it, and a failed-attempt count is easily misread as a capability finding. That is why
`workforce_member` is proposed `destination_eligible: false` here specifically, and why the row
retains exemption markers as literal observations and never resolves them into reasons. The node
records only `potentially_sensitive`; handling classes are P7's.

All three legs differ. The row is not its schema's default template with a filter on it.

## Evidence — the file set, and what each one proves

Fifteen fixtures are in the JSON with full observations, legal facts and prohibited conclusions.
This memo records why each earns its place rather than restating it.

The set is chosen to cover the ugly cases the brief names, not the happy syllabus:

- **Labelled form vs unlabelled prose** — `LMS export - completions 2026-Q2.csv` (structured slots)
  against `Data Protection Essentials - Module 3 - facilitator guide.docx` (prose whose *shape* is
  the evidence).
- **OCR of the same thing** — `Manual Handling refresher - session sign-in sheet.jpg`, a photographed
  paper sheet. It carries `group_without_copying_facts: true`: it may join a cohort group without a
  programme fact being written onto it, per `00`: the graph *"does not automatically copy those
  missing facts onto sparse files."*
- **Archive packet** — `Leadership Programme 2026 - cohort pack.zip`, mixed members including a
  360-degree feedback report that **conflicts** with the packet purpose and is
  `hr.performance-cycle`'s evidence, whose protection must run before the packet's. Manifest
  inspection only; `00`: *"the normal scan should never extract archive contents to the filesystem"*.
- **Email and calendar** — `Course enrolment confirmation - Data Protection Essentials.eml`, which
  also carries a `finance` reading through its seat cost.
- **The two-dimensional shape** — `Mandatory training matrix - FY2026 - all staff.xlsx`, the row's
  cheapest and most disclosing fixture, and the one it contests with `hr.workforce-analytics`.
- **A file that is also another domain** — `Certificate of Completion - Fire Marshal Training - J
  Patel.pdf`, `also_schema: career`. That is a co-hold, not a collision.

The heterogeneous-packet judgement uses `00` verbatim: whether members are *"purpose-coherent
despite topic diversity, which members appear to be supporting materials rather than unrelated
records, and whether any member conflicts with the proposed purpose."*

## The collision fixture

**`Excel Advanced - Udemy - certificate.pdf`.** It looks exactly like this row's evidence and is
not. It names a course, a provider, a person and a date; it is byte-for-byte the same shape as
`Certificate of Completion - Fire Marshal Training - J Patel.pdf`, which *is* this row's evidence.

**What discriminates it: an employer-side provision anchor — an enrolment record, a completion
roster, a training matrix, a seat cost, or a mandatory-training designation — present somewhere in
the corpus.** Not the platform, not the subject, not whose device holds the bytes. Absent that
anchor the certificate is the individual's own credential and `00` already has a home for it:
*"Independent Records may live under Personal/Independent Records and hold standalone certificates,
notices, confirmations, forms, and PDFs that have a durable purpose but no broader group."*

A second collision fixture is carried for the policy seam: **`Safeguarding Policy v3.1.pdf`**, which
the awareness course quotes almost verbatim. Discriminator: approval / version / scope / effective-date
structure (the rule) versus objectives / audience / activity / assessment structure (the teaching of
the rule).

## Files considered and rejected — the tempting false positives

Each of these was a candidate fixture and each is *not* this row's evidence:

- **A conference programme or talk handout.** Sessions, speakers, times, learning-sounding titles —
  and no enrolment, cohort or completion. Routes to Reading Inbox.
- **A product manual or software help export.** Modules, exercises, screenshots, a "getting started"
  sequence. No audience, no assessment, no roster. It is documentation.
- **University lecture slides a colleague shared.** Academic, and `academic.*` owns it; a course-code
  token plus academic context is a rule family this row has no access to.
- **A recruitment assessment or aptitude test.** Quiz shape, pass mark, named candidates —
  `career.recruiting`'s evidence. A candidate is not a learner.
- **A job description saying "full training provided".** The word, alone, in prose.
- **A training budget line or an L&D cost-centre extract.** Finance / `business_operations` unless
  course-level or learner-level structure is present. This is in `never_alone` for a reason: it is
  the most common way "training" appears in a business corpus.
- **The L&D team's own org chart or headcount plan.** `hr.org-design-headcount`. The subject is the
  team that delivers training, not the training.
- **A training-room booking or catering order.** `business_operations.facilities-workplace` and
  Receipts and Confirmations.
- **A CV or LinkedIn export listing courses attended.** `career.*`. Name + date + course-shaped
  title in prose is explicitly barred as sole proof.
- **A `clinical_practice.teaching-material` fixture.** That row **refused** and authors no edges; its
  memo says of this row: *"mandatory training overlaps by employment purpose, not specialty."* I
  accept that and author no edge back. Recorded as a deliberate non-edge.

## Reciprocal boundaries

Nine `collides_with` edges, each naming the same fixture on both sides. The two most load-bearing:

**`career.credentials-licenses`** — the sharpest, because the bytes can be identical. Fixture:
`Certificate of Completion - Fire Marshal Training - J Patel.pdf`. *That row must not take* an
employer's completion roster, training matrix, enrolment record or catalogue merely because each
cell could be copied to the individual it names. *This row must not take* one person's own
certificate, licence, CPD log or renewal notice held as their own qualification evidence with no
employer anchor. `role_split` records the same seam as a role pair, since both are legitimate views
of one person's learning.

**`academic.continuing-education`** (the edge I added) — fixture: a CPD certificate stating credit
hours. *That row must not take* an employer's enrolment, seat cost, cohort or mandatory-training
year merely because a provider issued a credit-bearing certificate. *This row must not take* a
provider's named course of study plus an explicit credit-unit statement held as the individual's own
credit accumulation toward a credential. The credit-hour line is that row's signature; this row has
no equivalent of it, which makes the seam unusually clean.

The remaining seven — `hr.onboarding-offboarding` (induction), `hr.performance-cycle` (the
development plan), `hr.dei-program` (the bias course), `hr.workforce-analytics` (the completion-rate
sheet), `academic.online-course` (the platform course), `business_operations.policy-handbook` (the
policy and its awareness module), `business_operations.go-to-market` (customer enablement) — are
stated in both directions in the JSON with their fixtures. Three of them (`onboarding-offboarding`,
`performance-cycle`, `dei-program`) had already argued the seam from their side and named the
fixture; this row accepts their framing rather than re-litigating it.

## Co-holds removed from the JSON — recommendations for R1c

These four are real co-activations and were deleted only because a template may not author
`also_holds_with`. They are recorded here so R1c can place them (see NJ-TD-3):

1. **`hr.engagement-survey`** — a post-course evaluation is both a listening instrument and a
   learning record. That row holds it where it is fielded as part of a listening programme; this row
   holds it where it is attached to one session and one cohort roster, as
   `Harassment Prevention - post-course evaluation responses.csv` is. The stricter handling governs
   the free-text column.
2. **`hr.workplace-health-safety`** — statutory safety training is simultaneously learning delivery
   and safety-competence evidence. This row holds course, cohort and completion; that row holds the
   competence requirement, the risk assessment it discharges, and the incident context.
3. **`business_operations.compliance-audit`** — a mandatory-training matrix is both a learning record
   and audit evidence that a control operated. The audit row holds the control, finding and sample;
   the per-learner grid and its protection stay here.
4. **`business_operations.vendor-management`** — an external provider's course produces both a
   programme record and a supplier record. Curriculum, cohort and completions here; contract, SOW,
   invoice and provider review there.

## Proposed fields

`fields: []` — the `hr` schema declares none under PR-6 and a template may serialise none.

- **`learning_programme`** — the one genuinely new concept this row contributes upward, and it is
  minted **with its alternative named rather than assumed**. `subject` is the closest canonical key
  and `00` uses it for exactly this concept academically, but its validation rule family is
  course-code-plus-academic-context — `00`: a candidate *"becomes a course fact only when the engine
  finds a course-code pattern together with academic context"* — and an employer course has a prose
  title, no code and none of that context, so the rule that makes `subject` trustworthy cannot fire.
  `work_type` is the wrong altitude (certificate vs deck, not *Fire Marshal* vs *Unconscious Bias*);
  `project` ends, a course is re-run; `people_cycle` is the cohort, and collapsing the two would
  destroy the fact that makes this row distinct. Proposed `destination_eligible: true` — the only
  `hr` key this row would put first, because a programme name is an organisational artefact that
  discloses nothing about any individual.
- **`people_cycle`** — **seconding, not minting.** Already proposed by the schema row. This row's
  added evidence: a cohort, a delivery wave and a renewal year each join a sign-in sheet, a
  recording, an evaluation and a roster that share a date and nothing else. R1c should note that
  here the cycle sits **below** the programme, the reverse of the schema row's prose default.
- **`workforce_member`** — **seconding, not minting.** Added evidence: the training-matrix cell, a
  value that exists only at the intersection of a named learner and a named course, which is a
  stronger and more disclosing join than a name appearing in a document. This row asks R1c to keep
  `destination_eligible: false` here **specifically**, for the course-title leak argued in Leg 3.

## NEEDS-JOSEPH

**NJ-TD-1 — `learning_programme` vs widening `subject`.** Alternatives: (a) mint
`learning_programme` as a role-specific key; (b) widen `subject` beyond academia with a second rule
family for employer courses; (c) refuse both and let programme identity live only as a group label —
which costs this row its recommended first dimension and most of its distinctness. I recommend (a)
and state (b) as a live alternative.

**NJ-TD-2 — may a template recommend a dimension order that contradicts its schema row's prose
default?** This row does exactly that (programme first, `workforce_unit` demoted) and argues the
contradiction from `00`'s intelligibility rule. If a template must instead defer to its schema's
default, this row loses Leg 2 and must be re-tested on Legs 1 and 3 alone — it would still pass, but
the register should record which rule governs.

**NJ-TD-3 — template-level co-activation has no edge.** Four real co-holds were deleted (above).
Alternatives: (a) give template↔template co-activation its own edge; (b) promote these to
`hr ↔ business_operations` schema edges, which loses which template co-holds; (c) accept that a
co-hold between two templates of the **same** schema (the two `hr` cases) is inexpressible and
record it only in prose. Not settleable from `CONNECTION.md`, which asserts the restriction without
addressing the template case.

**NJ-TD-4 — the audience discriminator for the absorbed `soft.training-material` coverage.** It is a
role perspective and `00` bars role perspectives as sole proof. Alternatives: (a) keep it as a
`needs_llm` item with abstention, as now; (b) route staff-vs-customer ambiguity to a residual by
default and require user confirmation; (c) hand the whole product-course world to
`business_operations.go-to-market` and drop the absorbed coverage. I implemented (a) and flag that
it is the row's weakest half.

## Self-verification

- `python3 -m json.tool planning/domains/nodes/hr.training-development.json` → parses.
- All 9 `collides_with` entries are `{domain, signal, provenance}` objects; all 9 signals carry
  `SAME FIXTURE BOTH SIDES:`; `also_holds_with` is `[]`.
- All 13 edge ids checked against `roster.json` `domain_id` values — all present, none dangling.
- All four `falls_through_to` templates are among `00`'s nine residual homes.
- Nine `00` spans quoted in the JSON and this memo were each `grep -c`'d against
  `planning/00-database-agent-product-design.md` and returned 1. No quote is paraphrased.
- Every `file_examples.source_type` is in `SOURCE_TYPES`; `fields: []`; no threshold number, no
  confidence score, no handling class, no regex, no folder path written as a fact.
- Files written: only `hr.training-development.json` and `hr.training-development.research.md`.
