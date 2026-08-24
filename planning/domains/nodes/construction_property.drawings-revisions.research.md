# construction_property.drawings-revisions — research memo

Depth: J-DEPTH
Row: `construction_property.drawings-revisions` · kind `template` · schema `construction_property`
· launch `placeholder` · `fields: []` · absorbs the legacy row `cons.drawings-revisions`.

**Verdict: KEPT — but on one leg instead of three, on a different structure than the gist pass
named, and with the gist's field proposal withdrawn.** This is not a confirmation of the earlier
row. Three of its four claims are reversed below and each reversal is stated as a reversal.

The dispatch warned that this row was at serious risk of being a version-family concern in
disguise. That warning was correct about the *danger* and wrong about *where* the danger was. The
trap this row nearly fell into was not the version family — the gist had already seen and refused
that. It was **standing on a signal that belongs to its own schema.**

---

## Sources actually used

### Binding

- `planning/00-database-agent-product-design.md` — the only document quoted as `design`. Every span
  used here was grep-verified verbatim out of it (audit at the end). The ones that did work:
  - the **universal-facts sentence** — *"file type, creation date, language, duplicate family,
    version family, and sensitivity status"* — the sentence the dispatch pointed at, and the reason
    this row proposes no version-shaped field;
  - the **collision-policy sentence** — *"A content-hash match supports deduplication review; a
    filename match alone does not."* — the same point from the other end, and this row's first
    `never_alone`;
  - the **table sentence** — *"Tables matter because resumes, forms, applications, invoices, and
    administrative documents often place their most useful information in cells rather than body
    paragraphs."* — the licence to read a register at all, which is now this row's whole case;
  - the **university-name sentence**, the family's constitutional never-alone, read across to a
    postal address by the schema row;
  - the **dimension-order sentence** — *"For document and record domains, project, function, or
    subject usually comes before time because putting year first scatters related work across
    calendar folders."*;
  - the **sparse-file sentence** — *"The graph does not automatically copy those missing facts onto
    sparse files."* — which is what stops a register row becoming a fact about the sheet it names;
  - the **supersession sentence**, found this pass and quoted in the open questions: *"A newer
    result should supersede an earlier result while retaining the old observation and the reason it
    was superseded."*
- `planning/domains/nodes/construction_property.research.md` — **the schema anchor, read first and
  in full, and decisive against this row twice.** It states the family's default template and it
  claims the title block. Both are argued below.
- `planning/domains/nodes/business_operations.policy-handbook.research.md` — read on the dispatch's
  instruction. Its reissue argument is adopted, not answered: that row *"gains nothing from reissue
  and claims nothing from it."* So does this one, now.
- `src/facts/families.py` and `tests/p6/test_p6_families.py` — the landed G5 duplicate/version-family
  work, read directly rather than summarised. Decisive for the field withdrawal.
- `planning/domains/nodes/construction_property.construction-project.json` — the branch root. It
  names this row reciprocally and its wording is adopted verbatim.
- `planning/domains/nodes/construction_property.snagging-defects.json` — read second, and it turned
  out to be the sharpest collision on the row. New this pass.
- `planning/domains/nodes/construction_property.compliance-certificate.json` and `.timesheet.json` —
  the family's two landed refusals, read as the standard this row had to clear.
- `CONNECTION.md` §2 (node test), §4 step 2 (activation), §5 (edge vocabulary), §9 (failure modes);
  `_CONTRACT.md` rules 10 and 15; `ALIGNMENT.md`; `roster.json`; `canonical_fields.json`;
  `DECISION-BRIEF.md` (D1 as narrowed, D6, PR-6, J-IND).

**Attribution note.** `00` is quoted as `design`. Everything else quoted here is attributed in place
to the local file it came from — the schema anchor's memo, the branch root's and snagging's JSON,
`policy-handbook`'s memo, and (twice, marked) this row's own superseded gist memo, recoverable at
`git show HEAD:planning/domains/nodes/construction_property.drawings-revisions.research.md`.

### A source that does not exist, and it matters

`00` never names construction. The template-library sentence lists *"academic programs, university
applications, recruiting processes, client engagements, research workflows, financial records,
travel, legal matters, creative projects, software repositories, personal administration, and photo
collections"* — this world is absent. Hence `design_cite: null`, `provenance: proposal`, and every
`collides_with` entry marked `provenance: inference`. `00` supplies the machinery; the family
supplies the situation.

---

## What this situation is, in one paragraph

A building is built from a *controlled* set of information. A sheet has an identity — a drawing
number — and each time it changes it is **issued** again under a new designator, with a status
saying what it may be used for. The apparatus that makes this control rather than mere versioning is
the **issue register**: a schedule recording which revision of which sheet went to which recipient
on which date. Its purpose is to make one question answerable — *what was the site working from on
the day this was built?* — and its defining failure is building from a sheet that has since been
superseded. Nothing in the situation is about the bytes. Two byte-identical PDFs can be different
issues; two byte-different PDFs can be the same issue re-exported.

---

## The node test, leg by leg

CONNECTION §2: a template row exists only where its **detection signals**, **recommended
dimensions**, or **privacy rules** differ from its schema's default template. ALIGNMENT adds that a
row that *"would only repeat its schema's fields and dimension_order"* is not a node — *"it is the
schema's default template."* The test is disjunctive; one clean leg suffices. This row has one.

### Leg 1 — fields. Fails, and cannot pass.

`construction_property` declares no fields. PR-6 forbids field rows on it; `_CONTRACT` rules 10 and
15 forbid a dimension branching on a field the schema does not declare. There is nothing here to
differ on, for this row or any of its 27 siblings, and this leg is dead until NJ-CP-1 and NJ-CP-2
are answered. No leg-1 claim was made by the gist and none is made now.

### Leg 2 — detection signals. **PASSES, on one structure. This is the row.**

Here is where this pass reverses the gist pass, and the reversal is the most important thing in the
memo.

**The gist row rested the whole case on the title block.** Its words: *"What this row actually
stands on: the **title block**. A bordered zone carrying project, drawing number, sheet title,
revision, scale, status, originator and date as co-occurring *labelled slots* is a detection
structure that exists nowhere else on the roster."* Every clause of that is true, and it does not
earn a node, because **the schema anchor claims the title block as its own.** The anchor's leg 2
lists four structures belonging to no other schema, and the title block is the first of them:

> **The title block.** A bordered zone on a drawing sheet carrying, *in labelled slots and together*,
> a project or site name, a drawing-number-shaped token, a revision designator, a scale, a status
> word and an originator. Nothing else in the catalogue has this.

That paragraph is what makes the *schema* pass its own test. A sibling that repeats it is repeating
its schema's default template, which is exactly what ALIGNMENT says is not a node. The anchor even
warns sibling authors off the near-misses in the same breath — *"a revision designator alone (every
version family has one), a `.dwg` extension (a routing signal, not a meaning), or a project name."*
The gist was written before the anchor was deepened and could not have known. It is reversed here.

**What survives is the issue register, and it survives cleanly.** The schema's four structures are
the title block, the measured-works table, the *"to date, less previously certified"* arithmetic,
and the apportionment schedule. **The transmittal / drawing register is not among them.** It is a
distinct table: rows that are *drawing-number-shaped tokens naming other files*, columns that are
revision, status, issue date and recipients. Reading it is licensed by `00`'s table sentence, and
what makes it *this row's* rather than the schema's is what its rows denote — a register whose rows
are other documents is structurally unlike a register whose rows are measured works, leaseholders,
or defects.

Two independent corroborations, neither authored by me:

- The **branch root already concedes it.** `construction_property.construction-project`, which owns
  the container these sheets live in and had every incentive to claim them, writes: *"a drawing
  number plus revision plus status, and the transmittal register that released it, activate the
  sibling; the contract those drawings are issued under activates this row."*
- The schema anchor's own **seam checklist** lists *"a title block"* as evidence for *"professional
  practice — **this schema**, and an instruction-bearing sibling"* — schema-level, not row-level,
  precisely as read here.

A second, weaker structure supports the leg and is marked contestable in the JSON: the
**revision-history table** on the sheet — rows of designator, date, change description and initials.
It is arguably separate from the title block (it is a table with a change *description*, not a set
of labelled slots) and arguably inside it. It is listed as supporting, never as load-bearing,
because a leg that needs it is a leg in trouble.

**Verdict on leg 2: passes, narrowly, on the register.** The single point of failure is stated in
the JSON's `node_test_note` rather than hidden: if the issue register is not a real, findable
structure at corpus scale, this row has nothing left and should be refused. That is what R1c should
test if it wants to overturn the row.

### Leg 3 — recommended dimensions. **FAILS as a differentiator. Reversed.**

The gist called its dimension recommendation *"this row's most useful single output"* and *"the
reason it differs from its schema's default."* The recommendation itself is right: revision must not
be a folder level, because a folder per revision scatters one sheet's history across as many folders
as it has issues and puts the current sheet and the superseded sheet at equal depth with nothing
distinguishing them.

It is right and it is **not this row's**. The schema anchor states the family default as
*property → instruction → document function*, **not time-first**, and reaches the same conclusion in
its own sentence: *"`Valuation 07` and `Rev C` are meaningless without the job, exactly as
`Homework 3` is meaningless without the course."* The anchor names `Rev C` specifically. It also
forecloses the other move this row might have made: *"Reversing is not a difference that earns a
node."* This row does put the job first — it lives inside `construction-project`'s branch and
inherits that licensed reversal — and inheriting a licensed reversal earns nothing.

The recommendation stays in `template.why` as prose, because it is useful to whoever answers
NJ-CP-1, and `template.why` now says explicitly that it earns the row nothing. **Verdict: fails.**

### Leg 4 (privacy) — **FAILS as a differentiator. Reversed.**

The gist offered two grounds and called the second *"unusual for this family"*: that a drawing set
is a complete map of a real building's internal layout, access, services and security provisions.
The claim of unusualness is false. The schema anchor's own leg 3 already names *"a building's
security-relevant layout"* among the schema's grounds. `policy-handbook` supplies the governing
principle in one line — *inheriting a posture is not differing from it* — and it applies here
identically. The commercial-confidentiality ground is likewise the schema's third ground (*"The
exposed party is usually not the user"*) restated.

The value stays `potentially_sensitive`; `sensitivity_why` was rewritten to say it is inherited.
No `is_safety_domain`; no P7 handling class. **Verdict: fails.**

### Overall

**Kept on leg 2 alone.** Stating that plainly is better than the gist's three-legged claim for the
same reason `policy-handbook` gave: it tells R1c exactly what to test.

---

## The version-family trap, answered directly

This is the dispatch's central question and it deserves its own section rather than a clause.

**The charge.** The row is called "drawings-**revisions**". If what makes it a row is that drawings
get revised, that is a version family, which `00` already handles universally — *"file type,
creation date, language, duplicate family, version family, and sensitivity status"* — and
`policy-handbook` used precisely that sentence to refuse annual reissue as a basis for a row.

**The answer, in three parts.**

1. **The charge is accepted in full as to the field.** The gist's `revision` proposal is
   **WITHDRAWN**. See the next section.
2. **The charge does not reach leg 2, because leg 2 is not about revision.** An issue register is
   not a version family and does not become one. A version family is a relation between *bytes*; a
   register is a *document about other documents*, with recipients and dates, which exists whether
   or not any of the files it names are ever seen. The clearest demonstration is that the two come
   apart in both directions in real corpora: the same sheet re-downloaded four times from a document
   portal is one version family and one issue; a sheet issued at Rev C for comment and re-issued
   unchanged at Rev D for construction is two issues that may be one version family. **Membership of
   a version family is neither necessary nor sufficient for this row.** The row's constitutional
   `never_alone` says so from the other end and carries `00`'s own warning: *"A content-hash match
   supports deduplication review; a filename match alone does not."*
3. **The row's name is worse than the row.** "drawings-revisions" is the legacy id's name and it
   advertises exactly the thing the row does not stand on. The `one_line` was rewritten this pass to
   say the anchor is a **controlled issue**, not a file version and not a drawing. The name is not
   mine to change; R1c may wish to.

**What the landed G5 work actually says**, read directly rather than assumed. `src/facts/families.py`
writes `duplicate_family` and `version_family` as `00`'s universal keys, decides byte identity by
content hash, and — the load-bearing part — its `Lineage` type carries a `family_value` and a
`reliability_state` and **no position**, with `VERSION_FAMILY_STATES` restricted to `validated` and
`possible` because *a version family is never `direct`*. Its docstring says the design *"lists
'duplicate and version-family signals' among what basic extraction produces and defines neither"* and
that the middle is *held open* for an injected rule. So the gist was factually right that position
has no owner. It was wrong about what follows from that.

---

## `proposed_fields` — the withdrawal, for R1c

`proposed_fields` is now **empty**. `proposed_fields_note` records the withdrawal in full so it is
auditable. In brief:

The gist proposed one key, `revision`, arguing that `version_family` establishes **membership** —
these bytes belong together — while the situation's whole purpose is **position**, Rev C rather than
Rev D. That argument is not wrong. It is withdrawn on three grounds:

- **It is not this row's question.** An unowned gap in the *universal* machinery is a question for
  the universal machinery. Every re-issued document in the catalogue wants the same answer — a
  snagging list, a programme, a specification, a policy handbook. One of 28 siblings minting a
  domain key for a universal gap is how the catalogue acquires 28 near-duplicate keys.
- **`policy-handbook` already declined the identical move**, and two rows minting the same field for
  the same reason *is* the D6 near-duplicate defect. Adopting its position rather than distinguishing
  it is the correct outcome.
- **The row does not need it.** Leg 2 stands on the register, and the register carries the revision
  as its own *content* — a cell in a schedule — not as a fact about the file that cell names. `00`
  forbids the copy anyway: *"The graph does not automatically copy those missing facts onto sparse
  files."*

The substance survives as **NJ-CP-5**, restated as a question for the version machinery rather than
a field proposal. **No canonical key was minted and no variant proposed.**

---

## Files considered and rejected

| File | Why it is not this row's evidence |
|---|---|
| `Structural calculations - 2431 - Rev 2.pdf` | Same job, same discipline, a revision designator on the face of it. Its evidence is prose, formulae and result tables — no register, no issue, no recipients. `construction-project`'s package, and the schema anchor records it as shared with `engineering`. **The revision designator is the trap, and it fires nothing.** |
| `Specification - Section A - Preliminaries.docx` | Controlled information issued alongside the drawings and often listed on the very same transmittal. Rejected as *this row's* evidence: being *named on* a register is not being one. Its own structure is clause-numbered prose. |
| `Point cloud - east elevation.e57` | Genuinely this world; `construction_property.site-survey` owns survey capture. Not mine. |
| `Title block template.dwt`, `Standard details library.dwg` | A practice's tooling. They contain title blocks — the most tempting false positive available for a row that (wrongly) stood on title blocks, and a useful demonstration of why standing on the register instead is safer: a template library has no issue and no recipient. |
| `Drawing register template.xlsx` | Sharper still: an *empty* register. It has the columns and no rows. Rejected — the row's signal is a register with drawing-number-shaped rows, not a schedule with the right headings. |
| `Planning drawings as submitted.pdf` | A bundle issued to an authority. Contested with `construction_property.planning-application`, which owns the application envelope; the sheets inside are this row's, the submission is not. |
| `As-built set (final).zip` inside a handover pack | The one genuinely contested artefact, and the branch root names it as such: *"assembled and final here, one issue in a controlled sequence there."* Not resolved by either side; recorded, not smoothed. |
| A student's studio drawings | Carry title blocks. The academic schema's course code plus academic context decides it cleanly and already owns the case; no edge. |

---

## The collision fixture, both directions

**A file that would wrongly fire this row.** `Handover schedule Rev D.xlsx` — a spreadsheet, a
revision designator in the name, a status column, an issue date, re-issued in sequence. Structurally
it is this row's register almost exactly, and it is **`construction_property.snagging-defects`**,
whose own file says its defining property is that *"the same document is re-issued repeatedly with a
status column changing"*. The discriminator is **what the rows denote**: drawing-number-shaped tokens
naming other files (this row) versus defects pinned to a location and a responsible trade (the
sibling). A status column, a re-issue sequence and a revision designator count for **neither** — they
are common to both. If the rows are unreadable, neither activates and it is Review Later:
*"Correct abstention is a successful outcome because the product's goal is reliable organization, not
maximum file movement."*

**A file that must not be lost *to* this row.** `2431-A-102 Rev C - Ground Floor Plan.pdf` where the
title block is a *marketing* floor plan drawn from the same model and re-numbered by a designer who
liked the convention — or, in the version already in `file_examples`,
`floor plan final FINAL v3 (2).pdf`, which carries three version-shaped tokens and no border, no
title block, no scale bar. It belongs to `construction_property.agency-listing`. The discriminating
evidence in both directions is the register: an agency's plan is never on a transmittal.

---

## Reciprocal boundaries

Read each neighbour's own file first; do not contradict it. Where the neighbour is unwritten or does
not yet name this row, the boundary is authored one-way here and R1c owes the reciprocal — the schema
anchor records that this is a catalogue-wide defect, not a judgement about any seam.

| Neighbour | This row must not take | The neighbour must not take | Shared fixture bytes |
|---|---|---|---|
| **`construction_property.construction-project`** (landed, reciprocal) | the contract, appointment, programme, completion certificate or general correspondence the drawings are issued *under* | a sheet or a transmittal merely because a job exists around it — its own words: the register *"activate[s] the sibling"* | `As-built set (final).zip` inside a handover pack — contested by both, unresolved by both |
| **`construction_property.snagging-defects`** (landed; **one-way, R1c owes the reciprocal**) | a tracker whose rows are defects with a location and a trade, however many times it is re-issued | a schedule whose rows are drawing numbers naming other files | `Handover schedule Rev D.xlsx` |
| **`construction_property.variation-claim`** | a numbered instruction, a confirmation of verbal instruction, or the change submission built on it | the revised sheet issued *because of* an instruction — that is an issue, and it is on the register | a sketch attached to an architect's instruction |
| **`construction_property.agency-listing`** | a marketing floor plan with room-area annotation and agency branding | a general arrangement sheet with a drawing number, revision and status | `floor plan final FINAL v3 (2).pdf` |
| **`creative.architectural-visualisation`** | a persuasive rendered image with a brief and amends rounds | a drawing sheet under issue control because it is a `design_creative` file with a scheme name — the schema anchor's own line | a `.skp` model and a PDF view of the same building |
| **`creative.revision-round`** | a client comment cycle on a creative deliverable, which uses the same three words | a construction issue released under a transmittal to named recipients | a PDF marked up in red and returned |
| **`construction_property.site-survey`** | survey and capture output — point clouds, measured surveys | a survey drawing that has been *issued* into the set, which is one issue among others | `Measured survey - existing ground floor.dwg` |
| **`engineering`** | a drawing set for a product, machine or system with **no site** | a site-anchored issued set — the schema anchor's line, unchanged | a structural calculation package for a named building |
| **`finance.household-property`** | a householder's own extension paperwork with no instruction around it | a controlled set merely because the building is somebody's home | `Kitchen layout options.pdf` |

---

## Neighbours considered that did *not* get an edge

- **`photos.drone-captures` / `construction_property.progress-photos`** — overlap on as-built
  recording, but the confusable artefact is a photograph recognised by capture metadata and rhythm.
  The progress-photos row owns that argument and the branch root has already accepted it; repeating
  it here would be duplicate authorship. The one photograph that touches this row —
  `IMG_0912.jpg`, a phone shot of a sheet on a hoarding — is handled in `file_examples` as
  `group_without_copying_facts` with `also_schema: photos`, not as a collision.
- **`code`** — retained as a thin file-kind collision from the gist (IFC and parametric formats are
  structured data), unchanged. It was correct and adding to it would be padding.
- **`business_operations.contract-administration`** — the schema anchor and the branch root both
  hold this seam. Not mine.
- **`legal.leases-agreements`** — a licence to alter attaches drawings. The instrument is legal's and
  legal protects first; the attached sheets are this row's if they are issued. Recorded here, no
  edge, because the contested bytes are the branch root's `commercial-lease` collision already.

---

## NEEDS-JOSEPH (this node only)

- **NJ-CP-5 · RESTATED, and handed up rather than answered.** Does *position within a version
  family* — Rev C rather than Rev D — get an owner anywhere? The landed G5 work is the evidence that
  it currently has none: it writes a family value and a reliability state, never a position, and
  holds the lineage rule open for injection. **Alternatives and costs:** *(a)* the injected lineage
  rule also reports an ordinal or designator — one answer for the whole corpus, at the cost of
  specifying a rule `00` does not state; *(b)* leave it unanswered — costs nothing to build and
  leaves the single most useful question in this world unanswerable; *(c)* a domain field per
  family — **rejected in advance here**, it is the D6 defect. This row no longer proposes *(c)*.
- **NJ-CP-6 · The superseded marker, and this pass located the exact shape of the gap.** `00` uses
  supersession in precisely the sense this world needs — *"A newer result should supersede an earlier
  result while retaining the old observation and the reason it was superseded."* — but says it about
  the **evidence record**, not about file content. Supersede-and-retain is the drawing world's
  entire requirement, stated about provenance rows. Whether it is ever exposed for content is
  Joseph's call. **Alternatives:** *(a)* a status *value*, which labels and marks nothing; *(b)* a P7
  concern; *(c)* out of scope — the honest default, and what this pass assumes. **No mechanism was
  invented.** (Renumbered from the gist, which filed this unnumbered.)
- **NJ-CP-7 · The row's name.** `drawings-revisions` advertises the one thing the row does not stand
  on, and a reader who takes the name at face value will re-derive the gist's error. *(a)* rename to
  something naming the issue apparatus; *(b)* keep the legacy-derived name and rely on `one_line`,
  which now states the anchor explicitly. Not mine to change.
- **Inherits NJ-CP-1** (does `property` become a canonical key) **and NJ-CP-2** (`project` reuse vs a
  new `instruction` key). Both gate leg 1 for this row as for all 27 siblings.

---

## What changed in this pass

**Preserved unchanged**, because it was right and rewriting it would have been churn: the whole
`file_examples` array (ten examples, each already splitting observations from facts, each already
naming a residual); `work_types`; `proposed_context_terms`; `file_kinds`; `grouping_reasons`;
`falls_through_to` (six residuals with verbatim quotes); the `never_alone` list, which was the gist's
strongest section and already opened with the version-token trap; and three of the four
`collides_with` entries.

**Reversed, explicitly:**

1. **The title block is no longer this row's node-test evidence.** It is the schema's first leg-2
   structure. The gist rested the entire row on it. `recognition.deterministic` was reordered to put
   the **issue register** first, and the title-block entry now says in terms that it is listed
   because activation needs it and is *not* counted toward the node test.
2. **The dimension leg is withdrawn.** "Revision is not a folder level" is the schema anchor's own
   conclusion (*"`Rev C` [is] meaningless without the job"*), and reversal to job-first *"is not a
   difference that earns a node"*. `template.why` now says so.
3. **The privacy leg is withdrawn.** The security-relevant-layout ground is the schema's own;
   `sensitivity_why` was rewritten to record inheritance rather than difference. The value is
   unchanged.
4. **The `revision` field proposal is WITHDRAWN.** `proposed_fields` is empty;
   `proposed_fields_note` records what was proposed and why it went, for R1c.

**Added:**

- `node_test_note` — the leg-by-leg verdict and the row's single point of failure, stated for R1c.
- A fifth `collides_with`: **`construction_property.snagging-defects`**, the sharpest collision on
  the row and one the gist missed entirely, with the shared fixture named.
- A rewritten `one_line` naming the **controlled issue** as the anchor.
- A rewritten `open_question` with three items, alternatives and costs spelled out, and the `00`
  supersession sentence that locates the gap precisely.
- This memo: 4.3KB → J-DEPTH, with the node test argued leg by leg, the version-family charge
  answered as its own section, a rejected-files table, a two-direction collision fixture, a
  reciprocal boundary table, and the neighbours that got no edge.

**On length.** This memo is shorter than the deepened schema anchors and that is deliberate. A row
kept on one leg has less to say than a row kept on three, and padding it to match would misrepresent
how narrowly it stands.

---

## Audits

- `python3 -m json.tool` on the node JSON: **parses.**
- Key set: matches the landed siblings, plus `proposed_context_terms` (house-standard across this
  family), plus `node_test_note` and `proposed_fields_note` — both the `*_note` idiom already used by
  the landed launch row `finance.crypto-assets`.
- Every `00` quotation used in this memo and in the JSON was grep-verified verbatim against
  `planning/00-database-agent-product-design.md`.
- Every quotation attributed to a local file was verified against that file.
- Every edge id is a roster id or a `00` §7.3 residual name.
- `fields: []`, `proposed_fields: []`, `launch: "placeholder"`. **No canonical key minted.**
- Files written: this memo and `construction_property.drawings-revisions.json`. Nothing else.
