# business_operations.market-research — lab notes (template row)

**Depth: J-DEPTH.** Deepened from the gist draft, 2026-08-24. The gist row's verdict — the row
**stands** — survived the full node test, and the closing section records exactly what changed.
The dispatch warned this row might not survive. It does, but not for the reason the gist gave, and
the argument below is written so that a reader can check the reversal that did *not* happen.

## Sources

`00-database-agent-product-design.md` (every quotation below machine-verified verbatim with
`grep -F`), `01-product-design-structured.md`, `planning/prompts/ALIGNMENT.md`,
`planning/domains/_CONTRACT.md`, `CONNECTION.md` §2 node test and §4 activation,
`CONNECTION-EXAMPLES.md`, `roster.json`, `canonical_fields.json`,
`planning/overnight/council/DECISION-BRIEF.md` (J-IND, J-DEPTH, D1, PR-6), `ROSTER.md` §4 +
Appendix A lines 828–829, `src/evidence_shape/vocabulary.py` for `SOURCE_TYPES`.

Read as **anchors**, not as background:

- `business_operations.research.md` (46KB) — the schema anchor. Its two binding paragraphs for me
  are *The default template, stated for the 24 siblings* and *The never-alone principle, generalised
  for all 24 siblings*. Both are applied explicitly below.
- `business_operations.organisational-records.json` — the family's refusal, and the source of that
  principle. Read first, on the assumption that this row was heading the same way.
- `business_operations.user-research.json` / `.research.md` — the sibling with the same
  `research`-collision problem, whose reasoning I follow rather than re-derive.
- The landed `research.*` rows at full depth: `research.json` (schema),
  `research.reading-library.json`, `research.dataset-analysis.json`,
  `research.project-workspace.json` (a refusal, and the sharpest precedent for what a
  default-template row looks like when it is caught).

## What it is for, and what it holds

Investigating a market — its size, its segments, its competitors and what it will pay — to inform a
commercial decision. Sizing models, competitive matrices and competitor profiles, pricing analyses,
purchased analyst reports, survey and panel summaries, captured price exports, and the findings deck
the whole thing was built to produce.

## Legacy ids absorbed (ROSTER.md Appendix A)

`ops.market-competitive-research` (ROW, line 828) and `ops.pricing` (FOLD, line 829). The fold is
recorded, not accepted uncritically; see NJ-BO-9, which the deepening did not resolve and which is
now the row's largest open risk.

---

## The node test, argued leg by leg

CONNECTION.md §2: a template row exists only when its **detection signals**, its **recommended
dimensions**, or its **privacy rules** differ from its schema's default template. Three legs, each
reasoned separately, each measured against the paragraph the schema anchor states for all 24
siblings:

> the **organisational unit or entity** *only where the corpus genuinely spans more than one* →
> the **governance body, project, contract, or account** the material belongs to → the **fiscal
> period** → the **document function**. Not time-first.

### Leg 1 — detection signals: PASSES, and this is the leg the dispatch doubted

The warning was precise and it was the right warning: market research risks being a **`work_type`
value** — the *subject* of a report — rather than a filing world. The schema anchor states the test
that decides it:

> **No sibling may rest its activation on an entity name, a business vocabulary word, or a document
> shape alone.** Each of the three is never-alone here. Every detection signal a sibling writes must
> pair a **structure** with a **labelled slot**.

Taken one at a time, the three signals the dispatch named do all fail:

- **A company name.** Constitutionally never-alone in this family, read across from
  *"A university name alone should not create a group because Columbia can appear as an authoring
  school, course provider, target institution, employer, research venue, or merely a cited
  organization."* Worse here than elsewhere: the company names in this row's files are
  **competitors, suppliers, customers and cited third parties all at once**, and nothing in the name
  says which.
- **A report-shaped document.** A document shape, explicitly never-alone by the family rule.
- **A chart deck.** Every reporting document in the corpus contains a chart.

If those were the row's evidence, it would be `organisational-records` a second time and it would be
refused. They are not. The row clears the bar on **three structure-plus-slot pairs**, each of which
is a real, nameable layout and none of which is a topic word:

1. **The competitive matrix.** A table whose one axis names **several** distinct companies and whose
   other axis names capabilities, price points or positioning attributes. It is not "a company name":
   it is *n* company names occupying one axis of a grid, which is a structural fact about the file
   and is essentially unique to this row. `00` licenses reading it, because it lives in cells:
   *"Tables matter because resumes, forms, applications, invoices, and administrative documents
   often place their most useful information in cells rather than body paragraphs."*
2. **The sizing ladder.** A stacked derivation from a population or spend figure down to an
   addressable and then an obtainable figure, with a **labelled assumptions column and a labelled
   source column per line**. The labelled slots are the point; a budget spreadsheet has neither.
3. **The price-capture export.** A machine-generated file whose **header row names competitor,
   product, price and captured-at**. A labelled slot set no other sibling produces — a captured-at
   column is a claim about *observing someone else's* price at a time.

Each is a structure married to a labelled slot, which is exactly the pair the family rule demands.
So the leg passes — but it passes narrowly and on structure only, and the honest form of that is:
**strip these three shapes out and the row has nothing.** A pile of PDFs about a market, with no
matrix, no ladder and no export, is `work_type` chatter and this row should not fire on it.

### Leg 2 — recommended dimensions: PASSES, and differs from the default at two levels

The `template.dimension_order` is empty **by contract** — the schema declares no field rows (PR-6;
D1's deferral), and a dimension may only branch on a declared field. The comparison is therefore
between the default *prose* paragraph and this row's *prose* recommendation, which is the comparison
the schema anchor intends. Two of the four levels genuinely differ:

- **The second level is not a governance body, contract or account.** It is the **study — the
  commercial question the work was commissioned to answer**. A market study has no counterparty, no
  governing body and no account; the thing that holds the model, the sources, the competitor profiles
  and the deck together is the question. That is `00`'s purpose-coherence case exactly:
  *"The documents are content-incoherent but purpose-coherent."* And the parent-context rule makes it
  mandatory rather than stylistic — *"The recommendation should follow the practical rule that a
  parent dimension should provide the context required to understand the child."* A pricing scenario
  tab is meaningless without the question it was built to answer, in the same way `Homework 3` is
  meaningless without the course.
- **The `fiscal_period` level drops out entirely.** This is the sharpest structural difference from
  the family default. The other 23 siblings are made of periods — budget years, board years, filing
  years — and the anchor warns that they will be tempted into time-first because of it. A market
  study is **not periodic at all**: it starts when someone asks, and it stops when the decision is
  made. Putting a fiscal period above a study would split one study across two quarters for no
  reason. So this row does not merely decline `time_first: true` (which the anchor forbids the whole
  family anyway, granting the time-first exception to capture-based media only, and this row obeys
  that: *"For document and record domains, project, function, or subject usually comes before time
  because putting year first scatters related work across calendar folders."*) — it removes the time
  level from the recommendation altogether.
- **The tempting alternative, named and rejected: a competitor-first tree.** It looks natural, since
  the competitor is the most salient token in the corpus. It is wrong: it scatters one study across
  every company it mentions, and it turns a shared source document into a filing decision with no
  right answer. The market or the competitor is a **facet inside the study**, never a level above it.
- **The `organization` level is inherited unchanged**, including its seeded ineligibility — in a
  single-entity corpus it would name the user's own employer above everything they have filed, which
  is both of `00`'s validator failures at once (*"create meaningless one-child levels"*, *"use an
  author or organization merely as a collector"*). Inheriting it unchanged is not a difference and
  is not claimed as one.

This leg is what saves the row from `research.project-workspace`'s fate. That row was refused because
its recommendation was *"word-for-word the Research schema's own default template"*. Mine is not
word-for-word the `business_operations` default: it replaces level two and deletes level three.

### Leg 3 — privacy rules: PASSES, on a narrow but genuinely distinct ground

Most of this corpus is about **organisations rather than people**, which makes it the lightest row in
a family full of people-identifying material. That alone would be a *weaker* posture, not a different
one, and a weaker posture is not a node. Two things do make it different:

1. **Licensed third-party material.** A purchased analyst report carries a redistribution restriction
   in its own footer. It is the only material in this family whose handling constraint is owed to
   **an outside licensor** rather than to the organisation or to a data subject. It must not be
   shipped to an external connector by default, and the reason is contractual, not privacy-shaped.
2. **The organisation's own commercially confidential position.** Pricing scenarios, margins and
   elasticity assumptions are the material a competitor would most want. The pricing half arrives in
   the *same folder* as the harmless half — a saved trade article and a board pricing scenario sit
   side by side — so the row takes the cautious catalogue value for the whole of it.

Both route through the same operative sentence rather than through anything this row invents:
*"Privacy policy must be enforced before content reaches any model or external connector."*, and for
whatever P7 classifies as protected, *"Protected material should not be included in cloud-model
prompts by default, should not display raw content in general group summaries, and should not be
moved automatically without a user policy that explicitly permits it."* This row assigns only the
catalogue value `potentially_sensitive`; it does not assign, alias, rank or infer a P7 handling class.

### Verdict

**Stands**, on all three legs, with leg 1 the narrowest. I am **not** reversing the gist row's
verdict — but I am replacing its reasoning. The gist argued the row stands because its *anchor* is a
commercial question. That is true and it is the right thing to say about the situation, but it is a
statement about *purpose*, and purpose is not a detection signal; had that been the whole case, the
family rule would have refused the row. What actually earns the node is the three structure-plus-slot
pairs in leg 1 and the two template differences in leg 2. If a later pass finds that real corpora do
not contain matrices, ladders and price exports — that people keep only PDFs *about* markets — then
leg 1 fails and this row should be refused and folded into `strategy-plan` plus the Reading Inbox
residual. That is the condition on which the verdict rests, and it is stated so it can be checked.

---

## The `research.*` collision — consistent with `user-research`, and where it diverges

This is the sharpest collision the row has: an academic research corpus and a commercial
market-research corpus can look identical on the page — same methods, same sources, same charts, and
the word *research* in both names. `business_operations.user-research` faced the same problem and was
argued to stand apart from `research.*`. I read its file before answering and I follow it rather than
re-derive it. Its two reasons transfer intact:

1. **The output differs absolutely.** A commercial study ends in an internal recommendation that
   changes a price, a roadmap or an investment. An academic study ends in a manuscript at a venue.
   Confirmed against `research.json`'s own declared fields — `project`, `stage`, `artifact_type`,
   `lab`, `venue`, `authored_by`. Not one of them fits a TAM model: a sizing workbook has no stage,
   no lab and no venue.
2. **The governance differs.** `research.ethics-compliance` exists to hold the review-board apparatus
   — protocol numbers, approval letters, training certificates — that commercial market work does not
   have. A competitive matrix has never been near an IRB.

**Where I diverge, explicitly.** `user-research` authored an `also_holds_with` to the `research`
**schema** for the industry-research case: one file carrying two disjoint evidence sets, `00`'s
abstract-and-application shape. I considered the equivalent join here — an industry study published in
a peer-reviewed venue, or an academic market analysis commissioned by a firm — and **decline to author
it**, keeping the mutex `collides_with` to `research` instead. The reason is that my version of that
file is *third-party published work with no project identifier on it*, and both candidate rows agree
it is **reading material**: it routes to the Reading Inbox residual rather than activating either row.
A join edge would claim two activations for a file that should get none. That is a divergence in
outcome from the same principle, not a contradiction of it, and I state it here so `user-research`'s
author and R1c can see it. It is logged as NJ-BO-MR-3.

**Reciprocity is missing on the `research` side and I did not create it.** `research.json` does not
name `business_operations` anywhere. `user-research` already flagged this as NJ-BO-UR-1; this row
inherits the same gap rather than opening a second ticket for it, and does not edit a landed
neighbour's file to close it.

---

## Collision fixtures — both directions

The addendum requires a file that would **wrongly fire** this row, and a file that must **not be lost
to** it. Both are named on the same bytes as their neighbour.

**Direction 1 — would wrongly fire this row: `Interview notes - P07.docx`.**
A participant code, verbatim quotes about product use, a consent reference, a session date. It sits
in a folder called *Research*, it is about what customers want, and a topic-driven reader files it
here. It is `business_operations.user-research`, and the discriminator is not the topic but the
**unit of evidence**: this row's evidence is aggregate market structure — competitor sets, segments,
price points; `user-research`'s evidence is a **session with an individual under consent**. The
consequence of getting it wrong is not a misfiled document, it is a **privacy** failure: transcripts
carry whatever the participant volunteered. `user-research`'s own memo names this exact hazard on
`transcript_P04.vtt` — a participant volunteering an employer, a home city and a bank name — and both
rows now name the same bytes. This row's example carries
`falls_through_if_inactive: "Protected Records"` for that reason.

**Direction 2 — must not be lost to this row: `Gartner MQ 2026 - collaboration.pdf`.**
A title page naming a research house, a publication date, a methodology note, numbered figures, a
single-user licence notice in the footer — and **no organisation-specific content whatsoever**. Every
surface signal this row looks for is present: named companies, a market, charts, the word *research*.
It is not this row's analysis. It is somebody else's publication, and with no accepted study group
around it, it is reading material — the situation `research.reading-library` was written to carry and
which `00` gives a residual home: *"Reading Inbox may hold papers, articles, reports, and saved PDFs
that appear to be reading material but have no active research, course, or project association."* The
discriminator is the presence or absence of **a study group around the file** — the model, the sources
and the deck it was pulled to support. That distinction is now carried as a reciprocal
`collides_with` edge to `research.reading-library`, added in this pass.

`Industry outlook - saved article.pdf` is the same fixture in its cheaper form and is kept for the
same reason.

---

## Reciprocal boundaries, stated in both directions

For each, the boundary as this row sees it and as the neighbour sees it. Where the neighbour has a
landed file I read it first and did not contradict it.

- **`business_operations.user-research`.** *Here:* aggregate market structure, competitor sets, price
  points. *There:* sessions with individual participants, consent forms, transcripts, recordings,
  participant codes. Same bytes named on both sides (`Interview notes - P07.docx` /
  `transcript_P04.vtt`). Neither row may claim a study merely because it is "about customers".
- **`research` (schema).** *Here:* a commissioner, a deadline, a recommendation. *There:* a project,
  a stage, a lab, a venue and an intent to publish. Neither may claim the other on the word
  *research*. Reciprocity owed from the `research` side — see above.
- **`research.reading-library`.** *Here:* a third-party report **inside an accepted study group**, as
  source material. *There:* a third-party publication with **no project identifier**, which is that
  row's defining condition. Where there is no group, both rows decline and the file goes to the
  Reading Inbox residual. New edge in this pass.
- **`business_operations.strategy-plan`.** *Here:* the investigation — methodology, sources, a market
  as subject. *There:* a stated horizon, objectives, an organisation-wide commitment. The same deck
  at two stages of its life; `Pricing scenarios - board version.pptx` is deliberately marked
  undecidable at file level rather than assigned, because P10 chooses from an accepted group later.
- **`business_operations.go-to-market`.** *Here:* the analysis behind the positioning. *There:* a
  launch date, readiness checks, enablement material, channel plans. Neither may claim a positioning
  deck outright.
- **`business_operations.budget-forecast`.** *Here:* an **external** market with competitors and
  segments. *There:* an **internal** unit, a period, plan-versus-actual, variance commentary. The
  scenario-spreadsheet-with-assumptions shape is shared exactly and cannot discriminate; the
  internal/external subject can.
- **`business_operations.partnerships-bd`.** *Here:* a market with no counterparty being approached.
  *There:* a named counterparty being pursued, a proposal, a pipeline position. A target-account
  profile and a competitor profile are the same document; only the intent differs. The win/loss
  analysis is claimed by that row, not by this one (see below).
- **`business_operations.board-governance`.** Not edged. A pricing deck *presented* to a board is a
  board pack by residence, not by evidence; the file example carries the ambiguity in prose instead.
- **`creative.content-marketing`.** *Here:* an internal decision audience. *There:* an editorial
  calendar, a channel, a designed layout, an external audience. A published market analysis is
  content; the internal draft it came from is not.
- **`code.notebooks-experiments`.** Carried on `market_analysis.ipynb` as an undecidable rather than
  as a mutex: a notebook answering a commercial question genuinely carries both anchors.

---

## Files considered and rejected

Not what the row holds — what it was **tempted** by and turned down.

- **A win/loss analysis.** Competitor names, pricing, deal outcomes; every surface signal of this row.
  Rejected: it is anchored on **named deals with named counterparties**, and `partnerships-bd` lists it
  as a work type. Claiming it would be stealing a neighbour's situation on shared vocabulary.
- **A customer segmentation built from the organisation's own CRM data.** Genuinely astride this row
  and `user-research`, and the gist correctly declined to guess. Deepening does not settle it either:
  it is aggregate (this row) but derived from records of identified individuals (`user-research`'s
  privacy posture). Rejected as an example and raised as NJ-BO-MR-2 rather than assigned.
- **A supplier price list or an inbound quotation.** Company names and prices in a table — the single
  most convincing false positive by surface. Rejected: the organisation is the **buyer** and the
  document is a commercial offer to it, not an observation of a market. The family's *side* rule
  (buyer/seller) decides it.
- **The organisation's own rate card and quotation template.** Rejected despite the `ops.pricing` fold,
  because they contain **no analysis at all** — they are operational artifacts of selling. This is
  precisely the doubt in NJ-BO-9 and the row deliberately does not claim them.
- **An internal cost model.** Identical spreadsheet shape — price, volume, margin, scenarios — and no
  market in it. Rejected to `budget-forecast`.
- **A due-diligence pack on an acquisition target.** Market sizing, competitor analysis, the lot.
  Rejected: anchored on a **transaction with a named counterparty**, which is a corporate-development
  situation, not a market study. No roster row was confidently identified for it; noted, not invented.
- **An investor pitch deck's market slide.** Rejected: the deck is a fundraising artifact; the market
  slide is a *slide*, and claiming a document from one of its slides is the topic error this row is
  most at risk of.
- **Official statistics downloaded from a government source.** Rejected: a **source** for this row, not
  a confusion about it. Same treatment as the analyst report — reading material until a study surrounds
  it.
- **A market-research invoice from an agency.** Rejected: an invoice is a finance artifact whose subject
  happens to be market research. The clearest illustration of the dispatch's warning that this row's
  name is also a `work_type` **value** — and the reason the row must never fire on the phrase.

## proposed_fields

**None.** PR-6 forbids field rows on this schema and D1's deferral stands, so there is nothing for R1c
to adjudicate from this row. Two candidates were considered and deliberately **not** proposed:

- **A `study` or `question` key** for the row's natural second dimension. Not minted: the existing
  canonical `project` key would carry it, and `_CONTRACT` names minting a synonym for an existing key
  as the exact failure mode. If fields are ever licensed on this schema, this row asks for `project`,
  not a variant.
- **A `competitor` key.** Rejected on principle, not on availability. Its only use would be a folder
  level naming third-party companies — which is the competitor-first tree that leg 2 argues against.
  Minting a key to enable a dimension the row rejects would be incoherent. (Same reasoning
  `user-research` used to reject a `participant` key; deliberately consistent with it.)

## Neighbours considered that did NOT get an edge

- **`government.statistical-programme`** — a source, not a confusion. See above.
- **`finance.investment-brokerage`** — equity research and market research share shape, vocabulary and
  even publishers. Still not edged: `finance` is a safety-launch domain, and pulling an ordinary
  business row across that boundary would be answering a posture question rather than describing one.
  The gist declined for this reason and the deepening agrees; recorded as NJ-BO-MR-1 so R1c can decide
  rather than inherit silence.
- **`nonprofit.advocacy-campaign`** — campaign and constituency research is the same activity under a
  different motive. Too thin to author honestly from the design docs.
- **`academic.teaching`** — student market-analysis coursework. Covered by the `research` edge and by
  `academic`'s own course anchor; a third edge would add nothing.

## NEEDS-JOSEPH

- **NJ-BO-9 · Was the pricing fold right?** *(carried forward, unresolved and now the row's largest
  risk.)* Pricing **strategy** is built on the same competitor and willingness-to-pay analysis and
  belongs here. But the pricing pile a real organisation keeps is often mostly **rate cards, quotation
  templates, discount approval records and customer price lists** — no analysis in them at all — which
  belong nearer `go-to-market` or contract administration. **Alternatives and costs:** (a) keep the
  fold — cheap, but the row's name promises coverage it refuses to give, and users will file rate cards
  here and find nothing recognises them; (b) split `ops.pricing` back out as its own row — honest, but
  it needs its own structure-plus-slot pair to survive the same node test, and a rate card's structure
  (a price table) is weak evidence; (c) route the operational pricing artifacts to `go-to-market` and
  narrow this row's name to *market and competitive analysis* — my preference, and the cheapest honest
  fix. Joseph's call.
- **NJ-BO-MR-1 · The `finance` boundary.** Equity/sell-side research vs commercial market research.
  Deliberately unedged because `finance` is a safety domain. **Alternatives:** author a mutual
  `collides_with`, or state a one-way deference in which this row never claims a file that activates
  `finance` at all. The second is safer and is what I would do; either needs the `finance` side's
  agreement, so neither is authored here.
- **NJ-BO-MR-2 · Own-CRM customer segmentation.** Aggregate output, individual-record input. It sits
  exactly on the seam with `user-research` and the two rows have different privacy postures, so the
  answer changes how the file is handled and not merely where it lands. **Alternatives:** (a) this row,
  on the aggregate output; (b) `user-research`, on the provenance of the input — my instinct, because
  the safer posture should follow the data; (c) an `also_holds_with` join. Not guessed.
- **NJ-BO-MR-3 · The declined `research` join.** `user-research` authored an `also_holds_with` to the
  `research` schema; this row declines the equivalent and keeps the mutex, on the ground that its
  version of that file is reading material for both rows. Stated as a deliberate, reciprocal
  divergence. R1c should either endorse it or make the two rows consistent.

---

## What changed in this pass

**Preserved unchanged** (verified-but-shallow, not untrusted): the whole `recognition` block, the
`proposed_context_terms`, `work_types`, `grouping_reasons`, all nine `file_examples`, the
`template.why` prose, the `falls_through_to` set with its six verbatim residual quotes,
`sensitivity_why`, and the `open_question`. Every quotation in the JSON was re-verified verbatim
against `00` with `grep -F` in this pass; all matched.

**Changed in the JSON** — two edits only:

1. `one_line`: the retired "Gist-level placeholder" label replaced with "Placeholder row
   (J-IND/J-DEPTH)". No change of substance.
2. `collides_with`: **added `research.reading-library`**, stated reciprocally. The gist row named the
   purchased-analyst-report problem in prose and routed it to the Reading Inbox residual, which was
   right; it did not notice that a landed row exists for exactly that situation. This is the one
   substantive gap the deepening found in the draft.

**Added to the memo** — everything from *The node test, argued leg by leg* onward: the three legs
with reasoning per leg rather than a verdict, measured explicitly against the schema anchor's stated
default template and its never-alone principle; the family rule applied to the dispatch's three
doubted signals one at a time; the collision fixtures in both directions naming the same bytes as
their neighbours; ten reciprocal boundaries; nine files considered and rejected (up from four); the
two field candidates and why neither is proposed; and three new NEEDS-JOSEPH items with alternatives
and costs.

**Reasoning replaced, not silently reversed.** The gist justified the node on the row's *purpose
anchor* — a commercial question with a commissioner and a deadline. That is a true description of the
situation but it is not a detection signal, and on its own it would have failed the family's
never-alone rule. The node is now argued from structure. The **verdict is unchanged**; the ground it
stands on is not. If a later pass disconfirms leg 1 — real corpora holding PDFs about markets but no
matrices, ladders or price exports — this row should be refused and its coverage routed to
`strategy-plan` plus the Reading Inbox and Independent Records residuals. That condition is stated so
it can be tested rather than assumed.
