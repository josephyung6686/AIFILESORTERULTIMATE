# `business_operations.go-to-market` — lab notes (template row)

**Depth: J-DEPTH.** Deepened from the gist draft of the same name. The gist verdict (**stands**) is
**upheld**, but its reasoning is replaced — see *The node test* and *What changed in this pass*. The
fold question the gist row stated against itself is **settled here** rather than restated, per the
principle the `product-requirements` pass established: *a question stated identically on two rows is
a well-documented deferral, not an answer.*

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — authoritative. Every quotation below is verbatim
  and was re-checked with `grep -c -F`; each returns exactly `1`.
- `planning/01-product-design-structured.md` — numbered rendering only; `00` wins.
- `planning/prompts/ALIGNMENT.md`; `planning/domains/_CONTRACT.md`;
  `planning/domains/CONNECTION.md` + `CONNECTION-EXAMPLES.md`.
- `planning/domains/canonical_fields.json` — read to confirm that no key on it fits this row, and
  that this row mints none.
- `planning/domains/roster.json` — id, `kind`, `schema_id` and every edge target confirmed present.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` checked against every fixture.
- `planning/domains/ROSTER.md` §4 + Appendix A — line 833 and line 829.

### Family and neighbour files read before writing (and not touched)

- **`business_operations.research.md`** (deepened schema anchor) — the default template, the four
  default detection shapes, and the **never-alone principle generalised for all 24 siblings**. This
  row is measured against that paragraph explicitly, below.
- **`business_operations.organisational-records.json`** — the family's one refusal, read first on the
  dispatch's assumption that this row might be heading the same way. It is not; the reason is argued
  rather than asserted in *The charge*, below.
- **`business_operations.product-roadmap.json`**, **`.market-research.research.md`** (deepened),
  **`.product-requirements.research.md`** (deepened), **`.project-delivery.json`**,
  **`.strategy-plan.json`**, **`.customer-account-management.json`**, **`.partnerships-bd.json`**,
  **`.support-operations.json`**, **`.user-research.json`**.
- `creative.json` and `creative.research.md` for the campaign seam.

### Sources deliberately NOT used

- `creative.ad-campaign` and `creative.content-marketing` **have not landed** — only
  `creative.creative-brief`, `creative.raw-photo-catalogue` and `creative.self-initiated-work` exist
  as node files. The gist draft cited both as if read. They are real roster ids, so the edges are
  valid, but the boundaries to them are written **one-way from this side** and the reciprocals are
  owed. That correction is recorded rather than hidden.
- `planning/deferred-catalogues/` — this row's recognition consumes no catalogue. No gazetteer
  contents invented (R4), no detector regexes written (R2), no thresholds, no scores.

---

## The charge this row had to answer

The dispatch's warning was the sharpest given to any row in this family, and it deserves a direct
answer rather than a defence:

> "Go to market" is plausibly a **phase or an activity**, not a filing world — a launch is a moment
> in a product's life, and its documents each plausibly belong to a sibling that already exists.

**The first half of the charge is true and does not decide anything.** A launch *is* a phase. So is
a project (`project-delivery`), a study (`market-research`, `user-research`), a pursuit
(`partnerships-bd`) and a planning horizon (`strategy-plan`) — five of this family's rows are
temporally bounded activities, and the roster kept all five. CONNECTION §2's test does not ask
whether a situation is durable. It asks whether its **detection signals**, its **recommended
dimensions**, or its **privacy rules** differ from its schema's default template. Duration is not one
of the three legs and cannot be smuggled in as a fourth.

**The second half of the charge is the real one**, and it is the `organisational-records` failure
restated: if every document here is better explained by a sibling, the row's only remaining content
is a *word* — "launch" — and the anchor's rule kills it outright:

> **No sibling may rest its activation on an entity name, a business vocabulary word, or a document
> shape alone.** Each of the three is never-alone here. Every detection signal a sibling writes must
> pair a **structure** with a **labelled slot**.

So the whole question is whether this row can name **structure-plus-slot pairs that no sibling owns**.
That is what leg 1 below does, one pair at a time, and it is the test the gist draft did not run —
the gist argued from the row's *anchor* (one offering, one date, several functions), which is a
statement about purpose, and purpose is not a detection signal. Had that been the whole case, the
family rule would have refused this row, exactly as it would have refused `market-research` on the
same mistake.

**The answer is that the row survives**, on four pairs and on a privacy ground that is genuinely its
own. But the survival is narrower than the gist implied, and the boundary work below removes several
things the gist claimed.

---

## What it is for, and what it holds

The coordinated effort to make one offering **publicly available** on a dated, largely irreversible
moment, and the material produced to gate and support that moment: the cross-functional launch plan,
the readiness gate and its go / no-go record, the decided positioning and messaging, competitive
battlecards and sales enablement, packaging and pricing **as put into force**, the announcement and
its embargo, beta and reference-customer programmes, launch FAQs, and the post-launch review that
closes the loop against the plan's own targets.

The anchor stated precisely, because the gist's version was loose: **not** "one offering, one date,
several functions" — that describes a project — but **one offering crossing from private to public at
a stated instant, with several functions gated on that instant.** The crossing is what makes the
material both cross-functional and time-limited-confidential, and both of those are what the node
test turns on.

## Legacy ids absorbed (ROSTER.md Appendix A)

- Line 833: **`ops.go-to-market` (ROW)** → this row. That is the only id assigned here.
- Line 829: **`ops.pricing` (FOLD) → `business_operations.market-research`**, *"pricing work is built
  on the same commercial analysis"*. The gist draft read this narrowly and claimed "decided pricing in
  force" for itself. That reading is **corrected and narrowed further** below — see *The pricing fold,
  settled*.

---

## The node test, argued leg by leg

CONNECTION §2's template test. The schema's default template, quoted from the deepened anchor so the
comparison is checkable:

> the **organisational unit or entity** *only where the corpus genuinely spans more than one* →
> the **governance body, project, contract, or account** the material belongs to → the **fiscal
> period** → the **document function**. Not time-first.

And the anchor's four default detection shapes: the **governance-cycle structure**; the
**controlled-document header** (version / owner / approver / effective date / review date); the
**management-financial table without an institution header**; the **post-signature obligation
register**.

### Leg 1 — detection signals. **PASSES, on four structure-plus-slot pairs.**

First, against the schema's own four defaults, one at a time:

- **Against the governance-cycle structure.** A body name, a period date, an attendance list, a
  numbered agenda, a resolution block. A go / no-go meeting has attendees and a recorded outcome, so
  this is the closest of the four and the closeness is worth admitting. It is not a governance cycle:
  there is no constituted body, no standing terms of reference, no quorum, no numbering that
  continues into the next meeting. A launch gate happens **once, for one offering**, and its outcome
  is *ship / do not ship*, not a resolution binding the organisation. Where a launch decision *is*
  minuted by a constituted body with a quorum line, it has become board material and
  `business_operations.board-governance`'s signal is the better read; this row should not fight for
  it. Stated reciprocally in the boundaries table.
- **Against the controlled-document header.** Version / owner / **approver** / effective date /
  **review date**. A price book carries an effective date and an approval line — three-fifths of the
  header — and this is the second close call. It is not a controlled document: the missing slot is
  the **review date**, the periodic-recertification apparatus that makes a policy controlled. A price
  book is not reviewed on a cycle; it is **superseded** by the next one. Where a pricing document
  does carry a review date and a document owner, it has become `policy-handbook`'s.
- **Against the management-financial table.** Budget / forecast / actual / variance over line items.
  A packaging grid is tiers × features × list price. Both are money in cells and `00` licenses
  reading both — *"Tables matter because resumes, forms, applications, invoices, and administrative
  documents often place their most useful information in cells rather than body paragraphs."* — but
  the header vocabularies do not share a column: a variance column is retrospective and internal, a
  list-price column is prospective and external. No overlap at a single header.
- **Against the obligation register.** Renewal dates, notice periods, counterparties. Nothing in this
  row manages a post-signature relationship with a named external party. The nearest thing — a
  reference-customer agreement — is exactly the file this row hands to
  `customer-account-management` and to `legal`.

None of the schema's four defaults is this row's. Now the four pairs that are:

1. **The readiness gate.** A grid whose **rows are organisational functions** (product, marketing,
   sales, support, legal, operations) and whose columns are **readiness criteria**, a status marker,
   and a **go / no-go slot with a date and named attendees**. The structural fact is *functions on an
   axis* — the same shape-fact that earns `market-research` its competitive matrix (*n* companies on
   an axis). No other sibling produces a grid indexed by function against criteria: `project-delivery`
   indexes work packages against dates and predecessors, which is a different axis and a different
   column set.
2. **The positioning canvas.** A document with labelled slots for **target segment, problem,
   category, differentiators, proof points and messaging pillars** — a recurring template layout,
   present as labelled headings rather than as prose. `market-research` owns the *inputs* to it (the
   matrix, the sizing ladder, the price-capture export, all of which are observations of a market);
   this owns the *decided output*, whose slots are assertions the organisation has committed to.
   The slot set is unique on the roster.
3. **The battlecard.** Paired **objection → response** and **competitor → counter** blocks with an
   **internal-use-only footer**. Two labelled slots and a stated audience. The audience slot is the
   discriminator that a customer-facing one-pager lacks, and it is a real, printed slot, not an
   inference.
4. **The embargo block.** A **dateline + boilerplate** pair with an **"embargoed until" slot carrying
   a date and time**. This is the only labelled slot on the entire roster that states *the instant at
   which a document stops being confidential*. It is both a detection signal and the whole of leg 3.

**Verdict: passes.** Four pairs, two close calls against the family defaults, each close call
recorded and each producing a boundary rule rather than a claim. The honest limit, stated as
`market-research` stated its own: **strip the gate, the canvas, the battlecard and the embargo block
out, and this row has nothing.** A folder of decks that merely *mention* a launch is `work_type`
chatter and this row must not fire on it. That limit is written into `never_alone`.

### Leg 2 — recommended dimensions. **CANNOT PASS, and does not need to.**

Empty by binding contract, not by omission: `business_operations` declares no field rows (PR-6, D1's
deferral as narrowed, `_CONTRACT` rules 10 and 15), so `dimension_order` is `[]` here and on all 24
siblings. A dimension naming an undeclared field would open a tree level no fact could ever fill, and
`00` would then flag it — *"It should warn when a level produces only one child"*.

**Neutral for the whole family; not a pass and not a failure.** CONNECTION §2's test is disjunctive,
so a row passing leg 1 stands with leg 2 unavailable.

The recommendation held as prose does differ from the default paragraph at two levels, in the same
*shape* of divergence `market-research` argued:

- **Level two is the launch, not a governance body, contract or account.** A launch has no
  counterparty and no governing body; what holds a plan, a canvas, a battlecard, a press release and
  a retrospective together is the launch itself. That is `00`'s purpose-coherence case exactly —
  *"The documents are content-incoherent but purpose-coherent."* — and the parent-context rule makes
  it mandatory rather than stylistic: *"The recommendation should follow the practical rule that a
  parent dimension should provide the context required to understand the child."* An enablement deck
  is unintelligible above its offering, and a readiness checklist above its launch, in exactly the way
  `Homework 3` is unintelligible above its course.
- **The `fiscal_period` level drops out.** A launch is not periodic. Its date is a *content* date and
  an external event, not a management calendar, and a fiscal level above it would split one launch
  across two quarters for no reason.
- **`organization` is inherited unchanged**, including its seeded ineligibility — in a single-entity
  corpus it names the user's own employer above everything they have filed, which is both of `00`'s
  validator failures at once (*"create meaningless one-child levels"*, *"use an author or
  organization merely as a collector"*). Inherited, therefore not claimed as a difference.
- **The tempting alternative, named and rejected: a date-first tree.** It is the most seductive here
  of anywhere in the family, because the situation is *defined* by a date. It is still wrong, and the
  anchor forbids the whole family from claiming the time-first exception, which `00` grants to
  capture-based media only: *"For document and record domains, project, function, or subject usually
  comes before time because putting year first scatters related work across calendar folders."*
  `time_first: false`, and whatever eventually lands stays a recommendation — *"The system recommends
  an order based on the domain template, but the user can reverse, remove, add, or flatten
  dimensions."*

### Leg 3 — privacy rules. **PASSES, on a ground no other row in the family has.**

The schema's posture rests on the exposed party usually not being the user, on attachment carriage,
and on the `hr` bleed. The first applies here strongly; the third barely at all. Neither is this
row's own. The distinguishing ground is:

> **This row's confidentiality has a stated expiry, and the file says when.** An embargoed
> announcement, an unreleased price book, an unshipped feature list and a pre-announcement customer
> quote are damaging before an instant and harmless after it. Nowhere else in the family does a
> document carry, in a labelled slot, the moment at which its own sensitivity ends.

Three consequences, none of which is a handling class (P7 owns those and this row assigns none):

1. **The cautious value is correct for the whole row despite most of the material being dull**, which
   is the opposite of the argument `project-delivery` made when it declined the cautious value for
   the same family. The reason is that the *worst* member here — an embargoed release naming
   executives and a reference customer — is indistinguishable in form from the harmless member, and
   arrives in the same folder.
2. **The exposed third party often cannot consent and is not the user**: reference customers named in
   draft quotes; competitors whose capabilities are asserted in a battlecard (those assertions are
   the holder's claims about someone else, not facts about them).
3. **Post-expiry, the same file is a public document**, and nothing in the pipeline knows the date has
   passed. That asymmetry is NJ-J-IND-4's variant and is carried, not solved.

`00`'s corpus sentence reaches this row through named individuals in draft quotes and reference
records — the corpus *"can include identity documents, account statements, tax records, medical
information, legal records, credentials, private correspondence, GPS metadata, employment materials,
and educational records"* — and the enforcement point is `00`'s: *"Privacy policy must be enforced
before content reaches any model or external connector."*

**Verdict: passes.**

### Overall

**Kept.** Leg 1 passes on four pairs, leg 2 is unavailable to the whole family, leg 3 passes on a
ground that is uniquely this row's. **I am not reversing the gist verdict — I am replacing its
argument**, which rested on purpose rather than on evidence and would not have survived the anchor's
never-alone rule.

---

## The fold question, settled

The gist row recorded NJ-BO-14 against itself: *this is the weakest of the nine rows in this chunk;
KEEP on the readiness gate; the alternative is to fold it into the roadmap row and let the campaign
row hold the external material.* The schema anchor repeated the doubt in NJ-BO-2. Two files stating
the same unresolved question is the deferral pattern `product-requirements` named. It is settled here.

**The fold candidate the gist named is the wrong one.** Folding into `product-roadmap` fails
immediately: a roadmap is *"a communication about time, it expires, and there is one current version
of it"* (its own `one_line`), organised on a period axis with sequenced themes. A readiness gate has
no period axis, does not expire — it is a decision record that stays true — and there is no "current
version" of a go / no-go that happened. Delete the periods from a roadmap and it is destroyed; delete
the date from a gate record and the criteria and the decision still read. Different relationship to
time, in the roadmap row's own terms.

**The real fold candidate is `project-delivery`**, and the gist named it only in passing. A launch is
a bounded effort with a start, an intended end and a named owner, which is that row's anchor
verbatim. Three checkable separations decide it, none of them "one is bigger than the other":

1. **What the plan's rows are, and what column decides.** `project-delivery`'s own strongest signal
   is stated in its file as *"A dependency column is the strongest single discriminator against every
   other table in this family"* — work packages against start, end, percent-complete, predecessor,
   assigned resource. A launch readiness grid has **no dependency column and no percent-complete**;
   its rows are **functions**, and its columns are **criteria that are met or not met**. Percent-
   complete is meaningless against a criterion: legal sign-off is not sixty per cent done. Two grids, disjoint
   header vocabularies.
2. **Whether the end is internal or external.** A project ends on **acceptance and handover** — that
   row's closure structure pairs a deliverables-accepted block with a handover-to-operations block,
   and both parties are inside the organisation. A launch ends by **becoming public**, at an instant
   the organisation does not fully control and largely cannot reverse. The gate exists *because* the
   end is external and irreversible; nothing in project closure needs a go / no-go, because a project
   that is not ready simply slips.
3. **Whether the document's sensitivity has an expiry.** `project-delivery` explicitly declines the
   cautious sensitivity value for its bulk material and detects sensitivity per file. This row takes
   it for the whole row, on the embargo ground in leg 3. That is a privacy-rule difference between the
   two rows *directly*, not merely against the schema default — which is CONNECTION §2's third leg
   doing exactly what it is for.

**Where the merge case remains real, and why it does not win.** It is not dismissed: in a small
company one person writes both the launch plan and the project plan, in one folder, in one workbook;
and the leg that would separate them most visibly (dimensions) is unavailable to both. But that is an
argument about **how a small team stores** material, and the node test is about **what evidence
activates**. On evidence they are not close: a predecessor column and a per-function criteria column
do not co-occur by accident, and where a single workbook holds both, both rows activate on disjoint
evidence and P10 chooses — which is the designed outcome, not a defect.

**A fourth argument, from the catalogue rather than from the file.** Four landed siblings —
`product-roadmap`, `market-research`, `customer-account-management`, `partnerships-bd` — each already
carry a `collides_with` **to this row**, and each uses "a launch date, positioning and readiness
checks" as the *other side* of its own discriminator. Refusing this row would leave four dangling
edges and four discriminators that name nothing. That is not a reason to keep a row that fails the
test — `organisational-records` was refused with edges pointing at it — but it is evidence that four
independent authors found a real seam here, and it should be recorded before R1c reopens the question.

**Verdict: KEEP, and NJ-BO-14 is downgraded** from an open question about whether the row survives to
a narrow re-examination trigger: *if a fields pass never happens and real corpora turn out not to
contain readiness gates, positioning canvases and embargo blocks — only decks that mention launches —
then leg 1 fails and the row should be folded into `project-delivery`, with the external material to
`creative.ad-campaign` and the residue to Reading Inbox.* That is the condition the verdict rests on,
stated so it can be checked. The `open_question` string is rewritten to record the settlement.

---

## The pricing fold, settled

ROSTER Appendix A line 829 folds `ops.pricing` into `business_operations.market-research`. The gist
draft accepted the fold at the row level and then took "decided pricing in force" back for itself,
which is close to reversing a roster decision by prose. Narrowed here, and stated reciprocally:

- **`market-research` owns pricing as a body of work**, standalone: sensitivity studies,
  willingness-to-pay analysis, competitor price captures, scenario models — including the decided
  output when it stands alone in a pricing folder. Its own file already claims the price-capture
  export as one of its three structure-plus-slot pairs, and I do not contest it.
- **This row claims a packaging-and-pricing grid only where a launch structure is present in the same
  evidence** — a tier × feature × price grid inside a launch pack, or one whose effective date is the
  launch date. Absent that, it is not this row's.
- **The genuinely mixed workbook** — a scenario tab and a final price sheet in one file — is
  disjoint evidence, both rows activate, and neither resolves it from structure. `needs_llm` on both
  sides.

This narrows the gist's claim and is recorded as a change rather than made silently. R1c may prefer
to hand pricing wholly to `market-research`; the cost is that a launch pack then splits at the
pricing sheet.

---

## Files considered and rejected

A row that only lists what it holds has not been researched. The tempting false positives, and the
discriminator for each. The first four are kept as fixtures in the JSON.

| File | Why it is **not** this row's evidence |
|---|---|
| `The Ultimate Product Launch Playbook.pdf` (**primary collision fixture**) | Complete launch furniture — templates, sample gates, checklists — with a vendor's brand on the cover and a lead-capture page. Every deterministic signal this row owns fires on it, because a playbook is *made of* this row's structures. Discriminator: *"Topic answers what a file is about, while purpose answers what the file was for."* It was for *teaching* a launch. **Reading Inbox.** |
| `Atlas roadmap FY26.pptx` (**second fixture**) | A period axis with sequenced themes, now/next/later, no criteria, no functions, no single date. `product-roadmap`'s, and its own file says so in matching terms. |
| `Press release - Atlas 2.0 - EMBARGOED.docx` (**third fixture**) | Kept precisely because it is *this row's*, and is the row's clearest sensitivity case: a **public form that is precisely not public** before its stated instant. The trap is reading the form and concluding the status. |
| `Launch plan - Atlas 2.0.xlsx` vs a project plan (**fourth fixture**) | Both are dated grids in a `Launch` folder. Discriminator is the column set: predecessor + percent-complete versus function + criterion. See the fold section. |
| A **landing page mockup**, a **launch video**, a **social asset set** | Creative production artifacts. `creative.*` owns them, and claiming them would have made this row a campaign row wearing a launch label. Dropped, as the gist also dropped them — that judgement was right and is preserved. |
| A **win/loss review** or a **competitive teardown** | `market-research`'s: an observation of a market. This row's competitive artifact is the *battlecard*, which is an internal selling instrument with an objection→response structure, not an analysis. |
| A **customer-facing one-pager** with the same content as a battlecard | Near-identical bytes. The internal-use footer is the only reliable slot, and where it is absent, abstain — *"A model that cannot cite sufficient evidence must return unknown."* |
| A **beta agreement** or a **reference-customer consent form** | An instrument. `legal` protects first (CONNECTION §4 step 5). This row holds the *programme* — the recruitment list, the schedule, the feedback loop — not the signed paper. |
| A **launch retrospective naming an individual's performance** | Crosses into `hr` at the sentence where it does. The stricter side governs those members even where this row activates on the container. |
| A **sales quota plan** or **commission schedule** | Enablement-adjacent and not this row's: a quota names individuals against money, which is `hr`'s posture, and a compensation plan is `career`'s from the individual's side. |
| A **conference talk deck about launching products** | Saturated in this row's exact vocabulary, owned by nobody's launch. Reading Inbox, and the reason "launch vocabulary" heads the `never_alone` list. |
| A **job description for a Product Marketing Manager** | Reads like a launch charter and is `career`'s — held by the individual as recruiting material. |
| `Screenshot 2026-05-06 at 11.20.44.png` of a launch board (**fixture**) | OCR shows swimlanes and status chips; no header, no labelled slot, system-generated filename. And *"the system must not mistake the absence of EXIF for proof that an image is a screenshot"*. Temporary Screenshots. |
| `atlas-launch-kit.zip` (**fixture**) | *"the normal scan should never extract archive contents to the filesystem"*. No purpose fact from a manifest, and the presence of logos and a video is not a creative conclusion. |

---

## Collision fixtures, both directions

**A file that would wrongly fire this row.** `The Ultimate Product Launch Playbook.pdf`. This is a
worse case than most rows face, because the false positive contains **genuine instances of all four
of this row's structure-plus-slot pairs** — a sample readiness gate with real-looking criteria, a
blank positioning canvas with every slot labelled, a specimen battlecard, a specimen press release
with an embargo line. Structure cannot separate them; only the values can, and the discriminator is
the same one the schema anchor names for its own fixture: whether the value slots carry **this
organisation's actual commitments**. The playbook's owner column says `[Name]`; a real gate names a
person and a date. This is `needs_llm` and it is one where the abstention sentence applies without
softening. **What emphatically does not discriminate:** the brand on the cover or the slide master —
*"PDF metadata should be treated as supporting evidence, not as truth"*, and a corporate template
stamps the same entity on every blank form it ever generated.

**A file that must not be lost *to* this row.** `Atlas 2.0 - PRD v3.docx`, a specification with
given-when-then acceptance criteria and an out-of-scope section, filed in the launch folder because
the launch is what everyone was working on. It names the offering, it names the launch quarter, and
it sits beside the plan. `product-requirements`' own settled rule governs and this row obeys it: *a
file with an out-of-scope section and given-when-then criteria is that row's, even if it opens with a
target quarter on page one.* This row does not claim it, and folder membership is not evidence —
*"A session should never be treated as proof of topic"* is `00`'s statement of the same discipline
for download sessions, and the reasoning carries.

**The same bytes, named on both sides.** `Pricing and packaging - Atlas - effective 01 Jun 2026.xlsx`
is named as a fixture here and is the file the pricing fold above splits. `Launch plan - Atlas
2.0.xlsx` is named here and is the file the `project-delivery` fold turns on. Both are stated with the
same discriminator on each side.

---

## Reciprocal boundaries, both directions

| Neighbour | This row must not take | The neighbour must not take | Shared fixture bytes |
|---|---|---|---|
| **`business_operations.project-delivery`** (landed) | a plan whose rows are **work packages** with predecessors, percent-complete and assigned resources; a RAID log; a recurring period status form; a closure/handover pack | a grid whose rows are **functions** against readiness **criteria** with a dated go / no-go slot; and the post-launch review measured against the launch's own targets | `Launch plan - Atlas 2.0.xlsx` |
| **`business_operations.product-roadmap`** (landed) | a **period axis** with sequenced themes, a prioritisation score table, a changelog under added/changed/fixed/deprecated | the launch **gate**, positioning, enablement and announcement material for one dated release. Its own edge to this row already says so | a release-scope list with a cut line **and** a readiness column — disjoint evidence, both activate |
| **`business_operations.product-requirements`** (landed) | an out-of-scope section, given-when-then acceptance criteria, a traceability matrix — that row's settled rule stands and is not re-litigated here | a **market-facing** segment / problem / differentiator / proof-point slot set describing the same feature to buyers | `Atlas 2.0 - PRD v3.docx` in the launch folder |
| **`business_operations.market-research`** (landed) | the competitive **matrix**, the sizing **ladder**, the price-capture **export** — its three pairs, uncontested; and standalone pricing analysis per line 829 | the **decided** positioning canvas, the seller-facing battlecard, and a packaging grid inside a launch pack | `Pricing and packaging - Atlas - effective 01 Jun 2026.xlsx` |
| **`business_operations.customer-account-management`** (landed) | one **named customer's** own plan, usage, health and renewal record | the **programme** the customers were recruited into — the beta cohort list, the reference schedule, the launch-quote approvals. Its own edge already draws it this way | a reference-customer case study |
| **`business_operations.partnerships-bd`** (landed) | a **named counterparty being pursued** — pitch, proposal, negotiation trail to signature or loss | a joint launch's own gate and announcement, where the partner is a channel rather than the subject | a co-marketing annex; its own edge already draws it this way |
| **`business_operations.strategy-plan`** (landed) | goals, horizons, OKRs, an initiative portfolio, a business case arguing an option should be funded | the execution of a funded decision at its public moment | a launch business case — the funding argument (theirs) and the gate it feeds (ours) |
| **`business_operations.board-governance`** | a constituted body's minute with quorum, numbering and a resolution block, even where the subject is the launch | a launch gate's own decision record, which binds a launch and not the organisation | a board paper recommending a launch date |
| **`business_operations.policy-handbook`** | a controlled-document header **with a review date** — the recertification apparatus | a price book that is superseded rather than reviewed | a discount-approval policy |
| **`business_operations.support-operations`** (landed) | the ticket/case record, queue and SLA reporting, the standing knowledge base | launch FAQs and support enablement **produced by the launch and gated on it** — they are this row's until they enter the standing knowledge base, at which point they are that row's | a launch FAQ, before and after publication |
| **`creative.ad-campaign`** (**roster id; row not landed — one-way, reciprocal owed**) | a channel plan, creative concepts and asset versions, a media buy, a revision round, production files | the cross-functional readiness gate and the internal enablement set | a launch messaging deck used to brief a campaign |
| **`creative.content-marketing`** (**roster id; row not landed — one-way, reciprocal owed**) | an editorial calendar, a content brief, an asset production trail | the launch plan and gate that commissioned the content | a launch blog post draft |
| **`legal`** (safety) | an executed agreement, a trademark registration, a privileged clearance opinion — `legal` protects first | the **naming/approval record and the launch's own legal-readiness criterion**, which are gate rows, not instruments | a beta agreement; a trademark clearance |
| **`hr`** (schema not written) | anything that identifies **named employees** — a quota plan, a launch bonus schedule, a retrospective naming performance | role-level enablement content addressed to a selling function with no individuals named | a launch retrospective that names a person mid-document |

---

## Neighbours considered that did NOT get an edge

- **`business_operations.user-research`** — launch feedback loops touch it, and beta feedback is
  arguably a study. No edge: that row's activation requires participant-derived raw material
  (screeners, consent, transcripts), which a beta programme's *administration* does not contain. The
  discriminator is already carried once by the `customer-account-management` edge.
- **`hr.training-development`** — sales enablement *is* training, and the gist declined the edge. That
  judgement is **preserved and now argued**: enablement here is commercial content whose audience is a
  selling function and whose lifetime is one launch; `hr`'s row is anchored on an employee's
  development record, which is a person-anchored, longitudinal thing. Different anchor, and adding an
  edge would imply contested evidence where there is only a contested word.
- **`academic`** — a business-school launch case study is identical in vocabulary and shape. No edge,
  for the anchor's stated reason: `academic` fires on its own evidence, and the confusion is fully
  handled by this row's `never_alone` entry on launch vocabulary.
- **`code`** — a release engineering repository contains a launch checklist. No edge: `code` owns the
  repository layout, and this row must not propose re-filing anything inside a preserved root.
- **`business_operations.contract-administration`**, **`.procurement-sourcing`**,
  **`.compliance-audit`** — each touches a launch at one gate row. An edge to each would say only that
  a launch has legal, sourcing and compliance criteria, which is true and useless. A criterion naming
  a function is not a claim on that function's records.

---

## Sparse-file discipline

The single most likely damage this row could do is **copying an offering label onto every file that
mentions the product**. A launch folder is exactly the setting where that temptation is strongest,
because the offering name is the most salient token in every filename. `00` forbids it directly:
*"The graph does not automatically copy those missing facts onto sparse files."* Every fixture in the
JSON carries `must_not_conclude` entries to that effect, and the schema declares no fields to write
in any case.

The corresponding grouping discipline: a launch pack is a legitimate purpose-coherent group and
grouping is not fact-copying (`group_without_copying_facts: true` on the members that support it).
And the stop rule applies as written — *"when members carry irreconcilable course, institution,
project, term, or purpose facts"* — two offerings' launch material in one folder does not merge.

---

## `proposed_fields`

**None**, and this is deliberate rather than empty. PR-6 forbids field rows on this schema and this
row mints nothing. The family's two existing proposals — `organization` and `fiscal_period`, exactly
as `business_operations.research.md` words them — are **seconded, not varied**, in line with every
landed sibling.

Two field-shaped holes are **named and deliberately not proposed**, because minting on a field-less
schema at the point of maximum temptation is the 574's mistake performed knowingly:

- **An `offering` / `product` key.** This row's prose template argues for a product level, and so does
  `product-requirements`', which declined to propose one for the same reason: *arguing for a level is
  not the same as being owed a key.* If R1c licenses fields, the product/offering question should be
  adjudicated **once for the three product rows** (`product-requirements`, `product-roadmap`,
  `go-to-market`), not separately on each.
- **A `launch` / `release` key.** Even more this row's own — it is the second level of the prose
  recommendation — and still not proposed. `fiscal_period` cannot express it (a launch is not a
  management period) and `project` would assert that a launch is a project, which is precisely the
  claim the fold section spent its argument denying. Recorded as NJ-BO-GTM-2.

Note that leg 1 of the *schema's* node test is contingent on NJ-BO-1. This row does not rely on that
contingency: it passes on detection signals, which the field question does not touch.

---

## NEEDS-JOSEPH

- **NJ-BO-14 · The fold question. *Settled here as KEEP; downgraded to a re-examination trigger.***
  Settled on three checkable separations from `project-delivery` (function-and-criteria columns versus
  predecessor-and-percent-complete; external irreversible end versus internal acceptance; sensitivity
  with an expiry versus without), on the roadmap fold being the wrong candidate in the roadmap row's
  own terms, and on four siblings already depending on this row as the far side of their
  discriminators. **Remaining ask for R1c:** the schema anchor's NJ-BO-2 still names this row as *"the
  weakest"* and as the cheapest trim, and this agent may not edit the anchor. Recommendation: **update
  NJ-BO-2 to record the settlement**, keeping only the narrow trigger — *if real corpora contain no
  readiness gates, positioning canvases or embargo blocks, leg 1 fails and the row folds into
  `project-delivery`.* A one-sided change would leave anchor and row contradicting each other, which
  is why none was made here.
- **NJ-J-IND-4 (carried; this row's variant, and the family's sharpest instance)** — **sensitivity
  with an expiry.** An embargo slot states the instant at which a document becomes public, and nothing
  downstream reads it or knows when it has passed. Alternatives and costs: (a) do nothing — the row
  stays `potentially_sensitive` forever, and years-old public press releases are treated as protected,
  which is over-protection and cheap; (b) P7 gains a notion of an expiring restriction — correct, and
  it needs an owner and a mechanism nobody has specified; (c) the embargo date is read as evidence and
  used — attractive and **wrong at this layer**, since it would be a row inventing a handling rule.
  *Recommendation: (a) now, (b) recorded as the real fix.*
- **NJ-BO-GTM-1 (new) · The `creative.*` reciprocals do not exist.** `creative.ad-campaign` and
  `creative.content-marketing` are roster ids with **no node files**. The two campaign boundaries most
  load-bearing for this row are authored one-way from this side, and the gist draft cited both files
  as if read. Either those rows land and adopt the reciprocals as written above, or R1c accepts an
  asymmetric edge. This is the same defect class as NJ-BO-4, in a family that had already recorded it.
- **NJ-BO-GTM-2 (new) · The pricing fold, narrowed.** Line 829 folds `ops.pricing` to
  `market-research`; the gist row took decided pricing back for itself and this pass narrows that to
  *pricing inside a launch structure only*. R1c may prefer the cleaner rule — all pricing to
  `market-research` — whose cost is that a launch pack splits at the pricing sheet. Stated on both
  sides above; not edited into the neighbour's file.
- **NJ-BO-GTM-3 (new) · Support enablement changes owner over time.** A launch FAQ is this row's while
  it is a gated deliverable and `support-operations`' once it enters the standing knowledge base, and
  **nothing in the file marks the transition**. Alternatives: leave it as the boundary above and accept
  that the same document is claimed by different rows at different times; or give the knowledge base
  sole ownership and lose the launch pack's coherence. No recommendation — this needs a real corpus.
- **NJ-BO-2 / NJ-BO-1 (carried, not re-argued)** — the 24-templates question and the two canonical-key
  proposals remain the anchor's and R1c's.

---

## Audits run before returning

- `python3 -m json.tool` on the node JSON — parses.
- Every `00` quotation in both files re-checked with `grep -c -F` against
  `planning/00-database-agent-product-design.md` — each returns exactly `1`.
- Every edge `domain` checked to exist as a `domain_id` in `planning/domains/roster.json` (358 ids).
- Every `file_examples.source_type` checked against `SOURCE_TYPES` in
  `src/evidence_shape/vocabulary.py`.
- `fields: []`, `proposed_fields: []` and `template.dimension_order: []` confirmed; no canonical key
  minted, no synonym coined.
- No threshold, no confidence score, no regex, no gazetteer content, no P7 handling class in either
  file.
- Key set diffed against the landed siblings — identical.
- Files written: only this row's two. No roster edit, no sibling edit, no `src/`, no `check.py`.

---

## What changed in this pass

**Preserved unchanged in the JSON** — the gist draft was largely right and is not rewritten for its
own sake: `name`, `launch`, `provenance`, `refuse_node: false`; `fields: []` and
`proposed_fields: []`; the **whole `recognition` block**, including its PRECONDITION entries, all
nine `deterministic` entries, all seven `needs_llm` entries and all ten `never_alone` entries — the
four structure-plus-slot pairs leg 1 argues were already written there correctly and needed argument,
not rewriting; all 34 `proposed_context_terms`; all 14 `work_types`; `grouping_reasons`;
`template.why` and `time_first: false`; `file_kinds`; all ten `file_examples` with their
`must_not_conclude` lists; the six `falls_through_to` routes; `sensitivity: potentially_sensitive`;
`role_split: []`; and six of the eight `collides_with` signals verbatim. Its judgement to drop
landing-page mockups and launch videos to `creative.*`, and to decline an `hr.training-development`
edge, is preserved and is now argued rather than asserted.

**Changed in the JSON**, each deliberate: `one_line` (anchor restated as the private-to-public
crossing, and the `Gist-level placeholder` tail replaced with `Placeholder row (J-IND/J-DEPTH)`);
`sensitivity_why` (rewritten to lead with the expiry ground, which is leg 3's actual argument, with
the gist's third-party and former-employer points preserved inside it); `open_question` (rewritten
from a deferral to a recorded settlement plus a narrow trigger); the `project-delivery` signal
(the gist's *"This pair is genuinely thin"* is superseded by the three settled discriminators, and
the supersession is stated in the signal itself); the `product-roadmap` signal (extended, not
replaced, with why the fold fails in the roadmap row's own terms); and **two new edges** —
`business_operations.support-operations` (NJ-BO-GTM-3) and `business_operations.board-governance`
(the governance-cycle close call from leg 1).

**Added or corrected:**

1. **The charge answered directly** — phase-versus-world — with the concession that a launch *is* a
   phase, and the reason that does not decide the test.
2. **The node test argued leg by leg** against the anchor's now-explicit default template and its four
   default detection shapes, with the two close calls (governance cycle; controlled-document header)
   recorded as close and each producing a boundary rule.
3. **Leg 1 rebuilt on four structure-plus-slot pairs**, replacing the gist's purpose-based argument,
   which the anchor's never-alone rule would have refused. Its honest limit is stated.
4. **Leg 3 given a ground of its own** — confidentiality with a stated expiry, which no other row in
   the family has — where the gist argued only that the material is commercially sensitive.
5. **The fold question settled**, with the gist's named fold candidate (`product-roadmap`) shown to be
   the wrong one and `project-delivery` argued instead on three checkable separations. NJ-BO-14
   downgraded to a trigger; the `open_question` string rewritten.
6. **The pricing fold narrowed** against ROSTER line 829, reversing part of the gist's claim, stated as
   a reversal and reciprocally.
7. **A source error corrected** — `creative.ad-campaign` and `creative.content-marketing` do not exist
   as node files and the gist cited them as read. Logged as NJ-BO-GTM-1.
8. **Files considered and rejected expanded** from five items to fourteen, with a discriminator each.
9. **Collision fixtures in both directions**, including the file that must not be lost *to* this row
   (`Atlas 2.0 - PRD v3.docx`), decided by `product-requirements`' own settled rule.
10. **Reciprocal boundaries table**, fourteen neighbours, both directions, with shared fixture bytes —
    where the gist had a five-line prose list.
11. **Sparse-file discipline** stated explicitly.
12. **Three new NEEDS-JOSEPH items** and NJ-J-IND-4 sharpened into this row's specific mechanism gap.
