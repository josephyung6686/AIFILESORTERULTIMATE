# business_operations.project-delivery — lab notes (template row, deepened to J-DEPTH)

**Depth: J-DEPTH.** Deepened from the gist draft under `DEEPEN-ADDENDUM.md`. The gist draft's facts
were checked and its arguments were sound as far as they went; this pass preserves them, argues the
node test leg by leg against the now-stated family default template, answers three charges the gist
never faced, authors three new reciprocal boundaries, and **escalates one carried-forward assumption
into a refusal-shaped open question**. What changed is listed at the end and has been checked line by
line against the JSON actually written.

This row is the nearest thing `business_operations` has to a spine: two siblings define themselves by
reference to it. `retrospective-postmortem` was charged with being a `work_type` of it;
`risk-register` was charged with being an artefact inside it. Both argued their way out. A spine that
cannot say clearly what it *is* cannot carry rows that define themselves by what they are *not*, so
this memo states this row's side of both boundaries reciprocally and without contradicting either.

## Sources

`planning/00-database-agent-product-design.md` (every quotation below machine-verified verbatim by
`grep` against the file), `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`,
`planning/domains/CONNECTION.md` (§2 node test, §4 activation), `planning/domains/canonical_fields.json`,
`planning/domains/roster.json`, `planning/overnight/council/DECISION-BRIEF.md` (D1–D6 and J-IND
ratified, not re-argued), `planning/domains/ROSTER.md` §4 and Appendix A (lines 811, 813, 814).

Read in full before writing, and **not edited**:

- `business_operations.research.md` — the deepened schema anchor. It states the family's default
  template and the never-alone principle for all 24 siblings. Both are applied explicitly below.
- `business_operations.organisational-records.json` — the family's one refusal, and the source of
  the never-alone principle. Read as the standard this row had to clear.
- `business_operations.risk-register.research.md` (deepened) — read for its answer to charge (b),
  which names this row.
- `business_operations.retrospective-postmortem.research.md` (gist) — read for its three grounds for
  standing apart from this row.
- `construction_property.construction-project.research.md` (deepened) — the equivalent spine on
  another schema, read for its leg-1 structures and its boundary table, which names this row.

Legacy rows absorbed per Appendix A: `ops.project` (ROW), `ops.status-report` (FOLD),
`ops.programme-portfolio` (FOLD — carried under protest; see the open question).

## What it is for, and what it holds

Someone has a bounded piece of work with a start, an intended end and a named owner, and needs to say
what it is, when it will happen, what could stop it, how it is going, and when it is finished. The
row holds charters and terms of reference, plans and schedules (including proprietary scheduling
binaries), RAID and decision logs, recurring status reports, steering-group packs, change requests,
portfolio roll-ups, and closure, acceptance and handover records.

The evidence that this is a real filing situation and not a management fashion is that the material
is **content-incoherent and purpose-coherent** — `00`'s own phrase for exactly this: a charter, a
schedule export, four status decks, a blank issue form and a signed acceptance page share almost no
vocabulary and no shape, and belong together anyway. `00`: *"The documents are content-incoherent but
purpose-coherent."* That sentence is the strongest single piece of design support this row has, and
it is why the row is defined by an anchor rather than by a document type.

---

## The node test, argued leg by leg against the family default template

CONNECTION §2: a template row exists only where its **detection signals**, its **recommended
dimensions**, or its **privacy rules** differ from its schema's default template. The schema anchor
now states that default explicitly, so this test can be run against a real paragraph rather than
against an idea of one. The default:

> the **organisational unit or entity** *only where the corpus genuinely spans more than one* → the
> **governance body, project, contract, or account** the material belongs to → the **fiscal period**
> → the **document function**. Not time-first.

Note the difficulty this creates immediately, and which the gist draft never confronted: **the word
"project" is already inside the family's default template.** This row's anchor is a level of the
default. That is not fatal, but it means leg 2 cannot be won by naming the anchor, and it means
leg 1 must be argued on the *order of the remaining levels*, which is a narrow win. Stated up front
rather than buried.

### Leg 1 — recommended dimensions

`template.dimension_order` is `[]` **by contract, not by judgement** — `_CONTRACT` rules 10 and 15
and PR-6: a dimension may only branch on a field the same schema declares, and `business_operations`
declares none under D1's deferral as narrowed. The recommendation is therefore held as prose, exactly
as the schema anchor and `construction_property.construction-project` hold theirs.

This row recommends **project → document function → reporting period**. The family default is
**project → fiscal period → function**. The last two levels are inverted, and here is the argument
for the inversion:

- In the rest of this family the period *defines the exercise*. A budget round, a board year, a
  filing year — the period is the thing being run, and the documents are its outputs. Function below
  period is right there: *FY26 → variance report* reads correctly.
- In this row the period is a **leaf that distinguishes members of one function**, and nothing else.
  Twelve status decks are twelve instances of one function differing only by period. Under the family
  default they scatter across twelve period folders, one deck each — which is `00`'s named validator
  failure, *"create meaningless one-child levels"*, reached by following the family default rather
  than by breaking it. Under this row's order they collect: *Phoenix → status reports → WK14*.
- The charter, the schedule and the closure record have **no meaningful period at all**. They are
  once-per-project documents. A period level above function forces a period onto three of the row's
  four core structures that none of them has.

Both orders honour the parent-context rule — `00`: *"The recommendation should follow the practical
rule that a parent dimension should provide the context required to understand the child."* A status
report for week 14 is meaningless before the project is known, exactly as `00`'s own `Homework 3` is
meaningless before the course. The inversion is about which of *function* and *period* supplies
context to the other, and in a bounded effort the function does.

Neither order is time-first, and this row does not claim the exception: `00` grants the
capture-based-media exception only, and the schema anchor rules that **no sibling in this family may
claim it**. `00`: *"For document and record domains, project, function, or subject usually comes
before time because putting year first scatters related work across calendar folders."* A programme
or portfolio level above the project is the one defensible extra depth and belongs to the user, not
to the catalogue — `00`: *"the user can reverse, remove, add, or flatten dimensions."*

**Verdict on leg 1: passes narrowly, on an inversion of two levels rather than on a different tree.**
Recorded as the second half of `open_question` so R1c confirms it rather than inheriting it. The gist
draft claimed this leg as the row's *sharpest* difference; that claim was made before the default
template existed to compare against, and this pass downgrades it.

### Leg 2 — detection signals of its own

This is where the row is genuinely strong, and it is strong in the specific way the schema anchor
demands: **a structure paired with a labelled slot**, four times, none of them owned by another row
in this family.

1. **The scope-and-out-of-scope pair.** An initiation document that states what is in scope
   *together with an explicit exclusion list*, beside named sponsor and manager slots and a milestone
   list. No standing-cycle document in this family carries an exclusion list, because a standing cycle
   has no boundary to draw. This is the single cleanest structure the row has.
2. **The dependency-bearing schedule.** A table pairing a work-package name with a start, an end or
   duration, a percent-complete, **a predecessor reference**, and an assigned resource. The
   predecessor column is the discriminator: budgets, registers, asset inventories and meeting packs
   all produce tables in this family and none of them expresses ordering between rows.
3. **The stage-gate-and-RAG cadence.** A fixed short form repeating period after period with a health
   indicator, a progress block, a next-period block and a blockers block, carrying a stage-gate name.
   The schema anchor names the *governance-cycle* structure (body + period + agenda/attendance/
   resolution) as the family's own; this is a different structure with a different slot set, and the
   discriminator between them is that a status form has no attendance and no resolution.
4. **The acceptance-paired-with-handover closure.** A deliverables-accepted block sitting beside a
   handover-to-operations or benefits-realisation block, usually with a signature slot. A record that
   exists to *end* something. Nothing in this family that runs forever produces one.

**Verdict on leg 2: passes cleanly.** Note what is deliberately *not* offered: a Gantt shape, the
word "project", `.mpp`, or a milestone list. Each of those is a document shape or a vocabulary word,
each is on the row's `never_alone` list, and each would be exactly the failure
`organisational-records` was refused for.

### Leg 3 — privacy rules of its own

The family carries `potentially_sensitive`. This row carries **`none`**, and differing *downward* is
a real difference, not an absence of one — the schema anchor rests the family's posture on the
observation that *"The exposed party is usually not the user"*, and that observation does not hold
here. A milestone list, a RAG slide and a dependency chart expose nobody. Marking the row
`potentially_sensitive` wholesale would be inflation that weakens the value where it matters.

The material that *is* sensitive here is sensitive for reasons owned elsewhere and is detected **per
file, never per row**: a resource plan names individuals against costs and reaches `hr`'s posture; a
business case carries unannounced commercial figures; a closure report may name a person's
performance and reaches the retrospective row's caution. Where such a member appears, `00`'s per-file
transition governs it — *"A scanned passport, tax statement, medical document, authentication key, or
account record should enter a protected state immediately."* — and the operative limits are `00`'s:
*"Protected material should not be included in cloud-model prompts by default, should not display raw
content in general group summaries, and should not be moved automatically without a user policy that
explicitly permits it."* The row assigns only the catalogue value `none` and no P7 handling class.

`retrospective-postmortem` states this same difference from its side — it carries
`potentially_sensitive` *"which is why this row carries `potentially_sensitive` and `project-delivery`
does not"*. This pass agrees with that reading and adds the corollary it left implicit: the row
default is not a per-file verdict, which is why a `Resource plan FY26 - delivery team.xlsx` fixture
was added in this pass to say so in the JSON rather than only in prose.

**Verdict on leg 3: passes.**

**Overall: the row stands, narrowed.** Legs 2 and 3 pass cleanly; leg 1 passes narrowly and is
flagged. One member — the portfolio roll-up — does **not** clear the test and is retained under
protest; see the open question.

---

## The three charges, answered

The dispatch put three charges to this row. They deserve separate answers, because two of them are
partly right.

### (a) "Project delivery is an activity — a `work_type`, not a filing world"

**Rejected, with the reasoning stated rather than asserted.** The charge would land if the row's
anchor were the *managing*. It is not: the anchor is the bounded effort as a durable custody object,
and the test for that is whether the effort leaves structures behind that outlive the activity. It
does — leg 2's four. A charter is not a record *of* managing; it is the instrument that authorises
the effort and is still meaningful, years later, to someone who never managed anything.

The stronger form of the charge is the reverse: if delivery were a `work_type`, **of what row would
it be a value?** There is no candidate. It cannot be a value of `strategy-plan` (which stops at the
decision to proceed), nor of `contract-administration` (which has no internal effort), nor of
`meeting-record` (which has no schedule). A `work_type` value must be a value *of something*, and
nothing in this family is the something. That absence is affirmative evidence.

### (b) "It is a container so generic that it is a residual wearing a domain's clothes"

**Partly conceded, and the concession is the most useful thing in this pass.**
`organisational-records` was refused because *everything* it had was never-alone — an organisation
name plus a document-type word, which per the schema anchor *"can never clear activation"*. This row
has four structures that are not, so it does not fall the same way. But two of its gist-era members
did behave residually, and both have been dealt with:

- **"Deliverable or work product under review"** was listed as a `work_type` in the gist JSON.
  *Anything* can be a deliverable. That entry made the row a catch-all for any file found near a
  project, which is residual behaviour precisely. **Removed from `work_types` in this pass.** Sparse
  files near a project still join its neighbourhood — `00`: *"The graph does not automatically copy
  those missing facts onto sparse files."* — but they do so as sparse files, not as a named class.
- **The portfolio roll-up.** See the open question; it is the one place the charge lands squarely.

What survives the concession is a row whose activation requires a structure, never a topic. That is
the schema anchor's own bar and this row now clears it explicitly rather than by assumption.

### (c) "It is indistinguishable from `construction_property.construction-project` except by industry"

**Rejected, on that row's own evidence rather than on mine.** Its deepened memo names four leg-1
structures: the letter of acceptance, the **contract-particulars block with a date for possession
paired with a date for completion**, the programme issued under a contract reference and revision,
and the completion-and-handover envelope. This row carries none of the four. Its own structures —
scope-and-out-of-scope, predecessor column, stage-gate cadence, acceptance-and-handover pairing —
are not on that list either.

Industry is indeed a value and not a structure, and neither row rests on it. The two rows meet
exactly where that memo says they meet: it assigns this row *"a plan, a RAG status, a decision log, a
change record, a closure document — the generic shapes"*, assigns itself *"a fit-out or a scheme with
a contract sum, measured works and a valuation cycle"*, and names *"a Gantt chart, which counts for
neither"* as the shared bytes. **This memo adopts that boundary in full, states it reciprocally, and
does not diverge from it.** The `Kilnfield Phase 2 - programme rev D.pdf` fixture added to this row's
JSON names the same bytes from this side, so the reciprocal can be checked rather than asserted, and
its `must_not_conclude` says in terms that a dependency-bearing schedule — this row's strongest
signal — is still never-alone and does not win against a possession-and-completion pair.

---

## The two siblings that define themselves against this row

### `risk-register` — it argued its way out, and it was right

Its memo answers the charge that it is an artefact inside this row, and its answer is: *"What
separates them is not shape at all; it is **lifespan and scope**"* — a RAID log has a project name in
the header, Assumptions/Issues/Dependencies sheets, and a **closure date, because the project does**;
a corporate register has an appetite statement, an inherent-versus-residual pair, and **no end date**.
It adds the containment argument: *"an organisation that runs no projects at all still keeps a
register, because the register exists to outlive whatever created its entries."*

**This row's side, stated reciprocally and without contradiction.** That reasoning is accepted in
full. This row must not take the standing register, its appetite statement or its inherent/residual
pair, **even when a project's RAID log was seeded from it**; that row must not take the bounded log
that closes when the project closes. Both files name `RAID log.xlsx` as the shared fixture and both
name it identically. This row's `RAID log.xlsx` example already declines to choose between the two,
on the correct ground that P10 chooses from an accepted group later; that is preserved unchanged.

The containment argument also cuts the way this row needs: a register outliving its project proves
the register is not inside the project, and equally proves the project is not merely a scope tag on a
register. Two independent objects, one shared table shape.

### `retrospective-postmortem` — it argued at gist depth, and it still holds

Its three grounds: a large share of its material (an outage, a near-miss, a failed launch) has **no
project at all** and would be homeless here; its detection shape is “a timeline of timestamped
past-tense events plus a causal section, sitting *above* the actions table.”, which nothing here has;
and its privacy posture differs.

**Does it still hold, from this side? Yes — and the first ground is the load-bearing one, more so
than that memo realised.** Ground two on its own is thin: "a section above the actions table" is a
difference of layout, and this row would not have wanted a layout argument used against it either.
Ground three is real but is a consequence rather than a cause. Ground one, however, is decisive and
is decisive *for structural reasons this row can state*: this row's anchor is a bounded effort, and an
incident is not one. It has no charter, no scope-and-out-of-scope pair, no schedule and no acceptance
— it has an occurrence. That memo puts it exactly right: folding it here *"would file an outage under
a project that does not exist."* Filing a real record under an anchor that is absent is the failure
this whole pass exists to prevent, so this row **actively does not want** the incident half.

The tense discriminator both rows can use: forward-looking control artifacts — plan, schedule, RAID,
status — are this row's; a backward-looking causal account is that row's. Where a single file carries
both, that row's `Phoenix closure report.docx` is the named fixture and it calls the overlap *"not a
defect"*. **That fixture is now named from this side too**, agreeing rather than competing: the
closure envelope is this row's, the causal account is that row's, and P10 chooses.

One addition made in consequence: that row's first `never_alone` is "an actions-with-owners table
alone". **The same entry has been added to this row's `never_alone` list**, so the most common table
in the family belongs to neither row on its own from both directions.

---

## Files considered and rejected

A row that only lists what it holds has not been researched. The tempting false positives:

| File | Why it is **not** this row's evidence |
|---|---|
| `Kitchen renovation plan.xlsx` (**kept as the primary collision fixture**) | The schedule shape in full — task, start, finish, duration, dependency, cost, a milestone row, a contingency line — and **no organisational anchor at all**: no sponsor, no stage gate, no organisation. It proves the schedule structure is necessary and not sufficient. Belongs to household property records. |
| `Kilnfield Phase 2 - programme rev D.pdf` (**added this pass; the file that must not be lost TO this row**) | A construction programme, more schedule-shaped than anything this row holds. Discriminator, taken from that row's own memo: a contract-particulars block with **a date for possession paired with a date for completion**, under a contract reference and a revision. `construction_property.construction-project`. |
| A **test plan or QA sign-off** | Real and common; its anchor is the thing being tested, not the effort. Earns a `work_type` value at most, and was left as one. |
| A **Jira or backlog export** | Rejected as an example because it is indistinguishable from the support-queue and software-repository exports. Survives as the `code.software-project` collision signal only. |
| A **business case** | Names the same effort, the same benefits, the same milestones. Discriminator: an options-and-recommendation structure with an appraisal horizon is `strategy-plan`; the scope-and-out-of-scope pair and the status cadence are this row's. A business case sits on the *far* side of the decision to proceed; this row starts on the near side. |
| A **project budget tracker** | Tempting, and deliberately not taken. A budget-versus-actual column pair is the schema anchor's own *management-financial table* — the family's default evidence, not this row's. Its collision runs through `budget-forecast`, a sibling's row, and tripling it would put one concept in three places. **Added to `never_alone` this pass** so the tracker cannot fire this row on its columns. |
| An **architecture decision record** | Past-tense rationale in a decision-log shape. `retrospective-postmortem` considered and rejected it too, routing it to `code.software-project`; this memo agrees and does not open a competing claim. |
| A **research project's progress report** | Identical vocabulary — project, workpackages, deliverables, milestones. Discriminator: a protocol, a method, a funder or ethics reference. `research.project-workspace`. |
| A **student group-project plan** | The same shape with no organisation. Not made a second fixture: the kitchen-renovation file already carries the no-organisation lesson and a second one would be padding. Said plainly rather than inflated. |

## The collision fixtures, in both directions

- **Would wrongly fire this row:** `Kitchen renovation plan.xlsx` — full schedule structure including
  a dependency column, zero organisational anchor. The lesson: this row's strongest signal is still
  never-alone.
- **Must not be lost to this row:** `Kilnfield Phase 2 - programme rev D.pdf` — a construction
  programme, discriminated by the possession-and-completion pair that this row never carries. The
  same bytes are named on both sides.
- **Shared with a sibling, and correctly shared:** `RAID log.xlsx`, named identically by this row and
  `risk-register`; `Phoenix closure report.docx`, named identically by this row and
  `retrospective-postmortem`. Neither is a defect and neither row is asked to give it up.

## Reciprocal boundaries, both directions

Every neighbour's own file was read before its boundary was written; where the neighbour does not
name this row, that is stated rather than assumed.

| Neighbour | This row must not take | The neighbour must not take | Shared fixture bytes |
|---|---|---|---|
| **`business_operations.risk-register`** (deepened, **names this row**) | the standing register, its appetite statement, its inherent/residual pair — even where a project seeded it | the bounded log with a project name in the header, Assumptions/Issues/Dependencies sheets and a closure date | `RAID log.xlsx`, named identically from both sides |
| **`business_operations.retrospective-postmortem`** (gist, **names this row**) | the backward-looking causal account with a timeline above the actions table; and every incident-anchored review, which has no bounded effort at all | the forward-looking control artifacts — charter, schedule, RAID, status, acceptance | `Phoenix closure report.docx`, now named from both sides |
| **`construction_property.construction-project`** (deepened, **names this row**) | the contract-particulars block, the possession-and-completion pair, valuations, measured works, the handover envelope pinned to a site | the generic shapes — plan, RAG status, decision log, change record, closure document | a Gantt chart, *"which counts for neither"*; and `Kilnfield Phase 2 - programme rev D.pdf`, added here |
| **`business_operations.contract-administration`** (gist) | the post-signature obligation register — renewal dates, notice periods, counterparties — which the schema anchor names as a family-own structure | the internal delivery record merely because a contract funded it | `Acceptance certificate - signed.pdf`. **Edge added this pass**; the fixture already named this neighbour and no `collides_with` entry existed. **One-way; R1c owes the reciprocal** |
| **`business_operations.board-governance`** (gist) | the meeting apparatus — notice, numbered agenda, attendance, resolution block, pack pagination | the status deck or change request merely because it was tabled | a project board pack: covering minute there, status annex here. **Edge added this pass. One-way; R1c owes the reciprocal** |
| **`hr.org-design-headcount`** (roster) | establishment posts, headcount budgets, grades, an organisation chart with no bounded effort | allocation stated against work packages on a project's schedule, ending when the project ends | `Resource plan FY26 - delivery team.xlsx`, added this pass. **Edge authored one-way, reversing the gist pass's decision to leave it unedged. R1c owes the reciprocal** |
| **`business_operations.strategy-plan`** (gist) | the options-and-recommendation structure and its appraisal horizon | the scope-and-out-of-scope pair, the dependency-bearing schedule, the status cadence | a business case, which sits on the far side of the decision to proceed |
| **`business_operations.meeting-record`** (gist) | agenda, attendance and minutes structure | a plan, log or status artifact merely because it was circulated to a meeting | steering-group papers |
| **`research.project-workspace`** (roster) | a protocol, a method, a funder or ethics reference, a manuscript-facing artifact | a sponsor, a stage gate, a RAG status, a benefits-realisation frame | a progress report against milestones |
| **`career.consulting-client-engagement`** (roster) | a statement of work, a rate or fee schedule, a client counterparty | an internal sponsor, internal governance, no counterparty | the same delivery pack held by two parties. `00` supplies the role split: *"A consulting document may mention the author’s firm and the client organization."* |
| **`code.software-project`** (roster) | residence in a repository with source, configuration and commit-shaped history | a governance-facing artifact with a sponsor, a stage gate and a status cadence | a backlog export; an ADR |

## Neighbours considered that did **not** get an edge

- **`finance.small-business-bookkeeping`** — a project budget tracker touches it, but the collision
  runs through `business_operations.budget-forecast`, which is a sibling's row. Not tripled.
  Preserved from the gist pass; still the right call.
- **`business_operations.compliance-audit`** — a stage-gate assurance review looks like an audit.
  Left unedged: `risk-register` already carries that boundary for the family, and its statement of it
  (a finding keyed to an *identified assessment*, with a severity and a corrective action) discharges
  the confusion without a third claimant.
- **`academic`** — a student group project is the same shape with no organisation. The kitchen fixture
  already carries the no-organisation lesson.

## `proposed_fields`

**None**, and this is a deliberate second rather than an abstention.

The natural anchor for this row is `project`, which is **already a canonical key** (shared with the
research and code schemas), so there is nothing to mint — the row would reuse it if D1's deferral
were lifted. `fiscal_period`, which this row's period level would want, is **already proposed by the
schema row** and is adjudicated at R1c; the addendum's instruction to second the family's existing
proposals rather than mint variants applies exactly here, and duplicating the proposal would put one
concept in two places, which is the 574 failure in miniature. `organization`, the schema row's other
mint, is seconded on the same terms.

One candidate was considered and **not** proposed: a key for the *reporting period of a status
series*, distinct from `fiscal_period` because a project week is not a fiscal one. It is a real
concept and it is precisely the thing this row must not mint alone — `budget-forecast` and
`board-governance` would want it too, and a `reporting_period` alongside `fiscal_period` alongside
`tax_year` is the two-spellings-one-concept bug D6 exists to prevent. Recorded here for R1c rather
than minted.

## NEEDS-JOSEPH

- **NJ-BO-PD-1 · The portfolio fold — escalated, not carried forward.** The gist pass recorded this
  as an open question about *where* a roll-up sits. This pass states it more sharply: a portfolio
  dashboard naming twenty projects is held together by an organisational unit plus a document-type
  word, and **that is the exact shape the schema anchor rules constitutionally never-alone and for
  which `organisational-records` was refused.** It is the one member of this row that cannot clear
  activation on its own evidence. Alternatives and their costs: **(i)** place the roll-up at the
  branch root above the project level — costs a level that a user with one project would never want;
  **(ii)** give it its own row — costs a row that fires rarely and re-opens whether it, too, is a
  residual; **(iii)** accept that it can only ever fire as a low-confidence member of an
  already-accepted project group — costs nothing structurally but means the legacy id
  `ops.programme-portfolio` is not really covered, only nominally. This pass declines to choose
  silently. The portfolio structure is retained in `recognition` and `work_types` **under protest**
  and R1c must decide.
- **NJ-BO-PD-2 · Resource plans and `hr`.** A staffing or capacity plan names individuals against
  costs and utilisation: a delivery artifact by purpose, a workforce record by content. The gist pass
  left this unedged; **this pass reverses that and authors the edge one-way**, with a fixture, on the
  ground that leaving a real privacy bleed unrecorded is worse than recording it in one direction.
  R1c should confirm the discriminator (allocation against work packages, ending with the project vs
  establishment posts and grades) and write the reciprocal on `hr.org-design-headcount`.
- **NJ-BO-PD-3 · The dimension inversion.** This row recommends function above period; the family
  default puts period above function. The argument is in leg 1 and rests on status series collapsing
  into one-child period folders under the default. R1c should confirm or overrule it explicitly —
  siblings should not inherit an inversion by copying this row.
- Inherits the schema row's **NJ-J-IND-3** (where an organisation's money lives) by reference. Not
  restated as an edge here: this row's money is a management view rather than an account, and the
  `Portfolio dashboard Q2.xlsx` fixture already says so in its `must_not_conclude`.

---

## What changed in this pass

Checked line by line against the JSON as written, not against intention.

**Preserved unchanged** (the gist draft was right and was not rewritten for its own sake): the whole
`recognition.deterministic` block and its seven structures; all six `needs_llm` entries; the seven
original `never_alone` entries; the 27 `proposed_context_terms`; all five `grouping_reasons`; the
`template.why` prose in full; `file_kinds`; the ten original `file_examples` including the
`Kitchen renovation plan.xlsx` collision fixture and the `RAID log.xlsx` refusal-to-choose; all eight
original `collides_with` entries; the `also_holds_with` edge to `career`; all four `falls_through_to`
routings; `sensitivity: none`; `refuse_node: false`; `fields: []` and `proposed_fields: []`.

**Added to the JSON:**

- Three `collides_with` entries: `business_operations.contract-administration`,
  `business_operations.board-governance`, `hr.org-design-headcount` — bringing the total to eleven.
- Three `never_alone` entries: an actions-with-owners table (reciprocal to
  `retrospective-postmortem`), a milestone or deliverable vocabulary word (applying the schema
  anchor's never-alone principle by name), a budget-versus-actual column pair (which is the family
  default's evidence, not this row's) — bringing the total to ten.
- Three `file_examples`: `Kilnfield Phase 2 - programme rev D.pdf` (the must-not-be-lost-to-this-row
  fixture, naming construction's bytes from this side), `Phoenix closure report.docx` (naming
  `retrospective-postmortem`'s both-anchors fixture from this side), `Resource plan FY26 - delivery
  team.xlsx` (the `hr` bleed, and the statement that a row sensitivity value is not a per-file
  verdict) — bringing the total to thirteen.
- A clause in `sensitivity_why` stating that `none` is a row default and never a per-file verdict.
- `one_line` rewritten to name the four structures that activate the row, to say explicitly that it
  is not the activity of managing, and to drop the retired "gist-level" label.

**Removed from the JSON:**

- The `work_type` **"deliverable or work product under review"**, as conceded under charge (b): it
  made the row a catch-all for any file near a project, which is residual behaviour. Nine
  `work_types` remain.

**Reversed:**

- **The portfolio fold is no longer treated as settled.** The gist `open_question` asked where a
  roll-up sits; the rewritten `open_question` says the roll-up fails this row's own node test on the
  schema anchor's never-alone principle, retains it under protest, and puts three costed alternatives
  to R1c.
- **The `hr.org-design-headcount` boundary is now authored** rather than deferred. The gist memo
  explicitly declined to edge it; this pass judges that leaving a privacy bleed unrecorded is the
  worse error.
- **The leg-1 claim is downgraded.** The gist memo called the dimension order this row's sharpest
  difference. Measured against the now-stated family default, it is an inversion of two levels — a
  narrow win, argued and flagged rather than claimed.

**Not reversed, and the gist verdict stands:** `refuse_node` remains `false`. The full node test was
run against a real default template and the row clears it on leg 2 outright, leg 3 by a genuine
downward difference, and leg 1 narrowly. The row is narrowed, not refused.
