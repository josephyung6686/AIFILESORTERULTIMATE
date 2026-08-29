# `business_operations.strategy-plan` — lab notes (template row, deepened to J-DEPTH)

Row kind: **template** on `business_operations`. Launch: **placeholder** (`fields: []`).
**Verdict: kept, not refused** — and the deepening pass argues the case for refusing it rather than
assuming the gist verdict, because the dispatch charge against this row is a serious one and two of
its three legs are the same legs that ended `business_operations.organisational-records`.

**Status.** The gist-era JSON was **verified-but-shallow, not untrusted**: its quotations were
machine-checked verbatim, its key set matched the landed siblings, and its two collision fixtures
(`Phoenix project plan.xlsx`, `Our 5 year plan.docx`) were already the right ones. It was therefore
**verified and extended, not rewritten**. The memo was 4.7KB of gist and is replaced. Everything this
memo claims was changed is itemised, and checked against the JSON, in *What changed in this pass*.

---

## Sources actually used

### Binding

- `planning/00-database-agent-product-design.md` — the only document quoted anywhere in the JSON.
  Twenty distinct quotations; all twenty grep back verbatim (see *Self-verification*). The spans that
  did real work on this row:
  - the **multi-role token sentence** — *"A university name alone should not create a group because
    Columbia can appear as an authoring school, course provider, target institution, employer,
    research venue, or merely a cited organization."* Read across to a company name as an
    **inference**, and marked so. It is the sentence the family's refusal turns on, and the first
    charge against this row.
  - the **purpose-coherence sentence** — *"The documents are content-incoherent but
    purpose-coherent."* — which is the licence for this row's characteristic grouping reason, the
    planning round, and the answer to the third charge (that a "plan" is a document type).
  - the **dimension-order rule** — *"For document and record domains, project, function, or subject
    usually comes before time because putting year first scatters related work across calendar
    folders."* — which fixes `time_first: false` even though this row is the family's most plausible
    candidate for a high period level.
  - the **parent-context rule** — *"The recommendation should follow the practical rule that a parent
    dimension should provide the context required to understand the child."* — an options appraisal
    is unintelligible before the reader knows which decision it served.
  - the **topic/purpose distinction** — *"Topic answers what a file is about, while purpose answers
    what the file was for."* — the only clean way to separate the holder's own plan from a collected
    competitor plan.
  - the **abstention sentence** and *"A model that cannot cite sufficient evidence must return
    unknown."* — invoked on the unlabeled-deck and offsite-notes cases.
  - the **session sentence**, the **extension sentence**, the **authorship prohibition**, the
    sparse-file sentence *"The graph does not automatically copy those missing facts onto sparse
    files."*, and the residual definitions for all five fallthroughs.
- `planning/domains/_CONTRACT.md` — rules 1–3, 8 (a dimension may only branch on a declared field),
  10 (no field rows on placeholder schemas), 13 (closed edge vocabulary).
- `planning/domains/CONNECTION.md` — §2 node test, §4 activation (step 2 never-alone), §5 closed edge
  vocabulary, §9 failure mode 6.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/canonical_fields.json`,
  `planning/overnight/council/DECISION-BRIEF.md` (D1 as narrowed, PR-6 taken as ratified),
  `ROSTER.md` Appendix A lines 805 / 807 / 809 — `ops.strategy-plan` (ROW), `ops.okr-goals` (FOLD),
  `ops.business-case` (FOLD).
- `src/evidence_shape/vocabulary.py` — every `source_type` in the JSON checked against `SOURCE_TYPES`.

### Neighbours read in full before writing, and not touched

- **`business_operations.research.md`** (46KB, the schema anchor) — read first. Supplies the default
  template this row must differ from, and the **never-alone principle generalised for all 24
  siblings**. Both are applied explicitly below.
- **`business_operations.organisational-records.json`** — the family's refusal, read on the working
  assumption that this row was heading the same way. It is not, and the reason is stated rather than
  asserted.
- **`business_operations.product-requirements.research.md`** (41KB) — the settled pair question. Its
  reasoning is adopted, not reargued.
- **`business_operations.product-roadmap.json`** — the row this one is charged with duplicating. Its
  `one_line`, its eight deterministic signals and its `collides_with` entry for this row were read
  before the axis section was written.
- **`business_operations.budget-forecast.research.md`** (43KB) — states its edge to this row as
  **two-way** and accepts this row's existing edge *verbatim*. Nothing here contradicts it.
- **`business_operations.risk-register.research.md`** (46KB) and **`.go-to-market.research.md`**
  (47KB) — both name this row and both flag their edges as one-way, owed a reciprocal.

---

## The node test, argued leg by leg

The schema anchor states what a sibling must clear:

> **No sibling may rest its activation on an entity name, a business vocabulary word, or a document
> shape alone.** Each of the three is never-alone here. Every detection signal a sibling writes must
> pair a **structure** with a **labelled slot**. If a proposed row cannot name such a pair, it is not
> a node — it is the schema's default template, or a residual wearing a domain's clothes.

### Leg 1 — detection signals. **Passes**, and this is where the first charge is answered.

The charge is that this row's only signal is an organisation name plus a document-type word, which is
exactly the never-alone evidence that ended `organisational-records`. Taken seriously, the charge is
correct about *one* of the row's candidate signals and wrong about the rest — and the JSON already
disqualifies that candidate rather than relying on it. The word *strategy*, the word *plan*, the word
*goals*, the organisation's name and the slide master are all in `never_alone`, and the deepening
pass **added a sixth** — a stated horizon or a period axis alone, which is `product-roadmap`'s
evidence, not this row's.

What is left after subtracting all of that is four structures, each pairing a shape with a labelled
slot, and each of which a person can see on a page before reading a word:

1. **The options-appraisal structure.** A do-nothing or baseline option set beside two or more
   alternatives, each with costs, benefits and risks, resolving into a **single recommendation** and
   an **approval or decision slot**. No other row in this family has this shape. A project schedule
   has no baseline-versus-alternatives comparison; a budget has no recommendation; a board minute
   records that a decision was taken rather than arguing for one.
2. **The objectives-with-measures-and-owners structure.** Numbered strategic objectives or
   priorities, each carrying measures, targets and a named owner — or the objective-with-nested-key-
   results shape, the same structure in a named idiom. The **owner column** is the labelled slot; a
   bare numbered objectives list without it is in `never_alone`, because appraisal forms, syllabi and
   job descriptions all have one.
3. **The strategic-analysis structure.** A labelled four-quadrant grid, a five-forces or PESTLE
   heading set, a scenario layout naming two or more futures. These are layouts, not vocabulary.
4. **The benefits structure.** Quantified and non-quantified benefits paired with a **realisation
   period** and a **benefit owner** — distinct from a project's deliverable list because it names
   outcomes rather than outputs.

Each is a structure-plus-slot pair, which is precisely the thing `organisational-records` could not
name. That row's refusal was not "business documents are hard"; it was that after subtracting every
sibling situation *nothing structural remained*. Here, subtracting every sibling situation leaves the
options appraisal untouched, because no sibling claims it. That is the difference, and it is the
whole difference.

**A note on honesty here.** The four structures are named real document shapes, not design quotes;
`00` does not enumerate business-case anatomy. They are argued **inference**, and the JSON marks
every edge built on them `provenance: inference`. What is *not* inference is the disqualification
list: the organisation-name, session, extension and sparse-file prohibitions are all quoted.

### Leg 2 — recommended dimensions. **Passes in prose; empty by contract, and the emptiness is not evasion.**

`dimension_order` is `[]` and must be: `business_operations` declares no fields, and `_CONTRACT` rule
8 forbids a dimension branching on an undeclared field. Every sibling is in the same position, so
this leg cannot by itself distinguish anything — the same limitation the requirements row recorded.
What can be said is what the prose order would be, and how it differs from the anchor's paragraph:

> the **organisational unit or entity** *only where the corpus genuinely spans more than one* → the
> **governance body, project, contract, or account** → the **fiscal period** → the **document
> function**. Not time-first.

This row's second level is not a body, a project, a contract or an account — it is the **decision or
planning round**, the thing people actually name and remember (*the 2026–27 plan*, *the warehouse
case*). That is a genuine divergence from the default at the level the default treats as "the real
top", and it is the family's most defensible case for putting a period high. It still does not claim
`time_first`: the anchor is explicit that the time-first exception is capture-based media only and
that a sibling claiming it should be rejected on sight, and a plan year is a content period, not a
capture date. Recorded as `time_first: false` and left there.

### Leg 3 — privacy posture. **Passes, and differs from the family's default in kind.**

Most of this family is `potentially_sensitive` because it carries personal or employment material.
This row is `potentially_sensitive` for a **different reason**: an unapproved plan states intentions
— a closure, a disposal, a redundancy programme, an acquisition — *before the people affected have
been told*, and the harm is disclosure of a future rather than of a person's data. This produces a
posture no sibling shares: **a folder named after an unannounced initiative is itself the leak**,
which is why the JSON reaches for *"Protected branches should have configurable redaction in the
canvas and review screens"* rather than only the prompt-exclusion rule. That is a privacy rule
differing from the schema's default, and leg 3 passes independently of legs 1 and 2.

**Overall: kept.** Legs 1 and 3 pass on their own evidence; leg 2 passes in prose and is contract-
blocked from passing in data.

---

## The second charge, answered: what this row's axis is, and how it differs from the roadmap's

The requirements row settled the requirements-versus-roadmap pair on **structural axis**, and its
reasoning binds here. Its terms: in a roadmap, time is a *structural axis* — the document is
organised **by** period and items sit in period cells; in a specification, time is at most a *date on
the document*; delete the dates from a PRD and it still reads, delete the periods from a roadmap and
it is destroyed. Requirements' own axis is **intended behaviour with acceptance criteria**.

**This row's axis is the argument: a baseline set beside alternatives, compared, resolved into one
recommendation, and signed off.** Stated in the requirements row's own three tests, so the three
files can be laid side by side:

| | axis | does it expire? | what are its atoms? |
|---|---|---|---|
| `product-roadmap` | **period** — items in period cells | **yes**, superseded quarterly; there is one current one | positions in an order; nothing can be *passed* |
| `product-requirements` | **intended behaviour** | **no**, stays true after the quarter | obligations with an acceptance test |
| `strategy-plan` (this row) | **the argued option** | **no**, and for a third reason | **choices under an approval** |

The expiry column is where this row is least like the roadmap and least like the requirements row
too. A roadmap is superseded. A specification stays true. **An approved business case becomes an
archival record of why money was committed** — it is not superseded when the horizon passes, because
its function afterwards is to explain a past decision. Last year's roadmap is stale; last year's
approved case is evidence.

**Why altitude is not the answer, and is not relied on.** The tempting phrasing — "a roadmap is
product-level, a strategy is company-level" — is exactly the move the schema anchor forbids:
*"Differing in business function is not automatically a difference"*, because a function or a unit is
a **value of a dimension**, not a structure. A company-wide roadmap is still a roadmap and this row
does not claim it. The JSON says so twice: the added never-alone entry disclaims a horizon and a
period axis outright, and the added deterministic signal states the discriminator as a **decision
axis versus a period axis**, testable by deleting the dates.

This does not contradict the requirements settlement. That memo listed this row among the
**roadmap's** neighbours, not among its duplicates, and used the same axis-and-expiry reasoning. The
deepening pass adopts it rather than reopening it.

---

## The third charge, answered: is "a plan" a document type rather than a filing world?

Partly yes, and the JSON already concedes the part that is true: *plan* names a project plan, a floor
plan, a lesson plan, a birth plan and a meal plan, and it sits in `never_alone` on those grounds.
Nothing in this row activates from the word.

What makes it a world rather than a type is the **planning round** — the licensed grouping shape.
`00`'s application-packet sentence, *"The documents are content-incoherent but purpose-coherent."*,
describes this pile exactly: a draft narrative, a financial model, a market slide, a benefits sheet
and a blank approval form share nothing in content and everything in purpose. A document *type* does
not produce that pile; it produces copies of itself. This is also the reason the two folded legacy
ids belong here rather than as rows of their own — an OKR set is how a strategy is *stated* and a
business case is how it is *funded*; all three are members of one round, and splitting them would
have scattered one purpose-coherent group across three branches.

---

## Files considered and rejected

| File | Why it is not this row's evidence |
|---|---|
| **`Phoenix project plan.xlsx`** | Kept as the primary collision fixture. It has an objectives sheet *and* dependency-bearing task rows with a critical path. A goals tab inside a schedule does not make a schedule a strategy: the axis is the task order, and there is no baseline-versus-alternatives comparison and no approval slot. `business_operations.project-delivery`. |
| **`Our 5 year plan.docx`** | Kept as the second fixture and the one with real stakes. The horizon-and-goals shape is present *in full* and the subject is a household. Discriminator: first-person plural, no unit, no owner column, no approval. Filing a family's private plan in a work branch is the concrete harm. |
| **`Corporate strategy 2030 - Rival plc.pdf`** | **Added this pass.** Every structural signal fires and the document is somebody else's plan. The discriminator is **custody**, not shape — no approval route the holder is part of, an investor-relations publication apparatus instead. Reading Inbox. |
| **`Market sizing model.xlsx`** | Kept unresolved on purpose: it is analysis for a strategy, an output of market research, and a forecast in shape, all at once. The three candidate rows sit with three different agents; a one-sided resolution here would be a guess. |
| **`Top risks` slide inside the board strategy deck** | **Named this pass, from the risk row's side.** A snapshot quoted *into* an argument, with no likelihood/impact scoring and no review dates — no standing scope of its own. It stays here; the register it was quoted from is a separate file and is the risk row's. |
| **A pitch deck to investors** | Rejected. Its purpose is fundraising, not internal direction-setting, and `finance.cap-table-equity` is a landed row belonging to another agent. |
| **An annual report from the holder's own organisation** | Rejected as a *sole* signal. It reports the year that happened; it accounts rather than recommends. Where it also contains next-year priorities with owners, the objectives structure is what fires, not the report. |
| **A job description with numbered objectives** | Rejected. The numbered-objectives shape without measures, targets and an owner column is the disqualified candidate signal, and this is the file that proves why the owner slot is load-bearing. |
| **`Company letterhead template.docx` / an org chart** | Rejected: named in the refusal row as files a branch root would have swallowed. Neither is argued material. |

---

## Collision fixtures, in both directions

**Direction one — a file that would wrongly fire this row: `Our 5 year plan.docx`.** Horizon in the
title, goals with target years, the word *plan*. Everything a naive signal set would want. What stops
it is the absence of the labelled slots: no unit, no owner column, no approval, and a first-person
subject. It falls through to Independent Records. The row's `career.employment-records` edge names
the same shape from the personal side.

**Direction two — a file that must not be lost *to* this row: `H1 roadmap.pptx`, and now
`Corporate strategy 2030 - Rival plc.pdf`.** The roadmap deck has swimlanes across a quarter
timeline and items in period cells; every theme may be a company initiative and the altitude may be
company-wide, and it is still the roadmap's, because deleting the periods destroys it. The rival
strategy has all four of this row's structures and fails on custody. This row claims neither, and the
added never-alone entry is what enforces the first.

**The same bytes named on both sides.** `Board strategy paper - May.pptx` is named by three rows now:
`board-governance` (paper number, committee footer, pack pagination), `risk-register` (the top-risks
slide), and this row (the recommendation-and-options argument). All three name the same file and
state the same discriminators, so a reader checking one file finds three consistent accounts.

---

## Reciprocal boundaries, stated in both directions

Eleven `collides_with` edges, three added this pass. Direction of authorship recorded honestly, because
the budget row's memo made the point that nine of its ten boundaries ran one way and asked for the
reciprocals to be audited.

| Neighbour | **They take** | **This row takes** | Contested bytes | Direction |
|---|---|---|---|---|
| `business_operations.product-roadmap` | a period axis, items in period cells, now/next/later, release scope | an option comparison, objectives with owners, an approval slot | a company-wide themes-by-quarter deck | **two-way** — that row's edge already names this one and is accepted verbatim |
| `business_operations.budget-forecast` | period-scoped line items with variance against actuals | an argument comparing options over a horizon | a business case: a financial model with a narrative wrapped round it | **two-way** — that row states it and quotes this row's edge as accepted |
| `business_operations.project-delivery` | a dependency-bearing schedule, a RAID log, a status cadence | the case that authorised the project | `Phoenix project plan.xlsx`; the business case that names its own project throughout | authored here; reciprocal owed |
| `business_operations.board-governance` | notice, agenda, pack pagination, minute, resolution | the strategic argument itself | `Board strategy paper - May.pptx` | authored here; reciprocal owed |
| `business_operations.risk-register` | a standing register with likelihood/impact/owner/mitigation/review-date columns | the same risks as one summary slide inside an argument | the top-risks slide in the board strategy deck | **added this pass, reciprocating** that row's one-way edge, in its own terms |
| `business_operations.product-requirements` | out-of-scope sections and given-when-then acceptance criteria — things that can be *passed* | baseline, costed alternatives, recommendation, approval — a thing that can be *approved* | a build-or-buy paper carrying both | **added this pass**; consistent with that row's settled pair verdict |
| `business_operations.go-to-market` | one offering and one launch date | goals, horizons, an initiative portfolio, the funding argument | a launch business case | **added this pass, reciprocating** that row's edge, in its wording |
| `business_operations.market-research` | a research question, a method, a source set | a recommendation and a horizon | `Market sizing model.xlsx` | authored here; unresolved by design |
| `hr.performance-cycle` | objectives attached to **named individuals** with ratings or calibration | objectives attached to units or the entity | `OKRs Q3.xlsx` when the cascade reaches individuals | authored here; **NJ-BO-SP-1** |
| `career.employment-records` | a first-person subject with no unit, no owners, no approval | an entity or unit with owners and measures | `Our 5 year plan.docx` | authored here |
| `research.grants-funding` | a funder, a call reference, a protocol | an internal approval route, an operational benefits frame | a case for support | authored here |

**`also_holds_with` is deliberately empty**, and that is a finding rather than an omission. Every
candidate examined resolved into a collision (the same bytes contested by two rows, mutually
exclusive) or into a role difference, not into one file legitimately carrying two schemas. The
nearest genuine candidate — a nonprofit's strategic plan that is also its trustees' annual report —
is a difference of *entity type*, not of evidence, and the schema row already carries the `nonprofit`
edge.

---

## `proposed_fields` — none, and why

**None minted, none restated.** `fiscal_period`, the key this row wants most for the planning round,
is **already proposed on the schema row** with a full argument and marked `adjudicate: R1c`;
`organization` likewise, seeded `destination_eligible: false` under the collector prohibition.
Seconding both from here rather than minting variants is the brief's instruction and the right
answer regardless: one concept in two places is how a catalogue drifts.

Nothing else this row needs is unheld. A horizon is a **value** of a period key, not a key. Objectives
are content, not a folder dimension. A "decision" or "option" key was considered and rejected: it
would be a field whose values are unique per document, which produces one-child levels — one of the
two failures `00`'s template validator names.

`proposed_context_terms` carries 27 entries and is proposal-grade throughout; `00` names an academic
context floor and nothing for this world, so none of them is claimed as design.

---

## Neighbours considered that did NOT get an edge

- **`nonprofit`** — entity type, not evidence; the schema row carries it.
- **`academic`** — a departmental strategy is structurally identical to an organisational one and adds
  nothing an edge could discriminate on.
- **`business_operations.meeting-record`** — an offsite's notes are a real ambiguity and it is stated
  as a `needs_llm` line rather than an edge, because the discriminator is *whether the document
  argues or records*, which is a model judgement, not a structural one.
- **`business_operations.retrospective-postmortem`** — looks adjacent (both are reflective documents
  about a unit) and is not: a retrospective is backward-looking about what happened, and has no
  option comparison and no approval. No contested bytes were found, so no edge was authored.
- **`business_operations.partnerships-bd`** — a joint-venture case would contest bytes, but that row
  is being deepened in this same pass by another agent and a one-way edge authored blind into a
  moving file is worse than none. Flagged to R1c below instead.

---

## NEEDS-JOSEPH

- **NJ-BO-SP-1 · Should OKRs and goals have stayed folded here?** The fold is right at entity and
  team level and wrong at individual level, where the same workbook becomes a performance record
  under `hr.performance-cycle` — and the cascade means one file often holds both, tab by tab.
  *Alternatives and costs:* (a) keep the fold and rely on the named-individual discriminator — cheap,
  but a mis-fire files someone's personal objectives under a corporate branch, which is the privacy
  cost; (b) split individual OKRs to `hr.performance-cycle` outright — safer, but the cascade file
  then has no home at all; (c) route the mixed workbook to Protected Records — safest, and loses the
  organisational material. Unresolved; R1c should settle it, and this row does not choose.
- **NJ-BO-SP-2 · Another organisation's strategy.** This pass routes a collected competitor plan to
  the Reading Inbox and now carries `Corporate strategy 2030 - Rival plc.pdf` as the fixture. The
  market-research reading is defensible — a competitor's published strategy is a research source. The
  cost of being wrong either way is small (both destinations are recoverable), which is why it is
  stated rather than escalated.
- **NJ-BO-SP-3 · The reciprocals this row is owed and cannot write.** Six of eleven boundaries are
  authored one-way from here: `project-delivery`, `board-governance`, `market-research`,
  `hr.performance-cycle`, `career.employment-records`, `research.grants-funding`. A single node agent
  may not edit a neighbour. **Recommendation to R1c:** add the matching edge on each, and add the
  `partnerships-bd` pair (joint-venture case) that this memo deliberately left unauthored.
- Inherits the schema row's **NJ-J-IND-3** (where an organisation's money lives) by reference: a
  business case is a financial model with a narrative, and the `budget-forecast` boundary depends on
  that unresolved answer. Both rows now state it, and neither guesses.

---

## What changed in this pass

Checked line by line against the JSON as written, not against intent.

**Preserved unchanged** — the row's verdict; all nine original `file_examples` (both collision
fixtures included); all eight original `collides_with` entries with their original wording; all five
`falls_through_to` entries; `work_types` (10); `grouping_reasons` (5); `proposed_context_terms` (27);
`sensitivity` and its full justification; `template.dimension_order: []` and `time_first: false`;
`fields: []` and `proposed_fields: []`.

**Added to the JSON:**

1. `one_line` — the axis statement replacing the horizon-anchor phrase, naming `product-roadmap` and
   `product-requirements` and the delete-the-dates test; and the `Gist-level placeholder` label
   replaced with `Placeholder row (J-IND, deepened to J-DEPTH)`.
2. `recognition.deterministic` — one new signal (now 8): the **decision axis versus period axis**
   discriminator with the delete-the-dates test.
3. `recognition.never_alone` — one new entry (now 9): **a stated horizon or a period axis alone**,
   with the explicit statement that altitude is not a structural difference.
4. `collides_with` — three new edges (now 11): `business_operations.risk-register` (reciprocating
   that row's one-way edge, in its terms), `business_operations.product-requirements` (approvable
   versus passable), and `business_operations.go-to-market` (reciprocating that row's existing edge,
   in its wording).
5. `file_examples` — one new example (now 10): `Corporate strategy 2030 - Rival plc.pdf`, the
   must-not-be-lost-to-this-row direction, falling through to Reading Inbox.
6. `file_examples` — `Board strategy paper - May.pptx` extended by one observation (the top-risks
   slide) and one `must_not_conclude` (naming `risk-register` and its discriminator).
7. `open_question` — a third question appended and **settled**: the roadmap-altitude charge, with the
   axis/expiry/atoms reasoning and an explicit statement that it does not contradict the
   requirements row's settlement.

**Reversed:** nothing. The gist verdict (`refuse_node: false`) is **confirmed, not assumed** — the
refusal case was argued in full above and fails on leg 1, because the options-appraisal structure
survives subtracting every sibling. Leg 3 passes independently on a privacy posture no sibling shares.

**Where this row has less to say than its longest siblings, it says less.** Leg 2 is contract-empty
for every sibling and is not inflated here; `also_holds_with` is empty and the emptiness is argued
rather than filled.

---

## Self-verification

- `python3 -m json.tool` on the JSON: **parses**.
- All **20** distinct `“…”` quotations in the JSON grep back **verbatim** against
  `00-database-agent-product-design.md` — checked programmatically, zero failures.
- Key set unchanged from the landed siblings' 27 keys; no key added, none removed.
- Every `file_examples.source_type` is in `SOURCE_TYPES`; every `falls_through_to.residual_template`
  is one of `00`'s residual names; every `collides_with.domain` is a roster id.
- `fields: []` and `proposed_fields: []` hold; no dimension names an undeclared field; no threshold,
  count or confidence score appears anywhere.
- No folder path is written as a fact in any example.
- Files written: **only** `business_operations.strategy-plan.json` and `.research.md`. No neighbour
  edited; the three neighbour changes this row wants are recommendations to R1c under NJ-BO-SP-3.
