# business_operations.meeting-record — lab notes (template row, deepened to J-DEPTH)

Row kind: **template** on `business_operations`. Launch: **placeholder** (`fields: []`).
Verdict: **kept, narrowed — and the gist verdict is sustained, not reversed.** The reasoning below is
new; the conclusion is the same one the gist pass reached, and I say why I did not reverse it.

**Status of this file.** The row was written under the retired J-IND *gist* standard and carried a
4.4KB memo against a 24.9KB JSON — an unusually large gap, because the JSON was already doing most of
the work. Per the deepening addendum the draft is **verified-but-shallow, not untrusted**: its
quotations were machine-checked, its key set matched the landed siblings, and its narrowing carve-out
was sound. It has been **deepened, not rewritten.** Four surgical JSON edits and a new memo; itemised
under *What changed in this pass* at the end.

---

## Sources actually used

### Binding

- `planning/00-database-agent-product-design.md` — the only document quoted as design. Every
  quotation in the JSON and in this memo was grep-verified verbatim against it in this pass (22
  quoted spans in the JSON; two of them are quotations of a *sibling row*, marked as such below and
  verified against that file instead).
- `planning/domains/_CONTRACT.md` — rules 1–3 (provenance, no fabricated quotes, no invented
  numbers), 6 (residuals stay out of this namespace), 8 (a dimension may only branch on a declared
  field), 10 (no field rows on a placeholder schema), 11–15.
- `planning/domains/CONNECTION.md` — §2 node test, §4 activation (step 2 never-alone, step 5
  protective ordering), §5 closed edge vocabulary, §9 failure mode 6 (a residual duplicating a
  template).
- `CONNECTION-EXAMPLES.md` fixture 5 — the `.ics` fixture. It is why `Weekly ops sync.ics` is a
  fixture here and why `calendar` is treated as contributing a file-kind signal only, never
  activation.
- `planning/prompts/ALIGNMENT.md`, `roster.json`, `canonical_fields.json`,
  `DECISION-BRIEF.md` (D1-as-narrowed, PR-6, J-IND/J-DEPTH taken as ratified), `ROSTER.md` §4 and
  Appendix A line 810 — the legacy id absorbed is `ops.meeting-record`.

### The schema anchor, read first as the addendum requires

`business_operations.research.md` (deepened, 46KB). Three things in it govern this row and are
applied explicitly below:

1. **The default template paragraph**, stated there *for the 24 siblings* — the paragraph this row
   must differ from. Quoted and answered in *Leg 2* below.
2. **The never-alone principle generalised**: *"No sibling may rest its activation on an entity name,
   a business vocabulary word, or a document shape alone. Each of the three is never-alone here.
   Every detection signal a sibling writes must pair a **structure** with a **labelled slot**."*
   This row is the sibling that principle was most obviously aimed at, and it is applied leg by leg.
3. **The values-are-not-nodes rule**: *"Differing in business function is not automatically a
   difference"*. A meeting is not a business function, but the same objection lands in a harsher
   form: a meeting may be a *format*. That is this row's actual risk and it is answered head-on.

### Siblings and neighbours read before writing (and not edited)

- `business_operations.organisational-records.json` — the family's refusal, read for what a genuine
  never-alone failure looks like. The comparison is made explicitly rather than gestured at.
- `business_operations.board-governance.json` — being deepened in parallel; its `collides_with`
  entry naming this row was read and this row now reciprocates **in that row's own words**.
- `clinical_practice.case-conference.research.md` (deepened, 37KB) — argued this boundary from its
  side. Its wording is adopted, not competed with.
- `business_operations.retrospective-postmortem.research.md` — a meeting that produces a document,
  and the row that deliberately declined to edge back at me.
- `business_operations.json` itself, for the shared vocabulary and posture.

---

## Provenance: why `provenance: "proposal"` and `design_cite: null`

Inherited from the schema row and restated because it is checkable here. `00`'s template-library
sentence enumerates the common organizational situations — *"covering common organizational
situations such as academic programs, university applications, recruiting processes, client
engagements, research workflows, financial records, travel, legal matters, creative projects,
software repositories, personal administration, and photo collections."* — and a meeting is not among
them. Nor is an organisation's own running record, which is the schema row's finding.

So the *existence* of this situation rests on the same inference the whole family rests on, and this
row may not claim `provenance: "design"` for it. The individual mechanisms it uses — reading tables,
purpose coherence, abstention, the residual homes — are `design` and are quoted as such. Every
`collides_with` signal on this row is marked `provenance: "inference"`, correctly: `00` names none of
these seams.

---

## The node test, argued leg by leg

CONNECTION §2 for a template row: it exists only where its **detection signals**, **recommended
dimensions**, or **privacy rules** differ from its schema's default template. One leg suffices; this
row is argued on all three because the dispatch flagged it as at serious risk, and a one-leg pass
would not be an honest answer to that flag.

### The objection, stated at its strongest before any leg

The dispatch's warning deserves to be written out properly rather than answered in passing. It runs:

> *Agenda / minutes / actions is a document **format**, not a situation. It sits beside calendar,
> mail, chat and call — the eighteen legacy ids the roster triage already dropped as "format /
> SOURCE_TYPE" material. Every sibling in this family already holds its own meetings: board packs
> (`board-governance`), status meetings (`project-delivery`), retros (`retrospective-postmortem`),
> clarification meetings (`procurement-sourcing`), QBRs (`customer-account-management`), case
> conferences (`clinical_practice.case-conference`). Subtract all of those and what remains is a file
> with no reliable deeper association — which is `00`'s own definition of a **residual**. A generic
> meeting row is therefore `organisational-records` wearing different clothes, and it survived the
> gist pass on thin reasoning while its neighbour was correctly refused.*

That is the argument to beat, and it is not a straw version. Three of its four premises are true: a
meeting *is* a format; the siblings *do* each hold their own meetings; and this row's discriminators
against those siblings *are* largely absence-shaped (no constitution, no project id, no causal
section, no solicitation reference, no account apparatus). A row whose whole definition is *what the
others did not take* is a residual.

The premise that fails is the fourth: that nothing positive remains. It does, and Leg 1 is that
argument.

### Leg 1 — detection signals of its own

The refused sibling failed here because its only candidate signal was *an organisation name plus a
document-type word*, and both halves are never-alone. This row's signals must be tested against the
same bar: **does each pair a structure with a labelled slot?**

Taking the JSON's `deterministic` list one at a time:

1. **The four-part meeting-note structure** — a meeting name or counterparty, a date, an attendee or
   participant list, and a decisions-or-actions section, *all four together*. This is a structure
   (four co-occurring blocks in a stable arrangement) with labelled slots (an attendee line, a date
   line, an action header). Each part alone is never-alone and the JSON says so in four separate
   `never_alone` entries. This clears the family bar as stated.
2. **The actions table with an `action / owner / due` header row.** A labelled slot in the strict
   sense — `00` licenses reading it: *"Tables matter because resumes, forms, applications, invoices,
   and administrative documents often place their most useful information in cells rather than body
   paragraphs."* But this one is **shared with three siblings and with the clinical neighbour**, so it
   is a family signal, not this row's own. It is not load-bearing here and I am not counting it.
3. **The series structure** — several documents whose titles differ only by a date token and which
   share an identical internal heading skeleton. **This is the signal that saves the row**, and it
   deserves its own paragraph.

The series signal is not absence-shaped and it is not a format. It is a *cross-file structural
regularity*: N files, one varying token, one invariant skeleton. No other row in this family has it —
`board-governance` has a cycle but the cycle is evidenced by a constitution (notice, quorum,
resolution) rather than by repetition; `project-delivery` has a project id; `budget-forecast` has a
period column set. And critically, it is exactly what a residual **cannot** have: `00` describes the
residual library as the destination for files with no reliable deeper association, and a file that is
provably the fourteenth instance of a series has a strong, positive, machine-checkable association —
to the other thirteen. It is an association to a *recurrence* rather than to a topic, which is
unusual, but it is not an absence.

Its variants strengthen it rather than dilute it:

- the **`.ics` form**: a labelled `SUMMARY` naming a recurring working meeting plus an agenda list in
  the body plus a recurrence rule — structure plus labelled slot, in the cleanest form this row has;
- the **conferencing-export form**: a machine-generated filename pairing a meeting title with a
  timestamp, plus a speaker-turn transcript structure;
- the **one-to-one form**: exactly two participants, one recurring across the whole series, plus a
  rolling carried-forward list — a structure no other row on the roster describes.

4. **What I am explicitly not counting as a signal**: the words *agenda, minutes, sync, standup,
   catch-up, 1:1* in a filename. They name the format and the family principle rules them out. The
   JSON already had them in `never_alone` and they stay there. This is the discipline the refused
   sibling did not have available to it, because *its* vocabulary was all it had.

**Verdict on leg 1: passes, on the series signal.** And the dependency is worth stating baldly rather
than hiding: **if the series signal is rejected, this row is a residual.** Signals 2 and 4 are
family-shared or forbidden; signal 1 is real but is a shape, and a shape shared with six siblings.
The row stands on cross-file recurrence. That is recorded as NJ-BO-MR-1.

### Leg 2 — recommended dimensions

The schema's default template, quoted from the anchor:

> *the **organisational unit or entity** only where the corpus genuinely spans more than one → the
> **governance body, project, contract, or account** the material belongs to → the **fiscal period** →
> the **document function**. Not time-first.*

This row's prose recommendation (`template.why`, unchanged from the draft): organisation → **meeting
series** → **occurrence date** → document function.

The differences are two, and only one of them is real:

- **Level 2 differs in kind, not just in value.** The default's second level is a *body, project,
  contract or account* — four things that exist independently of any document and persist between
  them. A meeting series is none of those; it is a recurrence, and it is constituted by the documents
  themselves. This is a genuine structural difference, and it is the same fact leg 1 turned on.
- **Level 3 is a calendar date where the default has a fiscal period.** This is the difference I want
  to be careful about, because it is the one that most looks like a difference and most nearly is
  not. The anchor is emphatic: *"No sibling in this family may claim it"* — `time_first: true` — and
  *"A budget year, a board year and a filing year are all content periods, not capture dates."*
  This row does **not** claim time-first and `time_first` stays `false`. What it claims is narrower:
  that the **occurrence is the unit** here in a way it is not elsewhere in the family, so a date level
  is load-bearing rather than scattering — and that it sits *under* the series, satisfying `00`'s
  parent-context rule, *"The recommendation should follow the practical rule that a parent dimension
  should provide the context required to understand the child."* A bare date tells a reader nothing
  about which meeting it was; `Ops weekly / 2026-03-12` does.

**A prohibition this row must carry louder than its siblings.** The one-to-one series is named for a
person, and the natural series label for it *is* that person's name. `00` requires that the system
avoid using authorship or creator identity as a destination dimension, and this is the single point
in the family where that rule is most likely to be broken by accident, because here the person's name
genuinely is the series identity rather than a collector. The JSON says so in `template.why` and
repeats it in the fixture's `must_not_conclude`. That is a **privacy-shaped dimension rule** and it
belongs to this row alone.

**Verdict on leg 2: passes, weakly.** One real difference of kind at level 2, one careful and
narrowly-scoped difference at level 3, one prohibition of its own. Weakly, because
`dimension_order: []` is empty by contract — the whole leg is a recommendation held in prose for a
pass that may never license fields, and a leg argued entirely in the subjunctive should not be
counted as strong evidence. If this leg were the row's only one, I would refuse.

### Leg 3 — privacy rules of its own

This leg passes cleanly and it is the row's second-strongest, after the series signal.

The schema's posture is `potentially_sensitive` on three grounds: the exposed party is usually not the
user, attachment carriage, and the `hr` bleed. This row differs on **all three, in the direction of
more risk**, and adds a fourth of its own:

- **The unguarded-document argument.** Working meeting notes are the least ceremonial documents an
  organisation produces and, for exactly that reason, the least guarded. A board pack is written
  knowing it will be circulated; a scratch note of a call is not. This is an inference, marked as
  one, and it is the row's own — the schema's third-party argument is about *who* is exposed, this
  one is about *how little care* the document was written with.
- **The running one-to-one.** One named person's pay, performance, health and complaints accumulating
  in one appended file, with no structural marker at the point where it stops being an ordinary work
  note and becomes an employment record. `00`'s corpus sentence names the material — the corpus *"can
  include identity documents, account statements, tax records, medical information, legal records,
  credentials, private correspondence, GPS metadata, employment materials, and educational
  records."* — and employment material is squarely in it. The fixture routes to **Protected Records**,
  not to Independent Records, and that routing is a privacy rule this row states and its siblings do
  not.
- **The recording.** A `.m4a` that is unreadable at scan time carries every participant's voice and
  whatever was said. It is the only file class in this family that is *more* sensitive for being
  unparsed, and the fixture's `must_not_conclude` says transcription is a model path P7 gates first.
  No sibling has this shape.
- **The clinical and legal bleeds**, which are the reciprocal half of two neighbours' arguments and
  are stated under *Reciprocal boundaries* below.

The row assigns only the catalogue value `potentially_sensitive`; it assigns, aliases, ranks and
infers **no P7 handling class**, and carries no `is_safety_domain`. The operative limits are `00`'s:
*"Protected material should not be included in cloud-model prompts by default, should not display raw
content in general group summaries, and should not be moved automatically without a user policy that
explicitly permits it."*

**Verdict on leg 3: passes.**

### Overall, and why I am not reversing the gist verdict

Two legs pass (1 on a single signal, 3 cleanly), one passes weakly. **Kept, narrowed.**

The addendum is explicit that reversing a gist "stands" on good evidence is a correct outcome, and I
went looking for that evidence. I did not find it. What I found instead is that the gist pass reached
the right answer for reasons it stated too briefly to be checkable — it asserted that "the signals
differ sharply" and listed three, of which only one (the series structure) actually survives the
family's never-alone principle. The conclusion holds; the argument needed replacing, and has been.

**The comparison with the refused sibling, made explicit**, since the dispatch asks for it. The two
rows fail and pass on genuinely different facts, not on a difference of enthusiasm:

| | `organisational-records` (refused) | `meeting-record` (kept) |
|---|---|---|
| Candidate signal | an organisation name + a document-type word | a cross-file series regularity + a four-part in-file structure |
| Never-alone status of that signal | **both halves never-alone** → can never clear CONNECTION §4 step 2 | the series regularity is **not** a name, a vocabulary word, or a single document's shape |
| Dimensions | identical to the schema default | level 2 differs in kind; a person-name prohibition of its own |
| Privacy | identical to the schema default | four grounds of its own, one routing to Protected Records |
| Residual test | *is* the definition of no reliable deeper association | has a positive association — to the other instances of its series |

The refused row could never fire. This one can, and the JSON names the bytes that fire it.

**The narrowing is what makes the difference safe.** The row's `one_line` carves out, explicitly,
every meeting produced inside a governance cycle, a project, a sourcing event, a retrospective, a
matter or a case conference. Those are **values of `work_type` on those rows**, which is the anchor's
own rule applied to itself. What is left is what the anchor's rule leaves: standing team meetings,
one-to-ones, and counterparty call notes.

---

## Files considered and rejected

The tempting false positives, and what discriminates each. Fixtures that stayed in the JSON are
marked.

| File | Why it is **not** this row's evidence |
|---|---|
| `Board pack - March 2026.pdf` (**fixture**) | The meeting shape in full — agenda, attendance, minutes, actions. Discriminator: a notice of meeting, a quorum statement, numbered papers with paper references, a register of interests, draft resolutions. Constitutional apparatus is `board-governance`'s and that row names this one back. |
| `Retro - sprint 41.docx` (**fixture**) | A meeting whose record has attendees, discussion and actions. Discriminator: what sits *above* the actions table — a went-well / went-badly / try-next facilitation structure, or a timeline plus a causal section. That row's own memo makes the same point from its side and calls the causal section its first `never_alone`. |
| `MDT outcomes 2026-05-14.xlsx` (**fixture, added this pass**) | The must-not-be-lost direction. A `case / decision / responsible / action by` table is structurally identical to an actions table. Discriminator: whether the rows are the **attendees' own work items** or **people who are not in the room**. If the latter, the clinical row owns it and it is protected material. |
| `Team meeting minutes 2026-05-14.docx` (**fixture, added this pass**) | The same seam in the opposite direction: a clinical department's rota-and-equipment meeting, clinicians in the room, no patient anywhere. `case-conference` names this file from its side precisely so it can disclaim it. The company equivalent is this row's; the clinical practice's own is `clinical_practice.practice-administration`'s. |
| A **wedding, PTA or club-committee agenda** | Real, identical four-part shape, no organisation. The anchor triple fails at its first term — there is no organisational unit — so this family does not activate at all. Personal administration or the nonprofit rows, and **Independent Records** where neither fires. Not given a fixture: the discriminator is the schema's, not this row's. |
| A **downloaded minutes template** or a "how to run effective 1:1s" article | The seductive one, and the schema's primary collision fixture in miniature. Every deterministic signal fires: heading skeleton, attendee line, an empty actions table. Discriminator is `00`'s — *"Topic answers what a file is about, while purpose answers what the file was for."* — plus the tell that the slots are placeholders. The blank-form case is worse than the article, because a blank form *is* the skeleton this row's series signal looks for. **A folder of blank meeting templates is a false series.** Named here because the JSON's series signal does not currently carry this caveat and R1c should decide whether it must. |
| A **personal journal** with dated bullets | The most common file in the corpus with this shape. Discriminator: no attendee list, no action-owner slot, first-person voice. Already this row's first `never_alone`, and the JSON's hardest `needs_llm` case is the overlap — unheaded free prose typed during a call. |
| A **to-do list** or standup scratchpad | Actions with owners and no meeting. It is the actions table without the other three parts, which is exactly why the four-part rule requires all four. |
| A **conferencing transcript `.vtt`** | Not rejected — folded into the recording fixture rather than given its own, because the extractor story and the privacy story are identical and a second fixture would be padding. |
| A **contact export** or distribution list | Carries the attendee-list half alone. `00` already keeps contacts data out of folder proposals; the JSON's third `never_alone`. |
| An **email thread that scheduled a meeting** | `source_type: email` is a routing signal — *"The engine should treat the file extension as a routing signal rather than an assumption about meaning, inspect the real MIME type or file signature where possible, and dispatch each file to a type-specific extractor."* A thread about a meeting is not a record of one; the row activates on the artifact, not on the arrangement. |
| An **attendance register** for a training course | Attendee list plus dates plus an organisation. It is `hr.training-development`'s, and the discriminator is that there are no decisions and no actions — two of the four parts absent. |

---

## The collision fixtures, in both directions

The addendum asks for both. This row has three, because the third costs more than tidiness.

**Would wrongly fire this row: `Board pack - March 2026.pdf`.** Argued above and in the JSON.
What emphatically does **not** discriminate: the words *agenda* and *minutes*, present on both; the
presence of an attendance list, present on both; a recurring monthly cadence, present on both. Both
sides say so — `board-governance` calls it *"The load-bearing collision for this row, and the one both
siblings must state."* and states that *"Meeting vocabulary discriminates neither."*

**Must not be lost to this row: `MDT outcomes 2026-05-14.xlsx`.** The clinical row's memo puts the
asymmetry better than I would: *"This matters more in this direction than in the other, because the
business row's residual posture is not protective and a wrong answer here **loses protection**, not
just tidiness."* I accept that framing without qualification. My side's residuals are Independent
Records and Review Later; theirs is Protected Records. A tie must therefore break toward them, which
is CONNECTION §4 step 5's protective ordering doing exactly what it is for.

**The third, and the one this row should be most ashamed to get wrong: `1-1 notes - running.md`.**
It is not a collision between two rows so much as a collision *inside one file over time*. Sections
one through eleven are an ordinary work note. Section twelve records a grievance. Nothing in the
document's structure changes at that line. Both anchors are genuinely present after it and P10 chooses
from an accepted group later; the JSON's `must_not_conclude` says so rather than pretending the row
can resolve it. This is NJ-BO-MR-2 and it is stated reciprocally for the `hr` author.

---

## Reciprocal boundaries, both directions

| Neighbour | This row must **not** take | The neighbour must **not** take | Shared fixture bytes |
|---|---|---|---|
| **`business_operations.board-governance`** (deepening in parallel; two-way, in its words) | a constituted body's cycle — terms of reference, notice, quorum, numbered papers, resolutions, conflict declarations | *"a team, project or stand-up record with owners and next steps and no constitution"* | `Board pack - March 2026.pdf`; prior minutes attached for approval |
| **`business_operations.project-delivery`** (one-way from here) | a project or programme identifier, a schedule reference, a RAID item | a standing team or counterparty series with **no** project anchor, merely because one agenda item names a project | a status-meeting note carrying both a series name and a project id |
| **`business_operations.retrospective-postmortem`** (one-way from here, **by their choice**) | a look-back structure: went-well/went-badly columns, an incident timeline, a contributory-factors or causal section above the actions | the *forward-looking* working meeting whose actions table it shares | `Retro - sprint 41.docx` |
| **`business_operations.customer-account-management`** (one-way from here) | an account identifier, adoption or usage reporting, a renewal date, a success plan | a call note with **no** account apparatus, merely because a customer was on the call | `Call notes - Meridian 4 Feb.txt` — three-cornered with `partnerships-bd` |
| **`business_operations.procurement-sourcing`** (one-way from here) | a solicitation reference, an evaluation scoring sheet, a panel record — minutes that must sit in the sourcing file for audit reasons | a routine supplier catch-up with no solicitation around it | supplier clarification-meeting minutes |
| **`clinical_practice.case-conference`** (**two-way, landed, deepened**) | a meeting-shaped file whose subjects are third parties under care — and the tie breaks their way, because their residual is protective and mine is not | *"an agenda/actions artifact whose subjects are the attendees themselves"*; a clinical department's own rota-and-budget meeting | `MDT outcomes 2026-05-14.xlsx`; `Team meeting minutes 2026-05-14.docx` — both now fixtures on both sides |
| **`hr.employee-relations`** (schema not landed; **one-way, knowingly**) | employment apparatus — a formal invitation, a right to be accompanied, an allegation, a warning, an appeal reference | an ordinary work discussion, merely because it names one employee and a manager | `1-1 notes - running.md`, where the file crosses mid-document |
| **`law_practice.matter-correspondence`** (not landed; one-way) | a matter or file reference, a client identifier, a privilege marking — an attendance note of a client or counsel meeting | an internal business meeting held by a firm about its own operations | an attendance note |
| **`clinical_practice.practice-administration`** (one-way from their side, accepted here) | a clinical practice's own departmental business meeting, where that practice is the corpus | — this row holds the company equivalent, and neither takes the other's | `Team meeting minutes 2026-05-14.docx` |

**Reciprocity status, verified by grep across `planning/domains/nodes/` in this pass.**
`clinical_practice.case-conference` names this row and is named back, with matched wording and shared
fixture bytes on both sides — the one fully two-way edge this row has. `board-governance` names this
row; this row now names it back in that row's own words, though that row is being deepened in
parallel and R1c should re-verify the quoted sentence survived. `retrospective-postmortem` names this
row in its memo and **deliberately declines the edge** — *"Left unedged deliberately: the confusion is
already carried by the meeting row's own scope"* — so the asymmetry there is a considered choice by
that author, not a defect, and I have not overridden it. `hr.*` and `law_practice.*` have not landed:
no files exist for either, so those edges are authored one-way knowingly and R1c owes the reciprocals.

---

## Neighbours considered that did **not** get an edge

- **`research`** — lab meetings and supervision meetings are exactly this shape. No edge:
  `clinical_practice.case-conference` already carries the meeting-versus-third-party-subject pair at
  full depth, and a research edge would restate it with the study anchor swapped in. The distinction
  that would matter (a study identifier or ethics-approval slot) is that row's own evidence firing.
- **`academic.teaching`** — office hours, staff meetings, supervision notes. Same reasoning, plus the
  schema anchor's ruling that an academic context term plus a course-code-shaped token is `academic`
  firing on its own evidence, which is a vocabulary confusion rather than contested bytes.
- **`government.legislative-record`** — formally recorded proceedings, with genuinely different
  apparatus (a chamber, a motion, a division). `board-governance` already carries the
  formal-proceedings edge for this family and adding a second would duplicate it.
- **`personal administration`** — a club or PTA committee agenda. Rejected as an edge because the
  failure is at the *schema* level (no organisational unit, so the family does not activate), not at
  this row's. Named in the rejected-files table instead.
- **`code.software-project`** — sprint ceremonies produce meeting artifacts inside repositories.
  No edge: the exclusion rule removes repository internals before this row could see them, and where
  a repo root fires, `code` owns the layout.

---

## `proposed_fields` — one, and it is a **seconding**, not a mint

The gist draft carried none, on the reading that PR-6 forbids fields on this schema. That reading
conflates two things: PR-6 forbids **field rows**, and `proposed_fields` is the mechanism for
naming a hole without minting one — the schema row itself carries two. So one has been added.

- **`organization`** — seconded, not minted, and it must be adjudicated **once** at R1c together with
  the schema row's proposal and `construction_property`'s. This row's own argument for it: a meeting
  series is identified by its name plus its **custody**, and the name alone is worthless. `Weekly
  sync` names hundreds of unrelated series across two employers and a side company, and the notes
  files are near-identical in shape. Without a custody fact, this row's central grouping reason (one
  recurring series across dates) can join two different organisations' series that happen to share a
  heading skeleton. That is the collector failure inverted: not one entity hoovering up everything,
  but two entities silently merged. `reliability_ceiling: "possible"`, because an entity name in a
  meeting note is the multi-role token at its worst — host, discussed counterparty, supplier in one
  agenda item, letterhead on an attached pre-read.

**Deliberately not proposed, and the omission is the point:**

- **`fiscal_period`** — four siblings want it and this row is not one of them. A meeting occurrence is
  a calendar date, not a management period. Claiming the key here would misuse it and would muddy an
  adjudication four other rows depend on.
- **A meeting-series key.** This is the field-shaped hole this row most obviously has — leg 1 turns on
  the series and no canonical key names one. I am **not** minting it, for the reason the schema row
  gave when it declined to mint a supplier role: *"minting a role key on a field-less schema at the
  exact point of maximum temptation would be the 574's mistake performed knowingly."* The same logic
  applies with more force here, because a series identity is also wanted by `board-governance` (its
  cycle) and arguably by `project-delivery` (its ceremonies), so the row that most wants it is the
  row least entitled to mint it alone. Raised as NJ-BO-MR-1 for R1c.

---

## Sparse-file discipline

Seven of this row's eleven fixtures carry `group_without_copying_facts: true`, the highest proportion
in the family, and the reason is structural rather than incidental: **this row's grouping reason is
strong exactly where its extraction is weakest.** A recording, a whiteboard photo, a bare `.ics`, an
untitled actions workbook and an unheaded prose note will all group correctly by neighbourhood and
series while yielding almost no facts of their own. That is precisely the configuration `00` warns
about — *"The graph does not automatically copy those missing facts onto sparse files."* — and it is
`HW 3.pdf` in a meetings folder.

Two applications specific to this row:

- **The recording beside the notes.** The notes file names the meeting, the attendees and the date;
  the `.m4a` names nothing. Grouping them is right; writing the notes' meeting fact onto the recording
  is the copy this rule forbids, and it would be the *worst* copy in the family, because it would
  attach a named participant list to an unlistened audio file.
- **The download session.** A meeting pack's attachments arriving at once is a session, and *"A
  session should never be treated as proof of topic, and it should not carry the same confidence as a
  hash match or a directly extracted document fact."* Already the JSON's seventh `never_alone`.

Every fixture also carries `"any business_operations fact - the schema declares none"` or its
equivalent in `must_not_conclude`, so the placeholder status is checkable file-by-file.

---

## NEEDS-JOSEPH

- **NJ-BO-MR-1 · The row stands on cross-file series recurrence — is that a legal signal, and does it
  need a key?** Leg 1 passes on one signal and I have said so plainly. Two dependent questions.
  (a) *Is a cross-file structural regularity an activation signal at all?* Every other signal in the
  catalogue is read from one file; this one is read from the relationship between several, and I could
  not settle from the design docs whether P4/P6 can produce it. If it cannot, this row has no signal
  of its own and should be refused and routed through `falls_through_to` — which is why the fallthrough
  list is already five deep. (b) *If it can, does the series need a canonical key?* Not minted here, for
  the reason above; `board-governance` and `project-delivery` would both want it. Cost of getting (a)
  wrong: a row that never fires, i.e. `organisational-records`'s failure discovered late.
- **NJ-BO-MR-2 · Where does a running one-to-one note live?** Simultaneously an ordinary work file and
  an employment record about a named person, drifting from one to the other mid-file with no
  structural change. Stated reciprocally: the `hr.employee-relations` author should carry the same
  question, and `hr` has not landed. Alternatives: (i) this row holds it and routes to **Protected
  Records** on the sensitivity signal, as the JSON currently does — cheap, but leaves protection
  depending on a `needs_llm` read of the note's content; (ii) `hr` claims the whole one-to-one class
  by shape — safer, but files an ordinary manager's notes folder as protected employment material,
  which is a real cost to the user; (iii) co-activation with the stricter side governing the members
  that identify people, which is the schema anchor's stated pattern for the `hr` bleed. This pass
  takes (i) and flags it. Guessing wrong in the (i) direction leaks; in the (ii) direction it
  over-protects. Not the row's call.
- **NJ-BO-MR-3 · A folder of blank meeting templates is a false series.** N files, one varying token,
  one identical skeleton — the series signal fires perfectly on material that is not a record of
  anything. The purpose test separates them (*"purpose answers what the file was for"*), but that is a
  `needs_llm` read standing between a deterministic signal and a wrong group. R1c should decide
  whether the series signal must carry a filled-slots precondition. Surfaced here rather than written
  into the JSON, because writing it would be inventing a detector rule this row does not own.
- **NJ-BO-MR-4 · Is a working meeting a situation or a format?** Carried forward from the gist pass as
  the row's `open_question` and answered above at length rather than smoothed. It is retained as a
  Joseph item because the answer is a *catalogue* decision, not a row decision: if the answer is
  *format*, this row folds into a `work_type` value on every sibling plus `Independent Records` /
  `Review Later`, and NJ-BO-MR-2's protection question must be **re-homed rather than dropped** — that
  is the part a fold would silently lose.

---

## What changed in this pass

**Preserved unchanged** (verified correct, not rewritten):

- the 27-key set, identical to the landed siblings and in the same order;
- every quotation, re-grepped verbatim against `00` in this pass (22 quoted spans; the two that are
  not `00`'s are quotations of `board-governance.json` and were verified against that file);
- `fields: []`, `dimension_order: []`, `time_first: false`, `refuse_node: false`, no threshold, no
  statistic, no P7 handling class;
- the whole `recognition` block (7 deterministic, 6 `needs_llm`, 7 `never_alone`), the 19 context
  terms, 9 work types, 4 grouping reasons, the nine original fixtures, the six other `collides_with`
  entries, the five `falls_through_to` entries, `sensitivity`, `sensitivity_why`, and the
  `open_question` — all of it correct as written;
- the `template.why` prose recommendation, including the person-name prohibition, unchanged;
- **the narrowing carve-out in `one_line`**, which is the draft's best single decision and the reason
  the row survives its own refusal question.

**Changed in the JSON** (four surgical edits, nothing rewritten):

1. `one_line` — the retired `Gist-level placeholder (J-IND)` label replaced with *"A PLACEHOLDER
   TEMPLATE ROW written to J-DEPTH"*. Substance unchanged.
2. `proposed_fields` — one entry added, **seconding** `organization` with this row's own argument
   (series identity requires custody) and stating explicitly that it is a seconding to be adjudicated
   once, with the schema row and `construction_property`, not a competing proposal.
3. `collides_with` — two signals rewritten to reciprocate neighbours **in their own words**:
   `board-governance` (quoting its load-bearing-collision sentence and its no-constitution
   discriminator) and `clinical_practice.case-conference` (adopting its *named cases / third parties
   who are not attendees* wording, and its finding that this direction loses protection rather than
   tidiness). No new edges; no edge removed.
4. `file_examples` — two fixtures added at the clinical seam, naming the **same bytes both
   neighbours name**: `MDT outcomes 2026-05-14.xlsx` (would be wrongly taken by this row; must not be)
   and `Team meeting minutes 2026-05-14.docx` (is this row's shape in a clinical building; the
   clinical row disclaims it from its side). Eleven fixtures now.

**Added in this memo** (the deepening proper): the provenance argument; the objection stated at full
strength before being answered; the node test argued leg by leg with a verdict and a stated weakness
per leg, including the admission that the row stands on **one** signal; the explicit
kept-versus-refused comparison table against `organisational-records`; the default-template paragraph
quoted and answered including the time-first prohibition; the twelve-row rejected-files table; three
collision fixtures in both directions; nine reciprocal boundaries with shared bytes and a grep-verified
reciprocity status; five neighbours argued as deliberately unedged; the `proposed_fields` argument and
the two deliberate non-proposals; the sparse-file section; and four NEEDS-JOSEPH items with
alternatives and their costs, up from two.

**What did not change: the verdict.** The gist pass said *kept, narrowed*, and on a full test it is
still kept, narrowed. What it lacked was a checkable argument, and the argument is now on the record —
including the single condition (NJ-BO-MR-1) on which the row would fall.
