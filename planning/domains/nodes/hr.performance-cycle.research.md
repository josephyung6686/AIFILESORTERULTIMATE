# Research memo — `hr.performance-cycle`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/hr.performance-cycle.json`
Roster row: template on the fieldless `hr` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accept, narrowly, and on a different argument from the one the row's name suggests.** The row survives
not because "performance reviews are a kind of HR document" — that is a work-type value and would have
been a refusal — but because a review round is the one HR world that produces a **matched set of
role-differentiated documents about the same subject over the same period**, and that set has two
consequences no other row and no schema default has: it must be grouped **without** being collapsed as
duplicates or versions, and its members carry **different exposure tiers inside a single packet**.

Those are a grouping rule and a privacy rule. They are what the node test asks for.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (full).
- Stamped assignment via `make_prompt.py hr.performance-cycle`.
- `planning/domains/nodes/hr.json` — the schema anchor, read in full. This is the row I am measured
  against and it is quoted below from its own text.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — one landed launch row, for depth
  calibration.
- `planning/00-database-agent-product-design.md` — targeted greps only, per the token discipline.
  Two spans verified verbatim and quoted below.
- `planning/domains/nodes/business_operations.strategy-plan.{json,research.md}` — the only landed row
  that already argued a boundary against this id (found by `grep -rl`).
- `planning/domains/roster.json` — confirmed every edge id exists: `hr.compensation-planning`,
  `hr.employee-relations`, `hr.workforce-analytics`, `hr.training-development`,
  `business_operations.strategy-plan`, `business_operations.go-to-market`,
  `career.employment-records`.

Verbatim `00` spans relied on:

> "Purpose must be a first-class facet. Topic answers what a file is about, while purpose answers what
> the file was for."

> "Protected Records may represent sensitive isolated material such as passport scans, medical
> documents, account statements, visas, legal forms, or credentials; it should normally remain
> local-only and must not cause filenames or content to be exposed in model prompts."

The first is the licence for treating a review round as a purpose packet whose members are
content-diverse. The second is the residual routing quote in `falls_through_to`.

## THE CHARGE — the strongest case that this row should not exist

I put four prongs against the row before writing anything. The first is genuinely dangerous.

### Prong 1 (the serious one): it is a duplicate of its own schema's default template

The `hr` anchor does not merely permit performance material — it already **names** it. Its
`recognition.deterministic` contains, verbatim from `hr.json`:

> "a performance-cycle packet whose page-one or workbook labels combine review period, employee,
> manager, rating or calibration, goals, and outcome fields. A generic goals document is never enough"

Its `work_types` already contains "performance objective, review, calibration, rating, or
improvement-plan record". Its `grouping_reasons` already contains "one bounded people cycle: intake,
payroll run, review round, survey wave, pay review, consultation, or training cohort". And one of its
ten `file_examples` is `Annual review calibration - Customer Ops.xlsx` — the same fixture I would
reach for first.

So the anchor already fires on my evidence, already enumerates my work types, and already groups my
round. Under CONNECTION's node test — a template exists only where detection signals, dimensions or
privacy rules **differ** from the schema default — this looks like a straight refusal.

### Prong 2: it is a lifecycle stage

Hire → onboard → perform → develop → exit. `hr.onboarding-offboarding` takes the ends,
`hr.training-development` takes develop, and "performance cycle" is the middle stage. Stages are not
filing worlds.

### Prong 3: it is a work_type value

"Performance review" is a document type. The stamped prompt is explicit that `work_types[]` is an enum
of values and that a child node per work type is the 574's error.

### Prong 4: its evidence is never-alone

Performance, review, rating, feedback, goals, objectives, 1:1, scorecard. Every one of those words
appears in a quarterly business review, a design review, a code review, a vendor scorecard, a peer
review, a product review, and a sales dashboard. A row whose evidence is a vocabulary cannot activate.

## Defeating the charge

**Prong 3 falls first, and its fall weakens Prong 1.** The row is not the value "performance review
document." A review round has members drawn from *ten* different work types (goal record,
self-assessment, manager assessment, peer response, calibration worksheet, outcome record, check-in
note, improvement plan, timetable, acknowledgement) and from *nine* source types including email,
calendar, OCR and archive. The anchor's list collapses five of those ten into one enum value. The row
is the container; the anchor's value is one member. `00`'s purpose clause is exactly this shape: the
members are content-incoherent and purpose-coherent, and a content-similarity system will split them.

**Prong 2 falls on recurrence with identity.** Onboarding is a transition: it terminates on
completion and there is one of it per person. A review round **recurs with a name**, and FY25, FY26
and FY27 co-exist as distinct corpora about the same person that the user needs side by side — the
FY25 review is the evidence in an FY27 promotion argument. A stage that produces named, co-existing,
cross-referencing instances is a grouping anchor, not a stage.

**Prong 1 — the real work.** Three differences from the anchor's default, each of which changes
behaviour rather than restating it:

1. **The assessing-role slot.** The anchor's signal requires "review period, employee, manager,
   rating or calibration, goals, and outcome fields." It does not require, and does not use, the
   *completed-by role*. This row's first and second deterministic signals do. That is what separates
   `FY26 Mid-Year Self-Assessment - J Patel.docx` from `FY26 Mid-Year Review - J Patel - manager.docx`
   — two files with the same boilerplate, the same headings, the same subject and the same period,
   differing only in one slot.

2. **A grouping rule the anchor cannot state: an anti-collapse rule.** Those two files will look to
   the universal `duplicate_family` / `version_family` machinery like v1 and v2 of one document. They
   are not versions. They are independent statements by different roles, and merging them is both a
   correctness error and a confidentiality event. The anchor's grouping reason ("one bounded people
   cycle") is a *positive* rule; it has no negative rule because no other people cycle produces
   near-identical bytes from different authors. A payroll run has one author and many subjects. An
   intake tracker has one author and many tasks. An engagement survey has many authors and one subject
   — the organisation — and its anonymity is a design property, not an accident. Only a review round
   has *same subject × same period × different role* → near-duplicate bytes that must stay apart.

3. **A privacy rule the anchor does not have.** The anchor's posture is uniform: protect
   employee-identifying content. This row's is **asymmetric inside one packet**. The subject
   legitimately holds the self-assessment, the outcome letter and the acknowledgement; the subject
   legitimately must **not** hold the calibration worksheet, another manager's pre-calibration notes,
   or attributable peer responses gathered under a promise of aggregation. `FY26 review packet -
   J Patel.zip` contains both classes of member. No other HR row has a packet whose members are
   selectively visible **to the person the packet is about**.

**Prong 4 falls to the fixtures, not to an assertion.** I built two files specifically to trip a
vocabulary-only reading — `Q2 Business Review - EMEA.pptx` and `Sales rep performance dashboard -
Aug 2026.xlsx` — and the `never_alone` list is written so that both fail. See the collision section.

Verdict: accept. The row's honest one-line is "the round, not the review document."

## The node test, all three legs

**Leg 1 — detection signals differ from the schema default.** Yes, and specifically. The anchor asks
for review period + employee + manager + rating + goals + outcome. This row adds three signals the
anchor does not carry: the assessing-role slot; the co-occurrence of two instruments sharing
boilerplate and subject but differing in that slot; and the **proposed-to-calibrated pair** as the
discriminator for a moderation worksheet. That last one matters — a single rating column is a
scorecard (an interview scorecard, a supplier scorecard), and only the *pair* proves a moderation
event happened.

**Leg 2 — dimension order differs.** This is the weakest leg and I will not overstate it. Both
`dimension_order` arrays are `[]`, because `hr` declares no canonical fields under PR-6 and a template
may not mint a dimension its schema has not licensed. The landed `legal.practice-matter-file` faced
the identical situation and passed on the other two legs. What I can say honestly is that the *prose*
recommendations are inverted, so the difference becomes real the moment R1c ratifies keys: the anchor
recommends **work type first, then workforce unit, then people cycle**; this row recommends **cycle
first, then work type, then unit**. The reason is `00`'s own parent-dimension argument — a
self-assessment or a calibration extract is unintelligible without the round it belongs to, the same
way a homework item is unintelligible without its course. Second, `time_first` is false here for a
stronger reason than the anchor's: FY27 goal setting is authored *while* the FY26 round is still in
calibration (`FY27 Goals - J Patel - draft.docx`), so a creation-date-led order does not merely fail
to help, it actively splits one round across two years.

**Leg 3 — privacy rules differ.** Yes, and this is the strongest leg. See the asymmetric-exposure
argument above and `sensitivity_why` in the JSON. It is also the source of NJ-HR-PC-1, because the
contract has one sensitivity value per file and no way to express a tier inside a packet.

Two legs pass decisively, one passes conditionally and honestly. Accept.

## Files considered and rejected

These are the tempting false positives. Each was a candidate fixture and each is not this row's
evidence.

- **A blank review form or the review-cycle guidance document.** No completed subject, no submitted
  state. This is a controlled corporate document and belongs to
  `business_operations.policy-handbook`. Rejected as evidence; kept in `never_alone`.
- **`Q2 Business Review - EMEA.pptx`.** Rejected — see the collision fixture section; it is the
  primary one.
- **`Sales rep performance dashboard - Aug 2026.xlsx`.** Named individuals, a score per person, a
  ranking column. Structurally near-identical to a rating distribution. Rejected because it is
  continuous rather than bounded, has no reviewer role, no assessment narrative and no round; its
  columns are territory and product, not competency and objective. It routes to
  `business_operations.go-to-market`.
- **An interview scorecard for a job candidate.** Assessing role present, rating scale present, named
  subject present, and a hiring round that recurs. This one is genuinely close. It is rejected because
  the subject is not an employee and the round is a requisition, not a review period — it is
  `career.employer-side-hiring`. This is why `never_alone` says a name beside a score is not enough.
- **A 360 supplier or vendor scorecard.** Multi-rater, rated subject, periodic. Rejected: the subject
  is an organisation, so `business_operations.vendor-management` holds it.
- **An org chart with a grade or potential column.** Rejected — no assessment instrument;
  `hr.org-design-headcount`.
- **A team retrospective.** Recurring, evaluative, discusses what went well. Rejected: the subject is
  a process or a sprint, not a person; `business_operations.retrospective-postmortem`.
- **An engagement survey response file.** Recurring, periodic, about people, sensitive. Rejected: the
  subject being assessed is the *organisation*, the authors are the employees, and anonymity is a
  design property of the instrument. That is `hr.engagement-survey` and the direction of assessment is
  the discriminator.
- **A payslip or a bonus statement.** Rejected: no assessment instrument. Compensation or `finance`.
- **A training completion certificate.** Rejected: delivery of a learning activity, not assessment of
  a period; `hr.training-development`.

## The collision fixture

**`Q2 Business Review - EMEA.pptx`.**

It carries the word Review in its title, a fiscal quarter token, RAG *ratings*, targets, named
individuals with owner labels, and a slide headed **People** listing team changes. A row that
activated on performance vocabulary would take it, and it would be one of the worst possible errors —
a commercial deck routed into a protected personnel branch, and a whole business unit's revenue
figures acquiring an HR privacy posture.

What discriminates it: **every row is a metric or an initiative; no person is the assessed subject.**
There is no rating scale applied to a person, no assessing role, no review period bounded to an
individual, and no instrument. The People slide names people as *the subject of changes*, not as the
subject of assessment. The discriminator is the direction of assessment — the deck assesses the
business, and mentions people; a cycle instrument assesses a person, and mentions the business.

A second, subtler collision: `Q3 OKRs - Growth team.xlsx`, tab by tab. That one is not resolved here;
it is NJ-HR-PC-3 and it is stated reciprocally below.

## Reciprocal boundaries

Six `collides_with` edges, each written in both directions and each naming the same fixture on both
sides. The full text is in the JSON; the fixtures are:

| Neighbour | Shared fixture | Discriminator |
|---|---|---|
| `hr.compensation-planning` | `Annual review calibration - Customer Ops.xlsx` with a merit column; `Merit increase letter - J Patel - effective 2026-04-01.pdf` | assessments of people vs money allocations |
| `hr.employee-relations` | `Performance Improvement Plan - J Patel - signed.pdf` | presence of a formal case apparatus, not severity of rating |
| `hr.workforce-analytics` | a rating-distribution export from the calibration workbook | is a person the row and the decision, or a member of a cut |
| `hr.training-development` | an IDP attached to a review outcome | assesses the period just ended vs delivers a learning activity |
| `business_operations.strategy-plan` | `Q3 OKRs - Growth team.xlsx` | per-person tab with review period + rating scale + reviewer role |
| `career.employment-records` | `FY26 Mid-Year Review - J Patel - manager.docx` in the subject's own possession | employer-side round structure, not whose device holds the bytes |

The `strategy-plan` edge is genuinely reciprocal already: that row's landed memo names
`hr.performance-cycle` on its own boundary table with the fixture `OKRs Q3.xlsx` and defers the
resolution as NJ-BO-SP-1, writing that "the cascade means one file often holds both, tab by tab." I
have adopted its fixture and its framing rather than inventing a competing one, and I have **not**
edited that row. **Recommendation to R1c:** align the two fixture filenames (`OKRs Q3.xlsx` there,
`Q3 OKRs - Growth team.xlsx` here) so the pair is machine-checkable.

The `career.employment-records` boundary is also expressed as the row's single `role_split`, because
it is a holder-role split rather than an evidence ambiguity: the *same bytes* are the employer's
instrument and the individual's employment evidence depending on who holds them and whether a round
exists around them.

## Neighbours considered that did NOT get an edge

- `hr.onboarding-offboarding` — a 30/60/90-day plan looks like goal setting. No edge: a probation plan
  is bounded by a start date and terminates on confirmation; it never enters calibration and has no
  population round. If a firm runs probation reviews *through* the review cycle, that is a
  configuration, not a shared fixture.
- `hr.dei-program` — representation analysis of promotion and rating outcomes is real, but it consumes
  this row's output rather than competing for the same bytes. That competition is already carried by
  the `hr.workforce-analytics` edge; a second edge would be duplication.
- `hr.payroll-benefits-administration` — a merit increase reaches payroll, but the payroll register is
  a different artefact with different rows. The compensation edge covers the confusable case.
- `business_operations.meeting-record` — a review conversation is a meeting. No edge: a meeting record
  minutes a discussion; a review instrument records an assessment of a person against a scale. The
  `never_alone` entries handle the vocabulary overlap.
- `legal.practice-matter-file` — a contested rating can become evidence. No edge from here: the
  handover is via `hr.employee-relations`, which owns the case apparatus. Adding a legal edge would
  route routine reviews toward a litigation posture on the strength of a hypothetical.
- `finance.payroll-received` — the individual's own merit letter. Covered by the `career` role_split;
  a finance edge would be a third copy of the same seam.

## `proposed_fields` — deliberately empty, and why

`fields: []` and `proposed_fields: []`.

The tempting mint was a `reviewer_role` or `assessing_role` key, since the whole acceptance argument
turns on that slot. I did not mint it, for a reason worth recording: **it is already carried by
`work_type`.** "self-assessment", "manager assessment or review of record", and "peer, upward,
skip-level or multi-rater feedback response" are three of this row's ten `work_types` values, and the
stamped prompt is explicit that work types are values on a field, not new keys. Minting
`reviewer_role` would be minting a synonym for a value that already exists — exactly the failure the
brief warns about.

For the round anchor I reuse the `hr` anchor's existing `people_cycle` proposal rather than minting a
review-specific variant, per the brief's instruction to reuse an existing proposal. NJ-HR-PC-4 records
the risk that `people_cycle` is too broad — it currently spans a payroll run, an intake and a review
round, which are three different kinds of boundedness — and leaves the split to R1c.

## Grouping without copied facts

`1-1 notes - J Patel.md`, the platform notification email, and the review-tool screenshot are all
sparse: they carry no review period, no rating scale and no template structure. They join an accepted
round by membership and acquire **no** subject, cycle, rating or period fact. This is the
`HW 3.pdf` case named in the stamped prompt, and all three are marked
`group_without_copying_facts: true`.

The archive `FY26 review packet - J Patel.zip` is also marked true, for a different reason: its
manifest may be read without unpacking, and its members must not inherit one another's exposure
posture merely because they share a container.

## NEEDS-JOSEPH

Four, all carried verbatim in the JSON's `open_question`, summarised here with their alternatives:

- **NJ-HR-PC-1 — intra-packet exposure tier.** The defining privacy property of this row cannot be
  expressed in the current contract, which carries one sensitivity value per file. (a) strictest
  member governs the packet — safe, but hides a person's own review from them; (b) P7 carries a
  per-member tier keyed on the author-role slot — correct, but needs a fact `hr` does not declare.
  This row assumes (a).
- **NJ-HR-PC-2 — duplicate/version suppression.** Self-assessment vs manager assessment are
  near-identical bytes. (a) a universal exception when a completed-by slot differs, which requires
  promoting that slot to a fact; (b) leave the collapse to user review, which risks a confidentiality
  event at the moment the user is least attentive. Not settleable from the design docs.
- **NJ-HR-PC-3 — the OKR cascade**, reciprocal with `business_operations.strategy-plan`'s
  NJ-BO-SP-1 over the same workbook. (a) whole file to `strategy-plan` with this row's posture applied
  to the person tab; (b) tab-level split, which requires member-level activation the contract does not
  define. Stated, not resolved.
- **NJ-HR-PC-4 — is `people_cycle` the right anchor**, or does a review round need a key distinct
  from a payroll run and a joiner intake? This row reuses rather than mints; if R1c splits the key,
  this row's grouping anchor moves with it.

## Recommendations to R1c (no file edited outside my two)

1. Align the OKR fixture filename between this row and `business_operations.strategy-plan`.
2. When adjudicating `hr`'s four proposed keys, treat NJ-HR-PC-4 as a fifth question: `people_cycle`
   currently means three structurally different kinds of bounded round.
3. NJ-HR-PC-2 is not local to this row — it is a universal `duplicate_family` / `version_family`
   question that this row happens to surface first. It should be adjudicated at the P9 level, not on
   an HR template.

## Self-verification

- `python3 -m json.tool` parses the node cleanly.
- Both quoted `00` spans were extracted by grep from `planning/00-database-agent-product-design.md`
  and are verbatim. No other span is in quote marks and attributed to `00`.
- The `hr.json` span quoted in the charge section was copied from that file's own
  `recognition.deterministic` array.
- Every edge id checked against `planning/domains/roster.json`.
- Every `falls_through_to` template is one of `00`'s residual homes: Protected Records, Independent
  Records, Review Later, Temporary Screenshots.
- Every `file_examples.source_type` is in `SOURCE_TYPES`; no file example writes a folder path as a
  fact; no threshold, score, count or handling class appears anywhere.
- Only `planning/domains/nodes/hr.performance-cycle.json` and this file were written.
