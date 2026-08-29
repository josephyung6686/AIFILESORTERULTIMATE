# `business_operations.retrospective-postmortem` — lab notes (template row, deepened to J-DEPTH)

**Depth: J-DEPTH.** Deepened from the gist draft under `DEEPEN-ADDENDUM.md`. The gist draft's facts and
its three grounds were sound and are preserved; what it lacked was the test argued leg by leg against a
default template that did not exist when it was written, a proper answer to three further charges, a
collision fixture in the must-not-be-lost direction, and reciprocal boundaries with neighbours that have
since landed. One decision is **reversed** and said so plainly below.

---

## Sources actually used

**Binding.** `planning/00-database-agent-product-design.md` (every quotation below machine-checked with
`grep -F`, count 1 in that file); `planning/01-product-design-structured.md`; `planning/prompts/ALIGNMENT.md`;
`planning/domains/CONNECTION.md` and `CONNECTION-EXAMPLES.md`; `planning/domains/_CONTRACT.md`;
`planning/domains/canonical_fields.json`; `planning/domains/roster.json` (every edge id verified present);
`src/evidence_shape/vocabulary.py` for `SOURCE_TYPES`; `planning/overnight/council/DECISION-BRIEF.md`
(D1–D6 and J-IND ratified, not re-debated); `ROSTER.md` §4 + Appendix A lines 679 and 815 for the absorbed
legacy ids `ops.retrospective-postmortem` (ROW) and `soft.incident-postmortem` (FOLD).

**Neighbours read before writing, and not touched.**

- `business_operations.research.md` — the schema anchor. Its **default template paragraph** and its
  **never-alone principle for all 24 siblings** are the bar this row is now measured against. It did not
  exist when the gist draft was written; measuring against it is the largest single change in this pass.
- `business_operations.organisational-records.json` — the family's refusal, read **first and on the
  assumption this row might be heading the same way**. Its four-part closure of the two-role escape route
  is the most rigorous refusal in the corpus and it is what §"The residual charge" below is tested against.
- `business_operations.project-delivery.research.md` (35KB, deepened) — the original charge's other half.
  It re-examined this row from its side and **kept it**, while correcting one of its three grounds.
- `business_operations.meeting-record.research.md` (40KB, deepened) — it names this row, quotes the gist
  draft's decision to decline the edge, and states the boundary. Its answer is accepted here and
  reciprocated; the edge is now written from this side.
- `business_operations.risk-register.research.md` (45KB, deepened) — the tense seam.
- `clinical_practice.case-conference.json` — read for the morbidity-and-mortality edge, posture respected.

---

## What this row holds, and what actually makes it one situation

Something has already happened — a project finished, a launch failed, a service went down, a near miss was
caught — and the organisation writes down what occurred, why, and what it will change. The row holds
retrospectives and lessons-learned write-ups, incident and outage post-mortems, timeline reconstructions,
root-cause and contributing-factor analyses, remediation trackers, accumulated lessons registers, retro-board
captures, debrief recordings, and the metrics and log exports attached as evidence.

The reason an engineering incident review and a sprint retrospective are **one** row rather than two is not
that they share vocabulary — they do not; one says *severity* and *mitigation*, the other says *went well*
and *try next*. It is that both are anchored on an occurrence in the past and both terminate in a committed
change. That is the FOLD `ROSTER.md` Appendix A records, and this pass agrees with it.

---

## The node test, argued leg by leg

CONNECTION §2 for a template row: it exists only where its **detection signals**, **recommended dimensions**,
or **privacy rules** differ from its schema's default template. One leg suffices. All three are argued
because four independent charges were put to this row, and a one-leg pass would not honestly answer them.

### The schema's default template, quoted, so the comparison is real

The anchor states the paragraph every sibling must differ from:

> the **organisational unit or entity** *only where the corpus genuinely spans more than one* → the
> **governance body, project, contract, or account** the material belongs to → the **fiscal period** → the
> **document function**. Not time-first.

and the family bar for signals:

> **No sibling may rest its activation on an entity name, a business vocabulary word, or a document shape
> alone.** Each of the three is never-alone here. Every detection signal a sibling writes must pair a
> **structure** with a **labelled slot**.

### Leg 1 — detection signals of its own

This is the leg the row actually wins on, and the gist draft's version of it was **too weak**. It offered
*"a timeline of timestamped past-tense events plus a causal section, sitting *above* the actions table."* — and
`project-delivery`, reviewing that from its side, called it correctly: *"Ground two on its own is thin: "a
section above the actions table" is a difference of layout, and this row would not have wanted a layout
argument used against it either."* That criticism is accepted without qualification. A layout argument is
not a structure-plus-labelled-slot pair, and the anchor's bar is the latter.

Re-argued at the anchor's bar, taking the JSON's `deterministic` list one at a time:

1. **The incident header.** An incident or reference identifier, a **severity or priority label**, a
   **detection time**, a **resolution time**, and an impact statement naming affected users, customers or
   services, co-occurring in one header block. This is a labelled slot set in the strict sense — `00`
   licenses reading such slots: *"Tables matter because resumes, forms, applications, invoices, and
   administrative documents often place their most useful information in cells rather than body
   paragraphs."* — and the discriminator inside it is the **detection/resolution time pair**. No plan,
   budget, register, minute, asset inventory or status form in this family carries one, because none of them
   describes something that started without permission and stopped. **This is now the row's first
   deterministic signal**, promoted in this pass from sixth. It is the cleanest answer the row has to the
   charge that it is only a document type.
2. **The causal block in a fixed position.** Labelled blocks reading *root cause*, *contributing factors*,
   *why this was not caught*, or a repeated why-chain, sitting between a summary and an
   **owned-and-dated remediation row**. Two labelled slots with a fixed relation between them. Alone the
   remediation row is worthless as evidence — every plan, minute, audit and register in this family ends
   with one — which is why *"an actions-with-owners table alone"* is the row's first `never_alone`, and
   that entry is preserved verbatim from the gist draft because it was right.
3. **The facilitation triad.** *Went well / did not go well / do differently*, as three headings, three
   table columns, or three groups of short entries. A structure of three co-labelled groups. It is the only
   signal that fires on a retro with no incident anywhere, and it is what carries `Retro - sprint 41.docx`.
4. **The lessons-learned register.** One row per lesson with a category, a recommendation and a project or
   period of origin, **accumulated across efforts**. The cross-file regularity is the signal, not any one
   document's shape — the same *kind* of argument `meeting-record` won its leg 1 on, and it is offered here
   knowing it competes with `risk-register` (see the seam below).

**Verdict on leg 1: passes, and passes more cleanly than the gist draft argued it.** What is deliberately
not offered: the words *retro*, *review*, *post-mortem*, *lessons* or *RCA*; a past-tense voice; a timeline
on its own; `.md` in a repository. Each is a vocabulary word or a document shape, each is on the row's
`never_alone` list, and each would be precisely the failure `organisational-records` was refused for.

### Leg 2 — recommended dimensions

`dimension_order` is **empty by binding contract** — the schema declares no fields, so nothing can branch.
The honest position is therefore that **this leg is not available to this row**, and it is not claimed.

Held as prose for the pass that may license fields: the effort or the incident under review, then the
document function, with the review date last, on `00`'s parent-context rule. **The row is this family's
strongest candidate for a time-first exception and still must not take it.** An incident series genuinely
reads chronologically — that is a real pull, not a hypothetical — but `00` grants the exception to
capture-based media, and the anchor rules that no sibling in this family may claim it. `00`: *"For document
and record domains, project, function, or subject usually comes before time because putting year first
scatters related work across calendar folders."* A review-date-first tree would separate a post-mortem from
the project it closes and from the recurrence it later matches. And in any case, *"the user can reverse,
remove, add, or flatten dimensions."*

**Verdict on leg 2: not claimed.** This differs from the gist draft only in saying so plainly.

### Leg 3 — privacy rules of its own

The row carries `potentially_sensitive` where its closest sibling `project-delivery` carries `none`, and
that difference survives inspection from both sides: that row states it too, and adds the corollary this row
had left implicit — the row default is not a per-file verdict.

The grounds are specific rather than defensive. A retrospective is **by construction** a candid written
account of what went wrong, naming people who were involved and, in a blameless culture, deliberately
recording statements made on the understanding they would not travel. An incident post-mortem additionally
states how a live system failed and what was not caught. And the failure mode is asymmetric: a review that
turns out to concern an individual's conduct is employment material, for which `00`'s transition is
immediate and the limits are `00`'s — *"Protected material should not be included in cloud-model prompts by
default, should not display raw content in general group summaries, and should not be moved automatically
without a user policy that explicitly permits it."*

A ground the gist draft did not state: **the branch name is itself a disclosure.** A folder named after a
failure discloses the failure to anyone who can see the tree, before any file is opened. `00` anticipates
this — *"Protected branches should have configurable redaction in the canvas and review screens"* — and it
is NJ-BO-RP-3 below.

**Verdict on leg 3: passes.**

**Overall: the row stands. Legs 1 and 3 pass; leg 2 is unavailable and is not claimed.** That is a
different grade from the gist draft's "passes on three independent grounds", and a more honest one: one of
those three grounds was a layout argument, and one was a consequence rather than a cause.

---

## The four charges, answered separately

The dispatch put four independent ways to fail. Each is answered on its own, because a row that answers
three and waves at the fourth has not been tested.

### (a) A `work_type` value of `business_operations.project-delivery`

**Answered, and this is the strongest of the four answers.** A large share of this row's material has no
project at all: an outage, a near miss, a failed launch. Under a project-first row those files would be
homeless — filed under an anchor that is absent, which is the failure the whole pass exists to prevent.

The gist draft argued this and `project-delivery`, deepened since, tested it from its side and agreed —
*"Ground one, however, is decisive and is decisive *for structural reasons this row can state*"* — because
its own anchor is a bounded effort with a charter, a scope-and-out-of-scope pair, a schedule and an
acceptance, and an incident has none of those. It has an occurrence. That row states outright that it
**actively does not want** the incident half.

Note what this answer does **not** rest on: that retrospectives are *about* projects (they often are, and
that would make them a work type), or that the vocabulary differs (it does, and vocabulary is never-alone).
It rests on a class of files with no candidate anchor on the other side.

### (b) A meeting output, already covered by `business_operations.meeting-record`

**Answered in both directions, and this is where a gist decision is reversed.**

That row states the boundary in its own reciprocal table: this row must not take *"the forward-looking
working meeting whose actions table it shares"*, and it must not take *"a look-back structure: went-well/went-badly columns, an incident timeline, a contributory-factors or causal section above the actions"*. It
names `Retro - sprint 41.docx` as the shared fixture bytes. That is exactly right and this pass does not
diverge from a word of it.

**Two things make the charge fail.** First, the discriminator above the actions table is real evidence, not
a taxonomic preference: the facilitation triad and the causal block are structures with labelled slots,
whereas the meeting apparatus this row would otherwise share (attendee line, date line, actions section) is
now written into this row's `never_alone` list so it can never activate this row alone. Second — and this is
the half that answers the charge rather than merely dividing the overlap — **a large part of this row's
material is not a meeting output at all.** An outage post-mortem reconstructed from logs and dashboards by
one engineer, a lessons-learned register accumulated across years and efforts, a remediation tracker, and a
metrics export attached as evidence: none has a meeting behind it. A row that were merely `meeting-record`'s
output format would have no such members. This row's asymmetry with `meeting-record` therefore mirrors its
asymmetry with `project-delivery`: in both cases the load-bearing material is the material the neighbour has
no anchor for.

**REVERSAL.** The gist draft declined this edge: *"Left unedged deliberately: the confusion is already
carried by the meeting row's own scope, and the distinguishing content (a causal section) is stated here."*
That reasoning is wrong on the contract. CONNECTION requires a `collides_with` edge wherever the same
evidence would confuse two rows, and a retro write-up plainly does; whether a neighbour has *also* stated it
is not the test. The edge is written in this pass, one-way from this side, in that row's own wording, with
the same fixture bytes named on both sides. `meeting-record` treated the gist decision generously —
*"the asymmetry there is a considered choice by that author, not a defect, and I have not overridden it"* —
and that generosity is declined: it was a defect, and it is fixed here rather than left for R1c.

### (c) A document type — a findings doc

**Answered on the family's own bar, and the charge is half right.** It is right that
*summary → analysis → recommendations* is a document shape, and that the shape is shared with an audit
report, a consultancy deliverable, a due-diligence memo, a research write-up and a school project. The
anchor names a document shape as one of the three constitutionally never-alone things in this family, and
this pass **adds that explicitly to `never_alone`** — the charge earned that entry.

Where the charge fails is that the row does not rest on the shape. It rests on slot sets inside it: the
detection/resolution time pair, and the causal block's fixed relation to an owned-and-dated remediation row.
A findings doc has findings; it does not have a time at which something was detected and a time at which it
stopped. Compare the refused sibling directly: `organisational-records`' only candidate signal was *an
organisation name plus a document-type word* — **both halves never-alone**, so the row could never clear
CONNECTION §4 step 2. This row's signals pair a structure with a labelled slot, four times. That is the
difference between a row that never fires and a row that fires on named bytes.

### (d) The content splits entirely between `project-delivery` and `risk-register`, leaving nothing

**Answered, and this is the weakest-answered of the four. R1c should test this one hardest.** Stated at full
strength: *what happened* is the delivery record's; *what we will do about it* is the register's; subtract
both and a retrospective is a stapler.

It fails on the facts of the two neighbours, both now deepened and both consulted:

- `project-delivery` **declines the incident half on structural grounds** (above), so the subtraction does
  not run. It also declines the causal account itself: its reciprocal table cedes *"the backward-looking
  causal account with a timeline above the actions table; and every incident-anchored review, which has no
  bounded effort at all"*.
- `risk-register` holds **possibilities, not realised events**, and states the discriminator from its side:
  *"an entry describing something that already happened supports `retrospective-postmortem`; something that
  might happen, with a treatment, supports this row."* A remediation commitment attached to an occurrence is
  not a risk entry; it becomes one only if the register chooses to open a row for the recurrence.

**But the honest weakness is this**: the residue is defined partly by what two neighbours refuse, and a row
whose definition leans on refusals sits uncomfortably close to the `organisational-records` failure, which
was refused precisely because it *"is defined by subtraction"*. What keeps this row on the right side of
that line is that the residue has a **positive** structure of its own — the incident header, the timeline,
the causal block, the facilitation triad — rather than being *carries an organisation and a document type
but no more specific operational sub-domain*. A negative definition cannot own a positive structure; this
row can name the bytes that fire it. That is the whole of the difference, and it is stated in
`open_question` so R1c inherits the doubt rather than the verdict.

---

## The residual charge, tested against the refusal

`00` on residuals: *"Residual templates provide safe, intentionally broad destinations for files that have
no reliable deeper association."* The `meeting-record` memo shows how the test is run, and it is run here.

| | `organisational-records` (refused) | this row (kept) |
|---|---|---|
| Candidate signal | an organisation name + a document-type word | a detection/resolution time pair in a labelled header; a causal block in fixed relation to an owned remediation row |
| Never-alone status | **both halves never-alone** → can never clear activation | neither half is an entity name, a vocabulary word, or a document shape |
| Dimensions | identical to the schema default | not available (no fields); not claimed |
| Privacy | identical to the schema default | differs, on three grounds, one of them the branch name itself |
| Residual test | *is* the definition of no reliable deeper association | positive association to a named occurrence |

The refused row could never fire. This one can, and the JSON names the bytes.

---

## Files considered and rejected

Fixtures kept in the JSON are marked.

| File | Why it is / is not this row's evidence |
|---|---|
| `Grievance investigation report - redacted.pdf` (**fixture**) | The must-not-be-lost direction. Identical timeline–cause–actions shape in full. Discriminator: the subject is a **person**, with a terms-of-reference block, an investigating officer and a right-of-response section. `hr.employee-relations`'; falls through to **Protected Records**, not to this row's Independent Records. |
| `Phoenix closure report.docx` (**fixture**) | Both anchors genuinely present in one file — a project artifact whose last third is a retrospective. Not a defect; P10 chooses from an accepted group. Named from both sides, and `project-delivery` agrees it is not a defect. |
| `Retro - sprint 41.docx` (**fixture, added this pass**) | The `meeting-record` seam, named with the same bytes on both sides. Meeting apparatus in full; the facilitation triad above the actions table is what discriminates. |
| `DR test report - March.docx` (**fixture, added this pass**) | The `risk-register` seam. Timeline, findings and a remediation table — and yet **the event was deliberate and scheduled**, with success criteria agreed in advance. That row names the same bytes and the same discriminator. |
| `incident_metrics_20260430.csv` (**fixture**) | Sparse member. Joins the review packet without inheriting its anchor — *"The graph does not automatically copy those missing facts onto sparse files."* |
| An **architecture decision record** | Past-tense rationale in a decision-log shape. The situation is design, not review. Routed to `code.software-project` as a collision signal only; `project-delivery` considered it independently, reached the same answer, and declined to open a competing claim. |
| A **regulatory incident notification** | Real, and a post-mortem in prose. Its anchor is the **authority it is sent to**, which is a side, not an occurrence. `corporate-regulatory-filings` / `compliance-audit`; collision signal only. |
| A **downloaded post-mortem template** or a published incident write-up from another company's engineering blog | The seductive one, and this row's version of the family's primary collision fixture. Every deterministic signal fires — incident header, timeline, causal block, actions — because the artifact was *written to demonstrate the shape*. Discriminator is `00`'s alone: *"Topic answers what a file is about, while purpose answers what the file was for."* Not given a fixture because the discriminator is the schema's, not this row's; named here so R1c can see it was considered. **A folder of published post-mortems is a reading collection, not a review series.** |
| A **status report** with a "what went wrong last week" paragraph | Past-tense causal prose inside a forward-looking control artifact, on a fixed cadence. `project-delivery`'s stage-gate-and-RAG structure owns it; a paragraph is not a causal block in a fixed relation to a remediation row. |
| A **personal journal** entry reflecting on a bad week | Timeline, causes, resolutions. The anchor triple fails at its first term — no organisational unit — so this family does not activate at all. Personal administration, or **Independent Records**. |
| An **academic reflective essay** | Shares the voice and the structure exactly. Rejected as a fixture at gist depth for thinness; that judgment is upheld, but the reason is now stated: the discriminator is purpose, which is the schema's test, and the essay's anchor is a course. It remains in `needs_llm`. |
| A **complaint response letter** to a customer | Contains a timeline, a cause and a commitment. Its anchor is a counterparty relationship; `customer-account-management` or `support-operations`. No edge minted beyond the existing support-operations one. |

---

## The collision fixture, in both directions

**Would wrongly fire this row: `Grievance investigation report - redacted.pdf`.** Every deterministic signal
except the incident header is present, and the causal block is present in textbook form. What does **not**
discriminate: the timeline, the findings section, the recommendations table with owners, the confidentiality
footer, or the word *investigation*. The single discriminator is **what is under review — an effort, a
system or an event, versus a named individual as the subject**. This is the row's most expensive possible
error, because the consequence is not untidiness: it files a disciplinary record in a working branch that
was never protected.

**Must not be lost to this row: the same file, and the direction matters more.** The asymmetry that
`meeting-record` accepted from `case-conference` applies here identically, in the words that memo used when
it accepted it — *"a wrong answer here **loses protection**, not just tidiness."* This row's residuals are Independent Records and Review Later; `hr.employee-relations`' is **Protected
Records**. A tie must therefore break toward the neighbour, because a wrong answer here **loses protection**
rather than tidiness. CONNECTION §4 step 5's protective ordering doing what it is for.

**A third, inside one file: `Postmortem INC-4417 checkout outage.md`.** Named engineers appear throughout.
They are actors in a chronology — and in a blameless post-mortem that is the entire point. Reading them as
subjects turns the row's own flagship fixture into an employee-relations file. Nothing in the document's
structure marks the difference; only the relation between the person and the occurrence does. This is
NJ-BO-RP-2 and it is why the discriminator is stated reciprocally rather than assumed.

---

## Reciprocal boundaries, both directions

| Neighbour | This row must **not** take | The neighbour must **not** take | Shared fixture bytes |
|---|---|---|---|
| **`business_operations.project-delivery`** (deepened; **two-way, both sides agree**) | the forward-looking control artifacts — charter, scope-and-out-of-scope pair, dependency-bearing schedule, RAID, stage-gate status, acceptance and handover | *"the backward-looking causal account with a timeline above the actions table; and every incident-anchored review, which has no bounded effort at all"* | `Phoenix closure report.docx`, named from both sides |
| **`business_operations.meeting-record`** (deepened; **one-way from their side, now written from this side too**) | *"the *forward-looking* working meeting whose actions table it shares"* — the four-part meeting apparatus alone | *"a look-back structure: went-well/went-badly columns, an incident timeline, a contributory-factors or causal section above the actions"* | `Retro - sprint 41.docx`, now named identically on both sides |
| **`business_operations.risk-register`** (deepened; **two-way**) | an entry about something that **might** happen, with a likelihood, an impact and a treatment | *"an entry about something that already happened, with a causal analysis and a recommendation"* | `Lessons learned register.xlsx`; `DR test report - March.docx`, where the discriminator is that the event was **deliberate and scheduled** |
| **`hr.employee-relations`** (schema not landed; **one-way, knowingly**) | a named individual as the **subject** — terms of reference, investigating officer, allegation, right of response | an occurrence-anchored review, merely because named people appear as actors in its timeline | `Grievance investigation report - redacted.pdf`; and `Postmortem INC-4417 checkout outage.md` from the other side |
| **`business_operations.compliance-audit`** (one-way from here) | an external standard, a control reference, an auditor, a finding-severity scheme | an internally chosen, internally owned review with no control framework behind it | an audit finding with a corrective-action plan |
| **`hr.workplace-health-safety`** (schema not landed; one-way) | a physical-harm frame, a statutory reporting reference, an injured party | a service, delivery or commercial outcome with no person harmed | an accident / near-miss investigation |
| **`code.software-project`** (one-way from here) | residence in a repository beside source and configuration, in a decision-record framing | an incident header with severity, detection and impact, merely because it is markdown in a repo | an engineering post-mortem committed to `docs/` |
| **`clinical_practice.case-conference`** (landed, deepened; one-way from here, protective) | named patients, a clinical service, a care episode — **and the tie breaks their way**, because their residual is protective and this row's is not | an organisational service, product or delivery outcome with no patient anywhere | an M&M / significant-event review, whose vocabulary of contributing factors and learning points is shared verbatim |
| **`business_operations.support-operations`** (one-way from here) | the live queue — tickets, SLAs, an open case's working record | the **major-incident review** that comes out of that queue after the fact | a major-incident review referencing its originating tickets |

**Reciprocity status, verified by `grep` across `planning/domains/nodes/` in this pass.**
`project-delivery` and `risk-register` name this row and are named back, with matched wording and shared
fixture bytes. `meeting-record` names this row and quoted the gist draft's refusal of the edge; that refusal
is reversed here and the edge now exists on both sides, in their words. `clinical_practice.case-conference`
is named one-way from here and its protective posture is respected rather than overridden. `hr.*` has not
landed — no files exist for either row — so those two edges are authored one-way knowingly and R1c owes the
reciprocals; NJ-BO-RP-2 says so.

---

## Neighbours considered that did **not** get an edge

- **`business_operations.board-governance`** — a board reviewing a failure produces minutes with a causal
  discussion. No edge: the constitutional apparatus (notice, quorum, numbered papers, resolutions) is
  decisive, and the `meeting-record` edge already teaches the meeting-apparatus discriminator in-family. A
  third edge on the same evidence would be noise.
- **`business_operations.corporate-regulatory-filings`** — a regulator-facing incident notification. The
  `compliance-audit` edge already carries the external-authority discriminator; adding a second would
  duplicate it.
- **`research`** — a negative-results write-up and a failed-experiment log are causal accounts of something
  that went wrong. No edge: the anchor triple fails at *organisational unit*, so this family does not
  activate; and a research artifact's anchor is a project or a protocol, which `research` holds outright.
- **`academic`** — a reflective essay. Considered at gist depth and rejected as too thin; the judgment is
  upheld and the reason is now stated (purpose, not topic, and the essay's anchor is a course). Remains a
  `needs_llm` case rather than an edge.

---

## `proposed_fields` — none, and the hole named rather than minted

**None.** This is unchanged from the gist draft and the reasoning is unchanged, but it is now stated against
the anchor's own inventory.

The review's own occasion would use the universal `creation_date` plus, if licensed, the schema row's
proposed `fiscal_period`. The effort under review would reuse the existing canonical `project`. The
genuinely unheld concept is **the event being reviewed, where that event is an incident rather than a
project** — and that is precisely the thing this row must not mint alone, because `risk-register` and
`support-operations` would want the same key for the same occurrence. Minting an incident key here would be
minting a role key on a field-less schema at the exact point of maximum temptation, which the anchor names
as *"the 574's mistake performed knowingly"*.

**Seconding, not minting.** This row seconds both of the schema row's existing proposals — `organization`
(custody, `destination_eligible: false`) and `fiscal_period` (`validated`, not first) — and proposes no
variant of either. The incident hole is recorded as NJ-BO-RP-4 for R1c to adjudicate once, across the three
rows that want it, rather than three times.

`proposed_context_terms` carries 25 practice terms. They are **proposals**. `00`'s named context-term floor
is the academic one (`syllabus`, `lecture`, `credits`, `instructor`, `semester`) and this row does not
pretend otherwise.

---

## Sparse-file discipline, stated for this row's worst case

The row's grouping reasons are the most seductive in the family, because a review packet is
purpose-coherent and content-incoherent by construction — `00`: *"The documents are content-incoherent but
purpose-coherent."* — and the packet frequently arrives as one bounded drop. Both `00` limits apply and both
are in the JSON: *"A session should never be treated as proof of topic, and it should not carry the same
confidence as a hash match or a directly extracted document fact."*, and *"The graph does not automatically
copy those missing facts onto sparse files."*

Concretely: `incident_metrics_20260430.csv`, `retro board 2026-04-30.jpg` and `debrief_recording.m4a` all
sit beside `Postmortem INC-4417 checkout outage.md` and **none of them inherits its incident anchor**. Each
carries `group_without_copying_facts: true`. The image and the audio additionally carry a warning the gist
draft got right and which is worth restating: they are not harmless because they are unreadable. A retro
wall photographs candid statements about named people, and a blameless debrief is candid speech about them.
Any transcription is a model path P7 gates first — *"Privacy policy must be enforced before content reaches
any model or external connector."* — and where signals conflict the answer is abstention: *"A model that
cannot cite sufficient evidence must return unknown."*

---

## What changed in this pass

**Preserved** (checked against the file that was written, not against intent): the row's name; the
`launch: placeholder` / `fields: []` / `proposed_fields: []` posture; all nine original file examples with
their observations, `facts_legal`, `must_not_conclude` and fall-throughs unaltered; all seven original
`collides_with` edges and their signals; all five `falls_through_to` entries with their design quotes;
`work_types`, `grouping_reasons`, `file_kinds`, the 25 `proposed_context_terms`, the `template.why` prose,
and the entire `sensitivity_why` paragraph. The gist draft's first `never_alone` — *"an actions-with-owners
table alone"* — is preserved verbatim because it was the draft's single best line.

**Added.** (1) The incident-header signal rewritten as an explicit structure-plus-labelled-slot pair and
**promoted to first** in `deterministic`. (2) A review-pack signal, marked as never sufficient alone.
(3) Two new `never_alone` entries: a findings-document **shape** alone, answering charge (c); and a
meeting's four-part apparatus alone, answering charge (b). (4) A `collides_with` edge to
`business_operations.meeting-record`. (5) Two file examples — `Retro - sprint 41.docx` (the `meeting-record`
seam, same bytes both sides) and `DR test report - March.docx` (the `risk-register` seam, deliberate and
scheduled). (6) A rewritten `one_line` naming the event-anchored half as load-bearing and dropping the
retired gist label. (7) A rewritten `open_question` grading all four charges, including which one is
answered weakest.

**Reversed, and said plainly.** (i) **The `meeting-record` edge.** The gist draft declined it on the ground
that the neighbour already carried the confusion; that is not the test, and the edge is now written. (ii)
**The grade on leg 1.** The gist draft offered a layout argument ("a section above the actions table") as
the row's detection difference and called the row's three grounds independent and equal. `project-delivery`
was right to call that thin. The leg is re-argued on slot sets, and the three grounds are now explicitly
**unequal** — one decisive, one re-argued, one a consequence. (iii) **Leg 2 is no longer implied to pass.**
The gist draft's `template.why` prose was sound but the test was never stated as unavailable; it is now.

**Not reversed:** the row's verdict. It stands, and the gist pass was right that it stands. What was wrong
was the confidence and one of the reasons.

---

## NEEDS-JOSEPH

- **NJ-BO-RP-1 · Node or `work_type`, now with the four charges on the record.** This pass keeps the row.
  Charges (a), (b) and (c) are answered on evidence; **charge (d) is answered weakest** and is the one to
  test. If R1c disagrees, the alternatives and their costs: folding into `project-delivery` files an outage
  under a project that does not exist (that row refuses to accept it); folding into `risk-register` files a
  realised event among possibilities (that row states the tense discriminator against it); folding into
  `meeting-record` loses every non-meeting member — the log-reconstructed post-mortem, the multi-year
  lessons register, the remediation tracker. There is no clean fold. The cheapest partial is to keep the row
  and narrow it to occurrence-anchored reviews only, ceding the project-closure retrospective to
  `project-delivery` — at the cost of splitting `Phoenix closure report.docx`'s two anchors by catalogue fiat
  rather than leaving it to P10.
- **NJ-BO-RP-2 · The person-versus-effort discriminator**, stated reciprocally against
  `hr.employee-relations` — which **has not landed**, so this edge is one-way and the reciprocal is owed. A
  grievance investigation and a blameless post-mortem are the same document shape; the only discriminator is
  whether a person is the subject or an actor, and it is not marked structurally. Guessing wrong files a
  disciplinary record in an unprotected working branch. R1c should confirm the discriminator this row
  authored, or replace it, and should ensure the `hr` author writes the reciprocal.
- **NJ-BO-RP-3 · Branch naming as disclosure.** A folder named after a failure is a statement about the
  failure, readable without opening anything. This row recommends no dimensions and so cannot cause it
  today, but if fields are ever licensed the branch label needs user approval rather than automatic
  derivation. `00` provides the hook — *"Protected branches should have configurable redaction in the canvas
  and review screens"* — but this is a P10 policy question, flagged here because this row is where it first
  bites and it bites nowhere else in the family.
- **NJ-BO-RP-4 · The incident key, named and deliberately not minted.** Three rows want a key for *the
  occurrence being referred to* — this one, `risk-register` (for a realised risk) and `support-operations`
  (for a major incident). None can mint it alone; a variant per row would be exactly the synonym
  proliferation `canonical_fields.json` exists to prevent. R1c should adjudicate it **once**, across the
  three, in the same way the anchor asks `organization` to be adjudicated once across
  `business_operations` and `construction_property`.
