# Research memo — `hr.compensation-planning`

Depth: J-DEPTH
Date: 2026-08-26
Output: `planning/domains/nodes/hr.compensation-planning.json`
Roster row: template on the fieldless `hr` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accept the node**, on one discriminator that survived the charge below: this is the only situation in
the `hr` family whose records are **keyed by a job grade or a plan option rather than by a person or a
population**, and the `hr` schema's default template cannot see it. It is accepted with one minted
proposal (`job_grade`), one dimension-order recommendation that contradicts the schema default, and a
privacy rule that inverts the schema's.

It is accepted *narrowly*. It does not get a reward taxonomy, does not decide what anyone is paid, is
worth, or is owed, and does not treat "before payday" as its definition — that framing is exactly what
nearly killed it.

## Sources actually read

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (in full) and the stamped assignment from
  `make_prompt.py hr.compensation-planning`.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — the depth calibration row.
- `planning/domains/nodes/hr.json` — the schema anchor, read for its default template, its four
  proposed keys, its `recognition` lists, its `work_types` enum, and its `template.why` prose.
- `planning/00-database-agent-product-design.md` — **greped, never streamed**, per the token rule. The
  residual-library paragraph and the stop-rules paragraph are the only spans quoted.
- `planning/domains/roster.json` — greped for the `hr.*`, `career.*`, `finance.*` and
  `business_operations.*` id lists. **Every edge id in the JSON was confirmed against that output.**
- `grep -rl "hr.compensation-planning" planning/domains/nodes/` returned exactly three files;
  `business_operations.budget-forecast.{json,research.md}` and
  `business_operations.board-governance.research.md` were read only at the matched lines.

**A finding worth recording:** `grep -niE "salary|compensation|benchmark|payroll|pay review|bonus"`
over `00` returns **zero hits**. `00` contains no compensation vocabulary at all. Therefore **no claim
in this node may carry `provenance: design`**, and none does — the node is `inference` throughout, and
the only quoted spans are the general residual and stop-rule sentences, used for routing and for the
never-alone rule, not for reward content.

## THE CHARGE — the strongest case that this row should not exist

I put five charges, in descending strength. The third is the one that nearly won.

**Charge 1 — it is a `work_type` value, verbatim, on its own schema.** The `hr` anchor's `work_types`
array literally contains the string `"salary structure, benchmarking, pay-review, bonus, or
benefits-design record"`. That is this row, spelled out as an enum value, and the dispatch prompt is
explicit that work types are values, not nodes.

*Answer:* the charge is true and **it is true of the entire `hr` family**. `"grievance, disciplinary,
capability, investigation, consultation, or appeal record"` is `hr.employee-relations`;
`"workforce census, movement, attrition, absence, cost, or diversity analysis"` is
`hr.workforce-analytics`; each of the eleven strings maps onto one roster sibling. The anchor's
`work_types` list is a *rendering of the row family*, not independent evidence against any member. So
this charge cannot discriminate — it convicts all eleven or none. It is disposed of, but it does mean
**the row's name is not its justification**; something else has to do the work, and I take that as the
burden for the rest of the memo.

**Charge 2 — it is defined by an absence.** The `one_line_hint` says "as distinct from paying it." A
row whose definition is "the part that is not the neighbour" is the failure mode the brief names.

*Answer:* the hint's framing is bad and I did not reuse it. The written `one_line` defines the row
positively — a grid keyed by a grade or a plan option — and every deterministic signal in the JSON is
a positive structure, not the absence of a payroll column. The absence framing survives only inside the
`hr.payroll-benefits-administration` collision, where it is one half of a two-way test.

**Charge 3 — it is a lifecycle stage of `hr.payroll-benefits-administration`.** This is the serious
one. "Decide the pay" then "pay the pay" is a *stage*, and a lifecycle stage is explicitly named in the
brief as a disqualifier. If the only thing separating the two rows were tense, this row should be
refused and its coverage folded into payroll administration.

*Answer, and the reason the node survives:* the separation is not tense, it is **the key of the
record**, and the test does not require knowing any date. A payroll register is keyed by
`employee × pay period` and its columns are gross pay, statutory deductions, employer contributions,
net pay, and a period control total — an executed transaction. A salary structure is keyed by `grade`
and its columns are minimum, midpoint, maximum, and range spread — a *rule with no transaction and no
person in it at all*. Half of this row's corpus contains **no employee**, which no payroll artifact
can say of itself. Even at the point of maximum overlap — the round proposal worksheet, which *is*
employee-keyed — the column sets separate cleanly: *proposed increase / new salary / compa-ratio /
budget envelope* against *deduction / net pay / period total*. A stage boundary would blur under a
detector; this one does not. Charge defeated, and the answer is serialized as the
`hr.payroll-benefits-administration` collision signal.

**Charge 4 — it duplicates `business_operations.budget-forecast`.** A people-cost model and a
compensation plan are, as that row's own memo says, "the same grid with one column different."

*Answer:* `budget-forecast` itself already draws the line and awards **"salary bands"** to this row
(quoted below). Two grids that differ in their *row key* — period columns resolving to an approved
budget line, versus grade rows carrying ranges — are not duplicates; they are a genuine mutex, which is
what the reciprocal edge records. Defeated, but it earns the strongest boundary in the file.

**Charge 5 — it duplicates its own schema's default template.** Applied per CONNECTION §2: a template
exists only where **detection signals, recommended dimensions, or privacy rules** differ from the
schema default.

*Answer:* this is the node test proper, argued leg by leg immediately below. All three legs differ.

## The node test, all three legs

**The schema default I am measured against.** From `hr.json`: seven deterministic signals, every one
of which requires "labelled slots [that] jointly identify an employee or workforce cohort AND a
personnel process"; four proposed keys — `workforce_member` (the person who is the subject),
`workforce_unit` (department, site, reporting population), `people_cycle` (bounded process instance),
`personnel_case` (one ER or safety matter); a `dimension_order` of `[]` with a prose default of "work
type or named people programme first; then workforce unit or cohort …; then people cycle"; and a
privacy posture built around employee-identifying content.

**Leg 1 — detection signals differ, and the schema default has a hole this row fills.** Run
`Salary structure FY27 - grades and ranges.xlsx` against the schema's seven deterministic signals. It
identifies **no employee** (there is no name and no ID column), **no cohort** (no department, no
population, no headcount), and **no process instance** (no round, no run, no review period). It fails
all seven, and on the schema default **`hr` would not activate on it at all**. The same is true of the
job-evaluation scorecard, the survey match table, the merit matrix, and the plan-option comparison —
five of the fifteen fixtures. That is not a stylistic difference in signals; it is a class of employer
personnel record the schema's default template is structurally blind to. The row's first deterministic
signal — a grid whose row key is a grade, band, level, or job-match code, with range or percentile
columns — exists nowhere in the anchor.

**Leg 2 — the recommended dimensions differ, and differ in an argued way.** PR-6 forces the serialized
`dimension_order` to `[]`, so like every `hr` template this row cannot differ in the *array*. It
differs in the *recommendation*, which is what R1c will adjudicate. Uniquely in this family, the corpus
splits in two. **Standing** instruments — the grade ladder, job evaluations, the survey library — are
round-independent and are correctly ordered work-type-first with grade at the leaf, their revisions
carried by `version_family`. **Round-bounded** instruments — the matrix, the unit worksheets, the
budget reconciliation — are uninterpretable outside their round: a matrix cell reading three-and-a-half
percent means nothing without knowing which round, which is `00`'s own homework-needs-the-course
argument. For those, `people_cycle` should lead — **first**, not third as the schema default has it.
No other `hr` row has a standing/instance split; a grievance file is always case-bounded, a survey wave
always wave-bounded. This is a real, defensible departure from the default recommendation.

**Leg 3 — the privacy rule differs, and inverts.** The schema protects material *because* it
identifies a person. Here the **least personal files are among the most sensitive**: a range table, a
merit matrix, and a licensed survey result set name nobody and still expose pay-equity position,
negotiation posture, and third-party data carrying redistribution restrictions printed on the file
itself. The operational consequence is a rule the schema default would not produce — *absence of names
is not a reason to relax handling* — and it is serialized in `sensitivity_why`. The round worksheet is
strict for a second reason: it puts a named person's current salary, performance rating, and proposed
increase **on one row**, a combination neither a payslip nor a review form produces alone.

Three legs, three differences. The node is not a disguised file-kind, not a stage, and not a copy of
its template. **Accept.**

## Files considered and REJECTED — the tempting false positives

A row that only lists what it holds has not been researched. These were considered and are **not** this
row's evidence:

- **`Payslip Feb 2026.pdf`** — an executed transaction addressed to one person; it evidences what *was
  paid*, never how a range was set. `finance.payroll-received`.
- **`Employment contract - executed.pdf`** — salary, bonus target and grade, but an individually
  addressed instrument. `career.employment-records`; see the collision fixture below.
- **`Job advert - Senior Analyst - £55-65k.pdf`** — superficially the closest match on this list: a
  title and a salary range in one file. Rejected because the range advertises *one vacancy*; there is
  no grade, no midpoint, no spread, no second row. `career.employer-side-hiring` by holder role.
- **`Compensation philosophy and pay policy v4.pdf`** and **`Employee handbook - benefits chapter.pdf`**
  — kept as a fixture precisely because it is a false friend. A version table, owner, approval date,
  next-review date and handbook numbering mark a governed standing rule, not a bounded-year instrument.
  `business_operations.policy-handbook`.
- **`Recruiter fee schedule.pdf` / `HR consultancy invoice.pdf`** — money plus HR words plus a job
  title, but a vendor transaction. `business_operations.vendor-management`.
- **`Benefits enrolment file 2027.csv`** — design is keyed by *option*, enrolment by *person*.
  `hr.payroll-benefits-administration`.
- **`Salary comparison - my next move.xlsx`** — an individual researching their own worth with the same
  percentile columns as a survey file. `career`; the holder is the subject, not the employer.
- **A compensation-planning SaaS export or live HRIS connection** — a source system, not a file node. A
  bounded export with a readable manifest is represented (`Comp round 2026 - manager pack.zip`).
- **Grade, band, and job-architecture vocabularies themselves** — deliberately not enumerated; grade
  schemes are employer-specific and inventing one would be the gazetteer fabrication R4 forbids.

## THE COLLISION FIXTURE

**`Offer letter - A Okafor - Senior Analyst.pdf`.** It contains *every single token this row
recognises*: a grade, an annual salary, a bonus target percentage, a benefits summary, and an employer
letterhead. A naive detector built on reward vocabulary fires on it with high confidence.

**What discriminates it:** the file is an **instrument addressed to one individual**, and its
population is one. There is no second row, no range, no midpoint, no matrix, no round label, and no
budget envelope. This row's artifacts are *rules and grids*; that file is an *executed instrument*.
It is `career.employment-records` in a personal corpus, and it becomes this row's evidence only as a
member of an employer-held generation batch or template set carrying a round or plan-year anchor.

The corresponding **never_alone** — "a currency amount beside a job title" — is written specifically so
that this fixture trips it. Offer letters, adverts, recruiter emails, consultant quotes, invoices, and
CVs all carry that pair.

A second collision worth naming: **`FY27 people cost model.xlsx`**, held as a fixture and routed to
`business_operations.budget-forecast`. It fails this row not because it lacks names — half of this
row's corpus lacks names — but because its grid resolves to an **approved period budget line** rather
than to a grade ladder.

## Reciprocal boundaries — both directions, same fixture named on each side

| Neighbour | Their side takes | This side takes | Shared fixture |
|---|---|---|---|
| `hr.payroll-benefits-administration` | gross pay, statutory deductions, employer contributions, net pay, pay-period control total; enrolment keyed by employee | proposed increase, new salary, compa-ratio, rating, unit budget envelope; plan comparison keyed by option | one employee-keyed salary grid — the round worksheet vs the register |
| `hr.org-design-headcount` | approved posts, vacancies, FTE, reporting lines, structural moves | pay ranges, market percentiles, increase guidelines, plan targets attached to the same grade | one establishment plan carrying a cost column per post |
| `hr.workforce-analytics` | a population measurement series with period-over-period cuts and a reporting output | workings held against a named structure version or round, produced to move ranges or set a budget | `Pay gap analysis 2026 - draft workings.xlsx` |
| `career.employment-records` | an individually addressed instrument in a personal corpus | the same bytes as a member of an employer-held generation batch with a round or plan-year anchor | the offer letter and the total reward statement |
| `business_operations.budget-forecast` | period columns resolving to a submitted-and-approved budget line | grade rows with range or market columns, or a rating-by-range matrix | `FY27 people cost model.xlsx` |
| `business_operations.policy-handbook` | version table, owner, approval and next-review date, handbook numbering | plan year, eligible population, targets keyed to grade, payout curve | `STI plan rules FY2026` vs `Compensation philosophy v4` |
| `finance.cap-table-equity` | grantee identity, share counts, strike price, vesting, instrument ids | grant *value* bands keyed to grade with no grantee | one equity grant guideline table |

**On `business_operations.budget-forecast` specifically.** That row landed first and authored the
boundary one-way. Its own words, verified at
`business_operations.budget-forecast.json:405`: *"named individuals, salary bands, or personal review
outcomes support the hr row and must be protected before any model path; roles, FTE counts and
aggregate cost support this row. A single spreadsheet frequently crosses that line at one column, and
when it does the stricter side wins."* I have authored the return edge on the **same fixture** and in
compatible terms, and added the test that does not depend on names, since their formulation cannot
classify a salary structure containing no people at all. **R1c owes nothing here — the edge is now
two-way.** The other six edges are authored one-way from this side and R1c owes the returns.

`also_holds_with` carries one entry: `finance.insurance-corporate` on the benefits renewal fixture,
where a group plan-design comparison is genuinely *both* an employer reward instrument and a corporate
insurance record — the insurer, option, tier, and premium are insurance facts; the contribution split
and employer cost are reward facts. Per `00`'s abstract-that-is-also-an-application-document case, that
is co-holding, not a collision.

`role_split` is **empty**, for the same reason it is empty on `legal.practice-matter-file`: the schema
declares no fields, so no key pair can be named on either side. The holder-role seam that would
otherwise be a role split — employer vs individual, over the same person — is expressed as the
`career.employment-records` collision instead.

## Neighbours considered that got NO edge, with reasons

- **`business_operations.board-governance`** — remuneration-committee papers are genuinely both
  governance and reward material and the edge is tempting. **That row already considered and refused
  it**, reasoning that the material only crosses when it names individuals, that the schema anchor
  states that rule family-wide, and that restating it would be CONNECTION §9 duplication rather than
  coverage. I checked whether this side has a discriminator they lacked — the remuneration appendix is
  a *structure or benchmarking exhibit*, not merely a named list — and judged it insufficient to
  overturn a considered refusal by a landed row. Deliberate non-edge, routed to `open_question`.
- **`finance.payroll-received`** — the payslip's mutex is with `hr.payroll-benefits-administration`,
  which owns the register side. An edge here would put the boundary in the wrong place.
- **`career.recruiting` / `career.employer-side-hiring`** — the salaried job advert. The holder-role
  seam is already carried by `career.employment-records`; a second career edge adds no discriminator.
- **`business_operations.vendor-management`** — the broker and survey-vendor *relationship* is theirs
  and uncontested; only the returned data is mine. No shared fixture.
- **`finance.small-business-bookkeeping`** — the paybill in a ledger collides with `budget-forecast`
  and payroll administration, not with a grade ladder.
- **`hr.performance-cycle`** — looks like a collision until the fixtures are compared: a review form is
  keyed by employee-and-review-period and carries no money; the matrix is keyed by
  rating-and-range-position and carries no employee. They share a *value*, not evidence. No edge.

## `proposed_fields` justification

**`job_grade`** is the row's one mint, and its necessity is the cleanest evidence for leg 1. None of
the schema's four proposed keys can key a salary structure: `workforce_member` is a person,
`workforce_unit` is a department or site, `people_cycle` is a process instance, `personnel_case` is a
matter. A grade is none of those — it is a levelling assignment attached to a **job**, and it is the
literal row key of five of the fifteen fixtures. Folding grade into `workforce_unit` would repeat
exactly the ambiguity the anchor rejects when it refuses to let `organization` mean department, entity,
cost centre, and location at once. It is proposed `destination_eligible: true` — a branch named
`Band 6` discloses no individual — but must never lead and must not become a one-child collector.
`reliability_ceiling: possible`, because grade vocabularies are employer-specific and are renamed at
every restructure; validation would need an employer grade roster this row may not invent.

**`people_cycle`** is **reused verbatim from the anchor, not minted**. It appears in
`proposed_fields` only because this row makes a stronger ordering claim about it than the schema does
(leg 2). R1c should treat it as one proposal, not two.

`fields: []` and `template.dimension_order: []` are correct and intentional under PR-6.
`time_first: false` — an effective date, a survey data date, a plan year, and a document creation date
routinely sit on one page and mean four different things.

## NEEDS-JOSEPH

- **NJ-1 — mint `job_grade` or not.** Alternatives: (a) mint it as proposed, accepting one more key in
  the `hr` vocabulary; (b) refuse it and leave this row's signature artifact with no legal fact, which
  makes the row's acceptance argument true but unserviceable; (c) generalise it to a cross-schema
  `level` key that academic, military, and civil-service rows could share, at the cost of the same
  ambiguity the anchor rejected for `organization`. This row recommends (a) and flags (c) as the only
  serious alternative.
- **NJ-2 — same-schema co-holding.** `Pay gap analysis 2026 - draft workings.xlsx` genuinely belongs to
  both this row and `hr.workforce-analytics`, but CONNECTION frames `also_holds_with` as one file
  carrying **both schemas**, and these are two templates on **one** schema. I recorded it as
  `collides_with` to stay inside the closed vocabulary. Alternatives: extend `also_holds_with` to
  same-schema template pairs; or accept that same-schema siblings can only ever collide. This affects
  far more rows than this one.
- **NJ-3 — the remuneration-committee pack.** `business_operations.board-governance` refused the edge
  with a stated reason; this row honoured the refusal. R1c should confirm the non-edge is correct on
  both sides, or author it on both at once.
- **NJ-4 — third-party licensed data.** Survey result sets carry redistribution restrictions printed on
  the file. The catalogue can observe the notice but must not decide a licence question; whether such
  an observation should influence residual routing is a P7 policy matter, not this row's.
- **NJ-5 — the standing/round dimension split.** Leg 2 recommends two different orders for two halves
  of one corpus. If R1c decides a template may recommend only one, default to the standing order and
  treat round-bounded material as a grouping concern instead.

## Self-verification

- `python3 -m json.tool` parses cleanly. `fields: []`; both `proposed_fields` argued and marked
  `adjudicate: R1c`. Every `file_examples.source_type` is in `SOURCE_TYPES`.
- All eight edge ids were confirmed present in the `roster.json` id grep. All four `falls_through_to`
  names appear verbatim in `00`'s residual-library paragraph, together with *"Protected Records may
  represent sensitive isolated material … it should normally remain local-only and must not cause
  filenames or content to be exposed in model prompts."*
- Both `00` spans quoted inside the node — *"the system should not infer a purpose from their filename
  alone"* and the university-name-alone sentence — grep-verified before writing, as was the
  `budget-forecast` span. No `provenance: design` is claimed anywhere, because `00` carries no
  compensation vocabulary at all.
- No threshold numbers, no confidence scores, no handling classes; sensitivity is
  `potentially_sensitive` only. Only the two assigned files were written.
