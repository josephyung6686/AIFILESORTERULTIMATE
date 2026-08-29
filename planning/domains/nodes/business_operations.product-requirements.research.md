# `business_operations.product-requirements` — lab notes (template row)

**Depth: J-DEPTH.** Deepened from the gist draft of the J-IND pass. The gist draft's facts and its
JSON key set were correct and are preserved; what it lacked was the node test argued leg by leg, the
rejected-file work, reciprocal boundaries, and a settled answer to the pair question. Those are added
here. A "what changed in this pass" section closes the memo.

**Result: the row STANDS, and the pair question is settled as TWO ROWS.** Both verdicts are argued
below rather than asserted, and both were genuinely at risk — the dispatch was right that this row
could have gone the way of `organisational-records`.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — authoritative. Every quotation in the JSON and in
  this memo was machine-checked verbatim against this file (`grep -c -F`, count 1 each).
- `planning/prompts/ALIGNMENT.md` — "A template that would only repeat its schema's fields and
  `dimension_order` **is not a node** — it is the schema's default template." That sentence is the
  charge this row had to answer.
- `planning/domains/CONNECTION.md` §2 (the node test), §4 (activation, and step 2 in particular),
  §5 (invariants), §9 (failure modes); `CONNECTION-EXAMPLES.md`; `_CONTRACT.md` rules 6, 7, 10, 15.
- `planning/domains/canonical_fields.json` — read to confirm that no field row is written here.
- `planning/overnight/council/DECISION-BRIEF.md` — D1 (deferral, as narrowed), PR-6, J-IND. Ratified;
  not re-debated. PR-6 is why `fields` is `[]` and `dimension_order` is `[]`.
- `planning/domains/ROSTER.md` §4 + Appendix A line 831 (this row), line 830 (the paired row).
- `planning/domains/roster.json` — every edge id in the JSON was checked to exist as a `domain_id`.

### Neighbour and family files read before writing (and not touched)

- **`business_operations.research.md` (the schema anchor, deepened).** This is the row's measuring
  stick and it is used as one throughout — its default-template paragraph, its never-alone principle
  for all 24 siblings, its anchor triple, and its named residual set.
- **`business_operations.organisational-records.json`** — the family's refusal, read first on the
  dispatch's assumption that this row might be heading the same way. It is not; see "The charge".
- **`business_operations.product-roadmap.json`** — the paired row, read in full, and the reason the
  pair question can now be settled rather than deferred.
- **`business_operations.meeting-record.json`** — read because a spec-review minute is a plausible
  theft in both directions. That row narrows itself explicitly and the boundary is not disputed.
- **`business_operations.user-research.json`** — read, and it already names this row reciprocally.
  Its wording is adopted rather than contradicted.
- **`code.json`, `code.software-project.json`, `code.scratch-prototypes.json`** — the two honest
  refusals in `code`, read at the dispatch's instruction. They changed one edge in this row's JSON
  (see "The `code` edge was wrong").
- `legal.practice-matter-file.research.md` — read as a depth exemplar for a landed launch row.

### Sources deliberately NOT used

- `planning/deferred-catalogues/` — this row's recognition consumes no catalogue. There is no
  gazetteer of product names, and inventing one would be R4's work invented here.
- No regex, no threshold, no confidence score, no P7 handling class appears in either file.

---

## The charge this row had to answer

The dispatch put it plainly: **a PRD is plausibly a document type within a product's lifecycle
rather than a filing world**, and that is exactly the charge that killed `organisational-records`.
It deserves a direct answer before anything else, because if it lands the rest of the memo is moot.

The refusal's argument, quoted from its own `refuse_reason`: *"the row has none of its own. Its only
candidate signal is an organisation name plus a document-type word, and an organisation name is
constitutionally never-alone"*. The schema anchor then generalises it for all 24 siblings:

> **No sibling may rest its activation on an entity name, a business vocabulary word, or a document
> shape alone.** Each of the three is never-alone here. Every detection signal a sibling writes must
> pair a **structure** with a **labelled slot**.

Applied honestly to this row, in the order that matters:

1. **Is this row's support an entity name?** No. A product's name is in the JSON's `never_alone`
   list precisely because it appears on marketing material, support articles, invoices and roadmaps
   equally — this row does not claim it.
2. **Is this row's support a business vocabulary word?** No, and the JSON says so as its first
   `never_alone` entry: *the words spec, PRD, requirements or stories in a filename alone*. That is
   the honest admission that the document-type word is worthless, and it is the same admission
   `organisational-records` made and then had nothing left after making.
3. **Is this row's support a document shape alone?** This is the real question, and the answer is
   the one that saves the row: **no, because the structures pair with labelled slots.** A
   `given` / `when` / `then` triple is not a shape, it is three labelled slots in a fixed relation.
   A `non-goals` or `out of scope` heading is a labelled slot whose *label states the exclusion* —
   and the schema anchor's point about absent evidence applies in reverse here: this is a labelled
   assertion of absence, not an inference from absence. A requirement identifier repeated in a
   numbered column and referenced from a traceability column is a slot-to-slot relation inside one
   document. A decision record's `status` / `context` / `decision` / `consequences` block is four
   labelled slots in a standing order.

**So the charge does not land.** The difference from `organisational-records` is not that this row
tried harder; it is that after you delete the never-alone evidence, `organisational-records` had
nothing left and this row still has four structure-plus-slot signals. That is the test, and it is
the right test.

**One honest concession.** The charge is not *absurd*. If this row's `deterministic` list were
allowed to shrink to "a document with numbered requirements", it would collapse — numbered clauses
belong to contracts, policies, standards and statutes alike, which is why that is also in
`never_alone`. The row survives on the specificity of the slot pairs, and if R1c weakens them it
should reopen the refusal question rather than keep the row on inertia.

---

## The node test, argued leg by leg

`kind: template`, so CONNECTION §2's template test applies: **a template row exists only when its
detection signals, recommended dimensions, or privacy rules differ from its schema's default
template.** Three legs, each with its own reasoning. The schema's default template is quoted from the
deepened anchor and each leg is measured against it.

### The schema's default template, quoted so the comparison is checkable

> the **organisational unit or entity** *only where the corpus genuinely spans more than one* →
> the **governance body, project, contract, or account** the material belongs to → the **fiscal
> period** → the **document function**. Not time-first.

And the anchor's four default detection shapes: the governance-cycle structure; the
controlled-document header (version / owner / approver / effective date / review date); the
management-financial table without an institution header; the post-signature obligation register.

### Leg 1 — detection signals. **PASSES, and this is the row's strongest leg.**

None of the schema's four default shapes is this row's, and this row's four are none of the
schema's. Taken one at a time, because a summary would hide the work:

- **Against the governance-cycle structure.** A body name plus a period date plus an attendance
  list, agenda and resolution block. A PRD has no body, no attendance and no resolution. It is not
  cyclical at all — it is produced once per feature and then revised, which is a *version family*,
  not a cycle. This is the sharpest of the four.
- **Against the controlled-document header.** This one is genuinely close and the closeness is worth
  admitting: a mature PRD carries an owner, a status and a date, which looks like three-fifths of a
  controlled-document header. It is not one. The controlled-document header's distinguishing slots
  are **approver** and **review date** — the compliance apparatus that makes a policy a controlled
  document — and a PRD carries neither. Where a PRD *does* carry an approval block and a periodic
  review date, the honest answer is that it has become a controlled document and
  `business_operations.policy-handbook`'s signal is the better read; this row should not fight for
  it. Stated reciprocally in the boundaries section.
- **Against the management-financial table.** A budget/forecast/actual/variance column set. An
  acceptance-criteria sheet has a `requirement id` / `scenario` / `given` / `when` / `then` column
  set. Both are tables and `00` licenses reading cells from both — *"Tables matter because resumes,
  forms, applications, invoices, and administrative documents often place their most useful
  information in cells rather than body paragraphs."* — but the header vocabularies do not overlap
  at a single column.
- **Against the obligation register.** A schedule of renewal dates, notice periods and
  counterparties. A requirements traceability matrix is also a register-shaped grid, and this is the
  second close call. The discriminator is the **counterparty column**: an obligation register manages
  a relationship with a named external party, and a traceability matrix relates a document to itself
  and to its tests. A traceability matrix with a counterparty column is a contractual specification
  annex, and `business_operations.contract-administration` should have it.

**Verdict: passes cleanly.** Two of the four comparisons were close, both are recorded as close, and
both produced a boundary rule rather than a claim.

### Leg 2 — recommended dimensions. **CANNOT PASS, and does not need to.**

This leg is empty by binding contract, not by omission. `business_operations` declares no field rows
(PR-6, D1's deferral as narrowed, `_CONTRACT` rules 10 and 15), so `dimension_order` is `[]` here, on
the paired roadmap row, and on all 24 siblings. A dimension naming an undeclared field would open a
tree level no fact could ever fill, and `00`'s own canvas rules would then flag it: *"It should warn
when a level produces only one child"*.

**This leg is therefore neutral for every row in this family, and it must not be read as a failure
or as a pass.** CONNECTION §2's test is disjunctive — *detection signals, recommended dimensions, **or**
privacy rules* — so a row that passes leg 1 stands even with leg 2 unavailable. Saying so plainly
matters because the pair question below turns on exactly this: the leg that would most obviously
separate a specification from a roadmap is the one nobody in this family is allowed to use yet.

The recommendation is held as prose in `template.why` instead, and it does differ from the schema's
default paragraph in one substantive place: a **product** level sits between the organisation and
the feature, and there is **no fiscal-period level at all**. A specification is a durable statement
about a feature that outlives the quarter it was written in, so a period level would split one
feature's history across the calendar — which is `00`'s own stated reason for putting subject before
time: *"For document and record domains, project, function, or subject usually comes before time
because putting year first scatters related work across calendar folders."* The row is emphatically
not time-first, and per the anchor no sibling in this family may claim the time-first exception,
which `00` grants to capture-based media only.

### Leg 3 — privacy rules. **PASSES, narrowly, on one ground that is genuinely this row's.**

The schema's privacy posture rests on the exposed party usually not being the user, on attachment
carriage, and on the `hr` bleed. Two of those three barely apply here: a specification is mostly an
internal description of intended behaviour, and it is among the least personal material in the
family. If that were the whole story this leg would fail.

It is not the whole story, and the distinguishing ground is one the schema anchor does not name:

> **A specification's illustrations are captured from production.** A mockup, a bug repro, an
> annotated screen — these are routinely screenshots of a live system with real accounts, real
> names and real balances in them, saved into a specification folder because they illustrate a
> behaviour. The file *looks* like a design artifact and carries somebody's personal data.

That is a privacy rule of this row's own, and it is an inference, marked as one. Its consequence is
not a handling class — this row assigns none, and P7 owns that — but it is why the row is
`potentially_sensitive` rather than `none` despite the specification text itself being dull. The
second ground, unreleased product plans being commercially confidential, is real but is shared with
the roadmap row and several others, so it is not load-bearing here.

`00`'s operative limits are quoted in `sensitivity_why` and the enforcement point is `00`'s:
*"Privacy policy must be enforced before content reaches any model or external connector."*

**Verdict: passes, narrowly, on the production-screenshot ground.** Surfaced as NJ-BO-11.

### Overall

**Kept.** Leg 1 passes cleanly, leg 2 is unavailable to the whole family, leg 3 passes narrowly on a
ground of its own. The row is not the schema's default template and it is not a residual wearing a
domain's clothes.

---

## The pair question, settled: `product-requirements` and `product-roadmap` are TWO worlds

The gist pass kept both rows but recorded the merge case as an unresolved `open_question` on each.
The dispatch is right that this was never properly settled — a question stated identically on two
rows is a well-documented deferral, not an answer. It is settled here.

### Reading the roadmap row's own file first

Its anchor sentence, quoted from its `one_line`: *"The organizing anchor is the HORIZON and the
audience - a roadmap is a communication about time, it expires, and there is one current version of
it"*. Its detection signals are a horizon grid with periods on one axis; now/next/later; a scored
prioritisation table with reach/effort/value/confidence headers; a release-scope list with a cut
line; a changelog grouped under added/changed/fixed/deprecated; and a forward-looking disclaimer.

### What separates a requirements document from a roadmap — stated precisely

Not "one is detailed and the other is high-level", which is the intuition that makes them look like
one world. Three separations, each checkable against a real file:

1. **What time is doing in the document.** In a roadmap, time is a **structural axis** — the
   document is organised *by* period, and items are placed in period cells. In a specification, time
   is at most a **date on the document**. A specification has no time axis; delete the dates from a
   PRD and it still reads correctly, whereas deleting the periods from a roadmap destroys it. This
   is the single most reliable discriminator and it is visible in layout before any text is read.
2. **Whether the document expires.** A roadmap is superseded — there is one current one, and last
   quarter's is historical. A specification stays true after the quarter: "the export button
   produces CSV" does not stop being what was specified. This is why the recommended orders would
   diverge in the sharpest possible way the moment fields are licensed: the roadmap's prose order
   puts a horizon level in, and this row's refuses one.
3. **Whether the document states obligations or sequence.** A specification's atoms are
   **obligations about behaviour** with an acceptance test attached. A roadmap's atoms are
   **positions in an order**, with no test attached — nothing about a roadmap can be *passed*.

### The reciprocal statement, so neither file can be read alone

- **A file with a period axis and sequenced themes and no acceptance criteria is the roadmap's, even
  if every theme name is a feature name.** This row does not claim it. That is `H1 roadmap.pptx`,
  kept as this row's collision fixture.
- **A file with an out-of-scope section and given-when-then criteria is this row's, even if it opens
  with a target quarter on page one.** The roadmap row does not claim it, and its own
  `collides_with` entry for this row says so in matching terms.
- **The genuinely mixed document** — a deck whose first slide is a roadmap and whose remaining
  twenty slides are a specification — is the hard case, and neither row should resolve it from
  structure. It is `needs_llm` on both sides, phrased on this row as the boundary that defines it.

### Where the merge case remains real, and why it does not win

It is not dismissed. In a two-person team these documents share a folder, an author, and sometimes a
file; and the leg that would separate them most visibly (dimensions) is unavailable to both. But the
merge case is an argument about **how a small team stores** them, and the node test is about
**what evidence activates**. On evidence they are not close: a period axis and a given-when-then
triple do not co-occur by accident, and the two rows' neighbour sets barely overlap — this row's
nearest neighbours are `engineering.requirements-specification`, `code` and `user-research`, while
the roadmap's are `project-delivery`, `strategy-plan` and `go-to-market`. Different neighbours and
opposite relationships to time is not what one situation under two names looks like.

**Verdict: two rows, and NJ-BO-10 is downgraded from an open question about which row survives to a
narrow re-examination trigger** — see the NEEDS-JOSEPH section. The `open_question` text stays on
both rows unchanged, because this memo cannot edit the roadmap row and a one-sided change would
leave the pair contradicting each other. The recommendation to R1c is in the NEEDS-JOSEPH section.

---

## The `code` edge was wrong, and is corrected

The gist draft carried `collides_with: code.software-project`. Reading that row at the dispatch's
instruction shows two problems with the edge, and both are fixed in the JSON.

1. **`code.software-project` is `refuse_node: true`.** Its reason: *"Fails the template half of the
   node test on all three limbs — detection signals, recommended dimensions, and privacy rules are
   the Code schema's own, not a second situation's."* A collision edge to a row that can never fire
   is not a collision; it is a dangling pointer. The edge now names **`code`**, the schema, which is
   what actually activates when an ADR sits in a repository.
2. **It is not a collision in the first place — it is `also_holds_with`.** CONNECTION reserves
   `collides_with` for the mutex case, and the ADR-in-a-repository case is not mutex: the code schema
   activates on genuine structural evidence (a repository root, a package manifest) that is *about
   the file's location and project*, while this row activates on the document's decision-record
   structure, which is about its purpose. `00` licenses both being true of one file. So the edge is
   moved to `also_holds_with`, with the reciprocal boundary stated: **the code schema owns the
   repository layout and this row must not propose re-filing anything inside a preserved root** —
   `code.json`'s own open question about repository atomicity is Joseph's, not this row's, and
   `_CONTRACT` rule 7 forbids answering it by edge.

**This is a reversal of a gist-pass decision and it is stated as one rather than made silently.**

---

## Files considered and rejected

The dispatch's own test: a row that only lists what it holds has not been researched. Named tempting
false positives, and what discriminates each. The first two were kept as fixtures in the JSON; the
rest are rejected here and get no fixture.

| File | Why it is **not** this row's evidence |
|---|---|
| **`H1 roadmap.pptx`** (kept as the primary collision fixture) | Swimlanes by team across a quarter timeline, themes with target quarters, a now/next/later slide, an external-audience disclaimer. **No acceptance criteria anywhere.** Time is the structural axis. `business_operations.product-roadmap` owns it, and that row names the same bytes. |
| **`Requirements specification - Rev C.pdf`** (kept as the second fixture) | Numbered *shall*-statements with a verification-method column, a revision block naming an engineering approver, references to standards by number. Discriminator: **verification method per requirement plus a standards reference**. That is `engineering.requirements-specification`, and no PRD carries a verification-method column. |
| **A competitor teardown or feature-comparison grid** | Reads as a requirements list and often *becomes* one. It is evidence about someone else's product, gathered as background. `business_operations.market-research`. Discriminator: the subject is a product the user does not build. |
| **A user-research findings deck ending in five recommendations** | The closest theft from a row that already named this boundary reciprocally. Its evidence is *sessions with participants, consent records and transcripts*; this row's is a specification of intended behaviour with acceptance criteria. `business_operations.user-research`'s wording is adopted unchanged. |
| **A support knowledge-base article describing how a feature works** | Same product, same behaviour, same sentences, opposite direction: it describes what the product **does** for an external audience, not what it **should do** for an internal one. `business_operations.support-operations`. `00`'s test is the one that works: *"Topic answers what a file is about, while purpose answers what the file was for"*. |
| **A statement of requirements inside an RFP** | Requirement-shaped and numbered, but written **as a buyer to unknown suppliers**, with evaluation criteria and a submission deadline attached. `business_operations.procurement-sourcing`. This is a genuine role split and it is now an edge; see below. |
| **A specification annexed to a customer contract** | Byte-for-byte the internal specification, and legally an obligation once executed. Discriminator: two named parties and an executed signature block. `business_operations.contract-administration`. |
| **A policy or standard with numbered clauses** | Numbered obligation prose, which is why "numbered clauses" is in `never_alone` rather than in `deterministic`. Discriminator: the controlled-document header — **approver and review date** — which a PRD does not carry. `business_operations.policy-handbook`. |
| **A test plan or V&V protocol** | Considered at gist depth and folded into the acceptance-criteria fixture; at this depth it earns a boundary instead. A protocol with a test-execution record, an operator and a pass/fail signature is `engineering.verification-validation`; a given-when-then sheet written *before* the code exists is this row's. Discriminator: **executed results versus intended criteria.** Now an edge. |
| **A retrospective or post-mortem naming action items** | Action items look like requirements and the document is about the same product. Discriminator: it is anchored on an **event that happened**, with a timeline and contributing factors. `business_operations.retrospective-postmortem`. No edge — the anchor difference is unambiguous. |
| **A student project brief or coursework specification** | Identical shape, identical vocabulary. `academic` fires on its own evidence — school, term, course-code-plus-context. Deliberately given no edge; the schema boundary is carried by the academic side's context terms. |
| **A `.fig` file of a design system with no annotations** | A design artifact in its own right — layered source, components, visual exploration. `creative.uiux-product-design`. Discriminator: **numbered behaviour statements beside the picture**, or their absence. |
| **A vendor's product datasheet saved while evaluating tools** | Feature lists and specifications, about a product the user is buying. `business_operations.vendor-management` or `procurement-sourcing`; and if it is merely saved reading, **Reading Inbox**. |
| **`Screenshot 2026-04-02 at 09.14.11.png` of an app screen with no callouts** | The bare interface capture. Without numbered behaviour statements it is not a specification illustration, and *missing EXIF does not prove it is a screenshot* either way. **Temporary Screenshots.** |
| **A `.git` / `node_modules` tree inside the product's repository** | Removed by the exclusion rule. Where the repo root fires, `code` owns the layout; this row proposes nothing inside it. |

---

## The collision fixture, in both directions

The dispatch asks for both directions, and they are different files.

**Direction one — a file that would wrongly fire this row: `Requirements specification - Rev C.pdf`.**
Everything about it invites activation. It is a `text_document` full of numbered requirements with
identifiers, it has a traceability structure, it has a revision family, and its filename contains
the word *requirements*. Three of this row's own deterministic signals appear to match. **What
discriminates it: the verification-method column and the standards references.** A product
requirements document says what the product should do and why; an engineering requirements
specification says what shall be true and *how it will be proven*, against a numbered external
standard. The verification column is the load-bearing byte, and it is named identically on this row's
`engineering.requirements-specification` collision entry so both sides discriminate on the same
evidence.

**Direction two — a file that must not be lost *to* this row: `H1 roadmap.pptx`.**
Same product, same team, same folder, often the same author and the same week. It carries a feature
list, which is the evidence a naive reading would take as requirements. **What discriminates it: the
period axis with items in cells, and the absence of any acceptance criterion.** The roadmap row names
these same bytes in its own `collides_with` entry for this row, in matching terms — this is the pair
of files where the two rows compete, and neither file appears as a positive fixture on the other row.

**A third case that is neither: `ADR-014 event schema versioning.md`.** It looks like a collision
with `code` and it is not one — it is `also_holds_with`, per the correction above. It is kept as a
fixture on this row with `must_not_conclude` naming the shared ownership explicitly, so that P10
chooses from an accepted group rather than this row asserting exclusivity.

---

## Reciprocal boundaries, both directions

For each neighbour this row could steal from, stated so the neighbour's author can lift it verbatim.

- **`business_operations.product-roadmap`.** *This row takes:* out-of-scope sections, requirement
  identifiers, acceptance criteria, given-when-then, decision records. *The roadmap takes:* a period
  axis, now/next/later, prioritisation scoring, release scope with a cut line, changelogs,
  forward-looking disclaimers. *Neither takes:* a product name, a feature list, a quarter token.
  Settled as two rows above; the roadmap row's existing wording is not contradicted.
- **`engineering.requirements-specification`.** *This row takes:* user stories, acceptance criteria,
  success metrics, a non-goals section, a stakeholder audience. *Engineering takes:* shall-statements
  with verification methods, tolerances, standards references, an engineering approval block.
  *Reciprocal rule:* **the verification-method column decides**, in both directions.
- **`code` (the schema; `code.software-project` is refused).** Not mutex —
  `also_holds_with`. *Code takes:* the repository layout, and a preserved root is not re-filed by
  this row. *This row takes:* the document's product-decision purpose. *Reciprocal rule:* residence
  is a code fact, purpose is a product fact, and one file may carry both.
- **`business_operations.user-research`.** *This row takes:* a specification of intended behaviour
  with acceptance criteria. *User research takes:* evidence gathered from participants with a
  method — sessions, consent records, transcripts. Adopted from that row's own file verbatim in
  substance; not diverged from.
- **`creative.uiux-product-design`.** *This row takes:* numbered behaviour statements sitting beside
  the picture. *Creative takes:* layered source files, component libraries, visual exploration,
  design-system content. *Reciprocal rule:* the annotation decides. **Flagged:** this may be an
  `also_holds_with` rather than a collision — see NJ-BO-12. Left as a collision here rather than
  silently changed, because that row has not landed and cannot answer.
- **`business_operations.project-delivery`.** *This row takes:* product behaviour and acceptance
  criteria. *Delivery takes:* a schedule, milestones, a RAID log, resourcing. *Reciprocal rule:* a
  scope statement with dates and owners is delivery's; a scope statement with behaviours is this
  row's.
- **`business_operations.contract-administration`.** *This row takes:* the internal specification.
  *Contract administration takes:* the same text once two named parties and an executed signature
  block are on it. *Reciprocal rule:* execution transfers ownership of the bytes.
- **`business_operations.procurement-sourcing`.** New at this depth, and a **role split**: the same
  requirement-shaped document exists on both sides of a purchase. *This row takes:* requirements for
  a product **we build**. *Procurement takes:* requirements issued to suppliers for a product **we
  buy**, with evaluation criteria and a submission deadline. *Reciprocal rule:* the presence of an
  evaluation or bid-submission apparatus marks the buyer side.
- **`business_operations.meeting-record`.** *That row has already ceded this*, narrowing itself so
  that minutes produced inside another situation belong to that situation. So a spec-review minute
  is this row's. *Reciprocal rule, restated for symmetry:* a standing team meeting that happens to
  discuss the product is `meeting-record`'s; minutes of a review **of a named specification** are
  this row's.
- **`engineering.verification-validation`.** New at this depth. *This row takes:* intended criteria
  written before the thing exists. *V&V takes:* executed protocols with results, an operator and a
  sign-off. *Reciprocal rule:* **executed results transfer it.**
- **`business_operations.policy-handbook`.** Not an edge, but a stated rule, because leg 1's second
  close call needs one: a specification that acquires an **approver and a review date** has become a
  controlled document and `policy-handbook`'s signal is the better read. This row does not fight for
  it.

---

## Neighbours considered that did NOT get an edge, and why

- **`business_operations.support-operations`** — knowledge-base articles describe the same behaviour,
  but the audience and direction are unambiguous (what it does, externally, versus what it should do,
  internally). A boundary rule without an edge.
- **`business_operations.market-research`** — competitor teardowns become requirements, but the
  subject is someone else's product. Rejected above; the confusion is one-directional and already
  carried by that row's own market/user-research edge.
- **`business_operations.retrospective-postmortem`** — action items look like requirements; the
  event anchor makes the difference unmissable.
- **`academic`** — student project briefs share the shape exactly. No edge: the academic side fires
  on school/term/course-plus-context evidence that no product specification carries, and adding an
  edge here would invite the schema to fire on business words, which the anchor forbids.
- **`engineering.change-order`** — a change request against a specification is close, but it is
  anchored on an approved baseline and a cost/schedule impact. One-directional and thin; boundary
  noted, no edge.
- **`business_operations.customer-account-management`** — a requirement raised by a named customer.
  It becomes that row's when the anchor is the account rather than the feature; the confusion is
  already covered by the contract-administration edge and adding a second one would double-count.

---

## Sparse-file discipline

The `HW 3.pdf` problem has an exact analogue here and it is this row's most likely failure mode.
`Acceptance criteria - checkout.xlsx` and `saved-views-spec-annotated.png` name a feature and nothing
else. The temptation is to copy the neighbouring PRD's context onto them because they share a folder.
`00` forbids it: *"The graph does not automatically copy those missing facts onto sparse files."*
Both fixtures therefore carry `group_without_copying_facts: true` — they may join a P9 group with the
specification without this row asserting a fact about them. The same applies to the download-session
case: a whole specification folder arriving in one download is not evidence of topic, because
*"A session should never be treated as proof of topic, and it should not carry the same confidence as
a hash match or a directly extracted document fact."*

The archive fixture `spec_pack_v2.zip` carries the matching discipline: no purpose fact is read from
a manifest, and *"the normal scan should never extract archive contents to the filesystem"*.

---

## `proposed_fields`

**None.** PR-6 forbids field rows on this schema and this row mints nothing.

Per the dispatch, the family's two existing proposals are **seconded, not varied**:
`organization` and `fiscal_period`, exactly as `business_operations.research.md` proposes them, with
no rewording and no third key. This row has no field need those two do not cover, and specifically
it does **not** propose a `product` or `feature` key — the prose template argues for a product level,
but arguing for a level is not the same as being owed a key, and minting one here would be exactly
the variant-spawning the anchor warns against. If R1c licenses fields, the product/feature question
should be adjudicated once for the pair, not separately on each row.

Note also that leg 1 of the *schema's* node test is contingent on NJ-BO-1 (its two proposed keys
being accepted). This row does not rely on that contingency: it passes on detection signals, which
is a leg the field question does not touch.

---

## NEEDS-JOSEPH

- **NJ-BO-10 · One product-management row, or two?** *Downgraded from an open question to a
  re-examination trigger.* This memo settles it as **two**, on three checkable separations (time as
  axis versus date; expiry; obligations versus sequence) and on disjoint neighbour sets. Remaining
  ask for R1c: the `open_question` text on **both** rows still describes this as unsettled, and this
  agent may not edit the roadmap row. **Recommendation: R1c updates both `open_question` strings
  together** to record the verdict and keep only the narrow trigger — *if the fields pass never
  happens and the dimension leg stays permanently unavailable, re-examine the pair.* A one-sided
  edit would leave the two files contradicting each other, which is why none was made here.
- **NJ-BO-11 · Screenshots taken from production.** Mockups and specification illustrations are
  routinely captured from live systems and carry real user data while looking exactly like design
  files. This is leg 3's load-bearing ground, so it is not merely noted — if P7 has no signal for
  "image captured from an authenticated interface", this row's privacy leg rests on something the
  pipeline cannot act on. Alternatives: (a) P7 gains such a signal, and this row's leg 3 is real;
  (b) it does not, and the row stands on leg 1 alone, which it does anyway. Cost of (b) is that
  specification folders quietly accumulate personal data with no marking. Reciprocally relevant to
  `creative.uiux-product-design`.
- **NJ-BO-12 · Is the annotated mockup a collision or an `also_holds_with`?** An annotated interface
  file is arguably a design artifact **and** an interaction specification simultaneously, which is
  the `also_holds_with` pattern, not the mutex pattern. It is left as `collides_with` here because
  `creative.uiux-product-design` has not landed and a unilateral change would pre-empt its author.
  Alternatives: keep mutex, and one situation loses annotated design files entirely; or make it
  `also_holds_with`, and accept that two situations both claim the same image and P10 chooses.
  Recommendation: the latter, decided reciprocally when that row lands.
- **NJ-BO-13 · The buyer-side role split.** `role_split` to `business_operations.procurement-sourcing`
  is written here from this side only. The procurement row should carry the matching entry, and if it
  declines the split the requirement-shaped RFP annex has no owner on either side.

---

## Audits run before returning

- `python3 -m json.tool` on the node JSON — parses.
- Every `00` quotation in both files re-checked with `grep -c -F` against
  `planning/00-database-agent-product-design.md` — each returns exactly 1.
- Every edge `domain` checked to exist as a `domain_id` in `planning/domains/roster.json`.
- Every `file_examples.source_type` checked against `src/evidence_shape/vocabulary.py`'s
  `SOURCE_TYPES`.
- `fields: []` and `template.dimension_order: []` confirmed; no canonical key minted.
- No threshold, no confidence score, no regex, no P7 handling class in either file.
- Key set diffed against the landed siblings — identical.
- Files written: only this row's two. Nothing else touched.

---

## What changed in this pass

**Preserved unchanged** (the gist draft was right and is not rewritten for its own sake): the row's
name and `one_line`; `launch`, `provenance`, `refuse_node: false`; `fields: []` and
`proposed_fields: []`; the full `recognition` block including its PRECONDITION entries; all nineteen
`proposed_context_terms`; all ten `work_types`; `grouping_reasons`; `template.why`; `file_kinds`; all
nine `file_examples`; the five `falls_through_to` routes; `sensitivity` and `sensitivity_why`; and the
`open_question` text (deliberately, per NJ-BO-10).

**Added or corrected:**

1. **The charge answered directly** — why this row is not `organisational-records`, using the family's
   never-alone principle from the deepened schema anchor, including the concession that the charge is
   not absurd.
2. **The node test argued leg by leg** against the anchor's now-explicit default template, with the
   two close calls (controlled-document header; obligation register versus traceability matrix)
   recorded as close and each producing a boundary rule.
3. **Leg 2 correctly characterised as unavailable to the whole family** rather than as a pass or a
   failure — which is what makes the disjunctive test survivable and what the pair question turns on.
4. **The pair question settled as two rows**, with three checkable separations and a reciprocal
   statement, replacing a deferral stated identically on both files. NJ-BO-10 downgraded to a
   re-examination trigger with an explicit R1c recommendation.
5. **The `code` edge corrected in two ways** — retargeted from the refused `code.software-project` to
   the `code` schema, and moved from `collides_with` to `also_holds_with`. Stated as a reversal.
6. **Two new edges**, each argued: `engineering.verification-validation` (executed results transfer
   it) and `business_operations.procurement-sourcing` (buyer side), the latter also as this row's
   first `role_split`.
7. **A rejected-files table of fifteen entries**, replacing the gist's four.
8. **A collision fixture in both directions**, plus the third case that is neither.
9. **Eleven reciprocal boundaries**, each stated in both directions, plus a non-edge boundary rule for
   `policy-handbook`.
10. **A sparse-file discipline section** making the `HW 3` analogue explicit.
11. **NJ-BO-12 and NJ-BO-13 surfaced**, with alternatives and their costs; NJ-BO-11 sharpened from a
    note into leg 3's load-bearing dependency.
12. `proposed_fields` **argued** rather than merely absent: the two family proposals seconded verbatim,
    and the temptation to mint a `product` key named and refused.

**Length note, honestly.** This memo is shorter than the deepened schema anchor and about the length
of a landed launch memo. That is not restraint for its own sake — this row has a narrow evidence
surface (a handful of document structures, no gazetteer, no field rows) and padding it would have
meant inventing neighbours. Where there was genuinely more to say — the pair question, the rejected
files, the reciprocal boundaries — the memo says it at length.
